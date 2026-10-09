import sys
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.schemas import User, Shop, Product, Sale, Expense, Employee, InventoryTransaction

def seed_data(email: str):
    db: Session = SessionLocal()
    
    try:
        # Find the user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Error: Could not find user with email '{email}'")
            return
            
        shop = db.query(Shop).filter(Shop.owner_id == user.id).first()
        if not shop:
            print(f"Error: User '{email}' does not have a shop registered.")
            return
            
        print(f"Seeding data for shop: {shop.name} (Owner: {user.name})")

        # 1. Clean existing dummy data (optional, but good for resetting)
        db.query(Sale).filter(Sale.shop_id == shop.id).delete()
        db.query(InventoryTransaction).filter(InventoryTransaction.shop_id == shop.id).delete()
        db.query(Product).filter(Product.shop_id == shop.id).delete()
        db.query(Expense).filter(Expense.shop_id == shop.id).delete()
        db.query(Employee).filter(Employee.shop_id == shop.id).delete()
        db.commit()

        # 2. Add Products
        product_names = [
            "Organic Milk 1L", "Whole Wheat Bread", "Basmati Rice 5kg", "Olive Oil 1L", 
            "Almonds 500g", "Green Tea Pack", "Laundry Detergent 2kg", "Dish Soap 500ml",
            "Apple Juice 1L", "Potato Chips", "Toothpaste 150g", "Shampoo 400ml",
            "Bath Soap (Pack of 3)", "Eggs (1 Dozen)", "Butter 500g"
        ]
        
        products = []
        for i, name in enumerate(product_names):
            purchase_price = random.uniform(10.0, 500.0)
            selling_price = purchase_price * random.uniform(1.1, 1.5) # 10-50% margin
            
            # Make one product "Dead Stock" (High stock, no sales later)
            current_stock = 200 if i == 0 else random.randint(10, 100)
            
            p = Product(
                shop_id=shop.id,
                product_code=f"PRD-{i+1000}",
                name=name,
                category="Groceries" if i < 10 else "Personal Care",
                purchase_price=round(purchase_price, 2),
                selling_price=round(selling_price, 2),
                current_stock=current_stock
            )
            db.add(p)
            products.append(p)
            
        db.commit()
        for p in products:
            db.refresh(p)
            
        print(f"Added {len(products)} products.")

        # 3. Add Sales over the last 90 days (for the chart and XGBoost ML forecasting)
        sales_added = 0
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        
        # We simulate 90 days of sales
        for day_offset in range(90):
            current_date = start_date + timedelta(days=day_offset)
            
            # 5 to 15 transactions per day
            num_transactions = random.randint(5, 15)
            for _ in range(num_transactions):
                # Pick a random product, BUT skip the first one so it becomes "Dead Stock"
                prod = random.choice(products[1:]) 
                qty = random.randint(1, 5)
                
                total_price = prod.selling_price * qty
                profit = (prod.selling_price - prod.purchase_price) * qty
                
                # Add random hour/minute to the current date
                sale_time = current_date.replace(
                    hour=random.randint(8, 20), 
                    minute=random.randint(0, 59)
                )
                
                s = Sale(
                    shop_id=shop.id,
                    product_id=prod.id,
                    quantity=qty,
                    total_price=round(total_price, 2),
                    profit=round(profit, 2),
                    timestamp=sale_time
                )
                db.add(s)
                sales_added += 1
                
        db.commit()
        print(f"Added {sales_added} historical sales over the last 90 days.")

        # 4. Add Expenses
        expense_categories = ["Rent", "Electricity", "Marketing", "Maintenance", "Software"]
        for _ in range(15):
            exp_date = end_date - timedelta(days=random.randint(0, 90))
            e = Expense(
                shop_id=shop.id,
                category=random.choice(expense_categories),
                amount=round(random.uniform(500, 5000), 2),
                description="Monthly bill",
                timestamp=exp_date
            )
            db.add(e)
        db.commit()
        print("Added 15 expense records.")

        # 5. Add Employees
        emp_names = ["Rahul Sharma", "Priya Singh", "Amit Kumar"]
        roles = ["Cashier", "Manager", "Store Clerk"]
        for i in range(3):
            emp = Employee(
                shop_id=shop.id,
                name=emp_names[i],
                role=roles[i],
                salary_amount=round(random.uniform(15000, 35000), 2),
                join_date=end_date - timedelta(days=random.randint(100, 300))
            )
            db.add(emp)
        db.commit()
        print("Added 3 employees.")

        print("\nSUCCESS! Database seeded perfectly. Your dashboard will now look amazing.")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seed.py <your_registered_email>")
        sys.exit(1)
        
    email_arg = sys.argv[1]
    seed_data(email_arg)
