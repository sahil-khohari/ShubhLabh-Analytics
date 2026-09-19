import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
import models.schemas as schemas

def get_revenue_and_profit(db: Session, shop_id: int, start_date: datetime, end_date: datetime, interval: str = 'M'):
    """
    Calculates daily, weekly, or monthly revenue and profit margins directly via SQL.
    interval: 'D', 'W', or 'M'
    """
    from sqlalchemy import func
    
    interval_map = {'D': 'day', 'W': 'week', 'M': 'month'}
    trunc_val = interval_map.get(interval, 'month')
    
    query = db.query(
        func.date_trunc(trunc_val, schemas.Sale.timestamp).label('timestamp'),
        func.sum(schemas.Sale.total_price).label('total_price'),
        func.sum(schemas.Sale.profit).label('profit')
    ).filter(
        schemas.Sale.shop_id == shop_id,
        schemas.Sale.timestamp >= start_date,
        schemas.Sale.timestamp <= end_date
    ).group_by(
        func.date_trunc(trunc_val, schemas.Sale.timestamp)
    ).order_by(
        func.date_trunc(trunc_val, schemas.Sale.timestamp)
    )
    
    df = pd.read_sql(query.statement, db.bind)
    
    if df.empty:
        return []

    # Calculate profit margin percentage
    df['profit_margin_pct'] = (df['profit'] / df['total_price'] * 100).fillna(0).round(2)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d')
    df = df.fillna(0)
    
    return df.to_dict(orient='records')

def get_product_performance(db: Session, shop_id: int, start_date: datetime, end_date: datetime):
    """
    Returns top 10 most profitable and top 10 low-margin products via SQL aggregations.
    """
    from sqlalchemy import func
    
    query = db.query(
        schemas.Sale.product_id, 
        schemas.Product.name, 
        func.sum(schemas.Sale.total_price).label('total_price'), 
        func.sum(schemas.Sale.profit).label('profit')
    ).join(
        schemas.Product, schemas.Sale.product_id == schemas.Product.id
    ).filter(
        schemas.Sale.shop_id == shop_id,
        schemas.Sale.timestamp >= start_date,
        schemas.Sale.timestamp <= end_date
    ).group_by(
        schemas.Sale.product_id,
        schemas.Product.name
    )
    
    df = pd.read_sql(query.statement, db.bind)
    
    if df.empty:
        return {"top_profitable": [], "low_margin": []}

    # Profit margin
    df['profit_margin'] = (df['profit'] / df['total_price'] * 100).fillna(0).round(2)
    
    top_profitable = df.sort_values(by='profit', ascending=False).head(10)
    low_margin = df.sort_values(by='profit_margin', ascending=True).head(10)
    
    return {
        "top_profitable": top_profitable.to_dict(orient='records'),
        "low_margin": low_margin.to_dict(orient='records')
    }

def get_all_products(db: Session, shop_id: int):
    """
    Returns a basic list of all products for the shop.
    """
    query = db.query(
        schemas.Product.id,
        schemas.Product.product_code,
        schemas.Product.name,
        schemas.Product.category,
        schemas.Product.selling_price.label('price'),
        schemas.Product.current_stock,
        schemas.Product.is_on_the_way
    ).filter(
        schemas.Product.shop_id == shop_id
    )
    
    df = pd.read_sql(query.statement, db.bind)
    if df.empty:
        return []
        
    import numpy as np
    df = df.astype(object).replace({np.nan: None})
    return df.to_dict(orient='records')

def get_inventory_health(db: Session, shop_id: int):
    """
    Calculates inventory turnover rate and identifies dead stock (no sales in last 30 days).
    """
    # Identify dead stock
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Get all products for the shop with current_stock > 0
    products_query = db.query(schemas.Product).filter(
        schemas.Product.shop_id == shop_id,
        schemas.Product.current_stock > 0
    )
    products_df = pd.read_sql(products_query.statement, db.bind)
    
    # Get sales in the last 30 days for these products
    sales_query = db.query(schemas.Sale.product_id, schemas.Sale.quantity).filter(
        schemas.Sale.shop_id == shop_id,
        schemas.Sale.timestamp >= thirty_days_ago
    )
    sales_df = pd.read_sql(sales_query.statement, db.bind)
    
    if products_df.empty:
        return {"dead_stock": [], "inventory_turnover_rate": 0}

    if sales_df.empty:
        dead_stock = products_df[['id', 'name', 'current_stock']].to_dict(orient='records')
        return {"dead_stock": dead_stock, "inventory_turnover_rate": 0}

    # Total quantity sold in last 30 days
    sales_agg = sales_df.groupby('product_id')['quantity'].sum().reset_index()
    
    # Merge with products
    merged = pd.merge(products_df, sales_agg, left_on='id', right_on='product_id', how='left')
    merged['quantity'] = merged['quantity'].fillna(0)
    
    # Dead stock: items with stock > 0 but 0 quantity sold in last 30 days
    dead_stock_df = merged[(merged['quantity'] == 0) & (merged['current_stock'] > 0)]
    dead_stock = dead_stock_df[['id', 'name', 'current_stock']].to_dict(orient='records')
    
    # Simplified Inventory Turnover Rate = (COGS) / (Average Inventory Value)
    # COGS = total purchase_price * quantity sold
    # Value = total purchase_price * current_stock
    # We'll use a simple turnover calculation: units sold / average units in stock
    # For a realistic metric, let's use: Total Units Sold / Total Current Stock (as proxy for average stock)
    total_units_sold = merged['quantity'].sum()
    total_current_stock = merged['current_stock'].sum()
    
    if total_current_stock > 0:
        turnover_rate = round(total_units_sold / total_current_stock, 2)
    else:
        turnover_rate = 0
        
    return {
        "dead_stock": dead_stock,
        "inventory_turnover_rate": float(turnover_rate)
    }
