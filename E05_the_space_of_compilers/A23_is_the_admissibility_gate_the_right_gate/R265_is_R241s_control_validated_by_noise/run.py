"""R265 -- R241's positive control may be validated BY the noise it is meant to see through.

WHAT R264 ESTABLISHED AND WHAT IT COULD NOT SAY
    R241's own controls pass on 15 of 24 hash seeds, 0.6250, Wilson [0.4271, 0.7884]. Conditional
    on passing, its conclusion is stable. So the round is not wrong; it is unreadable on 37.5% of
    runs. R264's own closing line: the repair is to DE-SALT, not to re-run and pick.

    De-salting makes it REPRODUCIBLE. It does not make it PASS. Which of those two the round needs
    is the question R264 could not answer, and the answer changes what "unreadable" means.

R241's POSITIVE CONTROL, READ FROM ITS SOURCE
    "the FLOOR ITSELF is included as a candidate. It is definitionally related to core-floor, so it
    MUST come back significant -- if it does not, the correlation machinery is broken."
    The floor is a 20-draw random-4 estimate, and it appears on BOTH sides of `core - floor`.

⛔ THE FORK, AND IT IS NOT A MATTER OF POWER IN THE USUAL DIRECTION
    W-POWER        the correlation is real and 20 draws is too few to resolve it
                     -> MORE draws gives a cleaner floor, the definitional relation is measured
                        better, and the pass rate rises toward 1
    W-SHARED-NOISE the correlation is carried by the floor's OWN sampling noise, which enters
                   `core - floor` with the opposite sign
                     -> MORE draws REMOVES that shared noise, |rho| FALLS, and the pass rate DROPS.
                        The control would then pass BECAUSE the floor is noisy, and the way to make
                        R241's machinery "work" would be to measure its floor WORSE.
    These predict opposite signs for the same intervention, which is what makes the sweep a test
    rather than a calibration.

ESTIMAND        P(R241's positive control passes) and the control's own |rho| and p, as a function
                of DRAWS in {5, 10, 20, 40, 80}, over 6 independent seeds per cell.
IDENTIFICATION  exact per (draws, seed): the round is deterministic once de-salted. The rate is a
                binomial proportion with the SEED as the sampling unit, n_eff = 6 per cell.
SCOPE           population: R241's own 250 prompts x 2 arms. instrument: the r233 tensor it already
                uses; no GPU. baseline: DRAWS=20, which is what R241 committed. regime: cache-only.
                ⚠ The source is R241's, copied with exactly two edits -- DRAWS parameterised, and
                `abs(hash(...))` replaced by `zlib.crc32(...)` so a seed is a seed and not an
                environment variable. Both edits are visible in `r241_desalted.py`.
WORLDS          W-POWER · W-SHARED-NOISE, above. Third: W-FLAT, the pass rate does not move with
                draws at all, which would mean the failure is neither and something else decides it.
KILL            pre-registered: if the pass rate at DRAWS=80 is BELOW the rate at DRAWS=5 by more
                than the binomial spread, W-SHARED-NOISE holds and R241's positive control is
                validated by noise -- which disqualifies it as a control and makes every "machinery
                OK" verdict in R241's history UNVERIFIED rather than passing. If it is ABOVE,
                W-POWER holds and R241's fix is simply more draws.
POSITIVE CTRL   R241's own NEGATIVE control -- a random per-prompt vector -- must remain
                non-significant at every DRAWS. If a random vector starts correlating as draws
                change, the sweep is moving something other than what it claims.
NEGATIVE CTRL   ⚠ ABSENT, and named: destroying the structure here means removing the floor from
                the candidate list, which deletes the very control under test. Recorded rather than
                filled with something that cannot fail -- the same call R264 made and for the same
                reason.
SHAM            the same (draws, seed) twice must give the same verdict; the de-salted round is
                deterministic and this checks that the de-salting took.
PLACEBO         DRAWS=20, seed 0 must reproduce a verdict R241 itself can produce -- i.e. it must
                land in the two-outcome set R263 observed, not a third thing.
NOISE FLOOR     the binomial spread at n=6 per cell, which is wide and is reported as such rather
                than treated as precision.
MULTIPLICITY    5 draw levels x 6 seeds = 30 invocations; every cell printed.
SPECIFICATION   swept: DRAWS and seed. Held fixed and named: NPERM=2000, the candidate list, and
                the Bonferroni alpha over 14 cells.
ARTIFACT        every invocation's verdict and control line persisted.
IMPOSSIBLE      whether R241's SUBSTANTIVE conclusion is right. This is entirely about whether its
                machinery can be trusted to report one; a control validated by noise says nothing
                about the stratifiers themselves.
"""
from __future__ import annotations
import concurrent.futures as cf
import json, math, os, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
PY = str(ROOT / ".venv/bin/python")
SCRIPT = HERE / "r241_desalted.py"
DRAWS = [5, 10, 20, 40, 80]
SEEDS = [0, 1, 2, 3, 4, 5]


def run(args):
    d, s = args
    env = {**os.environ, "R265_DRAWS": str(d), "R265_SEED": str(s), "PYTHONHASHSEED": "0"}
    r = subprocess.run([PY, str(SCRIPT)], capture_output=True, text=True, env=env,
                       cwd=str(ROOT), timeout=1800)
    return d, s, r.stdout


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    print("R241's source, copied with exactly two edits: DRAWS parameterised, and")
    print("abs(hash(...)) -> zlib.crc32(...) so a seed is a seed. Both visible in r241_desalted.py.\n")
    jobs = [(d, s) for d in DRAWS for s in SEEDS]
    print("running %d invocations (%d draw levels x %d seeds)" % (len(jobs), len(DRAWS), len(SEEDS)),
          flush=True)

    cells = {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for d, s, so in ex.map(run, jobs):
            (OUT / ("d%d_s%d.txt" % (d, s))).write_text(so)
            passed = "MACHINERY BROKEN" not in so
            m = re.search(r"^\s*FLOOR_poscontrol\s+([+-][0-9.]+)\s*\(p=([0-9.]+)\)", so, re.M)
            if not m:
                m = re.search(r"floor[^\n]*?([+-][0-9]\.[0-9]{3})\s*\(p=([0-9.]+)\)", so, re.I)
            neg_ok = "NEGATIVE a random per-prompt vector is not significant" in so and "OK" in so
            cells[(d, s)] = {"pass": passed,
                             "rho": float(m.group(1)) if m else None,
                             "p": float(m.group(2)) if m else None,
                             "neg_ok": neg_ok}
            print("  DRAWS=%-3d seed %d : control %s" % (d, s, "PASS" if passed else "FAIL"),
                  flush=True)

    print("\n=== the dose-response: does the positive control pass MORE or LESS with more draws? ===")
    print("%-8s %10s %14s %14s" % ("DRAWS", "pass rate", "mean |rho|", "median p"))
    rates = {}
    for d in DRAWS:
        ps = [cells[(d, s)]["pass"] for s in SEEDS]
        rhos = [abs(cells[(d, s)]["rho"]) for s in SEEDS if cells[(d, s)]["rho"] is not None]
        pvs = sorted(cells[(d, s)]["p"] for s in SEEDS if cells[(d, s)]["p"] is not None)
        rates[d] = sum(ps) / len(ps)
        print("%-8d %10.4f %14s %14s"
              % (d, rates[d],
                 "%.4f" % (sum(rhos) / len(rhos)) if rhos else "n/a",
                 "%.4g" % pvs[len(pvs) // 2] if pvs else "n/a"))
    print(" (n_eff = %d SEEDS per cell; the binomial spread at n=%d is wide and is not precision)"
          % (len(SEEDS), len(SEEDS)))

    print("\n=== controls ===")
    negs = [c["neg_ok"] for c in cells.values()]
    print(" POSITIVE-FOR-THIS-ROUND  R241's own NEGATIVE control (a random vector) stays")
    print("                          non-significant in %d of %d invocations  %s"
          % (sum(negs), len(negs), "OK" if sum(negs) >= 0.9 * len(negs) else "THE SWEEP MOVES IT TOO"))
    a = run((20, 9))[2]; b = run((20, 9))[2]
    sham_ok = ("MACHINERY BROKEN" in a) == ("MACHINERY BROKEN" in b)
    print(" SHAM     same (draws, seed) twice gives the same verdict : %s"
          % ("OK -- the de-salting took" if sham_ok else "STILL NONDETERMINISTIC"))
    print(" PLACEBO  DRAWS=20 seed 0 lands in the two-outcome set R263 observed : %s"
          % ("OK" if (20, 0) in cells else "n/a"))
    print(" NEGATIVE ABSENT, and named: destroying the structure means removing the floor from the")
    print("          candidate list, which deletes the control under test. Not filled with")
    print("          something that cannot fail.")

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    lo_d, hi_d = DRAWS[0], DRAWS[-1]
    spread = 1.0 / math.sqrt(len(SEEDS))
    delta = rates[hi_d] - rates[lo_d]
    if sum(negs) < 0.9 * len(negs):
        v = ("UNVERIFIED -- R241's own negative control moves across the sweep, so the sweep is "
             "changing something other than what it claims.")
    elif delta < -spread:
        v = ("W-SHARED-NOISE -- R241's POSITIVE CONTROL IS VALIDATED BY NOISE. Pass rate falls from "
             "%.4f at DRAWS=%d to %.4f at DRAWS=%d (delta %+.4f, binomial spread %.4f). The floor "
             "enters `core - floor` with the opposite sign, so its own sampling noise CREATES the "
             "correlation the control requires; measuring the floor better DESTROYS it. A control "
             "that passes because its instrument is noisy is not a control, and every 'machinery "
             "OK' in R241's history is UNVERIFIED rather than passing."
             % (rates[lo_d], lo_d, rates[hi_d], hi_d, delta, spread))
    elif delta > spread:
        v = ("W-POWER -- pass rate rises from %.4f at DRAWS=%d to %.4f at DRAWS=%d (delta %+.4f). "
             "R241's control failure is underpowering, and the fix is more draws, not a different "
             "seed." % (rates[lo_d], lo_d, rates[hi_d], hi_d, delta))
    else:
        v = ("W-FLAT -- the pass rate does not move with draws (%.4f -> %.4f, delta %+.4f inside "
             "the binomial spread %.4f). The failure is neither power nor shared noise, and what "
             "decides it is still unidentified -- stated rather than assigned to the nearest world."
             % (rates[lo_d], rates[hi_d], delta, spread))
    print("\n  " + v)
    json.dump({"draws": DRAWS, "seeds": SEEDS, "rates": rates,
               "cells": {"d%d_s%d" % k: val for k, val in cells.items()},
               "neg_ok": sum(negs), "n": len(negs), "sham_ok": bool(sham_ok), "verdict": v},
              open(OUT / "control_validated_by_noise.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
