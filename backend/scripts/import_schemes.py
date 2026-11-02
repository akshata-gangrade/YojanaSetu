"""CLI utility to import scheme definitions from JSON into the database.

Invariants:
- Creates each scheme with status 'needs_review'. Never sets status to 'verified'.
- Validates every item using the canonical SchemeCreate model.
- Reports precise validation errors per item (field path and reason) without stopping.
- Dry-run by default; requires --apply flag to commit changes to the database.
- Skips existing slugs unless --update is explicitly passed.
- Never prints connection strings or secrets.
"""

import argparse
import asyncio
import json
from pathlib import Path
import re
import sys
from typing import Any

from pydantic import ValidationError

from app.db.mongo import MongoDBManager
from app.repositories.base import ISchemeRepository
from app.repositories.scheme_repo import SchemeRepository
from app.schemas.enums import SchemeStatus
from app.schemas.scheme import SchemeCreate, SchemeUpdate


def _sanitize_error(exc: Exception) -> str:
    """Format a short error message strictly masking any connection URIs or credentials."""
    msg = str(exc)
    msg = re.sub(r"mongodb(?:\+srv)?://[^\s]+", "mongodb://<redacted>", msg)
    short = msg.splitlines()[0] if msg else type(exc).__name__
    return short[:200]


async def run_import(
    file_path: str | Path,
    apply: bool = False,
    update: bool = False,
    scheme_repo: ISchemeRepository | None = None,
) -> dict[str, int]:
    """Validate and import schemes from a JSON file.

    Args:
        file_path: Path to the JSON file containing a list of schemes.
        apply: When True, writes changes to the database; otherwise performs dry-run.
        update: When True, updates existing schemes matching on slug.
        scheme_repo: Optional repository instance (defaults to MongoDB SchemeRepository).

    Returns:
        Summary statistics dictionary.
    """
    path = Path(file_path)
    if not path.is_file():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        return {"total": 0, "valid": 0, "invalid": 0, "created": 0, "updated": 0, "skipped": 0, "failed": 1}

    try:
        with open(path, encoding="utf-8") as f:
            raw_data = json.load(f)
    except Exception as exc:
        print(f"ERROR: Failed to parse JSON file {path}: {exc}", file=sys.stderr)
        return {"total": 0, "valid": 0, "invalid": 0, "created": 0, "updated": 0, "skipped": 0, "failed": 1}

    if not isinstance(raw_data, list):
        print(f"ERROR: Expected JSON root to be a list of schemes, got {type(raw_data).__name__}", file=sys.stderr)
        return {"total": 0, "valid": 0, "invalid": 0, "created": 0, "updated": 0, "skipped": 0, "failed": 1}

    if scheme_repo is None:
        db = MongoDBManager.get_database()
        scheme_repo = SchemeRepository(db)

    stats = {
        "total": len(raw_data),
        "valid": 0,
        "invalid": 0,
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "failed": 0,
    }

    mode_label = "APPLY" if apply else "DRY RUN"
    print(f"=== YojanaSetu Scheme Importer [{mode_label}] ===")
    print(f"Source file: {path} ({stats['total']} items)\n")

    for idx, item in enumerate(raw_data):
        item_num = idx + 1
        item_slug = item.get("slug", f"<unknown-item-{item_num}>") if isinstance(item, dict) else f"<item-{item_num}>"

        if not isinstance(item, dict):
            print(f"[{item_num}/{stats['total']}] ERROR ({item_slug}): Item must be a JSON object, got {type(item).__name__}", file=sys.stderr)
            stats["invalid"] += 1
            stats["failed"] += 1
            continue

        # Enforce invariant: status must NEVER be verified upon import
        item_data = dict(item)
        item_data["status"] = SchemeStatus.NEEDS_REVIEW
        item_data["verified_by"] = None
        item_data["verified_at"] = None

        # Validate with SchemeCreate
        try:
            scheme_create = SchemeCreate.model_validate(item_data)
            stats["valid"] += 1
        except ValidationError as val_err:
            stats["invalid"] += 1
            stats["failed"] += 1
            print(f"[{item_num}/{stats['total']}] VALIDATION ERROR ({item_slug}):", file=sys.stderr)
            for err in val_err.errors():
                loc_str = " -> ".join(str(part) for part in err.get("loc", []))
                msg = err.get("msg", "Validation failed")
                print(f"    - field '{loc_str}': {msg}", file=sys.stderr)
            continue

        # Check existing slug in repository
        try:
            existing = await scheme_repo.get_by_slug(scheme_create.slug)
        except Exception as exc:
            print(f"[{item_num}/{stats['total']}] ERROR ({scheme_create.slug}): {_sanitize_error(exc)}", file=sys.stderr)
            stats["failed"] += 1
            continue

        if existing:
            if not update:
                print(f"[{item_num}/{stats['total']}] SKIP: Slug '{scheme_create.slug}' already exists (pass --update to overwrite).")
                stats["skipped"] += 1
            else:
                if apply:
                    try:
                        update_dict = scheme_create.model_dump(exclude_unset=True)
                        update_dict.pop("slug", None)
                        update_dict.pop("created_at", None)
                        update_dict.pop("id", None)
                        update_payload = SchemeUpdate(**update_dict)
                        update_payload.status = SchemeStatus.NEEDS_REVIEW
                        await scheme_repo.update_scheme(scheme_create.slug, update_payload)
                        print(f"[{item_num}/{stats['total']}] UPDATED: '{scheme_create.slug}' updated as needs_review.")
                        stats["updated"] += 1
                    except Exception as exc:
                        print(f"[{item_num}/{stats['total']}] ERROR ({scheme_create.slug}): {_sanitize_error(exc)}", file=sys.stderr)
                        stats["failed"] += 1
                else:
                    print(f"[{item_num}/{stats['total']}] [DRY RUN] Would update existing '{scheme_create.slug}' as needs_review.")
                    stats["updated"] += 1
        else:
            if apply:
                try:
                    await scheme_repo.create_scheme(scheme_create)
                    print(f"[{item_num}/{stats['total']}] CREATED: '{scheme_create.slug}' inserted as needs_review.")
                    stats["created"] += 1
                except Exception as exc:
                    print(f"[{item_num}/{stats['total']}] ERROR ({scheme_create.slug}): {_sanitize_error(exc)}", file=sys.stderr)
                    stats["failed"] += 1
            else:
                print(f"[{item_num}/{stats['total']}] [DRY RUN] Would create '{scheme_create.slug}' as needs_review.")
                stats["created"] += 1

    print("\n=== Import Summary ===")
    print(f"Total processed : {stats['total']}")
    print(f"Valid items     : {stats['valid']}")
    print(f"Invalid items   : {stats['invalid']}")
    print(f"Created         : {stats['created']}")
    print(f"Updated         : {stats['updated']}")
    print(f"Skipped         : {stats['skipped']}")
    print(f"Failed          : {stats['failed']}")

    if not apply:
        print("\nNotice: Dry-run completed. No database changes were made. Pass --apply to write to the database.")

    return stats


async def _async_main(args: argparse.Namespace) -> int:
    """Run import and client close inside one event loop with try/finally."""
    try:
        stats = await run_import(file_path=args.file, apply=args.apply, update=args.update)
        if stats.get("failed", 0) > 0 or stats.get("invalid", 0) > 0:
            return 1
        return 0
    finally:
        await MongoDBManager.close_client()


def main() -> None:
    parser = argparse.ArgumentParser(description="Import scheme definitions from a JSON file.")
    parser.add_argument(
        "file",
        nargs="?",
        default="data/scheme_drafts/template.json",
        help="Path to JSON file with schemes list (default: data/scheme_drafts/template.json)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit changes to database (default: dry run)",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update existing schemes if slug already exists (default: skip)",
    )

    args = parser.parse_args()

    exit_code = asyncio.run(_async_main(args))
    if exit_code != 0:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
