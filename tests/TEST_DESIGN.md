# Test Design: rigorous-proof skill

Date: 2026-03-28

## Overview

Three test layers covering both the orchestrator script and SKILL.md compliance:

| Layer | What | Cost | When to run |
|---|---|---|---|
| 1. Unit tests | orchestrate.py logic with mock claude | Free, fast | Every change |
| 2. Compliance | SKILL.md discipline via real Claude subagents | ~5 Opus calls | SKILL.md changes |
| 3. End-to-end | Full orchestrated run with real Claude | ~8-10 Opus calls | Major changes |

## Files

```
tests/
  conftest.py              # Shared fixtures (temp proof_work/, mock setup)
  mock_claude.py           # Mock script simulating Claude responses
  test_orchestrate.py      # Layer 1: unit tests
  test_compliance.py       # Layer 2: subagent compliance scenarios
  test_e2e.py              # Layer 3: end-to-end integration
```

---

## Layer 1: Orchestrator Unit Tests (`test_orchestrate.py`)

Uses `mock_claude.py` — a script that reads the prompt, writes expected files to `proof_work/`, and returns canned JSON summaries. No API calls.

### 1.1 Phase detection from files

Create various `proof_work/` file layouts in a temp directory, call `detect_phase_from_files()`, assert correct (phase, lemma, iteration):

| Test case | Files present | Expected |
|---|---|---|
| Fresh start | `00_setup.md` only | (2, 0, 0) |
| After decomposition | `00_setup.md`, `01_decomposition.md` | (3, 1, 1) |
| Mid proof | `00_setup.md`, `01_decomposition.md`, `proof_lemma_1.md` (of 3) | (3, 2, 1) |
| Needs audit | All `proof_lemma_*.md`, no audit files | (4, 1, 1) |
| Audit failed, no fork | Audit with ❌, no fork files | (5, k, iter) |
| Audit failed, fork exists | Audit with ❌, fork file exists | (6, k, iter) |
| Revision done | Proof file iteration > audit iteration | Skips to next lemma |
| All pass | All audits ✅ | (8, 0, 0) |
| Cold read done | `cold_read_audit.md` exists | (8, 0, 0) for 8c |
| Complete | `final_proof.md` exists | (9, 0, 0) |
| Missing setup | No `00_setup.md` | FileNotFoundError |

### 1.2 Resume after crash

- Write state file: `current_phase: 3, phase_status: "in_progress"`, heartbeat 5 minutes ago
- Call `_detect_resume_point()`
- Assert: returns Phase 3 (restarts the stale phase)

### 1.3 Resume after clean stop

- Write state file: `current_phase: 3, phase_status: "done"`
- Ensure corresponding files exist
- Assert: advances to next phase via file detection

### 1.4 Heartbeat staleness

- `is_heartbeat_stale()` with timestamp 10s ago → False
- `is_heartbeat_stale()` with timestamp 200s ago → True
- `is_heartbeat_stale()` with no heartbeat → True
- `is_heartbeat_stale()` with corrupt timestamp → True

### 1.5 Full phase progression (mock)

- Point orchestrator at mock_claude
- Run from Phase 2 through Phase 8
- Assert: all expected files created in order (`01_decomposition.md`, `proof_lemma_1.md`, ..., `final_proof.md`, `proof_journal.md`)
- Assert: state file updated at each phase

### 1.6 Fork timeout

- Call `prompt_user_fork_decision(summary, timeout=2)` with no stdin
- Assert: returns `("B", True)` after ~2 seconds

### 1.7 Iteration cap

- Mock audit always returns ❌
- Run `_run_audit_loop()` with `max_effort=True`
- Assert: exactly 3 iterations, then proceeds

### 1.8 Lemma dependency parsing

- Create decomposition files with various formats:
  - "Depends on: Lemma 1, Lemma 3"
  - "Depends on: H1, Lemma 2"
  - "Depends on: none"
- Assert correct dependency lists

### 1.9 JSON parsing robustness

- `parse_json_from_output('{"result": "..."}')` — outer JSON wrapper
- `parse_json_from_output('Some text\n```json\n{"a":1}\n```')` — markdown block
- `parse_json_from_output('garbage')` — returns None
- `parse_json_from_output('{"nested": {"a": 1}}')` — nested object

---

## Layer 2: SKILL.md Compliance (`test_compliance.py`)

Each test dispatches a real Claude subagent (via `Agent` tool or `claude -p`) with the rigorous-proof skill loaded. After the agent completes, inspect `proof_work/` files for compliance.

### 2.1 Justification discipline

**Proposition:** "Prove that every convergent sequence in R is bounded"

**Why this proposition:** Simple enough that Claude is tempted to skip justifications and write "clearly" or "obviously."

**Setup:** Run Phases 1-3 (inline mode, single pass).

**Checks on `proof_lemma_*.md`:**
- [ ] Every step has exactly one justification tag from: `[Hypothesis Hk]`, `[Definition of X]`, `[Theorem: Name]`, `[By Step n]`, `[By Lemma k]`, `[Algebraic manipulation]`, `[Logic: rule]`
- [ ] Zero occurrences of: "clearly", "obviously", "trivially", "it is easy to see", "by a standard argument"
- [ ] Status header present with correct format

### 2.2 Gap honesty under insufficient hypotheses

**Proposition:** "Prove that every continuous function on [0,1] is uniformly continuous"
**Hypotheses supplied:** Only "f: [0,1] → R is measurable" (deliberately too weak — should be continuous)

**Why this proposition:** Forces Claude to either silently strengthen the hypothesis (violation) or honestly flag the gap.

**Setup:** Run Phases 1-4 (inline mode).

**Checks:**
- [ ] `proof_lemma_*.md` contains `[⚠️ GAP]` markers OR audit catches the issue
- [ ] Audit file has ❌ on check 2 (hypothesis fidelity) — proof used continuity but only measurability was given
- [ ] If Phase 5 triggered: fork file exists with the missing assumption identified
- [ ] `00_setup.md` does NOT contain "continuous" unless the user's original hypothesis said so

### 2.3 Honest final reporting (Change 3 verification)

**Proposition:** "Prove the Bolzano-Weierstrass theorem: every bounded sequence in R has a convergent subsequence"
**Hypotheses:** Provide only ordering axioms of R (deliberately omit completeness/LUB property)

**Why this proposition:** Multi-lemma proof where the completeness gap creates an inter-lemma issue that per-lemma audits might miss but cold read should catch.

**Setup:** Run full workflow through Phase 8, max effort.

**Checks on cold read finding unresolved gaps:**
- [ ] `cold_read_audit.md` contains `[UNRESOLVED CRITICAL GAP]` (if completeness gap propagates)
- [ ] `final_proof.md` contains `## UNRESOLVED GAPS` section
- [ ] `final_proof.md` ends with `□ (INCOMPLETE — see unresolved gaps)` (not `∎`)
- [ ] `proof_journal.md` has gap summary at the TOP
- [ ] Output includes WARNING banner

**Alternative outcome:** If Claude correctly identifies the gap early (Phase 5) and the user/timeout resolves it, verify that the fork mechanism worked correctly and the resolution is tracked.

### 2.4 Fork timeout (Change 2 verification)

**Proposition:** Same as 2.2 (triggers crucial gap in Phase 5)

**Setup:** Run through Phase 5, do NOT provide user input.

**Checks:**
- [ ] After 600s (or shortened timeout for testing), option B is auto-selected
- [ ] Fork file contains `Decision: B (auto-selected after 600s timeout)`
- [ ] Workflow continues to Phase 6 with option B applied

**Note:** For practical testing, override `FORK_TIMEOUT` to a shorter value (e.g., 10s).

### 2.5 Quantifier and precondition rigor

**Proposition:** "Prove that if f: R→R is differentiable and f'(x) > 0 for all x, then f is strictly increasing"

**Why this proposition:** Requires applying MVT, whose preconditions (continuity on [a,b], differentiability on (a,b)) must be explicitly verified as sub-steps. Easy to get quantifier scope wrong.

**Setup:** Run Phases 1-4 (inline mode).

**Checks on `proof_lemma_*.md`:**
- [ ] MVT invoked with `[Theorem: Mean Value Theorem]` tag
- [ ] Preconditions of MVT verified as explicit sub-steps (continuity from differentiability, correct interval)
- [ ] Quantifier in conclusion matches target: ∀a,b ∈ R, a < b ⟹ f(a) < f(b)
- [ ] Audit check 5 (quantifier check) passes ✅

---

## Layer 3: End-to-End Integration (`test_e2e.py`)

One full orchestrated run with real Claude.

**Proposition:** "Prove that √2 is irrational"

**Why this proposition:** Well-known, tractable, produces 1-2 lemmas. Tests the full pipeline without excessive cost.

**Setup:**
1. Create `proof_work/00_setup.md` manually (or via interactive Phase 0-1)
2. Run `python scripts/orchestrate.py --max-effort`

**Checks:**
- [ ] All files created: `00_setup.md`, `01_decomposition.md`, `proof_lemma_*.md`, `audit_lemma_*_iter_*.md`, `cold_read_audit.md`, `final_proof.md`, `proof_journal.md`
- [ ] `orchestrator_state.json` shows progression through all phases
- [ ] `final_proof.md` ends with `∎` (clean proof)
- [ ] Proof health summary present with all fields
- [ ] Journal contains all sections (setup, decomposition, proofs, audits, cold read)
- [ ] Orchestrator stdout contains full intermediate summaries (Change 1 verification)

---

## mock_claude.py Design

A Python script that acts as a drop-in replacement for `claude -p`:

```
python mock_claude.py <prompt>
```

Behavior:
1. Parse the prompt to determine which phase is being requested
2. Write the expected output files to `proof_work/` with realistic content
3. Print a JSON response to stdout matching `--output-format json`

Phase detection heuristics (from prompt content):
- Contains "Decomposition" → write `01_decomposition.md` with 2 lemmas
- Contains "Prove Lemma" → write `proof_lemma_k.md`
- Contains "hostile referee" → write `audit_lemma_k_iter_n.md` (configurable pass/fail)
- Contains "Gap Analysis" → write `fork_lemma_k_gap_j.md`
- Contains "Revise" → overwrite `proof_lemma_k.md` with incremented iteration
- Contains "cold read" → write `cold_read_audit.md`
- Contains "final proof" → write `final_proof.md`
- Contains "journal" → write `proof_journal.md`

Environment variable `MOCK_AUDIT_RESULT=pass|fail` controls whether audits return ✅ or ❌.

---

## Running Tests

```bash
# Layer 1 only (fast, free)
pytest tests/test_orchestrate.py -v

# Layer 2 only (real Claude, ~5 calls)
pytest tests/test_compliance.py -v --timeout=1800

# Layer 3 only (real Claude, full run)
pytest tests/test_e2e.py -v --timeout=3600

# All layers
pytest tests/ -v --timeout=3600
```
