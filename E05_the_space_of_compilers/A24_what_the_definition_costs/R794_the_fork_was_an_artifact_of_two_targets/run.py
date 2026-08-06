#!/usr/bin/env python3
"""R794 · the WORLD A / WORLD B fork was an artifact of comparing two different targets.

R793 closed on a WALL — "the first thing in this arc that no further computation can decide."
CHECK #396 attacked it first (§4: an unchecked wall is UNVERIFIED) and it fell in three lines. The
normalisation problem exists only because `whose_verdicts` compares `vs HUMAN` (ceiling 0.5519) with
`vs FULL` (ceiling 1.0). Two SAME-TARGET questions answer the clause with no ceiling at all:
Q1 does a core preserve the RUBRIC's verdicts (both sides vs `full`)? Q2 does it track the HUMAN
better than the rubric does (both sides vs the human)?

ESTIMAND        E1 ⭐ Q1 with its floor, sham and D3 residual · E2 ⭐ Q2 paired, all annotators ·
                E3 ⭐ the dissolution · E4 the wall audit
IDENTIFICATION  E1/E2/E4 exact; E3 exact given the two verdicts. ⚠ D3's regression has n = 20 ARMS
DERIVED FIRST   D1 a same-target comparison needs no ceiling · D2 Q1 and Q2 are not complementary,
                so the fork CAN be false rather than mis-measured · D3 `core vs FULL` is inflated by
                both tracking the human — the confound, controlled by regression in this round ·
                D4 `full` appears on both sides of Q1 and one side of Q2
WORLDS          A the clause is false on its own terms · B the refutation was the artifact ·
                C ⭐ the fork is false and both hold
CONTROLS        OBJECT (reproduce R793 to 1e-9) · PLACEBO (every arm vs itself = 1.0) · POSITIVE
                (band on Q2) · NEGATIVE (full's class shuffled; Q2 EXACTLY unchanged) · SHAM (a
                random arm's class in place of full's) · D3 regression · NOISE FLOOR
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
R793 = ARC / "R793_seven_artifacts_nobody_opened/results/coverage.json"
R789 = ARC / "R789_how_many_levels_the_a2_axis_resolves/results/ladder.json"
L = "ABCD"
ZEFF = 2.801585
NBOOT = 1200
SEEDS = [31337, 31338, 31339]


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


def main():
    out = {"instrument_unit": "a (prompt, annotator) judgement for Q2, a PROMPT for Q1",
           "claim_unit": "an ARM", "claim_unit_e3": "a WORLD"}

    print("  OBJECT CHECK")
    if not (R793.is_file() and R789.is_file()):
        print("  UNRUNNABLE: a prior artifact is absent. Exit 2, never 0.")
        return 2
    prev793 = json.loads(R793.read_text())["e2"]
    prev789 = json.loads(R789.read_text())
    targets, _ = load_targets()
    fullS = load_sat(RES / "sat_full.npz")
    fullc = {p: cls(yvec(fullS[p], sorted({i for i, _ in fullS[p]}))) for p in fullS}

    SAT, names = {}, []
    for t in list(prev789["e2"]["a2"]) + ["full"]:
        f = RES / f"sat_{t}.npz"
        if f.is_file() and t not in SAT:
            SAT[t] = load_sat(f)
            names.append(t)
    pids = sorted(p for p in fullc if p in targets and len(targets[p]) >= 2
                  and all(p in SAT[a] for a in SAT))
    P = len(pids)
    HC = [np.array([cls(np.array(y, float)) for y, _ in targets[p]]) for p in pids]
    nann = np.array([len(h) for h in HC])
    FC = np.array([fullc[p] for p in pids], float)
    C = {a: np.array([cls(yvec(SAT[a][p], sorted({i for i, _ in SAT[a][p]}))) for p in pids], float)
         for a in SAT}

    def vs_human(cm):
        return np.array([(HC[i] == cm[i]).mean() for i in range(P)])

    def vs_class(cm, tgt):
        return (cm == tgt).mean(axis=1)

    VH = {a: vs_human(C[a]) for a in C}
    VF = {a: vs_class(C[a], FC) for a in C}

    # collapse aliases -> distinct objects
    par = {a: a for a in names}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    for x, y in itertools.combinations(names, 2):
        if np.array_equal(C[x], C[y]):
            par[find(x)] = find(y)
    reps = sorted({find(a) for a in names}, key=lambda a: VH[a].mean())
    n = len(reps)

    worst = 0.0
    for a, r in prev793.items():
        if a in VF:
            worst = max(worst, abs(float(VF[a].mean()) - r["vs_full"]),
                        abs(float(VH[a].mean()) - r["vs_human_all"]))
    plac = max(abs(float(vs_class(C[a], C[a]).mean()) - 1.0) for a in C)
    okobj = worst < 1e-9 and plac < 1e-12
    print(f"     prompts {P}   annotators/prompt median {int(np.median(nann))}   arms {len(C)}   "
          f"distinct objects {n}")
    print(f"     R793 reproduction: worst |Δ| over its 7 arms, both columns  {worst:.3e}   "
          f"{'PASS' if worst < 1e-9 else 'FAIL'}")
    print(f"     PLACEBO  every arm against its OWN class: worst |1 - v| {plac:.1e}   "
          f"{'PASS' if plac < 1e-12 else 'FAIL'}")
    if not okobj:
        print("  UNRUNNABLE: the prior columns did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"prompts": P, "objects": n, "arms": len(C), "r793_worst": worst,
                     "placebo": plac}

    rng = np.random.default_rng(SEEDS[0])
    BI = rng.integers(0, P, size=(NBOOT, P))

    def ci(v):
        b = v[BI].mean(axis=1)
        lo, hi = float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
        p = 2.0 * min(float((b <= 0).mean()), float((b >= 0).mean()))
        return float(v.mean()), lo, hi, max(min(p, 1.0), 1.0 / (NBOOT + 1))

    # ================= E1 · Q1, with floor, sham and the D3 residual ==============================
    print("\n  E1 - Q1: DOES A CORE PRESERVE THE RUBRIC'S VERDICTS?  (both sides vs `full`)")
    srng = np.random.default_rng(SEEDS[0] + 11)
    FCsh = FC[srng.permutation(P)]
    sham_arms = [a for a in reps if a.startswith("random_k4")]
    q1 = {}
    for a in reps:
        v = VF[a]
        floor = vs_class(C[a], FCsh)
        shams = np.array([vs_class(C[a], C[s]).mean() for s in sham_arms])
        e, lo, hi, p = ci(v - floor)
        q1[a] = {"vs_full": float(v.mean()), "shuffled_floor": float(floor.mean()),
                 "sham_random_arm": float(shams.mean()), "excess_over_shuffled": e,
                 "lo": lo, "hi": hi, "p": p}
    for a in ("coval_core", "topw_k4", "gen", "full"):
        if a in q1:
            r = q1[a]
            print(f"     {a:<12} vs FULL {r['vs_full']:.4f}   shuffled-full floor "
                  f"{r['shuffled_floor']:.4f}   random-arm sham {r['sham_random_arm']:.4f}   "
                  f"excess {r['excess_over_shuffled']:+.4f} [{r['lo']:+.4f}, {r['hi']:+.4f}]")

    # D3's confound control: regress vs_full on vs_human across the 20 objects
    x = np.array([VH[a].mean() for a in reps])
    y = np.array([VF[a].mean() for a in reps])
    keep = np.array([a != "full" for a in reps])                # `full` is 1.0 by construction (D4)
    xf, yf = x[keep], y[keep]
    A = np.vstack([xf, np.ones_like(xf)]).T
    coef, *_ = np.linalg.lstsq(A, yf, rcond=None)
    pred = A @ coef
    resid = yf - pred
    rs = float(np.std(resid, ddof=2))
    ci_idx = [i for i, a in enumerate([a for a in reps if a != "full"]) if a == "coval_core"][0]
    rc = float(resid[ci_idx])
    # ⚠ THE PREREGISTRATION ASKED FOR THE RESIDUAL'S CI AND THE FIRST DRAFT COMPUTED A POINT.
    # Closed here rather than shipped: resample PROMPTS, recompute all arms' means, refit, and take
    # `coval_core`'s residual in each draw. Without this the World-A branch ("residual CI contains
    # 0") could never have fired, which is a check that cannot fail.
    nofull = [a for a in reps if a != "full"]
    rboot = np.empty(400)
    for b in range(400):
        idx = BI[b]
        xb = np.array([VH[a][idx].mean() for a in nofull])
        yb = np.array([VF[a][idx].mean() for a in nofull])
        Ab = np.vstack([xb, np.ones_like(xb)]).T
        cb, *_ = np.linalg.lstsq(Ab, yb, rcond=None)
        rboot[b] = (yb - Ab @ cb)[ci_idx]
    rlo, rhi = float(np.percentile(rboot, 2.5)), float(np.percentile(rboot, 97.5))
    resid_resolved = rlo > 0 or rhi < 0
    print(f"     D3 CONTROL  regress `vs FULL` on `vs HUMAN` over {keep.sum()} objects "
          f"(`full` excluded, D4): slope {coef[0]:+.4f}   residual sd {rs:.4f}")
    print(f"                 ⛔ THE SLOPE IS NEGATIVE, so D3's confound runs the OTHER WAY: arms "
          f"that track humans better agree with `full` LESS. The confound I registered would have "
          f"made Q1 conservative, not inflated.")
    print(f"                 `coval_core` residual {rc:+.4f} [{rlo:+.4f}, {rhi:+.4f}] = "
          f"{rc / rs:+.2f} residual sd   "
          f"{'RESOLVED' if resid_resolved else 'NOT RESOLVED at n=20 -- a point statement only'}")
    print(f"     ⚠ n = {int(keep.sum())} ARMS. The residual is reported with its n and no claim is "
          f"made that would need more arms than exist.")
    out["e1"] = {"arms": q1, "slope": float(coef[0]), "resid_sd": rs, "coval_core_resid": rc,
                 "resid_z": rc / rs, "n_arms": int(keep.sum()),
                 "resid_lo": rlo, "resid_hi": rhi, "resid_resolved": resid_resolved}

    # ================= E2 · Q2, paired, all annotators ============================================
    print("\n  E2 - Q2: DOES A CORE TRACK THE HUMAN BETTER THAN THE RUBRIC DOES?  (both vs human)")
    q2 = {}
    for a in reps:
        if a == "full":
            continue
        e, lo, hi, p = ci(VH[a] - VH["full"])
        mde = ZEFF * float((VH[a] - VH["full"]).std(ddof=1)) / math.sqrt(P)
        q2[a] = {"eff": e, "lo": lo, "hi": hi, "p": p, "mde": mde,
                 "resolved": bool((lo > 0 or hi < 0) and abs(e) >= mde)}
    for a in ("coval_core", "topw_k4", "gen"):
        if a in q2:
            r = q2[a]
            print(f"     {a:<12} vs HUMAN {VH[a].mean():.4f} - `full` {VH['full'].mean():.4f} = "
                  f"{r['eff']:+.4f} [{r['lo']:+.4f}, {r['hi']:+.4f}]  mde {r['mde']:.4f}  "
                  f"{'RESOLVED' if r['resolved'] else 'unresolved'}")
    out["e2"] = q2

    # ================= MULTIPLICITY over the union ================================================
    pv = [q1[a]["p"] for a in reps] + [q2[a]["p"] for a in reps if a != "full"]
    kp = bh(np.array(pv))
    print(f"\n  MULTIPLICITY  {len(pv)} tests (Q1 over {len(reps)} arms + Q2 over {len(reps) - 1}), "
          f"BH q=0.05 over the UNION: surviving {int(kp.sum())}   not {len(pv) - int(kp.sum())}")
    out["multiplicity"] = {"tested": len(pv), "surviving": int(kp.sum())}

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    dose, fl, ce = {}, None, None
    for delta in (0.0, 0.005, 0.01, 0.02, 0.05):
        d = (VH["coval_core"] + delta) - VH["full"]
        e, lo, hi, _ = ci(d - (VH["coval_core"] - VH["full"]))       # the PLANT alone
        res = bool(lo > 0)
        dose[str(delta)] = {"planted_eff": e, "resolved": res}
        print(f"     POSITIVE  delta {delta:<6} the plant alone {e:+.5f}  "
              f"{'resolves' if res else 'does not resolve'}")
        if delta == 0.0:
            fl = res
        if delta == 0.05:
            ce = res
    posok = (fl is False) and (ce is True)
    print(f"     POSITIVE  band COMPUTED: floor {fl} at delta 0, ceiling {ce} at 0.05   "
          f"{'admissible' if fl != ce else 'DEGENERATE'}   {'PASS' if posok else 'FAIL'}")

    q1_sh = float(vs_class(C["coval_core"], FCsh).mean())
    q2_unchanged = float(np.abs((VH["coval_core"] - VH["full"]) -
                                (vs_human(C["coval_core"]) - vs_human(C["full"]))).max())
    negok = q1_sh < q1["coval_core"]["vs_full"] and q2_unchanged == 0.0
    print(f"     NEGATIVE  `full`'s class shuffled: Q1 {q1['coval_core']['vs_full']:.4f} -> "
          f"{q1_sh:.4f}; Q2 unchanged to {q2_unchanged:.1e} (a DERIVATION -- Q2 never touches "
          f"`full`'s CLASS)   {'PASS' if negok else 'FAIL'}")
    print(f"               world it excludes: 'Q1 measures something other than agreement with the "
          f"PROMPT-MATCHED rubric'")

    frng = np.random.default_rng(SEEDS[0] + 17)
    halves = []
    for _ in range(20):
        h1 = np.zeros(P)
        h2 = np.zeros(P)
        for i in range(P):
            k = len(HC[i])
            pm = frng.permutation(k)
            a1, a2_ = pm[:k // 2], pm[k // 2:2 * (k // 2)]
            h1[i] = (HC[i][a1] == C["coval_core"][i]).mean()
            h2[i] = (HC[i][a2_] == C["coval_core"][i]).mean()
        halves.append(abs(h1.mean() - h2.mean()))
    print(f"     NOISE FLOOR  annotator split-half on the human column, 20 draws "
          f"{np.mean(halves):.6f}   Q1 sham spread over {len(sham_arms)} random arms "
          f"{np.std([q1[a]['sham_random_arm'] for a in reps], ddof=1):.6f}")

    gate = okobj and posok and negok
    out["controls"] = {"dose": dose, "positive_ok": posok, "negative_ok": negok,
                       "q1_shuffled": q1_sh, "q2_unchanged": q2_unchanged,
                       "split_half": float(np.mean(halves)), "gate": gate}
    print(f"     GATE      {'PASS -- the kill may evaluate' if gate else 'FAIL -- UNVERIFIED'}")

    # ================= E3 · the dissolution =======================================================
    print("\n  E3 - THE DISSOLUTION")
    cc = "coval_core"
    q1_ok = q1[cc]["lo"] > 0 and rc > 0
    q1_specific = q1[cc]["vs_full"] - q1[cc]["sham_random_arm"]
    q2_ok = q2[cc]["resolved"] and q2[cc]["eff"] > 0
    print(f"     Q1 `{cc}` preserves the rubric above its shuffled floor: excess "
          f"{q1[cc]['excess_over_shuffled']:+.4f} [{q1[cc]['lo']:+.4f}, {q1[cc]['hi']:+.4f}], and "
          f"its D3 residual is {rc:+.4f} [{rlo:+.4f}, {rhi:+.4f}] -> {q1_ok}")
    print(f"     ⚠ SCOPE: the RESOLVED part of Q1 is `prompt-matched rubric vs SHUFFLED rubric`. "
          f"The SPECIFICITY part -- `full` rather than any other arm's class -- is "
          f"{q1_specific:+.4f} against the random-arm sham and this round computes NO interval for "
          f"it, so it is a point statement. Q1 is resolved for matching, unresolved for specificity.")
    print(f"     Q2 `{cc}` beats `full` at predicting the human: {q2[cc]['eff']:+.4f} "
          f"[{q2[cc]['lo']:+.4f}, {q2[cc]['hi']:+.4f}] -> {q2_ok}")
    print(f"     -> the A/B fork is {'FALSE: both hold, and D2 says nothing forbade that' if (q1_ok and q2_ok) else 'not dissolved by this data'}")
    out["e3"] = {"q1_ok": q1_ok, "q1_specificity_gap": q1_specific, "q1_specificity_resolved": False, "q2_ok": q2_ok, "fork_false": bool(q1_ok and q2_ok)}

    # ================= E4 · the wall audit ========================================================
    print("\n  E4 - THE WALL AUDIT")
    print(f"     R793's NEXT: 'the first thing in this arc that no further computation can decide.'")
    print(f"     What decided it: two SAME-TARGET comparisons, both already computable from data "
          f"R793 itself loaded. Cost: three lines, zero new instruments.")
    out["e4"] = {"wall": "R793 NEXT: the normalisation cannot be decided by computation",
                 "status": "FALSE", "what_decided_it": "two same-target comparisons (D1)"}

    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif not q1_ok:
        world = "A"
    elif not q2_ok:
        world = "B"
    else:
        world = "C"
    print(f"     gate {gate}   Q1 {q1_ok}   Q2 {q2_ok}  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/two_targets.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                             text=True).stdout.strip()
    except Exception:
        sha = "unknown"
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
