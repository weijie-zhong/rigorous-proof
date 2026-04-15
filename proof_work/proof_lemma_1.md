## Lemma 1 — Parity lemma: squares of odd integers are odd (equivalently, if $n^2$ is even then $n$ is even)
Status: DRAFT
Iteration: 1
Gaps: none

**Statement.** For every $n \in \mathbb{Z}$, if $n$ is odd then $n^2$ is odd. Equivalently (by contrapositive): for every $n \in \mathbb{Z}$, if $2 \mid n^2$ then $2 \mid n$.

---

### Part A. Direct form: $n$ odd $\Rightarrow n^2$ odd.

1. Let $n \in \mathbb{Z}$ be arbitrary, and assume $n$ is odd. [Logic: universal introduction + assumption for conditional]

2. There exists $k \in \mathbb{Z}$ such that $n = 2k + 1$. [Definition of odd integer, applied to Step 1]

3. Squaring both sides: $n^2 = (2k + 1)^2$. [By Step 2; equals applied to $(\cdot)^2$, which is a well-defined function on $\mathbb{Z}$ by Hypothesis H1]

4. Expand the right-hand side:
$$(2k+1)^2 = (2k+1)(2k+1) = (2k)(2k) + (2k)(1) + (1)(2k) + (1)(1) = 4k^2 + 2k + 2k + 1 = 4k^2 + 4k + 1.$$
[Algebraic manipulation: distributivity, commutativity, and associativity of $+$ and $\cdot$ in $\mathbb{Z}$, Hypothesis H1]

5. Rewrite: $4k^2 + 4k + 1 = 2 \cdot (2k^2 + 2k) + 1$. [Algebraic manipulation: factor $2$ out of $4k^2 + 4k$ using distributivity, Hypothesis H1]

6. Combining Steps 3, 4, and 5: $n^2 = 2 \cdot (2k^2 + 2k) + 1$. [By Steps 3, 4, 5; transitivity of equality]

7. Set $m := 2k^2 + 2k$. Then $m \in \mathbb{Z}$, since $\mathbb{Z}$ is closed under $+$ and $\cdot$. [Hypothesis H1: $\mathbb{Z}$ is a ring, hence closed under the operations used]

8. By Steps 6 and 7, $n^2 = 2m + 1$ with $m \in \mathbb{Z}$. [By Step 6 with substitution from Step 7]

9. Therefore $n^2$ is odd. [Definition of odd integer, applied to Step 8]

10. Since $n \in \mathbb{Z}$ was arbitrary, we have shown: for all $n \in \mathbb{Z}$, if $n$ is odd then $n^2$ is odd. [Logic: universal generalization + conditional introduction, discharging Step 1]

### Part B. Contrapositive form: $2 \mid n^2 \Rightarrow 2 \mid n$.

11. Let $n \in \mathbb{Z}$ be arbitrary, and assume $2 \mid n^2$. [Logic: universal introduction + assumption for conditional]

12. By Hypothesis H3 (parity dichotomy: every integer is exactly one of even or odd), $n$ is either even or odd. [Hypothesis H3, Definition of even/odd integer]

13. **Case 1:** $n$ is even. Then by Definition of "divides" (applied to the Definition of even integer), $2 \mid n$. This is the desired conclusion. [Definition of even integer; Definition of divides]

14. **Case 2:** $n$ is odd. Then by Step 10 (the direct form proved in Part A, instantiated at this $n$), $n^2$ is odd. [By Step 10]

15. In Case 2, by Definition of odd integer applied to $n^2$, there exists $j \in \mathbb{Z}$ with $n^2 = 2j + 1$. [Definition of odd integer, applied to Step 14]

16. In Case 2, suppose for contradiction that $2 \mid n^2$. Then by Definition of divides, there exists $\ell \in \mathbb{Z}$ with $n^2 = 2 \ell$. [Definition of divides, applied to Step 11 (the standing assumption of Part B)]

17. From Steps 15 and 16: $2\ell = 2j + 1$, hence $2\ell - 2j = 1$, hence $2(\ell - j) = 1$. [Algebraic manipulation: subtract $2j$ from both sides, then factor $2$ — valid in $\mathbb{Z}$ by Hypothesis H1]

18. Let $t := \ell - j \in \mathbb{Z}$ (closure of $\mathbb{Z}$ under subtraction, Hypothesis H1). Then $2 t = 1$, i.e., $1$ is even. [By Step 17; Definition of even integer]

19. But $1$ is not even: by Definition of odd, $1 = 2 \cdot 0 + 1$, so $1$ is odd; and by Hypothesis H3 (parity dichotomy), $1$ cannot be both even and odd. [Definition of odd integer; Hypothesis H3]

20. Step 18 contradicts Step 19. Therefore the assumption in Case 2 that $2 \mid n^2$ is untenable; Case 2 is incompatible with the standing hypothesis $2 \mid n^2$ (Step 11). [Logic: reductio ad absurdum]

21. Since Case 2 leads to a contradiction with Step 11, only Case 1 remains. Hence $n$ is even, and by Step 13, $2 \mid n$. [Logic: disjunction elimination on Step 12, using Steps 13 and 20]

22. Since $n \in \mathbb{Z}$ was arbitrary, we have shown: for all $n \in \mathbb{Z}$, if $2 \mid n^2$ then $2 \mid n$. [Logic: universal generalization + conditional introduction, discharging Step 11]

23. Both forms (Parts A and B) of the Lemma are established. $\blacksquare$ [By Steps 10 and 22]
