# The definition, stated once

`FORMULATION.md` is 2,000+ lines and is the **evidence record** — every clause that was written,
attacked and corrected, in the order it happened. It is titled *"stated once"* and it opens with a
correction, because the statement itself was never separated from its history.

**This file is the statement.** Numbers in it that are **anchored in the assertion table** are checked
against a committed artifact on every run by
[`assurance/definition_matches_the_record.py`](../assurance/definition_matches_the_record.py), and
those cannot drift from the evidence without the suite failing.

> ⛔ **CORRECTED 2026-08-06 (entry 1326). This sentence used to read "EVERY number in it is checked …
> so it cannot drift", and that was false by a wide margin — measured, not estimated.** The gate holds
> **340 assertions** capturing **254 distinct values** from this file. Against four definitions of
> "a numeric claim", the anchored share is:
> `every number token` **7.1%** · `bold` **13.6%** · `bold + decimal or "of N"` **13.0%** ·
> `bold + a claim verb on the line` **21.2%**.
> ⭐ **So the anchored share is bounded in [7.1%, 21.2%], and between 79% and 93% of this file's
> distinct numeric values are UNCHECKED.** Reported as a bound rather than a point because *"numeric
> claim"* has no crisp boundary — the loose end counts line numbers, round ids and dates, the tight
> end counts only bolded values on claim-bearing lines.
> ⚠ **Scope:** the unit is a distinct **VALUE**, not a distinct **claim** — two different claims that
> share the value `0.5` collapse to one, so the claim-level share is a different quantity.
> ⚠ **The extractor was blind twice before this was admissible**: it missed 48 anchored values that
> carry `+` signs or thousands separators, then 7 more using the Unicode minus `−` (U+2212). Both
> were caught by requiring it to see every value the gate already anchors.
> ⚠ **And these very numbers are themselves unanchored**, which is the honest shape of the finding
> rather than a defect hidden in it.
>
> ⭐ **SCOPE ADDED 2026-08-06 (entry 1327) — THE BOUND ABOVE IS ABOUT THIS FILE, NOT ABOUT THE
> DEFINITION.** Measured per section, coverage **declines monotonically with distance from the
> statement**: the **STATEMENT itself (this section) is 8 of 10 distinct values anchored = 80%, and
> the two that are not are `441` and `824` — round IDs in "R441" and "R824", not claims.** Excluding
> citations, **the statement is 8 of 8 = 100% anchored.** Statement + extension is **39.3%** (33 of
> 84), through the clause-table head **38.7%** (36 of 93), and the whole file **7.1%** (254 of 3,590).
> **So the guarantee holds exactly where the deliverable lives and decays through the evidence
> record** — which is the right shape and was not guaranteed in advance.
> ⚠ The statement's denominator is **10 values**, so 80% has coarse resolution; what is solid is the
> *list*, not the percentage. And entry 1326's "79–93% unchecked" remains true **of the file** and is
> misleading **of the definition** — a correct number reported without the scope over which it holds,
> which is G1's own opening line.

---

## The definition

> A **core** for a conversation is a small set of evaluation criteria, **producible from the
> conversation alone**, that
>
> **③** uses **no information from that prompt's own human labels** — not from the construction, not
> from any half of them, **and not by way of a rubric those same annotators wrote**; **and**
>
> **②** scores better, **under a named judge J**, than a size-matched criterion set that never read
> the conversation; **and**
>
> **④** scores better, under that same judge J, than **every rule computable from the response set
> alone** — **where a rule may be FIT on other prompts' human labels, and reads only the responses
> at inference** *(the permissive reading; R824 measured that the choice changes ④'s extension from
> 0 to 25 of 58 arms, so the clause is not well-formed without it)*.
>
> Its size, **under that same judge J**, is **greater than one**.
>
> *(Reported, not required: sizes **3 to 8 are not distinguishable** by this release.)*

### ⭐ THE SAME STATEMENT, WITH THE SCOPES R917–R926 MEASURED (added 2026-08-07)

**The clause text above is NOT edited** — it is anchored by
`assurance/definition_matches_the_record.py`, and a silent edit to a statement its gate keys on is
the one change that should never be made quietly (L81). What follows is the same definition with
what has since been measured attached to each clause.

⛔ **AND THE REASON THIS SECTION EXISTS IS A DEFECT IN THE GUARANTEE, NOT A TIDY-UP.** The anchoring
gate keys each assertion on the artifact it came from, so **it certifies CONSISTENCY and cannot see
CURRENCY**: the statement can match every artifact it cites and be wrong about every artifact it does
not. Measured by `assurance/a_statement_is_current_with_the_arc.py`, which reads the facts out of the
committed artifacts and requires the statement to say them: **5 of 7 were absent.**

**① `size > 1`** — **independently necessary, measured.** `0` of **120** label-blind size-1 arms
(4 orderings × 15 ranks × 2 coverage rules) clear clause ②, under either comparator; 240 cells
tested, 0 surviving BH (R925). The k=1 **oracle** does clear it, so clause ① is not implied by
clause ② (R924) — but that object is excluded by clause ③ anyway.
⚠ *Reported, not required:* sizes 3–8 remain indistinguishable.

**② the bar** — **it is a THRESHOLD on mean A2, not a comparison** (R922). Under both admissible
comparators the admitted set is exactly the top-N by mean A2: **0 inversions**, against **24** across
all 99 arms used as comparators, so the machinery *can* act as a comparison and here does not.
- **The comparator set has exactly 2 members** on this release — `generic` and `genericpool16`, the
  only arms whose selection is identical on every prompt and therefore prompt-blind by construction
  (R921). ⛔ **A third costs `968 × 4 × k` judge calls — NOT the constant 15,488 this line used to
  assert (R1027).** The old wording is withdrawn and replaced: `covalx/judge.py:151` is
  `build_prompt(criterion, reply)`, one call per (criterion, reply) pair, so the price is **linear in
  the criterion count** and the identity `cells = prompts × replies × k` holds with residual **exactly
  0 across all 74 fixed-k arms**. At full coverage: **k=1 → 3,872 · k=4 → 15,488 · k=16 → 61,952.**
  So `15,488` is a **k=4** arm's price quoted as universal — it **overstates** the cost of the small-k
  comparators most likely to be tried, and **understates by 4×** the cost of `genericpool16`, which
  the certified set already contains. ⚠ And the unit is **local GPU time** (`device_map="cuda"`,
  batch 32), not paid API spend; no runtime is claimed here. ⚠ **What does not change: R1026.** A
  cheaper comparator still has to be built and be prompt-blind, and none exists in this release —
  the cost was never the only obstacle, it was the one that was named, and it was named wrongly.
- **`generic` resolvably beats `genericpool16`**: margin **+0.009103 [+0.005730, +0.012488]** (R923).
  **Every published number in this arc used the weaker one.**
- **Calibration:** cut **0.5514** (28 admitted) under `genericpool16`; **0.5593** (24) under
  `generic`. A cut quoted without its comparator is unscoped.
- **Resolution 0.009956**, and **5** of the 28 admitted arms sit within that **resolution** of the
  bar (R923). **So the admitted set is 9 arms resolved + a boundary layer**, not a count.

**③ no prompt-specific labels** — **a PROVENANCE requirement, not a property of the artifact**
(R920, world **C_implies_B**). π (an arm's rank among all size-k subsets) separates label-consumers
from label-blind arms, but `R² = 0.9984` against the A2 margin: at the artifact level *"consumed the
labels"* and *"is simply better"* are the same observation. **The definition certifies a pipeline,
not a core**, and applying it to a core whose production is unknown is unsupported.
- **Its price decays monotonically in `k`**: 0.1164, 0.1029, 0.0915, 0.0856, 0.0691, 0.0552 for
  k = 1, 2, 3, 4, 6, 8, at every sampling cap (R926). **So ① and ③ guard the same failure from
  opposite sides** — ① excludes exactly the regime where ③ is cheapest to violate profitably.

**④ beats every response-only rule** — the permissive reading remains the one that makes the clause
well-formed (R824), but **"unchanged" is retracted**: ④'s reach is bounded, and the bound is a
property of the DESIGN rather than of the clause.
- **It is overlap-limited, not mean-determined** (R975). At a mean deficit held fixed at δ = 0.01,
  ④ stops removing an arm once that arm is strictly **above the floor on ~40–50% of prompts** — the
  point estimate is pinned by algebra and only the interval moves, widening 0.00255 → 0.01136 across
  the sweep. So an arm can sit below the floor **on average** and survive ④.
- **The bar has a closed form with no clause content and no corpus term** (R976):
  `φ* = (δ²·N / (z·STEP)² − δ/STEP) / 2`, registered before the run and landing within 1.5 grid
  steps on **13 of 14** measured cells across **N ∈ {242, 484, 726, 968} × δ ∈ {0.008…0.016}**.
  Measured φ*(968)/φ*(484) = 1.50 / 2.71 / 2.25 per seed against a registered 2.15.
- ⚠ **Therefore any statement of ④'s reach must carry `N` and `δ`.** R821's headline — the 0.01
  detection being finer than the design's half-split noise floor of 0.0067 — is a fact about a
  **968-prompt** design: at N = 242 the same δ is defeated at an overlap near 0.10.
- **Not established:** whether φ\* also depends on the corpus. Subsampling varies N only; the closed
  form needs no corpus term to predict the table, which is weaker than having measured a second one.

### ⛔⛔⛔ RETRACTED — R1005's CONVERGENCE FAILS THE NEGATIVE CONTROL R1005 DECLARED AND NEVER RAN (added 2026-08-07, R1007)

**The claim below — and the round above it that defended the claim — rest on a control that was
written into a docstring and never implemented.** R1005 declared:

```
NEGATIVE CTRL   shuffle the membership labels … ⚠ World it excludes: "any set of this size shows this Δ".
PLACEBO         Δ between two disjoint random halves of the NON-members must be ≈ 0.
```

`NSHUF = 200` is defined at line 74 and **used nowhere**; the only `permutation` call permutes
**prompts**. The committed artifact lists **one** control. ⭐ **The world R1005 named as excluded was
never tested.**

**R1007 ran it.** Against a **band-matched** null — random arms from the extension's own A2 band, so
level is fixed and only *which arms* is destroyed — Δ_real clears the 95th percentile in **6 of 30**
cells. And the survivors run the wrong way:

| caliper | clears the band null | mean band size |
|---:|---:|---:|
| 0.010 | **0 / 10** | 10.2 |
| 0.020 | **1 / 10** | 13.4 |
| 0.040 | **5 / 10** | 20.3 |

**Monotone: the cells that survive are the ones where level matching is LOOSEST.** A real effect is
clearest under the tightest matching. This one appears only when the comparison is relaxed — **the
signature of a band artifact.**

⛔ **SO: `Δ = +0.0828` IS WITHDRAWN. The extension is NOT established as a coherent family.** Any set
of that size drawn from that level band shows the same Δ.

**Controls making the retraction itself admissible** (a cheap attack that appears to kill a claim is
the most expensive error): **POSITIVE** — 6 literal copies score **0.8434** vs **0.6420** for a random
set of the same size, so the comparison can see coherence. **PLACEBO** — two disjoint halves of the
non-members, 1,000 draws: mean **−0.0001**, sd **0.0132**, exactly zero. **UNRESTRICTED null** — 18 of
30 clear it; reported beside the binding one, **never instead of it**, because it is the weaker test
and the flattering one.

⭐ **WHAT SURVIVES.** The **duplicate census** below (14 identical pairs, 96 → 85 distinct, extension
8→4 and 11→6) is a fact about the arms and is **unaffected**. **R1006's measurement stands** —
`indep_k` and `greedy_k` are the most homogeneous families — but **its purpose is moot**: it excluded
a rival explanation for an effect that is no longer established.

⚠ **The class of error, which is not "a number came out wrong":** a control was described, its
excluded world was named, and the headline was written as though the exclusion had happened. **A
docstring is a claim about what ran.** One grep for `NSHUF` found it. **No gate in `assurance/` checks
declared-versus-implemented** — there is one for a control that *cannot fail*, none for one that
*never ran*.

### ⭐ THE RIVAL EXPLANATION FOR THE CONVERGENCE IS EXCLUDED (added 2026-08-07, R1006)

R1005 reported Δ = +0.0828 and said it admitted **two readings**: members cohere, **or** the
level-matched comparison set — dominated by supervised arms — is unusually **heterogeneous** among
itself. The second is a claim about the supervised arms **alone**, so it needs no members, no
comparator and no level match. Within-family agreement, 85 distinct arms, 5,000 size-preserving
shuffles per family:

| family | n | within | null mean | z | rank |
|---|---:|---:|---:|---:|---:|
| **`indep_k`** (supervised) | 7 | **0.7663** | 0.6710 | **+3.24** | **1** |
| **`greedy_k`** (supervised) | 7 | **0.7511** | 0.6725 | **+2.68** | **2** |
| `coval_core` | 2 | 0.7297 | 0.6760 | +0.48 | 3 |
| `topw_k` | 15 | 0.7018 | 0.6715 | +2.05 | 6 |
| **`oracle_k`** (supervised) | 5 | 0.7016 | 0.6710 | +0.77 | 7 |
| `random_k` | 36 | 0.6970 | 0.6716 | +3.52 | 8 |
| `topabs_k` | 2 | 0.6405 | 0.6740 | −0.30 | 11 |

⭐⭐ **The two largest supervised families rank FIRST and SECOND of eleven.** The rival reading
required them to be unusually spread; they are the **most homogeneous families in the release**. **So
"the comparison set is heterogeneous" cannot explain R1005's Δ, and the convergence stands as member
coherence.**

⚠ **The BH column is driven by family SIZE and must not be read as homogeneity.** One family survives
BH at q = 0.05 — `random_k` — and it does so with a within-null gap of **+0.025**, while `indep_k`'s
gap is **+0.095** and does not survive. `random_k` has n = 36, so its null sd is 0.0072; `indep_k` has
n = 7 and a null sd of 0.0294. **BH answers "resolvably above its own null", which large families win
by construction.** The verdict above is a **rank** statement and does not rest on it.

⚠ **And the bottom tercile is entirely n = 2 families** (`gen`, `other`, `topabs_k`), whose
within-agreement is a single pair. *"Not in the bottom tercile"* is therefore a weak bar on its own —
which is why the claim above is the stronger, positive one: **ranks 1 and 2, at z = +3.24 and +2.68.**

⛔ **THE CONTRAST R1005 ACTUALLY ASKED FOR REMAINS UNAVAILABLE, and the count is why.** In the
members' A2 band [0.5593, 0.5698] there are **2 distinct** non-supervised non-members at caliper
0.020 and **5** at 0.040 — and they are `gen`, `generic`, `topw_k1`, `topw_k2`, `topw_k12`, i.e.
mostly the members' **own** family, which confounds in the opposite direction. **n = 2 and confounded
is not a design.** It would require a release with more arms in that band that are neither supervised
nor `topw`.

### ⭐⭐ THE EXTENSION CONVERGES BEYOND ITS SCORE LEVEL — AND ITS COUNT WAS INFLATED (added 2026-08-07, R1005)

**Two results, and the second corrects the section below it.**

#### ⛔ FIRST, THE CORRECTION: `9` and `12` counted the same arms twice

Over the 96-arm population there are **14 effectively identical pairs** — arms whose per-prompt
orderings agree at **exactly 1.000** on every prompt. `coval_core == coval_core_2bA ==
coval_core_2bB`; `generic == generic_reprov`; `oracle_k4 == oracle_k4_oracle_kA == …`. **The
population is 96 arms but 85 distinct objects.**

| | as counted (R1000/R1004) | **distinct** |
|---|---:|---:|
| `generic` | 8 | **4** |
| `genericpool16` | 11 | **6** |

⭐ **Roughly half the extension is the same object under another name.** R1004's *"admits 9 / 12"*
should be read as **4 / 6 distinct criterion-selection procedures**, and under `generic` the
extension is essentially **`coval_core` plus the `topw_k*` family**.

#### ⭐ SECOND: the convergence, with both confounds sized

Membership decided on half the prompts, agreement measured on the other half, 5 partitions × 3
calipers × 2 comparators = **30 cells, all reported**:

```
Δ  =  within-extension agreement  −  level-matched non-member agreement
   =  +0.0828   [+0.0499, +0.1169]     noise floor 0.0183     effect / floor = 4.5
```

⛔ **Two confounds, both real, both removed and sized rather than argued away:**
- **level** — clause ② admits high-A2 arms, and two arms that agree with the human *must* agree with
  each other. Unmatched Δ is **+0.1362**; the level effect is **+0.0533**. The unmatched number is a
  DERIVATION and is never the estimate.
- **duplication** — duplicates agree at 1.000 by construction. Full-population Δ is **+0.0996**;
  deduplicating costs **+0.0168**. Only the deduplicated column is an estimate.

⚠ **CONVERGENCE IS NOT TRUTH**, and this is labelled a convergence test throughout. A family can
agree because it shares a bias. **And the level-matched comparison set is dominated by the SUPERVISED
arms** — that is *why* they clear the level — so matching controls **level** but **not family**.
Δ > 0 could mean members cohere, or that supervised arms are unusually heterogeneous among
themselves; the round states both readings rather than picking one.

**Controls.** A planted duplicate of `coval_core` returns agreement **1.000000**, and the instrument
returns **0.523072** for a genuinely different arm — so it can see identity *and* is not saturated.
⚠ That control **failed on its first run for its own reasons**: the arm I named as "different",
`coval_core_2bA`, is an effective duplicate. Repaired to assert the instrument's *range* rather than
to trust an arm I picked by hand.

### ⛔⛔ UNDER `A1·consensus` THE DEFINITION EXCLUDES ITS OWN INSTANCE (added 2026-08-07, R1020)

R1019 left the cell that matters uncomputed: a target under which the definition admits nothing, at
the **96-arm** population rather than R288's 10. ⭐ **A1 was not reconstructed — it was copied from
R288's committed source**, `T["A1·annot"][n] = np.mean([float((c == h).all()) for h in HC[n]])`, so
R1019's hazard (*a target rebuilt in order to sweep it can be built to fail*) does not apply.

⭐ **THE TRANSCRIPTION CONTROL IS EXACT.** My `A1·annot` reproduces R288's committed per-arm values at
**Δ = 0.000e+00** on all 9 shared arms — `coval_core` 0.066476221325849, `topw_k4` 0.065973341200429,
`generic` 0.059203400221706. **It is R288's statistic, not a lookalike.**

| target | extension (96 arms) | `coval_core` in it |
|---|---:|---|
| `A2` (this arc throughout) | **9** | yes |
| `A1·annot` | **9** — the same nine | yes |
| **`A1·consensus`** | **4** — `coval_core_2bA`, `coval_core_2bB`, `topw_k6`, `topw_k8` | **NO** |

⛔⛔ **SCOPED BY R1021 — THE CONTRAST WITH THE TWINS IS THE IMPUTATION, NOT THE TARGET.** The wording
this section first carried was *"the definition admits the released core's TWINS and excludes the core
itself"*. **That is withdrawn and replaced, not annotated beside.**

On the **200 prompts the twins actually cover**, where nothing is imputed for anyone, **core and twins
are admitted or excluded TOGETHER — and all three are EXCLUDED** (`generic` Δ +0.0450 [−0.0100,
+0.1000]; `genericpool16` Δ +0.0400 [−0.0150, +0.0950], identical for all three). ⭐ **That identity is
a DERIVATION**: R1005 measured the twins' outputs identical to the core's there at agreement exactly
1.000, so a statistic computed from those vectors could not differ. At 968 the twins are admitted only
because the loader fills their missing **768** values with the twins' **own mean** — mean |Δ| from the
core **0.2057**.

⭐ **What survives, and it is the weaker claim:** under `A1·consensus` the released core is **not
admitted** — `generic` lo −0.0041, `genericpool16` lo +0.0000, neither clearing. **The target effect on
the core is real. The contrast with its twins is not.**

⚠ The 200-prompt intervals are wider by construction (n = 200 vs 968), so *"excluded together"* there
is not a tie the design could not resolve — the intervals are printed above. And what the twins would
score on the other 768 is **unknowable**: they were never run there.

⭐⭐ **GENERALISED BY R1022 — THE `A1·consensus` EXTENSION IS COVERAGE-DRIVEN, AND THE EFFECT IS
MONOTONE IN HOW MUCH IS IMPUTED.** R1021 measured this on the two twins. It is not a fact about those
two arms. Putting the release's most extreme arm in front of the same operator — `provenance_probe`,
**4 real prompts of 968, 99.6% of its vector filled with its own mean** — it **clears clause ②′ against
BOTH comparators under `A1·consensus` at lo +0.3476**, while the *same* arm is **rejected under `A2` at
lo −0.1335**. The margin is monotone in real coverage:

| arm | real prompts | imputed | `A2` | `A1·consensus` |
|---|---:|---:|---:|---:|
| `provenance_probe` | 4 | 99.6% | −0.1335 | **+0.3476** |
| `coval_core_2bA` | 200 | 79.3% | +0.0095 | **+0.0020** |
| `coval_core` | 968 | 0.0% | +0.0078 | **−0.0042** |
| `topw_k4` | 968 | 0.0% | +0.0054 | **−0.0021** |

(`lo` = the worse of the two comparators; > 0 means admitted by ②′.) **Under the exact-match target,
broadcasting an arm's own mean over unmeasured prompts is worth more than any real signal it could
carry** — so an `A1·consensus` extension is a statement about coverage before it is one about cores.
⚠ `provenance_probe` is **not** in R1000's population and **not** in ③'s size record, so it could never
enter a committed extension; it is a **declared counterfactual on the OPERATOR**, not a candidate.

⭐ **And the threshold itself cannot change any other answer — that is forced, not measured.** An arm's
imputed vector depends only on its **own** observed values, and each comparator is a single scored arm
loaded from its own file, never a pool recomputed over surviving candidates. So `admitted(τ) =
admitted(τ=1) − removed(τ)` **exactly**, verified at all 8 (target, τ) cells as a bookkeeping check.
Coverage takes only **four** distinct values here — {4, 200, 398, 968} — so the curve below is
**complete, not sampled**: `A2` 9 → 9 → 7 → 7 and `A1·consensus` 4 → 4 → 2 → 2.
⚠ The `200` is a bare literal in **22 round scripts**, 21 with no nearby comment. R1022 is the first
round to ask what it decides. **That is a finding about the programme, not about the release.**

⛔⛔ **SCOPE LIMIT ON THE OPERATOR ITSELF, MEASURED BY R1023 — CLAUSE ②′ IS CALIBRATED ONLY ON
FULL-COVERAGE ARMS.** Censoring is an intervention, so this is identified by construction rather than
adjusted for: take a full-coverage arm, hide all but `k` prompts, impute exactly as the committed
loader does, and compare it **against itself** — the true difference is then **exactly zero**, and
every admission is a false positive with no model involved.

| k real prompts | 4 | 25 | 100 | **200** | 400 | 800 | 968 |
|---|---:|---:|---:|---:|---:|---:|---:|
| false-admission rate | 0.45–0.51 | 0.33–0.38 | 0.21–0.28 | **0.17–0.21** | 0.07–0.16 | 0.04–0.05 | **0.000** |

**At the guard's own `k = 200`, an arm with a true difference of exactly zero is certified as
resolvably better ~21% of the time, against the operator's nominal 2.5% — eight times its stated
level.** Binomial SE at 300 draws is ±0.009, so the gap is not a resolution artifact.

⭐ **And the mechanism predicts the whole curve, so this is understood rather than merely observed.**
Imputing `968−k` cells with the observed mean leaves that mean exactly unchanged but makes those
cells **constants**, and the bootstrap reads a constant as zero-variance when it is in fact an
*estimate*. The ratio `SD_true / SE_boot` is closed-form (`sd(v)` cancels): 2.20 at k=200, predicting
level 0.186 against 0.195 measured; worst gap over the 8 censored levels **0.024**.
⚠ A consistency check, **not** an independent confirmation — both sides use the same normal
approximation, so it rules out a coding artifact and not a shared model error.

⚠ **Censoring is not conservative in either direction.** At k=200 a truly-*admitted* arm fails 24–31%
of the time **and** a truly-*excluded* arm is admitted 51% of the time. It destroys the verdict both
ways, so a partial-coverage admission cannot be read as "probably right, just noisy".

⭐ **What this buys:** the threshold is no longer a habit. The null curve is a **price list** — at the
operator's own nominal level nothing below full coverage qualifies; at a relaxed 5% the curve reaches
it only between k=800 and k=968. It also **explains** R1011's withdrawal of the twins quantitatively
rather than retracting anything further.

⭐⭐ **AND R1024 SETTLES WHAT TO DO ABOUT IT: THE REPAIR IS AN ESTIMATOR CHANGE, NOT A BETTER
CONSTANT — THE COVERAGE THRESHOLD IS THE WRONG INSTRUMENT AND IS DELETABLE.** The realizable fix
needs no new machinery: **do not impute.** Bootstrap the `k` observed prompts and nothing else, which
is what R1021 did by hand when it restricted the core/twin comparison to the 200 shared prompts.
Measured as one-sided coverage `P(lo ≤ Δ_true)` against the true full-population difference, nominal
0.975:

| estimator | k=4 | 10 | 50 | 200 | 400 | 968 |
|---|---:|---:|---:|---:|---:|---:|
| impute (committed) | 0.48–0.59 | 0.54–0.60 | 0.61–0.69 | **0.83–0.86** | 0.92–0.97 | 1.000 |
| **observed-only (fix)** | 0.92–1.00 | 0.95–0.99 | 0.96–0.98 | **0.98–1.00** | 0.99–1.00 | 1.000 |

**Worst observed-only coverage across every real pair at k ≥ 10 is 0.953**; even at k=4 it is 0.920.
So a minimum-`k` threshold answers a question that exists **only because of the imputation**.
⚠ The fix is **conservative, not exact** — it over-covers slightly at large k, costing power and
never correctness; the committed estimator errs in the other, unforgivable direction.
⚠ **No committed extension figure moves.** Only 4 arms are partial (the twins and the `promptecho`
pair), `promptecho` is in no extension, and R1011 already withdrew the twins — so the blast radius
was closed before this measured why.
⚠ **This prices the OPERATOR, not the TARGET.** Whether `A2` or `A1·consensus` is the right thing to
admit on still needs an external criterion this release does not carry.

⛔⛔ **AND THE `cross-release` REGISTER LINE IS RIGHT FOR THE WRONG REASON — R1028.** R802 declared it
**FALSE** (30 distinct impossibility claims, 1 false, base rate 0.0333) because `data/utterances.jsonl`
exists at 68 MB and 22+ rounds open it. ⚠ **That instrument measured a FILE; the claim asserts a
RELEASE**, and a second release implies more files while more files do not imply a second release.

Comparing the **populations** instead: overlap is **exactly 0 on all three join keys** — conversation
id, prompt id, and prompt **text** (1,078 scored prompts vs 8,011 conversations / 26,673 distinct
prompts). So a second, **genuinely disjoint** population does exist. **But it carries `score` and
`if_chosen` and NO criterion vocabulary at all.**

⭐ **So the line stands and its stated reason does not.** The requirement that actually binds is not
*"another release"* — R802 refuted that — but **"another release CARRYING A CRITERION VOCABULARY"**,
which neither side ever wrote down. A criteria-based definition cannot be validated against a
population that has no criteria, however independent it is.
⚠ Controls: the overlap instrument separates a **constructed** disjoint split (0) and returns exactly
**1.0000** for the scored release against itself, so the measured 0 is a measurement and not silence.
⭐ And `responses per prompt = [4]` read here directly **independently confirms** the `replies = 4`
that R1027 inferred from cell counts — different route, same value.

⛔⛔ **AND THE REGISTER CANNOT BE AUDITED FOR WHETHER ITS REQUIREMENTS ARE RIGHT — R1029, UNVERIFIED
ON IDENTIFICATION.** The obvious follow-up is to ask how many other entries name the requirement
R1028 falsified. **That question is not identified from what the register stores.** Three instruments
give three denominators — R472's committed tabulation **17**, a token matcher **9**, a direct phrase
regex **7** — and the spread is not noise: **the requirement TYPE was never stored as a field.** R472
derived its tabulation with a phrasing classifier and said so in its own README, verbatim: *"the
instrument's unit is PHRASING, the claim's unit is NAMING A REQUIREMENT."*

⭐ **The repair is structural, not analytic: store the requirement type when the entry is written.** A
register whose requirements must be recovered afterwards by a classifier cannot be audited for
whether those requirements are **right** — which is the one audit that separates a specification from
a list of excuses.
⭐ **The numerator survives even though the share does not.** At least **4** committed entries
(**R450, R451, R453, R464**) name the falsified requirement *and* guard a criteria-based check, so
R1028's repair applies to them whatever the true denominator is. **A lower bound is a result; a share
over a guessed population is not.**
⚠ R472 is **extended, not contradicted** — it measured whether a requirement is NAMED (46 of 100);
this asks whether a named one is RIGHT, and finds the question unanswerable as stored.

⛔⛔ **AND THE GATE THAT EXISTS TO CATCH THIS PASSES WHILE IT HAPPENS — R1030.** Five consecutive
rounds of this arc proposed NEXT work that already existed, and `assurance/next_gradient_is_new.py`
was built for exactly that after R858 measured **7 of 26 (0.269)**. It exits **0** throughout, because
it is a **self-test, not a monitor**: it validates its searcher on four *historical* cases and never
points it at the NEXT lines being written. On the live population the rate is **5 of 7 = 0.714**.

⛔ **And the gate is STRUCTURALLY unable to find the dominant form of prior art here.** Round
directories are `R472_the_register_half_complies` — **underscores** — while a NEXT is prose, with
**spaces**; `NG.search` compiles `re.escape(term)`, so an exact match can never bridge them. ⚠
Normalising separators is a **trade, not a fix** — it breaks the gate's own underscore-literal cases —
so the instrument must search **both** corpora.
⚠ **0.714 is a LOWER BOUND**: only the HIT direction is sound, since the search terms are
author-chosen, and it survived four self-attacks that each could only lower it (the first figure was
1.000, inflated by searching this round's own file and by counting the round that *acted* on each
NEXT). ⚠ And **subject novelty is not substantive novelty** — R1027–R1029 each produced a real result
on an existing subject; the cost is the part of each round spent rediscovering prior art.

⛔⛔ **AND THE REPAIR R1030 NAMED WAS BUILT AND MEASURED TO CATCH 0 OF 4 — R1031.** `preflight.py`
has accepted `--next` all along; the committed `preflight_log.jsonl` records `next_checked` at **4 of
15**, split cleanly — **R1019–R1021: 4 of 4 · R1022–R1030: 0 of 11** — at exactly the point the
session's context was compacted. **The capability never degraded; the memory of it did.** ⚠ 0.267
lands beside R858's 0.269 by **coincidence**; no mechanism is claimed.

⛔ A prior-art gate matching NEXT text against **round directory names** was then built and run
against the **four real committed NEXT lines** it exists to catch: **0 of 4**. ⚠ **And its calibration
PASSED — because I wrote the positive control's text to contain R472's title words.** The real R1028
NEXT says *"whether each entry names a requirement"*; R472's title says *"the register half
complies"*: **same subject, different words.** *A control validated only against cases you invented is
validated against your imagination* — committed while building the repair for a different failure.

⭐ **Prior art in this repository is SEMANTIC, and no lexical instrument reaches it.** Substring
matching, path indexing, separator normalisation and title-word overlap each fail on the same
title-vs-prose vocabulary gap, and a permissive threshold manufactures 7/7 (R1030). The gate is
therefore **deliberately NOT wired**: measured recall 0/4 exiting 0 would install §4's *check that
cannot fail* on purpose. **This defect has no mechanical detector**, and the habit that did catch it
was lost to compaction rather than to disbelief.

⚠ **AND R288's ∅ IS NOT REFUTED BY THIS.** The **target** is identical (Δ = 0). But R288 swept
**clause ② alone** against its own `_blind4`/`_blind15` references over **10** arms; this is **②′∧③**
against R921's certified comparators over **96**. **Different admission rule AND different
population** — calling it a refutation would be the naming-collision error R1019 caught one round
earlier, made in the opposite direction. ⭐ The positive control proving the target matches is exactly
what makes the remaining difference legible.

⚠ **The closest-arm diagnostic ranges over ALL arms, not ③-eligible ones** — it reports `oracle_k4`,
which fails ③ and is in no extension. It answers *"how far is the best ②-candidate"*, not *"how far is
the best core candidate"*.

⚠ `top1·mean` is **not swept** — a choice, not a limit: its R288 answer is about **which arm**, not
about emptiness, so folding it in would make the round about two questions.

### ⛔ EVERY EXTENSION FIGURE IN THIS ARC IS **A2's** ANSWER, AND NOTHING SAID SO (added 2026-08-07, R1019)

⛔ **PRIOR ART, AND IT IS THE SCOPE.** R558 recorded, from R288's committed `target_sweep.json` —
**968 prompts, six targets, four distinct admitted sets**:

| target | admits |
|---|---|
| `A2·annot`, `A2·consensus` | `coval_core`, `topw_k4` |
| `A1·annot`, `A1·consensus` | **∅ — nothing** |
| `tau·mean` | **`coval_core` alone** |
| `top1·mean` | `topw_k4` — **not the released core** |

**That sweep is over 10 arms.** This arc spent nineteen rounds reporting an extension over **96** —
*"9 arms, 4 distinct objects"* — **and never named the target.**

⭐ **What this round adds:** the CURRENT formulation ②′∧③, over the full 96 arms, under **A2** and
under a **per-annotator Kendall tau-b** — **identical, 9 arms, 0 either way.** So between those two
targets the extension is stable.

⛔⛔ **AND MY tau IS NOT R288's tau.** R288 records `coval_core` **alone** under `tau·mean`; this
round's tau-b gives the same 9 as A2. **Same name, different statistic** — R288's is a tau against a
**mean ranking**, this is a **per-annotator** tau averaged, at a different population (10 vs 96).
⚠ **The positive control validated the A2 branch ONLY** — it reproduces R288's `A2·annot` answer on
R288's own subset and **licenses nothing about tau**, which is exactly the blind-spot case the
standard names. **So R288's tau result is neither reproduced nor contradicted here.**

⚠ **A1 and top1 are NOT recomputed.** They need scoring conventions this round would have to
reconstruct, and *reconstructing a target in order to sweep it is how a specification curve becomes an
invention.* R288's committed answer stands for them, at its own population of 10.

⭐ **The correction that follows regardless of the stability result:** the extension figure carries a
target, and it is **A2**. R288's sweep shows at least one target under which the definition admits
**nothing**, and one under which it excludes **its own instance** — so the label is not decoration.

### ⛔⛔ THE BELONGING CLAUSE FAILS TWICE OVER — NOT EVALUABLE, AND IMPLIED BY ② WHERE IT IS (added 2026-08-07, R1017)

R1016 left discriminativeness able to support a **belonging** clause. Its natural form is
self-referential and mentions no rival:

> **⑤** an arm belongs iff it discriminates **resolvably more than the same criteria on the wrong
> prompt** — i.e. it beats **its own sham**.

⛔ **FIRST FAILURE — IDENTIFICATION.** A sham must be **SCORED**, not computed: misdirecting criteria
changes which `(criterion, response)` pairs exist, so a sham's satisfaction matrix cannot be derived
from its parent's. **⑤ is evaluable for 4 of 96 arms — 4.2%.** A clause that cannot be applied to 96%
of candidates is **not a clause**. Making it one would mean running the judge on a misdirected version
of every candidate, priced at **`968 × 4 × k` judge calls per new scored object** — for the k=4 arms
at issue here that is **15,488**, but ⚠ the figure is **not a constant** and the flat quotation of it
elsewhere is corrected above (R1027).

⛔ **SECOND FAILURE — AND IT IS INDEPENDENT.** On the 4 arms where ⑤ *can* be evaluated:

| | belongs | does not belong |
|---|---|---|
| **clause ②** | `coval_core`, `topw_k4` | **0** |
| **not clause ②** | `gen`, `promptecho` | **0** |

**Nothing clause ② admits fails belonging, and belonging admits two more.** So ⑤ is **strictly weaker**
on this sample — implied by ②, and stating it would be decoration. ⚠ **On 4 arms this is a bound from
a handful, not a law** — the same limit as the identification result, seen from the other side.

**Controls.** `coval_core` passes ⑤ at +0.013993 [+0.012842, …]. **Every sham, treated as a candidate,
FAILS ⑤ against its parent** — the direction that matters, because a belonging test a sham passes is
not a belonging test. An arm against itself returns exactly 0 and fails the strict `lo > 0`, so the
clause is not degenerate.

⭐ **So the arc's answer on additional clauses is now negative on both available routes**: text-only
properties are closed (R1014), and the one pairing-dependent candidate is post-hoc (R1015), measures
belonging rather than merit (R1016), and is neither evaluable nor additive (R1017). **The formulation
stands at ②′ ∧ ③**, with size and margin reported.

### ⭐⭐ WHAT DISCRIMINATIVENESS ACTUALLY MEASURES: BELONGING, NOT MERIT (added 2026-08-07, R1016)

R1015's candidate was post-hoc — chosen after `topw` was named as the rival. The pre-registered form
fixes the quantity first and defines the sets it *should* separate **without mentioning `topw` or
`coval_core`**:

| pre-registered LOW set | reason it is named, from the release's construction | result |
|---|---|---|
| every `*_sham` arm | criteria pointed at the **wrong** prompt | **5 / 5 below** — and **5/5 resolvably below their own parent** |
| every `random_k*` arm | criteria drawn at **random** from the pool | **18 / 38 (47%)** — chance |

⭐⭐⭐ **The split is the finding.** Misdirected criteria fall, resolvably, every time:
`coval_core_sham` −0.013993, `topw_k4_sham` −0.010233, `full_sham` −0.010842, `promptecho_sham`
−0.011653, `gen_sham` −0.006752. **But criteria drawn at random from this prompt's own pool are as
discriminative as anything else.**

⛔ **So the quantity tracks whether criteria BELONG to this prompt — not whether they are GOOD.** It
falls only when the criteria come from *another* prompt. **That bounds what any clause built on it
could claim**, and it was invisible from R1015's comparison alone, which only ever contrasted arms
that were all on the right prompt.

⚠ **The verdict string of this round's first run was not a computation** — it printed *"the LOW sets
do not sit below (shams 5/5, …)"*, self-contradictory, because it collapsed two pre-registered
predictions into one sentence and described both with the text of the failing one. Each prediction now
carries its own verdict and the world is composed from them.

**Controls.** The core−sham difference reproduces R1015's **+0.013993** to 1e-6, so this is the same
quantity; self-comparison is exactly 0; the deterministic pair is exactly 0 with interval width
**0.00000000**, the measured floor.

⚠ **This does not show the excluded objects should be excluded in any absolute sense.** The LOW sets
are named from the release's own construction — a sham is misdirected *by definition*, a random draw
is random *by definition* — which is the closest thing to a reason available without an external
standard.

### ⭐⭐⭐ A PAIRING-DEPENDENT QUANTITY THAT DOES SEPARATE — AND IT IS POST-HOC (added 2026-08-07, R1015)

R1014 closed the text-only class: content must read the criteria AND their own prompt. R1011 showed
clause ②'s metric cannot rank the instance above `topw_k4`. ⭐ **A different pairing-dependent
quantity can.**

**Criterion DISCRIMINATIVENESS** — the variance of a criterion's satisfaction across *this prompt's
own* responses, averaged over criteria then prompts. It reads **no human labels**, so it satisfies
clause ③ automatically and is independent of the comparator.

| arm | discriminativeness | Δ (core − arm) | lo | hi | resolvable |
|---|---:|---:|---:|---:|---|
| **`coval_core`** | **0.030628** | — | | | |
| `topw_k3` | 0.025345 | +0.005283 | +0.004300 | +0.006245 | **yes** |
| `topw_k4` (+ both dets) | 0.025579 | +0.005050 | +0.004176 | +0.005926 | **yes** |
| `topw_k6` | 0.025683 | +0.004945 | +0.004135 | +0.005746 | **yes** |
| `topw_k8` | 0.025753 | +0.004876 | +0.004097 | +0.005658 | **yes** |

**Resolvable against all six.** The released core's criteria discriminate among the prompt's own
responses more than a top-weight selector's do.

⭐ **THE CONTROL THAT MAKES IT ADMISSIBLE.** Discriminativeness must **drop** for the sham — the same
criteria on the **wrong** prompt — or the quantity is text-only by R1014's argument and the round is
void. It drops by **+0.013993 [+0.012817, +0.015174]**. ⭐⭐ **And the pairing effect is ~2.8× the
family effect** (0.0140 vs 0.0050), which is the scale worth carrying.
Self-comparison is exactly 0; the deterministic pair `topw_k4_detA`/`_detB` is exactly 0, and its
interval width — **0.00000000** — is the measured floor.

⛔⛔ **AND IT IS POST-HOC, WHICH THE ARC MUST NOT FORGET.** The quantity was chosen *after* R1011
identified `topw` as the rival it needed to exclude. **A property selected because it excludes the
known rival is the "definition describes the instance" failure with a better metric.** What would
make it a clause rather than a fitted separator: a reason to require discrimination that does not
mention `topw`, and an admissible object it excludes **for that reason**. **Neither is established
here**, and the finding is recorded as a **candidate**, not a clause.

⚠ Two further bounds. **A discriminative criterion is not thereby a good one** — this asks whether the
quantity separates, never whether separation means quality. And **every satisfaction value routes
through the release's judge**, so it is a claim about what that judge scores.

### ⭐⭐ THE TEXT-ONLY CLASS IS CLOSED — THE INSTANCE'S SHAM IS AN EXACT DERANGEMENT (added 2026-08-07, R1014)

R1013 withdrew size on the instance's evidence (R986: 43 = 43) but could not check the instance's
criteria directly — `core_coval_core.json` is not on disk. ⭐ **They are in the RELEASE**:
`data/conversation_rubrics.jsonl`, key `coval_core`, via `covalx.judge.load_join`. Recovered and
compared to `coval_core_sham`:

| | |
|---|---|
| multiset of criterion **sets** identical | **True** — 0 sets only in the core, 0 only in the sham |
| prompts where the sham holds the core's **own** set | **0 of 968 (0.0%)** — a **derangement** |
| `size_dist` | `{2:1, 3:42, 4:925}` **both** |
| `mean_chars` · `mean_words` · `mean_unique_criteria` | **348.686 · 49.5537 · 3.954545, both** |

⭐⭐⭐ **So the sham is exactly the released core's criterion sets, permuted with no fixed point.**
Every property computable from the criteria **text alone** is identical between them **by
construction** — and therefore **no text-only property can be definitional content for this object.**
R1013's withdrawal reaches the instance in full, and the class is **closed**, not merely doubted:
size, size residual, size variability, vocabulary, length **and** within-set redundancy (R990's
finding, which is text-only) are all ruled out as clauses.

**Controls.** The size recovered from the release reproduces R986's committed decomposition exactly —
min 2, max 4, **43 prompts off the cap = residual 43** — so this is the object R986 measured. A
runtime-assembled key yields no criteria, so "the multiset differs" could not have come from a
mis-keyed lookup returning empty. The core against itself is identical.

⭐ **What this leaves, positively.** A2 depends on the **pairing** and is *not* shared — the core beats
its own sham by **+0.0709 [+0.0615, +0.0801]**. **Definitional content must read the criteria AND
their own prompt together.** That is what clause ② does, and it is now the only place content can live.

### ⛔ SIZE AND ITS RESIDUAL ARE WITHDRAWN AS CANDIDATE CLAUSES — THE SHAM SHARES THEM (added 2026-08-07, R1013)

R1011 left the definition unable to rank its own instance. The first candidate for a separating clause
was R986's size **residual** — the prompts whose realised size is not explained by the cap and the
pool. `coval_core` has **43**; every `topw` in the extension has **0**; only **6 of 96** arms have any.

⛔ **And `coval_core_sham` has 43 too.** All six residual-bearing arms come in arm/sham pairs with
identical residuals — `coval_core` 43 / `coval_core_sham` 43, `gen` 2 / `gen_sham` 2 — and the sham's
own size distribution is `{2:1, 3:42, 4:925}`, the same 43 non-cap prompts. **A property a sham shares
cannot distinguish a core from the same criteria misapplied**, so **size, the size residual and size
variability are withdrawn.**

⚠ **The sweeping form of that argument was REFUTED by this round's own measurement.** I claimed every
text-only property is shared by construction. Over the three arm/sham criteria pairs on disk:

| pair | size structure | text volume |
|---|---|---|
| `promptecho` | same | same |
| `topw_k4` | same | same |
| **`gen`** | same | **differs** (mean_chars 241.0568 vs 240.7169, ~0.14%) |

**Size structure held on all three; text volume did not.** So the argument holds **per arm**, is not a
theorem, and **vocabulary and length are NOT withdrawn** — they need their own test.

⛔⛔ **And the scope that matters most: `coval_core`'s own criteria file is not on disk**, so the
pairwise comparison runs on arms **other than the instance**. The instance's evidence is R986's
committed residual — **43 for both core and sham** — which is the candidate clause's own test and is
what the withdrawal rests on.

⭐ **What the withdrawal leaves standing.** A2 depends on the **pairing** and is *not* shared: the core
beats its own sham by **+0.0709 [+0.0615, +0.0801]**. **So definitional content that survives a sham
must read the criteria AND their own prompt together** — which is what clause ② already does.
⚠ R990's non-redundancy is text-only and falls under the same doubt, but is **not withdrawn here**: it
was never measured on an arm/sham pair, and asserting it without that measurement would be the
sweeping claim this round just refuted.

### ⛔⛔⛔ THE DEFINITION CONTAINS THE RELEASED CORE WITHOUT SINGLING IT OUT (added 2026-08-07, R1011)

After every repair in this arc, the extension under ②′ is **9 arms, 4 distinct objects**:
`coval_core` and `topw_k` at k ∈ {3, 4, 6, 8}. **Paired A2 differences inside that extension**, all
arms at full 968-prompt coverage, 8,000 cluster-bootstrap draws:

| admitted arm | Δ (core − arm) | lo | hi | resolvable |
|---|---:|---:|---:|---|
| `topw_k3` | +0.0033 | −0.0029 | +0.0095 | **no** |
| `topw_k4` | +0.0023 | −0.0037 | +0.0084 | **no** |
| `topw_k4_detA` / `_detB` | +0.0023 | −0.0037 | +0.0084 | **no** |
| `topw_k6` | +0.0024 | −0.0032 | +0.0079 | **no** |
| `topw_k8` | +0.0072 | +0.0013 | +0.0130 | core better |

⭐⭐⭐ **5 of 6 are not resolvably ordered against the instance.** The definition **admits a set in
which the released core has no special status** — it *contains* the core and does not *single it
out*. **That is "the definition describes the instance" read from the other side:** the clauses were
written from one object and cannot rank that object above the trivial family they also admit.

**Controls.** `coval_core` beats `random_k4_s0` by **+0.0738 [+0.0646, +0.0829]** — the instrument
can order. The **sham** (`coval_core_sham`, ingredient inverted) is beaten by **+0.0709 [+0.0615,
+0.0801]**. `topw_k4_detA` vs `_detB`, a deterministic pair, returns **exactly zero with a degenerate
interval** — the measured noise floor of this design on a known-zero effect. Self-comparison is zero.

### ⭐ THE CUT SURVIVES THE IMPUTATION — THE COUNTS DO NOT (added 2026-08-07, R1012)

R1011 found two extension arms scored on 21% of the corpus. **The load-bearing question is whether the
CUT depends on them**, because every round in this arc pins its wiring control to R922's cut at 1e-9.
Recomputed with the same operator, same seed, same 8,000 draws, one population change:

| comparator | population | cut | n | argmin |
|---|---|---:|---:|---|
| `generic` | full | **0.5593110792** | 24 | `topw_k8` |
| `generic` | **minus partial-coverage** | **0.5593110792** | **22** | `topw_k8` |
| `genericpool16` | full | **0.5513543392** | 28 | **`generic`** |
| `genericpool16` | **minus partial-coverage** | **0.5513543392** | **26** | **`generic`** |

⭐ **The cut does not move — Δ = 0.0000000000 under both comparators**, and the argmin is a
full-coverage arm in each. **So the arc's calibration number is not an artifact of the imputation.**

⛔ **The COUNTS are.** `24 → 22` and `28 → 26`: **two of each committed count are partial-coverage
arms.** Any statement quoting *"24 admitted"* is quoting a count with two imputed members.

⭐⭐ **And a cross-check falls out of the argmin column.** Under `genericpool16` the cut is set by
**`generic`** — the prompt-blind arm R1009 found admitted. Two rounds reaching the same object by
different routes: the arm that should not qualify is the one defining the boundary.

**Controls.** The full-population recomputation reproduces R922's cut **and** count at 1e-9 under both
comparators — without which no difference here would mean anything. Excluding the **empty set**
reproduces the full result. Excluding the two **highest-A2** arms (never the argmin) leaves the cut
exactly unchanged, which is what distinguishes "removing arms moves the cut" from "removing *these*
arms moves the cut".

⚠ **What cannot be done here:** recomputing what the partial arms' A2 *would* be with real scores.
Those 768 prompts were never scored for them — that is the defect, not a gap in the round. It would
require scoring them on the full corpus.

### ⛔ AND TWO EXTENSION ARMS WERE ADMITTED ON 79% IMPUTED DATA

The first negative control used `coval_core_2bA`, which R1005's census reports as agreeing with
`coval_core` at **exactly 1.000**, so their A2 difference had to be zero. It came back
**−0.0033 [−0.0122, +0.0051]**, and the diagnosis is a defect rather than a bug:

| arm | prompts scored |
|---|---:|
| `coval_core` | 968 / 968 |
| **`coval_core_2bA`**, **`_2bB`** | **200 / 968 (21%)** |
| `promptecho`, `promptecho_sham` | 398 / 968 (41%) |
| all other 92 arms | 968 / 968 |

**The committed A2 loader fills missing prompts with the arm's OWN MEAN**
(`np.nan_to_num(v, nan=np.nanmean(v))`, guarded only by `< 200`). So the two twins entered R1000's
extension with **79% of their A2 vector imputed**, and R1005's census figure of 1.000 is a statement
about the **200 shared prompts**, not about 968 — its `pair_agree` skipped missing prompts.

⭐ **The consequence is bounded and states itself:** deduplication removes both twins, and the **4
distinct objects are all at 968/968**. So R1004's count of **9** was inflated by duplication **and**
by imputation; the **distinct** figure is clean, and every number in the table above is
imputation-free.

### ⛔⛔⛔ THE FORMULATION ADMITS AN ARM THAT NEVER READS THE CONVERSATION — AND THE REPAIR (added 2026-08-07, R1009)

**Read the extension arm by arm and `genericpool16`'s contains `generic` and `generic_reprov`.**
R921 certified `generic` as **prompt-blind**, and clause ② is *"resolvably beats a NAMED prompt-blind
comparator."* ⭐ **So under one certified comparator, the other certified comparator qualifies as a
core.** A criterion set that never reads the conversation is admitted by the definition of a core.

| comparator | prompt-blind arm | Δmean | lo | hi | admitted |
|---|---|---:|---:|---:|---|
| `generic` | `genericpool16` | −0.0091 | −0.0125 | −0.0057 | no |
| **`genericpool16`** | **`generic`** | **+0.0091** | **+0.0057** | +0.0125 | **YES** |

**`lo = +0.0057` — resolvable, not marginal.**

⭐ **THE MECHANISM.** R921's two certified comparators are **not of equal strength**: `generic`
resolvably beats `genericpool16`. Clause ② says *"a NAMED prompt-blind comparator"* and **never says
which** — so naming the weaker one lets the stronger one through. **That silence is the defect**, and
it is the standard's own test answered badly: *name an admissible object this clause excludes.*
Clause ② excludes 68–72 arms and does **not** exclude the comparator it is defined against.

⛔⛔ **AND THE REPAIR WAS COMMITTED AT R921 AND NEVER ADOPTED (R1010).** R921's artifact carries
**`survives_all_legitimate` (24 arms)** beside `admitted_by_at_least_one_legitimate` (28) — the
repair below, already computed and already named, ~90 rounds earlier. Measured over the 68 round
scripts written after R921:

| field | rounds that READ it | in the statement |
|---|---:|---|
| `legitimate_comparators` (the weaker, per-comparator route) | **13** | no |
| **`survives_all_legitimate`** (the stronger criterion) | **1** — R924 only | **no** |
| a runtime-assembled absent field (negative control) | 0 | no |

⭐ **The defect was never that nobody computed it. It is that nobody adopted it**, and the arc built
its formulation on the weaker route while the stronger one sat in a committed artifact.
⚠ **WHY it was not adopted is not measured and is not guessed** — intent is not in the record, and a
reason invented here would be a narrative. What is measurable is that it was not, and from when.

### ⭐ THE REPAIR, WITH ITS COST MEASURED

> **②′** it **resolvably beats at least `q`% of the certified prompt-blind comparator family** — the
> 2.5th percentile of the bootstrapped paired difference is > 0 against that share of the family,
> computed on the prompts the arm **actually covers**, **never on imputed values** — for a **declared
> `q`**, not *a* named comparator and not the whole family.

⛔⛔ **THE PARAMETER IS STATED HERE (R1037), AND IT IS DECLARED RATHER THAN FIXED.** Until now the
clause named no `q`, no family and no closure — so a reader implementing it implemented the form
R1034 measured **vacuous**. The literal reading of the wording above reproduces R1036's committed grid
at **every** quantile, under 3 seeds, against code from a different round:
`q` = 50 → 12 · 75 → 12 · 90 → 11 · 95 → 9 · 99 → 8 · 100 → does not stabilise.
⭐ **`q` is DECLARED, not fixed**, because R1036 found scale-stability **necessary and not
sufficient**: q ∈ {50, 75, 90} are all size-independent and **no measurement over this release selects
among them**. §4 — *a definition that names a number it cannot resolve is how "four" got in* — so the
clause states the **parameter and its measured onset** (100, 100, 100, 300, 2000, never), never a value.
⚠ **q = 100 is excluded by measurement, not taste**: the max never stabilises in family size, so
*"beats the whole family"* cannot be stated at any size this release reaches.
⚠ **N/A** — which `q` is *right* needs an external criterion for what the comparator family
represents (R1028).

⭐⭐ **AND R1038 NARROWS THE DECLARATION TO A DEFAULT OF `q = 90`, ON EVIDENCE.** R1036 and R1037 both
closed saying the choice among the scale-free quantiles could not be measured here. It can: **every
member of the comparator family is itself a scoreable arm**, so the family is its **own reference
population**, and the share of members clearing the q-bar is a **false-admission rate** — *a checklist
is not a core*. That is R1023's device applied to the bar instead of the loader.

| q | 50 | 75 | **90** | 95 | 99 | 100 |
|---|---:|---:|---:|---:|---:|---:|
| false-admission rate | 0.2550 | 0.1217 | **0.0250** | 0.0200 | 0.0050 | 0.0000 |

**Of the three scale-free quantiles, only `q = 90` reaches the operator's own nominal 0.025.**
⛔ **The monotonicity is FORCED** — a member at rank r of N beats ~r/N by construction — **so the
direction is not the finding; the level is.**
⚠ **And the exact match to 0.025 is arithmetic, not significance**: it is 5 of 200 members, SE ±0.0110.
The supported claim is *at nominal within resolution*, never *exactly nominal*.
⭐ So `q` stays a **declared** parameter and the definition still names the curve — but its **default
is now selected on evidence**: **q = 90**, admitting 11 arms, scale-free from n = 100.
⚠ **N/A** — a low rate does not make `q` *right*; a bar can be strict and still measure the wrong
thing, which is construct validity and needs the criterion vocabulary R1028 showed is absent here.

⛔⛔ **AND R1039 PRICES THIS ARC'S OWN IMPOSSIBILITY CLAIMS: 4 of 16 FELL TO ITS OWN LATER ROUNDS.**
That is **0.2500** against R802's committed **1 of 30 = 0.0333** — the same unit, a **7.5×**
difference. The four: R1026 (*a stricter prompt-blind comparator needs building and scoring* → R1033
built one for **0** judge calls), and R1035/R1036/R1037 (*which q needs an external criterion* →
R1038 measured it from the comparator family itself).

⛔ **All four share ONE SHAPE, and that is what the count buys: each said the answer needed something
OUTSIDE the release, and each was answered by an object already INSIDE it.** That is not four
mistakes; it is one habit. **So every `N/A` line in this arc should be read as a HYPOTHESIS, not a
limit** — including the ones still standing.
⚠ **Exposure is carried per entry**, because R999 recorded that *"eligibility is unequal: later rounds
had fewer chances to be checked"*; the hazard (0.0310 per round-of-exposure) is reported in its **own
unit** and is **not** compared to the baseline proportion.
⚠ **N/A** — an unfalsified line is not a true one. Absence of a later contradiction is the *unchecked
wall* itself; attacking each remaining line is one round each.

⭐⭐ **AND R1040 ATTACKED THE LONGEST-EXPOSED ONE AND IT FELL — THE FIFTH, IN THE SAME SHAPE.** R1023
wrote *"whether A2 or A1·consensus is the RIGHT target needs an external gold standard"*. It does not:
the release's **own annotator panel** answers it.

⛔ **The obvious criterion is circular and was refused, not overlooked** — *"which target better
predicts held-out annotators"* **is A2 by construction**. The neutral criterion is **reproducibility**:
a target whose induced arm ordering flips when the annotator panel is resampled is measuring
idiosyncrasy rather than the object, and it is defined identically for both targets.

| target | median ρ across 25 disjoint annotator splits | sd |
|---|---:|---:|
| **A2** | **0.9973** | 0.0007 |
| A1·consensus | 0.9664 | 0.0063 |

**Gap 0.0309 against a pooled across-split SD of 0.0045 — 6.9×.** ⭐ So **A2 is selectable on
evidence**, which is the first support for R1019's committed scoping that every extension figure here
is A2's answer — previously inherited, now measured.
⚠ Controls: within-prompt agreement reproduces R295's **0.5520** (mine 0.5556); permuting annotator
identity across prompts collapses A1c to **0.3439** while A2 holds at 0.9267 — **A2 averages over
annotators, A1·consensus depends on a consensus that shuffling destroys**; a half against itself gives
ρ exactly 1.
⚠ **N/A** — reproducibility is **necessary, not sufficient**, the same limit R1036 hit for `q`. A
stable target can still be the wrong one, and that needs a statement of intent the dataset card does
not carry.

⛔⛔ **AND R1041 ASKED WHETHER THE REMAINING WALLS CAN BE TRIAGED. THEY CANNOT.** Across nine text
features of the sixteen committed `IMPOSSIBLE` blocks, the best separator between the five that fell
and the eleven that stand reaches **p = 0.0769**, against a Bonferroni threshold of **0.0056** and a
label permutation of **0.2637** over 200 relabellings. **Fallen and standing blocks are structurally
indistinguishable in committed text.**
⛔ **And one answer was forced before any test:** a gate demanding a *declared field* flags **all 16**,
because the field exists in none of them — zero retroactive power by construction, which is R1029's
*store the field, don't recover it* restated.
⭐ **So the remedy is a declared field GOING FORWARD ONLY**, and "attack the longest-exposed line
first" is an **ordering guess** that should be labelled as one rather than dressed as triage.
⚠ **The null is a resolution statement, not an acquittal**: at 16 blocks with 5 positives the smallest
attainable p is **0.0002**, so only near-perfect separation could clear correction. This design cannot
see a weak signal, and says so.

⭐ **AND R1042 LANDS THE FORWARD-ONLY REMEDY.** An `IMPOSSIBLE` block now declares `SETTLES:` plus one
tag from a **closed set** — `IN-RELEASE <object>` · `OUT-OF-RELEASE <what>` · `UNATTACKED` — enforced
by `assurance/an_impossibility_names_where_it_would_be_settled.py`. That is HB8 (*if it can be an
enum, it may not be text*) and R1029 (*store the field, do not recover it*), applied to the field
whose absence R1039 priced at 5 of 16.
⚠ **`OUT-OF-RELEASE` is the tag the five falsified lines wrongly deserved**, so it is the one to
distrust when writing it; **`UNATTACKED` is the honest default and costs one word**.
⛔ **Red-first in the only sense a forward-only check admits**: with no round newer than R1041 the
gate exits **2 — UNRUNNABLE**, on the suite's own convention that an empty population is not a pass.
R1042's own block turns that into a live check at n = 1.
⚠ **It checks that a declaration EXISTS, never that it is TRUE** — tagging a genuinely external limit
`IN-RELEASE` passes. The enum removes the **wording** loophole, not the **mislabelling** one.

⛔⛔ **AND R1043 MUTATION-TESTED THE THREE GATES THAT GUARD EVERY COMMIT HERE. ONE IS BLIND.**
`attack_the_suite.py` had established the **floor** — exit 2 on empty input — but never **detection**
on corrupted content. Under a targeted corruption: **currency RED ✅ · next RED ✅ · anchoring GREEN
⛔**, where the anchoring mutation corrupted **`0.0098`**, a value chosen by intersecting the gate's
own asserted numbers with those occurring exactly once in this file. **So a green `anchoring` is
evidence about its silence**, and R1042's *"consistency, not correctness"* is a named hole rather than
a general worry.
⚠ **The mutation is itself an instrument, and it failed twice before it worked**: the first currency
mutation broke only one of two alternative patterns (the gate's pass was CORRECT), and the first
anchoring mutation corrupted a value the gate never asserts — which would have been a **false
retraction of a working gate**. Both are now verified to break what the gate keys on **before** the
verdict is read.
⚠ **Detection is necessary, not sufficient** — a firing gate may still check the wrong property.

⛔⛔ **AND R1044 RETRACTS R1043's HEADLINE ONE ROUND LATER: THE ANCHORING GATE IS NARROW, NOT BLIND.**
Two errors, both mine. ① The value R1043 corrupted, `0.0098`, is **not inside any assertion span** —
it appears in the gate's source and in this document, but its located-assertion set does not cover it,
so *"a value it explicitly asserts"* was **false**. ② The gate had been **printing its own coverage
all along** — `2.7%–7.8% of this document depending on what counts as a claim`, followed by *"A PASS
certifies the anchored numbers, never the document"* — and I read its **exit code**, never its output.
**That is door ①, a description instead of the object, inside a round about whether instruments can be
trusted.**

Split by the gate's **own** coverage: corrupting a **covered** value (`0.034722`) turns it **RED**;
the **uncovered** one stays **GREEN**, reproducing R1043's observation exactly — which makes this a
**scoping correction, not a contradiction**. ⭐ **The gate detects within its declared scope**;
**343 assertions, 349 located spans, 2.7%–7.8% coverage.**
⚠ **What R1043 got right and stands**: `attack_the_suite` tests the empty-input floor and not
detection; **currency** and **next** do detect; and the mutation is itself an instrument needing its
own control — the discipline that caught this.
⚠ **Coverage is a denominator, not a verdict on the remainder**: whether the 92–97% the gate does not
cover contains an error is untested.

⛔⛔ **AND R1045 WITHDRAWS R1044's OWN CLOSING SENTENCE: IT WAS AN INCIDENT, NOT A HABIT.** R1044
generalised its cause — reading an exit code where output was available — as *"a habit rather than an
incident"*, and proposed checking that against the round sources. **The check refutes the claim that
proposed it.** Of the **3** rounds in this window that invoke `subprocess` at all, exactly **1** reads
`returncode` without ever touching `.stdout`: R1043, the round already retracted. **A population of
one is an incident.** On the broader form of the same door-① question — does a round read an
artifact's VALUES or only check that it EXISTS — the answer is **0 of 14** artifact-loading rounds
check existence only; every one of the 14 reads a value. ⭐ **§4's row predicted this exactly**, and
the only surprise is the direction: *"asserting 'they all flattered me' was itself a narrative claim
that the count refuted."* Here the narrative was self-critical rather than flattering, and **a
self-critical generalisation from n=1 is still a generalisation from n=1.**
⚠ **The classifier's own negative control caught the classifier, not R1044.** A first regex version
scored R1044 as failing both axes — the round that reads `.stdout`, indexes `doc[a:b]` and iterates
`A.values()`. It never binds a name from `json.loads`, so it is **not in that population at all**, and
scoring it zero on an axis it does not join is the empty-denominator failure one level down. Replaced
by AST: in the population iff a name is bound from `json.loads`, reading values iff that name is later
subscripted. ⚠ **And 0 of 14 is `≤ 3/14 ≈ 0.21` at 95%, not "none exist"** — nor does reading values
license the conclusions built on them: **R1043 read artifact values throughout** and still reported an
exit code as its finding.

⛔⛔ **AND R1046 FINDS THE ASSERTION SURFACE ITSELF UNANCHORED: BETWEEN `0.164` AND `0.272` OF THE
NUMBERS A ROUND README ASSERTS ARE NOT IN THAT ROUND'S OWN ARTIFACT.** `DEFINITION.md` is guarded by
the anchoring gate; **READMEs are guarded by nothing**, and this arc has run 24 rounds that way. Of
**289** unbacked numbers over **1064**, **114** appear in some *other* round's artifact — plausibly
quoted, which is correct practice — and **175** appear in **no artifact in this arc at all**. Hence a
bracket and not a point: no rule available here separates a legitimate citation from a true miss.
⭐⭐ **THE SPECIFICATION CURVE IS THE FINDING, BECAUSE TWO CELLS GIVE OPPOSITE VERDICTS.** Scoring only
the first heading line gives **0 of 7 unbacked — World A** — and admits **4 of 24 rounds**. Scoring
every number in the README gives **World B**. **I built the h1 cell first, and its positive and
negative controls both passed**, because they test the *containment rule* and never ask whether the
population is the one the claim is about. **§4's search-instrument row with the control already in
place**: *a control asks "can this instrument see?" and never "is what it sees the thing I am about to
claim about?"* The instrument's unit was `first heading line`; the claim's unit is `numbers this round
asserts`; **20 of 24 rounds contributed nothing** and the cell would still have carried a verdict.
⚠ **What this does not say**: an unbacked number is **not re-derivable from its round's own persisted
output**, which is not the same as being **wrong**.

⛔⛔ **AND R1047 RETRACTS R1046's MAGNITUDE ONE ROUND LATER: THE BRACKET FALLS FROM `[0.164, 0.272]`
TO `[0.057, 0.159]`, AND THE WORLD B VERDICT — WHICH REQUIRED `>= 0.25` — IS WITHDRAWN.** The defect
is **display rounding**: a README prints `0.507` where the artifact stores `0.5071...`, and exact
numeric containment calls that unbacked. **122** of the 178 numbers the exact test placed in no
artifact are carried by the round's own artifact at the README's displayed precision; the residue is
**43**, not 152.
⭐⭐ **BOTH OF R1046's CONTROLS PASSED AND NEITHER COULD EVER HAVE CAUGHT THIS.** They drew their test
value **from the artifact itself**, so it was exact by construction — **§4's row verbatim**: *a control
that shares the instrument's blind spot confirms the instrument and licenses nothing.* The defect was
found by reading the object: a `grep` located `0.507` inside R1023's JSON one command after the
checker reported it absent. **That is the third consecutive round in which a control passed while the
population or the precision it was defined over was wrong**, and the through-line is a single missing
step — **name the instrument's unit and the claim's unit and require them equal, before the control is
designed.**
⭐ **WHAT SURVIVES R1046 IS THE SPECIFICATION CURVE, NOT THE MAGNITUDE**: the h1 and body cells still
give opposite verdicts, and **READMEs are still guarded by nothing**. And R1047's own verdict lands in
**neither pre-registered band** — in-source share `0.283` over `60` floating numbers — so **R1046's
proposed gate is neither built nor abandoned**: what splits it is whether a number shared by source and
README is a constant or a coincidence, which needs the **line**, not the value.

⛔⛔ **AND R1048 CANNOT SETTLE THAT, BECAUSE THE TEST IT BUILT CANNOT FAIL.** Partitioning R1047's
residue into constant / external / derived / floating requires a derivation test, and its **measured
coincidence floor over 3 seeds is `[0.965, 0.975]`** — it classifies **97.5% of RANDOM values on the
same order of magnitude as DERIVED**. The observed DERIVED share is **0.717**, *below* the floor: real
residue numbers are matched **less** often than random ones, which is the diagnostic that the test is
**saturated**, not merely noisy. The arithmetic is why — **410** artifact values and four operations
give **~672,400** candidate results, and at 2–4 decimal places the reachable set is dense in the unit
interval, so *"is x a product of two of these"* is nearly *"is x a number"*.
⭐ **VERDICT: UNVERIFIED.** `CONSTANT` **17 of 60** survives because it never routed through this test.
**The remaining 43 UNCLASSIFIED — never FLOATING, never exculpated.** ⭐ **The remedy is not a tighter
tolerance: it is requiring a derivation to be NAMED in the text**, which is what the arithmetic-trap
rule demands of one anyway. A number the author derived says so; a number that merely *could* be
derived says nothing.
⛔⛔ **AND TWO GATE DEFECTS WERE FOUND WHILE COMMITTING THIS ROUND, BOTH IN MY OWN INSTRUMENTS.**
① The verdict string printed **World B** while the line two above it said the class was inside its own
floor — the pre-registered kill said *"if the controls fire"*, and the floor **is** a control that was
measured and then not read. ② **The currency gate went GREEN with no annotation written at all**: this
fact's registered patterns matched **unrelated pre-existing text** — `97.5%` in an old table beside the
word *random*, and `UNVERIFIED` beside `R243`. **That gate has certified every round in this window**,
so a pattern loose enough to match by coincidence is not a defect of one entry. ③ A third, smaller:
**3 of 60** residue entries are written with a leading unicode minus whose negation the artifacts do
carry — the tokenizer is **sign-blind**, the same class as R1047's precision blindness.

⛔⛔ **AND R1049 ANSWERS WHETHER THAT WAS ONE ENTRY OR THE GATE: `multi-home 16 of 63` registered
facts, against a measured `random floor` over 3 seeds of `[0.092, 0.183]`.** The mutation is R1043's
shape applied to currency — delete the span a pattern matches, and ask whether it still matches. A
**second home** means the PASS cannot be attributed to the round's own annotation. At **0.254** the
observed share is **above** the floor, so it is not the document merely being dense; but the
pre-registered bands were `>=0.30` and `<=0.10`, and **0.254 is in NEITHER**, which is reported rather
than rounded to the nearer one.
⭐ **THESE 16 ARE NOW UNVERIFIED ON CURRENCY** — not overturned, not clean: `R921 R922 R920 R925 R926
R975 R978 R986 R989 R1000 R1001 R1005 R1012 R1027` and two more.
⛔ **THE PROXY LEDGER WAS WRITTEN BEFORE THE RUN AND IS SOUND ONE WAY ONLY.** `>=2 homes ⇒ the PASS is
not attributable` holds; `1 home ⇒ it is attributable` **does not**, because the single home may
itself be unrelated text — which is exactly how R1048 failed. **Single-home facts are UNVERIFIED,
never CLEAN**, and folding one into the other manufactures a false acquittal, which is permanent
because nobody re-examines a cleared claim.
⚠ **ONE POST-HOC OBSERVATION, LABELLED BECAUSE IT IS NOT A FINDING**: the multi-home share is `0.361`
before R1022 and `0.111` from R1022 on. The covariate was chosen **after seeing the list**, there is
one test and no multiplicity control. **It licenses a pre-registered test in a later round and nothing
more.**

⛔⛔ **AND R1050 SETTLES WHETHER ANY OF THAT REACHES THIS CLAUSE. IT DOES.** All **16** rounds R1049
flagged as unattributable on currency are cited inside the clause region, in **33 of 36** informative
cells — a hit rate of **`0.917`** against a **permutation floor** of **`[0.490, 0.524]`** (a *random*
set of 16 arc rounds, 3 seeds). Nearly double the floor, so the intersection is **not** forced by the
breadth of the citation region. **The flagged facts are disproportionately the ones this clause cites**:
`R920 R921 R922 R925 R926 R975 R978 R986 R989 R1000 R1001 R1005 R1012 R1027 R1036 R1045`.
⭐ **THE CLAUSE IS THEREFORE DOWNGRADED TO UNVERIFIED-PROVENANCE — NEVER OVERTURNED.** The gate cannot
show the statement carries these facts. It does **not** follow that the numbers are wrong: each flagged
round's own `run.py` re-derives its value directly, and that is the repair, one run per round.
⛔⛔ **AND THE POSITIVE CONTROL FOUND SOMETHING LARGER THAN IT WAS CHECKING: this clause occurs 9 times
in this document.** Anchoring on the first put the window ~47,000 characters from R1037 and R1038 — the
rounds that wrote its stated form — and the control failed, correctly. **The canonical clause is not
locatable by its own text.** That is R1049's multi-home defect one level up, in the STATEMENT rather
than in a gate's pattern, and it is why the anchor became a swept specification axis rather than a
detail. ⭐ **This also answers the production question honestly**: the six preceding rounds were not
orthogonal housekeeping — they land on the object, and the ledger they produced has a definitional
consequence.

⭐⭐ **AND R1051 EXECUTES THE REPAIR: all 16 flagged rounds re-derive their committed VALUES exactly —
`ran 16 of 16`, `drifted 0`, `non-deterministic 0`.** Each was run **twice**, because `differs from
committed` has two causes demanding opposite conclusions — non-determinism (comparison meaningless) or
genuine drift (the committed artifact did not come from the committed code). `run1` vs `run2` is the
noise floor and came back clean for every round, which is what makes the committed-vs-run comparison
readable at all.
⭐ **SO R1050's DOWNGRADE IS ABOUT THE GATE, NOT ABOUT THE NUMBERS.** The clause's provenance is
unverified in the sense that the currency gate cannot attribute it; **the values underneath it are
re-derivable on demand, and now have been.**
⚠ **9 of 16 differ on BYTES while matching on VALUES, and the difference is a git-hash stamp** —
`commit` in some rounds, `head` in others, exactly 2 diff lines each. **Every byte-mismatch is a
stamped round (measured, containment True)**; but 13 artifacts are stamped and only 9 mismatch, so
**four carry a STABLE stamp rather than a HEAD-tracking one** and the mechanism holds over 9, not 13.
⛔ **For those 9 the byte comparison is DEGENERATE** — `floor == ceiling`, it can only ever return
*differs*, so the value cell is the only admissible one. ⚠ **And the mirror defect: 3 artifacts carry
no stamp at all and cannot be traced to their producing commit by any means.**

⛔⛔ **AND R1052 RETRACTS TWO COUNTS, ONE OF THEM R1051's AND ONE OF THEM R1049's.**
**① The census is retracted: 9 stamps, not 13.** Four artifacts have a `head` field holding a TITLE
STRING — `the four cla…`, `the operator…`, `does the ext…`, `does the loa…` — which R1051 counted as
provenance stamps. The instrument's unit was *a key called `commit`/`head`*; the claim's unit is *a
git hash*. **The sixth unit mismatch this window.** ⭐⭐ And it supplies the mechanism R1051 could only
scope: **the true-stamp set is EXACTLY the byte-mismatch set** — a stamp tracking HEAD changes on every
re-run, a title does not.
**② The ancestry test is UNVERIFIED against its own floor.** A stamp records HEAD at run time and the
artifact is committed after, so an honest stamp must be an ancestor of its introducing commit. All
**9 of 9** pass — but a **random** commit from this history passes at **`[0.889, 1.000]`** over 3 seeds,
so passing carries no information. ⭐ **Ancestry is necessary, never sufficient. RE-DERIVATION is the
sufficient test, and R1051 has it for all 16** — which is why the unstamped artifacts are no worse off
than the stamped ones.
**③ R1049's count is retracted, from a quarter to two thirds.** This round's own fact passed GREEN with
nothing written and only one of its two patterns matching. The gate's source reads
`ok = any(re.search(p, region) for p in pats)` — **it passes on ANY pattern.** R1049 used
`all(homes >= 2)`, modelled from memory rather than read. Under the correct `any(homes >= 2)`:
**`45 of 67`** registered facts are unattributable, against R1049's `21 of 67` under the wrong
predicate. ⭐ **R1049 reported `0.254` and landed in neither band; the corrected `0.672` clears World
B — the currency gate is permissive by construction.** ⚠ **This propagates to R1050**, whose `0.917`
against `[0.490, 0.524]` used the 16-round set and must be recomputed before being quoted again; the
direction of the change is not predictable from here.

⭐⭐ **AND R1053 RECOMPUTES IT: THE DIRECTION SURVIVES, THE MAGNITUDE DOES NOT.** At the corrected
`45`-round set the hit rate is **`0.917`** against a floor recomputed **at that size** of
**`[0.719, 0.750]`** — still separable, so the clause region does cite flagged work more than chance.
⛔ **But the observation is AT the CEILING.** Every arc round in the set also returns `0.917`, because
3 of the 36 cells cite so little that no set can reach them; the g=0 floor is `0.000`. **Both
predicates returned exactly `0.917` on sets of 45 and 21 — that identity was the tell.** §4's
`floor == ceiling` applied to the observation: **a saturated statistic supports a DIRECTION and never
a MAGNITUDE**, so R1050's `0.917` was never an effect size and cannot be read as one now.
⛔⛔ **AND SATURATION IS CARRIED BY 11 ROUNDS, OF WHICH ONLY 5 ARE FLAGGED.** The smallest saturating
set is `R1000 R1005 R924 R1004 R923 R1026 R1009 R1010 R1034 R1036 R1037`; six of those eleven are not
flagged at all. ⭐ **So what the design licenses is narrow: the flagged set contains enough
clause-proximate rounds to saturate, and a random set of the same size usually does not.** It does not
license *"the clause depends on unattributable work"* at any stated strength. **R1050's downgrade
stands as a direction; its number is withdrawn as a magnitude.**

⛔⛔ **AND R1054 WITHDRAWS THE DIRECTION TOO, BY CHANGING THE UNIT.** A 12,000-character window catches
every round the document mentions nearby; **a SENTENCE containing both a clause component and a round
id asserts that the component rests on that round.** At the sentence unit nothing saturates: of
**113** arc rounds, **70** are cited in some sentence (the measured ceiling) and **21** are cited in a
sentence stating a clause component — the **declared dependency set**, nameable at last.
⭐⭐ **AND THE ENRICHMENT IS ZERO.** The declared set is flagged at **`0.667`** (14 of 21) against a
registry-wide rate of **`0.676`** (46 of 68) — a difference of **`−0.010`** against an **MDE of
`0.202`**, i.e. **0.05 of the MDE**. **R1050's claim that the clause rests DISPROPORTIONATELY on
unattributable work does not survive at the unit that matches its own wording**, and R1053 preserved
it only as a direction on a statistic already at its ceiling.
⚠ **This is a null, not a proof of no enrichment** — the design could not have resolved a difference
below `0.202`. ⭐ **What stands is the unconditional fact, and it is worse than the one withdrawn:
`0.676` of the whole registry is unattributable on currency, clause or no clause.** The clause is not
special; the gate is.
⚠ **And declared is not NECESSARY**: a sentence citing a round asserts a relation, not that the clause
would fail without it. Necessity needs the clause restated without each cited round and the admission
operator re-run.

⭐⭐⭐ **AND R1055 RUNS THAT NECESSITY TEST AGAINST THE REAL OPERATOR — 99 arms, 968 prompts, target
A2 — ONE ABLATION PER CLAUSE COMPONENT. Two components bind with NAMED excluded arms; two do not.**

| component | Δ admitted | what it excludes |
|---|---:|---|
| **resolvability** (2.5th pct → point estimate) | **2** | removing it ADMITS `greedy_k12_fit1`, `topw_k2` |
| **coverage, not imputed** (own prompts → imputed) | **2** | imputing LOSES `coval_core_2bA`, `coval_core_2bB` |
| comparator **family** (two → one) | **0** | nothing on disk |
| `q = 90` → `q = 100` | **0** | ⛔ **algebraically forced** |

⭐ **This is §4's remedy satisfied at last — *name an admissible object this clause EXCLUDES* — and no
earlier round in this arc supplied one.** The coverage row also **independently reproduces R1032**: the
twins are exactly the arms the imputing operator wrongly admitted.
⛔⛔ **THE `q` ROW IS A DERIVATION, NOT A MEASUREMENT, AND THAT IS THE FINDING.** At family size *k*,
`need(q=90) = ceil(0.9k)` and `need(q=100) = k`, and these are **equal for every k < 10**. The certified
family has **2** members, so `q = 90` and `q = 100` are **the same operator** and Δ=0 could not have come
out otherwise. ⭐ **The clause declares a parameter its own certified family is too small to exercise.**
R1036–R1038 measured `q`'s onset curve and set its default at 90; none of that is wrong, and **none of
it is exercised by the operator as the clause currently runs.** `q` first becomes testable at
**`|family| = 10`** — five times the current family.
⚠ **Binding is necessity, never correctness**: R1032 showed the pre-repair form also bound, and bound
wrongly. **Controls**: resolvability must bind — True; ablating nothing reproduces the baseline — True;
seed-only change leaves the set unchanged — True; 3-seed spread **24 in / 75 out / 0 unstable**.

⛔⛔⛔ **AND R1056 SETTLES WHETHER `q` CAN EVER BE EXERCISED HERE: IT CANNOT.** `q` first distinguishes
anything at `|family| = 10`. Sweeping the prompt-blindness threshold over the 95 arms with a committed
selection:

| rule | family | reaches q@10 |
|---|---:|---|
| `n_distinct ≤ 1` (the committed `fixed`) | **2** | No |
| `n_distinct ≤ 2 … ≤ 250` | **2** | No |
| `n_distinct ≤ 500` | 4 | No |
| `n_distinct ≤ 1000` | **95 — everything** | Yes, vacuously |
| `modal_share ≥ 1.0 … ≥ 0.25` | **2** | No |

⭐ **The distribution is extreme, not merely bimodal.** Two arms use one selection across all prompts;
essentially every other arm uses a **near-unique selection per prompt**. Relaxing "identical on every
prompt" all the way to "at most 250 distinct selections" **admits nobody new**. There is no middle to
stand on, so **the clause declares a parameter this release cannot exercise at any defensible
threshold** — `q` should be adopted with an explicit relaxation that does not exist, or dropped.
⛔ **AND THE KNOB THAT LOOKED RIGHT WAS THE WRONG ONE.** R918 stores `fixed` (*same across prompts*, 2
arms) and `exact` (*subset of the rubric*, **86 arms at 1.0**) one field name apart, and they are **not
nested** — every `exact` threshold from 0.01 to 1.0 returns the same 86. **Sweeping `exact` would have
manufactured a family of 86 and declared `q` testable.** The eighth unit confusion this window and the
first caught *before* any number was computed, by reading both definitions out of R918's source.
⚠ **Reaching 10 is necessary for `q` to bite and never sufficient for the family to be legitimate**: an
arm using few-but-more-than-one selections still conditions on the prompt, only coarsely.
**Controls**: strictest cell equals the committed `fixed` set — True; most permissive contains all 95 —
True; `coval_core` named untypable rather than dropped.

⭐⭐⭐ **AND R1057 SETTLES WHETHER TO DROP `q`: KEEP IT, WITH ITS PRECONDITION WRITTEN INTO THE CLAUSE.**
The proposal to restate the clause with and without `q` and re-ablate **cannot produce evidence** — at
|family| = 2 the two are the same operator and the ablation returns Δ=0 by algebra. So instead the
world where `q` acts was BUILT: a fixed criterion subset used on every prompt is prompt-blind under
R918's own `fixed` predicate, by construction.

| k | need @ q=90 / q=100 | admitted | Δ |
|---:|---|---:|---:|
| 2 · 4 · 8 | 2/2 · 4/4 · 8/8 | 46/46 · 46/46 · 37/37 | **0** |
| **10** | **9 / 10** | 39 / 37 | **2** |
| 12 | 11 / 12 | 37 / 37 | **0** |
| **15** | **14 / 15** | 37 / 35 | **2** |

⭐ **`q` buys 2 arms at the two cells where it bites and nothing at `k=12`** — the effect is **not
monotone in k**, because it turns on whether any arm beats *exactly* `k−1` comparators, which is a
property of the population rather than of `q`. **So `q` is a real parameter awaiting a real family,
not a dead one, and the clause keeps it with the precondition stated: inert below |family| = 10, and
this release supplies 2.**
⛔⛔ **AND THE BLIND-COMPARATOR SPACE IS ITSELF CAPPED AT 15.** Only **4** criterion indices are present
on every prompt, so the fixed subsets well-defined everywhere number **2⁴ − 1 = 15**. The first attempt
asked for 20 and the round **refused to run**. **A clause needing k > 15 would be unsatisfiable by
construction**, not merely unsupported.
⚠ **The family is SYNTHETIC** — constructed, blind by construction, legitimate under R918's rule, and
**not a release**. **Controls**: k<10 agree exactly (R1055's arithmetic) — True; 12 *identical*
comparators leave `q` inert — True; k=0 admits nothing — True; 3 seeds, unstable arms excluded and
counted.

⛔⛔⛔ **AND R1058 REACHES THE CLAUSE'S CENTRAL CLAIM AND FINDS IT UNIDENTIFIED ON THIS SITE.** The
question §4 names for a definition written from one instance — *has it ever judged an object other
than the one it was written from?* — was run: **13 never-seen synthetic cores, 3 seeds each, admitted
at 0**, against **`24 of 97 = 0.247`** for the released arms.
⭐ **The verdict is UNVERIFIED ON IDENTIFICATION, not World B**, and the reason is worth more than the
rate. **Three confounds, each found only after the round was built on it:** ① the positive control
built the comparator — the 4 criteria common to every prompt **are `generic`'s own selection**, so it
asked whether the comparator beats itself; ② every fixed subset of those criteria is a **subset of the
comparator**, so `0 admitted` meant only that a subset of X does not beat X — and **the verdict string
fired World B on a rule set that could not separate the worlds**; ③ the one that cannot be engineered
away: **every rule available to me is UNSELECTED and every admitted released arm was OPTIMISED**, so
the comparison confounds **provenance with quality**, and a definition *ought* to reject unoptimised
objects.
⭐⭐ **THE GAP CANNOT BE CLOSED INSIDE THIS RELEASE.** A never-seen *good* core needs an optimiser other
than the one that produced the released arms, and using that optimiser makes it no longer never-seen.
**So the clause's central claim — that it defines a category rather than describing its instance —
is UNIDENTIFIED here, and naming why no rate on this site can settle it is the stronger statement.**
This converts the register's standing `second release` entry from a formality into **the binding
constraint on the definition**.
⚠ **Reported as a finding rather than a control**: a never-seen core using **every** criterion
available per prompt is **not admitted** — more criteria is not better agreement with humans.
**Controls**: a known-admitted released arm from R1055's baseline **is** admitted (else every zero
would be silence); a comparator's own vector is **not**; the empty selection admits **0**.
⚠ **And R1057's NEXT is CLOSED, not run**: its own table already showed identical sets at k = 2, 4, 8,
so the operator returns the `q=100` answer **and emits no signal** — silent degradation, already
measured. Re-running it would have been a third derivation reported as an experiment.

⛔⛔ **AND R1059 BUILDS THE SECOND OPTIMISER R1058 CALLED THE BINDING CONSTRAINT — THE CONFOUND
REPRODUCES, AND NOW ITS SIZE IS MEASURED.** Two optimisers were built on axes the released
`greedy_*`/`topw_*` family shares and these do not: **`varmax`**, which never sees the human target
and ranks criteria by how much they discriminate among the four responses, and **`heldout`**, which
fits a global criterion ranking on **half** the prompts and is judged **only on the other half**.
**Neither is admitted at any k** (0/3 seeds, k = 2, 3, 4) while released arms pass at `0.247`.
⭐ **But the verdict is UNVERIFIED, not World B, and two controls say why.** ① **The sham condition I
wrote could only fire if the optimiser was admitted** — a check that cannot fail in the case that
occurred. Read on the **continuous score**, reversing `varmax`'s ranking moves mean agreement by
**`[+0.0094, −0.0004, −0.0015]`**: **the target-free objective contributes nothing**, so `varmax` is a
size-matched selection rule wearing an optimiser's name and **only `heldout` is a real optimiser —
n = 1**. ② **The quantity that decides the round is the one I almost did not look at**: the best
synthetic core scores **`0.4863`** against comparator `generic`'s **`0.5514`**, a gap of **`+0.0651`**.
**Non-admission is fully explained by QUALITY**, so R1058's provenance-vs-quality confound is not
resolved — it is **reproduced with better-built objects**.
⭐⭐ **WHAT THIS ESTABLISHES IS A SPECIFICATION, NOT AN ASPIRATION.** R1058 could say only *"the
comparison is confounded"*. This says **how far anything must travel to break it: `0.0651` of mean
agreement, against a comparator at `0.5514`.** Any future attempt — a second team, a second release —
must close that gap before its rejection or admission carries information about provenance at all.

⛔⛔⛔ **AND R1060 BOUNDS IT INSTEAD OF ATTEMPTING IT AGAIN: THE BOUND BINDS.** An exhaustive search
over **4,943 fixed subsets** of size 1–5 drawn from the 15 criteria available on ≥50% of prompts,
selected on half the prompts and scored on the other half, **fails to beat the comparator in 5 of 5
splits** — margins `[-0.0248, -0.0144, -0.0054, -0.0101, -0.0288]`.
⭐ **So every fixed-subset core's non-admission is FORCED by the release, not by the clause**, and the
question *does the clause test provenance* is **unanswerable by this family** — no experiment of this
shape can carry information about it, however well built. That closes the line R1058 opened by
bounding it rather than by another attempt.
⭐ **Controls, and one of them decides the round**: the comparator's own selection `[0,1,2,3]` is
inside the enumerated family (else the search is not over the space it claims); the worst subset scores
`0.3017` against `0.5880`, so the family is not degenerate; honest selection is worth **`+0.0090`**
over a random subset held-out, above the pre-registered `0.005` **but only just**; and **selection
optimism is `+0.0314` — larger than every margin measured**, so the in-sample best would have shown
the comparator beaten in all five splits. The held-out split is the only admissible number here.
⛔⛔ **AND AN ESTIMAND CHECK LANDED HARDER THAN INTENDED: `generic` scores `0.5880` under this round's
consensus aggregation, `0.5023` under a quick reimplementation of R1059's per-annotator one, and
R1059 itself reported `0.5514`. THREE numbers for one arm.** ⭐ So the honest statement is not
*different estimands* but **the two rounds' scales are UNVERIFIED against each other**: a three-line
reimplementation is not evidence about what another round computed. **R1059's `+0.0651` and R1060's
margins must not be quoted against each other** until one round re-derives the other's number with the
other's code. Each round's internal comparison — arm against comparator, same prompts, same
aggregation — stands.

⛔⛔⛔ **AND R1061 RECONCILES ALL THREE EXACTLY — THE CAUSE IS TWO ERRORS AT ONCE, AND R1060's
COMPARATOR WAS NOT THE COMPARATOR.**

| source | aggregation | value | |
|---|---|---:|---|
| **read `sat_generic.npz`** | per-annotator | **0.5514** | R1059's committed number |
| **read `sat_generic.npz`** | consensus | **0.6632** | ⭐ the cell nobody computed |
| reconstructed `sat_full[0:4]` | per-annotator | **0.5023** | R1060's 3-line reimplementation |
| reconstructed `sat_full[0:4]` | consensus | **0.5880** | R1060's committed number |

**All three published values reproduce to four decimals**, so the discrepancy is fully explained — and
not by aggregation alone. R1060 **reconstructed** `generic` as `sat_full` restricted to criteria
`[0,1,2,3]` while R1059 **read** `sat_generic.npz`; the two disagree on **`764 of 968` prompts**.
⭐ **Under R1060's own consensus aggregation the true comparator scores `0.6632`, not `0.5880`.** So
R1060's margins were measured against an arm that is not the comparator. **R1060's numbers are
RETRACTED; its conclusion survives and HARDENS** — the shortfall against the real comparator is ≈`0.08`
rather than ≈`0.015`, so **the bound binds about five times harder than reported**.
⭐⭐ **And the third number was never a measurement.** R1060's `0.5023` was a three-line guess at
another round's code; it lands in a real cell, but as *the reconstructed object under the read
object's aggregation* — a combination **neither round intended**. **R1060 was right to refuse to reason
from it, and that refusal is the only reason this reconciliation happened instead of a silently-wrong
cross-round gap.** ⚠ **Controls**: both committed numbers **read from artifacts**, never remembered;
the two sources shown to **differ** before the object hypothesis was entertained at all.

⛔⛔⛔ **AND R1062 RETRACTS R1061's HEADLINE ONE ROUND AFTER IT WAS WRITTEN: THE CRITERION INDEX IS
LOCAL TO ITS FILE, SO EVERY CROSS-FILE NUMBER IN THIS LINE IS VOID.** On the **15,488** `(criterion,
letter)` keys `sat_generic` and `sat_full` share, they disagree on **14,878 — `0.9606`** — identically
at 1e-12 and 1e-6, so it is not a floating-point artefact. **The integer in `(i, letter)` is a POSITION
IN THAT ARM'S OWN CRITERION LIST, not a global id**: `generic`'s criterion 0 and `full`'s criterion 0
are different criteria that share an index. Searching all `4 × 39` pairs for a value-preserving
correspondence finds **0 of 4** exact matches (closest mean |Δ| `0.0977`–`0.1495`).
⭐ **SO R1061's `the true comparator scores 0.6632 and the bound binds five times harder` IS
WITHDRAWN** — it read one file's comparator against another file's subsets. ⛔ **And the error is the
one R1060 warned about, one level down**: R1060 refused to quote numbers across ROUNDS without
re-deriving them; **one round later I quoted them across FILES without checking the files share an
index space.** The rule was right and I applied it at the wrong grain.
⭐⭐ **WHAT THIS RESTORES**: **R1060's margins are internally valid after all** — one file, one
consistent index space — and only its LABEL was wrong: `comparator` should read **`full` restricted to
its own first four criteria**. Its bound stands as originally reported, **neither harder nor softer**.
**R1059's `0.5514` remains the real `generic`**, read from its own file, and is not comparable to any
`sat_full`-derived number.
⚠ **And the route that would make cross-arm criterion claims admissible is IN-RELEASE and
unattempted**: `data/conversation_rubrics.jsonl` carries the rubric TEXT, so a global criterion
identity is obtainable by joining on text rather than on position.

⛔⛔ **AND R1063 RUNS THAT JOIN AND FINDS IT BLOCKED AT THE KEY — WHILE REDISCOVERING PRIOR ART THE
DOCUMENT ALREADY HELD.** The rubric file is keyed by `conversation.id`; every artifact in this arc is
keyed by **`comparisons.jsonl:prompt_id`** (located by measurement: 968 of 1,078 scanned rows carry
one). ⚠ **R466 ALREADY RECORDED THE DISJOINTNESS** — *"rubric-text ids 986, ranking ids 1078,
intersection 0"* — so half of R1063 is a rediscovery, and **the prior-art gate was not run before
building it**. What surfaced the duplication was an accident: the currency gate went GREEN because my
registered pattern coincidentally matched R466's own sentence. **A coincidence is not a mechanism.**
⭐⭐ **WHAT IS GENUINELY NEW IS THE CRITERION SPACE, NOT THE ID SPACE.** `core_generic` uses **4 fixed
generic texts** — *"the reply is accurate and factually correct."* and three like it — the **same
selection on every one of 968 prompts**, sharing **0 shared** strings with the **14,808
rubric-derived texts** `core_full` draws on. **The two arms range over DISJOINT CRITERION UNIVERSES**,
which fully explains R1062's 96% index disagreement: there is no correspondence to recover, and
criterion-level cross-arm claims are **meaningless** rather than merely unrecovered.
⭐⭐⭐ **AND THAT CLOSES THE LINE INSTEAD OF EXTENDING IT: the admission operator consumes a RANKING of
the same four responses, never criteria.** Two arms drawing from disjoint criterion universes still
rank the same objects, so **score-level comparison was valid throughout** and only R1061's
criterion-index reasoning was ever void.
⛔⛔ **A THIRD DEFECT, IN THE REGISTRY ITSELF, AND IT HID ALL OF THIS FOR FIVE CONSECUTIVE CHECKS.**
Every fact is registered under `if d:` where `d = load(<artifact glob>)`. **R1063's script was crashing
before writing its artifact, so `load` returned `None`, no fact was registered, and the gate reported
PASS — five times.** A missing artifact is therefore **indistinguishable from a satisfied fact**: it is
§4's *empty population passes*, sitting inside the instrument that certifies every commit here.

⭐⭐ **AND R1064 AUDITS THAT INSTRUMENT'S OWN INPUTS AND SHIPS THE FIX: all 79 globs resolve, dead 0**,
and none matches more than one file. ⚠ **That is true NOW only because R1063's artifact was written
minutes earlier** — it was false while that script was crashing, and nothing in the currency gate
would have said so. The count reassures about the past only because the past has just been repaired.
⭐ **The remedy is shipped, not merely proposed**: `assurance/a_registered_fact_must_load.py` exits
**1** on any unresolved glob and names it. A round that leaves the defect in place is cost recovery;
the gate is the production.
⭐ **AND THE LOCK WAS ATTACKED BEFORE BEING TRUSTED.** Redirecting one glob to a nonexistent round →
**exit 1** with the dead glob named; a registry containing **no** `load()` calls at all → **exit 2**,
because a gate over nothing must not pass; restoring the registry → **exit 0**, 79 of 79. **The second
attack is the load-bearing one**: without it, emptying the registry would have turned the new gate
green. ⚠ **Existence is not correctness** — a resolving glob may still point at the wrong artifact,
which is the currency gate's own pattern check and not this one's.

⛔⛔⛔ **AND R1065 TURNS THAT ATTACK ON THE CURRENCY GATE ITSELF: IT IS TEXT-ONLY. IT CERTIFIES PROSE
AGAINST PROSE.** A registered artifact's measured value was changed from `79` to `4321` and its `dead`
list given a **fabricated** entry, with the statement **untouched** — **the gate exited 0, identical to
baseline.** ⭐⭐ **And it PRINTED the falsified numbers as it passed**:
`R1064 … = globs 4321, dead 1`. It reads the artifact, displays its values, and **its verdict ignores
them**. Read from the source: each fact is `(round, description, value_string, patterns)`; the
`value_string` is an f-string that is *printed*, the `patterns` are hand-written literals matched
against this document, and **nothing in the match consumes the artifact**. Its only roles are to exist
(R1063) and to supply a display string.
⭐ **THE CONTROLS ARE WHAT MAKE THIS ADMISSIBLE, AND THE POSITIVE ONE FAILED FIRST — CORRECTLY.**
Redacting **one** anchor left the gate green, because the gate is `any(...)` and the fact had two
patterns; **calling that a control would have made a working gate look broken.** Defeating **every**
anchor turns it red (exit 1). The **sham** — mutating an artifact key no pattern mentions — leaves the
verdict unchanged, which is what shows the intervention result is not *"any file edit is ignored"*.
Placebo restores the baseline; both mutated files were restored in a `finally` and the worktree
verified clean.
⚠ **THIS IS A SCOPE FINDING, NOT A DEFECT VERDICT.** A currency gate may be *meant* to ask *did the
statement get updated*, which is a real question and the one it answers well. **What is not licensed is
reading its PASS as *the statement agrees with what was measured* — which is how every round in this
window has been reading it.**

⭐⭐⭐ **AND R1066 ATTACKS THE ANCHORING GATE FROM THE SAME SIDE AND GETS THE OPPOSITE ANSWER: IT IS
ARTIFACT-COUPLED, SO THE TWO GATES DIFFER IN KIND.** Mutating one JSON number in
`R444_clause_three_reconciled`'s artifact — `clause3_excludes_before`, `4 -> 7781`, **statement
untouched** — turns it **RED (exit 1)**, while the **sham** (adding a key it asserts nothing about)
leaves it **green**. ⭐ **That intervention/sham pair is what carries the finding**: coupling to *that
value*, not sensitivity to any file edit. **Currency certifies that words were written; anchoring
certifies that the words match a measurement.** R1065's result stands and is now **scoped to one
gate**, a materially different conclusion from the one its own NEXT anticipated.
⛔ **TWO OF MY OWN CONTROLS WERE MALFORMED AND BOTH FAILURES WERE THEIR OWN.** ① The target resolver
searched `load(...)` globs under `E05` when the gate's globs are **round-directory** patterns resolved
against arc directories — and the round **refused to run** rather than reporting *no artifact found* as
a result. ② The first positive control replaced the **first `"4"` anywhere in a 2,400-line document**,
an arbitrary digit rather than the asserted one, and its green said nothing. ⚠ **Its repair is blunt
and that is stated rather than hidden**: `4` occurs **933** times as a standalone number, so mutating
all of them licenses only *the gate can return red at all* — **the artifact side is what isolates the
asserted value.**
⚠ **And R1044's ceiling still binds**: anchoring covers **2.7-7.8%** of this document, so
**artifact-coupled WITHIN ITS COVERAGE** is the entire claim — never *the statement is anchored*.

⛔⛔⛔ **AND R1067 ASKS WHERE THE CLAUSE ITSELF SITS, AND THE ANSWER IS THE WORST CASE THOSE TWO FACTS
LEFT OPEN: `0 of 121` NUMERIC CONSTANTS IN THE CLAUSE REGION ARE NOTICED.** Every number inside a
±700-character window around each of the **9** `resolvably beats` homes was mutated **one at a time**
and the anchoring gate stayed **green for every one** — while a value R1066 established as anchored
**reds**. ⭐ **So the gate is perfectly coupled to values that are NOT the definition, and the sentence
this entire arc exists to defend sits in the uncovered remainder.**
⭐ **THE POSITIVE CONTROL IS WHAT MAKES `0 of 121` A MEASUREMENT RATHER THAN SILENCE** — without a
demonstrated red, a zero from this instrument would be *"never shown to return non-zero"*. And the
**sham** (mutating a WORD rather than a number inside the clause) does **not** red, so the finding is
*these values are unguarded*, not *any edit to this region is ignored*. Placebo restores; the document
was restored after every one of the 121 mutations.
⭐⭐ **THE READING OF THE COMMIT RECORD CHANGES COMPLETELY.** Every `all gates green` in this window
meant **the expected strings are present** (currency, R1065) **and some values elsewhere in this
document still match their artifacts** (anchoring, R1066) — **and never that the clause is anchored.**
⚠ **Coverage is not correctness**: an unguarded constant is not thereby wrong. It is unguarded, which
is a statement about the instrument and a licence the instrument does not grant.

⭐⭐⭐ **AND R1068 BUILDS THE COVERAGE INSTEAD OF MEASURING ITS ABSENCE AGAIN: `4 of 4 declared clause
constants` NOW TURN A GATE RED WHEN MUTATED.** `assurance/the_clause_is_anchored.py` re-derives each
from the round that measured it — **certified family size `2`** and **q threshold family size `10`**
(R1055), **k needed for q `10`** (R1056), **blind-comparator space cap `15`** (R1057) — and requires
the statement to state it.
⭐ **THE ACCEPTANCE TEST IS R1067's OWN SWEEP, WHICH THE OLD GATE FAILED 121 OF 121**, and the two
controls that carry it are the last two: the **sham** (mutating an *undeclared* clause number, `74`)
stays **green**, so the gate reacts to *these values* rather than to any edit — without it four reds
would prove nothing; and the **negative** (deleting a source artifact) turns it **RED**, verifying it
**fails closed** rather than repeating R1063's silent skip. That is checked here, not asserted.
⛔ **AND IT COVERS NUMBERS, NOT PROSE, AND THE GATE'S OWN DOCSTRING SAYS SO. Four constants is not
*the clause is anchored*** — R1067 counted **121** numeric tokens in the clause region, so this closes
the **declared subset** and leaves the rest **exactly as exposed as before**. A gate that overstated
its reach would be the failure it was built to fix.

⭐⭐ **AND R1069 ASKS WHICH OF THE REMAINING CLAUSE NUMBERS COULD BE DECLARED — AND THE ANSWER SPLITS
BY MAGNITUDE CLASS, WHICH A POOLED NUMBER WOULD HAVE HIDDEN.**

| class | tokens | sourceable | its own floor (3 seeds) | margin |
|---|---:|---:|---|---:|
| **decimals** | **38** | **0.789** | **[0.105, 0.184]** | **+0.605** |
| integers | 93 | 1.000 | **[0.935, 0.946]** | +0.054 |
| *(pooled)* | 131 | 0.939 | [0.672, 0.710] | +0.229 |

⭐ **With 72,754 distinct values across 872 artifacts, nearly any small integer is `sourceable` by
coincidence** — so the **integer class is saturated** and its `1.000` carries almost no information,
while the **decimal class — the measured quantities — separates by `+0.605` and is the finding.**
**R1068's gate can be extended to the clause's decimal constants; its integers are unresolved by this
test whatever their share.**
⛔ **TWO COUNTING CORRECTIONS, BOTH MINE.** ① My first count was **144** where R1067 counted **121**:
the 9 clause homes have **overlapping ±700 windows**, and appending per window counts a shared token
once per window while R1067 keyed by absolute offset. ② ⚠ **Deduplicated it still reads 131, and that
is not a bug — the statement has GROWN between the two rounds**, since each round appends its
annotation. **A population that changes between rounds means any cross-round count needs the document
version attached**, which is the same class of error R1060 and R1061 spent two rounds untangling.
⚠ **And no aggregate licenses a single token**: the floor makes the count readable, not any particular
`this number has a source`. That is **one reading per token, and there are 131**.

⛔⛔⛔ **AND R1070 RETRACTS R1069's HEADLINE ONE ROUND LATER: `31 of 38 clause decimals` ARE STORED BY
NO ROUND AT ALL.** R1069's extractor pulled numbers out of **strings inside artifacts**, so a value
merely **quoted in another round's verdict text** counted as sourced. **Quoter inflation, measured:
mean `+4.8` candidate rounds per value, max `+59`.** Restricting candidacy to rounds that **stored**
the value as a numeric leaf: unsourced **8 → 31 of 38 (`0.816`)**, ambiguous **28 → 6**, unique
**2 → 1**. ⭐ **The clause's decimals are sourceable AS TEXT and largely not AS MEASUREMENTS.**
⛔ **THE TELL WAS THE PRECISION CURVE RUNNING BACKWARDS.** Six-decimal values are nearly unique by
construction, yet **0 of 19** resolved to a single round under the first extractor — which is not how
precision behaves, and is what sent me back to the walker. Under the corrected one **all 19 are
unsourced**: consistent, and much worse.
⚠ **AND THE VERDICT IS NEITHER PRE-REGISTERED WORLD.** I registered *most are addressable* (≥0.50) and
*ambiguity dominates* (≤0.20); the modal outcome is **UNSOURCED at `0.816`**. Reporting the category I
did not anticipate, instead of forcing the result into one of my two, is the whole reason for naming
bands in advance.
⭐ **What survives is small and honest: `1` decimal whose provenance can be checked by opening one
file instead of searching 820 rounds.** A single candidate is an **address**, never a proof of
citation — and R1068's gate cannot be extended mechanically to the rest, because there is nothing
stored to extend it to.

⭐⭐⭐ **AND R1071 SETTLES WHAT THAT GAP IS: A RECORDING FAILURE, NOT AN UNSUPPORTED CLAIM.
`31 of 31 = 1.000` of the unstored clause decimals appear in the committed PROSE record** — round
READMEs, `run.py` sources, commit bodies — against a **measured floor of `[0.032, 0.161]`** for random
decimals at matched precision, and a **SHAM of `0 of 31`** when the same values are searched in the
release data. **Nothing in the clause is a number no committed text supports.** The gap is that rounds
reported values they never persisted to a results file, and the remedy is a writing habit rather than
a search.
⛔⛔ **AND THE NEGATIVE CONTROL CAUGHT CONTAMINATION TWICE OVER.** ① My sentinel was FOUND — because
**R1070's `run.py`, written minutes earlier, contains it as ITS sentinel**. ② Far worse for the real
question: the corpus included **R1067–R1070, the very rounds that quote these decimals wholesale**, so
*found in the prose record* would have been trivially true for anything the audit rounds mentioned.
**That is R1070's `a quoter is not a source`, one level along.** Rounds from **R1067 on are excluded**
as downstream of the clause. ⭐ **Without that exclusion this round would have reported `1.000` for
entirely the wrong reason — and reported it as a clean result.**
⚠ **Presence in prose is not provenance**: a README may quote a value it did not compute, exactly as
found on the artifact side. This separates **in the record** from **absent**; it does not separate
**measured** from **quoted**.

⛔⛔ **AND R1073 SPLITS THAT RECORDING GAP INTO THREE, ONLY ONE OF WHICH IS A WRITE.** Of the 31
unstored clause decimals: **exactly one upstream README carries it — 6**; **many carry it — 15**;
**no upstream README carries it at all — 10** (those live only in `run.py` sources and commit bodies,
which R1071's wider corpus could not distinguish). Single-carrier share **`0.194`** against a measured
floor of **`[0.000, 0.129]`** and a **SHAM of `0 of 31`** in the release data. ⚠ **The margin over the
floor is `+0.065` and the World-B threshold is `<= 0.20`, so the observation at `0.194` is close to
both** — reported as resolved-and-propagated with the narrowness stated rather than rounded away.
⭐ **So `write it down` repairs 6 values, not 31.** `0.5514` is carried by **12** rounds — propagation
in action; `0.009103` by exactly one (`R981`); `0.005730`, `0.012488` and `0.009956` by none.
⛔ **AND HALF OF R1071's OWN NEXT WAS FORCED AND WAS NOT RUN.** It proposed checking that the round
reporting an unstored value also fails to store it — but **the population was DEFINED as `stored by no
round`**, so that check could only ever return 100%. **It would have printed a clean-looking result
that restates the selection criterion.** Named here so it is closed rather than dropped.
⚠ **Corpus restricted to rounds before R1067**, carrying forward R1071's contamination lesson rather
than relearning it.

⛔⛔⛔ **AND R1074's READING EXPOSED A UNIT ERROR RUNNING BACK THROUGH THE WHOLE CHAIN: THE COUNTS ARE
OCCURRENCES, NOT VALUES.** R1073 built its list by deduplicating clause tokens **by offset**, so the
same value at two positions counts twice. Measured: R1070's **`31` unstored is `31 occurrences = 18
distinct values`**, and R1073's **`6` single-carrier is `6 occurrences = 3 distinct`** — `0.009103`
appears 3×, `0.559311` 2×. ⭐ **The same unit failure this window has caught repeatedly, and it
survived four rounds because each inherited its population from the last.**
⭐ **Read, the three distinct singly-carried values are**: `0.009103` (**R981**, under *"Two controls
failed before one passed"* — **R981 itself calls it a population error being corrected**, so
persisting it would store a number the round wrote to disown); `0.559311` (**R1000**, a bar quoted in
a derivation discussion); `0.551354` (**R782**, `| A2 | POOL[0:4] 0.550436 · generic 0.551354 |`, a
comparator mean in a result table). **Candidate-finding 2 of 3** — and the sentences are printed
because they, not the count, are the evidence.
⛔ **THE PROXY IS SOUND ONE WAY ONLY, WRITTEN BEFORE THE RUN**: a controls/limitations placement DOES
establish *incidental*; a result placement does **not** establish *finding*, because a result section
also carries baselines and quoted comparisons — `0.551354` is exactly that. **Result placement returns
CANDIDATE, never CONFIRMED.**

⛔⛔⛔ **AND R1075 VOIDS THE PREMISE OF FIVE ROUNDS: THE `UNSTORED` VALUES ARE ALL STORED, AT FULL
PRECISION.** R1070 declared 31 clause decimals *stored by no round* using an **exact float
comparison**. Checked properly: `0.559311` is **`0.5593110791885862`** on disk, `0.551354` is
`0.5513543391990778`, `0.009103` is `0.009102604212460431` — **3 of 3 checked are stored.** The
statement prints a **rounded display value**, the artifact stores the **full** one, and exact matching
finds nothing. **This kills R1070's `31 unstored`, and with it R1071, R1073, R1074 and R1075's own
premise.**
⭐⭐ **THE LESSON IS WORTH MORE THAN THE CHAIN IT KILLED: R1047 FOUND AND FIXED THIS EXACT DEFECT** —
display rounding versus stored precision — and wrote `has_rounded()` for it. **R1070 wrote a fresh
exact `has()` instead of reusing it.** ⭐ **A fix that lives inside one round's script does not
propagate.** Five rounds inherited the broken population without re-deriving it, and **every control
in each of them was correctly aimed at the wrong question** — none could have caught this, because each
tested its own instrument against its own population, and the population *was* the defect.
⛔ **AND IT WAS NOT CAUGHT BY A CONTROL. It was caught by the currency gate going GREEN when it should
have gone RED**: a registered pattern matched a table in this document reading `0.5593110792 …
0.5513543392` — **longer values that my six-digit tokens were truncations of.** The coincidental match
was the evidence.
⭐ **What survives is the origin test, whose own controls fired**: `0.009103` CONSUMED (a literal in
R981's source), `0.559311` and `0.551354` PRODUCED — agreeing with R1074's independent
position-based classification. **Two instruments converged; they answer a question that no longer
needs asking.**

⭐⭐⭐ **AND R1076 SETTLES WHETHER THAT WAS A LAPSE OR A PATTERN, AND SHIPS THE ONE PLACE THE FIX CAN
LIVE: `38 independent value-membership implementations` IN THIS REPOSITORY, `34` OF THEM
PRECISION-BLIND against 4 precision-aware.** So every round re-makes the choice and R1075's collapse
was waiting to happen again. **The remedy is `assurance/valuematch.py`** — *when one side of a
comparison is a value read from PROSE, match at that value's own displayed precision* — and its
acceptance test is not its own green: it **finds the three values R1070's exact test missed** and
**still rejects an unrelated value**.
⛔ **THREE CLASSIFIER REPAIRS, EACH FORCED BY A CONTROL, AND THE COUNT FELL FROM `132` TO `38`.**
① `main` was classified as a membership test, because any long function contains ` in `, `==` and
`abs(` — **length became part of the definition**. ② `cls`, `agree`, `top1`, `rank_obs` were counted —
scoring helpers, not membership tests — and ⭐ **the positive control passed anyway, because it only
checks that KNOWN cases are FOUND, never that what is found is the thing being claimed**; §4's row
verbatim. ③ `agree` survived even that: it iterates and compares but **returns a number**, and a
membership test returns a **verdict**. **The negative control — a named list of helpers that must NOT
appear — is what made repairs ② and ③ possible at all.**
⚠ **38 is a LOWER bound**: the classifier recognises membership tests by shape. **And a precision-blind
test is not thereby wrong** — exactness is correct when both sides come from the same computation, and
fails only when one side is a displayed value.

⭐⭐ **AND R1077 TURNS THAT COUNT INTO A RISK SET: `22` OF THE 34 CANNOT BE EXPOSED AT ALL, `12` ARE
AT-RISK.** A round whose source performs no `.md` file operation cannot put a displayed value on
either side of its comparison — so those 22 compare quantities that never left a computation, where
exactness is correct. At-risk share `0.353`, **neither pre-registered band**, reported as such.
⛔ **THE PROXY IS SOUND ONE WAY ONLY, AND THE ROUND'S ACTUAL CLAIM IS THE NEGATIVE ONE**: *reads no
prose ⇒ cannot be exposed* holds; *reads prose ⇒ is exposed* does **not**, since a round may read
prose for titles or sections and never compare a displayed value. **The 12 is an UPPER bound and the
22 is the finding.**
⛔⛔ **AND THE PROXY'S FIRST VERSION MATCHED MENTIONS RATHER THAN READS.** Searching for `DEFINITION`,
`README` and `.md` as words classified nearly the whole arc as prose-reading, because **every round's
docstring discusses the definition** — §4's *a grep is a measuring instrument*, a third time this
window. ⭐ **The fix was not a tighter word list: it was to STRIP COMMENTS AND DOCSTRINGS via AST and
search executable code only.** A mention is not a read. The negative control — R923, which reads only
`.npz` and prior artifacts — went from **False to True** on that change alone, and is what forced it.

⛔⛔⛔ **AND R1078 FINDS THAT THE CENSUS THOSE TWO ROUNDS REST ON EXCLUDES THE ONE CONFIRMED DEFECT.**
R1070's membership test is `cands(t)` — **ONE argument, closing over its container** — and R1076's
classifier required two, so **R1070 has NO rows in that census at all.** The single confirmed exposure
in this repository, the cause of R1075's retraction, **was never among the 38**. ⭐ **And R1076's
positive control passed throughout**, because it checked `has`/`has_rounded`, which happen to take two
arguments: **it confirmed the instrument could see A membership test, never THE one the claim was
about** — §4's row at a new level. R1077's `34 → 12` narrowing inherits the hole.
⛔⛔ **HOW BIG THE MISSING POPULATION IS: UNVERIFIED, AND THAT IS A CONTROL FAILING, NOT A GAP IN
EFFORT.** A one-argument scan returned 249, and **its own sizing control FAILS** — it readmitted
`cls`, `pair_sign`, `rank_obs`, `toks`, `canon`, `content_toks`, `kendall_pairs`, **the very scoring
helpers R1076 removed in three successive repairs**. ⭐ **I reproduced the contamination inside the
round whose entire subject was that instrument's blind spot.** So `249` is **not a count**, no
corrected total is claimed, and **what stands is n = 1, verified — enough to void the census as a
characterisation.**
⛔ **AND THE TRACE QUESTION IS DELIBERATELY NOT ANSWERED.** Tracing arguments through a population
known to be incomplete would produce a tidy number over the wrong set — **precisely the error R1075
cost five rounds to find.** The population is fixed first.

⛔⛔ **AND R1079's PRE-REGISTERED KILL FIRED: THE COUNT IS WITHHELD, AND THREE ROUNDS OF CLASSIFIERS IS
NOW THE FINDING.** Requiring a one-argument closure's free variable to be a **container built from
artifact values** excludes 6 of the 7 known scoring helpers — **and loses `cands`, the only function in
this repository known to have caused a retraction.** Both controls failed, the kill said *withhold*,
and 8 candidates sit in the artifact unreported as a count.

| round | rule | outcome |
|---|---|---|
| R1076 | two-argument shape | 3 repairs, **132 → 38**, still **excluded the one confirmed defect** |
| R1078 | one-argument shape | readmitted **7** scoring helpers; count **withheld** |
| R1079 | closure over an artifact-built container | admits `toks`, **loses `cands`** |

⭐⭐ **Three attempts, three failures.** `membership test` versus `scoring helper` is a **SEMANTIC**
distinction, and it has now been attacked three times from **SYNTAX**. Each attempt was better argued
than the last and each failed a control it could not have passed. **The honest reading is not `try a
fourth rule`: this population cannot be enumerated mechanically at acceptable cost, and every count
built on it inherits that** — R1076's `38` and R1077's `34 → 12` included.
⭐ **AND THAT REDIRECTS THE REMEDY RATHER THAN ENDING IT.** `assurance/valuematch.py` **never needed a
census**: it needs to be the thing reached for at the **point of use**. Enumerating past sites was the
expensive path; **making the next comparison correct is the cheap one, and it was available from R1076
onward without any of this.**

⛔⛔ **AND R1080 KILLS THE REASON R1079 GAVE FOR WHY IT WAS NOT REACHED FOR.** R1079 closed by proposing
that a helper needing a path fiddle gets re-implemented rather than reused. **It needs no fiddle.** The
helper is reachable from every depth this repository contains — a probe placed at component counts
2·3·4·5·6·8, run in three invocation modes, imports it in **18 of 18** in-repo cells using the landmark
idiom this repository already commits **262** times, and **139** committed files already reach into
`assurance/`. All three pre-registered kill conditions fired together.

⭐ **What the grid measured versus what it derived, kept apart.** The `parents[3]` row fails at every
non-canonical depth, and that is a **DERIVATION**: `parents[3]` of a file at component count *d* lands
at *d−3*, which is the root only at *d = 4*. It was executed and it could not have come out otherwise,
so it is the negative control's evidence and **not a finding**. Only the landmark row could have gone
either way, which is why the confound below had to be run at all.

⚠ **The confound, controlled in the same iteration.** A landmark search is depth-robust but would be
**ambiguous** if any directory beneath the root held its own marker. Measured: exactly **1** directory
in this checkout holds a `covalx` child, the root itself — and a **planted decoy** marker does capture
the search, so that uniqueness is a measurement rather than an instrument that never fires.

⭐⭐ **THE FINDING THE ROUND DID NOT GO LOOKING FOR: THE HELPER HAS ZERO STATIC IMPORTERS.** Four rounds
after it shipped, `assurance/valuematch.py` is imported by **no** committed file. The single mechanical
reader is **R1076**, its own author, via `import_module` while verifying it loads. **R1077, R1079 and
R1080 each name it in prose only** — and R1077 and R1079 each *wrote a sentence saying it needs adopting
rather than merely existing*. **The rounds that diagnosed the adoption problem are the population of
non-adopters, and this one joins them.**

⛔ **What is NOT settled, stated as the fork rather than resolved by preference.** World A (mechanical
barrier) is dead. *Unknown to its callers* is already weak — all three non-adopting rounds name the file
by path. *Rounds are conventionally self-contained* is untested. **The discriminator is deliberately not
a fourth syntactic classifier**: asking "did this round have an occasion to use it?" is the same
semantic question that failed three controls in R1076·R1078·R1079. It needs an instrument that finds an
occasion by **execution** — running a comparison both ways and observing a disagreement — not by
parsing.

⭐⭐ **AND R1081 ANSWERS IT BY EXECUTION: THE OCCASION IS THE MAJORITY OF THE CORPUS.** Running both
membership tests over every round that carries prose and an artifact — **368 of 476** eligible rounds
hold a decimal in their own README that **exact matching cannot locate in their own artifact and
precision-aware matching can**. The shuffled-pairing floor is `0.170 ± 0.027`; the within-round
shifted-artifact floor is `0.385`; the observed rate is `0.773`.
⭐ **The worlds separated on the shape, not the size.** Coincidence predicts the gap is flat in
displayed precision; a latent defect predicts it **widens**, because a high-precision token is harder
to hit by accident. Measured, the gap **widens** monotonically: `+0.3363` at `dp≥0` to `+0.6855` at
`dp≥4`. **24 of 24 cells at `min_dp≥2` clear both floors.**
⛔ **4 of 40 cells are KILLED and are reported rather than dropped** — every one at `min_dp = 0` with
integers admitted, where the *shifted* artifact scores `0.959` against a real `0.611`. **An integer
matches anything**, so that cell measures nothing, and the control that says so is the within-round
one the shuffled placebo is structurally blind to.
⚠ **What the count does NOT establish, from the sham's own dose-response.** A blanket 2-decimal
rounding flags **387** rounds where the token's own displayed precision flags **381**. **The count
cannot discriminate the two rules.** It establishes that these prose numbers are rounded renderings
of stored values — not that displayed precision specifically is what is required.
⛔ **And the first sham could not have passed.** It asserted `round(x, 17)` removes the ingredient;
`round(x, n)` is `n` places **after the decimal point**, not `n` significant digits, so below 1 it
still coarsens, and it rescued 7 pairs against a control demanding zero. The repair was to sweep the
dose, not to loosen the threshold: `dp=325 → 0` rounds, `dp=2 → 387`, real `381`.

⛔⛔ **AND R1082 TURNS THE INSTRUMENT ON THE GATE THAT GUARDS THIS DOCUMENT: 3 OF 343 ANCHORS WERE
green because of document ORDER.** `definition_matches_the_record.read_claims` is `re.search(pat,
text)` — the **first** match, over the whole 11,902-line document, once per anchor. **4** anchors
matched more than once and **3** captured more than one distinct value. Prepending the second home's
own sentence made the committed gate **exit 1 on all three**, while prepending a number-free
paragraph changed nothing. **Its agreement with the record was a fact about layout.**
⭐ **The invariant nobody had named:** *an anchor identifies a SENTENCE, and a pattern that matches
two sentences has identified nothing.* R1049 measured this defect class in the **currency** gate —
16 of 63 facts multi-home — and **the repair never crossed to the sibling gate.**
⛔ **The pre-registered kill was mis-specified and its verdict is WITHHELD.** World C — *the document
states one quantity twice with different values* — fires on `Q2 = 3` as written, and as written it
is wrong: **the instrument's unit is a regex match capturing a number; the claim's unit is a
statement of the same quantity.** Read from the object the three hits are three DIFFERENT quantities
— R348's `POOL[0:k]` percentile then R812's `POOL[0:4]`; R432's headroom floor then an unrelated
token-Jaccard floor; `oracle_k4`'s SCORE then its mean selection POSITION. **C is UNVERIFIED: never
admitted, never overturned.**
⭐ **Repaired and guarded in the same commit.** The three patterns now carry context unique to their
intended sentence, and `assurance/an_anchor_binds_to_one_number.py` is wired into `preflight.py` so
the next anchor cannot reintroduce it. It was **attacked six ways** before being trusted, including
the production scenario that broke the old gate — prepending all three rival sentences, under which
the repaired gate holds at `rc=0`. It fails on `distinct > 1` and only **warns** on a same-value
repeat, and that leniency's admitted world is named rather than hidden: **1 anchor (`n_arms_r301`)
sits in it today.**
⚠ **The measurement is pinned to `e0f433c1`** and loads its anchor set from that revision, because
reading the live file would regenerate the artifact from the repaired gate and **the finding would
vanish from its own evidence.** The specification curve is `4 / 3 / 0` in all 8 cells.

⛔⛔ **AND R1083 FINDS THE GATE'S COVERAGE WAS DECIDED BY THE CALLER'S WORKING DIRECTORY.** Eight of
the anchoring gate's artifacts were loaded through a **hard-coded relative path** —
`json.load(open("E05_the_space_of_compilers/A24_…/results/….json"))` — which resolves against the
process's CWD. Measured by running the same gate on the same files from two directories: **0** anchors
`⚠ UNEVALUABLE` from the repository root, **32 of 343** from a round directory, **and it exits 0 both
times**. 9.3% of this document's coverage, silently, in the direction of passing.
⭐ **The route was found by intervention, not by reading.** Blocking each declared round's artifacts
and re-deriving: **32 of 348** keys are unchanged when their **own** declared round is removed, and
the same 32 are killed by **no** single-round block at all. The gate prints a round beside every
number and **nothing verifies it**. The blocker's completeness is a measured cell, not a claim — an
`art()`-only blocker reports **252** instead of 32.
⛔ **AND THIS ROUND'S OWN VERDICT STRING WAS WRONG BEFORE IT WAS CHECKED.** It first said the 32 were
*"a literal in the gate rather than a reading of the record"*. **Nobody computed that.** Zero of the
32 were `None` in the baseline, which is what a literal would have looked like — they read the
record, through the CWD. §4's `the verdict string is not a computation`, committed inside the round
that cites it.
⛔ **R1082's PROPOSED NEXT WAS NOT IDENTIFIED, and that is measured rather than shrugged.** It asked
whether each anchor lands in the region naming its declared round: **166** per-round headings exist
and **83 of the 84** declared rounds have none. A region model would have invented a region for 99%
of the population.
⭐ **Repaired and guarded in the same commit.** All 8 sites now build from the module's own `ROOT`
(`0 / 0 / 0` unevaluable from the root, a round directory and `/`), and
`assurance/a_gate_is_cwd_invariant.py` is wired into `preflight.py`: it runs each watched gate from
two directories and requires the exit code **and** the coverage count to match. **Attacked five
ways** — reverting one of the eight paths turns it red at `UNEVALUABLE 311→315`; neutering its
comparator makes its own POSITIVE control fail and it exits 2. ⚠ It cannot say the coverage two
agreeing runs share is *correct*, and it does **not** make `UNEVALUABLE` fatal — that is a policy
change and is not smuggled in.

⭐⭐ **AND R1084 PRICES BOTH HALVES OF R1083's INSTRUCTION ACROSS ALL 88 ASSURANCE SCRIPTS.** Propose
by parse, confirm by execution: measured, the parse has **recall 1.000** and **precision 0.111** — it
missed nothing and **8 of its 9 proposals are literals the run never reaches**. It is a **sound
NOMINATOR and a poor DECIDER**, and the single script whose behaviour actually moves is
`a_control_that_cannot_fail.py` (`rc 0 → 2`). A stricter proposer gives identical numbers, so the
worry that the loose rule inflates the kill's own cell was unfounded and is now measured rather than
carried as a caveat.
⛔ **AND 41 OF THE 88 SCRIPTS ARE NOT IDENTIFIED FOR THIS INSTRUMENT AT ALL — learned by damaging the
repository.** A script that writes **reads its own previous run's output**, so a two-run comparison
measures the side effect and not the directory. The full-population pass truncated
`assurance/ASSURANCE.md` to **22 of 111** lines, cut **395** from `DEFECTS.json` and churned **943**
in `MANIFEST.json` (all restored) — and **the single FALSE NEGATIVE it produced was itself a
writer**, so the cell that would have killed the finding was an artifact of my own concurrency.
**N/A, with what it would require: one isolated copy of the repository per run.**
⚠ **AND THE EXPOSURE OF R1083's DEFECT IS BOUNDED HERE: it was LATENT, never live.** All three
programmatic runners pin the working directory to the repository root — `preflight.py:57`
(`cwd=ROOT`), `run_all.py:67` (`cwd=ROOT.parent`, where *that file's* `ROOT` is `assurance/`), and
`audit_the_auditors.py:276`. No shell, hook or Makefile caller exists. **I nearly reported the
opposite**, reading `ROOT.parent` through the meaning `ROOT` carries in the other 87 files — the same
error class as the rest of this arc, committed in my own analysis rather than in code.
⭐ **The retraction ledger is written for the first time since R1007, and the entry is a CLASS, not a
list.** Seven retractions in ten rounds — R1075's void premise, three failed classifiers, R1080's
`ast.dump` substrings, R1081's `dp=17` sham, R1082's mismatched unit, R1083's typed verdict string,
R1084's `ROOT` — are **one error: reading a REPRESENTATION as evidence about its REFERENT.** The
remedy that worked every time was the same: **execute the thing.** Detail: `RETRACTIONS.md`.

⛔ **And one control earned the round.** The census classifier's POSITIVE control went **red on the
first run**: it matched substrings of `ast.dump()`, which emits `Name(id='next', ctx=Load())`, so
`"Call(func=Name(id='next')"` can never fire. It labelled **all 262** committed landmark searches
`other`. Had the control not existed, `k2` would have read **False** and this round would have
concluded that world A survived. **Matching a serialisation of a tree is a text scan wearing an AST's
clothes** — R1077's lesson one level up.

⛔⛔ **THE CLAUSE TEXT ITSELF IS REPAIRED HERE (R1032), NOT ANNOTATED BESIDE.** It read *"resolvably
beats **EVERY** comparator in the certified prompt-blind set"* until R1032 measured that the
as-written reading and the repaired one **compute different extensions**: identical under `A2`
(9 = 9, three seeds) but differing by **2 arms under `A1·consensus`** — `coval_core_2bA` and
`coval_core_2bB`, the twins, admitted only because the as-written operator **imputes 768 of their 968
values** (R1021). **R1024's repair and R1011's withdrawal are one correction reached by two routes,
and this sentence still encoded the version that needed withdrawing.**
⭐ **The shipped figures are unaffected**: R1019 established every extension figure in this arc is
`A2`'s answer, and the two readings agree there. The staleness bit only on a target the arc does not
report under — which is why it survived four rounds of annotation.
⚠ `EVERY` is dropped rather than replaced by `generic` because R1025's reduction is **release-scoped**:
`generic` binds 94/94 here, and naming it would harden an accident of this release into the
definition. The set is named; which member binds is measured, not asserted.

⛔⛔ **AND R1033 MEASURED THAT THE CHOICE WAS LOAD-BEARING, BY BUILDING THE SEPARATING OBJECT FOR
FREE.** `score.yvec(sat_p, idxs)` sums over an arbitrary criterion subset and `sat_genericpool16.npz`
holds all 16 × 4 × 968 cells, so **every subset of pool16's criteria is a fixed checklist —
prompt-blind by construction, and already scored. A third certified comparator costs 0 judge calls,
not `968 × 4 × k`.**

Over a family pre-registered **by size** (713 subsets, k ∈ {1,2,3,15,16}), **35 are stricter than
`generic`'s 24**; the strictest admits **17** at k=2, and its strictness **holds out** (15 vs 24 on
prompts it was not selected on, 3 seeds).

⭐ **Adding it removes 6 of the 9 extension arms** — `topw_k3`, `topw_k4`, `topw_k4_detA`,
`topw_k4_detB`, `topw_k6`, `topw_k8` — **leaving `coval_core` and its two twins.** So the extension is
not robust to a comparator that costs nothing to add, and the arms it loses are exactly the
non-instance ones.
⚠ **R1026 is not contradicted**: 2 of 96 *arms in the release* are prompt-blind, and that stands. What
falls is the implication beside it, and in R1027's cost line, that a third comparator must be **built
and scored**.
⚠ **N/A:** whether a stricter comparator exists *outside* pool16's criteria — that needs new criteria
scored at `968 × 4 × k`. This bounds what is reachable from the committed cells.

⛔⛔⛔ **AND R1034 CLOSES THE SET AND FINDS THE CLAUSE VACUOUS.** ②′ requires beating **every** member,
so under a **closed** set an arm is admitted iff it beats the **strictest** — and closure under
`fixed` contains all **65,535** subsets of pool16's criteria, all already scored. Over a sample
pre-registered by size and seed (**4,261** checklists, all sizes, 400/size at seed 77):

| operator | extension, 3 seeds |
|---|---|
| committed (**imputing**) | `coval_core_2bA`, `coval_core_2bB` — **`coval_core` is NOT among them** |
| **R1024-repaired** | **∅** |

Both survivors under the imputing operator are the **twins**, 79% imputed (R1021) and **already
withdrawn** by R1011. **With the repaired operator nothing survives.**
⭐ **So ②′∧③ admits nothing once its own certification predicate is closed and its own operator repair
is applied — the 9-arm extension exists only because the set was never closed.**
⛔ **Emptiness is EXACT, not a bound**: adding comparators can only remove arms, so the remaining
61,274 could only remove more. (Survival, had there been any, would have been the upper bound.)
⚠ **N/A** — the exhaustive 65,535-mask closure with a full bootstrap is ~254 GFLOP per seed; what it
would require is the matrix form at float32 on the GPU.

⛔⛔ **AND R1034's `∅` IS SEED-DEPENDENT — R1035 WITHDRAWS THE WORD `EXACT`.** Two of my own rounds
disagreed: R1034 measured `∅` at q=100 under seeds (1034, 2068, 3102); the same construction at
(1035, 2070, 3105) admits `coval_core`. Measured across **seven** seeds including R1034's own,
`coval_core` is admitted in **4 of 7**, with min `lo` in **[−0.000167, +0.000484]** against R923's
reference scale of **+0.005736** — **34× larger**. **The boundary sits inside the design's
resolution: the extension under closure is neither `∅` nor `{coval_core}` but UNRESOLVED.**
⭐ R1034's **monotonicity** argument survives — more comparators can only remove arms. **What falls is
calling the measured `∅` exact.**

⭐ **AND THE CURVE IS WHAT STANDS, NOT THE ENDPOINT.** Requiring an arm to resolvably beat **≥ q%** of
the family gives a small, stable, non-empty extension, **seed-identical at all seven seeds**:

| q | 0 | 50 | 75 | 90 | **95** | **99** | 100 |
|---|---:|---:|---:|---:|---:|---:|---|
| \|ext\| | 73 | 12 | 12 | 11 | **9** | **8** | ⚠ seeds disagree |

Only q=100 is unstable — exactly where a **maximum over a search** sits. ⛔ The device is **R863's**,
which bounded clause ④'s 1,820-member family at `null_p95` rather than its max; what is new is the
curve for ②′.
⚠ **N/A** — whether a quantile bound is the *right* clause is construct validity, needing an external
criterion this release does not carry.

⭐⭐ **AND R1036 SELECTS q, WITHDRAWING R1035's CLOSING SENTENCE.** R1035 asserted the curve *cannot*
choose among q ∈ {50…99}. It can — by **scale-stability**, the device R848 already used for clause ④
(its bar rose **0.0074 per ln(n)**, the signature of a **maximum**). A quantile has no such drift, so
sweeping **family size** selects q where sweeping q alone cannot.

⭐ **And scale-freeness is not binary — it has an ONSET family size that grows with q:**

| q | 50 | 75 | 90 | 95 | 99 | 100 |
|---|---:|---:|---:|---:|---:|---|
| onset n | 100 | 100 | 100 | 300 | 2000 | **never** |
| \|ext\| | 12 | 12 | 11 | 9 | 8 | — |

**The clause's cost is therefore not a threshold but how much family you must enumerate to state it**,
and **q=100 cannot be stated at any size reached here** — the max-over-search seen as a rate rather
than a cliff. ⚠ q=0 is excluded as **degenerate**: it imposes no requirement and admits 73 arms.
⚠ **Scale-stability is necessary, not sufficient** — a size-independent q can still be the wrong bar,
and deciding that needs an external criterion for what the comparator family represents. **N/A.**

| | |
|---|---:|
| extension under `generic` alone | 9 |
| extension under `genericpool16` alone | 12 |
| **②′ — the intersection** | **9** |
| `coval_core` survives | **yes** |
| `generic`, `generic_reprov` excluded | **yes** |
| only other loss | `topw_k2` |

**The repair costs three arms and keeps the instance.** ⚠ And note the intersection equals
`generic`'s extension exactly, i.e. **`generic`'s extension is contained in `genericpool16`'s** —
**measured, not derived**: resolvable beats are not transitive in general, so this is a fact about
this release and not a theorem.

⭐⭐ **R1025 STRENGTHENS THAT SET FACT TO A PER-ARM ONE, AND THE CONSEQUENCE IS A WORDING CHANGE:
ON THIS RELEASE `every comparator` REDUCES TO `generic`.** The containment above is a statement about
two *sets*, and a set containment can survive individual arms flipping in both directions as long as
they cancel. At the level of the **bound itself** they do not flip at all: `Δlo = lo(A,generic) −
lo(A,genericpool16)` is **negative for 94 of 94 candidates on `A2` and 94 of 94 on `A1·consensus`**,
with **zero resolved sign flips** against each arm's own 3-seed spread (median |Δlo| 0.00911 / 0.00517
against floors of 0.00021 / 0.00103). So `min` over the certified set **always** selects `generic`,
and the second member never binds.

⛔ **And algebra — not that measurement — caps what the quantifier could ever have meant.** R921's
committed derivation records that `mean margin(A,C) = mean A2(A) − mean A2(C)`, whose second term is
identical for every `A`; verified here as a falsifier at a span of **6.9e−17** over 97 arms. So the
**point-estimate ordering is comparator-invariant**, and the entire content of *"every comparator"* is
**which comparator gives the tighter interval** — never which arm is better, only how confidently
that is known.

⚠ **The verdict flipped twice on audit, both times on a degenerate diagonal wearing a name.** The
first pass found 2 resolved flips (`generic` — which *is* a comparator, so `lo ≡ 0`) and then 1
(`generic_reprov`, whose paired sd against `generic` is **exactly 0.0000** on `A1·consensus`; it *is*
`generic` there under another name). Both would have been reported as evidence that `every` is
irreducible. The rule that removes them is mechanical and general: **an arm is not a candidate
against comparator `C` on target `T` if its paired sd against `C` is exactly zero there.**

⚠ **What does NOT follow: that the clause is safe to simplify in general.** A third comparator could
bind, and none has been built. **N/A here, with the cost named:** a comparator that is not already a
scored arm costs **`968 × 4 × k` judge calls** — 3,872 at k=1, 15,488 at k=4, 61,952 at k=16 (R1027).
⚠ This line first said a flat **15,488**, which is a k=4 arm's price; the correction is one round
later and is recorded at the head of this file. **Sites 3 of 3** — the same wrong constant was
written in three places, and a correction that reaches two of them leaves the third quotable.

⛔⛔ **CORRECTED BY R1026 ONE ROUND LATER — "CERTIFIED 2 FROM A LARGER POOL" WAS WRONG, AND IT IS
REPLACED RATHER THAN CAVEATED.** This section first said the certified set is *"a choice the clause
never mentions — R921 certified 2 comparators from a larger pool"*. Read from the source, R918
computes the `fixed` predicate over **96** arms and **exactly 2 satisfy it**. There was **no selection
among viable alternatives**: the predicate is a filter and it admitted everything that qualified.

⭐ **And the replacement is a stronger statement, not a weaker one.** The set is the **complete
population of prompt-blind arms in this release**, so **clause ②′'s satisfiability is hostage to the
release containing such arms at all** — a constraint belonging to the RELEASE, not to the definition.
Joining R921's counts to R918's properties: **26 of 99** arms are stricter than `generic`, and
**0 of them are prompt-blind** — 23 have `exact = 1.0` (their selection is a subset of *that prompt's*
rubric) and the remaining 3 are the instance and its twins, which cannot be their own comparator.

⚠ **And the predicate that decides this was itself uncalibrated until R1026.** Its chance base rate:
a prompt-blind draw lands inside a prompt's own rubric at **0.0000** for every k ∈ {2,3,4,6,8,12}
(binomial SE ±0.0093), against **1.0000** for a draw from the prompt's own rubric.
⛔ **Most of that is FORCED** — pool **14,810** vs median rubric **15** is a **987:1** ratio, so the
analytic chance is 1.03e−06 at k=2 and 1.17e−36 at k=12. What was genuinely unknown is **the ratio**.
⭐ **The cell that could have failed is the SHAM**: drawing *real* criteria from *another prompt's
real* rubric also lands at **0.0000**, and directly, **0.0000 of adjacent prompt pairs share any
criterion at all.** **Rubric criteria are prompt-unique across this corpus** — a fact about the
release, and the thing that licenses reading `exact` as *prompt-matching* rather than *"rubric-shaped"*.

**Controls.** R922's cut and count reproduced at 1e-9; `coval_core` admitted under both comparators;
**an arm is never admitted against itself** (the paired difference is identically zero, so `lo > 0` is
False — without this the counts would be void); and `topw_k4_sham`, the same operation with the
ingredient inverted, is **excluded** under both. A definition that admits the sham has no content.

⚠ **What this does not say:** that the release *intends* `generic` to be a candidate arm. R921
certified it as a **comparator**; nothing says it may not also be scored, and the definition as
written places no restriction. **The silence is the defect, and the repair removes it.**

### ⭐⭐⭐ THE FORMULATION THIS ARC HAS EARNED — two conditions, and both of them bind (added 2026-08-07, R1004)

Twenty-nine rounds of this arc killed wordings. **This is the one that survives all of them**, and it
is stated as a product rather than as another defect.

> An arm is a **CORE** iff
> **②** it **resolvably beats a NAMED prompt-blind comparator** — the 2.5th percentile of the
> bootstrapped paired difference is > 0 — **and**
> **③** it **consumes no prompt-specific human labels.**
>
> **Reported, never required:**
> **①** its **size** (max realised), because R1000 measured **0** unique removals — it describes, it
> does not filter;
> **④** its **margin over a DECLARED response-only class**, as a **lower bound with its interval**,
> because R1003 measured that as a *filter* the clause is **vacuous or empty at every setting**.

**Both conditions bind — neither is an ornament:**

| comparator | ② admits | ③ admits | **extension** | **② unique** | **③ unique** | `coval_core` in |
|---|---:|---:|---:|---:|---:|---|
| `generic` | 24 | 73 | **9** | **64** | **15** | **yes** |
| `genericpool16` | 28 | 73 | **12** | **61** | **16** | **yes** |

⭐ **And it is stable where the release has the prompts for it.** Churn against the full-corpus
extension, R978's subsampling design, 3 seeds: **median 0 at N = 726**, **0 at N = 484** under
`genericpool16`, and **5 at N = 242** — where one seed collapses the extension to **0 arms** outright.
**That is consistent with R980's ~500-prompt requirement and it is the honest boundary of the claim.**

⛔ **ONE CELL HERE IS A DERIVATION AND IS LABELLED AS SUCH.** "Dropping ④ changes the extension by 0"
could not have come out otherwise: R1000 measured ④'s unique removals as **0**, and *removes nothing
uniquely* ⇒ *dropping it changes nothing* **by definition**. It is bookkeeping confirmation, not
evidence, and it is the reason R1003's NEXT was not run as written.

**Controls.** R922's cut and count at 1e-9; `oracle_k4` fails ③; both conditions disabled admits all
96; the intersection is order-independent.

⚠ **WHAT THIS CANNOT SHOW — and it is the limit of the whole arc.** That the extension is the
**right** one. That needs an external standard for what a core is, and **the release ships none**: its
own card calls core *"a proof of concept … an invitation for others to develop and validate better
synthesis and aggregation methods."* This formulation is **coherent and non-vacuous on this release**;
it is not validated against a ground truth, because none exists to validate against.

⚠ **Cross-dataset — N/A.** One release. It would require a second release carrying human rankings
over the same response sets.

### ⛔⛔⛔ CLAUSE ④ HAS NO VIABLE SETTING AS A FILTER — every class is either vacuous or empties the definition (added 2026-08-07, R1003)

Every prior verdict on clause ④ was reached in a **different unit system** — R849 on annotator parity
halves, R825/R826 on prompt splits, R847 on 1,078 prompts — and comparing across them is this arc's
recurring error. **Rebuilt on ONE ruler** (A2, 968 prompts) under **one protocol** (R825's own: select
on the fit half, score on the eval half, 8 splits):

| class | bar | ④ admits | conjunction | ④'s unique removals | `coval_core` in |
|---|---:|---:|---:|---:|---|
| lexical-394 (R849's class) | 0.481738 | 58 | 9 / 12 | **0 — vacuous** | yes |
| lexical-394 ∪ {char-n-gram witness} | 0.572551 | 14 | **0 — empty** | 9 / 12 | **no** |
| the witness alone (permissive) | 0.572551 | 14 | **0 — empty** | 9 / 12 | **no** |

⭐⭐⭐ **So clause ④ cannot be stated as a filter on this release: at every setting it either does
nothing or admits nothing.** There is no class between them, because the third row is the second row
— once the witness is in, it *is* the max.

### ⭐ THE DEBT R1002 REFUSED TO PAY, NOW LEGITIMATE

R1002 declined to say how far the bar moves when the witness is admitted, because the two numbers
were on different splits. On one ruler and one protocol:

```
admitting ONE admissible rule:   0.481738  ->  0.572551      = +0.090813
coval_core's margin over R849's class:                          +0.084740
```

⭐⭐ **The released core's entire margin under the surviving wording is SMALLER than what a single
admissible rule adds to the bar.** That is R1002's closure failure with a magnitude attached, and it
is why "name the class" cannot rescue the clause: the verdict is decided by one membership decision,
not by the object.

**Controls.** `coval_core`'s A2 reproduces **0.566477**, the value R825 compared its bar to — so the
imported bar sits on the same ruler. R849's own selected rule `+mean_word_len+uppercase` comes back at
**median rank 1 of 394** on the fit halves, so this re-implementation picks exactly the rule R849
picked. A constant rule lands at **0.139736**, far below the bar. A one-rule class's max equals that
rule. R922's cut and count reproduce at 1e-9.

⚠ **Corroboration, not reproduction:** B(lexical) here is **0.481738** against R849's committed
**0.482016** — agreement to ~3e-4 across **different split protocols** (prompt vs annotator parity).
That is convergent evidence, and it is not the same measurement.

⚠ **The union bar is a max of two MEANS.** R826 committed the witness's bar as a mean over its splits,
not per split, so the union class's variance is understated. Its point value — the quantity used — is
unaffected.

### ⛔⛔⛔ THE SURVIVING REPAIR'S REFERENCE CLASS IS NOT CLOSED UNDER ITS OWN CLAUSE (added 2026-08-07, R1002)

R1001 left exactly one wording standing: entry 1368's repair — *"exceeds, by a margin reported with
its interval, the best rule in a **NAMED reference class R**"* — instantiated by R849 as **394
response-only rules**, the only form under which the definition admits its own instance.

**R is not closed under the predicate the clause quantifies over.**

Re-enumerated from R849's own construction and reproducing its committed count **exactly**:

```
14 hand-picked lexical features
   30 singletons  +  364 signed pairs  =  394      (R849 committed 394 — positive control PASS)
```

⭐ **So R is: every linear rule in AT MOST TWO of fourteen hand-chosen lexical features.** The clause
says *"every rule computable from responses alone."* **R825's char 3–5-gram TF-IDF + SVD predictor is
computable from responses alone, is not in R, and is known to beat the instance.** Witness exhibited.

⛔ **THE REPAIR INHERITS THE DEFECT 1368 DIAGNOSED, ONE LEVEL UP.** 1368 killed the universal
quantifier because *"every"* ranged over a convenience family. The repair replaced *"every"* with
*"the best rule in a named class R"* — **and R is a convenience family too.** Naming it makes the bar
**honest and reproducible**; it does not make it **closed**. ⭐ **The definition's verdict on its own
instance is therefore a property of a boundary we drew.**

⭐ **AND THAT IS A DERIVATION, NOT A MEASUREMENT.** A max over a superset is ≥ a max over a subset,
by definition. No experiment can overturn the closure failure; an experiment could only say **how
much** the bar moves — which is **not claimed here**, because R825's number is on its own 12 splits
and R849's is on parity halves. **Different splits, different units, not compared.**

⚠ **NOT the size axis, which is prior art.** R847 enlarged the family once (bar **raised**, not
crossed) and R848 gave the dose-response, **+0.007412 per e-fold**, with an extrapolation whose own
artifact key reads `extrapolated_n_for_core_D4_NOT_A_MEASUREMENT`. This is about **closure**, and it
does not re-ask either.

⚠ **The one disputable step, stated rather than hidden in a boolean.** R825's source touches the
human ranking, because *scoring* any rule needs it. Reading the witness as response-**only** is a
judgement about what the **rule** consumes versus what its **evaluation** consumes. It is R826's own
framing — that artifact calls the family response-only — and it is the step a reader could reasonably
dispute.

**Controls.** Re-enumeration reproduces 394 exactly, which is what makes my reading of R *be* R849's
R; R849's own selected bar rule `+mean_word_len+uppercase` tests as a member; and a rule that
consumes the human ranking (`oracle_k4`) is outside R **and** inadmissible under the clause — without
that control, *"outside R"* alone would make every arm in the release look like a witness.

### ⛔⛔⛔ AND UNDER THE PERMISSIVE READING THE OPERATOR ADMITS NOTHING — BECAUSE ③ AND ④ ARE DISJOINT (added 2026-08-07, R1001)

**R1000's headline is READING-DEPENDENT and is restated here with its reading attached.** Running the
same operator with clause ④ read permissively, swept over **R826's whole effort curve**:

| | enumerated reading (R849) | **permissive reading (R825/R826)** |
|---|---|---|
| conjunction admits | 9 / 12 of 96 | **0 of 96, in 20 of 20 saturated cells** |
| `coval_core` in it | **yes** | **no, in 20 of 20** |
| clause ④'s unique removals | **0** — inert | **9 / 12** — load-bearing |

⚠ **PRIOR ART, and it is in this very document.** *Entry 1368* and R824 already committed **"the
extension is EMPTY"** under the permissive reading, and **"clause ④ as written cannot both do work and
admit its own instance."** So the table above is a **CONFIRMATION by a different route** — the full
four-clause conjunction over 96 arms rather than ④'s exclusions alone — and **not a discovery.**
⭐ *It was caught because the currency gate refused to go red on arrival: the statement already
matched. An instrument built to catch decoration caught a rediscovery instead.*

### ⭐ WHAT IS ACTUALLY NEW — the mechanism, which entry 1368 does not state

At R825's own k = 100 (bar **0.572551**), clause ④ admits **14** arms of the 96. **All 14 read human
rankings, and therefore fail clause ③.**

```
④ admits            14
of which supervised  14      ⇒ ④ ∧ ③ = 0, before clause ② is even applied
```

⭐⭐⭐ **Clauses ③ and ④ have DISJOINT satisfaction sets on this release.** The permissive bar is set
so high that **the only arms that clear it are the ones that consume the labels ③ forbids.** Entry
1368 said ④ *"cannot both do work and admit its own instance"*; this says **why**, and the reason is
not internal to ④ — it is a **direct conflict with a different clause**. The definition is not merely
reading-dependent; under one reading **two of its clauses cannot be jointly satisfied by anything**.

⚠ **THE BAR IS TREATED AS FIXED.** R826 reports its sd (0.0062–0.0079) but not R825's 12 per-split
values, so the `lo > bar` shape carries the **arm's** error and not the **bar's**. Named direction:
conservative for admission, **anti-conservative for exclusion**. Closing it needs those 12 values.

**Controls.** R922's cut and count reproduced at 1e-9; the k = 0 bar must and does admit the core
(R826's own committed verdict there is *"admits core"*); `oracle_k4` fails ③ and `topw_k1` fails ①;
a bar of 0.0 admits all 96 and a bar of 1.0 admits none; and at k = 0 clause ④ has **0** unique
removals — a non-zero there would have meant the join was broken. Verdicts are taken **only** on
R826's saturated cells (k ≥ 40); the four unsaturated cells are shown for contrast and used for
nothing, because a threshold below saturation measures modelling effort rather than a clause.

### ⭐⭐⭐ THE FOUR CLAUSES RUN AS ONE OPERATOR — AND TWO OF THEM ARE ORNAMENTS (added 2026-08-07, R1000)

**Twenty-six rounds studied the clauses separately. This is the first time the definition was applied
as a single operator**, and the result is the one thing the quest was for.

**⭐ THE RELEASED CORE IS ADMITTED BY ITS OWN DEFINITION, in both comparator cells.** That could have
failed — R825 had already shown clause ④'s *permissive* bar excluding `coval_core` outright — and it
is the first evidence that the four clauses, taken together, describe the object they were written
about rather than a family that happens to exclude it.

**The extension is small.** Over the **96-arm** population (the intersection of the three artifacts;
`full`, `full_sham` and `genericpool16` carry no size record and are named as dropped):

| comparator | conjunction admits | `coval_core` in it | conjunction == clause ② alone |
|---|---:|---|---|
| `generic` | **9 of 96** | yes | no |
| `genericpool16` | **12 of 96** | yes | no |

**⛔ AND THE PRE-REGISTERED KILL FIRED ON TWO CLAUSES.** Counting, for each clause, the arms it
removes that **no other clause removes**:

| clause | admits alone | removes | **unique removals** |
|---|---:|---:|---:|
| **①** size > 1 | 94 | 2 | **0** |
| **②** resolvably beats a prompt-blind comparator | 24 / 28 | 72 / 68 | **10 / 7** |
| **③** consumes no prompt-specific labels | 73 | 23 | **15 / 16** |
| **④** beats every response-only rule | 39 | 57 | **0** |

**Clauses ② and ③ carry the entire extension. ① and ④ remove nothing the others do not.**

⛔⛔ **CORRECTION, added 2026-08-07 while building R1005 — HALF OF THIS WAS ALREADY IN THIS DOCUMENT.**
**Clause ①'s inertness is PRIOR ART, and R1000 presented it as a finding.** This file's own section
*"① — a consequence, not a test"* (from the R327–R347 work) already states that on this arm space
clause ② **implies** clause ①, that the cell *(① fails, ② passes)* is **empty**, that it is empty
**by derivation** — a counterexample needs `GAP < SLACK` and the measured minimum GAP exceeds the
maximum SLACK on all 41 arms — and it closes with the instruction **"State it as a consequence and
stop presenting it as independent evidence."** ⭐ **R1000 did exactly what that sentence forbids.**
**What R1000 legitimately added for ①** is scope: 41 arms → **96**, and pairwise ①-vs-② → unique
removals under the **full four-clause conjunction**. That is a widening, not a discovery, and the
headline should have read *"one ornament, confirmed; one newly measured."* **④'s inertness is the
genuinely new half** and is unaffected. Recorded here rather than by editing R1000's artifact, which
is a record of what that round computed (L81).

⚠ **THAT IS A FACT ABOUT THIS RELEASE'S ARM SET, NOT A PROOF EITHER CLAUSE IS EMPTY.** Exercising ①
or ④ requires an arm that violates *only* that clause, and this release contains none. The two arms
① removes — `topw_k1`, `topw_k1_08b` — are removed by ② and ④ as well.

⛔ **AND ④'s INERTNESS IS A DERIVATION, not a measurement.** Clause ②'s extension is **strictly
contained** in clause ④'s under both comparators, at a minimum R849 margin of **+0.0714** (`generic`)
and **+0.0633** (`genericpool16`) — comfortably clear, not knife-edge. So ④ adds nothing *given* ② by
set containment: **everything that resolvably beats a prompt-blind comparator on this release already
beats the enumerated response-only bar.** ⚠ The two bars themselves — ④'s 0.482016 on R849's even
half, ②'s cut 0.559311 on the full sample — are **in different units and are not compared**; what is
checked is the containment, which is unit-free.

⚠ **NOT MEASURED — clause ④ under the PERMISSIVE reading.** R825's bar reaches the core (0.572335 vs
0.566477, 12 of 12 splits) and R826 puts it on a plateau that *straddles* it. Neither committed a
99-arm extension, so **the conjunction cannot be evaluated there at all.** It would require a 99-arm
scoring run at the permissive bar, held out on R825's own 12 splits. Under that reading ④ would
almost certainly stop being inert — and would exclude the instance. **The clause's inertness is a
property of the reading, and the definition does not yet say which reading it means.**

**Controls.** ② reproduced R922's committed cut and count at 1e-9 under both comparators; `oracle_k4`
must and does fail ③; `topw_k1`/`topw_k1_08b` must and do fail ①; with every clause disabled the
operator admits all 96; each clause is idempotent.

### ⛔ WHAT THE EXTENSION IS, AND HOW MUCH OF THE CORPUS IT RESTS ON (added 2026-08-07, R978–R980)

**The admitted set is not a list. It is a list-at-an-N.** Clause ② is a *resolvable* beat, so its
extension inherits a bootstrap interval that widens as `1/√N` — the same mechanism that bounds
clause ④, one clause over.
- **The admitted set moves with the prompt count** (R978). Median churn against the full-corpus set,
  three seeds: at **N = 242, 10 of the 24 arms admitted under `generic` change**; under
  `genericpool16`, 2. At N = 726 and above, 0. Bracketed above by the count of arms within
  `z·sd/√N` of the cut, registered from the full data before the sweep.
- ⚠ **A stricter bar is not a more stable one.** `generic` has the higher cut and the smaller
  admitted set, and churns **five times more** than `genericpool16`.
- **How many prompts the definition needs to admit its own instance** (R980). Admission becomes
  resolvable at `N* = (z·sd/margin)²`. For `coval_core` against `generic` the margin is **+0.015123**
  and **N\* = 237** — the coin-flip point, measured crossing at grid point 240. It reaches 10 of 10
  seeds only at **N ≈ 500**. Against `genericpool16`, N\* = 94.
  ⚠ **So "we used 968 prompts" overstates the headroom by roughly 2×.** For contrast, `oracle_k4`
  needs **9** prompts, and `random_k4_s0` is never admitted at any N. **The released core sits ~26×
  closer to the bar than the arm this benchmark treats as its ceiling.**
  ⭐ This is **not** fragility at full N: there the verdict is deterministic and the instance is in.
  It is a statement about how much of the corpus is load-bearing — about a quarter.

### ⛔ WHERE THIS DEFINITION DEPARTS FROM THE RELEASE'S OWN CARD — stated, because it was not (R988–R990)

`data/DATASET_CARD.md` describes how a core is built: *"we keep only a small set of highly rated,
**non-redundant**, and **non-conflicting** rubric items … it aims to select **up to four** … that
remain compatible with each other and do not repeat the same idea."* **Three departures, and until
now none was written down anywhere.**

| the card | this definition |
|---|---|
| size: **up to four** — an **upper** bound | clause ①: **greater than one** — a **lower** bound |
| **non-redundant** | *no clause* |
| **non-conflicting** | *no clause* |

- **The missing upper bound admits objects the release could not produce** (R988). Of 96 prompt-pool
  arms, 28 exceed four and clause ② admits **4** of them: `greedy_k8_fit1` (8), `indep_k8_fit1` (8),
  `topw_k6` (6), `topw_k8` (8). Control: the operator also admits **20 of 68** arms at or below the
  cap, so this measures the cap and not the operator.
- **Non-redundancy is a REAL property, so the missing clause is a real gap** (R990). Within-core
  criterion pairs overlap less than size-matched pairs from the same prompt's full rubric, by a
  **difference-in-differences of −0.0084** against cross-prompt vocabulary baselines, resolved on
  3 of 3 seeds. ⚠ The measure is **lexical and one-directional**: high overlap ⇒ repetition, low
  overlap ⇏ distinctness. ⭐ And the confound ran *against* the finding — the raw gap is −0.0063, so
  correcting for synthesis vocabulary **enlarged** it.
- **Non-conflict is not reachable from this release** (R989). Core items publish a criterion string
  and **no weights**, and only **7.8%** match a full item verbatim, so what a particular core
  reconciled cannot be recovered. ⚠ And a related number must not be misread: **80.0%** of full
  rubric items have annotators disagreeing in sign, but against a permutation null of **93.3%**
  [92.9, 93.8] that means criteria are **more sign-coherent than chance**, not less.

⭐ **The departure may be right** — the card calls core *"a proof of concept … an invitation for
others to develop and validate better synthesis and aggregation methods"*. But a definition that
silently inverts the direction of its source's own size criterion is departing **by omission**, and
this section exists so that it no longer is.

#### ⭐ DECIDED (R994): the cap is REFUSED, and the reason is measured

**The size departure stays open deliberately.** Clause ① keeps its lower bound and gains no upper
one. The reason is not that the card is only an invitation — it is that **the cap's boundary is below
this release's resolution.**

The cap would uniquely exclude two arms (R992–R993). Against `coval_core`, paired over the same 968
prompts, 8000-draw cluster bootstrap, 3 seeds:

| arm | size | margin vs `coval_core` | 95% CI | resolvable? |
|---|---|---|---|---|
| **`topw_k6`** | 6 | −0.002360 | [−0.00786, +0.00328] | **NO** |
| `topw_k8` | 8 | −0.007166 | [−0.01318, −0.00114] | yes (worse) |

**`topw_k6` is indistinguishable from the instance the cap would keep.** Adopting the cap would
assert a distinction this release cannot support — **which is exactly how the number "four" entered
this definition the first time**, and the failure the standard records under *a definition that names
a number it cannot resolve*.

⭐ **The statement's own parenthetical was checked, not assumed**: `topw_k3` vs `topw_k8` is
unresolvable (margin −0.003865, CI [−0.00997, +0.00219]), so *"sizes 3 to 8 are not distinguishable"*
holds as a positive control on the premise. And the instrument can resolve — `random_k4_s0` sits
resolvably below the instance at −0.073790.

⚠ **`topw_k8` IS resolvably worse than the instance and still clears clause ②.** Excluding it is
available to the bar on the metric; it does not need a size clause, and reading this as an argument
*for* the cap would be taking the one arm the evidence separates and generalising from it.

⛔ **THIS REOPENS IF** a release's design resolves sizes 3 from 8. That condition — not the verdict —
is the thing to watch.

### ⛔ WHAT `ITS SIZE` MEANS — the clause named a scalar the released core does not have (R986–R987)

**`coval_core`'s per-prompt size runs 2 to 4**, and **34 of 96 arms have no single size at all**. So
*"Its size … is greater than one"* names a scalar property the instance lacks. The variation has two
causes and only one belongs to the arm:
- **pool capping** — the prompt offers fewer criteria than the rule requests, so the realised size is
  `min(k, pool)`. **A property of the PROMPT**: every `k12`, `k8` and `k6` family shares a
  byte-identical per-prompt profile. It explains **28 of the 34** variable arms entirely.
- **arm selection** — the arm takes fewer than the pool allows. **6 arms**, `coval_core` among them
  on **43 prompts (4.4%)**, `gen` on 2.

**⭐ THE READING ADOPTED: nominal size = the MAXIMUM realised size over prompts.** Two reasons, and
they are of different kinds:
1. **Argument, not measurement** — a definition of `core` whose verdict moves because one prompt
   offered fewer criteria is answering a question about the corpus. The reading must quotient pool
   capping out, and the maximum does.
2. **Measured (R987)** — the maximum **is recoverable from the artifact alone**: it reproduces the
   independently recorded `k` on **40 of 40** arms, including **12 where the pool genuinely binds**
   and **4 whose capping model has a residual**. So **clause ① is artifact-checkable, and the
   definition has exactly ONE provenance clause — ③, not two.**

⚠ **This resolves a live disagreement rather than a hypothetical.** Under *min per-prompt size* `gen`
fails clause ① (its minimum is 1); under the adopted reading it clears at 4. **`coval_core` clears
under every reading** — its minimum is 2 — so the defect was the clause's TYPE, never its verdict on
the instance.
⚠ **The parenthetical is worse off than the clause.** *"Sizes 3 to 8 are not distinguishable"*
presumes each arm has one size to compare; **34 of 96 do not**, and under the adopted reading it
should be read of nominal size.
⚠ **Still authorial, and not settled here:** whether SIZE is the right property for a definition of
`core` at all.

**③ has no artifact-level ordering content** (R979). R920 settled world C on `R² = 0.998412`, but
`R²` is a magnitude statistic and a clause admits by **ordering**. Counting inversions instead — the
instrument R922 used for clause ② — `pi` and the A2 margin disagree on **2 of 78 pairs**, and **0 of
those 2 are resolvable** on A2 (gaps of −0.00427 and −0.00097, both far inside the resolution of
0.0099555). So ③ never reorders a pair this design can order, and it is **irreducibly a provenance
requirement**: not checkable from an artifact, now measured rather than argued.
⚠ R920's `n` is **13 independent units, not 21** — six duplicate clusters. Recomputed on the 13, R²
is 0.998205 and Spearman 0.983516, so the duplication does **not** inflate the statistic; the
correction is to the `n` a later round must quote.

**The metric is `A2`, the graded per-prompt agreement**, and naming it excludes a real reading:
under exact-class agreement `coval_core` sits below its floor and fails clause ② itself.


⛔ **THE STATEMENT NAMES ITS JUDGE AND NEVER ITS METRIC (entry 1349).** *"Scores better, under a named
judge J"* is incomplete: **J produces a score, and the statement never says which one.** `A2` — the
graded per-prompt agreement every clause is actually computed on — first appears at **line 200 of this
file, inside an annotation**, and nowhere in the statement.

**That omission is load-bearing, and R243 measured how much.** The triple-blind arm disagreed on
**sign** over exactly this choice, and the sweep of it reads:

| what "a match" means | core | floor | core − floor |
|---|---:|---:|---:|
| **exact class — ≥ 6 of 6 pairs** | 0.3864 | 0.3891 | **−0.0027** |
| ≥ 5 of 6 | 0.7603 | 0.7331 | **+0.0273** |
| **graded, mean pairwise** *(what A2 is)* | 0.8321 | 0.8253 | **+0.0068** |

⭐ **So the clause should read *"scores better, under a named judge J, ON THE GRADED PER-PROMPT
AGREEMENT A2"*** — and by §4's own test, that qualifier is **not decoration, because it EXCLUDES a
real reading**: under exact-class agreement `coval_core` sits **below** its floor and **fails clause ②
itself**. The definition's one instance is admissible only on the metric the definition failed to
name.

⚠ **And that is the uncomfortable half, stated rather than buried.** The metric was never named
because **there has only ever been one**, which is precisely the *"definition describes the instance"*
failure this file's own register warns about. Naming it does not make the choice more justified — it
makes the choice **visible**, and it moves the burden onto why a graded agreement is the right target
rather than leaving it as an unstated default.

⚠ **Not rewritten into the clause text (L81)** — the clause lines above are anchored by
`assurance/definition_matches_the_record.py`, and a silent edit to a statement its gate keys on is the
one change that should never be made quietly.

⛔⛔ **AND THE BURDEN IS NOT MERELY UNPAID — THE CARD ANSWERS BOTH DEFENCES, AND ONE POINTS THE OTHER
WAY (entry 1350).** Two arguments could license the graded metric. Both were checked against
`data/DATASET_CARD.md`, the object itself.

**① "Graded matches how the humans were asked" — REFUTED.** The card: annotators *"ranked the four
responses from most preferred to least preferred"*, twice (personal and world-view), each with a
written rationale, and the release stores **`"ranking": "A>B>C=D"`** — a **complete weak ordering with
ties**. **The elicited unit is the WHOLE ORDERING.** The reading faithful to the elicitation is the
**exact-class** one — R231's — which is the reading on which `coval_core` sits **below** its floor.

**② "Graded is what the release itself scores" — VOID.** The card publishes **no ranking aggregation**.
Its only construction paragraph is about distilling *rubric items* — *"rewrites all rubric items to
have positive weight and then merges semantically redundant rubric items"* — and it closes: *"Core is
a proof of concept that surfaces difficult design choices in distilling the full rubrics and **an
invitation for others to develop and validate better synthesis and aggregation methods for this
format**."* **There is no published target for "scores better" to be right about.**

⭐ **So the metric this statement omits has no support from the object, and its stronger available
defence is contradicted by the elicitation format.**

> ⛔⛔ **AND THE ALARM THAT SENTENCE RAISED IS REFUTED BY MEASUREMENT (entry 1351).** Entry 1350 went
> on to imply that the elicitation-faithful reading is the one on which the core FAILS. **That joined
> two different targets.** R243's exact-class number — core `0.3864` against floor `0.3891` — is
> *"reproduce **Full's** exact weak ordering"*, the **rubric's** ordering. The card's `A>B>C=D` is the
> **human's**. Different targets, and the definition's own metric is human-targeted:
> `corebench/rule_sweep.py` defines `a2(c,h) = mean(c[q]==h[q] for q in range(6))` with `h` the
> held-out **human** ranking. **So the exact-class reading of the definition's own target is one word
> away — `all(...)` instead of `mean(...)` — and it had never been run.**
>
> **Run, on the same 968 prompts, the same three draws, the same arms:**
>
> | arm | GRADED A2 | EXACT (all 6 pairs) |
> |---|---:|---:|
> | **`coval_core`** | **0.5680** | **0.0730** |
> | `generic` — clause ②'s prompt-blind comparator | 0.5548 | 0.0644 |
> | `full` | 0.5110 | 0.0458 |
> | `random_k4` ×3 | 0.4939 / 0.4999 / 0.4900 | 0.0475 / 0.0551 / 0.0437 |
> | `coval_core_sham` | 0.4998 | 0.0444 |
>
> **`coval_core` − random floor: GRADED +0.0733 · EXACT +0.0242.**
> **`coval_core` − `generic`: GRADED +0.0132 · EXACT +0.0086.**
> ⭐ **Both positive under both readings — on the HUMAN target the sign does NOT flip.** The flip R243
> found is a fact about reproducing the **rubric**, not the people.
>
> ⚠ **Magnitude is UNRESOLVED and no significance is claimed.** These are point comparisons over three
> draws with **no MDE and no interval**; the exact-class rates are small (**7.3%** of prompts get all
> six pairs right) and the gaps are correspondingly small. **Sign preserved, size unmeasured.**
> ⚠ **What still stands from entry 1350:** the metric is unnamed, and *"graded is how the humans were
> asked"* remains **refuted as a justification** — the humans gave orderings. What is withdrawn is the
> stronger implication that the faithful reading kills the core.
>
> ⛔⛔ **AND ENTRY 1351's OWN SENTENCE IS NOW TOO STRONG (entry 1352, measured the same hour).** It
> read *"the sign does NOT flip."* **Priced against the design's own resolution — paired per-prompt
> differences over the same 968 prompts, cluster bootstrap over prompts, 4,000 resamples:**
>
> | reading | `coval_core` − `generic` | 95% CI | MDE | verdict |
> |---|---:|---|---:|---|
> | **GRADED** | **+0.0151** | **[+0.0060, +0.0243]** | 0.0134 | **RESOLVED** — CI excludes 0 |
> | **EXACT** | +0.0083 | **[−0.0024, +0.0196]** | 0.0159 | **BELOW its own MDE — CI includes 0** |
>
> ⭐ **So under exact-class the design CANNOT TELL.** That is **UNVERIFIED** — not a confirmation, and
> not the overturn entry 1350 claimed. Reading the positive point estimate as "the sign holds" is the
> same overshoot as reading R243's negative one as "the core fails"; **both were a point estimate
> inside an interval that contains zero.** I made the weaker version of the error I had just withdrawn.
>
> ⭐⭐ **AND THE ONTOLOGY SHIFT, which is the part worth keeping.** Entry 1350 framed graded-vs-exact
> as a pure **construct** question that *"the card explicitly declines to settle."* **It is not purely
> a construct question — it is partly a POWER question.** Exact-class is a ~7% binary hit, so its
> per-prompt variance against the effect is large and its MDE (**0.0159**) is *worse* than graded's
> (**0.0134**) despite testing the same arms on the same prompts. **The stricter reading is also the
> lower-resolution one.** ⭐ **Consequence for the definition: even a reader who prefers exact-class on
> construct grounds cannot adjudicate clause ② under it on this release at n = 968.** The clause is
> not merely unqualified — under one of its two admissible readings it is **undecidable here**, and
> that is a property of the data, not of the wording.
>
> ⛔⛔⛔ **BOTH OF THOSE SENTENCES ARE OVERTURNED BY R841, AND THE NUMBER THEY REST ON IS
> UNVERIFIED.** Entry 1352 drew **3 annotators per prompt**. The release ships **18,384 annotator
> rankings over 1,078 prompts, median 16** — 1352 consumed **17.6%** of what was on disk. Worse, it
> seeded that draw with `hash(p)`, and **Python randomises `hash()` of a str per process**: measured
> against a `crc32` control, `hash('prompt_42')%1000` returns **924 / 294 / 947** across three fresh
> processes while `crc32` returns **632 / 632 / 632**. **So 1352's draw was unseeded and its numbers
> are one unlabelled sample — UNVERIFIED, and not to be quoted.** Its seed spread alone is **0.0041
> on an effect of ~0.007, 59% of the effect.**
>
> **R841, stable seed, every annotator, 8 cells reported whole** (placebo exactly 0; reproducible
> byte-identically; a different seed does move the draw):
>
> | annotators used | GRADED | EXACT |
> |---|---|---|
> | 3 draws | +0.0191 [+0.0099, +0.0285] | **+0.0010 [−0.0103, +0.0127]** — contains 0 |
> | ≤16 | +0.0159 [+0.0084, +0.0235] | **+0.0085 [+0.0016, +0.0155]** — RESOLVED |
> | **ALL** | +0.0151 [+0.0076, +0.0226] | **+0.0073 [+0.0005, +0.0141]** — **RESOLVED** |
>
> ⭐ **Clause ② is NOT undecidable under exact-class. It resolves** — the CI narrows 42% and excludes
> zero. **The undecidability was an artifact of consuming a sixth of the data.**
>
> ⭐⭐ **And the ontology shift is overturned too, in the opposite direction.** 1352 said *"the
> stricter reading is also the lower-resolution one"* from `MDE_exact 0.0159 > MDE_graded 0.0134`. On
> all annotators **the ordering REVERSES: `MDE_exact 0.0096 < MDE_graded 0.0106`.** Exact-class is
> **not** intrinsically lower-resolution; a binary hit simply needs more annotators to stabilise than
> a 6-pair mean. **The property 1352 attributed to the METRIC belonged to the SAMPLE SIZE.**
>
> ⭐ **What this settles for the definition, and it is the first thing this thread has settled rather
> than withdrawn:** clause ② holds **under both admissible readings of its own metric**, on the human
> target, at n≈968 paired prompts, with every annotator the release ships.
>
> ⭐⭐⭐ **AND R845 LOCATES WHAT IS ACTUALLY WEAK IN CLAUSE ② — the BINARISATION, not the property.**
> R711 measured clause ②'s sham separation as **2 of 5 pairs**, against an exactly enumerated null
> (445,891,810 admissions) giving **p = 0.5727** — at chance. **That verdict is correct and stands.**
> But R711 wrote its own ceiling and never followed it: *"separation is only POSSIBLE where the base
> is admitted — 2 of 5 pairs, so the residual is 2 of 2 possible."* **A statistic capped at 2, scoring
> 2, is saturated.**
>
> **Un-binarised — the paired margin `base − its OWN wrong-prompt sham`, every annotator, 10 cells,
> BH at q=0.05, 9 surviving, the one non-survivor printed:**
>
> | pair | graded margin | exact | R711 binary |
> |---|---|---|---|
> | `coval_core` | **+0.0709** [+0.0615, +0.0806] | +0.0265 | SEPARATED |
> | **`full`** | **+0.0483** [+0.0385, +0.0583] | +0.0167 | **not separated** |
> | **`gen`** | **+0.0524** [+0.0416, +0.0637] | +0.0228 | **not separated** |
> | `promptecho` | +0.0122 [−0.0067, +0.0302] *(ns)* | +0.0130 | not separated |
> | `topw_k4` | **+0.0733** [+0.0631, +0.0835] | +0.0286 | SEPARATED |
>
> ⭐ **`full` and `gen` carry resolved margins the binary test scored as nothing**, because for those
> pairs *both* arms were rejected, so separation was structurally impossible. **Reference scale: three
> same-family NON-sham pairs give |margin| ≤ ~0.014**, so these are 3.4–5.2× mere arm-difference.
>
> ⛔ **And the poison check is UNIFORM: all five shams sit BELOW the arm that reads no prompt at all**
> (−0.0466, −0.0818, −0.0594, −0.0954, −0.0513). **Reading the WRONG conversation is worse than
> reading none, for every arm measured.** ⚠ This **downgrades R844's "the deflation is arm-specific"**
> — that was n=1 against n=1; across five pairs the property is uniform and `coval_core` is not
> special. ⚠ It does **not** license calling the other writer's A1 an outlier: A1 was not measured here.
>
> ⭐⭐ **THE FORMULATION CONSEQUENCE, which is what this whole quest is for:** *a clause that asks
> "is it admitted?" throws the margin away, and the margin is where the content is.* **Clause ② should
> state a margin against the arm's own wrong-prompt twin, with its interval — not an admission
> verdict.** That is the first change to the definition's SHAPE, rather than to its numbers, that this
> arc has earned.
>
> ⛔⛔ **AND ENTRY 1363's ALARM NAMED THE WRONG POPULATION — corrected by measurement (entry 1364).**
> 1363 wrote: *"a clause quantified over 'every arm' where the arm set is a directory listing is not a
> definition — it is a query against mutable state."* **The arm set is indeed mutable and did move:
> R436 saw 93 arms when committed and 99 on a fresh run, with 107 `sat_*.npz` on disk today.**
>
> **But clause ④ does not quantify over the arm set.** Its own words are *"every rule computable from
> responses alone"* — and R436 realises that as a **response-only FAMILY of 30**. Re-run against the
> grown arm set:
>
> | | committed | fresh re-run |
> |---|---|---|
> | **bar** | **0.4511956297670583** | **0.4511956297670583** — identical to 16 dp |
> | **best_rule** | `min_ttr` | `min_ttr` |
> | **excluded** | 22 | 22 |
> | **response-only family** | **30** | **30 — nothing added, nothing removed** |
> | n_arms | 93 | 99 |
> | n_arms_at_J | 56 | 62 |
>
> ⚠ **The stability of the bar is a DERIVATION, not evidence.** The bar is a `max` over the family;
> the family did not change; therefore the bar could not change. **Reporting it as robustness would be
> the arithmetic trap.**
>
> ⭐ **What IS measured, and it is the useful part: the family did not grow even though the arm set
> grew by six.** All six new arms fall outside *"computable from responses alone"*. **So clause ④'s
> exposure is to FAMILY growth, and that exposure has never been exercised** — no response-only rule
> has been added since R436. The clause's wording was right; entry 1363 attached its alarm to the
> wrong set.
>
> ⛔⛔ **STALE WITHIN ONE ROUND, BY MY OWN HAND (entry 1380).** **R847 — the very next round —
> exercised exactly this exposure**, enlarging the family **30 → 394** with two-feature combinations
> and measuring the bar rise **+0.0241** against a noise arm that moved **+0.0039**. **I wrote this
> claim, answered it one round later, annotated R847 into THIS FILE, and never corrected the sentence
> it answered.** *A correction must reach the artifact that provoked it* — and here the correction and
> the stale claim are in the same document, forty lines apart.
>
> ⭐⭐ **The general lesson this earns for the FORMULATION: a universal clause must name the population
> it quantifies over, and that population must be checkable.** *"Every rule computable from responses
> alone"* is a **specification** (30 rules realise it); *"every arm"* would have been a **directory
> listing**. The difference is invisible in prose and decides whether the clause has a fixed meaning.
>
> ⛔⛔⛔ **AND R847 SHOWS THE SPECIFICATION IS NOT THE SUPREMUM — clause ④ has R406's defect too.**
> R406 already measured this for clause ②: *"better than EVERY prompt-blind set"* had been tested
> against a **p99** bar while the max over 1,820 subsets is **0.5574753088** vs a reference of
> **0.5546019830**. **Clause ④ is the same shape**, and its 30 rules are a *convenience family*, not
> a universal.
>
> **Enlarged mechanically — every normalised TWO-FEATURE combination, no fitting on labels, so
> "computable from responses alone" on any reading — 1,078 prompts, every annotator:**
>
> | family | rules | best | A2 | noise max | excess over noise |
> |---|---:|---|---:|---:|---:|
> | R436's committed | 30 | `min_ttr` | 0.4560 | 0.4412 | **+0.0148** |
> | enlarged | **394** | `+mean_word_len+uppercase` | **0.4801** | 0.4451 | **+0.0351** |
>
> ⚠ **The noise arm is the other writer's R843 control and it is what makes this readable**: the raw
> max moved **+0.0241** while the noise max moved only **+0.0039**, so the excess over what family
> size buys **more than doubled**. Controls: human-vs-itself **1.0000**, reversed **0.2523**.
>
> ⭐ **Clause ④ is NOT flipped** — `coval_core` at 0.5664774812 clears the enlarged bar by **0.0864**.
> ⚠ **But the gap is not shown safe: the first honest push closed 21% of it**, triples and ratios are
> untested, and the supremum is unknown and **≥ 0.4801**.
> ⚠ **And the committed bar was understated TWICE**: **+0.0048** from using 3 annotator draws instead
> of all (R841's lesson, applied to R436 itself) and **+0.0241** from family size.
>
> ⭐⭐⭐ **THE FORMULATION CONSEQUENCE, and it is the same one in both universal clauses:** *"better
> than every X"* reads as a **supremum** and is implemented as a **max over an enumerated family**.
> **The definition's "every"s are searches, and a search reports what it searched.** So each such
> clause must (a) name its family, and (b) report its bar as a **LOWER BOUND**, never as the
> supremum — because "computable from responses alone" is not a finite set and no round can enumerate
> it. **That is a permanent property of the clause, not a gap to be closed later.**
>
> ⭐⭐⭐ **AND R848 GIVES THAT LOWER BOUND A RATE — the first POSITIVE result about clause ④ in this
> arc.** Every prior finding here was a caveat; this one is a margin with a growth law.
>
> ⚠ **First, the trap:** *"is membership monotone in search effort?"* is **forced** — `core > max(F)`
> and a max is non-decreasing, so membership is non-increasing **by construction**. Not asked.
>
> **The dose-response, 1,078 prompts, every annotator, 24 subfamily draws per size:**
>
> | n | real max | noise max | excess |
> |---:|---:|---:|---:|
> | 5 | 0.4461 | 0.4326 | +0.0135 |
> | **30** *(R436's family)* | 0.4636 | 0.4397 | +0.0240 |
> | 100 | 0.4716 | 0.4423 | +0.0293 |
> | **394** | **0.4801** | 0.4451 | **+0.0351** |
>
> **Slope per `ln(n)`: real +0.00741 · noise +0.00278 — the real curve grows 2.7× faster**, so
> enlarging buys **content**, not search. Controls: human-vs-itself 1.0000, reversed 0.2523, and a
> **seed check** confirming the draw seed changes the subfamily (entry 1358 found 29 files where it
> did not). ⚠ The **noise slope is positive**, which quantifies the other writer's R843 mechanism.
>
> ⭐ **So "every" has a price: the bar rises +0.0074 per e-fold of family size, and `coval_core`
> leads the 394-rule bar by 0.0864 — about 11.7 e-folds of headroom.**
>
> > ⚠ **D4, NOT A MEASUREMENT.** `max ≈ 0.4377 + 0.00741·ln(n)` puts the crossing at **n ≈ 3.5×10⁷
> > rules**. A2 is **bounded above**, so a log fit must eventually break; this is what a 9-point
> > model says, not what the world says.
>
> ⚠ **And the scope that matters most: the rate belongs to a family CLASS** — single- and two-feature
> rules over 14 response features. **A class with learned features or fitted combiners is a different
> curve, and this says nothing about it.** Clause ④ is not *safe*; its exposure is **quantified within
> one class**, which is the first time any clause in this definition has had that.
>
> ⛔⛔⛔ **AND R847/R848 REPORTED ONE READING OF ④ WHILE A COMMITTED ROUND ALREADY SETTLED THE OTHER
> AGAINST IT (entry 1367). `11.7 e-folds of headroom` is a correct number without its scope — the
> register's dominant retraction mode, committed twice today by me.**
>
> **R824** established the clause's text is **silent** about whether *"computable from the response
> set alone"* constrains **inference** or also **construction**. **R825** then measured the
> permissive reading, and its committed artifact says:
>
> | | |
> |---|---:|
> | leak-free **char-n-gram** response-only bar | **0.572335** |
> | `coval_core` | **0.566477** |
> | paired difference, 12 splits | **+0.006197072 [+0.004172, +0.008222]**, SE 0.001033 |
> | splits where the bar BEATS the core | **12 of 12** |
>
> ⛔ **Under the permissive reading, clause ④ EXCLUDES the released core.** ⚠ *(The R825 README quotes
> [+0.003923, +0.008471]; the artifact recomputes and prose does not, so the artifact's interval is
> the one used here.)*
>
> ⭐⭐⭐ **So the two readings give OPPOSITE verdicts on the definition's own instance:**
>
> | reading | bar | `coval_core` | verdict |
> |---|---:|---:|---|
> | **strict** — no fitting, hand-built lexical rules (R847) | 0.4801 | 0.5665 | core clears by **+0.0864** |
> | **permissive** — fitted, char n-grams (R825) | **0.5723** | 0.5665 | **core FAILS by −0.0058** |
>
> ⭐⭐ **AND THE TECHNICAL POINT THAT CORRECTS R848's AXIS.** R848 measured the dose-response along
> **family SIZE**: +0.00741 per e-fold. R825 reports that **char n-grams buy +0.0487 over lexical
> features** — *(arithmetic, labelled: 0.0487 / 0.00741 ≈ **6.6 e-folds** of my rate)* — **from a
> change of REPRESENTATION, not a bigger family.**
>
> ⭐ **The axis that threatens clause ④ is representational richness, not enumeration.** R848's curve
> is real and its controls hold, but **it is the shallow axis**, and reporting `11.7 e-folds` beside a
> committed result where one change of view already crosses the bar was scope-blind. **The honest
> statement of clause ④'s status is that it is READING-DEPENDENT and unresolved as a definition until
> the reading is fixed in the text.**
>
> ## ⛔⛔⛔ AND FIXING THE READING DOES NOT SAVE IT — BOTH READINGS FAIL, FOR OPPOSITE REASONS
>
> *(entry 1368; both numbers read from committed artifacts, not from prose.)*
>
> | reading | clause ④ excludes | consequence |
> |---|---:|---|
> | **strict** — no fitting | **0 of 42** (`R440.excluded_by_4 == []`), and **0 of 56** at the judge the definition names | **untested decoration** |
> | **permissive** — fitting allowed | **25 of 58** (`R824.e1.excluded_permissive`), and the bar beats `coval_core` **12 of 12 splits** (R825) | **the extension is EMPTY** |
>
> ⭐ **The register's own rule decides the first row:** *"name an admissible object this clause
> EXCLUDES. If nothing you have built is excluded, the clause is untested decoration."* **Under the
> strict reading nothing is excluded — so clause ④ does no definitional work at all.** Under the
> permissive reading it excludes 25 arms **including the object the definition was written from.**
>
> ⭐⭐ **There is no third reading.** The clause constrains what a rule consumes; it either counts
> construction or it does not. **So clause ④ as written cannot both do work and admit its own
> instance — and that is a property of the WORDING, not of the object.**
>
> ## ⭐⭐⭐ THE REPAIR THIS ARC HAS EARNED — the first constructive proposal, not another defect
>
> Three findings compose into one wording:
>
> | from | finding | what it forces |
> |---|---|---|
> | **R845** | the binary admission test is at chance; the **margin** resolves in 9 of 10 cells | state a **margin**, not an admission |
> | **R847** | *"every"* is a max over a convenience family, and the bar rose **+0.0241** on the first honest enlargement | **name the family**; report a **LOWER BOUND** |
> | **1368** | strict excludes 0 (vacuous), permissive excludes the core (empty) | **do not use a universal quantifier at all** |
>
> ⭐ **Proposed form of ④:** *"…exceeds, by a margin reported with its interval, the best rule in a
> NAMED reference class R, where R is stated in full and the margin is a lower bound on the margin
> against any superset of R."*
>
> ⚠ **What this buys and what it costs.** It buys a clause that is **checkable, falsifiable and
> honest about its own search** — R845 showed the margin is measurable and resolvable, R848 showed the
> bound moves at a measurable rate. **It costs the word "every"**, and with it the appearance that the
> clause states a universal property. **That appearance was never true**: every "every" in this
> definition has always been a max over something someone enumerated.
>
> ## ⭐⭐⭐ AND R849 INSTANTIATED IT AND COUNTED ITS EXTENSION — the proposal survives its own test
>
> *(entry 1369. It could have failed; the same question killed four earlier clauses.)*
>
> **Reference class R = 394 response-only rules, named in full. Bar selected on the ODD annotators
> (`+mean_word_len+uppercase`, 0.4785) and every margin evaluated on the EVEN half (bar 0.4820) —
> the other writer's R843 remedy, because selecting on the scoring set would FLATTER the clause.**
>
> | control | result |
> |---|---|
> | PLACEBO bar vs itself | **+0.00e+00 · PASS** |
> | POSITIVE `oracle_k4` | satisfies, **+0.1390 · PASS** |
> | NEGATIVE `random_k4_s0` | does **not** satisfy · **PASS** |
>
> | | |
> |---|---:|
> | arms tested | **99** (77 survive BH q=0.05; 22 non-survivors) |
> | **EXTENSION of ④′** | **41** |
> | **arms EXCLUDED** | **58** |
> | `coval_core` | **+0.0794 [+0.0667, +0.0915] — SATISFIES** |
>
> ⭐ **Strictly between 1 and 99** — neither the *describes-the-instance* failure nor decoration.
> **It excludes 58 admissible objects, which neither reading of the original ④ could do** (strict
> excluded 0; permissive excluded the core).
>
> ⭐⭐⭐ **And the negative control is the whole argument for the margin form:** `random_k4_s0` has a
> **positive point estimate, +0.0057.** The original wording *"scores better than"* is a point
> comparison and **admits it**. ④′'s interval **rejects it**. **The original clause would have called
> a random baseline better than every rule computable from responses alone.**
>
> ⚠ **Not claimed:** that 41 of 99 is selective enough to *define* a core — it is one clause of four,
> and ①②③ do the rest. The extension is **scoped to this R**; a richer R (char n-grams, R825) raises
> the bar and shrinks it, which is precisely why the clause **requires R to be stated**. **Construct
> validity is untouched** — no external gold standard for corehood exists.
>
> ⛔⛔⛔ **AND R850 DOWNGRADES THE ROUND ABOVE — mine, one round old (entry 1370).** R849's cell
> reproduces exactly through different code (**|R| = 394 → 41.0**), and then two things it never
> measured cut against it:
>
> | \|R\| | extension | **noise** | excess | controls |
> |---:|---:|---:|---:|---|
> | 5 | 63.8 | 55.2 | 8.5 | **neg FAIL** |
> | **30** *(R436's committed family)* | 57.1 | 38.2 | 18.9 | **neg FAIL** |
> | 200 | 43.8 | 30.8 | 13.0 | **neg FAIL** |
> | **394** | **41.0** | **30.0** | **11.0** | **neg PASS** |
>
> **① The negative control passes at ONE size only.** `random_k4_s0` **satisfies ④′ at every
> |R| ≤ 200 — including 30, the original ④'s own family size.** ④′ rejects a random baseline only
> when R is essentially the whole family, so **its selectivity is contingent on R being large, and
> the original clause's family is far too small to have it.**
>
> **② The noise arm says most of the extension is free.** **30 of 99 arms satisfy ④′ against a
> SHUFFLED target.** The excess is **11, not 41.** R849 ran **no noise arm**; its *"excludes 58"*
> stands as arithmetic, but *"does definitional work"* is now **quantified at 11 arms of excess.**
>
> ⭐ **What survives:** the extension **stabilises well above 1**, so ④′ is not the
> *describes-the-instance* failure arriving inside my own repair. ⚠ **But the honest headline is
> `excess 11 at |R| = 394`, not `41`** — and the clause must state **both** its class **and** the
> noise level of its own selection procedure, which is a third requirement neither the original ④
> nor my first draft of ④′ carried.
>
> ⭐⭐⭐ **AND R851 APPLIED THAT SAME NULL TO THE PUBLISHED CLAUSES — the two MEASURED ones agree
> (entry 1371).** ⚠ First, entry 1370's *"every extension may carry a free component"* was **too
> broad, and the table at lines 582–586 of this file already refuted it**: ① and ③ are **DERIVED**
> (0 of 41 by arithmetic; 14 of 42 read from the source), so they have **no noise floor of this
> kind** — no selection, no interval, no BH — and ④ strict excludes 0, so it has nothing to inflate.
> **Exactly one published extension was exposed: ②'s.**
>
> | clause | real | **noise** | **excess** |
> |---|---:|---:|---:|
> | **② — published** | **29** of 99 | **16** | **13** |
> | **④′ — proposed (R850)** | 41 of 99 | 30 | **11** |
>
> Controls on ②: placebo **+0.00e+00**, positive `oracle_k4` **PASS**, negative `random_k4_s0`
> **PASS** *(not a formality — the same control failed for ④′ at 7 of 8 class sizes)*.
> `coval_core` satisfies ② at **+0.0250**.
>
> ⭐⭐ **Both measured clauses land in the low teens.** The definition's **measured** selectivity is
> on the order of **11–13 arms per clause**, not the 29–41 the raw counts suggest — and **the
> proposed ④′ is neither better nor worse than the clause it replaces on this axis.** That comparison
> is worth more than either number alone, and it is the closing state of this arc: **the definition's
> clauses do real work, and roughly half of what each appears to do is what the procedure would do to
> a shuffled target.**
>
> ⚠ **Not a retraction of ②'s published 33 of 42** — that is R360's 42-arm space with a different
> comparator; this is 99 arms against `genericpool16`. **Different populations.** What transfers is
> the **shape**, not the number.
>
> ## ⛔⛔⛔ AND R852 RETRACTS BOTH BLOCKS ABOVE — THE NULL WAS WRONG (entry 1372)
>
> **The arithmetic that should have been run first:** under BH at q=0.05 over 99 arms, a **pure**
> null yields on the order of `q·N ≈ 5` rejections. R850 reported **30** and R851 **16** as "noise".
> **3–6× the pure-null scale — and I called it noise twice without checking what my shuffle
> preserved.** §1's own row says: *"a permutation null answers `did the pairing matter`, never `why`
> — before calling one load-bearing, NAME THE WORLD IT EXCLUDES and build that world."*
>
> | null | extension | seeds |
> |---|---:|---|
> | **REAL** | **29** of 99 | — |
> | **N1 pair-shuffle** *(what R850/R851 used)* | **14.3** | `[16, 12, 15]` |
> | **N2 cross-prompt swap** | **0.0** | `[0, 0, 0]` |
> | **N3 uniform — the pure null** | **0.0** | `[0, 0, 0]` |
>
> ⭐⭐⭐ **Two independent proper nulls return EXACTLY ZERO.** The pair-shuffle permutes *which pair
> is which* but **preserves each prompt's marginal verdict mix**, so an arm whose output has a
> human-like mix of ties and strict orderings scores above chance **whatever the pairing is**. **That
> is FORMAT agreement — real, measurable, and not a null.**
>
> | claim | status |
> |---|---|
> | *"④′'s excess is 11, not 41"* (R850) | ⛔ **RETRACTED** — against a proper null it is **41** |
> | *"②'s extension is ~55% free; excess 13"* (R851) | ⛔ **RETRACTED** — the excess is **29** |
> | *"both measured clauses agree in the low teens"* | ⛔ **RETRACTED** — an agreement between two artifacts of the same bad null |
> | *"extension 41 of 99, excludes 58"* (R849) | ⭐ **RESTORED as reported** |
>
> ⚠ **The direction matters and it is the rarer one.** The register records that of 7 mis-specified
> controls only **1** failed in the flattering direction. **This failed the other way: a bad null made
> me retract something true — §3's named most-expensive error — and I ran it twice and published
> both.**
>
> ⭐ **What N1 does measure, and it is worth keeping:** how much of an arm's A2 advantage is
> **marginal-format agreement** — for clause ②, **14.3 of 99 arms' worth.** A real quantity, wrongly
> used as a null.
>
> ⛔⛔ **THAT LAST SENTENCE IS REFUTED ONE ROUND LATER, BY A CONTROL BUILT TO CONFIRM IT (entry
> 1373).** Cohen's **κ** is *defined* to subtract marginal-expected agreement, so *"N1 survives on
> marginal format"* predicts **κ-extension under N1 ≈ 0**. Pre-registered as R853's key control.
> **It failed:**
>
> | | A2 | **κ** |
> |---|---:|---:|
> | REAL | 29 | **30** |
> | **N1 pair-shuffle** | **14.3** | **15.7** — *rises* |
> | N2 cross-prompt | 0.0 | **0.0** |
> | N3 uniform | 0.0 | **0.0** |
>
> ⭐ **κ removes the marginal component and the count does not move. So what survives N1 is NOT
> marginal-format agreement.** R853 exits **2** and reports **no** content-vs-format verdict.
>
> ⚠ **What still stands:** the two proper nulls return **0** under κ as well as A2, three seeds each
> — so **R852's retraction of R850/R851 is unaffected.** N1 remains the wrong null; **why** it is
> wrong has changed.
>
> ⭐⭐ `[HYPOTHESIS — untested]` **N1 is not a null at all but a comparison against a DIFFERENT BUT
> FIXED target**: permuting the six pairs yields a per-prompt target that no ranking realises, yet is
> the *same* target for every arm and is still **a function of this prompt**. N2 and N3 give 0
> because they sever the prompt-level coupling; N1 keeps it. **That is the separation the next round
> owes.**
>
> ## ⭐⭐⭐ R854 SETTLES IT — the survivors are ARM-INTRINSIC, and they are the LABEL-TOUCHING arms
>
> *(entry 1374. The hypothesis above is **refuted**: the target-per-seed story predicts chance
> overlap, and the overlap is 10.7× chance.)*
>
> | | |
> |---|---:|
> | pair-shuffle survivor sizes, 8 seeds | `[16, 12, 15, 13, 13, 15, 9, 17]` |
> | **observed mean Jaccard**, 28 pairs | **0.8047** [0.5294, 1.0000] |
> | chance at the same sizes | 0.0752 → **ratio 10.70×** |
> | arms surviving **all 8** seeds | **9** |
>
> **Controls:** the real survivor set is identical on a repeat call (29 arms); and — the load-bearing
> one, because a closed form I derived is a claim about my own algebra — the **closed-form chance
> overlap agrees with a simulated one to max\|Δ\| = 0.0086**.
>
> ⭐⭐⭐ **The nine that survive every permutation are `oracle_k4`, `oracle_k4_fit1`,
> `oracle_k4_oracle_kA`, `greedy_k2_fit1`, `greedy_k4_fit1`, `greedy_k4_greedy_kA`,
> `greedy_k4_greedy_kB`, `indep_k2_fit1` (+1) — every one an ORACLE or FITTED arm, an arm that
> touched the human labels.**
>
> ⭐ **So an arm fitted to the labels acquires a property that beats a prompt-blind comparator even
> when which-pair-is-which is scrambled, and CLAUSE ② ALONE CANNOT TELL THAT APART FROM TRACKING THE
> HUMANS.** That is a concrete, measured limitation of ② — the first one this thread has established
> about what the clause *confuses*, rather than about how big its extension is.
>
> ⚠ **The mechanism is NOT claimed** (R853 refuted the last one a round after publication).
> `[HYPOTHESIS — untested]`: shape properties of a fitted verdict vector — transitivity, tie rate,
> the strict/tie mix — none of which κ's marginal correction removes.
>
> ⚠ **And one thing owed rather than asserted:** these nine look like arms **clause ③ (*no prompt
> labels*) already excludes**. **If so, ③ removes exactly the arms ② is most fooled by — an interlock
> the definition has never claimed and this round did not check.**
>
> ## ⭐⭐⭐ R855 CHECKED IT — the interlock HOLDS, on the third of the set that is checkable
>
> *(entry 1375. The first result is that the check could not be run as I stated it.)*
>
> **R854's nine live in a 99-arm space; ③ was measured by R360/R444 on 42.** ⚠ **Only 3 of the 9 are
> in that population at all** — the population trap this file recorded earlier today (*"29 of 99 is
> not 33 of 42"*), and **my own NEXT walked into it.**
>
> | | |
> |---|---:|
> | checkable survivors | **3** — `greedy_k4_fit1`, `oracle_k4`, `oracle_k4_fit1` |
> | **admitted by ②** | **3 of 3** |
> | **admitted by ②∧③** | **0 of 3** |
> | uncheckable | **6** — never in the space where ③ was measured |
>
> ⭐⭐⭐ **Every checkable survivor passes ② and is removed by ③.** The arms that fool ② under a pair
> shuffle are exactly the arms ③ takes out.
>
> ⭐ **So the clauses are NOT independent filters — they form a CHAIN, and ③ covers ②'s permutation
> blind spot.** That changes what the definition **is**: a conjunction whose parts each stand alone is
> a different object from one whose parts repair each other, **and every report of "② excludes N, ③
> excludes M" in this file has been written as if the parts were independent.**
>
> ⚠ **Established on 3 of 9**; the other six need ③ re-measured on the 99-arm space — a different
> experiment, named rather than approximated.
>
> ⚠⚠ **And the structural point that outlives the round: ② and ③ were measured on 42 arms while this
> session's ②-work used 99. "② admits X" and "③ excludes Y" cannot be composed into a statement about
> the conjunction unless the populations match.** Extensions reported on different spaces are **not
> intersectable**, and this file has laid them side by side. The metric is still
> **unnamed in the statement** — that gap from entry 1349 is untouched — but it is no longer true
> that naming it the strict way costs the clause its verdict. ⚠ **What this does NOT establish:** that
exact-class is *correct*. Whether a core should reproduce an ordering or track it gradedly is a
CONSTRUCT question, and the card explicitly declines to settle it. **What is settled is that the
graded choice cannot be defended as "what the data is" — it is a choice this campaign made, on which
its one instance passes and the alternative fails.**

⚠ **The size line was two different things and is now written as two (R441).** *"3 to 8 are not
distinguishable"* is a statement about **resolution**, and a non-result cannot remove a member — it
excludes nothing **by construction**, so it is a **caveat, not a clause**. That is a derivation and
no measurement changes it. **"Greater than one" is left in the conjunction**, and here is its
evidence: of **52** arms with a k readable from their committed core file, exactly **1** has k=1
(`topw_k1`), and clause ② already excludes it — so on this evidence half A removes **0 of 1** arms
the other clauses admit. ⛔ **It is NOT demoted on n=1.** Retracting a clause on a single arm is the
cheap-attack failure this campaign's standard names explicitly: the most expensive error is the one
that retracts something true. **What would settle it** is constructing a k=1 core that ②∧③∧④ admits.
→ [`R441`](A24_what_the_definition_costs/R441_is_the_size_clause_a_clause)

**Clause ① is not a clause.** It is a consequence — see below.

## ⛔ THE EXTENSION — and this document states two incompatible answers (R442, 2026-08-04)

**What the conjunction actually admits on the home release, at judge J, over R360's 42-arm space:**

| | admits |
|---|---|
| ~~as IMPLEMENTED — hand-written 4-arm set~~ | ~~5~~ — **superseded, R444** |
| **as WRITTEN, now also as implemented** | **1**: `coval_core` |

⭐ **CLOSED 2026-08-04 (R444), by a DECISION rather than an experiment.** The set was corrected to
match the text, and the choice was **forced**: weakening the text was preferable only while ③-as-
written looked unenforceable, and R443 showed `select_core.py` names every selector consuming
annotator importance. `assurance/clause3_as_written.py` now derives ③ from the source —
**target-readers** (`oracle_k`, `indep_k`, `greedy_k`) **and w-readers** (`topw_k`, `topabs_k`,
`topwvar_k`), but **not** `topvar_k`, whose own comment calls the spread *"a property of the
responses, never of the human target"*. ③ goes from excluding **4** to **14** of 42; the extension
goes from **5** to **1**. ⚠ **7** arms have provenance the source cannot classify (`coval_core`,
`gen`, `generic`, `promptecho`, shams) and are returned **UNKNOWN, never silently admitted** —
`coval_core` survives on R443's separate containment measurement, not on anything ③ can decide.
⚠ **`[unchallenged]`** — this standard prescribes an adversary for a judgement call; agent dispatch
was unavailable, so the decision is recorded as unchallenged, not as clean.

⭐ **Neither is the published five** (`coval_core, topabs_k4, topvar_k4, topw_k4, topwvar_k4`) —
only **2 of 5** overlap. The definition's boundary runs along the **selector** axis, not the k axis:
it admits `topw` at four sizes and rejects three sibling selectors at k=4. ④ and the size clause add
nothing to this (R440, R441).

⛔ **And under its own written clause ③ the extension is ONE ARM — the object the definition was
written from.** The ③ section below states that `topw_k` is *"not producible from the conversation
alone"* — which is this definition's **own opening phrase** — while the implemented set admits four
`topw_k` arms. **The document asserts both and reconciles neither.** ⚠ This is *not* a claim that
③'s derivation is wrong: if it stands the extension is one arm, if it falls the extension is five.
**What is certain is that the two cannot both be published as they are**, and until that is
resolved the extension must be quoted with which reading produced it.
✅ **And the extension under the written reading is 1, not 0 (R443).** ③ as written excludes
**three** selectors, not one — `select_core.py:131` computes `w = mean annotator score` and
`topw_k`, `topabs_k` and `topwvar_k` all consume it, while `topvar_k` does not. But `coval_core`
survives: only **0.0779** of its criteria appear verbatim in its own prompt's rubric, against a
cross-prompt sham of exactly **0.0000**, over **968** prompts. So its text is not drawn from the
rubric and the containment objection does not reach it. ⚠ **UNVERIFIED-leaning by construction:**
containment is *sufficient* for the provenance objection and *not necessary* — the same annotators
could have authored it in different words, and this instrument cannot see that. ⭐ The 7.8% that
*is* contained is real and strictly prompt-specific, since the sham is zero.
⭐ **AND THE ONE ARM IS A FINDING, NOT A THRESHOLD ARTIFACT (R445).** The extension is one arm
*not* because no third-source object exists: **`gen` — a home-release core generated from the
conversation alone — has been in the 42 the whole time**, ③-corrected does not exclude it, and **②
does**. Paired against ②'s own reference `POOL[0:4]` over **968** prompts, `gen` scores
**-0.0162 [-0.0270, -0.0051] against an MDE of 0.0151** — resolved, but at **1.07×** its floor —
while `coval_core` scores **+0.0178 [+0.0079, +0.0285]** vs 0.0146, at 1.22×. **The definition's
entire boundary at home separates the two by 0.0340 across a floor of ~0.015.** Resolved, and thin;
quoting only the first half would make a 1.07× margin sound like a verdict. Controls: an oracle
clears the reference by **+0.1702** (MDE 0.0184), the reference against itself is exactly 0, and the
wrong-prompt sham fails by **more** (**-0.0669**) as it must.
✅ **AND THAT VERDICT SURVIVES EVERY ADMISSIBLE REFERENCE (R446).** R331's standing defect is that
②'s reference `POOL[0:4]` was **chosen by file order**. Sweeping **all 1,820** size-4 subsets of the
pool, paired per prompt over 968 prompts: `gen` is **resolvedly** better than **0.4%** of them and
`coval_core` than **98.4%**, against an oracle admitted under **1820/1820**. **So the file-order
choice did not manufacture the verdict.** ⭐ And the point-vs-resolved gap is its own finding: `gen`
would be *"better"* than **26.2%** of references but is resolvedly better than 0.4% — a **25.8**-point
gap that is the resolution effect made visible, and the reason the naive quantile sweep would have
misled in the flattering direction. ⚠ This shows the ANSWER does not depend on the arbitrary choice;
it does not FIX the choice, which remains R331's open defect.
→ [`R446`](A24_what_the_definition_costs/R446_clause_two_over_every_admissible_reference) ·
[`R445`](A24_what_the_definition_costs/R445_is_the_extension_empty_on_a_resolved_difference) ·
[`R442`](A24_what_the_definition_costs/R442_the_extension_under_clause_three_as_written) ·
[`R443`](A24_what_the_definition_costs/R443_does_clause_three_as_written_exclude_the_core_itself)

⭐ **Clause ④ was ADOPTED 2026-08-04**, after every objection I could raise against it was measured
rather than argued: it is **statable** (its bar saturates at 6 of 30 rules, R435); it **excludes
nothing at home and everything on the second release** (R436/R434); the two bars **invert**, so it
binds exactly where ② goes slack (R437); the sign **does not flip** across strata of one release
(R438); and it is **not a reparameterisation of ②** — its bar sits at the **0.00th percentile** of
all 1,820 size-4 subsets of ②'s own reference pool, **0.0687 below the weakest of them** (R439) — where the published reference sits at 91.7.
⚠ **Its scope:** two releases, one judge, and a **30-rule hand-built family** standing in for "every
criterion-free rule". The family is published in R435's artifact so that extending it is how this
clause gets refuted.
⭐⭐ **AND THAT ROUTE WAS TAKEN (R823) — THE CLAUSE SURVIVED IT.** R803's judge-free floor, on which
R821 retained ④, was the max over **six** rules, and all six are members of this thirty. Recomputed
on R803's own 968-prompt population, **`max_len_chars` 0.455679 is the argmax over the whole family,
not merely over the subset — the 6→30 rise is exactly +0.000000**, and ④ still excludes **0 of 58**.
The zero is admissible only because the sham prices it: 30 **random** scorers reach 0.440503 against
0.437091 ± 0.002830 for a random six, so **pure selection buys +0.003412 on noise and the real rise
is below that** — the extra 24 rules add less than random scorers of the same count would. And
R803's choice of six was not luck: a **random** six of this thirty reaches only 0.439060 ± 0.018355,
so the choice bought **+0.0166**, while a random six contains the argmax **6/30 = 0.200** of the time
(measured 0.208 over 2,000 draws — the search's own positive control). ⚠ **The held-out bar moves the
other way**: fitting the max on half the prompts and scoring on the other half gives 0.456094 ±
0.004345 at m=6 and **0.454779 ± 0.004791 at m=30**, a rise of **−0.001315** — inside its own sd, so
a direction and not a value, but the opposite of what "a larger class is a stronger bar" predicts.

---

## What each clause is measured to do

> ⭐⭐⭐ **THE DEFINITION, RESTATED — R874, all four kills read committed artifacts, D8.**
> Thirteen rounds bound a comparator and a criterion to every clause below. **Two clauses survive.**
>
> > **A CORE is a criterion set of size > 1 that ③ consumes no prompt-specific labels and
> > ② beats a NAMED prompt-blind comparator by a RESOLVABLY POSITIVE margin — its bootstrap
> > CI lower bound above zero.**
> >
> > ⛔⛔ **CORRECTED R888 — `28` WAS CLAUSE ②'s EXTENSION, REPORTED AS THE DEFINITION'S.**
> > **The TWO-clause definition admits 12 arms.** Clause ② admits 29 (R856's committed `c2`);
> > **clause ③ then excludes 16 of them — 57.1%** *(⛔ R889: was `17 of 29 — 58.6%`;
> > R888 ran on a SUPERSEDED population, see below)* — because their generator opens
> >
> > ⭐ **WHAT CLAUSE ③ BUYS, MEASURED (R892–R895).** Its cheating-prevention half is now priced.
> > Over **8 cells matched on (rule, k, JUDGE)**, a leaky arm — fitted on all annotators, scored
> > against annotators it saw — beats its held-out twin by **+0.0097, bootstrap CI
> > [+0.0068, +0.0127], sign-flip p = 0.0073** (floor 0.0078). All 8 gaps positive, range
> > +0.0042…+0.0158 — **no k-dependence.**
> > ⚠ **Resolution, stated precisely:** +0.0097 is BELOW R860's *per-cell* MDE of 0.0103, so **no
> > single cell is individually resolvable.** What carries the result is CONSISTENCY across 8
> > cells, which is what the sign-flip test measures and all it claims. Comparing a pooled
> > estimate to a per-cell MDE would mix resolutions.
> > ⭐⭐ **CROSS-MODEL COMES OFF THE IMPOSSIBILITY REGISTER.** Every round in this arc listed it as
> > structurally impossible — *"more than one site"*. The release ships `oracle_k4_08b` and
> > `oracle_k4_fit1_08b`: **a complete leakage cell under the 0.8B judge.** It gives **+0.0042**,
> > **agreeing in sign**, and is reported apart — never pooled, because a 0.8B gap and a 2B gap
> > measure one construct with two instruments.
> > ⛔ **THREE NUMBERS WITHDRAWN ON THE WAY HERE.** `+0.0190` (k-confounded: leaky arms were all
> > k=4 while held-out spanned k=2,4,8,12) → `+0.0378` (judge-MIXED: a prefix regex swept the
> > 0.8B `_08b`/`_08bR` rebuilds into the held-out side of every k=4 cell) → **+0.0097**. Each was
> > overturned by a better instrument, never by a better argument.
> > ⚠ **AND ONLY HALF OF CLAUSE ③ IS PRICED.** `held-out − label-free` stays UNIDENTIFIED:
> > `oracle_k`/`indep_k`/`greedy_k` consume labels by construction and have no label-free twin,
> > so rule and label-access cannot be varied separately on this release.
> > `data/comparisons.jsonl` and parses human rankings. Read from the object, not the name:
> > `corebench/select_core.py:102` branches on `a.rule in ("oracle_k", "indep_k", "greedy_k")`,
> > and **those three rules, and only those three, consume the labels clause ③ forbids.**
> > The 17: 7 `greedy_*`, 5 `indep_*`, 5 `oracle_*`. The 12 that survive BOTH clauses:
> > `coval_core`, `coval_core_2bA/2bB`, `generic`, `generic_reprov`, `topw_k2/k3/k4/k6/k8`,
> > `topw_k4_detA/detB`.
> >
> > ⛔ **AND A WALL FELL.** R856 recorded `clause3_on_99_arms: "IMPOSSIBLE — provenance measured
> > only on 42"` — **while the same JSON printed a `c2` list containing five arms named
> > `oracle_*`.** The falsifying evidence was inside the artifact that declared the wall. *An
> > unchecked wall is UNVERIFIED, never SETTLED*, and this one cost 17 arms of a headline number.
> > ⚠ Why it was believable: the comment above that branch says *"human target, for the ORACLE
> > arm only"* — **one rule behind its own code** — so the name-level story and the code-level
> > story disagreed, and the name-level one was the one written down.
> >
> > ⛔ **RESOLVED R889 — THE 28-vs-29 GAP WAS THE WORD `RESOLVABLY`, AND R888 USED THE WRONG SET.**
> > The two committed lists differ by **exactly one arm**: `greedy_k4_fit1_08bR`, margin
> > **+0.003786**, CI lower bound **−0.006910** — *point positive, interval crosses zero*.
> > **R856's `c2` admitted on `margin > 0`; R881 admitted on `lo > 0`.** The headline names the
> > second, so **R881's 28 is current and R856's 29 is superseded** — and R888 measured against
> > the superseded one.
> > ⭐ **The correction is a SHARE, not a conclusion.** The disputed arm is `greedy_*`, i.e.
> > label-consuming, so clause ③ removes it under either criterion:
> > superseded 29 → 17 excluded, **12 survive**; current 28 → 16 excluded, **12 survive**.
> > **The surviving set is IDENTICAL, so `the definition admits 12` now holds under BOTH
> > populations — the finding got stronger, not weaker.**
> > ⚠ The process error is the reusable part: R888 printed *"Clause ② admits 29 here"* against
> > this file saying 28, and recorded it as an open question. **A discrepancy NAMED but not
> > RESOLVED is a deferred error with a receipt.** The resolution was one set difference.
> > ⚠ Units: `29`, `17`, `12` are all **ARMS** — not prompts, not criteria.
> >
> > ⭐ **RECOMPUTED ON THE 12, R890 — SAME ESTIMATOR, SO THIS IS A POPULATION DIFFERENCE AND NOT
> > A SPECIFICATION ONE.** The `25 procedurally distinct` / `1.6 vs 3.6` figures were computed on
> > the **29-arm clause-② set**. On the 12 that survive BOTH clauses:
> > · **8 procedurally distinct of 12**, at R875's inherited criterion `r > 0.9999`. Five pairs
> >   sit at **exactly r = 1.000000**: `topw_k4 == _detA == _detB`, `coval_core_2bA == _2bB`,
> >   `generic == generic_reprov`. ⭐ **No pair at all lies between 0.99 and 0.9999**, so the
> >   count does not depend on where the cutoff is put.
> > · **PR = 1.8751 effective dimensions** against a size-matched null of median **3.2101**,
> >   95% CI [2.5796, 4.0393], over 1000 random 12-subsets. **Observed percentile 0.000** —
> >   below every draw. ⚠ That is the resolution FLOOR, `1/(N+1) ≈ 0.001`; it means *lower than
> >   all 1000*, not a p-value smaller than that.
> > ⭐⭐ **THE CONCENTRATION IS NOT AN ARTIFACT OF THE 29.** R876 on the 29-arm set: PR 1.6368 vs
> > null median 3.5605, percentile **0.000**. R890 on the 12: 1.8751 vs 3.2101, percentile
> > **0.000**. **Same verdict after dropping 57% of the extension** — so the definition admits
> > several KINDS (8, not 3 as the arm NAMES suggest) that nonetheless span **less than two
> > effective dimensions**, more concentrated than any random draw of the same size.
> > ⛔⛔ **DOWNGRADED R891 — THAT CONCENTRATION IS CLAUSE ②'s, NOT THE DEFINITION'S.**
> > All three rounds above compared the admitted set against a **UNIFORM** random subset of the
> > 99. But the admitted arms are **by construction the high-scoring ones**, and if there are few
> > ways to be right and many to be wrong, any high-scoring subset is concentrated. **The sham:
> > draw 12 at random from the 28 that clause ② already admits** — score-matched by construction,
> > with only clause ③'s label criterion removed.
> > · uniform null (12 of 99): median **3.2101** → observed percentile **0.000**
> > · **score-matched null (12 of the 28): median 1.7672 → observed percentile 0.710**
> > **The observed 1.8751 sits comfortably INSIDE the score-matched null.** Contributions, reported
> > apart and NOT summed: clause ② **−1.4429**, clause ③ **+0.1079** — clause ③ does not
> > concentrate the set at all, and if anything mildly diversifies it.
> > ⭐ **So the finding is RE-SCOPED, not retracted: the admitted set IS one direction wide, but
> > that is what scoring well does, not what the two-clause definition does.** Any sentence
> > crediting the DEFINITION with the concentration is withdrawn.
> > ⚠ The matching is REAL, not nominal: the 12's margins (median +0.0219, range +0.0091…+0.0326)
> > are spread through the 28's (+0.0326, +0.0091…+0.0861), so the pool is not a top-slice.
> > ⚠ Controls: the uniform null reproduced R890's median to 4 decimals at the same seed; PR of 5
> > identical vectors = 1.000000; the score-matched null went both ways around the observed
> > (290 above, 710 below), so the contrast could have failed.
> > ⛔ DERIVATION, not evidence: `PR < n` means the arms are not mutually independent — forced by
> > the algebra. The measured question is only ever *concentrated RELATIVE TO WHAT*.
> > ⚠ My own prefix reading — *"3 `coval_core*`, 2 `generic*`, 7 `topw_k*`, so three procedures"*
> > — was **measured and OVERTURNED**: `topw_k2/k3/k6/k8` are not aliases of one another. A
> > prefix is not a measurement, including when it is my own suspicion.
> > ⚠ `0.28 MDE` is still the 29-arm figure and is NOT recomputed here.
> >
> > ⚠ **On this release that admits 28 arms** *(including the core)*, **of which 25 are
> > procedurally distinct**; the admitted set spans **1.6 effective dimensions** against **3.6**
> > for a random 25, and its **closest member clears the boundary by 0.28 MDE**.
> >
> > ⛔ **CORRECTED R886.** This read *"WITH THE COMPARATOR AND THE ADMISSIBILITY CRITERION
> > NAMED"* — as though the criterion were irreducible. **R881 measured that criterion B's BH
> > correction binds for 0 of 28 admitted arms while the CI condition binds for all 28**, so the
> > criterion is **one condition, not two**. That finding reached this file as an annotation ~200
> > lines below and never reached the sentence a reader actually quotes — *a correction that did
> > not reach the artifact it was about.* The breadth and the marginality are now **in** the
> > statement for the same reason.
> > ⚠ **Units, because six rounds just failed on them:** `28` and `25` are **arms**, `1.6` and
> > `3.6` are **effective dimensions**, `0.28` is **MDE**. ⚠ And unchanged: *the definition
> > describes the instance* stays live — one release, one core.
> >
> > ⭐⭐⭐ **WHAT THE LEAKAGE CONTRAST ACTUALLY MEASURES — THREE ROUNDS, ONE STANDING RESULT
> > (R897–R899).** The gap is not mainly about the arms:
> > · **SIZE — 57%.** `R²_LOO = 0.5669` of each cell's per-prompt gap is a component SHARED across
> >   all 8 (rule, k) cells. Leave-one-out, because regressing a cell on a mean containing it is
> >   circular; **the inflation is measured, not asserted: +0.0904** (0.6573 circular vs 0.5669).
> > · **RELIABILITY — 0.87.** Split-half over all **35** balanced disjoint 4-vs-4 splits:
> >   mean **r = 0.8730** [0.7577, 0.9136]; Spearman-Brown **0.9322** *(DERIVED — assumes parallel
> >   halves; length holds, parallel does not)*. Stratified by how many rules a split separates,
> >   it is flat — 0.8750 / 0.8550 / 0.8851 — so **it is not a rule-family effect.** Positive
> >   control (raw margins) 0.9440; placebo (permuted half) 0.0586.
> > · **NAME — none.** Against every arm-free property the release exposes, only `n_annotators`
> >   survives BH, at **r = −0.0982** — smaller in magnitude than the largest null draw in that
> >   round (0.1264). ⛔ `human_tie_rate` moves the leaky arm −0.5771 and the held-out arm
> >   −0.5486 and **cancels in the difference (−0.0301)** — the difference-of-bounded-scores
> >   artifact, observed. R877 found tie rate at **+0.5662** for the admitted set's PC1; **that is
> >   a different object and the two share only the phrase "a prompt axis".**
> > ⭐ **SO: a large, highly reliable, prompt-level quantity that this release cannot name.**
> > A small real cell signature survives underneath it (residual cross-judge r +0.0952…+0.1984
> > against a mismatched floor of [−0.0759, +0.0248], weakest at 3.0 SE).
> > ⚠ Reliable is not interesting: split-half says STABLE, never MATTERS. And naming it would
> > need a prompt property the release does not ship.
> >
> > ⭐⭐⭐ **WHAT `ADMITTED` SPANS — THE CRITERION-SOURCE PARTITION, COMPLETE (R903–R905).**
> > The admitted arms do not merely disagree about criteria; **their criteria come from three
> > structurally different SOURCES**, verified from the committed strings and the release's own
> > schema (`coval_full` items carry a `rubric_item_id`; **`coval_core` items carry none** — the
> > data model itself says the core's criteria are free text, not rubric references):
> >
> > | source kind | arm | exact ⊆ rubric | lexical coverage @0.60 |
> > |---|---|---|---|
> > | **rubric selector** | `topw_k*`, `topabs_k4` | **1.000** | **1.0000** |
> > | **paraphrasing generator** | `coval_core` | **0.001** | **0.5959** |
> > | **fixed external checklist** | `generic` | 0.000 | 0.0003 |
> >
> > ⭐ **The core selects almost no rubric item verbatim (0.001) yet reuses ~60% of the rubric's
> > wording.** That independently reproduces `corebench/ablate_novel.py:5` — *40.3% have no
> > counterpart above 0.60*, i.e. 59.7% — to within 0.11 pp, with the arm comparison it lacked.
> > ⚠ **Threshold-dependent, so the curve is the result, not the cell:** 0.7850 / 0.5959 /
> > 0.4360 / 0.3017 at t = 0.50 / 0.60 / 0.70 / 0.80, all four committed thresholds read from
> > the source rather than chosen.
> > ⚠ **Every coverage figure is a LOWER bound:** `difflib` compares CHARACTERS, so it is
> > LEXICAL, not semantic — a true paraphrase sharing no wording is invisible to it.
> > ⛔ **And overlap is not a meaningful statistic ACROSS these kinds.** R903 reported `generic`
> > and `topw_k4` as *literally disjoint* and banked it as a finding; it is forced — two arms
> > drawing from disjoint vocabularies overlap 0 whatever the definition does. **RETRACTED.**
> > Within the one kind where overlap can vary, the admitted arms agree well: minimum Jaccard
> > **0.4475** against a random floor of **0.1820**.
> > ⭐ **So `admitted` means CLEARED THE BAR, and the bar is source-agnostic.** That is a
> > property of the definition worth stating plainly rather than a defect.
> >
> > ⛔ **AND THE PARTITION HAS A PRICE, WHICH IS WHY THE INVENTORY LOOKS THE WAY IT DOES
> > (R906–R907).** Asking whether the bar FAVOURS a source is not answerable here: over the 99
> > scored arms, `RUBRIC_SELECTOR` is 23/86 admitted (Wilson [0.185, 0.369]) and
> > `FIXED_CHECKLIST` is **1/1** ([0.207, 1.000] — width 0.793). The intervals overlap, so
> > ⛔ *(R915 CORRECTION: R906 reported this as **1/2 = 0.500**. The second member was
> > `genericpool16` — **the comparator itself**, whose margin against itself is exactly
> > 0.000000, so it can never be admitted. It is an INELIGIBLE unit, a **structural zero in
> > the denominator** — R902's finding one level up, with ARMS in place of prompts, hidden
> > because the denominator was 2. ⚠ The width moves 0.811 → 0.793, both above the 0.60
> > readability bound, so **the defect is real but NOT load-bearing** and the verdict
> > below stands. The other three kinds are unchanged.)*
> > **no source preference is demonstrable**; that is weaker than *the bar is source-agnostic*
> > and is the statement the evidence carries.
> > ⭐ **The limit is a PRICED WALL, not a missing run.** Every existing selection arm costs
> > *0 judge calls* for one reason: it is a **subset of `coval_full`**, already judged. A fixed
> > checklist is by definition NOT a subset, so each new one costs `k × 4 × 968` =
> > **15,488 judge calls** — 6–8 of them, enough to make the comparison decidable, is
> > **92,928–123,904 calls.** ⚠ Measured: which kinds are subsets (rubric 1.000, checklist
> > 0.000) and their k. Derived: the multiplication. Priced in CALLS only — not wall-clock or
> > money. ⚠ And **no committed builder for `generic`/`genericpool16` exists anywhere in the
> > repo** — searched with the search itself controlled.
> > ⭐ **[D5, inference]** That asymmetry very likely explains the inventory's shape — 86 rubric
> > selectors against 2 checklists — so *what got built* was steered by *what was free*. Stated
> > as inference, not measurement.
> >
> > ⛔⛔ **A QUALIFIER ON EVERY NUMBER BELOW (R913): THE COMPARATOR IS ITSELF ONE OF THE ARMS.**
> > Clause ② says *"beats a NAMED prompt-blind comparator"*, and every admission decision in
> > this arc used exactly one — `genericpool16` — which **is one of R881's 99 scored arms.** So
> > the set has been scored against one of its own members throughout. R913's self-inclusion
> > control was written to catch that in the ALTERNATIVES and caught it in the incumbent.
> > ⛔ **And the sweep that would have tested it is BLOCKED, for a reason that is not a
> > shortage.** The release's four other named prompt-blind arms — `transport_generic`,
> > `transport_randblind_s0/s1/s2` — are **on disk** but raise
> > `ValueError: too many values to unpack` in `load_sat`: **a different key schema**, so this
> > arc's instrument cannot read them at all.
> > ⚠ Wiring anchor: under `genericpool16`, on R881's arms only, admission reproduces **28 vs
> > 28** — so the numbers below are internally sound; what is untested is whether they SURVIVE a
> > different comparator. **They are comparator-CONDITIONAL until that schema is bridged.**
> > ⛔ **REGISTER ENTRY CORRECTED (R914) — R913 WROTE IT IN THE FLATTERING DIRECTION.**
> > R913 said comparator robustness *"would require a loader for the `transport_*` schema"*.
> > One read of the keys kills that: `genericpool16` is `<uuid>|<idx>|A` — **3 fields, a
> > CoVal UUID, an A/B/C/D response** — while all four `transport_*` files are
> > `c365|int10006|ut3170|0` — **4 fields, non-UUID ids, a numeric last field**, and 74,048
> > keys against 61,952. **They are a DIFFERENT CORPUS**, which is what
> > `R427_does_the_definition_transport_at_all` says in its own name. A loader would have
> > produced numbers on a different population — **the requirement understated the work,
> > which is the direction the standard forbids for unavailability claims.**
> > **IMPOSSIBILITY REGISTER, corrected:** *comparator robustness* — requires **a
> > prompt-blind arm on THIS corpus that is not already a scored arm**, priced by R907 at
> > **15,488 judge calls** (a fixed checklist is not a subset of `coval_full`).
> > ⚠ This does NOT say the definition fails to transport; R427 asked that question.
> > ⭐⭐⭐ **AND THE BAR DOES DISCRIMINATE — BY RULE (R908).** R906 asked the SOURCE axis and could
> > not answer at n=2; R907 priced fixing that at 15,488 calls/arm. **Both treated the inventory
> > as the obstacle. It is thin on the axis I chose and thick on one never looked at** — and the
> > thick axis is free, because every arm on it is a subset of `coval_full`:
> >
> > | rule | admitted/built | share | Wilson 95% | k range |
> > |---|---|---|---|---|
> > | `random_k` | **0/38** | **0.000** | **[0.000, 0.092]** | 2…12 |
> > | `topw_k` | 7/16 | 0.438 | [0.231, 0.668] | 1…12 |
> > | `greedy_k` | 6/8 | 0.750 | [0.409, 0.929] | 2…12 |
> > | `oracle_k` | 5/7 | 0.714 | [0.359, 0.918] | 4 |
> > | `indep_k` | 5/8 | 0.625 | [0.306, 0.863] | 2…12 |
> >
> > **Four disjoint Wilson pairs, every one against `random`.** So clause ②'s bar separates
> > **informed selection from random selection**, decisively and for free.
> > ⚠ **The zero is a MEASUREMENT, not an algebraic necessity** — a random k-subset could clear
> > the bar by chance, and the control is that `topw` IS admitted at k = 2, 3, 4, 6, 8 where
> > `random` is 0.
> > ⛔ **And the k question closes for the third time by the same arithmetic.** Within `topw`,
> > 16 arms over 7 k values is ~2 per cell; every per-k Wilson interval is ≥ 0.654 wide.
> > Printed, never quoted. (R902 caught this at n=1, R906 at n=2, R908 at n≈2.)
> > ⚠ **What it does NOT say: WHY.** It shows THAT the bar separates these rules — not what it
> > separates on — and no share here is an admission probability, since the arms were built.
> >
> > ⭐⭐ **AND IT REWARDS A SPECIFIC SELECTION OBJECTIVE, NOT MERELY BEING INFORMED (R909–R910).**
> > Among **label-free** rubric selectors — label-consuming rules excluded, since R900/R907 made
> > label access a separate axis — the split is what the rule optimises, read from the
> > generator's docstrings: `topw` takes the **highest signed MEAN importance**; `topabs`,
> > `topvar`, `topwvar` take **|mean| or variance**.
> >
> > | objective | spec | adm/built | Wilson 95% |
> > |---|---|---|---|
> > | signed mean weight | pooled | 7/16 | **[0.231, 0.668]** |
> > | variance or magnitude | pooled | **0/14** | **[0.000, 0.215]** |
> > | signed mean weight | matched k=4 | 3/4 | [0.301, 0.954] |
> > | variance or magnitude | matched k=4 | 0/8 | [0.000, 0.324] |
> >
> > **Disjoint in the pooled specification by +0.016.** ⚠ **NOT in the matched-k=4 one**
> > (−0.024) — 1 of 2 specifications separates, and both are reported.
> > ⭐ **The route matters more than the number.** R909 missed separation by 0.024, reported the
> > near-miss AS a near-miss, and pre-registered the kill — *disjoint in either specification, or
> > WORLD B stands*. Six new arms were then generated at **k values not yet built, never by
> > expected outcome**, for **0 judge calls** (verified: rubric selectors are subset 1.000 of
> > `coval_full`). All six came back not admitted. **Overturned by more data, not by argument.**
> > ⚠ **Only one group was enlarged** — `topw` is still 16 arms / 4 at k=4 — so the separation
> > comes entirely from the variance group's interval tightening 0.324 → 0.215, which is what
> > more data should do if the effect is real, and the comparison is asymmetric by design.
> > ⚠ Cross-round wiring: the admission test reproduced R881's `lo` on four reference arms to
> > within **0.00032** — numbers checked, not only verdicts.
> >
> > ⭐⭐⭐ **STRENGTHENED BY BALANCING (R911) — BOTH GROUPS GROWN AT THE SAME NEW k.** R910's
> > separation came entirely from one interval shrinking. Twelve more arms were built at
> > **k = 5, 7, 9** — four rules × three k, **0 judge calls** — so both sides move and a genuinely
> > **k-matched** population exists for the first time.
> >
> > | specification | signed | variance/magnitude | disjoint | gap |
> > |---|---|---|---|---|
> > | **PRIMARY, k-matched {2,4,5,7,8,9}** | **8/11 [0.434, 0.903]** | **0/17 [0.000, 0.184]** | **yes** | **+0.250** |
> > | pooled over k | 10/19 [0.317, 0.727] | 0/17 [0.000, 0.184] | yes | +0.133 |
> > | matched k=4 | 3/4 [0.301, 0.954] | 0/8 [0.000, 0.324] | **no** | −0.024 |
> >
> > **The gap widens +0.016 → +0.250 once both sides move.** The three new `topw` arms are ALL
> > admitted (+0.0127…+0.0225) and the nine new variance arms ALL rejected — so signed-weight
> > selection clears the bar across k, not only at k=4.
> > ⛔ **The obvious fix would have been fake n.** `topw_k` is DETERMINISTIC (R890: replicas at
> > r = 1.000000), so re-running a covered k yields identical copies. Growth had to come from
> > **new k**, and the round asserts in code that no new arm duplicates another's selections.
> > ⚠ **1 of 3 specifications does NOT separate** (matched k=4, −0.024) and is reported, not
> > dropped. Three specs is a wider family than R909's two, which is why the **primary was
> > designated before the run** rather than chosen after.
> >
> > ⭐ **AND THE LAST DISSENTING SPECIFICATION FLIPS — BUT IRREDUCIBLY ONE-SIDEDLY (R912).**
> > `--select-npz` re-runs a satisfaction-consuming rule on a DIFFERENT satisfaction while still
> > emitting values from the same judge, so two new k=4 variance arms were built at 0 judge calls
> > (`topvar_k4_sel08`, `topwvar_k4_sel08` — selection from 0.8B, **values from 2B**, so R895's
> > judge-mixing defect is not reintroduced). They differ from their originals on **931/968**
> > prompts and are **both rejected**, with the most negative margins in the group (−0.091,
> > −0.071). k=4 goes **0/8 → 0/10**, [0.000, 0.324] → **[0.000, 0.278]**, and the gap moves
> > **−0.024 → +0.023**. **All three specifications now separate.**
> > ⛔⛔ **AND THE STRUCTURAL FACT LEADS RATHER THAN TRAILS.** `select_core.py:72` says
> > `topw_k` and `topabs_k` are **satisfaction-BLIND**, so `--select-npz` cannot make a new
> > SIGNED arm at k=4. **Only the variance side can grow there — growing one side is the very
> > defect R911 fixed everywhere else, and at k=4 it is irreducible.**
> > **IMPOSSIBILITY REGISTER, new and STRUCTURAL:** *a balanced k=4 comparison* — would require
> > **a second signed-weight rule that consumes satisfaction**, and the generator has none.
> > ⚠ **So the k=4 result is weaker than the k-matched one by construction, whatever its verdict.
> > R911's PRIMARY specification (+0.250) remains the one to quote.**
>
> | clause | verdict | comparator | criterion |
> |---|---|---|---|
> | **①** better than a draw of the prompt's own rubric | ⛔ **DROPPED — dominated** | n/a: no comparator rescues a dominated bar | invariant (no threshold) |
> | **②** better than a prompt-blind set | ⭐ **RETAINED — the only clause doing score work** | **must be named**; published `argmax_arm`; **vacuous at `per_prompt_max` (0 of 99, oracle included)** | **must be named**; `ratio ≥ 1.5` is *strictly* stricter than BH q=0.05 + CI |
> | **③** consumes no prompt-specific labels | ⭐ **RETAINED — provenance, no bar** | invariant | invariant |
> | **④** better than every criterion-free rule | ⛔ **DROPPED — vacuous or unmet at every comparator** | none makes it both meaningful and satisfied | **UNVERIFIABLE** — its negative control clears the clause |
>
> ⭐ **Why ① goes:** the bar ordering is MEASURED — ② **0.5404–0.5462** > ① **0.4922** > ④′
> **0.4820** (R857) — and R347 had already committed that ①'s binding region is empty by arithmetic
> (`ref_gap_min = 0.0470`, ②'s reference exceeds ①'s on **every** arm, `contingent: []`).
> ⭐ **Why ④ goes:** its meaningful window is a **single** comparator, `family_p90`, and the
> published `argmax_arm` is **outside** it — there `random_k4_s0` scores **+1.816** and clears the
> bar. At `family_p90`, the one comparator where ④ has content, `coval_core` scores **−0.565** and
> **fails** it. **At every comparator where the core passes ④, so does random noise** (R867).
> ⭐ **Why ② must carry its scopes:** its extension runs **29 → 0** across six defensible
> comparators (R866) and **23–24 vs 29** across the two criteria, with A a **strict** subset of B at
> every seed (R865). **A count quoted without both is arbitrary, not merely imprecise.**
>
> ⚠ **SIZE:** the design supports *"more than one"*; **3 to 8 are indistinguishable**, so no number
> is stated. That is what the k-sweep could resolve, not a preference.
> ⚠ **THE CEILING ON ALL OF IT, unretired:** this is still written from a release shipping exactly
> **ONE** core, so *the definition describes the instance* stays live for every clause above. **It
> would take a second release with a differently-built core to retire it** — and that is an
> availability claim in the unflattering direction, not a plan.

> ⛔⛔ **AND THE BREADTH IS NARROWER THAN THE ARM-COUNT SUGGESTS — R876, both controls PASS, D8.**
> R875 measured that the two retained clauses admit **25 procedurally distinct arms**, with the
> minimum correlation to the core (**+0.5406**) *below* the random negative control's own
> (**+0.5798**). That answered *does the definition reach past its instance*. **It did not answer
> what it reaches** — and a definition admitting 25 copies of one alternative is a different object
> from one admitting 25 different things, indistinguishable in any min-correlation statistic.
>
> ⭐ **Measured threshold-free**, because R875's verdict had used a `0.7` cutoff I invented and
> clustering would have needed the same kind of guess. The **participation ratio** of the
> correlation eigenspectrum, `PR = (Σλ)²/Σλ²`, is an effective count of independent directions and
> takes no cutoff: **PR = 1 for identical vectors, PR = k for k orthogonal ones.**
>
> | set | n | PR |
> |---|---:|---:|
> | **admitted by ② + ③** (aliases excluded) | **25** | **1.6368** |
> | size-matched random subsets of all arms | 25 | **3.5605**, 95% [3.0313, 4.2135] |
> | the random family, as a second reference | 38 | **3.3054** |
>
> ⭐⭐⭐ **The admitted set sits at the 0.0th percentile — below ALL 999 null draws.** Twenty-five
> arms occupying **1.6 effective dimensions** where a random twenty-five occupies **3.6**.
> **The definition admits a NARROW BAND, not a category.**
>
> ⛔ **This qualifies R875's closing sentence and the qualification is the finding.** *"The
> definition is not merely re-describing `coval_core`"* stands — the minimum correlation really is
> below the random control's. **But "25 procedurally distinct arms" overstates the breadth**: they
> are distinct from the core and **not from each other**. The reach past the instance is real and
> it is **one direction wide**.
>
> ⭐ **Controls, both on REAL objects:** PR of five identical vectors = **1.000000** exactly (a
> measure that does not collapse duplicates cannot be read as a count of distinct things); and
> adding the two **real** aliases `coval_core_2bA/2bB` to a ten-arm set moves PR by **+0.3979 ≤ 1**
> — they carry no new direction, as an alias should not.
>
> ⚠ **Unchanged: nothing here retires `the definition describes the instance`.** If anything it
> tightens the limitation — the clauses are non-degenerate, and the set they pick out is narrow
> enough that a second release remains the only thing that could settle whether they define a
> category or trace one contour of a single object.

> ⭐⭐⭐ **AND THE AXIS HAS A NAME: THE HUMAN TIE RATE — R877, four controls PASS, D8.**
> R876 left the admitted set at **1.6 effective dimensions** with that direction unnamed. R877 takes
> **PC1 of the 25×968 score matrix in prompt space** — which explains **77.08%** of the admitted
> set's variance, consistent with the PR — and correlates it against prompt properties **split by
> whether they can see an arm score at all.**
>
> | candidate | kind | r | p | BH |
> |---|---|---:|---:|:--:|
> | `mean_A2_of_REJECTED_arms` | PARTIALLY INDEPENDENT | **−0.7069** | ≤0.001 | ✓ |
> | ⭐ `human_tie_rate` | **INDEPENDENT** | **+0.5662** | ≤0.001 | ✓ |
> | `mean_response_length` | INDEPENDENT | +0.1013 | 0.0020 | ✓ |
> | `n_annotators` | INDEPENDENT | −0.0838 | 0.0080 | ✓ |
> | `response_length_spread` | INDEPENDENT | +0.0833 | 0.0130 | ✓ |
>
> ⚠ **The bottom three are RESOLVED BUT NEGLIGIBLE** — `r ≈ 0.08–0.10` survives BH and means
> nothing. Calling them "tracked" would confuse significance with magnitude, so they are listed and
> dismissed. ⚠ And **`p ≤ 0.001` is the resolution floor** (1000 draws → 1/1001), not a measurement
> of 0.001.
>
> ⭐⭐ **THE ONE CHECK THAT DECIDED IT.** A prompt where humans tie a lot is plausibly also a prompt
> where any arm's A2 behaves oddly — so `human_tie_rate` could be the difficulty proxy under another
> name. They do share variance (`r = −0.4752`, `r² = 0.2258`). **But the partial correlation
> `corr(PC1, tie | difficulty) = +0.3700` — the tie rate SURVIVES controlling for difficulty.** It
> is a third smaller than the raw +0.5662, so difficulty accounts for about a third of it and not
> the rest.
>
> ⭐⭐⭐ **WHAT THIS SAYS ABOUT THE DEFINITION, and it is not flattering.** The set the two retained
> clauses admit is essentially **one axis**, and that axis co-varies with **how often the humans
> declined to choose**. So the definition may be selecting on **tie-handling behaviour** as much as
> on criterion quality — a property of how an arm resolves indifference, not of what it measures.
> **That is a live alternative reading of clause ②, and nothing measured so far excludes it.**
>
> ⚠ **CORRELATION IS NOT IDENTITY.** This licenses *"the axis co-varies with the tie rate"*, never
> *"the axis IS the tie rate"*. ⚠ And the wiring control — `|corr(PC1, mean A2 of admitted)| =
> 0.9999` — is **circular by construction** and is reported as a wiring check, never as evidence.
>
> ⚠ **A correction to my own NEXT, recorded because it was written from memory.** Check #543 asked
> for *"the per-prompt loadings of R876's eigenvector"*. **R876's eigenvector is over ARMS** (25×25);
> its components are 25 per-arm loadings, not 968 per-prompt ones. The per-prompt axis is a
> different object, and the matrix was in the artifact the whole time.

> ⭐⭐⭐ **AND THE TIE-RATE READING IS EXCLUDED FOR THE CLAUSE'S VERDICT — R878, four controls PASS,
> D8.** R877 left a live alternative: clause ② may be rewarding **tie-handling behaviour** rather
> than criterion quality. Correlation cannot separate those; **stratification can.** Prompts split
> into tie-rate terciles, ②'s admitted set recomputed inside each.
>
> | | mean pairwise Jaccard |
> |---|---:|
> | **TIE strata** (0.000–0.094 / 0.094–0.152 / 0.152–0.632) | **0.8998** — pairs 0.963, 0.852, 0.885 |
> | **RANDOM splits** at matched sizes, 90 draws | **0.8640**, 95% [0.7007, 0.9692] |
> | observed percentile in the reference | **60.0** |
>
> ⛔ **THE WHOLE DIFFICULTY WAS ONE CONFOUND, NAMED BEFORE THE RUN.** Stratifying cuts n from 968 to
> ~322, so **membership moves from power loss alone** — a bare *"the admitted set changed"* would
> have looked like a finding while measuring only the split. **Everything is read against random
> splits at matched size, never against 1.0.**
>
> ⭐⭐ **WORLD A: membership moves no more than resampling explains.** So **clause ②'s VERDICT does
> not track the tie rate**, and R877's `+0.5662` is a property of **the axis along which admitted
> arms co-vary**, not of **who gets admitted**. ⭐ **The axis and the verdict are different objects,
> and only this round could tell them apart.**
>
> ⚠ **BOUNDED BY ITS OWN POWER, and the bound is wide.** The reference CI is [0.7007, 0.9692], so
> WORLD B needed the observed to fall below **0.70** — a large membership shift. **This design
> excludes a big tie-rate dependence and cannot exclude a small one**, and 3 terciles is the only
> stratification tested.
> ⚠ Controls: `oracle_k4` admitted in **every** stratum — the arm that decides whether the split
> left enough power to read anything; `random_k4_s0` in **none**; reference spread `sd = 0.0671`.
> ⚠ `NBOOT` was cut 1500 → 500 and `NREF` 200 → 90 after the first run timed out — **applied to
> BOTH arms**, because cheapening only the reference would put the observed value and its null on
> different instruments. Both are noisier; they remain comparable to each other, which is all this
> round needs.
>
> ⭐⭐⭐ **AND R878's NULL NOW HAS A SIZE — R879, three controls PASS, D8.** R878 said WORLD B needed
> the observed below **0.70**, a large shift, and a null quoted without saying how large *"large"*
> was is the shape this project keeps retracting. R879 sweeps the stratum count.
>
> | k | ref mean | ref p2.5 | **MDE** | TIE J | DIFF J *(pos. ctrl)* | rnd2 J *(g=0)* |
> |---:|---:|---:|---:|---:|---:|---:|
> | 2 | 0.9272 | 0.8576 | 0.0696 | 0.8621 | **0.7097** | 0.9286 |
> | ⚠ **3** *(R878)* | 0.8512 | 0.7247 | **0.1266** | 0.8998 | **0.6647** | 0.8001 |
> | 4 | 0.7764 | 0.6926 | 0.0838 | 0.7619 | **0.6232** | 0.8438 |
> | 5 | 0.7217 | 0.6607 | 0.0610 | 0.6913 | **0.6222** | 0.7368 |
> | 6 | 0.7082 | 0.6680 | 0.0402 | 0.6843 | **0.5936** | 0.6707 |
> | ⭐ **7** | 0.6933 | 0.6646 | **0.0287** | 0.6807 | **0.6288** | 0.6943 |
> | 8 | 0.6902 | 0.6553 | 0.0349 | **0.6571** | **0.6428** | 0.6819 |
>
> ⛔ **R878 RAN AT THE WORST k IN THE SWEEP.** Its `k=3` has **MDE 0.1266** against **0.0287** at
> `k=7` — **4.4× looser than was available**, and nothing in R878 chose 3 for a reason.
>
> ⭐⭐ **BUT THE NULL HOLDS ANYWAY, AND NOW MUCH TIGHTER.** `TIE J` never falls below `ref p2.5` at
> **any** k. **So clause ②'s verdict is invariant to tie rate against a membership shift of 0.0287
> or larger** — a bound 4.4× sharper than the one R878 stated. ⚠ **Smaller shifts remain open**, and
> at `k=8` the margin is **0.6571 vs 0.6553 = 0.0018**, razor-thin; the null is holding, barely, at
> the finest split tested.
>
> ⭐ **The positive control is what makes the zero a measurement.** Stratifying by prompt DIFFICULTY
> — which R877 measured at `r = −0.7069` with the admitted set's axis — is **detected at every one
> of the seven k**, and its Jaccard sits below the tie stratification's at every k. **A design that
> sees difficulty everywhere and tie nowhere is reporting a contrast, not a silence.**
>
> ⛔ **AND THE ROUND REFUTED ITS OWN PREMISE.** Check #545 asked to *"read where the CI NARROWS with
> k"*, assuming more strata buys resolution. **Two effects compete** — fewer prompts per stratum
> (noisier) versus more pairs averaged (less noisy) — **so it was a fork, not a derivation.** The
> curve settles it toward narrowing, but non-monotonically: `0.0696 → 0.1266 → 0.0838 → 0.0610 →
> 0.0402 → 0.0287 → 0.0349`. **That is the third time this session a NEXT presumed its own answer.**
>
> ⭐⭐⭐ **AND THE ADMITTED SET IS EXACTLY STABLE IN THE RESAMPLING BUDGET — R880, four controls
> PASS, D8.** R878 ran at `NBOOT=500`, R865 at `2000`, and R875/R876/R877 inherited whichever they
> were handed. **If clause ②'s admitted set moved with that number, "25 arms" and everything stacked
> on it would be a resampling artifact.** Swept 250 → 8000 at two seeds:
>
> | NBOOT | 250 | 500 | 1000 | 2000 | 4000 | 8000 |
> |---|---:|---:|---:|---:|---:|---:|
> | admitted | 28 | 28 | 28 | 28 | 28 | 28 |
> | Jaccard vs the 8000-set | **1.0000** | **1.0000** | 1.0000 | 1.0000 | 1.0000 | — |
> | flips vs reference | 0 | 0 | 0 | 0 | 0 | — |
>
> ⭐⭐ **Identical at every budget and both seeds — zero flips.** So `NBOOT=500` was already enough
> and **no downstream count is a resampling artifact on this axis.**
>
> ⭐⭐⭐ **AND THAT IS A SUBSTANTIVE PROPERTY OF THE CLAUSE, NOT A FORMALITY: the admitted set is not
> MARGINAL.** The check could plainly have failed — arms sitting near the BH boundary would flip
> between draws. **None does.** At n=968 the 28 arms are far from the decision boundary in both
> directions.
>
> ⭐ **FULL RECONCILIATION ACROSS FOUR ROUNDS, computed rather than asserted:**
> **28** (R880, total) = **1** core + **2** aliases (`coval_core_2bA/2bB`, r > 0.9999) + **25**
> distinct — and 28 − 1 = **27** is exactly R875's *"admitted besides `coval_core`"*, while 25 is
> exactly R876's population. **Four rounds, four numbers, one object.**
>
> ⛔ **THE DERIVATION, STATED SO IT IS NOT MISTAKEN FOR THE FINDING:** Monte-Carlo error falls as
> `NBOOT → ∞`, so the largest budget is the best estimate **by arithmetic**. What was measured is
> the **convergence**, and it is immediate.
> ⚠ **SCOPE, and it matters:** this is the FULL 968-prompt population. R878/R879 stratified to
> ~322 and ~138 prompts, where the set does move — that movement is what their Jaccards measure.
> **Stability at full n does not imply stability at stratum n**, and R879's MDE curve is the number
> that governs there.
>
> ⛔⛔⛔ **AND R880's "NOT MARGINAL" IS RETRACTED — R881, four controls PASS, D8.** R880 saw zero
> flips across a 32× budget range and concluded the 28 arms sit *"far from the decision boundary"*.
> **That was an inference, and R881 measured the quantity it stood in for.**
>
> ⭐ **CI slack among the 28 admitted, in A2 units:** min **+0.00314** · p25 +0.01415 ·
> median +0.02070 · max +0.07808, against a typical per-arm MDE of **0.01126**.
> **The closest admitted arm sits 0.28 MDEs above the boundary**, and four are inside 0.6 MDE:
> `topw_k2` **0.28** · `greedy_k12_fit1` **0.39** · `generic` and `generic_reprov` **0.51**.
> **That is hairline, not far.**
>
> ⭐⭐ **WHY ZERO FLIPS WAS NEVER EVIDENCE OF DISTANCE.** Bootstrap Monte-Carlo error at
> `NBOOT ≥ 250` is far smaller than 0.28 MDE, so **the ESTIMATE of `lo` is precise even when `lo`
> itself is small.** R880 read **the precision of the instrument** as **the distance of the
> object** — and that is the alternative R881 was built to separate.
>
> ⭐⭐⭐ **AND A SECOND FINDING THAT NEEDS NO THRESHOLD: criterion B's BH correction is DECORATION.**
> **BH binds for 0 of 28 admitted arms; the CI condition binds for all 28.** That is a count, not a
> comparison against a cutoff. **So clause ②'s criterion B reduces to its CI condition** — simpler
> than it has been written throughout this project.
>
> ⛔ **AND MY OWN CUTOFF DECIDED WHICH FINDING PRINTED.** The branch read
> `C if closest/MDE < 0.25`. The measured value is **0.28**. **Had I written 0.30, the file would
> print "the set IS marginal" instead.** Nothing justified 0.25, and **the two worlds are not
> alternatives — both are supported by the same numbers**, so both are reported. Sixth commission
> of the invented-threshold error this session.
>
> ⚠ **What survives from R880 untouched:** the set really is budget-invariant — 28 arms, Jaccard
> 1.0000, zero flips, two seeds. **That measurement stands; only the interpretation laid on top of
> it falls.** The corrected reading is **stable BUT marginal**: stable because the bootstrap is
> precise, marginal because 4 of 28 members clear by less than 0.6 MDE.

| clause | excludes | status | scope |
|---|---:|---|---|
| **①** better than a random draw of the prompt's own rubric | **0 of 41** | **DERIVED** — the region where ① could bind is empty by arithmetic (`GAP ≥ SLACK` on every arm) | R347 |
| **②** better than a prompt-blind set | **33 of 42** | **MEASURED** — carries the whole boundary among label-free arms | R360 |
| **③** no prompt labels | **14 of 42** | **DERIVED** from the source, not hand-listed (R444) — target-readers *and* w-readers | R360·R444 |
| **④** better than every criterion-free rule | **0 of 42** | **MEASURED** — coverage of this space is 42/42 | R440 |
| ⭐ *why that zero* — **④ is DOMINATED by ②** (R856, entry 1376) | ②'s comparator **0.5404** sits **+0.0584 above** ④′'s bar **0.4820**, so **②⇒④ is largely FORCED**: ④ can only bind on arms ② already rejected. **Everything ④ would exclude, ② already excluded.** | **DERIVATION** — labelled, not banked | R856 |
| ⭐⭐⭐ **AND SO IS ① — only ② does work** (R857, entry 1377) | **Bar ordering, measured: ② 0.5404–0.5462 > ① 0.4922 > ④′ 0.4820.** R347 already committed this for ① — verdict `W1_DERIVATION`, `ref_gap_min = 0.0470` (②'s reference exceeds ①'s on **every** arm), `contingent: []` — **and nobody generalised it.** **The definition reduces to ② + ③ (provenance, no bar) + the size floor.** | ordering **MEASURED**; domination **DERIVED** | R857·R347 |
| **④** *under the PERMISSIVE reading adopted by R824* | **25 of 58** | **MEASURED** — the rule class is supervised response-only predictors; 21 specification cells, held out over 20 splits | R824 |

> ⭐⭐⭐ **THE TABLE ABOVE IS UNDER-TYPED: IT HAS NO COLUMN FOR *WHICH CRITERION* — R865, D8.**
> R864 established that this project runs two admissibility criteria which disagree. This table
> records **one verdict per clause**, so it silently reports whichever criterion the author ran.
> R865 recomputed both, on one population, from ONE bootstrap, changing only the decision rule.
>
> ⛔ **HALF THE TABLE IS SETTLED BY ARITHMETIC.** Clauses **① and ③ are DERIVED** — no threshold,
> no interval, no multiplicity — so **there is nothing for a criterion to act on and their verdicts
> are criterion-INVARIANT by construction.** A derivation, assumption named: that the DERIVED
> labels are accurate, which R851 checked against the source. **At most two rows could ever move.**
>
> ⭐ **CLAUSE ② IS CRITERION-DEPENDENT, AND MEASURED** (99 arms, even annotators, `genericpool16`):
>
> | seed | A: `ratio ≥ 1.5` | B: BH q=0.05 + CI | both | only-A | only-B |
> |---:|---:|---:|---:|---:|---:|
> | 11 | 23 | 29 | 23 | **0** | 6 |
> | 22 | 23 | 29 | 23 | **0** | 6 |
> | 33 | 24 | 29 | 24 | **0** | 5 |
>
> ⭐ **`A ⊂ B` STRICTLY, at every seed — `only-A = 0` three times out of three.** The criterion gap
> is **5.7 against a seed spread of 1**, so it is READABLE and not resampling noise. **WORLD A: the
> 1.5 floor is the binding constraint, and ②'s published count is the FLOOR's count, not the
> clause's.** ⚠ The docstring predicted this nesting from `4.203·SE` vs BH's rank-dependent `q·k/C`
> **and explicitly refused to bank it** — after two rounds where a "forced" direction was refuted.
> This time the prediction held; that is one for three, which is why it was measured.
>
> ⚠ **CLAUSE ④′ IS UNVERIFIED, and for a reason already on record.** Its negative control
> `random_k4_s0` **satisfies** the clause — R850 measured the same failure at **7 of 8 class sizes**
> and R856 reported ④ as dominated by ②. **A random 4-criteria set really does clear it.** Its
> counts (58–59 vs 63) are in the artifact and are **not** folded into the verdict.
>
> ⛔ **AND THE FIRST RUN EXITED 2 BECAUSE OF A DEFECT I BUILT.** `ok_all` accumulated across BOTH
> clauses, so ④′'s expected failure overrode ②'s three clean controls and withheld a readable
> result. **§4's `the control fails for its own reasons`, in its contaminating form — a control
> failing for a DIFFERENT object's reasons.** The kill is now per clause.
> ⚠ Two smaller repairs, recorded because they are the same species: a KILL arm that compared
> `marg` across two `decide` calls **could not fail** (`marg` never touches the bootstrap) and was
> replaced, before running, by the seed-spread test above; and the surviving verdict line still
> reads *"across both clauses"* while its sum correctly covers only the readable one — **a verdict
> string that is prose, one more time.**
>
> ⭐ **NET, and this is what the table should say:** of four clause verdicts, **two are
> criterion-invariant by construction, one is criterion-dependent with both counts now measured,
> and one cannot be verified at all because its own negative control clears it.**
> ⭐ For the object: `coval_core` on clause ② scores margin **+0.024981**, ratio **+2.2524**, and
> **passes under BOTH** criteria — against the FIXED prompt-blind comparator. Against the
> **max over 1,820** it is 0.910 and fails one of the two. **Same core, same clause, two
> comparators, opposite verdicts — which is precisely the column this table does not have.**

> ⭐⭐⭐ **AND THE COMPARATOR IS NOT A COLUMN — IT IS THE WHOLE CLAUSE. R866, D8, all four kills PASS.**
> Six rounds attacked this comparison's denominator, threshold and criterion. **All six held the
> comparator fixed, and the two in use were never compared.** Swept across every defensible form,
> on one population, one bootstrap per cell, 99 arms:
>
> | comparator | core margin | core ratio | A `≥1.5` | B BH+CI | count A | count B |
> |---|---:|---:|:--:|:--:|---:|---:|
> | `single_genericpool16` | +0.024245 | **+2.2524** | ✓ | ✓ | 26 | 28 |
> | `family_mean` | +0.027912 | **+2.8166** | ✓ | ✓ | 26 | **29** |
> | `family_p75` | −0.000683 | −0.0683 | ✗ | ✗ | 13 | 13 |
> | `family_p90` | −0.017803 | −1.8459 | ✗ | ✗ | 11 | 12 |
> | ⭐ `argmax_arm` *(R860/R862/R864)* | +0.009002 | **+0.8639** | ✗ | **✓** | 13 | 17 |
> | `per_prompt_max` | −0.057981 | −6.2433 | ✗ | ✗ | **0** | **0** |
>
> ⛔ **WORLD C: the verdict flips AND the two criteria flip at DIFFERENT points.** Comparator and
> criterion **interact**, so clause ② has no verdict until BOTH are written into it.
>
> ⭐⭐ **CLAUSE ②'s EXTENSION RUNS FROM 29 TO 0 ON THE COMPARATOR CHOICE ALONE.** The published
> count sits at the **weakest** end of that range. **A count quoted without its comparator is not a
> weak claim — it is an arbitrary one.**
>
> ⭐⭐ **AND THE STRONGEST READING IS VACUOUS.** `per_prompt_max` — beat the best subset chosen
> afresh on every prompt, which is what *"better than EVERY prompt-blind set"* most naturally says
> in English — admits **0 of 99 arms, `oracle_k4` included.** A clause that excludes every
> admissible object is as empty as one that excludes none. **So the clause is bracketed between two
> degeneracies, and every useful reading lives strictly between them.**
>
> ⭐ **The ambiguity is in the clause's own wording and had never been written down.** Under a
> universal reading, *"better than a prompt-blind set"* admits **two different bars** this project
> has used interchangeably: the **ARGMAX ARM** (best subset by mean, then its per-prompt vector) and
> the **PER-PROMPT MAXIMUM**. They differ by **7.1 units of the statistic** (+0.8639 vs −6.2433).
>
> ⭐ **Where the six prior rounds were standing.** R860/R862/R864 all used `argmax_arm` — **the one
> comparator in the sweep where the two criteria disagree.** Not a coincidence: criteria only
> diverge where the margin sits near the bar, and that comparator places `coval_core` there. But it
> means **the entire denominator-and-threshold thread was conducted at the single point where the
> answer is criterion-dependent**, which is why it kept producing verdicts that needed another
> round to interpret.
>
> ⭐ **KILL ① was a derivation used as wiring, and it is the cheapest check in this file.**
> `mean ≤ p75 ≤ p90 ≤ per-prompt max` are pointwise non-decreasing, so the counts MUST fall:
> A `[26, 13, 11, 0]`, B `[29, 13, 12, 0]`. **Useless as evidence, perfect as a check** — a
> non-monotone result would have meant the implementation was wrong, not that the world was
> interesting. `single` and `argmax_arm` are outside that pointwise chain and are excluded from it.

> ⭐⭐⭐ **CLAUSE ④'s PUBLISHED VERDICT COMES FROM A REGIME WHERE RANDOM NOISE SATISFIES IT — R867,
> D8, both kills PASS, one shared 968-prompt population.** Two results from the preceding rounds
> were the same measurement seen from opposite ends: R865 found ④'s NEGATIVE control clears the
> clause (noise gets in), R866 found ②'s strongest comparator excludes even the ORACLE (the ceiling
> gets out). **Those are the two ways a clause can be empty, and the comparator moves between them.**
>
> ⭐ **DEFINITION USED HERE — a clause is MEANINGFUL at a comparator iff `random_k4_s0` does NOT
> clear it and `oracle_k4` DOES.** Outside that window the clause is decoration in one direction or
> the other, and **neither end is visible from a single cell**, which is why six rounds did not see it.
>
> | comparator | ② core | ② oracle | ② random | ② window | ④ core | ④ oracle | ④ random | ④ window |
> |---|---:|---:|---:|:--:|---:|---:|---:|:--:|
> | `family_mean` | +2.817 | +8.781 | −3.420 | **YES** | +17.710 | +24.234 | **+11.585** | no |
> | `family_p75` | −0.068 | +6.157 | −5.405 | **YES** | +7.620 | +14.199 | **+2.062** | no |
> | `family_p90` | −1.846 | +4.866 | −6.776 | **YES** | **−0.565** | +5.706 | −5.625 | **YES** |
> | ⭐ `argmax_arm` *(published)* | +0.864 | +6.700 | −4.409 | **YES** | +5.904 | +10.494 | **+1.816** | **no** |
> | `per_prompt_max` | −6.243 | **+0.518** | −9.650 | no | −7.900 | **−3.176** | −11.431 | no |
>
> ⭐⭐ **CLAUSE ② IS HEALTHY: its window is 4 of 5 comparators, and the published `argmax_arm` is
> INSIDE it.** It falls out only at `per_prompt_max`, and there because the **oracle** stops clearing
> (+0.518) — the strict degeneracy R866 found, now localised to its cause.
>
> ⛔⛔ **CLAUSE ④'s WINDOW IS A SINGLE POINT — `family_p90` — AND THE PUBLISHED COMPARATOR IS OUTSIDE
> IT.** At `argmax_arm`, `random_k4_s0` scores **+1.816** and clears the 1.5 bar. **So ④'s published
> count was measured in a regime where a random 4-criteria set satisfies the clause.** This is the
> mechanism behind two older observations that were never connected: R850's negative control failing
> at **7 of 8 class sizes**, and R856's finding that **④ is dominated by ②**. Both were symptoms of
> a comparator too weak to make the clause say anything.
>
> ⭐⭐⭐ **AND THE SHARPEST SENTENCE THE DATA SUPPORTS:** at `family_p90`, the ONE comparator where
> clause ④ has content, `coval_core` scores **−0.565 and FAILS it**. At every comparator where
> `coval_core` passes ④, **so does random noise.** **There is no comparator at which clause ④ both
> means something and is satisfied by the released core.**
>
> ⚠ **WORLD B fired, but WORLD D's condition ALSO holds and the code's `if/elif` ordering hid it.**
> D was check #530's actual hypothesis — that the ambiguity is a property of the DEFINITION's grammar
> — and `set(w②) != set(w④)` is true: the windows differ in KIND, 4 comparators versus 1. **Both are
> reported, because a verdict selected by precedence is a verdict that suppressed its alternatives.**
> The honest reading: the unresolved quantifier is a grammar defect the definition has throughout,
> and **② tolerates it while ④ does not.**
>
> ⭐ **KILL ① again as wiring, both clauses:** the controls must be monotone along the pointwise
> chain — once a control stops clearing it can never clear again. **PASS for both.** A derivation,
> useless as evidence, and the only thing that would have caught a mis-indexed family.

⛔ **SCOPE ADDED 2026-08-06 (entry 1322) — THE PARAGRAPH BELOW IS ABOUT THE READING THIS DOCUMENT NO
LONGER USES.** The statement at the top of this file adopts the **PERMISSIVE** reading of ④, and the
row directly above says so — *"under the PERMISSIVE reading adopted by R824 · **25 of 58**."* Under
that reading **④ does not cost nothing; it removes 25 of 58 arms.** Entry 1257 already retracted this
in scope: *"'④ excludes nothing at home' was never a fact about the clause — it was a fact about a
reading nobody had chosen."* **The correction reached the TABLE and never reached the ARGUMENT.**
Kept, annotated rather than deleted (L81), because it is the correct and still-live argument **for
the strict reading**, and the strict reading is a defensible cell of the specification curve — but it
is no longer the argument for the clause **as stated**.

⭐ **PARTLY REVERSED 2026-08-06 (entry 1328) — THE ARGUMENT SURVIVES THE READING CHANGE, THE NUMBER
DOES NOT.** The paragraph below argues ④ is *free where the definition works and binding where it
fails*. That turns on ④'s **MARGINAL** exclusion over ②, not on its **STANDALONE** count — and the
two were being conflated. R518 measured the marginal at the strict bar: among the **9 arms that pass
②**, every one clears ④'s bar by **4.90×–8.65× its own MDE**, so ④ removes none of them, WORLD B.
**Rebased onto the adopted permissive bar (0.519689, R824), all 9 still clear it — margins
1.84×–5.40×, none below the 1.5× admissibility floor**, the tightest being `topw_k8` (4.90× → 1.84×).
So ④'s **25 of 58** are *entirely among arms ② already rejects*, and the clause is free at the
conjunction under **both** readings.

> ⚠⚠ **AN EXPOSURE THIS BLOCK PREDATES, NAMED NOT ASSERTED (entry 1386).** R860 measured that when a
> bar is a **MAXIMUM over a family**, it carries its own sampling variability, and an MDE computed as
> though the bar were fixed is **understated** — there, by **1.56×** (0.0066 → 0.0103), which moved a
> ratio from **1.358 to 0.870**, across the 1.5 floor and across 1.0.
>
> ⭐ **④'s bar IS a maximum** — over the response-only family. **Whether R518's per-arm MDEs treat it
> as fixed is not stated in this block, and I have not opened R518 to check.** ⚠ **So this is a
> QUESTION, not a defect**, and it is recorded as one.
>
> ⚠ **Where it would bite, if it bites at all:** the tightest rebased margin here is **1.84×**
> (`topw_k8`). R860's measured correction factor on a structurally identical comparison was **1.56×**.
> `1.84 / 1.56 ≈ 1.18` — **below the 1.5 admissibility floor.** ⛔ **That arithmetic is an
> ILLUSTRATIVE PROPAGATION, not a measurement**: it imports a factor from a different comparison,
> which is precisely the borrowed-denominator move R860 just showed costs 56%. **It is written to
> locate the one cell where the question could change a verdict — and for no other purpose.**
>
> ⭐ **The other six `its own MDE` claims in this file were checked and are sound or already
> corrected**: two are mine and annotated (entries 1352, 1383), three are per-cell own MDEs that state
> their own limits, one is a register row. **This is the only cell where the question is open.**
>
> ⭐⭐⭐ **AND IT IS NOW ANSWERED, FROM SOURCE — the alarm NARROWS (entry 1387).** R518 line 27:
> *"NOISE FLOOR: each arm's own MDE, **as computed by R436**"* — so the denominator is imported, but
> from a round computing **the same comparison**. Going one level down to R436:
>
> | | |
> |---|---|
> | `run.py:249` | `bar_per = rule_per[best_rule]` — the bar's **per-prompt vector** |
> | the bootstrap | resamples **prompts**, with `d = arm − bar_per` — **both sides together** |
> | ⭐ **so the bar IS resampled with the arm** | a proper paired bootstrap, capturing their covariance |
> | ⚠ `run.py:187` | `best_rule = max(rule_mean, …)` — selected **once, before** the bootstrap, held **fixed** |
>
> ⭐ **So the MDE captures that rule's sampling variability but NOT the variability of WHICH rule is
> the max.** That is exactly the component R860 measured — **direction confirmed: understated.**
>
> ⚠⚠ **But the MAGNITUDE almost certainly does not transfer.** R860's 1.56× came from a max over
> **1,820** subsets; **R436's family is 30 rules — 60× smaller — and selection variability scales with
> family size.** ⭐ **So entry 1386's illustrative `1.84 / 1.56 ≈ 1.18` imported a factor from a
> 60×-larger family and OVERSTATED the concern** — the same borrowed-quantity move, one level up, and
> caught by reading the source instead of propagating a number.
>
> ⭐⭐ **Final status of this cell: the omission is REAL and its size is UNMEASURED.** The tightest
> margin, **1.84×**, would need a correction factor above **1.23** to fall under the 1.5 floor.
> **Whether a 30-rule selection carries that is unknown** — and it is the one thing this thread leaves
> open, stated as a magnitude nobody has measured rather than as a defect.
⛔ **This is a DERIVATION, not a measurement** — subtracting a known bar shift from published margins
is forced once both bars are known. **Assumption 1:** R518's `d` and R824's bars share one A2 scale —
**UNVERIFIED, and the two strict bars already disagree (0.4512 vs 0.455679)** because R823 widened the
rule class from 6 to 30. **Assumption 2:** each arm's MDE is unchanged by moving the bar. A measured
answer needs R518 re-run against R824's bar.

> ⛔⛔ **WITHDRAWN THE NEXT ROUND (entry 1329). Assumption 1 was tested and is FALSE, and the
> threshold above was the wrong one.**
> ① **`d` is a PAIRED quantity, not `a2 − bar`.** R436 records `bar = 0.4511956` and both `a2` and
> `d` per arm: **0 of 56 cells satisfy `d = a2 − bar`**, and the disagreement reaches **0.98× an
> MDE** (`coval_core_2bA`). Moving the comparator changes the pairing, so a constant shift is not a
> valid rebase **in principle**, whatever its size.
> ② **R518 pre-registered its kill at `2× MDE`** — *"if any ②-passing arm's margin over ④'s bar is
> under 2x its MDE, world B dies"*. The paragraph above compared against a generic **1.5×** floor.
> At the permissive bar `topw_k8`'s derived margin is **1.85×**, which **fires R518's own kill.**
> ⭐ **WHAT SURVIVES, and it is identified:** all **9** ②-passers are **above** the permissive bar as
> point estimates — `a2 − 0.519689` runs **+0.0431 (`topw_k8`) … +0.1156 (`oracle_k4`)**, **0 below**.
> ⚠ **WHAT DOES NOT:** their **MDEs against that bar are not on disk** — R436 computed variance paired
> against `min_ttr` only — so *margin in MDE units*, which is the entire statistic R518 used to
> separate a MEASUREMENT from a RESOLUTION LIMIT, is **NOT IDENTIFIED** here.
> **So ④'s freedom at the conjunction is CONFIRMED under the strict reading (R518) and UNVERIFIED
> under the adopted permissive one** — not refuted, and not established.
>
> ⭐⭐ **RESOLVED THE NEXT ROUND — MEASURED, NOT DERIVED (entry 1330).** The claim above that a
> measured answer *"needs a scoring run"* was **false**, and the numbers were in **R824's own
> artifact** all along: `e1.rows` carries, for all 58 arms, `perm_margin` with `perm_lo`/`perm_hi` —
> **the paired margin against the permissive bar, with a 95% CI.** Joined to R294's ② verdicts
> (39 arms, **9** ②-passers):
> **all 9 clear the permissive bar with CIs excluding zero** — narrowest `topw_k8`
> **+0.039622 [+0.025045, +0.054199]**, then `topw_k3` +0.0435, `topw_k6` +0.0444, `topw_k4` +0.0445,
> **`coval_core` +0.046789 [+0.032645, +0.060932]**, up to `oracle_k4` +0.108614. **0 of 9 excluded
> by ④.**
> **NEGATIVE CONTROL:** 28 of 58 arms sit *below* the permissive bar, so the scale is two-sided.
> **POSITIVE CONTROL:** `full_sham` at **−0.059260 [−0.0741, −0.0444]**, `perm_excluded = True`.
> ⭐ **④ is FREE at the conjunction under BOTH readings — now on measured evidence with intervals.**
> ⚠ And the earlier rebase was invalid in a **second** way nobody had checked: **R436 and R824 do not
> share an A2 scale** — of 52 arms carrying `a2` in both, **0 are identical**, mean Δ **+0.003440**,
> max **0.009722**. Two independent reasons the constant shift could not have been trusted.
>
> ⭐⭐ **AND THE READING DOES NOT MOVE THE EXTENSION (entry 1332).** ④'s standalone count swings
> **0 → 25 of 58** between readings, which is why the clause is *"not well-formed without"* naming
> one. **It does not follow that the reading changes what a core IS**, and on R360's 42-arm space it
> does not. Swept over **both defensible ③ definitions**, because they give different populations:
>
> | ③ definition | ②∧③ admits | ④ verdicts that FLIP between readings |
> |---|---:|---:|
> | R360's hand-written ③ | **5** — `coval_core`, `topw_k3/k4/k6/k8` | **0** |
> | R444's derived ③ (`clause3_as_written`) | **1** — `coval_core` | **0** |
>
> **POSITIVE CONTROL, on this same 42-arm space: 23 of 40 arms DO flip** (`coval_core_sham`,
> `full_sham`, `gen_sham`, the `random_k*` family …). The contrast is live exactly where the
> comparison runs — this is not a null from a blind instrument.
> ⭐ **The margins move a great deal and the verdicts not at all**: `coval_core` **+0.110798 →
> +0.046789**, `topw_k8` **+0.103632 → +0.039622**. **The reading choice sets ④'s BAR; it does not
> set the definition's EXTENSION.**
> ⚠ **Both populations are CENSUSES, not samples** — 5 and 1 are *every* arm ②∧③ admits here, so the
> zero is exhaustive rather than under-powered. ⚠ But the `n=1` cell rests on `coval_core`, which
> `clause3_as_written` returns as **UNKNOWN**, and 2 of the 42 arms carry no row in R824 (neither is
> in either ②∧③ set).
⚠ **And R518's artifact cannot support this on its own** — it persists `margins_in_mde` ratios and no
bar and no per-arm `d`; the numbers above were recovered from its **README**. §5 requires an artifact
to carry *"what a LATER round needs to ATTACK this"*, and this one does not.
⚠ **And note why no gate caught it:** `definition_matches_the_record.py` passes, because **both
numbers are present and both are right.** The defect is a *sentence* that a correct number stopped
supporting. Nothing in the assurance layer checks that.

⭐ **④'s zero is the argument, not an embarrassment** *(under the STRICT reading only — see above)*.
On this release ④ **costs nothing** — it
⛔ **AND THE SECOND-RELEASE HALF OF THIS ARGUMENT IS CONTRADICTED BY ITS OWN CITATION (entry 1333).**
The sentence below says *"on the second release it removes all 7 and **② removes none** (R434)"*, and
it is the **load-bearing support for ④ being a sufficiency clause** — free where the definition works,
binding where it fails. **R434's artifact says `sat2 = []` and `world = "W-EMPTY"`, and its own title
is *"on a second release the definition admits NO CORE AT ALL"*.** An empty SAT2 means **② admits 0 of
7 — ② removes all 7 there too.** So ④ is **not** distinguished from ② on that release; both are
binding, and the "binding where it fails" half does not isolate ④. R434 refuses the inference in its
own words: *"The SAT2→USEFUL relation is **UNVERIFIED**, and honestly so: with an empty SAT2 the
relation has no referent."* ⚠ The charitable reading — *② removes none that ④ has not already removed*
— is **vacuously true** when ④ removes all 7, and it reads as "② is inert there", which is the
opposite of what R434 measured. **The clause-④ sufficiency argument therefore rests on the home
release alone**, where entry 1332 measured it: ④ excludes 0 of the arms ②∧③ admits, under both
readings.

removes no arm the definition already admits — while on the second release it removes **all 7** and
② removes **none** (R434). A clause that is free where the definition works and binding where it
fails is what a sufficiency clause is for; a **non-zero** here would have meant ④ was quietly
re-litigating ②'s boundary, which R439 independently ruled out. ⚠ **①'s row is on R347's 41-arm
space, not this one**, and is left unharmonised rather than given a denominator no round recomputed.

### ① — a consequence, not a test

On this arm space clause ② **implies** clause ①. The cell *(① fails, ② passes)* is **empty**, and
empty **by derivation**: a counterexample needs `GAP < SLACK`, and the measured minimum GAP exceeds
the maximum SLACK on all 41 arms. It could not have come out otherwise.

**Do not delete it** — the implication rests on a *measured* reference gap, not on the definition's
own logic, so a release with a weaker blind reference restores its bite. **State it as a consequence
and stop presenting it as independent evidence.**

### ② — real, and it must carry a judge index

It excludes the most, and every one of the following is measured:

- It tests a **curated instrument, not blindness.** Crowd-written sets that never read the
  conversation do *no better* than clause ①'s own reference, and 2 of 5 are resolvably worse. *(R348)*
- The reference is `POOL[0:k]` — chosen by **file order** — sitting at the **93.7th percentile** of
  all 1,820 size-4 subsets, where it admits **3 members of the class the clause defines itself
  against**. *(R331)*
- The admitted set is **not stable**: two distinct sets inside **0.25 of one MDE**. *(R332)*
- The "closure level" is the **first** closed reference, not the lowest safe one — at 6 of 9 k,
  **stronger** references admit blind sets again. This replicates at a second judge, so it is a
  property of the **estimator**, not of one model. *(R355, R358)*
- ~~**It is emptied by a change of judge**: **5** arms admitted at Qwen3.5-2B-Base, **0** at
  Qwen3.5-0.8B-Base, on all 41 arms. *(R301)*~~ ⛔ **CORRECTED 2026-08-04 (R447): false as a
  statement about the JUDGE.** R301's `0` is measured at `POOL[0:4]` — the file-order draw. Swept
  over all **1,820** references judged by 0.8B, ② admits `coval_core` under **11.9%** of its own
  class and `gen` under **25.6%**, with an oracle admitted under 1820/1820 so the shares are
  measurements and not silence. ⭐ **And the ordering INVERTS**: at 2B `coval_core` clears 98.4% and
  `gen` 0.4%; at 0.8B `gen` clears more than `coval_core` does. **The judge does not merely move the
  threshold — it reorders the definition's two candidate members**, which is a stronger claim than
  the one being corrected. ⚠ Shares are comparable across judges; A2 LEVELS are not.
  **NARROWED 2026-08-04 (R448): the reordering is real but it is NOT a symmetric swap, and it has a
  measured mechanism.** Against a null built from the 1,820 references' own shifts, `gen` rises
  **+0.5319** in quantile where references starting at its rank move a median **+0.015…+0.054**
  (p ≤ 0.0055, **10 of 10** grid cells surviving BH), while `coval_core`'s **−0.3016** survives only
  at the two narrowest bands (4 of 10) **and its null is CENSORED** — it starts at quantile exactly
  1.0000, so its band can only move down and its p is an upper bound. **The mechanism is
  cross-judge criterion stability**: per-criterion sign agreement is `gen` **0.6302** vs the
  reference pool's **0.5899** (Δ **+0.0403**, MDE 0.0143, RESOLVED), while `coval_core` **0.6044** is
  *unresolved* against the same pool (Δ +0.0144, MDE 0.0147). **So `gen`'s absolute A2 FALLS
  (0.5374 → 0.4743) while its RANK rises, because the reference class falls further.** Regression to
  the mean is dead as the whole story; ties are dead as the mechanism (2B 0.045 → 0.8B 0.080, and
  dropping tied pairs changes no cell). *(R448)*
  **AND IT DOES NOT BECOME A FIFTH CLAUSE (R449).** Cross-judge criterion stability X is a **real
  axis**, measured: it varies across the 13 arms carrying both judges (permutation p = **0.0000**,
  between-arm sd 0.0251 vs null median 0.0063), it responds to a content manipulation (**5 of 5**
  arms beat their own wrong-prompt sham, pooled **+0.0417** [+0.0306,+0.0524] vs MDE 0.0152), and it
  is **not** a reparameterisation of clause ②'s score gap — paired at n=398 prompts,
  corr(ΔX, ΔA2) = **−0.0431** [−0.1424,+0.0578], so the two share **at most ~2.0%** of their
  variance. ⛔ **It is nevertheless not statable as a clause here**, and no measurement can change
  that: a stability predicate ranges over a judge **PAIR**, `n_judge_pairs = 1`, and the register
  records that no third judge exists. **A property can be real and unstatable at the same time.**
  ⚠ Measured on 398 prompts (the 13-arm intersection), not the 968 the rest of this document uses.
  *(R449)*

⭐ **THE EXTENSION OF 1 IS STRICTNESS, NOT TAUTOLOGY (R450) — §4's oldest suspicion about this
document is dead.** Every earlier round tested the clauses against arms built by *other selectors*;
none tested objects **adjacent to the released core itself**. Scoring `r` of the core's own criteria
plus `a` generic pool criteria — free, since per-criterion satisfaction is already on disk — the
share of the size-matched class beaten is **0.1661 · 0.4184 · 0.7187 · 0.9215 · 0.9868** for
`r = 0..4`, monotone across all five levels. **Variance of admission explained: by `r` 98.6%, by
`a` 1.0%.** So admission is governed almost entirely by how much of the released core survives, and
adding generic criteria is nearly free. **Dropping one criterion of four still clears 92% of the
class**, so the definition does not collapse on perturbation: **the extension of 1 is a fact about
WHICH ARMS WERE BUILT, not about the definition's strictness.** Anchored at both ends without a free
parameter — d=0 reproduces R446's committed **0.9841** through an independent code path, and the
floor matches the class's own computed self-share (**0.2198**; same-rule fixed subset 0.2563). ⚠ This
measures the definition's **extension**, never its correctness: whether a neighbour is *really* a core
needs a standard outside this definition. *(R450)*

⛔ **BUT THE NEIGHBOURHOOD IS ENTIRELY A NEIGHBOURHOOD OF ONE POINT (R451), AND R450'S READING ABOVE
IS NARROWED.** Every admitted object in R450's grid shares criteria with the released core — `r > 0`
by construction — so the question that had never been asked is whether anything **disjoint** from it
has ever been admitted. Over every disjoint object on this site at m=4: the **only** hindsight-free,
content-driven one ever built is `gen`, at **0.0038**, while an **oracle** selecting from that same
disjoint space clears **1.0000**. ⭐ **The oracle is what makes the zero a measurement rather than
silence: the space demonstrably contains admissible disjoint objects, and no generator we have finds
one.** So *"the extension of 1 is a fact about which arms were built"* is **too kind** —
prompt-specific arms **were** built and they fail. ⚠ The verdict is threshold-swept, not defended:
over t ∈ {0.50…0.90} the candidate-core verdict is `W-BALL` at **every** cell, while the
all-objects verdict flips below 0.80 on `generic` (0.7154) — which is prompt-**blind**, hence a
within-family comparison against the reference class and near-circular. ⚠ **This measures our
GENERATORS, not the category:** nothing here shows a disjoint core does not exist. *(R451)*

⚠ **AND THE ORACLE THAT MADE THAT ZERO READABLE IS ITSELF LARGELY A FIXED SUBSET (R452).** The oracle
selects, per prompt, the best of 1,820 prompt-blind subsets — but its **winners concentrate**: the
effective number of distinct winners is **57.8** of 1,820 (**3.2%**), and one single subset wins
**33.57%** of all prompts, **611×** the uniform rate. Against a synthetic pool with *no* per-prompt
criterion structure, assembled through the identical combinatorics so overlap is reproduced, the
no-structure baseline gives **185.7** effective winners — so the real oracle is **3.2× more
concentrated** than no-structure produces, and per-prompt structure would push concentration the
*other* way. ⛔ **So `per-conversation` overstates what the oracle does: its ceiling is largely a
FIXED better subset of generic criteria plus max-of-1820 inflation** (`oracle 0.6610` vs
`best fixed 0.5618`, a difference that is a **DERIVATION** — a max of 1,820 draws exceeds the best
single draw by construction). R451's control stands; its *interpretation* narrows. ⭐ **And it
sharpens the circularity already flagged for `generic`:** if a fixed prompt-blind set sits near the
top of the prompt-blind class, clause ② is a **within-family ranking** where it was meant to be a
prompt-specificity test. *(R452)*

⚠ **AND CLAUSE ② IS PARTIALLY A WITHIN-FAMILY RANKING — MEASURED, AS A BOUND (R453).** The circular
version of this test (the *best* subset's share against a class containing it) is near 1 by
construction; the non-circular version holds out. Choosing the best fixed prompt-blind subset on half
the prompts and scoring it on the other half, it reaches **0.5773** [0.3188, 0.7456] on prompts it
was never chosen on — above the class floor **0.2198** and above a destroyed-objective g=0 at
**0.1327**, but below the released core's own half-sample bar of **0.8194**. On the floor→core scale
that is **59.6%** of the way. **So ② is not purely a prompt-specificity test, and the released core
still clearly beats the best generalising prompt-blind set.** ⚠ Every number here is at n=484; the
pipeline anchor at the committed n=968 reproduces **0.9841** exactly. ⭐ **R452's concentration is
CONFIRMED, not narrowed:** under R452's own selection rule the top subset's win share goes
33.47% (train) → **33.68%** [31.29%, 36.43%] (held out). *(R453)*

⭐ **AND THAT BOUND SATURATES IN POOL BREADTH, SO IT IS NOT A POOL-SIZE ARTIFACT (R454).** Drawing the
reference class from a random `W` of the 16 pool criteria and re-running the hold-out at each breadth,
the position of the best fixed set between floor and core is **0.4518 · 0.5817 · 0.6639 · 0.6296 ·
0.6337** for `W = 8, 10, 12, 14, 16` — a rise of **+0.1298** from W=8 to W=10 and then a plateau
(sd over W=12…16 = **0.0153**). **R453's W=16 measurement is in the saturated regime: more breadth
would not move it.** ⚠ What this does NOT say is that the fraction is breadth-independent — below
W≈12 it clearly is not. The anchor reproduces R453's **0.5773** exactly through an independent path.
⛔ **And it remains a property of THIS prompt-blind family**: exactly one family on this site has
breadth ≥ 16 (`genericpool16`; `full` is the rubric, `provenance_probe` covers 4 prompts), so
`n_prompt_blind_families_with_breadth = 1` and no resampling makes a second. *(R454)*

⭐ **AND ② CAN BE STRENGTHENED — THE FIRST REPAIR IN THIS ARC RATHER THAN A NARROWING (R455).** Since
most of what ② demands is reachable without reading the prompt, the fix is to strengthen its
**baseline**: require a core to beat not a size-matched member of the prompt-blind class but **the
best prompt-blind set that GENERALISES**. Cross-fitted over 10 folds so no prompt's baseline is
chosen using it, the released core clears that stronger bar by **+0.0141**, CI
**[+0.0047, +0.0236]**, resolved at all three seeds with a seed spread of 0.0001. ⚠ **That is
1.04× its own MDE — the edge of what this design can see, so the INTERVAL is the claim and not the
point.** The controls are what make it readable: an oracle clears the same baseline by **+0.1034**
(so the design has power), a wrong-prompt sham **loses** at −0.0558, and — decisively — the
prompt-blind arm `generic` sits at **−0.0020 [−0.0086, +0.0045]**, *unresolved*, so this separates
*the core is good* from *anything beats a cross-fitted pick*. ⭐ **And an IN-FOLD baseline gives
+0.0011**: the naive design finds nothing, so cross-fitting did not inflate this effect, it revealed
one that an unfairly strong in-sample baseline was hiding. **R453's 59.6% therefore stops being an
objection to the definition** — it remains a true statement about how weak the original baseline was.
⚠ Stated against THIS prompt-blind family; exactly one with breadth exists. *(R455)*

⛔ **AND THAT RESOLUTION CLAIM NARROWS TO A BOUND — THE DATA DID NOT HAVE MORE TO GIVE (R456).** Every
A2 above uses 3 annotator draws while the release ships a median of 16 on this population (min 4, mean
16.1, max 46, **15,593** total). Recomputing the strengthened gap across the whole annotator ladder
`m = 1,2,3,5,8,16,ALL`: the gap is **positive in 7 of 7** cells but clears its own MDE in only
**6 of 7**, failing at **m=16** (gap **+0.0095**, MDE 0.0104, ratio 0.92). ⭐ **The measured exponent
is α = 0.208, not the 0.500 that √ would give** — the MDE falls just **1.19×** from m=3 to all
annotators, so **the between-prompt spread is not annotator noise and no annotator count resolves
this gap cleanly.** The honest statement is therefore a bound: the released core sits above the best
generalising prompt-blind set by **+0.0095 to +0.0191**, sign stable across every specification,
resolution not. ⭐ The oracle clears the same baseline at **8.5–11.6×** its MDE at every m, which is
what makes this a measurement rather than silence: the design can resolve a large gap throughout and
simply cannot resolve this one. *(R456)*

⭐ **AND THAT BETWEEN-PROMPT VARIANCE IS SIGNAL, NOT NOISE (R457) — SO ②'s ADVANTAGE IS NOT UNIFORM
ACROSS PROMPTS.** Splitting each prompt's annotators into two disjoint halves with the baseline held
fixed, the *value of having the right criteria on a given prompt* — `A2(core,p) − A2(sham,p)`, which
cancels both the shared baseline and the shared prompt-difficulty term — replicates at
**ρ_full = 0.8812**, CI **[+0.8460, +0.8946]**, seed sd 0.0084. ⛔ **The naive version of this test is
contaminated and its own sham control says so:** `A2(arm,p) − A2(base,p)` inherits reliability from
the baseline term that every arm shares, and on that statistic the **sham scores 0.8913 — HIGHER than
the core's 0.8355** — so it cannot distinguish *the core's advantage is prompt-structured* from
*prompt difficulty is reliable*. ⭐ **What this licenses is a per-prompt stratification with a
measured ceiling of 0.8812**, subject to a both-arms check on every covariate; ⚠ what it does NOT
license is any claim about *which* prompts, and the covariate R456 proposed — annotator agreement —
is **inadmissible**, because it raises both arms of a bounded difference and manufactures a gradient.
*(R457)*

⛔ **AND NOTHING ON THIS SITE PREDICTS WHERE THAT ADVANTAGE LIVES (R458) — SO THE DEFINITION GAINS NO
SCOPE LINE.** Cross-fitting a ridge from **17 target-free features** (core/sham/pool satisfaction
means, sds, ranges, per-response spreads and k, plus response-length mean/sd/range) onto R457's
arm-specific gap gives out-of-fold **R² = +0.0384** — **4.4%** of the 0.8812 ceiling. Per block:
core-only +0.0135, sham-only +0.0170, pool-only +0.0167, lengths-only **−0.0040**. ⭐ **The positive
control makes that a measurement rather than silence: a planted `d + noise` column is recovered at
R² = +0.9170**, 24× the observed value, and a pure-noise column does not move it. ⭐ **And the
both-arms diagnostic caught §4's trap in the act — 8 of 17 features raise BOTH arms**, with
`core_range` at **+0.4520 / +0.3676** against the two arms but only **+0.0636** against their
difference: a naive stratification on satisfaction spread would have shown a large arm gap produced
entirely by both arms rising. **So clause ②'s advantage is prompt-specific, replicable at 0.88, and
unexplained at 0.04 by everything the release yields without a second instrument** — structured, but
not by anything on this site. ⚠ Scope is that named feature set, not "observables"; a semantic
representation of the prompt is the next instrument and is deliberately outside this round. *(R458)*

⭐ **AND THAT RELIABILITY IS NOT A PARTNER ARTIFACT (R459).** R457's estimand subtracts a sham that
applies **another prompt's** criteria, and the partner is **fixed per prompt** — so an annotator
split counts partner variance as perfectly reliable while it is no property of the prompt. Tested
against a **partner-free** estimand (`generic` is a single fixed criterion set, verified in-run at
**1** distinct criterion-index tuple): `core − generic` replicates at **0.8363**
[+0.7684, +0.8474] against `core − sham`'s **0.8812** — **Δ = −0.0449**, inside the ±0.15 band, with
R457's committed value reproduced **exactly** through an independent path. ⭐ **And the component
table shows why the paired design works at all: `d_sham` (0.8812) is MORE reliable than either of its
parts (core 0.8378, sham 0.8593)** — a difference exceeding both its components is what happens when
their noise is positively correlated and cancels in the subtraction. ⚠ **This does NOT decompose
partner variance** — impossible here, since the partner is fixed per prompt — it shows the conclusion
survives without a partner at all. *(R459)*

⛔ **AND BOTH OF THOSE NUMBERS ARE OUTLIERS — R459 INHERITED THE DEFECT IT WAS BUILT TO TEST (R460).**
R459 answered an n=1-draw objection with `core − generic`, itself **one** fixed prompt-blind set.
Every such set is a row of the C(16,4) matrix, so a **census of all 1,820** is free. The reliability
of `core − F` across that whole population: min **0.8226**, p25 0.8419, median **0.8486**, p75 0.8544,
max **0.8675** — **IQR 0.0125**. ⛔ **R459's `generic` sits at 0.8114, percentile 0.000 — below every
one of the 1,820 — and R457's sham at 0.8726, above the census maximum.** The entire population lies
**between** the two numbers whose agreement R459 read as evidence, and
**corr(ρ, comparator strength) = −0.7995**: reliability rises as the comparator weakens, because a
weak comparator contributes less signal variance and the difference is dominated by the core's own
reliable variation. ⚠ **What this does NOT overturn: the per-prompt advantage is reliable — the census
MINIMUM is 0.8226, so every comparator agrees.** What it narrows is the number and its reading: the
honest quantity is the census IQR **0.8419–0.8544**, and any single-comparator figure must name its
comparator. *(R460)*

⭐ **AND THAT CLASS DEFECT DID NOT REACH THIS DOCUMENT (R461).** Since a difference is a joint
statement about the arm and its comparator, every difference-based claim here must name what it was
measured against. Rather than grep for them — **a grep is a measuring instrument with no positive
control** — the comparator is now **DECLARED per anchor and checked** by
`assurance/comparator_scope.py`, with the containment window **swept rather than chosen**:
**18** declared difference-anchors, **0 flagged** at windows 400/800/1600 and **3** at the tightest
200 (`r456_gap16`, `r456_ratio16`, `r460_iqr`) — **a window artifact, and the sweep is the only thing
that distinguishes it from a real defect.** The window mechanism is positive-controlled on a
comparator planted at a known distance (flagged below it, passing above it, at both 300 and 1200
chars), and a declared-absolute claim is never flagged. ⚠ **Declaration coverage is 27 of 343 anchors
(10.3%)** — ⛔ a SELF-REFERENTIAL count: this sentence lives inside the document the
gate checks, so it goes stale the moment an anchor is added, and it did, one commit after R461 ran; the 230 undeclared are **not passes**, and that count measures the instrument's coverage
rather than any property of this document. **The product of that round is the enforced instrument: a
future difference-anchor cannot be added without naming its comparator.** *(R461)*

⭐ **AND THE OLDEST BLOCK IS CLEAN TOO (R462) — declaration coverage now 80 of 343.** The proposed
ordering for the remaining work was *"oldest first, because old numbers have survived the most
rewrites"*; nothing measured that, and every anchor defect this campaign's value-gate has caught was
in a **newly written** anchor. Declaring the whole **R442–R454** block — the one called riskiest —
gives a flag rate of **0 of 32** at windows 400/800/1600, against the recent block's **0 of 18**;
at the tightest window 200 the flags are **all** from the recent block and **none** from the old.
**The ordering is refuted, and doing the work was the test.** ⚠ This does not establish that the
remaining **181** undeclared anchors are clean — undeclared is not a pass — and it leaves the correct
ordering **open**, since the only proposed basis has been eliminated. *(R462)*

⭐ **AND A THIRD BLOCK IS CLEAN — 71 DECLARED DIFFERENCES, 0 FLAGGED (R463); coverage 154 of 265.**
The ordering proposed to replace refuted-age was *"count, per anchor, how many clause-sections cite
its round"*: measured, `sections_citing(round)` is **min 1, max 1 over 21 rounds** — **flat by
construction**, since each round's paragraph lives in exactly one section. **Two orderings proposed,
both eliminated**, so the remaining order is **arbitrary and is stated to be arbitrary** rather than
dressed in a third story; the block declared was simply the next contiguous one. Across three
independent blocks — R430–R441 (21), R442–R454 (32), R455–R462 (18) — **0 flagged at windows
400/800/1600**, with 6 at the tightest 200 split 3/0/3 between the outer blocks. ⚠ This says nothing
about the **111** still undeclared; undeclared is not a pass. ⭐ **A separate fact the census gives:
clause ② carries 19 of the 21 round-markers and clause ③ carries 2** — 90% of this campaign's
attention went into one clause. *(R463)*

⭐ **AND CLAUSE ① IS UNEXERCISED, NOT DECORATION (R464).** The per-clause table records ① as excluding
**0 of 41** arms, and §4's remedy reads *"if nothing you have built is excluded, the clause is
untested decoration."* ⚠ **But "excludes nothing BUILT" and "excludes nothing CONSTRUCTIBLE" are
different claims, and only the second makes a clause vacuous.** Building objects designed to fail ①
from each prompt's own rubric: the adversarially **worst** rubric subset is excluded at
**−0.2779** [−0.2914, −0.2651] against an MDE of 0.0190, while the released core sits at
**+0.0797** [+0.0677, +0.0915] and is not excluded, and a **random** rubric draw — a sample from the
very process ① compares against — sits at **+0.0088** with a CI straddling zero, exactly as a
correctly-calibrated boundary requires. ⭐ **So ① is a real predicate with a real extension, and
`0 of 41` is a fact about the ARM SPACE rather than about the clause.** ⚠ What it does not establish
is that any real *generator* would produce such an object: the excluded arm was built adversarially,
on purpose, which is both the point of the test and its limit. *(R464)*

⭐ **AND ③ IS A PREDICATE OF A DIFFERENT TYPE FROM ①②④ (R465) — THE FORMULATION MIXES TWO KINDS OF
CLAUSE.** ③ is derived from *which selector built the arm*, so it is invariant under every measurable
property of the object: criteria, satisfaction scores, A2. Constructing the collision directly — a
label-**reading** selector against a label-**free** one at matched k — they emit **exactly the same
criterion set on 9 of 967** prompts where a genuine choice exists (rate **0.0097**, seed spread
0.0018), with **identical A2 to machine precision** on every collided prompt, while ③ excludes one and
admits the other. ⚠ Against a label-free/label-free baseline of **0.0062** that rate is **not a
resolved difference and does not need to be**: the estimand is **existence**, and one collision
suffices. The single prompt whose rubric admits exactly one subset collides at 1.0000 by construction
and is excluded as a **DERIVATION**. ⭐ **What this costs the formulation: ①, ② and ④ can be checked on
an object you are handed; ③ cannot** — a reader given a criterion set can verify three of four clauses
and must be given the construction history for the fourth. That is not a defect to remove but a fact
the definition must state, because four uniform-looking predicates silently promise a check one of
them cannot deliver. *(R465)*

⛔ **AND ③'s TWO INSTRUMENTS RANGE OVER DISJOINT ID SPACES (R466) — SO "`coval_core` SURVIVES ③" IS
UNVERIFIED, NOT REFUTED.** Running `clause3_as_written.partition` over every arm with a satisfaction
file gives **39 EXCLUDED, 43 ADMITTED, 19 UNKNOWN** — and **`coval_core` is UNKNOWN**: the object the
definition was written from cannot be classified by the instrument that implements ③. The document
resolves that with containment (**0.0779**), but ③ as derived forbids consuming the **rankings** and
the **annotator scores**, while containment measures copying of the rubric's **text**. Measured:
rubric-text ids **986**, ranking ids **1078**, **intersection 0** — the two instruments cannot be
joined on disk without a mapping, and none was used. **Containment is therefore not a weak proxy for
③; it is computed over a population that does not intersect the one ③ quantifies over.** The decisive
construction — a label-reading arm with zero verbatim overlap — is consequently **unrunnable**, and is
recorded as **UNVERIFIED, never OVERTURNED**. ⚠ The containment instrument itself is sound: it
reproduces its anchor (**0.0778** vs 0.0779), its cross-prompt floor is **0.0000** and a verbatim copy
scores **1.0000**. **What is defective is the join, not the clause** — and **19 arms remain UNKNOWN
under ③, the paradigm case among them, so the definition still owes a third verdict.** *(R466)*

⚠ **AND THE REASON IS NOT THE ONE R466 GAVE (R467).** R466's *"cannot be joined"* invited the far
larger reading that the two files describe **different conversations** — and an early version of R467
printed exactly that. **It is false.** Record 0 of each file is manifestly the same exchange; the
rubric file simply stores a **different wording** (*"should people stop **eat** beef"* against
*"…stop **eating** beef"*) and interleaves metadata tokens. **The files describe the SAME
conversations in DIFFERENT TEXT**, so neither an id join (intersection **0**) nor an exact-text join
(**0.0000** after the schema was corrected) bridges them, and a fuzzy join is excluded because a
threshold would decide the question rather than measure it. ⛔ **What caught the false verdict was
that the NEGATIVE control returned the same 0.0000 as the result** — *when a result equals its own
null it is silence* — and the missing control was a **cross-file** case with a known answer: the
within-file uniqueness checks passed at **1.0000** both ways and could not see a normaliser that was
merely *incomparable across files*. **R466's UNVERIFIED therefore stands, for a better reason, and
the campaign-wide claim is dead.** *(R467)*

⛔ **AND BOTH OF THOSE CONCLUSIONS WERE OVER-STATED — THE JOIN EXISTS (R468).** R466 and R467 both
joined on **conversation** text, which the rubric file stores degraded. The **criterion** texts are
short exact strings carried in *both* id spaces, and joining on them needs no threshold: **coverage
1.0000 (968 of 968), uniqueness 1.0000, 0 ambiguous.** ⭐⭐ **And it is validated on a channel it was
not built from** — built from criteria, checked on conversations: joined pairs are **0.8811** similar
against **0.2859** for random pairs, so the validation cannot be an artifact of the construction. Both
prior numbers are reproduced as anchors before anything is narrowed (id intersection **0**;
conversation-text coverage **0.0000**). ✅ **So R466's UNVERIFIED is now DECIDABLE: ③'s two instruments
can be pointed at one population, and the 19-arm UNKNOWN region can be revisited.** ⭐ **The pattern
across three rounds is the lesson: a failed join licenses "this join failed", never "no join exists"**
— the second quantifies over every possible key, and neither round enumerated one. ⚠ 18 rubric-space
records have no ranking-space partner (986 > 968) and are reported rather than explained away.
*(R468)*

⛔ **AND WITH THE JOIN IN HAND, CONTAINMENT TURNS OUT TO BE CONSTANT ON ③'s OWN PARTITION (R469) — SO
IT CANNOT IMPLEMENT ③ AT ALL.** Every selector in `select_core.py` draws from the prompt's own rubric,
the ③-excluded ones and the ③-admitted ones alike, so containment is ~1.0 for both by construction —
a **DERIVATION**, confirmed by measurement rather than asserted: **EXCLUDED 0.9744** (n=39, sd 0.1581)
against **ADMITTED 0.9767** (n=43, sd 0.1507), **separation −0.0023**. The **UNKNOWN** class sits at
**0.0002** (n=7), which is the mechanism made visible: those arms are the ones *not* built by a rubric
selector, so neither instrument can separate them and **the arms the two instruments both fail on are
the same arms**. ⭐ **This converts R466's UNVERIFIED from "not yet decided" into "NOT DECIDABLE BY
THIS INSTRUMENT", and makes the definition's third verdict PERMANENT for the 19-arm UNKNOWN region
rather than provisional.** Controls: the core reproduces **0.0778** vs its committed 0.0779, the
cross-prompt floor is **0.0000**, and `full` — every rubric criterion — returns **0.9999**, without
which a low number would be silence. ⚠ It rules out **one** instrument; another would need its own
round, and this round says so rather than generalising. *(R469)*

⛔ **AND THEREFORE THE EXTENSION IS AN INTERVAL, NOT AN INTEGER (R470).** Of the **5** arms admitted by
①∧②∧④, four — `oracle_k4`, `oracle_k4_fit1`, `greedy_k4_fit1`, `indep_k4_fit1` — are **EXCLUDED** by
③, and **`coval_core` is the sole UNKNOWN**. So the extension is **0** under unknown-as-excluded,
**1** under unknown-as-admitted, and **0 confirmed + 1 unverified** under the three-valued reading.
**The committed value of 1 corresponds to unknown-as-ADMITTED — a convention this document has never
named** — and its justification (R443's containment argument) is the instrument R469 showed to be
constant on ③'s partition. ⛔ **The choice is not innocent: the only arm it admits is the object the
definition was written from, and under the other reading the extension is EMPTY.** ⭐ **The honest
form is the interval [0, 1] with the convention named, and the three-valued reading is the one this
campaign's own proxy ledger requires**, since UNVERIFIED must never be folded into EXCLUDED or
ADMITTED — which is what has been happening. ⚠ This does not say the definition is wrong; it says its
extension has never been *measured*, only **counted under an invisible convention**. *(R470)*

⛔⛔⛔ **AND THE RELEASE'S OWN DATASET CARD DECIDES ③ — AGAINST THE OBJECT THE DEFINITION WAS WRITTEN
FROM (R475).** `data/DATASET_CARD.md`, 432 lines, **opened for the first time in round 475**, says in
its own words: *"it aims to **select up to four rubric items with the highest average ratings** that
remain compatible with each other and do not repeat the same idea"*, having *"first rewrit[ten] all
rubric items to have positive weight"*. **That is `topabs_k` / `topw_k`, and both are in `W_READERS`.
So clause ③ as derived by R444 EXCLUDES `coval_core`, and the extension is 0 under EVERY reading —
not the interval [0, 1] committed one round earlier.** *(R475)*

⭐ **AND R469 WAS RIGHT ABOUT THE INSTRUMENT AND WRONG ABOUT THE WORLD.** The released core items
carry **only `criterion`** — no `rubric_item_id`, no `scores` — so the rewrite severs the link to the
rated items and **no instrument on this site can recover the provenance**. R469's measurement was
sound. Its conclusion, *"③ is not decidable here"*, quantified over the wrong domain: **③ is a
provenance predicate, and provenance is established by a RECORD, not by a measurement.** The release
publishes the record. **Four rounds — R466, R469, R470, R471 — reasoned about ③'s undecidability
while the answer sat in an unopened file in `data/`.** *(R475)*

⭐ **AND THE OBJECT WAS MADE TO JUDGE THE CARD, NOT ONLY QUOTED FROM IT.** Matching each core item to
its nearest `coval_full` item within the same prompt and reading off that item's weight percentile:
the core sits **27.1%** of the way from chance to a pure top-4-by-`w` selector, and **21.5%** of the
way to a pure top-4-by-`|w|` one — **both LOWER BOUNDS**, because the matcher recovers the source text
at only `sim ≈ 0.49` and imperfect matching attenuates toward chance. All four controls hold: the
verbatim plant is recovered to within **0.01** of a **measured** ceiling (0.8399 vs **0.8437**; 0.8462
vs **0.8495**), a verbatim *random* plant lands at **0.492–0.502** so the control could have failed,
the cross-prompt null is **0.486–0.523**, and the file-index placebo is null. *(R475)*

⚠ **AND THE CARD'S STATED MECHANISM IS THE ONE THING THE OBJECT DOES NOT CONFIRM.** The card says the
process rewrites every item to positive weight *before* ranking, which predicts `|w|` should track the
core more closely than `w`. **It is the other way round — 27.1% on `w` against 21.5% on `|w|`.** So the
negation step exists but does not govern selection: the core tracks items annotators rated **highly**,
not items they rated **strongly**. **The card is right that ratings are consumed and wrong about which
functional of them.** *(R475)*

⭐⭐⭐ **THE ONTOLOGY SHIFT, AND IT IS THE LARGEST OF THIS CAMPAIGN. A definition of "core" whose
extension excludes CoVal-core is not a definition of CoVal-core.** Clause ③ was derived by R444 from
`corebench/select_core.py` — **this campaign's own arm-generation code** — and then applied to an
object built by a pipeline that **is not released** and that the card describes as consuming exactly
what ③ forbids. One of two things must now give: **either ③ is too strong** and should forbid only the
prompt's *rankings* (`TARGET_READERS`) while permitting its *ratings*, **or the campaign has spent 32
rounds defining an object other than the one it measures.** ⛔ **This is not a repair that can be made
by choosing the convenient branch** — the two differ in what "core" *means*, and R475 does not
adjudicate them. *(R475)*

⭐⭐ **AND THE GAP THAT LEAVES ②∧③ UNDETERMINED HAS REAL PER-PROMPT STRUCTURE (R494–R497).** Settling
②∧③ needs a better ③-admissible arm than `gen` (p32.6). ⭐⭐ **AND R822 SHOWS THAT GAP IS ALSO AN
UNNAMED-ESTIMAND GAP, NOT ONLY A POWER GAP.** `gen`'s ② margin against the prompt-blind pool moves
**−0.0049 (annotator-weighted) → −0.0071 (prompt-weighted) → −0.0077 (subgroup-weighted)** — a 57%
swing, larger than the design's own noise floor of **0.0057**, and it **straddles the exclusion
threshold**: ② excludes 29, 30 or 31 of 58 arms depending on the cell. **More data cannot settle a
question whose estimand is unnamed.** Four candidate explanations for its deficit
were tested and four died. **Repetition:** `gen` repeats phrasings up to 29× against `coval_core`'s
near-total uniqueness, but stratifying prompts by that repetition gives a gradient of **−0.0357** in
`gen` and **−0.0393** in `generic` — whose criteria are identical on every prompt and therefore cannot
repeat differentially, so the gradient is prompt difficulty. **Discriminativeness across arms:**
`corr(mean SD, A2)` = **−0.4758** over 7 arms, and dropping `topvar_k4` alone flips it to **+0.4819**
— one arm, built to be extreme on the predictor, owns the sign. **Discriminativeness paired:** at
n=968 the correlation with the deficit is **+0.0013** [−0.0640, +0.0608] while the same predictor
tracks `generic`'s score at **+0.2577**, so the control fires and the null is evidence. **Length:**
`gen` writes **9.34** words against `coval_core`'s **13.25**, and correlates with the deficit at
**+0.0319**, CI spanning zero. *(R494, R495, R496)*

⭐⭐⭐ **AND THE ADMISSIBLE SIDE IS NOT A WEAK FIELD — IT IS ONE ARM (R502).** Counted from the
criterion **text** (`core_<arm>.json`, 968 prompts each) rather than from the scores, the
③-admissible population is **1** prompt-responsive full-coverage arm (`gen`), **6** prompt-varying
but *random* draws, **2** prompt-blind fixed sets and **3** partial-coverage arms — against **14**
prompt-varying arms on the ③-**excluded** side. ⭐ **So "p32.6 of 23, with 22 at p0.0" was never a
field of weak candidates: it is one candidate and a floor**, and the 22 at p0.0 are random draws and
fixed sets behaving exactly as they should. **`UNDETERMINED` keeps its value and changes its scope —
the definition is not unresolvable; the SITE ships one ③-admissible prompt-responsive generator.**
That is a property of the release, and it names what a second site must supply, which no analysis
here can produce. ⚠ Bound: *responsive* vs merely *varying* is assigned from construction knowledge,
not measured — measuring it needs the generator, not its output. *(R502)*

⭐⭐⭐ **AND THE FIFTH CANDIDATE — THAT THERE IS NOTHING TO EXPLAIN — DIED TOO, WHICH IS THE ONE THAT
MATTERS.** Three large between-arm differences with three null within-prompt correlations invites the
conclusion that the deficit is a constant offset. It is not: mean **+0.0311**, observed sd **0.1388**
against a **measured** noise floor of **0.0353**, implied true sd **0.1342** — **3.8× the noise** — and
**test-retest reliability +0.9355** across independent held-out-annotator draws. ⛔⛔ **RETRACTED BY R499 — see below; two arms with NO functional difference score higher.** ⭐ **The floor is
supplied by the instrument itself**: A2 samples a held-out annotator per prompt, so a second seed is a
second draw of the same quantity. **`gen` does not lose uniformly — its deficit's spread is 4.3× its
own mean, it wins on some prompts and loses badly on others, reproducibly.** *(R497)*

⚠ **SO THE SEARCH IS VALIDATED, NOT EXCUSED.** There is a large, stable, per-prompt target; four
predictors are simply wrong about it. ⛔ **And the design that keeps suggesting itself — "look at the
prompts where `gen` loses most" — is selection on the outcome (Oldham 1962), proposed twice and killed
twice before running.** *(R496, R497)*

⛔⛔⛔ **AND THE WHOLE THREAD RESTED ON A STATISTIC THAT CANNOT TELL A MECHANISM FROM TWO ARBITRARY
CRITERION SETS (R499).** `random_k4_s0 − random_k4_s1` — two seeds of one random procedure, no
functional difference of any kind — returns **r = +0.9581, true sd 0.1553, 4.76× noise**, higher on
every statistic than any real pair. Against a null of three such pairs (r ∈ [+0.9532, +0.9604],
true sd ∈ [0.1525, 0.1589]), `coval_core − gen`, `gen − generic` and `gen − genericpool16` all sit at
**percentile 0.0 on both statistics**. So *"these two arms differ reliably per prompt"* is true of
**every** pair of distinct k=4 sets in this release, and R494–R497 spent four rounds explaining a
distinctness that was never in question. **The placebo used throughout — an arm against ITSELF —
removes the arm difference and therefore asks whether the instrument is noisy, never whether a
difference between two arms means anything.** *(R499)*

⭐⭐⭐ **AND THAT IS ALSO THE ANSWER TO CLAUSE ②, WHICH IS WHAT THE ROUND WAS FOR (R499).** The gap
that matters is not `coval_core − gen` but **`gen − 0.5404`**, the cross-fitted prompt-blind ceiling:
`gen` is at **0.5337**, a gap of **−0.0067**, inside the **0.0122** floor. Two worlds: the arms
**agree**, or they **differ per prompt and cancel**. The cancelling world required the real pairs to
**exceed** the no-difference null; they fall **below** it. **So prompt-awareness buys nothing
per-prompt either, and clause ② is a genuine wall for ③-admissible prompt-aware arms rather than an
artifact of aggregation.** ⚠ The further suggestion — that `gen` lands *closer* to a prompt-blind arm
than two random arms land to each other — is **directional only**: k=4 affords 3 independent
no-difference pairs, so `n_eff = 3` and the permutation floor is `p ≥ 0.25`. *(R499)*

⚠⚠ **AND THAT NULL IS A CEILING, NOT A ZERO — WORDING CORRECTED, CONCLUSION SURVIVES AND SHARPENS
(R499, re-read under §0's severity test).** I called `random_k4_s0` vs `random_k4_s1` a pair with
*"no functional difference"*. They share a **procedure** and differ in **realisation** — two
arbitrary k=4 sets, which is near the **maximum** difference two criterion sets can have, not zero.
So *"gen − generic does not EXCEED it"* was decided against a high baseline and could not easily have
come out otherwise. **That specific comparison is not severe, and World B is killed against a
ceiling rather than cleanly.**

⭐⭐⭐ **WHAT SURVIVES IS STRONGER, AND IT IS THE SENTENCE TO KEEP.** The severe comparison runs the
other way. `gen` and `generic` are **two different procedures**; `random_k4_s0/s1` are **two
realisations of one**. Two different procedures landing **closer together** (r **0.9349**, true sd
**0.1314**) than two realisations of a single random procedure (r **0.9574**, true sd **0.1557**) is
**not forced by any algebra** — it could have gone either way, and did not.

⭐ **The definitional statement, in the scope the design supports:** *whatever prompt-awareness does
to `gen`'s criteria, the per-prompt differences it produces are **no larger than those produced by
drawing criteria arbitrarily** — so at this resolution **prompt-awareness is not distinguishable
from arbitrariness**.* That is why clause ②'s admissible side is empty, and it is a claim about the
**mechanism**, not about the mean. ⚠ `n_eff = 3` for the baseline, so the **ordering** is
directional; the **non-exceedance** is what the design resolves. *(R499)*

⛔ **AND THE COMPUTE THAT WOULD SETTLE ②∧③ IS NOT THE COMPUTE I NAMED (R490).** The generator already
exists — `corebench/generate_core.py` states in its own docstring that it *"MUST NOT SEE `coval_full`"*
and *"sees the CONVERSATION and the FOUR RESPONSES only"*, i.e. rubric-blind, rating-blind and
prompt-aware — and **`gen` is its output**, the best ③-admissible arm at percentile 32.6. And the
second judge cannot adjudicate: `oracle_k4`, which reads the human target **directly**, keeps only
**0.105** of the Bayes ceiling under Qwen3.5-0.8B against **1.088** under 2B, while `topw_k4`
collapses to 0.193 — so the collapse is the judge, not the oracle. **A judge on which an arm that
reads the answer scores at a tenth cannot separate a +0.0067 gap. What would settle ②∧③ is a judge
STRONGER than 2B, and this site has none.** *(R490)*

⛔⛔⛔ **AND THE EXTENSION IS EMPTY BECAUSE ② AND ③ CONFLICT, NOT BECAUSE THE RELEASE OMITS A MEMBER
(R485).** An empty extension is unremarkable if the world merely contains no member; it is a **defect**
if the clauses cannot be jointly satisfied. Measured against R478's **cross-fitted** prompt-blind
ceiling of **0.5404** (not its in-sample max, since ② says *the best* set and a max over 1,820 is an
order statistic): **every arm that clears the ceiling is one ③ excludes.** Five of five —
`oracle_k4` **0.6282**, `greedy_k4_fit1` **0.6071**, `indep_k4_fit1` **0.5915**, `coval_core`
**0.5640**, `topw_k4` **0.5618** — reaching it by reading the prompt's rankings, its ratings, or (for
the released core) via a pipeline that does. **The best ③-admissible prompt-AWARE arm is `gen` at
0.5337, a gap of −0.0067, inside the 0.0122 floor.** *(R485)*

⭐ **AND THE NULL IS EVIDENCE RATHER THAN SILENCE, BECAUSE THE BAR IS DEMONSTRABLY REACHABLE.** The
positive control is the excluded class itself: five arms clear the ceiling, so the design can detect
clearing it, and `random_k4_s0` (0.4920) does not, so the bar is not one a random arm meets. Placebo
**0.4309** against measured chance 0.428. ⚠ And prompt-BLIND admissible arms — `generic` 0.5505,
`genericpool16` 0.5416, `promptecho` 0.4540 — are held OUT of the numerator: an arm compared against
its own class is a degenerate comparison, and folding them in would have produced a "pass" that means
nothing. *(R485)*

⭐⭐ **THE SHARPER HALF, AND IT IS ABOUT PROMPT-AWARENESS RATHER THAN ABOUT ③.** The best rating-blind
prompt-aware arm (**0.5337**) is **indistinguishable from a criterion set that never sees the prompt
at all** (`generic` **0.5505**; the cross-fitted class **0.5404**) — the difference sits inside the
floor. **Seeing the prompt, without reading what humans said about it, buys nothing measurable here.**
That is the mechanism behind the conflict: ② asks an arm to beat a class that already performs at the
level prompt-awareness alone can reach, and only the human labels ③ forbids go further. *(R485)*

⚠ **WHAT THIS DOES NOT SHOW.** That ②∧③ is unsatisfiable *in principle* — that would require
enumerating all prompt-aware rating-blind selectors, which is not a finite object. It bounds **what
has been built here**, on 968 prompts and the 2B judge; five admissible arms have no `_08b` build, so
the second judge cannot host the comparison. **A limit, named, not a result.** *(R485)*

⭐⭐ **AND THE AGGREGATION WAS NEVER A CHOICE ANYONE MADE — IT WAS `score.py:63` (R481).** Every A2 in
this campaign sums satisfaction over the selected criteria, and `/yvec/` and `/sum/` both returned
**0** in this document before this round. A sum's variance grows with k, so a k-gradient is precisely
where an aggregation artifact would hide. ⛔ **Half the sweep is void by algebra**: `mean = sum/k` with
k fixed within a prompt and `cls()` reading signs of differences, so `cls(mean) ≡ cls(sum)` — **2000/2000
on random matrices, and 0.00e+00 across 26 real arm×judge cells.** MEAN is therefore used as a
**positive control on the implementation**, not as a specification. *(R481)*

⭐⭐⭐ **AND THE NULL WAS NEARLY COUNTED WITH BLIND INSTRUMENTS IN IT.** The reversal is present under
`sum` and `median` and absent under `max`, `min` and `midrange` — which reads as 2 of 5. **But `max`
and `midrange` cannot resolve k at all**: their A2 range across the whole ladder is 0.0084/0.0059 and
0.0086/0.0077, **below the 0.0122 floor**, because `max` reports only the single best-satisfied
criterion and is structurally blind to accumulation. **A null from an instrument that cannot see the
effect is silence, not an acquittal.** Correct denominator: **2 of the 3 aggregators that can resolve
k**, with `min` the sole genuine disagreement. *(R481)*

⚠ **AND THE SYNTHETIC NULL DOES NOT RESCUE THE REVERSAL, THOUGH IT INDICTS THE LEVELS.** On
structureless iid data the spurious `corr(k, A2)` is **+0.4176** for `sum` — **the largest of any
aggregator**, against +0.0125 for `max` and +0.0036 for `midrange`. So the campaign's committed
aggregator is the most mechanically k-dependent one. ⭐ **But that term is a property of the
AGGREGATOR and is identical for both judges, so it shifts both correlations equally and cannot create
a sign difference between them.** It explains levels, never the reversal. *(R481)*

⭐ **AND THE IDENTITY CONTROL CAUGHT A DEFECT IN ANOTHER CONTROL.** The synthetic null's first version
printed `sum = +0.4176` and `mean = −0.4790` — two algebraically identical quantities disagreeing,
which is impossible, so the control was broken (one generator consumed in aggregator order, giving
each aggregator different random data). ⭐ **An algebraic identity embedded in a sweep is a tripwire
that fires on any defect in the sweep's plumbing** — shared state, ordering, caching, seeding — and it
was the only control here capable of catching a bug located inside a control. *(R481)*

⛔⛔ **AND THE JUDGE MOVES THE ORDER, NOT ONLY THE LEVEL — BUT ONLY IN ONE PLACE (R480).** ② is a
COMPARATIVE, so what matters is whether *"better than"* survives a judge swap. Over 31 arms carrying
both judges, on the 318 of 465 pairs resolved under 2B, sign survival is **0.8019** [0.7610, 0.8396]
against a split-half **same-judge** placebo of **0.9848** — a gap of **−0.1829**. ⭐ **Stratified, the
pooled number is two different facts: across-family survival is 0.9130 (253 pairs) and within-family
survival is 0.3692 (65 pairs).** Below chance is not disagreement, it is **reversal**. *(R480)*

⭐⭐ **AND THE ENTIRE REVERSAL IS ONE FAMILY, WITH A DIRECTION.** `corr(k, A2)` for the `random`
family is **+0.8570** at 2B and **−0.5026** at 0.8B — **adding criteria to an UNSELECTED set helps the
larger judge and hurts the smaller one** (sign survival 14/55). The `topw` family, which *selects*,
agrees in direction under both (−0.0211 / −0.4234, survival 10/10). **The judges agree on the ordering
of selective rules and disagree on the effect of SIZE for unselected ones.** ⛔ **This lands on the
definition's size clause**: *"more than one; 3–8 indistinguishable"* was established on 2B, and the
k-gradient for unselected sets has the opposite sign under 0.8B. **A size claim is judge-relative in a
way a family claim is not.** *(R480)*
> ⚠ **DOWNGRADED (R481): that correlation is one cell of a two-cell sweep.** With **one seed per
> budget** instead of three the same quantity is **+0.9381 / +0.0111** — the 0.8B sign flips and the
> reversal vanishes. The population is not the cause (968 prompts either way, own-pop ≡ common-pop).
> **The pairwise sign-survival statistic above stands; the directional gloss on this correlation does
> not.** A correlation over arms is a statistic whose SAMPLE is a design choice, and R480 swept the
> threshold axis while silently fixing the arm axis.

⭐ **AND THE SPLIT-HALF PLACEBO IS WHY ANY OF THIS IS READABLE.** Splitting the prompts and treating
the halves as "two judges" gives **0.9848**, so the design demonstrably resolves order and the gap is
attributable to the instrument rather than to noise. Without it, 0.80 would be uninterpretable. The
disagreement is also **concentrated in small differences** — survival rises 0.8019 → 0.9109 → 0.9522
across thresholds of 1×, 2×, 3× floor while the placebo stays ≈1.0. **At 3× floor the judges agree; at
the resolution this definition actually operates at, they do not.** *(R480)*

⚠ **AND THE STEP THIS ROUND WAS SUPPOSED TO BE WAS VOID BY ALGEBRA.** R479 proposed selecting criteria
to maximise *attainment* rather than A2; attainment is affine in A2 with slope **5.3997 > 0**, so the
two objectives have identical `argmax`. **A quantity I had just derived was immediately proposed as
something to measure** — the arithmetic trap arriving inside a `next gradient` line, which is the
sentence written last and controlled never. Cost zero: rung 1 of the attack ladder is three lines.
*(R480)*

⭐⭐⭐ **AND THE 0.54 BAND IS NOT THE TARGET'S NOISE — IT IS THE JUDGE (R479).** Four unrelated routes
converge at 0.54–0.55, which admits three explanations with opposite next moves: the criteria, the
judge, or the target's own irreducible disagreement. The maximum A2 any scorer *without sight of the
target* can reach is the **modal human ranking scored against a HELD-OUT annotator** — the Bayes point
predictor under per-pair 0/1 loss. It is **0.6132** (resolution **0.0093**, measured at four seeds).
Against the best non-oracle arm (`coval_core`, 0.5665) that leaves **+0.0467 of headroom, 3.8× the
floor.** **The band is not a ceiling.** *(R479)*

⛔ **AND THE SAME CRITERIA ATTAIN 0.738 OF THAT CEILING UNDER ONE JUDGE AND 0.193 UNDER THE OTHER.**
`topw_k4`: attainment **0.738** at Qwen3.5-2B, **0.193** at 0.8B — a gap of **0.545**, five times the
0.10 pre-registered threshold. `random_k4_s0` attains **−0.106** at 0.8B, i.e. *below chance*.
**World B: the instrument is what the band is made of, not the criteria.** This is the quantitative
form of what ② already encodes qualitatively — a core is only ever *"a core under J"* — and it says
the judge index is not a caveat but the dominant term. *(R479)*

⭐ **AND THE LEAVE-ONE-OUT DISCIPLINE IS THE WHOLE DESIGN, WORTH +0.0388.** Including the held-out
annotator in the mode that is scored against it gives **0.6520** instead of 0.6132 — and that error
runs in exactly the direction that manufactures headroom and licenses *"the criteria are the
problem"*. The leakage is **reported beside** the honest number rather than argued away. ⭐ And a free
positive control fell out: single-annotator-vs-annotator returns **0.5458** against this campaign's
independently committed human ceiling of **0.5451**, **Δ +0.0007** — a loader written this round
reproducing a number computed by other code in another round. *(R479)*

⚠ **`oracle_k4` ATTAINS 1.088, AND THAT IS NOT A DEFECT.** It was fitted on the prompt's own rankings,
so it is not a member of the class BAYES bounds; **its +0.088 excess is the fitting advantage, now
measured rather than asserted.** ⚠ **And R479's population is 1,078 prompts (≥3 rankings), not
R477/R478's 968** — so `topw_k4` reads 0.5647 here and 0.5475 there, **both correct for their own
populations**. This round rules on the ORDERING and the attainment ratio, never on a level quoted
across the two. *(R479)*

⭐⭐ **AND THE RIVAL CLASS WAS CENSUSED IN FULL — 1,820 MEMBERS, NOT THE NINE ON DISK (R478).** R477
bounded the ③-admissible class by the arms that happened to carry a `.npz`, which is the defect R477's
own retraction had just named. Evaluating **every** 4-subset of `genericpool16` (968 prompts × 16
criteria, complete on disk): min **0.5049**, median **0.5261**, max **0.5433**. `generic` sits at
**0.5377**, percentile **94.4** — a strong comparator, not a weak one. **`topw_k4` at 0.5475 is
percentile 100.0, above every member of the class.** *(R478)*

⭐ **AND THE MAXIMUM OVER 1,820 IS AN ORDER STATISTIC, SO IT WAS CROSS-FITTED.** Selecting the argmax
on half the prompts and scoring it on the other half over 20 splits gives **0.5404 ± 0.0061**, against
an in-sample max of 0.5433 — **selection inflation of just +0.0029**, so the best subset is genuinely
selectable rather than a noise peak. **`topw_k4` − cross-fitted best = +0.0071**, still inside the
**0.0122** floor. **③ stays cheap, and the margin is SMALLER than R477 reported, not larger.** *(R478)*

⚠ **AND THE PREMISE THAT SENT R478 THERE WAS FALSE.** This document's own line — `generic` at
percentile 0.000 of a 1,820-member census — is about the **replication** statistic (0.8114 against
0.8226–0.8675), **not** A2. I matched the two censuses on the phrase *"percentile of the 1,820"* when
`1820` is just C(16,4) and any subset census of this pool has it. ⭐ **A census is identified by its
STATISTIC, not by its size.** The round survived its own bad premise and tightened the estimand
anyway, which is the argument for running it. *(R478)*

⭐ **A STRUCTURAL FINDING THE SWEEP HANDED OVER FREE.** Cross-fitted best is **flat at ~0.538 from
k=2 to k=6** (0.5364 · 0.5393 · 0.5386 · 0.5381 · 0.5371) while the census median rises with k. **The
prompt-blind class has a ceiling near 0.54 that more criteria do not raise** — the best small set is
as good as the best large one, across 14,876 subsets. *(R478)*

⭐⭐⭐ **AND THE FORK IS DECIDED BY EVIDENCE, NOT BY STIPULATION (R477).** R475's fork — weaken ③ to
forbid only the prompt's *rankings*, or keep it strong and exclude CoVal-core — **is a choice of
convention, and no measurement adjudicates a convention.** What decides it is measurable: **what does
a core GAIN by reading the annotator ratings?** Against the best ③-admissible arm on disk (`generic`,
a fixed prompt-blind set, **0.5376**), `topw_k4` gains **+0.0099 [+0.0009, +0.0189]** against a
**measured** floor of **0.0122** — `effect/floor` = **0.81**, so **no count is admissible, only a
direction**. ⛔ **③ is CHEAP: it forbids nothing that a good rating-blind selector cannot match.
③ stays as written, `coval_core` stays EXCLUDED, and the extension stays 0.** *(R477)*

⚠ **AND THE FIRST ANSWER WAS THE OPPOSITE, KILLED BY ITS OWN SHAM'S SCORE.** Measured against
`topvar_k4` the gain is **+0.0695 [+0.0587, +0.0809]**, 5.7× the floor — which would have licensed
*"③ forbids the mechanism"*. **`topvar_k4` scores 0.4780, BELOW the random baseline (0.4856 · 0.4913 ·
0.4790).** It is a poison, not a placebo, and `+0.0695` is the ratings' value **plus the cost of
ranking by response variance**. ⭐ **A sham answers "is the ingredient doing the work" only when the
sham is otherwise COMPETENT; a weak sham measures the ingredient plus its own incompetence, and both
terms are positive, so the number always flatters.** The comparator must be the **best member of the
rival class**, and a class is not bounded by one arm. *(R477)*

⭐ **CONTROLS, AND CHANCE IS NOT WHERE ANYONE WOULD HAVE PUT IT.** The floor is **measured** from three
`random_k4` arms differing in nothing but the draw (0.0122 · 0.0096). `oracle_k4`, which reads the
human target directly, clears it on both judges (**+0.1184** · **+0.0365**). And the placebo — every
arm re-scored against *shuffled* rankings — lands at **0.4250–0.4293**, spread 0.0043: **A2's chance
level is 0.428, not 0.5**, because `cls()` emits {−1, 0, +1} per pair and ties are not coin flips.
The design **measured** it instead of assuming it. *(R477)*

⚠ **AND ONE JUDGE CANNOT ANSWER THE QUESTION AT ALL.** The 0.8B judge has no `_08b` build of
`generic`, `genericpool16`, `gen`, `full` or `promptecho`, so its admissible class holds **4** arms and
"the best admissible" is unbounded there. **UNVERIFIED on 0.8B — which is neither agreement nor
disagreement**, and folding it into either would be the false-acquittal direction. *(R477)*

⭐ **A SIDE FINDING THAT LANDS ON CLAUSE ②, NOT ③.** `generic` reads no ratings, no rankings, and not
even the prompt — and it scores **0.5376**, within the floor of `topw_k4`. Clause ② is precisely
*"better than the best generalising prompt-blind set"*. **Seen from this side, `topw_k4` does not
clear ②** — consistent with the committed census in which only 5 arms pass ①∧②∧④. *(R477)*
> ⛔ **RETRACTED ONE ROUND LATER (R478).** `topw_k4` scores **0.5475 — percentile 100.0** of the
> 1,820-member reference class, **above every single member**; its margin over the *cross-fitted*
> best is **+0.0071**, inside the 0.0122 floor. ② is **UNRESOLVED** for `topw_k4`, not failed.
> **Folding UNRESOLVED into FAILED is the false-retraction direction** — permanent, because nobody
> re-examines a withdrawn claim. The sentence above is kept, not edited, because the error is
> instructive: it sat in the `next gradient` line, which is written last and controlled never.

⛔⛔ **AND THE GATE THAT POLICES THIS DOCUMENT CHECKS BETWEEN A QUARTER AND TWO-THIRDS OF IT (R476).**
`definition_matches_the_record.py` reported *"302 of 302 assertions"* — its count at the time — and nothing else — **a fact
about the LIST, not about the document** — and that is how R475's substring replace corrupted a
measured `+0.1298` while the gate returned PASS. Measuring the denominator it owed: coverage is
**69.2%** of author-emphasised numbers (**117** of 169), **35.2%** of decimals (156 of 443), **34.3%**
of values carrying ≥2 decimal places (134 of 391), and **28.0%** of every number (282 of 1007). *(R476)*

⭐ **AND THE SPREAD IS THE ANSWER, NOT A DEFECT IN THE MEASUREMENT.** The denominators differ by
**5.96×**, because *"a numeric claim"* is a choice and not a property of the file. So **there is no
single coverage number to quote**, and any one of the four alone would be a specification cherry-pick.
Coverage is decided **by span, never by value** — a number counts as checked only if its own character
offsets lie inside the span an anchor captured *at that site* — because value-matching would certify
every `0.5` in the document on the strength of one anchor capturing a `0.5` elsewhere. *(R476)*

⚠ **WHAT THIS DOES NOT SAY.** It does not say the document is wrong; every anchored number still
re-derives from a committed artifact, and the four controls hold (the probe site `0.8437` at char
41653 is COVERED, R475's corrupted `+0.1298` is UNCOVERED, an absent literal extracts 0× and appears
once injected, and never-matching anchors give exactly 0). **It says a PASS certifies the anchored
numbers and never the document** — and the gate now prints that sentence itself, with its own
denominator, on every run. *(R476)*

⚠ **AND THE FIGURE IS SCOPED TO THE DOCUMENT THAT WAS MEASURED, WHICH THIS PARAGRAPH ALREADY IS NOT.**
Writing R476's result into DEFINITION.md added numeric claims to the very population R476 counted, so
the live gate now reports **69.0% / 27.7%** where the round measured **69.2% / 28.0%**. That is not
drift and neither number is wrong: **a document that states its own coverage changes its coverage by
stating it.** The round's numbers hold at commit `8b57ace` **measured with the gate's 338 anchors** — both halves of the scope, because the instrument grows too; the gate's line is the current value, and
the two are expected to differ by exactly the size of whatever was last written. *(R476)*
- **Self-normalising does not repair that.** At matched strictness the relative and absolute forms
  are indistinguishable — 9 vs 9 at 2B, 0 vs 0 at 0.8B. The judge-dependence is in the **arms'
  ordering**, which no reference can reorder. *(R359, R356, R357)*

**Therefore clause ② is stated with a judge index and the claim it licenses is *"a core under J"*,
never *"a core"*.**

⭐ **AND J CAN NOW BE NAMED (R367).** The rule: **name the judge that best tracks the human.** On the
full rubric — a fixed criterion set that is neither an admitted arm nor the clause-② reference — A2
is **0.5087 at 2B against 0.4120 at 0.8B**, paired **+0.0967 vs MDE 0.0160**.

⛔ **And that rule names the judge under which the definition is non-empty, which is the answer
already published — so it was checked against a DEFINITION-EXTERNAL channel.** On the release's
`unacceptable` ratings, which no clause of the definition reads, 2B ranks the unacceptable response
last **0.7019** of the time against 0.8B's **0.5839** (paired +0.1180 vs MDE 0.0638, on the **161**
prompts carrying such a rating). **Same judge named.** A synthetic judge built to rank it last scores
1.0000, so the channel can separate; shuffled labels score 0.59–0.63, which is where **0.8B nearly
sits**.

⚠ The external rule resolves at **1.85×** its MDE against the adjacent rule's 6×, and **two judges can
refute a rule and never establish one.** What is earned is *"not refuted, and not circular on the one
external channel available"*.

### ③ — the one unsubstitutable clause

That clause ③ excludes the four label-using arms is **forced** — it *is* "no prompt labels". The
measured part is that **nothing else can do its job**:

> Across all **45** reference levels the label-user count **never falls below 4**, while the
> published five fall to **0** at the strongest reference. At p=100 the only arms still admitted are
> the four that read the prompt's labels. *(R360)*

**Strengthening clause ② removes the arms the definition exists to admit and leaves exactly the arms
it exists to exclude.**

⛔ **AND THAT IS 2B-SPECIFIC (R361).** At Qwen3.5-0.8B-Base the label-user count over the same sweep
falls to **0** — references *do* purge them there. The rank dominance is **resolved at 2B**
(gap −4.50, exact two-sided p = **0.0159** over all C(9,4)=126 assignments) and **not resolved at
0.8B** (+2.25, p = 0.2857), so the inversion is a direction rather than a finding.

**Corrected: clause ③ is unsubstitutable at 2B; at 0.8B a strong enough reference substitutes for
it.** The *rule* still stands — it is a **provenance** requirement that applies by inspection and
needs no judge at all. That is a weaker and different argument than irreplaceability.

And its wording is load-bearing: it must say **held out from the PROMPT**, not "from the
construction". Three fitted arms pass the weaker reading, and in the quintile where two annotator
halves disagree **their entire advantage is gone**. *(R295)*

⛔ **AND AS IMPLEMENTED IT CLOSES ONLY THE RANKING CHANNEL (R363).** Clause ③ is applied everywhere
by one hand-written set — `{oracle_k4, oracle_k4_fit1, greedy_k4_fit1, indep_k4_fit1}` — duplicated
across four rounds. Audited against `corebench/select_core.py`, that set is **correct about the
rankings**: `comparisons.jsonl` is opened only for `oracle_k / indep_k / greedy_k`.

But `topw_k` — **four of the published five** — selects on `w = mean importance score` from
`conversation_rubrics.jsonl`, and the annotators who wrote those scores are, at **95.3%**, the same
people whose rankings define that prompt's target (cross-prompt sham **0.016**, ratio **58×**, over
**1,160** distinct annotators against a median panel of 16; **473 of 968** prompts have complete
overlap and **none** has zero).

⚠ **MEASURED** is the overlap — a census, with no judge anywhere in it. **DERIVED**, from that plus
this release's own finding that rubrics are authored *after* ranking, is that `topw_k` is **not
producible from the conversation alone**.

✅ **AND THE CHANNEL CARRIES NOTHING MEASURABLE (R364).** Rebuilding `topw_k4`'s weights from
annotators overlapping the evaluators in a swept fraction, the margin is **flat**: paired
`margin(d=1) − margin(d=0)` is **−0.0000 against its own MDE of 0.0096**, with three seeds
straddling zero. A **planted** person-specific channel is detected from **+0.0297** upward and not
at g=0, so the null has demonstrated power; the sham that permutes *which annotator's scores carry
which id* lands inside the MDE, so the dose was measuring identity.

⚠ **A bound, not a zero:** `topw_k4`'s margin is +0.0139, so this rules out a channel larger than
~69% of it and says nothing about a smaller one. **So clause ③'s wording was wrong and stays
corrected; the published five are not compromised at this resolution.**

⭐ **AND IT IS NOT A 2B STATEMENT (R365).** The dose is flat at **both** judges — −0.0000 vs MDE
0.0096 at 2B, **+0.0000 vs MDE 0.0107 at 0.8B** — and 0.8B's MDE is only **1.11×** 2B's, so that
design could have excluded what 2B excluded. The planted channel is detected at **both** judges and
undetected at g=0 at both, so neither null is silence. **After a change of judge emptied clause ②,
inverted an arm family's ordering, destroyed the size band's premise and cost clause ③ its
irreplaceability, this is the first claim here to come through unchanged.**

⚠ Two judges can **refute** instrument-independence and never establish it, so what is earned is
**"not refuted at a second judge"** — and at 0.8B the level itself is unresolved (−0.0126 vs 0.0145),
so it is a flat dose on a null level.

⛔ **AND THAT SURVIVAL IS CHEAPER THAN IT SOUNDS (R366).** Under **any** scaling `x → βx` a true
**zero maps to zero exactly**, while a true nonzero maps to `β·nonzero` and may fall below its MDE —
so **a null surviving a shrink is the cheapest possible survival**, and this claim is a null. My own
explanation for it — *"it is a difference, and differences are what shrink transformations
preserve"* — is **refuted**: R362's size-band steps are differences of differences too, and **1 of 3**
survive. Over the whole population of **7** claims run at both judges, neither `difference` (Fisher
**p = 1.0000**) nor `null` (**p = 0.4286**) sorts survival, on a test where a perfect split **would**
have reached **p = 0.0286**. **So nothing in this record predicts which claims survive the judge, and
the proposal to restate the definition in differences is withdrawn.**

---

## The size

**Not four.** The release ships exactly one core, of size four, and "four criteria" was a
description of that instance rather than a property of the category — the k-sweep cannot separate 3
from 8. The largest identifiable *member* core is **k ≤ 2**; the class is identifiable where the
member is not. *(R224, R228, R230)*

**State the bound the design supports: more than one, and 3–8 indistinguishable.**

⛔ **AND THAT BAND IS ALSO JUDGE-INDEXED (R362).** At 0.8B there is no band to bound: the rubric's
top-k margin against a size-matched blind reference is **negative at 6 of 7 sizes** and resolvably so
at k=12. Only the band's **exit** (8→12) resolves at both judges; both entry steps (1→2, 2→3) resolve
at 2B and not at 0.8B, and 0.8B resolves an interior step (3→4) that 2B does not.

⚠ The median margin ratio is **−0.343** against R301's fitted shrink **β = +0.401** — a *sign
inversion* at **4 of 7 sizes**, not attenuation. Two parts of the size question were **not** re-run
because they are settled: the upper bound `k_max = max{k : C(n,k) ≤ a(m)}` is **combinatorial with no
judge in it** (R224/R228), and the k-curve's *shape* across judges was already measured by R356
(ρ = +0.667, inside its forced band).

---

## ⛔ THE PIPELINE'S OWN FLOOR IS UNMEASURED AT THIS JUDGE 2026-08-04 (R415)

**5** committed re-run pairs exist at the 0.8B judge — ⚠ **same RULE, not same code: R416 hashed the
committed criterion sets and all five differ, on 91–99.6% of prompts.** Re-running the rule END TO END
— re-selecting the criteria and re-scoring them — shifts an arm's
**mean A2 by up to `0.116489`**, which is 13× the +0.009002 clause ②'s headline rests on.
⚠ This is a **rule-level** floor, not a scoring floor, and it does **not** establish that scoring is
unstable. ⭐ **FULLY RESOLVED 2026-08-04 (R419 + R420): IT WAS NEVER A FLOOR.** Scoring is deterministic
(R419, bitwise on 200 prompts) and selection is deterministic (R420, byte-identical criteria, 0
unseeded stochastic constructs), so the pipeline is deterministic **given its inputs** — and two
deterministic stages cannot produce a 91–99.6% criteria difference from the same inputs. **The
`_08b`/`_08bR` files are two different CONFIGURATIONS, not two draws, and `0.116489` is a
between-configuration difference rather than a noise floor of anything.**
⭐ **AND THE TWO CONFIGURATIONS ARE NOW NAMED (R422–R424, 2026-08-04).** The families agree with each
other at `≤ 0.03%` disjoint cells but are **~96% absent from the default judge's table** — `0.0380`
(587 of 15,448) against that table's `1.0000` (15,440 of 15,440) on a known default-emitted arm. So
`0.116489` is a difference between **`--select-npz` frozen at the default** and **the rule re-run
under a second judge**, and that second judge's table is **not committed anywhere in this repo**.
⛔ ~~Every number on this page computed from an `_08b` arm is therefore instrument-UNKNOWN.~~
**RETRACTED the same day by R426.** R424's candidate loop skipped `corebench/results` — 106 files, 4
of them full-shaped — so it never tested the emitter. `sat08_full.npz` contains both families at
`1.0000` (15,448 of 15,448) while containing `topw_k4` at `0.0369`, the exact mirror of the default
table. ⭐ **The
instrument is `Qwen3.5-0.8B-Base`, named in committed source at `R290/run.py:58`.** ⚠ Containment is
necessary, not sufficient — the artifact evidence names *the table whose values these are*, and the
model behind it is **source-attested**, not artifact-verified. *Conflating those two kinds of
evidence is what built the wall.*

⭐ **(R419): the scoring-only floor is EXACTLY ZERO.** Two runs of
identical criteria at this judge — proven identical by their committed `criteria_sha256` — are
**bitwise identical on all 200 prompts**. So the shift above is located **entirely in SELECTION**, and
**every A2 figure on this page is a fixed quantity given its criteria**, at batch 32.

**No such pair exists at the 2B judge that produced every number on this page.** So the floor here is
**not measured**, and every A2 figure in this document rests on an assumption of pipeline stability
that **failed at the only judge where it could be checked**.

⚠ The cause is not separated: a 0.1 shift is large for kernel non-determinism, so either the pipeline
is wildly unstable **or** two configurations share a filename. Both disqualify those files as
replicates, and neither branch is claimed.

⚠ This does not retract any number. It scopes them: they are single draws whose draw-to-draw spread
is unknown at this judge, and §1's *"noise floor: measured, not assumed"* is unmet for the first time
explicitly rather than by omission.

## ⛔ READ LITERALLY, CLAUSE ② ADMITS ALL FIVE — INSIDE THEIR OWN NOISE 2026-08-04 (R408)

The clause says **scores better than**. The code says `e > 0 AND |e| >= ZEFF*se` — *significantly*
better. Run both at the per-k maximum blind set:

| label-free admitted | |
|---|---|
| **STRICT** (`e>0` and `\|e\| >= ZEFF*se`) | **0** |
| **LITERAL** (`e>0`) | **5** — `coval_core`, `topw_k3/4/6/8` |

`coval_core` scores **`+0.009002`** against `se = 0.003703` — **0.87 of its own significance bar.**
The other four label-free arms reach 0.38–0.81. The four **label-reading** arms reach **3.4×–6.7×**.

**So clause ② at the universal reference IS satisfiable without label access, under the definition's
own wording — and every arm that satisfies it does so by a margin it cannot distinguish from zero.**
The honest statement is not that a core was found; it is that **the definition as written has no error
control**, and the order-of-magnitude gap between the label-free and label-reading arms is exactly
what the significance term was separating.

⚠ One release. An unguarded positive mean is the quantity least likely to survive a second.

## ⛔ AT THE MAXIMUM BLIND SET ONLY THE LABEL-READERS SURVIVE 2026-08-04 (R407)

The universal reading is answerable from a **single cell**, which needs no strictness ordering — only
that the cell's reference be the maximum, and `ref_at(k, 100)` returns `order[-1]`, the highest-scoring
prompt-blind set of that arm's own size.

**At that reference the admitted set is `{greedy_k4_fit1, indep_k4_fit1, oracle_k4, oracle_k4_fit1}` —
all four of which read the prompt's own rankings. Label-free admitted: 0.**

Per arm, the highest grid point still admitting it: `topw_k8` 95.0 · `topw_k3` 95.5 · `topw_k4` 98.0 ·
**`coval_core` 99.5** · `topw_k6` 99.5 · the four label-readers 100.0. **The released core clears the
99.5th-percentile blind set and not the maximum.**

⛔ **And this answers a test the sentence does not contain.** The code's `admits` is
`e > 0 AND |e| >= ZEFF*se` — *significantly* better — while the definition says **scores better than**.
The coded test is STRICTER, in the direction that flatters. **The literal `e > 0` reading has never
been run.** That is the fourth under-specification in clause ②, after the missing member, held-out vs
in-sample, and the percentile called *every*.

## ⛔ THE UNIVERSAL READING HAS NEVER BEEN RUN 2026-08-04 (R406)

Clause ② names a class and no member, and the campaign's answer has been R327's three readings, of
which **A** was labelled *"better than EVERY prompt-blind set of that size"* — the plain-English one.

**It was instantiated at `0.5546019830`, the best HELD-OUT of 1,820. The MAXIMUM over the same 1,820
is `0.5574753088`.** The gap is **`+0.0028733259`**, and the reference brackets **below the committed
p99**: between **1% and 10%** of the blind subsets beat the bar the word *every* was tested against.
*(A bracket, not a count — R331 committed seven order statistics, not 1,820 scores.)*

> ⭐ **VERIFIED STILL LIVE, 2026-08-06 (entry 1381).** Checked against the whole committed record: the
> **maximum is known** (`0.5574753088`) but **no round has instantiated clause ② against it**. R847
> enlarged clause ④'s family; R851 measured ②'s extension against `genericpool16`; neither is the
> universal reading. ⭐ **Knowing the maximum is not running the reading**, and the sentence below is
> accurate as written. **Marked verified rather than left ambiguous** — an unchecked forward-looking
> claim and a checked-and-live one are indistinguishable to a reader, which is the whole defect
> entry 1380 found.
>
> ⭐⭐⭐ **AND IT IS NOW RUN — from committed artifacts, no new scoring (entry 1382).** R331's
> `blind_dist` carries the whole order-statistic set of the 1,820 prompt-blind subsets:
>
> | | |
> |---|---:|
> | p90 | 0.5490166733 |
> | **p99** — the bar the word *"every"* was tested against | **0.5546396620** |
> | **max** — the bar *"every"* actually means | **0.5574753088** |
> | **`coval_core`** | **0.5664774812** |
> | **margin over the MAXIMUM** | **+0.0090021724** |
>
> ⭐ **So the universal reading is SATISFIED on the point estimate: `coval_core` clears not the p99
> but the maximum of all 1,820.** ⚠ **Raising a bar can only remove arms — that direction is a
> DERIVATION** — and what was open was whether the released core itself survived the raise. **It does.**
>
> ⚠⚠ **BUT THE RESOLUTION IS UNMEASURED, AND THAT IS THE HONEST REMAINDER.** R331's three
> `clearing_sets` each clear their reference by a gap barely over its own MDE — **0.006191/0.005936,
> 0.005628/0.005508, 0.006793/0.006631, ratios ≈ 1.02–1.04** — i.e. **at the resolution limit.**
> Against those MDEs, `coval_core`'s +0.0090 is **1.36×–1.63×**, which straddles this project's own
> **1.5× admissibility bar**. ⛔ **And no round has computed an MDE for THIS comparison** —
> core-versus-max. **Borrowing the subsets' MDEs is an approximation and is labelled as one.**
>
> ⭐ **Status: the universal reading is RUN and PASSED on the point estimate; its resolution is
> UNVERIFIED.** That is a strictly better position than *"has never been run"*, and it names exactly
> one thing still owed: **the MDE of `coval_core` against the blind maximum.**
>
> ⭐⭐⭐ **AND THE RESOLUTION IS NOW BOUNDED — the wall was not a wall (entry 1383).** R331 does **not**
> commit the argmax's membership (all three `clearing_sets` return `IS-ARGMAX = False`). **But the
> highest subset that DOES carry membership, `[0, 3, 9, 13]` at `0.5572285602`, sits only
> `0.0002467487` below the true max.** So:
>
> | | |
> |---|---:|
> | `coval_core` − nearest membership-carrying subset | **+0.0092489210** |
> | **`coval_core` − the true blind maximum** | **+0.0090021724** |
> | the two differ by | **0.0002467487** |
> | that subset's own committed MDE | **0.0066309665** |
> | **ratio `margin / MDE`** | **1.358** |
>
> ⭐ **The margin is pinned to ±0.00025 from committed artifacts, with no re-run of the 1,820-subset
> sweep.** ⚠ **And entry 1382's "straddles the 1.5× bar" is sharpened to a number: 1.358 — BELOW it.**
>
> ⭐⭐ **So the universal reading PASSES on the point estimate and FAILS this project's own 1.5×
> admissibility bar on the best available resolution proxy.** ⚠ **That MDE is the subset's own gap
> statistic, not the MDE of core-versus-max** — the right floor still needs the argmax's membership,
> which is **not committed** and requires re-running the sweep. **Labelled as a proxy, not quoted as
> the answer.**
>
> ⭐⭐⭐ **AND THE RE-RUN NEEDS NOTHING THAT WAS LOST (entry 1384).** R331 commits `pool = 16` — the
> pool **SIZE**, an integer — and `n_blind = 1820`. **C(16,4) = 1820 exactly**, and the identity is
> unique to 16: **C(15,4) = 1365, C(17,4) = 2380.** The clearing subsets index **0..14**, consistent
> with a 16-member pool.
>
> ⭐ **So the 1,820 "blind subsets" are the COMPLETE ENUMERATION of all 4-subsets of the 16-criterion
> pool — not a sample.** No seed, no draw, nothing to have been lost. **The argmax is exactly
> recoverable by re-scoring, and the exact MDE of core-versus-max is a scoring job with no missing
> information.**
>
> ⚠ **The wall was named twice and shrank twice**: 1382 called it *"requires re-running the sweep"*,
> 1383 bounded the margin to **±0.00025** without one, and this shows the re-run itself is
> unobstructed. **§4's `a wall never checked` — fired twice on the same wall.**
>
> ## ⭐⭐⭐ AND R860 CLOSED IT — the exact MDE, and the proxy was optimistic by 56%
>
> *(entry 1385. Both kill checks reproduce EXACTLY: blind max `0.55747530882624` and `coval_core`
> `0.5664774811929549`, |Δ| = 0.000e+00 — the construction reproduces the two numbers the round is
> about before computing anything new.)*
>
> ⭐ **ARGMAX subset recovered: `[0, 3, 9, 14]`** — membership never previously committed anywhere.
>
> | | |
> |---|---:|
> | margin `coval_core` − argmax | **+0.0090021724** |
> | **95% CI** | **[+0.0017734642, +0.0163000494]** — **excludes zero** |
> | SE | 0.0036914813 |
> | **EXACT MDE** | **0.0103435305** |
> | **margin / MDE** | **0.870** |
>
> ⛔⛔ **Entry 1383's proxy gave 1.358. The true ratio is 0.870.** The neighbouring subset's MDE
> (`0.0066309665`) **understated the real one by 36%**, moving the ratio **across 1.0** and toward the
> 1.5 bar. **1383 said a proxy must not be quoted near a threshold; this measures exactly what that
> costs.**
>
> ⭐⭐ **THE FINAL STATEMENT OF THE UNIVERSAL READING, and it holds two things at once:**
> **the margin is RESOLVABLY POSITIVE** — the CI excludes zero, so `coval_core` does clear the maximum
> of all 1,820 prompt-blind quadruples — **and it is NOT ADMISSIBLE AS A MAGNITUDE**, at **0.870× the
> design's own MDE**, below this project's **1.5×** floor. **Sign established; size not.**
>
> ⚠ **Winner's-curse note, stated rather than corrected:** the max over 1,820 is an extreme order
> statistic and is biased *up* as an estimate of a typical blind quadruple. **That makes it a
> CONSERVATIVE bar for the core** — the direction the universal reading wants — and it is not quoted
> as an estimate of anything else.

> ⛔⛔ **AND THE PHRASE "SELECTION COMPONENT" ATTACHED TO THIS NUMBER IS WRONG — R861, measured,
> D8.** For three entries `1.56 = 0.0103435 / 0.0066310` was carried forward as *the factor by which
> a fixed argmax understates an MDE*. **It is nothing of the kind, and this artifact says so in its
> own field:** `results/exact_mde.json` records `replaces_proxy = {entry: 1383, proxy_mde:
> 0.0066309665}`. **1.56 is the ratio between the RIGHT subset's MDE and a DIFFERENT subset's** — a
> borrowed-denominator correction, which is what the round was actually for. The selection reading
> was my gloss, applied afterwards, and it survived because the number it produced was plausible.
>
> ⭐ **R861 measured the real thing for the first time, and the sign is REVERSED: 0.966.**
> Re-selecting `best_rule` INSIDE each bootstrap resample rather than once outside gives an MDE
> **3.4% SMALLER**, consistently across four arms (0.965–0.966) at a seed spread of ~5e-5.
> **So the fixed-argmax MDE is CONSERVATIVE, and every margin computed against it is UNDERSTATED:
> the tightest published cell moves 1.84× → 1.91×, further ABOVE the 1.5 floor, not below it.**
>
> ⛔ **The mechanism, and why I got the direction wrong while calling it forced.** A max has TWO
> consequences and I derived one and assumed the other. The LEVEL rises — `max_k mean_b(R_k) >=
> mean_b(R_star)` — and that IS forced, confirmed at **100.0%** of 4,000 resamples. The VARIANCE
> does not follow: when the rank-1 rule dips on a resample **a different rule wins instead**, so the
> max **clips the downside** and is LESS variable (bar sd **0.004968 → 0.004606**, ratio 0.927).
> Here rank1 `min_ttr` 0.4560 and rank2 `max_len_chars` 0.4515 differ by **0.0045 against a bar sd
> of 0.0050** — the top rules are tied relative to bootstrap noise, which is exactly the regime
> where switching is frequent (**21.8%**, 4 distinct winners) and clipping dominates.
>
> ⚠ **SCOPE, stated because it is the same trap one level up:** 0.966 is the **30-rule** family.
> R860's own MDE carries the identical fixed-argmax omission over **1,820** subsets, and whether the
> sign holds at that width is **UNMEASURED**. It is not transferred.
>
> ⭐ **What this row is really a record of:** the correction ran three deep — a borrowed MDE (1383),
> then a borrowed factor (1386), then a corrected magnitude that accepted the wrong label (1387) —
> and each was caught by reading the source instead of carrying the number forward. **The last one
> was caught by the measurement contradicting my own derivation**, which is the only reason a
> mislabelling that had been quoted three times was ever examined.

> ⭐⭐ **AND THE SIGN SURVIVES THE 60× WIDER FAMILY, MONOTONICALLY — R862, measured, D8.** R861
> refused to transfer its 0.966 to R860's 1,820-subset family. R862 measured it there instead, as a
> **dose-response in family width** rather than one cell:
>
> | w | ratio `MDE_sel/MDE_fix` | switch % | distinct winners |
> |---:|---:|---:|---:|
> | **1** | **1.000000** (placebo, exact) | 0.0% | 1.0 |
> | 30 | 0.9901 | 12.4% | 5.7 |
> | 100 | 0.9729 | 44.5% | 11.1 |
> | 300 | 0.9698 | 60.2% | 19.5 |
> | 1000 | 0.9631 | 60.7% | 26.7 |
> | **1820** (complete enumeration) | **0.9564** | 69.3% | 36.7 |
>
> ⭐ **Monotone decreasing across all six widths, no reversal**, trend −0.0337 at roughly 10× its
> own between-cell SE. **WORLD A: clipping STRENGTHENS with width.** 4-subsets of a 16-pool overlap
> heavily, so a wider family is a max over more and *more correlated* variables, and extreme-value
> concentration truncates the lower tail harder.
>
> ⛔ **R861's closing sentence guessed the opposite** — *"clipping should weaken as the family
> widens and the winners stop being near-tied."* **Refuted.** That is the second directional guess
> in two rounds the measurement reversed, and both were catchable **only because they were written
> down**. R862 therefore pre-registered no direction at all and stated both mechanisms as a fork.
>
> ⚠ **Width is not the only variable, and the two rounds must not be merged.** At the SAME width
> w=30 the two families give **0.966** (R861, criterion-free rules) and **0.9901** (R862, blind
> 4-subsets). Different composition, different correlation structure, different clipping. **The
> numbers sit side by side; neither stands for the other.**
>
> ⭐ **What this does to the object.** R860's published `margin/MDE = 0.870` for the universal
> reading of clause ② becomes **0.910** once the argmax is re-selected inside the resample.
> **It is still BELOW this project's 1.5× admissibility floor** — it would need a ratio ≤ **0.5800**
> to clear, and the measured ratio is 0.9564. ⭐ **So the correction is real, it moves the number in
> the flattering direction, and it changes no verdict: the universal reading of clause ② remains
> unresolved at this design's resolution.**
>
> ⭐ **The kill checks are what make this readable**: R331's blind max, `coval_core`, **and R860's
> own committed MDE `0.010343530538451993`** all reproduced at **|Δ| = 0.000e+00**, the last by
> replaying R860's seed *and its draw order* — a comparison against the number on disk rather than
> against a fresh re-derivation of it.

> ⭐⭐⭐ **AND THE THRESHOLD ITSELF WAS NEVER CALIBRATED FOR THIS COMPARISON — R863/R864, D8.**
> Three rounds corrected this comparison's DENOMINATOR while treating **1.5 as fixed**. It is not
> fixed; it was adopted for **paired arm-vs-arm** designs, and here the comparator is an **order
> statistic** — the max over C(16,4) = 1,820 blind subsets.
>
> ⛔ **R863's first attempt at calibrating it FAILED, and its own derivation is what proved so.**
> A leave-one-out null (each subset plays the arm against the max of the other 1,819) is degenerate:
> under exchangeability the expected number of positive margins is `M/(M+1) ≈ 1`, and **exactly 1 of
> 1820 was observed**. A family member cannot beat the max of its own family except by being it.
> Its `p95 = −1.0113` and `FP = 0.0000%` were **forced by arithmetic**, and its `WORLD A` verdict was
> withdrawn before commit. ⚠ The round's SCOPE block had already named the correlation and called it
> *"conservative in a specific direction"* — **too mild by a category: the defect was degeneracy.
> Naming a confound is not controlling it.**
>
> ⭐ **R864 ran three nulls that share neither defect, 20 seeds each — and they converge.**
>
> | null | mean | sd | p95 | max | ≥1.5 | obs percentile |
> |---|---:|---:|---:|---:|---:|---:|
> | N1 pair shuffle | −0.3380 | 0.2592 | +0.0269 | +0.0567 | 0.0% | 100.0% |
> | N2 cross-prompt | −0.3030 | 0.3454 | +0.2656 | +0.3809 | 0.0% | 100.0% |
> | N3 uniform | −0.4398 | 0.2982 | −0.0021 | +0.0102 | 0.0% | 100.0% |
>
> ⭐ **Null means span only 0.1368 — far less than the observed 0.8683 — and the observed value is
> above ALL 60 draws.** Three different destructions of the target agree; §2.5's strongest available
> reading, applied to nulls rather than designs.
> ⚠ **Resolution floor, stated because it bounds the claim:** 20 seeds give `p ≥ 1/21` per null and
> `p ≥ 1/61 ≈ 0.016` pooled. **So this is `p ≤ 0.017`, NOT `p < 0.001`** — the design cannot say more.
>
> ⭐⭐ **A sub-finding that closes an older worry.** R852/R853 established the pair shuffle is NOT a
> pure null for the clause-② extension COUNT: it preserves marginal verdict mix and left ~14 arms
> clearing ②. **On `margin/MDE` against the max it does not:** N1's maximum over 20 seeds is
> **+0.0567**, nowhere near +0.8683. **The format explanation is excluded for THIS statistic** — and
> it had to be measured, because the same word "null" covered two different instruments.
>
> ⛔⛔ **WHAT THIS DOES AND DOES NOT LICENSE — and the printed verdict overreached on one clause.**
> The run printed *"the floor is OVER-STRICT … coval_core's failure is a property of the BAR."*
> The first half is measured: an empirically calibrated 5%-false-positive threshold on this statistic
> would be about **+0.27**, and 1.5 is **5.6× stricter**. The second half is too strong, and is
> **not adopted**. What stands is narrower and sharper:
>
> ⭐ **TWO ADMISSIBILITY CRITERIA NOW EXIST AND THEY DISAGREE.**
> ① `margin/MDE ≥ 1.5` → **FAILS**, at 0.910 after R862's argmax correction.
> ② outside a 3-null, 60-draw empirical null → **PASSES**, at `p ≤ 0.017`.
> **The disagreement is the finding. It is reported as two numbers and is NOT resolved by adopting
> the criterion that happens to pass** — a threshold chosen after seeing the result is a narrative,
> and swapping bars mid-audit is the precise move this whole thread has been catching. The 1.5 floor
> stays; what changes is that **failing it is now known to mean "below 1.5× this design's MDE", and
> NOT "indistinguishable from having no advantage".** Those were being read as the same sentence.
>
> ⭐ **The design's own resolution, measured rather than argued:** a planted advantage of
> **g = 0.01** — about one A2 point in a hundred — is the smallest dose that clears 1.5
> (0.8683 → 1.3505 → **1.8327** → 2.7972 → 4.7262, monotone, not clearing at g=0). `coval_core`'s
> real margin is **under half of it**.

**So the universal reading of clause ② has never been run**, and the disagreement about whether this
definition admits its own instance is exactly that `0.0029`: `coval_core` clears a p99 bar and does
not clear the maximum.

⚠ This does not retract R327 — its divergence finding stands and is strengthened. What is corrected is
the **name of one rung**. ⚠ And no control could have caught it from inside R327, whose controls all
concerned the **ordering** of its readings: an ordering can be perfectly correct while every rung is
mislabelled.

## ⛔ CONJUNCT DECOMPOSITION 2026-08-04 (R404) — clause ③ is not one clause, and its third part is not implemented

Clause ③'s exclusion is published as one number, `4 of 42`, attributed to the clause as a whole.
Decomposed against `corebench/select_core.py`'s rule dispatch — **not against the arm names** — the
three conjuncts do wildly different amounts of work:

| conjunct | excludes on its own | **beyond ③a** |
|---|---:|---:|
| **③a** reads the prompt's own rankings | 4 | — |
| **③b** fitted on a **half** of them | 3 | **0** |
| **③c** weights from an annotator-written **rubric** | 13 | **13** |

**③b excludes nothing whatsoever.** Every `_fit1` arm already reads the rankings, so ③a has removed it
first. And enforcing ③c **as written** collapses the admitted set from **5 to 1 — `coval_core` alone**,
the object this definition was written from.

**So the definition sits between two failures.** *As implemented*, ③c does no work and R363's
`W_CHANNEL_OPEN` stands — arms are admitted that the text forbids. *As written*, it admits only its own
instance. **Neither is a definition of a category.**

⚠ The count is a **lower bound**: a label route the rule dispatch does not reveal would mean more
exclusions, not fewer. ⚠ And whether ③c *should* be enforced is an act of definition, not a
measurement, and is not decided here.

## ⛔ STATABILITY 2026-08-04 (R403) — three of six clause-parts cannot be SAID off this release

Applied to the second corpus R398 found, the clauses split. **Not into true and false — into sayable
and unsayable**, which is a third value and was never available while there was one object.

| clause-part | needs | corpus two |
|---|---|---|
| **①** vs a draw of the prompt's **own rubric** | a per-prompt rubric | **NOT-STATABLE** |
| **③b** …not from any **HALF** of the annotators | ≥2 annotators per prompt | **NOT-STATABLE** — measured: **max 1 rater**, 0 of 27,172 interactions have 2 |
| **③c** …nor via a **rubric those annotators wrote** | a per-prompt rubric | **NOT-STATABLE** |
| **②** vs a prompt-blind size-matched set | responses + human target + pool | **STATABLE** |
| **③a** no information from the prompt's own labels | per-prompt human labels | **STATABLE** |
| **size** >1; 3–8 indistinguishable | a judge + a k sweep | **STATABLE** |

**3 of 6 clause-parts are NOT-STATABLE off this release.**

**Clause ① is now doubly hollow.** It was already `DERIVED` vacuous here — the region where it could
bind is empty by arithmetic. It is now also **unsayable elsewhere**. A clause that excludes nothing
where it was born and cannot be stated off that object is a description of a **schema**, not of cores.

⚠ **No clause is restated here.** Rewriting one so it survives on a new corpus is an act of
definition, not a measurement, and doing it in the same breath as the diagnosis is how a definition
gets tuned to whatever object is in front of it.

**The transportable residue: *label-free, and better than prompt-blind*** — clauses ③a and ②, which is
also the pair that carries the whole measured boundary.

## ⛔ ON THE SECOND RELEASE THE DEFINITION ADMITS **NO CORE AT ALL** 2026-08-04 (R434)

R433 showed clause ②'s subject loses to a length heuristic. R434 asked the next question of all
**7** criterion arms scored on that release — prompt-specific, prompt-blind, three randomly
reassigned, evaluatively vacuous, and the wrong-conversation sham — on one shared population of
**7,342 interactions over 2,200 conversations**:

> **Clause ② admits 0 of 7. And 0 of 7 beat the length rule.**
> **7 of 7 are statistically indistinguishable from the blind reference** — including the
> prompt-specific core — and **7 of 7 are resolvedly worse** than a rule that reads neither the
> conversation nor any criteria (**0.5135**, against a best arm of **0.4590**).

⭐ **The emptiness is a measurement, not silence.** A synthetic oracle run through the *same* two
membership tests lands in both by a wide margin: **+0.5503 against the blind reference (MDE 0.0158)
and +0.4865 against the length rule (MDE 0.0169)**. Both tests can return TRUE; neither did.

⚠ **What this is not.** Evidence that no core exists. Seven arms is a census of what this campaign
built, not a sample of criterion-space, and R432's oracle over five of them reaches 0.7220.

**And the structural point needed no measurement at all.** ③ is a *provenance* restriction, ② a
*comparative* test against another criterion **set**, the size clause a *bound*. **Every clause
compares a core to other criteria; none requires it to beat anything outside its own family.** A
sufficiency clause would have to be stated against a **non-criterion reference** — a different
*kind* of clause from anything this definition contains. ⚠ And *"add a clause excluding the length
rule"* is a **category error**: the definition's domain is "a set of evaluation criteria", the
length rule is not one, and it was never admissible.
→ [`R434`](A24_what_the_definition_costs/R434_does_the_definition_have_a_utility_floor)

---

## ⭐ A SUFFICIENCY CLAUSE IS STATABLE — the bar saturates after **6** rules 2026-08-04 (R435)

R434 named the missing piece: a clause stated against a **non-criterion reference**. Two things had
to be checked before one could be written, and the first refuted a sentence of my own.

**① There are four non-criterion references, not one.** R427's `baselines_prejudge`
(`computed_before_arms: true`) holds **chance 0.4194 · first 0.4375 · longest 0.5096 · shortest
0.3362**. So the clause cannot be *"better than the longest-reply rule"* — that **names the
instance**, the failure this document's own ledger row is about. It must quantify over a **class**.

**② A maximum over a class climbs as the class grows — so does the bar mean anything?** Over a
family of **30** judge-free rules (14 response-set features × {max, min}, plus first/last), the
maximum **saturates at m\* = 6**: `BAR(|F|) − BAR(6) = +0.0232`, inside the **0.0234** that the
conversation bootstrap says one accuracy can resolve. Adding the other 24 rules moves the bar by
less than the data can see. **The bar is not an artifact of how hard anyone looked.** Lift over a
signal-free family of the same size is **+0.0715**, ~3× the data floor.

**So the clause is statable, and here it is as a predicate:**

> **④** …and scores better, under that same judge J, than **every rule computable from the response
> set alone**.

| the remedy's two questions | answer |
|---|---|
| an admissible object it **EXCLUDES** | **all 7 arms on the second release** (R434), including the published prompt-blind `generic`. Not vacuous. |
| a useful object it **ADMITS** | an oracle arm, **+0.4865** over the length rule (R434). Not impossible. |

⭐ **AND R436 MEASURED IT AT HOME. THE TWO RELEASES SPLIT.** Scoring the same 30-rule family on the
home release's own statistic — **A2**, agreement on the 6 pairwise comparisons, computed through the
same `cls` the arms use — the bar is **`min_ttr` at 0.4512** (*not* the length rule). Against it:

| release | do the definition's arms beat every criterion-free rule? |
|---|---|
| **home**, at the named judge J | **yes** — `oracle_k4` sits **+0.1824** above the bar (MDE **0.0211**), and **no 2B arm is resolvedly below it** |
| **second** (R434) | **no — 0 of 7**, all seven resolvedly worse |

**④ excludes 22 of 93 arms overall but 0 of 56 at the judge the definition names** — every exclusion
is an `_08b` variant, where R301 already measured clause ② admitting nothing. **So ④ is not redundant
in general; it is redundant *where the definition already works*** — silent when things are fine,
binding when they are not, which is what a sufficiency clause should look like. On this evidence it
earns adoption, and its value is stated precisely: **it would have caught the second release before
anything was generated.**

⚠ Two defects found on the way, both in this round's own instrument: the kill first tested
*"excludes some"* when the remedy's word is **admissible** — 22 of 93 would have passed while
excluding nothing the definition admits; and the round was **not reproducible** (`hash(str)` is
randomised per process, giving 25 then 22) until the seed was made stable. Two runs are now
byte-identical.
⭐ **AND R437 FOUND THE REASON TO KEEP ④ THAT IS STRONGER THAN "IT WOULD HAVE CAUGHT ONE RELEASE".
THE TWO BARS INVERT.** Clause ② and candidate ④ are two bars on the same accuracy axis, and their
order **flips between releases**:

| release | statistic (chance) | BAR2 — ②'s reference | BAR4 — best criterion-free rule | GAP = BAR4 − BAR2 | binds |
|---|---|---|---|---|---|
| **home** | A2 over 6 pairs (0.5000) | `random_k4_s0` **0.4945** | `min_ttr` **0.4512** | **-0.0416** vs MDE 0.0237 · RESOLVED | **②** |
| **second** | top-1 (0.4194) | `generic` **0.4497** | `length` **0.5135** | **+0.0637** vs MDE 0.0231 · RESOLVED | **④** |

**Neither clause dominates.** A definition carrying both carries a **max over two bars**, not two
independent tests, and which one does the work is a property of the release: **④ binds exactly where
② goes slack**, and R434 measured ② admitting nothing on the second release.

⚠ **SIGN ONLY.** The two GAPs are on different statistics with different chance rates and **must not
be compared in magnitude**. ⚠ And at home **both bars sit below chance** (A2's base rate is 0.5,
while the real arms reach 0.51–0.64) — which is *why* ② binds there: a reference nearer chance is a
**higher** bar than a systematically wrong rule. ⚠ What is NOT established: that the max of the two
bars is the *right* bar, or that no third regime exists where both go slack.
✅ **AND R438 ATTACKED THAT ONTOLOGY WHERE IT WAS MOST LIKELY TO BREAK, AND IT HELD.** A structural
claim resting on n=2 releases is attacked most cheaply from *inside* one: if the GAP's sign flips
across strata of a single release, "release" is not the variable. Splitting the second release by
n_responses — the one axis that exists, since **home has 4 responses by construction** and the two
releases share no stratifier:

| stratum | interactions | chance | BAR2 | BAR4 | GAP | MDE | |
|---|---|---|---|---|---|---|---|
| n=2 | 5,204 | 0.5000 | 0.5081 | 0.5600 | **+0.0519** | 0.0283 | RESOLVED |
| n=3 | 454 | 0.3333 | 0.4053 | 0.4449 | +0.0396 | 0.0948 | — |
| n=4 | 1,684 | 0.2500 | 0.2815 | 0.3884 | **+0.1069** | 0.0490 | RESOLVED |

**2 of 3 resolve, both positive** — the sign holds across strata where **chance itself moves from
0.2500 to 0.5000**, so both bars had every opportunity to cross and did not. ⭐ The GAP also **grows
with n**: `generic` decays toward chance as responses are added while the criterion-free rule does
not. ⚠ **One attack survived is one attack survived** — this does not establish the framing is
right, and whether a stratum flip and a release flip are one phenomenon needs a shared axis that
does not exist. ⚠ Selection inflation from re-choosing the best rule per stratum was **measured**
(+0.0000 / +0.0022 / +0.0000), not assumed away.
→ [`R435`](A24_what_the_definition_costs/R435_is_a_sufficiency_clause_even_statable) ·
[`R436`](A24_what_the_definition_costs/R436_does_clause_four_exclude_anything_at_home) ·
[`R437`](A24_what_the_definition_costs/R437_do_the_two_bars_invert_between_releases) ·
[`R438`](A24_what_the_definition_costs/R438_does_the_gap_flip_inside_one_release)

---

## What this definition cannot claim

| | |
|---|---|
| **"a core", unindexed** | the admitted set is **empty at the second judge**; only *"a core under J"* is licensed — and J is named by R367's rule, not chosen |
| **a count of admitted arms** | the set moves within **0.25 MDE** (R332) and with the reference's percentile (R354) |
| **that its three clauses each test something** | one excludes nothing, one is judge-emptied, one is irreplaceable |
| **an unindexed size** | at 0.8B top-k loses to a size-matched blind set at **6 of 7** sizes (R362) |
| **that it works on responses it was NOT scored against** | **unresolved against a fair floor** — see the transport note below (R368, R370) |
| **transfer to another criterion pool** | every level here is a fact about **this 16-criterion pool** (R331) |
| **a prompt-SPECIFIC core anywhere else** | ⭐ **the route is now WALKED, not open.** R427 measured clause ②'s *comparator* on the second corpus and it **loses to a longest-reply rule**; clause ② itself is untestable there because its *subject* — a prompt-specific core — does not exist. **Requires: generating criteria from the conversation alone on a rubric-less corpus**, a job with its own assumptions, not a re-run. ⭐ **R432 gated that job at zero GPU and it is worth running:** over the five criterion texts already scored, the best single arm ranks the human's choice first on **0.4527** of interactions while *some* arm does on **0.7220** — headroom **+0.2693** against a floor of **0.0084**, and **the oracle clears the judge-free length rule (0.5096) by +0.2124**. So a prompt-specific arm that fails would be failing *about the criteria*, not about the instrument. ⚠ The oracle chooses **with hindsight, using the answer**: it is an upper bound, and the generated arm's bar is **0.5096**, never 0.7220. ⛔ **R433 RAN IT. `W-LOSES`.** A core generated from each conversation alone — clause ②'s subject, absent from every previous cross-release number — scores **0.4590** against a judge-free longest-reply rule at **0.5135** on the same 7,342 interactions: **-0.0545 [-0.0706, -0.0377] against its own MDE of 0.0235, resolved**, and resolved under the other weighting too (-0.0604 [-0.0781, -0.0418] vs 0.0258). **And clause ② is not even SATISFIED resolvedly:** its own statement is `core > neutral`, and that gap is **+0.0093 [-0.0008, +0.0186] against an MDE of 0.0140** — the interval contains zero. **So the clause names a bar its subject cannot be shown to clear, while a rule reading neither conversation nor criteria beats them both.** ⚠ The conversation-match itself buys **less than 0.0176**: the wrong-conversation sham costs only +0.0050. ⚠ What this does NOT establish: that no generator could. R432's oracle over five existing texts reaches 0.7220, so the ceiling is far above this one greedy decode — **the failure is this generator's** |
| **a k-free criterion share** | the criterion's share of satisfaction variance is **not scale-free in k**, and the cells compared differ (15 vs 4). **Requires: matched k across every cell**, which the home rubric's per-prompt criterion counts do not allow |
| **position randomisation** | unchanged in kind but now measured: the release carries **storage order only**, and R427's `first` baseline indexes that, never what a human saw. **Requires: a presentation-order field** |
| **a causal effect of response length on the human choice** | the target is length-loaded (tau **`+0.2113`**), and every test of it here is **nuisance-matching on a covariate**, never an ablation. **Requires: an intervention on response length** |
| **the MAGNITUDE of random-criteria scatter** | two random draws differ **4.0×** their own resolution in how they align with the hand-written arm — a **direction**, established. **Requires: many draws**; three cannot estimate the sampling distribution of a spread, and saying otherwise would be the bound-versus-point error again |
| **transfer to another release** | ~~one release~~ — ⛔ **RETRACTED 2026-08-04 (R398). This line was never a wall; it was a query nobody ran.** `data/utterances.jsonl` — **68 MB, fetched 2026-07-29** and referenced by 0 files in this repository — holds **68,371 rows over 8,011 conversations, 100% carrying a human `score`, with 26,285 prompts having ≥2 distinct model responses across 21 models.** A second corpus has been on disk the whole time. ⚠ It has **no rubric**, so clauses defined against `full` still cannot transport; **clause ② and the human-agreement target can.** |

---

## ⛔ CORRECTION 2026-08-04 — the limit below is not structural, it is untested

The transport section closes on R233's limit, stated in the definition's strongest terms: the fresh
responses carry **no human rankings**, so transport is of the **compilation** and *"never agreement
with people"*. **That sentence describes this release, and was silently read as describing the
world.**

[`R398`](A24_what_the_definition_costs/R398_is_there_a_second_object_on_disk) asked the cheapest
question left and it had never been asked: **a second corpus with 68,371 human-scored responses has
been sitting in `data/` since 2026-07-29, referenced by no round and named in no document.**

**What changes:** *"agreement with people on responses the core was not built for"* moves from
**impossible** to **untested**. **What does not:** every number below still stands as measured — R398
ran no transport test, computed no core, and reports no effect. It established that the object exists
and nothing more.

## ⭐ THE FIRST CROSS-RELEASE NUMBER 2026-08-04 (R427) — and clause ②'s comparator loses to a length heuristic

**74,048 judge calls, 2,200 seeded conversations, 7,342 interactions of the second corpus.** The
prompt-blind arm — clause ②'s own comparator — picks the human-chosen response at **`0.4374`**. The
judge-free *longest-reply* rule reaches **`0.5096`**.

| arm | ACC | note |
|---|---|---|
| `generic` (prompt-blind) | **`0.4374`** | 74,048 calls |
| chance | `0.4194` | derivation, `mean(1/n_responses)` |
| **longest reply** | **`0.5096`** | **no judge, no criteria, no compute** |
| first (position) | `0.4375` | `generic` is indistinguishable from it |

⛔ **And the bar was fixed before the arm existed.** Read against chance alone, `+0.0179` at 1.05× its
MDE would have been reported as transport. Against the shortcut it is a loss of **−0.0722**, 2.85× the
MDE.

**Robust across the whole grid: `generic` clears the shortcut in 0 of 24 cells** — aggregation
{mean, min, max, median} × restriction {all, n=2, n≥3} × unit {conversation, interaction}, the length
baseline recomputed *inside* every cell. ⚠ Those four aggregations are monotone transforms of the
same values, so this is a **falsification sweep, not a replication**.

⭐ **A pooling attack on the one positive number FAILED, and the scope it leaves is narrower.**
Chance is `1/n` and n varies, so the pooled `+0.0179` could have been a weighting artifact. Stratified
against each stratum's own chance, with the length arm firing as positive control in all three:

| n responses | chance | `generic` − chance | MDE | verdict |
|---|---|---|---|---|
| **2** (2,191 convs) | 0.5000 | **+0.0071** | 0.0229 | **at chance** |
| 3 | 0.3333 | +0.0720 | 0.0646 | clears |
| 4 | 0.2500 | +0.0315 | 0.0307 | clears |

**So the apparatus carries a small real signal only where ≥ 3 responses are compared, and none at
all in the two-response case that is almost the whole corpus.**

⚠ **This measures clause ②'s FLOOR, not clause ②** — see the next section.

### ⭐ `randblind` and `vacuous` have landed (2026-08-04, R427 + R429) — and the content contributes nothing

They were queued to decide whether the criteria's *content* contributes anything. It does not, and
**neither arm moves the result above**:

| arm | what it removes | accuracy | `generic` − arm | its MDE | verdict |
|---|---|---|---|---|---|
| `generic` | — (the comparator) | **0.4374** | — | 0.0171 | the floor |
| `randblind_s0` | the criteria↔prompt assignment | 0.4397 | **−0.0024** | 0.0189 | inside noise |
| `randblind_s1` | " (seed 1) | 0.4396 | **−0.0023** | 0.0217 | inside noise |
| `randblind_s2` | " (seed 2) | 0.4383 | **−0.0010** | 0.0182 | inside noise |
| `vacuous` | **all evaluative content** | 0.4276 | **+0.0097** | 0.0154 | inside noise |

**Stripping every evaluative word changes neither the accuracy nor which responses get picked.**
Three randblind seeds land *above* `generic`, not below — so the criteria's *assignment to a
prompt* carries nothing either, and the direction is the unflattering one in all three.

⛔ **And the pick-level agreement says where what remains lives.** Over ten arm-pairs,
`generic|vacuous` has the **highest excess agreement over its own marginal-matched null**, above
every randblind–randblind pair. R429 asked whether that rank is a *measurement* or an *ordering*
and ran the paired cluster bootstrap the ranking never had:

> **Δ(rank 1 - rank 2) = +0.0234 [+0.0103, +0.0364], p = 0.0003, surviving BH(q=0.10) over all 45
> ordered comparisons.** Controls: placebo Δ(P,P) = 0 exactly · plant at g=0.5 resolves and at
> g=1.0 does not · seed spread 0.00025 across 3 seeds.

<!-- ⚠ THE THREE NUMBERS ABOVE AND THE MEAN GAP BELOW USE AN ASCII HYPHEN, NOT THE TYPOGRAPHIC
     MINUS U+2212 THIS DOCUMENT OTHERWISE PREFERS. That is deliberate and it is load-bearing:
     `definition_matches_the_record.py` compares the captured string to the artifact's own
     `f"{x:+.4f}"`, which emits ASCII. With U+2212 the regex matched nothing and the gate FAILED
     LOUDLY -- which is the correct behaviour and is why this comment exists rather than a silent
     normalisation step. A gate that quietly folded the two characters together would also fold
     together every other pair of glyphs that look alike, and that is how a document drifts from
     its record while the gate keeps printing PASS. -->


**So what the arm responds to survives deletion of the criteria's meaning** — the axis is the
criteria's *topical phrasing*, not their evaluative content. This is a **stronger** statement than
the randblind comparison alone supports, and it **changes the reason**: randblind says *"the
prompt-matching does nothing"*; vacuous says *"the meaning does nothing."*

⚠ **Only ranks 1–3 of that grid are quotable.** R429 measured R427's permutation null against the
analytic expectation of R427's own construction — **all ten gaps carry the same sign, mean -0.0148
against a one-draw band half-width of 0.0104, only 2 of 10 inside** — and attributed the
disagreement to the **null construction**. ⛔ **R430 overturned that attribution the same day.**

The R427↔R429 comparison changed **two** things at once, and the decomposition names which one
carries the gap:

| | R427 | R429 |
|---|---|---|
| aggregation | **CONV** — mean over conversations of per-conversation means | **INTER** — pooled over interactions |
| null | **PERM** — one realised within-stratum permutation | **ANLY** — the closed-form expectation |

Reproducing R427's committed per-pair null from all four cells: **CONV/PERM 8 of 10 · CONV/ANLY 9
of 10 · INTER/PERM 2 of 10 · INTER/ANLY 2 of 10.** *Both* nulls reproduce R427 when aggregated by
conversation and *neither* does when pooled. **The two nulls agree to ~0.002; the two weightings
differ by ~0.013.** The gap is the **aggregation weight**, not the null.

**What survives unchanged:** rank 1 is `generic|vacuous` under *both* weightings, and its separation
from rank 2 resolves under both — **CONV +0.0226 [+0.0083, +0.0374] p=0.0027** and **INTER +0.0234
[+0.0107, +0.0367] p=0.0003**. The number is weighting-dependent and must be quoted with its
weighting, which R429 did not do.

**Where the ordering actually breaks, measured per axis instead of subtracted:** changing the
weighting alone moves **2 of 10** ranks (positions 9 and 10). Redrawing the *same* permutation null
30 times at fixed weighting moves a **median of 4** (IQR 2, range 0–6) — **positions 1, 2 and 3
never move in any draw; position 4 moves in 10 of 30.** So the mid-table ordering is
permutation-draw noise, and R429's own *"ranks 5–10"* named the wrong boundary and the wrong cause.
**Which null is correct remains UNVERIFIED** — that needs a corpus with known truth.

⭐ **And the weighting gap is 10× smaller on the quantity anyone reports.** R430's ~0.013 is the
CONV/INTER difference **on the null**. On the **excess** — agreement minus null, which is what every
round quotes — R431 measures it at **at most 0.0050** across all ten pairs, because reweighting
moves the agreement and the null *together* and the difference largely cancels. That is consistent
with R430's two headline Δ differing by only **0.0008**, and it is why the weighting choice does not
threaten any excess number in this document. **Neither weighting is size-confounded:** **0 of 30**
within-stratum size-association cells clear BH(q=0.10), and the apparent n=2 association at
rho ≈ **-0.19** is a granularity artifact the permutation null carries too (**-0.2116 ± 0.0203**,
observed **+1.21 sd inside it**). ⚠ **What R431 could not explain:** after standardising the stratum
mix the gap is inside its own floor for only **7 of 10** pairs — short of the 8 pre-registered — and
for some pairs standardisation makes it *larger*. Those 3 pairs are an open residual, and the
world they landed in was not among the three the round declared.
→ [`R429`](A24_what_the_definition_costs/R429_is_the_tightest_pair_a_resolved_claim) ·
[`R430`](A24_what_the_definition_costs/R430_is_the_null_gap_the_null_or_the_weighting) ·
[`R431`](A24_what_the_definition_costs/R431_is_the_excess_statistic_size_confounded)

---

## ⛔ `generic` IS CLAUSE ②'s COMPARATOR, NOT ITS SUBJECT 2026-08-04 (R403 + R427)

R403 measured which clause-parts can even be SAID off the home release: **3 of 6 are STATABLE on the
second corpus** — the *size* bound, clause **②**, and **③a**. The three that cannot: **①** and **③c**
need a per-prompt rubric the corpus does not have, and **③b** needs ≥ 2 annotators per prompt where
the corpus carries **`max_raters = 1`** and **0** multi-rater interactions.

⚠ **And a STATABILITY verdict is a fact about the release's FIELDS, not about whether anyone ran the
test.** Clause ② is statable there and, until R427 lands, unstated.

⛔ **The precision error worth naming.** Clause ② reads *"better than a size-matched set that never
read the conversation."* **`core_generic.json` IS such a set** — prompt-blind by construction. So
R427 measures **the comparator's own accuracy on a second release**, i.e. clause ②'s **floor**. It
cannot test clause ② itself, because clause ②'s *subject* — a prompt-specific core — **does not exist
for this corpus and must be generated before the clause has two arms.** Saying "R427 tests clause ②
elsewhere" would have inverted which side of the inequality was measured.

---

## Transport — the clause this definition does not have

Every clause above certifies a core against **the four responses it was scored on**. Nothing says it
works on new ones, and until R368 nothing had measured it: `transport` appeared here **zero** times.

Matched on per-prompt difficulty — the confound R233 named when it declined its own verdict — the
core reproduces the full rubric's ordering on **unseen** responses better than a size-matched random
draw, by **+0.0992 against an MDE of 0.0654** on R233's own exact-class metric, and **+0.0612 vs
0.0535** on a finer pair metric. Same sign, both resolved.

⚠ **Marginal, and stated as such**: 1.52× and 1.14× of their own MDEs, where the MDE is computed over
**4 strata** — the effective n is the strata, not the 250 prompts.

⚠ **And the shape underneath is unexplained.** The core is **at or below random on the responses it
was built for** and above random on responses it was not. **[UNTESTED]** nothing here explains that,
and it is recorded as the residual.

⚠ **R233's limit does not move:** the fresh responses carry **no human rankings**, so this is
transport of the **compilation** — agreement with the full rubric — and never agreement with people.

⛔ **AND THE CONTRAST DECOMPOSES THE OPPOSITE WAY UNDER THE TWO METRICS (R369).** R368 computed the
floors per stratum per arm and never printed them: `Δfloor` is **+0.0308** on exact and **−0.0187** on
pair — under one metric the random baseline **rises** on the fresh arm, under the other it **falls**.
The instability is **bounded**: `Δcore` is positive under both (**+0.1300**, +0.0425) and larger in
magnitude than `Δfloor` in both, so the core term dominates either way. What is metric-dependent is
the **attribution of magnitude**, not the direction.

⚠ And a structural asymmetry remains unseparated: the floor is drawn from **`full`'s own criteria** —
among the items summed to make the target — while the core is a rewrite. A difference-in-differences
cancels that only if it is additive across arms, which the flipping `Δfloor` puts in doubt.
Separating it needs a floor drawn from criteria **outside `full`**.

⛔ **AND AGAINST A FLOOR THAT IS NOT A SUBSET OF ITS OWN TARGET, IT DOES NOT RESOLVE (R370).** The
suspicion was testable and the test needed new labels: the generic 16-criterion pool, identical
across prompts and therefore outside any prompt's `full` rubric by construction, judged against the
fresh responses (16,000 labels). With that floor the contrast is **+0.0810 vs MDE 0.0920** (exact)
and **+0.0161 vs 0.0251** (pair) — **inside the MDE on both**.

**The subset advantage is now a number**: on the original arm the subset floor sits **+0.1413** above
the non-subset floor (exact; +0.0662 on pair). A random draw from `full`'s own criteria reproduces
`full` far better than an external pool does.

⚠ **Not refuted — not resolved.** Both point estimates stay positive; with a fair floor this design
**cannot resolve** transport. And the collapse arrives two ways: on `pair` the contrast falls **74%**
while the MDE shrinks, on `exact` the contrast barely moves and the **MDE grows 41%**.

⛔ **AND THAT VERDICT IS ITSELF A SPECIFICATION CHOICE (R371).** R370 fixed the stratification at
**S = 4** and never swept it. Sweeping S on the same data, the `exact` contrast **resolves at S = 2
and S = 5** and does not at S = 3, 4, 6, 8. On `pair` it is inside the MDE at every S. So
*"transport collapses"* is what S=4 says, not what the data says.

⚠ The between-stratum spread is **sampling noise, not structure**: against a *no-heterogeneity* null
the median ratio is **0.98**. And the MDE **rises** with S, because smaller strata get noisier faster
than √S recovers — so more prompts would help only **at fixed S**, never by adding strata.

⛔⛔ **AND R371'S OWN READING DIED THE SAME WAY (R372) — the curve is no more reportable than the
cell was.** R371 closed by saying *"the honest statement is the curve, not the cell."* Re-run on
**480 random halves** of the same 250 prompts:

| | |
|---|---:|
| R371's set `{2, 5}` recurs | **2.9%** of halves |
| modal outcome | **∅**, at **41.5%** — with **38** distinct sets |
| two halves of one split agree on the set | **4.4%** *(both-empty agreements removed)* |
| `exact` set at full n under an order-independent floor | **{2, 3, 5}**, not `{2, 5}` |

**And the curve's shape is a derivation, not a measurement:** R371 itself measured that the MDE rises
with S while the contrast does not, which makes the resolution rate fall with S **by algebra**.
**S = 2 tops every ranking because its between-stratum sd has ONE degree of freedom and collapses**
— below half the typical contrast in **28.3%** of halves against at most **7.3%** anywhere else
(3.9×). The tell was a full-sample `pair|2` cell returning **MDE = 0.0007**.

⚠ R371's floor was also **order-dependent** — one rng shared across a call, so a prompt's floor
depended on its company. 12 permutations move the `exact|S=4` contrast across **+0.0540 … +0.1185**.

⛔ **AND R368'S OWN MDE IS UNDER-PRICED, WHICH THE CAMPAIGN HAD NO RECORD TO NOTICE (R373).** The
transport MDE above divides by the square root of a count of **strata**, and that count is **4**. A
4-unit sd estimate lands **below half its true value 13.9%** of the time and below three quarters
**36.0%** of the time — so `+0.0992 vs 0.0654` is a comparison against a threshold that is itself a
4-point estimate. **Not refuted; under-priced** — and the distinction matters because nobody
re-examines a cell that reported RESOLVED.

⚠ Of **55** MDE call sites across **38** rounds, **5** divide by a count of aggregated units rather
than the sample, and after resolving each k, **R368 is the only one outside R370–R372 with k < 10**
(R355 is flagged and its k is **25**, which is fine). *The flag is not the severity; only k is.*

> **`The resolving set` is not a well-defined object of this design.** R371 was right that R370's
> S = 4 was a specification choice, and then read a SET off the same single draw — **the error it
> convicted R370 of, one level up.**

**So transport is a stated LIMIT, not a candidate clause** — and the limit is now stronger and
simpler than R370's or R371's version: **the transport contrast is not resolvable by this design at
any stratification, and no stratum count is preferable to another on this data.** R368's number
stands as a number; what it measured was the floor.

## The one sentence

> **What survives every attack in this campaign is clause ③'s RULE — but stated more strictly than
> the campaign has ever implemented it, and on provenance rather than irreplaceability.** Clause ① is a consequence, clause ② holds only under a named judge, the size is
> a bound rather than a number, and *"nothing else can do clause ③'s job"* is **2B-specific**
> (R361). What is left is the rule itself: **a core may not be built from the labels of the prompt
> it is for** — which is checkable by inspection, needs no judge, and is the one claim here that no
> instrument can empty.

⚠ *That closing sentence was published unconditionally one round earlier and was corrected by
attacking it rather than by building on it. It had survived exactly one round.*


⛔⛔⛔ **AND THE RECOMMENDATION THAT RESTED ON THE PREDICTION CEILING IS WITHDRAWN, ONE ROUND AFTER IT
WAS MADE (R504).** The campaign recommended reading ② over ③-dropping because `oracle_k4` (**0.6282**)
exceeded the Bayes ceiling for any predictor (**0.6132**). Recomputed **in one process, on one
population of 968 prompts, with one hold-out convention and three seeds**:

| quantity | recomputed | seed range | as quoted |
|---|---|---|---|
| held-out ceiling (majority of the non-held-out annotators) | **0.6466** | [0.6408, 0.6534] | 0.6132 |
| in-sample ceiling (scored annotator included — the biased one) | **0.6886** | [0.6801, 0.6971] | 0.6520 |
| `oracle_k4` | **0.6325** | [0.6279, 0.6355] | 0.6282 |
| random predictor | **0.3321** | [0.3275, 0.3411] | — |
| ceiling on shuffled annotator assignment | **0.4144** | [0.4005, 0.4225] | — |

**Gap `−0.0141` against a measured noise floor of `0.0220`: `oracle_k4` sits BELOW the ceiling, and
the difference is inside the floor.** Controls all pass and all could fail — the in-sample ceiling
exceeds the held-out one by more than the floor, which is the control that would have caught a
silently biased ceiling; the shuffled ceiling falls toward chance; the random predictor lands at
0.3321 rather than at zero.

⭐ **The recommendation's own text named this as the first check an attacker should run. I wrote that
sentence and did not run it** — and it is the same error as two rounds earlier, when `coval_core`
0.6044 (per-criterion sign agreement) was set against an A2 ceiling. **Twice in three rounds, the
second time with my own warning already in the artifact.**

⚠ **Three-valued, because the attack must not be over-trusted either.** Both recomputed figures come
in *higher* than the quoted ones — a systematic offset rather than noise, so this instrument differs
from the campaign's in a convention not yet isolated. **CONFIRMED: the two compared numbers are not
comparable, which suffices to withdraw. UNVERIFIED: whether `oracle_k4` exceeds the ceiling under the
campaign's own instrument.** *(R504)*


⭐⭐⭐ **AND THE WITHDRAWAL IS ITSELF REVERSED — A CORE IS A RANKER, SO ONE CEILING APPLIES, AND AT THE
CAMPAIGN'S OWN 20-DRAW CONVENTION THE GAP RESOLVES (R505, R506).** Two facts settle it, and the first
is a **derivation** read out of `corebench/score.py` rather than measured: `yvec()` returns **one
scalar per response** and `cls()` takes signs of scalar differences, so a core's six pairwise verdicts
are **necessarily transitive**. It cannot emit the intransitive patterns the per-pair mode uses on
**33.5%** of prompts. **So the RANKER ceiling is the only bound that can apply to a core, and the
PAIR-PREDICTOR ceiling is unattainable by one — comparing a core to it was R504's category error.**

| recomputed at **20 draws/prompt**, 968 prompts, 3 seeds | value | seed range |
|---|---|---|
| `oracle_k4` | **0.6293** | [0.6283, 0.6308] |
| **RANKER ceiling — the applicable bound** | **0.6220** | [0.6200, 0.6235] |
| pair-predictor ceiling (unattainable by a core) | 0.6437 | [0.6415, 0.6451] |
| in-sample ceiling (the biased one — hold-out control) | 0.6863 | [0.6840, 0.6877] |
| random predictor | 0.3342 | [0.3327, 0.3356] |
| shuffled-annotator ceiling | 0.4099 | [0.4077, 0.4123] |

**Gap `+0.0073` against a conservative floor of `0.0047` — RESOLVED.** The resolution sweep is the
evidence that the earlier verdict was about **effort**, not nature: `reps=1` gap +0.0042 floor 0.0091
(inside) · `reps=5` +0.0056 / 0.0082 (inside) · **`reps=20` +0.0073 / 0.0035 (resolved)**. The floor
falls while the gap holds. **R504 and R505 both stopped at "inside the floor" without asking for more
draws, and R479 had been averaging twenty all along.** *(R505, R506)*

⚠ **Bound stated, not smoothed:** the recomputed ranker ceiling is **0.6220** against R479's quoted
**0.6132** — smaller than the discrepancy it replaced, and **still not isolated**. *(R506)*


⭐⭐⭐ **AND THE LAST RESIDUAL IS CLOSED — IT WAS ARM COVERAGE, AND THE FILTER I BLAMED EXCLUDES
NOTHING (R507).** R506 reported a ranker ceiling of **0.6220** against R479's quoted **0.6132** and
left it open. On R479's **actual** population — all prompts with ≥3 rankings — the ceiling recomputes
to **0.6174**, which is **0.0042** from the quoted value and **inside R479's own stated resolution of
0.0093**. On the **968** prompts `oracle_k4` covers it is **0.6218**. **The residual was the
arm-coverage restriction, and R506's comparison stays correct BECAUSE of it** — comparing an arm to a
ceiling requires both sides on the same prompts.

⛔ **The hypothesis that round was built on died to its own positive control.** I opened on
`R479:91`'s `len(v) >= 3` against my `>= 2`. Swept: **n = 1078 at m = 1, 2 and 3 alike** — every
prompt in the release carries at least three rankings, so **R479's filter excludes nothing and is a
no-op.** The control requiring the sweep to move **FAILED**, the script refused to report, and the
round redirected to the axis that does vary. **A flat sweep is not evidence of no effect; it is
evidence the axis was mis-chosen, and only the control tells those apart.** *(R507)*


⭐⭐⭐ **AND ③ HAS A PARTIAL BEHAVIOURAL SURROGATE AFTER ALL — IN THE SELECTION, NOT THE TEXT
(R508).** R501 failed its own positive control looking for one in per-prompt A2 dispersion. R503 then
showed both sides of ③ draw **100.0%** of their criteria verbatim from the *same* rubric pool, which
means no textual test can exist and moves the search to **which items are picked**.

Mean **normalised position** of an arm's selected criteria within that prompt's own rubric list:

| arm | mean position | |
|---|---|---|
| `oracle_k4` | **0.2791** | ③-excluded label-**optimiser** — separates |
| `greedy_k4_fit1` | **0.2880** | ③-excluded label-**optimiser** — separates |
| `random_k4_s0` / `s1` / `s2` | **0.5012** / **0.5039** / **0.5071** | uniform selectors, spread **0.0059** |
| `topw_k8` | **0.5051** | ⛔ ③-excluded and **MISSED** |
| `topwvar_k4` | **0.5090** | ⛔ ③-excluded and **MISSED** |

**POSITIVE control:** `oracle_k4` separates — the case R501's instrument could not see.
**NEGATIVE control:** uniform selectors land where uniform selection predicts, which validates the
position index and was discovered to be a control rather than designed as one.

⛔ **The pre-registered kill fired: a surrogate that misses a KNOWN reader cannot certify an unknown
one, so ③ is NOT replaceable and the fork does not dissolve.** ⭐ **But the shape of the failure is
the finding: every reader that OPTIMISES against the labels is caught, and every miss is RULE-BASED
selection. What escapes is rule-following, not optimisation** — sharper than *"no surrogate exists"*,
and what R501 could not reach. ⚠ Arms whose rule is *stated over the rubric ordering* also separate;
that is a **derivation** and counts for nothing. *(R503, R508)*


⛔⛔⛔ **AND A CHECKABLE ③ DOES NOT RESCUE THE DEFINITION — IT MAKES THE SAME VACUITY HARDER TO SEE
(R509).** R508's surrogate invites an obvious reformulation: replace ③ *"not built by reading the
labels"* (provenance) with **③′ *"not OPTIMISED against the labels"*** (checkable from the criterion
set plus the prompt's rubric). Applied to the **5** arms admitted by ①∧②∧④:

| arm | criterion text | ③′ verdict |
|---|---|---|
| `oracle_k4`, `greedy_k4_fit1`, `indep_k4_fit1` | yes | **EXCLUDED — separate as optimisers (measured)** |
| `topw_k4` | yes | excluded by **derivation** (rule stated over the ordering) |
| **`coval_core`** | **no** | ⛔ **CANNOT RULE — no criterion text, so no positions** |

**③ extension 0. ③′ extension 1 — and that 1 is `coval_core`, with 0 adjudicated members and 1 blind
spot.** Of **95** arms carrying a criterion-text file, the **released core is not one of them**; only
its sham is. **POSITIVE control passes: the instrument ruled on 4 of 5 by measurement.**

⭐ **A zero from an instrument that could not look is silence, not an acquittal — so `coval_core` is
not a member of ③′, it is missing data wearing a member's clothes.** The reformulation converts
*"empty because ③ excludes everything"* into *"one member the instrument cannot see"*: the same
vacuity, less visible. ⭐⭐ **The fork is therefore not provenance-vs-checkability but AN HONEST ZERO
VS A FLATTERING ONE.** *(R508, R509)*


⛔⛔⛔ **AND R509's PREMISE WAS FALSE — THE RELEASED CORE'S CRITERIA ARE IN THE RELEASE, AND
ADJUDICATING THEM MAKES ③′ CHANGE NOTHING AT ALL (R510).** R509 called `coval_core` an
un-adjudicable blind spot because `corebench/results/` has no `core_coval_core.json`.
**`data/conversation_rubrics.jsonl` carries a `coval_core` field with `criterion` text** — sixth
false wall this session, and like the other five it was asserted right after correctly checking
something adjacent.

**Adjudicated:** `coval_core`'s mean normalised selection position within its own conversation's
`coval_full` is **0.2746** (median **0.2222**), against `oracle_k4` **0.2791**, `greedy_k4_fit1`
**0.2880**, and a uniform-selector null band of **[0.4894, 0.5189]**. **It sits with the
label-optimisers. ③′ EXCLUDES it, so ③′'s extension is 0 — exactly ③'s.**

⭐ **The correction makes the result simpler and stronger.** R509 said a checkable clause *hides* the
vacuity; it does not — **it changes nothing.** The definition is empty under both readings, and the
fork's B-column loses the extra cost R509 gave it.

⚠⚠ **SCOPE, and it is large: only 256 of 3,899 core criteria — 6.6% — are locatable verbatim in
`coval_full`.** The statistic is a subsample and may be biased. ⭐ **And that is itself a finding: the
released core is NOT a pure subset of the full rubric**, so 93.4% of its criteria are rewritten or
drawn from elsewhere — which R503's `coval_core (no text)` row concealed by looking in
`corebench/results/` rather than in the release. **The claim WAS bounded as "on every criterion this instrument can
locate" — and that bound is not sufficient (R511).**

⛔⛔ **R510's NUMBER IS DOWNGRADED TO `UNVERIFIED`, AND THE ACCUSATION AGAINST THE CARD IS
RETRACTED.** The dataset card states the construction in full: *"Our process first **REWRITES** all
rubric items to have positive weight and then **MERGES** semantically redundant rubric items while
adjusting their scores. **THEN**, it aims to select up to four rubric items with the highest average
ratings"* — plus *"LM-assisted synthesis plus human review"* and an explicit warning that the method
*"can produce core rubrics that **drift from the data**."* **The 93.4% non-match is the documented
REWRITE step. I quoted step three of three and called the object non-compliant with it.**

**And that voids the statistic.** The 6.6% locatable subset is *exactly the criteria that survived
rewriting unchanged* — a selection with no reason to be independent of selection position. **0.2746
is a reading about the unrewritten remainder, not about `coval_core`.** ⭐ What survives: the released
core's criterion text **is** in the release, so R509's "blind spot" stays retracted. *(R511)*


⛔⛔⛔ **AND R508's SURROGATE IS RETRACTED — MEASURED ON THE ACTUAL RATINGS IT IDENTIFIES THE WRONG
ARMS (R512).** R468's `id_map.json` joins corebench's prompt ids to the release at **968 of 968**, and
`coval_full[i].scores` carries the per-annotator ratings — so ③′ is testable against **the quantity
the dataset card names**, *"the highest average ratings"*, rather than against list position.

| arm | **mean rating percentile** | position (R508) |
|---|---|---|
| `oracle_k4` | **0.4888** | 0.2791 — "separates" |
| `greedy_k4_fit1` | **0.4964** | 0.2880 — "separates" |
| `indep_k4_fit1` | 0.5356 | ~0.29 — "separates" |
| `topw_k4` | **0.7857** | 0.5378 — "derivation" |
| `topw_k8` | **0.6547** | 0.5051 — ⛔ "missed" |
| `topwvar_k4` | **0.5036** | 0.5090 — ⛔ "missed" |
| `random_k4_s0/s1/s2` | 0.4381 / 0.4498 / 0.4473 | 0.5012 / 0.5039 / 0.5071 |

⛔⛔ **The proxy LOSES RECALL — it does not invert.** Against a random band of **[0.4146, 0.4734]**
(3 seeds, spread 0.0118), **every ③-excluded arm sits ABOVE it**, including the two position missed.
So its catches are real and its misses are genuine. ⚠ My first write-up said *inverted*, comparing
0.4888 to a remembered "≈0.5" instead of to the computed band. ⭐ **The
mechanism: `coval_full`'s list order is not rating order.** Position measured *where an item sits in a
list*; ③′ is about *how highly it was rated*. **Instrument's unit ≠ claim's unit, inside the check
built to catch that failure.** ⚠ `gen`, `generic` and `coval_core` remain N/A — no pool overlap — so
③′ stays open and R340's derivation stands. *(R512)*

---

## R514 · Clause ① is subsumed by clause ②, and it is a derivation

**The question.** `STATEMENT.md` had said since R464 that ① *"excludes 0 of 41 arms — UNEXERCISED,
not vacuous"*, defended by an adversarially-constructed worst rubric subset it does exclude at
−0.2779. The label was never checked against the obvious rival: that ① excludes nothing because it
**cannot**.

**The method — no new compute.** R294's census stores, per arm, the A2 score and the two clause
contrasts `c1`, `c2` over the same 968 prompts. Each clause bar is therefore recoverable as
`a2 − c[0]`. Both clauses have the form `a2 > bar`.

**The result.** Across all 41 arms:

| bar | range | meaning |
|---|---|---|
| **bar₁** | **[0.4821, 0.4927]** | a random draw of the prompt's own rubric |
| **bar₂** | **[0.5386, 0.5504]** | the generalising prompt-blind ceiling |

**The ranges are disjoint, gap 0.0459, on every arm.** So `a2 > bar₂ ⟹ a2 > bar₁` by transitivity
of `>`, and the count of arms satisfying ② while violating ① is **0 by construction**.

⛔ **DERIVATION, not measurement.** The 41 arms tested nothing; the algebra did. The assumption it
rests on is that **both bars are global scalars** on a common statistic (A2) and direction — which
is how the census computes them, and which is the only reason the implication holds.

**Controls.** Positive: **24 of 41** arms do fail ①, so the ① verdict is not degenerate and a
"0 violations" reading is admissible. Negative: the bar ordering was verified on **every** arm, not
the one first inspected — a single-arm read would have generalised from n=1.

⭐⭐⭐ **Consequence: the definition has THREE independent clauses — ② ③ ④.** ① is either deleted
or **re-operationalised per-prompt**: admit an arm only if it beats *that conversation's own* random
rubric draw. That is the only reading in which ① can bind, because for individual conversations the
local bar exceeds the global 0.5404. **No round has run it**, and the census stores aggregate
contrasts only, so running it means re-scoring against each conversation's own draw.

**What this does NOT overturn.** The R464 adversarial subset is still excluded at −0.2779; ① is a
*true statement about cores*. It is simply not doing work in the definition as operationalised.

---

## R515 · The per-prompt escape is real, and R514's warrant was wrong

**R514's mechanism claim is retracted.** It said both clauses have the form `a2 > bar`, so `bar₁ <
bar₂` forces subsumption by transitivity. **Reading R294's code shows they are not.** Line 139:

```python
c1 = cell_a(on(S[a], ps), on(S["random_k4_s0"], ps))
c2 = cell_a(on(S[a], ps), on(POOL, ps, list(range(min(K[a], npool)))))
ok1 = verdict(*c1[:3], c1[4]) == POS
```

Both clauses are **paired-difference interval verdicts with an MDE**, against two comparator **arms**
— ① against `random_k4_s0`, ② against the blind pool truncated to the arm's own k.

**Why that matters.** Transitivity of `>` does not carry to interval verdicts, because the two
contrasts have different variances. **`c1`'s CI is WIDER than `c2`'s on 20 of 41 arms**, so the
route by which ① could fail while ② passes is genuinely open. What closes it is not algebra but
**margin**: the tightest ②-passer clears ① by **+0.0582** against a mean CI width of **0.0200** —
about three widths of headroom.

⭐ **Corrected claim: ① is subsumed by ② EMPIRICALLY on all 41 arms with ~3 CI-widths of slack,
NOT by derivation.** The conclusion (① adds nothing as operationalised) survives; the warrant is an
empirical regularity, not a theorem. Calling it a derivation made it sound more certain than it is
and removed the reason to check the flip route.

**And the escape R514 named is real.** Per prompt, `random_k4_s0` scores **0.4927** on average and
the pool **0.5504**, gap **+0.0577** — but the ordering **reverses on 26.96% of prompts** (20.56%
exact ties, sd of the per-prompt difference 0.1597). So the global gap is an average concealing a
large minority.

⭐⭐⭐ **Consequence for the formulation.** ① is **not deletable**. As a global bar it is subsumed;
**per-prompt it has something to bind on, on roughly a quarter of conversations.** The open question
is no longer *"is ① vacuous"* but *"does any actual arm fail a per-prompt ①"*, which needs each
admitted arm re-scored prompt-by-prompt against `random_k4_s0`.

**Instrument note, carried because it will recur:** the release ships **two** saturation families,
`sat_*` and `sat08_*`. Both load without error. R294 uses `sat_*`; a reconstruction on `sat08_*`
reproduces the aggregate to +0.0685 instead of +0.0577 and looks entirely plausible.

---

## R516 · A per-prompt clause ① is not one clause, and ① is deletable

**R515 closed by saying ① is "not deletable" because per-prompt it has something to bind on.**
That escape exists — the comparator ordering does reverse on 26.96% of prompts — but **using it
requires an aggregation, and the aggregation determines the answer.**

**Every admitted arm scored per-prompt against the ① comparator, with all five positive controls
reproducing their stored `c1[0]` to six decimals:**

| arm | win | tie | loss |
|---|---|---|---|
| `coval_core` | **0.5382** | 0.2655 | 0.1963 |
| `topw_k3` | 0.5331 | 0.2696 | 0.1973 |
| `topw_k4` | 0.5227 | 0.2934 | 0.1839 |
| `topw_k6` | 0.5072 | 0.3244 | **0.1684** |
| `topw_k8` | **0.4897** | 0.3316 | 0.1787 |
| null `random_k4_s1` | 0.3781 | 0.2934 | 0.3285 |
| sham `coval_core_sham` | 0.3998 | 0.2149 | 0.3853 |

**Every admitted arm clears the null by a wide margin, so a null-calibrated per-prompt ① excludes
nothing.** At the natural majority reading **τ = 0.50 it excludes `topw_k8`** — and that exclusion
is an artifact.

⭐⭐⭐ **Win rate and loss rate rank the admitted arms at Kendall τ = −0.600.** `coval_core` is 1st
by wins and **4th by losses**; `topw_k6` is 4th by wins and **1st by losses**. The mechanism is
resolution: per-prompt A2 has **7 levels over 6 pairs**, ties are structural, and the tie rate rises
**monotonically with k** (0.2655 → 0.3316). A higher-k arm wins less *and* loses less. **A win-rate
rule punishes an arm for tying; a loss-rate rule rewards it.** Under ties-as-half-wins nothing is
excluded below τ = 0.70.

**So a "per-prompt ①" is a family of rules that disagree about which arm fails, and the aggregation
choice does more work than the criterion.** It is not a clause; it is a knob.

⭐ **Resolution of the ① question, across R514–R516:** globally ① is subsumed by ② (empirically, on
all 41 arms, with ~3 CI-widths of slack); per-prompt it is ill-posed. **① is deletable, and now for
a demonstrated reason rather than an assumed one.** The definition is **② ③ ④**. ⚠ **SUPERSEDED — the definition is ② ∧ ③** *(R519, R599)*. This line predates R519, which measured clause **④ dropping 0 of the 9 ②-passers — identical to ①** — so ④ adds nothing and was retired alongside it. **The retirement reached the claim table and not this sentence**, which is why the deliverable stated two different definitions for 80 rounds. Annotated rather than rewritten (L81): the reasoning below about ① is unaffected and still correct. ⭐⭐ **AND THE RETIREMENT IS ITSELF OVERTURNED (R821) — THE HEAD IS THE DELIVERABLE, ④ IS RETAINED.** The retirement's stated reason was that ④ is *"identical to ①"*. It is not, and the distinction is one this very file already draws eight lines from its own clause table (L385–393): **"excludes nothing BUILT" ≠ "excludes nothing CONSTRUCTIBLE"**, and a count of `0 of N` is *"a fact about the ARM SPACE rather than about the clause."* ① is **DERIVED** — its binding region is *empty by arithmetic* (`GAP ≥ SLACK` on every arm, R347). ④ is **MEASURED**, and R821 ran the test no round in 380 had run: **plant an arm below the floor and see whether ④ removes it.** It removes the plants at δ = 0.10, 0.05 and **0.01** — finer than the design's own noise floor of **0.0067** — and does **not** remove the one at δ = 0. So ④'s binding region is **non-empty and reachable**; it is a clause that has never had to fire, not one that cannot. Two clauses sitting at `0 of N` for opposite reasons, and 80 rounds of counting arms could never have separated them, because **the claim's unit is a CLAUSE and the instrument's unit is an ARM** (§4). On the current 58-arm set ④ still excludes **0 of 58**, with `full_sham` **UNVERIFIED** at +0.0047 [−0.0080, +0.0178]. **The definition is ② ∧ ③ ∧ ④ with size > 1, as the head states.**

**What is NOT claimed:** that no principled per-prompt aggregation exists. Choosing one is a
construct claim and needs an external standard for what a core must do — which this site does not
have, and which the impossibility register already names.

---

## R517 · Clause ④ has never been placed where it could fail

**R439 established ④ is not a reparameterisation of ②** — its bar (**0.4512**) sits **0.0687 below
the weakest of all C(16,4) = 1,820 subsets** in ②'s reference class (min 0.5199, percentile 0.00).
That is a claim about **reachability of the bar within ②'s knob**, and it is sound.

⚠ **The deliverable read it as a claim about the extension, and those are different properties.**
④ adds to the definition only if some arm **passes ② and fails ④**. That cell:

| population | n | ②pass | ④fail | E[both] | identified? |
|---|---|---|---|---|---|
| home judge J | 56 | 0 | **0** | 0.000 | ⛔ **④'s marginal is 0** |
| second release | 7 | **0** | 7 | 0.000 | ⛔ **②'s marginal is 0** |

**In both populations one marginal is degenerate, so the cell is 0 by construction.** A derivation,
not a null. The negative control shows the design is not the problem: pairing the home population
with ④'s global fail rate (22/93) and a 50% ② pass rate expects **6.62 arms** in that cell.

⭐ **So "④ excludes all 7 arms on the second release" is true and is not evidence of independence** —
**② excludes the same 7** *(R434)*. And at home ④ excludes nobody *(R436, `W-REDUNDANT-AT-J`)*.

⭐⭐⭐ **④ is UNVERIFIED, and that is NOT ①'s situation.** ① was measured redundant across 41 arms
with a mechanism and a margin; ④ has simply never been tested where it could fail. **The definition
is ② ③ with ④ carried as unverified** — dropping it would be as unwarranted as asserting it.

**What would settle it:** arms that clear the blind-pool bar scored against the criterion-free rules
on the same release. That is a scoring run, and it is the cheapest open item in the register.

> ⛔⛔ **ANSWERED — AND THIS LINE WENT ON CALLING IT OPEN (entry 1380).** **R849** ran exactly that
> scoring run: all 99 arms against the response-only (criterion-free) family bar, the bar selected on
> the ODD annotator half and every margin scored on the EVEN half. **R856** then intersected the two
> sets — the blind-pool-bar clearers (② , **29**) against the criterion-free clearers (④′, **41**) —
> and found **② ⊆ ④′**, with ②'s comparator **0.5404** sitting **+0.0584 above** ④′'s bar **0.4820**.
> ⚠ **And the sentence two lines above — *"④ has simply never been tested where it could fail"* — was
> answered by R847**, which enlarged the family 30 → 394 and measured the bar rise **+0.0241** against
> a noise arm that moved only **+0.0039**. **Both were still described here as open.**

---

## R518 · ④ is redundant at home, and R517 under-claimed

**R517's wall — "settling ④ needs a scoring run rather than a reanalysis" — is false.** **41 arms
carry both a ② verdict (R294) and a ④ score (R436)**, and at the home judge **②'s marginal is 9,
not 0**. The joint was one merge away.

**Among the 9 arms passing ②, the margin over ④'s bar in units of each arm's own MDE:**

| | margin |
|---|---|
| `topw_k8` (smallest) | **4.90×** |
| `coval_core` | 5.16× |
| `oracle_k4` (largest) | **8.65×** |

**Pre-registered kill was 2.00×.** So "④ excludes 0 of 56 at home" is a **measurement with power**,
not a resolution limit — ④ cannot exclude a ②-passer here.
⛔ **SCOPE ADDED 2026-08-06 (entry 1322): "0 of 56" is the STRICT reading**, on this round's own arm
space — a **third denominator** beside the table's 42 and 58, and it is not harmonised with either.
The power result stands as stated; what does **not** follow is that ④ excludes nothing under the
**permissive** reading the statement adopts, where it removes **25 of 58** (R824). A measurement with
power is still a measurement **of one cell of the reading axis**.

**Negative control:** the scale does place an arm below ④'s bar — `promptecho_sham` at d = −0.0106.
⚠ But it is **under-resolved** (|d|/MDE = 0.29) **and fails ②**, so it cannot populate the
informative cell in either direction.

⭐⭐⭐ **④ is REDUNDANT at the judge the definition names — the same status as ①, by a different
route.** ① is redundant because its bar sits *below* ②'s; ④ because its bar sits **so far** below
(0.0687 under the weakest of ②'s 1,820 subsets, R439) that only arms ② already rejects come near it.

⚠ **On the second release ④ remains genuinely unidentified** — ② admits 0 of 7 *(R434)*, so nothing
there can distinguish the clauses. Unchanged from R517.

**Correction to R517, and the direction matters.** It marked ④ UNVERIFIED in *both* populations,
which is right for one and wrong for the other. **A false UNVERIFIED manufactures work**: it invented
a scoring run that the record already answered. A false acquittal is permanent because nobody
re-examines a cleared claim; a false *unverified* is expensive because everybody re-runs it.

---

## R519 · Only ③ narrows what ② admits — all four clauses, one population, one instrument

R514–R518 tested ① and ④ against ② in separate rounds with separate instruments. Putting all four
on the **41 arms** that carry both R294's verdicts and R436's ④ scores:

| clause | drops of the **9 ②-passers** | drops of the **32 ②-rejects** | reading |
|---|---|---|---|
| **①** | **0** | **24** | **nested inside ②** |
| **③** | **4** | **0** | ⭐ **orthogonal to ②** |
| **④** | **0** | **0** | discriminates nothing at home |

⭐⭐⭐ **The sham column is what makes this a mechanism rather than a tally.** ① *does* discriminate
— on 24 arms — but every one of them is an arm ② has already removed, which is subsumption made
visible. ④ discriminates on nothing at all here. **③ alone cuts where ② does not, and cuts nothing
where ② already has.**

**The four arms ③ removes are the highest scorers**, and all four read the prompt's labels:
`oracle_k4` (all annotators), `oracle_k4_fit1`, `greedy_k4_fit1`, `indep_k4_fit1` (parity 1).

**Surviving all four clauses:** `coval_core`, `topw_k3`, `topw_k4`, `topw_k6`, `topw_k8` —
**identical to the census's own `admitted`**, confirming ①∧④ contribute nothing to it.

**Controls.** Negative: ② against its own admitted set drops 0 — the join is sound. Positive: ③
drops 4, so ①'s and ④'s zeros are measurements rather than silence. Noise floor: R518 put every
②-passer at 4.90×–8.65× MDE above ④'s bar.

⭐⭐⭐ **So the definition is a PAIR, and the two clauses are orthogonal by measurement:**

> A **core** for a conversation is a set of criteria that **② scores better than the best
> generalising prompt-blind criterion set**, and **③ was not built by reading that conversation's
> human labels**.

⚠ **The tension, now measured rather than asserted: the only clause doing independent work is the
one that cannot be checked from the object.** ② is behavioural and anyone can run it. ③ is
provenance — it needs the producer. And it earns its place by removing the *best-performing* arms,
which score highest precisely because they read the answer.

---

## R520 · ③'s provenance literal is complete where used, incomplete one join away

R519 left the definition resting on **② ∧ ③**, with ③ the only clause narrowing anything. ③'s
verdicts come from a **4-element hardcoded literal** in R294 — `USES_PROMPT_LABELS` — declared, not
derived. So the definition's entire working content is one Python set.

**The keyword route fails first, and instructively.** Grepping for scripts that touch the labels
returns **19 of 19** — `score.py` reads labels *to score*. **Instrument's unit: "imports
load_targets". Claim's unit: "the SELECTION consumed this prompt's labels."** Only the source gate
separates them: `select_core.py:102` opens `comparisons.jsonl` **only** under
`a.rule in ("oracle_k", "indep_k", "greedy_k")`.

**Deriving from that gate over the 56-arm universe:**

| | |
|---|---|
| arms in a label-reading family | **10** |
| declared in the literal | **4** |
| **absent** | **6** — `oracle_k4_oracle_k{A,B}`, `greedy_k4_greedy_k{A,B}`, `indep_k4_indep_k{A,B}` |

⭐ **None of the six carries a ③ verdict in R294's census** — they exist only in R436's 56. **The
literal is complete over the 41 arms ③ was ever applied to, so R519 stands unchanged.**

**Controls.** Positive: the derivation recovers all 4 declared members from tags alone. Negative:
none of the 33 documented label-blind arms is derived as a reader — where the keyword version failed.
Sham: deriving on the *satisfaction* list gives 12, not 10, so the instrument reads the label gate
specifically rather than "any rule that consumes something".

⚠ **The hazard is live one join away.** R518 and R519 both joined R294's verdicts to R436's 56 arms
for ④. **A future round extending ③ to that same 56 would silently admit six label-readers.**

⭐⭐⭐ **The general point: a hardcoded set is scoped to the population it was authored against, and
nothing in it records that scope.** The remedy is six lines and is demonstrated here — **derive the
set from the code's own gate instead of declaring it.**

---

## R521 · What the declared literal costs, and a forced check demoted to a control

**The previous round's announced next step could not have failed.** "Does the derivation reproduce
R294's admitted set over the 41?" — R520's output forces *yes*: `derived − declared` = 6 arms, **0**
of which carry a ③ verdict, and `declared ⊆ derived` was already established. **Used here as a
positive control (it passes at 0 disagreements), never as a finding.**

**The version that can fail is the wider population.** Over R436's 56 home-judge arms, literal and
gate disagree on exactly the 6 R520 named, and **all six sit above the ② bar**:

| arm | A2 |
|---|---|
| `oracle_k4_oracle_k{A,B}` | **0.6353** |
| `greedy_k4_greedy_k{A,B}` | **0.6292** |
| `indep_k4_indep_k{A,B}` | 0.6079 |

The current 9 ②-passers span **0.5593–0.6283**. **Four of the six outscore all of them.**

**Controls.** Negative: the 33 label-blind arms disagree on 0. Sham: the *satisfaction* partition
disagrees on 8 versus the label partition's 6, so the price is specific to the label gate rather
than to any rule split. Noise floor: the ② bar is taken at the conservative top of its measured
range [0.5386, 0.5504], so every candidate clears it under every setting.

⚠ **Bound: candidacies, not verdicts** — 15 of the 56 carry no ② interval verdict, and producing
one is a scoring run.

⭐⭐⭐ **The pattern, now three times: the highest scorers are the label-readers.** R519 found ③
removes the top 4 of the 9 admitted; here the 6 the literal misses would be the top 4 of the
extended set. **③ does its work at the top of the distribution, which is where a benchmark's
headline comes from — without it the leaderboard ranks how much each arm read the answer.**

---

## R522 · The six are verdicts, not candidacies

**The wall fell first.** R521 closed saying the real ② verdicts for the six needed a scoring run.
**All six saturation matrices are on disk**, so R294's own contrast machinery re-runs directly —
reanalysis, not scoring. **Third false "needs new computation" wall this session.**

**All six clear ② as interval verdicts:**

| arm | c2 | 95% CI | MDE | verdict |
|---|---|---|---|---|
| `oracle_k4_oracle_k{A,B}` | **+0.0779** | [+0.0701, +0.0853] | 0.0107 | **BEATS** |
| `greedy_k4_greedy_k{A,B}` | +0.0722 | [+0.0643, +0.0797] | 0.0105 | **BEATS** |
| `indep_k4_indep_k{A,B}` | +0.0527 | [+0.0447, +0.0600] | 0.0104 | **BEATS** |

**Controls.** Five positive: the reconstruction reproduces R294's stored `c2` for `coval_core`,
`topw_k4`, `gen`, `generic` and `oracle_k4` at **Δ = 0.00e+00**. Negative: an arm against itself
gives exactly 0 with a degenerate CI. Multiplicity: BH over C = 47.

⭐ `oracle_k4_oracle_kA` reproduces `oracle_k4`'s stored +0.077867 exactly, so the doubled-tag arms
behave as the same object — consistent with oracle-family construction.

⭐⭐⭐ **Settled: under the declared literal, widening the population to the 56 admits six
label-reading arms that BEAT ②, four of them outscoring every currently-admitted arm. Under the
derived gate, all six are excluded.** The fix is six lines (R520) and the cost of not applying it is
a leaderboard topped by arms that read the answer.

---

## R523 · The six are two — and R519 survives because its population had no aliases

**Exact matrix comparison, not a summary statistic:**

- all three A/B pairs are **byte-identical** → six tags name **three objects**;
- `oracle_k4_oracle_k{A,B}` **is exactly `oracle_k4`**, an arm the literal already declares.

⭐⭐⭐ **The literal misses TWO distinct objects — the greedy and indep families — not six.**

**This retracts three of my own claims.** R521's *"four of the six outscore every currently
admitted arm"* fails three ways: two of that four were `oracle_k4` itself; the remaining margin is
`greedy` **0.6292 vs 0.6283 = +0.0009, inside the MDE of ~0.0105**, with `indep` at **0.6079**
resolvedly below; and the arm being outscored is `oracle_k4`, which **③ excludes** — the comparison
baseline was itself a label-reader. R520's "6 missing" and R522's "6 of 6 BEATS" are counts of
**tags**; the per-tag verdicts hold, the population was never a list of objects.

⭐ **R519 is safe.** All 41 census arms are readable and **0 exact alias pairs** exist among them, so
its counts are counts of objects. **The definition ② ∧ ③ stands unchanged, as does ③ removing 4 of
the 9 ②-passers.**

⭐ **And the defect is still real:** two distinct label-reading objects that **BEAT ②** are admitted
by the literal and excluded by the derived gate. The six-line fix remains warranted. What is dead is
the framing — **not "a leaderboard topped by label-readers", but "two more label-readers admitted,
neither demonstrably above the admitted set."**

**Controls:** arm vs itself equal, `coval_core` vs `generic` unequal (positive); a shuffled copy
compares unequal, so the test is order-sensitive (negative). **Exact equality has no noise floor,
which is why it is the right instrument and a four-decimal agreement was the wrong one.**

---

## R524 · The tag population is 56 tags and 46 objects

Partitioning all 56 home-judge tags under **exact** saturation-matrix equality: **46 distinct
objects, 10 duplicate tags in 8 classes.** Controls: the partition recovers **4/4** of R523's
hand-found identities (positive); `coval_core` ≠ `generic` and a shuffled copy does not match its
original (negative, order-sensitive).

⭐⭐⭐ **Most of the collapse is intentional and that is why it went unseen.** `topw_k4_det{A,B}` is
a determinism check whose correct outcome is byte-identity; `random_k4_s{0,1}_ctlS{0,1}` are control
tags; `generic_reprov` is a re-provenance run. **They are supposed to be duplicates. Only their
effect on denominators is a defect.**

**What moves:** R436's *"0 of 56 excluded at J"* has a denominator of **46 objects** — the **zero is
unchanged**. **What does not:** R518's per-arm margins (4.90×–8.65× MDE) and R519's *"③ removes 4 of
9"*, since R523 measured **0** alias pairs among R294's 41.

⚠ **One flag:** `random_k4_s1` — R516's null — has a byte-identical twin tagged `_ctlS1`. The null
stands, but **a tag named as a control that is the same object as what it controls cannot control
anything**, and nothing in the name says so.

---

## R525 · Three variant runs produced no variant, and the source said they should

**The wall fell first.** R524 called the duplicates' intent *"a question about the generating
invocations rather than about the artifacts."* **`select_core.py`'s own `--select-npz` help text
makes the prediction**: the five satisfaction-consuming rules *"change IDENTITY, not just score"*
under a second selection, while `random_k`, `topw_k`, `topabs_k`, `full` are *"satisfaction-blind
and the two specifications coincide for them exactly."* **Fourth false wall of the session.**

**Splitting R524's 8 duplicate classes by that rule partition:**

| | classes | reading |
|---|---|---|
| satisfaction-**blind** | **3** | `topw_k4_det{A,B}`, `random_k4_s{0,1}_ctlS{0,1}` — **duplicate is correct** |
| outside the rule families | 2 | `coval_core_2b{A,B}`, `generic_reprov` |
| ⛔ satisfaction-**consuming** | **3** | `oracle_k`, `greedy_k`, `indep_k` — **should have differed** |

⭐⭐⭐ **So three variant runs were designed to change identity and produced byte-identical
artifacts — a control that did not control.** Controls: all 3 blind-rule variants ARE duplicates, as
the source predicts (positive, and a differing blind variant would have voided the partition);
`oracle_k4` ≠ `oracle_k4_fit1`, so the consuming family can produce distinct objects (negative).

**This gives R523's "alias" a mechanism.** `oracle_k4_oracle_kA` is not a deliberate alias but a
**failed variant run**. ⭐ **And the campaign's "six missing label-readers" trace entirely to three
such runs** — the literal misses **2 distinct objects**, both existing only because a variant run
produced no variant.

⚠ **R524's `_ctlS1` flag is WITHDRAWN.** Those tags are `random_k`, satisfaction-blind, so their
identity is the documented correct outcome. **I flagged them on the naming convention rather than on
the rule — a label read as a description.**

---

## R526 · Closure — the variant mechanism works where the invocation is recorded

**The wall fell first, fifth of the session.** R525 closed saying only "whatever produced them"
could settle the remaining tags. **`corebench/rebuild_selection_08b.sh` records a natural experiment
for the mechanism**: `frozen()` passes `--select-npz` (selection fixed), `rerun()` omits it (rule
re-run under the new judge). **Five arms get both treatments, all five satisfaction-consuming.**

**All 5 pairs differ.** Pre-registered kill was ≥1 identical; it did not fire. Positive control:
`_08b` differs from the home-judge arm of the same name in **5/5**, so the judge swap genuinely
changed the artifacts and the family is not a mislabelled copy.

⭐⭐⭐ **So `--select-npz` does change identity when invoked, and R525's reading stands: the three
home-judge identities are runs where the variant treatment was never applied.**

⚠ **Limit, stated:** this tests the **mechanism** on the second-release population. The home-judge
A/B invocations are genuinely unrecorded — the round establishes the flag is capable of what R525
assumed, not what was typed elsewhere. **Labelled CLOSURE, not a new world.**

---

## R527 · ②'s baseline is a choice, and the baseline-robust arms are the ones ③ excludes

**Sweeping ②'s comparator across its own reference class** — all C(16,4) = 1,820 pool subsets, k=4
arms, R294's estimator:

| baseline | A2 | admitted |
|---|---|---|
| p0 | 0.5144 | **8** |
| p5 · p25 · p50 | 0.5242–0.5391 | **7** |
| p75 · p95 · **PUBLISHED (0.5504, pct 93.7)** | 0.5446–0.5511 | **6** |
| p100 | 0.5575 | **4** |

**The published reference is `POOL[0:4]`, picked by FILE ORDER, landing at percentile 93.7** — a
strict comparator, and the extension moves from **4 to 8** across the class.

⭐⭐⭐ **The four arms admitted at every specification are exactly the four ③ excludes.** The
label-readers are baseline-robust *because* they read the answer; **every arm whose admission is
contingent on the pick is a ③-admissible one.**

⭐ **`coval_core` clears ② at 7 of 8 specifications**, failing only against the strongest of 1,820
subsets — an extreme order statistic, so over-strict by §4. **Its admission is robust; its scope is
not "beats the prompt-blind pool" but "beats it at every baseline below the class maximum."**

**Controls.** Positive: **16/16** k=4 arms reproduce R294's stored `c2` at **Δ ≤ 1e-6**. Negative: a
subset against itself gives exactly 0. ⚠ The first version failed its own positive control and
returned UNVERIFIED, targeting R439's 0.5537 — **a different annotator draw**; 0.5504 is R514's
measured bar₂ maximum, i.e. R294's scale. **The control was comparing two different objects.**

**What the formulation owes:** ②'s *"best generalising prompt-blind criterion set"* hides a choice.
The record should name the subset, that file order picked it, and that it sits at p93.7.

---

## R528 · The definition is non-empty only because "best" was not taken literally

R527 reported admitted-set **sizes**. Reading the p100 **membership** shows what the sizes hid: the
four arms admitted at the strongest baseline are exactly the four ③ excludes.

**Sweeping the upper tail of ②'s reference class, k=4 arms:**

| pct | baseline A2 | ② | **② ∧ ③** | surviving cores |
|---|---|---|---|---|
| 50 | 0.5391 | 7 | **3** | `coval_core`, `generic`, `topw_k4` |
| 75 – 98 | 0.5446–0.5529 | 6 | **2** | `coval_core`, `topw_k4` |
| 99 – 99.5 | 0.5545–0.5555 | 5 | **1** | `coval_core` |
| **100** | 0.5575 | 4 | **0** | ⛔ **(EMPTY)** |

⭐⭐⭐ **The deliverable said ② compares against "the BEST generalising prompt-blind criterion set."
Taken literally that is p100 — and there the definition has no extension at all.** The definition is
non-empty only because the published comparator is `POOL[0:4]` at **p93.7**, not the class maximum.

⭐ **`coval_core` is the last survivor**, holding alone from p99 to p99.5. **The released core is the
most baseline-robust ③-admissible arm in the class** — a genuine positive result about the object.

**Controls.** Positive: the published cell must reproduce R294's own admitted k=4 arms —
`['coval_core', 'topw_k4']` both ways. **PASS.** Negative: a subset against itself gives exactly 0.
⚠ **Scope: k=4 arms only**; arms at other k are outside this reference class.

**Wording corrected in `STATEMENT.md`:** ② now says *"a **strong** generalising prompt-blind
criterion set — the released pool's first four, at percentile 93.7 of its own 1,820-subset class"*,
with the emptiness at the maximum stated in the same clause.

---

## R529 · ③ has been two clauses the whole time, and the page asserted both

**The deliverable said, two sentences apart:** *"② is satisfied by `coval_core`"* and *"③ is what
**empties** the definition."* R294's census has `coval_core` passing both ② and ③, so both could not
hold. Tracing it: `DEFINITION.md` recorded R475 excluding `coval_core` as a **w-reader**, while
R294's code admits it.

**The release settles what a w-reader reads:**

- `DATASET_CARD.md:73` — annotators *"assign **signed weights** ranging from −10 to +10 … the
  absolute value indicated the **importance**"*;
- `DATASET_CARD.md:74` — core selects *"up to four rubric items with the **highest average
  ratings**"*;
- `select_core.py:16` — `topw_k` is *"the k criteria with the highest MEAN importance score.
  **Non-leaky: the weights come from the rubric, not from the outcome.**"*

⭐⭐⭐ **So the ratings ARE annotator-authored, and they are NOT the ranking labels A2 predicts.
`coval_core` is a weight-reader and not a ranking-reader — and ③'s phrase is two-valued:**

| reading | extension of ② ∧ ③ |
|---|---|
| **③-rank** — not built from the response **rankings** | **5**: `coval_core`, `topw_k3`, `topw_k4`, `topw_k6`, `topw_k8` |
| **③-any** — no annotator signal for the prompt at all | **0 — EMPTY** |

**Controls.** Positive: under ③-rank the extension must equal R294's own `admitted` restricted to
②-passers — it does, exactly, so **③-rank is what the code implements**. Negative: the two readings
disagree on **16** arms, so the distinction is not vacuous.

⭐⭐⭐ **This resolves the campaign's central contradiction without retracting either sentence.**
*"② is satisfied by `coval_core`"* is true under ③-rank; *"③ empties the definition"* is true under
③-any. **Neither said which reading it used, and the difference is exactly "the released core IS a
core" versus "no core exists."**

⚠ **Which reading is right is NOT a measurement.** The card describes construction, not a definition
of core. The impossibility register already carries this as **row 7 — a decision about purpose** —
and this round makes it concrete: *does a core have to be producible without any annotator input for
that conversation, or only without the outcome it is scored against?*

---

## R530 · What the empty world costs: 1.29 MDE

R529 forked ③; under **③-any** the extension is empty. **A verdict of "empty" is not a
specification**, and register row 4 asked for *"a strong ③-admissible prompt-aware arm"* without
saying how strong. Measured from R294's stored contrasts:

| ③-any-admissible arm | c2 | MDE | shortfall | mode |
|---|---|---|---|---|
| `generic` | **+0.0009** | 0.0022 | — | **UNRESOLVED** |
| ⭐ `gen` | **−0.0153** | 0.0119 | **1.29 MDE** | LOSES |
| `full` | −0.0310 | 0.0119 | 2.60 MDE | LOSES |
| `random_k12_s0` | −0.0332 | 0.0122 | 2.74 MDE | LOSES |

⚠ **`generic` is excluded from the headline on purpose**: it is a *fixed blind set* measured against
the *blind pool*, so the contrast is near self-comparison — its interval straddles zero. **Row 4 asks
for a prompt-RESPONSIVE arm, and the closest one is `gen`.**

⭐⭐⭐ **So the ③-any world is 1.29 MDE from non-empty, and what would fill it is a `gen`-like
generator ~0.0153 A2 stronger.** "EMPTY" understates how close it is.

**Controls.** Positive: `ok2` reconstructed from each stored `(eff, lo, hi, mde)` via
`report.verdict` matches the census for **41 of 41** arms — so the reading of *why* an arm fails ②
is the code's, not mine. Negative: both failure modes are present (**29** resolvedly-below, **3**
unresolved), so "shortfall" does not conflate them.

**Register rows 3 and 4 now carry the fork and the number.** They were always ③-any rows; under
③-rank neither binds.

---

## R531 · Prompt-responsiveness derived, and the 1.29 MDE survives

**R530's "prompt-responsive" filter was a hardcoded tuple** — `a in ("gen","gen_sham") or
a.startswith("promptecho")` — **the exact defect R520 logged in `USES_PROMPT_LABELS`, committed
three rounds later by its author.** Its closing line then claimed `gen` was *"the ONE"* such arm,
which a hand-written list cannot establish.

**Derived instead from the artifacts** — an arm is index-varying iff its criterion index set differs
across prompts: **18 of 41 vary, 14 are also ③-any-admissible.** `gen` is the closest at
**1.29 MDE**, then `full` at 2.60, then the `random_k12/8/6` family, out to `full_sham` at 5.83.

⭐⭐⭐ **R530's number survives; only the word "one" was wrong — the set has 14 members.**

**Controls.** Positive: `coval_core` VARYING, `generic` BLIND. Negative: `random_k6_s0` is
index-varying while **prompt-blind by construction**, so the proxy measures index variation and not
semantics. ⚠ **That control took two repairs** — it first named `random_k4_s0`, which R294 **skips**
as the clause-① comparator so it could not run, and which loaded directly comes out **FIXED**,
because at small k the same indices exist in every prompt. **The instrument was right both times;
my expectation was wrong.**

⭐ **A fact surfaced in passing and worth carrying: the clause-① comparator `random_k4_s0` uses the
SAME criterion indices for every prompt.** Nothing in the record said so.

**Proxy limit, now demonstrated rather than asserted:** index variation is sound for *"the criteria
differ by prompt"* and **not** for *"the criteria were written for this prompt."*

---

## R532 · The ③ fork costs +0.0748 in A2

**My previous closing line proposed auditing `random_k4_s0` "because clause ① compares every arm
against it" — clause ① was retired eight rounds ago.** The comparator matters for a different
reason: `coval_core`'s **+0.0738** over it is what prices the ③ fork, and R531 showed it uses the
**same criterion indices for every prompt**.

**Re-measured against a TRUE per-prompt uniform 4-draw from each prompt's own rubric, 3 seeds:**

| | |
|---|---|
| published (fixed-index) | **+0.0738** |
| per-prompt draw, 3 seeds | **+0.0748**, spread 0.0030 |
| ratio | **1.01×** (kill at 0.50×) |

**Controls.** Positive: the fixed-index contrast reproduces R294's stored `c1` at
**+0.073790 = +0.073790**, so both comparators share a scale. Negative: the per-prompt draw varies
across prompts where `random_k4_s0` does not.

⭐⭐⭐ **So ③-any forbids an operation worth +0.0748 in A2 — selecting rubric items by their
annotator-assigned weights rather than at random.** Against R530's finding that the ③-any world sits
**1.29 MDE ≈ 0.0153** from non-empty, **the forbidden operation is worth ~5× the gap.** ③-any is not
marginally restrictive; it removes the largest single source of advantage a ③-rank core has.

⭐ **And the fixed-index property did not bias the number** — a flag I raised that turned out not to
bite, which is worth saying as plainly as if it had.

---

## R533 · Weight-reading is the operation, not the core: a dose curve to a forced zero

My previous closing line called `topw_k4` *"the other admitted arm that reads weights"* — **there
are four**, which turns one check into a dose-response.

| arm | k | advantage over a per-prompt random draw @k | spread |
|---|---|---|---|
| `coval_core` | 4 | **+0.0726** | 0.0031 |
| `topw_k3` | 3 | +0.0724 | 0.0057 |
| `topw_k4` | 4 | +0.0705 | 0.0015 |
| `topw_k6` | 6 | +0.0644 | 0.0007 |
| `topw_k8` | 8 | +0.0585 | 0.0020 |
| **`full`** | **15** | **+0.000000** | 0.0000 |

⭐⭐⭐ **`coval_core` (+0.0726) is indistinguishable from `topw_k4` (+0.0705): the released core's
advantage IS generic top-weight selection.** The number prices the **operation**, not the object.

**Controls.** Positive: `coval_core` reproduces R532's +0.0748 at +0.0726, within its seed spread.
Negative: `full` selects every criterion, so weight-reading can be worth nothing — **+0.000000,
exactly**. ⛔ **That zero is a DERIVATION** (at k=all both arms take the same items), which is what
makes it a good endpoint: **a curve failing to hit it would indict the construction.** It hits to
six decimals.

⭐ **So the fork's price is a curve: ③-any forbids an operation worth +0.0726 at k=4, decaying to 0
by k=15.** Fewer items kept ⇒ selecting them by weight is worth more.

⚠ **Not shown: that the weights are GOOD.** This prices reading them, not whether the annotators
were right — register row 6, an external standard.

---

## R534 · ③ has three input classes, not two

R529's partition put `topvar_k`/`topwvar_k` in the **weight** bucket. `select_core.py` disagrees:
`topw_k` sorts on `-w[i]` and `topabs_k` on `-abs(w[i])` (**annotator weights**), while `topvar_k`
sorts on `var(ssat)` — **judged satisfaction** — with the code's own comment: *"Non-leaky: the spread
is a property of the **responses**, never of the human target."* `topwvar_k` reads both.

⭐⭐⭐ **So an arm can read the responses' judged satisfaction while reading no human input at all**
— a class ③-any's phrase does not cover, **because a judge is not an annotator.**

| class | n | | reading | extension |
|---|---|---|---|---|
| rank | 4 | | ③-rank | **5** *(R529: 5)* |
| weight | 10 | | ③-any | **0** *(R529: 0)* |
| **sat** | **1** (`topvar_k4`) | | **③-judge** *(new)* | **0** |
| weight+sat | 1 | | | |

**Both extensions unchanged — R529's conclusion survives and only its taxonomy was wrong.** On this
population ③-any and ③-judge coincide because no ②-passer is in the `sat` class; **a future
satisfaction-reading arm clearing ② would separate them.**

**Controls.** Source read: 4/4 selection expressions confirmed verbatim. Positive: the ③-rank
extension equals R294's own `admitted` restricted to ②-passers. Negative: all three classes
non-empty on real arms.

⚠ **Register row 7 now carries three options, not two:** must a core be producible without the
rankings, without any annotator signal, or without any judged signal either?

---

## R535 · ③-judge is remote, and spread-selection loses to weight-selection

**Pricing the third reading rather than restating its verdict:**

| arm | reads | A2 | shortfall (MDE) | ② |
|---|---|---|---|---|
| `coval_core` | weights | **0.5665** | −1.51 | **True** |
| `topw_k4` | weights | **0.5642** | −1.26 | **True** |
| `topwvar_k4` | weights+sat | 0.5040 | 3.24 | False |
| `topvar_k4` | **sat** | 0.4863 | **4.24** | False |

⭐ **③-judge is 4.24 MDE from becoming distinguishable, against `gen`'s 1.29 for ③-any** *(R530)* —
**remote, not nearly-live.**

⭐⭐⭐ **And the release's own selection rationale is refuted.** `select_core.py` argues in a comment
marked *"DERIVATION, not a hunch"* that spread-selection is **"the direct fix"** for `topw_k`'s
blindness to arithmetically-inert criteria. **Measured, `topw_k4` 0.5642 beats `topvar_k4` 0.4863 by
0.0779**, and the hybrid `topwvar_k4` at 0.5040 is still **0.0602** below weights alone.

**The mechanism in the comment is right** — an inert criterion flips no pairwise sign. **The
inference is wrong: selecting FOR spread optimises the wrong quantity, because high spread with low
importance is noise.** Even multiplying importance by spread loses to importance alone.

**Controls.** Source read: rationale confirmed verbatim. Positive: `ok2` reconstructed for **41/41**
arms. Negative: `topw_k4` and `coval_core` **clear** ②, so the shortfall scale is anchored on both
sides. ⚠ **Scope correction to R534:** one sat-class arm in *this census*; `topvar_k4_08b` and
`_08bR` are on the second release. ⚠ **Impossible here:** whether spread wins under a different
judge — register row 2.

---

## R536 · The selector ordering survives a second judge

**The wall fell first, for the sixth time.** R535 closed saying a second judge needs *"an install"*.
**`rebuild_selection_08b.sh` had already re-run every selection arm under the 0.8B judge** — 32
`_08b` artifacts on disk.

**Which arms, from the source:** `topw_k` is satisfaction-blind, so its frozen and rerun
specifications *"coincide exactly"* — hence **no `topw_k4_08bR` exists**, and `topw_k4_08b` *is* the
0.8B-judge topw arm. `topvar_k4_08bR` is the 0.8B-judge topvar arm.

| judge | n | topw | topvar | diff | 95% CI |
|---|---|---|---|---|---|
| **2B** | 968 | 0.5642 | 0.4863 | **+0.0779** | [+0.0679, +0.0879] |
| **0.8B** | 968 | 0.4646 | 0.4009 | **+0.0636** | [+0.0551, +0.0720] |

⭐⭐⭐ **Weights beat spread under both judges. R535's refutation of `select_core.py`'s own "direct
fix" rationale is a fact about SELECTION, not about the 2B model** — and the `cross-model` criterion
the register lists as needing another site is **met on this one**.

**Controls.** Source read: the satisfaction-blind claim confirmed, and the **absence** of
`topw_k4_08bR` confirms it operationally. Positive: `topw_k4_08b` differs from `topw_k4`, so the
judge swap bit. Negative: `topvar_k4_08b` differs from `_08bR`, so the 0.8B topvar arm is a distinct
object. ⚠ **Correction to my own caveat: both judges resolve to n = 968, not different populations —
an over-cautious scope statement is still a wrong one.**

---

## R537 · The dose curve replicates under the 0.8B judge

R533 measured weight-selection's advantage over a per-prompt random draw at matched k under the 2B
judge. Re-run under the 0.8B judge, using `topw_k*_08b` and `sat08_full`:

| k | 2B | **0.8B** | ratio |
|---|---|---|---|
| 3 | +0.0724 | **+0.0521** | 0.72 |
| 4 | +0.0705 | **+0.0519** | 0.74 |
| 6 | +0.0644 | **+0.0443** | 0.69 |
| 8 | +0.0585 | **+0.0410** | 0.70 |
| **all** | +0.000000 | **+0.000000** | — |

⭐⭐⭐ **Positive at every k, monotone, exact zero at the endpoint, under both judges — and
attenuating consistently to ~0.7× under the weaker one.** Weight-reading's value is a fact about
**selection**, replicated cross-model for the second time *(R536 was the first)*.

**Controls.** Positive: all **4** 0.8B arms differ from their 2B namesakes, so this is not the same
measurement twice. Negative, forced: k=all returns **+0.000000** — a derivation, and the reason it
is a good endpoint is that a curve missing it would indict the construction.

⭐ **A naming trap worth carrying:** `sat_<arm>_08b` are the rebuilt **selection arms**;
`sat08_full` is the 0.8B **judging of the full rubric**. **`sat_full_08b` does not exist** — reading
its absence as missing data would have made this round look impossible.

⚠ **`sat_coval_core_08b` is absent, so the released core is the one admitted arm whose curve
position is unreplicated.**

---

## R538 · No second judging of the released core, and the first wall to survive

**The wall check, which this session has run seven times and which failed six:** artifacts from a
judge stronger than the home 2B are **`*_7b*` → 0, `*qwen*` → 0**. **This one holds.** Six false
walls made "my walls are false" feel like a law; it was a tendency, and only checking each one
distinguishes them.

**And `coval_core_2bA` is not the missing second judging.** R524 had it in a duplicate class not
containing `coval_core`, with no documented prediction. Measured: it covers **200 prompts** against
`coval_core`'s 968, and on the **200 shared prompts 0 cells differ**. It is the **same judging on a
subsample**; its identity to `_2bB` is the correct outcome for a deterministic judge run twice.

**Controls.** Positive: `coval_core` vs its **sham** on the same 200 shared prompts differs on
**200 of 200**, so a zero is a measurement rather than silence. Negative: `coval_core` against
itself gives **0**.

⭐ **So R537's gap is real: the released core is the one admitted arm whose cross-judge position
cannot be replicated from anything on disk** — and `Qwen2.5-7B-Instruct`, register row 2, remains
**an install**, now verified rather than assumed.

---

## R539 · The on-site round is 16,440 model calls

My last line said the honest version of *"why not run rows 3 and 4"* is a cost that had not been
measured. It is measurable exactly, because **`gen` already exists** — a generation round has been
run here, so the work is readable rather than estimated.

| component | calls |
|---|---|
| generation — one criterion set per prompt | **968** |
| judging — 16 satisfaction cells per prompt × 968 | **15,472** |
| **TOTAL** | **16,440** |

⭐⭐⭐ **Comfortably within one local-model session. Cost cannot be the reason not to spend rows 3
and 4.**

**Controls.** Positive: the counter must read judge cells, so `topw_k4` must give exactly **k × 4 =
16** per prompt — it does. Negative: `full` keeps every criterion and must exceed any k-limited arm
— **60 > 16**.

⚠ **Not measured and not guessed: wall-clock and money.** Converting 16,440 calls to time needs a
measured tokens/sec for the local model on this GPU, through pueue. **That is the one number a "why
not" would have to cite.**

⭐ `coval_core` ranges **[8, 16]** cells per prompt and `gen` **[4, 16]** — consistent with the
dataset card's *"about 95% end up with four … the remainder two or three."* **The artifact and the
card agree without being asked to.**

---

## R540 · R541 · The on-site round is 25.3 minutes, and the first figure was 17× too high

**R539 priced one rows-3/4 round at 16,440 model calls and named wall-clock as unmeasured.**
R540 measured decode throughput on the two sizes that *are* the campaign's judges — **89.2 tok/s
(0.8B), 80.6 tok/s (2B)**, both controls passing — and converted it to **7.25 h**.

⛔ **The conversion was wrong. The judging step does not decode.** `judge_core.py` calls
`Judge(model).score(prompts)` on a batch and contains no `generate()`; R417, quoted in that file's
own provenance comment, had already established the judge has no stochastic step.

⭐ **And the project had measured the right thing four times, in its own pueue logs**, because
`judge_core.py:117` prints elapsed seconds beside the call count:

| task | calls | seconds | calls/s |
|---|---|---|---|
| 634 / 635 / 636 | 3,168 | 40.1 / 40.0 / 40.0 | 79.0 / 79.2 / 79.2 |
| **642** | **15,488** | **199.3** | **77.7** |

| step | time |
|---|---|
| judging — 15,472 calls @ 77.7/s | **3.3 min** |
| generation — 968 × 110 tok @ 80.6 tok/s | **22.0 min** |
| **TOTAL** | **25.3 min** |

**Controls.** Positive: three replicates agree at **0.25%** spread. Negative: **4.89×** the work took
**4.98×** the time — throughput, not startup.

⭐ **R540 is not void — its decode figure is the right instrument for the GENERATION half.**
**A correct measurement pointed at the wrong operation is a wrong APPLICATION, and only naming the
instrument's unit and the claim's unit separately catches it.**

⭐ **Register row 2 is confirmed by a real failure**, not asserted: pueue task 654 (`r492-7b-b2`)
attempted Qwen2.5-7B judging on 2026-08-04 and died with
`torch.OutOfMemoryError: 14.60 GiB in use of 15.40 GiB`. **R538's "no 7B artifacts exist" now has
its mechanism — attempted, not unattempted.**

## R555 · Register row 2 named a model where it meant a requirement — and it is unblocked

Row 2 read *"a second, stronger judge — `Qwen2.5-7B-Instruct` is present (29 GB, 4/4 shards) but
OOMs in bf16"*, and treated **that model's** OOM as the row's blocker. The **requirement** is a judge
stronger than the home judge. `covalx/judge.py:48,258` name the campaign's two judges as
`Qwen3.5-2B-Base` (home) and `Qwen3.5-0.8B-Base` (second) — so anything above 2B satisfies it.

**`Qwen/Qwen3.5-4B` loads and scores.** On 24 real prompts from the home release, judged through
`covalx.Judge` exactly as the campaign does:

| judge | peak VRAM | secs | distinct scores | mean |
|---|---|---|---|---|
| `Qwen3.5-2B-Base` (home, positive control) | **4.00** GB | 4.3 | 15 | **0.4038** |
| **`Qwen3.5-4B`** | **8.89** GB | 21.2 | 16 | **0.4058** |

**8.89 against 16 GB is 7 GB of headroom** — not marginal. The negative control confirms a
nonexistent checkpoint fails to load, so *"it loaded"* is informative rather than vacuous.

⚠ **And the register's size for the 7B was wrong.** Every real copy on this box measures
**15.23** GB of safetensors, not 29 — consistent with an fp32 arithmetic slip (7.6B × 4 bytes).
At 15.23 GB the 7B's OOM on a 16 GB card is *tight*, not hopeless, which is a different claim from
the one the row was making.

⚠ **Scope: `stronger` remains a proxy.** 2× parameters in the same family is defensible and is not a
demonstration that the 4B is a *better* judge. What is demonstrated is that it **loads, fits, and
returns non-degenerate scores** — which is what row 2 said could not be had without an install.

## R556 · Row 5 offered two alternatives and one was already satisfied

Row 5 prices independent replication at *"another site"*, requiring *"a second team **or** a second
release"*. **The second release is on disk** — `data/utterances.jsonl`, 68.2 MB — and **3 of 376
artifacts** were computed on it *(R556)*, under `R398_…` · `R427_…` · `R433_…`.
⚠ Those directory names are **file provenance, not citations**: R398 and R427 predate the
`world` convention and record `verdict`/`controls` keys instead, so they carry evidence and
settle nothing. Only R433 has a world. **The count is this round's claim, not theirs.**

⚠ **Two axes, which I nearly conflated and which the register does too.** A *second **judge***
(`Qwen3.5-0.8B-Base`, used by R536/R537) scores **the same release**; a *second **corpus*** is a
different release. They discharge different criteria, and only the second is what row 5 names.

**So the row is wrong in KIND rather than in price.** What is missing is not a site — it is a
**second designer**, and §2.5 states that is dischargeable here by clean-context agents given the
QUESTION and never the ALGORITHM. ⚠ **Not available this session:** the operating instructions in
force forbid dispatching agents unless asked, so the remedy is named and **not** claimed as planned.

⚠ **My count was 4 before I read the hits.** The fourth was R550's gate audit, whose amended-rounds
dict holds the directory name `R399_what_estimand_does_the_second_corpus_admit`. **The instrument
matched a round's NAME and would have been reported as a corpus RESULT.**

## R557 · Row 1 measured VERBATIM overlap on an object its own card documents as a REWRITE

Row 1 blocks ③′ on the released core because only **6.6%** of core criteria appear verbatim in
`coval_full`, and asks for the field `coval_core[i].source_rubric_item_ids`. **The dataset card
documents a rewrite and merge before selection** — so a rewrite is precisely what an exact-match
instrument cannot see. **The row named an OBJECT where the requirement is a PROPERTY: a recoverable
mapping from core item to source items.**

Matching by **similarity** instead of identity, per prompt, over 968 prompts and 3,828 core items:

| | value |
|---|---|
| **POSITIVE CONTROL** — top-1 on the 298 items whose source is known verbatim | **1.0000** |
| **PLACEBO** — a *different* prompt's rubric matches at least as well | **0.0000** |
| margin (top1−top2), KNOWN median | **0.8035** |
| margin, UNKNOWN median (n=3,530) | **0.3101** |
| unknown items clearing the KNOWN set's 10th-percentile margin | **21.0%** |

⚠ **21.0% is a BOUND ON IDENTIFIABILITY, not an accuracy.** There is no ground-truth mapping — that
absence *is* row 1 — so accuracy is identified **only** on the verbatim subset and merely bounded
elsewhere. **Partial identification means bounds, not a point.**

⚠ **My verbatim share is 7.8% (298/3,828), the row says 6.6%.** My normalisation — lowercase plus
whitespace collapse — is strictly more permissive, and a looser rule returning a larger share is
consistent rather than contradictory. **Both are reported; neither silently overrides the other.**

**So the row's PRICE is right for a COMPLETE mapping and wrong for the requirement.** A partial
mapping is available on this site with no new field, and the publisher's field remains the only
route to a *complete* one.

## R558 · The scope column named every axis but the one that empties the definition

Register row 6 asks *"construct validity — is A2-vs-held-out-annotator the right target?"* and
prices it at **another site**. **That is two questions in one row.** Construct validity — does A2
measure core-ness — genuinely needs an external standard. **Target robustness — does the choice of
agreement statistic change the answer — was measured on this site and the artifact has been on disk
throughout.**

**968 prompts, six targets, four distinct admitted sets** *(R558)*, from the sweep artifact
under `R288_does_the_partition_survive_the_target/results/target_sweep.json` — named as file
provenance, because that round predates this campaign's `world` convention and settles nothing
on its own:

| target | admits |
|---|---|
| `A2·annot`, `A2·consensus` | `coval_core`, `topw_k4` |
| `A1·annot`, `A1·consensus` | **∅** |
| `tau·mean` | `coval_core` |
| `top1·mean` | `topw_k4` — **not** `coval_core` |

**And the claim table did not say so.** Parsed mechanically: **10 of 10** rows name a known axis
(judge, prompts, arms); **0 of 10** name the target. The positive control is what makes that zero a
measurement rather than silence — the parse demonstrably sees scope tokens.

⭐⭐⭐ **So every extension count on the page — the 5, the two 0s — has been readable as
unconditional, while two of six defensible targets send the extension to zero and a third excludes
the only released core.** The fix is one scope note above the table, stated once: a scope restated
per row drifts, and the copy is never the one that gets corrected.

## R559 · The B recommendation is one cell of a two-cell curve, and row 7 calls it "not a measurement"

Register row 7 reads *"whether reading **A** is correct after all"*, removed by *"a use for 'core'
that does not require prediction"*, priced as **"not a measurement — a decision about purpose"**.
**But the recommendation of B rests entirely on a measurement**: `oracle_k4` clearing the ranker
ceiling, because an object that beats the bound for its own class is reading rather than predicting.

**Two rounds computed that gap. Both persist 4-of-4 passing controls. Their ratios straddle P14's
admissibility line of 1.5.**

| instrument | gap (rank) | floor | **effect / floor** | admissible |
|---|---|---|---|---|
| `R505_…` | **0.009527** | **0.022039** | **0.432** | **no** |
| `R506_…` — the cell on the statement | **0.007338** | **0.004666** | **1.573** | barely |

**Range 0.432 – 1.573, a spread of 3.64×, and the page shows one cell.** G4 asks for the whole
specification curve including the cells that kill the finding; **this is the curve, and one of its
two cells kills it.**

⚠ **What is NOT claimed here.** R506 argues by derivation that only the ranker ceiling applies —
`corebench/score.py`'s `yvec()` returns one scalar per response, so a core's six verdicts are
necessarily transitive. **That derivation is not attacked.** What is shown is narrower and enough:
the *floor* against which the surviving gap is judged differs by **4.7×** between two rounds whose
controls both pass, and only the flattering one is published. **A negative control excludes the
cross-round ratio (0.333) as a cell nobody ran.**

⭐⭐⭐ **So row 7 is wrong in the same way rows 1, 2, 5 and 6 were, and worse: it does not merely name
an object where a property is meant — it declares a measurement to be a decision, which removes the
question from the register's own jurisdiction.** The decision about purpose is real and downstream;
the measurement in front of it is at **1.57 by one instrument and 0.43 by another.**

## R560 · The scope column's defect is a SHAPE, and `baseline` was stated by zero rows

R558 found the **target** missing from 10 of 10 claim rows and fixed it with one note. That was one
axis, found by hand. **G1 requires four.** Measured across all ten rows:

| dimension | rows stating it |
|---|---|
| **baseline** | **0 / 10** |
| **regime** | 4 / 10 |
| instrument | 6 / 10 |
| population | 8 / 10 |
| **all four** | **0 / 10** |

**The positive control is what makes the zero admissible**: `population` was found in **8 of 10**, so
the vocabulary demonstrably matches this page's own usage. **An axis vocabulary that finds nothing
everywhere is a broken vocabulary; one that finds `population` in 8 rows and `baseline` in none is a
measurement.** A negative control (an invented axis vocabulary) matched **0** rows.

⭐⭐⭐ **`baseline` at 0/10 is the consequential one.** ②'s comparator is `POOL[0:4]` **by file
order**, at percentile **93.7** of its 1,820-subset reference class — and **the extension moves
4 → 8 across that class.** So every extension count on the page was conditional on a baseline the
page never named, in the same way it was conditional on a target the page never named.

⭐ **This is why the fix is structural rather than another note.** Patching one axis per round would
have taken four rounds and converged on nothing, because the defect is that **the column had no
shape**: it was prose, and prose omits silently. The constants now sit in one table with four named
fields, and a row's own cell carries only its departures from them.

---

## R602 · The two corpora are disjoint on the string axis

Re-derived directly from `data/comparisons.jsonl` (home, **1078** distinct prompts) and
`data/utterances.jsonl` (second, **68371** rows carrying a text key, **26673** distinct), because
R399's *"3 strings, 2 of them greetings"* was an **exact-match** count and comparability need not be
an exact-match question.

| definition of overlap | home vs second | shuffled-vocabulary floor |
|---|---|---|
| exact identity | **0** | 0 |
| normalised identity | **0** | 0 |
| token-Jaccard, median max per prompt | **0.1654** | **0.1654** |

Per seed, real vs floor: **0.1667 / 0.1667 · 0.1628 / 0.1628 · 0.1667 / 0.1667**. p90 **0.2117**
against a floor of **0.2117**. Maximum observed **0.2778**.

⭐ **The real and shuffled medians are identical to four places**, so the apparent token overlap is
**shared English function words with no shared content.** The negative control — shuffle tokens to
preserve the vocabulary and destroy the strings — is what makes that separation, and the gap it
measures is **0.0000**.

**Controls:** home-vs-home returns exact **1078/1078** and Jaccard max **1.0000**; the synthetic
placebo returns exact **0** and Jaccard max **0.0000**.

⚠ **Bounded below:** the Jaccard sweep runs against a **3000**-text subsample, so a max over a subset
cannot exceed the max over the whole — a small value is conservative.

⚠ **Discrepancy, reported:** R399 says **3**, this says **0**. Different extractions of the home
population; the direction replicates and the exact figure does not.

⚠ **IMPOSSIBLE:** string overlap is not topical comparability. A corpus can share no strings and ask
the same question. One axis, bounded.

---

## R606 · Provenance recording misses the page's own sources

The corpus carries a source-hash mechanism: **109** of **426** parseable artifacts (**25.6%**) hold a
`source_sha256` / `source_name` / `sha256` / `src_sha` key. Adoption by citation status, at the round
level over 377 rounds with artifacts:

| | cited by `STATEMENT.md` | not cited |
|---|---|---|
| rounds | 105 | 272 |
| **carry a provenance key** | **0.1143** | **0.2904** |

**Δ = −0.1762**, time-stratified permutation **p = 0.0003** over 12,000 draws; unstratified 0.0002.
At the stricter *non-empty value* level the picture is unchanged: **0.1143 vs 0.2868, Δ = −0.1725,
p = 0.0008.**

**Controls.** Plant — provenance stripped from every cited round — returns **Δ = −0.2904 at
p = 0.0001**; at g=0 the unplanted statistic reproduces **−0.1762** exactly; the placebo at the same
marginal returns **+0.0350 / +0.1011 / −0.0574** across three seeds.

⚠ **The dose-response MDE is DEGENERATE for this plant and is not used.** Stripping moves Δ monotonely
away from zero starting at the observed value, so the smallest planted |Δ| (**0.1857**) necessarily
exceeds the observed (**0.1762**) and the band cannot contain the observation. The observed effect is
judged by its own stratified permutation.

⚠ **Δ is a DERIVATION** forced by four counts over a complete enumeration; only the permutation p is
tested. ⚠ **A recorded hash proves a source was NAMED, not that the bytes match it**, so 0.1143 is an
upper bound on attributability.

---

## R607 · Which eras drive the provenance gap

R606's pooled gap of −0.1762 decomposed over five equal round-id bands, 378 rounds, 106 cited.
**Every cell is a DERIVATION** — a count over a complete enumeration; only the reconstruction check
is a test.

| era | round ids | n | cited | P(prov \| cited) | P(prov \| uncited) | Δ |
|---|---|---|---|---|---|---|
| 0 | — | 0 | 0 | — | — | UNDEFINED |
| 1 | 220–242 | 23 | 0 | — | 0.0870 | UNDEFINED |
| 2 | 243–364 | 118 | 3 | 0.0000 | 0.1739 | −0.1739 |
| 3 | 365–485 | 118 | 35 | **0.2571** | **0.6627** | **−0.4055** |
| 4 | 486–606 | 119 | 68 | 0.0441 | 0.0392 | **+0.0049** |

**Citation rate by era:** 0.0000 · **0.0254** · **0.2966** · **0.5714** — citation concentrates LATE.
**Provenance rate by era:** 0.0870 · 0.1695 · **0.5424** · **0.0420** — a 13× collapse between the
last two bands.

So the pooled value is two effects: a within-era selection in the best-documented band (era 3), and a
compositional effect from citing heavily into the band where the practice had collapsed (era 4).

**Controls.** The cell-weighted mean of the per-era Δs reconstructs the pooled value at **−0.1625 vs
−0.1772**. A random `cited` label at the same marginal returns **−0.0461 / −0.0199 / −0.0330**.
Shuffling provenance **within** each era gives per-era Δs of mean magnitude **0.0626** against the
pooled **0.1772**.

⚠ Two eras have an empty arm and their Δ is **UNDEFINED, never 0**. ⚠ Round id is a proxy for time,
not time; no artifact carries a timestamp.

---

## R608 · What separates era 3's documented cited rounds

Population: the **35** rounds in 365–485 that `STATEMENT.md` cites, split **9** with a provenance key
against **26** without. Era and citation are held fixed by construction.

**Power was computed before any feature was read.** Null distribution of max|Δ| over the whole
6-feature grid, 200 draws: median **0.2863**, p95 **0.4359**, max 0.5812 — so a feature must exceed
**0.4359** to clear the grid. The pre-registered kill (MDE above 0.50 ⇒ unresolvable regardless) did
not fire.

| feature | P(f \| provenance) | P(f \| none) | Δ |
|---|---|---|---|
| **`late_in_era`** | **0.3333** | **1.0000** | **−0.6667** — SURVIVES |
| `many_artifacts` | 0.1111 | 0.0000 | +0.1111 |
| `has_py` | 1.0000 | **0.9615** | +0.0385 |
| `has_readme` | 1.0000 | 1.0000 | 0.0000 |
| `big_readme` | 1.0000 | 1.0000 | 0.0000 |
| `has_npz` | 0.0000 | 0.0000 | 0.0000 |

Arc offers no contrast: all 35 are in `A24`.

**Controls.** A feature perfectly correlated with provenance returns |Δ| = **1.0000**; a feature
independent of it returns **0.2051**, below the grid null, so the instrument can fail; a constant
feature returns exactly **0.0000**.

⭐ **All 26 undocumented cited rounds are in the band's late half**, and every non-temporal feature is
flat. The separation is temporal, so **R607's within-era selection is partly an artifact of a
120-round bin**: the collapse happens inside era 3, not at the boundary drawn. The 13× figure stands;
its location does not.

⚠ A structural correlate is not a reason; why a round recorded its source needs the round's author.

---

## R609 · Where the unattributable evidence begins

Sweeping every admissible cut (at least 5 rounds each side) across band 365–485, cited rounds only,
n=35 with 9 carrying provenance. **26 cuts tested; the null is taken on the MAXIMUM across them**, so
the winning cut earns no credit for being the best of many.

**Best cut 434 · Δ = 1.0000** against a max-over-cuts null of median **0.3095**, p95 **0.4800**, max
**0.6333** over 400 label permutations.

Every cited round below 434 records its source; **not one at or above it does**. The right-hand side
is `P(prov | ≥ c) = 0.0000` at every cut from 434 through 477 — 0.6923, 0.6429, 0.6000, 0.5625,
0.5294, 0.5000, 0.4737, 0.4500, 0.4286, 0.4091, 0.3913, 0.3750, 0.3600, 0.3462, 0.3333, 0.3214,
0.3103 and 0.3000 on the left as the cut moves right, and zero on the right throughout.

**Controls.** A step planted at 450 is recovered **at 450** with |Δ| = 1.0000; provenance independent
of id returns max|Δ| = **0.2857**, below the null, so the instrument can fail; constant provenance
returns **0.0000** at every cut.

⚠ **The shape claim is one-sided.** The round also reported a rank correlation of **−0.1471** failing
to clear its null of **0.7961**, implying *step rather than slope* — but the outcome is binary with 26
ties, so that statistic is degenerate, and a perfect step is also the extreme slope. **The separation
is established; its shape is not.**

⚠ Round ids order the work; they do not date it.

---

## R610 · The switch appears in the uncited rounds too

The sweep of R609 rerun through one code path on both arms of band 365–485, each read against **its
own** max-over-cuts null because the arms differ in size.

| arm | n | with provenance | cuts | best cut | Δ | own null p95 | median | max |
|---|---|---|---|---|---|---|---|---|
| CITED | 35 | 9 | 26 | **434** | **1.0000** | 0.4800 | 0.3095 | 0.6333 |
| UNCITED | 83 | 55 | 74 | **428** | **1.0000** | 0.4923 | 0.2841 | 0.7051 |

**Distance between boundaries: 6.** Both switches are total — every round below the cut records its
source, none at or above it does.

**Controls, on the uncited arm.** A step planted at 412 is recovered **at 412** with |Δ| = 1.0000
against 0.5385. Provenance independent of id returns |Δ| = **0.4567** against its null of **0.4722** —
a pass by **0.0155**, narrow enough that the conclusion rests on the observed 1.0000 rather than on
the control's comfort. Constant provenance returns **0.0000** at every cut.

So the shortfall R606 measured is real and its cause is the **work**, not the **selection**:
provenance recording ended corpus-wide at ~430 and the page's citations concentrate after it.

⚠ A boundary in id order is not a change in practice — it is equally consistent with a reorganisation,
a renumbering or a gap in the record, and nothing here carries a timestamp.

---

## R611 · What else changed at the boundary

Band 365–485, **both arms pooled**, n=118, cut fixed at **B = 431** — the midpoint of R610's two
independently measured boundaries (434 cited, 428 uncited), **chosen before any feature was read**, so
no feature selects its own cut. Whole-grid null on max|Δ| over 9 random features, 200 draws: median
**0.1492**, p95 **0.2057**, max **0.2512**.

| feature | before | after | Δ | clears 0.2057 |
|---|---|---|---|---|
| provenance *(positive control)* | 0.9808 | 0.0455 | **−0.9353** | yes |
| `has_world` | 0.0455 | 0.9808 | **+0.9353** | yes |
| `has_controls` | 0.8788 | 0.3269 | **−0.5519** | yes |
| `readme_over_4k` | 0.7727 | 0.6154 | −0.1573 | no |
| `py_over_8k` | 1.0000 | 0.9231 | −0.0769 | no |
| `multi_artifact` | 0.1212 | 0.0577 | −0.0635 | no |
| `many_keys` | 0.6061 | 0.5577 | −0.0484 | no |
| `has_py` | 1.0000 | 0.9615 | −0.0385 | no |
| `has_readme` | 1.0000 | 0.9808 | −0.0192 | no |
| `has_mde` | 0.2273 | 0.2115 | −0.0157 | no |

The provenance and `world` shifts are **equal in magnitude and opposite in sign to four decimals**, so
the convention **substituted** a verdict field for a provenance field rather than losing one. The
`controls` fall is **unmirrored** and is a genuine reduction.

**Controls.** Provenance clears at the fixed B (**−0.9353** vs 0.2057), so the boundary survives
pooling and fixing; a feature independent of id returns **0.0262**, so the instrument can fail; a
constant feature returns **0.0000**.

⚠ A boundary in id order is not a date and a correlate is not a cause.

---

## R614 · How much of the era the claim table draws on

Population: rounds **431–606** with at least one parseable `results/*.json` — **171** of them. The
numbered claim table cites **17 distinct** rounds, spanning **519–581**; that span holds **63** id
positions and **63** existing rounds, so it is dense.

| quantity | value |
|---|---|
| coverage of the era | 17/171 = **0.0994** |
| coverage within the span | 17/63 = **0.2698** |
| observed mean gap between cited rounds | **3.8750** |
| null over 2,000 random 17-subsets | 5% **8.5000** · median **10.0000** · 95% **10.8125** |

The observed gap sits far below the null's 5th percentile, so the cited set is **more clustered than
chance**: the concentration is a habit rather than a shortage, and **154 rounds of the same era exist
and are not cited.**

**Controls.** A contiguous block of 17 returns a mean gap of **1.0000** against the same null, so
clustering is detectable; a random 17-subset returns **10.0625**, inside [8.5000, 10.8125], so the
instrument can fail; the full era as its own cited set returns coverage exactly **1.0000**. The
pre-registered kill required at least 10 cited rounds for the clustering statistic; 17 clears it.

⚠ Coverage is a **DERIVATION** over a complete enumeration — only the clustering is tested. ⚠ A
citation may carry a caveat rather than a number, so coverage bounds the evidence base from **above**.

---

## R615 · Does the citation selection track outcome?

Population: rounds **431–606** with artifacts (**171**), split by whether the numbered claim table
cites them (**17** / 154). Classification is the first token of `world`, case-folded and
punctuation-stripped — the rule `statement_provenance.py` already uses.

| quantity | value |
|---|---|
| rounds writing a `world` | 170 of 171 |
| with a classifiable first token | **117** = 0.6842 |
| classifiable among the cited | **17 of 17** |
| classifiable among the uncited | 100 of 154 |
| class mix | B **73** · A **27** · C **9** · UNVERIFIED **7** · D **1** |
| Δ on the most common class, cited − uncited | **+0.0271** |
| permutation null, 2,100 draws | **[−0.2482, +0.2335]** |

The observed Δ sits inside the null, so **the selection does not track outcome on the classifiable
slice**: R614's clustering is positional.

**Kill, evaluated before any distribution was read:** classifiable cited **17 ≥ 8** and smallest
expected cell **6.00 ≥ 5** — both cleared, so the comparison was admissible.

**Controls.** A synthetic population with cited all one class and uncited all another returns Δ =
**+1.0000**; classes assigned independently of citation return **−0.0200**; a constant class returns
**+0.0000** exactly.

⚠ Conditional on classifiability: that subset is non-random — R594 measured short values as commoner
late — so nothing here speaks for the 54 rounds whose verdict is unclassifiable. ⚠ A first-token class
is a convenience, not a type: R595 measured this field as open **corpus-wide**, which is a different
population from this era.

---

## R616 · Is the cited set's six-token rate more than chance?

Property: the first token of `world`, case-folded and punctuation-stripped, lies in
{A, B, C, D, E, UNVERIFIED}. **This is FORM, not legibility or quality** — R591's own value,
`"MIXED — …"`, is a well-formed verdict the rule excludes.

| quantity | value |
|---|---|
| era 431–606, six-token rate | 117/171 = **0.6842** |
| cited | **17/17 = 1.0000** |
| uncited | **0.6494** |
| Δ = cited − uncited | **+0.3506** |
| null, 2,100 random 17-subsets | 2.5% **−0.2372** · median **+0.0241** · 97.5% **+0.2200** |

The observed Δ sits **above** the null, so the cited set takes the six-token form more often than
drawing 17 rounds from the era at random would give. The pre-registered ceiling kill — unresolvable
if the era rate exceeds 0.95 — did not fire at 0.6842.

**Controls.** A cited set drawn only from six-token rounds returns **+0.3506**, ⚠ *identical to the
observation*, since the cited set already is 17/17 and the ceiling is 1.0: the control proves the
value is **attainable**, not that it could be **exceeded**, so the verdict rests on the null. A random
17-subset returns **+0.1547**, inside the interval, so the instrument can fail. A property every round
has returns **+0.0000** exactly.

Taken with R614 (position: clustered) and R615 (outcome: flat), the selection is sensitive to **when**
and **how** a round wrote and not to **what it concluded**.

---

## R617 · Does the `controls` key track controls being run?

Population: rounds **431–606** with artifacts (**171**). The property under test is a JSON key named
`controls` at any depth; the construct is checked against two independent signals before any contrast
is read.

| quantity | value |
|---|---|
| rounds writing the key | **0.1462** |
| rounds whose README discusses controls | **0.9006** |
| rounds whose `.py` carries control-shaped names | **0.8596** |
| agreement key ↔ README prose | **0.2339** |
| agreement key ↔ code names | **0.2865** |

Both agreements fall far below the pre-registered floor of 0.60, so the kill fired and the contrast
was **not read as evidence**. Ninety per cent of rounds discuss controls and eighty-six per cent carry
control-shaped code while fifteen per cent write the key: **the key is a schema habit.**

**So R611's `has_controls` fall from 0.8788 to 0.3269 is a schema change, not a loss of controls** —
retracting the one unmirrored casualty the R605–R617 arc had identified.

**Controls.** A round with key and signal alongside one with neither scores agreement **1.0000**;
shuffling the key across rounds moves agreement to **0.2456 / 0.1754 / 0.2105**, so the observed value
is not merely the marginal; a key every round has scores **0.9006**, exactly the signal's own rate
rather than 1, so the statistic does not saturate.

The contrast was computed and printed for completeness — Δ = **−0.1623** against a null of
**[−0.1623, +0.1642]** — and marked NOT READ AS EVIDENCE.

⚠ README prose and code identifiers are proxies too; agreement bounds the construct from above and
nothing here shows any round's controls were correct.

## R618 · What a next site must provide for clause ② to be evaluable

**This belongs in the definition and not only in the audit**: it is the condition under which the
definition can be *stated* about an object at all.

| a release must carry | it serves ②'s phrase | home | second |
|---|---|---|---|
| a prompt / user turn | *…for a conversation…* | ✓ | ✓ |
| multiple responses per unit | *…scores RESPONSES…* | ✓ | ✓ |
| a human preference target | *…better THAN…* | ✓ | ✓ |
| **a released criterion POOL** | *…drawn from the RELEASED POOL…* | ✓ | ⛔ |
| **a released CORE** | *…a CORE scores…* | ✓ | ⛔ |

Validated by reproduction against R603 — home evaluable, second not, missing exactly those two — with
the g=0 control showing that stripping the home release of the same two fields reproduces the second
release's exact failure. ⚠ **NECESSARY, NOT SUFFICIENT**: R602 measured the second corpus as disjoint
in content, which no schema check can see.

## R628 · What the assurance suite establishes about a number — the bound

> **Provenance cannot be INFERRED. It must be DECLARED, and then checked.**

Four register lines, each written as a prediction and tested by intervention; all four held.
**UNVERIFIED citation → CAUGHT · laundered value → NOT caught · a real value asserted as a different
quantity → NOT caught · a drifted re-derived label → CAUGHT.**

The two measured limits behind it: **the collision floor** — an invented decimal matches a persisted
artifact value **35.15 / 36.12 / 37.60%** of the time at 4 dp — R625's own verdict is
`UNVERIFIED`, since its decomposition's controls failed; **this null is the measured part**
(R625, 3 seeds × 4000) — and **the
rarity signal being the gate's own selection**, gate-verified precision **0.072 → 0.905** across the
threshold sweep against gate-blind **0.450 → ~0.70** (R627).

⚠ The drift was caught by transitive anchoring, not by re-derivation, so a drift in a value
`STATEMENT.md` does not also carry is untested. ⚠ The register's completeness is not testable from
its own lines.

## R631 · Clause ③'s testability — the bound, carried in from FORMULATION.md

**Clause ③ is decided per arm by reading `select_core.py`. That is an annotation, not a
measurement**, and whether it *could* be a measurement was tested along both available routes.
**Both bound out.**

- **Route 1 · through PERFORMANCE — REFUTED.** The leak slope has sensitivity **1.000** and
  specificity **0.886** blind over 41 arms, but `corr(slope, A2) = +0.934`, its four false positives
  are exactly the admitted set, and `oracle_k4` — the *maximally* leaky arm — sits **3.25 sd BELOW**
  what its quality alone predicts. **No residual leak signal.** The confound is structural: fitting
  on labels is *what makes an arm better*, so a performance detector measures the leak's effect and
  cannot be separated from it.
- **Route 2 · through SELECTION — one rule family only.** Label-free features of the selected
  criterion set reach **0.866** held-out-by-arm (structure+text), but **0.510 — chance — held out by
  MECHANISM.**

⛔ **Route 1's refutation also retracts R335**, whose 32.9-sd dose-response separated *dose-induced
quality*. R335's artifact still records `W-DECIDABLE`; **that verdict is superseded.**

⚠ Whether this bound is *correct* needs re-running R336–R338, which this site cannot do. What R631
established is that it was **stated only in `FORMULATION.md`**, which no gate reads.

## R704 · What the generator's name is worth once an arm is held out

R693 measured that clause ②'s verdict is **88.1%** predictable from the arm's rule family, and R694
that a memorising fit on `(family, k)` scores **95.2%**. Both are fits scored on their own data and
both said so. R704 measures the matching floor: **leave-one-out**, against the **base rate** (the
majority class, no partition at all), over **all 42 arms** rather than over the arms a clause happens
to exclude.

The gain from the `(family,k)` partition for clause ② is **+0.000** — base rate **0.786**, with the
partition **0.786**. Across five partitions (`family` · `k` · `(family,k)` · `(family,k,sham)` · a
single cell) the best gain is **+0.048**, two arms of 42, and **no partition clears its own
2000-draw permutation null**. F1 provenance reaches **+0.048** at best. F3's **+0.286** under a
`k`-partition is a **derivation**, not a measurement: F3 *is* the predicate `1 < k <= 4`.

So the asymmetry R703 opened — clause ② carrying 20 unique exclusions against 4 and 2 — is a
**count**: ② excludes **33 of 42** arms, and a demanding clause produces many unique exclusions
whatever it encodes. At n=42 the resolution is **0.024** per arm, so the cross-clause ordering is
reported and the cross-clause difference is not.

Two designs failed before the object did, each caught by a control registered before the run. The
round's registered headline — a cell-determined share — was refuted by its own **sham**: a
single-cell partition scored **1.000** against the treatment's **0.650**, because under one cell every
prediction books as cell-determined. And the registered population was **outcome-conditioned**:
evaluating a clause on its own exclusions fixes the base rate at 1.000 for any clause excluding a
majority and 0.000 for any clause excluding a minority, by algebra, before any data is read. That
population was named in R703's closing sentence, so the defect was inherited from the question.

## R705 · What gain this design can detect, and what that withdraws

R704 reported the `(family,k)` partition as worth `+0.0476` to clause F1 and `+0.0000` to clause ②,
and read a difference between them. R705 prices that number against the design's own floor.

The minimum detectable gain — the smallest true partition-attributable gain at which this design
rejects its own nuisance-matched permutation null at alpha 0.05 with power 0.80 — was measured by a
count-preserving swap dose-response over 66 cells: 3 base rates by 2 partitions by 11 doses, 400
replicates per cell, 2000 null draws. **The observed `+0.0476` is resolvable in 1 of 6 cells.** At
F1's base rate under `(family,k)` power is **0.807** and the MDE **0.0468**; at clause ②'s base rate
power is **0.564** and the MDE **0.0792**; at a balanced base rate power is **0.037** and the
permutation null alone sits at **+0.4048**. Under `(family,k,sham)` the power target is never reached
at any dose at F1's base rate.

So the F1-versus-② ordering is **withdrawn as unresolvable, not as wrong**: a comparison between a
value this design can see and one it cannot is not a comparison. **The zero is untouched and is
strengthened** — a gain of exactly 0.0000 requires no resolution to read, and the refutation of
R703's premise rests on it.

A derivation separates the two clauses without any of that. Since `gain <= 1 - base_rate`, F1's
ceiling is **0.0952** and clause ②'s is **0.2143**, so the same `+0.0476` is **50.0%** of one and
**22.2%** of the other. Equality in raw units across different ceilings is not equality.

Controls: calibration at dose 0 returned power **0.0625** against a 2-alpha bound of 0.10, so the
test is not anti-conservative; a maximal plant returned power 1.0000; the negative control — planting
on the true cells and measuring with shuffled ones — returned **0.0275**; the sham, planting on the
true cells and measuring with a single cell, returned a mean gain of exactly zero; monotonicity of
power in dose gave Spearman **+0.9909**; the noise floor, the standard deviation of the gain at dose
zero, is **0.0453**. Two of these were mis-specified on the first run in the same way — the label was
planted as a function of the very partition it was then measured with, so the negative control
destroyed nothing and returned power **0.9975** — and the correction is that the ingredient must be
removed from the measurement while the plant stays on the true structure.

## R709 · Whether clause F1's n=1 is the corpus or the definition that counted it

R685 reported that the judge-dependence of clause ③'s separation rests on a single verdict pair, and
`STATEMENT.md` carried that as "one verdict pair". R709 applies the standard's own remedy — count
what the release contains against what the code consumed.

Eleven rounds in this repository carry both judge keys; R685 examined seven. The four it skipped are
R683 through R686, the instrument rounds themselves, so that exclusion is a self-inclusion control
and not a search failure. R685 then reduced seven rounds to one pair by counting only booleans and
small closed-set strings, stating that continuous per-judge values differ by construction and are
excluded — while clause F1's scope claim is itself about a continuous quantity's sign across judges.

Measured under three nested rules: R685's own gives **1** pair, reproducing its count exactly; adding
the SIGN of continuous per-judge numerics gives **15** comparisons at **0.8000** agreement; adding
vector orderings gives 17 at 0.7647. Six of the widened comparisons bear on the separation — two
disagree and four agree — against the one R685 could use.

**All six are in R361.** Widening the rule added fields, not independent rounds, and correlated
measurements of a single comparison are not a second comparison. So the phrase understated the
corpus and is corrected to "one round"; the conclusion is unchanged. What does change is the
surrounding claim: the two judges are not broadly discordant, agreeing at eighty percent across the
widened set while disagreeing on this quantity, which makes the disagreement more specific rather
than less real.

The round's own first pass returned ten pairs under R685's rule rather than one. Nine of the ten were
control flags — positive, g=0, placebo and sham — which pass at both judges by design. R685 had
already found and excluded exactly that defect, and the audit reimplemented the walk from scratch
while reading R685's verdict string rather than its exclusion logic. Reported, it would have
retracted a correct result.

## R711 · Whether the core-versus-sham residual is above a same-size random admission

Clause F2 was kept, after its agreement with A2 was shown to be arithmetic, for the residual it was
said to genuinely own — the released core against its own sham. R711 tests that residual against the
only null that matters: a clause that admits the same number of arms with no regard to shams at all.

The ledger holds five sham pairs. Clause ② separates two of them, `coval_core` and `topw_k4`, and
zero of the other three, because it rejects both members of those. Separation is therefore only
possible where the base arm is admitted, which is two of the five pairs, so the residual is two of
two possible rather than two of five — a ceiling of two, and reaching a ceiling of two is precisely
what makes the exact probability large.

Enumerated over all **445,891,810** admissions of nine arms from forty-two, the separation count has
mean **1.7247** and the exact probability of reaching two or more is **0.5727**. The enumeration was
cross-checked against a sixty-thousand-draw sampled null agreeing to within **0.00154**, so the
figure carries no Monte-Carlo error. Swept over admission sizes the exact probability never clears
0.05: **0.2876** at k=5 and **0.7577** at k=14.

Controls: a plant admitting all five bases and rejecting all five shams yields five separations at an
exact probability of **0.002581**, so the instrument registers a maximal effect; an admission drawn
only from non-pair arms yields zero separations, so the statistic is not free; and three same-family
non-sham control pairs yield zero separations at an exact probability of 1.0000, so sham-ness is the
ingredient and removing it removes the signal.

So the justification is downgraded. This does not say the two separations are wrong — they are real
verdicts — it says they are not evidence for the clause, since a clause with no sham sensitivity
produces them fifty-seven percent of the time. Why they separate is untestable here: the prompt
having been withheld is an interpretation of a verdict, and no counterfactual over the generator
exists in this release. F2 stands on its exclusions and no longer on a justification.

## R712 · Whether a clause's unique-exclusion count is above a same-size random admission

After its A2 agreement was shown circular and its sham residual shown to be at chance, clause F2 was
left standing on one thing: the twenty arms it uniquely excludes, the largest count of the three
clauses. R712 gives that count the null it never had.

A clause's unique exclusions are the arms the other two clauses admit and it does not, so the ceiling
is the size of that intersection. For F2 the ceiling is twenty-three, making its count twenty of
twenty-three possible rather than twenty of forty-two. Under a uniformly random admission of nine
arms from forty-two the expected count is **18.0714**, and the exact probability of reaching twenty
or more is **0.1405**, enumerated hypergeometrically over all **445,891,810** admissions with no
Monte-Carlo error, cross-checked against a sixty-thousand-draw sample agreeing to within **0.00097**.

Running the identical machinery on all three clauses inverts the asymmetry the campaign has carried
since R703. F1 provenance excludes **4** against a ceiling of **7** at an exact probability of
**0.0003**; F2 behaviour excludes **20** of **23** at **0.1405**; F3 size excludes **2** of **5** at
**0.5956**. Under Benjamini-Hochberg at q equals 0.10 over the whole nine-cell sweep only F1 at its
observed admission size survives. So the clause with the fewest unique exclusions is the only one
whose count beats its own null, and the raw ranking that put F2 first was a statement about its
admission size.

Controls: a clause admitting nine arms entirely outside the ceiling set yields the full ceiling at an
exact probability of **0.000207**, so the instrument registers a maximal effect; a clause admitting
nine arms drawn only from the ceiling set yields fourteen, below the null mean, so the statistic can
move down as well as up.

This does not say F2 is wrong, nor that the arms it excludes are the wrong arms. It says the count is
not evidence, and whether the excluded arms are the right ones is construct validity requiring a
standard outside this repository. All three of F2's supports have now fallen — the A2 agreement to
circularity, the sham residual to chance, the exclusion count to admission arithmetic — and the
clause is retained while carrying no evidential support this site can supply.

## R713 · Whether clause F1's exclusions are stipulated or discovered

R712 left clause F1 as the only one whose unique-exclusion count beat its own null, at an exact
probability of three ten-thousandths. R713 asks what that number is measuring.

F1 excludes exactly four arms and nothing else in the forty-two-arm ledger: greedy_k4_fit1,
indep_k4_fit1, oracle_k4 and oracle_k4_fit1. The name predicate matching oracle or the fit1 suffix
returns exactly that set — four of four, no false positive, no false negative, a miss of **zero**
arms. The best predicate for clause F2 over the same families misses **five**, and clause F3's exact
match under a k-predicate is a derivation because F3 is that predicate.

So F1's probability measures that we built four label-reading arms and a clause that excludes
label-reading arms. A uniformly random admission is a meaningful null for a clause whose exclusions
are discovered and an empty one for a clause whose exclusions are stipulated, and the exact name
agreement is what distinguishes the two cases here. F1 is therefore the most constructed of the three
clauses rather than the most informative, and R712's reading is corrected accordingly.

This is not a defect in the clause. A clause stating that criteria were selected without reading
outcome labels should exclude exactly the arms built to read labels, and exact agreement is the
clause working. What is void is the probability, not the clause.

Controls: a predicate known wrong for F1 misses by thirteen arms, so the matcher does not match
everything; three thousand random four-arm subsets reproduce F1's exclusions zero times against an
exact chance of one in one hundred eleven thousand nine hundred thirty; and scrambling arm names
against verdicts at fixed multisets gives zero exact matches in three thousand draws, which excludes
the world in which any predicate can be made to fit four of forty-two strings.

Two defects in the round's own instruments were caught and fixed before it landed. Its first sweep
compared every predicate only against a clause's exclusion set, so F3's own k-predicate scored a miss
of forty-two and looked like the worst fit on the board when it is the exact complement and therefore
a perfect reproduction; the miss is now the minimum over both polarities. And its negative control
built a list from a set before shuffling, so the seed fixed the permutation but not the input order
and two runs returned one match and zero; sorting first makes the round byte-identical across runs
and across a changed hash seed.

The limit is the claim unit. Exact name agreement is evidence about construction and never proof of
it: that the arms were built to be excluded is a fact about this project's history rather than about
the ledger, and this round measures reproducibility while reasoning about what a null can price.

## R714 · How many cores the release ships, and whether the clauses share a unit

R713 closed by asking whether a definition can be attacked at all by a site that built the objects it
is defined over. Taking that question literally meant looking for objects this site did not build,
and there are 986 of them two directories away: `data/conversation_rubrics.jsonl` carries a
`coval_core` for each of 986 conversations, with criteria counts distributed two at one, three at
forty-three, and four at nine hundred forty-two.

So the deliverable's headline, that the release ships one core, is true at the arm level — one core
generator — and false at the object level, where the release ships **986** core instances. The page
never stated which it meant, while the impossibility register used one released core as a hard limit
round after round.

The larger finding is that the formulation mixes units. F1 and F2 are predicates over a generator: a
selection procedure, and a score across prompts. F3 is a predicate over an instance: the cardinality
of one criteria list. A three-clause definition whose clauses range over different objects cannot be
applied to any single object as written, and no round in this arc had said so — invisible while every
round tested the formulation against the forty-two arms, because an arm carries both a generator
identity and a criteria list, so the distinction never had to be made. The 986 instances force it:
they have a size and no provenance record, so they can satisfy F3 and cannot even be asked about F1.

Measured on the 986, **F3 is evaluable and admits 1.0000**, while **F1 and F2 are not evaluable** and
are reported as such rather than as passing. Controls: the card's own published statistic reproduces
from the file at a maximum of four and **0.9554** at exactly four; a nonexistent field yields zero
instances rather than a silent empty pass; F3 applied to the same file's `coval_full` field rejects
**0.9970**, so the clause reads size rather than the file; and F3 with its bound removed admits
everything in both fields, so the bound is what does the work.

F3 admitting all 986 is weak evidence for F3. Its ceiling was read off this release's card, so
admitting this release's instances is close to circular, and what the result establishes is that the
card's statement is true of the data — a verification of the object's own documentation rather than a
finding about cores.

## R715 · Whether any per-instance predicate separates, and whether it is clause F1

R714 established that the release ships 986 core instances and that only the size clause can be
evaluated on them, where it admits every one. R715 asks whether any per-instance predicate separates
at all.

The size clause's instance form is **degenerate** over the 986: one distinct value, admitting
everything. A provenance predicate is not. The share of a core's criteria appearing verbatim in its
own full rubric has mean **0.0655**, ranges from zero to one across seven distinct values, and
**794** of the 986 conversations have **zero** overlap, with exactly **one** core drawn wholly from
its rubric.

So the released cores are written fresh rather than selected from the full rubric. That is what the
retired clause about being drawn from a rubric asserted, and it had never been measured per instance.
The negative control puts the same overlap against a different conversation's rubric at **0.0000**,
so the figure is a property of the pairing rather than of criteria vocabulary in general, and the
sweep over three matchings — verbatim, casefolded, and a forty-character prefix — runs 0.0655, 0.0778
and 0.1777 on the own-conversation comparison while the shifted control stays at 0.0000, 0.0000 and
0.0003. Verbatim is the strictest matching, so a looser one can only raise the overlap, and the sweep
bounds the answer from both sides rather than reporting a single cell.

This predicate is **not** clause F1, and the preregistration said so before the run. F1 concerns
criteria selected without reading the outcome labels; the full rubric is not the labels, and the
labels do not appear in that file. Naming the predicate as a restatement of F1 would substitute a
label for a description. F1 therefore remains without an instance form, and of the three clauses one
has a degenerate instance form, one has none, and the separating predicate that does exist belongs to
neither.

Separating is not being right. Whether this predicate is the one a definition of core should use is
construct validity and is impossible at this site.

## R716 · What the provenance statistic can and cannot resolve

R715 found a per-instance predicate that separates: the share of a core's criteria appearing verbatim
in its own full rubric. R716 prices what that share can support, because a quantity that varies is not
thereby a quantity that resolves.

The share is quantised. With criteria counts of two, three or four, the ratio can take exactly seven
values — zero, a quarter, a third, a half, two thirds, three quarters and one — and that count is
forced before any data is read rather than observed. All seven do appear, which is the measurement.
The smallest non-zero value a single instance can take is **0.2500**, against a population mean of
**0.0655**: a ratio of **3.82**. So no single instance can express a value near the mean, which is
carried entirely by the minority that overlap at all.

The group mean, by contrast, is resolvable. Its bootstrap standard error over four thousand five
hundred resamples is **0.00469**, with a ninety-five percent interval of 0.0566 to 0.0749, and the
minimum detectable difference for an even split of the 986 is **0.040** — below the quantum. A
between-group difference smaller than one instance's smallest step is therefore detectable in
aggregate while a per-instance reading of the same statistic is not a fine measurement of anything.
That is the distinction R705 had to make for the gain statistic, and it is the second time in this
campaign that a statistic has been precise in the mean and coarse in the unit.

Controls: a planted shift of one tenth is detected at unity, with a no-shift floor of 0.07 and a
maximal-shift ceiling of 1.00, so the eighty-percent target lies strictly inside a real band; a shift
of exactly zero rejects at 0.07 against a two-alpha bound of 0.10; shuffling the group labels at
fixed sizes gives a ninety-five percent interval of minus 0.0171 to plus 0.0181, containing zero, so
no split of these instances shows a difference by itself; and the same question asked of the full
rubric against itself, which is identically one, returns a bootstrap standard error of exactly zero,
which is what the machinery should return when there is nothing to resolve.

No analysis choice can improve the quantum. It follows from the release's own bound of at most four
criteria per core, so only a release shipping larger cores could reduce it. The raw match count,
swept as the other side of that bound, has a minimum detectable difference five to seven times worse
and degrades as the split becomes uneven, while the share's does not.

## R717 · Why the k-split of the provenance share is biased, and what it can bound

R716 closed by proposing that the provenance share be compared between the cores carrying four
criteria and the forty-four carrying two or three. The share is the match count divided by the
criteria count, so that split conditions on the statistic's own denominator, and the groups do not
share a support: four criteria admit zero, a quarter, a half, three quarters and one, while two admit
only zero, a half and one.

The bias therefore has a sign that can be derived before any data is read. At the same match count of
one, the share is **0.2500** at four criteria and **0.5000** at two, so identical counts force a
higher share in the smaller group. The bias pushes the small group up.

Measured, the small group is **lower** on both statistics — **−0.0131** on the share and **−0.1052**
on the raw count — so the observed direction runs against the bias, which would make it informative
in principle, since a biased comparison landing opposite to its bias understates rather than
manufactures.

None of it is readable. The minimum detectable difference at the true forty-four against
nine-hundred-forty-two imbalance is **0.080**, exactly twice the even-split figure of 0.040, against
an observed absolute difference of **0.0131**. Zero of six specification cells survive their own
permutation null. So the caution R716 attached to its own proposal was correct: an even-split minimum
detectable difference does not carry over to a group of forty-four, and the question remains
unanswerable at this site.

The bias cannot be analysed away. Every share with the criteria count in its denominator inherits it,
and only the raw match count avoids it, at a resolution five to seven times worse.

## R719 · Whether the falsifier verdict against clause three survives its own population

R718 certified two blocks on the statement as standing unamended, one of them the finding that the
standard's falsifier does not fire against clause three. R719 asks what that finding was computed
over.

Its population is the five-arm literal that R689 retracted one round after it was written. The
finding reads that the three published arms outside the clause's extension all fail clause two
anyway, and those three — topabs_k4, topvar_k4 and topwvar_k4 — are three of the four arms R689
showed the release does not name. The release's card names **one** of the five, and at a population
of one the test cannot be run at all: it requires a set of published arms outside the extension, and
the corrected set contains none.

So the block is downgraded to **unevaluable** rather than refuted. The clause itself is not shown to
be decoration: over R360's forty-two arms it excludes thirty-seven, and four that clause two does
not. What falls is the evidence R688 offered for it.

The instrument R718 used could not have seen this. It computed amendment as a round cited in a
block's body outranking the highest round cited in its heading, and R688's block cites only R683 and
R688 — the retraction lives in a different block entirely. Measured across the statement, **two of
the three** blocks touching the retracted literal never cite the retracting round, and both are the
blocks R718 reported as standing. An amendment test scoped to a block cannot see a retraction filed
elsewhere, so the earlier count is an overcount.

The round's own positive control caught a defect of the same shape before any verdict was printed.
Its first version reconstructed the clause's extension from a sibling round's formula, which admits
the three arms R688 excludes; the recomputation returned an empty list against R688's committed
three, the control failed, and the round printed unverified. Reading the extension from R688's own
committed artifact fixed it. Auditing a round means using that round's object rather than a sibling's
algebra.

## R720 · Premise or contrast, and what the deliverable still asserts

R719 closed by proposing that a retraction anywhere on the statement reaches every block citing the
retracted literal. Applied literally that rule leaves a residue of zero, and it is too coarse.

The lineage block cites the retracted five-arm literal in order to distinguish its own object from
it. Its "number 5" is clause three's extension — coval_core, topw_k3, topw_k4, topw_k6, topw_k8 — and
the sentence containing the literal reads that five other five-member arm sets are committed in this
corpus and denote other objects. A block that cites a retracted literal to say it is not that does
not rest on it.

Measured across the twelve claim blocks, three cite a retracted literal: one as a premise, which is
R688's falsifier block already downgraded by R719; one as a contrast, the lineage block; and one as
the retraction itself. The role-aware residue is therefore **one** block, against **zero** under the
naive rule, so the naive rule over-kills by one.

The real defect in the surviving block is smaller and still real. It glosses the literal as CoVal's
publication list, the exact description R689 retracted, without citing R689. That is a defect in the
prose rather than in the claim, and it has been corrected on the statement to name the list as
retracted with the retracting round cited. Conflating a stale gloss with a compromised claim is the
over-kill this round exists to prevent, and it is the mirror of R719's finding: there a retraction
reached a claim nobody had connected to it, here a retraction reaches only a phrase.

Controls: the reading classifies R688 as premise and the lineage block as contrast, two roles that
can be stated independently of it; blocks citing no retracted literal return no role rather than a
default; the block recording the retraction reads as the retraction rather than as a victim of
itself; and removing the contrast markers flips the lineage block to premise, so the markers are the
ingredient.

The round's own first residue was wrong. It computed asserting-and-not-premise and returned three,
counting two blocks R718 had already found amended by later rounds, so the registered point would
have landed inside its interval for the wrong reason. A new criterion is a conjunct rather than a
substitute, and with the earlier amendment test restored the residue is one.

## R721 · Whether the six independent computations are six independent evidences

The one block on the statement that no later round has undermined asserts that the number five is
supported by one identified set with a named producer and by at most six independent computations.
R721 asks what independent means there, since the block does not say.

R680's six derive the set with no member literals in executable source and without reading a prior
round's results file. That is independence from copying. It is not independence of source, and R678
names the extension's unique producer as R294's census with R294 itself among the six, so six
programs computing the same predicate over the same data would agree by construction.

Measured, they do not share one source. The six read **eleven** distinct upstream files. The
registered prediction was two, so the round's directional failed by a factor of five, and that
failure is its most useful output: an attack that fails is evidence about the claim, and this is the
first block in this campaign to survive one.

The survival is qualified rather than clean. Three files are read by more than one deriver, the
clause ledger by four of the six, and all six read at least one shared file. They are eleven files
with three in common rather than six disjoint evidences, and the block's phrase at most is precisely
what makes it survivable. A negative control puts six randomly chosen rounds from the same arc at
fifteen, fifteen and fourteen distinct sources against these six's eleven, so the derivers are
slightly more convergent than the corpus and not dramatically so.

The block had also already made the naive attack against itself, calling its own number a ceiling
twice over and noting that absent literals remove one way of copying rather than all. A block that
names its own ceiling twice cannot be killed by pointing at the ceiling, and the only live attack
remaining was on the meaning of independent, which the measurement answered in the block's favour.

## R722 · Whether the shared file is a shared input

R721 measured that four of the six derivations behind the number five read the same file, the clause
ledger. R722 asks whether they read the same part of it, since two rounds taking disjoint fields from
one file share a path and no data.

All four readers parse, and they share four fields. The clause-two-and-three admission list is read
by three of the four; the clause-two admission list, the sweep and the criteria count by two each. So
the sharing is not nominal: two of the six derivations take the same field from the same file, which
is a shared input rather than a shared path, and R721's description of eleven files with three in
common as not-disjoint evidences was right and understated.

The probe run while writing the previous round's closing line was an uncontrolled search. It returned
fields for two readers and nothing for the other two, which is silence rather than zero, and
reporting those as reading no fields would have been a fabricated absence. This round replaces it
with a pattern ladder, reports coverage as a first-class number, and treats unmeasured as a value
distinct from zero that the two branches never print alike. With the ladder all four parse, so the
registered prediction that coverage would be incomplete failed, which is the right way for that
prediction to die.

The round's negative control also had to be repaired. It required the extractor to recover at least
three schema fields from the round that writes the ledger, and the ceiling is two: that round builds
its dictionary from variables, so only two of fifteen schema keys appear as string literals anywhere
in its source. The control could not pass and the round printed unverified. The repair computes the
band — floor zero, ceiling two, threshold one — rather than lowering the number, because recovering
any schema field from the writer is what the control exists to show. A threshold that is picked is a
guess; a threshold that is computed is a control.

## R723 · the ceiling on independent computations is one, not six

The count of independent computations behind the extension was measured again at the unit the claim
is about. Of the eight rounds that derive the set without carrying its members as literals, seven
read a prior round's artifact, and the round that certified the earlier bound found two of those
seven, a recall of 0.2857. The corrected ceiling on independent computations is therefore one, and
that one is the round that produced the set. The earlier instrument searched executable source for
the substring results-slash or a round directory followed by a slash. A path assembled from pathlib
operands places quotation marks and spaces between its segments, so neither substring occurs, and
the search was invariant under a rewrite that the property it stood for is not. The five rounds it
missed are exactly the five that build their paths from operands, and the two it found are exactly
the two that write the path inside a single string, so the partition is complete in both directions.
A strict specification requiring every cross-round reference to sit inside a path-shaped literal
returns the same seven, which is what makes the count reportable rather than an artifact of a loose
pattern. The bound remains a ceiling and not a count, because reading an artifact is measured here
and using its value is not.

## R724 · the producer could have returned otherwise, and the released core is not invariant

The single computation the deliverable rests on was tested for whether its answer was forced. Over
the decision-rule space of the producer's own procedure — five defensible readings of each measured
clause, the provenance clause on or off, and the k-capped arms kept or dropped, one hundred cells in
all — six distinct extensions are reachable and the released set of five is the answer in thirty of
them, which is the modal cell and the answer of fifteen of the twenty-five rule combinations with
the provenance clause on. So the producer is a measurement and not a derivation, and the arc's one
independent computation stands as one rather than collapsing to zero. Two further facts belong with
that number. Every reading that requires the whole interval of the second clause to sit above the
design's resolution excludes the released core itself and leaves a single arm, topw_k6, admitted
alone; the released core's second-clause interval runs from 0.008274 to 0.024117 against a minimum
detectable effect of 0.010616, so its point estimate clears resolution while its lower bound does
not. Membership of the core in its own extension therefore rests on reading the clause as effect
above resolution rather than interval above resolution, and that is a choice. Second, the axis
dropping k-capped arms changed nothing in any of the fifty rule combinations, so it is an axis that
could not have moved the answer and is reported as such. The count of six is a lower bound: the
bootstrap seed, the number of resamples, the multiplicity level and the annotator filter are fixed
inside the persisted artifact and would need the census re-run to vary.

## R725 · the rule space is one statistic with four thresholds, and the core's exclusion is not noise

The five readings of a measured clause swept in the previous round are not five criteria. The
minimum detectable effect is the effective z multiplied by the sample standard deviation over the
root of the sample size, and the interval is a percentile bootstrap of the same mean, so every
reading is a threshold on the ratio of the effect to its standard error. The point reading is that
ratio above zero, the interval reading above 1.959964, the resolution reading and the round's own
conjunction both above 2.801585, and the strict reading requiring the whole interval above
resolution is that ratio above 4.7615. Four thresholds carried by five labels, and the conjunction
is identical to the resolution reading whenever the effect is positive. That is algebra and not
evidence. What is evidence is that the equivalence holds on the artifact across four hundred and ten
checks with no disagreement, even though the bootstrap and analytic standard errors differ by up to
seven percent, which means no arm sits close enough to a threshold for that discrepancy to change a
verdict. The consequence for the previous round is that its hundred cells contain at most sixteen
distinct rule pairs of twenty five, so its coverage was narrower than its cell count suggested.
Separately, the exclusion of the released core under the strict reading was tested for whether the
minimum detectable effect's own sampling error could move it. The core's ratio is 4.2336 against a
threshold of 4.7615, a gap of more than eight sampling standard deviations of that quantity at a
sample size of nine hundred and sixty eight, and the crossing probability is zero at every seed. The
exclusion is a property of the arm. The crossing probability assumes the per-prompt differences are
normal, which this artifact cannot check; the distance in sampling standard deviations does not.

## R726 · the collapse is structural, and the check that established it was smaller than it looked

The previous round found no disagreement between the interval-based admission rules and the
threshold on the ratio of effect to standard error, and left open whether that zero was a property
of the rules or of where these particular arms happen to sit. It is a property of the rules. The
ratio of the two standard error estimates runs from 0.9478 to 1.0691 across eighty two cells, and
the interval of the statistic within which the two constructions can disagree is 0.237796 wide at
the interval reading and identically wide at the strict reading, the equality holding by algebra
because both boundaries move with the same coefficient. No cell falls inside either interval and
none would change verdict at the adverse end of the observed range. A dose response multiplying the
spread by nought, a half, one, two and four gives widths that are monotone and exactly zero at
nought, with the first occupancy appearing only when the spread is doubled, so the design's
resolution is stated as a factor rather than asserted as safety. Two qualifications belong with
this. The range used is a minimum and a maximum over eighty two draws, which are extreme order
statistics; the fifth to ninety fifth percentile range gives 0.172352, and the difference between
those two spreads is the floor. And of the four hundred and ten checks the previous round reported,
only one hundred and sixty four had a boundary that could move at all, because three of the five
readings never touch the interval estimate; the other two hundred and forty six could not have
disagreed however the data fell. The zero stands, over a failable population smaller than the one
it was quoted against.

## R727 · the disagreement zone is a resample count, and one skew test had no power

The spread that sets the previous round's disagreement zone was attributed. It is not a property of
the arms. A synthetic normal world at a sample size of nine hundred and sixty eight with twelve
hundred resamples, containing no skew and no arm-to-arm variation of any kind, reproduces a standard
deviation of the ratio of 0.027699 against the observed 0.027341, and an asymptotic derivation from
the sampling error of a bootstrap percentile independently gives 0.027821. Two routes, one answer.
Sweeping the resample count over three hundred, twelve hundred, four thousand eight hundred and
nineteen thousand two hundred gives a fitted log-log slope of 0.4951 in magnitude and negative in
sign, which is the half-power of Monte-Carlo error. So the zone narrows when the resample count
rises, and the previous round's statement that the spread would have to double describes a constant
chosen in the producing round rather than anything the data does. Two further findings belong here.
The correlation between the ratio and the interval's asymmetry is an underpowered detector of skew
at this resample count: planting real skew moves it by less than three standard deviations of its
own seed spread at twelve hundred resamples while moving it clearly at nineteen thousand two
hundred, so a null from it is silence. On the statistic whose power is established by the positive
control, the mean asymmetry, the observed cells give a value of minus 0.00410 with a standard error
of 0.00296, which is one point four standard errors from zero skew and nine point four from the
planted skewed world, so these cells carry no detectable skew by a powered test. And the sample size
cannot be tested at all: it takes two values across the arms with four of eighty two cells at the
minority level, which is an unidentified covariate and is recorded as unidentified rather than as a
null.

## R728 · the census reproduced from the object, and its population is a directory glob

The producing round's census was re-run from the saturation store rather than read from its summary,
which no round in this arc had done. Its committed verdicts are reproduced on all forty one arms
exactly. Raising the resample count sixty four fold, from twelve hundred to seventy six thousand
eight hundred, changes no admission and leaves the extension identical, and neither does changing the
bootstrap seed across five values at the shipped count, with the seed verified to move the draws.
The largest movement of any interval bound across the whole sweep is 0.001408. Most of that outcome
is forced: the minimum detectable effect does not depend on the resample count, only the lower bound
does, and the one cell within Monte-Carlo reach of its own boundary, at a ratio of 2.1458, is already
excluded by the count-invariant half. What is not forced is the reproduction itself, and that is what
this round establishes. Separately, and found by the failure of the round's own anchor rather than
registered in advance, the census defines its population by a glob over a results directory that
later rounds write into. That directory held forty one usable arms when the census was committed and
holds ninety two now, and re-running the same procedure over today's population admits sixteen rather
than five. The additional arms were built by later rounds for other purposes and their admissibility
is a separate question, so this is not a correction to the extension. It is a statement about the
procedure: the same code returns a different answer depending on when it is run, because its
population is not fixed by anything the definition says.

## R729 · the provenance clause is a blocklist and admits by default

The third clause requires the evaluation annotator to be held out from the core's own construction.
It is implemented as a set of four literal arm names. The selection program loads the human target
for exactly three of its rules, and any arm built by one of those rules is an object the clause was
written to exclude. Of the sixteen arms today's population admits, seven are built by such a rule and
the clause excludes none of them; across the whole population thirteen target-reading arms pass by
default. The clause excludes exactly and only its four literal names. Two independent routes agree on
every one of the eighty two arms both can classify, with no disagreement: one parses the tag the
builder emits from the rule, the size, the seed and the fit parity, and the other compares the
selected criteria per prompt and never sees a name. Both re-derive the four names the census already
knew, from construction rather than from the list, which is what makes the rest readable rather than
circular. Six arms carry no rule prefix because the selection program never emitted them; they are
reported as single-route and the one called target-reading by that single route is marked
uncorroborated and excluded from every count. None of this says those arms leak into the evaluation,
which is a question settled elsewhere and not re-opened. It says the clause never asks. The defect is
structural rather than clerical: an arm built after the census passes unless someone edits a literal,
so the clause's coverage decays with every round that adds an arm.

## R729 addendum · this finding belongs to R520, and what is new is that the defect is now realised

The blocklist finding recorded above was established earlier, by the round asking whether the
provenance set is complete. That round used the same line of the selection program, the same
positive control recovering the four declared names from tags alone, and the same negative control
over the label-blind rules, and it named six of the arms the literal misses. The present round did
not check for it before building and found the overlap only when a gate refused an unrelated
citation. Three things survive as additions. The earlier round recorded that every arm it flagged
carried no third-clause verdict at all, because those arms sat outside the scored population; on
today's population seven of them are admitted, so what was latent is now realised. The universe has
grown from fifty six arms to ninety two, which adds a seventh admitted target-reader and takes the
population-wide count that the clause admits to thirteen. And the classification is now corroborated
by a route that never reads a name, comparing the selected criteria per prompt, which agrees with the
tag route on all eighty two arms both can classify -- a corroboration worth having because the
earlier round's own record notes that a keyword search on this same question failed nineteen times
out of nineteen. The headline is the earlier round's.

## R730 · the seven admitted arms are four objects, and the clause already excludes one of them

The previous round's count of admitted target-reading arms was over tags. Resolved to objects by
exact per-prompt satisfaction-vector identity, the seven tags are four objects. One of those objects
carries a tag the provenance clause names, so the clause excludes it; what it fails to do is
recognise two further tags of the same object. The clause therefore admits three distinct
target-reading objects rather than seven, and the defect is real but smaller than both the round that
found it and the round that restated it claimed. Today's ninety three tags partition into eighty one
objects across eight multi-tag classes, and the partition is identical at every tolerance tried
because the smallest non-zero difference anywhere in the population is 4.762e-02, far above any
floating-point threshold, so exact equality is not a knife-edge choice. Computed from the same
partition though not registered in advance, the population-wide count of thirteen tags resolves to
ten objects of which the clause admits nine. The unit error is the third of its kind in three
consecutive rounds — a denominator the design could not return, a nine-way rule where the claim was
binary, and now tags where the claim is objects — and this one ran in the flattering direction,
inflating a defect attributed to someone else's definition.

## R731 · two of the three admitted objects carry the excluded object's size, and the third does not

The three target-reading objects the provenance clause admits were compared, at the object level with
each object counted once, against the object the clause excludes and against the four label-blind
arms, on both measured clauses. The greedy object's second-clause margin is 0.072210 and the
independent object's is 0.052679, against the excluded oracle object's 0.077867 and a label-blind
mean near 0.0169, with the released core at 0.016042. In units of the spread among the label-blind
objects, which is 0.003122 on the second clause, the greedy object sits 1.81 from the excluded object
and 17.71 from the blind group, and the independent object 8.07 against 11.45. Both sit with what the
clause excludes, on both clauses, and the two clauses agree on the nearest group for every object.
The third admitted object does not. It is built by the oracle rule and named for it, and its
second-clause margin is 0.014483, a ratio to its own minimum detectable effect of 1.04 against the
excluded oracle object's 7.29; it sits 0.78 spreads from the label-blind group and 20.30 from the
oracle. So construction and behaviour come apart, and a predicate over construction alone — which is
what the two preceding rounds proposed as the remedy — would exclude an object that behaves like the
ones the definition accepts. The mean distances to the two reference groups, 0.0314 and 0.0312, are
indistinguishable precisely because that third object drags the mean across, which is why the
per-object table in spread units is the reportable form and the two means are not. This compares
outcomes and not mechanisms: a margin near the excluded object's does not establish that the same
construction produced it, and establishing that would require an intervention this site cannot run.

## R732 · the third admitted object differs in two ways at once, so its cell carries nothing

The comparison that placed the third admitted object with the label-blind arms mixed two factors. That
object and the excluded oracle object select identical criteria on only 0.0888 of their 968 shared
prompts, against a floor of 1.0000 that every same-object tag pair in the partition returns, so the
selection genuinely differs; and their per-cell satisfaction agreement is 0.0354, with an earlier
round having established that the suffixed family is scored by an emitter foreign to the default one.
Their margin gap is therefore a sum of a selection effect and an emitter effect and neither term is
identified from the gap. No arm on disk carries the third object's criteria under a default-emitter
score, so the design that would separate them does not exist at this site. The reading drawn from
that cell — that construction and behaviour come apart — is withdrawn to unverified. It is not
refuted, and unverified is not an acquittal in either direction, so the proposal that the provenance
clause needs a predicate over construction returns to untested rather than being restored. Two things
are untouched. The greedy and independent objects both sit with the excluded object on both clauses
and both are scored by the default emitter, so that comparison mixes no instruments. And the rule
name is a poor proxy for construction, which is now measured directly at 8.9 percent selection
agreement between two arms that share a rule, rather than inferred from a margin.

## R733 · the two admitted objects move with the excluded one, prompt by prompt

The question left standing was whether the two admitted target-reading objects merely land at the
same level as the object the provenance clause excludes, or share its per-prompt structure. They
share it. Against a shared-subtrahend floor of 0.5034, computed in this round's own units from three
pairs of random-selection arms that have no shared mechanism, the greedy object's per-prompt margin
correlates with the excluded object's at an excess of 0.4632 and the independent object's at 0.3965,
against excesses of 0.1592 and 0.1966 toward the label-blind arms. The two measured clauses agree on
the ordering, and all forty eight cells of the grid survive a Benjamini-Hochberg correction over the
whole grid. The precondition was established elsewhere: the per-prompt gap is reliable, with a
split-half value of 0.8311 against a shuffled null of 0.0168, so this is not a correlation of noise.
Three limits attach. Correlation of outcomes excludes unrelatedness and cannot identify a shared
mechanism; that needs an intervention on the construction. The floor is essential and not decorative,
because every margin here subtracts the same baseline arm, so a large raw correlation is guaranteed
before any mechanism is shared. And the raw correlation of 0.9747 for the greedy object exceeds the
attenuation ceiling that the reliability estimate implies, which means that estimate does not
transfer to these arms or the shared subtrahend inflates past it; the disattenuated column is
therefore a diagnostic and not a correlation.

## R734 · the floor the previous round used was too high, so its excesses were understated

The floor against which the previous round measured profile similarity was built from pairs of
random-selection arms. Those arms share the subtrahend and they also share whatever structure their
common selection pool imposes. Isolating the subtrahend by re-pairing one arm's own contribution to
prompts at random, while leaving the subtrahend aligned, gives a floor of 0.3062 against the
random-arm value of 0.5034, a difference of 0.1972 which is more than ten times the seed spread of
0.0190. So the random arms do carry structure beyond the subtrahend, the floor used was too high, and
the excesses reported were understated rather than inflated. Re-scoring the previous round's
comparisons under both floors changes neither verdict: both admitted objects sit with the excluded
one either way, so the ordering never depended on the choice. Two limits. The difference names a
magnitude and not a cause; attributing it to the selection pool would require an intervention on that
pool. And the design the previous round proposed for this measurement would have measured nothing,
because re-pairing the margin destroys the subtrahend's alignment along with the arm's own signal and
collapses to a null that round had already run under another name — established by algebra before any
compute was spent.

## R735 · the floor depends on how many criteria the compared arms share

The floor used in the two preceding rounds was a single number built from three pairs of one size
family. Measured across one hundred and fifty three pairs of random-selection arms spanning six
selection sizes, the floor tracks the criteria the two arms actually share, at a correlation of
0.9264, rising from 0.4003 where arms select two criteria to 0.8438 where they select twelve. The
size-matched floor for the four-criterion arms the definition's comparisons involve is 0.6458. That
reverses the direction of the previous round's correction: measuring against a floor that strips all
overlap gave 0.3062 and suggested the excesses were understated, but the arms being compared all
select four criteria, and two unrelated four-criterion arms already reach 0.6458, so for the
comparison that matters the floor was too low and the excesses were overstated. Both admitted objects
still sit with the excluded one under every floor tried; the margins halve. Two limits. Overlap rises
with selection size by construction and each same-size stratum holds three pairs, so this design
cannot separate a floor that depends on overlap from one that depends on size, and the within-stratum
test is underpowered rather than negative. And the pool size used to predict overlap is the union of
observed selections, a lower bound, which biases the prediction upward and explains why measured
overlap is 0.9694 of predicted rather than equal to it.

## R735 addendum · the corrected excesses at the size-matched floor

Re-read against the size-matched floor of 0.6458 rather than the 0.5034 previously used, the greedy
object's excess toward the excluded object is 0.3289 and toward the label-blind arms 0.0989, and the
independent object's are 0.2781 and 0.1311. Both orderings are unchanged from every earlier floor and
both margins are roughly halved. These four values are the ones the statement carries and they are
recorded here so each resolves to this round rather than standing alone on the deliverable.

## R736 · the deferred experiment is a reanalysis, and the finding that led there was an indexing error

The previous round declared that separating overlap from selection size requires a new selection run.
It does not. Satisfaction scores are stored per prompt, criterion index and response letter, and
joining arms on prompt, response and criterion text shows the score to be a function of that triple
to 0.997357 across one hundred and ninety key-sharing pairs. A median of fifteen distinct criteria
carry a score on each prompt and nine hundred and seventeen of nine hundred and sixty eight prompts
carry at least eight, which is enough to assemble two four-criterion arms at any chosen overlap from
zero to four; the reachable prompt counts at those five targets are nine hundred and seventeen, nine
hundred and forty eight, nine hundred and sixty four, nine hundred and sixty five and nine hundred
and sixty eight. So the deferred experiment is available without asking the judge anything new. The
route to that conclusion began with an inverted index: reading the response letter as the criterion
position produced an apparent eighty five percent inconsistency, which would have said the judge's
score depends on which other criteria share the set. The scoring source builds one judge call per
criterion, so that world was impossible by construction. The control that should have caught it did
not, because it compared two tags of a single object and the inversion cancelled on both sides; the
control that does catch it runs both joins and requires them to disagree, which they do by 0.851120.
A residual inconsistency of 0.002643 survives the corrected join and is real, since an earlier round
measured the scoring floor at exactly zero on identical criteria; it is bounded here and not
explained.

## R737 · the floor is a curve in overlap, and the compared arms sit on it

Assembling four-criterion arms from scores already on disk at a chosen number of shared criteria, on
nine hundred and sixty eight prompts held fixed across every target, gives a floor of 0.4244 where the
arms share no criterion, rising through 0.5654, 0.7076 and 0.8517 to exactly one where they share all
four. The construction is validated by a one-parameter model: writing the raw correlation of two
subsets sharing j of k criteria as a shared per-response component plus the independent part, fitting
that component at zero shared criteria alone gives 0.3385 and predicts the four remaining targets to
within 0.0046. The simpler form registered in advance, the ratio of shared to total, assumes the
per-criterion satisfactions are independent, and they are not, because a good response satisfies many
criteria at once; that prediction was wrong and the construction was not. Applied to the definition's
own comparison, the greedy object shares 2.8492 criteria with the excluded object and the independent
object shares 2.1095, so their matched floors are 0.8299 and 0.7234. Four floors have now been used
for this one comparison and only these are matched on the quantity that drives it. Two limits. The
floors for the comparison against the label-blind arms were not computed here, so the excesses are not
re-scored in this round. And this is a floor for random subsets of the scored pool; the real arms were
produced by rules that may prefer criteria with particular satisfaction profiles, and whether a
rule-produced arm behaves like a random subset at the same overlap would need a new selection run.

## R738 · matched on every side, the admitted objects fall below the floor rather than above it

The comparison the previous rounds left half matched was completed. Each side is now read off a curve
built for its own pair of selection sizes rather than one curve for all, because three of the four
comparisons cross sizes; the four curves give shared-component values of 0.3026, 0.3361, 0.3826 and
0.4007 and each is validated by fitting that component at zero shared criteria alone and predicting
every remaining target, with a pooled worst deviation of 0.0100. Against those matched floors every
one of the ten excesses is negative. The greedy object correlates with the excluded object at 0.8123
against a matched floor of 0.8299, and with the label-blind arms at a mean 0.1151 below their floors;
the independent object is 0.0638 below against the excluded object and 0.1212 below against the blind
arms. So the ordering reported earlier survives, with gaps of 0.0975 and 0.0574 against a band of
0.0151, but it is now a comparison of two shortfalls rather than of two excesses. The earlier reading,
that these objects track the excluded object beyond what shared selection explains, does not survive a
floor matched on measured overlap: they track it less far below expectation than they track the blind
arms, which is a weaker statement and the one the evidence supports. Every floor here is built from
random subsets of the scored pool, and the arms being measured were produced by rules; whether a
rule-produced arm should meet a random-subset floor at equal overlap is not identified at this site
and is precisely what the negative excesses now make the open question.

## R739 · the rules do not select higher-variance criteria, so the shortfall is not a population artifact

The previous round's negative excesses had one obvious candidate explanation: the floor is built from
random subsets while the arms measured against it were produced by rules, and the selection source
derives that a criterion whose satisfaction is identical across the four responses contributes nothing
to any pairwise comparison, so a rule fitting the human target should avoid such criteria and a random
subset should take them at the pool rate. Measured against the full candidate set, that is false. The
mean percentile rank of a selected criterion's across-response variance, whose null is one half by
construction, is 0.5028 for the excluded object, 0.4677 and 0.5318 for the two admitted ones, and
between 0.4925 and 0.4982 for the label-blind arms, while uniformly random arms return 0.5005 with a
seed spread of 0.0029. The instrument is validated by a known-answer case from the same source: the
rule that selects by this variance ranks first at 0.8528. Matching the floor on variance as well as
overlap therefore moves none of the ten excesses to zero or above; the magnitudes shrink and every
sign holds. So the shortfall is a property of the arms rather than of the population the null was
drawn from, and one candidate explanation is eliminated rather than confirmed. Eliminating a confound
does not name a cause, and the shortfall is now unexplained rather than explained away.

## R740 · nine of the ten shortfalls, and both orderings, are inside their own resolution

Three rounds reasoned about ten negative excesses and one tried to explain them without anyone having
measured what the design can resolve. Bootstrapping prompts and recomputing the correlation, its
overlap-matched floor and the overlap itself together on every resample, only one of the ten has a
ninety five percent interval excluding zero, and that one is the independent object against the
eight-criterion label-blind arm at minus 0.0556 with an interval from minus 0.1009 to minus 0.0116.
Both ordering gaps cover zero: 0.0396 with an interval from minus 0.0102 to 0.0904, and 0.0511 from
minus 0.0022 to 0.0995. The signs are not stable either — the greedy object against the excluded one
is plus 0.0211 under joint resampling against a point estimate of minus 0.0176 two rounds earlier,
which is the same fact as the interval covering zero arriving as a change of sign. So the ordering
that survived every floor does not survive its own resolution, and the honest report for nine cells
is a bound rather than a shortfall. The naive combination of the three uncertainty sources in
quadrature gives 0.0213 while the joint bootstrap gives 0.0162 and resampling the correlation alone
gives 0.0181, so the correlation and its floor move together and treating them as independent
overstates the width. The intervals are conditional on this criterion pool; pricing the pool itself
would need a second release.

## R741 · the two rounds ran on two populations, and the disagreement was the pool

The round that measured ten excesses and the round that priced them ran on different prompt sets
against different candidate pools. The first built its pool from the union of every arm's observed
selections, which a later round showed is a sample of the candidate set biased by the rules under
study; the second used the full candidate set, against which fewer prompts supply the twelve criteria
the widest comparison needs, so its population is seven hundred and thirty four rather than nine
hundred and sixty eight. The mean absolute difference this makes across the ten cells is 0.0857,
several times the bootstrap standard errors, and it is the whole of the disagreement between them. On
the corrected population the pricing round's point estimates reproduce within their own standard
error in every one of the ten cells, so those numbers stand and the ten excesses computed on the
union pool are withdrawn. What was wrong was the comparison between them: the difference was read as
a change of sign under resampling when it is a change of population. On one correct population, one
of the ten excesses excludes zero and neither ordering gap does, so the ordering remains unresolved
and the honest report is a set of bounds. Correcting the pool drops two hundred and thirty four
prompts, and because the criterion threshold is applied against the true pool that drop is a selection
on pool size rather than a random subsample; the surviving population is therefore not the release,
and both pool-size distributions are recorded rather than exchangeability assumed.

## R741 addendum · the one surviving interval, as this round computes it

The single excess whose interval excludes zero is the independent object against the eight-criterion
label-blind arm, at minus 0.0556 with a ninety five percent interval from minus 0.1008 to minus
0.0116 on the corrected population. The pricing round reported minus 0.1009 for the same lower bound;
the two runs differ in their bootstrap draws and the third decimal is the estimator's own noise, not a
disagreement. The value recorded on the statement is this round's, and both are within the
Monte-Carlo error each round reports.

## R742 · maximal power resolves nothing new, and two of the three quantities were never restricted

The previous round applied the widest comparison's criterion requirement, twelve, to every cell,
leaving seven hundred and thirty four prompts throughout. Each cell needs only four plus its own
reference size: seven, eight, eight, ten and twelve, which against the true candidate set give nine
hundred and fifty, nine hundred and nineteen, nine hundred and nineteen, eight hundred and fifty nine
and seven hundred and thirty four prompts. Recomputed at that maximal power the cell the arc turns on
rises from seven hundred and thirty four prompts to nine hundred and nineteen and its standard error
falls from 0.0162 to 0.0138, and its interval still spans zero. One of the ten excesses excludes zero,
the same one as before, and no cell resolves that did not. So the global threshold was not the binding
constraint and the bounds stand as reported. Separately, the scope worry that closed the previous
round applied to one of the three quantities rather than all three: the provenance clause is a name
lookup that consults no prompt, and the extension comes from a census computed on each arm's own
population, so neither is a function of the restricted set. The admission count is three and the
extension has five members, both without any prompt restriction. The per-cell figures are not
comparable across cells because each rests on a different prompt set, which is why the global column
is recorded beside them and why the ordering gap is left on the global population, where an average
across cells is defined.

## R743 · what the claim table's population constant actually rests on

**Question.** The four-row constants table declares one population — *"R294's 41 arms · 968 prompts ·
the 56-tag / 46-object census"* — for all ten claim rows. Do the rounds those rows cite establish that
population, and is the number a scope or a timestamp?

**Estimand, named before the method.** Among the rounds cited inside the ten claim rows, the fraction
whose `run.py` obtains its arm population by a live glob rather than by explicit enumeration.

**Identification.** From SOURCE, by `ast`. **Not** from artifact fields: across **465** artifacts a
population size is recorded under **19** distinct key spellings, the commonest (`n_arms`) covering
**35**. An instrument reading one key measures spelling. The gauge test killed that estimand before
any code existed *(ledger 991)*.

**Instrument.** The classifier is **reused** from `assurance/arm_population_is_derived.py`, whose
`ARM_NAMES` come from the arm store on disk rather than from a naming convention. Three detectors
sweep the one free choice — what counts as a population-bearing glob:

| detector | rule |
|---|---|
| `loose` | any `glob`/`iglob`/`iterdir`/`listdir`/`discover` call anywhere — **the existing gate's rule** |
| `medium` | a glob whose pattern literal contains `sat_` or `.npz` |
| `tight` | a glob whose pattern literal starts with `sat_` — the arm store's own pattern |

**The grid — 3 detectors × 2 populations, all six cells reported.** `f = DERIVED / (DERIVED + TYPED +
DECLARED)`, denominator fixed in the preregistration before any code.

| detector | population | DERIVED | TYPED | DECL | NO_ARMS | NONE | n with a population | f |
|---|---|---|---|---|---|---|---|---|
| loose | cited | 2 | 4 | 0 | 6 | 4 | 6 | 0.3333 |
| loose | complement | 49 | 38 | 1 | 262 | 53 | 88 | 0.5568 |
| **medium** | **cited** | **1** | **4** | **0** | **6** | **5** | **5** | **0.2000** |
| medium | complement | 26 | 41 | 1 | 262 | 73 | 68 | 0.3824 |
| tight | cited | 1 | 4 | 0 | 6 | 5 | 5 | 0.2000 |
| tight | complement | 25 | 41 | 1 | 262 | 74 | 67 | 0.3731 |

**The SHAM is the complement population — the ingredient ABSENT, not inverted.** The ingredient is
*being cited by a claim row*. Globbing is **more** common outside the cited set (0.3824) than inside
it (0.2000) at the same detector, so "the cited rounds glob" is not a property of the tree that the
citation inherits — it is a property the citation *lacks*.

**Registered against measured.**

| | registered | measured | |
|---|---|---|---|
| P1 distinct rounds cited | 17 [12, 24] | **18** | ✓ |
| P2 glob fraction, medium | 0.60 [0.30, 0.90] | **0.2000** | ⛔ **outside the band, low side** |
| P3 cited derived globs returning ≠ 41 today | ≥ 1 | **1 of 1** | ✓ |
| P4 detector agreement per round | ≥ 0.70 | **15/16 = 0.9375** | ✓ |
| D directional: derived rounds spread across eras | true | **false** — there is exactly one | ⛔ |

**Controls — 5 PASS, 0 FAIL, both after repair.**

| control | returned |
|---|---|
| **POSITIVE** | `R728 → DERIVED`, `R477 → TYPED`. Band **computed**: floor 0 DERIVED, ceiling 16 parseable cited rounds, threshold 2 — `0 < 2 ≤ 16` |
| **g=0** | a source with no arm code → `NO_ARMS` — unknown, never a silent class |
| **NEGATIVE** | every glob call deleted from R728's source, everything else kept → `DERIVED → TYPED`. Excludes *"the classifier fires on any file"* |
| **PLACEBO** | 410 `README.md` → **0 DERIVED**, reported as **0 of 410** and not 0 of 0; 21 of them mention an arm artifact in prose, so the detector was pointed at a real population |
| **UNIT** | 0 cited rounds map to >1 `run.py`; the 2 mapping to **zero** are named (`R580`, `R581`) and excluded from every denominator by construction |

**⛔ Both repaired controls had failed for their own reasons** *(ledger 993)* — the positive control's
second case expected `R719 → TYPED` when R719 loads no arm artifact at all, and the unit control
demanded exactly one source file per round when codeless rounds are a known category here.

**⛔ The confound is UNCONTROLLED, and the script now says so** *(ledger 994)*. Written before the run:
class might be a function of ERA rather than of the claim. With `|DERIVED| = 1` and `|TYPED| = 4`,
separability of the two round-number sets is **forced** — a single point is separable from every set —
so the computed `true` was algebra, not evidence. It prints `UNINFORMATIVE`.

**Verdict.** `WORLD A` on the registered threshold (`f ≤ 0.25`): the constant is a scope for the rows.
**But the shape none of the three worlds named is the finding**: the constant's *source* is derived and
expired (`sat_*.npz` → **101** today vs the stated **41**) while its *inheritors* are stable, and **11
of 16** cited rounds with code name no arm population in their own source — **6** naming no arm
artifact and **5** naming one without a classifiable population.

> ⛔ **CORRECTED BY R744** *(ledger 995, 996)*. This paragraph first read *"establish no arm population
> at all"*, and the block above reported the 6 as a count. Following named cache edges, **5 of the 6
> reach the arm store**; only `R558` does not. **The 6 is an upper bound on a FILE-level property, and
> the sentence asserted a ROUND-level one.**

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 12345, **both writes confirmed to disk
before the comparison ran**. No rng in the design.

## R744 · is `NO_ARMS` a measurement or silence? — the bound on R743's central count

**Question.** R743 reported 6 cited rounds as `NO_ARMS` — loading no arm artifact — from a **regex over
each round's own file**. Its positive control validated the `DERIVED`/`TYPED` split *among rounds that
already pass that gate*, and never asked whether the gate can MISS.

**Estimand.** Among those 6, how many reach the arm store through a static path the flat regex cannot
see (a local import, or a cache written by a store-reading round).

**Identification — PARTIAL, so the answer is a BOUND.** Transitive closure only ADDS reach, so it
lower-bounds the reachers and upper-bounds `NO_ARMS`. Non-reachability is not establishable statically.
R650 already measured the general resolution question undecidable (**172 of 364** read sites resolve);
this round asks only the binary a bound can answer.

**The grid — 4 levels × 3 populations.**

| level | NO_ARMS(6) | all cited(16) | complement(404) |
|---|---|---|---|
| **L0** own file *(= R743's detector)* | **0/6** | 10/16 | 142/404 |
| **L1** + locally imported modules | **0/6** | 10/16 | 145/404 |
| **L2 tight** + caches naming their round dir | **5/6** | 15/16 | 165/404 |
| ⛔ L2 loose *(uncontrolled, for contrast)* | 6/6 | 16/16 | 259/404 |

⛔ **`L0 ≤ L1 ≤ L2` is FORCED** — each level is a superset. **A derivation.** Only the gain is measured.

**Per round.** `R519, R520, R529, R530, R534` gain at L2-tight; **`R558` does not.**

**Registered against measured.**

| | registered | measured | |
|---|---|---|---|
| P1 reach at L1 | 2, band [0, 5] | **0** | in band, point wrong |
| P2 reach at L2 tight | 3, band [0, 6] | **5** | in band, point wrong |
| P3 L0 reproduces R743 | 16/16 (hard) | **16/16** | ✓ |
| P4 cited rounds with an import edge | ≥ 5 | **8** | ✓ |
| **D** gainers carry an import edge | true | **false** | ⛔ mechanism refuted |

⭐ **The directional failing is the finding.** Imports contribute **0** to the gain in every cell; the
tree shares data through **artifacts**, not through code.

**Controls — 6 PASS, 0 FAIL.**

| control | returned |
|---|---|
| **POSITIVE** | R294's `sat_` literals moved into an imported constant → flat goes **blind**, L1 still reaches; refactor **asserted to parse**; band computed `True → True` |
| **g=0** | a store-free helper adds **no** reach — the detector counts data, not edges |
| **NEGATIVE** | import graph emptied → L2 equals L0 on **16/16** exactly |
| **SHAM** | ingredient **absent**: L1 gain on the 8 import-free cited rounds = **0** |
| **PLACEBO** | L0 recomputed differs by exactly **0** |
| **P3** | L0 is R743's instrument, not a lookalike |

⛔ **Both of this round's own instruments were broken first** — a positive control whose refactor did
not parse *(ledger 997)*, and an L2 cache detector matching by basename across **155** round
directories, which would have printed **6/6** *(ledger 998)*.

**What it retracts.** R743's *"11 of 16 never load an arm artifact"* → **6 name none + 5 name one
without a classifiable population** *(995)*; the 6 → **an upper bound**, ≥5 of 6 reach the store
*(996)*; `NO_ARMS` as a round property → **a file property**.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 99, **both writes confirmed to disk**
before the comparison ran (3384 and 3385 bytes, differing only in the recorded seed).

## R745 · are the added arms candidate cores, or our own apparatus?

**Question.** R728 measured the census admitting **16** on today's 92-arm store against **5** on the
committed 41, and called it a scope condition. Its residue, verbatim: *"whether R294's construction is
the right one is not addressed here."* Are the added arms candidate cores at all?

**Estimand.** The class composition of the 51 arms present today and absent from the committed 41, and
separately of the 11 newly admitted, under a partition **read off the builder**.

**Identification — from `corebench/select_core.py`, asserted at runtime.**

| line | establishes |
|---|---|
| `:50-52` | the rule vocabulary is a closed set of **nine** |
| `:102` | `if a.rule in ("oracle_k", "indep_k", "greedy_k"):` **loads the human target** |
| `:204` | the tag is **emitted by the builder** from rule + k + seed + fit-parity + `tag_suffix` |

⇒ **TARGET-READING** `oracle_k · indep_k · greedy_k` · **RANDOM** `random_k` · **CEILING** `full` ·
**SELECTOR** `topw_k · topabs_k · topvar_k · topwvar_k`. The round **exits 2** if the source does not
carry all three assertions.

⚠ **Gauge bound.** A name is invariant under renaming while the property is not, so name
classification is blind **in general**; it is admissible here **only** because `:204` emits the tag
from the rule. Non-parsing tags return **`UNPARSED`**, never a class.

**The grid — 3 classifiers × 3 populations.**

| classifier | population | SEL | TGT | RND | CEIL | UNPARSED | non-SEL share |
|---|---|---|---|---|---|---|---|
| loose / **tight** / family | added(51) | 14 | 13 | 20 | 0 | 4 | **0.7021** |
| loose / **tight** / family | newly admitted(11) | 2 | 7 | 0 | 0 | 2 | **0.7778** |
| loose / **tight** / family | committed extension(5) | 4 | 0 | 0 | 0 | 1 | **0.0000** |

⚠ **The curve is FLAT and that is a fact about the tags, not robustness** — every tag here is
builder-emitted with a clean rule prefix, so the three classifiers **could not have differed**
*(ledger 1002)*.

**The 11, named.** `oracle_k4_08bR`, `oracle_k4_oracle_kA/kB`, `greedy_k4_greedy_kA/kB`,
`indep_k4_indep_kA/kB` → **TARGET-READING** (7). `topw_k4_detA/detB` → **SELECTOR** (2).
`coval_core_2bA/2bB` → **UNPARSED** (2).

⚠ **`UNVERIFIED`:** whether the four suffixed tags are **replicas** of `coval_core` and `topw_k4` —
which would leave the 11 containing **no new object at all** — is not readable from a name, because
`tag_suffix` is caller-supplied rather than rule-emitted. It needs **R525's satisfaction-vector
partition on today's 92**.

**Registered against measured.**

| | registered | measured | |
|---|---|---|---|
| P1 share of the 51 parsing | ≥ 0.70 | **0.9216** | ✓ |
| P2 non-SELECTOR share of the 51 | 0.55 [0.20, 0.90] | **0.7021** | ✓ in band |
| P3 non-SELECTOR of the 11 | 9 [0, 11] | **7** | in band, point wrong *(1001)* |
| **D** the 11 exceed the 51 | true | **true**, 0.7778 vs 0.7021 | ✓ |

⚠ **P3 was PARTIALLY SIGHTED**, declared in the preregistration: 6 of the 11 names were visible in a
truncated print before registration. ⛔ **The 11 are a SUBSET of the 51** — a within-population
contrast, **no significance claimed**, and labelled a derivation.

**Controls — 6 PASS, 0 FAIL.**

| control | returned |
|---|---|
| **PROVENANCE** | all three source assertions hold; otherwise exit 2 |
| **POSITIVE** | `random_k8_s0 → RANDOM`, `topw_k4 → SELECTOR`, **different classes**; band computed — at a floor classifier assigning one class they **cannot** separate |
| **g=0** | out-of-grammar tags → `UNPARSED`; a silent `SELECTOR` default would have **manufactured World A** |
| **NEGATIVE** | rule→class shuffled → `{TGT 29, SEL 14, CEIL 2, RND 2}` vs real `{RND 20, SEL 14, TGT 13}` |
| **SHAM** | ingredient **absent**: the committed extension, **0/4** non-SELECTOR |
| **PLACEBO** | 10 non-tag strings → 0 in every class, stated as **0 of 10** |

⚠ **SHAM shortfall stated:** R728 records the committed **count** (41), not the committed **names**, so
the sham ran on the **5** it does record.

**Verdict — `WORLD B`.** The census's new admissions are dominated by apparatus. **World A is killed:
the wider population is not a wider sample of cores**, and `16` beside `5` would present our own
instruments as rival subject matter *(ledger 1000)*.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 7777, **both writes confirmed to
disk** before the comparison ran (5734 / 5737 bytes, differing only in the recorded seed).

## R746 · the census admitted arms measured on two different populations

**Question.** R745 left four tags unresolved and proposed exact satisfaction-vector identity to settle
them. ⛔ **The objects refused half of it before any code:** `sat_coval_core.npz` holds 15,312 cells
over 968 prompts; `sat_coval_core_2bA/2bB.npz` hold 3,168 over **200**. Identity across different cell
sets is **undefined**, not false *(ledger 1004)*.

**E1 estimand.** The prompt-coverage distribution of today's 92-arm population, split by the 16
admitted, the 51 added, and the whole 92. **Identified exactly** — `select_core.py:200` emits meta as
`f"{pid}|{j}|{x}"`, so the prompt set is field 0 of a builder-emitted structured string.

**E2 estimand.** Whether the four unresolved tags coincide with an extension member, **on shared
cells**. **Partially identified → a BOUND**: `identical ⇒ indistinguishable THERE`; `not identical ⇒
different objects`.

**E2 result — all four are replicas.**

| pair | identical | shared / larger |
|---|---|---|
| `topw_k4_detA` / `detB` vs `topw_k4` | ✓ | 15,488 / 15,488 = **1.000** |
| `coval_core_2bA` vs `coval_core_2bB` | ✓ | 3,168 / 3,168 = **1.000** |
| `coval_core_2bA` vs `coval_core` | ✓ | 3,168 / 15,312 = **0.207** |

⇒ **the 11 extra admissions contain no new SELECTOR object** — 7 target-reading *(R745)* + 4
duplicates. ⚠ Whether the 7 target-reading **tags** are 7 **objects** is `UNVERIFIED`; R730's
precedent (7 → 4) says expect fewer.

**E1 result — the coverage grid, 3 definitions × 3 populations.**

| definition | population | min | median | max | distinct | below max |
|---|---|---|---|---|---|---|
| **prompts** | **admitted(16)** | **200** | 968 | 968 | **2** | **2** |
| prompts | added(51) | 4 | 968 | 968 | 3 | 3 |
| prompts | all(92) | **4** | 968 | 968 | **4** | 5 |
| cells | admitted / added / all | 3,168 / 256 / 256 | 15,488 | 30,680 / 43,812 / 59,936 | 6 / 9 / 13 | 15 / 47 / 90 |
| pairs | admitted / added / all | 792 / 64 / 64 | 3,872 | 7,670 / 10,953 / 14,984 | 6 / 9 / 13 | 15 / 47 / 90 |

⭐ **The committed extension is uniform — all five at 968.** The heterogeneity arrived with the drift.

**⛔ The arithmetic, derived before measuring, points AWAY from a defect.** `mde = ZEFF·std/√n`, so
968 → 200 multiplies the bar by **2.2000**. Realised, the low-coverage admissions cleared a mean
`mde1` of **0.026962** against **0.013275** for the rest — **2.03× wider**. They were admitted
**despite** a harder threshold.

⛔ **The first verdict string said the opposite and the same run refuted it three lines above**
*(ledger 1006)*: it branched on the share comparison alone while the realised-threshold comparison sat
computed and unused. **Over-representation ≠ advantage.** The branch now references it and the
mechanism is reported as **unexplained**.

**Registered against measured.**

| | registered | measured | |
|---|---|---|---|
| B1 distinct coverage values over the 92 | 3 [1, 10] | **4** | in band, point wrong |
| B2 added arms below 968 | 8 [0, 51] | **3** | in band, point wrong *(1007)* |
| B3 committed extension all at 968 | yes | **yes** | ✓ |
| B4 admitted arms below 968 | 2 [2, 16] | **2** | ✓ |
| B5 the five identity tests | all yes | **all yes** | ✓ |
| **D** coverage does not predict admission | true | **false** — 0.1250 vs 0.0395 | ⛔ |

⚠ **World A was dead before registration and the preregistration declares it** — the 200-prompt
coverage was visible while inspecting the objects. Second declared sighting in two rounds.

**Controls — 6 PASS, 0 FAIL.** POSITIVE separates two arms whose **file sizes** differ 4.52×, a signal
the parser never reads, against a floor parser that cannot separate them · g=0 an empty-meta arm →
`UNREADABLE`, never `0`, since **a silent zero would have manufactured World B** · NEGATIVE field-1
parsing moves coverage on 20/20 · SHAM the ingredient **absent**, the 76 non-admitted arms (3/76) ·
PLACEBO 0 on all 92 · UNIT every tag → exactly one `.npz`, asserted.

**Verdict — `WORLD B`.** The census admits across two populations. Low-coverage arms are
over-represented among the admitted, **but cleared a wider bar**, so it is not an admission advantage
and the mechanism is unexplained.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 424242, **both writes confirmed to
disk** (11,963 / 11,968 bytes, differing only in the recorded seed).

## R747 · 81 objects is *not* a transitive-closure artifact — the attack failed

**Question.** R730's object partition merges tags that are equal **on the prompts they share**, with a
guard `len(shared) ≥ 0.5·min(|A|,|B|)`, and builds classes by **union-find**. Equality on a shared
subset is **not transitive**, and union-find takes the closure regardless. Since **81** is the
denominator R730, R745, R746 and this page all rest on, it is worth attacking.

**Estimand.** E1 how many of R730's multi-tag classes are **not cliques** under its own `same()`.
E2 the object count under the **clique** partition. **Exact and finite** — 93 tags, 4,278 pairs, R730's
own cached vectors, imported rather than re-implemented.

**Result — the attack failed.**

| | registered | measured | |
|---|---|---|---|
| P1 non-clique multi-tag classes | 1, band [0, 8] | **0** | in band, point wrong |
| P2 clique-partition object count | 83, band [81, 93] | **81** | at the floor, point wrong |
| P3 reproduce R730's 81 with its own code | yes *(hard)* | **81 = 81** | ✓ |
| **P4** pairs rejected **only** by the guard | **≥ 1** | **0** | ⛔ **FAILED** *(ledger 1010)* |

**8 multi-tag classes, 4 of size ≥ 3, 0 not cliques.**

**Specification curve — flat, and the flatness is arithmetic, not robustness.**

| guard | 0.00 | 0.25 | **0.50** | 0.75 | 1.00 |
|---|---|---|---|---|---|
| objects | 81 | 81 | **81** | 81 | 81 |
| non-clique | 0 | 0 | **0** | 0 | 0 |

⛔ The guard is `len(shared) ≥ g·min(|A|,|B|)`. For a **strict subset** pair `len(shared) = min`, so
the test is `min ≥ g·min` — **true for every g ≤ 1**. The guard can only reject a **partial** overlap,
and this population has none. That is why `P4 = 0`, and it means the sweep could not have failed.

⛔ `E2 ≥ union-find count` is **FORCED** — the clique partition refines the closure. Only the **size**
of the increase is a measurement, and it is **0**.

**⭐ But the subset rule IS load-bearing, and the SHAM locates it.** Ingredient **absent** — require
**identical** prompt sets — gives **83 objects**, still 0 non-cliques. So the count carries **one
unstated parameter worth 2 objects**: `81` under shared-subset merging, `83` under full overlap. The
two extra are the `coval_core`/`_2b*` case R746 measured at 200 of 968 prompts. **R730's own residue
already calls this a modelling choice, and this round does not adjudicate it.**

**Controls — 6 PASS, 0 FAIL.** POSITIVE is a **synthetic** non-transitive triple built by construction
(A≈B, B≈C, A≢C): union-find merges to 1 class and the clique test flags it, against a never-flagging
floor of 0 — **that is what makes the zero on real data admissible rather than silent** · g=0 a
synthetic clique triple → 0 flagged, since flagging every multi-tag class would have manufactured
World B · NEGATIVE `same()` forced False → 93 singletons, 0 violations · SHAM as above · PLACEBO 73
singletons → 0, stated as 0 of 73 · P3 the instrument is R730's, not a lookalike.

**Verdict — `WORLD A`.** Union-find added nothing the relation did not already give. **81 is well
defined and every downstream count is clear of a chaining artifact.**

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 31337, **both writes confirmed to
disk** (1,357 / 1,361 bytes, differing only in the recorded seed).

## R748 · the page's two object counts differ in three factors, and both move under the rule

**Question.** R747 priced one unstated parameter and closed by proposing it be priced at the claim
level. Running P4 on that question — on **every** question the round asks, which is R747's own lesson
— found something larger: the deliverable's two object counts were computed by **different relations
on different quantities over different populations**.

| round | relation | quantity |
|---|---|---|
| **R524** | `len(ma)==len(mb) and (ma==mb).all() and array_equal(sa,sb)` | **full overlap**, raw satisfaction cells |
| **R730** | equal on **shared** prompts, guard `≥ 0.5·min` | **subset**, per-prompt aggregated agreement vectors |

They disagree on a class both computed: R524 has `['coval_core_2bA','coval_core_2bB']`; R730 has
`['coval_core','coval_core_2bA','coval_core_2bB']`.

**⛔ The first implementation was wrong and its own control caught it** *(ledger 1011)*. v1 applied both
rules to raw cells and `P4` returned **70** against R730's committed **81**. R730's relation never
touches raw cells. The two published rules differ in **two ways at once** — R732's failure in this same
arc — so the grid became **2 quantities × 2 rules × 2 populations**.

**The grid — 8 cells.**

| quantity | population | full overlap | subset | gap |
|---|---|---|---|---|
| **raw cells** | **56 (R524)** | **46** ← *the page's number* | **39** | 7 |
| raw cells | 93 (R730) | 83 | 70 | 13 |
| agg vectors | 56 (R524) | 45 | 44 | 1 |
| **agg vectors** | **93 (R730)** | **83** | **81** ← *the page's number* | 2 |

⛔ `subset ≤ full` is **FORCED** — full overlap refines subset. Only the **gap** is measured.
⭐ **Aggregation absorbs most of what the overlap rule would separate** — gaps 7→1 on the 56 and
13→2 on the 93.

**E2 — both stated counts move under the rule alone.** *"56 tags are 46 objects"* → 46 full / **39**
subset. *"93 tags are 81 objects"* → **83** full / 81 subset. *"13 tags are 10 objects"* → population
not reconstructible, **OUT OF SCOPE**, not assumed unaffected.

**Registered against measured.**

| | registered | measured | |
|---|---|---|---|
| P1 56 under subset | 45 [40, 46] | **39** raw / **44** agg | ⚠ **under-specified as written** — it presupposed one quantity *(1012)* |
| P2 93 under full overlap | 83 | **83** on both quantities | ✓ |
| P3 / P4 reproduce 46 and 81 | yes *(hard)* | **46 = 46**, **81 = 81** | ✓ |
| P5 stated counts that move | 1 [0, 10] | **2** | in band, point wrong |
| P6 disagreeing classes | 2 [0, 20] | **2** | ✓ exact |
| **D** all disagreements carry a strict subset | true | **false — 1 of 2** | ⛔ *(1013)* |

⭐ **D failing is the informative part**: the second disagreeing class is a **partial overlap** with no
containment, so there are **two** mechanisms and a fix aimed at subsetting alone would leave half in
place.

⛔ **D2, a DERIVATION asserted and excluded from the findings** *(1014)*: the extension's 5 members sit
in 5 classes under both rules — forced, because a refinement cannot merge what is already separate.

**Controls — 7 PASS, 0 FAIL.** POSITIVE a synthetic **strict-subset** pair: subset merges, full overlap
does not — **opposite sides**, band computed against merge-nothing/merge-everything · g=0 a synthetic
**unequal** pair, both refuse, since a subset rule merging unequal arms would have manufactured P1 ·
NEGATIVE distinct seeded noise ×3 seeds → **(93, 93)** every time · **SHAM** the ingredient **absent**,
the 88 arms sharing one prompt set → **79 = 79**, so the rules are identical where overlap is constant
and the gaps are attributable to overlap structure · PLACEBO 0 of 93 · P3/P4 both instruments are the
ones they claim to be.

**Verdict — `WORLD B`.** Both stated counts move; **every object count must carry its cell**.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 98765, **both writes confirmed to
disk** (1,905 / 1,909 bytes, differing only in the recorded seed).

## R749 · which cell did each object-count claim come from?

**Question.** R748 established an 8-cell identity grid and that the page's two headline counts sit in
different cells. Which cell does *each* object-count claim descend from?

**⛔ First, a defect in R748's own instrument** *(ledger 1015)*. It enumerated claims with one pattern
matching **3** sentences; a medium pattern matches **5**. Its `P5` was a share of an under-counted
population — §4's *a search is an instrument*, one round after quoting it.

| pattern | sentences | live | in a retracted block |
|---|---|---|---|
| tight *(R748's)* | 3 | 3 | 0 |
| **medium** | **5** | 5 | 0 |
| loose | 50 | 50 | 0 |

⛔ `loose ≥ medium ≥ tight` is **FORCED**. The order is algebra; only the gaps measure.

**The five, resolved.**

| count | cites | cell | how |
|---|---|---|---|
| **46** | R524 | `raw cells × full overlap` | defined in its own source |
| **81** | R730 | `agg vectors × subset` | defined in its own source |
| **2** | R520, R523, R525 | **UNRESOLVED** | R520 holds no identity relation |
| **4** | — | **UNRESOLVED** | the sentence cites nothing |
| **10** | — | **UNRESOLVED** | the sentence cites nothing |

**E3 = 2 distinct cells among the resolved → `WORLD B`:** the rows are not comparable and each must
carry its cell.

**Registered against measured.**

| | registered | measured | |
|---|---|---|---|
| P1 assertions per pattern | ⚠ **SIGHTED**, declared before registering | 3 / 5 / 50 | — |
| P2/E3 distinct cells | 2 [1, 4] | **2** | ✓ exact |
| P3 assertions resolving | 3 [0, 5] | **2** | in band, point wrong |
| **P4** resolved rounds importing their relation | 2 [0, 10] | **0** | in band, point wrong |
| P5 citing a round with no `run.py` | 0 [0, 5] | **0** | ✓ |
| **D** the unresolved are the importers | true | **false** | ⛔ *(1017)* |

⭐ **D failing is the finding.** Import-following was built because R747 and R748 both import
`same()` — a real limitation, correctly anticipated, that **never bit**. The three failures are
**missing citations**, which no instrument improvement can repair.

⚠ **The resolver takes the FIRST citation and that choice has a measured cost**: the NEGATIVE control
rotates it and **2 of 5** cells change. So *"row 8 is untraceable"* is a statement about the resolver,
not about the row.

**Controls — 5 PASS, 0 FAIL.** POSITIVE resolves R524 and R730 to their known cells, **correct and
distinct**, against a constant-cell floor that cannot separate them · g=0 an uncited assertion →
`UNRESOLVED`, since **a default cell would have manufactured World A** · NEGATIVE rotation moves 2/5 ·
SHAM ingredient **absent**: 36 of the first 40 rounds hold no locatable relation and every one returns
`UNRESOLVED` · PLACEBO 0 of 5.

⛔ **A CENSUS HAS NO CONFIDENCE INTERVAL.** n = 5 is every object count on the page: no sampling
uncertainty, and **no power to generalise**. None is reported.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 55555, **both writes confirmed to
disk** (2,756 / 2,760 bytes, differing only in the recorded seed).

## R750 · when a sentence cites several rounds, how many of them hold the number?

**Severity check first, and it changed the round.** R749's NEXT asked about multi-cited **object-count**
sentences — there is exactly **1**. **A round with n = 1 is not a measurement.** One level up the page
holds **1,389** sentences, **65** citing ≥2 rounds, **17** of those carrying a number, with group sizes
2, 3, 4, 5, 8. That is measurable; the narrower version was not.

**Estimand.** For each such sentence, the **support depth**: how many cited rounds' own artifacts
contain the stated number.

**⚠ R590's repair reused.** Its prefix matcher required the printed value to be a prefix of a stored
float, so rounded-up values failed — 13 orphans of which **9 were its own bug**. R590 has no `run.py`,
so the relation is re-implemented with the repair carried forward and the prefix rule kept only to
price it.

| matcher | population | n | median | share ≥2 | share = 0 |
|---|---|---|---|---|---|
| prefix *(broken)* | multi-cited | 17 | 1.0 | 0.4118 | **0.2353** |
| **rounded** *(repair)* | **multi-cited** | **17** | **1.0** | **0.4118** | **0.1176** |
| **rounded** | **single-cited (SHAM)** | **37** | **1.0** | — | **0.2162** |
| tolerance | multi-cited | 17 | 1.0 | 0.4706 | 0.1176 |

⛔ `support ≤ group size` **ALWAYS**. ⛔ The **SHAM's `share ≥2` is structurally 0** — a single-citation
sentence cannot have support 2; its informative column is `share = 0`.
⭐ **The broken rule manufactures 2 extra orphans on this page** (4 vs 2) — R590's bug, re-measured.

**Registered against measured.** P1 median 1 **[0,3] → 1** ✓ · P2 share≥2 0.35 → **0.4118** ✓ ·
P3 SHAM 0.79 → **0.7838** ⚠ **prior-art informed from R590's 15/19, declared, not scored as a blind
hit** *(ledger 1021)* · P4 zero-support 2 → **2 of 17** ✓ · P5 manufactured orphans ≥1 → **2** ✓ ·
D no growth with size → **true on usable sizes** ✓.

⚠ **The directional excludes sizes with n < 3.** Sizes 4 and 8 hold **one sentence each** at mean 4.00;
a mean over n=1 is not a trend *(ledger 1020)*. They stay in the table with their counts visible.

**⛔ The NEGATIVE control could not have fired** *(ledger 1019)*. v1 rotated the group **within** a
sentence — but `support` **sums over every member**, so rotation permutes a set being summed and the
count is invariant **by construction**. ⭐ **The identical operation was a valid control one round
earlier**, because R749's resolver reads exactly one citation and order is load-bearing there.
**A control is a property of its design and cannot be carried across.** Repaired by giving each
sentence **another sentence's** group: **10 of 17** change.

**Controls — 4 PASS, 0 FAIL.** POSITIVE `0.0316`, found by **direct search** in both R294 and R426 —
not by the matcher — scores **2** against a never-matching floor of 0 · g=0 a number in no artifact →
**0, reported not skipped**, since a skipped zero would raise the median by deleting the worst cases ·
NEGATIVE as above · PLACEBO 0 of 17 · SHAM the ingredient **absent** · UNIT **7 of 17** sentences state
more than one number, so support is per **number** and the sentence value is the **maximum**.

**⚠ The confound, written before the run, does not rescue the result.** Against the rounds' READMEs
rather than their artifacts: **median 1.0, share ≥2 = 0.4118** — identical. Reported beside, never
merged.

**Verdict — `WORLD B`.** A citation group is not joint grounding. **Where a figure matters, the page
must name which citation computed it.**

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 13579, **both writes confirmed to
disk** (7,990 / 7,994 bytes, differing only in the recorded seed).

## R751 · `UNVERIFIED` — the annotation detector inverted its own SHAM

**Question.** How much of what a defect-flag counts is **already repaired** on the page? R750 reported
2 zero-support figures as residue; one of them is the row this page already annotates as ungrounded
*(ledger 1022)*.

**⛔ P4 first, and it stopped the fourth rebuild in this arc.** R750's proposed corpus-wide value search
**is R591**, which scanned 355 rounds for R590's four orphans and returned four different verdicts,
including `0.0200` **CONFIRMED UNGROUNDED**.

**The grid — 3 matchers × 3 windows, SHAM arm beside every cell.**

| matcher | window | flagged | annot | share | **SHAM (supported)** |
|---|---|---|---|---|---|
| **rounded** | **tight** | **33** | **6** | **0.1818** | **0.4600** |
| rounded | medium | 33 | 8 | 0.2424 | 0.4667 |
| **rounded** | **loose** | **33** | **10** | **0.3030** | **0.5133** |
| prefix | tight / loose | 71 | 23 / 27 | 0.3239 / 0.3803 | 0.4643 / 0.5357 |

⛔ `annotated ≤ flagged` and `loose ≥ tight` are **both FORCED** — order is algebra, only gaps measure.

**⛔ The SHAM did not match, it INVERTED.** Supported figures carry annotation keywords **more** often
than flagged ones, at every window and matcher. **Annotation does not track groundedness**, so the
question is unanswerable with this detector and the verdict is `UNVERIFIED`.

**Where the failure lives — the confound run on BOTH arms:**

| keyword | flagged | supported | |
|---|---|---|---|
| **`ungrounded`** | **0.0606** | 0.0400 | flagged 1.5× |
| **`corrected`** | **0.0606** | 0.0200 | flagged 3.0× |
| `retracted` | 0.1515 | **0.2867** | supported |
| `unverified` | 0.1818 | **0.4400** | supported |

**A keyword detector cannot separate *"this number is ungrounded"* from *"this claim's scope is
unverified"*.** ⚠ **The restricted detector is NOT reported as a result** — selecting it after seeing
which subset favours the hypothesis is choosing the specification from the outcome *(ledger 1024)*.

**Registered against measured.** P1 10 [3,40] → **33** in band, point wrong · P2/P3 ⛔ **registered with
bands `[0.00, 1.00]`, which no share can fall outside — a check that cannot fail, in the
preregistration of a round about instruments that cannot fail** *(ledger 1023)* · P4 the known case
found loose and **missed tight** ✓ *(hard)* · P5 2 [0,10] → **10**, at the ceiling · D ✓.

**Controls — 4 PASS, 1 FAIL.** POSITIVE `0.0200` missed tight, found loose, against a never-annotating
floor — **a detector finding it at every window would not be measuring the window** · g=0 **23** flagged
figures carry no keyword anywhere · NEGATIVE detached windows drop the share 0.3030 → 0.2424 · PLACEBO
0 of 33 · **SHAM FAIL, inverted** · UNIT **17 of 33** flagged figures share a line.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 24680, **both writes confirmed to
disk** (3,356 / 3,360 bytes, differing only in the recorded seed).

## R752 · the MDE refuses the comparison, and the formula computing it was too generous

**Question.** R751 demanded the restricted detector be preregistered **and its MDE computed before the
run**. Done in the preregistration: at **n = 33 vs 150**, MDE ∈ **[0.1174, 0.1924]** against gaps of
**0.0206** and **0.0406**. **The comparison was dead before any code ran.**

**⛔ Then the formula failed its own control.** Planting a difference of exactly the analytic MDE and
running the exact test it approximates rejects **0.6237**, not 0.80 — 3 seeds, spread **0.0101**. The
confound was written before the run: `0.05 × 33` is **under 2 expected events**.

⭐ **The preregistration pre-authorised the repair**, so it was applied rather than improvised:

| | analytic | **empirical (searched)** |
|---|---|---|
| MDE | 0.1174 | **0.1604** — 1.37× larger |
| ratio to the gap | 2.89× | **3.95×** |
| required n per arm | 453 | **846** vs **33** available |

⚠ **The positive control is the monotone LADDER, not the search's own answer** — asserting the searched
MDE rejects at 0.80 would be circular. `0 → m/2 → m → 2m` gives **0.0395 → 0.4460 → 0.7999 → 0.9954**.

**The grid — 0 of 24 cells detect the gap.** Even the most permissive (p̄ 0.05, α 0.10, power 0.80,
one-sided) is **0.0838**, twice the gap.

**Controls — 5 PASS, 0 FAIL.** g=0 rejects at **0.0395 ≈ α** · NEGATIVE at 10× n moves the MDE
0.1174 → **0.0371**, ratio **3.16** against √10 = 3.16, and the gap then rejects at **0.7823** —
**the sample is the problem, not the estimator** · SHAM with the imbalance removed (both arms at the
harmonic mean 54.1) leaves the MDE **unchanged**, so the imbalance is not the binding constraint ·
PLACEBO exactly 0.

**E2 — the census, n = 4, no rate computed.**

| line | value | cites | keyword | scope language too? |
|---|---|---|---|---|
| 551 | `0.0022`, `0.0995` | R741 | `corrected` | **yes** — ambiguous |
| 620 | `+0.0582`, `0.0200` | R514, R515 | `ungrounded` | **no** — clean |

⇒ **2 of 4 are unambiguous groundedness declarations**; the other 2 sit under a `CORRECTED` marker that
also carries scope language. **The same confusion that inverted R751's pooled detector, visible at the
level of the individual figure** *(ledger 1027)*. ⛔ A census of 4 has **no interval and no power to
generalise**.

**Registered against measured.** P1 0.80 [0.70, 0.90] → **0.6237** ⛔ **FAILED, and it is the formula
that failed, not the design** *(1025)* · P2 0.05 → **0.0395** ✓ · P3 800 → **453 analytic / 846
empirical**, ⚠ **the registration named neither and neither is scored as a hit** *(1026)* · P4 4 → **4**
✓ · P5 2 → **2** ✓ · D ✓.

**Verdict — `WORLD B`.** The design is blind; the comparison is **REFUSED**; the census is the round's
only claim about the page.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 86420, **both writes confirmed to
disk** (4,259 / 4,263 bytes, differing only in the recorded seed).

## R753 · the three deliverables are not one population, and the ungated one is 4.5× worse

**Question.** R752 left a requirement of **846 figures per arm** and asked how many pages reach it.
⛔ **That is division.** The count settles itself; the question worth asking is whether pooling is
legitimate — §1's G1, *asking for power on an unidentified quantity is how a well-powered-looking
round gets built*.

| document | figures | lines | flagged | **rate** | median cited era |
|---|---|---|---|---|---|
| `STATEMENT.md` | 184 | 68 | 33 | **0.1793** | R607 |
| `DEFINITION.md` | 118 | 67 | 45 | **0.3814** | R439 |
| **`FORMULATION.md`** | 125 | 57 | **100** | **0.8000** | R256 |
| **pooled** | **427** | | 178 | 0.4169 | — |

**427 / 846 = 0.50 of one arm**; **12** documents of average size would be needed.

**Pairwise, with the MDE computed before interpretation.**

| pair | diff | MDE (figures) | MDE (lines) | verdict |
|---|---|---|---|---|
| STATEMENT vs DEFINITION | 0.2020 | 0.1629 | 0.2378 | **DIFFERENT** |
| **STATEMENT vs FORMULATION** | **0.6207** | 0.1601 | 0.2481 | **DIFFERENT** |
| DEFINITION vs FORMULATION | 0.4186 | 0.1773 | 0.2489 | **DIFFERENT** |

⭐ **The SHAM makes it readable.** Ingredient **absent** = being a different document: two halves of
`STATEMENT.md`, exchangeable **by construction**, differ by **0.0933**. The largest between-document
difference is **6.7×** that.

⚠ **The confound is live and unresolved** *(ledger 1029)*. The ungated document is also the **oldest**
— governance and era are the same column here. The directional fires (`FORMULATION.md` at **4.5×**
this page's rate) but **"being ungated caused it" is not established**, and the era is printed beside
each rate.

**Controls — 5 PASS, 0 FAIL.** POSITIVE the monotone ladder `0.0529 → 0.2955 → 0.8026 → 0.9999` ·
g=0 rejects at **0.0532 ≈ α** · NEGATIVE document labels shuffled collapses the spread **0.6207 →
0.0482** · SHAM as above · PLACEBO exactly 0.

⭐ **The formula was honest here** — analytic **0.1601**, empirical **0.1620**, ratio **1.01×**, against
**1.37×** in R752. **The difference is expected count**: under 2 events there, ~52 here. *The
approximation's failure is predictable from the counts* *(ledger 1030)*.

**Registered against measured.** P1 0.18 → **0.1793** ✓ · **P2 0.30 → 0.8000 ⛔ at the ceiling** ·
**P3 0.12 → 0.6207 ⛔ outside the band** · P4 0.125 → **0.1601** ✓ · P5 0.75 → **0.7955** ✓ · D ✓.
**I under-predicted the disagreement between my own pages by 5×** *(ledger 1028)*.

**Verdict — `WORLD C`.** The documents are **not exchangeable**; pooling would manufacture power
without validity, which is worse than the shortfall. **And the shortfall stands regardless.**

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 97531, **both writes confirmed to
disk** (2,287 / 2,291 bytes, differing only in the recorded seed).

## R754 · era does not explain it where it can be measured, and where the effect lives it cannot be

**Question.** R753 found the ungated `FORMULATION.md` at a **0.8000** flagged rate and flagged that
governance and era are confounded. Separate them by comparing eras *within* a document.

**⛔ The identification check ran first and killed the main contrast.**

| document | `<300` | `300-450` | `450-600` | `600+` | total |
|---|---|---|---|---|---|
| `STATEMENT.md` | 4 | 6 | 86 | 88 | 184 |
| `DEFINITION.md` | 5 | 43 | 55 | 19 | 122 |
| **`FORMULATION.md`** | **110** | **15** | **0** | **0** | 125 |

**2 of 3 pairs have an empty joint bin ⇒ UNIDENTIFIABLE.** Only `STATEMENT`–`DEFINITION` is 4/4.
⛔ **An empty joint bin cannot be stratified — definitional.** This is an **identification** failure,
not a power failure *(ledger 1031)*, and more data does not repair it.

**E2 — within `DEFINITION.md`, governance constant, era varying.**

| | n_old | n_new | rate_old | rate_new | diff |
|---|---|---|---|---|---|
| **`DEFINITION.md`** | 48 | 74 | **0.3958** | **0.4054** | **−0.0096** |
| `STATEMENT.md` | 10 | 174 | 0.5000 | 0.1609 | +0.3391 ⚠ **n_old = 10, far below its MDE — uninformative** |
| `FORMULATION.md` | 125 | **0** | 0.8000 | **UNDEFINED** | ⛔ undefined is **not** zero |

**The difference sits at the 14.5th percentile** of a 5,000-shuffle permutation null (sd **0.0915**,
95% band **[−0.1813, +0.1622]**). ⭐ And five **arbitrary** split points give `|diff|` up to **0.0763**
— **the era split is less different than an arbitrary one.**

**⛔ My first negative control presupposed a non-null effect** *(ledger 1032)*. It asked whether one
shuffle beat the real difference; with a real difference of −0.0096 that is **§4 row ② verbatim** —
*"a coin flip when the real effect is null, which is exactly when you are running it."* Repaired to the
shuffle **distribution**.

**Controls — 5 PASS, 0 FAIL.** POSITIVE the monotone ladder `0.0504 → 0.2833 → 0.7991 → 1.0000` ·
g=0 at **0.0497 ≈ α** · NEGATIVE as above · SHAM the arbitrary splits · PLACEBO exactly 0.
⭐ The formula was honest again: analytic **0.2545**, empirical **0.2565**, **1.01×**.

**Registered against measured.** **P1 +0.30 ⚠ prior-art-informed from R607's 13× era effect → −0.0096**
— in band, point badly wrong, and **the prior did not transfer from rounds to a document's figures**
*(ledger 1033)* · P2 15 → **4** ✓ · P3 0.25 → **0.2545** ✓ · P4 0.78 → **0.7939** ✓ · P5 2 → **2** ✓ ·
**D false** — DEFINITION's old-era rate is closer to STATEMENT's than to FORMULATION's.

**Verdict — `WORLD B`.** Era does not explain it where it can be measured, so **the governance reading
survives its strongest confound** — the most it can do, since the decisive contrast is unidentifiable.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 11223, **both writes confirmed to
disk** (2,830 / 2,834 bytes, differing only in the recorded seed).

## R755 · era, governance and maintenance are one variable here, and it is n = 1

**Question.** R754 proposed measuring MAINTENANCE from git to separate *ungated* from *abandoned*.

**⛔ The design died twice before running.** ① A correlation over **three** documents is not a
measurement — three points always admit a line. ② `git blame`: every line of all three deliverables
was last touched inside a **two-day** window (`distinct days = 2` each). **No maintenance gradient
exists in wall-clock time.**

**⛔⛔ The ontology error, running back through R753 and R754** *(ledger 1034)*:

| document | commits | last touched | new citations | **max R ever cited** |
|---|---|---|---|---|
| **`FORMULATION.md`** | **99** | **2026-08-04T02:11** | 105 | **R360** |
| `STATEMENT.md` | 131 | 2026-08-05T18:51 | 202 | R754 |

**It is not abandoned** — 99 commits, stopped **41 hours** ago. **Round ids 164–755 are a LOGICAL
clock**, and *old-era*, *ungated* and *unmaintained* are **one variable**: position in a three-day
burst. ⚠ **One document stopped ⇒ the treatment is n = 1**, collinear with document identity; 417
commits do not repair a document-level contrast *(ledger 1036)*. **This line is CLOSED.**

**What IS identified — within `FORMULATION.md`, governance constant.**

| | value |
|---|---|
| new citations per commit, mean | **1.0606** |
| slope, raw / per added line | **−0.0090** / −0.001052 — **same sign**, not a commit-size artifact |
| shuffled-order slopes ×5 | mean −0.0021, sd **0.0046** |
| first 10 / last 10 commits | **23** / **11** |
| terminal zero-adding run | **1** |

**Neither a reliable slope (−0.0090 against a −2σ threshold of −0.0092, missing by 0.0002) nor a
cutoff ⇒ `UNRESOLVED`, and the series is published rather than a slope.**

**⭐ The informative residue is a registered point whose SIGN I got wrong** *(ledger 1035)*. I
registered `STATEMENT.md`'s slope at **+0.05**; it is **−0.0074** — **the same decline as the stopped
document**. A declining citation rate is not a property of abandonment; it is what happens when a
document consumes uncited rounds faster than the pool refills.

**Controls — 5 PASS, 0 FAIL.** POSITIVE the live stream adds **23** citations in its last 20 commits,
band `0 < 23 ≤ 202` · g=0 **31 of 99** zero-adding commits are **in the series, not skipped** ·
NEGATIVE shuffled order → mean −0.0021 · **SHAM** the ingredient **absent** — added `⛔` markers slope
**+0.0032** against the citation slope **−0.0090**, so the trend is about **citing**, not commit style ·
PLACEBO exactly 0.

⛔ **A derivation I failed to label in the preregistration:** *new distinct citations per commit* is
partly self-exhausting. For `FORMULATION.md`, whose pool froze at R360, it is close to forced. **The
parity with `STATEMENT.md`, whose pool kept growing, is what makes the comparison informative.**

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 44556, **both writes confirmed to
disk** (2,158 / 2,162 bytes, differing only in the recorded seed).

## R756 · the flagged rate belongs to ROUNDS — and R753's headline was mostly artifact ABSENCE

**⛔⛔ RETRACTION.** R753 reported `FORMULATION.md` at **0.8000** against `STATEMENT.md`'s **0.1793**
and read it as governance. **93 of FORMULATION's 125 figures — 74.4% — cite ONLY rounds with no
`results/` directory**, against **4.0%** (DEFINITION) and **0.0%** (STATEMENT). The matcher scored
*"no artifact"* identically to *"artifact does not hold this value"* *(ledger 1038)*.

**⭐ And the direction REVERSES once absence is separated:** among rounds that DO have artifacts,
FORMULATION's average **0.2188**, STATEMENT's **0.4455** *(ledger 1039)*.

**Two cheap checks did the work.** ① Artifact availability by era is **uniform** (1.00/1.00/0.98/1.00),
killing the era-level version of the rival. ② At the exact-round level the documents are
**near-disjoint** — 43 / 61 / 97 rounds cited by figures, **`F ∩ S = 0`**, DEFINITION matching
FORMULATION on **5 of 125**. **A matched comparison is structurally unavailable, not under-powered.**

**The identified estimand — the ROUND as the unit.** 1,186 (figure, round) **pairs** from 416 figures.
⭐ **The g=0 control caught the retraction:** **27** cited rounds have no artifact and return
**UNDEFINED**, excluded **with their count printed** — never `0.0` (perfect support) nor `1.0` (total
failure). **R753 had no such control.**

| | all rounds | ≥3 figures |
|---|---|---|
| n | 138 | 76 |
| between-round variance | 0.1396 | **0.0905** |
| sampling null (5 seeds) | 0.1165 | **0.0394** |
| ratio | 1.20× | **2.30×** |

⛔ A round cited by ONE figure is 0 or 1 **by construction**; the columns are never merged.

**⚠ The SHAM bounds it.** Line-blocked at the same sizes: **0.0852** vs observed **0.0905** — only
**1.06×**. Random reassignment destroys all structure; line-blocking preserves **positional**
clustering. **Much of the clustering is positional**, and that is reported rather than resolved
favourably *(ledger 1040)*.

**Controls — 5 PASS, 0 FAIL.** POSITIVE **R392**, chosen by **artifact size** (116,141 B) *before* its
rate was seen — **not selected on the outcome** — scores **0.2000** vs pooled **0.6233** · g=0 as above ·
NEGATIVE 0.0905 → 0.0394 · SHAM as above · PLACEBO exactly 0. **CONFOUND printed:**
`corr(artifact size, rate) = −0.1382`.

**Registered against measured.** P1 150 → **138** ✓ · P2 0.09 → **0.0905** ✓ near-exact · P3 0.03 →
**0.0394** ✓ · **P4 ⚠ its band spanned [0,1] and could not fail — reported, not scored, and labelled**
(R751 made that mistake silently) · P5 20 → **36** ✓ · **D predicted true, measured FALSE and
INVERTED**.

⛔ **The document-level implication is ALGEBRA**: with near-disjoint round sets a document's rate is a
weighted average of its rounds', so *"documents differ"* **follows**. Only the variance was measured.

**Verdict — `WORLD A`.** The rate belongs to **rounds**; R753's document headline is a shadow of
**which rounds each document cites**.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 66778, **both writes confirmed to
disk** (1,866 / 1,870 bytes, differing only in the recorded seed).

## R757 · the artifact corpus was scoped to ONE arc of ten

**Question.** R756 contradicted itself — its era table said 17 of 17 early rounds have artifacts, its
g=0 said 27 cited rounds have none. **Both cannot be true.**

**⛔ The object settles it.** `E05_the_space_of_compilers/` holds **ten arcs, A16–A25**; **A24 begins
at R276**. The "artifact-less" rounds live in **A17 and A23**. Every round from **R748 to R756**
resolved `A24.glob(f"R{rid:03d}_*")` — **98 of 577 artifacts across 72 round directories were
invisible** *(ledger 1041)*. **§4's *a search is an instrument*, at repository scale.**

| document | A24 corpus | repo-wide | drop | flagged |
|---|---|---|---|---|
| `STATEMENT.md` | 0.1784 | 0.1784 | **0.0000** | 33 → 33 |
| `DEFINITION.md` | 0.3984 | 0.3984 | **0.0000** | 51 → 51 |
| **`FORMULATION.md`** | **0.8000** | **0.3680** | **0.4320** | **100 → 46** |

⭐ **Both arms use the same document text**, so this contrast is internally valid. ⛔ The repo corpus
**contains** the A24 one, so the rate can only fall — *"it fell"* is algebra.

**⛔ My first SHAM was more generous than the treatment** *(ledger 1042)*: it appended the whole blob
to **every** figure and dropped **0.4880**, which would have read as pure haystack. The real correction
gives each figure **its own** out-of-arc round. **Per-figure matched:** sham **0.0800** vs real
**0.4320** — **ratio 0.185**, so the correction is **5.4×** the haystack.

**⛔ The NEGATIVE control FAILED, and it is the more important finding** *(ledger 1043)*. Restricted to
A24, today's rates do not reproduce R753's: `DEFINITION.md` **0.3814 → 0.3984**, `STATEMENT.md`
**0.1793 → 0.1784**, `FORMULATION.md` **0.8000 → 0.8000** exactly. **The two that moved are the two I
append to every round; the one that matches is the one nobody edits.** The deliverable is a **moving
population**. ⇒ **the corpus defect is established, its size against published numbers is not, and the
verdict is `UNVERIFIED`.**

**Controls — 4 PASS, 1 FAIL.** POSITIVE `0.6602` found **verbatim by direct search** in
`A16/R220/tournament.json` — flagged under A24, supported repo-wide; **the FLIP is unreachable from
either degenerate end** · g=0 a fabricated value stays flagged under **both** · SHAM as above ·
PLACEBO exactly 0. **CONFOUND printed:** newly-resolved matches span **six arcs**
(`A23:25 · A19:16 · A20:7 · A16:4 · A17:4 · A18:1`), so it is not one arc's format.

**Registered — all five landed** (P1 **0.3680** · P2 **0.1784** · P3 **26** · P4 **0.2201** ·
P5 **0.0800**, D true). **And the round is still `UNVERIFIED`: prediction accuracy is not a verdict**
*(ledger 1044)*.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 13131, **both writes confirmed to
disk** (1,979 / 1,983 bytes, differing only in the recorded seed).

## R758 · git pins the population — both of them — and the correct pin is the PARENT commit

**Question.** R757 failed its NEGATIVE control and left `UNVERIFIED`, diagnosing *"the deliverables
grow every round"*. **Git holds every version, so the population can be pinned retrospectively.**

**⭐ Result.** Pinned to R753's **parent** tree, all three rates reproduce **EXACTLY**:
`0.1793 / 0.3814 / 0.8000`, including `DEFINITION.md`'s **118** figures and **45** flagged.

| document | PARENT | commit | today | vs R753 |
|---|---|---|---|---|
| `STATEMENT.md` | **0.1793** | 0.1793 | 0.1784 | **EXACT at parent** |
| **`DEFINITION.md`** | **0.3814** | **0.4016** | 0.4000 | **EXACT at parent, +0.0202 at its own commit** |
| `FORMULATION.md` | **0.8000** | 0.8000 | 0.8000 | **EXACT** (A24 corpus) |

⭐ **The correct pin is the PARENT**, because a round's own commit holds the document **after** that
round appended to it: `DEFINITION.md` is **122** figures at the commit and **118** at the parent, and
the four are R753's own appended section *(ledger 1046)*. **The preregistration named this limit before
the run and printed the bracket; the bracket was the answer.**

⚠ **The earlier diagnosis was right in kind and 10× too small** *(ledger 1047)*: isolated document
drift contributes **0.0016**, against a **0.0202** discrepancy.

**Two populations, and R757 pinned neither.** At R753: documents 1205 / 4677 / 2397 lines; A24 rounds
**456**; repo-wide **525**. At HEAD: 1255 / 4875 / 2397; **460**; **529**.

**Controls — 5 PASS, 0 FAIL.** POSITIVE recovered deltas `{+50, +198, +0}`; band computed — a recovery
returning today's file gives **all-zero** deltas, **the exact failure this round's own first lookup
produced** *(ledger 1045)* · g=0 HEAD's tree reproduces today's rates exactly · NEGATIVE **both**
crossed cells fail, so **both** populations are needed · **SHAM** R750's trees reproduce R753 in only
**1 of 3**, so reproduction is specific to the right tree · PLACEBO byte-identical.
**CONFOUND, decisive:** 574 artifacts present at both commits, **0 changed in place**, 4 added.

**⭐ R756's finding SURVIVES the corpus correction** *(ledger 1048)*: repo-wide, between-round variance
**0.1036** vs null **0.0420** = **2.47×**, against 2.30× narrow. **The rate belongs to rounds, and that
was not an artifact of the scoping defect.**

**Registered.** P1 **yes at the parent** *(hard)* · P2 0.43 → **0.4320** ✓ · **P3 0.017 → 0.0016**, in
band but **10× wrong — drift was not the cause** · P4 2.0 → **2.47** ✓ · P5 455 → **456** ✓ · D ✓.

**The pin, applied to this round's own numbers:** `STATEMENT.md` 1255 / `f792bdd6bfc417e3` ·
`DEFINITION.md` 4875 / `7fbde36cf36daf8d` · `FORMULATION.md` 2397 / `36ae2fbc2875c9f4`.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 99887, **both writes confirmed to
disk** (4,386 / 4,390 bytes, differing only in the recorded seed).

## R759 · the provenance arc is WRITE-ONLY, and it closes here

**Question.** R758 refused to pay the recomputation debt blindly and asked which of R748–R756's
numbers anything actually reads.

**Answer.** Of **110 distinctive** numbers (≥4 dp) published across those nine rounds, **15 — 13.6% —**
appear in any strictly later round.

| class | era | n | **read by a later round** |
|---|---|---|---|
| **distinctive** | **R748–R756** | **110** | **0.1364** |
| NON-distinctive *(SHAM)* | R748–R756 | 65 | **0.6154** — **4.51× inflation** |
| distinctive | R700–R747 | 174 | **0.1954** — with 8 more rounds of exposure |

⛔ **"Appears in a deliverable" is NEAR-FORCED** — every round appends its own numbers to this file.
Printed, **excluded from the verdict**. ⛔ **A number can only be read by later rounds**, so decline
toward the present is partly mechanical — which is why the older era was measured.

⚠ **The confound bounds it, and was written before the run:** later rounds cite a round's **ID** 30
times against **9** value-reprints — **3.3×**. `13.6%` measures *numbers reprinted*, not *findings
used*, and the two are not converted into each other.

**Controls — 5 PASS, 0 FAIL.** POSITIVE `0.8000` read by [754, 756, 757, 758], band `0 < 2 ≤ 6` ·
g=0 a fabricated value read by **0** · NEGATIVE shuffled publishing rounds give 0.44–0.49 against the
real **0.1364** · SHAM as above · PLACEBO 0 of 110.

⛔ **Two defects in this round's own instrument, both caught by its controls.** ① The tracer scanned
**its own `run.py`**, detecting the fabricated constant it defines and counting itself as a reader —
**the instrument was part of its own corpus** *(ledger 1049)*. ② The **two-seed check** caught a real
non-determinism: `published()` returns a **set**, and hash-seed-dependent iteration resolved the
first-publisher tie-break differently, so a different value could win a tie and carry a different
reader set *(ledger 1050)*.

**⭐ The four most-read values are all R753's — `0.8000 / 0.3814 / 0.1793 / 0.6207` — and all four were
subsequently corrected.** The numbers this arc reused are the ones that turned out to be wrong: a
working retraction chain, and also reuse *for correction* rather than for building *(ledger 1052)*.

**Verdict — `WORLD B`.** The debt is near zero. **The provenance sub-arc closes** *(ledger 1051)*.
What outlives it is three instruments, not their rates: the one-arc lookup defect *(R757)*, the
parent-commit pin *(R758)*, and the 4.51× spurious-match price on non-distinctive values *(here)*.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 31415 **after** the set-ordering
repair, **both writes confirmed to disk**.

## R760 · clause ③ by RULE instead of by NAME — the `16 vs 5` tension dissolves

**Question.** ③ is implemented as **four literal arm names**; R520 and R729 showed it **fails open**,
and R745 measured the cost — the census admits **3 target-reading objects** ③ is meant to exclude.
The builder names those rules exactly at `select_core.py:102`. **What does ③-by-rule cost?**

**⚠ P4 on both questions.** R509 killed a **behavioural** ③′ (*"makes the same vacuity harder to
see"*); R623 is a documentation-anchor rule. **A rule-based PROVENANCE ③ keeps ③'s type and changes
only its implementation — that is the gap.**

| clause ③ | admitted tags | admitted **objects** | excluded tags |
|---|---|---|---|
| **name** (current) | **16** | **9** | 76 |
| **RULE** | **9** | **5** | 83 |
| inverted *(block selectors)* | 14 | 8 | 78 |

**The 7 newly excluded** — `greedy_k4_greedy_kA/kB`, `indep_k4_indep_kA/kB`, `oracle_k4_08bR`,
`oracle_k4_oracle_kA/kB` — **are exactly R729's seven and R730's four objects.** Three rounds converge
on the same set from different directions. **All 5 committed members survive**, and `② ∧ ③rule` admits
**9 tags / 5 objects — NON-VACUOUS**.

⇒ **The extension over today's 92-arm population is 5 objects, identical to the committed one. The
`16 vs 5` tension was ③ being a list** *(ledger 1054)*.

**⛔ Two results were FORCED and are labelled.** **D1** the rule set is a **superset** of the blocklist
(every blocklisted name carries a target-reading prefix, asserted in code), so *"rule excludes more"*
is algebra and only the **size** measures. **D2** no committed member carries a target-reading prefix,
so the committed 5 are **invariant** — stated before the run, verified 5/5 on the outcome.

**⭐ The SHAM prices the list.** Five **random** size-4 blocklists admit **[20, 20, 19, 20, 19]**,
mean **19.6**, against the actual blocklist's **16** and the rule's **9**. **The four names buy 3.6
arms over an arbitrary list; the rule buys 10.6** *(ledger 1055)*.

**Controls — 6 PASS, 0 FAIL.** PROVENANCE all three source facts hold, else **exit 2** · POSITIVE
rule-③ **excludes** `oracle_k4_oracle_kA` and **keeps** `topw_k4`, against a band where a ③ blocking
**nothing** and one blocking **everything** are both unable to separate them · g=0 **0 UNPARSED** tags,
none silently admitted or blocked · NEGATIVE inverting the rule changes the set (14 vs 16), so **③ is
not decoration** · SHAM as above · **PLACEBO name-③ reproduces R728's committed 16 EXACTLY — the
harness *is* the census.**

⚠ **This repairs ③'s IMPLEMENTATION, not whether ③ is the right CLAUSE** — that still requires the
external criterion the impossibility register has always named.

**Reproducibility.** Two `PYTHONHASHSEED` runs, both writes confirmed to disk.

## R761 · ②-robustness over the full reference class, and its residual on A2 rank

**Scope.** population = 27 arms (R294's 18 k=4 census arms ∪ R729's seven target-reading tags ∪ the
five committed extension members); instrument = R294's estimator (paired cluster bootstrap, NBOOT
1200, seed 31337, MDE floor, three-valued `verdict`), reproduced at **1e-6 on 16/16** stored `c2`;
baseline = **the swept axis**, all C(16,4) = **1,820** size-4 subsets of `sat_genericpool16`; regime =
first release, home judge, **968** prompts. `promptecho_sham` has coverage **398/968** and is flagged;
the identity is recomputed on the 26 coverage-complete arms and is unchanged.

**rob(a)** = share of the 1,820 references at which arm *a* clears ②.

| arm | A2 | rob | ③name | ③rule |
|---|---|---|---|---|
| `oracle_k4` · `oracle_k4_oracle_kA` · `oracle_k4_oracle_kB` | 0.6283 | 1.0000 | 1 of 3 | BLK |
| `greedy_k4_greedy_kA` · `greedy_k4_greedy_kB` | 0.6226 | 1.0000 | . | BLK |
| `oracle_k4_fit1` | 0.6142 | 1.0000 | BLK | BLK |
| `greedy_k4_fit1` | 0.6106 | 1.0000 | BLK | BLK |
| `indep_k4_indep_kA` · `indep_k4_indep_kB` | 0.6031 | 1.0000 | . | BLK |
| `indep_k4_fit1` | 0.5941 | 1.0000 | BLK | BLK |
| `coval_core` | 0.5665 | 0.9978 | . | . |
| **`oracle_k4_08bR`** | **0.5649** | **0.9401** | **.** | **BLK** |
| `topw_k6` | 0.5641 | 0.9863 | . | . |
| `topw_k4` | 0.5642 | 0.9835 | . | . |
| `topw_k3` | 0.5632 | 0.9703 | . | . |
| `topw_k8` | 0.5593 | 0.8857 | . | . |
| `generic` | 0.5514 | 0.7780 | . | . |
| `gen` | 0.5352 | 0.0396 | . | . |
| the 6 sham/random/topabs/topvar/topwvar arms | 0.4828–0.5040 | 0.0000 | . | . |
| `promptecho_sham` *(coverage 398)* | 0.2599 | 0.0000 | . | . |

**E2 · inversions** rob vs mean A2: **4 of 351** pairs — `oracle_k4_08bR` vs `topw_k3` (ΔA2 +0.0017,
Δrob −0.0302), vs `topw_k4` (+0.0007, −0.0434), vs `topw_k6` (+0.0008, −0.0462), and `topw_k4` vs
`topw_k6` (+0.0001, −0.0027). SHAM S1, random ordering, 200 draws: **131.3 [89, 174]**, computed
ceiling 176.

**E3 · Jaccard with { rob = 1.0 }** ③name **0.400** · ③rule **0.909** · SHAM S2 random size-11
blocklist **0.254 [0.105, 0.500]**, exact-match rate **0.000**. Threshold curve
t ∈ {1.00, 0.99, 0.95, 0.90, 0.75} → ③name {0.400, 0.364, 0.286, 0.267, 0.235},
③rule {0.909, 0.833, 0.667, 0.733, 0.647}; **set equality at none**.

**Controls.** PROVENANCE 16/16 at 1e-6 · POSITIVE R527's committed `coval_core_by_spec` **8/8**
(band: admit-everything 7/8, admit-nothing 1/8) · g=0 planted null **0.0050 of 200** (band [0, ~0.50])
· NEGATIVE `coval_core` 0.9978 vs permuted **0.8422 [0.8242, 0.8599]**, `oracle_k4` 1.0000 vs 1.0000
· PLACEBO four `*_sham` arms **0.0000**. **WORLD C.**

**Derived, not measured.** ① rob is monotone in A2 up to the paired SE, so the arm ordering is forced
and only the residual measures. ② the 1,820-wide bootstrap is exact at marginal cost (linearity of the
bootstrap mean; `var(x−y)` by one matrix product) — asserted at 4 probe cells. ③ the exact self-cell
is `UNRESOLVED` by `verdict()`'s first branch.

## R762 · the resolution behind R761's ordering, and the interval rob never had

**Scope.** population = R761's 27 arms unchanged (so the rounds are comparable), of which **5 pairs
are degenerate** — identical per-prompt vectors, one object under R730 — leaving **346** resolvable
pairs of 351; instrument = R294's estimator, reproduced **exactly on 27/27** arms before any
contradiction was permitted; baseline = all 1,820 references; regime = first release, home judge,
968 prompts.

**E1 · resolution of a between-arm ΔA2** paired MDE median **0.0136**, IQR **[0.0097, 0.0149]**,
min 0.0031, max 0.0237. A second and **different** floor, R415's committed run-to-run re-selection
shift, is **0.116489**; the two are not interchangeable and both are reported.

**E2 · the floor curve**

| floor | surviving pairs | inversions | SHAM mean | P(sham = 0) |
|---|---|---|---|---|
| 0 | 346 | 4 | — | — |
| 0.5× MDE | 319 | **0** | 3.70 | 0.000 |
| 1× MDE | 304 | **0** | 3.54 | 0.000 |
| 2× MDE | 280 | **0** | 3.35 | 0.000 |
| 0.116489 | 81 | 0 | 0.90 | 0.375 |

R761's 4 inverting pairs collapse to **2 independent events** (`oracle_k4_08bR`, `topw_k4`).

**E3 · nested-bootstrap intervals on rob** (120 outer × 300 inner; POSITIVE-2: inner 1200 → 300 moves
rob by 0.0000 on all 27)

| arm | rob | 2.5% | 97.5% | share of outer draws at 1.0 |
|---|---|---|---|---|
| `oracle_k4` | 1.0000 | 1.0000 | 1.0000 | 1.000 |
| `coval_core` | 0.9978 | 0.8943 | 1.0000 | 0.250 |
| `topw_k6` | 0.9863 | 0.8463 | 1.0000 | 0.092 |
| `topw_k4` | 0.9835 | 0.8411 | 1.0000 | 0.067 |
| `topw_k3` | 0.9703 | 0.7997 | 1.0000 | 0.067 |
| `oracle_k4_08bR` | 0.9401 | 0.6077 | 1.0000 | 0.092 |

paired `08bR − coval_core` = **−0.0932 [−0.3584, +0.0212]**, not separated.

**Instrument identity of `oracle_k4_08bR`** — anchor test, both controls: matches `sat08_full.npz`
(0.8B) at **0.4609**, `sat_full.npz` (default) at **0.0345**; `oracle_k4` matches them at **0.0342**
and **0.5342**. `select_core.py:75` makes `--tag-suffix` mandatory off-default; R416 measured 91.1%
of this arm's prompts changing selection.

**Controls.** PROVENANCE 27/27 exact (exit 2 otherwise) · POSITIVE-1 346/346 at 2× MDE, none at 0.5× ·
POSITIVE-2 worst |Δrob| 0.0000 · g=0 planted zero never resolved · NEGATIVE pairing destroyed → MDE
×**1.80 [0.96, 3.70]** · PLACEBO 215 pairs at |ΔA2| > 0.05, **0** inversions · SHAM as tabled.
**WORLD A**, E3 verdict **UNRESOLVED**.

**Derived, not measured.** ① a floor can only remove inversions (monotone by subset), so only reaching
zero measures, and the size-matched random subset is what attributes it. ② three of R761's four pairs
are one arm against three arms lying within 0.0010 of each other — one event, three labels.

## R763 · whether a round moved the definition, measured three ways

**Scope.** population = the 24 rounds R739–R762 (matched to R664's n = 24 so the eras compare);
instrument = three classifiers, each with its own control set; baseline = R664's committed
**0 of 24** over R640–R663; regime = this repository, this tree_sha.

| unit | what it tests | % of page | count / 24 | own sham 95% | admissible |
|---|---|---|---|---|---|
| **C1** | R664's keyword rule on the headline | — | **1** | R664's control set | **YES** |
| C2 | commit edits `## The definition` block | 36.7% | 9 | [4, 12] | **NO** |
| C3 | commit edits a clause bullet | 3.1% | 2 | [0, 2] | **NO** |

**Rounds editing `STATEMENT.md` at all: 23 of 24**, so a positional unit covering *p* of the page is
hit at ≈ *p* of them by chance — C2 caught 9 of 23 = 39% against a 36.7% block.

**2×2 (C1 × C2).** OBJECT/OBJECT **1** (`R760`) · OBJECT/apparatus **0** · apparatus/OBJECT **8**
(`R739 R740 R741 R742 R745 R746 R761 R762`) · apparatus/apparatus **15**.

**Controls.** POSITIVE-1 C1 reproduces R664's committed `0 of 24` on R664's own era **exactly** ·
POSITIVE-2 C1 fires on R527/R519, C2 fires on R760 · NEGATIVE C1 not OBJECT on R654; 1 round touches
no `STATEMENT.md` and C2 fired on 0 of it · g=0 empty headline and empty diff both negative ·
PLACEBO keyword-free headline negative · SHAM ×2 as tabled. **WORLD A on the only admissible unit.**

**Combined with R664: 1 object headline in 48 rounds** (R640–R663: 0 of 24; R739–R762: 1 of 24).

**Impossible here, and now named with what it would require.** *Whether a round moved the definition*
is **not reconstructible from diffs** — two positional units, two sham failures. It would require a
**per-round declaration recorded at the time**: each README naming the clause it moves or naming NONE.
Intent is not in a diff.

## R764 · the three readings of ③ over 86 arms and ②'s whole baseline curve

**Scope.** population = **86** arms with full 968-prompt coverage (R534: 41); instrument = R294's
estimator for ②, `select_core.py`'s own selection expressions for ③; baseline = **the swept axis**,
8 percentiles of the 1,820-subset class including the published one; regime = first release, home
judge, this tree_sha.

**Readings, corrected from R534's own text before any code was written.**

| reading | excludes | admits |
|---|---|---|
| ③-rank | rank | weight, sat, weight+sat, neither |
| ③-any | rank, weight, weight+sat | **sat**, neither |
| ③-judge | rank, weight, sat, weight+sat | neither |

R534 computed ③-any and ③-judge with the same expression; its headline says *"a judge is not an
annotator"*, which admits the sat class to ③-any. Nesting `judge ⊆ any ⊆ rank` is **derived**.

**E1 · partition over 86 arms** rank **17** · weight **20** · sat **3** (`topvar_k4`, `_08b`,
`_08bR`) · weight+sat **3** (`topwvar_k4`, `_08b`, `_08bR`) · neither **42** · UNPARSED **1**
(`generic_reprov`, a re-provenance run of `generic` — **0 objects** under R730's partition).

**E3 · the grid**, tags (objects):

| baseline | \|②\| | ③-rank | ③-any | ③-judge |
|---|---|---|---|---|
| p000 | 24 | 11 (9) | **2 (2)** `gen`, `generic` | **2 (2)** |
| p005 | 23 | 10 (8) | **1 (1)** `generic` | **1 (1)** |
| p025 | 21 | 9 (7) | **1 (1)** `generic` | **1 (1)** |
| p050 | 21 | 9 (7) | **1 (1)** `generic` | **1 (1)** |
| p075 | 18 | 7 (5) | 0 | 0 |
| p095 | 16 | 6 (4) | 0 | 0 |
| **published** | 17 | **6 (4)** | **0** | **0** |
| p100 | 10 | 0 | 0 | 0 |

**Controls.** PROVENANCE R534's 41-arm partition reproduced exactly (exit 2 otherwise) · POSITIVE
four arms into four classes, band from both degenerate ends · g=0 `zzz_k4` UNPARSED not `neither` ·
NEGATIVE 200 random 5-class partitions → ③-any at published **6.90 [4, 11]** vs real **0** · PLACEBO
3 `*_sham` arms in 0 extensions · SHAM ② with no clause = the `|②|` column. **WORLD B** (object
unit; the tag-unit branch says C — both printed).

**Excluded, on evidence, named.** 7 foreign-key-schema artifacts (`transport_*`, another corpus);
5 with partial prompt coverage (`coval_core_2bA/2bB`, `promptecho`, `promptecho_sham`,
`provenance_probe`).

## R765 · the comparator in the census, and the pipeline's variance decomposition

**Scope.** population = **88** arms with a committed `core_*.json`; instrument = string equality on
per-prompt criterion sets, plus R294's estimator; baseline = all 8 percentiles as R764; regime =
first release, home judge, 968 prompts, this tree_sha.

**E1 · containment against `genericpool16`.** Comparator-identical (exact prefix on every shared
prompt): **`generic` alone**, 968/968, k=4, overlap 1.0000. `gen` 0.0010 · `full` 0.0000 ·
`coval_core_sham` 0.0000 · all 84 others 0.0000. **`coval_core` has no committed core JSON** (R441).

**E2 · ③-any with the comparator excluded.**

| baseline | ③-any as R764 ran it | comparator excluded |
|---|---|---|
| p000 | `gen`, `generic` | **`gen`** (pool-overlap 0.0010) |
| p005 · p025 · p050 | `generic` | — |
| p075 · p095 · published · p100 | — | — |

**1 of 8 cells**, not 4. `POOL[0:4]` at percentile 93.7 clears ② below itself by **construction**.

**E3 · the variance decomposition, from 34 identical-criteria groups.**

| class | pairs | \|Δ A2\| mean | min | max |
|---|---|---|---|---|
| same judge, identical criteria | **10** | **0.0000** | 0.0000 | 0.0000 |
| different judge, identical criteria | **38** | **0.0969** | 0.0597 | 0.1799 |
| same judge, re-selected criteria *(R415)* | — | **0.1165** | — | — |

Exact same-judge pairs: `topw_k4`/`_detA`/`_detB` · `random_k4_s0`/`_ctlS0` · `random_k4_s1`/`_ctlS1`
· `oracle_k4`/`_oracle_kA`/`_oracle_kB` · `greedy_k4_greedy_kA`/`kB` · `indep_k4_indep_kA`/`kB`.

**Open anomaly.** `generic` vs `genericpool16[:4]` = **0.0009 [−0.0006, +0.0024]**, identical on
**896/968** where every other same-judge pair is exact. Candidates: the pool tensor sums by index
order while the core JSON lists by string order, or the two artifacts scored different response sets.
The registered confound check passed on all pairs it could evaluate (**0 failures**) and cannot
evaluate this one.

**Controls.** PROVENANCE R764's 8×3 grid reproduced (exit 2 otherwise) · POSITIVE `generic` 1.0000
**and** `gen` 0.0010, band from both degenerate ends · g=0 shuffled pool → prefix 0.0000 · SHAM random
size-4 subsets → prefix 0.0000, subset 1.0000 · PLACEBO `full` 0.0000 · NEGATIVE **uninformative by
construction** — `generic` has **1** distinct criterion set across 968 prompts, so a derangement
changes nothing. **WORLD B.**

## R766 · the across-pass scoring floor, and why the thread is decision-inert

**Scope.** population = the 15,488 cells (968 prompts × 4 criteria × 4 responses) shared by
`sat_generic` and `sat_genericpool16[0:4]`, criterion strings identical (R765, 968/968); instrument =
direct value comparison, plus R294's estimator for the propagation; regime = first release, home
judge, this tree_sha.

**E1 · the discrepancy.** differing cells **5,235 / 15,488 = 0.3380** · differing prompts **957 / 968**
· \|Δ\| mean **0.008574**, median **0.000000**, p95 **0.030967**, max **0.062419** · signed mean
**+0.000613** · **share(`generic` > `pool`) = 0.1793**, outside the registered symmetric band
[0.40, 0.60] ⇒ **systematic offset, not run-to-run variance**.

**E2 · identical-criteria pairs.** 48 total; **16 carry a replication marker** (`_det`, `_ctl`,
`_kA`, `_kB` — determinism controls, or the same object under R730); 32 across-pass candidates.
⚠ LOWER BOUND: "same pass" is recorded nowhere in the release and is inferred from naming and R730.

**E3 · propagation to the decision.**

| | percentile of `POOL[0:4]` in its 1,820-subset class |
|---|---|
| committed *(R527)* | 93.7 |
| recomputed | **93.74** |
| perturbed ×200 at sd = 0.012816 | **94.16 [91.59, 96.59]** |

The point lies inside the interval — **the discrepancy cannot move any ② verdict**.

**Controls.** POSITIVE nested `topw_k` sweep, worst spread **0.000e+00** · g=0 artifact vs itself **0**
differing · NEGATIVE two different criteria differ on **0.9287** of cells · PLACEBO `topw_k4` vs
`_detA` at the **cell** level **0** differing · SHAM `generic` vs `gen` \|Δ\| mean **0.190755** vs
**0.008574**, so criterion identity buys **95.5%**. **WORLD B.**

**Status of the two published zeros.** R419 (`--limit 200`) and R765 (10 pairs) both measured
**within-pass** determinism and both are correct at that scope. The **across-pass** floor is
`UNVERIFIED` — neither measured nor refuted here.

**Impossible, named.** Whether two artifacts came from one scoring pass would need a run identifier
the release does not carry · whether a sat file scored the strings its core JSON lists would need
criterion **strings** in the npz, which stores **indices** · whether the offset is temperature, judge
version or batching would need the scoring harness's logs.

## R767 · the five committed members, three-valued

**Scope.** population = the five committed extension members plus the `topw_k` family and 3 placebo
arms; instrument = R294's estimator with `report.verdict`, B ∈ {1200, 4800, 19200}; baseline =
`POOL[0:4]` published (A2 **0.550436**) and the 8-point percentile curve; regime = first release,
home judge, **968** prompts, this tree_sha.

| arm | A2 | eff | CI | MDE | eff/MDE | verdict |
|---|---|---|---|---|---|---|
| `coval_core` | 0.5665 | +0.0160 | [0.0083, 0.0241] | 0.0106 | 1.509 | BEATS |
| `topw_k6` | 0.5641 | +0.0137 | [0.0059, 0.0209] | 0.0104 | 1.311 | BEATS |
| `topw_k4` | 0.5642 | +0.0137 | [0.0054, 0.0216] | 0.0109 | 1.264 | BEATS |
| `topw_k3` | 0.5632 | +0.0127 | [0.0045, 0.0203] | 0.0111 | 1.152 | BEATS |
| **`topw_k8`** | 0.5593 | **+0.0089** | **[0.0009, 0.0163]** | **0.0107** | **0.827** | **BELOW RESOLUTION** |

Unchanged at B = 4800 and B = 19200.

**The `topw_k` family** (the registered confound): k=1 **−0.0249 / −1.825 LOSES** · k=2 +0.0031 /
0.263 UNRESOLVED · k=3 BEATS · k=4 BEATS · **k=6 +0.0137 / 1.311 BEATS (peak)** · k=8 BELOW
RESOLUTION · k=12 −0.0124 / −1.094 LOSES. An inverted U with eff/MDE monotone falling 6 → 8 → 12.

**The convention, measured by the SHAM** (`mde=None`, the floor absent): exactly **1** verdict
changes — `topw_k8` → BEATS. **Extension = 4 with the floor, 5 without.**

**Across the baseline curve** — p000·p005·p025·p050·p075: **5 / 5** (both conventions agree) ·
**p095: 4 / 5** · **published: 4 / 5** · p100: 0 / 1.

**Controls.** POSITIVE 4 of 5 return BEATS, band from both degenerate ends · g=0 baseline vs itself
eff 0.000000 → **UNRESOLVED** · NEGATIVE `topw_k8` with the pairing destroyed ×200 → **200/200
UNRESOLVED** · PLACEBO `coval_core_sham`, `topw_k4_sham`, `gen_sham` → **LOSES**. **WORLD A.**

**This explains R760 vs R764.** R760's `admitted_rule` = 9 tags / 5 objects; R764's published
`3-rank` = 6 / 4. Two tags are R764's declared coverage exclusion (`coval_core_2bA/_2bB`, 200 of 968
prompts); the third, `topw_k8`, is the three-valued verdict read two-valued.

## R768 · the pairwise ordering matrix over the extension

**Scope.** population = the 5 committed extension members and the 7-arm `topw_k` family (11 distinct
arms); instrument = R294's estimator on **paired per-prompt differences**, B = 1200, `report.verdict`;
baseline = **none — these are arm vs arm**, the baseline appears only in controls; regime = first
release, home judge, 968 prompts, this tree_sha.

| a | b | eff | CI | MDE | verdict |
|---|---|---|---|---|---|
| `coval_core` | `topw_k8` | +0.0072 | [+0.0012, +0.0131] | 0.0085 | BELOW RESOLUTION |
| `topw_k4` | `topw_k8` | +0.0049 | [−0.0001, +0.0101] | 0.0076 | UNRESOLVED |
| `topw_k6` | `topw_k8` | +0.0048 | [+0.0009, +0.0087] | 0.0056 | BELOW RESOLUTION |
| `topw_k3` | `topw_k8` | +0.0039 | [−0.0024, +0.0095] | 0.0087 | UNRESOLVED |
| `coval_core` | `topw_k3` | +0.0033 | [−0.0031, +0.0096] | 0.0090 | UNRESOLVED |
| `coval_core` | `topw_k6` | +0.0024 | [−0.0030, +0.0075] | 0.0079 | UNRESOLVED |
| `coval_core` | `topw_k4` | +0.0023 | [−0.0038, +0.0084] | 0.0085 | UNRESOLVED |
| `topw_k3` | `topw_k4` | −0.0010 | [−0.0048, +0.0028] | 0.0054 | UNRESOLVED |
| `topw_k3` | `topw_k6` | −0.0009 | [−0.0062, +0.0040] | 0.0076 | UNRESOLVED |
| `topw_k4` | `topw_k6` | **+0.0001** | [−0.0041, +0.0044] | 0.0063 | UNRESOLVED |

**Resolvable by verdict: 0 of 10.** Surviving BH on the bootstrap p with no MDE floor: **2** —
`topw_k6 vs topw_k8`, `coval_core vs topw_k8`. The gap between those two counts is the MDE floor.

**Multiplicity**: 31 unordered pairs (D3 — antisymmetric, not 62), BH at q = 0.05, **17 survivors**,
all k-family pairs involving `k1`, `k2` or `k12`, the arms that lose outright.

**The ranking decomposition.** by **eff**: k4, k6, k3, k8, k2, k12, k1 · by **eff/MDE**: k6, k4, k3,
k8, k2, k12, k1 · by eff/**pooled** sd (sd removed): k4, k6, … — **1 transposition vs 0**, so the
"peak at k=6" is exactly one sd-driven inversion. `MDE = z·sd/√n`, so eff/MDE ranks by eff/sd.

**Controls.** POSITIVE `coval_core` vs `gen_sham` **+0.0837 [+0.0733, +0.0936]**, MDE 0.0153, BEATS ·
g=0 arm vs itself eff **0.000000** → UNRESOLVED · PLACEBO `topw_k4` vs `_detA` eff **0.000000** ·
NEGATIVE pairing destroyed ×200 → MDE **×2.25 [2.18, 2.32]** · CONFOUND corr(criterion overlap,
|eff|/MDE) = **−0.3949** over 27 pairs, so resolution does not track overlap. **WORLD A.**

## R769 · contains vs consumed, and the n each ordering would require

**Scope.** population = the release's **1,078** prompts against the estimator's **968**; instrument =
R294's estimator on paired per-prompt differences; regime = first release, home judge, this tree_sha.

**Contains vs consumed.** prompts 1,078 / 968 · annotations **18,384 / 15,593 = 0.8482** · annotators
per prompt median **16** on both sides — **the annotator dimension is exhausted**.

**Why the 110 drop.** absent from the base arm only **0** · absent from the pool only **0** · fewer
than 2 annotators **0** · **both coverage clauses at once 110**. **Recoverable for the five committed
arms: 0.** So 968 is the correct population and the campaign's numbers carry no hidden scope.

**The power curve** (`coval_core` vs `topw_k4`, 50 subsamples per n; the 1/√n law asserted, not fitted):

| n | MDE | sd | law | ratio | sham (with replacement) | negative / real |
|---|---|---|---|---|---|---|
| 100 | 0.02648 | 0.00304 | 0.02653 | 0.998 | 0.02689 | 2.22 |
| 200 | 0.01871 | 0.00160 | 0.01876 | 0.998 | 0.01864 | 2.23 |
| 400 | 0.01347 | 0.00064 | 0.01327 | 1.015 | 0.01337 | 2.23 |
| 600 | 0.01079 | 0.00038 | 0.01083 | 0.996 | 0.01082 | 2.26 |
| 800 | 0.00935 | 0.00017 | 0.00938 | 0.997 | 0.00932 | 2.26 |
| 968 | 0.00853 | 0.00000 | 0.00853 | 1.000 | 0.00796 | 2.17 |

Worst deviation **1.5%**.

**Required n per pair — a DERIVATION from the measured sd under a stated stability assumption:**
`topw_k6`/`topw_k8` **1,293** · `coval_core`/`topw_k8` **1,373** · `topw_k4`/`topw_k8` **2,376** ·
`topw_k3`/`topw_k8` **4,880** · `coval_core`/`topw_k3` **7,132** · `coval_core`/`topw_k6` **10,761** ·
`coval_core`/`topw_k4` **13,346** · `topw_k3`/`topw_k4` **28,456** · `topw_k3`/`topw_k6` **63,241** ·
**`topw_k4`/`topw_k6` 9,534,441**.

**Controls.** POSITIVE the 1/√n law to 1.5% · g=0 reproduces R768's committed MDEs exactly · NEGATIVE
pairing destroyed → ratio **2.17–2.26** at every n · SHAM drawing with replacement gives the same MDE
(0.993 at n = 400), so only NEW prompts move the curve · PLACEBO self-difference MDE **0.0** ·
CONFOUND **UNIDENTIFIED** — 0 recoverable, so the sd comparison could not be made. **WORLD B.**

## R770 · the variance decomposition, and the partition test

**Scope.** population = 968 prompts, the 5 committed members (10 pairs); instrument = annotator-level
agreement vectors, paired per-prompt differences; regime = first release, home judge, this tree_sha.

**E1 · decomposition** (within = annotator draw, between = prompts):

| pair | between | within | ratio | within share | max MDE gain |
|---|---|---|---|---|---|
| `coval_core`/`topw_k3` | 0.009901 | 0.001867 | 5.30 | 0.1587 | 8.3% |
| `coval_core`/`topw_k4` | 0.008970 | 0.001689 | 5.31 | 0.1585 | 8.3% |
| `coval_core`/`topw_k6` | 0.007637 | 0.001529 | 4.99 | 0.1668 | 8.7% |
| `coval_core`/`topw_k8` | 0.008982 | 0.001546 | 5.81 | 0.1469 | 7.6% |
| `topw_k3`/`topw_k4` | 0.003657 | 0.000659 | 5.55 | 0.1527 | 8.0% |
| `topw_k3`/`topw_k6` | 0.007135 | 0.001228 | 5.81 | 0.1469 | 7.6% |
| `topw_k3`/`topw_k8` | 0.009287 | 0.001464 | 6.34 | 0.1362 | 7.1% |
| `topw_k4`/`topw_k6` | 0.004871 | 0.000823 | 5.92 | 0.1446 | 7.5% |
| `topw_k4`/`topw_k8` | 0.007177 | 0.001139 | 6.30 | 0.1370 | 7.1% |
| `topw_k6`/`topw_k8` | 0.003805 | 0.000635 | 5.99 | 0.1431 | 7.4% |

**E2 · heterogeneity** I² **0.833–0.864**; `mean/sd` **0.0009–0.0779**, so a balanced sign split is
nearly forced (D3) and the observed `d > 0` shares of **0.16–0.32** are **not** read as a minority
carrying the mean, because the complement includes exact ties.

**E3 · partition test** — a flip = two levels with opposite-sign means, both clearing their own MDE.
S1 annotator count **0** · S2 response-set size **0** · S3 baseline A2 **0**. **90 cells, 0 flips**;
sham (200 random equal-sized partitions) **0.00 [0, 0]**; negative (200 label permutations) **0.00**.

**Controls.** POSITIVE a centred, swept plant: 0× **False**, 0.5× False, 1.0× False, **2.0× True** —
the registered band is *0× must not fire, 2× must*; 1× is the test's own 50%-power point and was never
a registered criterion. g=0 delta 0 finds nothing · PLACEBO an arm against itself, variance **0.0**,
flips 0. **WORLD A.** ⚠ Resolution: a flip needs ≳2× the half-sample MDE ≈ **0.024**.

## R771 · the correlation structure of the ten difference vectors

**Scope.** population = 968 prompts, 5 committed members, their 10 pairwise differences; instrument =
per-prompt A2 over all annotators, Pearson correlation across prompts; baseline = a **generated**
independence model, not a chosen number; regime = first release, home judge, this tree_sha.

**Rank and spectrum.** rank **4** (forced: 5 arms − 1); eigenvalues **[3.791, 2.957, 1.771, 1.481,
0, 0, 0, 0, 0, 0]**; leading share **0.3791**; uniform reference at rank 4 = **0.2500**.

**E1 · residual variances**, identified from 10 equations in 5 unknowns (`var(d_ab) = v_a + v_b`):
`coval_core` **0.005878** · `topw_k3` **0.004042** · `topw_k8` **0.003799** · `topw_k4` **0.002273** ·
`topw_k6` **0.001864**. Relative fit residual **0.1748**, all positive → admissible. A negative `v`
would have refuted the model at that arm; clipping was forbidden in advance.

**E2 · observed vs the independence prediction** (computed per pair from the fitted `v`, never a 0.5
constant): arm-sharing (n=30) |observed| **0.4864** vs |predicted| **0.4938**, **excess −0.0074**;
disjoint (n=15) observed **+0.0312** vs predicted **0**.

**E3 · spectrum vs simulation.** sham — 200 draws of independent residuals at the fitted variances —
**0.3072 [0.2974, 0.3172]**; observed **0.3791**, above the band.

**Calibration.** The positive control's monotone dose curve (differential loadings
[+1.0, +0.5, 0, −0.5, −1.0]): λ 0.00 → 0.3121 · 0.25 → 0.3183 · 0.50 → 0.3556 · 1.00 → 0.4843.
Observed 0.3791 interpolates to **λ ≈ 0.59 × the residual sd**.

**Controls.** POSITIVE monotone, detected from λ = 0.25, not at 0 · g=0 λ = 0 inside the sham band ·
SHAM as above · NEGATIVE 200 independent prompt permutations → **0.1164 [0.1127, 0.1207]** · PLACEBO
`topw_k4` vs `_detA` sd **0.0** and excluded by construction.
**WORLD: none claimed — the two estimands split, and A and B each required both.**

⛔ **A factor loading EQUALLY on all arms is invisible in differences** — `d_ab` retains only
`λ(√v_a − √v_b)·f`, which vanishes at equal variances. The first plant was that object and produced
0.308–0.312 at every loading including 1.0.

## R772 · the per-prompt separability scale

**Scope.** population = 968 prompts, 5 committed members, 10 pairwise differences; instrument =
per-prompt A2 over all annotators; baseline = a generated independence model with a planted
multiplicative scale; regime = first release, home judge, this tree_sha.

**E1 · |d| co-movement.** disjoint (15 cells, admissible) **+0.2974** · arm-sharing (30 cells, co-move
with no scale by D2) +0.4560 · independence reference over 200 simulations **+0.0000 [−0.0314,
+0.0323]**. Dose curve: width 0.25 → +0.0950 · 0.50 → +0.2731 · 1.00 → +0.5204 ⇒ observed calibrates
to a **lognormal width ≈ 0.55**.

**E2 · what the scale is.** corr(`c`, per-prompt annotator agreement) **+0.1246** · corr(`c`,
per-prompt within-SE) **+0.5278** (r² **0.2786**) against a pre-registered line of **0.50** — fires by
**+0.0278**. `c(p)` quantiles **[0.0000, 0.0055, 0.0333, 0.0667, 0.3042]**, **223 zeros**.

**E3 · leave-one-pair-out normalisation** (the all-pairs version is circular and its 0.3330 is
inadmissible): raw leading share **0.3791** → LOPO **0.3298**; SHAM, a random draw from `c`'s own
distribution, **0.3822 [0.3541, 0.4090]**; NEGATIVE, a permuted `c`, **0.3826 [0.3528, 0.4099]**.
Both controls **raise** the share; only the aligned scale lowers it. Divisor floor **0.00893**.

**Controls.** POSITIVE a **multiplicative** plant, monotone, detected from width 0.25 not at 0 · g=0
width 0 inside the band · PLACEBO `topw_k4` vs `_detA` max |d| **0.0** · SHAM/NEGATIVE as above.
**WORLD B — a partly noise-amplitude map**, called on a 0.028 margin, with r² printed beside the label.

## R773 · the 223 ties, and the invariance of eff/MDE to dropping them

**Scope.** population = 968 prompts split into **223 tied** and **745 discriminating** — two
populations, never pooled; instrument = A2 (sign-based) plus a magnitude-sensitive alternative, both
stated; regime = first release, home judge, this tree_sha.

**E1 · the invariance (a DERIVATION).** Dropping exact zeros scales the effect by `n_f/n_d` and the
MDE by `sd_ratio·√(n_f/n_d)` — the same factor to O(μ²/σ²), μ/σ = 0.024. Measured over ten committed
pairs: ratios **0.9998–1.0008**, **verdict changes 0 of 10**, `n_required × 0.7696`.

**E2 · on the 223 tied prompts.** sign vectors identical **0.9740** [0.9596, 0.9910] · satisfaction
cosine distance **0.0046** [0.0014, 0.0082] · quantiles **[0.0002, 0.0008, 0.0021, 0.0051, 0.0185]** ·
share > 0.20 **0.0000** · share < 0.05 **0.9969**.

**E3 · a magnitude-sensitive estimator on the same prompts.** Largest eff/MDE **0.570**
(`topw_k3`/`topw_k4`); **0 of 10** pairs separate. ⚠ A different estimand — *"does the arm order the
responses like the human"* vs *"does its sign pattern match"* — so a separation would not have shown
A2 wrong.

**Controls.** POSITIVE `coval_core` vs `gen_sham` on tied prompts **0.0358** against the largest
committed pair **0.0082** (**4.36×**), band computed on this subset [−8.46e-18, 0.2794] · g=0
**−8.46e-18**, PLACEBO **−4.98e-19**, both at tolerance **1e-9** (a floating-point cosine identity is
not exactly zero) · SHAM the same distance on the 745 discriminating prompts **0.0066** vs tied
**0.0046** (0.696) · NEGATIVE 200 random equal-sized subsets **0.0062 [0.0055, 0.0069]**.
**WORLD A — STRUCTURAL.**

## R774 · who owns the scale — the prompt, or the five arms that defined it

**Scope.** population = 968 prompts; committed family = the 5 extension members; comparison family =
`random_k4_s0/s1/s2`, `topabs_k4`, `topvar_k4` — **disjoint**, asserted, exit 2 otherwise; instrument =
A2 per prompt over all annotators, cosine distance on satisfaction vectors; regime = first release,
home judge, this tree_sha.

**E1/E2 · two curves, never their ratio** (D1: corr(c, committed) = +0.2042 puts the regressor in the
denominator):

| c quartile | n | c | committed | sham | ratio |
|---|---|---|---|---|---|
| Q1 | 242 | 0.0003 | 0.0047 | 0.0354 | 7.47 |
| Q2 | 237 | 0.0200 | 0.0059 | 0.0376 | 6.32 |
| Q3 | 244 | 0.0486 | 0.0061 | 0.0313 | 5.15 |
| Q4 | 245 | 0.1124 | 0.0078 | 0.0340 | 4.34 |

**corr(c, sham) = −0.0212** (flat) · **corr(c, committed) = +0.2042** (rising).

**E3 · ownership.** split-half reliability committed **0.8806**, comparison **0.8438**, attenuation
ceiling **0.8620**. Cross-family **+0.2438 = 0.283× ceiling**. SHAM — the committed five split into
**overlapping** halves — **+0.5097**, i.e. arm-sharing buys **2.09×**. NEGATIVE 200 one-sided
permutations **−0.0021 [−0.0654, +0.0665]**. PLACEBO a family against itself **1.000000**.

**Calibration.** Planted prompt-scale dose curve: 0.00 → −0.0192 · 0.25 → +0.3380 · 0.50 → +0.6076 ·
1.00 → +0.8582. Observed **+0.2438** interpolates to a width of **≈0.18**; R772's within-family
spectral estimate was **0.59**.

**Confound printed, not assumed away.** mean A2 committed **0.5635** vs comparison **0.4910**; `c`
quartiles committed [0.0055, 0.0333, 0.0667] vs comparison [0.0416, 0.0856, 0.1479].

**WORLD: none claimed** — registered A needed ≥0.5× the ceiling, B ≤0.2×, and 0.283 is neither.

## R775 · four disjoint families, and the rule gradient

**Scope.** population = 968 prompts; four families of five arms with **zero shared objects** under
R730, every member default-judge (no `_08b`, R765) and non-replica (no `_ctl`/`_det`, R766) —
F1 committed `coval_core, topw_k3/k4/k6/k8` · F2 selector-seed `random_k4_s0/s1/s2, topabs_k4,
topvar_k4` · F3 target-reading `oracle_k4, oracle_k4_fit1, greedy_k4_fit1, indep_k4_fit1,
greedy_k4_greedy_kA` · F4 selector-k `random_k2/k3/k6/k8/k12_s0`; regime = first release, home judge,
this tree_sha.

| pair | raw | ceiling | relative | class |
|---|---|---|---|---|
| F2 × F4 *(both `random_k`)* | 0.6017 | 0.8410 | **0.7154** | sel–sel |
| F1 × F2 | 0.2438 | 0.8580 | **0.2841** | sel–sel |
| F1 × F4 | 0.1716 | 0.8565 | **0.2003** | sel–sel |
| F1 × F3 | 0.1353 | 0.8863 | 0.1527 | sel–TARGET |
| F3 × F4 | −0.0020 | 0.8688 | −0.0023 | sel–TARGET |
| F2 × F3 | −0.0120 | 0.8702 | −0.0138 | sel–TARGET |

**Reliabilities** F1 0.8738 · F2 0.8424 · F3 0.8990 · F4 0.8396.
**Family levels** mean A2 0.5635 / 0.4910 / **0.6140** / 0.4942 · internal mean |d| 0.0457 / 0.1017 /
**0.0305** / 0.0935 — **F3 is compressed to a third of the selector families**.

**Controls.** DISJOINT 0 shared objects (exit 2 otherwise) · POSITIVE a planted prompt-scale, all six
detected from width 0.25, min **+0.2770 → +0.7871**, monotone · g=0 width 0 not all detected ·
NEGATIVE 200 one-sided permutations **+0.0017 [−0.0629, +0.0603]** · PLACEBO **1.000000** · SHAM
within-family overlapping halves F1 **+0.5097** · F2 **+0.6545** · F3 **+0.8512** · F4 **+0.4256**.
**WORLD C** — the target-reading family is compressed.

⚠ **The axis null is under-powered by construction**: four families admit four labelings, so the
observed difference **+0.3544** equals the permutation interval's upper end **[−0.2117, +0.3544]**.

## R776 · six families, and the first quantity with no arm in it

**Scope.** population = 968 prompts; six families of five arms, **zero shared objects** under R730,
all default-judge and non-replica — `Ra/Rb/Rc` = `random_k{2,3,6,8,12}_s{0,1,2}` (pure `random_k`,
differing only in seed) · `F1_committed` · `F3_target` · `M_mixed_sel`; regime = first release, home
judge, this tree_sha.

**E3 · the arm-free covariate** `poolspread(p)` = spread of the 16 pool criteria × 4 responses.

| family | corr | with poolmean | partial |
|---|---|---|---|
| F1_committed | **−0.1782** | +0.0250 | −0.1861 |
| F3_target | −0.0914 | −0.0248 | −0.1139 |
| Rb_random_s1 | −0.0767 | +0.1244 | −0.0248 |
| M_mixed_sel | −0.0688 | +0.0703 | −0.0423 |
| Rc_random_s2 | −0.0664 | +0.1016 | −0.0244 |
| Ra_random_s0 | −0.0490 | +0.1138 | +0.0010 |

**0 of 6 ≥ 0.30 · 5 of 6 < 0.15**; SHAM **−0.0005 [−0.0644, +0.0591]**; corr(poolspread, poolmean)
**−0.4387**. **WORLD B — rule artifact; the prompt-property mechanism is refuted.**

**E1 · the 15 pairs, relative to each pair's own ceiling.** pure-random × pure-random **0.6283 ·
0.6386 · 0.6168** · pure-random × mixed **0.7151 · 0.7033 · 0.7018** · pure-random × committed
**0.1995 · 0.2578 · 0.2224** · committed × mixed **0.2835** · committed × target **0.1519** ·
target × anything **−0.0023 · 0.0033 · −0.0103 · −0.0137**.

**E2 · the registered axis test.** SAME-RULE **0.6279** (n=3) vs "diff-rule" **0.2677** (n=12),
difference **+0.3602**, rank 4/20, **p = 0.2000** (floor **0.0500** — C(6,3) = 20 assignments).
⚠ **Uninformative**: `M_mixed_sel` holds 3 of 5 `random_k` arms, so three majority-same-rule pairs sat
in the diff-rule block. **Post-hoc**: pure-random pairs **0.6279** vs pairs with no pure-random family
**0.1406**.

**Controls.** DISJOINT 0 shared objects · POSITIVE planted scale, all 15 detected from width 0.25,
covariate 0.5806 → 0.9106, monotone · g=0 not all detected at width 0 · NEGATIVE **+0.0058 [−0.0607,
+0.0651]** · SHAM as above · PLACEBO **1.000000**.

## R777 · ordering disagreement — the second arm-free candidate, and a failed derivation

**Scope.** population = 968 prompts; R776's six disjoint families unchanged; instrument = A2 per
prompt over all annotators, plus `orderdisagree(p)` = mean pairwise disagreement of the 16 pool
criteria's induced sign vectors over the 6 response pairs; regime = first release, home judge, this
tree_sha.

**k is dead by derivation.** `F3` × `M` share k exactly (both {4}) → **−0.0137**, the lowest of 15;
`Ra` × `M` share none → **+0.7151**, the highest. corr(k-overlap, relative) = **+0.1620**.

**The covariates are distinct.** corr(orderdisagree, poolspread) = **−0.5901**; corr(orderdisagree,
tieshare) = **+0.7392** (the registered confound). `orderdisagree` mean **0.2618**, sd **0.1210**.

| family | random? | corr | partial (tie share) |
|---|---|---|---|
| F1_committed | — | **+0.2182** | +0.1755 |
| F3_target | — | +0.1461 | +0.1089 |
| Rb_random_s1 | RANDOM | +0.0994 | +0.0550 |
| Rc_random_s2 | RANDOM | +0.0961 | +0.0236 |
| M_mixed_sel | RANDOM | +0.0956 | +0.0677 |
| Ra_random_s0 | RANDOM | +0.0699 | +0.0385 |

random-containing mean |corr| **0.0902** · others **0.1821** · **gap −0.0919** (backwards).
**0 of 4** random families ≥ 0.30; **5 of 6** < 0.15. **WORLD B.**

**Conditioning changes nothing.** `Ra`×`M` 0.6017 → 0.5992 (**0.4%**) · `Rb`×`M` 0.5917 → 0.5878
(0.7%) · `Rc`×`M` 0.5895 → 0.5857 (0.6%).

**The failed derivation.** D3 held that |d| must rise with ordering disagreement by construction. The
synthetic control confirms the mechanism — width 0.25 → **+0.6260**, 0.50 → **+0.6503**, 1.00 →
**+0.5465**, and **UNDEFINED** at zero disagreement — so it recovers **6.5×** what the real arms show.
⚠ Not monotone at the top: at high disagreement the between-prompt variance the correlation needs
collapses.

**Controls.** POSITIVE as above · g=0 undefined at zero, printed as undefined · NEGATIVE 200
permutations **+0.0011 [−0.0604, +0.0674]** · SHAM random draw from the covariate's own distribution
**+0.0033 [−0.0657, +0.0662]** · PLACEBO **1.000000**.

## R778 · the covariates were computed on the wrong criterion set

**Scope.** population = 968 prompts; R776's six disjoint families unchanged; instrument = A2 per
prompt over all annotators, covariates from the prompt's own rubric (`sat_full.npz` /
`core_full.json`); regime = first release, home judge, this tree_sha.

**Object check.** distinct pool sets across 968 prompts **1** (prompt-blind) · `random_k4_s0` ⊂ pool
**0/968** · `topw_k4` ⊂ pool **0/968** · `random_k4_s0` ⊂ **rubric 968/968** · distinct criteria used
**3,869** against the pool's **16**. Rubric size median **15**, range **4–39**.

| family | random? | `n_rubric` | `rubricdisagree` | `rubricspread` |
|---|---|---|---|---|
| Ra_random_s0 | RND | +0.1052 | **+0.3206** | +0.1041 |
| Rb_random_s1 | RND | +0.1549 | **+0.3393** | +0.0653 |
| Rc_random_s2 | RND | +0.1119 | **+0.3588** | +0.0977 |
| M_mixed_sel | RND | +0.1289 | **+0.3649** | +0.0742 |
| F1_committed | — | −0.0181 | +0.2742 | −0.0911 |
| F3_target | — | −0.0552 | +0.1689 | −0.0612 |
| **≥ 0.30 among the 4 random** | | **0/4** | **4/4** | **0/4** |

**Degenerate prompts** (`n_rubric ≤ k`, the draw is the whole rubric and |d| = 0): k=4 **3** · k=6
**18** · k=8 **80** · **k=12 302 (31%)**.

**Conditioning on each covariate**, M × R raw 0.5895–0.6017: `n_rubric` **+1.1%** · `rubricdisagree`
**+9.6%** · `rubricspread` **+0.4%**.

**Controls.** OBJECT as above (exit 2 otherwise) · POSITIVE synthetic k-subsets, size-spread 0.25 →
+0.0379, 0.50 → +0.1273, 1.00 → **+0.3109**, monotone · g=0 fixed size → **UNDEFINED** · NEGATIVE 200
permutations **−0.0003 [−0.0552, +0.0667]** · SHAM **+0.0010 [−0.0619, +0.0549]** · PLACEBO
**1.000000** · CONFOUND corr(`n_rubric`, a baseline arm's A2) **−0.0190**. **WORLD B.**

## R779 · the mediation bound

`corr(A,B)` between arm families **0.5943**. Required single-covariate correlation `sqrt(r)`
**0.7709**. Best achieved with either scale **0.3649** (`rubricdisagree`) → **2.11× short**.

**Bound vs measured drop**, 6 covariates × 3 M×R pairs, largest four:

| covariate × pair | r(Z,A) | r(Z,B) | bound | measured | gap |
|---|---|---|---|---|---|
| rubricdisagree × Rc | +0.3588 | +0.3649 | +0.1309 | +0.0618 | −0.0691 |
| rubricdisagree × Rb | +0.3393 | +0.3649 | +0.1238 | +0.0575 | −0.0663 |
| rubricdisagree × Ra | +0.3206 | +0.3649 | +0.1170 | +0.0521 | −0.0649 |
| overlap × Rb | −0.1708 | −0.1543 | +0.0264 | +0.0110 | −0.0154 |

**All 18 gaps negative**; worst |gap| **0.0691**. Spearman bounds are larger than Pearson in every
cell, so the Pearson figure does not flatter the null.

**In-sample multiple correlation** (a ceiling, not an estimate): Ra **0.3938** · Rb **0.4110** ·
Rc **0.4133** · F1 **0.3102** · F3 **0.2034** · M **0.4290**. Reaching 0.7709: **0 of 6**.

**Overlap shared across families 0.8871** against scales at **0.5943**.

**Controls.** PLACEBO **1.000000** · g=0 **+0.0000** inside the negative band · NEGATIVE 200
permutations **+0.0001 [−0.0010, +0.0023]** · SHAM **+0.0000** · POSITIVE (rebuilt, generative share
1.0 by construction) recovered **1.0526** at w=0.5 and **1.0000** at w=1.0 · SPEARMAN on every
correlation. **WORLD A.**

## R780 · clause ② across two releases

**Release 2**: 2,200 conversations · 7,344 interactions · strata 2:**5204** / 3:**456** / 4:**1684** ·
7 arms · blind reference `core_generic.json`, **the same file as release 1's**.

| contrast | n | eff | CI | MDE | verdict |
|---|---:|---:|---|---:|---|
| r1 `gen` − blind | 968 | **−0.0267** | [−0.0424, −0.0115] | 0.0216 | **LOSES** |
| r2 `gen` − blind | 1684 | **+0.0020** | [−0.0065, +0.0104] | 0.0124 | **UNRESOLVED** |
| r1 `gen_sham` − blind | 968 | −0.1043 | [−0.1191, −0.0887] | 0.0219 | LOSES |
| r2 `gen_sham` − blind | 1684 | −0.0243 | [−0.0346, −0.0134] | 0.0151 | LOSES |
| r2 `vacuous` − blind | 1684 | −0.0396 | [−0.0487, −0.0306] | 0.0131 | LOSES |
| r2 `randblind_s0` − blind | 1684 | −0.0313 | [−0.0424, −0.0192] | 0.0168 | LOSES |
| r2 `randblind_s1` − blind | 1684 | −0.0516 | [−0.0664, −0.0358] | 0.0219 | LOSES |
| r2 `randblind_s2` − blind | 1684 | −0.0221 | [−0.0317, −0.0112] | 0.0153 | LOSES |
| r1 `gen` − blind, ALL annotators *(specification)* | 968 | −0.0162 | [−0.0247, −0.0082] | 0.0119 | LOSES |
| r2 n=2 *(not gauge-matched)* | 5204 | +0.0065 | [−0.0050, +0.0183] | 0.0170 | UNRESOLVED |
| r2 n=3 *(not gauge-matched)* | 456 | +0.0117 | [−0.0124, +0.0358] | 0.0357 | UNRESOLVED |

**Blind-arm spread on release 2: 0.0295**, against an MDE of 0.0124–0.0219.
**Required n** to resolve a release-1-sized effect on release 2: **366**, have **1,684**.
**Census**: 21 unscoped-wall lines, **13** at or before R556, **8** after.

**Controls.** OBJECT as above, exit 2 otherwise · PLACEBO **0.000000** both · g=0 **0.000000** both ·
NEGATIVE target-permuted 200 draws r1 **[−0.0215, +0.0221]**, r2 **[−0.0159, +0.0161]** · the
pairing permutation is a **DERIVATION** (3.4e-18 / 7.5e-19), labelled not reported · SHAM
prompt-specificity ABSENT **−0.0313** · POSITIVE swept 0 → **UNRESOLVED**, 0.25/0.50/1.00 → BEATS on
both releases, band floor **+0.0000** < t < ceiling **+0.4478** · SEARCH positive and negative both
PASS. **NO WORLD CLAIMED.**

## R781 · the reference class, measured

**Class**: C(16,4) = **1820** subsets of `sat_genericpool16.npz` · 968 prompts · mean A2 **0.5386** ·
range **[0.5144, 0.5575]** = **0.0431** wide · mean pairwise correlation **+0.8709** →
**n_eff = 1.1**.

**q = fraction of the class an arm beats, leave-one-out** (20 k=4 arms, full coverage):

| arm | A2 | q | q resolved |
|---|---:|---:|---:|
| oracle_k4 / _oracle_kA / _oracle_kB | 0.6283 | 1.0000 | 1.0000 |
| greedy_k4_greedy_kA / _kB | 0.6226 | 1.0000 | 1.0000 |
| oracle_k4_fit1 | 0.6142 | 1.0000 | 1.0000 |
| greedy_k4_fit1 | 0.6106 | 1.0000 | 1.0000 |
| indep_k4_indep_kA / _kB | 0.6031 | 1.0000 | 1.0000 |
| indep_k4_fit1 | 0.5941 | 1.0000 | 1.0000 |
| topw_k4 / _detA / _detB | 0.5642 | 1.0000 | 0.9835 |
| **generic = POOL[0:4]** | 0.5504 | **0.9379** | 0.7422 |
| topwvar_k4 | 0.5040 | 0.0000 | 0.0000 |
| random_k4_s1 | 0.4981 | 0.0000 | 0.0000 |
| random_k4_s0 | 0.4927 | 0.0000 | 0.0000 |
| topabs_k4 | 0.4894 | 0.0000 | 0.0000 |
| random_k4_s2 | 0.4884 | 0.0000 | 0.0000 |
| topvar_k4 | 0.4863 | 0.0000 | 0.0000 |

**Shape**: in [0.35, 0.65] **0 of 20** · outside [0.10, 0.90] **20 of 20**. Self-matching references
excluded: **1**.

**Release 2** (5-member blind class, q takes 6 values): transport_gen 0.5541 / 1.00 ·
transport_generic 0.5522 / 1.00 · randblind_s2 0.5301 / 0.75 · gen_sham 0.5278 / 0.60 ·
randblind_s0 0.5209 / 0.50 · vacuous 0.5126 / 0.25 · randblind_s1 0.5006 / 0.00.

**DERIVED, not measured**: median-dominance IS p50; mean-dominance is the skew's percentile.

**Controls.** OBJECT as above, exit 2 otherwise · PLACEBO **0.0000** · g=0 a class member returns
**0.7273** against its own rank **0.7269** · POSITIVE dominating plant **1.0000**, dominated
**0.0000**, all real arms inside the measured band · ⛔ NEGATIVE **[0.9374, 0.9379]** vs real 0.9379 —
**VOID, a derivation** · ⛔ SHAM **1.0000 > 0.9379** — **VOID, a poison**. **WORLD B printed; the
distributional reading UNVERIFIED on n_eff.**

## R782 · realised size, the comparator pair, and the corrected population

**Size read from the sat file** (distinct criterion indices per prompt), 50 arms, **18 ragged**:

| arm | size distribution | off-modal |
|---|---|---:|
| `full` (the rubric) | 4 … 39 | 887 of 968 |
| `random_k12_s0/s1/s2` · `topw_k12` | {4:3, 5:1, 6:14, 7:31, 8:31, 9:29, 10:57, 11:68, 12:734} | 234 |
| `random_k8_s0/s1/s2` · `topw_k8` | {4:3, 5:1, 6:14, 7:31, 8:919} | 49 |
| **`coval_core`** · `coval_core_sham` | **{2:1, 3:42, 4:925}** | **43** |
| `random_k6_s0/s1/s2` · `topw_k6` | {4:3, 5:1, 6:964} | 4 |
| `gen` · `gen_sham` | {1:1, 3:1, 4:966} | 2 |

**Prompts whose rubric holds fewer than 4 criteria: 0.** Core files and sat files agree on size for
all **48** arms with a readable core file; `coval_core` and `generic_reprov` have none.

**`POOL[0:4]` vs `sat_generic.npz`**: arrays identical **False**, max |dY| **0.120967** · A2
**0.550436** vs **0.551354** · paired **−0.000918** [−0.002430, +0.000562], MDE **0.002188**,
**UNRESOLVED** · differs on **73 of 968** prompts, max |diff| **0.2500**.

**Filters**: name regex **20** · strict k=4 everywhere **22** · modal k=4 **26**.
`modal \ name` = coval_core, coval_core_sham, gen, gen_sham, generic, generic_reprov.
`modal \ strict` = coval_core, coval_core_sham, gen, gen_sham. `name \ modal` = ∅.

**q over the corrected 26** (n_eff 1.1, so a band fraction, not a probability): oracle family
0.6283/1.0000 · greedy_kA/kB 0.6226/1.0000 · oracle_fit1 0.6142/1.0000 · greedy_fit1 0.6106/1.0000 ·
indep_kA/kB 0.6031/1.0000 · indep_fit1 0.5941/1.0000 · **coval_core 0.5665/1.0000, q_res 0.9978** ·
topw_k4/detA/detB 0.5642/1.0000, q_res 0.9835 · generic & generic_reprov 0.5514/0.9538, q_res 0.7780 ·
**gen 0.5352/0.3308, q_res 0.0396** · nine arms 0.4828–0.5040 at 0.0000.
**Shape: middle band 0.0000 · extreme 0.9615 · the one arm in neither is `gen`.**

**Controls.** OBJECT as above, exit 2 otherwise · PLACEBO **0.000000** · g=0 same file twice
**0.000000**, UNRESOLVED · REPLICA `topw_k4` vs `topw_k4_detA` **0.000000** — the negative's job, the
permutation null being void by derivation · POSITIVE 0× / 0.5× / 1× UNRESOLVED, 4× **BEATS**, band
computed at both ends · ⛔ SHAM **INADMISSIBLE**: a sham is undefined for a prompt-blind arm.
**WORLD B — different objects, below resolution.**

## R783 · the release side, measured

**Release** `data/conversation_rubrics.jsonl`: **986** records, **986** distinct ids, **0**
duplicates, **0** missing a key.

| field | release | scored sat file |
|---|---|---|
| `coval_core` size | **{2: 1, 3: 43, 4: 942}** | **{2: 1, 3: 42, 4: 925}** |
| `coval_full` size | min **4** max **39**, below 4 **0** | min **4** max **39**, below 4 **0** |
| fewer than 4 criteria | **44 of 986 = 4.46%** | **43 of 968 = 4.44%** |

**Residual** per cell {2: 0, 3: 1, 4: 17}, worst **17**, D1 bound **18**.
**Join** on rubric criterion texts: **968 of 968 exact**, 0 unmatched, 0 ambiguous (R468 reproduced).
**Unscored**: **18**, core sizes **{3: 1, 4: 17}**; `release − unscored` = **{2: 1, 3: 42, 4: 925}** =
the scored distribution **exactly**.
**Short-core mechanism**: empty **0** · whitespace-only **0** · duplicate-within-record **0** ·
criterion text length min **31** median **89** max **215**.

**`coval_core` clause-② standing**: all 968 prompts A2 **0.5665**, q **1.0000**, q_res **0.9978** ·
4-criterion-only 925 prompts A2 **0.5671**, q **1.0000**, q_res **0.9978**. ⚠ near-determined — R782
had already measured 0.9978.

**Controls.** OBJECT as above, exit 2 otherwise · CROSS-INSTRUMENT exact after the join · PLACEBO
identical recount · g=0 empty list counts 0, **0** empty cores · POSITIVE injected {0,1,4,39}
recovered exactly, broken character-counter returns {2,20,80,809} · DUPLICATES **0** ·
⛔ NEGATIVE and SHAM **declined in the preregistration** on D2 and D3. **WORLD A.**

## R784 · the population, measured

| set | n |
|---|---:|
| ranked (parsed human rankings) | **1078** |
| rubricked (`core_full.json`) | **968** |
| scored (this arc's population) | **968** |
| released conversations | **986** |
| **ranked WITHOUT a rubric** | **110 (10.20%)** |
| rubricked without rankings | 0 |
| dropped by the `>=2 rankings` rule | **0** |
| dropped by absence from the sat file | **0** |
| released but never scored | 18 (R783) |

**The 110 against the 968**, three estimators, 3 primary cells, **0 surviving**:

| axis | mean 968 | mean 110 | med 968 | med 110 | var ratio | rank | verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| rankings per prompt | 16.108 | 25.373 | 16.0 | 17.0 | 395.80 | +0.0526 | inside null |
| unacceptable flags | 4.163 | 10.109 | 0.0 | 0.0 | 82.99 | −0.0530 | inside null |
| flag rate per ranking | 0.341 | 0.290 | 0.0 | 0.0 | 0.99 | −0.0510 | inside null |

**MDE**: this design **0.2819 SD** · R783's proposed n=18 **0.6665 SD** · required n for 0.20 SD
**246**, 0.15 SD **545**, 0.10 SD **4,149**.

**Controls.** OBJECT 1078 = 968 + 110 exactly, exit 2 otherwise · PLACEBO **+0.000000** · g=0 200
random 110-subsets: rankings [−0.1063, +0.1074], flags [−0.0857, +0.0931], rate [−0.0980, +0.0859] ·
POSITIVE 0.00 inside · 0.25 inside · **0.50 RESOLVES** · 1.00 RESOLVES · NEGATIVE group-label
permutation (**valid here, unlike ledger 1125/1129**) rankings [−0.1271, +0.1150], flags [−0.0896,
+0.1029], rate [−0.0988, +0.0807] · CONFOUND flag rate reported beside the raw count. **WORLD C.**

## R785 · rubric affinity, measured

**Join** ranking→release: exact **968**, unmatched **0**, ambiguous **0** (R468, rebuilt in R783).

| object | tok | verbatim | affinity | null | own − null | MDE | |
|---|---:|---:|---:|---:|---:|---:|---|
| coval_core | 3 | 0.0668 | 0.4938 | 0.0836 | +0.4103 | 0.0139 | RESOLVES |
| gen | 3 | 0.0000 | 0.1410 | 0.1028 | +0.0382 | 0.0044 | RESOLVES |
| **core − gen** | 3 | | | | **+0.3535** | 0.0149 | **RESOLVES** |
| coval_core | 4 | 0.0668 | 0.4951 | 0.0555 | +0.4396 | 0.0145 | RESOLVES |
| gen | 4 | 0.0000 | 0.0865 | 0.0356 | +0.0508 | 0.0048 | RESOLVES |
| **core − gen** | 4 | | | | **+0.4090** | 0.0154 | **RESOLVES** |
| coval_core | 5 | 0.0668 | 0.5014 | 0.0465 | +0.4549 | 0.0147 | RESOLVES |
| gen | 5 | 0.0000 | 0.0867 | 0.0319 | +0.0549 | 0.0053 | RESOLVES |
| **core − gen** | 5 | | | | **+0.4150** | 0.0157 | **RESOLVES** |

**Containment**: cores entirely inside their rubric **1 of 986**; records with zero verbatim overlap
**792 of 986**.

**The pair** (n = 2, no correlation computed): coval_core affinity **0.4951**, q_resolved **0.9978** ·
gen affinity **0.0865**, q_resolved **0.0396**.

**Controls.** OBJECT join exact, exit 2 otherwise · PLACEBO **1.000000** · NULL **+0.4396**
[+0.4293, +0.4499], MDE 0.0145, 986 of 986 · NULL-TOPIC **+0.4013**, MDE 0.0363, n=150 · POSITIVE
delete 0% → **1.0000**, 25% → 0.7536, 50% → 0.4992, 75% → 0.2523, monotone · SWEEP {3,4,5} ·
⛔ SHAM not built (the ingredient's removal IS the null). **WORLD A.**
**Release data quality**: **3 of 19,147** criteria tokenise to nothing — `'Lwa'`, a bare UUID, an
empty string.

## R786 · the affinity axis, enumerated

**Arms with criterion text: 89** (counted in code). **Rubric-derived (verbatim ≥ 0.5): 79.**
**Not rubric-derived: 10.**

| arm | verbatim | aff@3 | aff@4 | aff@5 | null@4 | A2 | q_res |
|---|---:|---:|---:|---:|---:|---:|---:|
| coval_core | 0.0670 | 0.4944 | **0.4954** | 0.5018 | 0.0552 | 0.5665 | 0.9978 |
| promptecho | 0.0006 | 0.1479 | 0.1401 | 0.1478 | 0.0359 | — | — |
| gen | 0.0000 | 0.1410 | 0.0865 | 0.0867 | 0.0357 | 0.5352 | 0.0396 |
| topw_k4_sham | 0.0000 | 0.0905 | 0.0564 | 0.0471 | 0.0562 | 0.4909 | 0.0000 |
| full_sham | 0.0000 | 0.0885 | 0.0561 | 0.0465 | 0.0579 | — | — |
| coval_core_sham | 0.0000 | 0.0836 | 0.0550 | 0.0459 | 0.0558 | 0.4956 | 0.0000 |
| gen_sham | 0.0000 | 0.1028 | 0.0356 | 0.0319 | 0.0360 | 0.4828 | 0.0000 |
| promptecho_sham | 0.0000 | 0.0595 | 0.0352 | 0.0214 | 0.0353 | — | — |
| genericpool16 | 0.0000 | 0.1094 | 0.0316 | 0.0265 | 0.0316 | — | — |
| **generic** | 0.0000 | 0.1212 | **0.0249** | 0.0243 | **0.0249** | 0.5514 | **0.7780** |

**Correlation** affinity vs q_resolved: with shams n=6, r **+0.7678 / +0.6907 / +0.6993** ·
sham-free n=3, r **+0.6421 / +0.5841 / +0.5841**. **D3 MDE** n=5 **0.963** · 6 **0.924** · 7 **0.886**
· 8 **0.849** · 10 **0.785**, printed before any r. **All inside.**
**A2-CHECK**: corr(affinity, A2) **+0.6391** with shams, **+0.7878** sham-free ·
**corr(A2, q_resolved) +0.8747** with shams, **+0.9601** sham-free.

**Arms with text but no q_resolved**, listed: full_sham, genericpool16, promptecho, promptecho_sham.

**Controls.** OBJECT enumeration computed in code, exit 2 otherwise · PLACEBO **1.000000** · POSITIVE
rubric-derived arms return **1.0** exactly (D1, a derivation used as an instrument check) · NULL
per-arm cross-conversation · SHAM-SPLIT both populations printed · A2-CHECK the registered confound ·
SWEEP {3,4,5} · MDE printed FIRST. **WORLD C — underpowered, as D3 predicted.**

## R787 · q against A2

**Identity** `sign(mean(v − REF)) == sign(A2_arm − A2_ref)`: **0 disagreements of 47,320 pairs**
(26 arms × 1,820 references).

| | distinct values, 26 arms |
|---|---:|
| A2 | **19** |
| q | **4** |
| q_resolved | **6** |

**Kendall tau(A2, q)** +1.0000, 197 concordant, **0 discordant** ·
**tau(A2, q_resolved)** +1.0000, 240 concordant, **0 discordant**. ⚠ the first is a DERIVATION.

**The class**: reference A2 min **0.514375**, max **0.557475**, range **0.043100** ·
p0 0.5144 · p5 0.5242 · p25 0.5329 · p50 0.5391 · p75 0.5446 · p95 0.5511 · p100 0.5575.
**Baseline-conditional ⇔ A2 ∈ [0.5144, 0.5575]** → `generic` 0.5514, `gen` 0.5352.

**SHAM (class removed, ONE reference at A2 0.5504)**: agrees with `q > 0.5` on **26 of 26** arms.

**E4, the variance term** (two synthetic arms, identical A2): ratio 1.0 → 0.9835 / 0.9835 no
inversion · **1.5 → 0.9819 / 0.9835 INVERTS** · 2.0 → 0.9731 / 0.9835 · 4.0 → 0.8385 / 0.9835 ·
8.0 → 0.1714 / 0.9835. Real arms' per-reference sd **[0.0711, 0.1744]**, ratio **2.453** —
**inversion is inside the observed range**.

**Controls.** OBJECT 1820 rebuilt, exit 2 otherwise · PLACEBO **0.000000** · PLACEBO-2 a class member
returns q **0.726923** = its own A2 rank **0.726923** · POSITIVE `gen` swept 0 → **0.3308**, +0.02 →
**0.9923**, +0.05 → **1.0000**, +0.30 → **1.0000**, all matching the independent percentile to 1e-12,
band **admissible** · ⛔ NEGATIVE not built (D1 makes a permutation void). **WORLD B.**

## R788 · membership, the exclusion rule, and the variance advantage

**`generic` IS a class member**: `core_generic.json` = pool indices **[0, 1, 2, 3]** = reference
**#0** of the C(16,4) = 1,820.

| exclusion rule | references excluded for `generic` |
|---|---:|
| satisfaction-based (R781/R782) | **0** |
| criterion-based (the right unit) | **1** (reference #0) |

**POSITIVE**: jitter 0 → satisfaction rule catches **1**; 0.001 → **0**; observed 0.005638 → **0**;
criterion rule catches **1** at every level.

| | q | q_resolved |
|---|---:|---:|
| published (R782) | 0.9538 | 0.7780 |
| recomputed | 0.9538 | 0.7780 |
| self-reference #0 removed | 0.9538 | 0.7784 (**+0.000428**, D1 bound 0.000549) |
| **sd scaled to `gen`'s (1.871×)** | — | **0.5429 (−0.2352)** |

**CONFOUND (it won)**: `generic` blind AND member, k=4, sd **0.0711** · `genericpool16` blind, NOT a
member, k=16, sd **0.0635** — ratio **0.893**. **Blindness, not membership.**

**sd(v − REF) by arm class**: blind **0.0635–0.0711** · prompt-specific **0.123–0.174** · no arm
crosses the gap.

**Controls.** OBJECT membership verified, exit 2 otherwise · E1 decomposition worst mismatch
**2.082e-17** · PLACEBO **0.000000** · POSITIVE band computed at both ends · COUNTERFACTUAL labelled a
construction. **WORLD C.**

## R789 · what the A2 axis can resolve, and why a scalar cut is not a free simplification

**The question.** R788's NEXT proposed replacing `q_resolved` with A2 against a stated cut. A cut is
only as good as its axis, so this round prices the axis: how many levels does A2 resolve, and is the
released core resolvedly above the prompt-blind baseline?

**Derived before measuring.** D1 the admitted set `{arm : A2 > c}` changes at each distinct A2 value,
so ℝ gives (#distinct)+1 admitted sets — algebra, not a finding. D2 a cut's plateau IS the gap it
sits in, and a gap below its pair's MDE is not a distinction. D3 `var(a−b)=var(a)+var(b)−2cov(a,b)`,
so the paired MDE cannot be predicted from marginals and the pairing must be destroyed to be priced.
D4 #levels ≤ #distinct A2, so the measurement is where in [1, 20] it lands.

**The ladder, over the whole grid.**

| rule | `t` | adjacent | greedy |
|---|---|---:|---:|
| point | 0 | 20 | 20 |
| ci_only | 1.959964 | 10 | 11 |
| **strict / mde** (pre-registered, the rule `corebench/report.py` implements) | **2.801585** | **9** | **10** |
| conservative | 4.761549 | 5 | 7 |

**The levels** (strict, adjacent; emitted by `run.py`, not derived in prose): ① 9 floor arms
0.4828–0.5040 · ② `gen`, `genericpool16` 0.5352–0.5422 · ③ `generic`, `generic_reprov` 0.5514 ·
④ **`topw_k4`, `_detA`, `_detB`, `coval_core` 0.5642–0.5665** · ⑤ `indep_k4_fit1` 0.5941 ·
⑥ `indep_k4_indep_kA/kB` 0.6031 · ⑦ `greedy_k4_fit1`, `oracle_k4_fit1` 0.6106–0.6142 ·
⑧ `greedy_k4_greedy_kA/kB` 0.6226 · ⑨ `oracle_k4`, `_kA`, `_kB` 0.6283.

**The decisive pairs.**

| pair | eff | CI | MDE | `t` | verdict |
|---|---|---|---|---|---|
| `coval_core` − `generic` | **+0.01512** | [+0.00746, +0.02283] | 0.01069 | 3.96 | **BEATS** |
| `coval_core` − `gen` | +0.03130 | [+0.02314, +0.04002] | 0.01223 | 7.17 | BEATS |
| `generic` − `gen` | +0.01618 | [+0.00816, +0.02470] | 0.01185 | 3.82 | BEATS |
| `coval_core` − `genericpool16` | +0.02424 | [+0.01649, +0.03183] | 0.01081 | 6.29 | BEATS |
| `generic` − `genericpool16` | +0.00912 | [+0.00570, +0.01278] | 0.00489 | 5.23 | BEATS |
| **`coval_core` − `topw_k4`** | +0.002297 | [−0.00378, +0.00844] | 0.00853 | 0.75 | **UNRESOLVED** |

**SHAM (the second arm removed) versus NEUTRAL (a non-arm vector).** Scalar cut **0.539126**, median
reference **#1151** of 1,820.

| arm | vs the SCALAR cut | vs the median reference's VECTOR |
|---|---|---|
| `coval_core` | +0.02735 · mde 0.01351 · BEATS | +0.02735 · mde 0.01088 · BEATS |
| **`generic`** | +0.01223 · mde 0.01351 · **BELOW RESOLUTION** | +0.01223 · mde **0.00591** · **BEATS** |
| `gen` | −0.00395 · mde 0.01516 · UNRESOLVED | −0.00396 · mde 0.01214 · UNRESOLVED |

Population-wide: **23 of 27** resolve against the scalar, **25 of 27** against the vector; mean sd
**0.15333** versus **0.13103**.

**Controls.** OBJECT 27 arms · 968 prompts · annotators median 16, max 46 · **0** A2 mismatches
against R782 beyond 1e-9, exit 2 otherwise · PLACEBO eff 0.000000, CI [0,0], UNRESOLVED · POSITIVE
δ=0 UNRESOLVED (the floor fails, as required) → 0.01 BELOW RESOLUTION → 0.02 BEATS → 0.05 BEATS,
empirical MDE **0.01331**; the constant plant resolves at every δ>0 because its sd is 0 and it is
labelled degenerate in the docstring before the run · NEGATIVE pairing destroyed → MDE ×**1.529**
median, ×1.795 mean over 342 non-degenerate pairs, 9 duplicates excluded, synthetic independent arms
×1.036 · SHAM and NEUTRAL as above · NOISE FLOOR annotator split-half **0.003416**, and it is a
MARGINAL quantity that may not be compared to paired gaps.

**Multiplicity.** 351 cells tested · 305 survive the verdict rule · 46 do not (39 UNRESOLVED, of
which 9 are byte-identical duplicates; 7 BELOW RESOLUTION) · 311 survive BH at q=0.05 with no MDE
floor. **WORLD A.**

## R790 · whether a LEVEL can carry a definition, and why the answer is no

**The question.** R789's NEXT proposed rewriting clause ② as a membership claim. Membership needs
levels to be objects; this round asks whether they are.

**Derived before measuring.** D1 a non-transitive relation induces no partition, so the two
constructions are FORCED. D2 the sort key is an estimate, so the partition is rebuilt end-to-end in
every draw and never by re-thresholding a fixed order. D3 `t = |Δ|√P/sd`, so a rule change is a pure
rescaling — every difference between the four rules is threshold placement alone. D4 the 9 alias
pairs must return P = 1.000 exactly, which is this round's placebo with a known expected value.

**E1 · the relation is not an equivalence relation.**

| rule | intransitive chains | of | rate |
|---|---:|---:|---:|
| point | 0 | 0 | — |
| ci_only | 23 | 146 | 15.8% |
| strict / mde | 16 | 202 | 7.9% |
| conservative | 16 | 253 | 6.3% |

**E2/E3 · the bootstrap, B = 1,000.** Level count (adjacent) 7:0.084 · 8:0.359 · **9:0.408** ·
10:0.138 · 11:0.011. Greedy 8:0.022 · 9:0.209 · **10:0.560** · 11:0.192 · 12:0.017.

| pair | P(same level) adjacent | greedy |
|---|---:|---:|
| **`coval_core` ~ `generic`** | **0.339** | **0.132** |
| `coval_core` ~ `topw_k4` | **0.975** | 0.758 |
| `generic` ~ `gen` | 0.045 | 0.094 |
| `coval_core` ~ `gen` | 0.004 | <0.001 |
| `coval_core` ~ `genericpool16` | 0.005 | <0.001 |
| `coval_core` ~ `indep_k4_fit1` | <0.001 | <0.001 |

**The specification curve** (3 seeds per cell, all twelve published): `P(core ~ generic)` = 0.000
(point) · 0.065–0.090 (ci_only) · 0.310–0.339 (strict) · 0.920–0.955 (conservative).

**E4 · the formulation.** `generic` in level **3 of 9**; admits 8 classes = **14 named arms**;
excludes 12 classes = **13**; the same admitted set in **0.640** of 300 resamples.

**Controls.** OBJECT 20 distinct objects from 27 named arms, worst `t` delta against R789
**1.066e-14**, exit 2 otherwise · PLACEBO the 9 alias pairs at exactly **1.000** · POSITIVE δ sweep
0.990 → 0.955 → 0.755 → 0.110 → **0.000**, band admissible; ⛔ **the pre-registered criterion
`floor == 1.000` FAILED at 0.990 and was itself mis-specified** — at δ=0 the plant adds zero-mean
noise, so the rule fires at `α = 0.005085` and `P(floor == 1) = 0.361` over 200 draws, a **64%
false-failure rate by construction**; repaired against its own binomial null, |−0.00491| ≤ 0.01509,
PASS · NEGATIVE synthetic matched-spread arms mode **5** against the real **9**, so World C does not
fire · SHAM equal-width binning at the same level count, adjusted Rand **0.7798**.

**Multiplicity.** 190 unordered pairs among 20 objects — not 351; the 9 alias pairs are the placebo.
Bootstrap resolution 1/1000, so 0 is reported as `< 0.001`. **WORLD B.**

## R791 · the six-comparison decomposition, and why it is a reparameterisation

**The gauge freedom.** A2 per prompt = mean over annotators of mean over the six response-pairs of
`(sign == class)`. The two means commute, so `A2 = (1/6)·Σ_c component_c` **exactly** — worst
deviation 1.1e-16 over 27 arms. The measurement is invariant under permuting which comparison an arm
gets right; the property "is a core" is not obviously invariant, which is what made the decomposition
worth computing.

**E4 · the effective rank.** Centred 20 × 6 matrix, eigenvalue shares
**0.9936 · 0.0031 · 0.0015 · 0.0009 · 0.0007 · 0.0002**. Shared component profile (mean over arms):
AB 0.5356 · AC 0.5536 · AD 0.5479 · BC 0.5342 · BD 0.5411 · CD 0.5458.

**E2 · the decisive pair, `coval_core` − `topw_k4`** (scalar +0.002297, mde 0.008528, `t` 0.75):

| | AB | AC | AD | BC | BD | CD |
|---|---|---|---|---|---|---|
| eff | +0.010331 | +0.005510 | −0.002140 | −0.004866 | +0.001375 | +0.003569 |
| mde | 0.016766 | 0.017702 | 0.017495 | 0.019459 | 0.017368 | 0.017240 |
| `t` | 1.73 | 0.87 | 0.34 | 0.70 | 0.22 | 0.58 |

**None survives BH + MDE.**

**`coval_core` − `generic`** (scalar +0.015123, mde 0.010694, `t` 3.96): AB 1.80 · **AC 3.47** ·
AD 1.23 · BC 0.70 · BD 1.54 · **CD 3.20** — two of six survive.

**E1/E3 · the decision.** Scalar: 190 cells, **155** resolve. Componentwise: 1,140 cells, 855 resolve
across **152** pairs. D2 registered in advance that a 6× family cannot resolve fewer at the same
nominal level, so only the post-BH comparison counts — and it **loses three**. Clause-② admitted
sets: scalar **14** named arms, componentwise **11**, symmetric difference `{topw_k4, topw_k4_detA,
topw_k4_detB}`, all on the losing side.

**Pre-multiplicity specification curve** (published because D2 makes it arithmetic): ci_only 167 vs
161 · strict 152 vs 155 · conservative 138 vs 145.

**Noise floor**, measured by annotator split-half over 20 draws: AB 0.006317 · AC 0.005018 ·
AD 0.006572 · BC 0.005035 · BD 0.005624 · CD 0.005867. ⚠ MARGINAL, per arm — R790's unit note
forbids comparing it to the paired effects. **WORLD C.**

## R792 · the estimand 2×2, and the three defaults nobody chose

**The question.** A committed round separated `coval_core` from `topw_k4` on a *subgroup-weighted,
annotator-resampled* estimand while this arc reported them inseparable on a *prompt-weighted,
prompt-resampled* one. That round changed two things at once and said so. A 2×2 separates them.

**Derived before measuring.** D1 weighting fixes the ESTIMAND, the resampling unit fixes its SE —
changing both confounds target with precision. D2 the 36 subgroups are six OVERLAPPING partitions of
one judgement set. D3 alias arms return exactly 0 in every cell. D4 a weighting correlation above
~0.99 makes the second a reparameterisation.

**E1 · the 2×2** (decisive pair, 1,200 draws):

| weighting | resampling | eff | 95% CI | p | verdict |
|---|---|---:|---|---:|---|
| pooled | prompt | +0.002297 | [−0.002203, +0.007005] | 0.2917 | not separable |
| pooled | annotator | +0.002297 | [−0.000163, +0.004650] | 0.0683 | not separable |
| subgroup | prompt | +0.004107 | [−0.002590, +0.010857] | 0.2267 | not separable |
| **subgroup** | **annotator** | **+0.004107** | **[+0.000424, +0.007765]** | **0.0300** | **SEPARABLE** |

**E2 · the grid.** 190 pairs per cell, BH over each whole grid: resolved **166 / 180 / 161 / 177**;
non-survivors 24 / 10 / 29 / 13. **11 of 190 verdicts flip** between the default and the prior cell.
`corr(pooled eff, subgroup eff) = 0.9993`.

**E3 · the decision.** All four admitted sets **IDENTICAL**, 14 named arms.

**A third default, found by the code failing.** The judgement table spans **1,078** prompts, the arms
share **968**, and the prior round used whatever each arm had. Both populations are carried: per-arm
availability for the reproduction, the common set for the grid.

**Controls.** OBJECT — the committed artifact reproduced by different code on a different day: 36
subgroups, mean 0.004107, win_rate 0.833333, exit 2 otherwise · PLACEBO 9 alias pairs, worst
per-judgement difference exactly 0.0 · POSITIVE floor **0 of 4** at δ=0, ceiling **4 of 4** at δ=0.002
· SUBGROUP-SPECIFIC plant, ratio (subgroup/pooled) by group size **3.870 (n=155) → 1.053 (n=2,125) →
0.948 (n=9,535)**, monotone as D2 requires — ⛔ the first version planted on the largest group and
failed against my own D2 · NEGATIVE demographics permuted across annotators, pooled unchanged to
0.0e+00, subgroup difference moves 0.000581 · SHAM random groups of the same 36 sizes **+0.002586
[+0.001073, +0.005076]** against the real +0.004107 · NOISE FLOOR sham sd **0.000974**.

**WORLD C** — only the corner separates. **The estimand moves verdicts and does not move the
definition.**

## R793 · the coverage audit, and where the "preserves ITS verdicts" retirement actually rests

**Coverage.** 11 deliberate artifacts (not `sat_`, `sat08_`, `core_`); **4** opened by this arc's 468
`run.py` files, **7** by none: `ablate_novel`, `dimension_curve`, `importance_recoverable`,
`similarity_gradient`, `synthetic_world`, `unit_robustness`, `whose_verdicts`.
⭐ **`importance_recoverable` IS NOW READ AND FOLDED IN** — see the closure section at the end
of this file. ⚠ **The `7` above is NOT decremented here.** R793's count was produced by an
instrument that scanned 468 `run.py` files; editing the number by hand would make the text
disagree with the instrument that computed it. The correct repair is to re-run R793's scan,
which is a round, not an edit. **Reading an artifact does not license editing a count nobody
recomputed.** Positive control (R792
found for the file R792 opens) PASS; negative control PASS after repair.

**Derived before measuring.** D1 the `vs FULL` column is deterministic and cannot move — the exact
object check. D2 all-annotator averaging IS the arc's A2. D3 sampling 1 of 16 inflates variance and
leaves expectation alone, so a POINT move would mean something other than sampling. D4 dividing by a
ceiling is **not** disattenuation; that divides by its square root.

**E2 · all annotators against the shipped 1-annotator design.**

| arm | vs HUMAN (all) | shipped | Δ | vs FULL | raw difference |
|---|---:|---:|---:|---:|---|
| `coval_core` | 0.5665 | 0.5682 | −0.0018 | 0.7850 | −0.2185 [−0.2336, −0.2024] |
| `topw_k4` | 0.5642 | 0.5650 | −0.0008 | 0.8049 | −0.2407 [−0.2567, −0.2255] |
| `gen` | 0.5352 | 0.5386 | −0.0035 | 0.7414 | −0.2062 [−0.2217, −0.1914] |
| `full` | 0.5087 | 0.5136 | −0.0049 | 1.0000 | −0.4913 [−0.5009, −0.4811] |
| `gen_sham` | 0.4828 | 0.4834 | −0.0006 | 0.7023 | −0.2195 [−0.2343, −0.2045] |
| `random_k4_s0` | 0.4927 | 0.5005 | −0.0078 | 0.8247 | −0.3320 [−0.3454, −0.3176] |
| `topvar_k4` | 0.4863 | 0.4882 | −0.0019 | 0.8586 | −0.3724 [−0.3845, −0.3592] |

Largest move **0.0078**, all negative — the under-powered design overstated the human column, as D3
predicted. **World C did not fire.**

**E3 · the normalisation curve.** raw → **A** (registered) · /CEIL_H → **B** (shipped) · /√CEIL_H →
**A** (standard). Normalised values: `coval_core` 1.0264 / 0.7625 against `vs FULL` 0.7850;
`topw_k4` 1.0223 / 0.7594 against 0.8049; `gen` 0.9697 / 0.7204 against 0.7414. CEIL_H sweep returns
B in 1.000 of 400 draws.

**E4 · reconciliation.** `unit_robustness.json` — prompt order == annotator order, 0 inversions.
R792 — 11 of 190 pair verdicts flip. Both hold; ORDERING and PAIRWISE RESOLUTION are different
objects.

**Controls.** OBJECT worst |Δ| **1.110e-16** on the deterministic column, exit 2 otherwise · PLACEBO
`full` vs FULL **1.000000000000** · POSITIVE band, raw crosses zero only at δ=0.30 · NEGATIVE
`full`'s class shuffled 0.7850 → 0.4998 with vs HUMAN unchanged to 0.0e+00 · SHAM against
`random_k4_s0`'s class 0.7342 · NOISE FLOOR split-half 0.003523. **WORLD A.**

## R794 · why the normalisation question did not have to be asked

**The wall.** R793 closed on *"the first thing in this arc that no further computation can decide."*
It was decided by two comparisons already computable from data R793 had loaded — the fifth wall to
fall in seven rounds.

**Derived before measuring.** D1 a same-target comparison needs no ceiling, because a common ceiling
divides out. D2 Q1 and Q2 are not complementary, so the fork can be FALSE rather than mis-measured.
D3 `core vs FULL` may be inflated by both tracking the human — **refuted by its own control**. D4
`full` is 1.0 against itself by construction and must be excluded from the regression.

**Q1 · preserving the rubric** (both sides against `coval_full`'s class):

| arm | vs FULL | shuffled-full floor | random-arm sham | excess over shuffled |
|---|---:|---:|---:|---|
| `coval_core` | 0.7850 | 0.4888 | 0.7363 | **+0.2961 [+0.2744, +0.3166]** |
| `gen` | 0.7414 | 0.4941 | 0.6993 | +0.2472 [+0.2268, +0.2689] |
| `full` | 1.0000 | 0.4969 | 0.8192 | +0.5031 [+0.4876, +0.5183] |

**Q2 · beating the rubric at the human** (both sides against the human annotators):

| arm | vs HUMAN | `full` vs HUMAN | difference | MDE | |
|---|---:|---:|---|---:|---|
| `coval_core` | 0.5665 | 0.5087 | **+0.0578 [+0.0502, +0.0658]** | 0.0111 | RESOLVED |
| `gen` | 0.5352 | 0.5087 | +0.0265 [+0.0173, +0.0352] | 0.0130 | RESOLVED |

**D3's regression**, 20 objects, `full` excluded: slope **−0.4825**, residual sd **0.0450**,
`coval_core` residual **+0.0286 [+0.0199, +0.0377]** = **+0.64** residual sd. Resolved against prompt
resampling; not exceptional among arms. ⚠ The preregistration asked for this CI and the first draft
computed a point, which would have made the World-A branch unable to fire; closed before shipping.

**Controls.** OBJECT R793's two columns reproduced to **0.000e+00**, exit 2 otherwise · PLACEBO every
arm against its own class exactly 1.0 · POSITIVE the plant alone does not resolve at δ=0 and resolves
from 0.005 · NEGATIVE `full`'s class shuffled sends Q1 to 0.4888 while Q2 is unchanged to 0.0e+00 (a
derivation — Q2 never touches `full`'s class) · SHAM Q1 against a random arm's class 0.7363 ·
NOISE FLOOR split-half 0.003523.

**Multiplicity.** 41 tests, BH over the UNION of both families: **40 survive, 1 does not.**
**WORLD C — the fork is false.**

## R795 · size versus identity, and why the matching floor was misdirection

**The confound, found before building.** `full` carries mean k **15.48**; every k4 arm carries
**4.00**; `genericpool16` carries **16.00** and is prompt-blind. R794's specificity comparison varied
whose criteria the target is built from AND how many, at once.

**Derived before measuring.** D1 a k-subset dose must terminate at `vs full` = 0.7850 — the positive
control. D2 k = 1 targets may be degenerate; the share is reported (measured **0.000** at every k).
D3 size and identity separate into two one-factor comparisons. D4 the core is 98.8% novel (R785), so
no subset of `full` is a superset of it.

**E1 · the dose, content fixed** (20 draws per cell):

| k | matched | sd | mismatched prompt | sd | gap |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.6403 | 0.0066 | 0.4762 | 0.0059 | +0.1641 |
| 2 | 0.6944 | 0.0094 | 0.4975 | 0.0071 | +0.1969 |
| 4 | 0.7362 | 0.0058 | 0.4999 | 0.0060 | +0.2362 |
| 8 | 0.7691 | 0.0039 | 0.4995 | 0.0040 | +0.2696 |
| 12 | 0.7801 | 0.0031 | 0.5029 | 0.0016 | +0.2772 |
| all | **0.7850** | 0.0000 | 0.5053 | 0.0000 | +0.2796 |

Monotone; terminates at the committed value.

**E2/E3 · identity at matched k = 4**, 21 size-matched comparators: a 4-subset of `full` **0.7362**
against the mean k = 4 arm **0.7734** → **−0.0372 [−0.0446, −0.0294], p 0.0008**. Tails: the
full-subset beats `topw_k4_sham` (+0.0203) and `topabs_k4` (+0.0155) resolvedly and loses to
`topw_k4` and its aliases by **−0.0990 [−0.1097, −0.0880]**. BH q=0.05: 17 of 21 survive.

**E4 · the neutral, size-matched comparator**: `coval_core` vs `genericpool16` (k = 16, blind)
**0.7886** against `vs full` (k = 15.48, matched) **0.7850** → **−0.0036 [−0.0195, +0.0119],
p 0.6550, UNRESOLVED**.

**The poison correction.** The mismatched-prompt floor is another prompt's *specific* criteria — 
misdirection, landing at ≈0.50 — while the *neutral* floor lands at 0.7886, level with the matched
target. R794's Q1 excess of +0.2961 is therefore priced against a poison and is **DOWNGRADED**.

**NO WORLD CLAIMED** — the outcome was resolved and negative, which no registered branch covered.

## R796 · the matched-versus-blind dose: what prompt-matching buys when the floor is absence

**The instrument.** `sat_genericpool16.npz` ships per-criterion satisfactions, so a BLIND dose over k
is constructible exactly parallel to R795's matched one. ⚠ `randblind_k4_s0/s1/s2` cover **1 prompt
each** and are not population arms — caught in check #398 before use.

**Derived before measuring.** D1 the blind k=16 cell IS `vs genericpool16`, the object check. D2 both
doses must rise with k or the curves are not comparable. D3 the matched k=16 cell is a MIXTURE
(`full` has mean 15.48 criteria), so the clean cells are k ≤ 12. D4 `generic` = `POOL[0:4]` must lie
inside the blind k=4 distribution.

**E1/E2 · the two doses and the gap** (20 draws per cell, 968 prompts):

| k | matched | sd | blind | sd | gap | |
|---:|---:|---:|---:|---:|---|---|
| 1 | 0.6391 | 0.0080 | 0.7175 | 0.0068 | **−0.0784 [−0.0890, −0.0686]** | RESOLVED |
| 2 | 0.6928 | 0.0058 | 0.7590 | 0.0030 | **−0.0663 [−0.0770, −0.0554]** | RESOLVED |
| 4 | 0.7356 | 0.0063 | 0.7771 | 0.0025 | **−0.0415 [−0.0530, −0.0290]** | RESOLVED |
| 8 | 0.7693 | 0.0036 | 0.7848 | 0.0028 | **−0.0155 [−0.0285, −0.0014]** | RESOLVED |
| 12 | 0.7805 | 0.0024 | 0.7863 | 0.0016 | −0.0058 [−0.0201, +0.0086] | unresolved |
| 16 | 0.7842 | 0.0018 | 0.7886 | 0.0000 | −0.0044 [−0.0196, +0.0111] | unresolved ⚠ MIXTURE |

Both monotone: matched 0.6391 → 0.7842, blind 0.7175 → 0.7886.

**The pool-size confound control**, registered before the run, on the **437 of 968** prompts with
≥ 16 criteria: k=4 **−0.0550 [−0.0705, −0.0380]** · k=8 **−0.0311 [−0.0493, −0.0132]** · k=12
**−0.0228 [−0.0418, −0.0031]**. Every cell more negative; k=12 becomes resolved.

**E3 · the whole population**, `vs full` − `vs genericpool16`: `topvar_k4` **+0.1572 [+0.1424,
+0.1723]** · `topwvar_k4` +0.1420 · `random_k4_s2` +0.1231 · **`coval_core` −0.0036 [−0.0195,
+0.0119], rank 15 of 27** · `generic` and `generic_reprov` −0.2076 · `genericpool16` −0.2467.

**D4, failed and repaired exactly.** 20 draws gave [0.7727, 0.7803] and `generic` at **0.7856** sat
outside. The admissible check is the exact family: all **1,820** blind 4-subsets span
**[0.7357, 0.8025]**, mean **0.7767**, `generic` at percentile **76.3 — INSIDE**; the 20-draw mean
**0.7771** against the exact **0.7767** shows the dose unbiased and only its range too narrow.

**Controls.** OBJECT matched all-criteria to **2.2e-16** and blind k=16 to **0.0e+00** against
committed values, exit 2 otherwise · PLACEBO **1.000000000000** · POSITIVE both doses monotone with
bands printed · NEGATIVE the core's class shuffled sends matched to **0.5138** and blind to
**0.5083** · NOISE FLOOR largest draw sd **0.0080**. BH over 33 tests: **23 survive, 10 do not**.
**WORLD B.**

## R797 · the target-quality gap: the rubric is the weaker human predictor

**The question.** Check #399 found R796's NEXT rested on a pair R789 had already separated
(`coval_core` 0.5665 against `topvar_k4` 0.4863) and on a correlation of −0.2550 over 27 names. But
it surfaced a sharper object: the two TARGETS differ as human predictors.

**Derived before measuring.** D1 both columns are proportions against the same target, so no ceiling
enters. D2 |r| must reach ~0.44 at n=20 to exclude zero, so a correlation without its MDE is silence.
D3 the 27 names collapse to 20 distinct objects. D4 mixtures of the two targets produce an inverse
relation BY CONSTRUCTION whenever the pool is the better predictor.

**E1 · the gap**: `genericpool16` vs HUMAN **0.5422329001**, `coval_full` vs HUMAN **0.5087225654**,
paired over 968 prompts and all annotators: **+0.0335 [+0.0251, +0.0420]**, MDE **0.0118**,
p 0.0008 — **RESOLVED**.

**E2 · the size confound**, stratified by the prompt's own criterion count:

| criteria | n | gap | mde | |
|---|---:|---|---:|---|
| 4–8 | 80 | +0.0268 [+0.0019, +0.0527] | 0.0368 | unresolved |
| 9–12 | 222 | +0.0361 [+0.0194, +0.0558] | 0.0258 | RESOLVED |
| 13–16 | 299 | +0.0292 [+0.0160, +0.0429] | 0.0204 | RESOLVED |
| 17–20 | 206 | +0.0450 [+0.0269, +0.0634] | 0.0266 | RESOLVED |
| 21–39 | 161 | +0.0267 [+0.0054, +0.0475] | 0.0295 | unresolved |
| **12–20 matched** | **573** | **+0.0369 [+0.0244, +0.0454]** | 0.0155 | **RESOLVED** |

Same sign in all five; BH over 6 tests: **6 survive**.

**E3 · R796's correlation, done properly**: −0.2550 over 27 names, **−0.3138 over the 20 distinct
objects**, permutation **p 0.1820**, against an **MDE of |r| = 0.6** at 80% power. Unresolved.

**E4 · and its sign was forced**: synthetic mixtures of `full`-like and pool-like classes give
**−0.6872 [−0.8817, −0.4018]** by construction. The observed −0.3138 is weaker than the forced
value, which is stated rather than used.

**Controls.** OBJECT both A2 values reproduced to 1e-9 against committed numbers, exit 2 otherwise ·
PLACEBO a target against itself **0.000000000000** · POSITIVE the plant does not resolve at δ=0 and
resolves from 0.01 · NEGATIVE human classes shuffled sends `full` to **0.4266**, the pool to
**0.4255**, and the gap to **−0.0011** · NOISE FLOOR annotator split-half on the gap **0.002832**,
twelve times smaller than the effect. **WORLD A.**

## R798 · the singleton decomposition: individually weaker, and it is accuracy not discrimination

**Derived before measuring.** D1 `composite = (1 − tie) × accuracy` — **FALSE as registered**; a tie
CAN agree, because `cls()` returns 0 when a human ranks two responses equally. D2 each `full`
criterion appears on exactly one prompt, so no per-criterion estimate exists. D3 the aggregate is not
the mean of the singletons. D4 the pool's instances cluster by CRITERION (16), not by instance.

**E1 · the two distributions**, over criterion instances:

| pool | n | mean | interval | clustered by |
|---|---:|---:|---|---|
| `coval_full` | 14,984 | **0.4664** | [0.4609, 0.4730] | PROMPT |
| `genericpool16` | 15,488 | **0.5142** | [0.5057, 0.5228] | CRITERION (16) |

Paired-by-prompt gap **+0.0490 [+0.0441, +0.0543]**, MDE 0.0078 — **RESOLVED**.
⚠ The naive independent-instance half-width would be **±0.0025** against the clustered **±0.0085** —
a 3.4× overstatement avoided (D4).

**E2 · the decomposition**: discrimination `full` **0.9526** vs pool **0.9476**, gap
**−0.0053 [−0.0077, −0.0029]** RESOLVED · accuracy-on-non-tied `full` **0.4805** vs pool **0.5332**,
gap **+0.0538 [+0.0486, +0.0592]** RESOLVED. **The whole effect is accuracy; `full` discriminates
slightly more and is right less than a coin.**

**E3 · individual versus aggregate**: singleton **+0.0490** against R797's aggregate **+0.0335**,
ratio **1.461**. Different quantities by D3 — summing partially recovers what the individual criteria
lack.

**E4 · the spread confound**: satisfaction spread `full` **0.1403**, pool **0.1192**; quintile gaps
+0.0285, +0.0418, +0.0485, +0.0664, +0.0892; **spread-matched gap +0.0577** against the raw +0.0490.
The confound was suppressing the effect.

**Controls.** OBJECT both summed aggregates to 1e-9 against committed values, exit 2 otherwise ·
PLACEBO ⛔ D1 failed at **3.246e-01**; corrected identity checks at **2.220e-16** · POSITIVE ⛔ the
first threshold demanded a 0.05 drop where **0.0284** was the maximum; repaired to a direction
inversion with a computed band **0.5142 → 0.3184**, drop 0.1958 · NEGATIVE humans shuffled sends
`full` to **0.4115** and the pool to **0.4103** · NOISE FLOOR annotator split-half **0.001699**, the
gap 29× it. BH over 3 tests: **3 survive**. **WORLD A.**

## R799 · deconvolving the instance spread, and what only the generic pool can separate

**The design R798 proposed was inadmissible.** One instance is 5.73 non-tied pairs × 16.1 annotators
= 92 draws, SE ≈ 0.0521, so ranking 14,979 noisy estimates and reading a share off the ranking
measures the noise (§4, *conditioning on the outcome*).

**Derived before measuring.** D1 `var(obs) = var(true) + var(noise)`. D2 split-half needs no noise
model. D3 a pool criterion is observed on 968 prompts and a rubric criterion on 1. D4 an
annotator split-half leaves PROMPT variation inside "signal".

**E1/E2 · reliability and deconvolution:**

| | `coval_full` | `genericpool16` |
|---|---:|---:|
| split-half r (annotators) | **+0.8204 [+0.8172, +0.8278]** | **+0.7597 [+0.7531, +0.7668]** |
| Spearman-Brown | +0.9013 | +0.8635 |
| zero-signal control | +0.0080 | −0.0060 |
| observed sd | 0.1853 | 0.1649 |
| noise sd | 0.0578 | 0.0609 |
| **deconvolved signal sd** | **0.1760 (95.0%)** | **0.1532 (92.9%)** |
| naive share below 0.5 | 0.509 | 0.388 |
| **deconvolved share below 0.5** | **0.544** | **0.416** |

**E3 · the pool's 16 criteria, individually** (n = 968 each): 0.5585, 0.5553, 0.5483, 0.5482, 0.5452,
0.5404, 0.5404, 0.5329, 0.5310, 0.5278, 0.5265, 0.5246, 0.5198, 0.5154, 0.5130, 0.5048 — **sd
0.0157**, top-4 mean 0.5526, bottom-4 0.5133, and **16 of 16 exceed `coval_full`'s 0.4805**.

**⭐ The decomposition that follows**: criterion identity contributes **sd 0.0157** while the
instance-level signal is **sd 0.1532**, so most reliable variation is PROMPT, not criterion. For
`coval_full` this split is unavailable in principle (D3) and is declined rather than estimated.

**Controls.** OBJECT R798's accuracies reproduced to 1e-9 once the aggregation was matched — ⛔ the
first run exited 2 and located a defect in R798, whose LEVELS were instance-weighted (`full` 0.4805)
while its GAPS were prompt-weighted (0.4795); instance-weighted gap **+0.0527** against
prompt-weighted **+0.0538**, same sign, both resolved · PLACEBO self-split **1.000000000000** ·
POSITIVE planted sd 0.020 → **0.0200**, 0.080 → **0.0791**, band at both ends · NEGATIVE zero-spread
synthetic **+0.0080 / −0.0060** · NOISE FLOOR analytic 0.0521 against measured 0.0578 / 0.0609, so
the binomial model understates it. BH over 18 tests: **18 survive**. **WORLD A.**

## R800 · the two-way decomposition on the only fully-crossed grid in the release

**The grid.** All 968 prompts carry the identical pool criterion set `(0..15)`, so criterion, prompt
and interaction are separately identified (check #402). `coval_full`'s are not — each appears on one
prompt (R799 D3) — and the round declines that half rather than estimating it.

**Derived before measuring.** D1 on a crossed grid the marginal means identify the parts. D2 R799's
0.0157 is an UPPER bound; the correction is expected small. D3 the deficit is PAIRED, so its noise
must be measured on the DIFFERENCE. D4 a share read off a ranking is biased away from the centre.

**E1 · the components:**

| component | variance | sd | share of total 0.027171 |
|---|---:|---:|---:|
| criterion | 0.000237 | 0.0154 | **0.9%** |
| **prompt** | **0.018197** | **0.1349** | **67.0%** |
| interaction | 0.004965 | 0.0705 | 18.3% |
| annotator noise | 0.003773 | 0.0614 | 13.9% |

D2 held: 0.0157 → **0.0154**.

**E2/E3 · the prompt-level deficit** (`coval_full` − pool): mean **−0.0538**, observed sd **0.0885** =
noise **0.0309** + signal **0.0829**; share of prompts where the rubric loses **naive 0.733**,
**deconvolved 0.743**. ⛔ Measured unpaired the noise would have been **0.0869** — nearly the whole
observed spread, and the round would have concluded the deficit is noise.

**E4 · the size confound**: `full` carries 4–39 criteria (mean 15.48); size-matched deficit
**−0.0543** against raw **−0.0538**, worth 0.0006.

**Controls.** OBJECT instance sd **0.1648692616** and across-criteria sd **0.0156900510** against
R799's committed values to 1e-9, exit 2 otherwise · PLACEBO a cell against itself **0.0e+00** ·
POSITIVE two synthetic crossed grids — interaction-heavy 0.01/0.03/0.12 recovered as
**0.012/0.030/0.118**, prompt-heavy 0.01/0.12/0.03 as **0.013/0.123/0.027**, both distinguished in
the right direction · NEGATIVE criterion labels shuffled within prompt drives `s2_criterion`
**0.000237 → 0.000004** with the total unchanged to **3.5e-18**. **WORLD B.**

## R801 · the pooled-mean/robustness frontier over 1,820 blind cores

**Well-posedness first.** `select_core.py:121` loops PER PROMPT, so rubric-derived arms have no
cross-prompt objective and cannot express this choice. It is real only for BLIND arms, where one
criterion set serves all 968 prompts — giving C(16,4) = **1,820** candidate cores.

**Derived before measuring.** D1 two anchors — the all-16 subset IS `genericpool16` (exact) and
(0,1,2,3) IS `generic` ⛔ (**refuted by R788 before this round was written**: same criterion set,
different judge pass, satisfactions differing by mean |Δ| 0.005638). D2 an affine robustness
statistic cannot disagree with the mean, so the estimand is the RESIDUAL. D3 a worst-decile is an
order statistic, biased down and noisier. D4 the 1,820 share the same prompts, so differences need a
PAIRED bootstrap.

**E1 · the space**: pooled mean **[0.5144, 0.5575]**, across-subset sd **0.0082**; cross-prompt sd
**[0.1479, 0.1614]**, noise-corrected **[0.1354, 0.1501]**; worst-decile **[0.2257, 0.2783]**.

**E2 · the residual**: −cross-prompt sd R² on the mean **0.7844** (residual sd 0.00119) ·
worst-decile **0.8366** (0.00417) · −noise-corrected sd **0.7843** (0.00129). Argmaxes:
pooled mean **(0,3,9,14)** · −sd **(1,2,3,14)** · worst-decile **(0,1,9,14)** — **the two robustness
statistics disagree with each other.**

**E3 · the price**: mean forgone by the −sd argmax **+0.00358 [−0.00136, +0.00818]**, by the
worst-decile argmax **+0.00085 [−0.00280, +0.00429]** — both **unresolved**. Pareto-optimal in
(mean, −sd): **4 of 1,820**, and the pooled-mean winner is among them.

**E4 · the released blind arm**: `generic` = `POOL[0:4]` — mean **0.5504, percentile 93.7**;
cross-prompt sd **0.1504, percentile 3.1**; worst-decile 0.2721. Near-optimal on both at once.

**Controls.** OBJECT anchor 1 exact at **0.0e+00**; anchor 2 **|Δ| 0.000918** inside R788's
**0.005638** after repair, having exited 2 first · PLACEBO **0.0e+00** · POSITIVE a mean-preserving
perturbation leaves the mean at **+0.00e+00** while cross-prompt sd goes 0.1490 → **0.1500** →
**0.1731** and the decile 0.2765 → **0.2726** → **0.2436** · NEGATIVE humans shuffled sends the mean
**0.5386 → 0.4247** · NOISE FLOOR per-prompt split-half variance **0.003527**.
**NO WORLD CLAIMED** — the pre-registered first branch.

## R802 · auditing the register, and what a `## IMPOSSIBLE HERE` line is worth

**Derived before measuring.** D1 an impossibility is a UNIVERSAL claim — refuted by one instance,
never confirmed by their absence, so verdicts are FALSE / UNVERIFIED. D2 a `run.py` grep UNDERcounts
readers, so 23 is a lower bound. D3 the cross-release line has two readings and both are reported.
D4 this round excludes itself from its own population, as R793 had to.

**E1 · the population**: 13 rounds (R789–R801), **52** tight lines / **65** loose, ratio **1.25**,
**30** distinct claims after normalisation.

**E2/E3 · the verdicts**: **1 FALSE of 30** — base rate **3.3%**. The false line is *cross-release*,
contaminating **8 rounds** (R791, R792, R793, R795, R796, R798, R799, R800). The 29 survivors are
listed in full in the run output; the most repeated are *independently replicated* (13 rounds),
*construct validity* (3), *a blind pool larger than 16* (2).

**D3 · both readings**: (i) any second corpus with human judgement → **FALSE**, since
`data/utterances.jsonl` holds 68,371 utterances with a human `score` and **23** rounds read it;
(ii) rubrics + per-annotator rankings → **UNVERIFIED**, since it carries neither.

**E4 · the correction to R801**: clause markers **① 6 · ② 56 · ③ 18 · ④ 0 · ⑤ 0**; exclusion-test
rounds **7** (R360, R403, R436, R464, R665, R688, R790). R801 said "two of five"; both are wrong, and
"five" was imported from §4's narrative.

**Controls.** OBJECT the file present at 68,231,088 bytes with ≥18 readers, exit 2 otherwise ·
PLACEBO the extractor over an empty list returns **0**, not an error swallowed as 0 · POSITIVE a
known-TRUE line is **not** condemned (an over-firing instrument would) · NEGATIVE a known-FALSE line
**is** condemned (without it the extractor is untested in one direction) · both extractors reported.
**WORLD A.**

## R803 · the judge-free floor, drawn on release one for the first time

**Why here.** R802's NEXT proposed transporting R794's Q2 to release two; that needs a judge pass over
68,371 utterances which does not exist, since every `sat_*.npz` is keyed to release one. R433 had
measured a judge-free length heuristic on release TWO; the FIRST release — where every committed A2
lives — had never been checked against one.

**Derived before measuring.** D1 a judge-free predictor is a FLOOR, not a rival. D2 the sign is not
forced, so this is a measurement. D3 the comparison is paired and needs no new instrument. D4 if
length predicts criterion satisfaction the arms inherit its power.

**E1 · the six predictors** (all reported; the floor is a MAX over them, which is a selection and is
stated): characters longer **0.4557** / shorter 0.4023 · tokens longer 0.4351 / shorter 0.4063 ·
position 0.4182 / 0.4421.

**E2/E3 · the arms**: floor **0.4557**; arms span **0.4828–0.6283**, median **0.5642**.
**27 of 27 beat the floor resolvedly and 27 of 27 survive BH.** `gen_sham` (weakest) **+0.0271
[+0.0134, +0.0409]** · `coval_core` **+0.1108 [+0.0989, +0.1233]** · `oracle_k4` **+0.1726
[+0.1610, +0.1844]**.

**E4 · D4's partialling**: slope of an arm's per-prompt A2 on the floor's — mean **+0.1211**, range
**[+0.0632, +0.1738]**, `coval_core` **+0.1005**. ⚠ The residual MEAN is 0 by construction (OLS), so
the slope is the informative quantity; and the residual is a lower bound because partialling removes
shared prompt difficulty too.

**Controls.** OBJECT `coval_core` recomputed **from raw response text + annotators** reproduces
R789's committed **0.5664774812** exactly, exit 2 otherwise · **PLACEBO a constant predictor gives A2
0.1397355039 against a human tie rate of 0.1397355039 — identical to ten decimals, computed not
assumed** · POSITIVE `oracle_k4` − floor **+0.1726**, band placebo **0.1397** → oracle **0.6283** ·
NEGATIVE lengths shuffled within prompt **0.4557 → 0.4305** · NOISE FLOOR annotator split-half
**0.003295**, and the weakest arm's margin is 8× it. **WORLD A.**

## R804 · both ends of the A2 axis, and the "human ceiling" was never one

**Why here.** R803's NEXT asked what an A2 above the human ceiling means. CHECK #406 read the
ceiling's source: `whose_verdicts.py:65` computes it as `a2(annotator_i, annotator_j)` — noise on
both sides — while an arm is a deterministic predictor scored against each annotator. A noiseless
predictor of the central tendency beats pair-agreement **by construction**.

**Derived before measuring.** D1 two noisy raters agree less than a noiseless one. D2 a strict
predictor forfeits the tie mass outright. D3 `CEIL_PLUR ≥ CEIL_ATT`, the gap being human
intransitivity. D4 the k-consensus curve must be monotone.

**E1 · the ceiling is EXACT, not estimated.** Four responses admit **75 weak orders** and every
scoring function induces one, so the supremum of A2 is a per-prompt brute-force max:
**`CEIL_ATT` = 0.686265**. Per-pair plurality (transitivity ignored) is 0.686701, so **human
intransitivity costs +0.000436** — the human plurality is very nearly transitive.

**E5 · and the in-sample oracle is not attainable.** Fitted on half the annotators and scored on the
other half: **`CEIL_HO` = 0.633370, optimism +0.052895.** Both are reported; quoting only `CEIL_ATT`
flatters every arm.

**E2 · the axis.** floor **0.4557** (R803) < `CEIL_H` **0.551880** < best arm **0.6283** <
`CEIL_HO` **0.633370** < `CEIL_ATT` **0.686265**. As a share of the **generalising** range:
`oracle_k4` 97.1% · `greedy_k4` 94.0% · **`coval_core` 62.4%** · `generic` 53.8% ·
`genericpool16` 48.7% · `gen_sham` 15.3%. **14 of 27 arms exceed `CEIL_H`; 0 exceed `CEIL_ATT`**
(forced — a code check, never evidence). Headroom to the ceiling is resolved for all 27 and **27 of
27 survive BH**, so **no arm is at the ceiling** — `oracle_k4`'s own headroom is **+0.0580 [+0.0529, +0.0633]**.

**E4 · ties.** On human-tied pairs the best arm scores **0.0186** against one annotator's 0.2182; on
strict pairs **0.7220** against 0.5875. A strict predictor forfeits the tie mass and wins anyway —
its advantage on strict pairs alone is **+0.1346**. World C dead.

**E3 · what was NOT computed.** Annotator-equivalents. D4 failed on both estimators, so none is
quoted. The k-curve (mean-score consensus): 0.551055 / 0.550943 / 0.584223 / 0.597517 / 0.614237 /
0.620795 / 0.624963 at k = 1/2/3/4/6/8/12. The pre-registered estimand survived the unfit method
because it does not need monotonicity: **a 3-annotator consensus scores 0.584223 against `CEIL_H`
0.551880 and beats it directly.** ⚠ `CEIL_H` landing at k=1 is FORCED, and is used as a positive
control on the curve rather than quoted as a result.

**Controls.** OBJECT `CEIL_H` reproduced by R793's own exhaustive method **0.551880** exactly ·
PLACEBO constant predictor **0.1397355039** = the human tie rate **0.1397355039** · POSITIVE one
annotator as predictor **0.555874**, band **0.1397 < t < 0.6863** · NEGATIVE each annotator slot
filled from a different prompt **0.686265 → 0.527548** (best corpus-wide constant 0.451773) ·
NOISE FLOOR **0.001991**. **WORLD A.**

## R805 · the held-out arms scored held-out — fitting survives, and the census was contaminated

**Why here.** R804's NEXT proposed cross-validating the oracle selection over PROMPTS. CHECK #407
read the selector: `select_core.py` chooses **per prompt** against that prompt's own modal human
class, so nothing transfers across prompts and the split is ill-posed — R801 established this and
the NEXT proposed it anyway. The correct split is over **annotators**, and it already existed:
`--fit-parity` (`select_core.py:55`) with 16 committed `*_fit1` files.

**One split, every quantity under it.** floor_p0 **0.457228** · **`CEIL_HO_p0` 0.636344** (best weak
order fitted on parity-1, scored on parity-0 — the same estimator class as the fitted arms) ·
`CEIL_ATT_p0` 0.707062 (in-sample upper bound; `CEIL_HO ≤ CEIL_ATT` is forced and run as a code
check).

**E2 · the arms on parity-0, as a share of `[floor_p0, CEIL_HO_p0]`**: LEAKY `oracle_k4` 0.6314
(97.2%) · held-out `oracle_k4_fit1` **0.5993 (79.3%)** · `greedy_k4_fit1` 0.5984 (78.8%) ·
`indep_k4_fit1` 0.5866 (72.2%) · **`coval_core` 0.5677 (61.7%)** · `topw_k4` 0.5656 (60.5%) ·
`generic` 0.5533 (53.7%) · `genericpool16` 0.5441 (48.5%) · `full` 0.5099 (29.4%) · `random_k4_s0`
0.4937 (20.4%) · `gen_sham` 0.4845 (15.2%). **BH 10 of 11 survive**; the non-survivor is
`genericpool16` against **itself**, a degenerate self-test and a built-in placebo.

**⭐ THE FINDING.** `oracle_k4_fit1` − `genericpool16` on parity-0 = **+0.0553 [+0.0456, +0.0653]**,
20× the noise floor. **Fitting a core to a prompt's own human labels is an admissible route with
real content** — it does not vanish when the labels it is scored on are held out. WORLD A.

**⛔ E3 · two inflations, both now measured.** (a) R294's committed census builds `HC[p]` from ALL
annotators (`R294/run.py:110`), so its `oracle_k4_fit1 = 0.6142` is scored on annotators half of
which are its own fit set: contamination **+0.014832 [+0.011175, +0.018461]**, and `greedy` +0.012214,
`indep` +0.007470. ⭐ The honest arm prices the confound: `coval_core` (no prompt labels) shows
**−0.001218 [−0.004766, +0.002230]**, a null — so the gap is the labels, not the split.
(b) The answer key itself: LEAKY `oracle_k4` − held-out `oracle_k4_fit1` on parity-0 =
**+0.032022 [+0.026225, +0.038194]**. ⚠ D3 — R295 measured that the fit1 advantage concentrates
where the halves agree, so **every leak number here is a LOWER bound**.

**⛔ E4 · and R804's headline was mine to correct.** R804 published *"the best arm reaches 97.1% of
the generalising range"* — a LEAKY arm against a HELD-OUT ceiling, with the caveat in prose and the
number left standing. Matched: **79.3%**.

**Controls.** OBJECT R293's committed **0.631353 / 0.625062** reproduced exactly, plus `coval_core`
**0.5664774812** · PLACEBO parity-0 constant **0.1389806792** = parity-0 tie rate **0.1389806792** ·
POSITIVE each fit scores higher on its own half (0.630410 > 0.599331 · 0.624184 > 0.598415 ·
0.602500 > 0.586595), band **0.1390 < t < 0.7071** · NEGATIVE cores against another prompt's humans
0.567696 → **0.422319** · NOISE FLOOR **0.002181** · population 968 prompts, **0 dropped**.

## R806 · the relative test is blind, so the leak verdict stands and R805's clause must narrow

**Why here.** CHECK #408 killed R805's NEXT — R295 had already run the low-agreement stratification
and committed `killed = True` — and found the contradiction R805 created: R805's WORLD A ("fitting
has real content", +0.0553 pooled) against R295's committed **−0.0054** for the same arm in the
quintile where the two annotator halves disagree. R805 cited R295 for a caveat and never reconciled.

**The attack, and it failed honestly.** R295 subtracts the honest arm's slope **additively** while
the confound is plausibly **multiplicative** (agreement raises every arm). Relative profiles —
each arm's quintile margin over its own pooled margin — give **fitted − honest = +0.2491 [−0.1838,
+0.6804]**, a CI holding 0. ⭐ **But the same statistic cannot separate a PERFECT LEAK either**:
`_perfect_leak` (parity-1's own modal class as the predictor) **minus honest = +0.4499 [−0.0447,
+0.9647]**. **A statistic blind to a maximal leak cannot exonerate anything** — E2 is **UNVERIFIED**,
never OVERTURNED.

**E3 · so an independent binning variable decides.** R295 binned on parity-1↔parity-0 agreement
while scoring on parity-0 — a shared term it named and left. Re-binned on agreement **within
parity-1 only**: fitted slopes **+0.0302 [+0.0217, +0.0392]** · **+0.0251 [+0.0165, +0.0344]** ·
**+0.0213 [+0.0124, +0.0309]**, all resolved; honest slopes **+0.0084 [−0.0001, +0.0164]** and
**+0.0049 [−0.0029, +0.0127]**, both holding zero. Fitted mean **+0.0256**, honest **+0.0067**,
excess **+0.0189**, against a perfect-leak ceiling of **+0.0350**. **BH 4 of 6 survive**; the two
non-survivors are the honest arms. ⚠ D3: `corr(within-parity-1, half-agreement) = +0.7790`, so this
is a **weaker** instrument, not an independent replication.

**E4 · the reconciliation.** Bottom quintile: **fitted −0.0110, honest −0.0024**. The fitted arms go
negative exactly where parity-1 stops predicting parity-0. **So R805's +0.0553 is a property of
high-agreement prompts, not of the fitted route** — R295's W-LEAK stands and the clause narrows.
**WORLD A.**

**Controls.** OBJECT R295 reproduced exactly (N 968 · agreement 0.552048 · slope 0.033719 · floor
0.008548 · full quintile vector) · PLACEBO the k=4 pool against itself, **0.0e+00** in all five
quintiles · POSITIVE (absolute) synthetic perfect leak **+0.046491 [+0.034749, +0.058202]**, steepest
of all seven · **POSITIVE (relative) FAILS, and that failure is the finding** · NEGATIVE binning
permuted, all three slopes hold 0 · population 968, **0 dropped**.

## R807 · a calibrated scale for "how much of an arm is the leak" — and WORLD C by my own branch

**Why here.** R806 left the fitted arms at roughly half the maximal-leak profile and proposed
regressing each fitted arm's per-prompt margin on the synthetic `_perfect_leak`'s. CHECK #409 found
that as posed both margins are scored on the **same** parity-0 annotators, so their errors are
correlated — the shared-term defect R806 had just corrected in R295.

**⛔ The original estimand was unidentified, and this round's own g=0 control found it.** R804 had
already killed the OLS residual mean (0 by construction), so I used the **intercept**. The g=0
control — the same predictor scored on two independent halves, nothing planted — returned intercept
**+0.0271**. That is errors-in-variables: `intercept = (1 − λ)·mean(y)`. **Derivation check:
(1 − 0.4774) × 0.0512 = +0.026772 vs observed +0.027134, |diff| 0.000362.** So "content = +0.0213"
was mostly the fitted arms having larger mean margins — R806's scale trap in a new coordinate.

**⭐ The identified estimand: the DISATTENUATED slope.** λ is measured directly as the leak's own
split-half reliability (**0.4597** on the fixed split), and a pure copy of the leak scores exactly
**1.000** — a derivation, the ceiling. On that scale: `oracle_k4_fit1` **0.650 [+0.558, +0.751]** ·
`greedy_k4_fit1` 0.611 [+0.520, +0.719] · `indep_k4_fit1` 0.504 [+0.407, +0.606] · `coval_core`
**0.349 [+0.246, +0.454]** · `topw_k4` 0.338 [+0.237, +0.457]. **Paired, fitted − honest = +0.245
[+0.154, +0.333].** ⭐ The positive control lands at **0.651** against a predicted midpoint of
**0.659**, |diff| **0.008** — the scale is calibrated at a point neither end determines.

**⭐ The shared-draw inflation, measured**: same-draw minus split-draw slope is **+0.2757** ·
+0.2593 · +0.2233 for the fitted arms and +0.1328 · +0.1372 for the honest ones. D4 held for all
five. The shared annotator draw was worth about **half** the apparent association.

**⛔ WORLD C, and I am not overturning it.** My preregistration's first branch — placed first because
it kills the round — reads *"if honest slope CI overlaps fitted slope CI → WORLD C"*, and
`indep_k4_fit1`'s [0.407, 0.606] overlaps `coval_core`'s [0.246, 0.454]. **CI overlap between two
separately estimated quantities is not a test of their difference**, and the paired difference here
excludes zero — but the preregistration binds, so WORLD C stands with the paired number beside it.

**Controls.** OBJECT binning-free pooled margins **+0.051224409 / +0.047060767**, exact · PLACEBO
leak on itself, slope **1.000000000**, intercept **+0.000000000** · POSITIVE (repaired estimand)
0.651 vs 0.659 predicted · NEGATIVE **permutation null over 200 permutations**, null +0.0031
[−0.0492, +0.0561], the real slope +0.5727 outside the entire null · NOISE FLOOR 20 half-splits, sd
0.0136 / 0.0121 / 0.0109 / 0.0098 / 0.0112.

## R808 · the scale is precision-invariant, and the leak proxy's identity matters to the fitted arms

**Why here.** R807's scale is one division by an estimated λ and had never been swept. CHECK #410
also found that R807's NEXT asked for the wrong sweep: λ is the reliability of the **evaluation
draw** (parity-0), not of the proxy (parity-1). More parity-1 annotators change **what the leak is**;
more parity-0 annotators change **how noisily it is measured**. Two axes, two predictions.

**⭐ A-AXIS — the §4 remedy aimed at my own headline.** Holding the y-side fixed and varying the
x-side over k = 1,2,3,4 parity-0 annotators: **λ 0.2094 / 0.3477 / 0.4291 / 0.4864 (×2.32)**,
**raw slope 0.1292 / 0.2175 / 0.2671 / 0.3077 (×2.38)**, **disattenuated fitted mean 0.561 / 0.572 / 0.569 / 0.576 — spread 0.0154 against
3× its across-split sd of 0.1281.** **A-STABLE.** The pre-registered derivations both held: D1 λ
rises with k, D2 the raw slope rises with it, so raw drift is what attenuation predicts and only
corrected drift would have been evidence. *An estimate that does not move when its instrument
sharpens 2.3× is the one property that makes a disattenuated number trustworthy.*

**⭐ B-AXIS — a differential leak test no earlier round ran.** Building the leak's modal class from
j = 1,2,4,8 parity-1 annotators: `oracle_k4_fit1` **0.403 → 0.617**, `greedy_k4_fit1` 0.387 → 0.578,
`indep_k4_fit1` 0.339 → 0.492, against `coval_core` 0.231 → 0.314 and `topw_k4` 0.231 → 0.332.
**Fitted mean rise +0.186, honest +0.092, contrast +0.094** vs a pre-registered threshold of
**0.079** → **B-SPECIFIC**: the fitted arms track the specific labels they were fitted to, at twice
the rate of arms that never saw one. ⚠ The honest rise is **not** a defect but the floor — a modal
class from more annotators is a better estimate of the population ordering, which any good arm
tracks, and that is why the estimand is the differential. ⚠⚠ **MARGINAL at 1.19× the threshold; a
paired CI was not pre-registered and is not quoted**, so B-SPECIFIC is the rule firing, not a
resolved interval.

**Controls.** OBJECT R807's λ **0.459704** and all five disattenuated values reproduced exactly ·
PLACEBO the leak on itself **1.000000000** at every k · **g=0 the pure copy lands at 1.000000000 at
every k** · POSITIVE the planted arm within **0.006** of its predicted midpoint at all four k — a
calibration holding at one k and failing at another *is* the drift this round hunted · NEGATIVE
permutation nulls at both ends (k=1 max +0.0481 vs real +0.1467; k=4 max +0.0679 vs real +0.2867) ·
NOISE FLOOR **0.0427**. Population: 968 prompts, parity-0 median 8 (min 2, max 23), **620 of 968**
carry ≥8, and the A-axis uses each prompt's own cap rather than dropping prompts.

## R809 · B-SPECIFIC withdrawn — on a λ-free scale the fitted arms rise LESS than honest ones

**Why here.** R808 returned B-SPECIFIC on an additive contrast (+0.094 vs a 0.079 threshold, ratio
1.19) and flagged it as marginal. CHECK #411 found the arithmetic before the bootstrap ran: every
disattenuated value is `raw/λ_j`, and **λ_j falls with j** (0.5834 · 0.5658 · 0.5546 · 0.4954), so
every j=8 value carries a common multiplicative inflation and an arm **starting higher** collects a
larger absolute rise for free. **[DERIVATION]** `log dis(a,j) = log raw(a,j) − log λ_j`, and λ_j is
common to all arms, so it **cancels exactly** in a difference of log-rises.

**The two contrasts.** E1 additive **+0.0242 [−0.0606, +0.1131]** — contains 0. ⭐ E2 log
**−0.1317 [−0.4044, +0.1397]** — contains 0 **and points the other way**. **WORLD B: B-SPECIFIC
withdrawn.**

**⭐ The decomposition is the whole story.** Fitted arms **start** at 0.383, honest at 0.195 — a
ratio of **1.97× before anything about rising is measured**. Rises: additive +0.122 vs +0.098
(1.25×); **log +0.276 vs +0.408 (0.68×)**. R808's "the fitted arms rise twice as fast" was the fitted
arms **starting twice as high**. ⭐ And `topw_k4` — which never saw a human label for the prompt —
has the **steepest log-rise of any real arm, +0.494**: relative sensitivity to the proxy's identity
is not a property of having been fitted.

**⛔ R808's contrast was inside its own split noise.** Measured here, the across-split sd of the log
contrast is **0.1077** — larger than R808's entire +0.094, and the single-split additive estimate is
+0.0242. A threshold built from per-arm sds could not bound a contrast whose split-to-split
variation exceeds the effect.

**Controls.** OBJECT R808's whole B table reproduced — 4 λ_j and 20 disattenuated cells to 1e-6 ·
D4 λ_j falls with j, checked not assumed · PLACEBO the pure leak copy's log-rise **+0.000000000** ·
POSITIVE `_target_full` (the arms' actual fit target) **+0.6620**, largest of any arm, band
**+0.4081 < fitted < +0.6620** · NEGATIVE **arm-label permutation, exact over all 10 splits of 5
arms 3/2**, null [−0.1317, +0.1021], the real split ranking **1 of 10** — the most negative of every
possible labelling, where B-SPECIFIC predicted last · NOISE FLOOR **0.1077** · LOG DOMAIN 0
non-positive cells. **BH 4 of 5 per-arm log-rises survive; `coval_core` does not.**

**What survives**: R808's A-axis invariance and R807's scale itself. What is withdrawn is the claim
about how the fitted arms' position **changes** as the proxy sharpens, not the position.

## R810 · three quarters of the fitted advantage was size, and the remaining quarter is resolved

**Why here.** R809 left LEVEL as the only thing separating fitted from honest arms, but the fitted
arms measured throughout this arc are k=4 while `genericpool16` carries 16 — size and fitting were
confounded in every number. CHECK #412 also killed R809's NEXT as named: `--rule oracle_k` caps
enumeration at **20,000** combinations and **samples** above it (prompts over the cap: k=2 → 0,
k=4 → 31, **k=8 → 367**, k=12 → 254 of 968), so the oracle's identity changes with k. `greedy_k` and
`indep_k` are linear and were used instead, generated fresh at k ∈ {2,8,12}.

**⭐ The gap at matched k**, on the 734 prompts attaining nominal k at every k: **+0.0472 [+0.0374,
+0.0580]** at k=2 · **+0.0343 [+0.0256, +0.0426]** at k=4 · **+0.0160 [+0.0096, +0.0223]** at k=8 ·
**+0.0116 [+0.0070, +0.0162]** at k=12. **Monotone decreasing, 4× smaller at k=12, BH 4 of 4
survive.** The fitted levels themselves are **0.6046 · 0.6032 · 0.5896 · 0.5645** against `topw_k`'s
0.5574 · 0.5689 · 0.5735 · 0.5528 and the size-matched blind pool `POOL[0:k]`'s **0.5556** · 0.5568 ·
**0.5497** · 0.5482. **WORLD B** — fitting survives matched — **but three quarters of it was size**, and
R805's +0.0553 and R807's 0.50–0.65 were both measured at k=4 against a 16-criterion pool.

**⚠ D2, written before the run: the closure is partly forced.** A fitted arm at k = n **is** `full`,
so the gap must reach 0 at k = n. Median candidates here is **16**, so at k=12 the median prompt
leaves 4 unselected. ⭐ **But the shrinkage is not "less freedom":** median `C(16,k)` is 120 · 1,820 ·
12,870 · 1,820 at k = 2 · 4 · 8 · 12 — **non-monotone, peaking near k=8** — while the gap falls
monotonically. **The gap tracks k, not the option count**, which is what a size explanation predicts.

**E3, measured not assumed**: effective k is 2.00 · 4.00 · **7.92** · **11.32**, and prompts attaining
nominal k are 968 · 968 · 919 · **734**. Both populations reported; they agree to within 0.008.

**Controls.** OBJECT `greedy_k4_fit1` **0.598415** and `indep_k4_fit1` **0.586595** reproduce R805 ·
PLACEBO the blind pool against itself, `0.0e+00` at all four k · POSITIVE D1 `topw_k` → `full`,
⚠ **weakly**: the curve is non-monotone (0.5574 · 0.5689 · 0.5735 · 0.5528) and k=12 beats k=2 by
only 0.0046 · g=0 at k=2 the arms must not coincide, and do not · NEGATIVE each prompt's fitted core
against **another prompt's** parity-0 humans, null **−0.1211 [−0.1325, −0.1107]** vs real +0.0116 ·
NOISE FLOOR **0.0017**, so the surviving gap is 6.8× it.

## R811 · source and rule are the same size, so clause ② needs two baselines — and one was a 96th-percentile draw

**Why here.** R810 asked whether `topw_k`'s advantage over `POOL[0:k]` is resolved, to decide whether
clause ② names one baseline or two. CHECK #413 found that gap is non-monotone (+0.0018 · +0.0121 ·
+0.0238 · +0.0046) and confounds **source** (the prompt's own rubric vs a fixed generic set of 16)
with **rule** (weight-ranked vs uninformative). `random_k` — the rubric under an uninformative rule —
decomposes it.

**⭐ The decomposition, at matched k on 734 prompts.** RULE (informative − uninformative, within the
rubric): **+0.0752 [+0.0651, +0.0851]** · +0.0743 · +0.0699 · **+0.0419 [+0.0353, +0.0479]**.
SOURCE (generic pool − rubric, both uninformative): **+0.0568 [+0.0468, +0.0664]** ·
+0.0503 [+0.0390, +0.0613] · +0.0436 [+0.0320, +0.0552] · **+0.0372 [+0.0253, +0.0491]**. The k=4 and
k=8 rule cells carry [+0.0646, +0.0829] and [+0.0619, +0.0780]. **At k=12 the difference is +0.0047 [−0.0073, +0.0173] —
it contains zero. WORLD C: two baselines, not one.**

**⭐ And the source effect points against clause ②'s own assumption.** A fixed generic list of 16,
blind to the prompt, beats a random subset of the prompt's own rubric by **+0.0372 to +0.0568** at
every matched k. Under an uninformative rule, prompt-specificity is a **liability**. Cell levels:
rubric/uninformative **0.4823 · 0.4946 · 0.5036 · 0.5109**, rubric/informative 0.5574 · 0.5689 ·
0.5735 · 0.5528, pool/uninformative **0.5390 · 0.5449 · 0.5472 · 0.5482**. ⚠ The `pool × informative`
cell is **structurally absent** — the pool is one fixed list with no per-prompt weights (verified: 1
distinct criterion-list over 50 prompts) — and is named rather than dropped.

**⛔⛔ The blind baseline this arc has been using is a near-best draw.** `POOL[0:k]` is one arbitrary
subset; the cell is the distribution over k-subsets of 16, enumerated **exactly at every k** (120 ·
1,820 · 12,870 · 1,820). The first-k sits at percentile **95.8** (k=2), **96.0** (k=4), 69.2 (k=8),
50.9 (k=12) — stronger than a typical subset by **+0.0166** and **+0.0119** at small k. **The
correction makes prior gaps LARGER**, which is why it is stated rather than banked. At k=12, where
R810 drew its headline, no correction is needed.

**Controls.** OBJECT R810's k=12 cells reproduced (**0.552830 · 0.515424 · 0.548235**) · PLACEBO the
pool's first-k against itself, `0.0e+00` at all four k · POSITIVE D1 the rule effect shrinks toward
its forced zero · g=0 at k=2 it must not be zero, and is not · NEGATIVE every arm against another
prompt's humans, null **−0.0004 [−0.0067, +0.0061]** vs a real **+0.0419** · NOISE FLOOR three
committed seeds, sd **0.0033 · 0.0055 · 0.0040 · 0.0037**. **BH 10 of 12 survive**; the two
non-survivors are the E4 cells at k=2 and k=12 reported as holding zero.

## R812 · the baseline was a 96th-percentile draw and it changed nothing — all 1,820 swept

**Why here.** R811 measured `POOL[0:4]` at the **96.0th percentile** of C(16,4)=1,820. CHECK #414
established which rounds carry it: **R806, R807, R808 and R809 each subtract
`yvec(POOL[p], [0,1,2,3])`**. Four consecutive rounds on one near-best draw, and the baseline was a
defensible-choice axis never swept — realstat G4. ⚠ R811's NEXT proposed the subset MEAN, which is
one cell for another; the estimand is the curve.

**⭐ Every verdict holds at 1,820 of 1,820**: every fitted arm above every honest arm (100.0%) · no
arm reaching the pure-copy ceiling of 1.000 (100.0%) · R809's log contrast negative (100.0%).

**D3, written before the run, is why.** The baseline is subtracted from **both** sides of the slope
and partially cancels. Committed vs family: `oracle_k4_fit1` **0.6497** vs mean **0.6740**, sd
0.0229, range [0.5912, 0.7328], percentile **15.6** · `greedy_k4_fit1` 0.6115 / 0.6379 / [0.5547,
0.7023] / 14.9 · `indep_k4_fit1` 0.5035 / 0.5356 / [0.4388, 0.6100] / 18.2 · `coval_core` 0.3489 /
0.3917 / [0.2717, 0.4991] / 18.0 · `topw_k4` 0.3379 / 0.3640 / [0.2715, 0.4626] / 25.2.
⭐ **No committed value is in a tail** — so *extreme for the pool's own A2* is **not** *extreme for
the derived slope*: 96.0 vs ~18, because a slope depends on the baseline's per-prompt covariance and
not its level.

**⚠ The point estimates do move, conservatively.** The committed baseline sits below the family mean
for every arm, so R807's scale understated leak-likeness: at a typical baseline the fitted arms read
**0.54–0.67** rather than 0.50–0.65, and across the family **0.44–0.73**.

**⭐ And the baseline is second-order against sampling**: the prompt bootstrap's sd is **0.0496**
against the whole family's **0.0229** — reported side by side and never pooled.

**E2**: R809's contrast, committed **−0.1317** (reproduced), family mean −0.1256, sd 0.0347, range
[−0.2428, −0.0374], committed at the **43.1st** percentile, **negative at 100%** of baselines.

**Controls.** OBJECT R807's λ **0.459704** and all five values · OBJECT (E2) R809's **−0.131725**
reproduced **after repair** · PLACEBO an arm minus itself, **0.0e+00** · POSITIVE `_perfect_leak` on
itself **0.0e+00** deviation from 1.000 across all 1,820 · g=0 the honest arms sit **0.501** from the
ceiling · NEGATIVE the permuted baseline's range **[0.782, 0.900]** is **disjoint** from the real
family's **[0.591, 0.733]** · **0 of 1,820** degenerate λ.

## R813 · the intervals are 14–30% too narrow, and nothing breaks

**Why here.** R812 proposed a prompt-level cluster bootstrap. CHECK #415 killed it twice: every
round already bootstraps prompts, and the release carries **1,078 conversations for 1,078 prompts,
max 1 each, 0 spanning more than one** — there is no coarser grouping. ⭐ But the same check found
the real dependence: **1,012 annotators, each judging a median of 19 prompts** (on parity-0, **964
annotators at a median of 8**), crossed with prompts, with every committed interval holding that
panel fixed.

**⭐ The design effect, per headline.** H1 (R805, +0.0553): prompt [+0.0456, +0.0653] → crossed
**[+0.0435, +0.0666]**, DE **1.17**. H2 (R810, +0.0116): [+0.0069, +0.0164] → **[+0.0054, +0.0178]**,
DE **1.30**. H3 (R811 rule, +0.0419): [+0.0356, +0.0482] → **[+0.0346, +0.0493]**, DE **1.17**.
H4 (R811 source, +0.0373): [+0.0272, +0.0483] → **[+0.0249, +0.0489]**, DE **1.14**. **All four
remain resolved**, including H2, the arc's smallest surviving effect, whose half-width goes 0.0047 →
0.0062.

**⭐ And two controls read together explain why the effect is small.** The annotator scheme responds
monotonically to a planted annotator offset — width **0.0096 → 0.0120 → 0.0228** at g = 0 / 0.05 /
0.15 — while the prompt scheme stays flat (ratio 1.01), so the instrument *can* see annotator
dependence. ⚠ But destroying the crossing entirely (ids reassigned at random) gives **0.0097 ±
0.0007** against the real **0.0099** — a **weak pass**, separating by 0.0002 inside an sd of 0.0007.
**The data carries almost no annotator-level shared error**, so the design effect comes mostly from
resampling a second axis at all.

**Controls.** OBJECT all four points reproduced (**+0.0553 · +0.0116 · +0.0419 · +0.0373**) after two
repairs · PLACEBO an arm minus itself, **0.0e+00** over 200 crossed draws · POSITIVE monotone in
dose and null at g=0 · NEGATIVE ⚠ weak · D1 the crossed interval is never narrower than the prompt
one · DROPPED **2.6 / 968 (0.3%)** per draw · NOISE FLOOR crossed width sd **0.0004** (H1), **0.0009**
(H2).

## R814 · the annotator main effect is 9.42%, and clause ③ can be written against that number

**Why here.** R813's NEXT called it a **tension** that annotators agree pairwise only 0.551880 of the
time while their errors look independent. ⛔ CHECK #416 killed the framing with a three-line gauge
test on **zero real data**: at planted `rater_sd` = 0.00 / 0.15 / 0.35 the pairwise agreement is
**0.6230 / 0.6244 / 0.6223** — flat — while the rater ICC goes **0.0002 / 0.1751 / 0.3803**. The two
quantities are **independent**; there was never a tension. That is §4's *"the closing sentence is a
claim and never gets a control"*, committed one round after this project filed a ledger entry about
that exact mode.

**⭐ The measurement, against a label-permutation null.** Observed variance of annotator means
**0.004298** against a null of **0.001753 [0.001608, 0.001901]**, excess **+0.002545** on a total of
**0.027007** → **rater share 9.42% weighted**, **10.23% unweighted**, both above the null band.
⚠ **The verdict straddles the pre-registered 10% boundary** — weighted gives WORLD C, unweighted
WORLD B — and **D3 pre-registered reporting both** because weighting is a defensible-choice axis. The
honest statement is **~9–10%**, not a side of a line. Noise floor over 20 annotator half-splits:
**9.71% ± 0.79%**, so the estimate is stable and the threshold was the fragile part.

**⭐ The dose ladder, on the observed AND a rater-nulled table**: observed 9.43 / 10.41 / 15.59 /
29.95 / 56.73% at g = 0 / 0.02 / 0.05 / 0.10 / 0.20; **rater-nulled 0.00 / 0.50 / 6.16 / 22.10 /
52.09%**, firing only from g = 0.05. Monotone on both. ⛔ **My first g=0 check required the OBSERVED
table not to fire — which presumes the real data has no rater effect, the very thing under test.**
§4's "the control presupposes a non-null effect", inverted. A true zero exists only where the rater
structure has been destroyed.

**E4 · what clause ③ buys**: an annotator holdout can remove **at most 9.42%** of this table's
variance; the remaining **90.58%** is prompt plus interaction. ⚠ D4: on a crossed design the residual
absorbs the interaction and the release ships one judgement per (annotator, prompt) pair, so this
bounds the **additive** effect and does not show annotators are interchangeable.

**Controls.** OBJECT `CEIL_H` recomputed from this round's own table, **0.551880** exactly · PLACEBO
**0.0e+00** · POSITIVE monotone on both ladders · g=0 **PASS after repair** · NEGATIVE the null has
spread (sd **0.000075**) · population **968 / 968, 0 dropped**.

## R815 · a second human construct was on disk all along, and the ordering is identical under it

**Why here.** R814 closed by calling the next step a writing decision, on the ground that the release
ships one judgement per (annotator, prompt) pair. ⛔ CHECK #417 found **111 repeated pairs** — and,
behind that, **`ranking_blocks` carries three keys**: `world` (18,384 rankings), `personal` (4,901),
`unacceptable` (4,901). **This arc has scored A2 against `world` alone for its entire length.** Where
the same annotator answered both on the same prompt, the rankings **differ in 2,374 of 4,901 cases —
48.4%**.

**⭐ Asked the other question, the arms come out in exactly the same order.** Spearman **1.0000**,
Kendall τ **1.0000**, **36/36** concordant pairs, on 293 prompts carrying both blocks with ≥2
annotators each. Order under both: `oracle_k4_fit1` > `greedy_k4_fit1` > `indep_k4_fit1` > `topw_k4`
> `coval_core` > `genericpool16` > `random_k4_s0` > `full` > `gen_sham`.

**⭐ The shift is uniform and small**: every arm scores **higher** on `personal`, by 0.005–0.012 —
`coval_core` **0.5587 → 0.5707**, `oracle_k4_fit1` **0.5880 → 0.5939**, `gen_sham` **0.4766 →
0.4871**. A level shift in the target, not a reordering, which is why the ordering survives.
**BH: 7 of 9 differences survive.**

**E4 · the committed margins hold their sign**: R805 fitted − blind pool **+0.0549 → +0.0514**;
released core − blind pool **+0.0256 → +0.0282**; R811's rule effect **+0.0717 → +0.0711**; the sham
gap **+0.0822 → +0.0836**. **0 of 4 flip.** MDE at n=293 is **0.0173**, below the smallest margin
tested (**0.0256**), and it was computed before any null was read.

**Controls.** OBJECT `coval_core` on `world` over 968 = **0.5664774812** exactly · PLACEBO
**0.0e+00** · POSITIVE an arm built from `personal`'s modal class scores **0.6555** there, above the
best real arm's **0.5939** · g=0 the same construction from `world` scores **0.6366** on `personal`,
lower · NEGATIVE block labels shuffled within each assessment, null **+0.0002 [−0.0056, +0.0053]**
against a real **−0.0119** · NOISE FLOOR **0.0032**. ⚠ The `unacceptable` block cannot be a third
target: it records ratings, not a ranking, so `cls()` cannot consume it — checked against the record.

## R816 · the shift toward `personal` is the TIE RATE, not the target's reliability

**Why here.** R815 found nine arms scoring 0.005–0.012 higher against `personal` and its NEXT
proposed one explanation: the target is more reliable. ⛔ CHECK #418 found that inference's
**direction is nearly forced** — higher inter-annotator agreement raises A2 for any predictor — so
only the magnitude is evidence, and the test must be **slope = 1**, not slope > 0. It also found the
rival R815 never named: **[DERIVATION] a strict-signed arm can never match a tied human pair**, so
its attainable A2 is bounded by `1 − tie_rate`, and the tie rate is **world 0.145080 vs personal
0.124460**, a drop of **0.020620** — more than the whole shift, available on its own. Panel depth is
**median 12 in both blocks**, so that rival is out by measurement.

**⭐ The result.** Mean **ceiling slope +0.313**, with the CI containing 1 in **0 of 9 arms** — the
reliability account as posed is refuted. Mean **tie slope −0.476**, with the CI excluding 0 in **9 of
9**. ⚠ Both mechanisms are live: every ceiling slope is resolvedly positive (**+0.123 to +0.441**).
What died is that reliability *accounts for* the shift. **WORLD B.**

**The joint model is admissible** — `corr(ceiling, tie) = −0.4314`, below the pre-registered 0.7.
Jointly, `coval_core` ceiling **+0.269 [+0.162, +0.351]** / tie **−0.367 [−0.493, −0.244]**; and on
`gen_sham` the ceiling term **vanishes** at **−0.031 [−0.158, +0.089]** while the tie term holds at
**−0.572 [−0.744, −0.379]**.

**Controls.** OBJECT R815's shifts reproduced exactly (`coval_core` **−0.011944**, `gen_sham`
**−0.010529**) · PLACEBO **0.0e+00** · POSITIVE planted c = 0/0.5/1.0/2.0 recovered as
**+0.000/+0.500/+1.000/+2.000** · NEGATIVE the regressor-to-outcome pairing destroyed, ceiling null
**+0.004 [−0.091, +0.086]** vs real **+0.368**, tie null **−0.004 [−0.141, +0.156]** vs real
**−0.553** · NOISE FLOOR **0.044**. ⚠ D3's strictness ordering has the right sign (**+0.4899**) on a
regressor spanning only **0.994–1.000**, and is reported as weak. ⚠ The pre-registered per-arm
RESIDUAL family is **forced** — an OLS residual has mean 0 by construction — and is labelled rather
than reported as a finding.

## R817 · removing the tie handicap changes nothing — six normalisations, one ordering

**Why here.** R816 showed A2 penalises strict arms on tied human pairs, and its NEXT proposed
dividing by each prompt's attainable maximum. ⛔ CHECK #419 found this arc burned by that operation
twice: **R793 swept three ceiling normalisations and got WORLD A / B / A**, flagging a "fraction of
ceiling" of **1.0264** as proof the quantity was not a proportion; and **R807's g=0 control** caught a
denominator estimated from the numerator's own data. Measured here, `corr(A2, att)` is **+0.6138**
with shared annotators against **+0.3798** with disjoint halves — **+0.2340 is shared annotator
noise**, so only the SPLIT-HALF normalisation is identified.

**⭐ Six normalisations, zero reorderings.** raw · ÷att(shared) · ÷att(split-half) · ÷(1−tie) ·
subtractive · ÷√att — every one gives **Spearman +1.0000** against raw and **0 of 4** committed
margins flipping sign; the shared and split-half orderings agree at **+1.0000** with each other.
⭐ R793's pathology does not recur, and the reason is measurable: R793 divided by a pooled `CEIL_H`
= 0.5519, **below** the arms' scores; per-prompt `att` has mean **0.686265**, above every arm, and
**no normalisation produced a value above 1**.

**⭐ The number the arc could not previously state**: on the identified normalisation `coval_core`
reads **0.8132** of its prompts' attainable maximum, `oracle_k4_fit1` **0.8780**, `topw_k4` 0.8059,
`genericpool16` 0.7764, `gen_sham` **0.6925**.

**Controls.** OBJECT mean per-prompt attainable max **0.686265** matching R804, plus `coval_core`
**0.5664774812** · PLACEBO a constant divisor leaves the ordering at **1.000000000000** · POSITIVE a
dose ladder holding the raw mean fixed at 0.5664774812 while the normalised mean moves **0.822608 →
0.820424 → 0.816057**, matching its **derived** slope `1 − mean(att)·mean(1/att) = −0.02183537` to
**1.46e-16** · NOISE FLOOR **0.0046**. ⚠ The NEGATIVE control is **uninformative here and is not
upgraded**: because every normalisation leaves the ordering at 1.0000, permuting `att` also leaves it
at 1.0000, so it cannot separate "the normalisation does nothing" from "the permutation destroyed
it". The load-bearing control is the positive one, which predicts its own slope.

## R818 · a fixed ordering already reaches 65% of the ceiling, and the released core captures half of what is left

**Why here.** R817's NEXT asked what an arm with no per-prompt information would score. ⛔ CHECK #420
found **R804 already computed it** — `R804/run.py:197` gives the best constant weak order and prints
it **inside a negative control's parenthetical**, unused for fourteen rounds.

**⛔ And the object check caught a unit inconsistency in that same line.** R804's `BESTC` pools all
annotator rows across all prompts — **annotator-weighted**, **0.451773** (reproduced exactly here) —
while its `CEIL_ATT` is **prompt-weighted**, 0.686265. Every A2 in this arc is prompt-weighted, and
on that scale the floor is **0.449421**, a difference of **−0.002352**. Held out over 20 prompt
half-splits: **0.446628 ± 0.006628**, optimism **0.002792**.

**⭐ So the scale runs from 0.6508 to 1, not from 0 to 1.** Share of the INFORMATIVE range:
`oracle_k4_fit1` **+0.6991 [+0.6715, +0.7255]** · `greedy_k4_fit1` +0.6844 · `indep_k4_fit1` +0.6152
· **`coval_core` +0.5001 [+0.4631, +0.5331]** · `topw_k4` +0.4905 · `genericpool16` +0.3990 · `full`
+0.2591 · `random_k4_s0` +0.1922 · `gen_sham` **+0.1509 [+0.1071, +0.1950]**. **`coval_core` reads
0.8255 of attainable and 0.5001 of what is informative.** The ÷attainable column reads
`oracle_k4_fit1` **0.8949** · `genericpool16` **0.7901** · `gen_sham` **0.7035**, and
`genericpool16`'s informative share carries **[+0.3596, +0.4338]**.

**⚠⚠ D1, stated before the run**: the corpus-level rescaling is **affine** and cannot reorder — a
DERIVATION, not a measurement. Only E3 can come out otherwise, and it does: per-prompt, Spearman
**+0.9833** with one swap at the bottom, and **four arms fall BELOW the constant floor**
(`genericpool16` −0.1118, `full` −0.4221, `gen_sham` −0.5398, `random_k4_s0` −0.5938). ⚠ 48 of 968
prompts (5.0%) are excluded there because `att_p = floor_p`.

**Controls.** OBJECT R804's **0.451773** reproduced exactly once the weighting was separated ·
PLACEBO the constant arm's own share **0.0e+00** · POSITIVE a synthetic arm at f = 0/0.25/0.5/1.0
recovers **0.000000/0.250000/0.500000/1.000000**, max |Δ| **2.2e-16** · NEGATIVE a **synthetic world
with no aggregate human tendency**, floor refitted and prompt-weighted: **0.416423 [0.414047,
0.419088]**, max **0.420731**, entirely below the real **0.449421** · NOISE FLOOR **0.006628**.

## R819 · R818's per-prompt statistic was one estimator with 6× the noise — its reordering is retracted

**Why here.** R818 returned WORLD C on a reordering (Spearman **+0.9833**) and reported four arms
falling below the constant floor. ⛔ CHECK #421 killed its NEXT on arithmetic first: **[D2] if
`margin_p = c·span_p` exactly, every estimator returns c**, so proportionality produces AGREEMENT,
not the divergence observed — the NEXT asked a question whose affirmative answer explains the
opposite of what was seen.

**The cause is the denominator.** Span mean **0.2368**, median 0.2131, with **12.8% of prompts below
0.05** and 24.5% below 0.10; the ratio runs to **−29.00**; the smallest-span decile averages
**−3.105** against the other nine at **+0.414** and **contributes −503.1% of the total sum**.

**⭐ Across the estimator family**, Spearman against the corpus-level ordering is **+1.0000** for
trim5, trim10, trim20, median and weighted, and **+0.9833** for the naive mean and winsorised mean
alone. Arms below the floor: naive **4**, trim5 2, trim10 1, trim20 **0**, median **0**, winsor 3,
weighted **0**. Half-split sd: naive **0.0693** against weighted **0.0110** — **6.3×**.
⭐ **D1 holds exactly**: `weighted` = `Σmargin/Σspan` **is** the corpus-level ratio, max |difference|
**6.66e-16** — so the corpus number was always the minimum-variance member of this family.

**⚠ WORLD C, not A.** The ordering agrees under every trimmed member, but `trim10`'s `coval_core` of
**0.4136** lies **outside** the corpus-level bootstrap CI **[0.4827, 0.5499]**. Retracted: R818's
reordering and its four-arms-below-the-floor count. Not established: that the two shares are the same
number — a trimmed mean is a different estimand, not a better estimate of the same one.

**Controls.** OBJECT R818's **+0.0617** and **−0.5938** reproduced exactly · PLACEBO the constant arm
returns **0.0e+00** under every member · POSITIVE a plant at f = 0/0.25/0.5 recovers f exactly, and
the repaired separating dose targets SPREAD: at eps=0.05 naive **±0.0348** vs weighted **±0.0073**,
both exactly 0 at eps=0 · NEGATIVE ⛔ the first version targeted `weighted`, which is
**permutation-invariant by construction**, and returned a point mass — the **fifth degenerate null of
this session**; repaired to the six movable members, each real value outside its own null.

## R820 · the null-degeneracy detector — validated on ten labelled cases, and installed

**Why here.** R819 counted five degenerate negative controls this session and proposed a gate. ⛔
CHECK #422 found the architectural problem: **the committed artifacts do not contain the degenerate
nulls** — each was repaired before anything was written — so a commit-time gate like the existing
seven is structurally blind to this class. Only 9 recent rounds record a null field at all, under six
inconsistent names. The detector therefore had to be a **runtime assertion**, not a gate.

**⭐ Validated on ten labelled cases** — the five broken nulls and their five repaired counterparts,
transcribed from `RETRACTIONS.md` and `R819/README.md`. **R1 (zero spread) fires on 4 of 5 BROKEN and
0 of 5 REPAIRED**; **R2 (overshoot) fires on 2 of 5 broken and 2 of 5 REPAIRED** and is **unusable** —
exactly as D1 predicted before the run, because R816's bad null and R819's good one both have
|null| > |observation| with the same sign. Threshold sweep: R1 separates from 0 through **1e-3** and
breaks at 1e-2; the installed default is **1e-9**.

**⛔ The transcription check fired on 6 of 10 and was right** — my table used ASCII hyphens where the
files use the Unicode minus U+2212, and cited the wrong file for two values. **⛔ And I manufactured
the signature on R816**, encoding its reported centre **−0.870** as a zero-width interval when its
real null was **[−1.283, −0.416]** over 200 draws; that inflated R1 to 5/5 until corrected back to
the **4/5** R819 predicted.

**Installed**: `assurance/null_is_informative.py`, raising on an all-zero null, on a point mass at
the observation, and on fewer than two draws; silent on a null with genuine spread. Its message names
the diagnosis — *the permutation is a no-op on this statistic; check whether the statistic is
invariant to it by construction* — which is what four of those five rounds needed and none had.


## R821 · which definition is the deliverable

**The deliverable is the head: ② ∧ ③ ∧ ④, size > 1.** The `② ∧ ③` retirement at the R470 line is
overturned above; the contradiction that stood for 80 rounds is closed by evidence rather than by
choosing the newer sentence.

⛔ **SCOPE ADDED 2026-08-06 (entry 1322): the sentence below is DOWNGRADED 88 LINES FURTHER DOWN, in
this same file** — *"THIS DOWNGRADES R821. ④ is 'free-but-real' **under the strict reading only**.
Under the adopted reading it is a **BINDING** clause."* This paragraph sits under the heading **"The
deliverable is the head"**, so it is the sentence a reader of the deliverable meets, and it is the one
that is stale. **Read it as: free-but-real UNDER THE STRICT READING; BINDING (25 of 58) under the
permissive reading the statement adopts.**

**Clause ④ is free-but-real.** Excludes **0 of 58** arms at home (1 UNVERIFIED: `full_sham`, margin
+0.0047 [−0.0080, +0.0178] against R803's judge-free floor **0.4557**). Removes planted below-floor
arms at δ = 0.10 (A2 0.3549), δ = 0.05 (0.4058) and δ = 0.01 (0.4450), and correctly does **not**
remove the arm planted at δ = 0. Half-split noise floor **0.0067**, so the δ = 0.01 detection is
inside the design's resolution.

⛔ **A DERIVATION, not evidence (§0's arithmetic trap).** ④'s statistic is a difference of corpus
means, hence **permutation-invariant by algebra** — checked over 20 permutations, max |Δ| = 0.000e+00.
**A permutation null is structurally unavailable for clause ④.** Two degenerate nulls were built in
this one round before that was derived; both were caught by `assurance/null_is_informative.py` on its
first live use, one round after being installed. The admissible negative control resamples the arm
from the floor's own per-prompt distribution: **−0.00001 ± 0.00525** against a real margin of
**+0.08188**.


## R822 · the clause counts under the estimand nobody chose

**The grid**: weighting {prompt, annotator, subgroup} × resampling {prompt, annotator}, 6 cells,
968 prompts · 1,012 annotators · 15,593 judgements · 33 subgroups at n≥200 · 58 arms.

⭐ **ALL CLAUSE COUNTS IN THIS FILE ARE PROMPT-WEIGHTED. That default was never chosen, and for two
of the three clauses it does not matter.**

| clause | over the 6 cells | |
|---|---|---|
| **④** | **0 of 58 in all six** | invariant — R821's retention does not rest on the default |
| **③** | **23 of 58 in all six** | invariant, and **necessarily so**: ③ reads the arm's SOURCE, not its score. Its invariance is this grid's free falsifier and it passed. |
| **②** | **29 / 30 / 31** | **MOVES.** Two arms flip: `gen` (outside the noise floor) and `topw_k12` (inside it, sign unresolved). |

**So ② — the clause the table at L128 records as carrying the whole boundary among label-free arms —
is the one whose boundary is estimand-dependent.** Any future ② count must state its weighting.

⛔ **A DERIVATION, not evidence.** Resampling cannot move a point estimate, only its CI, so the 6
cells carry **3** distinct quantities; a verdict change at fixed weighting is precision, never
estimand. The three weightings are nonetheless genuinely distinct (max |Δmargin| 0.0086 / 0.0053 /
0.0076, pairwise corr ≥ 0.99904), so the grid is not a reparameterisation.

⭐ **AND THE SUBGROUP COLUMN IS NEARLY FREE.** The sham — subgroup weighting over **random groups of
matched size** — reproduces the real demographic subgroups at **corr 0.99988**, and correlates with
plain prompt weighting at **0.99938**. The ingredient is not *which* groups; it is barely that
grouping happens. **Any future proposal for a demographically-weighted estimand should be shown this
number before it is built.**


## R823 · the floor was a fifth of its own published family, and it cost nothing

**④'s scope widens from a 6-rule class to the full 30-rule family this file names**, with no change
to any number. `max_len_chars` **0.455679** is the family argmax on the 968-prompt population; the
6→30 rise is **+0.000000**; ④ excludes **0 of 58** at both, with `full_sham` UNVERIFIED at +0.0047
[−0.0079, +0.0185].

⛔ **A DERIVATION, not evidence:** max over a superset is monotone non-decreasing, so "the floor
rises" is forced and is not a finding. What is measurable is its size, whether it crosses an arm, and
how much is winner's curse — which is what the sham prices at **+0.003412**.

**The zero is a measurement rather than silence only because of that sham**, and the sham had to be
rebuilt: its first version sorted 30 random scorers and took the top six, making `sham6 == sham30`
by construction — a control that could not fail, inside the round whose subject is selection.


## R824 · ④'s class is not closed under fitting, and the text never said which

**④'s extension is 0 or 25 of 58 depending on a reading of its own sentence.** *"Every rule
computable from the response set alone"* constrains what a rule CONSUMES AT INFERENCE and is silent
about what its CONSTRUCTION consumed.

| reading | ④'s bar | ④ excludes |
|---|---|---|
| **STRICT** — no parameters fit on human data | **0.455679** (`max_len_chars`, R823) | **0 of 58** |
| **PERMISSIVE** — fit on other prompts allowed | **0.519689 ± 0.005438** | **25 of 58** |

**The deliverable adopts the PERMISSIVE reading**, recorded in the head clause above. Grounds, not
taste: the 25 it removes are exactly the arms that read nothing (`random_k*`, `topvar`, `topabs`,
`topwvar`) or are shams (`full_sham`, `gen_sham`, `topw_k4_sham`, `coval_core_sham`), while **every
③-admissible load-bearing arm survives** — `coval_core` +0.0468, `topw_k4` +0.0445, `generic`
+0.0317, `genericpool16` +0.0225.

⛔⛔ **THAT GROUNDS STATEMENT IS RETRACTED (R825). `coval_core` DOES NOT SURVIVE.** The survival was
measured on **14 lexical features**. Adding **character n-grams** — a response-only family never in
the 30-rule class this file names at L118 — raises the leak-free held-out bar to **0.572335**, and
paired against `coval_core` on the same evaluation halves the difference is **+0.006197 [+0.003923,
+0.008471], 12 of 12 splits positive**, sign-test p = 0.00049. **Under the permissive reading, ④
excludes the released core.** Character n-grams alone buy **+0.0487 = 104% of the whole gap**.
⚠ The per-split effect ranges +0.000945 to +0.011824, a 12.5× spread: the claim is about the MEAN
over evaluation halves, never about a given half. **R824's finding that ④'s extension depends on the
reading stands; the REASON given for choosing the permissive one does not.** ③'s own wording already uses the fit-on-other-prompts distinction,
so the permissive reading is the one consistent with the rest of the definition.

⚠ **THIS DOWNGRADES R821.** ④ is *"free-but-real"* **under the strict reading only**. Under the
adopted reading it is a **BINDING** clause. R823's confirmation is scoped the same way — it widened
the **strict** class from 6 rules to 30.

⭐ **`gen` clears ④'s permissive bar by +0.0005 at its lower bound** (+0.0155 [+0.0005, +0.0304]).
R822 found `gen`'s ② verdict straddling its threshold across weightings; **the arm the ②∧③ question
rests on is now marginal under two independent clauses.**

**Specification curve**: 19 of 21 cells clear the strict bar. Only `length_only|logistic_C0.01`
(0.454833) and `length_only|gboost` (0.426911) fall below. **The non-length features alone reach
0.5063**, beating the strict bar by more than 10× its noise floor.

⛔ **A DERIVATION, not evidence:** a fitted combination cannot score below its best single feature
IN SAMPLE, so an in-sample rise is forced. Every number above is HELD OUT — fit on half the prompts,
scored on the other half, 20 splits.

**The sham is what makes the rise attributable**: the identical learner on 14 RANDOM features reaches
**0.429425 ± 0.004633**, so held-out fitting on noise buys **+0.000684** over chance and the learned
bar sits **+0.090263 above it**.


## R825 · the permissive bar reaches the released core

**Clause ④, under the permissive reading adopted in R824, excludes `coval_core`.** ⚠⚠ **SCOPED BY R826: THAT HOLDS AT
ONE POINT ON A PLATEAU THAT STRADDLES THE CORE.** Sweeping modelling effort k = 0…200 SVD components,
the held-out bar **saturates** at **0.571263** (last rise −0.001823 against a noise floor of
0.007376) — and across the five saturated cells k ≥ 40 it **excludes the core in 2, is
indistinguishable in 3, and admits it in 0**. R825's k = 100 reproduces here at 0.572551 and its
exclusion is real *at k = 100*; it does not generalise across the plateau. A response-only
predictor over character n-grams — every unsupervised stage (vectoriser, SVD basis, SVD z-score,
lexical z-score) fit on the fit half — reaches a held-out bar of **0.572335** against the core's
**0.566477**. Paired on the same evaluation halves over 12 splits: **+0.006197 [+0.003923,
+0.008471]**, **12 of 12** positive, sign-test **p = 0.00049**.

⛔ **A DERIVATION, not evidence:** `mean(bar) − mean(core) ≡ mean(bar − core)` by linearity, checked
at **1.21e-16**. Pairing cannot move the point estimate; it moves the standard error from 0.002353 to
**0.001033**, a 2.3× shrink, because `corr(bar, core) = +0.8377`.

⚠ **AND A UNITS CORRECTION THAT MATTERS MORE THAN THE PAIRING.** The first comparison called this
difference *"inside the floor"* — it compared a **mean over 10 splits** against a **per-split noise
floor**. A floor is a single draw's dispersion; a mean's standard error is `sd/√n`, ~3× smaller.
**That is a √n units mismatch, and it fails toward "no effect", which is why it reads as caution and
passes unexamined.** Both the paired and unpaired intervals exclude zero at n = 12.


## R826 · the response-only bar saturates, and it saturates ON the released core

**The effort curve settles.** Held out, over k = 0, 5, 10, 20, 40, 60, 100, 150, 200 SVD components
of character 3–5-grams, the bar runs 0.524670 → 0.528836 → **0.558620** → 0.564312 → 0.570737 →
0.570526 → 0.572551 → 0.572162 → 0.570339. **Most of the gain arrives by k = 10.** The last rise is
**−0.001823** against a noise floor of **0.007376**, so it is saturated — and it *falls* at k = 150
and 200, which is R823's held-out-bar-falls result appearing again.

⭐ **The plateau sits ON `coval_core`.** Bar **0.571263** against **0.566477**, mean paired
**+0.003836**, and of the five saturated cells **2 exclude · 3 indistinguishable · 0 admit**.
**At the modelling limit, ④'s bar and the released core are the same number to within this design's
resolution**, so ④'s verdict on the object the definition was written to describe depends on where in
the plateau one samples.

⛔ **A DERIVATION, not evidence (D2, written before the run):** a crossing between k = 0 (admits) and
k = 100 (excludes) exists **by construction** given those endpoints. Finding one is not a finding —
only its location, its sharpness and the saturation are measurable.

⭐ **The sham is what makes the rise attributable.** Run at *every* k on random features of matched
dimension, it **declines** 0.524670 → 0.493813, so the excess grows monotonically to **+0.076527**.
**Capacity alone makes the held-out bar worse**; every point of the rise is the features.

⚠ **The pre-registered verdict is UNVERIFIED, and it is not being rewritten.** Three worlds were
registered — saturates above, below, or not at all. **The observed outcome was a fourth: saturates
ON the core.** The kill read the k = 200 endpoint, matched nothing, and refused. A kill that refuses
because the outcome was not in the world list is the kill working.

## R827 · a per-prompt correlation is forced by item difficulty, and the round that would have used one produced no verdict

R826 left the response-only bar saturating **on** `coval_core`. Asking whether that is *structural*
requires comparing the two arms' per-prompt profiles — and **a raw correlation between any two arms
is forced.** Every arm scores accuracy against the same human labels on the same items, so pairs
sharing no mechanism still correlate: `random_k4_s0` × `oracle_k4` = **+0.5132**.

**The round therefore used a PARTIAL correlation**, residualising both on a difficulty index built
from arms excluding both members of every pair. It returned **+0.1278 [+0.0605, +0.1935]**, at the
**75.4th** percentile of a 1,596-pair null spanning **−0.3053** to **+0.5588**.

⛔ **That number is NOT admitted.** The round's positive control required pairs known to share
mechanism to clear the null. `topw_k4` × `topw_k6` did — **+0.5739**, criterion-text overlap
**0.6696**. `random_k4_s0` × `random_k4_s1` did not — **+0.0905**, overlap **0.1931**, essentially
the cross-family rate of **0.1868**. **Two seeds share a procedure and not content; that pair belongs
in the null and was written into the control.** The gate required all positive pairs to pass, so the
verdict is **UNVERIFIED and it stands** — respecifying the control after seeing it fail would bend
the kill to the answer.

**What this fixes in the record regardless:** any future comparison of per-prompt profiles must
residualise, and must build its difficulty index from arms **excluding both** members of the pair, or
it is measuring difficulty and calling it structure.


## CLOSURE · two artifacts committed 2026-08-03 and never read, folded in — the core is NOT a response-only rule

R826 left the response-only bar saturating **on** `coval_core` and named the mechanism question. **Two
artifacts already answer it**, both committed 2026-08-03, both on R793's list of seven never opened by
any of this arc's 468 `run.py` files. This is **CLOSURE**, not a new measurement: nothing was run.

### `corebench/is_importance_recoverable.py` → `importance_recoverable.json` *(`1cbde4ca62843f46`)*

The core selects rubric items by **mean human importance**. Is that quantity predictable from features
computable **without any human importance data** — satisfaction on the four responses, criterion text
length, position in the rubric, the prompt's criterion count?

| arm | 5 prompt splits |
|---|---|
| **deployable held-out R²** | 0.046610 · 0.053298 · **0.055375** · 0.044030 · **0.055475** |
| Pearson r | 0.211657 – **0.236674** |
| **POSITIVE, leaky** (adds importance sd) | 0.045511 – **0.059883** |
| **NEGATIVE, target shuffled** | −0.007808 – **+0.001432** |
| PLACEBO, importance from importance | R² exactly 1 |

**WORLD A — partially recoverable, held-out R² ≤ 0.0555.**

⚠ **THAT VERDICT STRING IS NOT GATED BY ITS OWN CONTROLS, so it is quoted here only after the
controls were re-verified from the artifact.** The module computes `ok_pos`, `ok_neg`, `ok_pla`,
prints all three PASS/FAIL, and then decides with `v = "WORLD B" if d.max() <= 0.02 else "WORLD A"`
— **the ternary tests `d.max()` alone.** A run with all three controls failing would still print
WORLD A. Re-checked from `importance_recoverable.json`:
**`ok_pos` mean(leaky) 0.054111 > mean(deployable) 0.050958 → TRUE** ·
**`ok_neg` |mean(shuffled)| 0.003154 < 0.02 → TRUE** ·
⛔ **`ok_pla` UNVERIFIABLE — the PLACEBO(y~y) value is NOT PERSISTED in the artifact**, so its
run-time PASS print is the only record of it. Unverifiable, not failed.
⚠ And the positive control's band is thin: leaky exceeds deployable by 0.001481–0.004408 across the
five splits, **6.2% above the arm it is meant to bound**.

⚠ **The positive control's band is narrow and must be stated, not glossed.** Leaky exceeds deployable
by only **+0.0015 to +0.0044** (5 of 5 splits, consistent in sign but tiny). Floor ≈ 0, ceiling ≈ 0.06,
deployable 0.0555 — **the deployable arm reaches ~92% of what the leaky arm reaches.** ⭐ The binding
limit is therefore **not feature hygiene**: mean importance is only ~5% predictable *at all* from text
and satisfaction, and leaking the target's own dispersion barely moves it.

### `corebench/learned_core.py` → `learned.json` *(`9b027237d67d59e9`)*

A ridge fit over 8 deployable features → top-4 selection, evaluated on **held-out prompts**, against
unfitted `topw_k4`. Exact-class agreement, 3 splits:

| arm | splits |
|---|---|
| **LEAKY** (target-derived usefulness) | 0.241736 · 0.210744 · 0.206612 |
| `topw_k4`, unfitted | 0.117769 · 0.115702 · 0.117769 |
| **learned, deployable** | 0.107438 · 0.109504 · 0.101240 |
| shuffled coefficients | 0.053719 · 0.051653 · 0.095041 |
| PLACEBO, fit on test | 0.109504 · 0.092975 · 0.107438 |

**`d_learn_topw` = −0.011019 · −0.025482 · +0.002772** — the fitted deployable rule does **not** beat
the unfitted one, and is worse in 2 of 3 splits. **`d_leak_topw` = +0.102617 · +0.084711 · +0.120523**,
so the pipeline is validated: a leaky arm clears `topw_k4` by ~0.1 and the honest arm does not.

⭐ **WORLD B, in that round's own words: *"importance alone is the best deployable rule found, and the
benchmark's answer is that the trivial rule is the answer."***

### What this settles for R826's open question

**`coval_core` sits at the response-only ceiling, and it is not a response-only rule.** Deployable
features reconstruct **~5%** of the variance in the quantity driving its selection, and fitting on them
**loses** to a hand-built top-weight rule. The coincidence of level is not a coincidence of mechanism.

⚠ **Bound on this claim**: both artifacts admit **rubric-side** features (criterion text, position,
count), which is a *superset* of the response-only class clause ④ names. A response-only predictor is
nested inside them, so its ceiling is ≤ 0.0555 **by nesting, not by measurement** — a derivation, and
the reason no further round was run on this axis.

## `synthetic_world` · the round that licenses additivity does not follow its own registered kill

**STATUS: UNVERIFIED.** `corebench/synthetic_world.py` exists to check whether the set-structure
separator can detect set structure at all, and registers its kill in its own docstring: *"if the gap
at g=1.0 does not exceed the gap at g=0 by more than the g=0 spread across seeds, the separator is
BLIND and the additivity claim on real data is downgraded to UNVERIFIED."*

That test is `dose_ok`. It is computed, printed **FAIL**, and never enters a condition — the verdict
branches on `fires` alone. Artifact: `fires: True`, **`dose_ok: False`**, **`monotone: False`**,
`real_gap: 0.0079`; doses 0.0→1.0 give 0.5483 · 0.5708 · 0.5625 · 0.5800 · 0.5775, **not monotone**.

The additivity claim rests on two non-rejections (`oracle_HO − indep_HO = +0.0079 [−0.0079,
+0.0238]`) and this is the round meant to license them. ⚠ **Both branches are stated and neither is
adopted here**: `fires` is a real signal at a 10× threshold, and which test should govern is a
judgement made in code and contradicted in prose. **What is established is that the verdict does not
follow from the checks the round registered.** Nothing cites the artifact — measured,
filename-anchored: 1 reference, its own module.

Found by `assurance/kill_is_wired_into_the_branch.py`, which carries a positive control
(`synthetic_world` must fire) **and** a negative control (`pairwise_matrix` must not) and exits 2 if
either fails. ⚠ Its flag list is a name heuristic, so a clean report is silence about the names not
searched, never a clean bill.

---

## What the clause can distinguish here — the resolution, measured rather than bounded

Clause ④'s bar is a comparison, and a comparison is only as fine as the design that makes it. The
between-arm resolution of this site was **bounded** for two rounds and is now **measured**: the
per-prompt difference vector between two arms is a pure function of their committed selections and
the committed human rankings, so no judge call is needed to obtain it.

Over the **45** adjacent pairs of the ③-admissible ordering, exactly **1** separates at twice its own
paired MDE — `gen` above `random_k12_s0`, a gap of
**0.034722** against an MDE of **0.011805**, which is 2.9×. The positive control, `oracle_k4`
against `generic`, gives **0.075872** against **0.010615**; an arm scored twice through the same
path gives a standard deviation of exactly zero.

⛔ **So the ③-admissible ordering is not a ranking. It is two groups with one boundary** — the
substantive label-free arms above the random cluster — and every distinction inside either group is
below this design's resolution. **Clause ④ can therefore express at most a two-way split on this
site**, whatever bar it names.

⚠ **And the resolution is not uniform, which is why it had to be measured.** **27** of the 45 true
MDEs fall below **0.0104**, and the smallest is **0.000000** — two pairs of duplicate arms whose
difference vector is identically zero across every prompt. A single bound applied to the whole
ordering is wrong in both directions, not merely conservative. *(R835 · R836 · R837 · R838)*

⛔ **AND THIS IS NOT A CLAUSE, WHICH IS THE POINT.** The obvious next move — *"a core must be in the
upper group"* — was drafted and rejected here. Three reasons, in order of decisiveness:

1. **④'s extension is already correctly resolved and does not change.** R436 adjudicates each arm
   against the bar with `ZEFF · std(bootstrap of mean(arm − bar))` on the **per-prompt paired
   difference** — the right MDE for the comparison ④ actually makes. The two-group finding concerns
   the ordering **among ③-admissible arms**, which is a different comparison, so nothing in ④'s
   extension moves. Adding a resolution parameter to ④ on these grounds would be decoration.
2. **The boundary is a fact about the arm inventory, not about cores.** It sits between `gen` and
   `random_k12_s0` because those are the arms that were built. Add one arm between them and it
   moves. **A clause whose extension depends on which competitors happened to be constructed is not
   a definition** — it is a leaderboard position wearing a definition's clothes.
3. **It fails the exclusion test this document applies to every clause.** Asked to name an
   admissible object it excludes, the honest answer is *"whatever is currently below the boundary"*,
   which is not an object but a rank.

**So the measured resolution belongs here as a SCOPE on what ④ can express, and nowhere in the
conjunction.** *(R838; the rejection is a derivation, not a measurement.)*

---

## ⛔ R917 · EVERY RATE IN THIS ARC WAS COMPUTED OVER TWO JUDGES — corrected, and the findings hold

**R906's `RUBRIC_SELECTOR` population is 86 arms of which 37 (43%) are `_08b`/`_08bR` — rebuilds
scored by the 0.8B judge.** R908 reads that list; R911 reads R908. So every per-rule admitted share
published in this arc is a share over **two instruments**, which R895 established must never be
pooled. It was found by R917's wiring control, after I first mistook it for my own glob bug — and it
was my glob bug too, the same prefix-regex shape R894 found in R893.

⚠ **AND R917's OWN OPENING PREMISE WAS FALSE AND IS RETRACTED HERE.** It claimed `topw_k4_sham` sat
inside R908's `topw` 16. R906 types that arm `OTHER_SOURCE`; R908's population is `RUBRIC_SELECTOR`;
the sham was never in the denominator. Its admission was measured anyway before this was known —
`margin −0.051343, lo −0.060777, not admitted` — and answers a question no cell depended on.

**Candidates only = apparatus removed (R916) and judge matched to 2B (R895): 86 → 48 arms.**

| rule | published (mixed) | Wilson 95% | **candidates only** | Wilson 95% |
|---|---|---|---|---|
| `random` | 0/38 · 0.000 | [0.000, 0.092] | **0/20 · 0.000** | [0.000, 0.161] |
| `topw` | 7/16 · 0.438 | [0.231, 0.668] | **7/9 · 0.778** | [0.453, 0.937] |
| `greedy` | 6/8 · 0.750 | [0.409, 0.929] | **6/6 · 1.000** | [0.610, 1.000] |
| `indep` | 5/8 · 0.625 | [0.306, 0.863] | **5/6 · 0.833** | [0.436, 0.970] |
| `oracle` | 5/7 · 0.714 | [0.359, 0.918] | **4/4 · 1.000** | [0.510, 1.000] |
| `topvar` | 0/3 | [0.000, 0.562] | **0/1** | [0.000, 0.793] |
| `topwvar` | 0/3 | [0.000, 0.562] | **0/1** | [0.000, 0.793] |
| `topabs` | 0/2 | [0.000, 0.658] | **0/1** | [0.000, 0.793] |

**All eight rules move. The direction is not uniform**: `oracle`'s NUMERATOR falls 5 → 4, because
`oracle_k4_08bR` is an admitted 0.8B arm. That is what makes this a measurement rather than a
denominator derivation, and R917 checked it rather than assuming it.

**R911's objective separation, recomputed on candidates only:**

| specification | signed (published) | **signed (candidates)** | **other (candidates)** | gap | disjoint |
|---|---|---|---|---|---|
| PRIMARY k-matched | 8/11 | **8/8** | **0/12** | **+0.433** (was +0.250) | ✅ |
| pooled over k | 10/19 | **10/12** | **0/12** | **+0.309** (was +0.133) | ✅ |

⭐⭐⭐ **The primary cell is now 8 of 8.** Every candidate signed-mean-weight arm at a shared k is
admitted, and no arm built on magnitude or variance is. The separation the arc reported was
understated, not overstated.

⚠ **WHAT THE PLACEBO WILL NOT LET ME SAY.** Dropping the same NUMBER of arms per rule uniformly at
random (2000 draws) reproduces the corrected share in **7 of 8 rules**; only `topw` escapes its
own small-n null (0.778 vs [0.222, 0.667]). So **only `topw`'s correction is resolvable as a
judge effect** — the other seven are consistent with having simply dropped arms. And for the four
rules whose share is 0 the null is a **point mass at 0**, so the placebo there *cannot fail* and
certifies nothing (P6: UNVERIFIED, not acquitted).

**⚠ EVERY per-rule number written above this section is the MIXED one and is superseded.**

---

## ✅ R918 · THE POPULATION IS NOT A CHOICE — the two "thresholds" are structural predicates

R917 corrected every rate by restricting the population, reading **R906's typing as given**. R906 is
where the population comes from — R908, R909, R910, R911 and R917 all read its `RUBRIC_SELECTOR`
list — and its typing is a decision tree on two numbers chosen in the lines that used them:

```
fixed          -> FIXED_CHECKLIST
exact > 0.95   -> RUBRIC_SELECTOR      <- the population of every rate in this arc
lex   > 0.25   -> PARAPHRASING_GENERATOR
else           -> OTHER_SOURCE
```

⭐ **The cheap hypothesis died before the round cost anything.** I expected the typing to restate my
own arm names, which would make *"the partition is complete at three kinds"* a derivation about a
naming scheme. It does not: it reads each arm's committed per-prompt selection.

**GAUGE (run before the sweep, because it can end the round for free):** of 94 non-fixed arms,
**86 sit at `exact` exactly 1.000, 7 at exactly 0.000, and 1 strictly between** (0.00103). The
widest arm-free band containing the published 0.95 is **(0.001, 1.0], width 0.999**. For `lex`, one
arm at 0.642 and the rest at 0, ≈0 or 1 — arm-free band **(0.033, 0.642], width 0.608**.

**SPECIFICATION CURVE, 9 × 5 = 45 cells, all printed:** 4 distinct partitions, and **`topw`'s
candidates-only share is 7/9 = 0.778 in every cell that has a population at all.**

| `t_exact` | FIXED | RUBRIC | PARA | OTHER | `topw` |
|---|---|---|---|---|---|
| −0.001 (extreme) | 2 | 94 | 0 | 0 | **7/9** |
| 0.00 | 2 | 87 | 0 | 7 | **7/9** |
| 0.50 – 0.99 | 2 | **86** | 1 | 7 | **7/9** |
| 1.00 | 2 | 0 | 87 | 7 | 0/0 |

**CONTROLS.** ① recomputed R906's published four kinds and its 3 untypable arms exactly, from
different code on the same objects. ② the gauge above. ③ **the sweep can move the answer** — at
`t_exact` below the observed minimum, all 94 non-fixed arms become `RUBRIC_SELECTOR` and 8 arms
change kind, so the flat curve is not a blind instrument.

⭐⭐⭐ **VERDICT: `exact > 0.95` is a STRUCTURAL PREDICATE — "is the selection a subset of this
prompt's rubric" — wearing a threshold's clothes.** Naming it as a threshold is what invited this
attack. **R917's corrected numbers do not inherit a researcher degree of freedom from the typing.**

⚠ **AND THE ROUND'S OWN CONTROL FIRED AGAINST ME FIRST.** I pre-registered the extreme as
`t_exact = 0.0`. Seven arms have `exact` **exactly** 0.0 and the tree tests `exact > te` — **a
strict inequality cannot fire on a structural zero at any `te ≥ 0`**, so the extreme I committed to
was unreachable inside [0, 1] and the control failed on its own arithmetic. Same at the top end:
`t_exact = 1.0` empties the kind for the same reason. **Both endpoints of my grid were forced by the
operator, not by the data** — the third structural-zero error in this session, after R915 and
R917's `random` placebo. The pattern is one habit: *I choose a boundary value without checking
whether the comparison operator can reach it.*

---

## ⛔ R919 · SEVEN OF R917's EIGHT PLACEBOS COULD NEVER HAVE FIRED — "1 of 8" was really "1 of 1"

R917 reported that its random-drop placebo put **7 of 8** per-rule corrections inside their own null,
and concluded *"only `topw`'s correction is resolvable as a judge effect — the other seven are
consistent with having simply dropped arms."* **That sentence is withdrawn.** "Consistent with"
implies evidence of no effect. It was silence.

⚠ **AND MY OWN NEXT WAS KILLED FIRST.** R917 proposed *"an MDE on the share, per rule"*. An MDE
presumes a sampling distribution over arms, and **R906's artifact already says
`not_an_admission_probability: "there is no sampling frame over arms"`.** The quantity is
unidentified, not merely hard — G1's exact failure, committed in the closing sentence of the
previous round, which is the sentence with no control attached.

**What IS identified:** R917's placebo drops `d` of a rule's `N` arms uniformly, so the admitted
count among the kept arms is **exactly hypergeometric(N, A, N−d)** — a finite-population fact
needing no sampling frame. Its support is a finite integer set, so *"is any attainable value outside
the 95% band?"* has a closed-form answer.

| rule | N | A | dropped | attainable `a` | 95% band | detectable outcomes | verdict |
|---|---|---|---|---|---|---|---|
| `topw` | 16 | 7 | 7 | 0..7 | 2..6 | **3** | **RESOLVABLE**, MDE **0.326** share |
| `greedy` | 8 | 6 | 2 | 4..6 | 4..6 | 0 | **BLIND** |
| `indep` | 8 | 5 | 2 | 3..5 | 3..5 | 0 | **BLIND** |
| `oracle` | 7 | 5 | 3 | 2..4 | 2..4 | 0 | **BLIND** |
| `random` | 38 | 0 | 18 | 0..0 | 0..0 | 0 | **CONSTANT STATISTIC** |
| `topabs` | 2 | 0 | 1 | 0..0 | 0..0 | 0 | **CONSTANT STATISTIC** |
| `topvar` | 3 | 0 | 2 | 0..0 | 0..0 | 0 | **CONSTANT STATISTIC** |
| `topwvar` | 3 | 0 | 2 | 0..0 | 0..0 | 0 | **CONSTANT STATISTIC** |

**CONTROLS.** ① the exact hypergeometric band reproduces R917's 2000-draw Monte-Carlo band for
**all eight** rules — different method, same object. ② at least one rule is resolvable, so the
instrument is not uniformly blind. ③ every `UNRESOLVABLE` verdict traces mechanically to `A = 0` or
`A = N`, named rather than inferred. ④ R917's observed values re-read from its artifact, not
recomputed.

⭐⭐⭐ **CORRECTED READING: `topw` is 1 hit out of 1 REAL TEST, not 1 of 8.** Its observed 0.778
against an expected 0.438 clears a detectable threshold of 0.326 in share units. The multiplicity
denominator in R917 was wrong by 8×, **in the direction that made me under-claim** — I reported a
lone survivor among eight tests when seven of those were not tests.

⚠ **THE THREE `BLIND` RULES ARE THE INTERESTING FAILURE**, because unlike the four constant ones
they *look* testable: `greedy` 6/8 with 2 dropped has a real, non-degenerate null — and yet **every
one of its 3 attainable outcomes lies inside that null.** A placebo can be non-degenerate and still
have zero power, and nothing on its printed output distinguishes that from a genuine pass.

---

## ⛔ R920 · CLAUSE ③ IS IRREDUCIBLY A PROVENANCE CLAIM — it cannot be checked on the artifact

Every application of clause ③ in this project has been made by **reading
`corebench/select_core.py:102`**, where `oracle_k`, `indep_k` and `greedy_k` open
`data/comparisons.jsonl`. That is a fact about the producer. **This round asked whether the clause
can be checked on the object instead**, and the answer is no.

**The detector.** For each prompt, every size-`k` subset of its full rubric is a candidate core;
their A2 scores form a distribution. Define `π(arm)` = mean over prompts of the arm's own percentile
in that distribution. A label-consumer should sit high; a heuristic should sit where its heuristic
lands. **π needs the labels but not the generator's source** — that is the weakening under test.

**CONTROLS.** ① the measured ceiling **0.9287** and floor **0.0347** bound every real arm, and
`floor < random 0.4962 < ceiling`. ② a uniformly random size-4 arm lands at **0.4962**, inside the
pre-registered [0.40, 0.60] — calibrated, not merely monotone. ④ 965 prompts, **598 exhaustive**,
367 sampled at M=2000, cap logged. Text→index misses: **0**.

**③ THE CONTROL THAT DECIDED IT: `R² (π ~ A2 margin) = 0.9984` over 21 arms.** π orders the arms
exactly as the margin does. It is **not a second instrument**.

| arm | rule | labels? | π | mean A2 |
|---|---|---|---|---|
| `oracle_k4` (+`_oracle_kA/kB`) | oracle | **yes** | 0.8261 | 0.6287 |
| `greedy_k4_greedy_kA/kB` | greedy | **yes** | 0.8163 | 0.6233 |
| `oracle_k4_fit1` | oracle | **yes** | 0.7787 | 0.6145 |
| `greedy_k4_fit1` | greedy | **yes** | 0.7723 | 0.6113 |
| `indep_k4_indep_kA/kB` | indep | **yes** | 0.7680 | 0.6038 |
| `indep_k4_fit1` | indep | **yes** | 0.7339 | 0.5948 |
| `topw_k4` (+`_detA/detB`) | topw | no | 0.6672 | 0.5648 |
| `topwvar_k4` | topwvar | no | 0.5276 | 0.5044 |
| `random_k4_s0/s1/s2` (+ctl) | random | no | 0.4940–0.5161 | 0.4888–0.4986 |
| `topabs_k4` | topabs | no | 0.4924 | 0.4898 |
| `topvar_k4` | topvar | no | 0.4822 | 0.4867 |

⭐⭐⭐ **The bands ARE disjoint — labelled [0.7339, 0.8261] vs blind [0.4822, 0.6672], gap +0.0667 —
and that is not detection.** The separation is carried entirely by score. **At the level of the
artifact, "this core consumed the labels" and "this core is simply better" are the same
observation**, and by `R² = 0.9984` there is no room for a label-blind arm to score as high yet rank
low. A genuinely excellent third-party core would land in the labelled band and be rejected.

**CONSEQUENCE FOR THE DEFINITION:** clause ③ must be stated as a **provenance requirement** — *the
producer must show that no prompt-specific label entered the selection* — and not as anything a
scorer can verify. The definition certifies a **pipeline**, not an artifact, and every use of it on
a core whose production is unknown is unsupported.

⚠ **Register, new line:** *clause ③ verifiable from the artifact* → **N/A**. It would require a
property of the criteria themselves that survives label-consumption, and no round has proposed one.

⚠ **TWO OF MY OWN DEFECTS, BOTH CAUGHT BY THE ROUND'S OWN CONTROLS.**
**① Fifth population error this session.** The first run filtered arms with `a.endswith("_k4")` and
caught **5 of 21**, excluding **every `greedy_*` and `indep_*` arm** — two of the three
label-consuming rules the round is about. Arm names carry suffixes (`_fit1`, `_detA`, `_s0`), so a
suffix test silently selects the arms that happen to have none.
**② A pre-registered WORLD wired into the KILL conditional.** Control ③ *is* the world selector, so
its "failure" is the result — yet the first version exited `UNVERIFIED`, which would have reported a
pre-registered outcome as an unfit instrument. **A kill asks whether the instrument works; a world is
what the working instrument returns.**
**③ And the first `π(max) > 0.98` threshold was §4's `control that cannot PASS`, built again**: A2
over 6 comparisons is discrete, many subsets tie at a prompt's maximum, and the mid-rank percentile
of a tied maximum is **strictly below 1** — so the ceiling is 0.9287 and my threshold sat above what
a maximal plant can return. Restated as `floor < random < ceiling`, which the design can fail.

---

## ✅ R921 · THE COMPARATOR MOVES THE COUNT, NOT THE ORDER — and 2 of the 12 still flip

Clause ② admits an arm when `lo(A2(arm) − A2(comparator)) > 0`, and every published admission used
`genericpool16`, which R913 showed is itself one of the 99 scored arms. R914 priced an independent
comparator at 15,488 judge calls. **The cheap question was never asked: what if the comparator is
any arm already on disk?** Zero judge calls, and it bounds what the 15,488 would buy.

⭐⭐⭐ **GAUGE TEST SPLITS THE ROUND.** `mean margin(A,C) = mean A2(A) − mean A2(C)`, and the second
term is identical for every arm `A`. **So the ordering of arms by mean margin is invariant to the
comparator, exactly, by linearity — a DERIVATION.** What is *not* forced is the admission decision:
`lo` is a bootstrap quantile whose width depends on `cov(A2(A), A2(C))`, so the admitted sets need
not be nested. That is the measurement. ⚠ It also makes the sweep nearly free — bootstrap the
**per-arm** means once (99 × 8000) and every comparator pair is a subtraction.

**CONTROLS.** ① R881's committed `lo` reproduced by a different code path *and* a different seed:
`topw_k4` +0.014402 → +0.014252, `topabs_k4` −0.063677 → −0.063580, `topvar_k4` −0.066342 →
−0.066258, `topwvar_k4` −0.048203 → −0.048328; all four decisions identical, max |Δ| = 0.00015
against a stated tolerance of 3e-3. ② the derivation verified numerically against 6 random
comparators — this tests the **code**, not the world. ③ **placebo:** every arm against itself,
max |lo| = 0.0000000000, 0 of 99 admitted.

**THE CHAIN TEST, ON THREE NESTED POPULATIONS:**

| population | comparators | non-comparable pairs |
|---|---|---|
| all scored arms | 99 | **2 of 4851** |
| candidates (apparatus + second judge removed) | 53 | **0 of 1378** |
| legitimate (prompt-blind) | **2** | **0 of 1 — nested** |

⭐ **Only 2 of 99 arms are legitimate comparators.** Clause ② needs a *prompt-blind* one, and an arm
whose selection is identical on every prompt is prompt-blind by construction — R906's `fixed`
predicate. Exactly `generic` and `genericpool16` qualify. `generic` admits **24**, `genericpool16`
admits **28**, and 24 ⊂ 28.

⭐⭐⭐ **WORLD A: the comparator slides a threshold along a fixed ordering.** It changes **how many**
arms pass, not **which** — so `28` is a cut point, and R914's 15,488 judge calls would buy a
different **count**, not a different **set**.

⚠ **BUT THE FLIP IS NOT ZERO, AND IT REACHES THE DELIVERABLE.** Of the **12** arms the two-clause
definition admits: **9 survive both legitimate comparators**, **2 genuinely flip** —
`generic_reprov` and `topw_k2` — and **1 (`generic`) is unevaluable because it IS one of the two
comparators** (a structural zero, R915's shape, and the reason a raw difference set names 4 arms
when only 3 are real). **So `topw_k2`'s membership in the twelve is comparator-dependent and must
be quoted with `genericpool16` named.**

⚠ **AND MY VERDICT STRING OVER-CLAIMED BEFORE THE FIX — R917's DEFECT, ONE ROUND AFTER WRITING IT
UP.** The first run computed the chain test over all 99 comparators, found 2 non-comparable pairs,
and printed **WORLD B**. All four arms in those pairs — `oracle_k4_fit1_08b`, `random_k12_s2_08b`,
`random_k4_s0_08b`, `promptecho_sham` — are second-judge or apparatus arms this arc had already
excluded. **The verdict's population was wider than the claim's.** Restricted to candidates the
family is a perfect chain, 0 of 1378.

---

## ⛔ R922 · CLAUSE ② IS A THRESHOLD ON MEAN A2, NOT A COMPARISON — on its own admissible comparators

R921 proved the arm ordering by mean margin is comparator-invariant and that the admitted sets nest.
That leaves one possibility the definition never confronted: **if the admitted set is always the
top-N of one fixed ordering, clause ② is a threshold and the comparator only places the cut.**

⚠ **NOT FORCED, checked first.** `lo(M_a − M_c)` is a quantile of the bootstrap distribution of a
*difference*, so it depends on `cov(M_a, M_c)` — an arm with a **higher** mean A2 can have a **lower**
bound. An **inversion** (higher-mean arm rejected while a lower-mean arm passes) is possible, and
whether any exist is the estimand. R921's nesting is *necessary* for threshold behaviour but not
*sufficient*.

**CONTROLS.** ① R921's admitted count reproduced for **all 99** comparators at the same seed. ②
**plant, calibrated by arithmetic before running**: σ_diff **0.5214**, predicted `lo(P)` **−0.012844**,
achieved **−0.012581**; at g=0.02 P is rejected while Q (half the mean margin) is admitted and the
inversion is **FLAGGED**; at g=0 neither is admitted and nothing is flagged. ③ **synthetic threshold
world** — every arm = comparator + a constant — returns **0 inversions**, so a zero is a measurement
and not silence.

| comparator population | comparators | inversions |
|---|---|---|
| all scored arms | 99 | **24** (11 carry ≥1) |
| candidates (apparatus + second judge out) | 53 | **10** (5 carry ≥1) |
| **legitimate (prompt-blind — all clause ② permits)** | **2** | **0** |

⭐⭐⭐ **WORLD A on the population the clause permits.** Under both `generic` and `genericpool16` the
admitted set is **exactly the top-N by mean A2**. **Clause ② as the definition actually uses it is a
threshold with a calibration, not a contrast** — and "beats a named prompt-blind comparator" implies
work that, here, is not being done.

**The implied cut, per legitimate comparator:** `genericpool16` **0.5514** (28 admitted), `generic`
**0.5593** (24 admitted). Spread between them **0.0080**; across all 99 comparators the cut ranges
**0.4084–0.6283**, spread **0.2199**. **A cut quoted without its comparator is unscoped either way.**

⚠ **THE MACHINERY IS NOT INCAPABLE — IT SIMPLY DOES NO WORK HERE.** 24 inversions exist across the
full comparator set and the planted pair was detected, so the instrument can see non-threshold
behaviour. **Clause ② *could* act as a comparison; on its own admissible comparators it does not.**

⚠ **AND MY VERDICT STRING READ WORLD B OFF ALL 99 BEFORE THE FIX — the seventh time this session a
verdict's population and a claim's population came apart.** This one was caught before publication
rather than after, which is the only thing that has changed.

⚠ **AND THE FIRST PLANT COULD NOT HAVE PASSED**, for a reason arithmetic settles in one line: with
Gaussian noise σ=0.12 at n=968 the SE is ≈0.0039, so `lo(P) ≈ +0.012` and **P was admissible by
construction** — no inversion could exist and control ② failed on its own design. That is §4's
*control that cannot PASS* in a form the entry does not yet name: **not a threshold above the
ceiling, but a plant too weak to reach the threshold.** The remedy is the same shape — compute what
the design can return under the plant *before* running it.

---

## ⛔ R923 · EVERY PUBLISHED NUMBER WAS CALIBRATED AGAINST THE WEAKER COMPARATOR

R922 left two admissible calibrations: `genericpool16` → cut **0.5514**, 28 admitted; `generic` →
cut **0.5593**, 24 admitted. **Clause ② already has a procedure for deciding whether one arm
resolvably beats another, and both comparators are arms.** So the round turns the definition on
itself.

⚠ **AND MY OWN NEXT PROPOSED THE WRONG COMPARISON.** It said to check the 0.0080 cut gap against
R860's MDE of 0.0103. **R860's MDE is for a paired difference between two arms; the cut is a
threshold on mean A2** — different statistics, different scales. That is §4's *"the control targets
a different statistic than the one being reported"*, and an inherited MDE is another design's
resolution, never this one's.

⭐⭐⭐ **CLAUSE ② TURNED ON ITS OWN COMPARATORS:**

| contrast | margin | 95% CI | admits? |
|---|---|---|---|
| `generic` − `genericpool16` | **+0.009103** | **[+0.005730, +0.012488]** | **YES** |
| `genericpool16` − `generic` | −0.009103 | [−0.012488, −0.005730] | no |

**`generic` resolvably beats `genericpool16` by the definition's own bar.** So the two calibrations
are genuinely different — and **every published number in this arc used the weaker one.** Under the
stronger admissible comparator the admitted count is **24**, not 28.

**CONTROLS.** ① R922's cuts and counts reproduced exactly at the same seed (0.559311/24,
0.551354/28). ② **resolution measured for THIS estimand, not inherited**: the half-width of an
arm's margin CI vs `genericpool16` has median **0.009956**, IQR **[0.008227, 0.011842]** over 99
arms. ③ dose-response on the arm nearest the bar, **with its forced part labelled** — `lo(d) =
lo(0) + d` exactly, verified once against a real bootstrap, so linearity and the flip at `d = −lo(0)`
are derivations; what is measured is that `|lo(0)| = 0.005730` falls **inside** the 0.009956 band.
④ placebo `lo(X − X) = 0.0` for both comparators.

⭐⭐ **BOUNDARY CENSUS — and this is the number the deliverable turns on.** Against `genericpool16`
at resolution **0.009956**, **5 of the 28 admitted arms sit within the resolution of the bar**:
`generic`, `generic_reprov`, `greedy_k12_fit1`, `topw_k2`, `topw_k8`. Seven arms in total are inside
the band on either side. **Their admission is a coin this design cannot call.**

**CONSEQUENCE FOR THE DEFINITION.** Two of the five — `generic_reprov` and `topw_k2` — are exactly
the arms R921 found flipping between comparators, and now with a mechanism: they are within one
resolution of the cut. **So the twelve is not twelve.** It is **9 arms admitted by a margin the
design can resolve**, plus a boundary layer whose membership depends on which admissible comparator
is named.

⚠ **The definition must therefore state the comparator AND the resolution**, and quote the admitted
set as a resolved core plus a named boundary layer — not as a count.

---

## ⚠ R924 · CLAUSE ① IS NOT IMPLIED BY CLAUSE ② — but its independent necessity is still open

§4's remedy for *"the definition describes the instance"* is per-clause and mechanical: **name an
admissible object this clause EXCLUDES.** Clauses ② and ③ have been taken apart; **clause ①
(`size > 1`) had never been asked.**

**The cheapest decisive form is an upper bound.** Build the **k=1 ORACLE** — per prompt, the single
criterion with the highest A2, chosen *with* the labels. No label-blind size-1 selector can beat it
on any prompt.

| contrast | mean A2 | margin | lo | admitted |
|---|---|---|---|---|
| k=1 oracle vs `generic` | 0.6478 vs 0.5514 | **+0.096403** | **+0.089529** | **YES** |
| k=1 oracle vs `genericpool16` | 0.6478 vs 0.5422 | **+0.105524** | **+0.098130** | **YES** |

⭐⭐⭐ **The k=1 oracle clears clause ② by an order of magnitude more than the bar's resolution
(0.00996), and at mean A2 0.6478 it beats every k=4 arm in this arc — including the k=4 oracle at
0.6287.** With labels, **one well-chosen criterion beats four.** So clause ① **excludes an object
clause ② admits: it is not implied.**

⚠ **BUT ITS INDEPENDENT NECESSITY IS NOT SETTLED, AND THE ROUND SAYS SO.** The oracle consumes
labels, so clause ③ excludes it too — the exclusion may be doubly redundant. **An upper bound that
FAILS settles a family; this one PASSED, so it settles nothing about *label-blind* size-1 sets.**
The only label-blind size-1 arm built, `topw_k1`, is not admitted — **1 arm, an observation, not a
bound.**

**MECHANISM, reported either way so the result is readable:** a size-1 set ties on **4.71%** of
pairwise comparisons against **0.03%** at k=4 — **137× more**, because one criterion often cannot
separate two responses and `cls` returns 0, which scores as a miss. **That cost is real but far too
small to stop the oracle.**

**CONTROLS.** ① R921's counts (24 / 28) and R881's decision for `topw_k1` reproduced. ② upper-bound
validity — **0** violations by the 2B arm. ③ placebo: a uniformly random size-1 selector sits at
percentile **0.4939**, mid-distribution as required. ④ the tie mechanism measured, not asserted.

⚠ **THE BOUND HAS A JUDGE SCOPE, AND CONTROL ② FOUND IT BY FAILING.** The oracle is built from
`sat_full.npz` (2B judge) and bounds **2B-judged** size-1 sets only: `topw_k1` violates on **0** of
968 prompts, `topw_k1_08b` on **34**. Eighth scope error of the session — and **the first caught by
a control written for it** rather than discovered afterwards. ② was written to catch a mis-joined
criterion index and caught a judge mismatch instead, which is the argument for writing the control
even when you are sure what it will say.

⚠ **AND THE VERDICT STRING PRINTED "k=1 fails for a reason" IN THE BRANCH WHERE k=1 PASSED** — §4's
*"the verdict string is not a computation"*, with the mechanism sentence hard-coded to the failing
branch. Fixed to be computed per branch.

### ⚠ DERIVATION, not evidence — the arc under the stronger comparator
R921 proved the admitted sets **nest** and committed both, so recomputing under `generic` is set
arithmetic on committed data. Arms lost: **`generic_reprov`, `greedy_k12_fit1`, `topw_k2`** (plus
`generic` itself, a self-exclusion structural zero). **R911's OTHER group was already 0 admitted and
cannot fall** — its survival is forced, and reporting it as a replication would be false.

---

## ✅ R925 · CLAUSE ① IS INDEPENDENTLY NECESSARY — and label access is worth 1.82× more at k=1

R924 left clause ①'s independent necessity open: the k=1 oracle clears the bar, but clause ③
excludes it anyway, and only **one** label-blind size-1 arm had ever been built. **This sweeps every
label-blind ordering the generator itself expresses** — mean weight, |weight|, satisfaction variance,
weight×variance — across **rank positions r = 1…15** (the arc had only ever used rank 1) and **both
coverage rules**. 120 arms, all subsets of `coval_full`, **zero judge calls**.

⭐⭐⭐ **WORLD A: 0 of 120 arms clear clause ②, under either comparator. 240 cells tested, 0
surviving BH at q=0.05.** Clause ① is **independently necessary** against every ordering this
generator can express.

| arm | mean A2 | lo vs `generic` |
|---|---|---|
| `weight` rank **2** (best of 120) | **0.5314** | −0.028963 |
| `weight` rank 1 (= `topw_k1`) | 0.5256 | −0.035329 |
| `weight` rank 3 | 0.5233 | −0.037314 |
| comparator `generic` | **0.5514** | — |
| comparator `genericpool16` | **0.5422** | — |
| **k=1 ORACLE** | **0.6478** | +0.089529 |

⭐ **Rank 2 beats rank 1** — the top-weighted criterion is not the best label-blind single choice,
which is a question the arc never asked because it only ever built rank 1.

⭐⭐ **THE PRICE OF CLAUSE ③ AT k=1: 0.6478 − 0.5314 = 0.1164.** ⚠ Its **sign** is forced (the oracle
is a per-prompt maximum) and is a derivation; its **size** is not. Against the same gap at k=4
(0.6287 − 0.5648 = **0.0639**), **label access is worth 1.82× as much at k=1** — **clause ③ protects
most exactly where clause ① bites.**

**CONTROLS.** ① `weight` rank 1 reproduces the built `topw_k1` on **all 968 prompts, 0 differences**,
and its R881 admission decision. ② upper-bound validity: **0** of 108,936 defined cells exceed the
oracle. ③ placebo: a uniformly random rank sits at percentile **0.4939**. ④ the orderings genuinely
differ — max pairwise rank-1 agreement **0.6043**, so the grid is as wide as it looks.

⚠ **FOUR OF MY OWN DEFECTS, ALL CAUGHT BY CONTROLS ① AND ②, NONE AFTER PUBLICATION.**
**① The emission index is not the rubric index.** `select_core.py` emits `f"{pid}|{j}|{x}"` where `j`
is the position in `sel`, and for `full`, `sel = ok` — a *filtered* subset of the rubric. Reading
`items[p][i]` with those indices misaligned every weight; control ① caught it at **|ΔA2| = 0.544**.
**② The 529 "bound violations" were my own NaN-fill.** A RESTRICTED arm is undefined below rank `r`;
filling those cells with the arm's mean can exceed that prompt's oracle maximum. The bound must be
checked only where the arm is *defined*.
**③ Sort stability is part of the specification.** `select_core` uses Python's stable `sorted()`;
`np.argsort` defaults to unstable quicksort. Measured: rank 1 differs on **137 of 968** prompts under
the default sort, **8** under `kind="stable"`. A tie-breaking rule was a 26%-of-population difference.
**④ A text key is not an identity key.** The last 2 mismatches were prompts carrying a criterion
whose **text appears twice** with different weights and satisfaction rows; a `text → index` dict
collapses the pair onto its first occurrence. **The instrument's unit was TEXT; the claim's unit is
CRITERION INDEX.** Repaired with an order-preserving two-pointer match — 0 differences remain.

⚠ **WHAT THIS CANNOT SAY:** that *no* label-blind size-1 selector exists. It sweeps the orderings
**this generator expresses**; a selector built on some other property of the criteria is uncovered,
and nothing here excludes one.

---

## ✅ R926 · THE PRICE OF CLAUSE ③ DECAYS MONOTONICALLY IN k — at every sampling cap

R925 gave two points (0.1164 at k=1, 0.0639 at k=4). Two points are not a curve, and the shape
decides how clause ① should be worded.

⛔ **THE STRONGEST CONFOUND WAS IN MY OWN INSTRUMENT AND POINTED THE SAME WAY AS THE HYPOTHESIS.**
The oracle at each k is a maximum over `C(m,k)` subsets, sampled above a cap — and a sampled maximum
is a **lower bound**. `C(m,k)` peaks at middle k, so a fixed cap biases the oracle down most exactly
where the gap was predicted to fall. **So the cap is a swept axis, not a constant.**

**THE CURVE, at M = 8000:**

| k | oracle | best label-blind | **gap** | blind spec |
|---|---|---|---|---|
| 1 | 0.6478 | 0.5314 | **0.1164** | `weight` rank 2 |
| 2 | **0.6565** | 0.5536 | **0.1029** | `weight` rank 1 |
| 3 | 0.6547 | 0.5632 | **0.0915** | `weight` rank 1 |
| 4 | 0.6497 | **0.5642** | **0.0856** | `weight` rank 1 |
| 6 | 0.6332 | 0.5641 | **0.0691** | `weight` rank 1 |
| 8 | 0.6145 | 0.5593 | **0.0552** | `weight` rank 1 |

⭐ **The oracle peaks at k=2, the best blind selector at k=4.** Neither peaks at the released core's
k, and both are interior optima — so "more criteria is better" is false on both sides.

**② THE PRECISION SWEEP — and the bias runs AGAINST the finding, not for it:**

| k | M=500 | M=2000 | M=8000 | spread | exhaustive @8000 |
|---|---|---|---|---|---|
| 1 | 0.1164 | 0.1164 | 0.1164 | 0.0000 | 968 |
| 2 | 0.1029 | 0.1029 | 0.1029 | 0.0001 | 968 |
| 3 | 0.0893 | 0.0913 | 0.0915 | 0.0023 | 965 |
| 4 | 0.0814 | 0.0847 | 0.0856 | 0.0041 | 873 |
| 6 | 0.0644 | 0.0677 | 0.0691 | 0.0047 | 531 |
| 8 | 0.0494 | 0.0530 | 0.0552 | 0.0057 | 531 |

⭐⭐⭐ **More sampling RAISES the high-k gaps, so a bigger cap makes the curve FLATTER, never
steeper.** The measured decay is therefore an **upper bound on the steepness**, and the confound
cannot have manufactured it. Worst spread **0.0057**, below the **0.0103** yardstick — and the curve
is **monotone at all three caps**, so the ordering is robust across the whole specification.

**CONTROLS.** ① k=1 reproduces R925's oracle 0.6478 and blind 0.5314 to Δ 4.3e-05 / 6.3e-06 — and
k=1 is exhaustive for every rubric, so drift there would be code, not sampling. ③ forced endpoint:
**0** prompts with `m ≤ k` where oracle ≠ blind. ④ placebo: a random k-subset sits at percentile
0.490–0.504 across all six k.

⭐⭐ **WORLD A: `size > 1` is correctly shaped as a lower bound.** Label access is worth most at the
smallest set and its value decays as the set grows — **the regime clause ① excludes is precisely the
one where clause ③ is cheapest to violate profitably.** The two clauses are not independent
requirements that happen to coexist; they guard the same failure from opposite sides.

⚠ **THE TAIL IS FORCED**: at `k = m` every selector picks the whole rubric and the gap is exactly 0,
so decay near the top of the range is a derivation. It does not dominate here — **888 of 968 prompts
still have a real choice at k=8.**

⚠ **EVERY GAP IS AN UPPER BOUND ON THE PRICE**: the blind side is the best of the orderings *this
generator* expresses, so a better label-blind selector shrinks all of them.
