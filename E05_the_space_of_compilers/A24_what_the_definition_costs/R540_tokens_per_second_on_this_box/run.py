#!/usr/bin/env python3
"""R540 — measure tokens/sec for the two judge sizes, converting R539's call count to wall-clock.

R539 priced one rows-3/4 round at 16,440 model calls and named what it did NOT measure: wall-clock,
which needs a tokens/sec figure for the local model on this GPU. My closing line called that "a
single pueue job", and check #139 verified the claim rather than assuming it -- the model store
holds Qwen3.5-0.8B-Base and Qwen3.5-2B-Base, torch and transformers are in this venv, the 5080 is
at 791 of 16303 MiB, and gpu-run is on PATH.

⭐ The two model sizes are not arbitrary: they are the SAME two the campaign's judges already are
(sat_* is 2B, sat08_* is 0.8B), so the measurement converts R539's count on the actual instruments.

ESTIMAND (before method): decode throughput in tokens/sec for each judge size, and the implied
  wall-clock for 16,440 calls at a measured output length.
IDENTIFICATION: fully identified on this box; ⚠ NOT transferable -- a throughput number is a fact
  about THIS GPU, driver and dtype, and expires at the next infra event.
SCOPE  population: n/a, an instrument measurement · instrument: the model itself · baseline: n/a ·
  regime: bf16 on an RTX 5080, batch 1, this venv's torch.
WORLDS  A · throughput makes the round cheap in wall-clock -- hours or less.
        B · it does not, and cost becomes a real answer to "why not run it".
KILL (pre-registered): >12 h implied for 16,440 calls puts it in world B.
POSITIVE CONTROL: the 2B model must be SLOWER than the 0.8B. If the larger model is not slower the
  measurement is not measuring decode throughput.
NEGATIVE CONTROL: a second timing run at the same size must land within 20% of the first, else the
  number is noise and no wall-clock follows from it.
NOISE FLOOR: 2 repeats per size, reported.
MULTIPLICITY: 2 sizes x 2 repeats; all printed.
IMPOSSIBLE HERE: throughput under vLLM or batching -- vllm is ABSENT from this venv, so this is a
  batch-1 transformers figure and is a LOWER bound on what the round would actually achieve.
"""
import json, pathlib, time, sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

STORE = pathlib.Path("/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly")
SIZES = [("0.8B", STORE / "Qwen3.5-0.8B-Base"), ("2B", STORE / "Qwen3.5-2B-Base")]
NEW_TOKENS, CALLS = 128, 16440

def main():
    if not STORE.exists():
        print("  model store absent -> UNRUNNABLE"); return 2
    print(f"  GPU: {torch.cuda.get_device_name(0)}  torch {torch.__version__}")
    rows = {}
    for label, path in SIZES:
        if not path.exists():
            print(f"  {label}: {path} absent -> skipped"); continue
        tok = AutoTokenizer.from_pretrained(path)
        model = AutoModelForCausalLM.from_pretrained(path, torch_dtype=torch.bfloat16,
                                                     device_map="cuda")
        model.eval()
        prompt = "Rate whether the response satisfies the criterion. Criterion: clarity.\nResponse:"
        ids = tok(prompt, return_tensors="pt").to("cuda")
        with torch.no_grad():                      # warmup, excluded from timing
            model.generate(**ids, max_new_tokens=8, do_sample=False)
        reps = []
        for _ in range(2):
            torch.cuda.synchronize(); t0 = time.perf_counter()
            with torch.no_grad():
                out = model.generate(**ids, max_new_tokens=NEW_TOKENS, do_sample=False)
            torch.cuda.synchronize()
            dt = time.perf_counter() - t0
            n = out.shape[-1] - ids["input_ids"].shape[-1]
            reps.append(n / dt)
        tps = sum(reps) / len(reps)
        spread = abs(reps[0] - reps[1]) / tps
        hours = CALLS * NEW_TOKENS / tps / 3600
        rows[label] = {"tok_per_s": tps, "reps": reps, "rel_spread": spread,
                       "implied_hours_16440_calls": hours}
        print(f"  {label:<5} {tps:>8.1f} tok/s   reps {reps[0]:.1f}/{reps[1]:.1f}   "
              f"spread {spread:.1%}   -> {hours:.2f} h for {CALLS} calls x {NEW_TOKENS} tok")
        del model; torch.cuda.empty_cache()

    if len(rows) < 2:
        print("  fewer than two sizes measured -> UNVERIFIED"); return 0
    pc = rows["2B"]["tok_per_s"] < rows["0.8B"]["tok_per_s"]
    print(f"\n  POSITIVE CONTROL  2B slower than 0.8B: {pc} -> {'PASS' if pc else 'FAIL'}")
    nc = all(r["rel_spread"] <= 0.20 for r in rows.values())
    print(f"  NEGATIVE CONTROL  repeat within 20% at both sizes: {nc} -> "
          f"{'PASS' if nc else 'FAIL -- the number is noise'}")
    if not (pc and nc):
        print("  -> UNVERIFIED."); return 0
    worst = max(r["implied_hours_16440_calls"] for r in rows.values())
    world = "B" if worst > 12 else "A"
    print(f"\n  ⭐ worst-case implied wall-clock for one rows-3/4 round: {worst:.2f} h")
    print(f"  WORLD {world} -- " +
          ("the round is cheap in wall-clock; cost is not an answer to 'why not'" if world == "A"
           else "wall-clock is a real answer"))
    print(f"  ⚠ batch-1 transformers, vllm ABSENT -> this is a LOWER bound on achievable throughput.")

    out = pathlib.Path(__file__).parent / "results/throughput.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"rows": rows, "calls": CALLS, "new_tokens": NEW_TOKENS,
                               "world": world, "worst_hours": worst,
                               "caveat": "batch-1 transformers; vllm absent; expires at next infra event"},
                              indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
