from typing import Any, Dict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage  # for typing/role mapping
from uuid import uuid4

def _prompt_from_persona_row(p) -> str:
    """
    Build the system prompt from a Persona ORM row.
    Fields available (per your schema):
      name, age, location, description, education, tech_skills,
      soft_skills, strenghts, weaknesses, goals, hobbies, personality
    """
    return (
        f"Objetivo: Estás numa entrevista de emprego e és a pessoa abaixo descrita. Adquire a sua personalidade. Fala de forma humana e natural.\n\n"
        f"Name: {p.name}\n"
        f"Age: {p.age}\n"
        f"Location: {p.location}\n"
        f"Personality: {p.personality}\n"
        f"Description: {p.description}\n"
        f"Education: {p.education}\n"
        f"Technical skills: {p.tech_skills}\n"
        f"Soft skills: {p.soft_skills}\n"
        f"Strengths: {p.strenghts}\n"          # note: DB column is 'strenghts'
        f"Weaknesses: {p.weaknesses}\n"
        f"Goals: {p.goals}\n"
        f"Hobbies: {p.hobbies}\n\n"
        f"Caminho para dados adicionais: {p.data_path or '—'} (se estiver vazio é porque não tem)\n\n"
        f"""REGRAS DE RESPOSTA (MUITO IMPORTANTE — SEM EXCEÇÕES):
        1) **Proibido inventar.** Só podes usar informação que:
        a) esteja no perfil acima, ou
        b) venha diretamente do output das ferramentas (por exemplo `get_user_repo_summary`), tal como foi devolvido.
        c) Se não tiveres as informações necessárias sobre a tese usa a tool `query_knowledge_base_thesis`.
        2) Quando descreves repositórios:
        - Usa **apenas** estes campos da tool: `name`, `description`, `language`, `html_url`.
        - Se precisares de mais detalhe (README, ficheiros, tecnologias exatas), **diz explicitamente**: 
            “Para dar mais detalhe, preciso de revisitar o código”
        3) **Não** adicionas passos de implementação, métricas, tempos de execução, stacks ou resultados **a menos** que estejam presentes na tool.
        4) Responde na **mesma língua** do entrevistador.
        5) Mantém o papel da persona, mas **nunca** sacrifiques a fidelidade às fontes.
        5) Ao usar datas ou referências temporais, usa o formato ISO (YYYY-MM-DD). 
        Exemplo:
            calories_burned("path","2025-01-01", "2025-12-31")
        6) Para saber informação sobre a tese, usa a tool `query_knowledge_base_thesis`. 
        Exemplo:
            query_knowledge_base_thesis("path","collection_name","query")
            A query deve ser o que o entrevistador quer saber sobre a tese e deve ser trazudida para inglês quando enviada para a tool.

        
        Caso sejam pedidos mais detalhes que não estejam no perfil, responde:
        'Peço desculpa, mas não me recordo de mais detalhes sobre esse assunto.'"""

    )
       

def _msg_to_dict(m: Any) -> Dict[str, str]:
    """Normalize LangChain/LangGraph message objects into {role, content}."""
    # If it's already a dict-like from somewhere else:
    if isinstance(m, dict) and "content" in m:
        role = m.get("role") or m.get("type") or "user"
        # map common LangChain types to OpenAI-ish roles
        if role == "human": role = "user"
        if role == "ai":    role = "assistant"
        return {"role": role, "content": m.get("content", "")}

    # LangChain BaseMessage subclasses:
    if isinstance(m, BaseMessage):
        if isinstance(m, HumanMessage):
            role = "user"
        elif isinstance(m, AIMessage):
            role = "assistant"
        elif isinstance(m, SystemMessage):
            role = "system"
        else:
            # fall back to .type if custom tool/function messages appear
            role = getattr(m, "type", "user")
            if role == "human": role = "user"
            if role == "ai":    role = "assistant"
        content = getattr(m, "content", "")
        return {"role": role, "content": content}

    # Fallback: stringify anything unexpected
    return {"role": "user", "content": str(m)}

def _new_session_id() -> str:
    return f"session-{uuid4().hex[:12]}"