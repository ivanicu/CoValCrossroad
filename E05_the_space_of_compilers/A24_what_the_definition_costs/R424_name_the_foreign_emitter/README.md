# R424 · both `_08b` families are foreign to the default judge. Which table DID emit them?

**The decision this round makes safe:** what instrument the 74 committed `_08b` artifacts belong to,
and therefore what 30 rounds citing them are entitled to say.

**Answer: none on disk.** `W-NOT-ON-DISK`.

## The anchors are the instrument, not decoration

| anchor | rate |
|---|---|
| default table contains `topw_k4` — **known** default-emitted | **`1.0000`** (15,440 of 15,440) |
| default table contains `oracle_k4_08b` — the **floor** | **`0.0380`** (587 of 15,448) |

**Both are required.** The positive alone would pass a table so dense it contains anything; the
negative alone would pass a table that contains nothing. ⚠ And every count carries its denominator —
R423 printed `29,742 uncontained` with none, and that is not a rate.

## Every committed table, tested

| table | `topw_k4` | `_08b` | `_08bR` |
|---|---|---|---|
| `corebench/results/sat_full.npz` | `1.0000` | `0.0380` | `0.0375` |
| `E01/…/R04_rebuild_satisfaction/results/a04_full.npz` | `1.0000` | `0.0380` | `0.0375` |
| `_archive/work/a04_full.npz` | `1.0000` | `0.0380` | `0.0375` |
| `E04/…/R164_instrument/results/sat_full_phi.npz` | `0.0056` | `0.0049` | `0.0039` |
| `E04/…/R164_instrument/results/sat_full_qwen3b.npz` | `0.0000` | `0.0000` | `0.0000` |

**5 admitted · 49 rejected** on the key-set precondition — a candidate enters only if its `meta` key
set *equals* `sat_full.npz`'s, because otherwise `core_full.json` does not map its indices and the
join would compare unrelated cells: **R422's failure, one level up.** Rejections are printed, never
silently dropped.

## ⭐ What the two measurements jointly force

`select_core.py` makes **zero judge calls** — criteria come from the rule run on `--select-npz`,
values are looked up from `--full-npz`. So:

| file | measured | forced configuration |
|---|---|---|
| `_08b` | criteria **identical** to a default-npz run (R421, sha256) **+** values ~96 % foreign (here) | `--select-npz <default> --full-npz <foreign>` — the tool's own *"freeze the selection to re-score a fixed criterion set"* |
| `_08bR` | criteria **91–99.6 %** different (R416) **+** the *same* foreign values (R423) | the rule **re-run** under the foreign judge |

**`R` is `rebuilt`, not `wrong`. Neither file is an anomaly** — they are the two arms of exactly the
experiment `--select-npz`'s help text describes. R415's "instability", R421's "outlier" and my own
closing sentence were all the same error wearing three costumes: **a configuration difference read as
a defect.**

## ⛔ The scope this forces, and it is worse than it sounds

**74 `_08b` artifacts · 30 rounds cite them.** Their emitting table is not committed anywhere in this
repo, so those arms are **instrument-UNKNOWN — not instrument-0.8B.** The suffix is a *filename*.
Naming the **table** would have been the claim; naming the **model** never was, and no table matched.

## Impossible here, named

- **an emitter never committed** — reported as `W-NOT-ON-DISK`, never approximated by the closest file.
- **which model produced a named table** — a filename is a name, not evidence about weights.
- **which selection input differed** — unchanged; the artifacts record no configuration, which is
  exactly the gap `judge_core.py`'s provenance field closes going forward and cannot close backwards.
- **cross-release** — one release.

Findings, with their scope, live in the top-level README. This file states the design.
