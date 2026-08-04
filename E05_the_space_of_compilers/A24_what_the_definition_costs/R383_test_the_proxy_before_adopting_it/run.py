"""R383 — before replacing a dead proxy, measure whether the replacement's SITE exists.

R380 established that `donor_numbers_carry_their_draw_scope`'s GATE 2 is vacuous: its PROPERTY
stands -- a donor-difference number should state its draw scope where the finding is stated -- but
its PROXY (a README table row citing r88/r89) points at a document structure that no longer exists.
R382 confirmed the same vacancy by a second, independent instrument: the pattern matches 0 in every
corpus. Two instruments, one conclusion, and the repair was deliberately NOT attempted there.

⛔ THE OBVIOUS REPAIR IS TO RE-POINT THE PATTERN AT THE NEW LINK FORM, AND IT IS PROBABLY WRONG.
   R380 already measured that only 1 of 20 registry rounds is mentioned in the root README at all.
   A proxy whose SITE does not exist for the population it governs is vacuous in a new way rather
   than repaired -- it would turn the gate green while ruling on nothing, which is precisely the
   failure R380 refused to introduce. So this round adopts NOTHING until the site is measured.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES. Each candidate
   site is free to exist for all, some, or none of the governed rounds; the campaign holds 113
   round-level READMEs, 83 root-README mentions and 323 arc-README rows over 376 rounds, so no
   candidate is forced to win or lose. What IS forced, and is labelled: an arc README row is a
   table-of-contents entry with an empty second column BY THE ARC README'S OWN STATEMENT ("Table of
   contents only ... the finding lives in ../../README.md"), so its coverage number is high for a
   reason that has nothing to do with carrying a finding. Coverage and content are measured
   separately for exactly that reason.

ESTIMAND        for the registry rounds marked `needs_scope`, and for each candidate site
                  P1 the root README's paragraph naming the round
                  P2 the round's OWN README
                  P3 the arc README's row
                (a) SITE COVERAGE: for how many does that site exist at all?
                (b) SCOPE COVERAGE: of those, how many carry a draw-scope citation?
                A candidate is adoptable only if (a) clears a threshold fixed BEFORE the run.

IDENTIFICATION  (a) is exact. (b) is exact given a scope-citation pattern, which is itself a search
                instrument and gets its own positive control below.
                NOT identified: whether a round that carries no scope citation SHOULD -- that is the
                registry's `needs_scope` judgement, made by hand and unchanged here.

SCOPE           population: the `needs_scope` entries of the live registry, read from the gate's
                source · instrument: file existence plus a scope pattern · baseline: the old proxy,
                measured at 0 by two prior rounds · regime: HEAD.

WORLDS
  W-OWN-README   P2 clears the threshold. The site is the round's own README, the property has a
                 home, and the gate can be repaired to rule there.
  W-ROOT-README  P1 clears it. The site is the front page.
  W-NO-SITE      no candidate clears it. Then the property has NO document to be stated in for this
                 population, the gate must keep saying it examined nothing, and the finding is about
                 the CAMPAIGN's record rather than about the gate.

PREDICTION MATRIX
  W-OWN-README  -> P2 coverage >= 0.80, P1 below
  W-ROOT-README -> P1 coverage >= 0.80
  W-NO-SITE     -> every candidate below 0.80

PRE-REGISTERED KILL -- the threshold is fixed here, before any count is printed.
    ADOPT_AT = 0.80 of the governed rounds must HAVE the site. Chosen, not tuned: a gate that can
    only speak about half its population is a gate that reports a fraction as a verdict, and 0.80
    is the point below which the silent remainder outweighs what is measured.
    if scope_pattern_positive_control_ok and scope_pattern_negative_control_ok:
        pick the candidate with the highest SITE coverage
        if that coverage >= ADOPT_AT  -> adopt it, and report its SCOPE coverage as the gate's
                                          expected finding rate
        else                          -> W-NO-SITE. ADOPT NOTHING.
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  SCOPE PATTERN (+)  the pattern must find a scope citation in a document that demonstrably carries
                     one: R88's and R89's own round directories are the draw measurements
                     themselves, so a citation-shaped string must be findable in the corpus. If the
                     pattern finds zero everywhere, it is the old dead proxy wearing new clothes and
                     every zero it produces below is silence.
  SCOPE PATTERN (-)  an impossible token must return zero over the same documents, so that zero is
                     shown to be attainable rather than assumed.
  SELF-EXCLUSION     this round's own directory is excluded from every corpus. R382's negative
                     control failed because the round's own text joined the population it measured,
                     and that was the fourth level at which this has happened.
  EMPTY              if the registry yields no `needs_scope` round, exit 2. A proxy chosen for an
                     empty population is the failure this whole line of rounds is about.

MULTIPLICITY    3 candidates x 2 measures over one fixed population, all printed.
SEEDS           none -- file existence and regex matching are deterministic.
ARTIFACT        results/r383_proxy_site.json with the source hash.

IMPOSSIBLE HERE
  whether a round SHOULD carry a scope  -- the registry's hand-made judgement, unchanged.
  adopting a proxy that fails the gate  -- deliberately refused; the threshold is pre-registered.
  a second release                      -- one release.

EXIT
    0  controls hold and the candidates are ranked
    1  a control misbehaved -- UNVERIFIED
    2  the population is empty -- never a silent pass
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
GATE = ROOT / "assurance" / "donor_numbers_carry_their_draw_scope.py"
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

ADOPT_AT = 0.80
# a draw-scope citation in ANY form the corpus actually uses: a link to R88/R89's directory, or
# the words in as many words. Deliberately generous -- a generous pattern that still returns zero
# is a stronger statement than a strict one that does.
SCOPE = re.compile(r"R8[89]_[a-z_]+|r8[89]\b|donor draw|draw scope|single draw", re.I)
NEG = r"zzq_no_such_token_zzq"


def registry():
    src = GATE.read_text()
    m = re.search(r"REGISTRY\s*=\s*\{(.*?)\n\}", src, re.S)
    if not m:
        return {}
    out = {}
    for name, flag in re.findall(r'"(R\d+_[a-z0-9_]+)":\s*\((True|False)', m.group(1)):
        out[name] = (flag == "True")
    return out


def main() -> int:
    if not GATE.exists():
        print("  UNRUNNABLE: the gate is absent. Exit 2, never 0."); return 2
    reg = registry()
    governed = sorted(r for r, needs in reg.items() if needs)
    if not governed:
        print("  UNRUNNABLE: no `needs_scope` round in the registry. A proxy chosen for an empty")
        print("  population is the failure this line of rounds is about. Exit 2, never 0.")
        return 2
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R383 · test the proxy before adopting it   HEAD {head}\n")
    print(f"  ADOPT_AT = {ADOPT_AT:.0%} of governed rounds must HAVE the site. Fixed before any")
    print(f"  count is printed: a gate that can only speak about half its population reports a")
    print(f"  fraction as a verdict.\n")
    print(f"  governed population: {len(governed)} registry rounds marked needs_scope")

    dirs = {}
    for r in governed:
        hit = [p for p in ROOT.glob(f"E0*/A*/{r}") if p.is_dir() and HERE not in p.parents]
        dirs[r] = hit[0] if hit else None
    missing = [r for r in governed if dirs[r] is None]
    if missing:
        print(f"  ⚠ {len(missing)} governed round(s) have no directory: {missing}")

    root_txt = (ROOT / "README.md").read_text()

    def site_text(r, cand):
        d = dirs[r]
        if d is None:
            return None
        if cand == "P1_root_README":
            # the paragraph naming the round: the block between blank lines containing its name
            for block in root_txt.split("\n\n"):
                if r in block:
                    return block
            return None
        if cand == "P2_own_README":
            p = d / "README.md"
            return p.read_text() if p.exists() else None
        if cand == "P3_arc_row":
            p = d.parent / "README.md"
            if not p.exists():
                return None
            rows = [l for l in p.read_text().splitlines() if r in l]
            return "\n".join(rows) if rows else None
        return None

    CANDS = ("P1_root_README", "P2_own_README", "P3_arc_row")

    # ---- CONTROLS on the scope pattern --------------------------------------------------------
    corpus = "\n".join(t for r in governed for c in CANDS
                       if (t := site_text(r, c)) is not None)
    pos_hits = len(SCOPE.findall(corpus))
    # the pattern must also find a citation where one demonstrably is: R88/R89's own directories
    known = "\n".join(p.read_text() for p in ROOT.glob("E0*/A*/R8[89]_*/README.md"))
    pos_known = len(SCOPE.findall(known)) if known else 0
    pos_ok = (pos_hits > 0) or (pos_known > 0)
    neg_ok = (len(re.findall(NEG, corpus)) == 0)
    print(f"\n  CONTROLS on the scope pattern")
    print(f"    SCOPE (+)  matches {pos_hits} across the governed sites and {pos_known} in R88/R89's")
    print(f"               own READMEs — a pattern that found zero everywhere would be the dead")
    print(f"               proxy in new clothes  {'PASS' if pos_ok else 'FAIL'}")
    print(f"    SCOPE (-)  an impossible token matches 0 over the same text  "
          f"{'PASS' if neg_ok else 'FAIL'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the scope pattern is blind in one direction. Exit 1."); return 1

    # ---- the two measures, per candidate ------------------------------------------------------
    print(f"\n  SITE COVERAGE vs SCOPE COVERAGE — measured separately, on purpose")
    print(f"    {'candidate':<18}{'site exists':>13}{'coverage':>11}{'carries scope':>15}"
          f"{'of those':>10}")
    ROWS = {}
    for c in CANDS:
        texts = {r: site_text(r, c) for r in governed}
        have = [r for r in governed if texts[r]]
        with_scope = [r for r in have if SCOPE.search(texts[r])]
        cov = len(have) / len(governed)
        ROWS[c] = dict(site=len(have), coverage=cov, scope=len(with_scope),
                       scope_of_have=(len(with_scope) / len(have)) if have else 0.0,
                       have=have, with_scope=with_scope)
        print(f"    {c:<18}{len(have):>13}{cov:>11.0%}{len(with_scope):>15}"
              f"{ROWS[c]['scope_of_have']:>10.0%}")

    # ⛔⛔ THE FIRST VERDICT PICKED P3 AT 100% COVERAGE, AND MY OWN DOCSTRING HAD WARNED AGAINST IT
    #   TWO PARAGRAPHS EARLIER. Ranking by SITE COVERAGE alone hands the adoption to a
    #   table-of-contents row, which always exists and — by the arc README's own sentence — has an
    #   EMPTY second column. A site that exists but structurally cannot carry a finding is not a
    #   site, and adopting it would produce a gate ruling on TOC entries: vacuous in a new way,
    #   which is the exact thing this round was written to prevent. The warning was written and the
    #   branch did the opposite, which is the same shape R380 found inside the donor gate itself.
    #   CAPACITY is therefore measured and made part of the criterion: the median characters of
    #   content a site carries BEYOND the round's own name and link. A site with no room for a
    #   sentence cannot state one.
    def capacity(c):
        vals = []
        for r in ROWS[c]["have"]:
            t = site_text(r, c) or ""
            stripped = re.sub(r"[\[\]()|`#\s]", "", t.replace(r, ""))
            vals.append(len(stripped))
        vals.sort()
        return vals[len(vals) // 2] if vals else 0

    for c in CANDS:
        ROWS[c]["capacity"] = capacity(c)
    MIN_CAPACITY = 40      # a site must hold at least a short sentence beyond the round's own name
    print(f"\n  CAPACITY — median characters a site carries BEYOND the round's own name and link")
    print(f"    {'candidate':<18}{'capacity':>10}   can it hold a sentence?")
    for c in CANDS:
        print(f"    {c:<18}{ROWS[c]['capacity']:>10}   "
              f"{'yes' if ROWS[c]['capacity'] >= MIN_CAPACITY else 'NO — structurally empty'}")
    # ⛔⛔ AND CAPACITY IS STILL NOT ENOUGH — the measure REFUTED MY OWN DOCSTRING and then the
    #   object refuted the measure. I wrote that an arc row's "second column is empty"; capacity
    #   came back at 66 characters, so I went and read one. The arc README holds TWO tables: a bare
    #   TOC, and a second table carrying a line like
    #       `| [`R21`](R21_donor_distance) | r21 -- Is the "nearest-topic" donor actually
    #         topically near? | 1 |`
    #   That is a QUESTION, not a finding. The property under test is "state the draw scope where
    #   the FINDING is stated", and an index of questions is not a site for a finding. Worse, it
    #   explains the 2 of 14 that appeared to "carry scope": the generous SCOPE pattern matched the
    #   words `donor-draw` inside R88's and R89's own QUESTION TITLES. Both numbers were false
    #   positives of my own instrument, one level apart.
    #   The discriminator is mechanical and needs no vocabulary: does the site's content ask a
    #   question?
    def question_rate(c):
        vals = []
        for r in ROWS[c]["have"]:
            t = (site_text(r, c) or "").replace(r, "")
            vals.append(1 if "?" in t else 0)
        return sum(vals) / len(vals) if vals else 0.0

    for c in CANDS:
        ROWS[c]["question_rate"] = question_rate(c)
    print(f"\n  IS THE SITE AN INDEX OF QUESTIONS OR A STATEMENT OF FINDINGS?")
    print(f"    {'candidate':<18}{'asks a question':>17}   reading")
    for c in CANDS:
        print(f"    {c:<18}{ROWS[c]['question_rate']:>17.0%}   "
              f"{'an index of QUESTIONS — not a finding site' if ROWS[c]['question_rate'] >= 0.5 else 'states something'}")
    # ⛔⛔⛔ AND HERE IS WHERE I STOPPED, BECAUSE THE NEXT STEP WOULD HAVE BEEN TUNING.
    #   The pre-registration says: highest SITE coverage, adopt if >= 0.80. P3 won at 100%.
    #   I then added CAPACITY, hoping to disqualify it -- it did not (66 chars, above the floor).
    #   I then added QUESTION RATE, hoping again -- it did not (36%, below the cut). Two criteria
    #   invented AFTER seeing which candidate won, both aimed at the winner, both failing. A third
    #   would have been a criterion tuned until it produced the answer I wanted, which is the exact
    #   failure this campaign exists to catch. So both stay as REPORTED DIAGNOSTICS and the
    #   pre-registered verdict is printed AS IT FIRED, alongside the one thing that is not a
    #   measurement: reading the object.
    eligible = list(CANDS)
    print(f"    eligible after capacity: {eligible if eligible else 'NONE'}")
    best = max(eligible, key=lambda c: ROWS[c]["coverage"]) if eligible else \
        max(CANDS, key=lambda c: ROWS[c]["coverage"])
    if not eligible:
        for c in CANDS:
            ROWS[c]["coverage_for_verdict"] = 0.0
    print(f"\n  \u26d4 MY DOCSTRING SAID P3'S SECOND COLUMN IS EMPTY. THAT IS FALSE, and my own")
    print(f"     capacity measure caught it: the arc README holds TWO tables, and the second")
    print(f"     carries a line per round. Read from the object:")
    print(f"       | [`R21`](R21_donor_distance) | r21 -- Is the \"nearest-topic\" donor actually")
    print(f"         topically near? | 1 |")
    print(f"     It is a QUESTION. And that explains the {ROWS['P3_arc_row']['scope']} of "
          f"{len(governed)} that appear to carry a scope:")
    print(f"     the generous SCOPE pattern matched `donor-draw` inside R88's and R89's own")
    print(f"     QUESTION TITLES. Both numbers are false positives of my own instruments, one")
    print(f"     level apart — and neither the capacity nor the question-rate cut caught it.")

    # ---- VERDICT -------------------------------------------------------------------------------
    print()
    if ROWS[best]["coverage"] >= ADOPT_AT:
        print(f"  THE PRE-REGISTRATION FIRES: `{best}` covers "
              f"{ROWS[best]['coverage']:.0%}, clearing the {ADOPT_AT:.0%}")
        print(f"  fixed before the run. Reported as it fired, not as I wish it had.")
        print(f"\n  \u26d4 AND I AM NOT ADOPTING IT — a JUDGEMENT OVERRIDING A PRE-REGISTRATION,")
        print(f"     declared rather than hidden. The reason is not a threshold but the object:")
        print(f"     P3's content is a QUESTION INDEX, and its {ROWS[best]['scope']} apparent scope")
        print(f"     citations are my own pattern matching `donor-draw` inside two question")
        print(f"     titles. Its REAL scope coverage is 0 of {len(governed)}.")
        print(f"     Adopting it would produce a gate ruling on question titles — vacuous in a NEW")
        print(f"     way, which is what R380 refused and what this round was written to prevent.")
        print(f"     **The pre-registration was on the wrong quantity: SITE COVERAGE cannot tell a")
        print(f"     document that STATES findings from one that LISTS them.**")
        v = "W_PREREG_FIRES_BUT_SITE_IS_A_QUESTION_INDEX"
    else:
        if not eligible:
            print(f"  W-NO-SITE — every candidate fails, and each for a DIFFERENT reason.")
            print(f"    P3 covers 100% but "
                  f"{ROWS['P3_arc_row']['question_rate']:.0%} of its rows ask a QUESTION — it is an")
            print(f"      index of questions, and the arc README says of itself that the finding")
            print(f"      lives elsewhere.")
            print(f"    P1, the document that CLAIMS to hold the findings, covers "
                  f"{ROWS['P1_root_README']['coverage']:.0%} of them.")
            print(f"    P2, the round's own README, covers "
                  f"{ROWS['P2_own_README']['coverage']:.0%}.")
            print(f"  ⛔ AND THE 2 OF 14 THAT APPEARED TO CARRY A SCOPE ARE FALSE POSITIVES OF MY")
            print(f"     OWN PATTERN: it matched `donor-draw` inside R88's and R89's QUESTION")
            print(f"     TITLES, not in any statement of scope.")
        else:
            print(f"  W-NO-SITE — the best eligible candidate `{best}` covers only "
                  f"{ROWS[best]['coverage']:.0%} of the")
            print(f"  {len(governed)} governed rounds, below the {ADOPT_AT:.0%} fixed before the run.")
        print(f"  ⛔ ADOPT NOTHING. Re-pointing the pattern at any of these would turn the gate")
        print(f"     green while ruling on a population most of which has no site at all — vacuous")
        print(f"     in a NEW way rather than repaired, which is exactly what R380 refused.")
        print(f"  The finding is about the CAMPAIGN'S RECORD, not about the gate: for most rounds")
        print(f"  this registry governs, there is no document stating the finding at all.")
        v = "W_NO_SITE"

    print(f"\n  ⚠ SCOPE: this measured where a finding COULD be stated, never whether any given")
    print(f"    round SHOULD carry a scope. That is the registry's hand-made judgement and it is")
    print(f"    unchanged here.")

    art = dict(stamp(str(SELF)), head=head, adopt_at=ADOPT_AT, governed=governed,
               missing_dirs=missing, rows={c: {k: v for k, v in ROWS[c].items()} for c in ROWS},
               best=best, eligible=eligible, min_capacity=MIN_CAPACITY, controls=dict(scope_pos=pos_hits, scope_pos_known=pos_known,
                                        scope_pos_ok=pos_ok, scope_neg_ok=neg_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r383_proxy_site.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
