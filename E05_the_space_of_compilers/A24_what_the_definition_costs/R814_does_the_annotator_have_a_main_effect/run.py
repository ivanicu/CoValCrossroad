#!/usr/bin/env python3
"""R814 · does the annotator have a main effect — is clause ③ holding out the right thing?

R813's NEXT called it a tension that annotators agree pairwise only 0.551880 of the time while their
errors look independent. CHECK #416 killed that framing with a three-line gauge test on zero real
data: at planted rater_sd = 0.0 / 0.15 / 0.35 the pairwise agreement is 0.6230 / 0.6244 / 0.6223 —
FLAT — while the rater ICC goes 0.0002 / 0.1751 / 0.3803. The two quantities are independent and
there was never a tension. But the underlying question is decision-relevant: clause ③ holds out the
ANNOTATOR, and if annotators have no main effect that holdout is aimed at a near-empty source.

ESTIMAND        E1 excess variance of annotator means over a label-permutation null · E2 ⭐ the rater
                share · E3 ⭐ a planted dose-response · E4 what clause ③ buys, as a number
IDENTIFICATION  the permutation removes the rater main effect and preserves the rest; E3 builds the
                rival's world synthetically because a bare permutation says "did it matter", not why
DERIVED FIRST   D1 a negative excess is noise, reported as 0 with its interval · D2 pairwise
                agreement is INVARIANT to the rater effect, so CEIL_H is evidence for neither side ·
                D3 loads vary, so weighted and unweighted are both reported · D4 the residual
                absorbs the interaction, so a small rater share means no ADDITIVE main effect and
                NOT that annotators are interchangeable
WORLDS          A no main effect · B real main effect · C between — B checked FIRST
CONTROLS        OBJECT (CEIL_H 0.551880 from this round's own table) · PLACEBO · POSITIVE (dose
                0/0.02/0.05/0.10/0.20, must not fire at g=0) · NEGATIVE (500-draw permutation null)
                · NOISE FLOOR (20 annotator half-splits)
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
from score import load_sat, cls                                        # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
PR = list(itertools.combinations(range(4), 2))
NPERM = 500
DOSES = [0.0, 0.02, 0.05, 0.10, 0.20]


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


def parse_ranking(s):
    sc = {}
    for lvl, grp in enumerate(s.split(">")):
        for tok in grp.split("="):
            tok = tok.strip()
            if tok in "ABCD":
                sc[tok] = -lvl
    return [sc[c] for c in "ABCD"] if len(sc) == 4 else None


def main():
    out = {"instrument_unit": "a (prompt, annotator) judgement", "claim_unit": "the ANNOTATOR panel"}
    print("  loading assessments WITH annotator identity")
    per = {}
    for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        rows = []
        for a in r["metadata"].get("assessments", []):
            aid = a.get("annotator_id")
            for e in (a.get("ranking_blocks") or {}).get("world") or []:
                y = parse_ranking(e.get("ranking") or "")
                if y and aid:
                    rows.append((aid, np.array(cls(np.array(y, float)))))
        if rows:
            per[r["prompt_id"]] = rows
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids_all = sorted(set(per) & set(base))
    pids = [p for p in pids_all if len(per[p]) >= 2]
    dropped = len(pids_all) - len(pids)
    print(f"  POPULATION  {len(pids_all)} prompts; carrying the leave-one-out statistic: {len(pids)}"
          f"; dropped for <2 annotators: {dropped} ({100 * dropped / max(len(pids_all), 1):.1f}%)")
    if dropped / max(len(pids_all), 1) > 0.10:
        print("  UNVERIFIED: more than 10% of prompts cannot carry the statistic. Exit 2.")
        return 2

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK - reproduce R793's CEIL_H from THIS round's assessment table")
    ch = []
    for p in pids:
        C = np.array([c for _, c in per[p]])
        n = len(C)
        m = np.array([[float((C[i] == C[j]).mean()) for j in range(n)] for i in range(n)])
        iu = np.triu_indices(n, 1)
        ch.append(m[iu].mean())
    CEIL_H = float(np.mean(ch))
    ok = abs(CEIL_H - 0.551880) < 1e-6
    print(f"     CEIL_H {CEIL_H:.6f} vs R793's committed 0.551880   {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: the one committed number this table can anchor did not reproduce. "
              "Exit 2, never 0.")
        return 2
    out["object"] = {"ceil_h": CEIL_H, "prompts": len(pids), "dropped": dropped}

    # ---- the (prompt, annotator) leave-one-out agreement table ---------------------------------
    aid_index, rows_p, rows_a, agree = {}, [], [], []
    for i, p in enumerate(pids):
        C = [c for _, c in per[p]]
        A = [a for a, _ in per[p]]
        n = len(C)
        for t in range(n):
            v = float(np.mean([(C[t] == C[o]).mean() for o in range(n) if o != t]))
            rows_p.append(i)
            rows_a.append(aid_index.setdefault(A[t], len(aid_index)))
            agree.append(v)
    rows_p = np.array(rows_p)
    rows_a = np.array(rows_a)
    agree = np.array(agree)
    NA = len(aid_index)
    load = np.bincount(rows_a, minlength=NA)
    print(f"  table: {len(agree)} (prompt, annotator) cells · {NA} annotators · load median "
          f"{np.median(load):.0f} max {load.max()}")

    def rater_share(v, ra, weighted=True):
        """excess variance of annotator means over the permutation null, as a share of total."""
        s = np.bincount(ra, weights=v, minlength=NA)
        c = np.bincount(ra, minlength=NA).astype(float)
        ok_ = c > 0
        mu = s[ok_] / c[ok_]
        w = c[ok_] if weighted else np.ones(ok_.sum())
        gm = float((mu * w).sum() / w.sum())
        return float((w * (mu - gm) ** 2).sum() / w.sum()), float(v.var())

    def statistic(v, weighted=True, nperm=NPERM, seed=101, ra=None):
        ra = rows_a if ra is None else ra          # the noise floor subsets BOTH v and ra
        obs, tot = rater_share(v, ra, weighted)
        rng = np.random.default_rng(seed)
        nulls = np.array([rater_share(v, rng.permutation(ra), weighted)[0]
                          for _ in range(nperm)])
        excess = obs - nulls.mean()
        return {"obs": obs, "null_mean": float(nulls.mean()), "null_sd": float(nulls.std()),
                "null_lo": float(np.percentile(nulls, 2.5)),
                "null_hi": float(np.percentile(nulls, 97.5)),
                "excess": excess, "total": tot,
                "share": max(excess, 0.0) / max(tot, 1e-12),
                "raw_share": excess / max(tot, 1e-12),
                "fires": bool(obs > np.percentile(nulls, 97.5))}

    # ================= E1/E2 =====================================================================
    print("\n  E1/E2 - THE RATER MAIN EFFECT AGAINST A LABEL-PERMUTATION NULL")
    R = {w: statistic(agree, weighted=w) for w in (True, False)}
    for w in (True, False):
        r = R[w]
        print(f"     {'weighted' if w else 'unweighted':<11} observed var of annotator means "
              f"{r['obs']:.6f}   null {r['null_mean']:.6f} [{r['null_lo']:.6f}, "
              f"{r['null_hi']:.6f}]")
        print(f"     {'':<11} excess {r['excess']:+.6f}   total var {r['total']:.6f}   "
              f"⭐ RATER SHARE {100 * r['share']:.2f}%   above the null band: {r['fires']}")
    print(f"     D1 a negative excess is noise and is reported as 0: raw shares "
          f"{100 * R[True]['raw_share']:+.2f}% / {100 * R[False]['raw_share']:+.2f}%")
    out["e1"] = {("weighted" if w else "unweighted"): R[w] for w in (True, False)}

    # ================= E3 · the dose-response ====================================================
    print("\n  E3 - PLANTED RATER OFFSETS")
    print("     ⛔ THE FIRST g=0 CHECK WAS MIS-SPECIFIED. It required the OBSERVED table not to fire")
    print("     at g=0 — which PRESUMES the real data has no rater effect, the very thing under")
    print("     test. realstat §4's 'the control presupposes a non-null effect', in mirror. A true")
    print("     zero exists only on a RATER-NULLED table, so the ladder is run on both.")
    rngp = np.random.default_rng(7)
    off = rngp.normal(0, 1, NA)
    nulled = agree[np.random.default_rng(31337).permutation(len(agree))]   # rater effect destroyed
    dose, dose0 = {}, {}
    print(f"     {'g':>6}{'OBSERVED table':>20}{'RATER-NULLED table':>24}")
    for g in DOSES:
        v = np.clip(agree + g * off[rows_a], 0.0, 1.0)
        v0 = np.clip(nulled + g * off[rows_a], 0.0, 1.0)
        d = statistic(v, weighted=True, nperm=200, seed=202)
        d0 = statistic(v0, weighted=True, nperm=200, seed=203)
        dose[g], dose0[g] = d, d0
        print(f"     {g:>6}{100 * d['share']:>13.2f}% {str(d['fires']):>5}"
              f"{100 * d0['share']:>17.2f}% {str(d0['fires']):>5}")
    mono = all(dose[DOSES[i]]["share"] <= dose[DOSES[i + 1]]["share"] + 1e-12
               for i in range(len(DOSES) - 1))
    mono0 = all(dose0[DOSES[i]]["share"] <= dose0[DOSES[i + 1]]["share"] + 1e-12
                for i in range(len(DOSES) - 1))
    g0_ok = (not dose0[0.0]["fires"]) and dose0[0.2]["fires"]
    print(f"     monotone on the observed table: {mono}   on the nulled table: {mono0}")
    print(f"     ⭐ g=0 CHECK, correctly specified: the RATER-NULLED table does NOT fire at g=0 "
          f"({dose0[0.0]['fires']}) and DOES at g=0.2 ({dose0[0.2]['fires']})   "
          f"{'PASS - the control can fail' if g0_ok else 'FAIL'}")
    out["e3"] = {"observed": {str(g): dose[g] for g in DOSES},
                 "rater_nulled": {str(g): dose0[g] for g in DOSES}}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    plac = rater_share(agree, rows_a)[0] - rater_share(agree, rows_a)[0]
    plac_ok = plac == 0.0
    print(f"     PLACEBO   the statistic against ITSELF: {plac:.1e}   "
          f"{'PASS - exactly 0' if plac_ok else 'FAIL'}")
    print(f"     NEGATIVE  the permutation null itself, {NPERM} draws: mean "
          f"{R[True]['null_mean']:.6f}  sd {R[True]['null_sd']:.6f}  "
          f"95% [{R[True]['null_lo']:.6f}, {R[True]['null_hi']:.6f}]")
    print(f"               the null has SPREAD (sd > 0): {R[True]['null_sd'] > 0}")
    rngh = np.random.default_rng(55)
    hs = []
    for _ in range(20):
        keep = rngh.permutation(NA)[: NA // 2]
        mask = np.isin(rows_a, keep)
        ra2 = rows_a[mask]
        hs.append(statistic(agree[mask], weighted=True, nperm=60,
                            seed=int(rngh.integers(1e6)), ra=ra2)["share"])
    print(f"     NOISE FLOOR  20 half-splits of the annotator panel: share "
          f"{100 * np.mean(hs):.2f}% ± {100 * np.std(hs):.2f}%")
    gate = ok and plac_ok and mono and g0_ok and R[True]["null_sd"] > 0
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo_ok": plac_ok, "monotone": mono, "g0_ok": g0_ok,
                       "null_sd": R[True]["null_sd"], "halfsplit_mean": float(np.mean(hs)),
                       "halfsplit_sd": float(np.std(hs)), "gate": gate}

    # ================= E4 · what clause ③ buys ===================================================
    print("\n  E4 - WHAT CLAUSE ③ BUYS")
    sh = R[True]["share"]
    print(f"     an annotator holdout can remove at most the RATER share of the variance in this")
    print(f"     table: {100 * sh:.2f}%. The remaining {100 * (1 - sh):.2f}% is prompt plus")
    print(f"     interaction, and D4 says the residual absorbs the interaction — so a small share")
    print(f"     means no ADDITIVE main effect, NOT that annotators are interchangeable.")
    out["e4"] = {"share": sh, "remainder": 1 - sh}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif sh > 0.10 and R[True]["fires"]:
        world = "B"
    elif sh < 0.02 or not R[True]["fires"]:
        world = "A"
    else:
        world = "C"
    print(f"     rater share {100 * sh:.2f}%   above the null band: {R[True]['fires']}"
          f"  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/rater_main_effect.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
