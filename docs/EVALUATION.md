# Evaluation & Benchmarking Strategy

YojanaSetu employs systematic benchmarks across two dimensions:

1. **Persona Evaluation (`evaluate_personas.py`)**:
   - Curated test personas representing typical Indian citizens (e.g. smallholder farmer, marginal weaver, urban street vendor, rural student).
   - Validates that the deterministic Python rule engine outputs 100% mathematically correct qualification statuses against ministry-prescribed eligibility criteria.

2. **RAG & Grounding Evaluation (`evaluate_rag.py`)**:
   - Assesses context retrieval accuracy from MongoDB Atlas Vector Search.
   - Measures hallucination rate: answers must only cite retrieved official ministry clauses.
   - Validates that whenever a scheme clause does not specify an answer, the model explicitly states it is not found instead of guessing.

