"""Tests for ContextBuilder (cached system-prompt blob)."""

import os
import sys
import time
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from context import ContextBuilder, STATUS_LOG_KEEP


def _bump_mtime(path: Path) -> None:
    """Force a measurable mtime change even on coarse filesystems."""
    st = path.stat()
    new_time = st.st_mtime + 5
    os.utime(path, (new_time, new_time))


class TestSystemPromptContent:
    def test_includes_all_stable_files_when_present(self, proof_dir, distilled_md,
                                                     strategy_md, decomposition_md):
        (proof_dir / "00_distilled.md").write_text(distilled_md, encoding="utf-8")
        (proof_dir / "00_strategy.md").write_text(strategy_md, encoding="utf-8")
        (proof_dir / "01_decomposition.md").write_text(decomposition_md, encoding="utf-8")

        cb = ContextBuilder(proof_dir)
        prompt = cb.system_prompt()

        assert "<distilled_problem>" in prompt
        assert "</distilled_problem>" in prompt
        assert "<proof_strategy>" in prompt
        assert "</proof_strategy>" in prompt
        assert "<lemma_decomposition>" in prompt
        assert "</lemma_decomposition>" in prompt
        # Content from each file appears
        assert "n^2 is even" in prompt or "n^2 even" in prompt.lower()
        assert "contradiction" in prompt.lower()
        assert "Lemma 1" in prompt and "Lemma 2" in prompt

    def test_omits_missing_files(self, proof_dir, distilled_md):
        (proof_dir / "00_distilled.md").write_text(distilled_md, encoding="utf-8")
        cb = ContextBuilder(proof_dir)
        prompt = cb.system_prompt()
        assert "<distilled_problem>" in prompt
        assert "<proof_strategy>" not in prompt
        assert "<lemma_decomposition>" not in prompt
        assert "<recent_status_log>" not in prompt

    def test_no_files_returns_preamble_only(self, proof_dir):
        cb = ContextBuilder(proof_dir)
        prompt = cb.system_prompt()
        # Preamble appears, no blocks, no footer
        assert "rigorous mathematical proof workflow" in prompt
        assert "<distilled_problem>" not in prompt
        assert "do NOT re-read" not in prompt

    def test_footer_appears_when_any_block_present(self, proof_dir, distilled_md):
        (proof_dir / "00_distilled.md").write_text(distilled_md, encoding="utf-8")
        cb = ContextBuilder(proof_dir)
        prompt = cb.system_prompt()
        assert "do NOT re-read" in prompt


class TestVersioning:
    def test_version_starts_at_zero_then_bumps_on_first_build(self, proof_dir):
        cb = ContextBuilder(proof_dir)
        assert cb.version() == 0
        cb.system_prompt()
        assert cb.version() == 1

    def test_version_stable_when_files_unchanged(self, proof_dir, distilled_md):
        (proof_dir / "00_distilled.md").write_text(distilled_md, encoding="utf-8")
        cb = ContextBuilder(proof_dir)
        cb.system_prompt()
        v1 = cb.version()
        cb.system_prompt()
        cb.system_prompt()
        assert cb.version() == v1

    def test_version_bumps_on_mtime_change(self, proof_dir, distilled_md):
        f = proof_dir / "00_distilled.md"
        f.write_text(distilled_md, encoding="utf-8")
        cb = ContextBuilder(proof_dir)
        cb.system_prompt()
        v1 = cb.version()
        _bump_mtime(f)
        cb.system_prompt()
        assert cb.version() == v1 + 1

    def test_version_bumps_on_new_stable_file(self, proof_dir, distilled_md, strategy_md):
        (proof_dir / "00_distilled.md").write_text(distilled_md, encoding="utf-8")
        cb = ContextBuilder(proof_dir)
        cb.system_prompt()
        v1 = cb.version()
        (proof_dir / "00_strategy.md").write_text(strategy_md, encoding="utf-8")
        cb.system_prompt()
        assert cb.version() == v1 + 1

    def test_invalidate_forces_rebuild(self, proof_dir, distilled_md):
        (proof_dir / "00_distilled.md").write_text(distilled_md, encoding="utf-8")
        cb = ContextBuilder(proof_dir)
        cb.system_prompt()
        v1 = cb.version()
        cb.invalidate()
        cb.system_prompt()
        assert cb.version() == v1 + 1

    def test_returned_string_reflects_latest_content_after_change(self, proof_dir,
                                                                    distilled_md):
        f = proof_dir / "00_distilled.md"
        f.write_text(distilled_md, encoding="utf-8")
        cb = ContextBuilder(proof_dir)
        first = cb.system_prompt()
        assert "n^2 is even" in first
        f.write_text("## Proposition\nA totally different problem.\n", encoding="utf-8")
        _bump_mtime(f)
        second = cb.system_prompt()
        assert "totally different" in second
        assert "n^2 is even" not in second


class TestStatusLogPruning:
    def _make_log(self, n_entries: int) -> str:
        lines = ["# Status Log\n"]
        for i in range(1, n_entries + 1):
            lines.append(f"## Iteration {i} — Lemma 1\n")
            lines.append(f"### What failed\nFailure {i}\n")
            lines.append(f"### Lessons for next iteration\nLesson {i}\n\n")
        return "".join(lines)

    def test_keeps_only_last_k_entries(self, proof_dir):
        log_text = self._make_log(10)
        (proof_dir / "status_log.md").write_text(log_text, encoding="utf-8")
        cb = ContextBuilder(proof_dir)
        prompt = cb.system_prompt()
        # First 5 iterations dropped; last 5 kept
        for i in range(1, 6):
            assert f"Iteration {i} —" not in prompt
        for i in range(6, 11):
            assert f"Iteration {i} —" in prompt

    def test_short_log_kept_entirely(self, proof_dir):
        log_text = self._make_log(2)
        (proof_dir / "status_log.md").write_text(log_text, encoding="utf-8")
        cb = ContextBuilder(proof_dir)
        prompt = cb.system_prompt()
        assert "Iteration 1 —" in prompt
        assert "Iteration 2 —" in prompt

    def test_exactly_k_entries_kept(self, proof_dir):
        log_text = self._make_log(STATUS_LOG_KEEP)
        (proof_dir / "status_log.md").write_text(log_text, encoding="utf-8")
        cb = ContextBuilder(proof_dir)
        prompt = cb.system_prompt()
        for i in range(1, STATUS_LOG_KEEP + 1):
            assert f"Iteration {i} —" in prompt

    def test_log_with_no_iteration_headers_kept_as_is(self, proof_dir):
        (proof_dir / "status_log.md").write_text(
            "Some unstructured text.\nNo headers.\n", encoding="utf-8"
        )
        cb = ContextBuilder(proof_dir)
        prompt = cb.system_prompt()
        assert "<recent_status_log>" in prompt
        assert "unstructured text" in prompt

    def test_empty_log_omitted(self, proof_dir):
        (proof_dir / "status_log.md").write_text("", encoding="utf-8")
        cb = ContextBuilder(proof_dir)
        prompt = cb.system_prompt()
        assert "<recent_status_log>" not in prompt


class TestThreadSafety:
    def test_concurrent_calls_all_return_same_string(self, proof_dir, distilled_md):
        import threading

        (proof_dir / "00_distilled.md").write_text(distilled_md, encoding="utf-8")
        cb = ContextBuilder(proof_dir)
        results = []
        lock = threading.Lock()

        def worker():
            r = cb.system_prompt()
            with lock:
                results.append(r)

        threads = [threading.Thread(target=worker) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 20
        assert all(r == results[0] for r in results)
        # Only one rebuild should have happened
        assert cb.version() == 1
