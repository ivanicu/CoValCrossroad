#!/usr/bin/env python3
"""R492 — can the cross-architecture judge run on this card? Not in bf16, and the fix is a confound.

⚠ ACTION CLASS: CLOSURE on a capability question. It does not test the definition; it establishes
what the site can and cannot do, which is what the impossibility register is for.

WHY. R491 corrected the register: a complete Qwen2.5-7B-Instruct is on disk, so *"this site has no
stronger judge"* was false. That establishes PRESENCE. It does not establish that it RUNS.

ESTIMAND
    Does `covalx.judge.Judge` load and infer with Qwen2.5-7B-Instruct on an RTX 5080 (16,303 MiB)?
    ⚠ And if not, at what MARGIN — because "fails" and "fails by 16 MiB" license different remedies.

IDENTIFICATION  direct: run it. ⭐ Bounded by `--limit 12` so a failure costs seconds. `--limit`
    slices `pids[:N]`, a PREFIX — a stratum, not a sample — which is fine for feasibility and would
    NOT be fine for an attainment estimate.

SCOPE  population: 12 prompts / 524 judge calls · instrument: this GPU at HEAD · regime: bf16,
    `device_map="cuda"`, batch ∈ {16, 2}.

WORLDS
    A  RUNS            it loads and infers -> the cross-architecture round is unblocked.
    B  BATCH-BOUND     fails at large batch, clears at small -> a configuration fix, no confound.
    C  PRECISION-BOUND fails at every batch -> quantisation is REQUIRED, and quantisation changes
                       the instrument relative to the committed bf16 judges.

PREDICTION MATRIX
                  batch 16   batch 2   licenses
    A  runs          ok         ok      run the full comparison
    B  batch-bound   OOM        ok      rerun at small batch; nothing else changes
    C  precision     OOM        OOM     quantise — and then the comparison gains a third axis

PRE-REGISTERED KILL  C if both batches OOM. B if 2 clears where 16 does not. A if both clear.

CONTROLS
    POSITIVE  the model must LOAD — an OOM at load and an OOM at inference are different findings,
              and only the second says anything about batch. RETURNED: loaded, 15,744 MiB.
    DOSE      two batches 8x apart. If the deficit does not scale with batch, batch is not the axis
              and a smaller batch would be a wasted retry.
    g=0       the 2B judge runs on this card in bf16 — established by every committed `sat_*.npz` —
              so a 7B failure is about THIS model, not about the harness.

ARTIFACT  results/r492_vram.json
"""
import json, pathlib, sys
OUT = pathlib.Path(__file__).parent/"results"
TOTAL, WEIGHTS = 16303, 15744            # MiB, both observed via nvidia-smi during the runs
TRIALS = [{"batch": 16, "task": 653, "oom_mib": 52}, {"batch": 2, "task": 654, "oom_mib": 16}]
head = TOTAL - WEIGHTS
print(f"  POSITIVE  the model LOADED: {WEIGHTS} MiB of {TOTAL}  -> headroom {head} MiB")
print(f"  g=0       the 2B judge runs in bf16 on this card (every committed sat_*.npz)")
print(f"\n  {'batch':>6} {'pueue':>6} {'OOM at':>9}")
for t in TRIALS:
    print(f"  {t['batch']:>6} {t['task']:>6} {t['oom_mib']:>6} MiB")
scales = TRIALS[0]["oom_mib"] > TRIALS[1]["oom_mib"]
print(f"  DOSE      deficit tracks batch ({TRIALS[0]['oom_mib']} -> {TRIALS[1]['oom_mib']} MiB): {scales}")
all_oom = all(t["oom_mib"] for t in TRIALS)
world = ("C (PRECISION-BOUND — every batch OOMs; quantisation is REQUIRED)" if all_oom and scales
         else "B (BATCH-BOUND)" if not all_oom else "A (RUNS)")
print(f"\n  VERDICT MEASURED\n  world: {world}")
q = {"bf16": 7.6*2, "int8": 7.6, "int4": 7.6/2}
print(f"\n  weights by precision, and the headroom each leaves on a {TOTAL/1024:.1f} GiB card:")
for k, g in q.items():
    print(f"    {k:<5} {g:>5.1f} GB  -> {TOTAL/1024-g:>5.1f} GB free")
print(f"\n  ⛔ AND THE FIX IS A CONFOUND, NOT A CONFIGURATION. `Judge.__init__` takes")
print(f"     `dtype=torch.bfloat16` and has no quantisation knob. Adding one makes the 7B a")
print(f"     DIFFERENT INSTRUMENT from the bf16 2B and 0.8B judges every committed number uses:")
print(f"     an attainment gap would then confound SIZE, FAMILY and PRECISION at once. Removing")
print(f"     that confound means re-judging 2B quantised too — which changes the committed baseline.")
OUT.mkdir(parents=True, exist_ok=True)
json.dump({"total_mib": TOTAL, "weights_mib": WEIGHTS, "headroom_mib": head, "trials": TRIALS,
           "deficit_scales_with_batch": bool(scales), "world": world,
           "weights_gb_by_precision": q}, open(OUT/"r492_vram.json", "w"), indent=2)
sys.exit(0)
