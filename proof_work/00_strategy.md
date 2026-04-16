# Proof Strategy — General Premium-Family Bundle Dominance

## 1. Overall Approach

The theorem has three logically independent parts, each requiring a different
proof technique:

### Part I (Sufficiency): Direct Construction
**Strategy:** Direct construction of a certifying transport plan $\gamma$ that
satisfies the DDT Saddle-Point Criterion (Definition 8) for the full cost
$c_\alpha$, building on the restricted-optimal transport $\gamma^{\mathcal{F}}$.

**Why this strategy:** The DDT framework reduces optimality verification to a
constructive task: exhibit a non-negative measure $\gamma$ satisfying three
explicit conditions. This is the canonical approach for establishing optimality
in the DDT framework and matches the structure of the restricted optimality
hypothesis (H4), which already provides a transport plan for the restricted
cost. The challenge is upgrading this to the full cost, which requires showing
that the restricted cost dominates the non-premium cost on the support of
$\gamma$. This upgrade is achieved through five layers:

1. **Layer 1 (Cone Dominance):** A lattice-theoretic argument using the
   upper-set property (H3) to control non-premium bundle values within the
   direction cone $K^{\mathcal{F}}_{B_k}$. The key step is showing $h_j \le 0$
   for $j \notin B_k$, which bounds non-premium costs by $S_+(h) \le \varepsilon_k$.

2. **Layer 2 (Oblique Transport):** A probabilistic argument constructing
   cell-level couplings $\gamma_k$ with $\preceq_{B_k}$-monotone support and
   guaranteed obliqueness $\lambda_k > 0$. Uses the MTP2 structure (H9),
   Karlin--Rinott conditional theorems, EPW conditional association, and
   Strassen's coupling theorem.

3. **Layer 3 (Threshold):** An algebraic argument combining the cone dominance
   bound from Layer 1 with the obliqueness parameter from Layer 2 to derive
   the critical threshold $\alpha^* = \max_k 1/\lambda_k$.

4. **Layer 4 (Boundary Partition):** A geometric argument using inclusivity
   (H5) and face assignment (H6) to show that all boundary mass $\mu^\partial$
   is captured by selling cells.

5. **Layer 5 (Saddle-Point Verification):** Assembly of the aggregate transport
   $\gamma$ and verification of all three DDT conditions.

### Part II(a) (Upper-set necessity): Direct Perturbation
**Strategy:** Direct augmentation argument — introduce a non-premium bundle
$B_k \cup \{j\}$ at a suitably chosen price and show strict revenue
improvement via first-order gain vs. second-order cannibalization.

**Why this strategy:** When $\mathcal{F}$ is not an upper set, there exist
$B_k \in \mathcal{F}$ and $j \notin B_k$ with $B_k \cup \{j\} \notin \mathcal{F}$.
The non-premium bundle $B_k \cup \{j\}$ has additive (un-amplified) valuation.
A direct perturbation argument exploits the gap between the amplified price of
$B_k$ and the additive value of the larger bundle to capture positive-measure
sets of buyers, yielding $\Theta(\varepsilon)$ revenue gain against
$O(\varepsilon^2)$ cannibalization.

### Part II(b) (Inclusivity necessity): Direct Perturbation
**Strategy:** Direct augmentation — offer the singleton $\{j\}$ at price
$\bar{v}_j - \varepsilon$ and show strict revenue improvement.

**Why this strategy:** When inclusivity fails, there exist excluded types with
high $x_j$ that are not served. The singleton $\{j\}$ is non-premium (since
$j \notin \bigcap \mathcal{A}$), so it has additive valuation $x_j$. Offering
it cheaply captures these stranded types.

---

## 2. Known Results to Be Used

### 2.1 Primary verification tool

**Saddle-Point Criterion (Daskalakis--Deckelbaum--Tzamos, 2017).**
*Econometrica*, 85(3):735–767.

A piecewise-linear mechanism with cells $\{C_k\}$ and slopes $\{q^k\}$ is
optimal if there exists a non-negative measure $\gamma$ on $D \times D$ such
that: (1) $\gamma(C_k \times C_k^c) = 0$ for every $k$; (2) for $\gamma$-a.e.
$(y,y')$ in $C_k \times C_k$, $q^k \cdot (y-y') = c(y,y')$; (3) $\gamma_1 - \gamma_2 = \mu$.

**Role in proof:** The entire sufficiency direction constructs $\gamma$
satisfying these conditions for the full cost $c_\alpha$.

### 2.2 Coupling existence tools

**Strassen's Theorem (1965).** *Ann. Math. Statist.*, 36(2):423–439.

Let $(X, \le)$ be a partially ordered Polish space with closed order relation.
Let $\mu_1, \mu_2$ be finite Borel measures on $X$ with $\mu_1(X) = \mu_2(X)$.
A coupling $\pi$ of $\mu_1, \mu_2$ supported on $\{(x,y) : x \ge y\}$ exists
iff $\int \phi \, d\mu_1 \ge \int \phi \, d\mu_2$ for every bounded
measurable increasing function $\phi$.

**Role in proof:** Constructs the cell-level oblique coupling $\gamma_k$
in Layer 2.

**Monotone Coupling Lemma (univariate).** Standard; see Lindvall (2002).

Finite Borel measures $\alpha, \beta$ on $\mathbb{R}$ with equal total mass
and $\alpha([r,\infty)) \ge \beta([r,\infty))$ for all $r$ admit a coupling
supported on $\{(x,y) : x \ge y\}$.

**Role in proof:** Applied to the $s_k$-marginals in the shifted-tail argument
within Layer 2.

### 2.3 Dependence structure tools

**Karlin--Rinott (1980).** *J. Multivariate Anal.*, 10(4):467–498.

For an MTP2 density $f$ and $T = \sum a_i X_i$ with all $a_i > 0$:
(a) $f(\cdot \mid T = t)$ is MTP2 on the slice;
(b) $E[\phi(X) \mid T = t]$ is increasing in $t$ for increasing $\phi$;
(c) MTP2 $\Rightarrow$ positive association.

**Role in proof:** (a) gives conditional MTP2 on level sets of $s_k$ after
$\varepsilon$-perturbation; (b) provides the monotonicity needed for
stochastic dominance; (c) provides positive association for the FKG step.

**Extension to partial sums.** Via $\varepsilon$-perturbation:
$T_\varepsilon = s_k + \varepsilon \sum_{j \notin B_k}(\bar{v}_j - x_j)$
has all positive coefficients in $\preceq_{B_k}$-flipped coordinates. Take
$\varepsilon \downarrow 0$ via dominated convergence.

**Role in proof:** Extends Karlin--Rinott from full positive-coefficient sums
to the partial sum $s_k$.

**Esary--Proschan--Walkup (1967).** *Ann. Math. Statist.*, 38(5):1466–1474.

Conditioning a positively associated vector on an increasing event preserves
positive association.

**Role in proof:** Since $C_k$ is a $\preceq_{B_k}$-upper set (increasing
event), EPW preserves positive association when conditioning on $\{X \in C_k\}$.

**FKG Inequality (1971).** *Comm. Math. Phys.*, 22(2):89–103.

Under MTP2 (log-supermodular) density, increasing functions have non-negative
covariance.

**Role in proof:** Converts positive association on conditional distributions
to the covariance bounds needed in the shifted-tail argument.

### 2.4 Measure-theoretic tools

**Disintegration Theorem.** Standard; see Bogachev (2007).

A finite Borel measure on a Polish space can be disintegrated along any
measurable map into regular conditional distributions.

**Role in proof:** Disintegrates $\nu^\pm|_{C_k}$ along $s_k$ to obtain
conditional distributions on slices $\{s_k = s\} \cap C_k$.

### 2.5 Perturbation tools (for Part II)

**Envelope Theorem / Milgrom--Segal (2002).** *Econometrica*.

Small perturbations of the mechanism produce revenue changes computable to
first order.

**Role in proof:** Computing $\Theta(\varepsilon)$ revenue gain from
augmentation in Parts II(a) and II(b).

⚠️ **Note:** The precise form of the envelope theorem for piecewise-linear
mechanism perturbations needs careful application. The first-order revenue
gain computation requires that the set of switching types has positive measure,
which follows from $f > 0$ (H1', H1'').

---

## 3. Key Insights

### 3.1 Core mathematical idea (Part I)

**The upper-set property creates a one-sided sign constraint in the direction
cone that decouples the premium-vs-non-premium cost comparison.**

Specifically, for any active bundle $B_k \in \mathcal{F}$ and any direction
$h \in K^{\mathcal{F}}_{B_k}$, the upper-set property forces $h_j \le 0$
for all $j \notin B_k$. This means that every non-premium bundle
$B' \notin \mathcal{F}$ has value $\sum_{B'} h_i \le S_+(h)$, where $S_+(h)$
counts only the positive displacements within $B_k$. Meanwhile, the premium
bundle $B_k$ captures the full sum $\sum_{B_k} h_i$ (which may be much larger
because it includes both positive and negative terms, with the net being
non-negative). The obliqueness parameter $\lambda_k$ quantifies the gap
between the premium sum and the deficit $\varepsilon_k$, and the threshold
$\alpha \ge 1/\lambda_k$ ensures that the $\alpha$-amplified premium cost
dominates the non-premium cost.

**This is the key generalization from the single-core case:** in the
principal-filter case, the cone characterization is tighter (individual
sign constraints on $B_k \setminus C$ coordinates), but the cone dominance
bound $S_+(h) \le \varepsilon_k$ is the same. The general upper-set
case achieves the same bound through a weaker cone characterization that
nonetheless suffices for the cost comparison.

### 3.2 Why MTP2 and oblique transport are needed

The saddle-point criterion requires the transport $\gamma$ to be supported on
pairs where $q^{B_k} \cdot h = c_\alpha(h)$. This means $h = x^1 - x^2$ must
lie in the direction cone $K^{\mathcal{F}}_{B_k}$, which (by Lemma 1) requires
$h_j \le 0$ for $j \notin B_k$ — i.e., the transport must move mass "inward"
in non-$B_k$ coordinates. The MTP2 property (via positive association and FKG)
ensures that the boundary mass $\nu^+|_{C_k}$ is stochastically larger than
the interior mass $\nu^-|_{C_k}$ in the $\preceq_{B_k}$ order, which is
exactly the condition for Strassen's theorem to provide a cone-supported
coupling. The obliqueness parameter then quantifies the "slack" in this
coupling: how much of the deficit $\varepsilon_k$ is captured by the premium
sum $\sum_{B_k} h_i$.

### 3.3 Why both converses are needed

Part II(a) shows the upper-set structure is necessary by exhibiting a
profitable augmentation when it fails. Part II(b) shows inclusivity is
necessary by exhibiting stranded high-value types. These are independent
failure modes: a family can be an upper set but fail inclusivity (Part II(b)),
or satisfy inclusivity but fail to be an upper set (Part II(a)). Both
converses use perturbation arguments with $\Theta(\varepsilon)$-vs-$O(\varepsilon^2)$
accounting, but the perturbation targets are different (superset bundle vs.
singleton).

### 3.4 Role of each hypothesis

- **H1–H2:** Regularity and virtual positivity ensure the DDT framework
  applies and $\mu^-$ is purely interior.
- **H3:** Upper-set structure → cone dominance → non-premium cost bound.
- **H4:** Restricted optimality → existence of $\gamma^{\mathcal{F}}$,
  cell mass balance, cell structure.
- **H5–H6:** Geometric inclusivity + face assignment → boundary partition
  (all boundary mass in selling cells).
- **H7–H8:** Tail dominance + cell inclusivity → shifted-tail stochastic
  dominance for $s_k$-marginals.
- **H9:** MTP2 → positive association → Strassen condition via FKG.
- **H10:** Decreasing $\Phi$ → virtual density stochastic ordering →
  interior mass dominated by boundary mass.
