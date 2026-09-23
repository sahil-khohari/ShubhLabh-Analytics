import os
import pandas as pd
import numpy as np
import xgboost as xgb
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import models.schemas as schemas

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "forecasting")
os.makedirs(MODELS_DIR, exist_ok=True)

def _get_model_path(shop_id: int, product_id: int) -> str:
    return os.path.join(MODELS_DIR, f"shop_{shop_id}_product_{product_id}.json")

def _create_features(df_in):
    df_feat = df_in.copy()
    df_feat['day_of_week'] = df_feat.index.dayofweek
    df_feat['month'] = df_feat.index.month
    df_feat['is_weekend'] = df_feat['day_of_week'].isin([5, 6]).astype(int)
    df_feat['rolling_7_day_avg'] = df_feat['quantity'].rolling(window=7, min_periods=1).mean()
    df_feat['lag_1_day'] = df_feat['quantity'].shift(1).bfill()
    df_feat['lag_7_day'] = df_feat['quantity'].shift(7).bfill()
    return df_feat

def train_forecasting_model(db: Session, shop_id: int, product_id: int):
    """
    Trains an XGBoost model on historical sales data and persists it.
    """
    query = db.query(schemas.Sale.timestamp, schemas.Sale.quantity).filter(
        schemas.Sale.shop_id == shop_id,
        schemas.Sale.product_id == product_id
    )
    
    df = pd.read_sql(query.statement, db.bind)
    if df.empty:
        return {"error": "No historical data available for this product."}

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    daily_sales = df.resample('D').sum().fillna(0)
    
    if len(daily_sales) < 14:
        return {"error": "Not enough historical data to train the model. Minimum 14 days required."}

    daily_sales_feat = _create_features(daily_sales)
    
    features = ['day_of_week', 'month', 'is_weekend', 'rolling_7_day_avg', 'lag_1_day', 'lag_7_day']
    X = daily_sales_feat[features]
    y = daily_sales_feat['quantity']
    
    model = xgb.XGBRegressor(
        objective='reg:squarederror', 
        max_depth=4, 
        learning_rate=0.1, 
        n_estimators=100,
        random_state=42
    )
    model.fit(X, y)
    
    model_path = _get_model_path(shop_id, product_id)
    model.save_model(model_path)
    
    return {
        "message": "Model trained successfully.",
        "shop_id": shop_id,
        "product_id": product_id,
        "training_timestamp": datetime.utcnow().isoformat()
    }

def predict_demand(db: Session, shop_id: int, product_id: int, days_ahead: int = 7):
    """
    Loads a pre-trained XGBoost model and predicts future demand.
    """
    model_path = _get_model_path(shop_id, product_id)
    if not os.path.exists(model_path):
        return {"error": "Forecast model is not trained yet. Please train/retrain the model first."}
        
    model = xgb.XGBRegressor()
    model.load_model(model_path)

    # Fetch last 30 days of data to safely compute lags and rolling avg
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    query = db.query(schemas.Sale.timestamp, schemas.Sale.quantity).filter(
        schemas.Sale.shop_id == shop_id,
        schemas.Sale.product_id == product_id,
        schemas.Sale.timestamp >= thirty_days_ago
    )
    
    df = pd.read_sql(query.statement, db.bind)
    if df.empty:
        return {"error": "No recent historical data available to seed predictions."}

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    daily_sales = df.resample('D').sum().fillna(0)
    
    if len(daily_sales) < 7:
        # We need at least 7 days to seed the lags
        return {"error": "Not enough recent data (minimum 7 days) to generate a forecast."}

    daily_sales_feat = _create_features(daily_sales)
    
    features = ['day_of_week', 'month', 'is_weekend', 'rolling_7_day_avg', 'lag_1_day', 'lag_7_day']
    
    last_date = daily_sales_feat.index[-1]
    future_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
    
    future_df = pd.DataFrame(index=future_dates)
    
    predictions = []
    current_history = daily_sales_feat['quantity'].copy()
    
    for i, date in enumerate(future_dates):
        row = {}
        row['day_of_week'] = date.weekday()
        row['month'] = date.month
        row['is_weekend'] = 1 if row['day_of_week'] in [5, 6] else 0
        
        row['rolling_7_day_avg'] = current_history.iloc[-7:].mean()
        row['lag_1_day'] = current_history.iloc[-1]
        row['lag_7_day'] = current_history.iloc[-7]
        
        X_pred = pd.DataFrame([row])[features]
        pred_val = max(0, round(float(model.predict(X_pred)[0])))
        predictions.append(pred_val)
        
        current_history.loc[date] = pred_val
        
    future_df['predicted_demand'] = predictions
    
    future_df.reset_index(inplace=True)
    future_df.rename(columns={'index': 'date'}, inplace=True)
    future_df['date'] = future_df['date'].dt.strftime('%Y-%m-%d')
    
    result = future_df[['date', 'predicted_demand']].to_dict(orient='records')
    
    return {
        "product_id": product_id,
        "shop_id": shop_id,
        "forecast": result
    }
