# R844 · does the OTHER WRITER's deflation transfer to `coval_core`?

**Arc A24 — what the definition costs.**

## ⭐⭐ THIS IS THE LINE §2 CALLS STRUCTURALLY IMPOSSIBLE

The register says *independently replicated — N/A: needs a second team or a second release.*
**This repository has two concurrent writers** (entry 1360, D8: a reflog commit this session did
not make, two shell-snapshot ids among live processes, and the other writer's own commit body
saying so). So the impossible line is **available**, and §2.5 names what to do with it: *take a
claim the other designer derived independently and run it against yours.*

Their **R843** (`d4205a7e`), reached with no input from me:

> *"A1's relevance vector sent to the WRONG prompt scores **0.552705** against A1's own
> **0.551732** and A0's **0.540676** — the permuted selector is as good as the real one. So A1's
> gain over A0 is NOT prompt-specific fit … what it buys is a better fixed subset."*
> *"REMEDY: the contextualisation estimand is **A1 minus ITS OWN PLACEBO**, never A1 minus A0."*

⛔ **If that transfers, R841's `coval_core − generic` is the wrong estimand** and my result is about
a better fixed subset rather than about reading the conversation — a direct threat to clause ②, and
**one I could not have generated from inside my own framing.**

## ⭐ CONTROLS

| control | result |
|---|---|
| **PLACEBO / kill precondition** `coval_core` − itself, both metrics | **+0.00e+00 exactly · PASS** (n = 968 paired prompts) |
| **NEGATIVE** two arms that BOTH never read the prompt (`genericpool16` − `generic`) | **−0.0091 graded (RESOLVED)** · −0.0031 exact (contains 0) |

⚠ **The negative control is the quantitative answer to their challenge, not a formality**: it
measures exactly the mechanism they identified — *a better fixed subset* — and finds it **real and
worth ~0.009 graded.**

## ⭐⭐ RESULT — world B, on every annotator (no draw, so no seed and nothing to be unstable about)

| estimand | metric | obs | 95% CI | MDE | verdict |
|---|---|---:|---|---:|---|
| **(a) core − its OWN wrong-prompt sham** *(their estimand)* | graded | **+0.0709** | [+0.0617, +0.0801] | 0.0133 | **RESOLVED** |
| | exact | **+0.0265** | [+0.0198, +0.0329] | 0.0093 | **RESOLVED** |
| **(b) sham − never-reads-a-prompt pool** | graded | **−0.0466** | [−0.0558, −0.0376] | 0.0129 | RESOLVED |
| | exact | **−0.0162** | [−0.0224, −0.0098] | 0.0088 | RESOLVED |

⭐ **The deflation does NOT transfer.** Their A1's wrong-prompt arm beat its own real arm by
**+0.001** — indistinguishable. `coval_core` beats its wrong-prompt arm by **+0.0709 graded**,
roughly **70× larger** and resolved by its own MDE.

⭐⭐ **And (b) is BELOW zero — the poison signature.** Misdirection *actively hurts*: the wrong
prompt lands **beneath** the arm that reads no prompt at all. **That is a stronger statement than
"reading helps": it says WHICH conversation is read matters, not merely that one is.**

⭐⭐⭐ **The fixed-subset mechanism they found is real here too and cannot explain the gap:**
`0.0709 / 0.0091 ≈ 7.8×`. Their mechanism exists; it is the wrong size.

## ⭐ WHAT THIS DOES TO THE DEFINITION

Clause ② previously rested on `coval_core − generic` (R841: +0.0151 graded, +0.0073 exact). **R843's
remedy demands the more conservative placebo estimand instead — and that one also resolves, and
larger.** So the clause survives a challenge designed by someone who could not see my framing, under
*their* estimand rather than mine.

## ⚠ WHAT IS NOT CLAIMED

- **Not a refutation of R843.** Their A1 finding stands on their arm. **What this establishes is that
  the deflation is ARM-SPECIFIC** — prompt-*reading* is not automatically prompt-*specific*, and it
  has to be measured per arm rather than assumed either way. That is the transferable lesson.
- **Not causal.** No intervention on the compiler; this says the wrong prompt scores worse, never why.
- **Not cross-release.** One release, one judge family.

## STRUCTURALLY IMPOSSIBLE HERE
| criterion | what it would require |
|---|---|
| causally identified | an intervention on the compiler, not a re-scoring |
| cross-release / cross-domain | a second release |
| construct validated | an external gold standard for the agreement metric |

⚠ **N/A with what each would require — never "planned".**
⭐ **But `independently replicated` is no longer on this list for this round**, and that is the
finding this round exists to record.
