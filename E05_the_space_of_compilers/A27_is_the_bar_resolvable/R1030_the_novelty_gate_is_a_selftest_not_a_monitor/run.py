#!/usr/bin/env python3
"""R1030 — a gate exists to catch NEXT lines proposing existing work. It never runs on live ones.

FIVE CONSECUTIVE ROUNDS OF MINE PROPOSED WORK THAT ALREADY EXISTED, and each cost part of a round:
    R1026 NEXT "re-derive the 15,488 cost"        -> genuinely new, R1027 did it
    R1027 NEXT "audit the register as instrument" -> R291/R472/R547/R660/R802 had done it
    R1028 NEXT "re-score entries for presence"    -> R472 had done exactly that
    R1029 NEXT "a typed entry template, one gate" -> `assurance/register_requirements.py` EXISTS
                                                     and its docstring already states R1029's limit
And `assurance/next_gradient_is_new.py` EXISTS to catch precisely this, built after R858 measured
**7 of 26 (27%)** NEXT lines pointing at something already done.

⛔ SO WHY DID IT NOT FIRE? Because it is a SELF-TEST, not a MONITOR. Run with no arguments it
   validates its own searcher against FOUR HISTORICAL cases whose answers are known, prints "every
   historical case is still detected", and exits 0 — **without ever pointing that searcher at the
   NEXT lines the session is actually writing.** It certifies CAPABILITY and never CURRENCY, which is
   the same shape as the `determinism read as currency` failure: a check that compares two runs to
   each other and never to disk. Its own closing caveat says the rest: *"it cannot flag one whose
   subject exists under words nobody thought to search"* — and `register_requirements.py` is exactly
   a subject existing under a word I did not search until after writing the NEXT.

ESTIMAND        the share of this session's committed NEXT lines whose PROPOSED SUBJECT already
                exists in the repository — R858's 27% recomputed on the live population, using the
                committed gate's OWN searcher rather than a new one.
IDENTIFICATION  partial, and the bound is stated rather than hidden. A subject is identified by terms
                I choose, so a MISS is not evidence of novelty (P6: sound in one direction only).
                The HIT direction is sound: a term found in a committed file is prior art.
SCOPE           population : the NEXT lines of R1022–R1029, read from their commit bodies
                instrument : `next_gradient_is_new.search` imported, not reimplemented
                baseline   : R858's committed 7 of 26 (0.269) · regime : this session
WORLDS          A THE LOOP IS COMPOUNDING — the live rate is at or below R858's 0.269, so the four I
                  noticed are a tail and the gate's coverage is adequate.
                B THE GATE IS BLIND TO ITS OWN DOMINANT FAILURE — the live rate is materially above
                  0.269 while the gate passes green, so a self-test is masking the failure it was
                  built for, and the repair is to make it a MONITOR that consumes the live NEXT.
                prediction matrix: A -> rate <= ~0.30, gate's green is informative.
                                   B -> rate >= 0.50 with the gate green, which is the mask.
                ⚠ ONTOLOGICAL: A says coverage is fine and I was unlucky; B says a passing gate is
                  evidence of nothing here. They imply different trust in all 81 gates.
KILL            pre-registered and CONDITIONAL:
                  if the searcher reproduces the gate's four historical cases and the negative
                  control finds nothing:
                      live rate >= 0.50 -> World B
                      live rate <= 0.30 -> World A
                      otherwise         -> report the rate, claim neither
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ① the imported searcher must reproduce the gate's OWN four historical cases — if it
                cannot, this is not that gate's instrument and no comparison to R858 is licensed.
                ② FOUR CASES FROM THIS SESSION WITH KNOWN LABELS, which the self-test does not have:
                R1027/R1028/R1029's subjects MUST be found (I found them by hand), and R1026's must
                be found too since R1027 then did it — the label there is "new at the time", so it is
                excluded from the positive control and reported separately rather than fudged.
NEGATIVE CTRL   a term that exists nowhere must return nothing, run through the SAME searcher.
                ⚠ and g=0: an empty term list must be UNRUNNABLE, never a silent pass.
PLACEBO         a term certain to exist everywhere (`coval_core`) must hit, bounding the searcher
                from above — a searcher that finds nothing would pass the negative control trivially.
NOISE FLOOR     N/A — exact substring search over a fixed corpus. Stated rather than omitted.
MULTIPLICITY    every NEXT in the window is scored and printed, hits and misses alike.
SEEDS           N/A — deterministic. Stated rather than silently skipped.
IMPOSSIBLE      whether a NEXT is SUBSTANTIVELY novel given that its subject exists — a round can
                legitimately revisit an existing subject with a new question, and telling those apart
                is a judgement about prose. N/A; what it would require is a reader. This round bounds
                SUBJECT novelty only, and says so wherever it reports a number.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "assurance"))
import next_gradient_is_new as NG  # noqa: E402  — the committed gate's OWN searcher

BASELINE = 7 / 26  # R858, committed

# the window, with the subject each NEXT proposed and the label I established by hand
WINDOW = [
    ("R1022", "does raising the loader guard change other counts",
     ["coverage guard", "isfinite"], None),
    ("R1023", "price the guard by false-admission rate", ["false-admission"], None),
    ("R1024", "resample the censoring / drop the imputation", ["observed-only"], None),
    ("R1025", "attack the certification rule", ["legitimate_comparators"], None),
    ("R1026", "re-derive the 15,488 judge-call cost", ["15,488"], "NEW_AT_THE_TIME"),
    ("R1027", "audit the impossibility register as an instrument",
     ["the impossibility register audited"], "EXISTED"),
    ("R1028", "re-score entries for whether they name a requirement",
     ["the register half complies"], "EXISTED"),
    ("R1029", "a typed entry template enforced by one gate",
     ["register_requirements"], "EXISTED"),
]


def main() -> int:
    # ⛔⛔ THIS ROUND'S OWN FILES MUST LEAVE THE CORPUS, AND THE FIRST RUN PROVED WHY TWICE.
    #   The committed gate excludes ITSELF (`p != SELF`) and I did not extend that to this round.
    #   Result: the NEGATIVE control's marker string was found — in MY OWN run.py — and FAILED
    #   correctly; and worse, POSITIVE ② PASSED FOR THE WRONG REASON, because the searcher located
    #   R1027's and R1028's subject terms in this script rather than in the prior art. A control
    #   that finds its answer inside the question confirms nothing. Only R1029's hit was genuine.
    files = [(p_, txt) for p_, txt in NG.corpus() if HERE not in p_.parents and p_ != HERE]
    # ⛔⛔ AND THE SEARCHER'S BLIND SPOT IS MEASURED, NOT ASSUMED — the second run's POSITIVE ②
    #   failed on R1028 and the failure LOCALISED: `R472_the_register_half_complies` exists as a
    #   DIRECTORY NAME, and `NG.corpus()` returns (path, CONTENTS) so `NG.search` only ever reads
    #   contents. A prior-art round whose subject lives in its PATH is invisible to the gate. That
    #   is precisely why it never fired on me: I name rounds by their question, and the question is
    #   the subject. Both corpora are built and BOTH rates are reported, so the repair is measured
    #   rather than asserted.
    # ⛔⛔⛔ AND INDEXING PATHS WAS NOT ENOUGH EITHER — the third run localised it further, and
    #   THIS is the mechanism. Round directories are `R472_the_register_half_complies`, joined by
    #   UNDERSCORES; a NEXT line is prose, with SPACES. `NG.search` compiles `re.escape(term)`, so
    #   an exact substring match can NEVER bridge the two. The committed gate is therefore
    #   STRUCTURALLY incapable of matching a prior-art ROUND from a prose subject — and a round is
    #   the dominant form of prior art in this repository. Normalising separators is the repair,
    #   and it is applied to the CORPUS rather than to the gate, so the gate stays as committed and
    #   the difference between them is what gets measured.
    def norm(s):
        return s.replace("_", " ").replace("-", " ")
    files_norm = [(p_, norm(p_.as_posix()) + "\n" + norm(txt)) for p_, txt in files]
    files_raw = [(p_, p_.as_posix() + "\n" + txt) for p_, txt in files]

    # ⛔⛔⛔⛔ AND NORMALISING IS A TRADE, NOT A FIX — the fourth run measured that too. On the
    #   normalised corpus the gate's OWN historical cases (`R306_the_table_at_every_annotator`,
    #   `register_requirements`) STOP matching, because those terms are underscore-literals. So
    #   neither corpus alone is the instrument: prose subjects need normalisation, symbol subjects
    #   need the raw text, and the committed gate searches ONLY raw. Both are searched below and
    #   the DIFFERENCE between them is reported, which is the repair stated as a measurement.
    # ⛔⛔⛔⛔⛔ AND THE FIRST RATE WAS 7/7 = 1.000, WHICH IS THE SELF-CONFIRMATION TRAP AGAIN, ONE
    #   LEVEL UP. Searching `false-admission` for R1022's NEXT finds R1023 — the round that ACTED
    #   on it and coined the term. A subject is prior art only if it existed BEFORE the proposing
    #   round, so every path from round R_n onward is excluded per-entry. Without this the rate is
    #   forced to 1.000 by construction and could not have come out otherwise, which makes it a
    #   derivation dressed as a measurement.
    import re as _re
    def _rnum(path):
        m = _re.search(r"/R(\d+)_", "/" + path)
        return int(m.group(1)) if m else -1

    def both(terms, before=None):
        a = NG.search(files_raw, terms)
        b = NG.search(files_norm, terms)
        out = {k: sorted(set(a.get(k, [])) | set(b.get(k, []))) for k in set(a) | set(b)}
        if before is not None:
            # ⛔ AND SHARED FILES ARE DROPPED ENTIRELY, not just dated by path. `assurance/*.py`
            #   and top-level READMEs accumulate THIS session's edits — R1023's first "prior art"
            #   hit was in the fact registry I edited an hour earlier. A round directory carries a
            #   number and can be dated; a shared file cannot be, without git. So only hits inside
            #   a STRICTLY EARLIER ROUND DIRECTORY count. Conservative, and it can only LOWER the
            #   rate — which is the direction that could have refuted the finding.
            out = {k: [f for f in v if 0 <= _rnum(f) < before] for k, v in out.items()}
            out = {k: v for k, v in out.items() if v}
        return out
    files_path = files_raw
    if not files:
        print("  UNRUNNABLE: empty corpus. Exit 2, never 0.")
        return 2
    print(f"  instrument: `next_gradient_is_new.search` IMPORTED from the committed gate, not "
          f"reimplemented\n  corpus: {len(files):,} files · baseline: R858's {BASELINE:.3f} "
          f"(7 of 26)")

    # ---------- POSITIVE ①: the gate's own four historical cases ----------
    hist = [t for t, _ in getattr(NG, "CASES", [])] if hasattr(NG, "CASES") else []
    if not hist:
        hist = ["R306_the_table_at_every_annotator", "R295_held_out_annotators",
                "R250_can_provenance_be_reconstructed", "db/ledger.py"]
    h = both(hist)
    pos1 = all(hist_t in h for hist_t in hist)
    print(f"\n  POSITIVE ① — the imported searcher must reproduce the gate's OWN historical cases:")
    for t in hist:
        print(f"     {t:<48}{'FOUND' if t in h else '⛔ MISSING'}")
    print(f"     {'PASS' if pos1 else '⛔ FAIL — this is not that gate´s instrument'}")

    # ---------- POSITIVE ②: four LIVE cases with labels the self-test does not have ----------
    labelled = [(r, terms, lab) for r, _s, terms, lab in WINDOW if lab == "EXISTED"]
    hits2 = {r: both(terms) for r, terms, _ in labelled}
    blind = {r: (bool(both(terms)) and not bool(NG.search(files, terms)))
             for r, terms, _ in labelled}
    pos2 = all(hits2[r] for r, _t, _l in labelled)
    print(f"\n  POSITIVE ② — FOUR LIVE CASES this session, labelled BY HAND, which the gate's "
          f"self-test\n     does not have. Each subject was found manually, so the searcher MUST "
          f"find it too:")
    for r, terms, _ in labelled:
        got = hits2[r]
        first = next(iter(got.values()))[0] if got else "—"
        print(f"     {r}  {str(terms):<38}{'FOUND' if got else '⛔ MISSING'}  {first}")
    print(f"     {'PASS' if pos2 else '⛔ FAIL — the searcher cannot see prior art I found by hand'}")
    nblind = sum(blind.values())
    print(f"     ⛔ AND {nblind} of {len(labelled)} are invisible to the COMMITTED gate and visible only "
          f"once PATHS are\n        indexed AND separators normalised: "
          f"{[r for r, v in blind.items() if v]}. Round directories are\n        "
          f"`R472_the_register_half_complies` — UNDERSCORES — and a NEXT is prose, with SPACES. "
          f"`NG.search`\n        compiles `re.escape(term)`, so an exact match can NEVER bridge "
          f"them. The gate is\n        STRUCTURALLY unable to match a prior-art ROUND from a "
          f"prose subject, and a round is the\n        dominant form of prior art here. ⚠ And "
          f"normalising ALONE is a TRADE, not a fix: it breaks\n        the gate's own "
          f"underscore-literal cases, so the instrument must search BOTH corpora.")

    # ---------- NEGATIVE + PLACEBO, through the SAME searcher ----------
    neg = NG.search(files, ["zzq_nonexistent_subject_marker_r1030"])
    neg_ok = not neg
    plac = NG.search(files, ["coval_core"])
    plac_ok = bool(plac)
    g0 = not NG.search(files, [])
    print(f"\n  NEGATIVE — a term existing nowhere must return nothing: "
          f"{'PASS' if neg_ok else '⛔ FAIL'}")
    print(f"  PLACEBO  — a term certain to exist (`coval_core`) must hit, or the searcher passes the "
          f"negative\n     trivially by finding nothing at all: {'PASS' if plac_ok else '⛔ FAIL'}")
    print(f"  g=0      — an empty term list returns nothing and is UNRUNNABLE, not a pass: "
          f"{'PASS' if g0 else '⛔ FAIL'}")

    if not (pos1 and pos2 and neg_ok and plac_ok and g0):
        print("\n  a control did not fire. Exit 2, never 0.")
        return 2

    # ---------- the live rate ----------
    print(f"\n  ⭐ THE LIVE POPULATION — every NEXT in the window, hits AND misses:")
    print(f"     {'round':<8}{'proposed subject':<52}{'prior art':>10}  where")
    rows, existed, scored = [], 0, 0
    for r, subj, terms, lab in WINDOW:
        got = both(terms, before=int(r[1:]))
        got_contents = {k: [f for f in v if _rnum(f) < int(r[1:])]
                        for k, v in NG.search(files, terms).items()}
        got_contents = {k: v for k, v in got_contents.items() if v}
        found = bool(got)
        where = next(iter(got.values()))[0] if got else "—"
        # ⚠ R1026 is EXCLUDED from the rate: its subject exists NOW because R1027 created it.
        #   Counting it would be conditioning on the outcome.
        counted = lab != "NEW_AT_THE_TIME"
        if counted:
            scored += 1
            existed += int(found)
        rows.append({"round": r, "subject": subj, "terms": terms, "prior_art": found,
                     "prior_art_contents_only": bool(got_contents),
                     "where": where, "counted": counted, "hand_label": lab})
        print(f"     {r:<8}{subj[:50]:<52}{('YES' if found else 'no'):>10}  "
              f"{where[:38]}{'' if counted else '   ⚠ EXCLUDED (subject created by R1027)'}")
    rate = existed / max(scored, 1)
    print(f"\n     prior-art rate on the live population: {existed}/{scored} = {rate:.3f}   "
          f"against R858's committed {BASELINE:.3f}")

    print()
    if rate >= 0.50:
        world = (f"⭐ B THE GATE IS BLIND TO ITS OWN DOMINANT FAILURE — {existed} of {scored} "
                 f"({rate:.1%}) of this session's NEXT lines proposed a subject that already exists, "
                 f"against R858's {BASELINE:.1%}, WHILE `next_gradient_is_new.py` exits 0. It is a "
                 f"SELF-TEST: it validates its searcher on four historical cases and never points it "
                 f"at the live NEXT. A passing self-test is evidence about the instrument, not about "
                 f"the corpus — the same shape as `determinism read as currency`.")
    elif rate <= 0.30:
        world = (f"⭐ A THE LOOP IS COMPOUNDING — {rate:.1%} against R858's {BASELINE:.1%}; the "
                 f"cases I noticed are a tail and the gate's coverage is adequate.")
    else:
        world = (f"⭐ NEITHER PRE-REGISTERED BAND — {rate:.3f}, between 0.30 and 0.50. The rate is "
                 f"reported and no world is claimed.")
    print(world)
    print(f"⛔ AND THE HIT DIRECTION IS THE ONLY SOUND ONE. A term FOUND in a committed file is prior "
          f"art;\n   a term NOT found is not evidence of novelty, because I chose the terms. So "
          f"{rate:.3f} is a LOWER\n   BOUND on the true rate, and every 'no' in the table above is "
          f"UNVERIFIED rather than clear.")
    print(f"⚠ AND SUBJECT NOVELTY IS NOT SUBSTANTIVE NOVELTY. R1027–R1029 each produced a real result "
          f"ON\n   an existing subject — R1028 corrected R802's unit, R1029 showed the population is "
          f"unidentified.\n   The cost is not that those rounds were wasted; it is that each spent "
          f"part of itself\n   discovering prior art the NEXT line should have named.")
    print(f"⚠ THE REPAIR IS ONE ARGUMENT, NOT A NEW GATE. `next_gradient_is_new.py` already ACCEPTS "
          f"terms on\n   argv and searches them. What it lacks is a caller that feeds it the NEXT "
          f"line being written.\n   That is a wiring change, and this round does not make it — "
          f"naming it is not doing it.")

    out = HERE / "results" / "next_novelty_live.json"
    out.write_text(json.dumps({
        "round": "R1030", "baseline_r858": BASELINE, "corpus_files": len(files),
        "instrument": "next_gradient_is_new.search, imported from the committed gate",
        "controls": {"positive_historical": bool(pos1), "positive_live_labelled": bool(pos2),
                     "negative": bool(neg_ok), "placebo": bool(plac_ok), "g0": bool(g0)},
        "rows": rows, "n_scored": scored, "n_prior_art": existed, "rate": rate,
        "searcher_blind_spot": {"n_found_only_with_paths": nblind,
                                "rounds": [r for r, v in blind.items() if v],
                                "cause": "NG.corpus() returns file CONTENTS; round subjects live in "
                                         "DIRECTORY NAMES"},
        "rate_contents_only": sum(1 for r in rows if r["counted"] and
                                  r["prior_art_contents_only"]) / max(scored, 1),
        "excluded": [r["round"] for r in rows if not r["counted"]],
        "world": world,
        "limitation": "the HIT direction is sound and the MISS direction is not, because the terms "
                      "are author-chosen; the rate is a LOWER BOUND and subject novelty is not "
                      "substantive novelty",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
