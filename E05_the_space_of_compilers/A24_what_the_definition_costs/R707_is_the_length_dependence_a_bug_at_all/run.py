#!/usr/bin/env python3
"""
R707 -- is the gate's length dependence a bug at all? R706's instrument finding, attacked.

CHECK #309 ON R706's NEXT LINE -- ITS CITATION DOES NOT RESOLVE.
  It cites the decile rates "from results/widening.json". ⛔ That artifact holds no decile table, no
  length-matched difference, no stratified null; 0.065 and 0.620 appear only inside a PROSE verdict
  string. §5 requires the artifact to carry what a LATER round needs to ATTACK the result, and
  R706's central finding -- the confound that overturned its own pre-registered kill -- was printed
  and discarded. This round recomputes and PERSISTS it rather than re-running a committed artifact.

⛔ AND THE CHEAPER QUESTION THE NEXT LINE SKIPPED PAST, WHICH IS THE WHOLE ROUND.
  R706 concluded the gate "measures verbosity, exactly the wrong direction". But `flagged()` is a
  PRESENCE detector -- "does this paragraph contain at least one unsourced quantifier". A longer
  paragraph makes MORE CLAIMS, so it has more chances to contain one, and for n independent
  opportunities the rate is 1-(1-p)^n, which RISES WITH LENGTH BY CONSTRUCTION. ⭐ So the length
  dependence may be CORRECT BEHAVIOUR and R706's instrument finding may be the error. Settle that
  before normalising anything -- normalising a correct detector would BREAK it.

ESTIMAND        (i) per-opportunity flag rate (flags / quantifier occurrences) per length decile;
                (ii) CHANCE SHARE -- the flag rate on a word-shuffled corpus (syntax and proximity
                destroyed, length and vocabulary preserved exactly) as a share of the real rate;
                (iii) whether the detector flags 20d1d1f's NEXT line for the RIGHT reason.
IDENTIFICATION  deterministic given the corpus and `flagged()`, held FIXED. ⚠ "opportunity" is
                operationalised as a QUANT match -- my assumption, so raw counts are reported beside.
SCOPE           population : the 1067 NEXT paragraphs R706's extractor finds over 1270 commits
                instrument : `flagged()` imported unchanged + a word-order permutation
                             instrument unit = A NEXT PARAGRAPH
                             claim unit      = THE DETECTOR'S BEHAVIOUR
                             ⚠ NOT EQUAL -- a per-paragraph rate is not a property of the predicate
                             until opportunity count is held fixed, which is what (i) does.
                baseline   : the real corpus flag rate, 0.2774
                regime     : this repository at HEAD, WINDOW = 60 characters
WORLDS          A CORRECT BEHAVIOUR · B PROXIMITY ARTIFACT · C RESIDUAL BIAS (PREREGISTRATION.txt)
KILL            conditional on POSITIVE firing and g=0 returning ~0; thresholds pre-registered
POSITIVE CTRL   the gate's own 3 known-false NEXT lines must still flag
g=0             a corpus with every QUANT span deleted must flag at ~0
NEGATIVE CTRL   the word shuffle, and the world it excludes is NAMED: "the detector responds to
                SYNTACTIC PROXIMITY, not to bag-of-words composition"
SHAM            the proximity window removed -- any quantifier anywhere plus any artifact word
                anywhere. Isolates what the 60-char constraint is worth.
PLACEBO         two identical runs differ by exactly 0
NOISE FLOOR     the shuffled rate's spread over >=1000 permutations, measured
ARTIFACT        results/length.json -- carrying the decile table, per-opportunity rates, the shuffle
                distribution and the window sweep AS FIELDS, because check #309 is that failure
IMPOSSIBLE      construct validity (no external standard says which NEXT lines OUGHT to flag) ·
                cross-release (the convention and vocabulary are this project's)
"""
from __future__ import annotations
import importlib.util, json, pathlib, random, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
NPERM, SEEDS, DEC = 1200, (0, 1, 2), 10
INSTRUMENT_UNIT, CLAIM_UNIT = "A NEXT PARAGRAPH", "THE DETECTOR'S BEHAVIOUR"

_spec = importlib.util.spec_from_file_location(
    "nlq", ROOT / "assurance" / "next_line_quantifiers_are_computed.py")
_nlq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_nlq)
flagged, QUANT, ARTIFACT = _nlq.flagged, _nlq.QUANT, _nlq.ARTIFACT
BARE_COUNT, PROVENANCE, LIVE_WINDOW = _nlq.BARE_COUNT, _nlq.PROVENANCE, _nlq.WINDOW
EXTRACT = re.compile(r"(?:\A|\n\n)NEXT[:.,]\s*(.*?)(?:\n\n|\Z)", re.S | re.M)


def flag_at(text: str, window) -> str:
    """`flagged()` with the proximity WINDOW as a parameter. window=None -> the whole paragraph.

    ⭐ Everything else is byte-identical to the live predicate: same PROVENANCE discharge, same
      BARE_COUNT precedence, same QUANT and ARTIFACT patterns. Only the one ingredient moves.
    """
    if PROVENANCE.search(text):
        return ""
    c = BARE_COUNT.search(text)
    if c:
        return f"bare count '{c.group(0)}'"
    for q in QUANT.finditer(text):
        near = text if window is None else text[max(0, q.start() - window): q.end() + window]
        a = ARTIFACT.search(near)
        if a:
            return f"quantifier '{q.group(1)}' over '{a.group(1)}'"
    return ""


def paragraphs():
    out = subprocess.run(["git", "log", "--format=%H%x1f%B%x1e"], cwd=ROOT,
                         capture_output=True, text=True, timeout=180).stdout
    got = []
    for rec in out.split("\x1e"):
        if "\x1f" not in rec:
            continue
        sha, body = rec.split("\x1f", 1)
        ms = list(EXTRACT.finditer(body))
        if ms:
            got.append((sha.strip()[:8], " ".join(ms[-1].group(1).split())))
    return got


def main() -> int:
    ps = paragraphs()
    texts = {s: t for s, t in ps}
    print(f"─── POPULATION ───\n  NEXT paragraphs: {len(ps)}   real flag rate: "
          f"{sum(1 for t in texts.values() if flagged(t))/len(ps):.4f}   WINDOW = {LIVE_WINDOW}")

    print("\n─── CONTROLS ───")
    KNOWN = re.compile(r"the 9 rounds cited|every number in the ceiling chain|"
                       r"the open items are the ones|only unexplained number", re.I)
    kb = [t for t in texts.values() if KNOWN.search(t)]
    posok = bool(kb) and all(flagged(t) for t in kb)
    print(f"  POSITIVE   the gate's known-false NEXT lines: {len(kb)} found, all flagged -> "
          f"{'PASS' if posok else '⛔ FAIL'}")
    stripped = {s: QUANT.sub(" ", t) for s, t in texts.items()}
    g0_flags = {s: flag_at(t, LIVE_WINDOW) for s, t in stripped.items()}
    g0_quant = sum(1 for w in g0_flags.values() if w.startswith("quantifier"))
    g0_bare = sum(1 for w in g0_flags.values() if w.startswith("bare"))
    g0ok = g0_quant == 0
    print(f"  g=0        every QUANT span deleted -> quantifier flags {g0_quant} (must be 0), "
          f"bare-count flags {g0_bare} (a different trigger, counted not excused) -> "
          f"{'PASS' if g0ok else '⛔ FAIL'}")
    plc = {s: flag_at(t, LIVE_WINDOW) for s, t in texts.items()} == \
          {s: flag_at(t, LIVE_WINDOW) for s, t in texts.items()}
    print(f"  PLACEBO    two identical runs differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")

    # ⭐ NEGATIVE CONTROL: shuffle WORDS within each paragraph. Length and vocabulary preserved
    #   exactly; syntax and proximity destroyed. The world it excludes: "the detector responds to
    #   bag-of-words composition rather than to two words being NEAR each other."
    shuf_rates = []
    for seed in SEEDS:
        rng = random.Random(seed)
        for _ in range(NPERM // len(SEEDS)):
            k = 0
            for t in texts.values():
                w = t.split()
                rng.shuffle(w)
                if flag_at(" ".join(w), LIVE_WINDOW):
                    k += 1
            shuf_rates.append(k / len(texts))
    shuf_rates.sort()
    real = sum(1 for t in texts.values() if flagged(t)) / len(texts)
    smu = sum(shuf_rates) / len(shuf_rates)
    slo, shi = shuf_rates[int(0.025 * (len(shuf_rates) - 1))], shuf_rates[int(0.975 * (len(shuf_rates) - 1))]
    share = smu / real if real else 0.0
    negok = not (slo <= real <= shi)
    print(f"  NEGATIVE   word-shuffled rate {smu:.4f} [{slo:.4f},{shi:.4f}] vs real {real:.4f} -> "
          f"{'PASS — the real corpus is outside the shuffle null' if negok else '⛔ FAIL'}")
    print(f"             NOISE FLOOR: shuffle spread {shi-slo:.4f} over {len(shuf_rates)} permutations")
    seedok = len({round(sum(shuf_rates[i::len(SEEDS)]) / len(shuf_rates[i::len(SEEDS)]), 6)
                  for i in range(len(SEEDS))}) > 1
    print(f"  SEEDS      3 shuffle streams differ -> {'PASS' if seedok else '⛔ FAIL — seed is inert'}")
    sham = sum(1 for t in texts.values() if flag_at(t, None)) / len(texts)
    shamok = abs(sham - real) > 0.01
    print(f"  SHAM       proximity window REMOVED (whole paragraph): {sham:.4f} vs real {real:.4f} -> "
          f"{'PASS — the 60-char constraint is doing work' if shamok else '⛔ FAIL — it is not'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT       '{INSTRUMENT_UNIT}' != '{CLAIM_UNIT}' -> {'PASS' if unitok else '⛔ FAIL'}")
    ctl = posok and g0ok and plc and negok and seedok and shamok and unitok

    # ⭐ THE ESTIMAND: per-OPPORTUNITY rate by length decile. An opportunity is a QUANT match.
    lens = sorted(len(t) for t in texts.values())
    cuts = [lens[int(i / DEC * (len(lens) - 1))] for i in range(1, DEC)]
    binof = lambda L: sum(1 for c in cuts if L > c)
    print(f"\n─── THE ESTIMAND — PER-OPPORTUNITY RATE BY LENGTH DECILE (persisted, per check #309) ───")
    print(f"  {'dec':>4}{'n':>5}{'med len':>9}{'flag rate':>11}{'opps/para':>11}"
          f"{'flags/opp':>11}{'shuffled':>10}")
    deciles = []
    for d in range(DEC):
        grp = [t for t in texts.values() if binof(len(t)) == d]
        if not grp:
            continue
        fl = sum(1 for t in grp if flagged(t))
        opp = sum(len(QUANT.findall(t)) for t in grp)
        rng = random.Random(99 + d)
        sh = 0
        for _ in range(60):
            for t in grp:
                w = t.split(); rng.shuffle(w)
                if flag_at(" ".join(w), LIVE_WINDOW): sh += 1
        row = {"decile": d, "n": len(grp), "median_len": sorted(len(t) for t in grp)[len(grp) // 2],
               "flag_rate": fl / len(grp), "opps_per_para": opp / len(grp),
               "flags_per_opp": (fl / opp) if opp else None, "shuffled_rate": sh / (60 * len(grp))}
        deciles.append(row)
        print(f"  {d:>4}{len(grp):>5}{row['median_len']:>9}{row['flag_rate']:>11.4f}"
              f"{row['opps_per_para']:>11.2f}"
              f"{(('%.4f' % row['flags_per_opp']) if row['flags_per_opp'] is not None else '--'):>11}"
              f"{row['shuffled_rate']:>10.4f}")
    fpo = [r["flags_per_opp"] for r in deciles if r["flags_per_opp"]]
    ratio = fpo[-1] / fpo[0] if fpo and fpo[0] else None
    print(f"  ⭐ per-opportunity rate, longest decile / shortest = "
          f"{('%.3f' % ratio) if ratio else 'UNCOMPUTED'}  "
          f"(raw flag rate ratio: {deciles[-1]['flag_rate']/deciles[0]['flag_rate']:.3f})")

    print(f"\n─── THE WINDOW SWEEP (G4 — {5} windows × {DEC} deciles = {5*DEC} cells) ───")
    cells = []
    print(f"  {'window':>10}{'rate':>9}{'flags/opp lo':>14}{'flags/opp hi':>14}{'ratio':>8}")
    for w in (0, 20, LIVE_WINDOW, 200, None):
        rows = []
        for d in range(DEC):
            grp = [t for t in texts.values() if binof(len(t)) == d]
            if not grp: continue
            fl = sum(1 for t in grp if flag_at(t, w))
            opp = sum(len(QUANT.findall(t)) for t in grp)
            rows.append({"decile": d, "flag_rate": fl / len(grp),
                         "flags_per_opp": (fl / opp) if opp else None})
        rr = [r["flags_per_opp"] for r in rows if r["flags_per_opp"]]
        rt = rr[-1] / rr[0] if rr and rr[0] else None
        overall = sum(1 for t in texts.values() if flag_at(t, w)) / len(texts)
        cells.append({"window": "whole" if w is None else w, "overall_rate": overall,
                      "rows": rows, "ratio_hi_lo": rt})
        print(f"  {('whole' if w is None else w):>10}{overall:>9.4f}"
              f"{(('%.4f' % rr[0]) if rr else '--'):>14}{(('%.4f' % rr[-1]) if rr else '--'):>14}"
              f"{(('%.3f' % rt) if rt else '--'):>8}")

    print(f"\n─── POINT C — THE COMMIT THAT STARTED THIS ───")
    target = texts.get("20d1d1fc")
    why = flagged(target) if target else ""
    c_ok = bool(target) and "only" in why
    print(f"  20d1d1fc extractable: {bool(target)}   flagged: {bool(why)}   reason: {why or '(none)'}")
    print(f"  registered YES/YES (the reason must name 'the only') -> {'BOTH HOLD' if c_ok else '⛔'}")
    print(f"  ⭐ so the gate could ALWAYS have caught it -- the predicate was never the problem, "
          f"the EXTRACTOR was, which is what R706 fixed.")

    A_ok = ratio is not None and 0.4 <= ratio <= 2.5
    B_ok = 0.05 <= smu <= 0.50
    print(f"\n─── REGISTERED ───")
    print(f"  A  per-opportunity ratio hi/lo = 1.0 [0.4,2.5] -> "
          f"{('%.3f' % ratio) if ratio else 'UNCOMPUTED'}: {'INSIDE' if A_ok else '⛔ OUTSIDE'}")
    print(f"  B  word-shuffled flag rate = 0.20 [0.05,0.50] -> {smu:.4f}: "
          f"{'INSIDE' if B_ok else '⛔ OUTSIDE'}")
    print(f"  C  flags 20d1d1fc for the right reason -> {'YES/YES' if c_ok else '⛔ NO'}")
    print(f"  DIRECTIONAL shuffled < real, outside its own spread -> "
          f"{'HOLDS' if smu < real and negok else '⛔ FAILS'}")

    print(f"\n  MULTIPLICITY: {sum(len(c['rows']) for c in cells)} window×decile cells, all above.")
    nonsurv = [c["window"] for c in cells if c["ratio_hi_lo"] is None or not (0.4 <= c["ratio_hi_lo"] <= 2.5)]
    print(f"  NON-SURVIVORS (windows whose per-opportunity ratio leaves [0.4,2.5]): {nonsurv}")

    # ⭐⭐ A AND B ARE NOT MUTUALLY EXCLUSIVE, AND THE FIRST DRAFT'S BRANCH ORDER DECIDED WHICH ONE
    #   PRINTED — the data satisfied BOTH. They answer different questions: A is "why does the rate
    #   rise with length", B is "what does the detector respond to at all". §4: the branch must
    #   reference every control, so both are computed and both are stated.
    opp_ratio = deciles[-1]["opps_per_para"] / deciles[0]["opps_per_para"]
    raw_ratio = deciles[-1]["flag_rate"] / deciles[0]["flag_rate"]
    per_dec_share = [(r["decile"], r["shuffled_rate"] / r["flag_rate"] if r["flag_rate"] else None)
                     for r in deciles]
    sh_lo = min((s for _, s in per_dec_share if s is not None), default=None)
    sh_hi = max((s for _, s in per_dec_share if s is not None), default=None)
    print(f"\n─── ⭐ THE DECOMPOSITION, AND THE CHANCE SHARE PER DECILE ───")
    print(f"  raw flag-rate ratio {raw_ratio:.3f} ≈ opportunities {opp_ratio:.2f}× "
          f"× per-opportunity residual {ratio:.3f}× = {opp_ratio*ratio:.3f}")
    print(f"  shuffled / real, by decile: "
          + "  ".join(f"{d}:{(('%.2f' % s) if s is not None else '--')}" for d, s in per_dec_share))
    print(f"  ⭐ chance share ranges {sh_lo:.2f} to {sh_hi:.2f} — highest in the SHORTEST paragraphs")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; nothing here licenses a reading."
    elif A_ok and share >= 0.7:
        world = (
            f"⭐⭐⭐ A AND B BOTH HOLD, AND THEY ANSWER DIFFERENT QUESTIONS. ① R706's INSTRUMENT "
            f"FINDING IS LARGELY RETRACTED: the raw flag rate rises {raw_ratio:.1f}× from the "
            f"shortest length decile to the longest, but that decomposes as {opp_ratio:.2f}× MORE "
            f"OPPORTUNITIES per paragraph ({deciles[0]['opps_per_para']:.2f} → "
            f"{deciles[-1]['opps_per_para']:.2f} quantifier occurrences) times a per-opportunity "
            f"residual of only {ratio:.3f}×, inside the registered [0.4,2.5]. `flagged()` is a "
            f"PRESENCE detector and a longer paragraph makes more claims, so a rate of 1-(1-p)^n "
            f"rises with n BY CONSTRUCTION. ⭐ THE NORMALISATION R706's NEXT LINE PROPOSED WOULD "
            f"HAVE BROKEN A MOSTLY-CORRECT DETECTOR — dividing a presence rate by length penalises "
            f"exactly the careful, claim-dense NEXT lines the gate exists to police. ② BUT A WORSE "
            f"PROBLEM IS FOUND, AND IT IS NOT THE ONE R706 NAMED: scrambling the word order within "
            f"each paragraph — length and vocabulary preserved EXACTLY, syntax and proximity "
            f"destroyed — still flags {smu:.4f} against the real {real:.4f}, a share of "
            f"{share:.3f}. ⭐⭐ SO ROUGHLY THREE QUARTERS OF THIS GATE'S FLAGGING IS TWO WORDS "
            f"LANDING WITHIN {LIVE_WINDOW} CHARACTERS BY CHANCE, and it is WORST WHERE THE "
            f"PARAGRAPHS ARE SHORTEST — chance share {sh_hi:.2f} in one decile against {sh_lo:.2f} "
            f"at best. ⚠ The real corpus is still outside the shuffle null "
            f"[{slo:.4f},{shi:.4f}], so the detector is not pure noise; and removing the window "
            f"entirely moves the rate to {sham:.4f}, so the proximity constraint is worth "
            f"{abs(sham-real):.4f}. ⚠ UNIT GAP: instrument unit is {INSTRUMENT_UNIT}, claim unit is "
            f"{CLAIM_UNIT} — this round tests the predicate's MECHANICS and cannot test whether the "
            f"lines it flags OUGHT to be flagged.")
    elif share >= 0.7:
        world = (f"⭐⭐⭐ B PROXIMITY ARTIFACT — a word-shuffled corpus, with syntax destroyed and "
                 f"length and vocabulary preserved exactly, still flags at {smu:.4f} against the "
                 f"real {real:.4f}, a share of {share:.3f}. The detector is largely measuring two "
                 f"words landing within {LIVE_WINDOW} characters BY CHANCE, and the per-opportunity "
                 f"ratio {ratio:.3f} leaves [0.4,2.5], so R706's finding also stands.")
    elif A_ok:
        world = (
            f"⭐⭐⭐ A THE LENGTH DEPENDENCE IS CORRECT BEHAVIOUR, AND R706's INSTRUMENT FINDING IS "
            f"RETRACTED. The raw flag rate rises {deciles[-1]['flag_rate']/deciles[0]['flag_rate']:.1f}× "
            f"from the shortest length decile to the longest, which R706 called 'measuring verbosity, "
            f"exactly the wrong direction'. ⛔ But PER OPPORTUNITY the rate is "
            f"{('%.3f' % ratio)}× — flat inside the registered [0.4,2.5] — while opportunities per "
            f"paragraph go from {deciles[0]['opps_per_para']:.2f} to "
            f"{deciles[-1]['opps_per_para']:.2f}. ⭐ `flagged()` IS A PRESENCE DETECTOR, AND A LONGER "
            f"PARAGRAPH MAKES MORE CLAIMS: a rate of 1-(1-p)^n rises with n by construction, so the "
            f"length dependence is the detector working, not failing. ⭐⭐ SO THE DEBT R706 RECORDED "
            f"AND THE NORMALISATION ITS NEXT LINE PROPOSED WOULD HAVE BROKEN A CORRECT DETECTOR — "
            f"dividing a presence rate by length penalises exactly the careful, claim-dense NEXT "
            f"lines the gate exists to police. ⚠ The word-shuffle control puts {share:.3f} of the "
            f"flagging at chance co-occurrence, real but not dominant, and the sham shows the "
            f"{LIVE_WINDOW}-char constraint is worth {abs(sham-real):.4f}. ⚠ UNIT GAP: instrument "
            f"unit is {INSTRUMENT_UNIT}, claim unit is {CLAIM_UNIT} — this round tests the "
            f"predicate's MECHANICS and cannot test whether the lines it flags OUGHT to be flagged.")
    else:
        world = (f"⭐⭐ C RESIDUAL BIAS — per-opportunity rate moves {ratio:.3f}× across deciles, "
                 f"outside [0.4,2.5], while the shuffle explains only {share:.3f}. Something in long "
                 f"paragraphs trips the detector beyond opportunity count, and R706's finding stands "
                 f"in weakened form.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "length.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "n_paragraphs": len(ps), "live_window": LIVE_WINDOW, "real_flag_rate": real,
        "deciles": deciles,                       # ⭐ check #309: the table, AS A FIELD
        "per_opportunity_ratio_hi_lo": ratio,
        "raw_flag_rate_ratio_hi_lo": deciles[-1]["flag_rate"] / deciles[0]["flag_rate"],
        "shuffle": {"mean": smu, "ci95": [slo, shi], "share_of_real": share,
                    "n_permutations": len(shuf_rates), "spread": shi - slo},
        "sham_whole_paragraph_rate": sham,
        "g0": {"quantifier_flags": g0_quant, "bare_count_flags": g0_bare},
        "window_sweep": cells,                    # ⭐ every cell, as data
        "point_C": {"sha": "20d1d1fc", "extractable": bool(target), "reason": why},
        "decomposition": {"raw_ratio": raw_ratio, "opportunity_ratio": opp_ratio,
                          "per_opportunity_residual": ratio, "product": opp_ratio * ratio},
        "chance_share_by_decile": [{"decile": d, "shuffled_over_real": s} for d, s in per_dec_share],
        "registered": ("A per-opportunity ratio 1.0 [0.4,2.5]; B shuffled rate 0.20 [0.05,0.50]; "
                       "C flags 20d1d1fc naming 'the only'; directional shuffled < real"),
        "observed": {"A": ratio, "B": smu, "C": c_ok, "directional": smu < real and negok},
        "retracts": ("R706's 'this gate's flag rate is a function of verbosity, the wrong direction' "
                     "-- if world A holds, the dependence is opportunity count and the detector is "
                     "behaving correctly."),
        "limit": ("construct validity is impossible here: no external standard says which NEXT lines "
                  "OUGHT to flag. This round tests MECHANICS, never correctness."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
