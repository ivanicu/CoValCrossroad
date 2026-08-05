#!/usr/bin/env python3
"""R554 · Does the new --model flag have anything STRONGER to point at?

ESTIMAND  the number of local checkpoints that are (a) complete, (b) larger than the incumbent
          generator, and (c) loadable in bf16 within this box's 16 GB VRAM.
IDENT     (a) and (b) fully identified from the store. (c) is PARTIALLY identified -- a bf16
          footprint is arithmetic, but whether it loads also depends on live VRAM, so (c) is
          reported as a BOUND, not a verdict.
SCOPE     population = the local model store · instrument = file sizes + shard manifests ·
          baseline = the incumbent Qwen3.5-2B-Base · regime = bf16, 16 GB RTX 5080.
WORLDS    A the flag unlocks a real choice -- >=1 complete, larger, loadable checkpoint exists,
            and rows 3+4 are genuinely compute-bound as the register now says.
          B every stronger checkpoint is incomplete or too large in bf16, so rows 3+4 are
            NESTED INSIDE row 2's blocker and the register's independence is wrong.
KILL      pre-registered: if 0 checkpoints are complete AND larger AND fit, WORLD B and the
          register must nest 3+4 under row 2.
POS CTRL  the incumbent must be found and read as COMPLETE. If the scanner cannot see the model
          that demonstrably works, a zero elsewhere is silence.
NEG CTRL  an invented model directory must be found by neither.
ARTIFACT  results/checkpoints.json
"""
import json, pathlib, re, sys

# ⛔ THE FIRST VERSION SCANNED ONE STORE and its positive control PASSED, because the incumbent
# lives there. It found 0 stronger checkpoints and would have concluded WORLD B from a blind
# instrument -- Qwen2.5-7B-Instruct and Qwen3.5-9B both exist on this box, in sibling projects
# and the HF caches. Instrument unit was "top-level dirs of ONE store"; the claim's unit is
# "checkpoints --model can point at". Not equal. §4's row, exactly.
STORES = [pathlib.Path(x) for x in [
    "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly",
    "/home/ivan/research.alignment.emergent-misalignment.persona-forensics.build.lg.private.editable/models",
    "/mnt/e/cache/huggingface/hub", "/home/ivan/.cache/huggingface/hub",
]]
STORE = STORES[0]
VRAM_GB, INCUMBENT = 16.0, "Qwen3.5-2B-Base"

def scan(d):
    if not d.is_dir(): return None
    # ⚠ HF cache snapshots are SYMLINKS into blobs/. A pruned blob leaves a dangling link, so
    # "the directory exists" is not "the weights exist" -- resolve and require the target.
    sh = sorted(f for f in d.glob("*.safetensors") if f.exists())
    dangling = len([f for f in d.glob("*.safetensors") if not f.exists()])
    idx = d / "model.safetensors.index.json"
    total = sum(f.stat().st_size for f in sh) / 1e9
    expected = None
    if idx.exists():
        try:
            m = json.loads(idx.read_text()).get("weight_map", {})
            expected = len(set(m.values()))
        except Exception: expected = None
    complete = (expected is None and len(sh) > 0) or (expected is not None and len(sh) == expected)
    complete = complete and dangling == 0
    return {"name": d.name, "shards": len(sh), "expected": expected, "dangling": dangling,
            "gb_on_disk": round(total, 2), "complete": bool(complete)}

# population = every directory holding >=1 .safetensors, at any depth, across ALL stores
cands = sorted({f.parent for st in STORES if st.is_dir()
                for f in st.rglob("*.safetensors")}, key=str)
if not cands:
    print("  model store unreadable -> UNRUNNABLE"); sys.exit(2)

info = {}
for p in cands:
    d = scan(p)
    if d:
        # de-dup by name, keeping the largest copy -- the same model appears in several stores
        # ⛔ FIRST VERSION KEYED ON p.name, which for an HF cache is the SNAPSHOT HASH --
        # so every result was named `851bf6e8...` and could not be identified. A finding named
        # by a hash is not a finding. Walk up to the `models--org--name` component.
        key = p.name
        for anc in p.parents:
            if anc.name.startswith("models--"):
                key = anc.name.replace("models--", "").replace("--", "/"); break
        d["name"], d["path"] = key, str(p)
        if key not in info or d["gb_on_disk"] > info[key]["gb_on_disk"]:
            info[key] = d
inc = info.get(INCUMBENT)
print(f"  POSITIVE CONTROL  the incumbent {INCUMBENT} is found and COMPLETE: "
      f"{bool(inc and inc['complete'])} -> {'PASS' if inc and inc['complete'] else 'FAIL'}")
fake = scan(STORES[0] / "Not-A-Real-Model-9Z")
print(f"  NEGATIVE CONTROL  an invented model dir reads as absent: {fake is None} -> "
      f"{'PASS' if fake is None else 'FAIL'}")
if not (inc and inc["complete"]) or fake is not None:
    sys.exit(2)

inc_gb = inc["gb_on_disk"]
print(f"\n  incumbent generator: {INCUMBENT}  {inc_gb} GB on disk\n")
print(f"  {'checkpoint':<34} {'shards':>7} {'GB':>7}  complete  larger  fits bf16")
rows = []
for n, d in sorted(info.items(), key=lambda kv: -(kv[1]["gb_on_disk"] if kv[1] else 0)):
    if not d or d["shards"] == 0: continue
    larger = d["gb_on_disk"] > inc_gb
    # bf16 weights ~= on-disk size for a bf16 checkpoint; require headroom for activations.
    fits = d["gb_on_disk"] < VRAM_GB * 0.85
    rows.append({**d, "larger": larger, "fits_bf16_bound": fits})
    print(f"  {n[:34]:<34} {d['shards']:>7} {d['gb_on_disk']:>7.2f}  "
          f"{str(d['complete']):>8}  {str(larger):>6}  {str(fits):>9}")

usable = [r for r in rows if r["complete"] and r["larger"] and r["fits_bf16_bound"]]
print(f"\n  complete AND larger AND fitting in bf16: {len(usable)}")
for u in usable: print(f"    -> {u['name']}")
world = "A" if usable else "B"
print(f"\n  WORLD {world} -- " + (
    "the flag unlocks a real choice; rows 3+4 are independently compute-bound."
    if world == "A" else
    "every stronger checkpoint is incomplete or too large -- rows 3+4 are NESTED INSIDE row 2."))
(pathlib.Path(__file__).parent / "results" / "checkpoints.json").write_text(json.dumps(
    {"world": world, "incumbent": INCUMBENT, "incumbent_gb": inc_gb, "vram_gb": VRAM_GB,
     "n_usable": len(usable), "usable": [u["name"] for u in usable], "all": rows,
     "identification_note": "fits_bf16_bound is a BOUND from on-disk size, not a load test"},
    indent=2))
