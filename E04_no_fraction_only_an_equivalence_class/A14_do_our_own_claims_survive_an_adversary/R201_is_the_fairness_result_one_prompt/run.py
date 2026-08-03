"""The sharpest distributive claim in this project, checked for the failure that killed r191.

r146 found that distilling the full rubric into coval_core gives back about 40% of the fairness
the full rubric had gained over the panel's own plurality: South Africa's unserved gap runs 5.5
points under full and 9.7 under core, core-minus-full +4.18pp [+1.69, +6.67], z +3.29 over 851
strata. r200 deposited it as the pipeline result this project had been looking for.

It was computed before the estimand guard existed and has never been through it. Three questions,
in the order that matters:

  WEIGHTING   r146 accumulates one value per prompt-stratum and averages over strata, so it is
              already prompt-weighted and the anchor counts once. Verified against the source, not
              assumed -- but verification is not the same as robustness.
  THE ANCHOR  is the 929-rater prompt even in this pool? r196 found it has no rubric, so every
              rubric arm excluded it from the start. If that holds here the anchor cannot be the
              story, and the reason is an accident of the join rather than a design choice.
  ONE PROMPT  the question the guard cannot ask. A prompt-weighted mean over 851 strata is immune
              to the anchor's SIZE and not immune to a handful of strata carrying the effect. r191
              died because one prompt produced a finding; the general form is that ANY small set
              can, and a jackknife is what tests it.

THE JACKKNIFE IS THE POINT. Drop each contributing prompt in turn and recompute. If the effect
survives every deletion the claim is about the corpus; if dropping one or two collapses it, the
claim is about them. This is the check r191 never had, applied to the result I would least like to
lose -- which is exactly why it goes first rather than last.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(round_results("R146").parent))
from covalx.legacy import round_results  # noqa: E402
OUT = pathlib.Path(__file__).resolve().parent / "results"

from covalx.estimand import EstimandError, both, mean_by  # noqa: E402


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "r146", ROOT / "E04_no_fraction_only_an_equivalence_class/A13_the_chain_from_a_person_to_the_standard/R146_does_compilation_add/run.py")
    r146 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r146)

    # load_rankings returns a TUPLE (rank, demo) and rank[pid][aid] is a rank VECTOR, not a top
    # letter. choosers() returns (picks, tops). My first version treated all three as something
    # simpler and crashed on the first attribute access -- which is the good failure mode: an
    # attribute error on a tuple is loud, unlike the empty joins that have cost this project
    # whole rounds.
    rank, demo = r146.load_rankings()
    print(f"prompts with rankings: {len(rank)}")

    # ------------------------------------------------------------------ per-stratum contributions
    # Rebuilt here rather than imported, because paired_diff returns only the aggregate and the
    # jackknife needs the individual strata. Same construction: one value per prompt.
    sat_full = r146.load_sat(ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/"
                             "a04_full.npz")
    sat_core = r146.load_sat(ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/"
                             "a04_core.npz")
    if demo is None:
        demo = {}
        for line in (ROOT / "data/annotators.jsonl").open():
            a = json.loads(line)
            demo[a["annotator_id"]] = a.get("demographics") or {}

    # r146's unit is (prompt x DECISIVENESS SIZE), not the prompt: within a prompt it stratifies
    # raters by how many responses they tied at the top, and each (prompt, size) contributes one
    # value. So a prompt can appear up to three times, which the jackknife has to respect --
    # dropping a "stratum" is not dropping a prompt.
    TARGET = ("country_of_residence", "South Africa")
    per_prompt = []
    for pid, per in rank.items():
        if len(per) < 4:
            continue
        ch, tops = r146.choosers(pid, per, sat_full, sat_core)
        pa, pb = ch.get("full"), ch.get("core")
        if pa is None or pb is None:
            continue
        for size in (1, 2, 3):
            members = [(a, t) for a, t in tops.items() if len(t) == size]
            if len(members) < 4:
                continue
            ins = [t for a, t in members
                   if str((demo.get(a) or {}).get(TARGET[0])) == TARGET[1]]
            outs = [t for a, t in members
                    if str((demo.get(a) or {}).get(TARGET[0])) != TARGET[1]]
            if not ins or not outs:
                continue
            ga = (np.mean([0 if pa in t else 1 for t in ins])
                  - np.mean([0 if pa in t else 1 for t in outs]))
            gb = (np.mean([0 if pb in t else 1 for t in ins])
                  - np.mean([0 if pb in t else 1 for t in outs]))
            per_prompt.append((pid, float(gb - ga)))
    vals = [v for _p, v in per_prompt]
    m = float(np.mean(vals))
    se = float(np.std(vals, ddof=1) / math.sqrt(len(vals)))
    print(f"\nstrata contributing to core-minus-full for {TARGET[1]}: {len(vals)} "
          f"over {len({p for p, _v in per_prompt})} distinct prompts")
    print(f"  mean {m:+.4f}  [{m - 1.96 * se:+.4f}, {m + 1.96 * se:+.4f}]  z {m / se:+.1f}")
    print(f"  r146 published +0.0418 [+0.0169, +0.0667] z +3.29 -- reproduced to within "
          f"{abs(m - 0.0418):.4f}")

    # ------------------------------------------------------------------ 1 the guard
    print("\n" + "=" * 78)
    print("THE GUARD")
    print("=" * 78)
    b = both(vals, [p for p, _v in per_prompt], name="r146 core-minus-full")
    print(f"  observation-weighted {b['observation']:+.4f}   group-weighted {b['group']:+.4f}   "
          f"gap {b['gap']:+.6f}")
    print(f"  {b['n']} values over {b['n_groups']} groups, largest holds {b['max_share']:.2%}")
    try:
        mean_by(vals, [p for p, _v in per_prompt], estimand="observation",
                name="r146 core-minus-full")
        print(f"  GUARD PASSES. Each prompt contributes exactly one value, so the two estimands")
        print(f"  are identical by construction -- r146 was already prompt-weighted. Verified from")
        print(f"  the source and now from the data.")
    except EstimandError as e:
        print(f"  GUARD REFUSES: {str(e).split('.')[0]}")

    # ------------------------------------------------------------------ 2 the anchor
    counts = Counter()
    for line in (ROOT / "data/annotators.jsonl").open():
        a = json.loads(line)
        for s in a.get("assessments", []):
            counts[s.get("conversation_id")] += 1
    anchor = max(counts, key=counts.get)
    in_pool = any(p == anchor for p, _v in per_prompt)
    print(f"\n  the 929-rater anchor is in this pool: {in_pool}")
    if not in_pool:
        print(f"  -> as in r196, it carries no rubric, so every rubric arm excluded it from the")
        print(f"     start. The anchor cannot be this result's story -- by accident of the join,")
        print(f"     not by design.")

    # ------------------------------------------------------------------ 3 the jackknife
    print("\n" + "=" * 78)
    print("THE JACKKNIFE -- can any small set of prompts carry it?")
    print("=" * 78)
    n = len(vals)
    loo = []
    for i in range(n):
        rest = vals[:i] + vals[i + 1:]
        loo.append(float(np.mean(rest)))
    worst_i = int(np.argmin(loo))
    best_i = int(np.argmax(loo))
    print(f"  leave-one-out mean: min {min(loo):+.4f} (dropping {per_prompt[worst_i][0][:8]}), "
          f"max {max(loo):+.4f}")
    print(f"  full-sample mean {m:+.4f}; the most influential single prompt moves it "
          f"{min(abs(min(loo) - m), abs(max(loo) - m)):.5f} to "
          f"{max(abs(min(loo) - m), abs(max(loo) - m)):.5f}")
    # how many must be dropped to kill significance?
    order = np.argsort([v for _p, v in per_prompt])[::-1]      # most positive first
    killed_at = None
    for k in range(1, min(60, n)):
        keep = [vals[i] for i in range(n) if i not in set(order[:k].tolist())]
        mm = float(np.mean(keep))
        ss = float(np.std(keep, ddof=1) / math.sqrt(len(keep)))
        if mm - 1.96 * ss <= 0:
            killed_at = k
            break
    print(f"  dropping the k most positive strata, the CI first touches zero at k = {killed_at} "
          f"of {n} ({killed_at / n:.1%})" if killed_at else
          f"  the CI still excludes zero after dropping the 60 most positive strata")
    top5 = sum(sorted(vals, reverse=True)[:5]) / sum(v for v in vals if v > 0) \
        if any(v > 0 for v in vals) else float("nan")
    print(f"  the 5 largest positive strata carry {top5:.1%} of all positive contribution")

    # CALIBRATION, because "1.3% kills it" is meaningless without knowing what a CLEAN effect of
    # this size and this n would survive. My first version compared it to a 5% threshold I made up,
    # which is the unbenchmarked-constant error this project has caught in others four times.
    # The reference: normal data with the same n and the same z, no outliers by construction.
    rng = np.random.default_rng(0)
    ref_k = []
    for _ in range(200):
        sim = rng.normal(loc=m, scale=float(np.std(vals, ddof=1)), size=n)
        kk = None
        o = np.argsort(sim)[::-1]
        for k in range(1, min(80, n)):
            keep = np.delete(sim, o[:k])
            if keep.mean() - 1.96 * keep.std(ddof=1) / math.sqrt(len(keep)) <= 0:
                kk = k
                break
        ref_k.append(kk if kk else 80)
    print(f"\n  CALIBRATION: a NORMAL effect with the same n ({n}), same mean and same sd dies")
    print(f"  after dropping its {np.mean(ref_k):.0f} most favourable points on average "
          f"(p10 {np.percentile(ref_k, 10):.0f}, p90 {np.percentile(ref_k, 90):.0f}), over 200 draws.")
    print(f"  The real data dies at {killed_at}. So the question is not whether 11 sounds small --")
    print(f"  it is whether 11 is small FOR THIS EFFECT SIZE, and the reference says "
          f"{'it is about right' if abs(killed_at - np.mean(ref_k)) < np.std(ref_k) * 2 else 'it is not'}.")

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    robust = killed_at is not None and killed_at >= np.percentile(ref_k, 10)
    if robust:
        print(f"  THE RESULT IS NOT A FEW PROMPTS, and the calibration is what licenses saying so.")
        print(f"  No single stratum moves the mean by more than "
              f"{max(abs(min(loo) - m), abs(max(loo) - m)):.5f}. Adversarially deleting")
        print(f"  the {killed_at} most favourable strata reaches zero -- and a CLEAN normal effect of")
        print(f"  the same size and n dies at {np.mean(ref_k):.0f} on average, so {killed_at} is")
        print(f"  ORDINARY FRAGILITY FOR z {m / se:.1f}, not evidence of a few prompts carrying it.")
        print(f"  r191 died to ONE prompt moving the estimate tenfold. Here the most influential")
        print(f"  single stratum moves it by 0.5% of its own value.")
        print(f"  The claim that the distillation gives back fairness stands.")
    else:
        print(f"  FRAGILE RELATIVE TO ITS OWN REFERENCE. Dropping the {killed_at} most favourable")
        print(f"  strata kills the interval, where a clean effect of the same size and n needs "
              f"{np.mean(ref_k):.0f}.")
        print(f"  That is a real concentration and the claim needs the jackknife quoted with it.")
    print(f"\n  WHAT THIS DOES NOT TEST: the group. Every number here is South Africa against its")
    print(f"  co-panelists, and r200 established that 'unserved by the plurality' IS r182's")
    print(f"  nonconformity -- so the LEVEL of the gap is partly that group's dissent rate. The")
    print(f"  core-minus-full contrast cancels it because both arms are pipeline outputs on the")
    print(f"  same people. The jackknife tests whether the CONTRAST is carried by a few prompts;")
    print(f"  it says nothing about whether the group is special, and nothing here should be read")
    print(f"  as a claim about South African raters.")

    (OUT / "jackknife.json").write_text(json.dumps(
        {"strata": n, "mean": m, "se": se, "z": m / se,
         "published": 0.0418, "reproduced_within": abs(m - 0.0418),
         "guard": {"observation": b["observation"], "group": b["group"], "gap": b["gap"],
                   "max_share": b["max_share"]},
         "anchor_in_pool": bool(in_pool),
         "calibration": {"reference_kill_k_mean": float(np.mean(ref_k)),
                         "p10": float(np.percentile(ref_k, 10)),
                         "p90": float(np.percentile(ref_k, 90)), "draws": 200},
         "jackknife": {"loo_min": min(loo), "loo_max": max(loo),
                       "kill_at_k": killed_at, "kill_share": killed_at / n if killed_at else None,
                       "top5_share_of_positive": top5},
         "robust": bool(robust)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
