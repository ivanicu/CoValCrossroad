#!/usr/bin/env python3
"""
R640 -- of the seven harnesses, how many actually CLASSIFY a run as failed?

CHECK #241: "SIX OF THE SEVEN PREDATE THIS ARC" IS FALSE -- ALL SEVEN ARE IN A24.
  ⛔ What I meant was "predate the R630s". "This arc" is A24, which contains every one of them.
     Twenty-seventh, and the same class as the last four: a claim about my own corpus written from
     narrative position rather than from the object.
  ⛔ "one predicate and seven call sites" -- the FOURTH size/cost claim in five rounds, and this
     round measures it rather than repeating it.

⭐ WHY THE COUNT MATTERS AND IS NOT BOOKKEEPING. R639 established the prohibition is needed wherever
   a harness turns a non-zero exit into a FAILURE. A harness that runs rounds for TIMING or for
   CONTENT never forms that judgement, so editing it changes nothing. The repair's real size is the
   number that classify, and asserting seven without checking is how a cost claim becomes a fourth
   uncomputed one.

ESTIMAND        n_classify = of the 7 harnesses, those whose source turns a returncode into a
                failure/success JUDGEMENT that reaches output or a branch.
IDENTIFICATION  Exact by source read on three markers: (i) the returncode is compared, (ii) the
                result is bound to a failure-named variable, (iii) that variable reaches a print or
                a branch. ⚠ A harness could classify without any marker -- the classification could
                be implicit in a downstream consumer -- so n_classify is a LOWER bound.
SCOPE           population : the 7 harnesses from R639, self excluded
                instrument : marker scan over each harness's source
                             instrument unit = A SOURCE MARKER
                             claim unit      = A HARNESS THAT CLASSIFIES. NOT equal; a marker can
                             appear in a docstring. Docstrings are stripped before scanning.
                baseline   : my claim of "seven call sites"
                regime     : this repository at this sha
WORLDS          A ALL SEVEN CLASSIFY: the repair is seven sites, as claimed.
                B SOME CLASSIFY: the repair is smaller than claimed, and the rest are no-ops.
                C ONLY R636: the repair is local after all, and both "only one harness" (wrong the
                  other way) and "seven call sites" were wrong -- in opposite directions, which is
                  the pattern this arc keeps producing.
KILL            pre-registered: n_classify is the repair size, whatever it is; C fires if it is 1.
POSITIVE CTRL   R636 must classify -- it computes `failed` and branches on it. Fails at g=0: a
                harness with no returncode comparison at all must not be counted.
NEGATIVE CTRL   a marker appearing ONLY in a docstring must not count -- docstrings are stripped
                and the strip is verified by checking R636 still classifies after stripping.
PLACEBO         a marker no harness uses -> 0.
SEEDS           n/a, deterministic.
MULTIPLICITY    7 harnesses x 3 markers + 4 controls. Full per-harness table printed.
ARTIFACT        results/how_many_classify.json
IMPOSSIBLE      classification could be implicit in a consumer this scan never reads, so
                n_classify is a LOWER bound on the repair size, not an upper one.
"""
from __future__ import annotations
import ast, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
SELF = pathlib.Path(__file__).resolve().parent.name

RC_COMPARE = re.compile(r"returncode\s*(?:==|!=|>|<|>=|<=)|\.returncode\s*\)|check=True")
FAIL_VAR = re.compile(r"\bfail\w*\b|\bbroken\b|\bunrunnable\b", re.I)
REACHES = re.compile(r"(?:print|world|verdict|len)\s*\([^)]*fail|fail\w*\s*(?:>=|>|==)\s*|"
                     r"len\(fail\w*\)")


def strip_docstrings(src):
    """Remove every docstring so a marker in prose cannot count."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return src
    spans = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            b = getattr(node, "body", None)
            if b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant) \
               and isinstance(b[0].value.value, str):
                spans.append((b[0].lineno, b[0].end_lineno))
    lines = src.split("\n")
    for a, z in spans:
        for i in range(a - 1, min(z, len(lines))):
            lines[i] = ""
    return "\n".join(lines)


def main():
    src639 = A24 / "R639_is_the_world_live" / "results" / "is_the_world_live.json"
    if not src639.exists():
        print("UNRUNNABLE: R639 artifact absent. Exit 2, never 0."); return 2
    harnesses = [h for h in json.loads(src639.read_text())["harnesses"] if h != SELF]
    print(f"  harnesses from R639: {len(harnesses)}")

    rows = []
    for h in harnesses:
        raw = (A24 / h / "run.py").read_text(errors="ignore")
        code = strip_docstrings(raw)
        m = {"rc_compare": bool(RC_COMPARE.search(code)),
             "fail_var": bool(FAIL_VAR.search(code)),
             "reaches_output": bool(REACHES.search(code))}
        classifies = m["rc_compare"] and m["fail_var"] and m["reaches_output"]
        rows.append({"harness": h, **m, "classifies": classifies})

    print(f"\n─── DOES EACH HARNESS TURN A RETURNCODE INTO A JUDGEMENT? ───")
    print(f"  {'harness':<48} {'rc?':>4} {'fail?':>6} {'out?':>5}  CLASSIFIES")
    for r in rows:
        print(f"  {r['harness'][:48]:<48} {str(r['rc_compare']):>4} "
              f"{str(r['fail_var']):>6} {str(r['reaches_output']):>5}  "
              f"{'YES' if r['classifies'] else 'no'}")
    n_cls = sum(1 for r in rows if r["classifies"])

    print(f"\n─── CONTROLS ───")
    r636 = next((r for r in rows if r["harness"].startswith("R636")), None)
    pos = bool(r636 and r636["classifies"])
    print(f"  POSITIVE  R636, which computes `failed` and branches on it, classifies -> "
          f"{'PASS' if pos else '⛔ FAIL'}")
    norc = [r["harness"] for r in rows if not r["rc_compare"]]
    print(f"  g=0       {len(norc)} harness(es) never compare a returncode and are not counted -> "
          f"{'PASS' if norc else '⚠ every harness compares one; the marker cannot exclude'}")
    doc_only = strip_docstrings('"""fail failed failure"""\nx = 1\n')
    neg = not FAIL_VAR.search(doc_only)
    print(f"  NEGATIVE  a marker appearing only in a docstring is stripped -> "
          f"{'PASS' if neg else '⛔ FAIL'}")
    plc = sum(1 for r in rows if re.search("zzq_nomarker", (A24 / r["harness"] / "run.py").read_text(errors="ignore")))
    print(f"  PLACEBO   a marker no harness uses -> {plc} -> {'PASS' if plc == 0 else '⛔ FAIL'}")
    controls_ok = pos and neg and plc == 0

    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif n_cls == 1:
        world = (f"C ONLY R636 — exactly one harness turns a returncode into a judgement. The "
                 f"repair is local after all, and BOTH my claims were wrong in OPPOSITE "
                 f"directions: 'only one harness runs rounds' (there are 7) and 'seven call "
                 f"sites' (there is 1).")
    elif n_cls == len(rows):
        world = f"A ALL {n_cls} CLASSIFY — the repair is {n_cls} sites, as claimed."
    else:
        world = (f"B {n_cls} OF {len(rows)} CLASSIFY — the repair is {n_cls} site(s), not "
                 f"{len(rows)}. The other {len(rows)-n_cls} run rounds without ever forming a "
                 f"failure judgement, so editing them would change nothing.")
    print(f"  {world}")
    print(f"\n  ⚠ LOWER BOUND: classification could be implicit in a consumer this scan never "
          f"reads, so n_classify bounds the repair from BELOW, not above.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "how_many_classify.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "n_harnesses": len(rows),
        "n_classify": n_cls, "rows": rows,
        "check241": ("'six of the seven predate this arc' is false -- all seven are IN A24; and "
                     "'one predicate and seven call sites' was the fourth size claim in five rounds"),
        "impossible": "n_classify is a lower bound; implicit classification is invisible here",
    }, indent=2))
    print(f"\n  wrote {OUT / 'how_many_classify.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
