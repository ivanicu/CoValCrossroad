# R582 · The page scopes itself — and my verdict string ignored a failing control again

**Decision this makes safe:** whether other rows carry row 2's defect. **They do not.**

**WORLD A.** Of 10 claim rows, **2 state a decimal value** (5 and 7), and **both name how that value
moves** — claim 5 *"decaying monotonically to exactly 0 at k=all"*, claim 7 *"survives the judge
change"*. **0 rows state a value and stay silent.**

⚠ **Population = 2.** That is small, and it is stated rather than smoothed: the conclusion is that
**no row shares row 2's defect**, not that the page is broadly self-scoping.

## ⛔ Two defects in the first run, and the second is a repeat
1. **The number detector required the bold to END at the number** — `**0.0726**`. Claim 5 writes
   `**+0.0726 at k=4**`. **Tenth instrument defect of this class this session.**
2. ⭐⭐⭐ **The verdict printed `WORLD A` while its own positive control was printing `FAIL`.** That
   is §4's verdict-string row, and **R562 already caught me doing exactly this.** The branch now
   returns **UNVERIFIED** whenever a control fails.

**The second is the worse one.** A broken detector produces a wrong number that a control can catch.
**A branch that does not read its control makes the control decorative** — it fired correctly, on
screen, and changed nothing.

## Controls
- **Positive** — claim 5, which visibly names a dose curve, must read as naming movement. **Failed in
  v1 (detector blind), passes now.**
- **Negative** — claim 9 (*56 tags are 46 objects*) states no swept axis and must not. **PASS.**
