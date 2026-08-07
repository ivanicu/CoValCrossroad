# R618 · What a third object must provide — the register, finally written as a specification

**Decision this makes safe:** what to check a next site against, before spending anything on it.

⚠ **CLASSIFICATION, STATED: this is PRODUCTION, not Frontier.** It converts thirteen rounds of
measurement into a requirement. **A specification cannot be surprised by data**, so the derivation is
labelled as one — and the single failable part is bolted on.

| a release must carry | it serves ②'s phrase | home | second |
|---|---|---|---|
| a prompt / user turn | *…for a conversation…* | ✓ | ✓ |
| multiple responses per unit | *…scores RESPONSES…* | ✓ | ✓ |
| a human preference target | *…better THAN…* | ✓ | ✓ |
| **a released criterion POOL** | *…drawn from the RELEASED POOL…* | ✓ | ⛔ |
| **a released CORE** | *…a CORE scores…* | ✓ | ⛔ |

## The one thing that could fail — and it is the whole validation
**A specification that cannot re-derive what is already known is wrong regardless of how reasonable it
reads.** Pre-registered kill: any disagreement with R603 ⇒ **withhold the spec**, not publish it with a
caveat.

> **home evaluable ✓ · second NOT evaluable ✓ · missing set matches exactly {pool, core} ✓**

**PASS.** F reproduces R603 on both objects it can be checked against.

## Controls
| control | returned |
|---|---|
| **positive @ g=0** — home stripped of rubric and core | **not evaluable**, missing exactly those two — **the check is not vacuous** |
| **negative** — a release carrying only fields ② does not need | not evaluable, **5 of 5 missing** |
| **placebo** — a release carrying every needed field | evaluable; **adding an irrelevant field changes nothing** |

⭐ **The g=0 control is what makes this more than a restatement**: stripping the home release reproduces
the second release's exact failure, so the specification discriminates on the fields it names rather
than on which file it is reading.

**IMPOSSIBLE, named — and it is the important line:** **F is NECESSARY, NOT SUFFICIENT.** A release can
carry all five fields and still fail to support ②. **R602 measured the second corpus as disjoint in
content** — exact overlap 0, token-Jaccard at the shuffled floor — **and no schema check can see
that.** This screens out impossibilities; **it cannot certify a site.**

## ⛔ Check #217, and a pattern that is now standing
R617 closed with *"**every** axis of this arc now measures artifact FORM"*. **R614 measured position,
R615 the verdict-class distribution, and R617 itself measured README prose and code identifiers.**

⚠ **Fourth quantifier error in six closing lines** (#212 "every", #213 units, #216 "evidential
quality", #217 "every"). *That is no longer an occasional slip — it is a standing property of the
sentence written last, when the round's controls have fired and the attention they held has been
released. The commit gate catches the numeric ones; the universal ones pass it.*

## The sentence I can no longer write
> *"the second release cannot carry ② because it is a different kind of object."*

**It cannot carry ② because it lacks two specific fields**, and now anything else can be checked for
them in one pass.

## NEXT
The gate catches bare counts in a NEXT line but not universals — four have passed it. **Extend
`next_line_quantifiers_are_computed.py` to flag `every` / `all` / `none` / `only` over the corpus's own
nouns**, then run it over the frozen shas to see how many historical closing lines it would have
caught. If the count is large, the gate has been measuring the easy half of its own subject.
