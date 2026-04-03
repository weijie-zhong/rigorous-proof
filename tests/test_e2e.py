"""
Layer 3: End-to-end integration test with real Claude.

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
    """Set up proof_work/ with 00_user_input.md for sqrt(2) irrationality."""
    proof_dir = tmp_path / "proof_work"
    proof_dir.mkdir()

    (proof_dir / "00_user_input.md").write_text("""\
Prove that sqrt(2) is irrational. That is, there do not exist integers p, q
with q != 0 such that (p/q)^2 = 2.

Hint: Use proof by contradiction. Assume sqrt(2) = p/q in lowest terms,
derive that both p and q must be even, contradicting gcd(p,q) = 1.
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

        assert result.returncode == 0, f"Orchestrator failed:\n{result.stderr}"

        assert (proof_dir / "00_distilled.md").exists(), "Missing distilled problem"
        assert (proof_dir / "00_strategy.md").exists(), "Missing strategy"
        assert (proof_dir / "01_decomposition.md").exists(), "Missing decomposition"
        assert len(list(proof_dir.glob("proof_lemma_*.md"))) > 0, "No proof lemmas"
        assert len(list(proof_dir.glob("audit_lemma_*_iter_*.md"))) > 0, "No audits"
        assert (proof_dir / "cold_read_audit.md").exists(), "Missing cold read"
        assert (proof_dir / "final_proof.md").exists(), "Missing final proof"
        assert (proof_dir / "proof_journal.md").exists(), "Missing journal"

        final = (proof_dir / "final_proof.md").read_text(encoding="utf-8")
        assert "∎" in final, "Final proof missing tombstone"

        state_file = proof_dir / "orchestrator_state.json"
        assert state_file.exists(), "Missing state file"
        state = json.loads(state_file.read_text(encoding="utf-8"))
        assert state.get("phase_status") == "done"

        journal = (proof_dir / "proof_journal.md").read_text(encoding="utf-8")
        assert "distill" in journal.lower() or "proposition" in journal.lower()
        assert "audit" in journal.lower()
