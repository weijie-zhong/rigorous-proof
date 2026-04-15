# Audit of Lemma 3 — Iteration 1

**Lemma 3 statement.** Let $p, q \in \mathbb{Z}$ with $q \neq 0$. If $p^2 = 2 q^2$, then $2 \mid p$ and $2 \mid q$.

## 1. Justification audit

- **Step 2 (k := q²).** Cites H1 closure under $\cdot$. Valid.
- **Step 3 (2 | p²).** Definition of divides: $a \mid b \iff \exists k \in \mathbb{Z}, b = ak$. Here $p^2 = 2k$ with $k = q^2 \in \mathbb{Z}$. Valid.
- **Step 4 (apply Lemma 1).** Lemma 1 Part B (line 22 of proof_lemma_1.md): $\forall n \in \mathbb{Z}, 2 \mid n^2 \Rightarrow 2 \mid n$. Instantiated at $n = p$. Preconditions $p \in \mathbb{Z}$ (Step 1) and $2 \mid p^2$ (Step 3) satisfied. Valid.
- **Step 5 (p = 2m).** Standard existential instantiation from definition of divides. Valid.
- **Steps 6–8 (squaring and expansion).** Pure ring arithmetic in $\mathbb{Z}$, H1. Valid.
- **Step 9 (combine).** Transitivity of equality. Valid.
- **Step 10 (cancel 2).** Uses that $\mathbb{Z}$ is an integral domain and $2 \neq 0$. H1 supports $\mathbb{Z}$'s ring structure; cancellation by a nonzero element in an integral domain is standard. Valid.
- **Steps 11–12 (2 | q²).** Symmetry of equality + definition of divides with $k' = m^2 \in \mathbb{Z}$. Valid.
- **Step 13 (apply Lemma 1 to q).** Same as Step 4, instantiated at $n = q$. Valid.
- **Steps 14–15 (conjunction, universal generalization).** Standard. Valid.

✅ All justifications sufficient.

## 2. Hypothesis fidelity

The proof uses only: H1 (ring/integral domain structure of $\mathbb{Z}$), Lemma 1 (declared dependency). No silent strengthening. Lemma 3's stated dependencies match exactly.

✅ Pass.

## 3. Target fidelity

Statement proved (Step 15): for all $p \in \mathbb{Z}$, $q \in \mathbb{Z}$ with $q \neq 0$, $p^2 = 2q^2 \Rightarrow (2 \mid p \wedge 2 \mid q)$. Matches Lemma 3 statement exactly — same quantifiers ($\forall p, q$), same domain ($\mathbb{Z}$, $q \neq 0$), same conclusion ($2 \mid p \wedge 2 \mid q$).

✅ Pass.

## 4. Edge cases

- **p = 0:** Then $p^2 = 0 = 2q^2$, so $q^2 = 0$, so $q = 0$ — but $q \neq 0$ is assumed, so this sub-case is vacuous. Even if we ignored that, $0 = 2 \cdot 0$ so $2 \mid 0$ trivially; Lemma 1 handles $n = 0$ (even) without issue.
- **p < 0:** Sign does not affect divisibility; $p^2 = (-p)^2$, and Lemma 1 is stated for all $n \in \mathbb{Z}$.
- **q < 0:** Same — $q^2 > 0$ regardless.
- **Cancellation of 2 in Step 10:** Requires $2 \neq 0$ in $\mathbb{Z}$, explicitly verified.
- **q ≠ 0 unused:** The hypothesis $q \neq 0$ is not invoked in the proof, but that is fine — the statement is still proved for the restricted domain.

✅ Pass.

## 5. Quantifier check

Step 1 fixes arbitrary $p, q$ (universal introduction). Step 15 discharges via universal generalization + conditional introduction. Step 5's existential ($\exists m$) is properly instantiated and the resulting free variable is used consistently. Lemma 1 applications instantiate a universal at a specific integer — valid. No quantifier order issues.

✅ Pass.

## 6. Circularity check

Lemma 3 does not appeal to Lemma 4 (the main theorem) or to any equivalent of "$\sqrt{2}$ is irrational." Dependencies: Lemma 1 (proved independently from H1/H3) and H1 only. No cycle.

✅ Pass.

---

## Summary

All six checks pass. Lemma 3's proof is rigorous and correctly justified.
