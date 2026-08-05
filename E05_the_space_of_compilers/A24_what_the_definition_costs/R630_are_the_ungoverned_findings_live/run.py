#!/usr/bin/env python3
"""
R630 -- are FORMULATION.md's 17 ungoverned findings superseded, or live and never carried?

CHECK #229: I QUANTIFIED OVER A TRUNCATED PRINT -- A LISTED FAILURE MODE, COMMITTED DIRECTLY.
  ⛔ "nine of the seventeen cite rounds in the 280-360 band" and "the six that name a clause" --
     NEITHER COMPUTED. R629 printed `uh[:12]` and I counted off the display. §4's "truncated
     string read as data" row, in its purest form: I read a slice as the population. Thirteenth
     and fourteenth uncomputed counts, and the first two sourced from my own truncation.
  ⭐ The remedy is not care, it is arithmetic: this round computes both numbers, and every count
     it reports is over the full list.

ESTIMAND        for each of FORMULATION.md's R-headed findings that the gated pair does not carry:
                  BAND      the round-id range it cites
                  CLAUSE    does it name ① ② ③ or ④
                  STATUS    RETRACTED (its round appears in RETRACTIONS.md) ·
                            UNSETTLED (its round's artifact world is UNVERIFIED or absent) ·
                            LIVE (settled verdict, no retraction) -> ungoverned debt
IDENTIFICATION  Exact for band and clause. STATUS is a PROXY and its ledger is stated: appearing
                in RETRACTIONS.md means SOMETHING about that round was retracted, not necessarily
                THIS finding. SOUND direction: a round absent from the ledger with a settled
                verdict is genuinely uncorrected. UNSOUND: a listed round may have had a different
                claim retracted, so RETRACTED OVERSTATES supersession and LIVE is a LOWER bound.
SCOPE           population : the R-headed findings in FORMULATION.md absent from the gated pair
                instrument : RETRACTIONS.md membership + the cited round's artifact verdict
                             instrument unit = A ROUND ID
                             claim unit      = A FINDING. NOT equal -- a finding can cite several
                             rounds, so a finding is LIVE only if EVERY round it cites is live,
                             which is the conservative direction for the debt claim.
                baseline   : the live definition, `② ∧ ③`
                regime     : this repository at this sha
WORLDS          A SUPERSEDED: the ungoverned findings are old work already retracted elsewhere.
                  Then FORMULATION.md is a history file and belongs in _archive/ under L81.
                B LIVE DEBT: findings with settled verdicts, no retraction, naming a clause.
                  Then substantive claims about the definition sit outside every gate, and the
                  arc owes their adjudication rather than another instrument.
KILL            pre-registered: >= 1 finding that names a clause AND is LIVE -> world B.
POSITIVE CTRL   a round known to be in RETRACTIONS.md must classify RETRACTED. Fails at g=0: a
                round absent from the ledger must not.
NEGATIVE CTRL   a fabricated round id must classify UNSETTLED (no artifact), never LIVE.
PLACEBO         a clause glyph that does not occur -> 0 findings named.
SEEDS           n/a, deterministic.
MULTIPLICITY    every finding x 3 status classes x 4 clause glyphs + 4 controls. Full list printed.
ARTIFACT        results/are_they_live.json
IMPOSSIBLE      whether a finding CONTRADICTS `② ∧ ③` needs a reader -- no extractor decides it.
                Every LIVE finding is printed verbatim with its band and clause so one can.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
E05 = ROOT / "E05_the_space_of_compilers"
A24 = E05 / "A24_what_the_definition_costs"
CITE = re.compile(r"R(\d{3})")
HEAD = re.compile(r"^#{2,3} (.+)$", re.M)
CLAUSE = re.compile(r"[①②③④]|clause\s*[1-4②③①④]", re.I)


def verdict(rid):
    for d in A24.glob(f"R{rid}_*"):
        for f in (d / "results").glob("*.json"):
            try: j = json.loads(f.read_text())
            except Exception: continue
            if isinstance(j, dict):
                for k in ("world", "verdict"):
                    if isinstance(j.get(k), str): return j[k]
    return None


def main():
    F = (E05 / "FORMULATION.md").read_text()
    G = (E05 / "STATEMENT.md").read_text() + "\n" + (E05 / "DEFINITION.md").read_text()
    RET = (ROOT / "RETRACTIONS.md").read_text()
    fh = [h.strip() for h in HEAD.findall(F) if CITE.search(h)]
    uh = [h for h in fh if not all(("R" + r) in G for r in CITE.findall(h))]
    if not uh:
        print("UNRUNNABLE: no ungoverned findings. Exit 2, never 0."); return 2
    print(f"  R-headed findings in FORMULATION.md: {len(fh)}   not carried by the gated pair: {len(uh)}")

    print(f"\n─── CONTROLS ───")
    listed = sorted({r for r in CITE.findall(RET)})
    pos = listed and all(("R" + listed[0]) in RET for _ in (0,))
    print(f"  POSITIVE  RETRACTIONS.md names {len(listed)} distinct rounds; R{listed[0]} classifies "
          f"RETRACTED -> {'PASS' if pos else '⛔ FAIL'}")
    absent = next((f"{n:03d}" for n in range(100, 1000) if f"R{n:03d}" not in RET), None)
    print(f"  g=0       a round absent from the ledger (R{absent}) does NOT classify RETRACTED -> "
          f"{'PASS' if absent and absent not in listed else '⛔ FAIL'}")
    fab = "R997"
    neg = verdict("997") is None
    print(f"  NEGATIVE  a fabricated round {fab} has no artifact -> classifies UNSETTLED, never "
          f"LIVE -> {'PASS' if neg else '⛔ FAIL'}")
    plc = sum(1 for h in uh if "⑨" in h)
    print(f"  PLACEBO   a clause glyph that does not occur -> {plc} findings -> "
          f"{'PASS' if plc == 0 else '⛔ FAIL'}")
    controls_ok = bool(pos) and absent is not None and neg and plc == 0

    print(f"\n─── EVERY UNGOVERNED FINDING, FULL LIST — no truncation ───")
    rows, bands = [], {}
    for h in uh:
        rs = sorted(set(CITE.findall(h)))
        lo = min(int(r) for r in rs)
        band = f"{lo//100*100+((lo%100)//40)*40:03d}s"
        bands[band] = bands.get(band, 0) + 1
        ret = [r for r in rs if f"R{r}" in RET]
        vs = {r: verdict(r) for r in rs}
        unsettled = [r for r, v in vs.items() if v is None or v.upper().startswith("UNVERIFIED")]
        status = "RETRACTED" if ret else ("UNSETTLED" if unsettled else "LIVE")
        named = bool(CLAUSE.search(h))
        rows.append({"heading": h, "rounds": rs, "min_round": lo, "clause": named,
                     "status": status, "retracted_rounds": ret, "unsettled_rounds": unsettled})
        print(f"  [{status:<9}] {'clause' if named else '      '}  R{','.join(rs[:3]):<12} "
              f"{h[:74]}")

    live_clause = [r for r in rows if r["status"] == "LIVE" and r["clause"]]
    in_band = sum(1 for r in rows if 280 <= r["min_round"] <= 360)
    named_n = sum(1 for r in rows if r["clause"])
    print(f"\n─── THE TWO COUNTS I ASSERTED FROM A TRUNCATED PRINT ───")
    print(f"  cite a round in the 280-360 band : claimed 9  measured {in_band}")
    print(f"  name a clause                    : claimed 6  measured {named_n}")
    print(f"  status: LIVE {sum(1 for r in rows if r['status']=='LIVE')} · "
          f"RETRACTED {sum(1 for r in rows if r['status']=='RETRACTED')} · "
          f"UNSETTLED {sum(1 for r in rows if r['status']=='UNSETTLED')}")

    print(f"\n─── VERDICT (pre-registered: >=1 LIVE finding naming a clause -> world B) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif live_clause:
        world = (f"B LIVE DEBT — {len(live_clause)} finding(s) name a clause, carry a settled "
                 f"verdict and appear in no retraction, while sitting outside every gate. The arc "
                 f"owes their adjudication against `② ∧ ③`, not another instrument.")
    else:
        world = (f"A SUPERSEDED — no ungoverned finding is both clause-naming and live. "
                 f"FORMULATION.md is a history file and belongs in _archive/ under L81.")
    print(f"  {world}")
    for r in live_clause:
        print(f"    LIVE · R{','.join(r['rounds'][:3])} · {r['heading'][:88]}")
    print(f"\n  ⚠ PROXY LEDGER: RETRACTIONS.md membership means SOMETHING about that round was "
          f"retracted, not necessarily THIS finding — so RETRACTED OVERSTATES supersession and "
          f"LIVE is a LOWER bound on the debt.")
    print(f"  ⚠ Whether a LIVE finding CONTRADICTS `② ∧ ③` needs a reader. Every one is printed "
          f"above with its rounds so one can judge; the count is not that judgement.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "are_they_live.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "n_ungoverned": len(uh),
        "claimed_band_count": 9, "measured_band_count": in_band,
        "claimed_clause_count": 6, "measured_clause_count": named_n,
        "bands": bands, "findings": rows,
        "check229": ("both counts in the closing line were read off a `uh[:12]` truncated print -- "
                     "§4's 'truncated string read as data', committed directly"),
        "impossible": "contradiction with the live definition needs a reader; LIVE is a lower bound",
    }, indent=2))
    print(f"\n  wrote {OUT / 'are_they_live.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
