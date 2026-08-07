# R842 · is the definition's own evidence byte-reproducible? — measured, not inferred

**Arc A25 — can the instrument be run at all.**

## ⛔ WHY THIS COULD NOT BE ANSWERED BY READING SOURCE

Entry 1358's sweep found `hash()`-seeded RNGs in 33 code lines across 29 files — but **its own proxy
ledger says the inference runs one way only**: *`hash(` in a seed ⇒ not reproducible* is sound;
*absence ⇒ reproducible* is **not**. A clean grep licenses nothing.

⚠ **And the tempting shortcut is a DERIVATION, not evidence.** The definition's anchor table names
**83 source rounds, all in R301–R838**; the unstable-seed rounds are **25, all in R122–R302**. The
intersection is **0 — but the ranges overlap only at `{R301, R302}`**, so that zero was very nearly
forced by arithmetic. **Reporting it as a clean bill would be the arithmetic trap this standard opens
with.** Labelled as a derivation; it is not the finding.

Two worlds survive reading, and only running separates them:

| | |
|---|---|
| **A** | the practice was corrected ~R302, and the rounds the definition rests on **are** reproducible |
| **B** | later rounds are irreproducible by a mechanism a source grep cannot see — set iteration order, dict-over-set, wall clock, an env var, a rebuilt input |

## ⭐ CONTROLS — both required, both passed

| control | result |
|---|---|
| **POSITIVE** a synthetic `hash()`-seeded script must be **non**-identical across two fresh processes | **True · PASS** |
| **g=0** a synthetic `crc32`-seeded script must be **identical** | **True · PASS** |

⚠ **The g=0 arm is not decorative: a differ that answers "different" to everything passes the
positive arm alone**, and that is the shape this suite keeps rebuilding.

**Pre-registered kill, conditional:** unless the synthetic pair separates, nothing the differ says
about a real round counts.

## ⭐⭐ RESULT — world A

sha256 over every file in `results/` (run logs excluded — they carry timings), two **fresh
processes** per round.

| round | role | exit codes | byte-identical |
|---|---|---|---|
| **R243** | **positive control on the real corpus** — on the frozen unstable-seed list | [0, 0] | **False** |
| **R436** | definition anchor | [1, 1] | **True** |
| **R440** | definition anchor | [0, 0] | **True** |
| **R824** | definition anchor | [0, 0] | **True** |

⭐ **3 of 3 tested definition anchors reproduce byte-for-byte; the known-unstable round does not.**
This is the first direct satisfaction of the checklist line *`REPRODUCIBILITY two hash seeds
byte-identical`*, which has been demanded all along and never run.

⚠ **R436 exits 1 and still reproduces** — an exit code is a verdict about the repo, not about
determinism, and the two are independent.

## ⚠ SCOPE — stated because 3 is not 83

- **population tested: 3 of 83 anchor rounds = 3.6%.** This licenses *"the three tested anchors are
  reproducible"*, **never** *"the definition's evidence is reproducible."*
- The measurement says **whether**, never **why**. A round can sit on the unstable list and still
  write an artifact that does not depend on the unstable draw — that is a real outcome and not a
  failure of the differ.
- **Cross-machine is untested** — one box, one interpreter build.

## WHAT THIS SITE STRUCTURALLY CANNOT DO
| criterion | what it would require |
|---|---|
| cross-machine / cross-scale | a second machine and a second interpreter build |
| independently replicated | a second suite |
| causally identified | an intervention isolating each irreproducibility mechanism |

⚠ **N/A with what each would require — never "planned".**

## ⚠ SAFETY NOTE, because re-running a round OVERWRITES its committed artifacts

Every touched round is restored with `git restore --staged --worktree` after the comparison, and the
tree census is stamped before the run. **A reproducibility test that destroys the artifact it is
testing is not a test** — and the outer timeout truncating before the restore is a live hazard,
recorded here rather than discovered later.
