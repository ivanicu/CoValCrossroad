# R1015 · a pairing-dependent quantity that does separate — and it is post-hoc

**THE DECISION THIS MAKES SAFE.** Whether clause ②'s A2 is the only pairing-dependent content
available. **It is not.** But the alternative was chosen after seeing the rival, and that is recorded
as loudly as the result.

---

## The quantity

**Criterion DISCRIMINATIVENESS** — the variance of a criterion's satisfaction across **this prompt's
own** responses, averaged over criteria then over prompts.

- needs the criteria **and** the prompt's responses → **pairing-dependent**, so R1014's closure does
  not rule it out
- reads **no human labels** → satisfies clause ③ automatically, and is **independent of the comparator**

## The result

| arm | discriminativeness | Δ (core − arm) | lo | hi | resolvable |
|---|---:|---:|---:|---:|---|
| **`coval_core`** | **0.030628** | — | | | |
| `topw_k3` | 0.025345 | +0.005283 | +0.004300 | +0.006245 | **yes** |
| `topw_k4` (+ `_detA`, `_detB`) | 0.025579 | +0.005050 | +0.004176 | +0.005926 | **yes** |
| `topw_k6` | 0.025683 | +0.004945 | +0.004135 | +0.005746 | **yes** |
| `topw_k8` | 0.025753 | +0.004876 | +0.004097 | +0.005658 | **yes** |

**Resolvable against all six** — where A2 (R1011) was resolvable against one.

## ⭐ The control the round is built on

**Discriminativeness must DROP for the sham** — the same criteria on the **wrong** prompt. If it did
not, the quantity would be text-only by R1014's argument and **the whole round would be void.**

```
core − sham = +0.013993  [+0.012817, +0.015174]      PASS
```

⭐⭐ **The pairing effect is ~2.8× the family effect** (0.0140 vs 0.0050). That ratio is the scale
worth carrying: most of what this quantity measures is *being on the right prompt*, and the
core-vs-topw gap is the smaller residue.

| control | result |
|---|---|
| **POSITIVE** | the sham drops resolvably — the quantity **is** pairing-dependent |
| **NEGATIVE** | an arm against itself: **exactly 0** |
| **PLACEBO** | `topw_k4_detA` vs `_detB`, deterministic pair: **exactly 0**, interval width **0.00000000** |
| **NOISE FLOOR** | that placebo width — a known-zero effect measured in the same design |

## ⛔⛔ And it is post-hoc — the part that must not be lost

The quantity was chosen **after** R1011 identified `topw` as the rival that needed excluding.

> **A property selected because it excludes the known rival is "the definition describes the
> instance" wearing a better metric.**

What would turn it into a clause rather than a fitted separator:
1. a **reason** to require discrimination that does not mention `topw`, and
2. an admissible object it excludes **for that reason**.

**Neither is established here.** This is recorded as a **candidate**, not a clause, and the statement
carries the caveat with the number.

## ⚠ Two further bounds

**A discriminative criterion is not thereby a good one.** This asks whether the quantity separates,
never whether separation means quality — a criterion can discriminate by being idiosyncratic.

**Every satisfaction value routes through the release's judge**, so this is a claim about what that
judge scores, not about the criteria in the abstract.

## Alternatives considered

**Report it as the missing clause ⑤.** Refused, and the refusal is the round's discipline: the arc has
already killed five clauses that were each true of the object and false as definitions. Proposing a
sixth, chosen to exclude the arm that embarrassed the fifth, without a reason independent of that arm,
would be the same error a sixth time.

**Skip the sham control because the quantity is "obviously" pairing-dependent.** Refused — obvious is
what R1013's sweeping derivation was, and it was refuted by measurement one round later. The sham is
what makes the result admissible rather than plausible.
