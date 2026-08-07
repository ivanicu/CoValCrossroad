# R680 · citations are not computations

**⭐⭐⭐ 20 rounds hold the ③ extension; 8 derive it and 12 carry it as code literals. Of the 8, two
read a prior round's artifact — so **at most 6 independent computations** stand behind the **22
rounds** the deliverable's extension rows cite.**

## ⚠ THIS DIRECTORY WAS NAMED `R680_twenty_two_citations_one_computation`
**I encoded the answer in the name before measuring it.** The answer is 8 derivers, at most 6
independent — not one. Renamed, and recorded in the ledger rather than quietly fixed. *A directory
name is a claim, and it is the one claim in a round that no control ever touches.*

## ⭐ CHECK #281 · R679's PROPOSED TEST WAS BLIND — KILLED BY A GAUGE TEST AT ZERO COMPUTE
R679 asked to separate *recomputed* from *restated* by whether the set appears **as a value in
`results/`**. A value in `results/` is produced **identically** by recomputation and by a hard-coded
literal — the **measurement is invariant under the distinction the property depends on.** Attack
ladder step 1, three lines. And R676's census had already recorded `R529.ext_rank` and
`R534.ext_rank`, so the proposed test's answer was committed before the round was proposed.

**The separable test:** do the members appear as **literals in executable source**?

## THE CONFOUND, NAMED BEFORE THE RUN, WITH ITS CONTROL IN THE SAME ITERATION
Every round's docstring quotes arm names, so a raw literal count measures **prose, not code**.
Executable source is extracted by a tokenizer strip of comments and docstrings first.

| control | returned |
|---|---|
| POSITIVE — all five as list literals | **5/5 → RESTATES** → PASS |
| **g=0** — a source with none | **0/5** → PASS, *the detector returns both values* |
| NEGATIVE — all five in a **docstring only** | **0/5** → PASS, **the confound is stripped** |
| PLACEBO — run twice | identical → PASS |

## THE COUNT (G3 — every round holding the set, none sampled)

| literals | rounds |
|---|---|
| **0/5 — ⭐ derives** | R294 · R353 · R404 · R405 · R408 · R409 · R519 · R667 |
| 1/5 | R301 · R332 · R354 · R529 · R534 · **R677** |
| 2/5 | R330 · R339 · R442 |
| **5/5 — fully hard-coded** | R360 · R361 · **R676** |

- rounds holding the set **20** · derive **8 (40.0%)** · restate **12**
- of the 8 derivers, **2 read a prior `results/` file** (R353, R519) → **at most 6 independent**
- Registered **A 3 [1,8] → 8, INSIDE (+5)** · **B 30% [10,60] → 40.0%, INSIDE (+10.0)** ·
  **directional (R294 among derivers) HOLDS**

## ⚠ UPPER BOUND, NOT A COUNT — TWICE OVER
*"No code literals"* does not prove independent computation. It removes **one** way of faking it. A
deriver reading the release's own data shares a source rather than copying, so **6 is a ceiling on
independence, not a measurement of it.** The honest form is *at most 6*, never *exactly 6*.

## WHY THIS MATTERS FOR THE DEFINITION
R679 found the deliverable's extension rows cite **22 rounds**, none of them a producer. This round
puts a number on what those citations are worth: **the citation count and the computation count are
different quantities**, and only the second bounds how much independent support the central set has.
**Twenty-two agreeing citations can be six computations, and agreement among copies is not
replication.**

## IMPOSSIBLE HERE
Proving independent computation would need each round re-executed against its own inputs; **93 rounds
in this arc are corpus-dependent** and would not reproduce. Named, not planned.

## NEXT
Three rounds carry the set as five source literals — R360, R361 and R676 (`results/n_eff.json`, the
`rounds` list, entries with `literals: 5`). R676 is mine, written four rounds ago, and it hard-coded the set
while measuring set membership. Check what each of the three does with the literal: a fixture the
round compares against is legitimate, a value the round reports as its own finding is not. That
distinction is readable from whether the literal feeds an assertion or an output field.
