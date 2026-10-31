"""PII detector and filter to enforce zero-persistence and data redaction."""

import re

# Patterns matching sensitive identifiers (Aadhaar, PAN, phone numbers, email, bank acc)
AADHAAR_PATTERN = re.compile(r"\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b")
PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
PHONE_PATTERN = re.compile(r"\b(?:\+91|0)?[6-9]\d{9}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


class PIIGuardService:
    """Detects and strips accidental personal identifiers from incoming text."""

    @classmethod
    def sanitize(cls, text: str) -> str:
        """Replace detected PII with neutral redaction tokens."""
        text = AADHAAR_PATTERN.sub("[REDACTED_AADHAAR]", text)
        text = PAN_PATTERN.sub("[REDACTED_PAN]", text)
        text = PHONE_PATTERN.sub("[REDACTED_PHONE]", text)
        text = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
        return text
