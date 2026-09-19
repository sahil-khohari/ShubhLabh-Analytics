from pydantic import BaseModel
from typing import List, Optional

class RevenueItem(BaseModel):
    timestamp: str
    total_price: float
    profit: float
    profit_margin_pct: float

class SaleCreate(BaseModel):
    product_id: int
    quantity: int
    sale_date: str
    custom_selling_price: Optional[float] = None

class SaleUpdate(BaseModel):
    quantity: Optional[int] = None
    sale_date: Optional[str] = None
    custom_selling_price: Optional[float] = None

class ProductCreate(BaseModel):
    name: str
    category: str
    purchase_price: float
    selling_price: float
    current_stock: int

class RestockCreate(BaseModel):
    product_id: int
    quantity: int
    restock_date: Optional[str] = None

class EmployeeCreate(BaseModel):
    name: str
    role: str
    salary_amount: float
    join_date: Optional[str] = None

class ExpenseCreate(BaseModel):
    category: str
    amount: float
    description: str
    expense_date: Optional[str] = None

class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None

class RevenueDataResponse(BaseModel):
    data: List[RevenueItem]

class ProductItem(BaseModel):
    product_id: int
    name: str
    total_price: float
    profit: float
    profit_margin: float

class ProductPerformanceData(BaseModel):
    top_profitable: List[ProductItem]
    low_margin: List[ProductItem]

class ProductPerformanceResponse(BaseModel):
    data: ProductPerformanceData

class BasicProductItem(BaseModel):
    id: int
    product_code: Optional[str] = None
    name: str
    category: str
    price: float
    current_stock: int
    is_on_the_way: Optional[int] = 0

class AllProductsResponse(BaseModel):
    data: List[BasicProductItem]

class DeadStockItem(BaseModel):
    id: int
    name: str
    current_stock: int

class InventoryHealthData(BaseModel):
    dead_stock: List[DeadStockItem]
    inventory_turnover_rate: float

class InventoryHealthResponse(BaseModel):
    data: InventoryHealthData

class ForecastItem(BaseModel):
    date: str
    predicted_demand: float

class ForecastResponse(BaseModel):
    forecast: List[ForecastItem]

class AnomalyItem(BaseModel):
    date: str
    quantity: int
    profit: float

class AnomalyResponse(BaseModel):
    shop_id: int
    total_days_analyzed: int
    anomalies_found: int
    anomalies: List[AnomalyItem]

class UserBase(BaseModel):
    email: str
    name: str
    business_name: Optional[str] = None
    business_category: Optional[str] = None
    phone_number: Optional[str] = None
    store_address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    business_name: Optional[str] = None
    business_category: Optional[str] = None
    phone_number: Optional[str] = None
    store_address: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class VerifyEmailRequest(BaseModel):
    email: str
    otp: str

class ResendOTPRequest(BaseModel):
    email: str
