# R534 · ③'s input taxonomy has three classes; R529 named two

**Decision this makes safe:** whether the ③ fork was measured on the right partition.

## The source disagrees with R529

R529 used `WEIGHT_RULES = (topw_k, topabs_k, topvar_k, topwvar_k)`. `select_core.py` says:

| rule | selection expression | reads |
|---|---|---|
| `topw_k` | `sorted(ok, key=lambda i: -w[i])` | **annotator weights** |
| `topabs_k` | `sorted(ok, key=lambda i: -abs(w[i]))` | **annotator weights** |
| `topvar_k` | `var([ssat[pid][(i,x)] for x in L])` | ⭐ **judged satisfaction** |
| `topwvar_k` | `-(abs(w[i]) * var[i])` | **both** |
| `oracle/indep/greedy` | open `comparisons.jsonl` | **human rankings** |

And the code's own comment on `topvar_k`: *"Non-leaky: the spread is a property of the **responses**,
never of the human target."*

⭐⭐⭐ **So an arm can read the responses' judged satisfaction while reading no human input at all
— a class ③-any's phrase ("no annotator signal for that prompt") does not cover, because a judge is
not an annotator.**

## Result — WORLD A

| class | n | arms |
|---|---|---|
| rank | 4 | `oracle_k4`, `oracle_k4_fit1`, `greedy_k4_fit1`, `indep_k4_fit1` |
| weight | 10 | `coval_core`, `topw_k*`, `topabs_k4` |
| **sat** | **1** | **`topvar_k4`** |
| weight+sat | 1 | `topwvar_k4` |
| neither | 25 | `gen`, `generic`, `full`, `random_k*`, shams |

| reading | extension of ② ∧ ③ | R529 reported |
|---|---|---|
| ③-rank | **5** | 5 |
| ③-any | **0** | 0 |
| **③-judge** *(new)* | **0** | — |

**Both extensions unchanged.** R529's conclusion survives; **only its taxonomy was wrong — a latent
defect that would mislabel a future arm.** On this population ③-any and ③-judge coincide, because no
②-passer is in the `sat` class; **a future satisfaction-reading arm that cleared ② would separate
them.**

## Controls
- **Source read** — all **4** selection expressions confirmed verbatim from `select_core.py`.
- **Positive** — the ③-rank extension must equal R294's own `admitted` restricted to ②-passers:
  identical. **PASS**, so this partition is the code's.
- **Negative** — the three classes must be non-empty on real arms: **3/3. PASS.**
- ⚠ **The premise check exited 2 on the first run**, because the quoted comment spans three comment
  lines and flattening whitespace left a `#` mid-sentence. **Second premise check this session to
  catch source wrapping. The fix was to normalise the markup, never to loosen the quote.**

**Impossible here:** whether reading the *judge* should disqualify a core. Same decision about
purpose as ③-rank vs ③-any — **register row 7, now with a third option on it.**
