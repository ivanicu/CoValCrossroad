# R400 — the two corpora share depth *support* and almost no depth *mass*

**The decision this makes safe:** *can a transport test match on conversation depth?* **Only at
n ≤ 99, three-quarters of it at depth 2 — and CoVal's modal conversation has no counterpart at all.**

## Result — `W_DEPTH_DISJOINT`. Both extractor controls pass. **No GPU spent.**

### The two distributions, printed whole

| depth | CoVal | second corpus |
|---:|---:|---:|
| **1** | **980 (90.9%)** | **1 (0.0%)** |
| 2 | 77 (7.1%) | **2,729 (34.1%)** |
| 3 | 15 (1.4%) | 2,420 (30.2%) |
| 4 | 5 (0.5%) | 1,409 (17.6%) |
| 6 | 1 (0.1%) | 376 (4.7%) |
| *deeper* | — | 1,076 (max depth **22**) |
| **total** | **1,078** | **8,011** |

**The supports overlap. The mass sits on opposite sides.**

## ⛔ My pre-registered threshold was applied to the wrong quantity

I declared *"matched pool ≥ 100"*, where `matched` = second-corpus conversations at depths CoVal also
attests. **That is SUPPORT overlap.** A transport test needs **pairs**, so each depth is bounded by
the **smaller** side:

| depth | CoVal | second | **pairable** |
|---:|---:|---:|---:|
| 1 | 980 | 1 | **1** |
| 2 | 77 | 2,729 | **77** |
| 3 | 15 | 2,420 | **15** |
| 4 | 5 | 1,409 | **5** |
| 6 | 1 | 376 | **1** |
| | | **balanced pool** | **99** |

| the threshold, unchanged, applied to… | value | fires |
|---|---:|---|
| the **declared** quantity | 6,935 | `W-DEPTH-MATCHED` |
| the **balanced** pool | **99** | **`W-DEPTH-DISJOINT`** |

> **⚠ OVERRIDE DECLARED.** The threshold was **not retuned** — it was **re-applied unchanged** to the
> quantity a transport test can actually draw from. The override moves the verdict toward the **less
> convenient** answer, which is the only direction in which a post-hoc change is not goalpost-moving.

## ⚠ And the binary is a knife-edge — the composition is the real finding

**99 vs 100 is one conversation.** Do not read `DISJOINT` as a wall. What the numbers actually say:

1. **n ≤ 99** for any depth-matched transport test — two orders of magnitude below the 6,935 the
   support count suggested.
2. **77 of the 99 sit at depth 2.** Any such test is a claim about **depth-2 conversations**.
3. **CoVal's modal object — depth 1, 90.9% of its corpus — has exactly ONE counterpart.** So transport
   would say nothing about the conversations CoVal is mostly made of.

**That scope is the deliverable here**, not the verdict word.

## Controls

| | returned |
|---|---|
| **EXTRACTOR-A (+)** | a CoVal-shaped conversation with 3 user turns measures **3** — `PASS` |
| **EXTRACTOR-B (+)** | a second-corpus-shaped group with 3 user turns measures **3** — `PASS` |
| **UNIT** ⭐ | depth defined **once** — *distinct user turns* — and required of both. **Two formats mean two extractors, and two extractors are two chances to measure two different things and call them one** |
| **DISTRIBUTION** | histograms printed whole. A mean over a skewed integer distribution hides exactly what this round exists to find — and would have reported ~1.1 vs ~3.2 and lost the depth-1 collapse entirely |

## Register

| criterion | status |
|---|---|
| **whether depth-matching suffices** | **NO** — topic, response length, model era and annotator population remain unmatched. Each is a further filter a later design must apply or declare |
| **matching on topic** | **N/A** — needs a topic model and a shared taxonomy; neither exists |
| **a transport result** | **N/A** — this round ran no test and computed no core |

## The sentence I can no longer write

> *"the corpora share depths, so match on depth and proceed"* — **a shared support is not a shared
> distribution.** 6,935 and 99 are the same overlap counted two ways, and only one of them is a
> sample size.

Artifact: `results/r400_depth_confound.json`, source-stamped.
