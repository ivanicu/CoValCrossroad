#!/usr/bin/env python3
"""R832 -- R831's rank claim is an interval, and the direction has to survive both ends.

See PREREGISTRATION.txt, committed before this file was executed.

ESTIMAND        the rank of the best SUBSTANTIVE non-label-reading arm, as an INTERVAL over the two
                readings of ③'s UNKNOWN: lower = unknown-as-ADMITTED, upper = unknown-as-EXCLUDED.
⚠ DERIVATION    this re-scopes committed numbers; it does not re-measure them. Labelled as one.
                What could come out otherwise is only the robustness question below.
IDENTIFICATION  the interval is identified. Deciding the 11 UNKNOWNs is NOT -- it needs a per-arm
                provenance record, and DEFINITION.md already states these do not have one here.
SCOPE           population: R831's 93 arms. instrument: clause3_as_written.partition + R831's
                committed ranks. regime: the two readings of UNKNOWN.
WORLDS          W-DIRECTION-SURVIVES (the top is label-readers under BOTH readings -- R831's world
                stands and only its rank NUMBER becomes an interval) vs W-READING-DEPENDENT (under
                unknown-as-admitted the top is no longer dominated by label-readers -- R831 must be
                scoped to one reading in its README).
KILL            CONDITIONAL. Evaluated only if both positive controls behave and g=0 is null.
POSITIVE CTRL   a synthetic ordering whose top 8 are all admitted must report 0 excluded; one whose
                top 8 are all excluded must report 8. Both required.
NEGATIVE CTRL   ③'s partition recomputed from source twice and compared -- the producer invoked on
                both sides, not `x - x`.
MULTIPLICITY    top-8 and top-16 under two readings = 4 cells, all reported.
ARTIFACT        results/r832_interval.json with source hash.
"""
from __future__ import annotations
import hashlib, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parent.parent
RES = HERE / "results"
sys.path.insert(0, str(ROOT / "assurance"))
import clause3_as_written as C3                                            # noqa: E402

BASELINE = re.compile(r"(^random_|sham|^const|shuffle|^full)", re.I)       # same as R831
R436 = next(A24.glob("R436_*/results/r436_clause4_at_home.json"))


def top_excluded(order, status, k):
    return sum(1 for a in order[:k] if status[a] == "EXCLUDED")


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    print("\n  R832 · R831's RANK CLAIM IS AN INTERVAL\n")

    # ---- controls ------------------------------------------------------------------------
    syn = [f"a{i}" for i in range(20)]
    all_adm = {a: "ADMITTED" for a in syn}
    all_exc = {a: "EXCLUDED" for a in syn}
    pc1 = top_excluded(syn, all_adm, 8) == 0
    pc2 = top_excluded(syn, all_exc, 8) == 8
    print(f"  POSITIVE  synthetic top-8 all ADMITTED -> {top_excluded(syn, all_adm, 8)} excluded   "
          f"{'PASS' if pc1 else '⛔ FAIL'}")
    print(f"  POSITIVE  synthetic top-8 all EXCLUDED -> {top_excluded(syn, all_exc, 8)} excluded   "
          f"{'PASS' if pc2 else '⛔ FAIL'}")

    d = json.loads(R436.read_text())
    a2 = {c["arm"]: c["a2"] for c in d["cells"]}
    arms = list(a2)
    p1, p2 = C3.partition(arms), C3.partition(arms)          # the producer, invoked TWICE
    g0 = p1 == p2
    print(f"  g=0       ③'s partition recomputed from source twice -> "
          f"{'identical   PASS' if g0 else '⛔ FAIL'}")
    exc, adm, unk = p1
    status = {**{a: "EXCLUDED" for a in exc}, **{a: "ADMITTED" for a in adm},
              **{a: "UNKNOWN" for a in unk}}

    order = sorted(arms, key=lambda a: -a2[a])
    rank = {a: i + 1 for i, a in enumerate(order)}

    # ---- the interval --------------------------------------------------------------------
    def best_substantive(treat_unknown_as_admitted):
        pool = [a for a in order
                if status[a] == "ADMITTED"
                or (treat_unknown_as_admitted and status[a] == "UNKNOWN")]
        pool = [a for a in pool if not BASELINE.search(a)]
        return (pool[0], rank[pool[0]], a2[pool[0]]) if pool else (None, None, None)

    hi_arm, hi_rank, hi_a2 = best_substantive(False)         # unknown-as-EXCLUDED -> upper end
    lo_arm, lo_rank, lo_a2 = best_substantive(True)          # unknown-as-ADMITTED -> lower end
    print(f"\n  best SUBSTANTIVE non-label-reading arm, by reading of ③'s UNKNOWN:")
    print(f"     unknown-as-ADMITTED  rank {lo_rank:>2}/93   A2 {lo_a2:.4f}   {lo_arm}")
    print(f"     unknown-as-EXCLUDED  rank {hi_rank:>2}/93   A2 {hi_a2:.4f}   {hi_arm}")
    print(f"     => the claim is the INTERVAL [{lo_rank}, {hi_rank}], not the point {hi_rank}")

    # ---- the robustness question, the only part that could come out otherwise --------------
    cells = {}
    for reading, as_adm in (("unknown-as-EXCLUDED", False), ("unknown-as-ADMITTED", True)):
        st = dict(status)
        if as_adm:
            for a in unk:
                st[a] = "ADMITTED"
        else:
            for a in unk:
                st[a] = "EXCLUDED"
        for k in (8, 16):
            cells[f"{reading}|top{k}"] = top_excluded(order, st, k)
    print(f"\n  label-readers (③-EXCLUDED) at the TOP of the ordering, all 4 cells:")
    for k, v in cells.items():
        kk = int(k.split("top")[1])
        print(f"     {k:<32} {v}/{kk}")

    strict = cells["unknown-as-EXCLUDED|top8"] == 8
    lenient = cells["unknown-as-ADMITTED|top8"] == 8
    controls_ok = pc1 and pc2 and g0
    if not controls_ok:
        world, verdict = "UNVERIFIED", "a control is unfit; no world is chosen"
    elif strict and lenient:
        world = "W-DIRECTION-SURVIVES"
        verdict = ("the top 8 are ③-EXCLUDED under BOTH readings -- R831's world stands and only "
                   f"its rank number becomes the interval [{lo_rank}, {hi_rank}]")
    else:
        world = "W-READING-DEPENDENT"
        verdict = ("the top of the ordering stops being dominated by label-readers under one "
                   "reading -- R831 must be scoped to the other in its README")
    print(f"\n  VERDICT: {world} -- {verdict}\n")

    out = {"world": world, "verdict": verdict,
           "interval_rank": [lo_rank, hi_rank],
           "lower_end": {"arm": lo_arm, "rank": lo_rank, "a2": lo_a2, "reading": "unknown-as-ADMITTED"},
           "upper_end": {"arm": hi_arm, "rank": hi_rank, "a2": hi_a2, "reading": "unknown-as-EXCLUDED"},
           "top_excluded_cells": cells, "n_unknown": len(unk), "unknown_arms": sorted(unk),
           "controls": {"pos_all_admitted": pc1, "pos_all_excluded": pc2, "g0_deterministic": g0},
           "is_a_derivation": True,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]}
    (RES / "r832_interval.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"  artifact -> {RES/'r832_interval.json'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
