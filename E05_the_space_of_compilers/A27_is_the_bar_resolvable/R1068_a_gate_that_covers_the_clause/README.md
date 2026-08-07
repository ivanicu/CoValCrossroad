# R1068 — build the coverage R1067 found missing. ⭐ **4 of 4 declared clause constants now red when mutated — and the gate fails closed.**

**The decision this round makes safe:** whether `the clause is anchored` can be made checkable at all.
**For its numeric constants, yes** — and the gate is shipped, not proposed.

## What was built

`assurance/the_clause_is_anchored.py` re-derives each clause constant **from the round that measured
it** and requires the statement to state it:

| constant | value | source |
|---|---:|---|
| certified family size | **2** | R1055 |
| q threshold family size | **10** | R1055 |
| k needed for q | **10** | R1056 |
| blind-comparator space cap | **15** | R1057 |

## The acceptance test is R1067's sweep — which the old gate failed 121 of 121

| cell | result |
|---|---|
| baseline (unmutated) | **green** |
| mutate `certified family size` | **RED** |
| mutate `q threshold family size` | **RED** |
| mutate `k needed for q` | **RED** |
| mutate `blind-comparator space cap` | **RED** |
| **SHAM** — mutate an **undeclared** clause number (`74`) | **green** |
| **NEGATIVE** — delete a source artifact | **RED (exit 1)** |
| PLACEBO — restore | **green** = baseline |

⭐ **The two controls that matter are the last two.** The **sham** shows the gate reacts to *these
values*, not to any edit — without it, four reds would prove nothing. The **negative** checks it
**fails closed**: R1063's defect was a gate that silently skipped a missing artifact and passed, so
this gate was written to red instead, and that is **verified here rather than asserted**.

## ⛔ What it does not cover, stated in the gate itself

**4 constants is not "the clause is anchored."** R1067 counted **121** numeric tokens in the clause
region. This closes the **declared subset** and leaves the rest **exactly as exposed as before** — and
the gate's own docstring says so. **A gate that overstated its reach would be the failure it was built
to fix.**

It asserts **numbers, never prose**. Prose assertions are possible but are a different instrument.

## IMPOSSIBLE here

- **covering the clause's prose** — **SETTLES: IN-RELEASE**, but by a different instrument than this
  one; declared rather than quietly folded into the count.

`run.py` · `results/clause_gate.json` · **ships:** `assurance/the_clause_is_anchored.py`
