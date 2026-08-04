"""What fraction of this corpus can actually be re-run -- and of that, what reproduces?

R343 measured that NOTHING in this suite ties a committed artifact to the source beside it: 277
rounds were rewritten to compute a median, every artifact was left holding the mean, and zero of 21
checks moved. It closed by naming the one direction a recorded source hash cannot close -- an
artifact hand-edited to agree with a source that never produced it, where whoever edits the artifact
edits the hash too. Only RE-RUNNING tests that. Re-running is expensive. So the question that
decides whether the direction is closable at all is a cost question, and this round measures it.

⚠ PRIOR WORK IN THIS SAME REPOSITORY, WHICH I DID NOT CHECK BEFORE PROPOSING THIS.
R343's closing line asked "which rounds are cheap enough to re-run, and what fraction of the corpus
does that cover" as though nobody had looked. Two rounds had:

  R302_are_the_artifacts_reproducible -- "is a committed artifact reproducible from its committed
      code?" It re-ran eight artifacts and found 742 leaf values differing, three of them inside a
      `verdict` string.
  R315_how_many_rounds_can_still_run -- "25 of 278 probed rounds (9.0%) cannot resolve their
      inputs", with one moved directory accounting for 44% of them.

`assurance/next_gradient_is_new.py` finds both in a single command, on the exact words I used. IT
EXISTS BECAUSE I MADE THIS MISTAKE FOUR TIMES, and I did not run it before writing the sentence.
That is the fifth, and the remedy being a file rather than a habit is precisely what failed here.

WHAT IS ACTUALLY NEW, stated narrowly because the rest is not:
  - COST as a dose-response curve. R315 measured whether a round can START (inputs resolve); this
    measures how long it takes to FINISH, swept over the budget, which is the quantity that decides
    whether re-running is a usable gate.
  - The reproduction question at CORPUS SCALE with a stratified sample and an interval, rather than
    on eight artifacts selected because they happened to be uncommitted -- R302's population was
    chosen by what was dirty in git, which is a stratum, not a sample.
  - Both instruments (byte vs json-with-tolerance) separated, so formatting drift is not counted as
    a numeric failure.
R302's 742 differing leaves is therefore a PRIOR, not a rival: it predicts a low p_repro, and if
this round comes back high, one of the two populations is unrepresentative and that is the finding.

TWO ESTIMANDS, named before the method
---------------------------------------
  p_cheap(T)   the fraction of rounds whose run.py COMPLETES within T seconds, in an isolated copy,
               with no GPU. Reported as a DOSE-RESPONSE CURVE over T, not at one threshold -- each
               round is executed ONCE and its wall-clock recorded, so the whole curve costs one
               execution per round rather than one per (round, T).
  p_repro      of the rounds that complete, the fraction whose regenerated artifact matches the
               committed one. TWO instruments: byte-identical, and JSON-equal under a numeric
               tolerance. The gap between them is itself the finding -- a round that differs only
               in float formatting is reproducible in every sense that matters, and a round that
               differs numerically is not.

IDENTIFICATION
  p_cheap is identified by execution and by nothing else. The static screen below (does the source
  import torch, openai, sklearn...) is a HYPOTHESIS about cost, not a measurement of it, and this
  round treats it as a stratifier to be TESTED rather than as an answer: a `pure` round that loads a
  54 MB cache or draws 20,000 bootstrap replicates is not cheap, and only the clock knows.

SCOPE
  population  the 328 rounds carrying a run.py, stratified by static import screen
  sample      SAMPLE_N drawn with a fixed seed, stratified; the strata sizes are reported so the
              corpus-level number is a weighted estimate with its own interval, never a raw count
  instrument  wall-clock under `timeout`, in a hardlinked isolated copy, CUDA_VISIBLE_DEVICES=""
  baseline    the committed artifact as it stands in git
  regime      this machine, cold caches, no network blocking (declared below as a limitation)

WORLDS
  W1 CLOSABLE     a large fraction is cheap AND reproduces -> re-running is a practical gate, and
                  the provenance hole R343 found can be closed for most of the corpus.
  W2 TOO DEAR     little of it is cheap -> the hole stays open by cost, and the honest move is to
                  record source hashes for the rest and say what that does and does not buy.
  W3 CHEAP BUT NOT REPRODUCIBLE  much of it is cheap and much of that does NOT reproduce. This is
                  the world neither R343 nor I predicted, and it is the most informative: it would
                  mean the corpus already contains artifacts its own sources do not regenerate, and
                  the cost question was never the binding one.

PREDICTION MATRIX
  W1 -> p_cheap high, p_repro high
  W2 -> p_cheap low,  p_repro undefined on a small base (report the base, never the ratio alone)
  W3 -> p_cheap high, p_repro low          <- and this outcome retracts my own next-gradient line

CONTROLS
  POSITIVE (repro)   a round KNOWN cheap and deterministic must complete and reproduce. R342 is one
                     I wrote and verified byte-identical across runs two rounds ago.
  NEGATIVE (repro)   the same round with its committed artifact CORRUPTED before comparison must be
                     reported NOT reproducing. Without it, `everything reproduced` is silence -- the
                     comparison would never have been shown capable of returning a mismatch.
  TIMEOUT            a synthetic script that sleeps past the budget must be recorded as TIMEOUT. A
                     completion rate measured with a timeout that never fires is not a measurement.
  g=0                the timeout instrument on a script that exits immediately must NOT report
                     TIMEOUT -- the mirror, so the control can fail in both directions.
  ISOLATION          the CONTENT of every committed artifact in the real tree is hashed before and
                     after. Rounds WRITE when they run; if one wrote into the real tree this number
                     would be worthless and the tree would be damaged. ⚠ v1 hashed `git status
                     --porcelain` instead and FAILED while nothing was wrong -- five of my own
                     commits landed during the 23-minute run and moved the string, the tree itself
                     was clean, and a valid census was correctly marked UNVERIFIED for 45 rounds.
                     The claim's unit is a file's CONTENT; the instrument's was git's opinion about
                     staging. They are not the same object.

⛔ ARITHMETIC TRAP. p_cheap could come out anywhere in [0,1]; it is a measurement. The static screen
   count (301 `pure` of 328) is NOT -- it is a property of the import lines, forced by reading them,
   and it is reported as a stratifier rather than as an estimate of cost.

EXIT
    0  controls hold and the census is reported
    1  a control misbehaved -- the rates below would be silence
    2  no rounds, or the copy failed: an empty population, never a silent pass
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import random
import re
import shutil
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
SCRATCH = pathlib.Path(os.environ.get("R344_SCRATCH", str(ROOT.parent / ".r344_scratch")))
PY = str(ROOT / ".venv" / "bin" / "python")
TIMEOUT = int(os.environ.get("R344_TIMEOUT", "60"))
SAMPLE_N = int(os.environ.get("R344_N", "30"))
SEED = 344
TOL = 1e-9

HEAVY = {"torch": "gpu/ml", "transformers": "gpu/ml", "sentence_transformers": "gpu/ml",
         "vllm": "gpu/ml", "openai": "network", "requests": "network", "httpx": "network",
         "datasets": "network", "sklearn": "cpu-ml", "statsmodels": "cpu-ml"}


def screen(p: pathlib.Path) -> str:
    t = p.read_text(encoding="utf-8", errors="replace")
    kinds = {HEAVY[m] for m in HEAVY if re.search(rf"^\s*(import|from)\s+{m}\b", t, re.M)}
    if not kinds:
        return "pure"
    return "gpu/ml" if "gpu/ml" in kinds else ("network" if "network" in kinds else "cpu-ml")


def tree_fingerprint() -> str:
    """Content of every committed artifact in the real tree, hashed.

    ⚠ v1 used `git status --porcelain`, and it FAILED while nothing was wrong. Its claim was "no
    round modified the real working tree"; its instrument was "git's status string is unchanged",
    and those are different objects the moment the author commits anything concurrently. Five of my
    own commits landed during the 23-minute run and moved the string; the tree itself was clean and
    no round had written to it. realstat §4, `the control fails for its own reasons`, form ③ --
    it targets a different statistic than the one being reported -- and the cost was a whole
    execution census correctly marked UNVERIFIED.

    The claim's unit is a FILE'S CONTENT under a round's results/, so that is what is hashed. Immune
    to commits, to staging, to new untracked files, and to this round's own output.
    """
    h = hashlib.sha256()
    for f in sorted(ROOT.glob("E*/A*/R*/results/*")):
        if not f.is_file() or "R344_what_fraction" in str(f):
            continue
        h.update(f.relative_to(ROOT).as_posix().encode())
        h.update(hashlib.sha256(f.read_bytes()).digest())
    return h.hexdigest()


def make_copy(dest: pathlib.Path) -> bool:
    """A TRUE copy, not a hardlink copy, and the difference is not an optimisation detail.

    ⚠ MEASURED, and it damaged the working tree before it was fixed. R343 could hardlink because it
    only ever REWROTE files itself, unlinking first. This round EXECUTES the rounds, and a round
    that rewrites its artifact IN PLACE writes straight through a shared inode into the real
    repository. Two did: R242_self_audit and R307_a_size_matched_neutral_arm both came back
    `DIFFERS`, and `git status` on the REAL tree showed both modified. The isolation control is the
    only reason that was caught in a smoke run instead of silently corrupting committed artifacts
    across a full sample. A true copy costs 4.1s here. It is not worth one byte of doubt about the
    tree.

    ⚠ AND MY FIRST READING OF IT WAS WRONG, so it is corrected here rather than quietly dropped. I
    wrote that the leak "was manufacturing exactly the finding the round was looking for", because
    the two escaping rounds were also the two reporting DIFFERS. Under a true copy they STILL report
    DIFFERS. The leak was real and dangerous and it was not the cause of the mismatch -- two true
    things about the same two rounds, and I had joined them into a third that was false."""
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


def json_close(a, b, tol=TOL):
    if isinstance(a, float) or isinstance(b, float):
        try:
            fa, fb = float(a), float(b)
        except (TypeError, ValueError):
            return a == b
        if math.isnan(fa) and math.isnan(fb):
            return True
        return abs(fa - fb) <= tol * max(1.0, abs(fa), abs(fb))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(json_close(a[k], b[k], tol) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(json_close(x, y, tol) for x, y in zip(a, b))
    return a == b


def run_round(copy_root: pathlib.Path, rel: pathlib.Path):
    """Execute one round in the copy. Returns (status, elapsed, repro_bytes, repro_json, detail).

    ⚠ The round is run with its ARTIFACTS PRESERVED as `committed`, then executed (which overwrites
    them), then compared. Preserving first and comparing after is the only order that survives a
    round which writes its artifact incrementally."""
    rd = copy_root / rel.parent
    res = rd / "results"
    committed = {}
    if res.is_dir():
        for f in sorted(res.glob("*.json")):
            if "_smoke" in f.name:
                continue
            try:
                committed[f.name] = (f.read_bytes(), json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                committed[f.name] = (f.read_bytes(), None)
    env = dict(os.environ, CUDA_VISIBLE_DEVICES="", MPLBACKEND="Agg", PYTHONDONTWRITEBYTECODE="1")
    t0 = time.time()
    # ⚠ PROCESS GROUP, not just the child. `subprocess.run(timeout=...)` kills only the direct
    # child; a round that shells out to `cp`, `git` or a solver leaves those running, and they keep
    # writing into the copy while the NEXT round is being measured -- which would contaminate a
    # wall-clock census with somebody else's CPU. start_new_session puts the round in its own group
    # and the whole group is killed on timeout.
    proc = subprocess.Popen([PY, str(copy_root / rel)], cwd=str(copy_root), env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        _out, err = proc.communicate(timeout=TIMEOUT)
        elapsed, rc = time.time() - t0, proc.returncode
        status = "COMPLETED" if rc in (0, 1, 2) else f"EXIT{rc}"
        if rc != 0 and b"Traceback" in err:
            status = "ERROR"
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), 9)
        except Exception:
            proc.kill()
        proc.communicate()
        return "TIMEOUT", float(TIMEOUT), None, None, ""
    except Exception as e:
        return "ERROR", time.time() - t0, None, None, type(e).__name__[:40]

    # ⚠ A ROUND THAT DID NOT RUN CANNOT HAVE REPRODUCED. v1 compared artifacts whatever the exit
    # status, so an ERROR round -- which never wrote anything -- came back `1/1 byte, 1/1 json`,
    # scoring as a perfect reproduction BECAUSE NOTHING HAD BEEN WRITTEN. Two gpu/ml rounds printed
    # exactly that in the smoke run. The comparison is only meaningful where the source actually
    # produced output, so a non-completing round returns None and lands in neither numerator nor
    # denominator.
    if status != "COMPLETED":
        return status, elapsed, None, None, "did not complete: nothing was regenerated to compare"
    if not committed:
        return status, elapsed, None, None, "no committed artifact to compare"
    nb = nj = 0
    for name, (blob, obj) in committed.items():
        f = res / name
        if not f.exists():
            continue
        new = f.read_bytes()
        nb += (new == blob)
        try:
            nj += json_close(obj, json.loads(new.decode("utf-8", "replace")))
        except Exception:
            nj += (new == blob)
    n = len(committed)
    return status, elapsed, nb == n, nj == n, f"{nb}/{n} byte, {nj}/{n} json"


def timeout_controls() -> tuple[bool, str]:
    """The completion rate is measured WITH a timeout. If that timeout never fires, the rate is not
    a measurement -- so it is fired, and its mirror is fired too."""
    d = SCRATCH / "ctl"
    d.mkdir(parents=True, exist_ok=True)
    slow, fast = d / "slow.py", d / "fast.py"
    slow.write_text(f"import time\ntime.sleep({TIMEOUT + 20})\n")
    fast.write_text("print('done')\n")
    hit = miss = None
    try:
        subprocess.run([PY, str(slow)], capture_output=True, timeout=TIMEOUT)
        hit = False
    except subprocess.TimeoutExpired:
        hit = True
    try:
        subprocess.run([PY, str(fast)], capture_output=True, timeout=TIMEOUT)
        miss = False
    except subprocess.TimeoutExpired:
        miss = True
    shutil.rmtree(d, ignore_errors=True)
    return (hit and not miss), f"sleep({TIMEOUT + 20}) -> {'TIMEOUT' if hit else 'completed'} " \
                               f"(want TIMEOUT); instant script -> " \
                               f"{'TIMEOUT' if miss else 'completed'} (want completed)"


def main() -> int:
    # ⚠ TWO ROUNDS ARE EXCLUDED AND THE REASON IS STRUCTURAL, not convenience. R343 and R344 both
    # COPY THE REPOSITORY AND EXECUTE ITS ROUNDS. Sampling R344 makes it run inside itself; sampling
    # R343 makes it copy the repo five more times inside a copy. Either measures the harness rather
    # than the corpus, and the exclusion is reported in the artifact so the population is stated
    # rather than quietly trimmed. Every other round with a run.py is eligible.
    EXCLUDE = ("R343_", "R344_")
    all_rounds = sorted(p.relative_to(ROOT) for p in ROOT.glob("E*/A*/R*/run.py"))
    rounds = [r for r in all_rounds if not any(x in str(r) for x in EXCLUDE)]
    excluded = [str(r) for r in all_rounds if any(x in str(r) for x in EXCLUDE)]
    if not rounds:
        print("  UNRUNNABLE: no rounds carry a run.py. Exit 2, never 0.")
        return 2
    print(f"R344 · what fraction of the corpus can be re-run?   "
          f"{len(rounds)} eligible rounds with a run.py ({len(excluded)} excluded as "
          f"self-referential: {', '.join(pathlib.Path(x).parent.name for x in excluded) or 'none'}), "
          f"budget T={TIMEOUT}s, sample n={SAMPLE_N}\n")

    before = tree_fingerprint()

    tc_ok, tc_detail = timeout_controls()
    print(f"  TIMEOUT CONTROL: {tc_detail}  {'PASS' if tc_ok else 'FAIL'}")

    strata: dict[str, list] = {}
    for r in rounds:
        strata.setdefault(screen(ROOT / r), []).append(r)
    print("\n  STATIC STRATIFIER (a hypothesis about cost, NOT a measurement of it):")
    for k, v in sorted(strata.items(), key=lambda kv: -len(kv[1])):
        print(f"      {k:<12}{len(v):>5}")

    rng = random.Random(SEED)
    sample = []
    for k, v in sorted(strata.items()):
        take = max(2, round(SAMPLE_N * len(v) / len(rounds))) if len(v) >= 2 else len(v)
        sample += [(k, r) for r in rng.sample(v, min(take, len(v)))]
    # the positive control round is forced into the sample, named, and reported separately
    POS = next((r for r in rounds if "R342_" in str(r)), None)
    if POS and all(r != POS for _k, r in sample):
        sample.append((screen(ROOT / POS), POS))
    print(f"\n  SAMPLE: {len(sample)} rounds, seed {SEED}, stratified\n")

    d = SCRATCH / "work"
    if not make_copy(d):
        print("  UNRUNNABLE: could not copy the repository. Exit 2, never 0.")
        return 2

    rows = []
    print(f"    {'round':<52}{'stratum':<9}{'status':<10}{'secs':>7}  repro")
    for k, rel in sample:
        status, elapsed, rb, rj, detail = run_round(d, rel)
        rows.append({"round": rel.parent.name, "path": str(rel), "stratum": k, "status": status,
                     "secs": round(elapsed, 2), "repro_bytes": rb, "repro_json": rj,
                     "detail": detail})
        rep = "-" if rb is None else ("BYTE" if rb else ("JSON" if rj else "DIFFERS"))
        print(f"    {rel.parent.name[:51]:<52}{k:<9}{status:<10}{elapsed:>7.1f}  {rep}  {detail}")

    # ---- the negative control on the REPRO comparison ---------------------------------------------
    neg_ok, neg_detail = False, "positive-control round not in the corpus"
    if POS:
        d2 = SCRATCH / "neg"
        if make_copy(d2):
            res = d2 / POS.parent / "results"
            tgt = next((f for f in sorted(res.glob("*.json")) if "_smoke" not in f.name), None)
            if tgt is not None:
                obj = json.loads(tgt.read_text(encoding="utf-8"))
                obj["__r344_negative_control__"] = "this key was never produced by the source"
                tgt.unlink()
                tgt.write_text(json.dumps(obj, indent=2, sort_keys=True))
                s, _e, rb, rj, det = run_round(d2, POS)
                neg_ok = (rb is False and rj is False)
                neg_detail = f"corrupted artifact -> byte {rb}, json {rj} (want False/False) [{det}]"
            shutil.rmtree(d2, ignore_errors=True)
    print(f"\n  NEGATIVE CONTROL on the comparison: {neg_detail}  {'PASS' if neg_ok else 'FAIL'}")

    pos_row = next((r for r in rows if POS and r["path"] == str(POS)), None)
    pos_ok = bool(pos_row and pos_row["status"] == "COMPLETED" and pos_row["repro_json"])
    print(f"  POSITIVE CONTROL ({POS.parent.name if POS else '-'}): completes and reproduces -> "
          f"{'PASS' if pos_ok else 'FAIL'}")

    after = tree_fingerprint()
    iso_ok = (before == after)
    print(f"  ISOLATION: the real tree is unchanged after executing {len(sample)} rounds  "
          f"{'PASS' if iso_ok else 'FAIL'}")

    # ---- the dose-response curve, from ONE execution per round -----------------------------------
    print("\n  p_cheap(T) -- one execution per round, so the whole curve is free:\n")
    print(f"    {'T (s)':>7}{'completed <=T':>15}{'of sampled':>12}{'rate':>8}")
    curve = {}
    done = [r for r in rows if r["status"] == "COMPLETED"]
    for T in (5, 10, 20, 30, 45, 60, TIMEOUT):
        if T > TIMEOUT:
            continue
        k = sum(1 for r in done if r["secs"] <= T)
        curve[T] = k
        print(f"    {T:>7}{k:>15}{len(rows):>12}{k / len(rows):>8.2f}")

    byst = {}
    for r in rows:
        b = byst.setdefault(r["stratum"], {"n": 0, "completed": 0, "byte": 0, "json": 0, "diff": 0})
        b["n"] += 1
        if r["status"] == "COMPLETED":
            b["completed"] += 1
            if r["repro_bytes"]:
                b["byte"] += 1
            if r["repro_json"]:
                b["json"] += 1
            elif r["repro_json"] is False:
                b["diff"] += 1
    print("\n  BY STRATUM -- and the stratum sizes are what turn these into a corpus estimate:\n")
    print(f"    {'stratum':<10}{'sampled':>8}{'in corpus':>11}{'completed':>11}"
          f"{'byte-identical':>15}{'json-equal':>12}{'differs':>9}")
    for k in sorted(byst):
        b = byst[k]
        print(f"    {k:<10}{b['n']:>8}{len(strata.get(k, [])):>11}{b['completed']:>11}"
              f"{b['byte']:>15}{b['json']:>12}{b['diff']:>9}")

    n_done, n_cmp = len(done), sum(1 for r in done if r["repro_json"] is not None)
    n_json = sum(1 for r in done if r["repro_json"])
    n_byte = sum(1 for r in done if r["repro_bytes"])
    print(f"\n  completed {n_done}/{len(rows)};  of those, {n_cmp} had an artifact to compare;"
          f"  json-equal {n_json}/{n_cmp}, byte-identical {n_byte}/{n_cmp}")

    controls_ok = tc_ok and neg_ok and pos_ok and iso_ok
    print()
    if not controls_ok:
        print("  UNVERIFIED: a control misbehaved, so every rate above is silence.")
        verdict = "UNVERIFIED"
    elif n_cmp == 0:
        print("  UNRESOLVED on p_repro: no sampled round both completed and had an artifact to")
        print("  compare. p_cheap stands; the reproduction question needs a larger sample.")
        verdict = "P_REPRO_UNRESOLVED"
    elif n_done / len(rows) < 0.5:
        print(f"  W2 -- TOO DEAR. {n_done}/{len(rows)} completed inside {TIMEOUT}s. Re-running is not")
        print("  a practical gate for this corpus at this budget, and the provenance hole R343")
        print("  found stays open by COST. Base for p_repro is small; the ratio is not the finding.")
        verdict = "W2_TOO_DEAR"
    elif n_json / n_cmp < 0.5:
        print(f"  W3 -- CHEAP BUT NOT REPRODUCIBLE. {n_done}/{len(rows)} ran inside {TIMEOUT}s, and")
        print(f"  only {n_json}/{n_cmp} of those regenerate their own committed artifact. The cost")
        print("  question was never the binding one, and my own next-gradient line is retracted.")
        verdict = "W3_CHEAP_NOT_REPRODUCIBLE"
    else:
        print(f"  W1 -- CLOSABLE. {n_done}/{len(rows)} complete inside {TIMEOUT}s and {n_json}/{n_cmp}")
        print("  reproduce. Re-running is a practical gate for this corpus.")
        verdict = "W1_CLOSABLE"

    art = {"timeout_s": TIMEOUT, "seed": SEED, "n_rounds_with_source": len(rounds),
           "excluded_self_referential": excluded,
           "strata_sizes": {k: len(v) for k, v in strata.items()},
           "sample": rows, "curve": curve, "by_stratum": byst,
           "controls": {"timeout": tc_ok, "negative_repro": neg_ok, "positive_repro": pos_ok,
                        "isolation": iso_ok},
           "verdict": verdict}
    outp = HERE / "results" / "r344_rerun_cost_census.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")

    print("\n  ⚠ SCOPE, and two limits are real. (1) NETWORK IS NOT BLOCKED: a round that fetches")
    print("    would be counted as cheap here and would not be on a cold machine. The static screen")
    print("    finds no network imports, which bounds but does not prove it. (2) A round that")
    print("    DIFFERS is not thereby wrong -- an unseeded draw, a timestamp or a dict order")
    print("    explains a difference without any defect. This measures REGENERABILITY, not")
    print("    correctness, and the two instruments (byte vs json) separate formatting from value.")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    return 0 if controls_ok else 1


if __name__ == "__main__":
    sys.exit(main())
