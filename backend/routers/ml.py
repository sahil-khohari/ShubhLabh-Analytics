from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.database import get_db
import ml.forecasting as forecasting
import ml.anomaly_detection as anomaly_detection
import api_schemas
from utils.auth import get_current_user, get_current_shop
import models.schemas as schemas
import utils.cache as cache

router = APIRouter(
    prefix="/ml",
    tags=["machine learning"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/forecast", response_model=api_schemas.ForecastResponse)
def get_forecast(product_id: int, days: int = 7, shop: schemas.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    """
    Returns a future demand forecast for a specific product using XGBoost.
    """
    try:
        cache_key = f"ml_forecast_{shop.id}_{product_id}_{days}"
        cached_data = cache.get_cache(cache_key)
        if cached_data:
            return cached_data

        data = forecasting.predict_demand(db, shop.id, product_id, days)
        if not data or "error" in data:
            detail = data.get("error") if isinstance(data, dict) and "error" in data else "Product not found or not enough data to forecast"
            raise HTTPException(status_code=404, detail=detail)
            
        cache.set_cache(cache_key, data, expire_seconds=900)
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML Forecasting Error: {str(e)}")

@router.get("/anomalies", response_model=api_schemas.AnomalyResponse)
def get_anomalies(shop: schemas.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    """
    Returns dates with anomalous sales or profit activity using Isolation Forest.
    """
    try:
        cache_key = f"ml_anomalies_{shop.id}"
        cached_data = cache.get_cache(cache_key)
        if cached_data:
            return cached_data

        data = anomaly_detection.detect_anomalies(db, shop.id)
        
        # If there is an error (e.g., not enough historical data), return empty response
        if not data or "error" in data:
            empty_response = {
                "shop_id": shop.id,
                "total_days_analyzed": 0,
                "anomalies_found": 0,
                "anomalies": []
            }
            cache.set_cache(cache_key, empty_response, expire_seconds=900)
            return empty_response

        cache.set_cache(cache_key, data, expire_seconds=900)
            
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML Anomaly Detection Error: {str(e)}")
