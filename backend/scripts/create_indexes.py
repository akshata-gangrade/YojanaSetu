"""Idempotent script to create standard non-vector indexes on MongoDB database.

Invariants:
- Creates standard unique, compound, and TTL indexes across collections.
- Does NOT create the Atlas Vector Search index.
- Does NOT insert or modify any documents.
- Idempotent and safe to run multiple times.
"""

import asyncio
import sys
from pathlib import Path

# Ensure backend root is on sys.path for direct script execution
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.core.config import get_settings  # noqa: E402
from app.core.logging import logger, setup_logging  # noqa: E402
from app.db.indexes import ensure_indexes  # noqa: E402
from app.db.mongo import MongoDBManager  # noqa: E402


async def run_create_indexes() -> None:
    """Connect to database, ensure all non-vector indexes, and report results."""
    settings = get_settings()
    logger.info(
        "Connecting to database '%s' to create standard non-vector indexes...",
        settings.MONGODB_DB,
    )
    print(
        f"Connecting to database '{settings.MONGODB_DB}' on MongoDB...\n"
        f"Ensuring standard non-vector indexes (idempotent)..."
    )

    db = MongoDBManager.get_database()
    try:
        # Create standard non-vector indexes only (include_vector=False)
        created = await ensure_indexes(db, include_vector=False)

        print("\n--- Standard Indexes Verified ---")
        for collection_name, index_names in created.items():
            print(f"Collection: '{collection_name}'")
            for idx_name in index_names:
                print(f"  [OK] Index: {idx_name}")
        print("\nAll standard non-vector indexes created/verified successfully.")
        print("Vector index creation was omitted. Zero documents inserted.")

    finally:
        await MongoDBManager.close_client()


def main() -> None:
    """CLI entry point for creating standard database indexes."""
    setup_logging("INFO")
    asyncio.run(run_create_indexes())


if __name__ == "__main__":
    main()
