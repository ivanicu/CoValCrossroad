# R519 · Only ③ narrows what ② admits — the definition is a pair

**Decision this makes safe:** how many clauses the definition of "core" actually has, measured on
one population with one instrument.

**Estimand:** for each clause X, the number of ②-passing arms X drops — the only quantity in which
a clause adds to the definition. **Population:** the 41 arms carrying ①②③ verdicts (R294) joined
to ④ scores (R436). **Instrument:** interval verdicts. **Baseline:** the set ② admits.
**Regime:** home judge J, 968 prompts.

## Result — WORLD B

| clause | drops of the **9 passers** | drops of the **32 rejects** | reading |
|---|---|---|---|
| **①** | **0** | **24** | **nested inside ②** — discriminates, but only among arms ② already removed |
| **③** | **4** | **0** | ⭐ **orthogonal to ②** — cuts exactly where ② does not |
| **④** | **0** | **0** | discriminates **nothing** at home |

**The four arms ③ drops, and why:**

| arm | provenance |
|---|---|
| `oracle_k4` | uses THIS prompt's labels (all annotators) |
| `oracle_k4_fit1` | uses THIS prompt's labels (parity 1) |
| `greedy_k4_fit1` | uses THIS prompt's labels (parity 1) |
| `indep_k4_fit1` | uses THIS prompt's labels (parity 1) |

**Surviving all four clauses:** `coval_core`, `topw_k3`, `topw_k4`, `topw_k6`, `topw_k8` —
**identical to the census's own admitted set**, so ①∧④ contribute nothing to it.

## Controls
- **Negative** — ② against its own admitted set drops **0**. PASS; the join is not malformed.
- **Positive** — some clause must drop a ②-passer, else every zero is silence: **③ drops 4.** PASS,
  so ①'s and ④'s zeros are measurements.
- **Sham** — each clause applied to the arms ② *rejects*. This is the column that explains the
  mechanism: ① drops 24 there and ④ drops 0, while ③ drops none. **①'s discrimination is real but
  redundant; ④'s is absent; ③'s is orthogonal.**
- **Noise floor** — R518 measured every ②-passer at **4.90×–8.65× MDE** above ④'s bar, so ④'s zero
  is resolved rather than under-powered.

## ⭐⭐⭐ The definition

> A **core** for a conversation is a set of criteria that **② scores better than the best
> generalising prompt-blind criterion set**, and **③ was not built by reading that conversation's
> human labels**.

**Two clauses, orthogonal, both doing measured work.** ① and ④ are decoration — true of cores, but
excluding nothing ② has not already excluded.

⚠ **And the tension the campaign has been circling, now measured rather than asserted: the only
clause doing independent work is ③, which is checkable from the PRODUCER and never from the
product.** The four arms it removes are the *highest scorers* — they win by reading the answer.

**Impossible here:** the second release, where ② admits 0 of 7 so no clause can be compared against
it. Unchanged from R517/R518.
