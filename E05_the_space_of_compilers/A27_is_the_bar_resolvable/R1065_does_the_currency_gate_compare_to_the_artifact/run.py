"""R1065 — does the currency gate compare the STATEMENT to the ARTIFACT, or only to my own patterns?

R1064 shipped a gate ensuring every registered fact's artifact exists. R1063 showed a missing artifact
made the currency gate pass vacuously. Both are about the artifact's PRESENCE. Neither asks the
question one level in: **when the artifact IS present, does the gate check that the statement agrees
with it?**

⛔ READ FROM THE SOURCE BEFORE PREDICTING. Each fact is a 4-tuple `(round, description, value_string,
   patterns)`. `value_string` is an f-string built from the loaded artifact and is PRINTED. `patterns`
   are hand-written literals, matched against DEFINITION.md. **Nothing in the match consumes the
   artifact.** If that reading is right, mutating a measured value changes the printed line and NOT
   the verdict — so the gate certifies THAT I WROTE CERTAIN WORDS, never that those words are true of
   what was measured.

ESTIMAND        whether the currency gate's verdict changes when a registered artifact's VALUE is
                mutated while the statement text is untouched
IDENTIFICATION  exact - a two-cell intervention on committed files, restored afterwards.
SCOPE           population : one registered fact whose value appears verbatim in the statement
                instrument : the currency gate, executed as a subprocess, stdout AND exit code read
                baseline   : the gate's PASS on the unmutated repository
                regime     : this checkout
WORLDS          A THE GATE IS ARTIFACT-COUPLED — mutating the artifact turns it RED, so a PASS is
                  evidence the statement agrees with what was measured.
                B THE GATE IS TEXT-ONLY — mutating the artifact leaves it GREEN. Then its PASS means
                  only `these hand-written patterns appear in the document`, and every currency PASS
                  in this arc must be read that narrowly: it certifies prose against prose.
                prediction matrix: A -> red after artifact mutation; B -> green
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      gate RED after artifact mutation -> World A
                      gate GREEN                        -> World B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ deleting the fact's ANNOTATION from the statement must turn the gate RED. A gate
                never shown to fail cannot evidence a pass, and this is the mutation it is designed
                to catch.
NEGATIVE CTRL   the unmutated repository must be GREEN, or the baseline is not a baseline.
SHAM            mutate a DIFFERENT artifact key that no pattern mentions — the verdict must not move
                either way, showing the artifact-mutation result is not just any file edit.
PLACEBO         mutating nothing must reproduce the baseline exactly.
NOISE FLOOR     N/A - the gate is deterministic. Stated, not omitted.
MULTIPLICITY    all four cells reported: baseline, artifact-mutated, statement-mutated, sham.
SEEDS           N/A.
IMPOSSIBLE      whether a text-only gate is the WRONG design. It may be the intended one — a currency
                gate asks `did the statement get updated`, not `is the statement true`. This round
                establishes which question it answers, not which it should.
                SETTLES: OUT-OF-RELEASE for the design intent; IN-RELEASE for the behaviour.
"""
import json, pathlib, re, shutil, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GATE = ROOT / "assurance/a_statement_is_current_with_the_arc.py"
DEF = ROOT / "E05_the_space_of_compilers/DEFINITION.md"
ART = next(ROOT.glob("E05_the_space_of_compilers/A27*/R1064_*/results/registry_inputs.json"), None)


def run_gate():
    p = subprocess.run([sys.executable, str(GATE)], cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout


def main() -> int:
    if ART is None:
        print("  UNRUNNABLE: the target artifact is missing. Exit 2, never 0."); return 2
    bak_art = ART.read_bytes()
    bak_def = DEF.read_bytes()
    results = {}
    try:
        rc, out = run_gate()
        results["baseline"] = rc
        neg = rc == 0
        print(f"  NEGATIVE — the unmutated repository must be GREEN: {neg} (exit {rc})")

        # ---------- POSITIVE: delete the fact's annotation from the statement ----------
        # ⛔ THE FIRST POSITIVE CONTROL REDACTED ONE ANCHOR AND THE GATE STAYED GREEN — CORRECTLY.
        #   The gate is `ok = any(...)`: a fact with two patterns survives losing one. So the
        #   statement mutation must defeat EVERY anchor of the target fact, or it is not the
        #   mutation the gate is designed to catch. Redacting one and calling it a control would
        #   have made a passing gate look broken.
        doc = DEF.read_text()
        anchors = ["a_registered_fact_must_load.py", "79 globs resolve", "all 79 globs",
                   "79 registered artifact glob"]
        hit = [a for a in anchors if a in doc]
        if not hit:
            print("  UNRUNNABLE: no anchor of the target fact is present. Exit 2, never 0."); return 2
        mutated = doc
        for a in hit:
            mutated = mutated.replace(a, "REDACTED")
        DEF.write_text(mutated)
        print(f"     (statement mutation redacted {len(hit)} anchor(s): {hit})")
        rc_s, _ = run_gate()
        results["statement_mutated"] = rc_s
        pos = rc_s != 0
        print(f"  POSITIVE — deleting the annotation from the STATEMENT must turn it RED: {pos} "
              f"(exit {rc_s})")
        DEF.write_bytes(bak_def)

        if not (pos and neg):
            print("  the gate cannot be read either way. Exit 2, never 0."); return 2

        # ---------- the intervention: mutate the measured VALUE, leave the statement alone ----------
        d = json.loads(ART.read_text())
        before = d["globs"]
        d["globs"] = before + 4242
        d["dead"] = ["A27_*/FABRICATED_*/results/nothing.json"]
        ART.write_text(json.dumps(d, indent=2) + "\n")
        rc_a, out_a = run_gate()
        results["artifact_mutated"] = rc_a
        print(f"  ⭐ INTERVENTION — artifact `globs` {before} -> {d['globs']}, `dead` given a "
              f"fabricated entry, STATEMENT UNTOUCHED: gate exit {rc_a}")
        shows = re.search(r"R1064[^\n]*", out_a)
        print(f"     the gate's own printed line for that fact: "
              f"{shows.group(0).strip()[:96] if shows else '(not printed on a PASS)'}")
        ART.write_bytes(bak_art)

        # ---------- SHAM: mutate a key no pattern mentions ----------
        d2 = json.loads(ART.read_text())
        d2["limitation"] = "SHAM: this key is mentioned by no pattern"
        ART.write_text(json.dumps(d2, indent=2) + "\n")
        rc_sh, _ = run_gate()
        results["sham_mutated"] = rc_sh
        ART.write_bytes(bak_art)
        print(f"  SHAM — mutating a key no pattern mentions: exit {rc_sh} (must equal the baseline "
              f"{results['baseline']}): {rc_sh == results['baseline']}")

        rc_p, _ = run_gate()
        results["placebo_restored"] = rc_p
        print(f"  PLACEBO — restoring everything reproduces the baseline: "
              f"{rc_p == results['baseline']} (exit {rc_p})")
    finally:
        ART.write_bytes(bak_art)
        DEF.write_bytes(bak_def)

    coupled = results["artifact_mutated"] != results["baseline"]
    print()
    if coupled:
        world = (f"⭐ A THE GATE IS ARTIFACT-COUPLED — mutating a measured value turned it RED "
                 f"(exit {results['artifact_mutated']} vs baseline {results['baseline']}), so a PASS "
                 f"is evidence the statement agrees with what was measured.")
    else:
        world = (f"⛔ B THE GATE IS TEXT-ONLY — the measured value was changed by +4242 and the `dead` "
                 f"list was given a fabricated entry, and the gate still exited "
                 f"{results['artifact_mutated']}, identical to baseline. **Its patterns are "
                 f"hand-written literals matched against DEFINITION.md; nothing in the match consumes "
                 f"the artifact.** So every currency PASS in this arc means exactly `these words "
                 f"appear in the document` — it certifies PROSE AGAINST PROSE, and the artifact's only "
                 f"roles are to exist (R1063) and to supply a printed string.")
    print(world)
    print(f"⛔ AND THIS IS A SCOPE FINDING, NOT A DEFECT VERDICT. A currency gate may be MEANT to ask")
    print(f"   `did the statement get updated`, which is a real question and the one it answers well.")
    print(f"   What is not licensed is reading its PASS as `the statement is true of the measurement`,")
    print(f"   which is how I have been reading it for every round in this window.")

    o = HERE / "results" / "gate_coupling.json"
    o.write_text(json.dumps({
        "round": "R1065", "exits": results, "artifact_coupled": bool(coupled),
        "target_artifact": str(ART.relative_to(ROOT)), "world": world,
        "controls": {"positive_statement_mutation_reds": bool(pos),
                     "negative_baseline_green": bool(neg),
                     "sham_unrelated_key_no_change": results["sham_mutated"] == results["baseline"],
                     "placebo_restore": results["placebo_restored"] == results["baseline"]},
        "limitation": "establishes which question the gate answers, not which it should",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
