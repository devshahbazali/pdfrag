"""
Simple eval recorder.

Step 1:  python evaluate.py run        -> writes results.json (no judging)
Step 2:  python evaluate.py mark       -> interactive, you set True/False per item
Step 3:  python evaluate.py report     -> writes evaluation_report.md
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt

from pdfrag.generation.rag import RagChain

from pdfrag.vectorstore.chroma_store import Hit
console = Console()
RESULTS = Path("results.json")


# ---------- STEP 1: run the eval ----------

def run(eval_path: str = "eval.json", top_k: int = 5):
    ds = json.load(open(eval_path))
    questions = ds["questions"]

    rag = RagChain()
    console.print("[green]RAG ready[/green]")

    results = []
    for item in questions:
        console.print(f"\n[yellow]Q:[/yellow] {item['question']}")
        t0 = time.perf_counter()
        try:
            rag_answer = rag.Ask(question=item["question"], top_k=top_k)
            answer = getattr(rag_answer, "answer", "") or ""
            hits:list[Hit] = getattr(rag_answer, "hits", []) or []
        except Exception as e:
            answer, hits= "", []
            console.print(f"[red]ERROR:[/red] {e}")
        latency = time.perf_counter() - t0

        console.print(f"[yellow]A:[/yellow] {answer}")
        console.print(f"[green]E:[/green] {item.get('gold_answer', '')}")
        console.print(f"[dim]{latency:.2f}s[/dim]")

        results.append({
            "id": item["id"],
            "category": item["category"],
            "question": item["question"],
            "expected": item.get("gold_answer", ""),
            "answer": answer,
            "latency_s": round(latency, 3),
            "chunk_ids": [getattr(h, "id", "?") for h in hits],
            "correct": None,          # ← you will set this in step 2
            "hits":[{"id":hit.id,"text":hit.text} for hit in hits]
        })

    RESULTS.write_text(json.dumps({
        "meta": {
            "run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "date": datetime.now().isoformat(timespec="seconds"),
            "n_questions": len(results),
            "top_k": top_k,
            "doc_meta": ds.get("meta", {}),
        },
        "results": results,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    console.print(f"\n[green]Saved:[/green] {RESULTS}")
    console.print("[yellow]Next:[/yellow] python evaluate.py mark")


# ---------- STEP 2: mark true/false ----------

def mark():
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    results = data["results"]

    for i, r in enumerate(results, start=1):
        if r.get("correct") is not None:
            continue  # already marked — skip
        console.rule(f"[bold]{i}/{len(results)}  {r['id']}  ({r['category']})")
        console.print(f"[yellow]Q:[/yellow] {r['question']}")
        console.print(f"[green]E:[/green] {r['gold_answer']}")
        console.print(f"[cyan]A:[/cyan] {r['answer']}")
        for i,hit in enumerate(r["hits"],start=0):
            console.print(f"[blue]{i}[/blue]: {hit}")


        while True:
            v = Prompt.ask("Correct?", choices=["y", "n", "s"], default="s")
            if v == "y":
                r["correct"] = True
                break
            if v == "n":
                r["correct"] = False
                break
            if v == "s":
                console.print("[dim]skipped[/dim]")
                break
            

        # save after every mark so you can quit anytime
        RESULTS.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    console.print("\n[green]All marked. Next:[/green] python evaluate.py report")


# ---------- STEP 3: write the markdown report ----------

def report():
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    results = data["results"]
    meta = data["meta"]

    unmarked = [r["id"] for r in results if r.get("correct") is None]
    if unmarked:
        console.print(f"[red]{len(unmarked)} unmarked results:[/red] {unmarked}")
        console.print("[yellow]Run `python evaluate.py mark` first.[/yellow]")
        return

    # compute percentages
    by_cat = {}
    for r in results:
        by_cat.setdefault(r["category"], []).append(r)

    lines = []
    w = lines.append

    w(f"# RAG Evaluation Report")
    w("")
    w(f"**Run:** `{meta['run_id']}`  ")
    w(f"**Date:** {meta['date']}  ")
    w(f"**Test set:** {meta['n_questions']} questions  ")
    w(f"**Top K:** {meta['top_k']}")
    w("")

    # summary table
    w("## Summary")
    w("")
    w("| Category | N | Correct | Accuracy | Mean latency (s) |")
    w("|---|---|---|---|---|")
    for cat, items in by_cat.items():
        n = len(items)
        passed = sum(1 for r in items if r["correct"])
        acc = passed / n
        mean_lat = sum(r["latency_s"] for r in items) / n
        w(f"| {cat} | {n} | {passed} | {acc:.1%} | {mean_lat:.2f} |")
    n = len(results)
    passed = sum(1 for r in results if r["correct"])
    mean_lat = sum(r["latency_s"] for r in results) / n
    w(f"| **Overall** | **{n}** | **{passed}** | **{passed/n:.1%}** | **{mean_lat:.2f}** |")
    w("")

    # per-question table
    w("## Results")
    w("")
    w("| ID | Category | Question | Expected | Answer | Latency (s) | Correct |")
    w("|---|---|---|---|---|---|---|")
    for r in results:
        mark = "✅" if r["correct"] else "❌"
        ans = (r["answer"] or "").replace("\n", " ")
        exp = (r["gold_answer"] or "").replace("\n", " ")
        w(f"| {r['id']} | {r['category']} | {r['question']} | {exp} | {ans} | {r['latency_s']} | {mark} |")
    w("")

    Path("evaluation_report.md").write_text("\n".join(lines), encoding="utf-8")
    console.print(f"[green]Wrote evaluation_report.md[/green]")
    console.print(f"[bold]Overall accuracy: {passed}/{n} = {passed/n:.1%}[/bold]")


# ---------- CLI ----------

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        run()
    elif cmd == "mark":
        mark()
    elif cmd == "report":
        report()
    else:
        console.print("usage: python evaluate.py [run|mark|report]")