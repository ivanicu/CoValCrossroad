# R544 · The generator is greedy — register row 3 is not a re-run

**Decision this makes safe:** whether row 3 (*"more ③-any-admissible prompt-responsive generators"*)
is satisfiable by running the existing generator again.

## ⛔ The wall this round tested

R543 closed: *"nothing further can be learned about the cost without running it."* **Eighth wall of
the session, seventh false** — and written one round after logging that a wall needs the same check
as a model.

## What the source says

- **`generate_core.py:147` — `do_sample=False`.** Generation is **greedy**, so it is deterministic
  for a fixed prompt.
- **`--seed` reaches only `JT.load_second(path, convs, seed)` (line 117)** — it selects **which
  conversations**, never **what is generated**.
- **Yield is `mean k = 4.00`** on both corpora, matching `coval_core`'s k.

⭐⭐⭐ **So re-running on the home release produces byte-identical criteria whatever the seed.
Row 3 cannot come from a re-run.**

## ⭐ A defect the source documents about itself (lines 104–114)

> *"the same seed and the same count gave two DIFFERENT samples, and coverage came back
> 1,644/2,200 = 0.7473, below this round's own pre-registered 0.80 gate, with 1,870 interactions
> dropped. **The gate caught it, which is the gate working; lowering it would have been the move
> AMENDMENT 1 forbids.**"*

Its remedy is general: **"Two producers that must agree on a population should share the function
that defines it"** — alignment as a property of the code rather than of remembering to pass
matching flags.

## What it changes

**Row 3 is not a compute problem, it is a design problem.** The cost was never the obstacle:
**4.63 minutes buys the same criteria again.**
