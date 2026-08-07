# R425 · how far does the unknown instrument reach? The search is the instrument, so control it first

**The decision this round makes safe:** which committed claims need their scope rewritten after R424,
and which do not. **`(D) = 11` rounds outside this audit arc** read a satisfaction `_08b` arm —
**W-WIDE**, and an **upper bound**, not a count of exposure.

## ⛔ `30 rounds` was the instrument's unit, not the claim's

`grep -rl 08b` counts files containing four characters. One `grep -n` showed the two units are not
equal: **`R12_response_set` reads `a08_gold_08b.npz` — a GOLD file, which R424 tested and found
carries no `meta`/`sat` at all.** Same four characters, *different kind of object*, and it **is**
committed, so a round using it carries no exposure. **The population is `reads sat_*_08b* /
core_*_08b*`,** and gold files, prose and print strings are counted **separately** rather than
dropped — a class removed silently is a class nobody can check.

## ⛔ The known-answer control failed twice, and it was right both times

| attempt | what happened |
|---|---|
| **① source scan** | called R422–R424 `PROSE`. They assemble paths across **two** f-strings (`load(f"{tag}_08b")` → `f"core_{tag}.json"`), so the literal `core_..._08b` **exists nowhere**. |
| **② + artifact scan** | R424 recovered (its artifact records `oracle_k4_08b`), R422/R423 still failed — their artifacts key on **base tags**, not suffixed arms. **Both instruments blind to the same two rounds.** |
| **③ fragment rule** | a bare `"_08b"` counts as a read only when **filename-shaped** (no whitespace, ≤ 40 chars) **and** the module elsewhere spells a `core_`/`sat_` prefix. |

⭐ **The synthetic plant passed every time; the real corpus failed twice.** *A classifier validated
only on cases I invented is validated against my imagination* — and this is the **third** time in
this arc a real-case control caught what an invented one could not.

⚠ **The fragment rule is loose enough to be dangerous, so it is tested in both directions.** Without
the shape test, R420/R421's print banners (`⛔ SO THE _08b/_08bR DIVERGENCE …`) flip to `SAT` and
they read nothing. **That false positive is exactly what the two `NOT-SAT` known cases exist to
catch** — the rule was tested, not loosened until the answer I wanted appeared.

| known case | want | got |
|---|---|---|
| `R422` · `R423` · `R424` | `SAT` | `SAT` |
| `R420` · `R421` (print banners only) | `NOT-SAT` | `PROSE` |
| `R12_response_set` (gold file) | `GOLD` | `GOLD` |

## The census — 408 sources scanned

| class | n |
|---|---|
| **(A)** reads a satisfaction `_08b` arm — **emitter not on disk** | **15** |
| (B) reads only the GOLD `_08b` file — **is** committed | 3 |
| (C) `08b` in prose only, no artifact read | 6 |
| **(D) = (A) − the audit arc** — upper bound on **downstream** exposure | **11** |

**Instrument disagreement, printed because it is the informative part:** 14 `SAT`-by-source-only, 0
`SAT`-by-artifact-only. Each is blind where the other sees; **the union is the bound, neither alone
is.**

The 11: `R301` `R311` `R358` `R359` `R360` `R361` `R362` `R408` `R414` `R415` `R416`.

## ⭐ What this does and does not overturn

**Most of the 11 are named *"at the second judge"* — they are deliberate cross-instrument
replications.** R424 measured that the foreign table genuinely differs from the default (**~96 %** of
values absent). So **the comparison survives; only the instrument's NAME was wrong.**

⚠ And *"judge"* is itself more than the evidence carries. What R424 established is a **second
TABLE** — a different set of satisfaction values. That it came from a model, let alone a 0.8B one, is
**not** established by anything on disk.

## Impossible here, named

- **reads vs publishes-from** — needs reading; (A) is an upper bound and (D) subtracts only the audit
  arc, the one subset established by construction.
- **exposure through data rather than source** — a round consuming a downstream artifact itself built
  from an `_08b` arm is invisible to both instruments. Needs a provenance graph, which is exactly
  what these artifacts do not carry.
- **cross-release** — one release.

Findings, with their scope, live in the top-level README. This file states the design.


---

## ⛔ ITS CLOSING SENTENCE IS RETRACTED BY R426

> ~~*"'judge' is a noun I never had evidence for."*~~

**False.** `R290/run.py:58` names `Qwen3.5-0.8B-Base` as the 0.8B judge in committed source, and
R426 corroborates it from data: `sat08_full.npz` contains both `_08b` families at **`1.0000`**.

**The census itself stands** — 15 `SAT`, 11 outside the arc, six known-answer cases reproducing.
What was wrong is the *consequence* I drew from it, which was inherited from R424's wall rather than
measured here. ⚠ **A round can be sound and still ship a false conclusion if it accepts a
predecessor's verdict as a premise** — and this one listed R301 among its own 11 without ever opening
it. **The refutation was inside my own output.**

→ [`R426`](../R426_the_emitter_was_excluded_by_my_own_filter)
