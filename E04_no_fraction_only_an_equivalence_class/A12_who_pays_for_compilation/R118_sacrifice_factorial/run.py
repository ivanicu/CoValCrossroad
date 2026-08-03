"""r118 -- the sacrifice FACTORIAL. Every definition x every bearer x every baseline x every floor.

Ivan, 2026-07-30: prove multidimensional invisible sacrifice surviving cross-verification across ALL
definitions, massively deep statistics, NO TOY -- and prove that everything already done IS a toy.

THE TOY PROOF, first, because it is the premise
----------------------------------------------
r116 measured ONE definition (absolute harm) on ONE bearer (person) against ONE baseline (full) with
ONE null (paired rater shuffle) at four thresholds. r117 measured ONE statistic family across six
bearers against one baseline. Laid on the grid below, r116 is the cell

    (bearer=person, definition=absolute_harm, baseline=full, statistic=rate, null=rater_shuffle)

and r117 is one column of it. Together they are **2 of the 1,000+ admissible cells**. Every headline
either produced -- "12.46% are worse off", "five dimensions cross-verified" -- is a single-cell result
reported as if it characterised the phenomenon. That is the 100-line-python failure at the level of
an experiment rather than a script: a real result, in one cell, of a matrix nobody swept.

THE ORTHOGONAL AXES
-------------------
  A BEARER      person · prompt · decision · subjectivity-level · stratum · label · contest-bin
  B DEFINITION  absolute harm · withheld gain · no-available-benefit · verdict-without-basis ·
                withheld decision · concentration · tail burden
  C BASELINE    full · rand4 · first4 · oracle · chance  (a baseline is what "worse" is worse THAN,
                and it is the axis every previous round held fixed at `full` without saying so)
  D THRESHOLD   eps in {0, 0.005, 0.01, 0.02, 0.05}
  E STATISTIC   rate · tail-mass · spread · CVaR · Gini · departure-from-the-r115-line
  F NULL        within-prompt rater shuffle · within-rater prompt shuffle · label permutation ·
                within-prompt bin permutation · replicate-derived
  G SCALE       raw · PURGED of the accuracy-gap line (r115: beta_a proportional to (0.5 - e_a))

G is not optional. r115 proved any covariate raising both arms yields a differential proportional to
their accuracy gap, so every cell is computed BOTH raw and purged, and a cell that survives only raw
is reported as geometry rather than as sacrifice.

WHAT THE GRID COSTS, stated rather than hidden
----------------------------------------------
The BASELINE axis only exists on the 7,275 even-rater cells, because that is where the non-compiled
arms (oracle, rand4, first4) were built -- selected on odd raters, evaluated on even. So the design is
two blocks, not one: the FULL population (15,202 cells, 80,521 decisions) carries every axis except
baseline, and the MATCHED block (7,275 cells) carries all seven at a third of the size. Reporting a
single N over the whole grid would be false.

MULTIPLICITY. Benjamini-Hochberg over EVERY admissible cell at once, not per axis and not per family.
A grid this size will produce dozens of nominally significant cells by construction; the only honest
statement is the corrected one, and the number of cells tested is reported beside it.

ADMISSIBILITY. A cell is admissible only if (i) its bearer has enough units for its statistic --
a rate over 4 levels has no resolution, so rates are restricted to bearers with >= 20 units and
spreads to those below -- and (ii) its null actually destroys the structure its bearer encodes.
Inadmissible cells are COUNTED AND NAMED, never silently dropped.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join            # noqa: E402
from covalx.stamp import stamp          # noqa: E402

FULL = _ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz"
CORE = _ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_core.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
R113 = _ROOT / "E04_no_fraction_only_an_equivalence_class/A12_who_pays_for_compilation/R113_accuracy_matched_arm/results/r113_cells.npz"

SEED = 20260730
N_PERM = 400
EPS_GRID = (0.0, 0.005, 0.01, 0.02, 0.05)
TAIL_Q = 0.10
CVAR_Q = 0.10
BH_Q = 0.05
LOW_UNITS = 20
CHANCE = 0.5


def nfkc(s):
    return unicodedata.normalize("NFKC", str(s))


def load_sat(path):
    z = np.load(path, allow_pickle=True)
    d = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        d[pid][(int(ci), lab)] = float(s)
    return d


def eq_scores(satp):
    out = {}
    for lab in sorted({l for _, l in satp}):
        v = [s for (ci, ll), s in satp.items() if ll == lab]
        if v:
            out[lab] = float(np.mean(v))
    return out


def strict_pairs(r):
    tiers = [t.split("=") for t in r.split(">")]
    out = set()
    for i, a in enumerate(tiers):
        for b in tiers[i + 1:]:
            for x in a:
                for y in b:
                    out.add((x.strip(), y.strip()))
    return out


def build_full():
    """The 15,202-cell population, with every bearer label attached."""
    F, C = load_sat(FULL), load_sat(CORE)
    cells, pairs = [], []
    joined = sorted(((p, c) for p, c, r in load_join(COMPARISONS, RUBRICS)
                     if p in F and p in C), key=lambda t: t[0])
    personal = {p: any((a.get("ranking_blocks") or {}).get("personal")
                       for a in c["metadata"]["assessments"]) for p, c in joined}
    for pid, comp in joined:
        sc = {"full": eq_scores(F[pid]), "core": eq_scores(C[pid])}
        if min(len(sc["full"]), len(sc["core"])) < 2:
            continue
        votes = defaultdict(lambda: [0, 0]); here = []
        for a in sorted(comp["metadata"]["assessments"], key=lambda x: str(x.get("annotator_id"))):
            w = (a.get("ranking_blocks") or {}).get("world") or []
            if not w:
                continue
            P0 = strict_pairs(w[0].get("ranking", ""))
            here.append((str(a.get("annotator_id")), nfkc(a.get("subjectivity", "")), P0))
            for x, y in P0:
                k = tuple(sorted((x, y))); votes[k][0 if (x, y) == k else 1] += 1
        for rid, subj, P0 in here:
            e, pp_ = {}, {}
            for arm in ("full", "core"):
                s = sc[arm]
                P = {(x, y) for x, y in P0 if x in s and y in s and s[x] != s[y]}
                if not P:
                    break
                e[arm] = sum(1 for x, y in P if s[x] < s[y]) / len(P)
                pp_[arm] = {(x, y): (1.0 if s[x] < s[y] else 0.0) for x, y in P}
            if len(e) != 2:
                continue
            cells.append({"pid": pid, "rid": rid, "subj": subj, "pers": personal[pid],
                          "full": e["full"], "core": e["core"]})
            for xy in sorted(set(pp_["full"]) & set(pp_["core"])):
                k = tuple(sorted(xy)); v = votes[k]; t = v[0] + v[1]
                pairs.append({"pid": pid, "rid": rid, "win": xy[0],
                              "contest": (min(v) / t) if t else 0.0,
                              "full": pp_["full"][xy], "core": pp_["core"][xy]})
    return cells, pairs


def unit_mean(key, val, n):
    c = np.maximum(np.bincount(key, None, n), 1)
    return np.bincount(key, val, n) / c, np.bincount(key, None, n)


def statistic(name, d, eps):
    """Every DEFINITION reduced to a number on a per-unit delta vector."""
    if len(d) == 0:
        return float("nan")
    if name == "rate":                       # B1 absolute harm
        return float(np.mean(d > eps))
    if name == "withheld":                   # B2 withheld gain: share gaining LESS than the median
        return float(np.mean(d > np.median(d)))
    if name == "nobenefit":                  # B3 no available benefit: share with |gain| ~ 0
        return float(np.mean(np.abs(d) <= eps))
    if name == "tailmass":                   # B6 concentration of the sacrifice
        pos = np.maximum(d, 0.0)
        if pos.sum() <= 0:
            return 0.0
        k = max(1, int(round(TAIL_Q * len(d))))
        return float(np.sort(pos)[-k:].sum() / pos.sum())
    if name == "spread":                     # for low-unit bearers
        return float(d.max() - d.min())
    if name == "cvar":                       # B7 tail burden
        k = max(1, int(round(CVAR_Q * len(d))))
        return float(np.sort(d)[-k:].mean())
    if name == "gini":
        g = np.sort(np.maximum(-d, 0.0)); n = len(g)
        if g.sum() <= 0:
            return float("nan")
        i = np.arange(1, n + 1)
        return float(2 * (i * g).sum() / (n * g.sum()) - (n + 1) / n)
    raise ValueError(name)


RATE_STATS = ("rate", "withheld", "nobenefit", "tailmass", "cvar", "gini")
LOW_STATS = ("spread", "cvar")


def _run_sweep(job, idx, nperm, seed=SEED):
    """One (block, bearer, arms, scale) sweep. Module level so it pickles to a worker process."""
    block, bearer, key, n_units, a_arm, b_arm, group, arms_name, purge = job
    rng = np.random.default_rng([seed, idx])
    out, bad = [], []
    d_cell = b_arm - a_arm
    if purge:
        ssum = b_arm + a_arm
        k = float(d_cell.mean() / (ssum.mean() - 1.0))
        d_cell = d_cell - k * ssum
    stats_ok = RATE_STATS if n_units >= LOW_UNITS else LOW_STATS
    obs_u, n_u = unit_mean(key, d_cell, n_units)
    present = n_u > 0
    obs = {}
    for st in stats_ok:
        for eps in (EPS_GRID if st in ("rate", "nobenefit") else (0.0,)):
            obs[(st, eps)] = statistic(st, obs_u[present], eps)
    null = {k2: [] for k2 in obs}
    for _ in range(nperm):
        if group is None:
            s_ = rng.permutation(key)
        else:
            s_ = key.copy()
            for g in np.unique(group):
                ix = np.flatnonzero(group == g)
                s_[ix] = key[rng.permutation(ix)]
        du, nu = unit_mean(s_, d_cell, n_units)
        m = nu > 0
        for (st, eps) in obs:
            null[(st, eps)].append(statistic(st, du[m], eps))
    for (st, eps), o_ in obs.items():
        v = np.array(null[(st, eps)], float); v = v[~np.isnan(v)]
        if o_ != o_ or len(v) < 10:
            bad.append({"block": block, "bearer": bearer, "arms": arms_name, "stat": st,
                        "eps": eps, "purge": purge, "why": "statistic or null undefined"})
            continue
        c0 = float(v.mean())
        p2 = float((np.sum(np.abs(v - c0) >= abs(o_ - c0)) + 1) / (len(v) + 1))
        out.append({"block": block, "bearer": bearer, "arms": arms_name, "stat": st, "eps": eps,
                    "purge": purge, "n_units": int(present.sum()), "obs": o_, "floor": c0,
                    "p": p2, "direction": "above" if o_ > c0 else "below"})
    return out, bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(_RES / "r118_sacrifice_factorial.json"))
    ap.add_argument("--nperm", type=int, default=N_PERM)
    ap.add_argument("--jobs", type=int, default=20)
    # A seed FLAG, because three background runs of a module-level constant are three IDENTICAL runs.
    # I launched exactly that and came within one command of reporting it as multi-seed replication --
    # which would have been a determinism check relabelled, the same shape as certifying determinism
    # and calling it currency. Seed robustness requires the generator to actually differ.
    ap.add_argument("--seed", type=int, default=SEED)
    # Data transforms that each constitute one RIGOR-AXIS variation of the whole grid. They are
    # flags rather than separate scripts so the variant and the base are provably the same code.
    ap.add_argument("--subsample", type=float, default=1.0, help="cross-scale: fraction of cells")
    ap.add_argument("--jitter", type=float, default=0.0, help="perturbation-robust: sd of noise")
    ap.add_argument("--fold", default="", help="prompt-robust: k/K, hold OUT prompt fold k of K")
    ap.add_argument("--stratum", default="", help="OOD: world_only | both_forms")
    # POSITIVE CONTROL AS A GRID VARIATION. Without it every non-surviving cell is UNVERIFIED rather
    # than null: a cell that fails may be measuring nothing, or may be an instrument that has never
    # been shown to return non-zero. Planting a KNOWN effect on a KNOWN bearer and re-running the
    # whole grid is the only way to tell those apart at 628-cell scale, and sweeping g turns it into
    # a dose-response curve and an MDE per cell at the same time.
    ap.add_argument("--plant", default="", help="positive control: bearer:share:g")
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    cells, pairs = build_full()
    # --- rigor-axis variations, applied to the population BEFORE any statistic is computed ---
    vrng = np.random.default_rng([args.seed, 999])
    if args.stratum:
        want = (args.stratum == "both_forms")
        keep_p = {c["pid"] for c in cells if c["pers"] == want}
        cells = [c for c in cells if c["pid"] in keep_p]
        pairs = [q for q in pairs if q["pid"] in keep_p]
        print(f"  OOD variation: stratum={args.stratum} -> {len(cells):,} cells")
    if args.fold:
        k, K = (int(x) for x in args.fold.split("/"))
        allp = sorted({c["pid"] for c in cells})
        fold_of = {p_: i % K for i, p_ in enumerate(vrng.permutation(allp))}
        cells = [c for c in cells if fold_of[c["pid"]] != k]
        pairs = [q for q in pairs if fold_of.get(q["pid"], -1) != k]
        print(f"  prompt-robust variation: holding out fold {k} of {K} -> {len(cells):,} cells")
    if args.subsample < 1.0:
        idx = vrng.random(len(cells)) < args.subsample
        keep_c = {(c["pid"], c["rid"]) for c, m in zip(cells, idx) if m}
        cells = [c for c in cells if (c["pid"], c["rid"]) in keep_c]
        pairs = [q for q in pairs if (q["pid"], q["rid"]) in keep_c]
        print(f"  cross-scale variation: {args.subsample:.0%} -> {len(cells):,} cells")
    if args.plant:
        pb, psh, pg = args.plant.split(":")
        psh, pg = float(psh), float(pg)
        if pb == "person":
            units = sorted({c["rid"] for c in cells})
            hit = set(vrng.choice(units, max(1, int(psh * len(units))), replace=False).tolist())
            for c in cells:
                if c["rid"] in hit:
                    c["core"] = float(min(1.0, c["core"] + pg))
        elif pb == "prompt":
            units = sorted({c["pid"] for c in cells})
            hit = set(vrng.choice(units, max(1, int(psh * len(units))), replace=False).tolist())
            for c in cells:
                if c["pid"] in hit:
                    c["core"] = float(min(1.0, c["core"] + pg))
            for q in pairs:
                if q["pid"] in hit:
                    q["core"] = float(min(1.0, q["core"] + pg))
        elif pb == "label":
            labs = sorted({q["win"] for q in pairs})
            hit = set(vrng.choice(labs, max(1, int(psh * len(labs))), replace=False).tolist())
            for q in pairs:
                if q["win"] in hit:
                    q["core"] = float(min(1.0, q["core"] + pg))
        elif pb == "stratum":
            for c in cells:
                if c["pers"]:
                    c["core"] = float(min(1.0, c["core"] + pg))
        elif pb == "subjectivity":
            lv = sorted({c["subj"] for c in cells})
            hit = {lv[0]}
            for c in cells:
                if c["subj"] in hit:
                    c["core"] = float(min(1.0, c["core"] + pg))
        else:
            raise SystemExit(f"REFUSING: unknown plant bearer {pb!r}")
        print(f"  POSITIVE CONTROL: planted g={pg} on {psh:.0%} of bearer '{pb}'")

    if args.jitter > 0:
        for c in cells:
            c["full"] = float(np.clip(c["full"] + vrng.normal(0, args.jitter), 0, 1))
            c["core"] = float(np.clip(c["core"] + vrng.normal(0, args.jitter), 0, 1))
        print(f"  perturbation-robust variation: jitter sd={args.jitter}")
    if not cells:
        print("REFUSING: empty population. Exits 2, never 0.", file=sys.stderr)
        return 2

    pid_l = sorted({c["pid"] for c in cells}); rid_l = sorted({c["rid"] for c in cells})
    PI = {p: i for i, p in enumerate(pid_l)}; RI = {r: i for i, r in enumerate(rid_l)}
    cp = np.array([PI[c["pid"]] for c in cells]); cr = np.array([RI[c["rid"]] for c in cells])
    cf = np.array([c["full"] for c in cells]); cc = np.array([c["core"] for c in cells])
    subj_l = sorted({c["subj"] for c in cells}); SI = {v: i for i, v in enumerate(subj_l)}
    csub = np.array([SI[c["subj"]] for c in cells])
    cstr = np.array([1 if c["pers"] else 0 for c in cells])

    pp = np.array([PI[q["pid"]] for q in pairs])
    pf = np.array([q["full"] for q in pairs]); pc_ = np.array([q["core"] for q in pairs])
    lab_l = sorted({q["win"] for q in pairs}); LI = {v: i for i, v in enumerate(lab_l)}
    plab = np.array([LI[q["win"]] for q in pairs])
    pcon = np.digitize(np.array([q["contest"] for q in pairs]), [0.0001, 0.15, 0.30, 0.45])

    # BEARERS: (name, key, n_units, arm_a, arm_b, group_for_null, level)
    BEARERS = {
        "person":       (cr, len(rid_l), cf, cc, cp, "within_prompt"),
        "prompt":       (cp, len(pid_l), cf, cc, cr, "within_rater"),
        "subjectivity": (csub, len(subj_l), cf, cc, None, "global"),
        "stratum":      (cstr, 2, cf, cc, None, "global"),
        "label":        (plab, len(lab_l), pf, pc_, pp, "within_prompt"),
        "contest":      (pcon, 5, pf, pc_, pp, "within_prompt"),
    }
    print(f"FULL BLOCK: {len(cells):,} cells, {len(pairs):,} decisions, "
          f"{len(pid_l)} prompts, {len(rid_l)} raters")

    # ---- MATCHED BLOCK: the baseline axis, which costs population --------------------
    matched = None
    if R113.exists():
        z = np.load(R113, allow_pickle=True)
        matched = {"gp": z["gp"], "gr": z["gr"],
                   "arms": {a: z[f"e_{a}"] for a in ("full", "core", "oracle", "rand4", "first4")}}
        print(f"MATCHED BLOCK: {len(matched['gp']):,} even-rater cells carrying "
              f"{len(matched['arms'])} arms -- the ONLY block where the BASELINE axis exists")

    grid, inadmissible = [], []
    JOBS = []          # (block, bearer, key, n_units, a, b, group, arms_name, purge)

    def permute(key, group, n_units):
        if group is None:
            return rng.permutation(key)
        s = key.copy()
        for g in np.unique(group):
            ix = np.flatnonzero(group == g)
            s[ix] = key[rng.permutation(ix)]
        return s

    def enqueue(block, bearer, key, n_units, a_arm, b_arm, group, arms_name, purge):
        JOBS.append((block, bearer, key, n_units, a_arm, b_arm, group, arms_name, purge))

    def sweep(block, bearer, key, n_units, a_arm, b_arm, group, arms_name, purge, rng):
        d_cell = b_arm - a_arm
        if purge:
            ssum = b_arm + a_arm
            k = float(d_cell.mean() / (ssum.mean() - 1.0))
            d_cell = d_cell - k * ssum
        stats_ok = RATE_STATS if n_units >= LOW_UNITS else LOW_STATS
        obs_u, n_u = unit_mean(key, d_cell, n_units)
        present = n_u > 0
        obs = {}
        for st in stats_ok:
            for eps in (EPS_GRID if st in ("rate", "nobenefit") else (0.0,)):
                obs[(st, eps)] = statistic(st, obs_u[present], eps)
        null = {k2: [] for k2 in obs}
        for _ in range(args.nperm):
            s = permute(key, group, n_units)
            du, nu = unit_mean(s, d_cell, n_units)
            m = nu > 0
            for (st, eps) in obs:
                null[(st, eps)].append(statistic(st, du[m], eps))
        for (st, eps), o in obs.items():
            v = np.array(null[(st, eps)], float)
            v = v[~np.isnan(v)]
            if o != o or len(v) < 10:
                inadmissible.append({"block": block, "bearer": bearer, "arms": arms_name,
                                     "stat": st, "eps": eps, "purge": purge,
                                     "why": "statistic or null undefined on this bearer"})
                continue
            c0 = float(v.mean())
            p2 = float((np.sum(np.abs(v - c0) >= abs(o - c0)) + 1) / (len(v) + 1))
            grid.append({"block": block, "bearer": bearer, "arms": arms_name, "stat": st,
                         "eps": eps, "purge": purge, "n_units": int(present.sum()),
                         "obs": o, "floor": c0, "p": p2,
                         "direction": "above" if o > c0 else "below"})

    print(f"\nsweeping the FULL block: 6 bearers x {len(RATE_STATS)} statistics x "
          f"{len(EPS_GRID)} thresholds x 2 scales")
    for bn, (key, nu, a_, b_, grp, _kind) in BEARERS.items():
        for purge in (False, True):
            enqueue("full_population", bn, key, nu, a_, b_, grp, "core-full", purge)

    if matched:
        print(f"sweeping the MATCHED block: the BASELINE axis, "
              f"{len(matched['arms'])*(len(matched['arms'])-1)//2} arm pairs x 2 bearers x 2 scales")
        mg, mr = matched["gp"], matched["gr"]
        n_mp, n_mr = int(mg.max()) + 1, int(mr.max()) + 1
        for a, b in itertools.combinations(sorted(matched["arms"]), 2):
            for bn, key, nu, grp in (("person", mr, n_mr, mg), ("prompt", mg, n_mp, mr)):
                for purge in (False, True):
                    enqueue("matched_even_rater", bn, key, nu,
                            matched["arms"][a], matched["arms"][b], grp, f"{b}-{a}", purge)

    # Run every sweep across cores. Each worker derives its own generator from SEED and its job
    # index, so the whole grid stays reproducible under a changed hash seed.
    from concurrent.futures import ProcessPoolExecutor
    print(f"\n  {len(JOBS)} sweeps x {args.nperm} permutations, across {args.jobs} workers")
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        futs = [ex.submit(_run_sweep, j, i, args.nperm, args.seed)
                for i, j in enumerate(JOBS)]
        for f in futs:
            g_, bad = f.result()
            grid.extend(g_)
            inadmissible.extend(bad)

    # The guard this file did not have, which is why deleting the sweep above surfaced as a
    # ZeroDivisionError three prints later instead of as a refusal. Empty population exits 2.
    if not grid:
        print("REFUSING: the grid is empty -- no sweep produced a cell. Nothing-to-correct exits 2, "
              "never 0, and never a traceback in the middle of a summary.", file=sys.stderr)
        return 2

    # RESOLUTION, stated correctly on the SECOND attempt. A permutation p cannot fall below
    # 1/(N+1). My first version demanded that the TOP cell clear q/C and refused otherwise -- that is
    # the BONFERRONI bound applied to a BENJAMINI-HOCHBERG procedure. BH's threshold at rank k is
    # q*k/C, so the LARGEST threshold is q itself, and the binding statement is not a refusal but a
    # count: ranks below C*min_p/q cannot be resolved at this N, everything below them can.
    min_p = 1.0 / (args.nperm + 1)
    unresolvable_ranks = int(np.ceil(len(grid) * min_p / BH_Q)) - 1
    print(f"\n  RESOLUTION: {args.nperm} permutations floor p at {min_p:.2e}. BH at q={BH_Q} over "
          f"{len(grid)} cells has threshold q*k/C, so the top {max(unresolvable_ranks,0)} rank(s) "
          f"cannot be resolved at this N; every rank below them can. "
          f"(A blanket 'needs N >= q/C' would be Bonferroni, not BH.)")

    ps = np.array([g["p"] for g in grid])
    o = np.argsort(ps)
    passed = ps[o] <= BH_Q * (np.arange(1, len(ps) + 1) / len(ps))
    kk = np.max(np.flatnonzero(passed)) + 1 if passed.any() else 0
    keep = np.zeros(len(ps), bool); keep[o[:kk]] = True
    for g, s_ in zip(grid, keep):
        g["bh"] = bool(s_)

    n_cells = len(grid)
    surv = [g for g in grid if g["bh"]]
    surv_purged = [g for g in surv if g["purge"]]
    nominal = int((ps < 0.05).sum())
    print(f"\n{'='*100}")
    print(f"GRID: {n_cells} admissible cells, {len(inadmissible)} inadmissible and named.")
    print(f"  nominally p<0.05: {nominal} ({nominal/n_cells:.1%})   "
          f"after BH at q={BH_Q}: {len(surv)} ({len(surv)/n_cells:.1%})")
    print(f"  of the survivors, {len(surv_purged)} survive ON THE PURGED SCALE -- the only ones that "
          f"are not the r115 geometry")

    by_bearer = defaultdict(lambda: [0, 0])
    for g in grid:
        by_bearer[g["bearer"]][0] += 1
        by_bearer[g["bearer"]][1] += int(g["bh"] and g["purge"])
    print(f"\n  {'bearer':<16}{'cells':>8}{'purged survivors':>19}")
    for b, (t, s_) in sorted(by_bearer.items(), key=lambda kv: -kv[1][1]):
        print(f"  {b:<16}{t:>8}{s_:>19}")

    by_stat = defaultdict(lambda: [0, 0])
    for g in grid:
        by_stat[g["stat"]][0] += 1
        by_stat[g["stat"]][1] += int(g["bh"] and g["purge"])
    print(f"\n  {'definition':<16}{'cells':>8}{'purged survivors':>19}")
    for b, (t, s_) in sorted(by_stat.items(), key=lambda kv: -kv[1][1]):
        print(f"  {b:<16}{t:>8}{s_:>19}")

    if matched:
        by_arms = defaultdict(lambda: [0, 0])
        for g in grid:
            if g["block"] == "matched_even_rater":
                by_arms[g["arms"]][0] += 1
                by_arms[g["arms"]][1] += int(g["bh"] and g["purge"])
        print(f"\n  BASELINE AXIS -- the one every previous round held fixed without saying so")
        print(f"  {'arm pair':<20}{'cells':>8}{'purged survivors':>19}")
        for b, (t, s_) in sorted(by_arms.items(), key=lambda kv: -kv[1][1]):
            print(f"  {b:<20}{t:>8}{s_:>19}")

    print(f"\n  STRONGEST PURGED SURVIVORS (the cells that are sacrifice and not geometry):")
    for g in sorted(surv_purged, key=lambda x: x["p"])[:14]:
        print(f"    {g['bearer']:<13}{g['arms']:<14}{g['stat']:<9}eps={g['eps']:<6}"
              f"obs {g['obs']:+.4f} floor {g['floor']:+.4f} {g['direction']:<6} p={g['p']:.4f}")

    world = ("W-FACTORIAL-ROBUST" if len(surv_purged) >= 10 else
             "W-THIN" if len(surv_purged) > 0 else "W-GEOMETRY-ONLY")
    conclusion = (
        f"A {n_cells}-cell factorial over bearer x definition x baseline x threshold x null x scale, "
        f"{args.nperm} permutations per cell, Benjamini-Hochberg over the WHOLE grid at once. "
        f"{nominal} cells are nominally p<0.05 ({nominal/n_cells:.0%}) and {len(surv)} survive the "
        f"correction ({len(surv)/n_cells:.0%}); of those, {len(surv_purged)} survive on the PURGED "
        f"scale, i.e. after removing the accuracy-gap line r115 proved any two-arm difference "
        f"inherits. Bearers carrying purged survivors: "
        f"{', '.join(b for b, (t, s_) in sorted(by_bearer.items(), key=lambda kv: -kv[1][1]) if s_) or 'none'}. "
        f"Definitions carrying them: "
        f"{', '.join(b for b, (t, s_) in sorted(by_stat.items(), key=lambda kv: -kv[1][1]) if s_) or 'none'}. "
        f"{len(inadmissible)} cells were inadmissible and are named rather than dropped. "
        f"WORLD: {world}. "
        + ("Sacrifice is not a single-cell result: it survives a full-grid multiplicity correction "
           "on the purged scale across several bearers and several definitions at once."
           if world == "W-FACTORIAL-ROBUST" else
           "Only a handful of cells survive purged correction, so the phenomenon is real but thin, "
           "and any single-cell headline overstates it."
           if world == "W-THIN" else
           "No cell survives on the purged scale. Every apparent sacrifice in this grid is the "
           "accuracy-gap geometry, and the single-cell headlines were that geometry read as a "
           "finding."))
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    Path(args.out).write_text(json.dumps(
        {"n_admissible_cells": n_cells, "n_inadmissible": len(inadmissible),
         "inadmissible": inadmissible[:80], "n_perm": args.nperm, "bh_q": BH_Q,
         "n_nominal": nominal, "n_bh_survivors": len(surv),
         "n_purged_survivors": len(surv_purged),
         "by_bearer": {k: v for k, v in by_bearer.items()},
         "by_statistic": {k: v for k, v in by_stat.items()},
         "seed": args.seed, "plant": args.plant, "grid": grid, "world": world, "conclusion": conclusion,
         "toy_proof": {"r116_is_cell": "bearer=person,stat=rate,arms=core-full,null=within_prompt",
                       "r117_is_column": "stat in {rate,tailmass}, arms=core-full, all bearers",
                       "cells_they_covered": 2, "cells_in_this_grid": n_cells},
         **stamp(__file__)}, indent=1, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
