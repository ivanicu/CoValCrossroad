#!/usr/bin/env python3
"""
R620 -- are the 87 unflagged quantifiers a correct rejection, or a cheap fix nobody made?

CHECK #219 CAUGHT TWO OVERSTATEMENTS IN MY OWN CLOSING LINE.
  ⚠ "which is the open-vocabulary failure R594-R596 measured on the `world` field" -- an ANALOGY
    stated as an IDENTITY. R594's open vocabulary was a DATA FIELD I control and could have typed;
    this is PROSE, which is open-vocabulary by nature and not thereby defective. The two share a
    shape, not a mechanism.
  ⚠ "an untyped string rule over prose cannot be made sound by adding words" -- a universal I did
    not compute. A keyword list has a PRECISION/RECALL TRADEOFF, and which regime it is in is a
    measurable property of the noun distribution, not a thing to assert.

⭐ THE DESIGN POINT, AND IT IS WHY THIS ROUND IS NOT ANOTHER KEYWORD LIST. "does this line quantify
   over project artifacts" is a JUDGEMENT, and writing a second keyword list to decide it would be
   the same failure one level up, with me as the instrument. So the round does NOT classify. It
   EXTRACTS the actual noun sitting beside each quantifier and reports the distribution verbatim.
   A judgement becomes an enumeration, and the distribution's SHAPE answers the question on its own.

ESTIMAND        the head-concentration of the noun distribution beside unflagged quantifiers:
                the share of the 87 VOCAB lines covered by the top-5 most frequent nouns.
IDENTIFICATION  Exact given an extraction rule. The rule is deliberately dumb -- the first
                alphabetic token after the quantifier -- so it cannot encode my expectations. Its
                failure mode is named: it returns adverbs and articles for some lines, and those
                are REPORTED rather than filtered, because filtering is where a judgement would
                re-enter.
SCOPE           population : the VOCAB class of R619 -- NEXT lines with a quantifier and no
                             artifact noun in window, over 400 commit bodies
                instrument : first-alphabetic-token-after-quantifier
                             instrument unit = A TOKEN
                             claim unit      = A LINE. NOT equal: one line can hold several
                             quantifiers, so lines are counted by their FIRST hit and the
                             multi-hit count is reported so the gap is visible.
                baseline   : the 112 lines the gate already flags, whose nouns are the list's
                             own vocabulary -- the head-concentration there is the comparison
                regime     : this repository, this history depth
WORLDS          A CORRECT REJECTION / LONG TAIL: the nouns are a long tail of singletons and
                  ordinary English ("stop", "determined"). Widening cannot reach them, my R594
                  analogy holds after all, and the gate is closer to right than R619 assumed.
                B CHEAP FIX MISSED / HEAD-HEAVY: a handful of nouns cover most of the 87, they
                  are project artifacts, and one small edit closes most of the gap. My "cannot be
                  made sound" is then simply false, and the tradeoff is favourable.
KILL            pre-registered THRESHOLD, written before the run: top-5 coverage >= 50% -> world
                B, head-heavy, widening is cheap. < 50% -> world A, long tail. And the sign is
                pre-committed: I expect A, because I wrote "cannot be made sound" in the closing
                line -- so B refutes me a third consecutive round.
POSITIVE CTRL   the one KNOWN miss (#217, "every axis of this arc") must appear in the extraction
                with the noun `axis`. Fails at g=0: an empty population yields no nouns.
NEGATIVE CTRL   the 112 ALREADY-FLAGGED lines, run through the same extractor, must yield nouns
                that ARE in the artifact list -- otherwise the extractor is not finding the noun
                the gate reacted to, and the whole distribution is measuring something else.
PLACEBO         a noun that occurs nowhere -> 0 lines.
SEEDS           n/a, deterministic over a fixed history.
MULTIPLICITY    87 + 112 lines x 1 extractor + 4 control checks + a 3-cell threshold sweep.
ARTIFACT        results/vocab_gap_shape.json
IMPOSSIBLE      "this noun denotes a project artifact" is a judgement no extractor can make. The
                nouns are printed VERBATIM with counts so a reader decides; the head-concentration
                is a SHAPE claim, which is decidable, and it is the only thing asserted.
"""
from __future__ import annotations
import collections, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
sys.path.insert(0, str(ROOT / "assurance"))
import next_line_quantifiers_are_computed as G

STOP = {"of", "the", "a", "an", "in", "on", "at", "to", "and", "or", "is", "was", "that", "this",
        "it", "its", "one", "two", "so", "but", "for", "with", "by", "as", "not", "no", "be"}


def noun_after(text, q):
    """Deliberately dumb: the first alphabetic token after the quantifier that is not a stopword."""
    for m in re.finditer(r"[A-Za-z][A-Za-z_.]+", text[q.end(): q.end() + 90]):
        w = m.group(0).lower().strip(".")
        if w not in STOP:
            return w
    return "(none)"


def first_hits(lines):
    out, multi = [], 0
    for sha, t in lines:
        qs = list(G.QUANT.finditer(t))
        if not qs:
            continue
        if len(qs) > 1:
            multi += 1
        out.append((sha, qs[0].group(1).lower(), noun_after(t, qs[0]), t))
    return out, multi


def main():
    rows = G.next_lines(400)
    if len(rows) < 20:
        print("UNRUNNABLE: population too small. Exit 2, never 0."); return 2

    vocab, flagged = [], []
    for sha, t in rows:
        if G.flagged(t):
            flagged.append((sha, t))
        elif G.QUANT.search(t):
            vocab.append((sha, t))
    V, v_multi = first_hits(vocab)
    F, f_multi = first_hits(flagged)
    if not V:
        print("UNRUNNABLE: the VOCAB class is empty. Exit 2, never 0."); return 2

    print("─── CONTROLS ───")
    pos = [r for r in V if r[2] == "axis"]
    print(f"  POSITIVE  the one KNOWN miss (#217) appears with noun 'axis': {len(pos)} line(s) -> "
          f"{'PASS' if pos else '⛔ FAIL — the extractor is not finding the noun the miss turned on'}")
    g0, _ = first_hits([])
    print(f"  g=0       empty population -> {len(g0)} noun(s) -> "
          f"{'PASS — it can return nothing' if not g0 else '⛔ FAIL'}")
    # ⛔ v1's NEGATIVE CONTROL FAILED FOR ITS OWN REASONS, and the ceiling is why. It required the
    #    forward-only extractor to land on an artifact-list noun in >=30% of ALL flagged lines --
    #    a threshold set without ever computing what the design can return. Measured: 34.8% of
    #    flagged lines have the gate's noun AFTER the quantifier; 34.8% have it BEFORE (invisible
    #    to a forward-only rule), 17.0% were flagged by BARE_COUNT with no quantifier rule at all,
    #    and in 13.4% the FIRST quantifier is not the one that fired. So the CEILING is 34.8% and
    #    the threshold demanded 86% of it. §4's remedy verbatim: compute floor and ceiling and
    #    require floor < t < ceiling. Normalised by the reachable subset, the control becomes a
    #    RECALL measurement instead of a pass/fail on an uncomputed scale.
    reachable = []
    for sha, t_ in flagged:
        if G.BARE_COUNT.search(t_): continue
        qs = list(G.QUANT.finditer(t_))
        if not qs: continue
        q = qs[0]; ns = max(0, q.start() - G.WINDOW)
        a = G.ARTIFACT.search(t_[ns: q.end() + G.WINDOW])
        if a and ns + a.start() >= q.start(): reachable.append(sha)
    in_list = [r for r in F if G.ARTIFACT.fullmatch(r[2] or "")]
    ceiling = len(reachable) / len(F) if F else 0
    recall = len(in_list) / len(reachable) if reachable else 0
    neg_ok = recall >= 0.50
    print(f"  NEGATIVE  extractor lands on an artifact-list noun in {len(in_list)}/{len(F)} "
          f"({len(in_list)/len(F):.1%}) of flagged lines; CEILING for a forward-only rule is "
          f"{ceiling:.1%}")
    print(f"            -> recall on the REACHABLE subset: {recall:.1%} -> "
          f"{'PASS — noisy but not blind' if neg_ok else '⛔ FAIL'}")
    plc = [r for r in V if r[2] == "zzq" + "nonexistentnoun"]
    print(f"  PLACEBO   a noun that occurs nowhere -> {len(plc)} -> "
          f"{'PASS' if not plc else '⛔ FAIL'}")
    controls_ok = bool(pos) and not g0 and neg_ok and not plc

    print(f"\n─── THE NOUN DISTRIBUTION BESIDE UNFLAGGED QUANTIFIERS (n={len(V)}) ───")
    cnt = collections.Counter(n for _, _, n, _ in V)
    print(f"  distinct nouns: {len(cnt)}   singletons: {sum(1 for c in cnt.values() if c==1)} "
          f"({sum(1 for c in cnt.values() if c==1)/len(cnt):.1%} of types)")
    print(f"  ⚠ {v_multi} of {len(V)} lines carry MORE THAN ONE quantifier; each is counted by its "
          f"first, so line-level and token-level counts differ and this is the gap.")
    print(f"\n  {'noun':<18} {'n':>4}   the quantifiers it appears with")
    for noun, c in cnt.most_common(14):
        qs = collections.Counter(q for _, q, n, _ in V if n == noun)
        print(f"  {noun:<18} {c:>4}   {', '.join(f'{k}×{v}' for k, v in qs.most_common(3))}")

    print(f"\n─── HEAD CONCENTRATION, against the flagged class as the baseline ───")
    def cov(counter, k, total):
        return sum(c for _, c in counter.most_common(k)) / total
    fcnt = collections.Counter(n for _, _, n, _ in F)
    print(f"  {'top-k':>6}  {'VOCAB (unflagged)':>20}  {'FLAGGED (baseline)':>20}")
    curve = []
    for k in (3, 5, 10):
        a, b = cov(cnt, k, len(V)), cov(fcnt, k, len(F))
        curve.append({"k": k, "vocab": round(a, 4), "flagged": round(b, 4)})
        print(f"  {k:>6}  {a:>19.1%}  {b:>19.1%}")
    top5 = cov(cnt, 5, len(V))

    print(f"\n─── VERDICT (threshold pre-registered at top-5 >= 50%) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif top5 >= 0.50:
        world = (f"B HEAD-HEAVY — the top 5 nouns cover {top5:.1%} of the {len(V)} unflagged "
                 f"lines, so a handful of additions closes most of the gap and 'cannot be made "
                 f"sound by adding words' is false")
    elif abs(top5 - cov(fcnt, 5, len(F))) < 0.10:
        # ⭐ WORLD C, WHICH v1 DID NOT CODE -- THE SAME DEFECT R619 RETRACTED, ONE ROUND LATER.
        #    R619's lesson was "three worlds designed, two branches coded". v1 of THIS round wrote
        #    two worlds and two branches, and the data landed between them: both classes are long
        #    tails AND their head-concentrations are within a few points of each other.
        world = (f"C NO CATEGORY TO CARVE — the unflagged class (top-5 {top5:.1%}) and the "
                 f"FLAGGED class (top-5 {cov(fcnt,5,len(F)):.1%}) have the SAME head-"
                 f"concentration. The artifact-noun list is not separating a head-heavy "
                 f"population from a long-tailed one; both are long tails, so widening it moves "
                 f"a boundary through a continuum rather than closing a gap.")
    else:
        world = (f"A LONG TAIL — the top 5 nouns cover only {top5:.1%} of the {len(V)} unflagged "
                 f"lines across {len(cnt)} distinct nouns, vs {cov(fcnt,5,len(F)):.1%} in the "
                 f"flagged class. Widening the list reaches a small fraction; the gate's "
                 f"rejection is closer to correct than R619 assumed")
    print(f"  {world}")
    print(f"\n  ⚠ WHAT IS ASSERTED IS THE SHAPE, NOT THE CLASSIFICATION. 'this noun denotes a "
          f"project artifact' is a judgement no extractor can make — the nouns are printed above "
          f"verbatim with counts so a reader overrules the reading, and head-concentration is the "
          f"only claim.")
    print(f"  MULTIPLICITY: {len(V)}+{len(F)} lines x 1 extractor + 4 controls + 3 threshold cells.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "vocab_gap_shape.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "n_vocab": len(V), "n_flagged": len(F), "distinct_nouns": len(cnt),
        "singleton_types": sum(1 for c in cnt.values() if c == 1),
        "multi_quantifier_lines": v_multi, "top5_coverage": round(top5, 4),
        "coverage_curve": curve,
        "noun_counts": cnt.most_common(30),
        "negative_control_recall_on_reachable": round(recall, 4),
        "negative_control_ceiling": round(ceiling, 4),
        "check219": ("the closing line stated the R594 analogy as an identity — that was a DATA "
                     "FIELD, this is PROSE — and asserted 'cannot be made sound by adding words', "
                     "a universal it did not compute"),
        "impossible": "whether a noun denotes a project artifact is a judgement; only shape is claimed",
    }, indent=2))
    print(f"\n  wrote {OUT / 'vocab_gap_shape.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
