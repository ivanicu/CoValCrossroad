#!/usr/bin/env python3
"""R493 — R492 priced a GPU run. What does the quantisation route actually require?

⚠ ACTION CLASS: CLOSURE. It prices a capability the register names; it tests nothing about the
definition.

WHY. R492 established the 7B judge OOMs in bf16 and that quantising it confounds size, family and
precision. It closed by proposing to also judge the 2B at int8 — *"a fifth of the 7B's cost"*. That
prices GPU time, which is the only resource the round happened to meter.

ESTIMAND  the full precondition set for int8 judging on this site, as a list of things that must be
    true, each checked against the machine rather than recalled.

IDENTIFICATION  direct import probes and version reads. Nothing estimated.

SCOPE  population: this `.venv` and this GPU at HEAD · instrument: `importlib.util.find_spec`,
    `torch.cuda.get_device_capability`.

WORLDS
    A  A FLAG        a quantisation path is installed -> R492's pricing stands.
    B  AN INSTALL    absent, but routine -> add a line item.
    C  AN ENVIRONMENT CHANGE  absent, and installing it touches the shared harness that every
       committed number depends on -> the cost is risk, not hours.

KILL  C if no quantisation path is present AND the venv is shared by the committed harness.

CONTROLS
    POSITIVE  the probe must FIND libraries that ARE installed (`accelerate`, `torch`,
              `transformers`) — a probe that reports everything absent is measuring nothing.
    NEGATIVE  a package that certainly is not here must report ABSENT.

ARTIFACT  results/r493_quantisation_preconditions.json
"""
import importlib.util as iu, json, pathlib, sys
import torch, transformers
OUT = pathlib.Path(__file__).parent/"results"
QUANT = ["bitsandbytes", "optimum", "auto_gptq", "awq"]
KNOWN_PRESENT = ["accelerate", "torch", "transformers"]
probe = lambda m: iu.find_spec(m) is not None

q = {m: probe(m) for m in QUANT}
pos = {m: probe(m) for m in KNOWN_PRESENT}
neg = probe("a_package_that_does_not_exist_xyz")
cap = torch.cuda.get_device_capability(0) if torch.cuda.is_available() else None
print(f"  POSITIVE  known-present libraries found: {pos}   {'PASS' if all(pos.values()) else '⛔'}")
print(f"  NEGATIVE  a nonexistent package reports absent: {not neg}")
print(f"\n  quantisation paths: {q}")
print(f"  torch {torch.__version__}   transformers {transformers.__version__}   CUDA cap {cap}")

# does the committed harness share this venv? the judge imports from it, so yes by construction.
shared = (pathlib.Path("covalx/judge.py").exists()
          and pathlib.Path("corebench/judge_core.py").exists())
none_present = not any(q.values())
world = ("C (AN ENVIRONMENT CHANGE)" if none_present and shared
         else "B (AN INSTALL)" if none_present else "A (A FLAG)")
print(f"\n  the committed harness imports from this venv: {shared}")
print(f"\n  VERDICT MEASURED\n  world: {world}")
print(f"\n  WHAT IT WOULD REQUIRE, in order:")
for i, step in enumerate([
    "install a COMPILED CUDA package (bitsandbytes) against capability "
    f"{cap} with torch {torch.__version__}",
    "into the SHARED .venv that covalx/judge.py and every committed sat_*.npz's harness use",
    "add a quantisation knob to covalx.judge.Judge (it takes dtype= only)",
    "re-judge the 2B quantised, or the comparison confounds size, family AND precision"], 1):
    print(f"    {i}. {step}")
OUT.mkdir(parents=True, exist_ok=True)
json.dump({"quant_paths": q, "known_present": pos, "negative_probe_absent": not neg,
           "torch": torch.__version__, "transformers": transformers.__version__,
           "cuda_capability": list(cap) if cap else None, "harness_shares_venv": bool(shared),
           "world": world}, open(OUT/"r493_quantisation_preconditions.json", "w"), indent=2)
sys.exit(0 if all(pos.values()) and not neg else 2)
