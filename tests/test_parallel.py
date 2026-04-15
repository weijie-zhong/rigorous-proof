"""Tests for parallel Phase 4 / Phase 5 execution."""

import sys
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from orchestrate import ProofOrchestrator


# ---------------------------------------------------------------------------
# Dependency-wave construction
# ---------------------------------------------------------------------------

def _write_decomposition(proof_dir, lemmas: list[tuple[int, list[int]]]) -> None:
    """Write a 01_decomposition.md file describing lemmas and their deps.

    Note: the dep parser greedily extracts digits from the "Depends on" line,
    so the no-deps placeholder must contain no digits.
    """
    lines = ["## Decomposition", ""]
    for k, deps in lemmas:
        dep_str = ", ".join(f"Lemma {d}" for d in deps) if deps else "(none)"
        lines.append(f"**Lemma {k}**: claim {k}.")
        lines.append(f"- Depends on: {dep_str}")
        lines.append(f"- Why needed: testing.")
        lines.append("")
    (proof_dir / "01_decomposition.md").write_text("\n".join(lines), encoding="utf-8")


class TestDependencyWaves:
    def test_linear_chain(self, proof_dir):
        # 1 → 2 → 3
        _write_decomposition(proof_dir, [(1, []), (2, [1]), (3, [2])])
        orch = ProofOrchestrator(proof_dir.parent, parallel=4)
        waves = orch._build_dependency_waves(3)
        assert waves == [[1], [2], [3]]

    def test_diamond(self, proof_dir):
        # 1, 2 deps 1, 3 deps 1, 4 deps 2 and 3
        _write_decomposition(
            proof_dir,
            [(1, []), (2, [1]), (3, [1]), (4, [2, 3])],
        )
        orch = ProofOrchestrator(proof_dir.parent, parallel=4)
        waves = orch._build_dependency_waves(4)
        assert waves == [[1], [2, 3], [4]]

    def test_all_independent(self, proof_dir):
        _write_decomposition(
            proof_dir,
            [(1, []), (2, []), (3, []), (4, [])],
        )
        orch = ProofOrchestrator(proof_dir.parent, parallel=4)
        waves = orch._build_dependency_waves(4)
        assert waves == [[1, 2, 3, 4]]

    def test_two_disjoint_chains(self, proof_dir):
        # 1 → 3, 2 → 4
        _write_decomposition(
            proof_dir,
            [(1, []), (2, []), (3, [1]), (4, [2])],
        )
        orch = ProofOrchestrator(proof_dir.parent, parallel=4)
        waves = orch._build_dependency_waves(4)
        assert waves == [[1, 2], [3, 4]]


# ---------------------------------------------------------------------------
# Phase 4 parallel dispatch
# ---------------------------------------------------------------------------

class TestPhase4Parallel:
    def test_sequential_with_parallel_one(self, proof_dir):
        _write_decomposition(proof_dir, [(1, []), (2, [1]), (3, [2])])
        orch = ProofOrchestrator(proof_dir.parent, parallel=1)
        orch.lemma_count = 3
        called = []
        with patch.object(orch, "_run_phase_4",
                          side_effect=lambda k, it: called.append(k)) as _:
            orch._run_phase_4_all(start_lemma=1, iteration=1)
        assert called == [1, 2, 3]

    def test_parallel_calls_each_lemma_once(self, proof_dir):
        _write_decomposition(
            proof_dir,
            [(1, []), (2, []), (3, []), (4, [])],
        )
        orch = ProofOrchestrator(proof_dir.parent, parallel=4)
        orch.lemma_count = 4
        called = []
        lock = threading.Lock()

        def fake(k, it):
            with lock:
                called.append(k)

        with patch.object(orch, "_run_phase_4", side_effect=fake):
            orch._run_phase_4_all(start_lemma=1, iteration=1)

        assert sorted(called) == [1, 2, 3, 4]

    def test_parallel_runs_concurrently(self, proof_dir):
        # Four independent lemmas, each fake-call sleeps 0.2s.
        # Sequential would take ~0.8s; parallel=4 should finish in ~0.3s.
        _write_decomposition(
            proof_dir,
            [(1, []), (2, []), (3, []), (4, [])],
        )
        orch = ProofOrchestrator(proof_dir.parent, parallel=4)
        orch.lemma_count = 4

        def slow(k, it):
            time.sleep(0.2)

        with patch.object(orch, "_run_phase_4", side_effect=slow):
            t0 = time.monotonic()
            orch._run_phase_4_all(start_lemma=1, iteration=1)
            elapsed = time.monotonic() - t0

        assert elapsed < 0.6, f"parallel exec took {elapsed:.2f}s — not concurrent"

    def test_parallel_resume_skips_completed_lemmas(self, proof_dir):
        _write_decomposition(
            proof_dir,
            [(1, []), (2, []), (3, []), (4, [])],
        )
        orch = ProofOrchestrator(proof_dir.parent, parallel=4)
        orch.lemma_count = 4
        called = []
        lock = threading.Lock()

        def fake(k, it):
            with lock:
                called.append(k)

        with patch.object(orch, "_run_phase_4", side_effect=fake):
            orch._run_phase_4_all(start_lemma=3, iteration=1)

        assert sorted(called) == [3, 4]

    def test_dependency_cycle_falls_back_to_sequential(self, proof_dir):
        # 1 → 2 → 1 (cycle)
        _write_decomposition(proof_dir, [(1, [2]), (2, [1])])
        orch = ProofOrchestrator(proof_dir.parent, parallel=4)
        waves = orch._build_dependency_waves(2)
        # All lemmas should still appear, just in single-lemma waves
        flat = [k for w in waves for k in w]
        assert sorted(flat) == [1, 2]


# ---------------------------------------------------------------------------
# Phase 5 parallel dispatch
# ---------------------------------------------------------------------------

class TestPhase5Parallel:
    def test_sequential_with_parallel_one(self, proof_dir):
        orch = ProofOrchestrator(proof_dir.parent, parallel=1)
        results_calls = []

        def fake(k, it):
            results_calls.append((k, it))
            return {"failures": []}

        with patch.object(orch, "_run_phase_5", side_effect=fake):
            results = orch._run_phase_5_all([1, 2, 3], iteration=1)

        assert results == {1: {"failures": []}, 2: {"failures": []}, 3: {"failures": []}}
        assert results_calls == [(1, 1), (2, 1), (3, 1)]

    def test_parallel_returns_dict_keyed_by_lemma(self, proof_dir):
        orch = ProofOrchestrator(proof_dir.parent, parallel=4)

        def fake(k, it):
            return {"lemma": k, "failures": [] if k % 2 == 0 else ["bad"]}

        with patch.object(orch, "_run_phase_5", side_effect=fake):
            results = orch._run_phase_5_all([1, 2, 3, 4], iteration=2)

        assert set(results.keys()) == {1, 2, 3, 4}
        assert results[1]["failures"] == ["bad"]
        assert results[2]["failures"] == []
        assert results[3]["failures"] == ["bad"]
        assert results[4]["failures"] == []

    def test_parallel_runs_concurrently(self, proof_dir):
        orch = ProofOrchestrator(proof_dir.parent, parallel=4)

        def slow(k, it):
            time.sleep(0.2)
            return {"failures": []}

        with patch.object(orch, "_run_phase_5", side_effect=slow):
            t0 = time.monotonic()
            orch._run_phase_5_all([1, 2, 3, 4], iteration=1)
            elapsed = time.monotonic() - t0

        assert elapsed < 0.6, f"parallel audit took {elapsed:.2f}s — not concurrent"


# ---------------------------------------------------------------------------
# State updates during parallel execution
# ---------------------------------------------------------------------------

class TestConcurrentLemmasState:
    def test_concurrent_lemmas_tracked_during_wave(self, proof_dir):
        _write_decomposition(
            proof_dir,
            [(1, []), (2, []), (3, []), (4, [])],
        )
        orch = ProofOrchestrator(proof_dir.parent, parallel=4)
        orch.lemma_count = 4

        seen_concurrent = []
        barrier = threading.Barrier(4)

        def fake(k, it):
            barrier.wait()
            # All four workers active here — snapshot state
            seen_concurrent.append(list(orch.state.get("concurrent_lemmas", [])))

        with patch.object(orch, "_run_phase_4", side_effect=fake):
            orch._run_phase_4_all(start_lemma=1, iteration=1)

        # At least one snapshot should contain all 4 lemmas
        assert any(sorted(snap) == [1, 2, 3, 4] for snap in seen_concurrent), \
            f"expected a snapshot with all 4 lemmas, got {seen_concurrent}"

        # After the wave finishes, concurrent_lemmas should be empty
        assert orch.state.get("concurrent_lemmas", []) == []


# ---------------------------------------------------------------------------
# Worker exception propagation
# ---------------------------------------------------------------------------

class TestUnlimitedParallel:
    def test_zero_means_unlimited_runs_full_wave_concurrently(self, proof_dir):
        # 6 independent lemmas, each fake-call sleeps 0.2s.
        # Sequential = 1.2s, parallel=2 = 0.6s, unlimited = 0.2s.
        _write_decomposition(
            proof_dir,
            [(k, []) for k in range(1, 7)],
        )
        orch = ProofOrchestrator(proof_dir.parent, parallel=0)
        orch.lemma_count = 6

        def slow(k, it):
            time.sleep(0.2)

        with patch.object(orch, "_run_phase_4", side_effect=slow):
            t0 = time.monotonic()
            orch._run_phase_4_all(start_lemma=1, iteration=1)
            elapsed = time.monotonic() - t0

        # All 6 should overlap; allow generous slack for thread startup
        assert elapsed < 0.5, \
            f"unlimited parallel took {elapsed:.2f}s — workers serialized"

    def test_zero_passes_audit_pool_unlimited(self, proof_dir):
        orch = ProofOrchestrator(proof_dir.parent, parallel=0)

        def slow(k, it):
            time.sleep(0.2)
            return {"failures": []}

        with patch.object(orch, "_run_phase_5", side_effect=slow):
            t0 = time.monotonic()
            orch._run_phase_5_all([1, 2, 3, 4, 5, 6], iteration=1)
            elapsed = time.monotonic() - t0

        assert elapsed < 0.5, \
            f"unlimited parallel audit took {elapsed:.2f}s — workers serialized"

    def test_default_constructor_is_unlimited(self, proof_dir):
        # No parallel kwarg → should use PARALLEL_DEFAULT (= 0 = unlimited)
        orch = ProofOrchestrator(proof_dir.parent)
        assert orch.parallel == 0


class TestWorkerExceptions:
    def test_worker_exception_propagates(self, proof_dir):
        _write_decomposition(proof_dir, [(1, []), (2, [])])
        orch = ProofOrchestrator(proof_dir.parent, parallel=2)
        orch.lemma_count = 2

        def fake(k, it):
            if k == 2:
                raise RuntimeError("kaboom on lemma 2")

        with patch.object(orch, "_run_phase_4", side_effect=fake):
            with pytest.raises(RuntimeError, match="kaboom"):
                orch._run_phase_4_all(start_lemma=1, iteration=1)
