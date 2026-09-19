import pytest
from tests.conftest import TestingSessionLocal
from models.schemas import User, Shop, Product, Sale
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(scope="module")
def ai_isolation_data():
    db = TestingSessionLocal()
    
    # User A
    user_a = User(
        name="User A", email="user_a@example.com", 
        password_hash=pwd_context.hash("password"), is_email_verified=True
    )
    db.add(user_a)
    db.commit()
    db.refresh(user_a)
    
    shop_a = Shop(owner_id=user_a.id, name="Shop A", category="Electronics", location="NYC")
    db.add(shop_a)
    db.commit()
    db.refresh(shop_a)
    
    product_a = Product(shop_id=shop_a.id, product_code="A1", name="Product A", category="Electronics", purchase_price=10, selling_price=20, current_stock=100)
    db.add(product_a)
    db.commit()
    db.refresh(product_a)
    
    sale_a = Sale(shop_id=shop_a.id, product_id=product_a.id, quantity=1, total_price=20, profit=10, timestamp=datetime.utcnow())
    db.add(sale_a)
    db.commit()
    
    # User B
    user_b = User(
        name="User B", email="user_b@example.com", 
        password_hash=pwd_context.hash("password"), is_email_verified=True
    )
    db.add(user_b)
    db.commit()
    db.refresh(user_b)
    
    shop_b = Shop(owner_id=user_b.id, name="Shop B", category="Grocery", location="LA")
    db.add(shop_b)
    db.commit()
    db.refresh(shop_b)
    
    product_b = Product(shop_id=shop_b.id, product_code="B1", name="Product B", category="Grocery", purchase_price=5, selling_price=10, current_stock=50)
    db.add(product_b)
    db.commit()
    db.refresh(product_b)
    
    sale_b = Sale(shop_id=shop_b.id, product_id=product_b.id, quantity=2, total_price=20, profit=10, timestamp=datetime.utcnow())
    db.add(sale_b)
    db.commit()
    
    db.close()
    
    return {
        "user_a_email": "user_a@example.com",
        "user_b_email": "user_b@example.com",
    }

def test_ai_isolation(client, ai_isolation_data, monkeypatch):
    # Mock AI response so we don't actually hit Gemini in tests
    # Instead, we just check if the temporary DB contains ONLY the right shop's data
    
    called_db_paths = []
    
    import services.ai_service as ai_service
    original_ask_database = ai_service.ask_database
    
    # We will test the underlying _create_isolated_ai_db directly 
    # to guarantee the data going to the LLM is isolated.
    from tests.conftest import TestingSessionLocal
    import pandas as pd
    import sqlite3
    
    db = TestingSessionLocal()
    
    # Get Shop A
    user_a = db.query(User).filter(User.email == ai_isolation_data["user_a_email"]).first()
    shop_a = db.query(Shop).filter(Shop.owner_id == user_a.id).first()
    
    # Get Shop B
    user_b = db.query(User).filter(User.email == ai_isolation_data["user_b_email"]).first()
    shop_b = db.query(Shop).filter(Shop.owner_id == user_b.id).first()
    
    # 1. Create DB for User A and inspect contents
    temp_db_path_a = ai_service._create_isolated_ai_db(shop_a.id, db)
    conn_a = sqlite3.connect(temp_db_path_a)
    products_a_df = pd.read_sql("SELECT * FROM products", conn_a)
    conn_a.close()
    
    # Assert Shop A sees ONLY Product A
    assert len(products_a_df) == 1
    assert products_a_df.iloc[0]["name"] == "Product A"
    assert products_a_df.iloc[0]["product_code"] == "A1"
    
    # 2. Create DB for User B and inspect contents
    temp_db_path_b = ai_service._create_isolated_ai_db(shop_b.id, db)
    conn_b = sqlite3.connect(temp_db_path_b)
    products_b_df = pd.read_sql("SELECT * FROM products", conn_b)
    conn_b.close()
    
    # Assert Shop B sees ONLY Product B
    assert len(products_b_df) == 1
    assert products_b_df.iloc[0]["name"] == "Product B"
    assert products_b_df.iloc[0]["product_code"] == "B1"
    
    # Assert no cross-contamination
    assert products_a_df.iloc[0]["name"] != "Product B"
    assert products_b_df.iloc[0]["name"] != "Product A"
    
    db.close()
