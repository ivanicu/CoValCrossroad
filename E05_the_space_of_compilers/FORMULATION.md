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

## 9 · What the blind arm established that this arc never did — `SINGLE ARM`, R235, seed 29

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

- `representative` **FAILED** — 4 printed, at most 2 identifiable (R228). **The artifact does not
  distinguish identified items from chosen ones. Naming the split would pass the field without
  changing a single criterion.**
- `provenance` **FAILED** — `0.00`. Across all 986 rubrics every `coval_core` item carries exactly one
  field, `criterion` (R232).
- `transport` **NOT_MEASURED** — requires a second candidate set. Now runnable; `UNVERIFIED` at R233
  because its own floors showed the arms differ in difficulty.

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
