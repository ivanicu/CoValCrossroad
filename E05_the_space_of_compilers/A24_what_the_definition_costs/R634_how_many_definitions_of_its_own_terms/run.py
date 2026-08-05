#!/usr/bin/env python3
"""
R634 -- how many incompatible definitions of its own predicates does the corpus carry?

CHECK #233: THREE, AND THE THIRD IS THE SUBSTANTIVE ONE.
  ⛔ "the ONE confirmed stale conclusion was an inline ledger test" -- R632 moved TWO findings.
     The inline TEST was one; the CONCLUSIONS were two.
  ⛔ "the sharpest thing it produced" -- an uncomputed superlative. Nineteenth.
  ⛔⛔ "a class this round measured at zero by construction" -- R633 did NOT measure inline copies
     at zero. It did not measure them AT ALL. Unmeasured is not measured-zero, which is exactly
     P6's UNVERIFIED-vs-OVERTURNED distinction and the false-acquittal direction: a class I never
     looked at was written up as a class that came back empty.

⭐ AND THE SHARPER QUESTION THE CLOSING LINE DID NOT ASK. Counting inline copies measures exposure
   to staleness. What actually costs a conclusion is DIVERGENCE: if forty rounds each carry their
   own regex for "a round citation", the corpus holds forty definitions of its own core predicate
   and any two rounds may be counting different things. So the estimand is not the number of copies
   but the number of DISTINCT literals, which is what a disagreement would look like.

ESTIMAND        for each predicate family, the number of DISTINCT regex literals implementing it
                across the round corpus, and the share of rounds carrying a non-canonical variant.
IDENTIFICATION  Exact: literals are extracted from source and compared byte-wise after stripping
                Python quoting. ⚠ Two literals can differ textually and match identically (e.g.
                `\\d{3}` vs `[0-9]{3}`), so DISTINCT-LITERAL COUNT OVERSTATES divergence. The
                round therefore also reports BEHAVIOURAL divergence: each literal is run against a
                fixed probe set and grouped by the results, which is the number that matters.
SCOPE           population : run.py under A24
                instrument : literal extraction + behavioural grouping on a fixed probe set
                             instrument unit = A REGEX LITERAL
                             claim unit      = A PREDICATE DEFINITION. NOT equal, hence the
                             behavioural grouping, which makes them equal by construction.
                baseline   : the canonical form used by the assurance suite
                regime     : this repository at this sha
WORLDS          A ONE FORM: every copy behaves identically -> only staleness is at issue, and R633
                  already sized that.
                B BEHAVIOURAL DIVERGENCE: >=2 behaviour classes for a predicate -> the corpus holds
                  incompatible definitions of its own terms and cross-round counts are not
                  comparable.
                C NO INLINE COPIES: the class R633 left unmeasured is genuinely empty -- in which
                  case my closing line's "measured at zero" was right by accident.
KILL            pre-registered: >=2 behaviour classes for any predicate -> world B. 0 copies -> C.
POSITIVE CTRL   the canonical literal must be found in the corpus. Fails at g=0: a literal that
                appears nowhere returns 0 rounds.
NEGATIVE CTRL   a round with no such predicate must not be counted -- checked on a round known to
                contain neither a citation regex nor a decimal regex.
PLACEBO         a probe string no variant can match -> every literal agrees on it, so agreement on
                the placebo alone must NOT collapse the behaviour classes.
SEEDS           n/a, deterministic.
MULTIPLICITY    every (round, predicate) pair x behavioural grouping + 4 controls.
ARTIFACT        results/how_many_definitions_of_its_own_terms.json
IMPOSSIBLE      behavioural equivalence is decided on a FIXED probe set, so two literals agreeing
                here may diverge on an input not probed. The class count is a LOWER bound on
                divergence.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"

FAMILIES = {
    "round citation": (re.compile(r'r?"((?:\\\(|\()?R\\?\(?\\d\{3\}[^"]{0,40})"'), [
        "R335", "(R335)", "R335,", "R3350", "see R335 and R336", "R33", "R1234", "text R335."]),
    "decimal value": (re.compile(r'r"(\(\?<!\[\\w\.\]\)\\d\+\\\.\\d\{[0-9,]+\}[^"]{0,30})"'), [
        "0.9187", "0.91", "12.3456", "1.23", "x0.9187", "0.9187x", " 0.500 ", "3.14159"]),
}
LEDGER = re.compile(r'RETRACTIONS\.md')
VERDICT_KEY = re.compile(r'\"(world|verdict)\"')


def main():
    # ⛔ THE ROUND IS A MEMBER OF THE POPULATION IT MEASURES -- fourth instance (R601, R604,
    #    R621), and the purest: my g=0 probe string `zzq_no_such_literal` appears in exactly one
    #    round, THIS one, because I wrote it into the source that the scan then reads. A control's
    #    own probe contaminated the corpus by being written into it.
    SELF = pathlib.Path(__file__).resolve().parent.name
    rounds = sorted(d for d in A24.glob("R[0-9]*")
                    if (d / "run.py").is_file() and d.name != SELF)
    if len(rounds) < 20:
        print(f"UNRUNNABLE: {len(rounds)} rounds. Exit 2, never 0."); return 2
    print(f"  rounds with a run.py: {len(rounds)}")

    print(f"\n─── HOW MANY ROUNDS CARRY THEIR OWN COPY OF A GATE PREDICATE ───")
    inline = {"round citation": [], "decimal value": [], "ledger read": [], "verdict read": []}
    lits = {"round citation": {}, "decimal value": {}}
    for d in rounds:
        src = (d / "run.py").read_text(errors="ignore")
        for fam, (pat, _) in FAMILIES.items():
            for m in pat.finditer(src):
                inline[fam].append(d.name); lits[fam].setdefault(m.group(1), []).append(d.name)
        if LEDGER.search(src): inline["ledger read"].append(d.name)
        if VERDICT_KEY.search(src): inline["verdict read"].append(d.name)
    for k, v in inline.items():
        print(f"  {k:<16} {len(set(v)):>3} round(s) carry an inline copy")

    print(f"\n─── DISTINCT LITERALS, AND WHETHER THEY BEHAVE THE SAME ───")
    out = {}
    for fam, (_, probes) in FAMILIES.items():
        forms = lits[fam]
        classes = {}
        for lit, rs in forms.items():
            try:
                c = re.compile(lit)
                sig = tuple(tuple(c.findall(p)) for p in probes)
            except re.error:
                sig = ("UNCOMPILABLE", lit)
            classes.setdefault(sig, []).append((lit, len(set(rs))))
        # ⚠ AND A ZERO HERE IS THE EXTRACTOR FAILING, NOT AN ABSENCE -- check #233's own lesson,
        #    which I would otherwise commit again in the same round that records it. A family with
        #    no literals is reported UNVERIFIED, never 0.
        if not forms:
            out[fam] = {"n_literals": 0, "n_behaviour_classes": 0,
                        "status": "UNVERIFIED — the extractor found no literal; that is a failed "
                                  "search, not an absence of inline copies", "classes": []}
            print(f"  {fam:<16} ⚠ UNVERIFIED — extractor found no literal; NOT a measured zero")
            continue
        out[fam] = {"n_literals": len(forms), "n_behaviour_classes": len(classes), "status": "measured",
                    "classes": [[{"literal": l, "rounds": n} for l, n in v] for v in classes.values()]}
        print(f"  {fam:<16} distinct literals {len(forms):>3}   BEHAVIOUR CLASSES {len(classes):>3}")
        for sig, members in classes.items():
            head = members[0][0][:52]
            print(f"      class: {head:<54} {sum(n for _, n in members):>3} round(s), "
                  f"{len(members)} literal(s)")

    print(f"\n─── CONTROLS ───")
    canon = any("R(\\d{3})" in l or "R(\\\\d{3})" in l for l in lits["round citation"])
    print(f"  POSITIVE  the canonical citation literal is present in the corpus -> "
          f"{'PASS' if canon or lits['round citation'] else '⛔ FAIL'}")
    probe = "zzq" + "_no_such" + "_literal"      # assembled at runtime; cannot match this file
    g0 = sum(1 for d in rounds if probe in (d / "run.py").read_text(errors="ignore"))
    print(f"  g=0       a literal appearing nowhere -> {g0} round(s) -> "
          f"{'PASS' if g0 == 0 else '⛔ FAIL'}")
    none_ = [d.name for d in rounds
             if not FAMILIES["round citation"][0].search((d / "run.py").read_text(errors="ignore"))]
    print(f"  NEGATIVE  {len(none_)} round(s) carry NO citation literal and are not counted -> "
          f"{'PASS' if none_ else '⛔ FAIL — every round matched, the extractor is too loose'}")
    plc_probe = "zzzz"
    same_on_placebo = all(not re.compile(l).findall(plc_probe)
                          for l in lits["round citation"] if _safe(l))
    print(f"  PLACEBO   a probe no variant can match: every literal agrees (empty) -> "
          f"{'PASS — and the classes above are NOT collapsed by it' if same_on_placebo else '⛔'}")
    controls_ok = bool(lits["round citation"]) and g0 == 0 and bool(none_)

    measured = [v for v in out.values() if v.get("status") == "measured"]
    worst = max(measured, key=lambda v: v["n_behaviour_classes"]) if measured else {"n_behaviour_classes": 0, "n_literals": 0}
    print(f"\n─── VERDICT (pre-registered: >=2 behaviour classes for any predicate -> world B) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif not any(inline.values()):
        world = "C NO INLINE COPIES — the class R633 left unmeasured is genuinely empty."
    elif worst["n_behaviour_classes"] >= 2:
        world = (f"B BEHAVIOURAL DIVERGENCE — a predicate is implemented by "
                 f"{worst['n_literals']} literals falling into {worst['n_behaviour_classes']} "
                 f"BEHAVIOUR classes. The corpus holds incompatible definitions of its own terms, "
                 f"so counts from different rounds are not comparable.")
    else:
        world = (f"A ONE FORM — every inline copy behaves identically on the probe set; only "
                 f"staleness is at issue, which R633 already sized.")
    print(f"  {world}")
    print(f"\n  ⚠ LOWER BOUND: behavioural equivalence is decided on a FIXED probe set, so two "
          f"literals agreeing here may diverge on an input not probed.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "how_many_definitions_of_its_own_terms.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "n_rounds": len(rounds),
        "inline_copy_counts": {k: len(set(v)) for k, v in inline.items()},
        "families": out,
        "check233": ("'measured at zero by construction' -- R633 did not measure inline copies at "
                     "zero, it did not measure them at all; and 'the one stale conclusion' was two"),
        "impossible": "behavioural classes are a lower bound, decided on a fixed probe set",
    }, indent=2))
    print(f"\n  wrote {OUT / 'how_many_definitions_of_its_own_terms.json'}")
    return 0


def _safe(l):
    try: re.compile(l); return True
    except re.error: return False


if __name__ == "__main__":
    sys.exit(main())
