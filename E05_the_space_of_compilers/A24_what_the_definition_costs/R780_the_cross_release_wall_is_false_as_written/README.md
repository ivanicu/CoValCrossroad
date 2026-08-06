# R780 · the cross-release wall is false as written, and the site it hid is better powered

`run.py` · `PREREGISTRATION.txt` · `results/cross_release.json` · 968 prompts (r1) + 1,684 n=4
interactions (r2)

## THE DECISION THIS MAKES SAFE

**`cross-release` may no longer be written into an impossibility register unqualified.** A second
release is on disk — 2,200 conversations / 7,344 interactions, seven arms already scored — and for
the definition's load-bearing contrast it has **better resolution than release 1**: MDE **0.0124**
against release 1's **0.0216**, and the n required to resolve a release-1-sized effect is **366**
against **1,684 available — a 4.6× surplus**. The register was not merely wrong, it was hiding the
better-powered site.

## ⚠ WHAT IS AND IS NOT NEW HERE

**The existence is R556's**, not mine: *"the second release is present — `data/utterances.jsonl` —
and 3 of 375 artifacts were computed on it."* R398, R427, R433, R434 measured on it. **What is new
is that the correction never reached the artifacts.**

**And the object already scopes the wall correctly.** `corebench/score.py:33` registers
`H3_cross_release: "a second values-annotation release WITH THIS SCHEMA"`. Release 2 ships no rubric
and no annotator panel, so the schema-bound half of the wall is **real**. The round READMEs drop
*"with this schema"* and thereby assert something strictly stronger than the object supports — the
scope error that accounts for 11 of 12 retractions in the audited programme.

## E1 · THE CENSUS

| | lines |
|---|---:|
| assert an unscoped cross-release wall | **21** |
| written at or before R556 — true as far as their author knew | 13 |
| **written after R556 — a correction that did not reach the artifact** | **8** |

Rounds after R556: **704, 714, 716, 718, 720, 721, 722, 779**. The last is mine, written an hour
before this round. R780's own artifacts are excluded from the count.

### the search is an instrument, and its negative control caught it

The first pattern matched `one release`, which also matches **inside `one released core, and its
sham is ours`** — a *correctly*-scoped line. It flagged 1 of 3 known-good lines and inflated the
count to 23 across 9 post-R556 rounds. Tightened to `one release(?!d)`: **0 of 3** wrongly flagged,
and **R711 leaves the list** — it was never asserting the wall. The loose pattern would have
inflated the number using exactly the entries that prove the arc sometimes gets this right.

| search control | returned | |
|---|---|---|
| POSITIVE — a known-unscoped line, and R779's own register row | flagged, found exactly once | PASS |
| NEGATIVE — three correctly-scoped lines | 0 of 3 flagged | PASS |
| UNIT — instrument unit vs claim unit named as two strings | *a regex match in a round artifact* vs *a line in a round artifact* → a line is the unit of both | PASS |

## E2 · THE MEASUREMENT THE WALL FORBADE

Gauge-matched: release 2's **n=4 stratum only** (6 pairs, as release 1), release 1's **mean ranking**
as a single score vector (as release 2 ships), and the **same `core_generic.json`** as the blind
reference on both sides — asserted in code, exit 2 otherwise.

| contrast | n | eff | CI | MDE | verdict |
|---|---:|---:|---|---:|---|
| **r1 `gen` − blind** | 968 | **−0.0267** | [−0.0424, −0.0115] | 0.0216 | **LOSES** |
| **r2 `gen` − blind** | 1684 | **+0.0020** | [−0.0065, +0.0104] | 0.0124 | **UNRESOLVED** |
| r1 `gen_sham` − blind | 968 | −0.1043 | [−0.1191, −0.0887] | 0.0219 | LOSES |
| r2 `gen_sham` − blind | 1684 | −0.0243 | [−0.0346, −0.0134] | 0.0151 | LOSES |
| r2 `vacuous` − blind | 1684 | −0.0396 | [−0.0487, −0.0306] | 0.0131 | LOSES |
| r2 `randblind_s0` − blind | 1684 | −0.0313 | [−0.0424, −0.0192] | 0.0168 | LOSES |
| r2 `randblind_s1` − blind | 1684 | −0.0516 | [−0.0664, −0.0358] | 0.0219 | LOSES |
| r2 `randblind_s2` − blind | 1684 | −0.0221 | [−0.0317, −0.0112] | 0.0153 | LOSES |
| r1 `gen` − blind, ALL annotators *(specification)* | 968 | −0.0162 | [−0.0247, −0.0082] | 0.0119 | LOSES |
| r2 n=2 stratum *(not gauge-matched, D1)* | 5204 | +0.0065 | [−0.0050, +0.0183] | 0.0170 | UNRESOLVED |
| r2 n=3 stratum *(not gauge-matched, D1)* | 456 | +0.0117 | [−0.0124, +0.0358] | 0.0357 | UNRESOLVED |

## ⛔ NO WORLD CLAIMED — AND THAT IS THE FINDING

The prediction matrix has three branches and **every one presupposes `r1 BEATS`**. It does not:
under the matched estimator the prompt-specific arm **loses** to the prompt-blind reference on
release 1 (−0.0267), and the all-annotator specification agrees on sign (−0.0162). The script
refused to name a world rather than adding a branch after seeing the result. **I registered a matrix
that could not describe the outcome, which is a defect in the registration, not in the data.**

⭐ **And the reason is visible in the table.** Three prompt-blind `randblind` arms sit at −0.0221,
−0.0313 and −0.0516 from `generic` — all resolved LOSES, spanning **0.0295**, more than twice the
r2 MDE. **The "prompt-blind reference" is not a point; it is a spread wider than the effect clause ②
is asked to detect.** Clause ② is the definition's only MEASURED clause (R360: ① excludes 0, ③ is
derived, ④ excludes 0), and on release 2 its verdict depends on which blind arm is chosen as the
reference. **Scope: measured on release 2 only** — release 1's blind spread is not computed here.

## CONTROLS, AND WHAT THEY RETURNED

| control | returned | |
|---|---|---|
| OBJECT | 7 arms · 7,344 interactions · strata 2:5204 / 3:456 / 4:1684 · blind core matched · id spaces disjoint | PASS, else exit 2 |
| PLACEBO | an arm against itself, r1 **0.000000**, r2 **0.000000** | PASS |
| g=0 | blind vs a byte-identical copy of its own core, **0.000000** both | PASS |
| NEGATIVE (pairing) | permuting the pairing moves the mean by **3.4e-18 / 7.5e-19** | **a DERIVATION** — a paired mean is permutation-invariant; labelled, not reported as a null |
| NEGATIVE (target) | target permuted, 200 draws: r1 [−0.0215, +0.0221], r2 [−0.0159, +0.0161] | the real null |
| SHAM | prompt-specificity **ABSENT**, not inverted — blind vs blind, r2 **−0.0313** | see the spread finding above |
| POSITIVE | w 0.00 → UNRESOLVED both · 0.25 → +0.1167 / +0.1363 · 0.50 → +0.2099 / +0.2554 · 1.00 → +0.3313 / +0.4478, all BEATS | PASS, band computed: floor **+0.0000** < t < ceiling **+0.4478** |

## WHAT DIED

- **`cross-release | N/A — one release`** as an unqualified register row, in 21 lines across 21 rounds.
- **the premise of my own prediction matrix** — that clause ② holds for `gen` on release 1.
- **"the blind reference"** as a definite article, on release 2.

## WHAT SURVIVES

The **schema-bound** half of the wall, exactly as `score.py` words it: clause ① needs a rubric that
release 2 does not ship, and any annotator-panel quantity needs a panel it does not ship. Those are
real and are re-registered below with what each requires.

## SCOPE

population r1 968 prompts / r2 1,684 n=4 interactions · instrument pairwise sign agreement against a
single score vector, identical code both releases · baseline `core_generic.json`, the same file on
both sides · regime home judge Qwen3.5-2B-Base, k=4.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| a cross-release test of clause ① | release 2 ships **no rubric**, and ① is defined against the prompt's own rubric. **This half of the wall is real.** |
| a cross-release annotator-panel quantity | release 2 ships one score vector, not a panel |
| a cross-release test of clause ③ | provenance is shipped on release 2 and absent from release 1's sat files, so the predicate is checkable on one side only |
| a third release | a third corpus |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

Release 1's blind spread is the missing half of the spread finding: this round measured three
prompt-blind arms against `generic` on release 2 and, as computed by this round's `run.py`, zero on
release 1 — the E2 table above carries no r1 blind-vs-blind row — so "the blind reference is not a
point" is currently a one-release claim.

⚠ **And the obvious next step is underpowered, which I checked before registering it rather than
after.** Computed by enumerating every release-1 arm that has both a sat file and a core whose
per-prompt sets are identical across all 968 prompts: the answer is **exactly 2** — `generic` and `genericpool16`;
`promptecho` looks blind by name and is not (398 distinct sets over 398 prompts). **Two arms give one
difference, not a spread**, so release 1 cannot reproduce release 2's three-arm range as the data
stand. The step is therefore a RUN and not a DATA ask: score `randblind`-style blind arms on release
1 with the existing generator at k=4, at which point the same `cell()` in this round computes the
comparison. If release 1's spread is also wider than clause ②'s effect, the clause needs a *named*
reference rather than a definite article — a change to the definition's wording, not to its evidence.
