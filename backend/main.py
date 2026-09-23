from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
allow_origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000", "http://127.0.0.1:8000"]
if frontend_url != "*" and frontend_url not in allow_origins:
    allow_origins.append(frontend_url)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if frontend_url == "*" else allow_origins,
    allow_credentials=True if frontend_url != "*" else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Mount the static assets directly to avoid catchall latency for JS/CSS files
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

if os.path.isdir(os.path.join(frontend_dist, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

# The catchall MUST be at the very bottom, to serve the React app
@app.get("/{catchall:path}")
def serve_react_app(catchall: str):
    file_path = os.path.join(frontend_dist, catchall)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    index_path = os.path.join(frontend_dist, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
        
    return {"message": "Welcome to ShubhLabh Analytics API. (Frontend build not found)."}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
