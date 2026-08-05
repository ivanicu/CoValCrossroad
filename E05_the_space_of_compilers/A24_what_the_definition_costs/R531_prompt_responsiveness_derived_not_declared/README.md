# R531 · Prompt-responsiveness, derived rather than declared

**Decision this makes safe:** whether R530's 1.29 MDE was measured over the right population.

## ⛔ First — the defect in my own previous round

R530's filter was literally:

```python
responsive = [a for a in anyadm if a in ("gen","gen_sham") or a.startswith("promptecho")]
```

**A hardcoded literal — the exact defect R520 logged in `USES_PROMPT_LABELS`, committed three
rounds later by its author.** And the closing line then asserted *"gen is the ONE prompt-responsive
③-any arm in the census"*, which a hand-written tuple cannot establish.

## The derivation

An arm is **index-varying** iff its selected criterion index set differs across prompts — a property
of the `.npz`, needing no declaration.

**Result: 18 of 41 arms vary; 14 are also ③-any-admissible.**

| arm | c2 | MDE | shortfall |
|---|---|---|---|
| ⭐ `gen` | −0.0153 | 0.0119 | **1.29** |
| `full` | −0.0310 | 0.0119 | 2.60 |
| `random_k12_s0` | −0.0332 | 0.0122 | 2.74 |
| … 10 more, to `full_sham` | −0.0832 | 0.0143 | 5.83 |

⭐⭐⭐ **WORLD A: `gen` really is the closest, so R530's 1.29 MDE survives.** What was wrong is only
the word **"one"** — the derived set has **14** members.

## Controls
- **Positive** — `coval_core` must come out VARYING and `generic` BLIND. **PASS.**
- **Negative** — an arm that is index-varying while **prompt-blind by construction**, to show the
  proxy measures index variation and not semantics: **`random_k6_s0`. PASS.**
- ⚠ **The negative control took two repairs, both instructive.** First it named `random_k4_s0`,
  which **R294 skips** (it is the clause-① comparator), so `cls.get()` returned `None` — the control
  **could not run** rather than returning a wrong answer. Loaded directly it came out **FIXED**:
  at small k the same indices exist in every prompt. Only at **k ≥ 6** does the available pool
  differ per prompt, making the drawn set vary. **My expectation was wrong twice; the instrument
  was right both times.**

## The proxy limit, demonstrated rather than asserted

`random_k6_s0` is index-varying and prompt-blind by construction. **So index variation is sound for
*"the criteria differ by prompt"* and NOT for *"the criteria were written for this prompt."***
R530's earlier claim to a proxy limit was itself unverified until this arm was found.

⭐ **A fact the round surfaced in passing, and worth carrying:** the **clause-① comparator
`random_k4_s0` uses the SAME criterion indices for every prompt.** Nothing in the record said so.
