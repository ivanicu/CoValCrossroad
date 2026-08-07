# R367 — the judge can be named non-circularly, so the definition becomes applicable

**The decision this makes safe:** *"under a named judge J"* — **which J?** Name the judge that best
tracks the human. The naming survives a **definition-external** check, so it is not selecting for the
definition's own outcome.

## Result — `W_RULE_EXISTS`. Controls PASS. Two runs byte-identical.

`DEFINITION.md` carries *"under a named judge J"* four times. **Nothing in 366 rounds says which J,
or how to pick one.** A definition that cannot be applied without an unstated choice is not usable.

| rule | 2B | 0.8B | paired | own MDE | names |
|---|---:|---:|---:|---:|---|
| **A** · A2 of the full rubric *(definition-adjacent)* | 0.5087 | 0.4120 | **+0.0967** | 0.0160 | **2B** |
| **B** · ranks the **UNACCEPTABLE** response last *(definition-external)* | 0.7019 | 0.5839 | **+0.1180** | 0.0638 | **2B** |

RULE-A population **968** prompts; RULE-B population **161** — those carrying an `unacceptable`
rating — **counted, not assumed**.

## ⛔ The confound, named before the run, and why RULE-B is the whole point

The obvious rule names the judge under which the definition is **non-empty** (2B admits five, 0.8B
admits none) — **the answer I have already published.** And A2 is the *definition's own quantity*. A
rule built on it could be choosing the judge that makes my claims survive rather than the judge that
is better.

> **RULE-B reads the `unacceptable` channel — which no clause of the definition uses, and which no
> round in this campaign has ever scored a judge on.** It names the same judge.

## Controls

| | returned |
|---|---|
| **PLACEBO** — each judge against itself, each rule | 0 exactly |
| **POSITIVE** — a synthetic judge built to rank the unacceptable last | **1.0000**, above both real judges — so RULE-B *can* separate |
| **g=0** — labels shuffled across responses, 3 seeds | 0.6346 / 0.6242 / 0.5921, below 2B's 0.7019 |
| reproducibility | two runs **byte-identical** (`1f23bd88c714`) |

**Without the positive control, a null on RULE-B would have been silence** rather than *"the external
channel does not discriminate"*.

## Two qualifications the numbers make visible

- **RULE-B resolves at 1.85× its MDE**, against RULE-A's 6×. The external check agrees, with far less
  margin, on a fifth of the prompts.
- **0.8B sits essentially at the shuffle floor on the external channel** — 0.5839 against a shuffled
  0.59–0.63. It is not merely worse than 2B there; it is close to uninformative.

## What this earns

⭐ **The definition becomes APPLICABLE.** *"Under a named judge J"* stops being an instruction nobody
can follow: **name the judge that best tracks the human**, and check that naming on a channel the
definition does not use.

⚠ **Two judges can refute a rule and never establish one.** What is earned is *"not refuted, and not
circular on the one external channel available"* — not *"this is the right rule"*.

## Register

| criterion | status |
|---|---|
| **a third judge** | **NOT-ATTEMPTED-AND-NOT-CHEAP** (R357) — and two judges cannot establish a rule |
| **a second external channel** | **N/A** — `unacceptable` is the only definition-external human signal this release carries |
| **cross-release** | **N/A** — one release |

## The sentence I can no longer write

> *"the definition holds under a named judge J"* — with no way to name one.

**Name the judge that best tracks the human; here that is 2B, by both an adjacent and an external
rule.**

Artifact: `results/r367_naming_the_judge.json`, source-stamped.
