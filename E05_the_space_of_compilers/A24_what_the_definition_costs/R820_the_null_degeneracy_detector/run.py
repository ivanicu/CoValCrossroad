#!/usr/bin/env python3
"""R820 · the null-degeneracy detector, validated against ten labelled cases.

R819 counted five degenerate negative controls this session and proposed a gate. CHECK #422 found
the architectural problem: the committed artifacts do NOT contain the degenerate nulls — each was
repaired before anything was written — so a commit-time gate like the existing seven is structurally
blind to this class. But the broken values ARE committed, in RETRACTIONS.md entries 1214, 1217,
1226, 1234 and 1244, which gives five known-BROKEN nulls and five known-REPAIRED counterparts.

ESTIMAND        E1 two candidate rules · E2 ⭐ validation on ten labelled cases · E3 ⭐ the threshold
                sweep · E4 the installed runtime assertion
IDENTIFICATION  the cases are hand-transcribed, which §4 warns against; every value is therefore
                verified to appear LITERALLY in the file it cites, before any rule is evaluated
DERIVED FIRST   D1 R2 cannot separate R816 from R819's repaired control — both have |null| >
                |observation| with the same sign — so R2 is PREDICTED to false-positive ·
                D2 zero spread destroyed nothing regardless of centre · D3 R813's repaired null is
                the hard case, centre within one sd of the observation · D4 both error directions
                are counted
WORLDS          A R1 separates · B neither does · C both do — B checked FIRST
CONTROLS        OBJECT (literal verification of all ten) · PLACEBO · POSITIVE (spread ladder) ·
                NEGATIVE (a real permutation null)
"""
import hashlib
import json
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
LEDGER = ROOT / "RETRACTIONS.md"
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"

# ---- the ten labelled cases. Each carries the literal string that must be found in `cite`. ------
# ⛔ THE TRANSCRIPTION CHECK FIRED ON 6 OF 10 AND IT WAS RIGHT. My first table used ASCII hyphens
# where the committed files use the UNICODE MINUS U+2212, and cited RETRACTIONS.md for two values
# that live only in a round README. That is §4's warning arriving on schedule: a hand-built case set
# is a transcription, and the transcription is the thing that fails. Every literal below was located
# at its source before being written here, and each is re-verified at run time.
R = lambda n: next(ARC.glob(f"{n}_*")) / "README.md"                    # noqa: E731
CASES = [
    # round, label, null_lo, null_hi, observed, cite, literal-string-that-must-appear
    ("R809", "BROKEN", -0.1317, -0.1317, -0.1317, LEDGER, "[\u22120.1317, \u22120.1317]"),
    ("R810", "BROKEN", +0.0156, +0.0156, +0.0116, LEDGER, "+0.0156 [+0.0156, +0.0156]"),
    ("R813", "BROKEN", 0.0099, 0.0099, 0.0099, LEDGER, "sd of exactly 0.0000"),
    # ⛔ ENCODED AS A POINT ON THE FIRST RUN, WHICH MANUFACTURED THE SIGNATURE. R816's broken
    # null was NOT degenerate in spread — its output was "-0.870 [-1.283, -0.416]" over 200 draws
    # — only its CENTRE was wrong, overshooting the observation. Encoding a reported centre as a
    # zero-width interval made R1 fire on it and inflated the score to 5/5. The honest interval is
    # below, R1 correctly does NOT fire, and the count returns to the 4/5 R819 predicted.
    ("R816", "BROKEN", -1.283, -0.416, -0.553, LEDGER, "\u22120.870"),
    ("R819", "BROKEN", +0.5162, +0.5162, +0.5162, LEDGER, "+0.5162 [+0.5162, +0.5162]"),
    ("R809", "REPAIRED", -0.1317, +0.1021, -0.1317, LEDGER, "[\u22120.1317, +0.1021]"),
    ("R810", "REPAIRED", -0.1325, -0.1107, +0.0116, LEDGER,
     "\u22120.1211 [\u22120.1325, \u22120.1107]"),
    ("R813", "REPAIRED", 0.0090, 0.0104, 0.0099, LEDGER, "0.0097 \u00b1 0.0007"),
    ("R816", "REPAIRED", -0.091, +0.086, +0.368, LEDGER, "+0.004 [\u22120.091, +0.086]"),
    ("R819", "REPAIRED", +1.0591, +1.2287, +0.0617, "R819", "+1.1439 \u00b1 0.0848"),
]



def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    raise TypeError(type(o))


def rule_zero_spread(lo, hi, obs, eps=1e-9):
    """R1: a null whose spread is below eps destroyed nothing, whatever its centre."""
    return (hi - lo) <= eps


def rule_overshoot(lo, hi, obs):
    """R2: the null's centre lies further from zero than the observation."""
    return abs((lo + hi) / 2.0) > abs(obs)


def main():
    out = {"instrument_unit": "a declared NULL", "claim_unit": "a RULE"}

    # ================= OBJECT ====================================================================
    print("  OBJECT CHECK - every transcribed value must appear LITERALLY in the file it cites")
    print("  (§4: a control validated only against cases you invented is validated against your")
    print("  imagination. These are transcriptions, so the transcription is what gets checked.)")
    texts = {}
    verified, missing = [], []
    for rnd, lab, lo, hi, obs, cite, lit in CASES:
        path = R(cite) if isinstance(cite, str) else cite
        if path not in texts:
            texts[path] = path.read_text()
        ok = lit in texts[path]
        (verified if ok else missing).append((rnd, lab, lit))
        print(f"     {rnd:<6}{lab:<10} {'found' if ok else 'MISSING':<8} in {path.name:<28} {lit!r}")
    print(f"     verified {len(verified)} of {len(CASES)}   missing {len(missing)}")
    if missing:
        print("  UNRUNNABLE: a transcribed value is not in the file it cites. Exit 2, never 0.")
        return 2
    out["object"] = {"verified": len(verified), "total": len(CASES)}

    # ================= E1/E2 · the two rules on ten cases ========================================
    print("\n  E1/E2 - THE TWO RULES ON TEN LABELLED CASES")
    print(f"     {'round':<7}{'label':<11}{'null':>22}{'observed':>11}{'R1 zero-spread':>17}"
          f"{'R2 overshoot':>15}")
    rows = []
    for rnd, lab, lo, hi, obs, cite, lit in CASES:
        r1 = rule_zero_spread(lo, hi, obs)
        r2 = rule_overshoot(lo, hi, obs)
        rows.append({"round": rnd, "label": lab, "lo": lo, "hi": hi, "obs": obs,
                     "r1": bool(r1), "r2": bool(r2)})
        print(f"     {rnd:<7}{lab:<11}[{lo:+.4f}, {hi:+.4f}]{obs:>11.4f}"
              f"{('FIRES' if r1 else '—'):>17}{('FIRES' if r2 else '—'):>15}")
    b = [r for r in rows if r["label"] == "BROKEN"]
    g = [r for r in rows if r["label"] == "REPAIRED"]
    r1b, r1g = sum(r["r1"] for r in b), sum(r["r1"] for r in g)
    r2b, r2g = sum(r["r2"] for r in b), sum(r["r2"] for r in g)
    print(f"\n     R1 zero-spread : fires on {r1b}/5 BROKEN, {r1g}/5 REPAIRED")
    print(f"     R2 overshoot   : fires on {r2b}/5 BROKEN, {r2g}/5 REPAIRED")
    print(f"     ⭐ D1 predicted R2 would false-positive on a PASSING control: it fires on "
          f"{r2g} repaired case(s) — {[r['round'] for r in g if r['r2']]}")
    out["e2"] = {"rows": rows, "r1_broken": r1b, "r1_repaired": r1g,
                 "r2_broken": r2b, "r2_repaired": r2g}

    # ================= E3 · the threshold sweep ==================================================
    print("\n  E3 - THE THRESHOLD SWEEP FOR R1")
    sweep = {}
    for eps in (0.0, 1e-9, 1e-6, 1e-4, 1e-3, 1e-2):
        fb = sum(rule_zero_spread(r["lo"], r["hi"], r["obs"], eps) for r in b)
        fg = sum(rule_zero_spread(r["lo"], r["hi"], r["obs"], eps) for r in g)
        sweep[eps] = (fb, fg)
        print(f"     eps={eps:<8} BROKEN {fb}/5   REPAIRED {fg}/5   "
              f"{'separates' if fb >= 4 and fg == 0 else 'does NOT separate'}")
    good = [e for e, (fb, fg) in sweep.items() if fb >= 4 and fg == 0]
    print(f"     ⭐ thresholds that separate: {good}   widest safe eps: "
          f"{max(good) if good else 'none'}")
    out["e3"] = {str(k): v for k, v in sweep.items()}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    plac = (rule_zero_spread(-0.05, +0.05, 0.0), rule_overshoot(-0.05, +0.05, 0.0))
    plac_ok = not plac[0] and not plac[1]
    print(f"     PLACEBO   a null with genuine spread centred on zero: R1 {plac[0]}, R2 {plac[1]}   "
          f"{'PASS - silent' if plac_ok else 'FAIL'}")
    print("     POSITIVE  a dose ladder on spread; R1 must fire below its threshold and not above")
    lad = {}
    for sd in (0.0, 1e-9, 1e-6, 1e-3, 1e-2):
        lad[sd] = rule_zero_spread(-sd, +sd, 0.5, eps=1e-6)
        print(f"        sd={sd:<8} R1 at eps=1e-6: {'FIRES' if lad[sd] else '—'}")
    pos_ok = lad[0.0] and lad[1e-9] and not lad[1e-3] and not lad[1e-2]
    print(f"        fires at sd=0 and sd=1e-9, silent at 1e-3 and 1e-2: {pos_ok}   "
          f"{'PASS - monotone and can fail' if pos_ok else 'FAIL'}")
    r819 = next(r for r in g if r["round"] == "R819")
    neg_ok = not rule_zero_spread(r819["lo"], r819["hi"], r819["obs"])
    print(f"     NEGATIVE  R819's own REPAIRED six-member null "
          f"[{r819['lo']:+.4f}, {r819['hi']:+.4f}]: R1 "
          f"{'FIRES' if not neg_ok else 'silent'}   {'PASS' if neg_ok else 'FAIL'}")
    print(f"     NOISE FLOOR  the detector is DETERMINISTIC given its inputs — it has no spread, "
          f"and inventing one would be the arithmetic trap")
    gate = not missing and plac_ok and pos_ok and neg_ok
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo_ok": plac_ok, "ladder": {str(k): bool(v) for k, v in lad.items()},
                       "positive_ok": pos_ok, "negative_ok": neg_ok, "gate": gate}

    # ================= E4 · install ==============================================================
    print("\n  E4 - THE INSTALLED ASSERTION")
    lib = ROOT / "assurance/null_is_informative.py"
    lib.write_text('''"""A runtime assertion for negative controls. Installed by R820.

Five degenerate negative controls shipped in one session (R809, R810, R813, R816, R819) and every
one was caught by its output looking wrong, never by a check. A commit-time gate cannot catch them:
each was repaired before anything was written, so the artifact holds the repaired value.

Call this where the null is computed, not where it is reported.

    from assurance.null_is_informative import assert_null_is_informative
    assert_null_is_informative(nulls, observed, name="R821 negative control")

VALIDATED by R820 against ten labelled cases: fires on 4 of 5 known-broken nulls and 0 of 5
known-repaired ones. The fifth broken case (R816, an OVERSHOOT) is NOT caught, and the rule that
would catch it false-positives on a passing control — see R820's D1.
"""
import numpy as np

EPS = 1e-9


def assert_null_is_informative(nulls, observed, name="negative control", eps=EPS):
    """Raise if a null distribution destroyed nothing.

    nulls    : array-like of draws from the null
    observed : the real statistic the null is meant to be compared against
    """
    a = np.asarray(nulls, float)
    if a.size < 2:
        raise AssertionError(f"{name}: a null needs >=2 draws, got {a.size}")
    spread = float(a.max() - a.min())
    if spread <= eps:
        raise AssertionError(
            f"{name}: DEGENERATE NULL. spread {spread:.3e} <= {eps:.0e} over {a.size} draws "
            f"(centre {a.mean():+.6f}, observed {observed:+.6f}). A null with no variation "
            f"destroyed nothing -- the permutation is a no-op on this statistic. "
            f"Check whether the statistic is invariant to it BY CONSTRUCTION.")
    return {"spread": spread, "centre": float(a.mean()), "observed": float(observed),
            "sd": float(a.std())}
''')
    print(f"     wrote {lib.relative_to(ROOT)}")
    check = subprocess.run([sys.executable, "-c",
                            "import sys; sys.path.insert(0,'.');"
                            "from assurance.null_is_informative import assert_null_is_informative as f;"
                            "import numpy as np;"
                            "print('good null ->', f(np.linspace(-.1,.1,50), 0.5)['spread']>0);"
                            "\ntry:\n f(np.zeros(50), 0.5)\n print('degenerate -> NOT RAISED')\n"
                            "except AssertionError:\n print('degenerate -> raised')"],
                           cwd=ROOT, capture_output=True, text=True)
    print("     smoke test:", check.stdout.strip().replace("\n", " | ") or check.stderr.strip()[:200])
    installed = "raised" in check.stdout
    out["e4"] = {"installed": installed, "path": str(lib.relative_to(ROOT))}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif r1b >= 4 and r1g == 0:
        world = "A"
    elif r1g > 0:
        world = "B"
    else:
        world = "C"
    print(f"     R1 {r1b}/5 broken and {r1g}/5 repaired   R2 {r2b}/5 broken and {r2g}/5 repaired"
          f"   assertion installed and raising: {installed}  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/detector_validation.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
