# Rigorous-Proof Test Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a three-layer test suite covering orchestrator correctness (mock) and SKILL.md compliance (real Claude).

**Architecture:** Unit tests monkeypatch `invoke_claude` to avoid API calls. Compliance tests dispatch real Claude via `claude -p` with the skill loaded. A shared `conftest.py` provides fixtures for temp `proof_work/` directories with pre-populated files.

**Tech Stack:** pytest, monkeypatch, tmp_path, subprocess (for compliance/e2e)

---

### Task 1: conftest.py — Shared Fixtures

**Files:**
- Create: `tests/conftest.py`

- [ ] **Step 1: Write conftest.py with all fixtures**

```python
"""Shared fixtures for rigorous-proof test suite."""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

import pytest

# Add scripts/ to sys.path so we can import orchestrate
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def proof_dir(tmp_path):
    """Create an empty proof_work/ directory and return its path."""
    d = tmp_path / "proof_work"
    d.mkdir()
    return d


@pytest.fixture
def setup_md():
    """Realistic 00_setup.md content."""
    return """\
## Proposition
For all n in N, if n^2 is even then n is even.

## Hypotheses
H1: n is a natural number
H2: n^2 is even

## Definitions
Even: An integer k is even if there exists an integer m such that k = 2m.

## Strategy
Proof by contradiction.

## Known Results Used
- Division algorithm
"""


@pytest.fixture
def decomposition_md():
    """Realistic 01_decomposition.md content with 2 lemmas."""
    return """\
## Decomposition

**Lemma 1**: If n is odd, then n^2 is odd.
- Depends on: H1
- Why needed: Contrapositive of target — if n^2 even implies n even.

**Lemma 2**: Main result — if n^2 is even then n is even.
- Depends on: Lemma 1
- Why needed: Direct application of contrapositive from Lemma 1.

## Dependency Graph
H1 → Lemma 1 → Lemma 2 (main result)
"""


@pytest.fixture
def proof_lemma_md():
    """Realistic proof_lemma_1.md content."""
    return """\
## Lemma 1 — If n is odd, then n^2 is odd
Status: DRAFT
Iteration: 1
Gaps: none

Step 1. Assume n is odd. [Hypothesis H1]
Step 2. By definition, n = 2k + 1 for some integer k. [Definition of Odd]
Step 3. n^2 = (2k+1)^2 = 4k^2 + 4k + 1 = 2(2k^2 + 2k) + 1. [Algebraic manipulation]
Step 4. Let m = 2k^2 + 2k. Then n^2 = 2m + 1. [By Step 3]
Step 5. Therefore n^2 is odd. [Definition of Odd]
"""


@pytest.fixture
def audit_pass_md():
    """Audit file where all 6 checks pass."""
    return """\
## Audit: Lemma 1 (Iteration 1)

1. Justification audit: ✅ All steps properly justified.
2. Hypothesis fidelity: ✅ Only uses stated hypotheses.
3. Target fidelity: ✅ Conclusion matches claim exactly.
4. Edge cases: ✅ No edge cases for this lemma.
5. Quantifier check: ✅ All quantifiers correct.
6. Circularity check: ✅ No circularity detected.
"""


@pytest.fixture
def audit_fail_md():
    """Audit file with failures."""
    return """\
## Audit: Lemma 1 (Iteration 1)

1. Justification audit: ✅ All steps properly justified.
2. Hypothesis fidelity: ❌ Step 3 silently assumes continuity, but only measurability was given.
3. Target fidelity: ✅ Conclusion matches claim exactly.
4. Edge cases: ❌ Does not handle the case n = 0.
5. Quantifier check: ✅ All quantifiers correct.
6. Circularity check: ✅ No circularity detected.
"""


@pytest.fixture
def proof_dir_at_phase(proof_dir, setup_md, decomposition_md, proof_lemma_md,
                        audit_pass_md, audit_fail_md):
    """
    Factory fixture: populate proof_dir to simulate being at a given phase.
    Returns a function: populate(phase, lemma_count=2, audit_result="pass")
    """
    def populate(phase, lemma_count=2, audit_result="pass"):
        # Always write setup
        (proof_dir / "00_setup.md").write_text(setup_md, encoding="utf-8")

        if phase <= 2:
            return proof_dir

        # Phase 3+: write decomposition
        (proof_dir / "01_decomposition.md").write_text(decomposition_md, encoding="utf-8")

        if phase <= 3:
            return proof_dir

        # Phase 4+: write all proof lemmas
        for k in range(1, lemma_count + 1):
            content = proof_lemma_md.replace("Lemma 1", f"Lemma {k}")
            (proof_dir / f"proof_lemma_{k}.md").write_text(content, encoding="utf-8")

        if phase <= 4:
            return proof_dir

        # Phase 5+: write audits
        audit = audit_pass_md if audit_result == "pass" else audit_fail_md
        for k in range(1, lemma_count + 1):
            content = audit.replace("Lemma 1", f"Lemma {k}")
            (proof_dir / f"audit_lemma_{k}_iter_1.md").write_text(content, encoding="utf-8")

        if phase <= 5:
            return proof_dir

        # Phase 6+: write fork files (if audit failed)
        if audit_result == "fail":
            for k in range(1, lemma_count + 1):
                (proof_dir / f"fork_lemma_{k}_gap_1.md").write_text(
                    f"## Gap Analysis: Lemma {k}, Gap 1\n\n### The gap\nTest gap.",
                    encoding="utf-8",
                )

        if phase <= 8:
            return proof_dir

        # Phase 8+: write cold read and final
        if phase >= 8:
            (proof_dir / "cold_read_audit.md").write_text(
                "Cold read: all checks pass. ✅", encoding="utf-8"
            )

        if phase >= 9:
            (proof_dir / "final_proof.md").write_text(
                "## Final Proof\n...\n∎", encoding="utf-8"
            )
            (proof_dir / "proof_journal.md").write_text(
                "## Proof Journal\n...", encoding="utf-8"
            )

        return proof_dir

    return populate


@pytest.fixture
def write_state(proof_dir):
    """Write an orchestrator_state.json file. Returns a function."""
    def _write(data: dict):
        state_path = proof_dir / "orchestrator_state.json"
        state_path.write_text(json.dumps(data), encoding="utf-8")
        return state_path
    return _write


@pytest.fixture
def fresh_heartbeat():
    """Return an ISO timestamp from 10 seconds ago."""
    return (datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat()


@pytest.fixture
def stale_heartbeat():
    """Return an ISO timestamp from 5 minutes ago."""
    return (datetime.now(timezone.utc) - timedelta(seconds=300)).isoformat()
```

- [ ] **Step 2: Verify imports resolve**

Run: `cd "C:/Users/wjzhong/OneDrive - Stanford/claude-skills/rigorous-proof" && python -c "import tests.conftest; print('OK')"`

Expected: `OK` (no import errors)

---

### Task 2: Pure Function Unit Tests (no mocking)

**Files:**
- Create: `tests/test_orchestrate.py`

These tests cover functions that don't call `invoke_claude`: phase detection, heartbeat, JSON parsing, dependency parsing.

- [ ] **Step 1: Write test_orchestrate.py with pure function tests**

```python
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
)


# ===== 1.1 Phase detection from files =====

class TestPhaseDetection:
    def test_missing_setup_raises(self, proof_dir):
        with pytest.raises(FileNotFoundError, match="00_setup.md"):
            detect_phase_from_files(proof_dir)

    def test_setup_only_returns_phase_2(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=2)
        assert detect_phase_from_files(d) == (2, 0, 0)

    def test_with_decomposition_returns_phase_3(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=3)
        assert detect_phase_from_files(d) == (3, 1, 1)

    def test_mid_proof_returns_next_lemma(self, proof_dir_at_phase, proof_lemma_md):
        d = proof_dir_at_phase(phase=3)
        # Write proof for lemma 1 only (of 2)
        content = proof_lemma_md.replace("Lemma 1", "Lemma 1")
        (d / "proof_lemma_1.md").write_text(content, encoding="utf-8")
        assert detect_phase_from_files(d) == (3, 2, 1)

    def test_all_proofs_no_audit_returns_phase_4(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=4)
        assert detect_phase_from_files(d) == (4, 1, 1)

    def test_audit_failed_no_fork_returns_phase_5(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=5, audit_result="fail")
        phase, lemma, iteration = detect_phase_from_files(d)
        assert phase == 5
        assert iteration == 1

    def test_audit_failed_with_fork_returns_phase_6(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=6, audit_result="fail")
        phase, lemma, iteration = detect_phase_from_files(d)
        assert phase == 6

    def test_revision_done_skips_lemma(self, proof_dir_at_phase, audit_fail_md):
        d = proof_dir_at_phase(phase=5, audit_result="fail")
        # Simulate revision: update proof_lemma_1 to iteration 2
        proof = (d / "proof_lemma_1.md").read_text(encoding="utf-8")
        proof = proof.replace("Iteration: 1", "Iteration: 2")
        (d / "proof_lemma_1.md").write_text(proof, encoding="utf-8")
        # Lemma 1 is revised, so detection should move to lemma 2
        phase, lemma, iteration = detect_phase_from_files(d)
        assert lemma == 2

    def test_all_audits_pass_returns_phase_8(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=5, audit_result="pass")
        assert detect_phase_from_files(d) == (8, 0, 0)

    def test_cold_read_done_returns_phase_8(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=8)
        (d / "cold_read_audit.md").write_text("Clean pass ✅", encoding="utf-8")
        assert detect_phase_from_files(d) == (8, 0, 0)

    def test_final_proof_exists_returns_done(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=9)
        assert detect_phase_from_files(d) == (9, 0, 0)


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
        state.set("current_phase", 3)
        state.set("phase_status", "in_progress")
        state.save()

        state2 = OrchestratorState(proof_dir)
        assert state2.get("current_phase") == 3
        assert state2.get("phase_status") == "in_progress"

    def test_corrupt_state_file_returns_empty(self, proof_dir):
        (proof_dir / "orchestrator_state.json").write_text("not json!", encoding="utf-8")
        state = OrchestratorState(proof_dir)
        assert state.data == {}


# ===== 1.8 Lemma dependency parsing =====

class TestDependencyParsing:
    def test_depends_on_lemmas(self, proof_dir, setup_md):
        (proof_dir / "00_setup.md").write_text(setup_md, encoding="utf-8")
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
        # Note: the simple regex fallback won't handle this,
        # but the direct json.loads will
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
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `cd "C:/Users/wjzhong/OneDrive - Stanford/claude-skills/rigorous-proof" && python -m pytest tests/test_orchestrate.py -v`

Expected: All tests pass

---

### Task 3: Mock-Based Orchestrator Tests

**Files:**
- Modify: `tests/test_orchestrate.py` (append new test classes)

These tests monkeypatch `invoke_claude` to test orchestrator flow without API calls.

- [ ] **Step 1: Add mock invoke_claude and resume tests to test_orchestrate.py**

Append to `tests/test_orchestrate.py`:

```python
from unittest.mock import patch, MagicMock
from orchestrate import (
    ProofOrchestrator,
    prompt_user_fork_decision,
    invoke_claude as real_invoke_claude,
    FORK_TIMEOUT,
)


def make_mock_invoke(proof_dir, audit_result="pass"):
    """
    Return a mock invoke_claude that writes expected files based on prompt content.
    """
    call_count = {"n": 0}

    def mock_invoke(prompt, system_prompt=None):
        call_count["n"] += 1

        if "Decomposition" in prompt:
            (proof_dir / "01_decomposition.md").write_text("""\
**Lemma 1**: First claim.
- Depends on: H1
- Why needed: Foundation.

**Lemma 2**: Second claim.
- Depends on: Lemma 1
- Why needed: Main result.
""", encoding="utf-8")
            return '{"lemma_count": 2, "lemmas": ["First claim", "Second claim"]}'

        if "Prove Lemma" in prompt:
            import re
            m = re.search(r"Lemma\s+(\d+)", prompt)
            k = m.group(1) if m else "1"
            iter_m = re.search(r"iteration.*?(\d+)", prompt, re.IGNORECASE)
            iteration = iter_m.group(1) if iter_m else "1"
            (proof_dir / f"proof_lemma_{k}.md").write_text(f"""\
## Lemma {k} — Test claim
Status: DRAFT
Iteration: {iteration}
Gaps: none

Step 1. Test step. [Hypothesis H1]
""", encoding="utf-8")
            return f'{{"lemma": {k}, "steps": 1, "status": "DRAFT", "gaps": []}}'

        if "hostile referee" in prompt or "hostile mathematical referee" in prompt:
            import re
            m = re.search(r"proof_lemma_(\d+)", prompt)
            k = m.group(1) if m else "1"
            iter_m = re.search(r"iter_(\d+)", prompt)
            iteration = iter_m.group(1) if iter_m else "1"

            if audit_result == "pass":
                content = "\n".join(
                    f"{i}. Check: ✅" for i in range(1, 7)
                )
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

        if "Gap Analysis" in prompt:
            import re
            m = re.search(r"Lemma\s+(\d+)", prompt)
            k = m.group(1) if m else "1"
            (proof_dir / f"fork_lemma_{k}_gap_1.md").write_text(
                f"## Gap Analysis: Lemma {k}, Gap 1\nTest gap.", encoding="utf-8"
            )
            return f'{{"lemma": {k}, "fixable": 1, "crucial": 0, "fatal": 0, "fork_files": []}}'

        if "Revise" in prompt:
            import re
            m = re.search(r"Lemma\s+(\d+)", prompt)
            k = m.group(1) if m else "1"
            iter_m = re.search(r"next_iteration.*?(\d+)", prompt, re.IGNORECASE)
            if not iter_m:
                iter_m = re.search(r"Iteration:\s*(\d+)", prompt)
            next_iter = iter_m.group(1) if iter_m else "2"
            (proof_dir / f"proof_lemma_{k}.md").write_text(f"""\
## Lemma {k} — Test claim
Status: REVISED
Iteration: {next_iter}
Gaps: none

Step 1. Revised step. [Hypothesis H1]
""", encoding="utf-8")
            return f'{{"lemma": {k}, "iteration": {next_iter}, "steps_changed": 1, "all_issues_addressed": true}}'

        if "Compile" in prompt or "compiled" in prompt.lower():
            (proof_dir / "assembled_proof_order.md").write_text(
                "proof_lemma_1.md\nproof_lemma_2.md", encoding="utf-8"
            )
            return '{"lemma_count": 2, "lemma_files": ["proof_lemma_1.md", "proof_lemma_2.md"]}'

        if "cold read" in prompt.lower():
            (proof_dir / "cold_read_audit.md").write_text(
                "Cold read: all checks pass. ✅", encoding="utf-8"
            )
            return '{"clean_pass": true, "issues_found": 0, "issues_fixed": 0, "unresolved_critical": 0}'

        if "final proof" in prompt.lower():
            (proof_dir / "final_proof.md").write_text(
                "## Final Proof\n\nStep 1. ... [Hypothesis H1]\n\n∎", encoding="utf-8"
            )
            return '{"complete": true, "unresolved_gaps": 0}'

        if "journal" in prompt.lower():
            (proof_dir / "proof_journal.md").write_text(
                "## Proof Journal\n\nFull audit trail.", encoding="utf-8"
            )
            return '{"sections": 7, "has_unresolved_gaps": false}'

        return '{"status": "unknown prompt"}'

    return mock_invoke


# ===== 1.2 & 1.3 Resume tests =====

class TestResume:
    def test_resume_stale_heartbeat_restarts_phase(self, proof_dir_at_phase,
                                                     write_state, stale_heartbeat):
        d = proof_dir_at_phase(phase=3)
        write_state({
            "current_phase": 3,
            "current_lemma": 2,
            "current_iteration": 1,
            "phase_status": "in_progress",
            "heartbeat": stale_heartbeat,
        })
        orch = ProofOrchestrator(d.parent)
        phase, lemma, iteration = orch._detect_resume_point()
        assert phase == 3
        assert lemma == 2

    def test_resume_done_advances_to_next(self, proof_dir_at_phase, write_state):
        d = proof_dir_at_phase(phase=4)  # has proofs, no audits
        write_state({
            "current_phase": 3,
            "phase_status": "done",
        })
        orch = ProofOrchestrator(d.parent)
        phase, lemma, iteration = orch._detect_resume_point()
        # State says 3 done, files show proofs exist but no audits → phase 4
        assert phase == 4


# ===== 1.5 Full phase progression (mock) =====

class TestFullProgression:
    def test_full_run_creates_all_files(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=2)  # starts with 00_setup.md only
        mock = make_mock_invoke(d, audit_result="pass")

        with patch("orchestrate.invoke_claude", side_effect=mock):
            orch = ProofOrchestrator(d.parent, max_effort=False)
            orch.run()

        # All expected files should exist
        assert (d / "01_decomposition.md").exists()
        assert (d / "proof_lemma_1.md").exists()
        assert (d / "proof_lemma_2.md").exists()
        assert (d / "audit_lemma_1_iter_1.md").exists()
        assert (d / "audit_lemma_2_iter_1.md").exists()
        assert (d / "cold_read_audit.md").exists()
        assert (d / "final_proof.md").exists()
        assert (d / "proof_journal.md").exists()

    def test_state_tracks_progression(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=2)
        mock = make_mock_invoke(d, audit_result="pass")

        with patch("orchestrate.invoke_claude", side_effect=mock):
            orch = ProofOrchestrator(d.parent, max_effort=False)
            orch.run()

        state = json.loads((d / "orchestrator_state.json").read_text(encoding="utf-8"))
        assert state["phase_status"] == "done"


# ===== 1.6 Fork timeout =====

class TestForkTimeout:
    def test_timeout_returns_b_auto(self):
        # Use a very short timeout; no stdin available in test
        choice, was_auto = prompt_user_fork_decision("Test gap", timeout=1)
        assert choice == "B"
        assert was_auto is True


# ===== 1.7 Iteration cap =====

class TestIterationCap:
    def test_max_3_iterations(self, proof_dir_at_phase):
        d = proof_dir_at_phase(phase=4)  # has proofs, needs audit
        mock = make_mock_invoke(d, audit_result="fail")

        with patch("orchestrate.invoke_claude", side_effect=mock):
            orch = ProofOrchestrator(d.parent, max_effort=True)
            orch.lemma_count = 2
            orch._run_audit_loop(start_lemma=1, start_iteration=1)

        # Should have audit files for iterations 1, 2, 3 but not 4
        assert (d / "audit_lemma_1_iter_1.md").exists()
        assert (d / "audit_lemma_1_iter_2.md").exists()
        assert (d / "audit_lemma_1_iter_3.md").exists()
        assert not (d / "audit_lemma_1_iter_4.md").exists()
```

- [ ] **Step 2: Run all tests**

Run: `cd "C:/Users/wjzhong/OneDrive - Stanford/claude-skills/rigorous-proof" && python -m pytest tests/test_orchestrate.py -v`

Expected: All tests pass

---

### Task 4: Compliance Test Scaffolding

**Files:**
- Create: `tests/test_compliance.py`

These tests dispatch real Claude agents. They are expensive and slow — marked with `@pytest.mark.compliance` so they can be run selectively.

- [ ] **Step 1: Write test_compliance.py**

```python
"""
Layer 2: SKILL.md compliance tests using real Claude agents.

These tests invoke `claude -p` with the rigorous-proof skill loaded
and inspect proof_work/ outputs for compliance.

Run with: pytest tests/test_compliance.py -v -m compliance --timeout=1800
"""

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).parent.parent
SKILL_FILE = SKILL_DIR / "SKILL.md"

# All compliance tests are slow and cost money
pytestmark = [pytest.mark.compliance, pytest.mark.slow]

BANNED_PHRASES = [
    "clearly",
    "obviously",
    "trivially",
    "it is easy to see",
    "by a standard argument",
]

JUSTIFICATION_TAGS = re.compile(
    r"\["
    r"(?:Hypothesis\s+H\d+|Definition\s+of\s+\w+|Theorem:\s+.+?|"
    r"By\s+Step\s+\d+|By\s+Lemma\s+\d+|Algebraic\s+manipulation|"
    r"Logic:\s+.+?|⚠️\s*GAP)"
    r"\]"
)


def run_proof_inline(proposition: str, hypotheses: str | None, phases: str,
                     work_dir: Path, max_effort: bool = False) -> str:
    """
    Run the rigorous-proof skill inline via claude -p.
    Returns Claude's output text.
    """
    prompt_parts = [f"prove {proposition} inline"]
    if max_effort:
        prompt_parts[0] = f"prove {proposition} inline with max effort"
    if hypotheses:
        prompt_parts.append(f"\nHypotheses (use ONLY these, do not add others):\n{hypotheses}")
    prompt_parts.append(f"\nRun through {phases}. Working directory: {work_dir}")

    prompt = "\n".join(prompt_parts)
    skill_text = SKILL_FILE.read_text(encoding="utf-8")

    cmd = [
        "claude", "-p",
        "--model", "opus",
        "--output-format", "json",
        "--append-system-prompt", skill_text,
        prompt,
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8",
        timeout=900,  # 15 min per test
    )

    output = result.stdout.strip()
    try:
        parsed = json.loads(output)
        if isinstance(parsed, dict) and "result" in parsed:
            return parsed["result"]
    except (json.JSONDecodeError, TypeError):
        pass
    return output


class TestJustificationDiscipline:
    """2.1: Every step must have a justification tag, no banned phrases."""

    def test_convergent_sequence_bounded(self, tmp_path):
        proof_dir = tmp_path / "proof_work"
        proof_dir.mkdir()

        run_proof_inline(
            proposition="every convergent sequence in R is bounded",
            hypotheses=None,
            phases="Phases 0-3",
            work_dir=tmp_path,
        )

        # Check all proof_lemma files
        proof_files = list(proof_dir.glob("proof_lemma_*.md"))
        assert len(proof_files) > 0, "No proof lemma files created"

        for pf in proof_files:
            content = pf.read_text(encoding="utf-8")

            # No banned phrases
            for phrase in BANNED_PHRASES:
                assert phrase.lower() not in content.lower(), (
                    f"Banned phrase '{phrase}' found in {pf.name}"
                )

            # Every "Step N." line should have a justification tag
            step_lines = re.findall(r"^Step\s+\d+\..*$", content, re.MULTILINE)
            for line in step_lines:
                assert JUSTIFICATION_TAGS.search(line), (
                    f"Step missing justification tag in {pf.name}: {line[:80]}"
                )


class TestGapHonesty:
    """2.2: Insufficient hypotheses must trigger gaps or audit failures."""

    def test_measurable_not_continuous(self, tmp_path):
        proof_dir = tmp_path / "proof_work"
        proof_dir.mkdir()

        run_proof_inline(
            proposition="every continuous function on [0,1] is uniformly continuous",
            hypotheses="H1: f: [0,1] → R is measurable",
            phases="Phases 0-4",
            work_dir=tmp_path,
        )

        # Check for gap markers in proofs OR audit failures
        proof_files = list(proof_dir.glob("proof_lemma_*.md"))
        audit_files = list(proof_dir.glob("audit_lemma_*_iter_*.md"))

        has_gap_marker = any(
            "⚠️ GAP" in f.read_text(encoding="utf-8") for f in proof_files
        )
        has_audit_failure = any(
            "❌" in f.read_text(encoding="utf-8") for f in audit_files
        )

        assert has_gap_marker or has_audit_failure, (
            "Neither gap markers nor audit failures found — "
            "Claude silently strengthened hypotheses"
        )

        # Setup should not contain "continuous" as a hypothesis
        setup = (proof_dir / "00_setup.md").read_text(encoding="utf-8")
        # Find the hypotheses section
        hyp_match = re.search(
            r"##\s*Hypotheses(.*?)(?=##|\Z)", setup, re.DOTALL
        )
        if hyp_match:
            hyp_text = hyp_match.group(1)
            # "continuous" should not appear as a stated hypothesis
            # (it may appear in the proposition or discussion, that's OK)
            h_lines = [l for l in hyp_text.split("\n") if l.strip().startswith("H")]
            for line in h_lines:
                assert "continuous" not in line.lower() or "measurable" in line.lower(), (
                    f"Hypothesis silently strengthened: {line}"
                )


class TestHonestFinalReporting:
    """2.3: Unresolved cold-read gaps must be reported prominently."""

    def test_bolzano_weierstrass_without_completeness(self, tmp_path):
        proof_dir = tmp_path / "proof_work"
        proof_dir.mkdir()

        run_proof_inline(
            proposition=(
                "the Bolzano-Weierstrass theorem: every bounded sequence "
                "in R has a convergent subsequence"
            ),
            hypotheses=(
                "H1: (a_n) is a sequence of real numbers\n"
                "H2: There exist real numbers L, U such that L <= a_n <= U for all n\n"
                "H3: R is an ordered field\n"
                "NOTE: Do NOT assume completeness or the least upper bound property."
            ),
            phases="Phases 0-8",
            work_dir=tmp_path,
            max_effort=True,
        )

        # Either the proof caught the gap early (fork) or cold read found it
        cold_read = proof_dir / "cold_read_audit.md"
        final_proof = proof_dir / "final_proof.md"
        journal = proof_dir / "proof_journal.md"
        fork_files = list(proof_dir.glob("fork_lemma_*_gap_*.md"))

        if cold_read.exists():
            cold_text = cold_read.read_text(encoding="utf-8")
            if "[UNRESOLVED CRITICAL GAP]" in cold_text:
                # Verify honest reporting
                if final_proof.exists():
                    fp_text = final_proof.read_text(encoding="utf-8")
                    assert "UNRESOLVED GAPS" in fp_text, (
                        "final_proof.md missing UNRESOLVED GAPS section"
                    )
                    assert "∎" not in fp_text or "□" in fp_text, (
                        "final_proof.md claims complete (∎) despite unresolved gaps"
                    )

                if journal.exists():
                    j_text = journal.read_text(encoding="utf-8")
                    # Gaps should be near the top
                    gap_pos = j_text.lower().find("unresolved")
                    setup_pos = j_text.lower().find("## setup") if "## setup" in j_text.lower() else j_text.lower().find("## proposition")
                    if gap_pos >= 0 and setup_pos >= 0:
                        assert gap_pos < setup_pos, (
                            "Unresolved gaps not at TOP of journal"
                        )

        # If gaps were caught early via fork, that's also acceptable
        if fork_files:
            any_fork_mentions_completeness = any(
                "completeness" in f.read_text(encoding="utf-8").lower()
                or "least upper bound" in f.read_text(encoding="utf-8").lower()
                or "lub" in f.read_text(encoding="utf-8").lower()
                for f in fork_files
            )
            # At least one fork should identify the missing assumption
            assert any_fork_mentions_completeness or (
                cold_read.exists() and "[UNRESOLVED CRITICAL GAP]" in cold_read.read_text(encoding="utf-8")
            ), "Neither fork nor cold read identified the completeness gap"


class TestForkTimeoutCompliance:
    """2.4: Fork timeout defaults to B after 600s."""

    # This is tested more practically in Layer 1 (test_orchestrate.py)
    # with a short timeout. The compliance version would need the full
    # orchestrator running with real Claude, which is covered in Layer 3.
    # Here we just verify the SKILL.md text is correct.

    def test_skill_documents_timeout(self):
        skill_text = SKILL_FILE.read_text(encoding="utf-8")
        assert "600 seconds" in skill_text
        assert "(default if no response)" in skill_text
        assert "auto-selected after 600s timeout" in skill_text


class TestQuantifierRigor:
    """2.5: MVT preconditions must be verified as sub-steps."""

    def test_differentiable_positive_derivative_increasing(self, tmp_path):
        proof_dir = tmp_path / "proof_work"
        proof_dir.mkdir()

        run_proof_inline(
            proposition=(
                "if f: R→R is differentiable and f'(x) > 0 for all x in R, "
                "then f is strictly increasing"
            ),
            hypotheses=None,
            phases="Phases 0-4",
            work_dir=tmp_path,
        )

        proof_files = list(proof_dir.glob("proof_lemma_*.md"))
        assert len(proof_files) > 0, "No proof lemma files created"

        all_content = "\n".join(
            f.read_text(encoding="utf-8") for f in proof_files
        )

        # MVT should be invoked with proper tag
        assert re.search(
            r"\[Theorem:.*Mean Value Theorem.*\]", all_content, re.IGNORECASE
        ), "MVT not invoked with [Theorem: ...] tag"

        # Check audit passed on quantifiers (check 5)
        audit_files = list(proof_dir.glob("audit_lemma_*_iter_*.md"))
        if audit_files:
            latest_audit = sorted(audit_files)[-1]
            audit_text = latest_audit.read_text(encoding="utf-8")
            # Find check 5 line
            check5_match = re.search(r"5\..*?(✅|❌)", audit_text)
            if check5_match:
                assert check5_match.group(1) == "✅", (
                    "Quantifier check (check 5) failed in audit"
                )
```

- [ ] **Step 2: Verify the file compiles (don't run — costs money)**

Run: `cd "C:/Users/wjzhong/OneDrive - Stanford/claude-skills/rigorous-proof" && python -m py_compile tests/test_compliance.py && echo OK`

Expected: `OK`

---

### Task 5: End-to-End Test

**Files:**
- Create: `tests/test_e2e.py`

- [ ] **Step 1: Write test_e2e.py**

```python
"""
Layer 3: End-to-end integration test with real Claude.

Runs the full orchestrator on a simple proposition.

Run with: pytest tests/test_e2e.py -v -m e2e --timeout=3600
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"

pytestmark = [pytest.mark.e2e, pytest.mark.slow]


@pytest.fixture
def e2e_proof_dir(tmp_path):
    """Set up proof_work/ with a pre-written 00_setup.md for sqrt(2) irrationality."""
    proof_dir = tmp_path / "proof_work"
    proof_dir.mkdir()

    (proof_dir / "00_setup.md").write_text("""\
## Proposition
√2 is irrational. That is, there do not exist integers p, q with q ≠ 0 such that (p/q)² = 2.

## Hypotheses
H1: p, q are integers with q ≠ 0
H2: gcd(p, q) = 1 (fraction in lowest terms)

## Definitions
Irrational: A real number r is irrational if there do not exist integers p, q (q ≠ 0) such that r = p/q.
Even: An integer n is even if there exists an integer k such that n = 2k.
Odd: An integer n is odd if there exists an integer k such that n = 2k + 1.

## Strategy
Proof by contradiction. Assume √2 = p/q in lowest terms, derive that both p and q must be even, contradicting gcd(p,q) = 1.

## Known Results Used
- Every integer is either even or odd (parity).
- If n² is even, then n is even (can be proved as lemma or assumed).
""", encoding="utf-8")

    return tmp_path


class TestEndToEnd:
    def test_full_orchestrated_run(self, e2e_proof_dir):
        """Run the full orchestrator and verify all outputs."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "orchestrate.py"),
                "--max-effort",
                "--work-dir", str(e2e_proof_dir),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=3600,
        )

        proof_dir = e2e_proof_dir / "proof_work"

        # Orchestrator should succeed
        assert result.returncode == 0, f"Orchestrator failed:\n{result.stderr}"

        # All expected files created
        assert (proof_dir / "01_decomposition.md").exists(), "Missing decomposition"
        assert len(list(proof_dir.glob("proof_lemma_*.md"))) > 0, "No proof lemmas"
        assert len(list(proof_dir.glob("audit_lemma_*_iter_*.md"))) > 0, "No audits"
        assert (proof_dir / "cold_read_audit.md").exists(), "Missing cold read"
        assert (proof_dir / "final_proof.md").exists(), "Missing final proof"
        assert (proof_dir / "proof_journal.md").exists(), "Missing journal"

        # Final proof should be complete (this is a well-known proof)
        final = (proof_dir / "final_proof.md").read_text(encoding="utf-8")
        assert "∎" in final, "Final proof missing tombstone (∎)"

        # State file should show completion
        state_file = proof_dir / "orchestrator_state.json"
        assert state_file.exists(), "Missing state file"
        state = json.loads(state_file.read_text(encoding="utf-8"))
        assert state.get("phase_status") == "done"

        # Proof health should be present
        assert "Proof Health" in final or "Iterations:" in final, (
            "Missing proof health in final proof"
        )

        # Stdout should contain full agent summaries (not just log lines)
        assert "---" in result.stdout, (
            "Orchestrator stdout missing agent output separators"
        )

        # Journal should contain all sections
        journal = (proof_dir / "proof_journal.md").read_text(encoding="utf-8")
        assert "setup" in journal.lower() or "proposition" in journal.lower()
        assert "audit" in journal.lower()
```

- [ ] **Step 2: Verify the file compiles**

Run: `cd "C:/Users/wjzhong/OneDrive - Stanford/claude-skills/rigorous-proof" && python -m py_compile tests/test_e2e.py && echo OK`

Expected: `OK`

---

### Task 6: pytest Configuration

**Files:**
- Create: `tests/__init__.py`
- Create: `pyproject.toml` (or append pytest config)

- [ ] **Step 1: Create tests/__init__.py**

Empty file to make tests a package:

```python
```

- [ ] **Step 2: Create pyproject.toml with pytest markers**

```toml
[tool.pytest.ini_options]
markers = [
    "compliance: SKILL.md compliance tests using real Claude (expensive)",
    "e2e: end-to-end integration tests (very expensive)",
    "slow: tests that take more than 30 seconds",
]
testpaths = ["tests"]
```

- [ ] **Step 3: Run Layer 1 tests to verify everything works**

Run: `cd "C:/Users/wjzhong/OneDrive - Stanford/claude-skills/rigorous-proof" && python -m pytest tests/test_orchestrate.py -v`

Expected: All tests pass

---
