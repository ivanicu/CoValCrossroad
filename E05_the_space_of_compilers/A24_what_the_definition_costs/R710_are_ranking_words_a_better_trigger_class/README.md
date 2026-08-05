# R710 · are ranking words a better trigger class, or just more words on a chance detector?

**The extension does not ship, and that refusal is the round's output. On the same 1073 paragraphs
with the same machinery and window, the RANKING class's own chance share is `0.8960` against QUANT's
`0.7942` — ranking words are WORSE per flag than the words already in the gate. R709's NEXT line
proposed a change whose cost was measurable before building it.**

Population **the 1073 NEXT paragraphs over 1270 commits** · instrument **`flagged()`'s machinery with
the trigger class as the only moving part; `ARTIFACT`, `WINDOW`, `PROVENANCE`, `BARE_COUNT` held
fixed** · baseline **QUANT's own chance share, re-measured here, plus a size-matched non-ranking sham**
· regime **this repository at HEAD, WINDOW = 60**.

## check #312 — it holds, exactly as stated

✓ `the only` (ledger 873) and `every` (ledger 892) are in `QUANT` and both flag; `weakest`
(ledger 893) is not and does not. **Verified against the live pattern, not from memory.**

## ⛔ the cheaper question the NEXT line assumed past

It proposed extending `QUANT` with ranking adjectives. But R707 measured that **0.758 of this gate's
flagging survives scrambling word order** — the detector largely responds to two words landing within
60 characters *by chance*. **Adding trigger words to a 76%-chance detector plausibly adds mostly
chance.** So the question is not *"does the extension catch the missed case"* — it will, by
construction, since `weakest` **is** the word — but **is the ranking class better than what is
already there?**

## the classes, on one corpus and one window

| class | words | flag rate | shuffled | **chance share** |
|---|---|---|---|---|
| **QUANT (live)** | 20 | 0.2535 | 0.2013 | **0.7942** |
| **RANKING (proposed)** | 10 | 0.0401 | 0.0359 | **0.8960** ⛔ |
| SHAM non-ranking | 10 | 0.0261 | 0.0244 | **0.9337** ⛔ |
| QUANT ∪ RANKING | 30 | 0.2777 | 0.2250 | **0.8101** |

**Ranking words are worse per flag than the class already in the gate**, and the non-ranking sham is
worse still. Adding either raises the union's chance share above QUANT's alone.

⚠ **QUANT re-measures at `0.7942` here against R707's `0.758`, and the difference is named rather
than papered over**: R707 used the full `flagged()` including its `BARE_COUNT` trigger; this round
holds the trigger class as the only moving part and therefore excludes it. **Different quantities,
both reported, neither substituted for the other.**

## window sweep — 4 classes × 3 windows, all reported

| class | w=20 | w=60 | whole |
|---|---|---|---|
| QUANT | 0.1528 | 0.2535 | 0.3756 |
| RANKING | 0.0140 | 0.0401 | 0.0643 |
| SHAM | 0.0121 | 0.0261 | 0.0419 |
| UNION | 0.1650 | 0.2777 | 0.4045 |

## controls — 4 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | ledger 893's actual sentence → `'weakest' over 'claim'`. ⚠ **A known-answer check — `weakest` IS the word — so it is a CONTROL on the extension, never evidence for it** |
| **g=0** | ranking words deleted from the corpus → **0** new flags |
| **NEGATIVE** | within-paragraph word scramble, length and vocabulary preserved exactly; the excluded world is named |
| **SHAM** | size-matched non-ranking adjectives: **7** new flags against ranking's **24** |
| PLACEBO / UNIT | identical runs differ by 0 · instrument unit ≠ claim unit |
| NOISE FLOOR | measured: shuffle spread **0.3750** on the 24-paragraph new-flag set |

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** new flags | 60 [10, 300] | **24**, inside |
| **B** chance share of the new flags | 0.75 [0.30, 1.00] | **0.5988**, inside |
| **C** catches ledger 893 | YES | **YES** — *recorded as a control* |
| directional | ranking is NOT better (world B) | **HOLDS** |

⚠ **POINT B is not readable and the round says so.** Its shuffle noise floor is **0.3750** over only
**24** paragraphs — wide enough to contain almost any comparison. The full-corpus figures carry the
verdict; the new-flags share is reported because it was registered, not because it decides anything.

## what this round produces

**A decision not to act.** The extension would have closed ledger 893's class of miss and imported 24
flags of the same quality as the ones R708 could not show mean anything. **The sham being
distinguishable from the ranking class (7 vs 24) does not make ranking a better class** — its own chance share (0.9337) is worse than both.

## limits

- **Construct validity is impossible here.** R708 put the gate's sensitivity ceiling at ~0.38 against
  the only labels available and could not resolve the gap. This round tests a word class's
  **mechanics**, never its correctness.
- A chance share is a property of **this corpus's prose**, not of the words.

## impossible here

| criterion | what it would require |
|---|---|
| construct validity | an external standard for which NEXT lines ought to flag |
| cross-release | the vocabulary and the `NEXT` convention are this project's |
