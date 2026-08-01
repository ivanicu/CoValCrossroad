"""What survives, read out of the graph rather than out of my memory.

Every summary I could write from recollection would be a summary of what I remember concluding,
which is exactly the thing five adversary findings have shown to be unreliable. This queries the
claim graph instead: statuses, kill edges, evidence rows and recorded limitations, as they actually
stand after the correction sweep.

The ordering is deliberate and is the opposite of a paper's. Retractions first, because a reader who
sees the survivors first will read the retractions as caveats on them rather than as the larger
result. In this phase they ARE the larger result. The count is printed rather than stated here, because it
has already changed twice: claims fell, two were later restored on corrected data, and one
retraction had itself to be retracted.

WHAT THIS CANNOT TELL YOU. A graph says what was recorded, not what was overlooked. Every entry here
survived the attacks that were actually run, and the phase's own history is the argument for
treating that as provisional: three of four instrument-free claims fell to the first adversary who
looked, and the bug behind them had been sitting in a guard I wrote specifically to prevent it.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from derivation_chain import q  # noqa: E402
from status_domains import DOMAIN, needs_kill_edge  # noqa: E402

# THE PHASE LIST WAS TYPED OUT AND WENT STALE, which is the third instance of one defect in this
# project: r175 found a hardcoded tally beside a computed count in DEFECTS.py, r198 found a
# hardcoded threshold beside an imported one in its own commentary, and here a hardcoded round list
# beside a growing graph. Every one made a generated artefact quietly describe a smaller world than
# the one it sits in -- this ledger printed "3 withdrawn" while the graph held 15 refuted claims.
# Derived now: any experiment tagged rNNN counts, so the scope grows with the work.
_ROUND = __import__("re").compile(r"^r\d+")


def _in_phase(experiment: str) -> bool:
    return bool(_ROUND.match(experiment or ""))


def evidence_for(nid: int) -> list[tuple[str, str]]:
    return [(e, f) for e, f in
            q("SELECT experiment, coalesce(finding,'') FROM evidence WHERE node_id=%s "
              "ORDER BY experiment", (nid,))]


def killers_of(nid: int) -> list[tuple[str, str]]:
    return q("SELECT s.name, coalesce(e.note,'') FROM edge e JOIN node s ON s.id=e.src "
             "WHERE e.dst=%s AND e.kind IN ('overturns','refines') ORDER BY e.kind", (nid,))


def phase_nodes(kinds: tuple[str, ...]) -> list[tuple]:
    # the psql helper substitutes parameters as text and does not adapt Python lists into
    # Postgres arrays, so ANY(%s) arrives as a malformed array literal. Build the IN list from a
    # fixed tuple of kind names, which are ours and not user input.
    inlist = ", ".join("'" + k.replace("'", "''") + "'" for k in kinds)
    rows = q("SELECT id, kind, name, coalesce(statement,''), coalesce(status,''), "
             f"coalesce(props::text,'{{}}') FROM node WHERE kind IN ({inlist}) ORDER BY name")
    out = []
    for nid, kind, name, stmt, status, props in rows:
        ev = evidence_for(nid)
        if any(_in_phase(e) for e, _f in ev):
            out.append((nid, kind, name, stmt, status, props, ev))
    return out


def main() -> int:
    nodes = phase_nodes(("my_claim", "fact", "their_assumption"))
    dead = [n for n in nodes if n[4] == "refuted"]
    alive = [n for n in nodes if n[4] != "refuted"]

    rounds = sorted({m.group(0) for row in nodes for e, _f in row[-1]
                     if (m := _ROUND.match(e or ""))}, key=lambda r: int(r[1:]))
    span = f"{rounds[0]}-{rounds[-1]}" if rounds else "no rounds"
    print(f"NORMATIVE-CHAIN LEDGER  --  {len(nodes)} claims with evidence from {span}\n")

    print(f"=== WITHDRAWN ({len(dead)}) " + "=" * 40)
    for nid, _k, name, stmt, _s, _p, _ev in dead:
        print(f"\n  {name}")
        print(f"    {stmt[:300]}")
        for kname, note in killers_of(nid):
            print(f"    killed by: {kname}")
            if note:
                print(f"      {note[:200]}")

    print(f"\n\n=== STANDING ({len(alive)}) " + "=" * 41)
    for nid, _k, name, stmt, status, props, ev in sorted(alive, key=lambda r: r[4]):
        try:
            pr = json.loads(props) if isinstance(props, str) else (props or {})
        except ValueError:
            pr = {}
        print(f"\n  [{status}] {name}")
        print(f"    {stmt[:340]}")
        for kname, note in killers_of(nid):
            print(f"    narrowed by: {kname}")
        for k, v in pr.items():
            print(f"    {k}: {str(v)[:180]}")
        for e, _f in ev[:3]:
            print(f"    evidence: {e}")

    print("\n\n=== METHOD DEFECTS, AND WHAT CAUGHT EACH " + "=" * 24)
    for name, props in q("SELECT name, props::text FROM node WHERE kind='defect' ORDER BY name"):
        try:
            pr = json.loads(props) if props else {}
        except ValueError:
            pr = {}
        c = pr.get("caught_by")
        if c:
            print(f"  {name}")
            print(f"    caught by: {c}")
            if pr.get("affects"):
                print(f"    affects:   {pr['affects']}")

    # integrity, not a summary: does the graph obey its own rules?
    print("\n\n=== INTEGRITY " + "=" * 51)
    bad_status = q("SELECT kind, name, status FROM node WHERE status IS NOT NULL")
    bad = [(k, n, s) for k, n, s in bad_status if k in DOMAIN and s not in DOMAIN[k]]
    print(f"  statuses outside their kind's domain: {len(bad)}")
    orph = [(k, n) for k, n, s in bad_status if needs_kill_edge(k, s)
            and not q("SELECT 1 FROM edge WHERE dst=(SELECT id FROM node WHERE name=%s) "
                      "AND kind='overturns' LIMIT 1", (n,))]
    print(f"  refuted claims with no kill edge:     {len(orph)}")
    noev = [n for _i, _k, n, _s, _st, _p, ev in nodes if not ev]
    print(f"  claims in this phase with no evidence row: {len(noev)}")
    print(f"\n  ratio of withdrawn to standing: {len(dead)}/{len(alive)}")
    # COUNTED, NOT ASSERTED. This line first said "five", which was true when written and false
    # two commits later after two claims were restored and one un-retracted. A summary that states
    # a number the graph can compute is a summary that will eventually contradict it.
    print(f"  A phase with no retractions is a phase whose ontology has no word for error; "
          f"this one currently has {len(dead)} withdrawn, after restorations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
