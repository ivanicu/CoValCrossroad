# R536 · Weights beat spread under a second judge — a register "impossible" that was on disk

**Decision this makes safe:** whether R535's refutation of the release's own selection rationale is
a fact about **selection** or about the **2B judge**.

## ⛔ First — the sixth false wall

`db32023` closed saying a second judge is *"an install rather than a GPU run"* (register row 2).
**`rebuild_selection_08b.sh` had already re-run every selection arm under the 0.8B judge — 32 `_08b`
artifacts on disk.** This is a reanalysis. **Sixth wall of this shape.**

## Which arms, from the source rather than by convenience

`frozen (_08b)` = selection fixed at 2B, **scored** at 0.8B. `rerun (_08bR)` = the **rule** re-run
under 0.8B. `select_core.py` says the satisfaction-blind rules' *"specifications coincide for them
exactly"* — **which is why no `topw_k4_08bR` exists.** So `topw_k4_08b` **is** the 0.8B-judge topw
arm, and `topvar_k4_08bR` is the 0.8B-judge topvar arm.

## Result — WORLD A

| judge | n | topw | topvar | diff | 95% CI |
|---|---|---|---|---|---|
| **2B** (home) | 968 | 0.5642 | 0.4863 | **+0.0779** | [+0.0679, +0.0879] |
| **0.8B** (second) | 968 | 0.4646 | 0.4009 | **+0.0636** | [+0.0551, +0.0720] |

⭐⭐⭐ **Weights beat spread under both judges, both CIs excluding zero.** So **R535's refutation of
`select_core.py`'s own "the direct fix" rationale is a fact about SELECTION, not about the 2B
model** — and the standard's `cross-model` criterion, which the register lists as needing another
site, is **met here**.

## Controls
- **Source read** — the satisfaction-blind claim confirmed, **and** the absence of `topw_k4_08bR`
  confirms it operationally: the file the source implies should not exist, does not.
- **Positive** — `topw_k4_08b` must **differ** from `topw_k4`, else the `_08b` family is a
  mislabelled copy: **True.**
- **Negative** — `topvar_k4_08b` (frozen) must differ from `_08bR` (rerun), else the 0.8B-judge
  topvar arm is not a distinct object: **True.**

⚠ **Correction to my own caveat:** I wrote that the two judges use *different* populations. **Both
resolve to n = 968.** The size comparison is therefore better founded than I claimed — **an
over-cautious scope statement is still a wrong one.**

⭐ **Sanity that passed implicitly:** the weaker judge scores both arms lower (0.4646/0.4009 vs
0.5642/0.4863), which is what a weaker judge should do.

**Impossible here:** a third judge, and `coval_core` under 0.8B — `sat_coval_core_08b` is absent.
