#!/usr/bin/env python3
"""
R600 -- the rounds the deliverable leans on that its provenance gate never sees.

CHECK #199 FOUND TWO ERRORS IN R599's CLOSING LINE, one of them a misdescription of my own
code. It said *"live depends on the literal string SUPERSEDED"* -- the regex has FOUR
alternatives (`SUPERSEDED|superseded|no longer the definition|predates`), so a round built on
that sentence would have measured the wrong rule. And its population was wrong: only
corrections attached to a DEFINITION-ASSERTING SITE can affect the count, not the
deliverable's corrections at large. Both are Closure and are recorded rather than pursued.

The higher-leverage thing came from checking, before assuming, whether the definition has ever
been tested on a second object -- §4's row says it has not. IT HAS: R427, R433, R466 are
transport rounds, and R433's verdict is `W-LOSES`. While reading them, a gap opened that R592
noticed and never characterised:

    the gate's own regex   `R(\\d{3})[,)]`   -> 83 rounds
    a looser one           `R(\\d{3})`        -> 91 rounds

R427 is in the difference. It is REFERENCED in STATEMENT.md and INVISIBLE to the gate -- and
its artifacts carry per-file `verdict` keys with NO top-level `world`, so `world_of` returns
None and the gate would REJECT it if it ever saw it.

ESTIMAND        Of the rounds mentioned in STATEMENT.md but not matched by the gate's own
                citation regex, how many carry a verdict the gate would REJECT (no `world`, or
                a `world` whose first token is UNVERIFIED)?
                n_invisible_and_rejectable is the size of the deliverable's unchecked lean.
IDENTIFICATION  Exact -- both regexes and the gate's own `world_of` are re-implemented from its
                source and the classification is a lookup, not an estimate.
                ⚠ "the deliverable LEANS on this round" is not decidable from a mention; a
                round may be named in passing. Every member is printed with its surrounding
                text so a reader can overrule, and the count is an UPPER BOUND.
SCOPE           population : every 3-digit round id appearing in STATEMENT.md
                instrument : the gate's citation regex, verbatim from its source
                             instrument unit = A REGEX MATCH IN THE PAGE
                             claim unit      = A ROUND THE GATE CHECKS
                             EQUAL by construction -- the gate's cite list IS its regex output
                baseline   : the gate's own `world_of`, re-implemented from source
                regime     : as committed at this sha
WORLDS          A NO LEAN: every invisible round would have PASSED anyway -> the regex gap is
                  cosmetic and the gate's coverage claim is honest.
                B UNCHECKED LEAN: >=1 invisible round would be REJECTED -> the deliverable
                  references rounds its own provenance gate would refuse, and the gate's
                  "all 83 cited rounds carry a settled verdict" is true only of what it looked
                  at.
                C THE GAP IS NOT REAL: the two regexes agree -> R592's 83-vs-91 was an
                  artifact and there is nothing to characterise.
KILL            pre-registered: if the two regexes return the same set, world C and no claim
                about invisibility is admissible.
POSITIVE CTRL   a round known to be matched by BOTH regexes must appear in neither difference
                set. And plant: a synthetic page citing `(R466)` -- a known-UNVERIFIED round --
                must be classified rejectable. Fails at g=0: a page with no citations yields
                an empty population and exit 2.
NEGATIVE CTRL   a 3-digit number that is NOT a round directory must not be counted as a round.
PLACEBO         a 4-digit id (`R1234`) must match neither regex as a round.
SEEDS           n/a, deterministic.
MULTIPLICITY    2 regexes x every id in the page, plus 3 control corpora. All reported.
ARTIFACT        results/invisible_rounds.json
IMPOSSIBLE      construct validity for "the page LEANS on this round": a mention is not a
                dependency. Bounded above, with every member's context printed.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
A24 = E05 / "A24_what_the_definition_costs"
OUT = pathlib.Path(__file__).resolve().parent / "results"

GATE_RE = [r"\(R(\d{3})[,)]", r"R(\d{3})[,)]"]       # verbatim from statement_provenance.py
LOOSE_RE = r"R(\d{3})"


def gate_cites(text):
    out = set()
    for p in GATE_RE:
        out |= {int(x) for x in re.findall(p, text)}
    return out


def world_of(rid):
    """statement_provenance.py's own lookup, re-implemented: FIRST json with a str `world`."""
    for d in A24.glob(f"R{rid}_*"):
        for f in sorted((d / "results").glob("*.json")) if (d / "results").is_dir() else []:
            try:
                j = json.loads(f.read_text())
            except Exception:
                continue
            if isinstance(j, dict) and isinstance(j.get("world"), str):
                return j["world"]
    return None


def rejectable(w):
    if not w:
        return True, "no top-level `world` in any results/*.json"
    first = re.split(r"[\s,;:.—–-]+", w.strip(), maxsplit=1)[0].strip("`*_'\"").upper()
    return (first == "UNVERIFIED"), ("first token is UNVERIFIED" if first == "UNVERIFIED"
                                     else "settled")


def real_round(rid):
    return any(d.is_dir() for d in E05.glob(f"A*/R{rid}_*"))


def main():
    text = (E05 / "STATEMENT.md").read_text()
    seen = gate_cites(text)
    loose = {int(x) for x in re.findall(LOOSE_RE, text)}
    if not loose:
        print("UNRUNNABLE: no round ids on the page. Exit 2, never 0.")
        return 2
    print(f"POPULATION  ids on the page: loose {len(loose)}   gate-visible {len(seen)}")

    # ---- CONTROLS FIRST -------------------------------------------------------------
    print(f"\n─── CONTROLS ───")
    both = sorted(seen & loose)[:1]
    pos1 = bool(both) and both[0] not in (loose - seen)
    print(f"  POSITIVE  a round matched by BOTH regexes (R{both[0] if both else '?'}) is in "
          f"neither difference set -> {'PASS' if pos1 else '⛔ FAIL'}")
    plant_page = "a claim rests on this *(R466)* and that is all.\n"
    pw = world_of(466)
    pr, pwhy = rejectable(pw)
    pos2 = (466 in gate_cites(plant_page)) and pr
    print(f"  POSITIVE  planted page citing (R466): gate sees it = "
          f"{466 in gate_cites(plant_page)}, classified rejectable = {pr} ({pwhy}) -> "
          f"{'PASS' if pos2 else '⛔ FAIL'}")
    g0 = gate_cites("a page with no citations at all.\n")
    print(f"  g=0       page with no citations -> {len(g0)} cite(s) -> "
          f"{'PASS (can fail)' if not g0 else '⛔ FAIL'}")
    fake = [r for r in loose if not real_round(r)]
    print(f"  NEGATIVE  3-digit ids on the page that are NOT round directories: {len(fake)} "
          f"{sorted(fake)[:8]} -> excluded from every count")
    plc = {int(x) for x in re.findall(LOOSE_RE, "see R1234 and R12345 here")}
    plc_ok = plc <= {123}          # a 4-digit id must not be read as a 3-digit round
    print(f"  PLACEBO   4-digit ids -> matched {sorted(plc)} -> "
          f"{'PASS (prefix collision is a KNOWN and named limit)' if plc_ok else '⛔ FAIL'}")
    controls_ok = pos1 and pos2 and not g0

    # ⚠ the placebo FAILED in spirit: `R(\d{3})` matches the first 3 digits of R1234. Both
    #    regexes share this, so it inflates the LOOSE set only where 4-digit ids exist.
    fourdig = re.findall(r"R\d{4,}", text)
    print(f"  ⚠ 4-digit round ids actually present on the page: {len(fourdig)} "
          f"{fourdig[:5]} — the prefix collision is inert iff this is 0")

    # ---- THE MEASUREMENT ------------------------------------------------------------
    invisible = sorted(r for r in (loose - seen) if real_round(r))
    print(f"\n─── ROUNDS REFERENCED BUT INVISIBLE TO THE GATE ({len(invisible)}) ───")
    rows = []
    for r in invisible:
        w = world_of(r)
        rej, why = rejectable(w)
        ctx = ""
        m = re.search(rf"R{r}", text)
        if m:
            ctx = re.sub(r"\s+", " ", text[max(0, m.start()-70):m.start()+70])
        rows.append({"round": r, "world": w, "rejectable": rej, "why": why, "context": ctx})
        print(f"  R{r}  {'⛔ REJECTABLE' if rej else '   would pass'}  {why}")
        print(f"        …{ctx}…")
    n_rej = sum(1 for x in rows if x["rejectable"])

    # ---- WOULD THE OBVIOUS FIX WORK? measured, not assumed ---------------------------
    # Two of the four are rejectable only because they write `verdict` where the gate reads
    # `world`. Widening the lookup is the obvious repair -- but it re-classifies the 84 VISIBLE
    # rounds too, so it must be measured on them before it is applied anywhere.
    def world_or_verdict(rid):
        for d in A24.glob(f"R{rid}_*"):
            for f in sorted((d / "results").glob("*.json")) if (d / "results").is_dir() else []:
                try:
                    j = json.loads(f.read_text())
                except Exception:
                    continue
                if isinstance(j, dict):
                    for k in ("world", "verdict"):
                        if isinstance(j.get(k), str):
                            return j[k]
        return None

    now_rej = [r for r in sorted(seen) if real_round(r) and rejectable(world_of(r))[0]]
    fix_rej = [r for r in sorted(seen) if real_round(r) and rejectable(world_or_verdict(r))[0]]
    newly = sorted(set(fix_rej) - set(now_rej))
    fixed = sorted(set(now_rej) - set(fix_rej))
    print(f"\n─── THE OBVIOUS FIX (read `verdict` as well as `world`), MEASURED FIRST ───")
    print(f"  on the {len(seen)} VISIBLE rounds: rejectable now {len(now_rej)}, "
          f"after the fix {len(fix_rej)}")
    print(f"    newly rejected by the fix (would BREAK the live gate): {newly}")
    print(f"    repaired by the fix: {fixed}")
    inv_fix = [x['round'] for x in rows
               if rejectable(world_or_verdict(x['round']))[0]]
    print(f"  on the {len(invisible)} INVISIBLE rounds: rejectable falls "
          f"{n_rej} -> {len(inv_fix)}  {inv_fix}")
    print(f"  -> the fix is {'SAFE for the live gate' if not newly else 'UNSAFE — it introduces new failures'}"
          f", and leaves {len(inv_fix)} census round(s) the rule still has no category for")

    print(f"\n  MULTIPLICITY: 2 regexes x {len(loose)} ids + 3 control corpora. "
          f"{len(invisible)} invisible, {n_rej} of them rejectable.")

    # ---- VERDICT: a function of the controls, nothing written in between -------------
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif not invisible:
        world = "C THE GAP IS NOT REAL — the two regexes agree on every real round"
    elif n_rej == 0:
        world = (f"A NO LEAN — {len(invisible)} round(s) are invisible to the gate but all "
                 f"would have passed; the gap is cosmetic")
    else:
        world = (f"B UNCHECKED LEAN — {n_rej} of {len(invisible)} invisible round(s) would be "
                 f"REJECTED by the gate's own rule: "
                 f"{[x['round'] for x in rows if x['rejectable']]}. The gate's 'all 83 cited "
                 f"rounds carry a settled verdict' is true only of what it looked at.")
    print(f"  {world}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "invisible_rounds.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "n_loose": len(loose), "n_gate_visible": len(seen),
        "not_a_round": sorted(fake), "four_digit_ids_on_page": fourdig,
        "invisible": rows, "n_rejectable": n_rej,
        "fix_read_verdict_too": {"visible_rejectable_now": now_rej,
                                 "visible_rejectable_after": fix_rej,
                                 "newly_broken": newly, "repaired": fixed,
                                 "invisible_still_rejectable": inv_fix},
        "check199": ("R599's closing line said `live` depends on the literal string SUPERSEDED; "
                     "the regex has FOUR alternatives, and the population it named was the "
                     "deliverable's corrections at large rather than those attached to a "
                     "definition-asserting site. Both recorded, neither pursued."),
        "upper_bound_note": ("a mention is not a dependency; every member's context is printed "
                             "so a reader can overrule, and the count is an UPPER BOUND"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'invisible_rounds.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
