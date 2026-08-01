"""The last two stdout-only rounds, deposited -- and one of them turns out to be r182 restated.

r200 left r146 and r147 as the only rounds existing nowhere but their own output. Reading them for
the first time since they ran produces a connection neither round could have made, because the
rounds it connects to did not exist yet.

r145/r146 measured whether a group is UNSERVED BY THE PANEL'S OWN PLURALITY: how often the response
the most people top-ranked is not the one this participant wanted. South Africa came out 15.6
points worse than its co-panelists on a 34% base.

r182, thirty-six rounds later, measured NONCONFORMITY: how often a rater's top choice differs from
the prompt's majority. South Africa came out highest in the panel at 0.540 against a 0.379 mean.

THOSE ARE THE SAME QUANTITY WEARING TWO NAMES. "Unserved by the plurality" and "departs from the
majority" are one event described from two sides. So r145/r146's plurality column is not an
independent finding about distributive cost -- it is r182's trait, restated, and a group that
disagrees with the majority more will be "unserved" more by arithmetic alone.

WHAT SURVIVES THAT, AND IT IS THE PART WORTH KEEPING: the core-minus-full contrast. Both arms are
pipeline outputs scored on the same people and the same prompts, so whatever makes a group depart
from the majority cancels between them. That comparison says the compilation from the full rubric
to the distilled core GIVES BACK about 40% of the fairness the full rubric had gained over
plurality -- and it says so with the group's own dissent rate held fixed by construction.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "db"))
from derivation_chain import edge, evid, node  # noqa: E402


def main() -> int:
    N = {}
    N["full-rubric-serves-better-than-plurality"] = node(
        "full-rubric-serves-better-than-plurality", "my_claim",
        "The pipeline is FAIRER than the panel's own plurality, which is the opposite of the "
        "worry. Unserved rates: plurality 34.0%, full rubric 58.0%, core 49.5% at base -- but the "
        "GROUP GAP is what matters and it shrinks. South Africa's disadvantage runs 15.6 points "
        "under plurality, 5.5 under the full rubric and 9.7 under core. Paired by construction: "
        "same prompt, same panel, same four candidates, matched on decisiveness, 851 strata.",
        d=7, status="settled")
    evid(N["full-rubric-serves-better-than-plurality"], "r146-chooser-swap",
         "core minus plurality -5.97pp [-9.07, -2.87], z -3.78", 7)

    N["compilation-gives-back-fairness"] = node(
        "compilation-gives-back-fairness", "my_claim",
        "THE PIPELINE FINDING, and the one that survives the confound below. Distilling the full "
        "rubric into coval_core re-introduces group disadvantage: South Africa's gap goes 5.5 -> "
        "9.7 points, core minus full +4.18pp [+1.69, +6.67], z +3.29 over 851 strata. Both arms "
        "are pipeline outputs on the same people and prompts, so whatever makes a group depart "
        "from the majority CANCELS between them -- which is why this contrast survives while the "
        "plurality column does not. Roughly 40% of the fairness the full rubric gained over "
        "plurality is given back by the distillation the card calls non-conflicting, "
        "non-redundant and highly rated.",
        d=7, status="settled")
    evid(N["compilation-gives-back-fairness"], "r146-core-minus-full",
         "the within-pipeline contrast holds the group's own dissent rate fixed by construction", 7)

    N["unserved-is-nonconformity-restated"] = node(
        "unserved-is-nonconformity-restated", "fact",
        "A CROSS-ROUND IDENTITY nobody could see when either round ran. r145/r146's 'unserved by "
        "the panel's own plurality' and r182's 'nonconformity -- top choice differs from the "
        "majority' are the same event described from two sides. South Africa is the extreme of "
        "both (15.6pp unserved gap; 0.540 nonconformity against a 0.379 panel mean). So the "
        "plurality column of r146 is not independent evidence of distributive cost; a group that "
        "departs from the majority more is unserved more by arithmetic. Only the within-pipeline "
        "contrasts are informative about the pipeline.",
        d=8, status="settled")
    evid(N["unserved-is-nonconformity-restated"], "r200-consolidation",
         "identified while depositing the last two stdout-only rounds, 36 rounds after the second "
         "of them ran", 8)

    N["serving-gap-lives-in-wide-margins"] = node(
        "serving-gap-lives-in-wide-margins", "my_claim",
        "Tracking and serving are different functionals of one score vector and both results "
        "stand: they correlate 0.818 [0.686, 0.898], sharing 67% of variance, over 43 groups and "
        "15,490 rows. The serving gap is concentrated where the decision margin is WIDE -- South "
        "Africa's gap is 0.15pp (CI spanning zero) on narrow-margin prompts, 12.96pp on middle, "
        "16.04pp on wide. A well-powered null on tracking and a real gap on serving are not in "
        "conflict; the rubric can order responses well and still pick a different winner where "
        "the top two are far apart.",
        d=7, status="settled")
    evid(N["serving-gap-lives-in-wide-margins"], "r147-margin-terciles",
         "cuts at 0.05 and 0.126; narrow CI [-0.0401, 0.0431], wide CI [0.1116, 0.2091]", 7)

    for src, dst, kind, note in [
        ("unserved-is-nonconformity-restated", "full-rubric-serves-better-than-plurality",
         "refines", "the plurality column is the group's dissent rate, not a pipeline property"),
        ("compilation-gives-back-fairness", "unserved-is-nonconformity-restated", "depends_on",
         "the within-pipeline contrast is what remains once the identity is applied"),
        ("serving-gap-lives-in-wide-margins", "compilation-gives-back-fairness", "supports",
         "both locate the cost in what the rubric PICKS rather than how it orders"),
    ]:
        if src in N and dst in N:
            edge(N[src], N[dst], kind, note=note)
    print(f"deposited {len(N)} nodes for r146 and r147")
    print("  and one of them is a cross-round identity: 'unserved by the plurality' IS")
    print("  'nonconformity', so r146's headline column was r182's trait 36 rounds early.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
