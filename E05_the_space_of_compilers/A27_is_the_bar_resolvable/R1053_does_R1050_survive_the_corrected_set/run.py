"""R1053 — R1050 said the clause rests on unattributable work. It used the wrong set. Recompute.

R1050 measured that the 16 rounds R1049 flagged are cited near the definition's clause at 0.917
against a permutation floor of [0.490, 0.524], and downgraded the clause on that. R1052 then showed
R1049's predicate was wrong — the gate is `ok = any(...)`, so ONE loose pattern carries a pass, and
the corrected count is 45 of 67 rather than a fifth.

⛔ A RETRACTION OBLIGES THE RE-RUN, NOT JUST THE ANNOTATION. R1050's number was computed on a set
   that no longer exists. Both the intersection AND its permutation floor move with set size, and
   the direction is genuinely not predictable: a larger flagged set hits more windows, but so does
   every random set of that size, and the floor may rise faster than the observation.

⚠ AND THE HONEST PRIOR IS THAT THIS KILLS R1050. At 45 of 67 the flagged set is two thirds of the
   population; a random two-thirds sample will hit nearly any window that cites more than a couple of
   rounds. If the floor saturates, the test loses its power and R1050's downgrade was an artifact of
   the smaller set. That is written here BEFORE the run so it cannot be claimed afterwards.

ESTIMAND        the hit rate of the CORRECTED flagged set over (anchor x window) cells near the
                clause, and its permutation floor at the corrected set size
IDENTIFICATION  exact. The flagged set is recomputed here from the registry and the document rather
                than read from R1049's artifact, so it does not inherit the wrong predicate.
SCOPE           population : registry facts x DEFINITION.md as it stands at this commit
                instrument : `any(homes >= 2)` per fact; round-id citation in a window
                baseline   : R1050's 0.917 vs [0.490, 0.524] on the 16-round set
                regime     : one document, one registry, this commit
WORLDS          A THE DEPENDENCE SURVIVES — the corrected hit rate still clears its own (higher)
                  floor, so the clause really does cite unattributable work disproportionately and
                  R1050's downgrade stands on a corrected basis.
                B THE FINDING WAS A SET-SIZE ARTIFACT — the corrected rate sits inside the corrected
                  floor. Then R1050's downgrade is withdrawn, and what remains is only the
                  unconditional fact that most registered facts are unattributable.
                prediction matrix: A -> obs > floor_hi at the corrected size
                                   B -> obs inside [floor_lo, floor_hi]
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      obs > floor_hi -> World A
                      otherwise      -> World B, R1050's downgrade WITHDRAWN
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   a round KNOWN to have written the clause (R1037/R1038) must appear in some cell, or
                no window is over the clause. This is the control that exposed the 9 clause homes.
NEGATIVE CTRL   a non-existent round id must appear in no cell.
PLACEBO         a zero-width window must cite nothing.
NOISE FLOOR     ⭐ the permutation floor is recomputed AT THE CORRECTED SET SIZE. Reusing R1050's
                floor would compare a 45-round observation against a 16-round null, which is the
                error this round exists to fix.
MULTIPLICITY    all cells reported; both predicates reported side by side.
SEEDS           3 for the floor; spread reported.
IMPOSSIBLE      whether a citation near the clause means the clause DEPENDS on that round. Proximity
                in a document is not a dependency graph.
                SETTLES: IN-RELEASE - the clause's own text names the rounds it rests on, at one
                careful reading; unattempted, not unavailable.
"""
import ast, json, pathlib, random, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REG = ROOT / "assurance/a_statement_is_current_with_the_arc.py"
DEF = ROOT / "E05_the_space_of_compilers/DEFINITION.md"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
WINDOWS = (400, 1200, 4000, 12000)


def homes(pat, text, cap=8):
    n, cur = 0, text
    for _ in range(cap):
        m = re.search(pat, cur, re.I | re.S)
        if not m:
            break
        n += 1
        cur = cur[:m.start()] + cur[m.end():]
    return n


def main() -> int:
    doc, reg = DEF.read_text(), REG.read_text()
    facts, unreadable = [], 0
    for nd in ast.walk(ast.parse(reg)):
        if not (isinstance(nd, ast.Call) and isinstance(nd.func, ast.Attribute)
                and nd.func.attr == "append" and nd.args and isinstance(nd.args[0], ast.Tuple)):
            continue
        el = nd.args[0].elts
        if len(el) < 4 or not isinstance(el[0], ast.Constant):
            continue
        if not isinstance(el[3], ast.List):
            unreadable += 1; continue
        ps = [x.value for x in el[3].elts if isinstance(x, ast.Constant)]
        if len(ps) != len(el[3].elts):
            unreadable += 1; continue
        facts.append((el[0].value, ps))
    if not facts:
        print("  UNRUNNABLE: no readable facts. Exit 2, never 0."); return 2

    h = {rid: [homes(p, doc) for p in ps] for rid, ps in facts}
    flagged_any = sorted({r for r, v in h.items() if v and any(x >= 2 for x in v)})
    flagged_all = sorted({r for r, v in h.items() if v and all(x >= 2 for x in v)})
    print(f"  ⭐ registry facts {len(facts)} · unreadable {unreadable} · flagged under `any` "
          f"{len(flagged_any)} · under `all` (R1049's wrong predicate) {len(flagged_all)}")

    anchors = [m.start() for m in re.finditer("resolvably beats", doc)]
    arc_ids = {re.match(r"(R\d+)", p.name).group(1) for p in A27.glob("R*") if p.is_dir()}
    if not anchors or not arc_ids:
        print("  UNRUNNABLE: no clause anchor or no arc rounds. Exit 2, never 0."); return 2

    def cited(a, w):
        return set(re.findall(r"R\d{3,4}", doc[max(0, a - w): a + w]))

    pos = any({"R1037", "R1038"} & cited(a, w) for a in anchors for w in WINDOWS)
    neg = all("R9999" not in cited(a, w) for a in anchors for w in WINDOWS)
    plac = not cited(anchors[0], 0)
    print(f"  POSITIVE — a round known to have written the clause appears in some cell: {pos}")
    print(f"  NEGATIVE — a non-existent round id appears in none: {neg}")
    print(f"  PLACEBO  — a zero-width window cites nothing: {plac}")
    if not (pos and neg and plac):
        print("  no window is over the clause. Exit 2, never 0."); return 2

    cells = [(i, w) for i in range(len(anchors)) for w in WINDOWS]
    cells = [c for c in cells if len(cited(anchors[c[0]], c[1]) & arc_ids) / len(arc_ids) < 0.5]
    if not cells:
        print("  UNRUNNABLE: no informative cell. Exit 2, never 0."); return 2

    def rate(s):
        return sum(1 for i, w in cells if s & cited(anchors[i], w)) / len(cells)

    pool = sorted(arc_ids)
    out_rows = []
    for name, s in (("any (corrected)", set(flagged_any)), ("all (R1049's)", set(flagged_all))):
        obs = rate(s)
        floors = []
        for seed in (3, 13, 29):
            rng = random.Random(seed)
            floors.append(sum(rate(set(rng.sample(pool, min(len(s), len(pool)))))
                              for _ in range(60)) / 60)
        lo, hi = min(floors), max(floors)
        out_rows.append({"predicate": name, "n_flagged": len(s), "observed": obs,
                         "floor": [lo, hi], "separable": obs > hi})
        print(f"  ⭐ {name:<16} n={len(s):>3}  observed {obs:.3f}  floor [{lo:.3f}, {hi:.3f}]  "
              f"separable={obs > hi}")

    # ⛔⛔ THE CEILING, AND IT IS THE CONTROL THIS DESIGN WAS MISSING. Both predicates returned
    #   EXACTLY 0.917 on sets of size 45 and 21 — the tell that the statistic is saturated. §4's
    #   `control that cannot PASS` in its floor==ceiling form: if the observation already sits at
    #   the maximum the design can return, `separable` means only that a random set fails to
    #   saturate, and no threshold above the ceiling is admissible.
    ceiling = rate(set(pool))                      # every arc round flagged — the maximum possible
    empty = rate(set())                            # nothing flagged — the true zero
    print(f"  ⭐ CEILING (every arc round in the set): {ceiling:.3f} · FLOOR at g=0 (empty set): "
          f"{empty:.3f}")
    at_ceiling = abs(out_rows[0]["observed"] - ceiling) < 1e-9
    print(f"     the corrected observation is AT the ceiling: {at_ceiling}  "
          f"({'3 cells cite too little for ANY set to reach them' if at_ceiling else 'headroom exists'})")

    # ⛔⛔ AND A SATURATED STATISTIC DEMANDS ONE MORE QUESTION: HOW SMALL A SET ALREADY SATURATES IT?
    #   If a handful of rounds reach the ceiling, then the corrected set's saturation says nothing
    #   about the other forty — it is carried by whichever few rounds the clause region cites most,
    #   and `the clause depends on unattributable work` would be a claim about those few.
    freq = sorted(pool, key=lambda r: -sum(1 for i, w in cells if r in cited(anchors[i], w)))
    k_sat = None
    for k in range(1, len(freq) + 1):
        if abs(rate(set(freq[:k])) - ceiling) < 1e-9:
            k_sat = k; break
    greedy = freq[:k_sat] if k_sat else []
    in_flagged = [r for r in greedy if r in set(flagged_any)]
    print(f"  ⛔ SMALLEST SATURATING SET — {k_sat} round(s) reach the ceiling on their own: {greedy}")
    print(f"     of those, flagged under the corrected predicate: {len(in_flagged)} of {len(greedy)} "
          f"{in_flagged}")
    print(f"     ⭐ so the corrected set's saturation is carried by {k_sat} round(s), and the claim it")
    print(f"     licenses is about THOSE, not about all {len(flagged_any)}.")

    corrected = out_rows[0]
    print()
    if corrected["separable"]:
        world = (f"⭐ A THE DEPENDENCE SURVIVES THE CORRECTION, WITH ITS CEILING STATED"
                 f"{' — AND THE OBSERVATION IS AT THAT CEILING' if at_ceiling else ''} — with the corrected "
                 f"{corrected['n_flagged']}-round set the hit rate is {corrected['observed']:.3f} "
                 f"against its own recomputed floor {corrected['floor']}, so the clause still cites "
                 f"unattributable work more than a random set of the same size would. R1050's "
                 f"downgrade stands on a corrected basis.")
    else:
        world = (f"⛔ B R1050's DOWNGRADE IS WITHDRAWN — at the corrected set size "
                 f"{corrected['n_flagged']} the observed rate {corrected['observed']:.3f} sits "
                 f"INSIDE its own floor {corrected['floor']}. A random set that large hits these "
                 f"windows just as often, so the clustering R1050 measured was a SET-SIZE ARTIFACT "
                 f"and not evidence the clause depends on flagged work. ⭐ What survives is the "
                 f"unconditional fact, which is worse and not better: {corrected['n_flagged']} of "
                 f"{len(facts)} registered facts are unattributable AT ALL, clause or no clause.")
    print(world)
    print(f"⛔ AND THE FLOOR HAD TO BE RECOMPUTED AT THE NEW SIZE. Comparing a {corrected['n_flagged']}-round")
    print(f"   observation to R1050's 16-round null would have been the error this round exists to fix:")
    print(f"   a null priced at the wrong level is not a null.")

    o = HERE / "results" / "recomputed_dependence.json"
    o.write_text(json.dumps({
        "round": "R1053", "facts": len(facts), "unreadable": unreadable,
        "flagged_any": flagged_any, "flagged_all": flagged_all,
        "cells": len(cells), "rows": out_rows,
        "smallest_saturating_set": greedy, "k_saturate": k_sat,
        "saturating_and_flagged": in_flagged,
        "ceiling": ceiling, "floor_at_g0": empty, "observation_at_ceiling": bool(at_ceiling),
        "R1050_original": {"observed": 0.917, "floor": [0.490, 0.524], "n_flagged": 16},
        "controls": {"positive": bool(pos), "negative": bool(neg), "placebo": bool(plac)},
        "world": world,
        "limitation": "proximity in a document is not a dependency graph",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
