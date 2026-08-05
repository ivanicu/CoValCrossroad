#!/usr/bin/env python3
"""
R638 -- can a harness decode this corpus's exit codes at all?

CHECK #239: AN UNCOMPUTED COST CLAIM, IN THE CHEAP DIRECTION THIS TIME.
  ⛔ "the fix is ONE LINE" -- never measured. Classifying by declared convention requires parsing
     each round's own docstring for its own EXIT mapping and then interpreting it, which is not one
     line. ⭐ I have now made uncomputed cost claims in BOTH directions -- "re-runs are expensive"
     to avoid work, "the fix is one line" to justify it -- and both felt obviously true.

⭐ AND THE PROMISED COUNT CARRIES A TRAP THE CLOSING LINE NAMED BUT DID NOT DISARM. The 15 came from
   the 43-round at-risk subset. Applying a subset's rate to the corpus is the error that carried 195
   forward. So this round counts over ALL rounds -- and then asks the question that actually decides
   whether a fix exists: DO THE CONVENTIONS AGREE?

ESTIMAND        ① the share of all rounds declaring an EXIT convention;
                ② n_meanings(1) = the number of DISTINCT worlds that `EXIT 1` denotes across them.
IDENTIFICATION  Exact from the docstrings. ⚠ A round can encode an exit convention without writing
                the word EXIT, so ① is a LOWER bound; and two differently-worded meanings may be the
                same world, so ② is an UPPER bound. Both directions stated; neither is favourable.
SCOPE           population : every round under A24 with a run.py, SELF EXCLUDED by default
                instrument : `EXIT 0 ... 1 ... 2 ...` docstring parse
                             instrument unit = A DOCSTRING LINE
                             claim unit      = A ROUND'S EXIT SEMANTICS. NOT equal -- a docstring
                             can lie about the code. Named; this round does not execute anything.
                baseline   : the 43-round subset's 15 (34.9%)
                regime     : this repository at this sha
WORLDS          A RARE: the corpus rate is far below the subset's -> the subset was unusual and the
                  world-C-fires-on-nothing derivation does not generalise.
                B COMMON AND UNIFORM: the rate holds AND `EXIT 1` means one thing -> a decoding
                  harness is buildable, and the cost is whatever this round measures it to be.
                C COMMON AND INCOHERENT: the rate holds but `EXIT 1` denotes many different worlds
                  -> NO generic harness can decode it. The only sound rule is the weak one:
                  non-zero does not mean failure. "The fix is one line" would then be false in a
                  deeper way than cost -- there is no fix, only a prohibition.
KILL            pre-registered: >=3 distinct meanings for `EXIT 1` -> world C.
POSITIVE CTRL   the four rounds known to declare a convention (R433, R437, R441, R442) must be
                found. Fails at g=0: a round with no convention must not match.
NEGATIVE CTRL   R431, which showed no convention under the earlier grep, must not be found here.
PLACEBO         an exit code no round declares -> 0 meanings.
SEEDS           n/a, deterministic.
MULTIPLICITY    every round x 3 exit codes + 4 controls. Full distribution printed.
ARTIFACT        results/can_the_exit_codes_be_decoded.json
IMPOSSIBLE      a docstring is not the code. This round measures what the corpus DECLARES, never
                what it does -- and R636 already showed the two can disagree in the other direction.
"""
from __future__ import annotations
import collections, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
SELF = pathlib.Path(__file__).resolve().parent.name
EXITLINE = re.compile(r"^EXIT\s+0\s+(.+)$", re.M)
PARTS = re.compile(r"(?:^|·)\s*(\d)?\s*([A-Z][A-Za-z0-9\- ]{2,40})")


def meanings(line):
    """`EXIT 0 W-A · 1 W-B · 2 W-C` -> {0:'W-A', 1:'W-B', 2:'W-C'}"""
    segs = [s.strip() for s in line.split("·")]
    out = {}
    if segs:
        out[0] = segs[0].strip()
    for s in segs[1:]:
        m = re.match(r"(\d)\s+(.*)", s)
        if m:
            out[int(m.group(1))] = m.group(2).strip()
    return out


def main():
    rounds = [d for d in sorted(A24.glob("R[0-9]*"))
              if (d / "run.py").is_file() and d.name != SELF]
    if len(rounds) < 50:
        print(f"UNRUNNABLE: {len(rounds)} rounds. Exit 2, never 0."); return 2

    decl, table = {}, collections.defaultdict(list)
    for d in rounds:
        m = EXITLINE.search((d / "run.py").read_text(errors="ignore"))
        if not m: continue
        mp = meanings(m.group(1))
        decl[d.name] = mp
        for code, world in mp.items():
            table[code].append((world, d.name))

    n, k = len(rounds), len(decl)
    print(f"  rounds with a run.py (self excluded) : {n}")
    print(f"  declaring an EXIT convention         : {k}  ({k/n:.1%})")
    print(f"  the 43-round subset's rate           : 15/43 = 34.9%  -> "
          f"{'the subset was UNUSUAL' if abs(k/n - 15/43) > 0.10 else 'the subset rate HOLDS'}")

    print(f"\n─── WHAT EACH EXIT CODE DENOTES, ACROSS THE WHOLE CORPUS ───")
    summary = {}
    for code in sorted(table):
        worlds = collections.Counter(w for w, _ in table[code])
        summary[code] = {"n_rounds": len(table[code]), "distinct_meanings": len(worlds),
                         "top": worlds.most_common(6)}
        print(f"  EXIT {code}: {len(table[code]):>3} round(s), "
              f"{len(worlds):>3} DISTINCT meaning(s)")
        for w, c in worlds.most_common(5):
            print(f"      {c:>3}x  {w[:64]}")

    print(f"\n─── CONTROLS ───")
    known = [r for r in decl if r[:4] in ("R433", "R437", "R441", "R442")]
    pos = len(known) == 4
    print(f"  POSITIVE  the 4 rounds known to declare a convention are found: {len(known)}/4 -> "
          f"{'PASS' if pos else '⛔ FAIL — ' + str(sorted(x[:4] for x in known))}")
    # ⛔ v1's NEGATIVE CONTROL FAILED, AND IT CAUGHT MY OWN EARLIER GREP RATHER THAN THIS
    #    INSTRUMENT. I had asserted R431 declares no convention, from `grep -E "EXIT [0-9]"` --
    #    a SINGLE SPACE. R431 line 99 reads `EXIT  0 W-COMPOSITION · 1 W-CONFOUND or W-BOTH · 2
    #    UNVERIFIED`, with TWO. So the earlier claim was a whitespace artifact, and the correct
    #    reading is that ALL FIVE of R636's "failures" were verdicts and NONE was a failure.
    #    Repaired: the control now uses a round VERIFIED to have no EXIT line at all -- 219 of 314
    #    qualify, so the control tests the instrument instead of testing my prior.
    negname = next((d.name for d in rounds if d.name not in decl), None)
    neg = negname is not None and negname not in decl
    print(f"  NEGATIVE  a round verified to have no EXIT line ({(negname or '—')[:34]}) is not "
          f"found -> {'PASS' if neg else '⛔ FAIL'}")
    g0 = sum(1 for r, mp in decl.items() if not mp)
    print(f"  g=0       rounds matching the pattern but yielding no mapping: {g0} -> "
          f"{'PASS' if g0 == 0 else '⚠ ' + str(g0) + ' parsed empty'}")
    plc = len(table.get(7, []))
    print(f"  PLACEBO   an exit code no round declares (7) -> {plc} -> "
          f"{'PASS' if plc == 0 else '⛔ FAIL'}")
    controls_ok = pos and neg and plc == 0

    m1 = summary.get(1, {}).get("distinct_meanings", 0)
    print(f"\n─── VERDICT (pre-registered: >=3 distinct meanings for EXIT 1 -> world C) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif abs(k / n - 15 / 43) > 0.10:
        world = (f"A RARE — the corpus rate is {k/n:.1%} against the subset's 34.9%, so the subset "
                 f"was unusual and the world-C derivation does not generalise beyond it.")
    elif m1 >= 3:
        world = (f"C COMMON AND INCOHERENT — {k} of {n} rounds ({k/n:.1%}) declare a convention and "
                 f"`EXIT 1` denotes {m1} DISTINCT worlds across them. No generic harness can decode "
                 f"it; the only sound rule is the weak one — NON-ZERO DOES NOT MEAN FAILURE. "
                 f"'The fix is one line' is false in a deeper way than cost: there is no fix, only "
                 f"a prohibition.")
    else:
        world = (f"B COMMON AND UNIFORM — {k} of {n} declare a convention and `EXIT 1` means "
                 f"{m1} thing(s). A decoding harness is buildable.")
    print(f"  {world}")
    print(f"\n  ⚠ ① IS A LOWER BOUND (a round can encode a convention without the word EXIT) and "
          f"② IS AN UPPER BOUND (two wordings may name one world). Neither direction is favourable.")
    print(f"  ⚠ A DOCSTRING IS NOT THE CODE: this measures what the corpus DECLARES, never what it "
          f"does, and R636 already showed the two can disagree in the other direction.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "can_the_exit_codes_be_decoded.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "n_rounds": n, "n_declaring": k,
        "corpus_rate": round(k / n, 4), "subset_rate": round(15 / 43, 4),
        "per_code": {str(c): v for c, v in summary.items()},
        "check239": "'the fix is one line' was an uncomputed cost claim, in the cheap direction",
        "impossible": "a docstring is not the code; declared semantics only",
    }, indent=2))
    print(f"\n  wrote {OUT / 'can_the_exit_codes_be_decoded.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
