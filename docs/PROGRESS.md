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

---

## Module: Design System, UI/UX, and Logo (Frontend Shell)

- **Status**: Completed
- **Date**: 2026-10-31

### What Was Built
1. **Design Tokens & Theme Architecture**:
   - Defined CSS variables in `frontend/src/styles/index.css` and mapped them to Tailwind CSS in `tailwind.config.js`:
     - Navy `#0B2A5B` (headings, primary brand, header, footer).
     - Saffron `#FF9933` (accents, highlights, borders, icons, large text).
     - Dark Saffron `#9A4A00` (for small text on white backgrounds and light tints, ensuring WCAG 2.1 AA 4.5:1+ contrast).
     - Green `#138808` (primary buttons, success, "Eligible" status).
     - White `#FFFFFF`, page background `#F7F9FC`, borders `#D9E0EA`, primary text `#1A2433`, muted text `#55627A`.
     - Status tokens: Eligible (green `#138808`), Maybe eligible (saffron `#9A4A00` on `#FFF4E5`), Not eligible (neutral grey `#475569` on `#F1F5F9` with reason text in `#B3261E`).
   - High contrast mode support (`html[data-contrast="high"]`) and fluid typography scaling (`data-text-size="normal|large|xlarge"`).
   - Automated mathematical test suite `src/styles/contrast.test.js` validating that all 13 color pairs satisfy WCAG 2.1 AA contrast requirements.

2. **Self-Hosted Typography**:
   - Integrated self-hosted Fontsource packages: `@fontsource/inter` (Latin) and `@fontsource/noto-sans-devanagari` (Hindi).
   - Zero external calls or dependencies on Google Fonts CDN.
   - Body line height 1.6, base minimum size 16px, fluid responsive scaling.

3. **Inline SVG Logo & Favicon**:
   - Implemented `Logo.jsx` with `mark` and `horizontal` variants.
   - Design follows a concentric two-arch bridge motif (saffron outer arch, green inner arch, navy deck, and navy eligibility checkmark).
   - Live text for "Yojana" (navy `#0B2A5B`) and "Setu" (green `#138808`), with tagline: *"Bridging people to the schemes they deserve."*
   - Created standalone `public/favicon.svg` and updated `index.html`.

4. **App Shell & Layout**:
   - `UtilityBar.jsx`: Skip-to-content link, language toggle (`English` / `हिन्दी`), text-size controls (`A−`, `A`, `A+`), and high-contrast toggle.
   - `Header.jsx`: Logo, accessible navigation links (`Home`, `Check Eligibility`, `Browse Schemes`, `About`), mobile responsive drawer, and tri-color saffron/white/green accent stripe.
   - `Footer.jsx`: Institutional navy background, non-government disclaimer ("Not an official Government of India website"), zero data persistence guarantee, links to About, Privacy, and Terms, and last-updated verification date (*October 2026*).
   - Max content width 1200px, 8px grid system, 12px card border radius, soft shadows.

5. **Accessible Component Library (`frontend/src/components/ui/`)**:
   - `Button`: Primary (#138808), secondary (#0B2A5B), outline, ghost, loading spinner (`aria-busy`), disabled state, and 44px minimum tap targets.
   - `Card`: 12px radius, soft shadow, `#D9E0EA` border, with loading skeleton, error, and empty state rendering.
   - `Badge`: Eligible, Maybe eligible, and Not eligible (with `#B3261E` reason display).
   - `Alert`: Info, warning, error, success with `role="alert"`.
   - `Stepper`: Multi-step indicator with `aria-current="step"` and keyboard support.
   - `ChatBubble`: Conversational bubble with `aria-live="polite"`, timestamps, and animated typing indicator.
   - `TextInput`: Accessible label, helper text, `#B3261E` error state, and 3px navy focus ring.
   - `Checklist`: Document and criteria checklist with status indicators.
   - `Tabs`: Keyboard-navigable tablist (`ArrowLeft`, `ArrowRight`, `Home`, `End`).
   - `Skeleton`: Pulse loaders for cards, text lines, buttons, respecting `prefers-reduced-motion`.
   - `Toast` & `useToast`: Accessible notification toasts with polite live announcements.
   - `Modal`: Native HTML `<dialog>` with scroll containment (`overscroll-behavior: contain`) and ESC dismissal.
   - `EmptyState` & `ErrorState`: High-clarity fallback components.

6. **Routing & Placeholder Pages (`react-router-dom` & `react-i18next`)**:
   - `/`: Clean Homepage with hero, single primary CTA, 3-step "How it works", and Trust & Privacy section.
   - `/about`: Mission, independence declaration, and official sources disclaimer.
   - `/privacy`: Zero-storage guarantee (no Aadhaar, PAN, phone, email, or bank details collected).
   - `/terms`: Informational terms of service and external portal links.
   - `/schemes`: Placeholder with `EmptyState` indicating directory will arrive with verified gazette data.
   - `/check-eligibility`: Placeholder with `EmptyState` indicating questionnaire will arrive with verified rules.
   - `/admin`: Placeholder titled "Admin sign-in (coming soon)" with `noindex, nofollow` robots meta tag and zero navigation links.
   - `/design-system`: Full interactive showcase of all components, registered strictly when `import.meta.env.DEV` is true.
   - `*`: 404 page with home navigation.

7. **Refinements & Institutional Accuracy**:
   - **Trust & Claim Precision**: Replaced "Official / Ministry-verified sources" with "Verified sources / Checked against official government sources" and "0 Bytes / Personal data stored" with "No personal data / Stored by us". Cleaned copy across `en.json`, `hi.json`, and components to prevent implying government endorsement or unprovable guarantees.
   - **Hero Badge**: Standardized to `"100% Free • Privacy First • No Login Required"` without hyphens (Hindi: `"100% निःशुल्क • गोपनीयता पहले • लॉगिन ज़रूरी नहीं"`), removing unnecessary hyphens across the hero section.
   - **Hero Subtitle Trust Line**: Replaced with exact verified wording:
     - EN: *"Find the schemes you qualify for in minutes. We never ask for your name, Aadhaar, phone number, or bank details, and every scheme is checked against its official source."*
     - HI: *"कुछ ही मिनटों में जानें कि आप किन योजनाओं के पात्र हैं। हम आपका नाम, आधार, फ़ोन नंबर या बैंक विवरण कभी नहीं माँगते, और हर योजना की जाँच उसके आधिकारिक स्रोत से की जाती है।"*
   - **High Contrast Mode & Pre-Paint Flash Prevention**:
     - Diagnosed that Tailwind arbitrary classes bypassed contrast variables without explicit `html[data-contrast="high"]` overrides.
     - Defined a comprehensive high contrast token set under `html[data-contrast="high"]`: pure black text (`#000000`) on white (`#FFFFFF`), 2px solid black borders on cards, inputs, and buttons, underlined links, no tinted/translucent backgrounds, hero displayed as a solid black panel with white text, black buttons with white text, and 3px focus rings on all interactive elements.
     - Differentiated status badges through distinct icons (`✓`, `?`, `✕`), explicit text labels, and border treatments (`solid`, `dashed`, `inverted solid`), meeting WCAG 1.4.1 (Use of Color).
     - Synchronous inline `<script>` in `<head>` applies `data-contrast="high"` before initial DOM paint, preventing flash of low contrast.
     - Added automated DOM unit test suite `src/styles/highContrast.test.js` verifying attribute toggling, token overrides, 21:1 black/white contrast, and `localStorage` privacy compliance.

8. **High Contrast Fixes, Text Size Controls, and 360px Mobile Layout**:
   - **Hero Trust Strip High-Contrast Fix**:
     - Diagnosed cause of white block: `[class*='border-white/']` in `index.css` had erroneously set `background-color: #ffffff !important;` on the trust strip container inside the black hero panel, while all children had `color: #ffffff !important;` (white text on white background).
     - Fixed by removing `border-white/` from background overrides, making `[data-hero-trust-strip]` explicitly transparent with a 2px solid white top border, and styling `[data-stat-icon]` with black backgrounds and 2px solid white borders.
     - Enforced `stroke: currentColor` on all SVGs, ensuring the button arrow inherits black on the white primary button, and all trust icons inherit pure white on black.
     - Added `[data-hero-arch]` and hid the decorative arch graphic in high contrast mode via `html[data-contrast='high'] [data-hero-arch] { display: none !important; }`.
   - **Text Size Controls Replacement**:
     - Replaced `A-`, `A`, `A+` controls with `A` (16px, default and selected on first load), `A+` (18px), and `A++` (20px).
     - Marked the active button with `aria-pressed="true"`, stored the preference in `localStorage` under `yojanasetu_text_size`, and pre-painted via synchronous `<head>` script.
     - Added automated unit tests in `highContrast.test.js` validating text size switching and persistence.
   - **Utility Bar 360px Readability**:
     - Replaced badge text with `"Independent informational project. Not an official Government of India website."` (Hindi: `"स्वतंत्र सूचनात्मक परियोजना। यह भारत सरकार की आधिकारिक वेबसाइट नहीं है।"`).
     - Designed mobile-first layout using `flex-col sm:flex-row` and `break-words leading-relaxed text-[11px] sm:text-xs` so text wraps naturally across two legible lines on 360px screens without truncation.
   - **Hero Trust Copy Update**:
     - Item 1: `"Hindi and English / Choose your language"` (Hindi: `"हिन्दी और अंग्रेज़ी / अपनी भाषा चुनें"`).
     - Item 2: `"No personal data stored / We keep none of your details"` (Hindi: `"कोई व्यक्तिगत डेटा संगृहीत नहीं / हम आपका कोई विवरण नहीं रखते"`).
     - Item 3: `"Verified sources / Checked against official government sources"` (Hindi: `"सत्यापित स्रोत / आधिकारिक सरकारी स्रोतों से जाँचे गए"`).
   - **Comprehensive Page Audit**:
     - Audited and converted fixed color hexes (`#0B2A5B`, `#55627A`, `#1A2433`, `#D9E0EA`, etc.) across `Home`, `About`, `Privacy`, `Terms`, `Check Eligibility`, `Browse Schemes`, `Admin`, and `404` to semantic theme tokens, guaranteeing pure black-on-white / white-on-black contrast everywhere.

9. **Single-Polarity High Contrast Mode Redesign (Pure Black on White)**:
   - **Root Cause Analysis of Prior High Contrast Inversions**:
     - The previous two-polarity design (inverted solid black hero banner with white text alongside white cards with black text) was prone to color collisions when arbitrary Tailwind utility classes (`border-white/10`, `bg-white/10`, `text-[#FF9933]`, `bg-white/20`) caused the hero badge to render as a white pill with invisible white text, the secondary button to show as a blank white box, and the trust tiles to show as empty white squares with missing icons.
   - **New Architecture - Single Polarity Everywhere**:
     - Enforced a single polarity (pure black `#000000` text on pure white `#FFFFFF` background) everywhere across the application: page, header, utility bar, hero section, cards, modals, inputs, and footer.
     - Zero dark panels, zero inverted sections, zero translucent tints, and zero opacity below 1.
     - Hero, cards, inputs, badges, icon tiles, and buttons receive a uniform `2px solid #000000` border.
     - Primary action buttons: solid `#000000` background, pure `#FFFFFF` text, with SVG arrow icons styled via `currentColor` (`#FFFFFF`). Explicitly targeted via `[data-variant="primary"]`.
     - Secondary, outline, and ghost buttons: `#FFFFFF` background, `#000000` text, and `2px solid #000000` border.
     - Links: pure black and underlined with accessible text-underline-offset.
     - Focus ring: `3px solid #000000` with a `2px` white offset (`outline-offset: 2px`).
     - Removed gradients, box shadows, text shadows, translucency, background images, and decorative elements (decorative arch `[data-hero-arch]` and header tricolor accent line `[data-header-accent]` set to `display: none !important`).
     - Status badges (Eligible, Maybe Eligible, Not Eligible): `#FFFFFF` background, `#000000` border and text, plus distinct status icons (`✓`, `?`, `✕`), border patterns (`solid`, `dashed`, `double`), and text labels (`data-badge-reason`).
     - All SVG icons enforce `fill: currentColor` (or `fill: none` when stroked) and `stroke: currentColor`.
   - **Unified Implementation Strategy**:
     - Rather than patching individual components, implemented a single unified override block at the end of `src/styles/index.css` scoped to `[data-contrast="high"]`.
     - Applied universal baseline rules (`background-color: #ffffff !important`, `color: #000000 !important`, `border-color: #000000 !important`, `box-shadow: none !important`), followed by clean, targeted exceptions for primary buttons, utility active buttons, and focus outlines.
   - **Comprehensive Page Verification**:
     - Verified all 8 core pages (`Home`, `About`, `Privacy`, `Terms`, `Check Eligibility`, `Browse Schemes`, `Admin`, and `404`) in high contrast mode:
       - Confirmed via select-all (Ctrl+A) that zero text or icons are invisible.
       - Hero badge renders with black text and border on white background.
       - "Browse All Schemes" button renders as white button with black text and 2px black border.
       - Three trust icon tiles render with white background, 2px black border, and visible black icons.
       - Header, footer, modals, alerts, and inputs render with crisp black-on-white polarity.
   - **Test & Accessibility Guarantees**:
     - High contrast toggle in `UtilityBar` marked with `aria-pressed={highContrast}`.
     - Synchronous `<head>` script in `index.html` prevents flash before first paint.
     - Expanded unit test suite `src/styles/highContrast.test.js` to 8 tests verifying attribute toggling, `aria-pressed`, pre-paint DOM execution, 21:1 contrast ratio, primary button exceptions, and privacy storage invariants.

### Decisions
- Separated the Design System showcase into `/design-system` behind `import.meta.env.DEV` so production builds remain lightweight and clean.
- Kept `BrowseSchemesPage` and `CheckEligibilityPage` as clean placeholders using `EmptyState` without any mock or fabricated scheme results, maintaining institutional integrity.
- Admin page removed from all navigation and protected with an automated `noindex, nofollow` DOM meta tag effect.
- Standardized high contrast mode on a single polarity (pure black on white) rather than inverted polarity blocks, eliminating any possibility of white-on-white text bugs.
- UI preferences (`yojanasetu_lang`, `yojanasetu_text_size`, `yojanasetu_contrast`) are stored in `localStorage`, while citizen profiles remain transient in memory only.

### Verification
- **Vitest**: 30 tests passing across contrast calculations, text size scalability, high contrast DOM manipulation, i18n key parity, and validator security.
- **ESLint**: 0 errors, 0 warnings.
- **Prettier**: Clean formatting verification across all source files.
- **Vite Build**: Production build passes with zero errors, bundling self-hosted fonts into `dist/`.

---

## Module: Database Schema, Repositories, and MongoDB Data Layer

- **Status**: Completed
- **Date**: 2026-10-31

### What Was Built
1. **Pydantic Schemas (`backend/app/schemas/`)**:
   - `enums.py`: `SchemeLevel`, `SchemeStatus`, `ChunkSection`, `AdminRole`, `FeedbackVote`, `CriterionField`, `CriterionOperator`, and complete Indian states and demographic enums (`Gender`, `IndianState`, `SocialCategory`, `Occupation`, `EducationLevel`, `ResidenceType`, `MaritalStatus`, `DisabilityStatus`).
   - `criteria.py`: `Criterion` and `EligibilityCriteria` supporting deterministic operators (`eq`, `in`, `not_in`, `gte`, `lte`, `between`) with strict boundary and type validation.
   - `user_profile.py`: `UserProfile` model with bounded numbers and strict enums (`extra="forbid"`), where omitted fields or `prefer_not_to_say` signify unknown criteria. Preserves zero persistence invariant.
   - `scheme.py`: `SchemeBase`, `SchemeCreate`, `SchemeUpdate`, `Scheme` with slug regex, url protocol validation, and central/state level invariants.
   - `chunk.py`: `SchemeChunkBase`, `SchemeChunkCreate`, `SchemeChunk` for vector search retrieval.
   - `admin.py`: `AdminUserBase`, `AdminUserCreate`, `AdminUserInDB`, `AdminUser` with login attempt and lockout tracking.
   - `audit.py`: `AuditLogBase`, `AuditLogCreate`, `AuditLog` immutable append-only models.
   - `feedback.py`: `FeedbackBase`, `FeedbackCreate`, `Feedback` with 90-day TTL constraint and zero personal identifiers.

2. **MongoDB Data Layer (`backend/app/db/`)**:
   - `mongo.py`: Switched to PyMongo 4.9+ native `AsyncMongoClient` with shared connection pool, socket timeouts, and graceful asynchronous shutdown (`await aclose()`). Replaced deprecated Motor dependency.
   - `indexes.py`: Implemented unique index on `schemes.slug`, compound index on `(status, state, level)`, unique index on `admin_users.email`, index on `scheme_chunks.scheme_id`, 90-day TTL index on `feedback.created_at`, reverse chronological index on `audit_logs`, and Atlas Vector Search index creation with asynchronous polling.

3. **Repositories & Test Fakes (`backend/app/repositories/`)**:
   - `base.py`: Protocol interfaces for `ISchemeRepository`, `IChunkRepository`, `IAdminRepository`, `IAuditRepository`, and `IFeedbackRepository`.
   - `scheme_repo.py`: Whitelisted query building, strictly enforcing `status="verified"` and `is_sample=False` for production queries.
   - `chunk_repo.py`: Chunk CRUD and Atlas Vector Search aggregation pipeline (`$vectorSearch`).
   - `admin_repo.py`: Admin account lookups, failed login attempt tracking, and account lockouts.
   - `audit_repo.py`: Append-only audit logger without delete/update mutations.
   - `feedback_repo.py`: Anonymous helpfulness rating collection.
   - `fakes.py`: High-speed in-memory fake repositories replicating database semantics for 100% test isolation.

4. **Sample Seeding Script (`backend/scripts/seed_schemes.py`)**:
   - 5 clearly labelled FICTIONAL sample schemes (`pm-yuva`, `kanya-shiksha`, `maha-solar`, `divyangjan-skills`, `up-vridha`) marked `is_sample: True`.
   - CLI flags: `--confirm` strictly required to perform database writes; `--purge-samples` to clean up fictional test data.
   - Completely isolated from automated test execution.

5. **Test Suite & Verification**:
   - 32 pytest tests passing across unit schemas, repositories, indexes, and health endpoints.
   - Ruff and Black checks pass with 0 errors and 0 warnings.

### Decisions
- Replaced deprecated Motor driver with PyMongo 4.9+ native `AsyncMongoClient` across the application.
- Structured `UserProfile` with `extra="forbid"` and helper methods (`is_field_unknown`, `get_effective_value`) ensuring no personal data can ever be ingested or persisted.
- Isolated unit tests with `Fake*Repository` classes so tests execute instantly without requiring Atlas or network connectivity.
- Implemented vector index creation in `indexes.py` behind an unexecuted function awaiting final embedding model confirmation.
- Made `seed_schemes.py` strictly require an explicit `--confirm` flag, refusing to execute or seed any data automatically.

### Assumptions
- Database name is read from `MONGODB_DB` (default `yojanasetu`).
- Target embedding model will output vectors with dimensionality matching `EMBEDDING_DIM` (384).

### Open Issues / Next Steps
- Create Atlas Vector Search index after hosted multilingual embedding model is final.
- Implement Module: Deterministic Python Rule Engine over structured criteria.

---

## Follow-up: Data Layer Refinements & Live Standard Index Creation

- **Status**: Completed
- **Date**: 2026-10-31

### What Was Built & Modified
1. **PyMongo Driver Upgrade**:
   - Upgraded `pymongo` to latest stable release on PyPI: `4.19.0`.
   - Completely uninstalled deprecated `motor` package.
   - Pinned `pymongo==4.19.0` in `backend/requirements.txt`.
2. **Vector Index Definition Verification**:
   - Verified that `create_vector_index()` in `backend/app/db/indexes.py` defines `"similarity": "cosine"`, uses `embedding_dim` parameter, targets `"path": "embedding"`, and declares both `"section"` and `"scheme_id"` as filter fields for metadata filtering. Left strictly unexecuted per instructions.
3. **`INCLUDE_SAMPLE_SCHEMES` Setting & Invariants**:
   - Added `INCLUDE_SAMPLE_SCHEMES: bool = False` to `Settings` in `backend/app/core/config.py`.
   - Added fail-fast startup validator rejecting `INCLUDE_SAMPLE_SCHEMES=True` when `ENV="production"`.
   - Updated `SchemeRepository` and `FakeSchemeRepository` (`get_verified_schemes` and `count_verified`) to evaluate `get_settings().INCLUDE_SAMPLE_SCHEMES` when `include_samples` is not passed.
   - Documented in `backend/.env.example`, root `.env.example`, and referenced in `frontend/.env.example`.
   - Added 3 unit tests verifying: default exclusion, development enablement, and production startup rejection.
4. **Sample Purge Invariant Verification**:
   - Added `test_purge_samples_preserves_real_schemes` confirming that `delete_sample_schemes()` deletes only `is_sample: True` schemes and preserves real schemes (`is_sample: False`) completely intact.
5. **Standard Index Execution on Live Database**:
   - Implemented idempotent `backend/scripts/create_indexes.py` printing verified indexes per collection.
   - Executed against user's live database: created standard non-vector indexes across `schemes`, `admin_users`, `scheme_chunks`, `feedback`, and `audit_logs`.
   - Vector index was omitted; zero documents inserted.

### Verification
- **Pytest**: 37 passed in 0.20s.
- **Ruff**: All checks passed with 0 errors.
- **Black**: Clean formatting verification across all source files.

---

## Follow-up: Settings Test Isolation & Ambient Environment Stripping

- **Status**: Completed
- **Date**: 2026-10-31

### What Was Built & Modified
1. **Settings Constructor Isolation**:
   - Passed `_env_file=None` in all test calls instantiating `Settings(...)` across `tests/unit/test_config.py` and `tests/conftest.py` so tests never load local `.env` files.
2. **Conftest Autouse Isolation Fixture**:
   - Added `isolate_settings_env` autouse fixture in `tests/conftest.py` using `monkeypatch` to delete all environment variables matching `Settings.model_fields.keys()` and calling `get_settings.cache_clear()` before and after every test.
3. **Environment Isolation Proof Test**:
   - Added `test_settings_isolated_from_process_environment` in `tests/unit/test_config.py` proving that even when `INCLUDE_SAMPLE_SCHEMES=true` exists in the local environment, `Settings(_env_file=None)` evaluates cleanly to `False` without influence from local files or ambient state.
4. **Test Suite Isolation Audit**:
   - Fixed `test_indexes.py` to use `test_settings` fixture rather than calling bare `get_settings()`.
   - Updated `FakeSchemeRepository` to take `include_sample_schemes: bool = False` by default for 100% deterministic test isolation.

---

## Module: Deterministic Rule Engine & Follow-up Selector

- **Status**: Completed
- **Date**: 2026-10-31

### What Was Built & Modified
1. **Deterministic Rule Engine (`backend/app/services/rule_engine.py`)**:
   - Implemented `RuleEngineService`, pure Python engine with zero database, network, LLM, or randomness dependencies.
   - Built three-valued logic system (`ThreeValuedLogic`: `TRUE`, `FALSE`, `UNKNOWN`):
     - Missing or `prefer_not_to_say` fields evaluate strictly to `UNKNOWN`, never `FALSE`.
     - In `all_of`: any condition evaluating to `FALSE` yields `not_eligible`; otherwise any `UNKNOWN` condition yields `maybe`; otherwise `eligible`.
     - In `any_of`: any condition evaluating to `TRUE` satisfies the block; all conditions evaluating to `FALSE` fails the block; otherwise `UNKNOWN`.
     - In combined conjunction (`all_of` AND `any_of`), one failed condition deterministically beats unknowns (`not_eligible`).
   - Exact boundary value enforcement across all operators (`eq`, `in`, `not_in`, `gte`, `lte`, `between`).
   - Age "as on" cut-off date evaluation with mathematical precision using user DOB or age windows.
   - Bilingual reason generation in English and Hindi from deterministic templates without LLM involvement (e.g. `"Age 18 to 30: your age is 22 ✓"`, `"आयु 18 से 30: आपकी आयु 22 है ✓"`).
   - Fast state and level pre-filtering (`prefilter_schemes` and `evaluate_scheme`): central schemes apply nationwide; state schemes mismatching citizen domicile are disqualified or pre-filtered.
   - Defensive validation raising clear errors on malformed criteria, invalid operators, or incompatible types.

2. **Follow-up Question Selector (`backend/app/services/followup_selector.py`)**:
   - Implemented `FollowupSelectorService` to resolve citizen qualification ambiguity across candidate "maybe" schemes.
   - Frequency-based ranking: finds the single missing field appearing in the most candidate schemes.
   - Deterministic tie-breaking: ties broken strictly by `FIELD_PRIORITY_ORDER` (`age` > `annual_income` > `state` > `gender` > `occupation` > `social_category` > `residence_type` > `education_level` > `marital_status` > `disability_status` > `is_student`).
   - Generates plain-language clarification questions in English and Hindi for all standard profile attributes.
   - Automatically filters out already-answered profile attributes and returns `None` when candidate set is empty or unambiguous.

3. **Schema Refinements (`backend/app/schemas/`)**:
   - `criteria.py`: Tightened `as_on` typing to `date | None` (removed string unions and custom validators); Pydantic v2 automatically coerces ISO date strings like `"2026-01-01"` to `date` and rejects malformed strings with `ValidationError`.
   - `user_profile.py`: Completely removed `dob` field, its validator, and all associated branches across `is_field_unknown` and `get_effective_value`. Date of birth is not collected, ensuring strictly minimal citizen data collection.

4. **Age Cut-off Evaluation from Age Alone**:
   - `rule_engine.py`: Removed `_calculate_exact_age_on_date` and the `dob` branch. Implemented `_compute_possible_age_range_at_cutoff`, which determines the possible completed age interval on the cut-off date from current age alone.
   - Evaluates the condition across the entire possible range: returns True if whole range passes, False if whole range fails, and Unknown (resulting in "maybe") if the range straddles the boundary. Tested for both past and future cut-off dates across all 3 cases.

5. **Test Suite & Tooling**:
   - Added `pytest-timeout==2.3.1` and `pytest-cov==6.0.0` to `backend/requirements-dev.txt`.
   - Configured `timeout = 10` in `backend/pyproject.toml`.
   - Added 60 comprehensive unit tests in `backend/tests/unit/test_rule_engine.py` (48 tests) and `backend/tests/unit/test_followup_selector.py` (12 tests).
   - Reached **97% line coverage** on `app.services.rule_engine` (surpassing 95% threshold).
   - Verified that `findstr /s /i /n "dob" app\*.py tests\*.py` returns zero matches across the entire codebase.
   - Black and Ruff formatting and linting pass with 0 errors across `app`, `tests`, and `scripts`.

### Decisions
- Structured `EligibilityResult` with bilingual collections (`passed_conditions_en`, `passed_conditions_hi`, `failed_conditions_en`, `failed_conditions_hi`) while honoring requested `lang` in default `passed_conditions` and `failed_conditions`.
- Kept all reason generation purely templated to enforce zero hallucination and complete auditability.
- Pre-filtering preserves all schemes when citizen state is unknown, ensuring potential state scheme matches are never prematurely discarded.

### Assumptions
- Input profile has passed Pydantic validation before being passed to rule evaluation.
- Dates follow ISO 8601 formatting (`YYYY-MM-DD`).

### Open Issues / Next Steps
- Integrate `RuleEngineService` and `FollowupSelectorService` into the `/api/v1/match` endpoint and conversational intake flow.







---

## Module: Backend API and LLM Integration (Part A - LLM Layer, Profile Extraction & PII Guard)

- **Status**: Completed
- **Date**: 2026-11-01

### What Was Built & Modified
1. **PII Guard Service (`backend/app/services/pii_guard.py`)**:
   - Upgraded regex detection across Aadhaar (4-4-4 format with hyphens/spaces and continuous 12 digits), PAN (case-insensitive 5 letters, 4 digits, 1 letter), Indian phone numbers (10 digits starting with 6-9, with optional +91/0 prefix and delimiters), and standard email addresses.
   - Preserves legitimate scheme criteria numbers (age, income like 250000, pincodes, land acreage, years) from accidental false-positive redaction.
   - Implemented `scan_and_redact()` returning `PIIGuardResult` with sanitized text, detected PII categories, and bilingual user advisory notices ("Notice: Sensitive personal details were detected and removed...").
   - Preserved backwards-compatible `sanitize()` classmethod.

2. **LLM Layer & Groq Provider (`backend/app/services/llm_client.py`)**:
   - Defined `LLMClient` abstract interface supporting unstructured text (`generate`) and schema-governed JSON (`generate_structured`).
   - Implemented `GroqClient` with `GroqLLMClient` backwards-compatibility alias:
     - Model and API key sourced strictly from typed settings (`GROQ_MODEL`, `GROQ_API_KEY`).
     - Enforces 20-second timeout, 2 retries with exponential backoff on network/5xx/429 errors.
     - Enforces application-wide daily budget tracking via `DailyCallTracker` against `LLM_DAILY_CALL_CAP`.
     - Supports structured outputs with `response_format={"type": "json_schema", ...}` in strict mode.
     - Gracefully degrades parameters: automatically strips `reasoning_effort` and/or `temperature` if rejected by the model API without crashing.
     - Validates non-truncation (`finish_reason != "length"`) and non-empty responses.

3. **Versioned Extraction Prompt (`backend/app/prompts/v1_profile_extraction.txt`)**:
   - Versioned prompt template loaded from disk (never inline strings).
   - Treats citizen message strictly as raw text data; explicitly ignores embedded prompts or injection attempts.
   - Enforces zero LLM arithmetic (extracts raw numbers and raw units).
   - Prohibits inferring sensitive fields (`social_category`, `disability_status`) unless explicitly stated.

4. **Profile Extraction Service (`backend/app/services/profile_extractor.py`)**:
   - Built `ProfileExtractorService` orchestrating PII pre-redaction, structured LLM extraction, deterministic currency/period calculations, and Pydantic validation.
   - Implemented `calculate_annual_income()`: deterministic Python conversion for Indian monetary scales (crore, lakh, hazaar, k, rupees) and payment periods (monthly, annual, daily).
   - Formatted strict JSON Schema where every UserProfile property is required and nullable (`[type, null]`), preventing hallucinated demographic attributes.
   - Validates response with Pydantic `RawExtractedProfile`; retries once on schema/truncation error, and returns safe fallback (`"Please rephrase"`) if errors persist.
   - Returns only detected fields as normalized English enum values.

5. **Diagnostic & Benchmark Scripts (`backend/scripts/`)**:
   - `scripts/smoke_llm.py`: Live Groq connectivity verification making one minimal call and printing strictly "OK" or the error type without exposing secrets.
   - `scripts/try_extraction.py`: Benchmark script running 10 fixed scenarios (5 English, 3 Hindi, 2 Hinglish) and displaying a console comparison table.

6. **Unit Test Suite (`backend/tests/unit/`)**:
   - Added 60 comprehensive unit tests across 3 new test modules:
     - `test_pii_guard.py`: 32 tests covering single/multiple PII formats, benign criteria preservation, and bilingual notices.
     - `test_llm_client.py`: 8 tests covering config inheritance, daily call caps, structured JSON generation, parameter degradation, retry backoff, and truncation detection.
     - `test_profile_extractor.py`: 20 tests covering income arithmetic across scales and frequencies, multilingual inputs, sensitive field omission guards, PII pre-redaction, retry logic, and safe fallback.
   - All tests use 100% mocked LLM calls; zero live calls are made during pytest.

### Decisions
- Standardized on strict nullable JSON Schema for OpenAI/Groq structured outputs so missing demographic attributes evaluate to `null` instead of being invented.
- Placed all currency and frequency arithmetic into pure Python, ensuring the LLM is strictly an extractor and never does math.
- Added parameter degradation handling directly in `GroqClient` so variations across Groq-hosted models (such as models that reject `reasoning_effort` or `temperature`) fail open gracefully.

### Assumptions
- Input text is in English, Hindi, or Hinglish.
- Citizen profile state is ephemeral and passed in-memory per request.

### Open Issues / Next Steps
- Implement Part B: API endpoints (`/intake/extract`, `/match`, `/schemes`, `/schemes/{slug}/ask`, `/feedback`) and security middleware.

---

## Module: Backend API and LLM Integration (Part B - Endpoints & Security Middleware)

- **Status**: Completed
- **Date**: 2026-11-01

### What Was Built & Modified
1. **API Endpoints (`backend/app/api/v1/`)**:
   - `POST /api/v1/intake/extract`: Citizen message extraction endpoint. Orchestrates PII scrubbing, LLM extraction with structured JSON, profile merging, verified scheme evaluation in `RuleEngineService`, and `FollowupSelectorService` to select the highest-impact question across ambiguous candidate "maybe" schemes.
   - `POST /api/v1/match`: Deterministic scheme qualification engine. Pre-filters schemes by state/level, evaluates all criteria in pure Python `RuleEngineService`, and returns results grouped into `eligible`, `maybe`, and `not_eligible` with bilingual human-readable reasons and `last_verified` dates. LLM is never called.
   - `GET /api/v1/schemes`: Paginated listing of verified schemes with whitelisted state, level, and category filters. Excludes sample schemes unless `INCLUDE_SAMPLE_SCHEMES=True`.
   - `GET /api/v1/schemes/{slug}`: Single scheme detail endpoint returning verified data or 404 Not Found.
   - `POST /api/v1/schemes/{slug}/ask`: Grounded question answering endpoint delegating to stubbed `RAGService` that always returns `answerable=False`.
   - `POST /api/v1/feedback`: Anonymous helpfulness rating collection with zero personal identifiers.
   - Preserved `admin.py` without implementing routes (reserved for the admin module).

2. **Clean Layered Separation & Dependencies (`backend/app/api/deps.py`, `backend/app/services/`)**:
   - Created `IntakeService` and `MatchService` orchestrators keeping routers 100% free of business logic.
   - Implemented dependency injection in `app/api/deps.py` for all services, clients, and repositories.

3. **Defensive Security Middleware (`backend/app/core/middleware.py`, `backend/app/core/rate_limit.py`)**:
   - `CORSMiddleware`: Configured with exact origins from `ALLOWED_ORIGINS` without wildcards.
   - `SecurityHeadersMiddleware`: Injects `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, and `Cache-Control: no-store` on all API responses.
   - `RequestIdMiddleware`: Generates or propagates `X-Request-ID` across every request and response.
   - `RequestBodyLimitMiddleware`: Enforces 32 KB maximum payload ceiling on JSON routes, counting actual received bytes across both `Content-Length` and chunked transfer streams, returning 413 `PAYLOAD_TOO_LARGE`.
   - Per-IP Rate Limiting: Sliding 60-second window tracking requests per client IP, applying `RATE_LIMIT_PER_MINUTE` generally, and stricter limits (exactly `RATE_LIMIT_PER_MINUTE // 4`, lower, not higher) on `/intake/extract` and `/schemes/{slug}/ask`. Evicts expired entries older than the window to prevent unbounded memory growth.
   - Client IP Detection: In production (`ENV=production`) behind Render's reverse proxy, uses the trusted rightmost IP appended by the proxy in `X-Forwarded-For`; in development (`ENV=development`), uses the direct socket peer address (`request.client.host`). Forged client `X-Forwarded-For` headers cannot bypass limits.
   - `StructuredLoggingMiddleware`: Logs access events in structured JSON with duration, status, path, client IP, and request ID. Strictly omits request bodies, citizen messages, profile fields, or sensitive parameters.

4. **Centralized Error Contract (`backend/app/core/errors.py`)**:
   - Unified error format `{"error": {"code": "...", "message": "...", "request_id": "...", "details": ...}}`.
   - Global exception handlers: `AppException`, `RequestValidationError` (422), `StarletteHTTPException`, `PayloadTooLargeError` (413), `LLMError` (mapped to friendly 429 or 503), and unhandled `Exception` (500 without leaking stack traces).

5. **Test Suite & Verification (`backend/tests/api/test_api_v1.py`, `backend/tests/unit/test_schemas.py`)**:
   - 23 comprehensive API integration tests and unit tests verifying:
     - All endpoint success paths.
     - `extra="forbid"` on all request schemas (`IntakeExtractRequest`, `MatchRequest`, `SchemeAskRequest`, `FeedbackCreate`, `UserProfile`, etc.).
     - Oversize message (> 1000 chars) and payload size limit (fast-path Content-Length > 32 KB and chunked stream > 32 KB returning 413).
     - Malformed JSON handling.
     - LLM error mapping to 429 (`LLMRateLimitError`) and 503 (`LLMTimeoutError`, `LLMError`).
     - Exact quarter rate limits (`RATE_LIMIT_PER_MINUTE // 4`) on `/intake/extract` and `/schemes/{slug}/ask`.
     - Client IP determination: socket address in dev vs. Render proxy rightmost XFF IP in prod, with tests proving forged XFF cannot bypass rate limiting.
     - Eviction of expired rate limiter entries older than 60s.
     - Documentation routes (`/docs`, `/redoc`, `/openapi.json`) return 404 when `ENABLE_DOCS=False` and 200 when `ENABLE_DOCS=True`.
     - CORS rejection for disallowed origins and acceptance for allowed origins.
     - Defensive security headers (`nosniff`, `no-referrer`, `no-store`, `X-Request-ID`).
     - Structured access logs contain zero citizen message text or profile data.

### Follow-up Checks & Security Hardening
1. **Rate Limits**:
   - Base limit: `RATE_LIMIT_PER_MINUTE` (default 60 rpm).
   - Stricter routes (`/intake/extract` and `/schemes/{slug}/ask`): Exactly `RATE_LIMIT_PER_MINUTE // 4` (e.g. 15 rpm when base is 60). Strictly lower, never higher.
2. **Client IP Determination**:
   - In development: Sourced from `request.client.host` (socket peer address). Forged `X-Forwarded-For` headers are ignored.
   - In production (`ENV=production` behind Render): Sourced from the rightmost entry in `X-Forwarded-For` (`ips[-1].strip()`), which is the IP appended by Render's trusted proxy. Client-prepended spoofed IPs are ignored.
3. **Body Size Limiting**:
   - Lowered to 32 KB (32,768 bytes) across all JSON routes.
   - ASGI middleware checks `Content-Length` on fast-path and intercepts `receive()` to count actual streamed bytes, catching chunked bodies without `Content-Length`.
4. **Rate Limiter Memory Eviction**:
   - `cleanup_expired(now)` purges keys whose timestamps are entirely older than the 60-second window, running on check and periodic maintenance to prevent unbounded memory growth.
5. **Documentation Toggle & Schema Invariants**:
   - `/docs`, `/redoc`, and `/openapi.json` return 404 when `ENABLE_DOCS=False`, and 200 when `ENABLE_DOCS=True`.
   - Every request model explicitly configures `model_config = ConfigDict(extra="forbid")`.

### Decisions
- Standardized error format with `request_id` attached automatically from `request.state.request_id` across all HTTP handlers.
- Decoupled router layer completely from business logic by introducing `IntakeService` and `MatchService`.
- Excluded wildcards in CORS configuration to prevent unauthorized cross-origin requests.

### Assumptions
- Frontend client communicates exclusively over JSON with `extra="forbid"`.
- Scheme guidelines Q&A remains stubbed (`answerable=False`) until the RAG vector search module is built.

### Open Issues / Next Steps
- Implement Admin authentication, dashboard, and scheme verification workflows.


---

## Module: Frontend Features (Part A - API Client, Browse Schemes & Scheme Detail)

- **Status**: Completed
- **Date**: 2026-11-01

### What Was Built & Modified
1. **Centralized API Client (`frontend/src/lib/api.js`)**:
   - Single source of truth reading base URL exclusively from `VITE_API_BASE_URL` and appending `/api/v1`.
   - Injects current active UI language (`i18n.language`) when not explicitly overridden.
   - Built 6000ms watchdog timer firing `onSlow` callback to alert users of Render cold starts (*"Waking up the server, this can take up to a minute"*).
   - Structured error handling via `ApiError` class with HTTP status, code, details, and request ID. Friendly fallbacks for 404, 413, 429 (*"Too many requests, please wait a minute"*), 503, and network disconnects.
   - Exact query parameter matching: `getSchemes` constructs `skip`, `limit`, `state` (lowercased), `level`, and `category`.
   - Comprehensive test suite in `frontend/src/lib/api.test.js` (10 tests passing).

2. **Official Government Domain Validator (`frontend/src/lib/urlHelper.js` & `GovLink.jsx`)**:
   - `isOfficialGovDomain(url)`: Strictly validates that the host ends in `.gov.in` or `.nic.in` (case-insensitive, ignoring trailing dots).
   - Rejects URLs containing user credentials (`user:pass@host`), non-http/https protocols, and lookalikes (`evil-gov.in.com`, `gov.in.evil.com`, `fakegov.in`).
   - `GovLink` component: Safely opens in new tab with `rel="noopener noreferrer"` for allowlisted domains; renders safe plain text otherwise.
   - Unit tests in `frontend/src/lib/urlHelper.test.js` (7 tests passing).

3. **Browse Schemes Page (`/schemes`)**:
   - `BrowseSchemesPage.jsx`: Connects to real `GET /api/v1/schemes` with pagination and filters.
   - `SchemeCard.jsx`: Displays localized name, level badge, state badge, sample data badge (when `is_sample: true`), category tags, benefit summary, verified date, and view details button.
   - `SchemeFilters.jsx`: Filter controls for administrative level (`central`, `state`), all 36 Indian states & UTs, and category tag search.
   - State handling: 4-card loading skeletons, `ErrorState` with retry, `EmptyState` explaining verified schemes review process, and slow server notice.

4. **Scheme Detail Page (`/schemes/:slug`)**:
   - `SchemeDetailPage.jsx` & `SchemeDetail.jsx`:
     - Displays mandatory indicative disclaimer strip: *"Indicative information. The concerned department makes the final decision."*
     - Localized scheme title, level badge, state badge, last verified date, and administrator verification name.
     - Benefit summary callout card.
     - Human-readable eligibility criteria list (evaluating `all_of` and `any_of`).
     - Required documents checklist with interactive checkboxes whose tick state is preserved strictly in React memory (`useState`), never persisted to storage.
     - Numbered application steps (`application_steps`).
     - Official application portal and source links secured through `GovLink`.
     - Print-friendly layout with `@media print` styles and a *"Print this page / PDF"* button (`window.print()`, avoiding jsPDF).
     - 404 Not Found state with clear navigation back to the directory.

5. **"Ask About This Scheme" Box (`frontend/src/features/scheme/components/SchemeAskBox.jsx`)**:
   - Text input capped at 500 characters with live character counter.
   - Calls `POST /api/v1/schemes/{slug}/ask` with question and active locale.
   - Displays official guideline answer with citations when `answerable: true`.
   - Displays friendly notice when `answerable: false` indicating information is not found in retrieved official text.
   - Handles rate limits (429) with advisory notice.

6. **React Error Boundary & Code Splitting (`frontend/src/app/App.jsx`)**:
   - Created `ErrorBoundary.jsx` catching unhandled render errors with accessible fallback and reload options.
   - Converted all routes to `React.lazy` with `<Suspense>` skeleton fallbacks.
   - Registered `/schemes/:slug` route for `SchemeDetailPage`.

7. **Internationalization (`frontend/src/i18n/en.json` & `hi.json`)**:
   - Added full bilingual keys across `schemes`, `schemeDetail`, `ask`, `apiErrors`, and `criteria` with 100% key parity verified by `i18n.test.js`.

8. **Environment Configuration**:
   - Rewrote `frontend/.env.example` to contain only `VITE_API_BASE_URL` with a one-line comment and value `http://127.0.0.1:8000`.

### Decisions
- Separated `urlHelper.js` (pure JS domain validator) from `GovLink.jsx` (React UI component) to keep JS utilities purely functional without JSX syntax in `.js` files.
- Kept document checklist tick state strictly in local React `useState` to adhere to zero-PII and zero-persistence principles.
- Filtered state parameter to lowercase and verified exact parameter names `skip`, `limit`, `state`, `level`, and `category` as defined in `schemes.py`.

### Assumptions
- Indian states dropdown values match backend `IndianState` enum strings.
- Frontend test runner expects `@testing-library/react` and `@testing-library/jest-dom` installed in `frontend/node_modules`.

### Hindi Copy Review Notes (For User Verification)
- "संकेतात्मक जानकारी। अंतिम निर्णय संबंधित विभाग करता है।" (Indicative information. The concerned department makes the final decision.)
- "सर्वर सक्रिय हो रहा है, इसमें एक मिनट तक का समय लग सकता है" (Waking up the server, this can take up to a minute)
- "सत्यापित योजनाएं यहाँ प्रदर्शित होंगी" (Verified schemes will appear here)
- "उद्धृत आधिकारिक संदर्भ" (Retrieved official citations)


---

## Module: Frontend Features (Part B - Check Eligibility Intake, Real-Time Details Panel & Results Page)

- **Status**: Completed
- **Date**: 2026-11-01

### What Was Built & Modified
1. **In-Memory Eligibility Context (`frontend/src/context/EligibilityContext.jsx`)**:
   - Central ephemeral state management provider mounted above `BrowserRouter` in `App.jsx` so state survives navigation between `/check-eligibility` and `/check-eligibility/results`.
   - **Zero-Persistence Guarantee**: Strictly in React memory. No `localStorage`, `sessionStorage`, cookies, or URL search parameters touch citizen data. Page refresh resets all profile data.
   - **AbortController & Request ID Tracking**: "Clear my details" instantly aborts active HTTP requests, increments a monotonic request counter, and discards delayed responses that arrive after reset or component unmount.
   - **Quick-Reply Chip Precedence**: Clicking an enumerated chip immediately updates the panel field in state; if the LLM extraction from `POST /intake/extract` conflicts with the chip, the chip's value wins.
   - **Stale Results Invalidation**: Modifying any field in the profile automatically resets `matchResults` to `null` to prevent the browser Back button from showing stale evaluations.
   - Focus management via `focusedField` to automatically scroll and focus specific fields when requested from the Results page.

2. **Consent Gate (`frontend/src/features/intake/components/ConsentGate.jsx`)**:
   - Informational consent card shown before any citizen input can be entered.
   - Explains what criteria are asked, that details are used only to evaluate eligibility and are never stored, that text is processed by an AI extraction service, and explicitly instructs citizens never to provide Aadhaar, PAN, phone, email, address, or bank details.
   - Explains that sensitive fields (social category, disability status) are strictly optional and support "Prefer not to say".
   - Citizen must click *"I understand, continue"* (`"मैं समझ गया/गई, आगे बढ़ें"`) to access the chat and details panel.
   - Unit tests in `frontend/src/features/intake/components/ConsentGate.test.jsx`.

3. **Conversational Intake Chat (`frontend/src/features/intake/components/IntakeChat.jsx`)**:
   - Real-time conversation calling `POST /api/v1/intake/extract` with current profile and active UI language.
   - 1000-character input ceiling with live countdown and a privacy reminder badge (*"Never type Aadhaar, phone, or bank details"*).
   - Screen reader friendly `role="log"` container with `aria-live="polite"`.
   - Dynamic quick-reply chips for missing fields with fixed options (`gender`, `residence_type`, `marital_status`, `occupation`, `education_level`, `social_category`, `disability_status`).
   - Prevents double submissions by disabling the send button and quick-reply chips while requests are in flight.
   - Surfaces PII warnings from the backend API if sensitive identifiers are typed.
   - Friendly Render cold start alert (*"Waking up the server, this can take up to a minute"*) via 6-second watchdog timer, plus network/rate-limit error retry handlers.

4. **"Your Details" Side Panel (`frontend/src/features/intake/components/YourDetailsPanel.jsx`)**:
   - Serves as the source of truth for citizen criteria, synchronizing bidirectional updates with the chat extractor.
   - Form controls for all fields in `UserProfile`:
     - Number inputs for `age` and `annual_income` (with live INR currency formatting preview).
     - Selects matching `backend/app/schemas/enums.py` exactly (`gender`, `occupation`, `social_category`, `education_level`, `residence_type`, `marital_status`, `disability_status`, `is_student`, and all 36 Indian states/UTs).
     - Explicit support for "Not given" (clears/omits field) and "Prefer not to say" (`prefer_not_to_say` matching schema).
   - Smooth programmatic focus and scrolling into view when directed from a missing criterion callout.
   - *"Clear my details"* button with immediate reset and in-flight abort.
   - *"See my matching schemes"* button calling `POST /api/v1/match`, enabled as soon as at least one profile field is entered.

5. **Results Page (`frontend/src/pages/ResultsPage.jsx` & Components)**:
   - **Empty State Privacy Guard**: If visited directly or after page refresh without a profile in memory, renders a clear explanation and *"Start Eligibility Check"* button.
   - **Mandatory Disclaimer Strip**: *"Indicative result. The concerned department makes the final decision."* (`role="note"`).
   - **Keyboard-Navigable Results Tabs (`ResultsTabs.jsx`)**: Filter by status (*Eligible*, *Maybe eligible*, *Not eligible*) with live count badges and `ArrowLeft`, `ArrowRight`, `Home`, and `End` keyboard navigation.
   - **Clean Scheme Cards (`ResultSchemeCard.jsx`)**:
     - Localized name, benefit summary, level and state badges, sample-data badge, and last verified date.
     - Reason parsing (`parseReasonSymbol`): Strips duplicate trailing marks (`✓`, `✕`, `?`) from backend rule engine output, rendering distinct, accessible icon badges and clean text.
     - *"Add this detail"* button on Maybe eligible cards: identifies missing criteria and redirects directly to `/check-eligibility`, focusing the relevant panel field.
   - **Category Tag Filter**: Dropdown dynamically populated from available category tags to filter schemes within the active status tab.
   - **Print & PDF Support**: Dedicated *"Print Results / PDF"* button built using `window.print()` with `@media print` stylesheets that hide navigation, chat, and utility controls, excluding personal identifiers.

6. **ESLint & Code Standards**:
   - Added `'no-console': ['error', { allow: ['warn', 'error'] }]` to `frontend/eslint.config.js` to ensure citizen data and API responses are never logged.
   - Clean ESLint run: 0 errors, 0 warnings across the entire frontend.
   - All 75 tests passing across 12 test files (`npm test`).

### Decisions
- Context placed above `BrowserRouter` in `App.jsx` to maintain ephemeral state across route changes between `/check-eligibility` and `/check-eligibility/results` without writing to browser storage.
- Used an AbortController with monotonic request ID sequencing to ensure late-arriving responses after "Clear my details" or component unmount are completely discarded.
- Stripped trailing checkmarks and crossmarks from backend rule engine strings before rendering UI icon badges to prevent duplicate symbols (e.g. `✓ Age 18 to 30 ✓`).
- Avoided jsPDF in favor of native `window.print()` to maintain native browser Devanagari text shaping and ligatures.

### Assumptions
- Backend `/api/v1/intake/extract` returns `profile_updates`, `missing_fields`, `next_question`, and optional `pii_notice`.
- Backend `/api/v1/match` returns `eligible`, `maybe`, and `not_eligible` scheme arrays.

### Hindi Copy Review Notes (For User Verification)
- "संकेतात्मक परिणाम। अंतिम निर्णय संबंधित विभाग करता है।" (Indicative result. The concerned department makes the final decision.)
- "मेरा विवरण साफ़ करें" (Clear my details)
- "मेरी पात्र योजनाएं देखें" (See my matching schemes)
- "+ यह विवरण जोड़ें" (+ Add this detail)
- "स्मृति में कोई प्रोफ़ाइल नहीं है" (No profile in memory)

---

## Module: Admin Panel and Authentication (Backend - Part A)

- **Status**: Completed
- **Date**: 2026-11-01

### What Was Built
1. **Argon2id Password Authentication & Side-Channel Defense (`app/core/auth.py`)**:
   - Integrated `argon2-cffi` using `argon2.PasswordHasher` directly (defaulting to Argon2id) without legacy `passlib` wrappers.
   - Constant-time side-channel protection with precomputed dummy Argon2id hash verification for unregistered email accounts to prevent user enumeration via timing differentials.
   - Generic authentication error message strictly identical for unknown email and wrong password.
   - 15-minute account lockout triggered after 5 consecutive failed login attempts.
   - Heavy rate-limiting (5 requests/minute per client IP) on `POST /api/v1/admin/auth/login`.

2. **Fixed Server-Side HS256 JWT Token Management (`app/core/auth.py`)**:
   - Fixed HS256 algorithm enforcement on server side (algorithm header is strictly ignored and forced to HS256).
   - Generated tokens carry mandatory claims: `sub`, `role`, `iat`, `exp`, `iss`, and `jti`.
   - Token lifespan capped at a maximum of 30 minutes (between 15 and 30 minutes).
   - Strict token parsing via `Authorization: Bearer <token>` header exclusively; zero use of cookies.
   - Rejection with 401 Unauthorized on missing, malformed, expired, tampered, or `alg=none` tokens.

3. **Role-Based Authorization & Dependency Injection (`app/api/deps.py`)**:
   - `get_current_admin`: Verifies bearer token, checks account lockout, and loads admin entity.
   - `require_admin_role`: Role guard enforcing full `admin` permissions (rejects `reviewer` with 403 Forbidden).
   - Role boundaries:
     - `admin`: Full administrative access (can manage, verify, reject, archive, and read audit logs).
     - `reviewer`: Limited access (can list, view, create, edit, verify, reject, upload PDFs, and trigger ingestion, but strictly forbidden from archiving schemes or viewing audit logs).

4. **Administrative Routes (`app/api/v1/admin.py`)**:
   - `POST /api/v1/admin/auth/login`: Argon2id verification with rate limiting and lockout.
   - `GET /api/v1/admin/schemes`: Paginated list of schemes with status filtering and search.
   - `GET /api/v1/admin/schemes/{identifier}`: Scheme lookup by slug or document ID.
   - `POST /api/v1/admin/schemes`: Create scheme (always saved as `needs_review`, criteria validated against `EligibilityCriteria`, `source_url` and `apply_url` strictly require HTTPS on `.gov.in` or `.nic.in` domains).
   - `PUT` / `PATCH /api/v1/admin/schemes/{identifier}`: Edit scheme (any edit to a `verified` scheme resets it to `needs_review`).
   - `POST /api/v1/admin/schemes/{identifier}/verify`: Verify scheme (requires valid `source_url` and `last_verified` date; records `verified_by` and `verified_at`).
   - `POST /api/v1/admin/schemes/{identifier}/reject`: Reject scheme (requires non-empty explanation reason; reverts status to `draft`).
   - `POST /api/v1/admin/schemes/{identifier}/archive`: Archive scheme (restricted to `admin` role).
   - `POST /api/v1/admin/schemes/upload-pdf`: Upload PDF and compute SHA-256 source hash.
   - `POST /api/v1/admin/schemes/{identifier}/ingest`: Trigger ingestion pipeline for a scheme.
   - `GET /api/v1/admin/audit-logs`: Paginated read of immutable audit trail (restricted to `admin` role).

5. **Immutable Audit Logging (`app/repositories/audit_repo.py`)**:
   - Append-only audit trail logging for all mutations with `actor`, `action`, `target`, and `diff`.
   - Invariant: Zero logging of passwords, password hashes, tokens, or `JWT_SECRET`.

6. **Interactive Initial Admin Seeding Script (`scripts/seed_admin.py`)**:
   - Command-line utility using `getpass` to prompt for email and password at run time.
   - Enforces minimum 14-character password length.
   - Hashes password using Argon2id directly.
   - Refuses to execute if any administrator account already exists.
   - Zero hardcoded default credentials anywhere in codebase.

7. **Test Coverage (`tests/api/test_admin.py` & `tests/unit/test_seed_admin.py`)**:
   - 16 new automated test cases covering login, lockout, rate limiting, token tampering/expiry/alg=none, reviewer vs admin role separation, verified scheme resetting on edit, public API visibility invariants, and seeding script guards.
   - Total backend test suite: 203 passing tests.

