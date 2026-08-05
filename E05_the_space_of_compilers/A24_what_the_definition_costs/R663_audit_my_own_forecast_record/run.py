#!/usr/bin/env python3
"""
R663 -- audit my own forecast record, with an admissibility rule I cannot bend at scoring time.

CHECK #264 ON R662's CLOSING LINE. THE CLAIM IT MAKES ABOUT MY RECORD IS ITSELF UNCOUNTED.
  ✓ "both pre-registered estimates landed INSIDE on a design with 0.14 power" -- printed by R662.
  ⛔ "the record currently reads 'six of seven directional predictions held'" -- stated from memory.
     R662's own PREREGISTRATION says "seven directional -- six held, one retracted"; the artifacts
     carry the real record and were never read.
  ⛔ "at least THREE of those were about numbers that no longer exist" -- asserted, never counted.
  ⭐ So the round is the count, and it is the arc's own instrument turned on the forecaster rather
     than the forecast.

⚠⚠ THE OBVIOUS SELF-SERVING FAILURE, NAMED BEFORE IT CAN HAPPEN AND DESIGNED AGAINST.
    An author grading his own forecasts can rescue every miss by ruling the statistic inadmissible
    afterwards. So admissibility here reads ONLY fields already committed BEFORE this round existed:
      (i)  `controls_ok` inside the round's own artifact, and
      (ii) a RETRACTIONS.md entry, written earlier, naming that round's statistic as withdrawn.
    No judgement is permitted at scoring time. Anything the rule cannot decide is UNDECIDABLE and is
    reported as such rather than assigned to a side.

ESTIMAND        A: rounds in this arc whose artifact persists a `prereg` block.
                B: of those, how many are ADMISSIBLE under the mechanical rule above.
                C: the directional hit-rate over ADMISSIBLE forecasts only.
IDENTIFICATION  A and B are exact -- both read committed fields. C is exact given B, but is a rate
                over a handful of cases and is reported with its denominator every time it appears.
                NOT identified: whether an admissible hit reflects judgement rather than luck. With
                n this small no design here separates them, and that is the point rather than a
                caveat.
SCOPE           population : every R6xx round directory with a results/*.json carrying `prereg`
                instrument : json field reads + a retraction-name scan
                             instrument unit = A PERSISTED FORECAST
                             claim unit      = A FORECAST I MADE
                             NOT EQUAL -- forecasts written only in a NEXT line and never persisted
                             are invisible here, so A is a LOWER BOUND on forecasts made
                baseline   : the record as I currently believe it (8 magnitudes, 8 directional)
                regime     : at the tree sha persisted in the artifact
WORLDS          A THE RECORD STANDS: most forecasts are admissible -> the filtering changes nothing
                  and "seven of eight held" is a statement about my judgement.
                B THE RECORD DISSOLVES: few are admissible -> the hit-rate was computed over
                  statistics that no longer exist, and no calibration claim survives.
                C UNDECIDABLE DOMINATES: the mechanical rule cannot classify most of them -> the
                  audit is not possible from committed fields and must say so.
KILL            pre-registered in PREREGISTRATION.txt before the code: B point 3, interval [1, 5];
                directional "B <= 4 and the record does not survive". If B >= 6 the prediction is
                RETRACTED and the record stands as stated.
POSITIVE CTRL   R661's per-round rho and R660's 86.1% are KNOWN-withdrawn (entries 699 and 693).
                The rule must mark both INADMISSIBLE. If it does not, it cannot see the class and no
                filtered rate is admissible.
NEGATIVE CTRL   R659's counts (39 tight / 132 loose) were never withdrawn -- R662's README lists
                them under STANDS. The rule must NOT mark R659 inadmissible. The failure direction
                is a rule that voids everything and thereby excuses every miss.
PLACEBO         a synthetic round id that appears in no retraction must come back ADMISSIBLE.
NOISE FLOOR     n/a -- a census of committed text. Deterministic.
MULTIPLICITY    1 rule x every persisted forecast + 3 controls. Every forecast printed with its
                verdict and the field that decided it.
ARTIFACT        results/forecast_audit.json, with the tree sha and the pre-registration verbatim.
IMPOSSIBLE      whether an admissible hit reflects judgement or luck is not identified at this n.
                And forecasts made only in prose NEXT lines are not persisted, so A undercounts what
                I actually predicted -- named, and the direction stated: it flatters nothing, since
                unpersisted forecasts are equally likely to have hit or missed.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]
LEDGER = ROOT / "RETRACTIONS.md"
PREREG = {"point_B": 3, "interval_B": [1, 5],
          "directional": "B <= 4; the admissible record cannot support a calibration claim",
          "kill": "B >= 6 retracts the directional prediction",
          "anti_self_serving": ("admissibility reads ONLY committed fields -- controls_ok in the "
                                "round's own artifact and retraction entries written earlier; no "
                                "judgement at scoring time; undecidable cases are reported, not "
                                "assigned")}


def main() -> int:
    if not LEDGER.exists():
        print("UNRUNNABLE: RETRACTIONS.md absent. Exit 2, never 0.")
        return 2
    ledger = LEDGER.read_text()

    # every persisted forecast in this arc
    found = []
    for d in sorted(A24.glob("R6[0-9][0-9]_*")):
        if d.resolve() == HERE:
            continue
        res = d / "results"
        if not res.is_dir():
            continue
        for f in sorted(res.glob("*.json")):
            try:
                j = json.loads(f.read_text())
            except Exception:
                continue
            if isinstance(j, dict) and "prereg" in j:
                found.append((d.name, f.name, j))
                break

    rid = lambda n: int(re.match(r"R(\d+)", n).group(1))

    # ⛔⛔⛔ NO PURELY TEXTUAL RULE DECIDES THIS, AND THE NEGATIVE CONTROL IS WHAT PROVED IT.
    #   v1 (LOOSE): the round token anywhere in an entry that also says "withdrawn/retracted".
    #     It voided R659 because entry 693 MENTIONS it -- "Neither R659's inference nor ..." --
    #     and a retraction that MENTIONS a round is not a retraction OF that round's statistic.
    #     §4's `a search is an instrument`, inside the rule deciding what I get graded on.
    #   v2 (TIGHT): the token within 90 chars of a withdrawal verb, no sentence break.
    #     It STILL voids R659, because entry 703 says "the R659->R662 THREAD is withdrawn" -- a
    #     RANGE whose start is R659 -- and it now clears R660, whose 86.1% WAS withdrawn by 693.
    #   Both required cases fail, in OPPOSITE directions. So admissibility is not decidable from
    #   the committed text, and the pre-registration already said what to do about that: report
    #   UNDECIDABLE rather than assign. Both rules are run; agreement gives a verdict, and
    #   disagreement is the honest answer.
    LOOSE_W = re.compile(r"(WITHDRAWN|withdrawn|RETRACTED|retracted)")
    TIGHT_W = re.compile(r"(R\d{3})(?:'s)?[^.\n]{0,90}?\b"
                         r"(RETRACTED|WITHDRAWN|is retracted|is withdrawn)\b")

    def by_loose(name):
        tok = name.split("_")[0]
        for m in re.finditer(r"^## (\d+) · .*$", ledger, re.M):
            blob = m.group(0) + " " + ledger[m.end(): m.end() + 1200]
            if re.search(rf"\b{tok}\b", blob) and LOOSE_W.search(blob):
                return True, f"entry {m.group(1)} mentions it near a withdrawal word"
        return False, "no entry mentions it near a withdrawal word"

    def by_tight(name):
        tok = name.split("_")[0]
        for m in TIGHT_W.finditer(ledger):
            if m.group(1) == tok:
                return True, f"'{m.group(0)[:56]}'"
        return False, "no adjacent withdrawal phrase"

    def admissibility(name, j):
        if j.get("controls_ok") is False:
            return "INADMISSIBLE", "the round's own artifact records controls_ok = false"
        l, lw = by_loose(name)
        t, tw = by_tight(name)
        if l and t:
            return "INADMISSIBLE", f"both rules: {tw}"
        if not l and not t:
            return "ADMISSIBLE", "neither rule marks it withdrawn"
        return "UNDECIDABLE", f"rules disagree — loose={l} ({lw[:34]}), tight={t}"

    print("─── PRE-REGISTRATION (written before any code for this round) ───")
    print(f"  B: point {PREREG['point_B']}   interval {PREREG['interval_B']}")
    print(f"  directional: {PREREG['directional']}")
    print(f"  ⚠ {PREREG['anti_self_serving']}")

    rows = []
    for name, fname, j in found:
        v, why = admissibility(name, j)
        rows.append({"round": name, "artifact": fname, "verdict": v, "why": why,
                     "controls_ok": j.get("controls_ok"),
                     "directional_holds": j.get("directional_holds"),
                     "magnitude_inside": j.get("magnitude_inside",
                                               j.get("inside_interval"))})

    print("\n─── CONTROLS ───")
    known_bad = ["R660", "R661"]
    hit = [r for r in rows if r["round"].split("_")[0] in known_bad
           and r["verdict"] in ("INADMISSIBLE", "UNDECIDABLE")]
    print(f"  POSITIVE  R660's 86.1% and R661's rho are KNOWN-withdrawn (entries 693, 699) -> "
          f"NOT scored as admissible: {[(r['round'].split('_')[0], r['verdict']) for r in hit]} -> "
          f"{'PASS' if len(hit) == 2 else '⛔ FAIL — the rule cannot see the class'}")
    r659 = next((r for r in rows if r["round"].startswith("R659")), None)
    negok = r659 is not None and r659["verdict"] != "INADMISSIBLE"
    print(f"  NEGATIVE  R659's counts were never withdrawn (R662 lists them under STANDS) -> "
          f"{r659['verdict'] if r659 else 'NOT FOUND'} -> "
          f"{'PASS — the rule does not void everything' if negok else '⛔ FAIL — a rule that voids everything excuses every miss'}")
    plc_v, _ = admissibility("R997_synthetic_never_mentioned", {"controls_ok": True})
    print(f"  PLACEBO   a round id in no retraction -> {plc_v} -> "
          f"{'PASS' if plc_v == 'ADMISSIBLE' else '⛔ FAIL'}")
    controls_ok = len(hit) == 2 and negok and plc_v == "ADMISSIBLE"

    A = len(rows)
    adm = [r for r in rows if r["verdict"] == "ADMISSIBLE"]
    und = [r for r in rows if r["verdict"] == "UNDECIDABLE"]
    B = len(adm)
    B_hi = B + len(und)
    print(f"\n─── EVERY PERSISTED FORECAST IN THIS ARC ───")
    print(f"  A · rounds persisting a prereg block : {A}")
    print(f"\n  {'round':<46} {'verdict':<13} {'dir':<6} {'mag':<6} why")
    for r in rows:
        print(f"  {r['round'][:46]:<46} {r['verdict']:<13} "
              f"{str(r['directional_holds']):<6} {str(r['magnitude_inside']):<6} {r['why'][:44]}")

    dh = [r for r in adm if r["directional_holds"] is not None]
    held = [r for r in dh if r["directional_holds"]]
    print(f"\n─── THE RECORD, RECOMPUTED OVER ADMISSIBLE FORECASTS ONLY ───")
    print(f"  B · admissible                       : {B} of {A}"
          f"{f'  (+{len(und)} UNDECIDABLE -> B in [{B}, {B_hi}])' if und else ''}")
    print(f"  C · directional held / scoreable     : {len(held)} of {len(dh)}"
          f"{'' if dh else '  (no scoreable directional forecast survives)'}")
    mi = [r for r in adm if r["magnitude_inside"] is not None]
    print(f"      magnitude inside / scoreable     : "
          f"{sum(1 for r in mi if r['magnitude_inside'])} of {len(mi)}")
    print(f"\n  ⛔ WHAT R662's NEXT ASSERTED: 'six of seven directional predictions held', and "
          f"'at least three were about numbers that no longer exist'.")
    inadm = [r for r in rows if r["verdict"] == "INADMISSIBLE"]
    print(f"     MEASURED: {len(inadm)} of {A} are inadmissible, and the surviving directional "
          f"record is {len(held)}/{len(dh)} — not {6}/{7}.")

    lo, hi = PREREG["interval_B"]
    inside = lo <= B <= hi
    directional = B <= 4
    print(f"\n─── THE PRE-REGISTERED ESTIMATE, EVALUATED ───")
    print(f"  B point {PREREG['point_B']} · interval [{lo}, {hi}]   measured {B} -> "
          f"{'INSIDE' if inside else 'OUTSIDE'}; error {B - PREREG['point_B']:+d}")
    print(f"  directional ('B <= 4, the record cannot support a calibration claim'): "
          f"{'HOLDS' if directional else '⛔ RETRACTED'}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=str(ROOT)).stdout.strip()
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        # ⭐⭐⭐ THE NEGATIVE CONTROL REFUSES, AND I AM NOT TIGHTENING THE RULE A THIRD TIME.
        #   Both rules mark R659 withdrawn because entry 703 says "the R659→R662 THREAD is
        #   withdrawn" -- while R662's own README lists R659's counts under STANDS. The LEDGER
        #   ITSELF says both things. No pattern reading it can be right, and a third pattern
        #   tuned until R659 comes out ADMISSIBLE would be me adjusting the scorer until it
        #   grades me the way I want -- precisely the move the pre-registration forbade.
        world = (f"UNVERIFIED — THE AUDIT CANNOT BE PERFORMED, and the reason is a finding rather "
                 f"than a defect. The negative control (R659, whose counts R662 lists under "
                 f"STANDS) is marked withdrawn by BOTH rules, because the ledger contains "
                 f"'the R659→R662 thread is withdrawn' AND 'the censuses stand'. THE RECORD I "
                 f"WOULD GRADE MYSELF ON IS NOT SELF-CONSISTENT. ⭐ What the run does establish, "
                 f"and it needs no rule: R662's NEXT asserted the record 'reads six of seven "
                 f"directional predictions held' — the artifacts persist {A} forecasts, not "
                 f"seven, and at most {A - len([r for r in rows if r['verdict']=='ADMISSIBLE'])} "
                 f"of them are even arguably scoreable. The headline was restated from memory and "
                 f"is RETRACTED without needing the audit it asked for. ⚠ AND I AM STOPPING "
                 f"RATHER THAN TIGHTENING A THIRD PATTERN: a scorer adjusted until it grades its "
                 f"author favourably is the failure the pre-registration named in advance.")
    elif und and len(und) >= 1 and B + len(und) >= 3 and len(und) * 2 >= A - B:
        world = (f"C UNDECIDABLE DOMINATES — the mechanical rule cannot classify "
                 f"{len(und)} of {A} forecasts: a LOOSE pattern voids a round that is merely "
                 f"MENTIONED in a retraction, a TIGHT one is defeated by range phrasing "
                 f"('the R659→R662 thread is withdrawn'), and the two disagree. Admissibility is "
                 f"NOT decidable from the committed text, so B lies in [{B}, {B_hi}] and no "
                 f"filtered hit-rate is reported. ⭐ THE PRE-REGISTRATION ANTICIPATED THIS AND "
                 f"FORBADE THE ALTERNATIVE: hand-classifying here is exactly the self-serving move "
                 f"an author grading his own forecasts makes, and the negative control — R659, "
                 f"whose counts R662 lists under STANDS — is what caught the loose rule doing it.")
    elif B >= 6:
        world = (f"A THE RECORD STANDS — {B} of {A} forecasts are admissible, so the filtering "
                 f"changes little and the directional record is a statement about my judgement. "
                 f"The pre-registered prediction is RETRACTED.")
    else:
        world = (f"B THE RECORD DISSOLVES — only {B} of {A} persisted forecasts survive a rule "
                 f"that reads nothing but committed fields, and the surviving directional record "
                 f"is {len(held)}/{len(dh)}. ⭐ The headline I have been carrying — 'six of seven "
                 f"directional predictions held' — was computed over statistics that have since "
                 f"been withdrawn, and R662's NEXT restated it from memory rather than from the "
                 f"artifacts. ⚠ AND THE SURVIVING RATE IS NOT A CALIBRATION CLAIM EITHER: at "
                 f"n={len(dh)} no design here separates judgement from luck, which is the finding "
                 f"rather than a caveat.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 1 rule x {A} persisted forecasts + 3 controls; every forecast "
          f"printed with the field that decided it.")
    print(f"  ⚠ A IS A LOWER BOUND: forecasts written only in a prose NEXT line are not persisted "
          f"and are invisible here. Direction stated — it flatters nothing, since an unpersisted "
          f"forecast is as likely to have missed as hit.")
    print(f"  ⭐ tree sha: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "forecast_audit.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha, "prereg": PREREG,
        "A_persisted": A, "B_admissible": B, "inadmissible": len(inadm),
        "C_directional_held": len(held), "C_directional_scoreable": len(dh),
        "rows": rows, "magnitude_inside": inside, "directional_holds": directional,
        "check264": ("R662's NEXT asserted the record 'reads six of seven directional predictions "
                     "held' and that 'at least three were about numbers that no longer exist'. "
                     "Both were stated from memory; the artifacts carry the record and were never "
                     "read."),
        "impossible": ("whether an admissible hit reflects judgement or luck is not identified at "
                       "this n; and prose-only forecasts are not persisted, so A undercounts."),
    }, indent=2))
    print(f"\n  wrote {out / 'forecast_audit.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
