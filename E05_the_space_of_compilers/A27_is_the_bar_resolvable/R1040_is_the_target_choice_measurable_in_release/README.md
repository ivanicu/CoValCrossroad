# R1040 — R1023's wall falls: the target **is** selectable from inside the release

**The decision this round makes safe:** which target the definition's figures should be read under.
**A2** — its arm ordering is **6.9×** more reproducible across independent annotator panels.

## What was attacked, and why this one

R1039 measured that this arc's own `IMPOSSIBLE` lines fell at **4 of 16**, all sharing **one shape**:
*"the answer needs something outside the release"*, answered by an object already inside it. **R1023's
line is the longest-exposed line of that exact shape** — *"whether A2 or A1·consensus is the RIGHT
target needs an external gold standard"* — and had never been attacked.

## ⛔ The obvious in-release criterion is circular, and refusing it is the design

*"Which target better predicts held-out annotators"* **IS A2 by construction.** Using it would have
manufactured a separation. **It was refused, not overlooked.**

⭐ **The neutral criterion is reproducibility**, defined identically for both targets and restating
neither: *a target whose induced arm ordering flips when you resample the annotator panel is
measuring annotator idiosyncrasy, not the object.*

## Result — ⭐ **World A**

| target | median ρ | sd | min | max |
|---|---:|---:|---:|---:|
| **A2** | **0.9973** | 0.0007 | 0.9965 | 0.9988 |
| A1·consensus | 0.9664 | 0.0063 | 0.9545 | 0.9796 |

**Gap 0.0309 against a pooled across-split SD of 0.0045 — 6.9×.**

**So the target IS selectable from inside the release, and R1023's wall falls in the same shape as the
other four: the answer was the release's own annotator panel.**

## Controls

- **POSITIVE** — within-prompt annotator agreement reproduces R295's committed **0.5520**: mine
  **0.5556** (different prompt filter, so exact equality isn't expected; band 0.02): **PASS**.
- **NEGATIVE** — permuting annotator identity **across prompts** must collapse both: A2 0.9973 →
  **0.9267**, A1c 0.9664 → **0.3439**: **PASS**. The statistic is reading the panel.
- **PLACEBO** — a half against **itself** must give ρ exactly 1: **(1.0, 1.0)**: **PASS**.
- **NOISE FLOOR** — across-split SD over **25** splits, printed as the resolution the gap is judged
  against.
- **MULTIPLICITY** — the full distribution (median, sd, min, max) for both targets, not medians alone.

⚠ Note the negative control's asymmetry is itself informative: under a destroyed panel A1c collapses
to **0.34** while A2 holds at **0.93**. A2's ordering survives because it averages over annotators;
A1·consensus depends on a consensus that shuffling destroys.

## What this settles, and what it does not

- ⭐ **R1023's line is falsified** — the fifth of this session's own impossibility claims to fall, and
  the fifth of the same shape. R1039's habit is now **5 of 16**.
- ⚠ **Reproducibility is necessary, not sufficient** — the same limit R1036 hit for q. A stable target
  can still be the wrong one; that needs a **statement of intent** the dataset card does not carry.
  **N/A, stated not planned.**
- ⭐ It is also **consistent with R1019's committed scoping**: every extension figure in this arc is
  A2's answer. This is the first evidence that the choice was **right**, not merely inherited.

`run.py` · `results/target_choice_in_release.json`
