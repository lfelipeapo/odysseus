"""Regression: create_document must survive low-signal follow-up retrieval."""

from src.tool_index import ALWAYS_AVAILABLE, BUILTIN_TOOL_DESCRIPTIONS


def test_create_document_is_always_offered_to_agent():
    """System instructions may require create_document on any continuation."""
    assert "create_document" in BUILTIN_TOOL_DESCRIPTIONS
    assert "create_document" in ALWAYS_AVAILABLE
