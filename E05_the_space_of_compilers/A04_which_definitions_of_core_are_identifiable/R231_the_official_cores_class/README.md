# R231 — the official core's actual Q-class

**Arc E05·A04.** Every number in this arc so far is on a **planted** class. This measures the
official core's own — no plant, no simulation, 968 prompts.

## Controls first, and the band check refused the cell

| | |
|---|---|
| **placebo** — Full vs itself, same judge | **1.0000** ✔ the class function is deterministic |
| **floor** — random 4-criterion arm, 20 draws | **0.3836** [0.3657, 0.4019] |
| cross-judge — Full vs Full, different judge | **0.2359** |

I registered cross-judge agreement as the **ceiling** — *"no compiler can agree with Full more often
than Full agrees with itself under a change of instrument"* — and `covalx.control_band` **refused
the cell**: `floor 0.3836 is above ceiling 0.2359`.

**It was right, and I had conflated two axes.** Cross-judge agreement holds the criteria fixed and
changes `S`. The compiler holds `S` fixed and changes the criteria. Those are different
perturbations, and the correct ceiling on a *fixed* judge is **1.0**, which the placebo verifies.

> **Promoted from a broken ceiling to a finding in its own right: changing the judge moves the
> induced class MORE than dropping 11 of 15 criteria does — 0.2359 against 0.3836.**

This is R229's check catching my framing on its second use, having caught my *ceiling* on its first.

## The measurement

| comparand | base | phi | qwen3b | swapped | no_fewshot |
|---|---:|---:|---:|---:|---:|
| core vs full, same judge | **0.3864** | 0.2893 | 0.3068 | 0.4300 | 0.3300 |
| core vs human consensus | 0.1529 | 0.1674 | 0.1674 | 0.1600 | 0.0533 |
| full vs human consensus | 0.2004 | 0.1632 | 0.1880 | 0.1967 | 0.1067 |

Band: floor **0.3836**, ceiling **1.0000**, observed **0.3864** — **0% of the available headroom.**

## The verdict, and it is a C6 demonstration rather than an indictment

> On `Q = reproduce Full's exact weak ordering`, the official core scores **0.3864** against a
> random-4 floor of **0.3836 [0.3657, 0.4019]** — a difference of **+0.0028, inside the floor's own
> draw spread. On this Q the official core is indistinguishable from picking four criteria at
> random.**

**And R220 measured the opposite on a different `Q`** — predicting human pairwise preferences, where
the core scores 0.6602 against a random range of 0.645–0.659, clearly above.

**Both are correct.** That is the C6 claim, measured rather than asserted:

> **The answer is a function of `Q`. A compiler that is indistinguishable from random on one query
> family is clearly better than random on another, with the same criteria, the same judge and the
> same data.**

Anyone reporting *"the core preserves X% of the rubric"* without naming `Q` has reported a choice.

## Register

Whether the core's class is the **right** class is not measured here — that needs a downstream task
the release does not carry. This measures **preservation**, never correctness. And `core vs human`
at 0.1529 against `full vs human` at 0.2004 says both objects match the human consensus ordering
rarely, because matching all six pairwise relations exactly is a demanding target; neither number
should be read as an accuracy.

## The sentence that can no longer be written

*"The official core is better than random selection."* On one declared query family it is; on
another it is not; and the sentence is unfinished until `Q` is named.
