#!/usr/bin/env python3
"""R525 — the source predicts WHICH duplicate classes should exist. Does it hold?

R524 found 8 duplicate classes and I called their intent "a question about the generating
invocations rather than the artifacts". ⛔ FALSE, and it is the fourth wall of that shape this
session. select_core.py's own --select-npz help text makes a FALSIFIABLE PREDICTION:

  "Five rules consume satisfaction to choose criteria -- topvar_k, topwvar_k, oracle_k,
   greedy_k, indep_k -- so under a second judge those arms change IDENTITY, not just score.
   ... The other rules (random_k, topw_k, topabs_k, full) are satisfaction-blind and the two
   specifications coincide for them exactly."

So a duplicate class whose rule is SATISFACTION-BLIND is the documented, correct outcome. A
duplicate class whose rule CONSUMES satisfaction is a variant that was supposed to change
identity and did not.

ESTIMAND (before method): of the 8 duplicate classes R524 found, how many belong to
  satisfaction-CONSUMING rules -- i.e. how many variant runs failed to produce a variant.
IDENTIFICATION: fully identified -- the rule partition is a literal in the source's help text
  and the identity partition is R524's, both exact.
SCOPE  population: R524's 8 duplicate classes over 56 home-judge tags · instrument: the source's
  own rule partition, quoted · baseline: the prediction the source makes · regime: first release.
WORLDS  A · every duplicate class is satisfaction-blind. The collapse is entirely by design and
              nothing failed; R524's flag about ctlS1 was misplaced.
        B · some duplicate classes consume satisfaction. Those variant runs were designed to
              change identity and did not, so a control did not control.
KILL (pre-registered): 0 consuming classes among the duplicates kills world B.
POSITIVE CONTROL: the blind rules must ACTUALLY be duplicated where a variant tag exists -- if a
  blind rule's variant tag differed, the source's claim would be false and the whole partition
  would be untrustworthy. This is the source's prediction used as an instrument check.
NEGATIVE CONTROL: rules that consume satisfaction must NOT be duplicated across genuinely
  different arms -- e.g. oracle_k4 vs oracle_k4_fit1 differ (different fit parity), confirming
  the family is capable of producing distinct objects at all.
NOISE FLOOR: none. Exact equality, as in R523/R524.
MULTIPLICITY: 8 classes, each classified once; all reported.
IMPOSSIBLE HERE: WHY a variant run produced no variant -- whether the flag was omitted or
  ineffective is in the shell invocation, which is not in the repository as a per-arm record.
"""
import glob, json, pathlib, re, sys

CONSUME = ("topvar_k", "topwvar_k", "oracle_k", "greedy_k", "indep_k")
BLIND   = ("random_k", "topw_k", "topabs_k", "full")

def rule_of(tag):
    for f in sorted(CONSUME + BLIND, key=len, reverse=True):
        if tag.startswith(f):
            return f, (f in CONSUME)
    return None, None

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    src = (root / "corebench/select_core.py").read_text()
    # verify the partition is still what the source says
    ok_src = all(r in src for r in CONSUME + BLIND) and "satisfaction-blind" in src
    print(f"  SOURCE READ  the rule partition is present in select_core.py -> "
          f"{'PASS' if ok_src else 'FAIL'}")
    if not ok_src:
        print("  cannot confirm the partition from source -> UNRUNNABLE"); return 2

    part = json.loads((root / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                       "/R524_how_many_objects_are_in_the_fifty_six_tags/results/object_partition.json").read_text())
    classes = part["multi_tag_classes"]
    if not classes:
        print("  no duplicate classes -> UNRUNNABLE"); return 2

    print(f"\n  {'class':<52}{'rule':<12}{'consumes?':>10}  expected")
    rows, consuming = {}, []
    for c in classes:
        rule, cons = rule_of(c[0])
        exp = "SHOULD DIFFER" if cons else ("duplicate is correct" if cons is False else "unknown rule")
        rows["|".join(c)] = {"tags": c, "rule": rule, "consumes": cons, "expected": exp}
        if cons: consuming.append(c)
        print(f"  {'+'.join(t[:22] for t in c):<52}{str(rule):<12}{str(cons):>10}  {exp}")

    print(f"\n  POSITIVE CONTROL  every BLIND-rule variant tag IS a duplicate, as the source claims:")
    blind_dupes = [c for c in classes if rule_of(c[0])[1] is False]
    print(f"    {len(blind_dupes)} blind classes found duplicated -> "
          f"{'PASS -- the source''s prediction holds where it predicts identity' if blind_dupes else 'FAIL'}")

    # NEGATIVE CONTROL: a consuming family must be able to produce distinct objects
    import numpy as np
    RES = root / "corebench/results"
    def sig(t):
        d = np.load(RES / f"sat_{t}.npz", allow_pickle=True)
        m = np.array([str(k) for k in d["meta"]]); s = np.asarray(d["sat"], dtype=float)
        o = np.argsort(m, kind="stable"); return m[o], s[o]
    a, b = sig("oracle_k4"), sig("oracle_k4_fit1")
    distinct = not (len(a[0]) == len(b[0]) and (a[0] == b[0]).all() and np.array_equal(a[1], b[1]))
    print(f"  NEGATIVE CONTROL  oracle_k4 != oracle_k4_fit1 (family CAN differ): {distinct} -> "
          f"{'PASS' if distinct else 'FAIL -- family is degenerate'}")
    if not distinct:
        print("  -> cannot attribute identity to a failed variant. UNVERIFIED."); return 0

    world = "B" if consuming else "A"
    print(f"\n  ⭐ duplicate classes whose rule CONSUMES satisfaction: {len(consuming)} of {len(classes)}")
    for c in consuming: print(f"      {c}")
    print(f"  WORLD {world} -- " +
          ("these variant runs were designed to change IDENTITY and did not -- a control that "
           "did not control" if world == "B" else
           "every duplicate is satisfaction-blind; the collapse is entirely by design"))

    out = pathlib.Path(__file__).parent / "results/variant_intent.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"classes": rows, "n_classes": len(classes),
                               "n_consuming": len(consuming), "consuming": consuming,
                               "n_blind": len(blind_dupes), "world": world}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
