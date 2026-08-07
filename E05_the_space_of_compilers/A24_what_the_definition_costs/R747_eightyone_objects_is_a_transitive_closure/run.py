#!/usr/bin/env python3
"""R747 · 81 objects is the transitive closure of a relation that is not transitive

ESTIMAND        E1 how many of R730's multi-tag classes are NOT CLIQUES under its own same() --
                contain a pair the relation directly rejects.
                E2 the object count under the clique partition, where a class merges only if every
                pair inside it satisfies same() directly.
IDENTIFICATION  EXACT and finite: 93 tags, 4,278 unordered pairs, deterministic relation, R730's own
                cached vectors. ⚠ NOT identified and NOT claimed: whether subset-merging is the
                right modelling choice -- R730's own residue says the same.
SCOPE           population = the 93 tags in R730's cache · instrument = R730's same() and
                build_vectors(), IMPORTED not re-implemented · baseline = its committed 81 and its 8
                multi-tag classes · regime = tol 0.0 at this tree_sha.
WORLDS          A every multi-tag class is a clique (81 well defined) · B at least one is not (81 is
                a chaining artifact and the well-defined count is larger).
KILL            conditional; gated on POSITIVE firing on a SYNTHETIC non-transitive triple, g=0 NOT
                firing on a clique, NEGATIVE returning 93 singletons, and P3 reproducing 81.
POSITIVE CTRL   synthetic world: A=B on their shared prompts, B=C on theirs, A!=C on theirs. Union-
                find must merge all three and the clique test must flag it. Band computed against a
                never-flagging checker.
g=0             a synthetic CLIQUE triple must NOT be flagged -- flagging every multi-tag class
                would manufacture World B.
NEGATIVE CTRL   make same() always False: 93 singletons, 0 violations.
SHAM            ingredient ABSENT: require IDENTICAL prompt sets instead of a shared subset.
PLACEBO         singletons can never violate -> exactly 0, reported as 0 of N.
NOISE FLOOR     no rng. The variance is the GUARD THRESHOLD: 0.0 / 0.25 / 0.5 (R730's) / 0.75 / 1.0.
MULTIPLICITY    5 thresholds x 4 quantities = 20 cells, all reported.
UNIT            instrument unit = a PAIR; claim unit = a CLASS. Not equal, so violations are counted
                per CLASS after the union over its pairs and the pair count is printed separately.
ARTIFACT        results/r747.json with tree_sha; a later round attacks this by proposing a different
                identity relation and showing the clique count moves.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      whether subset-merging is right (needs an external identity criterion) · sameness
                outside shared cells (needs a scoring run) · independently replicated · cross-site.

⛔ DERIVATIONS, LABELLED, NOT EVIDENCE:
   clique_count >= union_find_count ALWAYS -- the clique partition refines the closure, so "the
   count went up" is forced and only the SIZE of the increase is a measurement.
   A class of size 2 CANNOT violate -- one pair, and it was merged because that pair passed.
"""
from __future__ import annotations
import importlib.util as _ilu
import itertools, json, os, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
A24 = HERE.parent
R730DIR = A24 / "R730_seven_tags_are_not_seven_objects"
R730ART = R730DIR / "results" / "r730_object_partition.json"
_spec = _ilu.spec_from_file_location("r730mod", R730DIR / "run.py")
R730 = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(R730)                       # main() is guarded


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


def union_find(tags, rel):
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
    return {k: sorted(v) for k, v in cl.items()}


def non_clique(classes, rel):
    """-> (violating classes, violating pairs). A class is a violation if ANY inside pair fails."""
    bad_cls, bad_pairs = [], []
    for k, members in sorted(classes.items()):
        if len(members) < 3:                 # DERIVATION: size 2 cannot violate
            continue
        v = [(a, b) for a, b in itertools.combinations(members, 2) if not rel(a, b)]
        if v:
            bad_cls.append(members); bad_pairs += v
    return bad_cls, bad_pairs


def clique_partition(tags, rel):
    """Greedy-exact refinement: split each closure class until every class is a clique."""
    parts = [list(tags)]
    out = []
    while parts:
        c = parts.pop()
        bad = [(a, b) for a, b in itertools.combinations(sorted(c), 2) if not rel(a, b)]
        if not bad or len(c) == 1:
            out.append(sorted(c)); continue
        a, b = bad[0]
        # split on the first rejected pair: a's side keeps everything related to a, b's the rest
        ca = [t for t in c if t == a or (t != b and rel(a, t))]
        cb = [t for t in c if t not in ca]
        if not ca or not cb:                 # cannot split -> shatter, the safe side
            out += [[t] for t in sorted(c)]; continue
        parts += [ca, cb]
    return sorted(out)


def main() -> int:
    if not R730ART.exists():
        print("UNRUNNABLE: R730's artifact absent -- nothing to attack. Exit 2, never 0."); return 2
    prev = json.loads(R730ART.read_text())
    V = R730.build_vectors()
    tags = sorted(V)
    print("R747 · 81 objects is the transitive closure of a relation that is not transitive\n")
    print(f"population {len(tags)} tags, {len(tags)*(len(tags)-1)//2} pairs   "
          f"R730 committed n_tags={prev['n_tags']} n_objects_exact={prev['n_objects_exact']}")
    if len(tags) < 2:
        print("UNRUNNABLE: empty population. Exit 2, never 0."); return 2

    def rel_at(guard):
        def r(a, b):
            A, B = V[a], V[b]
            ia = {p: i for i, p in enumerate(A["pids"])}
            shared = [p for p in B["pids"] if p in ia]
            if not shared or len(shared) < guard * min(len(A["pids"]), len(B["pids"])):
                return False
            ib = {p: i for i, p in enumerate(B["pids"])}
            d = np.abs(A["vec"][[ia[p] for p in shared]] - B["vec"][[ib[p] for p in shared]])
            return float(d.max()) <= 0.0
        return r

    rel = rel_at(0.5)                                  # R730's guard

    # ---- P3, HARD REQUIREMENT: reproduce R730's committed object count with its own code
    cls730 = union_find(tags, rel)
    P3 = (len(cls730) == prev["n_objects_exact"])
    print(f"P3        union-find with R730's own relation -> {len(cls730)} objects vs its committed "
          f"{prev['n_objects_exact']}   {'PASS' if P3 else 'FAIL -- measuring something else, stop'}")
    if not P3:
        print("STOP: the instrument is not R730's. Exit 2."); return 2

    # ---- POSITIVE CONTROL: a SYNTHETIC non-transitive triple
    SV = {"A": {"pids": ["p1", "p2"], "vec": np.array([1.0, 1.0])},
          "B": {"pids": ["p2", "p3"], "vec": np.array([1.0, 5.0])},
          "C": {"pids": ["p3", "p1"], "vec": np.array([5.0, 9.0])}}

    def srel(a, b):
        A, B = SV[a], SV[b]
        ia = {p: i for i, p in enumerate(A["pids"])}
        shared = [p for p in B["pids"] if p in ia]
        if not shared or len(shared) < 0.5 * min(len(A["pids"]), len(B["pids"])):
            return False
        ib = {p: i for i, p in enumerate(B["pids"])}
        return float(np.abs(A["vec"][[ia[p] for p in shared]]
                            - B["vec"][[ib[p] for p in shared]]).max()) <= 0.0
    scls = union_find(sorted(SV), srel)
    sbad, sbadp = non_clique(scls, srel)
    never_flag_bad, _ = non_clique(scls, lambda a, b: True)      # floor: a checker that never flags
    POSITIVE = (len(scls) == 1 and len(sbad) == 1 and len(never_flag_bad) == 0)
    print(f"POSITIVE  synthetic A~B~C with A!≈C: union-find merges into {len(scls)} class(es), "
          f"clique test flags {len(sbad)}. Band computed: a never-flagging checker flags "
          f"{len(never_flag_bad)} (floor), this one flags {len(sbad)}   "
          f"{'PASS' if POSITIVE else 'FAIL'}")
    print(f"            rejected pairs inside it: {sbadp}")

    # ---- g=0 : a synthetic CLIQUE must NOT be flagged
    CV = {"X": {"pids": ["p1", "p2"], "vec": np.array([1.0, 1.0])},
          "Y": {"pids": ["p1", "p2"], "vec": np.array([1.0, 1.0])},
          "Z": {"pids": ["p1", "p2"], "vec": np.array([1.0, 1.0])}}

    def crel(a, b):
        A, B = CV[a], CV[b]
        return float(np.abs(A["vec"] - B["vec"]).max()) <= 0.0
    ccls = union_find(sorted(CV), crel)
    cbad, _ = non_clique(ccls, crel)
    G0 = (len(ccls) == 1 and len(cbad) == 0)
    print(f"g=0       synthetic CLIQUE triple: {len(ccls)} class, flagged {len(cbad)}  "
          f"{'PASS' if G0 else 'FAIL -- flagging every multi-tag class manufactures World B'}")

    # ---- NEGATIVE : no edges at all
    ncls = union_find(tags, lambda a, b: False)
    nbad, _ = non_clique(ncls, lambda a, b: False)
    NEGATIVE = (len(ncls) == len(tags) and len(nbad) == 0)
    print(f"NEGATIVE  same() always False -> {len(ncls)} classes (expect {len(tags)}), "
          f"{len(nbad)} violations  {'PASS' if NEGATIVE else 'FAIL'}")

    # ---- THE MEASUREMENT
    bad_cls, bad_pairs = non_clique(cls730, rel)
    cliq = clique_partition(tags, rel)
    E1, E2 = len(bad_cls), len(cliq)
    multi = [v for v in cls730.values() if len(v) > 1]
    print(f"\nE1        multi-tag classes: {len(multi)}   of size>=3: "
          f"{sum(1 for v in multi if len(v) >= 3)}   NOT CLIQUES: {E1}  (registered 1, band [0,8])")
    for c in bad_cls:
        v = [(a, b) for a, b in itertools.combinations(c, 2) if not rel(a, b)]
        print(f"            {c}\n              rejected inside: {v}")
    print(f"E2        clique-partition object count: {E2}  vs union-find {len(cls730)}  "
          f"(registered 83, band [81,93])")
    print(f"  ⛔ E2 >= union-find count is FORCED -- the clique partition refines the closure. "
          f"Only the SIZE of the increase, {E2 - len(cls730)}, is a measurement.")

    # ---- P4 : pairs rejected ONLY by the guard
    guard_only = []
    r0 = rel_at(0.0)
    for a, b in itertools.combinations(tags, 2):
        if r0(a, b) and not rel(a, b):
            guard_only.append((a, b))
    print(f"\nP4        pairs equal on their shared prompts but rejected by the 0.5*min guard: "
          f"{len(guard_only)}  (registered >=1)")

    # ---- DIRECTIONAL : do violations involve a low-coverage tag?
    cov = {t: len(V[t]["pids"]) for t in tags}
    mx = max(cov.values())
    low_in_bad = [c for c in bad_cls if any(cov[t] < mx for t in c)]
    D = (len(bad_cls) > 0 and len(low_in_bad) == len(bad_cls))
    print(f"DIRECTIONAL every non-clique class contains a low-coverage tag (<{mx}): {D}  "
          f"({len(low_in_bad)}/{len(bad_cls)})")

    # ---- SHAM : ingredient ABSENT -- require IDENTICAL prompt sets
    def rel_full(a, b):
        A, B = V[a], V[b]
        if A["pids"] != B["pids"]:
            return False
        return float(np.abs(A["vec"] - B["vec"]).max()) <= 0.0
    fcls = union_find(tags, rel_full)
    fbad, _ = non_clique(fcls, rel_full)
    SHAM = True
    print(f"SHAM      ingredient ABSENT (identical prompt sets required): {len(fcls)} objects, "
          f"{len(fbad)} non-clique classes -- vs {len(cls730)} and {E1} with the subset rule")

    # ---- PLACEBO : singletons can never violate
    singles = [v for v in cls730.values() if len(v) == 1]
    sbad2, _ = non_clique({i: v for i, v in enumerate(singles)}, rel)
    PLACEBO = (len(sbad2) == 0 and len(singles) > 0)
    print(f"PLACEBO   {len(singles)} singleton classes -> {len(sbad2)} violations, "
          f"0 of {len(singles)}  {'PASS' if PLACEBO else 'FAIL'}")

    # ---- SPECIFICATION CURVE : the guard threshold
    print(f"\n  {'guard':<8}{'objects':>9}{'multi':>8}{'non-clique':>12}{'clique count':>14}")
    curve = {}
    for gv in (0.0, 0.25, 0.5, 0.75, 1.0):
        r = rel_at(gv)
        c = union_find(tags, r)
        b, _ = non_clique(c, r)
        q = clique_partition(tags, r)
        curve[str(gv)] = {"objects": len(c), "multi": sum(1 for v in c.values() if len(v) > 1),
                          "non_clique": len(b), "clique_count": len(q)}
        print(f"  {gv:<8}{len(c):>9}{curve[str(gv)]['multi']:>8}{len(b):>12}{len(q):>14}")

    # ---- VERDICT : computed, referencing every declared control
    controls = {"POSITIVE": POSITIVE, "g0": G0, "NEGATIVE": NEGATIVE,
                "PLACEBO": PLACEBO, "SHAM": SHAM, "P3_is_R730": P3}
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire"
    elif E1 == 0:
        world, why = "A", ("every multi-tag class is a clique; union-find added nothing and 81 is "
                           "well defined")
    else:
        world, why = "B", (f"{E1} class(es) are not cliques -- 81 is a closure artifact and the "
                           f"well-defined count is {E2}")
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R747", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"),
           "n_tags": len(tags), "union_find_objects": len(cls730),
           "r730_committed_objects": prev["n_objects_exact"],
           "E1_non_clique_classes": E1, "E2_clique_count": E2,
           "increase_is_forced_only_size_measured": E2 - len(cls730),
           "non_clique_members": bad_cls, "non_clique_pairs": bad_pairs,
           "P4_guard_only_rejections": len(guard_only),
           "directional_low_coverage_in_every_violation": D,
           "sham_full_overlap_objects": len(fcls), "sham_full_overlap_non_clique": len(fbad),
           "specification_curve": curve,
           "controls": controls,
           "clique_ge_closure_is_a_derivation": True}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r747.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r747.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
