import pytest
from unittest.mock import Mock
from app.utils.conversation import _prompt_from_persona_row, _msg_to_dict, _new_session_id
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage


class TestPromptFromPersonaRow:
    """Testes para _prompt_from_persona_row"""
    
    def test_prompt_with_all_fields(self):
        """Deve criar prompt completo."""
        persona = Mock()
        persona.name = "João Silva"
        persona.age = 30
        persona.location = "Porto"
        persona.personality = "Extrovertido"
        persona.description = "Developer"
        persona.education = "Computer Science"
        persona.tech_skills = "Python, JavaScript"
        persona.soft_skills = "Communication"
        persona.strenghts = "Problem solving"
        persona.weaknesses = "Perfectionism"
        persona.goals = "Become tech lead"
        persona.hobbies = "Gaming"
        
        result = _prompt_from_persona_row(persona)
        
        assert "João Silva" in result
        assert "30" in result
        assert "Porto" in result
        assert "Stay in character" in result


class TestMsgToDict:
    """Testes para _msg_to_dict"""
    
    def test_dict_with_role_and_content(self):
        """Deve converter dict simples."""
        msg = {"role": "user", "content": "Hello"}
        result = _msg_to_dict(msg)
        
        assert result == {"role": "user", "content": "Hello"}
    
    def test_dict_human_to_user(self):
        """Deve mapear 'human' para 'user'."""
        msg = {"role": "human", "content": "Hi"}
        result = _msg_to_dict(msg)
        
        assert result["role"] == "user"
    
    def test_dict_ai_to_assistant(self):
        """Deve mapear 'ai' para 'assistant'."""
        msg = {"role": "ai", "content": "Response"}
        result = _msg_to_dict(msg)
        
        assert result["role"] == "assistant"
    
    def test_langchain_human_message(self):
        """Deve converter HumanMessage."""
        msg = HumanMessage(content="Hello from human")
        result = _msg_to_dict(msg)
        
        assert result["role"] == "user"
        assert result["content"] == "Hello from human"
    
    def test_langchain_ai_message(self):
        """Deve converter AIMessage."""
        msg = AIMessage(content="AI response")
        result = _msg_to_dict(msg)
        
        assert result["role"] == "assistant"
    
    def test_langchain_system_message(self):
        """Deve converter SystemMessage."""
        msg = SystemMessage(content="System prompt")
        result = _msg_to_dict(msg)
        
        assert result["role"] == "system"


class TestNewSessionId:
    """Testes para _new_session_id"""
    
    def test_generates_valid_session_id(self):
        """Deve gerar session_id válido."""
        session_id = _new_session_id()
        
        assert session_id.startswith("session-")
        assert len(session_id) > len("session-")
    
    def test_generates_unique_ids(self):
        """Deve gerar IDs únicos."""
        ids = [_new_session_id() for _ in range(50)]
        
        assert len(ids) == len(set(ids))