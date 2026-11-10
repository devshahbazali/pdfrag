from pdfrag.vectorstore.chroma_store import Hit
from pdfrag.generation.llm import getllm,llmProvider
from pdfrag.generation.rewriter import rewrite_query
from pdfrag.generation.rag import RagChain,RagAnswer
from dataclasses import dataclass, field

@dataclass
class Turn:
    question:str
    answer:str
    hits:list[Hit]
    rewritten_query:str | None=None

@dataclass
class ChatSession:
    rag:RagChain
    llm:llmProvider
    history:list[Turn]=field(default_factory=list)


    def _get_history_messages(self,turn_history:list[Turn])->list[dict]:
        "function to extract question and answer from each turn and make dictionary"
        history_messages:list[dict]=[]
        for turn in turn_history:
            history_messages.append({"role":"user","content":turn.question})        
            history_messages.append({"role":"assistant","content":turn.answer})
        return history_messages

    def ask(self,question:str)->Turn:

        #get all the available history messages and turn them to dict of role and content
        history_messages=self._get_history_messages(self.history);

        #rewrite the query according to history if history availble
        print("history_messages::::",history_messages)

        print("rewriting the query...")
        rewritten_query=rewrite_query(question=question,history=history_messages)
        print("done rewriting: ", rewritten_query)
        
        rag=RagChain()

        rag_answer:RagAnswer=rag.Ask(rewritten_query,top_k=5)
        turn= Turn(question=question,
                                 answer=rag_answer.answer,
                                 hits=rag_answer.hits,
                                 rewritten_query=rewritten_query)
        self.history.append(turn)
        return turn
    

        
        



