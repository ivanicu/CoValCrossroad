# R404 — clause ③'s three conjuncts: one does all the work, one does none, one is not implemented

**The decision this makes safe:** *is clause ③ one clause or three?* **One. And the third, read
literally, admits only the object the definition was written from.**

## Result — `W_3C_BINDS`. Key-reproduction control passes (after it caught a real bug). **No GPU.**

### (A) what each conjunct excludes on its own, over 42 arms

| conjunct | excludes | beyond ③a |
|---|---:|---:|
| **③a** reads the prompt's own rankings | **4** — `oracle_k4`, `oracle_k4_fit1`, `greedy_k4_fit1`, `indep_k4_fit1` | — |
| **③b** fitted on a **HALF** of them | 3 — all `_fit1` | **0** |
| **③c** weights from an annotator **RUBRIC** | **13** — `full`, `topw_k*`, `topabs_k4`, `topvar_k4`, `topwvar_k4` … | **13** |

### (B) the admitted set, conjunct by conjunct (nested: verified)

| | n | arms |
|---|---:|---|
| ② | 9 | `coval_core`, 4 label-readers, `topw_k3/4/6/8` |
| ② ∧ ③a | **5** | `coval_core`, `topw_k3/4/6/8` |
| ② ∧ ③a ∧ ③b | **5** | *unchanged — ③b removes nothing* |
| **② ∧ ③a ∧ ③b ∧ ③c** | **1** | **`coval_core`** |
| published (R360) | 5 | matches `② ∧ ③a` |

## ⛔ The definition is caught between two failures

**As implemented**, ③c does no work — the enforcement is a hand-written key containing only ranking
readers, and **R363 established independently that the rubric channel is open** (`W_CHANNEL_OPEN`,
per-prompt annotator overlap far above a cross-prompt sham).

**As written**, ③c forbids *"by way of a rubric those same annotators wrote"* — and `topw_k`'s weights
come from `conversation_rubrics.jsonl`. Enforcing the sentence leaves **exactly one admitted arm: the
released core itself.**

> **Neither is a definition of a category.** One admits arms its own text forbids; the other admits
> only the instance it was written from. **This is the *"definition describes the instance"* failure,
> measured rather than suspected.**

## ⭐ The control caught a real bug, and the parser was fixed rather than the control relaxed

The **KEY REPRO** control requires the ③a set *derived from `corebench/select_core.py`'s rule
dispatch* to **equal** the key `USES_PROMPT_LABELS` hand-written in four rounds.

**My first parser was wrong**: a lazy `([a-z_]+?)_?k?` consumed the `_k`, so `oracle_k4` returned
`oracle`, the derived set came back **empty**, and the round **exited 1** rather than reporting a
decomposition built on a broken parser. *The control failed for the instrument's reasons — the
failure table's own warning — and the remedy was to fix the instrument.* The tag is now un-built by
**reversing** `select_core.py:204-206`'s construction in order, instead of pattern-guessing.

**On the repaired parser the two sets are identical**, which validates the hand-written key against
the object mechanically.

## Controls

| | returned |
|---|---|
| **KEY REPRO (+)** | derived ③a **=** hand-written key — `PASS` (after catching the parser bug) |
| **DISPATCH (−)** | a fabricated rule maps to no data file — `PASS`, so *"reads nothing"* is attainable |
| **PRIOR ROUND** ⭐ | that `oracle_k`/`indep_k`/`greedy_k` are the ranking readers comes from **R363**, a different round asking a different question. **The answer key was not made here** |
| **NESTED** | the four admitted sets must be subsets in order — verified `True` |

## ⚠ Two limits

1. **This round does not decide whether ③c *should* be enforced.** That is an act of **definition**,
   not a measurement. It reports what the sentence, read literally, does to the published set.
2. **The blind spot runs the flattering way.** A label route the rule dispatch does not reveal means
   **more** exclusions, not fewer — so every count here is a **lower bound**.

## Register

| criterion | status |
|---|---|
| **re-scoring any arm** | **N/A** — needs the judge; uses R360's published sets |
| **deciding whether ③c should be enforced** | **N/A** — an act of definition |
| **label use via a hidden route** | **UNIDENTIFIED**, biasing toward fewer exclusions |

## The sentence I can no longer write

> *"clause ③ excludes 4 of 42"* — **as though the clause were one thing.** ③a excludes 4, ③b excludes
> nothing at all, and ③c excludes 13 — including four of the five arms the definition currently
> admits.

Artifact: `results/r404_conjunct_decomposition.json`, source-stamped.
