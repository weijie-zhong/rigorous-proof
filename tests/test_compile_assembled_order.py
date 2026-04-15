"""Tests for the Python replacement of Phase 9a (assembled-order compile)."""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from orchestrate import ProofOrchestrator


def _make_orchestrator(proof_dir):
    return ProofOrchestrator(proof_dir.parent)


class TestCompileAssembledOrder:
    def test_orders_lemmas_numerically_not_lexicographically(self, proof_dir):
        # Create 12 lemma files — naive lexicographic would put 10, 11, 12 before 2.
        for k in range(1, 13):
            (proof_dir / f"proof_lemma_{k}.md").write_text(
                f"## Lemma {k}\nbody.", encoding="utf-8"
            )

        orch = _make_orchestrator(proof_dir)
        order_file, ordered = orch._compile_assembled_order()

        assert order_file.exists()
        assert order_file.name == "assembled_proof_order.md"
        assert [f.name for f in ordered] == [f"proof_lemma_{k}.md" for k in range(1, 13)]

        text = order_file.read_text(encoding="utf-8")
        # Each lemma listed in numeric order
        positions = [text.find(f"Lemma {k}:") for k in range(1, 13)]
        assert all(p >= 0 for p in positions), f"missing lemma in order file: {positions}"
        assert positions == sorted(positions), "lemmas not in numeric order"

    def test_handles_missing_lemma_indices(self, proof_dir, caplog):
        # Lemmas 1, 2, 4 exist (3 missing). Function still produces output for
        # the existing files and warns about the gap.
        for k in [1, 2, 4]:
            (proof_dir / f"proof_lemma_{k}.md").write_text(
                f"## Lemma {k}\nbody.", encoding="utf-8"
            )

        orch = _make_orchestrator(proof_dir)
        order_file, ordered = orch._compile_assembled_order()

        assert [f.name for f in ordered] == [
            "proof_lemma_1.md", "proof_lemma_2.md", "proof_lemma_4.md"
        ]
        text = order_file.read_text(encoding="utf-8")
        assert "Lemma 1:" in text
        assert "Lemma 2:" in text
        assert "Lemma 4:" in text
        assert "Lemma 3:" not in text

    def test_no_lemmas_produces_empty_order_file(self, proof_dir):
        orch = _make_orchestrator(proof_dir)
        order_file, ordered = orch._compile_assembled_order()
        assert ordered == []
        assert order_file.exists()
        text = order_file.read_text(encoding="utf-8")
        assert "Total lemma files: 0" in text

    def test_idempotent_overwrite(self, proof_dir):
        (proof_dir / "proof_lemma_1.md").write_text("body", encoding="utf-8")
        orch = _make_orchestrator(proof_dir)
        order_file, _ = orch._compile_assembled_order()
        first = order_file.read_text(encoding="utf-8")
        # Second call produces the same content (no growth)
        orch._compile_assembled_order()
        second = order_file.read_text(encoding="utf-8")
        assert first == second

    def test_ignores_unrelated_files_in_proof_dir(self, proof_dir):
        (proof_dir / "proof_lemma_1.md").write_text("body", encoding="utf-8")
        (proof_dir / "proof_lemma_2.md").write_text("body", encoding="utf-8")
        # Distractor files
        (proof_dir / "audit_lemma_1_iter_1.md").write_text("audit", encoding="utf-8")
        (proof_dir / "fork_lemma_1_gap_1.md").write_text("fork", encoding="utf-8")
        (proof_dir / "00_distilled.md").write_text("d", encoding="utf-8")

        orch = _make_orchestrator(proof_dir)
        _, ordered = orch._compile_assembled_order()
        assert [f.name for f in ordered] == ["proof_lemma_1.md", "proof_lemma_2.md"]
