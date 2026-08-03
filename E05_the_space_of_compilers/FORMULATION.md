# What a "core" is — the formulation, stated once

*Every claim carries its round and its status. Nothing here is asserted without one.*

**Status vocabulary.** `DERIVED` — forced by the algebra, labelled as such, evidence of nothing on
its own. `MEASURED` — with population, instrument, baseline, regime. `UNVERIFIED` — the measurement
ran and its controls did not behave; never an acquittal. `OPEN` — running now.

---

## The definition

> **A core is a quadruple `(Q, class, representative, certificate)`.**
>
> | | |
> |---|---|
> | `Q` | the declared family of questions the downstream system must answer |
> | `class` | `[N]_Q` — the equivalence class of behaviours under `Q`. **This is the object.** |
> | `representative` | the criteria actually printed. **A choice, not a measurement.** |
> | `certificate` | which is which, at what noise, on whose instrument, and what was not measured |
>
> **Admissible only if** `log₂ C(n,k) ≤ log₂ A_real(Q, data)`, where `A_real` is the alphabet the
> data **realises** — the number of distinct `Q`-classes actually induced by the `C(n,k)` candidate
> subsets — **not** what the observation space could hold.
>
> ⚠ **Superseded 2026-08-03 (R248).** Until then this line read `log₂|H(Q)| ≤ H_eff` with `H_eff`
> taken from channel capacity (`log₂ a(m) = 6.2288` bits at m=4, later R237's noisy bracket).
> **Capacity is necessary and never sufficient**, and the gap is not small: measured over 250
> prompts the median `admitted / A_real` is **1.33 / 4.67 / 5.77** at k = 1 / 2 / 3, reaching
> **10.71** at the ninth decile. The capacity gate *admits* k=1 and k=2; the realised alphabet
> **refuses both.**
>
> **And admissibility is a RATE, not a predicate.** The share of size-`k` cores this release can
> identify is **U(1) = 0.5714 · U(2) = 0.0606 · U(3) = 0.0105**. A binary gate has to round that to
> yes or no; the object it is describing does not.

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
of **0.3836 [0.3657, 0.4019]** — inside the floor's own spread. On `Q =` predict human pairwise
preferences (R220), **0.6602** against a random range of **0.645–0.659** — clearly above. Same data,
same judge, opposite verdicts. **Reporting a preservation percentage without naming `Q` reports a
choice.**

⚠ **Corrected 2026-08-03 by the blind arm.** R243 swept `Q`'s granularity and the sign flips between
requiring **6 of 6** pairwise relations and **5 of 6** — so granularity explains the *sign*. It does
not explain the *magnitude*: my graded endpoint is `+0.0068` and R235's is `+0.2466`, 36×. **A second
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

**5 · The bound must use the noisy channel — and even that is the wrong axis.** `MEASURED`, as a
bracket (R237), **superseded as the gate by claim 8** (R248)
`H_eff ∈ [1.02, 3.45]` bits at the release's noise and rater count, against the `6.23` five rounds
assumed. `k=1` needs `3.91`, so **a one-criterion core sits at the edge of the bracket.** Partially
identified, so bounds and not a point.

⚠ R237 sharpened the *capacity* — how much the channel delivers under noise. R248 showed capacity is
the wrong quantity at any sharpness: the binding constraint is how many classes the **rubric**
separates, which is a property of the criteria's mutual agreement and is invisible to every channel
argument. `H_eff` stays as the noise correction it is; it is no longer the gate.

**6 · The failure is the per-prompt factoring, not the data volume.** `DERIVED` (R239)
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

**8 · The binding constraint is the rubric's own redundancy, not the channel.** `MEASURED` (R248)
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

Consequence for the definition: a capacity argument cannot see redundancy, so no amount of
sharpening `H_eff` reaches the real constraint. Two rubrics with identical `n`, `m` and noise have
different `A_real`, and only the second number predicts whether a core is recoverable.

⚠ **This round's first positive control could not pass, and repairing it produced the result.** It
demanded `A_real = C(n,k)` from a "maximally separated" synthetic prompt — but a class is a **weak
ordering**, a quotient of the sum vector, so distinct sums need not give distinct classes and no
construction in vector space forces the quotient injective. It returned **10 of 28** at k=2 while a
real prompt returns **12**: *the synthetic bracket sat below the data it was built to bound.* The
replacements are a k=1 case where the ceiling is constructible (exact, passes) and an independent
recount through a second code path (exact agreement, 25 prompts × 3 k). **Fifth
control-that-cannot-pass in this arc, and the first whose repair was the finding.**

---

## 9 · The triple blind, read under the rule fixed before it ran — `BOTH ARMS IN`

`A08/README.md` fixed the reading before either agent was launched: *all three agree → design
independent · agree on sign, differ on size → the spread is the finding · **disagree on sign → the
framing is the finding, find the assumption they differ on and test that** · **the three will not be
averaged.***

**They disagree on sign. And the assumption they differ on is not a design choice — it is WHAT THE
CORE IS SCORED AGAINST.**

| arm | target | core vs a top-*k*-by-weight heuristic |
|---|---|---|
| **R234** (seed 11) — *primary*, `Φ` | the full rubric's own signed-weight pairwise ordering | **top4_pos beats the core by +0.0352** |
| **R235** (seed 29) | rubric-to-rubric | **top-4-by-mean-weight beats the core in 76 of 286 cells, the core wins 0** |
| **R234** (seed 11) — *secondary* | **the humans' own `world` rankings** | **core 0.6593 ≥ top4_pos 0.6547**, `d = −0.0046` `[−0.0122, +0.0029]` |
| **R231** (mine) | Full's exact weak-ordering class | core 0.3864 vs a random-4 floor 0.3836 — inside. **I never ran a top-*k*-by-weight arm at all** |

**The two blind arms AGREE with each other on the rubric-to-rubric target. The sign flips only when
the target changes from the full rubric to the people.** That is claim 2, arrived at by a designer
who was never told claim 2 existed — and R234 named the reason *in its own pre-registration, before
any number*:

> *"the comparison is rubric-to-rubric, NOT rubric-to-human. Comparing each rubric to human rankings
> confounds compilation loss with the judge's own error at predicting humans, and that error is
> large."*

**And R234's budget curve says something no arm of mine produced**: against the humans, the core is
not beaten by *any* top-*k*-by-positive-weight heuristic for k = 1…10 — `top1 0.6245 · top4 0.6547 ·
top5 0.6560 (best) · top10 0.6406`, against the core's **0.6593**. The CI contains zero, so the
honest statement is **not-worse, never better** — but *not-worse against people* while *worse against
the rubric* is exactly the asymmetry the arc has been missing.

**R234's own primary verdict is against the core**: `Λ = 1.1420`, read as
`budget=PARTIAL / reliability=INADMISSIBLE(>1) / prereg=INADMISSIBLE(>1)`, with a **measured**
ceiling (split-half annotator reproducibility) rather than an assumed one — and `Λ_rel = 1.0596 > 1`
means the core agrees with the full rubric *more* than the full rubric agrees with itself, which A
reads as inadmissible rather than as a win. Three seeds: 1.1413 / 1.1483 / 1.1365.

⚠ **R234 also warns off the decomposition I would have quoted.** Its `artifact_checks` matches
criteria on length and on discrimination to see what explains the `Φ` gap, and reports its own
size-matched sham beside every number: *"A restriction to a smaller candidate pool lowers Φ by
itself. Any 'the covariate explains the gap' claim must be net of the size-matched sham, or it is a
claim about pool size."* Net of that sham, length explains **+20.5%** of the gap and discrimination
explains **−53.3%** — so **neither covariate cleanly explains it**, and the raw drop from `+0.0352`
to `+0.0028` after matching is mostly pool size.

**This does not overturn R249.** R249 measured *redundancy* against a generic-vocabulary control and
found the compiler's redundancy is inherited from the text it writes. R234 measured a *performance
gap* and found length/discrimination do not account for it. Different quantities, and both hold.

---

## 10 · What the blind arm established that this arc never did — `SINGLE ARM`, R235, seed 29

Attributed, not absorbed. Design A has not returned and none of this is replicated here.

- **Compiler intelligence: OVERTURNED.** `top-4-by-mean-weight` beats the official core in **76 of
  286** specification cells and the core beats it in **0**. Primary cell `−0.0224 [−0.0407, −0.0050]`.
  **The compilation adds no selection value over the single most obvious heuristic.**
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

R236 issues the certificate: **NOT ADMISSIBLE, two fields FAILED.**

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
different defect from "the compiler picks redundant criteria", and it is the one the data supports.

⚠ **The pre-registered kill for that comparison was mis-scaled and is recorded `UNVERIFIED`.** It
compared a paired mean over 967 prompts (−0.2083) against a **per-prompt range over 20 draws**
(2.2378) — the same error this repository added to `realstat` as *"min/max of N draws quoted as an
interval"* three commits earlier, committed again while writing the round that cites it. The W4 arm
settles the question; the original threshold settles nothing.

**Every core is a choice of representative.** The official one is a defensible choice for the purpose
its dataset card states — a short readable summary. The certificate's job is to make the purpose and
the choice visible, not to score the object against a purpose it never claimed.

---

## What is `UNVERIFIED` right now, and stays that way until it is not

| | |
|---|---|
| candidate-set transport (R233) | its floors say fresh responses are *easier* for everyone; the arms are not comparable as built. R238 is the difficulty-matched control, waiting on 553's tensor |
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
- *"A core of size k is admissible because C(n,k) ≤ a(m)."* — that is the **necessary** condition,
  loose by up to 10.71× here. Admissibility is `C(n,k) ≤ A_real`, and it is a **rate**, not a yes.
- *"A global core transfers to prompts it was never fitted to."* — R240 printed it, R247 killed it
  off R240's own tensor, and R240's own negative control had already said the round was unreadable.
- *"The floor is 0.2983 [0.2567, 0.3467]."* — that bracket is the **min and max of 20 draws**, not a
  floor. Comparing to the max is over-strict, comparing to the mean is under-strict, and **only the
  draw distribution is a null.** Three rounds quoted the bracket as though it were an interval.
