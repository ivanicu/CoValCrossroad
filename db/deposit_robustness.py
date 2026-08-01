"""The robustness verdicts, attached to the claims they tested -- and one status changed by them.

r201 and r202 attacked four standing claims with a calibrated jackknife. Those verdicts lived in
two round directories and a results/*.json, which r200 established is the same as not being in the
index. Worse: one of them CHANGES a claim's status, and a graph that records a claim as settled
while a later round found it marginal is not stale, it is wrong.

WHAT GOES IN:
  four CONTROL nodes, one per attack, each edged to the claim it tested
  one INSTRUMENT node for covalx/robust.py, including the two defects its own attack suite found
  one STATUS CHANGE: post-hoc-rationalisation settled -> partial, because MARGINAL means the
  instrument cannot separate a clean effect from a spiked one at that effect size

THE STATUS CHANGE IS THE POINT. node() upserts with ON CONFLICT DO NOTHING, so re-declaring a node
does not update it -- a design that protects history and silently swallows corrections. The update
is therefore explicit and states its reason in the statement, which is how every other retraction
in this graph is recorded.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "db"))
import derivation_chain as dc  # noqa: E402
from derivation_chain import edge, evid, node  # noqa: E402


def main() -> int:
    N = {}
    N["robustness-instrument"] = node(
        "robustness-instrument", "instrument",
        "covalx/robust.py -- a calibrated jackknife. Deletes the k most favourable units until the "
        "95% interval touches zero, and compares k against what a CLEAN normal effect of the same "
        "n, mean and sd survives, because a deletion count alone is uninterpretable. Its own "
        "attack suite found two defects: (1) the reference p10 is a DISTRIBUTION, so the verdict "
        "is three-valued and a result inside the batch spread returns MARGINAL; (2) below roughly "
        "z 3 the reference itself dies at k<=2, so nothing can score below the threshold and NOT "
        "CONCENTRATED would be issued for every input including a pure spike -- now refused as NO "
        "RESOLUTION. Conservative by design: an effect carried entirely by 30 planted outliers "
        "returns MARGINAL, so MARGINAL reads as 'possibly concentrated', never 'probably fine'.",
        d=8, status="settled")
    evid(N["robustness-instrument"], "r202-attack-suite",
         "clean z~10 -> NOT CONCENTRATED (kill@87, p10 63-66); 30 planted outliers -> MARGINAL "
         "(kill@22, p10 19-23); weak z~2 -> NO RESOLUTION (p10 pinned at 1)", 8)

    # EXPLICIT TAGS, not string surgery. The first version built the evidence tag with
    # nm.replace("robustness-", "r") + "-jackknife", which turns "robustness-r146-fairness" into
    # "rr146-fairness-jackknife" -- a tag the round matcher (\br\d+\b) cannot read, so r201 and
    # r202 would have counted as depositing nothing. An identifier assembled by mangling another
    # identifier is the same defect as a constant retyped beside a computed one: it looks right and
    # is only checkable by running the thing that consumes it.
    for nm, desc, dlev, target, tag, note in [
        ("robustness-r146-fairness",
         "The distillation-gives-back-fairness contrast is NOT carried by a few units. 851 strata "
         "over 826 prompts, reproduced to four decimals; no single stratum moves the mean by more "
         "than 0.5% of its value; adversarial deletion reaches zero at k=11, where a clean effect "
         "of the same size and n dies at 18 on average (p10 1, p90 36). Ordinary fragility for "
         "z 3.3. The 929-rater anchor is absent from the pool because it carries no rubric.",
         8, "compilation-gives-back-fairness", "r201-calibrated-jackknife",
         "851 strata, kill@11 vs reference 18 (p10 1, p90 36); anchor absent, no rubric"),
        ("robustness-r187-posthoc",
         "MARGINAL. The post-hoc rationalisation DiD dies at k=306 of 4,504 author pairs (6.8%) "
         "against a reference p10 of 303-318 estimated over four batches -- inside the threshold's "
         "own noise, so the instrument cannot separate a clean effect from a spiked one here. The "
         "most influential single prompt moves it 7.0% across 649 prompts, against 0.5% for r146 "
         "and a tenfold move for the claim that died. Not a handful of units; not demonstrably "
         "clean either.",
         7, "post-hoc-rationalisation", "r202-calibrated-jackknife",
         "kill@306 of 4504 vs p10 303-318 over 4 batches; one prompt moves it 7.0%"),
        ("robustness-r193-hedging",
         "NOT CONCENTRATED. The hedging gap between the most- and least-flagged response dies at "
         "k=25 of 312 prompts against a reference p10 of 16-20; one prompt moves it 4.0%. Spread "
         "across the corpus.",
         7, "flagged-responses-hedge-less", "r202-calibrated-jackknife",
         "kill@25 of 312 vs p10 16-20; one prompt moves it 4.0%"),
        ("robustness-r189-rewrite",
         "ROBUST, by the attack its shape allows. The claim is a CONTRAST between correlations, so "
         "leave-one-prompt-out is run on the correlation itself: flipped criteria give -0.138 with "
         "an LOO range of -0.166 to -0.082 over 142 prompts, never approaching the +0.805 for "
         "unflipped criteria that the claim is contrasted against. No single prompt closes the gap.",
         7, "rewrite-loses-the-item", "r202-leave-one-prompt-out",
         "flipped -0.138, LOO range -0.166 to -0.082 over 142 prompts"),
    ]:
        N[nm] = node(nm, "control", desc, d=dlev, status="settled")
        evid(N[nm], tag, note, dlev)
        tgt = dc.q("SELECT id FROM node WHERE name=%s", (target,))
        if tgt:
            edge(N[nm], tgt[0][0], "tested_by", note=note)

    # ---------------------------------------------------------------- the status change
    # node() is ON CONFLICT DO NOTHING, which protects history and silently swallows corrections.
    # So this is explicit, and the reason goes in the statement the way every other retraction here
    # records itself.
    row = dc.q("SELECT id, status FROM node WHERE name='post-hoc-rationalisation'")
    if row:
        nid, old = row[0]
        dc.q("UPDATE node SET status='partial', statement = statement || %s WHERE id=%s",
             ("  ROBUSTNESS (r202): MARGINAL under a calibrated jackknife -- kill@306 of 4,504 "
              "author pairs against a reference p10 of 303-318, inside the threshold's own noise. "
              "The instrument cannot separate a clean effect from a spiked one at this effect "
              "size, and an effect built entirely from planted outliers scores the same. "
              "Downgraded from settled to partial: the DiD stands as measured and its "
              "concentration is unresolved.", nid))
        print(f"  post-hoc-rationalisation: {old} -> partial")

    print(f"deposited {len(N)} nodes; 4 controls edged to the claims they tested")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
