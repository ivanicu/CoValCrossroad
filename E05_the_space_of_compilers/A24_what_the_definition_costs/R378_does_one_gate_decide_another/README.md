# R378 — an intervention refuted my hypothesis, and the placebo was a single newline

**The decision this makes safe:** *are the ten red gates a dependency graph whose repair order
matters?* **Not shown to be one.** R377's hypothesis is **refuted by intervention**.

## Result — `W_ANY_EDIT`. Four controls PASS. Two runs byte-identical from a committed baseline. **No GPU spent.**

R377 proposed that `attack_every_check`'s state variable was whether
`every_round_reaches_the_readme` passes — it is one of the six checks the subject plants into, and
*"a plant into an already-failing check cannot demonstrate anything"*. That was labelled `[HYPOTHESIS]`
and untested. This is the controlled version, and it is an **intervention**, not an observation.

| cell | README | `every_round_reaches_the_readme` | `attack_every_check` × 3 |
|---|---|---|---|
| **A · BASE** | as committed | exit **0** | **[1, 1, 1]** |
| **B · KNOCKOUT** | R378's link line removed | exit **1** | **[2, 2, 2]** |
| **C · PLACEBO** | **one appended newline** | exit **0** | **[2, 2, 2]** |

> **The placebo moved it exactly as far as the knockout did.**

## ⛔ Without the placebo I would have published a false structural claim

Knockout alone reads cleanly as *"one gate's verdict decides another's"* — and that claim would have
made the ten red gates a **dependency graph with a mandatory repair order**, which is a statement
about how all remaining work must be scheduled.

**It is false.** The dependence is on the **file**, not on the other gate's verdict. A single
trailing newline — which changes no gate's verdict, and is asserted to change none — reproduces the
whole effect.

**This is the cheapest control in the design and the only one that mattered.**

## Controls

| | returned |
|---|---|
| **KNOCKOUT (+)** | `every_round_reaches_the_readme` **0 → 1**. The intervention demonstrably happened — otherwise the round is an examined-nothing |
| **PLACEBO EDIT** ⭐ | README sha `22fb32ee…` → `4f77c1cc…` — **really edited.** A no-op placebo is the *plant-invalid* failure wearing a control's clothes, and this subject prints `PLANT INVALID` for two of its own six |
| **PLACEBO NULL** ⭐ | the coupled gate stays at **0** in C. A placebo that moves the gate is a second knockout, not a null |
| **RESTORE** | README byte-identical to the committed version and the tree clean, after **every** cell |
| reproducibility | two runs **byte-identical** (`17962a0af4ef`) |

## ⛔ The round contaminated its own baseline, and its control caught it

First run: baseline green, verdict `W-ANY-EDIT`. **Second run: `UNVERIFIED`** — because R378's own
artifact had made R378 a completed round mentioned in no README, so the baseline gate went red
underneath the experiment.

**The subject exits reproduced exactly** (`[1,1,1] / [2,2,2] / [2,2,2]`); **the baseline did not.**
The KNOCKOUT control did precisely its job: it refused to certify an intervention whose starting
state had moved.

> **A round whose artifact joins the corpus its own gates read cannot re-run itself into the same
> baseline.** That is R376's scaffolding lesson at a third level — and the fix is ordering: the
> round's README row is committed *first*, so the baseline is a committed state and the knockout
> target becomes R378's own link line.

That is also why this round is **two commits**: it restores README with `git checkout`, so an
uncommitted README would be destroyed by its own restore. Design and measurement are genuinely two
actions here, not one split for convenience.

## Register

| criterion | status |
|---|---|
| **the other 44 pairs** | **N/A** — ten red gates admit **45** unordered pairs; this measured the one R377 named. Nothing here says the others are coupled, and nothing says they are not |
| **the mechanism inside the subject** | **N/A** — this establishes what it responds to, not how |
| **interventionally validated** | ⭐ **MET, for this claim only** — the repository is settable, which almost nothing else in this campaign has been |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"if a gate's verdict depends on another gate's verdict, the ten reds are not ten independent
> problems and fixing them in the wrong order will make some flip back."*

**The dependence is on README's bytes, not on a gate's verdict. The conditional was never satisfied,
and I had already written its consequence into a NEXT block as though it would be.**

Artifact: `results/r378_intervention.json`, source-stamped.
