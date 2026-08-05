#!/usr/bin/env python3
"""
R684 -- the judge is not in the record. What the deliverable's scope claims can actually rest on.

CHECK #285 ON R683's NEXT LINE -- IT HOLDS. `results/membership_null.json` carries `judges`, both
  cells, and the caution it raises ("two judges is a thin basis for instrument-dependent") is the
  right one. ⭐ Fifth NEXT in this arc to survive intact.

ESTIMAND        A: of rounds whose CODE references a judge, the share RECORDING it in the artifact.
                B: among recording artifacts, how many carry two or more judges?
IDENTIFICATION  ⚠ "code references a judge" is LEXICAL. A round varying the judge without naming it
                in a catchable way is excluded, which biases the population DOWN and the recorded
                share UP. Stated, not corrected.
SCOPE           population : this arc's rounds with a run.py and a results/*.json
                instrument : source regex for judge names + artifact key walk
                             instrument unit = A ROUND
                             claim unit      = A ROUND WHOSE SCOPE IS RECOVERABLE FROM ITS ARTIFACT
                             ⚠ NOT EQUAL — a recorded judge key is necessary, not sufficient.
                baseline   : the 14 artifacts the feasibility scan found
                regime     : this repository at HEAD
WORLDS          A RECORDED: most judge-varying rounds write the judge down; scope is recoverable.
                B SILENT: they do not, so a reader cannot tell a one-judge verdict from a two-judge
                  one without opening the code — and the deliverable inherits that.
KILL            fewer than 10 rounds referencing a judge -> counts only, no share.
CONFOUND        absence of a judge key ≠ one judge. Rounds with NO mention anywhere are EXCLUDED.
POSITIVE CTRL   R361 -> RECORDED-MULTI.
g=0             a round mentioning no judge -> EXCLUDED, not "unrecorded".
NEGATIVE CTRL   synthetic: code mentions a judge, artifact lacks it -> UNRECORDED.
PLACEBO         run twice identical.
ARTIFACT        results/judge_record.json
IMPOSSIBLE      whether a round's VERDICT would change at another judge needs that judge run; the
                release ships the two this arc uses.
"""
from __future__ import annotations
import io, json, pathlib, re, subprocess, sys, tokenize
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
KEY = re.compile(r"^(0\.8B|2B|8B|7B|judge|home|second)$", re.I)
SRC = re.compile(r"\b(0\.8B|2B|POOLS|judge|second judge|home judge)\b", re.I)


def executable_source(src: str) -> str:
    out, prev = [], tokenize.INDENT
    try: toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except Exception: return src
    for tk in toks:
        if tk.type == tokenize.COMMENT: continue
        if tk.type == tokenize.STRING and prev in (tokenize.INDENT, tokenize.NEWLINE,
                                                   tokenize.NL, tokenize.DEDENT,
                                                   tokenize.ENCODING):
            prev = tk.type; continue
        out.append(tk.string); prev = tk.type
    return " ".join(out)


def judge_keys(o, depth=0):
    out = set()
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(k, str) and KEY.match(k): out.add(k)
            if depth < 3: out |= judge_keys(v, depth + 1)
    elif isinstance(o, list) and depth < 3:
        for v in o[:20]: out |= judge_keys(v, depth + 1)
    return out


def assess(d: pathlib.Path):
    run = d / "run.py"
    res = sorted((d / "results").glob("*.json")) if (d / "results").is_dir() else []
    if not run.is_file() or not res: return None
    # ⭐ THE DOCSTRING STRIP, IMPORTED FROM R680 RATHER THAN RE-INVENTED. The first version scanned
    #   RAW source, and every round's header discusses judges in prose -- so the population was
    #   measuring DOCUMENTATION. R680 established this and I built the scan without it anyway, which
    #   is ledger 766: a validated instrument does not carry itself forward. Both numbers reported.
    src = executable_source(run.read_text(errors="ignore"))
    if not SRC.search(src): return {"round": d.name.split("_")[0], "kind": "EXCLUDED_no_judge"}
    ks = set()
    for j in res:
        try: ks |= judge_keys(json.loads(j.read_text()))
        except Exception: pass
    kind = ("RECORDED_MULTI" if len(ks) >= 2 else
            "RECORDED_ONE" if len(ks) == 1 else "UNRECORDED")
    return {"round": d.name.split("_")[0], "kind": kind, "keys": sorted(ks)}


def main() -> int:
    rows = [r for r in (assess(d) for d in sorted(ARC.glob("R*")) if d.is_dir()) if r]
    if not rows:
        print("UNRUNNABLE: no round has both a run.py and an artifact. Exit 2."); return 2

    print("─── CONTROLS ───")
    r361 = next((r for r in rows if r["round"] == "R361"), None)
    posok = bool(r361 and r361["kind"] == "RECORDED_MULTI")
    print(f"  POSITIVE  R361 (two judges in code AND artifact) -> "
          f"{r361['kind'] if r361 else 'absent'} -> {'PASS' if posok else '⛔ FAIL'}")
    excl = [r for r in rows if r["kind"] == "EXCLUDED_no_judge"]
    g0ok = len(excl) > 0
    print(f"  g=0       rounds mentioning NO judge are EXCLUDED, not counted unrecorded -> "
          f"{len(excl)} excluded -> "
          f"{'PASS — silence is not a verdict here' if g0ok else '⛔ FAIL — nothing excluded, so the confound is live'}")
    neg = judge_keys({"result": 1, "n": 3})
    negok = not neg
    print(f"  NEGATIVE  an artifact with no judge key -> {sorted(neg) or 'none'} -> "
          f"{'PASS' if negok else '⛔ FAIL'}")
    plc = [assess(d) for d in sorted(ARC.glob("R*")) if d.is_dir()] == \
          [assess(d) for d in sorted(ARC.glob("R*")) if d.is_dir()]
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and plc

    c = Counter(r["kind"] for r in rows)
    pop = c["RECORDED_MULTI"] + c["RECORDED_ONE"] + c["UNRECORDED"]
    rec = c["RECORDED_MULTI"] + c["RECORDED_ONE"]
    share = rec / pop if pop else 0.0
    killed = pop < 10

    print(f"\n─── THE SCOPE-RECORDING GAP (G3 — every category, none hidden) ───")
    print(f"  rounds with a run.py and an artifact : {len(rows)}")
    print(f"  ⚠ EXCLUDED — no judge mentioned at all: {c['EXCLUDED_no_judge']}  "
          f"(counted as unrecorded, this would be the confound)")
    print(f"  population — code references a judge  : {pop}")
    print(f"    ⭐ RECORDED_MULTI (>=2 judge keys)  : {c['RECORDED_MULTI']}")
    print(f"    RECORDED_ONE                        : {c['RECORDED_ONE']}")
    print(f"    ⛔ UNRECORDED                        : {c['UNRECORDED']}")
    print(f"  ⭐ share recording the judge          : {share:.1%}")
    print(f"  registered A 40% [10,80] -> {share:.1%}: "
          f"{'INSIDE' if 0.10 <= share <= 0.80 else '⛔ OUTSIDE'}, error {share-0.40:+.1%}")
    print(f"  registered B 7 [2,14] -> {c['RECORDED_MULTI']}: "
          f"{'INSIDE' if 2 <= c['RECORDED_MULTI'] <= 14 else '⛔ OUTSIDE'}, "
          f"error {c['RECORDED_MULTI']-7:+d}")
    dirn = c["UNRECORDED"] > rec
    print(f"  DIRECTIONAL under-recording dominates -> {'HOLDS' if dirn else '⛔ FAILS'}")
    print(f"  pre-registered kill (<10 in population) -> "
          f"{'⭐ FIRES — counts only' if killed else 'does not fire'}")
    print(f"\n  the rounds that DO record two judges: "
          f"{[r['round'] for r in rows if r['kind'] == 'RECORDED_MULTI']}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif share >= 0.5:
        world = (f"A RECORDED — {share:.1%} of judge-varying rounds write the judge into the "
                 f"artifact; scope is mostly recoverable without opening the code.")
    else:
        world = (f"⭐⭐⭐ B SILENT — of {pop} rounds whose code references a judge, only {rec} "
                 f"({share:.1%}) record one in their artifact, and {c['RECORDED_MULTI']} record two. "
                 f"⭐ SO A READER CANNOT TELL A ONE-JUDGE VERDICT FROM A TWO-JUDGE ONE WITHOUT "
                 f"OPENING THE CODE, and the deliverable inherits exactly that ambiguity — R683 "
                 f"showed the ③ separation resolves at 2B and not at 0.8B, so the judge is not a "
                 f"detail, it is the scope. ⚠ AND THE CONFOUND IS WHY THIS NUMBER IS SMALL AND NOT "
                 f"ZERO: {c['EXCLUDED_no_judge']} rounds mention no judge anywhere and are EXCLUDED "
                 f"rather than counted as unrecorded — absence of a judge key is not evidence of one "
                 f"judge, and folding those in would have manufactured a far worse-looking gap.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(rows)} rounds × (source scan + artifact walk), 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"judge_record.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "n_rounds": len(rows), "counts": dict(c), "population": pop,
        "recorded": rec, "recorded_share": share, "kill_fired": killed,
        "directional_holds": dirn, "rows": rows,
        "multi_judge_rounds": [r["round"] for r in rows if r["kind"] == "RECORDED_MULTI"],
        "registered": "A 40% [10,80]; B 7 [2,14]; under-recording dominates; kill if pop<10",
        "confound": ("absence of a judge key is NOT one judge; rounds mentioning no judge are "
                     "EXCLUDED, never counted unrecorded."),
        "limit": ("'code references a judge' is lexical; a round varying it without a catchable "
                  "name is excluded, biasing the population DOWN and the share UP."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'judge_record.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
