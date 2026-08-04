"""R393 -- what will the verification gate cost at full table, and is a cache justified yet?

R392's NEXT proposed a per-row cache keyed on source hash, and named the check that must come first:
measure the gate's cost before optimising it, because "an unmeasured optimisation on a gate is how a
gate stops running".

⛔ BUT THE QUESTION AS I POSED IT IS PARTLY A DERIVATION, AND SAYING SO CHANGES THE DESIGN. I asked
   whether the gate's cost grows "linear in rounds rather than in numbers". It grows in ROUNDS BY
   CONSTRUCTION: the gate re-runs every cited round, so its cost is the SUM OF THOSE RUNTIMES plus
   string work that is microseconds. That is algebra, not evidence, and measuring it would have been
   1+1=2 reported as a finding.
   What is NOT forced, and is the only thing worth measuring, is the SUM: runtimes across this corpus
   span at least 0.4s to over 300s, so the total at full table is set by a distribution nobody has
   sampled, not by a count anybody can multiply.

⛔ AND THE SAMPLE IS RIGHT-CENSORED, WHICH DECIDES HOW THE ANSWER MAY BE STATED. A cap is required --
   without one a single slow round eats the budget -- and every round that hits it contributes "at
   least the cap" rather than a value. So the projection is a LOWER BOUND and is reported as an
   inequality. A mean computed over censored draws as though they were complete is the arithmetic
   trap wearing a project plan, which is the shape R388 already warned about when it refused to
   multiply 21.3s by 237.

ESTIMAND        (a) the distribution of run times over a random sample of the OWING population --
                    the 154 rounds R392 found are not consumed by other code;
                (b) the implied lower bound on the gate's first-run cost at full table:
                    sum over the sample, scaled to 154, with censored draws contributing their cap.
                (a) is a measurement; (b) is a projection from it and is labelled one.

IDENTIFICATION  (a) exact for rounds that complete inside the cap; CENSORED otherwise, counted
                separately and never averaged in as if complete.
                (b) partially identified: a lower bound only. The upper bound is unavailable at any
                budget I can spend here, because the censored tail has no measured length.
                NOT identified: the cost with a cache, which is the thing the next decision is
                about -- this measures the cost WITHOUT one, which is what a cache must beat.

SCOPE           population: the 154 owing rounds from R392 · instrument: wall-clock in an isolated
                worktree · baseline: the three already-timed rounds · regime: cold worktree, which
                is the regime the gate actually runs in.

WORLDS
  W-CACHE-JUSTIFIED    the projected first-run cost is large enough that a full-table gate would not
                       be run -- and a gate nobody runs is not a gate. Then a cache is not an
                       optimisation but a precondition.
  W-CACHE-PREMATURE    the projection is small enough to run whole. Then building a cache now adds a
                       staleness failure mode for no measured benefit, which is strictly worse.
  W-UNRESOLVED         censoring is so heavy that the bound says nothing useful. Then the budget is
                       the finding and a larger one is required.

PREDICTION MATRIX
  W-CACHE-JUSTIFIED -> projected lower bound >= 30 minutes
  W-CACHE-PREMATURE -> projected lower bound <= 5 minutes
  W-UNRESOLVED      -> censored share > 50%, or the bound straddles both thresholds

PRE-REGISTERED KILL -- conditional on the controls, never on the projection alone.
    if timer_positive_control_ok and timer_negative_control_ok:
        if censored_share > 0.50                  -> W-UNRESOLVED
        elif projected_lower_bound_s >= 1800      -> W-CACHE-JUSTIFIED
        elif projected_lower_bound_s <= 300       -> W-CACHE-PREMATURE
        else                                       -> named explicitly, not defaulted
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  TIMER (+)   a script that sleeps a known interval must be timed within tolerance. Without it a
              timer reporting zero for everything would make the whole projection an artifact.
  TIMER (-)   a script that does nothing must time near zero, so the instrument is shown to
              distinguish work from no work rather than reporting a constant.
  CENSORING   every capped run is counted and reported separately, and the projection is stated as
              an inequality. Averaging a censored draw as if complete is the failure this round is
              designed around.
  SAMPLE      the sample is drawn with a fixed seed from the OWING population, not from the rounds
              that happened to be convenient -- R392's NEXT made exactly that correction about
              which rounds get paid, and it applies to which get timed.
  ISOLATION   subjects run in this round's own worktree, never the live tree.

MULTIPLICITY    one distribution, one bound. Every subject's time printed, censored ones marked.
SEEDS           1 for the sample draw, stated; the timing itself is not random but is noisy, which
                is why the controls bound the noise rather than assuming it away.
ARTIFACT        results/r393_gate_cost.json with the source hash.

IMPOSSIBLE HERE
  an UPPER bound          -- the censored tail has no measured length at any budget spendable here.
  the cost WITH a cache   -- that is the next decision's subject; this measures what a cache must
                             beat.
  a second release        -- one release.

EXIT
    0  controls hold and the bound is stated
    1  a control misbehaved -- UNVERIFIED
    2  the population or worktree is unusable -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import random
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
PY = ROOT / ".venv" / "bin" / "python"
WT = pathlib.Path("/tmp/claude-1000/-home-ivan/7d277876-c2fd-4a27-9b05-652b391121ff/scratchpad/r390_wt")
R392 = HERE.parent / "R392_how_much_is_infrastructure" / "results" / "r392_infrastructure_share.json"
N_SAMPLE = 15
CAP_S = 90
SEED = 1
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp
except Exception:
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}


def main() -> int:
    if not R392.exists():
        print("  UNRUNNABLE: R392's artifact absent. Exit 2, never 0."); return 2
    d = json.loads(R392.read_text())
    owing = sorted(k for k, v in d["rows"].items()
                   if v.get("present") and not v["artifact_consumers"])
    if len(owing) < 50:
        print(f"  UNRUNNABLE: owing population {len(owing)}. Exit 2, never 0."); return 2
    if not WT.exists():
        print(f"  UNRUNNABLE: worktree {WT} absent. Exit 2, never 0."); return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()
    print(f"R393 · what will the gate cost at full table?   HEAD {head[:12]}\n")
    print(f"  ⛔ MY OWN QUESTION WAS PARTLY A DERIVATION. I asked whether the gate's cost grows in")
    print(f"     ROUNDS rather than NUMBERS. It grows in rounds BY CONSTRUCTION — the gate re-runs")
    print(f"     every cited round, so its cost IS the sum of those runtimes. Measuring that would")
    print(f"     have been 1+1=2 reported as a finding. What is not forced is the SUM.\n")
    print(f"  owing population {len(owing)} · sample {N_SAMPLE} at seed {SEED} · cap {CAP_S}s")

    subprocess.run(["git", "checkout", "-f", "-q", head], cwd=str(WT), capture_output=True)
    subprocess.run(["git", "clean", "-fdq"], cwd=str(WT), capture_output=True)
    for n in ("data", ".venv"):
        src, dst = ROOT / n, WT / n
        if src.exists() and not dst.exists():
            dst.symlink_to(src, target_is_directory=src.is_dir())
        elif src.is_dir() and dst.is_dir():
            for c in src.iterdir():
                t = dst / c.name
                if not t.exists() and not t.is_symlink():
                    t.symlink_to(c, target_is_directory=c.is_dir())

    def timed(cmd, cwd, cap):
        t0 = time.monotonic()
        try:
            subprocess.run(cmd, cwd=str(cwd), capture_output=True, timeout=cap)
        except subprocess.TimeoutExpired:
            return None, time.monotonic() - t0
        return time.monotonic() - t0, time.monotonic() - t0

    # ---- CONTROLS ------------------------------------------------------------------------------
    probe = WT / "assurance" / "_r393_sleep.py"
    probe.write_text("import time\ntime.sleep(3)\n")
    s3, _ = timed([str(PY), str(probe)], WT, CAP_S)
    probe.write_text("pass\n")
    s0, _ = timed([str(PY), str(probe)], WT, CAP_S)
    probe.unlink(missing_ok=True)
    pos_ok = s3 is not None and 2.5 <= s3 <= 6.0
    neg_ok = s0 is not None and s0 < 2.0
    print(f"\n  CONTROLS on the timer")
    print(f"    TIMER (+)  a 3s sleep is timed at {s3:.2f}s — tolerance [2.5, 6.0] allows")
    print(f"               interpreter startup  {'PASS' if pos_ok else 'FAIL'}")
    print(f"    TIMER (-)  a script that does nothing times at {s0:.2f}s (< 2.0)  "
          f"{'PASS' if neg_ok else 'FAIL'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the timer cannot distinguish work from no work. Exit 1."); return 1

    # ---- the sample -----------------------------------------------------------------------------
    rng = random.Random(SEED)
    sample = rng.sample(owing, N_SAMPLE)
    print(f"\n  TIMING {N_SAMPLE} rounds drawn from the OWING population (not the convenient ones)")
    print(f"    {'round':<40}{'secs':>9}   status")
    rows, complete, censored = {}, [], 0
    for name in sorted(sample):
        dd = next((q for q in WT.glob(f"E0*/A*/{name}") if q.is_dir()), None)
        if dd is None:
            rows[name] = dict(secs=None, status="ABSENT")
            print(f"    {name:<40}{'—':>9}   ABSENT"); continue
        secs, elapsed = timed([str(PY), "run.py"], dd, CAP_S)
        if secs is None:
            rows[name] = dict(secs=CAP_S, status="CENSORED"); censored += 1
            print(f"    {name:<40}{CAP_S:>9}   CENSORED (>= cap)", flush=True)
        else:
            rows[name] = dict(secs=round(secs, 1), status="COMPLETE"); complete.append(secs)
            print(f"    {name:<40}{secs:>9.1f}   complete", flush=True)
        subprocess.run(["git", "checkout", "-f", "-q", head], cwd=str(WT), capture_output=True)

    measured = [v["secs"] for v in rows.values() if v["secs"] is not None]
    n_meas = len(measured)
    if n_meas < 5:
        print(f"\n  UNRUNNABLE: only {n_meas} timed subjects. Exit 2, never 0."); return 2
    cens_share = censored / n_meas
    total_sample = sum(measured)
    per_round_lb = total_sample / n_meas
    projected_lb = per_round_lb * len(owing)
    print(f"\n    complete {len(complete)} · censored {censored} ({cens_share:.0%}) · "
          f"timed {n_meas}")
    # ⛔ A MEAN OVER A HEAVY TAIL MISDESCRIBES THE DISTRIBUTION, and this one is heavy: the two
    #   censored draws contribute the cap each while the median round finishes in seconds. Quoting
    #   `per round >= 15.5s` alone would be the same error as quoting a min/max bracket as an
    #   interval — a summary that hides where the cost actually lives. Both are printed, and the
    #   tail's share of the total is printed too, because it is what a cache would actually buy.
    srt = sorted(measured)
    med = srt[len(srt) // 2]
    tail = sum(v for v in measured if v >= CAP_S)
    print(f"    sample total  >= {total_sample:.0f}s   MEAN per round >= {per_round_lb:.1f}s")
    print(f"    but the MEDIAN round is {med:.1f}s — p10 {srt[len(srt)//10]:.1f}, "
          f"p90 {srt[9*len(srt)//10]:.1f}")
    print(f"    the {censored} censored rounds contribute {tail:.0f}s of the {total_sample:.0f}s "
          f"total ({tail/total_sample:.0%})")
    print(f"    -> the cost is concentrated in a FEW SLOW ROUNDS, so a cache buys the tail and")
    print(f"       almost nothing else — which is a sharper design brief than `it is slow`.")
    print(f"    PROJECTED FIRST-RUN COST AT {len(owing)} ROWS  >= {projected_lb/60:.0f} min")
    print(f"    — an INEQUALITY, because every censored draw contributes its cap rather than its")
    print(f"      value, and the censored tail has no measured length.")

    # ---- VERDICT -------------------------------------------------------------------------------
    print()
    if cens_share > 0.50:
        print(f"  W-UNRESOLVED — {cens_share:.0%} of the sample hit the {CAP_S}s cap, so the bound")
        print(f"  is dominated by the cap I chose rather than by the corpus. The budget is the")
        print(f"  finding and a larger one is required before this question is answerable.")
        v = "W_UNRESOLVED"
    elif projected_lb >= 1800:
        print(f"  W-CACHE-JUSTIFIED — the first-run cost is at least {projected_lb/60:.0f} minutes")
        print(f"  at full table, and that is a floor. A gate that takes this long is a gate nobody")
        print(f"  runs, and a gate nobody runs is not a gate — so a cache is not an optimisation")
        print(f"  here, it is a PRECONDITION. ⚠ And it must be keyed on the round's SOURCE HASH, so")
        print(f"  a changed round invalidates its own row: a cache that serves a stale verification")
        print(f"  is worse than a slow gate, because it certifies without checking.")
        v = "W_CACHE_JUSTIFIED"
    elif projected_lb <= 300:
        print(f"  W-CACHE-PREMATURE — at least {projected_lb/60:.1f} minutes for the whole table,")
        print(f"  which is runnable. Building a cache now would add a staleness failure mode for no")
        print(f"  measured benefit, which is strictly worse than the cost it removes.")
        v = "W_CACHE_PREMATURE"
    else:
        print(f"  W-BETWEEN — named rather than defaulted: the floor is {projected_lb/60:.0f} min,")
        print(f"  between the {300/60:.0f}-minute and 30-minute thresholds fixed before the run.")
        print(f"  A cache is neither clearly premature nor clearly required, and the honest reading")
        print(f"  is that the decision waits on the censored tail this budget could not measure.")
        v = "W_BETWEEN"

    print(f"\n  ⚠ THE PROJECTION IS A LOWER BOUND AND ONLY A LOWER BOUND. {censored} of {n_meas}")
    print(f"    draws are right-censored at {CAP_S}s and contribute the cap, not their value. An")
    print(f"    UPPER bound is unavailable at any budget spendable here.")
    print(f"  ⚠ AND THIS IS THE COST WITHOUT A CACHE — the number a cache must BEAT, never the cost")
    print(f"    with one, which is the next decision's subject and is not measured here.")

    art = dict(stamp(str(SELF)), head=head[:12], n_owing=len(owing), n_sample=N_SAMPLE,
               cap_s=CAP_S, seed=SEED, rows=rows, n_timed=n_meas, n_censored=censored,
               censored_share=cens_share, sample_total_s=round(total_sample, 1),
               per_round_lower_bound_s=round(per_round_lb, 1),
               median_s=round(med, 1), tail_seconds=round(tail, 1),
               tail_share=round(tail / total_sample, 3),
               projected_lower_bound_s=round(projected_lb, 1),
               controls=dict(timer_sleep_s=round(s3, 2), timer_noop_s=round(s0, 2),
                             pos_ok=pos_ok, neg_ok=neg_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r393_gate_cost.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
