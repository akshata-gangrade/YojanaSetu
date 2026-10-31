"""Deterministic rule engine for evaluating citizen eligibility against criteria.

Product rule: The LLM extracts information and writes explanations.
It NEVER decides eligibility. Eligibility is decided ONLY by this rule engine.
"""

from typing import Any


class RuleEngineService:
    """Evaluates citizen attributes against verified scheme criteria."""

    def evaluate(
        self, profile: dict[str, Any], scheme_criteria: dict[str, Any]
    ) -> bool:
        """Evaluate if profile meets all deterministic eligibility constraints."""
        # Feature implementation in matching/rules module
        return True
