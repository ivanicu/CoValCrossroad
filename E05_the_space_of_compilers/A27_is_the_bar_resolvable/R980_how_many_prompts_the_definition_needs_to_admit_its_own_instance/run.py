#!/usr/bin/env python3
"""R980 — how many prompts does the definition need in order to admit its own instance?

⛔ WHY. R978 measured that clause ②'s extension churns with N, and its artifact contains a fact I did
not report: at N=242 under `generic`, **`coval_core` itself — the released core, the instance the
whole definition was written from — leaves the extension in 2 of 3 seeds**, and its `_2bA`/`_2bB`
siblings leave in 3 of 3. That is the churn's most consequential member and it was sitting in a
`left` list.

⭐ THE ARITHMETIC, DONE FIRST AND REGISTERED. Admission is `lo > 0` on the paired bootstrap margin,
so an arm is resolvably admitted once `z·sd(d)/√N < margin`, i.e. from
    N* = (z·sd / margin)²
Measured on the full corpus, before any sweep:
    coval_core vs generic         margin +0.015123, sd 0.11876  ->  N* = 236.9
    coval_core vs genericpool16   margin +0.024245, sd 0.12000  ->  N* =  94.1
    oracle_k4  vs generic         margin +0.076949              ->  N* =   9.2
    random_k4_s0 vs generic       margin -0.058667              ->  N* =  inf (never admitted)
**237 of the 968 available prompts, under the stronger comparator** — and R978 sampled at 242, just
above it, which is why that cell was a coin flip. The whole sweep below is a test of this curve.

ESTIMAND        `coval_core`'s admission rate under clause ② as a function of N, per comparator, and
                the N at which it crosses 0.5 and 0.95.
IDENTIFICATION  identified. Admission is a deterministic function of the subsample; the rate over
                seeds is a proportion with a binomial interval.
                ⚠ The 0.5 crossing is what N* predicts. The 0.95 crossing is NOT predicted by that
                formula and is reported as a measurement only.
SCOPE           population : subsamples of the 968 shared prompts of release one
                instrument : mean A2 vs human targets; 8000-draw paired prompt bootstrap; `lo > 0`
                baseline   : the registered N* curve above
                regime     : both legitimate comparators; N from 60 to 968
WORLDS          A THE INSTANCE IS SAFE       admission rate ≈ 1 at every N in the grid; the
                                             definition admits its own instance regardless of size.
                B ADMISSION IS A POWER FACT  the rate follows the registered curve, crossing 0.5
                                             near N* — so "coval_core is a core" is a statement
                                             about 968 prompts and not about coval_core.
                prediction matrix: A -> flat at 1.0. B -> sigmoid crossing 0.5 at 237 (generic) and
                94 (genericpool16), with genericpool16's curve strictly left of generic's.
KILL            pre-registered, CONDITIONAL on the controls: if the admission rate is ≥ 0.95 at
                every N ≥ 120 for both comparators, world B is dead. If a control fails, UNVERIFIED.
POSITIVE CTRL   `oracle_k4` (N* = 9) must be admitted at ~1.0 at every N in the grid, and
                `random_k4_s0` (N* = inf) at ~0.0. An instrument that cannot separate those two is
                not measuring admission. ⚠ These also make the g=0 direction failable: a rate of 1.0
                everywhere for the RANDOM arm would mean the rule admits anything.
NEGATIVE CTRL   at N = 968 the subsample IS the corpus, so every seed must give the identical
                verdict — a rate of exactly 0 or exactly 1, never in between.
PLACEBO         `generic` against itself: margin exactly 0, never admitted at any N.
NOISE FLOOR     10 seeds per cell; the binomial interval on each rate is reported, not assumed.
MULTIPLICITY    2 comparators × 9 N × 4 arms × 10 seeds = 720 cells, all recorded.
SEEDS           10 subsample seeds; rates reported with their interval, never a bare fraction.
ARTIFACT        results/instance_power.json with this file's source hash.
IMPOSSIBLE      cross-release — N/A: subsampling cannot separate "fewer prompts" from "different
                prompts". A second release would be required.
                construct validity — N/A: this asks how much data the RULE needs, never whether the
                rule is the right notion of a core.
"""
from __future__ import annotations
import hashlib
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                          # noqa: E402

Z = 1.96
NBOOT = 8000
NS = (60, 120, 180, 240, 300, 400, 500, 700, 968)
SEEDS = tuple(range(1001, 1011))
ARMS = ("coval_core", "oracle_k4", "random_k4_s0")


def wilson(k, n):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + Z ** 2 / n
    c = (p + Z ** 2 / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z ** 2 / (4 * n ** 2)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main() -> int:
    r921 = next(A26.glob("R921_*/results/comparator_sweep.json"), None)
    if not r921:
        print("  UNRUNNABLE: R921's artifact is missing. Exit 2, never 0.")
        return 2
    legit = json.loads(r921.read_text())["legitimate_comparators"]

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    def vec(nm):
        f = RES / f"sat_{nm}.npz"
        if not f.exists():
            return None
        Sa = load_sat(f)
        v = np.full(n, np.nan)
        for k, p in enumerate(pids):
            if p in Sa:
                c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
        return np.nan_to_num(v, nan=np.nanmean(v))

    Vc = {c: vec(c) for c in legit}
    Va = {a: vec(a) for a in ARMS}
    missing = [k for k, v in {**Vc, **Va}.items() if v is None]
    if missing:
        print(f"  UNRUNNABLE: no score vector for {missing}. Exit 2, never 0.")
        return 2
    print(f"POPULATION  {n} prompts   arms {list(Va)}   comparators {legit}")

    # ── THE REGISTERED CURVE, from the full corpus, before the sweep.
    print("\nREGISTERED N* = (z·sd/margin)²   [full corpus, no subsampling]")
    nstar = {}
    for a in ARMS:
        for c in legit:
            d = Va[a] - Vc[c]
            m, sd = float(d.mean()), float(d.std(ddof=1))
            ns = (Z * sd / m) ** 2 if m > 0 else float("inf")
            nstar[(a, c)] = ns
            print(f"  {a:<14} vs {c:<15} margin {m:+.6f}  sd {sd:.5f}  N* "
                  f"{('inf' if ns == float('inf') else f'{ns:.1f}'):>8}")

    # ── THE SWEEP
    print(f"\nADMISSION RATE over {len(SEEDS)} seeds   [Wilson 95% interval]")
    rows = []
    for c in legit:
        print(f"\n  comparator {c}   (registered N* for coval_core: {nstar[('coval_core', c)]:.0f})")
        print(f"    {'N':>6}" + "".join(f"{a:>26}" for a in ARMS))
        for N in NS:
            cells = {a: 0 for a in ARMS}
            for s in SEEDS:
                rng = np.random.default_rng(s)
                idx = np.arange(n) if N == n else rng.permutation(n)[:N]
                cnt = rng.multinomial(N, np.ones(N) / N, size=NBOOT).astype(float)
                for a in ARMS:
                    dv = (Va[a] - Vc[c])[idx]
                    bs = cnt @ dv / N
                    if float(np.percentile(bs, 2.5)) > 0:
                        cells[a] += 1
            line = f"    {N:>6}"
            for a in ARMS:
                lo, hi = wilson(cells[a], len(SEEDS))
                rows.append({"comparator": c, "N": N, "arm": a, "k": cells[a],
                             "n_seeds": len(SEEDS), "rate": cells[a] / len(SEEDS),
                             "ci": [lo, hi]})
                line += f"{f'{cells[a]}/{len(SEEDS)} [{lo:.2f},{hi:.2f}]':>26}"
            print(line)

    # ── PLACEBO: the comparator against itself.
    plac = []
    for c in legit:
        d = Vc[c] - Vc[c]
        rng = np.random.default_rng(7)
        cnt = rng.multinomial(n, np.ones(n) / n, size=NBOOT).astype(float)
        plac.append(bool(float(np.percentile(cnt @ d / n, 2.5)) > 0))
    print(f"\nPLACEBO           comparator vs itself admitted: {plac} (must be all False)")

    def rate(a, c, N):
        return next(r["rate"] for r in rows if r["arm"] == a and r["comparator"] == c
                    and r["N"] == N)

    pos_hi = all(rate("oracle_k4", c, N) == 1.0 for c in legit for N in NS)
    pos_lo = all(rate("random_k4_s0", c, N) == 0.0 for c in legit for N in NS)
    det = all(rate(a, c, 968) in (0.0, 1.0) for a in ARMS for c in legit)
    print(f"POSITIVE CONTROL  oracle_k4 admitted at 1.0 everywhere: {pos_hi}   "
          f"random_k4_s0 at 0.0 everywhere: {pos_lo}")
    print(f"NEGATIVE CONTROL  N=968 verdicts identical across seeds (rate 0 or 1): {det}")
    ctrl_ok = pos_hi and pos_lo and det and not any(plac)

    core_ok = all(rate("coval_core", c, N) >= 0.95 for c in legit for N in NS if N >= 120)
    if not ctrl_ok:
        world = "UNVERIFIED — a control failed; neither world is excluded by this run"
    elif core_ok:
        world = "A THE INSTANCE IS SAFE — admitted at ≥0.95 for every N ≥ 120; world B is dead"
    else:
        cross = {c: next((N for N in NS if rate("coval_core", c, N) >= 0.5), None) for c in legit}
        world = (f"B ADMISSION IS A POWER FACT — coval_core's rate crosses 0.5 between grid points "
                 f"{cross}, against registered N* "
                 f"{ {c: round(nstar[('coval_core', c)]) for c in legit} }")
    print(f"\n⭐ {world}")

    out = HERE / "results" / "instance_power.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_prompts=n, nboot=NBOOT, z=Z, Ns=list(NS), seeds=list(SEEDS), arms=list(ARMS),
        comparators=legit,
        registered_nstar={f"{a}|{c}": (None if nstar[(a, c)] == float("inf") else nstar[(a, c)])
                          for a in ARMS for c in legit},
        controls={"oracle_always_admitted": pos_hi, "random_never_admitted": pos_lo,
                  "deterministic_at_full_n": det, "placebo_self": plac, "all_ok": ctrl_ok},
        cells_tested=len(rows), rows=rows, world=world,
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}   cells {len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
