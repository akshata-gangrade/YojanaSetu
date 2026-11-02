"""Citizen intake orchestration service combining extraction, rule evaluation, and follow-up selection."""

from typing import Any

from app.core.config import Settings
from app.repositories.base import ISchemeRepository
from app.schemas.api import IntakeExtractResponse
from app.schemas.enums import CriterionField
from app.schemas.user_profile import UserProfile
from app.services.followup_selector import FollowupSelectorService
from app.services.profile_extractor import ProfileExtractorService
from app.services.rule_engine import EligibilityStatus, RuleEngineService


class IntakeService:
    """Orchestrates intake extraction, profile merging, rule evaluation, and next-question selection."""

    def __init__(
        self,
        extractor: ProfileExtractorService,
        scheme_repo: ISchemeRepository,
        rule_engine: RuleEngineService | None = None,
        followup_selector: FollowupSelectorService | None = None,
        settings: Settings | None = None,
    ):
        self.extractor = extractor
        self.scheme_repo = scheme_repo
        self.rule_engine = rule_engine or RuleEngineService()
        self.followup_selector = followup_selector or FollowupSelectorService(self.rule_engine)
        self.settings = settings

    async def process_intake(
        self,
        message: str,
        language: str = "en",
        current_profile: UserProfile | None = None,
    ) -> IntakeExtractResponse:
        """Process citizen message, update profile state, and select follow-up question.

        1. Redacts PII and extracts structured profile fields via LLM (temperature 0).
        2. Merges extracted fields into existing citizen profile.
        3. Evaluates candidate verified schemes using deterministic Python RuleEngineService.
        4. Selects optimal follow-up question via FollowupSelectorService across 'maybe' schemes.
        """
        # 1. Profile extraction
        extract_result = await self.extractor.extract_profile(
            message=message,
            current_profile=current_profile,
            language=language,
        )

        updates = extract_result.profile_updates

        # 2. Merge updates into profile
        merged_dict: dict[str, Any] = {}
        if current_profile:
            merged_dict.update(
                {k: v for k, v in current_profile.model_dump().items() if v is not None}
            )
        merged_dict.update(updates)

        try:
            merged_profile = UserProfile.model_validate(merged_dict)
        except Exception:
            merged_profile = current_profile or UserProfile()

        effective_include_samples = (
            self.settings.INCLUDE_SAMPLE_SCHEMES if self.settings else None
        )
        effective_include_unreviewed = (
            self.settings.PUBLISH_UNREVIEWED_SCHEMES if self.settings else None
        )
        # 3. Retrieve candidate schemes from repository
        verified_schemes = await self.scheme_repo.get_verified_schemes(
            limit=100,
            include_samples=effective_include_samples,
            include_unverified=effective_include_unreviewed,
        )

        # 4. Pre-filter and evaluate candidate schemes
        prefiltered = self.rule_engine.prefilter_schemes(verified_schemes, merged_profile)
        maybe_schemes_with_results = []
        all_missing_fields: set[str] = set()

        for s in prefiltered:
            result = self.rule_engine.evaluate_scheme(merged_profile, s, lang=language)
            if result.status == EligibilityStatus.MAYBE:
                maybe_schemes_with_results.append((s, result))
                for f in result.missing_fields:
                    if merged_profile.is_field_unknown(f):
                        all_missing_fields.add(f)

        # 5. Determine next question across candidate 'maybe' schemes
        next_question_str: str | None = None
        followup_q = self.followup_selector.select_followup(
            profile=merged_profile,
            candidate_schemes=maybe_schemes_with_results,
        )

        if followup_q:
            is_hi = language.lower().startswith("hi")
            next_question_str = followup_q.question_hi if is_hi else followup_q.question_en

        # Deterministic sorting of missing fields by standard priority order
        sorted_missing = [
            field.value
            for field in CriterionField
            if field.value in all_missing_fields
        ]

        return IntakeExtractResponse(
            profile_updates=updates,
            missing_fields=sorted_missing,
            next_question=next_question_str,
            pii_notice=extract_result.pii_notice,
        )

