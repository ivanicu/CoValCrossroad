"""Three nulls with no resolution statement -- and all three could always compute one.

r204 deposited a defect naming three standing nulls that state no MDE, no power and no
effect-over-floor. Reading them to derive one produced a better result than expected: every one
publishes a confidence interval, so the resolution was always derivable from what was already
written down. The defect was not that the quantity was unavailable. It was that nobody had taken
the two lines to compute it, in a project that has told other people to.

MDE from a published interval is arithmetic: se = width / (2 x 1.96), and the smallest effect
detectable at 80% power with alpha .05 is (1.96 + 0.8416) x se. No new data, no new judge, no
re-run. That is what makes the omission worth recording rather than excusing -- the cost was never
the reason.

AND THE THIRD ONE EXPLAINS A RETRACTION THIS PROJECT ALREADY MADE. r133's veto claim was withdrawn
because it failed in 7 of 12 held-out halves. Nobody asked WHY. If its MDE exceeds its own effect,
the failure was not bad luck in the splits -- it was a design that could never have supported the
sentence, and the held-out sweep was rediscovering that the hard way.

Each null is scored against the effect it had to rule out, because an MDE alone is a number
without a question.
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "db"))
OUT = pathlib.Path(__file__).resolve().parent / "results"

import derivation_chain as dc  # noqa: E402

Z_A, Z_P = 1.959964, 0.8416212


def se_from_ci(lo, hi):
    return (hi - lo) / (2 * Z_A)


def mde(se):
    return (Z_A + Z_P) * se


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cases = [
        ("the-compiled-rubric-does-not-inherit%",
         "the compiled rubric does not inherit the aggregation target's bias",
         0.0091, (-0.0039, 0.0221),
         0.0441, "the difficulty control -- the pooled crowd's own Borda ordering -- shows "
                 "+0.0441 world-bias on the same cells, which is the effect this null must be "
                 "able to see"),
        ("the-veto-is-lost-by-aggregation%",
         "core is not worse than a human peer at respecting vetoes",
         -0.0172, (-0.0311, -0.0040),
         0.0172, "its OWN effect: core 15.47% against a human peer 17.19%, a gap of 1.72pp. A "
                 "design whose MDE exceeds the effect it is testing cannot support the sentence "
                 "it was used to write"),
        ("whether-disagreement-ITSELF%",
         "disagreement predicts being dropped, after adjusting for rating magnitude (design A)",
         0.003, (-0.019, 0.025),
         0.098, "design A's own RAW association, -0.098, which adjustment is supposed to explain "
                "away"),
    ]

    print("=" * 100)
    print("MDEs FOR THE THREE NULLS r204 FLAGGED AS CARRYING NO RESOLUTION")
    print("=" * 100)
    print(f"  {'null':52s} {'observed':>9s} {'se':>8s} {'MDE':>8s} {'compare':>8s} {'ratio':>7s}")
    out = []
    for pat, label, obs, ci, comp, why in cases:
        row = dc.q("SELECT name FROM node WHERE name LIKE %s", (pat,))
        name = row[0][0] if row else pat
        se = se_from_ci(*ci)
        M = mde(se)
        ratio = M / abs(comp)
        out.append({"node": name, "label": label, "observed": obs, "ci": list(ci),
                    "se": se, "mde": M, "comparator": comp, "ratio": ratio, "why": why})
        print(f"  {label[:52]:52s} {obs:+9.4f} {se:8.5f} {M:8.4f} {comp:+8.4f} {ratio:7.2f}")

    print("\n" + "=" * 100)
    print("READING, ONE NULL AT A TIME -- an MDE without the effect it must see is a number")
    print("=" * 100)
    for r in out:
        print(f"\n  {r['label']}")
        print(f"    MDE {r['mde']:.4f} against {r['why'][:88]}")
        if r["ratio"] < 0.5:
            print(f"    -> WELL POWERED. It could have detected {r['ratio']:.0%} of that effect and "
                  f"saw {r['observed']:+.4f}.")
            print(f"       The null is evidence, not silence.")
        elif r["ratio"] < 1.0:
            print(f"    -> ADEQUATE. Detects {r['ratio']:.0%} of the effect in question; a subtler "
                  f"one would have been missed.")
        else:
            print(f"    -> UNDERPOWERED BY {r['ratio']:.2f}x. The design could NOT have detected an")
            print(f"       effect even as large as the one it was testing, so the null is SILENCE.")

    veto = [r for r in out if "veto" in r["label"]][0]
    print("\n" + "=" * 100)
    print("AND THE THIRD ONE EXPLAINS A RETRACTION THIS PROJECT ALREADY MADE")
    print("=" * 100)
    print(f"  r133 claimed 'core beats a human peer, significantly' and withdrew it after the")
    print(f"  comparison failed in 7 of 12 held-out halves. Nobody asked why.")
    print(f"  Its MDE is {veto['mde']:.4f} and the effect it was testing is "
          f"{abs(veto['comparator']):.4f} -- a ratio of {veto['ratio']:.2f}.")
    if veto["ratio"] > 1:
        print(f"  THE DESIGN COULD NEVER HAVE SUPPORTED THE SENTENCE. Its minimum detectable effect")
        print(f"  is LARGER than the effect it measured, so the full-sample CI barely excluding")
        print(f"  zero was luck, and halving the data removed the luck. The held-out sweep was")
        print(f"  rediscovering a power problem the hard way, twelve times.")
        print(f"  That is a mechanistic account of a retraction this project made empirically, and")
        print(f"  it was available from the numbers already in the node's own statement.")

    print("\n" + "=" * 100)
    print("WHAT THIS SAYS ABOUT THE DEFECT r204 RECORDED")
    print("=" * 100)
    print(f"  All three nulls PUBLISH a confidence interval, so the resolution was always two")
    print(f"  lines of arithmetic away -- no new data, no judge, no re-run. The defect was never")
    print(f"  that the quantity was unavailable. It was that nobody computed it, in a project")
    print(f"  whose own standard demands it of others.")
    print(f"  The r204 defect node stands as written; what changes is its remedy, from 'these need")
    print(f"  experiments' to 'these needed two lines', which is a worse look and the accurate one.")
    print(f"\n  LIMIT: an MDE from a published CI inherits that CI's assumptions -- clustering,")
    print(f"  normal approximation, whatever the original round did. Where the CI was")
    print(f"  cluster-bootstrapped (the veto null, 4,000 fits over 5 seeds) that is a real")
    print(f"  interval; where it was iid it would understate the SE and so understate the MDE,")
    print(f"  making the design look better powered than it is. None of these three is iid.")

    (OUT / "mdes.json").write_text(json.dumps({"cases": out}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
