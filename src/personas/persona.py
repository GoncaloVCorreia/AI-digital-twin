import json
import os
from typing import List, Dict, Optional


class Persona:
    """
    Loads a persona from a JSON file and builds the corresponding system prompt.
    """

    def __init__(self, name: Optional[str] = None, persona_dir: str = "personas_json"):
        self.persona_dir = persona_dir
        self.name: Optional[str] = None
        self.age: Optional[int] = None
        self.location: Optional[str] = None
        self.summary: Optional[str] = None
        self.education: List[Dict[str, str]] = []
        self.skills: Dict[str, List[str]] = {}
        self.strengths: List[str] = []
        self.weaknesses: List[str] = []
        self.goals: List[str] = []

        # Auto-load if a persona name was given
        if name:
            self.load_persona(name)

    def load_persona(self, name: str) -> None:
        """Loads a persona JSON file and initializes instance variables."""
        path = os.path.join(self.persona_dir, f"persona_{name}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Persona file not found: {path}")

        with open(path, "r") as f:
            data = json.load(f)

        required_fields = ["name", "age", "location", "summary"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field '{field}' in {path}")

        self.name = data["name"]
        self.age = data["age"]
        self.location = data["location"]
        self.summary = data["summary"]
        self.education = data.get("education", [])
        self.skills = data.get("skills", {})
        self.strengths = data.get("strengths", [])
        self.weaknesses = data.get("weaknesses", [])
        self.goals = data.get("goals", [])

    def build_prompt(self) -> str:
        if not self.name:
            raise ValueError("No persona loaded. Call load_persona(name) first.")
        edu_str = ", ".join(
            [f"{edu['degree']} em {edu['institution']}" for edu in self.education]
        )
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
