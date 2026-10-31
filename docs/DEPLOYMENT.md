# Deployment Guide

## Production Architecture

- **Frontend**: Hosted on Vercel as a static SPA bundle.
  - Environment variable required: `VITE_API_BASE_URL`.
- **Backend**: Hosted on Render as a containerized FastAPI web service.
  - Requires environment variables defined in `backend/.env.example`.
- **Database & Search**: MongoDB Atlas M0/M10+ cluster with Atlas Vector Search index configured for cosine similarity.
- **LLM**: Hosted Groq API (Llama-family model).
- **Embeddings**: Hosted multilingual embedding provider (e.g. Cohere / Voyage / HuggingFace Inference Endpoints).

