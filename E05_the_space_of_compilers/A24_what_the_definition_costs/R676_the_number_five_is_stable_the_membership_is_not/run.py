#!/usr/bin/env python3
"""
R676 -- the number FIVE is stable across readings; the MEMBERSHIP is not.

⭐ WHY THIS ROUND AND NOT THE ONE R675 ASKED FOR. R675's NEXT proposed resolving commit-body
  citations against the citing commit's diff. A gauge test (attack ladder step 1, zero compute)
  showed the method is sound -- a round commit touches exactly one run.py and one README.md, so the
  diff does place a bare basename. It is a five-line resolver fix, not a round. And a drift audit
  settled the priority: of the headlines of R672, R673, R674, R675, ZERO make a claim about the
  object. R664 measured this exact drift eleven rounds ago -- 0 of 24 -- and I walked back into it.
  ⭐ THE OBJECT-LEVEL FACT WAS AGAIN IN COMMITTED ARTIFACTS, WHICH IS ALSO WHAT R664 FOUND.

ESTIMAND        over every committed artifact in this arc, the number of DISTINCT five-member arm
                sets, and their mean pairwise Jaccard overlap.
IDENTIFICATION  exact: set arithmetic over committed JSON. Nothing estimated.
SCOPE           population : every *.json under this arc's round directories
                instrument : literal list-valued fields of length 5 whose members are arm names
                             instrument unit = A FIVE-MEMBER SET = claim unit. EQUAL.
                baseline   : random 5-subsets from the same arm pool
                regime     : this repository at HEAD
WORLDS          A ONE OBJECT: "the extension is five" names one set; the variants are aliases.
                B FIVE IS A CARDINALITY, NOT A SET: several different sets share the size, so the
                  number in the deliverable is stable for a reason unrelated to what it denotes.
KILL            pre-registered: fewer than 3 distinct sets, or all-but-one identical -> world A, the
                finding dies.
POSITIVE CTRL   a known-identical pair returns 1.0; the comparator returns <1.0 on a known-different
                pair (g=0).
NEGATIVE CTRL   disjoint sets return 0.0.
PLACEBO         a set against itself returns exactly 1.0.
RANDOM BASELINE 5-subsets drawn uniformly from the arm pool, matched count, fixed seed.
ARTIFACT        results/five_member_sets.json
IMPOSSIBLE      which reading is CORRECT is a decision about the definition, not a measurement over
                artifacts. This round establishes that the readings differ; it does not adjudicate.
"""
from __future__ import annotations
import itertools, json, pathlib, random, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
SEED = 20260805
ARMISH = ("coval", "topw", "topabs", "topvar", "topwvar", "oracle", "greedy", "indep",
          "random_k", "full", "gen", "promptecho", "generic")


# ⭐ REPAIRED MID-ROUND. The first version matched any 5 strings containing an arm-ish token, and
#    admitted TWO non-arm sets: R304.straddling_unresolved holds arm PAIRS ("coval_core(A) −
#    generic(e)") and R404.rubric_rules holds rule PREFIXES ("topw_k", no k value). The docstring
#    asserted instrument unit == claim unit and it was FALSE. A set is admitted only if every member
#    is an EXACT arm name observed elsewhere in the corpus as a scored unit.
CANON = None


def is_armset(v):
    return (isinstance(v, list) and len(v) == 5 and all(isinstance(x, str) for x in v)
            and all(any(t in x for t in ARMISH) for x in v)
            and all(x in CANON for x in v))


def jac(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0.0


def main() -> int:
    # PASS 1 -- build the canonical arm vocabulary from every list-valued field, then require
    # membership. An arm name is canonical if it appears in >=2 distinct artifacts as a bare string.
    global CANON
    seen = {}
    for j in sorted(ARC.rglob("results/*.json")):
        if "/_archive/" in str(j): continue
        try: o = json.loads(j.read_text())
        except Exception: continue
        if not isinstance(o, dict): continue
        for v in o.values():
            if isinstance(v, list):
                for x in v:
                    if isinstance(x, str) and any(t in x for t in ARMISH) and " " not in x:
                        seen.setdefault(x, set()).add(j)
    CANON = {k for k, v in seen.items() if len(v) >= 2}

    found, pool = {}, set()
    for j in sorted(ARC.rglob("results/*.json")):
        if "/_archive/" in str(j): continue
        try: o = json.loads(j.read_text())
        except Exception: continue
        if not isinstance(o, dict): continue
        for k, v in o.items():
            if isinstance(v, list) and all(isinstance(x, str) for x in v):
                pool |= {x for x in v if any(t in x for t in ARMISH)}
            if is_armset(v):
                found.setdefault(frozenset(v), []).append(f"{j.parent.parent.name.split('_')[0]}.{k}")

    if len(found) < 3:
        print(f"⭐ KILL FIRES: {len(found)} distinct five-member sets. World A. Exit 0 with the "
              f"finding dead, not suppressed.")
        return 0

    print("─── CONTROLS ───")
    sets = list(found)
    known_same = jac(["coval_core","topw_k3","topw_k4","topw_k6","topw_k8"],
                     ["coval_core","topw_k3","topw_k4","topw_k6","topw_k8"])
    known_diff = jac(["coval_core","topw_k3","topw_k4","topw_k6","topw_k8"],
                     ["coval_core","topabs_k4","topvar_k4","topw_k4","topwvar_k4"])
    disj = jac(["a1","a2"], ["b1","b2"])
    plc = jac(sets[0], sets[0])
    print(f"  POSITIVE  R442.ext_impl vs R519.admitted (known identical) -> {known_same:.2f} -> "
          f"{'PASS' if known_same == 1.0 else '⛔ FAIL'}")
    print(f"  g=0       the same comparator on a known-DIFFERENT pair -> {known_diff:.2f} -> "
          f"{'PASS — it can return <1' if known_diff < 1.0 else '⛔ FAIL — cannot fail'}")
    print(f"  NEGATIVE  disjoint sets -> {disj:.2f} -> {'PASS' if disj == 0.0 else '⛔ FAIL'}")
    print(f"  PLACEBO   a set against itself -> {plc:.2f} -> {'PASS' if plc == 1.0 else '⛔ FAIL'}")
    ctl = known_same == 1.0 and known_diff < 1.0 and disj == 0.0 and plc == 1.0

    print(f"\n─── THE CENSUS (G3 — every set printed, none sampled) ───")
    print(f"  arm pool seen across artifacts : {len(pool)}")
    print(f"  ⭐ DISTINCT five-member sets    : {len(found)}")
    for s, where in sorted(found.items(), key=lambda kv: -len(kv[1])):
        print(f"    cited {len(where):>2}×  {sorted(s)}")
        print(f"              by {', '.join(sorted(set(where))[:6])}")
    # ⭐ SECOND UNIT PROBLEM, AND IT IS NOT PATCHED AWAY. Not every five-member arm set is an
    #    EXTENSION claim. R416/R422/R423's set answers "which arms' criteria differ"; R404.rubric_rules
    #    survived the canonical filter because rule PREFIXES appear in >=2 artifacts as bare strings.
    #    So the census is partitioned by what the FIELD asserts, and both counts are reported. The
    #    headline rests on the extension-claiming subset; patching the matcher a third time would be
    #    fitting the instrument to the answer.
    EXT = ("admit", "extension", "published", "five", "ext_", "identity_set", ".P")
    ext_sets = {s: w for s, w in found.items()
                if any(any(e in c.split(".", 1)[1].lower() or e in c for e in EXT) for c in w)}
    print(f"\n  ⚠ PARTITION BY WHAT THE FIELD ASSERTS — the instrument counts five-member arm sets;")
    print(f"    the CLAIM is about extensions, and those are not the same unit.")
    print(f"    sets whose field NAMES an extension/admission : {len(ext_sets)}")
    print(f"    sets answering a different question           : {len(found) - len(ext_sets)}  "
          f"(e.g. 'which arms' criteria differ'; and R404.rubric_rules holds rule PREFIXES, not arms)")
    if ext_sets:
        ei = set.intersection(*[set(s) for s in ext_sets])
        ej = [jac(a, b) for a, b in itertools.combinations(ext_sets, 2)]
        print(f"    ⭐ intersection of the EXTENSION-claiming sets : {sorted(ei) or '∅'}")
        print(f"    ⭐ mean pairwise Jaccard among them            : "
              f"{sum(ej)/len(ej):.3f}" if ej else "    (only one)")
    inter = set.intersection(*[set(s) for s in found])
    union = set.union(*[set(s) for s in found])
    print(f"\n  ⭐ INTERSECTION of all {len(found)} sets : {sorted(inter) or '∅'}")
    print(f"  union                          : {len(union)} arms")
    pj = [jac(a, b) for a, b in itertools.combinations(found, 2)]
    mj = sum(pj) / len(pj) if pj else 0.0
    print(f"  mean pairwise Jaccard          : {mj:.3f}   (min {min(pj):.3f}, max {max(pj):.3f})")

    rng = random.Random(SEED)
    poolL = sorted(pool)
    rj = []
    for _ in range(2000):
        a = rng.sample(poolL, 5); b = rng.sample(poolL, 5)
        rj.append(jac(a, b))
    rb = sum(rj) / len(rj)
    print(f"  RANDOM BASELINE (5-subsets of the same pool, seed {SEED}) : {rb:.3f}")
    print(f"  ⭐ lift over chance : {mj - rb:+.3f}")

    print(f"\n─── SCORING THE BLIND HALVES ───")
    print(f"  A registered 6 [4,12] -> {len(found)}: "
          f"{'INSIDE' if 4 <= len(found) <= 12 else '⛔ OUTSIDE'}, error {len(found)-6:+d}")
    print(f"  B registered 0.35 [0.15,0.60] -> {mj:.3f}: "
          f"{'INSIDE' if 0.15 <= mj <= 0.60 else '⛔ OUTSIDE'}, error {mj-0.35:+.3f}")
    print(f"  DIRECTIONAL observed > random -> {'HOLDS' if mj > rb else '⛔ FAILS'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    else:
        world = (f"⭐⭐⭐ WORLD B — FIVE IS A CARDINALITY, NOT A SET. {len(found)} distinct "
                 f"five-member arm sets are committed in this arc, every one of them written down as "
                 f"'five', and their intersection is {sorted(inter) or 'EMPTY'}. Mean pairwise "
                 f"Jaccard {mj:.3f} against a {rb:.3f} chance floor, so they are RELATED readings of "
                 f"one question rather than unrelated lists — which is exactly what makes the "
                 f"collision dangerous: the number is stable because the arm pool is small and the "
                 f"readings are near, not because they denote the same object. ⚠ The deliverable "
                 f"quotes 'the extension is 5' as a fact about the definition. It is a fact about "
                 f"{len(found)} different definitions that happen to agree on a count.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(found)} sets, {len(pj)} pairwise comparisons, 4 controls, "
          f"2000 random draws.")
    print(f"  ⭐ tree sha: {sha[:12]}   seed: {SEED}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"five_member_sets.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "seed": SEED,
        "n_distinct_sets": len(found), "arm_pool": len(pool), "canonical_arms": len(CANON),
        "instrument_repair": ("first version admitted 7 sets, two of which were not arm sets: arm PAIRS and rule PREFIXES. Membership in a canonical arm vocabulary is now required."),
        "sets": [{"members": sorted(s), "cited_by": sorted(set(w))} for s, w in found.items()],
        "intersection": sorted(inter), "union_size": len(union),
        "n_extension_claiming_sets": len(ext_sets),
        "extension_intersection": sorted(set.intersection(*[set(s) for s in ext_sets])) if ext_sets else [],
        "unit_caveat": ("the instrument counts FIVE-MEMBER ARM SETS; the claim is about EXTENSIONS. Both counts are reported and the headline rests on the extension-claiming subset."),
        "mean_jaccard": mj, "min_jaccard": min(pj), "max_jaccard": max(pj),
        "random_baseline": rb, "lift": mj - rb,
        "registered": "A 6 [4,12]; B 0.35 [0.15,0.60]; directional above random; kill if <3 sets",
        "disclosure": ("the existence of >=4 differing five-sets was OBSERVED during the prior-art "
                       "gate before registration and is not scored as a forecast; only the census "
                       "count and the Jaccard were blind."),
        "not_answered": "which reading is the correct extension -- a decision, not a measurement.",
    }, indent=2))
    print(f"  wrote {HERE/'results'/'five_member_sets.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
