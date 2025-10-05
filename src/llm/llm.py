from abc import ABC, abstractmethod
from dotenv import load_dotenv
import os
from configs.groq_config import ConfigGroq
from langchain_groq import ChatGroq

class LLM(ABC):
    def __init__(self, model_name: str, temperature: float = 0.3):
        self.model_name = model_name
        self.temperature = temperature

    @abstractmethod
    def invoke(self, messages):
        pass

#LLMS implementation for Groq
class GroqLLM(LLM):
    def __init__(self, config: ConfigGroq):
        super().__init__(config.model_name, config.temperature)
        load_dotenv()
        groq_api_key = os.environ.get("GROQ_API_KEY")
        
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )

    def invoke(self, messages):
        return self.llm.invoke(messages)

    