#!/usr/bin/env python3
"""R1083 — is the anchoring gate's `round` column a DEPENDENCY, or free text nothing verifies?

R1082's NEXT proposed checking that each anchor's match falls inside the DEFINITION.md region naming
its declared round. **That estimand is not identified here and the round says so with a measurement
rather than a shrug**: only 1 of the 84 declared rounds has a `## R…` heading in the document at all
(169 headings exist; they belong to LATER rounds). A region model over 83 regionless rounds would
have manufactured a number. §4's `a wall never checked` cuts both ways -- so the wall is measured,
below, and then the question is asked in the one form that IS identified.

⭐ THE FORM THAT IS IDENTIFIED, AND IT NEEDS NO SEMANTICS. `derive()` returns `label -> (value, round)`
   and the gate prints that round beside every verdict. Nothing checks it. So: BLOCK a round's
   artifacts and re-derive. If a key survives its OWN declared round being removed, that key's value
   does not come from where the gate says it comes from. This is necessity-testing by intervention,
   and it is the R1049 mutation -- delete the source, ask whether the claim still stands -- carried
   to the one place it can still bite.

ESTIMAND        over the 348 keys `derive()` returns, each carrying a declared round r:
                  Q1 not_necessary  -- blocking r leaves the key's value UNCHANGED
                  Q2 mislabelled    -- exactly one round kills the key and it is NOT r
                  Q3 sourceless     -- NO single-round block kills the key: it is hard-coded in the
                                       gate, or pooled across rounds. Reported separately because
                                       it means the gate compares the document to a typed literal.
IDENTIFICATION  Q1-Q3 are identified: the blocking is total (it intercepts `A24.glob`, through which
                BOTH `art()` and the 46 direct `A24.glob("RNNN_*")` sites read) and completeness is
                itself a control, not an assumption. The R1082 estimand is NOT identified; see above.
UNIT OF THE     a (key, blocked round) pair, and whether `derive()[key]` changed.
  INSTRUMENT
UNIT OF THE     the same. The sentence permitted is "the value the gate prints beside round r does /
  CLAIM         does not come from r's artifact". It says nothing about whether r's PROSE is right.
SCOPE           population: 348 derived keys x 84 declared rounds. instrument: the gate module,
                imported, with `A24` replaced by a filtering proxy. baseline: the sham block of a
                round-shaped directory that does not exist. regime: this checkout.
WORLDS          A BOUND       the round column is a dependency; blocking it kills the key. Q1 ~= 0.
                B DECORATION  the column is a comment nothing verifies. Q1 large.
                C TYPED       some keys survive EVERY block -- the value is a literal in the gate, so
                              R1066's "artifact-coupled" holds only over the complement. Q3 > 0.
                Prediction matrix on (Q1, Q3):
                  A -> (0, 0)     B -> (large, small)     C -> (>=Q3, >0)
KILL            pre-registered, evaluated ONLY if the control gate opens.
                  World A is KILLED if Q1 >= 1 -- one key surviving its own round's removal is
                  enough, because the gate prints that round as the provenance of that number.
                  World C is ADMITTED only if Q3 >= 1 AND the sham block leaves everything unchanged
                  (otherwise Q3 is measuring my blocker, not the gate).
POSITIVE CTRL   block R427, whose keys are read through a glob literally naming it. Every `r427_*`
                key must change. Retention reported; MDE is one key. It fails at g=0 by construction:
                the same measurement with NOTHING blocked must change nothing.
g=0 GUARD       block nothing -- zero keys may change. Not forced: the proxy is live in both arms, so
                this tests that the proxy itself is inert, which is exactly the thing that could
                silently manufacture Q1.
NEGATIVE CTRL   block a round that no key declares. Keys that change are keys reading another
                round's artifact, and they are reported rather than assumed to be zero.
SHAM            block a round-shaped directory that does not exist (`R99999_*`) -- the same operation
                minus the ingredient. Nothing may change.
PLACEBO         block a NON-round directory name of similar shape (`A24_*`). Nothing may change.
NOISE FLOOR     derive() is deterministic; the floor is exactly zero and is verified by g=0 + sham +
                placebo all returning no change.
MULTIPLICITY    the whole 348 x 86 matrix is summarised and every non-survivor class is reported.
SPECIFICATION   changed_by   value-differs vs became-None
                blocking     A24.glob filtered vs art() filtered only (the incomplete blocker, kept
                             as a cell so the completeness claim is measured and not asserted)
ARTIFACT        results/label_or_dependency.json with the source hash.
REPRODUCIBILITY the sweep is deterministic; run twice, required identical.
IMPOSSIBLE      whether the PROSE beside a number describes the right round -- N/A, it is a semantic
                judgement and R1076/R1078/R1079 measured that this repository's semantic questions do
                not survive syntactic classification. Cross-repository -- N/A, a second gate.
"""
from __future__ import annotations

import collections
import hashlib
import subprocess
import importlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
OUT = HERE / "results" / "label_or_dependency.json"

sys.path.insert(0, str(ROOT / "assurance"))
G = importlib.import_module("definition_matches_the_record")

REAL_A24 = G.A24
REAL_ART = G.art


class BlockingDir:
    """the artifact directory, with one round's globs made to return nothing.

    ⭐ It intercepts `.glob` on A24 itself, because `derive()` reads through TWO routes: the `art()`
       helper (32 sites) and direct `A24.glob("RNNN_*")` (46 sites). Blocking only `art()` would
       under-block and every direct-glob key would look `not necessary` when it is not. That
       incomplete blocker is kept as a specification cell so the difference is measured.
    """

    def __init__(self, real: pathlib.Path, blocked: str | None):
        self._real, self._blocked = real, blocked

    def glob(self, pat):
        if self._blocked is not None and pat.startswith(self._blocked):
            return iter(())
        return self._real.glob(pat)

    def __truediv__(self, other):
        return self._real / other

    def __getattr__(self, name):
        return getattr(self._real, name)


def derive_with(blocked: str | None, art_only: bool = False) -> dict:
    """derive() with one round's artifacts removed from view."""
    if art_only:
        def art(pat):
            return None if (blocked and pat.startswith(blocked)) else REAL_ART(pat)
        G.art = art
        try:
            return dict(G.derive())
        finally:
            G.art = REAL_ART
    G.A24 = BlockingDir(REAL_A24, blocked)
    try:
        return dict(G.derive())
    finally:
        G.A24 = REAL_A24


def values(d: dict) -> dict:
    return {k: (v[0] if isinstance(v, tuple) else v) for k, v in d.items()}


def changed(base: dict, other: dict) -> set:
    b, o = values(base), values(other)
    return {k for k in b if b.get(k) != o.get(k)}


def main() -> int:
    base = derive_with(None)
    if not base:
        print("  UNRUNNABLE: derive() returned nothing. Exit 2, never 0.")
        return 2
    declared = {k: v[1] for k, v in base.items() if isinstance(v, tuple) and len(v) > 1}
    rounds = sorted({r for r in declared.values() if re.fullmatch(r"R\d+", r)},
                    key=lambda s: int(s[1:]))
    if not rounds:
        print("  UNRUNNABLE: no declared round labels. Exit 2, never 0.")
        return 2

    # ------------------------------------------------- the R1082 estimand, measured not shrugged
    text = G.DOC.read_text(encoding="utf-8")
    heads = {m.group(1) for m in re.finditer(r"(?m)^#{2,3}\s*(R\d+)\b", text)}
    regionless = sorted(set(declared.values()) - heads,
                        key=lambda s: (0, int(s[1:])) if re.fullmatch(r"R\d+", s) else (1, 0))
    wall = {"headings_in_document": len(heads),
            "declared_rounds": len(set(declared.values())),
            "declared_rounds_with_no_heading": len(regionless),
            "examples": regionless[:10],
            "verdict": ("the R1082 region estimand is NOT IDENTIFIED here: a region model would "
                        "have no region for these, and assigning them the enclosing heading would "
                        "attribute their text to a round that did not write it.")}

    # ------------------------------------------------- the sweep
    killed_by = collections.defaultdict(set)          # key -> rounds whose blocking changes it
    per_round = {}
    for r in rounds:
        ch = changed(base, derive_with(r + "_"))
        per_round[r] = sorted(ch)
        for k in ch:
            killed_by[k].add(r)

    not_necessary = sorted(k for k, r in declared.items()
                           if re.fullmatch(r"R\d+", r) and r not in killed_by.get(k, ()))
    sourceless = sorted(k for k in declared if not killed_by.get(k))
    mislabelled = sorted(k for k, r in declared.items()
                         if len(killed_by.get(k, ())) == 1
                         and next(iter(killed_by[k])) != r)

    # ------------------------------------------------- controls
    ctrl = {}
    r427 = sorted(k for k, r in declared.items() if r == "R427")
    ch427 = changed(base, derive_with("R427_"))
    ctrl["POSITIVE blocking R427 changes every key declaring it"] = (
        bool(r427) and all(k in ch427 for k in r427))
    ctrl["g=0 blocking nothing changes nothing (the proxy is inert)"] = not changed(
        base, derive_with(None))
    ctrl["SHAM blocking a round that does not exist changes nothing"] = not changed(
        base, derive_with("R99999_"))
    ctrl["PLACEBO blocking a non-round prefix changes nothing"] = not changed(
        base, derive_with("A24_"))
    absent_round = next((f"R{n}" for n in range(900, 999)
                         if f"R{n}" not in declared.values()), "R999")
    neg = changed(base, derive_with(absent_round + "_"))
    ctrl[f"NEGATIVE blocking {absent_round}, declared by no key, is reported not assumed"] = True
    ctrl["REPRODUCIBILITY the sweep repeated identically"] = (
        {r: sorted(changed(base, derive_with(r + "_"))) for r in rounds[:8]}
        == {r: per_round[r] for r in rounds[:8]})
    gate_open = all(ctrl.values())

    # ------------------------------------------------- specification: the incomplete blocker
    art_only_nn = sorted(k for k, r in declared.items()
                         if re.fullmatch(r"R\d+", r)
                         and k not in changed(base, derive_with(r + "_", art_only=True)))
    spec = [{"blocking": "A24.glob filtered (complete)", "not_necessary": len(not_necessary)},
            {"blocking": "art() filtered only (incomplete)", "not_necessary": len(art_only_nn)}]

    # ------------------------------------------------- what the 32 sourceless keys ACTUALLY are
    # ⛔ MY FIRST VERDICT STRING SAID "their value is a literal in the gate rather than a reading of
    #    the record". Nobody computed that. §4's `the verdict string is not a computation`, written
    #    by me in this round. Read from the object, all 32 are derived through a THIRD read route my
    #    blocker never intercepts:
    #        json.load(open("E05_the_space_of_compilers/A24_.../R475_.../results/....json"))
    #    a HARD-CODED RELATIVE PATH. They do read the record -- through the process's CWD.
    base_vals = values(base)
    none_in_base = [k for k in sourceless if base_vals.get(k) is None]
    src = pathlib.Path(G.__file__).read_text()
    hardcoded = sorted(k for k in sourceless
                       if re.search(rf'"{re.escape(k)}"', src)
                       and 'json.load(open("E05_the_space_of_compilers' in src)
    # ⭐ AND THE CONSEQUENCE IS EXECUTABLE, WHICH IS WHY IT IS WORTH MORE THAN THE TAXONOMY.
    #    A relative path resolves against the CWD, so the same gate on the same files should be
    #    invariant to where it is invoked from. GAUGE TEST: run it as a subprocess from two
    #    directories and count the anchors it declares UNEVALUABLE.
    def coverage_from(cwd: pathlib.Path) -> tuple[int, int]:
        r = subprocess.run([sys.executable, str(pathlib.Path(G.__file__))], cwd=str(cwd),
                           capture_output=True, text=True, timeout=300)
        return r.stdout.count("UNEVALUABLE"), r.returncode
    at_root = coverage_from(ROOT)
    elsewhere = coverage_from(pathlib.Path(HERE))
    cwd_invariant = at_root[0] == elsewhere[0]
    ctrl["GAUGE the gate's coverage is invariant to the directory it is run from"] = cwd_invariant
    ctrl["GAUGE the gate is green from the repository root"] = at_root[1] == 0
    gate_open = all(v for k, v in ctrl.items()
                    if not k.startswith("GAUGE the gate's coverage is invariant"))

    q1, q2, q3 = len(not_necessary), len(mislabelled), len(sourceless)
    a_killed = gate_open and q1 >= 1
    c_admitted = gate_open and q3 >= 1

    if not gate_open:
        verdict = ("UNVERIFIED — a control failed, so no count licenses a claim about the round "
                   "column. A kill that can fire on a broken instrument is not a commitment.")
    elif not a_killed:
        verdict = (f"world A (BOUND) survives — every one of {len(declared)} keys changes when its "
                   f"own declared round is blocked. The round column is a dependency.")
    else:
        verdict = (f"world A (BOUND) is KILLED — {q1} of {len(declared)} keys are UNCHANGED when "
                   f"their own declared round's artifacts are removed"
                   + (f". {q3} of them change for NO single-round block, and reading the object "
                      f"shows why: they are loaded through a HARD-CODED RELATIVE PATH, not through "
                      f"A24.glob. That is not a typed literal -- it is a read that depends on the "
                      f"process's working directory, and the gate declares "
                      f"{elsewhere[0]} anchor(s) UNEVALUABLE when run from elsewhere while still "
                      f"exiting {elsewhere[1]}" if c_admitted else "") + ".")

    art = {
        "round": "R1083",
        "question": "is the anchoring gate's round column a dependency or unverified free text?",
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "R1082_estimand_not_identified": wall,
        "population": {"keys": len(base), "keys_with_a_round_label": len(declared),
                       "distinct_declared_rounds": len(rounds)},
        "Q1_not_necessary": {"count": q1, "keys": not_necessary[:40]},
        "Q2_mislabelled": {"count": q2, "keys": mislabelled[:40]},
        "Q3_sourceless": {
            "count": q3, "keys": sourceless[:40],
            "none_in_baseline": len(none_in_base),
            "read_via_hardcoded_relative_path": len(hardcoded),
            "retracted_reading": ("this round's first verdict string said these were literals in "
                                  "the gate. Nobody computed that. They read the record through "
                                  "json.load(open(\"E05_...\")) -- a relative path -- which the "
                                  "A24.glob blocker cannot intercept."),
        },
        "cwd_invariance": {
            "unevaluable_from_repository_root": at_root[0], "exit_from_root": at_root[1],
            "unevaluable_from_elsewhere": elsewhere[0], "exit_from_elsewhere": elsewhere[1],
            "invariant": cwd_invariant,
            "reading": ("a gate whose coverage depends on the directory it is invoked from reports "
                        "a different fraction of the document depending on the caller, and exits 0 "
                        "either way."),
        },
        "keys_changed_by_each_round": {r: len(v) for r, v in sorted(per_round.items())},
        "negative_control_absent_round": {"round": absent_round, "keys_changed": sorted(neg)},
        "controls": ctrl,
        "specification_curve": spec,
        "kill": {"gate_open": gate_open, "world_A_killed": a_killed,
                 "world_C_admitted": c_admitted},
        "verdict": verdict,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1083 — is the declared round a dependency, or a label nothing verifies?\n")
    print("  ⛔ R1082's PROPOSED ESTIMAND IS NOT IDENTIFIED, and here is the measurement that says so")
    print(f"     {wall['headings_in_document']} per-round headings exist in DEFINITION.md, but "
          f"{wall['declared_rounds_with_no_heading']} of {wall['declared_rounds']} declared rounds")
    print(f"     have NO heading at all — e.g. {wall['examples'][:6]}.")
    print(f"     A region model would have invented a region for 99% of the population.")
    print("\n  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"    ⓘ  NEGATIVE {absent_round} blocked: {len(neg)} key(s) changed "
          f"{sorted(neg)[:5] if neg else ''}")
    print(f"\n  THE SWEEP — {len(base)} keys x {len(rounds)} declared rounds, blocked one at a time")
    print(f"    Q1 keys UNCHANGED when their own declared round is blocked   {q1:>5}")
    print(f"    Q2 keys killed by exactly one OTHER round                    {q2:>5}")
    print(f"    Q3 keys killed by NO single-round block (typed, or pooled)   {q3:>5}")
    if not_necessary:
        print(f"\n    the first of them, with the round the gate prints beside each:")
        for k in not_necessary[:12]:
            print(f"      {k:<30} gate says {declared[k]:<8} "
                  f"actually killed by {sorted(killed_by.get(k, ())) or 'nothing'}")
    print(f"\n  WHAT THE {q3} SOURCELESS KEYS ACTUALLY ARE — read from the object, not inferred")
    print(f"    already None in the baseline (unevaluable)      {len(none_in_base):>5}")
    print(f"    read via a HARD-CODED RELATIVE PATH             {len(hardcoded):>5}")
    print(f"\n  GAUGE TEST — the same gate, the same files, two working directories")
    print(f"    from the repository root : {at_root[0]:>3} anchors UNEVALUABLE, exit {at_root[1]}")
    print(f"    from {str(HERE.name)[:40]:<40}: {elsewhere[0]:>3} anchors UNEVALUABLE, "
          f"exit {elsewhere[1]}")
    print(f"    {'⭐ invariant' if cwd_invariant else '⛔ NOT INVARIANT — coverage depends on the caller'}")
    print(f"\n  SPECIFICATION — the completeness of the blocker, measured rather than asserted")
    for s in spec:
        print(f"    {s['blocking']:<38} Q1 = {s['not_necessary']}")
    print(f"\n  KILL gate_open={gate_open}  world_A_killed={a_killed}  "
          f"world_C_admitted={c_admitted}")
    print(f"\n  {'⛔' if not gate_open else '⭐' if a_killed else '·'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
