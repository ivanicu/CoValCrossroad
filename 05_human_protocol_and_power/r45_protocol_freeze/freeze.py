"""r45 (queue item 7) -- freeze the human-experiment frame by CONTENT, not by reference.

r38 selected 60 prompts, assigned them to four cells and computed sampling
weights.  It froze a list of prompt IDs.  That is not enough to run a human
experiment against, because the thing the experiment must rank is the exact
RESPONSE TEXT, and r12's fresh responses were generated at temperature 0.9 with
no seed -- "the fresh responses for prompt X" is not a well-defined object
outside the one file that happens to hold them.

So this freezes the payload and hashes it.  Every response gets a SHA-256, and
the frame gets a manifest hash over all of them.  When human rankings come back,
the first check is that the responses they saw hash to this manifest.  Without
that, H_fresh -- the counterfactual this entire project is waiting on -- would be
human rankings of *some* responses, comparable to nothing.

Nothing here is a new measurement.  It is the artifact the measurement needs to
be interpretable when it eventually exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"


def _git_anchor() -> dict:
    """The commit this freeze was taken at, and whether the tree was clean.

    A freeze whose anchor is null cannot be checked against anything later. A
    freeze taken from a DIRTY tree is worse than one with no anchor at all,
    because the hash names a state that was never what ran -- so the flag is
    recorded beside it, not inferred.
    """
    import subprocess
    here = pathlib.Path(__file__).resolve().parents[2]
    def git(*a):
        r = subprocess.run(["git", *a], cwd=here, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    head = git("rev-parse", "HEAD")
    status = git("status", "--porcelain")
    return {
        "frozen_at_commit": head,
        "frozen_tree_dirty": None if status is None else bool(status.strip()),
    }


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--r38", type=Path,
                    default=_ROOT / "05_human_protocol_and_power/r38_human_sampling_power/results/"
                                    "r38_human_sampling_power.json")
    ap.add_argument("--gen", type=Path,
                    default=_ROOT / "02_attribution_under_attack/r12_response_set/results/"
                                    "a12_fresh_generations.json")
    ap.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    ap.add_argument("--out", type=Path, default=_RES / "r45_frozen_frame.json")
    a = ap.parse_args()

    frame = json.loads(a.r38.read_text())
    gen = json.loads(a.gen.read_text())
    gidx = {p: i for i, p in enumerate(gen["prompt_ids"])}

    texts = {}
    for line in open(a.comparisons, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        texts[rec["prompt_id"]] = rec

    rows, missing = [], []
    for f in frame["frame"]:
        pid = f["pid"]
        if pid not in gidx or pid not in texts:
            missing.append(pid)
            continue
        i = gidx[pid]
        rec = texts[pid]
        user = [m["content"] for m in rec["prompt"]["messages"] if m["role"] == "user"]
        orig = gen["original"][i]
        fresh = gen["fresh"][i]
        rows.append({
            "pid": pid, "cell": f["cell"], "sampling_weight": f["sampling_weight"],
            "distance": f["distance"], "disagreement": f["disagreement"],
            "prompt_text": user[-1] if user else None,
            "prompt_sha256": sha(user[-1]) if user else None,
            "original": [{"text": t, "sha256": sha(t)} for t in orig],
            "fresh": [{"text": t, "sha256": sha(t)} for t in fresh],
        })

    # Manifest hash: order-independent over responses, so a reordered delivery
    # still verifies, but any edited character does not.
    leaves = sorted(h for r in rows for h in
                    [r["prompt_sha256"]] + [x["sha256"] for x in r["original"]]
                    + [x["sha256"] for x in r["fresh"]] if h)
    manifest = sha("\n".join(leaves))

    cells = {}
    for r in rows:
        cells[r["cell"]] = cells.get(r["cell"], 0) + 1

    doc = {
        # Was hard-coded to None for the life of this round (entry 77). A field
        # named `frozen_at_commit` holding null reads as "the anchor was
        # recorded" while recording nothing -- and this artifact is, in its own
        # README row, "the only definition of the object H_fresh refers to".
        # A freeze taken from a dirty tree is not a freeze, so the dirty flag is
        # stamped beside the hash rather than being left for a reader to assume.
        **_git_anchor(),
        "n_prompts": len(rows),
        "n_missing_from_frame": len(missing),
        "missing_pids": missing,
        "cells": cells,
        "sampling_weights": frame["sampling_weights"],
        "responses_per_prompt": {"original": 4, "fresh": gen["per_prompt"]},
        "generator": gen["generator"],
        "generation_params": {k: gen[k] for k in
                              ("temperature", "top_p", "max_new_tokens")},
        "manifest_sha256": manifest,
        "verification": (
            "Human rankings are admissible only if the responses shown hash to the "
            "per-response sha256 values below and the recomputed manifest equals "
            f"{manifest}. r12's generation is stochastic and unseeded, so 'the fresh "
            "responses' is not recoverable by re-running anything -- this file is the "
            "only definition of the object H_fresh refers to."),
        "prompts": rows,
    }
    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"froze {len(rows)} prompts ({len(missing)} missing)")
    print(f"  cells: {cells}")
    print(f"  responses hashed: {len(leaves)}")
    print(f"  manifest sha256: {manifest}")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
