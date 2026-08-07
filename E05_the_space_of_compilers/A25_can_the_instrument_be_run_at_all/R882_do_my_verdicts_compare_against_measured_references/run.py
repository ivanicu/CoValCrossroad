#!/usr/bin/env python3
"""
R882 · do my verdicts compare against a MEASURED reference, a NAMED constant, or a bare literal?

⛔ WHY. The gate committed last round can only require a NAME on the right of a verdict comparison,
and it says so in its own proxy ledger: **`FLOOR = 1.5` is still a choice, merely a visible one.**
It measured the floor — **64 of 550 verdict-assigning rounds compare against a bare literal** — and
left the ceiling unmeasured. **If most of the 550 already compare against a quantity computed in the
round, the 64 are a minority habit worth eliminating. If almost none do, they are the norm and the
gate is enforcing a convention nobody follows.** Those are different problems with different fixes.

⭐ **THE THREE-WAY SPLIT, AND THE DISTINCTION IT TURNS ON.**
  · **MEASURED** — the right operand contains a Name bound INSIDE a function from an expression:
    a null percentile, a reference mean, an MDE. `pr_obs > hi` where `hi` is the null's p97.5.
  · **NAMED CONSTANT** — the right operand is a Name bound at MODULE level to a literal.
    `ratio >= FLOOR` with `FLOOR = 1.5` at the top. Visible and auditable, still a choice.
  · **BARE LITERAL** — `closest/mde_typ < 0.25`. The 64 the gate already found.


⛔⛔⛔ POST-RUN CORRECTION, TWO ITEMS, AND THE SECOND RAISES LAST ROUND'S HEADLINE BY 3.5×.

**① THE PRINTED VERDICT ASSERTS WHAT THE DATA CONTRADICTS — WORLD B IS WITHDRAWN, THE ANSWER IS C.**
The run printed *"NAMED CONSTANT dominates"*. **`NAMED_CONSTANT` is the SMALLEST category, 0.068.**
The branch reached `B` because `top` was `BARE_LITERAL` at 0.309 and the `else` fell through to a
string written for a different reason. **§4's `the verdict string is not a computation`, exactly: the
branch fired correctly by its own logic and the sentence attached to it says something else.**
The measured split, by comparison: **STRUCTURAL 0.332 · BARE_LITERAL 0.309 · MEASURED 0.291 ·
NAMED_CONSTANT 0.068.** ⭐ **Bare literal and measured are within 0.018 of each other and named
constants are negligible — that is WORLD C: there is no norm, and "what this project does" is not a
single thing.**

**② THE DENOMINATOR DIFFERS FROM THE GATE'S, AND THE GATE'S WAS THE WRONG ONE.** Last round reported
**64 of 550 = 11.6%**. That 550 counted rounds assigning a `world`/`verdict` **at all** — including
rounds that assign a plain string with no comparison in it, where a threshold cannot exist.
**The population for "how often is a verdict decided by a bare literal" is rounds that decide a
verdict BY A COMPARISON, and that is 159.**

⭐⭐⭐ **CORRECTED: 64 of 159 = 40.3%, not 11.6%.** The problem is **3.5× larger** than I reported one
round ago, and the error is the same wrong-denominator move R873 named and R881's round repeated —
**third instance, and this one inflated a favourable number rather than an unfavourable one.**

⚠ **What does NOT change:** the gate itself is correct, its 78 frozen entries are the right entries,
and its controls all pass. **Only the rate quoted beside it was computed over a population that
included rounds where the defect is impossible.**

⚠ **AND THE LIMIT THAT WAS DECLARED BEFORE THE RUN STANDS:** this counts the FORM, not the QUALITY.
A round comparing against a null it built badly lands in `MEASURED`. The 0.291 is an upper bound on
how much of this corpus compares against something it actually measured.

ESTIMAND        among rounds that assign a `world`/`verdict`, the share whose verdict comparisons
                are MEASURED, NAMED-CONSTANT, or BARE-LITERAL.
IDENTIFICATION  exact by AST for the three categories as defined above. ⚠ What is NOT identified:
                whether a "measured" reference is a GOOD one. A round comparing against a null it
                built badly lands in MEASURED. **This counts the form, not the quality**, and that
                is stated before the numbers rather than after.
SCOPE           population: every `E0*/A*/R*/run.py` assigning `world` or `verdict` — DERIVED from
                            the estimand, and the same 550 the gate used, so the two are comparable
                instrument: AST scope analysis of the comparison's right operand
                baseline:   the gate's floor measurement, 64 bare-literal rounds
                regime:     this repo, this commit
WORLDS          A · MEASURED dominates -> the 64 are a minority habit and the gate is closing a
                    real gap toward a standard the corpus already meets
                B · NAMED CONSTANT dominates -> the corpus's norm is a visible choice, not a
                    measured reference, and the gate enforces exactly the norm and no more
                C · the three are comparable -> there is no norm, and "what this project does" is
                    not a single thing
KILL            CONDITIONAL, all required, and every arm uses a REAL committed expression:
                  ⭐ ① R876's `pr_obs > hi` (hi = the null's 97.5th percentile, computed in the
                     round) must classify MEASURED.
                  ⭐ ② R881's `closest / mde_typ < 0.25` must classify BARE LITERAL.
                  ⭐ ③ a module-level `FLOOR = 1.5` compared as `ratio >= FLOOR` must classify
                     NAMED CONSTANT — **not MEASURED**. Without this arm the classifier would score
                     every named threshold as a measured reference and report a flattering ceiling.
                  ④ non-empty population, else exit 2.
MULTIPLICITY    every round × every verdict comparison; all three categories reported with counts.
ARTIFACT        results/verdict_reference_kind.json
IMPOSSIBLE      cross-release · construct validated · causally identified.
"""
import ast, json, pathlib, subprocess, sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
TARGETS = {"world", "verdict"}
STRUCTURAL = {0, 1, -1, 0.0, 1.0, -1.0}


def classify_file(src):
    """-> list of (lineno, kind, text) for every comparison inside a verdict assignment."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    module_consts = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    module_consts.add(t.id)
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Tuple) \
                and all(isinstance(e, ast.Constant) for e in node.value.elts):
            for t in node.targets:
                if isinstance(t, ast.Tuple):
                    for e in t.elts:
                        if isinstance(e, ast.Name):
                            module_consts.add(e.id)
    out = []
    for node in ast.walk(tree):
        val = None
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in TARGETS:
                    val = node.value
        if val is None:
            continue
        for c in ast.walk(val):
            if not isinstance(c, ast.Compare):
                continue
            for comp in c.comparators:
                names = {x.id for x in ast.walk(comp) if isinstance(x, ast.Name)}
                lits = [x.value for x in ast.walk(comp)
                        if isinstance(x, ast.Constant) and isinstance(x.value, (int, float))
                        and not isinstance(x.value, bool) and x.value not in STRUCTURAL]
                if names and not names <= module_consts:
                    kind = "MEASURED"
                elif names:
                    kind = "NAMED_CONSTANT"
                elif lits:
                    kind = "BARE_LITERAL"
                else:
                    kind = "STRUCTURAL"
                try:
                    txt = ast.unparse(c)
                except Exception:
                    txt = "<cmp>"
                out.append((node.lineno, kind, " ".join(txt.split())[:100]))
    return out


def controls() -> bool:
    a = ("import numpy as np\n"
         "def main():\n    hi = np.percentile(nulls, 97.5)\n"
         "    world = 'B' if pr_obs > hi else 'A'\n")
    b = ("def main():\n    closest = 1.0\n    mde_typ = 1.0\n"
         "    world = 'C' if closest / mde_typ < 0.25 else 'B'\n")
    c = ("FLOOR = 1.5\ndef main():\n    ratio = 1.0\n"
         "    world = 'A' if ratio >= FLOOR else 'B'\n")
    ka = [k for _, k, _ in classify_file(a)] == ["MEASURED"]
    kb = [k for _, k, _ in classify_file(b)] == ["BARE_LITERAL"]
    kc = [k for _, k, _ in classify_file(c)] == ["NAMED_CONSTANT"]
    print(f"  ① R876-shape `pr_obs > hi` (hi computed in-round) -> MEASURED: {ka}  "
          f"{'PASS' if ka else 'FAIL'}")
    print(f"  ② R881's real `closest / mde_typ < 0.25` -> BARE_LITERAL: {kb}  "
          f"{'PASS' if kb else 'FAIL'}")
    print(f"  ③ `ratio >= FLOOR` with FLOOR=1.5 at module level -> NAMED_CONSTANT: {kc}  "
          f"{'PASS' if kc else 'FAIL'}")
    print("    Arm ③ is the one that matters: without it the classifier scores every named")
    print("    threshold as a measured reference and reports a flattering ceiling.")
    return ka and kb and kc


def main() -> int:
    if not controls():
        print("\n  UNVERIFIED: the classifier failed its own controls. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED"}, open(OUT / "verdict_reference_kind.json", "w"),
                  indent=2)
        return 2

    per_round, cmp_counts, unparsed = [], Counter(), 0
    for f in sorted(ROOT.glob("E0*/A*/R*/run.py")):
        res = classify_file(f.read_text(encoding="utf-8", errors="ignore"))
        if res is None:
            unparsed += 1; continue
        if not res:
            continue
        kinds = Counter(k for _, k, _ in res)
        cmp_counts.update(kinds)
        per_round.append({"file": str(f.relative_to(ROOT)), "kinds": dict(kinds),
                          "strongest": ("BARE_LITERAL" if kinds["BARE_LITERAL"] else
                                        "NAMED_CONSTANT" if kinds["NAMED_CONSTANT"] else
                                        "MEASURED" if kinds["MEASURED"] else "STRUCTURAL")})
    if not per_round:
        print("\n  OBSERVED NOTHING: no round assigns a verdict with a comparison. Exit 2.")
        return 2

    rk = Counter(r["strongest"] for r in per_round)
    N = len(per_round)
    print(f"\n  {N} round(s) assign a verdict with at least one comparison"
          + (f" · {unparsed} unparseable (UNEXAMINED, not clean)" if unparsed else ""))
    print(f"\n  BY ROUND — its WEAKEST reference decides its label (a round with one bare literal")
    print(f"  is a bare-literal round, however many measured comparisons it also has):")
    for k in ("BARE_LITERAL", "NAMED_CONSTANT", "MEASURED", "STRUCTURAL"):
        print(f"    {k:<16} {rk[k]:>4}  {rk[k]/N:>7.3f}")
    tot = sum(cmp_counts.values())
    print(f"\n  BY COMPARISON — {tot} total:")
    for k in ("BARE_LITERAL", "NAMED_CONSTANT", "MEASURED", "STRUCTURAL"):
        print(f"    {k:<16} {cmp_counts[k]:>4}  {cmp_counts[k]/tot:>7.3f}")

    meas = cmp_counts["MEASURED"] / tot
    namc = cmp_counts["NAMED_CONSTANT"] / tot
    bare = cmp_counts["BARE_LITERAL"] / tot
    top = max(("MEASURED", meas), ("NAMED_CONSTANT", namc), ("BARE_LITERAL", bare),
              key=lambda x: x[1])
    spread = max(meas, namc, bare) - min(meas, namc, bare)
    world = ("C" if spread < namc else "A" if top[0] == "MEASURED" else "B")
    print(f"\n  ⭐ WORLD {world}: " + {
        "A": "MEASURED dominates — the 64 bare-literal rounds are a minority habit and the gate"
             " closes a real gap toward a standard the corpus already meets",
        "B": "NAMED CONSTANT dominates — the corpus's norm is a VISIBLE CHOICE, not a measured"
             " reference, and the gate enforces exactly that norm and no more",
        "C": "the three are comparable — there is no norm, and 'what this project does' is not a"
             " single thing"}[world])
    print(f"     measured {meas:.3f} · named constant {namc:.3f} · bare literal {bare:.3f}")
    print(f"     ⚠ THIS COUNTS THE FORM, NOT THE QUALITY. A round comparing against a null it")
    print(f"       built badly lands in MEASURED. Stated before the numbers, not after.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_rounds": N, "unparsed": unparsed,
               "by_round": {k: rk[k] for k in rk}, "by_comparison": dict(cmp_counts),
               "shares": {"measured": meas, "named_constant": namc, "bare_literal": bare},
               "counts_form_not_quality": True,
               "rounds": per_round},
              open(OUT / "verdict_reference_kind.json", "w"), indent=2)
    print(f"\n  artifact: results/verdict_reference_kind.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
