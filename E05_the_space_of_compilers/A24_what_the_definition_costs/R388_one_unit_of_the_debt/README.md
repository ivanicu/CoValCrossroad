# R388 — one unit of the debt, paid and priced: 21.3 s of machine time, 7 numbers verified

**The decision this makes safe:** *is paying the debt a compute project or a writing one?*
**A writing one.** The machine time is 21.3 s; the cost is attention.

## Result — `W_CHEAP`. Two controls PASS. **Product shipped.** **No GPU spent.**

Eight rounds (R380–R387) established that the findings are missing, that generation cannot write
them, and that the code still runs. **That is a complete answer to *can this be done* and no answer
to *is it worth doing*.**

> **"If honesty were the objective function, shutting me off would be its maximum."** Eight rounds of
> diagnosis with no paragraph written is an audit presented as a product. **So this round writes
> one.**

## What was produced

**Two rows in the root README's `What was established` table**, under a heading marking them as
**backfill** — a row written months after its round is a different object from one written beside it,
and blending them would be the drift those rounds were about.

`R21_donor_distance`'s finding is now stated where the campaign's own documents say findings live:
the *"nearest-topic"* donor is **nearly a same-question restatement** — cosine **0.8804** vs random
**0.7495**, covering **91.4%** of the distance from random to a paraphrase, at the **97.85th**
percentile of all pairs — **so its failure to transfer is a strong result, not a weak one.**

## ⛔ The real risk is not cost, it is fabrication

Nothing about a backfilled row distinguishes a **copied** number from a **remembered** one. So every
number was checked against a **fresh run** — not the committed artifact, which R386 measured carries
**9%**.

| number | 0.1432 | 0.7495 | 0.8804 | 0.8927 | 300 | 91.4 | 97.85 |
|---|---|---|---|---|---|---|---|
| in the fresh run | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**And "all numbers verified" would merely restate "I copied carefully"** — so a number **absent** from
the run is planted and must be caught. It is.

## ⭐ The verification is now a permanent gate

`assurance/backfilled_findings_are_rederivable.py` — every backfilled row's numbers must re-derive
from a fresh run of the round it cites. **Registered in the suite: 26/26.**

⛔ **Its own positive control was a check that cannot fail**, and I caught it before committing: v1
computed `[n for n in [FAKE] if n not in set()]` and asked whether that was non-empty — **true by
construction**. The plant now goes through the *same comparison that rules*.

⛔ **And the suite corrected my registration.** I registered it `want 1`, reasoning that hiding the
rounds leaves nothing to re-derive. It returned **0** and was right: the gate re-runs from a **git
worktree at HEAD**, so emptying the working tree never reaches its subjects. That is deliberate — a
backfilled number should re-derive from **committed** code — but it means the attack cannot test it,
and saying so is the honest registration. Its empty-population behaviour is verified **separately**:
heading absent → **exit 2**.

## Controls

| | returned |
|---|---|
| **FABRICATION (+)** | a planted `0.7331`, absent from the run, is flagged |
| **FABRICATION (−)** | the real rows verify — both directions, because a verifier flagging everything would catch the plant and mean nothing |
| **FRESH RUN** | in an isolated worktree; R21 writes to its own `results/`, so a live run would rewrite a committed artifact |
| reproducibility | two runs identical **in every field except `run_seconds`** (21.3 → 21.5) — wall-clock is the measurement and is not deterministic, which is stated rather than hidden by rounding |

## Register

| criterion | status |
|---|---|
| **an estimate of the remaining 237** | **N/A — n = 1.** R387 measured 3 of 12 rounds exceeding 90 s, so the spread is wide. **Multiplying 21.3 s by 237 would be the arithmetic trap wearing a project plan** |
| **whether the WORDS are right** | **N/A** — numbers are checkable; the sentence around them is a judgement I may not make alone. The gate's proxy ledger says so in its own output |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"the 243 is a debt only writing can pay"* — as though that settled anything.

**One unit is paid. It cost 21.3 s of compute and the rest was reading. The debt is a writing project:
the harder kind to pipeline, and the easier kind to start.**

Artifact: `results/r388_unit_cost.json`, source-stamped.
