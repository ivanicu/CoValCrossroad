#!/usr/bin/env python3
"""
corebench/judge_core.py -- score an arbitrary GENERATED core against the release.

WHY THIS EXISTS. R283's overlap measurement settled that `coval_core` is REWRITTEN, not
selected: only 8% of its items appear verbatim in `coval_full`, 23% at similarity >= 0.90,
median best-match 0.676. So FULL -> CORE is a GENERATION task, and a generated core carries
no `scores` field -- its satisfaction against each response must be judged.

Emits the same `meta`/`sat` npz layout `R220.load_sat` reads, so every existing analysis in
E05 can consume a new core without changes.

Usage:  judge_core.py --core coval_core --out results/sat_coval_core.npz
        judge_core.py --core path/to/core.json --out ...
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, sys, time
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
MODEL = "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/Qwen3.5-2B-Base"
L = "ABCD"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--core", required=True,
                    help="'coval_core' for the incumbent, or a JSON {pid: [criterion, ...]}")
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--model", default=MODEL,
                    help="judge model dir; default Qwen3.5-2B-Base. A second judge is how `cross-model` stops being registered as impossible.")
    a = ap.parse_args()

    from covalx.judge import Judge, build_prompt, load_join
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")

    if a.core == "coval_core":
        cores = {pid: [i["criterion"] for i in (rub.get("coval_core") or [])]
                 for pid, _p, rub in joined}
    else:
        cores = json.loads(pathlib.Path(a.core).read_text())

    replies = {}
    for pid, prompt, _rub in joined:
        replies[pid] = {r["response_index"]: r["messages"][-1]["content"]
                        for r in prompt["responses"]}

    pids = [p for p, _, _ in joined if cores.get(p)]
    if a.limit:
        pids = pids[:a.limit]

    prompts, meta = [], []
    for pid in pids:
        for i, crit in enumerate(cores[pid]):
            for ltr in L:
                rep = replies[pid].get(ltr)
                if rep is None:
                    continue
                if isinstance(rep, list):
                    rep = " ".join(x.get("text", "") if isinstance(x, dict) else str(x)
                                   for x in rep)
                prompts.append(build_prompt(crit, rep))
                meta.append(f"{pid}|{i}|{ltr}")

    print(f"  core       : {a.core}")
    print(f"  prompts    : {len(pids)}   judge calls: {len(prompts)}", flush=True)
    t0 = time.time()
    j = Judge(a.model, batch=a.batch)
    print(f"  judge: {a.model}", flush=True)
    sat = j.score(prompts) if hasattr(j, "score") else j(prompts)
    sat = np.asarray(sat, dtype=np.float32)
    out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    # ⛔ PROVENANCE, ADDED 2026-08-04 AFTER AN ARC THAT KEPT HITTING ITS ABSENCE. R414 could not tell
    #   whether two 0.8B naming families were the same run; R415 called five pairs "same code" and was
    #   wrong; R416 found their criteria differed; R417 showed the judge has no stochastic step, so the
    #   only remaining non-stochastic mover is CONFIGURATION -- and the artifacts recorded none of it.
    #   Four rounds of archaeology on files that never wrote down what made them. This writes it.
    #   `load_sat` reads only `meta` and `sat`, so the extra key is backwards-compatible with all 93
    #   existing artifacts; they simply carry no provenance and are exempt by age, not by merit.
    prov = {
        "core": str(a.core),
        "model": str(a.model),
        "batch": int(a.batch),
        "limit": int(a.limit),
        "n_prompts": len(pids),
        "n_calls": len(prompts),
        "producer": "corebench/judge_core.py",
        "producer_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "core_sha256": (hashlib.sha256(pathlib.Path(a.core).read_bytes()).hexdigest()
                        if a.core != "coval_core" and pathlib.Path(a.core).exists() else None),
    }
    np.savez_compressed(out, meta=np.array(meta), sat=sat,
                        provenance=np.array(json.dumps(prov, sort_keys=True)))
    print(f"  wrote {out}  ({len(sat)} scores, {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    main()
