"""PII detector and filter to enforce zero-persistence and data redaction."""

from dataclasses import dataclass
import re

# Aadhaar: 12 digits starting with 2-9, with spaces/hyphens (4-4-4 format) or continuous 12 digits
AADHAAR_PATTERN = re.compile(r"\b[2-9]\d{3}[\s-]\d{4}[\s-]\d{4}\b|\b[2-9]\d{11}\b")

# PAN: 5 letters, 4 digits, 1 letter (case-insensitive)
PAN_PATTERN = re.compile(r"\b[A-Za-z]{5}[0-9]{4}[A-Za-z]\b")

# Phone: Indian 10-digit numbers starting with 6-9, optional +91 or 0 prefix, optional separator
PHONE_PATTERN = re.compile(r"(?:\+91[\s-]?|0)?[6-9]\d{4}[\s-]?\d{5}\b|\b[6-9]\d{9}\b")

# Email: standard email address format
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")


@dataclass(frozen=True)
class PIIGuardResult:
    """Outcome of PII scanning and redaction.

    Attributes:
        sanitized_text: Input text with all detected personal identifiers replaced.
        has_pii: True if any PII was detected and redacted.
        detected_types: List of detected PII categories ('aadhaar', 'pan', 'phone', 'email').
        notice: Informational notice for the user explaining that PII is neither needed nor stored.
    """

    sanitized_text: str
    has_pii: bool
    detected_types: list[str]
    notice: str | None = None


class PIIGuardService:
    """Detects and strips accidental personal identifiers from incoming text."""

    REDACTION_TOKENS = {
        "aadhaar": "[REDACTED_AADHAAR]",
        "pan": "[REDACTED_PAN]",
        "phone": "[REDACTED_PHONE]",
        "email": "[REDACTED_EMAIL]",
    }

    @classmethod
    def scan_and_redact(cls, text: str, language: str = "en") -> PIIGuardResult:
        """Scan text for PII patterns, redact them, and generate a user advisory notice.

        Args:
            text: Raw citizen input message.
            language: Requested language for the advisory notice ('en' or 'hi').

        Returns:
            PIIGuardResult containing sanitized text, detected types, and advisory notice.
        """
        if not text:
            return PIIGuardResult(
                sanitized_text="",
                has_pii=False,
                detected_types=[],
                notice=None,
            )

        detected_types: list[str] = []
        sanitized = text

        # Check Phone with explicit prefix (+91 or 0) or standard phone first if Aadhaar might clash
        # Check Aadhaar
        if AADHAAR_PATTERN.search(sanitized):
            detected_types.append("aadhaar")
            sanitized = AADHAAR_PATTERN.sub(cls.REDACTION_TOKENS["aadhaar"], sanitized)

        # Check PAN
        if PAN_PATTERN.search(sanitized):
            detected_types.append("pan")
            sanitized = PAN_PATTERN.sub(cls.REDACTION_TOKENS["pan"], sanitized)

        # Check Phone
        if PHONE_PATTERN.search(sanitized):
            detected_types.append("phone")
            sanitized = PHONE_PATTERN.sub(cls.REDACTION_TOKENS["phone"], sanitized)

        # Check Email
        if EMAIL_PATTERN.search(sanitized):
            detected_types.append("email")
            sanitized = EMAIL_PATTERN.sub(cls.REDACTION_TOKENS["email"], sanitized)

        has_pii = len(detected_types) > 0
        notice = cls._generate_notice(detected_types, language) if has_pii else None

        return PIIGuardResult(
            sanitized_text=sanitized,
            has_pii=has_pii,
            detected_types=detected_types,
            notice=notice,
        )

    @classmethod
    def sanitize(cls, text: str) -> str:
        """Replace detected PII with neutral redaction tokens.

        Maintains backwards compatibility with existing callers.
        """
        return cls.scan_and_redact(text).sanitized_text

    @classmethod
    def _generate_notice(cls, detected_types: list[str], language: str) -> str:
        """Generate bilingual advisory message explaining PII was removed."""
        labels_en = {
            "aadhaar": "Aadhaar number",
            "pan": "PAN card number",
            "phone": "phone number",
            "email": "email address",
        }
        labels_hi = {
            "aadhaar": "आधार संख्या",
            "pan": "पैन कार्ड संख्या",
            "phone": "फ़ोन नंबर",
            "email": "ईमेल पता",
        }

        if language == "hi":
            items = ", ".join(labels_hi.get(t, t) for t in detected_types)
            return (
                f"सूचना: व्यक्तिगत विवरण ({items}) हटा दिए गए हैं। "
                "योजनासेतु को आधार, पैन, फ़ोन नंबर या ईमेल पते की आवश्यकता नहीं है, "
                "और हम इन्हें कभी संगृहीत नहीं करते।"
            )

        items = ", ".join(labels_en.get(t, t) for t in detected_types)
        return (
            f"Notice: Sensitive personal details ({items}) were detected and removed. "
            "YojanaSetu does not need or store Aadhaar, PAN, phone numbers, or email addresses."
        )
