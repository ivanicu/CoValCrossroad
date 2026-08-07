"""R1054 — proximity saturated. Change the unit from WINDOW to SENTENCE and read what the clause cites.

R1053 showed the window statistic is at its ceiling: 3 of 36 cells are unreachable, every set from 21
to 109 rounds returns 0.917, and 11 rounds saturate it of which only 5 are flagged. A saturated
statistic supports a direction and never a magnitude.

⭐ THE FIX IS NOT A BETTER THRESHOLD, IT IS A SMALLER UNIT. A 12,000-character window around a clause
   catches every round the document mentions nearby; a SENTENCE containing both a clause component and
   a round id is an ASSERTION that the component rests on that round. §4's remedy, applied for once
   before the fact rather than after: the instrument's unit and the claim's unit must be the same, and
   the claim's unit here is `the clause rests on round X`, which is a sentence-level relation.

ESTIMAND        the set of rounds cited in the SAME SENTENCE as a clause component, and how many of
                them are unattributable under the corrected `any` predicate
IDENTIFICATION  ⚠ PARTIAL AND NAMED BEFORE THE RUN. A sentence citing a round asserts a relation; it
                does not prove the clause could not be stated without it. So this yields the
                DECLARED dependency set, an upper bound on what is cited and NOT a proof of
                necessity. Necessity would need the clause restated without each round.
SCOPE           population : sentences of DEFINITION.md containing a clause component term
                instrument : sentence segmentation + round-id containment
                baseline   : R1053's window result, ceiling-saturated at 0.917
                regime     : this document, this commit
WORLDS          A THE CLAUSE DECLARES ITS SOURCES — the sentence unit yields a small, specific set,
                  well below the ceiling, so the dependency is nameable and the flagged share of it
                  is a real number rather than a saturated one.
                B THE SENTENCE UNIT SATURATES TOO — the set is most of the arc again, so the document
                  does not distinguish dependence from mention at ANY unit, and the honest position
                  is that the clause's provenance is not recoverable from its own text.
                prediction matrix: A -> |declared| well below the ceiling; B -> at it
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      |declared| < 0.5 * |arc rounds| -> World A, report the set and its flagged share
                      otherwise                        -> World B, provenance not recoverable
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ R1037 and R1038 wrote the clause's `q` into the statement and set its default. At
                least one must appear in a sentence containing a `q` term, or the segmentation is not
                over the clause. This is a KNOWN case from committed commit bodies, not an invented one.
NEGATIVE CTRL   a non-existent round id must appear in no sentence.
PLACEBO         a component term that appears nowhere contributes no sentences - reported, not scored.
CEILING         ⭐ MEASURED, because R1053 was burned by not measuring one: the number of distinct
                rounds cited in ANY sentence of the document. The declared set cannot exceed it, and
                if it equals it the sentence unit has saturated exactly as the window did.
NOISE FLOOR     the flagged share of the declared set is compared against the flagged share of the
                WHOLE registry, which is the rate a set drawn without regard to the clause would show.
MULTIPLICITY    every component term reported with its own set, not only the union.
SEEDS           N/A - deterministic over committed text.
IMPOSSIBLE      whether a cited round is NECESSARY to the clause. SETTLES: IN-RELEASE - restate the
                clause without it and re-run the admission operator, one run per cited round;
                unattempted, not unavailable.
"""
import ast, json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEF = ROOT / "E05_the_space_of_compilers/DEFINITION.md"
REG = ROOT / "assurance/a_statement_is_current_with_the_arc.py"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
# the clause's components, named from its own canonical wording, before any counting
COMPONENTS = {
    "resolvable_beat": r"resolvably beats",
    "comparator_family": r"prompt-blind|comparator family|certified",
    "q_parameter": r"\bq\b ?=|declared q|q = 90|q=90",
    "no_human_labels": r"prompt-specific human label",
    "coverage_not_imputed": r"actually covers|imput",
}
RID = re.compile(r"R\d{3,4}")


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
    doc = DEF.read_text()
    # sentence segmentation: a period/question/exclamation followed by space, or a hard newline break
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n{2,}", doc) if s.strip()]
    if len(sents) < 50:
        print("  UNRUNNABLE: segmentation produced too few sentences. Exit 2, never 0."); return 2

    arc = {re.match(r"(R\d+)", p.name).group(1) for p in A27.glob("R*") if p.is_dir()}
    ceiling_set = {r for s in sents for r in RID.findall(s)} & arc
    if not ceiling_set:
        print("  UNRUNNABLE: no arc round cited in any sentence. Exit 2, never 0."); return 2

    per = {}
    for name, pat in COMPONENTS.items():
        hits = [s for s in sents if re.search(pat, s, re.I)]
        per[name] = {"sentences": len(hits),
                     "rounds": sorted({r for s in hits for r in RID.findall(s)} & arc)}
    declared = sorted({r for v in per.values() for r in v["rounds"]})

    qset = set(per["q_parameter"]["rounds"])
    pos = bool({"R1037", "R1038"} & qset)
    neg = all("R9999" not in s for s in sents)
    print(f"  POSITIVE — R1037/R1038 must appear in a sentence about q (known from their own commit "
          f"bodies): {pos}  q-sentences={per['q_parameter']['sentences']} rounds={sorted(qset)[:8]}")
    print(f"  NEGATIVE — a non-existent round id appears in no sentence: {neg}")
    if not (pos and neg):
        print("  the segmentation is not over the clause. Exit 2, never 0."); return 2

    # flagged set, recomputed here under the CORRECTED `any` predicate
    facts, unreadable = [], 0
    for nd in ast.walk(ast.parse(REG.read_text())):
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
    flagged = {r for r, ps in facts if any(homes(p, doc) >= 2 for p in ps)}
    registry_rate = len(flagged) / max(1, len({r for r, _ in facts}))

    print(f"\n  ⭐ sentences {len(sents)} · CEILING (distinct arc rounds cited in ANY sentence) "
          f"{len(ceiling_set)} of {len(arc)} · DECLARED (in a clause-component sentence) "
          f"{len(declared)}")
    for k, v in per.items():
        print(f"     {k:<22} sentences {v['sentences']:>3}  rounds {len(v['rounds']):>3}  "
              f"{v['rounds'][:7]}")
    dec_flag = sorted(set(declared) & flagged)
    dec_rate = len(dec_flag) / len(declared) if declared else 0.0
    print(f"\n  ⭐ declared set flagged under the corrected predicate: {len(dec_flag)} of "
          f"{len(declared)} = {dec_rate:.3f}")
    print(f"  ⭐ registry-wide flagged rate (the rate a clause-blind set would show): "
          f"{registry_rate:.3f}  ({len(flagged)} of {len({r for r, _ in facts})})")
    print(f"  ⚠ registry patterns not statically readable, reported not dropped: {unreadable}")

    # ⛔⛔ A NULL WITHOUT AN MDE IS SILENCE (§1). The declared rate and the registry rate are
    #   almost identical — but with 21 declared rounds the design cannot resolve a small difference,
    #   so the MDE must be stated before the equality is read as a finding.
    import math
    se = math.sqrt(max(1e-12, dec_rate * (1 - dec_rate) / max(1, len(declared))))
    mde = 1.96 * se
    diff = dec_rate - registry_rate
    resolvable = abs(diff) > mde
    print(f"\n  ⭐ ENRICHMENT TEST — declared {dec_rate:.3f} vs registry-wide {registry_rate:.3f} · "
          f"difference {diff:+.3f} · SE {se:.3f} · MDE (1.96 SE) {mde:.3f} · "
          f"resolvable={resolvable}")
    if not resolvable:
        print(f"     ⭐⭐ NO ENRICHMENT DETECTABLE, and the difference is {abs(diff) / mde:.2f} of the")
        print(f"     MDE. The clause's DECLARED dependencies are flagged at essentially the BASE RATE,")
        print(f"     so R1050's `the clause rests disproportionately on unattributable work` does NOT")
        print(f"     survive at the unit that matches its own claim. R1053 kept it as a direction on a")
        print(f"     saturated window statistic; the sentence unit does not saturate and shows nothing.")
        print(f"     ⚠ This is a NULL, not a proof of no enrichment: the design could not have seen a")
        print(f"     difference smaller than {mde:.3f}, and the whole registry is flagged at "
              f"{registry_rate:.3f}")
        print(f"     anyway, which is the finding that stands and is worse than the one withdrawn.")

    saturated = len(declared) >= len(ceiling_set)
    print()
    if saturated:
        world = (f"⛔ B THE SENTENCE UNIT SATURATES TOO — the declared set is {len(declared)}, equal "
                 f"to the ceiling {len(ceiling_set)}, so the document does not distinguish dependence "
                 f"from mention at this unit either and the clause's provenance is not recoverable "
                 f"from its own text.")
    elif len(declared) < 0.5 * len(arc):
        world = (f"⭐ A THE CLAUSE DECLARES ITS SOURCES — {len(declared)} rounds are cited in a "
                 f"sentence that also states a clause component, against a ceiling of "
                 f"{len(ceiling_set)} and an arc of {len(arc)}. That is a NAMEABLE dependency set, "
                 f"and {len(dec_flag)} of it ({dec_rate:.3f}) are unattributable on currency versus "
                 f"{registry_rate:.3f} registry-wide.")
    else:
        world = (f"⭐ NEITHER BAND — declared {len(declared)}, ceiling {len(ceiling_set)}, arc "
                 f"{len(arc)}. Reported; neither world claimed.")
    print(world)
    print(f"⛔ AND THIS IS THE DECLARED SET, NEVER THE NECESSARY ONE. A sentence citing a round")
    print(f"   asserts a relation; it does not show the clause would fail without it. Necessity needs")
    print(f"   the clause restated without each round and the admission operator re-run — one run per")
    print(f"   cited round, which this design does not do and does not pretend to.")

    o = HERE / "results" / "declared_dependencies.json"
    o.write_text(json.dumps({
        "round": "R1054", "sentences": len(sents), "arc_rounds": len(arc),
        "ceiling_cited_anywhere": sorted(ceiling_set), "declared": declared,
        "per_component": per, "declared_flagged": dec_flag, "declared_flagged_rate": dec_rate,
        "registry_flagged_rate": registry_rate, "unreadable_patterns": unreadable,
        "saturated": bool(saturated), "enrichment_diff": diff, "enrichment_mde": mde,
        "enrichment_resolvable": bool(resolvable),
        "controls": {"positive_q_authors_present": bool(pos), "negative_absent_id": bool(neg)},
        "world": world,
        "limitation": "declared, not necessary; necessity needs the clause restated without each "
                      "cited round and the admission operator re-run",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
