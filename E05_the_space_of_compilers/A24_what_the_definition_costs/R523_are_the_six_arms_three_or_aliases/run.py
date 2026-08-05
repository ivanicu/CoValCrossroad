#!/usr/bin/env python3
"""R523 — are the six missing arms distinct objects, duplicate pairs, or aliases of declared arms?

R522 closed noting oracle_k4_oracle_kA reproduces oracle_k4's stored contrast to four decimals,
and proposed that the A/B variants may be one object under two tags. ⚠ That closing line runs
TWO different hypotheses together, and they have opposite consequences:

  H_pair   A == B within each family. The six are really three; the deliverable's count is wrong
           but R520-R522's substance survives.
  H_alias  oracle_k4_oracle_kA == oracle_k4 (a DECLARED arm). Then the literal was never missing
           a distinct arm, only an alias of one it already names, and R520-R522 deflate sharply.

ESTIMAND (before method): for each of the six, the exact per-prompt satisfaction vector, compared
  to (i) its A/B sibling and (ii) every arm already in R294's census. Identity is exact equality
  of the saturation matrix, not closeness of a summary statistic.
IDENTIFICATION: fully identified -- the .npz files ARE the objects. No estimation involved.
SCOPE  population: 968 prompts x the criteria of each arm · instrument: exact array comparison ·
  baseline: n/a, this is an identity test · regime: first release.
WORLDS  A · all six are distinct objects. Count of six stands.
        B · A==B pairwise. Six is three.
        C · at least one equals a DECLARED arm. The literal missed an alias, and the price
              measured in R521/R522 is overstated by that many.
KILL (pre-registered): exact matrix equality decides. No threshold, no tolerance -- a tolerance
  is what let "matches to four decimals" masquerade as identity in the first place.
POSITIVE CONTROL: two arms KNOWN to differ (coval_core vs generic) must compare unequal, and an
  arm compared to ITSELF must compare equal. An identity test that cannot distinguish is void.
NEGATIVE CONTROL: comparing an arm to a shuffled copy of itself must be unequal -- the comparison
  must be sensitive to ordering, not just to the multiset of values.
NOISE FLOOR: none. Exact equality has no noise floor, which is why it is the right instrument
  here and a summary statistic was the wrong one.
MULTIPLICITY: 6 arms x (1 sibling + 41 census arms) comparisons; all reported.
IMPOSSIBLE HERE: WHY two tags name one object -- that is in the generating invocation, which the
  .npz does not carry. Named, not marked planned.
"""
import glob, json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
RES = ROOT / "corebench/results"
SIX = ["oracle_k4_oracle_kA", "oracle_k4_oracle_kB", "greedy_k4_greedy_kA",
       "greedy_k4_greedy_kB", "indep_k4_indep_kA", "indep_k4_indep_kB"]

def sig(tag):
    """exact content signature: the sorted (meta, sat) pairs of the npz."""
    d = np.load(RES / f"sat_{tag}.npz", allow_pickle=True)
    meta = np.array([str(k) for k in d["meta"]])
    sat = np.asarray(d["sat"], dtype=float)
    o = np.argsort(meta, kind="stable")
    return meta[o], sat[o]

def same(a, b):
    ma, sa = a; mb, sb = b
    return len(ma) == len(mb) and bool((ma == mb).all()) and bool(np.array_equal(sa, sb))

def main():
    cen = json.loads((ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                      "/R294_the_definition_against_everything/results/full_census.json").read_text())["rows"]
    S = {t: sig(t) for t in SIX}

    # POSITIVE CONTROL
    cc, gn = sig("coval_core"), sig("generic")
    p1 = same(cc, cc); p2 = not same(cc, gn)
    print(f"  POSITIVE CONTROL  arm vs itself equal: {p1} · coval_core vs generic unequal: {p2} -> "
          f"{'PASS' if p1 and p2 else 'FAIL'}")
    # NEGATIVE CONTROL: order sensitivity
    m, s = cc
    perm = np.random.default_rng(7).permutation(len(s))
    ord_ok = not same((m, s), (m, s[perm]))
    print(f"  NEGATIVE CONTROL  shuffled copy compares unequal: {ord_ok} -> "
          f"{'PASS' if ord_ok else 'FAIL -- comparison is order-blind'}")
    if not (p1 and p2 and ord_ok):
        print("  -> identity test void. UNVERIFIED."); return 0

    print(f"\n  H_pair -- does A equal B within each family?")
    pairs = [("oracle_k4_oracle_kA", "oracle_k4_oracle_kB"),
             ("greedy_k4_greedy_kA", "greedy_k4_greedy_kB"),
             ("indep_k4_indep_kA", "indep_k4_indep_kB")]
    npair = 0
    for a, b in pairs:
        eq = same(S[a], S[b]); npair += eq
        print(f"    {a:<24} == {b:<24} {eq}")

    print(f"\n  H_alias -- does any of the six equal an arm ALREADY in R294's census?")
    aliases = {}
    census_sigs = {}
    for t in sorted(cen):
        try: census_sigs[t] = sig(t)
        except Exception: pass
    print(f"    comparing against {len(census_sigs)} census arms with a readable npz")
    for t in SIX:
        hits = [c for c, cs in census_sigs.items() if same(S[t], cs)]
        aliases[t] = hits
        print(f"    {t:<24} -> {hits if hits else 'no census arm matches'}")

    n_alias = sum(1 for v in aliases.values() if v)
    world = "C" if n_alias else ("B" if npair == len(pairs) else "A")
    print(f"\n  pairs identical: {npair}/{len(pairs)} · arms aliasing a declared arm: {n_alias}/6")
    print(f"  WORLD {world} -- " + {
        "A": "all six are distinct objects; the count of six stands",
        "B": "A==B pairwise: the six are three distinct objects",
        "C": "at least one of the six IS an arm the census already carries -- the literal missed "
             "an alias, and the price is overstated"}[world])

    out = pathlib.Path(__file__).parent / "results/identity.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"pairs_identical": npair, "n_pairs": len(pairs),
                               "aliases": aliases, "n_alias": n_alias, "world": world,
                               "n_census_compared": len(census_sigs)}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
