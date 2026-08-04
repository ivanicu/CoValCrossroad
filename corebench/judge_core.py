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
# ⛔ HASHED AT IMPORT, NOT AT WRITE TIME, AND THE FIRST REAL USE OF THIS FIELD IS WHAT CAUGHT IT.
#   The original computed `sha256(Path(__file__).read_bytes())` inside main(), i.e. it hashed the
#   file AS IT SAT ON DISK WHEN THAT LINE RAN -- not the code Python had loaded. Task 633 proved it:
#   its artifact carries `core_sha256: null`, a field only the OLD code emits, beside a
#   producer_sha256 equal to the PATCHED file, because the file was edited between import and write.
#   A field that looks like it identifies the running code while identifying the file's current
#   contents is worse than no field: it would make two artifacts look like they shared a producer
#   when they did not. Module scope is the closest a script can get to load time.
PRODUCER_SHA256 = __import__("hashlib").sha256(
    pathlib.Path(__file__).read_bytes()).hexdigest()

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
        "producer_sha256": PRODUCER_SHA256,   # taken at IMPORT, see the note above
        # ⛔ HASH WHAT WAS ACTUALLY SCORED, NOT THE INPUT FILE. My first version hashed
        #   `pathlib.Path(a.core)` and returned None for `--core coval_core`, whose criteria are read
        #   from the rubric rather than a JSON -- so the ONE path used to score the released core
        #   would carry no criteria hash at all. That is precisely R416's lesson: two runs called
        #   "same code" whose CRITERIA differed. Hashing the built `cores` dict covers both paths
        #   uniformly and records the criteria that were scored rather than the file they came from.
        "criteria_sha256": hashlib.sha256(
            json.dumps({k: v for k, v in sorted(cores.items())}, sort_keys=True).encode()
        ).hexdigest(),
        "n_criteria": sum(len(v) for v in cores.values()),
    }
    np.savez_compressed(out, meta=np.array(meta), sat=sat,
                        provenance=np.array(json.dumps(prov, sort_keys=True)))
    print(f"  wrote {out}  ({len(sat)} scores, {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    main()
