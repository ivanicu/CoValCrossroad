# R492 · The cross-architecture judge is present, and does not run in bf16 on this card

⚠ **Action class: CLOSURE on a capability question.** It tests the site, not the definition.

**The decision this made safe.** R491 established the 7B is **present**. This establishes it does not
**run** — and, more usefully, that the fix is a **confound rather than a configuration**.

## Measured, not predicted

| | |
|---|---|
| model loaded (POSITIVE control) | **15,744 MiB of 16,303** → **559 MiB** headroom |
| batch 16 (pueue 653) | **OOM at 52 MiB**, in `RMSNorm` |
| batch 2 (pueue 654) | **OOM at 16 MiB**, in the MLP `down_proj` |
| DOSE | the deficit **tracks batch** (52 → 16 MiB), so batch is the right axis — and batch 2 is near its floor |
| g=0 | the 2B judge runs in bf16 on this card, per every committed `sat_*.npz` — so this is about **this model**, not the harness |

**World C: PRECISION-BOUND.** Two batches 8× apart both fail. **bf16 is out on a 16 GB card.**

⭐ **The previous round asserted the opposite from arithmetic:** *"7B × 2 bytes ≈ 14 GB and fits,
tightly."* The arithmetic was right and the conclusion was wrong. **A fit computed from parameter
count is not a fit — the allocator decides, and it decided at 52 MiB, then at 16.**

## Why quantisation is not just the next step

| precision | weights | free on a 15.9 GiB card |
|---|---|---|
| bf16 | 15.2 GB | **0.7 GB** |
| int8 | 7.6 GB | 8.3 GB |
| int4 | 3.8 GB | 12.1 GB |

⛔ **`Judge.__init__` takes `dtype=torch.bfloat16` and has no quantisation knob.** Adding one makes
the 7B a **different instrument** from the bf16 2B and 0.8B judges that every committed number uses.
**An attainment gap would then confound SIZE, FAMILY and PRECISION at once** — and removing that
confound means re-judging 2B quantised as well, which changes the committed baseline.

**This is what the pilot bought that no arithmetic would have:** I would have written *"quantise it"*
without noticing that quantising creates a three-axis comparison against a two-axis question.

## Cost

Two bounded pilots, `--limit 12` (524 judge calls), on free local hardware via pueue. **Both failed in
seconds** — which is the entire argument for bounding a feasibility probe.

⚠ `--limit` slices `pids[:N]`, a **prefix**: a stratum, not a sample. Fine for feasibility, **not**
for any attainment estimate.

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R492_the_cross_architecture_judge_needs_quantisation/run.py
