#!/usr/bin/env python3
"""
R955 · R947 checked the definition's 648-line STATEMENT. The other 9,128 lines are the RECORD.
        Does the record contradict the statement, and can a reader tell which is current?

⛔ WHY THIS IS OPEN, CHECKED BEFORE BUILDING. The prior-art gate has stopped two rounds in this arc,
so it ran first. `assurance/definition_matches_the_record.py` re-derives each hand-written assertion
from a committed ARTIFACT — document↔artifact. `corrections_propagated.py` checks a correction
reaching OTHER documents — document↔document. `no_withdrawn_framings.py` checks results JSONs.
**Nothing checks the file against ITSELF.** And the file has every reason to disagree with itself:
193 of its sections carry a round id in the heading and **0 of those headings name what they
overturn**, so supersession is prose-only, exactly as R951–R953 found for the ledger.

⭐ **AND UNLIKE R949, BOTH SIDES ARE PROSE.** R949's lexical bridge failed because JSON paths and
English sentences are disjoint vocabularies — `cells[0].gap` for what the text calls a *price*. Here
the statement and the record are written by the same hand in the same words, so a token overlap is a
plausible matcher for the first time in this arc.

⛔ **THE DOMINANT CONFOUND, WRITTEN BEFORE THE RUN, AND IT IS NOT A CAVEAT — IT IS MOST OF THE
SIGNAL.** The statement itself says *"cut 0.5514 (28 admitted) under `genericpool16`; 0.5593 (24)
under `generic`"*. Two numbers, near-identical vocabulary, **both correct**, differing only by a
qualifier. Any matcher keyed on shared words will pair them and call it a disagreement. **So a
disagreeing pair is a CANDIDATE REQUIRING A READ, never a contradiction**, and the number this round
reports is a candidate count bounded from above — the same discipline that stopped R949 from claiming
attribution it had not earned.

ESTIMAND        among numeral occurrences in the statement region and the record region whose
                surrounding phrases share >=t distinctive tokens, the count of pairs whose VALUES
                differ, and the agree:disagree ratio — against a shuffled-pairing floor.
IDENTIFICATION  the counts are exact. `contradiction` is NOT identified: shared vocabulary does not
                imply the same scoped quantity, and the statement itself contains correct pairs that
                differ only by a comparator name. Bounds, and the direction is named.
SCOPE           population: 176 statement numeral occurrences × 4,459 record occurrences; the
                            statement region is IMPORTED from the gate's own `statement_region`,
                            the record is the file minus that region
                instrument: >=t shared distinctive tokens in a ±70-char window, t swept over 2–4
                baseline:   a shuffled pairing at matched pair count, 3 seeds
                regime:     HEAD, one file
WORLDS          A · the real agree:disagree ratio is far above the shuffled floor AND disagreeing
                    pairs exist -> the matcher is finding genuinely-same quantities, and the
                    disagreeing ones are a NAMED repair list a reader can resolve
                B · the ratio sits at the shuffled floor -> the pairing is coincidence, no evidence
                    of self-contradiction is available from this instrument, and the question needs
                    the supersession markers the file does not carry
                C · too few pairs at any threshold -> unanswerable, and the threshold sweep says so
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE, PLANTED: a synthetic statement/record pair carrying the SAME phrase
                     with DIFFERENT values must be detected as a disagreeing pair. If the matcher
                     cannot see a contradiction built by hand, its count on the real file is silence.
                  ⭐ ② g=0, PLANTED: the same phrase with IDENTICAL values must NOT appear in the
                     disagreeing set. A matcher that flags agreement is measuring pairing, not
                     disagreement.
                  ⭐ ③ FLOOR: statement phrases shuffled against record phrases at matched pair
                     count, 3 seeds. **A real ratio inside the shuffled spread is World B.**
                  ⭐ ④ SPECIFICATION: t swept over 2–4 and every cell printed, because one threshold
                     reported as the answer is the failure this standard names at experiment scale.
                  ⭐ ⑤ EVERY DISAGREEING PAIR NAMED with both phrases, so a reader adjudicates
                     rather than trusting a count — which is the only thing this instrument's
                     confound permits.
MULTIPLICITY    3 thresholds × {real, 3 shuffle seeds}; all cells printed including the empty ones.
ARTIFACT        results/self_contradiction.json
IMPOSSIBLE      independently replicated · cross-release · construct validated. ⚠ AND: **`is this a
                contradiction` is not decidable here.** The statement contains correct pairs that
                differ only by a qualifier, so the candidate list bounds the answer from above and
                a read is what closes it. That price is stated, not assumed away.
"""
import json
import pathlib
import random
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "assurance"))
DOC = ROOT / "E05_the_space_of_compilers/DEFINITION.md"
NUM = re.compile(r"(?<![\w.])(\d+\.\d{3,})(?![\w])")
WORD = re.compile(r"[a-z]{3,}")
STOP = {"the", "and", "not", "for", "that", "this", "with", "its", "was", "are", "under", "than",
        "every", "each", "from", "one", "two", "all", "but", "has", "have", "own", "same", "only",
        "any", "how", "what", "which", "when", "then", "also", "into", "over", "out", "per", "see",
        "does", "did", "can", "cannot", "must", "here", "there", "they", "them", "their", "it"}
THRESHOLDS = (2, 3, 4)
SEEDS = (11, 23, 37)
WIN = 70


def stem(w):
    for s in ("ing", "ed", "es", "s"):
        if len(w) > 4 and w.endswith(s):
            return w[: -len(s)]
    return w


def toks(s):
    return {stem(w) for w in WORD.findall(s.lower()) if w not in STOP}


def occurrences(text):
    flat = " ".join(text.splitlines())
    out = []
    for m in NUM.finditer(flat):
        ph = flat[max(0, m.start() - WIN): m.end() + WIN]
        out.append({"num": m.group(1), "phrase": ph.strip(), "tok": toks(ph)})
    return out


def pairs_at(S, R, t):
    ag, dis = [], []
    for a in S:
        for b in R:
            if len(a["tok"] & b["tok"]) >= t:
                (ag if a["num"] == b["num"] else dis).append((a, b))
    return ag, dis


def main() -> int:
    from a_statement_is_current_with_the_arc import statement_region
    text = DOC.read_text()
    reg = statement_region(text)
    if reg is None:
        print("  UNRUNNABLE: no statement region. Exit 2, never 0.")
        return 2
    rec = text.replace(reg, "", 1)
    S, R = occurrences(reg), occurrences(rec)
    print(f"  statement {len(reg.splitlines()):,} lines / {len(S)} numeral occurrences; "
          f"record {len(rec.splitlines()):,} lines / {len(R)} occurrences")

    plant_phrase = ("the resolvable margin against the named comparator is")
    P_stmt = [{"num": "0.111111", "phrase": f"{plant_phrase} 0.111111 on this release",
               "tok": toks(f"{plant_phrase} 0.111111 on this release")}]
    P_dis = [{"num": "0.222222", "phrase": f"{plant_phrase} 0.222222 on this release",
              "tok": toks(f"{plant_phrase} 0.222222 on this release")}]
    P_ag = [{"num": "0.111111", "phrase": f"{plant_phrase} 0.111111 on this release",
             "tok": toks(f"{plant_phrase} 0.111111 on this release")}]
    _, d1 = pairs_at(P_stmt, P_dis, 2)
    c1 = len(d1) == 1
    print(f"\n  ① POSITIVE, PLANTED — a hand-built contradiction (same phrase, 0.111111 vs "
          f"0.222222) is detected: {c1}  "
          f"{'PASS' if c1 else 'FAIL — the matcher cannot see a contradiction I built'}")
    a2, d2 = pairs_at(P_stmt, P_ag, 2)
    c2 = len(d2) == 0 and len(a2) == 1
    print(f"  ② g=0, PLANTED — identical values are counted as AGREEMENT ({len(a2)}) and not as "
          f"disagreement ({len(d2)}): {c2}  "
          f"{'PASS' if c2 else 'FAIL — the matcher flags agreement'}")

    if not (c1 and c2):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2},
                  open(OUT / "self_contradiction.json", "w"), indent=2)
        return 2

    curve = {}
    print(f"\n  ④ SPECIFICATION — t swept, every cell printed:")
    for t in THRESHOLDS:
        ag, dis = pairs_at(S, R, t)
        n = len(ag) + len(dis)
        ratio = (len(ag) / n) if n else float("nan")
        floors = []
        for seed in SEEDS:
            rng = random.Random(seed)
            sh = [(rng.choice(S), rng.choice(R)) for _ in range(max(n, 1))]
            fa = sum(1 for a, b in sh if a["num"] == b["num"])
            floors.append(fa / len(sh))
        curve[t] = {"n_pairs": n, "agree": len(ag), "disagree": len(dis),
                    "agree_share": ratio, "floor": floors}
        print(f"     t={t}  pairs {n:>6}  agree {len(ag):>5}  disagree {len(dis):>6}  "
              f"agree-share {ratio:.4f}  shuffled floor "
              f"{[f'{x:.4f}' for x in floors]}")

    t = 3
    c = curve[t]
    fl_hi = max(c["floor"])
    c3 = c["n_pairs"] > 0 and c["agree_share"] > fl_hi
    print(f"\n  ③ FLOOR at t={t} — agree-share {c['agree_share']:.4f} vs shuffled "
          f"{min(c['floor']):.4f}–{fl_hi:.4f}: {c3}  "
          f"{'PASS — the matcher pairs genuinely-same quantities more often than chance' if c3 else 'FAIL — the pairing is coincidence'}")

    ag, dis = pairs_at(S, R, t)
    seen, named = set(), []
    for a, b in dis:
        k = (a["num"], b["num"])
        if k in seen:
            continue
        seen.add(k)
        named.append({"statement_value": a["num"], "record_value": b["num"],
                      "statement_phrase": a["phrase"][:120], "record_phrase": b["phrase"][:120]})
    print(f"\n  ⑤ DISAGREEING VALUE PAIRS AT t={t}, DISTINCT — {len(named)} "
          f"(from {len(dis)} pair instances):")
    for r in named[:10]:
        print(f"     {r['statement_value']} vs {r['record_value']}")
        print(f"        S: …{r['statement_phrase'][:96]}…")
        print(f"        R: …{r['record_phrase'][:96]}…")
    if len(named) > 10:
        print(f"     … and {len(named) - 10} more, all in the artifact")

    world = "C" if c["n_pairs"] == 0 else ("A" if c3 and named else "B")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"at t={t} the matcher pairs {c['n_pairs']:,} numeral occurrences across the statement and "
        f"the record, agreeing {c['agree_share']:.4f} of the time against a shuffled floor of at "
        f"most {fl_hi:.4f} — so it is finding genuinely-same quantities. **{len(named)} distinct "
        f"value pairs DISAGREE**, and every one is named above for a reader to adjudicate."
        if world == "A" else
        f"the agree-share {c['agree_share']:.4f} sits at the shuffled floor "
        f"{min(c['floor']):.4f}–{fl_hi:.4f}. **The pairing is coincidence**, so this instrument "
        f"provides no evidence about self-contradiction, and the question needs the supersession "
        f"markers the file does not carry — 0 of its 193 round-tagged headings name what they "
        f"overturn."
        if world == "B" else
        f"no pairs survive t={t}; the threshold sweep above is the whole answer and the question is "
        f"unanswerable at this resolution."))
    print(f"     ⚠ A DISAGREEING PAIR IS A CANDIDATE, NEVER A CONTRADICTION. The statement itself "
          f"carries correct pairs that differ only by a qualifier — cut 0.5514 under `genericpool16` "
          f"and 0.5593 under `generic` — and any word-keyed matcher pairs them. The count bounds the "
          f"answer from ABOVE; a read is what closes it.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world,
               "statement_lines": len(reg.splitlines()), "record_lines": len(rec.splitlines()),
               "statement_occurrences": len(S), "record_occurrences": len(R),
               "curve": {str(k): v for k, v in curve.items()},
               "chosen_threshold": t,
               "disagreeing_value_pairs": named,
               "prior_art_checked": "definition_matches_the_record is document↔artifact; "
                                    "corrections_propagated is document↔document; nothing checks "
                                    "the file against itself",
               "supersession_markers": "0 of 193 round-tagged headings name what they overturn",
               "bound": "a disagreeing pair is a CANDIDATE; shared vocabulary is not the same "
                        "scoped quantity, and the statement contains correct differing pairs",
               "unit_note": "counts are NUMERAL-OCCURRENCE PAIRS and DISTINCT VALUE PAIRS, "
                            "never summed",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "self_contradiction.json", "w"), indent=2)
    print(f"\n  artifact: results/self_contradiction.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
