#!/usr/bin/env python3
"""R484 — how many detectors in `assurance/` match the repository's own prose about them?

WHY. R382 was reported as applying the seed filter. It does not: its only match sat inside a
`print()` that QUOTES the regex while discussing it, and the round is named
`does_the_pattern_match_anything`. I was one line from registering a filter application that never
happened. That fix was local. **This asks whether the flaw is.**

⚠ A STATIC SCREEN IS NOT THE ANSWER, AND MY FIRST ONE WAS WRONG. Counting gates that "read files and
pattern-match" gave 33, of which 3 strip strings -> "30 exposed". That conflates two unlike things:
a gate searching a MARKDOWN file for a documentation pattern is CORRECTLY matching prose, and only a
gate searching PYTHON SOURCE for a CODE-shaped pattern can have R382's flaw. The screen's unit was
"reads a file"; the claim's unit is "matches code-shaped text inside a string literal".

ESTIMAND
    For each regex literal compiled in `assurance/*.py`, over the corpus of round `run.py` files:
        IN_STRING = matches whose character span lies inside a string literal or comment
        IN_CODE   = matches outside them
    A detector is EXPOSED iff IN_STRING > 0 -- it has at least one match that is text ABOUT code
    rather than code. ⭐ This is measured on the real corpus, not inferred from whether the gate
    happens to call `ast`.

IDENTIFICATION
    Identified for every pattern written as a `re.compile(r"...")` literal. ⚠ Patterns built at
    runtime from f-strings or variables are NOT extractable and are reported as UNSEEN rather than
    as clean -- an unmeasured pattern is not an acquitted one.

SCOPE
    population  every `E*/A*/R*/run.py` in the repo, counted in-run.
    instrument  `ast`-based string/comment span extraction; the same routine that repaired
                `seed_filter_is_disclosed`, so the two results are commensurable.
    baseline    IN_STRING == 0 is the clean state.
    regime      Python source only; markdown targets are out of scope BY CONSTRUCTION and named.

WORLDS
    A  LOCAL     only the already-fixed gate is exposed -> R382 was a one-off and the repair is done.
    B  SYSTEMIC  several gates are exposed -> a self-documenting repository systematically feeds its
                 own checks, and every regex detector here needs the same treatment.
    C  INERT     patterns match inside strings but never in a round that changes a verdict -> the
                 flaw exists and costs nothing, which is a different repair (document, don't fix).

PREDICTION MATRIX
                 exposed gates    what it licenses
    A  local          1 (fixed)   close the thread
    B  systemic       >1          a shared `_code_only` helper, applied and controlled per gate
    C  inert          >1 but no verdict changes    record it; do not churn 30 files

PRE-REGISTERED KILL
    if positive_control_fires and negative_is_null:
        A if exposed <= 1 ; B if exposed > 1 and any exposed gate's match set changes its verdict ;
        C otherwise
    else:
        UNVERIFIED

CONTROLS
    POSITIVE   the OLD `seed_filter_is_disclosed` pattern (`len(raters)+1)//2|>= thr`) MUST show
               IN_STRING >= 1, because R382 is a known real instance. An instrument that cannot
               re-find the case that motivated it is not measuring that case.
    NEGATIVE   a pattern that cannot occur in prose -- `\bdef _code_only\b` restricted to the round
               corpus -- must show IN_STRING == 0.
    g=0        a synthetic file whose ONLY occurrence is inside a docstring must be classified
               IN_STRING, and one whose only occurrence is executable must be IN_CODE. This is what
               makes the positive able to fail.
    UNSEEN     patterns not extractable as literals are counted and named, never folded into clean.

MULTIPLICITY  every extracted pattern reported, exposed or not.

ARTIFACT  results/r484_prose_matching.json

IMPOSSIBLE HERE, NAMED
    "does the exposure change any committed verdict" -- would require re-running each gate with and
        without stripping and diffing its FINDING lines; several gates are minutes-long, so this
        round reports EXPOSURE and explicitly does not claim consequence.
"""
import ast, json, pathlib, re, sys
ROOT = pathlib.Path(".")
OUT = ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/R484_how_many_detectors_read_their_own_prose/results"

def string_spans(src: str):
    """-> list of (start,end) char spans covered by string literals or comments."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    lines = src.splitlines(keepends=True)
    off, tot = [], 0
    for l in lines:
        off.append(tot); tot += len(l)
    pos = lambda r, c: off[r-1] + c if 0 < r <= len(off) else len(src)
    spans = [(pos(n.lineno, n.col_offset), pos(n.end_lineno, n.end_col_offset))
             for n in ast.walk(tree)
             if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.end_lineno]
    spans += [(m.start(), m.end()) for m in re.finditer(r"#[^\n]*", src)]
    return spans

ROUNDS = sorted(ROOT.glob("E*/A*/R*/run.py"))
SRC = {p: p.read_text() for p in ROUNDS}
SPANS = {p: string_spans(s) for p, s in SRC.items()}
print(f"  corpus: {len(ROUNDS)} round run.py files")

PAT = re.compile(r"re\.compile\(\s*r?(\"\"\".*?\"\"\"|'''.*?'''|\"(?:[^\"\\\\]|\\\\.)*\"|'(?:[^'\\\\]|\\\\.)*')",
                 re.S)
def extract(gate: pathlib.Path):
    out = []
    for m in PAT.finditer(gate.read_text()):
        lit = m.group(1)
        try:
            out.append(ast.literal_eval(lit))
        except Exception:
            pass
    return out

def measure(pattern: str):
    try:
        rx = re.compile(pattern)
    except re.error:
        return None
    ins = cod = 0
    for p, s in SRC.items():
        sp = SPANS[p]
        if sp is None: continue
        for m in rx.finditer(s):
            if any(a <= m.start() and m.end() <= b for a, b in sp): ins += 1
            else: cod += 1
    return ins, cod

# ---- controls ---------------------------------------------------------------
POS = r"len\(raters\)\s*\+\s*1\)\s*//\s*2|>=\s*thr\b"      # the OLD seed pattern; R382 is real
pos = measure(POS)
NEG = r"\bdef _code_only\b"
neg = measure(NEG)
g0_src = 'x = 1\n"""\nlen(raters)+1)//2\n"""\n'
g0_spans = string_spans(g0_src)
g0m = list(re.finditer(POS, g0_src))
g0_ok = bool(g0m) and all(any(a <= m.start() and m.end() <= b for a, b in g0_spans) for m in g0m)
g0b_src = 'thr = 3\nif n >= thr:\n    pass\n'
g0b = list(re.finditer(POS, g0b_src))
g0b_spans = string_spans(g0b_src)
g0b_ok = bool(g0b) and not any(any(a <= m.start() and m.end() <= b for a, b in g0b_spans) for m in g0b)
print(f"\n  POSITIVE  old seed pattern: IN_STRING={pos[0]}  IN_CODE={pos[1]}   "
      f"{'PASS — re-finds the R382 case' if pos[0] >= 1 else '⛔ FAIL'}")
print(f"  NEGATIVE  a pattern that cannot occur in prose: IN_STRING={neg[0]}   "
      f"{'PASS' if neg[0] == 0 else '⛔ FAIL'}")
print(f"  g=0       occurrence ONLY in a docstring -> IN_STRING: {g0_ok}; "
      f"only executable -> IN_CODE: {g0b_ok}")

# ---- the census -------------------------------------------------------------
gates = sorted(p for p in ROOT.glob("assurance/*.py")
               if not p.stem.startswith(("_", "apply_")) and p.stem not in
               {"run_all", "DEFECTS", "HEADLINES", "manifest", "pueue_wait", "generate_round_index"})
rows, unseen = [], []
for g in gates:
    pats = extract(g)
    if not pats:
        unseen.append(g.stem); continue
    tot_in = tot_cod = 0
    for pt in pats:
        r = measure(pt)
        if r: tot_in += r[0]; tot_cod += r[1]
    rows.append({"gate": g.stem, "patterns": len(pats), "in_string": tot_in, "in_code": tot_cod})

# ⛔⛔ THE EXTRACTOR IS UNFIT AND THE CENSUS IS VOID. Two independent defects, both measured:
#  ① IT CANNOT TELL A DETECTION PATTERN FROM AN INCIDENTAL ONE. Eight unrelated gates reported an
#     identical 296/66 because they all contain the same boilerplate
#     `smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip` -- a throwaway-round filter, not what
#     any of them detects. Identical counts across unrelated gates is the tell.
#  ② IT MANGLES IMPLICITLY-CONCATENATED LITERALS. Python joins adjacent string literals, so a
#     multi-line pattern is several literals; the extractor captured only the FIRST, yielding
#     `'model[- ]scored|model gold|gold proxy|proxy world|proxy-world|'` -- a TRAILING `|`, an empty
#     alternative that matches at every position. Hence 4,066,094 "in-string matches".
# Neither is fixable by tightening the regex: WHICH pattern is a gate's detection pattern is a
# semantic judgement, not a lexical one. The estimand is not identified by static extraction.
UNFIT = True
_bad = [r for r in rows if r["in_string"] > 100000]
print(f"\n  ⛔ INSTRUMENT UNFIT — census void.")
print(f"    ① identical counts across unrelated gates (shared boilerplate, not detection patterns)")
print(f"    ② {len(_bad)} gate(s) show >100k matches, from a captured FRAGMENT ending in `|`")
print(f"    -> WHICH pattern detects is semantic, not lexical. Static extraction cannot identify it.")
exposed = [r for r in rows if r["in_string"] > 0]
print(f"\n  ── EXPOSURE over {len(ROUNDS)} round files, per gate with extractable patterns ──")
print(f"    {'gate':<46} {'pats':>4} {'IN_STRING':>10} {'IN_CODE':>8}")
for r in sorted(rows, key=lambda x: -x["in_string"]):
    if r["in_string"]:
        print(f"    {r['gate']:<46} {r['patterns']:>4} {r['in_string']:>10} {r['in_code']:>8}")
print(f"\n  gates with extractable patterns : {len(rows)}")
print(f"  EXPOSED (>=1 match inside a string/comment) : {len(exposed)}")
print(f"  ⚠ UNSEEN (patterns not literal, not measurable, NOT clean) : {len(unseen)}")

# ⭐ The CONTROLS all pass -- the span logic works, and the positive control re-finds R382. What
# fails is EXTRACTION, upstream of them. A control saturating the measurement stage says nothing
# about a defect in the sampling stage, which is why controls passing is not a verdict.
ok = pos and pos[0] >= 1 and neg and neg[0] == 0 and g0_ok and g0b_ok and not UNFIT
verdict = "MEASURED" if ok else "UNVERIFIED"
world = ("A (LOCAL — only the already-repaired gate)" if ok and len(exposed) <= 1
         else "UNFIT — the span measurement is sound and the PATTERN EXTRACTION is not; "
              "no claim about how many detectors read their own prose is licensed by this round")
print(f"\n  VERDICT {verdict}\n  world: {world}")
OUT.mkdir(parents=True, exist_ok=True)
json.dump({"n_rounds": len(ROUNDS), "rows": rows, "unseen": unseen,
           "n_exposed": len(exposed), "positive": pos, "negative": neg,
           "verdict": verdict, "world": world}, open(OUT/"r484_prose_matching.json", "w"), indent=2)
sys.exit(0 if ok else 2)
