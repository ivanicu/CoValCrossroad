#!/usr/bin/env python3
"""R1081 — an occasion for the helper, found by EXECUTION rather than by parsing.

R1076, R1078 and R1079 each tried to recover a semantic category ("is this a membership test?")
from syntax, and each failed a control it could not have passed. R1080 killed the reachability
explanation for why `assurance/valuematch.py` has zero static importers. What remains is whether any
round ever had an OCCASION to use it -- and that question is answerable without classifying a single
line of code, by running the comparison both ways and looking for a disagreement.

ESTIMAND        For a round r with prose decimal tokens T(r) drawn from its README and numeric
                artifact values V(r) drawn from its results/*.json:
                    E(r) = { t in T(r) : exists v in V(r) with float(t) == float(v) }
                    P(r) = { t in T(r) : exists v in V(r) with round(v,dp(t)) == round(t,dp(t)) }
                The quantity: the number of rounds with |P(r) \\ E(r)| > 0 -- rounds whose own prose
                carries a decimal that EXACT matching cannot find in their own artifact and
                PRECISION-AWARE matching can. Call these OCCASION ROUNDS.
                ⛔ E(r) subset-or-equal P(r) is a DERIVATION, forced by the algebra: if
                   float(t) == float(v) then rounding both to any dp preserves equality. "The
                   precision-aware test finds at least as many" is therefore NOT evidence. What is
                   not forced, and is the measurement: HOW MANY rounds have a strict superset, WHICH
                   rounds, and whether that rate exceeds the rate obtained by pairing a round's
                   prose with SOMEBODY ELSE'S artifact.
IDENTIFICATION  identified as stated. ⚠ NOT identified: whether the round's author was performing a
                comparison at that moment. The instrument's unit and the claim's unit are written
                out separately below and required to be EQUAL before any sentence is built on them.
UNIT OF THE     a (round, token) pair on which the two membership tests DISAGREE.
  INSTRUMENT
UNIT OF THE     the same. The sentence this round is allowed to write is "a round whose own prose
  CLAIM         contains a decimal that exact matching cannot locate in its own artifact and
                precision-aware matching can". It is a LATENT occasion: it says any check over that
                round using exact matching would have been wrong. It does NOT say the round ran one.
SCOPE           population: every round directory holding both a README.md and >=1 results/*.json
                (690 of 1079 round directories). instrument: this script, CPython. baseline: TWO
                measured floors -- the shuffled-pairing placebo and the within-round shifted
                artifact. regime: this checkout.
WORLDS          A COINCIDENCE   the disagreements are low-precision collisions -- `0.5` matches
                                something in any artifact -- and carry no information about the
                                round they came from.
                B LATENT DEFECT the disagreements are a round's own rounded numbers, so they are
                                specific to their artifact and vanish under re-pairing.
                Prediction matrix, on the occasion RATE and its shuffled-pairing floor:
                  A -> real rate ~= shuffled rate at every min_dp; the gap does not grow with dp.
                  B -> real rate >> shuffled rate, and the gap WIDENS with min_dp, because a
                       high-precision token is progressively harder to hit by accident.
KILL            pre-registered. Evaluated ONLY if the control gate opens.
                  World B is KILLED if the real occasion rate fails to exceed the shuffled floor by
                  more than the floor's own spread (max over seeds) at min_dp >= 2, in the majority
                  of specification cells. If B dies, the disagreements are collisions and this whole
                  line -- including R1047's original repair -- is measuring nothing.
POSITIVE CTRL   a synthesised round whose README prints 0.507 and whose artifact stores 0.50713.
                Required: exact finds 0, precision-aware finds 1, and the round is flagged. This is
                R1047's original defect, planted. Retention must be 1.0.
                MDE: the instrument is a set difference; its MDE is ONE (round, token) pair, and
                the resolution that matters is the placebo floor, measured below.
g=0 GUARD       a synthesised round printing 0.507 whose artifact stores exactly 0.507. Both tests
                must find it and the round must NOT be flagged. Without this the instrument would
                flag every round that mentions any number.
NEGATIVE CTRL   a synthesised round printing 0.999 whose artifact holds nothing near it. Neither
                test finds it; not flagged. Destroys the value-token relationship, preserves
                everything else. World excluded: "the flag fires on the presence of prose numbers".
SHAM            the same operation minus the ingredient, as a DOSE-RESPONSE. The ingredient is
                "use the token's OWN displayed precision"; the sham replaces it with a FIXED
                precision, swept over dp in {2,3,4,6,8,10,12,17,325}. Required, all computed:
                the identity dose (dp=325) reproduces the exact test exactly; the curve is monotone
                in coarsening; and the real result is BRACKETED by it.
                ⛔ THE FIRST VERSION OF THIS CONTROL COULD NOT HAVE PASSED. It asserted dp=17 is
                   the identity on a double. `round(x, n)` is n places AFTER THE DECIMAL POINT, not
                   n significant digits, so below 1 it still coarsens -- it rescued 7 pairs, and the
                   control demanded 0. §4's `control that cannot PASS`, built and caught here.
WITHIN-ROUND    ⚠ THE STRONGEST CONFOUND, and the shuffled placebo cannot see it: a round's own
  NEGATIVE      artifact holds many numbers of the same family, so WITHIN-round collisions may be
                commoner than cross-round ones. The artifact is SHIFTED by one unit of the cell's
                own resolution -- same count, same spacing, same magnitudes, correspondence
                destroyed. A cell counts as clearing only if it beats this floor too.
PLACEBO         pair each round's prose with ANOTHER round's artifact, 5 seeds. This is the
                false-occasion floor. A permutation over the round-artifact pairing answers exactly
                the question at issue -- does the token belong to THIS artifact -- and the world it
                excludes (coincidental low-precision collision) is world A, which is built
                synthetically as well, below.
SYNTHETIC WORLD world A built directly: a round whose prose tokens are drawn uniformly at random
                from a fixed decimal grid, unrelated to its artifact. The instrument must land on
                the placebo floor for it, not above.
NOISE FLOOR     measured as the spread of the placebo across 5 seeds, per specification cell.
MULTIPLICITY    the whole grid is reported: min_dp x list_len_max x integers = 5 x 4 x 2 = 40 cells,
                survivors and non-survivors. No p-value correction is applied and the reason is
                stated: each cell reports a rate against its own measured floor, not a test.
SPECIFICATION   min_dp          the token's displayed precision floor -- collision-prone at 0-1
                list_len_max    artifact values inside a list longer than this are excluded; a
                                round with a 100k-element array would otherwise match anything
                integers        whether bare integers count as tokens
SEEDS           5 for the placebo; the real measurement is deterministic and is reproduced twice
                byte-identically instead.
ARTIFACT        results/occasion_by_execution.json with the source hash.
IMPOSSIBLE      author intent at the time of writing -- N/A, would require the session transcript,
                which is not in the release. Cross-repository -- N/A, would require a second site.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import random
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
OUT = HERE / "results" / "occasion_by_execution.json"

sys.path.insert(0, str(ROOT / "assurance"))
import valuematch as VM                                   # ⭐ the helper, imported not re-written

DEC = re.compile(r"(?<![\w.])[-+]?\d+\.\d+(?![\w.])")
INT = re.compile(r"(?<![\w.])[-+]?\d{1,9}(?![\w.\d])")
CAPS = [0, 10, 100, None]          # list_len_max: 0 == scalar leaves only, None == no limit
MIN_DPS = [0, 1, 2, 3, 4]
SEEDS = [0, 1, 2, 3, 4]


# ---------------------------------------------------------------------------- extraction

def tokens(text: str, with_ints: bool) -> list[str]:
    out = DEC.findall(text)
    if with_ints:
        out += INT.findall(text)
    return out


def leaves(obj, depth_list_len: int | None, cap: int | None, acc: list[float]) -> None:
    """numeric leaves, tagged by the length of the innermost list containing them."""
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        if cap is None or (depth_list_len or 0) <= cap:
            acc.append(float(obj))
        return
    if isinstance(obj, dict):
        for v in obj.values():
            leaves(v, depth_list_len, cap, acc)
    elif isinstance(obj, list):
        n = len(obj)
        for v in obj:
            leaves(v, n, cap, acc)


def round_values(rd: pathlib.Path, cap: int | None) -> list[float]:
    acc: list[float] = []
    for j in sorted((rd / "results").glob("*.json")):
        try:
            leaves(json.loads(j.read_text(errors="replace")), 0, cap, acc)
        except (json.JSONDecodeError, RecursionError, OSError):
            continue
    return acc


# ---------------------------------------------------------------------------- the two tests

def by_dp(vals: list[float], dps: set[int]) -> dict[int, set[float]]:
    return {d: {round(v, d) for v in vals} for d in dps}


def verdicts(toks: list[str], exact_pool: set[float], dp_pool: dict[int, set[float]],
             force_dp: int | None = None) -> tuple[int, int, list[str]]:
    """(found_exact, found_precision_aware, tokens found ONLY by precision-aware)

    `force_dp` replaces the token's DISPLAYED precision with a fixed one. It exists for the SHAM:
    at force_dp = 17 the rounding is the identity on a double, so the same code path runs with the
    ingredient -- displayed precision -- removed.
    """
    ex = pa = 0
    only = []
    for t in toks:
        try:
            f = float(t)
        except ValueError:
            continue
        e = f in exact_pool
        d = VM.displayed_precision(t) if force_dp is None else force_dp
        p = round(f, d) in dp_pool.get(d, ())
        ex += e
        pa += p
        if p and not e:
            only.append(t)
    return ex, pa, only


# ---------------------------------------------------------------------------- controls

def synth_controls() -> dict:
    """POSITIVE / g=0 / NEGATIVE, each a synthesised round, run through the SAME functions."""
    cases = {
        "POSITIVE  prose 0.507, artifact 0.50713 -> flagged": (["0.507"], [0.50713], True),
        "g=0       prose 0.507, artifact 0.507   -> NOT flagged": (["0.507"], [0.507], False),
        "NEGATIVE  prose 0.999, artifact 0.12    -> NOT flagged": (["0.999"], [0.12], False),
        "POSITIVE  prose 12.46, artifact 12.4638 -> flagged": (["12.46"], [12.4638], True),
        "g=0       an integer 5 present exactly  -> NOT flagged": (["5"], [5.0], False),
    }
    out = {}
    for name, (toks, vals, want) in cases.items():
        dps = {VM.displayed_precision(t) for t in toks}
        _e, _p, only = verdicts(toks, set(vals), by_dp(vals, dps))
        out[name] = (len(only) > 0) == want
    # the POSITIVE plant must also DISAPPEAR under the sham -- otherwise the flag is not the
    # rounding, and the whole instrument is measuring its own code path.
    _e, _p, sham_only = verdicts(["0.507"], {0.50713}, {17: {round(0.50713, 17)}}, force_dp=17)
    out["POSITIVE  the plant vanishes when the rounding is removed (SHAM)"] = not sham_only
    return out


# ---------------------------------------------------------------------------- main

def main() -> int:
    rounds = []
    for d in sorted(ROOT.glob("E*/A*/R*")):
        if d.is_dir() and (d / "README.md").is_file() and any((d / "results").glob("*.json")):
            rounds.append(d)
    if not rounds:
        print("  UNRUNNABLE: empty population. Exit 2, never 0.")
        return 2

    # ---- read once; the caps are applied at extraction so a huge array never enters the pool ----
    text = {d: (d / "README.md").read_text(errors="replace") for d in rounds}
    vals_by_cap = {c: {d: round_values(d, c) for d in rounds} for c in CAPS}
    exact_by_cap = {c: {d: set(vals_by_cap[c][d]) for d in rounds} for c in CAPS}
    # ⚠ the pools are built ONCE per (cap, round, dp) and reused across every cell and every
    #   placebo shuffle. Rebuilding them inside the shuffle loop would be 138,000 rebuilds of the
    #   same sets -- correct, and slow enough that the grid would have been cut instead.
    DPC: dict = {}

    def pool(cap, d, dps):
        for dp in dps:
            k = (cap, d, dp)
            if k not in DPC:
                DPC[k] = {round(v, dp) for v in vals_by_cap[cap][d]}
        return {dp: DPC[(cap, d, dp)] for dp in dps}

    cells = []
    detail_default = None
    for cap in CAPS:
        for with_ints in (False, True):
            tok_all = {d: tokens(text[d], with_ints) for d in rounds}
            for min_dp in MIN_DPS:
                toks = {d: [t for t in tok_all[d] if VM.displayed_precision(t) >= min_dp]
                        for d in rounds}
                dps_used = {d: {VM.displayed_precision(t) for t in toks[d]} for d in rounds}

                flagged, tok_disagree, per_round = [], 0, {}
                for d in rounds:
                    if not toks[d]:
                        continue
                    _e, _p, only = verdicts(toks[d], exact_by_cap[cap][d],
                                            pool(cap, d, dps_used[d]))
                    if only:
                        flagged.append(str(d.relative_to(ROOT)))
                        tok_disagree += len(only)
                        per_round[str(d.relative_to(ROOT))] = sorted(set(only))[:12]
                eligible = [d for d in rounds if toks[d]]
                rate = len(flagged) / len(eligible) if eligible else 0.0

                # ---- PLACEBO: the same statistic against SOMEBODY ELSE'S artifact ----
                floor = []
                for s in SEEDS:
                    rng = random.Random(s)
                    partners = list(rounds)
                    rng.shuffle(partners)
                    fl = 0
                    for d, o in zip(rounds, partners):
                        if not toks[d] or o is d:
                            continue
                        _e, _p, only = verdicts(toks[d], exact_by_cap[cap][o],
                                                pool(cap, o, dps_used[d]))
                        fl += bool(only)
                    floor.append(fl / len(eligible) if eligible else 0.0)

                # ---- WITHIN-ROUND NEGATIVE: the strongest confound, controlled in this cell ----
                # ⚠ The shuffled placebo measures BETWEEN-round collisions. A round's OWN artifact
                #   holds many numbers of the same magnitude and family, so within-round collisions
                #   could be commoner than cross-round ones and the placebo would never see it.
                #   Here the artifact is SHIFTED by one unit of the cell's own resolution: same
                #   count, same spacing, same magnitudes, correspondence destroyed. Anything still
                #   flagged is a distributional collision inside the round itself.
                delta = 10.0 ** (-max(min_dp, 1))
                shift_flag = 0
                for d in rounds:
                    if not toks[d]:
                        continue
                    sv = [v + delta for v in vals_by_cap[cap][d]]
                    _e, _p, only = verdicts(toks[d], set(sv),
                                            {dp: {round(v, dp) for v in sv}
                                             for dp in dps_used[d]})
                    shift_flag += bool(only)
                shift_rate = shift_flag / len(eligible) if eligible else 0.0

                # ---- SYNTHETIC WORLD A: prose drawn from a grid, unrelated to the artifact ----
                rng = random.Random(99)
                synth_flag = 0
                for d in rounds:
                    if not toks[d]:
                        continue
                    m = max(min_dp, 1)
                    fake = [f"{rng.randrange(0, 10**m) / 10**m:.{m}f}" for _ in range(len(toks[d]))]
                    _e, _p, only = verdicts(fake, exact_by_cap[cap][d],
                                            pool(cap, d, {VM.displayed_precision(t) for t in fake}))
                    synth_flag += bool(only)
                synth_rate = synth_flag / len(eligible) if eligible else 0.0

                cell = {"cap": cap, "with_ints": with_ints, "min_dp": min_dp,
                        "eligible_rounds": len(eligible), "occasion_rounds": len(flagged),
                        "occasion_rate": round(rate, 4), "tokens_disagreeing": tok_disagree,
                        "placebo_mean": round(sum(floor) / len(floor), 4),
                        "placebo_max": round(max(floor), 4),
                        "placebo_spread": round(max(floor) - min(floor), 4),
                        "synthetic_worldA_rate": round(synth_rate, 4),
                        "within_round_shifted_rate": round(shift_rate, 4),
                        "exceeds_floor": (rate > max(floor) + (max(floor) - min(floor))
                                          and rate > shift_rate)}
                cells.append(cell)
                if cap == 100 and not with_ints and min_dp == 2:
                    detail_default = {"cell": cell, "rounds": per_round}

    # ---- SHAM, as a DOSE-RESPONSE rather than a binary ---------------------------------------
    # ⛔ THE FIRST VERSION OF THIS CONTROL FAILED FOR ITS OWN REASON, and the diagnosis is the
    #    finding that fixed it. I asserted that `force_dp = 17` removes the ingredient because a
    #    double carries ~17 significant digits. `round(x, n)` rounds to n places AFTER THE DECIMAL
    #    POINT, not to n significant digits -- so for |x| < 1 the leading zeros are free and dp=17
    #    still COARSENS. It rescued 7 (round, token) pairs, e.g. `0.002` in R789, and a control
    #    demanding exactly zero could not have passed. That is §4's `control that cannot PASS`:
    #    the threshold was above what the design can return.
    # ⭐ The repair is not a looser threshold. A fixed dp is a DOSE of coarsening, so sweep it and
    #    require the curve to run from the exact test to the real test. floor and ceiling are then
    #    both computed rather than assumed.
    sham_curve = {}
    for fdp in [2, 3, 4, 6, 8, 10, 12, 17, 325]:
        flagged_n = 0
        for d in rounds:
            tk = tokens(text[d], False)
            if not tk:
                continue
            pf = {fdp: {round(v, fdp) for v in vals_by_cap[100][d]}}
            _e, _p, only = verdicts(tk, exact_by_cap[100][d], pf, force_dp=fdp)
            flagged_n += bool(only)
        sham_curve[fdp] = flagged_n
    # real, at DISPLAYED precision, same population and cap -- the ceiling the dose must approach
    real_all_dp = 0
    for d in rounds:
        tk = tokens(text[d], False)
        if not tk:
            continue
        _e, _p, only = verdicts(tk, exact_by_cap[100][d],
                                pool(100, d, {VM.displayed_precision(t) for t in tk}))
        real_all_dp += bool(only)
    sham_identity_ok = sham_curve[325] == 0                    # no coarsening -> exact test
    sham_monotone = all(sham_curve[a] >= sham_curve[b]
                        for a, b in zip([2, 3, 4, 6, 8, 10, 12, 17],
                                        [3, 4, 6, 8, 10, 12, 17, 325]))
    sham_brackets = sham_curve[325] < real_all_dp <= sham_curve[2]
    sham_ok = sham_identity_ok and sham_monotone and sham_brackets
    sham_flagged = sham_curve[17]

    cc = synth_controls()
    # reproducibility: the real (non-placebo) half recomputed
    rerun = []
    for d in rounds:
        tk = [t for t in tokens(text[d], False) if VM.displayed_precision(t) >= 2]
        if not tk:
            continue
        _e, _p, only = verdicts(tk, exact_by_cap[100][d],
                                pool(100, d, {VM.displayed_precision(t) for t in tk}))
        if only:
            rerun.append(str(d.relative_to(ROOT)))
    repro = sorted(rerun) == sorted(detail_default["rounds"]) if detail_default else False

    gate_open = all(cc.values()) and sham_ok and repro
    dp2 = [c for c in cells if c["min_dp"] >= 2]
    surviving = [c for c in dp2 if c["exceeds_floor"]]
    b_killed = gate_open and (len(surviving) <= len(dp2) / 2)

    # does the gap WIDEN with dp, as world B predicts and world A does not?
    prof = {}
    for m in MIN_DPS:
        cs = [c for c in cells if c["min_dp"] == m]
        prof[m] = {"rate": round(sum(c["occasion_rate"] for c in cs) / len(cs), 4),
                   "floor": round(sum(c["placebo_mean"] for c in cs) / len(cs), 4)}
    gaps = [prof[m]["rate"] - prof[m]["floor"] for m in MIN_DPS]
    widens = gaps[-1] > gaps[0]

    if not gate_open:
        verdict = ("UNVERIFIED — a control failed. A kill that can fire on a broken instrument is "
                   "not a commitment.")
    elif b_killed:
        verdict = (f"world B (LATENT DEFECT) is KILLED — only {len(surviving)} of {len(dp2)} cells "
                   f"at min_dp>=2 clear their own placebo floor. The disagreements are collisions.")
    else:
        verdict = (f"world A (COINCIDENCE) is KILLED — {len(surviving)} of {len(dp2)} cells at "
                   f"min_dp>=2 exceed their own shuffled-pairing floor, and the gap "
                   f"{'WIDENS' if widens else 'does NOT widen'} with displayed precision "
                   f"({gaps[0]:+.4f} at dp>=0 -> {gaps[-1]:+.4f} at dp>=4).")

    art = {
        "round": "R1081",
        "question": "did any round have an occasion for the helper, found by execution not parsing",
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "helper_imported_from": VM.__file__,
        "population": {"rounds_with_readme_and_results": len(rounds),
                       "round_dirs_total": len(list(ROOT.glob("E*/A*/R*")))},
        "unit_of_instrument": "a (round, token) pair on which the two membership tests disagree",
        "unit_of_claim": "a (round, token) pair on which the two membership tests disagree",
        "units_equal": True,
        "derivation_not_measurement": (
            "E(r) is a subset of P(r) by algebra: float equality implies equality after rounding to "
            "any dp. 'precision-aware finds at least as many' could not have come out otherwise and "
            "is NOT evidence. The measurement is the rate of STRICT superset against its own "
            "shuffled-pairing floor."),
        "controls": {**cc,
                     "SHAM identity dose (dp=325) reproduces the exact test": sham_identity_ok,
                     "SHAM dose-response is monotone in coarsening": sham_monotone,
                     "SHAM the real (displayed-precision) result is bracketed by the dose curve":
                         sham_brackets,
                     "REPRODUCIBILITY real half recomputed identically": repro},
        "sham_dose_response": {"fixed_dp_to_rounds_flagged": sham_curve,
                               "real_at_displayed_precision": real_all_dp,
                               "note": ("a fixed dp is a DOSE of coarsening. dp=325 is the identity "
                                        "on a double and must reproduce the exact test; dp=2 is "
                                        "coarser than most tokens and must meet or exceed the real "
                                        "result. `round(x, n)` is n places AFTER THE DECIMAL POINT, "
                                        "not n significant digits, which is why dp=17 still "
                                        "rescues values below 1.")},
        "grid": {"cells_tested": len(cells), "cells_at_min_dp_ge_2": len(dp2),
                 "cells_exceeding_their_own_floor": len(surviving),
                 "cells_killed_over_whole_grid": [
                     {k: c[k] for k in ("cap", "with_ints", "min_dp", "occasion_rate",
                                        "placebo_mean", "within_round_shifted_rate")}
                     for c in cells if not c["exceeds_floor"]],
                 "cells_surviving_over_whole_grid": sum(1 for c in cells if c["exceeds_floor"])},
        "cells": cells,
        "precision_profile": prof,
        "gap_widens_with_precision": widens,
        "kill": {"gate_open": gate_open, "world_B_killed": b_killed},
        "headline_cell": detail_default["cell"] if detail_default else None,
        "occasion_rounds_headline": detail_default["rounds"] if detail_default else {},
        "verdict": verdict,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1081 — an occasion found by running the comparison, not by classifying the code\n")
    print(f"  population {len(rounds)} rounds with both a README and a results artifact "
          f"(of {len(list(ROOT.glob('E*/A*/R*')))} round dirs)")
    print(f"  helper imported from {VM.__file__}")
    print("\n  CONTROLS")
    for k, v in art["controls"].items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  ⛔ DERIVATION, not a finding: E(r) ⊆ P(r) is forced by the algebra. Only the")
    print(f"     STRICT-superset rate against its own floor could have come out otherwise.")
    print(f"\n  PRECISION PROFILE — world B predicts the gap WIDENS with displayed precision")
    print(f"    {'min_dp':<8}{'occasion rate':>15}{'placebo floor':>15}{'gap':>10}")
    for m in MIN_DPS:
        print(f"    >={m:<6}{prof[m]['rate']:>15.4f}{prof[m]['floor']:>15.4f}"
              f"{prof[m]['rate']-prof[m]['floor']:>+10.4f}")
    print(f"\n  SHAM AS DOSE-RESPONSE — a FIXED precision is a dose of coarsening; the ingredient")
    print(f"     under study is the token's OWN displayed precision, which the fixed dose removes")
    print(f"    {'fixed dp':<10}" + "".join(f"{k:>7}" for k in sorted(sham_curve)) + "   real")
    print(f"    {'rounds':<10}" + "".join(f"{sham_curve[k]:>7}" for k in sorted(sham_curve))
          + f"   {real_all_dp}")
    killed_cells = [c for c in cells if not c["exceeds_floor"]]
    print(f"\n  GRID — {len(cells)} cells (cap × integers × min_dp); "
          f"{len(cells)-len(killed_cells)} survive, {len(killed_cells)} killed; "
          f"{len(surviving)} of {len(dp2)} at min_dp>=2 clear BOTH floors")
    if killed_cells:
        print(f"    ⛔ the specifications that KILL it, reported rather than dropped: "
              f"{sorted({(c['min_dp'], c['with_ints']) for c in killed_cells})} — at min_dp=0 with "
              f"integers the SHIFTED artifact scores "
              f"{max(c['within_round_shifted_rate'] for c in killed_cells):.3f} against a real "
              f"{max(c['occasion_rate'] for c in killed_cells):.3f}: an integer matches anything.")
    print(f"    {'cap':>6}{'ints':>6}{'min_dp':>7}{'rounds':>8}{'occ':>6}{'rate':>8}"
          f"{'floor':>8}{'spread':>8}{'shift':>8}{'synthA':>8}  clears")
    for c in cells:
        print(f"    {str(c['cap']):>6}{str(c['with_ints'])[0]:>6}{c['min_dp']:>7}"
              f"{c['eligible_rounds']:>8}{c['occasion_rounds']:>6}{c['occasion_rate']:>8.3f}"
              f"{c['placebo_mean']:>8.3f}{c['placebo_spread']:>8.3f}"
              f"{c['within_round_shifted_rate']:>8.3f}"
              f"{c['synthetic_worldA_rate']:>8.3f}  {'YES' if c['exceeds_floor'] else 'no'}")
    if detail_default:
        h = detail_default["cell"]
        print(f"\n  HEADLINE CELL cap=100 ints=False min_dp>=2 : "
              f"{h['occasion_rounds']} of {h['eligible_rounds']} rounds "
              f"({h['occasion_rate']:.3f}) vs floor {h['placebo_mean']:.3f}±{h['placebo_spread']:.3f}")
        for r, ts in sorted(detail_default["rounds"].items())[:8]:
            print(f"    {r.split('/')[-1][:58]:<60} {ts[:5]}")
        if len(detail_default["rounds"]) > 8:
            print(f"    … and {len(detail_default['rounds'])-8} more, all in the artifact")
    print(f"\n  KILL gate_open={gate_open}  world_B_killed={b_killed}")
    print(f"\n  {'⛔' if b_killed or not gate_open else '⭐'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
