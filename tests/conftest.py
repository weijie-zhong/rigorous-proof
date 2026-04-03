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
def user_input_md():
    """Realistic 00_user_input.md content."""
    return """\
Prove that for all n in N, if n^2 is even then n is even.
"""


@pytest.fixture
def distilled_md():
    """Realistic 00_distilled.md content."""
    return """\
## Proposition
For all n in N, if n^2 is even then n is even.

## Hypotheses
H1: n is a natural number
H2: n^2 is even

## Definitions
Even: An integer k is even if there exists an integer m such that k = 2m.

## Difficulty assessment: **moderate**
Standard result, provable by contradiction via the contrapositive.
"""


@pytest.fixture
def strategy_md():
    """Realistic 00_strategy.md content."""
    return """\
## Proof Strategy
Proof by contradiction via the contrapositive.

## Known Results Used
- Division algorithm

## Key Insights
If n is odd, then n^2 is odd — the contrapositive of the target.
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
def proof_dir_at_phase(proof_dir, user_input_md, distilled_md, strategy_md,
                        decomposition_md, proof_lemma_md,
                        audit_pass_md, audit_fail_md):
    """
    Factory fixture: populate proof_dir to simulate being at a given phase.
    Returns a function: populate(phase, lemma_count=2, audit_result="pass")

    Phase mapping:
      0  — empty (no user input yet)
      1  — has 00_user_input.md
      3  — has 00_distilled.md (+ 00_strategy.md / 01_decomposition.md at phase 4+)
      4  — has decomposition + all proof lemmas
      5  — has all proofs, no audits
      6  — has audits (pass or fail)
      7  — has fork files (if audit failed)
      9  — has cold_read_audit.md
      10 — has final_proof.md
    """
    def populate(phase, lemma_count=2, audit_result="pass"):
        # Phase 0: empty
        if phase <= 0:
            return proof_dir

        # Phase 1+: write user input
        (proof_dir / "00_user_input.md").write_text(user_input_md, encoding="utf-8")

        if phase <= 1:
            return proof_dir

        # Phase 3+: write distilled + strategy
        (proof_dir / "00_distilled.md").write_text(distilled_md, encoding="utf-8")
        (proof_dir / "00_strategy.md").write_text(strategy_md, encoding="utf-8")

        if phase <= 3:
            return proof_dir

        # Phase 4+: write decomposition
        (proof_dir / "01_decomposition.md").write_text(decomposition_md, encoding="utf-8")

        if phase <= 4:
            return proof_dir

        # Phase 5+: write all proof lemmas
        for k in range(1, lemma_count + 1):
            content = proof_lemma_md.replace("Lemma 1", f"Lemma {k}")
            (proof_dir / f"proof_lemma_{k}.md").write_text(content, encoding="utf-8")

        if phase <= 5:
            return proof_dir

        # Phase 6+: write audits
        audit = audit_pass_md if audit_result == "pass" else audit_fail_md
        for k in range(1, lemma_count + 1):
            content = audit.replace("Lemma 1", f"Lemma {k}")
            (proof_dir / f"audit_lemma_{k}_iter_1.md").write_text(content, encoding="utf-8")

        if phase <= 6:
            return proof_dir

        # Phase 7+: write fork files (if audit failed)
        if audit_result == "fail":
            for k in range(1, lemma_count + 1):
                (proof_dir / f"fork_lemma_{k}_gap_1.md").write_text(
                    f"## Gap Analysis: Lemma {k}, Gap 1\n\n### The gap\nTest gap.",
                    encoding="utf-8",
                )

        if phase <= 9:
            return proof_dir

        # Phase 9+: write cold read and final
        if phase >= 9:
            (proof_dir / "cold_read_audit.md").write_text(
                "Cold read: all checks pass. ✅", encoding="utf-8"
            )

        if phase >= 10:
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
