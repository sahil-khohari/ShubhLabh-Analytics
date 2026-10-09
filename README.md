# ShubhLabh Analytics 📈

ShubhLabh Analytics is an intelligent, full-stack ERP and Analytics platform designed for Small and Medium Enterprises (SMEs). It offers inventory management, sales tracking, expense monitoring, and state-of-the-art AI capabilities including natural language data querying and predictive demand forecasting.

---

## 🏗️ Architecture & System Design

The application is built on a modern, decoupled architecture designed for scale, security, and performance.

### Tech Stack
- **Frontend:** React.js, Vite, TailwindCSS, Axios
- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic
- **Database:** PostgreSQL (Supabase)
- **Caching & Brokers:** Redis (Upstash)
- **Machine Learning:** XGBoost, Pandas, Scikit-Learn
- **Generative AI:** Google Gemini, LangChain
- **Deployment:** Render (Unified Monolith serving static assets and API)

### 1. Data Flow & Security (Multi-Tenant AI)
Security is paramount when dealing with LLMs (Large Language Models) generating SQL queries. 
- **The Problem:** Giving an AI direct access to the main PostgreSQL database risks multi-tenant data leakage (one shop seeing another shop's data) or destructive `DROP/DELETE` operations.
- **The Solution:** We implemented a **Just-In-Time (JIT) SQLite Sandbox Isolation**.

```mermaid
sequenceDiagram
    participant User
    participant FastAPI
    participant PostgreSQL
    participant SQLite Sandbox
    participant LangChain (Gemini)

    User->>FastAPI: "What were my top selling items?"
    FastAPI->>PostgreSQL: Fetch ONLY this user's data
    PostgreSQL-->>FastAPI: Return Data
    FastAPI->>SQLite Sandbox: Create ephemeral DB & load data
    FastAPI->>LangChain (Gemini): Route query to agent
    LangChain (Gemini)->>SQLite Sandbox: Execute generated SQL safely
    SQLite Sandbox-->>FastAPI: Return query results
    FastAPI->>SQLite Sandbox: Instantly destroy Sandbox
    FastAPI-->>User: Return Natural Language Insights
```

  - When a user asks a question, the backend fetches *only* that user's data from PostgreSQL.
  - It creates a temporary, in-memory/ephemeral SQLite database containing *only* this scoped data.
  - LangChain + Gemini generates and executes SQL queries against this isolated SQLite sandbox.
  - Once the answer is returned, the sandbox is destroyed. Zero risk of cross-tenant leakage.

### 2. Decoupled ML Training Pipeline
Forecasting demand requires heavy CPU and Memory usage, which can crash the server if triggered on-demand by users during peak hours.
- **The Solution:** We decoupled ML Inference from ML Training.

```mermaid
graph TD
    subgraph Background Job (Training Pipeline)
        Cron[APScheduler - 3:00 AM] --> FetchData[Fetch Historical Data]
        FetchData --> TrainModel[Train XGBoost Models]
        TrainModel --> SaveJSON[Save Models to Disk as .json]
    end

    subgraph Real-time API (Inference Pipeline)
        UserRequest[User requests forecast] --> LoadJSON[Load .json Artifact]
        LoadJSON --> Predict[Predict Future Demand in milliseconds]
    end
    
    SaveJSON -.->|Provides Artifact| LoadJSON
```

  - **Training:** Handled by a background job using `APScheduler`. The system triggers a cron job every night between 3 AM - 4 AM. It pulls historical data, trains a new `XGBoost` model for each product, and saves the `.json` model artifact to disk.
  - **Inference:** When a user requests a forecast on the frontend, the FastAPI route instantly loads the pre-trained `.json` artifact from disk to predict future demand. This takes milliseconds and ensures the API remains lightning fast.

### 3. Caching Layer
- **Redis** is used heavily across the application to cache frequent API requests (like dashboard summaries and historical analytics). This significantly reduces the load on the primary PostgreSQL database and ensures sub-100ms response times for users.

---

## 🚀 Local Setup & Installation

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- PostgreSQL Database URL
- Redis Database URL

### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment Variables
# Create a .env file in the backend directory:
DATABASE_URL=postgresql://user:password@localhost:5432/shubhlabh
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=generate_a_secure_random_string_here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME="ShubhLabh Analytics"

# Start the server
uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

---

## 🌍 Production Deployment (Render)

This application is configured for a **Unified Monolith Deployment** on Render. This means the FastAPI backend serves the compiled React frontend static files, requiring only one server instance and avoiding CORS issues entirely.

### Deployment Steps:
1. Connect your GitHub repository to a new Render **Web Service**.
2. Set the Build Command to: `./render-build.sh`
3. Set the Start Command to: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add all Backend `.env` variables into the Render Environment Variables dashboard.
   - *Note: If using Supabase IPv4 Poolers, ensure you are using the Session Pooler connection string (`pooler.supabase.com:5432`).*
5. Click **Deploy**. Render will automatically build the React app, install Python dependencies, and boot the server.

---

## 🛡️ Key Defensible Interview Points

- **Why XGBoost over Deep Learning (LSTM/Transformers)?** 
  SME inventory data is highly tabular, sparse, and lacks millions of rows. XGBoost handles tabular feature engineering (lag features, rolling averages, day-of-week) much better and faster than deep learning models on smaller datasets.
- **Why JIT SQLite over Row-Level Security (RLS)?**
  While RLS is great for standard APIs, LLMs are unpredictable. If an LLM hallucinates a query that somehow bypasses an RLS policy context, it's catastrophic. Moving the data to a physical, isolated sandbox guarantees 100% data security mathematically, rather than relying on prompt engineering.
- **Why APScheduler instead of Celery?**
  For a monolithic startup MVP, Celery requires a separate worker process and complex queue management (RabbitMQ/Redis streams). `APScheduler` runs elegantly inside the FastAPI event loop lifespan, keeping the deployment architecture simple (1 web container) while still perfectly decoupling the training logic.
