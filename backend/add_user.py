import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.schemas import User, Shop
from utils.auth import get_password_hash

def run():
    db = SessionLocal()
    
    # 1. Check if user exists
    user = db.query(User).filter(User.email == "subhlabh@gmail.com").first()
    if user:
        print("User already exists! Updating password...")
        user.password_hash = get_password_hash("Subhlabh")
    else:
        print("Creating new user...")
        user = User(
            name="ShubhLabh",
            email="subhlabh@gmail.com",
            role="owner",
            password_hash=get_password_hash("Subhlabh")
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    # 2. Re-assign shop 1 to this new user so they can see all the populated data
    shop = db.query(Shop).filter(Shop.id == 1).first()
    if shop:
        shop.owner_id = user.id
        db.commit()
        print(f"Assigned Shop 1 to {user.email}")
    else:
        print("Shop 1 not found.")
        
    print("Database updated successfully.")

if __name__ == "__main__":
    run()
