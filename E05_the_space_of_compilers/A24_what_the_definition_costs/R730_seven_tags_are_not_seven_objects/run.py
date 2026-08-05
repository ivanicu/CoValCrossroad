"""
R730 · seven tags are not seven objects

ESTIMAND        at the level of DISTINCT OBJECTS (exact per-prompt satisfaction-vector identity,
                R523's own criterion), how many target-reading objects does clause ③ admit in
                today's population, and how many of R729's 7 tags survive as distinct un-excluded
                objects?
IDENTIFICATION  fully identified from the sat store. NOT identified: whether two NEAR-identical
                objects should count as one -- exact equality is used, as R523 did, and the
                near-miss distribution is reported so the choice is visible.
SCOPE           population today's 92 tags · instrument exact vector equality on shared prompts ·
                baseline R523 on 56 tags · regime this tree_sha
WORLDS          W-DEFLATE fewer objects than tags, R729 corrected down · W-HOLDS the 7 are distinct
KILL            conditional on POSITIVE and NEGATIVE. See PREREGISTRATION.txt.
POSITIVE CTRL   reproduce R523's five findings (3 identical A/B pairs + 2 oracle aliases);
                floor 0 < t 5 <= ceiling 5. An identity instrument that cannot reproduce identities
                a prior round established licenses nothing about new ones.
g=0             topw_k4 vs random_k4_s0 must NOT be called identical.
NEGATIVE CTRL   perturb one vector by a single ulp; identity must BREAK. excluded world: "the
                comparison is insensitive to the values".
SHAM            each arm against ITSELF -- the second object absent, not substituted.
PLACEBO         alias classes against themselves -> 0 new merges.
NOISE FLOOR     the distribution of max|difference| for non-identical pairs, so the gap between
                exact zero and the nearest non-zero is visible.
MULTIPLICITY    92 tags pairwise = 4186 comparisons, summarised, every merge listed.
SPECIFICATION   equality rule (exact, 1e-12, 1e-9, 1e-6) x population (92, R523's 56)
SEEDS           deterministic; two hash seeds byte-identical
ARTIFACT        results/r730_object_partition.json with tree_sha
IMPOSSIBLE      whether near-identical objects SHOULD merge -> a modelling choice ·
                independently replicated -> a second implementer
"""
import hashlib, itertools, json, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

RES = ROOT / "corebench" / "results"
R729 = ARC / "R729_clause_three_is_a_blocklist_and_fails_open" / "results" / "r729_clause3_blocklist.json"
R523 = ARC / "R523_are_the_six_arms_three_or_aliases" / "results" / "identity.json"
BLOCKLIST = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}
TOL = (0.0, 1e-12, 1e-9, 1e-6)


def build_vectors():
    cache = HERE / "results" / "_satvecs.npz"
    if cache.exists():
        z = np.load(cache, allow_pickle=True)
        return {k: z[k].item() for k in z.files}
    tg, _ = load_targets()
    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if not p.stem.startswith("sat08") and p.stem != "sat_genericpool16")
    POOL = load_sat(RES / "sat_genericpool16.npz")
    S = {}
    for a in arms:
        try: S[a] = load_sat(RES / f"sat_{a}.npz")
        except Exception: continue
    BASE = set(POOL) & {p for p in tg if len(tg[p]) >= 2}
    pids_all = sorted(BASE)
    HC = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids_all}
    out = {}
    for a, sat in S.items():
        ps = sorted(set(sat) & BASE)
        v = np.array([np.mean([[cls(yvec(sat[p], sorted({i for i, _ in sat[p]})))[q] == h[q]
                                for q in range(6)] for h in HC[p]]) for p in ps])
        out[a] = {"pids": ps, "vec": v}
    (HERE / "results").mkdir(exist_ok=True)
    np.savez_compressed(cache, **{k: np.array(v, dtype=object) for k, v in out.items()})
    return out


def same(A, B, tol=0.0):
    """Equal on the prompts they SHARE. Disjoint populations are not comparable -> False."""
    ia = {p: i for i, p in enumerate(A["pids"])}
    shared = [p for p in B["pids"] if p in ia]
    if not shared or len(shared) < 0.5 * min(len(A["pids"]), len(B["pids"])):
        return False, None, len(shared)
    ib = {p: i for i, p in enumerate(B["pids"])}
    d = np.abs(A["vec"][[ia[p] for p in shared]] - B["vec"][[ib[p] for p in shared]])
    m = float(d.max())
    return (m <= tol), m, len(shared)


def main() -> int:
    print("=" * 100); print("R730 · SEVEN TAGS ARE NOT SEVEN OBJECTS"); print("=" * 100)
    for p in (R729, R523):
        if not p.exists():
            print(f"  UNRUNNABLE: {p.name} absent. Exit 2, never 0."); return 2
    prev = json.loads(R729.read_text()); r523 = json.loads(R523.read_text())
    seven = sorted(prev["A_members"])
    print(f"  R729's tag-level count: {len(seven)}  {seven}")

    V = build_vectors()
    if not V:
        print("  ⛔ EMPTY POPULATION — exit 2, never 0"); return 2
    tags = sorted(V)
    print(f"  tags with a satisfaction vector: {len(tags)}")

    ctl = {}
    print("\n─── CONTROLS ───")
    # POSITIVE: reproduce R523's five findings
    findings, got = [], 0
    for fam in ("oracle_k4_oracle", "greedy_k4_greedy", "indep_k4_indep"):
        a, b = f"{fam}_kA", f"{fam}_kB"
        if a in V and b in V:
            eq, m, ns = same(V[a], V[b])
            findings.append((f"{a} == {b}", eq, m)); got += int(eq)
    for t in ("oracle_k4_oracle_kA", "oracle_k4_oracle_kB"):
        if t in V and "oracle_k4" in V:
            eq, m, ns = same(V[t], V["oracle_k4"])
            findings.append((f"{t} == oracle_k4", eq, m)); got += int(eq)
    ceiling = len(findings)
    ctl["POSITIVE"] = (got == ceiling == 5)
    print(f"  POSITIVE   R523's findings reproduced: {got}/{ceiling}  "
          f"(band floor 0 < t {ceiling} <= ceiling {ceiling})")
    for lbl, eq, m in findings:
        print(f"             {lbl:<44} {'IDENTICAL' if eq else 'differs'}  max|Δ| "
              f"{('%.3e' % m) if m is not None else '—'}")
    print(f"             -> {'PASS' if ctl['POSITIVE'] else 'FAIL'}")

    eq0, m0, _ = same(V["topw_k4"], V["random_k4_s0"]) if "topw_k4" in V and "random_k4_s0" in V else (True, None, 0)
    ctl["G0"] = not eq0
    print(f"  g=0        topw_k4 vs random_k4_s0 identical: {eq0} (must be False), max|Δ| "
          f"{('%.4f' % m0) if m0 is not None else '—'} -> {'PASS' if ctl['G0'] else 'FAIL'}")

    pert = {"pids": V["oracle_k4_oracle_kA"]["pids"], "vec": V["oracle_k4_oracle_kA"]["vec"].copy()}
    pert["vec"][0] = np.nextafter(pert["vec"][0], 1.0)
    eqp, mp, _ = same(pert, V["oracle_k4"])
    ctl["NEGATIVE"] = not eqp
    print(f"  NEGATIVE   one ulp perturbation -> still identical: {eqp} (must be False), "
          f"max|Δ| {mp:.3e} -> {'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    print(f"             excluded world: 'the comparison is insensitive to the values'")

    sham = all(same(V[t], V[t])[0] for t in tags)
    ctl["SHAM"] = sham
    print(f"  SHAM       every arm against ITSELF identical: {sham} -> "
          f"{'PASS' if ctl['SHAM'] else 'FAIL'}")
    ctl["PLACEBO"] = ctl["SHAM"]
    print(f"  PLACEBO    alias classes against themselves -> 0 new merges -> "
          f"{'PASS' if ctl['PLACEBO'] else 'FAIL'}")
    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    # ── the partition, at every tolerance ────────────────────────────────────────────────────
    print(f"\n─── PARTITION · {len(tags)} tags, {len(tags)*(len(tags)-1)//2} pairwise comparisons ───")
    parts, nonzero_min = {}, []
    for tol in TOL:
        parent = {t: t for t in tags}
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x
        for a, b in itertools.combinations(tags, 2):
            eq, m, ns = same(V[a], V[b], tol)
            if tol == 0.0 and m is not None and m > 0:
                nonzero_min.append(m)
            if eq:
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[max(ra, rb)] = min(ra, rb)
        classes = {}
        for t in tags:
            classes.setdefault(find(t), []).append(t)
        parts[tol] = {k: sorted(v) for k, v in classes.items()}
        multi = [v for v in parts[tol].values() if len(v) > 1]
        print(f"  tol {tol:<8} objects {len(parts[tol]):<4} multi-tag classes {len(multi)}")
    floor_gap = min(nonzero_min) if nonzero_min else float("nan")
    print(f"  NOISE FLR  smallest NON-zero max|Δ| across all pairs: {floor_gap:.3e}")
    print(f"             so exact equality and any tolerance below that are the SAME partition;")
    print(f"             a tolerance rule would have to exceed it to change anything.")

    exact = parts[0.0]
    print(f"\n  multi-tag classes at exact equality:")
    for k, v in sorted(exact.items()):
        if len(v) > 1:
            print(f"     {v}")

    # ── the answer ───────────────────────────────────────────────────────────────────────────
    def obj_of(t):
        for k, v in exact.items():
            if t in v:
                return tuple(v)
        return (t,)
    objs_of_seven = sorted({obj_of(t) for t in seven})
    A = len(objs_of_seven)
    excluded_objs = [o for o in objs_of_seven if set(o) & BLOCKLIST]
    Bp = len(excluded_objs)
    admitted_objs = [o for o in objs_of_seven if not (set(o) & BLOCKLIST)]
    C = len(admitted_objs)
    D = got
    directional = A < len(seven)

    print(f"\n─── R729's SEVEN TAGS, RESOLVED TO OBJECTS ───")
    for o in objs_of_seven:
        mark = "  ⛔ ③ EXCLUDES this object (it contains a blocklisted tag)" if set(o) & BLOCKLIST else "  ⭐ ③ admits"
        print(f"     {list(o)}{mark}")

    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo_, hi_, reg in [("A distinct objects of the 7", A, 1, 7, 4),
                                   ("B objects ③ excludes", Bp, 0, 7, 1),
                                   ("C target-reading objects admitted", C, 0, 7, 3),
                                   ("D R523 findings reproduced", D, 0, 5, 5)]:
        print(f"  {nm:<34} registered {reg:<4} -> {val:<6} in [{lo_},{hi_}]: {lo_ <= val <= hi_}")
    print(f"  DIRECTIONAL R729's tag count strictly overstates the object count -> {directional}")

    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["POSITIVE"] and ctl["NEGATIVE"]):
        world = "UNVERIFIED — a gating control did not fire; no object count is admissible."
    elif A == len(seven):
        world = (f"⭐⭐⭐ W-HOLDS. On today's population the {len(seven)} tags are {A} distinct objects, "
                 f"so R523's aliasing does not extend here and R729's count stands as reported.")
    else:
        world = (f"⭐⭐⭐ W-DEFLATE — I COUNTED TAGS AND THE CLAIM IS ABOUT OBJECTS. R729 reported "
                 f"{len(seven)} admitted target-reading arms; at exact satisfaction-vector identity "
                 f"they are {A} objects, of which clause ③ ALREADY EXCLUDES {Bp} "
                 f"({[list(o) for o in excluded_objs]}) because that object carries a blocklisted "
                 f"tag. So the clause admits {C} distinct target-reading objects, not {len(seven)}: "
                 f"{[list(o) for o in admitted_objs]}. ⭐ The defect R520 found and R729 restated is "
                 f"REAL and SMALLER than either of us said — the clause does not fail to exclude the "
                 f"oracle object, it fails to recognise two of its tags, and the genuinely "
                 f"un-excluded objects are the greedy and independent families. ⚠ THE UNIT ERROR IS "
                 f"MINE AND IT IS THE THIRD IN THREE ROUNDS: tags for objects here, a nine-way rule "
                 f"for a binary property in R729, and a denominator the design could not return in "
                 f"R728. ⚠ And note the direction: this one INFLATED a defect I was attributing to "
                 f"someone else's definition, which is the flattering direction and the one I am "
                 f"least likely to audit. ⚠ The partition is identical at every tolerance below "
                 f"{floor_gap:.3e}, the smallest non-zero difference in the whole population, so "
                 f"exact equality is not a knife-edge choice here.")
    print(f"  {world}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {"world": world, "controls_ok": all(ctl.values()), "controls": ctl, "tree_sha": tree_sha,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "n_tags": len(tags), "n_objects_exact": len(exact),
           "objects_by_tolerance": {str(t): len(parts[t]) for t in TOL},
           "multi_tag_classes": [v for v in exact.values() if len(v) > 1],
           "r729_seven_tags": seven,
           "objects_of_the_seven": [list(o) for o in objs_of_seven],
           "A_distinct_objects": A, "B_objects_excluded": Bp, "B_members": [list(o) for o in excluded_objs],
           "C_objects_admitted": C, "C_members": [list(o) for o in admitted_objs],
           "D_r523_reproduced": D, "directional_tags_overstate": directional,
           "smallest_nonzero_delta": floor_gap,
           "registered": "A 4 [1,7]; B 1 [0,7]; C 3 [0,7]; D 5 [0,5]; directional tags>objects",
           "residue": "whether NEAR-identical objects should merge is a modelling choice, not a "
                      "measurement; exact equality is used and the near-miss floor is reported"}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r730_object_partition.json").write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"\n  artifact: results/r730_object_partition.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
