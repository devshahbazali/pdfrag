from dataclasses import dataclass
from pdfrag.embeddings.embedder import embed_query
from pdfrag.vectorstore.chroma_store import ChromaStore
from pdfrag.reranking.reranking import rerankResults
from pdfrag.generation.prompt import build_messages
from pdfrag.generation.llm import getllm
from pdfrag.vectorstore.chroma_store import Hit
from typing import Any
@dataclass
class RagAnswer:
    question:str
    answer:str
    hits:list[Hit]
    model:str

  
    
    

class RagChain:
    def __init__(self):
        self.llm=getllm()

    
    def Ask(self,question:str,top_k=5):
        store=ChromaStore()
        query_embedding=embed_query(query=question)
        hits:list[Hit]=store.query(query_embedding=query_embedding,top_k=top_k)
        reranked_hits=rerankResults(query=question,results=hits)
        messages=build_messages(question=question,hits=reranked_hits)
        answer=self.llm.chat(messages=messages,temperature=0.0)
        return RagAnswer(
            question=question,
            answer=answer,
            model=getattr(self.llm,"model","unknown"),
            hits=reranked_hits
        )
