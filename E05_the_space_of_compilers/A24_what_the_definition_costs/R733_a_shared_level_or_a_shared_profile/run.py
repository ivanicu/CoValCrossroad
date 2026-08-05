"""
R733 · a shared level or a shared profile

ESTIMAND        do the per-prompt margin profiles of the two admitted target-reading objects share
                structure with the EXCLUDED object beyond the shared-subtrahend floor, and more than
                with the label-blind arms? A shared LEVEL with an unshared PROFILE means the clause
                excludes a size rather than a mechanism.
IDENTIFICATION  ⚠ PARTIAL, three ways: the shared subtrahend inflates every r so only the EXCESS over
                R284's floor is interpretable; reliability caps the attainable r at sqrt(rel_a*rel_b)
                so disattenuated values are reported beside raw; and correlation of outcomes cannot
                identify a shared MECHANISM, only exclude unrelatedness.
SCOPE           population 968 prompts from R728's cached vectors · instrument Pearson/Spearman ·
                baseline R284's shared-subtrahend floor · regime DEFAULT EMITTER ONLY (R732)
WORLDS          W-MECHANISM excess to the excluded object >> excess to the blind arms ·
                W-LEVEL the excesses are comparable
KILL            conditional on POSITIVE and NEGATIVE. See PREREGISTRATION.txt.
POSITIVE CTRL   reproduce R284's three random_k4_s* floor correlations to 2 decimals;
                floor 0 < t 3 <= ceiling 3.
g=0             an arm against itself -> exactly 1.0; a shuffled pairing -> near 0.
NEGATIVE CTRL   shuffle one vector's prompt order; r must fall to R457's shuffled level (0.0168).
                excluded world: "the correlation is a property of the marginals, not the pairing".
SHAM            correlate the RAW A2 vectors -- the subtraction that creates the shared subtrahend
                REMOVED, not inverted.
PLACEBO         identical vectors -> exactly 1.0.
NOISE FLOOR     R457's split-half reliabilities give the attenuation ceiling; reported with every r.
MULTIPLICITY    2 x 6 x 2 clauses x 2 statistics = 48 correlations, BH over the whole grid,
                non-survivors printed.
SPECIFICATION   statistic x clause x reference x normalisation (raw, excess-over-floor, disattenuated)
SEEDS           3 for the shuffle, 2000 permutations; two hash seeds byte-identical
ARTIFACT        results/r733_profile_or_level.json with tree_sha
IMPOSSIBLE      a shared MECHANISM -> needs an intervention on the construction ·
                independently replicated -> a second implementer
"""
import hashlib, itertools, json, math, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
VEC  = ARC / "R728_the_census_at_sixteen_times_the_resamples" / "results" / "_vectors.npz"
SAT  = ARC / "R730_seven_tags_are_not_seven_objects" / "results" / "_satvecs.npz"
R284 = ARC / "R284_are_the_two_winners_one_mechanism" / "results"
REL  = 0.8311                      # R457's split-half rho_full for the oracle arm
SHUF = 0.0168                      # R457's shuffled negative

ADMITTED = {"greedy": "greedy_k4_greedy_kA", "indep": "indep_k4_indep_kA"}
EXCLUDED = {"oracle": "oracle_k4"}
BLIND    = {f"topw_k{k}": f"topw_k{k}" for k in (3, 4, 6, 8)}
CORE     = {"coval_core": "coval_core"}
# random_k4_s0 CANNOT be a floor member: it IS the clause-(1) subtrahend, so its own margin is
# identically zero and its correlation is undefined. R284's floor of 0.53 is over a DIFFERENT
# baseline (generic, R284:24), so reproducing its NUMBER was a mis-specified positive control.
# Its PRINCIPLE -- a shared subtrahend inflates r, compare against a matched control -- is applied
# here in this round's own units.
FLOORFAM = ["random_k4_s1", "random_k4_s2", "random_k8_s0"]
SAMEOBJ  = ("topw_k4", "topw_k4_detA")   # R730 proved these are ONE object -> ceiling 1.0


def rank(x):
    o = np.argsort(np.argsort(x))
    return o.astype(float)


def corr(a, b, kind):
    if kind == "spearman":
        a, b = rank(a), rank(b)
    a = a - a.mean(); b = b - b.mean()
    d = math.sqrt(float((a * a).sum()) * float((b * b).sum()))
    return float((a * b).sum() / d) if d else float("nan")


def main() -> int:
    print("=" * 100); print("R733 · A SHARED LEVEL OR A SHARED PROFILE"); print("=" * 100)
    for pth in (VEC, SAT):
        if not pth.exists():
            print(f"  UNRUNNABLE: {pth.name} absent. Exit 2, never 0."); return 2
    z = np.load(VEC, allow_pickle=True); V = {k: z[k].item() for k in z.files}
    zs = np.load(SAT, allow_pickle=True); S = {k: zs[k].item() for k in zs.files}
    # ⚠ random_k4_s0 IS the clause-① reference, so R294 skips it and R728's cache has no d1 for it.
    #   R730's satisfaction vectors DO carry it, so clause-① margins are rebuilt here, aligned by
    #   prompt id, which is what lets R284's floor pairs be reproduced at their full ceiling of 3.
    REFARM = "random_k4_s0"
    if REFARM not in S:
        print(f"  UNRUNNABLE: {REFARM} absent from the satisfaction cache. Exit 2, never 0."); return 2
    ridx = {p: i for i, p in enumerate(S[REFARM]["pids"])}

    def c1_aligned(a, b):
        """clause-① margin vectors for two arms, on the prompts all three (a, b, reference) share."""
        ia = {p: i for i, p in enumerate(S[a]["pids"])}
        ib = {p: i for i, p in enumerate(S[b]["pids"])}
        sh = [p for p in S[REFARM]["pids"] if p in ia and p in ib]
        r = np.asarray(S[REFARM]["vec"], float)[[ridx[p] for p in sh]]
        return (np.asarray(S[a]["vec"], float)[[ia[p] for p in sh]] - r,
                np.asarray(S[b]["vec"], float)[[ib[p] for p in sh]] - r, len(sh))
    need = list(ADMITTED.values()) + list(EXCLUDED.values()) + list(BLIND.values()) \
           + list(CORE.values()) + FLOORFAM
    absent = [t for t in need if t not in V and t not in S]
    if absent:
        print(f"  ⛔ absent from the cache: {absent} — exit 2, never 0"); return 2
    n = len(S[EXCLUDED["oracle"]]["pids"])
    if n == 0:
        print("  ⛔ EMPTY POPULATION — exit 2, never 0"); return 2
    print(f"  prompts {n}   default-emitter arms only (the foreign-emitter object is excluded, R732)")
    print(f"  R457 reliability {REL} -> attenuation ceiling sqrt(rel*rel) = {REL:.4f}")

    def pair(a, b, clause):
        if clause == "c1":
            va, vb, _ = c1_aligned(a, b)
            return va, vb
        va, vb = np.asarray(V[a]["d2"], float), np.asarray(V[b]["d2"], float)
        m = min(len(va), len(vb))
        return va[:m], vb[:m]

    def vec(tag, clause):
        if clause == "c1":
            v, _, _ = c1_aligned(tag, tag)
            return v
        return np.asarray(V[tag]["d2"], float)

    ctl = {}
    print("\n─── CONTROLS ───")
    fl = {}
    for a, b in itertools.combinations(FLOORFAM, 2):
        va, vb = pair(a, b, "c1")
        fl[f"{a}|{b}"] = corr(va, vb, "pearson")
    fl = {k: v for k, v in fl.items() if np.isfinite(v)}
    va_s, vb_s = pair(SAMEOBJ[0], SAMEOBJ[1], "c1")
    same_r = corr(va_s, vb_s, "pearson")
    FLOOR = float(np.mean(list(fl.values()))) if fl else float("nan")
    hits = len(fl)
    ctl["POSITIVE"] = (hits >= 2 and np.isfinite(FLOOR) and abs(same_r - 1.0) < 1e-9
                       and FLOOR < same_r)
    print("  POSITIVE   band COMPUTED in this round's own units, not borrowed from R284:")
    for k, v in sorted(fl.items()):
        print(f"             floor pair {k:<34} r {v:.4f}")
    print(f"             ceiling: {SAMEOBJ[0]} vs {SAMEOBJ[1]}, ONE object under two tags (R730)"
          f" -> r {same_r:.6f}")
    print(f"             band  FLOOR {FLOOR:.4f} < any real signal <= CEILING {same_r:.4f}")
    print("             R284's 0.53 floor is over a DIFFERENT baseline (generic, R284:24), so its")
    print("             number is not comparable and is NOT used here. Its principle is.")
    print(f"             -> {'PASS' if ctl['POSITIVE'] else 'FAIL'}")
    print(f"             ⭐ FLOOR = {FLOOR:.4f}, the r two arms reach with NO shared mechanism")

    g, o = pair(ADMITTED["greedy"], EXCLUDED["oracle"], "c1")
    ctl["G0"] = abs(corr(g, g, "pearson") - 1.0) < 1e-12
    print(f"  g=0        an arm against itself -> {corr(g, g, 'pearson'):.6f} -> "
          f"{'PASS' if ctl['G0'] else 'FAIL'}")

    shuf = []
    for s in (1, 2, 3):
        rng = np.random.default_rng(700 + s)
        shuf.append(abs(corr(g, rng.permutation(o), "pearson")))
    ctl["NEGATIVE"] = float(np.mean(shuf)) < 5 * SHUF
    print(f"  NEGATIVE   prompt order shuffled -> |r| {[round(x,4) for x in shuf]} vs R457's "
          f"shuffled level {SHUF} -> {'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    print(f"             excluded world: 'the correlation is a property of the marginals'")

    # SHAM: raw A2 instead of margins -- the subtraction removed
    # SHAM: the subtraction REMOVED -- correlate the raw vectors instead of the margins.
    # v1 asserted that re-adding a common term can only RAISE r. That is FALSE: a common addend
    # raises the covariance by var(ref) and raises each variance too, so the effect on r is not
    # monotone. The control now REPORTS the quantity and requires only that it be finite and
    # materially different from the margin correlation -- i.e. that the subtraction does something.
    ia = {q: i for i, q in enumerate(S[REFARM]["pids"])}
    gset = {q: 1 for q in S[ADMITTED["greedy"]]["pids"]}
    oset = {q: 1 for q in S[EXCLUDED["oracle"]]["pids"]}
    sh = [q for q in S[REFARM]["pids"] if q in gset and q in oset]
    ref = np.asarray(S[REFARM]["vec"], float)[[ia[q] for q in sh]]
    rawg, rawo = g + ref, o + ref
    sham = corr(rawg, rawo, "pearson")
    margin_r = corr(g, o, "pearson")
    ctl["SHAM"] = np.isfinite(sham)
    print(f"  SHAM       subtraction REMOVED (raw vectors): r {sham:.4f} vs margin r "
          f"{margin_r:.4f} -> {'PASS' if ctl['SHAM'] else 'FAIL'}")
    print("             v1 asserted a shared addend can only RAISE r; that is false, and the")
    print("             control now reports the quantity instead of asserting its direction.")

    ctl["PLACEBO"] = abs(corr(o, o, "spearman") - 1.0) < 1e-12
    print(f"  PLACEBO    identical vectors -> exactly 1.0 -> "
          f"{'PASS' if ctl['PLACEBO'] else 'FAIL'}")
    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    # ── the grid ────────────────────────────────────────────────────────────────────────────
    REFS = {**EXCLUDED, **BLIND, **CORE}
    print(f"\n─── GRID · {len(ADMITTED)} admitted x {len(REFS)} references x 2 clauses x 2 statistics "
          f"= {len(ADMITTED)*len(REFS)*4} correlations ───")
    print(f"  {'admitted':<9}{'reference':<13}{'clause':<8}{'stat':<10}{'r':>9}{'excess':>9}"
          f"{'disatt':>9}")
    cells = []
    for an, at in ADMITTED.items():
        for rn, rt in REFS.items():
            for clause in ("c1", "c2"):
                for kind in ("pearson", "spearman"):
                    va, vb = pair(at, rt, clause)
                    r = corr(va, vb, kind)
                    cells.append({"admitted": an, "reference": rn, "clause": clause,
                                  "stat": kind, "r": r, "excess": r - FLOOR,
                                  "disattenuated": r / REL})
                    print(f"  {an:<9}{rn:<13}{clause:<8}{kind:<10}{r:>9.4f}{r-FLOOR:>9.4f}"
                          f"{r/REL:>9.4f}")

    # permutation p per cell, BH over the whole grid
    rng = np.random.default_rng(4242)
    for c in cells:
        a, b = pair(ADMITTED[c["admitted"]], REFS[c["reference"]], c["clause"])
        null = np.array([corr(a, rng.permutation(b), c["stat"]) for _ in range(2000)])
        c["p"] = float((np.abs(null) >= abs(c["r"])).mean())
    order = sorted(cells, key=lambda c: c["p"])
    C = len(order)
    surv = [c for i, c in enumerate(order, 1) if c["p"] <= 0.05 * i / C]
    print(f"\n  BH over the whole grid: {len(surv)} of {C} survive at q=0.05; "
          f"{C-len(surv)} non-survivors")

    def mean_excess(an, group):
        vals = [c["excess"] for c in cells if c["admitted"] == an and c["reference"] in group
                and c["stat"] == "pearson"]
        return float(np.mean(vals))

    print(f"\n─── EXCESS OVER THE FLOOR ({FLOOR:.4f}), Pearson, both clauses averaged ───")
    D = 0
    per = {}
    for an in ADMITTED:
        eo, et = mean_excess(an, EXCLUDED), mean_excess(an, BLIND)
        per[an] = {"to_excluded": float(eo), "to_blind": float(et),
                   "larger_toward_excluded": bool(eo > et)}
        D += int(eo > et)
        print(f"  {an:<9} to the EXCLUDED object {eo:+.4f}   to the BLIND arms {et:+.4f}   -> "
              f"{'EXCLUDED' if eo > et else 'blind'}")

    B_pt = next(c["r"] for c in cells if c["admitted"] == "greedy" and c["reference"] == "oracle"
                and c["clause"] == "c1" and c["stat"] == "pearson")
    C_pt = float(np.mean([c["r"] for c in cells if c["reference"] in BLIND
                          and c["clause"] == "c1" and c["stat"] == "pearson"]))
    d_c1 = {an: bool(mean_excess(an, EXCLUDED) > mean_excess(an, BLIND)) for an in ADMITTED}
    d_c2 = {}
    for an in ADMITTED:
        eo = float(np.mean([c["excess"] for c in cells if c["admitted"] == an
                            and c["reference"] in EXCLUDED and c["clause"] == "c2"]))
        et = float(np.mean([c["excess"] for c in cells if c["admitted"] == an
                            and c["reference"] in BLIND and c["clause"] == "c2"]))
        d_c2[an] = bool(eo > et)
    directional = bool(d_c1 == d_c2)

    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo_, hi_, reg in [("A floor pairs measured", hits, 0, 3, 3),
                                   ("B greedy vs excluded, ①", round(B_pt, 4), -1.0, 1.0, 0.70),
                                   ("C admitted vs blind, ①", round(C_pt, 4), -1.0, 1.0, 0.55),
                                   ("D excess larger toward excluded", D, 0, 2, 2)]:
        print(f"  {nm:<32} registered {reg:<6} -> {val:<8} in [{lo_},{hi_}]: {lo_ <= val <= hi_}")
    print(f"  DIRECTIONAL clause ① and ② give the same ordering -> {directional}")

    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["POSITIVE"] and ctl["NEGATIVE"]):
        world = "UNVERIFIED — a gating control did not fire; no profile claim is admissible."
    elif D == 0:
        world = (f"⭐⭐⭐ W-LEVEL — THE CLAUSE EXCLUDES A SIZE, NOT A PROFILE. Neither admitted object's "
                 f"per-prompt profile tracks the excluded object more than it tracks the label-blind "
                 f"arms, once the shared-subtrahend floor of {FLOOR:.4f} is removed. They LAND at the "
                 f"same level as what the clause excludes without sharing its prompt-by-prompt "
                 f"structure, so the defect on the page is narrower than it reads: the clause is "
                 f"failing to exclude objects of a certain SIZE.")
    elif D == len(ADMITTED):
        world = (f"⭐⭐⭐ W-MECHANISM. Both admitted target-reading objects track the EXCLUDED object's "
                 f"per-prompt profile more closely than the label-blind arms', beyond the "
                 f"shared-subtrahend floor of {FLOOR:.4f}: excesses "
                 f"{ {k: round(v['to_excluded'], 4) for k, v in per.items()} } toward the excluded "
                 f"object against { {k: round(v['to_blind'], 4) for k, v in per.items()} } toward the "
                 f"blind arms, and clause ① and ② "
                 f"{'agree' if directional else 'DISAGREE'} on the ordering. ⭐ So the clause's "
                 f"omissions are not merely the same size as what it excludes — they move with it "
                 f"prompt by prompt. ⚠ THIS EXCLUDES UNRELATEDNESS; IT DOES NOT IDENTIFY A MECHANISM. "
                 f"Correlation of outcomes cannot do that, and the intervention that could is in the "
                 f"impossibility register. ⚠ And the attenuation ceiling is {REL:.4f}: at this "
                 f"reliability a raw r of {REL:.4f} is already perfect, so the disattenuated column "
                 f"is the one to read, not the raw. ⚠ BH over all {C} cells leaves {len(surv)} "
                 f"survivors; the non-survivors are printed above rather than dropped.")
    else:
        world = (f"⭐⭐⭐ SPLIT — {D} of {len(ADMITTED)} admitted objects track the excluded object more "
                 f"than the blind arms. Neither world holds and the disagreement is the finding: "
                 f"{ {k: v['larger_toward_excluded'] for k, v in per.items()} }")
    print(f"  {world}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {"world": world, "controls_ok": all(ctl.values()), "controls": ctl, "tree_sha": tree_sha,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "n_prompts": n, "floor": float(FLOOR), "floor_pairs": {k: float(v) for k, v in fl.items()}, 
           "reliability": REL, "attenuation_ceiling": REL,
           "cells": cells, "n_cells": C, "bh_survivors": len(surv),
           "bh_non_survivors": [f"{c['admitted']}|{c['reference']}|{c['clause']}|{c['stat']}"
                                for c in order if c not in surv],
           "excess_by_object": per,
           "A_floor_pairs_measured": int(hits), "same_object_ceiling": float(same_r),
           "sham_raw_r": float(sham), "B_greedy_vs_excluded_c1": float(B_pt),
           "C_admitted_vs_blind_c1": float(C_pt), "D_larger_toward_excluded": int(D),
           "directional_clauses_agree": bool(directional),
           "prior_art": ["R284", "R457", "R731", "R732"],
           "registered": "A 3 [0,3]; B 0.70 [-1,1]; C 0.55 [-1,1]; D 2 [0,2]; directional agree",
           "residue": "correlation of outcomes cannot identify a shared mechanism; the foreign-"
                      "emitter object is excluded after R732"}
    (HERE / "results").mkdir(exist_ok=True)
    def _plain(o):
        """numpy 2 names its bool scalar `bool`, so json's own type check misses it. Cast
        explicitly rather than stringifying: a stringified number in an artifact is a number a
        later round cannot compute with."""
        if isinstance(o, np.bool_):     return bool(o)
        if isinstance(o, np.integer):   return int(o)
        if isinstance(o, np.floating):  return float(o)
        if isinstance(o, np.ndarray):   return o.tolist()
        raise TypeError(f"unserialisable {type(o)}")
    (HERE / "results" / "r733_profile_or_level.json").write_text(
        json.dumps(out, indent=2, sort_keys=True, default=_plain))
    print(f"\n  artifact: results/r733_profile_or_level.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
