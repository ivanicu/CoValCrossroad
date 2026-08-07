# R854 · are the pair-shuffle survivors the SAME arms every seed?

**Arc A24.** ⭐ **World A, both controls passing — and it is the first mechanism claim in this thread
that a control did not refute.**

## ⛔ WHY THIS, AND WHY IT IS CHEAPER THAN THE ROUND I PLANNED

R853's NEXT proposed two more nulls to separate *coupling* from *ordering*. **One rung lower on the
attack ladder decides it for almost nothing.** R852/R853 established that the pair shuffle leaves
~14–16 arms clearing clause ②, and that κ proves this is **not** marginal-format agreement. Two
explanations remained, making **opposite predictions about a quantity already sitting in those runs**:

| world | prediction |
|---|---|
| **A · arm-intrinsic bias** | the **same** arms survive every permutation → survivor sets nearly coincide |
| **B · a different-but-fixed target each seed** | whichever arms align with *that* target win → overlap at chance |

**Survivor-set stability across null seeds had never been measured** (check #512, no prior art).

## ⭐ CONTROLS — and the load-bearing one can fail

| control | result |
|---|---|
| **the REAL survivor set must not move on a repeat call** (the target does not move) | **True · PASS**, \|set\| = 29 |
| ⭐ **closed-form chance overlap vs SIMULATED chance overlap** | max\|Δ\| = **0.0086 · PASS** |

⚠ **The second is the load-bearing one.** A closed form I derived is a claim about my own algebra,
and this project does not accept those unchecked — so it is simulated beside it and the two must
agree. **The first control is degenerate by construction and is not relied on.**

## ⭐⭐ RESULT — world A

| | |
|---|---:|
| pair-shuffle survivor sizes, 8 seeds | `[16, 12, 15, 13, 13, 15, 9, 17]` |
| **observed mean Jaccard**, 28 seed pairs | **0.8047** [min 0.5294, max 1.0000] |
| chance overlap at the same sizes | 0.0752 |
| **ratio** | **10.70×** |
| arms surviving at **all 8** seeds | **9** |

⭐⭐⭐ **The same arms survive every permutation.** World B is dead: the ~15 is **not** an artifact of
each seed manufacturing its own winners — it names **a real property of specific arms**.

## ⭐⭐⭐ AND WHICH ARMS — the part that matters for the definition

`oracle_k4` · `oracle_k4_fit1` · `oracle_k4_oracle_kA` · `greedy_k2_fit1` · `greedy_k4_fit1` ·
`greedy_k4_greedy_kA` · `greedy_k4_greedy_kB` · `indep_k2_fit1` (+1)

**Every one is an oracle or a fitted arm — an arm that touched the human labels.** So: **an arm
fitted to the labels acquires a property that beats a prompt-blind comparator even when
which-pair-is-which is scrambled**, and clause ② alone cannot tell that apart from tracking the
humans.

⚠ **The mechanism is NOT claimed.** R853 refuted my last mechanism claim one round after I published
it, so this one is labelled: `[HYPOTHESIS — untested]` candidates are shape properties of a fitted
verdict vector — transitivity, tie rate, calibration of the strict/tie mix — none of which κ's
marginal correction removes. **What is measured is the stability, not the cause.**

⚠ **And one thing owed, not asserted:** these 9 look like arms clause **③** (*no prompt labels*)
already excludes. **If so, ③ removes exactly the arms ② is most fooled by — an interlock the
definition has never claimed.** That is a checkable statement and it has **not** been checked here.

## STRUCTURALLY IMPOSSIBLE HERE
| criterion | what it would require |
|---|---|
| causally identified | an intervention on the arms' construction |
| construct validated | an external gold standard for corehood |
| cross-release | a second release |

⚠ **N/A with what each would require — never "planned".**
