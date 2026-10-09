import os
import sys
from models.database import SessionLocal
from models.schemas import Shop, Product, Sale
from ml.forecasting import train_forecasting_model, predict_demand
from datetime import datetime, timedelta

db = SessionLocal()

shop = db.query(Shop).first()
if not shop:
    print("No shop found to test with.")
    sys.exit(1)

product = db.query(Product).filter(Product.shop_id == shop.id).first()
if not product:
    print("No product found to test with.")
    sys.exit(1)

sales = db.query(Sale).filter(Sale.product_id == product.id).count()
if sales < 14:
    print(f"Adding synthetic sales data for product {product.id} (shop {shop.id})")
    for i in range(20):
        sale = Sale(
            shop_id=shop.id,
            product_id=product.id,
            quantity=5 + i%3,
            total_price=100.0,
            profit=20.0,
            timestamp=datetime.utcnow() - timedelta(days=20-i)
        )
        db.add(sale)
    db.commit()

# Ensure model doesn't exist to test failure first
model_path = os.path.join(os.path.dirname(__file__), "models", "forecasting", f"shop_{shop.id}_product_{product.id}.json")
if os.path.exists(model_path):
    os.remove(model_path)

print("Testing predict_demand before training...")
res = predict_demand(db, shop.id, product.id)
print("Result:", res)
assert "error" in res, "Should have returned an error about missing model"

print("\nTesting training model...")
res = train_forecasting_model(db, shop.id, product.id)
print("Result:", res)
assert "message" in res, "Training failed"

print("\nTesting predict_demand after training...")
res = predict_demand(db, shop.id, product.id)
print("Forecast keys:", list(res.keys()))
assert "forecast" in res, "Forecast failed"
if "forecast" in res and res["forecast"]:
    print("First forecast day:", res["forecast"][0])
else:
    print("Forecast empty?", res)

print("\nALL TESTS PASSED")
