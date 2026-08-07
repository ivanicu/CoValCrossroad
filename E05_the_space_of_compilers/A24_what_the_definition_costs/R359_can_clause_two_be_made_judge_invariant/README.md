# R359 — self-normalising clause ② does not rescue it; at equal strictness it is just as empty

**The decision this makes safe:** *can the definition be repaired by restating clause ② relatively
instead of absolutely?* **No.** At the published reference's own percentile the two formulations are
indistinguishable, and both admit **zero** arms at the second judge.

## Where this started

The definition admits **5 arms at 2B and 0 at 0.8B** (R301, 41 arms), and at 0.8B no arm clears any
reference at or above that judge's closure (R358). **So the definition as written has no
judge-invariant content** — its verdict is not attenuated by a change of judge, it is emptied.

Clause ② is stated **absolutely**: beat one particular criterion set, `POOL[0:k]`, whose A2 is a
level on a scale every judge rescales. The obvious repair is to state it **relatively** — beat the
p-th percentile of the prompt-blind class *as scored by whatever judge is in use* — which is
self-normalising by construction.

## Result — `W_NEITHER_MATCHED_STRICTNESS`, on **42 arms** at both judges

R331 measured that the published `POOL[0:4]` reference sits at the **93.7th percentile** of its own
blind class. **That is the relative bar it must be compared against.**

| formulation | admitted at 2B | admitted at 0.8B |
|---|---:|---:|
| **ABSOLUTE** `POOL[0:k]` | 9 | **0** |
| **RELATIVE** at p = 93.7 | 9 | **0** |

**Indistinguishable — 9 vs 9 and 0 vs 0.** Self-normalising changes nothing at equal strictness.

## ⛔ The rescue that isn't, and it was the trap this round was most likely to fall into

RELATIVE **does** admit arms at 0.8B — at **p = 50, 60, 70, 75**, where the overlap with 2B is
complete (2 of 2, then 1 of 1) against chance expectations of 0.52 and 0.26.

Reading that as *"self-normalising helps"* would be **reading a lower bar as a better definition.**
Every one of those percentiles sits **below 93.7 by construction**.

> **There is no percentile at or above the published strictness at which the second judge admits a
> single arm — under either formulation.**

## The pre-registered statistic is UNRUNNABLE, and the reason is the finding

The design pre-registered a quantitative comparison: RELATIVE's excess-over-chance minus
ABSOLUTE's. **ABSOLUTE has zero defined cells** — it admits ∅ at 0.8B, so it has no
excess-over-chance for anything to be compared against. Exit **2**, an empty population, never a
silent pass.

The matched-strictness reading above is therefore **not the pre-registered statistic** and is
labelled as such throughout.

## Design defects found by reading the output

**① The saturation guard fired correctly and I nearly let it bury the result.** Agreement between
two admitted sets is trivially perfect when either is empty or full, so those cells are marked
UNDEFINED and excluded. Correct — but *why* ABSOLUTE had no defined cell was the answer, and
"no population, stop" would have discarded it.

**② `ABSOLUTE` has no percentile axis.** v1 printed the same cell 11 times, which reads as a swept
curve and is not one. One row now.

**③ ⛔ I declined validated evidence twice, and it killed v1 outright.** 30 of the 42 arms reach
0.8B via `sat_<arm>_08b.npz` rather than `sat08_<arm>.npz`. R358 and v1 of this round both called
that *"an assumption I decline to inherit."* But **R301 built a parity control for exactly this
path** — the two arms existing by *both* routes agree at Δ +0.00131 vs MDE 0.01193 and −0.00084 vs
0.01441, recorded `parity_can_fail: True`, i.e. shown able to reject.

> **Declining validated evidence is not rigour. It is a smaller n wearing rigour's clothes.**
> v1 ran on 12 arms, got |B| = 1, and had **not one defined percentile**.

## Controls

| | |
|---|---|
| **PLACEBO** — a judge against itself | overlap = \|A\| at every cell |
| **NOISE FLOOR** | the **exact hypergeometric** null for two random sets of the observed sizes — combinatorial, no draws |
| **saturation guard** | every undefined cell named, never dropped |
| reproducibility | two runs **byte-identical** (`beca3323d3c9`) |

The positive and g=0 synthetic-judge controls are **not reached**, because the branch they gate is
unrunnable. Stated rather than reported as passes.

## What this means for the definition

Consistent with R356/R357, which measured one arm family's ordering **inverting** between these two
judges: **the judge-dependence lives in the arms' ordering, not in the reference level.** A
reference sits *above* an ordering; it cannot *reorder* it. So no choice of reference — absolute,
relative, or any percentile of any class — repairs clause ②.

**A judge-invariant definition would need a judge named inside its text, or a different observable.**

## Register

| criterion | status |
|---|---|
| **a third judge** | **NOT-ATTEMPTED-AND-NOT-CHEAP** (R357) — no third checkpoint locally |
| **true invariance** | **N/A** — two judges can *refute* invariance, never establish it |
| **clause ③** | **not applied** — this round is about clause ②'s formulation; the 4 label-using arms stay in and are named |
| **cross-release** | **N/A** — one release |

## The sentence I can no longer write

> *"clause ② fails to transfer because it is stated on an unnormalised scale."*

**At equal strictness the self-normalised form is exactly as empty at the second judge.**

Artifact: `results/r359_judge_invariant.json`, source-stamped.
