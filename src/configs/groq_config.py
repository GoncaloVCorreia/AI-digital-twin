from typing import Type
from pydantic import BaseModel


class ConfigGroq(BaseModel):
    model_name: str = "openai/gpt-oss-20b"
    temperature: float = 0.0
    max_tokens: int = 512
    
    

    