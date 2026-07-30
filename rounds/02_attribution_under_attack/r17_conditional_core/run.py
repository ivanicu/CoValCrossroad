"""r17 -- Conditional cores routed by cross-prompt history.

An earlier design routed raters using half of a prompt's criteria and scored them
on the other half. CoVal cannot support it: every prompt carries the same six seed
criteria, so no prompt has more than six shared items and a k=4 core already uses
four. That infeasibility is recorded in the README because it constrains anyone
attempting personalised-rubric work on this release.

Raters are the axis with room. Each rated 5-20 prompts, and r01 showed their
agreement persists across disjoint prompts after response style is removed. So the
router sees only a rater's OTHER prompts -- never the one being scored.

  SINGLE   one direction per core item, fitted on TRAIN raters
  LEARNED  per-bloc directions, TEST raters routed by cross-prompt coordinate
  ORACLE   each TEST bloc handed the better direction map; unreachable ceiling
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = str(_HERE.parents[2])
_RES = str(_HERE / "results")
sys.path.insert(0, _ROOT)
from covalx import make_core  # noqa: E402

RULES = ("utility", "majority", "consensus", "constituency")


def conflict_aware(M, k):
    cons, pol = [], []
    for j in range(M.shape[1]):
        v = M[:, j]; v = v[~np.isnan(v)]
        if v.size == 0:
            cons.append((0.0, j)); pol.append((0.0, j)); continue
        lo = float(np.percentile(v, 25))
        cons.append((lo if lo > 0 else 0.0, j))
        p, ng = float((v > 0).mean()), float((v < 0).mean())
        pol.append((4 * p * ng * float(np.mean(np.abs(v))) / 10.0, j))
    cons.sort(key=lambda t: (-t[0], t[1])); pol.sort(key=lambda t: (-t[0], t[1]))
    out, seen = [], set()
    for _, j in cons[: max(1, k // 2)]:
        out.append(j); seen.add(j)
    for _, j in pol:
        if len(out) >= k:
            break
        if j not in seen:
            out.append(j); seen.add(j)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rubrics", type=Path, default=Path(_ROOT) / "data/conversation_rubrics.jsonl")
    ap.add_argument("--out", type=Path, default=Path(_RES) / "r17_conditional_core.json")
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--boot", type=int, default=4000)
    a = ap.parse_args()

    # ---- global rater x shared-item matrix, remembering which prompt owns which column
    prompts, col_prompt, cols_of = [], [], defaultdict(list)
    rater_ix, rows = {}, []
    entries = []
    for line in open(a.rubrics, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        items = rec.get("coval_full") or []
        raters = {s["annotator_id"] for it in items for s in it.get("scores") or []}
        if len(raters) < 10:
            continue
        thr = max(2, (len(raters) + 1) // 2)
        shared = [it for it in items if len(it.get("scores") or []) >= thr]
        if len(shared) < a.k:
            continue
        pid = len(prompts); prompts.append(rec["conversation"]["id"])
        for it in shared:
            c = len(col_prompt); col_prompt.append(pid); cols_of[pid].append(c)
            for s in it["scores"]:
                r = s["annotator_id"]
                if r not in rater_ix:
                    rater_ix[r] = len(rater_ix)
                entries.append((rater_ix[r], c, float(s["score"])))
    nR, nC = len(rater_ix), len(col_prompt)
    G = np.full((nR, nC), np.nan)
    for i, c, v in entries:
        G[i, c] = v
    col_prompt = np.array(col_prompt)
    print(f"raters {nR}  shared columns {nC}  prompts {len(prompts)}")
    print(f"  density {np.mean(~np.isnan(G)):.4%}  ratings/rater median "
          f"{np.median((~np.isnan(G)).sum(1)):.0f}")

    # global bloc axis over raters, item-centred
    Gc = G - np.nanmean(G, axis=0, keepdims=True)
    Gz = np.nan_to_num(Gc)
    u, s, vt = np.linalg.svd(Gz, full_matrices=False)
    axis = vt[0]
    print(f"  top singular value share {s[0]**2/ (s**2).sum():.3%}")

    rng = np.random.default_rng(20260727)
    names = list(RULES) + ["conflict_aware"]
    rows = {nm: {"SINGLE": [], "LEARNED": [], "ORACLE": []} for nm in names}
    agree_oracle = []

    for pid in range(len(prompts)):
        cols = np.array(cols_of[pid])
        if len(cols) < a.k:
            continue
        who = np.where(~np.isnan(G[:, cols]).all(axis=1))[0]
        if len(who) < 10:
            continue
        # routing coordinate: this rater's OTHER prompts only
        other = np.ones(nC, dtype=bool); other[cols] = False
        coord = np.nan_to_num(Gc[np.ix_(who, np.where(other)[0])]) @ axis[other]
        tr = rng.permutation(len(who))
        train, test = who[tr[: len(who)//2]], who[tr[len(who)//2:]]
        ctr, cte = coord[tr[: len(who)//2]], coord[tr[len(who)//2:]]
        if len(train) < 4 or len(test) < 4:
            continue
        thr_c = float(np.median(ctr))
        blocA, blocB = train[ctr >= thr_c], train[ctr < thr_c]
        testA, testB = test[cte >= thr_c], test[cte < thr_c]
        if min(len(blocA), len(blocB), len(testA), len(testB)) < 2:
            continue

        M = G[np.ix_(train, cols)]
        cores = {nm: [j for j, _ in make_core(M, nm, a.k)] for nm in RULES}
        cores["conflict_aware"] = conflict_aware(M, a.k)

        def dmap(rows_sel, core):
            d = {}
            for j in core:
                v = G[np.ix_(rows_sel, [cols[j]])].ravel(); v = v[~np.isnan(v)]
                d[j] = 1 if (v.size == 0 or v.mean() >= 0) else -1
            return d

        def sat(rows_sel, core, d):
            vals = []
            for j in core:
                v = G[np.ix_(rows_sel, [cols[j]])].ravel(); v = v[~np.isnan(v)]
                if v.size:
                    vals.append(d[j] * float(v.mean()))
            return float(np.mean(vals)) if vals else np.nan

        for nm, core in cores.items():
            dA, dB, dAll = dmap(blocA, core), dmap(blocB, core), dmap(train, core)
            single = [sat(testA, core, dAll), sat(testB, core, dAll)]
            learned = [sat(testA, core, dA), sat(testB, core, dB)]
            oracle = [max(sat(testA, core, dA), sat(testA, core, dB)),
                      max(sat(testB, core, dA), sat(testB, core, dB))]
            for key, vals in (("SINGLE", single), ("LEARNED", learned), ("ORACLE", oracle)):
                vals = [x for x in vals if not np.isnan(x)]
                if vals:
                    rows[nm][key].append(min(vals))
            if nm == "conflict_aware":
                agree_oracle.append(float(np.mean(
                    [abs(l - o) < 1e-9 for l, o in zip(learned, oracle)])))

    out = {}
    print(f"\n{'rule':16s} {'SINGLE':>8} {'LEARNED':>8} {'ORACLE':>8}  LEARNED-SINGLE 95% CI")
    for nm in names:
        r = {k: np.array(v) for k, v in rows[nm].items()}
        m = min(len(v) for v in r.values())
        if m < 20:
            print(f"{nm:16s} too few usable prompts ({m})"); continue
        d = r["LEARNED"][:m] - r["SINGLE"][:m]
        bs = np.array([d[rng.integers(0, m, size=m)].mean() for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        v = "helps" if lo > 0 else "hurts" if hi < 0 else "no gain"
        out[nm] = {"single": float(r["SINGLE"][:m].mean()), "learned": float(r["LEARNED"][:m].mean()),
                   "oracle": float(r["ORACLE"][:m].mean()), "delta": float(d.mean()),
                   "ci": [float(lo), float(hi)], "verdict": v, "prompts": int(m)}
        print(f"{nm:16s} {out[nm]['single']:>8.3f} {out[nm]['learned']:>8.3f} "
              f"{out[nm]['oracle']:>8.3f}  {d.mean():+.3f} [{lo:+.3f},{hi:+.3f}] {v}")

    if agree_oracle:
        print(f"\n  learned router matched the oracle choice on "
              f"{float(np.mean(agree_oracle)):.1%} of blocs")
        out["router_matches_oracle"] = float(np.mean(agree_oracle))
    ca = out.get("conflict_aware")
    if ca:
        out["conclusion"] = (
            "CONDITIONAL ENCODING DOES NOT RESCUE IT: with routing learned from a "
            "rater's other prompts, per-bloc directions give no gain over a single "
            "signed core, so r16 stands." if ca["verdict"] != "helps" else
            "CONDITIONAL ENCODING RESCUES IT: learned routing beats a single signed "
            "core, so r16 measured the encoding rather than the preservation of "
            "disagreement.")
        print(f"  -> {out['conclusion']}")
    Path(_RES).mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
