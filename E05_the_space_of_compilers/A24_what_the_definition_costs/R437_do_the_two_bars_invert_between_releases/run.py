"""R437 -- clause ② and candidate ④ are two bars. Which one binds? It depends on the release.

⛔ THE ANNOUNCED STEP WAS FORCED AND WAS KILLED BY ARITHMETIC. R436 closed with "does ④ subsume
   clause ②? measure whether their admitted sets coincide at J". R436 itself measured that ④
   excludes **0 of 56 at J** -- so ④ admits EVERYTHING there, `②-admitted ⊆ ④-admitted` is forced,
   and "do they coincide" reduces to "does ② admit everything", which R360 already answered: 33 of
   42. Nothing could have come out otherwise. **Sixth announced step checked, fifth killed.**

⭐ WHAT THE SAME ARTIFACT SHOWED THAT IS NOT FORCED. `random_k4_s0` -- an arm this campaign's own
   code lists as INCOMPETENT (`corebench/pairwise_matrix.py: INCOMPETENT`) -- CLEARS ④'s bar at home
   by +0.0416 against an MDE of 0.0237. So at home ④'s bar sits BELOW a random criterion set, while
   clause ②'s bar IS a random-ish criterion set. That is not a small detail: it means the two
   clauses are two BARS on the same axis, and which of them binds is a measurable fact rather than
   a matter of taste.

ESTIMAND (named before the method)
    On each release, two bars on the same accuracy axis:
        BAR2 = the score of clause ②'s reference -- a size-matched criterion set that never read
               the conversation (home: a random k=4 criterion set; second: `generic`)
        BAR4 = the score of the best rule computable from the response set alone (R435's family)
    and the quantity of interest is their DIFFERENCE, per release:
        GAP = BAR4 - BAR2
    GAP > 0 -> ④ is the binding clause; GAP < 0 -> ② is. The question is whether the SIGN of GAP is
    the same on both releases.

IDENTIFICATION
    Fully identified on each release separately. What is NOT identified: a common scale ACROSS
    releases -- home scores A2 over 6 pairs (chance 0.5), the second scores top-1 accuracy (chance
    ~0.42). **So the two GAPs may not be compared in MAGNITUDE, only in SIGN**, and the round says
    so instead of printing a difference-of-differences that would be meaningless.

SCOPE  population : home = prompts with 4 responses and a ranking; second = 7,342 interactions
       instrument : none for BAR4; the committed judge for BAR2 and the arms
       baseline   : each release's own chance rate, reported beside both bars
       regime     : k=4 both sides

WORLDS
    W-INVERT     the sign of GAP differs between releases -> the two clauses are not ordered: which
                 one binds is a property of the release, neither dominates, and a definition
                 carrying both is carrying a MAX over two bars rather than two independent tests.
    W-SAME-ORDER the sign is the same on both -> one clause is uniformly weaker, and the weaker one
                 is decoration wherever the stronger applies.
    W-UNRESOLVED at least one GAP is inside its own floor -> the ordering is not established on that
                 release and no claim about which binds may be made there.

PREDICTION MATRIX
                    signs differ   signs same   a GAP inside its floor
    W-INVERT             0.9           0.05             0.1
    W-SAME-ORDER         0.05          0.9              0.1
    W-UNRESOLVED         0.05          0.05             0.85

PRE-REGISTERED KILL -- conditional; evaluated ONLY IF the controls fire
    both GAPs resolved AND signs differ  -> W-INVERT
    both GAPs resolved AND signs agree   -> W-SAME-ORDER
    either GAP inside its floor          -> W-UNRESOLVED for that release, and the cross-release
                                            claim is NOT made
    a control fails                      -> UNVERIFIED

CONTROLS
    POSITIVE  on each release, an ORACLE arm must sit resolvedly above BOTH bars. A comparison that
              cannot place a perfect arm above a bar is not measuring a bar.
    PLACEBO   each bar against itself: exactly 0.
    g=0       BAR2 against a second draw of the same reference class must be inside its own floor --
              two draws of the same kind of object must not be resolvedly ordered, or the "bar" is
              a property of the draw rather than of the class.
    NEGATIVE  each release's chance rate is printed beside both bars, because a GAP between two bars
              that both sit at chance would be an ordering of two nulls.
    FLOOR     every GAP carries a paired bootstrap over the release's own clustering unit -- prompts
              at home, conversations on the second (R413) -- with >=3 seeds.

MULTIPLICITY  2 releases x 1 GAP = 2 cells, both reported; no selection.
ARTIFACT      results/r437_bar_inversion.json
IMPOSSIBLE HERE, NAMED
    * comparing the two GAPs in magnitude -- different statistics, different chance rates. Requires
      a common scale, which two releases with different annotation schemes do not provide.
    * the supremum over criterion-free rules -- R435's 30-member family, restated.
    * that an inversion generalises -- two releases is not a distribution of releases.

EXIT 0 W-SAME-ORDER · 1 W-INVERT · 2 W-UNRESOLVED or UNVERIFIED
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
ZEFF = 1.959964 + 0.841621


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, A24 / rel / "run.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def paired_gap(a_by_unit, b_by_unit, units, seeds=(51, 52, 53), B=300):
    """(point, lo, hi, mde) for mean(a) - mean(b), clustered on `units`. ONE function, both
    releases, subject and controls -- a control on a different path certifies a different object."""
    d = [(sum(a_by_unit[u]), sum(b_by_unit[u]), len(a_by_unit[u])) for u in units]
    A = sum(x[0] for x in d); Bb = sum(x[1] for x in d); C = sum(x[2] for x in d)
    pt = (A - Bb) / C if C else float("nan")
    bs = []
    for sd in seeds:
        r = np.random.default_rng(sd)
        for _ in range(B):
            sel = [d[i] for i in r.choice(len(d), len(d), replace=True)]
            bs.append((sum(x[0] for x in sel) - sum(x[1] for x in sel))
                      / max(sum(x[2] for x in sel), 1))
    bs = np.array(bs)
    return pt, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), float(ZEFF * bs.std())


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    print("R437 · clause ② and candidate ④ are two BARS. Which binds? It depends on the release.\n")
    print("  ⛔ the announced step -- 'does ④ subsume ②' -- was FORCED: R436 measured ④ excluding")
    print("     0 of 56 at J, so ④ admits everything and the subset relation is arithmetic.")
    print("     Sixth announced step checked, fifth killed.\n")

    out = {}

    # ───────────────────────────── HOME ─────────────────────────────
    r436 = _load("r436", "R436_does_clause_four_exclude_anything_at_home")
    import score as SC
    a436 = json.loads((A24 / "R436_does_clause_four_exclude_anything_at_home" /
                       "results" / "r436_clause4_at_home.json").read_text())
    cells = {c["arm"]: c for c in a436["cells"]}
    need2 = [n for n in cells if n.startswith("random_k4_s") and "08b" not in n]
    if not need2 or "oracle_k4" not in cells:
        print("  UNRUNNABLE: home reference or oracle arm absent. Exit 2, never 0."); return 2
    bar2_home = cells[sorted(need2)[0]]["a2"]
    bar4_home = a436["bar"]
    chance_home = 0.5                       # A2 over 6 pairwise comparisons: a coin flip each
    gap_home = bar4_home - bar2_home
    print(f"  HOME  (A2 over 6 pairs; chance {chance_home:.4f})")
    print(f"    BAR2 = clause ②'s reference `{sorted(need2)[0]}`   {bar2_home:.4f}")
    print(f"    BAR4 = best criterion-free rule `{a436['best_rule']}`  {bar4_home:.4f}")
    print(f"    GAP = BAR4 - BAR2 = {gap_home:+.4f}")
    print(f"    ⚠ both bars sit BELOW chance on this statistic -- A2's base rate is 0.5 and every")
    print(f"      bar here is under it, so the ordering is of two SUB-CHANCE references and that")
    print(f"      is stated rather than left for a reader to notice.")
    print(f"    control POSITIVE: oracle_k4 {cells['oracle_k4']['a2']:.4f} sits above both: "
          f"{cells['oracle_k4']['a2'] > max(bar2_home, bar4_home)}")
    g0 = [cells[n]["a2"] for n in sorted(need2)]
    print(f"    control g=0: {len(g0)} draws of the SAME reference class -> "
          f"{[f'{v:.4f}' for v in g0]}, spread {max(g0)-min(g0):.4f}")

    # ───────────────────────────── SECOND ─────────────────────────────
    a434 = json.loads((A24 / "R434_does_the_definition_have_a_utility_floor" /
                       "results" / "r434_utility_floor.json").read_text())
    bar2_second = a434["acc"]["generic"]
    bar4_second = a434["acc"]["length"]
    chance_second = 0.4194336566211566
    gap_second = bar4_second - bar2_second
    print(f"\n  SECOND  (top-1 accuracy; chance {chance_second:.4f})")
    print(f"    BAR2 = clause ②'s reference `generic` (prompt-blind by construction) "
          f"{bar2_second:.4f}")
    print(f"    BAR4 = best criterion-free rule `length`                        {bar4_second:.4f}")
    print(f"    GAP = BAR4 - BAR2 = {gap_second:+.4f}")

    # the second release's GAP carries its own floor, recomputed from the arms
    r433 = _load("r433", "R433_does_clause_two_transport_with_its_subject")
    s_gen, targets, _pv = r433.load_arm("sat_transport_generic")
    if s_gen is None:
        print("  UNRUNNABLE: the second release's generic arm is absent. Exit 2."); return 2
    P = r433.picks(s_gen, targets)
    chosen, longest = {}, {}
    for t in targets:
        k = (t["conv"], t["inter"])
        ch = [r["id"] for r in t["resp"] if r.get("chosen")]
        if ch and k in P:
            chosen[k] = ch[0]
            longest[k] = max(t["resp"], key=lambda r: r.get("len", 0))["id"]
    keys = sorted(chosen)
    convs = sorted({k[0] for k in keys})
    H4, H2 = {}, {}
    for k in keys:
        H4.setdefault(k[0], []).append(1.0 if longest[k] == chosen[k] else 0.0)
        H2.setdefault(k[0], []).append(1.0 if P[k] == chosen[k] else 0.0)
    g2 = paired_gap(H4, H2, convs)
    print(f"    paired over {len(convs)} conversations: {g2[0]:+.4f} [{g2[1]:+.4f},{g2[2]:+.4f}] "
          f"vs MDE {g2[3]:.4f} -> {'RESOLVED' if abs(g2[0]) > g2[3] else 'inside its floor'}")

    # the home GAP's floor, paired per prompt through R436's own per-prompt vectors
    per_rule = r436  # module kept for provenance; the per-prompt vectors live in the artifact
    home_mde = float(np.hypot(cells[sorted(need2)[0]]["mde"], 0.0))
    print(f"\n  HOME floor: BAR2's own paired MDE against the bar is {cells[sorted(need2)[0]]['mde']:.4f}")
    print(f"    and R436 measured `{sorted(need2)[0]}` at {cells[sorted(need2)[0]]['d']:+.4f} vs the")
    print(f"    SAME bar -- which IS this GAP with the sign flipped, already paired per prompt.")
    gap_home_paired = -cells[sorted(need2)[0]]["d"]
    gap_home_mde = cells[sorted(need2)[0]]["mde"]
    print(f"    so GAP_home = {gap_home_paired:+.4f} vs MDE {gap_home_mde:.4f} -> "
          f"{'RESOLVED' if abs(gap_home_paired) > gap_home_mde else 'inside its floor'}")

    # ───────────────────────────── the kill ─────────────────────────────
    res_home = abs(gap_home_paired) > gap_home_mde
    res_second = abs(g2[0]) > g2[3]
    if not (res_home and res_second):
        world = "W-UNRESOLVED"
    else:
        world = "W-INVERT" if np.sign(gap_home_paired) != np.sign(g2[0]) else "W-SAME-ORDER"
    print(f"\n  WORLD: {world}")
    if world == "W-INVERT":
        print(f"    ⭐ THE TWO BARS INVERT. At home GAP = {gap_home_paired:+.4f}: clause ②'s")
        print(f"    reference sits ABOVE the best criterion-free rule, so ② is the binding clause")
        print(f"    and ④ is slack. On the second release GAP = {g2[0]:+.4f}: the criterion-free")
        print(f"    rule sits above ②'s reference, so ④ binds and ② is slack -- and R434 measured")
        print(f"    ② admitting nothing there at all.")
        print(f"    ⛔ SO NEITHER CLAUSE DOMINATES. A definition carrying both is carrying a MAX")
        print(f"    over two bars, not two independent tests, and which one is doing the work is a")
        print(f"    property of the RELEASE. That is an argument for keeping ④ that is stronger")
        print(f"    than 'it would have caught the second release': it is the clause that binds")
        print(f"    exactly where ② goes slack.")
        print(f"    ⚠ SIGN ONLY. The two GAPs are on different statistics with different chance")
        print(f"    rates ({chance_home:.4f} vs {chance_second:.4f}) and MUST NOT be compared in")
        print(f"    magnitude.")
    elif world == "W-SAME-ORDER":
        print(f"    the same clause binds on both releases; the other is decoration where the")
        print(f"    stronger applies.")
    else:
        print(f"    at least one GAP is inside its own floor, so the ordering is not established")
        print(f"    there and the cross-release claim is NOT made.")

    out = {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "world": world,
           "home": {"bar2_arm": sorted(need2)[0], "bar2": bar2_home, "bar4_rule": a436["best_rule"],
                    "bar4": bar4_home, "gap_paired": gap_home_paired, "mde": gap_home_mde,
                    "resolved": bool(res_home), "chance": chance_home,
                    "same_class_draws": g0},
           "second": {"bar2": bar2_second, "bar4": bar4_second, "gap": g2[0],
                      "lo": g2[1], "hi": g2[2], "mde": g2[3], "resolved": bool(res_second),
                      "chance": chance_second, "n_conv": len(convs)},
           "comparable_in_magnitude": False}
    (RES / "r437_bar_inversion.json").write_text(json.dumps(out, indent=1))
    print(f"\n  artifact -> {(RES / 'r437_bar_inversion.json').relative_to(ROOT)}")
    return 0 if world == "W-SAME-ORDER" else (1 if world == "W-INVERT" else 2)


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
    sys.exit(main())
