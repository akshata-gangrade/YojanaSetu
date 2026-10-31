"""Ingestion module: Parses unstructured HTML/PDF documents into clean text sections."""

from typing import Any


class SchemeParser:
    """Parses raw content into structured scheme metadata and guideline sections."""

    def parse(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Convert raw content into structured guidelines and eligibility sections."""
        return {"title": "", "sections": []}
