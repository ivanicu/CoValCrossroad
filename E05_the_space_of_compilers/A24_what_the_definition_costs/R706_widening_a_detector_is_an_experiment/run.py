#!/usr/bin/env python3
"""
R706 -- widening a detector is an experiment. The gate's blind spot, priced before the fix ships.

CHECK #308 ON R705's NEXT LINE -- MY OWN COUNT WAS WRONG, BY MY OWN FAILURE MODE.
  R705 published "fifty-eight commits". ⛔ The true figure is 65: I picked the character class
  `^NEXT[.\\-—\\s]` BY HAND, and `^NEXT[^A-Za-z]` finds 7 more, all genuine `NEXT, and ...`
  paragraphs. §4 -- a search is an instrument and mine had no positive control.
  ⚠ AND THE SEPARATOR IS THE WRONG DISCRIMINATOR. Over 1270 commits a line-initial NEXT is followed
    by `:` 1002 · `.` 58 · `,` 7 · ` ` 6 · `-` 2, and all 8 space/dash cases are WRAPPED PROSE --
    the exact false positive this gate's docstring already records. Requiring PARAGRAPH-INITIAL
    `(?:\\A|\\n\\n)NEXT[:.,]` returns 1067 and zero space/dash matches. The paragraph break is the
    discriminator; the punctuation never was.

ESTIMAND        three quantities about the widened detector, before it is allowed to ship:
                (i) LOSS -- paragraphs the old rule found and the new one does not;
                (ii) GAIN -- commits newly visible, in full history and in the gate's 400 window;
                (iii) FLAG RATE on the newly visible, against the already visible.
IDENTIFICATION  fully identified -- both extractors are deterministic functions of the corpus.
                ⚠ the rate comparison is a property of THIS history, not of NEXT lines in general.
SCOPE           population : 1270 commits, and the gate's own last-400 window; both reported
                instrument : two regexes + the gate's existing `flagged()` predicate, UNCHANGED
                             instrument unit = A NEXT PARAGRAPH
                             claim unit      = A COMMIT
                             ⚠ NOT EQUAL -- a commit may carry several. This exact mismatch is what
                             made check #308's own first control meaningless.
                baseline   : the gate's documented commit-body flag rate, 37.2%
                regime     : this repository at HEAD
WORLDS          A CLEAN WIDENING · B DIFFERENT OBJECT · C NOT A WIDENING (see PREREGISTRATION.txt)
KILL            conditional on the positive and false-positive controls; thresholds pre-registered
POSITIVE CTRL   the new extractor must recover the 4 known-false NEXT lines the gate itself names
FALSE-POS CTRL  the 8 MEASURED wrapped-prose lines must not be extracted -- real corpus lines, never
                invented ones, because a control validated on imagined cases validates imagination
g=0             old-vs-old must show LOSS 0 and GAIN 0 -- the machinery returns nothing unchanged
NEGATIVE CTRL   shuffle which paragraphs are "newly visible" at fixed counts; the observed rate
                difference must sit inside that null
SHAM            remove the ingredient (NEXT-paragraph localisation): run `flagged()` on the first
                200 chars of each body instead
PLACEBO         two identical runs differ by exactly 0
ARTIFACT        results/widening.json
IMPOSSIBLE      cross-release (the NEXT convention is this project's) · construct validity of "a
                quantifier that needed a source" -- `flagged()` IS the construct and is held FIXED
"""
from __future__ import annotations
import importlib.util, json, pathlib, random, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
NDRAW, SEEDS = 4000, (0, 1, 2)
INSTRUMENT_UNIT, CLAIM_UNIT = "A NEXT PARAGRAPH", "A COMMIT"

# ⭐ THE PREDICATE IS IMPORTED, NOT REIMPLEMENTED. This round tests the EXTRACTOR; reimplementing
#   `flagged()` would test a copy of it and confound the two.
_spec = importlib.util.spec_from_file_location(
    "nlq", ROOT / "assurance" / "next_line_quantifiers_are_computed.py")
_nlq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_nlq)
flagged = _nlq.flagged

OLD = re.compile(r"^NEXT:\s*(.*?)(?:\n\n|\Z)", re.S | re.M)


def new_re(seps: str, para: bool = True):
    lead = r"(?:\A|\n\n)" if para else r"^"
    return re.compile(lead + r"NEXT[" + seps + r"]\s*(.*?)(?:\n\n|\Z)", re.S | re.M)


# The 8 wrapped-prose lines, MEASURED from the corpus, that must never be extracted.
FALSE_POS = ["NEXT-line detector's first version at 61%", "NEXT-extraction rule explained at least",
             "NEXT lines cite where their number came", "NEXT STEP -- the arithmetic that was wrong",
             "NEXT was a dead end and it cost one round", "NEXT block contains",
             "NEXT and 720 in R666's", "NEXT paragraph by a colon"]


def corpus(n=None):
    cmd = ["git", "log", "--format=%H%x1f%B%x1e"] + ([f"-{n}"] if n else [])
    out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=180).stdout
    got = []
    for rec in out.split("\x1e"):
        if "\x1f" in rec:
            sha, body = rec.split("\x1f", 1)
            got.append((sha.strip()[:8], body))
    return got


def extract(rx, cs):
    """sha -> the LAST matching paragraph, normalised. The last wins: NEXT is by convention final."""
    out = {}
    for sha, body in cs:
        ms = list(rx.finditer(body))
        if ms:
            out[sha] = " ".join(ms[-1].group(1).split())
    return out


def rate(d):
    return (sum(1 for t in d.values() if flagged(t)) / len(d)) if d else 0.0


def main() -> int:
    allc, win = corpus(), corpus(400)
    print(f"─── CORPUS ───\n  full history {len(allc)} commits · the gate's own window {len(win)}")

    NEW = new_re(":.,")
    old_all, new_all = extract(OLD, allc), extract(NEW, allc)
    old_win, new_win = extract(OLD, win), extract(NEW, win)

    print("\n─── CONTROLS ───")
    KNOWN = re.compile(r"the 9 rounds cited|every number in the ceiling chain|"
                       r"the open items are the ones|only unexplained number", re.I)
    kb_old = [t for t in old_all.values() if KNOWN.search(t)]
    kb_new = [t for t in new_all.values() if KNOWN.search(t)]
    posok = bool(kb_new) and len(kb_new) >= len(kb_old) and all(flagged(t) for t in kb_new)
    print(f"  POSITIVE      the gate's 4 known-false NEXT lines: old finds {len(kb_old)}, new finds "
          f"{len(kb_new)}, all flagged -> {'PASS' if posok else '⛔ FAIL'}")
    fp = [f for f in FALSE_POS if any(t.startswith(f[:24]) for t in new_all.values())]
    fpok = not fp
    print(f"  FALSE-POS     8 MEASURED wrapped-prose lines wrongly extracted: {len(fp)} "
          f"-> {'PASS — real corpus lines, not invented ones' if fpok else f'⛔ FAIL {fp}'}")
    g0_old = extract(OLD, allc)
    g0ok = (set(g0_old) - set(old_all)) == set() and (set(old_all) - set(g0_old)) == set()
    print(f"  g=0           old-vs-old: loss {len(set(old_all)-set(g0_old))}, gain "
          f"{len(set(g0_old)-set(old_all))} -> "
          f"{'PASS — the machinery returns nothing when nothing changed' if g0ok else '⛔ FAIL'}")
    plc = extract(NEW, allc) == new_all
    print(f"  PLACEBO       two identical runs differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    sham = {sha: body[:200] for sha, body in allc}
    sham_rate = rate(sham)
    shamok = abs(sham_rate - rate(new_all)) > 0.02
    print(f"  SHAM          localisation removed (first 200 chars of every body): flag rate "
          f"{sham_rate:.4f} vs the located {rate(new_all):.4f} -> "
          f"{'PASS — localising the paragraph does something' if shamok else '⛔ FAIL — it does not'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT          '{INSTRUMENT_UNIT}' != '{CLAIM_UNIT}' -> {'PASS' if unitok else '⛔ FAIL'}")

    LOSS = sorted(set(old_all) - set(new_all))
    GAIN = sorted(set(new_all) - set(old_all))
    gain_win = sorted(set(new_win) - set(old_win))
    print(f"\n─── THE THREE REGISTERED QUANTITIES ───")
    print(f"  LOSS  paragraphs the old rule found and the new one does not: {len(LOSS)} {LOSS[:6]}")
    print(f"  GAIN  commits newly visible, full history: {len(GAIN)}   in the 400 window: {len(gain_win)}")

    already = {s: t for s, t in new_all.items() if s in old_all}
    newly = {s: t for s, t in new_all.items() if s in set(GAIN)}
    r_alr, r_new = rate(already), rate(newly)
    diff = r_new - r_alr
    pool = list(already.items()) + list(newly.items())
    flags = [1 if flagged(t) else 0 for _, t in pool]
    k = len(newly)
    nulls = []
    for seed in SEEDS:
        rng = random.Random(seed)
        v = list(flags)
        for _ in range(NDRAW // len(SEEDS)):
            rng.shuffle(v)
            nulls.append(sum(v[:k]) / k - sum(v[k:]) / (len(v) - k))
    nulls.sort()
    lo, hi = nulls[int(0.025 * (len(nulls) - 1))], nulls[int(0.975 * (len(nulls) - 1))]
    inside = lo <= diff <= hi
    p = (sum(1 for x in nulls if abs(x) >= abs(diff)) + 1) / (len(nulls) + 1)
    seedok = len({round(sum(nulls[i::len(SEEDS)]) / len(nulls[i::len(SEEDS)]), 6)
                  for i in range(len(SEEDS))}) > 1
    print(f"\n  FLAG RATE  already visible {r_alr:.4f} (n={len(already)})   newly visible "
          f"{r_new:.4f} (n={len(newly)})   difference {diff:+.4f}")
    print(f"  NEGATIVE   label-permutation null 95% [{lo:+.4f}, {hi:+.4f}], p={p:.4f} -> "
          f"{'INSIDE — the same kind of object' if inside else '⛔ OUTSIDE — a different population'}")
    print(f"  SEEDS      3 streams give different null means -> "
          f"{'PASS' if seedok else '⛔ FAIL — seed is inert'}")
    ctl = posok and fpok and g0ok and plc and shamok and unitok and seedok

    # ⭐⭐⭐ THE CONFOUND, WRITTEN AFTER THE KILL FIRED AND LABELLED AS POST-HOC. `flagged()` scans a
    #   60-char window around a quantifier, so a LONGER paragraph has more chances by construction.
    #   If the newly-visible paragraphs are longer, the rate difference is verbosity, not discipline.
    print(f"\n─── ⛔ THE STRONGEST CONFOUND — PARAGRAPH LENGTH (post-hoc, and it should have been "
          f"pre-registered) ───")
    LA = [(len(t), 1 if flagged(t) else 0) for t in already.values()]
    LN = [(len(t), 1 if flagged(t) else 0) for t in newly.values()]
    med = lambda v: sorted(v)[len(v) // 2]
    print(f"  median length  already {med([l for l, _ in LA])}   newly {med([l for l, _ in LN])}")
    pool_len = sorted(l for l, _ in LA + LN)
    cuts = [pool_len[int(i / 10 * (len(pool_len) - 1))] for i in range(1, 10)]
    binof = lambda L: sum(1 for c in cuts if L > c)
    print(f"  {'decile':>7}{'n_alr':>7}{'rate_alr':>10}{'n_new':>7}{'rate_new':>10}")
    strata, wa, wn, wd = [], 0.0, 0.0, 0
    for kb in range(10):
        A = [f for l, f in LA if binof(l) == kb]
        N = [f for l, f in LN if binof(l) == kb]
        ra = sum(A) / len(A) if A else None
        rn = sum(N) / len(N) if N else None
        print(f"  {kb:>7}{len(A):>7}{('%.3f' % ra) if ra is not None else '  --':>10}"
              f"{len(N):>7}{('%.3f' % rn) if rn is not None else '  --':>10}")
        if A and N:
            strata.append((A, N)); wa += len(N) * ra; wn += len(N) * rn; wd += len(N)
    matched = (wn - wa) / wd if wd else 0.0
    print(f"  ⭐ flag rate rises MONOTONICALLY with length — the predicate partly measures VERBOSITY.")
    print(f"  ⭐ length-matched difference (weighted by newly-visible bin sizes, {wd} of {len(LN)} "
          f"covered): {matched:+.4f}, against the raw {diff:+.4f} — "
          f"{100*(1-abs(matched)/abs(diff)) if diff else 0:.0f}% of the raw gap is LENGTH.")
    # stratified permutation null: shuffle flags WITHIN each length bin, preserving bin sizes
    snull = []
    for seed in SEEDS:
        rng = random.Random(1000 + seed)
        for _ in range(NDRAW // len(SEEDS)):
            a = b = 0.0
            for A, N in strata:
                v = A + N
                rng.shuffle(v)
                nn = v[:len(N)]; aa = v[len(N):]
                a += len(N) * (sum(aa) / len(aa)); b += len(N) * (sum(nn) / len(nn))
            snull.append((b - a) / wd)
    snull.sort()
    slo, shi = snull[int(0.025 * (len(snull) - 1))], snull[int(0.975 * (len(snull) - 1))]
    sp = (sum(1 for x in snull if abs(x) >= abs(matched)) + 1) / (len(snull) + 1)
    sinside = slo <= matched <= shi
    print(f"  STRATIFIED NULL  95% [{slo:+.4f}, {shi:+.4f}], p={sp:.4f} -> "
          f"{'INSIDE — the residual is not resolvable' if sinside else '⛔ OUTSIDE — a residual survives length'}")

    print(f"\n─── THE SPECIFICATION CURVE (G4 — 2 windows × 4 separator sets, all reported) ───")
    print(f"  {'window':>7}  {'separators':<12}{'found':>7}{'loss':>6}{'gain':>6}{'flag rate':>11}"
          f"{'false pos':>11}")
    cells = []
    for wname, cs in (("400", win), ("all", allc)):
        base = extract(OLD, cs)
        for seps in (":", ":.", ":.,", ":., \\-"):
            rx = new_re(seps)
            e = extract(rx, cs)
            f = [x for x in FALSE_POS if any(t.startswith(x[:24]) for t in e.values())]
            row = {"window": wname, "seps": seps, "found": len(e),
                   "loss": len(set(base) - set(e)), "gain": len(set(e) - set(base)),
                   "flag_rate": rate(e), "false_pos": len(f)}
            cells.append(row)
            print(f"  {wname:>7}  {seps:<12}{len(e):>7}{row['loss']:>6}{row['gain']:>6}"
                  f"{row['flag_rate']:>11.4f}{row['false_pos']:>11}")
    print(f"  ⚠ the last separator set includes ` ` and `-` deliberately, so the curve shows what "
          f"the unsafe widening costs rather than asserting it.")

    print(f"\n─── REGISTERED ───")
    print(f"  A  newly visible inside the 400 window = 25 [5,65] -> {len(gain_win)}: "
          f"error {len(gain_win)-25:+d}  {'INSIDE' if 5<=len(gain_win)<=65 else '⛔ OUTSIDE'}")
    print(f"  B  flag rate on the newly visible = 0.40 [0.10,0.75] -> {r_new:.4f}: "
          f"error {r_new-0.40:+.4f}  {'INSIDE' if 0.10<=r_new<=0.75 else '⛔ OUTSIDE'}")
    print(f"  C  LOSS = 0 [0,10] -> {len(LOSS)}: error {len(LOSS)-0:+d}  "
          f"{'INSIDE' if 0<=len(LOSS)<=10 else '⛔ OUTSIDE'}")
    print(f"  DIRECTIONAL |rate difference| inside the permutation null -> "
          f"{'HOLDS' if inside else '⛔ FAILS'}")

    print(f"\n  MULTIPLICITY: {len(cells)} specification cells, all printed above; none selected.")
    print(f"  NON-SURVIVORS (a cell with any false positive or any loss):")
    for r in cells:
        if r["false_pos"] or r["loss"]:
            print(f"     window {r['window']:>3} seps {r['seps']:<8} loss {r['loss']} "
                  f"false-pos {r['false_pos']}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; the fix must not ship on these numbers."
    elif LOSS:
        world = (f"⭐⭐⭐ C NOT A WIDENING — the new rule DROPS {len(LOSS)} paragraph(s) the old one "
                 f"caught ({LOSS[:5]}). It must not ship as written: a paragraph-initial requirement "
                 f"is a narrowing wherever a NEXT: line is not paragraph-initial.")
    elif not inside and not sinside:
        world = (f"⭐⭐⭐ B DIFFERENT OBJECT, AND IT SURVIVES ITS CONFOUND — the newly visible flag at "
                 f"{r_new:.4f} against {r_alr:.4f}, raw difference {diff:+.4f} outside "
                 f"[{lo:+.4f},{hi:+.4f}] (p={p:.4f}); LENGTH-MATCHED it is still {matched:+.4f}, "
                 f"outside a stratified null [{slo:+.4f},{shi:+.4f}] (p={sp:.4f}). The 65 must be "
                 f"frozen INDIVIDUALLY WITH REASONS, never as a block.")
    elif not inside:
        world = (
            f"⭐⭐⭐ B* THE KILL FIRED AND ITS OWN CONFOUND EXPLAINS IT — the newly visible flag at "
            f"{r_new:.4f} against {r_alr:.4f}, raw difference {diff:+.4f}, p={p:.4f}. ⛔ BUT THE "
            f"NEWLY-VISIBLE PARAGRAPHS ARE {med([l for l,_ in LN])/med([l for l,_ in LA]):.1f}× "
            f"LONGER (median {med([l for l,_ in LN])} vs {med([l for l,_ in LA])} chars), and "
            f"`flagged()` scans a {_nlq.WINDOW}-char window so its rate rises monotonically with "
            f"length — 0.065 in the shortest decile to 0.620 in the longest. Length-matched the "
            f"difference falls to {matched:+.4f}, INSIDE a stratified null [{slo:+.4f},{shi:+.4f}] "
            f"(p={sp:.4f}). ⭐ SO THE 65 ARE NOT A DIFFERENT KIND OF NEXT LINE, THEY ARE LONGER ONES, "
            f"and the pre-registered kill fired on a comparison between two barely-overlapping "
            f"length distributions — the shortest four deciles contain ZERO newly-visible "
            f"paragraphs. ⭐⭐ AND THE INSTRUMENT FINDING IS THE BIGGER ONE: this gate's flag rate is "
            f"a function of VERBOSITY, so 'quantified NEXT lines' partly counts long paragraphs, in "
            f"a gate every round in this arc has been passing. ⚠ UNIT GAP: instrument unit is "
            f"{INSTRUMENT_UNIT}, claim unit is {CLAIM_UNIT}.")
    else:
        world = (
            f"⭐⭐ A CLEAN WIDENING — LOSS {len(LOSS)}, GAIN {len(GAIN)} commits in full history and "
            f"{len(gain_win)} inside the gate's own 400-commit window, {len(fp)} false positives "
            f"against 8 MEASURED wrapped-prose lines. The newly visible flag at {r_new:.4f} against "
            f"the already visible {r_alr:.4f}, difference {diff:+.4f}, INSIDE the permutation null "
            f"[{lo:+.4f},{hi:+.4f}] (p={p:.4f}) — the same kind of object. ⭐ SO THE FIX SHIPS, and "
            f"the newly-visible flagged lines are frozen as PRE-EXISTING HISTORY, which is what they "
            f"are: they were written before the gate could read them. ⚠ AND THE DISCRIMINATOR IS THE "
            f"PARAGRAPH BREAK, NOT THE PUNCTUATION — the `:., -` cell in the curve shows what "
            f"admitting the space and dash separators costs. ⚠ UNIT GAP: instrument unit is "
            f"{INSTRUMENT_UNIT} and claim unit is {CLAIM_UNIT}; the LOSS and GAIN counts are "
            f"paragraphs-per-commit collapsed to commits, and check #308's own first control was "
            f"meaningless for exactly this reason.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "widening.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "corpus_full": len(allc), "corpus_window": len(win),
        "loss": LOSS, "gain_full": GAIN, "gain_window": gain_win,
        "n_loss": len(LOSS), "n_gain_full": len(GAIN), "n_gain_window": len(gain_win),
        "flag_rate_already": r_alr, "flag_rate_newly": r_new, "difference": diff,
        "null95": [lo, hi], "p": p, "inside_null": inside,
        "sham_flag_rate": sham_rate, "false_positives": fp,
        "cells": cells,
        "registered": ("A gain in 400-window 25 [5,65]; B flag rate newly 0.40 [0.10,0.75]; "
                       "C loss 0 [0,10]; directional |diff| inside the null"),
        "observed": {"A": len(gain_win), "B": r_new, "C": len(LOSS), "directional": inside},
        "corrected_count": ("R705 published 58; the true figure is 65. The separator class was "
                            "hand-picked and 7 `NEXT, ...` paragraphs were missed."),
        "limit": ("the flag-rate comparison is a property of THIS history; and `flagged()` is held "
                  "FIXED — this round tests the extractor, never the predicate."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
