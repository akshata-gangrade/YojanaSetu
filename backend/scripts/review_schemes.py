"""Interactive CLI script to review schemes in 'needs_review' status.

Invariants:
- Formats criteria, required documents, application steps, and official sources into human-readable text.
- Prompts "Verify? [y/n/s/q]":
    - 'y' or 'yes': sets status to 'verified', verified_by to 'owner', verified_at to now, last_verified to now.
    - 'n' or 'no': sets status to 'draft'.
    - 's' or 'skip': skips without modifying status or logging.
    - 'q' or 'quit': exits review session safely.
- Appends an audit log entry for every verify or reject action with actor 'owner'.
- Accepts optional --slug to review a specific scheme.
- Connects to real database from backend/.env without exposing secrets or connection URIs.
"""

import argparse
import asyncio
from collections.abc import Callable
from datetime import UTC, datetime
import sys
from typing import Any

from app.db.mongo import MongoDBManager
from app.repositories.audit_repo import AuditRepository
from app.repositories.base import IAuditRepository, ISchemeRepository
from app.repositories.scheme_repo import SchemeRepository
from app.schemas.criteria import Criterion, EligibilityCriteria
from app.schemas.enums import SchemeStatus
from app.schemas.scheme import Scheme, SchemeUpdate


def format_criterion(c: Criterion) -> str:
    """Format a single Criterion object into readable text."""
    field_name = c.field.value if hasattr(c.field, "value") else str(c.field)
    op = c.op.value if hasattr(c.op, "value") else str(c.op)
    val = c.value

    op_symbols = {
        "eq": "==",
        "in": "in",
        "not_in": "not in",
        "gte": ">=",
        "lte": "<=",
        "between": "between",
    }
    symbol = op_symbols.get(op, op)
    return f"{field_name} {symbol} {val}"


def format_criteria_tree(criteria: EligibilityCriteria | None) -> list[str]:
    """Format an EligibilityCriteria tree into readable indented bullet points."""
    lines: list[str] = []
    if not criteria:
        return ["  None"]

    if criteria.all_of:
        lines.append("  All of (Must satisfy all):")
        for c in criteria.all_of:
            lines.append(f"    - {format_criterion(c)}")

    if criteria.any_of:
        lines.append("  Any of (Must satisfy at least one):")
        for c in criteria.any_of:
            lines.append(f"    - {format_criterion(c)}")

    if criteria.as_on:
        lines.append(f"  Cut-off date (as on): {criteria.as_on}")

    return lines if lines else ["  None"]


def display_scheme(scheme: Scheme) -> None:
    """Print readable inspection details for a scheme."""
    separator = "=" * 70
    print(f"\n{separator}")
    print(f"SCHEME: {scheme.name} ({scheme.slug})")
    if scheme.name_hi:
        print(f"HINDI : {scheme.name_hi}")
    print(separator)
    print(f"Level       : {scheme.level.value.upper()}")
    print(f"State       : {scheme.state or 'None (Central Scheme)'}")
    print(f"Source URL  : {scheme.source_url}")
    print(f"Apply URL   : {scheme.apply_url}")
    print(f"Source Hash : {scheme.source_hash}")
    print(f"\nBenefit Summary:\n  {scheme.benefit_summary}")
    if scheme.benefit_summary_hi:
        print(f"\nBenefit Summary (Hindi):\n  {scheme.benefit_summary_hi}")

    print("\nEligibility Criteria:")
    for line in format_criteria_tree(scheme.eligibility_criteria):
        print(line)

    print("\nRequired Documents:")
    if scheme.required_documents:
        for idx, doc in enumerate(scheme.required_documents, 1):
            print(f"  {idx}. {doc}")
    else:
        print("  None specified")

    print("\nApplication Steps:")
    if scheme.application_steps:
        for idx, step in enumerate(scheme.application_steps, 1):
            print(f"  {idx}. {step}")
    else:
        print("  None specified")
    print(separator)


async def run_review(
    slug: str | None = None,
    scheme_repo: ISchemeRepository | None = None,
    audit_repo: IAuditRepository | None = None,
    input_func: Callable[[str], str] = input,
) -> dict[str, int]:
    """Execute interactive CLI scheme review workflow.

    Args:
        slug: Optional slug to review a single scheme.
        scheme_repo: Repository instance (defaults to MongoDB SchemeRepository).
        audit_repo: Audit log repository instance (defaults to MongoDB AuditRepository).
        input_func: User prompt function (injectable for automated testing).

    Returns:
        Statistics dictionary of actions taken.
    """
    if scheme_repo is None or audit_repo is None:
        db = MongoDBManager.get_database()
        scheme_repo = scheme_repo or SchemeRepository(db)
        audit_repo = audit_repo or AuditRepository(db)

    stats = {
        "reviewed": 0,
        "verified": 0,
        "rejected": 0,
        "skipped": 0,
    }

    schemes_to_review: list[Scheme] = []

    if slug:
        scheme = await scheme_repo.get_by_slug(slug.strip())
        if not scheme:
            print(f"ERROR: Scheme with slug '{slug}' not found.", file=sys.stderr)
            return stats
        schemes_to_review.append(scheme)
    else:
        schemes_to_review = await scheme_repo.get_admin_schemes(
            status=SchemeStatus.NEEDS_REVIEW,
            limit=100,
        )

    if not schemes_to_review:
        print("No schemes currently awaiting review (status: needs_review).")
        return stats

    print(f"\nFound {len(schemes_to_review)} scheme(s) awaiting review.\n")

    for scheme in schemes_to_review:
        stats["reviewed"] += 1
        display_scheme(scheme)

        while True:
            raw_input = input_func("Verify? [y/n/s/q]: ")
            choice = raw_input.strip().lower()
            if choice in ("y", "yes", "n", "no", "s", "skip", "q", "quit"):
                break
            print("Please enter 'y'/'yes' to verify, 'n'/'no' to reject, 's'/'skip' to skip, or 'q'/'quit' to exit.")

        if choice in ("q", "quit"):
            print("-> EXIT: Exiting review session safely.")
            break

        now = datetime.now(UTC)

        if choice in ("y", "yes"):
            # Verify scheme
            update_payload = SchemeUpdate(
                status=SchemeStatus.VERIFIED,
                verified_by="owner",
                verified_at=now,
                last_verified=now,
            )
            await scheme_repo.update_scheme(scheme.slug, update_payload)

            diff = {
                "status": {"old": scheme.status.value, "new": SchemeStatus.VERIFIED.value},
                "verified_by": {"old": scheme.verified_by, "new": "owner"},
                "verified_at": {"old": None, "new": now.isoformat()},
                "last_verified": {"old": scheme.last_verified.isoformat(), "new": now.isoformat()},
            }
            await audit_repo.log_event(
                actor="owner",
                action="verify_scheme",
                target=scheme.slug,
                diff=diff,
            )
            stats["verified"] += 1
            print(f"-> SUCCESS: Scheme '{scheme.slug}' marked VERIFIED by owner.")

        elif choice in ("n", "no"):
            # Reject scheme -> draft
            update_payload = SchemeUpdate(status=SchemeStatus.DRAFT)
            await scheme_repo.update_scheme(scheme.slug, update_payload)

            diff = {
                "status": {"old": scheme.status.value, "new": SchemeStatus.DRAFT.value},
            }
            await audit_repo.log_event(
                actor="owner",
                action="reject_scheme",
                target=scheme.slug,
                diff=diff,
            )
            stats["rejected"] += 1
            print(f"-> NOTICE: Scheme '{scheme.slug}' marked DRAFT.")

        elif choice in ("s", "skip"):
            stats["skipped"] += 1
            print(f"-> SKIPPED: Scheme '{scheme.slug}'.")

    print("\n=== Review Session Summary ===")
    print(f"Schemes reviewed : {stats['reviewed']}")
    print(f"Verified [y]     : {stats['verified']}")
    print(f"Draft [n]        : {stats['rejected']}")
    print(f"Skipped [s]      : {stats['skipped']}")

    return stats


async def _async_main(args: argparse.Namespace) -> None:
    """Run review and close client inside one event loop with try/finally."""
    try:
        await run_review(slug=args.slug)
    finally:
        await MongoDBManager.close_client()


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive CLI review for schemes awaiting verification.")
    parser.add_argument(
        "--slug",
        type=str,
        default=None,
        help="Optional scheme slug to review a single scheme.",
    )
    args = parser.parse_args()

    asyncio.run(_async_main(args))


if __name__ == "__main__":
    main()
