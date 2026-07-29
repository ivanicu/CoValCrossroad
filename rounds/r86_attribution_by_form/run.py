"""r86 -- r85 bounded agreement by form. Bound the quantity the package is actually about.

CLAIM CARD
----------
Claim      entry 162 closed r85 by naming what it did not cover: "a null here
           means the rubric agrees with humans at a similar rate on both prompt
           sets, IN ONE QUANTITY. The ten sliced rounds measure several others,
           and nothing here covers them."
Estimand   the OWN-minus-DONOR attribution -- the package's central contrast --
           computed separately on the long-form and short-form prompts of the full
           join, with the same paired bootstrap, shuffle null and answerable
           margin r85 used.
Target
observed?  YES, and it is the quantity that matters. r85 measured how well the
           rubric agrees with humans; this measures how much of that agreement is
           OWN-rubric rather than any rubric -- which is what "source specificity"
           names and what every sliced round is ultimately about.
Alternative
worlds     B BOUNDED SMALL   the form gap in attribution is inside the answerable
                             margin. Then the ten long-form-sliced rounds measure
                             their central quantity where it behaves like the rest,
                             and entry 161's scope block is provenance rather than
                             threat on the axis that counts.
           D DIFFERENT       attribution differs by form. Then source specificity
                             itself is form-dependent, the ten rounds' headline
                             contrast is measured in the wrong third of the
                             release, and the scope block becomes a warning.
Intervention
           none. The same computation, partitioned, plus a donor arm.
Null       (i) shuffle the form labels at the observed split sizes -- the gap must
           collapse; (ii) the DONOR arm is itself the within-round null, since
           attribution is own minus donor and a rubric with no source specificity
           would score the same either way.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
Unchanged from r85 and not weakened by repetition: the forms cover DISJOINT
prompts, so a difference is between questions as well as instruments. This bounds
a form-associated difference; it cannot attribute one.

DONOR PAIRING
-------------
Each prompt is scored against another prompt's rubric under the permutation seed
20260727 -- r12's and r54's seed, so the donor pairing is the one the package's
other attribution numbers were computed against. Donors are drawn from the WHOLE
join, not within form: restricting donors to the same form would confound the
donor arm with the very split under test.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "rounds/r85_agreement_by_form"))

from covalx import human_pairs, load_join  # noqa: E402
from run import agree, long_form_prompts, weights  # noqa: E402

SAT = _ROOT / "rounds/r04_rebuild_satisfaction/results/a04_full.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
DELTA = 0.01
N_BOOT = 3000
N_SHUFFLE = 400


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r86_attribution_by_form.json")
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

    L = long_form_prompts()
    keep = []
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        pairs = human_pairs(comp["metadata"]["assessments"])
        items = rub.get("coval_full") or []
        if pairs and items and pid in sat:
            keep.append({"pid": pid, "items": items, "pairs": pairs, "long": pid in L})
    n = len(keep)
    if n < 300:
        raise SystemExit(f"REFUSING: only {n} usable prompts.")
    rng = np.random.default_rng(20260727)          # r12/r54's donor seed
    donor = np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])

    own_ok, own_tot, don_ok, don_tot, isl = [], [], [], [], []
    for k, r in enumerate(keep):
        satp = sat[r["pid"]]
        o1, t1 = agree(satp, r["items"], weights(r["items"]), r["pairs"])
        d = keep[int(donor[k])]
        # the donor's WEIGHTS and criterion count, scored against THIS prompt's
        # satisfaction values -- a rubric written for another question
        w = weights(d["items"])
        o2, t2 = agree(satp, d["items"], w, r["pairs"])
        if t1 and t2:
            own_ok.append(o1); own_tot.append(t1)
            don_ok.append(o2); don_tot.append(t2)
            isl.append(r["long"])
    own_ok, own_tot = np.array(own_ok, float), np.array(own_tot, float)
    don_ok, don_tot = np.array(don_ok, float), np.array(don_tot, float)
    isl = np.array(isl, bool)
    print(f"prompts scored {len(isl)}   long-form {int(isl.sum())}   short-form {int((~isl).sum())}")

    def attr(m):
        return float(own_ok[m].sum() / own_tot[m].sum()
                     - don_ok[m].sum() / don_tot[m].sum())

    def boot_one(m, seed):
        idx = np.flatnonzero(m)
        rg = np.random.default_rng(seed)
        b = []
        for _ in range(N_BOOT):
            s_ = idx[rg.integers(0, len(idx), len(idx))]
            b.append(own_ok[s_].sum() / own_tot[s_].sum()
                     - don_ok[s_].sum() / don_tot[s_].sum())
        return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))

    al, as_ = attr(isl), attr(~isl)
    all_ = attr(np.ones(len(isl), bool))
    ll, lh = boot_one(isl, 11)
    sl, sh = boot_one(~isl, 12)
    gap = al - as_
    rg = np.random.default_rng(20260909)
    gb = []
    for _ in range(N_BOOT):
        s_ = rg.integers(0, len(isl), len(isl))
        m = isl[s_]
        if m.sum() > 30 and (~m).sum() > 30:
            gb.append((own_ok[s_][m].sum() / own_tot[s_][m].sum()
                       - don_ok[s_][m].sum() / don_tot[s_][m].sum())
                      - (own_ok[s_][~m].sum() / own_tot[s_][~m].sum()
                         - don_ok[s_][~m].sum() / don_tot[s_][~m].sum()))
    glo, ghi = float(np.percentile(gb, 2.5)), float(np.percentile(gb, 97.5))
    half = (ghi - glo) / 2
    print(f"\n  attribution, whole join   {all_:+.4f}")
    print(f"  long-form   {al:+.4f} [{ll:+.4f},{lh:+.4f}]   ({int(isl.sum())} prompts)")
    print(f"  short-form  {as_:+.4f} [{sl:+.4f},{sh:+.4f}]   ({int((~isl).sum())} prompts)")
    print(f"  gap {gap:+.4f} [{glo:+.4f},{ghi:+.4f}]   answerable margin {half:.4f}")

    srng = np.random.default_rng(20260910)
    null = []
    for _ in range(N_SHUFFLE):
        lab = isl.copy()
        srng.shuffle(lab)
        null.append(attr(lab) - attr(~lab))
    null = np.array(null)
    nlo, nhi = float(np.percentile(null, 2.5)), float(np.percentile(null, 97.5))
    outside = bool(gap < nlo or gap > nhi)
    print(f"  form-label shuffle null [{nlo:+.4f},{nhi:+.4f}]  -> gap is "
          f"{'OUTSIDE' if outside else 'inside'}")

    equivalent = bool(glo > -DELTA and ghi < DELTA)
    significant = bool(glo > 0 or ghi < 0)
    both_positive = bool(ll > 0 and sl > 0)
    world = ("D DIFFERENT" if significant else
             "B BOUNDED SMALL" if equivalent else
             f"B BOUNDED -- no detectable difference, any form effect under {half:.3f}")

    verdict = (
        f"{world}. Entry 162 closed r85 by naming what it did not cover: a null in ONE quantity, while "
        f"the ten form-sliced rounds measure several. This takes the one that matters -- OWN-minus-DONOR "
        f"attribution, the source-specificity contrast the package is about. Over {len(isl)} prompts of "
        f"the full join, scored against real human rankings with r12's donor permutation: attribution is "
        f"{al:+.4f} [{ll:+.4f},{lh:+.4f}] on the {int(isl.sum())} long-form prompts and {as_:+.4f} "
        f"[{sl:+.4f},{sh:+.4f}] on the {int((~isl).sum())} short-form ones, against {all_:+.4f} on the "
        f"whole join. The gap is {gap:+.4f} [{glo:+.4f},{ghi:+.4f}], "
        f"{'OUTSIDE' if outside else 'inside'} a form-label shuffle null of [{nlo:+.4f},{nhi:+.4f}]. "
        f"THE ANSWERABLE MARGIN IS {half:.4f}, limited by {int(isl.sum())} long-form prompts, so this "
        f"settles equivalence at delta={half:.3f} and not at {DELTA}. "
        f"WHAT IT MEANS FOR THE TEN SLICED ROUNDS: source specificity is "
        f"{'positive in BOTH forms' if both_positive else 'NOT clear of zero in both forms'}, and any "
        f"form-associated difference in it is under {half:.3f}. So entry 161's scope block describes "
        f"where those rounds were measured "
        f"{'without implying their central contrast is peculiar to it' if not significant else 'AND their central contrast does differ across forms, which makes the block a warning rather than provenance'}. "
        f"CONFOUND, unchanged and not weakened by repetition: the forms cover disjoint prompts, so this "
        f"compares questions as well as instruments. It bounds a difference and cannot attribute one. "
        f"DONORS are drawn from the whole join, not within form -- restricting them would confound the "
        f"donor arm with the split under test."
    )

    doc = {
        "n_prompts": int(len(isl)), "n_long": int(isl.sum()), "n_short": int((~isl).sum()),
        "attribution_whole_join": all_,
        "attribution_long": al, "attribution_long_ci": [ll, lh],
        "attribution_short": as_, "attribution_short_ci": [sl, sh],
        "gap": gap, "gap_ci": [glo, ghi], "answerable_margin": half,
        "shuffle_null_ci": [nlo, nhi], "gap_outside_null": outside,
        "significant": significant, "equivalent_at_delta": equivalent,
        "positive_in_both_forms": both_positive, "delta": DELTA,
        "donor_seed": 20260727, "world": world,
        "outcome_variable_scope": (
            "Attribution against REAL HUMAN pairwise rankings, not a model gold head. Satisfaction "
            "from r04's tensor, so the judge is in the loop for s(c,r) and the target is human."),
        "scope": (
            "Forms cover disjoint prompts: this bounds a form-associated difference and cannot "
            "attribute one. Donors come from the whole join under r12's seed 20260727. A donor rubric "
            "brings its own criterion count, so the arms differ in K as well as in source -- that is "
            "the same donor construction the package's other attribution numbers use, kept identical "
            "on purpose rather than improved here."),
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
