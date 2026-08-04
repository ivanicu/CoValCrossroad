"""R394 -- is a round's SOURCE HASH a valid cache key, i.e. are its numbers a function of its source?

R393's NEXT specified a cache keyed on the round's source hash, on the reasoning that a changed round
must invalidate its own row. That reasoning has an unexamined premise, and the premise is the whole
question: a source hash is a valid key ONLY IF an unchanged source yields unchanged numbers. If any
round's output moves while its source stands still, the cache would serve a verification that was
never re-checked -- certifying without checking, which is the exact failure the R380-R393 line exists
to prevent.

⛔ AND THIS IS NOT ONLY ABOUT A CACHE THAT DOES NOT EXIST YET. R388's gate ALREADY re-runs every cited
   round and compares the numbers in the README row against a fresh run. If a round is not
   deterministic, that gate FAILS A CORRECT BACKFILL -- it would convict a row that was written
   honestly. So this measurement is load-bearing for a gate already committed, not merely for an
   optimisation being contemplated. That is why it is worth 90 seconds now rather than after the
   cache is built.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES, in both directions,
   and neither is forced. Nothing in Python guarantees a script prints the same digits twice: set and
   dict iteration over pointer-keyed objects, unseeded rng, wall-clock, filesystem order, thread
   scheduling and hash randomisation all vary at fixed source. Equally, nothing forbids stability.
   The answer is an empirical property of THIS corpus and cannot be derived from the language.

⚠ THE POPULATION IS SELECTED, AND THE SELECTION BIASES TOWARD THE ANSWER I WANT. The subjects are the
  13 rounds R393 timed as COMPLETE inside a 90s cap -- the complete subset of a seeded draw from the
  owing population. Conditioning on "finished fast" preferentially keeps rounds that load no model,
  draw no samples and touch no GPU, which are exactly the rounds most likely to be deterministic. So
  a clean result here is evidence about FAST rounds and is NOT transportable to the two censored ones,
  which are precisely where R393 found 80% of the gate's cost. Named here, repeated in the verdict.

ESTIMAND        for each subject: whether the multiset of numbers in its stdout+stderr is IDENTICAL
                across two consecutive runs at an unchanged source hash. Reported per round with the
                differing tokens named, never as a bare stability rate.

IDENTIFICATION  Exact for variation that reaches printed digits in two draws. NOT identified: rare
                nondeterminism that needs many runs to appear, and variation that changes an artifact
                without changing stdout. Two draws bound the detection probability from below only --
                a round called STABLE here is "not caught in 2 draws", never "proven deterministic".

SCOPE           population: R393's 13 COMPLETE subjects · instrument: the gate's OWN number regex,
                imported rather than re-implemented · baseline: two planted controls · regime:
                consecutive runs in a worktree at HEAD, so the round's committed artifact is present
                on run 1 and overwritten by run 1 on run 2 -- which is the regime the gate runs in.

WORLDS
  W-KEY-VALID       every subject is stable. The source hash is a sound key for this population, and
                    R388's gate is not convicting honest rows on this evidence.
  W-KEY-UNSOUND     >= 1 subject moves at fixed source. Then the cache as specified is not an
                    optimisation but a correctness bug, AND R388's gate has a false-conviction mode
                    that is already live. The named rounds are the finding.

PREDICTION MATRIX
  W-KEY-VALID   -> 0 of 13 unstable
  W-KEY-UNSOUND -> >= 1 unstable, named, with the differing tokens shown

PRE-REGISTERED KILL -- conditional on both controls, never on the count alone.
    if rng_plant_detected and constant_plant_stable:
        if n_unstable == 0 -> W-KEY-VALID    (scoped to fast rounds, see the selection note)
        else               -> W-KEY-UNSOUND, rounds and tokens named
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  PLANT (+)   a script printing an unseeded random draw MUST be classified unstable. Without it, "13
              of 13 stable" is silence from an instrument never shown to return instability.
  PLANT (-)   a script printing a constant MUST be classified stable, so stability is shown to be
              attainable rather than assumed -- the mirror control, which is the one this file's
              own failure table says gets skipped.
  EXTRACTOR   the gate's NUM regex is IMPORTED from the gate, not copied. A re-implemented classifier
              tests the copy; R387 already paid for that lesson.
  EMPTY       fewer than 5 subjects, or a missing worktree -> exit 2, never 0.

MULTIPLICITY    13 subjects x 1 comparison each, every result printed, stable and unstable alike.
SEEDS           the subjects' own; this round adds none. The rng PLANT is deliberately unseeded --
                seeding it would destroy the very property it is built to exhibit.
ARTIFACT        results/r394_source_hash_key.json with the source hash.

IMPOSSIBLE HERE
  proof of determinism   -- two draws cannot establish it. Only "not caught" is available, and that
                            is what will be written.
  the censored rounds    -- they exceed the budget that made this affordable, and they are where the
                            answer would matter most. The gap is named, not papered over.
  artifact-only variation -- a round whose file changes while its stdout does not is invisible here.
  a second release       -- one release.

EXIT
    0  controls hold and the subjects are classified
    1  a control misbehaved -- UNVERIFIED
    2  the population or worktree is unusable -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
PY = ROOT / ".venv" / "bin" / "python"
WT = pathlib.Path("/tmp/claude-1000/-home-ivan/7d277876-c2fd-4a27-9b05-652b391121ff/scratchpad/r390_wt")
R393 = HERE.parent / "R393_what_the_gate_will_cost" / "results" / "r393_gate_cost.json"
TIMEOUT = 300
sys.path.insert(0, str(ROOT / "covalx"))
sys.path.insert(0, str(ROOT / "assurance"))
try:
    from stamp import stamp
except Exception:
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}


def main() -> int:
    # ---- the extractor comes from the GATE, never from here ------------------------------------
    try:
        from backfilled_findings_are_rederivable import NUM
    except Exception as e:
        print(f"  UNRUNNABLE: cannot import the gate's own extractor ({e}). Exit 2 rather than")
        print(f"  re-implement it — a control that re-implements the classifier tests the copy.")
        return 2
    if not R393.exists():
        print("  UNRUNNABLE: R393's artifact absent. Exit 2, never 0."); return 2
    if not WT.exists():
        print(f"  UNRUNNABLE: worktree {WT} absent. Exit 2, never 0."); return 2
    d = json.loads(R393.read_text())
    subjects = sorted(k for k, v in d["rows"].items() if v["status"] == "COMPLETE")
    if len(subjects) < 5:
        print(f"  UNRUNNABLE: only {len(subjects)} subjects. Exit 2, never 0."); return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R394 · is the source hash a valid cache key?   HEAD {head}\n")
    print(f"  ⛔ THE PREMISE R393's NEXT DID NOT EXAMINE. A source hash keys a cache only if the")
    print(f"     numbers are a FUNCTION of the source. And this is not hypothetical: R388's gate")
    print(f"     ALREADY re-runs each cited round, so a round that moves at fixed source makes that")
    print(f"     gate convict an honest row. The bug would be live, not future.\n")

    def run_twice(path: pathlib.Path, cwd: pathlib.Path):
        outs = []
        for _ in range(2):
            try:
                p = subprocess.run([str(PY), str(path)], cwd=str(cwd), capture_output=True,
                                   text=True, timeout=TIMEOUT)
                outs.append(sorted(NUM.findall(p.stdout + p.stderr)))
            except subprocess.TimeoutExpired:
                return None, None
        return outs[0], outs[1]

    # ---- CONTROLS, both directions --------------------------------------------------------------
    print(f"  CONTROLS on the stability detector — both directions, because a detector that calls")
    print(f"  everything stable passes no test and a detector that calls everything unstable fails")
    print(f"  no round.")
    plants = HERE / "results" / "_plants"
    plants.mkdir(parents=True, exist_ok=True)
    (plants / "rng.py").write_text(
        "import random\nprint('value', random.random())\nprint('value', random.random())\n")
    (plants / "const.py").write_text("print('value 0.5000 and 12345')\n")
    a, b = run_twice(plants / "rng.py", plants)
    rng_caught = (a is not None) and (a != b)
    c, e = run_twice(plants / "const.py", plants)
    const_stable = (c is not None) and (c == e)
    print(f"    PLANT (+)  an UNSEEDED rng draw is classified unstable: {rng_caught}   "
          f"{'PASS' if rng_caught else 'FAIL — every STABLE below would be silence'}")
    print(f"    PLANT (-)  a constant is classified stable:             {const_stable}   "
          f"{'PASS' if const_stable else 'FAIL — the detector cannot return stable at all'}")
    if not (rng_caught and const_stable):
        print("\n  UNVERIFIED — the detector is blind in one direction. Exit 1."); return 1

    # ---- the subjects ---------------------------------------------------------------------------
    print(f"\n  {len(subjects)} SUBJECTS — R393's COMPLETE set, each run TWICE at an unchanged source")
    rows, unstable, undecided = {}, [], []
    for name in subjects:
        d2 = next((q for q in WT.glob(f"E0*/A*/{name}") if q.is_dir()), None)
        if d2 is None or not (d2 / "run.py").exists():
            rows[name] = dict(status="ABSENT"); undecided.append(name)
            print(f"    {name:<44} ABSENT in the worktree"); continue
        src = hashlib.sha256((d2 / "run.py").read_bytes()).hexdigest()[:12]
        n1, n2 = run_twice(d2 / "run.py", d2)
        if n1 is None:
            rows[name] = dict(status="TIMEOUT", src=src); undecided.append(name)
            print(f"    {name:<44} TIMEOUT — its own class, never folded into either verdict")
            continue
        same = (n1 == n2)
        diff = sorted(set(n1) ^ set(n2))[:6]
        rows[name] = dict(status="STABLE" if same else "UNSTABLE", src=src,
                          n_numbers=len(n1), differing=diff)
        if not same:
            unstable.append(name)
        print(f"    {name:<44} {'STABLE  ' if same else 'UNSTABLE'} "
              f"{len(n1):>4} numbers   src {src}"
              + (f"   differs on {diff}" if not same else ""))

    decided = [k for k, v in rows.items() if v["status"] in ("STABLE", "UNSTABLE")]
    print(f"\n    decided {len(decided)} · unstable {len(unstable)} · "
          f"undecided {len(undecided)} (ABSENT or TIMEOUT — their own class, never a pass)")

    # ---- VERDICT --------------------------------------------------------------------------------
    print()
    if not decided:
        print("  UNVERIFIED — nothing was decided. Exit 1."); return 1
    if not unstable:
        v = "W_KEY_VALID"
        print(f"  W-KEY-VALID — {len(decided)} of {len(decided)} reproduce their numbers exactly at an")
        print(f"  unchanged source hash. The key is sound for this population, and R388's gate is not")
        print(f"  convicting honest rows on this evidence — which was the live risk, not the future one.")
    else:
        v = "W_KEY_UNSOUND"
        print(f"  W-KEY-UNSOUND — {len(unstable)} of {len(decided)} move at fixed source: {unstable}.")
        print(f"  The cache as specified would certify without checking, AND R388's gate already has a")
        print(f"  false-conviction mode. The named rounds are the finding; a rate would say less.")

    print(f"\n  ⚠ STABLE MEANS `NOT CAUGHT IN TWO DRAWS`, never `deterministic`. Two runs bound the")
    print(f"    detection probability from below only. A round that varies once in fifty is called")
    print(f"    stable here and would still break a cache.")
    print(f"  ⚠ AND THE POPULATION IS SELECTED TOWARD THIS ANSWER. These are the rounds that finished")
    print(f"    inside 90s — the ones loading no model and drawing no samples, i.e. the ones most")
    print(f"    likely to be deterministic. R393's two CENSORED rounds carry 80% of the gate's cost")
    print(f"    and are exactly the rounds this design cannot speak for. The result is scoped to FAST")
    print(f"    rounds and does not transport to the expensive tail a cache would mostly serve.")

    art = dict(stamp(str(SELF)), head=head, n_subjects=len(subjects), rows=rows,
               n_decided=len(decided), n_unstable=len(unstable), undecided=undecided,
               controls=dict(rng_plant_caught=rng_caught, constant_plant_stable=const_stable),
               verdict=v)
    outp = HERE / "results" / "r394_source_hash_key.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
