from pydantic import BaseModel,Field

class chunk(BaseModel):
    #A chucnk of text ready to be embedded

    text:str=Field(...,description="chuck of the document text")
    source:str=Field(...,description="file name of source pdf")
    page:int= Field(..., ge=1,description="page number in source pdf")
    chunk_index:int=Field(...,ge=0,description="position of this chunck in the page")
    total_pages:int= Field(..., ge=1, description="total pages in the souurce pdf")
    
    @property
    def chunk_id(self):
        #chunck unique id across the whole index
        return f"{self.source}::p{self.page}::c{self.chunk_index}"
    
    def __repr__(self) -> str:
        preview = self.text[:50].replace("\n", " ")
        return f"<Chunk {self.chunk_id}: '{preview}...'>" 