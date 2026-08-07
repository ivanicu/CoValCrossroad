#!/usr/bin/env python3
"""R788 · `generic` is a MEMBER of its own comparator class, and the leave-one-out cannot see it.

CHECK #390 derived Var(v − REF) = Var(v) + Var(REF) − 2·Cov(v, REF), measured it over 26 arms, and
found `generic` at sd 0.0711 and corr 0.8859 against everyone else's 0.12–0.17 and 0.45–0.67. The
object says why: `core_generic.json`'s criteria are pool indices [0,1,2,3], so `generic` IS one of the
C(16,4) = 1,820 references. R782 measured its satisfactions differing from POOL[0:4]'s by up to 0.121
on 73 prompts — the same criterion SET scored in two judge passes — so the satisfaction-based
leave-one-out cannot fire.

ESTIMAND        E1 the decomposition, verified · E2 what each exclusion rule catches · E3 the
                MAGNITUDE via a counterfactual sd swap · E4 whether a published verdict moves
IDENTIFICATION  E1/E2/E4 exact; E3's leak size identified only by construction (D1: removing one of
                1,820 cannot move q by more than 0.000549, so the count is not the mechanism)
DERIVED FIRST   D1 one reference of 1,820 bounds the count effect at 0.000549 · D2 MDE scales with sd,
                so `generic` at 0.0711 faces a threshold 1.87x smaller than `gen` at 0.1330 ·
                D3 membership causes the low sd · D4 the exclusion matches the judge's OUTPUT where it
                should match the INPUT
WORLDS          A mechanical and small · B the variance advantage is large · C blindness not membership
CONTROLS        OBJECT · PLACEBO · POSITIVE (jitter sweep, band computed) · CONFOUND (genericpool16) ·
                COUNTERFACTUAL (a construction, labelled)
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
    out = {"instrument_unit": "an (arm, reference) pair", "claim_unit": "an arm"}
    rng = np.random.default_rng(SEED)

    print("  OBJECT CHECK")
    g = json.loads((RES / "core_generic.json").read_text())
    pool = json.loads((RES / "core_genericpool16.json").read_text())
    p0 = next(iter(g))
    G = [str(x).strip() for x in g[p0]]
    PO = [str(x).strip() for x in pool[p0]]
    gidx = sorted(PO.index(x) for x in G if x in PO)
    member = len(gidx) == len(G)
    print(f"     `generic` k={len(G)}   pool k={len(PO)}   its pool indices {gidx}   "
          f"IS a class member: {member}")
    q782 = json.loads(R782.read_text())["e4"]["q"]
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    P = len(pids)
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]

    def a2(Y):
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
        REF[si] = a2(T[:, list(s), :].sum(axis=1))
    self_si = SUB.index(tuple(gidx)) if member and tuple(gidx) in SUB else None
    print(f"     class rebuilt {len(SUB)}   `generic`'s own subset is reference #{self_si}")
    if not member or len(SUB) != 1820 or self_si is None:
        print("  UNRUNNABLE: membership or the class is not as the object says. Exit 2, never 0.")
        return 2

    arms = {}
    for t in list(q782) + ["genericpool16"]:
        f = RES / f"sat_{t}.npz"
        if not f.is_file():
            continue
        S = load_sat(f)
        if not set(pids) <= set(S):
            continue
        Y = np.array([[sum(S[p].get((i, x), 0.0) for i in sorted({i for i, _ in S[p]}))
                       for x in L] for p in pids])
        arms[t] = a2(Y)
    print(f"     arms rebuilt {len(arms)}")
    out["object"] = {"generic_pool_indices": gidx, "is_member": member, "self_ref": self_si,
                     "arms": len(arms), "refs": len(SUB)}

    # ================= E1 · the decomposition, verified ============================================
    print("\n  E1 - Var(v - REF) = Var(v) + Var(REF) - 2 Cov(v, REF), VERIFIED")
    worst = 0.0
    for t, v in arms.items():
        d = v[None, :] - REF
        lhs = d.var(axis=1, ddof=0)
        rhs = v.var(ddof=0) + REF.var(axis=1, ddof=0) - 2 * ((v - v.mean())[None, :]
                                                             * (REF - REF.mean(axis=1, keepdims=True))
                                                             ).mean(axis=1)
        worst = max(worst, float(np.abs(lhs - rhs).max()))
    print(f"     worst |LHS - RHS| over {len(arms)} arms x {len(SUB)} references: {worst:.3e}")
    print(f"     ⚠ a zero here is a DERIVATION check on the code, not evidence")
    out["e1"] = {"worst_mismatch": worst}

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    vg = arms["generic"]
    plac = float((vg - vg).std(ddof=1))
    print(f"     PLACEBO    an arm against itself: sd {plac:.6f}  "
          f"{'PASS' if plac == 0.0 else 'FAIL'}")
    dref = vg[None, :] - REF
    sat_excl = int(np.all(np.abs(dref) < 1e-12, axis=1).sum())
    crit_excl = 1
    print(f"     E2 · EXCLUSION RULES for `generic`:")
    print(f"                satisfaction-based (R781/R782's rule): excludes {sat_excl}")
    print(f"                criterion-based    (the right unit)  : excludes {crit_excl} "
          f"(reference #{self_si})")
    dose, posok = {}, True
    own = a2(T[:, list(gidx), :].sum(axis=1))
    for j in (0.0, 0.001, float(np.abs(vg - own).mean())):
        jit = own + (rng.normal(0, 1, P) * j if j > 0 else 0.0)
        d2 = jit[None, :] - REF
        s_catch = int(np.all(np.abs(d2) < 1e-12, axis=1).sum())
        dose[f"{j:.6f}"] = {"satisfaction_catches": s_catch, "criterion_catches": 1}
        print(f"     POSITIVE   jitter {j:.6f}  satisfaction rule catches {s_catch}   "
              f"criterion rule catches 1")
        if j == 0.0 and s_catch != 1:
            posok = False
        if j > 0 and s_catch != 0:
            posok = False
    print(f"                band COMPUTED: at jitter 0 the satisfaction rule must catch 1 "
          f"({dose['0.000000']['satisfaction_catches']}); at the observed discrepancy it must catch 0 "
          f"   POSITIVE {'PASS' if posok else 'FAIL'}")
    sd_g = float(dref.std(axis=1, ddof=1).mean())
    dp = arms["genericpool16"][None, :] - REF
    sd_p = float(dp.std(axis=1, ddof=1).mean())
    print(f"     CONFOUND   `generic` (blind AND member) sd {sd_g:.4f}   `genericpool16` "
          f"(blind, NOT a member, k=16) sd {sd_p:.4f}   ratio {sd_p / sd_g:.3f}")
    gate = plac == 0.0 and posok and worst < 1e-9
    out["controls"] = {"placebo": plac, "sat_excl": sat_excl, "crit_excl": crit_excl,
                       "dose": dose, "positive": posok, "sd_generic": sd_g,
                       "sd_pool16": sd_p, "confound_ratio": sd_p / sd_g, "gate": gate}

    # ================= E3 · the counterfactual sd swap =============================================
    print("\n  E3 - COUNTERFACTUAL: `generic` AT ANOTHER ARM'S sd, A2 HELD FIXED  (a construction)")

    def qres_with(v, sd_scale, drop=None):
        d = v[None, :] - REF
        keep = np.ones(len(REF), bool)
        if drop is not None:
            keep[drop] = False
        m = d[keep].mean(axis=1)
        mde = ZEFF * d[keep].std(axis=1, ddof=1) * sd_scale / math.sqrt(P)
        return float(((m > 0) & (np.abs(m) >= mde)).mean()), float((m > 0).mean())

    base_qr, base_q = qres_with(vg, 1.0)
    drop_qr, drop_q = qres_with(vg, 1.0, drop=self_si)
    sd_gen = float((arms["gen"][None, :] - REF).std(axis=1, ddof=1).mean())
    scale = sd_gen / sd_g
    swap_qr, _ = qres_with(vg, scale)
    print(f"     published (R782)                q {q782['generic']['q']:.4f}   "
          f"q_res {q782['generic']['q_res']:.4f}")
    print(f"     recomputed here                 q {base_q:.4f}   q_res {base_qr:.4f}")
    print(f"     self-reference #{self_si} removed      q {drop_q:.4f}   q_res {drop_qr:.4f}   "
          f"shift {drop_qr - base_qr:+.6f}   (D1 bounds this at 0.000549)")
    print(f"     sd scaled to `gen`'s ({scale:.3f}x)   q_res {swap_qr:.4f}   "
          f"shift {swap_qr - base_qr:+.4f}   <- the mechanism")
    out["e3"] = {"published_q": q782["generic"]["q"], "published_qres": q782["generic"]["q_res"],
                 "recomputed_q": base_q, "recomputed_qres": base_qr,
                 "drop_self_qres": drop_qr, "drop_shift": drop_qr - base_qr,
                 "sd_scale": scale, "swapped_qres": swap_qr, "swap_shift": swap_qr - base_qr}

    # ================= E4 · does a published verdict move? ========================================
    print("\n  E4 - DOES A PUBLISHED VERDICT MOVE?")
    print(f"     R786's counterexample: `generic` has zero RUBRIC affinity (0.0249 vs its own null "
          f"0.0249) and clears ② at q_res {q782['generic']['q_res']:.4f}")
    still = swap_qr > 0.0
    print(f"     with `gen`'s sd, `generic` would sit at q_res {swap_qr:.4f} — the counterexample "
          f"{'survives' if still else 'collapses'} as a statement about A2, and its q_res value is "
          f"{'contaminated' if abs(swap_qr - base_qr) >= 0.05 else 'stable'}")
    out["e4"] = {"counterexample_survives": still,
                 "qres_contaminated": bool(abs(swap_qr - base_qr) >= 0.05)}

    # ================= WORLD =======================================================================
    if not gate:
        world = "UNVERIFIED - a control did not fire. Never OVERTURNED, never CONFIRMED."
    elif sd_p / sd_g < 1.10:
        world = (f"C - BLINDNESS, NOT MEMBERSHIP: `genericpool16` is blind but not a member and its "
                 f"sd is {sd_p:.4f} against `generic`'s {sd_g:.4f}, a ratio of {sd_p / sd_g:.3f}")
    elif abs(swap_qr - base_qr) >= 0.05:
        world = (f"B - THE VARIANCE ADVANTAGE IS THE LEAK: removing the self-reference moves q_res by "
                 f"{drop_qr - base_qr:+.6f}, but giving `generic` `gen`'s sd moves it by "
                 f"{swap_qr - base_qr:+.4f}, from {base_qr:.4f} to {swap_qr:.4f}")
    else:
        world = (f"A - MECHANICAL AND SMALL: the self-reference is worth {drop_qr - base_qr:+.6f} and "
                 f"the sd swap {swap_qr - base_qr:+.4f}, both below 0.05")
    print(f"\n  WORLD {world}")
    out["world"] = world
    out["tree_sha"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip()
    d = pathlib.Path(__file__).resolve().parent / "results"
    d.mkdir(exist_ok=True)
    (d / "membership.json").write_text(json.dumps(out, indent=2, default=_plain))
    print("  artifact -> membership.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
