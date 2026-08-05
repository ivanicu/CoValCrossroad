#!/usr/bin/env python3
"""R524 — how many distinct OBJECTS are in the 56 home-judge tags?

R523 found six tags naming three objects, one of which was already declared. That was a spot
check on six. This partitions the whole population, because every count this campaign has taken
from R436 -- "0 of 56 at J", "22 of 93 excluded", "41 arms joined" -- is a count of TAGS unless
the partition says otherwise.

ESTIMAND (before method): the number of equivalence classes of the 56 home-judge tags under
  exact equality of the saturation matrix, and which prior counts move as a result.
IDENTIFICATION: fully identified -- the .npz files ARE the objects; no estimation.
SCOPE  population: the 56 tags R436 scores at the home judge · instrument: exact array equality
  after a stable sort on the meta keys · baseline: n/a · regime: first release.
WORLDS  A · 56 tags = 56 objects. Every R436-derived count is already a count of objects.
        B · the tags collapse. Each collapsed pair silently doubled a denominator somewhere.
KILL (pre-registered): exact equality decides, no tolerance. A tolerance is what let a
  four-decimal agreement pass as identity in R522.
POSITIVE CONTROL: the partition MUST recover the four identities R523 established by hand --
  three A/B pairs plus oracle_k4_oracle_kA == oracle_k4. If it misses any, it is not sensitive
  enough for the ones it claims to have found.
NEGATIVE CONTROL: coval_core vs generic must land in different classes, and a shuffled copy of
  an arm must not match its original -- the comparison must be order-sensitive, not a multiset.
NOISE FLOOR: none, by construction. Exact equality has no noise floor, which is why it is the
  right instrument for an identity question.
MULTIPLICITY: C(56,2) = 1540 pairwise comparisons; the classes are reported whole.
IMPOSSIBLE HERE: the second release's 37 tags, whose npz files are a different schema family;
  and WHY two tags name one object, which lives in the generating invocation. Both named.
"""
import glob, json, pathlib, sys, collections
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
RES = ROOT / "corebench/results"

def sig(tag):
    d = np.load(RES / f"sat_{tag}.npz", allow_pickle=True)
    m = np.array([str(k) for k in d["meta"]]); s = np.asarray(d["sat"], dtype=float)
    o = np.argsort(m, kind="stable"); return m[o], s[o]

def same(a, b):
    ma, sa = a; mb, sb = b
    return len(ma) == len(mb) and bool((ma == mb).all()) and np.array_equal(sa, sb)

def main():
    r436 = json.loads(pathlib.Path(glob.glob(str(ROOT/"E05_the_space_of_compilers/*/R436*/results/*.json"))[0]).read_text())
    tags = sorted({c["arm"] for c in r436["cells"] if not c["arm"].endswith(("_08b", "_08bR"))})
    S, unread = {}, []
    for t in tags:
        try: S[t] = sig(t)
        except Exception: unread.append(t)
    if not S:
        print("  empty population -> UNRUNNABLE"); return 2
    print(f"  tags at the home judge: {len(tags)} · readable: {len(S)}"
          + (f" · unreadable: {unread}" if unread else ""))

    # NEGATIVE CONTROL
    neg1 = not same(S["coval_core"], S["generic"])
    m, s = S["coval_core"]; perm = np.random.default_rng(11).permutation(len(s))
    neg2 = not same((m, s), (m, s[perm]))
    print(f"  NEGATIVE CONTROL  coval_core != generic: {neg1} · order-sensitive: {neg2} -> "
          f"{'PASS' if neg1 and neg2 else 'FAIL'}")
    if not (neg1 and neg2): return 0

    # partition by cheap bucket then exact compare
    buckets = collections.defaultdict(list)
    for t, (m_, s_) in S.items():
        buckets[(len(m_), round(float(s_.sum()), 12), round(float(s_.std()), 12))].append(t)
    classes = []
    for _, group in buckets.items():
        left = list(group)
        while left:
            head = left.pop(0); cls = [head]
            rest = []
            for o in left:
                (cls.append(o) if same(S[head], S[o]) else rest.append(o))
            left = rest; classes.append(sorted(cls))
    classes.sort(key=lambda c: (-len(c), c[0]))
    multi = [c for c in classes if len(c) > 1]

    # POSITIVE CONTROL: must recover R523's four identities
    def together(a, b):
        return any(a in c and b in c for c in classes)
    known = [("oracle_k4_oracle_kA", "oracle_k4_oracle_kB"),
             ("greedy_k4_greedy_kA", "greedy_k4_greedy_kB"),
             ("indep_k4_indep_kA", "indep_k4_indep_kB"),
             ("oracle_k4_oracle_kA", "oracle_k4")]
    rec = sum(together(a, b) for a, b in known if a in S and b in S)
    print(f"  POSITIVE CONTROL  recovers {rec}/{len(known)} of R523's hand-found identities -> "
          f"{'PASS' if rec == len(known) else 'FAIL'}")
    if rec != len(known):
        print("  -> partition not sensitive enough. UNVERIFIED."); return 0

    world = "B" if multi else "A"
    print(f"\n  ⭐ {len(S)} tags -> {len(classes)} DISTINCT OBJECTS "
          f"({len(S) - len(classes)} tags are duplicates)")
    print(f"  classes with more than one tag: {len(multi)}")
    for c in multi: print(f"    {len(c)}x  {c}")
    print(f"\n  WORLD {world} -- " +
          ("the tag population collapses; R436-derived counts are counts of TAGS"
           if world == "B" else "56 tags are 56 objects; nothing moves"))
    print(f"  bound this puts on prior counts: any denominator taken from this population is "
          f"overstated by up to {len(S) - len(classes)}")

    out = pathlib.Path(__file__).parent / "results/object_partition.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"n_tags": len(S), "n_objects": len(classes),
                               "n_duplicate_tags": len(S) - len(classes),
                               "multi_tag_classes": multi, "world": world,
                               "unreadable": unread}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
