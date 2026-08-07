# R1080 — the helper is reachable from every depth. It has **zero** static importers.

**The decision this round makes safe:** whether the remedy for the precision-blind comparison is
**production** (make `assurance/valuematch.py` importable) or something else. **It is something
else** — the file is already importable from every depth this repository contains, by an idiom
already used in **262** committed statements. Building an import shim would have been work against a
barrier that does not exist.

## What R1079's NEXT claimed, and what it was worth

> *"a helper that requires a path fiddle to import will be re-implemented rather than reused, and
> that is the mechanism this whole line failed on"*

⛔ **World A (MECHANICAL BARRIER) is KILLED**, on all three pre-registered conditions:

| condition | required | measured |
|---|---|---|
| **k1** landmark reaches the helper from every in-repo depth | all cells | **6 depths × 3 modes, 18/18** |
| **k2** the landmark idiom already adopted at scale | ≥ 100 statements | **262** |
| **k3** a committed round script already reaches into `assurance/` | ≥ 1 | **139 files** |

## The grid — 126 cells, all reported

Cells reaching the helper: **39 of 126**. Depth = path components from the repository root; a
canonical round `run.py` is at **4**, where **1006 of 1007** round scripts sit.

| idiom | role | d2 | d3 | **d4** | d5 | d6 | d8 | off-tree |
|---|---|---|---|---|---|---|---|---|
| `parents3` | committed-dominant | 0/3 | 0/3 | **3/3** | 0/3 | 0/3 | 0/3 | 0/3 |
| `landmark` | committed-robust | 3/3 | 3/3 | **3/3** | 3/3 | 3/3 | 3/3 | 0/3 |
| `namespace` | candidate remedy | 3/3 | 3/3 | **3/3** | 3/3 | 3/3 | 3/3 | 0/3 |
| `bare` | **PLACEBO** | 0/3 | 0/3 | **0/3** | 0/3 | 0/3 | 0/3 | 0/3 |
| `sham` | **SHAM** | 0/3 | 0/3 | **0/3** | 0/3 | 0/3 | 0/3 | 0/3 |
| `nonexistent` | **g=0 GUARD** | 0/3 | 0/3 | **0/3** | 0/3 | 0/3 | 0/3 | 0/3 |

⚠ **The `parents3` row is a DERIVATION, not a measurement.** `parents[3]` of a file at component
count *d* lands at *d−3*, which is the repository root only at *d = 4*. It was executed, but it
could not have come out otherwise. It is reported as the negative control's evidence and **is not a
finding**. The `bare` and `nonexistent` rows are likewise forced — given an empty `PYTHONPATH`,
which is the assumption they exist to check rather than assume.

⭐ **The `landmark` row is not forced**, and that is why the confound below had to be run.

## Controls — all green, and one went red first

| control | required | result |
|---|---|---|
| POSITIVE | `parents3` succeeds at canonical depth, all modes | **PASS** |
| NEGATIVE | `parents3` fails at every non-canonical in-repo depth | **PASS** |
| PLACEBO | no path work succeeds nowhere | **PASS** — exactly 0 |
| SHAM | the same search minus the ingredient (an absent marker) | **PASS** — 0, by `StopIteration` |
| g=0 GUARD | correct path, absent module | **PASS** — 0 |
| CROSS-INSTRUMENT | AST statement total vs an independent line scan | **1054 = 1054** |
| REPRODUCIBILITY | the whole grid run twice, byte-identical | **PASS** |

⛔ **The census classifier's POSITIVE control failed on the first run, and it was right to.** The
first implementation matched substrings of `ast.dump()` — `"Call(func=Name(id='next')"` — which can
never fire, because `ast.dump` emits `Name(id='next', ctx=Load())`. It labelled **all 262** committed
landmark searches `other`, and had the control not existed the round would have read `k2 = False`
and concluded that world A survived. **Matching a serialisation of a tree is a text scan wearing an
AST's clothes.** The repair walks the tree; a REGRESSION control now pins the exact committed form
verbatim.

## Strongest confound, written before the verdict and controlled in the same iteration

*The landmark succeeded because my probe tree contains no intervening marker. A round beneath a
directory with its own `covalx/` would stop early and resolve to the wrong root — depth-robust but
**ambiguous**.*

- **Observed** — directories in this checkout holding a `covalx` child: **1** (the root). Unique.
- **Sensitivity** — a planted decoy marker above a probe **captures** the search (it resolves to
  `_r1080_decoy_tmp/decoy_root`, not the repository). So the search *can* be misled, and the
  uniqueness above is a measurement rather than an instrument that never fires.

`k1` is conditioned on both. Without them, "reaches the helper" would only mean "reaches something".

## ⭐ The finding this round did not go looking for

**Q3 · adoption, by mechanism — the helper has been importable and known for four rounds and has
never been imported.**

| mechanism | count | which |
|---|---:|---|
| static `import valuematch` | **0** | — |
| dynamic `import_module("valuematch")` | **1** | R1076 — its own author, verifying it loads |
| names it in prose only | **3** | R1077 · R1079 · **R1080, this round** |

R1077 and R1079 each **wrote a sentence saying the helper needs adopting rather than merely
existing**, and neither adopted it. Neither did this one. **The rounds that diagnosed the adoption
problem are the population of non-adopters.**

## What this round cannot say — and it is the live fork

World A is dead. **B (the helper was unknown) and C (rounds are conventionally self-contained) are
not separated here**, and B is already weak: all three non-adopting rounds name the file by path, so
it was not unknown to them.

⛔ **The discriminator is deliberately NOT a syntactic classifier.** R1076, R1078 and R1079 each
tried to recover a semantic category from syntax, and each failed a control it could not have
passed. Asking "did this round have an occasion to use it?" is the same question in the same shape.
**N/A here — it would require an occasion that is identified by execution rather than by parsing:**
a round whose own artifact contains a prose-read decimal compared against a stored value, detected
by running the comparison both ways and observing a disagreement. That is a different instrument,
not a better rule.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| cross-site / cross-repository | **N/A** | a second repository with its own round convention; every number here describes this checkout only |
| construct validity of "why it was re-implemented" | **N/A** | the author's state at the time, which is not recoverable — hence B vs C is reported as unresolved, never as a point |
| multi-seed | **N/A** | the instrument is deterministic; substituted by a two-run byte-identical grid |
| multiplicity correction | **N/A** | no cell is a hypothesis test — each is a deterministic observation, and decorating booleans with a q-value would be the arithmetic trap |

`run.py` · `results/reachable_or_unknown.json`
