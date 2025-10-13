def _register(client, email="user@demo.com", username="demo", password="Abcdefg1!"):
    return client.post("/auth/register", json={
        "email": email,
        "username": username,
        "full_name": username.title(),
        "password": password,
    })

def _login(client, username="demo", password="Abcdefg1!"):
    return client.post("/auth/login", data={"username": username, "password": password})

def test_register_and_login_flow(client):
    r = _register(client)
    assert r.status_code in (200, 201), r.text

    dup = _register(client, email="user@demo.com", username="other")
    assert dup.status_code in (400, 409)

    login = _login(client)
    assert login.status_code == 200
    data = login.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"

def test_login_invalid_credentials(client):
    r = _login(client, username="unknown", password="wrong")
    assert r.status_code in (400, 401)

def test_protected_route_requires_token(client):
    # register + login
    _register(client, email="p@q.com", username="paula")
    token = _login(client, username="paula").json()["access_token"]

    protected = "/personas/"  # rota protegida no teu projeto
    no_auth = client.get(protected)
    assert no_auth.status_code in (401, 403)

    ok = client.get(protected, headers={"Authorization": f"Bearer {token}"})
    assert ok.status_code == 200
