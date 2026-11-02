from sentence_transformers.cross_encoder import CrossEncoder
from functools import lru_cache
from typing import Any
@lru_cache(maxsize=1)
def getEncoder()->CrossEncoder:
    reranker =  CrossEncoder(
        "cross-encoder/ms-marco-MiniLM-L-6-v2"
    )
    return reranker

def rerankResults(query:str,results:list[dict[str,Any]]):
    reranker=getEncoder()
    pairs=[[query,result["text"]] for result in results]
    scores=reranker.predict(pairs)
    
    ranked_results=sorted( zip(results,scores),
            key=lambda x:x[1],
            reverse=True)
    
    return [
        {**result, "rerank_score": float(score)}
        for result, score in ranked_results
    ]

    