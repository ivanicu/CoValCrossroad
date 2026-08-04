"""R380 — the gate reported 17 stale registry entries from a glob that matched zero files.

R379's NEXT chose the cheapest of the ten red gates: `donor_numbers_carry_their_draw_scope`, one of
three that exit 1 while opening ZERO round artifacts. Its output is:

    rounds constructing a donor mapping: 0   registry entries: 17
    FINDING: 17 registry entr(ies) name a round that no longer constructs a donor mapping --
             the registry has drifted from the source

⛔ THAT FINDING IS A CONVICTION HANDED DOWN BY AN INSTRUMENT THAT READ NOTHING. `0` from a detector
   never shown to return non-zero is silence, not a verdict -- and here it is worse than silence,
   because the sentence it produces is an ACCUSATION against seventeen rounds. A false acquittal is
   permanent because nobody re-examines a cleared claim; a false CONVICTION is worse in one specific
   way: it invites a repair to the innocent party. The obvious next action on that output is to
   delete seventeen registry entries.

⛔ AND THE GATE'S OWN DOCSTRING PREDICTED THIS, WHICH IS WHY IT IS WORTH A ROUND. It says the
   registry "is not trusted -- it is VERIFIED against the source tree on every run", and warns of
   "a check that is right about what it iterates over and blind to what is missing". It then
   iterates `ROOT/rounds/E*/A*/R*/run.py`. The confession was written and the code did the opposite.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES. If the seventeen
   rounds genuinely no longer construct a donor mapping, then pointing the detector at the real tree
   still finds nothing and the registry really has drifted. The two worlds differ in what the
   REPAIRED detector returns, which is measured here rather than argued from a glob that is
   obviously wrong -- because "obviously wrong" is how a plausible story replaces a measurement.

⛔ AND FIXING A GATE IS NOT THE SAME AS MAKING IT GREEN. This gate has TWO halves. Repairing only
   the half that is easy to repair would turn it green while the other half examines nothing, which
   is `realstat §4 · empty population passes` introduced BY a repair. Both halves are measured.

ESTIMAND        (a) how many round sources the detector finds under its CURRENT path vs under the
                    tree's actual layout;
                (b) of the 17 registry entries, how many the REPAIRED detector locates;
                (c) whether GATE 2's population -- README rows naming a round -- still exists at all;
                (d) whether a repaired GATE 1 can still FAIL, demonstrated with a plant.

IDENTIFICATION  (a)-(c) are exact enumerations over the tree. (d) is a planted positive control with
                a known answer. NOT identified: whether every round the repaired detector finds is
                correctly classified by idiom -- that is the detector's aim, and a third idiom would
                still be invisible. The gate's own docstring already states that limit and this
                round does not improve it.

SCOPE           population: 362 round sources under E0*/A*/R*/ · instrument: the gate's own two
                idiom regexes, unchanged · baseline: the gate's current behaviour · regime: HEAD.

WORLDS
  W-PATH-BLIND     the repaired detector finds the registry's rounds. The FINDING was false, the
                   registry is not drifted, and the defect is the path -- so the correct repair is
                   to the GATE, and deleting registry entries would have destroyed the record.
  W-REGISTRY-STALE the repaired detector still finds none of the seventeen. The registry really has
                   drifted and the gate was right for the wrong reason.
  W-MIXED          some found, some not. Then there is BOTH a path bug and real drift, and the two
                   counts separate them.

PREDICTION MATRIX
  W-PATH-BLIND     -> repaired detector locates ~all 17 ; current path matches 0 files
  W-REGISTRY-STALE -> repaired detector locates ~0 of 17 even on the real tree
  W-MIXED          -> strictly between, and the missing ones are NAMED

PRE-REGISTERED KILL -- conditional on the controls, never on a count alone.
    if detector_positive_control_ok and detector_negative_control_ok:
        f = number of the 17 registry rounds the REPAIRED detector locates
        if f == 0        -> W-REGISTRY-STALE
        elif f >= 15     -> W-PATH-BLIND
        else             -> W-MIXED, and the absentees are listed
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  DETECTOR (+)   `R21_donor_distance` contains idiom A at a line I located by grep, INDEPENDENTLY of
                 this gate: `(i + 1 + rng.integers(0, n - 1)) % n`. The repaired detector must find
                 it. A detector that cannot see a case verified by hand is blind.
  DETECTOR (-)   a round with no donor idiom must NOT be flagged. Both directions, because a
                 detector that flagged all 362 would pass the positive control and mean nothing.
  DISARM PROOF   after repair, a PLANTED unregistered round carrying idiom A must make GATE 1 FIRE,
                 and with the plant removed it must not. A repair that cannot fail is a deletion.
  GATE 2 POP     the count of README rows the gate can locate, measured rather than assumed. If it
                 is zero, GATE 2 is vacuous and saying so is the finding -- not passing it.

MULTIPLICITY    no test family. Every count is an enumeration and all are printed.
SEEDS           none -- globs and regexes are deterministic.
ARTIFACT        results/r380_donor_gate.json with the source hash.

IMPOSSIBLE HERE
  a third donor idiom      -- invisible to both regexes, as the gate's own docstring says. Unchanged.
  whether GATE 2's PROPERTY still matters  -- it does; what is gone is its PROXY. Choosing a new
                                              proxy is a design decision, and this round measures
                                              the vacancy rather than filling it silently.
  a second release         -- one release.

EXIT
    0  controls hold and the gate is classified
    1  a control misbehaved -- UNVERIFIED
    2  the tree is unreadable -- never a silent pass
"""
from __future__ import annotations
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
PY = ROOT / ".venv" / "bin" / "python"
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

# the gate's OWN regexes, copied verbatim so this round measures ITS detector and not a new one
IDIOM_A = re.compile(r"\+\s*1\s*\+\s*rng\.integers\(\s*0\s*,\s*n\s*-\s*1\s*\)")
IDIOM_B = re.compile(r"\bdonor\b[^\n]*\bshuffle_map\b|\bshuffle_map\b[^\n]*\bdonor\b", re.S)
OLD_GLOB = "rounds/E*/A*/R*/run.py"
NEW_GLOB = "E0*/A*/R*/run.py"
POS = "R21_donor_distance"


def main() -> int:
    if not GATE.exists():
        print("  UNRUNNABLE: the gate is absent. Exit 2, never 0."); return 2
    src = GATE.read_text()
    m = re.search(r'REGISTRY\s*=\s*\{(.*?)\n\}', src, re.S)
    if not m:
        print("  UNRUNNABLE: cannot read the registry from the gate. Exit 2, never 0."); return 2
    registry = re.findall(r'"(R\d+_[a-z0-9_]+)"', m.group(1))
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R380 · the gate convicted a registry it never read   HEAD {head}\n")

    old = sorted(ROOT.glob(OLD_GLOB))
    new = sorted(ROOT.glob(NEW_GLOB))
    print(f"  THE PATH, measured rather than inferred")
    print(f"    the gate globs `{OLD_GLOB}`  -> {len(old)} files")
    print(f"    the tree actually holds `{NEW_GLOB}` -> {len(new)} files")
    print(f"    registry entries: {len(registry)}")

    def detect(paths):
        out = {}
        for p in paths:
            try:
                s = p.read_text()
            except Exception:
                continue
            i = "A" if IDIOM_A.search(s) else ("B" if IDIOM_B.search(s) else None)
            if i:
                out[p.parent.name] = i
        return out

    found_old = detect(old)
    found_new = detect(new)
    print(f"\n  THE DETECTOR — the gate's OWN two regexes, unchanged, pointed two ways")
    print(f"    under the gate's path : {len(found_old)} donor rounds")
    print(f"    under the real tree   : {len(found_new)} donor rounds")

    # ---- CONTROLS ------------------------------------------------------------------------------
    pos_ok = POS in found_new
    non = [p.parent.name for p in new if p.parent.name not in found_new]
    neg_ok = len(non) > 0 and len(found_new) < len(new)
    print(f"\n  CONTROLS")
    print(f"    DETECTOR (+)  `{POS}` — verified by hand at "
          f"`E01_.../{POS}/run.py:111` — is found: {pos_ok}  "
          f"{'PASS' if pos_ok else 'FAIL — blind to a case confirmed independently'}")
    print(f"    DETECTOR (-)  {len(non)} of {len(new)} rounds carry NO donor idiom and are not "
          f"flagged  {'PASS' if neg_ok else 'FAIL — it flags everything'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the detector is blind in one direction. Exit 1."); return 1

    located = sorted(set(registry) & set(found_new))
    absent = sorted(set(registry) - set(found_new))
    unregistered = sorted(set(found_new) - set(registry))
    print(f"\n  THE SEVENTEEN, re-tried against the real tree")
    print(f"    located by the repaired detector : {len(located)} of {len(registry)}")
    print(f"    still absent                     : {absent if absent else 'none'}")
    print(f"    donor rounds NOT in the registry  : {len(unregistered)}"
          f"{'  ' + str(unregistered) if unregistered else ''}")

    # ---- GATE 2's population, measured -------------------------------------------------------
    readme = (ROOT / "README.md").read_text()
    rows_old = {r: len([l for l in readme.splitlines()
                        if f"rounds/{r})" in l and l.lstrip().startswith("|")])
                for r in registry}
    n_rows_old = sum(rows_old.values())
    mentions = {r: readme.count(r) for r in registry}
    n_mentioned = sum(1 for r in registry if mentions[r])
    print(f"\n  GATE 2's POPULATION, measured rather than assumed")
    print(f"    README table rows the gate can locate (`| ... rounds/<rnd>) ...`): {n_rows_old}")
    print(f"    registry rounds mentioned in README.md at all                   : "
          f"{n_mentioned} of {len(registry)}")
    print(f"    -> GATE 2 is {'VACUOUS — it rules on nothing' if n_rows_old == 0 else 'populated'}")

    # ---- DISARM PROOF: can a repaired GATE 1 still fail? --------------------------------------
    plant_dir = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs" / "R999_plant"
    plant = plant_dir / "run.py"
    plant_dir.mkdir(parents=True, exist_ok=True)
    plant.write_text("# donor idiom A, planted\n"
                     "x = S[i, (i + 1 + rng.integers(0, n - 1)) % n]\n")
    with_plant = detect(sorted(ROOT.glob(NEW_GLOB)))
    fires = ("R999_plant" in with_plant) and ("R999_plant" not in registry)
    plant.unlink(missing_ok=True)
    try:
        plant_dir.rmdir()
    except OSError:
        pass
    without = detect(sorted(ROOT.glob(NEW_GLOB)))
    quiet = "R999_plant" not in without
    print(f"\n  DISARM PROOF — a repaired GATE 1 must still be able to FAIL")
    print(f"    with an unregistered donor round planted : detected = {fires}  "
          f"{'FIRES' if fires else '⛔ BLIND'}")
    print(f"    with the plant removed (g=0)             : detected = {not quiet}  "
          f"{'silent, correctly' if quiet else '⛔ fires on nothing'}")
    disarm_ok = fires and quiet

    # ---- VERDICT -------------------------------------------------------------------------------
    print()
    if len(located) == 0:
        print(f"  W-REGISTRY-STALE — even against the real tree the detector locates none of the")
        print(f"  {len(registry)} registry rounds. The registry really has drifted and the gate was")
        print(f"  right, for a reason it had not established.")
        v = "W_REGISTRY_STALE"
    elif len(located) >= len(registry) - 2:
        print(f"  W-PATH-BLIND — the repaired detector locates {len(located)} of {len(registry)}")
        print(f"  registry rounds, while the gate's own glob matches {len(old)} files in the whole")
        print(f"  repository. ⛔ The FINDING was FALSE: the registry has not drifted, the gate never")
        print(f"  read the source it convicted, and the obvious action on its output — delete")
        print(f"  seventeen registry entries — would have destroyed the record to satisfy a typo.")
        v = "W_PATH_BLIND"
    else:
        print(f"  W-MIXED — {len(located)} of {len(registry)} located, {len(absent)} genuinely")
        print(f"  absent: {absent}. There is BOTH a path bug and real drift, and neither reading")
        print(f"  alone was right.")
        v = "W_MIXED"

    if n_rows_old == 0:
        print(f"\n  ⛔ AND REPAIRING ONLY GATE 1 WOULD DISARM THE GATE BY MAKING IT GREEN. GATE 2")
        print(f"     rules on README table rows, and the root README stopped being a per-round")
        print(f"     table: it locates {n_rows_old} rows for {len(registry)} registry rounds, and")
        print(f"     {len(registry) - n_mentioned} of them are not mentioned in it at all. A gate")
        print(f"     whose second half examines nothing must SAY so — exit 2 — never pass quietly.")
        v += "_GATE2_VACUOUS"

    if not disarm_ok:
        print(f"\n  ⚠ THE DISARM PROOF DID NOT HOLD, so no repair is recommended from this round.")
        v += "_NO_SAFE_REPAIR"

    print(f"\n  ⚠ SCOPE: a third donor idiom remains invisible to both regexes, exactly as the")
    print(f"    gate's own docstring states. This round repaired WHERE it looks, never WHAT it")
    print(f"    recognises, and the two are different claims.")

    art = dict(stamp(str(SELF)), head=head, old_glob=OLD_GLOB, new_glob=NEW_GLOB,
               n_old_files=len(old), n_new_files=len(new), registry=registry,
               found_old=found_old, found_new=found_new, located=located, absent=absent,
               unregistered=unregistered, gate2_rows=n_rows_old, gate2_mentioned=n_mentioned,
               controls=dict(detector_pos=pos_ok, detector_neg=neg_ok,
                             disarm_fires=fires, disarm_quiet=quiet),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r380_donor_gate.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
