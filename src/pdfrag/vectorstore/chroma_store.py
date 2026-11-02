from pathlib import Path
from typing import Any
import chromadb 
from chromadb.config import Settings as ChromaSettings

from pdfrag.chunking.models import Chunk
from pdfrag.config import settings

COLLECTION_NAME="ragpdf"

METADATA={"hnsw:space":"cosine"}

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
        self.collection=self.client.get_or_create_collection(name=COLLECTION_NAME,settings=ChromaSettings)

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

        
    def query(self,query_embedding:list[float],top_k=5)->list[dict[str,any]]:
        "this function will query the database and return top_k answers"
        results=self.collection.query(query_embeddings=query_embedding,n_results=top_k,include=["metadatas","documents","distances"])
        hits:list[dict[str,Any]]=[]
        for i in range(len(results["ids"][0])):
            hits.append(
                {
                    "id":results["ids"][0][i],
                    "text":results["documents"][0][i],
                    "metadata":results["metadatas"][0][i],
                    "distance":results["distances"][0][i],
                }
            )
        return hits