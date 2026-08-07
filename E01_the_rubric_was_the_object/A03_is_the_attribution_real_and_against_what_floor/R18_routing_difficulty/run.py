"""r18 -- Where does routing actually have to work?

r17 reported the learned router agreeing with the oracle on 84.6% of blocs while
the bloc axis carried 0.541% of the singular mass. Those two numbers do not sit
together comfortably, and the likely reason is that agreement is free: if the two
blocs would sign a core item the same way, any router is right about it.

So this restricts to CONTESTED items -- core items where the two blocs' fitted
directions disagree -- and asks, per test rater, whether the direction the router
hands them matches the sign they themselves gave.

Reported alongside:
  contested_share   how often routing has anything to decide at all
  accuracy_all      accuracy over all core items (the inflated figure)
  accuracy_contested   accuracy where it matters (chance = 0.5)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = str(next(p for p in _HERE.parents if (p / "covalx").is_dir()))
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


# SCHEMA (entry 61/62): "bloc" is the frozen word -- FROZEN.md section 3
# says read this partition as a LATENT PROFILE SPLIT, never as a bloc,
# minority or constituency. A field NAME is unreachable by any prose
# annotation, so the freeze cannot be delivered to it; it has to be
# renamed. Values and computation are unchanged.
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rubrics", type=Path, default=Path(_ROOT) / "data/conversation_rubrics.jsonl")
    ap.add_argument("--out", type=Path, default=Path(_RES) / "r18_routing_difficulty.json")
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--boot", type=int, default=4000)
    a = ap.parse_args()

    prompts, col_prompt, cols_of = [], [], defaultdict(list)
    rater_ix, entries = {}, []
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
                rater_ix.setdefault(r, len(rater_ix))
                entries.append((rater_ix[r], c, float(s["score"])))
    nR, nC = len(rater_ix), len(col_prompt)
    G = np.full((nR, nC), np.nan)
    for i, c, v in entries:
        G[i, c] = v
    print(f"raters {nR}  columns {nC}  prompts {len(prompts)}")

    Gc = G - np.nanmean(G, axis=0, keepdims=True)
    _, s, vt = np.linalg.svd(np.nan_to_num(Gc), full_matrices=False)
    axis = vt[0]
    print(f"  bloc axis carries {s[0]**2/(s**2).sum():.3%} of singular mass")

    rng = np.random.default_rng(20260727)
    names = list(RULES) + ["conflict_aware"]
    stat = {nm: {"all_hit": [], "all_n": [], "con_hit": [], "con_n": [], "con_share": []}
            for nm in names}

    for pid in range(len(prompts)):
        cols = np.array(cols_of[pid])
        who = np.where(~np.isnan(G[:, cols]).all(axis=1))[0]
        if len(who) < 10:
            continue
        other = np.ones(nC, dtype=bool); other[cols] = False
        coord = np.nan_to_num(Gc[np.ix_(who, np.where(other)[0])]) @ axis[other]
        perm = rng.permutation(len(who))
        train, test = who[perm[: len(who)//2]], who[perm[len(who)//2:]]
        ctr, cte = coord[perm[: len(who)//2]], coord[perm[len(who)//2:]]
        if len(train) < 4 or len(test) < 4:
            continue
        thr_c = float(np.median(ctr))
        A, B = train[ctr >= thr_c], train[ctr < thr_c]
        if min(len(A), len(B)) < 2:
            continue

        M = G[np.ix_(train, cols)]
        cores = {nm: [j for j, _ in make_core(M, nm, a.k)] for nm in RULES}
        cores["conflict_aware"] = conflict_aware(M, a.k)

        def d_of(rows_sel, core):
            out = {}
            for j in core:
                v = G[np.ix_(rows_sel, [cols[j]])].ravel(); v = v[~np.isnan(v)]
                out[j] = 1 if (v.size == 0 or v.mean() >= 0) else -1
            return out

        for nm, core in cores.items():
            dA, dB = d_of(A, core), d_of(B, core)
            contested = [j for j in core if dA[j] != dB[j]]
            stat[nm]["con_share"].append(len(contested) / max(len(core), 1))
            ah = an = ch = cn = 0
            for t, c in zip(test, cte):
                assigned = dA if c >= thr_c else dB
                for j in core:
                    v = G[t, cols[j]]
                    if np.isnan(v) or v == 0:
                        continue
                    own = 1 if v > 0 else -1
                    hit = int(assigned[j] == own)
                    an += 1; ah += hit
                    if j in contested:
                        cn += 1; ch += hit
            if an:
                stat[nm]["all_hit"].append(ah); stat[nm]["all_n"].append(an)
            if cn:
                stat[nm]["con_hit"].append(ch); stat[nm]["con_n"].append(cn)

    out = {"profile_axis_singular_share": float(s[0]**2/(s**2).sum())}
    print(f"\n{'rule':16s} {'contested%':>11} {'acc ALL':>9} {'acc CONTESTED':>15} "
          f"{'95% CI':>20} {'n':>8}")
    for nm in names:
        d = stat[nm]
        if not d["con_n"]:
            continue
        share = float(np.mean(d["con_share"]))
        acc_all = sum(d["all_hit"]) / max(sum(d["all_n"]), 1)
        ch, cn = np.array(d["con_hit"]), np.array(d["con_n"])
        acc_con = ch.sum() / max(cn.sum(), 1)
        bs = np.empty(a.boot)
        for i in range(a.boot):
            k = rng.integers(0, len(ch), size=len(ch))
            bs[i] = ch[k].sum() / max(cn[k].sum(), 1)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        beats = "above chance" if lo > 0.5 else "AT CHANCE" if hi > 0.5 else "below chance"
        out[nm] = {"contested_share": share, "accuracy_all": float(acc_all),
                   "accuracy_contested": float(acc_con), "ci": [float(lo), float(hi)],
                   "contested_decisions": int(cn.sum()), "verdict": beats}
        print(f"{nm:16s} {share:>10.1%} {acc_all:>9.4f} {acc_con:>15.4f} "
              f"{f'[{lo:.4f},{hi:.4f}]':>20} {int(cn.sum()):>8,}  {beats}")

    ca = out.get("conflict_aware")
    if ca:
        infl = ca["accuracy_all"] - ca["accuracy_contested"]
        print(f"\n  conflict_aware: routing has something to decide on only "
              f"{ca['contested_share']:.1%} of core items")
        print(f"  inflation from free agreement: {infl:+.4f} "
              f"({ca['accuracy_all']:.4f} overall vs {ca['accuracy_contested']:.4f} where it matters)")
        out["conclusion"] = (
            "ROUTING IS REAL: on contested items the learned router beats chance, so "
            "r17's conditional gain is not an artifact of free agreement."
            if ca["verdict"] == "above chance" else
            "ROUTING IS AT CHANCE WHERE IT MATTERS: r17's headline routing accuracy "
            "came from items both blocs sign the same way. The conditional gain in "
            "r17 needs re-examination -- it cannot be coming from correct routing.")
        print(f"  -> {out['conclusion']}")
    Path(_RES).mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
