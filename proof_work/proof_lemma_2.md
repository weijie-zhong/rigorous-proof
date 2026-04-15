## Lemma 2 — Lowest-terms representative (via well-ordering)
Status: DRAFT
Iteration: 1
Gaps: none

**Statement.** For every pair $(p, q) \in \mathbb{Z} \times (\mathbb{Z}\setminus\{0\})$, there exist integers $p', q'$ such that:
(i) $q' \neq 0$,
(ii) $p \cdot q' = p' \cdot q$ (so $(p,q) \sim (p', q')$ as rational representatives), and
(iii) $\gcd(p', q') = 1$.

---

### Part A. Setup and construction of the candidate representative.

1. Fix arbitrary $p \in \mathbb{Z}$ and $q \in \mathbb{Z}\setminus\{0\}$. [Logic: universal introduction]

2. Define the set
$$S \;:=\; \{\,d \in \mathbb{Z}_{>0} \;:\; \exists\, a \in \mathbb{Z},\ p \cdot d = a \cdot q\,\}.$$
[Definition: set-builder notation, using Hypothesis H1 for the ambient integers]

3. Observe $S \subseteq \mathbb{N}$, because $\mathbb{Z}_{>0} = \{1, 2, 3, \dots\} \subseteq \mathbb{N}$. [Hypothesis H4: $\mathbb{N} = \{0,1,2,\dots\}$]

4. **Claim:** $S$ is nonempty. We show $|q| \in S$.

5. Since $q \in \mathbb{Z}\setminus\{0\}$, we have $q \neq 0$, so $|q| > 0$; hence $|q| \in \mathbb{Z}_{>0}$. [Hypothesis H1: order on $\mathbb{Z}$; Definition of absolute value]

6. **Case I:** $q > 0$. Then $|q| = q$. Set $a := p$. Then $p \cdot |q| = p \cdot q = a \cdot q$. [Definition of absolute value; Algebraic manipulation: substitution]

7. **Case II:** $q < 0$. Then $|q| = -q$. Set $a := -p$. Then $p \cdot |q| = p \cdot (-q) = -(p \cdot q) = (-p) \cdot q = a \cdot q$. [Definition of absolute value; Algebraic manipulation: rules of signs in the ring $\mathbb{Z}$, Hypothesis H1]

8. By Hypothesis H1 (trichotomy on $\mathbb{Z}$) and $q \neq 0$, either $q > 0$ or $q < 0$. Combining Steps 6 and 7, in both cases there exists $a \in \mathbb{Z}$ with $p \cdot |q| = a \cdot q$. [Hypothesis H1: trichotomy; Logic: disjunction elimination]

9. Therefore $|q| \in S$ by Steps 5 and 8. [Definition of $S$ from Step 2]

10. Hence $S \neq \emptyset$. [By Step 9]

11. By Hypothesis H4 (well-ordering of $\mathbb{N}$), since $S$ is a nonempty subset of $\mathbb{N}$ (Steps 3 and 10), $S$ has a least element. Call it $q'$. Thus $q' \in S$ and $q' \leq d$ for every $d \in S$. [Hypothesis H4]

12. Since $q' \in S$, by Step 2 there exists $p' \in \mathbb{Z}$ with $p \cdot q' = p' \cdot q$. Fix one such $p'$. [Definition of $S$, Step 2; Logic: existential instantiation]

13. Also $q' \in \mathbb{Z}_{>0}$ by Step 11, so $q' > 0$, in particular $q' \neq 0$. This verifies clause (i). [By Step 11; Hypothesis H1: order on $\mathbb{Z}$]

14. Step 12 yields $p \cdot q' = p' \cdot q$, which is clause (ii). [By Step 12]

### Part B. Coprimality of $(p', q')$: clause (iii).

15. Since $q' > 0$ (Step 13), $p'$ and $q'$ are not both zero. Hence $d := \gcd(p', q')$ is defined, and $d$ is a positive integer. [Definition of greatest common divisor (from the Definitions section of the distilled problem)]

16. In particular, $d \geq 1$. [By Step 15; Definition: positive integer]

17. Suppose for contradiction that $d \neq 1$. Then $d \geq 2$. [Logic: assumption for reductio; By Step 16 and Hypothesis H1: the positive integer immediately above $1$ is $2$, so $d \geq 1$ and $d \neq 1$ force $d \geq 2$]

18. By Definition of gcd, $d \mid p'$ and $d \mid q'$. So by Definition of divides, there exist $p'', q'' \in \mathbb{Z}$ with
$$p' = d \cdot p'' \qquad\text{and}\qquad q' = d \cdot q''.$$
[Definition of greatest common divisor; Definition of divides; Logic: existential instantiation]

19. Since $q' > 0$ (Step 13) and $d > 0$ (Step 17, as $d \geq 2 > 0$), and $q' = d \cdot q''$ (Step 18), we conclude $q'' > 0$. [Algebraic manipulation: in $\mathbb{Z}$, a product of two integers is positive iff both factors have the same sign; since $d > 0$ and $d q'' = q' > 0$, $q''$ must be positive. Hypothesis H1.]

20. From $d \geq 2$ (Step 17) and $q'' \geq 1$ (Step 19, since $q''$ is a positive integer), we compute
$$q' = d \cdot q'' \geq 2 \cdot q'' = q'' + q'' \geq q'' + 1 > q''.$$
Hence $q'' < q'$. [Algebraic manipulation: multiplication and addition monotonicity on $\mathbb{Z}$, Hypothesis H1]

21. Substitute the expressions from Step 18 into the relation $p \cdot q' = p' \cdot q$ of Step 12:
$$p \cdot (d \cdot q'') = (d \cdot p'') \cdot q.$$
[By Steps 12 and 18; equals substituted into equals]

22. Using associativity and commutativity of multiplication in $\mathbb{Z}$ (Hypothesis H1), both sides of the equation in Step 21 rearrange:
$$d \cdot (p \cdot q'') = d \cdot (p'' \cdot q).$$
[Algebraic manipulation: associativity/commutativity, Hypothesis H1]

23. Since $d \geq 2 > 0$, in particular $d \neq 0$. The ring $\mathbb{Z}$ is an integral domain, i.e., it has the cancellation law: for $a, b, c \in \mathbb{Z}$ with $c \neq 0$, $c \cdot a = c \cdot b$ implies $a = b$. Applying cancellation with $c = d$ to Step 22 yields
$$p \cdot q'' = p'' \cdot q.$$
[Hypothesis H1: $\mathbb{Z}$ is an integral domain (standard ring-theoretic property of integers); Logic: modus ponens]

24. From Step 19, $q'' \in \mathbb{Z}_{>0}$. From Step 23, there exists an integer (namely $p''$) with $p \cdot q'' = p'' \cdot q$. Therefore, by the Definition of $S$ (Step 2), $q'' \in S$. [By Steps 19, 23; Definition of $S$, Step 2]

25. By Step 11, $q'$ is the least element of $S$, so $q' \leq q''$. [By Step 11 applied to $q'' \in S$ from Step 24]

26. But Step 20 asserts $q'' < q'$, which contradicts Step 25. [Logic: contradiction between $q'' < q'$ and $q' \leq q''$ is immediate from trichotomy, Hypothesis H1]

27. The contradiction refutes the assumption in Step 17. Therefore $d = 1$, i.e., $\gcd(p', q') = 1$. This is clause (iii). [Logic: reductio ad absurdum, discharging the assumption of Step 17]

### Part C. Conclusion.

28. By Steps 13, 14, and 27, the integers $p' \in \mathbb{Z}$ and $q' \in \mathbb{Z}$ satisfy all three clauses (i) $q' \neq 0$, (ii) $p q' = p' q$, and (iii) $\gcd(p', q') = 1$. [By Steps 13, 14, 27]

29. Since $(p, q)$ was an arbitrary element of $\mathbb{Z} \times (\mathbb{Z}\setminus\{0\})$ (Step 1), we have established the statement of Lemma 2. $\blacksquare$ [Logic: universal generalization, discharging Step 1]
