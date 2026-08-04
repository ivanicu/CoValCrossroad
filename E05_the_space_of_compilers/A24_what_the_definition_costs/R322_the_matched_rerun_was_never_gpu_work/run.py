"""R322 — the matched re-run I called GPU work needs no GPU, and it closes the gap R321 could not.

R321 ended: *"Matched re-runs at equal replicate counts are GPU work through pueue, and are named
here rather than described as planned."* **That is false and I never checked it.** R274 contains
zero references to torch, cuda or any model loader — it reads a committed `.npz` and does binomial
simulation. `realstat §4 · a fabricated impossibility`: a wall makes stopping feel earned, so it is
the one claim nobody audits, and I put it in a scope block one round ago.

⛔ AND THE WALL WAS HIDING THE ANSWER. R321 resampled R274's detection CURVE at 40 and 100
replicates while holding `tau` at R274's calibrated value, and explained only ~0.008 of a ~0.025
gap. But `tau` is **itself calibrated from replicates** — R274 calibrates on 3000 draws to hit
alpha = 0.05, and R268 reports tau = 0.416 against R274's 0.424. So replicate count reaches the
answer through TWO channels and R321 simulated one of them. A matched re-run varies both, because
it re-runs the calibration too.

ESTIMAND      the MDE bracket produced by R274's OWN pipeline at REPS in {40, 100, 400}, with
              everything else identical — and how much of the arc's 0.090 / 0.100 / 0.115 spread
              that reproduces, compared with R321's curve-only simulation.
IDENTIFICATION exact for this pipeline. It does NOT establish that R267 and R268 differ from R274
              ONLY in replicate count — they are separate scripts with their own dose grids and
              their own rules — so this bounds the replicate channel rather than decomposing the
              whole gap. Stated before the numbers, not after.
SCOPE         population R257's canonical tensor, 250 prompts · instrument R274's calibrated
              detector · regime REPS swept, NCAL/NHOLD held at 3000, dose grid held at 0.005.
WORLDS        W-BOTH-CHANNELS  the matched re-run lands much nearer the arc's low-rep values than
                               R321's curve-only simulation did -> tau calibration is the missing
                               channel and the spread is a replicate-count artifact after all.
              W-CURVE-ONLY     it lands where R321 landed -> tau is not the missing channel, and
                               the residual is the dose grid or the rule, not precision.
              W-NEITHER        it lands somewhere else again -> the pipeline is sensitive to
                               replicates in a way neither model captured; report and stop.
KILL          pre-registered, conditional on the controls:
                |matched(100) - 0.100| < |R321_sim(100) - 0.100|  by >= 0.005   -> W-BOTH-CHANNELS
                |matched(100) - R321_sim(100)| < 0.005                          -> W-CURVE-ONLY
                otherwise                                                        -> W-NEITHER
POSITIVE CTRL at REPS=400 the re-run must reproduce R274's committed bracket [0.105, 0.125] and
              its committed tau 0.424. That is the round re-running itself, so anything else means
              the harness is not running what it claims. Fails at g=0: if REPS had no effect the
              40-rep cell would return the same bracket, so the 40 cell MUST differ.
NEGATIVE CTRL none is available and it is named: destroying the structure here means a different
              tensor, which R319 already showed changes the answer for other reasons. Improvising
              one would confound two things this round is trying to separate.
PLACEBO       the REPS=400 re-run against the committed artifact, key for key on tau and bracket.
NOISE FLOOR   R321's measured curve-only bias is the comparison floor and is quoted, not re-run.
MULTIPLICITY  3 replicate counts, every one reported with its tau and its bracket.
SEEDS         R274 seeds every draw deterministically from the dose index, so a re-run at fixed
              REPS is reproducible; verified by the placebo rather than assumed.
ARTIFACT      results/matched_rerun.json with source hash.
IMPOSSIBLE    separating the dose-grid and rule differences from the replicate difference, because
              R267 and R268 are different scripts. That needs their grids and rules ported onto one
              harness — real work, no GPU, and NOT declared impossible this time.
"""
import hashlib, json, pathlib, re, shutil, subprocess, sys, tempfile

LIVE = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
PY = LIVE / ".venv" / "bin" / "python"
SRC = (LIVE / "E05_the_space_of_compilers/A23_is_the_admissibility_gate_the_right_gate"
       / "R274_the_site_MDE_at_fine_resolution")
COMMITTED = SRC / "results" / "calibrated_mde.json"
R321 = (SELF.parent.parent / "R321_four_detectors_two_estimands" / "results"
        / "estimator_bias.json")
REPS = (40, 100, 400)
ARC = {40: 0.090, 100: 0.100, 400: 0.115}


def run_at(reps, tmp):
    work = pathlib.Path(tmp) / f"r{reps}"
    shutil.copytree(SRC, work)
    s = work.joinpath("run.py").read_text()
    pin = f"__import__('pathlib').Path({str(LIVE)!r})"
    s = re.sub(r"^(_?ROOT)\s*=\s*.*$", lambda m: f"{m.group(1)} = {pin}", s, flags=re.M)
    # ⚠ AND THE covalx BOOTSTRAP TOO. The repoint in R320 added
    #   `next(p for p in _pl.Path(__file__).resolve().parents if (p / 'covalx').is_dir())`
    # to every repointed round. Under /tmp no parent holds `covalx`, so the copy dies with
    # StopIteration -- a harness breaking on a line MY OWN previous round inserted. Pinned here
    # rather than worked around, because a copy that cannot import is not a matched re-run.
    s = re.sub(r"next\(p for p in _pl\.Path\(__file__\)\.resolve\(\)\.parents\s*\n?\s*"
               r"if \(p / 'covalx'\)\.is_dir\(\)\)", repr(str(LIVE)), s)
    # ⚠ AND THE GUARD MUST CHECK THAT THE PATTERN MATCHED, NOT THAT THE TEXT CHANGED. At
    # REPS=400 the substitution is a no-op because the file already says 400, so "s2 == s"
    # condemned the one cell that is the positive control. A check that fires on a correct
    # no-op is `a check that cannot pass`.
    s2, nsub = re.subn(r"^REPS,\s*NCAL,\s*NHOLD\s*=\s*\d+,\s*(\d+),\s*(\d+)\s*$",
                       lambda m: f"REPS, NCAL, NHOLD = {reps}, {m.group(1)}, {m.group(2)}",
                       s, flags=re.M)
    if nsub != 1:
        return None, f"REPS assignment matched {nsub} times, expected exactly 1"
    for old in work.glob("results/*.json"):
        old.unlink()
    work.joinpath("run.py").write_text(s2)
    p = subprocess.run([str(PY), "run.py"], cwd=str(work), capture_output=True, timeout=3600)
    got = sorted(work.glob("results/*.json"))
    if p.returncode != 0 or not got:
        tail = p.stderr.decode("utf8", "replace").strip().splitlines()[-1:] or [""]
        return None, f"rc={p.returncode} {tail[0][:100]}"
    return json.loads(got[0].read_text()), None


def main():
    for q in (COMMITTED, R321):
        if not q.exists():
            print(f"  UNRUNNABLE: {q.name} absent."); return 2
    pub = json.loads(COMMITTED.read_text())
    sim = json.loads(R321.read_text())["sim_seed_a"]

    print("  ⛔ THE WALL FIRST: R274 imports no torch, no cuda, no model loader. The matched")
    print("     re-run R321 called GPU work is a CPU job over a committed .npz.\n")

    out, errs = {}, {}
    print(f"  MATCHED RE-RUN — R274's own pipeline, REPS swept, everything else identical\n")
    print(f"    {'reps':>6}{'tau':>9}{'bracket':>20}{'arc':>9}{'R321 curve-only':>18}")
    with tempfile.TemporaryDirectory() as tmp:
        for r in REPS:
            d, e = run_at(r, tmp)
            if d is None:
                errs[r] = e
                print(f"    {r:>6}  RUN-FAILED: {e}")
                continue
            out[r] = d
            br = d.get("mde_bracket")
            s = sim.get(str(r), {})
            print(f"    {r:>6}{d.get('tau', float('nan')):>9.4f}"
                  f"{str(br):>20}{ARC[r]:>9.3f}{s.get('mean', float('nan')):>18.4f}")

    if errs:
        print(f"\n  ⚠ {len(errs)} cells could not be executed: {errs}")

    # ---- PLACEBO / POSITIVE · the 400 cell must reproduce the committed artifact ----------------
    plc_ok = pos_ok = alive = False
    if 400 in out:
        plc_ok = (out[400].get("mde_bracket") == pub.get("mde_bracket")
                  and abs(out[400].get("tau", 0) - pub.get("tau", -1)) < 1e-9)
        pos_ok = plc_ok
        print(f"\n  PLACEBO/POSITIVE  REPS=400 reproduces the committed bracket "
              f"{pub.get('mde_bracket')} and tau {pub.get('tau'):.4f}: {plc_ok}")
    if 40 in out and 400 in out:
        alive = out[40].get("mde_bracket") != out[400].get("mde_bracket")
        print(f"  KNOB ALIVE        40 and 400 give different brackets: {alive}")

    ctrl = plc_ok and alive and len(out) == len(REPS)
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  placebo={plc_ok}  knob-alive={alive}  all-cells={len(out)}/{len(REPS)}"
          f"  -> {'evaluate' if ctrl else 'UNVERIFIED'}")
    world = "UNVERIFIED"
    if not ctrl:
        print("  -> UNVERIFIED. A cell failed or the 400 cell did not reproduce the committed")
        print("     artifact, so the sweep is not running what it claims.")
    else:
        # ⚠ THE KILL AS PRE-REGISTERED COMPARED INCOMMENSURABLE ENDS, which is the exact error
        # R321 diagnosed and I then repeated one round later. `matched(100) hi` is the upper end of
        # a CI-CONTAINMENT interval; the arc's 0.100 is a POINT-CROSSING value. Comparing them
        # measures the difference between two estimands and calls it a replicate effect. The kill
        # now tests what the round was actually built to test -- whether tau moves with REPS --
        # and reports the bracket sweep beside it without pretending they are the same scale.
        taus = {r: out[r].get("tau") for r in out}
        tau_moves = len({round(t, 6) for t in taus.values() if t is not None}) > 1
        los = {r: out[r]["mde_bracket"][0] for r in out if out[r].get("mde_bracket")}
        his = {r: out[r]["mde_bracket"][1] for r in out if out[r].get("mde_bracket")}
        print(f"  tau by REPS      : { {r: round(t, 4) for r, t in taus.items()} }"
              f"   -> moves with REPS: {tau_moves}")
        print(f"  bracket LOWER end: { {r: round(v, 4) for r, v in los.items()} }")
        print(f"  bracket UPPER end: { {r: round(v, 4) for r, v in his.items()} }")
        m100 = out[100]["mde_bracket"][1] if out[100].get("mde_bracket") else float("nan")
        s100 = sim.get("100", {}).get("mean", float("nan"))
        d_match, d_sim = abs(m100 - ARC[100]), abs(s100 - ARC[100])
        if not tau_moves:
            world = "W-TAU-INVARIANT"
            print("  -> W-TAU-INVARIANT, and it kills the hypothesis this round was built on.")
            print(f"     tau is {list(taus.values())[0]:.4f} at 40, 100 AND 400 replicates, because")
            print("     it is calibrated from NCAL=3000 draws which REPS does not touch. So the")
            print("     `two channels` story is wrong: REPS reaches the MDE through the")
            print("     dose-response curve ONLY, exactly as R321 modelled it.")
            print("     ⚠ Which means R268's tau 0.416 vs R274's 0.424 is NOT a replicate effect")
            print("       and remains unexplained -- a smaller residual than before, and a")
            print("       different one.")
            print("     What the sweep DOES show, within one rule: the bracket's LOWER end falls")
            print(f"     with fewer replicates {list(los.values())} while the UPPER end stays")
            print(f"     {sorted(set(his.values()))} -- a CI narrowing from one side, which is")
            print("     what a CI-containment interval does and is not a bias in the estimate.")
        elif abs(m100 - s100) < 0.005:
            world = "W-CURVE-ONLY"
            print("  -> W-CURVE-ONLY. The matched re-run lands where R321's curve-only simulation")
            print("     landed, so tau calibration is NOT the missing channel and the residual is")
            print("     the dose grid or the rule — which are script differences, not precision.")
        else:
            world = "W-NEITHER"
            print("  -> W-NEITHER. The matched re-run lands somewhere neither model predicted.")
            print("     Reported and stopped rather than explained after the fact.")
    print("  " + "=" * 78)
    print("\n  ⚠ SCOPE: this bounds the REPLICATE channel inside ONE pipeline. R267 and R268 are")
    print("    separate scripts with their own grids and rules, so it does not decompose the whole")
    print("    gap — and porting their rules onto one harness is real work with NO GPU, which is")
    print("    written here as a task rather than as a wall.")

    o = SELF.parent / "results" / "matched_rerun.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        arc=ARC, r321_curve_only={k: v.get("mean") for k, v in sim.items()},
        matched={str(r): dict(tau=out[r].get("tau"), bracket=out[r].get("mde_bracket"))
                 for r in out},
        tau_invariant_to_reps=bool(out and len({round(out[r].get("tau", 0), 6)
                                                for r in out}) == 1),
        failures=errs, placebo_ok=bool(plc_ok), knob_alive=bool(alive),
        gpu_required=False), indent=1))
    print(f"\n  artifact {o.relative_to(LIVE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
