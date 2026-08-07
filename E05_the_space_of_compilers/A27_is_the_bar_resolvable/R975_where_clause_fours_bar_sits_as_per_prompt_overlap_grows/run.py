#!/usr/bin/env python3
"""R975 — clause ④'s bar as per-prompt overlap grows, at a FIXED mean deficit.

⛔ WHY, AND WHAT THE PRIOR ROUND'S CLOSING SENTENCE GOT WRONG ABOUT ITSELF. Commit 54bab0e3 closed
with: *"The plants were built by subtracting a CONSTANT from the floor, so they are below it
uniformly. Whether ④ removes an arm below the floor on average but ABOVE it on some prompts is not
measured."* Read from the object (R821 run.py:146-152), the plant is `v[hurt] = 0.0` on a random
subset — it ZEROES a fraction and leaves every other prompt EXACTLY EQUAL to the floor. Not a
constant subtraction, and not uniform. So the sentence mis-describes its own round twice, and the
gap it names is narrower than it says: prompts strictly ABOVE the floor were never built, and
"equal to" is not "above".

ESTIMAND        at a FIXED mean deficit δ below the judge-free floor, the per-prompt overlap
                fraction φ — the share of prompts on which the planted arm is STRICTLY ABOVE the
                floor — at which clause ④ stops removing it.
IDENTIFICATION  ⛔ PARTIALLY, AND THE PART THAT IS NOT IS A DERIVATION, NOT A MEASUREMENT.
                ④'s statistic is `d.mean()` with `d = v - floor_v`. Holding `v.mean()` fixed
                holds `d.mean()` fixed EXACTLY — it could not have come out otherwise, so the
                invariance of the point estimate is algebra and is labelled as such. What is
                identified and measured is the BOOTSTRAP INTERVAL's upper end as φ grows, since
                `var(d)` is free to move while the mean is pinned. Removal is `hi < 0`, so the
                whole question is whether ④'s power is mean-determined or variance-limited.
SCOPE           population : 968 prompts of release one, the same set R803/R821 scored
                instrument : R803's judge-free floor (characters, longer-is-better), rebuilt from
                             data/comparisons.jsonl, and a 1200-draw prompt bootstrap
                baseline   : the floor itself, and R821's zeroing ladder as the positive control
                regime     : plants on the CONSTRUCTIBLE lattice {0, 1/6, ..., 1} — a per-prompt
                             A2 is agreement over 6 pairs, so an off-lattice plant is an object no
                             scoring function can emit and would not test the clause
WORLDS          A MEAN-DETERMINED  ④ removes the arm at every φ; overlap is irrelevant and the
                                   clause bites on the corpus mean alone.
                B VARIANCE-LIMITED there is a φ* beyond which `hi >= 0` and the SAME mean deficit
                                   survives, so ④'s exclusion power depends on per-prompt shape
                                   and the clause's binding region is narrower than stated.
                prediction matrix: A -> `removed` True across the whole φ grid at every δ.
                                   B -> a monotone boundary in φ, at a δ-dependent φ*.
KILL            pre-registered: if `removed` is True in EVERY cell of the grid, world B is dead
                and ④'s bar is mean-determined on this release. If any δ>0 cell survives at φ=0,
                the instrument is broken and the round reports UNVERIFIED, not world B.
POSITIVE CTRL   reproduce R821's ladder on this same floor: δ ∈ {0.01, 0.05, 0.10} zeroing plants
                all removed, δ=0 kept. An instrument that cannot reproduce a committed positive
                result is not measuring this clause.
NEGATIVE CTRL   the derivation, checked numerically: `d.mean()` must be constant across φ to
                machine precision at fixed δ. If it drifts, the construction leaked and every
                comparison across φ is confounded by the mean.
PLACEBO         the floor against itself must give margin exactly 0 and must NOT be removed.
NOISE FLOOR     the bootstrap CI half-width at φ=0, measured, not assumed.
SEEDS           3 seeds on the prompt selection; the grid is reported per seed, never averaged.
MULTIPLICITY    every cell of δ × φ × seed is reported, survivors and non-survivors alike.
ARTIFACT        results/overlap_bar.json with this file's source hash.
IMPOSSIBLE      cross-dataset / cross-release — N/A: one release. Would require a second corebench
                with human targets on the same 4-response format.
                independently replicated — N/A: no clean-context agent dispatched this session.
                Would require a second author given the question and not this construction.
"""
from __future__ import annotations
import hashlib
import itertools
import json
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
STEP = 1.0 / len(PR)              # the lattice: 6 pairs, so a per-prompt A2 moves in sixths
DELTAS = (0.01, 0.02, 0.05)
PHIS = (0.0, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50)
SEEDS = (11, 22, 33)


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
    # ⛔ THE POPULATION IS NOT "THE RELEASE". R821 intersects with the prompts a scored arm
    #    actually covers (`sat_random_k4_s0.npz`); dropping that filter gave 1,078 prompts and a
    #    floor of 0.451517 instead of 968 and 0.455679. The object check caught it on first run --
    #    which is the only reason this round is not comparing a clause against a different corpus
    #    than every number it cites.
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
    """An arm on the constructible lattice: φ·N prompts pushed STRICTLY ABOVE the floor, the mean
    deficit restored to exactly δ by stepping other prompts DOWN. Returns (v, n_up, n_down, ok)."""
    N = len(floor_v)
    v = floor_v.copy()
    up_pool = np.flatnonzero(floor_v < 1.0 - 1e-12)          # can only rise where there is headroom
    n_up = min(int(round(phi * N)), len(up_pool))
    up = rng.permutation(up_pool)[:n_up]
    v[up] += STEP
    # net down-steps needed so that mean(v) == mean(floor_v) - delta
    need = int(round(delta * N / STEP)) + n_up
    down_pool = np.array([i for i in range(N) if i not in set(up.tolist())])
    order = rng.permutation(down_pool)
    spent, cursor, sweep = 0, 0, 0
    while spent < need and sweep < len(PR) + 1:
        if cursor >= len(order):
            cursor, sweep = 0, sweep + 1
            continue
        i = order[cursor]; cursor += 1
        if v[i] > 1e-12:
            v[i] -= STEP
            spent += 1
    return v, n_up, spent, spent == need


def main() -> int:
    floor_v = build_floor()
    N = len(floor_v)
    FLOOR = float(floor_v.mean())
    print(f"POPULATION  {N} prompts · judge-free floor {FLOOR:.6f} "
          f"(R821 committed 0.4556792822122909)")
    if abs(FLOOR - 0.4556792822122909) > 1e-9:
        print("⛔ OBJECT CHECK FAILED: the floor did not reproduce. Exit 2, never 0.")
        return 2
    print("  OBJECT CHECK  the floor reproduces R821's committed value exactly.")

    rng = np.random.default_rng(1234)
    idx = rng.integers(0, N, (NBOOT, N))

    def verdict(v):
        d = v - floor_v
        bs = d[idx].mean(axis=1)
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        return float(d.mean()), lo, hi, bool(hi < 0)

    # ── POSITIVE CONTROL: reproduce R821's zeroing ladder on this floor.
    print("\nPOSITIVE CONTROL — R821's zeroing ladder, reproduced")
    ladder = {}
    for delta in (0.10, 0.05, 0.01, 0.0):
        v = floor_v.copy()
        if delta > 0:
            k = int(N * delta / max(FLOOR, 1e-9))
            v[rng.permutation(N)[:min(k, N)]] = 0.0
        m, lo, hi, rem = verdict(v)
        ladder[str(delta)] = {"margin": m, "lo": lo, "hi": hi, "removed": rem}
        print(f"  delta={delta:<5} margin {m:+.4f} [{lo:+.4f}, {hi:+.4f}]  ④ removes: {rem}")
    pos_ok = all(ladder[k]["removed"] for k in ("0.1", "0.05", "0.01")) and \
        not ladder["0.0"]["removed"]
    print(f"  -> reproduces R821: {pos_ok}")

    # ── PLACEBO: the floor against itself.
    pm, plo, phi_, prem = verdict(floor_v.copy())
    print(f"\nPLACEBO  floor vs itself: margin {pm:+.1e}  removed {prem}  "
          f"(must be 0.0 and False)")
    placebo_ok = abs(pm) < 1e-12 and not prem

    # ── NOISE FLOOR at φ=0.
    _, nlo, nhi, _ = verdict(plant(floor_v, DELTAS[0], 0.0, np.random.default_rng(11))[0])
    print(f"NOISE FLOOR  CI half-width at δ={DELTAS[0]}, φ=0: {(nhi-nlo)/2:.6f}")

    if not (pos_ok and placebo_ok):
        print("\n⛔ a control failed; this round certifies nothing about clause ④. Exit 2.")
        return 2

    # ── THE GRID. Every cell reported, survivors and non-survivors alike.
    print(f"\nGRID  δ × φ × seed = {len(DELTAS)}×{len(PHIS)}×{len(SEEDS)} = "
          f"{len(DELTAS)*len(PHIS)*len(SEEDS)} cells")
    rows, mean_drift = [], []
    for delta in DELTAS:
        print(f"\n  δ = {delta}   (mean deficit held FIXED — the point estimate is a DERIVATION)")
        print(f"    {'φ':>6} {'seed':>5} {'n_up':>6} {'margin':>10} {'lo':>10} {'hi':>10}  removed")
        for phi in PHIS:
            for seed in SEEDS:
                v, n_up, n_down, exact = plant(floor_v, delta, phi, np.random.default_rng(seed))
                m, lo, hi, rem = verdict(v)
                n_above = int((v > floor_v + 1e-12).sum())
                rows.append({"delta": delta, "phi": phi, "seed": seed, "n_up": n_up,
                             "n_strictly_above": n_above, "n_down_steps": n_down,
                             "construction_exact": exact, "margin": m, "lo": lo, "hi": hi,
                             "removed": rem})
                mean_drift.append(m)
                print(f"    {phi:>6.2f} {seed:>5} {n_up:>6} {m:>+10.5f} {lo:>+10.5f} "
                      f"{hi:>+10.5f}  {rem}")

    # ── NEGATIVE CONTROL: the derivation, checked numerically.
    # ⛔ THE FIRST VERSION OF THIS CONTROL FAILED FOR ITS OWN REASONS, which is §4's dominant mode.
    #    It compared the ACHIEVED margin against the NOMINAL −δ and demanded 1e-9. The lattice makes
    #    that impossible: δ·N/STEP = 0.05·968·6 = 290.40 steps, and an arm can only take 290, so the
    #    achieved deficit is 0.04993113 and the "drift" was 6.89e-05 — matching the arithmetic to
    #    the digit. The control's two sides were not the same object.
    #    ⭐ The claim is about φ, so the control must be about φ: WITHIN each δ, the margin must not
    #    move as φ grows. That is the confound the round has to exclude, and it is checkable exactly.
    per_delta = {}
    for r in rows:
        per_delta.setdefault(r["delta"], []).append(r["margin"])
    drift = max(max(v) - min(v) for v in per_delta.values())
    achieved = {d: round(d * N / STEP) * STEP / N for d in DELTAS}
    print(f"\nNEGATIVE CONTROL (the derivation)  max spread of margin ACROSS φ, within a δ: "
          f"{drift:.2e}")
    for d in DELTAS:
        print(f"    δ nominal {d}  ->  achieved {achieved[d]:.8f} "
              f"(lattice: {d*N/STEP:.2f} steps are not an integer)")
    deriv_ok = drift < 1e-12
    print(f"  the mean is pinned by construction: {deriv_ok}   "
          f"⚠ this is ALGEBRA, not evidence — only the interval was free to move.")

    exact_all = all(r["construction_exact"] for r in rows)
    n_removed = sum(r["removed"] for r in rows)
    print(f"\nCONSTRUCTION  every cell hit its target deficit exactly: {exact_all}")
    print(f"CELLS         {n_removed} of {len(rows)} removed by ④")

    if not (deriv_ok and exact_all):
        world = "UNVERIFIED — the construction leaked, so φ is confounded with the mean"
    elif n_removed == len(rows):
        world = "A MEAN-DETERMINED — ④ removes at every overlap level; world B is dead"
    elif any(r["removed"] is False and r["phi"] == 0.0 for r in rows):
        world = "UNVERIFIED — a δ>0 cell survived at φ=0, so the instrument, not the clause, moved"
    else:
        world = "B VARIANCE-LIMITED — the same mean deficit survives past some φ*"
    print(f"\n⭐ {world}")

    out = HERE / "results" / "overlap_bar.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_prompts=N, floor=FLOOR, lattice_step=STEP, nboot=NBOOT,
        positive_control_reproduces_R821=pos_ok, positive_control=ladder,
        placebo={"margin": pm, "removed": prem, "ok": placebo_ok},
        noise_floor_halfwidth=(nhi - nlo) / 2,
        derivation_max_mean_drift=drift, derivation_ok=deriv_ok,
        construction_exact_all=exact_all,
        cells_tested=len(rows), cells_removed=n_removed, rows=rows, world=world,
        r821_plant_as_read_from_source="v[hurt] = 0.0 on a random subset; the rest EQUAL the floor",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
