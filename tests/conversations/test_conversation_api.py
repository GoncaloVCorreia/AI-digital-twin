import pytest
from uuid import uuid4


@pytest.fixture
def sample_persona(db_session):
    """Cria uma persona de teste na BD."""
    from app.services.persona_service import PersonaService
    from app.schemas.persona import PersonaCreate
    
    persona_data = PersonaCreate(
        name="Test Developer",
        age=28,
        location="Lisbon",
        description="A software developer",
        education="Computer Science Degree",
        tech_skills="Python, FastAPI, PostgreSQL",
        soft_skills="Communication, Teamwork",
        strenghts="Problem solving, Quick learner",
        weaknesses="Perfectionism",
        goals="Become a senior developer",
        hobbies="Reading, Gaming",
        personality="Friendly and curious"
    )
    
    # PersonaService.create_persona precisa de creator_id
    return PersonaService.create_persona(db_session, persona_data, creator_id=1)


@pytest.fixture
def sample_conversation(db_session, sample_persona):
    """Cria uma conversa de teste."""
    from app.services.conversation_service import ConversationService
    from app.schemas.conversation import ConversationDBCreate
    
    conv_data = ConversationDBCreate(
        interviewer_id=1,
        persona=sample_persona.name,
        session_id=f"test-session-{uuid4().hex[:8]}",
        messages=[
            {"role": "system", "content": "You are Test Developer"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
    )
    
    # create_conversation já faz commit internamente
    return ConversationService.create_conversation(db_session, conv_data)


class TestListConversations:
    """Testes para GET /chat/conversations"""
    
    def test_list_conversations_success(self, authenticated_client, sample_conversation):
        """Deve listar todas as conversas."""
        response = authenticated_client.get("/chat/conversations")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verifica estrutura da resposta
        conv = data[0]
        assert "id" in conv
        assert "interviewer_id" in conv
        assert "persona" in conv
        assert "session_id" in conv
        assert "messages" in conv
        assert "created_at" in conv
        
        # Verifica que encontra a conversa criada
        found = any(c["session_id"] == sample_conversation.session_id for c in data)
        assert found, "Conversa criada não foi encontrada na lista"
    
    def test_list_conversations_empty(self, authenticated_client, db_session):
        """Deve retornar lista vazia quando não há conversas."""
        # Limpa todas as conversas primeiro
        from app.models.conversation import Conversation
        db_session.query(Conversation).delete()
        db_session.commit()
        
        response = authenticated_client.get("/chat/conversations")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_list_conversations_unauthorized(self, client):
        """Deve rejeitar pedidos sem autenticação."""
        response = client.get("/chat/conversations")
        assert response.status_code in [401, 403]  # Aceita tanto 401 quanto 403
    
    def test_list_conversations_ordered_by_newest(self, authenticated_client, db_session, sample_persona):
        """Deve retornar conversas ordenadas da mais recente para a mais antiga."""
        from app.services.conversation_service import ConversationService
        from app.schemas.conversation import ConversationDBCreate
        import time
        
        # Cria 3 conversas com delay para garantir ordem
        sessions = []
        for i in range(3):
            conv_data = ConversationDBCreate(
                interviewer_id=1,
                persona=sample_persona.name,
                session_id=f"test-session-{i}-{uuid4().hex[:4]}",
                messages=[{"role": "user", "content": f"Message {i}"}]
            )
            conv = ConversationService.create_conversation(db_session, conv_data)
            sessions.append(conv.session_id)
            time.sleep(0.01)  # Pequeno delay para garantir timestamps diferentes
        
        response = authenticated_client.get("/chat/conversations")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verifica que estão ordenadas por created_at descendente
        if len(data) >= 2:
            for i in range(len(data) - 1):
                assert data[i]["created_at"] >= data[i + 1]["created_at"]