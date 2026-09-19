import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import SessionLocal
from ml.forecasting import predict_demand
from ml.anomaly_detection import detect_anomalies
import json

db = SessionLocal()

import models.schemas as schemas

# Fetch dynamically
shop = db.query(schemas.Shop).first()
if not shop:
    print("No shop found!")
    exit(1)

shop_id = shop.id
products = db.query(schemas.Product).filter(schemas.Product.shop_id == shop_id).all()
pids = [p.id for p in products]

print("--- Testing Forecasting (XGBoost tuning) ---")
try:
    for pid in pids:
        print(f"\\nProduct {pid}:")
        forecast = predict_demand(db, shop_id=shop_id, product_id=pid, days_ahead=7)
        if "error" in forecast:
            print("Error:", forecast["error"])
        else:
            total_demand = sum(day["predicted_demand"] for day in forecast["forecast"])
            print(f"Total Predicted Demand (7 days): {total_demand}")
            for day in forecast["forecast"]:
                print(f"  {day['date']}: {day['predicted_demand']}")
except Exception as e:
    print(f"Forecasting error: {e}")

print("\\n--- Testing Anomaly Detection ---")
try:
    anomalies = detect_anomalies(db, shop_id=shop_id)
    if "error" in anomalies:
        print("Error:", anomalies["error"])
    else:
        print(f"Total anomalies found: {anomalies['anomalies_found']}")
        for anomaly in anomalies["anomalies"]:
            print(f"  {anomaly['date']}: Qty {anomaly['quantity']}, Profit {anomaly['profit']}")
except Exception as e:
    print(f"Anomaly Detection error: {e}")

db.close()
