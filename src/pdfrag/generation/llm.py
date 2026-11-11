import ollama
from typing import Protocol
from pdfrag.config import settings
from openai import OpenAI
class llmProvider(Protocol):
    def chat(self,message:list[dict],temperature:float)->str:...

class OllamaProvider:
    "provied the ollama client with default settings using env or using parameters "
    def __init__(self,
                 model:str| None =None,
                 host: str| None=None):
        self.model= model or settings.OLLAMA_MODEL
        self.client=ollama.Client(host=host or settings.OLLAMA_HOST)

    def chat(self,messages:list[dict],temperature:float=0.0):
        response=self.client.chat(model=self.model,
                                  messages=messages,
                                  options={"temperature":temperature})
        return response["message"]["content"]

class OpenAIProvider:
    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None
    ):
        self.model = model or settings.OPENAI_MODEL
        self.client = OpenAI(
            api_key=api_key or settings.OPENAI_API_KEY
        )

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.0
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )

        return response.choices[0].message.content or ""

    

def getllm(provider: str | None = None)->llmProvider:
    provider = (
        provider or settings.LLM_PROVIDER
                ).lower()
    print("got this provider ", provider)
    if provider == "ollama":
        print("olaama is used #################")
        return OllamaProvider()

    elif provider == "openai":
        print("openai IS being used##############")
        return OpenAIProvider()

        