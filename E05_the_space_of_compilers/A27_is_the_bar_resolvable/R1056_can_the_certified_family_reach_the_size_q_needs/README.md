# R1056 — can the certified family reach the size `q` needs? ⛔ **No. `q` is permanently inert in this release: the family is 2 at every defensible threshold and jumps to 95 at the next.**

**The decision this round makes safe:** whether to keep `q` in the clause. **It cannot be exercised
here at any threshold**, so the clause either adopts an explicit relaxation that does not exist, or
drops `q`.

## The certification curve

R1055 established by arithmetic that `q` first distinguishes anything at **|family| = 10**.

| rule | family | share | reaches q@10 |
|---|---:|---:|---|
| `n_distinct ≤ 1` (= the committed `fixed`) | **2** | 0.021 | No |
| `n_distinct ≤ 2 … ≤ 250` | **2** | 0.021 | No |
| `n_distinct ≤ 500` | **4** | 0.042 | No |
| `n_distinct ≤ 1000` | **95** | **1.000** | Yes — but it is *everything* |
| `modal_share ≥ 1.0 … ≥ 0.25` | **2** | 0.021 | No |

⭐ **The distribution is extreme, not merely bimodal.** Two arms use a single selection across all
prompts; essentially every other arm uses a **near-unique selection per prompt** (968 prompts, 500–968
distinct). Relaxing "identical on every prompt" all the way to "at most 250 distinct selections"
admits **nobody new**. There is no middle to stand on.

## ⛔ The knob that looked right was the wrong one, and checking is what saved the round

R918 stores two per-arm properties **one field name apart**:

| field | question | count |
|---|---|---:|
| `fixed` | is the selection **the same across prompts**? | **2** |
| `exact` | is the selection **a subset of the rubric**? | **86 at 1.0** |

**They are not nested.** Every threshold on `exact` from 0.01 to 1.0 returns the same 86 arms.
⭐ **Sweeping `exact` would have manufactured a family of 86 and declared `q` testable.** The eighth
unit confusion this window — and the first caught *before* any number was computed, by reading both
definitions out of R918's source rather than assuming the fields were a ladder.

## Controls

- **POSITIVE** — the strictest cell must equal R918's committed `fixed` set: **True** (`generic`,
  `genericpool16`). If the endpoint disagreed with the committed typing, the loader would be reading
  something else.
- **NEGATIVE** — the most permissive cell must contain every typed arm: **True** (95 of 95).
- **PLACEBO** — arms with no selection file are **counted as untypable and named**, never silently
  dropped.
- **MULTIPLICITY** — the whole curve is reported, both rules, including the cells that fail.

## What this round cannot say

**Reaching 10 is necessary for `q` to bite and never sufficient for the family to be legitimate.** An
arm using few-but-more-than-one selections still conditions on the prompt, just coarsely — whether
that counts as prompt-blind is a definitional choice, not a measurement.

## IMPOSSIBLE here

- **whether a coarsely-conditioned arm is prompt-blind in the sense the clause intends** —
  **SETTLES: OUT-OF-RELEASE** for the concept; **IN-RELEASE** for its consequences, since any
  candidate family can be run through the operator.

`run.py` · `results/certification_curve.json`
