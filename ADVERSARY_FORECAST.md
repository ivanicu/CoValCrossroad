# Adversary forecast — what I expect a clean-context reviewer to overturn

**Status of `PREREGISTRATION.md`: `[unchallenged]`, not clean.** Every experiment in it was designed,
attacked and repaired by the same process that wrote it. A reviewer sampled from the weights that
produced a document can only attack what that process already anticipated, which is exactly why the
anticipated parts read as fluent. No independent reviewer has read it.

I could not dispatch one in this session. The documented fallback is to say so, mark the work
unchallenged, and **write down in advance what an adversary should find** — because when one finally
runs, its findings score my calibration about my own work, and that is worth more than any individual
verdict. Recorded before any review, so it cannot be edited toward whatever comes back.

Confidence is my probability that an independent reviewer raises the objection **unprompted**.

---

## The six I expect

### 1 — δ = 0.01 is stipulated everywhere and connected to no decision · **0.85**

Every experiment reports significance and equivalence at δ = 0.01, the sweep is published, and the
stipulation is flagged in four places. **None of them says what decision changes at 0.01 that does
not change at 0.02.** A margin is supposed to encode "an effect this small would not alter what
anyone does" — and nobody ever wrote down the "anyone" or the "does". Flagging a number as
stipulated is not the same as justifying it, and the flag has been doing the work of the
justification.

*What would answer it:* name a decision — a deployment threshold, a rubric-acceptance rule — whose
outcome flips between 0.01 and 0.02, or drop the pretence and report the sweep as primary.

### 2 — "The unmatched rate is the measurement" conflates two failures · **0.80**  ·  ⚠ SELF-CONFIRMED AFTER FORECASTING

> [r62](rounds/r62_matching_floor) measured the within-arm floor **after** this forecast was
> committed: **87.3%** unmatched between two authors of the same prompt at Jaccard ≥ 0.20,
> **53.3%** at the most lenient threshold. The objection is upheld and the design changed —
> the unmatched rate is now reported as an excess over an in-study floor. **A scorer should
> count this raised-by-me and exclude it from the hit rate.** Forecast text unchanged below.

Experiment 1 promotes the PRE/POST unmatched rate from an exclusion to a primary outcome, arguing
that a POST criterion with no PRE counterpart is menu-induced construction. **It is also what a
vague, badly written, or idiosyncratic criterion produces.** The matcher cannot distinguish *"this
criterion could only arise after seeing responses"* from *"this criterion is too woolly to match
anything"*, and the design gives it no way to.

*What would answer it:* a criterion-quality rating collected alongside, so unmatched-and-clear can be
separated from unmatched-and-vague; or a within-arm matching baseline — how often do two PRE
participants' criteria fail to match **each other**? — which bounds the vagueness floor.

### 3 — the τ_c symmetric design assumes both edits are the same kind of object, and for many criteria they are not · **0.75**

This is the strongest attack I can see on my own work. The symmetric design rests on `R⁺` and `R⁻`
being *"the same kind of object"*, borrowed from r52 where both arms genuinely were — two token
lists, differing only in source. **A satisfy-edit and a violate-edit are frequently not symmetric at
all.** For *"contains no factual errors"*, satisfying is leaving the text alone and violating means
inserting a falsehood; for *"acknowledges uncertainty"*, satisfying adds a hedge and violating
deletes one. Insertion and deletion are different operations with different fluency signatures, and
a participant may respond to the operation rather than the criterion.

*What would answer it:* restrict to criteria admitting a genuine two-sided edit and report the
fraction excluded; or make both arms insertions of matched length — but that is not always
constructible, and where it is not, the design should say τ_c is not identified for that criterion
rather than estimating it anyway.

### 4 — Experiment 2's satisfaction sub-study is an escape hatch, not a design · **0.70**

It is specified as *"if that sub-study is not run, the primary result is reported as human rankings
against a model-scored rubric"*. **No n, no power, no sampling frame.** As written it can be skipped
and the headline merely reworded, which makes it a caveat wearing the costume of a commitment —
and this project has an entry (79) about exactly that move.

*What would answer it:* an n and a sampling frame, and a rule stating what agreement rate would
invalidate the primary analysis rather than annotate it.

### 5 — Experiment 1 has no power calculation at all · **0.65**  ·  ⚠ SELF-ANSWERED AFTER FORECASTING

> Addressed by [r61](rounds/r61_s_pre_power) **after** this forecast was written and committed,
> not before. The objection stood when recorded. **A scorer should count it as raised-by-me and
> exclude it from the hit rate**, since answering my own forecast item is not evidence about
> what an independent reviewer would find. The forecast text below is left exactly as written.

Experiment 2 carries reliability, attenuation and detection floors per rater count. Experiment 3 now
carries a flip-rate prior from r59. **Experiment 1 has "fixed n, decided from a pilot of 20
participants per arm"** and nothing else — no effect size it is powered for, no floor. It is the
experiment addressing S_pre, which this project calls one of three counterfactuals that end it.

*What would answer it:* the marginal-matched agreement baseline is computable from the release
today; the minimum detectable departure from it at plausible n should be in the document before the
pilot, not after.

### 6 — r60's "not answerable from this release" assumes the reversal rate is homogeneous · **0.55**  ·  ⚠ SELF-EXAMINED AND **NOT UPHELD**

> [r63](rounds/r63_r60_projection_audit) checked it **after** this forecast was committed. The
> design effect is **1.499** and was already inside r60's published CI; pairs come from 238 of
> 250 prompts; the release's growth is prompt-extensive, which is exactly the condition the
> √n step needs. **The objection does not bite.** Recorded as a forecast item that was worth
> raising and turned out negative — a forecast only means something if some of it is wrong.
> **A scorer should exclude this from the hit rate.** Text unchanged below.

The projection scales the observed half-width by √(n) to conclude that δ = 0.01 needs ~14,358
reversed pairs against 2,444 available. **The bootstrap clusters on prompt, so if reversed pairs
concentrate in a minority of prompts the effective n is well below the pair count** and the required
number is *larger* than stated — or, if a subset of prompts drives the signal, a targeted analysis
on those prompts could be better powered than the aggregate. Neither was checked.

*What would answer it:* the distribution of reversed pairs across the 250 prompts, and the design
effect implied by it.

---

## Two I expect to survive

Recorded so the forecast is falsifiable in both directions rather than a list of hedges.

- **The world-vs-personal finding (entry 88).** A reviewer may argue that using the world ranking was
  the *correct* default — the object is model behaviour, so the impartial ordering is the right
  target — and that calling it an omission overstates it. I expect the **documentation** finding to
  survive regardless: the choice was made in a helper function and stated in no reader-facing
  document, and 46.8% ordering disagreement makes it material whichever block is the right default.
- **The symmetric-pair fix to τ_c's manipulation check.** Objection 3 attacks its *constructibility*,
  not its logic. I expect the logic — that a base-vs-edited check is performed by an instrument known
  to respond causally to editing — to be upheld.

---

## How to score this

When an independent review runs: mark each of the six **raised / not raised**, note anything raised
that is **not on this list**, and compute the hit rate. **The unlisted findings are the number that
matters** — they measure what this process cannot see about itself, which is the whole reason the
door exists. A high hit rate on the six proves only that I can enumerate my own anticipated
weaknesses, which was never in doubt.
