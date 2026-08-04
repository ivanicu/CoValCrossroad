# R363 — clause ③ closes the ranking channel and not the rubric channel

**The decision this makes safe:** *may clause ③ be stated as "uses no information from that prompt's
own human labels"?* **Not as implemented.** It excludes arms that read the **rankings**. It does not
exclude `topw_k`, which selects on importance scores written by **the same annotators**, at 95.3%.

## Result — `W_CHANNEL_OPEN`. All controls PASS. Two runs byte-identical. **No judge involved.**

Clause ③ is applied everywhere by one hand-written line, which I wrote five times:

```python
USES_PROMPT_LABELS = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}
```

**That is an answer key**, duplicated across R294, R301, R359, R360 — and never checked against the
code that builds the arms.

### Half of it survives its first audit

`corebench/select_core.py:102` opens `data/comparisons.jsonl` — the rankings — **only** when
`rule ∈ (oracle_k, indep_k, greedy_k)`. The four listed arms are exactly the instances of those
three rules. **The key is correct about the rankings.**

### The half that does not is `topw_k` — which supplies four of the published five

`select_core.py:132`: `w = mean(s["score"] for s in items[i]["scores"])`, with `items` from
`conversation_rubrics.jsonl`. The source comment reads *"Non-leaky: the weights come from the
rubric, not from the outcome."* **True about the file.** This round asks who wrote it.

| quantity | median | mean | min |
|---|---:|---:|---:|
| **SAME prompt** — \|A_rubric ∩ A_rank\| / \|A_rubric\| | **0.962** | **0.953** | 0.62 |
| SHAM seed 0 — vs a **different** prompt | 0.000 | 0.016 | 0.00 |
| SHAM seed 1 | 0.000 | 0.016 | 0.00 |
| SHAM seed 2 | 0.000 | 0.017 | 0.00 |

**Ratio 58×.** In **473 of 968** prompts (48.9%) *every* rubric scorer also ranked. **Zero prompts
have zero overlap.**

## The sham is what makes this provenance and not arithmetic

*"The rubric scorers are the same people as the rankers"* would be **forced and meaningless** on a
small fixed panel — 16 people doing every prompt would overlap at 100% everywhere. The release has
**1,160 distinct annotators** against a median panel of **16**, and the cross-prompt overlap is
**0.016**. So the same-prompt 0.953 is a fact about *who was assigned to what*, not about pool size.

## Three different kinds of statement, kept apart

| | |
|---|---|
| **MEASURED** | the overlap above — a **census** over 968 prompts, no sampling, no judge |
| **DERIVED** | from that census **+** this release's own headline that rubrics are authored *after* ranking: `topw_k`'s selection weights are written by the very annotators whose rankings it is later scored against. So *"producible from the conversation alone"* is **false of `topw_k` as constructed** — it is the conversation **plus a post-ranking artefact of the same people** |
| **UNMEASURED** | how much of `topw_k`'s advantage is *attributable* to the channel. That needs the weights rebuilt from held-out annotators — **the next round**, not something this one may imply |

## Controls

| | returned |
|---|---|
| **SHAM** — `A_rubric(p)` vs `A_rank(q≠p)`, 3 seeds | 0.016 / 0.016 / 0.017 |
| **PLACEBO** — a scorer set against itself | **1.000** at every prompt |
| **POOL** — is the sham informative? | **1,160** annotators vs a median panel of **16** |
| **JOIN** — the joiner's own diagnostic | `role_canonical 966 · fuzzy≥0.95 2 · unmatched 18` |
| reproducibility | two runs **byte-identical** (`fa3a14f12eda`) |

⚠ The join is by **message content**, not by id — the two files use **different conversation-id
spaces**, and a naive id join returns **zero rows silently**. The 18 unmatched rubrics are a
population this round did not see, named rather than folded into the denominator.

## Why this one carries no judge index

Every other clause in `DEFINITION.md` now names an instrument. **This does not, and cannot need
to:** it is a property of the release's provenance structure, computed with no model in the loop at
all. It is the only claim in the campaign of that kind.

## Register

| criterion | status |
|---|---|
| **the channel's SIZE** | **N/A here** — needs `topw_k` rebuilt from held-out annotators' weights and rescored; named as the next round |
| **cross-release** | **N/A** — one release |
| **the 18 unmatched rubrics** | outside this round's population, stated |

## The sentence I can no longer write

> *"clause ③ uses no information from that prompt's own human labels."*

**It uses none of the RANKINGS. It uses the importance scores of the same people who produced them,
at 95.3%.**

Artifact: `results/r363_rubric_channel.json`, source-stamped.
