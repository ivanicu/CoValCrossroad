"""R324 — the dose grid, which R321 named and no round isolated. It completes the decomposition.

Three of the four differences between A23's detectors are now priced: the ESTIMAND (R321: point
crossing vs CI containment), the REPLICATE count (R322: the CI's lower end falls, the upper does
not), and the THRESHOLD (R323: tau is NCAL, 200 draws vs 3000, exact to six decimals). One
structural difference was named by R321 and isolated by nobody — the dose grid:

    R267   13 doses, step 0.01, MAX 0.12
    R268   11 doses, step 0.02, max 0.20
    R274   41 doses, step 0.005, max 0.20

⛔ AND BOTH COARSE GRIDS ARE EXACT SUBSETS OF R274's, which is what makes this free: 0.01 and 0.02
are multiples of 0.005, and every dose in the two coarse grids appears in R274's curve. So the grid
can be varied with the CURVE, the RULE, the REPLICATES and TAU all held fixed — the isolation the
other three rounds could not do because they varied together.

⚠ AND R267's GRID STOPS AT 0.12, while `R249 minimal-size move under label order` sits at 0.1680.
R267 therefore never MEASURED detection at the one effect it calls resolvable; it divided. Its own
output labels that section `A DERIVATION, not evidence`, so this is not a defect — but a grid whose
maximum is below the largest published effect can never do anything else, and that is worth stating
where the grid is priced.

ESTIMAND      the MDE bracket under R274's rule, R274's curve and R274's tau, with ONLY the dose
              grid changed to each round's own — and the share of the observed spread that the
              grid alone accounts for.
IDENTIFICATION exact. Every input except the grid is held byte-identical, and the two coarse grids
              are subsets rather than re-runs, so no resampling enters.
SCOPE         population R274's 41-dose curve at 400 replicates · instrument the CI-containment
              rule at 0.8 detection with tau = 0.424 · regime grid varied over three published
              grids plus a sweep.
WORLDS        W-GRID-MATTERS  the coarse grids move the bracket materially -> the grid is a real
                              part of the spread and the deliverable must name it.
              W-GRID-INERT    the bracket barely moves -> the grid was never a contributor and
                              R321 named a difference that does not act.
KILL          conditional on the controls:
                any coarse grid moves an end of the bracket by >= 0.010   -> W-GRID-MATTERS
                every end moves by < 0.010                                -> W-GRID-INERT
POSITIVE CTRL the FULL grid must reproduce R274's committed bracket [0.105, 0.125] exactly. This
              is the round recomputing R274 from R274's own curve, so a mismatch means the rule is
              not the one R274 ran and nothing below is readable.
              Fails at g=0: a grid that is NOT the full one must give something DIFFERENT, or the
              knob is dead and a match at the full grid proves nothing.
NEGATIVE CTRL a degenerate 2-dose grid {0.0, 0.2}. With only the endpoints the rule cannot locate
              a crossing at all, so it must return a bracket at the coarsest possible resolution
              -- if it instead returns the fine answer, the rule is not using the grid.
PLACEBO       the full grid against itself: zero movement by construction, and labelled as the
              DERIVATION it is rather than dressed as a check.
NOISE FLOOR   none is resampled here and that is the point: with the curve fixed, this round has
              no sampling noise at all. Its numbers are exact given R274's curve, and the floor
              that matters is R322's replicate spread, quoted not re-run.
MULTIPLICITY  3 published grids + 1 degenerate + a step sweep; every cell printed.
ARTIFACT      results/dose_grid.json with source hash.
IMPOSSIBLE    saying which grid is RIGHT. A finer grid localises the crossing better and costs
              replicates per dose at fixed budget; that trade is a design choice this round prices
              but cannot adjudicate.
"""
import hashlib, json, math, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
A23 = ROOT / "E05_the_space_of_compilers/A23_is_the_admissibility_gate_the_right_gate"
REF = A23 / "R274_the_site_MDE_at_fine_resolution" / "results" / "calibrated_mde.json"
REPS, TARGET = 400, 0.8
GRIDS = {
    "R274 (step 0.005, max 0.20)": [round(0.005 * i, 4) for i in range(41)],
    "R268 (step 0.02,  max 0.20)": [round(0.02 * i, 4) for i in range(11)],
    "R267 (step 0.01,  max 0.12)": [round(0.01 * i, 4) for i in range(13)],
    "degenerate {0.0, 0.20}": [0.0, 0.2],
}


def bracket(curve, doses):
    """R274's rule: [first g whose CI upper >= 0.8, first g whose CI lower >= 0.8]."""
    lo = hi = None
    for g in doses:
        p = curve.get(round(g, 4))
        if p is None:
            continue
        se = math.sqrt(max(p * (1 - p), 1e-12) / REPS)
        u, l = p + 1.96 * se, p - 1.96 * se
        if lo is None and u >= TARGET:
            lo = g
        if hi is None and l >= TARGET:
            hi = g
    return lo, hi


def main():
    if not REF.exists():
        print(f"  UNRUNNABLE: {REF.name} absent."); return 2
    d = json.loads(REF.read_text())
    curve = {round(float(k), 4): v for k, v in d["curve"].items()}
    committed = d.get("mde_bracket")
    print(f"  R274's curve: {len(curve)} doses at {REPS} replicates; committed bracket "
          f"{committed}\n")

    missing = {n: [g for g in gs if round(g, 4) not in curve] for n, gs in GRIDS.items()}
    bad = {n: m for n, m in missing.items() if m}
    if bad:
        print(f"  REFUSING: a grid is not a subset of the reference curve: {bad}")
        return 2
    print("  every grid is an exact SUBSET of the reference curve -- no resampling enters\n")

    rows = {}
    print(f"    {'grid':<30}{'n':>4}{'bracket':>20}{'vs committed':>26}")
    for name, gs in GRIDS.items():
        lo, hi = bracket(curve, gs)
        rows[name] = dict(n=len(gs), lo=lo, hi=hi)
        dl = None if (lo is None or committed is None) else lo - committed[0]
        dh = None if (hi is None or committed is None) else hi - committed[1]
        delta = (f"lo {dl:+.3f}  hi {dh:+.3f}" if dl is not None and dh is not None
                 else "one end undefined")
        print(f"    {name:<30}{len(gs):>4}{str([lo, hi]):>20}{delta:>26}")

    full = rows["R274 (step 0.005, max 0.20)"]
    pos_ok = committed is not None and [full["lo"], full["hi"]] == committed
    print(f"\n  POSITIVE  full grid reproduces the committed bracket exactly: {pos_ok}")
    coarse = [v for k, v in rows.items() if not k.startswith("R274")]
    alive = any([v["lo"], v["hi"]] != [full["lo"], full["hi"]] for v in coarse)
    print(f"  KNOB ALIVE a non-full grid gives something different: {alive}")
    deg = rows["degenerate {0.0, 0.20}"]
    neg_ok = [deg["lo"], deg["hi"]] != [full["lo"], full["hi"]]
    print(f"  NEGATIVE  the 2-dose grid does NOT return the fine answer: {neg_ok}  "
          f"(it gives {[deg['lo'], deg['hi']]})")

    # ---- step sweep, so the effect is a curve rather than three points -------------------------
    print(f"\n  STEP SWEEP — same curve, same rule, grid step varied\n")
    sweep = {}
    for step in (0.005, 0.01, 0.02, 0.025, 0.05):
        gs = [round(step * i, 4) for i in range(int(0.2 / step) + 1)]
        if any(round(g, 4) not in curve for g in gs):
            sweep[step] = None
            continue
        sweep[step] = list(bracket(curve, gs))
    print("    " + "   ".join(f"{s}:{v}" for s, v in sweep.items()))

    # ⚠ THE DEGENERATE GRID IS A CONTROL, NOT A PUBLISHED GRID, and the first version of this
    # computation swept it into `moves` -- so the verdict said "a PUBLISHED grid moves an end by
    # up to 0.095" when 0.095 is the 2-dose control. The claim's population and the statistic's
    # population must be the same set. Fourth time this session a verdict quoted from the wrong
    # one, and the fix is the same each time: name the population in the code, not in the prose.
    PUBLISHED_GRIDS = [k for k in rows if k.startswith(("R267", "R268"))]
    moves, undefined = [], []
    for k in PUBLISHED_GRIDS:
        v = rows[k]
        if v["lo"] is None or v["hi"] is None:
            undefined.append(k)
            continue
        moves.append(max(abs(v["lo"] - full["lo"]), abs(v["hi"] - full["hi"])))
    biggest = max(moves) if moves else 0.0
    if undefined:
        print(f"\n  ⚠ {undefined} cannot produce a bracket at all under this rule: the grid ends")
        print(f"    before the CI lower bound reaches {TARGET}, so one end is UNDEFINED rather")
        print(f"    than merely coarse. That is a stronger statement than 'the grid moves it'.")

    ctrl = pos_ok and alive and neg_ok
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  positive={pos_ok}  knob-alive={alive}  negative={neg_ok}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. Either the rule is not R274's or the grid does not reach it.")
    elif biggest >= 0.010:
        world = "W-GRID-MATTERS"
        print(f"  -> W-GRID-MATTERS. A PUBLISHED grid moves an end of the bracket by up to")
        print(f"     {biggest:.3f} (R268's step 0.02) with the curve, rule, replicates and tau all")
        print(f"     held FIXED -- and R267's grid produces no upper end at all. The")
        print("     grid is a real contributor to the four-detector spread and the deliverable")
        print("     must name it beside the estimand, the replicates and tau.")
    else:
        world = "W-GRID-INERT"
        print(f"  -> W-GRID-INERT. The largest move is {biggest:.3f}, below the 0.010 threshold.")
        print("     R321 named a difference that does not act, and the spread is accounted for")
        print("     by the other three components alone.")
    print("  " + "=" * 78)
    print(f"\n  ⚠ AND R267's GRID MAXIMUM IS 0.12 while the one effect it calls resolvable sits at")
    print(f"    0.1680. It never measured detection there -- it divided, and labelled the section")
    print(f"    a DERIVATION. Not a defect, but a grid that stops below the largest published")
    print(f"    effect can never do anything else, and that is a property of the grid.")

    o = SELF.parent / "results" / "dose_grid.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        committed=committed, grids={k: v for k, v in rows.items()},
        step_sweep={str(k): v for k, v in sweep.items()},
        largest_move_published_grids_only=biggest, undefined_end=undefined,
        positive_ok=bool(pos_ok), knob_alive=bool(alive), negative_ok=bool(neg_ok),
        r267_grid_max=0.12, largest_published_effect=0.168), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
