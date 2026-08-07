#!/usr/bin/env python3
"""R1043 — the suite is green and it is all mine. Mutation-test the three gates that guard commits.

R1042 closed by noting a green suite is evidence about my CONSISTENCY, not my correctness, and tagged
the missing input `OUT-OF-RELEASE: a reader who is not the author`.

⛔ THAT TAG IS ALREADY HALF WRONG, AND THE NEW ENUM CANNOT CATCH IT. §2.5 of the standard says a
   reader who is not the author is NOT structurally impossible — triple-blind clean-context agents
   supply exactly that. It is unavailable to THIS SESSION by an explicit instruction, which is a fact
   about the session and not about the release. The enum removes the wording loophole, not the
   mislabelling one, and this is the first live instance of that limitation biting — one round after
   the gate was built.

⛔ AND `attack_the_suite.py` IS THE PRIOR ART, WHICH BOUNDS WHAT IS LEFT. It empties each check's
   input and confirms exit 2 rather than 0 — the FLOOR. It does not confirm any gate fires on
   CORRUPTED content. A gate can exit 2 on empty and 0 on everything real: `next_gradient_is_new.py`
   is a self-test (R1030) and `a_next_names_its_prior_art.py` has measured recall 0 of 4 (R1031). So
   detection is unestablished, and that is what this round tests.

ESTIMAND        for each gate preflight runs, does it go RED when the content it guards is corrupted?
IDENTIFICATION  exact. The mutation is a controlled intervention on committed text; the verdict is an
                exit code.
SCOPE           population : the 3 gates `preflight.py` invokes — currency, anchoring, next
                instrument : each gate's own exit code · baseline : `attack_the_suite`'s floor result
WORLDS          A ALL THREE DETECT — each fires on a targeted corruption. Then a green preflight is
                  evidence about the content, and the suite's guarantee is real for the commit path.
                B AT LEAST ONE IS BLIND — some gate passes a corruption it exists to catch. Then a
                  green preflight is evidence about that gate's silence, and R1042's "consistency,
                  not correctness" is stronger than a general worry: it is a named hole.
                prediction matrix: A -> 3 of 3 RED under mutation.
                                   B -> the blind gate is named.
                ⚠ TWO OF THREE ARE ALREADY KNOWN POSITIVES: currency went red-first on every fact
                  registered this session, and `next` fired 8 times in 8 uses. The informative cell
                  is ANCHORING, which has never been observed firing.
KILL            pre-registered and CONDITIONAL:
                  if every mutation is restored and the suite is green again afterwards:
                      3 of 3 go RED -> World A
                      otherwise      -> World B, the blind gate named
                  else UNVERIFIED (a failed restore invalidates everything downstream)
POSITIVE CTRL   the two known positives must reproduce: corrupting a registered fact's supporting
                text must turn currency RED, and a bare quantifier must turn `next` RED. If a gate
                with an observed firing history does not fire here, the harness is wrong, not the gate.
NEGATIVE CTRL   before any mutation, all three must be GREEN on the untouched tree — otherwise a RED
                afterwards is not attributable to the mutation.
PLACEBO         a NO-OP mutation (write the file back byte-identical) must leave all three GREEN.
NOISE FLOOR     N/A — exit codes are exact. Stated rather than omitted.
MULTIPLICITY    3 gates x 1 targeted mutation each, every cell reported.
SEEDS           N/A — deterministic.
IMPOSSIBLE      whether a gate that DOES fire is checking the right property. Detection is necessary,
                not sufficient — the proxy-ledger problem this arc has hit at four levels.
                SETTLES: OUT-OF-RELEASE a reader who is not the author. ⚠ AND THAT TAG IS NARROWER
                THAN IT LOOKS: §2.5's triple-blind agents would supply it, and they are unavailable
                to this session by instruction, not by a property of the release.
"""
import json, pathlib, shutil, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PY = sys.executable
DEF = ROOT / "E05_the_space_of_compilers" / "DEFINITION.md"
GATES = {
    "currency": ROOT / "assurance" / "a_statement_is_current_with_the_arc.py",
    "anchoring": ROOT / "assurance" / "definition_matches_the_record.py",
}


def rc(path, *args):
    return subprocess.run([PY, str(path), *args], capture_output=True, text=True).returncode


def next_rc(text):
    g = ROOT / "assurance" / "next_line_quantifiers_are_computed.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("nq", g)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return 1 if m.flagged(text) else 0


def main() -> int:
    backup = pathlib.Path(tempfile.mkdtemp()) / "DEFINITION.md"
    shutil.copy2(DEF, backup)
    try:
        # ---------- NEGATIVE: green before any mutation, or nothing after is attributable ----------
        base = {k: rc(v) for k, v in GATES.items()}
        base["next"] = next_rc("a NEXT with no quantifier and no bare count, citing R1042.")
        print(f"  NEGATIVE — all three must be GREEN on the untouched tree: {base}")
        if any(v != 0 for v in base.values()):
            print("  a gate is already red; a red after mutation would not be attributable. Exit 2.")
            return 2

        # ---------- PLACEBO: byte-identical rewrite must change nothing ----------
        DEF.write_text(DEF.read_text())
        plac = {k: rc(v) for k, v in GATES.items()}
        print(f"  PLACEBO  — a byte-identical rewrite must leave them GREEN: {plac}  "
              f"{'PASS' if all(v == 0 for v in plac.values()) else '⛔ FAIL'}")

        rows = {}
        # ---------- MUTATION 1: currency — delete a registered fact's supporting text ----------
        t = DEF.read_text()
        # ⚠⚠ THE MUTATION IS ITSELF AN INSTRUMENT AND NEEDS A POSITIVE CONTROL, WHICH THE FIRST
        #   VERSION LACKED. I replaced `SETTLES:` and read currency as GREEN, concluding it was
        #   blind — while I had watched it go RED red-first on every fact registered this session.
        #   The cause: R1042's registered fact carries TWO alternative patterns, and the edit broke
        #   only one. A mutation that does not break what the gate keys on tests nothing, and the
        #   gate's "pass" was correct. So the mutation now VERIFIES it has broken every alternative
        #   before the verdict is read.
        import re as _re
        PATS = [r"(SETTLES:).{0,200}(IN-RELEASE|UNATTACKED|OUT-OF-RELEASE)",
                r"(forward[- ]only).{0,300}(declar\w+|enum)"]
        t = DEF.read_text()
        i = t.find("⭐ **AND R1042 LANDS THE FORWARD-ONLY REMEDY.**")
        if i < 0:
            print("  UNRUNNABLE: the currency mutation's anchor block is absent. Exit 2."); return 2
        j = t.find("\n\n", t.find("mislabelling** one.", i))
        mutated = t[:i] + t[(j if j > 0 else len(t)):]
        # POSITIVE CONTROL ON THE MUTATION: every alternative must now fail to match
        region_before = [bool(_re.search(q, t, _re.I | _re.S)) for q in PATS]
        region_after = [bool(_re.search(q, mutated, _re.I | _re.S)) for q in PATS]
        print(f"  MUTATION CONTROL — R1042's fact patterns matched {region_before} before, "
              f"{region_after} after")
        if any(region_after) or not all(region_before):
            print("  the mutation does not break what the gate keys on; its verdict would test "
                  "nothing. Exit 2, never 0.")
            return 2
        DEF.write_text(mutated)
        rows["currency"] = rc(GATES["currency"])
        DEF.write_text(t)

        # ---------- MUTATION 2: anchoring — corrupt a value the gate ACTUALLY ASSERTS ----------
        # ⚠⚠ THE SAME ERROR, CAUGHT TWICE IN ONE ROUND. My first anchoring mutation corrupted
        #   `0.9973`, which appears ZERO times in `definition_matches_the_record.py` — the gate never
        #   asserts it, so its GREEN tested nothing and "anchoring is blind" would have been a false
        #   retraction of a working gate. The value is now chosen by INTERSECTING the gate's own
        #   asserted numbers with those appearing exactly once in DEFINITION.md, so the mutation is
        #   guaranteed to hit something it keys on.
        import re as _re2
        gsrc = (ROOT / "assurance" / "definition_matches_the_record.py").read_text()
        t = DEF.read_text()
        cands = sorted(n for n in set(_re2.findall(r"\d\.\d{3,}", gsrc)) if t.count(n) == 1)
        print(f"  MUTATION CONTROL — values the anchoring gate asserts AND that occur exactly once "
              f"in\n     DEFINITION.md: {cands[:6]}")
        if not cands:
            print("  UNRUNNABLE: no value is both asserted and uniquely locatable. Exit 2."); return 2
        num = cands[0]
        DEF.write_text(t.replace(num, "0.1234"))
        rows["anchoring"] = rc(GATES["anchoring"])
        DEF.write_text(t)
        print(f"     corrupted `{num}` -> 0.1234")

        # ---------- MUTATION 3: next — a bare quantifier over our own work ----------
        rows["next"] = next_rc("every round in this arc has now been checked and nothing remains.")

        print(f"\n  ⭐ MUTATION TEST — each gate must go RED (rc != 0) on a corruption it exists to catch")
        print(f"     {'gate':<12}{'clean rc':>10}{'mutated rc':>12}  detects")
        for k in ("currency", "anchoring", "next"):
            det = rows[k] != 0
            print(f"     {k:<12}{base[k]:>10}{rows[k]:>12}  {det}")
        blind = [k for k in rows if rows[k] == 0]

        print()
        if not blind:
            world = ("⭐ A ALL THREE DETECT — each gate preflight runs goes RED on a targeted "
                     "corruption of the content it guards. A green preflight is therefore evidence "
                     "about the CONTENT for the commit path, not only about the gate's silence.")
        else:
            world = (f"⭐ B AT LEAST ONE IS BLIND — {blind} passed a corruption it exists to catch. "
                     f"A green preflight is evidence about that gate's silence, and R1042's "
                     f"'consistency, not correctness' is not a general worry but a NAMED HOLE.")
        print(world)
        print(f"⛔ AND `attack_the_suite.py` IS NOT THIS. It empties each input and confirms exit 2 —")
        print(f"   the FLOOR. Detection on corrupted content is a different property, and two gates in")
        print(f"   this repository have already failed it: `next_gradient_is_new` is a self-test")
        print(f"   (R1030) and `a_next_names_its_prior_art` has recall 0 of 4 (R1031).")
        print(f"⚠ AND DETECTION IS NECESSARY, NOT SUFFICIENT. A gate that fires may still be checking")
        print(f"   the wrong property — the proxy-ledger problem this arc has hit at four levels.")

        out = HERE / "results" / "mutation_test.json"
        out.write_text(json.dumps({
            "round": "R1043", "clean": base, "mutated": rows, "blind": blind,
            "placebo_green": all(v == 0 for v in plac.values()),
            "prior_art": "attack_the_suite.py tests the empty-input FLOOR, not detection",
            "known_positives": ["currency (red-first every round this session)",
                                "next (fired 8 of 8 uses)"],
            "world": world,
            "limitation": "detection is necessary, not sufficient; a firing gate may check the wrong "
                          "property",
        }, indent=2) + "\n")
        print(f"\nartifact {out.relative_to(ROOT)}")
        return 0
    finally:
        # ⛔ RESTORE IN `finally`, WHICH IS THIS REPOSITORY'S OWN SCAR: a timeout during
        #   attack_the_suite once left five epochs stashed and 776 files needed recovery.
        shutil.copy2(backup, DEF)
        after = {k: rc(v) for k, v in GATES.items()}
        print(f"  RESTORE — DEFINITION.md put back; gates on the restored tree: {after}")
        if any(v != 0 for v in after.values()):
            print("  ⛔ THE RESTORE DID NOT VERIFY. Everything above is void until this is repaired.")


if __name__ == "__main__":
    raise SystemExit(main())
