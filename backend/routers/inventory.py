from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from models.database import get_db
import models.schemas as schemas
import api_schemas
from utils.auth import get_current_user, get_current_shop
import utils.cache as cache

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/products")
def add_product(
    product: api_schemas.ProductCreate, 
    db: Session = Depends(get_db),
    shop: schemas.Shop = Depends(get_current_shop)
):
    try:
        if not shop:
            raise HTTPException(status_code=403, detail="Not authorized to add products to this shop")
            
        import random
        while True:
            code = str(random.randint(1000, 9999))
            existing = db.query(schemas.Product).filter(schemas.Product.product_code == code).first()
            if not existing:
                break
                
        new_product = schemas.Product(
            shop_id=shop.id,
            product_code=code,
            name=product.name,
            category=product.category,
            purchase_price=product.purchase_price,
            selling_price=product.selling_price,
            current_stock=product.current_stock
        )
        
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        # Invalidate relevant caches
        if cache.redis_client:
            try:
                keys_to_delete = cache.redis_client.keys(f"all_products:{shop.id}") + \
                                 cache.redis_client.keys(f"inventory:{shop.id}")
                if keys_to_delete:
                    cache.redis_client.delete(*keys_to_delete)
            except Exception as e:
                print("Failed to invalidate cache:", e)
                
        return {"success": True, "message": "Product added successfully", "product_id": new_product.id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/restock")
def restock_product(
    restock: api_schemas.RestockCreate, 
    db: Session = Depends(get_db),
    shop: schemas.Shop = Depends(get_current_shop)
):
    # Verify the shop belongs to the user and product exists
    product = db.query(schemas.Product).filter(
        schemas.Product.id == restock.product_id, 
        schemas.Product.shop_id == shop.id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or unauthorized")
        
    product.current_stock += restock.quantity
    
    restock_dt = datetime.utcnow()
    if restock.restock_date:
        try:
            restock_dt = datetime.strptime(restock.restock_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format, expected YYYY-MM-DD")

    # Log inventory transaction
    transaction = schemas.InventoryTransaction(
        shop_id=shop.id,
        product_id=restock.product_id,
        change_amount=restock.quantity,
        reason="Restock",
        timestamp=restock_dt
    )
    db.add(transaction)
    db.commit()
    
    # Invalidate relevant caches
    if cache.redis_client:
        try:
            keys_to_delete = cache.redis_client.keys(f"all_products:{shop.id}") + \
                             cache.redis_client.keys(f"inventory:{shop.id}")
            if keys_to_delete:
                cache.redis_client.delete(*keys_to_delete)
        except Exception as e:
            print("Failed to invalidate cache:", e)
            
    return {"success": True, "message": "Product restocked successfully"}

@router.put("/products/{product_id}/status")
def update_product_status(
    product_id: int,
    is_on_the_way: int,
    db: Session = Depends(get_db),
    shop: schemas.Shop = Depends(get_current_shop)
):
    product = db.query(schemas.Product).filter(
        schemas.Product.id == product_id, 
        schemas.Product.shop_id == shop.id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or unauthorized")
        
    product.is_on_the_way = is_on_the_way
    db.commit()
    
    # Invalidate relevant caches
    if cache.redis_client:
        try:
            keys_to_delete = cache.redis_client.keys(f"all_products:{shop.id}") + \
                             cache.redis_client.keys(f"inventory:{shop.id}")
            if keys_to_delete:
                cache.redis_client.delete(*keys_to_delete)
        except Exception as e:
            print("Failed to invalidate cache:", e)
            
    return {"success": True, "message": "Product status updated successfully"}
