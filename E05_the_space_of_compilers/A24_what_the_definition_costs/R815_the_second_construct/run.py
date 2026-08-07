#!/usr/bin/env python3
"""R815 · the second construct — does the definition survive changing which human question is asked?

R814 closed by calling the next step a WRITING decision, on the ground that the release ships one
judgement per (annotator, prompt) pair. CHECK #417 found 111 repeated pairs — and, behind that, three
`ranking_blocks` keys where this arc has always used one: `world` (18,384), `personal` (4,901),
`unacceptable` (4,901). 321 prompts carry both `world` and `personal`, and where the SAME annotator
answered BOTH on the SAME prompt the rankings differ in 2,374 of 4,901 cases — 48.4%.

ESTIMAND        E1 every arm on `personal` · E2 ⭐ the paired world−personal difference · E3 ⭐ the
                ordering's rank correlation · E4 the committed margins under the second target
IDENTIFICATION  on 321 prompts; the MDE is computed and reported BEFORE any null is interpreted
DERIVED FIRST   D1 an arm built from `personal` must top the `personal` table · D2 an arm against
                itself is 0 · D3 the 321 are NOT a random third — they are where the second question
                was asked, so world-target numbers are reported on both populations · D4 the 48.4%
                is a fact about annotators and bounds the targets' difference without predicting
                which arms move
WORLDS          A target-invariant · B target-dependent · C underpowered — B checked FIRST
CONTROLS        OBJECT · PLACEBO · POSITIVE with a g=0 check · NEGATIVE (block labels shuffled) ·
                NOISE FLOOR · MDE
"""
import hashlib
import itertools
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, yvec, cls                                  # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
ZEFF = 2.801585
ARMS = ["coval_core", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1", "topw_k4",
        "genericpool16", "random_k4_s0", "gen_sham", "full"]


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def bh(pv, q=0.05):
    pv = np.asarray(pv, float)
    m = len(pv)
    order = np.argsort(pv)
    kmax = 0
    for r, i in enumerate(order, start=1):
        if pv[i] <= q * r / m:
            kmax = r
    keep = np.zeros(m, bool)
    keep[order[:kmax]] = True
    return keep


def parse_ranking(s):
    sc = {}
    for lvl, grp in enumerate(s.split(">")):
        for tok in grp.split("="):
            tok = tok.strip()
            if tok in "ABCD":
                sc[tok] = -lvl
    return [sc[c] for c in "ABCD"] if len(sc) == 4 else None


def modal(hs):
    best, bc = None, -1
    for c in {tuple(h) for h in hs}:
        n = sum(1 for h in hs if tuple(h) == c)
        if n > bc:
            best, bc = c, n
    return np.array(best)


def main():
    out = {"instrument_unit": "a (prompt, annotator) judgement", "claim_unit": "an ARM x a TARGET"}
    W, P = {}, {}
    for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        pid = r["prompt_id"]
        for a in r["metadata"].get("assessments", []):
            b = a.get("ranking_blocks") or {}
            for key, store in (("world", W), ("personal", P)):
                for e in b.get(key) or []:
                    y = parse_ranking(e.get("ranking") or "")
                    if y:
                        store.setdefault(pid, []).append(np.array(cls(np.array(y, float))))
    S = {a: load_sat(RES / f"sat_{a}.npz") for a in ARMS}
    allp = sorted(set.intersection(*(set(v) for v in S.values())) & set(W))
    pids968 = [p for p in allp if len(W[p]) >= 2]
    BOTH = [p for p in pids968 if p in P and len(P[p]) >= 2]
    print(f"  POPULATION  world-only: {len(pids968)} prompts · carrying BOTH blocks with >=2 "
          f"annotators each: {len(BOTH)}")
    if len(BOTH) < 250:
        print("  UNVERIFIED: fewer than 250 prompts carry both blocks. Exit 2.")
        return 2
    CL = {a: {p: np.array(cls(yvec(S[a][p], sorted({i for i, _ in S[a][p]})))) for p in pids968}
          for a in ARMS}

    def a2(cl, tgt, ps):
        return np.array([float((np.array(tgt[p]) == cl[p]).mean()) for p in ps])

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK")
    cc = float(a2(CL["coval_core"], W, pids968).mean())
    ok = abs(cc - 0.5664774811929549) < 1e-9
    print(f"     `coval_core` on `world`, all {len(pids968)} prompts: {cc:.10f} vs committed "
          f"0.5664774812   {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: the pipeline is not anchored to the record. Exit 2, never 0.")
        return 2
    out["object"] = {"coval_core_world_968": cc, "n968": len(pids968), "nboth": len(BOTH)}

    # ================= E1/E2 =====================================================================
    print(f"\n  E1/E2 - EVERY ARM ON BOTH TARGETS, SAME {len(BOTH)} PROMPTS")
    print(f"     ⚠ the header first read '321 prompts'. 321 is the count with >=1 annotator in each")
    print(f"     block; the POPULATION here requires >=2 in each and is {len(BOTH)}. The label was")
    print(f"     stale, the computation was not — `BOTH` was built with >=2 throughout.")
    print(f"     ⚠ D3: these {len(BOTH)} are NOT a random third — they are where the second question")
    print(f"     was asked. The world column is therefore given on BOTH populations.")
    rng = np.random.default_rng(1234)
    idx = rng.integers(0, len(BOTH), (NBOOT, len(BOTH)))
    rows, pv = [], []
    for a in ARMS:
        w968 = float(a2(CL[a], W, pids968).mean())
        vw, vp = a2(CL[a], W, BOTH), a2(CL[a], P, BOTH)
        d = vw - vp
        bs = d[idx].mean(axis=1)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        rows.append({"arm": a, "world968": w968, "world321": float(vw.mean()),
                     "personal321": float(vp.mean()), "diff": float(d.mean()),
                     "lo": float(lo), "hi": float(hi)})
        pv.append(float(2 * min((bs <= 0).mean(), (bs >= 0).mean())))
    keep = bh(pv)
    print(f"     {'arm':<16}{'world(968)':>11}{'world(sub)':>11}{'personal':>10}"
          f"{'world-personal':>26}")
    for r, k in zip(rows, keep):
        r["bh"] = bool(k)
        print(f"     {r['arm']:<16}{r['world968']:>11.4f}{r['world321']:>11.4f}"
              f"{r['personal321']:>10.4f}   {r['diff']:+.4f} [{r['lo']:+.4f}, {r['hi']:+.4f}]"
              f"  {'BH keep' if k else 'BH drop'}")
    out["e1"] = rows

    # ================= E3 · the ordering =========================================================
    print("\n  E3 - THE ORDERING UNDER EACH TARGET")
    ow = [r["arm"] for r in sorted(rows, key=lambda r: -r["world321"])]
    op = [r["arm"] for r in sorted(rows, key=lambda r: -r["personal321"])]
    rw = {a: i for i, a in enumerate(ow)}
    rp = {a: i for i, a in enumerate(op)}
    x = np.array([rw[a] for a in ARMS], float)
    y = np.array([rp[a] for a in ARMS], float)
    sp = float(np.corrcoef(x, y)[0, 1])
    conc = sum(1 for i, j in itertools.combinations(range(len(ARMS)), 2)
               if (x[i] - x[j]) * (y[i] - y[j]) > 0)
    tot = len(ARMS) * (len(ARMS) - 1) // 2
    tau = (2 * conc - tot) / tot
    print(f"     world   : {' > '.join(ow)}")
    print(f"     personal: {' > '.join(op)}")
    print(f"     ⭐ Spearman {sp:.4f}   Kendall tau {tau:.4f}   concordant pairs {conc}/{tot}")
    out["e3"] = {"world_order": ow, "personal_order": op, "spearman": sp, "tau": tau,
                 "concordant": conc, "pairs": tot}

    # ================= E4 · the committed margins ================================================
    print("\n  E4 - THE ARC'S COMMITTED MARGINS UNDER THE SECOND TARGET")
    def marg(a, b, tgt):
        d = a2(CL[a], tgt, BOTH) - a2(CL[b], tgt, BOTH)
        bs = d[idx].mean(axis=1)
        return float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
    MARG = [("oracle_k4_fit1", "genericpool16", "R805 fitted − blind pool"),
            ("coval_core", "genericpool16", "R805 released core − blind pool"),
            ("topw_k4", "random_k4_s0", "R811 rule effect (k=4)"),
            ("coval_core", "gen_sham", "the sham gap")]
    flips = []
    e4 = []
    for a, b, lab in MARG:
        mw = marg(a, b, W)
        mp = marg(a, b, P)
        fl = (mw[0] > 0) != (mp[0] > 0)
        flips.append(fl)
        e4.append({"label": lab, "world": mw, "personal": mp, "flips": fl})
        print(f"     {lab:<34} world {mw[0]:+.4f} [{mw[1]:+.4f},{mw[2]:+.4f}]   "
              f"personal {mp[0]:+.4f} [{mp[1]:+.4f},{mp[2]:+.4f}]   "
              f"{'⛔ SIGN FLIPS' if fl else 'same sign'}")
    out["e4"] = e4

    # ================= MDE =======================================================================
    smallest = min(abs(m["world"][0]) for m in e4)
    dv = a2(CL["coval_core"], W, BOTH) - a2(CL["genericpool16"], W, BOTH)
    MDE = ZEFF * dv.std(ddof=1) / math.sqrt(len(BOTH))
    print(f"\n  MDE for this paired design at n={len(BOTH)}: {MDE:.4f}   smallest margin under "
          f"test {smallest:.4f}   underpowered: {MDE > smallest}")
    out["mde"] = {"mde": float(MDE), "smallest_margin": float(smallest),
                  "underpowered": bool(MDE > smallest)}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    plac = max(abs(float((a2(CL[a], t, BOTH) - a2(CL[a], t, BOTH)).mean()))
               for a in ARMS for t in (W, P))
    plac_ok = plac == 0.0
    print(f"     PLACEBO   an arm minus itself on either target: {plac:.1e}   "
          f"{'PASS - exactly 0' if plac_ok else 'FAIL'}")
    MP = {p: modal(P[p]) for p in BOTH}
    MW = {p: modal(W[p]) for p in BOTH}
    sp_on_p = float(a2(MP, P, BOTH).mean())
    sw_on_p = float(a2(MW, P, BOTH).mean())
    best_real_p = max(r["personal321"] for r in rows)
    pos_ok = sp_on_p > best_real_p
    g0_ok = sw_on_p < sp_on_p
    print(f"     POSITIVE  an arm built FROM `personal`'s modal class scores {sp_on_p:.4f} on "
          f"`personal`; best real arm {best_real_p:.4f}   {'PASS' if pos_ok else 'FAIL'}")
    print(f"     g=0 CHECK the same construction from `world` scores {sw_on_p:.4f} on `personal` — "
          f"lower than {sp_on_p:.4f}: {g0_ok}   "
          f"{'PASS - the control can fail' if g0_ok else 'FAIL'}")
    rngn = np.random.default_rng(808)
    nulls = []
    for _ in range(200):
        Wn, Pn = {}, {}
        for p in BOTH:
            w, pe = list(W[p]), list(P[p])
            n = min(len(w), len(pe))
            a_, b_ = [], []
            for i in range(n):
                if rngn.random() < 0.5:
                    a_.append(w[i]); b_.append(pe[i])
                else:
                    a_.append(pe[i]); b_.append(w[i])
            Wn[p], Pn[p] = a_, b_
        nulls.append(float((a2(CL["coval_core"], Wn, BOTH)
                            - a2(CL["coval_core"], Pn, BOTH)).mean()))
    nulls = np.array(nulls)
    real_d = next(r["diff"] for r in rows if r["arm"] == "coval_core")
    neg_ok = bool(np.percentile(nulls, 2.5) <= 0 <= np.percentile(nulls, 97.5))
    print(f"     NEGATIVE  block labels shuffled within each assessment, 200 draws: null "
          f"{nulls.mean():+.4f} [{np.percentile(nulls, 2.5):+.4f}, "
          f"{np.percentile(nulls, 97.5):+.4f}]   real {real_d:+.4f}   "
          f"{'PASS - null holds 0' if neg_ok else 'FAIL'}")
    rngh = np.random.default_rng(55)
    hs = []
    for _ in range(20):
        sub = [BOTH[i] for i in rngh.permutation(len(BOTH))[: len(BOTH) // 2]]
        hs.append(float((a2(CL["coval_core"], W, sub) - a2(CL["coval_core"], P, sub)).mean()))
    print(f"     NOISE FLOOR  20 half-splits of the {len(BOTH)} prompts: sd {np.std(hs):.4f}")
    gate = ok and plac_ok and pos_ok and g0_ok and neg_ok
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo": plac, "placebo_ok": plac_ok, "pos_personal": sp_on_p,
                       "world_arm_on_personal": sw_on_p, "positive_ok": pos_ok, "g0_ok": g0_ok,
                       "null_mean": float(nulls.mean()), "negative_ok": neg_ok,
                       "halfsplit_sd": float(np.std(hs)), "gate": gate}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif MDE > smallest:
        world = "C"
    elif sp < 0.9 or any(flips):
        world = "B"
    else:
        world = "A"
    print(f"     MDE {MDE:.4f} vs smallest margin {smallest:.4f}   Spearman {sp:.4f}   "
          f"margins flipping sign: {sum(flips)} of {len(flips)}  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/second_construct.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
