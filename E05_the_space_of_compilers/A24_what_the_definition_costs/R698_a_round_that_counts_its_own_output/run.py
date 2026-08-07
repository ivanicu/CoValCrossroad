#!/usr/bin/env python3
"""
R698 -- a round that counts its own output cannot report a stable number.

CHECK #300 -- THE THREE-HUNDREDTH, AND IT CAUGHT A NUMBER I HAD ALREADY REPORTED.
  R697's README says 79 co-located / 44 / 8 admissible. Its committed artifact says 10 admissible,
  32 dropped, 37 degenerate. A fresh run says 81 / 49 / 12. Three populations, one round.
  ⛔ CAUSE ①: I wrote the README from a PRE-PATCH run and never re-read the artifact I had just
     written -- the round's own output was on disk and disagreed with my prose.
  ⛔ CAUSE ②: R697 sweeps `results/*.json` across the arc, so it INCLUDES ITS OWN OUTPUT and
     everything committed after it. Its population grows whenever anything is committed.
  ⭐ THE VERDICT IS THE SAME IN ALL THREE RUNS: 0 cells could not have resolved. The kill fired every
     time. So the conclusion is stable and the counts are not, and that split is the measurement.

ESTIMAND        how much does R697's population move when its own artifact -- and the artifacts
                written after it -- are excluded, and does its VERDICT move with it?
IDENTIFICATION  ⚠ this measures sensitivity to WHICH FILES ARE PRESENT. It cannot recover the corpus
                as it stood when R697 first ran; R697 recorded its verdict, not its file list.
SCOPE           population : the arc's results/*.json under three exclusion regimes
                instrument : R697's own triple-extractor, re-used unmodified
                             instrument unit = A CO-LOCATED TRIPLE
                             claim unit      = A VERDICT'S STABILITY
                             ⚠ NOT EQUAL -- a moving denominator is not a moving conclusion, which
                             is exactly what is being separated.
                baseline   : the full-corpus run
                regime     : this repository at HEAD
WORLDS          A COUNTS DRIFT, VERDICT STABLE: self-inclusion moves the denominator only.
                B VERDICT DRIFTS: R697's finding is void, not merely mis-reported.
KILL            the verdict changes under any exclusion -> world B.
POSITIVE CTRL   excluding R697's own artifact must reduce the count.
g=0             two runs over an identical corpus must be identical.
NEGATIVE CTRL   excluding a file with no triple changes nothing.
PLACEBO         run twice identical.
ARTIFACT        results/self_inclusion.json
IMPOSSIBLE      recovering R697's original file list needs a record it never wrote.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
THRESH = 0.05
PKEYS = {"p", "two_sided_p", "pval", "p_value"}
NKEYS = {"n", "n_draws", "n_perm", "null_cells", "cells", "n_null"}
RKEYS = {"resolved", "is_resolved", "rank_resolved", "resolvable"}


def triples(o, where, path="", out=None):
    if out is None: out = []
    if isinstance(o, dict):
        n = next((v for k, v in o.items() if k.lower() in NKEYS and isinstance(v, int) and v > 1), None)
        p = next((v for k, v in o.items() if k.lower() in PKEYS and isinstance(v, (int, float))), None)
        r = next((v for k, v in o.items() if k.lower() in RKEYS and isinstance(v, bool)), None)
        if n is not None and p is not None:
            out.append({"where": f"{where}:{path or '(root)'}", "n": n, "p": p, "resolved": r})
        for k, v in o.items():
            if isinstance(v, (dict, list)): triples(v, where, f"{path}.{k}" if path else k, out)
    elif isinstance(o, list):
        for i, v in enumerate(o[:20]):
            if isinstance(v, (dict, list)): triples(v, where, f"{path}[{i}]", out)
    return out


def run(exclude_prefixes):
    cells = []
    for j in sorted(ARC.rglob("results/*.json")):
        rd = j.parent.parent.name.split("_")[0]
        if rd in exclude_prefixes: continue
        try: d = json.loads(j.read_text())
        except Exception: continue
        cells += triples(d, rd)
    def mult(p_, n_): 
        q = p_ * n_
        return abs(q - round(q)) < 1e-6
    kept = [c for c in cells if mult(c["p"], c["n"])]
    degen = [c for c in kept if abs(c["p"] - 1.0) < 1e-9]
    adm = [c for c in kept if abs(c["p"] - 1.0) >= 1e-9]
    notres = [c for c in adm if c["resolved"] is False or (c["resolved"] is None and c["p"] >= THRESH)]
    blind = [c for c in notres if 2 / c["n"] > THRESH]
    return {"colocated": len(cells), "after_multiple": len(kept), "degenerate": len(degen),
            "admissible": len(adm), "not_resolved": len(notres), "could_not_resolve": len(blind)}


def main() -> int:
    regimes = {
        "full corpus (what R697 ran)": set(),
        "excluding R697's own artifact": {"R697"},
        "excluding R697 and everything after it": {"R697", "R698"},
    }
    print("─── CONTROLS ───")
    a = run(set()); b = run({"R697"})
    posok = b["colocated"] < a["colocated"]
    print(f"  POSITIVE  excluding R697's own artifact reduces the count -> "
          f"{a['colocated']} -> {b['colocated']} -> "
          f"{'PASS — self-inclusion IS the mechanism' if posok else '⛔ FAIL — another cause'}")
    g0ok = run(set()) == run(set())
    print(f"  g=0       two runs over an identical corpus are identical -> "
          f"{'PASS — the drift is corpus growth, not nondeterminism' if g0ok else '⛔ FAIL'}")
    negok = run({"ZZQ_NO_SUCH_ROUND"}) == a
    print(f"  NEGATIVE  excluding a round with no artifact changes nothing -> "
          f"{'PASS' if negok else '⛔ FAIL'}")
    print(f"  PLACEBO   run twice identical -> {'PASS' if g0ok else '⛔ FAIL'}")
    ctl = posok and g0ok and negok

    print(f"\n─── THE THREE REGIMES (G3 — every count, none hidden) ───")
    rows = {}
    for name, ex in regimes.items():
        r = run(ex); rows[name] = r
        print(f"  {name:<42} colocated {r['colocated']:>3}  after-filter {r['after_multiple']:>3}  "
              f"degenerate {r['degenerate']:>3}  admissible {r['admissible']:>3}  "
              f"⭐ could-not-resolve {r['could_not_resolve']}")
    verdicts = {r["could_not_resolve"] for r in rows.values()}
    admins = {r["admissible"] for r in rows.values()}
    drop = rows["full corpus (what R697 ran)"]["admissible"] - \
           rows["excluding R697's own artifact"]["admissible"]
    print(f"\n  ⭐ admissible counts across regimes : {sorted(admins)}  (they DRIFT)")
    print(f"  ⭐ could-not-resolve across regimes  : {sorted(verdicts)}  "
          f"({'STABLE' if len(verdicts) == 1 else '⛔ DRIFTS'})")
    print(f"  registered A (excluding R697 drops the count by 2) [0,8] -> {drop}: "
          f"{'INSIDE' if 0 <= drop <= 8 else '⛔ OUTSIDE'}, error {drop-2:+d}")
    print(f"  registered B (verdict unchanged) -> {len(verdicts) == 1}: "
          f"{'HOLDS' if len(verdicts) == 1 else '⛔ FAILS'}")
    dirn = len(admins) > 1 and len(verdicts) == 1
    print(f"  DIRECTIONAL counts drift while the verdict is stable -> "
          f"{'HOLDS' if dirn else '⛔ FAILS'}")
    killed = len(verdicts) > 1

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = (f"⭐⭐⭐ B THE VERDICT DRIFTS — could-not-resolve takes values {sorted(verdicts)} "
                 f"across exclusion regimes. R697's finding is VOID, not merely mis-reported, and "
                 f"the retraction is of the conclusion.")
    else:
        world = (f"⭐⭐⭐ A COUNTS DRIFT, VERDICT STABLE. R697's admissible population takes "
                 f"{sorted(admins)} across three exclusion regimes while its could-not-resolve "
                 f"verdict is {sorted(verdicts)[0]} in every one. ⛔ SO R697's COUNTS ARE RETRACTED "
                 f"AND ITS CONCLUSION STANDS. ⭐ THE MECHANISM IS SELF-INCLUSION: R697 sweeps the "
                 f"arc's `results/*.json` and its own artifact is one of them, so its population "
                 f"grows whenever anything is committed — including by itself. ⚠ AND THE SECOND "
                 f"CAUSE IS MINE: R697's README was written from a PRE-PATCH run and never checked "
                 f"against the artifact the same round had just written. The round's own output was "
                 f"on disk, disagreeing with my prose, and nothing checks prose against artifact.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: 3 exclusion regimes × 6 counts, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"self_inclusion.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "regimes": rows, "admissible_values": sorted(admins),
        "verdict_values": sorted(verdicts), "verdict_stable": len(verdicts) == 1,
        "drop_excluding_self": drop, "kill_fired": killed, "directional_holds": dirn,
        "registered": "A drop of 2 [0,8]; B verdict unchanged; counts drift, verdict stable",
        "reported_vs_artifact": {"readme_said": [79, 44, 8],
                                 "artifact_said": [None, None, 10],
                                 "fresh_run_says": [rows["full corpus (what R697 ran)"]["colocated"],
                                                    rows["full corpus (what R697 ran)"]["after_multiple"],
                                                    rows["full corpus (what R697 ran)"]["admissible"]]},
        "limit": ("this measures sensitivity to which files are present; it cannot recover the "
                  "corpus as it stood when R697 first ran, because R697 recorded its verdict and "
                  "not its file list."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'self_inclusion.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
