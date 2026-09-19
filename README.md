# ShubhLabh360

An AI-powered business intelligence and decision-support platform designed to empower small and medium-sized businesses with enterprise-grade analytics, machine learning forecasting, and natural language insights.

## Overview

ShubhLabh360 solves the data fragmentation and analysis paralysis faced by SME owners. Traditional retail businesses generate thousands of data points daily across sales, inventory, and expenses but lack the tools to synthesize this into actionable intelligence. 

ShubhLabh360 transforms raw transactional data into cohesive visual insights, stockout predictions, and actionable recommendations. Its target users are small and medium-sized business owners and store managers who want to understand their performance dynamically without needing a data science team.

## Key Capabilities

### Business Intelligence
- **Revenue & Sales:** Track total gross revenue and transaction volumes dynamically.
- **Profit & Margin:** Granular calculation of net profit and profit margins based on real-time COGS (Cost of Goods Sold).
- **Expenses:** Monitor categorized operational expenses.
- **Product/Category Performance:** Visualize top-selling items and high-margin categories.
- **Inventory Overview:** Track active stock levels and identify critical low-stock items.

### Diagnostic Analytics
- **Identify Trends:** Determine the underlying reasons behind sales or profit changes over time.
- **Expense Analysis:** Break down spending to identify operational inefficiencies.
- **Product Performance Analysis:** Rank products by velocity and margin contribution.
- **Inventory Anomalies:** Detect irregular inventory movements or shrinkage.

### Predictive Analytics
- **Demand Forecasting:** Predict future product demand using historical sales velocity.
- **Sales Forecasting:** Anticipate revenue trends for the upcoming weeks.
- **Stockout-related Prediction:** Calculate estimated days-of-inventory remaining before a stockout.
- **ML-based Anomaly Detection:** Flag irregular transactions or anomalous spending patterns utilizing Isolation Forests.

### Decision Support
- **Reorder Recommendations:** Algorithmic suggestions for inventory replenishment.
- **Product Performance Actions:** Actionable insights for discounting slow-movers or pushing high-margin products.
- **Inventory Decisions:** Data-driven alerts for managing warehouse capital.
- **Business Investigation Prompts:** One-click prompts to dive deeper into performance metrics.

### AI Business Assistant
Users can interact with their business data using natural language. The AI Assistant converts business questions (e.g., *"What were my top 5 most profitable products last month?"*) into precise SQL queries, executes them against a dynamically isolated database, and returns conversational, data-backed answers.

### Secure Authentication
- **JWT Authentication:** Stateless, secure session management.
- **bcrypt Password Hashing:** Cryptographically secure credential storage.
- **Email OTP Verification:** Two-step signup flow utilizing Gmail SMTP.
- **Redis-backed OTP Storage:** High-performance, transient storage for OTPs.
- **Security Safeguards:** 5-minute OTP expiration, 60-second resend cooldowns, and strict attempt limits.

### Multi-Business Data Isolation
The platform is built from the ground up for multi-tenancy. Authenticated users can access **only** their authorized business/shop data. Backend authorization is enforced physically at the SQLAlchemy ORM and API route levels by dynamically deriving the authorized `shop_id` directly from the signed JWT, completely preventing IDOR (Insecure Direct Object Reference) vulnerabilities.

## Architecture

```mermaid
graph TD
    User([User / Browser])
    
    subgraph Frontend
        React[React + Vite Frontend]
    end
    
    subgraph Backend API
        Auth[Authentication & JWT Middleware]
        
        subgraph Business Services
            Analytics[Analytics Engine]
            ML[ML Forecasting & Anomalies]
            AI[AI Business Assistant]
            Sales[Sales Management]
            Inventory[Inventory Management]
            Expenses[Expense Management]
        end
    end
    
    subgraph Data Layer
        PG[(PostgreSQL Database)]
        Redis[(Redis Cache & OTPs)]
        TempDB[(Ephemeral SQLite)]
    end
    
    subgraph External APIs
        Gemini[Google Gemini API]
        SMTP[Gmail SMTP]
    end

    User -->|HTTPS| React
    React -->|REST / JSON| Auth
    Auth --> Business Services
    
    Sales --> PG
    Inventory --> PG
    Expenses --> PG
    Analytics --> PG
    
    Auth --> Redis
    Auth --> SMTP
    
    ML --> PG
    
    AI -->|1. Fetch Tenant Data| PG
    AI -->|2. Create Isolated Sandbox| TempDB
    AI -->|3. Generate SQL| Gemini
    AI -->|4. Execute SQL| TempDB
```

## Tech Stack

**Frontend:**
- React
- Vite
- Tailwind CSS
- React Router
- Recharts
- Axios

**Backend:**
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Alembic

**Database:**
- PostgreSQL
- Redis

**Analytics / ML:**
- Pandas
- NumPy
- scikit-learn
- XGBoost

**AI:**
- Google Gemini API (langchain-google-genai)

**Security:**
- JWT (python-jose)
- bcrypt/passlib
- OTP via SMTP
- Redis TTL
- Strict tenant/business authorization

**Deployment:**
- Vercel frontend
- Vercel-compatible FastAPI backend
- managed PostgreSQL
- managed Redis

## Project Structure

```text
.
├── backend/
│   ├── alembic/              # Database migration scripts
│   ├── ml/                   # Machine learning models (Forecasting, Anomalies)
│   ├── models/               # SQLAlchemy database schemas
│   ├── routers/              # FastAPI route controllers
│   ├── services/             # Core business logic (AI, Analytics, Email)
│   ├── tests/                # Pytest unit and integration tests
│   ├── utils/                # Auth, Cache, and Seed utilities
│   ├── main.py               # FastAPI application entrypoint
│   └── vercel.json           # Vercel Serverless configuration
├── frontend/
│   ├── public/               # Static assets
│   ├── src/
│   │   ├── components/       # Reusable React components
│   │   ├── context/          # React Context (Auth)
│   │   ├── pages/            # Top-level route views
│   │   └── services/         # Axios API configuration
│   └── vercel.json           # Vercel SPA routing
├── docker-compose.yml        # Local development infrastructure
├── .gitignore                # Git exclusions
├── .env.example              # Environment variable templates
└── README.md                 # Project documentation
```

## Local Development

### 1. Clone the repository
```bash
git clone https://github.com/sahil-khohari/SubhLabh360.git
cd SubhLabh360
```

### 2. Configure Environment Variables
Copy the `.env.example` to `.env` in the `backend/` directory:
```bash
cp backend/.env.example backend/.env
```
Edit `backend/.env` with your actual local credentials (see Environment Variables section).

### 3. Start Infrastructure (PostgreSQL & Redis)
Ensure Docker is running on your machine.
```bash
docker-compose up -d
```

### 4. Setup Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run database migrations:
```bash
alembic upgrade head
```

Start the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```

### 5. Setup Frontend
Open a new terminal window:
```bash
cd frontend
npm install
```

Start the Vite development server:
```bash
npm run dev
```

## Environment Variables

The backend requires the following environment variables (stored in `backend/.env`). **Never commit real values to version control.**

```env
# Database Connections
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
SECRET_KEY=your_super_secret_jwt_key_here
FRONTEND_URL=http://localhost:5173,http://127.0.0.1:5173

# External APIs
GEMINI_API_KEY=your_gemini_api_key_here

# SMTP Configuration (for OTP Emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_gmail_address@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_FROM_EMAIL=your_gmail_address@gmail.com
SMTP_FROM_NAME="ShubhLabh360"
```

## API Overview

The FastAPI backend provides comprehensive REST endpoints:

- **Authentication (`/auth`)**: `/login`, `/signup`, `/verify-otp`, `/resend-otp`
- **Users/Profile (`/users`)**: Profile retrieval and management.
- **Sales (`/sales`)**: CRUD operations for point-of-sale transactions.
- **Inventory (`/inventory`)**: Manage products, categories, stock levels, and restock transactions.
- **Expenses (`/expenses`)**: Track and categorize operational costs.
- **Employees (`/employees`)**: Manage staff profiles and roles.
- **Analytics (`/analytics`)**: Dashboard metrics, profit calculation, top products, and time-series data.
- **ML (`/ml`)**: Generate demand forecasts and detect sales/expense anomalies.
- **AI Assistant (`/ai`)**: Submit natural language queries (`/ask-business-question`).

## Security

ShubhLabh360 implements strict, enterprise-grade security protocols:

- **Authentication:** Handled via cryptographically signed JWTs. Passwords are never stored in plaintext and are hashed using bcrypt.
- **Two-Step Verification:** New account creation requires an email OTP verification step.
- **OTP Hardening:** OTPs are stored in Redis with strict TTL expirations (5 minutes), 60-second resend cooldowns, and failed-attempt limiting.
- **Backend Authorization:** Multi-business isolation is strictly enforced. The API determines the `shop_id` dynamically by decoding the signed JWT (`Depends(get_current_shop)`), making it physically impossible for User A to manipulate parameters to access User B's data.
- **AI Assistant Tenant Isolation:** To prevent the LLM from accidentally querying another business's data, the AI Assistant dynamically creates an ephemeral SQLite database per-request containing *only* the authenticated user's data. The LLM has zero network access to the primary PostgreSQL database.
- **Secrets Management:** All API keys, SMTP credentials, and database passwords are injected exclusively via environment variables and excluded from Git.

## Machine Learning

The platform utilizes embedded ML for operational intelligence:

- **Demand Forecasting:** Utilizes XGBoost Regressors on historical sales velocity to predict the next 7 days of product demand.
- **Anomaly Detection:** Utilizes scikit-learn's `IsolationForest` to identify irregular transaction volumes or unusual expense spikes.
- **Feature Engineering:** Dynamically calculates rolling averages, day-of-week indexing, and historical lag features before prediction.

## AI Assistant Architecture

The AI Assistant is built using LangChain and the Google Gemini API. 

To solve the complex problem of LLM data isolation, ShubhLabh360 uses **Physical Database Isolation**. When a user asks a question:
1. The backend securely queries the primary PostgreSQL database for the authorized tenant's data.
2. It constructs an ephemeral, temporary SQLite database on the local filesystem containing *only* that tenant's records.
3. LangChain provides the LLM with the schema of the isolated SQLite database.
4. The LLM generates SQL, which is executed against the temporary SQLite file.
5. The SQLite file is aggressively deleted (`os.remove`) the moment the request completes.

This guarantees that an LLM hallucination cannot expose another business's data or destroy production records.

## Testing

Backend test coverage utilizes `pytest`.
```bash
cd backend
export DATABASE_URL="sqlite:///:memory:"
pytest tests/
```
Current Status: **12/12 passing** (Authentication flows, Analytics, ML endpoints).

Frontend builds utilize Vite optimization:
```bash
cd frontend
npm run build
```
Current Status: **Passing** (Build successfully completes in ~200ms).

## Deployment

The recommended deployment architecture is:
- **Frontend:** Vercel (Static SPA)
- **Backend:** Vercel (Python serverless runtime)
- **PostgreSQL:** Managed database provider (e.g., Supabase, Neon, AWS RDS)
- **Redis:** Managed Redis provider (e.g., Upstash)

**Important:** You must configure all Environment Variables in your deployment platform's dashboard. Your `.env` file must never be committed.

## Production Checklist

Before going live, ensure the following are configured in your Vercel Dashboard:
- [ ] Configure production `DATABASE_URL`
- [ ] Configure production `REDIS_HOST` and `REDIS_PORT` (or Redis URL)
- [ ] Configure a secure, randomized `SECRET_KEY`
- [ ] Configure `GEMINI_API_KEY`
- [ ] Configure `SMTP_*` credentials
- [ ] Configure `VITE_API_URL` for the frontend Vercel project
- [ ] Configure `FRONTEND_URL` for the backend Vercel project to allow CORS
- [ ] Run Alembic migrations against the production database (`alembic upgrade head`)
- [ ] Verify OTP flow via production email delivery
- [ ] Verify AI Assistant responses
- [ ] Verify cross-business data isolation

## Limitations / Future Improvements

- **AI Assistant Performance:** The current ephemeral SQLite isolation architecture guarantees absolute security but creates a memory and IO bottleneck. Loading a tenant's entire transaction history into pandas DataFrames and writing it to SQLite per-request is not scalable for businesses with hundreds of thousands of rows. Future iterations should utilize PostgreSQL Row-Level Security (RLS) tightly coupled with transaction scopes.
- **Serverless Filesystem:** Vercel serverless functions have a read-only filesystem except for `/tmp`. While Python's `tempfile.mkstemp` utilized by the AI Assistant correctly targets `/tmp`, cold boots and 500MB function limits may constrain concurrent heavy AI queries.
- **ML Training Overhead:** ML models currently train on-the-fly per request. While sufficient for SME data volumes, this should be transitioned to a scheduled background worker (e.g., Celery) as dataset sizes grow.

## License

License: Not specified
