import sys
import os
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session
# Add backend directory to sys.path to resolve models
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from models.database import SessionLocal, engine
from models import schemas
import models.schemas as models
from utils.auth import get_password_hash

schemas.Base.metadata.create_all(bind=engine)
fake = Faker()

def seed_demo(db: Session = None):
    demo_email = os.getenv("DEMO_USER_EMAIL")
    demo_password = os.getenv("DEMO_USER_PASSWORD")

    if not demo_email or not demo_password:
        print("ERROR: DEMO_USER_EMAIL and DEMO_USER_PASSWORD environment variables must be set.")
        sys.exit(1)

    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    
    # Check for idempotency
    existing_user = db.query(models.User).filter(models.User.email == demo_email).first()
    if existing_user:
        print(f"Demo user {demo_email} already exists. Skipping seed to prevent duplicates.")
        db.close()
        return

    print("Creating Demo User...")
    user = models.User(
        name="Interviewer Evaluator",
        email=demo_email,
        role="owner",
        password_hash=get_password_hash(demo_password),
        is_email_verified=True,  # Bypass OTP
        business_name="ShubhLabh Demo Store",
        business_category="Grocery"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    print("Creating Demo Shop...")
    shop = models.Shop(
        owner_id=user.id,
        name="ShubhLabh Demo Store",
        category="Grocery",
        location="Silicon Valley"
    )
    db.add(shop)
    db.commit()
    db.refresh(shop)

    print("Creating Employees...")
    employees = [
        models.Employee(shop_id=shop.id, name="Rahul Sharma", role="Cashier", salary_amount=15000),
        models.Employee(shop_id=shop.id, name="Anita Desai", role="Store Manager", salary_amount=25000)
    ]
    db.add_all(employees)
    db.commit()

    print("Creating Products...")
    product_templates = [
        ("Rice (Basmati) 5kg", "Produce", 300, 450),
        ("Wheat Flour (Aashirvaad) 10kg", "Produce", 350, 420),
        ("Refined Cooking Oil 1L", "Produce", 110, 150),
        ("Sugar 1kg", "Produce", 40, 55),
        ("Milk (Amul Taza) 1L", "Dairy", 60, 68),
        ("Marie Gold Biscuits Family Pack", "Snacks", 80, 100),
        ("Tata Tea Gold 500g", "Produce", 250, 290),
        ("Nescafe Classic 50g", "Produce", 130, 160),
        ("Whole Wheat Bread", "Bakery", 40, 50),
        ("Maggi Noodles 4-pack", "Snacks", 45, 56)
    ]

    products = []
    for idx, (name, category, p_price, s_price) in enumerate(product_templates):
        prod = models.Product(
            shop_id=shop.id,
            product_code=f"DEMO-{idx+1:03d}",
            name=name,
            category=category,
            purchase_price=float(p_price),
            selling_price=float(s_price),
            current_stock=random.randint(20, 200)
        )
        db.add(prod)
        products.append(prod)
    db.commit()

    print("Generating 6 months of realistic transaction data...")
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=180)
    
    current_date = start_date
    sales = []
    expenses = []
    
    expense_categories = ["Rent", "Electricity", "Water", "Maintenance", "Marketing"]

    while current_date <= end_date:
        is_weekend = current_date.weekday() >= 5
        multiplier = 1.3 if is_weekend else 1.0
            
        # Daily sales
        daily_sales_count = int(random.randint(15, 40) * multiplier)
        for _ in range(daily_sales_count):
            prod = random.choice(products)
            qty = random.randint(1, 4)
            t_price = prod.selling_price * qty
            profit = (prod.selling_price - prod.purchase_price) * qty
            
            sales.append(models.Sale(
                shop_id=shop.id,
                product_id=prod.id,
                quantity=qty,
                total_price=t_price,
                profit=profit,
                timestamp=current_date + timedelta(hours=random.randint(8, 20), minutes=random.randint(0, 59))
            ))

        # Monthly expenses (approx 1st of the month)
        if current_date.day == 1:
            for cat in expense_categories:
                expenses.append(models.Expense(
                    shop_id=shop.id,
                    category=cat,
                    amount=float(random.randint(1000, 5000)),
                    description=f"Monthly {cat}",
                    timestamp=current_date
                ))

        if current_date.day % 10 == 0:
            db.add_all(sales)
            db.commit()
            sales = []
            
        current_date += timedelta(days=1)
        
    if sales:
        db.add_all(sales)
        db.commit()
        
    if expenses:
        db.add_all(expenses)
        db.commit()

    print("Demo data seeded successfully! The demo account is now ready.")
    if close_db:
        db.close()

if __name__ == "__main__":
    seed_demo()
