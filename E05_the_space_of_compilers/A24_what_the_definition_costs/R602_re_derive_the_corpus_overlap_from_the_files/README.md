# R602 · The two corpora are disjoint, and the token overlap is entirely function words

**Decision this makes safe:** whether the claim table's silence about the 18 cross-release rounds is
an omission or a correct exclusion. **Correct exclusion — the corpora share no content.**

| definition of "overlap" | home vs second | floor |
|---|---|---|
| **exact identity** | **0** | 0 |
| **normalised identity** *(casefold · collapse space · strip punctuation)* | **0** | 0 |
| **token-Jaccard, median max per prompt** | **0.1654** | **0.1654** |

⭐⭐⭐ **The Jaccard median equals the shuffled-vocabulary floor to four decimal places.** The
apparent 16.6% token overlap is **entirely shared English function words** — which is precisely what
the negative control was built to separate, and it separated it exactly. Seeds 0/1/2: **0.1667 ·
0.1628 · 0.1667** against floors **0.1667 · 0.1628 · 0.1667.**

**WORLD A DISJOINT. R399 stands, and R433's `W-LOSES` is evidence about a different object.**

## ⛔ A schema defect caught before the first run, by opening the file instead of assuming
The second corpus keys its text as **`user_prompt`**. v1's extractor searched
`text`/`content`/`utterance`/`prompt`/`message` — **exact-key matching would have returned an EMPTY
second corpus.**

⚠ **And an empty corpus yields overlap 0 — which is exactly the answer I was predisposed to accept.**
A zero from an extractor that found nothing is **silence, not disjointness**, and it would have
confirmed the conclusion while measuring nothing. **The population line now prints `68,371 rows
carried a text key, 26,673 distinct` so the reader can see the extractor worked.**

## ⚠ One honest discrepancy, reported not smoothed
R399 states the overlap as **3 strings, 2 of them greetings**. **I measure 0.** My home population is
**1,078 prompts** from `comparisons.jsonl`; R399's extraction differs. **Both say "essentially
nothing" and they disagree on the last unit** — the direction is the same and the exact figure is
not reproduced.

## Controls
| control | returned |
|---|---|
| **positive** — home vs home | exact **1078/1078**, Jaccard max **1.0000** — PASS |
| **negative** — home vs **token-shuffled** second *(vocabulary kept, strings destroyed)* | exact **0,0,0**, Jaccard median **0.1667/0.1628/0.1667** — PASS |
| **placebo** — home vs synthetic tokens | exact **0,0,0**, Jaccard max **0.0000** — PASS |

⭐ **The negative control is the whole design.** Shuffling tokens preserves the vocabulary and
destroys the strings, so the gap between real and shuffled is the only part of the Jaccard that
could mean shared content. **That gap is 0.0000.**

**Bounded below, stated:** the Jaccard sweep runs against a **3,000-text subsample** — a max over a
subset cannot exceed the max over the whole, so a small value is **conservative** and a large one
would be decisive.

**IMPOSSIBLE, named:** string overlap is **not** topical or distributional comparability. **A corpus
can share no strings and still ask the same question.** This bounds one axis and says so.

## ⛔ Check #201, and what it caught
R601 closed calling R399/R400 *"uncited and **unaudited**"* — `uncited` was measured, **`unaudited`
was never checked**, and it is at least partly wrong: **R401, R402, R427 and R556 all reference
them.** And *"**the single number** the whole cross-release question turns on"* was a **superlative
never computed** — R400's depth *mass* and the corpora's differing unit are two more. **This round
measures one of three and says so.**

## The sentence I can no longer write
> *"the claim table is silently omitting a cross-release result about clause ②."*

It is **excluding** one, and the exclusion is now **justified on a measured axis** rather than by
silence. R601's finding survives in the part that mattered: **every claim row is home-release-only
and now says so.**

## NEXT
Two of the three axes remain: **R400's depth-mass claim** and **the corpora's differing unit**
(prompt vs conversation). The unit is the cheaper and the more decisive — **R433 scores per
interaction while the home release scores per prompt**, and if the units are not commensurable then
`W-LOSES` is not a comparison at all, independently of any overlap. **Read `judge_transport.py`'s own
keying and compare it to `score.py`'s**, because that is a code-level fact, not a corpus statistic.
