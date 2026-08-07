"""R1049 — the currency gate passed a fact with nothing written. Is that one entry or the gate?

While committing R1048 the currency gate went GREEN with no annotation written at all: the fact's
patterns matched unrelated pre-existing text — a percentage in an old table beside the word `random`,
and `UNVERIFIED` beside a round id. That gate has certified every round in this window.

⭐ THE MUTATION IS THE TEST, AND IT IS THE SAME SHAPE R1043 USED ON THE ANCHORING GATE: delete the
   span a pattern matches, and ask whether the pattern still matches. If it does, the document holds
   a SECOND HOME for that pattern, and a PASS cannot be attributed to the annotation the fact is
   supposed to have written.

⛔ P6, WRITTEN BEFORE THE RUN, BECAUSE THIS PROXY IS SOUND IN ONE DIRECTION ONLY.
   PROPERTY   the gate's PASS is caused by the round's own annotation
   PROXY      the pattern matches in exactly one place
   IMPLICATION  >=2 homes  ==> the PASS is not attributable            [SOUND]
                 1 home    ==> the PASS is attributable                [NOT SOUND: the single home
                               may itself be unrelated text, which is precisely how R1048 failed
                               before its patterns were tightened]
   SAFE SIDE  rule only on multi-home. Single-home returns UNVERIFIED, never CLEAN.

ESTIMAND        the number of registered facts whose every pattern has >=2 disjoint homes in the
                statement region, i.e. whose gate PASS cannot be attributed to their own annotation
IDENTIFICATION  exact for the multi-home count. ⚠ Patterns built at runtime (f-strings, variables)
                cannot be read statically; they are COUNTED AND REPORTED as unreadable, never
                dropped, because a silent drop would shrink the denominator in the flattering
                direction.
SCOPE           population : every facts.append in the registry source
                instrument : static AST extraction + disjoint-span regex search
                baseline   : the gate's own PASS, which certified this window
                regime     : one document, one registry
WORLDS          A ONE LOOSE ENTRY — R1048's pair was unusual; nearly every other fact is single-home,
                  so the gate is sound and the fix already landed.
                B THE GATE IS PERMISSIVE BY CONSTRUCTION — a substantial share are multi-home, so
                  passing has never implied the annotation was written, and every round this window
                  certified is UNVERIFIED on currency rather than confirmed.
                prediction matrix: A -> multi-home share low  B -> high
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      multi-home share >= 0.30 -> World B
                      <= 0.10                  -> World A
                      otherwise                 -> report, claim neither
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   R1048's ORIGINAL loose patterns — the measured failure, quoted verbatim from the
                commit that fixed them — must be flagged multi-home. This is a control against a
                REAL case, not an invented one: §4's `validated against your imagination`.
NEGATIVE CTRL   a long literal lifted AT RUNTIME from the document must be single-home.
PLACEBO         a fact with no statically readable pattern contributes no denominator - reported
                separately, never scored as clean.
NOISE FLOOR     the share of RANDOM short patterns that are multi-home, measured over 3 seeds, is
                the floor the observed share must beat.
MULTIPLICITY    every fact reported with its home count, not only the flagged ones.
SEEDS           3 for the floor; spread reported.
IMPOSSIBLE      whether a SINGLE home is the round's own annotation or unrelated text that happens to
                match. SETTLES: IN-RELEASE - resolvable by reading the matched span against the
                round's README, one reading per fact; unattempted, not unavailable.
"""
import ast, json, pathlib, random, re, string

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REG = ROOT / "assurance/a_statement_is_current_with_the_arc.py"
DEF = ROOT / "E05_the_space_of_compilers/DEFINITION.md"


def homes(pat, text, cap=8):
    """disjoint match spans, found by deleting each match and re-searching — the mutation itself"""
    out, cur = 0, text
    for _ in range(cap):
        m = re.search(pat, cur, re.S)
        if not m:
            break
        out += 1
        cur = cur[:m.start()] + cur[m.end():]
    return out


def main() -> int:
    src, doc = REG.read_text(), DEF.read_text()
    facts, unreadable = [], 0
    for node in ast.walk(ast.parse(src)):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "append" and node.args
                and isinstance(node.args[0], ast.Tuple)):
            continue
        el = node.args[0].elts
        if len(el) < 4 or not isinstance(el[0], ast.Constant):
            continue
        if not isinstance(el[3], ast.List):
            unreadable += 1
            continue
        pats = [p.value for p in el[3].elts if isinstance(p, ast.Constant)]
        if len(pats) != len(el[3].elts):
            unreadable += 1
            continue
        facts.append((el[0].value, pats))

    if not facts:
        print("  UNRUNNABLE: no statically readable facts. Exit 2, never 0."); return 2

    # ---------- controls ----------
    POS = [r"(0\.965|97\.5|0\.975).{0,220}(random|coincidence)",
           r"(UNCLASSIFIED|UNVERIFIED).{0,240}(43|never exculpated)"]
    pos = all(homes(p, doc) >= 2 for p in POS)
    i = len(doc) // 2
    lit = re.escape(doc[i:i + 160])
    neg = homes(lit, doc) == 1
    print(f"  POSITIVE — R1048's ORIGINAL loose pair (a REAL measured failure, not an invented one) "
          f"must read multi-home: {pos}")
    print(f"  NEGATIVE — a 160-char literal lifted at runtime from the document must be single-home: "
          f"{neg}")
    if not (pos and neg):
        print("  the mutation does not discriminate. Exit 2, never 0."); return 2

    # ---------- measured floor: random short patterns ----------
    floors = []
    for seed in (5, 17, 31):
        rng = random.Random(seed)
        pats = ["".join(rng.choice(string.ascii_lowercase) for _ in range(3)) for _ in range(120)]
        floors.append(sum(homes(p, doc) >= 2 for p in pats) / len(pats))
    flo, fhi = min(floors), max(floors)

    rows, multi = [], []
    for rid, pats in facts:
        h = [homes(p, doc) for p in pats]
        vulnerable = bool(h) and all(x >= 2 for x in h)
        rows.append({"round": rid, "homes": h, "multi_home": vulnerable})
        if vulnerable:
            multi.append(rid)
    share = len(multi) / len(rows)

    print(f"\n  ⭐ {len(rows)} statically readable facts · MULTI-HOME (gate PASS not attributable to "
          f"the round's own annotation) {len(multi)} · share {share:.3f}")
    print(f"  ⚠ patterns not statically readable, reported not dropped: {unreadable}")
    print(f"  ⭐ MEASURED FLOOR — random 3-letter patterns that are multi-home, 3 seeds: "
          f"[{flo:.3f}, {fhi:.3f}]")
    print(f"  multi-home rounds: {multi[:14]}")

    resolved = share > fhi or share < flo
    print()
    if not resolved:
        world = (f"⛔ UNVERIFIED — the observed multi-home share {share:.3f} sits INSIDE the random "
                 f"floor [{flo:.3f}, {fhi:.3f}], so the mutation cannot separate a permissive gate "
                 f"from a document dense enough that any short pattern repeats.")
    elif share >= 0.30:
        world = (f"⭐ B THE GATE IS PERMISSIVE BY CONSTRUCTION — {share:.1%} of registered facts have "
                 f">=2 homes for EVERY pattern, so a PASS has never implied the annotation was "
                 f"written. Every round this window is UNVERIFIED on currency rather than confirmed, "
                 f"and R1048's entry was an instance, not an outlier.")
    elif share <= 0.10:
        world = (f"⭐ A ONE LOOSE ENTRY — {share:.1%} multi-home, below the {flo:.3f} floor, so "
                 f"R1048's pair was unusual and the gate's other {len(rows) - len(multi)} facts are "
                 f"not attributable-by-coincidence on this test.")
    else:
        world = (f"⭐ NEITHER BAND — multi-home {share:.3f} of {len(rows)}, floor "
                 f"[{flo:.3f}, {fhi:.3f}]. Reported; neither world claimed.")
    print(world)
    print(f"⛔ AND THE SOUND DIRECTION IS ONE-WAY, WRITTEN BEFORE THE RUN. >=2 homes means the PASS is")
    print(f"   NOT ATTRIBUTABLE. One home does NOT mean it is: the single home may itself be")
    print(f"   unrelated text, which is exactly how R1048 failed. Single-home facts are UNVERIFIED,")
    print(f"   never CLEAN, and folding UNVERIFIED into CLEAN manufactures a false acquittal.")

    # ⚠ POST-HOC AND LABELLED AS SUCH. The flagged list is visibly weighted to older rounds, so the
    #   split is computed rather than asserted — but it was NOT pre-registered, it is ONE test on a
    #   covariate chosen after seeing the list, and it is reported as an observation, never a finding.
    def n(r):
        return int(r[1:])
    old = [x for x in rows if n(x["round"]) < 1022]
    new = [x for x in rows if n(x["round"]) >= 1022]
    if old and new:
        so = sum(x["multi_home"] for x in old) / len(old)
        sn = sum(x["multi_home"] for x in new) / len(new)
        print(f"\n  ⚠ POST-HOC, NOT PRE-REGISTERED, ONE TEST ON A COVARIATE CHOSEN AFTER SEEING THE")
        print(f"     LIST — multi-home share before R1022: {so:.3f} ({len(old)} facts) · from R1022 "
              f"on: {sn:.3f} ({len(new)} facts).")
        print(f"     ⭐ This is an OBSERVATION, not a finding: with one post-hoc split there is no")
        print(f"     multiplicity control, and the direction was chosen by looking. What it licenses")
        print(f"     is a pre-registered test in a later round, nothing more.")

    out = HERE / "results" / "gate_coincidence.json"
    out.write_text(json.dumps({
        "round": "R1049", "facts_readable": len(rows), "patterns_unreadable": unreadable,
        "multi_home": len(multi), "multi_home_share": share, "multi_home_rounds": multi,
        "random_floor_3_seeds": [flo, fhi], "resolved_against_floor": bool(resolved),
        "controls": {"positive_R1048_original_pair": bool(pos), "negative_runtime_literal": bool(neg)},
        "post_hoc_era_split": {"before_R1022": [len(old), sum(x["multi_home"] for x in old)],
                               "from_R1022": [len(new), sum(x["multi_home"] for x in new)],
                               "status": "post-hoc, not pre-registered, licenses only a later test"},
        "detail": rows, "world": world,
        "proxy_ledger": {"property": "the PASS is caused by the round's own annotation",
                         "proxy": "the pattern matches in exactly one place",
                         "sound_direction": ">=2 homes => not attributable",
                         "unsound": "1 home => attributable", "safe_side": "single-home is UNVERIFIED"},
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
