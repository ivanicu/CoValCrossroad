# R351 — the drift is real and no published number moved

**The decision this makes safe:** whether R350's seven drifted rounds require any page to be
corrected. **They do not — at a stated precision floor, and by tracing every collision to its
true source.**

## Result

**27 differing leaves across the 7 CODE DRIFT rounds. 6 rendering collisions, across 2 distinct
leaves. Both refuted.**

| round | leaves differing | collisions |
|---|---:|---:|
| `R34_global_rater_crossfit` | 13 | **6** |
| `R36_channel_shapley` | 9 | 0 |
| `R102` · `R107` · `R115` · `R121` · `R328` | 1 each | 0 |

Most drift is **a single leaf**. Two rounds carry almost all of it.

## The two collisions, adjudicated by locating each page number in its *own* round's artifact

| page prints | I matched it to | it actually is |
|---|---|---|
| `② − ① = +0.0540` | `R34 .D_same … .ci[0]` = **0.05398465** | **`R347.ref_gap_mean` = 0.05403320** |
| `verbatim pairs 0.0191 apart` | `R34 .D_magnitude … .ci[1]` = **0.01907946** | **`R223.verbatim.err_vs_identity` = 0.01907966** |

The second is the instructive one: **two unrelated estimates, in different rounds, agreeing to six
decimals.** That is precisely how a rendering search manufactures a false identity — and why the
adjudication had to find each page number's *source*, not merely judge whether the match "looked
plausible".

**No published number moved.** Both collisions are real; neither identity is.

## Controls

| | returned |
|---|---|
| **DIFF, planted** | identical → 0 diffs; one perturbed leaf → exactly 1 |
| **SEARCH, planted, both directions** | present → found; absent → clean |
| **SEARCH, REAL** | `0.5665` — a value in a committed artifact *and* on the page — found |
| **ISOLATION** | of **767** artifacts present at the start, **0 changed, 0 vanished** |

### ⛔ Two defects in this round, both caught by its own machinery

**① The precision floor killed its own control.** At `MIN_SIGFIG = 4` the planted probe `0.0478`
— **three** significant figures — had every rendering discarded, so the search had nothing to look
for, while the real control fired on `0.5665`, which has four. And `0.0478` is not hypothetical: it
is **this campaign's own headline for the authoring effect**, printed in `FORMULATION.md`. *A floor
tuned on values near 0.5 makes every value near 0.05 invisible.*

The floor was doing two jobs and only one was its own. Spurious matching is a **substring** problem
— `0.51` inside `0.5123` — now handled where it belongs, by requiring the rendering to sit on a
**numeric boundary**. With that guard the floor drops to 3 and stops hiding an order of magnitude.

**② The verdict string asserted what only a read can settle**, then my correction to it contradicted
a count printed one line below. v1 announced `W2 — A NUMBER MOVED` the moment a rendering matched;
the search reports **collisions** and the claim is about **identity**. The fix said *"all of them are
one leaf"* while the same function printed **2 distinct**. Both are now computed, and the
adjudication traces each page number to the artifact that actually produced it.

## Register

| criterion | status |
|---|---|
| **precision floor** | 3 significant figures. A genuinely quoted 2-decimal number is **invisible** — this **under-counts**, so the zero is a bound, not a clean bill |
| **document scope** | `README.md` and `FORMULATION.md` only. A value quoted in a round's own README is not counted — the right scope for *published*, the wrong one for *written down somewhere* |
| **collision ≠ identity** | every hit is a CANDIDATE; only locating the page number's true source settles it, and that is a read, not a computation |

## The sentence I can no longer write

> *"seven rounds drifted, so seven published numbers are suspect."*

**Seven artifacts drifted. Zero published numbers moved** — at 3 significant figures, over two
documents.

Artifact: `results/r351_did_a_published_number_move.json`.
