# R1021 · the core/twin split under `A1·consensus` is the imputation, not the target

**THE DECISION THIS MAKES SAFE.** Whether R1020's headline — *the definition admits the core's twins
and excludes the core* — survives removing every imputed value. **It does not.** The target effect on
the core is real; the **contrast with the twins is an artifact.**

---

## The derivation, labelled before the measurement

R1005 measured the twins' outputs identical to the core's at agreement **exactly 1.000** on the
prompts they share. So:

> On those 200 prompts the twins' class vectors **are** the core's. Any statistic computed there must
> be **identical** for all three. **It could not come out otherwise.**

The check confirms bookkeeping (max |Δ| = **0.0** for both twins) and **is not evidence**.

## The measurement

| regime | arm | comparator | Δ | lo | hi | admitted |
|---|---|---|---:|---:|---:|---|
| **200 real** | `coval_core` | `generic` | +0.0450 | −0.0100 | +0.1000 | **No** |
| **200 real** | both twins | `generic` | +0.0450 | −0.0100 | +0.1000 | **No** |
| **200 real** | all three | `genericpool16` | +0.0400 | −0.0150 | +0.0950 | **No** |
| 968 imputed | `coval_core` | `genericpool16` | +0.0258 | **+0.0000** | +0.0527 | No |
| 968 imputed | both twins | `generic` | +0.0238 | **+0.0024** | +0.0450 | **Yes** |
| 968 imputed | both twins | `genericpool16` | +0.0290 | **+0.0066** | +0.0502 | **Yes** |

```
admitted on 200 REAL prompts    : []            ← core and twins together
admitted on 968 with imputation : twins only
```

⭐ **At 968 the twins clear only because the loader fills their missing 768 values with the twins' own
mean** — mean |Δ| from the core **0.2057**. On real data the three are inseparable, because they are
the same object.

## What this does to R1020

**Its wording is replaced, not annotated beside.**

- ❌ *"the definition admits the released core's TWINS and excludes the core itself"* — **withdrawn**
- ✅ **under `A1·consensus` the released core is not admitted** (`generic` lo −0.0041,
  `genericpool16` lo +0.0000 — neither clears)

**The target effect on the core stands. The contrast that made it vivid does not.**

## Controls

| control | result |
|---|---|
| **POSITIVE (the derivation)** | core vs each twin on 200 shared prompts: max \|Δ\| **0.0** |
| **NEGATIVE** | at 968 **with** imputation they must differ: mean \|Δ\| **0.2057** — the phenomenon R1020 found |
| **PLACEBO** | a full-coverage arm against itself on the same 200: **0.0e+00** |
| **NOISE FLOOR** | the 200-prompt intervals, printed — wider by construction (n = 200 vs 968) |

⚠ **"Excluded together" at 200 is not a tie the design could not resolve** — the intervals are shown,
and all three sit at the same Δ with the same bounds because they are the same vectors.

## ⚠ Impossible here

**What the twins would score on the other 768 prompts.** They were never run there. **That is the
defect, not a gap in this round** — and it is why the 200-prompt restriction is the only comparison in
which no value is invented for anyone.

## Alternatives considered

**Leave R1020's wording and add this as a caveat.** Refused, and the kill was pre-registered against
it: the earlier sentence is *materially stronger* than what the evidence supports, and a caveat beside
a too-strong claim leaves the too-strong claim quotable.

**Report the 200-prompt exclusion as confirming the target effect.** Refused — at 200 the core is
excluded, but so is everything else compared here, and the interval is wide. The core's exclusion is
established at **968** against full-coverage comparators; the 200-prompt run establishes only that the
**twin contrast** is not real.
