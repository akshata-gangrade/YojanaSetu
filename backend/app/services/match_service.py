"""Deterministic scheme matching service executing Python rule engine over verified schemes."""

from app.repositories.base import ISchemeRepository
from app.schemas.api import MatchResponse, SchemeMatchItem
from app.schemas.user_profile import UserProfile
from app.services.rule_engine import EligibilityStatus, RuleEngineService


class MatchService:
    """Orchestrates deterministic eligibility checks over verified schemes without calling any LLM."""

    def __init__(
        self,
        scheme_repo: ISchemeRepository,
        rule_engine: RuleEngineService | None = None,
    ):
        self.scheme_repo = scheme_repo
        self.rule_engine = rule_engine or RuleEngineService()

    async def match_schemes(
        self,
        profile: UserProfile,
        language: str = "en",
    ) -> MatchResponse:
        """Evaluate citizen profile against verified schemes in repository.

        Invariant: Evaluated strictly by deterministic Python RuleEngineService.
        The LLM is NEVER called during eligibility evaluation.
        """
        # Fetch verified schemes (respects INCLUDE_SAMPLE_SCHEMES setting inside repository)
        verified_schemes = await self.scheme_repo.get_verified_schemes(limit=100)

        # Pre-filter by citizen state and scheme administrative tier
        prefiltered = self.rule_engine.prefilter_schemes(verified_schemes, profile)

        eligible: list[SchemeMatchItem] = []
        maybe: list[SchemeMatchItem] = []
        not_eligible: list[SchemeMatchItem] = []

        for s in prefiltered:
            result = self.rule_engine.evaluate_scheme(profile, s, lang=language)

            # Assemble contextual reasons in requested language
            if result.status == EligibilityStatus.ELIGIBLE:
                reasons = result.passed_conditions
            elif result.status == EligibilityStatus.NOT_ELIGIBLE:
                reasons = result.failed_conditions
            else:
                # 'maybe' schemes show both what passed and what requires verification
                reasons = result.passed_conditions + [
                    f"Needs verification: {field.replace('_', ' ').title()}"
                    for field in result.missing_fields
                ]

            item = SchemeMatchItem(
                slug=s.slug,
                name=s.name,
                name_hi=s.name_hi,
                level=s.level,
                state=s.state,
                category_tags=s.category_tags,
                benefit_summary=s.benefit_summary,
                benefit_summary_hi=s.benefit_summary_hi,
                apply_url=s.apply_url,
                source_url=s.source_url,
                last_verified=s.last_verified,
                reasons=reasons,
                status=result.status.value,
            )

            if result.status == EligibilityStatus.ELIGIBLE:
                eligible.append(item)
            elif result.status == EligibilityStatus.MAYBE:
                maybe.append(item)
            else:
                not_eligible.append(item)

        return MatchResponse(
            eligible=eligible,
            maybe=maybe,
            not_eligible=not_eligible,
        )

