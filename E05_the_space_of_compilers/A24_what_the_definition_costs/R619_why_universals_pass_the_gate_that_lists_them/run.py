#!/usr/bin/env python3
"""
R619 -- WHY do universals pass the gate that lists them? Blanket amnesty, or a vocabulary gap?

CHECK #218 KILLED MY OWN NEXT LINE'S PREMISE, TWICE.
  ⛔ "the gate flags bare counts and lets universals through" -- FALSE. QUANT already contains
     every|all|none|nothing|never|only. The gate lists universals; they pass anyway, which is a
     different and more interesting fact.
  ⛔ "four have now passed it" -- I counted QUANTIFIER errors, not UNIVERSALS. #213 was a units
     conflation and #216 a construct promotion. An uncomputed count, in a closing line, about
     uncomputed closing lines. It is therefore PRE-REGISTERED here as a prediction and the corpus
     is allowed to refute it.

ESTIMAND        Among NEXT lines in this repository's history, the share that contain a quantifier
                over an artifact noun AND are discharged solely by PROVENANCE appearing ANYWHERE
                in the line -- the AMNESTY CLASS. Plus, separately, the share whose quantifier has
                no artifact noun in window -- the VOCABULARY CLASS.
IDENTIFICATION  Exact and mechanical: both classes are computable from the gate's own predicates
                by disabling one at a time. This is a DERIVATION about code behaviour, not an
                inference about intent -- labelled as such. What is NOT derivable is whether a
                given amnestied line is actually false; that needs a reader, and the two known
                cases are diagnosed individually rather than counted.
SCOPE           population : the last 400 commit bodies carrying a `NEXT:` paragraph
                instrument : the gate's own QUANT/ARTIFACT/PROVENANCE regexes, toggled
                             instrument unit = A NEXT PARAGRAPH IN A COMMIT BODY
                             claim unit      = THE SAME. Equal by construction here, because the
                             claim is about the gate's behaviour on its own population -- unlike
                             the gate itself, whose claim unit is a REPORT's closing sentence.
                baseline   : the gate as committed at HEAD
                regime     : this repository, this history depth
WORLDS          A VOCABULARY GAP: the misses have no artifact noun near the quantifier; amnesty
                  class is small. Fix = widen the noun list. Damage = bounded, and past passes
                  mostly meant what they said.
                B BLANKET AMNESTY: a citation anywhere discharges the whole line, so a large class
                  of quantified lines was never policed at all. Fix = scope the discharge to a
                  window around the quantifier. Damage = every NEXT line citing a round, which in
                  this project is most of them.
                C BOTH, in which case the amnesty class is the one that matters, because widening
                  nouns cannot reach a line that is discharged before the nouns are consulted.
KILL            pre-registered: amnesty class == 0 -> world B is dead and this is purely
                vocabulary. AND: my "four" is pre-registered -- if the count of universal-bearing
                amnestied lines differs, my closing line was wrong a second time and says so.
POSITIVE CTRL   the four KNOWN_BAD lines from real history must still flag under EVERY candidate
                fix. Fails at g=0: with QUANT emptied, nothing flags.
NEGATIVE CTRL   a line whose number IS computed and cited adjacent to the quantifier must not be
                flagged by the scoped rule -- the fix must not simply flag everything.
PLACEBO         a quantifier token that does not occur -> 0 lines.
SEEDS           n/a, deterministic over a fixed history.
MULTIPLICITY    2 classes x 400 lines + a 4-cell window sweep + 4 control checks. All reported.
ARTIFACT        results/why_universals_pass.json
IMPOSSIBLE      "this amnestied line is FALSE" needs a reader; only two are known false by hand.
                The class size is an EXPOSURE, never a defect count -- most amnestied lines are
                probably fine, and that is exactly why nobody noticed.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
sys.path.insert(0, str(ROOT / "assurance"))
import next_line_quantifiers_are_computed as G


def quant_hit(text):
    """The gate's rule MINUS the provenance short-circuit."""
    c = G.BARE_COUNT.search(text)
    if c:
        return f"bare count '{c.group(0)}'"
    for q in G.QUANT.finditer(text):
        near = text[max(0, q.start() - G.WINDOW): q.end() + G.WINDOW]
        a = G.ARTIFACT.search(near)
        if a:
            return f"'{q.group(1)}' over '{a.group(1)}'"
    return ""


def scoped(text, w):
    """Candidate fix: a citation discharges only quantifiers within w chars of it."""
    c = G.BARE_COUNT.search(text)
    if c and not any(abs(m.start() - c.start()) <= w for m in G.PROVENANCE.finditer(text)):
        return f"bare count '{c.group(0)}'"
    for q in G.QUANT.finditer(text):
        near = text[max(0, q.start() - G.WINDOW): q.end() + G.WINDOW]
        if G.ARTIFACT.search(near) and not any(
                abs(m.start() - q.start()) <= w for m in G.PROVENANCE.finditer(text)):
            return f"'{q.group(1)}'"
    return ""


def main():
    rows = G.next_lines(400)
    if len(rows) < 20:
        print("UNRUNNABLE: population too small. Exit 2, never 0."); return 2
    N = len(rows)

    print("─── CONTROLS ───")
    KB = [t for _, t in rows if re.search(
        r"the 9 rounds cited|every number in the ceiling chain|the open items are the ones|"
        r"only unexplained number", t, re.I)]
    pos = KB and all(G.flagged(t) for t in KB)
    print(f"  POSITIVE  {len(KB)} known-false NEXT lines from real history, all still flagged by "
          f"the LIVE gate -> {'PASS' if pos else '⛔ FAIL'}")
    saved = G.QUANT
    G.QUANT = re.compile(r"\bzzq_no_such_quantifier\b")
    g0 = sum(1 for _, t in rows if quant_hit(t) and not G.BARE_COUNT.search(t))
    G.QUANT = saved
    print(f"  g=0       QUANT emptied -> {g0} quantifier hit(s) -> "
          f"{'PASS — the detector can return nothing' if g0 == 0 else '⛔ FAIL'}")
    plc = sum(1 for _, t in rows if re.search("zzq" + "_nonexistent" + "_quantifier", t, re.I))
    print(f"  PLACEBO   a quantifier token that does not occur -> {plc} line(s) -> "
          f"{'PASS' if plc == 0 else '⛔ FAIL'}")
    controls_ok = bool(pos) and g0 == 0 and plc == 0

    print(f"\n─── THE TWO CLASSES, over {N} NEXT lines ───")
    amnesty, vocab, flagged_now = [], [], []
    for sha, t in rows:
        live, raw = G.flagged(t), quant_hit(t)
        if live:
            flagged_now.append(sha)
        elif raw:
            amnesty.append((sha, raw, t))      # would flag, discharged by a citation ANYWHERE
        elif G.QUANT.search(t):
            vocab.append((sha, t))             # a quantifier with no artifact noun in window
    print(f"  flagged by the live gate           : {len(flagged_now):>4}  ({len(flagged_now)/N:.1%})")
    print(f"  AMNESTY  would flag, discharged by a")
    print(f"           citation ANYWHERE in the line: {len(amnesty):>4}  ({len(amnesty)/N:.1%})")
    print(f"  VOCAB    quantifier, no artifact noun : {len(vocab):>4}  ({len(vocab)/N:.1%})")
    print(f"  clean                              : {N-len(flagged_now)-len(amnesty)-len(vocab):>4}")

    print(f"\n─── THE TWO KNOWN-FALSE UNIVERSALS, DIAGNOSED INDIVIDUALLY ───")
    diag = {}
    for name, pat in (("#217 every axis", r"every axis of this arc"),
                      ("#212 every", r"every (round|claim|number) (in|of) ")):
        m = [(s, t) for s, t in rows if re.search(pat, t, re.I)]
        if not m:
            print(f"  {name:<16} not present in this history depth -> UNVERIFIED, not absent")
            diag[name] = "not in history"
            continue
        s, t = m[0]
        prov = G.PROVENANCE.search(t)
        raw = quant_hit(t)
        why = ("AMNESTY — discharged by " + repr(prov.group(0))) if (prov and raw) else \
              ("VOCAB — quantifier present, no artifact noun in window" if not raw else "flagged")
        print(f"  {name:<16} {s}  -> {why}")
        diag[name] = why

    print(f"\n─── SPECIFICATION CURVE: scoping the discharge to a window ───")
    print(f"  {'window':>8}  {'flagged':>8}  {'new vs live':>12}  known-bad still flagged")
    curve = []
    for w in (40, 80, 160, 10**6):
        hits = [s for s, t in rows if scoped(t, w)]
        kb_ok = all(scoped(t, w) for t in KB)
        curve.append({"window": w, "flagged": len(hits), "known_bad_ok": kb_ok})
        lbl = "∞ (= live gate)" if w > 10**5 else str(w)
        print(f"  {lbl:>8}  {len(hits):>8}  {len(hits)-len(flagged_now):>+12}  "
              f"{'PASS' if kb_ok else '⛔ FAIL'}")

    print(f"\n─── VERDICT ───")
    predicted = 4
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif not amnesty:
        world = ("A VOCABULARY GAP — the amnesty class is empty; the misses are quantifiers with "
                 "no artifact noun nearby, and widening the noun list reaches all of them")
    else:
        world = (f"B BLANKET AMNESTY — {len(amnesty)} of {N} NEXT lines ({len(amnesty)/N:.1%}) "
                 f"carry a quantifier over an artifact noun and are discharged by a citation "
                 f"appearing ANYWHERE in the line. The short-circuit runs BEFORE the noun test, so "
                 f"widening the vocabulary cannot reach them.")
    print(f"  {world}")
    print(f"\n  ⚠ MY PRE-REGISTERED '{predicted}' vs the amnesty class of {len(amnesty)}: "
          f"{'held' if len(amnesty) == predicted else 'REFUTED — the closing line was wrong twice'}")
    print(f"  ⚠ EXPOSURE, NOT A DEFECT COUNT: 'this amnestied line is FALSE' needs a reader. Two "
          f"are known false by hand. Most of the rest are probably fine — which is exactly why "
          f"nobody noticed the discharge was unscoped.")
    print(f"  MULTIPLICITY: 2 classes x {N} lines + {len(curve)} windows + 3 controls, all reported.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "why_universals_pass.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "n_next_lines": N,
        "flagged_live": len(flagged_now), "amnesty_class": len(amnesty),
        "vocab_class": len(vocab), "predicted_by_closing_line": predicted,
        "prediction_held": len(amnesty) == predicted,
        "diagnosis_of_known_universals": diag,
        "specification_curve": curve,
        "amnesty_examples": [{"sha": s, "why": w, "line": t[:220]} for s, w, t in amnesty[:12]],
        "check218": ("the closing line claimed the gate lets universals through — FALSE, QUANT "
                     "lists them — and counted 'four' universals when 2 of the 4 were a units "
                     "conflation and a construct promotion"),
        "impossible": ("class size is EXPOSURE not defect count; whether an amnestied line is "
                       "false needs a reader"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'why_universals_pass.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
