#!/usr/bin/env python3
"""
R685 -- do the two judges agree? Whether instrument-dependence belongs to the clause or the bench.

CHECK #286 ON R684's NEXT LINE -- IT HOLDS. `multi_judge_rounds` lists exactly the seven, `counts`
  carries the 81, and the distinction it draws (a benchmark property vs a clause property) is a real
  fork with different consequences for the deliverable. ⭐ Sixth NEXT in this arc to survive intact.

ESTIMAND        A: of the 7 rounds recording two judges, how many DISAGREE on at least one
                   verdict-like field?
                B: the share of per-judge verdict PAIRS that disagree.
IDENTIFICATION  ⚠ agreement between THESE two judges is not agreement in general. Two is what the
                release ships; a rate over 2 bounds nothing about a third.
SCOPE           population : the 7 rounds R684 found recording >=2 judge keys
                instrument : artifact walk for dicts keyed by judge whose values are VERDICT-LIKE
                             instrument unit = A PER-JUDGE VERDICT PAIR = claim unit. EQUAL.
                baseline   : R683's single measured split (2B resolved, 0.8B not)
                regime     : this repository at HEAD
WORLDS          A CLAUSE PROPERTY: the judges mostly agree, so R683's split is specific to ③ and the
                  scope note in STATEMENT.md is correctly attributed.
                B BENCH PROPERTY: they mostly split, so instrument-dependence is a fact about this
                  benchmark, and attributing it to ③ overstates what was measured.
KILL            fewer than 4 rounds exposing a verdict-like field -> counts only, no share.
⚠ DESIGN        a per-judge dict of CONTINUOUS values differs at every judge by construction.
                Counting that as disagreement returns 100% and measures nothing. Only booleans and
                small-closed-set strings count; a round with no such field is EXCLUDED.
POSITIVE CTRL   R361 (rank_resolved 2B true / 0.8B false) must classify DISAGREE.
g=0             identical values at both judges -> AGREE; the classifier returns both.
NEGATIVE CTRL   a single-judge artifact -> EXCLUDED, not AGREE.
PLACEBO         run twice identical.
ARTIFACT        results/judge_agreement.json
IMPOSSIBLE      a third judge would settle whether the split is pairwise or general; the release
                ships two.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
PRIOR = ARC / "R684_the_judge_is_not_in_the_record" / "results" / "judge_record.json"
KEY = re.compile(r"^(0\.8B|2B|8B|7B|home|second)$", re.I)
VERDICTISH = re.compile(r"^(RESOLVED|NOT[_ ]RESOLVED|PASS|FAIL|TRUE|FALSE|W_|UNVERIFIED|"
                        r"CONFIRMED|OVERTURNED|YES|NO|NULL|ADMITTED|EXCLUDED)", re.I)


# ⭐⭐⭐ THE UNIT FIX. v1 counted `controls.positive`, `controls.g0`, `controls.placebo`,
#     `controls.sham` as verdicts. A CONTROL FLAG PASSES AT BOTH JUDGES BY DESIGN -- that is what
#     makes it a control -- so 9 of 10 "agreeing pairs" were agreement about my own controls
#     passing. Instrument unit was "a per-judge boolean"; claim unit is "a per-judge VERDICT ABOUT
#     THE OBJECT". Not equal, and the gap manufactured 90% of the population.
CONTROL_PATH = re.compile(r"(^|\.)(controls?|ctrl|checks?)(\.|$)", re.I)


def verdict_like(v):
    if isinstance(v, bool): return True
    if isinstance(v, str) and len(v) <= 24 and VERDICTISH.match(v.strip()): return True
    return False


def pairs_in(o, path="", depth=0, out=None):
    """dicts keyed by >=2 judges whose values are ALL verdict-like."""
    if out is None: out = []
    if isinstance(o, dict):
        ks = [k for k in o if isinstance(k, str) and KEY.match(k)]
        if (len(ks) >= 2 and all(verdict_like(o[k]) for k in ks)
                and not CONTROL_PATH.search(path)):
            out.append({"field": path or "(root)", "values": {k: o[k] for k in ks}})
        if depth < 4:
            for k, v in o.items(): pairs_in(v, f"{path}.{k}" if path else str(k), depth + 1, out)
    elif isinstance(o, list) and depth < 4:
        for v in o[:20]: pairs_in(v, path, depth + 1, out)
    return out


def assess(rd):
    d = next(iter(ARC.glob(f"{rd}_*")), None)
    if d is None: return None
    ps = []
    for j in sorted((d / "results").glob("*.json")):
        try: ps += pairs_in(json.loads(j.read_text()))
        except Exception: pass
    if not ps: return {"round": rd, "kind": "EXCLUDED_no_verdict_field", "pairs": []}
    dis = [p for p in ps if len(set(map(str, p["values"].values()))) > 1]
    return {"round": rd, "kind": "DISAGREE" if dis else "AGREE",
            "n_pairs": len(ps), "n_disagree": len(dis), "pairs": ps}


def main() -> int:
    if not PRIOR.is_file():
        print("UNRUNNABLE: R684's artifact absent. Exit 2, never 0."); return 2
    seven = json.loads(PRIOR.read_text())["multi_judge_rounds"]

    print("─── CONTROLS ───")
    r361 = assess("R361")
    posok = bool(r361 and r361["kind"] == "DISAGREE")
    print(f"  POSITIVE  R361 is KNOWN to split (2B resolved / 0.8B not) -> "
          f"{r361['kind'] if r361 else 'absent'} -> {'PASS' if posok else '⛔ FAIL'}")
    g0 = pairs_in({"v": {"2B": True, "0.8B": True}})
    g0ok = bool(g0) and len(set(map(str, g0[0]["values"].values()))) == 1
    print(f"  g=0       identical values at both judges -> "
          f"{'AGREE' if g0ok else 'not detected'} -> "
          f"{'PASS — the classifier returns both' if g0ok else '⛔ FAIL'}")
    neg = pairs_in({"v": {"2B": True}})
    negok = not neg
    print(f"  NEGATIVE  a single-judge artifact -> {len(neg)} pairs -> "
          f"{'PASS — EXCLUDED, not AGREE' if negok else '⛔ FAIL'}")
    cont = pairs_in({"m": {"2B": 0.51, "0.8B": 0.47}})
    contok = not cont
    print(f"  ⚠ DESIGN  a per-judge dict of CONTINUOUS values must NOT count -> {len(cont)} pairs -> "
          f"{'PASS — numeric difference is not disagreement' if contok else '⛔ FAIL — would return 100%'}")
    ctlpath = pairs_in({"controls": {"positive": {"2B": True, "0.8B": True}}})
    cpok = not ctlpath
    print(f"  ⚠ UNIT     a CONTROL flag keyed by judge must NOT count as a verdict -> "
          f"{len(ctlpath)} pairs -> "
          f"{'PASS — controls pass at both judges by design' if cpok else '⛔ FAIL — 90% of the population is my own controls'}")
    plc = [assess(r) for r in seven] == [assess(r) for r in seven]
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and contok and cpok and plc

    rows = [r for r in (assess(r) for r in seven) if r]
    c = Counter(r["kind"] for r in rows)
    scored = [r for r in rows if r["kind"] in ("AGREE", "DISAGREE")]
    npairs = sum(r["n_pairs"] for r in scored)
    ndis = sum(r["n_disagree"] for r in scored)
    share = ndis / npairs if npairs else 0.0
    killed = len(scored) < 4

    print(f"\n─── THE SEVEN (G3 — all printed, every verdict pair counted) ───")
    for r in rows:
        print(f"  {r['round']:<6} {r['kind']:<26} pairs {r.get('n_pairs',0):>2}  "
              f"disagreeing {r.get('n_disagree',0):>2}")
        for p in r.get("pairs", [])[:3]:
            print(f"           {p['field'][:44]:<46} {p['values']}")
    print(f"\n  rounds recording two judges : {len(rows)}")
    print(f"  ⚠ EXCLUDED — no verdict-like per-judge field : "
          f"{c['EXCLUDED_no_verdict_field']}  (scored AGREE, this would be the confound)")
    print(f"  scored : {len(scored)}   ⭐ DISAGREE {c['DISAGREE']}   AGREE {c['AGREE']}")
    print(f"  verdict pairs {npairs}   ⭐ disagreeing {ndis}  ({share:.1%})")
    print(f"  registered A 3 [1,6] -> {c['DISAGREE']}: "
          f"{'INSIDE' if 1 <= c['DISAGREE'] <= 6 else '⛔ OUTSIDE'}, error {c['DISAGREE']-3:+d}")
    print(f"  registered B 40% [15,70] -> {share:.1%}: "
          f"{'INSIDE' if 0.15 <= share <= 0.70 else '⛔ OUTSIDE'}, error {share-0.40:+.1%}")
    dirn = ndis >= npairs - ndis
    print(f"  DIRECTIONAL disagreement at least as common as agreement -> "
          f"{'HOLDS' if dirn else '⛔ FAILS'}")
    print(f"  pre-registered kill (<4 scored) -> "
          f"{'⭐ FIRES — counts only, no share' if killed else 'does not fire'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; no agreement claim is admissible."
    elif killed:
        world = (f"NOT IDENTIFIED — only {len(scored)} of {len(rows)} expose a verdict-like per-judge "
                 f"field. Counts only: {c['DISAGREE']} disagree, {c['AGREE']} agree. No share.")
    elif share >= 0.5:
        world = (f"⭐⭐⭐ B BENCH PROPERTY — {ndis} of {npairs} per-judge verdict pairs ({share:.1%}) "
                 f"disagree across {len(scored)} rounds. R683's split is TYPICAL, not specific to ③, "
                 f"so attributing instrument-dependence to the CLAUSE overstates what was measured — "
                 f"the scope note in STATEMENT.md needs re-attribution to the benchmark.")
    else:
        world = (f"⭐⭐ A CLAUSE PROPERTY (weakly) — {ndis} of {npairs} pairs ({share:.1%}) disagree; "
                 f"{c['DISAGREE']} of {len(scored)} rounds carry at least one split. The judges agree "
                 f"more often than not, so R683's split is NOT the default behaviour of this bench "
                 f"and the scope note stays attributed to ③. ⚠ BUT THE BASE RATE IS NOT ZERO: with "
                 f"{share:.1%} of pairs splitting, a single-judge verdict anywhere in this corpus has "
                 f"roughly that chance of not surviving the other judge — and R684 measured that 81 "
                 f"rounds vary a judge without recording which.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(rows)} rounds × {npairs} verdict pairs, 5 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"judge_agreement.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "rounds": rows, "counts": dict(c), "n_scored": len(scored),
        "n_pairs": npairs, "n_disagree": ndis, "disagree_share": share,
        "kill_fired": killed, "directional_holds": dirn,
        "registered": "A 3 [1,6]; B 40% [15,70]; disagreement >= agreement; kill if <4 scored",
        "design": ("continuous per-judge values differ by construction and are EXCLUDED; only "
                   "booleans and small-closed-set strings count as verdicts."),
        "limit": "two judges is what the release ships; a rate over 2 bounds nothing about a third.",
    }, indent=2))
    print(f"  wrote {HERE/'results'/'judge_agreement.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
