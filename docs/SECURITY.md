# Security Policy & Invariants

## Non-Negotiable Rules

1. **Zero Personal Identifiable Information (PII) Stored**:
   - The platform never solicits, accepts, or stores:
     - Aadhaar numbers
     - PAN cards
     - Mobile phone numbers
     - Email addresses
     - Residential street addresses
     - Bank account numbers or IFSC codes
   - User profiles reside strictly in browser memory and are evaluated transiently per request.

2. **Strict Input Validation & Sanitization**:
   - Every endpoint strictly validates payloads with Pydantic v2 schemas and enforces maximum length constraints.
   - Text inputs pass through `PIIGuardService` before any LLM processing.
   - LLM responses are treated as untrusted data and sanitized before presentation.

3. **Authentication & Authorization**:
   - Administrative endpoints require signed JWT bearer tokens with expiration limits.
   - Passwords are encrypted with bcrypt.
   - In production, `JWT_SECRET` must be at least 32 characters or startup halts immediately.

4. **Rate Limiting & Abuse Prevention**:
   - Sensitive routes (LLM intake, admin login) enforce sliding-window rate limiting.
   - Global daily LLM invocation caps prevent runaway API bills.

5. **Secrets Management**:
   - All credentials and API keys are passed via environment variables.
   - Real `.env` files are git-ignored; safe placeholders are maintained in `.env.example`.

