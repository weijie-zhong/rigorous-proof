## Proposition

There do not exist integers $p, q \in \mathbb{Z}$ with $q \neq 0$ such that
$$\left(\frac{p}{q}\right)^2 = 2.$$

Equivalently: $\sqrt{2} \notin \mathbb{Q}$, i.e., there is no rational number whose square equals $2$.

Formally: $\neg\,\exists\, p \in \mathbb{Z}\,\exists\, q \in \mathbb{Z}\setminus\{0\}\ :\ p^2 = 2 q^2$.

## Hypotheses Inventory

- **H1**: The ambient number system is the ring of integers $\mathbb{Z}$, equipped with the usual operations $+, \cdot$ and the usual order $<$.
- **H2**: The rationals $\mathbb{Q}$ are defined as the field of fractions of $\mathbb{Z}$; a rational is represented by a pair $(p, q)$ with $p \in \mathbb{Z}$, $q \in \mathbb{Z}\setminus\{0\}$, modulo the equivalence $(p,q) \sim (p',q') \iff p q' = p' q$.
- **H3**: Standard facts of elementary number theory are available: the fundamental theorem of arithmetic (unique prime factorization in $\mathbb{Z}$), divisibility, and parity (even/odd).
- **H4**: The natural numbers $\mathbb{N} = \{0, 1, 2, \dots\}$ satisfy the well-ordering principle: every nonempty subset of $\mathbb{N}$ has a least element.

## Definitions

- **Integer**: An element of the ring $\mathbb{Z} = \{\dots, -2, -1, 0, 1, 2, \dots\}$.
- **Rational number**: A number expressible as $p/q$ with $p, q \in \mathbb{Z}$ and $q \neq 0$. The set of all such numbers is denoted $\mathbb{Q}$.
- **Divides**: For $a, b \in \mathbb{Z}$, we say $a \mid b$ iff there exists $k \in \mathbb{Z}$ with $b = a k$.
- **Even integer**: An integer $n$ such that $2 \mid n$, i.e., $n = 2k$ for some $k \in \mathbb{Z}$.
- **Odd integer**: An integer $n$ such that $n = 2k + 1$ for some $k \in \mathbb{Z}$. Every integer is exactly one of even or odd.
- **Greatest common divisor**: For $a, b \in \mathbb{Z}$ not both zero, $\gcd(a,b)$ is the unique positive integer $d$ such that (i) $d \mid a$ and $d \mid b$, and (ii) for every $c \in \mathbb{Z}$ with $c \mid a$ and $c \mid b$, we have $c \mid d$.
- **Coprime / in lowest terms**: Integers $a, b$ are coprime iff $\gcd(a,b) = 1$. A representation $p/q$ of a rational is **in lowest terms** iff $\gcd(p,q) = 1$ and $q > 0$.
- **Square**: For $n \in \mathbb{Z}$, the square of $n$ is $n^2 := n \cdot n$.
- **$\sqrt{2}$** (informal, only used in the proposition's restatement): any real number $x$ with $x^2 = 2$ and $x > 0$; its existence in $\mathbb{R}$ is not required for the proof, since the proposition is stated purely in terms of integers $p, q$.

## Difficulty Assessment

**Easy.**

Justification: This is the canonical textbook result on irrationality. The standard proof strategy (proof by contradiction, reduce $p/q$ to lowest terms, derive that both $p$ and $q$ are even, contradicting coprimality) is immediately obvious and uses only elementary definitions (rational, even, coprime) plus the single lemma "if $p^2$ is even then $p$ is even." Fewer than three definitions carry load, and no case analysis or advanced machinery is required.

---

```json
{"difficulty": "easy", "hypothesis_count": 4, "proposition_summary": "There are no integers p, q with q ≠ 0 such that p^2 = 2q^2 (i.e., √2 is irrational)."}
```
