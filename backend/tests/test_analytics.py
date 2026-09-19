def test_analytics_revenue_no_jwt(client):
    response = client.get("/analytics/revenue?shop_id=1&interval=M")
    assert response.status_code == 401

def test_analytics_revenue_forged_jwt(client):
    headers = {"Authorization": "Bearer forged.jwt.token"}
    response = client.get("/analytics/revenue?shop_id=1&interval=M", headers=headers)
    assert response.status_code == 401

def test_ml_forecast_nonexistent_product(client):
    # To hit this, we need a valid JWT first
    # So we register and login
    client.post("/auth/register", json={"name": "Analytics User", "email": "analytics@example.com", "password": "password"})
    
    from tests.conftest import TestingSessionLocal
    from models.schemas import User
    db = TestingSessionLocal()
    user = db.query(User).first()
    if user:
        user.is_email_verified = True
        db.commit()
        user_email = user.email
    else:
        user_email = "analytics@example.com"
    db.close()

    login_resp = client.post("/auth/login", json={"email": user_email, "password": "password"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/ml/forecast?shop_id=1&product_id=99999", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "No historical data available for this product."
