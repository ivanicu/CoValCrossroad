#!/usr/bin/env python3
"""R816 · what accounts for the shift — target reliability, or the tie rate?

R815 found nine arms each scoring 0.005–0.012 higher against `personal` than `world`. Its NEXT
proposed one explanation (the target is more reliable). CHECK #418 found that inference's DIRECTION
is nearly forced, and that a second mechanism was never named: `personal`'s tie rate is 0.0206 lower,
and a strict-signed arm can never match a tied human pair, so lower ties make up to +0.0206
available — more than the whole shift. Panel depth is median 12 in both blocks, so that rival is out
by measurement rather than assumption.

ESTIMAND        E1 per-arm regression of the A2 shift on the ceiling shift · E2 ⭐ is the slope 1
                and the intercept 0 · E3 ⭐ the tie mechanism, alone and joint · E4 the residual
IDENTIFICATION  within-prompt differences across two blocks about the SAME four responses;
                ⚠ if the two regressors correlate above 0.7 the round reports single-term BOUNDS
DERIVED FIRST   D1 a strict arm's attainable A2 is bounded by 1 − tie_rate · D2 the ceiling term's
                SIGN is forced, so the test is slope = 1 not slope > 0 · D3 stricter arms should be
                more tie-sensitive, a testable ordering · D4 the placebo is a numerical check
WORLDS          A reliability · B ties · C both-or-neither — B checked FIRST
CONTROLS        OBJECT · PLACEBO · POSITIVE (planted coefficient ladder with a c=0 check) ·
                NEGATIVE (pairing destroyed) · NOISE FLOOR
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
from score import load_sat, yvec, cls                                  # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R815J = ARC / "R815_the_second_construct/results/second_construct.json"
NBOOT = 1200
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


def main():
    out = {"instrument_unit": "a PROMPT", "claim_unit": "a MECHANISM"}
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
    BOTH = [p for p in allp if len(W[p]) >= 2 and p in P and len(P[p]) >= 2]
    N = len(BOTH)
    print(f"  POPULATION  {N} prompts carrying both blocks with >=2 annotators each")
    CL = {a: {p: np.array(cls(yvec(S[a][p], sorted({i for i, _ in S[a][p]})))) for p in BOTH}
          for a in ARMS}

    def per_prompt_a2(cl, tgt):
        return np.array([float((np.array(tgt[p]) == cl[p]).mean()) for p in BOTH])

    def per_prompt_ceil(tgt):
        v = np.zeros(N)
        for i, p in enumerate(BOTH):
            C = np.array(tgt[p])
            n = len(C)
            v[i] = float(np.mean([(C[a] == C[b]).mean()
                                  for a, b in itertools.combinations(range(n), 2)]))
        return v

    def per_prompt_tie(tgt):
        return np.array([float((np.array(tgt[p]) == 0).mean()) for p in BOTH])

    dC = per_prompt_ceil(P) - per_prompt_ceil(W)
    dT = per_prompt_tie(P) - per_prompt_tie(W)
    corr = float(np.corrcoef(dC, dT)[0, 1])

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK - reproduce R815's committed per-arm shifts")
    r815 = {r["arm"]: r for r in json.loads(R815J.read_text())["e1"]}
    okall = True
    for a in ("coval_core", "gen_sham"):
        d = float((per_prompt_a2(CL[a], W) - per_prompt_a2(CL[a], P)).mean())
        m = abs(d - r815[a]["diff"])
        okall &= m < 1e-6
        print(f"     {a:<14} world−personal {d:+.6f} vs R815's committed "
              f"{r815[a]['diff']:+.6f}   |Δ| {m:.2e}   {'PASS' if m < 1e-6 else 'FAIL'}")
    print(f"     CEIL_H on this population: world {per_prompt_ceil(W).mean():.6f}   "
          f"personal {per_prompt_ceil(P).mean():.6f}   gap {dC.mean():+.6f}")
    print(f"     tie rate: world {per_prompt_tie(W).mean():.6f}   "
          f"personal {per_prompt_tie(P).mean():.6f}   gap {dT.mean():+.6f}")
    if not okall:
        print("  UNRUNNABLE: R815's shifts did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"ceil_world": float(per_prompt_ceil(W).mean()),
                     "ceil_personal": float(per_prompt_ceil(P).mean()),
                     "tie_world": float(per_prompt_tie(W).mean()),
                     "tie_personal": float(per_prompt_tie(P).mean()), "n": N}

    # ================= identification gate =======================================================
    print(f"\n  IDENTIFICATION  corr(ceiling shift, tie shift) = {corr:+.4f}   "
          f"{'⛔ ABOVE 0.7 - the joint model is not separately interpretable; single-term BOUNDS '
             'are reported' if abs(corr) > 0.7 else 'below 0.7 - the joint model is admissible'}")
    joint_ok = abs(corr) <= 0.7
    out["corr"] = corr

    rng = np.random.default_rng(1234)
    idx = rng.integers(0, N, (NBOOT, N))

    def fit1(y, x, iset):
        b, a0 = np.polyfit(x, y, 1)
        bs = np.array([np.polyfit(x[i], y[i], 1)[0] for i in iset])
        return float(b), float(a0), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))

    def fit2(y, x1, x2, iset):
        X = np.column_stack([x1, x2, np.ones(len(y))])
        c = np.linalg.lstsq(X, y, rcond=None)[0]
        bs = np.array([np.linalg.lstsq(np.column_stack([x1[i], x2[i], np.ones(len(i))]),
                                       y[i], rcond=None)[0] for i in iset[:400]])
        return c, np.percentile(bs, [2.5, 97.5], axis=0)

    # ================= E1/E2/E3 ==================================================================
    print("\n  E1/E2/E3 - THREE MODELS PER ARM")
    print(f"     {'arm':<16}{'shift':>9}{'ceiling slope':>26}{'tie slope':>26}")
    rows, pv = [], []
    for a in ARMS:
        y = per_prompt_a2(CL[a], P) - per_prompt_a2(CL[a], W)
        bC, aC, loC, hiC = fit1(y, dC, idx)
        bT, aT, loT, hiT = fit1(y, dT, idx)
        r = {"arm": a, "shift": float(y.mean()), "ceil_slope": bC, "ceil_lo": loC,
             "ceil_hi": hiC, "ceil_int": aC, "tie_slope": bT, "tie_lo": loT, "tie_hi": hiT,
             "tie_int": aT}
        if joint_ok:
            c, ci = fit2(y, dC, dT, idx)
            r["joint"] = {"ceil": float(c[0]), "tie": float(c[1]), "int": float(c[2]),
                          "ceil_ci": [float(ci[0][0]), float(ci[1][0])],
                          "tie_ci": [float(ci[0][1]), float(ci[1][1])]}
            resid = y - (c[0] * dC + c[1] * dT + c[2])
        else:
            resid = y - (bC * dC + aC)
        r["resid_mean"] = float(resid.mean())
        rows.append(r)
        bs = (y - (bC * dC + aC))[idx].mean(axis=1)
        pv.append(float(2 * min((bs <= 0).mean(), (bs >= 0).mean())))
        print(f"     {a:<16}{y.mean():>+9.4f}   {bC:+.3f} [{loC:+.3f}, {hiC:+.3f}]"
              f"   {bT:+.3f} [{loT:+.3f}, {hiT:+.3f}]")
    keep = bh(pv)
    mc = float(np.mean([r["ceil_slope"] for r in rows]))
    mt = float(np.mean([r["tie_slope"] for r in rows]))
    print(f"     ⭐ mean ceiling slope {mc:+.3f}   mean tie slope {mt:+.3f}")
    ceil_contains_1 = [r for r in rows if r["ceil_lo"] <= 1 <= r["ceil_hi"]]
    print(f"     arms whose CEILING slope CI contains 1: {len(ceil_contains_1)} of {len(ARMS)}")
    tie_excl0 = [r for r in rows if r["tie_lo"] > 0 or r["tie_hi"] < 0]
    print(f"     arms whose TIE slope CI excludes 0: {len(tie_excl0)} of {len(ARMS)}")
    out["e1"] = rows
    out["means"] = {"ceil_slope": mc, "tie_slope": mt,
                    "ceil_contains_1": len(ceil_contains_1), "tie_excludes_0": len(tie_excl0)}

    # ================= D3 · stricter arms should be more tie-sensitive ===========================
    print("\n  D3 - STRICTER ARMS SHOULD BE MORE TIE-SENSITIVE (a testable ordering, not an "
          "assumption)")
    strict = {a: float(np.mean([(CL[a][p] != 0).mean() for p in BOTH])) for a in ARMS}
    ts = np.array([abs(r["tie_slope"]) for r in rows])
    sv = np.array([strict[r["arm"]] for r in rows])
    d3 = float(np.corrcoef(sv, ts)[0, 1]) if sv.std() > 0 else float("nan")
    print(f"     strictness (share of non-tied arm signs) ranges {sv.min():.3f}–{sv.max():.3f}")
    print(f"     corr(strictness, |tie slope|) = {d3:+.4f}")
    out["d3"] = {"strictness": strict, "corr": d3}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    plac = max(abs(float((per_prompt_a2(CL[a], P) - per_prompt_a2(CL[a], P)).mean()))
               for a in ARMS)
    plac_ok = plac == 0.0
    print(f"     PLACEBO   an arm against itself: {plac:.1e}   "
          f"{'PASS - identically 0' if plac_ok else 'FAIL'}")
    y0 = per_prompt_a2(CL["coval_core"], P) - per_prompt_a2(CL["coval_core"], W)
    print("     POSITIVE  plant a shift = c x (ceiling difference); the recovered slope must track c")
    rec = {}
    for c in (0.0, 0.5, 1.0, 2.0):
        yy = y0 + c * dC
        b = fit1(yy, dC, idx[:200])[0]
        rec[c] = b
        print(f"        c={c:<4} recovered slope {b:+.3f}   (unplanted {rec[0.0]:+.3f}, so "
              f"increment {b - rec[0.0]:+.3f} vs planted {c:+.3f})")
    pos_ok = all(abs((rec[c] - rec[0.0]) - c) < 0.05 for c in (0.5, 1.0, 2.0))
    g0_ok = abs(rec[0.0] - fit1(y0, dC, idx[:200])[0]) < 1e-9
    print(f"        tracks c within 0.05 at every dose: {pos_ok}   c=0 recovers the unplanted "
          f"slope exactly: {g0_ok}   {'PASS' if pos_ok and g0_ok else 'FAIL'}")
    # ⛔ THE FIRST NEGATIVE CONTROL DID NOT DESTROY WHAT IT CLAIMED TO. It permuted only the
    # `personal` side of the outcome (`a2_personal[pm] - a2_world`), so the outcome still carried
    # the UN-permuted world term and `dT` still carried the un-permuted world tie rate — and those
    # two are coupled, because an arm scores lower where humans tie more. The null came back at
    # -0.870 on the tie slope, MORE negative than the real -0.553, which is the tell: a null that
    # overshoots the observation destroyed nothing and added something. The pairing this design
    # rests on is between the REGRESSORS and the OUTCOME, so that is what the permutation breaks.
    rngn = np.random.default_rng(909)
    y_cc = per_prompt_a2(CL["coval_core"], P) - per_prompt_a2(CL["coval_core"], W)
    nulls_c, nulls_t = [], []
    for _ in range(200):
        pm = rngn.permutation(N)
        nulls_c.append(np.polyfit(dC[pm], y_cc, 1)[0])
        nulls_t.append(np.polyfit(dT[pm], y_cc, 1)[0])
    nc, nt = np.array(nulls_c), np.array(nulls_t)
    real_c = next(r["ceil_slope"] for r in rows if r["arm"] == "coval_core")
    real_t = next(r["tie_slope"] for r in rows if r["arm"] == "coval_core")
    neg_ok = (np.percentile(nc, 2.5) <= 0 <= np.percentile(nc, 97.5)
              and np.percentile(nt, 2.5) <= 0 <= np.percentile(nt, 97.5)
              and real_c > nc.max() and real_t < nt.min())
    print(f"     NEGATIVE  the regressor-to-outcome pairing destroyed, 200 draws:")
    print(f"               ceiling slope null {nc.mean():+.3f} [{np.percentile(nc, 2.5):+.3f}, "
          f"{np.percentile(nc, 97.5):+.3f}] max {nc.max():+.3f}   real {real_c:+.3f}")
    print(f"               tie slope null {nt.mean():+.3f} [{np.percentile(nt, 2.5):+.3f}, "
          f"{np.percentile(nt, 97.5):+.3f}] min {nt.min():+.3f}   real {real_t:+.3f}")
    print(f"               both nulls hold 0 AND both real slopes fall outside them: {neg_ok}   "
          f"{'PASS' if neg_ok else 'FAIL'}")
    rngh = np.random.default_rng(55)
    hs = [fit1(y0[s], dC[s], rngh.integers(0, len(s), (100, len(s))))[0]
          for s in (rngh.permutation(N)[: N // 2] for _ in range(20))]
    print(f"     NOISE FLOOR  20 half-splits: ceiling slope sd {np.std(hs):.3f}")
    gate = okall and plac_ok and pos_ok and g0_ok and neg_ok
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo_ok": plac_ok, "recovered": rec, "positive_ok": pos_ok,
                       "g0_ok": g0_ok, "negative_ok": neg_ok, "halfsplit_sd": float(np.std(hs)),
                       "gate": gate}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif not joint_ok:
        world = "C"
    elif len(tie_excl0) >= 5 and len(ceil_contains_1) < 5:
        world = "B"
    elif len(ceil_contains_1) >= 5 and len(tie_excl0) < 5:
        world = "A"
    else:
        world = "C"
    print(f"     corr {corr:+.4f} (joint admissible: {joint_ok})   ceiling CIs containing 1: "
          f"{len(ceil_contains_1)}/9   tie CIs excluding 0: {len(tie_excl0)}/9  ->  WORLD {world}")
    print(f"     ⚠ BH over the per-arm RESIDUAL family: {int(keep.sum())} of {len(pv)} survive — "
          f"and that is FORCED, not measured.")
    print(f"       An OLS residual has mean 0 by construction (R804), so this family tests a")
    print(f"       quantity the algebra fixes. It is printed because it was pre-registered, and")
    print(f"       labelled because reporting it as a finding would be the arithmetic trap.")
    out["world"] = world
    out["bh"] = [bool(x) for x in keep]

    art = HERE / "results/shift_decomposition.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
