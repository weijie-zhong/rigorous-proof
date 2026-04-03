---
name: rigorous-proof
description: Use this skill whenever the user asks to prove a mathematical theorem, lemma, or proposition, or asks for a rigorous or formal proof. Also trigger when the user mentions "proof", "prove that", "show that", "demonstrate rigorously", "formal argument", or any request involving mathematical derivation where logical correctness matters. Always use this skill for proof tasks even if the math seems straightforward — rigor failures happen most often on "obvious" steps. If the user says "prove [X] with max effort", run the full iterative loop until the self-audit is fully satisfied.
---

# Rigorous Mathematical Proof Writing

## Purpose

This skill enforces a structured, iterative, file-backed proof workflow that eliminates the most common LLM proof failures: skipped justifications, unchecked edge cases, hand-waved implications, and silently strengthened hypotheses.

**Two modes:**

1. **Default mode (orchestrated + terminal).** The user's request is captured to a file, then the Python orchestrator (`scripts/orchestrate.py`) launches in a new terminal window (cross-platform) and handles all phases (0–9), dispatching each as a separate agent call with heartbeat monitoring and automatic resume. Difficulty is auto-detected: "difficult" problems automatically enable max effort (dual loop). The user can force max effort with `prove [X] with max effort`.
2. **Light mode (inline).** The user says `prove [X] light` or `prove [X] inline`. The full workflow runs in a single session without the orchestrator. Option: `prove [X] light, skip decomposition` for simple single-unit proofs.

---

## THE CARDINAL RULE: The Hard Part Is the Point

The hard part of the proof is the ENTIRE POINT. Your goal is not to produce text that looks like a proof — your goal is to produce a proof that IS a proof.

- **80% of your effort should go into the hardest 20% of the proof.** If you find yourself breezing through a step that should be difficult, you are almost certainly making an error or skipping a justification.
- The phrases "clearly", "obviously", "trivially", "it is easy to see", and "by a standard argument" are **red flags** — they signal you are about to dodge a hard step. Every time you want to write one of these, stop and ask: *can I actually justify this?*
- If a hard problem appears to solve itself effortlessly, **suspect an error**. Go back and check whether you silently strengthened a hypothesis, proved a different statement, or skipped a non-trivial sub-argument.
- Getting stuck is normal. It is NOT a reason to give up, hand-wave, or switch to an easier variant of the problem. The difficulty is where the mathematical content lives.

---

## Skill Entry Point

When the user asks to prove something:

1. Acknowledge the request briefly.
2. Collect the problem statement and any user-referenced files.
3. Create `proof_work/` directory if it does not exist.
4. Write the user's problem statement and any referenced file contents to `proof_work/00_user_input.md`.
5. Detect flags from the user's request:
   - `--max-effort`: if the user said "max effort" (also auto-enabled for difficult problems).
   - `--no-terminal`: if the user said "no terminal" or "run here".
6. Launch the orchestrator:
   ```bash
   python scripts/orchestrate.py [--max-effort] [--no-terminal] [--work-dir DIR]
   ```
7. The orchestrator handles Phases 0–9 automatically.
   - By default, the orchestrator opens a new terminal window (cross-platform: Windows, macOS, Linux) and the Bash call returns immediately. The proof runs independently — it survives even if this chat session stalls.
   - Difficulty is auto-detected after Phase 1: "difficult" problems automatically get max effort (dual loop).

If the user said `prove [X] light` or `prove [X] inline`, skip the orchestrator and run the full workflow within this session, following the phase descriptions below. Add `skip decomposition` for simple single-unit proofs.

---

## PHASE 0 — Environment Check

The orchestrator performs this locally (no Claude call needed):

- Create `proof_work/` directory if it does not exist.
- Verify `proof_work/00_user_input.md` exists.
- Log environment info: working directory, max effort mode.

---

## PHASE 1 — Problem Distillation

**Input:** `proof_work/00_user_input.md` (the user's original problem and any referenced material).

**Output:** `proof_work/00_distilled.md` — a fully self-contained, rigorous mathematical formulation.

The distilled file must contain:

1. **Proposition**: The exact statement to be proved, with all quantifiers, domains, and conditions.
2. **Hypotheses inventory**: Every assumption/given, numbered (H1, H2, ...).
3. **Definitions**: Formal definitions of every key term.
4. **Difficulty assessment**: Classify as **difficult**, **moderate**, or **easy** with brief justification:
   - **Easy**: Textbook exercise, proof strategy is immediately obvious, involves ≤ 2 definitions.
   - **Moderate**: Standard result but non-trivial, multiple possible approaches.
   - **Difficult**: Research-level, multiple interacting definitions, no obvious strategy.

**Firewall principle:** All subsequent phases use ONLY `00_distilled.md` as their source of truth for the problem statement — never the raw user input. This ensures the mathematical formulation is precise and self-contained.

---

## PHASE 2 — Literature Survey (Optional)

**Triggered only when difficulty = "difficult".** Skipped for easy and moderate problems.

**Input:** `proof_work/00_distilled.md`
**Output:** `proof_work/00_survey.md`

Write:
- **Problem classification**: Area and sub-area of mathematics.
- **Key objects and structures**: Central mathematical objects and their properties.
- **Hidden assumptions**: Implicit assumptions that need to be made explicit.
- **Directly applicable theorems**: Each with full hypotheses (not just names).
- **Closely related results**: Theorems for similar but not identical settings.
- **Useful lemmas and inequalities**: Technical tools that might be needed.
- **Known counterexamples**: Examples showing related but false statements.

**Critical rule:** The survey does NOT propose proof strategies — it only maps the mathematical landscape. Strategy choice happens in Phase 3, informed by the survey.

---

## Common LLM proof failure modes (internalize and avoid all of these)

1. **Unjustified implications**: Writing "clearly A ⟹ B" without citing the theorem or definition that makes it true.
2. **Boundary/edge case neglect**: Proving the general case but ignoring degenerate cases (empty set, n=0, measure-zero sets, non-compact domains, etc.).
3. **Silent hypothesis strengthening**: Quietly assuming more than given (e.g., assuming continuity when only measurability is stated).
4. **Definitional slippage**: Using a term in a way that subtly differs from its formal definition.
5. **Quantifier errors**: Swapping ∀∃ with ∃∀, or leaving quantifier scope ambiguous.
6. **Gap-bridging by assertion**: Replacing a non-trivial sub-proof with "by a standard argument" or "it is well known that."
7. **Circular reasoning**: Using the target proposition (or an equivalent) as a step in the proof.
8. **Target manipulation**: Quietly proving a weaker or slightly different statement than what was asked.

---

## PHASE 3 — Strategy and Decomposition

**Input:** `proof_work/00_distilled.md` (+ `00_survey.md` if it exists, + `status_log.md` if re-entering from the loop)
**Output:** `proof_work/00_strategy.md` + `proof_work/01_decomposition.md`

### Part A: Proof Strategy

Write to `proof_work/00_strategy.md`:
- **Proof strategy**: State the overall approach (direct, contradiction, contrapositive, induction, construction, etc.) and *why* this strategy is appropriate.
- **Known results to be used**: List any external theorems, lemmas, or well-known results you plan to invoke, with their precise statements. If unsure of the exact statement, flag it with ⚠️.
- **Key insights**: What is the core mathematical idea that makes this proof work?

### Part B: Decomposition into Lemmas

Write to `proof_work/01_decomposition.md`:

Break the proof into the smallest self-contained claims that chain together to yield the result.

For each:
- **Lemma k**: State it precisely with quantifiers.
- **Depends on**: Which earlier lemmas or hypotheses it requires.
- **Why needed**: One sentence on how it connects to the main result.

Write a **dependency graph** showing the logical chain.

If the proof is simple enough to not need decomposition (< 5 logical steps), say so and proceed as a single unit.

---

## PHASE 4 — Proof Execution (One Lemma at a Time)

**CRITICAL: Work on exactly one lemma per pass.**

For each Lemma k, in dependency order:

### 4a. Load context
- Read `proof_work/00_distilled.md` (hypotheses, definitions).
- Read `proof_work/00_strategy.md` (proof strategy, known results).
- Read `proof_work/01_decomposition.md` (lemma statements and dependencies).
- Read `proof_work/status_log.md` if it exists — use "Lessons for next iteration" entries.
- Read proofs of any lemmas that Lemma k depends on.

### 4b. Write the proof
Write numbered steps. **Every step must carry exactly one justification tag:**

| Tag | Meaning |
|---|---|
| `[Hypothesis Hk]` | Directly invoking a stated assumption |
| `[Definition of X]` | Expanding or applying a formal definition |
| `[Theorem: Name]` | Applying a named theorem — state which hypotheses are satisfied and why |
| `[By Step n]` | Following from an earlier numbered step |
| `[By Lemma k]` | Following from a previously proved lemma |
| `[Algebraic manipulation]` | Routine algebra/calculus — show the work explicitly |
| `[Logic: rule]` | A logical inference rule (modus ponens, universal instantiation, etc.) |

**Rules during this phase:**
- Never write "clearly", "obviously", "trivially", "it is easy to see", or "by a standard argument."
- If a step requires checking that preconditions of an invoked theorem are satisfied, that check is itself a sub-step with its own justification.
- If you feel uncertain about any step, mark it with `[⚠️ GAP]` and explain what you cannot verify. Do NOT silently bridge it.
- When using proof by contradiction: state the negation of the target explicitly, with correct quantifiers.
- When using induction: state the base case, inductive hypothesis (with exact quantifiers), and inductive step as separate labeled blocks.

### 4c. Save
**Write to `proof_work/proof_lemma_k.md`** with header:
```
## Lemma k — [Short description]
Status: DRAFT
Iteration: 1
Gaps: [none / list of ⚠️ GAP descriptions]
```

---

## PHASE 5 — Self-Audit (Hostile Referee, One Lemma at a Time)

**CRITICAL: Each lemma audit MUST be dispatched to a fresh subagent using the Agent tool** (in inline mode) or a separate `claude -p` call (in orchestrated mode). This ensures the auditor has no memory of the proof-writing process.

For each Lemma k, run the **SIX-POINT CHECK**:

1. **Justification audit**: For each step, is the cited justification actually sufficient? Does the cited theorem actually apply given the hypotheses? Check every precondition.
2. **Hypothesis fidelity**: Did the proof use anything not in the hypothesis list? Did it silently strengthen any assumption?
3. **Target fidelity**: Does the conclusion of this lemma match its stated claim *exactly* — same quantifiers, same domains, same conditions?
4. **Edge cases**: Are degenerate/boundary cases covered? List them and verify each.
5. **Quantifier check**: Read every quantified statement. Is the scope correct? Are ∀ and ∃ in the right order?
6. **Circularity check**: Is the target proposition (or anything logically equivalent) used as an assumption?

For each check, output ✅ or ❌ with explanation for any failure.

**Write audit to `proof_work/audit_lemma_k_iter_n.md`.**

---

## PHASE 6 — Gap Resolution and Forking

When a ❌ is found that cannot be fixed by simple revision:

### 6a. Classify the gap
- **Fixable**: A missing sub-step that can be filled with more work → fix it in the next revision.
- **Crucial**: A gap that requires an assumption not present in the hypotheses → proceed to 6b.
- **Fatal**: The proposition as stated may be false or unprovable from the given hypotheses → report to user.

### 6b. Fork: Explore stronger assumptions
For each **crucial** gap, create a file `proof_work/fork_lemma_k_gap_j.md` containing the gap analysis.

**Present fork options:**
- (A) Accept the stronger assumption and continue
- (B) Try the alternative proof strategy **(default if no response, unless failure threshold reached)**
- (C) Prove the weaker conclusion instead
- (D) Abandon this lemma and restructure

**Timeout:** Wait up to 600 seconds (10 minutes) for user input. If no response, automatically select the default option. Log the auto-selection with a note.

**Failure escalation:** The orchestrator tracks how many times each lemma has failed audit. After **3 failures** on the same lemma, the default auto-selection changes from **(B)** to **(A)** (accept stronger assumption). This is logged: `Decision: A (auto-selected after 600s timeout, default changed to A after 3 failures)`. The rationale is that repeated failures suggest the original hypotheses are genuinely insufficient, and accepting a stronger assumption is more productive than continuing to retry.

---

## PHASE 7 — Revision

For each lemma that received ❌ on any audit check:

- Re-read the audit file and the current proof file.
- Rewrite the affected steps with corrected justifications.
- If a gap was resolved via forking (Phase 6), integrate the chosen resolution and update `proof_work/00_distilled.md` with any new hypotheses (marked as `(added)`).
- Update the status header:
  ```
  Status: REVISED
  Iteration: [n+1]
  ```

**Overwrite `proof_work/proof_lemma_k.md` with the revised version.**

**After each revision, append to `proof_work/status_log.md`:**
```
## Iteration N — Lemma K
### What failed
[List of specific audit checks that failed]
### What was tried
[Brief description of the approach in this iteration]
### What changed
[List of steps rewritten and why]
### Lessons for next iteration
[What this failure reveals — e.g., "direct approach fails because X, try contradiction next"]
```

---

## PHASE 8 — Dual Loop

The proof uses a **dual loop architecture**:

### Inner loop (per-lemma audit-revision)
```
INNER LOOP (max 7 iterations):
    For each lemma:
        If lemma already marked as PASSED → skip
        Run PHASE 5 (Audit)
        If all 6 checks ✅:
            Mark lemma as PASSED (skip in future iterations)
        If any ❌ found:
            Run PHASE 6 (Gap Resolution) if needed
            Run PHASE 7 (Revision)
    If ALL lemmas PASSED:
        BREAK → proceed to Phase 9
    Else:
        Continue inner loop
```

**Passed-lemma tracking:** Once a lemma fully passes all 6 audit checks, it is marked as passed and will not be re-audited in subsequent iterations. This is persisted in `orchestrator_state.json` and survives resume. Passed lemmas are cleared on re-strategization (outer loop) since the decomposition may change.

### Outer loop (re-strategization)
If the inner loop exhausts its iterations without all lemmas passing:

```
OUTER LOOP (max 3 iterations, max-effort mode only):
    Return to PHASE 3 (Strategy + Decomposition)
    Re-prove all lemmas (PHASE 4)
    Run inner loop again
    If ALL lemmas pass:
        BREAK → proceed to Phase 9
```

The outer loop forces a fundamental rethink of the proof strategy when incremental fixes fail. The `status_log.md` entries guide Phase 3 to avoid repeating failed approaches.

**Without max-effort mode:** Only 1 inner iteration and no outer loop — a single audit pass followed by Phase 9.

---

## PHASE 9 — Cold Read Assembly

After the loop converges (or terminates):

### 9a. Compile
Read all `proof_work/proof_lemma_k.md` files **in order**, without reading any working notes or audit files. Assemble into a single coherent proof.

### 9b. Cold read audit
**Launch a fresh agent** with no memory of the proof-writing or per-lemma audit process. It sees only the assembled proof. Check inter-lemma coherence, notation consistency, and final step validity.

If critical gaps are found, mark them with `[UNRESOLVED CRITICAL GAP]` in `proof_work/cold_read_audit.md`.

### 9c. Write the final proof
**Write to `proof_work/final_proof.md`** in clean mathematical style, preserving justification tags.

- If all audits passed cleanly: end with **∎**
- If unresolved critical gaps exist: include `## UNRESOLVED GAPS` section, end with **□ (INCOMPLETE)**

### 9d. Compile the proof journal
Merge all working files into `proof_work/proof_journal.md`:
- Distilled problem and strategy
- Decomposition
- Each lemma's proof evolution (all iterations)
- All audit reports and fork analyses
- Cold read notes
- Final assembled proof

---

## Output to User

After Phase 9, present to the user:

1. **The final proof** (from `final_proof.md`)
   If unresolved critical gaps exist, present a WARNING banner first.
2. **Proof health summary**:
   ```
   ┌───────────────────────────────────────────────┐
   │        PROOF HEALTH                           │
   ├───────────────────────────────────────────────┤
   │ Iterations:      k                            │
   │ Lemmas:          n (all ✅ / m ⚠️)            │
   │ Forks explored:  f                            │
   │ Cold read:       ✅ clean / ❌ N unresolved    │
   │ Caveats:         [list or "none"]             │
   └───────────────────────────────────────────────┘
   ```
3. **The proof journal** (offer as downloadable file)
4. **Caveats**: Results invoked but not proved, any remaining ⚠️ flags, stronger assumptions adopted via forking.

---

## Output Format (Final Proof)

```
## Proposition
[Exact statement]

## Hypotheses
H1: ...
H2: ...
[If any were added via forking, mark them: H_new (added — see fork analysis): ...]

## Definitions
[Key term]: [Formal definition]

## Strategy
[Approach and rationale]

## Known Results Used
- [Theorem name]: [Precise statement]

## UNRESOLVED GAPS (if any — omit this section if cold read passed cleanly)
...

## Proof

### Lemma 1: [Statement]
Step 1. [Claim] — [Justification tag]
Step 2. [Claim] — [Justification tag]
...  ∎

### Main Result
Step 1. By Lemma 1 and Lemma 2, ...
...  ∎

## Proof Health
Iterations: k | All audits: ✅/❌ | Cold read: ✅/❌ | Forks: f | Unresolved gaps: [count or 0] | Caveats: [list]
```

---

## User Commands

| Command | Behavior |
|---|---|
| `prove [X]` | Write input, launch orchestrator in terminal window, auto-detect difficulty (default) |
| `prove [X] with max effort` | Same but force dual loop even for easy/moderate problems |
| `prove [X] no terminal` | Run orchestrator in current session instead of new terminal window |
| `prove [X] light` | Light mode — run entire workflow inline in a single session (no orchestrator) |
| `prove [X] light, skip decomposition` | Light mode, no lemma split, but full justification tags + audit |
| `continue proof` | Resume from last saved state in `proof_work/` |
| `orchestrate --resume` | Resume orchestrated execution after disruption |
| `show proof journal` | Present the compiled `proof_work/proof_journal.md` |
| `show fork analysis` | Present all fork files for review |

---

## Default Mode (Orchestrated + Terminal)

The Python orchestrator is the **default execution mode**. It makes the workflow robust to connection issues, sudden disruptions, or memory loss by dispatching each phase as a separate agent call with heartbeat monitoring.

### How it works

1. **The skill writes `proof_work/00_user_input.md`** — capturing the user's problem and any referenced files.
2. **The skill launches the orchestrator in a new terminal window** — which handles Phases 0–9 autonomously.
3. **Difficulty auto-detection**: After Phase 1, the orchestrator reads the difficulty from `00_distilled.md`. If "difficult", max effort (dual loop) is automatically enabled.

To opt out, say `prove [X] light` — this runs the full workflow in a single session without the orchestrator.

### Terminal window (cross-platform)

By default, the orchestrator launches in a separate terminal window. This provides:
- **Process independence**: The proof workflow continues even if the Claude chat session stalls or hits usage limits.
- **Persistent console**: The new window stays open after completion so the user can read the output.
- **Cross-platform**: Supported on Windows (new console), macOS (Terminal.app via osascript), and Linux (gnome-terminal, konsole, xfce4-terminal, or xterm).

To disable the terminal window and run in the current session, say `prove [X] no terminal`.

### Commands

```bash
# Start orchestrated execution in terminal window (default)
python scripts/orchestrate.py

# Run in current session instead of new terminal
python scripts/orchestrate.py --no-terminal

# Force max effort (auto-enabled for difficult problems)
python scripts/orchestrate.py --max-effort

# Resume after disruption
python scripts/orchestrate.py --resume

# Specify working directory
python scripts/orchestrate.py --work-dir /path/to/project
```

### Resilience features

- **Heartbeat**: The orchestrator writes a heartbeat every 30 seconds. On resume, if the heartbeat is stale (>120s) and a phase was in progress, it restarts that phase.
- **File-based state**: Progress is tracked in `proof_work/orchestrator_state.json` and can also be inferred from the proof files themselves.
- **No per-phase timeouts**: The orchestrator waits for each agent to finish — only Phase 6 (fork decision) has a 600-second timeout for user input, defaulting to option B (or A after 3 failures — see Phase 6).
- **Resume from anywhere**: Run `--resume` after any disruption to pick up where it left off.

---

## Tips for the user

- For hard proofs, the dual loop is auto-enabled. For moderate proofs where you suspect hidden difficulty, you can force it with "max effort".
- If Claude flags a `[⚠️ GAP]`, that is valuable signal — it means the model detected its own uncertainty rather than hiding it.
- The fork mechanism (Phase 6) is especially useful in research: it tells you exactly what additional assumptions your proof actually needs, which often reveals the sharpest version of the theorem.
- The proof journal shows where the mathematical difficulty actually lies, not just the final clean proof.
- For proofs with > 5 lemmas, consider running the proof in multiple conversations, passing the `proof_work/` files between sessions.
- The cold read pass (Phase 9) catches inter-lemma coherence issues that per-lemma audits miss — this is analogous to reading a full paper draft after editing sections independently.
