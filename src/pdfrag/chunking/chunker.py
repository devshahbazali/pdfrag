from pdfrag.config import settings
from pdfrag.chunking.splitter import split_text
from pdfrag.chunking.models import Chunk
from pdfrag.ingestion.models import Document
def _chunk_document(doc:Document)->list[Chunk]:
    if not doc:
        print("no Document provided to chunk method")
        return []

    
    raw_chunks= split_text(doc.text)
    chunks:list[Chunk]=[]
    for i, piece in enumerate(raw_chunks,start=1):
      chunks.append(
         Chunk(  text=piece, 
                 source=doc.source,
                 page=doc.page,
                 chunk_index=i,
                 total_pages=doc.total_pages)
                ) 

    return chunks

def chunk_documents(docs:list[Document])->list[Chunk]:
    if not docs:
        print("No Documents available")
        return []
    
    chunks:list[Chunk]=[]
    for doc in docs:
        one_doc_chunks=_chunk_document(doc)
        chunks.extend(one_doc_chunks)

    return(chunks)