# R436 · does clause ④ exclude anything at home? — **`W-REDUNDANT-AT-J`**, and the two releases split

**The decision this round makes safe:** whether ④ is a clause about *cores* or a restatement of the
second release's emptiness. **Neither, exactly.** ④ excludes **22 of 93** arms overall but **0 of 56
at the judge the definition names** — and the reason is the good one: at home the arms *clear* the
bar, by a wide margin.

## ⭐ The identification check came first, and this time it passed

The second release scores **top-1 picks**; the home release scores **A2 — agreement on the 6 pairwise
comparisons of 4 responses** (`corebench/score.py: cls`). Different estimands. But a criterion-free
rule induces a **full ordering**, so it is scorable on A2 exactly as the arms are, through the *same*
`cls` — reused, not reimplemented, so a difference between an arm and a rule cannot be a difference
between two scorers. **Five announced next-steps checked before running; four killed, this one
survived.**

## Result

| | |
|---|---|
| **the bar at home** | **`min_ttr` A2 0.4512** — *not* the length rule; minimum type–token ratio |
| arms scored | **93** from committed artifacts, 56 at the named judge (2B) |
| excluded by ④, overall | **22 of 93** — **every one an `_08b` variant** |
| **excluded at the named judge J** | **0 of 56** |
| best arm | `oracle_k4` **0.6353**, **+0.1824** over the bar vs MDE 0.0211 |
| weakest 2B arms | `promptecho_sham` 0.4347 (−0.0106 vs MDE 0.0372), `promptecho` 0.4465 (+0.0013 vs 0.0384) — **neither resolvedly below** |

**Population** home-release prompts with 4 response texts and a human ranking · **instrument** none
for the rules, the committed judge for the arms · **regime** k=4, A2 over 6 pairs, one annotator
drawn per prompt per seed · **multiplicity** 93 decisions, BH(q=0.10), **83 surviving**.

## ⛔ My kill tested the wrong predicate — and would have passed

It asked `0 < |EXCL| < |ARMS|`, which is **true** (22 of 93), and the verdict string would have
announced *"④ discriminates within the class the definition already admits."* **It does not.** Every
exclusion is an `_08b` arm, and **R301 measured clause ② admitting 0 arms at 0.8B** — so every arm
④ removes was already removed for another reason.

**The ledger's remedy says name an *admissible* object the clause excludes** — admissible meaning
admitted by the definition *as it stands*. The definition names its judge, and that judge is 2B. The
right predicate is exclusions **at J**, and there are none.

⚠ **`W-REDUNDANT-AT-J` was not pre-registered.** The three declared worlds don't cover *"excludes
arms, but only ones the definition already excludes."* Named honestly rather than routed into the
nearest branch — R429 had a world in prose with no branch, and the remedy is to say the prediction
matrix was incomplete, not to invent a branch afterwards.

## ⛔ And the round was not reproducible

Two runs of **unchanged code** returned **25** and **22** exclusions. `hash(str)` is randomised per
process in Python 3, and the per-prompt annotator draw was seeded with `hash(p) % 997`.

**The headline — 0 of 56 at J — was stable, which is exactly what made it dangerous:** the number a
reader would quote moved while the verdict did not, so nothing looked wrong. Replaced with md5 of
the prompt id; **two runs are now byte-identical** (22 / 0 / 83).

## ⭐ What this actually establishes: the two releases split

| release | do the definition's arms beat every criterion-free rule? |
|---|---|
| **home**, at J | **yes, by +0.1824** at the top, and no 2B arm is resolvedly below |
| **second** (R434) | **no — 0 of 7**, and all 7 resolvedly worse |

**So ④ is not redundant *in general* — it is redundant *where the definition already works*.** That
is what a sufficiency clause is supposed to look like: silent when things are fine, binding when they
are not. It earns adoption on this evidence, and the honest statement of its value is that it
*would have caught* the second release before anything was generated.

## Impossible here, named

- **the supremum over all criterion-free rules** — 30 hand-built members (R435's family, published).
  Requires a search, not an enumeration.
- **construct validity of the human ranking** — the release's own; no external gold standard.
- **that this split transports** — two releases is not a distribution of releases.
- **a causal reading of `min_ttr` being the best rule** — it is the argmax of a family, nothing more.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.

⚠ **Every number above is from the post-fix, reproducible run.** The first draft of this README and of `DEFINITION.md` quoted the *pre-fix* values (bar 0.4587, +0.1717, MDE 0.0232) — carried over from the run whose seeds were unstable. The assurance gate caught all three, which is the `retraction obliges a re-run` failure working as designed: a correction that does not carry the corrected number is not a correction.
