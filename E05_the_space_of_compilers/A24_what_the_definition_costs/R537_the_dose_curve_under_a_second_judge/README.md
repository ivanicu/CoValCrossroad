# R537 · The weight-reading dose curve survives a second judge

**Decision this makes safe:** whether R533's dose-response is a fact about **selection** or about
the **2B judge**.

## ⭐ The naming that nearly stopped the round

Two conventions coexist and confusing them reads as "missing data":

| pattern | what it is |
|---|---|
| `sat_<arm>_08b.npz` | the **selection arms** rebuilt under 0.8B (`rebuild_selection_08b.sh`) |
| `sat08_full.npz` | the 0.8B **judging of the full rubric** — that script's own `--full-npz` input |

**`sat_full_08b.npz` does not exist and never did.** `sat08_full.npz` plays full's role under this
judge, and it is what makes the per-prompt random comparator constructible.

## Result — WORLD A

| k | 2B *(R533)* | **0.8B** | 95% CI (0.8B) | spread |
|---|---|---|---|---|
| 3 | +0.0724 | **+0.0521** | [+0.0374, +0.0559] | 0.0038 |
| 4 | +0.0705 | **+0.0519** | [+0.0435, +0.0604] | 0.0031 |
| 6 | +0.0644 | **+0.0443** | [+0.0387, +0.0524] | 0.0007 |
| 8 | +0.0585 | **+0.0410** | [+0.0339, +0.0468] | 0.0007 |
| **all** | +0.000000 | **+0.000000** | [0, 0] | 0.0000 |

**Positive at every k, monotone decay, exact zero at the endpoint — under both judges.** Magnitudes
attenuate consistently to ~0.70–0.74× under the weaker judge, which is what a weaker judge should do.

⭐⭐⭐ **Weight-reading's value is a fact about SELECTION, now replicated cross-model.** The
standard's `cross-model` criterion — which the register lists as needing another site — is met here
for the second time *(R536 was the first)*.

## Controls
- **Positive** — the 0.8B arms must **differ** from their 2B namesakes, else this is the same
  measurement twice: **4 of 4 differ.** PASS.
- **Negative, forced** — at k=all there is nothing to select, so the advantage must be **exactly 0**:
  **+0.000000.** PASS. ⛔ **A DERIVATION, labelled** — which is precisely what makes it a good
  endpoint: **a curve missing it would indict the construction.**
- **Noise floor** — 3 seeds per cell, spreads 0.0007–0.0038.

⚠ **Impossible here, and it is the one my last line named:** `sat_coval_core_08b` is absent, so
**the released core is the one admitted arm whose curve position cannot be replicated.** `full_08b`
is also absent — but `sat08_full` substitutes for it exactly, which is why the endpoint survived.
