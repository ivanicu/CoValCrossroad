# R1041 — a wall that will **fall** is not distinguishable, in committed text, from one that stands

**The decision this round makes safe:** what to do with the eleven `IMPOSSIBLE` lines still standing.
**Not triage them** — nothing in the text predicts which fall, so any ordering is a **guess**, and the
remedy is a declared field **going forward only**.

## ⛔ R1031 is the precedent: ask before building

There I built a prior-art gate, measured recall **0 of 4** real cases, and **deliberately did not
wire it**. R1040's NEXT proposed another gate, so the prior question is whether the thing it would
flag is detectable at all.

## ⛔ And one answer is forced, which narrows the question

A gate demanding a **declared field** would flag **all 16** blocks — the field exists in none of them
yet. **Zero retroactive power, by construction.** That is R1029's *store the field, don't recover it*
restated. So the only open question: **does a feature already present separate the groups?**

## Result — ⭐ **World B. No retroactive signal.**

| feature | fell+ | stand+ | p |
|---|---:|---:|---:|
| says outside/external | 4 | 3 | **0.0769** |
| names a specific round | 2 | 3 | 0.5165 |
| says gold standard | 1 | 1 | 0.5417 |
| mentions the release itself | 2 | 4 | 0.6538 |
| names a cost in calls | 1 | 3 | 0.8187 |
| says construct validity | 1 | 3 | 0.8187 |
| says needs/would require | 4 | 11 | 1.0000 |
| names a second release | 0 | 1 | 1.0000 |

**Best p = 0.0769** against a **Bonferroni threshold of 0.0056** (a family of one-off tests, so
Bonferroni, not BH ranks) and a **label permutation of 0.2637** over 200 relabellings.

**So fallen and standing blocks are structurally indistinguishable.** The remedy is a **declared field
going forward only** — and R1040's *"attack the highest-exposure first"* is an **ordering guess that
should be labelled as one**, not dressed as triage.

## Controls

- **POSITIVE** — a feature **known** to be there must be found: `GFLOP` isolates exactly one block:
  **PASS**. Without it, a null means nothing.
- **PLACEBO** — the label as its own feature must reach the **attainable floor**: **2.289e−04**:
  **PASS**.
  ⚠ **My first version demanded p < 1e−9 — below what n=16 can return.** That is §4's *"control that
  cannot PASS"*, mirrored: a threshold outside the band the design can produce. The criterion is now
  **computed**, not typed.
- **NEGATIVE** — 200 random relabellings of the same 16: the best feature reaches p ≤ 0.0769 in
  **52/200**, permutation p **0.2637**. The observed separation is ordinary under a random label.
- **MULTIPLICITY** — every feature reported, threshold over the **whole** grid.

## ⛔ The null is a resolution statement, not an acquittal

With **16** blocks and **5** positives the **smallest attainable p is 0.0002**, so a feature would
have to separate **almost perfectly** to clear correction. **This design cannot detect a weak signal,
and says so** rather than reporting "no difference".

## What this does not ask

Whether an **unfalsified line is true**. This asks only whether *falling* is predictable from the
text. Testing the standing lines is **one round each** — exactly what this round tried to avoid, and
what R1039 already named.

`run.py` · `results/fallen_wall_signal.json`
