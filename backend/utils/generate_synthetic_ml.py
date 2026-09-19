import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
import numpy as np
from sqlalchemy.orm import Session
from models.database import SessionLocal, engine
import models.schemas as schemas
from utils.auth import get_password_hash

def generate_data():
    db = SessionLocal()
    
    # 1. Wipe existing data and reset IDs to 1
    print("Wiping existing data and resetting IDs...")
    from sqlalchemy import text
    try:
        db.execute(schemas.InventoryTransaction.__table__.delete())
        db.execute(schemas.Sale.__table__.delete())
        db.execute(schemas.Product.__table__.delete())
        db.execute(schemas.Shop.__table__.delete())
        db.execute(schemas.User.__table__.delete())
        
        # Reset sequences for postgresql
        db.execute(text("TRUNCATE TABLE users, shops, products, sales, inventory_transactions RESTART IDENTITY CASCADE;"))
    except Exception as e:
        print("Truncate fallback:", e)
    db.commit()

    # 2. Create User & Shop
    print("Creating User and Shop...")
    admin_user = schemas.User(
        name="Admin ML",
        email="admin_ml@example.com",
        role="admin",
        password_hash=get_password_hash("password123")
    )
    db.add(admin_user)
    db.commit()
    
    shop = schemas.Shop(
        owner_id=admin_user.id,
        name="ShubhLabh ML Test Shop",
        category="Retail",
        location="New Delhi"
    )
    db.add(shop)
    db.commit()

    # 3. Create Products for Edge Cases
    print("Creating Products...")
    products_data = [
        {"name": "Viral Widget (Spike)", "category": "Electronics", "purchase_price": 50.0, "selling_price": 100.0, "current_stock": 5000},
        {"name": "Stable Sock (OOS)", "category": "Apparel", "purchase_price": 5.0, "selling_price": 15.0, "current_stock": 100},
        {"name": "Fading Gadget (Downtrend)", "category": "Toys", "purchase_price": 20.0, "selling_price": 40.0, "current_stock": 1000},
        {"name": "Promo Item (Anomaly)", "category": "Groceries", "purchase_price": 10.0, "selling_price": 25.0, "current_stock": 5000},
    ]
    
    products = []
    for p_data in products_data:
        p = schemas.Product(shop_id=shop.id, **p_data)
        db.add(p)
        products.append(p)
    db.commit()

    # 4. Generate 12 Months of Daily Sales (365 days)
    print("Generating 12 months of synthetic sales...")
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=365)
    
    sales = []
    
    # Base params
    np.random.seed(42)
    random.seed(42)
    
    for day in range(365):
        current_date = start_date + timedelta(days=day)
        timestamp = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=random.randint(9, 18))
        
        # --- Product 0: Viral Widget (Spike) ---
        # Base demand: 20-30. Spike around day 200 for 3 days (300% increase)
        p0_demand = int(np.random.normal(25, 3))
        if 200 <= day <= 202:
            p0_demand = int(p0_demand * 4.0) # 300% increase
        p0_demand = max(0, p0_demand)
        p0_profit = p0_demand * (products[0].selling_price - products[0].purchase_price)
        sales.append(schemas.Sale(shop_id=shop.id, product_id=products[0].id, quantity=p0_demand, total_price=p0_demand * products[0].selling_price, profit=p0_profit, timestamp=timestamp))
        
        # --- Product 1: Stable Sock (OOS) ---
        # Base demand: 50-60. OOS around day 300 for 5 days.
        p1_demand = int(np.random.normal(55, 5))
        if 300 <= day <= 304:
            p1_demand = 0
        p1_demand = max(0, p1_demand)
        p1_profit = p1_demand * (products[1].selling_price - products[1].purchase_price)
        sales.append(schemas.Sale(shop_id=shop.id, product_id=products[1].id, quantity=p1_demand, total_price=p1_demand * products[1].selling_price, profit=p1_profit, timestamp=timestamp))
        
        # --- Product 2: Fading Gadget (Downtrend) ---
        # Starts at 100, drops slowly over the last 90 days (days 275-365)
        p2_base = 100
        if day > 275:
            p2_base = 100 - ((day - 275) * 0.8) # Drops to ~28
        p2_demand = int(np.random.normal(p2_base, 10))
        p2_demand = max(0, p2_demand)
        p2_profit = p2_demand * (products[2].selling_price - products[2].purchase_price)
        sales.append(schemas.Sale(shop_id=shop.id, product_id=products[2].id, quantity=p2_demand, total_price=p2_demand * products[2].selling_price, profit=p2_profit, timestamp=timestamp))
        
        # --- Product 3: Promo Item (Anomaly) ---
        # Base demand: 80, Margin: 15.
        # Anomalies at day 100 and day 250: Volume spikes to 300, but Profit drops to 0 (Discount gone wrong)
        p3_demand = int(np.random.normal(80, 8))
        p3_profit = p3_demand * (products[3].selling_price - products[3].purchase_price)
        
        if day in [100, 250]:
            p3_demand = 300
            p3_profit = 0 # Anomaly!
            
        p3_demand = max(0, p3_demand)
        sales.append(schemas.Sale(shop_id=shop.id, product_id=products[3].id, quantity=p3_demand, total_price=p3_demand * products[3].selling_price, profit=p3_profit, timestamp=timestamp))
    
    # Bulk insert
    db.bulk_save_objects(sales)
    db.commit()
    print(f"Generated {len(sales)} sales records successfully.")
    
    db.close()

if __name__ == "__main__":
    generate_data()
