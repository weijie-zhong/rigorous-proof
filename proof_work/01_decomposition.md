# Lemma Decomposition — General Premium-Family Bundle Dominance

## Overview

The proof is decomposed into 14 lemmas. Lemmas 1–11 establish the sufficiency
direction (Part I). Lemmas 12–13 establish the two converse directions
(Parts II(a) and II(b)). Lemma 14 is the main theorem combining all three
parts.

---

## Lemma 1 — Cone Sign Lemma (Cone Dominance from Upper-Set Property)

**Statement.** Let $\mathcal{F} \subseteq 2^{[N]} \setminus \{\emptyset\}$
be an upper set in $(2^{[N]}, \subseteq)$, and let $B_k \in \mathcal{F}$.
Then for every $h \in K^{\mathcal{F}}_{B_k}$ and every $j \notin B_k$:
$$
h_j \le 0.
$$

**Depends on:** H3 (upper-set structure), Definition 1 (direction cone).

**Why needed:** This is the foundational lattice-theoretic step. It shows
that the upper-set property forces all non-$B_k$ coordinates to be
non-positive in the direction cone, which is the key to bounding non-premium
bundle values in Lemma 2. Without this, there is no control over the cost of
non-premium bundles relative to premium bundles.

---

## Lemma 2 — Non-Premium Value Bound

**Statement.** Let $\mathcal{F}$ be an upper set, $B_k \in \mathcal{F}$, and
$h \in K^{\mathcal{F}}_{B_k}$. Suppose $h = x^1 - x^2$ with
$x^1, x^2 \in D$. Then for every non-premium bundle
$B' \in \mathcal{F}^c$:
$$
\sum_{i \in B'} h_i
\;\le\; S_+(h)
\;:=\; \sum_{\substack{i \in B_k \\ h_i > 0}} h_i
\;\le\; \varepsilon_k(x^2)
\;:=\; \bar{s}_k - s_k(x^2).
$$

Consequently, $c^P(h) \le \max(0, \varepsilon_k(x^2))= \varepsilon_k(x^2)$.

**Depends on:** Lemma 1, Definition 3 (cell sum, deficit), Definition 4
(positive-displacement sum).

**Why needed:** Provides the universal upper bound on non-premium bundle
values within the direction cone. This bound is the "target" that the
obliqueness parameter must exceed (after $\alpha$-amplification) in the
threshold derivation (Lemma 9).

---

## Lemma 3 — Selling Cells are $\preceq_{B_k}$-Upper Sets

**Statement.** Let $M$ be optimal for the $\mathcal{F}$-restricted problem
(H4) with selling cells $C_1, \ldots, C_K$ and active bundles
$B_1, \ldots, B_K \in \mathcal{F}$. Assume the face assignment condition
(H6). Then for each $k \ge 1$, the selling cell $C_k$ is an upper set in
$(D, \preceq_{B_k})$: if $x \in C_k$ and $x \preceq_{B_k} x'$ with
$x' \in D$, then $x' \in C_k$.

**Depends on:** H3, H4, H6, Definition 2 (partial order $\preceq_{B_k}$).

**Why needed:** This is the geometric input for the EPW conditioning step
(Lemma 4). The event $\{X \in C_k\}$ must be increasing under
$\preceq_{B_k}$ for EPW to apply.

---

## Lemma 4 — Preserved Positive Association on Cells

**Statement.** Let $f$ be $\preceq_{B_k}$-MTP2 on $D$ (H9). Let $C_k$ be a
$\preceq_{B_k}$-upper set in $D$ (Lemma 3). Then the conditional distribution
of $X$ given $X \in C_k$ is positively associated under $\preceq_{B_k}$:
for any two bounded measurable $\preceq_{B_k}$-increasing functions
$\phi, \psi: D \to \mathbb{R}$,
$$
\operatorname{Cov}(\phi(X), \psi(X) \mid X \in C_k) \ge 0.
$$

**Depends on:** H9 ($\preceq_{B_k}$-MTP2), Lemma 3, Karlin--Rinott (c)
(MTP2 $\Rightarrow$ positive association), EPW (conditioning on increasing
events preserves positive association).

**Why needed:** Positive association on cells is the probabilistic foundation
for the stochastic dominance argument in Lemma 6. It ensures that boundary
mass and interior mass can be compared via increasing-function integrals.

---

## Lemma 5 — Conditional MTP2 Given Cell Sum (Karlin--Rinott Extension)

**Statement.** Let $f$ be $\preceq_{B_k}$-MTP2 on $D$ (H9), and let
$C_k$ be a $\preceq_{B_k}$-upper set. For each value
$s \in (0, \bar{s}_k)$, the conditional density
$$
f_{k,s}(x) := f(x \mid X \in C_k,\; s_k(X) = s)
$$
is MTP2 on the slice
$\{x \in C_k : s_k(x) = s\}$ (in the coordinates of $B_k$, with the
non-$B_k$ coordinates retaining the $\preceq_{B_k}$-flipped order).

**Depends on:** H9, Lemma 3, Karlin--Rinott (a) (conditional MTP2), partial-sum
extension via $\varepsilon$-perturbation and dominated convergence.

**Why needed:** Conditional MTP2 on slices is needed for the Strassen coupling
step within each level set of $s_k$. It ensures that the conditional
distributions on slices satisfy the positive association conditions needed
for the multivariate monotone coupling.

---

## Lemma 6 — $\preceq_{B_k}$-Stochastic Dominance of Boundary over Interior

**Statement.** Under hypotheses H7 (tail dominance), H8 (cell inclusivity),
H9 (MTP2), H10 (decreasing radial score), and using Lemmas 4–5:

For each selling cell $k$, $\nu^+|_{C_k}$ stochastically dominates
$\nu^-|_{C_k}$ in the $\preceq_{B_k}$ order. That is, for every bounded
measurable $\preceq_{B_k}$-increasing function $\phi: D \to \mathbb{R}$:
$$
\int_{C_k} \phi \, d\nu^+ \;\ge\; \int_{C_k} \phi \, d\nu^-.
$$

**Depends on:** H7, H8, H9, H10, Lemma 4, Lemma 5, FKG inequality,
Karlin--Rinott (b) (TP2 kernel of conditional expectations), monotone
coupling lemma (for $s_k$-marginals), Definition 5 (boundary/interior tails),
Definition 7 (radial score), Definition 10 (crossing point), Definition 11
(cell-level inclusivity threshold).

**Why needed:** This is the stochastic dominance condition required by
Strassen's theorem (Lemma 7) to construct the oblique coupling. It is the
probabilistic heart of the sufficiency proof, converting the analytic
hypotheses (MTP2, tail dominance, decreasing radial score) into a
measure-theoretic ordering.

**Proof sub-structure (sketch):**
1. Disintegrate $\nu^\pm|_{C_k}$ along $s_k$ into level-set conditionals.
2. For the $s_k$-marginals: H7 gives $B_k(q) \ge I_k(q)$ tail dominance
   for $q > p_k$, and H8 ($p_k < s_*^k$) combined with H5/H6 ensures
   sufficient boundary mass above the crossing point.
3. For conditional distributions on each slice $\{s_k = s\}$: Lemma 5
   gives MTP2, and H10 ($\Phi$ decreasing) ensures that $w(x)/f(x)$ is
   $\preceq_{B_k}$-decreasing, so the boundary conditional (proportional
   to $f$) stochastically dominates the interior conditional (proportional
   to $w = f \cdot \Phi$) via FKG / positive association.
4. Combine the two layers (marginal + conditional) to obtain full
   $\preceq_{B_k}$-stochastic dominance.

---

## Lemma 7 — Cell-Level Oblique Coupling

**Statement.** Under the hypotheses and conclusions of Lemma 6: for each
selling cell $k \ge 1$, there exists a non-negative measure $\gamma_k$ on
$C_k \times C_k$ such that:

(i) $(\gamma_k)_1 = \nu^+|_{C_k}$ and $(\gamma_k)_2 = \nu^-|_{C_k}$.

(ii) For $\gamma_k$-a.e. $(x^1, x^2)$: $x^1 - x^2 \in K^{\mathcal{F}}_{B_k}$
(cone support).

(iii) There exists $\lambda_k \in (0,1)$ such that for $\gamma_k$-a.e.
$(x^1, x^2)$:
$$
\sum_{i \in B_k} (x^1_i - x^2_i) \;\ge\; \lambda_k \cdot \varepsilon_k(x^2).
$$

**Depends on:** Lemma 6, Strassen's theorem (applied in $(D, \preceq_{B_k})$),
Definition 9 (obliqueness parameter).

**Why needed:** Provides the coupling that will become the cell-level component
of the aggregate transport plan. The obliqueness bound (iii) is the
quantitative input for the threshold derivation.

---

## Lemma 8 — Cost Equality on Direction Cone

**Statement.** Let $M$ be optimal for the $\mathcal{F}$-restricted problem
with active bundle $B_k \in \mathcal{F}$ and slope $q^{B_k}$ on cell $C_k$.
Then for every $h \in K^{\mathcal{F}}_{B_k}$:
$$
q^{B_k} \cdot h \;=\; c^{\mathcal{F}}_\alpha(h)
\;=\; \alpha \sum_{i \in B_k} h_i.
$$

**Depends on:** H4 (restricted optimality), Definition 1 (direction cone),
Definition of $c^{\mathcal{F}}_\alpha$.

**Why needed:** This establishes that the slope $q^{B_k}$ attains the maximum
in the restricted cost function on the direction cone. It is a necessary
condition for the saddle-point verification: condition (2) of Definition 8
requires $q^k \cdot (y - y') = c(y, y')$ for transport pairs. Combined with
Lemma 9, it ensures this extends to the full cost.

---

## Lemma 9 — Threshold Cost Dominance

**Statement.** Let $B_k \in \mathcal{F}$, and let $(x^1, x^2)$ be a pair
in $C_k \times C_k$ with $h := x^1 - x^2 \in K^{\mathcal{F}}_{B_k}$ and
$\sum_{i \in B_k} h_i \ge \lambda_k \cdot \varepsilon_k(x^2)$ for some
$\lambda_k \in (0,1)$. If $\alpha \ge 1/\lambda_k$, then:
$$
c^{\mathcal{F}}_\alpha(h)
\;=\; \alpha \sum_{i \in B_k} h_i
\;\ge\; \alpha \lambda_k \cdot \varepsilon_k(x^2)
\;\ge\; \varepsilon_k(x^2)
\;\ge\; c^P(h).
$$
Consequently, $c_\alpha(h) = c^{\mathcal{F}}_\alpha(h)$.

**Depends on:** Lemma 2 (non-premium value bound $c^P(h) \le \varepsilon_k$),
Lemma 7 (obliqueness $\lambda_k$), Lemma 8 (cost equality on cone).

**Why needed:** This is the bridge between the cone dominance (lattice theory)
and the transport construction (optimal transport). It shows that for
$\alpha$ above the threshold, the restricted cost equals the full cost on
the support of the transport, so the restricted-optimal transport is also
full-optimal.

---

## Lemma 10 — Boundary Partition

**Statement.** Under H5 (geometric inclusivity: $F_j \cap C_0 = \emptyset$
for all $j$) and H6 (face assignment: $F_j \cap C_k \neq \emptyset \Rightarrow j \in B_k$):

(i) The boundary mass $\mu^\partial$ is fully supported in
$\bigcup_{k=1}^K C_k$:
$$
\mu^\partial = \sum_{k=1}^K \nu^+|_{C_k}.
$$

(ii) For each selling cell $k$, $\nu^+|_{C_k}$ is supported on the union
of faces $\{F_j : j \in B_k,\; F_j \cap C_k \neq \emptyset\}$.

**Depends on:** H5, H6, structure of $\mu^\partial$.

**Why needed:** Ensures that all positive boundary mass is accounted for in
the cell-level couplings $\gamma_k$. Without this, the aggregate transport
would have unmatched boundary mass, and the marginal identity (condition 3
of the saddle-point criterion) would fail.

---

## Lemma 11 — Part I: Sufficiency (Saddle-Point Verification)

**Statement (Part I of Main Theorem).** Under hypotheses H1–H10: there exist
obliqueness parameters $\lambda_1, \ldots, \lambda_K \in (0,1)$ such that $M$
is optimal for the full (unrestricted) problem whenever
$\alpha \ge \alpha^* := \max_{k=1,\ldots,K} 1/\lambda_k$.

Specifically, the aggregate transport
$$
\gamma \;:=\; (\delta_0 \otimes \mu^-|_{C_0})
\;+\; \sum_{k=1}^K \gamma_k
$$
satisfies all three conditions of the Saddle-Point Criterion (Definition 8)
for the full cost $c_\alpha$.

**Depends on:** Lemma 7 (cell-level couplings $\gamma_k$), Lemma 8 (cost
equality on cone), Lemma 9 (threshold: $c_\alpha = c^{\mathcal{F}}_\alpha$ on
support), Lemma 10 (boundary partition), H4 (restricted optimality for cell
mass balance), DDT Saddle-Point Criterion.

**Why needed:** This is the complete sufficiency statement. It assembles all
preceding lemmas into a verified optimal transport plan.

**Verification sketch:**
- **Condition 1 (cell compatibility):** $\gamma_k$ is supported on
  $C_k \times C_k$ by construction (Lemma 7). The origin component
  $\delta_0 \otimes \mu^-|_{C_0}$ is supported on $\{0\} \times C_0
  \subseteq C_0 \times C_0$. ✓
- **Condition 2 (cost equality):** For pairs in $\gamma_k$,
  $q^{B_k} \cdot h = c^{\mathcal{F}}_\alpha(h) = c_\alpha(h)$ by Lemmas 8–9.
  For the origin component, $q^0 \cdot (0 - y') = 0 = c_\alpha(0 - y')$
  since $-y' \in -D$ has all non-positive coordinates, so $c_\alpha(-y') = 0$. ✓
- **Condition 3 (marginal identity):** First marginal:
  $\gamma_1 = \delta_0 + \sum_k \nu^+|_{C_k} = \delta_0 + \mu^\partial = \mu^+$
  (using Lemma 10). Second marginal:
  $\gamma_2 = \mu^-|_{C_0} + \sum_k \nu^-|_{C_k} = \mu^-$ (using cell mass
  partition of interior mass). Hence $\gamma_1 - \gamma_2 = \mu^+ - \mu^- = \mu$. ✓

---

## Lemma 12 — Part II(a): Non-Upper-Set Implies Suboptimality

**Statement.** Let $N \ge 2$, $f \in C^2(D)$ with $f > 0$ (H1'), $w > 0$ on
$\operatorname{int}(D)$ (H2'). Let $\mathcal{F}$ be a nonempty family that is
**not** an upper set (H3'$\neg$): there exist $B_k \in \mathcal{F}$ and
$j \notin B_k$ with $B_k \cup \{j\} \notin \mathcal{F}$. Let $M$ be any
mechanism optimal for the $\mathcal{F}$-restricted problem.

Then for every $\alpha > 0$, $M$ is not optimal for the full problem.
Specifically, augmenting $M$ with the non-premium bundle $B_k \cup \{j\}$ at
a suitably chosen price strictly increases revenue.

**Depends on:** H1', H2', H3'$\neg$, envelope theorem.

**Why needed:** Establishes that the upper-set property (H3) cannot be
weakened in Part I — it is a necessary structural condition on $\mathcal{F}$.

**Proof sketch:**
1. Since $B_k \cup \{j\} \notin \mathcal{F}$, this bundle has additive
   valuation $\sum_{B_k} x_i + x_j$ (no $\alpha$-premium).
2. Types near the boundary of $C_k$ with high $x_j$ currently pay the
   $\alpha$-amplified price for $B_k$ but derive no utility from item $j$.
3. Offer $B_k \cup \{j\}$ at price $p_{B_k} + x_j^* - \varepsilon$ for a
   suitably chosen $x_j^*$. A positive-measure set of types with
   $x_j \ge x_j^*$ and marginal surplus from $B_k$ close to zero switch to
   the new bundle.
4. Revenue gain from switchers: $\Theta(\varepsilon)$ (positive-measure set,
   each paying a positive price).
5. Revenue loss from cannibalization of existing $C_k$ sales:
   $O(\varepsilon^2)$ (switching region is a thin shell of width
   $O(\varepsilon)$ with $O(\varepsilon)$ revenue difference per type).
6. Net effect: strictly positive for small $\varepsilon > 0$.

---

## Lemma 13 — Part II(b): Non-Inclusivity Implies Suboptimality

**Statement.** Let $N \ge 2$, $f \in C^2(D)$ with $f > 0$ (H1''), $w > 0$
on $\operatorname{int}(D)$ (H2''). Let $\mathcal{F}$ be an upper set with
$\mathcal{F} \neq 2^{[N]} \setminus \{\emptyset\}$ (H3''), with antichain
$\mathcal{A} = \min(\mathcal{F})$. Let $M$ be optimal for the
$\mathcal{F}$-restricted problem with exclusion cell $C_0$ and crossing
point $p > 0$.

Suppose there exists $j \notin \bigcap \mathcal{A}$ with $\bar{v}_j < p$
(H4''$\neg$), so that $F_j \cap C_0 \neq \emptyset$.

Then for every $\alpha > 0$, $M$ is not optimal for the full problem.
Specifically, offering the non-premium singleton $\{j\}$ at price
$\bar{v}_j - \varepsilon$ strictly increases revenue.

**Depends on:** H1'', H2'', H3'', H4''$\neg$, envelope theorem.

**Why needed:** Establishes that the inclusivity conditions (H5, H8) are
necessary — without them, there exist "stranded" high-value types in the
exclusion cell that can be profitably served.

**Proof sketch:**
1. Since $j \notin \bigcap \mathcal{A}$, there exists $A \in \mathcal{A}$
   with $j \notin A$. Then $\{j\} \not\supseteq A$ for this $A$, and since
   $|A| \ge 2$ (otherwise $A = \{j'\}$ for some $j' \neq j$, and $\{j\}$
   doesn't contain $\{j'\}$), $\{j\} \notin \mathcal{F}$. So $\{j\}$ is
   non-premium with valuation $x_j$.
2. Types in $C_0$ with $x_j \ge \bar{v}_j - \varepsilon$ have
   $v_{\{j\}}(x) = x_j \ge \bar{v}_j - \varepsilon$, so they are willing to
   pay at least $\bar{v}_j - \varepsilon$ for $\{j\}$.
3. Since $\bar{v}_j < p$ and $F_j \cap C_0 \neq \emptyset$ (by $\bar{v}_j < p$
   implying types with $x_j = \bar{v}_j$ and low other values are excluded),
   the set $C_0 \cap \{x_j \ge \bar{v}_j - \varepsilon\}$ has positive measure
   (since $f > 0$).
4. Revenue gain: $(\bar{v}_j - \varepsilon) \cdot \mu^-(C_0 \cap \{x_j \ge \bar{v}_j - \varepsilon\}) = \Theta(\varepsilon)$ (from newly served types).
5. Cannibalization: types switching from selling cells to $\{j\}$ are in a
   thin region of measure $O(\varepsilon^2)$.
6. Net: strictly positive for small $\varepsilon$.

---

## Lemma 14 — Main Theorem (Premium-Family Bundle Dominance)

**Statement.** Let $N \ge 2$, $D = \prod_{i=1}^N [0, \bar{v}_i]$, and
$f \in C^2(D)$ with $f > 0$ on $D$ and $w(x) > 0$ on $\operatorname{int}(D)$.
Let $\mathcal{F} \subseteq 2^{[N]} \setminus \{\emptyset\}$ be nonempty, and
let $M$ be optimal for the $\mathcal{F}$-restricted problem.

**(I) Sufficiency.** If $\mathcal{F}$ is an upper set satisfying H3–H10,
then there exist $\lambda_1, \ldots, \lambda_K \in (0,1)$ such that $M$ is
optimal for the full problem whenever
$\alpha \ge \alpha^* = \max_k 1/\lambda_k$.

**(II-a) Necessity of upper-set.** If $\mathcal{F}$ is not an upper set,
then $M$ is not optimal for the full problem for any $\alpha > 0$.

**(II-b) Necessity of inclusivity.** If $\mathcal{F}$ is an upper set with
$\mathcal{F} \neq 2^{[N]} \setminus \{\emptyset\}$, and there exists
$j \notin \bigcap \mathcal{A}$ with $\bar{v}_j < p$, then $M$ is not optimal
for the full problem for any $\alpha > 0$.

**Depends on:** Lemma 11 (Part I), Lemma 12 (Part II(a)), Lemma 13 (Part II(b)).

**Why needed:** This is the target theorem — the complete characterization of
when a restricted-optimal mechanism remains optimal for the full problem.

---

## Dependency Graph

```
Definitions: H1-H10, Defs 1-11
       │
       ├──────────────────────────────────────────────────┐
       │                                                  │
       ▼                                                  ▼
   Lemma 1                                          Lemma 3
 (Cone Sign)                                  (Cell Upper-Set)
       │                                          │         │
       ▼                                          ▼         ▼
   Lemma 2                                    Lemma 4   Lemma 5
 (Non-Prem                                 (Positive  (Cond MTP2
  Value Bound)                              Assoc)     on Slices)
       │                                      │    │       │
       │                                      │    └───┬───┘
       │                                      │        │
       │                                      ▼        ▼
       │                                     Lemma 6
       │                               (Stochastic Dominance:
       │                                 ν⁺ ≥_{B_k} ν⁻)
       │                                      │
       │                                      ▼
       │                                   Lemma 7
       │                              (Oblique Coupling
       │                                γ_k, λ_k > 0)
       │                                      │
       │         Lemma 8                      │
       │     (Cost Equality                   │
       │      on Cone)                        │
       │           │                          │
       └───────┐   │   ┌──────────────────────┘
               │   │   │
               ▼   ▼   ▼
              Lemma 9                      Lemma 10
         (Threshold Cost                 (Boundary
          Dominance:                      Partition)
          α ≥ 1/λ_k ⟹                       │
          c_α = c^F_α)                       │
               │                             │
               └──────────┬──────────────────┘
                          │
                          ▼
                      Lemma 11
                 (Part I: Sufficiency —
                  Saddle-Point Verified)
                          │
                          │      Lemma 12           Lemma 13
                          │   (Part II(a):       (Part II(b):
                          │    Non-upper-set      Non-inclusivity
                          │    ⟹ suboptimal)     ⟹ suboptimal)
                          │        │                    │
                          └────────┼────────────────────┘
                                   │
                                   ▼
                              Lemma 14
                         (MAIN THEOREM:
                      Premium-Family Bundle
                          Dominance)
```

### Critical path

The critical path for Part I runs through:
$$
\text{Lemma 1} \to \text{Lemma 2} \to \text{Lemma 9} \to \text{Lemma 11} \to \text{Lemma 14}
$$
and in parallel:
$$
\text{Lemma 3} \to \text{Lemma 4/5} \to \text{Lemma 6} \to \text{Lemma 7} \to \text{Lemma 9} \to \text{Lemma 11} \to \text{Lemma 14}
$$

These two paths merge at Lemma 9 (threshold cost dominance), which requires
both the non-premium value bound (from the lattice-theoretic path) and the
obliqueness parameter (from the probabilistic path).

Parts II(a) and II(b) (Lemmas 12–13) are independent of Part I and of each
other.

---

## Summary Table

| Lemma | Name | Layer | Technique | Difficulty |
|-------|------|-------|-----------|------------|
| 1 | Cone Sign | 1 | Lattice theory | Easy |
| 2 | Non-Premium Value Bound | 1 | Algebraic | Easy |
| 3 | Cell Upper-Set Property | 2 | Convex/polyhedral geometry | Medium |
| 4 | Preserved Positive Association | 2 | MTP2 + EPW | Medium |
| 5 | Conditional MTP2 on Slices | 2 | Karlin--Rinott + perturbation | Hard |
| 6 | Stochastic Dominance ν⁺ ≥ ν⁻ | 2 | FKG + disintegration | Hard |
| 7 | Cell-Level Oblique Coupling | 2 | Strassen's theorem | Medium |
| 8 | Cost Equality on Cone | 3 | Polyhedral / DDT | Easy |
| 9 | Threshold Cost Dominance | 3 | Algebraic chain | Easy |
| 10 | Boundary Partition | 4 | Geometric | Easy |
| 11 | Part I: Sufficiency | 5 | Saddle-point assembly | Medium |
| 12 | Part II(a): Upper-set necessity | — | Perturbation | Medium |
| 13 | Part II(b): Inclusivity necessity | — | Perturbation | Medium |
| 14 | Main Theorem | — | Assembly | Easy |

**Hardest lemmas:** Lemma 5 (conditional MTP2 via partial-sum extension) and
Lemma 6 (stochastic dominance via shifted-tail + FKG). These contain the
deepest probabilistic arguments and the most delicate hypotheses interactions.
