# YojanaSetu System Architecture

YojanaSetu is an AI-powered government scheme discovery and navigation platform for Indian citizens. It combines natural language understanding with a strictly deterministic eligibility evaluation engine.

---

## 1. Architectural Principles & Invariants

1. **Deterministic Eligibility:** The LLM extracts citizen criteria and generates clear human explanations. **The LLM never decides eligibility.** Qualification is decided strictly by a deterministic Python rule engine evaluating structured criteria.
2. **Verified Schemes Only:** Only schemes verified by an administrator against an official ministry source are surfaced to citizens.
3. **Citation & Verification Integrity:** Every scheme card and explanation includes the official government source URL and a "last verified" timestamp. If information is missing from the official text, the system explicitly disclaims it rather than guessing.
4. **Zero PII Persistence:** No personal identifiers (Aadhaar, PAN, phone number, email, bank details, or residential address) are requested or persisted. User profile state resides exclusively in browser memory and is transmitted ephemerally per request.
5. **Strict Layered Separation:**
   - **Routers (`app/api/v1`)** handle HTTP requests, headers, and input/output serialization. No business logic resides in routers.
   - **Services (`app/services`)** orchestrate business workflows, rules, and external interfaces. Services never import routers.
   - **Repositories (`app/repositories`)** manage data persistence and vector queries.
   - **Database (`app/db`)** provides raw database client lifecycles.
   - **Pluggable Clients:** The LLM resides behind an `LLMClient` interface and embeddings behind an `EmbeddingClient` interface, ensuring zero vendor lock-in and zero heavy local models in production.

---

## 2. Layered Architecture Diagram

```mermaid
graph TD
    Client["Browser Client (React + Tailwind CSS)"]

    subgraph FastAPI_Backend ["FastAPI Application Backend"]
        subgraph APILayer ["API Routers (app/api/v1)"]
            HealthR["health.py"]
            IntakeR["intake.py"]
            MatchR["match.py"]
            SchemesR["schemes.py"]
            QAR["qa.py"]
            FeedbackR["feedback.py"]
            AdminR["admin.py"]
        end

        subgraph ServiceLayer ["Service Layer (app/services)"]
            PIISvc["pii_guard.py"]
            ExtractorSvc["profile_extractor.py"]
            RuleEngineSvc["rule_engine.py (Deterministic)"]
            RAGSvc["rag_service.py"]
            ExplanationSvc["explanation_service.py"]
            FollowupSvc["followup_selector.py"]
            LLMInterface["LLMClient Interface"]
            EmbedInterface["EmbeddingClient Interface"]
        end

        subgraph RepoLayer ["Repository Layer (app/repositories)"]
            SchemeRepo["scheme_repo.py"]
            ChunkRepo["chunk_repo.py"]
            AdminRepo["admin_repo.py"]
            AuditRepo["audit_repo.py"]
        end

        subgraph DBLayer ["Database Layer (app/db)"]
            MongoMgr["mongo.py"]
            IndexMgr["indexes.py"]
        end
    end

    subgraph ExternalServices ["External Hosted APIs & Storage"]
        AtlasDB[("MongoDB Atlas (Database)")]
        AtlasVector[("MongoDB Atlas Vector Search")]
        GroqAPI["Groq Cloud API (Llama-family LLM)"]
        HostedEmbedAPI["Hosted Multilingual Embedding API"]
    end

    Client -->|Ephemeral JSON Request| APILayer
    APILayer --> ServiceLayer
    ServiceLayer --> RepoLayer
    RepoLayer --> DBLayer
    DBLayer --> AtlasDB
    RepoLayer --> AtlasVector

    LLMInterface --> GroqAPI
    EmbedInterface --> HostedEmbedAPI
    ServiceLayer -.-> LLMInterface
    ServiceLayer -.-> EmbedInterface
```

---

## 3. Data Flows

### A. Offline Data & Scheme Ingestion Pipeline

```mermaid
flowchart LR
    OfficialDocs["Official Ministry Portals / Guidelines"]
    Collect["1. collect.py\n(Scrape / Fetch raw docs)"]
    Parse["2. parse.py\n(Extract sections & metadata)"]
    Extract["3. extract.py\n(Structure eligibility rules)"]
    AdminReview["Admin Verification Gate\n(Status = verified)"]
    Embed["4. embed.py\n(Hosted multilingual embedding)"]
    AtlasStorage[("MongoDB Atlas\n(schemes & vector chunks)")]

    OfficialDocs --> Collect --> Parse --> Extract --> AdminReview --> Embed --> AtlasStorage
```

### B. Online Citizen User Flow

```mermaid
sequenceDiagram
    autonumber
    actor Citizen as Citizen User
    participant Frontend as React Frontend (Vite)
    participant IntakeAPI as /api/v1/intake
    participant MatchAPI as /api/v1/match & /api/v1/qa
    participant PIIGuard as PIIGuardService
    participant LLM as Groq LLM Client
    participant RuleEngine as Deterministic Rule Engine
    participant VectorDB as MongoDB Atlas Vector Search
    participant Explainer as Explanation Service

    Citizen->>Frontend: Describes situation in English or Hindi
    Frontend->>IntakeAPI: POST citizen description
    IntakeAPI->>PIIGuard: Sanitize text & check for PII
    IntakeAPI->>LLM: Extract structured profile (demographics, income, land, etc.)
    LLM-->>IntakeAPI: Structured criteria JSON
    IntakeAPI-->>Frontend: Structured Profile (Saved ONLY in browser memory)

    Citizen->>Frontend: Confirm / Adjust profile & check schemes
    Frontend->>MatchAPI: POST ephemeral profile
    MatchAPI->>RuleEngine: Deterministic evaluation against verified schemes
    RuleEngine-->>MatchAPI: Qualified scheme matches
    MatchAPI->>VectorDB: Semantic retrieval of scheme guideline chunks
    VectorDB-->>MatchAPI: Grounded context chunks
    MatchAPI->>Explainer: Synthesize explanation strictly from retrieved context
    Explainer->>LLM: Formulate citations & reasoning
    LLM-->>Explainer: Grounded explanation with last verified date
    Explainer-->>MatchAPI: Enriched qualified scheme payload
    MatchAPI-->>Frontend: Display verified matches, criteria breakdown & official sources
    Frontend-->>Citizen: Clear results with mandatory non-government disclaimer
```

