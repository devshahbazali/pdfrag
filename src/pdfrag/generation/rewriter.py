from pdfrag.generation.llm import getllm


REWRITE_SYSTEM="""Rewrite the user's latest question as a standalone search query.

- Use the conversation history to resolve pronouns ("it", "that", "they") and implicit references.
- Keep the meaning identical — do not answer the question.
- If the latest question is already standalone, return it unchanged.
- Output ONLY the rewritten query, nothing else.
"""



def rewrite_query(question:str,history:list[dict])-> str:
    "rewrite the query according to previous chat history"
    if not history:
        return question
    #used the last 4 messages and their replies
    history_used=history[-6:]    
    messages=[
        {"role":"system","content":REWRITE_SYSTEM}]
    messages += [{"role": h["role"], "content": h["content"]} for h in history_used]
    messages.append({"role": "user", "content":
    f"Rewrite this question as a standalone search query. "
    f"Output only the query, nothing else.\n\n"
    f"<latest_question>{question}</latest_question>"
    })  

    llm=getllm()
    rewritten_query= llm.chat(messages=messages,temperature=0.0)
    
    return rewritten_query