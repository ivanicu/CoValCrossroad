# R1007 · the negative control R1005 declared and never ran — and it retracts R1005

**THE DECISION THIS MAKES SAFE.** Whether R1005's convergence is a property of the **admission rule**
or of the **level band**. It is the band. **Δ = +0.0828 is withdrawn.**

---

## ⛔ Why this round exists — a defect in my own work

R1005's docstring declares:

```
NEGATIVE CTRL   shuffle the membership labels among the 96 arms, keeping set sizes fixed …
                ≥200 shuffles. ⚠ World it excludes: "any set of this size shows this Δ".
PLACEBO         Δ between two disjoint random halves of the NON-members must be ≈ 0.
```

**Neither was implemented.** `NSHUF = 200` sits at line 74 and is used nowhere; the only
`permutation` call permutes **prompts** for the held-out split. R1005's committed artifact lists one
control: `positive_planted_duplicate`.

⭐ **The world R1005 named as excluded was never tested — and R1006 then spent a whole round
excluding a *different* rival while this one stood open.**

## The result

Same statistic, same level-matching, same held-out split, same deduplication. Only *which arms are
called members* changes.

| null | what it destroys | cells clearing the 95th pct |
|---|---|---:|
| **BAND-MATCHED** (binding) | which-arms, **level held fixed** | **6 / 30** |
| unrestricted (weaker) | which-arms and level together | 18 / 30 |

⭐⭐ **And the survivors run the wrong way:**

| caliper | clears the band null | mean band size |
|---:|---:|---:|
| 0.010 | **0 / 10** | 10.2 |
| 0.020 | **1 / 10** | 13.4 |
| 0.040 | **5 / 10** | 20.3 |

**Monotone.** The cells that survive are exactly the ones where **level matching is loosest**. A real
effect is *clearest* under the tightest matching; this one appears only as the comparison is relaxed.
**That is a band artifact's signature, and it is why the retraction is not a coin flip.**

## Controls — because an attack that kills a claim needs them most

| control | result |
|---|---|
| **POSITIVE** | a planted extension of 6 literal copies scores **0.8434**; a random set of the same size **0.6420**. The comparison **can** see coherence |
| **PLACEBO** | two disjoint halves of the non-members, 1,000 draws: mean **−0.0001**, sd **0.0132** — exactly zero, as R1005 required and never checked |
| **NEGATIVE ①** | unrestricted null, 1,000 draws |
| **NEGATIVE ②** | band-matched null, 1,000 draws — **the binding one** |
| **DEDUPLICATION** | 96 → 85 distinct, inherited from R1005 |

⭐ **The unrestricted null passes 18 of 30 and is reported beside the binding one, never instead of
it.** It is the weaker test and the flattering one; quoting it would be the multiplicity failure with
manners applied to nulls.

## What survives, and what is moot

- ✅ **The duplicate census stands** — 14 identical pairs, 96 → 85 distinct, extension 8→4 and 11→6.
  A fact about the arms, independent of Δ.
- ⚠ **R1006's measurement stands, its purpose is moot.** `indep_k` and `greedy_k` really are the most
  homogeneous families; they are no longer defending anything.
- ❌ **R1005's Δ, and "the extension is a coherent family", are withdrawn.**

## ⚠ Impossible here, with what it would require

**A null over admission RULES rather than over SETS.** The honest null would sample alternative rules
of the same expressive class and re-derive membership. The release ships one comparator family and one
label predicate, so **the rule space has no measure on it here.** It would require a generator of
admissible rules.

**Construct validity — N/A**: this asks whether the admission rule carries the convergence, never
whether convergence tracks correctness.

## ⚠ Two engineering notes, both of which were nearly errors

- The first draft sliced a (968, 97, 97) tensor inside a 1,000-draw null — silent at 90 seconds.
  Averaging over prompts **first** is ~100× faster **and is exactly R1005's statistic**: R1005 took
  the mean over pairs of per-pair means, so the estimand was already mean-of-means. **The slow draft
  would have weighted pairs by valid-prompt count — a different quantity.** The fast version is the
  faithful one, which is the only reason it may replace the slow one.
- A `ps | grep` kill-loop matched **its own parent shell**, because the command text contained the
  path it was grepping for. Same class as `pgrep -f` matching itself.

## Alternatives considered

**Report the unrestricted null's 18/30 as the result.** Refused — it destroys level *and* membership
together, so it cannot separate them, and it is the null that flatters.

**Call Δ refuted to zero.** Refused: 6 cells do clear, and the extensions here are 2–7 arms, so power
is limited. The claim is **not established**, which is a different statement from **shown to be zero**.
