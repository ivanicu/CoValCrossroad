# R852 · what is the "free component" actually made of? — and mine was never checked

**Arc A24.** ⚠ **This round RETRACTS my own R850 and R851 downgrades.**

## ⛔ THE ARITHMETIC, RUN FIRST, AND IT INDICTS TWO OF MY ROUNDS

Under BH at q = 0.05 over 99 arms, a **pure** null yields on the order of `q·N ≈ 5` rejections.
**R850 measured 30 and R851 measured 16** on what I called a "shuffled target" and treated as a null.
**3–6× the pure-null scale.** Something systematic was surviving my shuffle, and **I called it
"noise" twice without checking.**

That is §1's own row, verbatim: *"A permutation null answers `did the pairing matter`, never `why`.
Before calling one load-bearing, **NAME THE WORLD IT EXCLUDES and build that world synthetically to
check**."* **I made it load-bearing in two consecutive rounds and never built the world.**

## ⭐ CONTROLS

| control | result |
|---|---|
| **PLACEBO** comparator vs itself | **+0.00e+00 · PASS** |
| **POSITIVE** `oracle_k4` satisfies ② on the real target | **True · PASS** |

## ⭐⭐ RESULT — world B. Three nulls, three seeds each.

| null | what it destroys / preserves | extension | seeds |
|---|---|---:|---|
| **REAL** | — | **29** of 99 | — |
| **N1 pair-shuffle** *(what I used)* | destroys which-pair-is-which; **preserves each prompt's marginal verdict mix** | **14.3** | `[16, 12, 15]` |
| **N2 cross-prompt swap** | each prompt gets **another prompt's** human ranking | **0.0** | `[0, 0, 0]` |
| **N3 uniform** — the pure null | a random ranking per prompt | **0.0** | `[0, 0, 0]` |

⭐⭐⭐ **Two independent proper nulls both return EXACTLY ZERO.** My pair-shuffle returns 14.3.

**The mechanism, now precise:** permuting *which pair is which* within a prompt leaves the prompt's
**marginal verdict mix** — how many ties, how many strict orderings — intact. An arm whose output has
a similar marginal mix to the human's matches above chance **whatever the pairing is**. **That is
FORMAT agreement, not content agreement, and it is not noise.**

## ⛔⛔⛔ WHAT THIS RETRACTS — both are mine, from the last two rounds

| claim | status |
|---|---|
| R850: *"④′'s excess is 11, not 41"* | **RETRACTED.** Against a proper null the excess is **41**. |
| R851: *"②'s extension is ~55% free; excess 13, not 29"* | **RETRACTED.** Against a proper null the excess is **29**. |
| R851: *"the two measured clauses agree in the low teens"* | **RETRACTED** — that agreement was between two artifacts of the same bad null. |
| R849: *"extension 41 of 99, excludes 58"* | **RESTORED as reported.** |

⚠ **And note the DIRECTION, because it is the rarer one.** The register records that of 7
mis-specified controls, **only 1 failed in the flattering direction.** This one failed in the
**unflattering** direction: **a bad null made me retract something true** — §3's named most-expensive
error, *"a cheap attack that appears to kill a claim."* **I ran it twice and reported both.**

## ⚠ WHAT IS NOT CLAIMED

- **N1 is not worthless** — it measures something real: **how much of an arm's A2 advantage is
  marginal-format agreement.** For clause ②, that is **14.3 of 99 arms' worth.** It is simply **not a
  null for the clause**, and I used it as one.
- **The 0.0 is not "below the q·N scale by luck"**: `q·N` bounds the expected false-discovery
  *proportion among rejections*; under a genuine null the p-values are uniform and the extra
  `CI > 0` requirement leaves almost nothing. **Two nulls, three seeds each, all zero.**
- **Construct validity untouched.**

## STRUCTURALLY IMPOSSIBLE HERE
| criterion | what it would require |
|---|---|
| construct validated | an external gold standard for corehood |
| cross-release | a second release |

⚠ **N/A with what each would require — never "planned".**
