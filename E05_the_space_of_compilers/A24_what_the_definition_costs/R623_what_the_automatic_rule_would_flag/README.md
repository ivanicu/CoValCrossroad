# R623 · The rule I proposed would flag half the document, and 84% of it for punctuation

**Decision this makes safe:** whether to build the automatic anchoring rule. **No, not as stated.**

| | pairs | PASS | **C1** no citation | **C2** no artifact | **C3** real mismatch |
|---|---|---|---|---|---|
| `DEFINITION.md` | 900 | 391 | **437** | 4 | 68 |
| `STATEMENT.md` | 158 | 130 | **10** | 0 | 18 |
| **total** | **1058** | 521 | **447** | **4** | **86** |

**537 of 1058 pairs (50.8%) would flag, and C3 — the only class that is evidence about a number — is
16.0% of them.** Pre-registered kill was C3 ≥ 33%. **World B.**

## ⭐ The design law this buys, and it is worth more than the rule
> **A gate satisfiable by formatting will be satisfied by formatting.**

Facing 447 `no citation` failures, an author does not go and check values — **they add citations.**
The rule would produce a document that passes and a set of numbers no better verified than before,
**while reading as though provenance had been established.** That is the failure R621 found, rebuilt
deliberately and at scale.

## ⛔⛔ And my own check was wrong by two orders of magnitude
Check #222 correctly caught the false universal *"every round's results JSON carries its values"* —
then asserted **~56% (345 of 614)**. Measured: **322 of 326 = 98.8%**, false by **4 rounds**.

**The 614 is the round index across ALL arcs; the rule's population is A24.** ⭐ *So the check that
caught an uncomputed magnitude attached an uncomputed magnitude of its own — and had I built on it,
the round would have been designed around a scarcity that does not exist.* **A check on a closing
line is itself a claim and inherits every rule the closing line has.**

## ⛔ The negative control failed, and I had wired it not to count
`0.5451 (R294)` — a value R622 classes **T1, gate-verified** — **flags C3** under the proposed rule.
**The rule condemns a number the current gate already verifies**, because R294's artifact is not in
A24's tree.

⚠ **And I set that control advisory in code** (`neg_ok = True`, reported not asserted). That is §4's
*check that cannot fail*, built by me, in the round that was measuring buildability. **Its result
does not change the verdict — it strengthens it** — but the wiring was wrong and is recorded as such.

## Controls
| control | returned |
|---|---|
| **positive** — a fabricated decimal planted in a paragraph citing an artifact-bearing round | flags **C3** — PASS |
| **g=0** — the same paragraph unmodified | **no such flag** — PASS |
| **placebo** — a paragraph citing a nonexistent round | **C2, not C3** — PASS |
| **negative** — a known T1 value in its own paragraph | **flags C3** — ⛔ FAIL, and advisory by my own wiring |

**MULTIPLICITY:** 1058 pairs × 3 causes across both documents + 4 controls. All reported.

⚠ **R622's contamination is not repeated:** the planted literal is **assembled at runtime** and
appears in this round's artifact **only inside a sentence, never as a value position** — so it cannot
launder itself into "anchored" the way R621's `0.9187` did.

**IMPOSSIBLE, named:** **C3 is an UPPER bound.** The paragraph is the binding unit, so a paragraph
citing several rounds passes if **any** of them carries the value, and a decimal cannot be tied to
one cited round without syntax these documents do not have.

## The sentence I can no longer write
> *"a gate could require any decimal to match a value position in the artifact of a round the same
> paragraph cites."*

**It could — and 84% of what it said would be about where citations sit, not about whether numbers
are real.**

## NEXT
Both remaining designs need the document to bind a decimal to a **specific** round, which no current
syntax does. **Before proposing a third rule, measure whether that binding is even recoverable**:
take the 86 C3 pairs and check how many sit in paragraphs citing exactly **one** round, because those
are the only ones where paragraph-level evidence and value-level evidence coincide — and if that
count is small, the binding must be authored, and no gate can be built from what is already written.
