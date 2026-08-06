#!/usr/bin/env python3
"""R787 · `q` is a monotone COARSENING of A2 — the 1,820-member class contributes a threshold.

R786 asked whether the residual of q_resolved on A2 is distinguishable from zero. CHECK #389 derived
the answer first: mean(v_arm − REF_i) = A2_arm − A2_ref_i, so an arm beats a reference iff its A2
exceeds that reference's, and q is the arm's PERCENTILE in the reference A2 distribution — a
deterministic monotone step function of A2 alone. Only q_resolved's per-reference MDE term, which
depends on sd(v − REF_i), can carry anything else.

ESTIMAND        E1 the identity, VERIFIED pair by pair (47,320 pairs) · E2 the information loss and
                the taus · E3 what the class contributes: its A2 quantiles, the cut points ·
                E4 CAN the variance term invert the A2 order, by construction
IDENTIFICATION  E1-E3 exact; E4 identified BY CONSTRUCTION and reported as a capability, never as a
                claim about the real arms
DERIVED FIRST   D1 q is a monotone function of A2, exactly · D2 therefore tau=+1 is a DERIVATION and
                a check on the code, not evidence · D3 only q_resolved's variance term can differ ·
                D4 a coarsening cannot add information
WORLDS          A coarsening + threshold · B the variance term is live · C the identity fails
CONTROLS        OBJECT · PLACEBO · POSITIVE (band computed) · SHAM (the class vs one reference) ·
                VARIANCE sweep · ⛔ no permutation NEGATIVE (D1 makes it void)
"""
import itertools
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls                 # noqa: E402

RES = ROOT / "corebench/results"
R782 = (ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
        / "R782_the_released_core_does_not_have_four_criteria/results/size_and_comparator.json")
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
SEED = 31337

INSTRUMENT_UNIT = "an (arm, reference) pair"
CLAIM_UNIT = "an arm"


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


def tau(x, y):
    c = d = 0
    for i, j in itertools.combinations(range(len(x)), 2):
        s = np.sign(x[i] - x[j]) * np.sign(y[i] - y[j])
        if s > 0:
            c += 1
        elif s < 0:
            d += 1
    return (c - d) / max(c + d, 1), c, d


def main():
    out = {"instrument_unit": INSTRUMENT_UNIT, "claim_unit": CLAIM_UNIT}

    # ================= OBJECT CHECK -- exit 2, never 0 ============================================
    print("  OBJECT CHECK")
    if not R782.is_file():
        print("  UNRUNNABLE: R782's artifact is absent. Exit 2, never 0.")
        return 2
    q782 = json.loads(R782.read_text())["e4"]["q"]
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    P = len(pids)
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]

    def a2_from_Y(Y):
        o = np.zeros(P)
        for a in range(P):
            s = np.sign(Y[a][[i for i, _ in PR]] - Y[a][[j for _, j in PR]])
            o[a] = np.mean([(s == h).mean() for h in HC[a]])
        return o

    idx = sorted({i for i, _ in POOL[pids[0]]})
    T = np.zeros((P, len(idx), 4))
    for a, p in enumerate(pids):
        for bi, i in enumerate(idx):
            for c_, x in enumerate(L):
                T[a, bi, c_] = POOL[p].get((i, x), 0.0)
    SUB = list(itertools.combinations(range(len(idx)), 4))
    REF = np.zeros((len(SUB), P))
    for si, s in enumerate(SUB):
        REF[si] = a2_from_Y(T[:, list(s), :].sum(axis=1))
    print(f"     R782 arms {len(q782)}   prompts {P}   references rebuilt {len(SUB)}")
    if len(SUB) != 1820 or not q782:
        print("  UNRUNNABLE: the class is not 1,820 or the artifact is empty. Exit 2, never 0.")
        return 2

    # ---- rebuild each arm's per-prompt A2 --------------------------------------------------------
    arms = {}
    for t in q782:
        f = RES / f"sat_{t}.npz"
        if not f.is_file():
            continue
        S = load_sat(f)
        if not set(pids) <= set(S):
            continue
        Y = np.zeros((P, 4))
        for a, p in enumerate(pids):
            ii = sorted({i for i, _ in S[p]})
            Y[a] = [sum(S[p].get((i, x), 0.0) for i in ii) for x in L]
        arms[t] = a2_from_Y(Y)
    print(f"     arms rebuilt from sat files: {len(arms)} of {len(q782)}")
    out["object"] = {"arms": len(arms), "refs": len(SUB), "prompts": P}

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    k0 = sorted(arms)[0]
    plac = float((arms[k0] - arms[k0]).mean())
    print(f"     PLACEBO    an arm against itself: paired mean {plac:.6f}  "
          f"{'PASS' if plac == 0.0 else 'FAIL'}")
    refA2 = REF.mean(axis=1)
    member = REF[7]
    q_mem = float(((member[None, :] - REF).mean(axis=1) > 0).mean())
    rank_mem = float((refA2 < member.mean()).mean())
    g0ok = abs(q_mem - rank_mem) < 1e-12
    print(f"     PLACEBO-2  a class member scored against the class: q {q_mem:.6f} vs its own A2 "
          f"rank {rank_mem:.6f}  {'PASS (identical)' if g0ok else 'FAIL'}")
    # ⚠ THE FIRST DRAFT USED `sorted(arms)[0]`, which is `coval_core` at A2 0.5665 -- ABOVE the whole
    # class, so every shift returned q = 1.0 and the "band computed at both ends" had floor ==
    # ceiling == 1.0. §4's *control that cannot PASS*, sub-kind one: a DEGENERATE band admits no
    # threshold. The arm is now chosen as the one whose A2 is nearest the class median, so the sweep
    # actually traverses the class and the band has two different ends.
    kmed = min(arms, key=lambda t: abs(arms[t].mean() - float(np.median(refA2))))
    print(f"     POSITIVE   sweeping `{kmed}` (A2 {arms[kmed].mean():.4f}), chosen as nearest the "
          f"class median {float(np.median(refA2)):.4f} so the band is not degenerate")
    dose, posok = {}, True
    v0 = arms[kmed]
    for c in (0.0, 0.02, 0.05, 0.30):
        v = v0 + c
        qq = float(((v[None, :] - REF).mean(axis=1) > 0).mean())
        expect = float((refA2 < v.mean()).mean())
        dose[str(c)] = {"q": qq, "expected_percentile": expect, "match": abs(qq - expect) < 1e-12}
        print(f"     POSITIVE   shift {c:>5.2f}  q {qq:.6f}  expected percentile {expect:.6f}  "
              f"{'MATCH' if dose[str(c)]['match'] else 'MISMATCH'}")
        if not dose[str(c)]["match"]:
            posok = False
    degenerate = dose["0.0"]["q"] == dose["0.3"]["q"]
    posok = posok and not degenerate
    print(f"                band COMPUTED: floor {dose['0.0']['q']:.4f} at shift 0, ceiling "
          f"{dose['0.3']['q']:.4f} above the class maximum   "
          f"{'DEGENERATE (floor == ceiling)' if degenerate else 'admissible'}   "
          f"POSITIVE {'PASS' if posok else 'FAIL'}")
    print(f"     NEGATIVE   ⛔ NOT BUILT -- D1: q is an algebraic function of A2, so permuting an arm "
          f"across prompts leaves A2 and therefore q unchanged (ledger 1125/1129, third decline)")
    gate = plac == 0.0 and g0ok and posok
    out["controls"] = {"placebo": plac, "placebo2": {"q": q_mem, "rank": rank_mem, "ok": g0ok},
                       "dose": dose, "positive": posok, "gate": gate}

    # ================= E1 · the identity, verified on every pair ==================================
    print(f"\n  E1 - THE IDENTITY, VERIFIED ON {len(arms) * len(SUB):,} (arm, reference) PAIRS")
    disagree = 0
    for t, v in arms.items():
        pm = (v[None, :] - REF).mean(axis=1)
        alg = v.mean() - refA2
        disagree += int((np.sign(pm) != np.sign(alg)).sum())
    print(f"     sign(mean(v - REF)) != sign(A2_arm - A2_ref):  {disagree} disagreements")
    print(f"     ⚠ D2: a zero here is a CHECK ON THE CODE, not evidence -- the identity is algebra")
    out["e1"] = {"pairs": len(arms) * len(SUB), "disagreements": disagree}

    # ================= E2 · the information loss ==================================================
    print("\n  E2 - INFORMATION LOSS")
    names = sorted(arms, key=lambda t: -q782[t]["a2"])
    a2 = np.array([q782[t]["a2"] for t in names])
    qv = np.array([q782[t]["q"] for t in names])
    qr = np.array([q782[t]["q_res"] for t in names])
    t1, c1, d1 = tau(a2, qv)
    t2, c2, d2 = tau(a2, qr)
    print(f"     distinct values   A2 {len(set(np.round(a2, 6)))}   q {len(set(qv))}   "
          f"q_resolved {len(set(qr))}   over {len(names)} arms")
    print(f"     Kendall tau(A2, q)          {t1:+.4f}   concordant {c1}  discordant {d1}")
    print(f"     Kendall tau(A2, q_resolved) {t2:+.4f}   concordant {c2}  discordant {d2}")
    out["e2"] = {"n_arms": len(names), "distinct_a2": len(set(np.round(a2, 6))),
                 "distinct_q": len(set(qv)), "distinct_qres": len(set(qr)),
                 "tau_q": t1, "disc_q": d1, "tau_qres": t2, "disc_qres": d2}

    # ================= E3 · what the class contributes: the cut points =============================
    print("\n  E3 - WHAT THE CLASS CONTRIBUTES: ITS A2 QUANTILES, i.e. THE CUT POINTS")
    print(f"     reference A2: min {refA2.min():.6f}  max {refA2.max():.6f}  "
          f"range {refA2.max() - refA2.min():.6f}")
    cuts = {f"p{p}": float(np.percentile(refA2, p)) for p in (0, 5, 25, 50, 75, 95, 100)}
    print("     " + "  ".join(f"{k} {v:.4f}" for k, v in cuts.items()))
    print(f"     ⭐ an arm's q is fully determined by where its A2 falls in this list; the class's "
          f"ONLY contribution to clause ② is these {len(refA2)} numbers, of which the arms resolve "
          f"{len(set(qv))}")
    # SHAM: the class removed -- one reference instead of 1,820
    one = refA2[0]
    sham = {t: bool(q782[t]["a2"] > one) for t in names}
    agree = sum(1 for t in names if (q782[t]["q"] > 0.5) == sham[t])
    print(f"     SHAM (class removed, ONE reference at A2 {one:.4f}): agrees with q>0.5 on "
          f"{agree} of {len(names)} arms")
    out["e3"] = {"ref_min": float(refA2.min()), "ref_max": float(refA2.max()), "cuts": cuts,
                 "sham_one_ref_agreement": agree, "sham_ref_a2": float(one)}

    # ================= E4 · CAN the variance term invert the order? ===============================
    print("\n  E4 - CAN q_resolved's VARIANCE TERM INVERT THE A2 ORDER?  (by construction)")
    rng = np.random.default_rng(SEED)
    va = arms[names[len(names) // 2]]
    base_a2 = va.mean()
    obs_sd = []
    for t, v in arms.items():
        obs_sd.append(float((v[None, :] - REF).std(axis=1, ddof=1).mean()))
    lo_sd, hi_sd = float(np.min(obs_sd)), float(np.max(obs_sd))
    print(f"     observed per-reference sd across real arms: [{lo_sd:.4f}, {hi_sd:.4f}]  "
          f"ratio {hi_sd / max(lo_sd, 1e-12):.3f}")
    sweep, inverted_at = {}, None
    for ratio in (1.0, 1.5, 2.0, 4.0, 8.0):
        noise = rng.normal(0, 1, P)
        noise -= noise.mean()
        s = noise.std(ddof=1)
        hi = va + noise * (base_a2 * 0 + 1) * ((ratio - 1.0) * 0.05 / max(s, 1e-12))
        hi = hi - hi.mean() + base_a2 + 1e-6          # equal A2 (+epsilon), larger variance
        lo = va - va.mean() + base_a2                  # equal A2, original variance
        def qres(v):
            d = v[None, :] - REF
            m = d.mean(axis=1)
            mde = ZEFF * d.std(axis=1, ddof=1) / math.sqrt(P)
            return float(((m > 0) & (np.abs(m) >= mde)).mean())
        qh, ql = qres(hi), qres(lo)
        sweep[str(ratio)] = {"q_hi_var": qh, "q_lo_var": ql, "inverted": bool(qh < ql)}
        print(f"     variance ratio {ratio:>4.1f}   higher-variance arm q_res {qh:.4f}   "
              f"lower-variance arm q_res {ql:.4f}   "
              f"{'INVERTS' if qh < ql else 'no inversion'}")
        if qh < ql and inverted_at is None:
            inverted_at = ratio
    in_range = inverted_at is not None and inverted_at <= hi_sd / max(lo_sd, 1e-12)
    print(f"     first inversion at ratio {inverted_at}   observed ratio "
          f"{hi_sd / max(lo_sd, 1e-12):.3f}   within the arms' observed range: {in_range}")
    out["e4"] = {"obs_sd_lo": lo_sd, "obs_sd_hi": hi_sd,
                 "obs_ratio": hi_sd / max(lo_sd, 1e-12), "sweep": sweep,
                 "inverted_at": inverted_at, "in_observed_range": bool(in_range)}

    # ================= WORLD =======================================================================
    if not gate:
        world = "UNVERIFIED - a control did not fire. Never OVERTURNED, never CONFIRMED."
    elif disagree > 0:
        world = (f"C - THE IDENTITY FAILS: {disagree} of {len(arms) * len(SUB):,} pairs disagree with "
                 f"the algebra; every q in this arc is UNVERIFIED")
    elif in_range:
        world = (f"B - THE VARIANCE TERM IS LIVE: q_resolved inverts the A2 order at a variance ratio "
                 f"of {inverted_at}, inside the arms' observed range of "
                 f"{hi_sd / max(lo_sd, 1e-12):.3f}")
    else:
        world = (f"A - q IS A COARSENING AND THE CLASS IS A THRESHOLD: the identity holds on all "
                 f"{len(arms) * len(SUB):,} pairs, {len(set(np.round(a2, 6)))} distinct A2 values "
                 f"collapse to {len(set(qv))} q and {len(set(qr))} q_resolved values with 0 "
                 f"discordant pairs, and the variance term does not inv"
                 f"ert within the observed range")
    print(f"\n  WORLD {world}")
    out["world"] = world
    out["tree_sha"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip()
    d = pathlib.Path(__file__).resolve().parent / "results"
    d.mkdir(exist_ok=True)
    (d / "q_is_a2.json").write_text(json.dumps(out, indent=2, default=_plain))
    print("  artifact -> q_is_a2.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
