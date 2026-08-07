"""R1066 — the anchoring gate claims to re-derive from artifacts. Attack it from the ARTIFACT side.

R1065 showed the CURRENCY gate is text-only: mutate a measured value, leave the statement alone, and
it exits 0 while printing the falsified number. The other gate on every commit here claims something
strictly stronger — *"every locatable claim in DEFINITION.md is re-derived from a committed artifact"*.

⭐ THAT CLAIM HAS ONLY EVER BEEN ATTACKED FROM THE DOCUMENT SIDE. R1043 corrupted a value in
   DEFINITION.md and R1044 found the gate narrow-not-blind at 2.7-7.8% coverage. Nobody has changed
   the ARTIFACT and asked whether the gate notices the document no longer agrees with it. If it does
   not, then `re-derived from a committed artifact` describes the code's intent and not its
   behaviour, and both gates on every commit here are text-only.

ESTIMAND        whether the anchoring gate's verdict changes when an artifact value it re-derives is
                mutated while the statement is untouched
IDENTIFICATION  exact - a controlled intervention on committed files, restored in a finally.
SCOPE           population : one artifact value the gate asserts against the document
                instrument : the anchoring gate, run as a subprocess, exit code AND stdout read
                baseline   : its PASS on the unmutated repository
                regime     : this checkout
WORLDS          A ANCHORING IS ARTIFACT-COUPLED — mutating the artifact turns it RED. Then the two
                  gates differ in kind: currency certifies that words were written, anchoring
                  certifies that the words match a measurement, and R1065's finding is about one gate
                  rather than about the discipline.
                B BOTH GATES ARE TEXT-ONLY — it stays GREEN. Then nothing on any commit in this arc
                  has ever compared the statement to a measured value, and every `all gates green`
                  in this window means only `the expected strings are present`.
                prediction matrix: A -> red; B -> green
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      RED after artifact mutation   -> World A
                      GREEN after artifact mutation -> World B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ mutating the SAME value in the DOCUMENT must turn it RED — that is the mutation
                R1043 already showed it catches, so a gate that stays green there is not the gate
                under discussion and no zero it reports means anything.
NEGATIVE CTRL   the unmutated repository must be GREEN.
SHAM            mutate an artifact key the gate asserts NOTHING about — the verdict must not move,
                or the result is `any edit to any file` rather than `this value`.
PLACEBO         restoring everything must reproduce the baseline exactly.
NOISE FLOOR     N/A - deterministic. Stated, not omitted.
MULTIPLICITY    all cells reported: baseline, artifact-mutated, document-mutated, sham, restore.
SEEDS           N/A.
IMPOSSIBLE      whether the gate SHOULD be artifact-coupled. Behaviour, not intent.
                SETTLES: OUT-OF-RELEASE for intent; IN-RELEASE for behaviour, measured here.
"""
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GATE = ROOT / "assurance/definition_matches_the_record.py"
DEF = ROOT / "E05_the_space_of_compilers/DEFINITION.md"


def run_gate():
    p = subprocess.run([sys.executable, str(GATE)], cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main() -> int:
    if not GATE.exists():
        print("  UNRUNNABLE: the anchoring gate is missing. Exit 2, never 0."); return 2

    # find a value the gate asserts: read its source for an artifact glob + a numeric assertion
    # ⛔ THE FIRST RESOLVER LOOKED IN THE WRONG PLACE AND THE ROUND REFUSED TO RUN. The gate's globs
    #   are ROUND-DIRECTORY patterns (`R427_*`) resolved against arc directories such as A24, not
    #   artifact paths under E05. Reading the gate's own base rather than assuming one.
    src = GATE.read_text()
    bases = sorted({m for m in re.findall(r"^([A-Z]\d+)\s*=", src, re.M)})
    arcs = [d for d in (ROOT / "E05_the_space_of_compilers").iterdir() if d.is_dir()]
    rounds = re.findall(r'glob\(\s*"(R\d+_\*)"', src)
    target = None
    for r in rounds:
        for arc in arcs:
            for rd in sorted(arc.glob(r)):
                arts = sorted((rd / "results").glob("*.json"))
                if arts:
                    target = arts[-1]; break
            if target:
                break
        if target:
            break
    if target is None:
        print(f"  UNRUNNABLE: no artifact of the anchoring gate could be located "
              f"({len(rounds)} round glob(s) read from its source). Exit 2, never 0.")
        return 2
    print(f"  ⭐ target artifact: {target.relative_to(ROOT)}")

    bak_art, bak_def = target.read_bytes(), DEF.read_bytes()
    results = {}
    try:
        rc, out = run_gate()
        results["baseline"] = rc
        neg = rc == 0
        print(f"  NEGATIVE — the unmutated repository must be GREEN: {neg} (exit {rc})")
        if not neg:
            print("  the baseline is not a baseline. Exit 2, never 0."); return 2

        d = json.loads(target.read_text())
        num_key = next((k for k, v in d.items()
                        if isinstance(v, (int, float)) and not isinstance(v, bool)), None)
        if num_key is None:
            print("  UNRUNNABLE: the target artifact holds no scalar to mutate. Exit 2, never 0.")
            return 2
        orig = d[num_key]
        shown = f"{orig}"
        in_doc = shown in DEF.read_text()
        print(f"  ⭐ mutating `{num_key}` = {orig}  (its printed form appears in the statement: "
              f"{in_doc})")

        # ⛔⛔ THE FIRST POSITIVE CONTROL WAS MALFORMED AND ITS FAILURE WAS ITS OWN. It replaced the
        #   FIRST occurrence of the digit "4" anywhere in a 2,400-line document — an arbitrary
        #   number, not the asserted one — so a green result said nothing about the gate. §4's
        #   `control fails for its own reasons`. The mutation must hit the value the gate names, so
        #   it is located by the gate's own failure message instead of by naive string search.
        d_probe = json.loads(target.read_text())
        d_probe[num_key] = orig + 7777
        target.write_text(json.dumps(d_probe, indent=2) + "\n")
        _, probe_out = run_gate()
        target.write_bytes(bak_art)
        m = re.search(r"[^\n]*" + re.escape(str(num_key)) + r"[^\n]*", probe_out)
        print(f"     the gate's own red line: {m.group(0).strip()[:110] if m else '(not named)'}")
        ctx = re.search(r"expect(?:ed|s)?[^\n]{0,60}?(\b" + re.escape(shown) + r"\b)", probe_out)
        doc_txt = DEF.read_text()
        anchor_pat = re.compile(r"(?<![\d.])" + re.escape(shown) + r"(?![\d.])")
        n_occ = len(anchor_pat.findall(doc_txt))
        print(f"     the value {shown!r} occurs {n_occ} time(s) in the statement as a standalone "
              f"number; a naive first-occurrence replace is not a control")
        if in_doc and n_occ:
            DEF.write_text(anchor_pat.sub("999999", doc_txt))
            rc_d, _ = run_gate()
            DEF.write_bytes(bak_def)
        else:
            rc_d = None
        results["document_mutated"] = rc_d
        pos = rc_d is not None and rc_d != 0
        print(f"  POSITIVE — mutating that value in the DOCUMENT must turn it RED: {pos} "
              f"(exit {rc_d})")

        # INTERVENTION: mutate the ARTIFACT, statement untouched
        d[num_key] = orig + 7777
        target.write_text(json.dumps(d, indent=2) + "\n")
        rc_a, out_a = run_gate()
        target.write_bytes(bak_art)
        results["artifact_mutated"] = rc_a
        print(f"  ⭐ INTERVENTION — artifact `{num_key}` {orig} -> {orig + 7777}, STATEMENT "
              f"UNTOUCHED: gate exit {rc_a}")

        # SHAM: mutate a key the gate asserts nothing about
        d2 = json.loads(target.read_text())
        d2["__sham_key_no_assertion__"] = "mutated"
        target.write_text(json.dumps(d2, indent=2) + "\n")
        rc_sh, _ = run_gate()
        target.write_bytes(bak_art)
        results["sham"] = rc_sh
        print(f"  SHAM — adding a key the gate asserts nothing about: exit {rc_sh} "
              f"(== baseline: {rc_sh == results['baseline']})")

        rc_p, _ = run_gate()
        results["placebo_restored"] = rc_p
        print(f"  PLACEBO — restore reproduces the baseline: {rc_p == results['baseline']}")
    finally:
        target.write_bytes(bak_art)
        DEF.write_bytes(bak_def)

    if not pos:
        world = ("⛔ UNVERIFIED — the document-side mutation did not turn the gate red, so this "
                 "value is outside its assertion set and no artifact-side result on it is readable. "
                 "That is R1044's coverage finding biting again: the gate anchors 2.7-7.8% of the "
                 "document, and I picked a value from the remainder.")
        coupled = None
    else:
        coupled = results["artifact_mutated"] != results["baseline"]
        if coupled:
            world = (f"⭐ A ANCHORING IS ARTIFACT-COUPLED — mutating the artifact turned it RED "
                     f"(exit {results['artifact_mutated']}). **The two gates differ in kind**: "
                     f"currency certifies that words were written; anchoring certifies that the "
                     f"words match a measurement. R1065's finding is about ONE gate, not about the "
                     f"discipline.")
        else:
            world = (f"⛔ B BOTH GATES ARE TEXT-ONLY — the artifact value moved by +7777 and the gate "
                     f"still exited {results['artifact_mutated']}. Then **nothing on any commit in "
                     f"this arc has ever compared the statement to a measured value**, and every "
                     f"`all gates green` in this window means only `the expected strings are "
                     f"present`.")
    print()
    print(world)
    print(f"⛔ AND THIS MEASURES BEHAVIOUR, NEVER INTENT. Whether a gate SHOULD be artifact-coupled is")
    print(f"   a design question; which one it IS is what an attack can settle, and this is the first")
    print(f"   time this gate has been attacked from the side its own claim is written about.")

    o = HERE / "results" / "anchoring_coupling.json"
    o.write_text(json.dumps({
        "round": "R1066", "target": str(target.relative_to(ROOT)), "mutated_key": num_key,
        "exits": results, "artifact_coupled": coupled, "world": world,
        "controls": {"positive_document_mutation_reds": bool(pos), "negative_baseline_green": True,
                     "sham_equals_baseline": results.get("sham") == results.get("baseline"),
                     "placebo_restore": results.get("placebo_restored") == results.get("baseline")},
        "limitation": "measures behaviour, not intent; and only for a value inside the gate's "
                      "declared 2.7-7.8% coverage",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
