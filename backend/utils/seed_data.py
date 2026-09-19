import sys
import os
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from faker import Faker

# Add backend directory to sys.path to resolve models
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from models.database import SessionLocal, engine
from models import schemas
import models.schemas as models

schemas.Base.metadata.create_all(bind=engine)

fake = Faker()

def seed_data():
    db = SessionLocal()
    
    # Check if we already seeded
    if db.query(models.User).first():
        print("Database already seeded!")
        return

    print("Generating users...")
    users = []
    for _ in range(5):
        user = models.User(
            name=fake.name(),
            email=fake.email(),
            role="owner",
            password_hash="fakehash123"
        )
        db.add(user)
        users.append(user)
    db.commit()

    print("Generating shops...")
    grocery_shop = models.Shop(
        owner_id=users[0].id,
        name="Fresh Mart",
        category="Grocery",
        location="Downtown"
    )
    clothing_shop = models.Shop(
        owner_id=users[1].id,
        name="Trendy Threads",
        category="Clothing",
        location="Uptown Mall"
    )
    db.add_all([grocery_shop, clothing_shop])
    db.commit()

    print("Generating products...")
    grocery_products = []
    for _ in range(25):
        p_price = random.uniform(1.0, 15.0)
        prod = models.Product(
            shop_id=grocery_shop.id,
            name=fake.word().capitalize() + " " + fake.word().capitalize(),
            category=random.choice(["Produce", "Dairy", "Bakery", "Snacks"]),
            purchase_price=round(p_price, 2),
            selling_price=round(p_price * random.uniform(1.2, 1.8), 2),
            current_stock=random.randint(50, 500)
        )
        db.add(prod)
        grocery_products.append(prod)

    clothing_products = []
    for _ in range(20):
        p_price = random.uniform(10.0, 50.0)
        prod = models.Product(
            shop_id=clothing_shop.id,
            name=fake.word().capitalize() + " " + random.choice(["Shirt", "Pants", "Dress", "Jacket"]),
            category=random.choice(["Men", "Women", "Kids", "Accessories"]),
            purchase_price=round(p_price, 2),
            selling_price=round(p_price * random.uniform(1.5, 3.0), 2),
            current_stock=random.randint(10, 100)
        )
        db.add(prod)
        clothing_products.append(prod)
    
    db.commit()

    print("Generating 6 months of historical transaction data...")
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=180)
    
    current_date = start_date
    sales = []
    transactions = []

    while current_date <= end_date:
        is_weekend = current_date.weekday() >= 5
        # Seasonal spike: Higher sales in last 30 days
        is_holiday_season = (end_date - current_date).days < 30
        
        # Base multiplier
        multiplier = 1.0
        if is_weekend:
            multiplier *= 1.5
        if is_holiday_season:
            multiplier *= 1.4
            
        # Grocery Shop daily sales
        grocery_sales_count = int(random.randint(20, 60) * multiplier)
        for _ in range(grocery_sales_count):
            prod = random.choice(grocery_products)
            qty = random.randint(1, 5)
            t_price = prod.selling_price * qty
            profit = (prod.selling_price - prod.purchase_price) * qty
            
            sales.append(models.Sale(
                shop_id=grocery_shop.id,
                product_id=prod.id,
                quantity=qty,
                total_price=t_price,
                profit=profit,
                timestamp=current_date + timedelta(hours=random.randint(8, 20), minutes=random.randint(0, 59))
            ))

        # Clothing Shop daily sales
        clothing_sales_count = int(random.randint(5, 25) * multiplier)
        for _ in range(clothing_sales_count):
            prod = random.choice(clothing_products)
            qty = random.randint(1, 2)
            t_price = prod.selling_price * qty
            profit = (prod.selling_price - prod.purchase_price) * qty
            
            sales.append(models.Sale(
                shop_id=clothing_shop.id,
                product_id=prod.id,
                quantity=qty,
                total_price=t_price,
                profit=profit,
                timestamp=current_date + timedelta(hours=random.randint(10, 21), minutes=random.randint(0, 59))
            ))
            
        # Commit in batches of 10 days to avoid massive memory usage
        if current_date.day % 10 == 0:
            db.add_all(sales)
            db.commit()
            sales = []
            
        current_date += timedelta(days=1)
        
    if sales:
        db.add_all(sales)
        db.commit()
        
    print("Database seeded successfully with 6 months of dummy data!")

if __name__ == "__main__":
    seed_data()
