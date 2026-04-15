# The Irrationality of $\sqrt{2}$

**Theorem (Main).** *There do not exist integers $p, q \in \mathbb{Z}$ with $q \neq 0$ such that $p^2 = 2 q^2$. Equivalently, $\sqrt{2} \notin \mathbb{Q}$.*

**Proof Health:** Clean pass. All four lemmas audited individually and cold-read as a chain; no unresolved critical gaps.

---

## Hypotheses in force

- **H1.** $\mathbb{Z}$ is the ring of integers with operations $+, \cdot$ and order $<$; $\mathbb{Z}$ is an integral domain (no nonzero zero divisors, cancellation law holds).
- **H2.** $\mathbb{Q}$ is the field of fractions of $\mathbb{Z}$; a rational is a class of pairs $(p,q)$ with $q \neq 0$ under $(p,q)\sim(p',q') \iff pq' = p'q$.
- **H3.** Parity dichotomy: every integer is **exactly one** of even ($n = 2k$) or odd ($n = 2k+1$), $k \in \mathbb{Z}$.
- **H4.** Well-ordering of $\mathbb{N} = \{0,1,2,\ldots\}$: every nonempty subset of $\mathbb{N}$ has a least element.

---

## Lemma 1 (Parity lemma)

*For every $n \in \mathbb{Z}$: if $n$ is odd, then $n^2$ is odd. Equivalently (contrapositive): for every $n \in \mathbb{Z}$, if $2 \mid n^2$ then $2 \mid n$.*

**Proof.**

### Part A. Direct form: $n$ odd $\Rightarrow n^2$ odd.

1. Let $n \in \mathbb{Z}$ be arbitrary, and assume $n$ is odd. [Logic: universal introduction + assumption for conditional]
2. There exists $k \in \mathbb{Z}$ with $n = 2k+1$. [Definition of odd integer]
3. Hence $n^2 = (2k+1)^2$. [By Step 2; squaring is well-defined on $\mathbb{Z}$, H1]
4. Expanding:
$$(2k+1)^2 = (2k)(2k) + (2k)(1) + (1)(2k) + 1 = 4k^2 + 4k + 1.$$
[Algebraic manipulation: distributivity, commutativity, associativity in $\mathbb{Z}$, H1]
5. Rewrite: $4k^2 + 4k + 1 = 2\,(2k^2 + 2k) + 1$. [Algebraic manipulation: factoring, H1]
6. Combining Steps 3–5, $n^2 = 2\,(2k^2 + 2k) + 1$. [Transitivity of equality]
7. Set $m := 2k^2 + 2k \in \mathbb{Z}$ (closure of $\mathbb{Z}$ under $+, \cdot$, H1). Then $n^2 = 2m + 1$. [H1; By Step 6]
8. Therefore $n^2$ is odd. [Definition of odd integer]
9. Since $n$ was arbitrary, $\forall n \in \mathbb{Z}$: $n$ odd $\Rightarrow n^2$ odd. [Logic: universal generalization + conditional introduction]

### Part B. Contrapositive form: $2 \mid n^2 \Rightarrow 2 \mid n$.

10. Let $n \in \mathbb{Z}$ be arbitrary, and assume $2 \mid n^2$. [Logic: universal introduction + assumption]
11. By the parity dichotomy (H3), $n$ is either even or odd. [H3]
12. **Case 1:** $n$ is even. Then $n = 2k$ for some $k \in \mathbb{Z}$, so by Definition of divides $2 \mid n$, as required. [Definition of even; Definition of divides]
13. **Case 2:** $n$ is odd. By Part A (Step 9), $n^2$ is odd, so by Definition of odd there is $j \in \mathbb{Z}$ with $n^2 = 2j + 1$. [By Step 9; Definition of odd]
14. The standing hypothesis $2 \mid n^2$ (Step 10) gives some $\ell \in \mathbb{Z}$ with $n^2 = 2\ell$. [Definition of divides]
15. Combining Steps 13–14: $2\ell = 2j + 1$, hence $2(\ell - j) = 1$. Setting $t := \ell - j \in \mathbb{Z}$ (H1 closure under subtraction), we obtain $2t = 1$, i.e., $1$ is even. [Algebraic manipulation, H1; Definition of even]
16. But $1 = 2\cdot 0 + 1$ with $0 \in \mathbb{Z}$, so $1$ is odd (Definition of odd), and by the parity dichotomy (H3), $1$ cannot be both even and odd — contradiction. [Definition of odd; H3]
17. Case 2 is therefore impossible; only Case 1 remains, whence $2 \mid n$. [Logic: reductio; disjunction elimination on Step 11]
18. Since $n$ was arbitrary, $\forall n \in \mathbb{Z}$: $2 \mid n^2 \Rightarrow 2 \mid n$. [Logic: universal generalization + conditional introduction] $\blacksquare$

---

## Lemma 2 (Lowest-terms representative)

*For every $(p,q) \in \mathbb{Z} \times (\mathbb{Z}\setminus\{0\})$ there exist $p', q' \in \mathbb{Z}$ with (i) $q' \neq 0$, (ii) $p\,q' = p'\,q$, and (iii) $\gcd(p', q') = 1$.*

**Proof.**

### Part A. Construction via well-ordering.

1. Fix arbitrary $p \in \mathbb{Z}$ and $q \in \mathbb{Z}\setminus\{0\}$. [Logic: universal introduction]
2. Define
$$S := \{\,d \in \mathbb{Z}_{>0} : \exists a \in \mathbb{Z},\ p\,d = a\,q\,\}.$$
[Definition: set-builder notation]
3. $S \subseteq \mathbb{N}$, since $\mathbb{Z}_{>0} \subseteq \mathbb{N}$. [H4: $\mathbb{N} = \{0,1,2,\ldots\}$]
4. **Claim:** $|q| \in S$. Since $q \neq 0$, $|q| > 0$, so $|q| \in \mathbb{Z}_{>0}$. [H1: order on $\mathbb{Z}$; Definition of absolute value]
5. **Case I:** $q > 0$. Then $|q| = q$; set $a := p$, and $p\,|q| = p\,q = a\,q$. [Definition of absolute value; Algebraic manipulation]
6. **Case II:** $q < 0$. Then $|q| = -q$; set $a := -p$, and $p\,|q| = p(-q) = -(pq) = (-p)q = a\,q$. [Sign rules in $\mathbb{Z}$, H1]
7. Trichotomy (H1) and $q \neq 0$ force one of Cases I–II; in either, an integer $a$ satisfying $p\,|q| = a\,q$ exists, so $|q| \in S$. Hence $S \neq \emptyset$. [H1; Logic: disjunction elimination; Definition of $S$]
8. By well-ordering (H4), $S$ has a least element; call it $q'$. Then $q' \in S$ and $q' \leq d$ for all $d \in S$. [H4]
9. By definition of $S$, there exists $p' \in \mathbb{Z}$ with $p\,q' = p'\,q$; fix one. [Definition of $S$; Logic: existential instantiation]
10. $q' \in \mathbb{Z}_{>0}$ so $q' \neq 0$, giving clause **(i)**. The equation of Step 9 is clause **(ii)**. [By Steps 8, 9; H1]

### Part B. Coprimality — clause (iii).

11. Since $q' > 0$, $p'$ and $q'$ are not both zero, so $d := \gcd(p', q')$ is defined and is a positive integer; in particular $d \geq 1$. [Definition of gcd]
12. Suppose for contradiction $d \neq 1$, so $d \geq 2$. [Logic: reductio; H1]
13. By the gcd definition, $d \mid p'$ and $d \mid q'$, so there exist $p'', q'' \in \mathbb{Z}$ with $p' = d\,p''$ and $q' = d\,q''$. [Definition of gcd; Definition of divides]
14. From $d > 0$, $q' > 0$, and $d\,q'' = q' > 0$, the sign rules in $\mathbb{Z}$ force $q'' > 0$, so $q'' \geq 1$. [H1]
15. Since $d \geq 2$ and $q'' \geq 1$,
$$q' = d\,q'' \geq 2\,q'' = q'' + q'' \geq q'' + 1 > q'',$$
so $q'' < q'$. [Algebraic manipulation: monotonicity in $\mathbb{Z}$, H1]
16. Substitute Step 13 into clause (ii) ($p\,q' = p'\,q$):
$$p\,(d\,q'') = (d\,p'')\,q,\qquad\text{i.e.,}\quad d\,(p\,q'') = d\,(p''\,q).$$
[Substitution; associativity and commutativity of $\cdot$ in $\mathbb{Z}$, H1]
17. $d \neq 0$ (since $d \geq 2$), and $\mathbb{Z}$ is an integral domain, so by cancellation $p\,q'' = p''\,q$. [H1: integral-domain cancellation law]
18. Thus $q'' \in \mathbb{Z}_{>0}$ (Step 14) and there exists $p'' \in \mathbb{Z}$ with $p\,q'' = p''\,q$, so $q'' \in S$ by Definition of $S$. [By Steps 14, 17; Definition of $S$]
19. But $q'$ is the least element of $S$ (Step 8), so $q' \leq q''$, contradicting $q'' < q'$ (Step 15). [Logic: contradiction via trichotomy, H1]
20. Hence $d = 1$, i.e., $\gcd(p', q') = 1$ — clause **(iii)**. [Logic: reductio]

### Part C. Conclusion.

21. Steps 10 and 20 establish clauses (i)–(iii) for the fixed but arbitrary $(p,q)$. By universal generalization, Lemma 2 holds. [By Steps 10, 20; Logic: universal generalization] $\blacksquare$

---

## Lemma 3 (Parity cascade)

*Let $p, q \in \mathbb{Z}$ with $q \neq 0$. If $p^2 = 2 q^2$, then $2 \mid p$ and $2 \mid q$.*

**Proof.**

### Part A. Setup.

1. Fix arbitrary $p, q \in \mathbb{Z}$ with $q \neq 0$, and assume $p^2 = 2 q^2$. [Logic: universal introduction + assumption]

### Part B. $2 \mid p$.

2. Set $k := q^2 \in \mathbb{Z}$ (H1 closure). Then $p^2 = 2\,k$. [H1; By Step 1]
3. By Definition of divides, $2 \mid p^2$. [Definition of divides; By Step 2]
4. Apply Lemma 1 (contrapositive form, Part B) to $p$: since $p \in \mathbb{Z}$ and $2 \mid p^2$, we obtain $2 \mid p$. [By Lemma 1]
5. Hence there exists $m \in \mathbb{Z}$ with $p = 2m$. [Definition of divides; Logic: existential instantiation]

### Part C. $2 \mid q$.

6. Squaring Step 5: $p^2 = (2m)^2$. [Squaring well-defined on $\mathbb{Z}$, H1]
7. $(2m)^2 = (2m)(2m) = 4\,m^2 = 2\,(2 m^2)$. [Associativity/commutativity of $\cdot$, H1]
8. Combining Steps 6–7: $p^2 = 2\,(2 m^2)$. [Transitivity of equality]
9. From the hypothesis $p^2 = 2 q^2$ (Step 1) and Step 8: $2\,(2 m^2) = 2\,q^2$. [Transitivity of equality]
10. $2 \neq 0$ in $\mathbb{Z}$, and $\mathbb{Z}$ is an integral domain, so the cancellation law yields $2 m^2 = q^2$. [H1: integral-domain cancellation law]
11. Equivalently $q^2 = 2\,m^2$, and $m^2 \in \mathbb{Z}$. By Definition of divides, $2 \mid q^2$. [H1; Definition of divides]
12. Apply Lemma 1 (contrapositive form) to $q$: since $q \in \mathbb{Z}$ and $2 \mid q^2$, we obtain $2 \mid q$. [By Lemma 1]

### Part D. Conclusion.

13. Steps 4 and 12 give $2 \mid p$ and $2 \mid q$. Since $(p,q)$ was arbitrary subject to the standing hypothesis, Lemma 3 is established. [Logic: conjunction introduction; universal generalization + conditional introduction] $\blacksquare$

---

## Lemma 4 (Main theorem)

*There do not exist $p \in \mathbb{Z}$ and $q \in \mathbb{Z}\setminus\{0\}$ with $p^2 = 2 q^2$.*

**Proof.**

### Part A. Assumption for reductio.

1. Suppose for contradiction that such integers exist: $\exists\,p \in \mathbb{Z},\ \exists\,q \in \mathbb{Z}\setminus\{0\}:\ p^2 = 2 q^2$. [Logic: reductio assumption]
2. Fix witnesses $p \in \mathbb{Z}$ and $q \in \mathbb{Z}\setminus\{0\}$ with $p^2 = 2 q^2$. [Logic: existential instantiation]

### Part B. Extract a lowest-terms representative (Lemma 2).

3. Apply Lemma 2 to $(p,q)$ (preconditions met by Step 2) to obtain $p', q' \in \mathbb{Z}$ with (i) $q' \neq 0$, (ii) $p\,q' = p'\,q$, (iii) $\gcd(p', q') = 1$. [By Lemma 2; Logic: existential instantiation]

### Part C. Transport $p^2 = 2 q^2$ to $(p', q')$.

4. Squaring clause (ii): $(p\,q')^2 = (p'\,q)^2$. [Squaring well-defined, H1]
5. By associativity/commutativity of $\cdot$ in $\mathbb{Z}$:
$$p^2\,(q')^2 = (p')^2\,q^2.$$
[Algebraic manipulation, H1]
6. Substitute $p^2 = 2 q^2$ (Step 2) into the LHS:
$$(2 q^2)\,(q')^2 = (p')^2\,q^2.$$
[By Steps 2, 5; substitution]
7. Rearrange: $q^2\,\bigl(2\,(q')^2\bigr) = q^2\,(p')^2$. [Algebraic manipulation, H1]
8. Since $q \neq 0$ (Step 2) and $\mathbb{Z}$ is an integral domain, $q^2 = q\cdot q \neq 0$. [H1: no nonzero zero divisors]
9. Apply cancellation with $c := q^2 \neq 0$ to Step 7:
$$2\,(q')^2 = (p')^2,\quad\text{i.e.,}\quad (p')^2 = 2\,(q')^2.$$
[H1: integral-domain cancellation law; symmetry of equality]

### Part D. Apply Lemma 3 to $(p', q')$.

10. $p' \in \mathbb{Z}$, $q' \in \mathbb{Z}\setminus\{0\}$ (from clause (i)), and $(p')^2 = 2\,(q')^2$ (Step 9) are exactly the preconditions of Lemma 3. [By Steps 3, 9]
11. By Lemma 3, $2 \mid p'$ and $2 \mid q'$. [By Lemma 3]

### Part E. Contradiction with coprimality.

12. From Step 11, $2$ is a common divisor of $p'$ and $q'$. [Definition of divides]
13. By the gcd definition (clause (ii): every common divisor divides the gcd), $2 \mid \gcd(p', q')$. [Definition of gcd; By Step 12]
14. By clause (iii) of Step 3, $\gcd(p', q') = 1$. Substituting into Step 13: $2 \mid 1$. [By Steps 3, 13]
15. By Definition of divides, $2 \mid 1$ would give $t \in \mathbb{Z}$ with $1 = 2 t$, making $1$ even. [Definition of divides; Definition of even]
16. But $1 = 2\cdot 0 + 1$, so $1$ is odd (Definition of odd), and by the parity dichotomy (H3), $1$ cannot be both even and odd. This contradicts Step 15. [Definition of odd; H3]

### Part F. Conclusion.

17. Steps 1–16 derive a contradiction from the reductio assumption of Step 1. By reductio ad absurdum, no such integers $p, q$ exist:
$$\neg\,\exists\,p \in \mathbb{Z}\ \exists\,q \in \mathbb{Z}\setminus\{0\}\ :\ p^2 = 2 q^2.$$
[Logic: reductio ad absurdum, discharging Step 1]

This is the statement of the Main Theorem. $\blacksquare$

∎

---

```json
{"complete": true, "unresolved_gaps": 0}
```
