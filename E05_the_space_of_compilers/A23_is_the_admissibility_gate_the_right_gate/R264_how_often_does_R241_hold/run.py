"""R264 -- R241's null is a coin flip. Four seeds established THAT; this measures the RATE.

WHAT R263 FOUND AND WHY FOUR SEEDS IS NOT ENOUGH
    R241 concluded "NO VALID STRATIFIER EXISTS among the seven per-prompt variables this release
    carries", and FORMULATION used that null to close the `transport` line -- recorded as
    "UNVERIFIED with a MEASURED REASON rather than a gap".

    Re-run under PYTHONHASHSEED 0/1/2/3, its verdict flips:
        seeds 0, 3  ->  "NO VALID STRATIFIER EXISTS ..."
        seeds 1, 2  ->  "UNVERIFIED -- the correlation machinery did not pass its own controls"

    Two of four is not a rate. It is consistent with anything from 15% to 85% at n=4, and the
    difference matters: a round whose controls fail 10% of the time is a round with a rare glitch,
    and one whose controls fail 50% of the time has no verdict at all. FORMULATION currently
    carries the first reading by default, because it quotes the published run.

ESTIMAND        P(R241's own controls pass), over PYTHONHASHSEED in 0..23, with a Wilson interval;
                and, conditional on passing, whether the substantive conclusion is stable.
IDENTIFICATION  exact per seed -- the round is deterministic given a hash seed. The rate is a
                binomial proportion over a sample of seeds, and the seeds are the sampling unit,
                so n_eff = 24 and not the number of prompts inside each run.
SCOPE           population: PYTHONHASHSEED 0..23, which is a sample from the space the environment
                actually varies over. instrument: R241's UNMODIFIED source -- nothing is edited, so
                this measures the committed artifact and not a repair of it. baseline: the
                published run, whose seed is unrecorded. regime: cache-only, no GPU.
WORLDS          W-RARE     the control failure is a rare glitch
                             -> pass rate above ~0.85, and the published null is typical
                W-COIN     it is close to even
                             -> the round has no verdict, and every downstream use of its null is
                                a citation of one draw
                W-MOSTLY-FAILS pass rate below ~0.5
                             -> the published run is the UNUSUAL one, and the honest default
                                reading of R241 is that its controls do not behave
KILL            pre-registered: if the Wilson 95% interval on the pass rate excludes 0.9, R241's
                null cannot be quoted without its rate, and FORMULATION's `transport` line must
                carry the rate rather than the verdict. If the interval excludes 0.5 on the low
                side, the published run is atypical and that must be said in those words.
POSITIVE CTRL   R230, int-keyed: its verdict must be identical at all 24 seeds, giving a pass rate
                of exactly 1.0. This proves the harness can observe a stable round, so a rate below
                1 for R241 is about R241 and not about the harness.
NEGATIVE CTRL   ⚠ THERE IS NO USEFUL NEGATIVE CONTROL FOR A RATE MEASURED THIS WAY, and inventing
                one would be theatre. Destroying the structure here means changing R241's source,
                which would stop measuring the committed artifact. Recorded as ABSENT with the
                reason, per the register discipline, rather than filled with something that
                cannot fail.
SHAM            the same seed twice must give the same verdict -- if not, something beyond string
                hashing is nondeterministic and the rate is not a property of the seed.
PLACEBO         R230's rate must be exactly 1.0000, not approximately.
NOISE FLOOR     the Wilson interval is the floor; a rate from 24 draws cannot resolve better.
MULTIPLICITY    2 rounds x 24 seeds; both rates reported with intervals.
SPECIFICATION   swept: PYTHONHASHSEED 0..23. Not swept, and named: which of R241's controls fails,
                extracted from the output rather than inferred.
ARTIFACT        every verdict string persisted per seed.
IMPOSSIBLE      whether the PUBLISHED run's seed was typical. Python's hash seed is not recorded in
                any artifact, so the published run cannot be located in this distribution -- only
                compared to it. That is a permanent gap in the committed round and the reason the
                repair is to de-salt, not to re-run.
"""
from __future__ import annotations
import concurrent.futures as cf
import json, math, os, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
E05 = ROOT / "E05_the_space_of_compilers"
PY = str(ROOT / ".venv/bin/python")
SEEDS = [str(i) for i in range(24)]
R241 = "A18_the_candidate_set_wall_was_wrong/R241_find_a_valid_stratifier"
R230 = "A17_which_definitions_of_core_are_identifiable/R230_the_class_not_the_member"


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 2
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def verdict(text):
    i = text.rfind("PRE-REGISTERED KILL")
    if i < 0:
        i = text.rfind("VERDICT")
    if i < 0:
        return None
    body = [l.strip() for l in text[i:].splitlines() if l.strip() and not set(l.strip()) <= {"="}]
    return " ".join(body[1:])[:400] if len(body) > 1 else None


def run(rel, seed):
    r = subprocess.run([PY, str(E05 / rel / "run.py")], capture_output=True, text=True,
                       env={**os.environ, "PYTHONHASHSEED": seed}, cwd=str(ROOT), timeout=900)
    return seed, r.stdout


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    print("R241's source is UNMODIFIED -- this measures the committed artifact, not a repair of it.")
    print("24 hash seeds, 2 rounds.\n", flush=True)

    res = {}
    for label, rel in (("R241", R241), ("R230", R230)):
        vs = {}
        with cf.ThreadPoolExecutor(max_workers=8) as ex:
            for seed, so in ex.map(lambda s: run(rel, s), SEEDS):
                vs[seed] = verdict(so) or ""
                (OUT / ("%s_seed%s.txt" % (label, seed))).write_text(so)
        res[label] = vs
        print(" %s : %d seeds run, %d distinct verdicts" % (label, len(vs), len(set(vs.values()))))

    print("\n=== POSITIVE CONTROL / PLACEBO ===")
    r230_rate = len({v for v in res["R230"].values()}) == 1
    print(" R230 (int-keyed) identical at all 24 seeds : %s  -> rate %s"
          % ("OK" if r230_rate else "MOVED", "1.0000" if r230_rate else "<1"))
    print("     (this is what proves the harness can observe a STABLE round, so a rate below 1")
    print("      for R241 is a fact about R241 and not about this measurement)")
    s1, s2 = run(R230, "5")[1], run(R230, "5")[1]
    print(" SHAM same seed twice identical : %s" % ("OK" if verdict(s1) == verdict(s2) else "NO"))
    print(" NEGATIVE  ABSENT, with the reason: destroying the structure would mean editing R241's")
    print("           source, which would stop measuring the committed artifact. Not filled with")
    print("           something that cannot fail.")

    print("\n=== the rate ===")
    passes = [s for s, v in res["R241"].items() if "UNVERIFIED" not in v]
    fails = [s for s, v in res["R241"].items() if "UNVERIFIED" in v]
    k, n = len(passes), len(res["R241"])
    lo, hi = wilson(k, n)
    print(" R241's own controls PASS on %d of %d seeds = %.4f" % (k, n, k / n))
    print(" Wilson 95%% interval : [%.4f, %.4f]   (n_eff = %d SEEDS, not prompts)" % (lo, hi, n))
    print(" seeds where the controls FAIL : %s" % ",".join(sorted(fails, key=int)))
    sub = {v for s, v in res["R241"].items() if s in passes}
    print(" among the passing seeds, %d distinct substantive verdict(s)" % len(sub))
    if len(sub) == 1:
        print("   -> conditional on the controls passing, the conclusion IS stable")

    print("\n=== which control fails ===")
    for s in sorted(fails, key=int)[:1]:
        txt = (OUT / ("R241_seed%s.txt" % s)).read_text()
        for line in txt.splitlines():
            if re.search(r"control|POSITIVE|NEGATIVE|chance|null", line, re.I) and "0." in line:
                print("   %s" % line.strip()[:110])

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    if not r230_rate:
        v = ("UNVERIFIED -- the int-keyed positive control moved across seeds, so this harness "
             "cannot observe a stable round and the R241 rate is not attributable.")
    elif hi < 0.9 and lo > 0.5:
        v = ("W-COIN -- R241's controls pass on %d of %d seeds, Wilson [%.4f, %.4f], which excludes "
             "0.9. Its null cannot be quoted without this rate, and FORMULATION's `transport` line "
             "must carry the RATE rather than the verdict. %s"
             % (k, n, lo, hi,
                "Conditional on passing, the conclusion is stable -- so the finding is not that "
                "R241 is wrong, it is that R241 is unreadable on %.0f%% of runs and nobody "
                "recorded which kind the published one was." % (100 * (n - k) / n)
                if len(sub) == 1 else
                "And among the passing seeds the substantive verdict is not even stable."))
    elif lo > 0.9:
        v = ("W-RARE -- the controls pass on %d of %d seeds, Wilson [%.4f, %.4f]. The failure R263 "
             "found is a rare glitch and the published null is typical." % (k, n, lo, hi))
    elif hi < 0.5:
        v = ("W-MOSTLY-FAILS -- the controls pass on only %d of %d seeds, Wilson [%.4f, %.4f]. THE "
             "PUBLISHED RUN IS THE UNUSUAL ONE, and the honest default reading of R241 is that its "
             "controls do not behave." % (k, n, lo, hi))
    else:
        v = ("UNRESOLVED at n=24 -- pass rate %.4f, Wilson [%.4f, %.4f] spans the thresholds. More "
             "seeds would narrow it; the rate is reported rather than rounded to a world."
             % (k / n, lo, hi))
    print("\n  " + v)
    print("\n  PERMANENT GAP: Python's hash seed is not recorded in any artifact, so the PUBLISHED")
    print("  run cannot be located in this distribution -- only compared to it. That is why the")
    print("  repair is to DE-SALT the round, not to re-run it and pick.")
    json.dump({"seeds": SEEDS, "r241_pass": passes, "r241_fail": fails, "k": k, "n": n,
               "wilson": [lo, hi], "r230_stable": bool(r230_rate),
               "distinct_substantive": len(sub), "verdict": v},
              open(OUT / "r241_rate.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
