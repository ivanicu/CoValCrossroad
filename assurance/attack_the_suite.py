"""Point every check at the state it exists to detect: ABSENCE.

Entry 64. Five of six checks returned exit 0 on an empty population -- including
one built two turns earlier specifically to catch delivery failures. Each had
been tested against the defect it hunts and none against having nothing to hunt
in. A `_floor()` was added to each; this verifies it, for all of them, rather
than for the one I happened to demonstrate.

For each check: empty its input, confirm exit 2 (not 0), restore, confirm exit 0.
Everything is restored in a `finally`, and the final line re-runs the live suite
so a broken restore cannot pass silently.

This does NOT replace the per-check attack scripts, which inject the specific
defect each check hunts. It covers the axis those all missed.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# The interpreter that is RUNNING this file, not a path guessed relative to the
# repo. A clean-clone run (entry 114) found this was the only check that could
# not run from a fresh clone: it invoked <repo>/.venv/bin/python, which exists
# only in the working copy. The first patch wrote `ROOT / sys.executable`, which
# works only because pathlib discards the left side when the right is absolute --
# accidentally correct, so it is written plainly instead.
PY = sys.executable


def run(check: str) -> int:
    return subprocess.run([PY, f"assurance/{check}.py"], cwd=ROOT,
                          capture_output=True, text=True).returncode


def empty_manifest_claims():
    p = ROOT / "assurance/MANIFEST.json"
    bak = p.read_text()
    d = json.loads(bak)
    d["claims"] = []
    p.write_text(json.dumps(d, indent=1))
    return lambda: p.write_text(bak)


def hide_rounds():
    """Empty the round population. There is no longer a single `rounds/` directory to move -- the
    EPOCHS sit at the repository root -- so each is moved separately and restored separately. A
    version that moved one path would silently hide NOTHING and report every check as refusing on an
    empty population it still had.

    ⚠ 2026-08-02: this matched `^\d\d_` and the EAR restructure renamed every one of those to
    `E\d\d_`. The harness then hid NOTHING, every gate kept its full population, passed, and this
    file reported 9 of 18 gates BROKEN -- a false accusation against nine working checks, produced
    by its own setup step no-oping. The assert below is why the class is survivable at all, and it
    is now also anchored on the count, because an assert that only tests non-emptiness passes on a
    single stray directory."""
    import re as _re
    camps = sorted(p for p in ROOT.iterdir()
                   if p.is_dir() and _re.match(r'^E\d\d_', p.name))
    assert len(camps) >= 2, (
        f"found {len(camps)} epoch directories: this harness would hide nothing and then report "
        f"every gate as passing on a population it still had")
    tmp = Path(tempfile.mkdtemp(prefix="attack_rounds_"))
    moved = []
    for c in camps:
        shutil.move(str(c), str(tmp / c.name))
        moved.append(c)
    def restore():
        for c in moved:
            shutil.rmtree(c, ignore_errors=True)
            shutil.move(str(tmp / c.name), str(c))
        shutil.rmtree(tmp, ignore_errors=True)
    return restore


def empty_frozen_registry():
    p = ROOT / "covalx/frozen.py"
    bak = p.read_text()
    i = bak.index("REGISTRY = {")
    j = bak.index("}", i)
    p.write_text(bak[:i] + "REGISTRY = {}\n" + bak[j + 1:])
    return lambda: p.write_text(bak)


def empty_prose():
    """Blank EVERY document the framing check scans, and leave no heading behind.

    A first version blanked only README.md and wrote "# README" into it. That
    failed twice over: the check also scans FROZEN.md and PREREGISTRATION.md, and
    a heading IS an assertion position, so the population it floors on was never
    empty. The check was reported BROKEN for my emptier's fault.
    """
    paths = [ROOT / n for n in ("README.md", "FROZEN.md", "PREREGISTRATION.md")]
    baks = {p_: p_.read_text() for p_ in paths if p_.exists()}
    for p_ in baks:
        p_.write_text("")
    def restore():
        for p_, t in baks.items():
            p_.write_text(t)
    return restore


def empty_corrections_registry():
    """Empty the CORRECTED registry corrections_propagated floors on.

    Its floor is `len(files) * len(CORRECTED)` -- a GRID SIZE. Blanking documents
    cannot empty it, because the files still exist. Only the registry can.
    """
    q = ROOT / "assurance/corrections_propagated.py"
    bak = q.read_text()
    i = bak.index("CORRECTED = [")
    j = bak.index("\n]", i)
    q.write_text(bak[:i] + "CORRECTED = []" + bak[j + 2:])
    return lambda: q.write_text(bak)


# (check, how to empty its population, expected exit when emptied, why)
#
# Expected 2 = "observed nothing", the entry-64 floor.
#
# registries_are_satisfied expects 1, and that is the design working rather than
# an exception being carved for it. It enumerates from the REQUIREMENT -- the
# rounds FROZEN.md names -- so emptying the registry does not blind it, it makes
# it report 11 rounds that should be registered and are not. A check that knows
# what OUGHT to exist cannot be silenced by deleting what does. That is exactly
# what entry 60 built it to do, and it is why this row differs.
CASES = [
    ("scope_reaches_the_reader", empty_manifest_claims, 2,
     "zero claims in the manifest -> nothing to check"),
    ("every_round_reaches_the_readme", hide_rounds, 2,
     "zero rounds with results -> nothing to check"),
    ("no_withdrawn_framings", hide_rounds, 2,
     "zero results files to scan -> nothing to check"),
    ("outcome_variable_declared", hide_rounds, 2,
     "zero gold-scored rounds -> nothing to check"),
    ("registries_are_satisfied", empty_frozen_registry, 1,
     "empty registry is a DETECTED FAILURE: FROZEN.md still names 11 rounds"),
    ("results_are_not_degenerate", hide_rounds, 2,
     "zero results files to read -> nothing to check (entry 137)"),
    ("retired_framing_in_emittable_source", hide_rounds, 2,
     "zero source files to parse -> nothing to check (entry 143)"),
    # Expect 1, not 2, and the difference is the point. Its registry names the 15
    # rounds that construct a donor mapping, so hiding the rounds does not empty
    # its input -- it makes every entry STALE and the completeness gate fires. A
    # check that knows what ought to exist cannot be silenced by deleting what
    # does, which is the same property registries_are_satisfied has (entry 168).
    ("donor_numbers_carry_their_draw_scope", hide_rounds, 1,
     "rounds hidden -> 15 registry entries go stale: a DETECTED failure, not silence"),
    # Same shape, same reason (entry 173): its registry names the 17 rounds that apply
    # the majority/seed filter, so hiding the rounds makes every entry stale rather
    # than emptying its input. Unlike the donor check it carries NO per-round
    # judgement -- applying the filter is a property of the source, so the rule is
    # flat: apply it, disclose it.
    ("seed_filter_is_disclosed", hide_rounds, 1,
     "rounds hidden -> 17 registry entries go stale: a DETECTED failure, not silence"),
    # Entry 174. Its population is the DOCUMENTS, which hide_rounds does not touch, so
    # it still finds all 257 links and reports them unresolvable -- a detected failure
    # from a population it did not lose. It returns 2 only if a document has no round
    # links at all, which is the genuine "nothing to check".
    ("round_links_resolve", hide_rounds, 1,
     "rounds hidden -> every one of the 257 links stops resolving: DETECTED, not silence"),
    # Added at R340. Its population is the SEARCH CORPUS, and three of its four historical
    # self-test cases (R306, R295, R250) live in round directories -- so hiding the rounds makes
    # those three stop being found and the self-test returns 1, DRIFTED. That is the failure it is
    # supposed to have: an instrument that no longer finds work it is known to contain must say so,
    # because a clean run from it after that would be silence. The fourth case is db/ledger.py,
    # which hide_rounds does not touch, so the attack does not empty the population -- it degrades
    # it, which is the harder case to detect and the one worth registering.
    ("next_gradient_is_new", hide_rounds, 1,
     "rounds hidden -> 3 of 4 historical cases stop being found: DETECTED, not silence"),
    # Added at R340. Its population IS the round sources, so hide_rounds empties it -- and its
    # floor must return 2, because "no disjoint pairs found in no files" is silence. Its synthetic
    # control still passes on a planted string (it does not need the tree), which is exactly why
    # the empty-population floor has to exist separately from the control.
    ("point_and_interval_share_a_source", hide_rounds, 2,
     "sources hidden -> zero round sources: nothing to check, not clean"),
    # Added at R340. Its population is the ARTIFACTS, reached through the coherence scanner, so
    # hiding them leaves it with zero pairs and it must return 2 -- "no pair is off-centre among no
    # pairs" is silence. Its synthetic control still passes on two planted numbers, which is again
    # why the empty floor is separate from the control.
    ("interval_is_centred_on_its_point", hide_rounds, 2,
     "artifacts hidden -> zero paired nodes: nothing to check, not clean"),
    # Entry 198. Its population IS the artifacts, so hiding them empties it -- and its
    # floor returns 2 rather than 0, because "no violations found in nothing" is
    # silence. Its own positive control still passes (it plants a temp tree), which is
    # why the floor has to exist separately.
    ("artifacts_are_internally_coherent", hide_rounds, 2,
     "artifacts hidden -> zero pairs and zero flagged nodes: nothing to check, not clean"),
    # R346. The stamp reader. Its population is rounds carrying a source hash, so hiding
    # the rounds empties it entirely -- and "no drift among no stamps" is silence, so the
    # floor is 2. Note its OTHER empty-population door: KNOWN_STALE.json missing also
    # returns 2, because `new drift` needs a baseline to be new against and a clean run
    # without one would mean nothing. Both doors were attacked; both hold.
    ("source_stamp_is_current", hide_rounds, 2,
     "rounds hidden -> no round carries a stamp: nothing to check, not a clean bill"),
    # Entry 205. DEFINITION.md's numbers are re-derived from the artifacts of the rounds it
    # cites. Hiding the rounds removes every artifact, so NOT ONE assertion is evaluable and
    # it must say so rather than pass a document it could not check. Attacked five ways
    # before being registered: a mutated number -> caught; a reworded claim the regex can no
    # longer locate -> caught, because a claim that vanished is not a pass; the document
    # deleted -> 2; the artifacts hidden -> 2; and the comparison itself neutered to always
    # agree -> its own positive control fails it, which only works because `same()` is the
    # function the gate rules with rather than a restatement of it. That last hole was
    # created BY the first fix, which is where P7 says to look.
    ("definition_matches_the_record", hide_rounds, 2,
     "rounds hidden -> no artifact to re-derive from: nothing to check, not a clean bill"),
    # Entry 206. Its population is COMMIT MESSAGES, which hiding round directories does not
    # touch -- so under the emptying it keeps its full corpus and keeps ruling, which is a
    # DETECTED non-empty run rather than silence. Attacked five ways before registering: a new
    # unlabelled causal NEXT block -> caught; the frozen list emptied -> caught; a frozen entry
    # that stops offending -> caught (shrink-only); the detector neutered to never offend -> its
    # own positive control fails it; no NEXT block anywhere -> exit 2. And its FIRST positive
    # control failed for the right reason: the word UNTESTED appearing as SUBJECT MATTER
    # ("or marked UNTESTED") was read as a label on the claim, so the gate excused the very
    # commit it was built from. A label is a FORM, not a mentioned word.
    # Its population is COMMIT MESSAGES, which `hide_rounds` does not touch -- the same case as
    # `markdown_tables_are_well_formed` above, so `want 0`. ⚠ AND THAT MEANS THE SUITE'S EMPTYING
    # IS NOT A TEST OF THIS CHECK: registering it as `want 1` claimed an emptying that does not
    # apply, and the suite CAUGHT that (23/24) rather than accepting a pass for the wrong reason.
    # Its own empty-population behaviour is verified separately and recorded: with no NEXT block
    # anywhere in the log it exits 2, never 0.
    ("next_gradient_labels_its_hypotheses", hide_rounds, 0,
     "commit messages untouched by hiding rounds -> the corpus is intact and it still rules"),
    # Entry 225. R373's gate. Its population is ROUND SOURCE, which `hide_rounds` removes
    # entirely -- so with the rounds hidden there is no aggregated-unit MDE call site anywhere
    # and it must report an EMPTY POPULATION rather than "every MDE records its denominator".
    # That is the exact failure mode it was written against: a gate that certifies a corpus it
    # never read. `want 2`.
    ("an_mde_records_its_denominator", hide_rounds, 2,
     "rounds hidden -> zero MDE call sites to examine: an empty population never passes"),
    # Entry 201. A REPORT check -- it never gates, so its non-empty exit is 0. With the
    # rounds hidden there is no newest round to measure staleness against, and it
    # returns 2 rather than reporting every section as current.
    ("synthesis_cites_recent_work", hide_rounds, 2,
     "rounds hidden -> no newest round to measure against: nothing to check"),
    # Entry 202. Expect 1, not 2: with the rounds hidden the frame is ABSENT, and an
    # absent frame is a DETECTED failure -- H_fresh would have no admissibility gate
    # and the responses it refers to would be undefined. There is no benign reading of
    # this file being missing, so it must never report "nothing to check".
    # Entry 217. Its population is the DOCUMENTS, which hide_rounds does not touch, so it
    # keeps finding all 794 rows and returns 0. It returns 2 only if a document genuinely
    # contains no table rows.
    ("markdown_tables_are_well_formed", hide_rounds, 0,
     "documents untouched by hiding rounds -> still checks all 794 rows"),
    ("frozen_frame_verifies", hide_rounds, 1,
     "frame hidden -> H_fresh has no admissibility gate: DETECTED, never nothing-to-check"),
    # Entry 144: four checks had a _floor that had never been exercised THROUGH
    # THE CALLING PATH. Verifying a floor by calling it directly proves it raises
    # when handed a zero, not that the check ever hands it one -- which is exactly
    # how retired_framing_in_emittable_source shipped broken and was caught here.
    ("readme_row_carries_the_verdict", hide_rounds, 2,
     "zero rounds with a row and a verdict -> nothing to compare"),
    # Expect 1, not 2. With rounds gone its census input is missing and it returns
    # 1 -- a DETECTED failure, the same convention registries_are_satisfied uses.
    # I first registered it wanting 2, saw BROKEN, and read a piped exit status
    # that reported tail's 0 rather than python's 1, which briefly turned a
    # working check into "it fails toward PASS". `$?` after a pipe is the LAST
    # command's status.
    ("verdict_cites_its_own_contrasts", hide_rounds, 1,
     "missing census input -> detected failure, not a silent pass"),
    ("retired_framing_in_assertion_positions", empty_prose, 2,
     "no prose in ANY scanned document -> no assertion position exists"),
    ("corrections_propagated", empty_corrections_registry, 2,
     "empty registry -> a zero-size document x correction grid"),
]


# Uses sys.executable, NOT a hardcoded .venv path (entry 114). A clean-clone
# run found this check was the only one that could not run from a fresh clone:
# it invoked <repo>/.venv/bin/python, which exists only in the working copy.
def main() -> int:
    results = []
    for check, emptier, want, what in CASES:
        before = run(check)
        restore = None
        try:
            restore = emptier()
            after = run(check)
        finally:
            if restore:
                restore()
        back = run(check)
        # `before` is not always 0. `verdict_cites_its_own_contrasts` exits 1 by
        # design -- it is a report of an open population, not a gate. The harness
        # asserted live==0 for everything, which would have called a
        # working-as-designed check BROKEN for the one reason that is not a fault.
        # What must hold is that emptying CHANGES the answer to the floor value
        # and restoring returns it to whatever it was.
        ok = (after == want and back == before)
        results.append((check, before, after, back, ok))
        print(f"  {'OK    ' if ok else 'BROKEN'} {check:32s} live={before} "
              f"empty={after} (want {want}) restored={back}   ({what})")

    print("\n  Emptied must NEVER be 0. Either the check reports it observed nothing (2)")
    print("  or it detects a real failure from a population it did not lose (1).")
    n = sum(1 for *_, ok in results if ok)
    print(f"\n{n}/{len(results)} checks refuse to pass on an empty population")
    if n != len(results):
        print("  A check that passes with no population has not passed -- it has not run.")
    return 0 if n == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
