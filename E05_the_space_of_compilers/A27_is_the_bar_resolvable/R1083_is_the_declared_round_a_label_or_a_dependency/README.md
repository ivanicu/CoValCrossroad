# R1083 — the anchoring gate lost **32 of 343 anchors** to the caller's working directory, silently, exiting 0.

**The decision this round makes safe:** whether the gate's coverage is a property of the record or of
the process that invoked it. **It was the process.** Repaired and guarded in this commit.

## ⛔ First: R1082's proposed estimand is NOT identified, and here is the measurement that says so

R1082's NEXT asked whether each anchor's match falls inside the DEFINITION.md region naming its
declared round. **166 per-round headings exist — and 83 of the 84 declared rounds have none.** The
anchors cite R3xx–R4xx; the headings belong to later rounds. A region model would have invented a
region for 99% of the population and assigned each anchor's text to a round that did not write it.

**A wall is only a wall once it has been checked** (§4). This one was.

## The form that IS identified — necessity by intervention, no semantics

`derive()` returns `label -> (value, round)` and the gate prints that round beside every verdict.
**Nothing checks it.** So: block a round's artifacts, re-derive, and see what survives. This is
R1049's mutation — *delete the source, ask whether the claim still stands* — carried to the sibling
gate, which is the crossing R1082 established had never happened.

| | |
|---|---:|
| keys `derive()` returns | **348** |
| distinct declared rounds | **83** |
| **Q1** keys UNCHANGED when their own declared round is blocked | **32** |
| **Q2** keys killed by exactly one *other* round | **2** |
| **Q3** keys killed by *no* single-round block | **32** |

⭐ **World A (the round column is a dependency) is KILLED.**

## ⛔ And my own verdict string was wrong — §4's row, committed inside this round

The first run printed *"their value is a **literal in the gate** rather than a reading of the
record."* **Nobody computed that.** Reading the object shows all 32 are derived through a **third
read route** the blocker never intercepts:

```python
json.load(open("E05_the_space_of_compilers/A24_.../R475_.../results/r475_card_vs_object.json"))
```

A **hard-coded relative path**. They *do* read the record — through the process's CWD. `0` of the 32
were `None` in the baseline, which is what a typed literal would have looked like, and checking that
is what killed the sentence.

## ⭐ The consequence is executable, which is why it beats the taxonomy

A gauge test: the same gate, the same files, two working directories.

| run from | anchors `⚠ UNEVALUABLE` | exit |
|---|---:|---:|
| the repository root | **0** | 0 |
| a round directory | **32** | **0** |

**9.3% of the document's coverage, decided by the caller's directory, silently, in the direction of
passing.** After the repair: `0 / 0 / 0` from the root, a round directory, and `/`.

## Controls — 8, all green

POSITIVE (blocking `R427` changes every key declaring it) · g=0 (blocking nothing changes nothing —
**not forced**: the proxy is live in both arms, so this is what would otherwise manufacture Q1) ·
SHAM (blocking a round-shaped directory that does not exist) · PLACEBO (blocking a non-round prefix)
· NEGATIVE (`R900`, declared by no key: **0** keys changed — reported, not assumed) ·
REPRODUCIBILITY · two GAUGE controls on the cwd test itself.

**Specification — the blocker's completeness, measured rather than asserted:**

| blocking route | Q1 |
|---|---:|
| `A24.glob` filtered (complete — intercepts `art()` **and** the 46 direct globs) | **32** |
| `art()` filtered only (incomplete) | **252** |

An `art()`-only blocker would have reported **252** keys as unbound. The difference is the whole
reason the completeness claim had to be a cell and not a sentence.

## The repair, and the guard so it cannot recur

**Repair** — all **8** relative `open("E05_…")` sites now build from the module's own `ROOT`.

**Guard** — `assurance/a_gate_is_cwd_invariant.py`, wired into `preflight.py` as `cwd-invariant`. It
runs each watched gate from two directories and requires the **exit code and the coverage token
count** to match.

⚠ **What it does not cover, named rather than left implicit:** it compares two runs of the same gate
and cannot say the coverage they agree on is *correct* — two runs that both lose 32 anchors pass.
And it does **not** make `⚠ UNEVALUABLE` fatal; that is a policy change with its own risk and is not
smuggled in here.

**Attacked five ways** (P7):

| # | vector | result |
|---|---|---|
| ① | run on the repaired tree | GREEN, rc=0 |
| ② | revert **one of eight** paths to relative | **RED rc=1**, `UNEVALUABLE 311→315` |
| ③ | neuter the comparator to always report equal | **rc=2** — its POSITIVE control fails |
| ④ | remove every watched gate | **rc=2**, never 0 |
| ⑤ | plant a cwd-dependent **exit code** | **RED rc=1**, `exit 1→0` |

⚠ **⑤ had to be built twice.** The first plant returned 1 from *both* directories, so it was not
cwd-dependent at all and tested nothing — my attack was mis-specified, not the guard. Rebuilt, it
fires.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| whether the *prose* beside a number describes the right round | **N/A** | a semantic judgement; R1076/R1078/R1079 measured that this repository's semantic questions do not survive syntactic classification |
| the R1082 region estimand | **N/A** | per-round headings for the cited rounds; 83 of 84 have none |
| cross-repository | **N/A** | a second gate suite |
| multi-seed | **N/A** | `derive()` is deterministic; the sweep is repeated identically instead |

`run.py` · `results/label_or_dependency.json`
