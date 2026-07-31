"""Project the claim graph into the paper's supplement, in the template's own schema.

The template ships two supplement tables and they are the publication form of what this project
already keeps in PostgreSQL:

  claim_to_source.csv   one row per CLAIM: its statement, the sources that license it, and the
                        limitation those sources SHARE -- a limitation that every source has in
                        common is not mitigated by having several of them.
  evidence_atlas.csv    one row per (source, claim) pair, with the axes along which that source
                        does or does not carry weight.

The template's atlas codes external literature. Here a source is a ROUND of this campaign, and the
axes are rewritten to the ones that decide whether a round's number means anything:

  instrument_free      0/1  does the round execute a model anywhere?
  control_saturated    0/1  did it run a positive control, a placebo AND its strongest confound?
  held_out             0/1  was it recomputed on data it was not found on?
  replication_breadth  0-3  independent designs that reached it (0 = one, 3 = four or more)
  prior_art_in_card    0/1  is the finding already stated in the release's own DATASET_CARD?

The last column is the one round 140 bought at the price of a day: a result that restates the
object's own documentation is a verification, and coding it as a finding is the error this table
exists to make impossible to repeat.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derivation_chain import q  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "paper" / "supplement"

# rounds whose numbers are computed without executing any model
INSTRUMENT_FREE_ROUNDS = {
    "r132-verbatim-adjudication", "r138-is-there-a-standard",
    "r140-polarity-without-the-judge", "r141-verification",
    "session-direct-count-2026-07-30", "session-partition-2026-07-30",
    "session-source-diff-2026-07-30", "session-text-inspection-2026-07-30",
    "session-self-audit-2026-07-30",
}
# rounds that ran a positive control, a placebo, and the strongest confound in the same script
CONTROL_SATURATED = {
    "r127-whose-sign", "r131-who-is-served", "r132-verbatim-adjudication",
    "r133-the-veto", "r134-do-ratings-individuate", "r135-which-target",
    "r137-batch-gauge", "r138-is-there-a-standard", "r141-verification",
}
HELD_OUT = {"r136-held-out-confirmation", "r141-verification"}
# findings already stated, qualitatively or exactly, in data/DATASET_CARD.md
PRIOR_ART_IN_CARD = {
    "a-zero-LLM-importance-sort-matches-the-compiler",
    "core-is-indistinguishable-from-dropping-the-negatives",
    "core-behaves-as-a-flat-summary-with-a-small-real-weighted-residual",
    "core-retains-the-negative-quarter-at-one-tenth-weight",
    "when-a-contested-criterion-survives-the-majority-captures-it",
    "disagreement-itself-costs-a-criterion-its-place-on-ground-truth",
}


def key(exp: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", exp.lower())[:28] or "unkeyed"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    nodes = q("""SELECT id, kind, name, coalesce(statement,''), coalesce(status,''),
                        coalesce(d_level::text,'')
                 FROM node WHERE kind IN ('my_claim','fact','their_assumption') ORDER BY id""")
    if not nodes:
        print("REFUSING: the claim graph is empty; the supplement would be a table of nothing. "
              "Exits 2.", file=sys.stderr)
        return 2
    ev = q("""SELECT n.name, e.experiment, coalesce(e.finding,''), coalesce(e.d_level::text,'')
              FROM evidence e JOIN node n ON n.id = e.node_id ORDER BY n.name, e.experiment""")
    by_claim: dict[str, list] = {}
    for name, exp, finding, d in ev:
        by_claim.setdefault(name, []).append((exp, finding, d))

    breadth = {}
    for name, rows in by_claim.items():
        indep = sum(1 for e, _f, _d in rows if "independent-design" in e)
        breadth[name] = min(3, indep if indep else max(0, len(rows) - 1))

    with (OUT / "claim_to_source.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["claim_id", "claim", "status", "d_level", "source_keys", "shared_limitation"])
        for nid, kind, name, stmt, status, d in nodes:
            rows = by_claim.get(name) or []
            if not rows:
                continue
            free = all(e in INSTRUMENT_FREE_ROUNDS for e, _f, _d in rows)
            lims = []
            if not free:
                lims.append("Every source routes through one locally rebuilt 2B satisfaction "
                            "judge; the release ships no satisfaction labels. The judge is not "
                            "polarity-symmetric (asking VIOLATE rather than SATISFY moves the "
                            "core-minus-full contrast from -0.0223 to +0.0708), and the arms "
                            "differ precisely in their negatively-rated criteria.")
            if name in PRIOR_ART_IN_CARD:
                lims.append("Stated in the release's own DATASET_CARD: this is a verification "
                            "that the documented method does what it documents, not a finding.")
            if not any(e in HELD_OUT for e, _f, _d in rows):
                lims.append("Discovered and tested on the same prompts; no held-out confirmation.")
            lims.append("One release, one annotator panel, one judge; no external replication is "
                        "available at this site.")
            w.writerow([f"C{nid}", stmt.replace("\n", " "), status, d,
                        ";".join(sorted({key(e) for e, _f, _d in rows})), " ".join(lims)])

    with (OUT / "evidence_atlas.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["source_key", "round", "claim_id", "licensed_claim", "limitation",
                    "instrument_free", "control_saturated", "held_out",
                    "replication_breadth_0_3", "prior_art_in_card", "d_level"])
        for nid, kind, name, stmt, status, d in nodes:
            for exp, finding, ed in (by_claim.get(name) or []):
                w.writerow([key(exp), exp, f"C{nid}", finding.replace("\n", " "),
                            "instrument-free" if exp in INSTRUMENT_FREE_ROUNDS
                            else "conditional on the rebuilt 2B judge",
                            int(exp in INSTRUMENT_FREE_ROUNDS),
                            int(exp in CONTROL_SATURATED), int(exp in HELD_OUT),
                            breadth.get(name, 0), int(name in PRIOR_ART_IN_CARD), ed])

    with (OUT / "exclusion_log.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["claim_id", "withdrawn_claim", "reason", "killed_by"])
        for nid, kind, name, stmt, status, d in nodes:
            if status != "refuted" or kind != "my_claim":
                continue
            killers = q("""SELECT s.name FROM edge e JOIN node s ON s.id = e.src
                           WHERE e.dst = %s AND e.kind = 'overturns'""", (nid,))
            w.writerow([f"C{nid}", stmt.replace("\n", " ")[:400], "withdrawn",
                        "; ".join(r[0] for r in killers) or "(no incoming kill edge)"])

    for f in ("claim_to_source.csv", "evidence_atlas.csv", "exclusion_log.csv"):
        n = sum(1 for _ in (OUT / f).open()) - 1
        print(f"  {f:<24}{n:>5} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
