# R850 · is ④′'s extension SELECTIVE, or merely a small reference class?

**Arc A24 — what the definition costs.** ⚠ **This round downgrades R849, which is mine, from one
round ago.**

## ⛔ THE ARITHMETIC TRAP, RUN FIRST

The bar is `max over R`, so enlarging R can only raise it, so every margin is non-increasing and
**the extension is monotonically NON-INCREASING in |R| by construction.** *"Does 41 shrink?"* is
`1+1=2`. **Not asked.** *(Third time this arc the obvious question was forced — 1364, 1366, here.)*
The non-forced questions: **how fast, and does it collapse toward 1 or stabilise?**

## ⛔⛔ TWO DEFECTS OF MY OWN, CAUGHT BEFORE ANY NUMBER WAS REPORTED

**① Population collapse.** The first version intersected *every* arm's prompt coverage, cutting
**1,078 → 87** and silently changing the estimand out from under a comparison with R849 (which uses
each arm's **own** set, ≥200). **The print `"prompts common to all arms: 87"` is what exposed it** —
an instrument that reports its own population is worth more than one that reports only its result.
Fixed: per-arm prompts, NaN-masked bootstrap. ⭐ **After the fix, R849's cell reproduces exactly:
|R| = 394 → 41.0, through different code.**

**② The verdict string was not a computation.** It read `good[0]` and `good[-1]`; **only one size
passes its controls**, so both were 394 and it printed *"does not fall"* from a Δ over a **single
point** — §4's named failure, committed here. Fixed: the curve's **shape** is reported as a property
of the **procedure**; the **clause's** status only where its controls hold.

## ⭐⭐ THE CURVE — 99 arms, per-arm prompts (median 968), bar always selected on the ODD half

| \|R\| | extension (real) | noise | excess | controls |
|---:|---:|---:|---:|---|
| 5 | 63.8 | 55.2 | 8.5 | pos PASS · **neg FAIL** |
| 10 | 64.2 | 47.9 | 16.4 | pos PASS · **neg FAIL** |
| 20 | 59.9 | 38.0 | 21.9 | pos PASS · **neg FAIL** |
| **30** *(R436's committed family)* | 57.1 | 38.2 | 18.9 | pos PASS · **neg FAIL** |
| 50 | 48.8 | 30.8 | 18.0 | pos PASS · **neg FAIL** |
| 100 | 47.0 | 30.4 | 16.6 | pos PASS · **neg FAIL** |
| 200 | 43.8 | 30.8 | 13.0 | pos PASS · **neg FAIL** |
| **394** | **41.0** | **30.0** | **11.0** | **pos PASS · neg PASS** |

## ⛔⛔⛔ THE TWO FINDINGS, AND BOTH CUT AGAINST R849

**① The negative control passes at ONE size only.** `random_k4_s0` **satisfies ④′ at every |R| ≤
200** — **including 30, which is R436's committed family size.** So the clause rejects a random
baseline only when R is essentially the whole family. **④′'s selectivity is contingent on R being
large, and the original ④'s family is far too small to have it.**

**② The noise arm says most of the extension is free.** At |R| = 394, **30 of 99 arms satisfy ④′
against a SHUFFLED target.** The excess over what the procedure admits for free is **11, not 41.**
⚠ **R849 reported the bare extension and ran no noise arm.** Its *"excludes 58 admissible objects"*
stands as arithmetic, but *"does definitional work"* is now **quantified at 11 arms of excess, not
41.**

## ⭐ WORLD B, at the one admissible size

The extension falls **63.8 → 41.0** across the swept range and **stabilises well above 1** — so it is
**not** the *describes-the-instance* failure arriving in my own repair. ⚠ **But the fall's direction
is forced**; only the rate and the level are measurements, and **the level that matters is the noise
excess, 11.**

## ⚠ WHAT IS NOT CLAIMED

- **No trend is fitted across the sizes whose negative control fails** — that would be a trend in how
  often a random arm is admitted, not in the clause.
- The noise extension of 30 is **not** an error rate; it is what this **procedure** (bar selection +
  BH + interval) admits on a target with the pairing destroyed.
- **Construct validity untouched**; no external gold standard for corehood exists.

## STRUCTURALLY IMPOSSIBLE HERE
| criterion | what it would require |
|---|---|
| construct validated | an external gold standard for corehood |
| cross-release | a second release |
| causally identified | an intervention on the compiler |

⚠ **N/A with what each would require — never "planned".**
