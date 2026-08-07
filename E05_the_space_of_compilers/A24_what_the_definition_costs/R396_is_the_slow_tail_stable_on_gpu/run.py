"""R396 -- is the ONE round the gauge test points at stable, where the cache would do all its work?

R394 proved 13 fast rounds reproduce their numbers at unchanged source and named its blind spot: the
two rounds R393 censored carry 80% of the gate's cost and are the population it cannot speak for.
R395 then measured whether a source grep could stand in for the re-run -- 23% false positives against
R394's committed labels, quiet on 10 of 13 -- and narrowed the expensive step from two rounds to one:
R114_demographic_subject is quiet, R130_judge_gauge carries `gpu`.

⛔ THIS IS THE STEP WHOSE FAVOURABLE OUTCOME I WOULD FIND UNWELCOME, WHICH IS WHY IT IS NEXT. If R130
   is stable, the cache is sound across the whole cost distribution and there is nothing more to say.
   If it MOVES, the cache is unsound exactly where it would do all its work, AND R388's committed gate
   has a live false-conviction mode on the slow tail. I would rather learn the second, and the design
   must be able to deliver it.

⛔ AND GPU NON-DETERMINISM IS NOT A HYPOTHETICAL I INVENTED TO HAVE A WORLD. Reductions with atomics,
   autotuned matmul kernels and non-deterministic attention backends all vary run to run at fixed
   source and fixed seed. This is the documented behaviour of the platform, not a suspicion about this
   round -- which is exactly why `gpu` earned a pattern family in R395 rather than being waved at.

⛔ THE FAILURE THIS DESIGN MUST NOT COMMIT: A CRASH IS BYTE-IDENTICAL TWICE. If R130 cannot run here
   -- missing model, busy GPU, changed API -- it emits the same traceback both times, the number sets
   match, and the round would print STABLE. That is a check that cannot fail, and it would certify the
   slow tail on the strength of a round that never executed. So a non-zero return code on either run
   is its own class, UNRUNNABLE_HERE, and can never reach the STABLE branch.

ESTIMAND        whether the multiset of numbers in R130_judge_gauge's stdout+stderr is IDENTICAL
                across two runs at an unchanged source hash, on the GPU path.

IDENTIFICATION  Exact for variation reaching printed digits in two draws. NOT identified: rare
                variation needing many runs, and variation confined to an artifact. n=1 subject, so
                the result is about R130 and is NOT a rate over the slow tail -- R114 is the other
                censored round and is not run here.

SCOPE           population: 1 round (the one R395's detector points at) · instrument: the GATE's own
                NUM regex, imported · baseline: R394's 13 stable fast rounds · regime: pueue `gpu`
                group, so the GPU is not shared while it runs.

WORLDS
  W-TAIL-STABLE   R130 reproduces exactly. The source hash is a sound cache key across both the fast
                  rounds and the one expensive round tested, and R388's gate is not convicting honest
                  rows anywhere measured.
  W-TAIL-MOVES    R130's numbers differ. The cache is unsound where it would do all its work; the
                  key must include an execution fingerprint or GPU rounds must be excluded from the
                  cache entirely -- and R388's gate has a LIVE false-conviction mode on the slow tail.
  W-UNRUNNABLE    R130 does not execute here. Then the finding is about the GATE, not the cache: a
                  round the gate cannot re-run cannot be verified by re-running it, and that is a
                  structural hole in R388's coverage which no cache design repairs.

PREDICTION MATRIX
  W-TAIL-STABLE -> both runs exit 0 and the number multisets are equal
  W-TAIL-MOVES  -> both runs exit 0 and the multisets differ, with the differing tokens named
  W-UNRUNNABLE  -> either run exits non-zero; classified separately, NEVER folded into STABLE

PRE-REGISTERED KILL -- conditional on the controls, never on the comparison alone.
    if cuda_probe_ok and rng_plant_caught and constant_plant_stable:
        if either run returncode != 0 -> W-UNRUNNABLE   (its own class)
        elif numbers equal            -> W-TAIL-STABLE
        else                          -> W-TAIL-MOVES, differing tokens named
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  CUDA (+)    a bf16 matmul on the GPU must succeed BEFORE the subject runs. Without it a `stable`
              result could be the CPU fallback path, which is silence about the question asked --
              the instrument's unit and the claim's unit must be the same unit.
  PLANT (+)   an unseeded rng draw must be classified unstable, so STABLE is a measurement.
  PLANT (-)   a constant must be classified stable, so the detector is not a constant.
  EXITCODE    a non-zero exit is UNRUNNABLE_HERE, never STABLE. A crash repeats byte-identically.
  EXTRACTOR   the gate's NUM regex is IMPORTED from the gate, never re-implemented.

MULTIPLICITY    1 subject x 1 comparison. No rate is computed and none is admissible at n=1.
SEEDS           the subject's own. The rng plant is deliberately unseeded.
ARTIFACT        results/r396_tail_stability.json with the source hash.

IMPOSSIBLE HERE
  a rate over the slow tail  -- n=1. R114 is quiet under R395's detector and is not run here.
  proof of determinism       -- two draws bound detection from below only.
  isolating WHICH kernel varies -- would need a deterministic-algorithms sweep, a different round.
  a second release           -- one release.

EXIT
    0  controls hold and the subject is classified
    1  a control misbehaved -- UNVERIFIED
    2  the environment or population is unusable -- never a silent pass
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
SUBJECT = "R130_judge_gauge"
TIMEOUT = 5400
sys.path.insert(0, str(ROOT / "assurance"))


def main() -> int:
    try:
        from backfilled_findings_are_rederivable import NUM
    except Exception as e:
        print(f"  UNRUNNABLE: cannot import the gate's extractor ({e}). Exit 2 rather than copy it.")
        return 2
    d = next((q for q in ROOT.glob(f"E0*/A*/{SUBJECT}") if q.is_dir()), None)
    if d is None or not (d / "run.py").exists():
        print(f"  UNRUNNABLE: {SUBJECT} absent. Exit 2, never 0."); return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    src = hashlib.sha256((d / "run.py").read_bytes()).hexdigest()
    print(f"R396 · is the slow tail stable?   HEAD {head}   subject {SUBJECT}  src {src[:12]}\n")
    print(f"  ⛔ THE STEP WHOSE FAVOURABLE OUTCOME I WOULD FIND UNWELCOME. If R130 moves, the cache is")
    print(f"     unsound exactly where it would do all its work, and R388's committed gate has a LIVE")
    print(f"     false-conviction mode on the slow tail. The design must be able to deliver that.\n")

    # ---- CUDA control: the claim's unit and the instrument's unit must be the SAME unit ----------
    probe = HERE / "results" / "_cuda_probe.py"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text(
        "import torch\n"
        "assert torch.cuda.is_available(), 'no cuda'\n"
        "a = torch.randn(256, 256, dtype=torch.bfloat16, device='cuda')\n"
        "print('cuda_ok', torch.cuda.get_device_name(0), float((a @ a).float().sum()) == float((a @ a).float().sum()))\n")
    pr = subprocess.run([str(PY), str(probe)], capture_output=True, text=True, timeout=600)
    cuda_ok = pr.returncode == 0 and "cuda_ok" in pr.stdout
    print(f"  CONTROLS")
    print(f"    CUDA (+)   a bf16 matmul runs on the GPU: {cuda_ok}   "
          f"{'PASS' if cuda_ok else 'FAIL — a STABLE result could be the CPU path, i.e. silence'}")
    if not cuda_ok:
        print(f"      {(pr.stderr or pr.stdout).strip().splitlines()[-1][:120] if (pr.stderr or pr.stdout).strip() else ''}")

    def run_twice(path, cwd, timeout=TIMEOUT):
        outs, rcs = [], []
        for _ in range(2):
            try:
                p = subprocess.run([str(PY), str(path)], cwd=str(cwd), capture_output=True,
                                   text=True, timeout=timeout)
                outs.append(sorted(NUM.findall(p.stdout + p.stderr))); rcs.append(p.returncode)
            except subprocess.TimeoutExpired:
                return None, None, None
        return outs[0], outs[1], rcs

    plants = HERE / "results" / "_plants"
    plants.mkdir(parents=True, exist_ok=True)
    (plants / "rng.py").write_text(
        "import random\nprint('value', random.random())\nprint('value', random.random())\n")
    (plants / "const.py").write_text("print('value 0.5000 and 12345')\n")
    a, b, _ = run_twice(plants / "rng.py", plants, 300)
    rng_caught = (a is not None) and (a != b)
    c, e, _ = run_twice(plants / "const.py", plants, 300)
    const_stable = (c is not None) and (c == e)
    print(f"    PLANT (+)  an unseeded rng draw is classified unstable: {rng_caught}   "
          f"{'PASS' if rng_caught else 'FAIL'}")
    print(f"    PLANT (-)  a constant is classified stable:             {const_stable}   "
          f"{'PASS' if const_stable else 'FAIL'}")
    if not (cuda_ok and rng_caught and const_stable):
        print("\n  UNVERIFIED — a control misbehaved. Exit 1, never a verdict."); return 1

    # ---- the subject ----------------------------------------------------------------------------
    print(f"\n  SUBJECT — {SUBJECT}, run TWICE at unchanged source, GPU held by the pueue gpu group")
    n1, n2, rcs = run_twice(d / "run.py", d)
    if n1 is None:
        print(f"    TIMEOUT at {TIMEOUT}s — its own class, never folded into STABLE or MOVES.")
        v, same, diff = "W_UNRUNNABLE", None, []
        rcs = None
    elif any(r != 0 for r in rcs):
        print(f"    return codes {rcs} — NON-ZERO. A crash repeats byte-identically, so this is")
        print(f"    UNRUNNABLE_HERE and can never reach the STABLE branch.")
        v, same, diff = "W_UNRUNNABLE", None, []
    else:
        same = (n1 == n2)
        diff = sorted(set(n1) ^ set(n2))[:12]
        print(f"    return codes {rcs} · {len(n1)} numbers per run · "
              f"{'IDENTICAL' if same else 'DIFFER'}")
        if not same:
            print(f"    differing tokens (first 12): {diff}")
        v = "W_TAIL_STABLE" if same else "W_TAIL_MOVES"

    print()
    if v == "W_TAIL_STABLE":
        print(f"  W-TAIL-STABLE — the expensive round reproduces exactly. The source hash is a sound")
        print(f"  cache key on the one slow round the detector pointed at, and R388's gate is not")
        print(f"  convicting honest rows anywhere yet measured.")
        print(f"  ⚠ n=1. This is NOT a rate over the slow tail: R114 is the other censored round and")
        print(f"    was not run here. And two draws bound detection from below only.")
    elif v == "W_TAIL_MOVES":
        print(f"  W-TAIL-MOVES — the expensive round does NOT reproduce. The cache as specified would")
        print(f"  certify a stale verification exactly where 80% of the cost lives, and R388's gate")
        print(f"  has a LIVE false-conviction mode on the slow tail: it would fail an honest backfill")
        print(f"  and the failure would read as a bad row. The key needs an execution fingerprint, or")
        print(f"  GPU rounds must be excluded from re-run verification altogether.")
    else:
        print(f"  W-UNRUNNABLE — the finding is about the GATE, not the cache. A round the gate cannot")
        print(f"  re-run cannot be verified by re-running it, and no cache design repairs that. This")
        print(f"  is a structural hole in R388's coverage and it is measured, not assumed.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, subject=SUBJECT, subject_src_sha256=src, returncodes=rcs,
               n_numbers=(len(n1) if n1 else None), identical=same, differing=diff,
               controls=dict(cuda_ok=cuda_ok, rng_plant_caught=rng_caught,
                             constant_plant_stable=const_stable),
               verdict=v)
    outp = HERE / "results" / "r396_tail_stability.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
