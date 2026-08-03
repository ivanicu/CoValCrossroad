"""R263 -- the five salted cache-only rounds nobody has swept, and one of them concluded a NULL.

WHERE THIS SITS
    R261 counted 13 of 19 E05 rng seeds keyed on a string. R262 swept two of them and found R220's
    comparison survives the axis while R231's SIGN FLIPS across seeds. Five salted cache-only rounds
    remain: R221, R238, R241, R244, R245.

⚠ AND ONE OF THEM CONCLUDED A NULL, WHICH IS THE DANGEROUS CASE
    R241: "NO VALID STRATIFIER EXISTS among the seven per-prompt variables this release carries."
    That null is what closed the `transport` line -- FORMULATION records it as UNVERIFIED with a
    MEASURED REASON rather than a gap, and the reason is R241. A null resting on a floor that moves
    with an environment variable is not a measured reason; it is one draw from a distribution
    nobody looked at. This is the asymmetry realstat names: a false retraction is as permanent as a
    false acquittal, because nobody re-examines a claim its own author withdrew.

ESTIMAND        for each of the five: the headline number(s) under PYTHONHASHSEED in {0,1,2,3}, the
                spread, and whether the round's own VERDICT STRING changes.
                The verdict string is the estimand that matters here -- a floor can move without
                changing anything, and the question is whether the CONCLUSION is seed-dependent.
IDENTIFICATION  exact; each round is deterministic given a hash seed. Comparing verdict strings is
                a byte comparison, not an inference.
SCOPE           population: R221, R238, R241, R244, R245 -- every salted round in E05 that reads
                only cached tensors. instrument: those caches; no GPU. baseline: each round's own
                committed output. regime: 4 hash seeds, 900s timeout per invocation.
WORLDS          W-STABLE   the floors move but no verdict does
                             -> the salting is exposure without consequence outside R231
                W-VERDICT  at least one verdict string differs across seeds
                             -> that round's CONCLUSION is a function of an environment variable,
                                and if it is R241's, the `transport` line loses its measured reason
KILL            pre-registered: any round whose verdict string is not byte-identical across all
                four seeds has its conclusion DOWNGRADED to seed-dependent. If R241's differs, the
                `transport: UNVERIFIED with a measured reason` line in FORMULATION reverts to
                `UNVERIFIED, reason itself unverified`.
POSITIVE CTRL   R231 again, whose verdict string R262 showed contains a floor that moves. Its
                verdict must DIFFER across seeds, or the string comparison is not sensitive enough
                to detect what we already know is there. This is the control that makes a
                byte-identical result meaningful rather than vacuous.
NEGATIVE CTRL   R230 and R228, int-keyed: verdict strings must be byte-identical across seeds.
SHAM            the same round twice at the same seed -- identical, or the round has some other
                nondeterminism and the sweep is unreadable.
PLACEBO         comparing a verdict string to itself returns identical, trivially.
NOISE FLOOR     the negative control's movement, which must be exactly zero.
MULTIPLICITY    8 rounds x 4 seeds = 32 invocations; every round's status printed, including the
                ones that time out.
SPECIFICATION   swept: PYTHONHASHSEED x round.
ARTIFACT        each invocation's stdout persisted per seed.
IMPOSSIBLE      R233, which needs 33,320 GPU judgements per seed. Checked, not assumed -- R262
                already established that the OTHER two rounds I had called GPU-bound are not.
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

TARGETS = [
    ("R221", "A16_what_a_compiler_is_and_what_its_operations_cost/R221_contamination", "salted"),
    ("R238", "A18_the_candidate_set_wall_was_wrong/R238_difficulty_matched", "salted"),
    ("R241", "A18_the_candidate_set_wall_was_wrong/R241_find_a_valid_stratifier", "salted"),
    ("R244", "A21_missing_weight_semantics/R244_not_rated_or_rated_zero", "salted"),
    ("R245", "A21_missing_weight_semantics/R245_does_it_move_the_formulation", "salted"),
    ("R231", "A17_which_definitions_of_core_are_identifiable/R231_the_official_cores_class",
     "positive"),
    ("R230", "A17_which_definitions_of_core_are_identifiable/R230_the_class_not_the_member",
     "negative"),
    ("R228", "A17_which_definitions_of_core_are_identifiable/R228_the_largest_core_this_release_can_carry",
     "negative"),
]


def verdict_of(text):
    """the block after the last KILL / VERDICT banner -- the round's own conclusion, verbatim."""
    for marker in ("PRE-REGISTERED KILL", "VERDICT", "KILL"):
        i = text.rfind(marker)
        if i >= 0:
            return re.sub(r"\s+", " ", text[i:]).strip()
    return None


def run_one(args):
    label, rel, seed = args
    try:
        r = subprocess.run([PY, str(E05 / rel / "run.py")], capture_output=True, text=True,
                           env={**os.environ, "PYTHONHASHSEED": seed}, cwd=str(ROOT), timeout=900)
        return label, seed, r.stdout, r.returncode
    except subprocess.TimeoutExpired:
        return label, seed, "", -1


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(l, rel, s) for l, rel, _k in TARGETS for s in SEEDS]
    print("running %d invocations (%d rounds x %d hash seeds)" % (len(jobs), len(TARGETS),
                                                                  len(SEEDS)), flush=True)
    outs, rcs = {}, {}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for label, seed, so, rc in ex.map(run_one, jobs):
            outs[(label, seed)] = so; rcs[(label, seed)] = rc
            (OUT / ("%s_seed%s.txt" % (label, seed))).write_text(so)
            print("  %-5s seed %s  rc=%-3d %d chars" % (label, seed, rc, len(so)), flush=True)

    print("\n=== per round: is the VERDICT STRING byte-identical across hash seeds? ===")
    res = {}
    for label, _rel, kind in TARGETS:
        vs = [verdict_of(outs[(label, s)]) for s in SEEDS]
        ok = [v for v in vs if v]
        if len(ok) < len(SEEDS):
            res[label] = {"kind": kind, "status": "INCOMPLETE",
                          "completed": len(ok), "identical": None}
            print(" %-5s %-9s only %d of 4 invocations produced a verdict -- reported INCOMPLETE, "
                  "not as a null" % (label, kind, len(ok)))
            continue
        ident = len(set(ok)) == 1
        res[label] = {"kind": kind, "status": "ok", "identical": bool(ident),
                      "n_distinct": len(set(ok))}
        print(" %-5s %-9s %d distinct verdict string(s)  %s"
              % (label, kind, len(set(ok)),
                 "IDENTICAL" if ident else "DIFFERS ACROSS SEEDS"))

    print("\n=== controls ===")
    pos = res.get("R231", {})
    pos_ok = pos.get("identical") is False
    print(" POSITIVE R231's verdict must DIFFER (R262 showed its floor moves) : %s"
          % ("OK -- the comparison is sensitive" if pos_ok
             else "THE STRING COMPARISON IS NOT SENSITIVE; a byte-identical result below is vacuous"))
    neg_ok = all(res.get(l, {}).get("identical") is True for l in ("R230", "R228"))
    print(" NEGATIVE R230 and R228 (int-keyed) must be IDENTICAL : %s"
          % ("OK" if neg_ok else "MOVED -- something other than string hashing is nondeterministic"))
    a = run_one(("R230", "A17_which_definitions_of_core_are_identifiable/R230_the_class_not_the_member",
                 "5"))[2]
    b = run_one(("R230", "A17_which_definitions_of_core_are_identifiable/R230_the_class_not_the_member",
                 "5"))[2]
    print(" SHAM     same round twice at the same seed identical : %s" % ("OK" if a == b else "NO"))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    salted = [l for l, _r, k in TARGETS if k == "salted"]
    differ = [l for l in salted if res.get(l, {}).get("identical") is False]
    incomplete = [l for l in salted if res.get(l, {}).get("status") == "INCOMPLETE"]
    if not pos_ok or not neg_ok:
        v = ("UNVERIFIED -- positive sensitive=%s, negative identical=%s. The string comparison "
             "cannot be trusted either way." % (pos_ok, neg_ok))
    elif differ:
        v = ("SEED-DEPENDENT CONCLUSIONS at %s. Those rounds' verdicts are a function of "
             "PYTHONHASHSEED and are DOWNGRADED. %s"
             % (differ,
                ("⛔ R241 IS AMONG THEM, so FORMULATION's `transport: UNVERIFIED with a measured "
                 "reason` reverts to `UNVERIFIED, and the reason is itself unverified` -- a null "
                 "resting on a floor that moves is one draw, not a measurement."
                 if "R241" in differ else
                 "R241 is NOT among them, so the transport line's measured reason survives.")))
    else:
        v = ("All %d salted cache-only rounds give a BYTE-IDENTICAL verdict across four hash seeds, "
             "and the positive control confirms the comparison can detect a difference. The salting "
             "R261 counted is exposure WITHOUT CONSEQUENCE outside R231 -- which is a real result "
             "about the arc and not a failure to find one." % len(salted))
    if incomplete:
        v += (" ⚠ %s did not complete under all four seeds and are reported INCOMPLETE rather than "
              "folded into either answer." % incomplete)
    print("\n  " + v)
    json.dump({"results": res, "positive_ok": bool(pos_ok), "negative_ok": bool(neg_ok),
               "sham_ok": bool(a == b), "verdict": v},
              open(OUT / "remaining_salted.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
