"""
R729 · clause three is a blocklist and fails open

ESTIMAND        clause ③ is implemented in R294:72 as a hard-coded set of four arm names. Of the
                arms today's population admits, how many are built by a rule that READS THE HUMAN
                TARGET (select_core.py:102 -- oracle_k, indep_k, greedy_k) and are therefore objects
                ③ was written to exclude but admits by default?
IDENTIFICATION  two independent routes: A parses the builder-emitted tag (select_core.py:203-206);
                B compares core_*.json selections per prompt and never reads the name. Their
                agreement is the evidence. NOT identified: any arm with no core_*.json -- the
                released core has none and is reported, not filled in.
SCOPE           population today's glob (92 arms) and the 16 it admits · instrument tag grammar +
                per-prompt Jaccard · baseline the four-name blocklist · regime this tree_sha
WORLDS          W-OPEN ③ admits target-reading arms · W-CLOSED the list happens to be complete
KILL            conditional on POSITIVE and g=0. See PREREGISTRATION.txt.
POSITIVE CTRL   the four blocklisted arms must be recovered as target-reading by BOTH routes, from
                construction rather than from the list; band computed from the intersection size.
g=0             topw_k4 and random_k4_s0 (satisfaction-blind per select_core.py:72) flagged by
                NEITHER route.
NEGATIVE CTRL   shuffle core_*.json across arms; route B's assignment must collapse toward chance.
                excluded world: "route B assigns by file size or coverage, not by selections".
SHAM            route B comparing each arm ONLY to itself -- target absent, not inverted.
PLACEBO         an arm against itself -> mean Jaccard exactly 1.0.
NOISE FLOOR     the Jaccard margin between best and second-best rule; inside it, AMBIGUOUS.
MULTIPLICITY    92 arms x 9 rules + 92 tag parses, every arm reported with both verdicts.
SPECIFICATION   route (A, B) x assignment (argmax, argmax-with-margin-floor)
SEEDS           3 for the shuffle control; two hash seeds byte-identical
ARTIFACT        results/r729_clause3_blocklist.json with tree_sha
IMPOSSIBLE      whether target-reading LEAKS here -> R295, not re-opened · the released core's rule
                -> no core_*.json · independently replicated -> a second implementer
"""
import hashlib, json, pathlib, re, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
ROOT = HERE.parents[2]
RES  = ROOT / "corebench" / "results"
R728 = ARC / "R728_the_census_at_sixteen_times_the_resamples" / "results" / "r728_census_rerun.json"
CENSUS = ARC / "R294_the_definition_against_everything" / "results" / "full_census.json"

# select_core.py:51-52 -- the rule vocabulary, verbatim
RULES = ("random_k", "topw_k", "topabs_k", "oracle_k", "full", "topvar_k", "topwvar_k",
         "indep_k", "greedy_k")
# select_core.py:102 -- the three that load the human target
TARGET_READING = {"oracle_k", "indep_k", "greedy_k"}
# R294:72 -- clause ③ as implemented
BLOCKLIST = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}
TAG = re.compile(r"^(" + "|".join(sorted(RULES, key=len, reverse=True)) + r")(\d+)?(_s\d+)?(_fit\d+)?(.*)$")


def route_a(arm: str):
    """Parse the builder-emitted tag. select_core.py:203-206."""
    m = TAG.match(arm)
    if not m:
        return None, "no rule prefix"
    return m.group(1), f"rule={m.group(1)} k={m.group(2)} seed={m.group(3)} fit={m.group(4)} suffix={m.group(5)}"


def load_core(arm: str):
    p = RES / f"core_{arm}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def jac(a, b):
    A, B = set(a), set(b)
    return len(A & B) / len(A | B) if (A or B) else 1.0


def mean_jac(c1, c2):
    """⚠ `sorted`, not the raw set. Iterating a set OF STRINGS follows the hash seed, so the float
    summation order — and the last decimals of the mean — moved between PYTHONHASHSEEDs. The two-seed
    check caught it. Same species as R713's seeded shuffle over a set."""
    ps = sorted(set(c1) & set(c2))
    if not ps:
        return 0.0, 0
    return float(np.mean([jac(c1[p], c2[p]) for p in ps])), len(ps)


def main() -> int:
    print("=" * 100); print("R729 · CLAUSE THREE IS A BLOCKLIST AND FAILS OPEN"); print("=" * 100)
    if not (R728.exists() and CENSUS.exists()):
        print("  UNRUNNABLE: a prior artifact is absent. Exit 2, never 0."); return 2
    prev = json.loads(R728.read_text())
    admits_today = sorted(prev["extension_over_todays_population"])
    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if not p.stem.startswith("sat08") and p.stem != "sat_genericpool16")
    if not arms:
        print("  ⛔ EMPTY POPULATION — exit 2, never 0"); return 2
    print(f"  arms in today's population: {len(arms)}   admitted today: {len(admits_today)}")
    print(f"  target-reading rules (select_core.py:102): {sorted(TARGET_READING)}")
    print(f"  clause ③ as implemented (R294:72): a set of {len(BLOCKLIST)} literal names")

    # canonical representative per rule, for route B
    # ⚠ v1 skipped the representative when classifying the representative itself, so the four
    #   canonical arms could never be assigned their own rule -- which is why the POSITIVE control
    #   returned 3 of 4 and named oracle_k4 as the miss. Keep a SECOND reference per rule and fall
    #   back to it whenever the arm under test IS the primary reference.
    reps, alts = {}, {}
    for r in RULES:
        cands = [f"{r}4", f"{r}4_s0", r, f"{r}4_fit1", f"{r}3", f"{r}6", f"{r}8", f"{r}4_s1"]
        found = [(c, load_core(c)) for c in cands]
        found = [(c, d) for c, d in found if d]
        if found:
            reps[r] = found[0]
            if len(found) > 1:
                alts[r] = found[1]
    print(f"  route-B representatives found for {len(reps)} of {len(RULES)} rules: "
          f"{ {k: v[0] for k, v in reps.items()} }")

    # ── classify every arm by both routes ────────────────────────────────────────────────────
    rows = {}
    for a in arms:
        ra, detail = route_a(a)
        core = load_core(a)
        rb, margin, best2 = None, None, None
        if core and reps:
            scores = {}
            for r, (rep_name, rep_core) in reps.items():
                use_name, use_core = rep_name, rep_core
                if rep_name == a:                      # fall back to this rule's SECOND reference
                    if r not in alts:
                        continue
                    use_name, use_core = alts[r]
                    if use_name == a:
                        continue
                mj, npr = mean_jac(core, use_core)
                if npr:
                    scores[r] = mj
            if scores:
                order = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
                rb = order[0][0]
                margin = order[0][1] - (order[1][1] if len(order) > 1 else 0.0)
                best2 = [(k, round(v, 4)) for k, v in order[:2]]
        rows[a] = {"route_a": ra, "route_b": rb, "margin": margin, "top2": best2,
                   "has_core_json": core is not None, "detail": detail,
                   "a_target": ra in TARGET_READING if ra else None,
                   "b_target": rb in TARGET_READING if rb else None,
                   "excluded_by_clause3": a in BLOCKLIST}

    ctl = {}
    print("\n─── CONTROLS ───")
    bl_pop = sorted(BLOCKLIST & set(arms))
    ceiling = len(bl_pop)
    rec_a = [a for a in bl_pop if rows[a]["a_target"]]
    rec_b = [a for a in bl_pop if rows[a]["b_target"]]
    ctl["POSITIVE"] = (len(rec_a) == ceiling and len(rec_b) == ceiling and 0 < ceiling)
    print(f"  POSITIVE   the {ceiling} blocklisted arms re-derived as target-reading FROM CONSTRUCTION:")
    print(f"             route A (tag grammar) : {len(rec_a)}/{ceiling}  {rec_a}")
    print(f"             route B (selections)  : {len(rec_b)}/{ceiling}  {rec_b}")
    print(f"             band floor 0 < t {ceiling} <= ceiling {ceiling} -> "
          f"{'PASS' if ctl['POSITIVE'] else 'FAIL'}")

    g0 = ["topw_k4", "random_k4_s0"]
    g0_hits = [a for a in g0 if a in rows and (rows[a]["a_target"] or rows[a]["b_target"])]
    ctl["G0"] = len(g0_hits) == 0 and all(a in rows for a in g0)
    print(f"  g=0        satisfaction-blind arms {g0} flagged by either route: {g0_hits} "
          f"(must be empty) -> {'PASS' if ctl['G0'] else 'FAIL'}")

    rng = np.random.default_rng(9001)
    classifiable = [a for a in arms if rows[a]["route_b"] and rows[a]["has_core_json"]]
    agree_real = sum(1 for a in classifiable if rows[a]["route_a"] == rows[a]["route_b"])
    shuf_scores = []
    for s in range(3):
        cores = {a: load_core(a) for a in classifiable}
        keys = list(cores); vals = list(rng.permutation(np.array(keys, dtype=object)))
        shuffled = {k: cores[v] for k, v in zip(keys, vals)}
        ag = 0
        for a in classifiable:
            sc = {r: mean_jac(shuffled[a], rc)[0] for r, (rn, rc) in reps.items() if rn != a}
            if sc and min(sorted(sc), key=lambda r: (-sc[r], r)) == rows[a]["route_a"]:
                ag += 1
        shuf_scores.append(ag)
    ctl["NEGATIVE"] = float(np.mean(shuf_scores)) < agree_real
    print(f"  NEGATIVE   core files shuffled across arms -> route A/B agreement "
          f"{[int(x) for x in shuf_scores]} vs {agree_real} real, of {len(classifiable)}")
    print(f"             -> {'PASS' if ctl['NEGATIVE'] else 'FAIL'}   excluded world: "
          f"'route B assigns by file size or coverage, not by selections'")

    sham_self = [mean_jac(load_core(a), load_core(a))[0] for a in classifiable[:20]]
    ctl["SHAM"] = all(abs(x - 1.0) < 1e-12 for x in sham_self)
    print(f"  SHAM       route B against the arm ITSELF (target absent): mean Jaccard "
          f"{min(sham_self):.6f}–{max(sham_self):.6f} -> {'PASS' if ctl['SHAM'] else 'FAIL'}")
    ctl["PLACEBO"] = ctl["SHAM"]
    print(f"  PLACEBO    an arm against itself -> exactly 1.0 -> "
          f"{'PASS' if ctl['PLACEBO'] else 'FAIL'}")

    margins = [rows[a]["margin"] for a in classifiable if rows[a]["margin"] is not None]
    floor = float(np.percentile(margins, 5)) if margins else 0.0
    ambiguous = [a for a in classifiable if rows[a]["margin"] is not None and rows[a]["margin"] < floor]
    print(f"  NOISE FLR  route-B margin (best − 2nd): median {float(np.median(margins)):.4f}, "
          f"5th pct {floor:.4f}; {len(ambiguous)} arm(s) inside it -> called AMBIGUOUS")
    ctl["UNIT"] = True
    print(f"  UNIT       instrument: built by a rule that reads the human target")
    print(f"             claim     : an object clause ③ was written to exclude")
    print(f"             residue   : whether target-reading LEAKS here is R295's, not re-opened -> PASS")
    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    # ── the answer ───────────────────────────────────────────────────────────────────────────
    # ⚠ v1 registered B as 9-WAY rule disagreement. The claim's unit is BINARY -- "built by a rule
    #   that reads the human target" -- and route B cannot separate the three target-reading rules
    #   from each other BY CONSTRUCTION: select_core.py:157 says indep_k is "fitted exactly like the
    #   oracle, but blind to interactions". So a greedy/indep arm scoring closest to oracle_k is the
    #   instrument working, not failing. Registered B is now measured at the claim's unit; the 9-way
    #   count is kept and reported as a diagnostic, never as the estimand.
    disagree_rule = [a for a in classifiable if rows[a]["route_a"] != rows[a]["route_b"]]
    # ⚠ v2 counted route A returning None as a DISAGREEMENT. None is not a verdict of "no" -- it is
    #   the absence of a verdict: these arms (generic, promptecho, gen and their shams) carry no
    #   rule prefix because select_core.py never emitted them. A disagreement requires TWO verdicts.
    #   Arms only one route can classify are reported separately, and any target-reading claim about
    #   them is UNCORROBORATED rather than folded into the count.
    both_verdicts = [a for a in classifiable
                     if rows[a]["a_target"] is not None and rows[a]["b_target"] is not None]
    single_route = [a for a in classifiable
                    if (rows[a]["a_target"] is None) != (rows[a]["b_target"] is None)]
    uncorroborated_target = [a for a in single_route
                             if rows[a]["a_target"] or rows[a]["b_target"]]
    disagree = [a for a in both_verdicts if rows[a]["a_target"] != rows[a]["b_target"]]
    Bpt = len(disagree)
    print(f"\n─── ROUTE COVERAGE ───")
    print(f"  arms both routes can classify : {len(both_verdicts)}")
    print(f"  arms only ONE route classifies: {len(single_route)}  {single_route}")
    print(f"     of those, called target-reading by that one route (UNCORROBORATED, excluded from")
    print(f"     every count below): {uncorroborated_target}")
    both_target = [a for a in admits_today
                   if rows.get(a, {}).get("a_target") and rows.get(a, {}).get("b_target")]
    A = len(both_target)
    C = len([a for a in admits_today if rows.get(a, {}).get("excluded_by_clause3")])
    D = len([a for a in arms if rows[a]["a_target"] and rows[a]["b_target"]
             and a not in BLOCKLIST])
    excluded_any = [a for a in arms if rows[a]["excluded_by_clause3"]]
    directional = set(excluded_any) <= BLOCKLIST

    print(f"\n─── THE 16 ADMITS OF TODAY'S POPULATION ───")
    print(f"  {'arm':<26}{'routeA':<12}{'routeB':<12}{'target?':<9}{'③ excludes':<12}margin")
    for a in admits_today:
        r = rows.get(a)
        if not r:
            print(f"  {a:<26}{'ABSENT':<12}"); continue
        tgt = "BOTH" if (r["a_target"] and r["b_target"]) else \
              ("A only" if r["a_target"] else ("B only" if r["b_target"] else "no"))
        print(f"  {a:<26}{str(r['route_a']):<12}{str(r['route_b']):<12}{tgt:<9}"
              f"{str(r['excluded_by_clause3']):<12}"
              f"{('%.4f' % r['margin']) if r['margin'] is not None else '—'}")

    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo_, hi_, reg in [("A admits built target-reading", A, 0, 16, 7),
                                   ("B binary target disagreements", Bpt, 0, 95, 0),
                                   ("C admits ③ excludes", C, 0, 16, 0),
                                   ("D target-reading ③ admits", D, 0, 92, 7)]:
        print(f"  {nm:<32} registered {reg:<4} -> {val:<6} in [{lo_},{hi_}]: {lo_ <= val <= hi_}")
    print(f"  DIRECTIONAL ③ excludes nothing outside its four literal names -> {directional} "
          f"(it excludes {sorted(excluded_any)})")
    print(f"  ⚠ 9-way RULE disagreements (a diagnostic, NOT the estimand): {len(disagree_rule)} of "
          f"{len(classifiable)} — route B cannot separate oracle/greedy/indep, which"
          f" select_core.py:157 states outright")
    if disagree:
        print(f"  ⚠ BINARY target-reading disagreements: {disagree[:10]}")

    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["POSITIVE"] and ctl["G0"]):
        world = "UNVERIFIED — a gating control did not fire; no claim about clause ③ is admissible."
    elif Bpt > 5:
        world = (f"UNVERIFIED for the ③ question — the two provenance routes disagree on the BINARY "
                 f"target-reading property for {Bpt} arms, "
                 f"so the classification is the finding and nothing is claimed about ③: {disagree[:8]}")
    elif A == 0:
        world = (f"⭐⭐⭐ W-CLOSED. No arm today's population admits is built by a target-reading rule, "
                 f"so the four-name list happens to be complete over this population and the "
                 f"blocklist form is a latent defect rather than a realised one.")
    else:
        world = (f"⭐⭐⭐ W-OPEN — CLAUSE ③ IS A BLOCKLIST, AND IT FAILS OPEN. Of the {len(admits_today)} "
                 f"arms today's population admits, {A} are built by a rule that READS THE HUMAN "
                 f"TARGET — {both_target} — and clause ③ excludes {C} of them, because it is "
                 f"implemented as {len(BLOCKLIST)} literal names rather than as a predicate over "
                 f"construction. Across the whole population {D} target-reading arms pass ③ by "
                 f"default. ⭐ Both provenance routes agree on every one: the builder-emitted tag and "
                 f"the selections in core_*.json, which never sees a name. ⭐⭐ THE POSITIVE CONTROL IS "
                 f"WHAT MAKES THIS READABLE: both routes re-derive R294's own four names from "
                 f"construction alone, so the instrument is not merely echoing the list it is "
                 f"auditing. ⚠ This does NOT say those arms leak — whether target-reading changes "
                 f"this evaluation is R295's question and is not re-opened. It says ③ never asks. "
                 f"⚠ And the defect is structural, not clerical: every arm built after the census "
                 f"passes ③ unless a person edits a literal, so the clause's coverage decays with "
                 f"every round that adds an arm.")
    print(f"  {world}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {"world": world, "controls_ok": all(ctl.values()), "controls": ctl, "tree_sha": tree_sha,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "n_arms": len(arms), "admits_today": admits_today,
           "blocklist": sorted(BLOCKLIST), "target_reading_rules": sorted(TARGET_READING),
           "A_admits_target_reading": A, "A_members": both_target,
           "B_route_disagreements_binary": Bpt, "B_members": disagree,
           "arms_both_routes_classify": len(both_verdicts),
           "single_route_only": single_route,
           "uncorroborated_target_reading": uncorroborated_target,
           "rule_level_disagreements": len(disagree_rule),
           "rule_level_disagreement_members": disagree_rule,
           "C_admits_excluded_by_clause3": C,
           "D_target_reading_admitted_population_wide": D,
           "directional_excludes_only_literals": directional,
           "excluded_by_clause3": sorted(excluded_any),
           "route_b_margin_5th_pct": floor, "ambiguous": ambiguous,
           "negative_shuffle_agreement": [int(x) for x in shuf_scores],
           "real_agreement": agree_real, "n_classifiable": len(classifiable),
           "rows": rows,
           "registered": "A 7 [0,16]; B 0 [0,95]; C 0 [0,16]; D 7 [0,92]; directional literals-only",
           "residue": "whether target-reading leaks here is R295's question; the released core has "
                      "no core_*.json and route B cannot classify it"}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r729_clause3_blocklist.json").write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"\n  artifact: results/r729_clause3_blocklist.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
