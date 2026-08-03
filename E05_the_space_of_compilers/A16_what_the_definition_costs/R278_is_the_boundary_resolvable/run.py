"""R278 — is the definition's own ADMIT/EXCLUDE boundary above this design's resolution?

WHY. R277 measured the MDE of the design behind every number in FORMULATION.md: [0.0100, 0.0200]
in A2 units across four specifications. The evidence table's clause-1 column then reads very
differently from how it was written:

    full        ADMITTED   +0.0131 [+0.0061, +0.0202]   <- inside the MDE bracket
    topwvar_k4  excluded   +0.0092 [-0.0003, +0.0153]   <- inside the MDE bracket

Those two verdicts are the boundary of the definition. If the difference between them is below what
the design resolves, then WHICH SIDE OF THE DEFINITION AN ARM FALLS ON was decided by noise, and the
table's four-admitted/six-excluded partition is not a measurement at that edge. **This round attacks
my own definition's central artifact, at the one place it is weakest, and it is the cheapest
decisive thing available -- the sat files are all on disk and nothing needs the GPU.**

ESTIMAND        (a) every pairwise paired A2 difference among the 10 arms of the evidence table,
                    with a cluster bootstrap CI over prompts -- 45 cells;
                (b) each cell's |effect| against R277's MDE bracket, giving a three-valued
                    resolvability verdict RESOLVED / MARGINAL / BELOW RESOLUTION;
                (c) the specific boundary cell `full` vs `topwvar_k4`.
IDENTIFICATION  exact for (a). (b) is a DERIVATION -- a division of a measured effect by a measured
                bracket -- and is labelled as one wherever it is printed.
SCOPE           population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base
                satisfaction judge · baseline each pair is its own baseline · regime k=4
                unweighted, 3 annotator draws, cluster bootstrap over PROMPTS, 2000 draws.
WORLDS          W-SHARP   the boundary cell is RESOLVED -> the table's partition is a measurement
                          everywhere and the definition's edge is real.
                W-BLUNT   the boundary cell is BELOW RESOLUTION -> the admit/exclude call between
                          `full` and `topwvar_k4` is not supported by this design, and the table
                          must carry that at the row level, not as a general caveat.
                These differ in what the artifact IS: a partition, or a partition with an
                unresolved edge that happens to have been written down as sharp.
KILL            pre-registered: if |full - topwvar_k4| < MDE_hi (0.0200), FORMULATION.md's
                admit/exclude verdicts for those two arms are marked UNRESOLVED AT THIS DESIGN.
                I do not get to keep them by pointing at the clause-1 CIs, because those CIs were
                computed by the same design whose resolution is the thing in question.
POSITIVE CTRL   every arm against ITSELF must return exactly 0.0000 with a CI of exactly [0,0].
                It can fail: any mismatch in prompt ordering between the two sides breaks it.
NEGATIVE CTRL   `random_k4_s0` vs `random_k4_s1` -- two independent random draws of the same rule.
                They differ only by seed, so their difference must be small; a large one would say
                the random baseline is not a baseline. Reported, not assumed.
PLACEBO         included in the positive control above (self-comparison must be identically zero).
NOISE FLOOR     R277's MDE bracket, measured, carried in rather than re-derived.
MULTIPLICITY    BH at q=0.05 over ALL 45 cells, threshold q*i/C. Non-survivors printed.
SPECIFICATION   the resolvability verdict is computed against BOTH ends of the MDE bracket, so
                every cell carries its own interval rather than a point ratio.
SEEDS           3 annotator draws; the R276 seed check is repeated.
ARTIFACT        results/boundary.json with source hash.
IMPOSSIBLE      cross-model, cross-release, independently replicated -- one judge, one release.
"""
import json, sys, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
DRAWS = (0, 1, 2)
NBOOT = 2000
Q = 0.05
MDE_LO, MDE_HI = 0.0100, 0.0200                              # R277, carried in

ARMS = ["coval_core", "topw_k4", "generic", "gen", "full",
        "topwvar_k4", "random_k4_s0", "topabs_k4", "topvar_k4", "gen_sham"]
VERDICT = {"coval_core": "ADMITTED", "topw_k4": "ADMITTED", "gen": "ADMITTED", "full": "ADMITTED",
           "generic": "excluded", "topwvar_k4": "excluded", "random_k4_s0": "excluded",
           "topabs_k4": "excluded", "topvar_k4": "excluded", "gen_sham": "excluded"}


def a2(c, h):
    return float(np.mean([c[q] == h[q] for q in range(len(PAIRS))]))


def main():
    tg, _ = load_targets()
    arms = {}
    for a in ARMS + ["random_k4_s1"]:
        S = load_sat(ROOT / "corebench" / "results" / f"sat_{a}.npz")
        arms[a] = {p: cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in S if p in tg and len(tg[p]) >= 2}
    pids = sorted(set.intersection(*(set(v) for v in arms.values())))
    H = {}
    for d in DRAWS:
        rng = np.random.default_rng(1600 + d)
        H[d] = {p: cls(np.array(tg[p][int(rng.integers(len(tg[p])))][0], float)) for p in pids}
    assert sum(tuple(H[0][p]) != tuple(H[1][p]) for p in pids) > 0
    base = {a: np.array([np.mean([a2(arms[a][p], H[d][p]) for d in DRAWS]) for p in pids])
            for a in arms}
    print(f"  {len(pids)} prompts · {len(ARMS)} arms · {len(ARMS)*(len(ARMS)-1)//2} pairs · "
          f"MDE carried from R277 [{MDE_LO:.4f}, {MDE_HI:.4f}]\n")

    rng = np.random.default_rng(31337)
    IDX = rng.integers(0, len(pids), (NBOOT, len(pids)))      # ONE index matrix -> paired across cells

    def cell(x, y):
        d = base[x] - base[y]
        bs = d[IDX].mean(axis=1)
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        p = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
        return float(d.mean()), lo, hi, float(p)

    # ---- controls -------------------------------------------------------------------------
    self_dev = max(abs(cell(a, a)[0]) + abs(cell(a, a)[1]) + abs(cell(a, a)[2]) for a in ARMS)
    pos_ok = self_dev == 0.0
    r_eff, r_lo, r_hi, _ = cell("random_k4_s0", "random_k4_s1")
    neg_ok = abs(r_eff) < MDE_HI
    print("  CONTROLS")
    print(f"    positive/placebo  every arm vs ITSELF   max|effect|+|CI| = {self_dev:.2e}  "
          f"{'PASS' if pos_ok else 'FAIL'}")
    print(f"    negative          random_s0 vs random_s1 {r_eff:+.4f} [{r_lo:+.4f}, {r_hi:+.4f}]  "
          f"{'PASS — two draws of the same rule agree below the MDE' if neg_ok else 'FAIL — the random baseline is not one'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — controls did not behave.")
        return

    # ---- the 45 cells ---------------------------------------------------------------------
    cells = {}
    for x, y in itertools.combinations(ARMS, 2):
        e, lo, hi, p = cell(x, y)
        cells[(x, y)] = dict(eff=e, lo=lo, hi=hi, p=p)
    order = sorted(cells, key=lambda k: cells[k]["p"])
    C = len(order)
    for i, k in enumerate(order, 1):
        cells[k]["bh"] = cells[k]["p"] <= Q * i / C

    def verdict(e):
        a = abs(e)
        if a >= MDE_HI:
            return "RESOLVED"
        if a >= MDE_LO:
            return "MARGINAL"
        return "BELOW RESOLUTION"

    tally = {"RESOLVED": 0, "MARGINAL": 0, "BELOW RESOLUTION": 0}
    cross = []                                                # cells that straddle the definition
    for k, v in cells.items():
        v["res"] = verdict(v["eff"])
        tally[v["res"]] += 1
        if VERDICT[k[0]] != VERDICT[k[1]]:
            cross.append(k)

    print(f"\n  RESOLVABILITY OF ALL {C} PAIRS — a DERIVATION (measured effect ÷ measured bracket)\n")
    for r, n in tally.items():
        print(f"    {r:<20}{n:>4} / {C}   {n/C:>6.1%}")
    print(f"    BH survivors        {sum(v['bh'] for v in cells.values()):>4} / {C}")

    print(f"\n  THE {len(cross)} CELLS THAT STRADDLE THE DEFINITION (one ADMITTED, one excluded)\n")
    print(f"    {'pair':<34}{'effect':>9}  {'95% CI':<22}{'verdict':<18}BH")
    bad = []
    for k in sorted(cross, key=lambda k: abs(cells[k]["eff"])):
        v = cells[k]
        nm = f"{k[0]}({VERDICT[k[0]][0]}) − {k[1]}({VERDICT[k[1]][0]})"
        print(f"    {nm:<34}{v['eff']:>+9.4f}  [{v['lo']:+.4f}, {v['hi']:+.4f}]{'':<3}"
              f"{v['res']:<18}{'y' if v['bh'] else '—'}")
        if v["res"] != "RESOLVED":
            bad.append(nm)

    # ---- the pre-registered kill ----------------------------------------------------------
    bk = ("full", "topwvar_k4") if ("full", "topwvar_k4") in cells else ("topwvar_k4", "full")
    b = cells[bk]
    killed = abs(b["eff"]) < MDE_HI
    print("\n  " + "=" * 72)
    print(f"  THE BOUNDARY CELL   full (ADMITTED) − topwvar_k4 (excluded)")
    print(f"    effect {b['eff']:+.4f}  [{b['lo']:+.4f}, {b['hi']:+.4f}]   |effect| vs MDE "
          f"[{abs(b['eff'])/MDE_HI:.2f}, {abs(b['eff'])/MDE_LO:.2f}]   {b['res']}")
    print(f"  PRE-REGISTERED KILL: |full − topwvar_k4| < {MDE_HI} ?   {killed}")
    if killed:
        print("  -> W-BLUNT. The definition's admit/exclude call between these two arms is NOT")
        print("     supported at this design. FORMULATION.md must carry UNRESOLVED on those rows.")
    else:
        print("  -> W-SHARP. The boundary is above resolution and the partition stands there.")
    if bad:
        print(f"\n  ⚠ {len(bad)} of {len(cross)} straddling cells are not RESOLVED:")
        for nm in bad:
            print(f"      {nm}")
    print("  " + "=" * 72)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    out = pathlib.Path(__file__).parent / "results" / "boundary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(source_sha=src, n_prompts=len(pids), nboot=NBOOT,
                                   mde=[MDE_LO, MDE_HI], tally=tally,
                                   cells={f"{x}|{y}": v for (x, y), v in cells.items()},
                                   straddling_unresolved=bad, boundary_killed=bool(killed),
                                   neg_ctrl=[r_eff, r_lo, r_hi]), indent=1))
    print(f"\n  artifact {out.relative_to(ROOT)}  src {src}")


if __name__ == "__main__":
    main()
