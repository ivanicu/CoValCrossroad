# R1082 — **3 of 343 anchors were green because of document ORDER.** Repaired, and guarded.

**The decision this round makes safe:** whether the anchoring gate's GREEN is evidence about the
record or about the layout. **For three anchors it was layout** — and prepending one paragraph made
the whole gate exit 1. The repair and its guard ship in this commit.

## The defect

`definition_matches_the_record.read_claims` is **`re.search(pat, text)`** — the **first** match, over
the whole 11,902-line document, once per anchor, **343 anchors**. R1049 measured this exact defect
class in the **currency** gate (16 of 63 facts multi-home). **The repair never crossed to the sibling
gate.** The invariant nobody named: *an anchor identifies a SENTENCE, and a pattern matching two
sentences has identified nothing.*

| | |
|---|---:|
| anchors, pinned at `e0f433c1` | **343** |
| matching more than once | **4** |
| capturing more than one DISTINCT value | **3** |
| whose FIRST home disagrees with the artifact | **0** |
| **green by ORDER** (first agrees, a later home does not) | **3** |

## ⛔ The pre-registered kill was mis-specified and its verdict is WITHHELD

World C — *the document states one quantity twice with different values* — fires on `Q2 = 3` **as
written**, and as written it is wrong. **My instrument's unit is *a regex match capturing a number*;
world C's unit is *a statement of the same quantity*.** §4 requires those to be equal *before* the
control is designed. Read from the object, the three hits are three **different** quantities:

| anchor | first home | second home | same quantity? |
|---|---|---|---|
| `published_ref_pctile` | R348's `POOL[0:k]`, 93.7th pct | **R812's** `POOL[0:4]`, 96.0th pct | **no** |
| `r432_floor` | R432's headroom floor `0.0084` | an unrelated token-Jaccard p90 floor `0.2117` | **no** |
| `r485_oracle` | `oracle_k4` **score** `0.6282` | `oracle_k4` mean selection **position** `0.2791` | **no** |

**C is UNVERIFIED — never ADMITTED, never OVERTURNED.** Folding it either way manufactures a
permanent verdict.

## ⭐ What is admissible needs no semantic judgement — a gauge test, executed

Prepending text to a document must leave a claim about the document's **content** invariant. Prepend
the second home's own sentence, then run **the real gate** — both of them.

| anchor | binds to | artifact | gate at `e0f433c1` | gate in this commit |
|---|---:|---:|---|---|
| `published_ref_pctile` | 96.0 | 93.7 | **rc=1 FAILS** | rc=0 **immune** |
| `r432_floor` | 0.2117 | 0.0084 | **rc=1 FAILS** | rc=0 **immune** |
| `r485_oracle` | 0.2791 | 0.6282 | **rc=1 FAILS** | rc=0 **immune** |

⚠ **World D was added AFTER the fact and is labelled so.** Its strength is that it executes the gate
under test and carries its own control — *prepending a number-free paragraph must change nothing*,
which passes — not that it was declared first.

## Controls — 11, all green

POSITIVE (the counter sees a planted second home · the planted home carries a different value · **the
gate stays green on the contradicted document**) · NEGATIVE (a *repeated* home is `n=2, distinct=1`;
the gate is green on mere repetition, **correctly** — without this, `Q1` would be read as a defect
count) · SHAM (a home with the number removed is not a home) · g=0 (the unplanted copy reproduces the
real count; the gate is green on the unmodified document) · PLACEBO (fewer than a tenth of the 343
patterns fire on 400 foreign READMEs) · GAUGE (a number-free prepend changes nothing) ·
REPRODUCIBILITY.

⭐ **The measurement is pinned to `e0f433c1`** and loads the anchor set from that revision. Reading
the live file would regenerate this artifact from the *repaired* gate and **the finding would vanish
from its own evidence.**

**Specification curve** — 8 cells (region × overlap × normalisation). `4 / 3 / 0` in **all eight**;
no defensible choice moves it.

## The repair, and the guard so it cannot recur

**Repair** — the three patterns now carry context unique to their intended sentence, e.g.
`against a floor of **X**` → `headroom **+Y** against a floor of **X**`.

**Guard** — `assurance/an_anchor_binds_to_one_number.py`, wired into `preflight.py` as `one-home`.
It fails on `distinct > 1` and only **warns** on `n > 1, distinct = 1`. ⚠ That leniency is bounded
and its admitted world is named: *a document repeats a correct number in two places, one of which
later goes stale while the other keeps the gate green.* Not covered here; it needs P16's
one-home-per-fact discipline, which is prose, not a gate. **1 anchor is in that state today
(`n_arms_r301`).**

**Attacked six ways before being trusted** (P7):

| # | vector | result |
|---|---|---|
| ① | run on the repaired tree | GREEN, rc=0 |
| ② | revert one anchor to its promiscuous form | **RED, rc=1**, names `r432_floor` |
| ③ | empty the anchor set | **rc=2**, never 0 |
| ④ | delete `DEFINITION.md` | **rc=2**, fails closed |
| ⑤ | neuter `homes()` to always return one home | **rc=2** — 3 of 4 controls fail |
| ⑥ | prepend all three rival sentences to the document | GREEN, and the repaired anchoring gate **rc=0** |

⑥ is the production scenario that broke the pinned gate. It holds.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| construct validity of "the same quantity" | **N/A** | it is a semantic judgement; here it was settled by *reading the object*, which does not generalise to a rule |
| author intent for each second home | **N/A** | the session transcript, not in the release |
| cross-repository | **N/A** | a second document with its own anchor set |
| multi-seed | **N/A** | deterministic; run twice, byte-identical |

`run.py` · `results/first_home_only.json`
