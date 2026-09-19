from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from models.database import get_db
import models.schemas as schemas
from api_schemas import SaleCreate, SaleUpdate
from utils.auth import get_current_user, get_current_shop
import utils.cache as cache

router = APIRouter(
    prefix="/sales",
    tags=["sales"],
    dependencies=[Depends(get_current_user)]
)

@router.post("")
def add_sale(sale: SaleCreate, shop: schemas.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    # Verify product
    product = db.query(schemas.Product).filter(
        schemas.Product.id == sale.product_id,
        schemas.Product.shop_id == shop.id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found or doesn't belong to this shop")
    
    # Check inventory
    if product.current_stock < sale.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Calculate totals
    selling_price = sale.custom_selling_price if sale.custom_selling_price is not None else product.selling_price
    total_price = selling_price * sale.quantity
    profit = (selling_price - product.purchase_price) * sale.quantity
    
    # Parse date
    try:
        sale_date = datetime.strptime(sale.sale_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, expected YYYY-MM-DD")
        
    # Insert new sale
    new_sale = schemas.Sale(
        shop_id=shop.id,
        product_id=sale.product_id,
        quantity=sale.quantity,
        total_price=total_price,
        profit=profit,
        timestamp=sale_date
    )
    
    db.add(new_sale)
    
    # Deduct inventory
    product.current_stock -= sale.quantity
    
    # Log inventory transaction
    transaction = schemas.InventoryTransaction(
        shop_id=shop.id,
        product_id=sale.product_id,
        change_amount=-sale.quantity,
        reason="Sale"
    )
    db.add(transaction)
    
    db.commit()
    db.refresh(new_sale)
    
    # Invalidate Cache
    if cache.redis_client:
        try:
            # Clear all analytics caches for this shop
            keys_to_delete = cache.redis_client.keys(f"revenue:{shop.id}:*") + \
                             cache.redis_client.keys(f"products:{shop.id}:*") + \
                             cache.redis_client.keys(f"all_products:{shop.id}") + \
                             cache.redis_client.keys(f"inventory:{shop.id}") + \
                             cache.redis_client.keys(f"ml_forecast_{shop.id}_*") + \
                             cache.redis_client.keys(f"ml_anomalies_{shop.id}_*")
            if keys_to_delete:
                cache.redis_client.delete(*keys_to_delete)
        except Exception as e:
            print("Failed to invalidate cache:", e)

    return {"status": "success", "message": "Sale added successfully", "sale_id": new_sale.id}

@router.get("")
def get_sales(filter: str = 'today', shop: schemas.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    # Calculate start date based on filter
    now = datetime.utcnow()
    if filter == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif filter == 'weekly':
        start_date = now - timedelta(days=7)
    elif filter == 'monthly':
        start_date = now - timedelta(days=30)
    else:
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0) # Default to today

    # Query sales with joined product to get product name
    sales = db.query(schemas.Sale).filter(
        schemas.Sale.shop_id == shop.id,
        schemas.Sale.timestamp >= start_date
    ).order_by(schemas.Sale.timestamp.desc()).all()

    # Format response
    response_data = []
    for sale in sales:
        response_data.append({
            "id": sale.id,
            "product_id": sale.product_id,
            "product_name": f"[{sale.product.product_code}] {sale.product.name}" if sale.product.product_code else sale.product.name,
            "quantity": sale.quantity,
            "total_price": sale.total_price,
            "profit": sale.profit,
            "selling_price": sale.total_price / sale.quantity if sale.quantity > 0 else 0,
            "sale_date": sale.timestamp.strftime("%Y-%m-%d")
        })

    return {"status": "success", "data": response_data}

@router.put("/{sale_id}")
def update_sale(sale_id: int, sale_update: SaleUpdate, shop: schemas.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    sale = db.query(schemas.Sale).filter(
        schemas.Sale.id == sale_id,
        schemas.Sale.shop_id == shop.id
    ).first()

    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found or unauthorized")

    product = sale.product
    
    # Handle inventory and quantity updates
    if sale_update.quantity is not None and sale_update.quantity != sale.quantity:
        quantity_diff = sale_update.quantity - sale.quantity
        
        # Check inventory if increasing quantity
        if quantity_diff > 0 and product.current_stock < quantity_diff:
            raise HTTPException(status_code=400, detail="Insufficient stock to update sale")
            
        product.current_stock -= quantity_diff
        sale.quantity = sale_update.quantity
        
        # Log inventory transaction
        transaction = schemas.InventoryTransaction(
            shop_id=shop.id,
            product_id=product.id,
            change_amount=-quantity_diff,
            reason="Sale Edit"
        )
        db.add(transaction)

    # Handle price updates
    current_selling_price = sale.total_price / sale.quantity if sale.quantity > 0 else product.selling_price
    selling_price = sale_update.custom_selling_price if sale_update.custom_selling_price is not None else current_selling_price
    
    sale.total_price = selling_price * sale.quantity
    sale.profit = (selling_price - product.purchase_price) * sale.quantity

    # Handle date updates
    if sale_update.sale_date:
        try:
            sale.timestamp = datetime.strptime(sale_update.sale_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format, expected YYYY-MM-DD")

    db.commit()

    # Invalidate Cache
    if cache.redis_client:
        try:
            keys_to_delete = cache.redis_client.keys(f"revenue:{shop.id}:*") + \
                             cache.redis_client.keys(f"products:{shop.id}:*") + \
                             cache.redis_client.keys(f"all_products:{shop.id}") + \
                             cache.redis_client.keys(f"inventory:{shop.id}") + \
                             cache.redis_client.keys(f"ml_forecast_{shop.id}_*") + \
                             cache.redis_client.keys(f"ml_anomalies_{shop.id}_*")
            if keys_to_delete:
                cache.redis_client.delete(*keys_to_delete)
        except Exception as e:
            print("Failed to invalidate cache:", e)

    return {"status": "success", "message": "Sale updated successfully"}


@router.delete("/{sale_id}")
def delete_sale(sale_id: int, shop: schemas.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    sale = db.query(schemas.Sale).filter(
        schemas.Sale.id == sale_id,
        schemas.Sale.shop_id == shop.id
    ).first()

    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found or unauthorized")

    # Add back to inventory
    product = sale.product
    product.current_stock += sale.quantity
    
    # Log inventory transaction
    transaction = schemas.InventoryTransaction(
        shop_id=shop.id,
        product_id=product.id,
        change_amount=sale.quantity,
        reason="Sale Delete Refund"
    )
    db.add(transaction)

    db.delete(sale)
    db.commit()

    # Invalidate Cache
    if cache.redis_client:
        try:
            keys_to_delete = cache.redis_client.keys(f"revenue:{shop.id}:*") + \
                             cache.redis_client.keys(f"products:{shop.id}:*") + \
                             cache.redis_client.keys(f"all_products:{shop.id}") + \
                             cache.redis_client.keys(f"inventory:{shop.id}") + \
                             cache.redis_client.keys(f"ml_forecast_{shop.id}_*") + \
                             cache.redis_client.keys(f"ml_anomalies_{shop.id}_*")
            if keys_to_delete:
                cache.redis_client.delete(*keys_to_delete)
        except Exception as e:
            print("Failed to invalidate cache:", e)

    return {"status": "success", "message": "Sale deleted successfully"}
