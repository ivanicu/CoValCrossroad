# R361 — the definition's one unconditional sentence does not hold at the second judge

**The decision this makes safe:** *may `DEFINITION.md` close with an unindexed claim?* **No.** The
sentence published one round ago as the campaign's only unconditional statement is **2B-specific**,
and must carry a judge index like everything else.

## Result — `W_2B_ONLY`. All controls PASS. Two runs byte-identical.

R360 established that no reference purges a label-using arm, so clause ③ does work no reference can.
It ran at **Qwen3.5-2B-Base only**, and its register waved the second judge off — *"nothing is
admitted at 0.8B anyway"*. That is true about **admission** and does not settle this: **the claim is
about an ORDERING**, which is computable whether or not anything is admitted.

| statistic | @ 2B | @ 0.8B |
|---|---:|---:|
| **min label-users over the 45-level sweep** | **4** — never purged | **0** — purged |
| published five at the strongest reference | 0 | 0 |
| level purging all labels while keeping a five-arm | NONE | NONE |

**At 0.8B, references do purge label-users.** R360's irrepleaceability is a fact about 2B.

## The rank statistic — and my branch let an unresolved test preempt a resolved one

Exact null over **all C(9,4) = 126** label/five assignments — enumerated, not sampled:

| judge | gap (mean label rank − mean five rank) | percentile | two-sided p | |
|---|---:|---:|---:|---|
| **2B** | **−4.50** | 0.8% | **0.0159** | **RESOLVED** — the label-users genuinely dominate |
| **0.8B** | +2.25 | 90.5% | **0.2857** | **NOT RESOLVED** |

⛔ **v1 fired `W-INVERTED` on `mlr > mfr`** — a bare comparison of two means — and was about to
publish *"the two judges disagree about which arms the definition should exclude."* At 0.8B the
label-users **split**: `indep_k4_fit1` ranks **1**, `greedy_k4_fit1` ranks **8**, sd **3.59**. A gap
of 2.25 inside that spread is a **direction**, not a separation.

Worse than the wrong threshold: **the branch order let the unresolved statistic preempt the resolved
one.** The sweep needs no rank at all, and it is where the verdict now rests.

## Controls

| | @ 2B | @ 0.8B |
|---|---|---|
| **POSITIVE** — the sweep distinguishes levels | weakest 9, strongest 4 | weakest 4, strongest 0 |
| **g=0** — a reference against itself not admitted | PASS | PASS |
| **PLACEBO** — each arm ranked against itself | difference 0 | difference 0 |
| **NOISE FLOOR** | the **exact** C(9,4) enumeration — combinatorial, no sampling | |
| multiplicity | 2 judges × 45 levels × 9 arms = **810** admission cells, both sweeps whole | |
| reproducibility | two runs **byte-identical** (`e4a731066570`) | |

The arms reach 0.8B by the **parity-controlled** path (R301: Δ +0.00131 vs MDE 0.01193, and −0.00084
vs 0.01441, `parity_can_fail: True`) — the evidence R359 established it was an error to decline
twice.

## ⛔ What this retracts, one round after I published it

`DEFINITION.md` closed with:

> ~~*"A core may not be built from the labels of the prompt it is for. No strengthening of any other
> clause can substitute for saying so."*~~

The **wording** of clause ③ needs no judge — it is a provenance rule, and it applies by inspection.
What was judge-dependent is its **justification**: *"nothing else can do its job"* is measured at 2B
and **fails at 0.8B**, where a reference does purge the label-users.

**Corrected: clause ③ is unsubstitutable at 2B; at 0.8B a sufficiently strong reference substitutes
for it.** The rule itself still stands on provenance grounds, which need no instrument at all — and
that is a *weaker and different* argument than the one it replaces.

⚠ **Note the direction.** I found this by attacking my own newest published sentence rather than
building on it. It had survived exactly one round.

## Register — what this site cannot do

| criterion | status |
|---|---|
| **a third judge** | **NOT-ATTEMPTED-AND-NOT-CHEAP** (R357) — no third checkpoint on the local store |
| **establishing instrument-independence** | **N/A** — two judges can refute it; they never establish it |
| **resolving the 0.8B rank inversion** | **needs more arms** — 9 arms give C(9,4)=126 assignments and a floor of p≈0.016; the observed 0.2857 is not near it |
| **cross-release** | **N/A** — one release |

## The sentence I can no longer write

> *"A core may not be built from the labels of the prompt it is for — no strengthening of any other
> clause can substitute for saying so."*

**The second half is 2B-specific. The rule survives on provenance, not on irreplaceability.**

Artifact: `results/r361_clause3_second_judge.json`, source-stamped.
