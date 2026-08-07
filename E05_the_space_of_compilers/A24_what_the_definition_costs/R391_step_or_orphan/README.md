# R391 — two of the three silent rounds are infrastructure; one is an orphan

**The decision this makes safe:** *should the silent rounds be backfilled?* **Two must not be — they
are steps other rounds consume. One has no consumer this instrument can see.**

## Result — `W_MIXED`. Both controls PASS. Two runs byte-identical. **No GPU spent.**

| round | consumers | artifact | disposition |
|---|---:|---|---|
| **R150_does_the_veto_do_anything** | **4** | `veto.json` | **infrastructure** |
| **R144_information_loss** | **2** | `information_loss.json` | **infrastructure** |
| **R147_tracking_vs_serving** | **0** | `tracking_vs_serving.json` | orphan *(by this instrument's reach)* |

R150 is read by `R133_the_veto`, `R173_why_people_veto`, `R314_silence_was_read_as_endorsement` and
`assurance/consistency.py`. **My R390 hypothesis — that R150's 0.4 s runtime is the profile of a
lookup, not an experiment — is supported by four independent consumers.**

> **Marking a consumed round "no finding" would retract work that was never wrong, and writing a
> finding for it would invent a result for a script never asked to produce one.**

## ⛔ The instrument is a search, so its control has an answer I did not produce here

*"Grep for anything that reads their artifacts"* is the class this campaign has been burned by four
times. The control uses **two consumption edges committed before this question existed**, for a
different purpose:

| edge | found |
|---|---|
| `sat_genericpool16_fresh.npz` → read by **R371** | ✓ |
| `r371_power.json` → read by **R372** | ✓ |

And a filename that exists nowhere returns **0** consumers — so zero is shown attainable rather than
assumed. **Self-references are excluded**, or every round would score as its own consumer.

## ⚠ The blind spot biases toward the flattering answer

A consumer that builds its path **dynamically**, or reads through a helper, is invisible to a literal
search. So **`0 consumers` is a bound on what this instrument can see, never a proof that nothing
reads it** — and *orphan* is the verdict that lets a round close a question, which is exactly the
direction to distrust.

**R147 is therefore `no consumer found`, not `no consumer`.**

## Register

| criterion | status |
|---|---|
| **dynamically-built paths** | **N/A** — invisible to a literal search, and the bias runs toward ORPHAN. Named, not waved at |
| **whether a consumed round HAD a finding** | **N/A** — *being useful and stating a finding are different*, and only the second is what the backfill debt is about |
| **the other 60 untitled rounds** | **N/A** — R390 ran 8 of 68; this classifies the 3 silent ones among those 8 |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"[HYPOTHESIS] I expect at least one of R144, R147 and R150 to be a STEP rather than a result."*

**Two of three are, with 2 and 4 named consumers — so the debt shrinks by two for a recorded reason
rather than by a judgement call. The third has no consumer this search can reach, which is a
statement about the search as much as about the round.**

Artifact: `results/r391_step_or_orphan.json`, source-stamped.
