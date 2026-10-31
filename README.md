# YojanaSetu (योजनासेतु)

AI-Powered Government Scheme Navigator for Indian Citizens.

A citizen describes their situation in plain English or Hindi, and YojanaSetu shows which government schemes they qualify for, why, which documents they need, and how to apply.

---

> [!IMPORTANT]
> **Independent Public Information Project**
> YojanaSetu is **not an official Government of India website** and has no official affiliation with any ministry or department.
> National symbols (Ashoka Chakra, State Emblem, National Flag) are strictly omitted in compliance with Emblem and Names guidelines.

---

## 🏛️ Core Product Principles (Invariants)

- **Deterministic Eligibility Engine:** The LLM extracts information and writes explanations. **It never decides eligibility.** Qualification is computed exclusively by a deterministic Python rule engine over structured criteria.
- **Verified Schemes Only:** Only schemes verified by an administrator against official government sources are ever surfaced to users.
- **Grounding and Citations:** Every scheme card and answer presents the official ministry source link and a "last verified" timestamp. If an answer is not present in official documents, the system explicitly disclaims it instead of guessing.
- **Zero PII Persistence:** The platform never requests or stores Aadhaar, PAN, phone number, email, address, or bank details. Citizen profiles exist only in browser memory and are sent ephemerally per request.

---

## 🛠️ Tech Stack

- **Frontend:** React 18, Vite, Tailwind CSS, Lucide Icons, ESLint, Prettier, Vitest.
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, pydantic-settings, Motor (MongoDB async driver), Pytest, Ruff, Black.
- **Database & Search:** MongoDB Atlas with Atlas Vector Search.
- **AI & Embeddings:** Groq Cloud API (Llama-family model), hosted multilingual embeddings via `EmbeddingClient`.
- **Infrastructure:** Docker, Vercel (Frontend), Render (Backend).

---

## 📂 Repository Structure

```text
yojanasetu/
  frontend/              # React + Vite + Tailwind CSS
    src/
      app/               # App layout, providers, routes
      components/        # Reusable UI elements (Header, Footer, DisclaimerBanner)
      features/          # Feature slices: intake/, results/, scheme/, admin/
      lib/               # API client, PII validators, formatters
      i18n/              # en.json, hi.json translations
      styles/            # Tailwind CSS base styles
  backend/               # FastAPI application
    app/
      main.py            # App factory, middleware, router setup
      core/              # config.py, security.py, logging.py, errors.py, rate_limit.py
      api/v1/            # API routers: health, intake, match, schemes, qa, feedback, admin
      schemas/           # Pydantic request/response models
      services/          # llm_client, profile_extractor, rule_engine, rag_service, etc.
      repositories/      # scheme_repo, chunk_repo, admin_repo, audit_repo
      ingestion/         # collect, parse, extract, embed pipelines
      prompts/           # Versioned system prompt text files
      db/                # mongo.py, indexes.py
    tests/               # unit/, api/, security/, evaluation/
    scripts/             # seed_admin.py, seed_schemes.py, ingest.py, evaluate_*.py
  docs/                  # ARCHITECTURE.md, PROGRESS.md, SECURITY.md, API.md, etc.
  .github/workflows/     # CI automation (ci.yml)
  README.md
```

---

## 🚀 Getting Started (Windows PowerShell)

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Git

### 1. Backend Setup

Open PowerShell in the repository root:

```powershell
# Navigate to backend
cd backend

# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt

# Create local environment configuration from template
Copy-Item .env.example .env
```

#### Run Backend Development Server:
```powershell
uvicorn app.main:app --reload --port 8000
```
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)
- API Docs (dev only): [http://localhost:8000/docs](http://localhost:8000/docs)

#### Run Backend Linters & Tests:
```powershell
# Format check with Black
black --check .

# Lint check with Ruff
ruff check .

# Execute Pytest suite
pytest
```

---

### 2. Frontend Setup

Open a new PowerShell terminal:

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create local environment configuration from template
Copy-Item .env.example .env

# Start development server
npm run dev
```
Frontend will be running at [http://localhost:5173](http://localhost:5173).

#### Run Frontend Linters & Tests:
```powershell
# Run ESLint
npm run lint

# Check Prettier formatting
npm run format:check

# Format with Prettier
npm run format

# Run Vitest suite
npm test

# Build production bundle
npm run build
```

---

## 🔒 Pre-Commit & Security Tools

The repository includes `.pre-commit-config.yaml` to enforce Ruff, Black, ESLint, Prettier, and Gitleaks secrets detection before code is committed.

### Installing Pre-Commit & Gitleaks:
1. Install pre-commit in your Python environment:
   ```powershell
   pip install pre-commit
   pre-commit install
   ```
2. **Gitleaks Installation (Optional on Windows):**
   If `gitleaks` is not installed on your system, install it using winget or chocolatey:
   ```powershell
   winget install Gitleaks.Gitleaks
   # OR
   choco install gitleaks
   ```
   If not installed, pre-commit will notify you or can run other hooks without blocking if skipped.

---

## 📖 Architecture & Progress Documentation

- [System Architecture & Flows](docs/ARCHITECTURE.md)
- [Project Progress & Session Logs](docs/PROGRESS.md)
- [Security Baseline & Invariants](docs/SECURITY.md)
- [API Contract](docs/API.md)
- [Evaluation Strategy](docs/EVALUATION.md)
- [Deployment Strategy](docs/DEPLOYMENT.md)

