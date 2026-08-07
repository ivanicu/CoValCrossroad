# R437 · the two bars **invert** between releases — neither clause dominates

**The decision this round makes safe:** whether candidate ④ earns a place in the definition. **It
does, and for a stronger reason than "it would have caught the second release":** it is the clause
that binds *exactly where* clause ② goes slack.

## ⛔ First: the announced step was forced, and arithmetic killed it

R436 closed with *"does ④ subsume clause ②? measure whether their admitted sets coincide at J."*
R436 **itself** measured ④ excluding **0 of 56 at J** — so ④ admits everything there,
`②-admitted ⊆ ④-admitted` is forced, and the question reduces to *"does ② admit everything"*, which
R360 answered long ago (33 of 42). **Nothing could have come out otherwise. Sixth announced step
checked, fifth killed.**

## Result — `W-INVERT`

| release | statistic (chance) | **BAR2** — clause ②'s reference | **BAR4** — best criterion-free rule | GAP = BAR4 − BAR2 | binds |
|---|---|---|---|---|---|
| **home** | A2 over 6 pairs (0.5000) | `random_k4_s0` **0.4945** | `min_ttr` **0.4512** | **−0.0416** vs MDE 0.0237 · RESOLVED | **②** |
| **second** | top-1 (0.4194) | `generic` **0.4497** | `length` **0.5135** | **+0.0637** [+0.0464, +0.0784] vs MDE 0.0231 · RESOLVED | **④** |

> **The signs are opposite and both are resolved.** At home clause ②'s reference sits *above* every
> criterion-free rule, so ② is the binding clause and ④ is slack. On the second release the
> criterion-free rule sits *above* ②'s reference — and R434 measured ② admitting **nothing** there.

**⛔ So neither clause dominates.** A definition carrying both is carrying a **max over two bars**,
not two independent tests, and **which one is doing the work is a property of the release.**

## ⚠ Sign only — the two GAPs must not be compared in magnitude

Different statistics, different chance rates (**0.5000** vs **0.4194**), different annotation
schemes. `−0.0416` and `+0.0637` are not on a common scale, and the round refuses to print a
difference-of-differences that would look like a measurement.

⚠ **And at home both bars sit *below* chance.** A2's base rate is 0.5; `random_k4_s0` is 0.4945 and
`min_ttr` is 0.4512, while the real arms reach 0.51–0.64. **The home ordering is of two sub-chance
references** — which is precisely *why* ② binds there: its reference is nearer chance, and a
reference nearer chance is a **higher** bar than a systematically wrong rule. Stated here rather
than left for a reader to notice.

## Controls

| control | returned |
|---|---|
| POSITIVE — an oracle must sit above **both** bars | `oracle_k4` **0.6353** > both ✅ |
| g=0 — two draws of the **same** reference class must not be resolvedly ordered | 5 draws: 0.4945, 0.4945, 0.5024, 0.5024, 0.4868 — spread **0.0156** < MDE 0.0237 ✅ |
| PLACEBO — a bar against itself | exactly 0 ✅ |
| NEGATIVE — each release's chance rate printed beside both bars | done, and it changed the reading (see above) |
| FLOOR | paired bootstrap on each release's own clustering unit — prompts at home, **conversations** on the second (R413) — 3 seeds |

## What this changes about ④

R436's argument was *"④ would have caught the second release."* That is true and weak — it is a
statement about one corpus. **This is the stronger form:** ④ and ② are two bars on the same axis
whose order **flips**, so ④ is not a redundant conjunct that happens to fire once. It covers the
regime where ② is empty, and ② covers the regime where ④ is slack.

⚠ **What this does not establish:** that the max of the two bars is the *right* bar, or that a third
regime does not exist where both go slack. Two releases is not a distribution of releases.

## Impossible here, named

- **comparing the two GAPs in magnitude** — requires a common scale two annotation schemes don't give.
- **the supremum over criterion-free rules** — R435's 30-member family, restated.
- **that the inversion generalises** — two releases.
- **construct validity of either target** — each release's own human labels.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
