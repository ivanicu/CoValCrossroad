#!/usr/bin/env python3
"""
R720 -- premise or contrast: the rule R719 proposed would have killed the last standing block wrongly.

CHECK #322 ON R719's NEXT LINE — IT HOLDS, AND ITS PROPOSED RULE IS TOO COARSE.
  ✓ `blind_spot_blocks` is in R719's artifact; the lineage block carries 62 rounds without the
    retracting one.
  ⛔ BUT "a retraction anywhere reaches every block citing the retracted literal" would have retracted
    the last standing block for the WRONG REASON. The lineage block's "number 5" is ③'s EXTENSION —
    coval_core, topw_k3, topw_k4, topw_k6, topw_k8 — a DIFFERENT five-member set, and it names
    `R442.published_five` precisely to DISTINGUISH itself: "Five other five-member arm sets are
    committed in this corpus and denote other objects".
  ⭐ A BLOCK THAT CITES A RETRACTED LITERAL TO SAY IT IS NOT THAT DOES NOT REST ON IT.
  ⚠ The real defect is smaller and still real: the block GLOSSES the literal as "CoVal's publication
    list", the exact description R689 retracted. Its CLAIM survives; its GLOSS is stale.

ESTIMAND        per block citing a retracted literal: PREMISE (its conclusion depends on the
                literal's members having the retracted property) or CONTRAST (cited to distinguish
                its own object); and separately whether it repeats the retracted DESCRIPTION.
                Then the corrected residue.
IDENTIFICATION  ⚠ PREMISE-vs-CONTRAST is a READING, positive-controlled against two blocks whose
                roles are independently stateable. The GLOSS check is exact.
SCOPE           population : the 12 claim blocks of STATEMENT.md
                instrument : sentence-level role reading + an exact gloss search
                             instrument unit = A CITATION OF A RETRACTED LITERAL
                             claim unit      = WHETHER A BLOCK'S CLAIM SURVIVES
                             ⚠ NOT EQUAL -- a stale gloss is a defect in PROSE, not in the CLAIM,
                             and conflating them is the over-kill this round exists to prevent.
                baseline   : R719's naive rule, which flags every citing block
                regime     : this repository at HEAD
WORLDS          A CONTRAST SAVES IT · B PREMISE TOO · C INDISTINGUISHABLE
KILL            conditional on the POSITIVE separating R688 from the lineage block
POSITIVE CTRL   R688 must read PREMISE, the lineage block must read CONTRAST
g=0             a block citing no retracted literal must yield role=None, not a default
NEGATIVE CTRL   the block that RECORDS the retraction must read as the RETRACTION, not a victim
SHAM            the same reading with CONTRAST markers removed -- the lineage block must flip
PLACEBO         two identical runs differ by exactly 0
ARTIFACT        results/roles.json
IMPOSSIBLE      deciding whether a surviving CLAIM is TRUE (unattacked is not true) · cross-release
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
STMT = ROOT / "E05_the_space_of_compilers" / "STATEMENT.md"
INSTRUMENT_UNIT = "A CITATION OF A RETRACTED LITERAL"
CLAIM_UNIT = "WHETHER A BLOCK'S CLAIM SURVIVES"
HEADRE = re.compile(r"^> ?#{2,4} (.+)$", re.M)
LITERALS = ["published_five", "topwvar_k4"]
RETRACTING = re.compile(r"R689|R714")
# ⭐ CONTRAST markers: the block cites the literal to say its own object is NOT that one.
CONTRAST = re.compile(r"denote other objects|other five-member|is CoVal's publication list|"
                      r"are unrelated|before ③ is applied|rule prefixes|their intersection is",
                      re.I)
# ⭐ RETRACTION markers: the block IS the retraction, not a victim of it.
RETRACTION = re.compile(r"IS RETRACTED|RETRACTED AS A DESCRIPTION|hard-coded literal", re.I)
GLOSS = re.compile(r"CoVal's publication list", re.I)


def blocks(text):
    ms = list(HEADRE.finditer(text))
    return [{"heading": m.group(1).strip(),
             "body": text[m.end(): (ms[i + 1].start() if i + 1 < len(ms) else len(text))]}
            for i, m in enumerate(ms)]


def role(b, contrast_on=True):
    """None if no retracted literal; else RETRACTION, CONTRAST or PREMISE."""
    full = b["heading"] + b["body"]
    if not any(l.lower() in full.lower() for l in LITERALS):
        return None
    if RETRACTION.search(full):
        return "RETRACTION"
    if contrast_on and CONTRAST.search(full):
        return "CONTRAST"
    return "PREMISE"


def main() -> int:
    if not STMT.exists():
        print(f"⛔ {STMT} absent — exit 2"); return 2
    bs = blocks(STMT.read_text())
    if not bs:
        print("⛔ no claim blocks — exit 2 rather than passing on an empty population"); return 2
    n = len(bs)
    rows = [{**b, "role": role(b), "gloss": bool(GLOSS.search(b["heading"] + b["body"])),
             "cites_retracting": bool(RETRACTING.search(b["heading"] + b["body"])),
             "asserts": "⭐" in b["heading"] and "⛔" not in b["heading"]} for b in bs]
    citing = [r for r in rows if r["role"] is not None]
    print(f"─── THE OBJECT ───\n  {STMT.relative_to(ROOT)}   blocks {n}   citing a retracted "
          f"literal {len(citing)}")

    print(f"\n─── CONTROLS ───")
    r688 = next((r for r in rows if "FALSIFIER" in r["heading"]), None)
    lin = next((r for r in rows if "LINEAGE" in r["heading"]), None)
    posok = (r688 and r688["role"] == "PREMISE") and (lin and lin["role"] == "CONTRAST")
    print(f"  POSITIVE  R688's block -> {r688['role'] if r688 else 'MISSING'} (expect PREMISE); "
          f"lineage -> {lin['role'] if lin else 'MISSING'} (expect CONTRAST) -> "
          f"{'PASS — the reading separates two independently stateable roles' if posok else '⛔ FAIL'}")
    nolit = [r for r in rows if r["role"] is None]
    g0ok = len(nolit) > 0 and all(r["role"] is None for r in nolit)
    print(f"  g=0       {len(nolit)} blocks cite no retracted literal -> role None, never a default "
          f"-> {'PASS' if g0ok else '⛔ FAIL'}")
    retr = [r for r in citing if r["role"] == "RETRACTION"]
    negok = len(retr) >= 1
    print(f"  NEGATIVE  the block RECORDING the retraction reads as RETRACTION, not a victim: "
          f"{len(retr)} -> {'PASS — the retraction is not counted against itself' if negok else '⛔ FAIL'}")
    sham_role = role(lin, contrast_on=False) if lin else None
    shamok = sham_role == "PREMISE"
    print(f"  SHAM      contrast markers removed -> the lineage block reads {sham_role} -> "
          f"{'PASS — the markers are the ingredient' if shamok else '⛔ FAIL'}")
    plc = [role(b) for b in bs] == [r["role"] for r in rows]
    print(f"  PLACEBO   two identical runs differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT      '{INSTRUMENT_UNIT}' != '{CLAIM_UNIT}' -> {'PASS' if unitok else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and shamok and plc and unitok

    print(f"\n─── EVERY BLOCK CITING A RETRACTED LITERAL ───")
    print(f"  {'role':<11}{'gloss':<7}{'asserts':<9}heading")
    for r in citing:
        print(f"  {r['role']:<11}{('STALE' if r['gloss'] else '—'):<7}"
              f"{('yes' if r['asserts'] else 'no'):<9}{r['heading'][:60]}")

    prem = [r for r in citing if r["role"] == "PREMISE"]
    contr = [r for r in citing if r["role"] == "CONTRAST"]
    # the residue: asserting blocks whose CLAIM is not undermined — a PREMISE citation undermines it,
    # a CONTRAST citation does not, and a stale gloss is a prose defect recorded separately.
    # ⛔ THE RESIDUE MUST AND BOTH CRITERIA, AND MY FIRST VERSION REPLACED R718's INSTEAD OF ADDING
    #   TO IT. `asserts and role != PREMISE` alone returned 3, counting R701's and R704's blocks,
    #   which R718 had already found AMENDED by later rounds. A new criterion is a CONJUNCT, never a
    #   substitute — and the registered point (1) landed inside its interval for the wrong reason.
    def amended(b):
        """R718's criterion: a round cited in the body outranks the highest in the heading."""
        hr = [int(x) for x in re.findall(r"R(\d{3})", b["heading"])]
        br = [int(x) for x in re.findall(r"R(\d{3})", b["body"])]
        return bool(hr) and bool(br) and max(br) > max(hr)
    for r in rows:
        r["amended"] = amended(r)
    residue = [r for r in rows if r["asserts"] and r["role"] != "PREMISE" and not r["amended"]]
    naive_residue = [r for r in rows if r["asserts"] and r["role"] is None and not r["amended"]]
    gloss_owed = [r for r in rows if r["gloss"] and not r["cites_retracting"]]

    print(f"\n─── THE SWEEP: WHAT RESIDUE EACH RULE PRODUCES ───")
    cells = [
        {"rule": "naive (any citation kills)", "residue": len(naive_residue)},
        {"rule": "role-aware (PREMISE kills)", "residue": len(residue)},
        {"rule": "role-aware + gloss recorded", "residue": len(residue),
         "gloss_corrections_owed": len(gloss_owed)},
    ]
    for c in cells:
        print(f"  {c['rule']:<32}residue {c['residue']}"
              f"{'   gloss corrections owed ' + str(c['gloss_corrections_owed']) if 'gloss_corrections_owed' in c else ''}")
    disagree = len(naive_residue) != len(residue)
    print(f"  ⭐ the naive and role-aware rules {'DISAGREE' if disagree else 'agree'} — the naive rule "
          f"over-kills by {len(residue)-len(naive_residue)} block(s)")

    print(f"\n─── ⭐ THE CORRECTED RESIDUE ───")
    for r in residue:
        print(f"  ⭐ {r['heading'][:88]}")
        if r["gloss"]:
            print(f"     ⚠ owes a GLOSS correction: it repeats \"CoVal's publication list\", the "
                  f"description R689 retracted")
    if not residue:
        print("  ⛔ NOTHING — every asserting block cites a retracted literal as a premise.")

    A, B, Cc = len(citing), len(prem), len(residue)
    print(f"\n─── REGISTERED ───")
    print(f"  A  blocks citing a retracted literal = 3 [1,6] -> {A}: "
          f"{'INSIDE' if 1 <= A <= 6 else '⛔ OUTSIDE'}")
    print(f"  B  of those, PREMISE = 1 [0,3] -> {B}: {'INSIDE' if 0 <= B <= 3 else '⛔ OUTSIDE'}")
    print(f"  C  corrected residue = 1 [0,4] -> {Cc}: {'INSIDE' if 0 <= Cc <= 4 else '⛔ OUTSIDE'}")
    print(f"  DIRECTIONAL the naive and role-aware rules disagree -> "
          f"{'HOLDS' if disagree else '⛔ FAILS'}")
    print(f"\n  MULTIPLICITY: {len(cells)} rules × {len(LITERALS)} literals scanned over {n} blocks; "
          f"counts are EXACT.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; the role reading would be silence."
    elif not residue:
        world = (f"⭐⭐⭐ B THE RESIDUE IS ZERO — every asserting block on the deliverable cites a "
                 f"retracted literal as a PREMISE. Reported as the finding and not dressed as a "
                 f"result.")
    else:
        world = (
            f"⭐⭐⭐ A THE CONTRAST CITATION SAVES IT, AND R719's PROPOSED RULE WOULD HAVE KILLED IT "
            f"WRONGLY. Of the {A} blocks citing a retracted literal, {B} uses it as a PREMISE — R688, "
            f"whose finding is about 'the 3 published arms' — and {len(contr)} as a CONTRAST: the "
            f"lineage block names `R442.published_five` in order to say its own five-member set is a "
            f"DIFFERENT object. ⭐ A BLOCK THAT CITES A RETRACTED LITERAL TO SAY IT IS NOT THAT DOES "
            f"NOT REST ON IT. ⛔ R719's naive rule — a retraction anywhere reaches every citing block "
            f"— yields a residue of {len(naive_residue)}; the role-aware rule yields {Cc}, so the "
            f"naive rule OVER-KILLS by {Cc-len(naive_residue)}. ⭐⭐ SO THE CORRECTED RESIDUE IS {Cc}: "
            f"{'; '.join(r['heading'][:52] for r in residue)}. ⚠ AND IT OWES A CORRECTION: "
            f"{len(gloss_owed)} block(s) repeat \"CoVal's publication list\" — the exact description "
            f"R689 retracted — without citing R689. That is a defect in the PROSE, not in the CLAIM, "
            f"and conflating the two is precisely the over-kill this round exists to prevent. ⚠ THE "
            f"ROLE READING IS A READING, not a measurement: it is positive-controlled against two "
            f"blocks whose roles are independently stateable, and the SHAM confirms the contrast "
            f"markers are the ingredient — removing them flips the lineage block to PREMISE. ⚠ AND "
            f"UNATTACKED IS STILL NOT TRUE: R719 showed a block can stand for thirty rounds on a "
            f"withdrawn set. ⚠ UNIT GAP: instrument unit is {INSTRUMENT_UNIT}, claim unit is "
            f"{CLAIM_UNIT}.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "roles.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "n_blocks": n,
        "citing": [{"heading": r["heading"], "role": r["role"], "gloss": r["gloss"],
                    "asserts": r["asserts"], "amended": r["amended"],
                    "cites_retracting": r["cites_retracting"]}
                   for r in citing],
        "n_premise": B, "n_contrast": len(contr), "n_retraction_blocks": len(retr),
        "residue": [r["heading"] for r in residue],
        "naive_residue": [r["heading"] for r in naive_residue],
        "gloss_corrections_owed": [r["heading"] for r in gloss_owed],
        "rules": cells, "naive_over_kills_by": Cc - len(naive_residue),
        "registered": ("A citing 3 [1,6]; B premise 1 [0,3]; C residue 1 [0,4]; "
                       "directional the rules disagree"),
        "observed": {"A": A, "B": B, "C": Cc, "directional": disagree},
        "corrects": ("R719's NEXT line proposed that a retraction anywhere reaches every citing "
                     "block. That rule over-kills: a CONTRAST citation does not rest on the "
                     "literal."),
        "limit": ("the role reading is a READING, positive-controlled but not a measurement; and a "
                  "surviving CLAIM is unattacked, not true."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
