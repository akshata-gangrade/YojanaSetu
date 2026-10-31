"""Unit tests for PIIGuardService verifying pattern detection and zero-PII redaction."""

import pytest

from app.services.pii_guard import PIIGuardService


class TestPIIGuardAadhaar:
    """Tests for detecting and redacting Aadhaar numbers."""

    @pytest.mark.parametrize(
        "raw_text,expected_token",
        [
            ("My aadhaar is 2345 6789 0123 please check", "[REDACTED_AADHAAR]"),
            ("Aadhaar card: 9876-5432-1098.", "[REDACTED_AADHAAR]"),
            ("Number is 555566667777 for record", "[REDACTED_AADHAAR]"),
            ("UID: 4321 8765 4321", "[REDACTED_AADHAAR]"),
            ("mera aadhaar 3214-5678-9012 hai", "[REDACTED_AADHAAR]"),
        ],
    )
    def test_aadhaar_redacted_across_formats(self, raw_text: str, expected_token: str):
        result = PIIGuardService.scan_and_redact(raw_text)
        assert result.has_pii is True
        assert "aadhaar" in result.detected_types
        assert expected_token in result.sanitized_text
        assert (
            "2345" not in result.sanitized_text
            or "9876-5432" not in result.sanitized_text
        )

    def test_numbers_starting_with_0_or_1_not_aadhaar(self):
        # Indian Aadhaar numbers never start with 0 or 1
        text = "Order id 012345678901 or 123456789012"
        result = PIIGuardService.scan_and_redact(text)
        assert "aadhaar" not in result.detected_types


class TestPIIGuardPAN:
    """Tests for detecting and redacting PAN card identifiers."""

    @pytest.mark.parametrize(
        "raw_text",
        [
            "My PAN is ABCDE1234F.",
            "pan number: xyzpk9876m",
            "Here is my PAN: BZRPK1234A please register",
            "Mera PAN card abCde9999Z hai",
        ],
    )
    def test_pan_redacted_case_insensitively(self, raw_text: str):
        result = PIIGuardService.scan_and_redact(raw_text)
        assert result.has_pii is True
        assert "pan" in result.detected_types
        assert "[REDACTED_PAN]" in result.sanitized_text


class TestPIIGuardPhone:
    """Tests for detecting and redacting Indian phone numbers."""

    @pytest.mark.parametrize(
        "raw_text",
        [
            "Call me at 9876543210 tomorrow",
            "Phone: +91 98765 43210",
            "Mobile: +91-8765432109",
            "Contact: +91 9123456789",
            "Call 09876543210 for details",
            "Number: 7012345678",
            "Contact 6398765432",
        ],
    )
    def test_phone_numbers_redacted(self, raw_text: str):
        result = PIIGuardService.scan_and_redact(raw_text)
        assert result.has_pii is True
        assert "phone" in result.detected_types
        assert "[REDACTED_PHONE]" in result.sanitized_text


class TestPIIGuardEmail:
    """Tests for detecting and redacting email addresses."""

    @pytest.mark.parametrize(
        "raw_text",
        [
            "Email me at citizen.help@example.com",
            "Send to user+tag@gov.in please",
            "Contact: RAMESH.KUMAR@GMAIL.COM",
            "info at test.name@sub.domain.co.in",
        ],
    )
    def test_email_addresses_redacted(self, raw_text: str):
        result = PIIGuardService.scan_and_redact(raw_text)
        assert result.has_pii is True
        assert "email" in result.detected_types
        assert "[REDACTED_EMAIL]" in result.sanitized_text


class TestPIIGuardBenignNumbers:
    """Critical tests verifying legitimate scheme criteria numbers are NEVER redacted."""

    @pytest.mark.parametrize(
        "safe_text",
        [
            "I am 24 years old and earn 250000 per year",
            "My annual income is 50000 rupees and I have 2 acres of land",
            "I live in pincode 110001 with 4 family members",
            "Born in year 1998, farming on 1.5 hectares",
            "Earning 15000 per month as a daily wage laborer",
            "Income is 1200000 and age is 62",
            "I completed 12th class in 2021",
        ],
    )
    def test_benign_criteria_numbers_preserved(self, safe_text: str):
        result = PIIGuardService.scan_and_redact(safe_text)
        assert result.has_pii is False
        assert result.detected_types == []
        assert result.notice is None
        assert result.sanitized_text == safe_text


class TestPIIGuardMultipleAndNotices:
    """Tests for combined PII detections and bilingual notices."""

    def test_multiple_pii_detected_together(self):
        text = (
            "I am Ramesh, Aadhaar 2345 6789 0123, PAN ABCDE1234F, "
            "phone 9876543210 and email ramesh@example.com"
        )
        result = PIIGuardService.scan_and_redact(text, language="en")
        assert result.has_pii is True
        assert set(result.detected_types) == {"aadhaar", "pan", "phone", "email"}
        assert "[REDACTED_AADHAAR]" in result.sanitized_text
        assert "[REDACTED_PAN]" in result.sanitized_text
        assert "[REDACTED_PHONE]" in result.sanitized_text
        assert "[REDACTED_EMAIL]" in result.sanitized_text
        assert "2345 6789 0123" not in result.sanitized_text
        assert "ABCDE1234F" not in result.sanitized_text
        assert "9876543210" not in result.sanitized_text
        assert "ramesh@example.com" not in result.sanitized_text

        # Verify English advisory notice
        assert result.notice is not None
        assert "Sensitive personal details" in result.notice
        assert "YojanaSetu does not need or store" in result.notice

    def test_hindi_notice_generation(self):
        text = "Mera phone 9876543210 aur aadhaar 2345-6789-0123 hai"
        result = PIIGuardService.scan_and_redact(text, language="hi")
        assert result.has_pii is True
        assert result.notice is not None
        assert "सूचना:" in result.notice
        assert "योजनासेतु को आधार" in result.notice

    def test_sanitize_backwards_compatibility(self):
        text = "Call 9876543210 please"
        sanitized = PIIGuardService.sanitize(text)
        assert sanitized == "Call [REDACTED_PHONE] please"

    def test_empty_string_handling(self):
        result = PIIGuardService.scan_and_redact("")
        assert result.has_pii is False
        assert result.sanitized_text == ""
        assert result.notice is None
