# R348 — it is CURATION, not blindness

**The decision this makes safe:** *may the page say a criterion set that never reads the conversation
beats a random draw of that conversation's own criteria?* **No.** That is true of the **curated
16-criterion pool** the clause-② reference draws from. It is **false** of criterion sets that never
read the conversation in general.

## What I published two rounds ago, and why it was wrong

R347 put this on the front page and in `FORMULATION.md`:

> *"A criterion set that never reads the conversation beats a random draw of that conversation's own
> criteria, on every arm."*

The clause-② reference is `sat_genericpool16.npz` — **sixteen generic criteria authored for the
benchmark.** It is a **curated instrument** that happens not to read the specific conversation.
*Blind* and *curated* are two properties, and I generalised the second into the first.

R287 had already flagged the same axis in its own words — *"the stricter the baseline's budget, the
harder the clause, and no round in this campaign has ever stated what budget a baseline SHOULD
have"* — and I did not check it before writing the sentence.

## Result — `c1` = A2(arm) − the clause-① reference (random draw from **this** prompt's own rubric)

| arm | k | c1 | MDE | verdict | class |
|---|---:|---:|---:|---|---|
| `coval_core_sham` | 4 | +0.0029 | 0.01518 | inside the MDE | crowd, blind |
| `full_sham` | 15 | **−0.0323** | 0.01522 | **resolvably WORSE** | crowd, blind |
| `gen_sham` | 4 | −0.0099 | 0.01655 | inside the MDE | crowd, blind |
| `promptecho_sham` | 4 | **−0.0441** | 0.02517 | **resolvably WORSE** | crowd, blind |
| `topw_k4_sham` | 4 | −0.0018 | 0.01534 | inside the MDE | crowd, blind |
| `generic` | 4 | **+0.0587** | 0.01436 | resolvably better | **curated**, blind |
| `topw_k4` | 4 | +0.0715 | 0.01281 | resolvably better | read the prompt |
| `coval_core` | 4 | +0.0738 | 0.01316 | resolvably better | read the prompt |

**Crowd criteria applied to the wrong conversation: 0 of 5 resolvably better, 2 resolvably worse,
mean c1 −0.0170.** The curated pool beats the own-rubric draw by **+0.0587**.

**Blindness is not the advantage. Curation is.**

## Controls

| | returned |
|---|---|
| **POSITIVE** — class A (`generic`, curated + blind) must be resolvably better | **+0.0587, PASS** |
| **DIRECTION** — arms that *did* read the prompt must also be resolvably better | `topw_k4` +0.0715, `coval_core` +0.0738, **PASS** |
| **g=0** — an arm equal to the reference must land inside the MDE | **PASS** |

The direction control separates *"the contrast can return positive"* from *"the contrast returns
positive for blind sets"* — the instrument's unit and the claim's unit, which is exactly the pair
this campaign has confused before.

**No permutation null.** The question is the *sign of a contrast against a fixed reference*, not
whether a pairing matters; a permutation would answer a question nobody asked.

## ⚠ Scope — and it makes the finding conservative

A `*_sham` arm is **selected** criteria applied to the wrong conversation, not a **random** draw from
another conversation's rubric. So class B is biased **upward** as a proxy for *"a crowd rubric that
never read this prompt"* — and even so it does not beat the own-rubric draw.

A true random cross-prompt draw is **not scored on this release**; it would need the satisfaction
layer recomputed for criteria against conversations they never saw.

## What this changes about the definition

Clause ②'s reference is hard because it is a **curated instrument**, not because it is blind. So the
clause is doing something narrower and more contingent than the page implied: it asks whether a core
beats *a good generic rubric*, and how good that rubric is was a design choice nobody registered.
**R287's unanswered question — what selection budget a baseline should have — is now load-bearing for
the whole clause-② boundary.**

## The sentence I can no longer write

> *"a criterion set that never reads the conversation beats a random draw of that conversation's own
> criteria."*

Artifact: `results/r348_blindness_or_curation.json`, census `sha256[:16] ac06c51261654769`.
