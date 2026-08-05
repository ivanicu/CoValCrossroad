#!/usr/bin/env python3
"""R529 — ③ says "not built by reading the conversation's human labels". WHICH labels?

The deliverable asserts, two sentences apart: "② is satisfied by coval_core" and "③ is what
EMPTIES the definition". Both cannot hold -- R294's census has coval_core passing ② and ③.
Tracing it: DEFINITION.md records R475 excluding coval_core as a "w-reader", while R294's code
admits it. The release settles what a w-reader reads.

  DATASET_CARD.md:73 -- annotators "assign signed weights ranging from -10 to +10 ... the
    absolute value indicated the importance"
  DATASET_CARD.md:74 -- core selects "up to four rubric items with the highest average ratings"
  select_core.py:16  -- topw_k = "highest MEAN importance score. Non-leaky: the weights come
    from the rubric, not from the outcome."

So the ratings ARE annotator-authored, and they are NOT the ranking labels A2 predicts.
③ is therefore two-valued, and the two readings give different definitions.

ESTIMAND (before method): the extension of ② ∧ ③ under each reading of "human labels" --
  ③-rank (the response rankings only) and ③-any (any annotator-supplied signal for the prompt).
IDENTIFICATION: fully identified. Each arm's inputs are declared by its rule in select_core.py:
  oracle/greedy/indep open comparisons.jsonl (rankings); topw/topabs/topvar/topwvar consume
  rubric weights; random/full consume neither.
SCOPE  population: R294's 41 arms · instrument: R294's ok2 · baseline: n/a, this is a partition
  of the clause · regime: first release, home judge.
WORLDS  A · the two readings give the same extension. ③ is unambiguous and the contradiction in
              the deliverable is a wording slip.
        B · they differ. ③ names two different clauses, the page asserts both, and which one is
              meant decides whether any core exists.
KILL (pre-registered): identical extensions under both readings kills world B.
POSITIVE CONTROL: under ③-rank the extension must equal R294's own `admitted` restricted to
  ②-passers -- the census is the implementation of that reading. If it does not, the partition
  is not the code's.
NEGATIVE CONTROL: the two readings must differ for at least one ARM overall (not necessarily an
  admitted one), else the distinction is vacuous and no conclusion follows.
NOISE FLOOR: none -- this partitions declared inputs, it does not estimate.
MULTIPLICITY: 2 readings x 41 arms; both extensions printed whole.
IMPOSSIBLE HERE: which reading the release's authors INTENDED. The card describes construction,
  not a definition of core; choosing is a decision about purpose, which the register already
  lists as row 7 and calls not-a-measurement.
"""
import json, pathlib, sys

RANK_RULES = ("oracle_k", "indep_k", "greedy_k")                      # open comparisons.jsonl
WEIGHT_RULES = ("topw_k", "topabs_k", "topvar_k", "topwvar_k")        # consume rubric weights
NEITHER = ("random_k", "full", "generic", "gen", "promptecho")

def fam(t, fams):
    return next((f for f in sorted(fams, key=len, reverse=True) if t.startswith(f)), None)

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    cen = json.loads((root / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                      "/R294_the_definition_against_everything/results/full_census.json").read_text())
    rows = cen["rows"]
    card = (root / "data/DATASET_CARD.md").read_text()
    src = (root / "corebench/select_core.py").read_text()
    ok_card = "signed weights" in card and "highest average ratings" in card
    flat = " ".join(src.split())   # the source wraps this sentence across a line
    ok_src = "Non-leaky: the weights come from the rubric, not from the outcome." in flat
    print(f"  SOURCE READ  card documents annotator-assigned weights: {ok_card}")
    print(f"               select_core calls topw_k non-leaky, rubric-not-outcome: {ok_src}")
    if not (ok_card and ok_src):
        print("  -> cannot confirm the premise from the objects; UNRUNNABLE"); return 2

    def reads_rank(t):   return fam(t, RANK_RULES) is not None
    def reads_weight(t): return fam(t, WEIGHT_RULES) is not None or t == "coval_core"

    p2 = [a for a in rows if rows[a]["ok2"]]
    ext_rank = sorted(a for a in p2 if not reads_rank(a))
    ext_any  = sorted(a for a in p2 if not reads_rank(a) and not reads_weight(a))

    # POSITIVE CONTROL
    want = sorted(a for a in cen["admitted"] if rows[a]["ok2"])
    ok = ext_rank == want
    print(f"\n  POSITIVE CONTROL  ③-rank extension vs R294's own admitted set:")
    print(f"    mine   {ext_rank}")
    print(f"    census {want}")
    print(f"    -> {'PASS -- ③-rank IS what the code implements' if ok else 'FAIL'}")
    if not ok:
        print("  -> partition is not the code's; UNVERIFIED."); return 0

    diff = [a for a in rows if reads_weight(a) != reads_rank(a) and (reads_weight(a) or reads_rank(a))]
    print(f"  NEGATIVE CONTROL  arms where the two readings disagree: {len(diff)} -> "
          f"{'PASS' if diff else 'FAIL -- distinction vacuous'}")
    if not diff: return 0

    print(f"\n  ②-passers: {len(p2)}")
    print(f"  ③-rank (not built from the RANKINGS)      -> {len(ext_rank)}: {ext_rank}")
    print(f"  ③-any  (no annotator signal for the prompt) -> {len(ext_any)}: "
          f"{ext_any if ext_any else '(EMPTY)'}")
    world = "B" if ext_rank != ext_any else "A"
    print(f"\n  WORLD {world} -- " +
          ("③ names TWO clauses; the page asserts both, and the choice decides whether any core "
           "exists" if world == "B" else "the readings coincide; the contradiction is a slip"))
    print(f"  MULTIPLICITY  2 readings x {len(rows)} arms; both extensions printed whole")

    out = pathlib.Path(__file__).parent / "results/which_labels.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"n_pass2": len(p2), "ext_rank": ext_rank, "ext_any": ext_any,
                               "n_disagree_arms": len(diff), "world": world,
                               "positive_control": ok}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
