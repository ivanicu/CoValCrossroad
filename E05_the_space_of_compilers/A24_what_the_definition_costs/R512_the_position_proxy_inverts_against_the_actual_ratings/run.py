"""R508 measured POSITION as a proxy for "picked highly-rated items". The ratings are on disk.

WHY. R508 built a provenance surrogate from the normalised POSITION of an arm's selected criteria in
`coval_full`'s list, and concluded that every label-OPTIMISER is caught while rule-based selectors
escape. Position was never the property; it was a proxy for "selected the highly-rated items". The
ratings themselves are in the release — `coval_full[i].scores`, per annotator — and R468's
`id_map.json` joins corebench's prompt ids to the release's conversations at 968 of 968. So the
proxy can be replaced by the thing it stood for, and CHECKED against it.

⛔ AND THE JOIN ALREADY EXISTED. I ran a comparison last round that returned `nan% of 0` for want of
exactly this map, which R468 built and committed. Second time in three rounds that the instrument
needed was already in this repository — recorded because the prior-art gate is aimed at libraries
and never at my own tools.

ESTIMAND        Per arm: the mean PERCENTILE of its selected criteria's average rating within that
                prompt's own rated pool. Named before the method. This is the quantity the dataset
                card names — "up to four rubric items with the highest average ratings" — and
                position was only ever a stand-in for it.
IDENTIFICATION  Exact for arms whose criteria appear verbatim in `coval_full`. Arms with no pool
                overlap have no rating data and are reported N/A, never as a number.
SCOPE           population = arms with criterion text joined through id_map.json · instrument =
                mean per-annotator score per pool item, percentile within the prompt's pool ·
                baseline = the three random_k4 seeds · regime = first release.
WORLDS          A THE PROXY HELD. Position and rating agree on which arms separate. R508 stands.
                B THE PROXY LOST RECALL. Rating catches more, position a subset. R508 is incomplete.
                C THE PROXY INVERTED. The arms position called caught sit at the random baseline on
                  ratings, and the ones it missed are the ones above it. R508 is void, not partial.
KILL            Pre-registered: if any arm R508 reported as SEPARATING sits within the random arms'
                rating band, world A is dead; if the arms it MISSED sit above that band, world C.
POSITIVE CTRL   `topw_k4` selects top-WEIGHTED items by construction, so it must score high on
                ratings. If it does not, the rating instrument is broken and nothing here reads.
NEGATIVE CTRL   The three `random_k4` seeds must cluster together and near the middle; they select
                uniformly, so a spread among them bounds the noise.
PLACEBO         `gen` and `generic` have 0% pool overlap (R503), so they have no rating data at all.
                They must be reported N/A — a number for them would mean the join is fabricating.
NOISE FLOOR     The spread across the three random seeds.
MULTIPLICITY    Every arm with criterion text is reported; none selected after the fact.
ARTIFACT        results/rating_percentile.json
IMPOSSIBLE      `coval_core` cannot be tested this way: 6.6% of its criteria appear verbatim in
                `coval_full` because the card documents a REWRITE step before selection. It would
                require a mapping from rewritten core items back to their source items, which the
                release does not ship.
"""
from __future__ import annotations
import json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
R = ROOT/"corebench"/"results"
OUT = pathlib.Path(__file__).resolve().parent/"results"; OUT.mkdir(exist_ok=True)
IDMAP = json.loads((ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/"
                    "R468_the_join_exists_and_is_exact/results/id_map.json").read_text())
READERS = ["oracle_k4","greedy_k4_fit1","indep_k4_fit1","topw_k4","topw_k8","topwvar_k4"]
FREE = ["random_k4_s0","random_k4_s1","random_k4_s2","gen","generic"]
R508_SEPARATES = {"oracle_k4","greedy_k4_fit1","indep_k4_fit1"}   # the "honest" catches
R508_MISSED = {"topw_k8","topwvar_k4"}


def pool_map():
    pool = {}
    with (ROOT/"data/conversation_rubrics.jsonl").open() as f:
        for line in f:
            r = json.loads(line)
            pool[r["conversation"]["id"]] = {
                c["criterion"]: float(np.mean([s["score"] for s in c["scores"]]))
                for c in r.get("coval_full") or [] if c.get("scores")}
    return pool


def pct(arm, pool):
    p = R/f"core_{arm}.json"
    if not p.exists(): return np.array([])
    o = json.loads(p.read_text()); out = []
    for pid, cs in o.items():
        pl = pool.get(IDMAP.get(pid)) or {}
        if len(pl) < 3: continue
        vals = np.array(sorted(pl.values()))
        for c in (cs if isinstance(cs, list) else []):
            if c in pl: out.append(float((vals < pl[c]).mean()))
    return np.array(out)


def main() -> int:
    pool = pool_map()
    if len(pool) < 500:
        print(f"  only {len(pool)} rated conversations -- refusing to report"); return 2
    rows = {a: pct(a, pool) for a in READERS + FREE}
    rnd = [rows[a].mean() for a in ("random_k4_s0","random_k4_s1","random_k4_s2") if len(rows[a])]
    if len(rnd) < 3:
        print("  the random arms produced no rating data -- no null"); return 2
    floor = max(rnd) - min(rnd)
    band = (min(rnd) - 2*floor, max(rnd) + 2*floor)

    print(f"  {'arm':<20}{'n':>7}{'mean rating pctile':>21}   note")
    for a in READERS + FREE:
        v = rows[a]
        if not len(v):
            print(f"  {a:<20}{0:>7}{'N/A':>21}   no pool overlap (R503) — reported N/A, not 0")
            continue
        tag = ""
        if a in R508_SEPARATES: tag = "R508 said SEPARATES"
        elif a in R508_MISSED: tag = "R508 said MISSED"
        print(f"  {a:<20}{len(v):>7}{v.mean():>21.4f}   {tag}")

    print(f"\n  NEGATIVE CONTROL: random_k4 seeds {[round(x,4) for x in rnd]}  spread {floor:.4f}")
    print(f"  null band [{band[0]:.4f}, {band[1]:.4f}]")
    pc = rows["topw_k4"].mean() > band[1] if len(rows["topw_k4"]) else False
    print(f"  POSITIVE CONTROL: topw_k4 selects top-WEIGHTED items, so must score high: "
          f"{rows['topw_k4'].mean():.4f} -> {'PASS' if pc else 'FAIL'}")
    if not pc:
        print("  the rating instrument cannot see a construction that must score high"); return 1
    pl_ok = all(len(rows[a]) == 0 for a in ("gen", "generic"))
    print(f"  PLACEBO: gen and generic have no rating data -> {'PASS' if pl_ok else 'FAIL'}")

    caught_now = {a for a in R508_SEPARATES if len(rows[a]) and rows[a].mean() > band[1]}
    missed_now = {a for a in R508_MISSED if len(rows[a]) and rows[a].mean() > band[1]}
    world = ("C THE PROXY INVERTED" if not caught_now and missed_now else
             "A THE PROXY HELD" if caught_now == R508_SEPARATES and not missed_now else
             "B THE PROXY LOST RECALL")
    print(f"\n  of the arms R508 said SEPARATE, above the rating band now: {sorted(caught_now)}")
    print(f"  of the arms R508 said it MISSED,  above the rating band now: {sorted(missed_now)}")
    print(f"\n  WORLD: {world}")
    if world.startswith("C"):
        print(f"  => `coval_full`'s list order is NOT rating order. Position measured WHERE an item")
        print(f"     sits; ③′ is about HOW HIGHLY it was rated. R508 is void, not partial, and every")
        print(f"     conclusion it drew about which provenance is detectable goes with it.")
    json.dump({"means": {a: (float(v.mean()) if len(v) else None) for a, v in rows.items()},
               "n": {a: int(len(v)) for a, v in rows.items()}, "band": band, "floor": floor,
               "caught_now": sorted(caught_now), "missed_now": sorted(missed_now),
               "positive_control": bool(pc), "placebo": bool(pl_ok), "world": world},
              (OUT/"rating_percentile.json").open("w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
