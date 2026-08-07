# Claim card — equivalence tests at a declared margin

Written before any code, per the binding process rule.

---

## Claim

Several load-bearing statements in this package are **null claims** — "no detected loss",
"costs nothing measurable", "the decay is flat" — and every one of them was read off a
**non-significant** result. Non-significance is not equivalence. At a declared margin
δ = 0.01 accuracy points, each of these contrasts either **is** shown practically equivalent to
zero or **is not**, and which one it is has never been tested.

## Estimand

For each paired contrast Δ, the two one-sided tests

```
H0_lower:  Δ ≤ −δ        H0_upper:  Δ ≥ +δ        δ = 0.01
```

Equivalence is declared only if **both** are rejected at α = 0.05 — equivalently, if the **90%**
bootstrap CI of Δ lies entirely inside (−δ, +δ). The published intervals are 95%, which is the
interval for a different question; using them here would be sloppy in an unprincipled direction.

Reported for all 21 persisted paired vectors from r34, r35, r36, r37.

## Is the target observed?

**The contrast is observed. The margin is not.** δ = 0.01 is a **stipulation** carried in from
external review, not a quantity derived from any decision this project makes. Nothing in the
data says 0.01 accuracy points is the threshold at which a rubric becomes unfit for a purpose,
because no purpose has been specified with that precision.

So every verdict below is **conditional on δ**, and the round reports a **δ-sweep** rather than a
single answer, so a reader who thinks the margin should be 0.005 or 0.02 can read their own row
instead of inheriting mine.

## Alternative worlds

| world | what the cross-tab shows |
|---|---|
| **real but negligible** | significant vs 0 **and** equivalent at δ — the effect exists and does not matter at this margin |
| **real and material** | significant **and** not equivalent |
| **genuinely no effect** | non-significant **and** equivalent — the only cell where "no effect" is a supported reading |
| **inconclusive** | non-significant **and** not equivalent — the data cannot distinguish zero from an effect that would matter. **This is the cell where a null was being read off silence** |

The point of the round is to find out which claims are in the fourth cell.

## Intervention

None. This is a re-analysis of persisted paired vectors, all of which reproduce their published
summaries exactly.

## Null / positive control

An equivalence test that declares everything equivalent has no discriminating power, and a
"tightly bounded" report from it would be silence mistaken for precision.

**Positive control (mandatory, must pass before any verdict is read):** run the same instrument
on `D_population` = +0.0576, an effect 5.8× the margin. It **must** return NOT EQUIVALENT. If it
does not, the instrument is unfit and every other row is void.

**Negative control:** a vector of exact zeros must return EQUIVALENT at every δ > 0.

---

## Five mandatory checks

**1. Can this instrument return the opposite answer?** Yes, in both directions, and both
directions are controlled for above.

**2. Does it observe the target?** It observes the contrasts exactly. It does **not** observe
whether δ = 0.01 is the right margin — that is stipulated, and the sweep is the honest form.

**3. By what path can construction data reach evaluation?** None new — this round adds no
estimation. It inherits whatever scope each source contrast already carries, and those scopes
travel with each row rather than being dropped at the summary.

**4. What other world produces the same result?** A contrast can be equivalent **in aggregate**
and heterogeneous underneath — the exact failure mode item 1 rescoped C19 for. An equivalence
result at the aggregate level is therefore **not** a population-invariance result, and must not
be reported as one. Criterion-level heterogeneity is queue item 5, not this round.

**5. Which decision changes?** Any contrast landing in the **inconclusive** cell cannot be cited
as a null anywhere in the package, and its README sentence has to say so. That is a concrete
edit list, which is the deliverable.

---

## Stopping rule

Pure CPU re-analysis, seconds. It ends when every persisted paired vector has a cross-tab cell
and the README/manifest sentences that read a null off a fourth-cell contrast have been changed.
