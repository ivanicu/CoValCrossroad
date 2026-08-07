# R1020 · under `A1·consensus` the definition excludes its own instance

**THE DECISION THIS MAKES SAFE.** Whether the arc's extension survives a target change **at the
population it reports**. **Under one defensible target it does not — and the arm it drops is
`coval_core`.**

---

## ⭐ A1 was copied, not reconstructed

R1019's NEXT warned that *a target rebuilt in order to sweep it can be built to fail*. **A1 is on
disk**, in R288's own `run.py`:

```python
T["A1·annot"][n]     = np.mean([float((c == h).all()) for h in HC[n]])
T["A1·consensus"][n] = float((c == CONS[n]).all())
```

exact-class agreement, averaged over annotators or taken against the sign-consensus. The only
remaining risk was transcription — which is what the control tests.

## The transcription control is exact

| arm | mine | R288 | Δ |
|---|---|---|---:|
| `coval_core` | 0.066476221325849 | 0.066476221325849 | **0.00e+00** |
| `topw_k4` | 0.065973341200429 | 0.065973341200429 | **0.00e+00** |
| `generic` | 0.059203400221706 | 0.059203400221706 | **0.00e+00** |

**Worst |Δ| over all 9 shared arms: 0.000e+00.** It is R288's statistic, not a lookalike.

## The result

| target | extension (96 arms) | `coval_core` in it |
|---|---:|---|
| `A2` (this arc throughout) | **9** | yes |
| `A1·annot` | **9** — the same nine | yes |
| **`A1·consensus`** | **4** — `coval_core_2bA`, `coval_core_2bB`, `topw_k6`, `topw_k8` | **NO** |

⛔⛔ **A target exists — at the full population, under this arc's own admission rule ②′∧③ — at which
the definition admits the released core's TWINS and two `topw` arms, and excludes the released core
itself.** That is *"the definition describes the instance"* failing in reverse: the object the clauses
were written from does not survive them under a defensible target.

## ⚠ R288's ∅ is NOT refuted by this

The **target** is identical (Δ = 0). But R288 swept **clause ② alone** against its own
`_blind4`/`_blind15` references over **10** arms; this is **②′∧③** against R921's certified
comparators over **96**. **Different admission rule and different population.**

Calling it a refutation would be the naming-collision error R1019 caught one round earlier, made in
the opposite direction. ⭐ **The positive control proving the target matches is exactly what makes the
remaining difference legible** — without it, "same name, different answer" would be unreadable.

## Controls

| control | result |
|---|---|
| **POSITIVE** | exact transcription against R288's committed per-arm values, worst \|Δ\| **0.000e+00** on 9 arms |
| **NEGATIVE** | a monotone rescaling (A1 × 3) leaves the admitted set **identical** — clause ② is a paired comparison and must be affine-invariant |
| **PLACEBO** | A1 against A1, symmetric difference **0** |
| **NOISE FLOOR** | the bootstrap interval on each paired difference, seed held equal to the A2 run so the target is the only moving part |

⚠ **The closest-arm diagnostic ranges over all arms, not ③-eligible ones.** It reports `oracle_k4`,
which fails ③ and appears in no extension. It answers *"how far is the best ②-candidate"*, not *"how
far is the best core candidate"* — reading it as the latter would be a unit mismatch.

## ⚠ `top1·mean` is not swept

A **choice**, not a limit: it is one line in the same committed source, but its R288 answer is about
**which arm** rather than about emptiness, so folding it in would make this round about two questions.

## Alternatives considered

**Report "R288's ∅ does not survive 96 arms".** Refused — that was this round's first verdict string
and it was wrong. Two things differ, not one, and the round's own positive control is what shows which
one does not.

**Lead with `A1·annot` matching A2.** Refused: it is the reassuring half. The `A1·consensus` result —
the definition dropping its own instance — is the one a reader needs, and burying it under the
agreement would be the multiplicity failure with manners applied to targets.
