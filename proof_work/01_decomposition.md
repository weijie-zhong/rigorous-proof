# Decomposition into Lemmas

The proof is broken into four lemmas. `Lemma 4` is the main theorem (the original target proposition). `Lemma 1` is the parity lemma, `Lemma 2` is the lowest-terms reduction, `Lemma 3` is the parity cascade (the algebraic core), and `Lemma 4` assembles them into the final contradiction.

---

## Lemma 1 (Parity lemma: squares of odd integers are odd)

**Statement.** For every $n \in \mathbb{Z}$, if $n$ is odd then $n^2$ is odd. Equivalently (by contrapositive): for every $n \in \mathbb{Z}$, if $2 \mid n^2$ then $2 \mid n$.

**Depends on.**
- H1 (integer arithmetic: $+, \cdot$, distributivity).
- H3 (definition of even/odd — every integer is exactly one of $2k$ or $2k+1$).

**Why needed.** This is the *only* non-purely-algebraic step in the proof. It is invoked twice inside Lemma 3 to move from "$p^2$ even" to "$p$ even", and from "$q^2$ even" to "$q$ even".

---

## Lemma 2 (Lowest-terms representative)

**Statement.** For every pair $(p, q) \in \mathbb{Z} \times (\mathbb{Z}\setminus\{0\})$, there exist integers $p', q'$ with:
(i) $q' \neq 0$,
(ii) $p q' = p' q$ (i.e., $(p,q) \sim (p',q')$ as rationals), and
(iii) $\gcd(p', q') = 1$ (i.e., $p'$ and $q'$ share no common integer divisor other than $\pm 1$).

**Depends on.**
- H1 (integers).
- H2 (rational equivalence $(p,q) \sim (p',q')$).
- H4 (well-ordering of $\mathbb{N}$) — used to pick $q' := \min\{\,d \in \mathbb{N}_{>0} : \exists p'\in\mathbb{Z},\ p d = p' q\,\}$, thereby producing a coprime pair without needing the full unique factorization theorem.

**Why needed.** Without a lowest-terms representative, the contradiction in Lemma 4 has nothing to collide with. The coprimality clause $\gcd(p',q') = 1$ is precisely the assumption that the parity cascade (Lemma 3) contradicts.

---

## Lemma 3 (Parity cascade: $p^2 = 2q^2$ forces $2 \mid p$ and $2 \mid q$)

**Statement.** Let $p, q \in \mathbb{Z}$ with $q \neq 0$. If $p^2 = 2 q^2$, then $2 \mid p$ **and** $2 \mid q$.

**Depends on.**
- Lemma 1 (parity lemma, applied twice).
- H1 (integer arithmetic, in particular $(2m)^2 = 4m^2$ and the cancellation $4m^2 = 2q^2 \Rightarrow q^2 = 2m^2$; note the cancellation by $2$ is valid in $\mathbb{Z}$ since $\mathbb{Z}$ has no zero divisors).

**Why needed.** This is the algebraic engine of the contradiction. It shows that *any* integer solution to $p^2 = 2q^2$ has both coordinates even, which is incompatible with coprimality (the property delivered by Lemma 2).

---

## Lemma 4 (Main theorem: $\sqrt{2}$ is irrational)

**Statement.** There do not exist $p \in \mathbb{Z}$ and $q \in \mathbb{Z}\setminus\{0\}$ such that $p^2 = 2 q^2$.

**Depends on.**
- Lemma 2 (lowest-terms representative).
- Lemma 3 (parity cascade).
- H2 (the equivalence relation on rationals; specifically, if $(p,q) \sim (p',q')$ and $p^2 = 2q^2$, then $(p')^2 = 2(q')^2$ — this is an algebraic consequence of $p q' = p' q$, which we will verify inside Lemma 4's proof).

**Why needed.** This IS the target proposition. It assembles the pieces:
1. Assume for contradiction that such $(p,q)$ exist.
2. Apply Lemma 2 to obtain a coprime representative $(p', q')$ with $(p')^2 = 2(q')^2$.
3. Apply Lemma 3 to $(p', q')$ to conclude $2 \mid p'$ and $2 \mid q'$.
4. This contradicts $\gcd(p', q') = 1$ from Lemma 2.
5. The assumption is false; no such $(p, q)$ exist. ∎

---

## Dependency Graph

```
     H1, H3                              H1, H2, H4
        │                                    │
        ▼                                    ▼
   ┌─────────┐                          ┌─────────┐
   │ Lemma 1 │                          │ Lemma 2 │
   │ (parity │                          │ (lowest │
   │  lemma) │                          │  terms) │
   └────┬────┘                          └────┬────┘
        │                                    │
        │  H1                                │
        ▼                                    │
   ┌─────────┐                               │
   │ Lemma 3 │                               │
   │(parity  │                               │
   │cascade) │                               │
   └────┬────┘                               │
        │                                    │
        │          H2                        │
        ▼          ▼                         ▼
        ┌──────────────────────────────────────┐
        │       Lemma 4 (Main Theorem)         │
        │   ¬∃ p,q ∈ ℤ, q≠0 : p² = 2q²         │
        └──────────────────────────────────────┘
```

**Reading the graph.** Lemma 1 feeds Lemma 3 (the parity lemma is used inside the cascade). Lemma 2 and Lemma 3 both feed Lemma 4 directly; Lemma 4 additionally uses H2 to transport the equation $p^2 = 2q^2$ from $(p,q)$ to its lowest-terms representative $(p',q')$. Terminal node: Lemma 4 — the main theorem.
