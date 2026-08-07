# R1028 — R802 declared the `cross-release` impossibility FALSE. Its instrument measured a **file**.

**The decision this round makes safe:** how the `cross-release` register line should be worded. It
**stands** — but for a reason neither R802 nor this arc ever stated.

## ⛔ Prior art first, and it is substantial — this round starts *after* five committed audits

R291, R472, R547, R660 and R802 all audit the impossibility register; R999 audits the walls. R1027's
NEXT proposed auditing the register: **most of that is rediscovery and is not re-run.**

**R802 is the one that matters.** It found **30 distinct impossibility claims across 13 rounds, of
which 1 is FALSE** (base rate **0.0333**) — the false one being `cross-release`, on the ground that
`data/utterances.jsonl` **exists, is 68 MB, and 22+ rounds' `run.py` open it.**

## ⛔ What is left is R802's own unit

| | |
|---|---|
| **instrument unit** | one **FILE** on disk, opened by ≥18 rounds |
| **claim unit** | one **RELEASE** — an independently collected population |

**Not equal.** A second release implies more files; more files do not imply a second release. That is
§4's rule verbatim: *name the instrument's unit and the claim's unit as two separate strings and
require them to be equal.* So R802's FALSE verdict is **UNVERIFIED until the populations are
compared** — which is this round.

## Result — ⚠ **World D, which I did not pre-register: a disjoint population without criteria**

| join key | scored | other | shared | share |
|---|---:|---:|---:|---:|
| conversation id | 1,078 | 8,011 | **0** | 0.0000 |
| prompt_id vs conversation_id | 1,078 | 8,011 | **0** | 0.0000 |
| prompt **TEXT** | 1,078 | 26,673 | **0** | 0.0000 |

`utterances.jsonl`: **68,371 rows · 8,011 conversations · 27,172 interactions · 26,673 distinct
prompts.** Fields: `score`, `if_chosen`, `model_name`, … — **no rubric, no criteria.**

**So R802's FALSE verdict is wrong for its stated reason** (*file ≠ release*) **while being closer to
true than I expected**: a second, genuinely disjoint population *does* exist. **It still cannot
validate a criteria-based definition, because it has no criteria.**

## ⛔ The register's line is right and its reason is wrong — which is not the same as being right

The honest entry names what a usable second release would need: **not "another release", but "another
release *carrying a criterion vocabulary*".** R802 refuted the first and this arc kept asserting it;
**neither side stated the second, which is the requirement that actually binds.**

## ⚠⚠ My own verdict string fired wrongly on the first run

The pre-registered branches were `A` (disjoint ≥10% **and** has rubric), `C` (contained **and** no
rubric), else `B`. Overlap came back **0.0000 with no rubric**, so `A` failed on the rubric and the
code **fell through to `B` — whose text reads "a second view of one collection", which overlap 0
refutes.** That is the *verdict string is not a computation* mode: **a branch that fires by
elimination and then asserts a mechanism nobody checked.** The missing cell is added and **labelled
post hoc**, because it was not pre-registered and pretending otherwise is the worse error.

## Controls

- **POSITIVE** — the overlap instrument must separate a **constructed** disjoint split of the scored
  release: overlap **0**: **PASS**. Without it, a measured 0 means nothing.
- **PLACEBO** — the scored release against **itself**: overlap exactly **1.0000**: **PASS**.
- **NEGATIVE** — the annotation question asked **separately** from the prompt question: does the
  other file carry a criterion vocabulary at all? **No.**
- **MULTIPLICITY** — **3** join keys, all reported. A single key that missed would have manufactured
  a false disjointness.
- **NOISE FLOOR / SEEDS** — **N/A**, exact set operations. Stated rather than omitted.

## ⭐ Independent confirmation of R1027

`responses per prompt = [4]`, read from `comparisons.jsonl` directly rather than inferred from a cell
count. **Different route, same value** — R1027's `replies = 4` holds.

## What this round cannot say

Whether a genuinely independent second **values-annotation** release exists **anywhere**. It speaks
only about the two files in `data/`. **What that would require:** a release index beyond this
repository. **N/A, not planned.**

`run.py` · `results/second_file_or_second_release.json`
