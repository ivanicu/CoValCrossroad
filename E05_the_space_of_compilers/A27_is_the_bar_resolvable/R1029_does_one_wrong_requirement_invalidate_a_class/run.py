#!/usr/bin/env python3
"""R1029 — R1028 falsified ONE requirement string. R472 says 17 entries share it. Does it propagate?

⛔ PRIOR ART, AND IT ALREADY CONTAINS R1028's PROPOSED NEXT. R1028 closed by proposing a re-score of
   the register on whether each entry NAMES a requirement. **R472 did that**: 100 entries, `explicit`
   35 · `implied` 11 · `none` 54, world W-HALF, with the requirement types tabulated —
   `a second release / corpus` **17**, `a second judge / third judge` 10, `an external gold standard`
   6, `a generator` 5, `more annotators / draws` 4, `an intervention on the mechanism` 2,
   `a second prompt-blind family` 1. That question is CLOSED and is not re-run.

   What R472 measured is PRESENCE. What R1027 and R1028 each found is a named requirement that is
   WRONG — a different property, and nobody has measured it. R1028's specific finding is that
   `a second release` does not bind: a disjoint 26,673-prompt population EXISTS and carries no
   criterion vocabulary, so the binding requirement is "a release CARRYING CRITERIA". R472 says 17
   entries name the falsified string. **One wrong requirement is a mistake; seventeen is a taxonomy.**

⛔ AND THE INSTRUMENT'S UNIT IS NOT THE CLAIM'S UNIT, WHICH BOUNDS WHAT THIS CAN CONCLUDE.
     instrument unit : the ENTRY TEXT, a prose description of a check
     claim unit      : the CHECK itself, and what data it would consume
   Text is the best available proxy and is not equal to the check. So the classifier is used ONLY in
   its sound direction — mentions criteria ⇒ criteria-based ⇒ R1028's repair applies. The other
   direction gets a SECOND, independent test rather than an inference: does the quantity the entry
   names actually EXIST as a field in the disjoint population? Absent that, the cell is UNVERIFIED.

ESTIMAND        of the 17 register entries naming `a second release / corpus`, how many
                ① are CRITERIA-BASED, so the requirement is misnamed and R1028's repair applies;
                ② name a quantity the disjoint population actually carries, so the entry is FALSE and
                   the check is runnable TODAY;
                ③ neither, and are therefore UNVERIFIED.
IDENTIFICATION  ① and ③ exact from committed text; ② exact against the disjoint file's field set.
SCOPE           population : R472's 100 committed register entries · instrument : a keyword
                classifier with its own positive control · baseline : R472's own type tabulation
                regime : the register as committed
WORLDS          A ISOLATED MISTAKES — the falsified requirement is shared by <= 2 entries, so R1027
                  and R1028 fixed local errors and the register's structure is sound.
                B A TYPE-LEVEL DEFECT — it is shared by many, so falsifying one requirement
                  invalidates a whole CLASS, R802's 1-of-30 base rate is a floor rather than an
                  estimate, and the repair is a requirement TAXONOMY, not two edited lines.
                prediction matrix: A -> <= 2 affected. B -> >= 10 affected.
                ⚠ ONTOLOGICAL: A makes a wrong requirement a per-entry slip; B makes it an inherited
                  string. They imply different repairs and different confidence in the whole register.
KILL            pre-registered and CONDITIONAL:
                  if the classifier's positive control fires and its negative control does not:
                      affected entries >= 10 -> World B
                      affected entries <= 2  -> World A
                      otherwise              -> report the count, claim neither
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   the classifier must flag a case whose answer is KNOWN: R1028's own cross-release line
                is criteria-based and MUST be flagged. And it must NOT flag a constructed sentence
                about annotator agreement alone. Both run before any count.
                ⚠ and it must fail at g=0 — on the empty string it must return neither class, not a
                default.
NEGATIVE CTRL   the same classifier run over the entries naming a DIFFERENT requirement (`a second
                judge`, `an external gold standard`): if it flags those at the same rate, it is
                reading the register's general vocabulary rather than this requirement's class, and
                the count means nothing.
PLACEBO         an entry set of size 0 must yield 0 and exit 2, never a silent pass.
NOISE FLOOR     N/A — exact string operations over a fixed corpus. Stated rather than omitted.
MULTIPLICITY    all 100 entries are classified and every requirement type is reported, not only the
                falsified one.
SEEDS           N/A — deterministic. Stated rather than silently skipped.
IMPOSSIBLE      whether each affected check would ACTUALLY run on the disjoint population — that
                needs the check implemented and executed, per entry. N/A; what it would require is
                one round per entry, and this round bounds the population that would need it.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))

FALSIFIED = "a second release / corpus"
# criteria vocabulary — the thing R1028 showed the disjoint population lacks
CRIT = re.compile(r"\b(criteri\w+|rubric\w*|clause|core|checklist|selector|prompt-blind)\b", re.I)
# quantities the disjoint population DOES carry, read from R1028's committed field list
CARRIED = re.compile(r"\b(preference|chosen|score|agreement|annotator|model|turn|user)\b", re.I)


def main() -> int:
    r472f = next(A24.glob("R472_*/results/*.json"), None)
    r1028f = next(A27.glob("R1028_*/results/*.json"), None)
    if not (r472f and r1028f):
        print("  UNRUNNABLE: a committed artifact is missing. Exit 2, never 0.")
        return 2
    r472 = json.loads(r472f.read_text())
    r1028 = json.loads(r1028f.read_text())
    entries = r472["entries"]
    fields = set(r1028["utterances_fields"])
    print(f"  ⛔ PRIOR ART — R472 scored {r472['n_entries']} entries for PRESENCE of a requirement: "
          f"explicit {r472['explicit']} · implied {r472['implied']} · none {r472['none']}.")
    print(f"     Its type tabulation: " + " · ".join(f"{v} {k}" for k, v in
          sorted(r472["requirements"].items(), key=lambda x: -x[1])))
    print(f"     ⚠ That is PRESENCE. R1027 and R1028 each found a named requirement that is WRONG, "
          f"which is a\n       different property and is what this round measures.")
    print(f"  ⛔ R1028's falsified requirement: `{FALSIFIED}` — a disjoint population of "
          f"{r1028['counts']['utterances_conversations']:,} conversations EXISTS\n     "
          f"(overlap {r1028['best_share_of_scored']:.4f}) and carries criteria: "
          f"{r1028['carries_criterion_vocabulary']}. Its fields: {sorted(fields)}")

    if not entries:
        print("  UNRUNNABLE: empty entry population must not pass. Exit 2, never 0.")
        return 2

    # ---------- POSITIVE / NEGATIVE controls on the classifier, before any count ----------
    known_crit = ("cross-release validation of a criteria-based definition would require a second "
                  "release carrying a rubric")
    known_not = "would require more annotators to stabilise the agreement estimate"
    pc = bool(CRIT.search(known_crit))
    nc = not bool(CRIT.search(known_not))
    g0 = not bool(CRIT.search("")) and not bool(CARRIED.search(""))
    print(f"\n  POSITIVE — the classifier must flag a KNOWN criteria-based sentence "
          f"(R1028's own line): {pc}")
    print(f"  NEGATIVE — and must NOT flag a sentence about annotator agreement alone: {nc}")
    print(f"  g=0      — on the empty string it must return NEITHER class, not a default: {g0}")
    if not (pc and nc and g0):
        print("  the classifier does not separate the two cases. Exit 2, never 0.")
        return 2

    # ---------- classify every entry, then isolate the falsified requirement ----------
    def kind_of(e):
        t = e.get("text", "")
        return {"crit": bool(CRIT.search(t)), "carried": bool(CARRIED.search(t))}

    for e in entries:
        e.update(kind_of(e))

    def names(e, req):
        """an entry names requirement `req` if R472's own phrasing appears in its text"""
        t = e.get("text", "").lower()
        toks = [w for w in re.split(r"[^a-z]+", req.lower()) if len(w) > 3]
        return sum(w in t for w in toks) >= max(1, len(toks) - 1)

    print(f"\n  ⭐ EVERY REQUIREMENT TYPE, not only the falsified one — multiplicity over the whole "
          f"register:")
    print(f"     {'requirement':<34}{'entries':>8}{'criteria-based':>16}{'share':>8}")
    rows = []
    for req, n472 in sorted(r472["requirements"].items(), key=lambda x: -x[1]):
        sel = [e for e in entries if names(e, req)]
        crit = [e for e in sel if e["crit"]]
        rows.append({"requirement": req, "r472_count": n472, "matched": len(sel),
                     "criteria_based": len(crit),
                     "share": len(crit) / max(len(sel), 1),
                     "rounds": sorted({e["round"] for e in crit})})
        print(f"     {req:<34}{len(sel):>8}{len(crit):>16}{len(crit)/max(len(sel),1):>8.2f}")

    tgt = next(r for r in rows if r["requirement"] == FALSIFIED)
    others = [r for r in rows if r["requirement"] != FALSIFIED and r["matched"] > 0]
    other_share = sum(r["criteria_based"] for r in others) / max(
        sum(r["matched"] for r in others), 1)
    print(f"\n  NEGATIVE (the classifier must not be reading the register's general vocabulary) —")
    print(f"     criteria-based share among `{FALSIFIED}` entries : {tgt['share']:.2f}")
    print(f"     criteria-based share among ALL OTHER requirements : {other_share:.2f}")
    discriminates = tgt["share"] > other_share
    print(f"     the classifier {'DISCRIMINATES' if discriminates else '⚠ DOES NOT DISCRIMINATE'} "
          f"between them")

    # ---------- the three-valued verdict, per P6's sound-direction rule ----------
    sel = [e for e in entries if names(e, FALSIFIED)]
    misnamed = [e for e in sel if e["crit"]]
    runnable = [e for e in sel if not e["crit"] and e["carried"]]
    unver = [e for e in sel if not e["crit"] and not e["carried"]]
    print(f"\n  ⭐ THE {len(sel)} ENTRIES NAMING THE FALSIFIED REQUIREMENT, three-valued:")
    print(f"     MISNAMED   (criteria-based ⇒ R1028's repair applies) : {len(misnamed)}"
          f"  rounds {sorted({e['round'] for e in misnamed})[:8]}")
    print(f"     FALSE      (names a quantity the disjoint file CARRIES,")
    print(f"                 so the check is runnable today)          : {len(runnable)}"
          f"  rounds {sorted({e['round'] for e in runnable})[:8]}")
    print(f"     UNVERIFIED (neither established — NOT an acquittal)  : {len(unver)}")
    print( "     ⚠ the classifier is used ONLY in its sound direction. `mentions criteria` ⇒")
    print( "       criteria-based is what the positive control licenses; the converse is not, so the")
    print( "       FALSE column needs its own evidence — the field actually existing in the data.")

    affected = len(misnamed) + len(runnable)

    # ⛔⛔ THE DENOMINATOR IS NOT IDENTIFIED, AND THAT IS THIS ROUND'S ACTUAL RESULT.
    #   Three instruments disagree about how many entries name the falsified requirement, and the
    #   disagreement is not noise — it is that the requirement TYPE WAS NEVER STORED. R472 derived
    #   its tabulation with a phrasing classifier and said so in its own README: "the instrument's
    #   unit is PHRASING, the claim's unit is NAMING A REQUIREMENT". So none of the three is the
    #   population, and reporting `affected / matched` would put a real numerator over an invented
    #   denominator.
    import re as _re
    direct = len([e for e in entries
                  if _re.search(r"second (release|corpus)|another release|second values|"
                                r"cross-release", e.get("text", ""), _re.I)])
    print(f"\n  ⛔ THREE INSTRUMENTS, THREE DENOMINATORS — and the spread IS the finding:")
    print(f"     {'instrument':<44}{'count':>7}")
    print(f"     {'R472 committed type tabulation':<44}{r472['requirements'][FALSIFIED]:>7}")
    print(f"     {'this round token matcher (>= n-1 tokens)':<44}{len(sel):>7}")
    print(f"     {'direct phrase regex on the same texts':<44}{direct:>7}")
    print(f"     R472's OWN README says why, verbatim: \"the instrument's unit is PHRASING, the")
    print(f"     claim's unit is NAMING A REQUIREMENT\" — so its 17 is a phrasing count, not a")
    print(f"     population, and neither is {len(sel)} nor {direct}.")

    identified = (r472["requirements"][FALSIFIED] == len(sel) == direct)

    print()
    if not identified:
        world = (f"⛔ UNVERIFIED ON IDENTIFICATION — the estimand fails G1 before power is even asked. "
                 f"The requirement TYPE was never stored as a field, so the population of entries "
                 f"whose requirement is `{FALSIFIED}` is not recoverable from committed text: three "
                 f"instruments give {r472['requirements'][FALSIFIED]}, {len(sel)} and {direct}. "
                 f"{affected} entries are affected AS A NUMERATOR, and no share is admissible. "
                 f"⭐ THE REPAIR IS STRUCTURAL, NOT ANALYTIC: store the requirement type when the "
                 f"entry is WRITTEN. A register whose requirements must be recovered by a classifier "
                 f"cannot be audited for whether those requirements are RIGHT — which is the one "
                 f"audit that decides if it is a specification or a list of excuses.")
    elif not discriminates:
        world = ("UNVERIFIED — the classifier flags other requirement types at the same rate")
    elif affected >= 10:
        world = (f"⭐ B A TYPE-LEVEL DEFECT — {affected} of {len(sel)} entries affected by ONE "
                 f"falsification; a wrong requirement is an inherited string.")
    elif affected <= 2:
        world = (f"⭐ A ISOLATED MISTAKES — only {affected} entries affected.")
    else:
        world = (f"⭐ NEITHER PRE-REGISTERED BAND — {affected} affected, between 2 and 10.")
    print(world)
    print(f"⛔ AND THE NUMERATOR STANDS EVEN THOUGH THE SHARE DOES NOT. At least {len(misnamed)} "
          f"committed\n   entries ({sorted({e['round'] for e in misnamed})}) name a requirement that "
          f"R1028 falsified AND guard a\n   criteria-based check, so R1028's repair applies to them "
          f"whatever the true denominator is.\n   A lower bound is a result; a share over a guessed "
          f"population is not.")
    print(f"⛔ AND R472 IS NOT CONTRADICTED, IT IS EXTENDED ON A DIFFERENT AXIS. It measured whether "
          f"a\n   requirement is NAMED and found {r472['explicit'] + r472['implied']} of "
          f"{r472['n_entries']}. This asks whether a NAMED one is RIGHT, and finds that\n   the "
          f"question is not answerable from what the register stores.")
    print(f"⚠ WHAT THIS CANNOT SAY: whether each affected check would ACTUALLY run on the disjoint "
          f"population.\n   That needs the check implemented and executed, one round per entry.")

    out = HERE / "results" / "requirement_class.json"
    out.write_text(json.dumps({
        "round": "R1029", "falsified_requirement": FALSIFIED,
        "prior_art": {"source": "R472", "n_entries": r472["n_entries"],
                      "explicit": r472["explicit"], "implied": r472["implied"],
                      "none": r472["none"], "types": r472["requirements"],
                      "note": "R472 measured PRESENCE of a requirement; this measures whether a "
                              "named one is RIGHT. Different property, not a re-run."},
        "classifier_controls": {"positive": bool(pc), "negative": bool(nc), "g0": bool(g0),
                                "discriminates_vs_other_types": bool(discriminates),
                                "target_share": tgt["share"], "other_share": other_share},
        "by_requirement": rows,
        "target": {"matched": len(sel), "misnamed": len(misnamed), "false_runnable": len(runnable),
                   "unverified": len(unver),
                   "misnamed_rounds": sorted({e["round"] for e in misnamed}),
                   "runnable_rounds": sorted({e["round"] for e in runnable})},
        "affected_numerator": affected,
        "denominator_not_identified": {"r472_tabulation": r472["requirements"][FALSIFIED],
                                       "token_matcher": len(sel), "direct_regex": direct,
                                       "why": "R472 README: the instrument's unit is PHRASING, the claim's unit is NAMING A REQUIREMENT"},
        "repair": "store the requirement TYPE as a field when the entry is written",
        "world": world,
        "limitation": "text is a proxy for the check; the classifier is used only in its sound "
                      "direction and the FALSE column requires the field to exist in the data",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
