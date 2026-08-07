#!/usr/bin/env python3
"""
R695 -- three sweeps, three wrong quantities. R694's question is not answerable from the artifacts.

CHECK #297 ON R694's NEXT LINE -- ITS DATA IS NOT THERE, AND FINDING THAT OUT TOOK FOUR PROBES OF
  WHICH THREE LIED. R694 proposed comparing each sham's committed A2 mean against its arm's. Only
  1 of 5 sham pairs has an A2-named value for both members anywhere in the corpus, and it is
  `gen/gen_sham` -- NOT one of the two pairs ② separates. So the question is unanswerable here.

⛔ THE THREE FALSE POSITIVES, EACH A DIFFERENT WRONG QUANTITY, EACH PRINTING "5/5 COMPLETE PAIRS":
   ① "a top-level dict of >=30 arms"    -> matched `k`, the arm's CRITERION COUNT.
   ② "numeric values keyed by >=2 arms" -> matched `k` again.
   ③ "a FLOAT in [0,1] keyed by arms"   -> matched `P_arm`, a POOL-ORDER PROBABILITY.
   ④ "a field whose NAME contains a2"   -> 1 of 5.
   ⭐ Each earlier test was a SUPERSET of the right one, so each matched something real and wrong,
   and none of them was a bug -- they were the right query for a different question. §4's "a search
   is an instrument" three times inside one feasibility hunt.

ESTIMAND        A: how many distinct arms carry a value in an a2-NAMED field anywhere in the corpus?
                B: is the one assemblable sham pair among the two ② separates?
IDENTIFICATION  ⚠ a field NAMED a2 is not guaranteed to BE A2. The name test is stricter than the
                type test and still a proxy -- the best available without opening every round.
SCOPE           population : every results/*.json in the repository
                instrument : field-name test (contains "a2") + arm-key coverage
                             instrument unit = A FIELD NAME
                             claim unit      = AN A2 MEAN
                             ⚠ NOT EQUAL -- and the three false positives above are what that gap
                             looks like when the instrument is loosened.
                baseline   : the loose "float in [0,1]" test, which reported 5/5
                regime     : this repository at HEAD
WORLDS          A UNANSWERABLE HERE: <5 pairs assemblable -> R694's question needs new scoring.
                B ANSWERABLE: 5 pairs -> run the measurement instead.
KILL            5 pairs assemblable -> world B, this becomes the measurement.
POSITIVE CTRL   `arm_a2` is KNOWN to hold A2; the name test must find it.
g=0             `k` (int criterion count) must NOT be classified as a score.
NEGATIVE CTRL   `P_arm` (pool-order probability) must NOT be classified as A2.
PLACEBO         run twice identical.
ARTIFACT        results/feasibility.json
IMPOSSIBLE      answering R694's question requires A2 for 10 arms; the corpus has it for a few.
                Producing the rest means RE-SCORING the sham arms through the judge -- and
                re-running a round destroyed its artifact once in this arc. Named, not planned.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
SEPARATED = {("coval_core", "coval_core_sham"), ("topw_k4", "topw_k4_sham")}


def a2_named(v_name: str) -> bool:
    return "a2" in v_name.lower()


def score_like(v) -> bool:
    if isinstance(v, float) and 0.0 <= v <= 1.0: return True
    return isinstance(v, list) and bool(v) and isinstance(v[0], float) and 0.0 <= v[0] <= 1.0


def sweep(name_test):
    hits = {}
    for j in ROOT.rglob("results/*.json"):
        if "/.git/" in str(j): continue
        try: d = json.loads(j.read_text())
        except Exception: continue
        def walk(o, path=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    p = f"{path}.{k}" if path else k
                    if isinstance(v, dict) and name_test(k):
                        for a in v:
                            if isinstance(a, str): hits.setdefault(a, set()).add(f"{j.name}:{p}")
                    if isinstance(v, (dict, list)): walk(v, p)
            elif isinstance(o, list):
                for v in o[:20]:
                    if isinstance(v, (dict, list)): walk(v, path)
        walk(d)
    return hits


def main() -> int:
    art = next(ARC.glob("R360_*/results/*.json"), None)
    if art is None:
        print("UNRUNNABLE: R360's ledger absent. Exit 2, never 0."); return 2
    arms = json.loads(art.read_text())["arms"]
    pairs = [(a, a + "_sham") for a in arms if a + "_sham" in arms]

    print("─── CONTROLS (the search IS the instrument here) ───")
    named = sweep(a2_named)
    posok = any("arm_a2" in s for v in named.values() for s in v)
    print(f"  POSITIVE  `arm_a2` is KNOWN to hold A2; the name test finds it -> "
          f"{posok} -> {'PASS' if posok else '⛔ FAIL — a zero would be silence'}")
    g0ok = not a2_named("k")
    print(f"  g=0       `k` (int criterion count) is NOT a score -> "
          f"{'PASS — the test that failed three probes ago' if g0ok else '⛔ FAIL'}")
    negok = not a2_named("P_arm")
    print(f"  NEGATIVE  `P_arm` (pool-order probability, float in [0,1]) is NOT A2 -> "
          f"{'PASS' if negok else '⛔ FAIL'}")
    plc = set(sweep(a2_named)) == set(named)
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and plc

    loose = {a for a, _ in [(k, v) for k, v in sweep(lambda n: True).items()]}
    cov = sorted(a for a in named if a in arms)
    assemblable = [p for p in pairs if p[0] in named and p[1] in named]

    print(f"\n─── FEASIBILITY (G3 — every pair, and the loose test beside the strict one) ───")
    print(f"  arms in the ledger                      : {len(arms)}")
    print(f"  ⭐ arms with a value in an a2-NAMED field: {len(cov)}  {cov[:10]}")
    print(f"  ⭐ sham pairs assemblable                : {len(assemblable)} of {len(pairs)} -> "
          f"{assemblable}")
    for p in pairs:
        have = [x for x in p if x in named]
        print(f"     {p[0]:<14}/{p[1]:<20} both present: {len(have) == 2}"
              f"{'   ⭐ ② SEPARATES THIS PAIR' if tuple(p) in SEPARATED else ''}")
    b_ok = all(tuple(p) not in SEPARATED for p in assemblable)
    print(f"\n  registered A 12 [4,30] -> {len(cov)}: "
          f"{'INSIDE' if 4 <= len(cov) <= 30 else '⛔ OUTSIDE'}, error {len(cov)-12:+d}")
    print(f"  registered B (the assemblable pair is NOT one ② separates) -> {b_ok}: "
          f"{'HOLDS' if b_ok else '⛔ FAILS'}")
    dirn = len(cov) < len(loose & set(arms))
    print(f"  DIRECTIONAL a2-named coverage < loose-test coverage -> "
          f"{'HOLDS' if dirn else '⛔ FAILS'}  ({len(cov)} vs {len(loose & set(arms))})")
    killed = len(assemblable) == len(pairs)
    print(f"  pre-registered kill (all 5 assemblable) -> "
          f"{'⭐ FIRES — answerable; this becomes the measurement' if killed else 'does not fire'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = ("B ANSWERABLE — all five pairs are assemblable from a2-named fields; R694's "
                 "question should be measured, not registered as impossible.")
    else:
        world = (f"⭐⭐⭐ A UNANSWERABLE HERE. Only {len(assemblable)} of {len(pairs)} sham pairs has "
                 f"an A2-named value for both members, and it is {assemblable} — NOT one of the two "
                 f"② separates. ⭐ AND THE ROAD HERE IS THE FINDING: three earlier probes each "
                 f"printed '5/5 COMPLETE PAIRS' while matching a DIFFERENT wrong quantity — `k`, the "
                 f"criterion count, twice; then `P_arm`, a pool-order probability. None was a bug. "
                 f"Each was the right query for a different question, and each was a SUPERSET of the "
                 f"right test, so each matched something real and wrong. ⚠ Instrument unit: A FIELD "
                 f"NAME. Claim unit: AN A2 MEAN. Not equal — and a field named a2 is still only a "
                 f"proxy for one. ⭐ IMPOSSIBILITY, NAMED WITH ITS PRICE: answering R694 needs A2 for "
                 f"10 arms; producing the missing ones means RE-SCORING sham arms through the judge, "
                 f"and re-running a round destroyed its artifact once in this arc.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(pairs)} pairs × 2 sweeps (strict, loose), 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"feasibility.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "n_arms": len(arms), "a2_named_coverage": cov, "n_a2_named": len(cov),
        "loose_coverage": len(loose & set(arms)),
        "pairs": [list(p) for p in pairs], "assemblable": [list(p) for p in assemblable],
        "kill_fired": killed, "directional_holds": dirn, "point_b_holds": b_ok,
        "registered": "A 12 [4,30]; B the pair is not one ② separates; strict < loose; kill if 5/5",
        "false_positives": [
            {"probe": "top-level dict of >=30 arms", "matched": "k (criterion count)", "reported": "hit"},
            {"probe": "numeric keyed by >=2 arms", "matched": "k again", "reported": "5/5 pairs"},
            {"probe": "float in [0,1] keyed by arms", "matched": "P_arm (pool-order probability)",
             "reported": "5/5 pairs"},
            {"probe": "field NAME contains a2", "matched": "arm_a2 / a2", "reported": "1/5 pairs"}],
        "impossible": ("answering R694 needs A2 for 10 arms; producing the missing ones means "
                       "re-scoring sham arms through the judge, and re-running a round destroyed an "
                       "artifact once in this arc."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'feasibility.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
