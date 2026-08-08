# R1084 — the parse has **recall 1.00 and precision 0.11**, and it can speak for **47 of 88** scripts.

**The decision this round makes safe:** whether the cheap AST scan can replace the executed sweep
when looking for cwd-dependent reads. **It can NOMINATE and it cannot DECIDE** — and for 41 of the
88 scripts the executed instrument is **not identified at all**, which is the sharper finding and was
learned by damaging the repository.

## The result, with its scope

**Population** `assurance/*.py`, **88** files. **41 WRITE** into the repository and are excluded as
N/A (below). **47** read-only, all 47 eligible. **Instrument** an AST proposer and a two-CWD
execution. **Baseline** the determinism floor (run-vs-run from the same directory). **Regime** this
checkout, tree clean at start and at end.

| | run: MOVED | run: STABLE |
|---|---:|---:|
| **parse: proposed** | **1** | **8** |
| **parse: silent** | **0** | 38 |

**precision 0.111 · recall 1.000.** The single moving script is `a_control_that_cannot_fail.py`
(`rc 0 → 2`). Eight of nine proposals are literals the run never reaches.

⭐ **World A survives on this population, and the honest reading is a division of labour:** the parse
is a **sound nominator** (it missed nothing) and a **poor decider** (89% of what it names is noise).
R1083's instruction — *propose by parse, confirm by execution* — is the right shape, and this
measures the price of each half.

⚠ **My own worry about the proposer was unfounded, and measuring it is why it is not a caveat.** The
loose `anchored()` rule suppresses a proposal whenever a call mentions `.parent`, `.resolve()` or
`next(` — which inflates FN, the exact cell the kill reads. A strict variant demanding an anchored
*name* gives **identical numbers**: 9 proposals, FN = 0.

## ⛔ The 41 excluded scripts are the finding, and I learned it by breaking things

A script that writes into the repository **reads its own previous run's output**, so a two-run
comparison measures the side effect and not the working directory. Running the full population from
two directories — with the two arms concurrent, which I added for speed — left:

| file | damage |
|---|---|
| `assurance/ASSURANCE.md` | truncated to **22 of 111** lines |
| `assurance/DEFECTS.json` | **−395** lines |
| `assurance/MANIFEST.json` | **943** lines churned |
| `R72_proxy_validity_coefficient.json` | overwritten |

All restored with `git checkout`. **And the single FALSE NEGATIVE the damaged pass produced was
itself a writer** — `attack_scope_reaches_the_reader.py`, which rewrites `ASSURANCE.md` and restores
it in a `finally`. **The cell that would have killed world A was an artifact of my own concurrency.**

**N/A, with what it would require:** one isolated copy of the repository per run — a clone or
worktree per script per direction. That is a different round with a real disk cost, and it is the
only way to bring those 41 into the executed arm.

## Controls — 7, all green, and one was rebuilt after failing for its own reasons

| control | required | result |
|---|---|---|
| POSITIVE | a planted cwd-dependent read: **parse fires** | PASS |
| POSITIVE | the same plant: **run confirms** | PASS |
| g=0 | the copied script with no plant fires neither | PASS |
| NEGATIVE | a `ROOT`-anchored read fires neither | PASS |
| SHAM | an **unreachable** read call: parse fires, run does not | PASS |
| PLACEBO | the determinism floor is clean for the eligible set | PASS |

⛔ **The first SHAM failed for its own reasons.** It planted a bare assignment
`_UNUSED = "assurance/MANIFEST.json"` and asserted the parse would fire, on the strength of R1077's
*"a text scan counts mentions as uses."* **This proposer is not a text scan** — it only inspects
literals that are arguments of a read call, so it ignored the assignment correctly. I asserted a
blind spot my own instrument does not have, from its description rather than its behaviour. The
rebuilt sham plants a read call on an `if False:` branch: syntactically a read, never executed.
Parse fires, run does not — the mentions-vs-uses gap, priced.

**Specification curve** — 4 cells (`compare_on` × `normalise`), **1 moving in all four**. Every cell
is a re-**reading** of the same captured runs: the first design re-executed the population per cell,
640 extra invocations to vary two post-hoc transformations of stdout, which cannot change what a
process did.

⭐ **The captures are persisted** (exit codes, scrubbed output hashes, first 200 chars per arm), so a
better proposer can be scored against this sweep **without re-running it**.

## ⚠ A bound on R1083, measured here: the defect was latent, never live

R1083 found the anchoring gate losing 32 of 343 anchors to the caller's directory. **Every
programmatic runner pins the cwd to the repository root**, so it never fired through one:

| runner | cwd it passes | note |
|---|---|---|
| `preflight.py:57` | `cwd=ROOT` | the commit path |
| `run_all.py:67` | `cwd=ROOT.parent` | ⚠ in *that* file `ROOT` is `assurance/`, so this **is** the repo root |
| `audit_the_auditors.py:276` | `cwd=str(ROOT)` | the meta-gate |

No shell, hook or Makefile caller exists. **I nearly reported the opposite** — reading `ROOT.parent`
through the meaning `ROOT` carries in the other 87 files. Same error class as the arc's other six,
committed in my own analysis rather than in code, and caught by opening the file.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| the executed arm for the 41 writing scripts | **N/A** | an isolated repository copy per run |
| whether a moving script is *wrong* rather than cwd-aware | **N/A** | a per-script judgement; the round reports movement and names it |
| cross-repository | **N/A** | a second assurance directory |
| multi-seed | **N/A** | deterministic; the floor is two same-directory runs per script |

`run.py` · `results/parse_vs_run.json`
