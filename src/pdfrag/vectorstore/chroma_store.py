from pathlib import Path
from typing import Any
import chromadb 
from chromadb.config import Settings as ChromaSettings
from dataclasses import dataclass
from pdfrag.chunking.models import Chunk
from pdfrag.config import settings

COLLECTION_NAME="ragpdf"

METADATA={"hnsw:space":"cosine"}


@dataclass 
class Hit:
    "data class for result returned by the db, metadata is dict with keys source,page, chunk_index,total_pages" 

    id:str
    text:str
    metadata:list[dict[str,Any]]
    distance:float
    rerank_score:float = None #to store the hit reanrak score from cross encoding

class ChromaStore:
    def __init__(self,persist_dir:Path|None=None)->None:
        persist_dir=persist_dir or settings.CHROMA_PATH
        persist_dir.mkdir(parents=True,exist_ok=True)
        self.client=chromadb.PersistentClient(path=str(persist_dir),
                                              settings=ChromaSettings(anonymized_telemetry="false"))

        self.collection=self.client.get_or_create_collection(name=COLLECTION_NAME,metadata=METADATA)

    def count(self)->int:
        return self.collection.count()

    def reset(self)->None:
        self.client.delete_collection(COLLECTION_NAME)
        self.collection=self.client.get_or_create_collection(name=COLLECTION_NAME,metadata=METADATA)

    def addChunks(self,chunks:list[Chunk],embeddings:list[list[float]])->None:
        "add chunks and there respective embeddings to the chroma db"
        if len(chunks)!=len(embeddings):
            print("Error: chunks and embeddings are not of same size")
            return

        self.collection.add(ids=[c.chunk_id for c in chunks],
                            documents=[c.text for c in chunks],
                            metadatas=[{"source":c.source,
                                        "page":c.page,
                                        "chunk_index": c.chunk_index,
                                        "total_pages":c.total_pages} for c in chunks],
                            embeddings=embeddings)

        
    def query(self,query_embedding:list[float],top_k=5)->Hit:
        "this function will query the database and return top_k answers"
        results=self.collection.query(query_embeddings=query_embedding,n_results=top_k,include=["metadatas","documents","distances"])
        hits:list[Hit]=[]
        for i in range(len(results["ids"][0])):
            hits.append(
                Hit(id=results["ids"][0][i],
                    text=results["documents"][0][i],
                    metadata=results["metadatas"][0][i],
                    distance=results["distances"][0][i])
                    )
        return hits