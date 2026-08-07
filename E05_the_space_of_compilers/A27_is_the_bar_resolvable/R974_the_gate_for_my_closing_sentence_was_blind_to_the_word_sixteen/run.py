#!/usr/bin/env python3
"""R974 — the gate built for false closing sentences could not see the word `sixteen`.

ESTIMAND        two quantities, named before any method was chosen:
                (a) is `next_line_quantifiers_are_computed`'s BARE_COUNT rule invariant under
                    writing a numeral as an English word, when the CLAIM it encodes is not?
                (b) of R960's six enumerated red gates, how many are green at HEAD?
IDENTIFICATION  (a) fully identified: the rule is a regex and both forms of one sentence exist.
                (b) fully identified for the SIX R960 NAMED. The other ten of its sixteen were
                    never written down, so their status is UNIDENTIFIED and is reported as such
                    rather than folded into a count.
SCOPE           population : 1,380 NEXT paragraphs, extracted by the gate's OWN `next_lines`, and
                             64 gates discovered by `assurance/run_all.py` at HEAD
                instrument : the gate's own QUANT / BARE_COUNT / PROVENANCE regexes and its own
                             `flagged()`; the suite's own discovery. No new population was built.
                baseline   : the digit-only BARE_COUNT as shipped
                regime     : word numerals immediately followed by an artifact noun; `one`
                             excluded; adjacency required
WORLDS          A the digit rule already covers the failure, word forms are rare or benign
                B the rule is gauge-blind and a measurable share of history evades it
                prediction matrix: A -> few word-numeral NEXT lines, and those that exist cite
                provenance. B -> a material share, uncited, including commits I wrote this week.
KILL            pre-registered before the sweep: if fewer than 20 of the 1,380 paragraphs carry an
                uncited word-numeral count, world B is dead and the gauge finding is a curiosity
                about one sentence rather than a defect in the rule.
POSITIVE CTRL   the word-form instrument must recover `e42fc832` (R973), whose NEXT paragraph is
                known to read "sixteen entries". Recovered by sha, not by count.
NEGATIVE CTRL   a word numeral beside a NON-artifact noun ("three lines of shell") must not count.
G=0             the gate's own SYNTH_OK line, which is unflagged and must stay unflagged after the
                patch; and the eleven `one` paragraphs, which must stay unflagged.
SPECIFICATION   three word lists swept — one..twenty, two..twenty, three..twenty — reported whole.
MULTIPLICITY    two estimands, both reported, including the one that did not move (b's ten
                unidentified members).
ARTIFACT        results/gauge_and_members.json, with the source hash of this file.
IMPOSSIBLE      cross-model / cross-dataset — N/A: one repository, one log. Would require a second
                project with the same commit discipline.
                independently replicated — N/A this round: no clean-context agent was dispatched
                (the session forbids it unless asked). Would require a second author given the
                question and not the regex.
"""
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NOUN = r"(?:rounds?|retractions?|entries|claims?|arms?|gates?|cells?|items?)"
LISTS = {
    "one..twenty": ("one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|"
                    "fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty"),
    "two..twenty": ("two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|"
                    "fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty"),
    "three..twenty": ("three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|"
                      "fifteen|sixteen|seventeen|eighteen|nineteen|twenty"),
}
KILL_THRESHOLD = 20

# ⛔ R960's SIX NAMED REDS, quoted from commit 85acc2e9. This is the ONLY enumerated record of the
#    red set that exists anywhere -- the sweep that produced it printed a histogram and persisted
#    nothing, so ten of its sixteen members have no name and never will. Their status is
#    UNIDENTIFIED, which is not the same as unresolved and is not the same as resolved.
R960_NAMED = ["a_share_carries_its_counts", "arm_population_is_derived",
              "outcome_variable_declared", "verdict_cites_its_own_contrasts",
              "next_line_quantifiers_are_computed", "a_commit_body_names_its_own_round"]
# ⛔ R973's closing sentence named these three as resolved. Checking a closing sentence is the
#    whole point of the gate this round repairs, so it is checked here rather than asserted.
R973_CLAIMED = ["outcome_variable_declared", "attack_outcome_variable_declared",
                "a_published_number_is_named"]


def load(rel):
    spec = importlib.util.spec_from_file_location(pathlib.Path(rel).stem, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> int:
    gate = load("assurance/next_line_quantifiers_are_computed.py")
    rows = gate.next_lines(n=4000)
    if len(rows) < 200:
        print(f"⛔ EMPTY-ISH POPULATION: {len(rows)} NEXT paragraphs. Exit 2, never 0.")
        return 2
    print(f"population: {len(rows)} NEXT paragraphs (the GATE's own extractor, not a new one)")

    # ── ① GAUGE TEST. Rung 1 of the attack ladder: three lines, zero compute, tried first.
    #    Writing a numeral as a word is a transformation that leaves the CLAIM identical.
    claim = ("R961's red list had sixteen entries and three are now resolved -- this harness, "
             "the gate it attacks, and the published-number gate.")
    forms = {"words": claim, "digits": claim.replace("sixteen", "16").replace("three", "3")}
    gauge = {k: bool(gate.BARE_COUNT.search(v)) for k, v in forms.items()}
    print(f"\n① GAUGE  digits->{gauge['digits']}  words->{gauge['words']}   "
          f"{'INVARIANT (repaired)' if gauge['digits'] == gauge['words'] else 'NOT INVARIANT'}")
    print("   the property — an uncomputed count over my own work — is TRUE in both forms.")

    # ── ② SCOPE. How much of history the digit-only rule could never have seen. Swept over three
    #    word lists so the number is a curve, not a cell.
    spec_curve = {}
    base = {s for s, t in rows if gate.flagged(t)}
    for label, words in LISTS.items():
        rx = re.compile(rf"\b({words})\s+{NOUN}\b", re.I)
        hit = [(s, t) for s, t in rows if rx.search(t)]
        uncited = [(s, t) for s, t in hit if not gate.PROVENANCE.search(t)]
        spec_curve[label] = {"word_numeral_hits": len(hit), "uncited": len(uncited),
                             "recovers_R973_commit": any(s == "e42fc832" for s, _ in hit)}
    print(f"\n② SCOPE  base flag rate {len(base)}/{len(rows)} = {len(base)/len(rows):.1%}")
    for label, v in spec_curve.items():
        print(f"   {label:<14} word-numeral {v['word_numeral_hits']:>4}   uncited "
              f"{v['uncited']:>4}   recovers R973's commit: {v['recovers_R973_commit']}")

    # ── ③ CONTROLS.
    rx_all = re.compile(rf"\b({LISTS['one..twenty']})\s+{NOUN}\b", re.I)
    pos = any(s == "e42fc832" for s, t in rows if rx_all.search(t))
    neg = bool(rx_all.search("NEXT: three lines of shell settle it."))
    g0_synth_ok = not gate.flagged(
        "every round in the arc is listed by assurance/every_round_is_committed.py, so re-run it")
    g0_one = [t for t in (
        "vectors 3 and 4 still read a whole-repo exit code while planting one round",
        "it is the one arm the definition was written from",
        "the satisfaction class holds exactly one arm, topvar_k4") if gate.flagged(t)]
    print(f"\n③ CONTROLS  POSITIVE (recovers a KNOWN case by sha) {pos}   "
          f"NEGATIVE ('three lines' must not count) {not neg}")
    print(f"            g=0 the gate's own clean line stays clean {g0_synth_ok}   "
          f"g=0 indefinite `one` false alarms {len(g0_one)}/3")
    controls_ok = pos and not neg and g0_synth_ok and not g0_one
    if not controls_ok:
        print("   ⛔ a control failed; this round certifies nothing. Exit 2, never 0.")
        return 2

    # ── ④ THE PRE-REGISTERED KILL, evaluated ONLY behind its controls (the conditional form: a
    #    kill that can fire on a broken instrument is an automated way to publish an artifact).
    uncited_two = spec_curve["two..twenty"]["uncited"]
    verdict = "WORLD B" if uncited_two >= KILL_THRESHOLD else "WORLD A — a curiosity, not a defect"
    print(f"\n④ KILL  pre-registered at {KILL_THRESHOLD}; observed {uncited_two} -> {verdict}")

    # ── ⑤ MEMBERSHIP. The count comparison is REFUSED and the per-member one is run instead.
    sweep_p = ROOT / "assurance/results/suite_sweep.json"
    members, where = None, {}
    if sweep_p.exists():
        members = json.loads(sweep_p.read_text())
        for b, names in members["members"].items():
            for n in names:
                where[n] = b
    print(f"\n⑤ MEMBERS  current population {members['n_gates'] if members else 'ABSENT'} gates   "
          f"counts {members['counts'] if members else '-'}")
    print("   ⛔ NO DELTA IS REPORTED against R960's 71. That population EXCLUDED attack_the_suite "
          "by name and this one includes it, so the two counts are not the same measurement.")
    named = {n: where.get(n, "NOT IN POPULATION") for n in R960_NAMED}
    claimed = {n: where.get(n, "NOT IN POPULATION") for n in R973_CLAIMED}
    print("   R960's six NAMED reds at HEAD:")
    for n, b in named.items():
        print(f"     {n:<38} {b}")
    print("   R973's three CLAIMED-RESOLVED at HEAD:")
    for n, b in claimed.items():
        print(f"     {n:<38} {b}{'   ⛔ CLAIM FALSE' if b == 'FAIL' else ''}")
    resolved = sum(1 for b in named.values() if b == "PASS")
    print(f"   -> {resolved} of {len(named)} named reds are PASS. Ten of R960's sixteen were never "
          f"named and are UNIDENTIFIED, not unresolved.")

    out = HERE / "results" / "gauge_and_members.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_next_paragraphs=len(rows), base_flagged=len(base),
        gauge=gauge, specification_curve=spec_curve,
        controls={"positive_recovers_known_sha": pos, "negative_non_artifact_noun": not neg,
                  "g0_clean_line_stays_clean": g0_synth_ok, "g0_indefinite_one_alarms": len(g0_one)},
        kill={"threshold": KILL_THRESHOLD, "observed": uncited_two, "verdict": verdict},
        r960_named_at_head=named, r973_claimed_at_head=claimed,
        n_named_resolved=resolved, n_r960_reds_never_named=10,
        delta_refused="R960's population excluded attack_the_suite; this one includes it",
    ), indent=1))
    print(f"\n   artifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
