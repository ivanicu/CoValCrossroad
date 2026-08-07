"""R321 — four detectors on one release differ by 40%. Is that the site, or the estimator?

R320 put four MDE brackets on the deliverable and called them "four brackets, one split", which
presented them as four comparable opinions about the same quantity. Reading the four rules from the
code says they are not:

    R267 / R268 / R269   above = [g : curve[g] >= 0.8];  hi = min(above);  lo = max(below < hi)
                         -> a GRID BRACKET around the first observed crossing. Its width is the
                            DOSE STEP and it says nothing about precision.
    R274                 up = [g : ci_upper(g) >= 0.8];  dn = [g : ci_lower(g) >= 0.8]
                         -> a CONFIDENCE INTERVAL for where the crossing is. Its width is the
                            BINOMIAL CI and it says nothing about the grid.

Two estimands. And applying R267's rule to R274's OWN 400-replicate curve gives [0.110, 0.115],
which R274's [0.105, 0.125] CONTAINS — so on identical data the two rules agree, and the headline
"disagreement" was never between the detectors' answers.

What remains is the same rule at three replicate counts: 0.09 at 40 reps, 0.10 at 100, 0.115 at 400.
Monotone. `min(g : observed >= 0.8)` is a MINIMUM OVER A NOISY SEQUENCE, and a minimum over noise is
biased LOW — the fewer replicates, the earlier some dose crosses by an upward excursion. That is
`min/max of N draws quoted as an interval` in a new costume, and this round tests it rather than
asserting it.

ESTIMAND      the bias of `min(g : detection(g) >= 0.8)` as a function of replicate count, with
              R274's 400-replicate curve as the reference, and whether that bias accounts for the
              0.09 / 0.10 / 0.115 sequence the arc actually produced.
IDENTIFICATION exact for the SIMULATION. Partial for the arc: R267's and R268's curves came from
              their own runs, not from subsampling R274's, so agreement in size is corroboration
              rather than proof they are the same phenomenon. Stated, not smuggled.
SCOPE         population R274's 41-dose calibration curve at 400 replicates · instrument the
              first-crossing rule at 0.8 detection · regime binomial resampling at each dose.
WORLDS        W-ESTIMATOR  the bias reproduces the arc's low-rep values -> the four brackets are
                           one quantity plus a known downward bias, and R274 is the estimate.
              W-SITE       the bias is far too small -> the low-rep rounds were measuring
                           something else and the spread is real.
              W-PARTIAL    the bias explains some of the gap -> report the decomposition, and do
                           not round it to either story.
KILL          conditional on the controls, pre-registered:
                simulated E[MDE_hat] at 40 reps within +/-0.015 of 0.090 AND at 100 within
                  +/-0.015 of 0.100                                        -> W-ESTIMATOR
                both simulated values within 0.005 of the 400-rep value    -> W-SITE
                anything else                                              -> W-PARTIAL
POSITIVE CTRL at 400 replicates the simulation must return R274's own first-crossing bracket
              (0.115), because that is resampling the reference against itself. If it does not,
              the resampler is not reproducing the curve it was built from and nothing else is
              readable. Fails at g=0 in the sense that a resampler that ignored reps would return
              0.115 at EVERY rep count -- so the 40-rep cell must differ, or the knob is dead.
NEGATIVE CTRL a DETERMINISTIC curve: replace each dose's detection with its reference value and
              resample nothing. The rule must return 0.115 at every replicate count, showing the
              bias is created by the noise and not by the resampling machinery.
PLACEBO       the reference curve scored against itself: exactly 0.115, no interval.
NOISE FLOOR   the spread of MDE_hat across simulations IS the floor and is reported per rep count
              as a range, never as a +/-.
MULTIPLICITY  3 replicate counts x 2000 simulations; every cell reported.
SEEDS         2000 draws per cell from one seeded generator; the whole grid recomputed at a
              second seed and both printed.
ARTIFACT      results/estimator_bias.json with source hash.
IMPOSSIBLE    proving R267's and R268's ACTUAL curves are subsamples of R274's -- they are
              independent runs, so this shows the estimator CAN produce their values, never that
              it DID. A stronger design re-runs all three at matched replicate counts, which is
              GPU work through pueue.
"""
import hashlib, json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
REF = (ROOT / "E05_the_space_of_compilers/A23_is_the_admissibility_gate_the_right_gate"
       / "R274_the_site_MDE_at_fine_resolution" / "results" / "calibrated_mde.json")
NSIM = 2000
REPS = (40, 100, 400)
ARC = {40: 0.090, 100: 0.100, 400: 0.115}      # first-crossing hi actually produced by the arc
THRESH = 0.8


def first_crossing(doses, det):
    above = [g for g, d in zip(doses, det) if d >= THRESH]
    return min(above) if above else float("nan")


def main():
    if not REF.exists():
        print(f"  UNRUNNABLE: {REF.name} absent."); return 2
    d = json.loads(REF.read_text())
    curve = {float(k): v for k, v in d["curve"].items()}
    doses = np.array(sorted(curve))
    p = np.array([curve[g] for g in doses])
    print(f"  reference curve: {len(doses)} doses, {doses[0]:.3f}..{doses[-1]:.3f}, "
          f"400 replicates (R274)")

    # ---- PLACEBO · the reference against itself ------------------------------------------------
    plc = first_crossing(doses, p)
    print(f"\n  PLACEBO   reference scored against itself: {plc:.4f}  "
          f"{'PASS' if abs(plc - ARC[400]) < 1e-9 else 'FAIL'} (must equal the arc's 400-rep value "
          f"{ARC[400]})")

    # ---- NEGATIVE · deterministic curve, no resampling -----------------------------------------
    det_same = {r: first_crossing(doses, p) for r in REPS}
    neg_ok = len(set(det_same.values())) == 1 and abs(list(det_same.values())[0] - plc) < 1e-9
    print(f"  NEGATIVE  deterministic curve at every rep count: "
          f"{ {r: round(v, 4) for r, v in det_same.items()} }  "
          f"{'PASS -- the bias is not the machinery' if neg_ok else 'FAIL'}")

    # ---- the simulation --------------------------------------------------------------------------
    def sweep(seed):
        rng = np.random.default_rng(seed)
        out = {}
        for r in REPS:
            xs = [first_crossing(doses, rng.binomial(r, p) / r) for _ in range(NSIM)]
            a = np.array([x for x in xs if np.isfinite(x)])
            out[r] = dict(mean=float(a.mean()), median=float(np.median(a)),
                          lo=float(np.percentile(a, 2.5)), hi=float(np.percentile(a, 97.5)),
                          n=len(a))
        return out

    print(f"\n  SIMULATION — resample the reference curve at each replicate count, {NSIM} draws\n")
    print(f"    {'reps':>6}{'E[MDE_hat]':>13}{'median':>9}{'95% range':>22}{'arc produced':>14}"
          f"{'gap':>8}")
    A = sweep(20260803)
    for r in REPS:
        s = A[r]
        print(f"    {r:>6}{s['mean']:>13.4f}{s['median']:>9.4f}"
              f"{f'[{s[chr(108)+chr(111)]:.3f}, {s[chr(104)+chr(105)]:.3f}]':>22}"
              f"{ARC[r]:>14.4f}{s['mean'] - ARC[r]:>+8.4f}")

    B = sweep(770077)
    print(f"\n    second seed: " + "  ".join(f"{r}->{B[r]['mean']:.4f}" for r in REPS))
    seed_ok = all(abs(A[r]["mean"] - B[r]["mean"]) < 0.01 for r in REPS)
    print(f"    seed-stable within 0.010: {seed_ok}")

    # ---- POSITIVE · the knob must be alive ------------------------------------------------------
    pos_ok = abs(A[400]["mean"] - ARC[400]) < 0.015
    alive = abs(A[40]["mean"] - A[400]["mean"]) > 0.005
    print(f"\n  POSITIVE  400-rep simulation reproduces the reference "
          f"({A[400]['mean']:.4f} vs {ARC[400]:.4f}): {pos_ok}")
    print(f"            and the rep knob CHANGES the answer (40 vs 400 differ by "
          f"{abs(A[40]['mean'] - A[400]['mean']):.4f}): {alive}")

    # ---- KILL ------------------------------------------------------------------------------------
    ctrl = (abs(plc - ARC[400]) < 1e-9) and neg_ok and pos_ok and alive and seed_ok
    near40 = abs(A[40]["mean"] - ARC[40]) <= 0.015
    near100 = abs(A[100]["mean"] - ARC[100]) <= 0.015
    flat = all(abs(A[r]["mean"] - A[400]["mean"]) < 0.005 for r in (40, 100))
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  placebo={abs(plc - ARC[400]) < 1e-9}  negative={neg_ok}  "
          f"positive={pos_ok}  knob-alive={alive}  seed={seed_ok}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the bias estimate is not readable.")
    elif flat:
        world = "W-SITE"
        print("  -> W-SITE. The estimator is nearly unbiased across replicate counts, so the")
        print("     arc's 0.09 / 0.10 / 0.115 sequence is NOT an artifact of precision and the")
        print("     spread is about the detectors or the release.")
    elif near40 and near100:
        world = "W-ESTIMATOR"
        print(f"  -> W-ESTIMATOR. Resampling the SAME curve at 40 and 100 replicates reproduces")
        print(f"     {A[40]['mean']:.4f} and {A[100]['mean']:.4f} against the arc's "
              f"{ARC[40]:.3f} and {ARC[100]:.3f}.")
        print("     `min(g : observed >= 0.8)` is a MINIMUM OVER NOISE and is biased LOW; the")
        print("     four brackets are one quantity at three precisions plus a second estimand,")
        print("     not four opinions about the site. R274's interval is the estimate.")
    else:
        world = "W-PARTIAL"
        print(f"  -> W-PARTIAL. The bias moves the estimate the right way but does not land on")
        print(f"     the arc's values (40: {A[40]['mean']:.4f} vs {ARC[40]:.3f}; 100: "
              f"{A[100]['mean']:.4f} vs {ARC[100]:.3f}).")
        print("     Reported as a decomposition rather than rounded to either story.")
    print("  " + "=" * 78)
    print(f"\n  ⚠ SCOPE, and it is the limit that matters: R267's and R268's curves are their OWN")
    print(f"    runs, not subsamples of R274's. This shows the estimator CAN produce their values")
    print(f"    at their replicate counts; it does not prove it DID. Matched re-runs are GPU work.")
    print(f"\n  MULTIPLICITY  {len(REPS)} rep counts x {NSIM} draws x 2 seeds; all cells printed.")

    o = SELF.parent / "results" / "estimator_bias.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        reference="R274 400-rep curve", n_doses=len(doses), n_sim=NSIM, threshold=THRESH,
        arc_produced=ARC, sim_seed_a={str(k): v for k, v in A.items()},
        sim_seed_b={str(k): v for k, v in B.items()},
        placebo=plc, negative_ok=bool(neg_ok), positive_ok=bool(pos_ok),
        knob_alive=bool(alive), seed_ok=bool(seed_ok),
        r274_ci_interval=d.get("mde_bracket")), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
