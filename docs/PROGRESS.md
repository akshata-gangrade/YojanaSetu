# Project Progress & Activity Log

## Module 1: Repository Structure, Clean Architecture and Environment

- **Status**: Completed
- **Date**: 2026-10-31

### What Was Built
1. **Monorepo Structure**:
   - Initialized `frontend/` (React, Vite, Tailwind CSS, ESLint, Prettier, Vitest).
   - Initialized `backend/` (FastAPI, Pydantic v2, pydantic-settings, Ruff, Black, Pytest).
   - Configured root settings: `.gitignore`, `.dockerignore`, `.editorconfig`, `.pre-commit-config.yaml`, and `.github/workflows/ci.yml`.
2. **Backend Clean Architecture**:
   - Implemented typed `Settings` in `app/core/config.py` using `pydantic-settings`, with fail-fast validation for missing variables and production length checks on `JWT_SECRET` (>= 32 characters).
   - Configured `backend/.env.example` documenting all configuration keys.
   - Built FastAPI factory in `app/main.py` with CORS, structured logging, centralized error handlers, and `/health` route.
   - Scaffolded interface-driven layer separation:
     - `api/v1/`: `health`, `intake`, `match`, `schemes`, `qa`, `feedback`, `admin`.
     - `services/`: `llm_client`, `profile_extractor`, `rule_engine`, `rag_service`, `explanation_service`, `followup_selector`, `pii_guard`.
     - `repositories/`: `scheme_repo`, `chunk_repo`, `admin_repo`, `audit_repo`.
     - `db/`: `mongo`, `indexes`.
     - `ingestion/`: `collect`, `parse`, `extract`, `embed`.
     - `prompts/`: versioned prompt templates.
     - `scripts/`: seeding and benchmark evaluators.
   - Configured virtual environment at `backend/.venv`, separated `requirements.txt` and `requirements-dev.txt`, with unit and API tests.
3. **Frontend Scaffold**:
   - React + Vite + Tailwind CSS scaffold with feature-sliced structure (`intake`, `results`, `scheme`, `admin`).
   - Mandated disclaimers ("Not an official Government of India website") across Header, Footer, and Results components, without national symbols.
   - Configured `frontend/.env.example` with `VITE_API_BASE_URL` exclusively.
   - Configured ESLint 9 and Prettier formatting.
4. **Documentation**:
   - Created `docs/ARCHITECTURE.md` featuring Mermaid diagrams for layered clean architecture, offline data ingestion pipeline, and online citizen request flow.
   - Scaffolding for `SECURITY.md`, `API.md`, `EVALUATION.md`, and `DEPLOYMENT.md`.

### Decisions
- Standardized on pydantic-settings with explicit validator checks for production environments.
- Kept embeddings strictly behind a hosted `EmbeddingClient` interface rather than pulling heavy local ML packages into the production backend.
- Positioned `/health` at both `/health` (for direct Docker/orchestrator pings) and `/api/v1/health` (for standard versioned client consumers).
- Built client-side PII regex filter baseline and backend `PIIGuardService` to uphold the zero-PII invariant from day one.

### Assumptions
- Python 3.11+ is available on developer and CI machines.
- Node.js 18+ is present for Vite and React frontend tooling.
- MongoDB Atlas will host collections and vector search indexes.

### Open Issues / Next Steps
- Implement Scheme Ingestion and Parsing module.
- Implement Groq LLM integration for citizen intake parsing in Module 2.

