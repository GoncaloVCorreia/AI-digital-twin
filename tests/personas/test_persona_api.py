import pytest
from .factories import make_persona_create, make_persona_update


def test_create_persona_success(authenticated_client):
    """Testa criação de persona com sucesso."""
    payload = make_persona_create(name="Test Persona", location="Porto").model_dump()
    
    response = authenticated_client.post("/personas/", json=payload)
    assert response.status_code == 201, response.text
    
    data = response.json()
    assert data["name"] == "Test Persona"
    assert data["location"] == "Porto"
    assert "id" in data
    assert isinstance(data["id"], int)


def test_create_persona_requires_auth(client):
    """Testa que criar persona sem autenticação falha."""
    payload = make_persona_create().model_dump()
    
    response = client.post("/personas/", json=payload)
    assert response.status_code in (401, 403)


def test_get_persona_by_id(authenticated_client):
    """Testa obter persona por ID."""
    # Cria persona primeiro
    payload = make_persona_create(name="Get Test").model_dump()
    create_response = authenticated_client.post("/personas/", json=payload)
    persona_id = create_response.json()["id"]
    
    # Obtém persona
    response = authenticated_client.get(f"/personas/{persona_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == persona_id
    assert data["name"] == "Get Test"


def test_get_persona_not_found(authenticated_client):
    """Testa obter persona inexistente."""
    response = authenticated_client.get("/personas/99999")
    assert response.status_code == 404


def test_list_personas_empty(authenticated_client):
    """Testa listar personas quando não há nenhuma."""
    response = authenticated_client.get("/personas/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_update_persona_success(authenticated_client):
    """Testa atualização de persona."""
    # Cria persona
    payload = make_persona_create(name="Original", location="Porto").model_dump()
    create_response = authenticated_client.post("/personas/", json=payload)
    persona_id = create_response.json()["id"]
    
    # Atualiza
    update_payload = make_persona_update(location="Lisboa", description="Updated desc").model_dump(exclude_unset=True)
    response = authenticated_client.put(f"/personas/{persona_id}", json=update_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["location"] == "Lisboa"
    assert data["description"] == "Updated desc"
    assert data["name"] == "Original"  # não mudou


def test_delete_persona_success(authenticated_client):
    """Testa remoção de persona."""
    # Cria persona
    payload = make_persona_create(name="To Delete").model_dump()
    create_response = authenticated_client.post("/personas/", json=payload)
    persona_id = create_response.json()["id"]
    
    # Remove
    response = authenticated_client.delete(f"/personas/{persona_id}")
    assert response.status_code == 204
    
    # Verifica que não existe mais
    get_response = authenticated_client.get(f"/personas/{persona_id}")
    assert get_response.status_code == 404