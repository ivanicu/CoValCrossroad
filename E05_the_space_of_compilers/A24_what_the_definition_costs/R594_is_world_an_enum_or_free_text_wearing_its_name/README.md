# R594 · The corpus's own verdict fields are free text — and the early rounds are the worse ones

**Decision this makes safe:** stop treating `world` / `verdict` as queryable. **Every `GROUP BY` over
this corpus's own verdicts is already broken**, and no round should be built on one.

| key | rounds | distinct | β | matched ceiling | verdict | values occurring **once** |
|---|---|---|---|---|---|---|
| `verdict` | 290 | 334 | **+0.9558** | +0.9898 | **B FREE TEXT** | **94.0%** |
| `world` | 270 | 217 | **+0.9279** | +0.9953 | **C PARTIAL** | **95.4%** |
| `controls` | 145 | 138 | **+0.9868** | +1.0062 | **B FREE TEXT** | **97.1%** |
| `n_prompts` | 135 | 116 | +1.0552 | +1.1169 | **SCALAR — wrong instrument** | 89.7% |

**334 distinct `verdict` values across 290 rounds.** `world` keeps a real enum core — `B`×52,
`A`×20, `UNVERIFIED`×8, about 30% of rounds — sitting on a **207-value singleton tail**. That is
HB8's `text_free` wearing an enum's name, which HB8 calls a schema bug outright.

## The instrument, and why it needs no judgement about content
"Free text vs enum" is not measurable by reading values and deciding — that is the rubric-invention
failure R593 already refused. The operational definition instead: **an enum's distinct-value count
saturates as more rounds are sampled; free text grows about linearly.** β is that exponent.

## ⛔ Two defects in my own instrument, both caught by a number that could not be true
1. **`n_prompts` returned β = +1.0677 and v1 called it FREE TEXT.** It is a **count**. HB8 types it
   `scalar_with_range`, and *"does its vocabulary saturate"* is not a question about a number — my
   instrument's unit was *distinct serialised values*, the claim's unit was *an unbounded vocabulary
   for a categorical field*. **Kept in the sweep and reported under its own type, because dropping it
   silently would have hidden the defect.**
2. **β > 1 was impossible against my ceiling, which means the ceiling was mis-specified.** The
   synthetic free-text control wrote **exactly one** value per round, pinning it at 1.0000, while
   real keys write **sets** (`n_prompts` averages 1.70 values/round). **A ceiling the object under
   test can jump over is not a ceiling** — §4's floor/ceiling row. Rebuilt **per key, matched to that
   key's own values-per-round distribution**, which is why the table above compares each β to its own
   ceiling rather than to 1.

## ⭐⭐⭐ The confound was refuted in the direction opposite to my expectation
R592 measured a **13.6× late-half decay** in code persistence, so I expected the free-text tail to be
recent — and therefore mine.

| key | short values (≤12 chars), early → late |
|---|---|
| `world` | **0.333 → 0.718** |
| `verdict` | **0.161 → 0.453** |
| `controls` | 0.000 → 0.000 *(always a serialised dict; structurally never short)* |

**The late rounds are MORE enum-like, not less. The discipline was acquired, not lost.**

⭐ **Two practices moved in opposite directions over the same rounds** — code persistence decayed
13.6×, verdict vocabulary tightened ~2.2× and ~2.8×. *"My practice degraded" is not a general truth;
it is specific to one axis, and R592's finding does not license the wider version of itself.*

⚠ **The singleton comparison (1.000 → 0.921) is NOT admissible** as evidence here: singleton fraction
falls mechanically as sample size rises, and early n = 93 against late n = 209. **The short-value
fraction is the clean contrast** — it is per-value and unbiased by n — and it moves the same way.

## Controls
| control | returned |
|---|---|
| **negative** — synthetic 3-value enum, same population | β = **+0.0180** [+0.0000, +0.0540], 3 distinct at n = 577 |
| **positive** — synthetic unique-per-round | β = **+1.0000** [+1.0000, +1.0000] |
| **separation** | **+0.9820** — PASS; the estimator distinguishes the two worlds |
| **placebo** — shuffle which round holds which value | β unchanged at +1.0000 — PASS, β reads the multiset not the pairing |
| **matched ceiling** | rebuilt per key: +0.9898 / +0.9953 / +1.0062 / +1.1169 |

**MULTIPLICITY:** 4 keys × 8 sweep points × 3 seeds + 2 synthetic controls, all reported; **1 landed
strictly between floor and ceiling.**

**KNOWN BIAS, stated:** lists and dicts are serialised, so a structural difference counts as a
different value. **This biases β upward — against the enum hypothesis** — which is the conservative
direction for a schema-bug claim.

**IMPOSSIBLE, named:** β measures whether a vocabulary is **closed**, never whether its members are
the **right** ones. A key could take exactly 3 values and all of them nonsense. That needs an external
reader this site does not have.

## The sentence I can no longer write
> *"`verdict` and `world` are the corpus's two reliable keys."*

They are its two most **frequent** keys. **Neither is queryable**, and `verdict` — the most frequent
of all — has **more distinct values than the rounds that write it**.

## NEXT
`world` has a real enum core of `B` · `A` · `UNVERIFIED` covering ~30% of the rounds that write it.
**Check whether the singleton tail is TRANSLATABLE into that core** — take the rounds whose `world` is
a sentence and test whether each sentence contains exactly one of the core tokens as a prefix. If it
does, the tail is a formatting failure with a mechanical repair; if it does not, the vocabulary is
genuinely open and the core is a coincidence of three short rounds.
