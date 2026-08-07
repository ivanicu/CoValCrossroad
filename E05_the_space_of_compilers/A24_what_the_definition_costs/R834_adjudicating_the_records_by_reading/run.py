#!/usr/bin/env python3
"""R834 -- adjudicate the eleven records by reading, then recompute R831's substantive picture.

See PREREGISTRATION.txt, committed before this ran. The adjudications live in adjudication.json,
each carrying the VERBATIM sentence it rests on so a later reader can overturn any single one
without re-running anything.

ESTIMAND        ① the ③-status of each of the 11 UNKNOWN arms, by record; ② the rank distribution
                of the substantive ③-admissible-by-record set. Both named before either was run.
IDENTIFICATION  identified where a record names the inputs. NO-RECORD and UNDECIDED are distinct
                statuses and neither is a guess.
SCOPE           population: R831's 93 arms. instrument: the introducing commit, READ. baseline:
                R831's committed ranks and its BASELINE regex, copied unchanged so the recomputed
                number is comparable to the one it replaces.
WORLDS          W-OVERTURNED (best substantive rank <= 8) · W-STRENGTHENED (set grew, best > 8) ·
                W-UNCHANGED (no UNKNOWN arm adjudicates to substantive-ADMITTED).
KILL            CONDITIONAL. Evaluated only if `coval_core` adjudicates EXCLUDED and every ADMITTED
                verdict carries a non-empty quote. Otherwise UNVERIFIED and R831 stands.
⚠ CONFOUND      I am reading my own commit messages. `coval_core`'s verdict comes from the RELEASE's
                dataset card via R475, not from anything I wrote -- that is the positive control.
ARTIFACT        results/r834_adjudicated.json with source hash.
"""
from __future__ import annotations
import hashlib, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parent.parent
RES = HERE / "results"
BASELINE = re.compile(r"(^random_|sham|^const|shuffle|^full)", re.I)       # unchanged from R831
sys.path.insert(0, str(ROOT / "assurance"))
import clause3_as_written as C3                                            # noqa: E402


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    adj = json.loads((HERE / "adjudication.json").read_text())
    adj = {k: v for k, v in adj.items() if not k.startswith("_")}
    print("\n  R834 · ADJUDICATING THE ELEVEN RECORDS BY READING\n")

    # ---- controls -------------------------------------------------------------------------
    pc = adj.get("coval_core", {}).get("status") == "EXCLUDED"
    print(f"  POSITIVE  `coval_core` (decided by the RELEASE's card via R475, not by me) -> "
          f"{adj.get('coval_core',{}).get('status')}   "
          f"{'PASS' if pc else '⛔ FAIL — reading toward comfort'}")
    quoted = [a for a, v in adj.items() if v["status"] in ("ADMITTED", "EXCLUDED")
              and v.get("quote", "").strip()]
    decided = [a for a, v in adj.items() if v["status"] in ("ADMITTED", "EXCLUDED")]
    qc = len(quoted) == len(decided)
    print(f"  QUOTES    every ADMITTED/EXCLUDED verdict carries a verbatim sentence: "
          f"{len(quoted)}/{len(decided)}   {'PASS' if qc else '⛔ FAIL'}")

    d = json.loads(next(A24.glob("R436_*/results/r436_clause4_at_home.json")).read_text())
    a2 = {c["arm"]: c["a2"] for c in d["cells"]}
    order = sorted(a2, key=lambda a: -a2[a])
    rank = {a: i + 1 for i, a in enumerate(order)}
    exc, adm, unk = C3.partition(list(a2))
    missing = sorted(set(unk) - set(adj))
    if missing:
        print(f"\n  ⛔ {len(missing)} UNKNOWN arm(s) have no adjudication: {missing}. Exit 2.")
        return 2

    by_status: dict = {}
    print(f"\n  {'arm':<20}{'rank':>6}{'A2':>9}   {'by record':<11} quote")
    for a in sorted(unk, key=lambda x: rank[x]):
        v = adj[a]
        by_status.setdefault(v["status"], []).append(a)
        print(f"  {a:<20}{rank[a]:>6}{a2[a]:>9.4f}   {v['status']:<11} {v['quote'][:56]}")

    # ---- the recomputation ----------------------------------------------------------------
    r831_subst = sorted(a for a in adm if not BASELINE.search(a))
    new_subst = sorted(a for a in by_status.get("ADMITTED", []) if not BASELINE.search(a))
    full = sorted(set(r831_subst) | set(new_subst), key=lambda a: rank[a])
    fams = sorted({re.split(r"_k\d|_0\d|_s\d", a)[0] for a in full})
    print(f"\n  R831's substantive ③-ADMITTED set: {len(r831_subst)} arm(s) — {r831_subst}")
    print(f"  added by record (substantive, non-sham): {len(new_subst)} — {new_subst}")
    print(f"\n  recomputed substantive ③-admissible-by-record set: "
          f"{len(full)} arms across {len(fams)} families {fams}")
    for a in full:
        print(f"     rank {rank[a]:>2}/93   A2 {a2[a]:.4f}   {a}")
    best = rank[full[0]] if full else None
    top8_excluded = sum(1 for a in order[:8] if a in exc)
    print(f"\n  best substantive rank: {best}/93     "
          f"top-8 arms that are ③-EXCLUDED label-readers: {top8_excluded}/8")

    if not (pc and qc):
        world, verdict = "UNVERIFIED", "a control is unfit; R831's picture stands as published"
    elif best is not None and best <= 8:
        world = "W-OVERTURNED"
        verdict = ("a substantive label-free arm reaches the top 8 -- the label-reader monopoly is "
                   "an artifact of ③'s name-prefix rule and R831's world must be withdrawn")
    elif len(full) > len(r831_subst):
        world = "W-STRENGTHENED"
        verdict = (f"the substantive set grows from {len(r831_subst)} arm(s) in 1 family to "
                   f"{len(full)} across {len(fams)}, and its best rank {best} is still below the "
                   f"top 8 -- W-SELF-DEFEATING rests on more evidence, not less")
    else:
        world, verdict = "W-UNCHANGED", "no UNKNOWN arm adjudicates to substantive-ADMITTED"
    print(f"\n  VERDICT: {world} -- {verdict}\n")

    out = {"world": world, "verdict": verdict, "adjudication": adj,
           "by_status": {k: sorted(v) for k, v in by_status.items()},
           "r831_substantive": r831_subst, "added_by_record": new_subst,
           "recomputed_substantive": full, "families": fams,
           "ranks": {a: rank[a] for a in full}, "best_rank": best,
           "top8_excluded": top8_excluded,
           "controls": {"positive_coval_core_excluded": pc, "every_verdict_quoted": qc},
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]}
    (RES / "r834_adjudicated.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"  artifact -> {RES/'r834_adjudicated.json'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
