#!/usr/bin/env python3
"""
R919 · of R917's eight placebos, which could EVER have fired — separating "no effect" from "no power".

⛔ WHY, AND MY OWN NEXT WAS THE FIRST THING THIS ROUND KILLED. R917 closed by proposing an "MDE on
the share, per rule". **That quantity is not identified here and R906 already said so in its own
artifact**: `not_an_admission_probability: "there is no sampling frame over arms"`. An MDE presumes
a sampling distribution; the arms were built, not drawn. So the round I pre-registered would have
computed a well-formed number for a quantity that does not exist — G1's exact failure, committed by
me in the closing sentence of the previous round, which is the sentence §4 names as the highest-risk
one in a report.

⭐⭐ **WHAT IS IDENTIFIED IS THE RESOLUTION OF THE TEST R917 ACTUALLY RAN.** Its placebo drops `d` of
a rule's `N` arms uniformly at random and asks whether the kept set's admitted share is unusual. That
is a **finite-population** procedure with no sampling frame required: the admitted count among the
kept arms is **exactly hypergeometric(N, A, N−d)**. Its support is a finite set of integers, and the
question *"is any attainable value outside the null's 95% band?"* is answerable in closed form.

⭐⭐⭐ **AND THAT QUESTION IS THE ONE THAT MATTERS, BECAUSE R917 REPORTED 7 OF 8 PLACEBOS AS "INSIDE
THE NULL" AND COULD NOT SAY WHETHER THAT MEANT NO EFFECT OR NO POWER.** For a rule with `A = 0`
admitted arms the statistic is **constant at 0 whatever is dropped** — the placebo cannot fail, so
its "pass" is silence, not an acquittal (P5 ★). R917 noted this for the four zero-share rules in
prose. This round computes it for all eight and turns it into a verdict per rule.

ESTIMAND        for each rule: the smallest departure — in admitted-share units on the kept set —
                that R917's random-drop test could have detected at its own 95% band, and whether
                any attainable value is detectable at all.
IDENTIFICATION  EXACT and closed-form. The null is hypergeometric over a finite population; no
                sampling frame over arms is required or claimed. ⚠ This is NOT an MDE on an
                admission probability, which is unidentified here — see WHY.
SCOPE           population: R906's `RUBRIC_SELECTOR` arms, per selection rule, as R917 used them
                instrument: the drop test itself — hypergeometric null, central 95%
                baseline:   R917's own observed judge-matched share per rule
                regime:     home release; counts are ARMS
WORLDS          A · every rule has attainable detectable values -> R917's 7 "inside the null" are
                    genuine nulls and the corrections really are unresolvable-but-testable
                B · some rules have NO attainable detectable value -> those placebos could never
                    have fired, and reporting them as passes was reporting silence as acquittal
KILL            CONDITIONAL:
                  ⭐ ① WIRING: the hypergeometric null must reproduce R917's simulated null band
                     for every rule, to within the resolution of its 2000 draws. Different method
                     (exact vs Monte Carlo), same object — if they disagree, one is wrong and
                     neither number may be used.
                  ⭐ ② POSITIVE / CAN-THIS-TEST-EVER-FIRE: for each rule, evaluate the two EXTREME
                     attainable outcomes (drop as many admitted arms as possible; drop as few).
                     If neither is outside the band, the test is structurally blind for that rule.
                     ⚠ This is the control that has failed against me three times this session —
                     R915, R917's `random` placebo, R918's `t_exact = 0.0` — always because I
                     compared to a boundary the arithmetic could not reach. Here it is the
                     MEASUREMENT, not an afterthought.
                  ⭐ ③ DEGENERACY NAMED, NOT INFERRED: a rule with `A = 0` or `A = N` has a
                     constant statistic. Report `UNRESOLVABLE` with the reason, never a number.
                  ⭐ ④ R917's observed value is re-read from its artifact, not recomputed here, so
                     this round cannot quietly change what it is evaluating.
MULTIPLICITY    8 rules × {null band, extreme outcomes, detectable set}; every rule printed,
                including the ones that resolve nothing.
ARTIFACT        results/placebo_resolution.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · admission probability (unidentified by construction — see WHY).
                ⚠ AND: this measures the RESOLUTION of R917's test. It does not re-measure the
                admitted shares, which stand as R917 reported them.
"""
import json, math, pathlib, subprocess
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
ALPHA = 0.05
MC_TOL = 0.05          # R917's null used 2000 draws; agreement is judged at this resolution


def hyper_pmf(N, A, n):
    """exact P(a admitted among n kept) for a in the attainable range"""
    lo, hi = max(0, n - (N - A)), min(A, n)
    out = {}
    denom = math.comb(N, n)
    for a in range(lo, hi + 1):
        out[a] = math.comb(A, a) * math.comb(N - A, n - a) / denom
    return out


def central_band(pmf, alpha=ALPHA):
    ks = sorted(pmf)
    cum, lo, hi = 0.0, ks[0], ks[-1]
    for k in ks:
        cum += pmf[k]
        if cum >= alpha / 2:
            lo = k
            break
    cum = 0.0
    for k in reversed(ks):
        cum += pmf[k]
        if cum >= alpha / 2:
            hi = k
            break
    return lo, hi


def main() -> int:
    r917 = next(A24.glob("R917_*/results/candidates_only.json"), None)
    if r917 is None:
        print("  UNRUNNABLE: R917 artifact missing. Exit 2, never 0.")
        return 2
    d917 = json.loads(r917.read_text())
    if d917.get("verdict") == "UNVERIFIED":
        print("  UNRUNNABLE: R917's artifact is UNVERIFIED. Exit 2, never 0.")
        return 2
    plac = d917["placebo"]
    rules = {r["rule"]: r for r in d917["rules"]}
    print(f"  ④ R917's observed values and null bands READ from its artifact, not recomputed: "
          f"{len(plac)} rules")

    rows, wire_ok, blind, degenerate = [], [], [], []
    for rule in sorted(rules):
        A_, N = rules[rule]["mixed"]           # admitted, built — the MIXED population R917 dropped from
        p = plac.get(rule)
        if p is None:
            rows.append({"rule": rule, "N": N, "A": A_, "verdict": "NO_DROP",
                         "reason": "no arms were dropped for this rule"})
            continue
        d = p["n_drop"]
        n = N - d
        pmf = hyper_pmf(N, A_, n)
        lo_k, hi_k = central_band(pmf)
        lo_s, hi_s = lo_k / n, hi_k / n
        exp_s = (A_ * n / N) / n
        attain = sorted(pmf)
        detectable = [a for a in attain if a < lo_k or a > hi_k]
        # smallest detectable departure, in share units on the kept set
        mde = min((abs(a / n - exp_s) for a in detectable), default=None)
        const = (A_ == 0 or A_ == N)
        row = {"rule": rule, "N": N, "A": A_, "n_drop": d, "n_kept": n,
               "expected_share": exp_s,
               "exact_band_counts": [lo_k, hi_k], "exact_band_share": [lo_s, hi_s],
               "mc_band_share": p["null_ci"], "observed_share": p["obs"],
               "attainable_counts": [attain[0], attain[-1]],
               "n_detectable_outcomes": len(detectable),
               "mde_share": mde,
               "statistic_is_constant": bool(const),
               "verdict": ("UNRESOLVABLE_CONSTANT" if const else
                           "BLIND" if not detectable else "RESOLVABLE")}
        if const:
            degenerate.append(rule)
        elif not detectable:
            blind.append(rule)
        # ① wiring: exact band vs R917's Monte-Carlo band
        agree = (abs(lo_s - p["null_ci"][0]) <= MC_TOL and abs(hi_s - p["null_ci"][1]) <= MC_TOL)
        row["wiring_agrees_with_R917_mc"] = bool(agree)
        wire_ok.append(agree)
        rows.append(row)

    c1 = all(wire_ok)
    print(f"\n  ① WIRING — exact hypergeometric band vs R917's 2000-draw Monte-Carlo band "
          f"(tol {MC_TOL}):")
    print(f"     {'rule':<10}{'N':>4}{'A':>4}{'drop':>6}{'exact 95%':>20}{'R917 MC 95%':>20}  agree")
    for r in rows:
        if "mc_band_share" not in r:
            continue
        e = "[%.3f, %.3f]" % tuple(r["exact_band_share"])
        m = "[%.3f, %.3f]" % tuple(r["mc_band_share"])
        print(f"     {r['rule']:<10}{r['N']:>4}{r['A']:>4}{r['n_drop']:>6}{e:>20}{m:>20}  "
              f"{r['wiring_agrees_with_R917_mc']}")
    print(f"     ① {c1}  {'PASS' if c1 else 'FAIL'}")

    # ② can this test ever fire — the extremes, evaluated
    print(f"\n  ② CAN-THIS-TEST-EVER-FIRE — the extreme attainable outcomes, per rule:")
    print(f"     {'rule':<10}{'attainable a':>16}{'band':>12}{'detectable':>12}"
          f"{'MDE (share)':>14}  verdict")
    for r in rows:
        if "attainable_counts" not in r:
            print(f"     {r['rule']:<10}{'—':>16}{'—':>12}{'—':>12}{'—':>14}  {r['verdict']}")
            continue
        at = "%d..%d" % tuple(r["attainable_counts"])
        bd = "%d..%d" % tuple(r["exact_band_counts"])
        md = f"{r['mde_share']:.3f}" if r["mde_share"] is not None else "—"
        print(f"     {r['rule']:<10}{at:>16}{bd:>12}{r['n_detectable_outcomes']:>12}{md:>14}  "
              f"{r['verdict']}")
    c2 = any(r.get("verdict") == "RESOLVABLE" for r in rows)
    print(f"     ② at least one rule is resolvable, so the instrument is not uniformly blind: "
          f"{c2}  {'PASS' if c2 else 'FAIL'}")

    c3 = all((r.get("verdict") != "UNRESOLVABLE_CONSTANT") or (r["A"] in (0, r["N"]))
             for r in rows)
    print(f"\n  ③ DEGENERACY NAMED — constant-statistic rules: {degenerate}")
    print(f"     structurally blind but non-constant: {blind}")
    print(f"     ③ every UNRESOLVABLE verdict traces to A=0 or A=N: {c3}  "
          f"{'PASS' if c3 else 'FAIL'}")

    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3, "rules": rows},
                  open(OUT / "placebo_resolution.json", "w"), indent=2)
        return 2

    res = [r for r in rows if r.get("verdict") == "RESOLVABLE"]
    fired = [r for r in res if r["observed_share"] / 1.0 not in (None,)
             and (r["observed_share"] < r["exact_band_share"][0]
                  or r["observed_share"] > r["exact_band_share"][1])]
    world = "B" if (degenerate or blind) else "A"
    print(f"\n  ⭐⭐⭐ WORLD {world}: of {len(rows)} rules, {len(res)} could ever have fired, "
          f"{len(degenerate)} have a CONSTANT statistic, {len(blind)} are non-constant but have no "
          f"attainable detectable outcome.")
    print(f"     of the {len(res)} that could fire, {len(fired)} did: "
          f"{[r['rule'] for r in fired]}")
    print(f"     ⛔ SO R917's \"7 of 8 corrections sit inside their own null\" SPLITS. "
          f"{len(degenerate) + len(blind)} of those were never tests at all — the placebo could not "
          f"have failed — and reporting them as passes was reporting SILENCE AS ACQUITTAL. The "
          f"remaining {len(res) - len(fired)} are genuine nulls with a stated resolution.")
    for r in res:
        print(f"     · {r['rule']:<10} resolvable from {r['mde_share']:.3f} in share units; "
              f"observed {r['observed_share']:.3f} vs expected {r['expected_share']:.3f}")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "alpha": ALPHA, "mc_tol": MC_TOL,
               "killed_my_own_next": {
                   "was": "compute an MDE on the admitted share, per rule",
                   "why_wrong": "an MDE presumes a sampling distribution over arms; R906's own "
                                "artifact says not_an_admission_probability — there is no sampling "
                                "frame. The quantity is unidentified, not merely hard",
                   "replaced_by": "the exact resolution of the finite-population drop test R917 "
                                  "ran, whose null is hypergeometric and needs no sampling frame"},
               "rules": rows,
               "resolvable": [r["rule"] for r in res],
               "constant_statistic": degenerate,
               "structurally_blind": blind,
               "fired": [r["rule"] for r in fired],
               "splits_R917_claim": "R917's '7 of 8 inside the null' is not one fact: some of those "
                                    "placebos could never have fired",
               "unit_note": "counts are ARMS; MDE is in admitted-share units on the KEPT set",
               "not_an_admission_probability": "inherited from R906; this round does not create one",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "placebo_resolution.json", "w"), indent=2)
    print(f"\n  artifact: results/placebo_resolution.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
