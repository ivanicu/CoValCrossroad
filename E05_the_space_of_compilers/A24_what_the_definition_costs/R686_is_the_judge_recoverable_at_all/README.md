# R686 · is the judge recoverable at all?

**⭐⭐⭐ 19 of the 81 unrecorded rounds (23.5%) do carry a judge somewhere R684's exact-key test
could not see — 13 in a value field, 6 as an embedded token, **0 in a filename**. For the other 62 it
is genuinely absent. So the scope is **partly a formatting defect and partly lost**, and the split is
now a number.**

## ⛔ CHECK #287 · MY OWN NEXT LINE PROPOSED A DERIVATION
R685 asked how many of the 81 store per-judge ranks or means. **R684 defined those 81 as the rounds
with no judge key in their artifact — and a per-judge mean is stored under a judge key.** The answer
is **zero by construction**. *"Could this have come out otherwise?"* No. **That is the arithmetic
trap the standard opens with, in my own closing sentence, one round after I quoted it.** The
arithmetic control in this round confirms R684's partition (81/81) and is **labelled a derivation
carrying no evidential weight**.

## ⭐⭐⭐ THE SAME BUG, THREE TIMES — SO I BUILT THE TOOL INSTEAD OF THE THIRD PATCH
The positive control **failed**: `(?<![\w.])(2B)` cannot match `scores_2B.json`, because **`_` is a
word character**.

| | |
|---|---|
| ledger **762** | `\bpublished\b` missed `published_five` → a publication list read as a measurement |
| ledger **768** | `\bR(\d{3})\b` missed `R294_the_...` → a producer map built **0 rounds from 5 paths** |
| **here** | `(?<![\w.])` missed `scores_2B.json` → the positive control failed |

**P7: same bug three times means build infrastructure.** → **`assurance/token_boundaries.py`**, with
its own self-check (7 boundary cases, all passing). The rule it encodes: for identifiers living in
snake_case and paths, the boundary you want is *"not adjacent to a letter or digit"* — `_ . - /` are
**separators**, and `\b` gets that backwards for exactly the characters this corpus uses most.
**A lesson in a ledger is not a function anyone calls.**

## THE RESULT

| encoding | rounds |
|---|---|
| filename | **0** |
| value field | **13** |
| embedded token only | 6 |
| **none — genuinely absent** | **62** |

**19 of 81 recoverable (23.5%).** Registered **A 20 [5,50] → 19, INSIDE, error −1.**
**DIRECTIONAL FAILS** — I predicted filename encoding would dominate; **it is zero.** Nobody in this
corpus names a judge in a filename; they put it in a value field.

**Controls:** POSITIVE — judge in a filename → recovered. **g=0** — no judge anywhere → not recovered.
NEGATIVE — `d2Bx` → no match, *a substring is not an encoding*. PLACEBO — identical. **ARITHMETIC —
a labelled derivation, not evidence.**

## ⚠ UPPER BOUND, AND THE UNITS ARE WHY
A recovered judge **name** is not proof it **produced the verdict**. Instrument unit: **a mention**.
Claim unit: **a provenance**. Not equal — so 23.5% bounds recoverability from above.

## IMPOSSIBLE HERE
Confirming a recovered judge produced the verdict needs the round re-run; **93 rounds in this arc are
corpus-dependent** and would not reproduce.

## NEXT
62 rounds carry no judge in any encoding (`results/recoverability.json`, counts field, `none`). The
13 that carry one in a value field are the tractable set: read each one's field NAME and check
whether the same name recurs, because a shared field name is a convention that could be made a
gate, and a set of one-off names is not. That decides whether the recording defect is fixable by a
rule or only by hand.
