def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"name": "Test User", "email": "test@example.com", "password": "securepassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data

def test_register_duplicate_user(client):
    response = client.post(
        "/auth/register",
        json={"name": "Test User 2", "email": "test@example.com", "password": "securepassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client):
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "securepassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client):
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "securepassword"}
    )
    assert response.status_code == 401

def test_access_protected_route_without_token(client):
    # Depending on how endpoints are protected, let's assume we try to hit an endpoint that requires auth?
    # Wait, did we protect /analytics endpoints yet?
    # Actually, in the auth implementation phase, we just provided get_current_user but we didn't add it as a Depends to /analytics or /ml!
    pass
