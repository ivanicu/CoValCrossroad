# ⛔⛔ RETRACTED BY R1007 — this round's headline fails the negative control THIS ROUND DECLARED

> **`Δ = +0.0828` is WITHDRAWN.** The `NEGATIVE CTRL` and `PLACEBO` declared in this round's
> docstring were **never implemented** — `NSHUF = 200` is defined at line 74 and used nowhere,
> and the artifact records one control. R1007 ran them: against a band-matched null Δ_real
> clears the 95th percentile in **6 of 30** cells, and the survivors are **monotone in the
> LOOSEST caliper** (0/10 · 1/10 · 5/10), which is the signature of a band artifact.
> ⭐ **What still stands: the duplicate census** — 14 identical pairs, 96 → 85 distinct, the
> extension 8→4 and 11→6. That is a fact about the arms and does not depend on Δ.
> Full account: `RETRACTIONS.md` and `R1007_*/README.md`.

---

# R1005 · the extension converges beyond its score level — and its count was inflated by duplicates

**THE DECISION THIS MAKES SAFE.** Whether the formulation's extension is a **coherent family** or
just a **score band**. It is a family — **Δ = +0.0828 [+0.0499, +0.1169]** against a measured floor of
**0.0183**, **effect/floor = 4.5**, resolved in **30 of 30** cells. ⚠ And along the way: **its size
was overstated ~2×.**

---

## ⚠ SCOPE ADDED BY R1011 — the `coval_core` twin collapse is on 200 prompts, not 968

> `coval_core_2bA` and `_2bB` are scored on **200 of 968 prompts (21%)**. This round's `pair_agree`
> **skips** prompts an arm does not cover, so *"agreement exactly 1.000"* is a statement about the
> **200 shared prompts**. ⭐ The census's other pairs are between full-coverage arms and are
> unaffected, and the deduplicated counts (8→4, 11→6) stand — the twins collapse into `coval_core`
> either way. What needed the scope is the word *"identical"*.

## ⛔ The correction, first

Over the 96-arm population there are **14 effectively identical pairs** — arms agreeing at **exactly
1.000** on every prompt. **96 arms, 85 distinct objects.**

```
coval_core == coval_core_2bA == coval_core_2bB
generic    == generic_reprov
oracle_k4  == oracle_k4_oracle_kA == oracle_k4_oracle_kB      … 14 pairs in total
```

| extension | as counted (R1000/R1004) | **distinct** |
|---|---:|---:|
| `generic` | 8 | **4** |
| `genericpool16` | 11 | **6** |

⭐ **Roughly half the extension is the same object under another name.** Under `generic` it is
essentially **`coval_core` plus the `topw_k*` family** — a far more informative statement than
*"admits 9 of 96"*.

## The convergence, with both confounds sized

Membership decided on **half** the prompts, agreement measured on **the other half**. 5 partitions ×
3 calipers × 2 comparators = **30 cells, all reported**.

```
Δ  =  within-extension agreement  −  level-matched non-member agreement
   =  +0.0828   [+0.0499, +0.1169]     floor 0.0183     effect / floor = 4.5
```

⛔ **Two confounds, each removed and sized rather than argued away:**

| confound | why it would fake the result | size |
|---|---|---:|
| **level** | clause ② admits high-A2 arms, and two arms that agree with the human **must** agree with each other | **+0.0533** |
| **duplication** | duplicates agree at 1.000 **by construction** | **+0.0168** |

**The unmatched contrast (+0.1362) is a DERIVATION** — forced by the algebra of clause ② — and is
reported only to size the confound. **The estimate is the deduplicated, level-matched Δ.**

## Controls

| control | result |
|---|---|
| **POSITIVE** | a planted duplicate of `coval_core` agrees **1.000000**; a genuinely different arm agrees **0.523072**. The instrument sees identity **and** is not saturated |
| **DUPLICATION** | every cell computed twice, on 96 arms and on 85 distinct — only the second is an estimate |
| **NOISE FLOOR** | measured across 30 held-out cells, not assumed |
| **IDENTIFICATION** | checked **before** estimating: level-matching needs non-members overlapping the members' A2. It exists only because clause ③ excludes the high-scoring supervised arms regardless of level. Cells without overlap are recorded **UNIDENTIFIED**, never estimated |

⚠ **The positive control failed on its first run — for its own reasons.** I named `coval_core_2bA` as
"a different arm"; it is an effective duplicate, so the control was comparing the wrong two objects.
Repaired to assert the instrument's **range** (some pair must score < 1) rather than to trust an arm I
picked by hand. **The failure is what surfaced the duplicate census**, which turned out to matter more
than the control did.

## Two further bugs this round caught in itself

- **The half-corpus A2 used annotator[0] only**, while A2 everywhere else averages over **every**
  annotator — the *"two different draws compared as one"* mode. Repaired to a column subset of the
  all-annotator vector.
- **`genericpool16` cells were silently skipped**, because the comparator was looked up inside the
  size-record population and it has no size row. **The docstring promised 30 cells and 15 ran.** The
  comparator is a *reference*, not a candidate, and needs no size record. Repaired; the grid above is
  the full 30.

## ⚠ Impossible here, with what it would require

**Criterion validity — N/A.** Convergence is **not truth**: a family can agree because it shares a
bias. This is labelled a convergence test throughout. Truth would require an external standard the
release does not ship.

**Family, as distinct from level — N/A.** The level-matched comparison set is **dominated by the
supervised arms**, because that is *why* they clear the level. So matching controls **level** but not
**family**, and Δ > 0 admits two readings: members cohere, **or** supervised arms are unusually
heterogeneous among themselves. Both are stated; neither is picked.

## Alternatives considered

**Report the unmatched contrast.** Refused — it is forced by clause ②'s own admission rule, and
reporting an algebraic consequence as convergence is the trap this round was built around.

**Report Δ on the full 96 arms.** Refused once the census existed: duplicates agree at 1.000 by
construction, so that column measures the release's naming, not the definition's coherence.
