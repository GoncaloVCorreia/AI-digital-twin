from uuid import uuid4
from app.schemas.persona import PersonaCreate, PersonaUpdate

def make_persona_create(**overrides):
    base = {
        "name": f"Persona-{uuid4().hex[:8]}",
        "age": 30,
        "location": "Porto",
        "description": "Desc",
        "education": "Lic",
        "tech_skills": "Python, SQL",
        "soft_skills": "Comunicação",
        "strenghts": "Resiliente",
        "weaknesses": "Impaciente",
        "goals": "Aprender",
        "hobbies": "Correr",
        "personality": "Extrovertido",
    }
    base.update(overrides)
    return PersonaCreate(**base)

def make_persona_update(**overrides):
    base = {
        "location": "Lisboa",
        "description": "Atualizada",
    }
    base.update(overrides)
    return PersonaUpdate(**base)
