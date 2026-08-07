# R521 · The declared literal's price: four label-readers at the top of the leaderboard

**Decision this makes safe:** whether ③'s hardcoded set may be carried forward, or must be replaced
by the derived gate before the population widens.

## ⛔ First — the announced next step was a check that cannot fail, and is demoted to a control

`f09c4bf` closed with *"the honest test is whether the derivation reproduces R294's admitted set
exactly over the original 41."* **R520's own output forces the answer**: `derived − declared` is 6
arms of which **0** carry a ③ verdict, and the positive control had already shown
`declared ⊆ derived`. So over the 41 the sets are **equal by construction**. It could not have come
out otherwise, and it is used below as a **positive control on the instrument** — which is what a
forced check is good for — not as a result.

## Result — WORLD B

**Arms whose ③ status differs between literal and gate, over all 56:**

| arm | A2 | vs ② bar (0.5504) |
|---|---|---|
| `oracle_k4_oracle_kA` | **0.6353** | ABOVE |
| `oracle_k4_oracle_kB` | **0.6353** | ABOVE |
| `greedy_k4_greedy_kA` | **0.6292** | ABOVE |
| `greedy_k4_greedy_kB` | **0.6292** | ABOVE |
| `indep_k4_indep_kA` | 0.6079 | ABOVE |
| `indep_k4_indep_kB` | 0.6079 | ABOVE |

**6 of 6 are admission candidates under the literal and excluded under the gate.** The current 9
②-passers span **0.5593–0.6283**, so **4 of the 6 outscore every one of them.**

⭐⭐⭐ **The price is not six marginal arms — it is the top of the leaderboard.**

## Controls
- **Positive** (forced, hence a control) — over R294's 41, literal and gate disagree on **0**. PASS.
- **Negative** — the **33** documented label-blind arms disagree on **0**. PASS.
- **Sham** — the *satisfaction* rule partition disagrees on **8**, the *label* partition on **6**.
  PASS: the price is specific to the label gate, not to any rule partition.
- **Noise floor** — the ② bar is a range [0.5386, 0.5504] across arms (R514); the **conservative
  top** is used, so every candidate is above it under every measured setting.

⚠ **Bound, stated: these are CANDIDACIES, not verdicts.** 15 of the 56 carry no ② interval verdict
on disk. Turning candidacy into verdict needs the blind-pool contrast recomputed on them — a
scoring run, named in the register and not marked planned.

## What it means for the formulation

Three times now the same shape: **the highest scorers are the label-readers.** R519 found ③ removes
the top 4 of 9 admitted arms. Here the 6 the literal misses would be the top 4 of the extended set.

⭐⭐⭐ **③ does its work at the top of the distribution — which is exactly where a benchmark's
headline comes from. Without it, the leaderboard ranks how much each arm read the answer.**
