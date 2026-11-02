from pdfrag.config import settings
from pdfrag.ingestion.loader import load_all_pdfs
from pdfrag.chunking.chunker import chunk_documents
from pdfrag.embeddings.embedder import embed_texts,embed_query
from pathlib import Path
from pdfrag.vectorstore.chroma_store import ChromaStore

def indexDocuments(reset=False)-> ChromaStore:
    'function to load -> chunk -> embed -> store documents in chroma db'
    store=ChromaStore()
    #reset will remove the records from chromadb and give back new db 
    if reset:
        print("resetting collection...")
        store.reset()
        print("Store is reset.")

    docs=load_all_pdfs()

    if not docs:
        print("documents found to load...")
        return store

    
    print(len(docs)," pages loaded.")
    print("Chunking Documets...")
    chunks=chunk_documents(docs=docs)
    print("embedding the chunks...")
    embeddings= embed_texts([ chunk.text for chunk in chunks  ])
    print("Storing in Database")
    store.addChunks(chunks=chunks,embeddings=embeddings)
    print(store.count() , " Chunks are successfully indexed in Db...")
    return store

