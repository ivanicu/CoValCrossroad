#!/usr/bin/env python3
"""R555 · Row 2 named a MODEL where the requirement was a PROPERTY.

Register row 2 reads "a second, stronger judge -- Qwen2.5-7B-Instruct ... but OOMs in bf16" and
treats that model's OOM as the row's blocker. The REQUIREMENT is a judge stronger than the home
judge. The campaign's judges are Qwen3.5-2B-Base (home) and Qwen3.5-0.8B-Base (second), so
Qwen3.5-4B -- 2x the home judge, 9.32 GB, complete (R554) -- satisfies the requirement if it loads.

ESTIMAND  does Qwen3.5-4B load in bf16 on this box and return scores over a real prompt batch?
IDENT     fully identified: run it and look. Peak VRAM measured, not modelled (R540/R541 cost me
          17x and 94x by modelling what a log already knew).
SCOPE     population = 24 real prompts from the home release · instrument = covalx.Judge ·
          baseline = the 2B home judge on the SAME prompts · regime = bf16, 16 GB RTX 5080.
WORLDS    A it OOMs or fails -> row 2's blocker survives, just for a different model.
          B it loads and scores -> row 2 is UNBLOCKED and its wording described the instance.
KILL      pre-registered: OOM, load failure, or a degenerate score vector (all-equal) -> WORLD A.
POS CTRL  the 2B home judge must load and score the SAME batch. If it does not, the harness is
          broken and the 4B result says nothing.
NEG CTRL  a nonexistent checkpoint path must FAIL to load. Else "it loaded" is not informative.
ARTIFACT  results/fourb.json  (scores, peak VRAM, wall-clock, per-arm)
"""
import json, pathlib, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
import torch
from covalx.judge import Judge, load_join, build_prompt

FOURB = "/mnt/e/cache/huggingface/hub/models--Qwen--Qwen3.5-4B/snapshots"
HOME  = "Qwen/Qwen3.5-2B-Base"
N     = 24

def resolve(p):
    d = pathlib.Path(p)
    if d.name == "snapshots" and d.is_dir():
        snaps = [s for s in d.iterdir() if s.is_dir() and any(s.glob("*.safetensors"))]
        return str(snaps[0]) if snaps else None
    return p

def try_judge(path, prompts, label):
    t0 = time.time()
    torch.cuda.reset_peak_memory_stats() if torch.cuda.is_available() else None
    try:
        j = Judge(path, batch=4)
        sat = j.score(prompts)
        peak = torch.cuda.max_memory_allocated() / 1e9 if torch.cuda.is_available() else -1.0
        del j; torch.cuda.empty_cache()
        uniq = len(set(round(float(x), 6) for x in sat))
        return {"ok": True, "n": len(sat), "distinct": uniq, "peak_vram_gb": round(peak, 2),
                "secs": round(time.time() - t0, 1), "mean": round(float(sum(sat) / len(sat)), 4)}
    except Exception as e:
        torch.cuda.empty_cache()
        return {"ok": False, "error": f"{type(e).__name__}: {str(e)[:160]}",
                "secs": round(time.time() - t0, 1)}

joined = load_join(ROOT / "data" / "comparisons.jsonl",
                   ROOT / "data" / "conversation_rubrics.jsonl")[:N]
# ⚠ FIRST VERSION GUESSED THE SCHEMA and crashed: `rub` is a dict, and build_prompt takes
# (criterion: str, reply: str), not messages+responses. Mirroring corebench/judge_core.py:66-77,
# the canonical call site, rather than inventing a second way to build the same prompt.
def _flat(rep):
    if isinstance(rep, list):
        return " ".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in rep)
    return str(rep)

prompts = []
for _pid, pr, rub in joined:
    crits = [c["criterion"] if isinstance(c, dict) else str(c) for c in rub["coval_core"]][:4]
    reps = pr.get("responses") or {}
    reps = list(reps.values()) if isinstance(reps, dict) else list(reps)
    for crit in crits:
        for rep in reps[:1]:
            prompts.append(build_prompt(crit, _flat(rep)))
prompts = prompts[:N]
print(f"  batch: {len(prompts)} real prompts from the home release\n")

fb = resolve(FOURB)
print(f"  4B resolved to: {fb}")

print("\n  NEGATIVE CONTROL  a nonexistent checkpoint must FAIL:")
neg = try_judge("/no/such/checkpoint/at/all", prompts[:2], "neg")
print(f"    loaded={neg['ok']} -> {'PASS' if not neg['ok'] else 'FAIL'}  {neg.get('error','')[:80]}")
if neg["ok"]:
    sys.exit(2)

print("\n  POSITIVE CONTROL  the 2B home judge on the same batch:")
pos = try_judge(HOME, prompts, "home")
print(f"    {pos}")
if not pos["ok"] or pos.get("distinct", 0) < 2:
    print("    -> harness broken or scores degenerate; the 4B result would say nothing")
    sys.exit(2)

print("\n  THE TEST  Qwen3.5-4B:")
four = try_judge(fb, prompts, "4B") if fb else {"ok": False, "error": "not resolved"}
print(f"    {four}")

world = "B" if (four["ok"] and four.get("distinct", 0) >= 2) else "A"
print(f"\n  WORLD {world} -- " + (
    "the 4B loads and scores; row 2's requirement is SATISFIABLE on this box."
    if world == "B" else "it failed; row 2's blocker survives for a different model."))
(pathlib.Path(__file__).parent / "results" / "fourb.json").write_text(json.dumps(
    {"world": world, "home_2b": pos, "qwen35_4b": four, "negative_control": neg,
     "n_prompts": len(prompts), "four_b_path": fb,
     "note": "row 2 asks for a judge STRONGER than the home judge; 4B is 2x its parameters"},
    indent=2))
