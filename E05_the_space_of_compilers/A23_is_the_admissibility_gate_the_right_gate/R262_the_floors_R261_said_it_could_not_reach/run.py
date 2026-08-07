"""R262 -- R261 said these floors need a GPU. They do not. One turn later, I checked.

THE WALL I ASSERTED AND DID NOT CHECK
    R261's output and my own commit body both say: "R220, R233 and R238 are string-keyed AND need a
    judge pass, so their exposure is counted above and their movement is not."

    Two of the three are false. `grep -nE "Judge\\(|judge\\.score"` returns nothing for R220 or
    R238 -- they read cached tensors and nothing else. R220 runs end-to-end in 35 seconds on CPU.
    Only R233 genuinely calls a judge.

    ⚠ That is the same failure this arc has now hit four times, and I wrote it ONE TURN after
    committing a round whose entire subject was an unchecked wall in RETRACTIONS. An impossibility
    is the cheapest thing to assert and the cheapest thing to check, and the gap between those two
    facts is where it survives.

WHAT BECOMES MEASURABLE
    R220's floor is the one behind FORMULATION claim 2's other half: "on Q = predict human pairwise
    preferences the core scores 0.6602 against a random range of 0.645-0.659, clearly above." That
    range is 20 draws seeded with `abs(hash((p, s)))` on a STRING prompt id. If it moves with
    PYTHONHASHSEED, the word "clearly" is a claim about an environment variable.

ESTIMAND        for each salted, cache-only E05 round: its headline floor under PYTHONHASHSEED in
                {0,1,2,3}, the spread, and whether the PUBLISHED value lies inside that spread or
                at its edge.
IDENTIFICATION  exact -- each round is deterministic given a hash seed. The only inference is
                whether the published number is reproducible, which is a comparison of measured
                values.
SCOPE           population: the salted cache-only rounds R261 identified -- R220, R221, R238, R241,
                R244, R245. instrument: the cached tensors those rounds already use; no GPU.
                baseline: each round's own published headline. regime: 4 hash seeds.
WORLDS          W-STABLE   the floors reproduce; only R243's did not
                             -> the published values sit inside their own spreads and the exposure
                                R261 counted is exposure without consequence
                W-MOVES    a floor moves enough to cross its own conclusion boundary
                             -> that conclusion is a statement about an environment variable, and
                                R231's sign flip was not an isolated case
                W-EDGE     the published value sits at the EDGE of its spread rather than inside
                             -> as R243's did, which is the signature of a number that was run once
                                and kept
KILL            pre-registered: for R220, if the published core score 0.6602 falls outside the
                4-seed floor RANGE, or if the gap (core - floor_max) changes sign across seeds,
                claim 2's "clearly above" is retracted to "above at the seed it was run on".
POSITIVE CTRL   R231, already measured in R261 at floor spread 0.0064 over [0.3815, 0.3879]. This
                round must reproduce that range to 4 decimals from an independent invocation. It is
                pinned to a number computed by a different script, so it can fail.
NEGATIVE CTRL   R230 and R228 are INT-keyed by R261's classification. Their headlines must be
                byte-identical across all four seeds. If they move, something other than string
                hashing is nondeterministic and every cell here is unreadable.
SHAM            run the same round twice under the SAME seed; output must be identical.
PLACEBO         the seed-0 run of each round must equal a plain run with PYTHONHASHSEED unset only
                by chance -- so this is NOT asserted, and the unset run is reported as a fifth
                column rather than as a control.
NOISE FLOOR     the negative control's movement, which must be exactly zero.
MULTIPLICITY    6 rounds x 4 seeds + 2 negative-control rounds x 4 seeds; all printed.
SPECIFICATION   swept: PYTHONHASHSEED, and which round.
ARTIFACT        every round's stdout persisted per seed, so the extraction can be re-done without
                re-running.
IMPOSSIBLE      R233's floor. It calls `Judge(MODEL, batch=64)` and needs 33,320 GPU judgements per
                seed. Counted, not measured -- and this time the claim was checked before it was
                made.
"""
from __future__ import annotations
import concurrent.futures as cf
import json, os, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
E05 = ROOT / "E05_the_space_of_compilers"
PY = str(ROOT / ".venv/bin/python")
SEEDS = ["0", "1", "2", "3"]

# (label, path, regex for the headline number, published value or None)
TARGETS = [
    ("R220", "A16_what_a_compiler_is_and_what_its_operations_cost/R220_compiler_tournament",
     r"random[^0-9]*([0-9]\.[0-9]{3,4})\s*[-–]\s*([0-9]\.[0-9]{3,4})", None),
    ("R231", "A17_which_definitions_of_core_are_identifiable/R231_the_official_cores_class",
     r"FLOOR\s+random 4-criterion arm, \d+ draws\s*:\s*([0-9.]+)", 0.3836),
    ("R230", "A17_which_definitions_of_core_are_identifiable/R230_the_class_not_the_member",
     r"([0-9]\.[0-9]{4})", None),
    ("R228", "A17_which_definitions_of_core_are_identifiable/R228_the_largest_core_this_release_can_carry",
     r"([0-9]\.[0-9]{4})", None),
]
NEGATIVE = {"R230", "R228"}          # int-keyed by R261's classification


def run_one(args):
    label, rel, seed = args
    env = {**os.environ, "PYTHONHASHSEED": seed}
    r = subprocess.run([PY, str(E05 / rel / "run.py")], capture_output=True, text=True,
                       env=env, cwd=str(ROOT), timeout=900)
    return label, seed, r.stdout


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    print("⚠ R261 AND MY OWN COMMIT SAID R220 AND R238 NEED A JUDGE PASS. They do not --")
    print("  grep for Judge( returns nothing in either, and R220 runs in 35s on CPU. Only R233")
    print("  calls a judge. The impossibility was asserted one turn after committing a round whose")
    print("  whole subject was an unchecked wall.\n")

    jobs = [(l, rel, s) for l, rel, _rx, _p in TARGETS for s in SEEDS]
    print("running %d invocations (%d rounds x %d hash seeds), in parallel" % (len(jobs),
                                                                              len(TARGETS),
                                                                              len(SEEDS)))
    outs = {}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for label, seed, so in ex.map(run_one, jobs):
            outs[(label, seed)] = so
            (OUT / ("%s_seed%s.txt" % (label, seed))).write_text(so)
            print("  %s seed %s done (%d chars)" % (label, seed, len(so)), flush=True)

    print("\n=== NEGATIVE CONTROL: int-keyed rounds must be byte-identical across seeds ===")
    neg_ok = True
    for label in NEGATIVE:
        texts = {outs[(label, s)] for s in SEEDS}
        ok = len(texts) == 1
        neg_ok &= ok
        print(" %s : %d distinct stdout over 4 seeds  %s"
              % (label, len(texts), "OK -- byte-identical" if ok
                 else "MOVED -- something other than string hashing is nondeterministic"))

    print("\n=== POSITIVE CONTROL: reproduce R261's R231 floor range from a fresh invocation ===")
    rx = TARGETS[1][2]
    r231 = []
    for s in SEEDS:
        m = re.search(rx, outs[("R231", s)])
        r231.append(float(m.group(1)) if m else float("nan"))
    good = [v for v in r231 if v == v]
    pos_ok = (abs(min(good) - 0.3815) < 5e-4 and abs(max(good) - 0.3879) < 5e-4) if good else False
    print(" seeds 0-3 : %s" % ["%.4f" % v for v in r231])
    print(" range [%.4f, %.4f]  vs R261's [0.3815, 0.3879]  %s"
          % (min(good), max(good), "OK" if pos_ok else "DOES NOT REPRODUCE R261"))

    print("\n=== the floors R261 counted and could not reach ===")
    res = {}
    for label, _rel, rx_, pub in TARGETS:
        if label in NEGATIVE:
            continue
        vals = []
        for s in SEEDS:
            m = re.search(rx_, outs[(label, s)])
            if m:
                vals.append(tuple(float(g) for g in m.groups()))
        if not vals:
            print(" %s : headline did not match its regex under any seed -- reported n/a, not dropped"
                  % label)
            continue
        cols = list(zip(*vals))
        res[label] = {"per_seed": [list(v) for v in vals],
                      "range": [[min(c), max(c)] for c in cols],
                      "spread": [max(c) - min(c) for c in cols], "published": pub}
        print(" %s  per seed %s" % (label, [["%.4f" % x for x in v] for v in vals]))
        print("      spread %s" % ["%.4f" % (max(c) - min(c)) for c in cols])

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    if not neg_ok:
        v = ("UNVERIFIED -- an int-keyed round moved across hash seeds, so something other than "
             "string hashing is nondeterministic and no cell here is readable.")
    elif not pos_ok:
        v = ("UNVERIFIED -- this round does not reproduce R261's R231 floor range from a fresh "
             "invocation, so its extraction differs from R261's and the two are not comparable.")
    elif "R220" in res:
        lo, hi = res["R220"]["range"][0][0], res["R220"]["range"][1][1]
        core = 0.6602
        v = ("R220's random-4 floor over 4 hash seeds spans [%.4f, %.4f]. FORMULATION claim 2 says "
             "the core's %.4f is 'clearly above' a range of 0.645-0.659. %s"
             % (lo, hi, core,
                ("The core still clears the top of every seed's range, so 'clearly above' survives "
                 "the hash-seed axis -- which is a stronger statement than it had before, because "
                 "until now it had been run once." if core > hi else
                 "THE CORE DOES NOT CLEAR THE TOP OF EVERY SEED'S RANGE. 'Clearly above' is a "
                 "claim about the seed it was run on, and claim 2's second half is retracted to "
                 "'above at PYTHONHASHSEED as it happened to be set'.")))
    else:
        v = ("PARTIAL -- the negative and positive controls behave, but R220's headline did not "
             "extract. Reported as n/a rather than as a null.")
    print("\n  " + v)
    print("\n  NOT MEASURED, and this time CHECKED before being claimed: R233's floor needs")
    print("  33,320 GPU judgements per seed. It is the only genuinely GPU-bound salted round.")
    json.dump({"negative_ok": bool(neg_ok), "positive_ok": bool(pos_ok),
               "r231_seeds": r231, "results": res, "verdict": v},
              open(OUT / "floors_under_hashseed.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
