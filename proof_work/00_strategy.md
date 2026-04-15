# Proof Strategy: Irrationality of √2

## Proof Strategy

**Approach:** Proof by contradiction (reductio ad absurdum), using the "lowest terms" normalization.

**Why this strategy is appropriate:**
The proposition is a *non-existence* statement: no integers $p, q$ (with $q \neq 0$) satisfy $p^2 = 2q^2$. Direct proofs of non-existence are typically unwieldy, since one would have to inspect all candidate pairs. Contradiction is the natural fit: *assume* such a pair exists, extract from it a canonical (lowest-terms) representative, and derive a contradiction with the canonical property itself. The contradiction arises from a parity/divisibility argument that is elementary and uses only the hypotheses listed (H1–H4). Induction is not needed; construction is inapplicable (we are proving the *absence* of an object); contrapositive does not simplify the statement since the proposition has no antecedent to negate.

## Known Results to be Used

1. **Lowest-terms representation (reduction lemma).** For every rational $p/q$ with $p, q \in \mathbb{Z}$, $q \neq 0$, there exist integers $p', q'$ with $q' > 0$, $\gcd(p', q') = 1$, and $p/q = p'/q'$ (equivalently, $p q' = p' q$). *Justification available:* Follows from H3 (unique factorization / gcd exists) by dividing both by $\gcd(p, |q|)$. ⚠️ We will re-derive the piece we need (coprime representative) rather than cite it as a black box, to keep the proof self-contained. Alternatively, we will use the well-ordering principle (H4) on the set of positive denominators.

2. **Parity lemma: "$n^2$ even $\Rightarrow n$ even".** For every $n \in \mathbb{Z}$, if $2 \mid n^2$ then $2 \mid n$. *Justification:* Follows from the definition of even/odd (every integer is $2k$ or $2k+1$) and direct computation: $(2k+1)^2 = 4k^2 + 4k + 1 = 2(2k^2+2k)+1$, which is odd. This is the *contrapositive* form: "$n$ odd $\Rightarrow n^2$ odd". This lemma does NOT require unique factorization — only the definition of odd/even and ring arithmetic in $\mathbb{Z}$.

3. **Elementary ring arithmetic in $\mathbb{Z}$.** Associativity, commutativity, distributivity, and cancellation laws for $+$ and $\cdot$ on $\mathbb{Z}$; in particular, if $a, b, c \in \mathbb{Z}$ and $a = b$ then $a \cdot c = b \cdot c$, and $(2k)^2 = 4k^2 = 2(2k^2)$.

4. **Well-ordering of $\mathbb{N}$ (H4).** Every nonempty subset of $\mathbb{N}$ has a least element. Used (optionally) to pick a minimal denominator, sidestepping an explicit appeal to gcd/unique factorization.

## Key Insights

The **core mathematical idea** is a *parity cascade*:

> If $p^2 = 2q^2$, then $p^2$ is even, so $p$ is even, so $p = 2m$, so $4m^2 = 2q^2$, so $q^2 = 2m^2$, so $q^2$ is even, so $q$ is even. Hence $2$ divides *both* $p$ and $q$ — which contradicts the assumption that $p/q$ is in lowest terms (i.e., $\gcd(p,q) = 1$).

Two supporting observations make this work cleanly:

- **(Parity lemma)** The implication "$p^2$ even $\Rightarrow p$ even" is the one non-trivial step; everything else is substitution and arithmetic. It is cheap to prove via the contrapositive on odd integers.
- **(Lowest-terms normalization)** Without reducing to lowest terms first, the parity cascade could be applied infinitely (producing a descent) but the contradiction is cleanest when we have a *single* coprime pair and observe that $2$ is a common divisor. Equivalently, one can phrase the contradiction as infinite descent via H4: the set of positive $q$ for which $p^2 = 2q^2$ has a solution would have no minimum, contradicting well-ordering. We will use the lowest-terms version for clarity.
