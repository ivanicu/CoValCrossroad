# R508 · Selection position is a PARTIAL provenance surrogate — every label-optimiser is caught, every miss is rule-based

**Decision this makes safe:** whether clause ③ can be replaced by a checkable clause. **It cannot** —
but the failure is now localised, which R501's could not be.

## Why this was not available before R503

R501 asked the same question and failed its own positive control: per-prompt A2 dispersion could not
place `oracle_k4` outside the middle of the pack. **R503 then measured that both sides of ③ draw
100% of their criteria verbatim from the same rubric pool.** If the pool is shared and the text is
identical, the only thing that can differ is **which items are picked** — which moves the search from
the criteria to the **selection**.

## The census

| ③-excluded arm | mean normalised position | verdict |
|---|---|---|
| `oracle_k4`, `oracle_k4_fit1`, `greedy_k4_fit1`, `indep_k4_fit1` | ≈ **0.28–0.29** | **SEPARATE**, and their rule is **not** stated in terms of position |
| `topw_k4`, `topw_k2`, `topabs_k4` | 0.54–0.59 | separate — but **position-defined, so a derivation** |
| `topw_k8`, `topwvar_k4` | **0.505**, **0.509** | ⛔ **MISSED — inside the null band** |
| `gen`, `generic`, `genericpool16` | — | **N/A**: 0% rubric overlap *(R503)*, reported as N/A not as a number |

**Controls.** **POSITIVE:** `oracle_k4` separates — the case R501's instrument could not see.
**NEGATIVE:** the random arms land at **0.5012 / 0.5039 / 0.5071**, spread **0.0059** — uniform
selectors sitting exactly where uniform selection predicts, which validates the position index and
was not designed as a control so much as discovered to be one.

⛔ **The arithmetic trap was named before the run and it bit:** arms whose rule is *stated in terms of
the rubric's ordering* must show a position effect. Their separation is **forced** and counts for
nothing; the round is judged on the four whose rule is not.

⚠ **`promptecho` contributes two criteria total** — a separation verdict on it would be an order
statistic of a 2-sample. Reported **UNDERPOWERED and not counted**.

## Verdict

**The pre-registered kill fired: ③ is NOT replaceable.** A surrogate that misses a **known** reader
cannot certify an **unknown** one, and two known readers sit inside the null band.

⭐⭐⭐ **But the shape of the failure is the finding.** Every reader that **optimises against the
labels** is caught. Every miss is **rule-based** selection. **So label-reading does leave a trace the
artifact carries — what escapes is rule-following, not optimisation.** That is a far sharper statement
than *"no behavioural surrogate exists"*, and it is what R501 could not reach.

## What it does to the fork

The fork survives — ③ still needs the producer. But **reading B's cost is smaller than stated**: a
third party holding the criterion set *and the prompt's rubric* can detect the strongest form of
label-reading, and only rule-based selection requires attestation.

## Bound

Whether `core_full.json`'s list order encodes quality is **not established here**. Position is used
as an **opaque index**. If the order were arbitrary the random arms would still sit at 0.5 and the
readers would not separate — so the design degrades to a null, never to a false positive.
