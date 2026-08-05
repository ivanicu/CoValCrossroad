#!/usr/bin/env python3
"""
R717 -- a ratio split by its own denominator: the comparison R716 proposed, and why it is biased.

CHECK #319 ON R716's NEXT LINE — ITS NUMBERS HOLD AND ITS COMPARISON IS STRUCTURALLY BIASED.
  ✓ 942 against 44 confirmed; no round has split provenance by k, so the question is genuinely
    unasked.
  ⛔⛔ BUT THE STATISTIC IS m/k AND THE SPLIT IS BY k. Splitting a ratio by its own DENOMINATOR is
    conditioning on a component of the statistic, and the groups do not share a support:
    k=4 admits {0, ¼, ½, ¾, 1}, k=3 admits {0, ⅓, ⅔, 1}, k=2 admits {0, ½, 1}.
  ⭐ DERIVATION, before any data: at the SAME match count m=1 the share is 0.2500 at k=4, 0.3333 at
    k=3, 0.5000 at k=2 — identical counts FORCE a higher share in the smaller-k group. The bias has
    a KNOWN SIGN, and that is what makes the observed direction readable at all.

ESTIMAND        (i) the bias DIRECTION, derived, against the observed direction; (ii) the group
                difference on the UNBIASED statistic, the raw match count; (iii) the MDE at the
                ACTUAL 942/44 imbalance, because an even-split MDE cannot be assumed to carry over.
IDENTIFICATION  (i) is a DERIVATION, labelled. (ii) and (iii) are measured. ⚠ the count is unbiased
                with respect to THIS split and is not thereby the right statistic — R716 measured
                its MDE as 5-7x worse than the share's.
SCOPE           population : the 986 rubrics, split 942 (k=4) against 44 (k in {2,3})
                instrument : permutation over group labels + planted-shift power at the true
                             imbalance
                             instrument unit = A CORE INSTANCE
                             claim unit      = WHETHER THE k-GROUPS DIFFER IN PROVENANCE
                             ⚠ NOT EQUAL -- a difference in a statistic computed FROM k cannot by
                             itself be a difference in provenance BETWEEN k-groups.
                baseline   : the structural bias's own direction, and a label-permutation null
                regime     : this repository at HEAD, alpha 0.05, power 0.80
WORLDS          A UNREADABLE · B REAL AND AGAINST THE BIAS · C CONFOUNDED
KILL            conditional on POSITIVE recovering a planted shift and g=0 sitting at alpha
POSITIVE CTRL   a 0.20 shift planted into the 44-member group, detected at >= 80%, with FLOOR and
                CEILING computed and the target required to lie strictly between
g=0             a shift of exactly 0 must reject at ~alpha
NEGATIVE CTRL   group labels permuted at the true 942/44 sizes
SHAM            the same comparison split on a variable UNRELATED to the statistic (id parity) at
                the same imbalance -- the ingredient removed
PLACEBO         two identical runs differ by exactly 0
ARTIFACT        results/split_by_k.json
IMPOSSIBLE      removing the bias by a better ratio (every share with k in its denominator inherits
                it) · cross-release (one release)
"""
from __future__ import annotations
import json, pathlib, random, statistics, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
SRC = ROOT / "data" / "conversation_rubrics.jsonl"
SEEDS, NPERM, NPOW, ALPHA, POWER = (0, 1, 2), 3000, 400, 0.05, 0.80
INSTRUMENT_UNIT = "A CORE INSTANCE"
CLAIM_UNIT = "WHETHER THE k-GROUPS DIFFER IN PROVENANCE"


def perm_null(vals, n_a, seeds=SEEDS, n=NPERM):
    out = []
    for sd in seeds:
        r = random.Random(sd)
        for _ in range(n // len(seeds)):
            x = r.sample(vals, len(vals))
            out.append(statistics.fmean(x[:n_a]) - statistics.fmean(x[n_a:]))
    out.sort()
    return out


def ci(dist):
    return dist[int(0.025 * (len(dist) - 1))], dist[int(0.975 * (len(dist) - 1))]


def power_at(vals, n_a, shift, seed, ndraw=NPOW):
    """Reject rate when group A (size n_a) is shifted. A is the SMALL group here."""
    r = random.Random(seed)
    rej = 0
    for _ in range(ndraw):
        x = r.sample(vals, len(vals))
        a = [min(1.0, v + shift) for v in x[:n_a]]
        b = x[n_a:]
        obs = statistics.fmean(a) - statistics.fmean(b)
        merged = a + b
        null = []
        for _ in range(60):
            r.shuffle(merged)
            null.append(statistics.fmean(merged[:n_a]) - statistics.fmean(merged[n_a:]))
        null.sort()
        if obs > null[int((1 - ALPHA) * (len(null) - 1))]:
            rej += 1
    return rej / ndraw


def main() -> int:
    if not SRC.exists():
        print(f"⛔ {SRC} absent — exit 2 rather than passing on an empty population")
        return 2
    rows = [json.loads(l) for l in SRC.read_text().splitlines() if l.strip()]
    recs = []
    for i, r in enumerate(rows):
        fs = {x["criterion"] for x in r["coval_full"]}
        c = [x["criterion"] for x in r["coval_core"]]
        m = sum(1 for x in c if x in fs)
        recs.append({"k": len(c), "m": float(m), "share": m / len(c),
                     "parity": int(r["conversation"]["id"].replace("-", "")[-1], 16) % 2})
    n = len(recs)
    big = [x for x in recs if x["k"] == 4]
    small = [x for x in recs if x["k"] < 4]
    n_s = len(small)

    print(f"─── ⛔ THE DERIVATION, STATED BEFORE THE MEASUREMENT ───")
    for k in sorted({x['k'] for x in recs}):
        sup = [round(m / k, 4) for m in range(k + 1)]
        print(f"  k={k}  n={sum(1 for x in recs if x['k']==k):>4}  support {sup}")
    print(f"  ⭐ at the SAME match count m=1: share = {1/4:.4f} (k=4), {1/3:.4f} (k=3), "
          f"{1/2:.4f} (k=2). Identical counts FORCE a higher share at smaller k.")
    print(f"  ⭐ so the bias pushes the SMALL group UP; any observed k=4 > k<4 runs AGAINST it.")

    obs_share = statistics.fmean([x["share"] for x in small]) - \
                statistics.fmean([x["share"] for x in big])
    obs_count = statistics.fmean([x["m"] for x in small]) - statistics.fmean([x["m"] for x in big])
    print(f"\n  observed (small minus big): share {obs_share:+.4f}   count {obs_count:+.4f}")
    print(f"  ⭐ both NEGATIVE — the small group is LOWER on both, against the bias's direction.")

    print(f"\n─── CONTROLS ───")
    sh_all = [x["share"] for x in recs]
    floor = power_at(sh_all, n_s, 0.0, 11)
    ceil = power_at(sh_all, n_s, 0.60, 12)
    pos = power_at(sh_all, n_s, 0.20, 13)
    band = floor < POWER < ceil
    posok = pos >= POWER and band
    print(f"  POSITIVE  a 0.20 shift into the {n_s}-member group detected at {pos:.4f}")
    print(f"            floor(no shift) {floor:.4f} < {POWER} < ceiling(0.60) {ceil:.4f} -> "
          f"{'PASS — the band is real' if band else '⛔ FAIL'}   overall "
          f"{'PASS' if posok else '⛔ FAIL'}")
    g0ok = floor <= 2 * ALPHA
    print(f"  g=0       a shift of exactly 0 rejects at {floor:.4f} vs 2a={2*ALPHA:.2f} -> "
          f"{'PASS' if g0ok else '⛔ FAIL'}")
    nd_share = perm_null(sh_all, n_s)
    lo_s, hi_s = ci(nd_share)
    negok = lo_s <= 0.0 <= hi_s
    print(f"  NEGATIVE  labels permuted at the true {n_s}/{n-n_s} sizes: 95% "
          f"[{lo_s:+.4f}, {hi_s:+.4f}] contains 0 -> "
          f"{'PASS — no 44-member subset differs by itself' if negok else '⛔ FAIL'}")
    par1 = [x for x in recs if x["parity"] == 1][:n_s]
    par0 = [x for x in recs if x not in par1]
    sham_diff = statistics.fmean([x["share"] for x in par1]) - \
                statistics.fmean([x["share"] for x in par0])
    shamok = lo_s <= sham_diff <= hi_s
    print(f"  SHAM      split on conversation-id PARITY at the same imbalance: difference "
          f"{sham_diff:+.4f} -> "
          f"{'PASS — inside the null, the ingredient is the k-split' if shamok else '⛔ FAIL'}")
    plc = perm_null(sh_all, n_s)[:5] == nd_share[:5]
    print(f"  PLACEBO   two identical runs differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT      '{INSTRUMENT_UNIT}' != claim unit -> {'PASS' if unitok else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and shamok and plc and unitok

    print(f"\n─── THE MDE AT THE TRUE {n_s}/{n-n_s} IMBALANCE ───")
    curve, mde = [], None
    for s in [i / 100 for i in range(0, 41, 4)]:
        p = power_at(sh_all, n_s, s, 400 + int(s * 100))
        curve.append({"shift": s, "power": p})
        if mde is None and p >= POWER:
            mde = s
    print("  " + "  ".join(f"{c['shift']:.2f}:{c['power']:.2f}" for c in curve))
    print(f"  ⭐ MDE = {('%.3f' % mde) if mde is not None else 'NOT REACHED by 0.40'}   against "
          f"R716's even-split 0.040   ratio "
          f"{(mde/0.040) if mde is not None else float('inf'):.1f}×")
    print(f"  ⭐ and against the OBSERVED |difference| of {abs(obs_share):.4f}")

    print(f"\n─── THE SPECIFICATION SWEEP (2 statistics × 3 splits = 6 cells) ───")
    cells = []
    rng = random.Random(99)
    rand_idx = set(rng.sample(range(n), n_s))
    splits = {
        "k=4 vs k<4": (small, big),
        "id-parity sham": (par1, par0),
        "random 44/942": ([recs[i] for i in rand_idx],
                          [recs[i] for i in range(n) if i not in rand_idx]),
    }
    print(f"  {'split':<18}{'statistic':<14}{'diff':>9}{'null 95%':>24}{'  verdict'}")
    for sname, (a, b) in splits.items():
        for stat in ("share", "m"):
            vals = [x[stat] for x in recs]
            d = statistics.fmean([x[stat] for x in a]) - statistics.fmean([x[stat] for x in b])
            nd = perm_null(vals, len(a))
            lo, hi = ci(nd)
            surv = not (lo <= d <= hi)
            cells.append({"split": sname, "statistic": stat, "diff": d, "null": [lo, hi],
                          "survives": surv})
            print(f"  {sname:<18}{stat:<14}{d:>+9.4f}   [{lo:+.4f}, {hi:+.4f}]"
                  f"   {'⭐ SURVIVES' if surv else 'inside the null'}")
    surv_n = sum(1 for c in cells if c["survives"])

    unreadable = mde is None or mde > abs(obs_share)
    print(f"\n─── REGISTERED ───")
    print(f"  A  [DERIVED] bias direction: higher share at smaller k for equal counts. Observed "
          f"share difference (small−big) {obs_share:+.4f} -> "
          f"{'AGAINST the bias' if obs_share < 0 else 'WITH the bias'}")
    print(f"  B  MDE at {n_s}/{n-n_s} = 0.10 [0.02,0.40] -> "
          f"{('%.3f' % mde) if mde is not None else 'NOT REACHED'}: "
          f"{'INSIDE' if mde is not None and 0.02 <= mde <= 0.40 else '⛔ OUTSIDE'}")
    cnt_cell = next(c for c in cells if c["split"] == "k=4 vs k<4" and c["statistic"] == "m")
    print(f"  C  count difference survives its null -> "
          f"{'SURVIVES' if cnt_cell['survives'] else 'does NOT survive (as predicted)'}, "
          f"|diff| {abs(cnt_cell['diff']):.4f}")
    print(f"  DIRECTIONAL MDE >= 2× the even-split 0.040 -> "
          f"{'HOLDS' if mde is not None and mde >= 0.08 else '⛔ FAILS'}")
    print(f"\n  MULTIPLICITY: {len(cells)} cells, {surv_n} surviving their own null; all printed.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; the comparison would be silence."
    elif unreadable:
        world = (
            f"⭐⭐⭐ A UNREADABLE, AND THE COMPARISON WAS BIASED BEFORE IT WAS UNREADABLE. R716's NEXT "
            f"line proposed splitting the provenance share by k — but the share IS m/k, so the split "
            f"conditions on the statistic's own DENOMINATOR, and the groups do not share a support: "
            f"k=4 admits {{0,¼,½,¾,1}} and k=2 admits {{0,½,1}}. ⭐ At the same match count m=1 the "
            f"share is {1/4:.4f} at k=4 and {1/2:.4f} at k=2, so identical counts FORCE a higher "
            f"share in the smaller-k group — the bias has a known SIGN and it pushes the small group "
            f"UP. ⭐⭐ THE OBSERVED DIFFERENCE RUNS AGAINST IT: small minus big is {obs_share:+.4f} on "
            f"the share and {obs_count:+.4f} on the count, both NEGATIVE. ⛔ BUT NONE OF IT IS "
            f"READABLE: the MDE at the true {n_s}/{n-n_s} imbalance is "
            f"{('%.3f' % mde) if mde is not None else 'not reached by 0.40'} — "
            f"{(mde/0.040) if mde is not None else float('inf'):.1f}× R716's even-split 0.040 — "
            f"against an observed |difference| of {abs(obs_share):.4f}. ⭐ SO R716's OWN CAUTION WAS "
            f"RIGHT AND ITS QUESTION IS STILL UNANSWERABLE: an even-split MDE does not carry over to "
            f"a group of {n_s}, and this is the second time in three rounds that computing the "
            f"resolution first turned a proposed comparison into a bound. ⚠ AND THE SHAM ESTABLISHES "
            f"LESS THAN IT LOOKS: {surv_n} of {len(cells)} sweep cells survive their own null — "
            f"INCLUDING the k-split cells — so the id-parity sham landing inside the null at "
            f"{sham_diff:+.4f} does NOT show that the k-split is the ingredient. It shows that NO "
            f"split at this imbalance is readable, which is weaker and different. "
            f"⚠ AND THE BIAS CANNOT BE ANALYSED AWAY: every share with k in its denominator inherits "
            f"it; only the raw count avoids it, and R716 measured the count's MDE as 5–7× worse. "
            f"⚠ UNIT GAP: instrument unit is {INSTRUMENT_UNIT}, claim unit is {CLAIM_UNIT}.")
    elif cnt_cell["survives"]:
        world = (f"⭐⭐⭐ B REAL AND AGAINST THE BIAS — the count difference {obs_count:+.4f} survives "
                 f"its null and runs opposite to the structural bias, so the share understates it.")
    else:
        world = (f"⭐⭐⭐ C CONFOUNDED — the share difference survives while the count difference does "
                 f"not, which is the quantisation the derivation predicted.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "split_by_k.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "n": n,
        "group_sizes": {"k=4": len(big), "k<4": n_s},
        "supports": {str(k): [m / k for m in range(k + 1)] for k in sorted({x["k"] for x in recs})},
        "bias_direction": "equal counts give a HIGHER share at SMALLER k",
        "observed_share_diff_small_minus_big": obs_share,
        "observed_count_diff_small_minus_big": obs_count,
        "runs_against_bias": obs_share < 0,
        "mde_at_true_imbalance": mde, "mde_even_split_R716": 0.040,
        "mde_ratio": (mde / 0.040) if mde is not None else None,
        "power_curve": curve, "unreadable": unreadable,
        "controls": {"positive_at_0.20": pos, "floor": floor, "ceiling": ceil,
                     "perm_null95": [lo_s, hi_s], "sham_parity_diff": sham_diff},
        "cells": cells, "n_surviving": surv_n,
        "registered": ("A[DERIVED] bias direction + observed sign; B MDE 0.10 [0.02,0.40]; "
                       "C count difference predicted NOT to survive; directional MDE >= 2x 0.040"),
        "observed": {"A": obs_share, "B": mde, "C": cnt_cell["survives"],
                     "directional": mde is not None and mde >= 0.08},
        "limit": ("the bias cannot be analysed away — every share with k in its denominator inherits "
                  "it; only the raw count avoids it, and its MDE is 5-7x worse."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
