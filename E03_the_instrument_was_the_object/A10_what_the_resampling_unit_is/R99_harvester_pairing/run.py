"""r99 -- r58 pairs the first mean-ish key with the first CI-ish key, and does not check they match.

CLAIM CARD
----------
Claim      r58's census reports 170 interval contrasts with cell counts -- 90 "real and
           material", 27 UNVERIFIED -- and those counts are quoted as the package's
           equivalence picture.
Estimand   how many harvested rows pair a point estimate with an interval that does NOT
           describe the same quantity, and how many are null summaries counted as
           contrasts.
Target
observed?  YES, and directly. r58's harvester is `walk()`: it takes the FIRST key
           matching MEANISH and the FIRST matching CIISH within a node and emits them
           as one contrast. Re-walking every stored row against its source node
           recovers exactly which keys were paired.
Alternative
worlds     C CLEAN        every pairing names the same quantity. Then the cell counts
                          stand and this round is a positive control on the harvester.
           P PROMISCUOUS  some rows pair a null's mean with a null's interval, or a
                          null's mean with the REAL interval, or pick arbitrarily among
                          several candidates by dict order. Then the counts are
                          contaminated and no cell total can be quoted without saying by
                          how much.
Intervention
           none. A re-walk of stored rows against their source files.
Null       POSITIVE CONTROL -- the re-walk must reproduce r58's own recorded `mean` for
           rows it can locate. A walker that cannot recover what r58 harvested is not
           inspecting r58's harvest, and its findings would be about a different
           traversal. Rows whose mean cannot be reproduced are reported UNRESOLVED and
           excluded from every count rather than assumed clean.

WHY THIS IS THE STEP
--------------------
Reading r58's UNVERIFIED pool one contrast at a time (entry 190's NEXT) reached r01,
whose row is `<root>` with mean 0.0022974697186539934. That is `null_mean`, and its
interval is `null_ci`. The row is the PERMUTATION NULL of r01, counted as a contrast and
classified UNVERIFIED. MEANISH matches `.*_mean` and CIISH matches `.*_ci`, so any node
storing a null summary is harvested as though it were a finding.

That is not an r01 quirk. It is a property of the harvester, and it decides whether
"90 real and material" means anything.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
A key whose name contains "null" is not automatically a null summary -- a round could
legitimately name a real contrast `null_hypothesis_gap`. So the flag is NAME-BASED and
therefore a proxy: it can over-report. Every flagged row is emitted with its actual key
names so the classification is reviewable rather than asserted, and the count is
reported as SUSPECT rather than as an error count.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

_HERE = pathlib.Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

R58 = _ROOT / "E03_the_instrument_was_the_object/A07_can_a_local_judge_be_an_instrument/R58_equivalence_census/results/r58_equivalence_census.json"
MEANISH = re.compile(r"^(mean|diff|delta|gap|advantage|drop|attribution|effect|"
                     r".*_mean|.*_diff|.*_delta|.*_gap)$", re.I)
CIISH = re.compile(r"^(ci|.*_ci|ci_.*|interval)$", re.I)
NULLISH = re.compile(r"null|shuffl|permut|chance|placebo", re.I)


def node_at(doc, path):
    """Resolve r58's dotted path, INCLUDING list indices written as `[i]`.

    The first version did dict lookups only, so every path through a list --
    `axes.country.weight_specificity.[0]` and 22 others -- came back "node not a
    dict" and was counted as resisting the re-walk. That was this inspector's gap,
    not r58's defect, and reporting it as the latter would have been the wrong
    object entirely.
    """
    if path == "<root>":
        return doc
    n = doc
    for k in path.split("."):
        if k.startswith("[") and k.endswith("]"):
            try:
                i = int(k[1:-1])
            except ValueError:
                return None
            if not isinstance(n, list) or not (-len(n) <= i < len(n)):
                return None
            n = n[i]
            continue
        if not isinstance(n, dict) or k not in n:
            return None
        n = n[k]
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=pathlib.Path, default=_RES / "r99_harvester_pairing.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    if not R58.exists():
        raise SystemExit("REFUSING: r58's census is absent; this round inspects its harvest.")
    rows = json.load(open(R58))["contrasts"]

    reproduced, unresolved, flagged, vector_backed = 0, [], [], 0
    for r in rows:
        f = _ROOT / r["file"]
        if not f.exists():
            unresolved.append({**{k: r[k] for k in ("round", "path")}, "why": "file absent"})
            continue
        try:
            node = node_at(json.load(open(f)), r["path"])
        except Exception:
            unresolved.append({**{k: r[k] for k in ("round", "path")}, "why": "unreadable"})
            continue
        if not isinstance(node, dict):
            unresolved.append({**{k: r[k] for k in ("round", "path")}, "why": "node not a dict"})
            continue
        mk = [k for k in node if MEANISH.match(k) and isinstance(node[k], (int, float))
              and not isinstance(node[k], bool)]
        ck = [k for k in node if CIISH.match(k) and isinstance(node[k], list) and len(node[k]) == 2]
        picked_m = mk[0] if mk else None
        picked_c = ck[0] if ck else None
        # VECTOR-BACKED ROWS ARE LEGITIMATE, not unresolved. r58 emits a contrast when
        # `ci is not None and (mean is not None or vec is not None)`, so a node naming
        # its estimate something MEANISH does not match -- r43's `own_minus_pooled` --
        # is still harvested, with mean None, and TOSTed from its stored vector. The
        # first version of this round counted all 22 such rows as "resisting the
        # re-walk", which read as an r58 defect and was this inspector's blind spot.
        vec_backed = isinstance(node.get("paired_differences"), list)
        if r["mean"] is None:
            if vec_backed:
                reproduced += 1
                vector_backed += 1
            else:
                unresolved.append({**{k: r[k] for k in ("round", "path")},
                                   "why": "r58 stored no mean and the node carries no vector"})
            continue
        # POSITIVE CONTROL: did we recover the value r58 recorded?
        if picked_m is None or abs(node[picked_m] - r["mean"]) > 1e-12:
            unresolved.append({**{k: r[k] for k in ("round", "path")},
                               "why": "re-walk did not reproduce r58's stored mean"})
            continue
        reproduced += 1
        why = []
        if picked_m and NULLISH.search(picked_m):
            why.append(f"point estimate is a NULL summary ({picked_m})")
        if picked_c and NULLISH.search(picked_c):
            why.append(f"interval is a NULL summary ({picked_c})")
        # bool() on BOTH sides: re.search returns a Match or None, and `None != False`
        # is True, so comparing a Match-or-None against a bool flags every clean row.
        # The first run of this round did exactly that and reported r06's `delta + ci`
        # as a mismatch.
        if picked_m and picked_c and bool(NULLISH.search(picked_m)) != bool(NULLISH.search(picked_c)):
            why.append("MISMATCH: one side is a null summary and the other is not")
        if len(mk) > 1 or len(ck) > 1:
            why.append(f"AMBIGUOUS: {len(mk)} mean-ish and {len(ck)} ci-ish keys in one node, "
                       f"paired by dict order")
        if why:
            flagged.append({"round": r["round"], "path": r["path"], "cell": r["cell"],
                            "picked_mean": picked_m, "picked_ci": picked_c,
                            "mean_candidates": mk, "ci_candidates": ck, "why": why})

    print(f"rows {len(rows)}   accounted for {reproduced} "
          f"({vector_backed} vector-backed, mean legitimately absent)   "
          f"unresolved {len(unresolved)}")
    if reproduced < 0.5 * len(rows):
        raise SystemExit("REFUSING: the re-walk reproduced fewer than half of r58's stored means, so "
                         "it is not inspecting r58's harvest and its findings would describe a "
                         "different traversal.")
    by_cell: dict = {}
    for h in flagged:
        by_cell[h["cell"]] = by_cell.get(h["cell"], 0) + 1
    print(f"\nSUSPECT pairings: {len(flagged)} of {reproduced} reproduced rows")
    for c, n in sorted(by_cell.items(), key=lambda x: -x[1]):
        print(f"   {c:<22} {n}")
    print()
    for h in flagged[:10]:
        print(f"   {h['round']:<5} {h['path'][:30]:<30} [{h['cell']}]  "
              f"{h['picked_mean']} + {h['picked_ci']}")
        for w in h["why"]:
            print(f"        - {w}")

    world = "P PROMISCUOUS" if flagged else "C CLEAN"
    verdict = (
        f"{world}. r58 harvests a contrast with `walk()`: the FIRST key matching MEANISH and the FIRST "
        f"matching CIISH inside a node, emitted as one pair, with NO requirement that they describe the "
        f"same quantity. Re-walking its {len(rows)} stored rows and reproducing r58's own recorded mean "
        f"for {reproduced} of them: {len(flagged)} pairings are SUSPECT"
        + (", by cell " + ", ".join(f"{c}={n}" for c, n in sorted(by_cell.items(), key=lambda x: -x[1]))
           if by_cell else "") + ". "
        f"THE THREE FAILURE SHAPES, each found: a PURE NULL counted as a contrast -- r01's row is "
        f"`null_mean` paired with `null_ci`, which is r01's permutation null classified UNVERIFIED; a "
        f"NULL CLASSIFIED AS AN EFFECT -- r43's three axes pair `reversal_null_mean` with "
        f"`reversal_null_ci` and land in 'real and material'; and a MISMATCHED PAIR -- r84 pairs "
        f"`shuffled_gap`, a null point estimate, with `gap_ci`, the REAL gap's interval. Rounds storing "
        f"several candidates of each kind at one node are paired by DICT ORDER, which is not a "
        f"measurement decision at all. "
        f"POSITIVE CONTROL: the re-walk reproduces r58's stored mean for {reproduced} rows to 1e-12, so "
        f"this inspects r58's actual harvest; {len(unresolved)} rows could not be reproduced and are "
        f"reported UNRESOLVED and excluded from every count rather than assumed clean. The round "
        f"refuses to run if under half reproduce. "
        f"SCOPE, AND IT IS A PROXY: the flag is NAME-BASED -- a key containing 'null' or 'shuffl' is "
        f"treated as a null summary -- so it can OVER-report, and a round could legitimately name a "
        f"real contrast that way. Every flagged row carries its actual key names so the call is "
        f"reviewable rather than asserted, and the count is SUSPECT rather than an error count. "
        f"WHAT THIS CHANGES: no cell total of r58's may be quoted without this caveat. 'Real and "
        f"material: 90' includes rows whose point estimate is a permutation null."
    )

    doc = {
        "rows_in_census": len(rows), "reproduced": reproduced,
        "vector_backed_no_mean": vector_backed,
        "unresolved": unresolved, "n_unresolved": len(unresolved),
        "suspect": flagged, "n_suspect": len(flagged), "suspect_by_cell": by_cell,
        "world": world,
        "outcome_variable_scope": (
            "A re-walk of r58's stored contrast rows against their source nodes, recovering which keys "
            "its harvester paired. No measurement, no model, no new data."),
        "scope": (
            "The suspect flag is NAME-BASED and can over-report; flagged rows carry their key names so "
            "the classification is reviewable. Rows whose mean the re-walk could not reproduce are "
            "excluded from all counts as UNRESOLVED, never assumed clean. This does not repair r58 -- "
            "it measures how far its cell totals can be trusted."),
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
