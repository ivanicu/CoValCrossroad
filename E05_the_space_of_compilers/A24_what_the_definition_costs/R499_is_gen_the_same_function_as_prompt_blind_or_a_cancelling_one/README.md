# R499 · Clause ②'s gap is inside the floor because the arms agree — and the statistic that said otherwise was blind

**Decision this makes safe:** whether clause ②'s `−0.0067` gap for the best ③-admissible prompt-aware
arm is a real wall or an artifact of averaging. **It is a real wall.** And the round's own first
answer — that it was an artifact — was killed by a gauge test before it left the terminal.

## The reframe this round rests on

R494–R497 spent four rounds decomposing `coval_core − gen`. **Clause ② does not compare against
`coval_core`.** It compares an admissible arm against the best *generalising prompt-blind set*,
cross-fitted at **0.5404**. The best ③-admissible prompt-aware arm is `gen` at **0.5337** — a gap of
**−0.0067**, inside the **0.0122** floor. **Four rounds decomposed a difference the definition does
not turn on.**

## What was measured, and what killed it

Two worlds, ontologically different: **A** the arms compute nearly the same thing · **B** they differ
reliably per prompt and cancel in the mean. B implies clause ② is the wrong instrument.

The first pass said **B**, emphatically: `gen − generic` had reliability **+0.9335** and true sd
**0.1320 = 3.77×** its own measured noise. Positive control passed — the script independently
recovered R497's **+0.9355** (got **+0.9358**) from fresh code. Placebo (`gen` vs itself at different
draws) returned **−0.0076**.

⛔ **Then the gauge test.** Is `r ≈ 0.93` a property of *the difference*, or merely of *being two
distinct criterion sets*?

| pair | r | true sd | × noise |
|---|---|---|---|
| `random_k4_s0 − random_k4_s1` — **two seeds of one procedure** | **+0.9581** | **0.1553** | **4.76** |
| `random_k4_s1 − random_k4_s2` — same | **+0.9582** | 0.1587 | 4.80 |
| `gen − generic` — the claim | +0.9335 | 0.1320 | 3.77 |

**A pair with no functional difference scores HIGHER on every statistic than the pair I was calling
"cancelling functions."**

## The null was wrong, and that is the transferable part

My placebo was `gen` against **itself**. That removes the arm difference entirely, so it asks *is the
instrument noisy* — never *does a difference between two arms carry meaning*. **The instrument's unit
was "two distinct criterion sets differ per prompt"; the claim's unit was "prompt-awareness produces
a functional difference." Not equal.**

The correct null is **a pair of arms with no functional difference** — same procedure, different
seed. Against it:

| claim | r | pctile | true sd | pctile |
|---|---|---|---|---|
| null: 3 independent pairs × 3 offsets | +0.9532 … +0.9604 | — | 0.1525 … 0.1589 | — |
| `gen − generic` | +0.9349 | **0.0%** | 0.1314 | **0.0%** |
| `gen − genericpool16` | +0.9358 | **0.0%** | 0.1297 | **0.0%** |
| `coval_core − gen` | +0.9354 | **0.0%** | 0.1345 | **0.0%** |

## Verdict, with its resolution stated

**World B is dead, decisively and independently of resolution** — it required the real pairs to
*exceed* the null, and they fall *below* it. A kill in the wrong direction needs no p-value.

**World A survives: prompt-awareness buys nothing per-prompt either. Clause ② is a genuine wall for
③-admissible prompt-aware arms, not an artifact of aggregation.**

⚠ **The refinement is under-resolved and is reported as directional only.** All three sit *below* the
whole null — suggesting `gen` lands **closer** to a prompt-blind arm than two prompt-blind random
arms land to each other. But k=4 offers only **3 independent no-difference pairs**, so `n_eff = 3`
and the permutation floor is `p ≥ 0.25`. **Directional, not resolved.** Sharpening it needs more
same-k same-procedure arms.

## What this costs R497

R497's headline — *"the per-prompt deficit is reliable at r = 0.9355, true sd 3.8× noise, so the
target is emphatically present"* — **is retracted.** The same statistics on two arms with no
mechanism come out higher. R497 measured *"these are two distinct criterion sets"*, not *"there is
something to explain."* Its **measured noise floor stands**; its interpretation does not. The four
nulls of R494–R496 are unaffected — they were nulls, and this makes them less surprising.
