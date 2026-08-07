# R635 · 43 rounds read a settled verdict as unsettled, and 58% of my closing lines talk about my own work

**Decision this makes safe:** the size of the verdict-key exposure. **43 rounds**, against a
pre-registered kill of 1.

| key set accepted | rounds |
|---|---|
| `['world']` only | **43 at risk** |
| `['world', 'verdict']` | 24 |
| no inline key read | 115 |

**77 artifacts record their result under `verdict` ALONE.** A reader accepting only `world` sees
those as having no verdict — **settled rounds read as unsettled**, which is exactly the class R600
widened the canonical reader to fix, in a repair that never reached the inline copies.

⛔ **The at-risk set includes `R596` and `R597` — rounds whose SUBJECT was the provenance gate**, i.e.
the very field that later changed. *The rounds most likely to be quoted about the gate are among those
reading it with the narrow key.*

## ⚠ One number in the table is not a measurement
Every at-risk row printed **"reaches 77"** — **identical across all 43**. That is the tell: my
`reaches` test matched any round carrying a citation regex at all, so **77 is the corpus-wide count
of verdict-only artifacts, not a per-round reach.** *An identical value on every row of a
per-item column is a property of the corpus wearing a per-item label.* **43 is measured; 77 is
context.**

## ⭐ The meta-count check #234 asserted, now computed
> **7 of the last 12 closing lines (58%) make a claim about my own prior work.**

Four of those were caught wrong — #230 *"outside every gate"*, #231 *"asked only the ledger"*, #232
*"widened once, repaired once"*, #234 *"one such reader"*. ⚠ **How many of the seven are wrong is not
decidable here** — it took a full round to find each. **The share that MAKE such a claim is the
measurable part, and it is the exposure.**

## Controls
| control | returned |
|---|---|
| **positive** — rounds accepting both keys exist | **24** — PASS |
| **positive** — artifacts recorded under `verdict` alone exist | **77** — so "at risk" is measurable and a zero would have been a measurement, not silence |
| **negative** — 115 rounds read no key inline and are not counted | PASS |
| **placebo** — a key no artifact uses | **0** |

⭐ **Self excluded by default**, not by repair — R634's lesson applied at design time rather than
after a control failed.

**MULTIPLICITY:** every (round, artifact) pair + 12 closing lines + 4 controls.

**IMPOSSIBLE, named:** a round can read an artifact **without its conclusion depending on that read**,
so 43 **overstates** conclusions actually wrong; every member is printed so the dependency can be
judged. And whether any specific conclusion **changes** needs re-running that round.

## ⛔ Check #234
*"R632 showed one **such** reader was wrong"* — R632's broken reader was the **ledger membership**
test, a different predicate family. *"**Any** round predating that reads a settled round as
unsettled"* — only those reaching an artifact that uses `verdict`, which is the conditional this
round measured and the sentence dropped.

## The sentence I can no longer write
> *"195 rounds read a verdict key inline."*

**80 do** — 43 narrowly, 24 widely, and the rest of R634's 195 was a looser match. **The number I
carried forward one round was itself from an untightened extractor.**

## NEXT
Both remaining directions are re-runs, and re-runs are expensive, so the cheap decisive question
first: **of the 43, how many actually PRINT a count of settled or unsettled rounds?** A round that
reads the key but reports something else is exposed and harmless. Grep their `results/*.json` for a
key whose value is a count of unsettled/settled rounds — **that intersection is the re-run list, and
everything outside it can be marked exposed-but-inert rather than re-run.**
