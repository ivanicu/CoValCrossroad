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
> **Admissible only if** `log₂|H(Q)| ≤ H_eff`, where `H_eff` is what the *channel delivers*, not what
> the observation space could hold.

---

## The seven claims it rests on

**1 · The class is always identifiable; the member never is.** `DERIVED` (R230)
`|{classes under Q}| ≤ |{observations}|` by construction, because `Q`'s classes are *defined* by the
observation. Measured consequence: 72 subsets per prompt collapse into **13** classes, 5.2:1, never
above the forced bound of 75. Class recovery **1.0000** at zero noise (an identity, labelled),
**0.3233** at the release's own rater noise, against the member's **0.0613**.

**2 · The answer is a function of `Q`, and the sign can flip.** `MEASURED` (R231)
On `Q =` reproduce Full's weak ordering, the official core scores **0.3864** against a random-4 floor
of **0.3836 [0.3657, 0.4019]** — inside the floor's own spread. On `Q =` predict human pairwise
preferences (R220), **0.6602** against a random range of **0.645–0.659** — clearly above. Same data,
same judge, opposite verdicts. **Reporting a preservation percentage without naming `Q` reports a
choice.**

**3 · Adding raters does not raise the within-prompt channel.** `MEASURED` (R225)
Recovery gain from keeping individual rankings instead of the consensus: `+0.019` at R=14 against a
seed spread of `0.06` — inside. It fires only at R=2, where the consensus is itself degenerate.
Three estimands were needed to establish this; the first two failed because *tie-count saturates at
both ends*, and the decisive bug was caught by arithmetic, not by a control.

**4 · Precision does not close the gap; independence does.** `MEASURED` (R227)
A 10-point score beats a ranking by `+0.5607` at zero noise and `+0.0118` at the noise level
calibrated to the release's own 47.8% two-rater agreement — **inside** a seed spread of `0.0296`. A
47× difference between the regime the capacity argument assumed and the one that applies.

**5 · The bound must use the noisy channel.** `MEASURED`, as a bracket (R237)
`H_eff ∈ [1.02, 3.45]` bits at the release's noise and rater count, against the `6.23` five rounds
assumed. `k=1` needs `3.91`, so **a one-criterion core sits at the edge of the bracket.** Partially
identified, so bounds and not a point.

**6 · The failure is the per-prompt factoring, not the data volume.** `DERIVED` (R239)
Within a prompt the bits do not add; across 986 prompts they do — `[1006, 3402]`. A **global** core
of up to `k=119` is identifiable at the conservative end while a per-prompt core of **2** is not.
The independence assumption was checked: of 15,058 distinct criterion token-sets, **one** appears in
more than one prompt. **CoVal ships the per-prompt object.**

**7 · Whether a global core exists is `OPEN`.** (R240, running)
The bits are there. Whether there is anything for them to identify is being measured on 160,000
judgements, fitted on half the prompts and evaluated on the other half.

---

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
- *"The positive control failed, so the instrument is broken."* — four times out of four, the
  instrument was fine and the threshold was impossible.
