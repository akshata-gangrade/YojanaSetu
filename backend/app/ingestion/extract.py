"""Ingestion module: Extracts deterministic eligibility criteria from parsed text."""

from typing import Any


class CriteriaExtractor:
    """Extracts structured age, income, caste, state, and occupation rules from text."""

    def extract_criteria(self, parsed_scheme: dict[str, Any]) -> dict[str, Any]:
        """Produce structured machine-evaluable eligibility criteria."""
        return {"criteria": {}}
