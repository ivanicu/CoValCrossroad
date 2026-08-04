"""Ten rounds regenerate a different value. Which of the three reasons, per round?

R344 measured that 41 of 45 sampled rounds re-run inside 90s and that **10 of the 40 with an
artifact to compare come back DIFFERENT** -- with `byte-identical` equal to `json-equal` at 30/40,
so not one of the ten differs merely in float formatting. Every difference is a value.

⛔ AND `25% DO NOT REPRODUCE` MEANS NOTHING UNTIL THE TEN ARE SEPARATED, because the categories are
not equivalent and only one of them is a defect:

  NONDETERMINISTIC   an unseeded draw. Two fresh runs of the SAME code disagree with each other.
                     A design choice, not a defect -- but it means the committed number was never
                     reproducible and no gate built on re-running can ever certify it.
  CORPUS-DEPENDENT   the round READS the corpus, and the corpus grew. `R242_self_audit` audits
                     rounds: committed at 23 rounds, today 124. Regenerating a different number is
                     CORRECT BEHAVIOUR and the artifact is simply old.
  CODE DRIFT         deterministic, does not read the corpus, and still disagrees with what is
                     committed. The number on the page is one its own code no longer produces.
                     This is the defect the whole provenance line has been chasing.

ESTIMAND, named before the method
---------------------------------
For each of the ten: which of those three, decided mechanically rather than by reading intent.

    run1, run2   two fresh executions in the SAME isolated copy
    committed    the artifact as it stands in git

    run1 != run2                      -> NONDETERMINISTIC          (the source is not a function)
    run1 == run2 != committed, reads  -> CORPUS-DEPENDENT
    run1 == run2 != committed, blind  -> CODE DRIFT
    run1 == run2 == committed         -> R344 WAS UNSTABLE, and that is a finding about R344

IDENTIFICATION. The first split is identified by execution and nothing else -- determinism is not
visible in a source, and a seeded-looking round can still consume `set` iteration order or a dict
built from a glob. The second split is a property of the SOURCE (does it read other rounds?) and is
decided by an AST/glob scan, which is a search and therefore an instrument with its own controls.

SCOPE
  population  the ten rounds R344 found completing-but-differing -- a CENSUS of that set, n=10
  instrument  execution in a true copy, `CUDA_VISIBLE_DEVICES=""`, plus a source scan for corpus
              reads
  baseline    the committed artifact
  regime      this machine; the same conditions R344 measured under

WORLDS
  W1 MOSTLY BENIGN   most are nondeterministic or corpus-dependent. `25% do not reproduce` is a
                     statement about design choices, and the provenance defect is rare.
  W2 REAL DRIFT      several are deterministic, corpus-blind, and disagree. The committed corpus
                     contains numbers its own code no longer produces, and R343's hole has victims.

PREDICTION MATRIX
  W1 -> CODE DRIFT count ~0; the STALE-stamped pair land in CORPUS-DEPENDENT or NONDETERMINISTIC
  W2 -> CODE DRIFT count >= 1, and it should be enriched among the STALE-stamped rounds, because
        for those the source is KNOWN to have changed since the artifact was written
The second prediction is what makes this severe: R345 already labelled two of the ten STALE from a
completely different instrument (a recorded hash), so if CODE DRIFT lands anywhere it should land
there, and if it lands ONLY on unstamped rounds the two instruments disagree and that is the finding.

PRE-REGISTERED KILL
    if the determinism control and the corpus-read control both hold:
        CODE DRIFT >= 1  -> W2. Name them; each is a published number its code cannot reproduce.
        CODE DRIFT == 0  -> W1. `25% do not reproduce` is retired as a defect count and restated as
                            a composition.
    else: UNVERIFIED.

CONTROLS
  DETERMINISM, positive   a round R344 found REPRODUCING must give run1 == run2 == committed here.
                          Without it, `run1 == run2` is an instrument never shown able to return
                          equality, and every NONDETERMINISTIC verdict would be unfalsifiable.
  DETERMINISM, negative   a synthetic round that draws from an unseeded rng must come out
                          NONDETERMINISTIC. Both directions, or it is not a control.
  CORPUS-READ, positive   `R242_self_audit` MUST be detected as corpus-reading: it counts rounds,
                          and its committed artifact says 23 where today's corpus has 124.
  CORPUS-READ, negative   a round that touches no other round's directory must not be flagged.
  ISOLATION               per path, over paths present at the start -- the v3 instrument from R344,
                          which is the only version of it whose unit matched its claim.

EXIT
    0  controls hold and the ten are classified
    1  a control misbehaved -- the classification is silence
    2  the R344 artifact is missing or lists no differing round: an empty population, never a pass
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
SCRATCH = ROOT.parent / ".r350_scratch"
PY = str(ROOT / ".venv" / "bin" / "python")
TIMEOUT = 150
CENSUS = ROOT / ("E05_the_space_of_compilers/A22_does_this_epochs_own_method_hold_up/"
                 "R344_what_fraction_can_be_rerun/results/r344_rerun_cost_census.json")
# ⚠ CORPUS-DEPENDENCE IS MEASURED, NOT PATTERN-MATCHED. v1 asked a regex whether the source globs
# rounds, and its own control refuted it IN BOTH DIRECTIONS: `R242_self_audit` -- which globs
# `A*/R*/run.py` through a variable prefix -- came out BLIND, and `R347`, which reads ONE named
# census file via `results/*.json`, came out READS. So R242 was filed as CODE DRIFT when direct
# measurement already showed it is corpus-dependent (committed at 23 rounds, today 124), and the
# defect count was inflated. A tighter regex fixes both cases -- but a regex `blind` is a NEGATIVE
# FROM A SEARCH, and §4 is explicit that a miss is not an acquittal: any of the other nine could
# read the corpus through a helper no pattern of mine can see.
#
# So the property is tested behaviourally instead: PLANT N SYNTHETIC ROUNDS and re-run. A round
# whose output depends on HOW MANY ROUNDS EXIST moves; a round that reads one named artifact does
# not. That is exactly the distinction the classification needs, and it is decided by the round's
# own behaviour rather than by my reading of its source.
N_PLANT = 24


def tree_snapshot() -> dict:
    out = {}
    for f in sorted(ROOT.glob("E*/A*/R*/results/*")):
        if f.is_file() and "R350_why_the_ten" not in str(f):
            out[f.relative_to(ROOT).as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def make_copy(dest: pathlib.Path) -> bool:
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["cp", "-a", "--reflink=auto", str(ROOT), str(dest)], capture_output=True)
    if r.returncode != 0:
        return False
    want, got = len(list(ROOT.glob("E*/A*/R*/run.py"))), len(list(dest.glob("E*/A*/R*/run.py")))
    if want == 0 or got != want:
        print(f"    COPY SHAPE WRONG: {got} vs {want}")
        return False
    return True


def artifacts(rd: pathlib.Path) -> dict:
    out = {}
    res = rd / "results"
    if res.is_dir():
        for f in sorted(res.glob("*.json")):
            if "_smoke" not in f.name:
                out[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def execute(copy_root: pathlib.Path, rd: pathlib.Path) -> bool:
    env = dict(os.environ, CUDA_VISIBLE_DEVICES="", MPLBACKEND="Agg", PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.Popen([PY, str(rd / "run.py")], cwd=str(copy_root), env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        p.communicate(timeout=TIMEOUT)
        return p.returncode in (0, 1, 2)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), 9)
        except Exception:
            p.kill()
        p.communicate()
        return False


def plant_rounds(copy_root: pathlib.Path, n: int = N_PLANT) -> pathlib.Path:
    """N synthetic rounds, shaped like real ones, so a corpus-counting round sees a bigger corpus."""
    # ⚠ PLANTED INSIDE E05, NOT E99. The first version planted into `E99_fixtures` and the control
    # failed: `R242_self_audit` globs `E05.glob("A*/R*/run.py")` -- it counts E05 rounds ONLY -- so
    # a probe in another epoch is invisible to it and R242 came out corpus-BLIND. The plant has to
    # land where the round under test is actually looking, which is the same unit-equality rule
    # this session keeps re-learning: the instrument's population and the claim's population must
    # be the same set before the control is designed.
    base = copy_root / "E05_the_space_of_compilers" / "A98_corpus_probe"
    for i in range(n):
        rd = base / f"R9{i:03d}_probe"
        (rd / "results").mkdir(parents=True, exist_ok=True)
        (rd / "run.py").write_text("# synthetic corpus probe (R350)\n")
        (rd / "results" / "r.json").write_text(json.dumps({"probe": i}))
        (rd / "README.md").write_text(f"# R9{i:03d} probe\n")
    return base


def reads_corpus(copy_root: pathlib.Path, rd: pathlib.Path, baseline: dict) -> bool:
    """MEASURED: does the output move when the corpus grows by N_PLANT rounds?"""
    base = plant_rounds(copy_root)
    try:
        if not execute(copy_root, rd):
            return False
        grown = artifacts(rd)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    return grown != baseline


def classify(copy_root: pathlib.Path, name: str):
    hits = list(copy_root.glob(f"E*/A*/{name}"))
    if not hits:
        return "NO ROUND", {}
    rd = hits[0]
    committed = artifacts(rd)
    if not execute(copy_root, rd):
        return "DID NOT COMPLETE", {}
    r1 = artifacts(rd)
    if not execute(copy_root, rd):
        return "DID NOT COMPLETE", {}
    r2 = artifacts(rd)
    det = (r1 == r2)
    cur = (r2 == committed)
    if not det:
        return "NONDETERMINISTIC", {"deterministic": False, "matches_committed": cur,
                                    "reads_corpus": None}
    if cur:
        return "REPRODUCES (R344 unstable)", {"deterministic": True, "matches_committed": True,
                                              "reads_corpus": None}
    rc = reads_corpus(copy_root, rd, r2)
    return ("CORPUS-DEPENDENT" if rc else "CODE DRIFT"), {"deterministic": True,
                                                          "matches_committed": False,
                                                          "reads_corpus": rc}


def corpus_read_controls(copy_root: pathlib.Path):
    """Both directions, on REAL rounds whose answer is known from outside this instrument.
    R242 counts rounds (committed at 23, today 124). R347 reads ONE named census file."""
    out = {}
    for nm, want in (("R242_self_audit", True), ("R347_does_clause_one_ever_bind", False)):
        h = list(copy_root.glob(f"E*/A*/{nm}"))
        if not h or not execute(copy_root, h[0]):
            out[nm] = None
            continue
        out[nm] = reads_corpus(copy_root, h[0], artifacts(h[0]))
    ok = (out.get("R242_self_audit") is True) and (out.get("R347_does_clause_one_ever_bind") is False)
    return ok, (f"R242 (counts rounds) -> {out.get('R242_self_audit')} (want True); "
                f"R347 (reads one named census) -> {out.get('R347_does_clause_one_ever_bind')} "
                f"(want False)")


def determinism_negative(copy_root: pathlib.Path):
    """A synthetic round with an UNSEEDED draw must come out NONDETERMINISTIC."""
    rd = copy_root / "E05_the_space_of_compilers" / "A99_ctl" / "R999_unseeded"
    (rd / "results").mkdir(parents=True, exist_ok=True)
    (rd / "run.py").write_text(
        "import json, pathlib, random\n"
        "p = pathlib.Path(__file__).parent / 'results' / 'r.json'\n"
        "p.write_text(json.dumps({'x': random.random()}))\n")
    (rd / "results" / "r.json").write_text(json.dumps({"x": 0.0}))
    lab, _d = classify(copy_root, "R999_unseeded")
    shutil.rmtree(rd, ignore_errors=True)
    return lab == "NONDETERMINISTIC", f"planted unseeded round -> {lab} (want NONDETERMINISTIC)"


def main() -> int:
    if not CENSUS.exists():
        print("  UNRUNNABLE: R344's census is missing. Exit 2, never 0.")
        return 2
    cen = json.loads(CENSUS.read_text(encoding="utf-8"))
    ten = sorted(r["round"] for r in cen["sample"]
                 if r["status"] == "COMPLETED" and r["repro_json"] is False)
    reproducers = [r["round"] for r in cen["sample"]
                   if r["status"] == "COMPLETED" and r["repro_json"] is True]
    if not ten:
        print("  UNRUNNABLE: the census lists no completing-but-differing round. Exit 2, never 0.")
        return 2
    print(f"R350 · why do the ten differ?   population = {len(ten)} rounds from R344\n")

    before = tree_snapshot()
    d = SCRATCH / "work"
    if not make_copy(d):
        print("  UNRUNNABLE: could not copy the repository. Exit 2, never 0.")
        return 2

    cr_ok, cr_detail = corpus_read_controls(d)
    print(f"  CORPUS-READ control: {cr_detail}  {'PASS' if cr_ok else 'FAIL'}")
    dn_ok, dn_detail = determinism_negative(d)
    print(f"  DETERMINISM negative: {dn_detail}  {'PASS' if dn_ok else 'FAIL'}")

    pos_name = reproducers[0] if reproducers else None
    dp_lab, _ = classify(d, pos_name) if pos_name else ("NONE", {})
    dp_ok = dp_lab.startswith("REPRODUCES")
    print(f"  DETERMINISM positive: {pos_name} — a round R344 found reproducing -> {dp_lab} "
          f"(want REPRODUCES)  {'PASS' if dp_ok else 'FAIL'}")

    print(f"\n  {'round':<46}{'verdict':<28}det  cur  reads")
    rows, counts = [], {}
    for name in ten:
        lab, det = classify(d, name)
        counts[lab] = counts.get(lab, 0) + 1
        rows.append({"round": name, "verdict": lab, **det})
        print(f"  {name:<46}{lab:<28}"
              f"{str(det.get('deterministic','-')):<5}{str(det.get('matches_committed','-')):<5}"
              f"{str(det.get('reads_corpus','-'))}")

    after = tree_snapshot()
    changed = [k for k in before if k in after and after[k] != before[k]]
    vanished = [k for k in before if k not in after]
    iso_ok = not changed and not vanished
    print(f"\n  ISOLATION: of {len(before)} artifacts present at the start, {len(changed)} changed "
          f"and {len(vanished)} vanished  {'PASS' if iso_ok else 'FAIL'}")

    print(f"\n  composition of the ten:")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"      {k:<30}{v:>3}")

    drift = [r["round"] for r in rows if r["verdict"] == "CODE DRIFT"]
    controls_ok = cr_ok and dn_ok and dp_ok and iso_ok
    print()
    if not controls_ok:
        print("  UNVERIFIED: a control misbehaved, so the classification above is silence.")
        verdict = "UNVERIFIED"
    elif drift:
        print(f"  W2 — REAL DRIFT. {len(drift)} of {len(ten)} are deterministic, corpus-blind, and")
        print(f"  still disagree with what is committed: {', '.join(drift)}")
        print("  Each is a published number its own code no longer produces.")
        verdict = "W2_REAL_DRIFT"
    else:
        print(f"  W1 — MOSTLY BENIGN. Zero of {len(ten)} are deterministic-and-corpus-blind.")
        print("  `25% do not reproduce` is retired as a defect count and restated as a composition:")
        print("  unseeded draws and rounds that read a corpus which has since grown.")
        verdict = "W1_MOSTLY_BENIGN"

    art = {"population": ten, "rows": rows, "counts": counts, "verdict": verdict,
           "controls": {"corpus_read": cr_ok, "determinism_negative": dn_ok,
                        "determinism_positive": dp_ok, "isolation": iso_ok},
           "census_source": CENSUS.relative_to(ROOT).as_posix()}
    outp = HERE / "results" / "r350_why_the_ten_differ.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")

    print("\n  ⚠ SCOPE. `NONDETERMINISTIC` here means two runs in the same copy disagreed — it does")
    print("    NOT say the round is wrong, only that its committed number was never reproducible")
    print("    and no re-running gate can certify it. `CORPUS-DEPENDENT` is MEASURED, not")
    print(f"    pattern-matched: {N_PLANT} synthetic rounds are planted in E05 and the round re-run, so a")
    print("    corpus reader that goes through any helper is caught. What it still cannot see is a")
    print("    round that depends on the corpus in a way N_PLANT rounds do not perturb -- a round")
    print("    keyed to a specific arc, say -- and that direction MISFILES AS CODE DRIFT, which")
    print("    over-counts the defect rather than hiding it.")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    return 0 if controls_ok else 1


if __name__ == "__main__":
    sys.exit(main())
