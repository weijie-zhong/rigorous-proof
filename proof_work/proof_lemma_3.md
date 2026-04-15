## Lemma 3 — Parity cascade: $p^2 = 2q^2$ forces $2 \mid p$ and $2 \mid q$
Status: DRAFT
Iteration: 1
Gaps: none

**Statement.** Let $p, q \in \mathbb{Z}$ with $q \neq 0$. If $p^2 = 2 q^2$, then $2 \mid p$ and $2 \mid q$.

---

### Part A. Setup.

1. Fix arbitrary $p, q \in \mathbb{Z}$ with $q \neq 0$, and assume $p^2 = 2 q^2$. [Logic: universal introduction + assumption for conditional]

### Part B. Showing $2 \mid p$.

2. From Step 1, $p^2 = 2 q^2$. Set $k := q^2$. Then $k \in \mathbb{Z}$, since $\mathbb{Z}$ is closed under multiplication. [Hypothesis H1: $\mathbb{Z}$ is a ring, closed under $\cdot$]

3. By Step 2, $p^2 = 2 \cdot k$ with $k \in \mathbb{Z}$. By Definition of divides, this says $2 \mid p^2$. [Definition of divides; By Steps 1, 2]

4. Apply Lemma 1 (contrapositive form, Part B) to the integer $p$: since $2 \mid p^2$ (Step 3), we conclude $2 \mid p$. [By Lemma 1; preconditions: $p \in \mathbb{Z}$ (Step 1) and $2 \mid p^2$ (Step 3), both of which are the hypotheses required by Lemma 1]

5. By Definition of divides applied to Step 4, there exists $m \in \mathbb{Z}$ with $p = 2 m$. [Definition of divides; Logic: existential instantiation]

### Part C. Showing $2 \mid q$.

6. Square both sides of the equation $p = 2m$ from Step 5:
$$p^2 = (2m)^2.$$
[By Step 5; equality applied to the well-defined function $x \mapsto x^2$ on $\mathbb{Z}$, Hypothesis H1]

7. Expand the right-hand side:
$$(2m)^2 = (2m)(2m) = 2 \cdot 2 \cdot m \cdot m = 4 \cdot m^2 = 2 \cdot (2 m^2).$$
[Algebraic manipulation: associativity and commutativity of $\cdot$ in $\mathbb{Z}$, Hypothesis H1]

8. Combining Steps 6 and 7:
$$p^2 = 2 \cdot (2 m^2).$$
[By Steps 6, 7; transitivity of equality]

9. From the hypothesis $p^2 = 2 q^2$ (Step 1) and Step 8, we have
$$2 \cdot (2 m^2) = 2 \cdot q^2.$$
[By Step 1 and Step 8; transitivity of equality]

10. The integer $2$ is nonzero in $\mathbb{Z}$. The ring $\mathbb{Z}$ is an integral domain, so it satisfies the cancellation law: for $a, b, c \in \mathbb{Z}$ with $c \neq 0$, $c \cdot a = c \cdot b$ implies $a = b$. Applying cancellation with $c = 2$ to Step 9 yields
$$2 m^2 = q^2.$$
[Hypothesis H1: $\mathbb{Z}$ is an integral domain; Logic: modus ponens]

11. Rewrite Step 10 as $q^2 = 2 m^2$, and set $k' := m^2$. Then $k' \in \mathbb{Z}$ (since $\mathbb{Z}$ is closed under multiplication, Hypothesis H1), and $q^2 = 2 \cdot k'$. [By Step 10; symmetry of equality; Hypothesis H1]

12. By Definition of divides applied to Step 11, $2 \mid q^2$. [Definition of divides; By Step 11]

13. Apply Lemma 1 (contrapositive form, Part B) to the integer $q$: since $q \in \mathbb{Z}$ (Step 1) and $2 \mid q^2$ (Step 12), we conclude $2 \mid q$. [By Lemma 1; preconditions: $q \in \mathbb{Z}$ from Step 1 and $2 \mid q^2$ from Step 12 are the hypotheses of Lemma 1]

### Part D. Conclusion.

14. Steps 4 and 13 together establish $2 \mid p$ and $2 \mid q$. [By Steps 4, 13; Logic: conjunction introduction]

15. Since $p, q \in \mathbb{Z}$ with $q \neq 0$ were arbitrary (Step 1), we have shown: for every such pair, $p^2 = 2 q^2$ implies $2 \mid p$ and $2 \mid q$. $\blacksquare$ [Logic: universal generalization + conditional introduction, discharging the assumption of Step 1]
