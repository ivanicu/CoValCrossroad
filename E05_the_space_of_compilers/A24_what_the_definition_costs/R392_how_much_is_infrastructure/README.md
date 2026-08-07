# R392 — 72 of 226 are consumed as data, 23 more are only cited, and a "nowhere" token stopped being nowhere

**The decision this makes safe:** *how much of the backfill debt must NOT be paid?* **32% is
infrastructure another round reads.** The denominator moves, and it moves for a measured reason.

## Result — `W_SPLIT`. Four controls PASS. Two runs byte-identical. **No GPU spent.**

| channel | count | share |
|---|---:|---:|
| **artifact CONSUMED** — a real dependency | **72 of 226** | **32%** |
| name MENTIONED — citation *or* read | 74 of 226 | 33% |
| **mentioned but artifact NOT read** | **23** | — |

**Those 23 are what a merged detector would have wrongly excused from the debt.**

## ⛔ R391's detector had a flaw that did not matter at n=3 and would at n=226

It counted a round as consumed if another source named **either** its artifact **or** its directory.
Those are different relations. **Naming a directory is often a prose citation** — R21's own docstring
opens *"r15 and r20 both rest on a neighbour arm chosen by cosine"*, an argument **about** those
rounds, not a read of their output.

**Correcting R391 on its own three rounds:**

| round | artifact | name |
|---|---:|---:|
| R144_information_loss | **1** | 3 |
| R147_tracking_vs_serving | **0** | 1 |
| R150_does_the_veto_do_anything | **4** | 3 |

R391 reported R144 at "2 consumers" — **1 artifact read + 1 prose mention.** Its *conclusion* stands
(R144 is infrastructure); its *count* was inflated, and it is corrected here rather than quietly
superseded.

## ⛔ The negative control failed, and the reason is itself a finding

R391 used `zzq_no_such_artifact_zzq.json` as **its** nowhere-file. That string is now **in the
corpus** — inside R391's committed source — so searching for it returned **1 consumer**.

> **A corpus absorbs its own instruments.** A nowhere-token is only nowhere until a round uses it.

The control caught it because a nowhere-file with a consumer is impossible by construction. Token
replaced; **mechanism recorded rather than the string quietly swapped.**

## Controls

| | returned |
|---|---|
| **ARTIFACT (+)** | two edges committed **before this question**, by other rounds, for other purposes: `sat_genericpool16_fresh.npz` → R371, `r371_power.json` → R372. Both found |
| **ARTIFACT (−)** ⭐ | a filename existing nowhere → **0** consumers, after the absorbed token was replaced |
| **CHANNEL** ⭐ | the two channels must **differ**, or the split is decorative and the correction to R391 is unsupported. They differ by 23 |
| **SELF** | a round's own directory excluded from its own consumer set |
| reproducibility | two runs **byte-identical** (`e11cf046b06f`) |

## Register

| criterion | status |
|---|---|
| **dynamically-built paths** | **N/A** — invisible to a literal search. **The bias runs DOWNWARD**, toward *"not infrastructure, so backfill it"* — the direction that **creates** work rather than excuses it, which is the safer way to be wrong about a debt |
| **whether a consumed round also HAD a finding** | **N/A** — *being read and having something to say are different*, and only the second is what the debt is about |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"[HYPOTHESIS] I expect the infrastructure share to be large enough to change the denominator
> materially."*

**It is 32% — material, but far from the majority I expected, and 23 of the rounds I would have
called infrastructure are merely cited by someone's prose.**

Artifact: `results/r392_infrastructure_share.json`, source-stamped.
