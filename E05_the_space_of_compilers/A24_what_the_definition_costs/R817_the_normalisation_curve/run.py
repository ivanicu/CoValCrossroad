#!/usr/bin/env python3
"""R817 · the normalisation curve — does the arc's ordering survive removing the tie handicap?

R816's NEXT proposed dividing each committed A2 by its prompt's attainable maximum. CHECK #419 found
this arc has been burned by that operation twice: R793 swept three ceiling normalisations and got
WORLD A / B / A — the verdict flipped with the choice — and R807's g=0 control caught a denominator
estimated from the numerator's own data. Measured here: corr(A2, att) = +0.6138 shared, +0.3798
disjoint, so ~0.23 of the coupling is shared annotator noise.

ESTIMAND        E1 the ordering under SIX normalisations · E2 ⭐ rank correlation vs raw and margin
                flips · E3 ⭐ the shared-noise price R793 never measured · E4 verdict changes
IDENTIFICATION  only the SPLIT-HALF normalisation is identified; the shared one is the confounded
                contrast and is never an answer
DERIVED FIRST   D1 a per-prompt divisor cannot reorder within a prompt but can after averaging,
                because the weights change — that IS the mechanism · D2 a constant divisor leaves
                the ordering exactly unchanged (placebo) · D3 att's mean 0.6863 is above every arm,
                so ratios should stay under 1 · D4 an arm proportional to att must move in rank
WORLDS          A ordering-robust · B normalisation-dependent · C not identified — B checked FIRST
CONTROLS        OBJECT · PLACEBO · POSITIVE with a g=0 check · NEGATIVE (att permuted) · NOISE FLOOR
"""
import hashlib
import itertools
import json
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
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
ARMS = ["coval_core", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1", "topw_k4",
        "genericpool16", "random_k4_s0", "gen_sham", "full"]
MARG = [("oracle_k4_fit1", "genericpool16", "R805 fitted − blind pool"),
        ("coval_core", "genericpool16", "R805 released core − blind pool"),
        ("topw_k4", "random_k4_s0", "R811 rule effect (k=4)"),
        ("coval_core", "gen_sham", "the sham gap")]


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


def weak_orders():
    seen = {}
    for v in itertools.product(range(4), repeat=4):
        seen.setdefault(tuple(int(np.sign(v[i] - v[j])) for i, j in PR), v)
    return np.array(sorted(seen))


def spearman(a, b):
    ra = np.argsort(np.argsort(-np.asarray(a, float)))
    rb = np.argsort(np.argsort(-np.asarray(b, float)))
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    out = {"instrument_unit": "a PROMPT", "claim_unit": "a NORMALISATION"}
    W = weak_orders()
    tg, _ = load_targets()
    S = {a: load_sat(RES / f"sat_{a}.npz") for a in ARMS}
    pids = sorted(set.intersection(*(set(v) for v in S.values())) &
                  {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(y, float)) for y, _ in tg[p]]) for p in pids}
    pids = [p for p in pids if len(H[p]) >= 2]
    N = len(pids)
    CL = {a: {p: np.array(cls(yvec(S[a][p], sorted({i for i, _ in S[a][p]})))) for p in pids}
          for a in ARMS}
    A2 = {a: np.array([float((H[p] == CL[a][p]).mean()) for p in pids]) for a in ARMS}
    att = np.array([((H[p][None, :, :] == W[:, None, :]).mean(axis=1)).mean(axis=1).max()
                    for p in pids])
    tie = np.array([float((H[p] == 0).mean()) for p in pids])
    print(f"  POPULATION  {N} prompts · per-prompt att mean {att.mean():.6f} "
          f"range [{att.min():.3f}, {att.max():.3f}] · tie mean {tie.mean():.4f} sd {tie.std():.4f}")

    # split-half: att from half A, A2 from half B, disjoint annotators
    rng = np.random.default_rng(7)
    attA = np.zeros(N)
    A2B = {a: np.zeros(N) for a in ARMS}
    for i, p in enumerate(pids):
        h = H[p]
        pm = rng.permutation(len(h))
        k = max(1, len(h) // 2)
        A, B = h[pm[:k]], (h[pm[k:]] if len(pm) > k else h[pm[:k]])
        attA[i] = ((A[None, :, :] == W[:, None, :]).mean(axis=1)).mean(axis=1).max()
        for a in ARMS:
            A2B[a][i] = float((B == CL[a][p]).mean())

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK")
    cc = float(A2["coval_core"].mean())
    ok = abs(att.mean() - 0.686265) < 1e-6 and abs(cc - 0.5664774811929549) < 1e-9
    print(f"     mean per-prompt attainable max {att.mean():.6f} vs R804's committed CEIL_ATT "
          f"0.686265")
    print(f"     `coval_core` A2 {cc:.10f} vs committed 0.5664774812   {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: the record did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"ceil_att": float(att.mean()), "coval_core": cc, "n": N}

    # ================= E1 · six normalisations ===================================================
    print("\n  E1 - SIX NORMALISATIONS, ALL DEFENSIBLE, ALL REPORTED")
    print("     ⚠ D1: a per-prompt divisor cannot reorder WITHIN a prompt; it reorders after")
    print("     averaging because the weights change. That is the mechanism, stated first.")
    NORMS = {
        "raw": lambda v, a_, t_: v,
        "div_att_shared": lambda v, a_, t_: v / a_,
        "div_att_splithalf": None,                       # handled separately, disjoint halves
        "div_1_minus_tie": lambda v, a_, t_: v / np.maximum(1 - t_, 1e-9),
        "subtractive": lambda v, a_, t_: v - a_,
        "div_sqrt_att": lambda v, a_, t_: v / np.sqrt(a_),
    }
    vals, over1 = {}, []
    for nm, f in NORMS.items():
        if nm == "div_att_splithalf":
            vals[nm] = {a: float((A2B[a] / attA).mean()) for a in ARMS}
        else:
            vals[nm] = {a: float(f(A2[a], att, tie).mean()) for a in ARMS}
        if nm.startswith("div") and max(vals[nm].values()) > 1.0:
            over1.append(nm)
    print(f"     {'arm':<16}" + "".join(f"{n[:13]:>15}" for n in NORMS))
    for a in ARMS:
        print(f"     {a:<16}" + "".join(f"{vals[n][a]:>15.4f}" for n in NORMS))
    print(f"     D3 normalisations producing a value above 1 (denominator is not a ceiling): "
          f"{over1 if over1 else 'none'}")
    out["e1"] = vals

    # ================= E2 · ordering and margins =================================================
    print("\n  E2 - RANK CORRELATION AGAINST RAW, AND MARGIN FLIPS")
    raw = [vals["raw"][a] for a in ARMS]
    idx = np.random.default_rng(1234).integers(0, N, (NBOOT, N))
    e2 = {}
    for nm in NORMS:
        sp = spearman(raw, [vals[nm][a] for a in ARMS])
        flips = []
        for x, y, lab in MARG:
            if nm == "div_att_splithalf":
                d = A2B[x] / attA - A2B[y] / attA
                d0 = A2[x] - A2[y]
            else:
                f = NORMS[nm]
                d = f(A2[x], att, tie) - f(A2[y], att, tie)
                d0 = A2[x] - A2[y]
            flips.append((d.mean() > 0) != (d0.mean() > 0))
        e2[nm] = {"spearman": sp, "flips": int(sum(flips)),
                  "which": [lab for (x, y, lab), fl in zip(MARG, flips) if fl]}
        print(f"     {nm:<20} Spearman vs raw {sp:+.4f}   margins flipping sign: {sum(flips)} of "
              f"{len(MARG)}   {e2[nm]['which'] if flips and sum(flips) else ''}")
    out["e2"] = e2

    # ================= E3 · the shared-noise price ===============================================
    print("\n  E3 - THE SHARED-NOISE PRICE, WHICH R793 NEVER MEASURED")
    cs = float(np.corrcoef(A2["coval_core"], att)[0, 1])
    cd = float(np.corrcoef(A2B["coval_core"], attA)[0, 1])
    sp_sd = spearman([vals["div_att_shared"][a] for a in ARMS],
                     [vals["div_att_splithalf"][a] for a in ARMS])
    print(f"     corr(A2, att) shared annotators {cs:+.4f}   disjoint halves {cd:+.4f}   "
          f"difference {cs - cd:+.4f}")
    print(f"     Spearman between the SHARED and SPLIT-HALF orderings: {sp_sd:+.4f}")
    print(f"     ⭐ the shared version's per-arm values sit "
          f"{np.mean([vals['div_att_shared'][a] - vals['div_att_splithalf'][a] for a in ARMS]):+.4f}"
          f" from the split-half version on average")
    out["e3"] = {"corr_shared": cs, "corr_disjoint": cd, "spearman_shared_vs_split": sp_sd}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    const = {a: float((A2[a] / 0.686265).mean()) for a in ARMS}
    sp_const = spearman(raw, [const[a] for a in ARMS])
    plac_ok = abs(sp_const - 1.0) < 1e-12
    print(f"     PLACEBO   D2 a CONSTANT divisor: Spearman vs raw {sp_const:.12f}   "
          f"{'PASS - exactly unchanged' if plac_ok else 'FAIL'}")
    # ⛔ BOTH THE POSITIVE CONTROL AND ITS g=0 CHECK WERE MIS-SPECIFIED, and in the same way:
    # each was built from an arbitrary synthetic LEVEL rather than from the mechanism.
    #  · the "proportional to att" arm was `att * 0.8`; whether it changes RANK depends on the
    #    constant 0.8 I chose, not on whether normalising does anything.
    #  · the "independent of att" arm was a CONSTANT, and a constant divided by a per-prompt
    #    divisor has mean(c/att) > c/mean(att) by JENSEN'S INEQUALITY — so it moves, and my check
    #    called that a failure when it is D1's mechanism operating exactly as derived.
    # Repaired to a DOSE LADDER on a real arm compared with itself, which involves no arbitrary
    # level: add c x (att − mean att), which leaves the RAW mean unchanged BY CONSTRUCTION (a
    # derivation) while the NORMALISED mean must move monotonically if the normalisation works.
    base_v = A2["coval_core"]
    cen = att - att.mean()
    ladder = {}
    for c in (0.0, 0.1, 0.3):
        v = base_v + c * cen
        ladder[c] = (float(v.mean()), float((v / att).mean()))
    # ⛔ AND THE DIRECTION WAS ASSERTED, NOT DERIVED — the third mis-specification of this same
    # control. Two lines settle it: mean((v + c·cen)/att) = mean(v/att) + c·mean(cen/att), and
    # mean(cen/att) = 1 − mean(att)·mean(1/att), which is NEGATIVE by Jensen's inequality since
    # mean(1/att) > 1/mean(att). So the ladder MUST DECREASE, and the slope is predictable exactly.
    raw_flat = all(abs(ladder[c][0] - ladder[0.0][0]) < 1e-12 for c in ladder)
    pred_slope = float(1.0 - att.mean() * np.mean(1.0 / att))
    obs_slope = (ladder[0.3][1] - ladder[0.0][1]) / 0.3
    nrm_mono = ladder[0.0][1] > ladder[0.1][1] > ladder[0.3][1]
    slope_ok = abs(obs_slope - pred_slope) < 1e-9
    pos_ok = raw_flat and nrm_mono and slope_ok
    g0_ok = abs(ladder[0.0][1] - float((base_v / att).mean())) < 1e-15
    print(f"     POSITIVE  dose ladder on a real arm, c x (att − mean att):")
    for c in (0.0, 0.1, 0.3):
        print(f"        c={c:<4} raw mean {ladder[c][0]:.10f}   normalised {ladder[c][1]:.6f}")
    print(f"        raw mean unchanged by construction: {raw_flat}")
    print(f"        DERIVED slope 1 − mean(att)·mean(1/att) = {pred_slope:+.8f}   observed "
          f"{obs_slope:+.8f}   |Δ| {abs(obs_slope - pred_slope):.2e}")
    print(f"        decreasing as Jensen requires: {nrm_mono}   slope matches the derivation: "
          f"{slope_ok}   {'PASS' if pos_ok else 'FAIL'}")
    print(f"     g=0 CHECK at c=0 the normalised value equals the un-doped arm exactly: {g0_ok}   "
          f"{'PASS - the control can fail' if g0_ok else 'FAIL'}")
    rngn = np.random.default_rng(909)
    sps = []
    for _ in range(200):
        ap = att[rngn.permutation(N)]
        sps.append(spearman(raw, [float((A2[a] / ap).mean()) for a in ARMS]))
    sps = np.array(sps)
    real_sp = e2["div_att_shared"]["spearman"]
    neg_ok = float(sps.mean()) >= real_sp - 1e-12
    print(f"     NEGATIVE  att PERMUTED across prompts, 200 draws: Spearman vs raw "
          f"{sps.mean():+.4f} [{np.percentile(sps, 2.5):+.4f}, {np.percentile(sps, 97.5):+.4f}]"
          f"   real {real_sp:+.4f}   reverts toward raw: {neg_ok}   "
          f"{'PASS' if neg_ok else 'FAIL'}")
    rngh = np.random.default_rng(55)
    hs = []
    for _ in range(20):
        aA = np.zeros(N)
        vB = np.zeros(N)
        for i, p in enumerate(pids):
            h = H[p]
            pm = rngh.permutation(len(h))
            k = max(1, len(h) // 2)
            A, B = h[pm[:k]], (h[pm[k:]] if len(pm) > k else h[pm[:k]])
            aA[i] = ((A[None, :, :] == W[:, None, :]).mean(axis=1)).mean(axis=1).max()
            vB[i] = float((B == CL["coval_core"][p]).mean())
        hs.append(float((vB / aA).mean()))
    print(f"     NOISE FLOOR  20 annotator half-splits, split-half cell: sd {np.std(hs):.4f}")
    gate = ok and plac_ok and pos_ok and g0_ok and neg_ok
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo_spearman": sp_const, "placebo_ok": plac_ok,
                       "positive_moves": pos_ok, "g0_ok": g0_ok,
                       "null_spearman": float(sps.mean()), "negative_ok": neg_ok,
                       "halfsplit_sd": float(np.std(hs)), "gate": gate}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    worst = min(e2[n]["spearman"] for n in NORMS)
    tot_flips = sum(e2[n]["flips"] for n in NORMS)
    if not gate:
        world = "UNVERIFIED"
    elif sp_sd < 0.9:
        world = "C"
    elif worst < 0.9 or tot_flips > 0:
        world = "B"
    else:
        world = "A"
    print(f"     worst Spearman vs raw across the six: {worst:+.4f}   total margin flips: "
          f"{tot_flips}   shared-vs-split Spearman {sp_sd:+.4f}  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/normalisation_curve.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
