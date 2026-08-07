# R805 · the held-out arms, scored held-out — fitting survives, and R294's census was 50% contaminated

`run.py` · `PREREGISTRATION.txt` · `results/heldout.json` · 968 prompts × 11 arms × parity split ·
**WORLD A** · two hash seeds byte-identical, md5 `ce83f0d6d1d33fd227ecbde86f9e54e9`

## THE DECISION THIS MAKES SAFE

**Fitting a core to a prompt's own human labels is a real route, not an artifact — it survives when
the labels it is scored on are genuinely held out.**

> `oracle_k4_fit1` − `genericpool16`, both on parity-0: **+0.0553 [+0.0456, +0.0653]**

**But every number the record carried about it was inflated**, in two separate ways this round
measures.

## ⭐ E1 · ONE SPLIT, EVERY QUANTITY UNDER IT

| | A2 on parity-0 |
|---|---:|
| `floor_p0` — judge-free length | **0.457228** |
| ⭐ **`CEIL_HO_p0`** — best weak order **fitted on parity-1**, scored on parity-0 | **0.636344** |
| `CEIL_ATT_p0` — in-sample max on parity-0 (an upper bound) | 0.707062 |

`CEIL_HO_p0` is not merely *a* ceiling: it is **the same estimator class as the fitted arms** — an
oracle that sees parity-1 and must predict parity-0. So a fitted arm's share of
`[floor_p0, CEIL_HO_p0]` is a matched statement, which is exactly what R804's was not.

## ⭐ E2 · EVERY ARM ON PARITY-0

| arm | kind | parity-0 | parity-1 | ALL | vs pool (parity-0) | share |
|---|---|---:|---:|---:|---|---:|
| `oracle_k4` | **LEAKY** | 0.6314 | 0.6251 | 0.6283 | +0.0873 [+0.0792, +0.0967] | 97.2% |
| `oracle_k4_fit1` | held-out | **0.5993** | 0.6304 | 0.6142 | **+0.0553 [+0.0456, +0.0653]** | **79.3%** |
| `greedy_k4_fit1` | held-out | 0.5984 | 0.6242 | 0.6106 | +0.0543 [+0.0452, +0.0642] | 78.8% |
| `indep_k4_fit1` | held-out | 0.5866 | 0.6025 | 0.5941 | +0.0425 [+0.0338, +0.0517] | 72.2% |
| `coval_core` | honest | 0.5677 | 0.5654 | 0.5665 | +0.0236 [+0.0152, +0.0322] | **61.7%** |
| `topw_k4` | honest | 0.5656 | 0.5629 | 0.5642 | +0.0215 [+0.0133, +0.0300] | 60.5% |
| `generic` | honest | 0.5533 | 0.5494 | 0.5514 | +0.0093 [+0.0055, +0.0128] | 53.7% |
| `genericpool16` | honest | 0.5441 | 0.5404 | 0.5422 | +0.0000 (itself) | 48.5% |
| `full` | honest | 0.5099 | 0.5077 | 0.5087 | −0.0341 [−0.0433, −0.0250] | 29.4% |
| `random_k4_s0` | honest | 0.4937 | 0.4918 | 0.4927 | −0.0504 [−0.0614, −0.0401] | 20.4% |
| `gen_sham` | honest | 0.4845 | 0.4811 | 0.4828 | −0.0596 [−0.0693, −0.0500] | 15.2% |

**BH q = 0.05 over 11 tests: 10 survive, 1 does not.** ⚠ The non-survivor is **`genericpool16`
against itself** — a degenerate self-test that is a built-in placebo (exactly `+0.0000`), not an
informative failure. Naming it is the point; leaving it uncounted would have made the family 10/10.

## ⛔ E3(a) · R294's COMMITTED CENSUS IS CONTAMINATED, AND THE HONEST ARM PRICES IT

R294 builds `HC[p]` from **all** annotators (`R294/run.py:110`) and publishes `oracle_k4_fit1 =
0.6142`. Half of those annotators **are that arm's fit set**. R293 declared the restriction — *"For
`*_fit1` the evaluation is restricted to parity-0"* — and implemented it (`R293/run.py:80-93`).
**R294, the table later rounds read, did not.** Declared ≠ implemented.

| arm | ALL − parity-0 | |
|---|---|---|
| `oracle_k4_fit1` | **+0.014832 [+0.011175, +0.018461]** | contamination |
| `greedy_k4_fit1` | +0.012214 [+0.008464, +0.016007] | contamination |
| `indep_k4_fit1` | +0.007470 [+0.003794, +0.011049] | contamination |
| **`coval_core` (honest, no prompt labels)** | **−0.001218 [−0.004766, +0.002230]** | ⭐ **the D4 confound, and it is null** |

**That last row is what makes the first three a leak measurement rather than a split artifact.** The
two evaluations use different annotator sets, so a gap could have been sampling — an arm that never
touches prompt labels shows **no gap**, so the gap the fitted arms show is the labels.

## ⭐ E3(b) · AND THE PRICE OF THE ANSWER KEY

> LEAKY `oracle_k4` − held-out `oracle_k4_fit1`, both on parity-0: **+0.032022 [+0.026225, +0.038194]**

⚠ **D3 — every leak number here is a LOWER BOUND.** R295 measured that the fit1 advantage
concentrates where the two halves agree, so parity-0 is a *proxy* for the parity-1 labels the fit
consumed. A split that held out the prompt itself would show more, not less.

## ⛔ E4 · R804's HEADLINE, CORRECTED — AND IT WAS MINE

| | |
|---|---|
| as R804 published | LEAKY `oracle_k4` **0.6283** against a **held-out** ceiling → **97.1%** of the generalising range |
| matched here | held-out `oracle_k4_fit1` **0.5993** against `CEIL_HO_p0` **0.636344** → **79.3%** |
| the released core | `coval_core` **0.5677** → **61.7%** |

R804 flagged the selection caveat in prose and **still published the number**. R293 had already
written that the leaky arm "is not comparable to the others"; R804's population took the leaky arm
and excluded all three held-out ones. **A caveat in the text is not a corrected number.**

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | leaky oracle on parity-0 **0.631353** and parity-1 **0.625062** vs R293's committed **0.631353 / 0.625062**; `coval_core` on all annotators **0.5664774812** | PASS, else exit 2 |
| PLACEBO | constant predictor on parity-0 **0.1389806792** vs parity-0 tie rate **0.1389806792** | PASS — exact |
| POSITIVE | D1, each fit must score higher on its own half: `oracle_k4_fit1` 0.630410 > 0.599331 · `greedy` 0.624184 > 0.598415 · `indep` 0.602500 > 0.586595 | PASS ×3, band **0.1390 < t < 0.7071** |
| NEGATIVE | each core scored against **another prompt's** parity-0 humans: 0.567696 → **0.422319** | PASS |
| CONFOUND | D4, above — the honest arm's all-vs-parity-0 gap is **−0.001218**, CI holds 0 | PASS |
| D2 | `CEIL_HO_p0 ≤ CEIL_ATT_p0` — forced; a violation would mean the code is wrong | PASS |
| NOISE FLOOR | parity-0 split in half, 20 draws: sd **0.002181** | every margin above is ≫ 20× it |

**Population**: 968 prompts, **0 dropped** — every prompt has an annotator in both parities.

## WHAT DIED

- **R804's NEXT as posed** — `select_core.py` selects **per prompt**, so there is nothing to
  cross-validate across prompts. R801 established this and I wrote the NEXT anyway.
- **R804's "97.1%"** — a leaky arm against a held-out ceiling. Matched, it is 79.3%.
- **R294's `oracle_k4_fit1 = 0.6142`** as a held-out number — it is contaminated by **+0.0148**.
- **World B and World C** — fitting neither vanishes nor inverts once labels are held out.

## WHAT SURVIVES — AND THIS ROUND ADDS

**Fitting to a prompt's own humans is an admissible route with real content**: +0.0553 above the
blind pool with labels held out, 20× the noise floor. And a matched axis: on parity-0, the released
`coval_core` captures **61.7%** of what a generalising oracle achieves, the best held-out fitted arm
**79.3%**, and the whole rubric `full` only **29.4%** — below the blind pool.

## SCOPE

968 prompts × 4 responses · annotators split by index parity, fit on 1, evaluate on 0 · 11 arms ·
instrument A2, identical to every prior round · paired bootstrap over prompts, NBOOT 1,200 · first
release, home judge · `CEIL_HO_p0` fitted on parity-1 over the 75 weak orders.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| a split that holds out the PROMPT, not the annotator | a second set of prompts with the same rubric; R295 showed the halves are not independent and this round inherits that — **checked**, and every leak number is reported as a lower bound |
| the same test on the second release | a judge pass over `utterances.jsonl`'s 68,371 utterances; `sat_*.npz` are keyed to release one — **checked** |
| whether A2 is the right instrument | an external gold standard — `corebench/score.py:34`'s open register |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The axis is matched and the fitted route survives. Computed by this round's `run.py`, held-out
fitting buys **+0.0553 [+0.0456, +0.0653]** over the blind pool while the answer key buys a further
**+0.0320 [+0.0262, +0.0382]** that no admissible core may have. What that leaves unresolved is
**where the +0.0553 comes from**: R295 showed the fit1 advantage concentrates in the quintile where
the two annotator halves AGREE, which is consistent both with prompt-specific content and with
parity-0 being a proxy for the labels the fit saw. The step is to separate those with a design R295
could not run: **re-fit the oracle on parity-1 and evaluate it on the prompts' LOW-agreement
quintile only**, where parity-0 is a poor proxy — if the +0.0553 survives there it is content, and
if it vanishes the whole fitted route is label access. That needs no judge pass and its outcome is
not forced.
