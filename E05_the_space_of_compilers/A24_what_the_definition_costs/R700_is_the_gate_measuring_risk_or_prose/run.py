#!/usr/bin/env python3
"""
R700 -- is the quantifier gate measuring epistemic risk, or prose style?

CHECK #302 ON THE LAST NEXT LINE -- IT PROPOSED SELF-ADJUDICATION ON n=5.
  It asked me to read the five freeze REASONS -- which I wrote, about my own flags -- and classify
  them. The separable version runs the classification over EVERY flagged instance in the frozen
  corpus by a mechanical rule, which is what this round does.

ESTIMAND        of the quantifier instances this gate flags, what share are IDIOMATIC (an intensifier
                or fixed phrase) rather than a universal claim over our own work?
IDENTIFICATION  ⚠ the idiom list is CLOSED and hand-written; a construction I did not think of counts
                as a real universal. That biases the idiomatic share DOWN, so "mostly earned" is the
                conservative verdict, not the convenient one.
SCOPE           population : the README `## NEXT` sections the gate currently flags, plus the frozen
                             commit bodies it has flagged historically
                instrument : the gate's own QUANT/ARTIFACT/PROVENANCE regexes + a closed idiom list
                             instrument unit = A FLAGGED QUANTIFIER OCCURRENCE
                             claim unit      = AN UNEARNED FLAG
                             ⚠ NOT EQUAL -- an idiom flagged is still a flag a reader must resolve.
                baseline   : the gate's own flag set
                regime     : this repository at HEAD
WORLDS          A MOSTLY EARNED: idioms are a minority; the gate measures risk and its PASS is worth
                  what it claims.
                B PROSE STYLE: idioms dominate; the flag rate overstates the defect.
KILL            idiomatic share above 50% -> world B, say so plainly.
POSITIVE CTRL   `at all` classifies IDIOMATIC.
g=0             `every round in this arc` classifies NON-idiomatic.
NEGATIVE CTRL   text with no quantifier is not counted.
PLACEBO         run twice identical.
ARTIFACT        results/idiom_share.json
IMPOSSIBLE      whether I MEANT a universal is not in the text; the idiom list is a proxy for intent
                and is named as one.
"""
from __future__ import annotations
import importlib.util, json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
spec = importlib.util.spec_from_file_location(
    "gate", ROOT / "assurance" / "next_line_quantifiers_are_computed.py")
gate = importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)

# ⭐ CLOSED, HAND-WRITTEN, AND BIASING THE ANSWER TOWARD "EARNED" ON PURPOSE.
IDIOMS = [r"at all\b", r"not at all\b", r"after all\b", r"all in all\b", r"for all\b",
          r"all the same\b", r"once and for all\b", r"all but\b", r"never mind\b",
          r"all along\b", r"all told\b", r"in all\b", r"never the less\b", r"nevertheless\b",
          r"all of a sudden\b", r"none the less\b", r"nonetheless\b"]
IDIOM = re.compile("|".join(IDIOMS), re.I)


def flagged_spans(text):
    out = []
    for m in gate.QUANT.finditer(text):
        w = text[max(0, m.start() - gate.WINDOW): m.end() + gate.WINDOW]
        if gate.ARTIFACT.search(w) and not gate.PROVENANCE.search(w):
            lo = max(0, m.start() - 24)
            out.append({"word": m.group(0),
                        "context": " ".join(text[lo: m.end() + 24].split()),
                        "idiomatic": bool(IDIOM.search(text[max(0, m.start() - 12): m.end() + 12]))})
    return out


def main() -> int:
    print("─── CONTROLS (the idiom list is an instrument) ───")
    pos = bool(IDIOM.search("differ from their arms at all in the means"))
    print(f"  POSITIVE  `at all` classifies IDIOMATIC -> {pos} -> {'PASS' if pos else '⛔ FAIL'}")
    g0 = bool(IDIOM.search("every round in this arc reports"))
    print(f"  g=0       `every round in this arc` is NOT idiomatic -> {not g0} -> "
          f"{'PASS — the classifier returns both' if not g0 else '⛔ FAIL'}")
    neg = flagged_spans("this sentence has no quantifier and no artifact word")
    print(f"  NEGATIVE  text with no quantifier is not counted -> {len(neg)} -> "
          f"{'PASS' if not neg else '⛔ FAIL'}")
    plc = flagged_spans("x") == flagged_spans("x")
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = pos and not g0 and not neg and plc

    spans = []
    for name, sec in gate.readme_next_sections(ROOT):
        for s in flagged_spans(sec): spans.append({**s, "src": f"README:{name.split('_')[0]}"})
    fr = json.loads((ROOT / "assurance" / "KNOWN_QUANTIFIED_NEXT.json").read_text())
    for sha in fr["shas"]:
        b = subprocess.run(["git", "log", "-1", "--format=%B", sha], cwd=ROOT,
                           capture_output=True, text=True).stdout
        ms = list(re.finditer(r"^NEXT:\s*(.*?)(?:\n\n|\Z)", b, re.S | re.M))
        if not ms: continue
        for s in flagged_spans(" ".join(ms[-1].group(1).split())):
            spans.append({**s, "src": f"commit:{sha}"})

    if not spans:
        print("\nUNRUNNABLE: 0 flagged spans. Exit 2, never 0."); return 2

    from collections import Counter
    idio = [s for s in spans if s["idiomatic"]]
    share = len(idio) / len(spans)
    words = Counter(s["word"].lower() for s in spans)
    print(f"\n─── THE FLAG POPULATION (G3 — every flagged occurrence) ───")
    print(f"  flagged occurrences : {len(spans)}   (README {sum(1 for s in spans if s['src'].startswith('README'))}, "
          f"commit bodies {sum(1 for s in spans if s['src'].startswith('commit'))})")
    print(f"  ⭐ IDIOMATIC        : {len(idio)}  ({share:.1%})")
    for w, c in words.most_common(8): print(f"     {c:>4}×  `{w}`")
    print(f"  examples of idiomatic flags:")
    for s in idio[:5]: print(f"     …{s['context'][:82]}…")
    print(f"\n  registered A 22% [5,60] -> {share:.1%}: "
          f"{'INSIDE' if 0.05 <= share <= 0.60 else '⛔ OUTSIDE'}, error {share-0.22:+.1%}")
    b_ok = words.most_common(1)[0][0] == "all"
    print(f"  registered B (`all` is commonest) -> {words.most_common(1)[0][0]}: "
          f"{'HOLDS' if b_ok else '⛔ FAILS'}")
    dirn = share < 0.5
    print(f"  DIRECTIONAL idioms are a minority -> {'HOLDS' if dirn else '⛔ FAILS'}")
    killed = share > 0.5
    print(f"  pre-registered kill (idioms > 50%) -> "
          f"{'⭐ FIRES — the gate measures prose style' if killed else 'does not fire'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = (f"⭐⭐⭐ B PROSE STYLE — {share:.1%} of flagged occurrences are idiomatic. The gate's "
                 f"flag rate OVERSTATES the defect it was built for, and its PASS is worth less than "
                 f"it reads.")
    else:
        world = (f"⭐⭐ A MOSTLY EARNED — {len(idio)} of {len(spans)} flagged occurrences ({share:.1%}) "
                 f"are idiomatic; the rest are genuine universals over our own work. So the gate "
                 f"measures the risk it was built for, and its PASS means what it claims. ⚠ AND THE "
                 f"IDIOM LIST BIASES THIS TOWARD 'EARNED': it is closed and hand-written, so any "
                 f"construction I did not think of counts as a real universal — {share:.1%} is a "
                 f"FLOOR on the idiomatic share, not an estimate. ⚠ AND A FLAGGED IDIOM IS STILL A "
                 f"FLAG SOMEONE MUST RESOLVE: instrument unit is a flagged occurrence, claim unit is "
                 f"an unearned flag, and the cost of the false ones is paid in attention regardless.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(spans)} occurrences × {len(IDIOMS)} idiom patterns, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"idiom_share.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "n_flagged": len(spans), "n_idiomatic": len(idio), "idiomatic_share": share,
        "word_counts": dict(words), "idiomatic_examples": idio[:20],
        "kill_fired": killed, "directional_holds": dirn,
        "registered": "A 22% [5,60]; B `all` commonest; idioms a minority; kill above 50%",
        "limit": ("the idiom list is closed and hand-written, so the share is a FLOOR; and a flagged "
                  "idiom is still a flag a reader must resolve."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'idiom_share.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
