# R526 · The mechanism works where the invocation is recorded

**Decision this makes safe:** whether R525's "failed variant run" attribution is an inference or a
tested one. **This round is CLOSURE, labelled as such** — it protects an existing conclusion rather
than opening a new world, and its kill condition did not fire.

## ⛔ First — the wall, fifth of this shape

`3cb7236` closed saying *"the only place that could say is whatever produced them."* **False.**
`corebench/rebuild_selection_08b.sh` records a natural experiment for exactly this mechanism:

```bash
frozen() { select_core.py --full-npz 0.8B --select-npz 2B --tag-suffix _08b  ... }
rerun()  { select_core.py --full-npz 0.8B                 --tag-suffix _08bR ... }
```

**Five arms get both treatments, and all five are satisfaction-consuming rules** — the ones the
source says *"change IDENTITY, not just score"* when re-run under a different judge.

## Result — WORLD A

| arm | `_08b` vs `_08bR` |
|---|---|
| `greedy_k4_fit1` | **differ** |
| `indep_k4_fit1` | **differ** |
| `oracle_k4` | **differ** |
| `topvar_k4` | **differ** |
| `topwvar_k4` | **differ** |

**0 of 5 identical.** Pre-registered kill was ≥1 identical, and it did not fire.

## Controls
- **Positive** — `_08b` must differ from the **home-judge** arm of the same name, else the whole
  `_08b` family is a mislabelled copy: **5/5 differ. PASS.** The judge swap really changed the
  artifacts.
- **Negative** — an artifact is self-equal and a shuffled copy is not: order-sensitive. **PASS.**
- **No noise floor** — exact equality, as in R523–R525.

## What it settles

⭐⭐⭐ **`--select-npz` does change identity when invoked.** So R525's reading of the three
home-judge identities is confirmed as far as this site can confirm it: **those were runs where the
variant treatment was never applied**, not runs where the mechanism failed to fire.

⚠ **Stated limit, and it is real:** this tests the **mechanism** on the second-release population.
The home-judge A/B invocations are genuinely unrecorded, so this cannot observe what was typed
there — it can only establish that the flag is capable of doing what R525 assumed it does.

**Impossible here:** recovering the home-judge invocations. The repository carries
`rebuild_selection_08b.sh` and no equivalent for those tags.
