# Problem Statement: General Premium-Family Bundle Dominance (with Converse)

## Context

This is a generalization of the Core-Bundle Dominance theorem. Previously, the
"premium family" was $\mathcal F = \{B : C \subseteq B\}$ for a fixed core $C$.
We now allow $\mathcal F$ to be **any upper set** (filter) in the Boolean lattice
$(2^{[N]}, \subseteq)$, and prove this is both sufficient AND necessary.

The theorem has two directions:

1. **(Sufficiency)** If $\mathcal F$ is an upper set AND inclusivity holds, then
   under regularity conditions, the restricted-optimal mechanism $M$ is optimal
   for the full problem when $\alpha$ is large enough.

2. **(Necessity / Converse)** If **either** condition fails:
   - (a) $\mathcal F$ is **not** an upper set, OR
   - (b) Strict non-inclusivity holds (some face meets the exclusion cell),

   then the restricted-optimal mechanism is **never** optimal for the full
   problem, for any $\alpha > 0$.

## Setup

**Items:** $[N] = \{1, \ldots, N\}$ with $N \ge 2$.
**Type space:** $D = \prod_{i=1}^N [0, \bar v_i]$, density $f \in C^2(D)$ with $f > 0$ on $D$.
**Premium family:** $\mathcal F \subseteq 2^{[N]} \setminus \{\emptyset\}$, a nonempty family of bundles.
**Valuations:** For each nonempty bundle $B \subseteq [N]$,
$$
  v_B(x) = \begin{cases}
    \alpha \sum_{i \in B} x_i & \text{if } B \in \mathcal F, \\
    \sum_{i \in B} x_i & \text{if } B \notin \mathcal F,
  \end{cases}
  \qquad \alpha > 0.
$$

**Restricted problem:** Only bundles in $\mathcal F$ are available. Cost:
$c^\mathcal{F}_\alpha(h) = \max(0, \max_{B \in \mathcal F} \alpha \sum_B h_i)$.

**Full problem:** All bundles available. Cost:
$c_\alpha(h) = \max(c^\mathcal{F}_\alpha(h),\; c^P(h))$ where
$c^P(h) = \max(0, \max_{B \notin \mathcal F} \sum_B h_i)$ is the non-premium cost.

**Restricted-optimal mechanism $M$:** Optimal for the restricted problem, with
selling cells $C_1, \ldots, C_K$ (active bundles $B_1, \ldots, B_K \in \mathcal F$)
and exclusion cell $C_0$.

**Direction cone:** $K^\mathcal{F}_{B_k} = \{h : \sum_{B_k} h \ge \sum_{B'} h \;\forall B' \in \mathcal F,\; \sum_{B_k} h \ge 0\}$.

**Partial order:** For each $B_k$, define $\preceq_{B_k}$ on $D$ by
$x \preceq_{B_k} x'$ iff $x_i \le x'_i$ for $i \in B_k$ and $x_j \ge x'_j$ for $j \notin B_k$.

## Part I: Sufficiency

**Theorem (Premium-Family Bundle Dominance).** Let $\mathcal F$ be an **upper set**
in $(2^{[N]}, \subseteq)$. Let $M$ be optimal for the $\mathcal F$-restricted
problem. Suppose:

- **(R1)** $\nabla f(x) \cdot x + (N+1)f(x) > 0$ on $\operatorname{int}(D)$.
- **(GI)** $F_j \cap C_0 = \emptyset$ for every item $j$ (geometric inclusivity).
- **(FA)** $F_j \cap C_k \ne \emptyset \Rightarrow j \in B_k$ (face assignment).
- **(CR)** $B_k(q) > I_k(q)$ for $q \in (p_k, \bar s_k)$ (cell-level tail dominance).
- **(CI)** $p_k < s_*^k$ (cell-level inclusivity).
- **(MTP2)** $f$ is $\preceq_{B_k}$-MTP2 for every selling cell $k$.
- **($\Phi$dec)** $\Phi(x) := \nabla f \cdot x / f + (N+1)$ is $\preceq_{B_k}$-decreasing for every $k$.

Then $M$ is optimal for the full problem whenever $\alpha \ge \alpha^\star := \max_k 1/\lambda_k$.

**Key new ingredient (Layer 1 / Cone Dominance Lemma):** Because $\mathcal F$ is
an upper set, for every $B_k \in \mathcal F$ and $j \notin B_k$, we have
$B_k \cup \{j\} \in \mathcal F$. The cone constraint then forces $h_j \le 0$ for
all $j \notin B_k$ and $h \in K^\mathcal{F}_{B_k}$. This gives the $S_+$ bound:
$\max_{B' \notin \mathcal F} \sum_{B'} h \le S_+(h) \le \varepsilon_k$ for all
$h \in K^\mathcal{F}_{B_k}$.

## Part II: Converse (Necessity)

### Part II(a): Upper-set structure is necessary

**Proposition (Non-upper-set ⟹ suboptimality).** If $\mathcal F$ is **not** an
upper set, then there exist $B_k \in \mathcal F$ and $j \notin B_k$ with
$B_k \cup \{j\} \notin \mathcal F$. For any restricted-optimal mechanism $M$
and any $\alpha > 0$, augmenting $M$ with the non-premium bundle
$B_k \cup \{j\}$ at a suitably chosen price strictly increases revenue.

**Proof sketch:** Since $B_k \cup \{j\} \notin \mathcal F$, buyers with high $x_j$
who are in cell $k$ (buying $B_k$ at $\alpha$-multiplied value) could switch to
the additive bundle $B_k \cup \{j\}$ at a slightly discounted price. The
augmentation captures buyers near the boundary of cell $k$ who value item $j$
highly but are currently paying the $\alpha$-premium for a bundle that doesn't
exploit their $j$-value optimally. The gain is $\Theta(\varepsilon)$ while
cannibalization is $O(\varepsilon^2)$.

### Part II(b): Inclusivity is necessary

**Proposition (Non-inclusivity ⟹ suboptimality).** If $\mathcal F$ is an upper
set with $\mathcal F \ne 2^{[N]}$ (so non-premium bundles exist), and
$p > \min_{j \notin \bigcap \mathcal A} \bar v_j$ where $\mathcal A$ is the
antichain of minimal elements of $\mathcal F$ and $p$ is the crossing point,
then the mechanism $M$ is not optimal for the full problem.

**Proof sketch:** Pick $j$ with $\bar v_j < p$ and $j$ not in every generator.
The singleton $\{j\}$ is non-premium (since $\{j\} \not\supseteq A$ for any
$A \in \mathcal A$). Augmenting with $\{j\}$ at price $\bar v_j - \varepsilon$
captures excluded types with high $x_j$ and low total value, giving
$\Theta(\varepsilon)$ gain vs $O(\varepsilon^2)$ cannibalization.

## Key definitions needed

All definitions from the previous proof (cell sums $s_k$, boundary/interior
tails $B_k(q), I_k(q)$, positive displacement $S_+$, radial score $\Phi$,
DDT signed measure $\mu$, saddle-point criterion) carry over with
"$C$-containing" replaced by "in $\mathcal F$".

## Reference files

The previous proof in `proof_work_v2/` contains the full machinery for the
single-core case $\mathcal F = \{B : C \subseteq B\}$. The present theorem
generalizes this: the proof of Part I is structurally identical (the upper-set
property gives Lemma 1, which is the only place the specific form of
$\mathcal F$ was used). Part II is new.

Key files to consult:
- `proof_work_v2/00_distilled.md` — full setup and known results
- `proof_work_v2/proof_lemma_1.md` through `proof_lemma_7.md` — lemma proofs
- `core_bundle_dominance.md` — the writeup (Sections 3, 5, 6, 6b, 8, 9)
