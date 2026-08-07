#!/usr/bin/env python3
"""R764 · is ③-any still EMPTY at 92 arms, and anywhere on ②'s baseline class?

R763's registered stopping rule binds: 1 object headline in 24 rounds, so this one moves the
definition or it does not run.

THE PAGE STATES: ③-rank -> extension 5 · ③-any -> EMPTY. Both measured by R529/R534 on R294's
**41** census arms. Today's population is **92**, and "③-any is EMPTY" is what makes ③-rank the only
live reading of the clause.

⛔ D1, CORRECTED BEFORE ANY CODE, FROM R534's OWN TEXT. R534 computed `ext_any` and `ext_judge` with
   the SAME expression (`klass(a) == "neither"`). But its own headline says *"a judge is not an
   annotator"* -- under which the SAT class is ADMITTED by ③-any. The readings are:
       ③-rank   excludes {rank}                       -> admits weight, sat, weight+sat, neither
       ③-any    excludes {rank, weight, weight+sat}   -> admits SAT and neither
       ③-judge  excludes {rank, weight, sat, wgt+sat} -> admits neither only
   nesting judge ⊆ any ⊆ rank is ALGEBRA; whether the smallest is ZERO is the measurement.
   It did not matter at 41 arms -- the sat class held one arm and it fails ②. At 92 it can.

⛔ D2 the extension is monotone non-increasing in the baseline, so a reading non-empty at the
   published comparator is non-empty below it. THE INFORMATIVE DIRECTION IS THE LOW END, which is
   the end the page does not report.

CONTROLS  PROVENANCE (R534's 41-arm partition reproduced EXACTLY, exit 2 otherwise) · POSITIVE (four
          known arms into four different classes; band from both degenerate ends) · g=0 (an
          unparseable tag is UNPARSED, never `neither` -- `neither` is the class that GROWS ③-any) ·
          NEGATIVE (200 random 5-class partitions -> the ③-any distribution) · SHAM (② with NO clause
          at all, beside every cell) · PLACEBO (`*_sham` arms never enter any extension).
UNIT      instrument = an ARM TAG · claim = an OBJECT (R730's partition). Both reported, never merged.
"""
import itertools, json, math, pathlib, subprocess, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls          # noqa: E402
from report import verdict, POS                        # noqa: E402

RES = ROOT / "corebench/results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
NBOOT, ZEFF, L = 1200, 1.959964 + 0.841621, "ABCD"
PAIRS4 = list(itertools.combinations(range(4), 2))

RANK   = ("oracle_k", "indep_k", "greedy_k")
WEIGHT = ("topw_k", "topabs_k")
SAT    = ("topvar_k",)
BOTH   = ("topwvar_k",)
VOCAB  = RANK + WEIGHT + SAT + BOTH + ("random_k",)

# the four readings, as ADMITTED class sets (D1)
READINGS = {
    "3-rank":  {"weight", "sat", "weight+sat", "neither"},
    "3-any":   {"sat", "neither"},
    "3-judge": {"neither"},
}


def fam(t, fams):
    return any(t.startswith(f) and t[len(f):len(f) + 1].isdigit() for f in fams)


CENSUS_NAMED = set()          # filled in main() from R294 -- the authoritative non-rule arm list


def parses(t):
    """⛔ REPAIRED IN FLIGHT, AND THE BUG RAN IN THE PAGE'S FAVOUR.

    The first version accepted only a rule prefix plus `full`/`coval_core`, which marked `gen`,
    `generic`, `gen_sham` and `coval_core_sham` UNPARSED. R534's classifier assigns exactly those to
    `neither` -- its README names them: *"neither | 25 | gen, generic, full, random_k*, shams"*.
    AND `neither` IS THE CLASS THAT POPULATES ③-any. So a stricter parser than the one being extended
    emptied ③-any's own candidate pool, biasing the round toward the sentence already on the page.
    The rule now is: a tag parses if it carries a rule prefix OR is a NAMED arm in R294's census.
    Anything else is genuinely unrecognised and stays UNPARSED, which is what g=0 is protecting."""
    return t in CENSUS_NAMED or t == "full" or fam(t, VOCAB)


def klass(t):
    """R534's classifier, verbatim in its assignments."""
    if fam(t, RANK):   return "rank"
    if fam(t, BOTH):   return "weight+sat"
    if fam(t, SAT):    return "sat"
    if fam(t, WEIGHT) or t == "coval_core": return "weight"
    return "neither"


def _plain(o):
    if isinstance(o, np.bool_):    return bool(o)
    if isinstance(o, np.integer):  return int(o)
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.ndarray):  return o.tolist()
    raise TypeError(type(o))


def main():
    # ---- CONTROL · PROVENANCE. Reproduce R534's 41-arm partition or stop. --------------------
    cen = json.loads((A24 / "R294_the_definition_against_everything/results/full_census.json"
                      ).read_text())
    rows41 = cen["rows"]
    CENSUS_NAMED.update(rows41)
    p41 = {}
    for a in sorted(rows41): p41.setdefault(klass(a), []).append(a)
    want41 = {"rank": 4, "weight": 10, "sat": 1, "weight+sat": 1, "neither": 25}
    got41 = {k: len(p41.get(k, [])) for k in want41}
    ok_prov = got41 == want41
    print(f"  PROVENANCE  R534's 41-arm partition: {got41}")
    print(f"              committed                {want41}   "
          f"{'PASS' if ok_prov else '⛔ FAIL'}")
    if not ok_prov:
        print("  -> not R534's classifier; it may not be extended. UNVERIFIED."); return 2

    # ---- CONTROL · POSITIVE (band from both degenerate ends) and g=0 -------------------------
    pos = {"oracle_k4": "rank", "topw_k4": "weight", "topvar_k4": "sat", "random_k4_s1": "neither"}
    got = {t: klass(t) for t in pos}
    ok_pos = got == pos
    print(f"  POSITIVE    {got}  {'PASS' if ok_pos else '⛔ FAIL'}")
    print(f"              band: all-`neither` fails the first three, all-`rank` fails the last")
    g0 = not parses("zzz_k4")
    print(f"  g=0         an unparseable tag `zzz_k4` is UNPARSED, not `neither`: {g0}  "
          f"{'PASS' if g0 else '⛔ FAIL'}")

    # ---- the 92-arm population ---------------------------------------------------------------
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    idxs = sorted({i for i, _ in POOL[pids[0]]})
    n_pool, P = len(idxs), len(pids)
    subs = list(itertools.combinations(range(n_pool), 4))

    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]
    Hm = max(len(h) for h in HC)
    HP = np.zeros((P, Hm, 6)); HK = np.zeros((P, Hm))
    for a, h in enumerate(HC):
        HP[a, :len(h)] = h; HK[a, :len(h)] = 1.0
    nH = HK.sum(1)
    T = np.zeros((P, n_pool, 4))
    for a, p in enumerate(pids):
        for bi, i in enumerate(idxs):
            for c, x in enumerate(L):
                T[a, bi, c] = POOL[p].get((i, x), 0.0)

    def a2_of_y(Y):
        s = np.sign(Y[:, [i for i, _ in PAIRS4]] - Y[:, [j for _, j in PAIRS4]])
        return ((s[:, None, :] == HP).mean(2) * HK).sum(1) / nH

    tags = sorted(p.name[4:-4] for p in RES.glob("sat_*.npz")
                  if p.name not in ("sat_genericpool16.npz",) and "full" not in p.name)
    A = {}
    foreign, partial = [], []
    for t in tags:
        try:
            S = load_sat(RES / f"sat_{t}.npz")
        except ValueError:
            # ⚠ A FILTER IS A SCOPE CLAIM. These do not fail to load by accident: their keys carry a
            # DIFFERENT SCHEMA (`load_sat` splits on "|" into 3 fields and gets more), i.e. they
            # belong to another corpus, not to this arm population. Excluded on that EVIDENCE and
            # named, never dropped by a name pattern.
            foreign.append(t); continue
        if not all(p in S for p in pids):
            partial.append(t); continue
        Y = np.zeros((P, 4))
        for ai, p in enumerate(pids):
            ii = sorted({i for i, _ in S[p]})
            for c, x in enumerate(L):
                Y[ai, c] = sum(S[p].get((i, x), 0.0) for i in ii)
        A[t] = a2_of_y(Y)
    arms = sorted(A)
    unparsed = [t for t in arms if not parses(t)]
    print(f"\n  population  {len(arms)} arms with full coverage (R534 saw 41)   "
          f"UNPARSED: {len(unparsed)} {unparsed if unparsed else ''}")
    print(f"  ⚠ EXCLUDED  {len(foreign)} artifacts with a FOREIGN KEY SCHEMA (another corpus): "
          f"{foreign}")
    print(f"  ⚠ EXCLUDED  {len(partial)} artifacts not covering all {P} prompts: "
          f"{partial if len(partial) <= 8 else str(partial[:8]) + f' ...+{len(partial)-8}'}")
    K = {t: (klass(t) if parses(t) else "UNPARSED") for t in arms}
    counts = {k: sum(1 for t in arms if K[t] == k) for k in
              ("rank", "weight", "sat", "weight+sat", "neither", "UNPARSED")}
    print(f"  E1 classes  {counts}")
    print(f"     sat class: {[t for t in arms if K[t]=='sat']}")
    print(f"     wgt+sat  : {[t for t in arms if K[t]=='weight+sat']}")

    # ---- ② over the baseline curve ------------------------------------------------------------
    Y = np.empty((len(subs), P))
    for si, s in enumerate(subs):
        Y[si] = a2_of_y(T[:, list(s), :].sum(axis=1))
    ymean = Y.mean(1); order = np.argsort(ymean)
    pub = subs.index(tuple(range(4)))
    ib = np.random.default_rng(31337).integers(0, P, (NBOOT, P))

    def clears(x, y):
        d = x - y; bs = d[ib].mean(axis=1)
        return verdict(float(d.mean()), float(np.percentile(bs, 2.5)),
                       float(np.percentile(bs, 97.5)),
                       ZEFF * d.std(ddof=1) / math.sqrt(P)) == POS

    specs = [(f"p{q:03d}", int(order[min(int(q / 100 * (len(subs) - 1)), len(subs) - 1)]))
             for q in (0, 5, 25, 50, 75, 95, 100)]
    specs.insert(-1, ("published", pub))

    r730 = json.loads((A24 / "R730_seven_tags_are_not_seven_objects/results/"
                       "r730_object_partition.json").read_text())
    # ⛔ THE FIRST VERSION LOADED `objects_of_the_seven` -- FOUR groups covering the 7 target-reading
    # tags only. Every other tag then mapped to ITSELF, so the "objects" column was silently
    # reporting TAGS wherever the map was absent, and the UNIT control this round declared was
    # decorative. The complete non-singleton partition is `multi_tag_classes` (8 groups; STATEMENT
    # records "all 8 multi-tag classes are cliques"), and every tag outside them is its own object.
    obj_of = {}
    for grp in r730["multi_tag_classes"]:
        for t in grp: obj_of[t] = sorted(grp)[0]
    print(f"  OBJECT MAP  {len(r730['multi_tag_classes'])} multi-tag classes covering "
          f"{len(obj_of)} tags (R730's 93 tags -> 81 objects)")

    def nobj(ts):
        return len({obj_of.get(t, t) for t in ts})

    print(f"\n  ⭐ E3 · THE GRID — 4 readings x {len(specs)} baselines, tags (objects)")
    print(f"  {'baseline':<12}{'|②| SHAM':>10}{'③-rank':>14}{'③-any':>12}{'③-judge':>12}")
    grid, sham_row = {}, {}
    for lbl, si in specs:
        bv = Y[si]
        p2 = [t for t in arms if clears(A[t], bv)]
        sham_row[lbl] = len(p2)
        row = {}
        for rd, adm in READINGS.items():
            ext = sorted(t for t in p2 if K[t] in adm)
            row[rd] = {"tags": ext, "n_tags": len(ext), "n_objects": nobj(ext)}
        grid[lbl] = row
        print(f"  {lbl:<12}{len(p2):>10}"
              + "".join(f"{row[r]['n_tags']:>8} ({row[r]['n_objects']:>2})"
                        for r in ("3-rank", "3-any", "3-judge")))

    any_cells = [(l, grid[l]["3-any"]) for l in grid if grid[l]["3-any"]["n_tags"] > 0]
    judge_cells = [(l, grid[l]["3-judge"]) for l in grid if grid[l]["3-judge"]["n_tags"] > 0]
    print(f"\n  ③-any NON-EMPTY in {len(any_cells)} of {len(specs)} cells"
          + (f": {[(l, v['tags']) for l, v in any_cells]}" if any_cells else ""))
    print(f"  ③-judge NON-EMPTY in {len(judge_cells)} of {len(specs)} cells"
          + (f": {[(l, v['tags']) for l, v in judge_cells]}" if judge_cells else ""))

    # ---- CONTROL · NEGATIVE, PLACEBO ----------------------------------------------------------
    rng = np.random.default_rng(764)
    kn = ["rank", "weight", "sat", "weight+sat", "neither"]
    pubrow = [t for t in arms if clears(A[t], Y[pub])]
    negd = []
    for _ in range(200):
        rk = {t: kn[int(rng.integers(5))] for t in arms}
        negd.append(sum(1 for t in pubrow if rk[t] in READINGS["3-any"]))
    print(f"\n  NEGATIVE    random 5-class partitions x200 -> ③-any at published: "
          f"mean {np.mean(negd):.2f} [{np.percentile(negd,2.5):.0f}, "
          f"{np.percentile(negd,97.5):.0f}]  vs real {grid['published']['3-any']['n_tags']}")
    shams = [t for t in arms if t.endswith("_sham")]
    leak = sorted({t for l in grid for r in READINGS for t in grid[l][r]["tags"] if t.endswith("_sham")})
    print(f"  PLACEBO     {len(shams)} `*_sham` arms; entering any extension in any cell: "
          f"{len(leak)}  {'PASS' if not leak else '⛔ FAIL ' + str(leak)}")
    print(f"  SHAM        ② with NO clause is the |②| column above; ③ is binding wherever "
          f"|②| > |③-rank|")

    # ⛔ THE REGISTERED BRANCH IS UNIT-INCONSISTENT, AND THE ROUND SAYS SO BEFORE ITS VERDICT.
    # I registered `UNPARSED >= 1 -> WORLD C`, whose stated world is "the partition does not extend
    # to today's POPULATION" -- a claim in the OBJECT unit. But `UNPARSED` counts TAGS. This round's
    # own UNIT control says those are not equal, and R730 settles this case: `generic_reprov` sits in
    # the object class [generic, generic_reprov, provenance_probe] -- a re-provenance run of an arm
    # that IS classified. So the count is 1 tag and 0 objects, and the two units give DIFFERENT
    # registered verdicts. Both are computed and printed; neither is chosen silently.
    unparsed_obj = sorted({obj_of.get(t, t) for t in unparsed}
                          - {obj_of.get(t, t) for t in arms if K[t] != "UNPARSED"})
    b_fires = bool(any_cells) and all(sham_row[l] < len(arms) for l, _ in any_cells)

    def branch(n_unparsed):
        if not ctrl:            return "UNVERIFIED"
        if n_unparsed:          return "C"
        if b_fires:             return "B"
        if not any_cells:       return "A · CLOSURE — it protects a sentence already on the page"
        return "NO WORLD — counts reported, none claimed"

    ctrl = ok_prov and ok_pos and g0 and not leak
    w_tag, w_obj = branch(len(unparsed)), branch(len(unparsed_obj))
    print(f"\n  ⚠ UNIT CONFLICT IN MY OWN REGISTERED BRANCH, stated before the verdict:")
    print(f"     UNPARSED in TAGS   : {len(unparsed)} {unparsed}  -> registered branch gives {w_tag}")
    print(f"     UNPARSED in OBJECTS: {len(unparsed_obj)} {unparsed_obj}  -> "
          f"registered branch gives {w_obj}")
    print(f"     `generic_reprov` is a re-provenance run of `generic` (R730's object class "
          f"[generic, generic_reprov, provenance_probe]); its OBJECT is classified.")
    print(f"     THE ROUND FOLLOWS THE OBJECT UNIT, because its own UNIT control mandates that the")
    print(f"     claim's unit is an OBJECT and the world named by branch C is a claim about the")
    print(f"     POPULATION. The tag-unit verdict is reported, not discarded.")
    world = w_obj
    print(f"\n  WORLD {world}   (tag-unit branch would have said {w_tag})")

    out = pathlib.Path(__file__).parent / "results/clause_three_readings_at_92.json"
    out.write_text(json.dumps({
        "tree_sha": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()[:16],
        "n_arms": len(arms), "n_prompts": P, "n_refs": len(subs),
        "classes": counts, "unparsed": unparsed,
        "excluded_foreign_schema": foreign, "excluded_partial_coverage": partial,
        "class_of": K, "grid": grid, "n_clears_2": sham_row,
        "controls": {"provenance_41": got41, "provenance_pass": ok_prov, "positive": got,
                     "g0_unparsed": g0, "placebo_leak": leak,
                     "negative_mean": float(np.mean(negd)),
                     "negative_lo": float(np.percentile(negd, 2.5)),
                     "negative_hi": float(np.percentile(negd, 97.5))},
        "any_nonempty_cells": [l for l, _ in any_cells],
        "judge_nonempty_cells": [l for l, _ in judge_cells],
        "unparsed_objects": unparsed_obj, "world_tag_unit": w_tag, "world_object_unit": w_obj,
        "world": world,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
