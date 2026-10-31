"""Ingestion module: Scrapes or collects raw scheme text from official portals."""

from typing import Any


class SchemeCollector:
    """Collects raw scheme text documents from designated official sources."""

    async def collect(self, source_url: str) -> dict[str, Any]:
        """Fetch raw document content from official government portals."""
        return {"source_url": source_url, "raw_content": ""}
