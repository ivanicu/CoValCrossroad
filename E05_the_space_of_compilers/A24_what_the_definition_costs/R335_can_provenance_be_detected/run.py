"""R335 — R295's leak detector was VALIDATED on six arms and never CALIBRATED. Here is its OC.

R334 closed by claiming clause 3 "has no instrument at all". False, and one artifact read away:
R295 built one -- the slope of the clause-2 margin across quintiles of within-prompt half-agreement,
with a `fitted` label per arm and an excess over an unfitted floor. Third round in a row whose
next-gradient line was wrong about my own work, and the second that MANUFACTURED a gap.

WHAT IS ACTUALLY MISSING, and it is sharper. R295's committed artifact carries SIX arms: four
labelled fitted, two labelled unfitted. A detector validated on 4 positives and 2 negatives has no
measurable operating characteristic -- no sensitivity, no specificity, no threshold with an error
rate attached. It was shown to FIRE on things known to leak. It was never shown not to fire on
things known not to, beyond n=2, and the arms it will be pointed at in future have unknown
provenance, which is the whole point of a clause-3 test.

SO THIS ROUND BUILDS THE POPULATION THE CALIBRATION NEEDS. Selection consumes only satisfaction that
is already judged -- "judged once so any k is free" -- so arms of KNOWN provenance can be
manufactured at a controlled LEAK DOSE without a single judge call:

    dose f = the fraction of this prompt's parity-1 annotators the selection is allowed to fit on.
    f = 0    a random draw: provenance clean by construction, the detector must NOT fire.
    f = 1    fitted on every parity-1 annotator: maximally leaky through the boundary.

That is a dose-response with its own g=0 cell, and the operating characteristic falls out of it.

⛔ THE ARITHMETIC TRAP, DECLARED. That a fitted arm scores higher than an unfitted one is FORCED --
it was selected to. The detector is not about the level, it is about the SHAPE: whether the
advantage concentrates where the two annotator halves agree. What is NOT forced and is measured: the
slope's dose-response, the SEPARATION between classes, and the dose at which separation begins.

ESTIMAND      (i) R295's slope statistic and its Q1 intercept, for arms of KNOWN provenance across
              a leak-dose grid; (ii) the operating characteristic -- the separation between the
              f=0 class and each f>0 class, in units of the across-seed spread; (iii) the smallest
              dose at which the classes stop overlapping.
IDENTIFICATION Exact for the manufactured arms: provenance is known because this round sets it.
              This is the one clause-3 question that IS identified here, and it is identified only
              because the arms are built rather than found. For arms found in the wild it remains
              unidentified, which is the register entry either way.
SCOPE         population 968 CoVal prompts with >=1 annotator in EACH parity · instrument
              Qwen3.5-2B-Base under R234's canonical builder · baseline the size-matched first-k
              subset of the blind pool · regime k=4, fit on parity 1, scored on parity 0.
WORLDS        W-DECIDABLE  the f=0 and f=1 slope distributions are disjoint by a wide margin, and
                           separation begins at a small dose -> provenance IS detectable from
                           artifacts, and clause 3 can carry a computed test with an error rate
                           instead of a provenance annotation.
              W-OVERLAP    the distributions overlap at every dose -> the detector cannot classify
                           an arm of unknown provenance, R295's verdicts were readable only because
                           it already knew the answers, and clause 3 stays an annotation. Register
                           entry, not a gap.
              W-COARSE     separation only at high dose -> the detector works but has a detection
                           limit, and the limit is the number clause 3 should carry.
KILL          pre-registered, conditional on the controls:
                f=1 class overlaps the f=0 class (min f=1 slope <= max f=0 slope)  -> W-OVERLAP
                else separation begins at f <= 0.25                                -> W-DECIDABLE
                else                                                               -> W-COARSE
POSITIVE CTRL reproduce R295's committed slope for BOTH of its unfitted arms, `coval_core` and
              `topw_k4`, to 1e-12 from this round's own pipeline. A statistic that is not R295's
              cannot calibrate R295's detector. AND IT FAILS AT g=0: the f=0 arms must land at the
              unfitted floor, not above it -- if a provably clean arm trips the detector, the
              specificity is zero and nothing else is readable.
NEGATIVE CTRL an arm fitted, genuinely and at f=1, on a DIFFERENT PROMPT's labels. The fit is real;
              the labels are the wrong ones. It must NOT fire, because clause 3 asks whether the
              core saw THIS conversation's labels, not whether it was fitted at all. This is the
              world where the detector responds to "was optimised" rather than "was optimised on
              this prompt", and it is built rather than argued.
PLACEBO       two independent f=0 arms: their slope difference must sit inside the across-seed
              spread.
NOISE FLOOR   the across-seed sd of the slope at each dose, which is what "separation" is measured
              in. Never a modelled variance.
MULTIPLICITY  |doses| x |seeds| arms x 2 signatures, every cell printed; the separation statement
              is over the whole grid.
SPECIFICATION the dose grid IS the curve, published whole including the doses where the classes
              overlap; both R295 signatures (slope AND Q1 intercept) are carried, because R295's own
              positive control failed on the slope and was rescued by the intercept.
SEEDS         3 per dose; all arms reported individually, never averaged into a class mean.
ARTIFACT      results/provenance_oc.json with source hash.
IMPOSSIBLE    - provenance for an arm this round did NOT build. The manufactured population
                calibrates the detector; it cannot certify an arm whose construction is unknown,
                because the mapping from construction to dose is what the release does not carry.
              - a second release, which is what would test whether the detection limit transfers.
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

SELF = pathlib.Path(__file__).resolve()
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
PAIRS = list(itertools.combinations(range(4), 2))
IIP = np.array([i for i, _ in PAIRS]); JJP = np.array([j for _, j in PAIRS])
K = 4
NSUB = 300                       # candidate subsets searched per prompt
DOSES = (0.0, 0.10, 0.25, 0.50, 0.75, 1.00)
SEEDS = (0, 1, 2)


def load_json(pat):
    d = next(A24.glob(pat), None)
    if d is None:
        return None
    f = sorted((d / "results").glob("*.json"))
    return json.loads(f[0].read_text()) if f else None


def main() -> int:
    r295 = load_json("R295_*")
    if r295 is None:
        print("  UNRUNNABLE: R295 absent."); return 2

    tg, _ = load_targets()
    FULL = load_sat(ROOT / "corebench" / "results" / "sat_full.npz")
    POOL = load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
    CORE = load_sat(ROOT / "corebench" / "results" / "sat_coval_core.npz")
    TOPW = load_sat(ROOT / "corebench" / "results" / "sat_topw_k4.npz")
    base = set(FULL) & set(POOL) & set(CORE) & set(TOPW)
    pids = sorted(p for p in base
                  if p in tg and len({i for i in range(len(tg[p])) if i % 2 == 0}) >= 1
                  and len({i for i in range(len(tg[p])) if i % 2 == 1}) >= 1
                  and len(tg[p]) >= 2)
    N = len(pids)
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    H1 = [h[1::2] for h in H]                     # parity 1 — the FIT half
    H0 = [h[0::2] for h in H]                     # parity 0 — the EVAL half
    RUB = [np.array([[FULL[p][(i, x)] for x in "ABCD"]
                     for i in sorted({i for i, _ in FULL[p]})], float) for p in pids]
    PL = [np.array([[POOL[p][(i, x)] for x in "ABCD"]
                    for i in sorted({i for i, _ in POOL[p]})], float) for p in pids]
    nrub = np.array([len(r) for r in RUB])
    npool = len(PL[0])

    # ---- the binning variable: how much do the two halves agree? (R295) --------------------------
    AGREE = np.array([float((H1[n][:, None, :] == H0[n][None, :, :]).mean()) for n in range(N)])
    print(f"  {N} prompts with both parities · half-agreement mean {AGREE.mean():.4f} · "
          f"rubric median {int(np.median(nrub))} · {NSUB} subsets searched per prompt\n")

    def a2_on(clsvec, n, half):
        v = np.asarray(clsvec, float)
        return float((v[None, :] == half[n]).mean())

    def cls_of(satmat, sel):
        Y = satmat[sel].sum(axis=0)
        return np.sign(Y[IIP] - Y[JJP])

    ref0 = np.array([a2_on(cls_of(PL[n], list(range(K))), n, H0) for n in range(N)])

    # ---- R295's statistic --------------------------------------------------------------------------
    def stat(margin):
        q = np.quantile(AGREE, [0.2, 0.4, 0.6, 0.8])
        b = np.digitize(AGREE, q)
        qs = [float(margin[b == i].mean()) for i in range(5)]
        x = (AGREE - AGREE.mean()) / AGREE.std()
        s = float(np.polyfit(x, margin, 1)[0])
        return qs, s

    # ---- POSITIVE CTRL · reproduce R295's committed slopes for its two unfitted arms --------------
    def arm_margin_from_npz(SAT):
        v = np.array([a2_on(cls(yvec(SAT[pids[n]], sorted({i for i, _ in SAT[pids[n]]}))), n, H0)
                      for n in range(N)])
        return v - ref0
    dev = {}
    for name, SAT in (("coval_core", CORE), ("topw_k4", TOPW)):
        _, s = stat(arm_margin_from_npz(SAT))
        dev[name] = abs(s - r295["arms"][name]["slope"])
    pos_ok = max(dev.values()) < 1e-12
    print("  POSITIVE CTRL  reproduce R295's committed slope for its two UNFITTED arms")
    for name in ("coval_core", "topw_k4"):
        _, s = stat(arm_margin_from_npz(CORE if name == "coval_core" else TOPW))
        print(f"    {name:<14}{s:+.12f}  vs R295 {r295['arms'][name]['slope']:+.12f}   "
              f"{'PASS' if dev[name] < 1e-12 else f'FAIL by {dev[name]:.2e}'}")
    FLOOR = max(r295["arms"]["coval_core"]["slope"], r295["arms"]["topw_k4"]["slope"])

    # ---- build an arm at a controlled LEAK DOSE ---------------------------------------------------
    def build(dose, seed, wrong_prompt=False):
        rng = np.random.default_rng(120_000 + 7919 * seed + int(dose * 1000))
        margin = np.empty(N)
        for n in range(N):
            sels = np.stack([rng.choice(nrub[n], K, replace=False) for _ in range(NSUB)])
            Y = RUB[n][sels].sum(axis=1)
            C = np.sign(Y[:, IIP] - Y[:, JJP])                 # (NSUB, 6)
            if dose <= 0.0:
                pick = int(rng.integers(NSUB))                 # no fit at all
            else:
                src = H1[(n + N // 2) % N] if wrong_prompt else H1[n]
                take = max(1, int(round(dose * len(src))))
                fit = src[rng.choice(len(src), take, replace=False)]
                sc = (C[:, None, :] == fit[None, :, :]).mean(axis=(1, 2))
                pick = int(np.argmax(sc))
            margin[n] = a2_on(C[pick], n, H0) - ref0[n]
        return margin

    print(f"\n  LEAK DOSE-RESPONSE — arms of KNOWN provenance, fit on parity 1, scored on parity 0\n")
    print(f"    {'dose':>6}{'seed':>6}{'Q1':>10}{'Q5':>10}{'slope':>10}{'excess':>10}  fires?")
    ARMS, rows = {}, []
    for f_ in DOSES:
        for s_ in SEEDS:
            m = build(f_, s_)
            qs, sl = stat(m)
            ex = sl - FLOOR
            fires = ex > 0.0
            ARMS[(f_, s_)] = dict(q1=qs[0], q5=qs[-1], slope=sl, excess=ex, fires=bool(fires))
            rows.append((f_, s_, sl, qs[0], ex, fires))
            print(f"    {f_:>6.2f}{s_:>6}{qs[0]:>10.4f}{qs[-1]:>10.4f}{sl:>10.4f}{ex:>+10.4f}"
                  f"  {'YES' if fires else 'no'}")

    def cls_slopes(f_):
        return np.array([ARMS[(f_, s_)]["slope"] for s_ in SEEDS])

    # ⚠ THE CLEAN CLASS MUST INCLUDE A QUALITY-MATCHED MEMBER, or the separation is confounded.
    # My f=0 arms are RANDOM draws and sit at slope ~-0.020, far below R295's real unfitted arms
    # (coval_core +0.00855, topw_k4 +0.00458). Fitted arms are better AND fitted, so "fitted vs
    # random" cannot separate provenance from quality. The clean boundary is therefore the MAXIMUM
    # over the manufactured f=0 arms AND the two high-quality unfitted arms the campaign already
    # has -- which is coval_core, an arm as good as anything admitted.
    clean_real = {name: r295["arms"][name]["slope"] for name in ("coval_core", "topw_k4")}
    s0 = np.concatenate([cls_slopes(0.0), np.array(list(clean_real.values()))])
    print(f"\n  THE CLEAN CLASS  manufactured f=0 arms {[round(float(x),4) for x in cls_slopes(0.0)]}")
    print(f"                   + REAL high-quality unfitted arms "
          f"{ {k: round(v,5) for k, v in clean_real.items()} }")
    print(f"    -> the boundary is max(clean) = {s0.max():+.4f} (coval_core), not the random floor,")
    print(f"       because a fitted arm is better AND fitted and `fitted vs random` would confound")
    print(f"       provenance with quality.")
    sd0 = float(cls_slopes(0.0).std(ddof=1))   # the noise unit stays the seed spread
    print(f"\n  NOISE FLOOR  across-seed sd of the slope at f=0: {sd0:.5f}  "
          f"(the unit `separation` is measured in)")

    # ---- POSITIVE at g=0 -----------------------------------------------------------------------------
    g0_ok = all(not ARMS[(0.0, s_)]["fires"] for s_ in SEEDS)
    print(f"  POSITIVE @ g=0  the {len(SEEDS)} provably-clean f=0 arms must NOT fire: "
          f"{[ARMS[(0.0, s_)]['fires'] for s_ in SEEDS]}  "
          f"{'PASS' if g0_ok else 'FAIL — specificity is zero and nothing else is readable'}")

    # ---- NEGATIVE · a real fit on the WRONG prompt's labels ------------------------------------------
    wrong = [stat(build(1.0, s_, wrong_prompt=True))[1] for s_ in SEEDS]
    wrong_fires = [w - FLOOR > 0.0 for w in wrong]
    neg_ok = not any(wrong_fires)
    print(f"  NEGATIVE CTRL  f=1 fitted on a DIFFERENT prompt's labels — a real fit, wrong labels:")
    print(f"    slopes {[round(w,4) for w in wrong]}   fires {wrong_fires}   "
          f"{'PASS — the detector responds to THIS prompt, not to being optimised' if neg_ok else 'FAIL — it fires on any fitted arm'}")

    # ---- PLACEBO ---------------------------------------------------------------------------------------
    plc = abs(ARMS[(0.0, 0)]["slope"] - ARMS[(0.0, 1)]["slope"])
    plc_ok = plc <= 3 * max(sd0, 1e-9)
    print(f"  PLACEBO        two independent f=0 arms differ by {plc:.5f} vs 3sd {3*sd0:.5f}  "
          f"{'PASS' if plc_ok else 'FAIL'}")

    # ---- the operating characteristic ------------------------------------------------------------------
    print(f"\n  OPERATING CHARACTERISTIC — separation from the f=0 class, in across-seed sd\n")
    print(f"    {'dose':>6}{'min slope':>11}{'max f=0':>10}{'disjoint?':>11}{'separation':>12}")
    sep, first_sep = {}, None
    for f_ in DOSES[1:]:
        sf = cls_slopes(f_)
        disjoint = bool(sf.min() > s0.max())
        d = (sf.mean() - s0.mean()) / max(sd0, 1e-9)
        sep[f_] = dict(disjoint=disjoint, separation_sd=float(d),
                       min=float(sf.min()), max_f0=float(s0.max()))
        if disjoint and first_sep is None:
            first_sep = f_
        print(f"    {f_:>6.2f}{sf.min():>11.4f}{s0.max():>10.4f}{str(disjoint):>11}{d:>12.1f}")

    ctrl = pos_ok and g0_ok and neg_ok and plc_ok
    top_disjoint = sep[DOSES[-1]]["disjoint"]
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  positive={pos_ok}  g0={g0_ok}  negative={neg_ok}  placebo={plc_ok}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the operating characteristic is not readable.")
    elif not top_disjoint:
        world = "W-OVERLAP"
        print(f"  -> W-OVERLAP. Even at f=1.00 the fitted class overlaps the clean class "
              f"(min {sep[DOSES[-1]]['min']:.4f} vs max f=0 {s0.max():.4f}).")
        print("     The detector cannot classify an arm of unknown provenance. R295's verdicts were")
        print("     readable only because it already knew the answers, and clause 3 stays an")
        print("     annotation. That is a REGISTER ENTRY, not a gap to be closed by more work here.")
    elif first_sep is not None and first_sep <= 0.25:
        world = "W-DECIDABLE"
        print(f"  -> W-DECIDABLE. The classes separate from f={first_sep:.2f} upward, at "
              f"{sep[first_sep]['separation_sd']:.1f} across-seed sd, and the clean arms never fire.")
        print("     Provenance IS detectable from artifacts at this site, so clause 3 can carry a")
        print("     computed test with a stated detection limit instead of a provenance annotation.")
    else:
        world = "W-COARSE"
        print(f"  -> W-COARSE. Separation begins only at f={first_sep}, so the detector works and")
        print(f"     has a DETECTION LIMIT: leakage below that dose is invisible to it. That limit")
        print("     is the number clause 3 should carry, and it is not currently on the page.")
    print("  " + "=" * 78)
    print(f"\n  ⚠ AND R295's CLASS SIZES ARE THE POINT: its committed artifact has "
          f"{sum(1 for v in r295['arms'].values() if v['fitted'])} fitted and "
          f"{sum(1 for v in r295['arms'].values() if not v['fitted'])} unfitted arms.")
    print(f"    A detector VALIDATED on 4 positives and 2 negatives has no operating characteristic.")
    print(f"    This round manufactures {len(DOSES)*len(SEEDS)} arms of known provenance to give it one.")
    print(f"\n  MULTIPLICITY  {len(DOSES)}x{len(SEEDS)} arms x 2 signatures, every cell printed.")

    o = SELF.parent / "results" / "provenance_oc.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_prompts=N, nsub=NSUB, doses=list(DOSES), seeds=list(SEEDS), floor=FLOOR,
        arms={f"{f_}|{s_}": ARMS[(f_, s_)] for (f_, s_) in ARMS},
        separation={str(k): v for k, v in sep.items()}, first_separating_dose=first_sep,
        noise_floor_sd=sd0, wrong_prompt_slopes=wrong,
        clean_real=clean_real, clean_boundary=float(s0.max()),
        r295_class_sizes=dict(fitted=sum(1 for v in r295["arms"].values() if v["fitted"]),
                              unfitted=sum(1 for v in r295["arms"].values() if not v["fitted"])),
        controls=dict(positive=bool(pos_ok), g0=bool(g0_ok), negative=bool(neg_ok),
                      placebo=bool(plc_ok)),
        corrects="R334's next-gradient line said clause 3 has no instrument; R295 built one.",
    ), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
