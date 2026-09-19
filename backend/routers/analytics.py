from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from models.database import get_db
import services.analytics_service as analytics_service
import api_schemas
import utils.cache as cache
import models.schemas as schemas
from utils.auth import get_current_user, get_current_shop

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/revenue", response_model=api_schemas.RevenueDataResponse)
def get_revenue(
    shop: schemas.Shop = Depends(get_current_shop), 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None,
    interval: str = Query("M", pattern="^(D|W|M)$"),
    db: Session = Depends(get_db)
):
    try:
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=180) # 6 months default
            
        cache_key = f"revenue:{shop.id}:{start_date.isoformat()}:{end_date.isoformat()}:{interval}"
        cached_data = cache.get_cache(cache_key)
        if cached_data:
            return {"data": cached_data}
            
        data = analytics_service.get_revenue_and_profit(db, shop.id, start_date, end_date, interval)
        if not data and data != []:
            raise HTTPException(status_code=404, detail="Shop not found or no data available")
            
        cache.set_cache(cache_key, data, expire_seconds=900)
        return {"data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/all-products", response_model=api_schemas.AllProductsResponse)
def get_all_products(
    shop: schemas.Shop = Depends(get_current_shop), 
    db: Session = Depends(get_db)
):
    try:
        cache_key = f"all_products:{shop.id}"
        cached_data = cache.get_cache(cache_key)
        if cached_data:
            return {"data": cached_data}
            
        data = analytics_service.get_all_products(db, shop.id)
        cache.set_cache(cache_key, data, expire_seconds=3600)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/products", response_model=api_schemas.ProductPerformanceResponse)
def get_products(
    shop: schemas.Shop = Depends(get_current_shop), 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    try:
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=180) # 6 months default
            
        cache_key = f"products:{shop.id}:{start_date.isoformat()}:{end_date.isoformat()}"
        cached_data = cache.get_cache(cache_key)
        if cached_data:
            return {"data": cached_data}
            
        data = analytics_service.get_product_performance(db, shop.id, start_date, end_date)
        cache.set_cache(cache_key, data, expire_seconds=900)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/inventory", response_model=api_schemas.InventoryHealthResponse)
def get_inventory(
    shop: schemas.Shop = Depends(get_current_shop), 
    db: Session = Depends(get_db)
):
    try:
        cache_key = f"inventory:{shop.id}"
        cached_data = cache.get_cache(cache_key)
        if cached_data:
            return {"data": cached_data}
            
        data = analytics_service.get_inventory_health(db, shop.id)
        cache.set_cache(cache_key, data, expire_seconds=900)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
