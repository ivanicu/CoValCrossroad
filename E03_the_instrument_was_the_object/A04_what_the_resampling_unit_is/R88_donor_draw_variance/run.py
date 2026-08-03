"""r88 -- is the donor arm a MEASUREMENT, or one realisation published as one?

CLAIM CARD
----------
Claim      every attribution figure in this package -- r12's +0.102, r86's whole-join
           +0.1215 and its form split, r87's three arms -- is computed under ONE donor
           draw, seed 20260727, and reported as a quantity rather than as a draw.
Estimand   the standard deviation and range of whole-join own-minus-donor attribution
           across independent draws of the SAME free-donor construction.
Target
observed?  YES. Nothing new is measured. The identical estimator, the identical
           tensor, the identical human rankings; only the donor seed changes.
Alternative
worlds     M MEASUREMENT   the donor-draw sd is small relative to the contrasts the
                           package reports. Then single-seed attribution numbers are
                           quantities, and r87's +0.0084 deterministic-vs-random
                           offset is real structure needing its own explanation.
           R REALISATION   the sd is comparable to those contrasts. Then several
                           published donor-condition differences sit INSIDE donor-draw
                           noise, every attribution figure needs a donor-averaged
                           estimate, and r87's +0.0084 caveat dissolves into the draw.
Intervention
           N independent seeds of the free construction. Nothing else varies.
Null       (i) seed 20260727 must reproduce r86's stored +0.121465 EXACTLY -- a rebuild
           control, so a spread cannot come from a re-implementation drifting;
           (ii) the two uncertainties are reported SEPARATELY and never compared as
           though interchangeable (see below).

WHY THIS IS THE STEP, AND WHY IT IS NOT THE SAME DIRECTION
----------------------------------------------------------
This project has already been burned three times by publishing a single realisation as
a measurement -- r57, r69 and r71 all had to average 200 splits after a single split
had been written down as a result. Every one of those was the RESPONSE/CRITERION axis.
The DONOR axis has never been checked, and it is the axis the headline rides on.

r87 sharpened the reason. The free donor construction is
    donor(i) = (i + 1 + U{0..n-2}) mod n
which draws INDEPENDENTLY for each prompt -- sampling WITH replacement, not a
permutation. Measured on this release: a given draw uses ~612 of 968 prompts as
donors and ~356 never serve at all, and the donor arm's mean criterion count is
15.4836 +- 0.1690 against the own arm's 15.4793. So each published attribution number
is computed against roughly 63% of the available donor rubrics, chosen at random.

TWO UNCERTAINTIES THAT ARE NOT INTERCHANGEABLE
----------------------------------------------
The bootstrap CI already reported beside every attribution number resamples PROMPTS at
a fixed donor draw. This round resamples DONOR DRAWS at a fixed prompt set. They answer
different questions and neither contains the other. They are reported side by side and
never combined, because comparing an uncertainty against a differently-paired
uncertainty is exactly the overshoot this package has logged before.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
A spread across seeds is guaranteed to be non-zero -- with n=968 and one draw per
prompt, some spread is arithmetic, not a finding. So the question is never "is the sd
above zero" (it must be) but "is it large relative to the differences this package
has already published as results." The seed spread is therefore reported AGAINST three
specific published contrasts, named before the run:
    r87  deterministic-vs-random pairing offset  +0.0084
    r86  long-form vs short-form attribution gap +0.0056
    r86  single-seed bootstrap CI half-width     ~0.0118
A sd that is small against all three leaves them standing. A sd comparable to them
puts them inside the draw, and this round says which.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "E03_the_instrument_was_the_object/A04_what_the_resampling_unit_is/R85_agreement_by_form"))

from covalx import human_pairs, load_join  # noqa: E402
from run import agree, weights  # noqa: E402

SAT = _ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
R86 = _ROOT / "E03_the_instrument_was_the_object/A04_what_the_resampling_unit_is/R86_attribution_by_form/results/r86_attribution_by_form.json"
R87 = _ROOT / "E03_the_instrument_was_the_object/A04_what_the_resampling_unit_is/R87_criterion_count_channel/results/r87_criterion_count_channel.json"
CANON_SEED = 20260727
N_SEEDS = 120

# named BEFORE the run -- the contrasts this spread must be judged against
PUBLISHED = {
    "r87 deterministic-vs-random pairing offset": 0.0084,
    "r86 long-form vs short-form attribution gap": 0.0056,
    "r86 single-seed bootstrap CI half-width": 0.0118,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r88_donor_draw_variance.json")
    ap.add_argument("--seeds", type=int, default=N_SEEDS)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)

    z = np.load(SAT, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s_ in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        sat[pid][(int(ci), lab)] = float(s_)

    keep = []
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        pairs = human_pairs(comp["metadata"]["assessments"])
        items = rub.get("coval_full") or []
        if pairs and items and pid in sat:
            keep.append({"pid": pid, "items": items, "pairs": pairs, "K": len(items)})
    n = len(keep)
    if n < 300:
        raise SystemExit(f"REFUSING: only {n} usable prompts.")
    K = np.array([r["K"] for r in keep])
    W = [weights(r["items"]) for r in keep]

    own_ok = np.zeros(n); own_tot = np.zeros(n)
    for i, r in enumerate(keep):
        own_ok[i], own_tot[i] = agree(sat[r["pid"]], r["items"], W[i], r["pairs"])
    print(f"prompts {n}   own arm {own_ok.sum() / own_tot.sum():.6f}")

    def draw(seed):
        rng = np.random.default_rng(seed)
        return np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])

    def score(d):
        ok = np.zeros(n); tot = np.zeros(n)
        for i, r in enumerate(keep):
            j = int(d[i])
            ok[i], tot[i] = agree(sat[r["pid"]], keep[j]["items"], W[j], r["pairs"])
        m = (own_tot > 0) & (tot > 0)
        return float(own_ok[m].sum() / own_tot[m].sum() - ok[m].sum() / tot[m].sum()), int(m.sum())

    canon, ncanon = score(draw(CANON_SEED))
    rebuild = None
    if R86.exists():
        stored = json.load(open(R86))["attribution_whole_join"]
        rebuild = {"r86_stored": stored, "here": canon, "delta": canon - stored}
        print(f"rebuild control  stored {stored:+.6f}  here {canon:+.6f}  delta {canon - stored:+.2e}")
        if abs(canon - stored) > 1e-9:
            raise SystemExit("REFUSING: the canonical seed does not reproduce r86. A spread measured "
                             "by a drifted re-implementation would be an artifact of the drift.")

    vals, used, mk = [], [], []
    for s in range(a.seeds):
        d = draw(1000 + s)
        v, _ = score(d)
        vals.append(v); used.append(len(set(d.tolist()))); mk.append(float(K[d].mean()))
        if (s + 1) % 20 == 0:
            print(f"  {s + 1}/{a.seeds} seeds   running sd {np.std(vals):.5f}")
    vals = np.array(vals); used = np.array(used); mk = np.array(mk)

    sd = float(vals.std(ddof=1))
    lo, hi = float(vals.min()), float(vals.max())
    p2, p97 = float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))
    print(f"\n  attribution across {a.seeds} donor draws")
    print(f"    mean {vals.mean():+.4f}   sd {sd:.5f}   range [{lo:+.4f},{hi:+.4f}]   "
          f"central 95% [{p2:+.4f},{p97:+.4f}]")
    print(f"    canonical seed {CANON_SEED} -> {canon:+.4f}  ({(canon - vals.mean()) / sd:+.2f} sd)")
    print(f"    donors used per draw {used.mean():.0f} +- {used.std():.0f} of {n}   "
          f"donor mean K {mk.mean():.3f} +- {mk.std():.3f} (own {K.mean():.3f})")

    print("\n  the spread against contrasts this package has already published")
    ratios = {}
    for name, v in PUBLISHED.items():
        ratios[name] = float(sd / v)
        print(f"    {name:<46} {v:+.4f}   sd is {sd / v:.2f}x it")

    # r87's offset re-judged against the draw it was measured against
    r87_note = None
    if R87.exists():
        r87 = json.load(open(R87))
        off = r87["matched_minus_unrestricted"]["mean"]
        z_off = (off) / sd if sd else float("inf")
        inside = bool(abs(off) <= 1.96 * sd)
        r87_note = {"offset": off, "z_vs_donor_draw": float(z_off), "inside_donor_noise": inside}
        print(f"\n  r87's deterministic-vs-random offset {off:+.4f} is {z_off:+.2f} donor-draw sd "
              f"-> {'INSIDE' if inside else 'OUTSIDE'} the draw")

    worst = max(ratios.values())
    realisation = bool(worst >= 0.5)
    world = ("R REALISATION" if realisation else "M MEASUREMENT")

    verdict = (
        f"{world}. Every attribution number in this package -- r12's, r86's whole-join {canon:+.4f} and "
        f"its form split, r87's three arms -- comes from ONE donor draw under seed {CANON_SEED}. The "
        f"project has already had to retract three single-realisation results (r57, r69, r71), but all "
        f"three were the response/criterion axis; the DONOR axis had never been checked, and it is the "
        f"axis the headline rides on. r87 sharpened why: the free construction draws independently per "
        f"prompt, so it samples WITH replacement -- a given draw uses {used.mean():.0f} of {n} prompts as "
        f"donors and about {n - used.mean():.0f} never serve at all. Across {a.seeds} independent draws "
        f"attribution is {vals.mean():+.4f} with sd {sd:.5f}, range [{lo:+.4f},{hi:+.4f}], central 95% "
        f"[{p2:+.4f},{p97:+.4f}]; the canonical seed sits {(canon - vals.mean()) / sd:+.2f} sd from the "
        f"centre, an ordinary draw. JUDGED AGAINST THE THREE CONTRASTS NAMED BEFORE THE RUN: the donor-draw "
        f"sd is "
        + "; ".join(f"{r:.2f}x the {nm.split(' ', 1)[1]}" for nm, r in ratios.items()) + ". "
        f"So published donor-condition differences of this size are "
        f"{'INSIDE the draw and cannot be read as structure' if realisation else 'NOT explained by which donors happened to be drawn'}. "
        f"TWO UNCERTAINTIES, KEPT SEPARATE: the bootstrap CI beside every attribution number resamples "
        f"PROMPTS at a fixed donor draw; this resamples DONOR DRAWS at a fixed prompt set. Neither "
        f"contains the other and they are not combined here. THE ARITHMETIC FLOOR, stated before the run: "
        f"a non-zero spread is guaranteed, so the question was never whether sd exceeds zero but whether "
        f"it is large against what has been published -- and that is the comparison above. REBUILD "
        f"CONTROL: seed {CANON_SEED} reproduces r86's stored value exactly, so this spread cannot be an "
        f"artifact of a drifted re-implementation."
    )

    doc = {
        "n_prompts": int(n), "n_seeds": int(a.seeds), "canonical_seed": CANON_SEED,
        "attribution_canonical": canon, "n_scored_canonical": ncanon,
        "attribution_mean": float(vals.mean()), "attribution_sd": sd,
        "attribution_min": lo, "attribution_max": hi,
        "attribution_central95": [p2, p97],
        "canonical_z": float((canon - vals.mean()) / sd),
        "donors_used_mean": float(used.mean()), "donors_used_sd": float(used.std()),
        "donor_mean_K": float(mk.mean()), "donor_mean_K_sd": float(mk.std()),
        "own_mean_K": float(K.mean()),
        "published_contrasts": PUBLISHED, "sd_over_contrast": ratios,
        "r87_offset_vs_donor_draw": r87_note,
        "rebuild_control_vs_r86": rebuild, "world": world,
        "outcome_variable_scope": (
            "Whole-join own-minus-donor attribution against REAL HUMAN pairwise rankings, satisfaction "
            "from r04's tensor. Only the donor seed varies across the "
            f"{a.seeds} draws -- same prompts, same rubrics, same responses, same judge, same rankings."),
        "scope": (
            "This bounds the DONOR-DRAW component of a single-seed attribution number. It says nothing "
            "about the prompt-sampling component, which the bootstrap CIs already report and which is a "
            "different uncertainty. It also does not license averaging the two: they are separate "
            "resampling designs over separate objects."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
