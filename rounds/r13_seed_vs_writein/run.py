"""r13 -- Seed criteria vs write-in criteria: who carries the advantage?

r12 showed the real rubric's edge over an unrelated rubric does not survive on
responses its authors never saw. Two readings remain: the criteria encode facts
about those four responses (they were written after reading them), or the gold
model simply fails out of distribution.

Seed criteria were prepared alongside candidate generation; write-ins were
authored after the annotator read all four. So the released corpus already
contains the experiment: split the rubric by provenance and measure attribution
separately.

Provenance proxy, stated honestly: the release does not flag seed vs write-in.
Seeds were shown to every rater for a prompt, write-ins to nobody, so rating
count separates them cleanly -- the visibility distribution is perfectly bimodal
(9,684 items with one score, 5,564 rated by at least half, nothing between).
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = str(_HERE.parents[1])
_RES = str(_HERE / "results")
sys.path.insert(0, _ROOT)
from covalx import LABELS, human_pairs, load_join  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparisons", type=Path, default=Path(_ROOT) / "data/comparisons.jsonl")
    ap.add_argument("--rubrics", type=Path, default=Path(_ROOT) / "data/conversation_rubrics.jsonl")
    ap.add_argument("--sat", type=Path,
                    default=Path(_ROOT) / "rounds/r04_rebuild_satisfaction/results/a04_full.npz")
    ap.add_argument("--out", type=Path, default=Path(_RES) / "r13_seed_vs_writein.json")
    ap.add_argument("--boot", type=int, default=4000)
    ap.add_argument("--with-shuffled", action="store_true",
                    help="judge the donor's criteria against THIS prompt's responses, "
                         "which the saved matrix cannot supply")
    ap.add_argument("--prompts", type=int, default=250)
    a = ap.parse_args()

    z = np.load(a.sat, allow_pickle=True)
    lut = {}
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = str(m).split("|")
        lut.setdefault((pid, int(ci)), {})[lab] = float(s)

    joined = load_join(a.comparisons, a.rubrics)
    rng = np.random.default_rng(20260727)
    prompts = [p for p, _, _ in joined]
    donor = {p: prompts[(i + 1 + rng.integers(0, len(prompts) - 1)) % len(prompts)]
             for i, p in enumerate(prompts)}

    # provenance-split criterion index per prompt
    crit = {}
    for pid, comp, rub in joined:
        items = rub.get("coval_full") or []
        raters = {s["annotator_id"] for it in items for s in it.get("scores") or []}
        thr = max(2, (len(raters) + 1) // 2)
        seed, writein, ci = [], [], 0
        for it in items:
            sc = it.get("scores") or []
            if sc:
                (seed if len(sc) >= thr else writein).append(ci)
            ci += 1
        crit[pid] = {"seed": seed, "writein": writein}

    pairs = {pid: human_pairs(comp["metadata"]["assessments"]) for pid, comp, _ in joined}

    def agree(pid, idx_source_pid, which):
        """score this prompt's responses using `which` criteria taken from idx_source_pid"""
        idx = crit.get(idx_source_pid, {}).get(which, [])
        if not idx or not pairs.get(pid):
            return None
        score = {}
        for lab in LABELS:
            v = [lut[(idx_source_pid, c)][lab] for c in idx
                 if (idx_source_pid, c) in lut and lab in lut[(idx_source_pid, c)]]
            if v:
                score[lab] = float(np.mean(v))
        if len(score) < 2:
            return None
        ok = tot = 0
        for x, y in pairs[pid]:
            if x in score and y in score:
                tot += 1
                ok += int(score[x] > score[y])
        return ok / tot if tot else None

    if a.with_shuffled:
        import torch
        from covalx import Judge, build_prompt
        sub = prompts[: a.prompts]
        texts = {pid: {r["response_index"]: r["messages"][0]["content"]
                       for r in comp["responses"]}
                 for pid, comp, _ in joined if pid in set(sub)}
        crit_text = {}
        for pid, comp, rub in joined:
            items = rub.get("coval_full") or []
            crit_text[pid] = [it["criterion"] for it in items if it.get("scores")]
        judge = Judge(__import__("os").environ.get("COVALX_MODEL_2B",
                                                   "Qwen/Qwen3.5-2B-Base"), batch=32)
        tasks, meta = [], []
        for pid in sub:
            d = donor[pid]
            for which in ("seed", "writein"):
                for ci in crit.get(d, {}).get(which, []):
                    if ci >= len(crit_text.get(d, [])):
                        continue
                    for lab in texts.get(pid, {}):
                        tasks.append(build_prompt(crit_text[d][ci], texts[pid][lab]))
                        meta.append((which, pid, ci, lab))
        print(f"  shuffled-arm judgements: {len(tasks):,}", flush=True)
        sat = judge.score(tasks)
        shuf = {}
        for (which, pid, ci, lab), s in zip(meta, sat):
            shuf.setdefault((which, pid), {}).setdefault(lab, []).append(float(s))
        shuf_acc = {"seed": [], "writein": []}
        for which in ("seed", "writein"):
            for pid in sub:
                d0 = shuf.get((which, pid))
                if not d0 or not pairs.get(pid):
                    continue
                score = {lab: float(np.mean(v)) for lab, v in d0.items()}
                ok = tot = 0
                for x, y in pairs[pid]:
                    if x in score and y in score:
                        tot += 1
                        ok += int(score[x] > score[y])
                if tot:
                    shuf_acc[which].append(ok / tot)
        del judge
        torch.cuda.empty_cache()
    else:
        shuf_acc = {"seed": [], "writein": []}

    out = {}
    print(f"{'provenance':12s} {'real':>8} {'shuffled':>9} {'attribution':>12} {'95% CI':>22} {'n':>6}")
    for which in ("seed", "writein"):
        rows = []
        for pid in prompts:
            # NOTE: a shuffled rubric must be scored on THIS prompt's responses.
            # The saved satisfaction matrix only holds (own prompt x own criteria),
            # so the shuffled arm is unavailable here and is computed in r10/r12.
            r = agree(pid, pid, which)
            if r is not None:
                rows.append(r)
        arr = np.array(rows)
        bs = np.array([arr[rng.integers(0, len(arr), size=len(arr))].mean()
                       for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        sa = np.array(shuf_acc[which]) if shuf_acc[which] else None
        rec = {"real": float(arr.mean()), "ci": [float(lo), float(hi)],
               "prompts": int(len(arr))}
        if sa is not None and len(sa):
            # paired on prompts is unavailable (different subsets), so compare means
            attr = float(arr[: len(sa)].mean() - sa.mean())
            bsd = np.array([arr[rng.integers(0, len(sa), size=len(sa))].mean()
                            - sa[rng.integers(0, len(sa), size=len(sa))].mean()
                            for _ in range(a.boot)])
            alo, ahi = np.percentile(bsd, [2.5, 97.5])
            rec.update({"shuffled": float(sa.mean()), "attribution": attr,
                        "attribution_ci": [float(alo), float(ahi)]})
            print(f"{which:12s} {arr.mean():>8.4f} {sa.mean():>9.4f} {attr:>+12.4f} "
                  f"{f'[{alo:+.4f},{ahi:+.4f}]':>22} {len(sa):>6}")
        else:
            print(f"{which:12s} {arr.mean():>8.4f} {'--':>9} {'--':>12} "
                  f"{f'[{lo:.4f},{hi:.4f}]':>22} {len(arr):>6}")
        out[which] = rec

    d = out["writein"]["real"] - out["seed"]["real"]
    print(f"\n  write-in minus seed: {d:+.4f}")
    out["writein_minus_seed"] = float(d)
    Path(_RES).mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
