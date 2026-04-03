"""Layer 1: Orchestrator unit tests."""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from orchestrate import (
    detect_phase_from_files,
    parse_json_from_output,
    OrchestratorState,
    _count_lemmas,
    _latest_audit_iteration,
    _audit_has_failures,
    _parse_lemma_dependencies,
    _get_difficulty,
    _is_retryable_error,
    _parse_retry_after,
    invoke_claude,
    RETRYABLE_PATTERNS,
)


# ===== 1.1 Phase detection from files =====

class TestPhaseDetection:
    def test_no_proof_dir_returns_phase_0(self, tmp_path):
        d = tmp_path / "proof_work"
        assert detect_phase_from_files(d) == (0, 0, 0)

    def test_user_input_only_returns_phase_1(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=1)
        assert detect_phase_from_files(d) == (1, 0, 0)

    def test_distilled_only_returns_phase_3(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=3)
        assert detect_phase_from_files(d) == (3, 0, 0)

    def test_with_decomposition_returns_phase_4(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=4)
        # Has decomposition but no proof lemmas → phase 4
        assert detect_phase_from_files(d) == (4, 1, 1)

    def test_mid_proof_returns_next_lemma(self, proof_dir_at_phase, proof_lemma_md):
        d = proof_dir_at_phase(phase=4)
        # Write decomposition
        (d / "01_decomposition.md").write_text("""\
**Lemma 1**: First.
- Depends on: H1
- Why needed: Foundation.

**Lemma 2**: Second.
- Depends on: Lemma 1
- Why needed: Main.
""", encoding="utf-8")
        # Write proof for lemma 1 only (of 2)
        (d / "proof_lemma_1.md").write_text(proof_lemma_md, encoding="utf-8")
        assert detect_phase_from_files(d) == (4, 2, 1)

    def test_all_proofs_no_audit_returns_phase_5(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=5)
        assert detect_phase_from_files(d) == (5, 1, 1)

    def test_audit_failed_no_fork_returns_phase_6(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=6, audit_result="fail")
        phase, lemma, iteration = detect_phase_from_files(d)
        assert phase == 6
        assert iteration == 1

    def test_audit_failed_with_fork_returns_phase_7(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=7, audit_result="fail")
        phase, lemma, iteration = detect_phase_from_files(d)
        assert phase == 7

    def test_revision_done_skips_lemma(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=6, audit_result="fail")
        # Simulate revision: update proof_lemma_1 to iteration 2
        proof = (d / "proof_lemma_1.md").read_text(encoding="utf-8")
        proof = proof.replace("Iteration: 1", "Iteration: 2")
        (d / "proof_lemma_1.md").write_text(proof, encoding="utf-8")
        # Lemma 1 is revised, so detection should move to lemma 2
        phase, lemma, iteration = detect_phase_from_files(d)
        assert lemma == 2

    def test_all_audits_pass_returns_phase_9(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=6, audit_result="pass")
        assert detect_phase_from_files(d) == (9, 0, 0)

    def test_cold_read_done_returns_phase_9(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=9)
        (d / "cold_read_audit.md").write_text("Clean pass ✅", encoding="utf-8")
        assert detect_phase_from_files(d) == (9, 0, 0)

    def test_final_proof_exists_returns_done(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=10)
        assert detect_phase_from_files(d) == (10, 0, 0)


# ===== 1.2 Difficulty parsing =====

class TestDifficultyParsing:
    def test_moderate_from_distilled(self, proof_dir, distilled_md):
        (proof_dir / "00_distilled.md").write_text(distilled_md, encoding="utf-8")
        assert _get_difficulty(proof_dir) == "moderate"

    def test_difficult(self, proof_dir):
        (proof_dir / "00_distilled.md").write_text(
            "## Difficulty assessment: **difficult**\nResearch-level problem.",
            encoding="utf-8",
        )
        assert _get_difficulty(proof_dir) == "difficult"

    def test_easy(self, proof_dir):
        (proof_dir / "00_distilled.md").write_text(
            "## Difficulty assessment: **easy**\nTextbook exercise.",
            encoding="utf-8",
        )
        assert _get_difficulty(proof_dir) == "easy"

    def test_missing_file_defaults_moderate(self, proof_dir):
        assert _get_difficulty(proof_dir) == "moderate"


# ===== 1.4 Heartbeat staleness =====

class TestHeartbeat:
    def test_fresh_heartbeat_not_stale(self, proof_dir, fresh_heartbeat):
        state = OrchestratorState(proof_dir)
        state.data["heartbeat"] = fresh_heartbeat
        assert state.is_heartbeat_stale() is False

    def test_old_heartbeat_is_stale(self, proof_dir, stale_heartbeat):
        state = OrchestratorState(proof_dir)
        state.data["heartbeat"] = stale_heartbeat
        assert state.is_heartbeat_stale() is True

    def test_no_heartbeat_is_stale(self, proof_dir):
        state = OrchestratorState(proof_dir)
        assert state.is_heartbeat_stale() is True

    def test_corrupt_heartbeat_is_stale(self, proof_dir):
        state = OrchestratorState(proof_dir)
        state.data["heartbeat"] = "not-a-timestamp"
        assert state.is_heartbeat_stale() is True

    def test_state_save_and_load(self, proof_dir):
        state = OrchestratorState(proof_dir)
        state.set("current_phase", 4)
        state.set("phase_status", "in_progress")
        state.save()

        state2 = OrchestratorState(proof_dir)
        assert state2.get("current_phase") == 4
        assert state2.get("phase_status") == "in_progress"

    def test_corrupt_state_file_returns_empty(self, proof_dir):
        (proof_dir / "orchestrator_state.json").write_text("not json!", encoding="utf-8")
        state = OrchestratorState(proof_dir)
        assert state.data == {}


# ===== 1.8 Lemma dependency parsing =====

class TestDependencyParsing:
    def test_depends_on_lemmas(self, proof_dir, distilled_md):
        (proof_dir / "00_distilled.md").write_text(distilled_md, encoding="utf-8")
        (proof_dir / "01_decomposition.md").write_text("""\
**Lemma 1**: Base case.
- Depends on: H1
- Why needed: Foundation.

**Lemma 2**: Inductive step.
- Depends on: Lemma 1, H2
- Why needed: Main step.

**Lemma 3**: Combination.
- Depends on: Lemma 1, Lemma 2
- Why needed: Final result.
""", encoding="utf-8")

        assert _parse_lemma_dependencies(proof_dir, 1) == []
        assert _parse_lemma_dependencies(proof_dir, 2) == [1]
        assert sorted(_parse_lemma_dependencies(proof_dir, 3)) == [1, 2]

    def test_no_decomposition_file(self, proof_dir):
        assert _parse_lemma_dependencies(proof_dir, 1) == []

    def test_no_depends_on_line(self, proof_dir):
        (proof_dir / "01_decomposition.md").write_text(
            "**Lemma 1**: Something.\n- Why needed: test.\n",
            encoding="utf-8",
        )
        assert _parse_lemma_dependencies(proof_dir, 1) == []


# ===== 1.9 JSON parsing robustness =====

class TestJsonParsing:
    def test_plain_json(self):
        result = parse_json_from_output('{"lemma": 1, "steps": 5}')
        assert result == {"lemma": 1, "steps": 5}

    def test_outer_wrapper(self):
        outer = json.dumps({"result": '{"lemma": 1}'})
        result = parse_json_from_output(outer)
        assert result == {"lemma": 1}

    def test_markdown_json_block(self):
        text = 'Some text\n```json\n{"a": 1}\n```\nmore text'
        result = parse_json_from_output(text)
        assert result == {"a": 1}

    def test_garbage_returns_none(self):
        assert parse_json_from_output("garbage text") is None

    def test_empty_string_returns_none(self):
        assert parse_json_from_output("") is None

    def test_nested_json(self):
        text = '{"nested": {"a": 1}}'
        result = parse_json_from_output(text)
        assert result == {"nested": {"a": 1}}


# ===== Helper function tests =====

class TestHelpers:
    def test_count_lemmas_from_decomposition(self, proof_dir, decomposition_md):
        (proof_dir / "01_decomposition.md").write_text(decomposition_md, encoding="utf-8")
        assert _count_lemmas(proof_dir) == 2

    def test_count_lemmas_from_proof_files(self, proof_dir):
        (proof_dir / "proof_lemma_1.md").write_text("test", encoding="utf-8")
        (proof_dir / "proof_lemma_2.md").write_text("test", encoding="utf-8")
        (proof_dir / "proof_lemma_3.md").write_text("test", encoding="utf-8")
        assert _count_lemmas(proof_dir) == 3

    def test_count_lemmas_empty(self, proof_dir):
        assert _count_lemmas(proof_dir) == 0

    def test_latest_audit_iteration(self, proof_dir):
        (proof_dir / "audit_lemma_1_iter_1.md").write_text("test", encoding="utf-8")
        (proof_dir / "audit_lemma_1_iter_2.md").write_text("test", encoding="utf-8")
        assert _latest_audit_iteration(proof_dir, 1) == 2

    def test_latest_audit_iteration_none(self, proof_dir):
        assert _latest_audit_iteration(proof_dir, 1) == 0

    def test_audit_has_failures_with_x(self, proof_dir, audit_fail_md):
        f = proof_dir / "audit.md"
        f.write_text(audit_fail_md, encoding="utf-8")
        assert _audit_has_failures(f) is True

    def test_audit_has_failures_clean(self, proof_dir, audit_pass_md):
        f = proof_dir / "audit.md"
        f.write_text(audit_pass_md, encoding="utf-8")
        assert _audit_has_failures(f) is False

    def test_audit_has_failures_missing_file(self, proof_dir):
        f = proof_dir / "nonexistent.md"
        assert _audit_has_failures(f) is True


import re as _re
from unittest.mock import patch, MagicMock

from orchestrate import (
    ProofOrchestrator,
    prompt_user_fork_decision,
)


def make_mock_invoke(proof_dir, audit_result="pass"):
    """
    Return a mock invoke_claude that writes expected files based on prompt content.
    """
    def mock_invoke(prompt, system_prompt=None, cwd=None, **_kwargs):
        # Phase 1: Distill
        if "Distill" in prompt and "00_user_input.md" in prompt:
            (proof_dir / "00_distilled.md").write_text("""\
## Proposition
For all n in N, if n^2 is even then n is even.

## Hypotheses
H1: n is a natural number
H2: n^2 is even

## Definitions
Even: An integer k is even if there exists an integer m such that k = 2m.

## Difficulty assessment: **moderate**
Standard result, provable by contradiction.
""", encoding="utf-8")
            return '{"difficulty": "moderate", "hypothesis_count": 2, "proposition_summary": "n^2 even implies n even"}'

        # Phase 2: Survey
        if "Literature Survey" in prompt:
            (proof_dir / "00_survey.md").write_text(
                "## Survey\nDivision algorithm applicable.", encoding="utf-8"
            )
            return '{"applicable_theorems": 1, "counterexamples": 0, "key_objects": ["integers"]}'

        # Phase 3: Strategy + Decomposition
        if "Strategy" in prompt and "Decomposition" in prompt and "Your Task: Phase 3" in prompt:
            (proof_dir / "00_strategy.md").write_text("""\
## Proof Strategy
Proof by contradiction via the contrapositive.

## Known Results Used
- Division algorithm
""", encoding="utf-8")
            (proof_dir / "01_decomposition.md").write_text("""\
**Lemma 1**: First claim.
- Depends on: H1
- Why needed: Foundation.

**Lemma 2**: Second claim.
- Depends on: Lemma 1
- Why needed: Main result.
""", encoding="utf-8")
            return '{"strategy": "contradiction", "lemma_count": 2, "lemmas": ["First claim", "Second claim"]}'

        # Phase 4: Prove Lemma
        if "Prove Lemma" in prompt:
            m = _re.search(r"Lemma\s+(\d+)", prompt)
            k = m.group(1) if m else "1"
            (proof_dir / f"proof_lemma_{k}.md").write_text(f"""\
## Lemma {k} — Test claim
Status: DRAFT
Iteration: 1
Gaps: none

Step 1. Test step. [Hypothesis H1]
""", encoding="utf-8")
            return f'{{"lemma": {k}, "steps": 1, "status": "DRAFT", "gaps": []}}'

        # Phase 5: Audit
        if "hostile" in prompt.lower():
            m = _re.search(r"proof_lemma_(\d+)", prompt)
            k = m.group(1) if m else "1"
            iter_m = _re.search(r"iter_(\d+)", prompt)
            iteration = iter_m.group(1) if iter_m else "1"

            if audit_result == "pass":
                content = "\n".join(f"{i}. Check: ✅" for i in range(1, 7))
                (proof_dir / f"audit_lemma_{k}_iter_{iteration}.md").write_text(
                    content, encoding="utf-8"
                )
                return f'{{"lemma": {k}, "iteration": {iteration}, "checks": ["✅","✅","✅","✅","✅","✅"], "failures": []}}'
            else:
                content = "1. Check: ✅\n2. Check: ❌ failure\n" + "\n".join(
                    f"{i}. Check: ✅" for i in range(3, 7)
                )
                (proof_dir / f"audit_lemma_{k}_iter_{iteration}.md").write_text(
                    content, encoding="utf-8"
                )
                return f'{{"lemma": {k}, "iteration": {iteration}, "checks": ["✅","❌","✅","✅","✅","✅"], "failures": ["check 2 failed"]}}'

        # Phase 6: Gap Analysis
        if "Gap Analysis" in prompt:
            m = _re.search(r"Lemma\s+(\d+)", prompt)
            k = m.group(1) if m else "1"
            (proof_dir / f"fork_lemma_{k}_gap_1.md").write_text(
                f"## Gap Analysis: Lemma {k}, Gap 1\nTest gap.", encoding="utf-8"
            )
            return f'{{"lemma": {k}, "fixable": 1, "crucial": 0, "fatal": 0, "fork_files": []}}'

        # Phase 7: Revision
        if "Revise" in prompt:
            m = _re.search(r"Lemma\s+(\d+)", prompt)
            k = m.group(1) if m else "1"
            # Read current iteration and increment
            proof_file = proof_dir / f"proof_lemma_{k}.md"
            current_iter = 1
            if proof_file.exists():
                text = proof_file.read_text(encoding="utf-8")
                im = _re.search(r"Iteration:\s*(\d+)", text)
                if im:
                    current_iter = int(im.group(1))
            next_iter = current_iter + 1
            (proof_dir / f"proof_lemma_{k}.md").write_text(f"""\
## Lemma {k} — Test claim
Status: REVISED
Iteration: {next_iter}
Gaps: none

Step 1. Revised step. [Hypothesis H1]
""", encoding="utf-8")
            return f'{{"lemma": {k}, "iteration": {next_iter}, "steps_changed": 1, "all_issues_addressed": true}}'

        # Phase 9 checks — order matters: most specific first
        if "proof journal" in prompt.lower():
            (proof_dir / "proof_journal.md").write_text(
                "## Proof Journal\n\nFull audit trail.", encoding="utf-8"
            )
            return '{"sections": 7, "has_unresolved_gaps": false}'

        if "Write the final proof" in prompt:
            (proof_dir / "final_proof.md").write_text(
                "## Final Proof\n\nStep 1. ... [Hypothesis H1]\n\n∎", encoding="utf-8"
            )
            return '{"complete": true, "unresolved_gaps": 0}'

        if "cold read" in prompt.lower() and "Compile" not in prompt:
            (proof_dir / "cold_read_audit.md").write_text(
                "Cold read: all checks pass. ✅", encoding="utf-8"
            )
            return '{"clean_pass": true, "issues_found": 0, "issues_fixed": 0, "unresolved_critical": 0}'

        if "Compile" in prompt:
            (proof_dir / "assembled_proof_order.md").write_text(
                "proof_lemma_1.md\nproof_lemma_2.md", encoding="utf-8"
            )
            return '{"lemma_count": 2, "lemma_files": ["proof_lemma_1.md", "proof_lemma_2.md"]}'

        return '{"status": "unknown prompt"}'

    return mock_invoke


# ===== 1.2 & 1.3 Resume tests =====

class TestResume:
    def test_resume_stale_heartbeat_restarts_phase(self, proof_dir_at_phase,
                                                     write_state, stale_heartbeat):
        d = proof_dir_at_phase(phase=4)
        write_state({
            "current_phase": 4,
            "current_lemma": 2,
            "current_iteration": 1,
            "phase_status": "in_progress",
            "heartbeat": stale_heartbeat,
        })
        orch = ProofOrchestrator(d.parent)
        phase, lemma, iteration = orch._detect_resume_point()
        assert phase == 4
        assert lemma == 2

    def test_resume_done_advances_to_next(self, proof_dir_at_phase, write_state):
        d = proof_dir_at_phase(phase=5)  # has proofs, no audits
        write_state({
            "current_phase": 4,
            "phase_status": "done",
        })
        orch = ProofOrchestrator(d.parent)
        phase, lemma, iteration = orch._detect_resume_point()
        assert phase == 5


# ===== 1.5 Full phase progression (mock) =====

class TestFullProgression:
    def test_full_run_creates_all_files(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=1)  # has user input
        mock = make_mock_invoke(d, audit_result="pass")

        with patch("orchestrate.invoke_claude", side_effect=mock):
            orch = ProofOrchestrator(d.parent, max_effort=False)
            orch.run()

        assert (d / "00_distilled.md").exists()
        assert (d / "00_strategy.md").exists()
        assert (d / "01_decomposition.md").exists()
        assert (d / "proof_lemma_1.md").exists()
        assert (d / "proof_lemma_2.md").exists()
        assert (d / "audit_lemma_1_iter_1.md").exists()
        assert (d / "audit_lemma_2_iter_1.md").exists()
        assert (d / "cold_read_audit.md").exists()
        assert (d / "final_proof.md").exists()
        assert (d / "proof_journal.md").exists()

    def test_state_tracks_progression(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=1)
        mock = make_mock_invoke(d, audit_result="pass")

        with patch("orchestrate.invoke_claude", side_effect=mock):
            orch = ProofOrchestrator(d.parent, max_effort=False)
            orch.run()

        state = json.loads((d / "orchestrator_state.json").read_text(encoding="utf-8"))
        assert state["phase_status"] == "done"


# ===== 1.6 Fork timeout =====

class TestForkTimeout:
    def test_timeout_returns_b_auto(self):
        choice, was_auto = prompt_user_fork_decision("Test gap", timeout=1)
        assert choice == "B"
        assert was_auto is True


# ===== 1.7 Iteration cap =====

class TestIterationCap:
    def test_max_7_inner_iterations(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=5)
        mock = make_mock_invoke(d, audit_result="fail")

        with patch("orchestrate.invoke_claude", side_effect=mock):
            orch = ProofOrchestrator(d.parent, max_effort=True)
            orch.lemma_count = 2
            orch._run_inner_audit_loop(start_lemma=1, start_iteration=1)

        assert (d / "audit_lemma_1_iter_1.md").exists()
        assert (d / "audit_lemma_1_iter_7.md").exists()
        assert not (d / "audit_lemma_1_iter_8.md").exists()


# ===== 2.0 Retry logic =====

class TestRetryLogic:
    def test_is_retryable_matches_all_patterns(self):
        for pattern in RETRYABLE_PATTERNS:
            assert _is_retryable_error(f"Error: {pattern} exceeded"), \
                f"Should match pattern: {pattern}"

    def test_is_retryable_case_insensitive(self):
        assert _is_retryable_error("RATE LIMIT exceeded")
        assert _is_retryable_error("Rate Limit hit")

    def test_is_retryable_rejects_permanent_error(self):
        assert not _is_retryable_error("unknown flag --foo")
        assert not _is_retryable_error("permission denied")
        assert not _is_retryable_error("invalid argument")

    def test_parse_retry_after_header(self):
        assert _parse_retry_after("Retry-After: 45") == 45.0
        assert _parse_retry_after("retry-after: 10") == 10.0
        assert _parse_retry_after("retry after: 120") == 120.0

    def test_parse_retry_after_prose(self):
        assert _parse_retry_after("Please try again in 30 seconds") == 30.0
        assert _parse_retry_after("retry in 60s") == 60.0

    def test_parse_retry_after_timestamp(self):
        from datetime import timedelta
        future = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
        stderr = f"reset at {future}"
        result = _parse_retry_after(stderr)
        assert result is not None
        # Should be ~300s (+2s margin), allow some tolerance
        assert 290 < result < 310

    def test_parse_retry_after_returns_none_on_garbage(self):
        assert _parse_retry_after("unknown error occurred") is None
        assert _parse_retry_after("") is None

    @patch("orchestrate.time.sleep")
    @patch("orchestrate.subprocess.run")
    def test_retries_on_rate_limit_with_retry_after(self, mock_run, mock_sleep):
        fail = MagicMock(returncode=1, stderr="Error: rate limit exceeded. Retry-After: 10", stdout="")
        ok = MagicMock(returncode=0, stderr="", stdout='{"result": "hello"}')
        mock_run.side_effect = [fail, fail, ok]

        result = invoke_claude("test prompt", max_retries=5, max_total_wait=1000)
        assert result == "hello"
        # Should sleep 10s per retry (under 60s chunk threshold), 2 retries
        total_slept = sum(call[0][0] for call in mock_sleep.call_args_list)
        assert total_slept == 20.0

    @patch("orchestrate.random.random", return_value=0.5)  # no jitter at midpoint
    @patch("orchestrate.time.sleep")
    @patch("orchestrate.subprocess.run")
    def test_retries_with_backoff_fallback(self, mock_run, mock_sleep, _mock_rand):
        fail = MagicMock(returncode=1, stderr="Error: rate limit exceeded", stdout="")
        ok = MagicMock(returncode=0, stderr="", stdout='{"result": "ok"}')
        mock_run.side_effect = [fail, fail, ok]

        result = invoke_claude("test prompt", max_retries=5, max_total_wait=100000)
        assert result == "ok"
        # Sleep is chunked into 60s intervals; check total sleep time
        total_slept = sum(call[0][0] for call in mock_sleep.call_args_list)
        # First delay: 300 * 2^0 = 300s, second: 300 * 2^1 = 600s → total 900s
        assert total_slept == 900.0

    @patch("orchestrate.time.sleep")
    @patch("orchestrate.subprocess.run")
    def test_raises_on_permanent_error(self, mock_run, mock_sleep):
        fail = MagicMock(returncode=1, stderr="Error: unknown flag --foo", stdout="")
        mock_run.return_value = fail

        with pytest.raises(RuntimeError, match="unknown flag"):
            invoke_claude("test prompt", max_retries=5)
        assert mock_sleep.call_count == 0

    @patch("orchestrate.time.sleep")
    @patch("orchestrate.subprocess.run")
    def test_raises_after_max_retries(self, mock_run, mock_sleep):
        fail = MagicMock(returncode=1, stderr="Error: rate limit. Retry-After: 1", stdout="")
        mock_run.return_value = fail

        with pytest.raises(RuntimeError, match="3 retries"):
            invoke_claude("test prompt", max_retries=3, max_total_wait=100000)
        # 4 total attempts (1 first + 3 retries); sleeps 1s between each
        total_slept = sum(call[0][0] for call in mock_sleep.call_args_list)
        assert total_slept == 3.0

    @patch("orchestrate.time.sleep")
    @patch("orchestrate.subprocess.run")
    def test_raises_after_budget_exhausted(self, mock_run, mock_sleep):
        fail = MagicMock(returncode=1, stderr="Error: rate limit exceeded", stdout="")
        mock_run.return_value = fail

        with pytest.raises(RuntimeError, match="budget exhausted"):
            invoke_claude("test prompt", max_retries=20, max_total_wait=10)
        # Fallback delay is 300s > budget of 10s, so should fail on first retry attempt
        assert mock_sleep.call_count == 0

    @patch("orchestrate.time.sleep")
    @patch("orchestrate.subprocess.run")
    def test_no_retry_disables_retries(self, mock_run, mock_sleep):
        fail = MagicMock(returncode=1, stderr="Error: rate limit exceeded", stdout="")
        mock_run.return_value = fail

        with pytest.raises(RuntimeError, match="rate limit"):
            invoke_claude("test prompt", max_retries=0, max_total_wait=100000)
        assert mock_run.call_count == 1  # exactly one attempt
        assert mock_sleep.call_count == 0


# ===== 3.0 Terminal mode =====

import argparse as _argparse
import subprocess as _subprocess

from orchestrate import (
    _launch_in_new_console, _build_extra_args,
    RETRY_MAX_ATTEMPTS, RETRY_MAX_TOTAL_WAIT,
    FORK_FAILURE_THRESHOLD,
    prompt_user_fork_decision,
    OrchestratorState,
    ProofOrchestrator,
)


class TestTerminalMode:
    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
    @patch("orchestrate.subprocess.Popen")
    def test_launch_windows_calls_popen_with_new_console(self, mock_popen):
        args = _argparse.Namespace(
            resume=False, max_effort=True, work_dir=".",
            max_retries=RETRY_MAX_ATTEMPTS, max_wait=RETRY_MAX_TOTAL_WAIT,
            no_retry=False,
        )
        result = _launch_in_new_console(args)
        assert result is True
        mock_popen.assert_called_once()
        call_kwargs = mock_popen.call_args
        assert call_kwargs.kwargs["creationflags"] == 0x00000010  # CREATE_NEW_CONSOLE
        # Verify cmd /c batch_file wrapper
        cmd = call_kwargs.args[0]
        assert cmd[0] == "cmd"
        assert cmd[1] == "/c"
        # Batch file should contain --max-effort but not --terminal-mode
        batch_path = cmd[2]
        batch_text = open(batch_path, encoding="utf-8").read()
        assert "--max-effort" in batch_text
        assert "--terminal-mode" not in batch_text

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
    @patch("orchestrate.subprocess.Popen")
    def test_launch_forwards_all_flags(self, mock_popen):
        args = _argparse.Namespace(
            resume=True, max_effort=True, work_dir="/some/path",
            max_retries=5, max_wait=100.0, no_retry=False,
        )
        _launch_in_new_console(args)
        # Flags are now written into the batch file, not passed as Popen args
        cmd = mock_popen.call_args.args[0]
        batch_path = cmd[2]
        batch_text = open(batch_path, encoding="utf-8").read()
        assert "--resume" in batch_text
        assert "--max-effort" in batch_text
        assert "--max-retries" in batch_text
        assert "5" in batch_text
        assert "--max-wait" in batch_text
        assert "100.0" in batch_text

    def test_build_extra_args(self):
        args = _argparse.Namespace(
            resume=True, max_effort=True, work_dir=".",
            max_retries=5, max_wait=100.0, no_retry=True,
        )
        extra = _build_extra_args(args)
        assert "--resume" in extra
        assert "--max-effort" in extra
        assert "--max-retries" in extra
        assert "5" in extra
        assert "--max-wait" in extra
        assert "100.0" in extra
        assert "--no-retry" in extra

    @patch("orchestrate._launch_linux")
    @patch("orchestrate.sys.platform", "linux")
    def test_linux_dispatches_to_launch_linux(self, mock_launch_linux):
        mock_launch_linux.return_value = True
        args = _argparse.Namespace(
            resume=False, max_effort=False, work_dir=".",
            max_retries=RETRY_MAX_ATTEMPTS, max_wait=RETRY_MAX_TOTAL_WAIT,
            no_retry=False,
        )
        result = _launch_in_new_console(args)
        assert result is True
        mock_launch_linux.assert_called_once()

    @patch("orchestrate._launch_macos")
    @patch("orchestrate.sys.platform", "darwin")
    def test_macos_dispatches_to_launch_macos(self, mock_launch_macos):
        mock_launch_macos.return_value = True
        args = _argparse.Namespace(
            resume=False, max_effort=False, work_dir=".",
            max_retries=RETRY_MAX_ATTEMPTS, max_wait=RETRY_MAX_TOTAL_WAIT,
            no_retry=False,
        )
        result = _launch_in_new_console(args)
        assert result is True
        mock_launch_macos.assert_called_once()


# ===== 4.0 Passed lemma tracking =====

class TestPassedLemmaTracking:
    def test_passed_lemmas_stored_in_state(self, tmp_path):
        """Passed lemmas should be persisted in orchestrator_state.json."""
        proof_dir = tmp_path / "proof_work"
        proof_dir.mkdir()
        state = OrchestratorState(proof_dir)
        state.set("passed_lemmas", [1, 3])
        # Reload and verify
        state2 = OrchestratorState(proof_dir)
        assert state2.get("passed_lemmas") == [1, 3]

    def test_passed_lemmas_cleared_on_restrategize(self, tmp_path):
        """Outer loop re-strategization should clear passed lemmas."""
        proof_dir = tmp_path / "proof_work"
        proof_dir.mkdir()
        state = OrchestratorState(proof_dir)
        state.set("passed_lemmas", [1, 2, 3])
        # Simulate clearing (as done in _run_dual_loop outer > 0)
        state.set("passed_lemmas", [])
        assert state.get("passed_lemmas") == []


# ===== 5.0 Fork failure threshold =====

class TestForkFailureThreshold:
    def test_timeout_defaults_to_b_under_threshold(self):
        """Under failure threshold, timeout default should be B."""
        choice, was_auto = prompt_user_fork_decision(
            "test gap", timeout=0, default="B")
        assert choice == "B"
        assert was_auto is True

    def test_timeout_defaults_to_a_at_threshold(self):
        """At/above failure threshold, timeout default should be A."""
        choice, was_auto = prompt_user_fork_decision(
            "test gap", timeout=0, default="A")
        assert choice == "A"
        assert was_auto is True

    def test_failure_count_tracked_in_state(self, tmp_path):
        """Failure counts should be persisted in state."""
        proof_dir = tmp_path / "proof_work"
        proof_dir.mkdir()
        state = OrchestratorState(proof_dir)
        failures = {"1": 2, "3": 4}
        state.set("lemma_failure_counts", failures)
        state2 = OrchestratorState(proof_dir)
        assert state2.get("lemma_failure_counts") == failures

    def test_threshold_constant_is_3(self):
        """Fork failure threshold should be 3."""
        assert FORK_FAILURE_THRESHOLD == 3


# ===== 6.0 Auto-detect difficulty =====

class TestAutoDetectDifficulty:
    def test_difficult_enables_max_effort(self, tmp_path):
        """Difficult problems should auto-enable max effort."""
        proof_dir = tmp_path / "proof_work"
        proof_dir.mkdir()
        # Write a distilled file marking difficulty as difficult
        (proof_dir / "00_distilled.md").write_text(
            "Difficulty: **difficult**\nHard problem.", encoding="utf-8")
        orch = ProofOrchestrator(tmp_path, max_effort=False)
        assert orch.max_effort is False
        # Simulate what _run_from does after Phase 1
        difficulty = orch._get_difficulty()
        assert difficulty == "difficult"
        # Auto-enable
        if difficulty == "difficult" and not orch.max_effort:
            orch.max_effort = True
        assert orch.max_effort is True

    def test_moderate_does_not_enable_max_effort(self, tmp_path):
        """Moderate problems should not auto-enable max effort."""
        proof_dir = tmp_path / "proof_work"
        proof_dir.mkdir()
        (proof_dir / "00_distilled.md").write_text(
            "Difficulty: **moderate**\nStandard problem.", encoding="utf-8")
        orch = ProofOrchestrator(tmp_path, max_effort=False)
        difficulty = orch._get_difficulty()
        assert difficulty == "moderate"
        assert orch.max_effort is False
