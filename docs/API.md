# API Documentation Overview

All API endpoints are prefixed with `/api/v1` (configurable via `API_PREFIX`).

## Error Format Contract
All error responses adhere to a consistent error envelope:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable description",
    "details": null
  }
}
```

## Endpoints Summary

- `GET /health` or `GET /api/v1/health`: Container health check and runtime environment status.
- `POST /api/v1/intake`: Extract demographic criteria from conversational input.
- `POST /api/v1/match`: Deterministic rule-based qualification check.
- `GET /api/v1/schemes`: Browse verified schemes.
- `GET /api/v1/schemes/{slug}`: Retrieve specific scheme details, citations, and last-verified date.
- `POST /api/v1/qa`: Ask scheme-grounded questions with citations.
- `POST /api/v1/feedback`: Submit user feedback.
- `POST /api/v1/admin/login`: Admin authentication.

