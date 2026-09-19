import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"
ARTIFACT_PATH = "/Users/sahil_khohari/.gemini/antigravity-ide/brain/1931f5dc-20bb-4b64-a0b5-e74b9a40d0a5/ml_verification.md"

def test_ml_endpoints():
    print("Testing /ml/forecast (shop=1, product=2)...")
    try:
        forecast_resp = requests.get(f"{BASE_URL}/ml/forecast", params={"shop_id": 1, "product_id": 2, "days": 7})
        forecast_resp.raise_for_status()
        forecast_data = forecast_resp.json()
    except Exception as e:
        forecast_data = {"error": str(e), "details": forecast_resp.text if 'forecast_resp' in locals() else ""}

    print("Testing /ml/anomalies (shop=1)...")
    try:
        anomalies_resp = requests.get(f"{BASE_URL}/ml/anomalies", params={"shop_id": 1})
        anomalies_resp.raise_for_status()
        anomalies_data = anomalies_resp.json()
    except Exception as e:
        anomalies_data = {"error": str(e), "details": anomalies_resp.text if 'anomalies_resp' in locals() else ""}
    
    print("Writing to artifact...")
    with open(ARTIFACT_PATH, "w") as f:
        f.write("# ML Response Verification\n\n")
        
        f.write("## Demand Forecast (Product 2, Grocery Shop)\n")
        f.write("```json\n")
        f.write(json.dumps(forecast_data, indent=2))
        f.write("\n```\n\n")
        
        f.write("## Anomaly Detection (Grocery Shop)\n")
        f.write("```json\n")
        f.write(json.dumps(anomalies_data, indent=2))
        f.write("\n```\n")
        
    print("Done!")

if __name__ == "__main__":
    test_ml_endpoints()
