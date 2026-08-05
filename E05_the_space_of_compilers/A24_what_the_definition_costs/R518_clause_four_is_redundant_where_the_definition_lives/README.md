# R518 · ④ is redundant at the home judge — measured, not unverified

**Decision this makes safe:** whether ④ does any work at the judge the definition names.

**Estimand:** among arms passing ②, the margin over ④'s bar **in units of each arm's own MDE** —
which is what separates "④ excludes nobody" as a *measurement* from "④ excludes nobody" as a
*resolution limit*. **Population:** the 41 arms carrying both a ② verdict (R294) and a ④ score
(R436). **Instrument:** A2 vs the best criterion-free rule. **Baseline:** `min_ttr` at 0.4512.
**Regime:** home judge J, 968 prompts.

## ⛔ First: R517's wall, tested before anything else

R517 closed with *"settling ④ needs a scoring run rather than a reanalysis."* **False.**
**41 arms already carry both verdicts on disk, and ②'s marginal there is 9, not 0.** The join was
one merge away.

## Result — WORLD B

| arm (passes ②) | d over ④'s bar | MDE | margin |
|---|---|---|---|
| `topw_k8` | +0.1098 | 0.0224 | **4.90×** |
| `topw_k3` | +0.1143 | 0.0225 | 5.07× |
| `topw_k4` | +0.1150 | 0.0227 | 5.08× |
| `coval_core` | +0.1186 | 0.0230 | 5.16× |
| `topw_k6` | +0.1179 | 0.0221 | 5.33× |
| `indep_k4_fit1` | +0.1482 | 0.0212 | 6.99× |
| `oracle_k4_fit1` | +0.1701 | 0.0214 | 7.94× |
| `greedy_k4_fit1` | +0.1674 | 0.0211 | 7.95× |
| `oracle_k4` | +0.1824 | 0.0211 | **8.65×** |

**Every ②-passer clears ④'s bar by 4.90–8.65 MDEs**, against a pre-registered kill at 2.00×.
**The zero is a measurement, not a resolution limit: ④ cannot exclude a ②-passer at home.**

## Controls
- **Positive (on the wall, run first)** — join non-empty and ②'s marginal non-degenerate:
  **41 arms, 9 passing ②.** The wall is false.
- **Negative** — the scale must be able to place an arm below ④'s bar: **`promptecho_sham`,
  d = −0.0106.** Two-sided. ⚠ And it is **under-resolved** (|d|/MDE = 0.29) **and fails ②**, so it
  could not populate the informative cell even if resolved.

## What this corrects

**R517 called ④ UNVERIFIED in both populations. That is right for the second release and wrong for
home.** At home ②'s marginal is 9, the join exists, and the margins are 5–9 MDEs.

⭐⭐⭐ **④ is REDUNDANT where the definition lives** — the same status as ①, reached by a different
route: ① because its bar sits below ②'s, ④ because its bar sits so far below that only arms ②
already rejects come near it.

⚠ **On the second release ④ remains genuinely unidentified** (② admits 0 of 7, R434). Restated, not
quietly dropped.

**The reusable lesson: a false UNVERIFIED manufactures work.** A false acquittal is permanent
because nobody re-examines a cleared claim; a false *unverified* is expensive because everybody
re-runs it. R517's over-caution invented a scoring run that was never needed.
