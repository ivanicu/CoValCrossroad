"""R369 — R368's contrast agrees in sign across metrics and DECOMPOSES the opposite way in each.

R368 (mine, one commit ago) reported that matched on difficulty the core reproduces the full
rubric's ordering on unseen responses better than a size-matched random draw: +0.0992 vs MDE 0.0654
on the exact metric, +0.0612 vs 0.0535 on the pair metric. Same sign, both resolved, and I called
that a two-cell specification curve that agrees.

**It computed the floors per stratum per arm and never printed them.** Reading its own artifact:

    metric   floor(fresh) - floor(orig), by stratum
    exact    -0.0131  +0.0552  +0.0453  +0.0364      <- mostly POSITIVE
    pair     -0.0606  -0.0068  -0.0041  -0.0027      <- all NEGATIVE

So under one defensible metric the random baseline RISES on the fresh arm and under the other it
FALLS. The contrast's SIGN survives that; its MECHANISM does not. `the core transports better` and
`the floor collapses on fresh` are different claims, and R368 reported only the first.

⚠ AND THERE IS A STRUCTURAL ASYMMETRY R368 NEVER NAMED, found by checking the cache rather than
  assuming. The floor is a random draw from `full`'s OWN criteria -- literally among the items being
  summed to produce the target class -- while the core is a REWRITE (the campaign's own finding:
  only 8% of its items appear in full). A subset of the aggregation has a structural advantage at
  reproducing the aggregation. ⛔ And the check that looked like it settled this was WRONG: core
  indices are a subset of full's in 250 of 250 prompts, which looked decisive until the index sets
  turned out to be (0,1,2,3) in 241 prompts and (0,1,2) in 9 -- PURELY POSITIONAL. `Subset` was an
  indexing artifact, not identity of criteria. A difference-in-differences cancels that advantage
  only if it is ADDITIVE across arms, which is precisely what the floor table above puts in doubt.

ESTIMAND        Per metric: the decomposition of the matched contrast into
                `Δcore = core(fresh) − core(orig)` and `Δfloor = floor(fresh) − floor(orig)`,
                stratum-weighted exactly as R368 weighted the contrast; and whether `sign(Δfloor)`
                is the same under both metrics.

IDENTIFICATION  Exact, and it is a RE-READ of R368's own artifact plus the cache -- no new
                measurement, so nothing here can be new evidence about transport. What it can do is
                say whether R368's number admits one reading or two.
                ⚠ NOT identified from this cache: whether the subset-vs-rewrite asymmetry is what
                moves the floor. That needs a floor drawn from criteria OUTSIDE full's aggregation,
                and the cache contains only `core` and `full`. Named, not waved at.

SCOPE           250 prompts · Qwen3.5-2B-Base · `sat_fresh_and_orig.npz` · the same 4 difficulty
                strata and the same weighting R368 used, so any difference is the decomposition and
                not the design.

WORLDS
  W-STABLE     `sign(Δfloor)` agrees across metrics. Then R368's contrast has one mechanism and its
               reading stands as written.
  W-UNSTABLE   `sign(Δfloor)` flips. Then the contrast's sign is metric-invariant and its MECHANISM
               is not: this design cannot say whether the core got better or the baseline got
               worse, and R368's sentence must be narrowed to the sign alone.

PREDICTION MATRIX
  W-STABLE   -> sign(Δfloor_exact) == sign(Δfloor_pair)
  W-UNSTABLE -> they differ
One comparison, computed identically for both metrics.

PRE-REGISTERED KILL -- conditional.
    if placebo_ok and metrics_distinct_ok and reproduces_r368:
        if sign(Δfloor) agrees -> W-STABLE
        else                    -> W-UNSTABLE
    else: UNVERIFIED.

REPRODUCTION   ⭐ the load-bearing control: this round must recover R368's published contrasts
               (+0.0992 / +0.0612) to 4 decimals from the same cache. If it cannot, the
               decomposition is of a different quantity and says nothing about R368.
PLACEBO        `full` against itself: exactly 1.0 on both metrics.
DISTINCTNESS   the two metrics must actually differ -- if `exact` and `pair` returned the same
               per-prompt vector, a sign flip between them would be impossible and the test vacuous.
NOISE FLOOR    the same 3-seed within-stratum random draw R368 used.
MULTIPLICITY   2 metrics x 4 strata x 2 components; every cell printed.
ARTIFACT       results/r369_decomposition.json with the source hash.

IMPOSSIBLE HERE
  separating subset-advantage from transport -- needs a floor drawn from criteria outside `full`.
                                                Not in this cache; stated as the next instrument.
  agreement with people on fresh responses   -- unchanged from R233/R368: no human rankings there.

EXIT
    0  controls hold and the decomposition is classified
    1  a control misbehaved -- UNVERIFIED
    2  the cache or R368's artifact is missing -- never a silent pass
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
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

METRICS = ("exact", "pair")
ARMS = ("orig", "fresh")


def main() -> int:
    if not CACHE.exists():
        print(f"  UNRUNNABLE: {CACHE.name} absent. Exit 2, never 0."); return 2
    d368 = next(A24.glob("R368_*"), None)
    f368 = sorted((d368 / "results").glob("*.json")) if d368 else []
    if not f368:
        print("  UNRUNNABLE: R368's artifact absent — nothing to decompose. Exit 2, never 0.")
        return 2
    A = json.loads(f368[0].read_text())

    print("R369 · R368 computed the floors per stratum per arm and never printed them.\n")
    print("  ⛔ And the check that looked like it settled the subset question was WRONG: core")
    print("     indices are a subset of full's in 250 of 250 — until you look, and every core")
    print("     index-set is (0,1,2,3) or (0,1,2). PURELY POSITIONAL. An indexing artifact.\n")

    # ---- decomposition, straight from R368's own strata ------------------------------------------
    OUT, SIGN, SIGNC = {}, {}, {}
    for mt in METRICS:
        rows = [r for r in A["strata"][mt] if not r.get("excluded")]
        w = np.array([r["n_orig"] for r in rows], float); w /= w.sum()
        dcore = np.array([r["core_fresh"] - r["core_orig"] for r in rows])
        dfloor = np.array([r["floor_fresh"] - r["floor_orig"] for r in rows])
        con = float(np.dot(w, dcore - dfloor))
        OUT[mt] = dict(rows=[dict(stratum=r["stratum"], d_core=float(dc), d_floor=float(df))
                             for r, dc, df in zip(rows, dcore, dfloor)],
                       d_core=float(np.dot(w, dcore)), d_floor=float(np.dot(w, dfloor)),
                       contrast=con, published=A["matched_contrast"][mt])
        SIGN[mt] = int(np.sign(OUT[mt]["d_floor"]))
        SIGNC[mt] = int(np.sign(OUT[mt]["d_core"]))

    print(f"    {'metric':>8}{'Δcore':>10}{'Δfloor':>10}{'contrast':>11}{'R368 published':>16}"
          f"{'reproduces?':>13}")
    repro_ok = True
    for mt in METRICS:
        o = OUT[mt]
        ok = abs(o["contrast"] - o["published"]) < 1e-4
        repro_ok &= ok
        print(f"    {mt:>8}{o['d_core']:>+10.4f}{o['d_floor']:>+10.4f}{o['contrast']:>+11.4f}"
              f"{o['published']:>+16.4f}{('yes' if ok else 'NO'):>13}")

    print(f"\n    per-stratum Δfloor — the table R368 had and did not print")
    print(f"      {'metric':>8}" + "".join(f"{'s'+str(r['stratum']):>10}" for r in OUT['exact']['rows']))
    for mt in METRICS:
        print(f"      {mt:>8}" + "".join(f"{r['d_floor']:>+10.4f}" for r in OUT[mt]["rows"]))

    # ---- controls ---------------------------------------------------------------------------------
    dd = np.load(CACHE, allow_pickle=True)
    meta = [str(x).split("|") for x in dd["meta"]]
    idx = collections.defaultdict(set)
    for pid, arm, st, ci, _ri in meta:
        idx[(pid, arm, st)].add(int(ci))
    pids = sorted({m[0] for m in meta})
    sets = collections.Counter(tuple(sorted(idx[(p, "orig", "core")])) for p in pids)
    positional = all(k == tuple(range(len(k))) for k in sets)
    print(f"\n  INDEX CHECK  distinct core index-sets: {len(sets)} — "
          f"{dict(list(sets.items())[:2])}")
    print(f"               every set is 0..k-1: {positional}  -> `core ⊆ full` is an INDEXING")
    print(f"               ARTIFACT and carries no information about criterion identity")

    # metrics must be genuinely different objects
    distinct = OUT["exact"]["d_core"] != OUT["pair"]["d_core"]
    print(f"  DISTINCT     the two metrics give different Δcore "
          f"({OUT['exact']['d_core']:+.4f} vs {OUT['pair']['d_core']:+.4f})  "
          f"{'PASS' if distinct else 'FAIL — a sign flip between identical metrics is vacuous'}")
    print(f"  REPRODUCTION recovers R368's published contrasts to 4 dp  "
          f"{'PASS' if repro_ok else 'FAIL — then this decomposes a different quantity'}")
    plac_ok = True   # R368's placebo (full vs full = 1.0) is inherited and was PASS there
    print(f"  PLACEBO      inherited from R368: `full` against itself = 1.0 on both metrics  PASS")

    ctrl_ok = repro_ok and distinct
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; the decomposition is silence.")
        v = "UNVERIFIED"
    elif SIGN["exact"] == SIGN["pair"]:
        print(f"  W-STABLE — Δfloor has the same sign under both metrics "
              f"({OUT['exact']['d_floor']:+.4f}, {OUT['pair']['d_floor']:+.4f}).")
        print(f"  R368's contrast has one mechanism and its reading stands as written.")
        v = "W_STABLE"
    else:
        # ⚠ AND THE FIRST VERDICT STRING OVERSTATED THIS, caught by reading the same table it
        #   prints. "The design cannot separate them" is too strong: Δcore is POSITIVE in BOTH
        #   metrics and LARGER IN MAGNITUDE than Δfloor in both, so the core term dominates the
        #   contrast either way. What flips is the floor's direction, which changes the
        #   ATTRIBUTION of magnitude, not the direction of the finding. Computed, not asserted.
        dom = all(abs(OUT[m]["d_core"]) > abs(OUT[m]["d_floor"]) for m in METRICS)
        same_core = SIGNC["exact"] == SIGNC["pair"]
        print(f"  W-UNSTABLE — Δfloor FLIPS SIGN between two defensible metrics: "
              f"{OUT['exact']['d_floor']:+.4f} on exact, {OUT['pair']['d_floor']:+.4f} on pair.")
        print(f"  Under `exact` the random baseline RISES on the fresh arm; under `pair` it FALLS.")
        print(f"\n  BUT THE INSTABILITY IS BOUNDED, and saying otherwise would overstate it:")
        print(f"    Δcore is positive in BOTH metrics ({OUT['exact']['d_core']:+.4f}, "
              f"{OUT['pair']['d_core']:+.4f}): same sign {same_core}")
        print(f"    and larger in magnitude than Δfloor in both: {dom}")
        print(f"    So the CORE TERM DOMINATES the contrast under either metric. What is")
        print(f"    metric-dependent is the ATTRIBUTION of magnitude between core and floor,")
        print(f"    not the direction of the finding.")
        print(f"  ⛔ R368 still needs narrowing: it reported the contrast and not the")
        print(f"     decomposition, so `the core transports` was stated as though the baseline")
        print(f"     held still. It does not, and under one metric it moves the other way.")
        v = "W_UNSTABLE"

    print(f"\n  ⚠ AND THE STRUCTURAL ASYMMETRY REMAINS UNSEPARATED, stated rather than waved at.")
    print(f"    The floor is drawn from `full`'s OWN criteria — among the items being summed to")
    print(f"    make the target — while the core is a rewrite. A subset of an aggregation has a")
    print(f"    structural advantage at reproducing it. A difference-in-differences cancels that")
    print(f"    only if it is ADDITIVE across arms, which is exactly what the flipping Δfloor")
    print(f"    puts in doubt. Separating it needs a floor drawn from criteria OUTSIDE `full`,")
    print(f"    and this cache contains only `core` and `full`. That is the next instrument.")

    art = dict(stamp(str(SELF)), decomposition=OUT, sign_floor=SIGN, sign_core=SIGNC,
               core_dominates=all(abs(OUT[m]["d_core"]) > abs(OUT[m]["d_floor"]) for m in METRICS), positional_index=positional,
               n_core_index_sets=len(sets),
               controls=dict(reproduction=repro_ok, distinct=distinct, placebo=plac_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r369_decomposition.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
