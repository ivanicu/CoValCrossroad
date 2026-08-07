# R575 · A dead instrument returned seven identical zeros, and I wrote a verdict under it

**Decision this makes safe:** none. **PARTIAL, and the instrument failure is the product.**

## What direct reading established
| gate | fleet | caps |
|---|---|---|
| `what_did_each_check_actually_read` | **46** — every `assurance/*.py` | ⏱ yes |
| `backfilled_findings_are_rederivable` | **265** — every round's `run.py` | ⏱ yes |
| the four non-cappers | `run(<named target>)` — a handful | no |

**Fleet size is CONSISTENT with the split. It is not established** — the fleet of `attack_the_suite`
and of the four non-cappers was never measured. **Consistency is not identification.**

## ⛔⛔ The instrument, and the signature I walked past
I built a static counter for `run(` call sites. Its regex required **a quote or `f` immediately
after `run(`** — and every call in this suite is `run(check)`, **a variable**. It returned:

```
cappers [0, 0, 0]   non-cappers [0, 0, 0, 0]
```

**And I printed "these do NOT separate" underneath it.** A verdict computed on an instrument that
could not see anything.

⭐⭐⭐ **Uniform output across a population an instrument was built to discriminate is the cheapest
possible signature of a dead instrument** — cheaper than a positive control, because it needs no
extra run. **Seven identical zeros should have stopped the sentence before it was written.**

## ⚠ Ninth instrument defect of this class, this session
`\b` before an underscore · `c2` inside a UUID · a wrapped docstring · `tail` for a count (×3) · an
interpreter alias · a loop-context grep matching 1 of 7 · now a quote-anchored call matcher.

⭐ **And the escalation is the point: this is the third consecutive round where the pattern failed,
and each time the fix was to READ THE OBJECT instead.** Reading gave 46 and 265 in one command.
**Every pattern I have written this session to avoid reading has cost more than reading would have.**
