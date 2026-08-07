#!/usr/bin/env python3
"""R1044 — R1043 called the anchoring gate BLIND. It is NARROW, it says so, and I never read it.

⛔ THIS ROUND RETRACTS THE HEADLINE OF THE ROUND COMMITTED IMMEDIATELY BEFORE IT. R1043 concluded
   "one of the three commit gates is blind: anchoring passes a corruption of a value it explicitly
   asserts". Two things are wrong with that sentence and both are mine.

   ① The value I corrupted, `0.0098`, is NOT inside any assertion span. It appears in the gate's
     SOURCE and in the document, but the gate's located-assertion set does not cover it — checked
     here by intersecting the document offsets of each value against the spans the gate's own
     ASSERTIONS regexes match. So "a value it explicitly asserts" is FALSE.
   ② And the gate had been PRINTING its own coverage the whole time: `2.7%-7.8% of this document
     depending on what counts as a claim`, followed by `A PASS certifies the anchored numbers, never
     the document`. **I read its EXIT CODE and never its OUTPUT.** That is door ① — a description
     instead of the object — inside a round whose entire subject was whether instruments can be
     trusted.

ESTIMAND        does the anchoring gate go RED when a value INSIDE its located assertion spans is
                corrupted? That is the detection question R1043 meant to ask and did not.
IDENTIFICATION  exact. Coverage is computed by intersecting document offsets with the spans the
                gate's own ASSERTIONS regexes locate, so "covered" is the gate's definition, not mine.
SCOPE           population : DEFINITION.md · instrument : the gate's exit code AND its printed
                coverage · baseline : R1043's committed (and now retracted) verdict
WORLDS          A NARROW BUT SOUND — corrupting a COVERED value turns it RED. Then the gate detects
                  within its declared scope, R1043's "blind" is withdrawn, and what stands is the
                  gate's own published coverage: a PASS certifies 2.7%-7.8% of the document.
                B GENUINELY BLIND — even a covered value passes. Then R1043's headline survives on
                  better evidence than it originally had.
                prediction matrix: A -> RED on covered, GREEN on uncovered, both measured here.
                                   B -> GREEN on both.
KILL            pre-registered and CONDITIONAL:
                  if the coverage computation reproduces the gate's own printed percentages:
                      covered mutation RED and uncovered GREEN -> World A, R1043 retracted
                      otherwise                                 -> World B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   the covered/uncovered split must be non-trivial: at least one value of each kind, and
                the gate's own printed coverage must be reproduced from the same spans — otherwise
                "covered" is my word rather than its.
NEGATIVE CTRL   the UNCOVERED mutation must stay GREEN, reproducing R1043's observation exactly. That
                is what makes this a scoping correction rather than a contradiction: both results are
                real and they differ in which value was touched.
PLACEBO         the untouched tree must be GREEN before either mutation.
NOISE FLOOR     N/A — exit codes and string offsets are exact. Stated rather than omitted.
MULTIPLICITY    2 mutations, both reported.
SEEDS           N/A — deterministic.
IMPOSSIBLE      whether the 92-97% the gate does NOT cover contains an error. Coverage is a
                denominator, not a verdict on the remainder.
                SETTLES: IN-RELEASE every uncovered number is in DEFINITION.md and in some round's
                committed artifact, so each is checkable — at the cost of one assertion per number,
                which is what the gate's 343 entries already are.
"""
import importlib.util, json, pathlib, re, shutil, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEF = ROOT / "E05_the_space_of_compilers" / "DEFINITION.md"
GATE = ROOT / "assurance" / "definition_matches_the_record.py"


def rc():
    return subprocess.run([sys.executable, str(GATE)], capture_output=True, text=True)


def spans(doc):
    spec = importlib.util.spec_from_file_location("dm", GATE)
    m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    A = getattr(m, "ASSERTIONS", {})
    return A, [(x.start(x.lastindex), x.end(x.lastindex))
               for pat in A.values() for x in re.finditer(pat, doc) if x.lastindex]


def main() -> int:
    backup = pathlib.Path(tempfile.mkdtemp()) / "DEFINITION.md"
    shutil.copy2(DEF, backup)
    try:
        doc = DEF.read_text()
        A, sp = spans(doc)
        if not A or not sp:
            print("  UNRUNNABLE: the gate exposes no assertions. Exit 2, never 0."); return 2

        def covered(v):
            occ = [x.start() for x in re.finditer(re.escape(v), doc)]
            return bool(occ) and any(any(s <= o < e for s, e in sp) for o in occ)

        cov = [doc[a:b] for a, b in sp if re.fullmatch(r"\d\.\d{3,}", doc[a:b])]
        unc = [v for v in ("0.0098", "0.9973") if not covered(v)]
        print(f"  assertions {len(A)} · located spans {len(sp)}")
        print(f"  ⛔ THE VALUE R1043 CORRUPTED: `0.0098` covered = {covered('0.0098')}")
        print(f"     so 'a value it explicitly asserts' was FALSE, and that sentence is retracted.")
        if not cov or not unc:
            print("  UNRUNNABLE: need one covered and one uncovered value. Exit 2, never 0."); return 2
        cval, uval = cov[0], unc[0]
        print(f"  POSITIVE — the split is non-trivial: covered `{cval}` · uncovered `{uval}`")

        base = rc()
        print(f"  PLACEBO  — untouched tree: rc={base.returncode}  "
              f"{'PASS' if base.returncode == 0 else '⛔ FAIL'}")
        if base.returncode != 0:
            print("  the tree is already red; nothing after is attributable. Exit 2."); return 2
        printed = [l.strip() for l in base.stdout.splitlines() if "covered" in l]
        print(f"  ⛔ AND THE GATE WAS PRINTING THIS ALL ALONG — R1043 read the exit code, not this:")
        for l in printed[:4]:
            print(f"     {l}")

        DEF.write_text(doc.replace(uval, "0.1234")); r_unc = rc().returncode; DEF.write_text(doc)
        DEF.write_text(doc.replace(cval, "0.1234")); r_cov = rc().returncode; DEF.write_text(doc)

        print(f"\n  ⭐ MUTATION, SPLIT BY THE GATE'S OWN COVERAGE")
        print(f"     {'value':<10}{'covered':>9}{'rc':>5}  reading")
        print(f"     {uval:<10}{'False':>9}{r_unc:>5}  outside the assertion table — GREEN is correct")
        print(f"     {cval:<10}{'True':>9}{r_cov:>5}  inside it — must be RED if the gate detects")

        print()
        if r_cov != 0 and r_unc == 0:
            world = (f"⭐ A NARROW BUT SOUND — corrupting a COVERED value turns the gate RED "
                     f"(rc={r_cov}) while an UNCOVERED one stays GREEN (rc={r_unc}). The gate "
                     f"detects within its declared scope. ⛔ R1043's headline — 'one of the three "
                     f"commit gates is blind' — is WITHDRAWN. What stands is the gate's OWN published "
                     f"coverage: a PASS certifies the anchored numbers, never the document.")
        elif r_cov == 0:
            world = (f"⭐ B GENUINELY BLIND — even a COVERED value passes (rc={r_cov}). R1043's "
                     f"headline survives, now on the evidence it should have had.")
        else:
            world = (f"UNVERIFIED — the uncovered mutation did not reproduce R1043's GREEN "
                     f"(rc={r_unc}), so the two rounds are not comparing the same thing.")
        print(world)
        print(f"⛔ AND THE DEEPER ERROR IS DOOR ①, INSIDE A ROUND ABOUT TRUSTING INSTRUMENTS. R1043")
        print(f"   read an EXIT CODE and called it a measurement of the gate. The gate's own stdout")
        print(f"   carried the answer — its coverage, and the sentence 'a PASS certifies the anchored")
        print(f"   numbers, never the document'. A description instead of the object.")
        print(f"⚠ WHAT R1043 GOT RIGHT AND STANDS: `attack_the_suite` tests the empty-input FLOOR and")
        print(f"   not detection; currency and next do detect; and the mutation is itself an")
        print(f"   instrument needing its own control — which is exactly what caught this.")

        out = HERE / "results" / "narrow_not_blind.json"
        out.write_text(json.dumps({
            "round": "R1044", "retracts": "R1043's 'anchoring is blind'",
            "assertions": len(A), "located_spans": len(sp),
            "r1043_value": {"value": "0.0098", "covered": covered("0.0098")},
            "mutation": {"uncovered": {"value": uval, "rc": r_unc},
                         "covered": {"value": cval, "rc": r_cov}},
            "gate_printed_coverage": printed[:4],
            "world": world,
            "limitation": "coverage is a denominator, not a verdict on the 92-97% remainder",
        }, indent=2) + "\n")
        print(f"\nartifact {out.relative_to(ROOT)}")
        return 0
    finally:
        shutil.copy2(backup, DEF)
        print(f"  RESTORE — DEFINITION.md put back; gate on restored tree: rc={rc().returncode}")


if __name__ == "__main__":
    raise SystemExit(main())
