from __future__ import annotations

from pathlib import Path

from services.memory.skills import AIDEV_MANAGED_SOURCE, SkillsManager


def _managed_fixture(tmp_path: Path) -> tuple[SkillsManager, Path, str]:
    data_dir = tmp_path / "data"
    skill_dir = data_dir / "skills" / "general" / "managed-demo"
    refs = skill_dir / "references"
    refs.mkdir(parents=True)

    raw = """---
name: managed-demo
description: >
  First description line
  continues here.
category: general
source: aidev-managed
status: published
---

# Managed Demo

## Purpose

This non-native heading must remain byte-for-byte untouched.
"""
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(raw, encoding="utf-8")
    (refs / "notes.md").write_text("managed reference\n", encoding="utf-8")
    return SkillsManager(str(data_dir)), skill_path, raw


def test_managed_skill_is_global_and_reads_block_scalar_description(tmp_path: Path) -> None:
    manager, _path, _raw = _managed_fixture(tmp_path)

    alice = manager.load(owner="alice")
    bob = manager.load(owner="bob")

    assert len(alice) == 1
    assert len(bob) == 1
    assert alice[0]["source"] == AIDEV_MANAGED_SOURCE
    assert alice[0]["status"] == "published"
    assert alice[0]["description"] == "First description line continues here."
    assert bob[0]["name"] == "managed-demo"


def test_managed_skill_crud_and_owner_backfill_do_not_rewrite_bytes(tmp_path: Path) -> None:
    manager, skill_path, raw = _managed_fixture(tmp_path)
    before = skill_path.read_bytes()

    assert manager.backfill_owner("alice", {"alice"}) == 0
    assert manager.update_skill(
        "managed-demo",
        {"status": "draft", "confidence": 0.35},
        owner="alice",
    ) is False
    assert manager.delete_skill("managed-demo", owner="alice") is False

    assert skill_path.read_bytes() == before == raw.encode("utf-8")


def test_managed_skill_raw_document_and_references_are_globally_readable(tmp_path: Path) -> None:
    manager, _skill_path, raw = _managed_fixture(tmp_path)

    assert manager.read_skill_md("managed-demo", owner="alice") == raw
    assert manager.read_skill_md("managed-demo", owner="bob") == raw
    assert manager.read_skill_reference(
        "managed-demo", "references/notes.md", owner="alice"
    ) == "managed reference\n"
    assert manager.read_skill_reference(
        "managed-demo", "references/notes.md", owner="bob"
    ) == "managed reference\n"


def test_non_managed_skill_keeps_strict_owner_scope(tmp_path: Path) -> None:
    manager = SkillsManager(str(tmp_path / "data"))
    manager.add_skill(
        name="private-demo",
        description="Private",
        source="user",
        status="published",
        owner="alice",
    )

    assert [item["name"] for item in manager.load(owner="alice")] == ["private-demo"]
    assert manager.load(owner="bob") == []
