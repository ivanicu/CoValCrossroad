"""R306 — the whole evidence table at EVERY annotator, with each cell carrying its own MDE.

WHY. R305 found the release ships a median of 16 annotators per prompt (15,593 annotations) and
every number in this campaign used 3. On the one cell recomputed, the effect nearly HALVED:
`full - topwvar_k4` 0.0089 -> 0.0048. So the table in FORMULATION.md is not merely noisier than it
could be -- its POINT ESTIMATES are drawn from a 3-of-16 subsample, and R304's resolvability verdicts
were computed against a GLOBAL MDE bracket when every pair has its own variance structure.

TWO CORRECTIONS IN ONE ROUND, both mechanical, neither optional:
  (1) use every annotator, so the estimate is the release's rather than a draw's;
  (2) give each cell ITS OWN MDE from R305's decomposition, since sigma_b and sigma_w differ by
      50% across pairs (0.0986 vs 0.1486) and a global bracket over-resolves the quiet pairs and
      under-resolves the loud ones.

ESTIMAND        (a) A2 per arm, averaged over EVERY annotator of every prompt;
                (b) all 45 pairwise differences, with a cluster bootstrap CI over prompts;
                (c) per-cell MDE = 2.80 * sqrt(sigma_b^2 + mean(sigma_w^2/m_p)) / sqrt(N), each
                    from that cell's own decomposition;
                (d) which of R304's verdicts change.
IDENTIFICATION  exact for (a) and (b). (c) is identified per R305 and its estimator carries that
                round's positive control. (d) is a comparison of two computed tables.
SCOPE           population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base
                satisfaction judge · baseline each pair is its own · regime k=4 unweighted, ALL
                annotators, cluster bootstrap over PROMPTS, 2000 draws.
WORLDS          W-STABLE  the verdicts hold; the 3-draw table was noisy but unbiased, and the
                          campaign's conclusions survive a 5x increase in annotator information.
                W-MOVES   at least one ADMIT/EXCLUDE or RESOLVED/BELOW verdict flips -> the table
                          as published was partly an artifact of the subsample, and every
                          comparison in the campaign inherits that.
KILL            pre-registered: if any arm's clause-1 verdict (separably above random, or not)
                flips, FORMULATION.md's evidence table is REWRITTEN at all annotators and the
                3-draw version is recorded as superseded, not merely refined.
POSITIVE CTRL   every arm against ITSELF: effect and CI exactly 0. Catches prompt-ordering drift.
NEGATIVE CTRL   `random_k4_s0` vs `random_k4_s1`, two draws of the same rule. Its |effect| must
                stay below its own MDE -- if a rule differs from itself by more than the design
                resolves, no comparison on this page means anything.
PLACEBO         included above (self-comparison identically zero).
NOISE FLOOR     per-cell sigma_w, measured.
MULTIPLICITY    BH at q=0.05 over all 45 cells, threshold q*i/C. Non-survivors printed.
SPECIFICATION   the 3-draw table and the all-annotator table are BOTH printed side by side; the
                axis is the annotator budget and both cells are reported.
SEEDS           the all-annotator estimate is seed-free by construction. The bootstrap uses one
                fixed index matrix so all 45 cells are paired.
ARTIFACT        results/all_annotators.json with source hash.
IMPOSSIBLE      cross-release, cross-model, independently replicated -- one judge, one release.
"""
import json, sys, math, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
NBOOT = 2000
Q = 0.05
ARMS = ["coval_core", "topw_k4", "generic", "gen", "full",
        "topwvar_k4", "random_k4_s0", "topabs_k4", "topvar_k4", "gen_sham"]
VERDICT = {"coval_core": "A", "topw_k4": "A", "gen": "A", "full": "A",
           "generic": "e", "topwvar_k4": "e", "random_k4_s0": "e",
           "topabs_k4": "e", "topvar_k4": "e", "gen_sham": "e"}
# R304's 3-draw effects, for the side-by-side. Read from that round's artifact, not retyped.
PRIOR = json.loads((ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                    / "R304_is_the_boundary_resolvable/results/boundary.json").read_text())


def a2v(c, hs):
    return np.array([np.mean([c[q] == h[q] for q in range(len(PAIRS))]) for h in hs])


def main():
    tg, _ = load_targets()
    arms = {}
    for a in ARMS + ["random_k4_s1"]:
        S = load_sat(ROOT / "corebench" / "results" / f"sat_{a}.npz")
        arms[a] = {p: cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in S if p in tg and len(tg[p]) >= 2}
    pids = sorted(set.intersection(*(set(v) for v in arms.values())))
    N = len(pids)
    HS = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    m = np.array([len(HS[p]) for p in pids])
    print(f"  {N} prompts · {int(m.sum())} annotations · median {int(np.median(m))} per prompt\n")

    # per-arm, per-prompt: the vector of A2 against EVERY annotator, and its mean
    perann = {a: {p: a2v(arms[a][p], HS[p]) for p in pids} for a in arms}
    mean_ = {a: np.array([perann[a][p].mean() for p in pids]) for a in arms}

    print("  A2 PER ARM — 3 draws (as published) vs EVERY annotator\n")
    print(f"    {'arm':<15}{'all-annot':>11}{'sd/√N':>9}   verdict")
    rng0 = np.random.default_rng(1600)
    for a in ARMS:
        v = mean_[a]
        print(f"    {a:<15}{v.mean():>11.4f}{v.std()/math.sqrt(N):>9.4f}   "
              f"{'ADMITTED' if VERDICT[a]=='A' else 'excluded'}")

    rng = np.random.default_rng(31337)
    IDX = rng.integers(0, N, (NBOOT, N))

    def cellstat(x, y):
        d_per = {p: perann[x][p] - perann[y][p] for p in pids}
        means = np.array([d_per[p].mean() for p in pids])
        wvar = np.array([d_per[p].var(ddof=1) if len(d_per[p]) > 1 else 0.0 for p in pids])
        s2w = float(np.mean(wvar))
        s2b = float(max(0.0, means.var(ddof=1) - np.mean(wvar / m)))
        mde = ZEFF * math.sqrt(s2b + float(np.mean(wvar / m))) / math.sqrt(N)
        bs = means[IDX].mean(axis=1)
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        p = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
        return dict(eff=float(means.mean()), lo=lo, hi=hi, p=float(p),
                    mde=mde, s2b=s2b, s2w=s2w)

    # ---- controls -------------------------------------------------------------------------
    s = cellstat("full", "full")
    pos_ok = (s["eff"] == 0.0 and s["lo"] == 0.0 and s["hi"] == 0.0)
    ncell = cellstat("random_k4_s0", "random_k4_s1")
    neg_ok = abs(ncell["eff"]) < ncell["mde"]
    print("\n  CONTROLS\n")
    print(f"    positive/placebo  arm vs ITSELF  eff {s['eff']:.2e} CI [{s['lo']:.2e},{s['hi']:.2e}]"
          f"  {'PASS' if pos_ok else 'FAIL'}")
    print(f"    negative  random_s0 vs random_s1  {ncell['eff']:+.4f} vs its own MDE "
          f"{ncell['mde']:.4f}  {'PASS' if neg_ok else 'FAIL — a rule differs from ITSELF by more than the design resolves'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — controls did not behave.")
        return

    # ---- the 45 cells ---------------------------------------------------------------------
    cells = {}
    for x, y in itertools.combinations(ARMS, 2):
        cells[(x, y)] = cellstat(x, y)
    order = sorted(cells, key=lambda k: cells[k]["p"])
    C = len(order)
    for i, k in enumerate(order, 1):
        cells[k]["bh"] = cells[k]["p"] <= Q * i / C
    for k, v in cells.items():
        v["res"] = "RESOLVED" if abs(v["eff"]) >= v["mde"] else "BELOW RESOLUTION"

    prior_cells = PRIOR["cells"]
    print(f"\n  ALL {C} PAIRS — 3-draw effect vs ALL-ANNOTATOR effect, each against ITS OWN MDE\n")
    print(f"    {'pair':<32}{'3-draw':>9}{'all-ann':>9}{'own MDE':>9}  {'verdict':<18}{'was':<18}BH")
    flips, shrunk = [], []
    for k in sorted(cells, key=lambda k: abs(cells[k]["eff"])):
        v = cells[k]
        pk = f"{k[0]}|{k[1]}"
        pv = prior_cells.get(pk) or prior_cells.get(f"{k[1]}|{k[0]}")
        old_eff = pv["eff"] if pk in prior_cells else -pv["eff"]
        old_res = pv["res"]
        old_norm = "RESOLVED" if old_res == "RESOLVED" else "BELOW RESOLUTION"
        nm = f"{k[0]}({VERDICT[k[0]]}) − {k[1]}({VERDICT[k[1]]})"
        if v["res"] != old_norm:
            flips.append((nm, old_res, v["res"]))
        if abs(v["eff"]) < abs(old_eff) * 0.75:
            shrunk.append((nm, old_eff, v["eff"]))
        print(f"    {nm:<32}{old_eff:>+9.4f}{v['eff']:>+9.4f}{v['mde']:>9.4f}  "
              f"{v['res']:<18}{old_res:<18}{'y' if v['bh'] else '—'}")

    nres = sum(v["res"] == "RESOLVED" for v in cells.values())
    print(f"\n    RESOLVED {nres}/{C} · BELOW RESOLUTION {C-nres}/{C} · BH survivors "
          f"{sum(v['bh'] for v in cells.values())}/{C}")
    print(f"    per-cell MDE ranges {min(v['mde'] for v in cells.values()):.4f} – "
          f"{max(v['mde'] for v in cells.values()):.4f}  — a GLOBAL bracket cannot serve both ends")

    # ---- the pre-registered kill ----------------------------------------------------------
    straddle_bad = [f"{k[0]}−{k[1]}" for k, v in cells.items()
                    if VERDICT[k[0]] != VERDICT[k[1]] and v["res"] != "RESOLVED"]
    print("\n  " + "=" * 74)
    print(f"  PRE-REGISTERED KILL: did any RESOLVED/BELOW verdict flip ?   {bool(flips)}")
    for nm, o, n in flips:
        print(f"      {nm:<34} {o} -> {n}")
    if shrunk:
        print(f"\n  {len(shrunk)} cells shrank by >25% moving from 3 draws to all annotators:")
        for nm, o, n in shrunk:
            print(f"      {nm:<34} {o:+.4f} -> {n:+.4f}   ({abs(n/o):.2f}×)")
    print(f"\n  straddling cells still unresolved: {len(straddle_bad)} — {straddle_bad}")
    print("  " + "=" * 74)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    out = pathlib.Path(__file__).parent / "results" / "all_annotators.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(source_sha=src, n_prompts=N, annotations=int(m.sum()),
                                   arm_a2={a: float(mean_[a].mean()) for a in ARMS},
                                   cells={f"{x}|{y}": v for (x, y), v in cells.items()},
                                   flips=flips, shrunk=shrunk,
                                   straddling_unresolved=straddle_bad), indent=1))
    print(f"\n  artifact {out.relative_to(ROOT)}  src {src}")


if __name__ == "__main__":
    main()
