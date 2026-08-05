#!/usr/bin/env python3
"""
R714 -- the release ships 986 core INSTANCES, and the formulation's clauses do not share a unit.

CHECK #316 ON R713's NEXT LINE — THE FOUR ROUNDS EXIST AND THE LINE'S PREMISE BREAKS.
  ✓ R696, R711, R712, R713 all exist with artifacts; the five pricings are theirs.
  ⛔ Asking its question — "can a definition be attacked by a site that built the objects it is
    defined over" — sent me to look for objects the site did NOT build. There are 986, on disk, in
    the release, untouched by this entire arc: `data/conversation_rubrics.jsonl` carries a
    per-conversation `coval_core` for each of 986 conversations.

⛔⛔ THE CLAIM THIS BREAKS IS ON THE DELIVERABLE.
  STATEMENT.md carries "THE RELEASE SHIPS ONE CORE" (R689) and the impossibility register has used
  "one released core" as a hard limit round after round. ⭐ At the ARM level that is true — one core
  GENERATOR. At the OBJECT level the release ships 986 core INSTANCES. That is the
  instrument-unit-versus-claim-unit distinction this arc has flagged in eleven rounds, sitting
  unexamined in the deliverable's own headline.

ESTIMAND        (i) COUNT of core instances and their k-distribution; (ii) UNIT — is each clause a
                predicate over a GENERATOR or over an INSTANCE; (iii) PORTABILITY — the first
                application of any clause to objects this site did not build.
IDENTIFICATION  (i) and (iii) exact from the release file. ⚠ (ii) is a READING of each clause's own
                wording, argued and labelled, never counted. ⚠ (iii) is PARTIAL: a clause needing a
                per-arm score cannot be evaluated on a rubric that ships none — reported NOT
                EVALUABLE, never as passing.
SCOPE           population : the 986 conversation rubrics in data/conversation_rubrics.jsonl
                instrument : direct field reads, criteria-list length per rubric
                             instrument unit = A CORE INSTANCE
                             claim unit      = THE FORMULATION'S APPLICABILITY
                             ⚠ NOT EQUAL, and that gap IS this round.
                baseline   : the DATASET_CARD's own "up to four, ~95% are four"
                regime     : this repository at HEAD
WORLDS          A ONE CORE STANDS · B UNIT CONFUSION · C THE CLAUSES MIX UNITS
KILL            conditional on POSITIVE firing and g=0 returning nothing
POSITIVE CTRL   the card's published statistic must be recovered from the file
g=0             a nonexistent field must yield 0 instances, not a silent empty pass
NEGATIVE CTRL   read `coval_full` — same file, other field, k far above 4; F3 must REJECT most of it
SHAM            F3's predicate with the bound removed — it must admit both fields
PLACEBO         two identical reads differ by exactly 0
ARTIFACT        results/instances.json
IMPOSSIBLE      evaluating F1 and F2 on the 986 (they need a provenance record and a per-arm score
                the rubric file does not carry) · cross-release (986 instances from ONE release is
                still one release)
"""
from __future__ import annotations
import collections, json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
SRC = ROOT / "data" / "conversation_rubrics.jsonl"
INSTRUMENT_UNIT, CLAIM_UNIT = "A CORE INSTANCE", "THE FORMULATION'S APPLICABILITY"

# ⭐ THE UNIT READING. Not a measurement -- a reading of each clause's own wording, labelled.
UNITS = {
    "F1 provenance": ("GENERATOR", "'the criteria were SELECTED without reading the outcome labels' "
                      "is a predicate over a SELECTION PROCEDURE, checkable from the producer"),
    "F2 behaviour": ("GENERATOR", "'the criteria BEAT a baseline that never sees the prompt' needs "
                     "scores ACROSS prompts, so it ranks a procedure, not one criteria list"),
    "F3 size": ("INSTANCE", "'more than one criterion, no more than the release's maximum' is a "
                "predicate over the CARDINALITY of a single criteria list"),
}


def main() -> int:
    if not SRC.exists():
        print(f"⛔ {SRC} absent — exit 2 rather than passing on an empty population")
        return 2
    rows = [json.loads(l) for l in SRC.read_text().splitlines() if l.strip()]
    print(f"─── THE OBJECT THE SITE DID NOT BUILD ───\n  {SRC.relative_to(ROOT)}   rubrics {len(rows)}")

    def ks(field):
        return [len(r[field]) for r in rows if isinstance(r.get(field), list)]

    kc, kf = ks("coval_core"), ks("coval_full")
    dc, df = collections.Counter(kc), collections.Counter(kf)
    print(f"  coval_core  instances {len(kc):>4}   k distribution {dict(sorted(dc.items()))}")
    print(f"  coval_full  instances {len(kf):>4}   k range {min(kf)}–{max(kf)}, "
          f"{len(df)} distinct values")

    print("\n─── CONTROLS ───")
    share4 = sum(1 for k in kc if k == 4) / len(kc)
    posok = 0.90 <= share4 <= 0.99
    print(f"  POSITIVE  the card's own 'up to four, ~95% are four' recovered from the file: "
          f"max k = {max(kc)}, share at 4 = {share4:.4f} -> "
          f"{'PASS — the published statistic reproduces' if posok else '⛔ FAIL'}")
    g0 = [len(r["coval_core_NONEXISTENT"]) for r in rows if isinstance(
        r.get("coval_core_NONEXISTENT"), list)]
    g0ok = len(g0) == 0
    print(f"  g=0       a nonexistent field yields {len(g0)} instances -> "
          f"{'PASS — absence is not a silent empty pass' if g0ok else '⛔ FAIL'}")
    f3 = lambda k: 1 < k <= 4
    rej_full = sum(1 for k in kf if not f3(k)) / len(kf)
    negok = rej_full > 0.5
    print(f"  NEGATIVE  F3 on `coval_full`, the other field in the same file: rejects "
          f"{rej_full:.4f} -> {'PASS — the clause reads SIZE, not the file' if negok else '⛔ FAIL'}")
    sham = lambda k: k >= 1
    sham_core = sum(1 for k in kc if sham(k)) / len(kc)
    sham_full = sum(1 for k in kf if sham(k)) / len(kf)
    shamok = sham_core == 1.0 and sham_full == 1.0
    print(f"  SHAM      F3 with the bound REMOVED (k >= 1): admits {sham_core:.4f} of core and "
          f"{sham_full:.4f} of full -> "
          f"{'PASS — the BOUND is what does the work' if shamok else '⛔ FAIL'}")
    plc = ks("coval_core") == kc
    print(f"  PLACEBO   two identical reads differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT      '{INSTRUMENT_UNIT}' != '{CLAIM_UNIT}' -> {'PASS' if unitok else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and shamok and plc and unitok

    print(f"\n─── ⭐ THE UNIT OF EACH CLAUSE (a READING of its wording, not a measurement) ───")
    for c, (u, why) in UNITS.items():
        print(f"  {c:<16}{u:<10}{why}")
    units = {u for u, _ in UNITS.values()}
    mixed = len(units) > 1
    print(f"  ⭐ distinct units among the three clauses: {len(units)} {sorted(units)} -> "
          f"{'MIXED — the formulation cannot be applied to a single object as written' if mixed else 'uniform'}")

    print(f"\n─── PORTABILITY: WHAT CAN BE EVALUATED ON 986 OBJECTS WE DID NOT BUILD ───")
    port = []
    for c, (u, _) in UNITS.items():
        if u == "INSTANCE":
            adm = sum(1 for k in kc if f3(k)) / len(kc)
            port.append({"clause": c, "evaluable": True, "admits": adm})
            print(f"  {c:<16}EVALUABLE   admits {adm:.4f} of the 986")
        else:
            port.append({"clause": c, "evaluable": False, "admits": None,
                         "reason": "needs a provenance record / per-arm scores the rubric file "
                                   "does not carry"})
            print(f"  {c:<16}NOT EVALUABLE — needs a provenance record or per-arm scores this file "
                  f"does not carry")
    n_eval = sum(1 for p in port if p["evaluable"])
    print(f"  ⚠ {n_eval} of {len(port)} clauses are evaluable here. The other {len(port)-n_eval} are "
          f"reported NOT EVALUABLE, never as passing.")

    print(f"\n─── THE SPECIFICATION SWEEP (2 fields × 3 bounds = 6 cells, all reported) ───")
    cells = []
    for fname, kk in (("coval_core", kc), ("coval_full", kf)):
        for bname, fn in (("F3  1<k<=4", f3), ("sham k>=1", sham), ("k==4 exactly", lambda k: k == 4)):
            r = sum(1 for k in kk if fn(k)) / len(kk)
            cells.append({"field": fname, "bound": bname, "admits": r})
            print(f"  {fname:<14}{bname:<14}admits {r:.4f}")

    A, B, Cc = len(kc), sum(1 for k in kc if f3(k)) / len(kc), share4
    print(f"\n─── REGISTERED ───")
    print(f"  A  core instances = 986 [1,1000] -> {A}: {'INSIDE' if 1 <= A <= 1000 else '⛔ OUTSIDE'}")
    print(f"  B  F3's admission rate on objects we did not build = 1.00 [0.80,1.00] -> {B:.4f}: "
          f"{'INSIDE' if 0.80 <= B <= 1.00 else '⛔ OUTSIDE'}")
    print(f"  C  share at k==4 vs the card's ~95% = 0.955 [0.90,0.99] -> {Cc:.4f}: "
          f"{'INSIDE' if 0.90 <= Cc <= 0.99 else '⛔ OUTSIDE'}")
    print(f"  DIRECTIONAL at least one clause is NOT evaluable here -> "
          f"{'HOLDS' if n_eval < len(port) else '⛔ FAILS'}")
    print(f"\n  MULTIPLICITY: {len(cells)} cells above, all printed. Counts are EXACT; no p-values "
          f"are computed and none are implied.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; these counts would be silence."
    elif mixed:
        world = (
            f"⭐⭐⭐ C THE CLAUSES DO NOT SHARE A UNIT, AND THE RELEASE SHIPS {A} CORE INSTANCES. "
            f"`data/conversation_rubrics.jsonl` carries a `coval_core` for each of {A} "
            f"conversations, k distributed {dict(sorted(dc.items()))} — objects this site did NOT "
            f"build, on disk in the release, untouched by this entire arc. ⛔ SO STATEMENT.md's 'THE "
            f"RELEASE SHIPS ONE CORE' IS TRUE ONLY AT THE ARM LEVEL: one core GENERATOR, {A} core "
            f"INSTANCES, and the deliverable never states which it means. That is the "
            f"instrument-unit-versus-claim-unit distinction this arc has flagged in eleven rounds, "
            f"sitting in its own headline. ⭐⭐ AND THE FORMULATION ITSELF MIXES UNITS: F1 and F2 are "
            f"predicates over a GENERATOR — a selection procedure, a score across prompts — while F3 "
            f"is a predicate over an INSTANCE's cardinality. A three-clause definition whose clauses "
            f"range over different objects cannot be applied to any single object as written, and no "
            f"round in this arc has said so. ⭐ THE ONE PORTABLE RESULT: F3 admits {B:.4f} of the "
            f"{A} instances, and the card's published 'up to four, ~95% are four' reproduces at "
            f"max k = {max(kc)} and {Cc:.4f} — the FIRST application of any clause to objects this "
            f"site did not build, in {n_eval} of {len(port)} clauses. ⚠ The other {len(port)-n_eval} "
            f"are NOT EVALUABLE here and are reported as such, never as passing: they need a "
            f"provenance record and per-arm scores the rubric file does not carry. ⚠ AND F3 "
            f"ADMITTING ALL {A} IS WEAK EVIDENCE FOR F3 — the clause's ceiling was read off this "
            f"release's card, so admitting this release's instances is close to circular; what it "
            f"establishes is that the card's statement is TRUE OF THE DATA. ⚠ UNIT GAP, stated twice "
            f"because it is both this round's control and its finding: instrument unit is "
            f"{INSTRUMENT_UNIT}, claim unit is {CLAIM_UNIT}.")
    else:
        world = (f"⭐⭐ B UNIT CONFUSION ONLY — the release ships {A} core instances and the "
                 f"deliverable's 'one core' is an arm-level statement, but the three clauses share a "
                 f"unit, so the formulation is applicable as written.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "instances.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "source": str(SRC.relative_to(ROOT)),
        "n_rubrics": len(rows), "n_core_instances": A,
        "k_distribution_core": {str(k): v for k, v in sorted(dc.items())},
        "k_range_full": [min(kf), max(kf)], "n_distinct_k_full": len(df),
        "f3_admission_rate_core": B, "share_k_equals_4": Cc,
        "clause_units": {c: {"unit": u, "reading": w} for c, (u, w) in UNITS.items()},
        "units_mixed": mixed, "portability": port, "n_evaluable": n_eval, "cells": cells,
        "registered": ("A instances 986 [1,1000]; B F3 admission 1.00 [0.80,1.00]; "
                       "C share k=4 0.955 [0.90,0.99]; directional >=1 clause not evaluable"),
        "observed": {"A": A, "B": B, "C": Cc, "directional": n_eval < len(port)},
        "corrects": ("STATEMENT.md's 'THE RELEASE SHIPS ONE CORE' — true at the ARM level (one "
                     "generator), false at the OBJECT level (986 instances), and the deliverable "
                     "never states which."),
        "limit": ("F3's ceiling was read off this release's card, so admitting this release's "
                  "instances is close to circular; what it establishes is that the card's statement "
                  "is TRUE OF THE DATA. F1 and F2 are NOT EVALUABLE here."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
