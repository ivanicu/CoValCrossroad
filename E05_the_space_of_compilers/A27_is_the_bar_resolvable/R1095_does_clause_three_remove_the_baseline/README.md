# R1095 — neither reading of ③ removes the generic baselines. The choice decides only the **instance**.

**The decision this round makes safe:** whether choosing between ③'s two readings can make the
definition distinguish a core from a generic rubric. **It cannot.** Both readings retain `generic`
and `genericpool16` — the objects a core is required to beat.

## ⛔ First, what would have been bookkeeping

R1090's `always` block **is** the ②′-admitted set, so *"how many arms does ③ remove that ②′ admits"*
is the size of the exclusion list — **19 and 22, already in R1094's artifact.** Re-reporting those
would be a derivation dressed as a finding. **The measurement is which arms SURVIVE.**

## The two extensions

| reading | survive | members |
|---|---:|---|
| **leakage** | **16** | the 3 cores · `gen` `generic` `generic_reprov` `genericpool16` · 9 × `topw_k*` |
| **authorship** | **13** | the same, **minus the 3 cores** |

**They differ on exactly `coval_core`, `coval_core_2bA`, `coval_core_2bB` — and on nothing else.**

⭐ **So the choice between readings decides whether the definition admits its own INSTANCE, and
neither choice removes the objects a core must beat.** `generic` and `genericpool16` are present
under both. **The separating work would have to come from the comparator family, not from ③.**

⚠ **And this is not automatic.** The SHAM prices it: a **random** exclusion of the same size spares
both released comparators only **20.1%** (leakage-sized) and **13.2%** (authorship-sized) of the
time. Their survival under ③ is therefore informative, not a consequence of ③ removing a minority.

## ⚠ Scope — the comparator family here is the synthetic one

R1090's block was built over the **15 universally-available blind subsets**, not the released
certified family of **2**. Under the released family an arm is compared against `generic` itself,
which `generic` cannot beat. **Every statement here is scoped to the blind-subset family** — and
that scope is why the result is as much about the *family choice* (R1089's certifier freedom) as
about ③.

## Controls — 5, all green

| control | result |
|---|---|
| POSITIVE `oracle_k4` — the definition's own ③ control — is **absent** from both extensions | PASS |
| g=0 with ③ disabled the extension is the whole 35-arm block | PASS |
| NEGATIVE the two extensions **differ**, by exactly R1094's disagreement set, recomputed here | PASS |
| PLACEBO each extension against itself is identical | PASS |
| SHAM the chance rate is **computed**, so survival is priced rather than assumed | PASS |

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| the same question under the **released** certified family | **N/A** | that family has 2 members and `generic` is one of them — an arm's comparison against itself is undefined; it needs a certified family disjoint from the arm set |
| which reading was intended | **N/A** | the author's state (R1094) |
| cross-release | **N/A** | a second release |

`run.py` · `results/baseline_survives.json`
