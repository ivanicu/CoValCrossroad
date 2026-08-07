#!/usr/bin/env python3
"""
R624 -- the binding unit is a specification axis, and looseness is the price of usability

CHECK #223 FOUND A UNIVERSAL AND A FALSE PREMISE, AND THE PREMISE IS WHAT THIS ROUND IS.
  ⛔ "EVERY remaining design needs the document to bind a decimal to a specific round" -- a
     universal over a set I never enumerated (I had named two). Seventh in fourteen closing lines.
  ⛔ "which no current syntax does" -- FALSE, and checked against the object rather than argued:
     DEFINITION.md carries 45 `## R###` section headings, which ARE a binding. STATEMENT.md carries
     0. So the binding exists, in one document, at SECTION granularity -- and the previous round
     declared it absent while appending to it every round.

⭐ THE TENSION THIS ROUND EXISTS TO MEASURE, stated before any number. A looser binding unit reduces
   false flags AND reduces evidential strength, and those move together by construction. At document
   scope the rule degenerates to R622's T2 -- "the value is in SOME artifact" -- which passes nearly
   everything. So a usable C3 share is worthless on its own; it must be read against how much the
   looser unit is passing that the strictest one would flag. Reporting one without the other is how
   a lax gate gets sold as a working one.

ESTIMAND        for each binding unit u in {paragraph, section, document}, jointly:
                  (a) C3's share of flags -- is the output about numbers?
                  (b) the pass rate -- how much is u buying by being lax?
                  (c) LAXITY = pairs that pass under u but flag under the strictest unit
IDENTIFICATION  Exact given the three scopes. ⚠ (a) and (b) are NOT independent: a coarser unit
                mechanically raises both, so neither alone identifies usability, and the round
                reports the pair as a frontier rather than picking a winner by (a).
SCOPE           population : every decimal >=3 fractional digits in DEFINITION.md and STATEMENT.md
                instrument : R623's classifier with the binding scope swapped
                             instrument unit = A (DECIMAL, SCOPE) PAIR
                             claim unit      = "THIS RULE IS USABLE" -- still not equal, still a
                             proxy for author workload, unchanged from R623 and restated not hidden
                baseline   : R623's paragraph row -- 50.8% flagged, C3 16.0% of flags
                regime     : this repository at this sha
WORLDS          A A USABLE UNIT EXISTS: some scope has C3 dominant among flags WITHOUT passing
                  nearly everything -- the rule is buildable at that scope.
                B USABILITY IS BOUGHT WITH LAXITY: every scope with C3 >= 33% also passes >90% of
                  pairs, so the only way to make the output about numbers is to stop asking.
KILL            pre-registered, both clauses required for world A: C3 share >= 33% AND pass rate
                <= 90%. Any scope meeting only one is reported as LAX, never as usable.
POSITIVE CTRL   a fabricated decimal planted in memory inside an R-headed section must flag C3 at
                section scope. Fails at g=0: the unmodified section must not produce that flag.
NEGATIVE CTRL   a T1 value in its own R-headed section must not flag -- R623 showed the paragraph
                rule condemns one, and whether section scope repairs that is the point.
PLACEBO         a section headed with a nonexistent round -> C2, never C3.
SEEDS           n/a, deterministic.
MULTIPLICITY    3 scopes x every pair x 3 causes, both documents, plus 4 controls. All reported.
ARTIFACT        results/binding_unit_curve.json
                ⚠ the planted literal is assembled at runtime and never persisted as a value
                position -- R622's contamination, still not repeated.
IMPOSSIBLE      "this flag is a real error" needs a reader per line, at every scope. C3 remains an
                UPPER bound and grows looser as the scope widens, which is why (c) is reported.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
E05 = ROOT / "E05_the_space_of_compilers"
A24 = E05 / "A24_what_the_definition_costs"
DEC = re.compile(r"(?<![\w.])(\d+\.\d{3,4})(?![\w])")
CITE = re.compile(r"R(\d{3})")
HEAD = re.compile(r"^##+ .*?R(\d{3})", re.M)

CACHE: dict[str, set | None] = {}


def vals(rid):
    if rid in CACHE: return CACHE[rid]
    ds = list(A24.glob(f"R{rid}_*"))
    fs = [f for d in ds for f in (d / "results").glob("*.json")]
    if not fs:
        CACHE[rid] = None; return None
    out = set()
    def walk(o):
        if isinstance(o, dict):
            for v in o.values(): walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o: walk(v)
        elif isinstance(o, bool) or o is None: return
        elif isinstance(o, (int, float)):
            for f in (repr(o), f"{o:.4f}", f"{o:.3f}", f"{abs(o):.4f}", f"{abs(o):.3f}"):
                out.add(f.lstrip("+"))
        elif isinstance(o, str) and DEC.fullmatch(o.strip().lstrip("+-")):
            out.add(o.strip().lstrip("+-"))
    for f in fs:
        try: walk(json.loads(f.read_text(errors="ignore")))
        except Exception: pass
    CACHE[rid] = out
    return out


def chunks(text, scope):
    if scope == "paragraph":
        return re.split(r"\n\s*\n", text)
    if scope == "document":
        return [text]
    # section: split at any heading, and a chunk inherits the round in its OWN heading
    parts, cur = [], []
    for line in text.split("\n"):
        if re.match(r"^##+ ", line) and cur:
            parts.append("\n".join(cur)); cur = [line]
        else:
            cur.append(line)
    if cur: parts.append("\n".join(cur))
    return parts


def classify(text, scope):
    out = {"C1": [], "C2": [], "C3": [], "PASS": []}
    for ch in chunks(text, scope):
        decs = sorted(set(DEC.findall(ch)))
        if not decs: continue
        cited = sorted(set(HEAD.findall(ch)) | set(CITE.findall(ch))) if scope == "section" \
                else sorted(set(CITE.findall(ch)))
        for d in decs:
            if not cited: out["C1"].append(d); continue
            sets = [vals(r) for r in cited]
            if all(s is None for s in sets): out["C2"].append(d); continue
            (out["PASS"] if any(s and d in s for s in sets) else out["C3"]).append(d)
    return out


def main():
    docs = {n: (E05 / n).read_text() for n in ("DEFINITION.md", "STATEMENT.md")}
    heads = {n: len(HEAD.findall(t)) for n, t in docs.items()}
    print(f"─── THE PREMISE THAT WAS FALSE ───")
    print(f"  R-headed sections: DEFINITION.md {heads['DEFINITION.md']}   "
          f"STATEMENT.md {heads['STATEMENT.md']}   -> the binding EXISTS, in one document")

    print(f"\n─── CONTROLS (at section scope, the new unit) ───")
    sec = next((c for c in chunks(docs["DEFINITION.md"], "section")
                if HEAD.findall(c) and vals(HEAD.findall(c)[0])), None)
    FAKE = "0." + "8" + "6" + "4" + "1"
    if sec is None:
        print("  UNRUNNABLE: no R-headed section with an artifact. Exit 2, never 0."); return 2
    pos = FAKE in classify(sec + f"\n\nThe value {FAKE} is asserted here.", "section")["C3"]
    print(f"  POSITIVE  a fabricated decimal planted in an R-headed section flags C3 -> "
          f"{'PASS' if pos else '⛔ FAIL'}")
    g0 = FAKE not in classify(sec, "section")["C3"]
    print(f"  g=0       the same section unmodified does not produce that flag -> "
          f"{'PASS' if g0 else '⛔ FAIL'}")
    p = classify("## R999 · nothing\n\nA value 0.4242 appears here.", "section")
    plc = len(p["C2"]) == 1 and not p["C3"]
    print(f"  PLACEBO   a section headed with a nonexistent round -> "
          f"{'C2, not C3 — PASS' if plc else '⛔ FAIL'}")
    ncl = classify("## R294 · a value\n\nThe measured value is 0.5451.", "section")
    neg = not ncl["C3"]
    print(f"  NEGATIVE  a T1 value in its own R-headed section -> "
          f"{'does not flag — PASS, section scope repairs R623 case' if neg else '⛔ still flags C3 — section scope does NOT repair it'}")
    controls_ok = pos and g0 and plc

    print(f"\n─── THE SPECIFICATION CURVE OVER THE BINDING UNIT ───")
    strict = {n: set(classify(t, "paragraph")["C3"] + classify(t, "paragraph")["C1"]
                     + classify(t, "paragraph")["C2"]) for n, t in docs.items()}
    print(f"  {'scope':<10} {'pairs':>6} {'pass%':>7} {'flags':>6} {'C1':>5} {'C2':>4} {'C3':>4} "
          f"{'C3/flags':>9} {'laxity':>7}")
    curve = []
    for scope in ("paragraph", "section", "document"):
        tot = {"C1": 0, "C2": 0, "C3": 0, "PASS": 0}
        lax = 0
        for n, t in docs.items():
            r = classify(t, scope)
            for k in tot: tot[k] += len(r[k])
            lax += len(set(r["PASS"]) & strict[n])
        pairs = sum(tot.values()); flags = pairs - tot["PASS"]
        share = tot["C3"] / flags if flags else 0.0
        rate = tot["PASS"] / pairs if pairs else 0.0
        curve.append({"scope": scope, "pairs": pairs, "pass_rate": round(rate, 4),
                      "flags": flags, **{k: tot[k] for k in ("C1", "C2", "C3")},
                      "c3_share": round(share, 4), "laxity_vs_strictest": lax})
        print(f"  {scope:<10} {pairs:>6} {rate:>6.1%} {flags:>6} {tot['C1']:>5} {tot['C2']:>4} "
              f"{tot['C3']:>4} {share:>8.1%} {lax:>7}")

    print(f"\n─── VERDICT (BOTH clauses required: C3 share >= 33% AND pass rate <= 90%) ───")
    ok = [c for c in curve if c["c3_share"] >= 0.33 and c["pass_rate"] <= 0.90]
    lax_only = [c for c in curve if c["c3_share"] >= 0.33 and c["pass_rate"] > 0.90]
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif ok:
        world = (f"A A USABLE UNIT EXISTS — {', '.join(c['scope'] for c in ok)}: C3 dominant among "
                 f"flags without passing nearly everything. The rule is buildable at that scope.")
    elif lax_only:
        world = (f"B USABILITY IS BOUGHT WITH LAXITY — {', '.join(c['scope'] for c in lax_only)} "
                 f"reaches C3 >= 33% only by passing >90% of pairs. The output becomes about "
                 f"numbers by ceasing to ask about most of them.")
    else:
        world = (f"NEITHER — no scope reaches C3 >= 33% at any pass rate; the binding unit is not "
                 f"the axis that decides this")
    print(f"  {world}")
    print(f"\n  ⚠ LAXITY IS THE COLUMN THAT MATTERS: pairs a scope PASSES that the strictest scope "
          f"FLAGS. A high C3 share with high laxity is a gate that stopped asking, not one that "
          f"got better.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "binding_unit_curve.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "r_headed_sections": heads,
        "curve": curve, "negative_control_repaired_by_section_scope": bool(neg),
        "check223": ("'every remaining design' was a universal over an unenumerated set, and 'no "
                     "current syntax binds a decimal to a round' was false -- DEFINITION.md has 45 "
                     "`## R###` sections and I had been appending to them every round"),
        "impossible": "C3 is an upper bound at every scope and loosens as the scope widens",
    }, indent=2))
    print(f"\n  wrote {OUT / 'binding_unit_curve.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
