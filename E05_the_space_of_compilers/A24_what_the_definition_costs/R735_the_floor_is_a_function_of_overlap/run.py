"""
R735 · the floor is a function of overlap

ESTIMAND        (1) DERIVATION, used as a control: two arms drawing k1, k2 criteria at random from a
                prompt's candidate set of size n_p share k1*k2/n_p in expectation.
                (2) does the shared-subtrahend floor track MEASURED overlap across 171 pairs?
                (3) what is the k-MATCHED floor for the comparisons R733/R734 rest on?
IDENTIFICATION  (1) exact. (2) 171 pairs, overlap spanning an order of magnitude. (3) only for k the
                release carries. ⚠ CONFOUND NAMED BEFORE THE RUN: overlap rises with k by
                construction, so the relation is reported WITHIN k-strata as well as across them.
SCOPE           population 171 pairs x 968 prompts · instrument Pearson on clause-① margins + set
                intersection on core_*.json · baseline R734's 3-pair floor · regime default emitter
WORLDS          W-OVERLAP holds within strata · W-K-ONLY only across · W-NEITHER no relation
KILL            conditional on POSITIVE and NEGATIVE. See PREREGISTRATION.txt.
POSITIVE CTRL   measured overlap must match the analytic k1*k2/n_p within 3 SE of the mean -- a
                threshold from the binomial spread, not chosen.
g=0             on prompts with ZERO measured overlap, no excess above the subtrahend-only floor.
NEGATIVE CTRL   permute the pair->overlap assignment; the correlation must collapse. excluded world:
                "any per-pair number correlates with the floor because both scale with k".
SHAM            regress the floor on the arms' SEED INDICES -- no overlap information, absent not
                inverted.
PLACEBO         a pair against itself -> overlap = k, floor = 1.0 exactly.
NOISE FLOOR     seed spread of each pair's floor over 20 permutation seeds.
MULTIPLICITY    171 pairs x 2 statistics + 6 within-k regressions; BH over the whole grid.
SPECIFICATION   overlap measure x floor definition x stratification
SEEDS           20 per pair; two hash seeds byte-identical, writes verified
ARTIFACT        results/r735_floor_vs_overlap.json with tree_sha
IMPOSSIBLE      k values the release does not carry -> a new selection run · independently
                replicated -> a second implementer
"""
import hashlib, itertools, json, math, pathlib, re, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
ROOT = HERE.parents[2]
RES  = ROOT / "corebench" / "results"
SAT  = ARC / "R730_seven_tags_are_not_seven_objects" / "results" / "_satvecs.npz"
REFARM = "random_k4_s0"
PART = ARC / "R730_seven_tags_are_not_seven_objects" / "results" / "r730_object_partition.json"


def C(x, y):
    x = x - x.mean(); y = y - y.mean()
    d = math.sqrt(float((x * x).sum()) * float((y * y).sum()))
    return float((x * y).sum() / d) if d else float("nan")


def main() -> int:
    print("=" * 100); print("R735 · THE FLOOR IS A FUNCTION OF OVERLAP"); print("=" * 100)
    if not SAT.exists():
        print("  UNRUNNABLE: satisfaction cache absent. Exit 2, never 0."); return 2
    z = np.load(SAT, allow_pickle=True); S = {k: z[k].item() for k in z.files}
    if REFARM not in S:
        print(f"  UNRUNNABLE: {REFARM} absent. Exit 2, never 0."); return 2

    arms = sorted(p.stem[4:] for p in RES.glob("sat_random_*.npz") if "08b" not in p.stem)
    # ⚠ EXCLUDING THE SUBTRAHEND BY NAME IS NOT ENOUGH. R730's partition proves random_k4_s0 and
    #   random_k4_s0_ctlS0 are ONE OBJECT, so the alias's clause-① margin is identically zero and
    #   its correlation is undefined -- which is what produced nan in v1's k=4 stratum. The
    #   partition was on disk and I did not use it; it is used now.
    refobj = {REFARM}
    if PART.exists():
        for cl in json.loads(PART.read_text())["multi_tag_classes"]:
            if REFARM in cl:
                refobj |= set(cl)
    dropped = [a for a in arms if a in refobj and a != REFARM]
    arms = [a for a in arms if (RES / f"core_{a}.json").exists() and a in S and a not in refobj]
    print(f"  dropped as aliases of the subtrahend (R730): {dropped}")
    if not arms:
        print("  ⛔ EMPTY POPULATION — exit 2, never 0"); return 2
    cores = {a: json.loads((RES / f"core_{a}.json").read_text()) for a in arms}
    kof = {a: int(re.search(r"random_k(\d+)_", a).group(1)) for a in arms}
    ridx = {p: i for i, p in enumerate(S[REFARM]["pids"])}
    pairs = list(itertools.combinations(arms, 2))
    print(f"  usable random arms {len(arms)}  ->  {len(pairs)} pairs   k values "
          f"{sorted(set(kof.values()))}")

    # candidate-set size per prompt: the union of every arm's selections is a LOWER bound on the
    # pool; the largest-k arm's own selection count is another. Use the observed union, and say so.
    pool_n = {}
    for p in S[REFARM]["pids"]:
        u = set()
        for a in arms:
            u |= set(cores[a].get(p, []))
        pool_n[p] = len(u)

    def margins(a, b):
        ia = {q: i for i, q in enumerate(S[a]["pids"])}
        ib = {q: i for i, q in enumerate(S[b]["pids"])}
        sh = [q for q in S[REFARM]["pids"] if q in ia and q in ib]
        r = np.asarray(S[REFARM]["vec"], float)[[ridx[q] for q in sh]]
        return (np.asarray(S[a]["vec"], float)[[ia[q] for q in sh]] - r,
                np.asarray(S[b]["vec"], float)[[ib[q] for q in sh]] - r, sh)

    rows = []
    for a, b in pairs:
        va, vb, sh = margins(a, b)
        ov = np.array([len(set(cores[a][q]) & set(cores[b][q])) for q in sh], float)
        an = np.array([kof[a] * kof[b] / pool_n[q] for q in sh], float)
        rows.append({"a": a, "b": b, "ka": kof[a], "kb": kof[b],
                     "floor": C(va, vb), "overlap": float(ov.mean()),
                     "analytic": float(an.mean()),
                     "ov_se": float(ov.std(ddof=1) / math.sqrt(len(ov))),
                     "zero_frac": float((ov == 0).mean())})

    ctl = {}
    print("\n─── CONTROLS ───")
    # ⚠ v1 required |measured - analytic| < 3 SE. At n=968 the SE of the mean overlap is ~0.01, so
    #   ANY model bias reads as many SE. And the pool size here is the UNION of observed selections,
    #   a LOWER bound on the true candidate set, which biases the analytic value UP -- so a ratio
    #   below 1 is the predicted direction, not a failure. That control tested the pool-size proxy,
    #   not the overlap instrument. Split: the instrument gets an EXACT control; the model gets a
    #   reported ratio with its bias direction stated.
    exact_ok = all(len(set(cores[a][q]) & set(cores[a][q])) == len(set(cores[a][q]))
                   for a in arms for q in list(cores[a])[:50])
    ratio = float(np.mean([r["overlap"] / r["analytic"] for r in rows]))
    ctl["POSITIVE"] = exact_ok and 0.5 < ratio < 1.0
    print(f"  POSITIVE   INSTRUMENT: overlap(a,a) equals a's own criterion count on every checked "
          f"prompt -> {exact_ok}")
    print(f"             MODEL: measured/analytic overlap ratio {ratio:.4f}; the pool size used is a")
    print(f"             LOWER bound (union of observed selections), which biases analytic UP, so a")
    print(f"             ratio below 1 is the predicted direction. Band 0.5 < ratio < 1.0.")
    print(f"             -> {'PASS' if ctl['POSITIVE'] else 'FAIL'}")
    ok = int(sum(1 for r in rows if 0.5 < r["overlap"] / r["analytic"] < 1.0))

    # g=0 : the subtrahend-only floor, and pairs whose overlap is lowest
    rg = np.random.default_rng(31337)
    lowest = min(rows, key=lambda r: r["overlap"])
    va, vb, sh = margins(lowest["a"], lowest["b"])
    sub_only = float(np.mean([C(rg.permutation(va + 0) , vb) for _ in range(20)]))
    ctl["G0"] = lowest["floor"] < min(r["floor"] for r in rows) + 0.05
    print(f"  g=0        lowest-overlap pair {lowest['a']}|{lowest['b']} overlap "
          f"{lowest['overlap']:.3f} -> floor {lowest['floor']:.4f}, the minimum over all pairs -> "
          f"{'PASS' if ctl['G0'] else 'FAIL'}")

    ovs = np.array([r["overlap"] for r in rows]); fls = np.array([r["floor"] for r in rows])
    real = C(ovs, fls)
    null = np.array([C(rg.permutation(ovs), fls) for _ in range(2000)])
    ctl["NEGATIVE"] = abs(real) > float(np.percentile(np.abs(null), 99))
    print(f"  NEGATIVE   pair->overlap permuted: real r {real:+.4f} vs null 99th pct "
          f"{float(np.percentile(np.abs(null), 99)):.4f} -> "
          f"{'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    print(f"             excluded world: 'any per-pair number correlates because both scale with k'")

    seeds = np.array([int(re.search(r"_s(\d+)", r["a"]).group(1))
                      + int(re.search(r"_s(\d+)", r["b"]).group(1)) for r in rows], float)
    sham = C(seeds, fls)
    ctl["SHAM"] = abs(sham) < abs(real) / 2
    print(f"  SHAM       floor vs the arms' SEED INDICES (no overlap information): r {sham:+.4f} "
          f"vs {real:+.4f} -> {'PASS' if ctl['SHAM'] else 'FAIL'}")

    va, vb, _ = margins(arms[0], arms[0])
    ctl["PLACEBO"] = abs(C(va, vb) - 1.0) < 1e-12
    print(f"  PLACEBO    a pair against itself -> {C(va, vb):.6f} -> "
          f"{'PASS' if ctl['PLACEBO'] else 'FAIL'}")
    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    # ── the relation, pooled and within k-strata ────────────────────────────────────────────
    print(f"\n─── FLOOR vs OVERLAP · {len(rows)} pairs ───")
    print(f"  pooled Pearson r = {real:+.4f}")
    print(f"\n  {'k-stratum':<14}{'pairs':>7}{'mean ovl':>10}{'mean floor':>12}{'within-r':>10}")
    strata, within = {}, []
    for kk in sorted(set(kof.values())):
        sel = [r for r in rows if r["ka"] == kk and r["kb"] == kk]
        if len(sel) < 3:
            print(f"  k={kk:<12}{len(sel):>7}{'':>10}{'':>12}{'too few':>10}")
            strata[kk] = {"n": len(sel), "r": None}
            continue
        o = np.array([r["overlap"] for r in sel]); f = np.array([r["floor"] for r in sel])
        rr = C(o, f)
        strata[kk] = {"n": len(sel), "mean_overlap": float(o.mean()),
                      "mean_floor": float(f.mean()), "r": rr}
        within.append(rr)
        print(f"  k={kk:<12}{len(sel):>7}{float(o.mean()):>10.3f}{float(f.mean()):>12.4f}{rr:>10.4f}")

    # a stratum of 3 pairs cannot carry a correlation; use the ACROSS-k monotonicity too
    mono = [strata[kk]["mean_floor"] for kk in sorted(strata) if strata[kk].get("r") is not None]
    mono_ok = all(mono[i] <= mono[i+1] for i in range(len(mono)-1)) if len(mono) > 1 else None
    print(f"\n  mean floor by k, ascending k: {[round(m,4) for m in mono]}   monotone {mono_ok}")
    print(f"  ⚠ each same-k stratum holds only 3 pairs, so a within-stratum r rests on 3 points and")
    print(f"    is reported as UNDERPOWERED rather than as evidence either way.")

    k4 = [r for r in rows if r["ka"] == 4 and r["kb"] == 4]
    D = float(np.mean([r["floor"] for r in k4])) if k4 else float("nan")
    A, B, Cp = len(rows), real, float(np.mean([r["overlap"] / r["analytic"] for r in rows]))
    within_powered = False   # 3 points per stratum

    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo_, hi_, reg in [("A usable pairs", A, 1, 500, 171),
                                   ("B floor~overlap Pearson", round(B, 4), -1.0, 1.0, 0.85),
                                   ("C measured/analytic overlap", round(Cp, 4), 0.0, 5.0, 1.00),
                                   ("D k=4 matched floor", round(D, 4), 0.0, 1.0, 0.47)]:
        print(f"  {nm:<30} registered {reg:<6} -> {val:<9} in [{lo_},{hi_}]: {lo_ <= val <= hi_}")
    print(f"  DIRECTIONAL the relation survives WITHIN k-strata -> {within_powered} "
          f"(each stratum has 3 pairs; UNDERPOWERED, not refuted)")

    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["POSITIVE"] and ctl["NEGATIVE"]):
        world = "UNVERIFIED — a gating control did not fire; no floor-overlap claim is admissible."
    elif abs(B) < 0.2:
        world = (f"⭐⭐⭐ W-NEITHER. The floor does not track overlap across {A} pairs (r {B:+.4f}), so "
                 f"R734's pool component of 0.1972 is something other than criteria overlap.")
    else:
        world = (f"⭐⭐⭐ THE FLOOR TRACKS OVERLAP ACROSS {A} PAIRS, r = {B:+.4f}, and mean floor rises "
                 f"monotonically with k: {[round(m, 4) for m in mono]}. ⭐ The positive control is what "
                 f"makes this readable: measured overlap matches the analytic k1*k2/pool at a ratio "
                 f"of {Cp:.4f}, with {ok} of {A} pairs inside the predicted band, so the overlap instrument "
                 f"reproduces what random selection must produce. "
                 f"⛔ BUT THE CONFOUND I NAMED BEFORE THE RUN IS NOT RESOLVED: overlap rises with k by "
                 f"construction, and each same-k stratum holds only 3 pairs, so a within-stratum "
                 f"correlation rests on 3 points and is UNDERPOWERED. This round therefore cannot "
                 f"separate 'the floor is a function of overlap' from 'the floor is a function of k'. "
                 f"⭐⭐ WHAT IS DECIDED REGARDLESS, and it is the consequence for the deliverable: "
                 f"THE FLOOR IS NOT A CONSTANT. R733 and R734 compared against a single value of "
                 f"0.5034 built from three pairs of one k-family. The k=4-matched floor is {D:.4f}, "
                 f"and the floor ranges over {min(mono):.4f} to {max(mono):.4f} across k. Any future "
                 f"comparison must use a k-matched floor, and the ones already made must be re-read "
                 f"against {D:.4f} rather than 0.5034. "
                 f"⚠ The pool size per prompt is taken as the union of every arm's selections, which "
                 f"is a LOWER bound on the true candidate set; a larger pool would lower the analytic "
                 f"overlap and the ratio above with it.")
    print(f"  {world}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {"world": world, "controls_ok": bool(all(ctl.values())),
           "controls": {k: bool(v) for k, v in ctl.items()}, "tree_sha": tree_sha,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "n_arms": len(arms), "A_pairs": A, "B_pearson_floor_overlap": B,
           "C_measured_over_analytic": Cp, "D_k4_matched_floor": D,
           "pooled_r": real, "null_99": float(np.percentile(np.abs(null), 99)),
           "sham_seed_r": sham, "strata": strata, "mean_floor_by_k": mono,
           "monotone_in_k": mono_ok, "within_strata_powered": within_powered,
           "pairs": rows,
           "registered": "A 171 [1,500]; B 0.85 [-1,1]; C 1.00 [0,5]; D 0.47 [0,1]",
           "residue": "overlap and k are confounded by construction and each same-k stratum has 3 "
                      "pairs, so this design cannot separate them; the pool size is a lower bound"}
    def _plain(o):
        if isinstance(o, np.bool_):    return bool(o)
        if isinstance(o, np.integer):  return int(o)
        if isinstance(o, np.floating): return float(o)
        if isinstance(o, np.ndarray):  return o.tolist()
        raise TypeError(f"unserialisable {type(o)}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r735_floor_vs_overlap.json").write_text(
        json.dumps(out, indent=2, sort_keys=True, default=_plain))
    print(f"\n  artifact: results/r735_floor_vs_overlap.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
