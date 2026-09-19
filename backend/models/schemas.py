from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String)
    password_hash = Column(String)
    is_email_verified = Column(Boolean, default=False)
    
    business_name = Column(String)
    business_category = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    store_address = Column(String, nullable=True)

    shops = relationship("Shop", back_populates="owner", cascade="all, delete-orphan")

class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String, index=True)
    category = Column(String)
    location = Column(String)

    owner = relationship("User", back_populates="shops")
    products = relationship("Product", back_populates="shop", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="shop", cascade="all, delete-orphan")
    transactions = relationship("InventoryTransaction", back_populates="shop", cascade="all, delete-orphan")
    employees = relationship("Employee", back_populates="shop", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="shop", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), index=True)
    product_code = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    purchase_price = Column(Float)
    selling_price = Column(Float)
    current_stock = Column(Integer, default=0)
    is_on_the_way = Column(Boolean, default=False)

    shop = relationship("Shop", back_populates="products")
    sales = relationship("Sale", back_populates="product", cascade="all, delete-orphan")
    transactions = relationship("InventoryTransaction", back_populates="product", cascade="all, delete-orphan")

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    quantity = Column(Integer)
    total_price = Column(Float)
    profit = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    shop = relationship("Shop", back_populates="sales")
    product = relationship("Product", back_populates="sales")

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    change_amount = Column(Integer)
    reason = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    shop = relationship("Shop", back_populates="transactions")
    product = relationship("Product", back_populates="transactions")

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), index=True)
    name = Column(String, index=True)
    role = Column(String)
    salary_amount = Column(Float)
    join_date = Column(DateTime, default=datetime.utcnow)

    shop = relationship("Shop", back_populates="employees")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), index=True)
    category = Column(String, index=True)
    amount = Column(Float)
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    shop = relationship("Shop", back_populates="expenses")
