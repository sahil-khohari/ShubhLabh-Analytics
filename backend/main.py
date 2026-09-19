from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import models
import utils.cache as cache

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    models.database.Base.metadata.create_all(bind=models.database.engine)
    cache.init_redis()
    yield

app = FastAPI(
    title="ShubhLabh Analytics API",
    description="Backend API for ShubhLabh Analytics",
    version="1.0.0",
    lifespan=lifespan
)

from routers import auth, analytics, ml, ai, sales, inventory, expenses, employees, users

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(analytics.router)
app.include_router(ml.router)
app.include_router(ai.router)
app.include_router(sales.router)
app.include_router(inventory.router)
app.include_router(expenses.router)
app.include_router(employees.router)

import os

# Configure CORS for frontend
frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
allow_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
if frontend_url != "*" and frontend_url not in allow_origins:
    allow_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if frontend_url == "*" else allow_origins,
    allow_credentials=True if frontend_url != "*" else False,  # credentials not allowed with "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the ShubhLabh Analytics API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
