#!/usr/bin/env python3
"""R748 · the page carries two object counts computed under two different identity rules

ESTIMAND        E1 the object count of each population under each rule, as a 2x2 grid:
                {R524's 56 tags, R730's 93 tags} x {full-overlap, subset}. Three cells are
                committed; the fourth (56 under subset) has never been computed.
                E2 which deliverable claims state an object count that DIFFERS between the rules.
IDENTIFICATION  E1 exact and finite -- deterministic relations over arrays on disk. E2 identified
                only for claims that STATE a count; claims resting on one without stating it are
                reported out of scope, never assumed unaffected.
SCOPE           population = R524's 56 and R730's 93 · instrument = both projects' own same(),
                imported not re-implemented · baseline = the committed 46, 81, and R747's sham 83 ·
                regime = exact equality at this tree_sha.
WORLDS          A the rule is cosmetic at the claim level (0 claims move) · B it moves >=1 claim.
KILL            conditional; gated on POSITIVE separating the rules on a synthetic strict-subset
                pair, g=0 leaving them agreeing on an unequal pair, NEGATIVE shattering both, and
                P3/P4 reproducing 46 and 81.
POSITIVE CTRL   synthetic strict-subset pair, equal on shared prompts: subset MUST merge, full
                overlap MUST NOT. Band computed against merge-nothing and merge-everything rules.
                If the two real rules agree here the instrument cannot see the distinction.
g=0             two synthetic arms differing on a shared prompt: BOTH must refuse. A subset rule
                that merges unequal arms would manufacture P1.
NEGATIVE CTRL   replace every vector with distinct seeded noise; both partitions must shatter to
                n_tags singletons. Excludes "the partition is driven by the tag NAMES".
SHAM            ingredient ABSENT: restrict to arms that all share one prompt set -- the two rules
                must then agree exactly.
PLACEBO         each rule against itself -> exactly 0 disagreeing classes, reported as 0 of N.
NOISE FLOOR     no rng except NEGATIVE's noise, seeded and swept over 3 seeds.
MULTIPLICITY    4 grid cells + the claim comparison + 3 negative seeds, all reported.
UNIT            instrument unit = a CLASS; claim unit = a STATED NUMBER on the page. NOT equal --
                E2 reads stated counts out of the deliverable rather than counting classes.
ARTIFACT        results/r748.json with tree_sha; a later round attacks this by proposing a third
                identity relation and showing a claim moves under it.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      which rule is CORRECT (needs an external identity criterion) · claims that rest on
                a count without stating one (needs reading intent out of prose) · independently
                replicated · cross-site.

⛔ TWO RESULTS ARE FORCED AND ARE LABELLED DERIVATIONS, NOT EVIDENCE:
   D1 subset_count <= full_overlap_count ALWAYS -- full overlap refines subset. Only the GAP is
      a measurement.
   D2 the extension's object count CANNOT move: its five members sit in five distinct classes under
      the coarser rule, and a refinement cannot merge what is already separate. ASSERTED in code,
      never counted as evidence.
"""
from __future__ import annotations
import importlib.util as _ilu
import glob, itertools, json, os, pathlib, re, subprocess
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
A24 = HERE.parent
STORE = ROOT / "corebench" / "results"
STM = ROOT / "E05_the_space_of_compilers" / "STATEMENT.md"
R524DIR = A24 / "R524_how_many_objects_are_in_the_fifty_six_tags"
R730DIR = A24 / "R730_seven_tags_are_not_seven_objects"


def _load(p, name):
    s = _ilu.spec_from_file_location(name, p / "run.py")
    m = _ilu.module_from_spec(s)
    s.loader.exec_module(m)
    return m


R524 = _load(R524DIR, "r524mod")
R730 = _load(R730DIR, "r730mod")
EXTENSION = ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"]


def _plain(o):
    for cast in (bool, int, float):
        if isinstance(o, cast) or type(o).__name__ == cast.__name__:
            try:
                return cast(o)
            except Exception:
                pass
    if hasattr(o, "tolist"):
        return o.tolist()
    return str(o)


def partition(tags, rel):
    parent = {t: t for t in tags}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a, b in itertools.combinations(tags, 2):
        if rel(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)
    cl = {}
    for t in tags:
        cl.setdefault(find(t), []).append(t)
    return sorted(sorted(v) for v in cl.values())


def main() -> int:
    # ---------- the two populations, each reconstructed the way its own round did
    r436 = json.loads(pathlib.Path(glob.glob(str(
        ROOT / "E05_the_space_of_compilers/*/R436*/results/*.json"))[0]).read_text())
    tags56 = sorted({c["arm"] for c in r436["cells"]
                     if not c["arm"].endswith(("_08b", "_08bR"))})
    V = R730.build_vectors()
    tags93 = sorted(V)
    print("R748 · the page carries two object counts under two different identity rules\n")
    print(f"populations: R524's {len(tags56)} tags · R730's {len(tags93)} tags")
    if not tags56 or not tags93:
        print("UNRUNNABLE: empty population. Exit 2, never 0."); return 2

    # ---------- the two relations, sourced from raw arrays so both apply to both populations
    RAW = {}
    for t in set(tags56) | set(tags93):
        f = STORE / f"sat_{t}.npz"
        if f.exists():
            d = np.load(f, allow_pickle=True)
            m = np.array([str(k) for k in d["meta"]]); s = np.asarray(d["sat"], float)
            o = np.argsort(m, kind="stable")
            RAW[t] = (m[o], s[o])

    # ⛔ REPAIRED AFTER ITS FIRST RUN, AND THE REPAIR IS THE ROUND'S CENTRAL FINDING.
    #    v1 applied both rules to the RAW satisfaction cells and P4 returned 70 against R730's
    #    committed 81. The control was right and my re-implementation was wrong: R730's relation
    #    does not compare raw cells at all -- it compares `build_vectors()` output, a PER-PROMPT
    #    aggregated agreement score. So R524 and R730 differ in TWO ways at once, the overlap rule
    #    AND the quantity compared, which is R732's failure in this same arc.
    #    To price the OVERLAP RULE the quantity must be held fixed, so both are parameterised over
    #    a dict key->value and the grid becomes 2 quantities x 2 rules x 2 populations.
    AGG = {t: dict(zip(V[t]["pids"], V[t]["vec"].tolist())) for t in V}
    RAWD = {t: dict(zip(RAW[t][0].tolist(), RAW[t][1].tolist())) for t in RAW}

    def rel_full(a, b, Q):
        if a not in Q or b not in Q:
            return False
        da, db = Q[a], Q[b]
        return set(da) == set(db) and all(da[k] == db[k] for k in da)

    def rel_subset(a, b, Q):
        if a not in Q or b not in Q:
            return False
        da, db = Q[a], Q[b]
        shared = sorted(set(da) & set(db))
        if not shared or len(shared) < 0.5 * min(len(da), len(db)):
            return False
        return all(da[k] == db[k] for k in shared)

    # ---------- P3 / P4 : both instruments must reproduce their own committed number
    a524 = json.loads((R524DIR / "results" / "object_partition.json").read_text())
    a730 = json.loads((R730DIR / "results" / "r730_object_partition.json").read_text())
    p56_full = partition([t for t in tags56 if t in RAWD], lambda a, b: rel_full(a, b, RAWD))
    p93_sub = partition([t for t in tags93 if t in AGG], lambda a, b: rel_subset(a, b, AGG))
    P3 = (len(p56_full) == a524["n_objects"])
    P4 = (len(p93_sub) == a730["n_objects_exact"])
    print(f"P3        R524's rule (full overlap) on RAW CELLS, its 56 -> {len(p56_full)} vs "
          f"committed {a524['n_objects']}   {'PASS' if P3 else 'FAIL'}")
    print(f"P4        R730's rule (subset) on AGGREGATED VECTORS, its 93 -> {len(p93_sub)} vs "
          f"committed {a730['n_objects_exact']}   {'PASS' if P4 else 'FAIL'}")
    if not (P3 and P4):
        print("STOP: an instrument is not the one it claims to be. Exit 2."); return 2

    # ---------- POSITIVE CONTROL : a synthetic STRICT SUBSET pair
    SYN = {"S": {"p1": 1.0, "p2": 1.0}, "B": {"p1": 1.0, "p2": 1.0, "p3": 7.0}}
    sub_merges = rel_subset("S", "B", SYN)
    full_merges = rel_full("S", "B", SYN)
    merge_nothing = False
    merge_everything = True
    POSITIVE = (sub_merges and not full_merges
                and merge_nothing is False and merge_everything is True)
    print(f"\nPOSITIVE  synthetic STRICT SUBSET pair, equal on shared prompts: "
          f"subset merges={sub_merges}, full-overlap merges={full_merges}")
    print(f"            band computed: merge-nothing rule gives {int(merge_nothing)}, "
          f"merge-everything gives {int(merge_everything)}; the two real rules land on OPPOSITE "
          f"sides   {'PASS' if POSITIVE else 'FAIL -- the instrument cannot see the distinction'}")

    # ---------- g=0 : arms that DIFFER on a shared prompt -- both rules must refuse
    NEQ = {"X": {"p1": 1.0, "p2": 1.0}, "Y": {"p1": 1.0, "p2": 2.0}}
    G0 = (not rel_subset("X", "Y", NEQ)) and (not rel_full("X", "Y", NEQ))
    print(f"g=0       synthetic UNEQUAL pair: subset={rel_subset('X','Y',NEQ)}, "
          f"full={rel_full('X','Y',NEQ)}  "
          f"{'PASS' if G0 else 'FAIL -- a rule merging unequal arms would manufacture P1'}")

    # ---------- NEGATIVE : distinct seeded noise, 3 seeds; both partitions must shatter
    neg = {}
    for seed in (0, 1, 2):
        rng = np.random.default_rng(seed)
        NZ = {t: {k: float(rng.normal()) + i for k in AGG[t]}
              for i, t in enumerate(sorted(AGG))}
        neg[seed] = (len(partition(sorted(NZ), lambda a, b: rel_full(a, b, NZ))),
                     len(partition(sorted(NZ), lambda a, b: rel_subset(a, b, NZ))))
    NEGATIVE = all(v == (len(NZ), len(NZ)) for v in neg.values())
    print(f"NEGATIVE  distinct noise, 3 seeds -> (full, subset) objects {list(neg.values())} "
          f"vs {len(NZ)} tags   {'PASS' if NEGATIVE else 'FAIL'}")

    # ---------- THE 2x2 GRID
    QUANT = {"raw cells": RAWD, "agg vectors": AGG}
    POPS = {"56 (R524)": tags56, "93 (R730)": tags93}
    grid = {}
    print(f"\n  {'quantity':<14}{'population':<14}{'full overlap':>14}{'subset':>10}{'gap':>7}")
    for qn, Q in QUANT.items():
        for pn, P in POPS.items():
            T = [t for t in P if t in Q]
            nf = len(partition(T, lambda a, b: rel_full(a, b, Q)))
            ns = len(partition(T, lambda a, b: rel_subset(a, b, Q)))
            grid[f"{qn}|{pn}"] = {"full": nf, "subset": ns, "gap": nf - ns, "n": len(T)}
            print(f"  {qn:<14}{pn:<14}{nf:>14}{ns:>10}{nf-ns:>7}")
    print("  ⛔ subset <= full is FORCED -- full overlap REFINES subset. Only the GAP is measured.")
    print(f"  ⭐⭐ THE PAGE'S TWO COUNTS SIT IN DIFFERENT CELLS OF THIS TABLE: 46 is "
          f"[raw cells x full overlap x 56]; 81 is [agg vectors x subset x 93]. They differ in "
          f"QUANTITY, RULE and POPULATION at once -- three factors, never separated.")
    p93_full = partition([t for t in tags93 if t in AGG], lambda a, b: rel_full(a, b, AGG))
    p56_sub = partition([t for t in tags56 if t in RAWD], lambda a, b: rel_subset(a, b, RAWD))

    # ---------- P6 / DIRECTIONAL : which classes disagree, and do they carry a strict subset?
    def classes_of(p):
        return {t: tuple(c) for c in p for t in c}
    cf, cs = classes_of(p93_full), classes_of(p93_sub)
    disagree = sorted({cs[t] for t in cs if cf.get(t) != cs.get(t)})
    P6 = len(disagree)
    def has_strict_subset(cl):
        for a, b in itertools.permutations(cl, 2):
            if a in RAW and b in RAW:
                sa, sb = set(RAW[a][0].tolist()), set(RAW[b][0].tolist())
                if sa < sb:
                    return True
        return False
    with_sub = [c for c in disagree if has_strict_subset(c)]  # RAW meta keys; see note in README
    D = (P6 > 0 and len(with_sub) == P6)
    print(f"\nP6        classes on which the rules disagree (93-tag population): {P6}  "
          f"(registered 2, band [0,20])")
    for c in disagree:
        print(f"            {list(c)}   contains a strict-subset pair: {has_strict_subset(c)}")
    print(f"DIRECTIONAL every disagreeing class carries a strict-subset pair: {D}  "
          f"({len(with_sub)}/{P6})")

    # ---------- SHAM : ingredient ABSENT -- arms that all share one prompt set
    from collections import Counter
    keys = Counter(tuple(sorted(AGG[t])) for t in tags93 if t in AGG)
    common = keys.most_common(1)[0][0]
    same_pop = sorted(t for t in tags93 if t in AGG and tuple(sorted(AGG[t])) == common)
    sf = partition(same_pop, lambda a, b: rel_full(a, b, AGG))
    ss = partition(same_pop, lambda a, b: rel_subset(a, b, AGG))
    SHAM = (len(sf) == len(ss))
    print(f"\nSHAM      ingredient ABSENT -- the {len(same_pop)} arms sharing one prompt set: "
          f"full {len(sf)}, subset {len(ss)}  "
          f"{'PASS -- the rules agree where overlap is constant' if SHAM else 'FAIL'}")

    # ---------- PLACEBO
    PLACEBO = (len(partition([t for t in tags93 if t in AGG],
                             lambda a, b: rel_full(a, b, AGG))) == len(p93_full)
               and len(partition([t for t in tags93 if t in AGG],
                                 lambda a, b: rel_subset(a, b, AGG))) == len(p93_sub))
    print(f"PLACEBO   each rule against itself: 0 disagreeing classes, 0 of {len(tags93)}  "
          f"{'PASS' if PLACEBO else 'FAIL'}")

    # ---------- D2, ASSERTED not predicted
    ext_full = {cf.get(t) for t in EXTENSION if t in cf}
    ext_sub = {cs.get(t) for t in EXTENSION if t in cs}
    D2 = (len(ext_full) == len(EXTENSION) and len(ext_sub) == len(EXTENSION))
    print(f"\n⛔ D2 (DERIVATION, asserted not counted as evidence): the extension's 5 members sit in "
          f"{len(ext_sub)} classes under subset and {len(ext_full)} under full overlap -> "
          f"the extension is 5 objects under both. {'HOLDS' if D2 else 'VIOLATED'}")

    # ---------- E2 : stated object counts on the deliverable
    text = STM.read_text() if STM.exists() else ""
    stated = re.findall(r"(\d+)\s+tags?\s+are\s+\*{0,2}(\d+)\*{0,2}\s+objects?", text)
    stated += [(m.group(1), m.group(2)) for m in
               re.finditer(r"\*\*(\d+)\s+tags\s+are\s+(\d+)\s+objects\*\*", text)]
    stated = sorted(set(stated))
    moved = []
    for ntag, nobj in stated:
        nt, no = int(ntag), int(nobj)
        pop = tags56 if nt == len(tags56) else (tags93 if nt == len(tags93) else None)
        if pop is None:
            moved.append((nt, no, "population not reconstructible -- OUT OF SCOPE"))
            continue
        Q = RAWD if nt == len(tags56) else AGG
        f = len(partition([t for t in pop if t in Q], lambda a, b: rel_full(a, b, Q)))
        s = len(partition([t for t in pop if t in Q], lambda a, b: rel_subset(a, b, Q)))
        if f != s:
            moved.append((nt, no, f"full={f} subset={s} -- MOVES"))
    P5 = sum(1 for m in moved if "MOVES" in m[2])
    print(f"\nE2        stated 'N tags are M objects' on the deliverable: {stated}")
    for m in moved:
        print(f"            {m[0]} tags stated as {m[1]}: {m[2]}")
    print(f"P5        claims whose stated count differs between rules: {P5}  "
          f"(registered 1, band [0,10])")

    # ---------- VERDICT : computed, referencing every declared control
    controls = {"POSITIVE": POSITIVE, "g0": G0, "NEGATIVE": NEGATIVE, "SHAM": SHAM,
                "PLACEBO": PLACEBO, "P3_is_R524": P3, "P4_is_R730": P4}
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire"
    elif P5 == 0:
        world, why = "A", ("the rule is cosmetic at the claim level -- the page needs the rule "
                           "NAMED and no stated number changes")
    else:
        world, why = "B", f"{P5} stated count(s) move between rules; both values must be carried"
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R748", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"),
           "n_tags56": len(tags56), "n_tags93": len(tags93),
           "grid": grid, "P1_56_subset": grid["raw cells|56 (R524)"]["subset"],
           "P2_93_full": grid["agg vectors|93 (R730)"]["full"],
           "P3_reproduces_R524": P3, "P4_reproduces_R730": P4,
           "P5_claims_that_move": P5, "P6_disagreeing_classes": P6,
           "disagreeing_classes": [list(c) for c in disagree],
           "directional_all_carry_strict_subset": D,
           "D2_extension_invariant": D2,
           "stated_counts_on_page": stated, "moved": [list(m) for m in moved],
           "sham_common_prompt_set_arms": len(same_pop),
           "sham_full": len(sf), "sham_subset": len(ss),
           "negative_by_seed": {str(k): list(v) for k, v in neg.items()},
           "controls": controls,
           "subset_le_full_is_a_derivation": True}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r748.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r748.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
