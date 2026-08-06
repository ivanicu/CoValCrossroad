#!/usr/bin/env python3
"""R830 -- was the correct determinism idiom learned, or was it always there?

See PREREGISTRATION.txt, committed before this file was executed.

ESTIMAND        the number of correct-idiom rounds with an index STRICTLY BELOW the earliest
                defective round. Zero => learning possible. Non-zero => learning refuted, because
                an idiom already in use cannot later be learned.
IDENTIFICATION  from the ordering alone. ⚠ PARTLY A DERIVATION: R-indices are assigned in sequence
                so the ORDER is free; what is not forced is whether the sets separate along it.
                Could have come out otherwise, so it is a cheap measurement, not a theorem.
SCOPE           population: every R-indexed directory under E01..E05. instrument: AST over
                committed source, same scan as R829. regime: syntactic.
WORLDS          W-LEARNED (0 precede -- the six are legacy, a note would suffice) vs
                W-ALWAYS-THERE (>=1 precedes -- only a MECHANICAL remedy can work).
KILL            CONDITIONAL. Evaluated only if the positive control reports SEPARATED and both
                negative arms report NOT SEPARATED. Otherwise UNVERIFIED and no world is chosen.
POSITIVE CTRL   a synthetic separated pair must report SEPARATED.
NEGATIVE CTRL   identical sets, and a straddling set, must both report NOT SEPARATED.
CLUSTER REPORT  n_eff = maximal runs of consecutive-in-corpus indices, reported BESIDE the raw
                count. 22 rows that are 6 clusters may not be quoted as 22 observations.
⛔ WITHDRAWN     a permutation drawing 22 rounds at random from the 821 gives p = 0.0002 for the
                correct-idiom rounds falling inside the defects' span. INADMISSIBLE: 14 of the 22
                are the contiguous block R679-R708, so one arc is counted as fourteen independent
                units. Recorded, never reported as evidence.
ARTIFACT        results/r830_idiom_timing.json with source hash.
IMPOSSIBLE      WHY a round used one form and not the other is not in the repository. Only
                AVAILABILITY is claimed; no intent is.
"""
from __future__ import annotations
import ast, hashlib, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
RES = HERE / "results"
DEFECTS = {332, 361, 436, 672, 731, 746}      # the six, from a_control_that_cannot_fail + R436


def separated(idiom: set[int], defect: set[int]) -> bool:
    """every idiom index strictly above every defect index."""
    return bool(idiom) and bool(defect) and min(idiom) > max(defect)


def clusters(xs, universe) -> int:
    """maximal runs that are consecutive IN THE CORPUS, not in the integers -- gaps in the
    numbering are not evidence of separation."""
    u = sorted(universe)
    pos = {v: i for i, v in enumerate(u)}
    s = sorted(pos[x] for x in xs if x in pos)
    if not s:
        return 0
    return 1 + sum(1 for a, b in zip(s, s[1:]) if b - a > 1)


def scan_corpus():
    idiom, allr = set(), set()
    for d in sorted(p for p in ROOT.glob("E0*") if p.is_dir()):
        for sub in d.rglob("R*"):
            if sub.is_dir():
                m = re.match(r"R(\d+)_", sub.name)
                if m:
                    allr.add(int(m.group(1)))
        for m in d.rglob("*.py"):
            r = re.search(r"/R(\d+)_", str(m))
            if not r:
                continue
            try:
                t = ast.parse(m.read_text(errors="ignore"))
            except SyntaxError:
                continue
            for nd in ast.walk(t):
                if not (isinstance(nd, ast.Compare) and len(nd.ops) == 1
                        and isinstance(nd.ops[0], ast.Eq)):
                    continue
                try:
                    if ast.unparse(nd.left) != ast.unparse(nd.comparators[0]):
                        continue
                except Exception:
                    continue
                if any(isinstance(x, ast.Call) for x in ast.walk(nd.left)):
                    idiom.add(int(r.group(1)))
    return idiom, allr


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    print("\n  R830 · WAS THE CORRECT IDIOM LEARNED, OR WAS IT ALWAYS THERE?\n")

    pos = separated({800, 810}, {300, 400})
    neg_same = separated({300, 400}, {300, 400})
    neg_strad = separated({250, 800}, {300, 400})
    print(f"  POSITIVE  a synthetic SEPARATED pair -> "
          f"{'SEPARATED   PASS' if pos else '⛔ NOT SEPARATED — the statistic cannot detect it'}")
    print(f"  NEGATIVE  identical sets            -> "
          f"{'not separated   PASS' if not neg_same else '⛔ SEPARATED — over-fires'}")
    print(f"  g=0       a straddling set          -> "
          f"{'not separated   PASS' if not neg_strad else '⛔ SEPARATED — over-fires'}")

    idiom, allr = scan_corpus()
    if not allr or not idiom:
        print("\n  ⛔ EMPTY POPULATION — nothing was examined. Exit 2, never 0.")
        return 2
    before = sorted(r for r in idiom if r < min(DEFECTS))
    after = sorted(r for r in idiom if r > max(DEFECTS))
    n_eff = clusters(idiom, allr)

    print(f"\n  corpus: {len(allr)} R-indexed rounds, {min(allr)}..{max(allr)}")
    print(f"  correct idiom `f() == f()` in {len(idiom)} rounds -- "
          f"n_eff = {n_eff} CLUSTERS of consecutive-in-corpus indices")
    print(f"  the six defective rounds: {sorted(DEFECTS)}")
    print(f"\n  idiom rounds BEFORE the earliest defect (R{min(DEFECTS)}): {before}  -> {len(before)}")
    print(f"  idiom rounds AFTER  the latest   defect (R{max(DEFECTS)}): {after}  -> {len(after)}")

    controls_ok = pos and not neg_same and not neg_strad
    if controls_ok:
        world = "W-LEARNED" if not before else "W-ALWAYS-THERE"
        verdict = ("no correct-idiom round precedes the earliest defect -- learning is possible "
                   "and the six may be legacy" if not before else
                   f"{len(before)} correct-idiom round(s) precede the earliest defect by "
                   f"{min(DEFECTS) - max(before)} indices -- the idiom was AVAILABLE and did not "
                   f"prevent the defect, so only a MECHANICAL remedy can work")
    else:
        world, verdict = "UNVERIFIED", "a control is unfit; no world is chosen"
    print(f"\n  VERDICT: {world} -- {verdict}\n")
    print("  ⚠ n_eff is CLUSTERS, not rows. The raw 22 includes the contiguous block R679-R708;")
    print("     it may not be quoted as 22 independent observations, and the p = 0.0002 from a")
    print("     22-row permutation is WITHDRAWN for exactly that reason.")
    print("  ⚠ AVAILABILITY is claimed, never intent. Why a round used one form is not in the repo.\n")

    out = {"world": world, "verdict": verdict, "n_idiom_rounds": len(idiom),
           "n_eff_clusters": n_eff, "idiom_rounds": sorted(idiom),
           "defect_rounds": sorted(DEFECTS), "before": before, "after": after,
           "n_corpus_rounds": len(allr),
           "withdrawn_p_0_0002": "22-row permutation; 14 of 22 are one contiguous arc",
           "controls": {"positive_separated": pos, "negative_identical_null": not neg_same,
                        "g0_straddle_null": not neg_strad},
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]}
    (RES / "r830_idiom_timing.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"  artifact -> {RES/'r830_idiom_timing.json'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
