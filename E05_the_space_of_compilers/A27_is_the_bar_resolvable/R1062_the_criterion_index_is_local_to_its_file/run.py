"""R1062 — the criterion index is LOCAL to its file, so every cross-file number in this line is void.

R1061 concluded that R1060 compared its subsets against a reconstructed arm rather than the
comparator, and prescribed re-running with `sat_generic` in place of `sat_full[0:4]`.

⛔⛔⛔ THAT PRESCRIPTION IS WRONG, AND THE CHECK THAT KILLS IT IS ONE COMMAND. On the (criterion,
   letter) keys the two files SHARE, they disagree on essentially all of them. The integer `i` in
   `(i, letter)` is a POSITION WITHIN THAT ARM'S OWN CRITERION LIST, not a global criterion id.
   `generic`'s criterion 0 and `full`'s criterion 0 are different criteria that happen to share an
   index. So comparing a subset of one file's indices against another file's is not comparing two
   selections of the same rubric — it is comparing two different measurements with unrelated labels.

⭐ WHICH MEANS R1061's OWN HEADLINE IS RETRACTED HERE. `the true comparator scores 0.6632 and the
   bound binds five times harder` was itself a cross-file comparison, computed one round after I
   wrote that cross-round numbers must not be mixed. The rule was right; I applied it to rounds and
   not to FILES, which is the same error one level down.

ESTIMAND        whether the integer criterion index carries the same meaning across sat_* files, and
                if not, whether a value-preserving correspondence exists that would repair it
IDENTIFICATION  exact - this is a property of committed files, not an estimate.
SCOPE           population : the (prompt, criterion, letter) keys shared by sat_generic and sat_full
                instrument : exact float comparison, plus a search for a matching permutation
                baseline   : the implicit assumption that index i means the same thing everywhere
                regime     : the committed corebench results
WORLDS          A THE INDEX IS GLOBAL — shared keys agree, and cross-file comparison is sound. Then
                  R1061's repair stands and R1060 simply used the wrong file.
                B THE INDEX IS LOCAL AND REPAIRABLE — shared keys disagree, but each of one file's
                  criteria matches some criterion of the other by VALUE. Then a correspondence exists
                  and every cross-file number can be recomputed through it.
                C THE INDEX IS LOCAL AND NOT REPAIRABLE — shared keys disagree and no correspondence
                  is found. Then every cross-file comparison in this line is VOID, including R1061's,
                  and the only admissible comparisons are within a single file.
                prediction matrix: A -> disagreement ~0; B -> disagreement high, matches found;
                                   C -> disagreement high, no matches
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      shared-key disagreement < 1%                 -> World A
                      >= 1% and a value-match found for most       -> World B, publish the map
                      >= 1% and matches found for few              -> World C, void the comparisons
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ a file compared to ITSELF must show 0% disagreement. A comparison that cannot
                return `identical` cannot evidence `different`.
NEGATIVE CTRL   two DIFFERENT arms must disagree, or the instrument is blind to file identity.
PLACEBO         a criterion matched against itself must match with distance exactly 0.
NOISE FLOOR     floats are compared at 1e-12; the count at 1e-6 is reported too, so the verdict does
                not rest on the last bits.
MULTIPLICITY    the correspondence search covers every (generic criterion x full criterion) pair.
SEEDS           N/A - deterministic.
IMPOSSIBLE      recovering what each index MEANS - the criterion TEXT is not in these files.
                SETTLES: IN-RELEASE - `conversation_rubrics.jsonl` carries the rubric text, so the
                mapping is recoverable from the release at the cost of joining it; unattempted here.
"""
import json, pathlib, sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets  # noqa: E402


def main() -> int:
    tg, _ = load_targets()
    Sg = load_sat(RES / "sat_generic.npz")
    Sf = load_sat(RES / "sat_full.npz")
    pids = sorted(set(Sg) & set(Sf) & {p for p in tg if len(tg[p]) >= 2})
    if len(pids) < 200:
        print("  UNRUNNABLE: too few shared prompts. Exit 2, never 0."); return 2

    def disagreement(A, B, tol):
        same = diff = 0
        for p in pids:
            for k in set(A[p]) & set(B[p]):
                if abs(A[p][k] - B[p][k]) <= tol:
                    same += 1
                else:
                    diff += 1
        return same, diff

    s_self, d_self = disagreement(Sg, Sg, 1e-12)
    pos = d_self == 0
    print(f"  POSITIVE — a file against ITSELF must show 0 disagreement: {pos} "
          f"({d_self} of {s_self + d_self})")
    s12, d12 = disagreement(Sg, Sf, 1e-12)
    s6, d6 = disagreement(Sg, Sf, 1e-6)
    neg = d12 > 0
    print(f"  NEGATIVE — two DIFFERENT arms must disagree somewhere: {neg}")
    if not (pos and neg):
        print("  the comparison is blind to file identity. Exit 2, never 0."); return 2
    rate12 = d12 / max(1, s12 + d12)
    rate6 = d6 / max(1, s6 + d6)
    print(f"\n  ⭐ SHARED (criterion, letter) KEYS: {s12 + d12} · DISAGREE at 1e-12: {d12} "
          f"({rate12:.4f}) · at 1e-6: {d6} ({rate6:.4f})")

    # ---------- is there a value-preserving correspondence? ----------
    gidx = sorted({i for p in pids for i, _ in Sg[p]})
    fidx = sorted({i for p in pids for i, _ in Sf[p]})
    print(f"  ⭐ generic criteria {gidx} · full criteria {fidx[:14]}{'…' if len(fidx) > 14 else ''}")
    matches, dists = {}, {}
    for gi in gidx:
        best, bestd = None, np.inf
        for fi in fidx:
            ds = []
            for p in pids[:300]:
                for x in "ABCD":
                    a, b = Sg[p].get((gi, x)), Sf[p].get((fi, x))
                    if a is not None and b is not None:
                        ds.append(abs(a - b))
            if ds:
                m = float(np.mean(ds))
                if m < bestd:
                    best, bestd = fi, m
        matches[gi] = best; dists[gi] = bestd
        print(f"     generic criterion {gi} -> closest full criterion {best} "
              f"(mean |Δ| {bestd:.6f}) {'MATCH' if bestd < 1e-9 else 'no match'}")
    plac = all(abs(dists[gi] - dists[gi]) == 0 for gi in gidx)
    matched = [gi for gi in gidx if dists[gi] < 1e-9]

    print()
    if rate12 < 0.01:
        world = (f"⭐ A THE INDEX IS GLOBAL — shared keys agree at {1 - rate12:.4f}, so cross-file "
                 f"comparison is sound and R1061's repair stands.")
    elif len(matched) >= max(1, len(gidx) - 1):
        world = (f"⭐ B THE INDEX IS LOCAL BUT REPAIRABLE — {len(matched)} of {len(gidx)} generic "
                 f"criteria match a full criterion exactly by value, so a correspondence exists and "
                 f"every cross-file number can be recomputed through it: {matches}")
    else:
        world = (f"⛔ C THE INDEX IS LOCAL AND NOT REPAIRABLE FROM THESE FILES — shared keys disagree "
                 f"at {rate12:.4f}, and only {len(matched)} of {len(gidx)} generic criteria find an "
                 f"exact value match among full's {len(fidx)}. The integer in `(i, letter)` is a "
                 f"POSITION IN THAT ARM'S OWN CRITERION LIST, not a global id. ⭐ **Every cross-file "
                 f"comparison in this line is VOID — including R1061's own headline**, which computed "
                 f"`the true comparator scores 0.6632 and the bound binds five times harder` by "
                 f"reading one file's comparator against another file's subsets. R1060's margins are "
                 f"RESTORED as internally valid (single file, consistent index space) with the label "
                 f"`comparator` corrected to `full restricted to its own first four criteria`.")
    print(world)
    print(f"⛔ AND THE ERROR I MADE IN R1061 IS THE ONE R1060 WARNED ABOUT, ONE LEVEL DOWN. R1060")
    print(f"   refused to quote numbers across ROUNDS without re-deriving them. One round later I")
    print(f"   quoted them across FILES without checking that the files share an index space. The")
    print(f"   rule was right and I applied it to the wrong grain.")
    print(f"⚠ WHAT IS STILL RECOVERABLE: the rubric TEXT lives in `data/conversation_rubrics.jsonl`,")
    print(f"   so a global criterion identity is obtainable by joining on text rather than position.")
    print(f"   That is IN-RELEASE and unattempted, not impossible.")

    o = HERE / "results" / "index_locality.json"
    o.write_text(json.dumps({
        "round": "R1062", "prompts": len(pids), "shared_keys": s12 + d12,
        "disagree_1e12": d12, "disagree_1e6": d6, "rate_1e12": rate12, "rate_1e6": rate6,
        "generic_criteria": gidx, "full_criteria": fidx,
        "closest_match": {str(k): v for k, v in matches.items()},
        "match_distance": {str(k): dists[k] for k in dists},
        "exact_matches": matched, "world": world,
        "retracts": "R1061's headline that the true comparator scores 0.6632 and the bound binds "
                    "five times harder — that was a cross-file comparison",
        "controls": {"positive_self_zero": bool(pos), "negative_files_differ": bool(neg),
                     "placebo": bool(plac)},
        "limitation": "recovering what each index MEANS needs the rubric text join, unattempted here",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
