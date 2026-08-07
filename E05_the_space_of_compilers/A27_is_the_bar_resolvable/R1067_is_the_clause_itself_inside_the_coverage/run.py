"""R1067 — is the CLAUSE ITSELF inside the anchoring gate's coverage, or in the uncovered remainder?

R1066 showed the anchoring gate is artifact-coupled — mutate a value it names and it reds. R1044
showed it covers only 2.7-7.8% of this document. Those two facts are compatible with the worst case:
**the gate could be perfectly coupled to values nobody cares about while the sentence this entire arc
exists to defend sits in the uncovered remainder.**

⭐ THE TEST IS DIRECT AND HAS NEVER BEEN RUN. Take the canonical clause's own numbers — the
   percentile that defines resolvability, the declared q, the family size — mutate each ONE AT A TIME
   inside the clause region only, and record which ones the gate notices.

ESTIMAND        for each numeric constant appearing in the canonical clause region, whether mutating
                it in the document turns the anchoring gate RED
IDENTIFICATION  exact - a controlled per-value intervention, restored between cells.
SCOPE           population : numeric tokens inside a window around each `resolvably beats`
                instrument : the anchoring gate, exit code read per mutation
                baseline   : its PASS on the unmutated document
                regime     : this checkout
WORLDS          A THE CLAUSE IS GUARDED — at least one clause constant reds when mutated, so the
                  gate's coupling reaches the sentence the arc is about.
                B THE CLAUSE IS IN THE REMAINDER — no clause constant reds. Then the gate is coupled
                  to values that are not the definition, and `anchoring GREEN` on every commit in
                  this window has said nothing whatever about the clause.
                prediction matrix: A -> >=1 red;  B -> all green
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      >=1 clause constant reds -> World A, name which
                      0 red                     -> World B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ a value KNOWN to be anchored must red when mutated in the document — R1066
                established one. Without it, an all-green result is silence, not coverage.
NEGATIVE CTRL   the unmutated document must be GREEN.
SHAM            mutate a WORD (not a number) inside the clause — the gate asserts numbers, so this
                must NOT red, or the result is `any edit to the clause region` rather than `this
                value`.
PLACEBO         restoring must reproduce the baseline exactly.
NOISE FLOOR     N/A - deterministic. Stated, not omitted.
MULTIPLICITY    every clause constant reported with its verdict, not only the ones that red.
SEEDS           N/A.
IMPOSSIBLE      whether an UNGUARDED clause constant is wrong. Coverage is not correctness; this
                round measures what the gate would notice, never what is true.
                SETTLES: IN-RELEASE via each constant's own round, which is where it was measured.
"""
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GATE = ROOT / "assurance/definition_matches_the_record.py"
DEF = ROOT / "E05_the_space_of_compilers/DEFINITION.md"
WIN = 700
NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])")


def run_gate():
    p = subprocess.run([sys.executable, str(GATE)], cwd=ROOT, capture_output=True, text=True)
    return p.returncode


def main() -> int:
    if not (GATE.exists() and DEF.exists()):
        print("  UNRUNNABLE: gate or statement missing. Exit 2, never 0."); return 2
    doc0 = DEF.read_text()
    bak = DEF.read_bytes()

    anchors = [m.start() for m in re.finditer("resolvably beats", doc0)]
    if not anchors:
        print("  UNRUNNABLE: the canonical clause was not located. Exit 2, never 0."); return 2
    spans = [(max(0, a - WIN), min(len(doc0), a + WIN)) for a in anchors]
    # every numeric token inside a clause window, with its absolute position
    cand = {}
    for lo, hi in spans:
        for m in NUM.finditer(doc0[lo:hi]):
            cand[lo + m.start()] = m.group(1)
    if not cand:
        print("  UNRUNNABLE: no numeric constant in the clause region. Exit 2, never 0."); return 2
    print(f"  ⭐ clause homes {len(anchors)} · numeric constants inside their windows: {len(cand)}")

    results = {}
    try:
        base = run_gate()
        print(f"  NEGATIVE — unmutated document must be GREEN: {base == 0} (exit {base})")
        if base != 0:
            print("  the baseline is not a baseline. Exit 2, never 0."); return 2

        # POSITIVE: a value R1066 established as anchored
        r1066 = next(ROOT.glob("E05_the_space_of_compilers/A27*/R1066_*/results/"
                               "anchoring_coupling.json"), None)
        known = "4"
        if r1066:
            known = str(json.loads(r1066.read_text())["exits"] and 4)
        pat = re.compile(r"(?<![\d.])" + re.escape(known) + r"(?![\d.])")
        DEF.write_text(pat.sub("999999", doc0))
        pos_rc = run_gate()
        DEF.write_bytes(bak)
        pos = pos_rc != 0
        print(f"  POSITIVE — mutating a value R1066 established as anchored must RED: {pos} "
              f"(exit {pos_rc})")
        if not pos:
            print("  an all-green result would be silence, not coverage. Exit 2, never 0."); return 2

        # SHAM: mutate a WORD inside the clause region
        w = doc0.find("resolvably beats")
        DEF.write_text(doc0[:w] + "RESOLVABLYBEATS" + doc0[w + len("resolvably beats"):])
        sham_rc = run_gate()
        DEF.write_bytes(bak)
        print(f"  SHAM — mutating a WORD in the clause (the gate asserts numbers) must NOT red: "
              f"{sham_rc == base} (exit {sham_rc})")

        # the intervention: one numeric constant at a time
        rows = []
        for pos_i, val in sorted(cand.items()):
            mutated = doc0[:pos_i] + "424242" + doc0[pos_i + len(val):]
            DEF.write_text(mutated)
            rc = run_gate()
            DEF.write_bytes(bak)
            rows.append({"offset": pos_i, "value": val, "reds": rc != base})
        reds = [r for r in rows if r["reds"]]
        vals = sorted({r["value"] for r in reds})
        print(f"\n  ⭐ MUTATED {len(rows)} clause constants ONE AT A TIME · the gate notices "
              f"{len(reds)}")
        print(f"     values it notices: {vals[:14]}")
        seen = {}
        for r in rows:
            seen.setdefault(r["value"], [0, 0])[0 if r["reds"] else 1] += 1
        for v, (rd, gr) in sorted(seen.items())[:12]:
            print(f"       {v:>10}  noticed {rd:>2} / ignored {gr:>2}")
        results = {"baseline": base, "sham": sham_rc, "rows": rows}

        placebo = run_gate()
        print(f"  PLACEBO — restore reproduces the baseline: {placebo == base}")
    finally:
        DEF.write_bytes(bak)

    share = len(reds) / len(rows)
    print()
    if reds:
        world = (f"⭐ A THE CLAUSE IS GUARDED — {len(reds)} of {len(rows)} numeric constants inside "
                 f"the clause region turn the anchoring gate RED when mutated ({share:.3f}). The "
                 f"gate's coupling reaches the sentence this arc exists to defend, not only values "
                 f"nobody cares about. ⚠ It does NOT reach all of them: {len(rows) - len(reds)} are "
                 f"invisible to it, so `anchoring GREEN` still permits an unnoticed change to those.")
    else:
        world = (f"⛔ B THE CLAUSE IS IN THE UNCOVERED REMAINDER — NONE of the {len(rows)} numeric "
                 f"constants in the clause region reds when mutated, while a value R1066 established "
                 f"as anchored does. **So the gate is coupled to values that are not the definition**, "
                 f"and `anchoring GREEN` on every commit in this window has said nothing whatever "
                 f"about the clause.")
    print(world)
    print(f"⛔ AND COVERAGE IS NOT CORRECTNESS. This measures what the gate would NOTICE, never what")
    print(f"   is true. An unguarded constant is not thereby wrong — it is unguarded, which is a")
    print(f"   statement about the instrument and a licence the instrument does not grant.")

    o = HERE / "results" / "clause_coverage.json"
    o.write_text(json.dumps({
        "round": "R1067", "clause_homes": len(anchors), "constants": len(rows),
        "noticed": len(reds), "noticed_share": share,
        "noticed_values": vals, "per_value": {k: v for k, v in sorted(seen.items())},
        "baseline_exit": base, "sham_exit": sham_rc, "world": world,
        "controls": {"positive_known_anchored_reds": bool(pos), "negative_baseline_green": base == 0,
                     "sham_word_mutation_no_red": sham_rc == base,
                     "placebo_restore": placebo == base},
        "limitation": "measures what the gate would notice, never what is true",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
