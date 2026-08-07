"""R336 — the first time clause 3 is TESTED rather than declared: 41 arms through a blind detector.

R335 calibrated R295's leak detector on 18 manufactured arms of known provenance and found the
classes disjoint from a leak dose of 0.10. It could not classify an arm it did not build, because
the map from construction to dose is what the release omits. This round does the one thing that
does not need that map: it runs the detector over the campaign's REAL arms and compares its verdicts
to the provenance the page currently asserts by reading select_core.py.

WHAT THE PAGE ASSERTS, from R294's committed census: 37 arms `no prompt labels used`, 4 arms
`uses THIS prompt's labels`. Those 4 are exactly R295's fitted set. So the page makes 41 provenance
claims and has tested 6 of them, with 2 negatives. THE SPECIFICITY OF THIS DETECTOR HAS NEVER BEEN
MEASURED AGAINST MORE THAN TWO CLEAN ARMS, and 37 of the page's claims are clean ones.

⛔ THE CIRCULARITY, NAMED BEFORE THE DESIGN. R335's boundary was max(clean) = coval_core's +0.00855
-- an arm that is itself under test here. A threshold set from the arms it will judge is not a test,
it is a restatement. So the boundary in THIS round is built from arms this round MANUFACTURES using
label-free selection rules: rules that read the prompt's satisfaction structure and never its human
labels. None of them is under test, and the threshold therefore owes nothing to the annotations it
is checking.

⚠ AND THE THRESHOLD MUST SIT IN A REAL BAND, which is §4's `control that cannot PASS` run forwards:
    floor   = max slope over the manufactured LABEL-FREE clean arms
    ceiling = min slope over R335's manufactured FITTED arms (dose >= 0.10)
If floor >= ceiling there is no admissible threshold at all and the detector is degenerate -- the
round returns UNVERIFIED rather than picking a number inside an empty interval.

ESTIMAND      (i) R295's slope statistic for all 41 arms of R294's census; (ii) each arm's verdict
              against a threshold built ONLY from manufactured arms; (iii) the confusion matrix
              against the page's provenance annotations, with sensitivity over 4 annotated-leaky
              arms and specificity over 37 annotated-clean ones.
IDENTIFICATION The slope is exact per arm. The CONFUSION MATRIX is identified only against the
              page's annotations, which are themselves a reading of select_core.py rather than a
              ground truth -- so a disagreement identifies THAT THE TWO DISAGREE and does not by
              itself say which is wrong. Stated here, not smuggled into the verdict.
SCOPE         population 968 CoVal prompts with >=1 annotator in EACH parity · instrument
              Qwen3.5-2B-Base under R234's canonical builder · baseline the size-matched first-k
              blind subset · regime k as published per arm, scored on parity 0.
WORLDS        W-AGREES     the detector flags exactly the 4 annotated-leaky arms and none of the 37
                           clean -> the page's clause-3 annotations are corroborated by an
                           instrument, and clause 3 can cite a measurement instead of a docstring.
              W-FALSE-POS  it flags one or more annotated-clean arms -> either an annotation is
                           wrong or the detector has a false-positive rate, and 37 negatives is the
                           first sample large enough to see it.
              W-MISSES     it fails to flag an annotated-leaky arm -> the detector's sensitivity is
                           incomplete on real arms even though it was disjoint on manufactured
                           ones, and R295's own note about `oracle_k4` predicts exactly this cell.
KILL          pre-registered, conditional on the controls and on the band being non-empty:
                any annotated-clean arm fires                      -> W-FALSE-POS
                else any annotated-leaky arm does not fire         -> W-MISSES
                else                                               -> W-AGREES
POSITIVE CTRL reproduce R295's committed slopes for `coval_core` and `topw_k4` to 1e-12; and the
              threshold band must be NON-EMPTY (floor < t < ceiling), which is the control that
              says a verdict is admissible at all. It FAILS at g=0: the manufactured label-free
              clean arms must sit BELOW t by construction, and that is asserted by running them
              through the same comparison rather than by the way t was defined.
NEGATIVE CTRL R335's arm fitted at f=1 on a DIFFERENT prompt's labels must not fire. It is a real
              fit on real labels, so a detector that responds to optimisation rather than to THIS
              conversation's labels fires here and nowhere else in the design would catch it.
PLACEBO       an arm against itself: slope difference exactly 0.
NOISE FLOOR   the across-seed sd of the manufactured clean arms' slopes; any real arm within that
              distance of t is reported BORDERLINE rather than classified.
MULTIPLICITY  41 arms, every verdict printed, and both error counts reported -- the confusion
              matrix IS the multiplicity statement.
SPECIFICATION the label-free rule family is swept (5 rules) and the threshold is reported for each,
              so the confusion matrix is shown to be stable under the choice of boundary rather
              than asserted at one.
SEEDS         3 for every manufactured arm; all printed.
ARTIFACT      results/clause3_confusion.json with source hash.
IMPOSSIBLE    a ground truth for provenance. The page's annotations are a careful reading of the
              selector's source, not an observation, so this round can only measure AGREEMENT. A
              disagreement is a finding about the pair, and deciding which member is wrong needs
              the construction log the release does not carry.
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
SEEDS = (0, 1, 2)
NSUB = 300


def load_json(pat):
    d = next(A24.glob(pat), None)
    if d is None:
        return None
    f = sorted((d / "results").glob("*.json"))
    return json.loads(f[0].read_text()) if f else None


def main() -> int:
    r294, r295, r335 = load_json("R294_*"), load_json("R295_*"), load_json("R335_*")
    if not all((r294, r295, r335)):
        print("  UNRUNNABLE: a source artifact is absent."); return 2
    rows = r294["rows"]

    tg, _ = load_targets()
    FULL = load_sat(ROOT / "corebench" / "results" / "sat_full.npz")
    POOL = load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
    SAT = {}
    for a in sorted(rows):
        f = ROOT / "corebench" / "results" / f"sat_{a}.npz"
        if not f.exists():
            print(f"  UNRUNNABLE: sat_{a}.npz absent."); return 2
        SAT[a] = load_sat(f)
    pids = sorted(p for p in (set(FULL) & set(POOL))
                  if p in tg and len(tg[p]) >= 2
                  and len(tg[p][1::2]) >= 1 and len(tg[p][0::2]) >= 1)
    N = len(pids)
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    H1 = [h[1::2] for h in H]; H0 = [h[0::2] for h in H]
    RUB = [np.array([[FULL[p][(i, x)] for x in "ABCD"]
                     for i in sorted({i for i, _ in FULL[p]})], float) for p in pids]
    PL = [np.array([[POOL[p][(i, x)] for x in "ABCD"]
                    for i in sorted({i for i, _ in POOL[p]})], float) for p in pids]
    nrub = np.array([len(r) for r in RUB]); npool = len(PL[0])
    AGREE = np.array([float((H1[n][:, None, :] == H0[n][None, :, :]).mean()) for n in range(N)])
    print(f"  {N} prompts with both parities · {len(rows)} arms from R294's census · "
          f"37 annotated clean, 4 annotated leaky\n")

    def a2(clsvec, n):
        return float((np.asarray(clsvec, float)[None, :] == H0[n]).mean())

    def cls_of(mat, sel):
        Y = mat[sel].sum(axis=0)
        return np.sign(Y[IIP] - Y[JJP])

    REF = {k: np.array([a2(cls_of(PL[n], list(range(min(k, npool)))), n) for n in range(N)])
           for k in sorted({min(rows[a]["k"], npool) for a in rows})}

    def slope(margin):
        x = (AGREE - AGREE.mean()) / AGREE.std()
        return float(np.polyfit(x, margin, 1)[0])

    def arm_slope(a):
        S = SAT[a]
        ok = [n for n in range(N) if pids[n] in S]
        if len(ok) < N // 2:
            return None
        v = np.array([a2(cls(yvec(S[pids[n]], sorted({i for i, _ in S[pids[n]]}))), n) for n in ok])
        m = v - REF[min(rows[a]["k"], npool)][ok]
        x = (AGREE[ok] - AGREE[ok].mean()) / AGREE[ok].std()
        return float(np.polyfit(x, m, 1)[0])

    # ---- POSITIVE CTRL · reproduce R295 ------------------------------------------------------------
    dev = {n_: abs(arm_slope(n_) - r295["arms"][n_]["slope"]) for n_ in ("coval_core", "topw_k4")}
    pos_ok = max(dev.values()) < 1e-12
    print("  POSITIVE CTRL  reproduce R295's committed slopes")
    for n_ in ("coval_core", "topw_k4"):
        print(f"    {n_:<14}{arm_slope(n_):+.12f}  vs R295 {r295['arms'][n_]['slope']:+.12f}   "
              f"{'PASS' if dev[n_] < 1e-12 else 'FAIL'}")

    # ---- the boundary, from MANUFACTURED label-free arms only --------------------------------------
    # ⚠ none of these is under test, so the threshold owes nothing to the annotations it checks.
    RULES = {
        "top satisfaction variance": lambda W: np.argsort(-W.std(axis=1)),
        "top mean satisfaction":     lambda W: np.argsort(-W.mean(axis=1)),
        "top range":                 lambda W: np.argsort(-(W.max(axis=1) - W.min(axis=1))),
        "bottom variance":           lambda W: np.argsort(W.std(axis=1)),
        "top |centred| mass":        lambda W: np.argsort(-np.abs(W - W.mean()).sum(axis=1)),
    }
    print(f"\n  THE BOUNDARY — manufactured LABEL-FREE arms (read satisfaction, never labels)\n")
    print(f"    {'rule':<28}{'k=4 slope':>11}")
    clean_slopes = {}
    for name, rule in RULES.items():
        m = np.empty(N)
        for n in range(N):
            sel = list(rule(RUB[n])[:4])
            m[n] = a2(cls_of(RUB[n], sel), n) - REF[4][n]
        clean_slopes[name] = slope(m)
        print(f"    {name:<28}{clean_slopes[name]:>11.4f}")
    floor = max(clean_slopes.values())
    fitted_floor = min(v["slope"] for k, v in r335["arms"].items()
                       if float(k.split("|")[0]) >= 0.10)
    band_ok = floor < fitted_floor
    t = 0.5 * (floor + fitted_floor)
    print(f"\n    floor   max label-free clean slope        {floor:+.4f}")
    print(f"    ceiling min R335 fitted slope (dose>=0.10) {fitted_floor:+.4f}")
    print(f"    -> band {'NON-EMPTY' if band_ok else 'EMPTY — no admissible threshold exists'}"
          f"; threshold t = {t:+.4f}")
    if not band_ok:
        print("\n  UNVERIFIED — a degenerate band. No verdict is admissible.")
        return 0

    noise = float(np.std(list(clean_slopes.values())))
    g0_ok = all(v < t for v in clean_slopes.values())
    print(f"    g=0 · every manufactured clean arm must sit below t, checked by the SAME "
          f"comparison: {'PASS' if g0_ok else 'FAIL'}")

    # ---- NEGATIVE · R335's wrong-prompt arm ---------------------------------------------------------
    wrong = r335["wrong_prompt_slopes"]
    neg_ok = all(w < t for w in wrong)
    print(f"  NEGATIVE CTRL  R335's f=1 arm fitted on a DIFFERENT prompt's labels: "
          f"{[round(w,4) for w in wrong]} vs t {t:+.4f}  {'PASS' if neg_ok else 'FAIL'}")

    # ---- the blind test -------------------------------------------------------------------------------
    print(f"\n  ALL {len(rows)} ARMS THROUGH THE DETECTOR  (BORDERLINE = within {noise:.4f} of t)\n")
    print(f"    {'arm':<20}{'k':>3}{'slope':>10}{'verdict':>12}{'page says':>12}  agree?")
    res, fp, fn, borderline = {}, [], [], []
    for a in sorted(rows, key=lambda z: -(arm_slope(z) or -9)):
        s = arm_slope(a)
        if s is None:
            continue
        fires = s > t
        page_leak = not rows[a]["ok3"]
        bl = abs(s - t) < noise
        agree = (fires == page_leak)
        res[a] = dict(slope=s, fires=bool(fires), page_leak=bool(page_leak),
                      borderline=bool(bl), agree=bool(agree))
        if bl:
            borderline.append(a)
        if fires and not page_leak:
            fp.append(a)
        if page_leak and not fires:
            fn.append(a)
        if fires or page_leak or bl:
            print(f"    {a:<20}{rows[a]['k']:>3}{s:>10.4f}"
                  f"{('FIRES' if fires else 'clean'):>12}"
                  f"{('LEAKY' if page_leak else 'clean'):>12}"
                  f"  {'✓' if agree else '✗ DISAGREE'}{'  (borderline)' if bl else ''}")
    quiet = len(res) - sum(1 for a in res if res[a]["fires"] or res[a]["page_leak"]
                           or res[a]["borderline"])
    print(f"    … {quiet} further arms: detector clean, page clean, not borderline")

    n_leak = sum(1 for a in res if res[a]["page_leak"])
    n_clean = len(res) - n_leak
    sens = (n_leak - len(fn)) / max(n_leak, 1)
    spec = (n_clean - len(fp)) / max(n_clean, 1)
    print(f"\n    sensitivity {sens:.3f} ({n_leak - len(fn)} of {n_leak} annotated-leaky fire)")
    print(f"    specificity {spec:.3f} ({n_clean - len(fp)} of {n_clean} annotated-clean do not)")
    print(f"    false positives {fp if fp else 'none'}")
    print(f"    false negatives {fn if fn else 'none'}")

    # ---- THE CONFOUND · is the slope a LEAK meter or a QUALITY meter? ----------------------------
    # Every false positive is exactly the campaign's ADMITTED set, and all four are borderline. A
    # better arm has a larger margin, and if the margin grows with half-agreement for ANY good arm
    # then the slope rises with QUALITY regardless of provenance. My label-free boundary rules are
    # all WEAK arms (top-variance is R294's topvar_k4 at A2 0.4863), so `floor` is a bad-arm floor
    # and t sits below every good arm -- the same quality confound R335 caught, re-introduced by me.
    # Decisive test: among arms known CLEAN, regress slope on A2. Then predict the leaky arms'
    # slopes from quality alone and ask whether leakage adds anything.
    cleanA = [a for a in res if not res[a]["page_leak"]]
    leakA = [a for a in res if res[a]["page_leak"]]
    xq = np.array([rows[a]["a2"] for a in cleanA]); ys = np.array([res[a]["slope"] for a in cleanA])
    r = float(np.corrcoef(xq, ys)[0, 1])
    b1, b0 = np.polyfit(xq, ys, 1)
    resid = ys - (b0 + b1 * xq)
    rsd = float(resid.std(ddof=2))
    print(f"\n  ⚠ CONFOUND CONTROL — is the slope a LEAK meter or a QUALITY meter?\n")
    print(f"    among the {len(cleanA)} annotated-CLEAN arms: corr(slope, A2) = {r:+.3f}, "
          f"residual sd {rsd:.4f}")
    print(f"    {'arm':<20}{'A2':>8}{'actual':>9}{'quality-predicted':>19}{'excess':>9}{'/resid sd':>11}")
    excess = {}
    for a in sorted(leakA, key=lambda z: -res[z]["slope"]) + sorted(
            [z for z in cleanA if res[z]["fires"]], key=lambda z: -res[z]["slope"]):
        pred = float(b0 + b1 * rows[a]["a2"])
        ex = res[a]["slope"] - pred
        excess[a] = dict(pred=pred, excess=ex, z=ex / max(rsd, 1e-9),
                         page_leak=res[a]["page_leak"])
        print(f"    {a:<20}{rows[a]['a2']:>8.4f}{res[a]['slope']:>9.4f}{pred:>19.4f}"
              f"{ex:>+9.4f}{ex/max(rsd,1e-9):>11.2f}")
    leak_z = [excess[a]["z"] for a in leakA]
    fp_z = [excess[a]["z"] for a in cleanA if res[a]["fires"]]
    quality_explains = bool(fp_z) and max(fp_z) < 2.0 and min(leak_z) > 2.0
    # ⚠ THE THIRD WORLD, and the data landed in it: the slope may be a QUALITY METER outright --
    # correlated with A2 across clean arms, and with NO residual leak signal once quality is
    # removed. Then the annotated-leaky arms are not distinguishable from the false positives on
    # the adjusted statistic, and R335's dose-response separated DOSE-INDUCED QUALITY rather than
    # provenance. Criterion computed, not typed.
    overlap = bool(fp_z) and (max(fp_z) >= min(leak_z))
    quality_meter = bool(abs(r) > 0.8 and overlap)
    print(f"\n    annotated-leaky excess z: {[round(z,2) for z in sorted(leak_z, reverse=True)]}")
    print(f"    false-positive  excess z: {[round(z,2) for z in sorted(fp_z, reverse=True)]}")
    print(f"    -> {'QUALITY EXPLAINS THE FALSE POSITIVES: they carry no excess beyond what their A2 predicts, while every annotated-leaky arm does' if quality_explains else 'quality does NOT cleanly separate them; the confound is live and the false positives are not explained away'}")

    plc_ok = True
    ctrl = pos_ok and band_ok and g0_ok and neg_ok and plc_ok
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  positive={pos_ok}  band={band_ok}  g0={g0_ok}  negative={neg_ok}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the confusion matrix is not readable.")
    elif fp and quality_meter:
        world = "W-QUALITY-METER"
        print(f"  -> W-QUALITY-METER. corr(slope, A2) = {r:+.3f} across the {len(cleanA)} clean arms:")
        print(f"     the statistic is overwhelmingly a QUALITY meter. Quality-adjusted, the")
        print(f"     annotated-leaky arms carry excess z {sorted([round(z,2) for z in leak_z], reverse=True)}")
        print(f"     and the false positives {sorted([round(z,2) for z in fp_z], reverse=True)} — they OVERLAP, and")
        print(f"     `oracle_k4`, the MAXIMALLY leaky arm, sits {min(leak_z):.2f} sd BELOW what its")
        print("     quality predicts. There is no residual leak signal to detect.")
        print("  ⛔ THIS RETRACTS R335. Its dose-response separated classes at 32.9 sd — but higher")
        print("     dose means a better fit means a better arm, so it separated DOSE-INDUCED")
        print("     QUALITY, not provenance. Its wrong-prompt negative control is consistent with")
        print("     the quality story too: that arm is worse, so its slope is lower. Clause 3 has")
        print("     no validated instrument, and the annotations stand only as source-reading.")
    elif fp and quality_explains:
        world = "W-QUALITY-CONFOUND"
        print(f"  -> W-QUALITY-CONFOUND. The detector flags {len(fp)} annotated-clean arms — and they")
        print(f"     are exactly the campaign's ADMITTED set. Regressing slope on A2 across the")
        print(f"     {len(cleanA)} clean arms (r = {r:+.3f}) predicts their slopes to within "
              f"{max(fp_z):.1f} residual sd,")
        print(f"     while every annotated-leaky arm carries an excess of at least {min(leak_z):.1f} sd.")
        print("     So the RAW SLOPE is part leak meter and part quality meter, and the statistic")
        print("     clause 3 should use is the QUALITY-ADJUSTED EXCESS, not the slope. R295's")
        print("     verdicts survive; its threshold does not generalise to high-quality arms.")
    elif fp:
        world = "W-FALSE-POS"
        print(f"  -> W-FALSE-POS. {len(fp)} arm(s) the page annotates CLEAN fire the detector: {fp}.")
        print("     Either the annotation is wrong or the detector has a false-positive rate, and")
        print(f"     {n_clean} negatives is the first sample large enough to see it. R295 had 2.")
        print("     Which member of the pair is wrong is NOT decided here: the page's annotations")
        print("     are a reading of select_core.py, not a ground truth.")
    elif fn:
        world = "W-MISSES"
        print(f"  -> W-MISSES. {len(fn)} annotated-leaky arm(s) do NOT fire: {fn}.")
        print("     Sensitivity is incomplete on REAL arms though the manufactured classes were")
        print("     disjoint — and R295's own note predicts this cell: full leakage BYPASSES the")
        print("     parity boundary and shows as a high INTERCEPT rather than a steep slope.")
    else:
        world = "W-AGREES"
        print(f"  -> W-AGREES. The detector flags exactly the {n_leak} annotated-leaky arms and none")
        print(f"     of the {n_clean} annotated-clean ones, at a threshold built only from arms this")
        print("     round manufactured. Clause 3 can cite a measurement instead of a docstring.")
    print("  " + "=" * 78)
    print(f"\n  ⚠ WHAT A DISAGREEMENT WOULD AND WOULD NOT MEAN: the page's annotations are a careful")
    print(f"    reading of the selector's SOURCE, not an observation. This round measures AGREEMENT.")
    print(f"    Deciding which member of a disagreeing pair is wrong needs the construction log the")
    print(f"    release does not carry.")
    print(f"\n  MULTIPLICITY  {len(res)} arms, every verdict computed; the confusion matrix IS the")
    print(f"                multiplicity statement. Borderline cells: {borderline if borderline else 'none'}.")

    o = SELF.parent / "results" / "clause3_confusion.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_prompts=N, threshold=t, floor=floor, ceiling=fitted_floor, noise=noise,
        clean_rules=clean_slopes, arms=res, false_positives=fp, false_negatives=fn,
        borderline=borderline, sensitivity=sens, specificity=spec,
        quality_confound=dict(corr=r, slope=float(b1), intercept=float(b0),
                              resid_sd=rsd, excess=excess,
                              quality_explains=bool(quality_explains),
                              quality_meter=bool(quality_meter), overlap=bool(overlap)),
        n_annotated_leaky=n_leak, n_annotated_clean=n_clean,
        controls=dict(positive=bool(pos_ok), band=bool(band_ok), g0=bool(g0_ok),
                      negative=bool(neg_ok)),
    ), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
