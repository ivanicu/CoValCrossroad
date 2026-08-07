# R533 · Weight-reading is worth +0.0726 at k=4 and exactly 0 at k=all — it is the operation, not the core

**Decision this makes safe:** whether R532's +0.0748 describes `coval_core` or describes the
operation ③-any forbids.

## ⛔ First — my closing line miscounted again

`51e63b8` said *"`topw_k4` is **the** other admitted arm that also reads weights."* **There are
four** — `topw_k3`, `k4`, `k6`, `k8`. **Which improved the experiment**: four k values turn a single
check into a **dose-response**, and `full` supplies a forced endpoint.

## Result — WORLD A

| arm | k | advantage | spread |
|---|---|---|---|
| `coval_core` | 4 | **+0.0726** | 0.0031 |
| `topw_k3` | 3 | +0.0724 | 0.0057 |
| `topw_k4` | 4 | +0.0705 | 0.0015 |
| `topw_k6` | 6 | +0.0644 | 0.0007 |
| `topw_k8` | 8 | +0.0585 | 0.0020 |
| **`full`** | **15** | **+0.000000** | 0.0000 |

**Monotone decay, +0.0726 → 0.0000.** The smallest `topw` is **0.81×** `coval_core`, against a
pre-registered kill at 0.50×.

⭐⭐⭐ **`coval_core` (+0.0726) is indistinguishable from `topw_k4` (+0.0705) — the released core's
advantage IS generic top-weight selection.** The +0.0748 is a property of the **operation**.

## Controls
- **Positive** — `coval_core` must reproduce R532's +0.0748 within its seed spread: **+0.0726.**
  PASS, so this round sits on R532's scale.
- **Negative, and it is the sharp one** — `full` selects **every** criterion, so there is nothing to
  select and weight-reading can be worth nothing: **+0.000000, exactly.** PASS.
  ⛔ **That zero is a DERIVATION, not a measurement** — at k=all both arms take the same items, so
  the contrast is forced. **That is precisely why it makes a good endpoint: a curve that failed to
  hit it would indict the whole construction.** It hits it to six decimals.
- **Noise floor** — 3 seeds per cell, spreads 0.0007–0.0057.

## What it means

**③-any forbids an operation whose value is a curve, not a point: +0.0726 at k=4, decaying to 0 by
k=15.** The fewer items you keep, the more selecting them by weight is worth — which is the
mechanism stated as a gradient rather than asserted.

⚠ **What this does NOT show:** that the weights are *good* weights. It measures the value of reading
them, not whether the annotators were right — that needs an external standard, **register row 6**.
