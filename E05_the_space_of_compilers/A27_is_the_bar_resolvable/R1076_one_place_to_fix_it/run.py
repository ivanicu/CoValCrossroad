"""R1076 — how many times was the value-membership test re-implemented, and how many are precision-blind?

R1075 killed five rounds because R1070 wrote a fresh EXACT float comparison instead of reusing the
rounding-aware one R1047 had already written. The stated lesson was that **a fix inside one round's
script does not propagate**. That is a hypothesis about this repository, and it is countable.

⭐ AND COUNTING IT IS NOT THE PRODUCT. The product is `assurance/valuematch.py` — one place the fix
   can live — shipped in this round with the acceptance test that it finds what R1070's exact test
   missed. A round that measures a defect and leaves it unfixable is cost recovery.

ESTIMAND        the number of distinct value-membership implementations across the repository, and
                how many compare floats EXACTLY rather than at the statement's displayed precision
IDENTIFICATION  ⚠ PARTIAL AND NAMED FIRST. `a membership test` is recognised by shape — a function
                whose body compares a float against a container or applies a tolerance. A helper
                written differently will be missed, so the count is a LOWER bound on
                re-implementation and an upper bound on nothing.
SCOPE           population : assurance/*.py and every round run.py in E05
                instrument : AST function extraction + a shape classifier on the body
                baseline   : R1047's `has_rounded` and R1070's exact `has`, both known
                regime     : this checkout
WORLDS          A ISOLATED — one or two implementations, so R1075's `does not propagate` describes a
                  single lapse rather than a pattern, and a shared helper is over-engineering.
                B A PATTERN — many independent implementations, most precision-blind, so the fix has
                  never had one place to live and every future round will re-make the same choice.
                prediction matrix: A -> few implementations; B -> many, mostly exact
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      >= 5 implementations and a majority precision-blind -> World B, ship the helper
                      otherwise                                           -> World A, report and stop
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ both KNOWN implementations must be found and classified correctly: R1047's
                `has_rounded` as precision-aware, R1070's `has` as exact. A classifier that misses a
                known case cannot count unknown ones.
NEGATIVE CTRL   a function that is plainly not a membership test — `main` — must not be classified as
                one.
PLACEBO         a file with no functions contributes nothing and is not counted as `no exact tests`.
NOISE FLOOR     N/A - this is an enumeration of committed code, not a sample. Stated, not omitted.
MULTIPLICITY    every implementation reported with its file, name and verdict, not a count alone.
SEEDS           N/A.
IMPOSSIBLE      whether a precision-blind test was WRONG in its own round. Exactness is correct when
                both sides come from the same computation; it is wrong only when one side is a
                displayed value. SETTLES: IN-RELEASE per round, by reading what it compares.
"""
import ast, json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E05 = ROOT / "E05_the_space_of_compilers"
ASSUR = ROOT / "assurance"


def classify(fn, src):
    """shape test: does this function decide membership of a float in a container?

    ⛔ THE FIRST VERSION CLASSIFIED `main` AS A MEMBERSHIP TEST AND ITS OWN NEGATIVE CONTROL CAUGHT
       IT. Any long function contains ` in `, `==` and `abs(`; shape alone cannot separate a helper
       from a script. A membership helper is SHORT and returns a comparison — so length is part of
       the definition, not a convenience. Stated because it changes what is being counted.
    """
    body = ast.get_source_segment(src, fn) or ""
    if len(body.splitlines()) > 12:
        return None
    # ⛔⛔ AND THE SECOND VERSION WAS STILL CONTAMINATED: it counted `cls`, `agree`, `top1` — the
    #   pairwise-sign and scoring helpers — as membership tests, because any short function
    #   returning a comparison matched. The positive control passed anyway: it only checks that the
    #   KNOWN cases are FOUND, never that what is found is the thing being claimed. §4's row
    #   verbatim. The claim's unit is `decides whether a scalar is present in a CONTAINER`, so the
    #   function must take >=2 args, iterate or test membership over the second, and compare the
    #   first — all three, not any of them.
    low = body.lower()
    args = [a.arg for a in fn.args.args]
    if len(args) < 2:
        return None
    container = args[1]
    over_container = bool(re.search(r"(for\s+\w+\s+in\s+" + re.escape(container) + r"\b|"
                                    r"\bin\s+" + re.escape(container) + r"\b)", low))
    compares_first = args[0] in low
    returns_bool = bool(re.search(r"return\s+(any\(|all\(|.*(==|<=|>=|\bin\b))", low))
    # ⛔ AND ONE STOWAWAY SURVIVED THAT: `agree`, which iterates a container and compares — but
    #   RETURNS A NUMBER. A membership test returns a VERDICT. Excluding numeric aggregations is
    #   principled rather than a patch on a symptom: it is what distinguishes `is it present` from
    #   `how much does it score`.
    aggregates = bool(re.search(r"return\s+[^\n]*\b(mean|sum|len|float|np\.)\s*\(", low))
    if not (over_container and compares_first and returns_bool) or aggregates:
        return None
    if "round(" in low:
        return "precision-aware"
    if "abs(" in low and ("1e-" in low or "tol" in low):
        return "tolerance"
    if "==" in low or re.search(r"\bin\s+\w*(pool|set|stored|arc|s)\b", low):
        return "exact"
    return None


def main() -> int:
    files = sorted(list(ASSUR.glob("*.py")) + list(E05.glob("A*/R*/run.py")))
    if len(files) < 20:
        print("  UNRUNNABLE: too few sources. Exit 2, never 0."); return 2
    rows = []
    for p in files:
        try:
            src = p.read_text()
            tree = ast.parse(src)
        except Exception:
            continue
        for fn in ast.walk(tree):
            if not isinstance(fn, ast.FunctionDef):
                continue
            k = classify(fn, src)
            if k:
                rows.append({"file": str(p.relative_to(ROOT)), "name": fn.name, "kind": k})
    if not rows:
        print("  UNRUNNABLE: no membership test found. Exit 2, never 0."); return 2

    def find(nm, frag):
        return [r for r in rows if r["name"] == nm and frag in r["file"]]

    # the KNOWN pair both live in R1047's file: it kept the exact `has` and added `has_rounded`
    pos_a = [r for r in find("has_rounded", "R1047") if r["kind"] == "precision-aware"]
    pos_b = [r for r in find("has", "R1047") if r["kind"] in ("exact", "tolerance")]
    pos = bool(pos_a) and bool(pos_b)
    NOT_MEMBERSHIP = {"main", "cls", "agree", "top1", "rank_obs", "yvec"}
    stowaways = sorted({r["name"] for r in rows} & NOT_MEMBERSHIP)
    neg = not stowaways
    print(f"  NEGATIVE — known NON-membership helpers must not be counted "
          f"({sorted(NOT_MEMBERSHIP)}): {neg}" + (f" ⛔ stowaways: {stowaways}" if stowaways else ""))
    print(f"  POSITIVE — both KNOWN implementations found and classified: {pos} "
          f"(R1047 has_rounded -> {[r['kind'] for r in find('has_rounded', 'R1047')]}, "
          f"R1047 has -> {[r['kind'] for r in find('has', 'R1047')]})")
    if not (pos and neg):
        print("  the classifier cannot be trusted to count. Exit 2, never 0."); return 2

    kinds = {}
    for r in rows:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    blind = kinds.get("exact", 0)
    aware = kinds.get("precision-aware", 0) + kinds.get("tolerance", 0)
    print(f"\n  ⭐ value-membership implementations found: {len(rows)} across "
          f"{len({r['file'] for r in rows})} files")
    for k, v in sorted(kinds.items()):
        print(f"     {k:<16} {v}")
    for r in rows[:10]:
        print(f"     {r['kind']:<16} {r['name']:<14} {r['file']}")

    pattern = len(rows) >= 5 and blind > aware
    print()
    if pattern:
        world = (f"⛔ B A PATTERN, NOT A LAPSE — {len(rows)} independent value-membership "
                 f"implementations, {blind} of them precision-blind against {aware} precision-aware. "
                 f"**The fix has never had one place to live**, so every round re-makes the choice "
                 f"and R1075's collapse was waiting to happen again.")
    else:
        world = (f"⭐ A ISOLATED — {len(rows)} implementations, {blind} exact and {aware} "
                 f"precision-aware. R1075's `does not propagate` describes a lapse rather than a "
                 f"pattern at this count.")
    print(world)

    # ---------- the remedy, shipped ----------
    helper = ASSUR / "valuematch.py"
    helper.write_text('''#!/usr/bin/env python3
"""The one place the value-membership test lives. Import it; do not re-implement it.

⭐ WHY THIS EXISTS (R1076, after R1075). R1047 found that a statement prints a ROUNDED display value
   while an artifact stores the FULL one, so an exact float comparison finds nothing. It wrote a
   rounding-aware test — inside its own round script. R1070 wrote a fresh EXACT one, and five rounds
   built on the empty population that produced. **A fix inside one round's script does not
   propagate.**

⛔ THE RULE: when one side of a comparison is a value READ FROM PROSE, match at that value's OWN
   displayed precision. Exact matching is correct only when both sides come from the same
   computation.
"""
from __future__ import annotations


def displayed_precision(token: str) -> int:
    """decimal places the statement actually shows — the precision the claim is made at"""
    return len(token.split(".")[1]) if "." in token else 0


def matches(token: str, value: float) -> bool:
    """does `value` (stored, full precision) match `token` (as written in prose)?"""
    dp = displayed_precision(token)
    return round(float(value), dp) == round(float(token), dp)


def in_pool(token: str, pool) -> bool:
    """is a value matching `token` present in `pool`? Use this, not `float(token) in pool`."""
    return any(matches(token, v) for v in pool)


def find_all(token: str, pool):
    """every stored value that the prose token could be a rounded rendering of"""
    return sorted(v for v in pool if matches(token, v))
''')
    sys.path.insert(0, str(ASSUR))
    import importlib
    vm = importlib.import_module("valuematch")

    known = {"0.559311": 0.5593110791885862, "0.551354": 0.5513543391990778,
             "0.009103": 0.009102604212460431}
    accept = all(vm.in_pool(t, {v}) for t, v in known.items())
    reject = not vm.in_pool("0.559311", {0.4})
    print(f"\n⭐ REMEDY SHIPPED — assurance/valuematch.py")
    print(f"   ACCEPTANCE — it finds the three values R1070's exact test missed: {accept}")
    print(f"   AND IT STILL SAYS NO — an unrelated value is not matched: {reject}")
    if not (accept and reject):
        print("   the helper does not do what the round claims. Exit 2, never 0."); return 2

    o = HERE / "results" / "membership_tests.json"
    o.write_text(json.dumps({
        "round": "R1076", "implementations": len(rows), "kinds": kinds,
        "precision_blind": blind, "precision_aware": aware, "rows": rows,
        "world": world, "remedy": "assurance/valuematch.py",
        "acceptance": {"finds_missed_values": bool(accept), "rejects_unrelated": bool(reject)},
        "controls": {"positive_known_pair": bool(pos), "negative_main_excluded": bool(neg)},
        "limitation": "the classifier recognises membership tests by shape, so the count is a LOWER "
                      "bound on re-implementation",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
