# Audit of Lemma 1, Iteration 1

**Lemma statement.** For every $n \in \mathbb{Z}$: (A) if $n$ is odd then $n^2$ is odd; equivalently (B) if $2 \mid n^2$ then $2 \mid n$.

Lemma 1 has no dependencies on other lemmas (depends only on H1 and H3).

## 1. Justification audit — ✅

- **Step 2**: "$n$ odd $\Rightarrow \exists k, n = 2k+1$" — direct from definition of odd (per distilled problem).
- **Steps 3–5**: Pure ring-arithmetic expansion $(2k+1)^2 = 4k^2+4k+1 = 2(2k^2+2k)+1$. Uses only distributivity/associativity/commutativity, licensed by H1.
- **Step 7**: $2k^2+2k \in \mathbb{Z}$ by closure of $\mathbb{Z}$ under $+,\cdot$ (H1). ✅
- **Step 9**: $n^2 = 2m+1$ matches the definition of odd. ✅
- **Step 12**: Parity dichotomy — stated in the distilled definitions ("Every integer is exactly one of even or odd"), which is part of H3's parity clause. ✅
- **Step 13**: $n$ even $\Rightarrow n = 2k \Rightarrow 2 \mid n$ is literally the definition of divides applied to the definition of even. ✅
- **Steps 15–18**: Unpack "$n^2$ odd" as $n^2 = 2j+1$, "$n^2$ even" as $n^2 = 2\ell$, equate, get $2(\ell-j)=1$. Subtraction closure from H1. ✅
- **Step 19**: $1 = 2\cdot 0 + 1$ witnesses $1$ is odd; parity dichotomy (H3) says $1$ cannot be both even and odd. ✅
- **Steps 20–21**: Clean reductio + disjunction elimination. ✅

All justifications are sufficient; every cited fact is in the hypothesis/definition inventory.

## 2. Hypothesis fidelity — ✅

The proof invokes only H1 (integer ring arithmetic + closure) and H3 (definitions of even/odd and parity dichotomy). No appeal to unique factorization, no appeal to Lemma 2/3/4. No hidden strengthening of hypotheses.

## 3. Target fidelity — ✅

Statement proved:
- Part A: $\forall n \in \mathbb{Z},\ n\text{ odd} \Rightarrow n^2\text{ odd}$.
- Part B: $\forall n \in \mathbb{Z},\ 2 \mid n^2 \Rightarrow 2 \mid n$.

Both match the lemma statement verbatim — same quantifier, same domain $\mathbb{Z}$, same condition.

## 4. Edge cases — ✅

- $n = 0$: $0$ is even ($0 = 2 \cdot 0$), handled by Case 1 of Part B; Part A is vacuous here since $0$ is not odd (dichotomy).
- $n = 1$: odd, $n^2 = 1$, which is $2\cdot 0 + 1$, odd. Fine.
- $n = -1$: $-1 = 2\cdot(-1) + 1$, $k = -1 \in \mathbb{Z}$; proof's algebra still yields $n^2 = 4k^2+4k+1 = 1$, odd. ✅
- Negative integers generally: $k$ ranges over all of $\mathbb{Z}$ (definition of odd uses $k \in \mathbb{Z}$), so no sign restriction sneaks in.
- $n^2 = 1$ edge (smallest odd square): Step 15's existence of $j$ with $n^2 = 2j+1$ holds with $j=0$, and Step 16's $\ell$ would have to give $2\ell=1$, which is where the contradiction lands. Correct.

No uncovered degenerate cases.

## 5. Quantifier check — ✅

- Part A: "Let $n \in \mathbb{Z}$ be arbitrary" (Step 1), proceeds under that assumption, discharges via universal generalization in Step 10. Correct scope.
- Part B: Same structure (Steps 11 and 22). Correct.
- Inner $\exists k$ in Step 2, $\exists j$ in Step 15, $\exists \ell$ in Step 16 are all correctly introduced from definition of odd/even and are fresh variables within each case. No captured variables, no $\exists/\forall$ swap.

## 6. Circularity check — ✅

Does not reference Lemma 2, 3, or 4, nor anything logically equivalent to the main target ($\sqrt 2 \notin \mathbb Q$). The only facts used are pre-lemma hypotheses H1 and H3. No circularity.

---

## Verdict

All six checks pass. The proof is rigorous, uses only permitted hypotheses, covers all edge cases, and has correct quantifier discipline. Minor stylistic note (not an error): Part B could have concluded the Case 2 contradiction more directly by applying Part A's result "n² odd" against the parity dichotomy for $n^2$ (rather than unpacking into $2j+1 = 2\ell$), but the longer route is correct.

**No failures found.**
