from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import random

from models.database import SessionLocal
import models.schemas as schemas
from ml.forecasting import train_forecasting_model

scheduler = BackgroundScheduler()

def train_all_models_nightly():
    """
    Cron job function that runs every night between 3-4 AM to retrain models.
    """
    db = SessionLocal()
    try:
        print("Starting nightly XGBoost model training CRON job...")
        # Get all products across all shops
        products = db.query(schemas.Product).all()
        success_count = 0
        for product in products:
            try:
                # Train the model, will skip if not enough data handled in function
                res = train_forecasting_model(db, product.shop_id, product.id)
                if "error" not in res:
                    success_count += 1
            except Exception as e:
                print(f"Failed to train model for product {product.id}: {e}")
        print(f"Nightly training complete. Successfully trained {success_count} models.")
    finally:
        db.close()

def start_scheduler():
    # Schedule to run at a random minute between 3:00 AM and 3:59 AM every day
    random_minute = random.randint(0, 59)
    scheduler.add_job(
        train_all_models_nightly,
        CronTrigger(hour=3, minute=random_minute),
        id='nightly_ml_training',
        name='Retrain XGBoost models every night',
        replace_existing=True
    )
    scheduler.start()
    print(f"Background ML Scheduler started. Next run scheduled for 3:{random_minute:02d} AM.")

def stop_scheduler():
    scheduler.shutdown()
    print("Background ML Scheduler stopped.")
