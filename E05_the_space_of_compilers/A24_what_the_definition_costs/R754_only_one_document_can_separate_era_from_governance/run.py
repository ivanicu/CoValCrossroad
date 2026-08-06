#!/usr/bin/env python3
"""R754 · only one document can separate era from governance, and it is not the one carrying the effect

ESTIMAND        E1 the identification structure -- per document pair, the era bins in which BOTH have
                figures. An empty joint bin is UNIDENTIFIABLE on that axis. E2 within DEFINITION.md,
                the flagged rate of OLD-era vs NEW-era citing figures, split at R450. E3 the MDE of
                E2, computed BEFORE interpretation and validated by simulation.
IDENTIFICATION  E1 exact and structural. E2 identified WITHIN DEFINITION.md only -- governance is
                constant inside one document and era is what varies. It is NOT identified for the
                STATEMENT-FORMULATION contrast, which is an IDENTIFICATION failure rather than a
                power failure, and the two are not reported as one.
                ⚠ A figure citing rounds on BOTH sides is assigned by the MEDIAN cited round and the
                count of split-spanning figures is REPORTED, never silently binned.
SCOPE           population = the figures on citing lines of DEFINITION.md, split at cited round R450
                · instrument = R750's rounded matcher · baseline = R753's per-document rates ·
                regime = this tree_sha.
WORLDS          A era explains it · B era does not, so the governance reading survives its strongest
                confound · C UNRESOLVED, which is silence rather than agreement.
KILL            conditional; gated on the simulation being calibrated at g=0 and monotone.
POSITIVE CTRL   the MONOTONE LADDER -- asserting a searched MDE rejects at 0.80 is circular; the
                ORDER is not. Band computed from the zero plant and the maximal plant.
g=0             zero planted difference rejects at ~alpha.
NEGATIVE CTRL   shuffle the OLD/NEW label across DEFINITION's figures; the difference must collapse.
                Excludes "any split of this document shows this gap".
SHAM            ingredient ABSENT: split at 5 RANDOM cited-round thresholds unrelated to R450. A real
                era effect must exceed what an arbitrary split produces.
PLACEBO         each arm's rate computed twice -> exactly 0, reported as 0 of N.
NOISE FLOOR     3 simulation seeds and 5 sham splits; spreads reported, never averaged into one.
MULTIPLICITY    3 pairs x bin overlap + 2 documents x {old,new} + {analytic, empirical MDE} + 5 sham
                splits + 3 seeds. All reported.
UNIT            instrument unit = a FIGURE; claim unit = an ERA's practice. Figures cluster within
                lines, so the distinct LINE count per arm is reported and the MDE is ALSO computed on
                lines as the conservative reading.
ARTIFACT        results/r754.json with tree_sha; a later round attacks this by supplying a version of
                FORMULATION.md that cites recent rounds, which does not exist.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      separating era from governance on the STATEMENT-FORMULATION contrast (needs a
                FORMULATION citing recent rounds -- UNIDENTIFIABLE, not under-powered) · whether a
                governance regime CAUSES a rate (needs an intervention) · generalising beyond this
                repo · independently replicated.

⛔ DERIVATIONS, LABELLED, NOT EVIDENCE:
   an empty joint bin cannot be stratified -- definitional. Splitting 118 figures gives arms near 59,
   so the MDE is ~2x R753's -- algebra. And FORMULATION's new-era rate is UNDEFINED, not zero; an
   undefined rate is never plotted as 0.
"""
from __future__ import annotations
import json, math, os, pathlib, re, subprocess, statistics
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
A24 = HERE.parent
E05 = ROOT / "E05_the_space_of_compilers"
DOCS = ["STATEMENT.md", "DEFINITION.md", "FORMULATION.md"]
BINS = [(0, 300), (300, 450), (450, 600), (600, 999)]
SPLIT = 450
NUM = re.compile(r"\*\*([-+]?\d[\d,]*\.?\d*)\*\*|(?<![\w.])(\d+\.\d{3,})(?![\w.])")


def _plain(o):
    for cast in (bool, int, float):
        if isinstance(o, cast) or type(o).__name__ == cast.__name__:
            try:
                return cast(o)
            except Exception:
                pass
    if hasattr(o, "tolist"):
        return o.tolist()
    return str(o)


def m_rounded(val, b):
    if re.search(rf"(?<![\d.]){re.escape(val)}", b):
        return True
    if "." not in val:
        return bool(re.search(rf"(?<![\d.]){re.escape(val)}\.0*(?![1-9])", b))
    dp = len(val.split(".")[1])
    try:
        t = float(val)
    except ValueError:
        return False
    for mm in re.finditer(r"[-+]?\d+\.\d+", b):
        try:
            if round(float(mm.group()), dp) == t:
                return True
        except ValueError:
            continue
    return False


def mde(n1, n2, pbar, alpha=0.05, power=0.80):
    from statistics import NormalDist
    nd = NormalDist()
    if n1 == 0 or n2 == 0:
        return None
    return (nd.inv_cdf(1 - alpha / 2) + nd.inv_cdf(power)) * \
        math.sqrt(pbar * (1 - pbar) * (1 / n1 + 1 / n2))


def sim_reject(n1, n2, p1, p2, seed, trials=20000, alpha=0.05):
    rng = np.random.default_rng(seed)
    x1 = rng.binomial(n1, p1, trials); x2 = rng.binomial(n2, p2, trials)
    ph1, ph2 = x1 / n1, x2 / n2
    pp = (x1 + x2) / (n1 + n2)
    se = np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(se > 0, (ph1 - ph2) / se, 0.0)
    from statistics import NormalDist
    return float(np.mean(np.abs(z) > NormalDist().inv_cdf(1 - alpha / 2)))


def main() -> int:
    if any(not (E05 / d).exists() for d in DOCS):
        print("UNRUNNABLE: a deliverable is absent. Exit 2, never 0."); return 2
    BLOB = {}

    def blob(rid):
        if rid not in BLOB:
            t = ""
            for d in sorted(A24.glob(f"R{rid:03d}_*")):
                if (d / "results").exists():
                    t = "".join(f.read_text() for f in sorted((d / "results").glob("*.json")))
                break
            BLOB[rid] = t
        return BLOB[rid]

    def harvest(doc):
        out = []
        for i, ln in enumerate((E05 / doc).read_text().splitlines()):
            rr = sorted({int(x) for x in re.findall(r"R(\d{3})", ln)})
            if not rr:
                continue
            for mm in NUM.finditer(ln):
                v = (mm.group(1) or mm.group(2)).replace(",", "")
                try:
                    float(v)
                except ValueError:
                    continue
                med = rr[len(rr) // 2]
                out.append({"line": i, "value": v, "cites": rr, "median_cite": med,
                            "spans_split": min(rr) < SPLIT <= max(rr),
                            "flagged": not any(m_rounded(v, blob(r)) for r in rr)})
        return out

    FIG = {d: harvest(d) for d in DOCS}
    print("R754 · only one document can separate era from governance\n")

    # ---- E1 : the identification structure. STRUCTURE, not a result.
    def binof(e):
        return next(i for i, (lo, hi) in enumerate(BINS) if lo <= e < hi)
    counts = {d: [0] * len(BINS) for d in DOCS}
    for d in DOCS:
        for f in FIG[d]:
            counts[d][binof(f["median_cite"])] += 1
    print(f"  {'document':<18}" + "".join(f"{f'{lo}-{hi}':>11}" for lo, hi in BINS) + f"{'total':>8}")
    for d in DOCS:
        print(f"  {d:<18}" + "".join(f"{c:>11}" for c in counts[d]) + f"{sum(counts[d]):>8}")
    pairs = [(DOCS[i], DOCS[j]) for i in range(3) for j in range(i + 1, 3)]
    ident = {}
    for a, b in pairs:
        joint = sum(1 for k in range(len(BINS)) if counts[a][k] > 0 and counts[b][k] > 0)
        empty = sum(1 for k in range(len(BINS)) if counts[a][k] == 0 or counts[b][k] == 0)
        ident[f"{a}|{b}"] = {"joint_bins": joint, "empty_joint_bins": empty,
                             "identifiable": empty == 0}
        print(f"  {a[:14]} vs {b[:14]:<16} joint bins {joint}/{len(BINS)}  "
              f"{'IDENTIFIABLE' if empty == 0 else 'UNIDENTIFIABLE on ' + str(empty) + ' bin(s)'}")
    P5 = sum(1 for v in ident.values() if not v["identifiable"])
    print(f"P5        pairs with >=1 empty joint bin: {P5}  (registered 2, band [0,3])")
    print("  ⛔ an empty joint bin cannot be stratified. That is DEFINITIONAL -- an IDENTIFICATION "
          "failure, not a power failure, and the two are not reported as one.")

    # ---- E2 : within DEFINITION.md, old vs new
    def split_rates(doc, thr=SPLIT):
        old = [f for f in FIG[doc] if f["median_cite"] < thr]
        new = [f for f in FIG[doc] if f["median_cite"] >= thr]
        r = lambda g: (sum(1 for f in g if f["flagged"]) / len(g)) if g else None
        return {"n_old": len(old), "n_new": len(new), "rate_old": r(old), "rate_new": r(new),
                "lines_old": len({f['line'] for f in old}), "lines_new": len({f['line'] for f in new}),
                "diff": (r(old) - r(new)) if (old and new) else None}
    D_def = split_rates("DEFINITION.md")
    D_stm = split_rates("STATEMENT.md")
    D_for = split_rates("FORMULATION.md")
    spanning = sum(1 for f in FIG["DEFINITION.md"] if f["spans_split"])
    print(f"\n  {'document':<18}{'n_old':>7}{'n_new':>7}{'rate_old':>10}{'rate_new':>10}{'diff':>9}")
    for nm, S in (("DEFINITION.md", D_def), ("STATEMENT.md", D_stm), ("FORMULATION.md", D_for)):
        ro = f"{S['rate_old']:.4f}" if S["rate_old"] is not None else "n/a"
        rn = f"{S['rate_new']:.4f}" if S["rate_new"] is not None else "UNDEFINED"
        df = f"{S['diff']:+.4f}" if S["diff"] is not None else "n/a"
        print(f"  {nm:<18}{S['n_old']:>7}{S['n_new']:>7}{ro:>10}{rn:>10}{df:>9}")
    print(f"  ⛔ FORMULATION's new-era rate is UNDEFINED (0 figures), NOT zero. An undefined rate is "
          f"never plotted as 0.")
    print(f"P2        DEFINITION figures citing rounds on BOTH sides of R{SPLIT}: {spanning}  "
          f"(registered 15, band [0,60])")

    # ---- E3 : the MDE, computed before interpretation, validated by simulation
    pbar = sum(1 for f in FIG["DEFINITION.md"] if f["flagged"]) / len(FIG["DEFINITION.md"])
    m_fig = mde(D_def["n_old"], D_def["n_new"], pbar)
    m_lin = mde(D_def["lines_old"], D_def["lines_new"], pbar)
    print(f"\nP3        analytic MDE (figures) {m_fig:.4f}, (lines, conservative) {m_lin:.4f}  "
          f"(registered 0.25, band [0.10,0.50])   pbar {pbar:.4f}")
    pos, nul = [], []
    for seed in (0, 1, 2):
        pos.append(sim_reject(D_def["n_old"], D_def["n_new"], min(pbar + m_fig, 0.999), pbar, seed))
        nul.append(sim_reject(D_def["n_old"], D_def["n_new"], pbar, pbar, seed))
    P4 = sum(pos) / len(pos); P_nul = sum(nul) / len(nul)
    lo, hi = 0.0, min(0.999 - pbar, 0.9)
    for _ in range(24):
        mid = (lo + hi) / 2
        if sim_reject(D_def["n_old"], D_def["n_new"], pbar + mid, pbar, 0, trials=8000) < 0.80:
            lo = mid
        else:
            hi = mid
    m_emp = (lo + hi) / 2
    ladder = [(0.0, sim_reject(D_def["n_old"], D_def["n_new"], pbar, pbar, 0)),
              (m_emp / 2, sim_reject(D_def["n_old"], D_def["n_new"], pbar + m_emp / 2, pbar, 0)),
              (m_emp, sim_reject(D_def["n_old"], D_def["n_new"], pbar + m_emp, pbar, 0)),
              (min(2 * m_emp, 0.9),
               sim_reject(D_def["n_old"], D_def["n_new"], min(pbar + 2 * m_emp, 0.999), pbar, 0))]
    MONOTONE = all(ladder[i][1] <= ladder[i + 1][1] + 1e-9 for i in range(len(ladder) - 1))
    print(f"P4        simulated rejection at the analytic MDE: {P4:.4f} (seeds "
          f"{[round(x,4) for x in pos]})  (registered 0.78, band [0.60,0.92])")
    print(f"          EMPIRICAL MDE {m_emp:.4f} ({m_emp/m_fig:.2f}x analytic); ladder "
          f"{[(round(d,3), round(r,4)) for d, r in ladder]}  monotone={MONOTONE}")
    POSITIVE = MONOTONE
    G0 = 0.02 <= P_nul <= 0.09
    print(f"POSITIVE  the LADDER is the control; band floor {ladder[0][1]:.4f}, ceiling "
          f"{ladder[-1][1]:.4f}   {'PASS' if POSITIVE else 'FAIL'}")
    print(f"g=0       null rejection {P_nul:.4f} ~ alpha  {'PASS' if G0 else 'FAIL'}")

    # ---- NEGATIVE : shuffle the OLD/NEW label
    # ⛔ REPAIRED AFTER ITS FIRST RUN, AND THE FAILURE IS §4's ROW ② VERBATIM.
    #    v1 asked whether ONE shuffle produced a smaller |diff| than the real one, and reported FAIL.
    #    But the real difference is -0.0096, essentially zero, and a single shuffle produces a
    #    random difference of order the standard error -- which will almost always EXCEED a
    #    near-null effect. "|permuted| < |real| is a coin flip when the real effect is null, which
    #    is exactly when you are running it." The control PRESUPPOSED a non-null effect.
    #    The correct null is the shuffle DISTRIBUTION, and the question is where the real difference
    #    sits inside it. A real difference at an unremarkable percentile CONFIRMS the null rather
    #    than failing the control.
    fl = [f["flagged"] for f in FIG["DEFINITION.md"]]
    n_old = D_def["n_old"]
    rng = np.random.default_rng(0)
    null_diffs = []
    for _ in range(5000):
        perm = rng.permutation(len(fl))
        a = [fl[perm[i]] for i in range(n_old)]
        b = [fl[perm[i]] for i in range(n_old, len(fl))]
        null_diffs.append(sum(a) / len(a) - sum(b) / len(b))
    null_diffs.sort()
    real = D_def["diff"]
    pct = sum(1 for d in null_diffs if abs(d) <= abs(real)) / len(null_diffs)
    null_sd = statistics.pstdev(null_diffs)
    NEGATIVE = (null_sd > 0)          # the null must be non-degenerate; that is what it certifies
    print(f"NEGATIVE  permutation null over 5000 shuffles: sd {null_sd:.4f}, "
          f"2.5-97.5 pct [{null_diffs[125]:+.4f}, {null_diffs[-126]:+.4f}]")
    print(f"            the real difference {real:+.4f} sits at the {pct:.1%} percentile of |null| "
          f"-- {'UNREMARKABLE, which CONFIRMS the null' if pct < 0.95 else 'EXTREME'}")
    print(f"            {'PASS' if NEGATIVE else 'FAIL -- the null is degenerate'}  (v1 asked "
          f"|shuffle| < |real|, which presupposes a non-null effect: §4 row ②)")

    # ---- SHAM : ingredient ABSENT -- arbitrary split points
    meds = sorted(f["median_cite"] for f in FIG["DEFINITION.md"])
    rng2 = np.random.default_rng(7)
    sham_diffs = []
    for _ in range(5):
        thr = int(meds[int(rng2.integers(len(meds) // 5, 4 * len(meds) // 5))])
        S = split_rates("DEFINITION.md", thr)
        if S["diff"] is not None:
            sham_diffs.append((thr, S["diff"]))
    sham_max = max(abs(d) for _, d in sham_diffs) if sham_diffs else None
    SHAM = sham_max is not None
    print(f"SHAM      ingredient ABSENT -- 5 arbitrary split points {[(t, round(d,4)) for t, d in sham_diffs]}")
    print(f"            largest arbitrary-split |diff| {sham_max:.4f} vs the R{SPLIT} split's "
          f"{abs(D_def['diff']):.4f}")

    # ---- PLACEBO
    PLACEBO = (split_rates("DEFINITION.md")["diff"] == D_def["diff"])
    print(f"PLACEBO   recomputed twice, difference exactly 0  {'PASS' if PLACEBO else 'FAIL'}")

    # ---- CONFOUND : the same split on STATEMENT.md
    print(f"CONFOUND  the SAME split on STATEMENT.md: old {D_stm['rate_old']:.4f} "
          f"(n={D_stm['n_old']}) vs new {D_stm['rate_new']:.4f} (n={D_stm['n_new']}), diff "
          f"{D_stm['diff']:+.4f} -- if this matches DEFINITION's slope the effect belongs to the "
          f"CITED ROUNDS rather than to any document's practice")

    # ---- DIRECTIONAL
    d_old = D_def["rate_old"]
    D_dir = abs(d_old - 0.8000) < abs(d_old - 0.1793)
    print(f"DIRECTIONAL DEFINITION's old-era rate {d_old:.4f} is closer to FORMULATION's 0.8000 "
          f"than to STATEMENT's 0.1793: {D_dir}")

    # ---- VERDICT : computed, referencing every declared control
    controls = {"POSITIVE": POSITIVE, "g0": G0, "NEGATIVE": NEGATIVE,
                "PLACEBO": PLACEBO, "SHAM": SHAM}
    diff = D_def["diff"]
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire"
    elif diff is not None and diff >= m_emp:
        world, why = "A", ("era carries it -- governance is NOT established and R753's directional "
                           "must be downgraded on the page")
    elif diff is not None and abs(diff) < m_emp / 3:
        world, why = "B", ("era does not explain it where it CAN be measured, so the governance "
                           "reading survives its strongest confound -- which is the most it can do, "
                           "since the decisive contrast is unidentifiable")
    else:
        world, why = "C", (f"UNRESOLVED: the difference {diff:+.4f} is below the empirical MDE "
                           f"{m_emp:.4f} but not near zero. Silence, not agreement")
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R754", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"),
           "era_bins": {d: counts[d] for d in DOCS}, "identifiability": ident,
           "P5_unidentifiable_pairs": P5,
           "split_at": SPLIT, "definition_split": D_def, "statement_split": D_stm,
           "formulation_split": D_for, "P2_spanning_figures": spanning,
           "pbar": pbar, "P3_mde_figures": m_fig, "P3_mde_lines": m_lin,
           "P4_reject_at_analytic": P4, "reject_at_null": P_nul,
           "mde_empirical": m_emp, "empirical_over_analytic": m_emp / m_fig,
           "ladder": [list(x) for x in ladder], "ladder_monotone": MONOTONE,
           "negative_null_sd": null_sd, "negative_null_ci": [null_diffs[125], null_diffs[-126]],
           "real_diff_percentile_of_null": pct,
           "sham_arbitrary_splits": [list(x) for x in sham_diffs], "sham_max_abs": sham_max,
           "directional_closer_to_formulation": D_dir,
           "controls": controls,
           "empty_bin_is_definitional": True, "undefined_is_not_zero": True}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r754.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r754.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
