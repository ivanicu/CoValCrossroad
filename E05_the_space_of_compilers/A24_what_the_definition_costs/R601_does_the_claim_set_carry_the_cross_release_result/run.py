#!/usr/bin/env python3
"""
R601 -- does the deliverable's CLAIM SET carry the cross-release result about clause ②?

CHECK #200 FOUND TWO ERRORS IN R600's CLOSING LINE.
  ⛔ "two of the eight ... being CENSUS rounds" -- verified for R294, INFERRED for R288 from a
     mention inside R558. Two hypotheses (a census round vs a round that merely omitted the
     key) were collapsed into one label on one round's worth of evidence.
  ⛔ "if that class is LARGE ... if it is SMALL" is a decision rule with NO THRESHOLD, so it
     could not have failed. A pre-registration without a number is a sentence, not a commitment.
Both recorded as Closure. The round goes elsewhere, because R600 surfaced something larger and
did not pursue it.

R433's README, verbatim: *"whether clause ② is a property of CORES or a description of what
CoVal did. It is a description."* A prompt-specific core generated from the conversation alone
-- the clause's own subject -- **loses to a judge-free length heuristic by −0.0545, resolved**,
on the SECOND release. That is §4's `the definition describes the instance` row, measured and
resolved rather than warned about.

`STATEMENT.md` cites R433 exactly once: in the impossibility register's row 5, as FILE
PROVENANCE that a second release exists on disk. **Not as a finding about the definition.**

ESTIMAND        For the live definition's clauses (② and ③): does the deliverable's CLAIM SET
                -- the numbered claim table, not the register and not the prose -- cite any
                round that scored that clause on the SECOND release?
                n_uncarried = clauses with a cross-release result on disk and no claim row.
IDENTIFICATION  Exact given two recognisers, both of which are searches and both of which get
                controls: (i) which rounds are cross-release, (ii) which rounds the CLAIM TABLE
                cites. ⚠ "bears on clause ②" is not decidable from a file listing; it is read
                from each round's own README heading and printed verbatim so a reader can
                overrule. Upper bound, never a verdict on the science.
SCOPE           population : rounds whose artifacts or run.py reference the second corpus
                instrument : (i) `utterances.jsonl` / `corpus.*second` / `transport` in the
                             round's own files; (ii) the gate's citation regex restricted to
                             the claim-table block of STATEMENT.md
                             instrument unit = A CITATION INSIDE THE CLAIM TABLE
                             claim unit      = THE CLAIM SET ASSERTS THIS
                             EQUAL by construction -- the claim table IS the claim set, and
                             the register and prose are deliberately excluded because they are
                             where a caveat goes, not where a claim is made
                baseline   : the home-release rounds the claim table does cite
                regime     : as committed at this sha
WORLDS          A CARRIED: the claim table cites a cross-release round for ② -> the scope is
                  already stated and nothing is owed.
                B UNCARRIED: cross-release results exist and the claim table is silent -> every
                  claim row is home-release-only and does not say so, and the definition's
                  scope is overstated by exactly one release.
                C NOT ABOUT THE CLAUSES: the cross-release rounds do not bear on ② or ③ ->
                  R433's W-LOSES is about a different object and nothing is owed.
KILL            pre-registered, with the threshold R600's line lacked: if the cross-release
                recogniser finds fewer than 2 rounds, it has not demonstrated it can see the
                class and no absence claim is admissible -- UNVERIFIED, not "uncarried".
POSITIVE CTRL   the claim-table recogniser must find the rounds the table visibly cites (R519,
                R529, R527 are in it). Fails at g=0: an empty block yields no citations.
                The cross-release recogniser must find R433, R427, R398 -- known members.
NEGATIVE CTRL   a home-only round (R519) must NOT be classified cross-release.
PLACEBO         a nonexistent corpus token must return 0 rounds.
SEEDS           n/a, deterministic.
MULTIPLICITY    2 recognisers x every round + 4 control checks. All reported.
ARTIFACT        results/cross_release_carriage.json
IMPOSSIBLE      construct validity for "this round bears on clause ②": intent is in the
                round's prose, not in its file list. Every member's README heading is printed.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
# ⛔ v1 INCLUDED THE BARE WORD `transport` AND CLASSED 109 OF 376 ROUNDS CROSS-RELEASE. The
# negative control caught it: R519, a home-only round, matched. `transport` collides with the
# helper `judge_transport` and with the ordinary English word used in prose about whether a
# result transports. Tightened to things that can only mean the second corpus: its data file,
# its loader, and its explicit flag.
SECOND = re.compile(r"utterances\.jsonl|load_second|corpus[\"']?\s*[,=:]\s*[\"']?second|"
                    r"--corpus\s+second", re.I)
CITE = r"\(R(\d{3})[,)]|R(\d{3})[,)]"


def claim_table(text):
    """The numbered claim table only. The register and the prose are NOT the claim set."""
    m = re.search(r"\n\| # \| claim \| scope it holds over \|\n.*?\n\n", text, re.S)
    if not m:
        m = re.search(r"\n\| \*\*1\*\* \|.*?\n\n", text, re.S)
    return m.group(0) if m else ""


def cites(block):
    return sorted({int(a or b) for a, b in re.findall(CITE, block)})


def rounds():
    out = {}
    for d in sorted(E05.glob("A*/R[0-9]*")):
        if not d.is_dir():
            continue
        m = re.match(r"R(\d+)", d.name)
        if not m:
            continue
        blob = ""
        for f in list(d.glob("*.py")) + (list((d / "results").glob("*.json"))
                                         if (d / "results").is_dir() else []):
            try:
                blob += f.read_text(errors="ignore")[:200000]
            except Exception:
                pass
        head = ""
        if (d / "README.md").is_file():
            head = (d / "README.md").read_text().split("\n")[0][:110]
        out[int(m.group(1))] = {"dir": d.name, "blob": blob, "head": head}
    out.pop(601, None)          # a round may not be a member of the population it measures
    return out


def main():
    text = (E05 / "STATEMENT.md").read_text()
    block = claim_table(text)
    R = rounds()
    if not R:
        print("UNRUNNABLE: no rounds. Exit 2, never 0.")
        return 2

    # ---- CONTROLS FIRST -------------------------------------------------------------
    print("─── CONTROLS ───")
    tab = cites(block)
    pos1 = len(block) > 200 and {519, 529, 527} & set(tab)
    print(f"  POSITIVE  claim-table block found ({len(block)} chars), cites {len(tab)} rounds; "
          f"known members 519/529/527 present -> {'PASS' if pos1 else '⛔ FAIL'}")
    g0 = cites("")
    print(f"  g=0       empty block -> {len(g0)} citation(s) -> "
          f"{'PASS (can fail)' if not g0 else '⛔ FAIL'}")
    xr = sorted(r for r, v in R.items() if SECOND.search(v["blob"]))
    known = {433, 427, 398}
    pos2 = known <= set(xr)
    print(f"  POSITIVE  cross-release recogniser finds {len(xr)} round(s); known members "
          f"{sorted(known)} present -> {'PASS' if pos2 else '⛔ FAIL — missing '+str(sorted(known-set(xr)))}")
    neg = 519 not in xr
    print(f"  NEGATIVE  a home-only round (R519) is NOT classified cross-release -> "
          f"{'PASS' if neg else '⛔ FAIL'}")
    # ⛔ v1's PLACEBO TOKEN MATCHED EXACTLY ONE ROUND: THIS ONE. The instrument scans a
    #    population that contains its own source, so any literal it searches for is guaranteed
    #    present. Same class as R598's harness reading a tree it was mutating. The token is now
    #    assembled at runtime so it cannot appear in the file, and the round excludes itself.
    plcpat = re.compile("zzq" + "_nonexistent" + "_corpus", re.I)
    plc = [r for r, v in R.items() if plcpat.search(v["blob"])]
    print(f"  PLACEBO   a nonexistent corpus token -> {len(plc)} round(s) -> "
          f"{'PASS' if not plc else '⛔ FAIL'}")
    enough = len(xr) >= 2
    print(f"  KILL      cross-release class size {len(xr)} >= 2 -> "
          f"{'PASS — an absence claim is admissible' if enough else '⛔ UNVERIFIED'}")
    controls_ok = bool(pos1) and not g0 and pos2 and neg and not plc and enough

    # ---- THE MEASUREMENT ------------------------------------------------------------
    print(f"\n─── CROSS-RELEASE ROUNDS, AND WHETHER THE CLAIM TABLE CITES THEM ───")
    carried, uncarried = [], []
    for r in xr:
        inside = r in tab
        (carried if inside else uncarried).append(r)
    print(f"  cross-release rounds: {len(xr)}   cited by the CLAIM TABLE: {len(carried)} "
          f"{carried}")
    print(f"\n  the ones the claim table does NOT cite ({len(uncarried)}), with their own "
          f"README headings:")
    for r in uncarried:
        h = R[r]["head"] or "(no README)"
        anywhere = bool(re.search(rf"R{r}\b", text))
        print(f"    R{r}  {'mentioned elsewhere on the page' if anywhere else 'ABSENT from the page entirely'}")
        print(f"          {h}")

    # ---- VERDICT: a function of the controls, nothing written in between -------------
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no carriage claim is admissible"
    elif carried:
        world = (f"A CARRIED — the claim table cites {len(carried)} cross-release round(s) "
                 f"{carried}; the scope is stated where the claims are made")
    else:
        world = (f"B UNCARRIED — {len(xr)} cross-release round(s) exist on disk and the claim "
                 f"table cites NONE of them. Every claim row is home-release-only and does not "
                 f"say so. R433 measured clause ②'s own subject LOSING to a length heuristic "
                 f"by −0.0545, resolved, on the second release — and that is not in the claim "
                 f"set.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 2 recognisers x {len(R)} rounds + 5 control checks. "
          f"{len(xr)} cross-release, {len(carried)} carried, {len(uncarried)} not.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "cross_release_carriage.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "claim_table_chars": len(block), "claim_table_cites": tab,
        "cross_release_rounds": xr, "carried": carried, "uncarried": uncarried,
        "headings": {str(r): R[r]["head"] for r in xr},
        "check200": ("R600's closing line called R288 a census round on inferred evidence, and "
                     "stated a large/small decision rule with no threshold. Both recorded."),
        "upper_bound_note": ("'bears on clause ②' is in the round's prose, not its file list; "
                             "every heading is printed so a reader can overrule"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'cross_release_carriage.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
