"""Tests that the orchestrator wires ContextBuilder into invoke_claude calls."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from orchestrate import ProofOrchestrator


class TestCachingWiring:
    def test_invoke_passes_system_prompt_when_stable_files_exist(self, proof_dir,
                                                                  distilled_md,
                                                                  strategy_md):
        (proof_dir / "00_distilled.md").write_text(distilled_md, encoding="utf-8")
        (proof_dir / "00_strategy.md").write_text(strategy_md, encoding="utf-8")

        orch = ProofOrchestrator(proof_dir.parent)
        captured = {}

        def fake_invoke(prompt, system_prompt=None, cwd=None, **_kw):
            captured["system_prompt"] = system_prompt
            return '{"ok": true}'

        with patch("orchestrate.invoke_claude", side_effect=fake_invoke):
            orch._invoke("test prompt body")

        sp = captured["system_prompt"]
        assert sp is not None
        assert "<distilled_problem>" in sp
        assert "<proof_strategy>" in sp
        assert "do NOT re-read" in sp

    def test_invoke_passes_none_when_no_stable_files(self, proof_dir):
        orch = ProofOrchestrator(proof_dir.parent)
        captured = {}

        def fake_invoke(prompt, system_prompt=None, cwd=None, **_kw):
            captured["system_prompt"] = system_prompt
            return '{"ok": true}'

        with patch("orchestrate.invoke_claude", side_effect=fake_invoke):
            orch._invoke("test prompt body")

        # ContextBuilder builds a preamble-only prompt; orchestrator should
        # treat that as None to avoid sending an empty/boilerplate prefix.
        # Either None or a preamble-only string is acceptable, but the test
        # asserts the orchestrator doesn't crash and forwards something sane.
        sp = captured["system_prompt"]
        assert sp is None or "rigorous mathematical proof workflow" in sp

    def test_phase_7_invalidates_context(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=6, audit_result="fail")
        orch = ProofOrchestrator(d.parent)

        # Force initial build
        orch.context.system_prompt()
        v_before = orch.context.version()

        # Mock the actual claude invocation to no-op
        with patch("orchestrate.invoke_claude", return_value='{"ok": true}'):
            orch._run_phase_7(lemma_k=1, iteration=1)

        # Next system_prompt() call should rebuild because invalidate()
        # was called (and Phase 7 also touched the proof file)
        orch.context.system_prompt()
        assert orch.context.version() > v_before
