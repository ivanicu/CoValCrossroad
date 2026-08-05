#!/usr/bin/env python3
"""
R623 -- what would the automatic anchoring rule flag today, and how much of it is unsatisfiable?

CHECK #222 CAUGHT THE SIXTH FALSE UNIVERSAL, AND THIS ONE IS LOAD-BEARING.
  ⛔ "EVERY round's results JSON already carries its values" -- R622 read 345 artifacts across 614
     rounds, so roughly 56%. A paragraph citing a round with NO artifact can never satisfy the rule
     I proposed, which makes the universal not merely wrong but the thing that decides whether the
     rule is buildable at all. Sixth uncomputed universal in twelve closing lines.

⭐ AND THE ROUND MUST NOT REPEAT R622's CONTAMINATION. R622's g=0 control failed because R621's fake
   value was RECORDED in an artifact and thereby became "anchored". So the planted literal here is
   assembled at runtime and never written to the artifact as a value position -- and the artifact
   says so, rather than leaving a later round to rediscover it.

ESTIMAND        for the proposed rule -- a decimal must match a value position in the artifact of a
                round cited in the SAME paragraph -- the number of (decimal, paragraph) pairs it
                would flag today, decomposed into three causes:
                  C1 NO CITATION       the paragraph cites no round -> the rule is asking the
                                       document to change its prose convention
                  C2 NO ARTIFACT       a round is cited but has no results/*.json -> STRUCTURALLY
                                       unsatisfiable; no amount of correct writing clears it
                  C3 REAL MISMATCH     a cited round HAS an artifact and the value is not in it ->
                                       the only class that is evidence about the number
IDENTIFICATION  Exact given the paragraph split and the citation regex, both reused verbatim from
                the live gate so this measures THAT rule and not a cousin of it. ⚠ The paragraph is
                the binding unit and cannot tie a decimal to a SPECIFIC cited round, so C3 is an
                UPPER bound on real mismatches: a paragraph citing several rounds passes if ANY of
                them carries the value.
SCOPE           population : every decimal >=3 fractional digits in DEFINITION.md and STATEMENT.md
                instrument : same paragraph split and citation regex as statement_provenance
                             instrument unit = A (DECIMAL, PARAGRAPH) PAIR
                             claim unit      = "THIS RULE IS USABLE". NOT equal -- usability is
                             about the AUTHOR's workload, which pairs only proxy. Named, not fixed.
                baseline   : R622's tiers -- T1 18.5%, T2 79.0%, T3 2.5%
                regime     : this repository at this sha
WORLDS          A USABLE: flags are few and dominated by C3. The rule is worth building and its
                  output is about numbers.
                B UNUSABLE BY CONVENTION: C1+C2 dominate. The rule would mostly measure prose
                  formatting and artifact hygiene, so building it would produce a wall of failures
                  that say nothing about whether a number is real -- and the author would be
                  trained to satisfy it by adding citations, not by checking values.
KILL            pre-registered: C3 < 33% of all flags -> world B, do not build the rule as stated.
POSITIVE CTRL   a fabricated decimal planted IN MEMORY into a paragraph that cites an
                artifact-bearing round must flag as C3. Fails at g=0: an unmodified document must
                not produce that same flag.
NEGATIVE CTRL   a T1 value from R622, in its own paragraph, must NOT flag -- otherwise the rule
                condemns the values the current gate already verifies.
PLACEBO         a paragraph citing a round id that does not exist -> C2, not C3, and no crash.
SEEDS           n/a, deterministic.
MULTIPLICITY    every (decimal, paragraph) pair in both documents x 3 causes + 4 controls.
ARTIFACT        results/what_the_automatic_rule_would_flag.json
                ⚠ the planted literal is assembled at runtime and appears in this artifact ONLY
                inside a sentence, never as a value position -- R622's contamination, not repeated.
IMPOSSIBLE      "this flag is a real error" needs a reader per line. C3 is an UPPER bound and the
                paragraph-level binding is why.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
E05 = ROOT / "E05_the_space_of_compilers"
A24 = E05 / "A24_what_the_definition_costs"
DEC = re.compile(r"(?<![\w.])(\d+\.\d{3,4})(?![\w])")
CITE = re.compile(r"R(\d{3})")


def values_of(rid):
    """Value positions in a round's artifacts. None means the round has NO artifact at all --
    a distinction the caller needs, so an empty set and an absent artifact are not merged."""
    ds = list(A24.glob(f"R{rid}_*"))
    if not ds:
        return None
    fs = [f for d in ds for f in (d / "results").glob("*.json")] if ds else []
    if not fs:
        return None
    vals = set()
    def walk(o):
        if isinstance(o, dict):
            for v in o.values(): walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o: walk(v)
        elif isinstance(o, bool) or o is None: return
        elif isinstance(o, (int, float)):
            for f in (repr(o), f"{o:.4f}", f"{o:.3f}", f"{abs(o):.4f}", f"{abs(o):.3f}"):
                vals.add(f.lstrip("+"))
        elif isinstance(o, str) and DEC.fullmatch(o.strip().lstrip("+-")):
            vals.add(o.strip().lstrip("+-"))
    for f in fs:
        try: walk(json.loads(f.read_text(errors="ignore")))
        except Exception: pass
    return vals


CACHE: dict[str, set | None] = {}
def vals(rid):
    if rid not in CACHE: CACHE[rid] = values_of(rid)
    return CACHE[rid]


def classify(text):
    """Apply the proposed rule to a document body. Returns per-cause lists of (dec, cites)."""
    out = {"C1": [], "C2": [], "C3": [], "PASS": []}
    for para in re.split(r"\n\s*\n", text):
        decs = sorted(set(DEC.findall(para)))
        if not decs: continue
        cited = sorted(set(CITE.findall(para)))
        for d in decs:
            if not cited:
                out["C1"].append((d, [])); continue
            sets = [vals(r) for r in cited]
            if all(s is None for s in sets):
                out["C2"].append((d, cited)); continue
            if any(s and d in s for s in sets):
                out["PASS"].append((d, cited))
            else:
                out["C3"].append((d, cited))
    return out


def main():
    docs = {n: (E05 / n).read_text() for n in ("DEFINITION.md", "STATEMENT.md")}
    if not all(docs.values()):
        print("UNRUNNABLE: a document is empty. Exit 2, never 0."); return 2

    # ── artifact coverage, the fact the closing line got wrong ──
    rounds = {m.group(1) for d in A24.glob("R[0-9]*") if (m := re.match(r"R(\d+)", d.name))}
    with_art = {r for r in rounds if vals(r) is not None}
    print(f"─── THE UNIVERSAL THAT WAS FALSE ───")
    print(f"  rounds on disk: {len(rounds)}   carrying a results artifact: {len(with_art)} "
          f"({len(with_art)/len(rounds):.1%})   -> 'every round' is false by "
          f"{len(rounds)-len(with_art)} rounds")

    print(f"\n─── CONTROLS ───")
    host = None
    for para in re.split(r"\n\s*\n", docs["DEFINITION.md"]):
        c = sorted(set(CITE.findall(para)))
        if c and any(vals(r) for r in c): host = (para, c); break
    FAKE = "0." + "7" + "3" + "1" + "9"          # assembled at runtime, never a value position
    pos = classify(host[0] + f"\n\nThe value {FAKE} is asserted here (R{host[1][0]}).") if host else None
    pos_ok = bool(pos) and any(d == FAKE for d, _ in pos["C3"])
    print(f"  POSITIVE  a fabricated decimal planted in a paragraph citing an artifact-bearing "
          f"round flags as C3 -> {'PASS' if pos_ok else '⛔ FAIL'}")
    g0 = classify(host[0]) if host else {"C3": []}
    g0_ok = not any(d == FAKE for d, _ in g0["C3"])
    print(f"  g=0       the same paragraph unmodified does not produce that flag -> "
          f"{'PASS' if g0_ok else '⛔ FAIL'}")
    plc = classify(f"A value 0.4242 appears here (R999).")
    plc_ok = len(plc["C2"]) == 1 and not plc["C3"]
    print(f"  PLACEBO   a paragraph citing a nonexistent round -> "
          f"{'C2, not C3 — PASS' if plc_ok else '⛔ FAIL'}")
    neg = classify("The measured value is 0.5451 (R294).")
    neg_ok = True   # reported, not asserted: see the note below
    print(f"  NEGATIVE  a known T1 value in its own paragraph -> "
          f"{'PASS' if not neg['C3'] else 'flags C3 — reported, and it is the rule condemning a value the CURRENT gate verifies'}")
    controls_ok = pos_ok and g0_ok and plc_ok

    print(f"\n─── WHAT THE RULE WOULD FLAG TODAY ───")
    tot = {"C1": 0, "C2": 0, "C3": 0, "PASS": 0}
    per = {}
    for name, text in docs.items():
        r = classify(text)
        per[name] = {k: len(v) for k, v in r.items()} | {"C3_examples": r["C3"][:8]}
        for k in tot: tot[k] += len(r[k])
        n = sum(len(v) for v in r.values()) or 1
        print(f"  {name:<16} pairs={n:>4}   PASS {len(r['PASS']):>3}   "
              f"C1 no-citation {len(r['C1']):>3}   C2 no-artifact {len(r['C2']):>3}   "
              f"C3 mismatch {len(r['C3']):>3}")
    flags = tot["C1"] + tot["C2"] + tot["C3"]
    share3 = tot["C3"] / flags if flags else 0
    print(f"\n  TOTAL   would-flag {flags} of {flags+tot['PASS']} pairs "
          f"({flags/(flags+tot['PASS']):.1%})   C3 share of flags {share3:.1%}")

    print(f"\n─── VERDICT (threshold pre-registered at C3 >= 33% of flags) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif share3 >= 0.33:
        world = (f"A USABLE — C3 is {share3:.1%} of flags, so most of what the rule says is about "
                 f"whether a number is in the artifact it cites")
    else:
        world = (f"B UNUSABLE AS STATED — C1+C2 are {1-share3:.1%} of {flags} flags. The rule would "
                 f"mostly measure PROSE CONVENTION and ARTIFACT HYGIENE, and an author facing it "
                 f"would be trained to add citations rather than to check values.")
    print(f"  {world}")
    print(f"\n  ⚠ C3 IS AN UPPER BOUND: the paragraph is the binding unit, so a paragraph citing "
          f"several rounds passes if ANY carries the value, and a decimal cannot be tied to a "
          f"specific cited round without syntax the documents do not have.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "what_the_automatic_rule_would_flag.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "rounds_on_disk": len(rounds), "rounds_with_artifact": len(with_art),
        "totals": tot, "flags": flags, "c3_share_of_flags": round(share3, 4),
        "per_document": per,
        "check222": ("the closing line said EVERY round's results JSON carries its values; "
                     f"{len(with_art)} of {len(rounds)} rounds have an artifact. Sixth uncomputed "
                     "universal in twelve closing lines."),
        "contamination_note": ("the planted literal is assembled at runtime and appears in this "
                               "artifact only inside this sentence, never as a value position, so "
                               "R622's g=0 failure is not repeated"),
        "impossible": "C3 is an upper bound; the paragraph cannot bind a decimal to one cited round",
    }, indent=2))
    print(f"\n  wrote {OUT / 'what_the_automatic_rule_would_flag.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
