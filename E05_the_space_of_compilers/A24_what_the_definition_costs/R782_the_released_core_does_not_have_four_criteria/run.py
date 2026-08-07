#!/usr/bin/env python3
"""R782 · the released core does not have four criteria, and every filter here is exact-match.

CHECK #384 went looking for R781's "baseline-conditional zone" and found the population broken three
times over: a NAME regex that misses `generic`; a hand-patched RECONSTRUCTION (`POOL[0:4]`) standing
in for a scored arm that was on disk; and my replacement filter, `k == 4 on every prompt`, which
excludes `coval_core` -- the released core -- because it is k=4 on 925 prompts, k=3 on 42, k=2 on 1.

ESTIMAND        E1 per-arm size DISTRIBUTION from the object · E1b core-file vs sat-file agreement ·
                E2 `POOL[0:4]` vs `sat_generic.npz`, R604's question · E3 the three filters'
                disagreement set · E4 R781's shape over the corrected population
IDENTIFICATION  E1/E1b/E3 exact (counting); E2 exact for identity, paired+MDE for resolution;
                E4 inherits R781's n_eff = 1.1, so q is reported as "fraction of a 0.043 band beaten"
DERIVED FIRST   D1 an exact-match filter on a ragged object excludes it · D2 the arm-side permutation
                null is void for a paired mean (ledger 1125) -- THIS ROUND DOES NOT BUILD IT, replica
                pairs play the negative role · D3 a sub-MDE difference cannot move a published verdict
WORLDS          A aliases · B different objects below resolution · C different and resolvable
CONTROLS        OBJECT · PLACEBO · REPLICA (R766's within-pass pair) · POSITIVE (swept, band computed)
                · g=0 · SHAM (ingredient ABSENT: a real set misaligned, not a destroyed comparator)
"""
import collections
import itertools
import json
import math
import pathlib
import re
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls                 # noqa: E402
from report import verdict                                    # noqa: E402

RES = ROOT / "corebench/results"
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
NBOOT = 1200
SEED = 31337
SKIP = re.compile(r"_08b|_ctlS|_2b[AB]|^transport_")


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


def main():
    targets, _ = load_targets()
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and len(targets[p]) >= 2})
    P = len(pids)
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]
    out = {"n_prompts": P}

    def a2(Y):
        o = np.zeros(P)
        for a in range(P):
            s = np.sign(Y[a][[i for i, _ in PR]] - Y[a][[j for _, j in PR]])
            o[a] = np.mean([(s == h).mean() for h in HC[a]])
        return o

    def yvec(S):
        return np.array([[sum(S[p].get((i, x), 0.0) for i in sorted({i for i, _ in S[p]}))
                          for x in L] for p in pids])

    def cell(d, use_mde=True):
        n = len(d)
        ib = np.random.default_rng(SEED).integers(0, n, (NBOOT, n))
        bs = d[ib].mean(axis=1)
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        eff = float(d.mean())
        sd = float(d.std(ddof=1))
        mde = ZEFF * sd / math.sqrt(n) if sd > 0 else 0.0
        return {"n": n, "eff": eff, "lo": lo, "hi": hi, "mde": mde,
                "verdict": verdict(eff, lo, hi, mde if use_mde else None)}

    # ================= OBJECT CHECK ===============================================================
    print("  OBJECT CHECK")
    ARMS = {}
    for p in sorted(RES.glob("sat_*.npz")):
        t = p.stem[4:]
        if SKIP.search(t):
            continue
        try:
            S = load_sat(p)
        except Exception:
            continue
        if set(pids) <= set(S):
            ARMS[t] = S
    have = (RES / "sat_generic.npz").is_file() and (RES / "sat_genericpool16.npz").is_file()
    print(f"     prompts {P}   home-judge arms with full coverage {len(ARMS)}   "
          f"both comparators on disk: {have}")
    if not have or P == 0 or len(ARMS) == 0:
        print("  UNRUNNABLE: a comparator or the census is absent. Exit 2, never 0.")
        return 2

    # ================= E1 · the size DISTRIBUTION, from the object =================================
    print("\n  E1 - REALISED CRITERION-SET SIZE PER PROMPT, READ FROM THE SAT FILE")
    size = {}
    for t, S in ARMS.items():
        c = collections.Counter(len({i for i, _ in S[p]}) for p in pids)
        size[t] = {str(k): v for k, v in sorted(c.items())}
    ragged = {t: d for t, d in size.items() if len(d) > 1}
    print(f"     arms censused {len(size)}   RAGGED (size varies across prompts) {len(ragged)}")
    for t in sorted(ragged, key=lambda t: -sum(v for k, v in ragged[t].items() if k != "4")):
        d = ragged[t]
        off = sum(v for k, v in d.items() if k != max(d, key=lambda k: d[k]))
        print(f"     {t:<26}{str(d):<34} off-modal {off:>4} of {P}")
    out["size"] = size
    out["ragged"] = sorted(ragged)

    # E1b · does the core FILE agree with the sat FILE?
    print("\n  E1b - CORE FILE vs SAT FILE on set size")
    agree, disagree, nofile = [], [], []
    for t in sorted(ARMS):
        f = RES / f"core_{t}.json"
        if not f.is_file():
            nofile.append(t)
            continue
        try:
            d = json.loads(f.read_text())
        except Exception:
            nofile.append(t)
            continue
        if not isinstance(d, dict):
            nofile.append(t)
            continue
        cf = collections.Counter(len(v) for p, v in d.items() if p in set(pids))
        sf = collections.Counter(int(k) for k, v in size[t].items() for _ in range(v))
        (agree if cf == sf else disagree).append(t)
    print(f"     agree {len(agree)}   DISAGREE {len(disagree)} -> {disagree}")
    print(f"     no readable core file {len(nofile)} -> {nofile}")
    out["corefile"] = {"agree": agree, "disagree": disagree, "nofile": nofile}

    # ================= E2 · R604's question ========================================================
    print("\n  E2 - `POOL[0:4]` vs `sat_generic.npz`   (R604 registered this UNVERIFIED)")
    POOL = ARMS["genericpool16"]
    idx = sorted({i for i, _ in POOL[pids[0]]})
    Yp = np.array([[sum(POOL[p].get((i, x), 0.0) for i in idx[:4]) for x in L] for p in pids])
    Yg = yvec(ARMS["generic"])
    same = bool(np.array_equal(Yp, Yg))
    A, B = a2(Yp), a2(Yg)
    c = cell(A - B)
    print(f"     raw satisfaction arrays identical: {same}   max |dY| {np.abs(Yp - Yg).max():.6f}")
    print(f"     A2  POOL[0:4] {A.mean():.6f}   generic {B.mean():.6f}")
    print(f"     paired difference {c['eff']:+.6f}  [{c['lo']:+.6f}, {c['hi']:+.6f}]  "
          f"MDE {c['mde']:.6f}  {c['verdict']}")
    print(f"     per-prompt A2 differs on {int((A != B).sum())} of {P} prompts, max "
          f"|diff| {np.abs(A - B).max():.4f}")
    out["e2"] = {"identical": same, "max_dY": float(np.abs(Yp - Yg).max()),
                 "a2_pool": float(A.mean()), "a2_generic": float(B.mean()),
                 "prompts_differing": int((A != B).sum()), **c}

    # ================= CONTROLS ====================================================================
    print("\n  CONTROLS")
    plac = cell(A - A, use_mde=False)
    print(f"     PLACEBO    an arm against itself: {plac['eff']:.6f}  "
          f"{'PASS' if plac['eff'] == 0.0 else 'FAIL'}")
    g0 = cell(a2(yvec(ARMS["generic"])) - B, use_mde=False)
    print(f"     g=0        the same file scored twice: {g0['eff']:.6f}  "
          f"{'PASS' if g0['eff'] == 0.0 else 'FAIL'}  and must NOT resolve: "
          f"{g0['verdict']}")
    rep = None
    if "topw_k4_detA" in ARMS:
        rep = cell(a2(yvec(ARMS["topw_k4"])) - a2(yvec(ARMS["topw_k4_detA"])), use_mde=False)
        print(f"     REPLICA    topw_k4 vs topw_k4_detA (R766: within-pass replicas): "
              f"{rep['eff']:.6f}  {'PASS' if abs(rep['eff']) < 1e-12 else 'FAIL'}")
        print(f"                (this is the NEGATIVE's job; the arm-side permutation null is VOID "
              f"by D2 and is not built)")
    # SHAM -- ingredient ABSENT: a real criterion set, misaligned to prompts, not a destroyed class
    rng = np.random.default_rng(SEED)
    perm = rng.permutation(P)
    sham = cell(a2(Yg[perm]) - B)
    print(f"     SHAM       generic's own sets, misaligned to prompts: {sham['eff']:+.6f}  "
          f"[{sham['lo']:+.6f}, {sham['hi']:+.6f}]  {sham['verdict']}")
    dose, okp = {}, True
    for g in (0.0, 0.5, 1.0, 4.0):
        shift = g * c["mde"] if c["mde"] > 0 else g * 0.01
        d = (A + shift) - B
        cc = cell(d)
        dose[str(g)] = cc
        print(f"     POSITIVE   plant {g:>4.1f} x MDE   eff {cc['eff']:+.6f}   {cc['verdict']}")
        if g == 0.0 and cc["verdict"] != "UNRESOLVED":
            okp = False
        if g == 4.0 and not cc["verdict"].startswith("BEATS"):
            okp = False
    print(f"                band COMPUTED: floor at g=0 {dose['0.0']['eff']:+.6f} UNRESOLVED, "
          f"ceiling at 4x {dose['4.0']['eff']:+.6f}   POSITIVE {'PASS' if okp else 'FAIL'}")
    gate = plac["eff"] == 0.0 and g0["eff"] == 0.0 and okp and (rep is None or abs(rep["eff"]) < 1e-12)
    out["controls"] = {"placebo": plac["eff"], "g0": g0["eff"], "g0_verdict": g0["verdict"],
                       "replica": rep, "sham": sham, "dose": dose, "positive": okp, "gate": gate}

    # ================= E3 · the three filters ======================================================
    print("\n  E3 - THREE POPULATION FILTERS, SIDE BY SIDE")
    f_name = {t for t in ARMS if re.search(r"_k4(_|$)", t)}
    f_strict = {t for t in ARMS if set(size[t]) == {"4"}}
    f_major = {t for t in ARMS if int(max(size[t], key=lambda k: size[t][k])) == 4}
    print(f"     name regex `_k4(_|$)`        {len(f_name):>3}")
    print(f"     strict  k == 4 every prompt  {len(f_strict):>3}")
    print(f"     modal   k == 4 most prompts  {len(f_major):>3}")
    print(f"     modal \\ name    {sorted(f_major - f_name)}")
    print(f"     modal \\ strict  {sorted(f_major - f_strict)}")
    print(f"     name \\ modal    {sorted(f_name - f_major)}")
    out["filters"] = {"name": sorted(f_name), "strict": sorted(f_strict), "modal": sorted(f_major),
                      "modal_minus_name": sorted(f_major - f_name),
                      "modal_minus_strict": sorted(f_major - f_strict),
                      "name_minus_modal": sorted(f_name - f_major)}

    # ================= E4 · R781's shape over the corrected population =============================
    print("\n  E4 - R781's SHAPE OVER THE MODAL-k=4 POPULATION")
    print("     ⚠ n_eff = 1.1 (R781): q is the fraction of a 0.043-wide band beaten, NOT a "
          "probability")
    SUB = list(itertools.combinations(range(len(idx)), 4))
    T = np.zeros((P, len(idx), 4))
    for a, p in enumerate(pids):
        for bi, i in enumerate(idx):
            for c_, x in enumerate(L):
                T[a, bi, c_] = POOL[p].get((i, x), 0.0)
    REF = np.zeros((len(SUB), P))
    for si, s in enumerate(SUB):
        REF[si] = a2(T[:, list(s), :].sum(axis=1))
    qs, newly = {}, sorted(f_major - f_name - {"generic"})
    for t in sorted(f_major):
        v = a2(yvec(ARMS[t]))
        d = v[None, :] - REF
        keep = ~np.all(np.abs(d) < 1e-12, axis=1)
        m = d[keep].mean(axis=1)
        mde = ZEFF * d[keep].std(axis=1, ddof=1) / math.sqrt(P)
        qs[t] = {"a2": float(v.mean()), "q": float((m > 0).mean()),
                 "q_res": float(((m > 0) & (np.abs(m) >= mde)).mean()),
                 "self_excluded": int((~keep).sum()), "new_in_R782": t in newly}
    print(f"     {'arm':<26}{'A2':>9}{'q':>9}{'q_res':>9}   ")
    for t, r in sorted(qs.items(), key=lambda kv: -kv[1]["a2"]):
        flag = "  <- ABSENT from R781" if r["new_in_R782"] else ""
        print(f"     {t:<26}{r['a2']:>9.4f}{r['q']:>9.4f}{r['q_res']:>9.4f}{flag}")
    qv = np.array([r["q"] for r in qs.values()])
    mid = float(((qv >= 0.35) & (qv <= 0.65)).mean())
    ext = float(((qv < 0.10) | (qv > 0.90)).mean())
    print(f"     shape over {len(qv)} arms: middle band {mid:.4f}   extreme {ext:.4f}   "
          f"(R781 on 20 arms: 0.0000 / 1.0000)")
    out["e4"] = {"q": qs, "middle": mid, "extreme": ext, "n_arms": len(qv), "newly_included": newly}

    # ================= WORLD =======================================================================
    if not gate:
        world = "UNVERIFIED - a control did not fire. Never OVERTURNED, never CONFIRMED."
    elif same:
        world = "A - ALIASES: the two names denote one object"
    elif c["verdict"] == "UNRESOLVED" or abs(c["eff"]) < c["mde"]:
        world = (f"B - DIFFERENT OBJECTS, BELOW RESOLUTION: arrays differ (max |dY| "
                 f"{np.abs(Yp - Yg).max():.4f}) but the A2 difference {c['eff']:+.6f} sits inside its "
                 f"MDE {c['mde']:.6f}; the pages must name which arm they mean, and no published "
                 f"verdict moves")
    else:
        world = (f"C - DIFFERENT AND RESOLVABLE: {c['eff']:+.6f} against MDE {c['mde']:.6f}; every "
                 f"②-verdict computed against the other comparator is suspect")
    print(f"\n  WORLD {world}")
    out["world"] = world
    out["tree_sha"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip()
    d = pathlib.Path(__file__).resolve().parent / "results"
    d.mkdir(exist_ok=True)
    (d / "size_and_comparator.json").write_text(json.dumps(out, indent=2, default=_plain))
    print("  artifact -> size_and_comparator.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
