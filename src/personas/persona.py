from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict
import json, os

class PersonaModel(BaseModel):
    name: str
    age: int
    location: str
    summary: str
    education: List[Dict[str, str]] = Field(default_factory=list)
    skills: Dict[str, List[str]] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)

    def build_prompt(self) -> str:
        edu_str = ", ".join(f"{e['degree']} em {e['institution']}" for e in self.education)
        return f"""
        Tu és o {self.name} ({self.age} anos, de {self.location}).
        Resumo: {self.summary}
        Formação: {edu_str}.
        Competências técnicas: {', '.join(self.skills.get('technical', []))}.
        Competências interpessoais: {', '.join(self.skills.get('soft', []))}.
        Pontos fortes: {', '.join(self.strengths)}.
        Pontos fracos: {', '.join(self.weaknesses)}.
        Objetivos: {', '.join(self.goals)}.

        Responde sempre como se fosses {self.name} numa entrevista de emprego.
        Responde de forma concisa e direta.
        Não inventes informação que não esteja no perfil.
        Caso o input recebido não faça sentido, pede para reformular a pergunta.
        """

def load_persona(name: str, persona_dir: str = "personas_json") -> PersonaModel:
    path = os.path.join(persona_dir, f"persona_{name}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Persona file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    try:
        return PersonaModel(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid persona file {path}:\n{e}")
