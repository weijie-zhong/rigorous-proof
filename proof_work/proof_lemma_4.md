## Lemma 4 — Main theorem: $\sqrt{2}$ is irrational ($\neg\exists\, p,q\in\mathbb{Z},\ q\neq0:\ p^2 = 2q^2$)
Status: DRAFT
Iteration: 1
Gaps: none

**Statement.** There do not exist $p \in \mathbb{Z}$ and $q \in \mathbb{Z}\setminus\{0\}$ such that $p^2 = 2 q^2$.

---

### Part A. Setup of the proof by contradiction.

1. Suppose, for contradiction, that there **do** exist $p \in \mathbb{Z}$ and $q \in \mathbb{Z}\setminus\{0\}$ with $p^2 = 2 q^2$. The negation of the statement of Lemma 4 is precisely:
$$\exists\, p \in \mathbb{Z}\ \exists\, q \in \mathbb{Z}\setminus\{0\}\ :\ p^2 = 2 q^2.$$
[Logic: assumption for reductio ad absurdum; negation of a universally-quantified $\neg\exists$ statement]

2. Fix such integers $p \in \mathbb{Z}$ and $q \in \mathbb{Z}\setminus\{0\}$ satisfying $p^2 = 2 q^2$. [Logic: existential instantiation applied to Step 1]

### Part B. Extract a lowest-terms representative via Lemma 2.

3. Apply Lemma 2 to the pair $(p, q)$. The preconditions of Lemma 2 — namely $p \in \mathbb{Z}$ and $q \in \mathbb{Z}\setminus\{0\}$ — are met by Step 2. Lemma 2 yields integers $p', q' \in \mathbb{Z}$ such that:
(i) $q' \neq 0$,
(ii) $p \cdot q' = p' \cdot q$, and
(iii) $\gcd(p', q') = 1$.
[By Lemma 2; Logic: existential instantiation]

### Part C. Transport the equation $p^2 = 2 q^2$ to the representative $(p', q')$.

4. From clause (ii) of Step 3, $p \cdot q' = p' \cdot q$. Square both sides of this equation:
$$(p \cdot q')^2 = (p' \cdot q)^2.$$
[By Step 3(ii); equality applied to the well-defined squaring map on $\mathbb{Z}$, Hypothesis H1]

5. Expand the squares on each side using associativity and commutativity of multiplication in $\mathbb{Z}$:
$$(p \cdot q')^2 = p^2 \cdot (q')^2 \qquad\text{and}\qquad (p' \cdot q)^2 = (p')^2 \cdot q^2.$$
[Algebraic manipulation: associativity and commutativity of $\cdot$ in $\mathbb{Z}$, Hypothesis H1]

6. Combining Steps 4 and 5:
$$p^2 \cdot (q')^2 = (p')^2 \cdot q^2.$$
[By Steps 4, 5; transitivity of equality]

7. Substitute the hypothesis $p^2 = 2 q^2$ (Step 2) into the left-hand side of Step 6:
$$(2 q^2) \cdot (q')^2 = (p')^2 \cdot q^2.$$
[By Steps 2, 6; substitution of equals]

8. Rearrange the left-hand side using associativity and commutativity of $\cdot$ in $\mathbb{Z}$:
$$2 \cdot (q')^2 \cdot q^2 = (p')^2 \cdot q^2,$$
equivalently $q^2 \cdot \bigl(2 \cdot (q')^2\bigr) = q^2 \cdot (p')^2$.
[Algebraic manipulation: associativity and commutativity of $\cdot$ in $\mathbb{Z}$, Hypothesis H1]

9. Since $q \neq 0$ (Step 2) and $\mathbb{Z}$ is an integral domain, the product $q^2 = q \cdot q$ is also nonzero (an integral domain has no nonzero zero divisors: a product of two nonzero elements is nonzero). [Hypothesis H1: $\mathbb{Z}$ is an integral domain; Logic: modus ponens]

10. Apply the cancellation law in the integral domain $\mathbb{Z}$ with the nonzero factor $c := q^2$ to the equation in Step 8: from $q^2 \cdot \bigl(2 (q')^2\bigr) = q^2 \cdot (p')^2$ and $q^2 \neq 0$, we deduce
$$2 \cdot (q')^2 = (p')^2,$$
equivalently $(p')^2 = 2 (q')^2$. [Hypothesis H1: $\mathbb{Z}$ is an integral domain, cancellation law; By Steps 8, 9; symmetry of equality]

### Part D. Apply Lemma 3 to the pair $(p', q')$.

11. From Step 3, $p' \in \mathbb{Z}$ and $q' \in \mathbb{Z}$ with $q' \neq 0$ (clause (i)). From Step 10, $(p')^2 = 2 (q')^2$. These are exactly the hypotheses of Lemma 3 instantiated at $(p', q')$. [By Steps 3, 10; checking preconditions of Lemma 3]

12. Apply Lemma 3 to $(p', q')$: we conclude $2 \mid p'$ and $2 \mid q'$. [By Lemma 3; preconditions verified in Step 11]

### Part E. Derive the contradiction with coprimality.

13. From Step 12, $2 \mid p'$ and $2 \mid q'$. By Definition of divides, $2$ is a common (positive integer) divisor of $p'$ and $q'$. [Definition of divides; By Step 12]

14. By the Definition of greatest common divisor, $\gcd(p', q')$ is divisible by every common integer divisor of $p'$ and $q'$; in particular, since $2$ is such a common divisor (Step 13), we have $2 \mid \gcd(p', q')$. [Definition of greatest common divisor: clause (ii) in the definition — every common divisor $c$ of $p', q'$ satisfies $c \mid \gcd(p', q')$; By Step 13]

15. From Step 3(iii), $\gcd(p', q') = 1$. Substituting into Step 14:
$$2 \mid 1.$$
[By Steps 3(iii), 14; substitution of equals]

16. By Definition of divides, $2 \mid 1$ means there exists $t \in \mathbb{Z}$ with $1 = 2 \cdot t$. [Definition of divides; By Step 15; Logic: existential instantiation]

17. However, no such $t \in \mathbb{Z}$ exists. We prove this directly: by Hypothesis H3 (parity dichotomy), every integer is exactly one of even or odd; in particular, $1$ is odd, since $1 = 2 \cdot 0 + 1$ and $0 \in \mathbb{Z}$, so $1$ fits the Definition of odd integer. If $1 = 2 t$ for some $t \in \mathbb{Z}$, then by Definition of even integer $1$ would be even. But $1$ cannot be both even and odd (Hypothesis H3, parity dichotomy). [Hypothesis H3: parity dichotomy; Definition of even integer; Definition of odd integer]

18. Therefore Step 16 (which asserts the existence of such a $t$) is false. This contradicts Step 15. [Logic: contradiction between Steps 16 and 17; equivalently, the chain "$2 \mid 1 \Rightarrow 1$ is even $\Rightarrow 1$ is not odd" collides with the Definition-of-odd fact "$1$ is odd"]

### Part F. Conclusion.

19. Steps 1 through 18 derive a contradiction from the assumption in Step 1. By reductio ad absurdum, the assumption is false: there do **not** exist $p \in \mathbb{Z}$ and $q \in \mathbb{Z}\setminus\{0\}$ with $p^2 = 2 q^2$. [Logic: reductio ad absurdum, discharging the assumption of Step 1]

20. This is the statement of Lemma 4. $\blacksquare$ [By Step 19]
