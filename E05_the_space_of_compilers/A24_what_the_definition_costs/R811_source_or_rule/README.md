# R811 · source and rule are the same size — clause ② needs two baselines, and one of them was a 96th-percentile draw

`run.py` · `PREREGISTRATION.txt` · `results/source_or_rule.json` · 968 prompts, common intersection
734 × 4 k × 3 seeds × up to 12,870 pool subsets · **WORLD C** — the branch that makes the definition
more expensive · two hash seeds byte-identical, md5 `389b5b4f6a2b1622e608ff1230f97c39`

## THE DECISION THIS MAKES SAFE

**R810 asked whether clause ② names one baseline or two. The answer is two**: informative selection
and prompt-specific sourcing buy the same order of advantage, and neither dominates.

| k | RULE (informative − uninformative, within the rubric) | SOURCE (generic pool − rubric, both uninformative) |
|---:|---|---|
| 2 | **+0.0752 [+0.0651, +0.0851]** | **+0.0568 [+0.0468, +0.0664]** |
| 4 | +0.0743 [+0.0646, +0.0829] | +0.0503 [+0.0390, +0.0613] |
| 8 | +0.0699 [+0.0619, +0.0780] | +0.0436 [+0.0320, +0.0552] |
| 12 | **+0.0419 [+0.0353, +0.0479]** | **+0.0372 [+0.0253, +0.0491]** |

> **at k=12 the difference is +0.0047 [−0.0073, +0.0173] — it contains zero.**

## ⭐ AND THE SOURCE EFFECT POINTS THE WRONG WAY FOR THE DEFINITION

**A fixed generic list of 16 criteria, blind to the prompt, beats a random subset of the prompt's own
rubric by +0.0372 to +0.0568 at every matched k.** Under an uninformative rule, prompt-specificity is
a **liability**. D3 was written before the run precisely because that is the opposite of what
clause ② assumes.

| k | rubric/uninformative | rubric/informative | pool/uninformative | `POOL[0:k]` | `full` |
|---:|---:|---:|---:|---:|---:|
| 2 | 0.4823 | 0.5574 | 0.5390 | 0.5556 | 0.5134 |
| 4 | 0.4946 | 0.5689 | 0.5449 | 0.5568 | 0.5134 |
| 8 | 0.5036 | 0.5735 | 0.5472 | 0.5497 | 0.5134 |
| 12 | 0.5109 | 0.5528 | 0.5482 | 0.5482 | 0.5134 |

⚠ **One cell of the 2×2 is structurally absent and is named rather than dropped**: `pool ×
informative` cannot be built, because the pool is a **fixed generic set of 16 identical across
prompts** (verified: 1 distinct criterion-list over 50 prompts) and carries no per-prompt importance
scores. It would require a release that weights them.

## ⛔⛔ E3 · THE BLIND BASELINE THIS ARC HAS BEEN USING IS A 96th-PERCENTILE DRAW

`POOL[0:k]` is **one arbitrary subset** — the first k in file order — and R810 and earlier rounds
used it as *the* blind baseline. The pool is fixed across prompts, so the uninformative-rule cell is
the **distribution over k-subsets of 16**, and the first-k's position in it is measurable. It was
**exactly enumerable at every k**:

| k | subsets | exact? | subset mean | sd | range | `POOL[0:k]` | **percentile** |
|---:|---:|---|---:|---:|---|---:|---:|
| 2 | 120 | yes | 0.5390 | 0.0115 | [0.5136, 0.5638] | 0.5556 | **95.8%** |
| 4 | 1,820 | yes | 0.5449 | 0.0075 | [0.5216, 0.5628] | 0.5568 | **96.0%** |
| 8 | 12,870 | yes | 0.5472 | 0.0046 | [0.5293, 0.5595] | 0.5497 | 69.2% |
| 12 | 1,820 | yes | 0.5482 | 0.0029 | [0.5374, 0.5564] | 0.5482 | 50.9% |

**At k=2 and k=4 the "blind pool" is a near-best draw from its own family**, stronger than a typical
subset by **+0.0166** and **+0.0119**. ⭐ **The direction matters and it is not flattering to state
it:** because the baseline is unusually strong, every "beats the blind pool" gap this arc reported at
small k is **understated** — the correction makes prior claims *larger*, which is exactly the kind
that has to be said out loud rather than quietly banked. At k=12, where R810 drew its headline, the
first-k sits at the **50.9th** percentile and needs no correction.

## E4 · R810's QUESTION, ANSWERED DIRECTLY

| k | `topw_k` − `POOL[0:k]` | |
|---:|---|---|
| 2 | +0.0018 [−0.0087, +0.0116] | holds 0 |
| 4 | +0.0121 [+0.0024, +0.0221] | RESOLVED |
| 8 | +0.0238 [+0.0146, +0.0336] | RESOLVED |
| 12 | +0.0046 [−0.0054, +0.0142] | holds 0 |

**Non-monotone, and resolved only in the middle** — and E3 explains the shape: at k=2 and k=4 the
comparison is against a 96th-percentile pool, at k=12 the rule effect itself has shrunk toward its
forced zero.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | R810's k=12 cells reproduced on the same population: `topw_k12` **0.552830**, `random_k12_s0` **0.515424**, `POOL[0:12]` **0.548235** | PASS, else exit 2 |
| PLACEBO | the pool's first-k against **itself**: `0.0e+00` at all four k | PASS — exactly 0 |
| POSITIVE | D1, the rule effect must shrink as k → n: **+0.0752 · +0.0743 · +0.0699 · +0.0419** | PASS |
| g=0 | at k=2 the rule effect must **not** be zero, and is not: **+0.0752 [+0.0651, +0.0851]** | PASS — the control can fail |
| NEGATIVE | every arm scored against **another prompt's** parity-0 humans, 200 permutations: null **−0.0004 [−0.0067, +0.0061]**, max **+0.0104**; real rule effect at k=12 **+0.0419** | PASS — outside the entire null |
| NOISE FLOOR | the three committed random seeds, sd of the rubric/uninformative cell: **0.0033 · 0.0055 · 0.0040 · 0.0037** | measured at every k |

**MULTIPLICITY**: 12 cells, BH q = 0.05 → **10 survive, 2 do not** — the two E4 cells at k=2 and
k=12, which are exactly the ones reported above as holding zero.

## ⚠ THE PREREGISTRATION WAS AMENDED BEFORE THE RUN, AND THE AMENDMENT IS STAMPED IN IT

Its identification section first claimed `random_k` has only seed s0 at k=12 — written from memory of
a truncated `ls`. The inventory run one command later shows **s0, s1 and s2 at every k**, so all four
k carry three seeds and the seed spread is measured throughout. The false sentence is left in the
file with the correction attached, because **a preregistration that quietly self-corrects is not a
preregistration.**

## WHAT DIED

- **"clause ② has one baseline"** — rule and source are the same order and neither dominates.
- **`POOL[0:k]` as an unqualified blind baseline** — at k=2 and k=4 it is a 96th-percentile draw.
- **the assumption behind clause ②'s prompt-specificity** — at matched uninformative rule, a fixed
  generic list beats the prompt's own rubric at every k.

## WHAT SURVIVES — AND THIS ROUND ADDS

A decomposition where the arc previously had one confounded number: R810's non-monotone
`topw − POOL[0:k]` splits into a **rule** effect and a **source** effect, both resolved at every k,
both shrinking with k, and statistically indistinguishable from each other at k=12.

## SCOPE

968 prompts, common intersection **734** (attaining nominal k at every k) · annotators split by index
parity, every arm scored on parity-0 · `topw_k`, `random_k` ×3 seeds, `POOL[0:k]`, and the full
enumeration of k-subsets of the 16 · paired bootstrap over prompts, NBOOT 1,200 · first release,
home judge.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| the `pool × informative` cell | a release that assigns per-prompt importance to the 16 generic criteria; the pool is one fixed list — **checked**, 1 distinct criterion-list over 50 prompts |
| a rule effect free of D1's forced decline | a rubric far larger than k; median candidates is 16 — **checked**, and the decline is reported as partly forced |
| the same decomposition on the second release | a judge pass over `utterances.jsonl`'s 68,371 utterances — **checked** |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

Clause ② needs two baselines, and this round supplies both with intervals. Computed by this round's
`run.py`, the rule effect at k=12 is **+0.0419 [+0.0353, +0.0479]** and the source effect
**+0.0372 [+0.0253, +0.0491]**, differing by **+0.0047 [−0.0073, +0.0173]**. The step is the one E3
forces: **re-measure the arc's headline gaps against the pool's subset MEAN rather than its first-k**,
because at k=2 and k=4 the committed baseline sits at the 95.8th and 96.0th percentile of its own
family. R805's `+0.0553`, R807's scale and R810's k-curve all used `POOL[0:k]` or `genericpool16`
somewhere in their construction, and the correction moves them in the flattering direction — which is
why it should be run now, by someone who has already said so, rather than found later by someone
looking for a reason the numbers were too small.
