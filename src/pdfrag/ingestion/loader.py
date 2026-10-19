from pathlib import Path
from pdfrag.ingestion.models import Document
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from pdfrag.config import settings
file_name="Report.pdf"

def _load_pdf(path:Path=None)-> list[Document]:
    "load the pdf and make one document of each page"
    path: Path= path or settings.PDF_PATH / file_name
    try:
        reader=PdfReader(str(path))
    except PdfReadError as e:
        print("failed oto load pdf \nError occured:",e)
        return []
    
    pdf_length=len(reader.pages)
    documents:list[Document]=[]

    for i, page in enumerate(reader.pages,start=1):
        documents.append(Document(text=page.extract_text().strip()
                                  ,source=path.name,page=i,total_pages=pdf_length))

   
    return documents

def load_all_pdfs(pdf_dir:Path=None)->list[Document]:
    "load all pdfs and return a list of document. 1 page is = 1 document"
    pdf_dir = pdf_dir or settings.PDF_PATH
    all_Documnets:list[Document]=[]
    if not pdf_dir:
        print("pdf directory not found")
        return[]
    
    pdf_paths:list[Path]=pdf_dir.glob("*.pdf")
    if not pdf_paths:
        print("No pdf file found in directory")
        return[]
    
    for path in pdf_paths:
        Documents:list[Document]=_load_pdf(path)
        all_Documnets.extend(Documents)

    return all_Documnets
    