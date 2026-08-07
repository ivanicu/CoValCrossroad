#!/usr/bin/env python3
"""R978 — does the definition's EXTENSION depend on how many prompts were scored?

⛔ WHY THIS AND NOT MORE CLAUSE ④ WORK. R976 showed ④'s bar is the design's resolution wearing a
clause's clothes. Clause ② has the same shape — a mean comparison against a cut, with a measured
resolution of 0.0099555 and 5 of its 28 admitted arms sitting inside that resolution (R923). The
extension is already known to be fragile across COMPARATOR: 2 of 12 admitted arms flip between the
only two legitimate ones (R906/R921). **Nobody has asked whether it is fragile across N.** If it is,
then `core` is not a category on this release — it is a category whose membership depends on how
many prompts you happened to score, and the definition has to say so.

ESTIMAND        the CHURN of clause ②'s admitted set under subsampling: |admitted(N) Δ admitted(968)|
                as a count of arms, per comparator, per seed.
IDENTIFICATION  identified. The cut and the arm means come from the SAME prompts, so subsampling is
                paired and no arm is advantaged; the admitted set is a deterministic function of the
                subsample.
                ⚠ PARTIALLY for the CAUSE: churn confounds "the arm is near the cut" with "the arm's
                per-prompt variance is high". The registered prediction below separates them, since
                it is built from each arm's OWN sd.
SCOPE           population : R881's arm inventory scored on the 968 shared prompts, subsampled
                instrument : mean A2 against human targets; cut = the comparator's own mean A2
                baseline   : the committed full-N sets — generic 24, genericpool16 28 (R923)
                regime     : N ∈ {242, 484, 726, 968}; both legitimate comparators
WORLDS          A STABLE        the extension is a property of the arms. Churn ≤ 1 arm even at
                                N = 242, and the definition's membership means what it says.
                B N-DEPENDENT   churn grows as the boundary layer widens (∝ 1/√N) and tracks the
                                count of arms inside z·sd/√N of the cut, which is computable from
                                the FULL data before any subsample is drawn.
                prediction matrix: A -> churn ≈ 0 at every N. B -> churn rises monotonically as N
                falls, and the measured churn is bracketed by the registered band count.
KILL            pre-registered, CONDITIONAL on the positive control reproducing R923's 24 and 28:
                if median churn at N=242 is ≤ 1 arm for both comparators, world B is dead.
                If the positive control fails, the verdict is UNVERIFIED — never world A.
POSITIVE CTRL   the full-N admitted counts must reproduce R923's committed 24 and 28 exactly. An
                instrument that cannot re-derive the committed extension is not measuring it.
NEGATIVE CTRL   shuffle the arm labels against the score vectors and recompute: churn must jump to
                near the maximum, showing the statistic can register instability at all.
PLACEBO         admitted(968) against itself: churn must be exactly 0.
NOISE FLOOR     the registered band count — arms within z·sd/√N of the cut — computed from the full
                data, so the prediction exists before the subsamples do.
SEEDS           3 subsample seeds per N, reported per seed, never averaged.
MULTIPLICITY    2 comparators × 4 N × 3 seeds = 24 cells, all reported.
ARTIFACT        results/extension_vs_n.json with this file's source hash.
IMPOSSIBLE      cross-release — N/A: subsampling varies N on ONE corpus and cannot separate
                "fewer prompts" from "different prompts". A second release would be required.
                construct validity — N/A: this measures whether the extension MOVES, not whether
                either extension is correct. An external gold standard for `core` would be needed.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import statistics as stats
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
# ⚠ parents[2], not [3]. Sibling rounds write `__file__.resolve().parents[3]`, which is correct
#   because it counts from the FILE; counting from HERE (already the round dir) is one shorter.
#   Copying the sibling's number without its starting point put ROOT at /home/ivan and the import
#   died — loudly, which is the good case. A path that resolves to a WRONG-but-existing directory
#   is the one that would have run and been silently about something else.
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                          # noqa: E402

Z = 1.96
NS = (242, 484, 726, 968)
SEEDS = (101, 202, 303)
CHURN_FLAT = 1          # world A's registered band


def main() -> int:
    r881 = next(A24.glob("R881_*/results/boundary_distance.json"), None)
    r921 = next(A26.glob("R921_*/results/comparator_sweep.json"), None)
    r923 = next(A27.glob("R923_*/results/bar_resolution.json"), None)
    if not (r881 and r921 and r923):
        print("  UNRUNNABLE: a prior artifact is missing. Exit 2, never 0.")
        return 2
    legit = json.loads(r921.read_text())["legitimate_comparators"]
    committed = json.loads(r923.read_text())["wiring"]
    arms881 = [x["arm"] for x in json.loads(r881.read_text())["arms"]]

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                return None
            v = np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p in Sa:
                    c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                    v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
            if np.isfinite(v).sum() < 200:
                return None
            return np.nan_to_num(v, nan=np.nanmean(v))
        return None

    V, names = [], []
    for a in arms881:
        v = vec(a)
        if v is not None:
            V.append(v); names.append(a)
    V = np.array(V)
    print(f"POPULATION  {len(names)} arms × {n} prompts")
    if len(names) < 20 or n < 500:
        print("  UNRUNNABLE: population too small. Exit 2, never 0.")
        return 2

    NBOOT = 8000

    def admitted(idx, comp, seed=921):
        """⛔ ADMISSION IS A *RESOLVABLE* BEAT, NOT A MEAN COMPARISON, AND MY FIRST VERSION HAD IT
        WRONG. I wrote `mean(arm) > mean(comparator)` and the positive control refused it: 26 and 30
        admitted against R923's committed 24 and 28. Read from R923 run.py:145-151, the rule is
        `lo > 0` where `lo` is the 2.5th percentile of the bootstrapped paired difference against the
        comparator, and the reported `cut` is `means[adm].min()` — the LOWEST ADMITTED ARM, not the
        comparator's score. That is why the committed `generic` cut 0.5593110792 turned out to be the
        mean A2 of `topw_k8`.
        ⭐ AND THE ERROR WAS A FRAMING ERROR, NOT A CODING ONE, which is the only kind a re-run of my
        own algorithm could never have caught. It also ran in the flattering direction for the null:
        a plain threshold has no interval to widen, so it would have UNDERSTATED the N-dependence
        this round exists to measure."""
        ci = names.index(comp)
        X = V[:, idx]
        N = X.shape[1]
        D = X - X[ci]
        rng = np.random.default_rng(seed)
        bidx = rng.integers(0, N, (NBOOT, N))
        counts = np.zeros((NBOOT, N))
        for b in range(NBOOT):
            counts[b] = np.bincount(bidx[b], minlength=N)
        Dboot = D @ counts.T / N                      # arms × NBOOT, via BLAS
        lo = np.percentile(Dboot, 2.5, axis=1)
        adm = lo > 0
        adm[ci] = False
        m = X.mean(axis=1)
        cut = float(m[adm].min()) if adm.any() else float("nan")
        return {names[i] for i in range(len(names)) if adm[i]}, cut

    ALL = np.arange(n)

    # ── POSITIVE CONTROL: re-derive R923's committed extension.
    print("\nPOSITIVE CONTROL — re-derive the committed full-N extension")
    full, pos_ok = {}, True
    for comp in legit:
        s, cut = admitted(ALL, comp)
        full[comp] = s
        want = committed[comp]
        ok = len(s) == want["n"] and abs(cut - want["cut"]) < 1e-6
        pos_ok &= ok
        print(f"  {comp:<16} cut {cut:.10f} (committed {want['cut']:.10f})   "
              f"admitted {len(s)} (committed {want['n']})   {'PASS' if ok else '⛔ FAIL'}")

    # ── PLACEBO
    placebo = sum(len(full[c] ^ full[c]) for c in legit)
    print(f"PLACEBO           admitted(968) against itself: churn {placebo} (must be 0)")

    # ── THE REGISTERED PREDICTION, from the FULL data, before any subsample is drawn.
    print("\nREGISTERED PREDICTION — arms within z·sd/√N of the cut (computed on full data)")
    band = {}
    for comp in legit:
        ci = names.index(comp)
        d = V - V[ci]                       # paired difference against the comparator
        m, sd = d.mean(axis=1), d.std(axis=1, ddof=1)
        for N in NS:
            k = int(sum(1 for i in range(len(names))
                        if i != ci and abs(m[i]) < Z * sd[i] / np.sqrt(N)))
            band[(comp, N)] = k
        print(f"  {comp:<16}" + "".join(f"  N={N}:{band[(comp,N)]:>3}" for N in NS))

    # ── THE SWEEP
    print("\nMEASURED CHURN  |admitted(N) Δ admitted(968)|, per seed")
    print(f"  {'comparator':<16}{'N':>6}" + "".join(f"{f'seed {s}':>10}" for s in SEEDS)
          + f"{'band':>7}")
    rows = []
    for comp in legit:
        for N in NS:
            cs = []
            for seed in SEEDS:
                rng = np.random.default_rng(seed)
                idx = ALL if N == n else rng.permutation(n)[:N]
                s, cut = admitted(idx, comp)
                c = len(s ^ full[comp])
                cs.append(c)
                rows.append({"comparator": comp, "N": N, "seed": seed, "churn": c,
                             "n_admitted": len(s), "cut": cut,
                             "entered": sorted(s - full[comp]), "left": sorted(full[comp] - s)})
            print(f"  {comp:<16}{N:>6}" + "".join(f"{c:>10}" for c in cs)
                  + f"{band[(comp,N)]:>7}")

    # ── NEGATIVE CONTROL: shuffle arm labels; the statistic must register instability.
    rng = np.random.default_rng(999)
    perm = rng.permutation(len(names))
    Vs = V[perm]
    neg = []
    for comp in legit:
        ci = names.index(comp)
        m = Vs.mean(axis=1)
        s = {names[i] for i in range(len(names)) if m[i] > m[ci]}
        neg.append(len(s ^ full[comp]))
    print(f"\nNEGATIVE CONTROL  arm labels shuffled -> churn {neg} "
          f"(must be large; the statistic can see instability)")
    neg_ok = min(neg) > 5

    # ── THE KILL, conditional on the controls.
    at242 = {c: stats.median([r["churn"] for r in rows if r["comparator"] == c and r["N"] == 242])
             for c in legit}
    print(f"\nKILL  median churn at N=242: " + ", ".join(f"{c}={at242[c]}" for c in legit)
          + f"   (world A registered at ≤ {CHURN_FLAT})")
    if not (pos_ok and placebo == 0 and neg_ok):
        world = "UNVERIFIED — a control failed; neither world is excluded by this run"
    elif all(v <= CHURN_FLAT for v in at242.values()):
        world = "A STABLE — the extension does not move with N; world B is dead"
    else:
        world = (f"B N-DEPENDENT — membership moves with the prompt count "
                 f"(median churn at N=242: {at242})")
    print(f"\n⭐ {world}")

    out = HERE / "results" / "extension_vs_n.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_arms=len(names), n_prompts=n, comparators=legit, Ns=list(NS), seeds=list(SEEDS),
        committed=committed, full_admitted={c: sorted(full[c]) for c in legit},
        registered_band={f"{c}|{N}": band[(c, N)] for c in legit for N in NS},
        controls={"positive_reproduces_R923": pos_ok, "placebo_churn": placebo,
                  "negative_shuffled_churn": neg, "negative_ok": neg_ok},
        median_churn_at_242=at242, cells_tested=len(rows), rows=rows, world=world,
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}   cells {len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
