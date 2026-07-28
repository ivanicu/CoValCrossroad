# Retractions

Every claim this repository made and then killed, scoped or corrected — in the order
it happened, with what did the killing.

The rounds are numbered by when they ran, not by what survived. Read in that order
the repository looks like a sequence of findings. It is not. **Nine of these entries
are a later round destroying an earlier round's conclusion, and in seven of them
both rounds are mine.**

This file exists because the git log has all of it and nobody reads a git log.

| # | The claim | What killed or scoped it | What survived |
|---|---|---|---|
| 1 | **"Governance uncertainty exceeds sampling uncertainty at k=4"** (+0.028), inherited from the source package and reproduced bit-identically | Matched-pairing analysis. The two halves were different objects: a distance from a bootstrap to a **noise-free reference** versus a distance between **two objects both carrying noise**. Under either matched pairing the sign reverses: −0.032 draw-vs-draw, −0.003 reference-vs-reference | The k-curve shape. The zero crossing moves from between k=5 and k=6 to between k=1 and k=2 |
| 2 | **"2.96% of crowd-written criteria address anthropomorphism"** (r07, first lexicon) | Substring matching. `persona` was catching *personal*, *personality*, *personalities*; `friend` was catching *friendly*, *friendships*. 321 of 452 hits were false | Word-boundary regexes give **0.16%** — twelve times smaller. The finding got *stronger* via a bug |
| 3 | **Pre-registered gaming prediction**: a majority-generic target should show rising verbosity and criterion-keyword overlap under optimization (r09) | r09 itself. Every marker **fell**: words 125→116, overlap 0.307→0.284, bullets 1.62→1.34 | Nothing of the prediction. Reported as refuted rather than reframed |
| 4 | **"Optimizing the rubric improves held-out preference"** (+0.53 [0.06, 0.99], r09) | r11's independent-backbone control. The gold head shared Qwen3.5-2B with the judge. On an independent 0.8B backbone the change is **+0.05 [−0.44, +0.53]** — indistinguishable from zero | Only the bound: *no overoptimization detected at this pressure, and no improvement established either*. r09 had passed its own positive control and its own paired test |
| 5 | **Assurance claim C6 passed** while testing `positive_control_passed`, a field unrelated to its own statement about lexical overlap | Reading the claim next to its test. Rewritten to test what it asserts; it now **FAILS** at −0.0229 | The habit, generalised: every claim's test must be readable against its own sentence |
| 6 | **"The advantage is response-set-specific"** — criteria were written after their authors read the four candidates, so they encode facts about them (r12) | r13. Seed criteria, prepared alongside candidate generation and **never tailored to those responses**, carry *more* attribution (+0.039, CI excludes 0) than write-ins authored after reading them (+0.029, CI includes 0) | The datum: the advantage does not transfer, +0.102 → −0.042. Only the mechanism died, and what replaced it is stranger |
| 7 | **The whole assurance manifest**, after the repository was reorganised into `rounds/` | Running it. Every claim source had moved and all thirteen resolved to `UNSUPPORTED`, which reads as *not yet measured* rather than *this package can no longer find its own evidence* | A new status, `BROKEN_HARNESS`, that refuses to emit a manifest at all |
| 8 | **r17's first design** — route a rater on half a prompt's criteria, score them on the rest | The data. Every prompt shows the same six seed criteria: 731 prompts have exactly 6, none has 10, and a k=4 core consumes four. **No held-out design at the criterion level is possible on CoVal** | The constraint became a finding, and routing moved to cross-prompt history |
| 9 | **"Preserving disagreement harms the worst-off bloc"** (r16) | r17. With routing learned from a rater's *other* prompts, conditional directions help exactly the rules carrying contested items — conflict_aware +0.195, constituency +0.148 — while consensus-seeking rules move by less than 0.02 | The ranking. Conditional conflict_aware still reaches only 2.999 against un-conditioned utility at 3.609. The correct claim is narrower: preserving disagreement **with a single direction** harms the worst-off bloc |
| 10 | **My own suspicion** that r17's 84.6% routing accuracy was entirely free | r18. The inflation is real, +0.147 — but on contested items the router still reaches **0.666 [0.643, 0.688]**, nowhere near chance | Routing works, and works far less often than the headline implied. *The first time the data corrected a doubt of mine rather than a claim* |
| 11 | **"Less than half of a values evaluation measures values"** — reported as 43% | r19. The shuffled arm used a **random** donor, which retains 47–60% of the self signal because a random prompt sometimes shares topic. Against a nearest-topic floor the attribution is 0.047; against the farthest, 0.115. **Span 2.47×** | The bracket, 27%–67%, and the rule that any single figure must name its floor |
| 12 | **r19's own first bracket**, 29%–63% | r19's proper runner. The inline version averaged in a judge cell whose self accuracy was **0.5405** — barely above chance, therefore not decomposable. Excluding it *widened* the spread to 27%–67% | The direction is worth noting: the reported interval was too **narrow**, and it was narrow because noise had been averaged in as data |

## The pattern

Eleven of the twelve are the same failure, and it is the one this repository's North
Star names:

> **a number was reported without the scope over which it holds.**

- an uncertainty compared against a differently-paired uncertainty (1)
- a lexicon whose match rule was not the concept (2)
- a gold model whose backbone was shared with the thing it judged (4)
- a claim whose test was not its statement (5)
- a mechanism attributed to a datum that did not require it (6)
- a manifest that could not tell *unmeasured* from *unfindable* (7)
- a metric that assumed an output format the claim did not (9)
- an accuracy averaged over cases where nothing had to be decided (10)
- a floor treated as measured when it was chosen (11, 12)

The exception is 3 — a prediction that was simply wrong.

## What this costs and what it buys

Seven of the twelve were caught by a **later round of my own**, which is the only
reason they are here rather than in the published headline. Two were caught only
because a control was run that nobody would have asked for: r11's independent
backbone and r18's contested-item restriction.

Both of those controls were cheap. Neither was obvious. **The expensive part of this
project was not any experiment — it was noticing which number had not been asked
where it stops being true.**
