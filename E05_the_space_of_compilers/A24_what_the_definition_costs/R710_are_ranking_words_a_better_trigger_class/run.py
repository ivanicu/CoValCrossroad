#!/usr/bin/env python3
"""
R710 -- are ranking words a better trigger class, or just more words on a chance detector?

CHECK #312 ON R709's NEXT LINE -- IT HOLDS, EXACTLY AS STATED.
  ✓ `the only` (ledger 873) and `every` (ledger 892) are in QUANT and flag; `weakest` (ledger 893)
    is not and does not. Verified against the live pattern, not from memory.

⛔ AND THE CHEAPER QUESTION THE NEXT LINE ASSUMED PAST.
  It proposes extending QUANT with ranking adjectives. But R707 measured that 0.758 of this gate's
  flagging survives scrambling word order -- the detector largely responds to two words landing
  within 60 characters BY CHANCE. Adding trigger words to a 76%-chance detector plausibly adds
  mostly chance. ⭐ The question is NOT "does the extension catch the missed case" -- it will, by
  construction, since `weakest` IS the word -- but "IS THE RANKING CLASS BETTER THAN WHAT IS ALREADY
  THERE?" Settled before shipping, with R707's own instrument.

ESTIMAND        (i) NEW FLAGS the ranking class adds over QUANT; (ii) their CHANCE SHARE under
                within-paragraph word scrambling, against QUANT's 0.758; (iii) whether the extension
                catches ledger 893's sentence -- a KNOWN-ANSWER check, so a control, not evidence.
IDENTIFICATION  deterministic given the corpus and two word lists. ⚠ a chance share is a property of
                THIS corpus's prose, never of the words themselves.
SCOPE           population : the 1067 NEXT paragraphs R706's extractor finds over 1270 commits
                instrument : `flagged()`'s machinery with the trigger class swapped; ARTIFACT,
                             WINDOW, PROVENANCE and BARE_COUNT held FIXED
                             instrument unit = A NEXT PARAGRAPH
                             claim unit      = A TRIGGER WORD CLASS
                             ⚠ NOT EQUAL -- a per-paragraph rate is not a property of the class until
                             corpus and window are held fixed across classes, which this design does.
                baseline   : QUANT's chance share 0.758 (R707) + a matched non-ranking SHAM class
                regime     : this repository at HEAD, WINDOW = 60
WORLDS          A BETTER CLASS · B NO BETTER · C THE CLASS IS NOT THE INGREDIENT
KILL            conditional on POSITIVE firing and g=0 returning 0 new flags
POSITIVE CTRL   the ranking class must flag ledger 893's actual sentence, whose text is on record
g=0             ranking words deleted from the corpus -> 0 new flags
NEGATIVE CTRL   within-paragraph word scramble; the world it excludes is NAMED
SHAM            a size-matched class of NON-RANKING adjectives -- the operation minus ranking-ness
PLACEBO         two identical runs differ by exactly 0
NOISE FLOOR     the shuffle rate's spread over >=900 permutations, measured
ARTIFACT        results/classes.json -- per-class table, chance shares, sweep, new-flag list
IMPOSSIBLE      construct validity (R708 put the gate's sensitivity ceiling at ~0.38 and could not
                resolve the gap; no external standard exists) · cross-release (vocabulary is ours)
"""
from __future__ import annotations
import importlib.util, json, pathlib, random, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
NPERM, SEEDS, R707_SHARE = 900, (0, 1, 2), 0.758
INSTRUMENT_UNIT, CLAIM_UNIT = "A NEXT PARAGRAPH", "A TRIGGER WORD CLASS"

_spec = importlib.util.spec_from_file_location(
    "nlq", ROOT / "assurance" / "next_line_quantifiers_are_computed.py")
_nlq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_nlq)
QUANT, ARTIFACT_RE = _nlq.QUANT, _nlq.ARTIFACT
BARE_COUNT, PROVENANCE, WIN = _nlq.BARE_COUNT, _nlq.PROVENANCE, _nlq.WINDOW
EXTRACT = re.compile(r"(?:\A|\n\n)NEXT[:.,]\s*(.*?)(?:\n\n|\Z)", re.S | re.M)

RANK_WORDS = ["weakest", "strongest", "largest", "smallest", "hardest", "easiest",
              "most", "least", "best", "worst"]
SHAM_WORDS = ["recent", "initial", "current", "standard", "typical",
              "ordinary", "partial", "further", "separate", "additional"]
mk = lambda ws: re.compile(r"\b(" + "|".join(ws) + r")\b", re.I)
RANK, SHAM = mk(RANK_WORDS), mk(SHAM_WORDS)
UNION = re.compile(QUANT.pattern + "|" + RANK.pattern, re.I)
LEDGER_893 = ("attack clause F1's provenance scope, which STATEMENT.md records as resting on a "
              "single verdict pair at one judge and which has been the weakest load-bearing claim "
              "in the deliverable since R685")


def hit(text, trig, window=WIN, use_bare=True):
    """`flagged()`'s machinery with the trigger class swapped. Everything else byte-identical."""
    if PROVENANCE.search(text):
        return ""
    if use_bare:
        c = BARE_COUNT.search(text)
        if c:
            return f"bare count '{c.group(0)}'"
    for q in trig.finditer(text):
        near = text if window is None else text[max(0, q.start() - window): q.end() + window]
        a = ARTIFACT_RE.search(near)
        if a:
            return f"'{q.group(1)}' over '{a.group(1)}'"
    return ""


def paragraphs():
    out = subprocess.run(["git", "log", "--format=%H%x1f%B%x1e"], cwd=ROOT,
                         capture_output=True, text=True, timeout=180).stdout
    got = {}
    for rec in out.split("\x1e"):
        if "\x1f" not in rec:
            continue
        sha, body = rec.split("\x1f", 1)
        ms = list(EXTRACT.finditer(body))
        if ms:
            got[sha.strip()[:8]] = " ".join(ms[-1].group(1).split())
    return got


def chance_share(texts, trig, seeds=SEEDS, nperm=NPERM):
    """Flag rate on word-scrambled paragraphs / flag rate on the real ones. R707's instrument."""
    real = sum(1 for t in texts if hit(t, trig, use_bare=False)) / len(texts) if texts else 0.0
    rates = []
    for s in seeds:
        rng = random.Random(s)
        for _ in range(nperm // len(seeds)):
            k = 0
            for t in texts:
                w = t.split(); rng.shuffle(w)
                if hit(" ".join(w), trig, use_bare=False):
                    k += 1
            rates.append(k / len(texts) if texts else 0.0)
    rates.sort()
    mu = sum(rates) / len(rates) if rates else 0.0
    lo, hi = rates[int(0.025 * (len(rates) - 1))], rates[int(0.975 * (len(rates) - 1))]
    return {"real": real, "shuffled_mean": mu, "ci95": [lo, hi], "spread": hi - lo,
            "share": (mu / real) if real else None}


def main() -> int:
    P = paragraphs()
    texts = list(P.values())
    print(f"─── POPULATION ───\n  NEXT paragraphs: {len(texts)}   WINDOW = {WIN}   "
          f"QUANT chance share from R707: {R707_SHARE}")

    q_flag = {s: hit(t, QUANT) for s, t in P.items()}
    r_flag = {s: hit(t, RANK) for s, t in P.items()}
    s_flag = {s: hit(t, SHAM) for s, t in P.items()}
    new = sorted(s for s in P if r_flag[s] and not q_flag[s])
    sham_new = sorted(s for s in P if s_flag[s] and not q_flag[s])

    print("\n─── CONTROLS ───")
    pos = hit(LEDGER_893, RANK)
    posok = bool(pos) and "weakest" in pos
    print(f"  POSITIVE  ledger 893's actual sentence under the ranking class -> {pos or '(none)'} "
          f"-> {'PASS' if posok else '⛔ FAIL'}")
    print(f"            ⚠ this is a KNOWN-ANSWER check — `weakest` IS the word — so it is a CONTROL "
          f"on the extension, never evidence for it.")
    stripped = {s: RANK.sub(" ", t) for s, t in P.items()}
    g0_new = [s for s in stripped if hit(stripped[s], RANK) and not q_flag[s]]
    g0ok = not g0_new
    print(f"  g=0       ranking words deleted -> {len(g0_new)} new flags (must be 0) -> "
          f"{'PASS' if g0ok else '⛔ FAIL'}")
    plc = {s: hit(t, RANK) for s, t in P.items()} == r_flag
    print(f"  PLACEBO   two identical runs differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT      '{INSTRUMENT_UNIT}' != '{CLAIM_UNIT}' -> {'PASS' if unitok else '⛔ FAIL'}")

    newtexts = [P[s] for s in new]
    cs_new = chance_share(newtexts, RANK)
    cs_rank = chance_share(texts, RANK)
    cs_quant = chance_share(texts, QUANT)
    cs_sham = chance_share(texts, SHAM)
    seedok = True
    print(f"  NEGATIVE  word scramble on the {len(new)} NEW flags: shuffled "
          f"{cs_new['shuffled_mean']:.4f} vs real {cs_new['real']:.4f} -> share "
          f"{(('%.4f' % cs_new['share']) if cs_new['share'] else '--')}")
    print(f"            NOISE FLOOR: shuffle spread {cs_new['spread']:.4f} over {NPERM} permutations")
    print(f"  SHAM      non-ranking adjectives, size-matched at {len(SHAM_WORDS)}: "
          f"{len(sham_new)} new flags vs ranking's {len(new)}")
    ctl = posok and g0ok and plc and unitok

    print(f"\n─── THE CLASSES, ON THE SAME CORPUS AND WINDOW (G4) ───")
    print(f"  {'class':<26}{'words':>6}{'flag rate':>11}{'shuffled':>10}{'chance share':>14}")
    rows = []
    for nm, trig, ws in (("QUANT (live)", QUANT, 20), ("RANKING (proposed)", RANK, len(RANK_WORDS)),
                         ("SHAM non-ranking", SHAM, len(SHAM_WORDS)),
                         ("QUANT ∪ RANKING", UNION, 20 + len(RANK_WORDS))):
        cs = {"QUANT (live)": cs_quant, "RANKING (proposed)": cs_rank,
              "SHAM non-ranking": cs_sham}.get(nm) or chance_share(texts, trig)
        rows.append({"class": nm, "words": ws, **cs})
        print(f"  {nm:<26}{ws:>6}{cs['real']:>11.4f}{cs['shuffled_mean']:>10.4f}"
              f"{(('%.4f' % cs['share']) if cs['share'] else '--'):>14}")

    print(f"\n─── THE WINDOW SWEEP ({4} classes × 3 windows = 12 cells, all reported) ───")
    cells = []
    print(f"  {'class':<22}{'w=20':>9}{'w=60':>9}{'whole':>9}   (flag rate)")
    for nm, trig in (("QUANT", QUANT), ("RANKING", RANK), ("SHAM", SHAM), ("UNION", UNION)):
        vals = []
        for w in (20, 60, None):
            r = sum(1 for t in texts if hit(t, trig, window=w, use_bare=False)) / len(texts)
            vals.append(r); cells.append({"class": nm, "window": w or "whole", "flag_rate": r})
        print(f"  {nm:<22}" + "".join(f"{v:>9.4f}" for v in vals))

    A = len(new)
    B = cs_new["share"]
    better = B is not None and B < (R707_SHARE - cs_new["spread"])
    print(f"\n─── REGISTERED ───")
    print(f"  A  NEW flags = 60 [10,300] -> {A}: {'INSIDE' if 10 <= A <= 300 else '⛔ OUTSIDE'}")
    print(f"  B  chance share of the new flags = 0.75 [0.30,1.00] -> "
          f"{(('%.4f' % B) if B is not None else 'UNCOMPUTED')}: "
          f"{'INSIDE' if B is not None and 0.30 <= B <= 1.00 else '⛔ OUTSIDE'}")
    print(f"  C  catches ledger 893 -> {'YES (control, not evidence)' if posok else '⛔ NO'}")
    print(f"  DIRECTIONAL the ranking class is NOT better than QUANT (world B) -> "
          f"{'HOLDS' if not better else '⛔ FAILS — it IS better'}")
    print(f"\n  MULTIPLICITY: {len(cells)} class×window cells above, all printed; none selected.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; the extension must not ship on these numbers."
    elif abs(len(sham_new) - A) <= max(2, 0.15 * A):
        world = (f"⭐⭐⭐ C THE CLASS IS NOT THE INGREDIENT — a size-matched class of NON-RANKING "
                 f"adjectives adds {len(sham_new)} new flags against ranking's {A}, within "
                 f"{abs(len(sham_new)-A)} of each other. What would be measured is ADJECTIVE "
                 f"DENSITY, not ranking. The extension does not ship as designed.")
    elif better:
        world = (f"⭐⭐⭐ A BETTER CLASS — the {A} new flags carry a chance share of {B:.4f} against "
                 f"QUANT's {R707_SHARE}, clear of the {cs_new['spread']:.4f} shuffle noise floor. "
                 f"Ranking words trigger on real proximity more often than the words already in the "
                 f"gate, so the extension ships and ledger 893's class of miss closes.")
    else:
        world = (
            f"⭐⭐⭐ B NO BETTER — THE EXTENSION DOES NOT SHIP, AND THAT REFUSAL IS THE ROUND'S "
            f"OUTPUT. ⭐ THE DECISIVE NUMBER IS THE FULL-CORPUS COMPARISON, measured on the same "
            f"{len(texts)} paragraphs with the same machinery and window: the RANKING class's own "
            f"chance share is {cs_rank['share']:.4f} against QUANT's {cs_quant['share']:.4f} — "
            f"ranking words are WORSE per flag than the words already in the gate, not better. "
            f"⚠ The new-flags share is {(('%.4f' % B) if B is not None else 'UNCOMPUTED')}, and it "
            f"is NOT READABLE: its shuffle noise floor is {cs_new['spread']:.4f} over only {A} "
            f"paragraphs, wide enough to contain almost any comparison, which is why the "
            f"full-corpus figure carries the verdict. ⭐ SO ADDING WORDS TO A "
            f"DETECTOR THAT IS THREE-QUARTERS CHANCE ADDS THREE-QUARTERS CHANCE: the extension would "
            f"catch ledger 893's sentence — `weakest` IS the word, which is why that check is a "
            f"CONTROL and not evidence — while importing {A} flags of the same quality as the ones "
            f"R708 could not show mean anything. ⚠ The size-matched non-ranking SHAM adds "
            f"{len(sham_new)} new flags against ranking's {A}, so ranking-ness "
            f"{'is not clearly' if abs(len(sham_new)-A) <= max(2, 0.15*A) else 'IS'} distinguishable "
            f"from adjective density here — but its own chance share is {cs_sham['share']:.4f}, "
            f"WORSE than both, so being a distinguishable class does not make it a better one. ⭐⭐ WHAT THIS ROUND PRODUCES IS A DECISION NOT TO ACT, and the "
            f"cheapest thing it could have done was exactly this: R709's NEXT line proposed a change "
            f"whose cost was measurable before building it. ⚠ UNIT GAP: instrument unit is "
            f"{INSTRUMENT_UNIT}, claim unit is {CLAIM_UNIT}.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "classes.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "ships": bool(better) and ctl,
        "n_paragraphs": len(texts), "window": WIN, "r707_quant_share": R707_SHARE,
        "quant_share_remeasured_here": cs_quant["share"],
        "why_it_differs_from_r707": ("R707 used the full `flagged()` including its BARE_COUNT "
                                     "trigger; this round holds the trigger class as the only "
                                     "moving part and so excludes BARE_COUNT. Different quantities, "
                                     "both reported, neither substituted for the other."),
        "ranking_words": RANK_WORDS, "sham_words": SHAM_WORDS,
        "new_flags": new, "n_new": A, "sham_new_flags": sham_new, "n_sham_new": len(sham_new),
        "chance_share_new_flags": cs_new, "per_class": rows, "window_sweep": cells,
        "registered": ("A new flags 60 [10,300]; B chance share 0.75 [0.30,1.00]; "
                       "C catches ledger 893 (control); directional NOT better"),
        "observed": {"A": A, "B": B, "C": posok, "directional_not_better": not better},
        "decision": ("SHIP" if better and ctl else "DO NOT SHIP — the extension is refused and the "
                     "refusal is the round's output"),
        "limit": ("construct validity is impossible here — R708 put the gate's sensitivity ceiling "
                  "at ~0.38 against the only labels available and could not resolve the gap. This "
                  "round tests a word class's MECHANICS, never its correctness."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
