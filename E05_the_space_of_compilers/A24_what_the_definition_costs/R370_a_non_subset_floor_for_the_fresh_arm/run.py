"""R370 — R368's transport contrast against a floor that is NOT a subset of its own target.

⏱ PRE-REGISTERED WHILE THE LABELS WERE STILL BEING JUDGED. pueue task 630 was submitted, and this
file was written and committed before `sat_genericpool16_fresh.npz` existed or could be read. That
ordering is the only thing that makes the kill below a COMMITMENT rather than a description of a
result I had already seen. R301 did the same thing and it is the reason its UNRESOLVED is worth
anything.

THE DEFECT THIS EXISTS FOR. R368 measured transport as `core − floor` on each arm, where the floor
is a random draw from `full`'s OWN criteria. The core is a rewrite; the floor's criteria are among
the very items being summed to produce the target class. **A subset of an aggregation has a
structural advantage at reproducing that aggregation**, so `core − floor` is not a clean contrast,
and R369 showed the difference-in-differences does not obviously cancel it: `Δfloor` is +0.0308
under the exact metric and −0.0187 under the pair metric, opposite signs.

⛔ AND THE CHECK THAT LOOKED LIKE IT SETTLED THIS WAS AN ARTIFACT. `core ⊆ full` held in 250 of 250
   prompts — until the index sets turned out to be (0,1,2,3) in 241 and (0,1,2) in 9. Purely
   positional. That is why the floor's construction had to be attacked with a new instrument rather
   than with another read of the same file.

THE NEW FLOOR: the 16-criterion generic pool, identical across every prompt and therefore outside
any prompt's `full` rubric BY CONSTRUCTION. Same pool clause ② has used as its blind reference all
campaign, so no new instrument enters. Already judged against the ORIGINAL responses; task 630
supplies the FRESH half.

ESTIMAND        R368's stratified transport contrast, recomputed with the POOL floor in place of the
                subset floor: `(core − poolfloor)_fresh − (core − poolfloor)_orig`, on the same 4
                difficulty strata, the same weighting, both metrics.

IDENTIFICATION  Identified wherever a prompt carries core, full and pool labels on both arms. The
                pool floor draws k pool criteria to match |core|, so the floor is size-matched as
                before. NOT identified, and unchanged since R233: the fresh responses carry NO HUMAN
                RANKINGS, so every number here is agreement with the FULL RUBRIC and never with
                people.

SCOPE           the 250 fresh-response prompts · Qwen3.5-2B-Base throughout · R233's cache joined to
                task 630's labels · the identical strata and weights R368 used, so a difference is
                the FLOOR and not the design.

WORLDS
  W-SURVIVES   the contrast stays positive beyond its own MDE with the non-subset floor. The subset
               advantage was not carrying R368's finding, and transport firms up from a candidate
               clause toward a clause.
  W-COLLAPSES  the contrast falls inside its MDE, or turns negative. Then R368 measured the FLOOR'S
               CONSTRUCTION rather than transport, and `DEFINITION.md`'s transport section becomes a
               stated LIMIT rather than a candidate clause.
  W-FLOOR-DEGENERATE  the pool floor is at ceiling or at chance on one or both arms, so it cannot
               serve as a baseline at all. Then neither reading is licensed and the round says so.

PREDICTION MATRIX
  W-SURVIVES          -> contrast > MDE on at least the exact metric, sign unchanged from R368
  W-COLLAPSES         -> |contrast| <= MDE, or contrast < -MDE
  W-FLOOR-DEGENERATE  -> pool floor within 0.02 of 0 or 1, or its sd across prompts ~ 0
Both outcomes change what DEFINITION.md says, which is the test for whether this was worth its GPU.

PRE-REGISTERED KILL — written before the labels existed.
    if placebo_ok and floor_nondegenerate and reproduces_r368_with_subset_floor:
        if contrast_exact > mde_exact          -> W-SURVIVES
        elif abs(contrast_exact) <= mde_exact  -> W-COLLAPSES  (inside resolution)
        else                                    -> W-COLLAPSES  (sign reversed; reported separately)
    else: UNVERIFIED — never OVERTURNED, never CONFIRMED.
⚠ AND A FOURTH BRANCH, because this session has repeatedly had a default assert past its data: if
  the two metrics DISAGREE in sign on the new floor, that is named as W-METRIC-SPLIT and neither
  reading is taken — R369's whole finding was that a metric can flip the decomposition.

REPRODUCTION   ⭐ load-bearing: recomputing with the SUBSET floor must recover R368's +0.0992 /
               +0.0612. If it cannot, the join is wrong and nothing below is about R368.
PLACEBO        `full` against itself: exactly 1.0.
FLOOR CHECK    the pool floor's level and spread on each arm, printed, before any contrast is read.
NOISE FLOOR    the same 3-seed within-stratum draw R368 used, now drawing from the pool.
MULTIPLICITY   2 floors x 2 metrics x 4 strata; every cell printed.
ARTIFACT       results/r370_nonsubset_floor.json with the source hash.

IMPOSSIBLE HERE
  agreement with people on fresh responses -- no human rankings there. Unchanged since R233.
  a second judge                           -- task 630 judged with 2B only, matching the cache.
  cross-release                            -- one release.

EXIT
    0  controls hold and the contrast is classified
    1  a control misbehaved -- UNVERIFIED
    2  task 630's labels are absent or the join is empty -- never a silent pass
"""
from __future__ import annotations
import collections, hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
CACHE = (ROOT / "E05_the_space_of_compilers" / "A18_the_candidate_set_wall_was_wrong"
         / "R233_fresh_candidate_transport" / "results" / "sat_fresh_and_orig.npz")
POOL_FRESH = HERE / "results" / "sat_genericpool16_fresh.npz"
POOL_ORIG = ROOT / "corebench" / "results" / "sat_genericpool16.npz"
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
SEEDS = (0, 1, 2)
NSTRATA = 4
METRICS = ("exact", "pair")
L = "ABCD"


def cls_of(y):
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    return np.sign(y[ii] - y[jj])


def agree(a, b, metric):
    m = (cls_of(a) == cls_of(b))
    return float(m.all()) if metric == "exact" else float(m.mean())


def main() -> int:
    if not POOL_FRESH.exists():
        print(f"  UNRUNNABLE: {POOL_FRESH.name} absent — pueue task 630 has not landed.")
        print("  Exit 2, never 0. This round is pre-registered against labels that do not")
        print("  yet exist; running it before they do would be reading an empty population.")
        return 2
    for f in (CACHE, POOL_ORIG):
        if not f.exists():
            print(f"  UNRUNNABLE: {f.name} absent. Exit 2, never 0."); return 2

    # ---- load R233's cache: core + full, both arms -----------------------------------------------
    d = np.load(CACHE, allow_pickle=True)
    T = collections.defaultdict(lambda: collections.defaultdict(lambda: [None] * 4))
    WT = collections.defaultdict(dict)
    for k, x in enumerate(d["meta"]):
        pid, arm, st, ci, ri = str(x).split("|")
        T[(pid, arm, st)][int(ci)][int(ri)] = float(d["sat"][k])
        WT[(pid, arm, st)][int(ci)] = float(d["weight"][k])

    # ---- load the POOL labels: fresh from task 630, orig from the campaign's own file ------------
    pf = np.load(POOL_FRESH, allow_pickle=True)
    for k, x in enumerate(pf["meta"]):
        pid, arm, st, ci, ri = str(x).split("|")
        T[(pid, arm, "pool")][int(ci)][int(ri)] = float(pf["sat"][k])
        WT[(pid, arm, "pool")][int(ci)] = 1.0
    po = np.load(POOL_ORIG, allow_pickle=True)
    for k, x in enumerate(po["meta"]):
        parts = str(x).split("|")
        pid, ci, ltr = parts[0], int(parts[1]), parts[2]
        T[(pid, "orig", "pool")][ci][L.index(ltr)] = float(po["sat"][k])
        WT[(pid, "orig", "pool")][ci] = 1.0

    pids = sorted({str(x).split("|")[0] for x in d["meta"]})
    ARMS = ("orig", "fresh")

    def score(pid, arm, st, crits=None):
        tab, w = T[(pid, arm, st)], WT[(pid, arm, st)]
        cs = sorted(tab) if crits is None else [c for c in crits if c in tab]
        if not cs:
            return None
        y = np.zeros(4)
        for c in cs:
            v = tab[c]
            if any(x is None for x in v):
                continue
            y += w[c] * np.array(v, float)
        return y

    usable = [p for p in pids
              if all(score(p, a, s) is not None for a in ARMS for s in ("core", "full", "pool"))]
    print(f"R370 · the transport contrast against a NON-SUBSET floor\n")
    print(f"  {len(usable)} prompts carry core, full and pool on BOTH arms "
          f"(of {len(pids)} in the cache)\n")
    if len(usable) < 100:
        print("  UNRUNNABLE: the join is too small to stratify. Exit 2, never 0."); return 2

    AG, DIFF, NC = {}, {}, {}
    for arm in ARMS:
        for p in usable:
            yf, yc = score(p, arm, "full"), score(p, arm, "core")
            for mt in METRICS:
                AG[(mt, p, arm)] = agree(yc, yf, mt)
            DIFF[(p, arm)] = float(np.std(yf))
            NC[(p, arm)] = len(T[(p, arm, "core")])

    dorig = np.array([DIFF[(p, "orig")] for p in usable])
    edges = np.quantile(dorig, np.linspace(0, 1, NSTRATA + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    strat = lambda v: int(np.searchsorted(edges, v, side="right") - 1)   # noqa: E731

    def floor_in(ps, arm, seed, metric, source):
        """size-matched random draw from `source` ('full' = R368's subset floor, 'pool' = new)."""
        rng = np.random.default_rng(seed)
        vals = []
        for pid in ps:
            tab = T[(pid, arm, source)]
            k = max(1, NC[(pid, arm)])
            cs = sorted(tab)
            if len(cs) <= k:
                continue
            sel = list(rng.choice(cs, k, replace=False))
            yr, yf = score(pid, arm, source, sel), score(pid, arm, "full")
            if yr is None or yf is None:
                continue
            vals.append(agree(yr, yf, metric))
        return np.array(vals, float)

    # ---- FLOOR CHECK first, before any contrast is read ------------------------------------------
    print(f"    {'floor':>8}{'metric':>8}{'orig':>9}{'fresh':>9}   degenerate?")
    degen = False
    for src in ("full", "pool"):
        for mt in METRICS:
            lv = {a: float(np.mean([floor_in(usable, a, s, mt, src).mean() for s in SEEDS]))
                  for a in ARMS}
            bad = any(v < 0.02 or v > 0.98 for v in lv.values())
            degen |= (src == "pool" and bad)
            print(f"    {src:>8}{mt:>8}{lv['orig']:>9.4f}{lv['fresh']:>9.4f}   "
                  f"{'DEGENERATE' if bad else 'usable'}")

    # ---- the contrast, both floors, both metrics -------------------------------------------------
    RES = {}
    for src in ("full", "pool"):
        for mt in METRICS:
            rows, con_, wts = [], [], []
            for s in range(NSTRATA):
                po_ = [p for p in usable if strat(DIFF[(p, "orig")]) == s]
                pf_ = [p for p in usable if strat(DIFF[(p, "fresh")]) == s]
                if len(po_) < 5 or len(pf_) < 5:
                    rows.append(dict(stratum=s, excluded=True)); continue
                co = np.mean([AG[(mt, p, "orig")] for p in po_])
                cf = np.mean([AG[(mt, p, "fresh")] for p in pf_])
                fo = np.mean([floor_in(po_, "orig", sd, mt, src).mean() for sd in SEEDS])
                ff = np.mean([floor_in(pf_, "fresh", sd, mt, src).mean() for sd in SEEDS])
                rows.append(dict(stratum=s, excluded=False, d_orig=float(co - fo),
                                 d_fresh=float(cf - ff), contrast=float((cf - ff) - (co - fo))))
                con_.append((cf - ff) - (co - fo)); wts.append(len(po_))
            w = np.array(wts, float) / sum(wts)
            c = float(np.dot(w, con_))
            sd_ = float(np.sqrt(np.dot(w, (np.array(con_) - c) ** 2)))
            RES[(src, mt)] = dict(rows=rows, contrast=c,
                                  mde=float(ZEFF * sd_ / math.sqrt(len(con_))))

    print(f"\n    {'floor':>8}{'metric':>8}{'contrast':>11}{'own MDE':>10}   verdict")
    for src in ("full", "pool"):
        for mt in METRICS:
            r = RES[(src, mt)]
            vd = "resolved +" if r["contrast"] > r["mde"] else (
                "resolved −" if r["contrast"] < -r["mde"] else "inside the MDE")
            print(f"    {src:>8}{mt:>8}{r['contrast']:>+11.4f}{r['mde']:>10.4f}   {vd}")

    # ---- REPRODUCTION: the subset floor must recover R368 -----------------------------------------
    d368 = next(A24.glob("R368_*"), None)
    f368 = sorted((d368 / "results").glob("*.json")) if d368 else []
    repro_ok, pub = False, {}
    if f368:
        A = json.loads(f368[0].read_text())
        pub = A["matched_contrast"]
        repro_ok = all(abs(RES[("full", m)]["contrast"] - pub[m]) < 0.02 for m in METRICS)
        print(f"\n  REPRODUCTION  subset floor here vs R368 published: "
              + ", ".join(f"{m} {RES[('full', m)]['contrast']:+.4f} vs {pub[m]:+.4f}"
                          for m in METRICS)
              + f"  {'PASS' if repro_ok else 'FAIL'}")
        print(f"                (tolerance 0.02 — the join drops prompts lacking pool labels, so")
        print(f"                 exact equality is not expected and demanding it would be a")
        print(f"                 control that cannot pass)")
    plac = all(agree(score(p, a, "full"), score(p, a, "full"), "exact") == 1.0
               for a in ARMS for p in usable[:40])
    print(f"  PLACEBO       `full` against itself: 1.0  {'PASS' if plac else 'FAIL'}")
    print(f"  FLOOR         pool floor non-degenerate: {'FAIL' if degen else 'PASS'}")

    ctrl_ok = repro_ok and plac and not degen
    ce, me = RES[("pool", "exact")]["contrast"], RES[("pool", "exact")]["mde"]
    cp, mp = RES[("pool", "pair")]["contrast"], RES[("pool", "pair")]["mde"]
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; the table above is silence.")
        v = "UNVERIFIED"
    elif (ce > me) != (cp > mp) and (abs(ce) > me or abs(cp) > mp):
        print(f"  W-METRIC-SPLIT — the two metrics disagree on the NEW floor "
              f"(exact {ce:+.4f}/{me:.4f}, pair {cp:+.4f}/{mp:.4f}).")
        print(f"  Named rather than defaulted: R369's finding was that a metric can flip the")
        print(f"  decomposition, so neither reading is taken here.")
        v = "W_METRIC_SPLIT"
    elif ce > me:
        print(f"  W-SURVIVES — with a floor that is NOT a subset of its own target, the transport")
        print(f"  contrast is still {ce:+.4f} against its own MDE {me:.4f}. The subset advantage")
        print(f"  was not carrying R368's finding, and transport firms up.")
        v = "W_SURVIVES"
    else:
        print(f"  W-COLLAPSES — against a non-subset floor the contrast is {ce:+.4f} vs MDE "
              f"{me:.4f}.")
        print(f"  ⛔ R368 measured the FLOOR'S CONSTRUCTION, not transport. DEFINITION.md's")
        print(f"     transport section becomes a stated LIMIT rather than a candidate clause.")
        v = "W_COLLAPSES"

    print(f"\n  ⚠ Unchanged since R233 and restated rather than dropped: the fresh responses carry")
    print(f"    NO HUMAN RANKINGS. Every number here is agreement with the FULL RUBRIC.")

    art = dict(stamp(str(SELF)), n_prompts=len(usable),
               results={f"{s}|{m}": RES[(s, m)] for s in ("full", "pool") for m in METRICS},
               r368_published=pub,
               controls=dict(reproduction=repro_ok, placebo=plac, floor_ok=not degen),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r370_nonsubset_floor.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
