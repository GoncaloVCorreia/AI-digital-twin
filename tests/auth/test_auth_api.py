"""Testes para endpoints de autenticação."""
def _register(client, email="user@demo.com", username="demo", password="Abcdefg1!"):
    """Helper para registar utilizador."""
    return client.post("/auth/register", json={
        "email": email,
        "username": username,
        "full_name": username.title(),
        "password": password,
    })


def _login(client, username="demo", password="Abcdefg1!"):
    """Helper para fazer login."""
    return client.post("/auth/login", data={"username": username, "password": password})


def test_register_success(client):
    """Testa registo de utilizador com sucesso."""
    response = _register(client, email="newuser@test.com", username="newuser")
    assert response.status_code in (200, 201), response.text
    
    data = response.json()
    assert "id" in data
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@test.com"
    assert "hashed_password" not in data  # não deve expor password


def test_register_duplicate_email(client):
    """Testa registo com email duplicado."""
    _register(client, email="dup@test.com", username="user1")
    
    # Tenta registar com mesmo email mas username diferente
    dup_response = _register(client, email="dup@test.com", username="user2")
    assert dup_response.status_code in (400, 409)


def test_register_duplicate_username(client):
    """Testa registo com username duplicado."""
    _register(client, email="test1@test.com", username="sameuser")
    
    # Tenta registar com mesmo username mas email diferente
    dup_response = _register(client, email="test2@test.com", username="sameuser")
    assert dup_response.status_code in (400, 409)


def test_register_and_login_flow(client):
    """Testa fluxo completo de registo e login."""
    # Regista
    reg_response = _register(client, email="flow@test.com", username="flowuser")
    assert reg_response.status_code in (200, 201), reg_response.text
    
    # Faz login
    login_response = _login(client, username="flowuser", password="Abcdefg1!")
    assert login_response.status_code == 200
    
    data = login_response.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"
    assert data.get("username") == "flowuser"


def test_login_invalid_username(client):
    """Testa login com username inexistente."""
    response = _login(client, username="nonexistent", password="Abcdefg1!")
    assert response.status_code in (400, 401)


def test_login_invalid_password(client):
    """Testa login com password errada."""
    # Regista utilizador
    _register(client, email="wrong@test.com", username="wrongpass")
    
    # Tenta login com password errada
    response = _login(client, username="wrongpass", password="WrongPass123!")
    assert response.status_code in (400, 401)


def test_login_empty_credentials(client):
    """Testa login com credenciais vazias."""
    response = client.post("/auth/login", data={"username": "", "password": ""})
    assert response.status_code in (400, 401, 422)


def test_protected_route_without_token(client):
    """Testa acesso a rota protegida sem token."""
    response = client.get("/personas/")
    assert response.status_code in (401, 403)


def test_protected_route_with_invalid_token(client):
    """Testa acesso a rota protegida com token inválido."""
    response = client.get(
        "/personas/",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code in (401, 403)


def test_protected_route_with_valid_token(client):
    """Testa acesso a rota protegida com token válido."""
    # Regista e faz login
    _register(client, email="protected@test.com", username="protecteduser")
    login_response = _login(client, username="protecteduser", password="Abcdefg1!")
    token = login_response.json()["access_token"]
    
    # Acede a rota protegida
    response = client.get(
        "/personas/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_token_contains_required_fields(client):
    """Testa se o token JWT contém os campos necessários."""
    _register(client, email="jwt@test.com", username="jwtuser")
    response = _login(client, username="jwtuser", password="Abcdefg1!")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "username" in data
    assert data["username"] == "jwtuser"


def test_register_invalid_email_format(client):
    """Testa registo com email inválido."""
    response = client.post("/auth/register", json={
        "email": "not_an_email",
        "username": "testuser",
        "full_name": "Test User",
        "password": "Abcdefg1!"
    })
    assert response.status_code == 422  


def test_register_password_too_short(client):
    """Testa registo com password muito curta."""
    response = client.post("/auth/register", json={
        "email": "short@test.com",
        "username": "shortpass",
        "full_name": "Short Pass",
        "password": "Short1!"  
    })
    assert response.status_code == 422


def test_register_password_no_uppercase(client):
    """Testa registo com password sem maiúsculas."""
    response = client.post("/auth/register", json={
        "email": "nouppercase@test.com",
        "username": "nouppercase",
        "full_name": "No Upper",
        "password": "abcdefg1!" 
    })
    assert response.status_code == 422


def test_register_password_no_digit(client):
    """Testa registo com password sem dígitos."""
    response = client.post("/auth/register", json={
        "email": "nodigit@test.com",
        "username": "nodigit",
        "full_name": "No Digit",
        "password": "Abcdefgh!"  # sem números
    })
    assert response.status_code == 422


def test_register_username_too_short(client):
    """Testa registo com username muito curto."""
    response = client.post("/auth/register", json={
        "email": "shortuser@test.com",
        "username": "ab",  
        "full_name": "Short User",
        "password": "Abcdefg1!"
    })
    assert response.status_code == 422


def test_multiple_users_can_login_independently(client):
    """Testa que múltiplos utilizadores podem fazer login independentemente."""
 
    _register(client, email="user1@test.com", username="user1", password="Pass1word!")
    _register(client, email="user2@test.com", username="user2", password="Pass2word!")
  
    login1 = _login(client, username="user1", password="Pass1word!")
    login2 = _login(client, username="user2", password="Pass2word!")
    
    assert login1.status_code == 200
    assert login2.status_code == 200
    
    token1 = login1.json()["access_token"]
    token2 = login2.json()["access_token"]
    
    # Tokens devem ser diferentes
    assert token1 != token2