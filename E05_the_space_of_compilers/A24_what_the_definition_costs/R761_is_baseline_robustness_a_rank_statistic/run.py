#!/usr/bin/env python3
"""R761 · is ②-robustness a fact about clause ③, or a rank statistic of A2?

R527 published, and STATEMENT.md carries: "the four arms admitted at EVERY specification are
exactly the four ③ excludes -- the label-readers are baseline-robust BECAUSE they read the answer."

THREE THINGS ATTACK IT, and this round runs all three:
  ① R760 showed ③-as-a-list excludes 4 names where ③-as-a-rule excludes 11 tags. R527's identity was
    measured against the under-excluding implementation.
  ② R294's census -- R527's population -- contains NONE of R729's seven target-reading tags, though
    all seven have sat_*.npz. Seven of the eleven counterexamples were invisible to the round.
  ③ Robustness may be a RANK STATISTIC of A2, which would make the finding a reparameterisation.

⛔ TWO RESULTS ARE FORCED AND ARE LABELLED, NOT MEASURED (see PREREGISTRATION D1/D2):
  D1 admission is mean(x-y) - z*se > 0, so with se constant rob would be strictly increasing in mean
     A2 and the arm ordering would be ALGEBRA. The measurement is the INVERSION RESIDUAL.
  D2 the bootstrap mean is LINEAR under a shared index matrix, so 45,500 exact cells cost the same
     as 1,845 marginals. The grid's SIZE IS NOT EFFORT and is not reported as such.

CONTROLS  PROVENANCE (R294's stored c2 at 1e-6, EXIT 2 on failure) · POSITIVE (reproduce R527's
          committed coval_core_by_spec on all 8 keys, band computed from both degenerate ends) ·
          g=0 (self-comparison admitted 0/1820) · NEGATIVE (200 prompt-pairing permutations, a
          DISTRIBUTION) · SHAM S1 (random arm ordering -> the computed inversion ceiling) · SHAM S2
          (random size-matched blocklist, 200 draws) · PLACEBO (the *_sham arms must have rob ~ 0).
UNIT      instrument = an (arm, reference) cell; claim = an ARM. Never conflated.
"""
import hashlib, itertools, json, math, pathlib, subprocess, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls          # noqa: E402
from report import verdict, POS                        # noqa: E402

RES = ROOT / "corebench/results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
NBOOT, ZEFF, L = 1200, 1.959964 + 0.841621, "ABCD"
BOOT_SEED = 31337                                       # R527's, so the POSITIVE control can be exact
PAIRS = list(itertools.combinations(range(4), 2))

# clause ③, both implementations. The rule vocabulary is read off the builder at select_core.py:102.
NAME_BLOCK = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}
TARGET_READING = ("oracle_k", "indep_k", "greedy_k")
SEVEN = ["greedy_k4_greedy_kA", "greedy_k4_greedy_kB", "indep_k4_indep_kA", "indep_k4_indep_kB",
         "oracle_k4_08bR", "oracle_k4_oracle_kA", "oracle_k4_oracle_kB"]
COMMITTED = ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"]
PLACEBO_ARMS = ["coval_core_sham", "gen_sham", "promptecho_sham", "topw_k4_sham"]


def rule_of(tag):
    """The tag is EMITTED from the rule at select_core.py:204; parse it back."""
    for r in ("random_k", "topw_k", "topabs_k", "oracle_k", "topvar_k", "topwvar_k",
              "indep_k", "greedy_k"):
        if tag.startswith(r) and tag[len(r):len(r) + 1].isdigit():
            return r
    return "full" if tag == "full" else None          # None = UNPARSED, counted, never silent


def blocked(tag, mode, blk=None):
    if mode == "name":  return tag in NAME_BLOCK
    if mode == "rule":  return rule_of(tag) in TARGET_READING
    if mode == "sham":  return tag in blk
    raise ValueError(mode)


def _plain(o):
    if isinstance(o, (np.bool_,)):    return bool(o)
    if isinstance(o, np.integer):     return int(o)
    if isinstance(o, np.floating):    return float(o)
    if isinstance(o, np.ndarray):     return o.tolist()
    raise TypeError(type(o))


def tree_sha():
    return subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()[:16]


def doc_pin(rel):
    """R758: a rate is a function of (document version, corpus version). Pin the document."""
    p = ROOT / rel
    b = p.read_bytes()
    return {"lines": b.count(b"\n"), "sha256": hashlib.sha256(b).hexdigest()[:16]}


def main():
    cen = json.loads((A24 / "R294_the_definition_against_everything/results/full_census.json"
                      ).read_text())["rows"]
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    idxs = sorted({i for i, _ in POOL[pids[0]]})
    n_pool, P = len(idxs), len(pids)
    subs = list(itertools.combinations(range(n_pool), 4))
    print(f"  pool criteria {n_pool} · prompts {P} · reference class C({n_pool},4) = {len(subs)}")

    # ---- padded annotator tensor, so a2_of_y is vectorised over prompts -----------------------
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]
    Hmax = max(len(h) for h in HC)
    HPAD = np.zeros((P, Hmax, 6)); HMASK = np.zeros((P, Hmax))
    for a, h in enumerate(HC):
        HPAD[a, :len(h)] = h; HMASK[a, :len(h)] = 1.0
    nH = HMASK.sum(1)

    T = np.zeros((P, n_pool, 4))
    for a, p in enumerate(pids):
        for bi, i in enumerate(idxs):
            for c, x in enumerate(L):
                T[a, bi, c] = POOL[p].get((i, x), 0.0)

    def a2_of_y(Y):
        s = np.sign(Y[:, [i for i, _ in PAIRS]] - Y[:, [j for _, j in PAIRS]])
        agree = (s[:, None, :] == HPAD).mean(2)                 # (P, Hmax)
        return (agree * HMASK).sum(1) / nH

    def arm_vec(tag):
        S = load_sat(RES / f"sat_{tag}.npz")
        ps = [p for p in pids if p in S]
        Y = np.zeros((P, 4))
        for ai, p in enumerate(pids):
            if p not in S: continue
            ii = sorted({i for i, _ in S[p]})
            for c, x in enumerate(L):
                Y[ai, c] = sum(S[p].get((i, x), 0.0) for i in ii)
        return a2_of_y(Y), len(ps)

    # ---- CONTROL · PROVENANCE. Everything below is on R294's scale or on none. ----------------
    pub = subs.index(tuple(range(4)))
    pv = a2_of_y(T[:, list(subs[pub]), :].sum(axis=1))
    k4 = sorted(a for a in cen if cen[a]["k"] == 4)
    A, COV = {}, {}
    for a in k4:
        v, nc = arm_vec(a)
        if nc != P: continue
        A[a], COV[a] = v, nc
    ctrl = [(a, float((A[a] - pv).mean()), cen[a]["c2"][0]) for a in A if "c2" in cen[a]]
    nok = sum(1 for _, m, s in ctrl if abs(m - s) <= 1e-6)
    print(f"  PROVENANCE   R294 stored c2 reproduced {nok}/{len(ctrl)} at 1e-6")
    if nok < max(3, len(ctrl) // 2):
        print("  -> not on R294's scale. UNVERIFIED, and nothing below is reportable."); return 2

    # ---- widen the population: + the seven, + the committed -----------------------------------
    for a in SEVEN + COMMITTED + PLACEBO_ARMS:
        if a in A or not (RES / f"sat_{a}.npz").exists(): continue
        v, nc = arm_vec(a); A[a], COV[a] = v, nc
    arms = sorted(A)
    incomplete = {a: COV[a] for a in arms if COV[a] != P}
    print(f"  population   {len(arms)} arms  (R527 saw {len(ctrl)})   "
          f"coverage-incomplete: {incomplete if incomplete else 'none'}")
    print(f"  ⚠ the seven are present here and were ABSENT from R527's census: "
          f"{[s for s in SEVEN if s in A]}")

    # ---- the whole 1,820-wide reference class, exactly (D2) -----------------------------------
    Y = np.empty((len(subs), P))
    for si, s in enumerate(subs):
        Y[si] = a2_of_y(T[:, list(s), :].sum(axis=1))
    ymean = Y.mean(1); order = np.argsort(ymean)
    pub_pct = 100.0 * (ymean < ymean[pub]).mean()
    print(f"  published POOL[0:4]  A2 {ymean[pub]:.4f} at percentile {pub_pct:.1f}")

    ib = np.random.default_rng(BOOT_SEED).integers(0, P, (NBOOT, P))
    YB = Y[:, ib].mean(axis=2)                                   # (S, NBOOT)  -- D2's linearity
    yvar = Y.var(1, ddof=1)

    def rob_row(x):
        """Exact R294 verdict for one arm against ALL 1,820 references. Returns bool (S,)."""
        xb = x[ib].mean(1)                                       # (NBOOT,)
        eff = x.mean() - ymean
        cov = (Y @ x) / P - ymean * x.mean()
        sd = np.sqrt(np.maximum(x.var(ddof=1) + yvar - 2 * cov * P / (P - 1), 0.0))
        mde = ZEFF * sd / math.sqrt(P)
        BS = xb[None, :] - YB                                    # (S, NBOOT)
        lo = np.percentile(BS, 2.5, axis=1); hi = np.percentile(BS, 97.5, axis=1)
        return np.array([verdict(float(e), float(l), float(h), float(m)) == POS
                         for e, l, h, m in zip(eff, lo, hi, mde)])

    # D2 is arithmetic, so it is ASSERTED against the direct computation rather than trusted.
    _x = A["coval_core"]
    for _j in (0, 7, 913, 1819):
        _sd = math.sqrt(float(np.var(_x - Y[_j], ddof=1)))
        _cv = float((Y[_j] @ _x) / P - Y[_j].mean() * _x.mean())
        _mine = math.sqrt(max(float(_x.var(ddof=1)) + float(yvar[_j]) - 2 * _cv * P / (P - 1), 0.0))
        assert abs(_sd - _mine) < 1e-12, f"D2 sd identity fails at {_j}: {_sd} vs {_mine}"
        _bs = (_x - Y[_j])[ib].mean(1)
        assert np.abs(_bs - (_x[ib].mean(1) - YB[_j])).max() < 1e-12, f"D2 linearity fails at {_j}"
    print(f"  D2 ASSERTED  sd identity and bootstrap linearity hold exactly at 4 probe cells")

    ADM = {a: rob_row(A[a]) for a in arms}
    rob = {a: float(ADM[a].mean()) for a in arms}

    # ---- CONTROL · POSITIVE. R527's committed dict is the known answer. -----------------------
    r527 = json.loads((A24 / "R527_is_clause_two_a_choice/results/clause2_spec_curve.json"
                       ).read_text())["coval_core_by_spec"]
    pcts = [0, 5, 25, 50, 75, 95, 100]
    spec_idx = {f"p{q:03d}": int(order[min(int(q / 100 * (len(subs) - 1)), len(subs) - 1)])
                for q in pcts}
    spec_idx["published"] = pub
    mine = {k: bool(ADM["coval_core"][i]) for k, i in spec_idx.items()}
    match = sum(1 for k in r527 if mine.get(k) == r527[k])
    print(f"  POSITIVE     reproduce R527's coval_core_by_spec: {match}/{len(r527)} keys  "
          f"{'PASS' if match == len(r527) else 'FAIL'}")
    print(f"               band computed: admit-everything -> 7/8 (wrong at p100); "
          f"admit-nothing -> 1/8. Threshold 8/8 unreachable from either end.")
    if match != len(r527):
        print(f"               mine {mine}\n               R527 {r527}")

    # ---- CONTROL · g=0, REPAIRED IN FLIGHT -----------------------------------------------------
    # ⛔ THE REGISTERED FORM WAS A CONTROL THAT CANNOT PASS. It demanded the published reference be
    # admitted at 0 of 1,820 -- but 1,819 of those cells are comparisons against OTHER references,
    # and a reference at percentile 93.7 beats most of them BY CONSTRUCTION. Measured: 1350/1820.
    # The threshold was unreachable, so the control carried no information whichever way it came out.
    self_row = rob_row(Y[pub])
    self_registered = int(self_row.sum())
    # ① the exact self-cell is a DERIVATION, not a measurement: eff=0, sd=0 -> lo=hi=0 -> UNRES by
    #    verdict()'s first branch. Asserted, and labelled as forced.
    assert not bool(self_row[pub]), "verdict() admitted an identically-zero difference"
    # ② the real g=0 is a PLANTED null: the reference's own vector plus mean-zero noise, which has
    #    a true effect of zero without being identically zero. BAND, COMPUTED: a correct instrument
    #    returns ~0; one that ignores the interval admits whenever the draw is positive, ~0.50.
    g0rng = np.random.default_rng(909)
    sdY = float(Y[pub].std(ddof=1))
    g0 = [bool(rob_row(Y[pub] + g0rng.normal(0, sdY, P))[pub]) for _ in range(200)]
    g0_rate = float(np.mean(g0))
    g0_pass = g0_rate <= 0.05
    print(f"  g=0          planted null (ref + mean-zero noise) admitted {g0_rate:.4f} of 200  "
          f"{'PASS' if g0_pass else 'FAIL'}   band [0, ~0.50], threshold 0.05 strictly inside")
    print(f"               (self-cell exactly: UNRESOLVED -- DERIVED from verdict(), not measured;"
          f" the registered '0 of 1820' form returned {self_registered} and could not pass)")
    self_hits = 0 if g0_pass else 1

    # ---- CONTROL · PLACEBO ---------------------------------------------------------------------
    plac = {a: rob[a] for a in PLACEBO_ARMS if a in rob}
    print(f"  PLACEBO      *_sham arms rob: " +
          ", ".join(f"{a} {v:.4f}" for a, v in plac.items()) +
          f"  {'PASS' if plac and max(plac.values()) <= 0.05 else 'FAIL'}")

    # ---- CONTROL · NEGATIVE, a DISTRIBUTION not a draw -----------------------------------------
    rng = np.random.default_rng(7)
    neg = {}
    for a in ["coval_core", "oracle_k4"]:
        if a not in A: continue
        d = [float(rob_row(A[a][rng.permutation(P)]).mean()) for _ in range(200)]
        neg[a] = {"real": rob[a], "perm_mean": float(np.mean(d)),
                  "perm_lo": float(np.percentile(d, 2.5)), "perm_hi": float(np.percentile(d, 97.5))}
        print(f"  NEGATIVE     {a:<12} real {rob[a]:.4f}  200 pairing-permutations "
              f"{np.mean(d):.4f} [{np.percentile(d,2.5):.4f}, {np.percentile(d,97.5):.4f}]")
    print(f"               reads ONLY as 'did the pairing matter', never as why")

    # ---- E2 · the inversion residual (the round's real content, per D1) ------------------------
    a2m = {a: float(A[a].mean()) for a in arms}
    pairs = [(x, y) for i, x in enumerate(arms) for y in arms[i + 1:]]
    def inversions(rank):
        return sum(1 for x, y in pairs
                   if (a2m[x] - a2m[y]) * (rank[x] - rank[y]) < 0)
    inv = inversions(rob)
    sh1 = [inversions({a: v for a, v in zip(arms, rng.permutation([rob[a] for a in arms]))})
           for _ in range(200)]
    inv_pairs = [(x, y, round(a2m[x] - a2m[y], 4), round(rob[x] - rob[y], 4))
                 for x, y in pairs if (a2m[x] - a2m[y]) * (rob[x] - rob[y]) < 0]
    print(f"\n  ⭐ E2 INVERSIONS  rob vs mean A2: {inv} of {len(pairs)} pairs")
    for x, y, da, dr in inv_pairs:
        print(f"     {x:<22} vs {y:<22} dA2 {da:+.4f}  drob {dr:+.4f}")
    print(f"     SHAM S1 random ordering: {np.mean(sh1):.1f} "
          f"[{np.percentile(sh1,2.5):.0f}, {np.percentile(sh1,97.5):.0f}]  "
          f"(computed ceiling {len(pairs)/2:.0f})")

    # ---- E3 · the identity, under both ③ implementations ---------------------------------------
    ROBUST = {a for a in arms if rob[a] == 1.0}
    sets = {}
    for mode in ("name", "rule"):
        blk = {a for a in arms if blocked(a, mode)}
        sets[mode] = {"excluded": sorted(blk), "robust": sorted(ROBUST),
                      "equal": bool(blk == ROBUST),
                      "robust_not_excluded": sorted(ROBUST - blk),
                      "excluded_not_robust": sorted(blk - ROBUST)}
        print(f"\n  ③{mode:<5} excludes {len(blk):>2}   robust(rob=1.0) {len(ROBUST):>2}   "
              f"EQUAL {blk == ROBUST}")
        print(f"     robust but NOT excluded : {sorted(ROBUST - blk) or '(none)'}")
        print(f"     excluded but NOT robust : {sorted(blk - ROBUST) or '(none)'}")

    nblk = len({a for a in arms if blocked(a, "rule")})
    sh2 = []
    for _ in range(200):
        blk = set(rng.choice(arms, size=min(nblk, len(arms)), replace=False))
        sh2.append(int(blk == ROBUST) + 0.0)
    jac = []
    for _ in range(200):
        blk = set(rng.choice(arms, size=min(nblk, len(arms)), replace=False))
        jac.append(len(blk & ROBUST) / max(1, len(blk | ROBUST)))
    print(f"\n     SHAM S2 random size-{nblk} blocklist: exact-match rate {np.mean(sh2):.3f}, "
          f"Jaccard with robust {np.mean(jac):.3f} [{np.percentile(jac,2.5):.3f}, "
          f"{np.percentile(jac,97.5):.3f}]")
    for mode in ("name", "rule"):
        b = set(sets[mode]["excluded"])
        print(f"     ③{mode:<5} Jaccard with robust: "
              f"{len(b & ROBUST)/max(1,len(b | ROBUST)):.3f}")

    # ---- G4 · the rob=1.0 threshold is a CHOICE, so the whole curve is reported ----------------
    tcurve = {}
    for t in (1.0, 0.99, 0.95, 0.90, 0.75):
        Rt = {a for a in arms if rob[a] >= t}
        row = {"n_robust": len(Rt)}
        for mode in ("name", "rule"):
            b = {a for a in arms if blocked(a, mode)}
            row[mode] = {"equal": bool(b == Rt),
                         "jaccard": len(b & Rt) / max(1, len(b | Rt))}
        tcurve[f"t{t}"] = row
    print(f"\n  G4 THRESHOLD CURVE  (the rob=1.0 cut is a specification, not a fact)")
    print(f"  {'t':>6}{'|robust|':>10}{'③name J':>10}{'③rule J':>10}   equal?")
    for k, v in tcurve.items():
        print(f"  {k:>6}{v['n_robust']:>10}{v['name']['jaccard']:>10.3f}"
              f"{v['rule']['jaccard']:>10.3f}   name={v['name']['equal']} rule={v['rule']['equal']}")

    # ---- confound control: recompute on the coverage-complete subset ---------------------------
    comp = [a for a in arms if COV[a] == P]
    ROBc = {a for a in comp if rob[a] == 1.0}
    blkc = {a for a in comp if blocked(a, "rule")}
    print(f"\n  CONFOUND     coverage-complete only ({len(comp)} arms): "
          f"③rule == robust -> {blkc == ROBc}")

    # ---- verdict, gated on the controls --------------------------------------------------------
    gates = (nok >= max(3, len(ctrl) // 2)) and match == len(r527) and self_hits == 0 \
        and bool(plac) and max(plac.values()) <= 0.05
    if not gates:
        world = "UNVERIFIED"
    elif inv <= 1:
        world = "B"
    elif sets["rule"]["equal"]:
        world = "A"
    else:
        world = "C"
    print(f"\n  WORLD {world}")

    rows = sorted(arms, key=lambda a: -rob[a])
    print(f"\n  {'arm':<24}{'A2':>8}{'rob':>8}  cov  ③name ③rule")
    for a in rows:
        print(f"  {a:<24}{a2m[a]:>8.4f}{rob[a]:>8.4f}  {COV[a]:>4} "
              f"{'BLK' if blocked(a,'name') else '  .':>6}{'BLK' if blocked(a,'rule') else '  .':>6}")

    out = pathlib.Path(__file__).parent / "results/robustness_vs_rank.json"
    out.write_text(json.dumps({
        "tree_sha": tree_sha(),
        "document_pin": {"STATEMENT.md": doc_pin("E05_the_space_of_compilers/STATEMENT.md"),
                         "DEFINITION.md": doc_pin("E05_the_space_of_compilers/DEFINITION.md")},
        "n_pool": n_pool, "n_prompts": P, "n_refs": len(subs), "published_pct": pub_pct,
        "population": arms, "coverage": COV, "a2_mean": a2m, "rob": rob,
        "controls": {"provenance": f"{nok}/{len(ctrl)}", "positive": f"{match}/{len(r527)}",
                     "positive_mine": mine, "g0_self_admitted": self_hits,
                     "placebo": plac, "negative": neg},
        "E2": {"inversions": inv, "n_pairs": len(pairs),
               "sham_random_ordering_mean": float(np.mean(sh1)),
               "sham_lo": float(np.percentile(sh1, 2.5)),
               "sham_hi": float(np.percentile(sh1, 97.5)),
               "computed_ceiling": len(pairs) / 2},
        "E3": sets, "E2_inverting_pairs": inv_pairs, "threshold_curve": tcurve,
        "g0_planted_null_rate": g0_rate, "g0_registered_form_returned": self_registered,
        "sham_S2_exact_match_rate": float(np.mean(sh2)),
        "sham_S2_jaccard_mean": float(np.mean(jac)),
        "confound_coverage_complete": {"n": len(comp), "equal": bool(blkc == ROBc)},
        "world": world,
    }, indent=2, default=_plain))
    print(f"\n  artifact -> {out.name}   tree {tree_sha()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
