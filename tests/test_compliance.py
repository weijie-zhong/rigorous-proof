"""
Layer 2: SKILL.md compliance tests using real Claude agents.

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
    skill_text = SKILL_FILE.read_text(encoding="utf-8")
    prompt_parts = [f"prove {proposition} inline"]
    if max_effort:
        prompt_parts[0] = f"prove {proposition} inline with max effort"
    if hypotheses:
        prompt_parts.append(f"\nHypotheses (use ONLY these, do not add others):\n{hypotheses}")
    prompt_parts.append(f"\nRun through {phases}. Working directory: {work_dir}")

    prompt = "\n".join(prompt_parts)

    cmd = [
        "claude", "-p",
        "--model", "opus",
        "--output-format", "json",
        "--append-system-prompt", skill_text,
        prompt,
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8",
        timeout=900, cwd=work_dir,
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
            phases="Phases 0-5",
            work_dir=tmp_path,
        )

        proof_files = list(proof_dir.glob("proof_lemma_*.md"))
        assert len(proof_files) > 0, "No proof lemma files created"

        for pf in proof_files:
            content = pf.read_text(encoding="utf-8")

            for phrase in BANNED_PHRASES:
                assert phrase.lower() not in content.lower(), (
                    f"Banned phrase '{phrase}' found in {pf.name}"
                )

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
            phases="Phases 0-5",
            work_dir=tmp_path,
        )

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
            phases="Phases 0-9",
            work_dir=tmp_path,
            max_effort=True,
        )

        cold_read = proof_dir / "cold_read_audit.md"
        final_proof = proof_dir / "final_proof.md"
        journal = proof_dir / "proof_journal.md"
        fork_files = list(proof_dir.glob("fork_lemma_*_gap_*.md"))

        if cold_read.exists():
            cold_text = cold_read.read_text(encoding="utf-8")
            if "[UNRESOLVED CRITICAL GAP]" in cold_text:
                if final_proof.exists():
                    fp_text = final_proof.read_text(encoding="utf-8")
                    assert "UNRESOLVED GAPS" in fp_text, (
                        "final_proof.md missing UNRESOLVED GAPS section"
                    )
                    assert "∎" not in fp_text or "□" in fp_text, (
                        "final_proof.md claims complete despite unresolved gaps"
                    )

                if journal.exists():
                    j_text = journal.read_text(encoding="utf-8")
                    gap_pos = j_text.lower().find("unresolved")
                    setup_pos = j_text.lower().find("## setup") if "## setup" in j_text.lower() else j_text.lower().find("## proposition")
                    if gap_pos >= 0 and setup_pos >= 0:
                        assert gap_pos < setup_pos, "Unresolved gaps not at TOP of journal"

        if fork_files:
            any_fork_mentions_completeness = any(
                "completeness" in f.read_text(encoding="utf-8").lower()
                or "least upper bound" in f.read_text(encoding="utf-8").lower()
                or "lub" in f.read_text(encoding="utf-8").lower()
                for f in fork_files
            )
            assert any_fork_mentions_completeness or (
                cold_read.exists() and "[UNRESOLVED CRITICAL GAP]" in cold_read.read_text(encoding="utf-8")
            ), "Neither fork nor cold read identified the completeness gap"


class TestForkTimeoutCompliance:
    """2.4: Verify SKILL.md documents the timeout correctly."""

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
            phases="Phases 0-5",
            work_dir=tmp_path,
        )

        proof_files = list(proof_dir.glob("proof_lemma_*.md"))
        assert len(proof_files) > 0, "No proof lemma files created"

        all_content = "\n".join(
            f.read_text(encoding="utf-8") for f in proof_files
        )

        assert re.search(
            r"\[Theorem:.*Mean Value Theorem.*\]", all_content, re.IGNORECASE
        ), "MVT not invoked with [Theorem: ...] tag"

        audit_files = list(proof_dir.glob("audit_lemma_*_iter_*.md"))
        if audit_files:
            latest_audit = sorted(audit_files)[-1]
            audit_text = latest_audit.read_text(encoding="utf-8")
            check5_match = re.search(r"5\..*?(✅|❌)", audit_text)
            if check5_match:
                assert check5_match.group(1) == "✅", "Quantifier check failed in audit"
