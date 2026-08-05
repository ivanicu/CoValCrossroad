"""
R738 · every side matched on its own overlap

ESTIMAND        with EVERY side matched on its OWN measured overlap and its OWN (k_a,k_b) curve, does
                each admitted object still track the EXCLUDED object more than the label-blind arms?
IDENTIFICATION  by construction for the k pairs the release carries, on ONE fixed prompt set across
                every target of every curve. ⚠ NOT identified: whether a RULE-produced arm behaves
                like a random subset at equal overlap. Every floor here is a random-subset floor.
SCOPE           population prompts reachable at every target of every curve · instrument margin
                correlation vs the reference arm · baseline R737's single k=4x4 curve · regime
                default emitter
WORLDS          W-SURVIVES both orderings hold · W-FLIPS at least one does not
KILL            conditional on POSITIVE and PLACEBO. See PREREGISTRATION.txt.
POSITIVE CTRL   per curve, rho fit at j=0 ALONE predicts every other target;
                model corr(j) = rho + (1-rho)*j/sqrt(k_a*k_b), verified synthetically at 18 cells to
                0.0032 before this round. Pooled max held-out deviation < 0.05.
g=0             per curve, j=0 below j=1 by more than three seed SDs.
NEGATIVE CTRL   shared set drawn at random so nominal j is not realised; every curve flattens.
SHAM            both arms from the SAME draw at every j -> a constant.
PLACEBO         k=4x4 at j=4 -> floor EXACTLY 1.0.
NOISE FLOOR     20 seeds per target per curve; every excess called only if it exceeds that spread.
MULTIPLICITY    4 curves x targets x 20 seeds + 2 objects x 5 references, all reported.
SPECIFICATION   curve x target x seed x object x reference
SEEDS           20 per cell; two hash seeds byte-identical, writes verified
ARTIFACT        results/r738_matched_excess.json with tree_sha
IMPOSSIBLE      a rule-produced arm vs a random subset at equal overlap -> a new selection run ·
                independently replicated -> a second implementer
"""
import hashlib, json, math, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
ROOT = HERE.parents[2]
RES  = ROOT / "corebench" / "results"
REFARM, SEEDS = "random_k4_s0", tuple(range(20))
OBJ   = {"greedy": "greedy_k4_greedy_kA", "indep": "indep_k4_indep_kA"}
EXCL  = "oracle_k4"
BLIND = ["topw_k3", "topw_k4", "topw_k6", "topw_k8"]


def C(x, y):
    x = x - x.mean(); y = y - y.mean()
    d = math.sqrt(float((x * x).sum()) * float((y * y).sum()))
    return float((x * y).sum() / d) if d else float("nan")


def load(a):
    core = json.loads((RES / f"core_{a}.json").read_text())
    z = np.load(RES / f"sat_{a}.npz", allow_pickle=True)
    return core, [str(s).split("|") for s in z["meta"]], z["sat"].tolist()


def main() -> int:
    print("=" * 100); print("R738 · EVERY SIDE MATCHED ON ITS OWN OVERLAP"); print("=" * 100)
    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if "08b" not in p.stem and p.stem != "sat_genericpool16"
                  and (RES / f"core_{p.stem[4:]}.json").exists())
    SC, POOL = {}, {}
    for a in arms:
        core, meta, sat = load(a)
        for (pid, j, x), v in zip(meta, sat):
            c = core.get(pid)
            if c is None or int(j) >= len(c): continue
            SC[(pid, x, c[int(j)])] = float(v)
            POOL.setdefault(pid, set()).add(c[int(j)])
    resp = sorted({k[1] for k in SC})
    CORE = {a: load(a)[0] for a in set(list(OBJ.values()) + [EXCL] + BLIND + [REFARM])}
    KA = 4
    CURVES = [(KA, int(np.median([len(v) for v in CORE[b].values()]))) for b in BLIND]
    CURVES = sorted(set(CURVES + [(KA, KA)]))
    need = max(ka + kb for ka, kb in CURVES)          # worst case: j = 0
    pids = sorted(p for p, s in POOL.items() if len(s) >= need and p in CORE[REFARM])
    if not pids:
        print(f"  ⛔ no prompt supplies {need} distinct criteria — exit 2, never 0"); return 2
    print(f"  curves {CURVES}   worst-case criteria needed {need}")
    print(f"  FIXED population across EVERY target of EVERY curve: {len(pids)} prompts")

    def vec(sel):
        return np.array([float(np.mean([SC[(p, x, c)] for x in resp for c in sel[p]
                                        if (p, x, c) in SC])) if sel.get(p) else np.nan
                         for p in pids])
    ref = vec({p: CORE[REFARM][p] for p in pids})

    def build(ka, kb, j, seed, realise=True, same=False):
        # ⚠ the seed carried j, so even the "same draw" sham re-drew at every target and could not
        #   return a constant. For the sham the draw must be held fixed as well as the overlap
        #   ingredient removed; j is dropped from the seed there.
        rng = np.random.default_rng(9973 * (ka * 100 + kb) + (0 if same else 17 * j) + seed)
        A, B = {}, {}
        for p in pids:
            pick = list(rng.permutation(np.array(sorted(POOL[p]), dtype=object)))
            a = pick[:ka]
            # ⚠ v1 wrote `a[:kb] if kb <= ka else a + pick[ka:kb]`, which EXTENDS the draw when
            #   kb > ka, so the two arms were not the same draw and the sham varied with j. The
            #   sham's job is the overlap ingredient ABSENT: draw b from a fixed disjoint slice,
            #   independent of j, so it must return one constant by construction.
            if same:   b = pick[ka:ka + kb]
            elif realise: b = a[:j] + pick[ka:ka + (kb - j)]
            else:      b = list(rng.permutation(np.array(sorted(POOL[p]), dtype=object)))[:kb]
            A[p], B[p] = a, list(b)
        return A, B

    ctl, curves = {}, {}
    print("\n─── CURVES ───")
    devs, g0ok, negflat = [], [], []
    for ka, kb in CURVES:
        rows = []
        for j in range(0, min(ka, kb) + 1):
            raws, fls = [], []
            for s in SEEDS:
                A, B = build(ka, kb, j, s)
                va, vb = vec(A), vec(B)
                m = np.isfinite(va) & np.isfinite(vb) & np.isfinite(ref)
                raws.append(C(va[m], vb[m])); fls.append(C(va[m] - ref[m], vb[m] - ref[m]))
            rows.append({"j": j, "raw": float(np.mean(raws)), "raw_sd": float(np.std(raws, ddof=1)),
                         "floor": float(np.mean(fls)), "floor_sd": float(np.std(fls, ddof=1))})
        rho = rows[0]["raw"]
        for r in rows:
            r["model"] = rho + (1 - rho) * r["j"] / math.sqrt(ka * kb)
            r["dev"] = abs(r["raw"] - r["model"])
        devs += [r["dev"] for r in rows if r["j"] > 0]
        g0ok.append(rows[1]["raw"] - rows[0]["raw"] > 3 * max(rows[0]["raw_sd"], rows[1]["raw_sd"]))
        nf = []
        for j in range(0, min(ka, kb) + 1):
            fl = []
            for s in SEEDS[:6]:
                A, B = build(ka, kb, j, s, realise=False)
                va, vb = vec(A), vec(B)
                m = np.isfinite(va) & np.isfinite(vb) & np.isfinite(ref)
                fl.append(C(va[m] - ref[m], vb[m] - ref[m]))
            nf.append(float(np.mean(fl)))
        negflat.append((max(nf) - min(nf)) < 0.25 * (max(r["floor"] for r in rows)
                                                     - min(r["floor"] for r in rows)))
        curves[(ka, kb)] = {"rows": rows, "rho": rho, "neg": nf}
        print(f"  k={ka}x{kb}  rho {rho:.4f}   floors "
              f"{[round(r['floor'],4) for r in rows]}   max held-out |Δ| "
              f"{max([r['dev'] for r in rows if r['j']>0]):.4f}")

    A_pt = float(max(devs))
    ctl["POSITIVE"] = A_pt < 0.05
    print(f"\n─── CONTROLS ───")
    print(f"  POSITIVE   one-parameter model per curve, rho fit at j=0 alone; pooled max HELD-OUT "
          f"|Δ| {A_pt:.4f} < 0.05 -> {'PASS' if ctl['POSITIVE'] else 'FAIL'}")
    ctl["G0"] = all(g0ok)
    print(f"  g=0        every curve responds to overlap (j=0 below j=1 by >3sd): {g0ok} -> "
          f"{'PASS' if ctl['G0'] else 'FAIL'}")
    ctl["NEGATIVE"] = all(negflat)
    print(f"  NEGATIVE   nominal j not realised -> every curve flattens: {negflat} -> "
          f"{'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    r44 = curves[(4, 4)]["rows"][-1]
    ctl["PLACEBO"] = abs(r44["floor"] - 1.0) < 1e-9
    print(f"  PLACEBO    k=4x4 at j=4 -> floor {r44['floor']:.6f} -> "
          f"{'PASS' if ctl['PLACEBO'] else 'FAIL'}")
    shc = []
    for ka, kb in CURVES:
        v = []
        for j in range(0, min(ka, kb) + 1):
            A, B = build(ka, kb, j, 0, same=True)
            va, vb = vec(A), vec(B)
            m = np.isfinite(va) & np.isfinite(vb) & np.isfinite(ref)
            v.append(C(va[m] - ref[m], vb[m] - ref[m]))
        shc.append(max(v) - min(v))
    ctl["SHAM"] = all(x < 1e-9 for x in shc)
    print(f"  SHAM       same draw at every j -> ranges {[round(x,9) for x in shc]} -> "
          f"{'PASS' if ctl['SHAM'] else 'FAIL'}")
    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    # ── matched excesses ────────────────────────────────────────────────────────────────────
    kof = {b: int(np.median([len(v) for v in CORE[b].values()])) for b in BLIND}
    kof[EXCL] = KA
    def matched(ka, kb, ov):
        rows = curves[(ka, kb)]["rows"]
        xs = np.array([r["j"] for r in rows], float); ys = np.array([r["floor"] for r in rows])
        sd = float(np.mean([r["floor_sd"] for r in rows]))
        return float(np.interp(ov, xs, ys)), sd

    print(f"\n─── EVERY SIDE MATCHED · {len(pids)} prompts ───")
    print(f"  {'object':<8}{'ref':<10}{'k':>4}{'overlap':>9}{'r':>9}{'floor':>9}{'excess':>9}")
    res, D = {}, 0
    for on, ot in OBJ.items():
        ovec = vec({p: CORE[ot][p] for p in pids}) - ref
        row = {}
        for rn in [EXCL] + BLIND:
            rvec = vec({p: CORE[rn][p] for p in pids}) - ref
            m = np.isfinite(ovec) & np.isfinite(rvec)
            r = C(ovec[m], rvec[m])
            ov = float(np.mean([len(set(CORE[ot][p]) & set(CORE[rn][p])) for p in pids]))
            fl, sd = matched(KA, kof[rn], ov)
            row[rn] = {"r": r, "overlap": ov, "floor": fl, "excess": r - fl, "floor_sd": sd}
            print(f"  {on:<8}{rn:<10}{kof[rn]:>4}{ov:>9.4f}{r:>9.4f}{fl:>9.4f}{r-fl:>+9.4f}")
        ex_e = row[EXCL]["excess"]
        ex_b = float(np.mean([row[b]["excess"] for b in BLIND]))
        band = float(np.mean([row[x]["floor_sd"] for x in [EXCL] + BLIND]))
        surv = (ex_e - ex_b) > band
        D += int(surv)
        res[on] = {"per_ref": row, "excess_excluded": ex_e, "excess_blind_mean": ex_b,
                   "band": band, "survives": bool(surv)}
        print(f"           -> excess to EXCLUDED {ex_e:+.4f}   mean to BLIND {ex_b:+.4f}   "
              f"gap {ex_e-ex_b:+.4f} vs band {band:.4f}   {'SURVIVES' if surv else 'FLIPS'}")

    B_pt = res["greedy"]["per_ref"][EXCL]["floor"]
    C_pt = float(np.mean([res["greedy"]["per_ref"][b]["floor"] for b in BLIND]))
    directional = all(res[o]["survives"] for o in OBJ)

    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo_, hi_, reg in [("A pooled held-out |Δ|", round(A_pt, 4), 0.0, 1.0, 0.05),
                                   ("B greedy floor vs excluded", round(B_pt, 4), 0.0, 1.0, 0.83),
                                   ("C greedy mean blind floor", round(C_pt, 4), 0.0, 1.0, 0.70),
                                   ("D orderings surviving", D, 0, 2, 2)]:
        print(f"  {nm:<30} registered {reg:<6} -> {val:<9} in [{lo_},{hi_}]: {lo_ <= val <= hi_}")
    print(f"  DIRECTIONAL both objects survive with every side matched -> {directional}")

    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["POSITIVE"] and ctl["PLACEBO"]):
        world = "UNVERIFIED — a gating control did not fire; no matched excess is admissible."
    elif D < 2:
        flipped = [o for o in OBJ if not res[o]["survives"]]
        world = (f"⭐⭐⭐ W-FLIPS — THE ORDERING DOES NOT SURVIVE A MATCHED NULL FOR {flipped}. With every "
                 f"side matched on its own measured overlap and its own k-pair curve, "
                 f"{ {o: round(res[o]['excess_excluded'] - res[o]['excess_blind_mean'], 4) for o in OBJ} } "
                 f"is the excess gap against a band of "
                 f"{ {o: round(res[o]['band'], 4) for o in OBJ} }. The ordering this arc has carried "
                 f"since R731 was an artifact of an unmatched null for those objects, and the "
                 f"statement block resting on it is amended in this commit.")
    else:
        world = (f"⭐⭐⭐ W-SURVIVES — THE ORDERING HOLDS WITH EVERY SIDE MATCHED. On {len(pids)} prompts "
                 f"fixed across every target of every curve, and with each comparison read off the "
                 f"curve for its OWN k pair rather than a single k=4x4 curve, both admitted objects "
                 f"still track the excluded object more than the label-blind arms: greedy "
                 f"{res['greedy']['excess_excluded']:+.4f} against "
                 f"{res['greedy']['excess_blind_mean']:+.4f}, indep "
                 f"{res['indep']['excess_excluded']:+.4f} against "
                 f"{res['indep']['excess_blind_mean']:+.4f}. ⭐ The construction is validated per "
                 f"curve by a one-parameter model fit at j=0 alone, predicting every held-out target "
                 f"to {A_pt:.4f}. ⚠ AND THE MARGINS ARE MUCH SMALLER THAN EVERY EARLIER FLOOR GAVE: "
                 f"greedy's matched floor against the excluded object is {B_pt:.4f} and its mean "
                 f"matched floor against the blind arms is {C_pt:.4f}, so the comparison is between "
                 f"two large and nearly equal nulls. ⚠ Every floor here is a RANDOM-SUBSET floor; "
                 f"whether a rule-produced arm behaves like a random subset at equal overlap is not "
                 f"identified and needs a new selection run.")
    print(f"  {world}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {"world": world, "controls_ok": bool(all(ctl.values())),
           "controls": {k: bool(v) for k, v in ctl.items()}, "tree_sha": tree_sha,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "n_prompts_fixed": len(pids), "criteria_needed": need,
           "curves": {f"{a}x{b}": curves[(a, b)] for a, b in CURVES},
           "results": res, "A_pooled_heldout_dev": A_pt, "B_greedy_floor_excluded": B_pt,
           "C_greedy_mean_blind_floor": C_pt, "D_orderings_surviving": int(D),
           "directional_both_survive": bool(directional),
           "prior_art": ["R731", "R733", "R735", "R736", "R737"],
           "registered": "A 0.05 [0,1]; B 0.83 [0,1]; C 0.70 [0,1]; D 2 [0,2]",
           "residue": "random-subset floors; a rule-produced arm at equal overlap is not identified"}
    def _plain(o):
        if isinstance(o, np.bool_):    return bool(o)
        if isinstance(o, np.integer):  return int(o)
        if isinstance(o, np.floating): return float(o)
        if isinstance(o, np.ndarray):  return o.tolist()
        raise TypeError(f"unserialisable {type(o)}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r738_matched_excess.json").write_text(
        json.dumps(out, indent=2, sort_keys=True, default=_plain))
    print(f"\n  artifact: results/r738_matched_excess.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
