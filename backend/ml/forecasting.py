import pandas as pd
import numpy as np
import xgboost as xgb
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import models.schemas as schemas

def predict_demand(db: Session, shop_id: int, product_id: int, days_ahead: int = 7):
    """
    Trains an XGBoost model on historical sales data to predict future demand.
    """
    # Fetch historical data
    query = db.query(schemas.Sale.timestamp, schemas.Sale.quantity).filter(
        schemas.Sale.shop_id == shop_id,
        schemas.Sale.product_id == product_id
    )
    
    df = pd.read_sql(query.statement, db.bind)
    if df.empty:
        return {"error": "No historical data available for this product."}

    # Prepare time-series data
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    # Resample daily (summing up quantities if multiple sales per day)
    daily_sales = df.resample('D').sum().fillna(0)
    
    if len(daily_sales) < 14:
        return {"error": "Not enough historical data to train the model. Minimum 14 days required."}

    # Feature Engineering
    def create_features(df_in):
        df_feat = df_in.copy()
        df_feat['day_of_week'] = df_feat.index.dayofweek
        df_feat['month'] = df_feat.index.month
        df_feat['is_weekend'] = df_feat['day_of_week'].isin([5, 6]).astype(int)
        df_feat['rolling_7_day_avg'] = df_feat['quantity'].rolling(window=7, min_periods=1).mean()
        df_feat['lag_1_day'] = df_feat['quantity'].shift(1).bfill()
        df_feat['lag_7_day'] = df_feat['quantity'].shift(7).bfill()
        return df_feat

    daily_sales_feat = create_features(daily_sales)
    
    # Prepare training data
    features = ['day_of_week', 'month', 'is_weekend', 'rolling_7_day_avg', 'lag_1_day', 'lag_7_day']
    X = daily_sales_feat[features]
    y = daily_sales_feat['quantity']
    
    # Train XGBoost Model (Baseline configuration, avoiding slow GridSearch per-request)
    model = xgb.XGBRegressor(
        objective='reg:squarederror', 
        max_depth=4, 
        learning_rate=0.1, 
        n_estimators=100,
        random_state=42
    )
    model.fit(X, y)
    
    # Generate future dates for prediction
    last_date = daily_sales_feat.index[-1]
    future_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
    
    # Create future dataframe
    future_df = pd.DataFrame(index=future_dates)
    
    # Iterative prediction for auto-regressive lag features
    predictions = []
    current_history = daily_sales_feat['quantity'].copy()
    
    for i, date in enumerate(future_dates):
        row = {}
        row['day_of_week'] = date.weekday()
        row['month'] = date.month
        row['is_weekend'] = 1 if row['day_of_week'] in [5, 6] else 0
        
        # Calculate dynamic rolling avg and lags
        row['rolling_7_day_avg'] = current_history.iloc[-7:].mean()
        row['lag_1_day'] = current_history.iloc[-1]
        row['lag_7_day'] = current_history.iloc[-7]
        
        X_pred = pd.DataFrame([row])[features]
        pred_val = max(0, round(float(model.predict(X_pred)[0])))
        predictions.append(pred_val)
        
        # Append prediction to history to use in next step
        current_history.loc[date] = pred_val
        
    future_df['predicted_demand'] = predictions
    
    # Format output
    future_df.reset_index(inplace=True)
    future_df.rename(columns={'index': 'date'}, inplace=True)
    future_df['date'] = future_df['date'].dt.strftime('%Y-%m-%d')
    
    result = future_df[['date', 'predicted_demand']].to_dict(orient='records')
    
    return {
        "product_id": product_id,
        "shop_id": shop_id,
        "forecast": result
    }
