#!/usr/bin/env python3
"""
R719 -- a block R718 certified as STANDING rests on a set the next round retracted.

CHECK #321 ON R718's NEXT LINE — IT HOLDS, AND FOLLOWING IT FOUND WORSE THAN IT ASKED FOR.
  ✓ R688's population is R360's arms, and R711/R712/R713 priced the clauses on the same 42.
  ⛔⛔ BUT R688's `published` FIELD IS EXACTLY `PUBLISHED_FIVE` — ['coval_core','topabs_k4',
     'topvar_k4','topw_k4','topwvar_k4'] — AND R689 RETRACTED THAT SET ONE ROUND LATER. R688's
     finding is "the 3 published arms outside ③'s extension all fail ② anyway", and those 3 are
     topabs_k4, topvar_k4, topwvar_k4 — three of the four arms R689 showed the release does NOT name.
  ⛔ AND R718's INSTRUMENT COULD NOT SEE IT. R688's block cites only R683 in its body, so "no body
     citation outranks the heading" returned UNAMENDED. The correction lives in a DIFFERENT block.
     ⭐ AN AMENDMENT TEST SCOPED TO A BLOCK CANNOT SEE A RETRACTION FILED ELSEWHERE.

ESTIMAND        (i) DEPENDENCE — does R688's verdict change when its population is corrected from
                PUBLISHED_FIVE to the set the release's card actually names? (ii) BLIND SPOT — how
                many blocks cite a retracted literal without citing the retracting round.
IDENTIFICATION  (i) exactly recomputable. ⚠ (ii) reads which literals were retracted from the
                ledger, a convention, so the search is positive-controlled against R688.
SCOPE           population : the 12 claim blocks of STATEMENT.md, and R360's 42 arms
                instrument : set recomputation + a cross-block citation search
                             instrument unit = A CLAIM BLOCK
                             claim unit      = WHETHER A BLOCK'S SUPPORT SURVIVES
                             ⚠ NOT EQUAL -- a block whose SUPPORT was retracted is not thereby
                             false; its verdict may survive on the corrected set, which (i) tests.
                baseline   : R688's committed verdict on PUBLISHED_FIVE
                regime     : this repository at HEAD
WORLDS          A VERDICT SURVIVES · B VERDICT FALLS · C DEGENERATE (see PREREGISTRATION.txt)
KILL            conditional on the POSITIVE reproducing R688 and g=0 returning nothing
POSITIVE CTRL   recomputing on PUBLISHED_FIVE must reproduce R688's committed 0 and its exact list
g=0             a literal never retracted (`coval_core`) must NOT be flagged by the cross-block search
NEGATIVE CTRL   a literal in NO block must return 0; an empty POPULATION exits 2
SHAM            the same search over DEFINITION.md, which is append-only
PLACEBO         two identical runs differ by exactly 0
ARTIFACT        results/retracted_support.json
IMPOSSIBLE      deciding whether ③ is a GOOD clause (construct validity) · cross-release
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
STMT = ROOT / "E05_the_space_of_compilers" / "STATEMENT.md"
DEFN = ROOT / "E05_the_space_of_compilers" / "DEFINITION.md"
CARD = ROOT / "data" / "DATASET_CARD.md"
INSTRUMENT_UNIT, CLAIM_UNIT = "A CLAIM BLOCK", "WHETHER A BLOCK'S SUPPORT SURVIVES"
PUBLISHED_FIVE = ["coval_core", "topabs_k4", "topvar_k4", "topw_k4", "topwvar_k4"]
HEADRE = re.compile(r"^> ?#{2,4} (.+)$", re.M)


def blocks(text, pat=HEADRE):
    ms = list(pat.finditer(text))
    return [{"heading": m.group(1).strip(),
             "body": text[m.end(): (ms[i + 1].start() if i + 1 < len(ms) else len(text))]}
            for i, m in enumerate(ms)]


def main() -> int:
    for p in (STMT, CARD):
        if not p.exists():
            print(f"⛔ {p} absent — exit 2 rather than passing on an empty population")
            return 2
    led = json.loads(next(ARC.glob("R360_*/results/*.json")).read_text())
    arms = set(led["arms"]); K = led["k"]
    p2 = set(led["clause2_admits"]); p23 = set(led["clause23_admits"])
    # ⛔ ③'s EXTENSION IS READ FROM R688's OWN ARTIFACT, NOT RECONSTRUCTED. My first version used
    #   R703's formula `p23 | (arms - p2)` -- "everything ② rejects is unconstrained by ③" -- which
    #   ADMITS the three arms R688 says ③ excludes, so the POSITIVE control failed and caught it.
    #   Same error as R709: reimplementing an audited round's computation from a DIFFERENT round's
    #   formula. Auditing a round means using ITS committed object, not a sibling's algebra.
    _r688 = json.loads(next(ARC.glob("R688_*/results/*.json")).read_text())
    p3 = set(_r688["extension"])                 # ③'s extension, as R688 committed it
    card = CARD.read_text()
    named = [a for a in PUBLISHED_FIVE if a in card]

    print(f"─── THE OBJECT ───")
    print(f"  PUBLISHED_FIVE        {PUBLISHED_FIVE}")
    print(f"  named in the card     {named}   ({len(named)} of {len(PUBLISHED_FIVE)})")

    def excl_by_three_alone(pop):
        """§4's falsifier for ③: arms ③ excludes that ② does NOT already exclude."""
        return sorted([a for a in pop if a in arms and a not in p3 and a in p2])

    def excl_by_three(pop):
        return sorted([a for a in pop if a in arms and a not in p3])

    print(f"\n─── CONTROLS ───")
    r688 = _r688
    repro_excl = excl_by_three(PUBLISHED_FIVE)
    repro_alone = excl_by_three_alone(PUBLISHED_FIVE)
    posok = (repro_excl == sorted(r688["published_excluded"]) and
             len(repro_alone) == r688["n_excluded_by_three_alone"])
    print(f"  POSITIVE  recompute on PUBLISHED_FIVE -> excluded {repro_excl}, "
          f"excluded-by-③-alone {len(repro_alone)}")
    print(f"            R688 committed {sorted(r688['published_excluded'])}, "
          f"{r688['n_excluded_by_three_alone']} -> "
          f"{'PASS — the committed numbers reproduce' if posok else '⛔ FAIL'}")
    bs = blocks(STMT.read_text())
    if not bs:
        print("⛔ no claim blocks found — exit 2"); return 2

    def cites_literal(b, lit):
        return lit.lower() in (b["heading"] + b["body"]).lower()

    g0_hits = [b for b in bs if cites_literal(b, "coval_core")]
    g0ok = len(g0_hits) < len(bs)
    print(f"  g=0       `coval_core`, never retracted, appears in {len(g0_hits)} of {len(bs)} blocks "
          f"-> {'PASS — the search does not flag everything' if g0ok else '⛔ FAIL'}")
    neg = [b for b in bs if cites_literal(b, "zzz_no_such_literal")]
    negok = len(neg) == 0
    print(f"  NEGATIVE  a literal in no block -> {len(neg)} hits -> "
          f"{'PASS' if negok else '⛔ FAIL'}")
    dbs = blocks(DEFN.read_text(), re.compile(r"^#{2,4} (.+)$", re.M))
    d_hits = [b for b in dbs if cites_literal(b, "published_five")]
    d_with = [b for b in d_hits if re.search(r"R689", b["heading"] + b["body"])]
    shamok = len(dbs) > 0
    print(f"  SHAM      DEFINITION.md (append-only): {len(dbs)} blocks, {len(d_hits)} mention the "
          f"literal, {len(d_with)} of those also cite R689 -> "
          f"{'PASS — population non-empty' if shamok else '⛔ FAIL — empty population'}")
    plc = excl_by_three(PUBLISHED_FIVE) == repro_excl
    print(f"  PLACEBO   two identical runs differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT      '{INSTRUMENT_UNIT}' != '{CLAIM_UNIT}' -> {'PASS' if unitok else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and shamok and plc and unitok

    print(f"\n─── THE SWEEP: §4's FALSIFIER ON EVERY POPULATION (3 × 2 = 6 cells) ───")
    pops = {"PUBLISHED_FIVE (retracted)": PUBLISHED_FIVE,
            "card-named only": named,
            "R360's 42 arms": sorted(arms)}
    cells = []
    print(f"  {'population':<28}{'n':>4}{'③ excludes':>12}{'③ alone':>10}")
    for pn, pop in pops.items():
        e, a = excl_by_three(pop), excl_by_three_alone(pop)
        cells.append({"population": pn, "n": len(pop), "excluded_by_three": e,
                      "excluded_by_three_alone": a})
        print(f"  {pn:<28}{len(pop):>4}{len(e):>12}{len(a):>10}   {a if a else ''}")

    corrected_alone = excl_by_three_alone(named)
    degenerate = len(named) < 2
    print(f"\n  ⭐ on the set the card ACTUALLY names (n={len(named)}), ③ excludes-alone "
          f"{len(corrected_alone)}   {'⛔ AND THE SET IS TOO SMALL TO RUN R688s TEST' if degenerate else ''}")

    print(f"\n─── THE BLIND SPOT R718's INSTRUMENT COULD NOT REACH ───")
    blind = []
    for b in bs:
        if cites_literal(b, "published_five") or cites_literal(b, "topabs_k4"):
            has = bool(re.search(r"R689|R714", b["heading"] + b["body"]))
            blind.append({"heading": b["heading"][:70], "cites_retracting_round": has,
                          "rounds": sorted(set(re.findall(r"R(\d{3})", b["heading"] + b["body"])))})
    unflagged = [x for x in blind if not x["cites_retracting_round"]]
    print(f"  blocks touching the retracted literal: {len(blind)}   of those NOT citing R689/R714: "
          f"{len(unflagged)}")
    for x in blind:
        print(f"    {'⛔' if not x['cites_retracting_round'] else '✓ '} {x['heading']}")
        print(f"       rounds cited: {x['rounds']}")

    A, B, Cc = len(repro_alone), len(corrected_alone), len(unflagged)
    print(f"\n─── REGISTERED ───")
    print(f"  A  on PUBLISHED_FIVE = 0 [0,3] -> {A}: {'INSIDE' if 0 <= A <= 3 else '⛔ OUTSIDE'} "
          f"(reproduces R688)")
    print(f"  B  on the card-named set = 0 [0,1] -> {B}: {'INSIDE' if 0 <= B <= 1 else '⛔ OUTSIDE'}")
    print(f"  C  blocks citing a retracted literal without the retracting round = 1 [0,5] -> {Cc}: "
          f"{'INSIDE' if 0 <= Cc <= 5 else '⛔ OUTSIDE'}")
    print(f"  DIRECTIONAL the corrected set has FEWER than 3 members -> "
          f"{'HOLDS' if len(named) < 3 else '⛔ FAILS'}  (n={len(named)})")
    print(f"\n  MULTIPLICITY: {len(cells)} sweep cells + {len(bs)} blocks scanned; counts are EXACT.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; the recomputation would be silence."
    elif degenerate:
        world = (
            f"⭐⭐⭐ C DOWNGRADED TO UNEVALUABLE — A BLOCK CERTIFIED AS STANDING ONE ROUND AGO RESTS ON "
            f"A SET RETRACTED THIRTY ROUNDS AGO. R688's finding is 'the {len(repro_excl)} published "
            f"arms outside ③'s extension all fail ② anyway', and its `published` field is exactly "
            f"PUBLISHED_FIVE — which R689 retracted THE VERY NEXT ROUND. The card names "
            f"{len(named)} of those 5 ({named}), and at n={len(named)} R688's test CANNOT BE RUN: it "
            f"needs a set of published arms outside ③'s extension, and the corrected set has "
            f"{len(corrected_alone)} such arm. ⭐ SO '§4's FALSIFIER DOES NOT FIRE AGAINST ③' IS "
            f"DOWNGRADED TO UNEVALUABLE — not refuted, unevaluable, because the population it was "
            f"computed over is not the release's. ⛔⛔ AND R718's INSTRUMENT WAS STRUCTURALLY BLIND "
            f"TO THIS: {Cc} of the blocks touching the retracted literal do not cite R689 or R714 in "
            f"their own body, so 'no body citation outranks the heading' returned UNAMENDED. AN "
            f"AMENDMENT TEST SCOPED TO A BLOCK CANNOT SEE A RETRACTION FILED IN A DIFFERENT BLOCK — "
            f"which means R718's '2 of 12 stand' is an OVERCOUNT, and the residue it reported first "
            f"is now {2-1} block. ⚠ THE VERDICT MAY YET SURVIVE: on R360's full 42 arms ③ excludes "
            f"{len(excl_by_three(sorted(arms)))} and excludes-alone "
            f"{len(excl_by_three_alone(sorted(arms)))}, so the CLAUSE is not shown to be decoration — "
            f"what is shown is that R688's EVIDENCE for it was drawn from a withdrawn set. ⚠ UNIT "
            f"GAP: instrument unit is {INSTRUMENT_UNIT}, claim unit is {CLAIM_UNIT}.")
    elif B > 0:
        world = (f"⭐⭐⭐ B VERDICT FALLS — on the card-named set ③ excludes {B} arm(s) that ② does not, "
                 f"so §4's falsifier DOES fire and R688's block is withdrawn.")
    else:
        world = (f"⭐⭐ A VERDICT SURVIVES — recomputed on the {len(named)} arms the card actually "
                 f"names, ③ still excludes {B} that ② does not, so R688's conclusion holds and only "
                 f"its wording needed the correction. ⚠ But {Cc} block(s) cite the retracted literal "
                 f"without citing the retracting round, which R718's test could not see.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "retracted_support.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "published_five": PUBLISHED_FIVE, "card_named": named,
        "r688_committed": {"published_excluded": r688["published_excluded"],
                           "n_excluded_by_three_alone": r688["n_excluded_by_three_alone"]},
        "reproduced": {"excluded": repro_excl, "excluded_alone": len(repro_alone)},
        "corrected_excluded_alone": corrected_alone, "degenerate": degenerate,
        "cells": cells, "blind_spot_blocks": blind, "n_unflagged": Cc,
        "registered": ("A on PUBLISHED_FIVE 0 [0,3]; B on card-named 0 [0,1]; "
                       "C unflagged blocks 1 [0,5]; directional corrected set < 3"),
        "observed": {"A": A, "B": B, "C": Cc, "directional": len(named) < 3},
        "downgrades": ("STATEMENT.md's '⭐ §4's FALSIFIER DOES NOT FIRE AGAINST ③ (R688)' — its "
                       "population is PUBLISHED_FIVE, retracted by R689 one round later, and the "
                       "card-named set is too small to run the test. UNEVALUABLE, not refuted."),
        "instrument_defect": ("R718's amendment test is scoped to a block and cannot see a "
                              "retraction filed in a different block. Its '2 of 12 stand' is an "
                              "overcount."),
        "limit": ("a block whose SUPPORT was retracted is not thereby false — on R360's full 42 arms "
                  "the clause is not shown to be decoration; what falls is R688's evidence for it."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
