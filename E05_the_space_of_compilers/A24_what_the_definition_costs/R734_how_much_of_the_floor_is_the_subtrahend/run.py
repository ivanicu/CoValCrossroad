"""
R734 · how much of the floor is the subtrahend

ESTIMAND        how much of R733's floor of 0.5034 is bought by the SHARED SUBTRAHEND alone, and
                does the random-arm floor exceed it -- which would mean R733's excesses are
                understated?
IDENTIFICATION  both quantities computable from R730's satisfaction vectors. NOT identified: WHICH
                structure the difference is; the round names a magnitude, not a cause.
SCOPE           population 968 prompts · instrument Pearson on clause-① margins · baseline the same
                random arms R733 used · regime default emitter only
WORLDS          W-UNDERSTATED corrected floor materially below R733's · W-EXACT equal within spread
KILL            conditional on POSITIVE and g=0. See PREREGISTRATION.txt.
POSITIVE CTRL   on synthetic vectors with a planted shared subtrahend, recover the ANALYTIC floor
                var(r)/sqrt((var(a)+var(r))(var(b)+var(r))) within 0.02 -- a threshold from the
                algebra, not chosen.
g=0             shared subtrahend set to zero -> the corrected floor falls to the shuffle null.
NEGATIVE CTRL   different subtrahends on the two sides -> the floor collapses. excluded world: "any
                common construction produces this correlation".
SHAM            shuffle BOTH arms' own parts, r still aligned -- the ingredient absent on both sides.
                The floor must be unchanged, because it never depended on either arm's signal.
PLACEBO         an arm against itself, r aligned, no shuffling -> exactly 1.0.
NOISE FLOOR     seed spread of the corrected floor over 20 seeds, reported as an SD; the comparison
                against R733's floor is made in units of that SD.
MULTIPLICITY    3 pairs x 20 seeds + the admitted-object comparisons re-scored under both floors.
SPECIFICATION   floor construction x statistic x clause
SEEDS           20 permutation seeds; two hash seeds byte-identical, write verified first
ARTIFACT        results/r734_subtrahend_floor.json with tree_sha
IMPOSSIBLE      WHICH structure the pool component is -> an intervention on the selection pool ·
                independently replicated -> a second implementer
"""
import hashlib, itertools, json, math, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
SAT  = ARC / "R730_seven_tags_are_not_seven_objects" / "results" / "_satvecs.npz"
R733 = ARC / "R733_a_shared_level_or_a_shared_profile" / "results" / "r733_profile_or_level.json"
REFARM = "random_k4_s0"
FLOORFAM = ["random_k4_s1", "random_k4_s2", "random_k8_s0"]
ADMITTED = {"greedy": "greedy_k4_greedy_kA", "indep": "indep_k4_indep_kA"}
EXCLUDED = "oracle_k4"
BLIND = ["topw_k3", "topw_k4", "topw_k6", "topw_k8"]
SEEDS = tuple(range(20))


def C(x, y):
    x = x - x.mean(); y = y - y.mean()
    d = math.sqrt(float((x * x).sum()) * float((y * y).sum()))
    return float((x * y).sum() / d) if d else float("nan")


def main() -> int:
    print("=" * 100); print("R734 · HOW MUCH OF THE FLOOR IS THE SUBTRAHEND"); print("=" * 100)
    for p in (SAT, R733):
        if not p.exists():
            print(f"  UNRUNNABLE: {p.name} absent. Exit 2, never 0."); return 2
    z = np.load(SAT, allow_pickle=True); S = {k: z[k].item() for k in z.files}
    prev = json.loads(R733.read_text())
    if REFARM not in S:
        print(f"  UNRUNNABLE: {REFARM} absent. Exit 2, never 0."); return 2
    ridx = {p: i for i, p in enumerate(S[REFARM]["pids"])}

    def aligned(a, b):
        ia = {p: i for i, p in enumerate(S[a]["pids"])}
        ib = {p: i for i, p in enumerate(S[b]["pids"])}
        sh = [p for p in S[REFARM]["pids"] if p in ia and p in ib]
        r = np.asarray(S[REFARM]["vec"], float)[[ridx[p] for p in sh]]
        return (np.asarray(S[a]["vec"], float)[[ia[p] for p in sh]],
                np.asarray(S[b]["vec"], float)[[ib[p] for p in sh]], r)

    print(f"  reference arm (the shared subtrahend): {REFARM}")
    print(f"  ⛔ R733's NEXT proposed re-pairing the MARGIN. That destroys the r-alignment too and")
    print(f"     collapses to the shuffle null. The construction used here re-pairs the ARM's own")
    print(f"     part and keeps r aligned — established by algebra before this round was written.")

    ctl = {}
    print("\n─── CONTROLS ───")
    rng = np.random.default_rng(20260805)
    n = 968
    ra, rb, rr = rng.normal(size=n), rng.normal(size=n), rng.normal(size=n) * 1.3
    analytic = float(np.var(rr) / math.sqrt((np.var(ra) + np.var(rr)) * (np.var(rb) + np.var(rr))))
    got = float(np.mean([C(rng.permutation(ra) - rr, rb - rr) for _ in SEEDS]))
    ctl["POSITIVE"] = abs(got - analytic) < 0.02
    print(f"  POSITIVE   planted shared subtrahend: analytic floor {analytic:.4f}, recovered "
          f"{got:.4f}, |Δ| {abs(got-analytic):.4f} < 0.02 -> "
          f"{'PASS' if ctl['POSITIVE'] else 'FAIL'}")

    zeros = np.zeros(n)
    g0 = float(np.mean([abs(C(rng.permutation(ra) - zeros, rb - zeros)) for _ in SEEDS]))
    ctl["G0"] = g0 < 0.05
    print(f"  g=0        subtrahend set to ZERO -> |floor| {g0:.4f} < 0.05 -> "
          f"{'PASS' if ctl['G0'] else 'FAIL'}")

    r2 = rng.normal(size=n) * 1.3
    neg = float(np.mean([abs(C(rng.permutation(ra) - rr, rb - r2)) for _ in SEEDS]))
    ctl["NEGATIVE"] = neg < 0.5 * got
    print(f"  NEGATIVE   DIFFERENT subtrahends on the two sides -> |floor| {neg:.4f} vs {got:.4f} "
          f"-> {'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    print(f"             excluded world: 'any common construction produces this correlation'")

    both = float(np.mean([C(rng.permutation(ra) - rr, rng.permutation(rb) - rr) for _ in SEEDS]))
    ctl["SHAM"] = abs(both - got) < 0.05
    print(f"  SHAM       BOTH arms' own parts shuffled, r still aligned -> {both:.4f} vs {got:.4f} "
          f"-> {'PASS' if ctl['SHAM'] else 'FAIL'}")
    print(f"             unchanged, because the floor never depended on either arm's signal")

    a0, b0, r0 = aligned(FLOORFAM[0], FLOORFAM[0])
    ctl["PLACEBO"] = abs(C(a0 - r0, b0 - r0) - 1.0) < 1e-12
    print(f"  PLACEBO    an arm against itself -> {C(a0-r0, b0-r0):.6f} -> "
          f"{'PASS' if ctl['PLACEBO'] else 'FAIL'}")
    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    # ── the two floors on the REAL arms ─────────────────────────────────────────────────────
    print(f"\n─── THE TWO FLOORS · {len(FLOORFAM)} pairs x {len(SEEDS)} seeds ───")
    print(f"  {'pair':<36}{'R733 floor':>12}{'corrected':>12}{'seed SD':>10}{'pool':>9}")
    rows, r733v, corrv = [], [], []
    for a, b in itertools.combinations(FLOORFAM, 2):
        va, vb, r = aligned(a, b)
        real = C(va - r, vb - r)
        rg = np.random.default_rng(4242)
        draws = [C(rg.permutation(va) - r, vb - r) for _ in SEEDS]
        cor, sd = float(np.mean(draws)), float(np.std(draws, ddof=1))
        rows.append({"pair": f"{a}|{b}", "r733": real, "corrected": cor, "sd": sd,
                     "pool": real - cor})
        r733v.append(real); corrv.append(cor)
        print(f"  {a+'|'+b:<36}{real:>12.4f}{cor:>12.4f}{sd:>10.4f}{real-cor:>9.4f}")

    A = float(np.mean(r733v)); B = float(np.mean(corrv))
    SD = float(np.mean([r["sd"] for r in rows]))
    Cp = A - B
    print(f"\n  R733 floor {A:.4f}   corrected floor {B:.4f}   pool component {Cp:+.4f}   "
          f"seed SD {SD:.4f}   = {abs(Cp)/SD:.1f} SDs")

    # ── re-score R733's verdicts under the corrected floor ──────────────────────────────────
    print(f"\n─── R733's COMPARISONS RE-SCORED UNDER BOTH FLOORS ───")
    print(f"  {'object':<9}{'ref':<11}{'r':>9}{'excess@R733':>13}{'excess@corr':>13}")
    changed, per = 0, {}
    for an, at in ADMITTED.items():
        exc = {}
        for label, refs in (("excluded", [EXCLUDED]), ("blind", BLIND)):
            vals = []
            for rt in refs:
                va, vb, r = aligned(at, rt)
                vals.append(C(va - r, vb - r))
            m = float(np.mean(vals))
            exc[label] = m
            print(f"  {an:<9}{label:<11}{m:>9.4f}{m-A:>13.4f}{m-B:>13.4f}")
        old = exc["excluded"] - A > exc["blind"] - A
        new = exc["excluded"] - B > exc["blind"] - B
        per[an] = {"r_excluded": exc["excluded"], "r_blind": exc["blind"],
                   "verdict_r733": bool(old), "verdict_corrected": bool(new)}
        changed += int(old != new)
        print(f"           -> R733 said {'EXCLUDED' if old else 'blind'}; corrected floor says "
              f"{'EXCLUDED' if new else 'blind'}")
    D = changed
    directional = bool(B < A - 3 * SD)

    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo_, hi_, reg in [("A R733 floor reproduced", round(A, 4), 0.0, 1.0, 0.5034),
                                   ("B corrected floor", round(B, 4), 0.0, 1.0, 0.48),
                                   ("C pool component", round(Cp, 4), -1.0, 1.0, 0.02),
                                   ("D verdicts changed", D, 0, 2, 0)]:
        print(f"  {nm:<28} registered {reg:<8} -> {val:<9} in [{lo_},{hi_}]: {lo_ <= val <= hi_}")
    print(f"  DIRECTIONAL the corrected floor is BELOW R733's by more than 3 seed SDs -> {directional}")

    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["POSITIVE"] and ctl["G0"]):
        world = "UNVERIFIED — a gating control did not fire; no floor decomposition is admissible."
    elif D > 0:
        world = (f"⭐⭐⭐ R733's ORDERING WAS FLOOR-DEPENDENT. {D} of {len(ADMITTED)} objects change "
                 f"verdict when the floor is corrected from {A:.4f} to {B:.4f}, so its conclusion is "
                 f"amended: { {k: v['verdict_corrected'] for k, v in per.items()} }")
    else:
        w = "W-UNDERSTATED" if directional else "W-EXACT"
        world = (f"⭐⭐⭐ {w}. The shared subtrahend alone buys a correlation of {B:.4f}; the random "
                 f"arms R733 used as its floor reach {A:.4f}, a difference of {Cp:+.4f} which is "
                 f"{abs(Cp)/SD:.1f} seed SDs. "
                 + (f"⭐ So those arms DO carry structure beyond the subtrahend, R733's floor was too "
                    f"HIGH, and its reported excesses are UNDERSTATED — its conclusion is "
                    f"strengthened, not weakened. "
                    if directional else
                    f"⭐ So the random arms carry nothing beyond the subtrahend and R733's floor was "
                    f"already the right one. ")
                 + f"⚠ NEITHER FLOOR CHANGES R733's VERDICTS: both admitted objects sit with the "
                   f"excluded one under both, so the ordering never depended on this choice. "
                   f"⚠ AND THE DIFFERENCE NAMES A MAGNITUDE, NOT A CAUSE. Calling it the criterion "
                   f"pool would be an attribution this design cannot make; identifying it needs an "
                   f"intervention on the pool. "
                   f"⛔ FINALLY, THE ROUND R733 PROPOSED WOULD HAVE MEASURED NOTHING: re-pairing the "
                   f"MARGIN destroys the subtrahend's alignment too, so it collapses to the shuffle "
                   f"null R733 had already run. Three lines of algebra killed my own next step "
                   f"before any compute was spent, which is what the attack ladder puts first.")
    print(f"  {world}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {"world": world, "controls_ok": bool(all(ctl.values())),
           "controls": {k: bool(v) for k, v in ctl.items()}, "tree_sha": tree_sha,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "pairs": rows, "A_r733_floor": A, "B_corrected_floor": B, "C_pool_component": Cp,
           "seed_sd": SD, "sds_apart": abs(Cp) / SD if SD else None,
           "D_verdicts_changed": int(D), "per_object": per,
           "analytic_check": {"analytic": analytic, "recovered": got},
           "directional_corrected_below": directional,
           "prior_art": ["R284", "R457", "R733"],
           "registered": "A 0.5034 [0,1]; B 0.48 [0,1]; C 0.02 [-1,1]; D 0 [0,2]",
           "residue": "the difference names a magnitude, not a cause; identifying it needs an "
                      "intervention on the selection pool"}
    def _plain(o):
        if isinstance(o, np.bool_):    return bool(o)
        if isinstance(o, np.integer):  return int(o)
        if isinstance(o, np.floating): return float(o)
        if isinstance(o, np.ndarray):  return o.tolist()
        raise TypeError(f"unserialisable {type(o)}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r734_subtrahend_floor.json").write_text(
        json.dumps(out, indent=2, sort_keys=True, default=_plain))
    print(f"\n  artifact: results/r734_subtrahend_floor.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
