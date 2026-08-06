# R243 — the two arms disagree on sign, and the framing is the finding

**Arc E05·A19.** `realstat` §2.5, the rule fixed before either agent launched: *"disagree on sign →
**your framing is the finding**. Do not adjudicate by picking the design you like; find the
assumption they differ on and test THAT."*

| arm | `Q` | result |
|---|---|---|
| **R231** (mine, full context) | reproduce Full's **exact** weak ordering | core 0.3864 vs random floor 0.3836 — **inside**. *"Indistinguishable from random."* |
| **R235** (blind, seed 29) | Kendall **τ_b** against Full's ordering | core 0.663 vs random 0.416, **η = +0.982 [0.917, 1.046]**. *"As good as an oracle at its own budget."* |

Same object, same release, same judge family, **opposite practical verdicts.**

## Sweeping the assumption I named

| `Q` = "a match means…" | core | floor | core − floor |
|---|---:|---:|---:|
| **≥ 6 of 6 pairs** (R231's Q) | 0.3864 | 0.3891 | **−0.0027** |
| ≥ 5 of 6 | 0.7603 | 0.7331 | **+0.0273** |
| ≥ 4 of 6 | 0.8957 | 0.8854 | +0.0102 |
| ≥ 3 of 6 | 0.9607 | 0.9617 | −0.0010 |
| ≥ 2 of 6 | 0.9897 | 0.9857 | +0.0039 |
| ≥ 1 of 6 | 1.0000 | 0.9968 | +0.0032 |
| mean pairwise (graded, R235's kind) | 0.8321 | 0.8253 | **+0.0068** |

**Controls:** positive — `t=6` reproduces R231 at **0.3864** exactly. Negative — `t=0` returns
**1.0000 / 1.0000**, a derivation, confirming the harness invents no difference.

**The sign flips between 6-of-6 and 5-of-6.** Requiring the *entire* class is the only setting at
which the core is not above its floor.

## ⚠ But this is too clean, and B's own specification curve says why

**My graded endpoint gives `+0.0068`. B's gives `Δ = +0.2466`.** Granularity cannot explain a
36× magnitude difference. **A second assumption differs, and B found it independently:**

> *"Every failing cell is a `signed`-baseline cell… median η uniform/world **+0.534** → signed/world
> **+0.110**. 72 of 286 cells have a CI containing 0 or Δ<0 and **all** of them use signed
> weighting; **zero** uniform cells fail."*

My floor gives the random subset the **full rubric's signed mean weights**. B's headline floor gives
it **uniform +1**, matched to the core's own information state — a **weaker** opponent, because the
core cannot express signs either.

## What R243 actually establishes

- **The sign disagreement at exact-match is Q-granularity.** Confirmed, with controls.
- **The magnitude disagreement is baseline format** — whether the random arm is granted the signs
  the core's format cannot carry. **Not granularity.**
- **Two assumptions differ, not one**, and I would have reported one had B not published its own
  signed/uniform split. **The blind arm caught a specification axis my arm never swept.**

## What this does *not* close

**Design A has not returned.** Closing a three-arm triple-blind on two arms is the thing the
protocol exists to prevent. This round tests the *assumption*, as the rule requires; the *verdict*
on the formulation waits for A.

## The sentence that can no longer be written

*"The official core is indistinguishable from random selection."* It is, **at exact-class match
against a signed baseline.** At five-of-six pairs, or against a format-matched baseline, it is
clearly above — and my arm swept neither axis.
