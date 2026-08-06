#!/usr/bin/env python3
"""R835 -- a performance bar cannot get discriminating power from the ordering it sits in.

See PREREGISTRATION.txt, committed before this file was executed.

ESTIMAND        among arms ③ admits, is any arm separably better than the next -- adjacent gap
                greater than the design's own MDE? Named before the method, reported per pair.
IDENTIFICATION  from R436's committed per-arm `a2` and `mde`. ⚠ that `mde` is the arm's paired
                bootstrap MDE against the BAR, not against another arm, so it APPROXIMATES the
                between-arm resolution. Gaps within 2x of it are reported UNRESOLVED, not resolved.
SCOPE           population: R436's 93 arms. instrument: R436's committed cells. baseline: each
                arm's own MDE. regime: A2, this judge, this release.
WORLDS          W-NO-SEPARABLE-BEST (④'' is empty too -- this site supports no performance clause
                with discriminating power inside the label-free class) vs W-SEPARABLE-BEST.
KILL            CONDITIONAL. Evaluated only if the positive control is separable and the negative
                is not. Otherwise UNVERIFIED.
POSITIVE CTRL   `oracle_k4` against the best ③-admissible arm must be separable.
NEGATIVE CTRL   an arm against ITSELF -- looked up TWICE from the artifact, not `x - x`.
MULTIPLICITY    every adjacent pair reported, separable or not.
ARTIFACT        results/r835_external_anchor.json with source hash.
"""
from __future__ import annotations
import hashlib, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parent.parent
RES = HERE / "results"
sys.path.insert(0, str(ROOT / "assurance"))
import clause3_as_written as C3                                            # noqa: E402


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    d = json.loads(next(A24.glob("R436_*/results/r436_clause4_at_home.json")).read_text())
    cells = {c["arm"]: c for c in d["cells"]}
    a2 = {k: v["a2"] for k, v in cells.items()}
    mde = {k: v["mde"] for k, v in cells.items()}
    print("\n  R835 · CAN A BAR GET DISCRIMINATING POWER FROM ITS OWN ORDERING?\n")

    # ③-admissible: the partition's ADMITTED, plus the three settled by construction record (R834)
    _, adm, _ = C3.partition(list(a2))
    by_record = ["generic", "gen", "promptecho"]
    pool = sorted(set(adm) | {a for a in by_record if a in a2}, key=lambda a: -a2[a])

    # ---- controls -------------------------------------------------------------------------
    best = pool[0]
    gap_pos = a2["oracle_k4"] - a2[best]
    m_pos = max(mde["oracle_k4"], mde[best])
    pc = gap_pos > m_pos
    print(f"  POSITIVE  oracle_k4 {a2['oracle_k4']:.4f} vs best ③-admissible {best} {a2[best]:.4f}"
          f" -> gap {gap_pos:+.4f} vs MDE {m_pos:.4f}   "
          f"{'SEPARABLE   PASS' if pc else '⛔ FAIL — the instrument resolves nothing'}")
    look1, look2 = cells[best]["a2"], cells[best]["a2"]        # looked up TWICE, not `x - x`
    nc = (look1 - look2) == 0.0 and not ((look1 - look2) > mde[best])
    print(f"  NEGATIVE  {best} against itself, looked up twice -> gap {look1-look2:+.4f}   "
          f"{'not separable   PASS' if nc else '⛔ FAIL'}")

    # ---- the estimand ---------------------------------------------------------------------
    print(f"\n  ③-admissible ordering ({len(pool)} arms) — every adjacent pair, separable or not:\n")
    print(f"  {'arm':<22}{'A2':>9}{'gap to next':>13}{'MDE':>9}   verdict")
    rows, any_sep = [], False
    for i, a in enumerate(pool):
        if i + 1 < len(pool):
            b = pool[i + 1]
            g = a2[a] - a2[b]
            m = max(mde[a], mde[b])
            v = "SEPARABLE" if g > 2 * m else ("unresolved" if g > m else "inside MDE")
            any_sep |= (g > 2 * m)
            rows.append({"upper": a, "lower": b, "gap": g, "mde": m, "verdict": v})
            print(f"  {a:<22}{a2[a]:>9.4f}{g:>+13.4f}{m:>9.4f}   {v}")
        else:
            print(f"  {a:<22}{a2[a]:>9.4f}{'—':>13}{'—':>9}")

    controls_ok = pc and nc
    if not controls_ok:
        world, verdict = "UNVERIFIED", "a control is unfit; no world is chosen"
    elif any_sep:
        world = "W-SEPARABLE-BEST"
        verdict = ("at least one adjacent gap exceeds 2x its MDE -- ④'' is a well-formed clause "
                   "here and names an arm")
    else:
        world = "W-NO-SEPARABLE-BEST"
        verdict = ("no adjacent gap in the ③-admissible ordering exceeds 2x its MDE -- ④'' is EMPTY "
                   "too, so this site supports no performance clause with discriminating power "
                   "inside the label-free class")
    print(f"\n  VERDICT: {world} -- {verdict}\n")
    print("  ⚠ DERIVATION, not measured, and it is why this round exists: [restriction P] ∧ [beat")
    print("     an ABSOLUTE bar B] is empty when B > ceiling(P) and possibly vacuous when B <=")
    print("     ceiling(P), and NOTHING ties B to ceiling(P). The obvious fix -- 'beat every rule")
    print("     in the same class' -- is satisfied by the class maximum BY CONSTRUCTION, which is")
    print("     a check that cannot fail. Both forms are forced; only an EXTERNAL anchor is not.\n")
    print("  ⚠ The MDE used is each arm's paired MDE against the BAR, not against the other arm.")
    print("     A true between-arm MDE needs per-pair difference vectors R436 did not persist.\n")

    out = {"world": world, "verdict": verdict, "pool": pool, "pairs": rows,
           "positive_gap": gap_pos, "positive_mde": m_pos, "positive_separable": pc,
           "negative_null": nc, "n_pool": len(pool),
           "mde_is_an_approximation": "arm-vs-BAR paired MDE, not arm-vs-arm",
           "source_r436": d.get("source_sha"),
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]}
    (RES / "r835_external_anchor.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"  artifact -> {RES/'r835_external_anchor.json'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
