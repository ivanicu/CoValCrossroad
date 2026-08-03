# What R240 will change — registered before it returns

**Written while task 554 is still judging.** The two blind designs have a reading rule fixed in
advance (`A08/README.md`); 554 does not, and a result whose reading is decided afterwards is a
result I will read as confirmation.

## The claim at risk

`FORMULATION.md` claim **6** is `DERIVED` and claim **7** is `OPEN`:

> **6** — the identifiability failure is a property of the per-prompt factoring; across 986 prompts
> the bits add to `[1006, 3402]` and a global core of `k ≤ 119` is identifiable.
> **7** — whether a global core *exists* is open.

**Claim 6 is about the channel. Claim 7 is about the object.** A channel with capacity for a signal
that is not there is a true statement about nothing, and R239 said so at the time.

## The prediction matrix, fixed now

| outcome of R240 | what it does to the formulation |
|---|---|
| **held-out agreement above the floor's best draw at ≥1 value of k** | claim 7 becomes `MEASURED`. **A global core exists and transfers to prompts it was never fitted to.** Claim 6 stops being a statement about capacity and becomes the explanation for why CoVal's per-prompt object was the wrong factoring. This is the strongest available outcome and I should distrust it accordingly |
| **held-out inside the floor at every k, fit-half above it** | the fitter works and there is **nothing to fit**. Claim 6 survives *as arithmetic* and is **demoted to irrelevant**: the bits add and no global core exists to use them. FORMULATION claim 6 gets an explicit "true and inconsequential" annotation |
| **fit-half also inside the floor** | `UNVERIFIED`. The positive control failed, the fitter cannot beat random on data it was fitted to, and **no held-out number is readable.** Nothing about claim 7 either way |
| **negative control non-null** (shuffled fit/eval still shows a gain) | `UNVERIFIED`, and worse — it would mean the split is not doing what a split does, and R240's design is wrong rather than its answer |

## What I expect, recorded so it can be wrong

**I expect the second row.** The bits add, and I expect no global core to be found — because R232
established that every `coval_core` item carries exactly one field and R239 established that of
15,058 criterion token-sets exactly **one** recurs across prompts. **Criteria in this release are
prompt-specific by construction, and a vocabulary chosen for genericness is still built from
prompt-specific text.**

If the first row happens instead, **that expectation was wrong and the finding is larger than the
formulation currently allows for.**

## What no outcome of R240 can establish

- that a global core is **useful** — no downstream task exists here
- that **humans** would endorse it — no labels for a global object exist
- that it transfers **beyond this release** — one site, and R242 just scored this arc at 46.9% of
  the standard it applies

## The one thing that would invalidate the round regardless of its number

The vocabulary was selected by **token document frequency across prompts** — the most
generic-sounding criteria — and selection was made **before** any satisfaction value was read. If
that turns out to have peeked at the outcome in any way, the round is void independent of what it
found. The selection code is `run.py` lines above the judge call, and it touches only `criterion`
text.
