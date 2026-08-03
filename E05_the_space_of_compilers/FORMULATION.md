# What a "core" is — the formulation, stated once

*Every claim carries its round and its status. Nothing here is asserted without one.*

**Status vocabulary.** `DERIVED` — forced by the algebra, labelled as such, evidence of nothing on
its own. `MEASURED` — with population, instrument, baseline, regime. `UNVERIFIED` — the measurement
ran and its controls did not behave; never an acquittal. `OPEN` — running now.

---

## The definition — COMPLETE EVIDENCE TABLE, 2026-08-03

> **A core is a set of criteria that predicts held-out human judgement better than chance, and
> better than the same criteria applied to a different prompt.**

**Both clauses have now been tested against every object this benchmark builds.** Nine arms, each
admitted or excluded by measurement, none by assertion.

| arm | A2 | clause 1: > chance | clause 2: > its own sham | |
|---|---:|---|---|---|
| `topw_k4` | 0.5667 | **+0.0692** [+0.0570,+0.0814] | **+0.0736** [+0.0648,+0.0820] | **ADMITTED** |
| `coval_core` | 0.5671 | separable | **+0.0694** [+0.0609,+0.0777] | **ADMITTED** |
| `gen` | 0.5350 | **+0.0390** [+0.0304,+0.0478] | **+0.0522** [+0.0428,+0.0625] | **ADMITTED** |
| `full` | 0.5134 | **+0.0131** [+0.0061,+0.0202] | **+0.0465** [+0.0379,+0.0553] | **ADMITTED** |
| `topwvar_k4` | 0.5059 | +0.0092 [−0.0003,+0.0153] — **includes 0** | — | **excluded** |
| `random_k4` | 0.4943 | 0 by construction | — | **excluded** |
| `topabs_k4` | 0.4941 | −0.0003 [−0.0146,+0.0177] | — | **excluded** |
| `topvar_k4` | 0.4884 | **−0.0123** [−0.0203,−0.0040] — *below* chance | — | **excluded** |
| `gen_sham` | 0.4828 | below random | — | **excluded** |

### ⚠ Both clauses are load-bearing — the object that proves it

Nothing above passes one clause and fails the other, which by the exclusion test left **clause 2
untested as an independent requirement.** The object that separates them:

**Four generic quality criteria, identical on every prompt** — *accurate · clear · helpful ·
avoids harm.*

| | | |
|---|---|---|
| **clause 1** | `generic − random` = **+0.0611** [+0.0515, +0.0702] | **PASSES** |
| **clause 2** | `generic − its sham` = **0.0000 exactly** | **FAILS** |

`generic` scores **0.5554** against `topw_k4`'s 0.5667 — **within 0.011 of the best arm in the
benchmark**, on criteria that never look at the prompt. Clause 1 alone would admit it.

⚠ **The clause-2 side is a DERIVATION, not a measurement.** The criteria are identical across
prompts, so prompt *i*'s sham *is* prompt *i*'s core and Δ=0 is forced by the algebra. It shows
clause 2 **can** reject what clause 1 admits — which is what "does this clause do work" asks —
and it must never be quoted as a measured rejection.

### ⛔ THE DEFINITION IS NOT MONOTONE IN FIDELITY, AND THE COST IS SEPARABLE

The exclusion test asks whether a clause rejects an admissible object. It does not ask **how good
the rejected object is.** Asked directly, over the same 968 prompts, 3 seeds, paired bootstrap:

| | A2 | |
|---|---:|---|
| `generic` | **0.5554** | **EXCLUDED** by clause 2 |
| `full` | **0.5134** | **ADMITTED** |

> **`generic − full` = `+0.0420` [+0.0334, +0.0502] — separable.**

**The definition rejects a separably better predictor than one it admits.** That is not an error in
either verdict; it is the price of the second clause, and it now has a number. **What clause 2 buys
is aboutness; what it costs is up to 0.042 of A2** — four times the +0.011 that being about the
prompt is worth at the top of the table.

**The obvious escape does not open** (R276). *Perhaps `generic` only looks good because A2 rewards
the common verdict* — i.e. it is a constant in disguise, and clause 2 discards nothing. Tested
against the **best of all 75 weak orderings, chosen with hindsight**, which is the strongest
prompt-blind constant that exists:

| | margin over best constant | emitted-class entropy |
|---|---:|---:|
| `coval_core` | +0.1187 [+0.1064,+0.1310] | 4.555 bits (0.772 of human) |
| `topw_k4` | +0.1155 [+0.1037,+0.1273] | 4.584 (0.777) |
| **`generic`** | **+0.1077** [+0.0952,+0.1198] | **4.579 (0.777)** |
| `full` | +0.0630 [+0.0507,+0.0749] | 4.561 (0.773) |

**`generic` is not degenerate by any measure available here** — its verdict entropy is
*indistinguishable from the best arm's* (4.579 vs 4.584), it departs from its own modal class on
94.4% of prompts, and it clears the hardest constant baseline by +0.108. Positive control (a
constant arm reproducing its own baseline) exact to 0.00e+00; placebo 0.0000; best/modal/mean-of-75
baselines agree in sign on all six arms.

⚠ **And the reason it is not degenerate is worth stating, because the label misleads**: `generic`
is **criteria-blind to the prompt, not response-blind.** The judge still scores those four fixed
criteria against *that prompt's four responses*. Prompt-blindness in the strong sense is the
constant baseline, and everything here beats it — including `random_k4` at +0.0448, **which is why
this statistic answers "is `generic` degenerate" and cannot rank arms.** All six clear BH.

⚠ **This is a CHOICE, and it must be read as one.** A definition of "core" keyed on fidelity alone
would admit `generic` and rank it fourth of eleven. This one does not, because a set of criteria
that never reads the conversation cannot be *a core of that conversation* whatever it scores — the
same reason a stopped clock is not a chronometer. **But nothing measured here forces that
preference.** It is a commitment about what the word is for, priced at −0.042, and the price is
stated so that anyone who disagrees can pay it back.

**4 admitted, 6 excluded.** Every sham lands at or below random — **0.4931 · 0.4976 · 0.4828 ·
0.4669** against 0.4943 — and `full`'s is the lowest: **fifteen criteria about the wrong
conversation are worse than four drawn at random from the right one.**

⚠ **AND THAT PATTERN IS A DIAGNOSIS, NOT A RESULT** (carved into `realstat §4` the same day). A
placebo should land **on** the floor; landing **below** it means the arm was built with the
ingredient *inverted*, not *absent*. So the clause-2 column above bounds **benefit + harm**, and
the value of aboutness in isolation is the neutral gap `topw − generic` = **+0.0114**
[+0.0045, +0.0192] — **6× smaller than the sham gap the same table reports.**

⚠ **What the table does NOT claim.** The four admitted arms span A2 0.513–0.567 and their sham
gaps span +0.047 to +0.074 with **overlapping intervals**. Only `topw_k4` vs `coval_core` was
tested for a tie and found one (5 of 5 fidelity dimensions null). **Any ordering read off this
column is an argmax over overlapping brackets** — the failure retracted at k=4 this morning.

⚠ **And the clause that is NOT here.** Nothing about **size**, **source**, or a **ceiling**.
Each was tried, each named a number or a provenance the release cannot resolve, and each was
removed by the exclusion test rather than softened. `k = 3…8` are mutually indistinguishable;
a generated core with 98.8% novel content is admitted; the rubric's own reliability is
1.0 by construction.

---

## The definition — THIRD REWRITE, superseded by the table above, kept per L81

The second rewrite added a mechanical test: **for each clause, name an admissible object it
EXCLUDES.** Applied to itself, in one command, it killed four of its own five clauses.

| clause of rewrite #2 | what it excludes | verdict |
|---|---|---|
| *a small set of criteria* | k=12 — but k=12 vs k=4 is **−0.0069 [−0.0210, +0.0072]**, not separable | **under-determined at the upper end** |
| *reproduces human judgement* | `random_k4` — agrees with the rubric at 0.8247 and with the human at chance | **CLEAN. The only clause that does work.** |
| *at the humans' own level* | `gen`, at **−0.0183 [−0.0323, −0.0036] BELOW** the ceiling — and the benchmark accepts `gen`. Meanwhile `coval_core` **+0.0176** and `topw_k4` **+0.0141** are separably **ABOVE** it | **FALSE in both directions** |
| *may be selected or written* | nothing | **decoration** |
| *on this release selection measures better* | nothing | **a finding, not a clause** |

> **A core is a set of criteria that predicts held-out human judgement better than chance, and
> better than the same criteria applied to a different prompt.**

| clause | the admissible object it excludes |
|---|---|
| **better than chance** | `random_k4` (0.5005 ≈ chance) · `topvar_k4`, separably **below** random at −0.0123 [−0.0203, −0.0040] |
| **better than the same criteria on a different prompt** | `gen_sham` (0.4834, below random). This is the **aboutness** requirement, and it is the clause the whole sham design exists to make testable |

**Admits:** `coval_core`, `topw_k4`, `gen`, `full` — each beats chance *and* beats its sham.
**Excludes:** `random_k4`, `gen_sham`, `topvar_k4`.

⚠ **It does not distinguish a core from the rubric it compresses, and neither does the data.**
`full` qualifies. Size, source and ceiling are all **out** — every attempt to put them in named a
number or a provenance the release cannot resolve. What is left is small enough to be true.

---

## The definition — SECOND REWRITE, superseded, kept per L81

The first rewrite is annotated below. **Three of its five clauses failed the same test within
hours: a word chosen because it described the released object, then carried as though it had
been measured.** `four` (k-sweep: 3–8 indistinguishable) · `its verdicts` (cores track the human,
not the rubric) · `the rubric's own reliability` (a rubric is deterministic; its reliability is
1.0 by construction). This version states each clause with what currently supports it.

> **A core is a small set of criteria that reproduces human judgement at the humans' own level
> of agreement with each other. It may be selected from an existing rubric or written from the
> conversation; on this release selection measures better.**

| clause | status | the measurement |
|---|---|---|
| **a small set of criteria** | **MEASURED, size unresolved** | k=1 is separably worse; **k = 3…8 are mutually indistinguishable**; k=12 and the full 15.5 lose. "Four" is retracted — it was the released core's k |
| **reproduces human judgement** | **MEASURED, and corrected** | normalised by each target's ceiling, top cores reach **1.04 / 1.04 / 0.99** of the human ceiling against **0.74–0.80** of the deterministic rubric. `its verdicts` retracted |
| **at the humans' own level of agreement** | **MEASURED, and corrected** | the ceiling is **0.5451** (A2, one annotator vs another) — the *human's*. `the rubric's own reliability` named a quantity that is **1.0000 by construction** |
| **may be selected or written** | **MEASURED, permission not prescription** | a core generated from the conversation alone, **98.8% novel, 0 verbatim**, beats random and beats its own sham — but is **separably worse than selection on A2/A3/A4/A5** |
| **on this release selection measures better** | **MEASURED** | `topw_k4` and `coval_core` are the only pair no fidelity comparison separates; `gen` sits separably below both |

⚠ **`of a rubric` is gone from the definition on purpose.** The generated core never saw
`coval_full` and is still admissible, so the rubric is a **source of candidates**, not a
constitutive part of what a core is. Keeping the phrase would have made the definition false of
an object the benchmark accepts.

---

## The definition — FIRST REWRITE, superseded, kept per L81

The old definition is kept below, annotated, because a ledger that edits its own history is
the thing it exists to prevent. What follows replaces it. **Six measurements constrain it;
each clause names the one it rests on and the scope over which that holds.**

> **A core is a rewriting of a rubric that preserves its verdicts at the rubric's own
> reliability, using fewer criteria than the rubric contains.**

| clause | why it is worded that way | the measurement |
|---|---|---|
| **a rewriting** | not *a subset*. `coval_core` shares only **8%** of its text verbatim with `coval_full`, 23% at similarity ≥ 0.90, median best-match **0.676**. The task the release actually performed is GENERATION | overlap gradient over 792 core items |
| **of a rubric** | the source is named, because the compression is only defined relative to it | — |
| **that preserves ~~its~~ THE HUMAN'S verdicts** | ⚠ **`its` was wrong and is retracted the same day.** Normalised by each target's own reliability, every top core reaches the **human** ceiling (1.04, 1.04, 0.99) while reproducing only **0.74–0.80** of the deterministic rubric it compresses. A core is **not a summary of the rubric** — it tracks the judgement the rubric was written to approximate, and departs from the rubric to do it | measured human ceiling 0.5451; Δ normalised +0.23 to +0.26, all top arms |
| **at the rubric's own reliability** | two annotators of one prompt agree on the exact class **8.0%** of the time; a constant gets **4.0%**; the best available predictor **15.0%**. A definition demanding high absolute agreement is incoherent on this data | R283, controls saturated |
| **using fewer criteria** | 4 criteria beat 15 by a **separable** paired margin, and adding the discarded criteria back COSTS 1.5 points. Compression is a gain, not a loss to be bounded | B1 = 1.30 ± 0.10; topw_k4 − full = +0.0203 [+0.0055, +0.0362] |
| **(no admissibility gate)** | deliberately absent. Every counting gate — capacity, realised alphabet, ordered Bell — gated a combinatorial structure the data does not exhibit | see below |

### What the definition deliberately does NOT contain, and why

**⛔ No admissibility gate.** `C(n,k) ≤ a(m)` was undefined (two readings of `n` give 0% and
91.7% violation), was violated by its own founding round in **292 of 750 cells**, and compared
*candidate representatives* to *behaviour classes* — two different units. Its only unit-coherent
ancestor, `log₂|H(Q)| ≤ H_eff`, does not admit this release under any reading.

**⛔ No combinatorial requirement.** A core's value is **additive over its criteria**: an
independent per-criterion scorer reaches a combination search, +0.0079 [−0.0079, +0.0238], and
the separator returns **+0.4467** on a synthetic world that does contain set structure — 57×.
Any interaction is below **+0.0176**, the smallest effect this design resolved.

**⛔ No provenance requirement.** Resemblance to the source rubric predicts **nothing** about a
criterion's usefulness: slope −0.0145 [−0.063, +0.033] over 968 clusters, and the decile curve's
range is **1.06×** its own permutation null. Traceability is worth measuring — it is a property
you either want or do not — but it **does not buy fidelity**.

**⛔ No discrimination requirement.** Selecting criteria by satisfaction spread is
**indistinguishable from selecting at random**, +0.0017 [−0.0131, +0.0165]. *Zero variance ⇒
inert* is sound; *high variance ⇒ informative* is its converse and is false.

### ⚠ How few is "fewer"? — the clause above was under-tested when written

`k` was swept on the same rule, paired against k=4, the same day the clause was written:

| k | A1 | norm | paired vs k=4 |
|---:|---:|---:|---|
| 1 | 0.0472 | +0.048 | **−0.0244 [−0.0413, −0.0079] — separably WORSE** |
| 2 | 0.0640 | +0.204 | −0.0072 [−0.0213, +0.0072] |
| **3** | **0.0758** | +0.312 | **+0.0007 [−0.0117, +0.0134]** |
| 4 | 0.0761 | +0.316 | — |
| 6 | 0.0751 | +0.306 | −0.0007 [−0.0131, +0.0121] |
| 8 | 0.0751 | +0.306 | +0.0007 [−0.0127, +0.0145] |
| 12 | 0.0613 | +0.179 | −0.0069 [−0.0210, +0.0072] |

**6 comparisons, 1 separable.** Only `k=1` is distinguishable from `k=4`; **3 through 8 tie**, and
the k=4 "peak" beats k=3 by **0.0003**, which is noise.

⛔ **So "four" is not supported and I inherited it from the released core without testing it.**
What the data supports is: **more than one criterion, and this release cannot resolve `k` anywhere
in 3–8.** The reference construction below is stated at k=4 for comparability with `coval_core`,
**not because 4 was measured to be right.**

### The reference construction, and it is one line

**Take the four highest-mean-importance criteria of `coval_full`.** It ties the hand-built
released core on **every** fidelity dimension (11 cells, 0 separable), is 100% traceable where
the release is 40% novel, costs **no GPU**, and **no fitted model has beaten it** — a ridge over
8 deployable features returns −0.0110 [−0.0255, +0.0028] while its own leaky arm gains +0.1026,
so the design could have seen a gain and there was none.

⚠ **Status: this is what SURVIVED, not what is proven.** Every clause is scoped to one release,
one judge, and exact-class agreement. The register of what this site structurally cannot answer —
cross-release, construct validity, causal identification — is in `corebench/DIMENSIONS.md` and is
not a formality.

---

## The definition — SUPERSEDED, kept per L81

> **A core is a quadruple `(Q, class, representative, certificate)`.**
>
> | | |
> |---|---|
> | `Q` | the declared family of questions the downstream system must answer |
> | `class` | `[N]_Q` — the equivalence class of behaviours under `Q`. **This is the object.** |
> | `representative` | the criteria actually printed. **A choice, not a measurement.** |
> | `certificate` | which is which, at what noise, on whose instrument, and what was not measured |
>
> **Admissible only if** `C(n,k) ≤ a(m)`, where `a(m)` is the ordered Bell number — `a(4) = 75`,
> i.e. **`log₂ 75 = 6.23` bits.**
>
> ⛔ **AND IT WAS VIOLATED BY ITS OWN FOUNDING ROUND, IN 292 OF 750 CELLS** (R279, 2026-08-03).
> R248 introduced this gate and its persisted artifact records `C` for every cell it studied.
> At R248's **own** `a(4) = 75`, over R248's **own** 250 prompts:
>
> | k | violating | share | |
> |---|---:|---:|---|
> | 1 | 0 / 250 | — | **DERIVATION**: `C(n,1)=n≤14≤75`, forced by algebra, never evidence |
> | 2 | 84 / 250 | 33.6% | smallest violating `n` is 13 |
> | 3 | 208 / 250 | 83.2% | smallest violating `n` is 9 |
> | **all** | **292 / 750** | **38.9%** | |
>
> Controls: the artifact's `C` equals `math.comb(n,k)` in **750 of 750** cells, so the field is
> what its name says; negative control `n→n+6` moved 834→1412; placebo (`k=1` under `a(5)`) exactly
> zero; two hash seeds byte-identical. **k=4 is out of reach and registered as such** — R248 never
> ran it.
>
> ⛔ **AND THE LEFT-HAND SIDE IS UNDEFINED** (R278, same day). `n` admits two defensible readings
> and they do not disagree about a magnitude — they disagree about whether this release is
> admissible at all. At the operating point `m=4, k=4`: `n` = `coval_full` (median 15, max 39) →
> **888 of 968 prompts violate (91.7%)**; `n` = the six seed criteria → **0 of 968 (0.0%)**.
> R248/R252/R253 all draw from `coval_full`, which settles the reading by code rather than taste.
>
> **How this was missed for five rounds:** the argument was about whether the right-hand side should
> be `6.23` bits or `3.45`. Both sides took `C(n,k)` as given, so neither could see that the
> left-hand side had already broken the gate. **A unit check would have caught it before any of it**
> — `C(n,k)` counts *candidate representatives*, `a(m)` counts *behaviour classes*, and those
> strings are not equal.
>
> ⛔ **AND THE DEFINITION CONTRADICTS ITS OWN CLAIM 5.** Claim 5 is still `MEASURED` and was never
> retracted: the channel delivers `H_eff ∈ [1.02, 3.45]` bits, so the gate's 6.23 is wrong by 2–6×.
> The gate went `log₂|H(Q)| ≤ H_eff` → `C(n,k) ≤ A_real` → `C(n,k) ≤ a(m)`, and **un-retracting
> `A_real` silently reverted `H_eff` too — only `A_real` was retracted.** So this is not where the
> definition started; it is two steps behind it, at the pre-R237 noiseless bound.
>
> **What that leaves, stated plainly: the definition currently carries NO admissibility criterion
> valid in this release's own noise regime.** The gate is a number the document says is wrong, its
> replacement is retracted (R253), and the one surviving upgrade is scoped to `eps = 0` (R259) — a
> world with 47.8% two-rater agreement is not that world. **Found by a clean-context adversary, not
> by me, and I had predicted "it ended where it started", which was the flattering reading.**
>
> ⛔ **`A_real` was tried as the right-hand side and is RETRACTED (R248 → R253).** It measures
> something real (claim 8, which survives) but it **predicts nothing about recoverability that the
> criterion count `n` does not already predict** — partial rank correlation `−0.0380` and `+0.0107`
> at k = 1, 2, against a permutation `|null|₉₅` of `0.1152` / `0.1399`, `p = 0.535` / `0.850`; and
> adding it makes held-out error **worse** (`+0.0183`, `+0.0085`). `n` alone predicts recovery
> *better* than `A_real` does (`−0.2516` vs `−0.1881`). **The gate had `n` on both sides.**
>
> ⚠ **The measurement R248 made is intact and is not the gate.** Over 250 prompts the median
> `admitted / A_real` is **1.33 / 4.67 / 5.77** at k = 1 / 2 / 3, reaching **10.71** at the ninth
> decile: the data realises far fewer classes than the observation space admits. True, and it
> **does not license a replacement**, because both sides of that ratio are functions of `n` and `k`
> and the difference carries no incremental information about what is recoverable.
>
> **Admissibility is a RATE, not a predicate — AT ZERO RATER NOISE, AND ONLY THERE** (R248,
> scoped by R259). The share of size-`k` subsets this release can identify is
> **U(1) = 0.5714 · U(2) = 0.0606 · U(3) = 0.0105**. Exhaustive arithmetic about the tie structure,
> not a renaming — **and it stops predicting anything once the release's own rater noise is
> present.**
>
> | k | eps | recovery | partial(U \| n) | perm `\|null\|₉₅` |
> |---:|---:|---:|---:|---:|
> | 1 | **0.00** *(forced)* | 0.7470 | **0.7269** | 0.1324 |
> | 1 | **0.25** *(the release's own)* | 0.2566 | **0.0999** | 0.1340 |
> | 2 | **0.00** *(forced)* | 0.2215 | **0.4127** | 0.1265 |
> | 2 | **0.25** | 0.0682 | **0.0541** | 0.1216 |
>
> The `eps=0` row is **algebra, not evidence** — R228 showed noiseless recovery is `E[1/|ties|]` and
> `U` is the share with `|ties| = 1`. It is the positive control, and it fires, so the machinery
> works. At the noise calibrated to the release's own **47.8% two-rater agreement**, `U` is inside
> its permutation null at both k, and adding it to `n` **raises** held-out error (`+0.0143`,
> `+0.0021`) where at `eps=0` it lowered it (`−0.0325`). **The rate says nothing about what is
> recoverable in this release's actual noise regime.**

---

## The eight claims it rests on

**1 · The class is always identifiable; the member never is.** `DERIVED` (R230)
`|{classes under Q}| ≤ |{observations}|` by construction, because `Q`'s classes are *defined* by the
observation. Measured consequence: 72 subsets per prompt collapse into **13** classes, 5.2:1, never
above the forced bound of 75. Class recovery **1.0000** at zero noise (an identity, labelled),
**0.3233** at the release's own rater noise, against the member's **0.0613**.

**2 · The answer is a function of `Q` **and of the baseline's format**, and the sign can flip on
either.** `MEASURED` (R231, R243, and R235 independently)
On `Q =` reproduce Full's weak ordering, the official core scores **0.3864** against a random-4 floor
of **0.3836** — inside the floor's own draw spread, whose `[0.3657, 0.4019]` is a MIN AND MAX OF 20 DRAWS and is no longer quoted as an interval. On `Q =` predict human pairwise
preferences (R220), **0.6602** against a random range of **0.645–0.659**.

⚠ **"Clearly above" is retired, and what replaces it is stronger in one way and weaker in another**
(R262). Re-run under `PYTHONHASHSEED 0/1/2/3`, R220's floor spans **[0.6420, 0.6580]** and the core
clears the top of **every** seed's range — so unlike R231's, this comparison does **not** flip with
the environment, and it had been run exactly once before today. **But the margin over the worst
seed's ceiling is `+0.0022`, and the floor's own hash-seed spread is `0.0020–0.0030`.** A margin the
size of its baseline's arbitrariness is *above*, not *clearly above*. Same data,
same judge, opposite verdicts. **Reporting a preservation percentage without naming `Q` reports a
choice.**

⚠ **Corrected 2026-08-03 by the blind arm.** R243 swept `Q`'s granularity and the sign flips between
requiring **6 of 6** pairwise relations and **5 of 6** — so granularity explains the *sign*. It does
not explain the *magnitude* — **but "36×" is wrong twice and both errors inflate it.**
`+0.0068` is a mean pairwise agreement on `[0,1]`; `+0.2466` is Kendall τ_b on `[−1,+1]`. With zero
sign-ties `τ = 2·frac − 1` holds *identically*, and R243's core τ is `0.6643` against R235's `0.663`
— **on one scale the ratio is 18×.** And the numerator is not reproducible: R243's floor is seeded
with `abs(hash((p, d)))` on a **string** id, so under `PYTHONHASHSEED = 1/2/3/unset` the delta is
`+0.0084 / +0.0090 / +0.0083 / +0.0098` — **the published `+0.0068` is below all four**, the extreme
that maximises the ratio. Honestly re-run it is 25–30×; on a common scale, 18×. **A second
axis differs, and R235 found it without being told to look**: whether the random baseline is granted
the **signed** weights the core's format cannot carry. R235's own grid: *"72 of 286 cells have a CI
containing 0 or Δ<0 and **all** of them use signed weighting; **zero** uniform cells fail."*
**Reporting a preservation number requires declaring the baseline format as well as `Q`.**

**3 · Adding raters does not raise the within-prompt channel.** `MEASURED` (R225)
Recovery gain from keeping individual rankings instead of the consensus: `+0.019` at R=14 against a
seed spread of `0.06` — inside. It fires only at R=2, where the consensus is itself degenerate.
Three estimands were needed to establish this; the first two failed because *tie-count saturates at
both ends*, and the decisive bug was caught by arithmetic, not by a control.

**4 · Precision does not close the gap; independence does.** `MEASURED` (R227)
A 10-point score beats a ranking by `+0.5607` at zero noise and `+0.0118` at the noise level
calibrated to the release's own 47.8% two-rater agreement — **inside** a seed spread of `0.0296`. A
47× difference between the regime the capacity argument assumed and the one that applies.

**5 · The bound must use the noisy channel — and the gate now CONTRADICTS this claim.** `MEASURED`,
as a bracket (R237). ⚠ **The status line used to read "superseded as the gate by claim 8 (R248)";
claim 8's gate role was itself retracted by R253, so this was superseded by nothing.**
`H_eff ∈ [1.02, 3.45]` bits at the release's noise and rater count, against the `6.23` five rounds
assumed. `k=1` needs `3.91`, so **a one-criterion core sits at the edge of the bracket.** Partially
identified, so bounds and not a point.

⚠ R237 sharpened the *capacity* — how much the channel delivers under noise. R248 showed capacity is
the wrong quantity at any sharpness: the binding constraint is how many classes the **rubric**
separates, which is a property of the criteria's mutual agreement and is invisible to every channel
argument. `H_eff` stays as the noise correction it is; it is no longer the gate.

**6 · The failure is the per-prompt factoring, not the data volume.** ⚠ `UNVERIFIED` (R239,
downgraded by R255)
**R239 checked its independence assumption by EXACT TOKEN-SET IDENTITY** — of 15,058 criterion
token-sets, one recurs. **R255 then measured that half of all co-prompt criterion pairs share no
content word at all and still agree behaviourally** (median lexical Jaccard `0.0000`; discrimination
predicts agreement at ρ +0.1440 where lexis manages +0.0447). **Lexical distinctness does not imply
observational independence, and the bits-add derivation `[1006, 3402]` and `k ≤ 119` rest on it.**
Found by a clean context reading two of my own rounds against each other.
Within a prompt the bits do not add; across 986 prompts they do — `[1006, 3402]`. A **global** core
of up to `k=119` is identifiable at the conservative end while a per-prompt core of **2** is not.
The independence assumption was checked: of 15,058 distinct criterion token-sets, **one** appears in
more than one prompt. **CoVal ships the per-prompt object.**

**7 · The bits add across prompts and there is still nothing to identify.** `MEASURED` (R240 → R246
→ R247), and **claim 6 is demoted to true-and-inconsequential**, exactly as `A10/PREDICTION.md`
registered in advance.

R240 fitted a 32-criterion global core on 160,000 judgements over 200 prompts and printed *"A GLOBAL
CORE TRANSFERS."* Three rounds later that verdict is gone and the tensor never changed:

| | fitted core, held out | random-k floor | unselected all-200 | length only |
|---|---|---|---|---|
| R240, **3 seeds**, vs floor's **max of 20 draws** | 0.3500 | max 0.3467 | — | — |
| R247, **10 seeds**, vs the floor's **own 500-draw distribution** | **0.3060** (ptp 0.1100) | 0.2649 | **0.2550** | 0.0420 |

- **Empirical p over the whole k grid: 0.0699–0.1637. BH at q=0.05 kills all six.** R240's crossing
  was `0.3500 − 0.3467 = 0.0033` — **one prompt out of 300** — against the *maximum* of 20 draws,
  which is an extreme order statistic and not a floor.
- **Selection is not the ingredient either.** Using the **entire** 200-criterion vocabulary scores
  0.2550, inside the fitted arm's seed spread at every k. There is no compression to call a *core*.
- **The effect that remains is a direction, not a count**: fitted sits above the floor's *mean* at
  6 of 6 k with the same sign (+0.012 … +0.061), against a seed spread of 0.08–0.11. `effect/floor
  spread < 1.5`, so no share, no percentage — a gradient only.

⚠ **Two of R240's own controls said this before I did, and I read past both.** Its negative control
printed `NOT NULL` and `A10/PREDICTION.md` — written *before* the run — says a non-null negative
control makes the round `UNVERIFIED` regardless of its number. R246 then measured *why*: the arm
evaluated an already-fitted core on a random half of **all** prompts, which is **50.00%** training
data by construction. It could not have come back null.

**What survives, and it is narrower than a core.** Greedy selection over a generic vocabulary
recovers the modal-plus structure out of sample better than *scrambled-target* selection does
(0.2080 vs 0.3060 at k=32) — so the fitter is not overfitting. It simply has nothing to find that
the whole vocabulary does not already carry.

**And two rivals died on the way, which is why the null is admissible.** The target class
distribution is nearly flat — 24 classes over 200 prompts, modal share 0.10, entropy **4.485** bits
against 4.585 for uniform — so a response-blind modal predictor scores **0.0633**, not 0.35.
Response length alone scores **0.0420**. Neither artifact explains anything here.

**8 · The rubric is redundant beyond its own marginals — but "binding constraint" is RETRACTED.**
`MEASURED` (R248, defended R252); the *binding* claim killed by R253

⚠ **The heading used to read "the binding constraint is the rubric's own redundancy, not the
channel."** That is two claims and only the first survives. Redundancy is real and survives its
strongest confound. **Whether it BINDS anything was never tested, and when it was (R253), the
quantity carrying it — `A_real` — predicted recovery no better than the criterion count.** A
property can be present, robust, and load-bearing for nothing. The phrase stayed for five rounds
because it was doing rhetorical work the measurement never did.
Paired per prompt, against a **random tensor of identical shape**: the real rubric separates
**fewer** classes than random noise does, at **62.0% / 90.4% / 91.2%** of prompts for k = 1 / 2 / 3
(median deficit −0.60 / −4.80 / −6.00 classes). This kills the reading that the collapse is
geometry — the quotient of subset-sums into 75 weak orderings — because random criteria pass
through the same quotient and come out **more** separated. **The criteria agree with one another.**

**And it survives its own strongest confound** (R252, run one round later, against my own claim).
R248's rival was `rng.random()` — **uniform, sd 0.2887, against the real tensor's 0.2399: 20.3% more
spread.** A weak ordering is a function of pairwise gaps, so a wider marginal separates more classes
for reasons that have nothing to do with redundancy. R248 varied two things and named one.

The control that separates them: **permute the four response values independently within each
criterion row** — every criterion keeps its *exact* multiset of values, so the marginal is identical
not approximately but exactly, while the alignment *between* criteria is destroyed.

| k | REAL | UNIFORM | **ROW-PERMUTED** (marginal-matched) | GAUSS-MATCHED |
|---:|---:|---:|---:|---:|
| 1 | 8.00 | 9.20 | **10.10** | 9.40 |
| 2 | 12.00 | 17.10 | **17.90** | 17.40 |
| 3 | 12.00 | 19.60 | **19.60** | 19.40 |

Paired sign test over 250 prompts (scale fixed before the run, after R249's mis-scaling):
`k=1 +1.40, 210 up / 30 down, p = 1.9e-34` · `k=2 +5.40, 228/19, p = 1.1e-46` ·
`k=3 +5.80, 230/18, p = 5.0e-48`.

**The uniform rival was CONSERVATIVE, not liberal**, at k=1 and k=2 (+0.60 and +4.80 against the
marginal-matched +1.40 and +5.40). Controls: identical criteria give `A_real = 1` and rise to 7.2 /
18.0 / 17.4 after row-permutation; the identity permutation reproduces the real tensor exactly; and
the **sham** — the *same* permutation applied to every criterion, i.e. relabelling the responses —
leaves `A_real` **unchanged at 9 / 14 / 15**, which is what isolates *agreement* from *labelling*.

⛔ **Consequence: none for the definition.** This paragraph used to end *"only the second number
predicts whether a core is recoverable"* — verbatim the sentence R253 retracted, left standing three
lines under a heading I had already fixed (`fc2c5c4`). **A fix that landed on one path of two**, and
a clean context found it before I did. `A_real` predicts recovery no better than `n`; redundancy is
a real property of the rubric that governs nothing measured here.

⚠ **This round's first positive control could not pass, and repairing it produced the result.** It
demanded `A_real = C(n,k)` from a "maximally separated" synthetic prompt — but a class is a **weak
ordering**, a quotient of the sum vector, so distinct sums need not give distinct classes and no
construction in vector space forces the quotient injective. It returned **10 of 28** at k=2 while a
real prompt returns **12**: *the synthetic bracket sat below the data it was built to bound.* The
replacements are a k=1 case where the ceiling is constructible (exact, passes) and an independent
recount through a second code path (exact agreement, 25 prompts × 3 k). **Fifth
control-that-cannot-pass in this arc, and the first whose repair was the finding.**

---

## 9 · The triple blind, CLOSED — both arms reported, read under the rule fixed before they ran

`A08/README.md` fixed the reading before either agent launched: *disagree on sign → the framing is
the finding, find the assumption they differ on and test that* · **the three will not be averaged.**

### The assumption they differ on, and design A tested it itself

| arm | target | core vs a top-4-by-weight heuristic |
|---|---|---|
| **R234** primary, `Φ` | the full rubric's own signed-weight ordering | **top4_pos beats core +0.0352**, survives BH |
| **R235** | rubric-to-rubric | **top-4-by-mean-weight beats core in 76/286 cells, core wins 0** |
| **R234** leakage-controlled | same target, **top4 selected on a DISJOINT annotator half** | **core 0.8182 > top4 0.8066 — the sign REVERSES** |
| **R234** human arm | the humans' `world` rankings | core **0.6593** vs top4_pos 0.6547; `−0.0046 [−0.0122,+0.0029]`, p=0.26, **BH-killed**, `CI_width/|eff| = 3.3` |
| **R231** (mine) | Full's exact weak-ordering class | core 0.3864 vs random-4 floor 0.3836 — inside. **I never ran a top-k arm** |

⚠ **R234 retracted the mechanical-compiler result by its own analysis, and the reason applies to
R235's too**: *"that target structurally favours subset compilers, since a subset is a sub-sum of
the target's own basis."* The weights used to **select** top-4 are the same weights that **define**
the target. Under leakage control the gap inverts; the human arm is null; the K-sweep is null.
**R235's 76-of-286 is measured on the confounded target, and this arc carried it for two rounds.**

**And the prior-art check neither R235 nor I ran**: R234 read `data/DATASET_CARD.md` first. The card
**documents `top4_pos` as the release's own selection rule**, and documents the positive-weight
rewrite. So "a four-line compiler matches the core on selection" is **the card restating itself** —
the compiler's remaining work is the *rewrite*, which is exactly where R249's redundancy finding
and R250's provenance curve live.

### R234's headline, with its scope

**`Λ_budget = 0.4237`** (seeds 0.4273 / 0.4188 / 0.4252) — the core reaches 42% of what any
4-criterion unit-weight compiler can reach. **Bounded, not estimated**: greedy verified exhaustively
on the 458 prompts with n ≤ 14 (suboptimal on 4.1%, shortfall 0.0069 Φ), so **`Λ_budget ≤ 0.44`**.

| compiler | Φ vs full signed | | human `world` |
|---|---:|---|---:|
| full_signed (target) | 1.0000 *(derivation)* | full_signed | 0.6765 |
| oracle4 (greedy ceiling) | 0.9797 | **core** | **0.6593** |
| top4_pos *(the card's own rule)* | 0.8622 | top4_pos | 0.6547 |
| **core (shipped)** | **0.8270** | full_unit | 0.5961 |
| full_unit (signs dropped) | 0.7669 | sham | 0.5024 |
| random4 — measured floor | 0.7146 ± 0.006 | | |
| sham_core — negative control | 0.4945 *(chance)* | | |
| worst4 | 0.2785 | | |

**Compression cost against humans: `0.0173` [0.0100, 0.0250], 2.1× the measured resolution floor of
0.0081. Above-chance retention 90.1%.** The K-sweep peaks at K=5 (0.6560) then declines — **the core
sits above every K from 1 to 10.**

> **R234's verdict, in its words:** *"The core is a faithful compression of what the full rubric can
> **decide**, and an unfaithful compression of what the full rubric **is**. The loss is in the
> FORMAT, not in this compiler's choices."*

### What R234 found against itself — all four reported, none buried

- **Its pre-registered ceiling was wrong**: `Λ_prereg = 1.142`, outside [0,1], because the split-half
  ceiling compares two n/2 aggregates while the core is scored on the n aggregate. It calls this
  *"the control-that-cannot-pass failure in mirror image"* — **independently hitting the failure mode
  this arc hit six times.**
- **A reproducibility defect in its own code**: `list(set(prompt_ids))` in the cluster bootstrap, and
  Python salts string hashing per process. Two identical runs gave a byte-identical grid but a
  **different summary** — 23 se/p values moved (largest p 0.095 → 0.117). No BH decision flipped,
  and it says so: *"luck, not design."* Fixed to `sorted(...)`, then byte-identical.
- **It retracted its own prohibition finding.** Its first statistic was a ratio of Fisher-z means
  with a near-zero denominator, permutation null centred at **−1.43**. The difference-in-differences
  gives `A = −0.057 [−0.162, +0.041]`, BH-killed. The veto arm points the other way: **the core
  retains 76.1% of above-floor veto detection while mechanically dropping the signs retains 0.9%.**
  The card's documented positive-weight rewrite does real work.
- **S1 is `UNVERIFIED`, not null**: the polarity asymmetry's **sign flips across instruments**
  (+0.19 / −0.20 / −0.21 / −0.29). It is a property of the judge, not of the rubrics.

### The gauge finding that reaches every round in this repository

**The judge is not label-order symmetric.** Reversing *"Yes or No"* to *"No or Yes"* in the question
moves its output to **r = 0.77 against itself**. R234's positive control reproduces the cached tensor
at r = 0.998, so the instrument is faithfully re-implemented — and then fails a basic gauge test that
**every round here, including all of mine, has assumed away.**

**R257 ran the propagation R234 called for, and its repaired pass reproduces R234's instrument
exactly: `r = 0.9980, MAD 0.0082` against R234's `0.998 / 0.008`.** The first pass had retyped the
prompt and scored 0.9407; importing `covalx.judge.build_prompt` closed it.

| control | value |
|---|---|
| **positive** — default re-judge vs the r04 cache | **r 0.9980, MAD 0.0082** |
| **negative** — 200 tasks judged twice in one process | 90.5% exact, **r 0.999450**, max 0.03097 |
| **gauge** — default vs flipped label order | **r 0.7851, MAD 0.2745** |
| **sham** — one extra space, same words, same order | r 0.9853, MAD 0.0669 |
| affine residual per prompt | 0.0340 (only this can reorder) |

**The flip is 4.1× the whitespace sham and 33× the determinism floor** — it is label order, not
prompt fragility in general.

| quantity | default | flipped | verdict |
|---|---:|---:|---|
| **Q1** R231 core vs floor | 0.4120 vs 0.3846 (**+0.0274**) | 0.3560 vs 0.3664 (**−0.0104**) | **OVERTURNED — sign flips** |
| Q2 R252 redundancy sign | 205/41 · 234/14 · 229/21 | 193/41 · 221/26 · 215/32 | **CONFIRMED** |
| **Q3** R249 minimal size | 1.4680 | 1.6360 (**+0.1680 = 7.7× its own se**) | **DOWNGRADED gauge-dependent** |
| Q4 R256 λ₁ excess | 0.1432 | 0.1423 | **CONFIRMED** |
| Q4b R256 rank-1 class | 0.4320 | 0.4200 | **OVERTURNED** |

### The hierarchy of error on that one number, measured (R266)

Three axes were reported today and nobody asked **which binds**. They have different remedies —
draw noise is bought with compute, instrument noise is not bought with anything this release
carries.

| DRAWS | floor mean | seed spread | gap (core − floor) |
|---:|---:|---:|---:|
| 10 | 0.3819 | 0.0096 | +0.0045 |
| 20 *(R231's committed value)* | 0.3833 | 0.0075 | +0.0031 |
| 100 | 0.3835 | 0.0024 | +0.0029 |
| **200** | 0.3829 | **0.0034** | **+0.0035** |

| source | size | vs the residual |
|---|---:|---:|
| residual **draw** spread at 200 | 0.0034 | 1× |
| **label order** (R257) | 0.0378 | **11.1×** |
| **batch bf16 noise** (R260) | 0.0568 | **16.7×** |
| **the gap itself** | **+0.0035** | 1.0× |

**The effect is the same size as the smallest noise source and one sixteenth of the largest.** The
gap's sign is stable at `+` across all five draw levels once draw noise is removed — **and it is
still not resolvable**, because the two axes compute cannot touch are an order larger.

> ⛔ **"More draws would settle it" is forbidden.** What R231 needs is a second instrument, and the
> release does not carry one — R164's variant tensors cover the full and core sets, not the
> arbitrary subsets the floor draws from.

Controls: the forced `1/√DRAWS` law holds (2.82 against a predicted 4.47, a harness check and not
evidence); the floor's **mean does not drift** (0.0022 against the DRAWS=10 spread of 0.0096), so
`DRAWS` changes precision and not the estimand; `DRAWS=20` lands inside R262's measured band.

⛔ **Q1 is now overturned or unresolvable on THREE independent axes** — label order (here), measured
batch noise (R260: interval contains 0), and `PYTHONHASHSEED` (R261: the sign flips between seeds 2
and 3). Three unrelated sources of arbitrariness, one conclusion: **`0.3864` against `0.3836` was
never a comparison.**

**And exactly two quantities in this arc survive every gauge tested: R252's redundancy sign and
R256's λ₁ excess.** Neither instrument is privileged — a quantity that moves is `UNVERIFIED`, never
"right in the default".

Stable across all four instruments: `top4_pos − core` on humans is **null on all four**, and core
veto retention ≫ full_unit on all four. **Not** stable: above-chance retention (0.673–0.919), veto
retention magnitude (0.458–0.864), and the polarity sign.

Multiplicity: BH q=0.05 over **C=46** p-valued tests, **31 survive**, non-survivors listed. 120
specification rows carry no p-value and are published whole; `Λ_budget` spans [0.375, 0.477] and
**100% land in the same verdict band.**

---

## 10 · What the blind arm established that this arc never did — `SINGLE ARM`, R235, seed 29

Attributed, not absorbed. Design A has not returned and none of this is replicated here.

- **Compiler intelligence: ⛔ this line is RETRACTED by the other blind arm.** R235 measured
  `top-4-by-mean-weight` beating the official core in **76 of 286** cells, core in **0**, primary
  `−0.0224 [−0.0407, −0.0050]`, and concluded *"the compilation adds no selection value."*
  **R234 tested that target and it does not hold up**: the weights used to *select* top-4 are the
  same weights that *define* the target, so a subset is a sub-sum of the target's own basis. Select
  top-4 on a **disjoint annotator half** and the sign inverts — core **0.8182** vs top4 **0.8066**.
  The human arm is null, the K-sweep is null. **And the card documents `top4_pos` as the release's
  own selection rule**, so the comparison was the card restating itself.
  *Kept rather than deleted (L81): this is what a confounded target looks like when every number in
  it is correct.*
- **Extrinsic retention `0.855 [0.818, 0.890]`** — the share of the full rubric's agreement with human
  *world* rankings that survives compilation. A number this arc never produced.
- **The weight matrix is `39.7%` filled, and the score `0` is used once in `102,147` ratings.**
  *"Not rated" and "rated zero" are not distinguishable.* R235 carries both readings as separate
  specification cells and they give different answers (η 0.10 vs 0.25). **This is a missing-data
  semantics problem affecting every weighted claim in this repository, including mine.**
- **`personal` rankings cover `29.8%` of prompts** — a prompt-level split, so a valid subpopulation.
  Consistent with R220's 26.66% of *assessments*; different denominator, same restriction.
- **The rubric and prompt files share no key** — 0 of 986 IDs overlap; the join is rebuilt from prompt
  text, which `covalx/judge.py` documents and R235 rediscovered and positive-controlled at 966/966.
- **R235's own pre-registered negative control could not fail** and it said so: permuting the
  interaction residual preserves every column mean, so an unsigned uniform rubric — which scores by
  the *mean* — is unchanged in **47.2%** of prompts. **Same failure mode this arc hit four times,
  found independently, reported rather than buried.**

## What the official core scores against this, and why that is not an indictment

R236 issued the certificate as **NOT ADMISSIBLE, two fields FAILED** — ⚠ **and that header is now
stale, because the two bullets under it repair both fields it names.** `representative` was issued
by R249; `provenance` is ≥ 0.0777 by string identity (R250). The header stood for eight rounds and
then survived its own repair by three.

- `representative` **— the split now exists** (R249). Eight rounds repeated *"naming the split would
  pass the field"* without producing it, because R228's `k_max` describes the **space of candidate
  subsets** and the certificate needs a statement about **the four criteria that were printed.**
  Measured by exhaustive leave-one-out over the printed set, 967 prompts, r04 tensor:

  | | |
  |---|---:|
  | criteria printed per core | **3.95** |
  | necessary-within-set | **1.45 (36.7%)** |
  | minimal subset reproducing the core's own class | **1.42** |
  | prompts where **zero** printed criteria are necessary | **23.8%** |
  | prompts where **all** are | 5.4% |
  | minimal size = 1 | **642 of 967 (66.4%)** |

  **On two thirds of prompts a single printed criterion reproduces what all four produce.**
  Controls: a synthetic core of one discriminating + three constant criteria returns exactly
  `necessary=1, minimal=1` and flags the right one; four identical criteria return `0, 1`; the
  placebo (the minimal subset induces the core's own class) holds on all 967.

  ⚠ **PROXY LEDGER.** `necessary` is *necessary-within-the-printed-set*, never *identified among the
  `C(n,k)` alternatives* — R231 measured that separately at 0.3864 against a floor of 0.3836. Only
  **`redundant` is sound in both directions**: if the class does not move, that criterion
  contributed nothing to this observable, full stop.
- `provenance` **— `0.00` is RETRACTED** (R250). R232's query is intact and still holds: across all
  986 rubrics every `coval_core` item carries exactly one field, `criterion`. **But the absence of a
  lineage COLUMN was reported as the absence of lineage,** and that inference was never checked —
  including by me, one round ago, in a commit body that said the field *"cannot be repaired from
  this release."*

  Asked of the object rather than of memory: of **3,899** printed core items, **303 (7.77%)** are
  **verbatim string matches** to a criterion in their own prompt's full rubric, and **943 (24.19%)**
  reach token-Jaccard ≥ 0.6. Provenance is therefore **at least 0.0777**, established by string
  identity with no inference at all.

  Those 303 are also the first **ground truth** this arc has had for anything: their parent is known
  without a model. R250 calibrates how far a rewrite can travel before provenance stops being
  recoverable — 298 usable items, 14,304 judgements, chance `0.0792` (mean candidate set 14.43):

  | dose | text-Jaccard to parent | **behaviour route** | text route |
  |---|---:|---:|---:|
  | identity | 1.0000 | 0.9883 *(identity, not a test)* | 0.9883 |
  | drop 20% | 0.7995 | **0.3031** (± 0.0436) | 0.9883 |
  | drop 40% | 0.6000 | **0.1913** (± 0.0235) | 0.9871 |
  | drop 60% | 0.4014 | 0.1051 (± 0.0168) | 0.9855 |
  | first-clause truncation | 0.4621 | **0.2299** | 0.9883 |

  **Provenance is recoverable by judge behaviour alone at 2.4–3.8× chance out to 40% content-token
  deletion, and at 2.9× chance under first-clause truncation** — the direction R249 showed the
  compiler actually travels. It reaches chance around Jaccard ≈ 0.40, which is the MDE.

  ⚠ **The text route's flat 0.988 is not evidence.** Deleting tokens never *introduces* a
  competitor's tokens, so a subset of the parent stays nearer the parent than anything else — token
  deletion cannot kill a set-overlap matcher. Real rewriting **substitutes** words; this dose axis
  does not. Likewise **shuffle is a null perturbation for the text route** (Jaccard is set-based),
  which its `1.0000` distance column makes visible.

  **R251 added substitution and the text route still did not move** — 0.9883 / 0.9860 / 0.9696
  (rival 20/40/60%) and 0.9883 / 0.9883 / 0.9855 (generic), at Jaccard down to **0.2848**. Behaviour
  fell as before: 0.2366 / 0.1353 / 0.0755 and 0.2349 / 0.1387 / 0.0968 against chance 0.0792.
  Its distance control passed — every substitution dose moves the text further than matched
  deletion — and its negative control sat at chance on all seven doses.

  ⛔ **But R251's verdict called that "adversarial substitution" and it was not.** Its donor pool was
  the **union of every rival criterion**, so the injected tokens *scatter* and no single competitor
  can overtake the parent. **A set-overlap matcher is not beaten by noise; it is beaten by
  concentration.** Fifth conclusion-string failure in the session, same shape as the other four: a
  comparative asserted rather than computed. R254 runs the concentrated version — substitute toward
  the **single nearest rival** and measure the crossover — with both ends of its positive control
  pinned (`f=0` must return 0.9883; `f=1` must return ≈0 *and* name the rival as top hit). Running
  on GPU task 570.

  Controls: the ceiling is **computed**, not assumed — `0.9883`, because 7 of 298 parents have a
  duplicate in their own rubric and the 1/k tie rule makes exact 1.0 unreachable. *The first
  threshold demanded 1.0 and was the sixth control-that-cannot-pass in this arc.* The repaired
  negative control keeps the candidate set (parent reachable) and destroys the query: **0.077–0.089
  text, 0.047–0.055 behaviour, against chance 0.0792 — at chance at every dose.** *The first version
  matched against a different prompt's rubric, where the parent is absent, so its 0.0000 was forced
  by the candidate set.*
- `transport` **NOT_MEASURED** — requires a second candidate set. Now runnable; `UNVERIFIED` at R233
  because its own floors showed the arms differ in difficulty.

**And the redundancy is inherited from the WRITING, not from the SELECTION** (R249, W4 arm,
registered before it ran). Paired on the same 200 prompts:

| minimal sufficient size | mean |
|---|---:|
| the printed **core** | 1.3750 |
| random 4 from R240's **generic vocabulary** (real full-rubric criteria, chosen only for token genericness) | 1.3707 |
| random 4 from the **full rubric** | 1.6207 |

`core − generic = +0.0042 [−0.0870, +0.0955]` — CI contains zero.
`full-random − generic = +0.2500 [0.2077, 0.2923]` — it does not.

**Generic criteria agree with one another, and the compiler writes generic criteria.** That is a
different defect from "the compiler picks redundant criteria."

⚠ **But "generic TEXT" is the weaker of two mechanisms, and R255 measured both.** Over **14,687
within-prompt criterion pairs across 250 prompts** (`n_eff = 250`, not 14,687 — pairs inside a
prompt share their criteria), clustered bootstrap, 1000 resamples:

| predictor of behavioural agreement | ρ | CI95 |
|---|---:|---|
| **lexical** similarity (Jaccard) | **+0.0447** | [+0.0172, +0.0741] |
| the same, containment · Pearson · both | +0.0439 … +0.0481 | all nonzero, all tiny |
| **discrimination** — `min(sd across the 4 responses)` | **+0.1440** | [+0.1103, +0.1800] |
| sham: token-count difference | −0.0114 | [−0.0356, +0.0117] — contains 0 |
| negative: pairs across *different* prompts | −0.0002 | at its null |

**The CIs do not overlap: saturation beats lexis by 3.2×.** And the base rate is the striking part —
**the median lexical Jaccard between two criteria in the same prompt is `0.0000`**. Half of all
co-prompt pairs share *no content word at all*, yet their judgements agree. **Whatever makes this
rubric redundant, it is mostly not shared vocabulary.**

**And a fourth property was tried and retracted the same day.** R256 found a common factor above
its measured null (λ₁ excess **+0.1394**, permutation null 0.6210) but carrying the *decision* on
only **0.4440** of prompts. Its core-vs-full contrast — core 0.6000, full 0.4440 — **is a size
effect** (R258): the statistic falls **1.0000 → 0.6322 → 0.5458 → 0.5134 → 0.4886 → 0.4740** for
k = 1…6 **by construction**, because a 1-row subset *is* rank one. At matched size the core scores
0.6000 against random-4's **0.5134**, `+0.0866` inside a draw spread of **0.2148**. And the
cross-prompt sham tracks random almost exactly (0.5192 vs 0.5134) — **the statistic is structure-free
geometry of k rows in 4 dimensions.**

⛔ **And neither mechanism closes it.** R255's generic vocabulary is *less* discriminating than the
full rubric (0.0951 vs 0.1043), which fits saturation — but R234 measured the **core** as *more*
discriminating than the full rubric (`core/full sd = 1.1047`). **The core matches the generic
vocabulary on redundancy while differing from it on discrimination.** A third property is doing the
work and this arc has not named it. Residual gap, stated rather than smoothed.

⚠ **The pre-registered kill for that comparison was mis-scaled and is recorded `UNVERIFIED`.** It
compared a paired mean over 967 prompts (−0.2083) against a **per-prompt range over 20 draws**
(2.2378) — the same error this repository added to `realstat` as *"min/max of N draws quoted as an
interval"* three commits earlier, committed again while writing the round that cites it. The W4 arm
settles the question; the original threshold settles nothing.

**Every core is a choice of representative.** The official one is a defensible choice for the purpose
its dataset card states — a short readable summary. The certificate's job is to make the purpose and
the choice visible, not to score the object against a purpose it never claimed.

---

## The site's own MDE — what this release could ever have shown (R268)

Thirteen rounds measured what is not resolvable. This is the constructive form of the same
measurement, and it is the arc's real output.

**Detector calibrated empirically to α = 0.05 on 200 no-effect replicates, then validated on 200
FRESH ones it never saw: `α̂ = 0.0600`.** (R267's detector — `arm > max(3 floor draws)`, which is
**the comparison form R231 and R220 use** — fired at **0.2000** on the same test. That defect is
what this replaces.)

| g | mean arm | detect |
|---:|---:|---:|
| 0.00 | 0.3790 | 0.0800 |
| 0.06 | 0.4154 | 0.4300 |
| **0.10** | 0.4418 | **0.7700** |
| **0.12** | 0.4535 | **0.8600** |
| 0.20 | 0.5104 | 1.0000 |

> ### The site's MDE is **[0.1250, 0.1250]** in class-agreement units (R274; R268's `(0.10, 0.12]` was read off a 0.02 grid with a 200-draw calibration and is superseded **upward**).
>
> ### And the arc chose the coarser statistic: the HUMAN-ranking statistic's MDE is **[0.0260, 0.0300]** — the gap is **[4.17×, 4.81×]**, on the same release (R271 → R274).

⚠ **R270 measured that gap at 2× and said it missed its own 3× threshold. R271 supersedes it**: R270
collapsed each prompt's annotators to a consensus *sign* first, giving 5,808 rows over 968 clusters
(ratio 6). The real structure is **93,558 rows over 968 prompts, ratio 96.7**. With the per-annotator
rows the gap is **4.0×**, which clears the threshold R270 set and could not reach.

### And the clustering inflation, as an interval rather than a point (R273)

Resampling **prompts** vs resampling **rows** on the same statistic:

| | MDE | |
|---|---|---|
| prompt-clustered | **[0.0260, 0.0300]** | the honest unit |
| pooled-row | **[0.0100, 0.0110]** | the wrong unit, run deliberately |
| **inflation** | **[2.36×, 3.00×]** | against `√(rows/clusters) = 9.83` |

Each bound is *the range of g where a 95% CI on detection still contains 0.8* — no interpolation, no
monotone fit. **The realised inflation reaches only 24–31% of what independence predicts**, so
intra-cluster correlation is large and **`√(rows/clusters)` overstates what the wrong resampling unit
buys** — the opposite of the direction the rule is usually quoted in.

⛔ **R272's point estimate of 2.0× is RETRACTED — it lies outside this interval.** R272 concluded
that *the grid, not the calibration, was the limiting term*, and then quoted a number the grid had
produced: at a 0.005 step the pooled MDE read as `(0.010, 0.015]`, where a 0.001 step puts it at
`[0.0100, 0.0110]`. **The coarse grid did not merely blur the number, it biased it low.**

| published effect | value | effect/MDE | |
|---|---:|---:|---|
| R231 core−floor gap | 0.0035 | **0.03** | below |
| R249 paired se | 0.0219 | **0.18** | below |
| R257 label-order delta | 0.0378 | **0.32** | below |
| R260 batch interval | 0.0568 | **0.47** | below |
| **R249 minimal-size move under label order** | **0.1680** | **1.40** | **resolvable** |

**Exactly one quantity this arc ever reported clears the site's own detection floor — and it is a
measure of the INSTRUMENT moving, not of the object.** Every substantive effect is 3–30× below what
this release can show. *Today's downgrades were forced by the site, not by the individual rounds*,
and **E05's real output is a specification for a better instrument rather than a set of findings.**

Controls: **positive** — the largest dose is detected 1.0000 against g=0's 0.0800, clearing 3
binomial se (0.0814); the threshold is **computed from two measured numbers**, where R267's was
typed as `> 0.9` and the design returned exactly 0.9000. **Placebo** — identical arms at the same
seed differ by exactly `0.000000`.

⚠ **R268's sham was void — and repairing it (R269) confirmed the MDE rather than moving it.**
It re-randomised *which* prompts carry the plant, and the carrier was all-`True`, so permuting it was
a no-op: 0.7200 against 0.7700 at the same g. **And the obvious repair is void too** — prompts are
exchangeable, so permuting which exchangeable units carry an effect changes nothing in distribution
at *any* fill rate. **A sham must destroy something the statistic depends on, and "which prompt" is
not such a thing.**

Two replacements, and only one of them is a test:

| | | |
|---|---:|---|
| **SHAM-A** uniform shift of g on all four responses | **0.1100** vs α 0.0600 | ⚠ **FORCED** — a constant cannot move a sign. A *placebo* in a sham's name; it checks only that the class function is shift-invariant **as coded**. |
| **SHAM-B** the same g applied to the **TARGET** instead of the arm | **0.0200** vs real **0.7700** | **can fail, and did not** — detection collapses below α when the plant is aimed at the reference |

**SHAM-B is the one that matters**: had making the reference easier *also* raised detection, the
statistic would not be measuring the arm and the MDE would be void. It falls from 0.7700 to 0.0200.

⛔ **The label-order axis is deliberately NOT inside this MDE.** It is one alternative instrument,
not a distribution — folding its 0.0378 in would average a **bias** into a **variance**.

---

## What is `UNVERIFIED` right now, and stays that way until it is not

| | |
|---|---|
| candidate-set transport (R233) | ⛔ **the reason carries a RATE, not a verdict** (R263 → R264). R241 concluded *"NO VALID STRATIFIER EXISTS"*, and that null closed this line. Re-run over **24 hash seeds**, R241's **own controls pass on 15 of 24 = `0.6250`, Wilson `[0.4271, 0.7884]`** — an interval that **excludes 0.9**, which was the pre-registered threshold for "cannot be quoted without its rate". On the other 9 seeds it prints `UNVERIFIED — the correlation machinery did not pass its own controls`. **Conditional on the controls passing the conclusion is stable (1 distinct verdict across all 15)** — so R241 is not *wrong*, it is **unreadable on 37.5% of runs**, and nothing records which kind the published run was. Positive control: the int-keyed R230 is identical at all 24 seeds, rate exactly `1.0000`. R238's headline separately moves `+0.0976 … +0.1242` (27%) on the same axis |
| the two independent designs (R234, R235) | dispatched blind at seeds 11 and 29. **The reading rule was fixed before they were launched** and they will not be averaged |

## What no elicitation here can settle

- whether a `k ≤ 2` core is **useful** — identifiability is not utility, and utility needs a
  downstream task the release does not carry
- whether **humans** would endorse any of these classes on unseen responses — no labels exist
- whether a core reaches a **trained model** — no `Y` in the release
- three designs from one model family test **framing**, never **population**

## The sentences that can no longer be written

- *"The core preserves X% of the rubric."* — unfinished until `Q` is named.
- *"This release cannot identify a core."* — it cannot identify a **per-prompt** one.
- *"The compiler selected four criteria."* — it selected two it could have identified and two it
  could not, and nothing in the artifact tells them apart.
- *"Candidate-set generalisation is structurally undetectable here."* — the artifact was in this
  repository for six days while I said that four times.
- *"The positive control failed, so the instrument is broken."* — five times out of five, the
  instrument was fine and the threshold was impossible. In R248 the impossible threshold was a
  synthetic control that scored **below** the real data.
- *"Admissibility is `C(n,k) ≤ A_real`."* — I wrote that into the definition, defended it against
  its strongest confound, and then found it predicts nothing `n` does not. **A quantity can be real,
  survive its confound, and still be decorative in the place you put it.**
- *"The capacity gate is loose by 5.5×, so it is the wrong quantity."* — looseness is not evidence
  of wrongness when the tighter quantity is a function of the same variables.
- *"A global core transfers to prompts it was never fitted to."* — R240 printed it, R247 killed it
  off R240's own tensor, and R240's own negative control had already said the round was unreadable.
- *"The floor is 0.2983 [0.2567, 0.3467]."* — that bracket is the **min and max of 20 draws**, not a
  floor. Comparing to the max is over-strict, comparing to the mean is under-strict, and **only the
  draw distribution is a null.** Three rounds quoted the bracket as though it were an interval.
