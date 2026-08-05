# R473 · a requirement is an **enum**, not prose — the check I announced would have inherited the defect it fixes

**The decision this round makes safe:** how the 88-entry worklist gets converted without the
conversion being cosmetic. **By enum, not by phrasing.**

## ⛔ The announced check would have repeated R472's own error

R472 closed proposing that *"a converted entry must name a **concrete artifact** the next site would
ship."* **Tested by pattern, "names a concrete artifact" is a phrasing test** — adding the right words
without adding a requirement passes it. **That is exactly how R472's own classifier failed**: it
measured phrasing and I reported it as content. *Forty-first announced step checked; its instrument
would have inherited the defect it was built to remove.*

## ⭐ The fix is the constitution's own rule — HB8

> *If it can be an enum, it may NOT be text.*

An entry declares `REQUIRES: <kind>` from a **closed set**, or `SCOPE_ONLY`, or `RESTATES: R###`.
**An enum cannot be gamed by wording** — a wrong tag is a wrong tag, and an invented one is rejected
by **membership** rather than by judgement.

The ten kinds are drawn from what this campaign was **actually blocked on**, not invented:
`SECOND_RELEASE · SECOND_JUDGE · GOLD_STANDARD · GENERATOR · MORE_ANNOTATORS · INTERVENTION ·
SECOND_FAMILY · SECOND_CORE · CROSS_SPACE_KEY · PROVENANCE_FIELD`.

⚠ **`SCOPE_ONLY` and `RESTATES` are not escapes.** Declaring `SCOPE_ONLY` is a **claim** that nothing
would lift the entry. A `RESTATES: R###` chain must terminate in a round carrying a real declaration —
checked, and currently **0 dangling**.

## Result

| | n |
|---|---|
| REQUIRES | 10 |
| SCOPE_ONLY | 2 |
| RESTATES | 0 |
| BAD_KIND | 0 |
| ⚠ **UNDECLARED** | **88** |

**PASS — 12 declared entries, all well-formed; 88 remain undeclared, which are not passes.**

## ⛔ Two defects in the gate, both caught by running it

1. **It passed with an empty declared population.** The first run reported *"PASS — every DECLARED
   entry is well-formed"* with **zero** declarations. **§4's *empty population passes*** — and the
   selftest uses **synthetic** strings, so it was no evidence the gate works on real entries. **Now
   exits 2 when nothing is declared.**
2. **13 tags inserted, 12 parsed.** One landed on a continuation line the parser merges into a
   neighbouring entry. ⚠ **Stated rather than rounded** — R472's lesson was that a count whose parts
   don't reconcile is the cheapest signal available, and 13 ≠ 12 is that signal.

## Controls

| control | returned |
|---|---|
| **POSITIVE** — accept a valid tag, reject an invented one | 5 of 5 cases ✅ including `REQUIRES: A_BETTER_VIBE` → `BAD_KIND` |
| RESTATES chains terminating in air | **0** ✅ |
| **EMPTY POPULATION** | exits **2**, never 0 |
| UNDECLARED | reported as a count, never as a pass |

## ⚠ What this gate cannot do, stated in its own output

It checks a declaration **exists** and is **well-formed**. It **cannot** check the declaration is
**true** of the entry — a gold-standard limit tagged `SECOND_JUDGE` passes. **The enum removes the
wording loophole, not the mislabelling one**, and naming which is which is the point of having the
gate rather than a habit.

Findings and their scope live in `DEFINITION.md`. `STATEMENT.md` is the residue; `NEXT_SITE.md` is the
specification; this is its enforcement.
