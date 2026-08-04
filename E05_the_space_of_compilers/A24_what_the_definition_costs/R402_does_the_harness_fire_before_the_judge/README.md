# R402 — the harness sees what it claims to see, verified before any GPU was spent

**The decision this makes safe:** *may the GPU be spent on the clause-② test?* **Yes — and a null it
returns later will be attributable to the core rather than to the instrument.**

## Result — `W_HARNESS_VALID`. Four controls pass at 3 seeds. **No GPU spent.**

| stub judge | accuracy | classified | wanted | |
|---|---:|---|---|---|
| **ORACLE** (reads the label) | 1.0000 | **ABOVE** | ABOVE | `PASS` |
| **RANDOM** (coin flip) | 0.4295–0.4354 | **NULL** | NULL | `PASS` |
| **ADVERSARY** (anti-correlated) | 0.0000 | **BELOW** | BELOW | `PASS` |
| **SHUFFLE** (ORACLE, labels destroyed) | — | **NULL ×3** | not ABOVE | `PASS` |

Population: **26,789** interactions · chance floor **0.4328** (k varies over 2/3/4, so it is not 0.5).

## ⛔ Why this round exists

**If the first real run is also the first test of the harness, a null is unattributable** — *"the core
has no advantage"* and *"the harness cannot see an advantage"* print the same string. This is the
**positive-control law applied to the apparatus** rather than to the effect, and a stub judge makes it
free.

## ⛔ ADVERSARY is the arm that matters

ORACLE and RANDOM alone cannot catch it. **If the harness takes an absolute value anywhere** — in an
effect size, a distance, a "how far from chance" — **a systematically wrong judge reads as a large
POSITIVE effect.** The `classify()` interval is signed end-to-end, and this arm is what verifies that.
*The sham-is-a-poison row cost four occurrences of exactly this shape.*

## ⛔ And the arithmetic trap has real bite here

**That ORACLE scores 1.0000 is FORCED** — it reads the label. **That is not the finding and is not
reported as one.** What is *not* forced is whether the harness's **inferential layer** classifies the
three judges correctly, and whether the oracle control **stops** passing when the labels are
destroyed. It does — `NULL` at all three seeds.

## ⭐ The exclusion filter fired, and removed more than it looks like

R399's **3 prompt strings** removed **97 interactions** — `hello`, `hi` and `does god exist?` recur
across many. **A filter that silently removes nothing is a filter that was never applied**, so the
round refuses to proceed if a non-empty exclusion list drops zero rows.

## ⭐ Free consistency check between two rounds

| | MDE at `p_d` = 0.30 |
|---|---:|
| this harness, n = 26,789 | **0.0094** |
| R401's independent derivation, n = 26,886 | **0.0094** |

**Two rounds, two code paths, same number to four decimals.** A disagreement would have meant one of
them was wrong; agreement is cheap and was worth taking.

## ⚠ What this does NOT license

**A stub judge's errors are independent; a real judge's correlate with content.** This validated the
**harness**, never the experiment. The clause-② result still requires the GPU, and the round
deliberately did not attempt it.

## Register

| criterion | status |
|---|---|
| **validation against a real judge** | **N/A** — its errors correlate with content; a stub's do not |
| **the actual clause-② result** | **N/A** — needs the GPU, which task `631` holds. Deliberately not attempted |
| **criteria generation** | **N/A** — no model here. The arms are the *judge's behaviour*, not criteria |

## The sentence I can no longer write

> *"the test returned null, so the core has no advantage"* — **without having shown the harness can
> return a non-null at all.** Those two sentences were indistinguishable until this round, and
> distinguishing them cost no GPU.

Artifact: `results/r402_harness_validation.json`, source-stamped.
