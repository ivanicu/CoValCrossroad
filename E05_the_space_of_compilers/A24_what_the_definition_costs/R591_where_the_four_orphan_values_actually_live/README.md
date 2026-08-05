# R591 · Three of the four orphans were never defects — and the fourth is real

**Decision this makes safe:** the deliverable's provenance audit can stop. **One ungrounded pair of
decimals exists, it is annotated, and the conclusion it decorated stands.**

**All four worlds fired, and each fired differently — the strongest shape this design admits.**

| value | cited | verdict | what it actually is |
|---|---|---|---|
| **0.5404** | *(R475, R485)* | **A · R590's truncation** | R485's artifact holds `"ceiling": 0.5404` **verbatim** |
| **0.0779** | *(R535)* | **grounded, derived** | `topw_k4.a2 − topvar_k4.a2 = 0.077890` |
| **0.5451** | *(R479)* | **the estimand was wrong** | R479 holds `single = 0.5458`; 0.5451 is external **by the sentence's own words** |
| **0.0200** | *(R514, R515)* | ⛔ **CONFIRMED UNGROUNDED** | absent from `results/` **and** both READMEs, unreachable by any combination |

## ⛔ First: this round's own NEXT line was a strictly dominated action
R590 closed with *"the cheapest next step is asking whether each sits in a NEIGHBOURING round."*
**Scanning all 365 rounds costs the same single pass and answers strictly more** — neighbour, distant,
or nowhere — while neighbour-only can return "not a neighbour" and leave you where you started.
*Check #191 caught it.* **A superlative over my own work, which §4 names as the highest-risk sentence
in a report.**

## ⛔ And this round's own KILL was the failure mode the standard names
v1 killed on **`|S(v)| inside [floor_min, floor_max]`** — *min/max of N draws quoted as an interval*,
verbatim from §4. Near `0.0200` that band was **[2, 30]**, wide enough to swallow any `|S|` a real
value could produce: **all four values were declared UNRESOLVABLE by construction.** It also tested
the wrong quantity — the estimand is not *"is S(v) unusually large"* but *"does S(v) hit a **cited**
round more often than a sourceless value would."* Rebuilt as an empirical hit-null: **p_hit = 0.0000
on all four** (120 synthetic values each, 3 seeds).

## ⭐⭐⭐ Presence is not provenance — and in this campaign's own score band it is barely evidence
**R235 persists 10,822 distinct 4-dp values; across `[0.4500, 0.6500]` it covers 78.6% of every
possible slot.** R439's 1,820-element distribution covers **83.8%** of `[0.5199, 0.5618]` — which is
exactly where every headline A2 lives (0.5404 · 0.5451 · 0.5458 · 0.5640).

⚠ **So a round that persists a bootstrap distribution "contains" almost any number you ask it for**,
and every one of `0.5451`'s four hits *(R235, R332, R355, R439)* is a collision of this kind — grid
cells and distribution entries, not a human ceiling.

⭐ **Both surviving groundings are SEMANTIC, not numeric.** `"ceiling": 0.5404` is a key whose *name*
matches the claim's word; `topw − topvar` are arms *named* for "reads weights" and "reads spread".
**Numeric presence found nothing that mattered; matching the name did.**

## The estimand that was false
`0.5451` is not a defect and **the question was**. The sentence reads *"single-annotator-vs-annotator
returns **0.5458** against this campaign's independently committed human ceiling of **0.5451**"* —
R479 holds `single = 0.54584879`. **A citation attaches to a CLAIM, not to every decimal in the
sentence**, and a claim may legitimately compare a measured number to an externally committed one.
R590 and this round's v1 both assumed containment of every decimal.

## Controls
| control | returned |
|---|---|
| **positive** — cited values recoverable in a cited round | **55 of 71 = 0.7746** *(pre-registered floor 0.60)* **PASS** |
| **positive @ g=0** — artifacts emptied | **0 of 71** — **PASS, it can fail** |
| **negative-a** — collision floor, 120 synthetics × 3 seeds | mean `|S|` **10.67 / 4.61 / 3.10 / 2.98** |
| **negative-b** — hit-null: a sourceless value landing in *v*'s own cited round | **0.0000** on all four |
| **cited-round population** — did those rounds ship artifacts at all | **all non-empty** — an absence is an absence, not an empty population |
| **contamination** — R585–R591 read `STATEMENT.md`, so hold its values by construction | **excluded**; reported both ways |

**Derivation reach is UNFALSIFIABLE at 4 dp and the round says so:** 30 unrelated rounds also reach
`0.0200` **30.0%** of the time, `0.0779` **26.7%**, `0.5451` **20.0%**. Only `0.5404` has a null low
enough (**6.7%**) to matter — and it did not need the test, being stored verbatim.

## Specification curve — 6 cells per value, all reported
`scope ∈ {json, json+txt, clean(−audit)} × match ∈ {rounded, prefix}`. **Prefix is R590's rule and is
included to price it:** it loses R485 for `0.5404` in *no* cell — so R590's miss was **not** the
matcher, it was recording `[475]` where the document writes `(R475, R485)`. Prefix does cost
`0.5451` three of four hits and `0.0779` seven of twelve.

**MULTIPLICITY:** 1,392 cells (4 values × 355 rounds), **39 surviving**.

## What this makes safe, and what it costs
✅ **The provenance audit closes.** Of 24 cross-era shared values, **23 are accounted for**; one pair
of margin decimals in clause ①'s row is ungrounded and now carries a `⁇` annotation in
`STATEMENT.md` naming what is missing and what still stands.

⚠ **`⛔ DELETABLE` for clause ① is unaffected** — it rests on `n_pass2_fail1 = 0` and `n_arms = 41`,
both in R514's artifact. **Annotated, not corrected**: which run produced `+0.0582` is unknown, and
substituting R515's `0.0577` would assert an identity nobody has established.

⚠ **R590 could not be audited from its own artifact** — it shipped `README.md` + `results/` and **no
`run.py`**, so its extractor is unreadable and the truncation had to be established indirectly, via
the specification curve showing prefix matching would have found R485 too.

## The sentence I can no longer write
> *"four values in the statement are cited to rounds that do not hold them."*

**One is.** One was R590's bookkeeping, one is grounded as a derived difference, and one was a
question wrongly posed.

## NEXT
**Rounds ship `README.md` + `results/` and no `run.py`** — R590 is the case where that cost a direct
answer. **Count how many of the 365 rounds carry a runnable `run.py`**, because a round nobody can
re-run is a round whose instrument cannot be attacked, and that is a property of the corpus rather
than of any one finding.
