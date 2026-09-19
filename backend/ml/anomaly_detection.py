import pandas as pd
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session
import models.schemas as schemas

def detect_anomalies(db: Session, shop_id: int):
    """
    Uses Isolation Forest to detect anomalous sales days based on volume and profit.
    """
    from sqlalchemy import func
    
    # Fetch historical sales for the shop, aggregated by day in DB to save memory
    query = db.query(
        func.date_trunc('day', schemas.Sale.timestamp).label('timestamp'),
        func.sum(schemas.Sale.quantity).label('quantity'),
        func.sum(schemas.Sale.profit).label('profit')
    ).filter(
        schemas.Sale.shop_id == shop_id
    ).group_by(
        func.date_trunc('day', schemas.Sale.timestamp)
    )
    
    df = pd.read_sql(query.statement, db.bind)
    if df.empty:
        return {"error": "No historical data available for this shop."}

    # Prepare continuous time-series data
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    # Resample daily to fill any missing days with 0
    daily_stats = df.resample('D').sum().fillna(0)
    
    if len(daily_stats) < 14:
        return {"error": "Not enough historical data to detect anomalies. Minimum 14 days required."}

    # Prepare training data
    from sklearn.preprocessing import StandardScaler
    X = daily_stats[['quantity', 'profit']]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Isolation Forest
    # Using 5% contamination to catch our injected drops + any natural outliers
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X_scaled)
    
    # Predict anomalies (-1 for anomaly, 1 for normal)
    daily_stats['anomaly'] = model.predict(X_scaled)
    
    # Filter only anomalies
    anomalies_df = daily_stats[daily_stats['anomaly'] == -1].copy()
    
    # Format output
    anomalies_df.reset_index(inplace=True)
    anomalies_df.rename(columns={'timestamp': 'date'}, inplace=True)
    anomalies_df['date'] = anomalies_df['date'].dt.strftime('%Y-%m-%d')
    
    result = anomalies_df[['date', 'quantity', 'profit']].to_dict(orient='records')
    
    return {
        "shop_id": shop_id,
        "total_days_analyzed": len(daily_stats),
        "anomalies_found": len(result),
        "anomalies": result
    }
