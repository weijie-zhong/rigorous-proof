# Rigorous-Proof Orchestrator Performance Design

**Date:** 2026-04-15
**Goal:** Reduce token consumption and wall-clock time of `scripts/orchestrate.py` while keeping every existing feature and the Phase 0–9 process unchanged.

## Constraints (locked decisions)

1. **Opus everywhere.** No per-phase model downgrades. Every LLM call continues to use `--model opus`.
2. **Process-preserving.** All phases still happen; all output files still exist with the same names and (semantically) the same contents. Workflow visible to the user is unchanged.
3. **Retries untouched.** `RETRY_MAX_ATTEMPTS=20` and `RETRY_MAX_TOTAL_WAIT=19800` (5.5h) are intentional to cover Claude's ~5h usage-limit reset window. Do not lower these.
4. **Backwards compatible defaults.** Existing CLI behavior must be unchanged when no new flags are passed.

## Cost analysis (the why)

The orchestrator dispatches each phase as a separate `claude -p` subprocess. With N lemmas and M audit iterations:

- Phases 4, 5, 6, 7 are called O(N·M) times.
- Each of those calls re-passes the same stable context (`00_distilled.md`, `00_strategy.md`, `01_decomposition.md`, `status_log.md`) through a fresh user message. The system prompt is currently empty, so Anthropic's prompt cache has no stable prefix to hit.
- Phase 4 and Phase 5 are called sequentially across lemmas, even when the dependency DAG would allow concurrent execution.
- Phase 9a is an LLM call that does file ordering — no reasoning required.

These four observations drive the four levers below.

## Levers (locked)

### Lever 1 — Aggressive versioned prompt caching

Move stable context into `--append-system-prompt` so Anthropic's prompt cache (5-minute TTL on identical prefixes) makes re-reads near-free.

**Cached blob contents:**
- `SKILL_PREAMBLE`
- `<distilled>` block: full contents of `proof_work/00_distilled.md`
- `<strategy>` block: full contents of `proof_work/00_strategy.md`
- `<decomposition>` block: full contents of `proof_work/01_decomposition.md`
- `<recent_status_log>` block: last 5 iteration entries from `proof_work/status_log.md` (pruned)
- A footer paragraph telling the agent these files are already loaded and must not be re-read

**Not cached** (because they change too frequently and would invalidate the cache):
- `proof_lemma_*.md` files (mutated by Phase 4 and Phase 7)
- `audit_lemma_*_iter_*.md` files (written by Phase 5)
- `fork_lemma_*_gap_*.md` files (written by Phase 6)
- `cold_read_audit.md` (written by Phase 9b)

These remain agent-side reads.

**Versioning.** A version counter bumps whenever any stable file's mtime changes. The orchestrator recomputes the system prompt only on version bump; otherwise it reuses the cached string. Version is logged on each invocation so cache rebuilds are visible in the orchestrator log.

**Invalidation triggers.** Phase 7 may rewrite `00_distilled.md` (added hypotheses). Phase 7 also appends to `status_log.md`. The orchestrator calls `context.invalidate()` after each Phase 7 run; the next phase call rebuilds. Within a 5-minute window, a rebuild loses the cache hit for that one call but subsequent calls in the same window cache against the new prefix.

### Lever 2 — Parallelize independent lemmas in Phase 4 and Phase 5

New CLI flag `--parallel N`, default `1` (preserves current sequential behavior).

**Phase 4 (proof execution).** Build a dependency DAG from `_parse_lemma_dependencies(proof_dir, k)` for every lemma. Topologically sort into waves: wave w contains all lemmas whose dependencies are all in waves < w. Execute each wave with up to N concurrent `claude -p` subprocesses; wait for the wave to finish before starting the next.

**Phase 5 (audit, inside the inner audit loop).** Audits are pure reads — completely independent across lemmas in a given iteration. Run all unpassed lemmas as a single concurrent pool of size N. Once the pool finishes, Phase 6 (gap analysis) and Phase 7 (revision) run **sequentially** per failing lemma, because Phase 7 may mutate `00_distilled.md` and that mutation must be visible to subsequent revisions in the same iteration.

**File-write safety.** Each parallel call writes to a distinct file (`proof_lemma_k.md` or `audit_lemma_k_iter_n.md`). No write collisions are possible.

**Cache safety.** Within a wave, no agent writes to a stable file (Phase 4 and Phase 5 do not touch `00_*.md` or `01_decomposition.md`). The cached prefix is therefore stable across the wave.

**Logging.** All log lines from inside a parallel worker are prefixed with `[L{k}]`. A `threading.Lock` around the `log()` function prevents byte interleaving in the console and the file log.

**State updates.** A `threading.Lock` protects `OrchestratorState.save()`. The state schema gains a `concurrent_lemmas: list[int]` field that lists lemmas currently in flight. The existing `current_phase` / `current_lemma` fields are still set at wave entry/exit so single-lemma resume detection stays meaningful.

**Heartbeat.** Unaffected — still one orchestrator process, still one heartbeat thread.

**Resume semantics.** `detect_phase_from_files` already operates per-file, so partial parallel completion is naturally restartable. No change required.

### Lever 3 — Replace Phase 9a with Python

The Phase 9a prompt explicitly says: *"Do not modify the content — just read and prepare for the cold read audit. Write the assembled order to `proof_work/assembled_proof_order.md` listing the files read and their lemma numbers."*

This is mechanical work. Replace the `_invoke(PHASE_9A_COMPILE)` call in `_run_phase_9` with a pure-Python helper that:
1. Globs `proof_lemma_*.md` in `proof_dir`.
2. Sorts numerically by lemma index.
3. Writes `assembled_proof_order.md` in the same format the LLM was producing (a header line + a list of lemma file paths in order).

Phases 9b, 9c, 9d remain LLM calls. Phase 9d still consumes the assembled order file, just as before.

### Lever 4 — Prompt edits to stop redundant rereads

Once the cached blob carries the stable files, edit the Phase 4/5/6/7 prompts in `scripts/prompts.py`:

- "Read `proof_work/00_distilled.md` (hypotheses, definitions)" → "The distilled problem (`00_distilled.md`) is already loaded in your system context. Use it directly; do not re-read."
- Same treatment for `00_strategy.md`, `01_decomposition.md`, `status_log.md`.

The prompts still tell the agent to read `proof_lemma_*.md` (dependencies, revision targets) and `audit_lemma_*.md` files, since those are not cached.

## Architecture changes

### New module: `scripts/context.py`

```python
class ContextBuilder:
    """Builds and caches the system-prompt blob for orchestrator phases."""

    STABLE_FILES = [
        "00_distilled.md",
        "00_strategy.md",
        "01_decomposition.md",
        "status_log.md",
    ]
    STATUS_LOG_KEEP = 5  # most recent iteration entries

    def __init__(self, proof_dir: Path): ...
    def system_prompt(self) -> str: ...      # returns cached or rebuilt blob
    def version(self) -> int: ...            # monotonic, bumps on rebuild
    def invalidate(self) -> None: ...        # forces next call to rebuild
    def _mtimes(self) -> tuple[float, ...]: ...
    def _prune_status_log(self, text: str) -> str: ...
```

`system_prompt()` checks current mtimes against the snapshot from the last build; on mismatch it rebuilds, bumps `version`, and logs the rebuild. The build assembles labeled XML-style blocks per stable file, plus a footer instructing the agent not to re-read. If a stable file does not yet exist (e.g., before Phase 1 finishes `00_distilled.md`), it is omitted from the blob.

### Modified: `scripts/orchestrate.py`

- `ProofOrchestrator.__init__` constructs a `ContextBuilder(self.proof_dir)` and stores it on `self.context`.
- `ProofOrchestrator._invoke` passes `system_prompt=self.context.system_prompt()` to `invoke_claude`.
- `invoke_claude` already accepts a `system_prompt` parameter; it currently passes it to `--append-system-prompt` when non-None. No signature change needed.
- New method `ProofOrchestrator._run_phase_4_parallel(start_lemma)` builds the dep DAG and dispatches waves via `concurrent.futures.ThreadPoolExecutor(max_workers=self.parallel)`. The existing `_run_phase_4(k, iteration)` is reused as the per-lemma worker.
- New method `ProofOrchestrator._run_phase_5_parallel(iteration, lemmas_to_audit)` returns a `dict[int, dict|None]` mapping lemma → audit summary, used by `_run_inner_audit_loop`.
- `_run_phase_7` calls `self.context.invalidate()` after writing the revised proof, because the revision may have mutated `00_distilled.md` and definitely appended to `status_log.md`.
- `_run_phase_9` replaces the `_invoke(PHASE_9A_COMPILE)` call with `self._compile_assembled_order()`, a new private method that performs the file ordering in Python.
- New method `_compile_assembled_order()` writes `assembled_proof_order.md`.
- `argparse` gains `--parallel N` with default 1.
- `log()` gains a module-level `threading.Lock` and an optional thread-local prefix that parallel workers set.
- `OrchestratorState.save()` is wrapped in a `threading.Lock`.
- `OrchestratorState` schema gains `concurrent_lemmas: list[int]`.

### Modified: `scripts/prompts.py`

- `PHASE_4_PROOF_LEMMA`, `PHASE_5_AUDIT_LEMMA`, `PHASE_6_GAP_ANALYSIS`, `PHASE_7_REVISION` have the file-read instructions for stable files replaced with "use the system context" language.
- `PHASE_9A_COMPILE` is removed (Python replacement).
- `format_prompt` and `get_dependency_files_text` are unchanged.

### Removed: nothing else

`SKILL_PREAMBLE` is moved into `ContextBuilder` (it's now part of the cached blob). The constant remains in `prompts.py` as the source of truth; `ContextBuilder` imports it.

## State file schema change

`orchestrator_state.json` gains one optional field:

```json
{
  ...existing fields...,
  "concurrent_lemmas": [3, 5, 7]
}
```

Absent or empty list = no parallel work in flight. Old state files without the field are still readable.

## Testing

### New unit tests (`tests/test_context.py`)

- `test_system_prompt_includes_all_stable_files`: write all four stable files, assert each appears in the prompt under its labeled block.
- `test_system_prompt_omits_missing_files`: only `00_distilled.md` exists; assert `<strategy>`, `<decomposition>`, `<recent_status_log>` blocks are absent.
- `test_version_bumps_on_mtime_change`: build once, modify a file, build again, assert `version()` increased by 1.
- `test_version_stable_when_files_unchanged`: build twice with no file changes, assert version is the same and the second call returned a cached string (use a counter or spy).
- `test_invalidate_forces_rebuild`: build, call `invalidate()`, build again, assert version bumped without any file change.
- `test_status_log_pruned_to_last_k`: write a `status_log.md` with 10 iteration entries, assert only the last 5 appear in the cached blob.
- `test_status_log_pruning_handles_short_logs`: log with 2 entries → both appear, no error.

### New unit tests (`tests/test_parallel.py`)

- `test_dag_waves_linear`: lemmas 1→2→3 (each depends on previous). Assert waves = `[[1], [2], [3]]`.
- `test_dag_waves_diamond`: 1, 2 deps on 1, 3 deps on 1, 4 deps on 2 and 3. Assert waves = `[[1], [2, 3], [4]]`.
- `test_dag_waves_independent`: 4 lemmas with no deps. Assert single wave `[[1, 2, 3, 4]]`.
- `test_phase_4_parallel_calls_invoke_per_lemma`: mock `invoke_claude`, assert one call per lemma, in correct wave order.
- `test_phase_5_parallel_returns_summaries_keyed_by_lemma`: mock `invoke_claude` to return distinct summaries; assert returned dict maps each lemma index to its summary.
- `test_parallel_default_is_sequential`: with `--parallel 1`, assert ThreadPoolExecutor max_workers is 1 (or that the path through the code is serial).
- `test_state_concurrent_lemmas_updated_during_wave`: spy on state writes during a parallel wave; assert `concurrent_lemmas` reflects in-flight workers.

### New unit tests (`tests/test_compile_assembled_order.py`)

- `test_assembled_order_lists_lemmas_numerically`: create `proof_lemma_1.md`, `proof_lemma_2.md`, ..., `proof_lemma_10.md`; assert order is 1, 2, ..., 10 (not lexicographic).
- `test_assembled_order_handles_missing_lemmas`: only lemmas 1, 2, 4 exist (lemma 3 missing); assert function still produces output for the existing files and logs a warning.

### Modified existing tests

- `tests/test_orchestrate.py`: any test that mocks `invoke_claude` and asserts on argument count must accept the new `system_prompt` kwarg. Update assertions.
- `tests/test_compliance.py`: if it inspects `_run_phase_9` to verify Phase 9a was called as an LLM phase, replace with assertion that `_compile_assembled_order` was called and produced the expected file.
- `tests/test_e2e.py`: if it dispatches the full orchestrator with a stub LLM, ensure the stub provides reasonable returns for all phases. Phase 9a stub call goes away.

### Test infrastructure

All tests mock `subprocess.run` (or higher-level mocking on `invoke_claude`) so no real `claude -p` calls happen in CI. Use `pytest` fixtures for temporary `proof_work/` directories.

## Estimated impact

- **Input tokens per Phase 4/5/6/7 call:** ~70-85% reduction after the first call within a 5-minute window. The reduction comes from cached-prefix hits replacing what is currently 5-15k tokens of repeated stable-context reads per call.
- **Output tokens:** ~5-10% reduction from Lever 4 — the agent stops summarizing files it just re-read.
- **LLM calls per run:** -1 (Phase 9a removed).
- **Wall clock on multi-lemma proofs:** roughly 2-4× faster at `--parallel 4` for proofs with wide dependency layers; linear-chain proofs see no parallelism win but still benefit from caching.
- **Risk surface:** low. All four levers are gated, mechanical, or invisible to downstream consumers. Worst case is a cache miss (back to current behavior) or `--parallel 1` (back to current behavior).

## Out of scope

- Model selection per phase (locked to Opus).
- Phase 9d Python replacement (kept as LLM for editorial smoothing).
- Restructuring the dual-loop logic in `_run_inner_audit_loop` and `_run_dual_loop`.
- Any change to `RETRY_MAX_ATTEMPTS`, `RETRY_MAX_TOTAL_WAIT`, or retry wait calculations.
- Refactoring the terminal-launch helpers (`_launch_windows`, `_launch_macos`, `_launch_linux`).
- Any change to the heartbeat thread or stale-detection logic.
- Any change to the user-facing fork-decision prompt in Phase 6.
