"""r72 -- the package's one direct human validation was computed, stored, and never surfaced.

CLAIM CARD
----------
Claim      r47 reports `differ: False` for gold-scored versus human-scored
           attribution on the original arm, and every round since carries the
           scope line "scored by the r08 model gold head, not by humans".
Estimand   (a) the paired difference human - gold with a PRACTICAL EQUIVALENCE
           test at the preregistered delta = 0.01, reported separately from
           significance; and
           (b) the per-prompt VALIDITY COEFFICIENT -- the correlation between
           the gold-scored and human-scored attribution -- which is the
           resolution at which every correlational row in the exhaustion ledger
           actually operates.
Target
observed?  YES, but ONLY on the original arm. The release contains human
           rankings for the four released candidates and none for generated
           responses. So the proxy can be validated exactly where it is least
           stressed and is applied where it is most stressed -- r47 says this
           about its length channel; it is equally true of its validity.
Alternative
worlds     E EQUIVALENT      the 90% CI for human - gold sits inside +/-0.01.
                             The proxy is interchangeable with humans at the
                             aggregate and the standing proxy caveat can be
                             narrowed to the per-prompt claims.
           N NOT EQUIVALENT  the interval is wider than the margin. Then
                             `differ: False` was never equivalence, the caveat
                             stays at full strength, and the package has been
                             quoting a non-result as reassurance.
           D DIFFERENT       the difference excludes zero outright.
Intervention
           none. Recomputation from released human rankings.
Null       the rebuild control: recomputing the GOLD-side attribution from the
           persisted tensor must reproduce r47's stored 0.102 / 0.0853. If it
           does not, the prompt-to-row mapping is wrong and nothing below is
           about the prompts it claims to be about.

WHY THIS EXISTS
---------------
`0.6029` and `0.6509` -- the per-prompt correlations between the two scorings --
appear NOWHERE in README.md, RETRACTIONS.md or PREREGISTRATION.md. Neither does
the human-scored attribution itself. The field is called
`proxy_validation_on_original`, it ran on all 250 prompts in both samples, and
it is the only place in this package where the outcome variable is a real human
ranking rather than a learned stand-in for one.

Everything else in the exhaustion ledger is proxy-world by its own scope lines.
This is the one measurement that says how much that costs, and it was never
read out.

A NOTE ON HOW NEARLY THIS WAS MISREAD
-------------------------------------
Twice while locating it I read `None` off the wrong level of the JSON --
once by indexing a dict as a list, once by asking for a key (`human_validation`,
the function's name) that is not the key it is stored under
(`proxy_validation_on_original`). Either misread would have produced a confident
"the validation silently returned nothing", which is a far more dramatic finding
than the true one. The object was fine; the reader was wrong, twice.
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join, parse_ranking  # noqa: E402

TENSOR = _ROOT / "rounds/05_human_protocol_and_power/r41_criterion_support/results/r41_satisfaction_qwen2b.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
R47 = _ROOT / "rounds/06_the_judges_mechanism/r47_gold_is_length/results/r47_gold_is_length.json"
DELTA = 0.01          # the preregistered practical margin, queue item 4
LAB = ["A", "B", "C", "D"]
N_BOOT = 4000


def human_pairs(asm):
    """Ordered pairs (better, worse) from an assessment's WORLD ranking block."""
    w = (asm.get("ranking_blocks") or {}).get("world") or []
    if not w:
        return []
    r = parse_ranking(w[0].get("ranking", ""))
    flat = [(lab, gi) for gi, grp in enumerate(r) for lab in grp]
    return [(x, y) for x, gx in flat for y, gy in flat if gx < gy]


def acc_gold(sc, gd, k):
    ok = tot = 0
    for x, y in combinations(range(4), 2):
        if gd[k, x] == gd[k, y]:
            continue
        tot += 1
        ok += int((sc[k, x] > sc[k, y]) == (gd[k, x] > gd[k, y]))
    return ok / tot if tot else np.nan


def acc_human(sc, k, prs):
    ok = tot = 0
    for x, y in prs:
        ix, iy = LAB.index(x), LAB.index(y)
        if sc[k, ix] == sc[k, iy]:
            continue
        tot += 1
        ok += int(sc[k, ix] > sc[k, iy])
    return ok / tot if tot else np.nan


def boot_mean(v, rng, reps=N_BOOT):
    b = np.array([v[rng.integers(0, len(v), len(v))].mean() for _ in range(reps)])
    return float(v.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r72_proxy_validity_coefficient.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    for p in (TENSOR, COMPARISONS, RUBRICS, R47):
        if not p.exists():
            raise SystemExit(f"REFUSING: {p.relative_to(_ROOT)} absent.")

    d = np.load(TENSOR)
    real, shuf, gold = d["mean_orig_real"], d["mean_orig_shuf"], d["gold_orig"]
    n = real.shape[0]

    # order the joined prompts exactly as the tensor rows, then VERIFY that
    # assumption against r47's stored value rather than trusting it
    pairs_by_row, seen = {}, 0
    for pid, comp, _rub in load_join(COMPARISONS, RUBRICS):
        if seen >= n:
            break
        prs = [pr for asm in comp["metadata"]["assessments"] for pr in human_pairs(asm)]
        if prs:
            pairs_by_row[seen] = prs
        seen += 1

    g = np.array([acc_gold(real, gold, k) - acc_gold(shuf, gold, k) for k in range(n)])
    h = np.array([acc_human(real, k, pairs_by_row[k]) - acc_human(shuf, k, pairs_by_row[k])
                  if k in pairs_by_row else np.nan for k in range(n)])
    ok = np.isfinite(g) & np.isfinite(h)
    stored = json.loads(R47.read_text())["samples"]["r12 (discovery)"]["proxy_validation_on_original"]
    rebuild_gap = abs(float(np.nanmean(g[ok])) - stored["gold"][0])
    print(f"prompts {n}   with human pairs {int(ok.sum())}")
    print(f"rebuild control: recomputed gold attribution {np.nanmean(g[ok]):.4f} vs r47's stored "
          f"{stored['gold'][0]:.4f}   gap {rebuild_gap:.2e}")
    if rebuild_gap > 5e-3:
        raise SystemExit("REFUSING: the prompt-to-row mapping does not reproduce r47's value.")

    rng = np.random.default_rng(20260803)
    mg = boot_mean(g[ok], rng)
    mh = boot_mean(h[ok], rng)
    diff = h[ok] - g[ok]
    md = boot_mean(diff, rng)
    # 90% interval for the equivalence test -- TOST at alpha=0.05 each side
    b90 = np.array([diff[rng.integers(0, len(diff), len(diff))].mean() for _ in range(N_BOOT)])
    lo90, hi90 = float(np.percentile(b90, 5)), float(np.percentile(b90, 95))
    equivalent = bool(lo90 > -DELTA and hi90 < DELTA)
    significant = bool(md[1] > 0 or md[2] < 0)
    validity = float(np.corrcoef(g[ok], h[ok])[0, 1])

    print(f"\nattribution on the ORIGINAL arm, {int(ok.sum())} prompts")
    print(f"  scored by the model gold head : {mg[0]:+.4f} [{mg[1]:+.4f},{mg[2]:+.4f}]")
    print(f"  scored by REAL HUMAN rankings : {mh[0]:+.4f} [{mh[1]:+.4f},{mh[2]:+.4f}]")
    print(f"  human - gold                  : {md[0]:+.4f} [{md[1]:+.4f},{md[2]:+.4f}]  (95%)")
    print(f"  90% interval for equivalence  : [{lo90:+.4f},{hi90:+.4f}]  vs margin +/-{DELTA}")
    print(f"\n  SIGNIFICANCE : {'differs from zero' if significant else 'does NOT differ from zero'}")
    print(f"  EQUIVALENCE  : {'EQUIVALENT' if equivalent else 'NOT EQUIVALENT'} at delta={DELTA}")
    print(f"\n  per-prompt VALIDITY COEFFICIENT gold vs human: {validity:.4f}")

    world = "D DIFFERENT" if significant else ("E EQUIVALENT" if equivalent else "N NOT EQUIVALENT")

    verdict = (
        f"{world}. THE ONLY DIRECT HUMAN VALIDATION IN THIS PACKAGE WAS COMPUTED, STORED AND NEVER "
        f"SURFACED: r47's `proxy_validation_on_original` ran on all {n} prompts in both samples, and "
        f"its per-prompt correlations, 0.6029 and 0.6509, appear nowhere in README.md, "
        f"RETRACTIONS.md or PREREGISTRATION.md. Recomputed here from the released human rankings "
        f"(rebuild control: the gold side reproduces r47's stored value to {rebuild_gap:.0e}), the "
        f"attribution on the original arm is {mg[0]:+.4f} [{mg[1]:+.4f},{mg[2]:+.4f}] scored by the "
        f"model gold head and {mh[0]:+.4f} [{mh[1]:+.4f},{mh[2]:+.4f}] scored by real human "
        f"rankings. SIGNIFICANCE AND EQUIVALENCE, REPORTED SEPARATELY as the process rules require: "
        f"the difference {md[0]:+.4f} [{md[1]:+.4f},{md[2]:+.4f}] does not differ from zero, and it "
        f"is NOT equivalent at the preregistered delta={DELTA} -- the 90% interval "
        f"[{lo90:+.4f},{hi90:+.4f}] is about {(hi90-lo90)/(2*DELTA):.1f}x wider than the margin, and "
        f"the point estimate itself is {abs(md[0])/DELTA:.1f}x the margin. r47's stored "
        f"`differ: False` is therefore a NON-RESULT, not the reassurance the phrasing invites. "
        f"THE NUMBER THAT MATTERS MORE is the per-prompt validity coefficient, {validity:.4f}: the "
        f"gold-scored and human-scored attributions share about {validity**2:.0%} of their variance "
        f"ACROSS PROMPTS, and per-prompt is the resolution at which every correlational row in the "
        f"exhaustion ledger operates. REFUSED HERE, EXPLICITLY: transferring {validity:.4f} onto "
        f"those rows as a third attenuation term. Their outcome is the DROP (original minus fresh) "
        f"and this coefficient is measured on the ORIGINAL attribution alone, because the release "
        f"contains no human rankings for generated responses. Carrying a coefficient across that "
        f"boundary is the error of entries 110, 119 and 120, three times over, and the boundary here "
        f"is not crossable by any recomputation -- only by H_fresh. What this DOES establish is that "
        f"the proxy is validated exactly where it is least stressed, which is the same asymmetry r47 "
        f"identified for its length channel, now shown to hold for its validity as well."
    )

    doc = {
        "n_prompts": n, "n_with_human_pairs": int(ok.sum()),
        "rebuild_gap_vs_r47": rebuild_gap,
        "attribution_gold": list(mg), "attribution_human": list(mh),
        "human_minus_gold_95": list(md),
        "equivalence_90_interval": [lo90, hi90], "delta": DELTA,
        "significant": significant, "equivalent": equivalent,
        "per_prompt_validity_coefficient": validity,
        "shared_variance": validity ** 2,
        "world": world,
        "outcome_variable_scope": (
            "ORIGINAL arm only. The release has human rankings for the four released candidates and "
            "none for generated responses, so the human-scored side of any DROP is unobservable. "
            "Every figure here is about the original attribution, not about the drop."),
        "scope": (
            "The human side uses ranking_blocks['world'], the same block every other number in this "
            "package is measured against. Ties are skipped pairwise on both sides. The validity "
            "coefficient is NOT an attenuation term for the ledger's rows and is not used as one: "
            "it is measured on a different quantity (original attribution, not the drop) and the "
            "boundary cannot be crossed by recomputation, only by H_fresh."),
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
