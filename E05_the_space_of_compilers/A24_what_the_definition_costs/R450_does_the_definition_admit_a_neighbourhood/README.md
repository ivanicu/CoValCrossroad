# R450 · the definition admits a **neighbourhood**, and the coordinate that governs it is not the one I designed

**The decision this round makes safe:** whether the extension of **1 arm** means the definition is
strict or means it *describes the instance* — §4's oldest entry, open since the definition was
written. **Strict. `W-NEIGHBOURHOOD`.**

## ⛔ First, the announced audit died — 2 of its 3 premises were false

R449 closed proposing an audit of "what else rests on a population of one", citing three examples.
Checked against the document rather than memory:

| claim | verdict |
|---|---|
| *"④'s adoption argument used a one-release bar"* | ⛔ **FALSE** — `DEFINITION.md:133`, `:522`: ④ removes **all 7 arms on the second release**. Explicitly two-release. |
| *"the register lists cross-release as unmet"* | ⛔ **FALSE** — `:600`: *"the route is now WALKED, not open"*; R433 ran it. |
| *"`n_judge_pairs = 1`"* | ✅ TRUE (R449) |

*Eighteenth announced step checked, tenth premise killed.* **Both false ones ran in the direction
that manufactures work** — inventing a weakness the document does not have.

## The separator was free, and it is the question the campaign never asked

Every round so far tested clauses against arms built by *other selectors*. None tested objects
**adjacent to the released core itself**. `sat_coval_core.npz` holds **per-criterion** satisfaction,
so any subset of the core's own criteria, and any mixture with the generic pool, scores with **no GPU
at all**.

Candidate = `r` of the core's own criteria + `a` of the 16 pool criteria. Outcome = the **share** of
the size-matched class `C(16, r+a)` it beats under clause ②'s own test. ⭐ **A share needs no
threshold, so this round introduces no free parameter anywhere.**

## ⭐ Result — and `d` was the wrong coordinate

| `r` (core retained) | share | sd | | `a` (generic added) | share | sd |
|---|---|---|---|---|---|---|
| 0 | 0.1661 | 0.0332 | | 0 | 0.7193 | 0.2207 |
| 1 | 0.4184 | 0.0460 | | 1 | 0.6555 | 0.3007 |
| 2 | 0.7187 | 0.0404 | | 2 | 0.6677 | 0.2930 |
| 3 | 0.9215 | 0.0376 | | 3 | 0.6588 | 0.3216 |
| 4 | **0.9868** | 0.0045 | | 4 | 0.6208 | 0.3394 |

> **Variance of admission explained: by `r` 98.6% · by `a` 1.0%.**

**Admission is governed almost entirely by how much of the released core is retained, and adding
generic criteria is nearly free.** I designed the round around distance `d`; the data says `d` mixes
one coordinate that matters with one that does not. The dose-response in `r` is **monotone across all
five levels** with non-overlapping spreads.

**Dropping one criterion of four still clears 92% of the class. The definition does not collapse on
perturbation — so the extension of 1 is a fact about which arms were built, not about strictness.**

## Controls — both anchors come free, and neither could be satisfied in advance

| control | returned |
|---|---|
| **CEILING** — d=0 must reproduce R446's committed share | **0.9841 vs 0.9841** ✅ (an independent code path re-deriving a published number) |
| **FLOOR** — the class's own mean self-share, computed | **0.2198**; same-rule fixed subset **0.2563** ✅ |
| SHAM — criteria from other prompts, size-matched | **0.0000** at every cell with `r>0` |
| SEEDS | 5 per cell; spread reported, never averaged away |

## ⛔ The FLOOR anchor was wrong twice, and both fixes were computations

1. **It asserted ~0.5** because a full-replacement candidate *is* a class member. **False:** `share`
   counts references beaten **resolvedly** (gap > MDE), not merely exceeded — different statistics.
   The campaign's own numbers already showed it (coval_core quantile 1.0000 → share 0.9841; `gen`
   quantile 0.2615 → share 0.0038). §4 sub-kind ③. Replaced by the class's **computed** self-share.
2. **It still compared two different objects.** `build()` re-draws criteria **per prompt** — correct
   for a core, which is per-conversation by definition — while every class member is **one fixed
   subset** used on all prompts. The anchor was measuring that difference, not the size-matching.
   Built the same way as the class it passes at **0.2563**.

⭐ **And the discarded comparison is a real finding, not a defect:** a prompt-**varying** random
selection from the pool scores **0.1145** against a **fixed** one at **0.2563**. Varying the generic
criteria per prompt makes an arm *worse*.

## Impossible here, named

- **whether a neighbour is "really" a core** — needs a standard outside this definition. This
  measures the definition's **extension**, never its correctness.
- **criteria not already judged** (paraphrases, new generations) — needs a generator and GPU; the
  round is deliberately confined to what is scored, which is why it costs nothing.
- **a second released core to repeat this around** — the release ships exactly one.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
