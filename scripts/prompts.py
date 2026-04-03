"""
Phase-specific prompt templates for the rigorous-proof orchestrator.

Each prompt tells a Claude agent which proof_work/ files to read,
what to do, and where to write output.

Phase mapping:
  0 — Environment check (handled locally, no prompt)
  1 — Distill problem from user input -> 00_distilled.md
  2 — Literature survey (optional, difficult only) -> 00_survey.md
  3 — Strategy + decomposition -> 00_strategy.md + 01_decomposition.md
  4 — Proof execution (one lemma at a time) -> proof_lemma_k.md
  5 — Self-audit (hostile referee) -> audit_lemma_k_iter_n.md
  6 — Gap resolution and forking -> fork_lemma_k_gap_j.md
  7 — Revision -> overwrites proof_lemma_k.md
  8 — Dual loop (inner: 5-7; outer: back to 3)
  9 — Cold read assembly -> final_proof.md, proof_journal.md
 10 — Done sentinel
"""

SKILL_PREAMBLE = """\
You are executing one phase of a rigorous mathematical proof workflow.
All state lives in the proof_work/ directory. Read the files specified below,
perform your task, and write output to the specified file(s).
Follow the instructions precisely — every step must carry a justification tag.
"""

# ---------------------------------------------------------------------------
# Phase 1 — Distill problem from user input
# ---------------------------------------------------------------------------

PHASE_1_DISTILL = """\
{preamble}

## Your Task: Phase 1 — Distill the Mathematical Problem

Read `proof_work/00_user_input.md` which contains the user's original problem statement
and any referenced material.

Write to `proof_work/00_distilled.md` a fully self-contained, rigorous mathematical
formulation containing:

1. **Proposition**: The exact statement to be proved, with all quantifiers, domains,
   and conditions written out explicitly.
2. **Hypotheses inventory**: Every assumption/given, numbered (H1, H2, ...).
3. **Definitions**: Formal definitions of every key term. Do not assume the reader
   shares your interpretation.
4. **Difficulty assessment**: Classify as **difficult**, **moderate**, or **easy** with
   brief justification. Use these criteria:
   - **Easy**: Textbook exercise, proof strategy is immediately obvious, involves ≤ 2 definitions.
   - **Moderate**: Standard result but non-trivial, multiple possible approaches.
   - **Difficult**: Research-level, multiple interacting definitions, no obvious strategy.

Write in rigorous, concise mathematical language. This file must be fully self-contained —
all subsequent phases use ONLY this file as input, not the original user input.

Return a JSON summary:
{{"difficulty": "difficult|moderate|easy", "hypothesis_count": N, "proposition_summary": "one line"}}
"""

# ---------------------------------------------------------------------------
# Phase 2 — Literature survey (optional, difficult problems only)
# ---------------------------------------------------------------------------

PHASE_2_SURVEY = """\
{preamble}

## Your Task: Phase 2 — Literature Survey

Read `proof_work/00_distilled.md` to understand the proposition and its context.

Perform a full literature survey. Write to `proof_work/00_survey.md`:

- **Problem classification**: Which area of mathematics (algebra, analysis, topology,
  combinatorics, etc.)? What sub-area?
- **Key objects and structures**: What are the central mathematical objects? What properties matter?
- **Hidden assumptions**: Are there implicit assumptions (e.g., working in a specific field,
  assuming separability)? List them.
- **Directly applicable theorems**: List each with full hypotheses — not just the name,
  but the precise conditions under which the theorem holds.
- **Closely related results**: Theorems that apply to similar but not identical settings —
  these help identify what makes this problem different.
- **Useful lemmas and inequalities**: Technical tools that might be needed (Cauchy-Schwarz,
  triangle inequality, dominated convergence, etc.).
- **Known counterexamples**: Examples showing that related but stronger/weaker statements
  are false. These reveal where the proof must be careful.

**Critical rule:** The survey does NOT propose proof strategies — it only maps the
mathematical landscape. Strategy choice happens in Phase 3, informed by the survey.

Return a JSON summary:
{{"applicable_theorems": N, "counterexamples": N, "key_objects": ["list"]}}
"""

# ---------------------------------------------------------------------------
# Phase 3 — Strategy + Decomposition
# ---------------------------------------------------------------------------

PHASE_3_STRATEGY_DECOMPOSITION = """\
{preamble}

## Your Task: Phase 3 — Proof Strategy and Decomposition

Read `proof_work/00_distilled.md` (proposition, hypotheses, definitions).
{survey_context}
{status_log_context}

### Part A: Proof Strategy

Determine and write to `proof_work/00_strategy.md`:

- **Proof strategy**: State the overall approach (direct, contradiction, contrapositive,
  induction, construction, etc.) and *why* this strategy is appropriate.
- **Known results to be used**: List any external theorems, lemmas, or well-known results
  you plan to invoke, with their precise statements. If unsure of the exact statement,
  flag it with ⚠️.
- **Key insights**: What is the core mathematical idea that makes this proof work?

### Part B: Decomposition into Lemmas

Break the proof into the smallest self-contained claims that chain together to yield the result.

For each lemma:
- **Lemma k**: State it precisely with quantifiers.
- **Depends on**: Which earlier lemmas or hypotheses it requires.
- **Why needed**: One sentence on how it connects to the main result.

Write a **dependency graph** showing the logical chain.

If the proof is simple enough (< 5 logical steps), say so and proceed as a single unit.

**Write the decomposition to `proof_work/01_decomposition.md`.**

Return a JSON summary:
{{"strategy": "description", "lemma_count": N, "lemmas": ["short description of each"], "dependency_chain": "description"}}
"""

# ---------------------------------------------------------------------------
# Phase 4 — Proof execution (one lemma at a time)
# ---------------------------------------------------------------------------

PHASE_4_PROOF_LEMMA = """\
{preamble}

## Your Task: Phase 4 — Prove Lemma {lemma_k}

### Load context
- Read `proof_work/00_distilled.md` (hypotheses, definitions).
- Read `proof_work/00_strategy.md` (proof strategy, known results).
- Read `proof_work/01_decomposition.md` (lemma statements and dependencies).
- Read `proof_work/status_log.md` if it exists — use the "Lessons for next iteration" entries to avoid repeating failed strategies.
{dependency_files}

### Write the proof
Write numbered steps. **Every step must carry exactly one justification tag:**

| Tag | Meaning |
|---|---|
| `[Hypothesis Hk]` | Directly invoking a stated assumption |
| `[Definition of X]` | Expanding or applying a formal definition |
| `[Theorem: Name]` | Applying a named theorem — state which hypotheses are satisfied and why |
| `[By Step n]` | Following from an earlier numbered step |
| `[By Lemma k]` | Following from a previously proved lemma |
| `[Algebraic manipulation]` | Routine algebra/calculus — show the work |
| `[Logic: rule]` | A logical inference rule |

**Rules:**
- Never write "clearly", "obviously", "trivially", "it is easy to see", or "by a standard argument."
- If a step requires checking preconditions of an invoked theorem, that check is a sub-step.
- If uncertain about any step, mark it with `[⚠️ GAP]` and explain. Do NOT silently bridge it.
- Proof by contradiction: state the negation explicitly with correct quantifiers.
- Induction: state base case, inductive hypothesis, and inductive step as separate labeled blocks.

### Save
Write the proof to `proof_work/proof_lemma_{lemma_k}.md` with this header:
```
## Lemma {lemma_k} — [Short description]
Status: DRAFT
Iteration: {iteration}
Gaps: [none / list of ⚠️ GAP descriptions]
```

Return a JSON summary:
{{"lemma": {lemma_k}, "steps": N, "status": "DRAFT", "gaps": ["list or empty"]}}
"""

# ---------------------------------------------------------------------------
# Phase 5 — Self-audit (hostile referee)
# ---------------------------------------------------------------------------

PHASE_5_AUDIT_LEMMA = """\
You are a hostile mathematical referee. Your job is to find errors in the proof below.
You have NO context about how or why this proof was written — judge it purely on its own merits.

Read the following files, then run the six-point audit check described below:
- `proof_work/00_distilled.md` (hypotheses, definitions)
- `proof_work/00_strategy.md` (proof strategy, known results)
- `proof_work/proof_lemma_{lemma_k}.md` (the proof to audit)
{dependency_files}

SIX-POINT CHECK:
1. **Justification audit**: For each step, is the cited justification actually sufficient? Does the cited theorem actually apply given the hypotheses? Check every precondition.
2. **Hypothesis fidelity**: Did the proof use anything not in the hypothesis list? Did it silently strengthen any assumption?
3. **Target fidelity**: Does the conclusion match the stated claim *exactly* — same quantifiers, same domains, same conditions?
4. **Edge cases**: Are degenerate/boundary cases covered? List them and verify each.
5. **Quantifier check**: Read every quantified statement. Is the scope correct? Are ∀ and ∃ in the right order?
6. **Circularity check**: Is the target proposition (or anything logically equivalent) used as an assumption?

For each check, output ✅ or ❌ with explanation for any failure.

Write your full audit to `proof_work/audit_lemma_{lemma_k}_iter_{iteration}.md`.

Return a JSON summary:
{{"lemma": {lemma_k}, "iteration": {iteration}, "checks": ["✅ or ❌ for each of the 6"], "failures": ["brief description of each ❌"]}}
"""

# ---------------------------------------------------------------------------
# Phase 6 — Gap resolution and forking
# ---------------------------------------------------------------------------

PHASE_6_GAP_ANALYSIS = """\
{preamble}

## Your Task: Phase 6 — Gap Analysis for Lemma {lemma_k}

Read:
- `proof_work/00_distilled.md`
- `proof_work/00_strategy.md`
- `proof_work/proof_lemma_{lemma_k}.md`
- `proof_work/audit_lemma_{lemma_k}_iter_{iteration}.md`

For each ❌ in the audit, classify the gap:
- **Fixable**: A missing sub-step that can be filled → describe the fix.
- **Crucial**: Requires an assumption not in hypotheses → create fork analysis.
- **Fatal**: Proposition may be false or unprovable → report to user.

For each **crucial** gap, create `proof_work/fork_lemma_{lemma_k}_gap_{{j}}.md` containing:
- The gap (precise description)
- Minimal additional assumption needed
- Why original hypotheses are insufficient
- Alternative strategies
- Recommendation

Return a JSON summary:
{{"lemma": {lemma_k}, "fixable": N, "crucial": N, "fatal": N, "fork_files": ["list of created fork files"]}}
"""

# ---------------------------------------------------------------------------
# Phase 7 — Revision
# ---------------------------------------------------------------------------

PHASE_7_REVISION = """\
{preamble}

## Your Task: Phase 7 — Revise Lemma {lemma_k}

Read:
- `proof_work/audit_lemma_{lemma_k}_iter_{iteration}.md`
- `proof_work/proof_lemma_{lemma_k}.md`
- `proof_work/00_distilled.md`
- `proof_work/00_strategy.md`
{fork_context}

Rewrite affected steps with corrected justifications.
If a gap was resolved via forking, integrate the chosen resolution and update
`proof_work/00_distilled.md` with any new hypotheses (marked as `(added)`).

Update the status header:
```
Status: REVISED
Iteration: {next_iteration}
```

Overwrite `proof_work/proof_lemma_{lemma_k}.md` with the revised version.

**After revising, append to `proof_work/status_log.md`:**
```
## Iteration {iteration} — Lemma {lemma_k}
### What failed
[List the specific audit checks that failed]
### What was tried
[Brief description of the approach in this iteration]
### What changed
[List of steps rewritten and why]
### Lessons for next iteration
[What this failure reveals — e.g., "direct approach fails because X, try contradiction next"]
```

Return a JSON summary:
{{"lemma": {lemma_k}, "iteration": {next_iteration}, "steps_changed": N, "all_issues_addressed": true/false}}
"""

# ---------------------------------------------------------------------------
# Phase 9 — Cold read assembly (sub-phases a–d)
# ---------------------------------------------------------------------------

PHASE_9A_COMPILE = """\
{preamble}

## Your Task: Phase 9a — Compile the proof

Read all `proof_work/proof_lemma_*.md` files in order (by lemma number), WITHOUT reading
any working notes or audit files. Also read `proof_work/00_distilled.md` and
`proof_work/00_strategy.md` for context.

Assemble them into a single coherent proof flow. Do not modify the content —
just read and prepare for the cold read audit.

Write the assembled order to `proof_work/assembled_proof_order.md` listing the
files read and their lemma numbers.

Return a JSON summary:
{{"lemma_count": N, "lemma_files": ["list of files in order"]}}
"""

PHASE_9B_COLD_READ = """\
You are a fresh mathematical reviewer performing a cold read of an assembled proof.
You have NO memory of the proof-writing or per-lemma audit process.

Read:
- `proof_work/00_distilled.md`
- `proof_work/00_strategy.md`
- All `proof_work/proof_lemma_*.md` files in order

Check:
- Do the lemmas chain together correctly?
- Are notation and conventions consistent?
- Does the final step yield the target proposition?
- Are there inter-lemma gaps invisible in per-lemma audits?

Write findings to `proof_work/cold_read_audit.md`.

For any critical gap that CANNOT be resolved, mark it with `[UNRESOLVED CRITICAL GAP]`.

Return a JSON summary:
{{"clean_pass": true/false, "issues_found": N, "issues_fixed": N, "unresolved_critical": N, "descriptions": ["list of issues"]}}
"""

PHASE_9C_FINAL_PROOF = """\
{preamble}

## Your Task: Phase 9c — Write the final proof

Read:
- `proof_work/00_distilled.md`
- `proof_work/00_strategy.md`
- All `proof_work/proof_lemma_*.md` files in order
- `proof_work/cold_read_audit.md`

Write to `proof_work/final_proof.md` in clean mathematical style, preserving justification tags.

If cold read passed cleanly (no `[UNRESOLVED CRITICAL GAP]` markers):
- End with ∎

If unresolved critical gaps exist:
- Include a prominent `## UNRESOLVED GAPS` section immediately after the Proof Health line
- Mark each unresolved gap inline at the relevant step with `[UNRESOLVED: description]`
- End with `□ (INCOMPLETE — see unresolved gaps)` instead of ∎

Return a JSON summary:
{{"complete": true/false, "unresolved_gaps": N}}
"""

PHASE_9D_JOURNAL = """\
{preamble}

## Your Task: Phase 9d — Compile the proof journal

Merge all working files into `proof_work/proof_journal.md`:

If any unresolved critical gaps remain, list them prominently at the TOP of the journal.

Then include in order:
- Distilled problem (from 00_distilled.md)
- Strategy (from 00_strategy.md)
- Decomposition (from 01_decomposition.md)
- Each lemma's proof evolution (all iterations)
- All audit reports
- All fork analyses
- Cold read notes
- Final assembled proof

This journal is the audit trail showing where difficulties arose.

Return a JSON summary:
{{"sections": N, "has_unresolved_gaps": true/false}}
"""


def format_prompt(template: str, **kwargs) -> str:
    """Format a prompt template with the given keyword arguments."""
    kwargs.setdefault("preamble", SKILL_PREAMBLE)
    return template.format(**kwargs)


def get_dependency_files_text(dependencies: list[int]) -> str:
    """Generate the dependency file reading instructions for a lemma."""
    if not dependencies:
        return "- No dependency lemmas to read."
    lines = ["- Read the proofs of dependency lemmas:"]
    for dep in dependencies:
        lines.append(f"  - `proof_work/proof_lemma_{dep}.md`")
    return "\n".join(lines)
