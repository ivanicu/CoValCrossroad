"""R382 — three gates carry a regex R381 called stale. Does any of them match anything?

R381 separated three regexes out of its path census, on the ground that `glob` is the wrong test for
a pattern matched against text, and named the right question: **does the pattern match anything in
the documents it is applied to?** This answers it.

⛔ ONE OF THE THREE IS NOT A LINK PATTERN AT ALL, and saying so first is the honest way to start.
   `seed_filter_is_disclosed` carries `len\\(raters\\)\\s*\\+\\s*1\\)\\s*//\\s*2|>=\\s*thr\\b`. It was
   flagged by R381 because it contains `//` -- INTEGER DIVISION -- and R381's `path_shaped` accepts
   any literal containing a slash. So the "stale link format" class is TWO, not three, and I am
   correcting my own count before using it. R381's number was right about what it measured and
   wrong as a description of what it found, which is the fourth distinct false-positive class that
   census has produced.

⛔ AND I WILL NOT INFER EACH PATTERN'S TARGET, because inferring it is where a wrong answer would
   come from. Reading the source says `CITE` is applied to README lines and `FILTER` to round
   sources -- but a claim resting on my reading of three call sites is a claim resting on me. Every
   pattern is instead run against EVERY corpus it could possibly be applied to. If a pattern matches
   zero in all of them, it matches zero wherever it is pointed, and no inference about intent is
   needed. That is a SUPERSET of the intended target, so a zero here is strictly stronger.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES. Each pattern is
   free to match many lines; two of them contain `r(\\d+)_` and `r8[89]_` fragments that plainly
   COULD match text in a corpus full of round ids. Whether they do is the measurement, and the
   negative control below establishes that zero is a value this counter can return at all.

ESTIMAND        for each flagged pattern, the number of matches in each corpus:
                  (a) README.md          (b) every arc README      (c) every round run.py
                and whether the total is zero.

IDENTIFICATION  Exact -- `re.findall` over a fixed corpus is an enumeration. NOT identified: whether
                a zero CAUSES its gate's failure. R380 needed a whole round with a disarm proof to
                establish that for one gate; this measures the pattern, not the gate.

SCOPE           population: 3 patterns x 3 corpora · instrument: the gates' OWN compiled patterns,
                extracted from source rather than retyped · baseline: a pattern from a GREEN gate ·
                regime: HEAD.

WORLDS
  W-PATTERNS-DEAD   both link patterns match ZERO across every corpus. Their gates rule on an empty
                    set, which is the same shape R380 found in the donor gate's GATE 2, and the
                    repair is to the pattern rather than to the corpus.
  W-PATTERNS-LIVE   they match. Then R381's "stale link format" reading is refuted, the gates fail
                    for some other reason, and the next search is elsewhere.
  W-MIXED           one dead, one live -- and then they are separate repairs, not a class.

PREDICTION MATRIX
  W-PATTERNS-DEAD -> total matches == 0 for both link patterns
  W-PATTERNS-LIVE -> total > 0 for both
  W-MIXED         -> exactly one at zero

PRE-REGISTERED KILL -- conditional on the controls, never on a count alone.
    if positive_control_matches_many and negative_control_matches_zero:
        d = number of LINK patterns (2) whose total across all corpora is 0
        if d == 2   -> W-PATTERNS-DEAD
        elif d == 0 -> W-PATTERNS-LIVE
        else        -> W-MIXED, and which is which is named
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.
    The third pattern is reported in the table and EXCLUDED from d, because it is not a link
    pattern and counting it would inflate the numerator with a mis-classification of my own making.

CONTROLS
  POSITIVE   a pattern lifted from a GREEN gate (`round_links_resolve`, exit 0) must match MANY
             lines of README.md. A counter that returns zero for everything would otherwise make
             every zero below meaningless. The gate is green, so its pattern demonstrably works.
  NEGATIVE   an impossible token (`zzq_no_such_token_zzq`) must match ZERO in every corpus. Both
             directions, because a counter that returned a large number for everything would pass
             the positive control and prove nothing.
  EXTRACTED  the patterns are read out of the gates' source by `ast`, never retyped here. A retyped
             regex is a different regex, and this campaign has already published one number from a
             pattern that differed from the one in the code.
  CORPUS     the size of each corpus is printed. A zero from an empty corpus is silence, so an
             empty corpus exits 2.

MULTIPLICITY    3 patterns x 3 corpora = 9 cells, all printed. No threshold on a p-value anywhere.
SEEDS           none -- regex matching is deterministic.
ARTIFACT        results/r382_pattern_matches.json with the source hash.

IMPOSSIBLE HERE
  whether a zero CAUSES its gate to fail  -- that is R380's shape of round, with a disarm proof.
  patterns built at runtime               -- only module-level compiled patterns are extracted.
  a second release                        -- one release.

EXIT
    0  controls hold and the patterns are classified
    1  a control misbehaved -- UNVERIFIED
    2  a corpus is empty -- never a silent pass
"""
from __future__ import annotations
import ast
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
ASSUR = ROOT / "assurance"
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

# gate -> the NAME of the module-level pattern to lift. Names, not the patterns themselves:
# the regex is read out of the source so this round cannot measure a retyped variant.
TARGETS = {
    "donor_numbers_carry_their_draw_scope": ("SCOPE", "link"),
    "synthesis_cites_recent_work":          ("CITE", "link"),
    "seed_filter_is_disclosed":             ("FILTER", "not-a-link"),
}
POS_GATE, POS_NAME = "round_links_resolve", None      # any pattern in a green gate that matches many
NEG = r"zzq_no_such_token_zzq"


def lift(gate: str, name: str):
    """Read a module-level `NAME = re.compile(r"...")` out of source. Never retyped."""
    try:
        tree = ast.parse((ASSUR / f"{gate}.py").read_text())
    except Exception:
        return None
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 \
                and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name \
                and isinstance(n.value, ast.Call):
            for a in n.value.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    return a.value
    return None


def lift_any(gate: str):
    """The first module-level compiled pattern in a gate — used for the positive control."""
    try:
        tree = ast.parse((ASSUR / f"{gate}.py").read_text())
    except Exception:
        return None, None
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 \
                and isinstance(n.targets[0], ast.Name) and isinstance(n.value, ast.Call) \
                and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "compile":
            for a in n.value.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    return n.targets[0].id, a.value
    return None, None


def main() -> int:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R382 · does the pattern match anything?   HEAD {head}\n")
    print(f"  ⛔ FIRST, A CORRECTION TO MY OWN COUNT. R381 reported THREE red gates carrying a")
    print(f"     'stale link format' regex. `seed_filter_is_disclosed`'s pattern is")
    print(f"     `len(raters)+1)//2 | >= thr` — it was flagged because `//` is INTEGER DIVISION and")
    print(f"     R381's path filter accepts any literal with a slash. The link class is TWO.")
    print(f"     It is still measured below, and excluded from the count.\n")

    # ⛔ THE ROUND'S OWN SOURCE IS IN THE CORPUS IT MEASURES, and the negative control caught it:
    #   the impossible token `zzq_no_such_token_zzq` matched TWICE, both times inside THIS FILE
    #   (the docstring and the NEG constant). That is not a quirk of the control -- it would have
    #   inflated all three pattern counts too, because this round PRINTS the patterns it measures.
    #   A round whose own text joins the corpus must exclude itself, which is R376's scaffolding
    #   lesson at a fourth level: the probe is never the population.
    def not_self(p):
        return HERE not in p.parents and p != SELF

    corpora = {
        "README.md": [ROOT / "README.md"],
        "arc READMEs": [p for p in sorted(ROOT.glob("E0*/A*/README.md")) if not_self(p)],
        "round sources": [p for p in sorted(ROOT.glob("E0*/A*/R*/run.py")) if not_self(p)],
    }
    text = {}
    for k, ps in corpora.items():
        blobs = []
        for p in ps:
            try:
                blobs.append(p.read_text())
            except Exception:
                continue
        text[k] = "\n".join(blobs)
        if not text[k]:
            print(f"  UNRUNNABLE: corpus `{k}` is empty. A zero from an empty corpus is silence. "
                  f"Exit 2, never 0.")
            return 2
    print(f"  CORPORA   " + " · ".join(f"{k}: {len(corpora[k])} file(s), "
                                       f"{len(text[k]):,} chars" for k in corpora))

    # ---- CONTROLS ------------------------------------------------------------------------------
    pn, pp = lift_any(POS_GATE)
    pos_counts = {k: len(re.findall(pp, text[k])) for k in text} if pp else {}
    pos_ok = bool(pp) and pos_counts.get("README.md", 0) > 20
    neg_counts = {k: len(re.findall(NEG, text[k])) for k in text}
    neg_ok = all(v == 0 for v in neg_counts.values())
    print(f"\n  CONTROLS")
    print(f"    POSITIVE  `{POS_GATE}.{pn}` (that gate exits 0) matches "
          f"{pos_counts.get('README.md')} lines of README.md  {'PASS' if pos_ok else 'FAIL'}")
    print(f"    NEGATIVE  an impossible token matches {neg_counts} — zero is attainable  "
          f"{'PASS' if neg_ok else 'FAIL'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the counter is blind in one direction. Exit 1."); return 1

    # ---- the three patterns --------------------------------------------------------------------
    print(f"\n  THE PATTERNS — lifted from source by `ast`, never retyped")
    print(f"    {'gate':<38}{'name':>8}{'class':>12}" +
          "".join(f"{k[:13]:>15}" for k in corpora) + f"{'total':>8}")
    ROWS = {}
    for gate, (name, cls) in TARGETS.items():
        pat = lift(gate, name)
        if pat is None:
            print(f"    {gate:<38}{name:>8}   NOT FOUND in source"); continue
        counts = {}
        for k in text:
            try:
                counts[k] = len(re.findall(pat, text[k]))
            except re.error:
                counts[k] = -1
        tot = sum(v for v in counts.values() if v >= 0)
        ROWS[gate] = dict(name=name, cls=cls, pattern=pat, counts=counts, total=tot)
        print(f"    {gate:<38}{name:>8}{cls:>12}" +
              "".join(f"{counts[k]:>15}" for k in corpora) + f"{tot:>8}")
    for g in ROWS:
        print(f"      {g}.{ROWS[g]['name']} = {ROWS[g]['pattern']!r}")

    links = {g: r for g, r in ROWS.items() if r["cls"] == "link"}
    dead = sorted(g for g, r in links.items() if r["total"] == 0)
    live = sorted(g for g, r in links.items() if r["total"] > 0)

    # ---- VERDICT -------------------------------------------------------------------------------
    print()
    if len(dead) == len(links) and links:
        print(f"  W-PATTERNS-DEAD — both link patterns match ZERO across README.md, every arc")
        print(f"  README and all {len(corpora['round sources'])} round sources:")
        for g in dead:
            print(f"    · {g}.{ROWS[g]['name']}  {ROWS[g]['pattern']!r}")
        print(f"  Their gates rule on an EMPTY SET — the same shape R380 found in the donor gate's")
        print(f"  GATE 2 — and the repair is to the PATTERN, not to the corpus.")
        v = "W_PATTERNS_DEAD"
    elif not dead:
        print(f"  W-PATTERNS-LIVE — every link pattern matches something "
              f"({', '.join(g + '=' + str(links[g]['total']) for g in links)}).")
        print(f"  R381's `stale link format` reading is REFUTED: these gates do not fail for want")
        print(f"  of a matchable pattern, and the next search is elsewhere.")
        v = "W_PATTERNS_LIVE"
    else:
        print(f"  W-MIXED — dead: {dead}; live: {live}. They are SEPARATE repairs, not a class,")
        print(f"  and calling them one would be the grouping error R379 already cost a round.")
        v = "W_MIXED"

    nl = [g for g, r in ROWS.items() if r["cls"] == "not-a-link"]
    if nl:
        g = nl[0]
        print(f"\n  ⚠ THE EXCLUDED ONE, reported rather than dropped: {g}.{ROWS[g]['name']} matches")
        print(f"    {ROWS[g]['total']} across all three corpora. It is not a link pattern, so it")
        print(f"    carries no weight in the verdict — but hiding a number because it does not fit")
        print(f"    the class is how a class becomes unfalsifiable.")

    print(f"\n  ⚠ SCOPE: this measured the PATTERN, never the GATE. Whether a zero CAUSES a gate to")
    print(f"    fail is R380's shape of round, and it needed a disarm proof at the end.")

    art = dict(stamp(str(SELF)), head=head,
               corpora={k: dict(files=len(corpora[k]), chars=len(text[k])) for k in corpora},
               rows=ROWS, dead=dead, live=live,
               controls=dict(positive_gate=POS_GATE, positive_name=pn,
                             positive_counts=pos_counts, positive_ok=pos_ok,
                             negative_counts=neg_counts, negative_ok=neg_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r382_pattern_matches.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
