"""R1068 — build the coverage R1067 found missing, and make R1067's sweep its acceptance test.

R1067 mutated all 121 numeric constants in the clause region one at a time; the anchoring gate
noticed NONE. The constants are already in committed artifacts — only the ASSERTIONS were missing.

⭐ SO THIS ROUND SHIPS `assurance/the_clause_is_anchored.py`, which re-derives each clause constant
   from the round that measured it and requires the statement to state it. And it does not take the
   gate's own green as evidence: **the acceptance test is R1067's exact mutation sweep**, which the
   old gate failed 121 times out of 121.

ESTIMAND        of the clause constants the new gate declares, how many turn it RED when mutated in
                the statement — and whether it stays GREEN where it should
IDENTIFICATION  exact - per-value intervention, restored between cells.
SCOPE           population : the constants the new gate declares + a sham + a placebo
                instrument : the new gate, exit code per mutation
                baseline   : its PASS on the unmutated repository
                regime     : this checkout
WORLDS          A THE GAP IS CLOSED FOR THE DECLARED CONSTANTS — every declared constant reds when
                  mutated, so `the clause is anchored` is now a checkable statement about them.
                B THE NEW GATE IS DECORATION — some declared constant does not red. Then it repeats
                  the failure it was built to fix, one level along, and must be reported as such.
                prediction matrix: A -> all declared constants red;  B -> any stays green
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      every declared constant reds -> World A
                      any stays green              -> World B, name it
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   the unmutated repository must be GREEN, and each mutation must be restored — a gate
                that is red before the mutation proves nothing.
NEGATIVE CTRL   ⭐ deleting the ARTIFACT a constant is re-derived from must turn it RED, not silently
                skip it. That is R1063's `empty population passes` failure, and the gate was written
                to fail closed; this is where that is checked rather than asserted.
SHAM            mutate a number in the clause region that the gate does NOT declare — it must stay
                GREEN, or the gate is reacting to any edit and its reds mean nothing.
PLACEBO         restoring everything reproduces the baseline exactly.
NOISE FLOOR     N/A - deterministic. Stated, not omitted.
MULTIPLICITY    every declared constant reported with its verdict, plus the sham and the negative.
SEEDS           N/A.
IMPOSSIBLE      covering the clause's PROSE. This gate asserts numbers only, and says so; a gate that
                overstated its reach would be the failure it was built to fix.
                SETTLES: IN-RELEASE - prose assertions are possible but are a different instrument.
"""
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GATE = ROOT / "assurance/the_clause_is_anchored.py"
DEF = ROOT / "E05_the_space_of_compilers/DEFINITION.md"


def run_gate():
    p = subprocess.run([sys.executable, str(GATE)], cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout


def main() -> int:
    if not GATE.exists():
        print("  UNRUNNABLE: the new gate is missing. Exit 2, never 0."); return 2
    bak = DEF.read_bytes()
    doc0 = DEF.read_text()
    base, out = run_gate()
    print(f"  POSITIVE — the unmutated repository must be GREEN: {base == 0} (exit {base})")
    if base != 0:
        print("  a gate red before the mutation proves nothing. Exit 2, never 0."); return 2

    declared = [(m.group(1).strip(), m.group(2)) for m in
                re.finditer(r"OK\s+(\S.*?)\s+=\s+(\d+)", out)]
    if not declared:
        print("  UNRUNNABLE: the gate declared no constant. Exit 2, never 0."); return 2
    print(f"  ⭐ constants the gate declares: {[(a, b) for a, b in declared]}")

    rows = []
    try:
        for label, val in declared:
            pat = re.compile(r"(?<![\d.])" + re.escape(val) + r"(?![\d.])")
            DEF.write_text(pat.sub("424242", doc0))
            rc, _ = run_gate()
            DEF.write_bytes(bak)
            rows.append({"constant": label, "value": val, "reds": rc != base})
            print(f"     mutate {label:<28} {val:>4} -> gate {'RED' if rc != base else 'green'}")

        # SHAM: a clause-region number the gate does not declare
        vals = {v for _, v in declared}
        anchor = doc0.find("resolvably beats")
        seg = doc0[max(0, anchor - 700): anchor + 700]
        sham_val = next((m.group(1) for m in re.finditer(r"(?<![\w.])(\d+)(?![\w.])", seg)
                         if m.group(1) not in vals), None)
        sham_rc = None
        if sham_val:
            p2 = re.compile(r"(?<![\d.])" + re.escape(sham_val) + r"(?![\d.])")
            DEF.write_text(p2.sub("424242", doc0))
            sham_rc, _ = run_gate()
            DEF.write_bytes(bak)
        print(f"  SHAM — mutating an UNDECLARED clause number ({sham_val}) must stay GREEN: "
              f"{sham_rc == base} (exit {sham_rc})")

        # NEGATIVE: hide an artifact the gate re-derives from — it must RED, not skip
        art = next(ROOT.glob("E05_the_space_of_compilers/A27*/R1056_*/results/"
                             "certification_curve.json"), None)
        neg_rc = None
        if art:
            hold = art.read_bytes()
            art.unlink()
            neg_rc, _ = run_gate()
            art.write_bytes(hold)
        print(f"  NEGATIVE — removing an artifact it re-derives from must RED (fail closed): "
              f"{neg_rc not in (None, base)} (exit {neg_rc})")

        plac, _ = run_gate()
        print(f"  PLACEBO — restore reproduces the baseline: {plac == base}")
    finally:
        DEF.write_bytes(bak)

    green = [r for r in rows if not r["reds"]]
    ok = (not green) and sham_rc == base and neg_rc not in (None, base)
    print()
    if ok:
        world = (f"⭐ A THE GAP IS CLOSED FOR THE DECLARED CONSTANTS — all {len(rows)} red when "
                 f"mutated, an undeclared clause number stays green, and removing a source artifact "
                 f"reds rather than silently skipping. R1067's sweep, which the old gate failed 121 "
                 f"of 121, now has an instrument that answers it for these values.")
    elif green:
        world = (f"⛔ B THE NEW GATE IS DECORATION FOR {len(green)} CONSTANT(S) — "
                 f"{[r['constant'] for r in green]} do not red when mutated, so it repeats the "
                 f"failure it was built to fix.")
    else:
        world = (f"⛔ UNVERIFIED — the sham or the fail-closed control did not behave, so the reds "
                 f"above are not attributable: sham exit {sham_rc}, artifact-removed exit {neg_rc}.")
    print(world)
    print(f"⛔ AND IT COVERS NUMBERS, NOT PROSE, AND SAYS SO. {len(rows)} constants is not `the clause")
    print(f"   is anchored`; R1067 counted 121 numeric tokens in the clause region, so this closes")
    print(f"   the declared subset and leaves the rest exactly as exposed as before.")

    o = HERE / "results" / "clause_gate.json"
    o.write_text(json.dumps({
        "round": "R1068", "declared": len(rows), "rows": rows,
        "sham_exit": sham_rc, "artifact_removed_exit": neg_rc, "baseline": base,
        "clause_region_constants_R1067": 121, "world": world,
        "gate": "assurance/the_clause_is_anchored.py",
        "controls": {"positive_baseline_green": base == 0, "sham_undeclared_stays_green":
                     sham_rc == base, "negative_fail_closed": neg_rc not in (None, base)},
        "limitation": "covers declared numeric constants only, never the clause's prose",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
