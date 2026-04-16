# Distilled Problem — General Premium-Family Bundle Dominance (with Converse)

**Difficulty:** difficult

(Research-level mechanism-design theorem generalizing core-bundle dominance.
The premium family is promoted from a principal filter $\{B : C \subseteq B\}$
to an arbitrary upper set in $(2^{[N]}, \subseteq)$. Part I (sufficiency)
requires a multi-layer argument: cone dominance from the upper-set property,
cell-level oblique transport via MTP2/FKG/Karlin--Rinott machinery, and
saddle-point verification. Part II (necessity) establishes two independent
converse directions via perturbation/augmentation arguments. At least 7
interacting definitions and 6+ lemmas are involved.)

---

## 1. Setup

### 1.1 Type space

**Items.** $[N] := \{1, \ldots, N\}$ with $N \ge 2$.

**Type space.** $D := \prod_{i=1}^{N} [0, \bar{v}_i]$, where each
$\bar{v}_i > 0$. The buyer's type is $x = (x_1, \ldots, x_N) \in D$, drawn
from a density $f$ on $D$.

### 1.2 Premium family and valuations

**Premium family.** $\mathcal{F} \subseteq 2^{[N]} \setminus \{\emptyset\}$
is a nonempty collection of bundles. The **non-premium family** is
$\mathcal{F}^c := \{B \subseteq [N] : B \neq \emptyset,\; B \notin \mathcal{F}\}$.

**Upper-set property.** $\mathcal{F}$ is an **upper set** (or **filter** in
the inclusion order) in the poset $(2^{[N]} \setminus \{\emptyset\}, \subseteq)$
if:
$$
B \in \mathcal{F} \text{ and } B \subseteq B' \subseteq [N]
\;\;\Longrightarrow\;\; B' \in \mathcal{F}.
$$

**Antichain of minimal elements.** When $\mathcal{F}$ is an upper set, define
$\mathcal{A} := \min(\mathcal{F})$, the set of inclusion-minimal elements
of $\mathcal{F}$. Then
$\mathcal{F} = \{B \subseteq [N] : B \supseteq A \text{ for some } A \in \mathcal{A}\}$.

**Valuations.** For each nonempty $B \subseteq [N]$ and type $x \in D$:
$$
v_B(x) \;:=\;
\begin{cases}
  \alpha \displaystyle\sum_{i \in B} x_i & \text{if } B \in \mathcal{F}, \\[6pt]
  \displaystyle\sum_{i \in B} x_i & \text{if } B \notin \mathcal{F},
\end{cases}
\qquad \alpha > 0.
$$

### 1.3 Cost functions

**Restricted cost** (only bundles in $\mathcal{F}$ available):
$$
c^{\mathcal{F}}_\alpha(h)
\;:=\; \max\!\Bigl(0,\; \max_{B \in \mathcal{F}}\, \alpha \sum_{i \in B} h_i\Bigr).
$$

**Non-premium cost** (bundles outside $\mathcal{F}$; independent of $\alpha$):
$$
c^{P}(h)
\;:=\; \max\!\Bigl(0,\; \max_{B \notin \mathcal{F}}\, \sum_{i \in B} h_i\Bigr).
$$

**Full cost** (all nonempty bundles available):
$$
c_\alpha(h) \;:=\; \max\bigl(c^{\mathcal{F}}_\alpha(h),\; c^{P}(h)\bigr).
$$

### 1.4 Restricted-optimal mechanism

$M$ is a piecewise-linear mechanism optimal for the $\mathcal{F}$-restricted
problem. It partitions $D$ into:

- **Exclusion cell** $C_0$: slope $q^0 = 0$ (buyer receives nothing).
- **Selling cells** $C_1, \ldots, C_K$: cell $C_k$ has active bundle
  $B_k \in \mathcal{F}$ and slope $q^{B_k}$ with $\mathbf{1}^\top q^{B_k} = 1$.

The mechanism is certified by a signed measure $\gamma^{\mathcal{F}}$
satisfying the Saddle-Point Criterion (Definition 8 below) with cost
$c^{\mathcal{F}}_\alpha$.

### 1.5 Signed measure $\mu$

The signed DDT measure on $D$ is
$$
\mu(A) \;=\; \mathbf{1}_A(0)
  \;+\; \sum_{i=1}^{N} \bar{v}_i \int_{F_i} \mathbf{1}_A \, f \, d\sigma_i
  \;-\; \int_A w(x)\, dx,
$$
where $F_i := \{x \in D : x_i = \bar{v}_i\}$ is the $i$-th top face,
$\sigma_i$ is its $(N{-}1)$-dimensional Lebesgue measure, and
$w(x) := \nabla f(x) \cdot x + (N{+}1)\,f(x)$ is the virtual density.

**Positive part:** $\mu^+ = \delta_0 + \mu^\partial$, where
$\mu^\partial := \sum_{i=1}^{N} \bar{v}_i \, f\, d\sigma_i$ is the
top-face boundary mass.

**Negative part:** $\mu^- = w(x)\, dx$ on $\operatorname{int}(D)$.

**Cell decomposition.** Restricted to each selling cell $k \ge 1$:
$\nu^+|_{C_k} := \mu^\partial|_{C_k}$, $\nu^-|_{C_k} := \mu^-|_{C_k}$.
Cell mass balance: $\nu^+(C_k) = \nu^-(C_k)$ for each $k \ge 1$
(a consequence of restricted optimality).

---

## 2. Key Definitions

**Definition 1 (Direction cone).** For each active bundle $B_k \in \mathcal{F}$:
$$
K^{\mathcal{F}}_{B_k}
\;:=\;
\Bigl\{ h \in \mathbb{R}^N \;:\;
  \sum_{i \in B_k} h_i \ge \sum_{i \in B'} h_i \;\;\forall\, B' \in \mathcal{F},
  \quad \sum_{i \in B_k} h_i \ge 0
\Bigr\}.
$$

**Definition 2 (Partial order).** For a bundle $B_k \subseteq [N]$, the
partial order $\preceq_{B_k}$ on $\mathbb{R}^N$ is defined by:
$$
x \preceq_{B_k} x' \;\;\Longleftrightarrow\;\;
\bigl(\forall\, i \in B_k:\; x_i \le x'_i\bigr)
\;\text{and}\;
\bigl(\forall\, j \notin B_k:\; x_j \ge x'_j\bigr).
$$

**Definition 3 (Cell sum, cell top, cell deficit).**
- $s_k(x) := \sum_{i \in B_k} x_i$.
- $\bar{s}_k := \sum_{i \in B_k} \bar{v}_i$.
- $\varepsilon_k(x) := \bar{s}_k - s_k(x) \ge 0$.

**Definition 4 (Positive-displacement sum).** For $h \in \mathbb{R}^N$ and
a bundle $B_k$:
$$
S_+(h) \;:=\; \sum_{\substack{i \in B_k \\ h_i > 0}} h_i.
$$

**Definition 5 (Boundary and interior tails).** For each selling cell $k$:
- $B_k(q) := \nu^+(C_k \cap \{s_k \ge q\})$ (boundary tail),
- $I_k(q) := \nu^-(C_k \cap \{s_k \ge q\})$ (interior tail).

**Definition 6 ($\preceq_{B_k}$-MTP2).** The density $f$ is
$\preceq_{B_k}$-MTP2 on $D$ if for all $x, y \in D$:
$$
f(x \vee_{B_k} y)\, f(x \wedge_{B_k} y) \;\ge\; f(x)\, f(y),
$$
where $\vee_{B_k}$ and $\wedge_{B_k}$ are the join and meet under the partial
order $\preceq_{B_k}$.

**Definition 7 (Radial score).** $\Phi(x) := \dfrac{\nabla f(x) \cdot x}{f(x)} + (N{+}1)$.

**Definition 8 (Saddle-Point Criterion, Daskalakis--Deckelbaum--Tzamos).**
Given a piecewise-linear mechanism with cells $\{C_k\}_{k=0}^K$ and slopes
$\{q^k\}$, a non-negative measure $\gamma$ on $D \times D$ **certifies
optimality** if:
1. **(Cell compatibility)** $\gamma(C_k \times C_k^c) = 0$ for every $k$.
2. **(Cost equality)** For $\gamma$-a.e. $(y, y')$ in $C_k \times C_k$:
   $q^k \cdot (y - y') = c(y, y')$.
3. **(Marginal identity)** $\gamma_1 - \gamma_2 = \mu$.

**Definition 9 (Obliqueness parameter).** For selling cell $k$, the
obliqueness parameter $\lambda_k \in (0, 1)$ is the largest constant such
that for all displacement pairs $(x^1, x^2)$ in the cell-level transport
$\gamma_k$:
$$
\sum_{i \in B_k}(x^1_i - x^2_i) \;\ge\; \lambda_k\, \varepsilon_k(x^2).
$$

**Definition 10 (Crossing point).** The crossing point $p_k$ of selling
cell $k$ is the supremum of values $q$ such that $B_k(q) > I_k(q)$ (boundary
tail dominates interior tail). The global crossing point is
$p := \max_k p_k$.

**Definition 11 (Cell-level inclusivity threshold).**
$s_*^k := \min\{\bar{v}_j : j \in B_k,\; F_j \cap C_k \neq \emptyset\}$.

---

## 3. Proposition — Part I (Sufficiency)

### Statement

**Theorem (Premium-Family Bundle Dominance — Sufficiency).**

Let $N \ge 2$, $D = \prod_{i=1}^N [0, \bar{v}_i]$, and let
$\mathcal{F} \subseteq 2^{[N]} \setminus \{\emptyset\}$ be an **upper set**
in $(2^{[N]}, \subseteq)$. Let $M$ be optimal for the $\mathcal{F}$-restricted
problem with selling cells $C_1, \ldots, C_K$, active bundles
$B_1, \ldots, B_K \in \mathcal{F}$, and exclusion cell $C_0$.

Assume the following hypotheses:

- **(H1) Density regularity.** $f \in C^2(D)$ and $f > 0$ on $D$.
- **(H2) Virtual positivity.** $w(x) := \nabla f(x) \cdot x + (N{+}1)\,f(x) > 0$
  for all $x \in \operatorname{int}(D)$.
- **(H3) Upper-set structure.** $\mathcal{F}$ is an upper set in
  $(2^{[N]}, \subseteq)$.
- **(H4) Restricted optimality.** $M$ is optimal for the $\mathcal{F}$-restricted
  problem, certified by a measure $\gamma^{\mathcal{F}}$ satisfying the
  Saddle-Point Criterion (Definition 8) with cost $c^{\mathcal{F}}_\alpha$.
- **(H5) Geometric inclusivity (GI).** For every item
  $j \in \{1, \ldots, N\}$: $F_j \cap C_0 = \emptyset$.
- **(H6) Face assignment (FA).** For every selling cell $k \ge 1$ and every
  item $j$ with $F_j \cap C_k \neq \emptyset$: $j \in B_k$.
- **(H7) Cell-level tail dominance (CR).** For every selling cell $k$:
  $B_k(q) > I_k(q)$ for all $q \in (p_k, \bar{s}_k)$.
- **(H8) Cell-level inclusivity (CI).** For every selling cell $k$:
  $p_k < s_*^k$.
- **(H9) $\preceq_{B_k}$-MTP2.** For every selling cell $k$, $f$ is
  $\preceq_{B_k}$-MTP2 on $D$ (Definition 6).
- **(H10) Decreasing radial score ($\Phi$dec).** For every selling cell $k$,
  $\Phi(x)$ (Definition 7) is $\preceq_{B_k}$-decreasing on $D$.

**Conclusion.** There exist obliqueness parameters $\lambda_1, \ldots, \lambda_K \in (0,1)$
such that $M$ is optimal for the **full** (unrestricted) problem whenever
$$
\alpha \;\ge\; \alpha^\star \;:=\; \max_{k=1,\ldots,K}\; \frac{1}{\lambda_k}.
$$

### Proof strategy sketch

The proof proceeds through five layers:

**Layer 1 — Cone Dominance Lemma.** Because $\mathcal{F}$ is an upper set
(H3), for every $B_k \in \mathcal{F}$ and $j \notin B_k$, we have
$B_k \cup \{j\} \in \mathcal{F}$. For any $h \in K^{\mathcal{F}}_{B_k}$:
$$
\sum_{i \in B_k} h_i \;\ge\; \sum_{i \in B_k \cup \{j\}} h_i
\;=\; \sum_{i \in B_k} h_i + h_j,
$$
forcing $h_j \le 0$ for all $j \notin B_k$. Consequently, for any
$B' \notin \mathcal{F}$:
$$
\sum_{i \in B'} h_i
\;=\; \underbrace{\sum_{i \in B' \cap B_k} h_i}_{\le\, S_+(h)}
  + \underbrace{\sum_{i \in B' \setminus B_k} h_i}_{\le\, 0}
\;\le\; S_+(h)
\;\le\; \varepsilon_k(x^2),
$$
where the last inequality uses $h = x^1 - x^2$ with $x^1, x^2 \in C_k \subseteq D$ and
$h_i \le \bar{v}_i - x^2_i$ for $i \in B_k$.

**Layer 2 — Cell-level oblique transport.** For each selling cell $k$,
construct a coupling $\gamma_k$ on $C_k \times C_k$ with marginals
$(\gamma_k)_1 = \nu^+|_{C_k}$ and $(\gamma_k)_2 = \nu^-|_{C_k}$, supported
on pairs $(x^1, x^2)$ satisfying:
- **Cone condition:** $x^1 - x^2 \in K^{\mathcal{F}}_{B_k}$.
- **Obliqueness:** $\sum_{B_k}(x^1_i - x^2_i) \ge \lambda_k\, \varepsilon_k(x^2)$.

This uses the shifted-tail inequality (H7, H8), Strassen's theorem with the
$\preceq_{B_k}$-MTP2 structure (H9), and the Karlin--Rinott conditional
theorems, applied cell-by-cell using $s_k = \sum_{i \in B_k} x_i$.

**Layer 3 — Threshold derivation.** Combining the cone dominance bound
$\max_{B' \notin \mathcal{F}} \sum_{B'} h_i \le S_+(h) \le \varepsilon_k$
with the obliqueness bound
$\alpha \sum_{B_k} h_i \ge \alpha \lambda_k \varepsilon_k$, whenever
$\alpha \ge 1/\lambda_k$ we get
$c^{\mathcal{F}}_\alpha(h) \ge c^{P}(h)$, hence $c_\alpha(h) = c^{\mathcal{F}}_\alpha(h)$.

**Layer 4 — Boundary partition.** Under (H5), $\mu^\partial$ is fully
supported in $\bigcup_{k \ge 1} C_k$, so
$\mu^\partial = \sum_{k \ge 1} \nu^+|_{C_k}$.

**Layer 5 — Saddle-point verification.** The aggregate transport
$\gamma := (\delta_0 \otimes \mu^-|_{C_0}) + \sum_{k \ge 1} \gamma_k$
satisfies all three conditions of the Saddle-Point Criterion for the full
cost $c_\alpha$ when $\alpha \ge \alpha^\star$.

---

## 4. Proposition — Part II(a) (Upper-set structure is necessary)

### Statement

**Proposition (Non-upper-set $\Longrightarrow$ suboptimality).**

Let $N \ge 2$, $D = \prod_{i=1}^N [0, \bar{v}_i]$, $f \in C^2(D)$ with
$f > 0$ on $D$. Let $\mathcal{F} \subseteq 2^{[N]} \setminus \{\emptyset\}$
be a nonempty family of bundles that is **not** an upper set. Let $M$ be any
mechanism optimal for the $\mathcal{F}$-restricted problem, with selling cells
$C_1, \ldots, C_K$ and active bundles $B_1, \ldots, B_K \in \mathcal{F}$.

Assume:

- **(H1') Density regularity.** $f \in C^2(D)$ and $f > 0$ on $D$.
- **(H2') Virtual positivity.** $w(x) > 0$ on $\operatorname{int}(D)$.
- **(H3'$\neg$) Non-upper-set.** $\mathcal{F}$ is **not** an upper set:
  there exist $B_k \in \mathcal{F}$ and $j \notin B_k$ such that
  $B_k \cup \{j\} \notin \mathcal{F}$.

**Conclusion.** For every $\alpha > 0$, $M$ is **not** optimal for the full
(unrestricted) problem. Specifically, augmenting $M$ with the non-premium
bundle $B_k \cup \{j\}$ at a suitably chosen price strictly increases revenue.

### Proof strategy sketch

Since $B_k \cup \{j\} \notin \mathcal{F}$, this bundle has additive (un-amplified)
valuation. Buyers near the boundary of cell $C_k$ with high $x_j$ currently
pay the $\alpha$-premium price for $B_k$ but receive no value from item $j$.
Offering $B_k \cup \{j\}$ at a price slightly below the $\alpha$-premium price
for $B_k$ captures a positive-measure set of such buyers. The revenue gain is
$\Theta(\varepsilon)$ (from buyers who switch from exclusion or who pay a
positive surplus for the new bundle) while cannibalization of existing cell-$k$
revenue is $O(\varepsilon^2)$ (the switching region is a thin shell).

---

## 5. Proposition — Part II(b) (Inclusivity is necessary)

### Statement

**Proposition (Non-inclusivity $\Longrightarrow$ suboptimality).**

Let $N \ge 2$, $D = \prod_{i=1}^N [0, \bar{v}_i]$, $f \in C^2(D)$ with
$f > 0$ on $D$. Let $\mathcal{F} \subseteq 2^{[N]} \setminus \{\emptyset\}$
be an upper set with $\mathcal{F} \neq 2^{[N]} \setminus \{\emptyset\}$
(so non-premium bundles exist). Let $\mathcal{A} = \min(\mathcal{F})$ be the
antichain of minimal elements of $\mathcal{F}$. Let $M$ be optimal for the
$\mathcal{F}$-restricted problem with exclusion cell $C_0$ and crossing point
$p > 0$.

Assume:

- **(H1'') Density regularity.** $f \in C^2(D)$ and $f > 0$ on $D$.
- **(H2'') Virtual positivity.** $w(x) > 0$ on $\operatorname{int}(D)$.
- **(H3'') Upper-set structure.** $\mathcal{F}$ is an upper set with
  $\mathcal{F} \neq 2^{[N]} \setminus \{\emptyset\}$.
- **(H4''$\neg$) Strict non-inclusivity.** There exists an item
  $j \notin \bigcap \mathcal{A}$ (i.e., $j$ is not contained in every
  minimal element of $\mathcal{F}$) such that $\bar{v}_j < p$, where $p$ is
  the crossing point. Equivalently, $F_j \cap C_0 \neq \emptyset$ — the top
  face of item $j$ meets the exclusion cell.

**Conclusion.** For every $\alpha > 0$, $M$ is **not** optimal for the full
problem. Specifically, the singleton bundle $\{j\}$ is non-premium (since
$\{j\} \not\supseteq A$ for any $A \in \mathcal{A}$, because $j$ is absent
from some generator), and augmenting $M$ with $\{j\}$ at price
$\bar{v}_j - \varepsilon$ strictly increases revenue.

### Proof strategy sketch

The singleton $\{j\}$ is non-premium, so its valuation is simply $x_j$ (no
$\alpha$-amplification). Types in the exclusion cell with $x_j$ close to
$\bar{v}_j$ have high willingness to pay for $\{j\}$ alone. Offering $\{j\}$
at price $\bar{v}_j - \varepsilon$ captures a positive-measure set of excluded
types (those with $x_j \ge \bar{v}_j - \varepsilon$ and low total value).
The revenue gain is $\Theta(\varepsilon)$ while cannibalization of existing
selling cells is $O(\varepsilon^2)$.

---

## 6. Hypotheses Inventory (Consolidated)

### Part I hypotheses

| Tag | Name | Statement |
|-----|------|-----------|
| H1 | Density regularity | $f \in C^2(D)$, $f > 0$ on $D$ |
| H2 | Virtual positivity | $w(x) := \nabla f(x) \cdot x + (N{+}1)f(x) > 0$ on $\operatorname{int}(D)$ |
| H3 | Upper-set structure | $\mathcal{F}$ is an upper set in $(2^{[N]}, \subseteq)$ |
| H4 | Restricted optimality | $M$ optimal for $\mathcal{F}$-restricted problem, certified by $\gamma^{\mathcal{F}}$ |
| H5 | Geometric inclusivity (GI) | $F_j \cap C_0 = \emptyset$ for every $j \in [N]$ |
| H6 | Face assignment (FA) | $F_j \cap C_k \neq \emptyset \Rightarrow j \in B_k$ |
| H7 | Cell-level tail dominance (CR) | $B_k(q) > I_k(q)$ for $q \in (p_k, \bar{s}_k)$, each $k$ |
| H8 | Cell-level inclusivity (CI) | $p_k < s_*^k$ for each $k$ |
| H9 | $\preceq_{B_k}$-MTP2 | $f$ is $\preceq_{B_k}$-MTP2 on $D$ for each $k$ |
| H10 | Decreasing radial score | $\Phi(x)$ is $\preceq_{B_k}$-decreasing on $D$ for each $k$ |

### Part II(a) hypotheses

| Tag | Name | Statement |
|-----|------|-----------|
| H1' | Density regularity | $f \in C^2(D)$, $f > 0$ on $D$ |
| H2' | Virtual positivity | $w(x) > 0$ on $\operatorname{int}(D)$ |
| H3'$\neg$ | Non-upper-set | $\exists\, B_k \in \mathcal{F},\; j \notin B_k$ with $B_k \cup \{j\} \notin \mathcal{F}$ |

### Part II(b) hypotheses

| Tag | Name | Statement |
|-----|------|-----------|
| H1'' | Density regularity | $f \in C^2(D)$, $f > 0$ on $D$ |
| H2'' | Virtual positivity | $w(x) > 0$ on $\operatorname{int}(D)$ |
| H3'' | Upper-set with non-premium bundles | $\mathcal{F}$ is an upper set, $\mathcal{F} \neq 2^{[N]} \setminus \{\emptyset\}$ |
| H4''$\neg$ | Strict non-inclusivity | $\exists\, j \notin \bigcap \mathcal{A}$ with $\bar{v}_j < p$ (equivalently, $F_j \cap C_0 \neq \emptyset$) |

---

## 7. Known Results Invoked

1. **Saddle-Point Criterion (Daskalakis--Deckelbaum--Tzamos).** See Definition 8.
2. **Strassen's Theorem (1965).** A coupling of $\mu_1, \mu_2$ supported on a
   closed set $K \subseteq X \times X$ exists iff every bounded measurable
   $K$-increasing function has weakly larger $\mu_1$-integral than $\mu_2$-integral.
3. **Monotone Coupling Lemma (Real line).** Finite Borel measures $\alpha, \beta$
   on $\mathbb{R}$ with equal total mass and
   $\alpha([r, \infty)) \ge \beta([r, \infty))$ for all $r$ admit a coupling
   supported on $\{(x, y) : x \ge y\}$.
4. **Karlin--Rinott (1980).** For an MTP2 density: (a) conditional density given
   a positive-coefficient linear statistic is MTP2 on the slice; (b) conditional
   expectations of increasing functions form a TP2 kernel in the conditioning
   variable; (c) MTP2 implies positive association.
5. **Extension to partial sums.** Karlin--Rinott extends to $s_k = \sum_{i \in B_k} x_i$
   via $\varepsilon$-perturbation ($T_\varepsilon = s_k + \varepsilon \sum_{j \notin B_k}(\bar{v}_j - x_j)$
   in $\preceq_{B_k}$-flipped coordinates) and limit $\varepsilon \downarrow 0$.
6. **Esary--Proschan--Walkup (1967).** Conditioning a positively associated vector
   on an increasing event preserves positive association.
7. **FKG inequality (1971).** Under MTP2, increasing functions have non-negative
   covariance.
8. **Disintegration Theorem.** Regular conditional distributions exist for Borel
   measures on Polish spaces.

---

## 8. Difficulty Assessment

**Classification: difficult.**

**Justification:**

1. *Multiple interacting definitions:* At least 11 formal definitions (upper set,
   direction cone, partial order, cell sums, positive displacement, boundary/interior
   tails, MTP2, radial score, saddle-point criterion, obliqueness parameter,
   crossing point) must be precisely coordinated.

2. *Research-level content:* The sufficiency direction (Part I) requires a five-layer
   proof combining lattice-theoretic arguments (cone dominance from the upper-set
   property), probability theory (MTP2/FKG/Karlin--Rinott conditional machinery,
   Strassen couplings), and optimal transport (DDT saddle-point verification).
   The cone dominance lemma is the key new ingredient distinguishing this from
   the single-core case.

3. *Two independent converse directions:* Part II requires separate perturbation
   arguments showing that failure of either the upper-set property or inclusivity
   destroys optimality for all $\alpha > 0$, with careful accounting of
   $\Theta(\varepsilon)$ gains versus $O(\varepsilon^2)$ cannibalization.

4. *No obvious single strategy:* The sufficiency and necessity directions use
   fundamentally different proof techniques (transport construction vs.
   perturbation/augmentation), and the sufficiency proof itself has multiple
   non-trivially interacting layers.
