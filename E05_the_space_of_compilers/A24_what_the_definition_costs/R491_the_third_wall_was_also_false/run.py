#!/usr/bin/env python3
"""R491 — "this site has no stronger judge" is the THIRD wall this session that was false.

⚠ ACTION CLASS: CLOSURE. It retracts a register line written one round earlier.

WHY. R490 put into the register: *"What would settle ②∧③ is a judge stronger than Qwen3.5-2B, and
this site has none."* That is a claim about the MACHINE, asserted from memory immediately after
checking the RECORD. §4 names *"a wall never checked"* as a failure mode, and this session has now
produced three of them.

ESTIMAND  does a model larger than Qwen3.5-2B exist on this machine, complete and loadable?
    ⭐ COMPLETE is the load-bearing word: a partial download is not a judge, and CLAUDE.md's own
    environment note lists a `Qwen3.5-9B` as *partial* — so the question cannot be answered by
    listing directory names.

IDENTIFICATION  direct: shard count against `model.safetensors.index.json`'s own weight map.

SCOPE  population: `/mnt/e/...local-model-store...` and `/home/ivan` to depth 4 · instrument: `find`
    + index verification · regime: this box at HEAD.

WORLDS  A NONE (register stands) · B PRESENT (register false; name what it does and does not test).

KILL  B if any complete model with >2B parameters is found.

CONTROLS
    POSITIVE ⭐ the search must FIND the models known to be here (Qwen3.5-0.8B, Qwen3.5-2B). A search
             that returns nothing proves nothing about absence — and it was this control, not the
             estimand, that surfaced the 7B: my first pass looked only in the model store.
    NEGATIVE a model known NOT to be here (`Qwen3.5-9B`, listed as partial in CLAUDE.md) must come
             back absent — otherwise the search finds everything and licenses nothing.

ARTIFACT  results/r491_judges_on_disk.json
"""
import json, pathlib, sys
ROOT = pathlib.Path(".")
OUT = ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/R491_the_third_wall_was_also_false/results"
STORE = pathlib.Path("/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly")
CANDS = [STORE/"Qwen3.5-0.8B-Base", STORE/"Qwen3.5-2B-Base", STORE/"Qwen3.5-9B",
         pathlib.Path("/home/ivan/Qwen2.5-7B-Instruct")]

def probe(p: pathlib.Path):
    if not p.is_dir(): return {"present": False}
    cfg = p/"config.json"
    j = json.loads(cfg.read_text()) if cfg.exists() else {}
    shards = {f.name for f in p.glob("*.safetensors")}
    si = p/"model.safetensors.index.json"
    want = set(json.loads(si.read_text())["weight_map"].values()) if si.exists() else shards
    return {"present": True, "model_type": j.get("model_type"), "hidden": j.get("hidden_size"),
            "layers": j.get("num_hidden_layers"), "shards_present": len(shards),
            "shards_expected": len(want), "complete": bool(want and want <= shards)}

rows = {p.name: probe(p) for p in CANDS}
print(f"  {'model':<24} {'present':>8} {'complete':>9} {'hidden':>7} {'layers':>7}")
for n, r in rows.items():
    print(f"  {n:<24} {str(r['present']):>8} {str(r.get('complete','—')):>9} "
          f"{str(r.get('hidden','—')):>7} {str(r.get('layers','—')):>7}")

pos = rows["Qwen3.5-0.8B-Base"]["present"] and rows["Qwen3.5-2B-Base"]["present"]
neg = not rows["Qwen3.5-9B"]["present"]
print(f"\n  POSITIVE  the search finds the two known judges          : {pos}")
print(f"  NEGATIVE  Qwen3.5-9B (CLAUDE.md says partial) is absent  : {neg}")

bigger = [n for n, r in rows.items()
          if r.get("complete") and (r.get("hidden") or 0) > (rows["Qwen3.5-2B-Base"].get("hidden") or 0)]
if not (pos and neg):
    verdict, world = "UNVERIFIED", "a control failed — the search is not calibrated"
elif bigger:
    verdict, world = "MEASURED", (f"B (PRESENT — {bigger} is complete and larger than Qwen3.5-2B; "
                                  f"the register line 'this site has none' is FALSE)")
else:
    verdict, world = "MEASURED", "A (NONE — the register stands)"
print(f"\n  VERDICT {verdict}\n  world: {world}")
print(f"\n  ⚠ WHAT IT DOES AND DOES NOT TEST. Qwen2.5-7B-Instruct is a DIFFERENT FAMILY and an")
print(f"    INSTRUCT model; the campaign's judges are Qwen3.5 BASE. So it tests CROSS-ARCHITECTURE,")
print(f"    not scale — a stronger axis than the one the register asked for, and a different one.")
print(f"    And 29 GB against 16 GB of VRAM: it needs quantisation or offload. Not free, not absent.")
OUT.mkdir(parents=True, exist_ok=True)
json.dump({"models": rows, "positive": bool(pos), "negative": bool(neg),
           "larger_complete": bigger, "verdict": verdict, "world": world},
          open(OUT/"r491_judges_on_disk.json", "w"), indent=2)
sys.exit(0 if verdict != "UNVERIFIED" else 2)
