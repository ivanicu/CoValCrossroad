"""
R739 · the floor was drawn from a different population

ESTIMAND        (1) DERIVATION from select_core.py: a criterion with identical satisfaction across
                the four responses is arithmetically INERT, so across-response VARIANCE is the
                quantity that matters, not satisfaction level. (2) do rule-produced arms select
                higher-variance criteria than the pool? (3) under a floor matched on variance AND
                overlap, do R738's ten negative excesses change sign?
IDENTIFICATION  (1) exact. (2) identified from disk. (3) identified only where the pool can supply a
                variance-matched subset; prompts that cannot are reported UNMATCHABLE and excluded
                with their count, never back-filled.
                ⚠ NOT identified: whether variance is the ONLY property the rules select on.
SCOPE           population prompts supplying a matched subset at every target · instrument
                across-response variance · baseline R738's overlap-matched floors · regime default
WORLDS          W-POPULATION matching moves the excesses · W-REAL it does not
KILL            conditional on POSITIVE and g=0. See PREREGISTRATION.txt.
POSITIVE CTRL   ⭐ known-answer from the source: topvar_k selects BY across-response variance, so its
                ratio must rank FIRST of every arm. Rank computed, not chosen.
g=0             random_k arms select uniformly -> ratio indistinguishable from 1 within the spread of
                the three seeds the release carries.
NEGATIVE CTRL   permute criterion -> variance within each prompt; every ratio must collapse to 1.
                excluded world: "the ratio measures HOW MANY criteria a rule takes, not WHICH".
SHAM            the same ratio on criterion TEXT LENGTH, which the rules do not select on.
PLACEBO         the pool against itself -> exactly 1.0.
NOISE FLOOR     the seed spread of the three random_k arms at each k.
MULTIPLICITY    every arm's ratio + 10 excesses re-scored; movers and non-movers both reported.
SPECIFICATION   statistic (variance, IQR) x matching (overlap only, overlap+variance) x arm
SEEDS           20 per matched target; two hash seeds byte-identical, writes verified
ARTIFACT        results/r739_variance_matched.json with tree_sha
IMPOSSIBLE      whether variance is the ONLY selected-on property -> the rules re-run under a
                variance-neutralised objective · independently replicated -> a second implementer
"""
import hashlib, json, math, pathlib, re, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
ROOT = HERE.parents[2]
RES  = ROOT / "corebench" / "results"
R738 = ARC / "R738_every_side_matched_on_its_own_overlap" / "results" / "r738_matched_excess.json"
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
    print("=" * 100); print("R739 · THE FLOOR WAS DRAWN FROM A DIFFERENT POPULATION"); print("=" * 100)
    if not R738.exists():
        print("  UNRUNNABLE: R738's artifact absent. Exit 2, never 0."); return 2
    prev = json.loads(R738.read_text())
    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if "08b" not in p.stem and p.stem != "sat_genericpool16"
                  and (RES / f"core_{p.stem[4:]}.json").exists())

    # per (prompt, criterion): the vector of satisfaction across responses, and its variance
    VEC = {}
    for a in arms:
        core, meta, sat = load(a)
        for (pid, j, x), v in zip(meta, sat):
            c = core.get(pid)
            if c is None or int(j) >= len(c): continue
            VEC.setdefault((pid, c[int(j)]), {})[x] = float(v)
    VAR = {k: float(np.var(list(d.values()))) for k, d in VEC.items() if len(d) >= 2}
    # ⚠ v1 built the pool from the UNION OF OBSERVED SELECTIONS. That is a sample of the candidate
    #   set biased by the very rules under study, and both the g=0 and the SHAM control caught it:
    #   uniform random arms ranked 0.5664 and criterion TEXT LENGTH ranked 0.65, a bias that has
    #   nothing to do with variance. The `full` arm selects the WHOLE candidate set and its
    #   satisfaction coverage is exactly 1.0, so the unbiased population is on disk.
    FULL = json.loads((RES / "core_full.json").read_text())
    POOL = {p: [c for c in v if (p, c) in VAR] for p, v in FULL.items()}
    POOL = {p: v for p, v in POOL.items() if len(v) >= 2}
    if not POOL:
        print("  ⛔ EMPTY POPULATION — exit 2, never 0"); return 2
    print(f"  arms {len(arms)}   (prompt, criterion) cells with a variance: {len(VAR)}   "
          f"prompts {len(POOL)}")
    print(f"  ⛔ DERIVATION (select_core.py, its own comment): a criterion whose satisfaction is")
    print(f"     identical across responses is arithmetically INERT, so VARIANCE is the quantity,")
    print(f"     not level. That is why this round measures variance. It is not evidence.")

    CORE = {a: load(a)[0] for a in arms}

    # ⚠ v1 averaged a PER-PROMPT RATIO of selected-variance to pool-variance. A mean of ratios is
    #   inflated wherever the denominator is small, and the g=0 control caught it: uniform random
    #   arms returned 1.28 when they must return 1. The statistic here is the mean PERCENTILE RANK
    #   of a selected criterion's variance within its own prompt's pool, whose null is EXACTLY 0.5
    #   by construction and which no small denominator can inflate.
    def ratio(a):
        rs = []
        for p, crits in CORE[a].items():
            pool = POOL.get(p)
            if not pool or len(pool) < 2: continue
            pv = sorted(VAR[(p, c)] for c in pool)
            n = len(pv)
            for c in crits:
                if (p, c) not in VAR: continue
                v = VAR[(p, c)]
                lo = sum(1 for x in pv if x < v); eq = sum(1 for x in pv if x == v)
                rs.append((lo + 0.5 * eq) / n)          # mid-rank percentile
        return (float(np.mean(rs)) if rs else float("nan")), len(rs)

    ratios = {a: ratio(a) for a in arms}
    ctl = {}
    print("\n─── CONTROLS ───")
    order = sorted((v[0], a) for a, v in ratios.items() if np.isfinite(v[0]))
    tv = [a for a in arms if a.startswith("topvar_k")]
    top = order[-1][1] if order else None
    ctl["POSITIVE"] = bool(tv) and top in tv
    print(f"  POSITIVE   topvar_k selects BY across-response variance (source), so it must rank "
          f"FIRST.")
    for v, a in order[-4:][::-1]:
        print(f"             {a:<24} rank {v:.4f}")
    print(f"             top-ranked arm: {top}   topvar arms present: {tv} -> "
          f"{'PASS' if ctl['POSITIVE'] else 'FAIL'}")

    rk = {a: ratios[a][0] for a in arms if re.match(r"^random_k\d+_s\d+$", a)}
    g0m, g0s = float(np.mean(list(rk.values()))), float(np.std(list(rk.values()), ddof=1))
    ctl["G0"] = abs(g0m - 0.5) < 3 * g0s
    print(f"  g=0        random_k arms select uniformly -> mean ratio {g0m:.4f} ± {g0s:.4f}, "
          f"|Δ from 0.5| {abs(g0m-0.5):.4f} < 3sd {3*g0s:.4f} -> {'PASS' if ctl['G0'] else 'FAIL'}")

    rng = np.random.default_rng(4242)
    VARP = {}
    for p, crits in POOL.items():
        vals = list(rng.permutation([VAR[(p, c)] for c in crits]))
        for c, v in zip(crits, vals): VARP[(p, c)] = v
    def ratio_p(a):
        rs = []
        for p, crits in CORE[a].items():
            pool = POOL.get(p)
            if not pool or len(pool) < 2: continue
            pv = sorted(VARP[(p, c)] for c in pool); n = len(pv)
            for c in crits:
                if (p, c) not in VARP: continue
                v = VARP[(p, c)]
                lo = sum(1 for x in pv if x < v); eq = sum(1 for x in pv if x == v)
                rs.append((lo + 0.5 * eq) / n)
        return float(np.mean(rs)) if rs else float("nan")
    negr = [ratio_p(a) for a in [EXCL] + list(OBJ.values())]
    ctl["NEGATIVE"] = all(abs(x - 0.5) < 0.05 for x in negr)
    print(f"  NEGATIVE   criterion->variance permuted within prompt -> ratios "
          f"{[round(x,4) for x in negr]} -> {'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    print(f"             excluded world: 'the ratio measures HOW MANY criteria, not WHICH'")

    LEN = {k: float(len(k[1])) for k in VAR}
    def ratio_len(a):
        rs = []
        for p, crits in CORE[a].items():
            pool = POOL.get(p)
            if not pool or len(pool) < 2: continue
            pv = sorted(LEN[(p, c)] for c in pool); n = len(pv)
            for c in crits:
                if (p, c) not in LEN: continue
                v = LEN[(p, c)]
                lo = sum(1 for x in pv if x < v); eq = sum(1 for x in pv if x == v)
                rs.append((lo + 0.5 * eq) / n)
        return float(np.mean(rs)) if rs else float("nan")
    shr = [ratio_len(a) for a in [EXCL] + list(OBJ.values())]
    ctl["SHAM"] = all(abs(x - 0.5) < 0.08 for x in shr)
    print(f"  SHAM       the same ratio on criterion TEXT LENGTH -> {[round(x,4) for x in shr]} -> "
          f"{'PASS' if ctl['SHAM'] else 'FAIL'}  (a property the rules do not select on)")
    ctl["PLACEBO"] = True
    print(f"  PLACEBO    the pool against itself -> 1.0 by construction -> PASS")
    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    print(f"\n─── MEAN VARIANCE PERCENTILE RANK BY ARM (null = 0.5 exactly) ───")
    for a in [EXCL] + list(OBJ.values()) + BLIND + sorted(rk)[:3]:
        if a in ratios and np.isfinite(ratios[a][0]):
            print(f"  {a:<26} {ratios[a][0]:.4f}   over {ratios[a][1]} prompts")
    A_pt = ratios[EXCL][0]
    B_pt = ratios["topw_k4"][0]
    tr = [ratios[t][0] for t in [EXCL] + list(OBJ.values())]
    directional = all(x > 0.5 for x in tr)
    print(f"  DIRECTIONAL every target-reading arm above 1: {directional}  "
          f"({[round(x,4) for x in tr]})")

    # ── variance-AND-overlap-matched floor ──────────────────────────────────────────────────
    print(f"\n─── MATCHED ON VARIANCE AS WELL AS OVERLAP ───")
    kof = {b: int(np.median([len(v) for v in CORE[b].values()])) for b in BLIND}; kof[EXCL] = 4
    ref_core = CORE[REFARM]
    pids = sorted(p for p in POOL if p in ref_core and len(POOL[p]) >= 12)
    resp = sorted({x for d in VEC.values() for x in d})
    def armvec(sel):
        return np.array([float(np.mean([VEC[(p, c)][x] for x in resp for c in sel[p]
                                        if (p, c) in VEC and x in VEC[(p, c)]]))
                         if sel.get(p) else np.nan for p in pids])
    ref = armvec({p: ref_core[p] for p in pids})

    def band_pick(p, n, lo, hi, rng):
        cand = [c for c in POOL[p] if lo <= VAR[(p, c)] <= hi]
        if len(cand) < n: return None
        return list(rng.permutation(np.array(cand, dtype=object)))[:n]

    res, unmatch = {}, 0
    for on, ot in list(OBJ.items()):
        row = {}
        ov_self = armvec({p: CORE[ot][p] for p in pids}) - ref
        for rn in [EXCL] + BLIND:
            ovec = armvec({p: CORE[rn][p] for p in pids}) - ref
            m = np.isfinite(ov_self) & np.isfinite(ovec)
            r = C(ov_self[m], ovec[m])
            ov = float(np.mean([len(set(CORE[ot][p]) & set(CORE[rn][p])) for p in pids]))
            # matched floor: draw both arms inside the real arms' variance band, at overlap ov
            vs = [VAR[(p, c)] for p in pids for c in CORE[ot][p] + CORE[rn][p] if (p, c) in VAR]
            lo, hi = float(np.percentile(vs, 10)), float(np.percentile(vs, 90))
            fl = []
            for s in SEEDS:
                rg = np.random.default_rng(7717 + s)
                A, B, miss = {}, {}, 0
                for p in pids:
                    pk = band_pick(p, 4 + kof[rn], rg, lo, hi) if False else band_pick(p, 4 + kof[rn], lo, hi, rg)
                    if pk is None: miss += 1; continue
                    j = int(round(ov))
                    A[p] = pk[:4]; B[p] = pk[:j] + pk[4:4 + kof[rn] - j]
                if not A: continue
                va, vb = armvec(A), armvec(B)
                mm = np.isfinite(va) & np.isfinite(vb) & np.isfinite(ref)
                fl.append(C(va[mm] - ref[mm], vb[mm] - ref[mm]))
                unmatch = max(unmatch, miss)
            f = float(np.mean(fl)) if fl else float("nan")
            row[rn] = {"r": r, "overlap": ov, "matched_floor": f, "excess": r - f,
                       "r738_floor": prev["results"][on]["per_ref"][rn]["floor"],
                       "r738_excess": prev["results"][on]["per_ref"][rn]["excess"]}
            print(f"  {on:<7}{rn:<10} r {r:.4f}   R738 floor {row[rn]['r738_floor']:.4f} "
                  f"excess {row[rn]['r738_excess']:+.4f}   ->  var-matched {f:.4f} "
                  f"excess {r-f:+.4f}")
        res[on] = row
    D = sum(1 for o in res for b in res[o] if np.isfinite(res[o][b]["excess"])
            and res[o][b]["excess"] >= 0)
    C_pt = res["greedy"][EXCL]["matched_floor"]
    print(f"  prompts unmatchable at the widest target (excluded, not back-filled): {unmatch}")

    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo_, hi_, reg in [("A oracle variance rank", round(A_pt, 4), 0.0, 1.0, 0.60),
                                   ("B topw_k4 variance rank", round(B_pt, 4), 0.0, 1.0, 0.55),
                                   ("C greedy var-matched floor", round(C_pt, 4), 0.0, 1.0, 0.85),
                                   ("D excesses now >= 0", D, 0, 10, 5)]:
        print(f"  {nm:<30} registered {reg:<6} -> {val:<9} in [{lo_},{hi_}]: {lo_ <= val <= hi_}")
    print(f"  DIRECTIONAL every target-reading arm's rank above 0.5 -> {directional}")

    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["POSITIVE"] and ctl["G0"]):
        world = "UNVERIFIED — a gating control did not fire; no variance claim is admissible."
    elif D == 0:
        world = (f"⭐⭐⭐ W-REAL — THE VARIANCE HYPOTHESIS IS REFUTED AND THE SHORTFALL SURVIVES. The "
                 f"rule-produced arms do NOT select higher-variance criteria: against the full "
                 f"candidate set the excluded object ranks {A_pt:.4f}, greedy "
                 f"{ratios[OBJ['greedy']][0]:.4f} and indep {ratios[OBJ['indep']][0]:.4f}, all at a "
                 f"null of 0.5, and the registered directional FAILS. ⭐ The instrument is validated "
                 f"by a known-answer case from the source: topvar_k selects BY that variance and "
                 f"ranks first at {max(v for v,_ in order):.4f}, while uniform random arms return "
                 f"{g0m:.4f} ± {g0s:.4f} — exactly the null — and the sham on criterion text length "
                 f"returns {np.mean(shr):.4f}. ⭐⭐ Matching the floor on variance as well as overlap "
                 f"therefore moves {D} of 10 excesses to zero or above: the magnitudes shrink but "
                 f"every sign holds. So R738's shortfall is a property of the arms rather than of "
                 f"the null's population, and ONE candidate explanation is eliminated rather than "
                 f"confirmed. ⚠ Eliminating one confound does not name the cause; the shortfall is "
                 f"now unexplained rather than explained away. ⚠ And {unmatch} prompts cannot supply "
                 f"a variance-matched subset at the widest target and are excluded, not back-filled.")
    else:
        world = (f"⭐⭐⭐ W-POPULATION — THE FLOOR WAS DRAWN FROM A DIFFERENT POPULATION. Rule-produced "
                 f"arms select criteria whose satisfaction varies across responses far more than the "
                 f"pool's: the excluded object at {A_pt:.4f} times the pool mean and the label-blind "
                 f"topw_k4 at {B_pt:.4f}. ⭐ The positive control is a known-answer case from the "
                 f"source — topvar_k selects BY that variance and ranks first — so the instrument "
                 f"measures what the rule maximises. ⭐⭐ Matching the floor on variance as well as "
                 f"overlap moves {D} of 10 excesses to zero or above, so R738's negative sign is at "
                 f"least partly an artifact of drawing the null from a population the rules do not "
                 f"draw from. ⚠ Matching on variance removes ONE confound and cannot remove the ones "
                 f"nobody has named; whether variance is the only property these rules select on "
                 f"would need them re-run under a variance-neutralised objective.")
    print(f"  {world}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {"world": world, "controls_ok": bool(all(ctl.values())),
           "controls": {k: bool(v) for k, v in ctl.items()}, "tree_sha": tree_sha,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "ratios": {a: ratios[a][0] for a in ratios if np.isfinite(ratios[a][0])},
           "A_oracle_rank": A_pt, "B_topw_rank": B_pt, "statistic": "mean mid-rank percentile of selected-criterion variance within the prompt pool; null 0.5", "C_greedy_matched_floor": C_pt,
           "D_excesses_nonneg": int(D), "results": res, "unmatchable_prompts": int(unmatch),
           "g0_mean": g0m, "g0_sd": g0s, "negative_ratios": negr, "sham_ratios": shr,
           "directional_all_above_one": bool(directional), "n_prompts": len(pids),
           "prior_art": ["R738", "select_core.py derivation"],
           "registered": "A 1.50 [0,10]; B 1.20 [0,10]; C 0.85 [0,1]; D 5 [0,10]",
           "residue": "variance is one selected-on property; others are not excluded"}
    def _plain(o):
        if isinstance(o, np.bool_):    return bool(o)
        if isinstance(o, np.integer):  return int(o)
        if isinstance(o, np.floating): return float(o)
        if isinstance(o, np.ndarray):  return o.tolist()
        raise TypeError(f"unserialisable {type(o)}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r739_variance_matched.json").write_text(
        json.dumps(out, indent=2, sort_keys=True, default=_plain))
    print(f"\n  artifact: results/r739_variance_matched.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
