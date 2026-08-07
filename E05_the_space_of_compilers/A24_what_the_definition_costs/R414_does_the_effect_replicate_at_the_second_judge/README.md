# R414 — UNVERIFIED. The second judge cannot rank, and an escape hatch in my own kill nearly published a false retraction.

**The decision this makes safe:** *can the 0.8B judge host a cross-model replication?* **No — and the
reason is that it does not rank, which is not what "nothing is admitted" was ever saying.**

## Result — `UNVERIFIED_JUDGE_CANNOT_RANK`. **No GPU.**

| | e | se | d | |
|---|---:|---:|---:|---|
| **`full` (INSTRUMENT CONTROL)** | **−0.055843** | — | **−0.377** | **FAIL** |
| `coval_core` at 0.8B | −0.018812 | 0.004313 | −0.140 | *recorded, not concluded* |
| `topw_k4` at 0.8B | −0.022478 | 0.004884 | −0.148 | *recorded, not concluded* |
| `coval_core` at 2B (R408, committed) | **+0.009002** | 0.003703 | +0.078 | |

**`full` is the complete rubric — the target's own source. The 0.8B judge ranks it BELOW a blind
16-criterion subset.** A judge that cannot put the rubric above a blind draw cannot host any
comparison, so **the negative on `coval_core` is silence about the core and a statement about the
judge.**

## ⛔ The escape hatch was in my own pre-registered kill

I wrote:

```
if family_identity_resolved and (oracle_positive_at_08b IF ORACLE USABLE) and pool_nonempty:
```

**That parenthesis let the round proceed with no instrument control at all.** The two 0.8B naming
families turned out **not** to be the same run (`topw_k4` differs across `sat08_*` and `*_08b`), so
the oracle file could not be mixed with this pool — and the condition simply evaporated.

**Without the repair this round would have published `W-SIGN-FLIP`:** *"the released core does not
beat the blind maximum at the second judge, so +0.009 is judge-specific."*

> **That would have been a false retraction — the most expensive kind of error, because a cheap attack
> that appears to kill a claim retracts something true and nobody re-examines a withdrawn claim.**

The repair used an arm that **is** in the same family: `full`. It is a **weaker** positive than an
oracle — it does not *read* the rankings, so it bounds *"can this judge rank"* and not *"can it detect
leakage"* — and that is stated rather than glossed.

## ⛔ What this actually settles about R358/R359

They reported *"at 0.8B nothing is admitted at any safe reference."* I treated that as a claim about
**admission** (a binary) that left the **continuous effect** unexamined — which was right, and the
continuous effect was worth looking at.

**But the answer is not "the effect is negative there."** It is that **the judge does not rank**, and
*"nothing admitted"* was the visible symptom of that. **R358/R359's number was correct and its natural
reading was too generous to the instrument, in both directions.**

## Controls

| | returned |
|---|---|
| **FAMILY (=)** ⭐ | `topw_k4` exists in **both** naming families, 968 shared prompts — **not identical**. So they are different runs, mixing is forbidden, and the round restricted to `sat08_*` **before** any effect was computed |
| **INSTRUMENT** | `full` must outrank the blind maximum at any judge that can rank — **e = −0.0558, FAIL** |
| **POOL** | 968 prompts, 16 criteria, matching the 2B run's prompt count |
| **SCORING** | `load_sat`/`load_targets`/`yvec`/`cls` **imported** from the module R360 and R408 use |

## What survives, and what does not

- **R408's +0.009 at 2B is untouched.** It was not attacked here; the attack was ruled inadmissible.
- **Cross-model replication remains unavailable on this box** — but now for a *measured* reason with a
  named failing control, rather than by citing a binary verdict.
- **A third judge would need a scoring pass**, i.e. the GPU.

## The sentence I can no longer write

> *"the effect reverses at the second judge, so it is judge-specific"* — **the second judge ranks the
> full rubric below a random blind draw.** Nothing measured against it means anything, in either
> direction, and I was one repair away from publishing the opposite.

Artifact: `results/r414_second_judge.json`, verdict `UNVERIFIED_JUDGE_CANNOT_RANK`, exit 1.
