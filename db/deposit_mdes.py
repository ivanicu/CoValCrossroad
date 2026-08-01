"""The three MDEs, and the retraction one of them explains."""
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
    for nm, desc, tgt_like, note in [
        ("power-aggregation-target-null",
         "POWER. MDE 0.0186 at 80% power (se 0.00663 from the published CI [-0.0039,+0.0221]) "
         "against the +0.0441 world-bias the difficulty control shows on the same cells. Ratio "
         "0.42: the design could detect 42% of the bias it had to rule out and saw +0.0091. A "
         "POWERED null -- evidence, not silence.",
         "the-compiled-rubric-does-not-inherit%", "r205-mde-from-published-ci"),
        ("power-veto-peer-null",
         "UNDERPOWERED BY 1.13x, and this explains a retraction made empirically. MDE 0.0194 "
         "against an effect of 0.0172 -- core 15.47% versus a human peer 17.19%. A design whose "
         "minimum detectable effect EXCEEDS the effect it measures cannot support the sentence it "
         "was used to write, so the full-sample CI barely excluding zero was luck and halving the "
         "data removed it. The held-out sweep that failed in 7 of 12 partitions was rediscovering "
         "a power problem twelve times. 'core is not worse than a human peer' is SILENCE at this "
         "resolution, not a supported null.",
         "the-veto-is-lost-by-aggregation%", "r205-mde-from-published-ci"),
        ("power-disagreement-adjusted-null",
         "POWER for design A's magnitude-adjusted null. MDE 0.0314 (se 0.01122 from CI "
         "[-0.019,+0.025]) against design A's own raw association of -0.098. Ratio 0.32: it could "
         "detect a third of the raw effect surviving adjustment and saw +0.003. The A-versus-B "
         "disagreement is therefore a DESIGN difference, not one design being blind.",
         "whether-disagreement-ITSELF%", "r205-mde-from-published-ci"),
    ]:
        N[nm] = node(nm, "control", desc, d=8, status="settled")
        evid(N[nm], note, "se = CI width / (2 x 1.96); MDE = (1.96 + 0.8416) x se. No new data.", 8)
        row = dc.q("SELECT id FROM node WHERE name LIKE %s", (tgt_like,))
        if row:
            edge(N[nm], row[0][0], "tested_by", note="MDE derived from the node's own interval")

    # the veto null is now known to be silence, so its status must move
    row = dc.q("SELECT id, status FROM node WHERE name LIKE 'the-veto-is-lost-by-aggregation%'")
    if row:
        nid, old = row[0]
        dc.q("UPDATE node SET status='partial', statement = statement || %s WHERE id=%s",
             ("  POWER (r205): the peer comparison is UNDERPOWERED by 1.13x -- MDE 0.0194 against "
              "an effect of 0.0172 -- so 'core is not worse than a human peer' is silence at this "
              "resolution rather than a supported null. The ORDERING result (self 0.039 < "
              "full_signed 0.138 < core 0.155 < full_equal 0.278 < chance 0.378), which is stable "
              "in all 12 held-out partitions, is unaffected.", nid))
        print(f"  the-veto-is-lost-by-aggregation: {old} -> partial (peer comparison underpowered)")

    dc.q("UPDATE node SET statement = statement || %s WHERE name=%s",
         ("  RESOLVED (r205): all three nulls PUBLISH a confidence interval, so the MDE was always "
          "two lines of arithmetic away -- no new data, no judge, no re-run. The remedy was never "
          "'these need experiments'; it was 'these needed two lines'.",
          "three-nulls-without-a-resolution"))
    print(f"deposited {len(N)} power controls; the r204 defect node annotated with its remedy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
