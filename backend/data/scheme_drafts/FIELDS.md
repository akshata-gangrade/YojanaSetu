# Scheme Specification & Field Reference

This document provides a field-by-field reference for scheme definitions imported into YojanaSetu, extracted directly from the canonical backend Pydantic models (`app.schemas.scheme`, `app.schemas.criteria`, and `app.schemas.enums`).

---

## 1. Top-Level Scheme Fields (`SchemeCreate`)

| Field Name | Type | Required | Constraints / Validation | Description |
|---|---|---|---|---|
| `slug` | `string` | **Yes** | Min 3, max 120 chars; regex `^[a-z0-9]+(?:-[a-z0-9]+)*$` | Unique URL-friendly slug identifier. |
| `name` | `string` | **Yes** | Min 2, max 255 chars | Official scheme title in English. |
| `name_hi` | `string` | **Yes** | Min 2, max 255 chars | Official scheme title in Hindi (Devanagari). |
| `level` | `string` (enum) | **Yes** | Must be `"central"` or `"state"` | Administrative level of the government scheme. |
| `state` | `string \| null` | Conditional | Null for `"central"` schemes; non-empty string matching an allowed Indian state for `"state"` schemes | State/UT responsible for the scheme. |
| `category_tags` | `list[string]` | No (default `[]`) | Array of categorization tags | Semantic tags (e.g., `["agriculture", "pension"]`). |
| `benefit_summary` | `string` | **Yes** | Min 10, max 2000 chars | Concise summary of entitlements/assistance in English. |
| `benefit_summary_hi` | `string` | **Yes** | Min 10, max 2000 chars | Summary of entitlements in Hindi. |
| `eligibility_criteria` | `object` | No (default empty) | Must match `EligibilityCriteria` structure | Deterministic evaluation criteria tree (`all_of`, `any_of`, `none_of`). |
| `required_documents` | `list[string]` | No (default `[]`) | Array of strings | Documentation required from the citizen to apply. |
| `application_steps` | `list[string]` | No (default `[]`) | Array of strings | Step-by-step instructions explaining how to apply. |
| `apply_url` | `string` | **Yes** | Must start with `http://` or `https://` | Link to official government application portal. |
| `source_url` | `string` | **Yes** | Must start with `http://` or `https://` | Link to official ministry guidelines/gazette document. |
| `source_hash` | `string` | **Yes** | Min length 16 chars (standard 64-char SHA-256 hex string) | Cryptographic SHA-256 hash of the official source document. |
| `status` | `string` (enum) | No (default `"draft"`) | Must be one of `SchemeStatus` enum values | Lifecycle status. Imports are always assigned `"needs_review"`. |
| `verified_by` | `string \| null` | No (default `null`) | Admin email or identifier string | Recording reviewer identity upon verification. |
| `verified_at` | `string \| null` | No (default `null`) | ISO 8601 UTC datetime string | Timestamp of verification. |
| `last_verified` | `string` | **Yes** | ISO 8601 UTC datetime string | Timestamp indicating when source validity was last confirmed. |
| `is_sample` | `boolean` | No (default `false`) | `true` or `false` | Marks fictional test schemes excluded from production. |

---

## 2. Eligibility Criteria Structure (`EligibilityCriteria`)

The `eligibility_criteria` object deterministically specifies evaluation rules:

```json
{
  "all_of": [ ...list of Criterion objects... ],
  "any_of": [ ...list of Criterion objects... ],
  "as_on": "2026-11-01"
}
```

- `all_of`: Every criterion in this list must evaluate to `True`.
- `any_of`: At least one criterion in this list must evaluate to `True` (if non-empty).
- `as_on`: Optional cut-off date string (`YYYY-MM-DD`) for age and criteria evaluation.
- Note: Negative conditions are expressed inside `all_of` using operator `"not_in"`.

### Criterion Object

| Field | Type | Required | Description |
|---|---|---|---|
| `field` | `string` (enum) | **Yes** | Profile field evaluated (see `CriterionField` enum below). |
| `op` | `string` (enum) | **Yes** | Deterministic comparison operator (see `CriterionOperator` enum below). |
| `value` | `any` | **Yes** | Threshold or target value (`int`, `float`, `string`, `list[int]`, `list[string]`, `bool`). |

---

## 3. Allowed Enumeration Values (`app.schemas.enums`)

### `SchemeLevel`
- `"central"`: Central government scheme.
- `"state"`: State government scheme (requires `state` to be specified).

### `SchemeStatus`
- `"draft"`: Incomplete or rejected scheme.
- `"needs_review"`: Awaiting administrative review against official source.
- `"verified"`: Authenticated and eligible to appear in citizen queries.
- `"archived"`: Retired or deprecated scheme.

### `CriterionField`
- `"age"`: Citizen age (numeric integer, typically evaluated with `gte`, `lte`, `between`).
- `"gender"`: Citizen gender.
- `"state"`: Indian State / Union Territory of residence.
- `"annual_income"`: Total household annual income in INR (numeric float/int).
- `"social_category"`: Affirmative action / caste classification category.
- `"occupation"`: Primary economic occupation of the citizen.
- `"education_level"`: Highest completed formal education tier.
- `"residence_type"`: Locality classification (`rural` vs `urban`).
- `"marital_status"`: Marital status.
- `"disability_status"`: Disability category.
- `"is_student"`: Whether citizen is actively enrolled as a student (`true` / `false`).

### `CriterionOperator`
- `"eq"`: Exact equality comparison.
- `"in"`: Value must be a member of the provided array.
- `"not_in"`: Value must NOT be a member of the provided array.
- `"gte"`: Greater than or equal to numeric threshold.
- `"lte"`: Less than or equal to numeric threshold.
- `"between"`: Value falls inclusively within `[min, max]` two-element array.

### `Gender`
- `"female"`
- `"male"`
- `"transgender"`
- `"other"`
- `"prefer_not_to_say"`

### `SocialCategory`
- `"general"`
- `"obc"`
- `"sc"`
- `"st"`
- `"ebc"`
- `"prefer_not_to_say"`

### `ResidenceType`
- `"rural"`
- `"urban"`
- `"prefer_not_to_say"`

### `MaritalStatus`
- `"single"`
- `"married"`
- `"widowed"`
- `"divorced"`
- `"separated"`
- `"prefer_not_to_say"`

### `DisabilityStatus`
- `"none"`
- `"locomotor"`
- `"visual"`
- `"hearing"`
- `"speech_and_language"`
- `"intellectual"`
- `"mental_illness"`
- `"multiple"`
- `"other"`
- `"prefer_not_to_say"`

### `Occupation`
- `"farmer"`
- `"artisan"`
- `"student"`
- `"salaried"`
- `"self_employed"`
- `"daily_wage"`
- `"unemployed"`
- `"homemaker"`
- `"retired"`
- `"other"`
- `"prefer_not_to_say"`

### `EducationLevel`
- `"none"`
- `"primary"`
- `"secondary"`
- `"higher_secondary"`
- `"diploma"`
- `"graduate"`
- `"post_graduate"`
- `"doctorate"`
- `"prefer_not_to_say"`

### `IndianState`
- `"andhra_pradesh"`
- `"arunachal_pradesh"`
- `"assam"`
- `"bihar"`
- `"chhattisgarh"`
- `"goa"`
- `"gujarat"`
- `"haryana"`
- `"himachal_pradesh"`
- `"jharkhand"`
- `"karnataka"`
- `"kerala"`
- `"madhya_pradesh"`
- `"maharashtra"`
- `"manipur"`
- `"meghalaya"`
- `"mizoram"`
- `"nagaland"`
- `"odisha"`
- `"punjab"`
- `"rajasthan"`
- `"sikkim"`
- `"tamil_nadu"`
- `"telangana"`
- `"tripura"`
- `"uttar_pradesh"`
- `"uttarakhand"`
- `"west_bengal"`
- `"andaman_and_nicobar"`
- `"chandigarh"`
- `"dadra_and_nagar_haveli_and_daman_and_diu"`
- `"delhi"`
- `"jammu_and_kashmir"`
- `"ladakh"`
- `"lakshadweep"`
- `"puducherry"`
- `"prefer_not_to_say"`
