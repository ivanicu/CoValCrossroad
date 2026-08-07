# R1065 — does the currency gate compare the statement to the ARTIFACT? ⛔ **No. It certifies prose against prose — and it printed the falsified numbers while passing.**

**The decision this round makes safe:** how to read every currency PASS in this arc. **As "these words
appear in the document"** — never as "the statement is true of the measurement."

## The intervention

| cell | mutation | gate exit |
|---|---|---:|
| baseline | none | **0** |
| **POSITIVE** | delete **every** anchor of the target fact from the statement | **1** |
| **⭐ INTERVENTION** | `globs` **79 → 4321**, `dead` given a **fabricated** entry — **statement untouched** | **0** |
| **SHAM** | mutate a key no pattern mentions | **0** = baseline |
| **PLACEBO** | restore everything | **0** = baseline |

⭐⭐ **And the gate printed the mutated values as it passed:**

```
R1064  every registered artifact glob resolves, and the skip is now loud = globs 4321, dead 1
```

**It read the artifact, displayed the falsified numbers, and its verdict ignored them.**

## Why — read from the source, not inferred

Each fact is `(round, description, value_string, patterns)`. `value_string` is an f-string built from
the loaded artifact and is **printed**. `patterns` are **hand-written literals matched against
`DEFINITION.md`**. **Nothing in the match consumes the artifact.** Its only roles are to **exist**
(R1063's finding) and to **supply a display string**.

## ⛔ The positive control failed first, and it was right to

My first statement mutation redacted **one** anchor and the gate stayed **green**. The gate is
`ok = any(...)` — a fact with two patterns survives losing one. **Redacting one anchor and calling it
a control would have made a working gate look broken.** The control must defeat **every** anchor; it
then went red (exit 1) as designed.

## What this does and does not license

⭐ **This is a SCOPE finding, not a defect verdict.** A currency gate may be *meant* to ask *"did the
statement get updated?"* — a real question, and the one it answers well. **What is not licensed is
reading its PASS as *"the statement agrees with what was measured"*** — which is how I have read it in
every round of this window.

## Controls

- **NEGATIVE** — unmutated repository is **green**: True. Without it the baseline is not a baseline.
- **POSITIVE** — statement mutation turns it **red**: True (after being corrected). A gate never shown
  to fail cannot evidence a pass.
- **SHAM** — mutating an artifact key no pattern mentions leaves the verdict **unchanged**: True. This
  is what shows the intervention result is not "any file edit is ignored."
- **PLACEBO** — full restore reproduces the baseline: True.
- **SAFETY** — both mutated files restored in a `finally`; worktree verified clean afterwards.

## IMPOSSIBLE here

- **whether a text-only gate is the WRONG design** — that is intent, not behaviour.
  **SETTLES: OUT-OF-RELEASE** for the intent; **IN-RELEASE** for the behaviour, which is what this
  round measured.

`run.py` · `results/gate_coupling.json`
