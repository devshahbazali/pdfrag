from pydantic import BaseModel, Field

class Document(BaseModel):
        text: str= Field(...,description="The text cotent of the page")
        source: str=Field(..., description="File name of pdf source")
        page: int=Field(...,ge=1,description="page number indexed")
        total_pages:int= Field(...,ge=1,description="total pages in source pdf document")

        def __repr__(self):
            preview= self.text[:60].replace("\n","")
            return f"Document: {self.source} pages: {self.page}/{self.total_pages}   Preview:'{preview}' "