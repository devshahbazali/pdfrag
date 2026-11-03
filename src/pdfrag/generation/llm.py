import ollama
from typing import Protocol
from pdfrag.config import settings
class llmProvider(Protocol):
    def chat(self,message:list[dict],temprature:float)->str:...

class OllamaProvider:
    "provied the ollama client with default settings using env or using parameters "
    def __init__(self,
                 model:str| None =None,
                 host: str| None=None):
        self.model= model or settings.OLLAMA_MODEL
        self.client=ollama.Client(host=host or settings.OLLAMA_HOST)

    def chat(self,messages:list[dict],temprature:float=0.0):
        response=self.client.chat(model=self.model,
                                  messages=messages,
                                  options={"temprature":temprature})
        return response["message"]["content"]

    

def getllm()->llmProvider:
    llm = OllamaProvider()
    return llm

        