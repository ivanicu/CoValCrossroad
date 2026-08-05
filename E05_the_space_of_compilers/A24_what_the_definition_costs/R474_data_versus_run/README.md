# R474 · the announced split was not clean — DATA vs RUN is, and it changes who the ask goes to

**The decision this round makes safe:** how `NEXT_SITE.md` distinguishes requirements.
**By what satisfying them costs, not by where they come from.**

## ⛔ The announced split needed judgement on a third of its members

R473 closed proposing to split the enum into *"what the next site **ships**"* vs *"what a different
**experiment** establishes."* Checked kind by kind:

- `SECOND_JUDGE` — a **model** (shipped), whose use is an **experiment**. Ambiguous.
- `GOLD_STANDARD` — could be a shipped dataset **or** a study. Ambiguous.
- `GENERATOR` — **code** (shipped) whose output needs a **run**. Ambiguous.

**Three of ten.** *A partition requiring judgement on ~30% of its members relocates the mislabelling
loophole rather than narrowing it* — which was the whole point of the split. *Forty-second announced
step checked; its criterion replaced.*

## ⭐ The criterion that is answerable without taste

> **Can this be satisfied by adding rows or fields, with nothing new executed?**

| axis | kinds | n declared |
|---|---|---|
| **DATA** | `SECOND_RELEASE · SECOND_CORE · SECOND_FAMILY · MORE_ANNOTATORS · CROSS_SPACE_KEY · PROVENANCE_FIELD` | **7** |
| **RUN** | `SECOND_JUDGE · GENERATOR · GOLD_STANDARD · INTERVENTION` | **3** |

**The consequence is what makes the axis worth having, and it is not cosmetic:** a **DATA**
requirement can be **asked for** — it is a release decision. A **RUN** requirement must be **done** —
it is a research programme. **Those are different asks, of different people, on different timescales**,
and the previous phrasing collapsed them.

⭐ **All three of the precise requirements this campaign can already specify — a second core, a
cross-space key, a provenance field — are DATA.** **The largest thing blocking this work is a release
decision, not an experiment.** That is a materially different conclusion from *"we need more research"*,
and it was invisible until the axis existed.

## Controls

| control | returned |
|---|---|
| **AXIS COVERAGE** — every enum kind carries an assignment | **none missing** ✅ *a kind added without one would be a silent gap, so the gate exits 2* |
| POSITIVE — the enum gate still accepts valid and rejects invented tags | 5 of 5 ✅ |
| RESTATES chains terminating in air | 0 ✅ |
| UNDECLARED | **88 of 100**, reported as a count, never a pass |

## ⚠ What this does not fix

**The mislabelling loophole is narrowed, not closed.** An entry tagged `SECOND_JUDGE` when it needs a
gold standard still passes — both are `RUN`, so the axis does not catch it. **Within-group confusions
survive**, which is exactly what the announced step predicted and the reason to say the surface is
*smaller*, not *gone*.

⚠ **And the split is over the declared subset only.** 88 entries remain undeclared, so **7/3 will
move** — it is a current reading, not a final ratio.

Findings and their scope live in `DEFINITION.md`. `NEXT_SITE.md` carries the specification.
