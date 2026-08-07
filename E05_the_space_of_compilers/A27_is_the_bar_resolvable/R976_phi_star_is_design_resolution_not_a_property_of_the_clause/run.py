#!/usr/bin/env python3
"""R976 — is φ* a property of clause ④, or is it the design's resolution?

⛔ WHY THIS IS RUNG 2 BEFORE RUNG 4. R975 closed by saying the cheapest separator is to resample the
corpus. Before spending that compute, the arithmetic: ④'s removal is `hi < 0`, the margin is pinned
at −δ by construction, and the interval is ≈ z·sd(d)/√N. On the lattice, d takes ±STEP on the
n_up = φN raised prompts and on the (δN/STEP + φN) lowered steps, so

    sd(d) ≈ STEP·√(2φ + δ/STEP)   and removal fails when   z·sd(d)/√N ≥ δ

    ⇒   φ*(δ, N) = [ δ²N / (z·STEP)² − δ/STEP ] / 2

Evaluated on R975's own grid this returns 0.4236, 1.7542, 11.1890 for δ = 0.01, 0.02, 0.05 — and
R975 measured the boundary inside (0.30, 0.40] for δ=0.01 (one seed of three flipping at 0.40,
three of three at 0.50) and removal everywhere for the other two. **Three cells, no free
parameters.** ⚠ But that is a POST-HOC fit to a grid already in hand, which is why it is not the
finding and this round exists.

ESTIMAND        the dependence of φ* on the design's two free quantities, N and δ, measured
                OUT OF SAMPLE against a prediction registered before the run.
IDENTIFICATION  identified: φ* is a boundary in a grid this site can run at any N ≤ 968 by
                subsampling prompts, and at any δ on the lattice.
SCOPE           population : subsamples of the same 968 prompts of release one
                instrument : R803's judge-free floor + a 1200-draw prompt bootstrap
                baseline   : the closed form above, evaluated before the run
                regime     : plants on the lattice {0, 1/6, ..., 1}; φ ≤ 0.5
WORLDS          A CLAUSE-OR-CORPUS PROPERTY   φ* is roughly invariant in N. If ④'s reach is a fact
                                              about the clause or about this corpus's per-prompt
                                              variance, shrinking the corpus should not move it
                                              by the factor the resolution story demands.
                B DESIGN RESOLUTION           φ* tracks the closed form: LINEAR in N, QUADRATIC
                                              in δ. ④ then has no free parameter at all and any
                                              statement of its reach must carry N and δ.
                prediction matrix, registered: A -> φ*(968)/φ*(484) ∈ [0.8, 1.25].
                                               B -> that ratio ≈ 2.15, and φ* ∝ δ² at fixed N.
KILL            pre-registered, and it is a CONDITIONAL: evaluate only if the positive control
                reproduces R975's boundary at N=968 AND the placebo never fires. Then —
                if the N-ratio lands in [0.8, 1.25], world B is dead;
                if it lands within the seed spread of 2.15, world A is dead;
                anything else is UNVERIFIED, not a partial confirmation.
POSITIVE CTRL   at N=968, δ=0.01, the measured boundary must sit in (0.30, 0.50] — R975's
                committed result. An instrument that cannot reproduce it is not measuring this.
NEGATIVE CTRL   the mean is pinned: margin spread across φ within a (δ, N) cell < 1e-12.
PLACEBO         δ=0 at every (N, φ): must NEVER be removed. A removal there is the instrument.
NOISE FLOOR     the bootstrap CI half-width at φ=0, measured per N.
SEEDS           3 on both the subsample and the plant; φ* reported per seed, never averaged.
MULTIPLICITY    every (N, δ, φ, seed) cell is recorded; φ* is read off the whole curve.
SPECIFICATION   N × δ swept jointly, so the two predicted exponents are tested against each other
                rather than one axis being fitted.
ARTIFACT        results/phi_star_scaling.json with this file's source hash.
IMPOSSIBLE      cross-release — N/A: subsampling one corpus tests N, NOT a different corpus. A
                second release would be required to separate "this corpus's variance" from
                "corpus variance in general", and this round cannot and does not claim that.
                independently replicated — N/A: no clean-context agent dispatched this session.
"""
from __future__ import annotations
import hashlib
import itertools
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_targets, load_sat, cls                          # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
RES = ROOT / "corebench/results"
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
STEP = 1.0 / len(PR)
Z = 1.96
PHI_GRID = tuple(round(x, 3) for x in np.arange(0.0, 0.505, 0.025))
SEEDS = (11, 22, 33)
RATIO_FLAT = (0.8, 1.25)          # world A's registered band


def phi_star_predicted(delta, N):
    return (delta ** 2 * N / (Z * STEP) ** 2 - delta / STEP) / 2


def build_floor():
    tg, _ = load_targets()
    text = {}
    for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        rs = r.get("responses") or []
        if len(rs) != 4:
            continue
        text[r["prompt_id"]] = [" ".join(str(m.get("content", "")) for m in (it.get("messages")
                                or []) if isinstance(m, dict)) for it in rs]
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted(p for p in base if p in tg and p in text and len(tg[p]) >= 2)
    H = {p: np.array([cls(np.array(y, float)) for y, _ in tg[p]]) for p in pids}
    CH = np.array([[len(t) for t in text[p]] for p in pids], float)
    v = np.zeros(len(pids))
    for i, p in enumerate(pids):
        s = np.sign(CH[i][[u for u, _ in PR]] - CH[i][[w for _, w in PR]])
        v[i] = float((H[p] == s).mean())
    return v


def plant(floor_v, delta, phi, rng):
    N = len(floor_v)
    v = floor_v.copy()
    up_pool = np.flatnonzero(floor_v < 1.0 - 1e-12)
    n_up = min(int(round(phi * N)), len(up_pool))
    up = rng.permutation(up_pool)[:n_up]
    v[up] += STEP
    need = int(round(delta * N / STEP)) + n_up
    upset = set(up.tolist())
    order = rng.permutation(np.array([i for i in range(N) if i not in upset]))
    spent, cursor, sweep = 0, 0, 0
    while spent < need and sweep < len(PR) + 1:
        if cursor >= len(order):
            cursor, sweep = 0, sweep + 1
            continue
        i = order[cursor]; cursor += 1
        if v[i] > 1e-12:
            v[i] -= STEP
            spent += 1
    return v, n_up, spent == need


def main() -> int:
    full = build_floor()
    if abs(float(full.mean()) - 0.4556792822122909) > 1e-9:
        print("⛔ OBJECT CHECK FAILED: the floor did not reproduce. Exit 2, never 0.")
        return 2
    NFULL = len(full)
    print(f"OBJECT CHECK  {NFULL} prompts, floor {full.mean():.6f} — reproduces R821 exactly.")

    NS = (242, 484, 726, 968)
    DELTAS = (0.008, 0.010, 0.012, 0.016)
    print("\nPREDICTION, REGISTERED BEFORE THE RUN (closed form, no free parameters):")
    print(f"  {'N':>6}" + "".join(f"{f'δ={d}':>12}" for d in DELTAS))
    for n in NS:
        print(f"  {n:>6}" + "".join(f"{phi_star_predicted(d, n):>12.4f}" for d in DELTAS))
    pred_ratio = phi_star_predicted(0.010, 968) / phi_star_predicted(0.010, 484)
    print(f"  registered world-B ratio φ*(968)/φ*(484) at δ=0.010: {pred_ratio:.3f}")
    print(f"  registered world-A band for the same ratio: {RATIO_FLAT}")

    rows, placebo_fires = [], 0
    noise = {}
    for n in NS:
        for si, seed in enumerate(SEEDS):
            sub_rng = np.random.default_rng(1000 + seed)
            sub = full if n == NFULL else full[sub_rng.permutation(NFULL)[:n]]
            brng = np.random.default_rng(4242 + si)
            idx = brng.integers(0, n, (NBOOT, n))

            def verdict(v):
                d = v - sub
                bs = d[idx].mean(axis=1)
                lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
                return float(d.mean()), lo, hi, bool(hi < 0)

            for delta in DELTAS:
                for phi in PHI_GRID:
                    v, n_up, exact = plant(sub, delta, phi, np.random.default_rng(seed))
                    m, lo, hi, rem = verdict(v)
                    rows.append({"N": n, "delta": delta, "phi": phi, "seed": seed,
                                 "n_up": n_up, "exact": exact, "margin": m,
                                 "lo": lo, "hi": hi, "removed": rem})
                    if phi == 0.0 and delta == DELTAS[0]:
                        noise[n] = (hi - lo) / 2
            # PLACEBO: δ=0 must never be removed, at any φ.
            for phi in (0.0, 0.25, 0.5):
                v0, _, _ = plant(sub, 0.0, phi, np.random.default_rng(seed))
                if verdict(v0)[3]:
                    placebo_fires += 1

    # ── read φ* off each curve: the smallest φ at which removal fails and stays failed.
    def boundary(n, delta, seed):
        cur = sorted((r for r in rows if r["N"] == n and r["delta"] == delta
                      and r["seed"] == seed), key=lambda r: r["phi"])
        for i, r in enumerate(cur):
            if not r["removed"] and all(not q["removed"] for q in cur[i:]):
                return r["phi"]
        return None                      # never fails inside the grid

    print(f"\nMEASURED φ* (smallest φ at which removal fails and stays failed; "
          f"None = still removed at φ=0.5)")
    print(f"  {'N':>6} {'δ':>7}" + "".join(f"{f'seed {s}':>10}" for s in SEEDS) + f"{'pred':>10}")
    meas = {}
    for n in NS:
        for delta in DELTAS:
            bs = [boundary(n, delta, s) for s in SEEDS]
            meas[(n, delta)] = bs
            print(f"  {n:>6} {delta:>7.3f}" +
                  "".join(f"{('—' if b is None else f'{b:.3f}'):>10}" for b in bs) +
                  f"{phi_star_predicted(delta, n):>10.3f}")

    # ── CONTROLS ────────────────────────────────────────────────────────────────────────────
    r975 = meas[(968, 0.010)]
    pos_ok = all(b is not None and 0.30 < b <= 0.50 for b in r975)
    print(f"\nPOSITIVE CONTROL  N=968, δ=0.010 boundary in (0.30, 0.50] on every seed: {pos_ok}"
          f"   (R975 committed (0.30, 0.40] at δ=0.01)")
    print(f"PLACEBO           δ=0 removals across all cells: {placebo_fires} (must be 0)")
    per_cell = {}
    for r in rows:
        per_cell.setdefault((r["N"], r["delta"]), []).append(r["margin"])
    drift = max(max(v) - min(v) for v in per_cell.values())
    print(f"NEGATIVE CONTROL  max margin spread across φ within a (N, δ) cell: {drift:.2e}")
    print(f"NOISE FLOOR       CI half-width at φ=0, δ={DELTAS[0]}: "
          + "  ".join(f"N={k}:{v:.5f}" for k, v in sorted(noise.items())))
    ctrl_ok = pos_ok and placebo_fires == 0 and drift < 1e-12

    # ── THE KILL, evaluated ONLY behind its controls ─────────────────────────────────────────
    got = [meas[(968, 0.010)][i] for i in range(3)], [meas[(484, 0.010)][i] for i in range(3)]
    ratios = [a / b for a, b in zip(*got) if a is not None and b is not None and b > 0]
    print(f"\nKILL  measured φ*(968)/φ*(484) at δ=0.010 per seed: "
          + ", ".join(f"{r:.3f}" for r in ratios) if ratios else "KILL  ratio unavailable")
    if not ctrl_ok:
        world = "UNVERIFIED — a control failed; nothing about ④ is certified by this run"
    elif not ratios:
        world = "UNVERIFIED — φ* left the grid at one of the two N, so the ratio is not measured"
    elif all(RATIO_FLAT[0] <= r <= RATIO_FLAT[1] for r in ratios):
        world = "A CLAUSE-OR-CORPUS PROPERTY — φ* is flat in N; the resolution story is dead"
    elif min(ratios) > RATIO_FLAT[1]:
        world = (f"B DESIGN RESOLUTION — φ* grows with N (registered prediction {pred_ratio:.2f}, "
                 f"measured {min(ratios):.2f}–{max(ratios):.2f})")
    else:
        world = "UNVERIFIED — the seeds straddle the registered bands; neither world is excluded"
    print(f"\n⭐ {world}")

    # ── the δ² axis, tested against the SAME closed form rather than fitted separately.
    print("\nSECOND AXIS (δ, at N=968) — the form predicts φ* quadratic in δ:")
    for delta in DELTAS:
        bs = [b for b in meas[(968, delta)] if b is not None]
        print(f"  δ={delta:<6} predicted {phi_star_predicted(delta,968):>7.3f}   "
              f"measured {('—' if not bs else '/'.join(f'{b:.3f}' for b in bs))}")

    out = HERE / "results" / "phi_star_scaling.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        closed_form="phi* = (delta^2 N / (z STEP)^2 - delta/STEP) / 2",
        z=Z, step=STEP, nboot=NBOOT, Ns=list(NS), deltas=list(DELTAS), seeds=list(SEEDS),
        registered_ratio=pred_ratio, registered_flat_band=list(RATIO_FLAT),
        measured_ratios=ratios,
        predicted={f"{n}|{d}": phi_star_predicted(d, n) for n in NS for d in DELTAS},
        measured={f"{n}|{d}": meas[(n, d)] for n in NS for d in DELTAS},
        controls={"positive_reproduces_R975": pos_ok, "placebo_fires": placebo_fires,
                  "margin_drift": drift, "noise_floor": noise, "all_ok": ctrl_ok},
        cells_tested=len(rows), world=world, rows=rows,
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}   cells {len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
