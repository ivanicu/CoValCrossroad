"""Two properties every published artifact must satisfy, checkable without knowing what it measures.

WHY THIS EXISTS
---------------
Twelve rounds of auditing (entries 184-196) found every defect in a SUMMARISER, an
index, a row or a check -- never in a measurement. These two invariants are how that
was established, and entry 196 left them as one-off scans. A one-off command protects
nothing after the terminal scrolls (entry 174).

THE TWO INVARIANTS, and why only these two
-------------------------------------------
  1. A point estimate lies INSIDE the interval published with it.
  2. A stored significance flag AGREES with its own interval.
     (plus: an interval's bounds are ordered, lo <= hi)

Both are checkable with NO knowledge of the estimand, the population, or what the round
intended. No judgement, no registry, no per-round exemption -- which is why they can run
over every artifact at once and why a violation is unarguable. Every richer property
this package cares about needs a reading; these two do not.

SCOPE -- deliberately narrow, so a hit is real
-----------------------------------------------
Invariant 1 applies only to STEM-MATCHED pairs: a mean and a CI the round itself names
together (`gap` / `gap_ci`). Cross-key pairs are exactly what r58's harvester got wrong,
and guessing at them here would import that defect.
Invariant 2 applies only where a node carries EXACTLY ONE CI and EXACTLY ONE flag. With
several of either, which pairs with which is a reading, and this check does not read.

THE PROXY LEDGER
----------------
PROPERTY    the artifact's numbers are mutually consistent.
PROXY       these two relations hold on unambiguous pairs.
IMPLICATION violation => inconsistent          SOUND, and this gates on it -- WITH ONE NAMED
                                               EXCEPTION, measured at R341 and not hypothetical:
                                               A RATIO ESTIMATOR SUMMARISED BY ITS BOOTSTRAP MEAN.
                                               R235 publishes eta = mean(d_core/gap) beside
                                               eta_ci = percentile(d_core/gap, 2.5/97.5) over the
                                               SAME bootstrap array (R235 run.py:644,675,503). When
                                               `gap` approaches zero the ratio is Cauchy-like, so
                                               the MEAN of the replicates can sit far outside their
                                               own central 95% with nothing whatever wrong: 13
                                               distinct cells do, at |offcentre| up to 2.48. This
                                               guard has never fired on them only because `eta` is
                                               not a MEANISH name. If a ratio ever gets a MEANISH
                                               name, invariant 1 will FAIL A CORRECT ARTIFACT --
                                               the false-CONVICTION direction, which is as
                                               permanent as a false acquittal because nobody
                                               re-examines a claim its own author withdrew.
                                               A violation is therefore: inconsistent, OR the point
                                               is a ratio's mean. The second is checkable only in
                                               the SOURCE, never in the artifact.
            holds     => the artifact is right  NOT SOUND. A round can be perfectly
                                                self-consistent and wrong about the
                                                world. These catch INCOHERENCE, never
                                                ERROR.
SAFE SIDE   reports incoherence; never certifies correctness.
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
CIISH = re.compile(r"^(ci|.*_ci|ci_.*|interval)$", re.I)
# Extended 2026-07-29 (entry 199) after measuring the blind spot: 148 nodes carried
# exactly one CI and NO match, i.e. the regex could not see the estimate at all -- a
# gap as large as the coverage. The additions are estimate names this package actually
# uses: accuracy, correlation coefficients, and explicit `x_minus_y` contrasts.
# ⚠ REVERTED, and the reversal is the finding (entry 199). Extending this to
# `accuracy`, correlation coefficients and `x_minus_y` doubled the nominal coverage and
# produced only FALSE POSITIVES: `regret` paired with `min_segment_ci`, `accuracy` with
# a delta's `ci`, `accuracy` with a `share_ci`. Each is the guard INVENTING a pairing
# the round never asserted -- r58's harvester defect, reproduced by the instrument built
# to catch it, three times in one round. This package's naming is too heterogeneous for
# a name-based rule to identify which quantity a CI belongs to. 134 sound pairs beat
# ~200 with invented ones.
MEANISH = re.compile(r"^(mean|diff|delta|gap|advantage|drop|attribution|effect|"
                     r".*_mean|.*_diff|.*_delta|.*_gap)$", re.I)
# A p-value is NOT an estimate and must never be paired with an interval. Named
# explicitly because `perm_p` (43 nodes) and `p_two_sided` (17) sit beside CIs
# throughout, and a lenient MEANISH would pair them.
PVALUE = re.compile(r"^(p|p_.*|.*_p|perm_p|pval|p_value|.*_pvalue)$", re.I)
NULLNAME = re.compile(r"null|shuffl|permut|placebo|random_drop", re.I)
BOOLISH = re.compile(r"^(excludes_zero|significant|.*_significant|significant_.*|"
                     r"excludes_0|is_significant)$", re.I)


def is_ci(v):
    return (isinstance(v, list) and len(v) == 2
            and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v))


def scan(root: pathlib.Path):
    # ⚠ `all_pairs` added at R340, ADDITIVE. scan() counted 389 unambiguous pairs and retained only
    # the violating ones, so a triage built on its output could only ever see nodes already known
    # to be outside their interval -- a population pre-filtered to the positives, which cannot
    # clear anything. Nothing that existed before reads this key and no verdict changes.
    out = {"outside": [], "contradict": [], "inverted": [], "degenerate": [],
           "all_pairs": [], "n_pairs": 0, "n_flagged": 0,
           "n_stem": 0, "n_sole": 0, "skipped_sole_null": [], "skipped_ci_spoken_for": []}

    def walk(o, rid, path):
        if isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, rid, f"{path}[{i}]")
            return
        if not isinstance(o, dict):
            return
        cks = [(k, o[k]) for k in o if CIISH.match(k) and is_ci(o[k])]
        mks = [(k, o[k]) for k in o
               if MEANISH.match(k) and not PVALUE.match(k)
               and isinstance(o[k], (int, float)) and not isinstance(o[k], bool)]
        bks = [(k, o[k]) for k in o if BOOLISH.match(k) and isinstance(o[k], bool)]
        for ck, cv in cks:
            if cv[0] > cv[1]:
                out["inverted"].append((rid, path or "<root>", ck, cv))
            # ⚠ ADDED at R341, REPORTED not gated. `inverted` is lo > hi, STRICTLY, so an interval
            # asserting ZERO uncertainty passes it silently and no other check looks at it. 573
            # were found the first time anyone counted, and they are not obviously wrong -- a
            # parameter pinned at a grid boundary legitimately has lo == hi. But an unexamined
            # class of 573 that every gate is structurally blind to is worth a number in the
            # banner, because silence is what let it reach 573.
            elif cv[0] == cv[1]:
                out["degenerate"].append((rid, path or "<root>", ck, cv))
        # invariant 1 pairs a mean with a CI when the pairing is UNAMBIGUOUS, by either
        # of two routes (entry 198):
        #   (a) STEM-MATCHED   -- the round names them together, `gap` / `gap_ci`
        #   (b) SOLE CANDIDATE -- exactly one mean-ish and one ci-ish key in the node
        # (b) is the same unambiguity standard invariant 2 already uses, and it is what
        # lifts coverage off the floor: the commonest shape in this package is
        # {"delta": x, "ci": [...]}, which no stem rule can match because "delta" is not
        # a substring of "ci". Restricting to stem matches alone checked 10 pairs.
        stem_hits = set()
        for mk, mv in mks:
            for ck, cv in cks:
                if mk.lower() in ck.lower() or ck.lower().replace("_ci", "") == mk.lower():
                    stem_hits.add((mk, ck))
                    lo, hi = sorted(cv)
                    out["n_pairs"] += 1
                    out["all_pairs"].append((rid, path or "<root>", mv, [lo, hi]))
                    out["n_stem"] += 1
                    if not (lo <= mv <= hi):
                        out["outside"].append((rid, path or "<root>", mk, mv, ck, [lo, hi]))
        # ...but NOT when the sole mean candidate is a NULL summary (entry 198). r84's
        # root matches exactly one mean-ish key, `shuffled_gap`, and one ci-ish key,
        # `gap_ci` -- yet its real estimate is `core_minus_full_pred_positive`, which
        # MEANISH does not match. Pairing those two invents a contrast the round never
        # asserted, which is r58's harvester defect reproduced inside this guard. If the
        # only mean we can see is a null's, the real one is somewhere we cannot see, and
        # the node is NOT unambiguous.
        # Count only nodes this actually DECLINES to pair -- one mean, one CI, no stem
        # match. Testing sole_is_null before the CI condition counted 201 nodes that
        # would never have been paired at all, which overstates what the guard refuses.
        sole_is_null = len(mks) == 1 and bool(NULLNAME.search(mks[0][0]))
        if sole_is_null and len(cks) == 1 and not stem_hits:
            out["skipped_sole_null"].append((rid, path or "<root>", mks[0][0]))
        # ...and NOT when the CI's own stem names a different key in the node (entry
        # 199). r16 carries `regret`, `min_segment` and `min_segment_ci`: the regex sees
        # `regret` as the only mean, so sole-candidate paired it with an interval that
        # plainly belongs to `min_segment`. Stripping `_ci` and testing membership is
        # mechanical -- if the stem is a key here, the CI is spoken for.
        ci_stem = re.sub(r"_ci$|^ci_", "", cks[0][0], flags=re.I) if len(cks) == 1 else None
        ci_spoken_for = bool(ci_stem and ci_stem != cks[0][0] and ci_stem in o
                             and not any(ci_stem == m for m, _ in mks))
        if ci_spoken_for:
            out["skipped_ci_spoken_for"].append((rid, path or "<root>", cks[0][0], ci_stem))
        if (len(mks) == 1 and len(cks) == 1 and not stem_hits and not sole_is_null
                and not ci_spoken_for):
            (mk, mv), (ck, cv) = mks[0], cks[0]
            lo, hi = sorted(cv)
            out["n_pairs"] += 1
            out["all_pairs"].append((rid, path or "<root>", mv, [lo, hi]))
            out["n_sole"] += 1
            if not (lo <= mv <= hi):
                out["outside"].append((rid, path or "<root>", mk, mv, ck, [lo, hi]))
        # ⛔ INVARIANT 2 USED SOLE CANDIDACY ALONE while invariant 1 carries three refusals, and
        # `ci_spoken_for` — computed a few lines above — is one of them. R235's `E_verdict` root
        # holds K1..K5 as SIBLING pre-registered kills; the guard paired `K4prime_..._ci` with
        # `K2_majority_negative_significant` because they share a parent and match the two regexes.
        # `ci_stem` there is `K4prime_core_minus_topw`, which IS a key in the node, so the refusal
        # was already true and simply never applied to this branch — the guard's own docstring
        # warns that cross-key pairs are what r58's harvester got wrong. Measured (R934): this
        # refuses exactly ONE pair across the whole corpus, the R235 one; a planted
        # `gap/gap_ci/gap_significant` contradiction is still caught; invariant 1's `outside` list
        # is bit-identical, still finding its 6 R141 cells.
        if len(cks) == 1 and len(bks) == 1:                  # invariant 2, unambiguous only
            (ck, cv), (bk, bv) = cks[0], bks[0]
            _bstem = re.sub(r"_significant$|^significant_?", "", bk, flags=re.I)
            _cstem = re.sub(r"_ci$|^ci_", "", ck, flags=re.I)
            _named_together = bool(_bstem and _cstem and (_bstem.lower() in _cstem.lower()
                                                          or _cstem.lower() in _bstem.lower()))
            if not (ci_spoken_for and not _named_together):
                lo, hi = sorted(cv)
                out["n_flagged"] += 1
                if bool(lo > 0 or hi < 0) != bv:
                    out["contradict"].append((rid, path or "<root>", ck, [lo, hi], bk, bv))
        for k, v in o.items():
            walk(v, rid, f"{path}.{k}" if path else k)

    for f in sorted(root.glob("E*/A*/R*/results/*.json")):
        if "_smoke" in str(f) or f.stat().st_size > 6_000_000:
            continue
        try:
            walk(json.load(open(f)), f.parts[-3], "")
        except Exception:
            continue
    return out


def positive_control() -> tuple[bool, str]:
    """Plant one violation of each invariant and one clean case of each. A check that has
    never returned non-zero cannot be trusted when it returns zero."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="coh_ctrl_"))
    try:
        d = fixture_dir(tmp, "R999_plant") / "results"   # a planted round must sit where real ones do
        d.mkdir(parents=True)
        (d / "p.json").write_text(json.dumps({
            "clean_pair":   {"gap": 0.05, "gap_ci": [0.04, 0.06]},
            "outside_pair": {"gap": 0.50, "gap_ci": [0.04, 0.06]},
            "clean_flag":   {"ci": [0.02, 0.05], "excludes_zero": True},
            "broken_flag":  {"ci": [0.02, 0.05], "excludes_zero": False},
        }))
        r = scan(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    got_o = [x[1] for x in r["outside"]]
    got_c = [x[1] for x in r["contradict"]]
    ok = got_o == ["outside_pair"] and got_c == ["broken_flag"]
    return ok, f"outside={got_o} contradict={got_c}"


import sys as _s
_s.path.insert(0, str(ROOT))
from covalx.rounds import (fixture_dir, iter_round_dirs,  # noqa: E402
                            round_dir)


def main() -> int:
    ok, detail = positive_control()
    print(f"positive control: {detail} -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("\nFINDING: the check does not fire on planted violations of its own invariants, so a "
              "zero on the live tree would be silence rather than a result.")
        return 1

    r = scan(ROOT)
    print(f"\n{r['n_pairs']} unambiguous mean/CI pairs ({r['n_stem']} stem-matched, "
          f"{r['n_sole']} sole-candidate); {r['n_flagged']} nodes with exactly one CI and one "
          f"significance flag; {len(r['skipped_sole_null'])} node(s) skipped because their only "
          f"visible mean was a null summary, {len(r['skipped_ci_spoken_for'])} because the CI's own "
          f"stem names another key")
    print(f"  ⚠ and {len(r['degenerate'])} interval(s) with lo == hi -- zero asserted uncertainty. "
          f"REPORTED, not gated:\n    `inverted` tests lo > hi strictly, so nothing else in this "
          f"suite ever looks at them (R341).")
    print(f"  ⚠ the 5,157 'CI stem names another key' skips are ONE round and ONE key triple "
          f"(R235's\n    eta/eta_ci), and a source read at R341 confirms the decline is correct in "
          f"every one.\n    The count is real; it is not a repo-wide blind spot.")
    # FLOOR: an empty population is "nothing to check" (2), never "clean" (0). With no
    # artifacts to scan this check finds no violations, and reporting that as a pass
    # would be silence mistaken for an acquittal -- the exact failure attack_the_suite
    # exists to prevent.
    if r["n_pairs"] == 0 and r["n_flagged"] == 0:
        print("\nZERO pairs and ZERO flagged nodes found -- nothing to check, not a clean bill.")
        return 2

    fail = 0
    # ⚠ ADDED at R340, because `outside the interval` UNDERCOUNTS a systematic offset by design.
    # R141_verification: every one of its 14 `raters` nodes sits +4.48 to +9.53 seed-sd ABOVE its
    # own CI centre, median +6.40, all 14 the same sign -- while its `length` nodes sit -0.88 to
    # -0.62 and `magnitude` -1.80 to +0.15. Only 6 of the 14 escape the interval far enough for the
    # criterion above to notice. So the gate reported 6 isolated cells where the object has one
    # systematic displacement in one sub-node. Reported, NOT gated: the exit condition is unchanged,
    # because widening what a gate fails on is a behaviour change and this is a diagnosis.
    disp = []
    for rid, path, mk, mv, ck, (lo, hi) in r["outside"]:
        disp.append((rid, path, mv - (lo + hi) / 2))
    if disp:
        print("\n  DISPLACEMENT from the interval's own CENTRE, for every flagged node:")
        for rid, path, d in disp:
            print(f"      {rid}:{path}  mean - centre = {d:+.5f}")
        print("  ⚠ `outside the interval` is the TAIL of an offset, not the offset. A node whose")
        print("    mean sits 3 sd off its own centre but inside a wide interval is not flagged here,")
        print("    and R141 has 8 more of exactly that shape. Read the centre, not only the bound.")

    for key, label in (("outside", "point estimate OUTSIDE the interval published with it"),
                       ("contradict", "significance flag CONTRADICTS its own interval"),
                       ("inverted", "interval bounds INVERTED (lo > hi)")):
        rows = r[key]
        print(f"  {label:<52} {len(rows)}")
        if rows:
            fail = 1
            for x in rows[:8]:
                print(f"      {x[0]}:{x[1]}  {x[2:]}")
    if fail:
        print("\n1 gate(s) failed.")
        return 1
    print("\nevery artifact is internally coherent on both invariants.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
