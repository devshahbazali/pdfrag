from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env"
                                    ,env_file_encoding="utf-8",
                                    extra="ignore")


    OLLAMA_HOST :str = "http://localhost:11434"
    OLLAMA_MODEL :str = "llama3.2:1b"
    EMBEDDING_MODEL :str ="all-MiniLM-L6-v2"
    CHUNK_SIZE:int=800
    CHUNK_OVERLAP:int= 150
    TOP_K:int=5
    PDF_PATH:Path=Path(__file__).resolve()  /"data" / "pdf"
    CHROMA_PATH:Path=Path(__file__).resolve()  /"data" / "chroma"

settings=Settings()
