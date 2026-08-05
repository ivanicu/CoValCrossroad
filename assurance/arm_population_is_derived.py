#!/usr/bin/env python3
"""A round that compares ARMS must DERIVE its arm list from a rule, or DECLARE why it is typed.

⛔ WHY THIS FILE EXISTS. Three rounds in one arc reached a conclusion over a population they had typed
by hand, and each time the fix was applied to that one class rather than to the practice:

    R477  bounded the ③-admissible class by the nine arms that happened to carry a `.npz`.
          R478 censused the real class: 1,820 subsets. The gain narrowed +0.0098 -> +0.0071.
    R485  bounded the admissible prompt-aware class by a hand-picked list of 14 arms.
    R486  asserted in prose that `gen`, `topvar_k4` and `full` "are the whole population".
          R487 counted 101 `sat_*.npz`, of which 30 are admissible and prompt-aware, 23 scorable.
          `gen` survived as the maximum -- but that was luck, not method.

**A class is what a rule admits, not what I enumerated.** `comparator_scope.py` enforces exactly this
shape for comparators and `register_requirements.py` for requirements. Nothing enforced it for arms.

PROXY LEDGER (P6) -- this check approximates its property in ONE direction:
    PROPERTY    "the round's arm population is the one its own rule admits"
    PROXY       the arm list is built by a comprehension/call over a glob or predicate, rather than
                written as a list of string literals
    IMPLICATION derived ⇒ nothing was silently omitted BY HAND. It does NOT imply the rule is right:
                R487's own first census derived 32 arms and 6 of them were from another benchmark.
    SAFE SIDE   a TYPED list is flagged unless it carries a declaration; a DERIVED list is never
                certified correct, only cleared of hand-enumeration.

DECLARATION, for the cases where typing is right (a named contrast, a worked example):
    put `ARM POPULATION: <reason>` in the round's docstring or beside the list. The reason is not
    parsed -- the point is that someone had to write one, which is what `comparator_scope` learned.
"""
from __future__ import annotations
import ast, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DECL = re.compile(r"ARM POPULATION\s*:", re.I)
# a round "compares arms" if it loads more than one arm artifact by name
LOADS = re.compile(r"sat_\{?[a-z_]|sat_\{|f\"sat_|'sat_|\"sat_")


# ⛔ THE DETECTOR IS GROUNDED IN THE OBJECT, NOT IN A NAMING CONVENTION.
# The first version looked for assignments whose NAME matched `ARM|arms$`. Its positive control --
# built from the three real rounds this check exists for -- failed 3 of 4, because rounds name the
# variable `ADMISSIBLE` (R477), `adm_aware` (R487), or build it inline (R486). 93 of 143 rounds
# landed in an unclassified bucket. An invented test case would have passed.
# An arm list is a list of strings that ARE arm names, and arm names are on disk.
ARM_NAMES = {p.stem[4:] for p in (ROOT/"corebench"/"results").glob("sat_*.npz")}


def _literal_arm_seq(x, n_min: int = 3) -> bool:
    """True iff x is a literal sequence containing >= n_min strings that name real arms."""
    if isinstance(x, (ast.List, ast.Set, ast.Tuple)):
        lits = [e.value for e in x.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        return sum(1 for s in lits if s in ARM_NAMES) >= n_min
    if isinstance(x, ast.BinOp) and isinstance(x.op, ast.Add):
        return _literal_arm_seq(x.left, n_min) or _literal_arm_seq(x.right, n_min)
    return False


def _derives_from_rule(tree) -> bool:
    """True iff the source enumerates arms from disk or filters a discovered list."""
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            name = getattr(f, "attr", getattr(f, "id", ""))
            if name in ("glob", "iterdir", "listdir", "discover"):
                return True
    return False


def classify(src: str):
    """-> (compares_arms, kind) with kind in DERIVED / TYPED / DECLARED / NONE."""
    if not LOADS.search(src):
        return False, "NONE"
    if DECL.search(src):
        return True, "DECLARED"
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return True, "UNPARSEABLE"
    # ANY literal sequence of >=3 real arm names, wherever it appears -- assignment, comprehension
    # iterable, call argument -- is a hand-typed population.
    # ⚠ PRECEDENCE, AND IT IS A PROXY DECISION WITH A NAMED COST.
    # R487 DERIVES its population (`glob("sat_*.npz")`) and ALSO contains literal sets of real arm
    # names -- `BLIND` and `CORE_FAMILY` -- which are EXCLUSIONS applied to the derived list, not the
    # population itself. A literal used to exclude is a rule component. Deciding this properly needs
    # dataflow; instead, enumeration-from-disk takes precedence, and the cost is stated:
    #   MISSED CASE: a round that globs for something else and hand-types its arms reads as DERIVED.
    # The check is therefore sound in ONE direction -- TYPED is reliable, DERIVED is "not obviously
    # hand-enumerated" -- which is the same asymmetry `comparator_scope` carries.
    if _derives_from_rule(tree):
        return True, "DERIVED"
    if any(_literal_arm_seq(n) for n in ast.walk(tree)):
        return True, "TYPED"
    return True, "NONE"


def main() -> int:
    rounds = sorted(ROOT.glob("E*/A*/R*/run.py"))
    if not rounds:
        print("⛔ no rounds found — this check examined nothing. EXIT 2.")
        return 2
    rows = [(p.parent.name, *classify(p.read_text())) for p in rounds]
    comparing = [r for r in rows if r[1]]
    if not comparing:
        print("⛔ no round loads an arm artifact — population empty. EXIT 2.")
        return 2

    # POSITIVE CONTROL, on REAL cases rather than invented ones: the three rounds whose hand-typed
    # populations were actually corrected must be flagged, and the two that derived theirs must not.
    want = {"R477_what_does_clause_three_actually_cost": "TYPED",
            "R485_is_the_definition_satisfiable_at_all": "TYPED",
            "R486_is_clause_two_bar_an_outlier_or_the_class": "TYPED",
            "R487_the_admissible_population_is_32_not_three": "DERIVED"}
    got = {n: k for n, _c, k in rows if n in want}
    ok = True
    print("  POSITIVE CONTROL — the rounds this check was built from:")
    for n, w in want.items():
        g = got.get(n, "ABSENT")
        good = g == w
        ok &= good
        print(f"    {n:<48} want {w:<9} got {g:<11} {'ok' if good else '⛔'}")

    # ---- RATCHET (R483's lesson: a gate that can never pass stops being read) -------------------
    import json
    FR = ROOT/"assurance"/"KNOWN_TYPED_ARM_POPULATION.json"
    frozen = set(json.loads(FR.read_text())["typed"]) if FR.exists() else set()
    typed_all = {r[0] for r in comparing if r[2] == "TYPED"}
    new = sorted(typed_all - frozen)
    fixed = sorted(frozen - typed_all)
    typed = [r for r in comparing if r[2] == "TYPED"]
    print(f"\n  rounds loading arm artifacts : {len(comparing)} of {len(rounds)}")
    print(f"  DERIVED   {sum(1 for r in comparing if r[2]=='DERIVED')}"
          f"   DECLARED {sum(1 for r in comparing if r[2]=='DECLARED')}"
          f"   TYPED {len(typed)}"
          f"   other {sum(1 for r in comparing if r[2] in ('NONE','UNPARSEABLE'))}")
    if typed:
        print(f"\n  ⚠ TYPED — an arm list written by hand, with no `ARM POPULATION:` declaration:")
        for n, _c, _k in typed[:25]:
            print(f"    {n}")
        if len(typed) > 25:
            print(f"    … and {len(typed)-25} more")
    print(f"\n  PROXY: derived ⇒ not hand-enumerated. It does NOT certify the rule is right —"
          f"\n    R487's own first census derived 32 arms and six were from another benchmark.")
    if not ok:
        print("\n  ⛔ FAIL: the positive control did not reproduce the known cases.")
        return 1
    bad = False
    if new:
        bad = True
        print(f"\n  ⛔ NEW hand-typed arm population(s) — the debt grew: {new}")
    if fixed:
        bad = True
        print(f"\n  ⛔ FROZEN LIST IS STALE — {len(fixed)} entr(ies) no longer type their population: "
              f"{fixed}\n     Remove them. A frozen list that outlives its reason is the confession "
              f"this ratchet replaces.")
    if not bad:
        print(f"\n  PASS — no new hand-typed populations; the frozen debt of {len(frozen)} is "
              f"unchanged and contains nothing already fixed.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
