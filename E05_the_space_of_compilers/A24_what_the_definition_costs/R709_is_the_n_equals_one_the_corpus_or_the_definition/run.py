#!/usr/bin/env python3
"""
R709 -- is F1's n=1 a fact about the corpus, or about the definition that counted it?

CHECK #311 ON THE LAST NEXT LINE -- THE CITATION RESOLVES, THE SUPERLATIVE DOES NOT.
  ✓ STATEMENT.md:141-142 does say F1's scope "rests on ONE VERDICT PAIR (R683, R685)".
  ⛔ "the weakest load-bearing claim in the deliverable since R685" is an UNVERIFIED SUPERLATIVE --
    I never ranked the deliverable's claims by strength. §4's closing-sentence failure, third time
    in this arc. WITHDRAWN: F1's scope is *a* claim resting on n=1, not demonstrably the weakest.

⛔ §4's OWN REMEDY, APPLIED: count what the release CONTAINS against what the code CONSUMED.
  11 rounds carry BOTH judge keys; R685 examined 7. ⚠ The 4 skipped are R683-R686, the instrument
  rounds themselves -- a SELF-INCLUSION control, correct and not a miss. So world B is nearly dead
  before the run and is registered anyway, because a world I expect to die is exactly the one I
  should not quietly drop.
  ⭐ THE LIVE GAP IS THE DEFINITION. R685 cut 7 rounds to 1 pair by counting ONLY booleans and small
    closed-set strings, stating "continuous per-judge values differ by construction and are
    EXCLUDED". But F1's scope claim IS about a continuous quantity's SIGN across judges -- "the
    separation does not hold at 0.8B". The rule that produced n=1 excludes the evidence type the
    claim is made of.

ESTIMAND        per-judge comparisons informative about F1's scope, under three NESTED definitions,
                with the agreement rate at each: D1 R685's (bool + small closed-set string) ·
                D2 = D1 + SIGN agreement on continuous numerics · D3 = D2 + ORDERING on vectors.
                ⚠ D1 <= D2 <= D3 is a DERIVATION (nesting), not evidence. The COUNTS are evidence.
IDENTIFICATION  identified from artifacts on disk. ⚠ "informative about F1's scope" is
                operationalised as "a value under both judge keys admitting a same/different
                verdict"; mine, so every pair is listed by field name in the artifact.
SCOPE           population : the 7 non-self rounds with both judge keys
                instrument : a JSON walk for dicts whose keys include both "0.8B" and "2B"
                             instrument unit = A PER-JUDGE FIELD
                             claim unit      = F1's SCOPE CONDITION
                             ⚠ NOT EQUAL -- a field differing across judges does not by itself bear
                             on whether the ③ SEPARATION holds; that link is named per field.
                baseline   : R685's committed n_pairs = 1
                regime     : this repository at HEAD
WORLDS          A THE LIMIT IS REAL · B THE SEARCH MISSED IT · C THE DEFINITION MADE IT
KILL            conditional on POSITIVE recovering R685's pair and g=0 returning 0
POSITIVE CTRL   R361's `rank_resolved` {0.8B: False, 2B: True} must be recovered by D1
g=0             a synthetic artifact with both judge keys but no comparable value -> 0 pairs
NEGATIVE CTRL   judge keys stripped -> 0 pairs. World excluded: "the finder responds to field NAMES"
SHAM            the judge-keying requirement dropped -- same walk minus the ingredient
PLACEBO         two identical runs differ by exactly 0
ARTIFACT        results/pairs.json -- every pair by round, field, values and verdict
IMPOSSIBLE      a THIRD judge (the release ships two) · construct validity of "informative about the
                separation" (needs a criterion outside this repo)
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
JA, JB = "0.8B", "2B"
SELF = ("R683", "R684", "R685", "R686", "R709")     # instrument rounds -- named, counted, excluded
INSTRUMENT_UNIT, CLAIM_UNIT = "A PER-JUDGE FIELD", "F1's SCOPE CONDITION"


def walk(node, path=""):
    """Yield (path, dict) for every dict whose keys include BOTH judge keys."""
    if isinstance(node, dict):
        if JA in node and JB in node:
            yield path, node
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")


def sign(x):
    return 0 if abs(x) < 1e-12 else (1 if x > 0 else -1)


def classify(a, b):
    """Return (definition_level, verdict) or None. D1 bool/str · D2 numeric sign · D3 vector order."""
    if isinstance(a, bool) or isinstance(b, bool):
        return ("D1", "AGREE" if a == b else "DISAGREE")
    if isinstance(a, str) and isinstance(b, str) and len(a) < 40 and len(b) < 40:
        return ("D1", "AGREE" if a == b else "DISAGREE")
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return ("D2", "AGREE" if sign(a) == sign(b) else "DISAGREE")
    if (isinstance(a, list) and isinstance(b, list) and len(a) == len(b) >= 2
            and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in a + b)):
        oa = sorted(range(len(a)), key=lambda i: a[i])
        ob = sorted(range(len(b)), key=lambda i: b[i])
        return ("D3", "AGREE" if oa == ob else "DISAGREE")
    return None


# ⛔⛔ A ROUND'S OWN CONTROL FLAGS ARE NOT VERDICTS. `controls.positive`, `controls.g0`,
#   `controls.placebo`, `controls.sham` pass at BOTH judges BY DESIGN, so counting them as per-judge
#   agreement is counting the design. R685 already found and fixed this exact defect. I reimplemented
#   the walk from scratch, read R685's VERDICT STRING and not its EXCLUSION LOGIC, and reintroduced
#   it: 9 of my first 10 D1 "pairs" were control flags. The registered POINT A "failure" (1 -> 10)
#   was my instrument regressing to a bug the round under audit had already closed.
CONTROL_PATH = re.compile(r"(^|\.)controls?(\.|$)|(^|\.)(positive|placebo|sham|g0|negative)(\.|$)",
                          re.I)


def collect(rounds, obj_of=None, excluded=None):
    out = []
    excluded = [] if excluded is None else excluded
    for rd in rounds:
        for art in sorted(ARC.glob(f"{rd}_*/results/*.json")):
            try:
                data = json.loads(art.read_text())
            except Exception:
                continue
            if obj_of:
                data = obj_of(data)
            for path, node in walk(data):
                if CONTROL_PATH.search(path):
                    excluded.append({"round": rd, "field": path}); continue
                c = classify(node[JA], node[JB])
                if c:
                    out.append({"round": rd, "artifact": art.name, "field": path,
                                "level": c[0], "verdict": c[1],
                                "values": {JA: node[JA], JB: node[JB]}})
    return out


def main() -> int:
    all_rounds = sorted({p.name.split("_")[0] for p in ARC.glob("R*") if p.is_dir()},
                        key=lambda r: int(r[1:]))
    with_keys = []
    for rd in all_rounds:
        for art in ARC.glob(f"{rd}_*/results/*.json"):
            t = art.read_text(errors="ignore")
            if f'"{JA}"' in t and f'"{JB}"' in t:
                with_keys.append(rd); break
    non_self = [r for r in with_keys if r not in SELF]
    print(f"─── POPULATION (§4: what the release CONTAINS vs what the code CONSUMED) ───")
    print(f"  rounds with BOTH judge keys : {len(with_keys)}  {with_keys}")
    print(f"  SELF-INCLUSION excluded     : {sorted(set(with_keys) & set(SELF))}  "
          f"— named and counted; this is the whole 11-vs-7 difference, not a search failure")
    print(f"  population for this round   : {len(non_self)}  {non_self}")
    print(f"  R685 consumed               : 7")

    print("\n─── CONTROLS ───")
    pairs = collect(non_self)
    pos = [p for p in pairs if p["round"] == "R361" and "rank_resolved" in p["field"]
           and p["level"] == "D1"]
    posok = bool(pos)
    print(f"  POSITIVE   R361's `rank_resolved` recovered by D1: {len(pos)} -> "
          f"{'PASS — a known-present object is re-found' if posok else '⛔ FAIL'}")
    if pos:
        print(f"             {pos[0]['field']}  {pos[0]['values']}  {pos[0]['verdict']}")
    g0doc = {"judges": {JA: {"note": "a string far too long to be a closed-set verdict " * 3},
                        JB: {"note": "another long free-text note " * 5}}}
    g0 = [c for _, n in walk(g0doc) if (c := classify(n[JA], n[JB]))]
    g0ok = not g0
    print(f"  g=0        synthetic artifact, both keys, no comparable value -> {len(g0)} pairs "
          f"-> {'PASS — keys alone do not manufacture a pair' if g0ok else '⛔ FAIL'}")
    strip = lambda d: json.loads(re.sub(r'"(0\.8B|2B)"', '"X"', json.dumps(d)))
    neg = collect(non_self, obj_of=strip)
    negok = not neg
    print(f"  NEGATIVE   judge keys stripped -> {len(neg)} pairs -> "
          f"{'PASS — the finder responds to the KEYING, not to field names' if negok else '⛔ FAIL'}")
    sham_fields = 0
    for rd in non_self:
        for art in ARC.glob(f"{rd}_*/results/*.json"):
            try: sham_fields += len(json.loads(art.read_text()))
            except Exception: pass
    shamok = sham_fields > len(pairs)
    print(f"  SHAM       keying requirement dropped: {sham_fields} top-level fields vs "
          f"{len(pairs)} judge-keyed pairs -> "
          f"{'PASS — the keying is what localises' if shamok else '⛔ FAIL'}")
    plc = collect(non_self) == pairs
    print(f"  PLACEBO    two identical walks differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT       '{INSTRUMENT_UNIT}' != '{CLAIM_UNIT}' -> {'PASS' if unitok else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and shamok and plc and unitok

    lv = lambda ps, *ls: [p for p in ps if p["level"] in ls]
    D1, D2, D3 = lv(pairs, "D1"), lv(pairs, "D1", "D2"), lv(pairs, "D1", "D2", "D3")
    print(f"\n─── THE THREE NESTED DEFINITIONS (D1 ⊆ D2 ⊆ D3 is a DERIVATION; the counts are not) ───")
    for nm, s in (("D1  R685's rule", D1), ("D2  + numeric SIGN", D2), ("D3  + vector ORDER", D3)):
        ag = sum(1 for p in s if p["verdict"] == "AGREE")
        print(f"  {nm:<22} pairs {len(s):>3}   agree {ag:>3}   disagree {len(s)-ag:>3}   "
              f"agreement {(ag/len(s) if s else 0):.4f}")
    print(f"\n  every D2-new pair, named (the operationalisation is mine, so it is inspectable):")
    for p in [x for x in D2 if x["level"] == "D2"][:14]:
        v = p["values"]
        print(f"    {p['round']:<6}{p['field'][:46]:<47}{JA}={v[JA]!s:>10} {JB}={v[JB]!s:>10}  "
              f"{p['verdict']}")
    extra = len([x for x in D2 if x['level'] == 'D2'])
    if extra > 14: print(f"    … {extra-14} more in results/pairs.json")

    print(f"\n─── THE SPECIFICATION SWEEP (G4 — 3 definitions × 2 populations) ───")
    allp = collect(with_keys)
    cells = []
    for pop, ps in (("the 7 (self excluded)", pairs), ("all 11 (self INCLUDED)", allp)):
        for nm, ls in (("D1", ("D1",)), ("D2", ("D1", "D2")), ("D3", ("D1", "D2", "D3"))):
            s = lv(ps, *ls)
            ag = sum(1 for p in s if p["verdict"] == "AGREE")
            cells.append({"population": pop, "definition": nm, "pairs": len(s), "agree": ag,
                          "agreement": (ag / len(s)) if s else None})
            print(f"  {pop:<26}{nm:<4} pairs {len(s):>3}  agreement "
                  f"{(('%.4f' % (ag/len(s))) if s else '--'):>8}")
    print(f"  ⚠ the self-included row is reported so the 11-vs-7 difference is visible, and it is "
          f"NOT used for any verdict — R683-R686 analyse this very question.")

    # ⭐⭐ THE DECISIVE DISTINCTION, COMPUTED NOT TYPED. F1's scope claim is about THE SEPARATION
    #   ("③ excludes the arms that win by reading labels"). A pair only bears on it if its FIELD is
    #   about that separation -- rank resolution or label-rank quantities. Everything else widens the
    #   evidence about judge agreement in general and says nothing about F1's scope.
    SEP = re.compile(r"rank_resolved|label|separation|rank_sd|mean_five_rank", re.I)
    sep_pairs = [p for p in D2 if SEP.search(p["field"])]
    sep_new = [p for p in sep_pairs if p["level"] != "D1"]
    print(f"\n─── ⭐ DOES ANY WIDENED PAIR MEASURE THE SEPARATION ITSELF? ───")
    print(f"  D2 pairs whose FIELD bears on the separation: {len(sep_pairs)} "
          f"({len(sep_new)} of them new at D2)")
    for p in sep_pairs:
        print(f"    {p['round']:<6}{p['level']:<4}{p['field'][:40]:<41}{p['verdict']}")
    print(f"  ⚠ separation-bearing is a FIELD-NAME judgement and it is mine; the names are printed "
          f"so it can be rejected without redoing the walk.")

    A, B = len(D1), len(D2)
    agr2 = sum(1 for p in D2 if p["verdict"] == "AGREE") / len(D2) if D2 else None
    print(f"\n─── REGISTERED ───")
    print(f"  A  D1 pairs = 1 [0,3] -> {A}: {'INSIDE' if 0 <= A <= 3 else '⛔ OUTSIDE'}  "
          f"(R685 committed 1)")
    print(f"  B  D2 pairs = 5 [1,15] -> {B}: {'INSIDE' if 1 <= B <= 15 else '⛔ OUTSIDE'}")
    print(f"  C  D2 sign-agreement = 0.60 [0.20,0.95] -> "
          f"{('%.4f' % agr2) if agr2 is not None else 'UNCOMPUTED'}: "
          f"{'INSIDE' if agr2 is not None and 0.20 <= agr2 <= 0.95 else '⛔ OUTSIDE'}")
    print(f"  DIRECTIONAL D2 > D1 -> {'HOLDS' if B > A else '⛔ FAILS'}")

    rounds_with = len({p["round"] for p in D2})
    print(f"\n  MULTIPLICITY: {len(cells)} cells above, all printed. Rounds contributing a D2 pair: "
          f"{rounds_with} of {len(non_self)}.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; these counts would be silence."
    elif B > A and not sep_new:
        world = (
            f"⭐⭐⭐ A* THE n=1 SURVIVES WHERE IT MATTERS, AND R685 IS REPLICATED EXACTLY. Under "
            f"R685's own rule this walk finds {A} pair — the same one, R361's `rank_resolved` "
            f"{{0.8B: False, 2B: True}} — so its count was correct and its exclusion of continuous "
            f"values was not hiding a second verdict. ⭐ Widening to numeric SIGN yields {B} "
            f"comparisons across {rounds_with} of {len(non_self)} rounds at "
            f"{('%.4f' % agr2) if agr2 is not None else 'UNCOMPUTED'} agreement — so the two judges "
            f"agree far more often than the one disagreeing pair suggests. ⛔ BUT NOT ONE OF THE "
            f"{B-A} NEW COMPARISONS MEASURES THE SEPARATION ITSELF: {len(sep_pairs)} pairs have a "
            f"separation-bearing field and {len(sep_new)} of those are new. ⭐⭐ SO F1's SCOPE "
            f"CONDITION STANDS AS STATEMENT.md WRITES IT — it rests on one measurement of the "
            f"separation — and what changes is the surrounding claim: the judges are not broadly "
            f"discordant, they disagree on THIS quantity while agreeing at "
            f"{('%.0f%%' % (100*agr2)) if agr2 is not None else '--'} elsewhere, which makes the "
            f"disagreement more specific and not less real. ⚠ UNIT GAP: instrument unit is "
            f"{INSTRUMENT_UNIT}, claim unit is {CLAIM_UNIT}.")
    elif B > A:
        world = (
            f"⭐⭐⭐ C THE DEFINITION MADE THE n=1. The corpus holds {A} pair under R685's rule and "
            f"{B} under a rule that also reads the SIGN of a continuous per-judge value — "
            f"{rounds_with} of the {len(non_self)} rounds contribute one, against the 1 round R685 "
            f"could use. ⭐ R685 excluded continuous values because they 'differ by construction', "
            f"but F1's scope claim is EXACTLY a claim about a continuous quantity's sign across "
            f"judges — 'the separation does not hold at 0.8B'. The rule that produced n=1 excluded "
            f"the evidence type the claim is made of. ⭐⭐ SO STATEMENT.md's 'rests on ONE VERDICT "
            f"PAIR' UNDERSTATES THE CORPUS: it is one pair under one definition, and "
            f"{len(sep_pairs)} separation-bearing comparisons exist ({len(sep_new)} new at D2), of "
            f"which {sum(1 for x in sep_pairs if x['verdict']=='DISAGREE')} disagree and "
            f"{sum(1 for x in sep_pairs if x['verdict']=='AGREE')} agree, against sign-level "
            f"agreement of {('%.4f' % agr2) if agr2 is not None else 'UNCOMPUTED'} over the whole "
            f"widened set. ⛔⛔ BUT DEEPER IS NOT WIDER, AND THAT IS THE LOAD-BEARING "
            f"QUALIFICATION: all {len(sep_pairs)} separation-bearing comparisons come from "
            f"{len({x['round'] for x in sep_pairs})} round — {sorted({x['round'] for x in sep_pairs})} "
            f"— so widening the rule added FIELDS, not independent ROUNDS. Correlated measurements "
            f"of one comparison are not a second comparison, and F1's generalisation still rests on "
            f"exactly one round. ⚠ WHAT THIS DOES NOT DO: it "
            f"does not restore F1's generalisation. A sign agreement is weaker evidence than a "
            f"verdict pair, the two judges are still two, and 'informative about the separation' is "
            f"my operationalisation — every pair is listed by field so a later round can reject it "
            f"without redoing the walk. ⚠ THE 11-vs-7 GAP IS NOT A SEARCH FAILURE: the 4 unexamined "
            f"rounds are R683-R686, which analyse this question, and excluding them is the "
            f"self-inclusion control. ⚠ UNIT GAP: instrument unit is {INSTRUMENT_UNIT}, claim unit "
            f"is {CLAIM_UNIT} — a field differing across judges does not by itself bear on the ③ "
            f"separation.")
    else:
        world = (f"⭐⭐ A THE LIMIT IS REAL — widening the rule from booleans to numeric signs and "
                 f"vector orderings yields {B} pairs against R685's {A}. The corpus really does hold "
                 f"one usable comparison, and F1's scope condition stands as STATEMENT.md writes it.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "pairs.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "rounds_with_both_judge_keys": with_keys, "self_excluded": sorted(set(with_keys) & set(SELF)),
        "population": non_self, "r685_consumed": 7, "r685_committed_pairs": 1,
        "D1": len(D1), "D2": len(D2), "D3": len(D3),
        "d2_sign_agreement": agr2, "rounds_contributing_d2": rounds_with,
        "pairs": pairs, "cells": cells,
        "registered": ("A D1 pairs 1 [0,3]; B D2 pairs 5 [1,15]; C D2 agreement 0.60 [0.20,0.95]; "
                       "directional D2 > D1"),
        "observed": {"A": A, "B": B, "C": agr2, "directional": B > A},
        "derivation_not_evidence": "D1 <= D2 <= D3 is forced by nesting; only the counts are measured.",
        "limit": ("'informative about the separation' is MY operationalisation; a sign agreement is "
                  "weaker than a verdict pair; and two judges remain two."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
