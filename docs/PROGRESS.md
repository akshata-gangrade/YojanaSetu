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






