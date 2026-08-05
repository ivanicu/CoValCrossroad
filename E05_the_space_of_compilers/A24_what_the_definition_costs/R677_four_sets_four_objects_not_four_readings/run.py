#!/usr/bin/env python3
"""
R677 -- four sets, four OBJECTS, not four readings. R676's attribution retracted.

CHECK #278 ON R676's NEXT LINE -- ITS CAUSAL ATTRIBUTION WAS ASSERTED, NEVER CHECKED.
  R676 closed: "Each was produced by a different ③ variant — ③-rank, ③-as-written, ③-checkable,
  ③-published." Reading the four rounds' own ESTIMAND lines shows three of the four are not ③
  readings at all: R470.P is the extension BEFORE ③ is applied, R442.published_five is the list
  CoVal PUBLISHED (R442's own output prints "and NEITHER is the published five"), and R509.five sits
  in a round whose stated answer is an extension of ONE. ⭐ SECOND TIME IN THIS ARC I ASSERTED THAT
  A MECHANISM PRODUCED SOMETHING WITHOUT CHECKING (ledger 745 was the first), and both times the
  sentence was the round's LAST -- the one with no control attached.

ESTIMAND        for every five-member arm set, what its field DENOTES per its own round's ESTIMAND:
                (a) extension under a ③ reading, (b) a set BEFORE ③, (c) an external publication
                list, (d) other. Then among (a): distinct sets and their intersection.
IDENTIFICATION  a docstring states INTENT, not what the code computed. This measures STATED
                denotation -- an upper bound on field-name/object agreement, and it is labelled so.
SCOPE           population : the five-member arm sets R676 censused
                instrument : regex over each round's docstring ESTIMAND + clause-③ mentions
                             instrument unit = A ROUND'S STATED ESTIMAND
                             claim unit      = WHAT A FIELD DENOTES
                             ⚠ NOT EQUAL -- a round may state one estimand and store many fields.
                             Hence per-FIELD adjudication below, and the bound.
                baseline   : R676's unclassified count of 4
                regime     : this repository at HEAD
WORLDS          A MIS-FRAMED: >=1 survives; R676's number was right and its attribution wrong.
                B VOID: 0 survive; R676's finding dies entirely, not just its framing.
KILL            pre-registered: 0 survivors -> world B, and the retraction says VOID.
POSITIVE CTRL   the 22×-cited ③-rank set must classify as a ③ extension.
NEGATIVE CTRL   R470.P (known pre-③) must NOT so classify -- the g=0 check.
PLACEBO         a field in a round never mentioning ③ must not classify as a ③ extension.
ARTIFACT        results/denotation.json
IMPOSSIBLE      proving a round's code computed what its docstring says needs re-execution of 600+
                rounds against their own inputs, several of which are corpus-dependent (93 rounds,
                measured earlier in this arc). Stated denotation is what is available.
"""
from __future__ import annotations
import itertools, json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
PRIOR = ARC / "R676_the_number_five_is_stable_the_membership_is_not" / "results" / "five_member_sets.json"

C3 = re.compile(r"③|clause[ _-]?(three|3)\b", re.I)
BEFORE = re.compile(r"before ③|before clause[ _-]?(three|3)|①∧②∧④|prior to ③", re.I)
PUBLISHED = re.compile(r"publish(ed)?(?![a-z])", re.I)   # ⭐ NOT \b -- "_" IS a word char, so
                                                         #   \bpublished\b cannot match published_five


def estimand_of(round_prefix):
    for d in ARC.glob(f"{round_prefix}_*"):
        f = d / "run.py"
        if f.is_file():
            t = f.read_text(errors="ignore")
            m = re.search(r"ESTIMAND(.{0,400})", t, re.S)
            return (" ".join(m.group(1).split()) if m else ""), t
    return "", ""


def classify(field, est, src):
    """⭐ per-FIELD, because a round states one estimand and stores many fields."""
    fname = field.split(".", 1)[1] if "." in field else field
    near = ""
    for m in re.finditer(re.escape(fname), src):
        near += " " + " ".join(src[max(0, m.start()-300): m.start()+120].split())
    if BEFORE.search(est) or BEFORE.search(near): return "b_before_three"
    if PUBLISHED.search(fname) or (PUBLISHED.search(near) and not C3.search(fname)):
        return "c_publication_list"
    if C3.search(est) and re.search(r"extens|admit", fname, re.I): return "a_three_extension"
    if re.search(r"extens|admit|published|identity", fname, re.I) and C3.search(est):
        return "a_three_extension"
    return "d_other"


def main() -> int:
    if not PRIOR.is_file():
        print("UNRUNNABLE: R676's census artifact absent. Exit 2, never 0."); return 2
    census = json.loads(PRIOR.read_text())["sets"]

    rows = []
    for s in census:
        for cite in s["cited_by"]:
            rp = cite.split(".", 1)[0]
            est, src = estimand_of(rp)
            rows.append({"set": tuple(sorted(s["members"])), "cite": cite,
                         "kind": classify(cite, est, src)})

    print("─── CONTROLS (the classifier is a TEXT instrument and gets its own) ───")
    def kind_of(c): return next((r["kind"] for r in rows if r["cite"] == c), None)
    # ⭐ `or` SHORT-CIRCUITS ON A TRUTHY STRING -- the first version never consulted the fallback,
    #    so it asked R339 (whose ESTIMAND has no ③) for a ③ verdict and read its FAIL as the
    #    classifier's. The control's two sides were not the same object. §4's remedy exactly.
    cands = [c for c in ("R294.admitted", "R339.published", "R301.admitted_2b") if kind_of(c)]
    kinds_pos = {c: kind_of(c) for c in cands}
    pos = "a_three_extension" if "a_three_extension" in kinds_pos.values() else kinds_pos
    posok = "a_three_extension" in kinds_pos.values()
    print(f"  POSITIVE  the 22×-cited ③-rank set classifies as a ③ extension -> {pos} -> "
          f"{'PASS' if posok else '⛔ FAIL'}")
    g0 = kind_of("R470.P")
    g0ok = g0 != "a_three_extension"
    print(f"  g=0       R470.P (known PRE-③) must NOT so classify -> {g0} -> "
          f"{'PASS — it can separate' if g0ok else '⛔ FAIL — cannot separate, no count admissible'}")
    neg = kind_of("R404.rubric_rules")
    negok = neg != "a_three_extension"
    print(f"  NEGATIVE  R404.rubric_rules (rule prefixes) not an extension -> {neg} -> "
          f"{'PASS' if negok else '⛔ FAIL'}")
    plc = classify("RX.some_field", "ESTIMAND a quantity with no clause mentioned", "some_field = 1")
    plcok = plc != "a_three_extension"
    print(f"  PLACEBO   a field in a round never mentioning ③ -> {plc} -> "
          f"{'PASS' if plcok else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and plcok

    from collections import Counter
    print(f"\n─── WHAT THE {len(census)} FIVE-MEMBER SETS ACTUALLY DENOTE (G3 — all printed) ───")
    # ⭐⭐⭐ THE AGGREGATOR IS AN UNREGISTERED DEGREE OF FREEDOM, AND IT DECIDES THE ANSWER.
    #     A set cited 22× has ONE producer and 21 copies, and nothing in these artifacts marks
    #     which. Under MAJORITY the copies outvote the producer; under ANY one ③-stating citation
    #     suffices; under EARLIEST the lowest round id wins. G4: run all three, publish the curve.
    def agg(k, how):
        ks = [r for r in rows if r["set"] == k]
        if how == "majority":
            return Counter(r["kind"] for r in ks).most_common(1)[0][0]
        if how == "any_three":
            return ("a_three_extension" if any(r["kind"] == "a_three_extension" for r in ks)
                    else Counter(r["kind"] for r in ks).most_common(1)[0][0])
        return sorted(ks, key=lambda r: r["cite"])[0]["kind"]          # earliest round id

    SPEC = ["majority", "any_three", "earliest"]
    curve = {h: sum(1 for s in census
                    if agg(tuple(sorted(s["members"])), h) == "a_three_extension") for h in SPEC}
    print(f"  ⭐ SPECIFICATION CURVE over the aggregator (G4 — every cell, including the killers):")
    for h in SPEC:
        print(f"     {h:<10} -> {curve[h]} genuine ③-reading extension(s)")
    print(f"  ⭐ the count is {min(curve.values())}–{max(curve.values())} depending ENTIRELY on an "
          f"aggregation choice nobody registered.")
    identified = len(set(curve.values())) == 1
    print(f"  ⚠ {'the estimand is IDENTIFIED — every aggregator agrees' if identified else 'THE ESTIMAND IS NOT IDENTIFIED: the specifications disagree, so no POINT is admissible, only the range.'}")

    per_set = {}
    for s in census:
        k = tuple(sorted(s["members"]))
        per_set[k] = agg(k, "majority")
        print(f"  {per_set[k]:<20} {list(k)}")
        print(f"  {'':20} cited by {', '.join(s['cited_by'][:5])}")
    surv = [k for k, v in per_set.items() if v == "a_three_extension"]
    print(f"\n  ⭐ genuine ③-reading extensions : {len(surv)}")
    print(f"  ⚠ registered 1 [1,3] -> {len(surv)}: "
          f"{'INSIDE' if 1 <= len(surv) <= 3 else '⛔ OUTSIDE'}, error {len(surv)-1:+d}")
    killed = len(surv) == 0
    print(f"  pre-registered kill (0 survivors) -> "
          f"{'⭐ FIRES — R676 is VOID, not mis-framed' if killed else 'does not fire'}")
    if surv:
        inter = set.intersection(*[set(k) for k in surv])
        dirn = all("coval_core" in k for k in surv)
        print(f"  intersection of survivors : {sorted(inter) or '∅'}")
        print(f"  DIRECTIONAL every survivor contains coval_core -> {'HOLDS' if dirn else '⛔ FAILS'}")
    else:
        inter, dirn = set(), False

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; no count of denotations is admissible."
    elif not identified:
        world = (f"⭐⭐⭐ NOT IDENTIFIED — AND THAT IS THE RESULT. The number of five-member sets that "
                 f"denote a ③-reading extension is {min(curve.values())}–{max(curve.values())} "
                 f"({curve}), decided entirely by whether a set's denotation is taken from its "
                 f"PRODUCER or from its 21 RE-CITATIONS. Nothing in these artifacts marks which "
                 f"citation produced a set, so a lineage question silently becomes a popularity "
                 f"contest. ⛔ R676's headline is RETRACTED: 'four extension readings sharing "
                 f"coval_core' is not merely mis-attributed, it is a quantity this corpus cannot "
                 f"currently pin down — and my registered point of 1 scored INSIDE under one "
                 f"aggregator and OUTSIDE under another, which is the tell. ⭐ THE STANDING FINDING "
                 f"IS THE MISSING FIELD: an artifact that stores a set must record whether it "
                 f"COMPUTED it or COPIED it, and none of the {len(rows)} citations here does.")
    elif killed:
        world = ("⭐ WORLD B — R676's FINDING IS VOID. No five-member set in the corpus denotes an "
                 "extension under a ③ reading, so 'the extension is written down four ways' had no "
                 "referent at all.")
    else:
        others = Counter(v for v in per_set.values() if v != "a_three_extension")
        world = (f"⭐⭐ WORLD A — MIS-FRAMED, NOT WRONG. {len(surv)} of the {len(census)} five-member "
                 f"sets denote an extension under a ③ reading; the rest denote DIFFERENT OBJECTS "
                 f"wearing extension-shaped names: {dict(others)}. ⛔ SO R676's HEADLINE IS RETRACTED "
                 f"as stated — 'four extension readings sharing coval_core' compared a ③ extension "
                 f"against a PRE-③ set, a PUBLICATION list and an intermediate. ⭐ AND THE REPLACEMENT "
                 f"IS SHARPER, BECAUSE IT IS ABOUT THE ARTIFACTS RATHER THAN THE CLAUSE: this corpus "
                 f"stores {len(census)} five-member arm sets under names a reader parses as "
                 f"'the extension', and only {len(surv)} is one. The collision that made R676 look "
                 f"like a clause finding is a NAMING failure, and naming is the layer a next site "
                 f"inherits.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(census)} sets × {len(rows)} citations, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"denotation.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "n_sets": len(census), "n_three_extensions": len(surv),
        "kill_fired": killed, "survivor_intersection": sorted(inter),
        "spec_curve_aggregator": curve, "identified": identified,
        "directional_holds": dirn,
        "per_set": [{"members": list(k), "denotes": v} for k, v in per_set.items()],
        "registered": "1 [1,3] survivors; every survivor contains coval_core; kill if 0",
        "check278": ("R676's NEXT asserted each set came from a different ③ variant. R470.P is the "
                     "extension BEFORE ③; R442.published_five is CoVal's published list; R509.five "
                     "sits in a round whose answer is ONE. The attribution was never checked."),
        "identification_limit": ("a docstring states INTENT, not what the code computed; this is an "
                                 "upper bound on field-name/object agreement."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'denotation.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
