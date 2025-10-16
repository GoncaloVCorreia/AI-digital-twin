"""
Testes adicionais para aumentar cobertura do módulo conversation.
Foca em cobrir linhas específicas não testadas anteriormente.
"""
import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4


@pytest.fixture
def sample_persona(db_session):
    """Cria uma persona de teste na BD."""
    from app.services.persona_service import PersonaService
    from app.schemas.persona import PersonaCreate
    
    persona_data = PersonaCreate(
        name="Coverage Test Dev",
        age=30,
        location="Porto",
        description="Test developer for coverage",
        education="CS Degree",
        tech_skills="Python",
        soft_skills="Testing",
        strenghts="Coverage",
        weaknesses="None",
        goals="100% coverage",
        hobbies="Testing",
        personality="Thorough"
    )
    
    return PersonaService.create_persona(db_session, persona_data, creator_id=1)


class TestChatRespondCoverage:
    """Testes para cobrir linhas específicas do POST /chat/respond (linhas 66-133)"""
    
    @patch("app.routers.conversation.get_runner")
    def test_chat_respond_auto_generate_session_id(
        self, mock_get_runner, authenticated_client, sample_persona
    ):
        """Testa geração automática de session_id quando não fornecido - linha 75."""
        mock_runner = MagicMock()
        mock_runner.stream_response.return_value = "Response"
        
        mock_snapshot = MagicMock()
        mock_snapshot.values = {
            "messages": [
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "Response"}
            ]
        }
        mock_runner.graph.get_state.return_value = mock_snapshot
        mock_get_runner.return_value = mock_runner
        
        payload = {
            "persona": sample_persona.name,
            "session_id": None,  # Deve gerar automaticamente
            "messages": [{"role": "user", "content": "Hi"}]
        }
        
        response = authenticated_client.post("/chat/respond", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"].startswith("session-")
        assert len(data["session_id"]) > len("session-")
    
    @patch("app.routers.conversation.get_runner")
    def test_chat_respond_with_custom_session_id(
        self, mock_get_runner, authenticated_client, sample_persona
    ):
        """Testa uso de session_id customizado - linha 75."""
        mock_runner = MagicMock()
        mock_runner.stream_response.return_value = "Response"
        
        mock_snapshot = MagicMock()
        mock_snapshot.values = {"messages": []}
        mock_runner.graph.get_state.return_value = mock_snapshot
        mock_get_runner.return_value = mock_runner
        
        custom_session = f"custom-{uuid4().hex[:8]}"
        payload = {
            "persona": sample_persona.name,
            "session_id": custom_session,
            "messages": [{"role": "user", "content": "Test"}]
        }
        
        response = authenticated_client.post("/chat/respond", json=payload)
        
        assert response.status_code == 200
        assert response.json()["session_id"] == custom_session
    
    @patch("app.routers.conversation.get_runner")
    @patch("app.routers.conversation.PersonaService.get_persona")
    def test_chat_respond_with_integer_persona_id(
        self, mock_get_persona, mock_get_runner, authenticated_client, sample_persona
    ):
        """Testa com persona ID como inteiro - linhas 83-85."""
        mock_get_persona.return_value = sample_persona
        
        mock_runner = MagicMock()
        mock_runner.stream_response.return_value = "Response"
        mock_snapshot = MagicMock()
        mock_snapshot.values = {"messages": []}
        mock_runner.graph.get_state.return_value = mock_snapshot
        mock_get_runner.return_value = mock_runner
        
        payload = {
            "persona": sample_persona.id,  # Integer ID
            "messages": [{"role": "user", "content": "Hi"}]
        }
        
        response = authenticated_client.post("/chat/respond", json=payload)
        
        assert response.status_code == 200
        mock_get_persona.assert_called_once()
    
    @patch("app.routers.conversation.get_runner")
    @patch("app.routers.conversation.PersonaService.get_persona")
    def test_chat_respond_with_string_numeric_persona_id(
        self, mock_get_persona, mock_get_runner, authenticated_client, sample_persona
    ):
        """Testa com persona ID como string numérica - linhas 83-85."""
        mock_get_persona.return_value = sample_persona
        
        mock_runner = MagicMock()
        mock_runner.stream_response.return_value = "Response"
        mock_snapshot = MagicMock()
        mock_snapshot.values = {"messages": []}
        mock_runner.graph.get_state.return_value = mock_snapshot
        mock_get_runner.return_value = mock_runner
        
        payload = {
            "persona": str(sample_persona.id),  # String numeric ID
            "messages": [{"role": "user", "content": "Hi"}]
        }
        
        response = authenticated_client.post("/chat/respond", json=payload)
        assert response.status_code == 200
    
    @patch("app.routers.conversation.get_runner")
    @patch("app.routers.conversation.PersonaService.get_by_name")
    def test_chat_respond_with_persona_name_string(
        self, mock_get_by_name, mock_get_runner, authenticated_client, sample_persona
    ):
        """Testa com nome de persona (string não-numérica) - linha 87."""
        mock_get_by_name.return_value = sample_persona
        
        mock_runner = MagicMock()
        mock_runner.stream_response.return_value = "Response"
        mock_snapshot = MagicMock()
        mock_snapshot.values = {"messages": []}
        mock_runner.graph.get_state.return_value = mock_snapshot
        mock_get_runner.return_value = mock_runner
        
        payload = {
            "persona": "Coverage Test Dev",  # String name
            "messages": [{"role": "user", "content": "Hi"}]
        }
        
        response = authenticated_client.post("/chat/respond", json=payload)
        
        assert response.status_code == 200
        mock_get_by_name.assert_called_once()
    
    @patch("app.routers.conversation.get_runner")
    def test_chat_respond_persona_not_found_exception(
        self, mock_get_runner, authenticated_client
    ):
        """Testa ValueError quando persona não existe - linha 90-91."""
        mock_runner = MagicMock()
        mock_get_runner.return_value = mock_runner
        
        payload = {
            "persona": "NonExistentPersona999",
            "messages": [{"role": "user", "content": "Hi"}]
        }
        
        response = authenticated_client.post("/chat/respond", json=payload)
        
        assert response.status_code == 400
        assert "Invalid persona" in response.json()["detail"]
    
    @patch("app.routers.conversation.get_runner")
    def test_chat_respond_uses_last_user_message(
        self, mock_get_runner, authenticated_client, sample_persona
    ):
        """Testa que usa última mensagem do user - linha 97."""
        mock_runner = MagicMock()
        mock_runner.stream_response.return_value = "Response to second"
        
        mock_snapshot = MagicMock()
        mock_snapshot.values = {"messages": []}
        mock_runner.graph.get_state.return_value = mock_snapshot
        mock_get_runner.return_value = mock_runner
        
        payload = {
            "persona": sample_persona.name,
            "messages": [
                {"role": "user", "content": "First message"},
                {"role": "assistant", "content": "Some response"},
                {"role": "user", "content": "Second message"}  # Esta deve ser usada
            ]
        }
        
        response = authenticated_client.post("/chat/respond", json=payload)
        
        assert response.status_code == 200
        # Verifica que chamou stream_response com a segunda mensagem
        call_kwargs = mock_runner.stream_response.call_args[1]
        assert call_kwargs["user_input"] == "Second message"
    
    @patch("app.routers.conversation.get_runner")
    def test_chat_respond_missing_user_message_raises_error(
        self, mock_get_runner, authenticated_client, sample_persona
    ):
        """Testa StopIteration quando não há mensagem user - linha 99."""
        mock_runner = MagicMock()
        mock_get_runner.return_value = mock_runner
        
        payload = {
            "persona": sample_persona.name,
            "messages": [
                {"role": "system", "content": "System"},
                {"role": "assistant", "content": "Assistant only"}
            ]
        }
        
        response = authenticated_client.post("/chat/respond", json=payload)
        
        assert response.status_code == 400
        assert "Missing user message" in response.json()["detail"]
    
    @patch("app.routers.conversation.get_runner")
    def test_chat_respond_calls_stream_response_correctly(
        self, mock_get_runner, authenticated_client, sample_persona
    ):
        """Testa chamada ao stream_response com parâmetros corretos - linhas 102-106."""
        mock_runner = MagicMock()
        mock_runner.stream_response.return_value = "AI generated response"
        
        mock_snapshot = MagicMock()
        mock_snapshot.values = {"messages": []}
        mock_runner.graph.get_state.return_value = mock_snapshot
        mock_get_runner.return_value = mock_runner
        
        session_id = f"test-{uuid4().hex[:6]}"
        payload = {
            "persona": sample_persona.name,
            "session_id": session_id,
            "messages": [{"role": "user", "content": "Test message"}]
        }
        
        response = authenticated_client.post("/chat/respond", json=payload)
        
        assert response.status_code == 200
        
        # Verifica argumentos da chamada
        mock_runner.stream_response.assert_called_once()
        call_kwargs = mock_runner.stream_response.call_args[1]
        assert call_kwargs["user_input"] == "Test message"
        assert call_kwargs["session_id"] == session_id
        assert "system_message" in call_kwargs
    
    @patch("app.routers.conversation.get_runner")
    def test_chat_respond_snapshot_with_messages(
        self, mock_get_runner, authenticated_client, sample_persona
    ):
        """Testa processamento de snapshot com mensagens - linhas 108-109."""
        mock_runner = MagicMock()
        mock_runner.stream_response.return_value = "Response"
        
        # Snapshot com múltiplas mensagens
        mock_snapshot = MagicMock()
        mock_snapshot.values = {
            "messages": [
                {"role": "system", "content": "System"},
                {"role": "user", "content": "User1"},
                {"role": "assistant", "content": "Asst1"},
                {"role": "user", "content": "User2"},
                {"role": "assistant", "content": "Response"}
            ]
        }
        mock_runner.graph.get_state.return_value = mock_snapshot
        mock_get_runner.return_value = mock_runner
        
        payload = {
            "persona": sample_persona.name,
            "messages": [{"role": "user", "content": "User2"}]
        }
        
        response = authenticated_client.post("/chat/respond", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Deve ter todas as mensagens do snapshot
        assert len(data["messages"]) == 5
    
    @patch("app.routers.conversation.get_runner")
    def test_chat_respond_empty_snapshot_uses_fallback(
        self, mock_get_runner, authenticated_client, sample_persona
    ):
        """Testa fallback quando snapshot vazio - linhas 111-117."""
        mock_runner = MagicMock()
        mock_runner.stream_response.return_value = "Fallback response"
        
        # Snapshot VAZIO
        mock_snapshot = MagicMock()
        mock_snapshot.values = {"messages": []}
        mock_runner.graph.get_state.return_value = mock_snapshot
        mock_get_runner.return_value = mock_runner
        
        payload = {
            "persona": sample_persona.name,
            "messages": [{"role": "user", "content": "Test"}]
        }
        
        response = authenticated_client.post("/chat/respond", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Fallback: system + user + assistant = 3 mensagens
        assert len(data["messages"]) == 3
        assert data["messages"][0]["role"] == "system"
        assert data["messages"][1]["role"] == "user"
        assert data["messages"][1]["content"] == "Test"
        assert data["messages"][2]["role"] == "assistant"
        assert data["messages"][2]["content"] == "Fallback response"
    
    @patch("app.routers.conversation.get_runner")
    def test_chat_respond_converts_messages_to_dict(
        self, mock_get_runner, authenticated_client, sample_persona
    ):
        """Testa conversão de mensagens para dict - linha 119."""
        from langchain_core.messages import HumanMessage, AIMessage
        
        mock_runner = MagicMock()
        mock_runner.stream_response.return_value = "Response"
        
        # Snapshot com objetos LangChain
        mock_snapshot = MagicMock()
        mock_snapshot.values = {
            "messages": [
                HumanMessage(content="User message"),
                AIMessage(content="AI message")
            ]
        }
        mock_runner.graph.get_state.return_value = mock_snapshot
        mock_get_runner.return_value = mock_runner
        
        payload = {
            "persona": sample_persona.name,
            "messages": [{"role": "user", "content": "User message"}]
        }
        
        response = authenticated_client.post("/chat/respond", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Deve converter LangChain messages para dicts
        assert all(isinstance(msg, dict) for msg in data["messages"])
        assert all("role" in msg and "content" in msg for msg in data["messages"])
    
    @patch("app.routers.conversation.get_runner")
    @patch("app.routers.conversation.ConversationService.create_conversation")
    def test_chat_respond_saves_conversation_to_db(
        self, mock_create_conv, mock_get_runner, authenticated_client, sample_persona
    ):
        """Testa salvamento da conversa na BD - linhas 122-130."""
        mock_runner = MagicMock()
        mock_runner.stream_response.return_value = "Response"
        
        mock_snapshot = MagicMock()
        mock_snapshot.values = {"messages": []}
        mock_runner.graph.get_state.return_value = mock_snapshot
        mock_get_runner.return_value = mock_runner
        
        # Mock do retorno de create_conversation
        mock_saved_conv = MagicMock()
        mock_saved_conv.id = 123
        mock_saved_conv.persona = sample_persona.name
        mock_saved_conv.session_id = "test-session"
        mock_saved_conv.messages = []
        mock_create_conv.return_value = mock_saved_conv
        
        payload = {
            "persona": sample_persona.name,
            "messages": [{"role": "user", "content": "Test"}]
        }
        
        response = authenticated_client.post("/chat/respond", json=payload)
        
        assert response.status_code == 200
        
        # Verifica que create_conversation foi chamado
        mock_create_conv.assert_called_once()
        call_args = mock_create_conv.call_args[0]
        conv_data = call_args[1]
        
        assert conv_data.persona == sample_persona.name
        assert isinstance(conv_data.messages, list)