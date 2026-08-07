# R222 — the compiler factorial

**Arc E05·A16.** The decision this makes safe: *when the compiled core differs from the full rubric,
which of the compiler's operations is responsible, and on which axis?*

Every round in this project has reported compilation as **one number**. The official pipeline is
documented as four operations — rewrite negatives into positive form · merge semantic duplicates ·
select ≤4 highly-rated compatible non-redundant criteria · drop the weights — and adding truncation
as its own operation gives five. This runs all **2⁵ = 32** on/off combinations and
Shapley-attributes each axis to each operation, exactly (no sampling: 32 coalitions is the whole
lattice).

---

## A derivation, found while building it, that changes what the factorial means

Polarity normalisation replaces `(w, s)` by `(−w, 1−s)` for `w < 0`. Its contribution to a response
is

```
−w(1 − s)  =  −w + w·s
```

— the original term **plus a constant that does not depend on the response**. A constant shifts
every candidate equally, so every `argmax`, every pairwise relation and every ranking is unchanged.
Exactly, not approximately.

> **The representational content of "rewrite negatives into positives" is decision-null.**

Measured, as a check on the algebra rather than as evidence: `human_agreement` is `0.686002` with
and without it, `pairwise_preservation` is `1.000000` both ways.

This is a **DERIVATION**, and it is labelled one. Its consequence is what matters: anything the
rewrite costs must come from the **text**, which needs a judge pass and is `NOT IDENTIFIED` here.
But the operation is **not inert in combination** — selection keeps the *highest-rated* criteria,
and flipping a `−8` to a `+8` moves it from the bottom of that ordering to the top:

| the rewrite applied on top of… | change in human agreement |
|---|---|
| Full (nothing else) | **+0.0000** — exactly as derived |
| select + truncate | **+0.0041** |

That interaction is invisible to any design that reports compilation as one number, and it is the
reason to run a factorial rather than an ablation.

---

## Shapley attribution — what each operation contributes

Positive = the operation **improves** that axis, averaged over every coalition it can join.

| operation | human agreement | not inverted | gauge stability | provenance | brevity (rules saved) |
|---|---:|---:|---:|---:|---:|
| `R_polarity` | +0.0017 | −0.0065 | **+0.0343** | +0.0022 | 0.00 |
| `M_merge` | +0.0000 | −0.0058 | −0.0009 | **−0.0227** | 0.33 |
| `S_select` | −0.0061 | **−0.0615** | −0.0158 | +0.0086 | 5.33 |
| `T_truncate` | **−0.0164** | −0.0326 | 0.0000 | −0.0031 | 5.33 |
| `W_dropweights` | −0.0043 | −0.0074 | −0.0036 | 0.0000 | 0.00 |

### What this says

- **Truncation is the expensive operation for prediction** (−0.0164), and **selection is the
  expensive one for causal direction** (−0.0615 on not-inverted: choosing *which* four is what
  makes a source intervention move the compiled object the wrong way).
- **Polarity normalisation is the only operation that improves instrument stability, and by an
  order more than anything else moves it** (+0.0343). The official-like arm's gauge spread is
  `−0.0571`; strip the rewrite and `S+T` alone is `−0.1240`. **The rewrite more than halves the
  compiled rubric's dependence on which judge scores it** — plausibly because "does this response
  do X?" is a more answerable question than "does this response avoid X?". This is a defence of the
  official design that this project had not previously found, and it was invisible while
  compilation was reported as one number.
- **Merge is the only operation that destroys the audit trail** (−0.0227 provenance, and it is the
  only one that can) and it buys **0.33 of a rule**.
- **Dropping the weights costs almost nothing on human agreement** (−0.0043), which is R220's
  `H_sign_only` result arriving by a second route.

---

## What is not admissible here

- **`pairwise_preservation_vs_Full` is DEGENERATE and is marked so in the output.** R221 measured
  that on 100% of prompts some single criterion alone reproduces the whole 4-response ranking, with
  a median of 3 tied. An axis defined as agreement with Full's own decision cannot rank compilers.
  It is printed because suppressing it would hide the reason the other axes were chosen.
- **Order.** The canonical order is polarity → merge → select → truncate → drop weights. Shapley
  attributes across **subsets**, not across orders; a different canonical order is a different
  compiler and would need its own run. Stated, not hidden.
- **`R_polarity` is implemented as the arithmetic operation, not as a rewrite of text.** The
  textual half is `NOT IDENTIFIED` without a judge pass, and that is the half the official pipeline
  actually performs.
- **`M_merge` uses lexical Jaccard ≥ 0.5** as its notion of "semantic duplicate". That is a proxy
  for the property, sound in one direction only: a lexical match is evidence of duplication, a
  lexical mismatch is not evidence of its absence.

## The sentence that can no longer be written

*"Compilation costs X."* It costs five different things on five different axes, two of the
operations pay for themselves, and one of them — the rewrite everyone treats as cosmetic — is the
single largest **positive** contribution to instrument stability in the whole lattice.
