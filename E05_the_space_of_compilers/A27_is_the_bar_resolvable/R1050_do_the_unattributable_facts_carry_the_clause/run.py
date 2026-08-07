"""R1050 — six rounds of instrument audits. Did any of it reach the definition?

R1044-R1049 retracted a habit claim, an anchoring headline, a magnitude, a derivation test and a
quarter of the currency gate's passes. Every one was about an INSTRUMENT. None touched the object the
arc exists for.

⛔ THE CONSTITUTION'S PRODUCTION FLOOR IS EXPLICIT THAT THIS IS NOT A RESULT: *not-being-wrong is a
   constraint, never the objective; a round that leaves only a retraction is cost recovery, not
   production.* It also names the question a retraction-heavy stretch must answer rather than dodge —
   **which world models were eliminated, and what understanding now STANDS.**

⭐ SO THE DECISIVE QUESTION IS NOT "was the gate loose" BUT "does the looseness REACH THE CLAUSE".
   R1049 flagged facts whose gate PASS is unattributable. If any of them is cited by the definition's
   own canonical clause region, the DEFINITION is downgraded and six rounds bought a real correction.
   If none is, the definition is untouched and the six rounds cost exactly their compute — which is
   also a finding, and the one that says the audit was orthogonal to the object.

ESTIMAND        |flagged rounds cited inside the clause region| and |cited anywhere in DEFINITION.md|
IDENTIFICATION  exact. Both sets are committed text; the only judgement is where the clause region
                begins and ends, which is swept rather than chosen (G4).
SCOPE           population : R1049's flagged facts x DEFINITION.md
                instrument : round-id citation inside a window around the canonical clause
                baseline   : the flagged set's size
                regime     : one document, one arc
WORLDS          A THE AUDIT REACHED THE OBJECT — >=1 flagged round is cited in the clause region, so
                  the definition rests in part on an unattributable fact and must be downgraded.
                B THE AUDIT WAS ORTHOGONAL — no flagged round is cited there. The definition stands
                  as written, and six rounds produced instrument repair and no definitional content.
                  ⭐ B IS NOT THE COMFORTABLE OUTCOME: it says the audit did not touch the object,
                  which under the production floor is the more damning of the two.
                prediction matrix: A -> intersection non-empty  B -> empty at every window
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      intersection non-empty at ANY window -> World A, downgrade the clause
                      empty at EVERY window                -> World B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   a round KNOWN to be cited in the clause region must be found. R1037 wrote the stated
                form of q into the clause and R1038 set its default; at least one must appear, or the
                window is not over the clause at all.
NEGATIVE CTRL   a round id that does not exist in this arc must be found nowhere, at every window.
PLACEBO         a window of size 0 must return the empty set rather than everything.
NOISE FLOOR     ⭐ the citation DENSITY of the document is measured: the share of ALL arc round ids
                appearing in each window. If a window cites nearly every round, membership carries no
                information and the verdict is UNVERIFIED regardless of the intersection.
MULTIPLICITY    5 window sizes swept, all reported, not the one that fires.
SEEDS           N/A - deterministic over committed text.
IMPOSSIBLE      whether a clause is WRONG because a fact under it is unattributable. Unattributable
                means the gate cannot prove the annotation was written, not that the number is false.
                SETTLES: IN-RELEASE - re-running the flagged round's own run.py re-derives its value
                directly, at one run per round; unattempted, not unavailable.
"""
import json, pathlib, random, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEF = ROOT / "E05_the_space_of_compilers/DEFINITION.md"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
WINDOWS = (0, 400, 1200, 4000, 12000)


def main() -> int:
    g = sorted((A27.parent).glob("A27*/R1049_*/results/gate_coincidence.json"))
    if not g:
        print("  UNRUNNABLE: R1049's artifact missing. Exit 2, never 0."); return 2
    flagged = set(json.loads(g[0].read_text())["multi_home_rounds"])
    doc = DEF.read_text()
    if not flagged:
        print("  UNRUNNABLE: empty flagged set. Exit 2, never 0."); return 2

    # ⛔⛔ THE CANONICAL CLAUSE IS NOT LOCATABLE BY ITS OWN TEXT, AND THE POSITIVE CONTROL IS WHAT
    #   FOUND THAT. `resolvably beats` occurs NINE times in this document. Anchoring on the FIRST
    #   put the window ~47,000 chars from R1037/R1038, the rounds that wrote the clause's stated
    #   form, and the control failed — correctly. This is R1049's multi-home defect one level up,
    #   in the STATEMENT rather than in a gate's pattern. So the anchor is a SPECIFICATION AXIS
    #   (G4), swept over all occurrences, and the count of occurrences is itself reported.
    anchors = [m.start() for m in re.finditer("resolvably beats", doc)]
    if not anchors:
        print("  UNRUNNABLE: the canonical clause was not located. Exit 2, never 0."); return 2
    print(f"  ⛔ THE CLAUSE HAS {len(anchors)} HOMES IN ITS OWN DOCUMENT — anchor choice is therefore "
          f"a specification axis, not a detail.")

    arc_ids = {re.match(r"(R\d+)", p.name).group(1) for p in A27.glob("R*") if p.is_dir()}

    def cited_at(a, w):
        return set(re.findall(r"R\d{3,4}", doc[max(0, a - w): a + w]))

    rows = []
    for i, a in enumerate(anchors):
        for w in WINDOWS:
            c = cited_at(a, w) if w else set()
            rows.append({"anchor": i, "window": w, "cited": len(c),
                         "density_of_arc": round(len(c & arc_ids) / max(1, len(arc_ids)), 3),
                         "intersection": sorted(flagged & c)})

    pos = any({"R1037", "R1038"} & cited_at(a, w) for a in anchors for w in WINDOWS if w)
    neg = all("R9999" not in cited_at(a, w) for a in anchors for w in WINDOWS if w)
    plac = all(r["cited"] == 0 for r in rows if r["window"] == 0)
    print(f"  POSITIVE — a round KNOWN to have written the clause (R1037/R1038) must appear in some "
          f"(anchor, window) cell: {pos}")
    print(f"  NEGATIVE — a non-existent round id must appear in none: {neg}")
    print(f"  PLACEBO  — every zero-width window must cite nothing: {plac}")
    if not (pos and neg and plac):
        print("  no window is over the clause. Exit 2, never 0."); return 2

    cells = [r for r in rows if r["window"]]
    informative = [r for r in cells if r["density_of_arc"] < 0.5]
    hit_cells = [r for r in informative if r["intersection"]]
    hits = sorted({x for r in hit_cells for x in r["intersection"]})
    print(f"\n  ⭐ flagged by R1049: {len(flagged)} · arc round directories: {len(arc_ids)} · "
          f"cells {len(cells)} · informative (arc density < 0.5) {len(informative)} · "
          f"cells with a flagged citation {len(hit_cells)}")
    for r in informative[:10]:
        print(f"     anchor {r['anchor']} w{r['window']:>6} cited {r['cited']:>3} "
              f"density {r['density_of_arc']:.3f}  {r['intersection']}")

    # ⛔⛔ THE MISSING CONTROL, AND IT IS THE ONE MISSED IN SIX CONSECUTIVE ROUNDS. With 16 of 63
    #   facts flagged and a window citing dozens of ids, a non-empty intersection may be forced by
    #   BREADTH rather than by the clause resting on flagged work. So: permute WHICH rounds are
    #   flagged — same count, drawn from the arc's own round ids — and measure how often a random
    #   flagged set also hits. If the observed hit rate sits inside that null, World A is an
    #   artifact of window size and the verdict must be UNVERIFIED.
    obs = len(hit_cells) / max(1, len(informative))
    pool = sorted(arc_ids)
    nulls = []
    for seed in (3, 13, 29):
        rng = random.Random(seed)
        rates = []
        for _ in range(200):
            fake = set(rng.sample(pool, len(flagged)))
            rates.append(sum(1 for r in informative
                             if fake & cited_at(anchors[r["anchor"]], r["window"]))
                         / max(1, len(informative)))
        nulls.append(sum(rates) / len(rates))
    nlo, nhi = min(nulls), max(nulls)
    print(f"  ⭐ PERMUTATION FLOOR — a RANDOM set of {len(flagged)} arc rounds hits an informative "
          f"cell at rate [{nlo:.3f}, {nhi:.3f}] over 3 seeds; observed {obs:.3f}")
    separable = obs > nhi

    print()
    if not separable:
        world = (f"⛔ UNVERIFIED — the observed hit rate {obs:.3f} sits INSIDE the permutation floor "
                 f"[{nlo:.3f}, {nhi:.3f}]. Any set of {len(flagged)} arc rounds hits these windows "
                 f"about as often, so a non-empty intersection is forced by the BREADTH of the "
                 f"citation region and says nothing about whether the clause rests on flagged work. "
                 f"⭐ The intersection {hits} is still the correct list of rounds cited near the "
                 f"clause AND flagged — it simply cannot be read as evidence of dependence. Neither "
                 f"world is separable by this design, and the clause is NOT downgraded on it.")
    elif not informative:
        world = ("⛔ UNVERIFIED — every window cites at least half the arc, so membership carries no "
                 "information and neither world is separable.")
    elif hits:
        world = (f"⭐ A THE AUDIT REACHED THE OBJECT — {hits} are cited within the clause region in "
                 f"{len(hit_cells)} of {len(informative)} informative cells AND flagged by R1049 as "
                 f"unattributable on currency. The clause is DOWNGRADED to unverified-provenance, "
                 f"never overturned: the numbers may be right and the gate simply cannot show the "
                 f"statement carries them.")
    else:
        world = (f"⭐ B THE AUDIT WAS ORTHOGONAL — no flagged round is cited in any informative cell. "
                 f"⛔ AND THAT IS THE MORE DAMNING OUTCOME: six rounds repaired instruments the "
                 f"object does not depend on.")
    print(world)

    out = HERE / "results" / "audit_reached_the_object.json"
    out.write_text(json.dumps({
        "round": "R1050", "flagged": sorted(flagged), "arc_rounds": len(arc_ids),
        "clause_homes": len(anchors), "cells": rows, "intersection": hits, "informative_windows": len(informative),
        "permutation_floor_3_seeds": [nlo, nhi], "observed_hit_rate": obs,
        "separable_from_floor": bool(separable),
        "controls": {"positive_clause_author_present": bool(pos),
                     "negative_absent_id": bool(neg), "placebo_zero_window": bool(plac)},
        "world": world,
        "limitation": "unattributable means the gate cannot prove the annotation was written, never "
                      "that the number is false",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
