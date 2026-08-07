# R445 · `gen` fails clause ② by a **resolved** margin — but at 1.07× its own floor

**The decision this round makes safe:** whether the definition's extension of one arm is a **finding
about generated cores** or an artifact of where a boundary was drawn. **A finding** — `W-RESOLVED` —
and the margins on both sides of the boundary are thin enough to state.

## ⛔ The announced step's premise was false

R444 closed with *"the generated core R433 built is the only object in this whole campaign that was
not built by `select_core.py` from one rubric."* **`gen` and `gen_sham` are home-release cores
generated from the conversation alone, and both have been in R360's 42-arm space the whole time.**

*Thirteenth announced step checked; its **premise** was wrong, not merely its necessity.* And the
check found something sharper than the step it killed: **③-corrected does not exclude `gen`** — its
selector is UNKNOWN, so R444's clause returns it unexcluded. **② excludes it.**

> **So the extension is one arm not because no third-source object exists, but because the one that
> exists fails the clause whose whole purpose is to admit things producible from the conversation
> alone.**

## Result — paired against clause ②'s own published reference `POOL[0:4]`, 968 prompts

| arm | Δ vs ②'s reference | 95% CI | MDE | |
|---|---|---|---|---|
| **`gen`** | **−0.0162** | [−0.0270, −0.0051] | 0.0151 | **RESOLVED below** — at **1.07×** the floor |
| `gen_sham` | −0.0669 | [−0.0790, −0.0543] | 0.0177 | RESOLVED below |
| `coval_core` | **+0.0178** | [+0.0079, +0.0285] | 0.0146 | **RESOLVED above** — at **1.22×** the floor |

**The definition's entire boundary at home separates `coval_core` from `gen` by 0.0340, across a
floor of ~0.015.** Resolved — and thin. Both statements belong together; quoting only the first
would make a 1.07× margin sound like a verdict.

## Controls

| control | returned |
|---|---|
| POSITIVE — an oracle ordering vs `POOL[0:4]` | **+0.1702** vs MDE 0.0184 ✅ |
| g=0 — `POOL[0:4]` against itself | **0.0e+00**, exactly ✅ |
| NEGATIVE — the sham must fail by **more** | **−0.0669 < −0.0162** ✅ |
| PLACEBO — the annotator draw held **common** across both arms | same 3 seeds, same prompt-keyed rng — drawing independently would add a difference that is not the arms' |

## What this settles

- **Settles:** the emptiness is about **generated cores**, not about a threshold. `gen` is worse than
  a size-matched blind set by a margin the design can see.
- **Does not settle:** that no generated core could pass. One generator, one greedy decode — and
  R432's oracle over five texts reaches far above any of them.
- **Does not re-open:** whether `POOL[0:4]` is the *right* reference. R331 measured it at the 93.7th
  percentile of 1,820 subsets, **chosen by file order**. That defect stands and this round leaves it.

## Impossible here, named

- **whether `POOL[0:4]` should be the reference** — R331's defect, not re-opened.
- **construct validity of A2** — the release's own human rankings.
- **generalising to generators this campaign did not build** — one generator, one decode.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
