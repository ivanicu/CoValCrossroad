# R707 · is the gate's length dependence a bug at all? — R706's finding attacked, and a worse one found

**Both, and they answer different questions. ① R706's instrument finding is largely RETRACTED: the
`9.6×` rise in flag rate across length deciles decomposes as `5.32×` more opportunities per
paragraph × a per-opportunity residual of `1.798×`. `flagged()` is a presence detector, so rising
with length is correct behaviour, and the normalisation R706 proposed would have broken it.
② But a worse problem is found and it is not the one R706 named: scrambling the word order within
each paragraph — length and vocabulary preserved exactly — still flags `0.2100` against the real
`0.2772`. **≈76% of this gate's flagging is two words landing within 60 characters by chance.****

Population **the 1067 NEXT paragraphs over 1270 commits** · instrument **`flagged()` imported
unchanged, plus a word-order permutation** · baseline **the corpus's own rate, 0.2772** · regime
**this repository at HEAD, WINDOW = 60**.

## check #309 — R706's citation does not resolve

R706's NEXT line cites the decile rates *"from `results/widening.json`"*. ⛔ **That artifact holds no
decile table, no length-matched difference, no stratified null.** `0.065` and `0.620` appear only
inside a prose `world` string. §5 requires the artifact to carry *what a later round needs to attack
this*, and R706's central result — the confound that overturned its own pre-registered kill — was
printed to a terminal and discarded. This round recomputes and **persists** it as fields rather than
re-running a committed artifact (ledger 848).

## ⛔ and the cheaper question the NEXT line skipped past

R706 concluded the gate *"measures verbosity, exactly the wrong direction"*. But `flagged()` answers
**does this paragraph contain at least one unsourced quantifier** — a *presence* question. A longer
paragraph makes more claims, and for n opportunities `1−(1−p)ⁿ` **rises with n by construction**. So
the length dependence might be the detector working. That had to be settled first: **normalising a
correct detector would break it.**

## the decile table (persisted, per check #309)

| decile | n | median len | flag rate | opps/para | **flags/opp** | shuffled | shuffled/real |
|---|---|---|---|---|---|---|---|
| 0 | 107 | 77 | 0.0654 | 0.35 | 0.1892 | 0.0648 | **0.99** |
| 1 | 108 | 130 | 0.2037 | 0.55 | 0.3729 | 0.1552 | 0.76 |
| 3 | 109 | 197 | 0.2294 | 0.52 | 0.4386 | 0.1893 | 0.83 |
| 5 | 107 | 270 | 0.2710 | 0.70 | 0.3867 | 0.1651 | 0.61 |
| 7 | 107 | 403 | 0.2617 | 0.69 | 0.3784 | 0.2190 | 0.84 |
| 9 | 107 | 675 | **0.6262** | 1.84 | 0.3401 | 0.4919 | 0.79 |

*(deciles 2, 4, 6, 8 in `results/length.json`; all ten are persisted.)*

**The decomposition:** `9.571 = 5.324 × 1.798` — opportunities × residual, exactly.

## controls — 7 PASS, 0 FAIL, two runs byte-identical

| control | returned |
|---|---|
| POSITIVE | the gate's own known-false NEXT lines: 3 found, all still flagged |
| **g=0** | every `QUANT` span deleted → **0** quantifier flags (bare-count flags counted separately as a different trigger, not excused) |
| **NEGATIVE** | word shuffle — **the world it excludes is named**: *the detector responds to bag-of-words composition rather than to two words being near each other*. 0.2100 [0.1938, 0.2257], real 0.2772 is **outside** it |
| SHAM | proximity window removed entirely → 0.3914 vs real 0.2772 — the 60-char constraint is worth **0.1142** |
| PLACEBO | two identical runs differ by exactly 0 |
| NOISE FLOOR | shuffle spread **0.0318** over 1200 permutations, measured |
| SEEDS | 3 streams differ |
| UNIT | instrument unit `A NEXT PARAGRAPH` ≠ claim unit `THE DETECTOR'S BEHAVIOUR` |

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** per-opportunity ratio hi/lo | 1.0 [0.4, 2.5] | **1.798**, inside |
| **B** word-shuffled flag rate | 0.20 [0.05, 0.50] | **0.2100**, inside |
| **C** flags `20d1d1f` naming "the only" | YES / YES | **`quantifier 'the only' over 'arm'`** |
| directional | shuffled < real, outside its spread | **HOLDS** |

⭐ **Point C settles the thread that started five rounds ago**: the predicate would *always* have
caught `20d1d1f`'s false quantifier. **The predicate was never the problem — the extractor was**,
which is exactly what R706 fixed.

⛔ **Both pre-registered worlds fired, and my first verdict's branch ORDER decided which printed.**
A and B are not mutually exclusive — one explains *why the rate rises with length*, the other *what
the detector responds to at all*. The branch now computes and states both.

## the window sweep — 5 windows × 10 deciles, all reported

| window | overall rate | flags/opp (shortest) | flags/opp (longest) | ratio |
|---|---|---|---|---|
| 0 | 0.0449 | 0.0270 | 0.0761 | 2.817 ⛔ |
| 20 | 0.1835 | 0.0811 | 0.2335 | 2.880 ⛔ |
| **60 (live)** | 0.2772 | 0.1892 | 0.3401 | **1.798** |
| 200 | 0.3736 | 0.2162 | 0.4162 | 1.925 |
| whole paragraph | 0.3914 | 0.2162 | 0.4467 | 2.066 |

Non-survivors (per-opportunity ratio outside [0.4, 2.5]): **windows 0 and 20** — at tight windows the
residual length dependence is *worse*, not better.

## limits

- **Construct validity is impossible here**: no external standard says which NEXT lines *ought* to be
  flagged. This round tests the predicate's **mechanics** and cannot test its correctness.
- "Opportunity" is operationalised as a `QUANT` match. That operationalisation is mine and is the
  round's main assumption, which is why raw counts sit beside every rate.
- The chance share is **0.61–0.99 across deciles** — a range, not a point, and it is **worst in the
  shortest paragraphs**, where a scrambled paragraph flags as often as the real one.

## impossible here

| criterion | what it would require |
|---|---|
| construct validity | an external standard for which NEXT lines ought to flag |
| cross-release | the `NEXT` convention and artifact vocabulary are this project's |
