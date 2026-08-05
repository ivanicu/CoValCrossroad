# R490 · The announced compute was already built, and could not have settled it

⚠ **Action class: CLOSURE.** It kills a proposed frontier action before compute. Labelling it a
discovery would be closure disguised as one.

**The decision this made safe.** Whether to spend a GPU round on *"a strong rating-blind prompt-aware
arm, scored under more than one judge."* **No — on two independent grounds, both free.**

## (a) The generator already exists

`corebench/generate_core.py`, in its own docstring: *"THE GENERATOR MUST NOT SEE `coval_full`… It sees
the CONVERSATION and the FOUR RESPONSES only."* **Rubric-blind, rating-blind, prompt-aware — the exact
object proposed.** `gen` is its output, and R487 measured it as the **best ③-admissible arm on the
site, at percentile 32.6.** I proposed building the thing I had spent three rounds measuring.

⭐ **Checked by reading the file's stated contract, not its name** — P4: *"did I establish it by asking
the system, or did I read it somewhere?"* **g=0:** the same check applied to a third judge returns
**0 artifacts**. A prior-art gate that finds everything present is not a gate.

## (b) The second judge cannot adjudicate the gap

Attainment of the Bayes ceiling (R479), by judge:

| arm | 2B | 0.8B | ratio |
|---|---|---|---|
| `oracle_k4` — reads the human target **directly** | **+1.088** | **+0.105** | **0.10** |
| `topw_k4` | +0.738 | +0.193 | 0.26 |
| `random_k4_s0` | +0.350 | **−0.106** | −0.30 |

**The oracle keeps 9.7% of its attainment under 0.8B.** A judge on which an arm that *reads the answer*
scores at a tenth cannot separate a **+0.0067** gap. **NEGATIVE control:** `topw_k4` collapses too
(26.2%), so the collapse is a property of the judge, not of the oracle.

## What this puts in the register

**What would settle ②∧③ is a judge STRONGER than Qwen3.5-2B, and this site has none.** Not "a second
judge" — that reads as available, and the one available is weaker. Not a new generator — it exists.

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R490_the_announced_compute_was_already_built/run.py

Zero compute · artifact `results/r490_prior_art.json`.
