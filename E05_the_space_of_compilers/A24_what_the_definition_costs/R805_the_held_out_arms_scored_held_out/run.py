#!/usr/bin/env python3
"""R805 · the held-out arms, scored held-out — one matched parity split for every quantity.

CHECK #407 killed R804's NEXT as ill-posed (`select_core.py` selects PER PROMPT, so nothing
transfers across prompts) and found two real defects in the same place. R294's 41-arm census — the
table later rounds read — builds `HC[p]` from ALL annotators and publishes `oracle_k4_fit1 = 0.6142`
while half those annotators ARE the arm's fit set; R293 declared that restriction and implemented
it, R294 did not. And R804 scored a LEAKY arm against a HELD-OUT ceiling. This round puts floor,
arms and ceiling under ONE split: fit on parity 1, evaluate on parity 0.

ESTIMAND        E1 ⭐ the honest axis on parity-0 · E2 ⭐ every arm on parity-0 · E3 ⭐ the leak,
                two ways · E4 R804's headline, corrected
IDENTIFICATION  exact under the split; ⚠ E3(a) needs the honest-arm confound to be a leak estimate
DERIVED FIRST   D1 a parity-1 fit scores higher on parity-1 (POSITIVE, forced in sign only) ·
                D2 CEIL_HO <= CEIL_ATT or the code is wrong · D3 R295 showed the halves are not
                independent, so every leak number here is a LOWER bound · D4 an honest arm must
                show no all-vs-parity0 gap
WORLDS          A fitting survives · B collapses to the pool · C collapses below — A checked FIRST
CONTROLS        OBJECT (R293's committed 0.631353 / 0.625062) · PLACEBO (parity-0 tie rate, exact)
                · POSITIVE (D1, band at both ends) · NEGATIVE (cores against another prompt's
                humans) · CONFOUND (D4) · NOISE FLOOR
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
from score import load_sat, load_targets, yvec, cls                    # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R293 = ARC / "R293_does_the_definition_exclude_a_fitted_core/results/fitted_arms.json"
PR = list(itertools.combinations(range(4), 2))
ZEFF = 2.801585
NBOOT = 1200
FITTED_HELDOUT = ["oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"]
LEAKY = ["oracle_k4"]
HONEST = ["coval_core", "generic", "genericpool16", "topw_k4", "random_k4_s0", "gen_sham", "full"]
ARMS = LEAKY + FITTED_HELDOUT + HONEST
POOLNAME = "genericpool16"


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


def weak_orders():
    seen = {}
    for v in itertools.product(range(4), repeat=4):
        s = tuple(int(np.sign(v[i] - v[j])) for i, j in PR)
        seen.setdefault(s, v)
    return np.array(sorted(seen))


def main():
    out = {"instrument_unit": "a (prompt, annotator) judgement", "claim_unit": "an ARM"}
    W = weak_orders()
    targets, _ = load_targets()
    S = {}
    for a in ARMS:
        f = RES / f"sat_{a}.npz"
        if not f.is_file():
            print(f"  UNRUNNABLE: {f.name} missing. Exit 2.")
            return 2
        S[a] = load_sat(f)

    # ---- the split, and the prompts it costs ---------------------------------------------------
    cand = sorted(set.intersection(*[set(S[a]) for a in ARMS]) & set(targets))
    pids, dropped = [], 0
    for p in cand:
        n = len(targets[p])
        if sum(1 for i in range(n) if i % 2 == 0) >= 1 and sum(1 for i in range(n) if i % 2) >= 1:
            pids.append(p)
        else:
            dropped += 1
    P = len(pids)
    print(f"  POPULATION  {P} prompts with at least one annotator in EACH parity; "
          f"{dropped} dropped for an empty half (printed, never silent)")
    HALL = [np.array([cls(np.array(y, float)) for y, _ in targets[p]]) for p in pids]
    H0 = [np.array([cls(np.array(y, float)) for i, (y, _) in enumerate(targets[p]) if i % 2 == 0])
          for p in pids]
    H1 = [np.array([cls(np.array(y, float)) for i, (y, _) in enumerate(targets[p]) if i % 2 == 1])
          for p in pids]

    CL = {a: np.array([cls(yvec(S[a][p], sorted({i for i, _ in S[a][p]}))) for p in pids])
          for a in ARMS}

    def score(cl, H):
        return np.array([float((H[a] == cl[a]).mean()) for a in range(P)])

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK")
    r293 = json.loads(R293.read_text())
    o_ev = float(score(CL["oracle_k4"], H0).mean())
    o_fit = float(score(CL["oracle_k4"], H1).mean())
    core_all = float(score(CL["coval_core"], HALL).mean())
    ok = (abs(o_ev - r293["oracle_on_ev"]) < 1e-6 and abs(o_fit - r293["oracle_on_fit"]) < 1e-6
          and abs(core_all - 0.5664774811929549) < 1e-9)
    print(f"     leaky oracle on parity 0: {o_ev:.6f} vs R293's committed "
          f"{r293['oracle_on_ev']:.6f}")
    print(f"     leaky oracle on parity 1: {o_fit:.6f} vs R293's committed "
          f"{r293['oracle_on_fit']:.6f}")
    print(f"     `coval_core` on ALL annotators: {core_all:.10f} vs committed 0.5664774812")
    print(f"     {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: the record did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"oracle_on_ev": o_ev, "oracle_on_fit": o_fit, "coval_core_all": core_all,
                     "prompts": P, "dropped": dropped}

    # ================= E1 · the honest axis on parity-0 ==========================================
    print("\n  E1 - THE HONEST AXIS, EVERY END COMPUTED ON PARITY-0")
    text = {}
    for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        rs = r.get("responses") or []
        if len(rs) != 4:
            continue
        text[r["prompt_id"]] = [" ".join(str(m.get("content", "")) for m in (it.get("messages")
                                or []) if isinstance(m, dict)) for it in rs]
    CH = np.array([[len(t) for t in text[p]] for p in pids], float)
    fl = np.zeros((P, 6), int)
    for a in range(P):
        fl[a] = np.sign(CH[a][[u for u, _ in PR]] - CH[a][[w for _, w in PR]])
    FLOOR0 = float(np.mean([float((H0[a] == fl[a]).mean()) for a in range(P)]))
    att0 = np.zeros(P)
    ho0 = np.zeros(P)
    for a in range(P):
        att0[a] = ((H0[a][None, :, :] == W[:, None, :]).mean(axis=1)).mean(axis=1).max()
        best = ((H1[a][None, :, :] == W[:, None, :]).mean(axis=1)).mean(axis=1).argmax()
        ho0[a] = float((H0[a] == W[best]).mean())
    CEIL_ATT0 = float(att0.mean())
    CEIL_HO0 = float(ho0.mean())
    d2_ok = CEIL_HO0 <= CEIL_ATT0 + 1e-12
    print(f"     floor_p0    (characters, longer-is-better)                  {FLOOR0:.6f}")
    print(f"     ⭐ CEIL_HO_p0  (best weak order FITTED ON PARITY-1)           {CEIL_HO0:.6f}"
          f"   <- the SAME estimator class as the fitted arms")
    print(f"     CEIL_ATT_p0 (in-sample max on parity-0, an UPPER bound)     {CEIL_ATT0:.6f}")
    print(f"     D2 CEIL_HO <= CEIL_ATT: {d2_ok}   {'PASS' if d2_ok else 'FAIL - code is wrong'}")
    if not d2_ok:
        return 2
    out["e1"] = {"floor_p0": FLOOR0, "ceil_ho_p0": CEIL_HO0, "ceil_att_p0": CEIL_ATT0}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    const = np.zeros(6, int)
    plac = float(np.mean([float((H0[a] == const).mean()) for a in range(P)]))
    tie0 = float(np.mean([float((H0[a] == 0).mean()) for a in range(P)]))
    plac_ok = abs(plac - tie0) < 1e-12
    print(f"     PLACEBO   constant predictor on parity-0 {plac:.10f}   parity-0 tie rate "
          f"{tie0:.10f}   {'PASS - exact' if plac_ok else 'FAIL'}")
    print("     POSITIVE  D1 - a parity-1 fit must score higher on parity 1 than on parity 0")
    pos_rows = []
    for a in FITTED_HELDOUT:
        s0, s1 = float(score(CL[a], H0).mean()), float(score(CL[a], H1).mean())
        pos_rows.append((a, s0, s1, s1 > s0))
        print(f"        {a:<18} parity-1 (its OWN fit) {s1:.6f}  >  parity-0 {s0:.6f}   "
              f"{'PASS' if s1 > s0 else 'FAIL'}   band {plac:.4f} < t < {CEIL_ATT0:.4f}")
    pos_ok = all(r[3] for r in pos_rows)
    rngn = np.random.default_rng(4321)
    perm = rngn.permutation(P)
    neg = float(np.mean([float((H0[perm[a]] == CL["coval_core"][a]).mean()) for a in range(P)]))
    neg_ok = neg < float(score(CL["coval_core"], H0).mean())
    print(f"     NEGATIVE  each core scored against ANOTHER prompt's parity-0 humans: "
          f"{float(score(CL['coval_core'], H0).mean()):.6f} -> {neg:.6f}   "
          f"{'PASS' if neg_ok else 'FAIL'}")
    conf_a = float(score(CL["coval_core"], HALL).mean())
    conf_0 = float(score(CL["coval_core"], H0).mean())
    print(f"     CONFOUND  D4 - an HONEST arm (`coval_core`, no prompt labels) all vs parity-0: "
          f"{conf_a:.6f} vs {conf_0:.6f}   gap {conf_a - conf_0:+.6f}")
    rngf = np.random.default_rng(99)
    draws = []
    for _ in range(20):
        v = []
        for a in range(P):
            h = H0[a][rngf.permutation(len(H0[a]))[:max(1, len(H0[a]) // 2)]]
            v.append(float((h == CL["coval_core"][a]).mean()))
        draws.append(np.mean(v))
    NF = float(np.std(draws))
    print(f"     NOISE FLOOR  parity-0 split in half, 20 draws: sd {NF:.6f}")
    gate = ok and plac_ok and pos_ok and neg_ok
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo": plac, "tie0": tie0, "placebo_ok": plac_ok,
                       "positive": pos_rows, "positive_ok": pos_ok, "negative": neg,
                       "negative_ok": neg_ok, "confound_all": conf_a, "confound_p0": conf_0,
                       "noise_floor": NF, "gate": gate}

    # ================= E2 · every arm on parity-0 ================================================
    print("\n  E2 - EVERY ARM ON PARITY-0, AS A SHARE OF THE HONEST RANGE")
    rngb = np.random.default_rng(1234)
    idx = rngb.integers(0, P, size=(NBOOT, P))
    pool0 = score(CL[POOLNAME], H0)
    rows, pv = [], []
    for a in ARMS:
        v0, v1, va = score(CL[a], H0), score(CL[a], H1), score(CL[a], HALL)
        d = v0 - pool0
        bs = d[idx].mean(axis=1)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        pv.append(float(2 * min((bs <= 0).mean(), (bs >= 0).mean())))
        rows.append({"arm": a, "p0": float(v0.mean()), "p1": float(v1.mean()),
                     "all": float(va.mean()), "vs_pool": float(d.mean()),
                     "lo": float(lo), "hi": float(hi),
                     "share": float((v0.mean() - FLOOR0) / (CEIL_HO0 - FLOOR0)),
                     "kind": ("LEAKY" if a in LEAKY else
                              "held-out" if a in FITTED_HELDOUT else "honest")})
    keep = bh(pv)
    for r, kp in zip(rows, keep):
        r["bh"] = bool(kp)
    print(f"     {'arm':<18}{'kind':<10}{'parity-0':>10}{'parity-1':>10}{'ALL':>10}"
          f"{'vs pool (p0)':>26}{'share':>8}")
    for r in sorted(rows, key=lambda r: -r["p0"]):
        print(f"     {r['arm']:<18}{r['kind']:<10}{r['p0']:>10.4f}{r['p1']:>10.4f}"
              f"{r['all']:>10.4f}   {r['vs_pool']:+.4f} [{r['lo']:+.4f}, {r['hi']:+.4f}]"
              f"{100 * r['share']:>7.1f}%")
    print(f"     BH q=0.05 over {len(rows)} arm-vs-pool tests: {int(keep.sum())} survive, "
          f"{len(rows) - int(keep.sum())} do not (printed above, not hidden)")
    out["e2"] = {"rows": rows, "bh_survivors": int(keep.sum())}

    # ================= E3 · the leak =============================================================
    print("\n  E3 - THE LEAK, TWO WAYS")
    print("     (a) the contamination in R294's committed census: the SAME arm on ALL annotators "
          "minus the same arm on parity-0")
    leak_a = []
    for a in FITTED_HELDOUT + ["coval_core"]:
        d = score(CL[a], HALL) - score(CL[a], H0)
        bs = d[idx].mean(axis=1)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        leak_a.append({"arm": a, "gap": float(d.mean()), "lo": float(lo), "hi": float(hi),
                       "honest": a == "coval_core"})
        tag = "  <- HONEST arm: this is the D4 confound, not a leak" if a == "coval_core" else ""
        print(f"        {a:<18} {d.mean():+.6f} [{lo:+.6f}, {hi:+.6f}]{tag}")
    print("     (b) the price of the answer key: LEAKY `oracle_k4` minus held-out "
          "`oracle_k4_fit1`, both on parity-0")
    d = score(CL["oracle_k4"], H0) - score(CL["oracle_k4_fit1"], H0)
    bs = d[idx].mean(axis=1)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    print(f"        {d.mean():+.6f} [{lo:+.6f}, {hi:+.6f}]")
    print("     ⚠ D3: R295 measured that the fit1 advantage concentrates where the halves AGREE, "
          "so parity-0 is a PROXY for parity-1 and every number here is a LOWER BOUND on the leak.")
    out["e3"] = {"contamination": leak_a,
                 "answer_key_price": {"gap": float(d.mean()), "lo": float(lo), "hi": float(hi)}}

    # ================= E4 · R804's headline corrected ============================================
    print("\n  E4 - R804's HEADLINE, CORRECTED")
    r804 = json.loads((ARC / "R804_the_human_ceiling_is_not_a_ceiling/results/ceiling.json")
                      .read_text())
    pub = 100 * (0.6283 - r804["e2"]["floor"]) / (r804["e5"]["ceil_ho"] - r804["e2"]["floor"])
    best_ho = max((r for r in rows if r["kind"] == "held-out"), key=lambda r: r["p0"])
    print(f"     as R804 published : LEAKY `oracle_k4` 0.6283 against a HELD-OUT ceiling "
          f"-> {pub:.1f}% of the generalising range")
    print(f"     matched here      : held-out `{best_ho['arm']}` {best_ho['p0']:.4f} against "
          f"CEIL_HO_p0 {CEIL_HO0:.4f} -> {100 * best_ho['share']:.1f}%")
    ch = next(r for r in rows if r["arm"] == "coval_core")
    print(f"     the released core : `coval_core` {ch['p0']:.4f} -> {100 * ch['share']:.1f}%")
    out["e4"] = {"published": pub, "matched_arm": best_ho["arm"],
                 "matched_share": best_ho["share"], "coval_core_share": ch["share"]}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    f1 = next(r for r in rows if r["arm"] == "oracle_k4_fit1")
    if not gate:
        world = "UNVERIFIED"
    elif f1["lo"] > 0:
        world = "A"
    elif f1["lo"] <= 0 <= f1["hi"]:
        world = "B"
    elif f1["hi"] < 0:
        world = "C"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   oracle_k4_fit1 - {POOLNAME} on parity-0 = {f1['vs_pool']:+.4f} "
          f"[{f1['lo']:+.4f}, {f1['hi']:+.4f}]  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/heldout.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
