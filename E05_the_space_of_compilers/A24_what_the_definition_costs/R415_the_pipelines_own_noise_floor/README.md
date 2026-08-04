# R415 — re-running the same arm at the same judge shifts its mean by 13× the effect under study

**The decision this makes safe:** *can a single committed `sat_*.npz` be treated as the value of an
arm?* **No — not at the judge where it can be checked, and at 2B it has never been checked at all.**

## Result — `W_FLOOR_BINDING`. Self-control exact. **No GPU.**

| arm (same judge, same code, **different run**) | prompts | **shift in mean A2** | per-prompt sd |
|---|---:|---:|---:|
| `oracle_k4` | 968 | **−0.116489** | 0.134355 |
| `greedy_k4_fit1` | 968 | **−0.098246** | 0.130060 |
| `indep_k4_fit1` | 968 | −0.034231 | 0.099651 |
| `topwvar_k4` | 968 | +0.023360 | 0.116709 |
| `topvar_k4` | 968 | +0.022443 | 0.112014 |

| | |
|---|---:|
| **worst run-to-run shift in the MEAN** | **0.116489** |
| R408's committed effect at 2B | **+0.009002** |
| **ratio** | **13×** |

## ⛔ §1 requires this and no round had done it

> *"NOISE FLOOR: measured, not assumed. **Replicates beat models.**"*

**The replicates were on disk the whole time.** `_08bR` — R for **re-run** — five pairs, same arm,
same judge, same code, both committed. **The campaign has computed MDEs from *within-run* standard
errors for hundreds of rounds and never measured the *between-run* floor.**

The git history is what surfaced it: the commit that added both 0.8B families is titled
*"five rounds change a CONCLUSION across hash seeds, so **a committed artifact in this repo is not a
function of its committed code**."* **A prior round had already said this. Nothing downstream acted on
it.**

## ⛔ My first comparison used the wrong units

R408's `+0.009002` is a **mean** over prompts; the `sd` column is a **per-prompt spread**. Setting them
side by side compares a mean to a dispersion. **The comparable quantity is the shift in the mean**, and
it is now the headline. *The sd is kept, because dropping a column after seeing it is how a table
becomes an argument.*

## ⚠ The cause is not separated, and that decides what this licenses

**A shift of 0.1 in an agreement metric is large for kernel non-determinism.** So either

- **the pipeline is wildly unstable**, or
- **two different configurations share a filename.**

**Both are disqualifying for treating these files as replicates**, and this round cannot tell them
apart — **so it claims the disjunction and not either branch.** *(It also explains R414's family
split: `topw_k4` differing across `sat08_*` and `*_08b` is the same phenomenon.)*

## ⚠ And no re-run pair exists at 2B

**The floor there is UNMEASURED.** So the correct statement is **not** *"R408's effect is inside the
noise"* — it is:

> **Every 2B number this session produced rests on an assumption of pipeline stability that has now
> failed at the only judge where it could be checked.**

## Controls

| | returned |
|---|---|
| **SELF (−)** | a file compared to **itself**: `max\|d\| = 0.0e+00` — `PASS`. Fails if the *loader* is noisy in a way that would fake a floor |
| **FIVE PAIRS** ⭐ | the floor is measured on **five independent arms**, so the floor measurement is itself replicated — one pair would be a single draw of a quantity about single draws |
| **SCORING** | `load_sat`/`yvec`/`cls` **imported** from the module every other round uses, so this is the floor of *the* pipeline, not of a re-implementation |
| **PROMPT MATCH** | 968 shared prompts on every pair, printed — a pair sharing few prompts would give a floor about coverage rather than noise |

## Register

| criterion | status |
|---|---|
| **the floor at 2B** | **UNMEASURED** — no committed re-run pair. A re-run needs the GPU |
| **the cause of the instability** | **NOT SEPARATED** — sampling, batching, kernel non-determinism, or a filename collision |
| **a second release** | **N/A** — one |

## The sentence I can no longer write

> *"the committed artifact is the arm's score"* — **at the only judge where two runs of the same arm
> both exist, they differ in the mean by 13× the effect this campaign has been chasing.**

Artifact: `results/r415_noise_floor.json`, source-stamped.
