from tests.conftest import TestingSessionLocal
from models.schemas import User
from unittest.mock import patch
import time

def verify_user(email: str):
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.is_email_verified = True
        db.commit()
    db.close()

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

def test_unverified_login_rejection(client):
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "securepassword"}
    )
    assert response.status_code == 403
    assert "not verified" in response.json()["detail"].lower()

@patch("routers.auth.send_otp_email")
def test_full_otp_flow(mock_send_otp, client):
    mock_send_otp.return_value = True
    
    # 1. Register new user
    response = client.post(
        "/auth/register",
        json={"name": "OTP User", "email": "otp@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    
    # Extract the plaintext OTP sent to the email mock
    assert mock_send_otp.called
    plaintext_otp = mock_send_otp.call_args[0][1]
    
    # 2. Invalid OTP
    verify_resp = client.post("/auth/verify-email", json={"email": "otp@example.com", "otp": "999999"})
    assert verify_resp.status_code == 400
    assert verify_resp.json()["detail"] == "Invalid OTP"
    
    # 3. Valid OTP
    verify_resp2 = client.post("/auth/verify-email", json={"email": "otp@example.com", "otp": plaintext_otp})
    assert verify_resp2.status_code == 200
    assert verify_resp2.json()["message"] == "Email verified successfully"
    
    # 4. OTP Invalidation (trying again)
    verify_resp3 = client.post("/auth/verify-email", json={"email": "otp@example.com", "otp": plaintext_otp})
    assert verify_resp3.status_code == 400
    assert verify_resp3.json()["detail"] == "OTP expired or not found"
    
    # 5. Login after verification
    login_resp = client.post("/auth/login", json={"email": "otp@example.com", "password": "password123"})
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

@patch("routers.auth.send_otp_email")
def test_otp_attempt_limit_and_resend(mock_send_otp, client):
    mock_send_otp.return_value = True
    
    client.post("/auth/register", json={"name": "Limit User", "email": "limit@example.com", "password": "password123"})
    
    # Fail 3 times
    for _ in range(3):
        resp = client.post("/auth/verify-email", json={"email": "limit@example.com", "otp": "000000"})
        assert resp.status_code == 400
        
    # 4th time should say "Too many failed attempts" or similar
    resp4 = client.post("/auth/verify-email", json={"email": "limit@example.com", "otp": "000000"})
    assert resp4.status_code == 400
    assert "Too many failed attempts" in resp4.json()["detail"]
    
    # Test Resend OTP
    resend_resp = client.post("/auth/resend-otp", json={"email": "limit@example.com"})
    assert resend_resp.status_code == 200
    
    # Test Resend Cooldown
    resend_resp2 = client.post("/auth/resend-otp", json={"email": "limit@example.com"})
    assert resend_resp2.status_code == 429
    assert "wait" in resend_resp2.json()["detail"].lower()

@patch("routers.auth.send_otp_email")
def test_smtp_failure_handling(mock_send_otp, client):
    mock_send_otp.return_value = False # Simulate SMTP failure
    
    response = client.post(
        "/auth/register",
        json={"name": "Fail User", "email": "fail@example.com", "password": "password123"}
    )
    assert response.status_code == 500
    assert "failed to send otp email" in response.json()["detail"].lower()

def test_register_duplicate_user(client):
    verify_user("test@example.com")
    response = client.post(
        "/auth/register",
        json={"name": "Test User 2", "email": "test@example.com", "password": "securepassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered and verified."

def test_login_success(client):
    verify_user("test@example.com")
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "securepassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client):
    verify_user("test@example.com")
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
