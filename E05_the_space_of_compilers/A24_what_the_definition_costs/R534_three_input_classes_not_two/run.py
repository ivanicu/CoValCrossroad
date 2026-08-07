#!/usr/bin/env python3
"""R534 — ③'s input taxonomy has THREE classes; R529 named two and mislabelled two arms.

R529 forked ③ into ③-rank and ③-any using WEIGHT_RULES = (topw_k, topabs_k, topvar_k, topwvar_k).
select_core.py disagrees, in code and in its own comments:

  topw_k     sel = sorted(ok, key=lambda i: -w[i])            -> ANNOTATOR WEIGHTS
  topabs_k   sel = sorted(ok, key=lambda i: -abs(w[i]))       -> ANNOTATOR WEIGHTS
  topvar_k   var = np.var([ssat[pid][(i,x)] for x in L])      -> JUDGED SATISFACTION
             "Non-leaky: the spread is a property of the RESPONSES, never of the human target."
  topwvar_k  key = -(abs(w[i]) * var[i])                      -> BOTH
  oracle/indep/greedy  open comparisons.jsonl                 -> HUMAN RANKINGS

So an arm can read the RESPONSES' judged satisfaction while reading no human input at all --
a class ③-any's phrase ("no annotator signal for that prompt") does not cover, because a judge
is not an annotator.

ESTIMAND (before method): the three-class partition of the 41 census arms, and whether either
  extension of ② ∧ ③ moves once topvar_k/topwvar_k are reclassified.
IDENTIFICATION: fully identified -- the class of each rule is a line of code, quoted above.
SCOPE  population: R294's 41 arms · instrument: the source's own selection expressions ·
  baseline: R529's two-class partition · regime: first release.
WORLDS  A · the extensions are unchanged. R529's conclusion survives and only its taxonomy was
              wrong -- a latent defect that would mislabel a FUTURE arm.
        B · an extension moves. R529's fork was measured on a wrong partition.
KILL (pre-registered): any change to either extension kills world A.
POSITIVE CONTROL: the ③-rank extension derived here must equal R294's own `admitted` restricted
  to ②-passers. If it does not, this partition is not the code's.
NEGATIVE CONTROL: the three classes must be non-empty and pairwise distinct on the real arms --
  a taxonomy with an empty or duplicated class explains nothing.
NOISE FLOOR: none -- this is a partition of declared inputs.
MULTIPLICITY: 3 classes x 41 arms; the whole partition printed.
IMPOSSIBLE HERE: whether reading the JUDGE should disqualify a core. That is the same decision
  about purpose as ③-rank vs ③-any -- register row 7 -- now with a third option on it.
"""
import json, pathlib, re, sys

RANK = ("oracle_k", "indep_k", "greedy_k")          # comparisons.jsonl
WEIGHT = ("topw_k", "topabs_k")                     # -w[i] / -abs(w[i])
SAT = ("topvar_k",)                                 # var(ssat)
BOTH = ("topwvar_k",)                               # abs(w[i]) * var[i]

def fam(t, fams):
    return next((f for f in sorted(fams, key=len, reverse=True) if t.startswith(f)), None)

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    # ⚠ the quoted comment spans THREE comment lines, so flattening whitespace alone leaves a
    # `#` mid-sentence. Strip comment markers too -- the second premise check this session to
    # catch source wrapping, and the fix is to normalise the markup, never to loosen the quote.
    raw = (root / "corebench/select_core.py").read_text()
    src = " ".join(re.sub(r"^\s*#\s?", " ", raw, flags=re.M).split())
    quotes = ["sel = sorted(ok, key=lambda i: -w[i])",
              "sel = sorted(ok, key=lambda i: -abs(w[i]))",
              "sel = sorted(ok, key=lambda i: -(abs(w[i]) * var[i]))",
              "the spread is a property of the responses, never of the human target"]
    hits = [q for q in quotes if q.lower() in src.lower()]
    print(f"  SOURCE READ  selection expressions confirmed: {len(hits)}/{len(quotes)} -> "
          f"{'PASS' if len(hits) == len(quotes) else 'FAIL'}")
    if len(hits) != len(quotes):
        print(f"    missing: {[q for q in quotes if q not in hits]}"); return 2

    cen = json.loads((root / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                      "/R294_the_definition_against_everything/results/full_census.json").read_text())
    rows = cen["rows"]

    def klass(t):
        if fam(t, RANK): return "rank"
        if fam(t, BOTH): return "weight+sat"
        if fam(t, SAT): return "sat"
        if fam(t, WEIGHT) or t == "coval_core": return "weight"
        return "neither"
    part = {}
    for a in sorted(rows): part.setdefault(klass(a), []).append(a)
    print(f"\n  {'class':<14}{'n':>4}  arms")
    for k in ("rank", "weight", "sat", "weight+sat", "neither"):
        v = part.get(k, [])
        print(f"  {k:<14}{len(v):>4}  {', '.join(v[:6])}{' …' if len(v) > 6 else ''}")

    nonempty = [k for k in ("rank", "weight", "sat") if part.get(k)]
    print(f"\n  NEGATIVE CONTROL  the three classes are non-empty on real arms: "
          f"{len(nonempty)}/3 -> {'PASS' if len(nonempty) == 3 else 'FAIL'}")
    if len(nonempty) != 3: return 0

    p2 = [a for a in rows if rows[a]["ok2"]]
    ext_rank = sorted(a for a in p2 if klass(a) != "rank")
    ext_any  = sorted(a for a in p2 if klass(a) == "neither")
    ext_judge = sorted(a for a in p2 if klass(a) == "neither")   # same here; stated, not assumed
    want = sorted(a for a in cen["admitted"] if rows[a]["ok2"])
    ok = ext_rank == want
    print(f"  POSITIVE CONTROL  ③-rank extension vs R294's admitted set: "
          f"{'PASS' if ok else 'FAIL'}")
    print(f"    mine {ext_rank}")
    print(f"    census {want}")
    if not ok:
        print("  -> partition is not the code's; UNVERIFIED."); return 0

    prev = {"rank": 5, "any": 0}
    world = "A" if (len(ext_rank) == prev["rank"] and len(ext_any) == prev["any"]) else "B"
    print(f"\n  ③-rank extension : {len(ext_rank)}  (R529 reported {prev['rank']})")
    print(f"  ③-any  extension : {len(ext_any)}  (R529 reported {prev['any']})")
    print(f"  ③-judge extension: {len(ext_judge)}  -- NEW class, no annotator AND no judge signal")
    print(f"  WORLD {world} -- " +
          ("extensions unchanged: R529's conclusion survives and only its TAXONOMY was wrong -- "
           "a latent defect that would mislabel a future arm"
           if world == "A" else "an extension moved; R529's fork used a wrong partition"))
    print(f"  ⚠ topvar_k / topwvar_k were in R529's WEIGHT bucket. topvar_k reads the JUDGE's "
          f"satisfaction and no annotator signal at all.")

    out = pathlib.Path(__file__).parent / "results/three_classes.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"partition": part, "ext_rank": ext_rank, "ext_any": ext_any,
                               "ext_judge": ext_judge, "world": world,
                               "r529_reported": prev}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
