#!/usr/bin/env python3
"""R781 · the extension as a DISTRIBUTION over the reference class, not a count at a chosen percentile.

CHECK #383 retracted R780's NEXT on the failure mode R780 itself documented: I counted blind arms
WITH AN NPZ ON DISK (2) when the claim was about blind references AVAILABLE -- every k=4 subset of
`sat_genericpool16.npz` is one, C(16,4) = 1,820, no generation required. And R527/R665 had already
established on release 1 what R780 reported as new on release 2.

ESTIMAND        E1 q(arm) = the fraction of the 1,820 blind references an arm beats · E2 the SHAPE of
                q over the arm population -- the estimand that decides whether an extension can be
                stated without naming a percentile · E3 q with resolution · E4 release-2 transport
IDENTIFICATION  exact on r1; r2's class has 5 members so q takes 6 values -- ordering, not shape
DERIVED FIRST   D1 median-dominance IS p50 · D2 mean-dominance is the skew's percentile · both are
                DERIVATIONS and neither is reported as a finding · D3 only the SHAPE is non-derived
WORLDS          A choice decisive (q ~ 0.5) · B choice marginal (q bimodal) · C ordered, no cut
CONTROLS        OBJECT · POSITIVE (two synthetic plants bounding the band) · g=0 (a class member must
                return its own rank) · NEGATIVE (200) · SHAM (criterion content destroyed) ·
                PLACEBO · DEPENDENCE (effective class size before any q is read)
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
NBOOT = 600
NPERM = 200
SEED = 31337
MID = (0.35, 0.65)
EXT = (0.10, 0.90)


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
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    P = len(pids)
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]

    def a2_from_Y(Yall):
        """Yall: (P, 4) predicted scores -> (P,) A2 over all annotators"""
        o = np.zeros(P)
        for a in range(P):
            s = np.sign(Yall[a][[i for i, _ in PR]] - Yall[a][[j for _, j in PR]])
            o[a] = np.mean([(s == h).mean() for h in HC[a]])
        return o

    # ---- the 1,820 reference class, built from the 16 prompt-blind criteria -----------------------
    idx = sorted({i for i, _ in POOL[pids[0]]})
    T = np.zeros((P, len(idx), 4))
    for a, p in enumerate(pids):
        for bi, i in enumerate(idx):
            for c_, x in enumerate(L):
                T[a, bi, c_] = POOL[p].get((i, x), 0.0)
    SUBSETS = list(itertools.combinations(range(len(idx)), 4))
    print(f"  OBJECT CHECK")
    print(f"     pool criteria {len(idx)}   subsets C(16,4) = {len(SUBSETS)}   prompts {P}")
    if len(idx) != 16 or len(SUBSETS) != 1820 or P == 0:
        print("  UNRUNNABLE: the pool is not 16 criteria. Exit 2, never 0.")
        return 2
    REF = np.zeros((len(SUBSETS), P))
    for si, s in enumerate(SUBSETS):
        REF[si] = a2_from_Y(T[:, list(s), :].sum(axis=1))
    print(f"     reference A2 matrix {REF.shape}   class mean {REF.mean():.4f}   "
          f"range [{REF.mean(1).min():.4f}, {REF.mean(1).max():.4f}]")

    # ---- DEPENDENCE, printed BEFORE any q is interpreted -----------------------------------------
    rng = np.random.default_rng(SEED)
    sam = rng.choice(len(SUBSETS), 300, replace=False)
    C = np.corrcoef(REF[sam])
    mr = float((C.sum() - len(sam)) / (len(sam) * (len(sam) - 1)))
    n_eff = len(SUBSETS) / (1 + (len(SUBSETS) - 1) * mr)
    print(f"     DEPENDENCE mean pairwise reference correlation {mr:+.4f}  ->  effective class size "
          f"{n_eff:.1f} of {len(SUBSETS)}  (q is a fraction over a CORRELATED class)")

    # ---- the arm population ----------------------------------------------------------------------
    arms = {}
    for p in sorted(RES.glob("sat_*.npz")):
        t = p.stem[4:]
        if not re.search(r"_k4(_|$)", t) or re.search(r"_08b|_sham|_ctlS|_2b[AB]", t):
            continue
        S = load_sat(p)
        if not set(pids) <= set(S):
            continue
        Y = np.zeros((P, 4))
        for a, pid in enumerate(pids):
            ii = sorted({i for i, _ in S[pid]})
            Y[a] = [sum(S[pid].get((i, x), 0.0) for i in ii) for x in L]
        arms[t] = a2_from_Y(Y)
    # the published comparator is POOL[0:4] by file order -- name it, do not re-derive it
    arms["generic_POOL0-3"] = a2_from_Y(T[:, [0, 1, 2, 3], :].sum(axis=1))
    print(f"     k=4 arms with full coverage: {len(arms)}")

    # ---- q, leave-one-out against identical references -------------------------------------------
    def q_of(v, loo=True):
        d = v[None, :] - REF
        m = d.mean(axis=1)
        if loo:
            keep = ~np.all(np.abs(d) < 1e-12, axis=1)
        else:
            keep = np.ones(len(REF), bool)
        return float((m[keep] > 0).mean()), int((~keep).sum()), m[keep]

    print("\n  CONTROLS")
    qs, self_excluded = {}, {}
    for t, v in arms.items():
        qs[t], self_excluded[t], _ = q_of(v)
    tot_self = sum(self_excluded.values())
    print(f"     LEAKAGE    self-matching references excluded: {tot_self}   "
          f"(arms affected: {[t for t, n in self_excluded.items() if n]})")

    # PLACEBO -- an arm against a class consisting of itself
    plac = float((( arms["generic_POOL0-3"] - arms["generic_POOL0-3"]).mean() > 0))
    print(f"     PLACEBO    an arm against itself: q = {plac:.4f}  "
          f"{'PASS (exactly tied, not >)' if plac == 0.0 else 'FAIL'}")

    # g=0 -- a genuine class member must return its OWN rank, not 0 or 1
    member = REF[7]
    q_mem, ex_mem, _ = q_of(member)
    rank_mem = float((REF.mean(1) < member.mean()).mean())
    g0ok = 0.0 < q_mem < 1.0 and abs(q_mem - rank_mem) < 0.05 and ex_mem == 1
    print(f"     g=0        a class member scored leave-one-out: q {q_mem:.4f} vs its own rank "
          f"{rank_mem:.4f}   self-excluded {ex_mem}   {'PASS' if g0ok else 'FAIL'}")

    # POSITIVE -- two synthetic plants that BOUND the band, both ends measured
    hi = REF.max(axis=0) + 0.05
    lo = REF.min(axis=0) - 0.05
    q_hi, _, _ = q_of(hi)
    q_lo, _, _ = q_of(lo)
    posok = q_hi == 1.0 and q_lo == 0.0
    inband = all(q_lo <= v <= q_hi for v in qs.values())
    print(f"     POSITIVE   dominating plant q {q_hi:.4f}   dominated plant q {q_lo:.4f}   "
          f"{'PASS' if posok else 'FAIL'}")
    print(f"                band COMPUTED: every real arm's q inside [{q_lo:.2f}, {q_hi:.2f}]: "
          f"{inband}")

    # NEGATIVE -- permute the per-prompt pairing between arm and reference
    v0 = arms["generic_POOL0-3"]
    negs = []
    for _ in range(NPERM):
        negs.append(q_of(v0[rng.permutation(P)])[0])
    negs = np.array(negs)
    print(f"     NEGATIVE   pairing permuted, {NPERM} draws: q "
          f"[{np.percentile(negs, 2.5):.4f}, {np.percentile(negs, 97.5):.4f}]  "
          f"(real {qs['generic_POOL0-3']:.4f})")

    # SHAM -- criterion CONTENT destroyed, prompt-blindness preserved
    Tsh = T[rng.permutation(P)]
    REFsh = np.zeros((200, P))
    pick = rng.choice(len(SUBSETS), 200, replace=False)
    for j, si in enumerate(pick):
        REFsh[j] = a2_from_Y(Tsh[:, list(SUBSETS[si]), :].sum(axis=1))
    q_sham = float(((v0[None, :] - REFsh).mean(axis=1) > 0).mean())
    print(f"     SHAM       criterion content destroyed, blindness kept: q {q_sham:.4f}  "
          f"(real {qs['generic_POOL0-3']:.4f})")

    gate = (plac == 0.0) and g0ok and posok

    # ---- E1/E2 · the distribution ----------------------------------------------------------------
    print(f"\n  E1 - ADMISSION PROBABILITY q OVER THE {len(SUBSETS)}-MEMBER CLASS")
    print(f"     {'arm':<28}{'A2':>9}{'q':>9}{'q_resolved':>12}   published comparator percentile")
    resolved = {}
    for t in sorted(arms, key=lambda t: -qs[t]):
        _, _, m = q_of(arms[t])
        d = arms[t][None, :] - REF
        keep = ~np.all(np.abs(d) < 1e-12, axis=1)
        dk = d[keep]
        sd = dk.std(axis=1, ddof=1)
        mde = ZEFF * sd / math.sqrt(P)
        resolved[t] = float(((m > 0) & (np.abs(m) >= mde)).mean())
        print(f"     {t:<28}{arms[t].mean():>9.4f}{qs[t]:>9.4f}{resolved[t]:>12.4f}")
    qv = np.array([qs[t] for t in arms])
    mid = float(((qv >= MID[0]) & (qv <= MID[1])).mean())
    ext = float(((qv < EXT[0]) | (qv > EXT[1])).mean())
    print(f"\n  E2 - SHAPE   arms {len(qv)}   in [{MID[0]}, {MID[1]}]: {mid:.4f}   "
          f"outside [{EXT[0]}, {EXT[1]}]: {ext:.4f}")
    print(f"     DERIVED, not measured: median-dominance IS p50 (D1); mean-dominance is the skew's "
          f"percentile (D2). Neither is reported as a finding.")

    # ---- E4 · release 2, 5-member blind class ----------------------------------------------------
    print(f"\n  E4 - RELEASE 2 TRANSPORT (blind class has 5 members; q takes 6 values)")
    r2, tg2 = {}, None
    for p in sorted(RES.glob("sat_transport_*.npz")):
        z = np.load(p, allow_pickle=True)
        o = collections.defaultdict(dict)
        for k, v in zip(z["meta"], z["sat"]):
            conv, inter, rid, ci = str(k).split("|")
            o[f"{conv}|{inter}"][(int(ci), rid)] = float(v)
        r2[p.stem[4:]] = o
        if tg2 is None:
            tg2 = {f"{t['conv']}|{t['inter']}": [(r["id"], float(r["score"])) for r in t["resp"]]
                   for t in json.loads(str(z["targets"]))}
    n4 = sorted(i for i, v in tg2.items() if len(v) == 4)
    def s2(arm):
        o = []
        for i in n4:
            S, rid = r2[arm][i], [r for r, _ in tg2[i]]
            ci = sorted({c for c, _ in S})
            y = np.array([sum(S.get((c, r), 0.0) for c in ci) for r in rid])
            t = np.array([s for _, s in tg2[i]])
            o.append(float((np.sign(y[[a for a, _ in PR]] - y[[b for _, b in PR]]) ==
                            np.sign(t[[a for a, _ in PR]] - t[[b for _, b in PR]])).mean()))
        return np.array(o)
    BLIND2 = ["transport_generic", "transport_randblind_s0", "transport_randblind_s1",
              "transport_randblind_s2", "transport_vacuous"]
    A2r2 = {a: s2(a) for a in r2}
    q2 = {}
    for a, v in A2r2.items():
        ms = [float((v - A2r2[b]).mean()) for b in BLIND2 if b != a]
        q2[a] = float(np.mean([m > 0 for m in ms]))
        print(f"     {a:<28}{v.mean():>9.4f}   q over {len(ms)} blind refs {q2[a]:.4f}")

    # ---- WORLD -----------------------------------------------------------------------------------
    if not gate:
        world = "UNVERIFIED - a control did not fire. Never OVERTURNED, never CONFIRMED."
    elif mid >= 0.5:
        world = (f"A - THE CHOICE IS DECISIVE: {mid:.1%} of arms sit in [{MID[0]}, {MID[1]}]; clause "
                 f"② states nothing about an arm without naming its comparator")
    elif ext >= 0.5 and mid < 0.25:
        world = (f"B - THE CHOICE IS MARGINAL: {ext:.1%} of arms are outside [{EXT[0]}, {EXT[1]}] "
                 f"and only {mid:.1%} are in the middle band; an extension can be stated as "
                 f"{{admitted}} + {{borderline, named}}")
    else:
        world = (f"C - ORDERED, NO NATURAL CUT: {mid:.1%} middle, {ext:.1%} extreme; the class "
                 f"induces an ordering and the honest formulation reports q per arm")
    print(f"\n  WORLD {world}")
    out = {"n_prompts": P, "n_refs": len(SUBSETS), "mean_ref_corr": mr, "n_eff_class": n_eff,
           "q": qs, "q_resolved": resolved, "self_excluded": self_excluded,
           "arm_a2": {t: float(v.mean()) for t, v in arms.items()},
           "shape": {"middle_band": mid, "extreme": ext, "MID": list(MID), "EXT": list(EXT)},
           "controls": {"placebo": plac, "g0_q": q_mem, "g0_rank": rank_mem, "g0": g0ok,
                        "positive_hi": q_hi, "positive_lo": q_lo, "positive": posok,
                        "all_in_band": inband, "sham_q": q_sham,
                        "negative": [float(np.percentile(negs, 2.5)),
                                     float(np.percentile(negs, 97.5))]},
           "release2_q": q2, "release2_n": len(n4), "world": world,
           "derivations": ["median-dominance IS p50", "mean-dominance is the skew's percentile"],
           "tree_sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                      capture_output=True, text=True).stdout.strip()}
    d = pathlib.Path(__file__).resolve().parent / "results"
    d.mkdir(exist_ok=True)
    (d / "extension_distribution.json").write_text(json.dumps(out, indent=2, default=_plain))
    print("  artifact -> extension_distribution.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
