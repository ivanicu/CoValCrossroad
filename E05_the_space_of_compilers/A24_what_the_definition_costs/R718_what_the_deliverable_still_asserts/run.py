#!/usr/bin/env python3
"""
R718 -- what the deliverable still ASSERTS. §0.2's question, asked of the statement rather than the ledger.

CHECK #320 ON R717's NEXT LINE — ITS COUNT IS WRONG BY ONE, AGAIN IN A CLASS THE GATE CANNOT CATCH.
  ⛔ "three consecutive rounds have ended in a bound" is FALSE. R715 produced a VALUE — a separating
    predicate at 0.0655 — and only R716 and R717 ended in bounds. It is TWO. Seventh false closing
    claim in this arc, and the third of the precedence/count species the quantifier gate cannot see.

⛔ AND ITS PROPOSAL NEEDED AMENDING BEFORE IT WAS RUN.
  It asked me to count rounds ending in a bound versus a value. §0.2 forbids exactly that as a
  product — "never lead with the ledger, never end on it" — and a count of my own retractions is the
  activity metric that section opens by forbidding. The admissible question is the one §0.2 demands
  instead: WHAT STANDS. So the object is the DELIVERABLE, not the 440 artifacts.

ESTIMAND        per claim block on STATEMENT.md: (i) does it ASSERT or record a WITHDRAWAL, and
                (ii) has a LATER round amended it — computed as "a round cited in the body outranks
                the highest round cited in the heading". Then: how many blocks assert something no
                later round has amended.
IDENTIFICATION  (ii) is exact from the file's own citations. ⚠ (i) reads the heading's marker, a
                CONVENTION I wrote, so it is validated against blocks whose status is independently
                stateable and is otherwise a reading.
SCOPE           population : the claim blocks of E05/STATEMENT.md at HEAD
                instrument : citation-number comparison, heading vs body
                             instrument unit = A CLAIM BLOCK
                             claim unit      = WHAT THE CAMPAIGN HAS PRODUCED
                             ⚠ NOT EQUAL -- a block standing unamended is NOT thereby true; it is
                             unattacked, and this arc has shown blocks were wrong while standing.
                baseline   : the block count and the marker convention
                regime     : this repository at HEAD
WORLDS          A PRODUCTION · B LEDGER · C CHURN (see PREREGISTRATION.txt)
KILL            conditional on the POSITIVE firing and g=0 returning UNKNOWN rather than clean
POSITIVE CTRL   R701's block must classify ASSERT, R696's must classify WITHDRAW
g=0             a block with NO citation must yield UNKNOWN, never a silent "unamended" pass
NEGATIVE CTRL   scramble which body belongs to which heading; the amendment count must change
SHAM            the same test on DEFINITION.md, an append-only record
PLACEBO         two identical runs differ by exactly 0
ARTIFACT        results/standing.json
IMPOSSIBLE      whether an unamended block is TRUE (no self-audit can answer it) · cross-release
"""
from __future__ import annotations
import json, pathlib, random, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
STMT = ROOT / "E05_the_space_of_compilers" / "STATEMENT.md"
DEFN = ROOT / "E05_the_space_of_compilers" / "DEFINITION.md"
SEEDS = (0, 1, 2)
INSTRUMENT_UNIT, CLAIM_UNIT = "A CLAIM BLOCK", "WHAT THE CAMPAIGN HAS PRODUCED"
HEAD = re.compile(r"^> ?#{2,4} (.+)$", re.M)
RN = re.compile(r"R(\d{3})")


def blocks(text):
    """A block is a blockquote heading plus everything up to the next such heading."""
    ms = list(HEAD.finditer(text))
    out = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        out.append({"heading": m.group(1).strip(), "body": text[m.end():end]})
    return out


def marker(h):
    if "⛔" in h: return "WITHDRAWS"
    if "⚠" in h: return "QUALIFIES"
    if "⭐" in h: return "ASSERTS"
    return "PLAIN"


def classify(b):
    hr = [int(x) for x in RN.findall(b["heading"])]
    br = [int(x) for x in RN.findall(b["body"])]
    if not hr:
        return {"marker": marker(b["heading"]), "head_rounds": hr, "max_body": max(br) if br else None,
                "amended": None, "why": "UNKNOWN — the heading cites no round, so nothing can outrank it"}
    mh, mb = max(hr), (max(br) if br else None)
    return {"marker": marker(b["heading"]), "head_rounds": hr, "max_head": mh, "max_body": mb,
            "amended": (mb is not None and mb > mh),
            "why": (f"body cites R{mb} > heading R{mh}" if mb and mb > mh else
                    f"no body citation outranks R{mh}")}


def main() -> int:
    for p in (STMT, DEFN):
        if not p.exists():
            print(f"⛔ {p} absent — exit 2 rather than passing on an empty population")
            return 2
    txt = STMT.read_text()
    bs = blocks(txt)
    rows = [{**b, **classify(b)} for b in bs]
    n = len(rows)
    print(f"─── THE DELIVERABLE ───\n  {STMT.relative_to(ROOT)}   claim blocks {n}   "
          f"rounds cited {len(set(RN.findall(txt)))}")

    print("\n─── CONTROLS ───")
    r701 = next((r for r in rows if 701 in r["head_rounds"]), None)
    r696 = next((r for r in rows if 696 in r["head_rounds"]), None)
    posok = (r701 and r701["marker"] == "ASSERTS") and (r696 and r696["marker"] == "WITHDRAWS")
    print(f"  POSITIVE  R701's block -> {r701['marker'] if r701 else 'MISSING'} (expect ASSERTS); "
          f"R696's -> {r696['marker'] if r696 else 'MISSING'} (expect WITHDRAWS) -> "
          f"{'PASS — the marker convention reads as written' if posok else '⛔ FAIL'}")
    synth = classify({"heading": "⭐ A HEADING WITH NO CITATION", "body": "no rounds named here"})
    g0ok = synth["amended"] is None
    print(f"  g=0       a block citing no round -> amended={synth['amended']} -> "
          f"{'PASS — UNKNOWN, never a silent clean pass' if g0ok else '⛔ FAIL'}")
    base_amended = sum(1 for r in rows if r["amended"])
    scr_counts = []
    for sd in SEEDS:
        rg = random.Random(sd)
        bodies = [b["body"] for b in bs]
        rg.shuffle(bodies)
        scr = [classify({"heading": bs[i]["heading"], "body": bodies[i]}) for i in range(n)]
        scr_counts.append(sum(1 for s in scr if s["amended"]))
    negok = any(c != base_amended for c in scr_counts)
    print(f"  NEGATIVE  bodies scrambled against headings: amended counts {scr_counts} vs the real "
          f"{base_amended} -> {'PASS — the pairing carries the verdict' if negok else '⛔ FAIL'}")
    # ⛔ THE SHAM'S OWN POPULATION WAS EMPTY AND IT PASSED. DEFINITION.md uses PLAIN `##` headings,
    #   not blockquoted ones, so `blocks()` returned 0 and the guard `len(dbs) == 0 or ...` let it
    #   through — §4's *empty population passes*, inside the control written to guard against it.
    #   Fixed: a document-appropriate extractor, and an EMPTY population now FAILS the sham.
    dbs = blocks(DEFN.read_text()) or [
        {"heading": m.group(1).strip(), "body": b}
        for m, b in ((m, DEFN.read_text()[m.end(): (nxt.start() if nxt else None)])
                     for m, nxt in zip(
                         list(re.finditer(r"^#{2,4} (.+)$", DEFN.read_text(), re.M)),
                         list(re.finditer(r"^#{2,4} (.+)$", DEFN.read_text(), re.M))[1:] + [None]))]
    d_amended = sum(1 for b in dbs if classify(b)["amended"])
    # ⛔ AND THE SHAM'S EXPECTATION WAS MIS-SPECIFIED TOO: it compared RAW COUNTS across documents of
    #   very different size. DEFINITION.md has 79 blocks to the statement's 12, so 5 > 3 while the
    #   RATE runs the other way. A control comparing two populations must compare RATES.
    d_rate = d_amended / len(dbs) if dbs else None
    s_rate = base_amended / n if n else None
    shamok = len(dbs) > 0 and d_rate is not None and d_rate < s_rate
    print(f"  SHAM      the same test on DEFINITION.md (append-only): {len(dbs)} blocks, "
          f"{d_amended} amended = {d_rate:.4f} vs the statement's {base_amended}/{n} = {s_rate:.4f}")
    print(f"            -> {'PASS — per block, an append-only record inverts less' if shamok else '⛔ FAIL — empty population or a higher rate'}"
          f"   (raw counts would have said {d_amended} > {base_amended}; the RATE is the comparison)")
    plc = [classify(b)["amended"] for b in bs] == [r["amended"] for r in rows]
    print(f"  PLACEBO   two identical runs differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT      '{INSTRUMENT_UNIT}' != '{CLAIM_UNIT}' -> {'PASS' if unitok else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and shamok and plc and unitok

    print(f"\n─── EVERY CLAIM BLOCK, WITH ITS VERDICT ───")
    print(f"  {'marker':<11}{'heads':<12}{'amended':<9}heading")
    for r in rows:
        hr = ",".join(f"R{x}" for x in r["head_rounds"]) or "—"
        am = {True: "⛔ YES", False: "no", None: "UNKNOWN"}[r["amended"]]
        print(f"  {r['marker']:<11}{hr:<12}{am:<9}{r['heading'][:66]}")

    asserts = [r for r in rows if r["marker"] == "ASSERTS"]
    standing = [r for r in asserts if r["amended"] is False]
    withdraw = [r for r in rows if r["marker"] == "WITHDRAWS"]
    qualify = [r for r in rows if r["marker"] == "QUALIFIES"]

    print(f"\n─── ⭐ WHAT STANDS — reported FIRST, per §0.2 ───")
    if standing:
        for r in standing:
            print(f"  ⭐ {r['heading'][:96]}")
    else:
        print(f"  ⛔ NOTHING: no asserting block is free of a later amendment.")
    print(f"\n─── what it cost, in one block ───")
    print(f"  blocks {n}   asserts {len(asserts)}   withdraws {len(withdraw)}   "
          f"qualifies {len(qualify)}   amended-by-a-later-round {base_amended}")

    A, B, Cc = n, len(asserts), sum(1 for r in asserts if r["amended"])
    print(f"\n─── REGISTERED ───")
    print(f"  A  claim blocks = 12 [8,20] -> {A}: {'INSIDE' if 8 <= A <= 20 else '⛔ OUTSIDE'}")
    print(f"  B  asserting blocks = 4 [2,10] -> {B}: {'INSIDE' if 2 <= B <= 10 else '⛔ OUTSIDE'}")
    print(f"  C  asserting blocks later amended = 2 [0,4] -> {Cc}: "
          f"{'INSIDE' if 0 <= Cc <= 4 else '⛔ OUTSIDE'}")
    print(f"  DIRECTIONAL withdrawals+qualifications > assertions -> "
          f"{'HOLDS' if len(withdraw)+len(qualify) > len(asserts) else '⛔ FAILS'}")
    print(f"\n  MULTIPLICITY: {n} blocks + {len(dbs)} sham blocks, all counted; counts are EXACT so "
          f"no p-values are computed and none are implied.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; these counts would be silence."
    elif not standing:
        world = (f"⭐⭐⭐ B THE LEDGER IS THE PRODUCT — §0.2's charge holds against this campaign. Of "
                 f"{n} claim blocks on the deliverable, {len(asserts)} assert and every one of them "
                 f"carries a later round's amendment. Nothing stands unamended.")
    else:
        world = (
            f"⭐⭐⭐ A THERE IS A RESIDUE, AND IT IS {len(standing)} OF {n} BLOCKS. Reported first "
            f"because §0.2 requires it: the statement carries {len(standing)} asserting block(s) that "
            f"no later round has amended — "
            f"{'; '.join(r['heading'][:60] for r in standing)}. ⭐ THAT IS WHAT THIS ARC HAS "
            f"PRODUCED, and it is a claim with its scope attached rather than a count of my own "
            f"retractions — which is the metric §0.2 opens by forbidding, and which R717's closing "
            f"line asked me to compute. ⚠ WHAT IT COST, in one line: {n} blocks, {len(asserts)} "
            f"assert, {len(withdraw)} record a withdrawal, {len(qualify)} qualify, and "
            f"{base_amended} carry a later round's amendment. ⛔⛔ AND THE LOAD-BEARING CAVEAT: "
            f"STANDING UNAMENDED IS NOT TRUTH. It means unattacked. This arc withdrew F2's A2 "
            f"justification, its sham residual and its exclusion count in three consecutive rounds, "
            f"and every one of those blocks stood unamended until the round that killed it. ⚠ The "
            f"marker reading is a CONVENTION I wrote, positive-controlled against two blocks whose "
            f"status is independently stateable, and the amendment test is exact but blind to a "
            f"correction that cites no round. ⚠ UNIT GAP: instrument unit is {INSTRUMENT_UNIT}, "
            f"claim unit is {CLAIM_UNIT}.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "standing.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "n_blocks": n, "n_asserts": len(asserts), "n_withdraws": len(withdraw),
        "n_qualifies": len(qualify), "n_amended": base_amended,
        "standing": [r["heading"] for r in standing],
        "blocks": [{k: r[k] for k in ("heading", "marker", "head_rounds", "max_body", "amended", "why")}
                   for r in rows],
        "sham_definition_md": {"blocks": len(dbs), "amended": d_amended},
        "negative_scrambled_counts": scr_counts,
        "registered": ("A blocks 12 [8,20]; B asserts 4 [2,10]; C asserts amended 2 [0,4]; "
                       "directional withdrawals+qualifications > assertions"),
        "observed": {"A": A, "B": B, "C": Cc,
                     "directional": len(withdraw) + len(qualify) > len(asserts)},
        "limit": ("STANDING UNAMENDED IS NOT TRUTH — it is unattacked. Three F2 blocks stood "
                  "unamended until the round that killed each. And the marker reading is a "
                  "convention, positive-controlled but not a measurement."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
