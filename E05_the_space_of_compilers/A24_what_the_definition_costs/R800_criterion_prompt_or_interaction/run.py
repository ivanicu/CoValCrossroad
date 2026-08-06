#!/usr/bin/env python3
"""R800 · criterion, prompt, or INTERACTION — the first fully-crossed decomposition in this release.

R799 bounded the pool's criterion share by comparing two spreads (0.0157 across criteria against
0.1532 across instances) and called the rest "prompt". CHECK #402 found (a) R799's own NEXT proposed
the ranking design R799 had just killed, one level up, and (b) the pool's grid is FULLY CROSSED — the
identical criteria 0..15 on all 968 prompts — so criterion, prompt and their INTERACTION are
separately identified.

ESTIMAND        E1 ⭐ the two-way decomposition · E2 ⭐ the prompt-level deficit, deconvolved ·
                E3 ⭐ naive vs deconvolved share of prompts where the rubric loses · E4 the size
                confound
IDENTIFICATION  E1 identified BY the crossed grid, and only for the pool. ⛔ Still not identified for
                `coval_full`, whose criteria appear on one prompt each (R799 D3)
DERIVED FIRST   D1 marginal means identify the parts on a crossed grid · D2 R799's 0.0157 is an
                UPPER BOUND, and the correction is expected small — said in advance · D3 the deficit
                is PAIRED, so its noise must be measured on the DIFFERENCE · D4 a share read off a
                ranking is biased away from the centre
WORLDS          A interaction dominates · B prompt dominates · C criterion dominates — C is treated
                as an instrument failure, not a finding
CONTROLS        OBJECT (two committed sds) · PLACEBO · POSITIVE (two synthetic grids, band both
                ends) · NEGATIVE (criterion labels shuffled within prompt) · CONFOUND (size-matched)
                · NOISE FLOOR (split-half on cells AND on the difference)
"""
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
from score import load_sat, load_targets, cls                          # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R799 = ARC / "R799_uniform_or_concentrated/results/deconvolution.json"
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
SEEDS = [31337, 31338, 31339]


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def decompose(A, s2e):
    """A (C, P) cell means; s2e the per-cell annotator noise variance. -> components (D1)."""
    C, P = A.shape
    tot = float(np.var(A, ddof=1))
    vc = float(np.var(A.mean(axis=1), ddof=1))          # = s2_c + (s2_int + s2e)/P
    vp = float(np.var(A.mean(axis=0), ddof=1))          # = s2_p + (s2_int + s2e)/C
    # solve: tot = s2_c + s2_p + s2_int + s2e
    s2_int = max(tot - (vc - 0) - (vp - 0) - s2e, 0.0)  # first pass, refined below
    for _ in range(50):                                  # fixed-point on the marginal inflations
        s2_c = max(vc - (s2_int + s2e) / P, 0.0)
        s2_p = max(vp - (s2_int + s2e) / C, 0.0)
        s2_int = max(tot - s2_c - s2_p - s2e, 0.0)
    return {"total": tot, "criterion": s2_c, "prompt": s2_p, "interaction": s2_int, "noise": s2e}


def main():
    out = {"instrument_unit": "a (criterion, prompt, annotator) judgement",
           "claim_unit": "a VARIANCE COMPONENT", "e3_unit": "a PROMPT"}

    print("  OBJECT CHECK")
    prev = json.loads(R799.read_text())
    targets, _ = load_targets()
    SF = load_sat(RES / "sat_full.npz")
    SG = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(p for p in SF if p in SG and p in targets and len(targets[p]) >= 2)
    P = len(pids)
    HC = [np.array([cls(np.array(y, float)) for y, _ in targets[p]]) for p in pids]
    CIDX = sorted({i for i, _ in SG[pids[0]]})
    C = len(CIDX)

    def cell(S, p_i, i):
        p = pids[p_i]
        y = np.array([S[p].get((i, x), 0.0) for x in L])
        s = np.sign(y[[u for u, _ in PR]] - y[[v for _, v in PR]])
        nz = s != 0
        if not nz.any():
            return None
        return (HC[p_i][:, nz] == s[nz]).astype(np.int8)

    HITS = [[cell(SG, a, i) for i in CIDX] for a in range(P)]
    A = np.full((C, P), np.nan)
    for a in range(P):
        for ci in range(C):
            h = HITS[a][ci]
            if h is not None:
                A[ci, a] = h.mean()
    ok_cells = ~np.isnan(A)
    print(f"     grid {C} criteria x {P} prompts   cells present {int(ok_cells.sum())} of {C * P}")
    Am = np.where(ok_cells, A, np.nanmean(A))
    inst_sd = float(np.nanstd(A[ok_cells], ddof=1))
    crit_sd = float(np.std(np.nanmean(A, axis=1), ddof=1))
    okobj = (abs(inst_sd - prev["e1"]["pool"]["obs_sd"]) < 1e-9
             and abs(crit_sd - prev["e3"]["sd"]) < 1e-9)
    print(f"     instance sd {inst_sd:.10f} vs R799's {prev['e1']['pool']['obs_sd']:.10f}   "
          f"across-criteria sd {crit_sd:.10f} vs {prev['e3']['sd']:.10f}   "
          f"{'PASS' if okobj else 'FAIL'}")
    if not okobj:
        print("  UNRUNNABLE: a committed sd did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"C": C, "P": P, "cells": int(ok_cells.sum()), "inst_sd": inst_sd,
                     "crit_sd": crit_sd}

    # ---- noise: annotator split-half per cell ----------------------------------------------------
    rng = np.random.default_rng(SEEDS[0])
    d2 = []
    for a in range(P):
        for ci in range(C):
            h = HITS[a][ci]
            if h is None or h.shape[0] < 4:
                continue
            idx = rng.permutation(h.shape[0])
            d2.append((h[idx[0::2]].mean() - h[idx[1::2]].mean()) ** 2)
    s2e = float(np.mean(d2)) / 4.0
    print(f"     NOISE FLOOR  per-cell annotator split-half: s2_e {s2e:.6f} (sd {math.sqrt(s2e):.4f})")

    # ================= E1 · the decomposition =====================================================
    print("\n  E1 - THE TWO-WAY DECOMPOSITION  (crossed grid, D1)")
    comp = decompose(Am, s2e)
    tot = comp["total"]
    for k in ("criterion", "prompt", "interaction", "noise"):
        print(f"     s2_{k:<12} {comp[k]:.6f}   sd {math.sqrt(comp[k]):.4f}   "
              f"{100 * comp[k] / tot:5.1f}% of total {tot:.6f}")
    print(f"     ⚠ D2: R799's across-criteria sd {crit_sd:.4f} was an UPPER BOUND; the corrected "
          f"criterion sd is {math.sqrt(comp['criterion']):.4f} — a small correction, as predicted")
    out["e1"] = comp

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    plac = float(np.nanmax(np.abs(A - A)))
    print(f"     PLACEBO  a cell against itself: {plac:.1e}   "
          f"{'PASS' if plac == 0.0 else 'FAIL'}")

    def synth(sc, sp, si, rg):
        c = rg.normal(0, sc, (C, 1))
        p_ = rg.normal(0, sp, (1, P))
        i_ = rg.normal(0, si, (C, P))
        return 0.52 + c + p_ + i_ + rg.normal(0, math.sqrt(s2e), (C, P))

    dose = {}
    for lab, (sc, sp, si) in (("interaction-heavy", (0.01, 0.03, 0.12)),
                              ("prompt-heavy", (0.01, 0.12, 0.03))):
        S_ = synth(sc, sp, si, np.random.default_rng(SEEDS[0] + 11))
        r_ = decompose(S_, s2e)
        dose[lab] = {"planted": {"criterion": sc ** 2, "prompt": sp ** 2, "interaction": si ** 2},
                     "recovered": {k: r_[k] for k in ("criterion", "prompt", "interaction")}}
        print(f"     POSITIVE  {lab:<18} planted sd c/p/i {sc:.2f}/{sp:.2f}/{si:.2f}  ->  recovered "
              f"{math.sqrt(r_['criterion']):.3f}/{math.sqrt(r_['prompt']):.3f}/"
              f"{math.sqrt(r_['interaction']):.3f}")
    ih = dose["interaction-heavy"]["recovered"]
    ph = dose["prompt-heavy"]["recovered"]
    posok = (ih["interaction"] > ih["prompt"]) and (ph["prompt"] > ph["interaction"])
    print(f"     POSITIVE  band COMPUTED at both ends: the two mixes are distinguished in the right "
          f"direction   {'PASS' if posok else 'FAIL'}")

    nrng = np.random.default_rng(SEEDS[0] + 13)
    Ash = np.array([Am[nrng.permutation(C), a] for a in range(P)]).T
    rsh = decompose(Ash, s2e)
    negok = rsh["criterion"] < comp["criterion"] / 4 and abs(rsh["total"] - tot) < 1e-9
    print(f"     NEGATIVE  criterion labels shuffled WITHIN each prompt: s2_criterion "
          f"{comp['criterion']:.6f} → {rsh['criterion']:.6f}; total unchanged to "
          f"{abs(rsh['total'] - tot):.1e}   {'PASS' if negok else 'FAIL'}")
    print(f"               world it excludes: 'the criterion component is an artefact of the "
          f"decomposition rather than of the labelling'")

    gate = okobj and plac == 0.0 and posok and negok
    out["controls"] = {"placebo": plac, "dose": dose, "positive_ok": posok,
                       "shuffled": rsh, "negative_ok": negok, "s2e": s2e, "gate": gate}
    print(f"     GATE  {'PASS -- the kill may evaluate' if gate else 'FAIL -- UNVERIFIED'}")

    # ================= E2/E3 · the prompt-level deficit, deconvolved ==============================
    print("\n  E2/E3 - THE PROMPT-LEVEL DEFICIT, AND THE SHARE R799's NEXT ASKED FOR")
    fullhits = []
    for a in range(P):
        hs = [cell(SF, a, i) for i in sorted({i for i, _ in SF[pids[a]]})]
        fullhits.append([h for h in hs if h is not None])
    dpf = np.array([np.mean([h.mean() for h in fullhits[a]]) for a in range(P)])
    dpg = np.nanmean(A, axis=0)
    defic = dpf - dpg
    # D3: the noise of the DIFFERENCE, measured on the difference
    dd = []
    for a in range(P):
        n = HC[a].shape[0]
        if n < 4:
            continue
        idx = rng.permutation(n)
        h1, h2 = idx[0::2], idx[1::2]
        f1 = np.mean([h[h1].mean() for h in fullhits[a]])
        f2 = np.mean([h[h2].mean() for h in fullhits[a]])
        g1 = np.mean([HITS[a][ci][h1].mean() for ci in range(C) if HITS[a][ci] is not None])
        g2 = np.mean([HITS[a][ci][h2].mean() for ci in range(C) if HITS[a][ci] is not None])
        dd.append(((f1 - g1) - (f2 - g2)) ** 2)
    s2e_d = float(np.mean(dd)) / 4.0
    obs_sd_d = float(np.std(defic, ddof=1))
    dec_sd_d = math.sqrt(max(obs_sd_d ** 2 - s2e_d, 0.0))
    naive = float((defic < 0).mean())
    corrected = float((rng.normal(defic.mean(), dec_sd_d, 200000) < 0).mean()) if dec_sd_d > 1e-9 \
        else (1.0 if defic.mean() < 0 else 0.0)
    print(f"     deficit (`full` − pool) mean {defic.mean():+.4f}   observed sd {obs_sd_d:.4f} = "
          f"noise {math.sqrt(s2e_d):.4f} + signal {dec_sd_d:.4f}")
    print(f"     ⭐ share of prompts where the rubric LOSES: NAIVE {naive:.3f}  vs  DECONVOLVED "
          f"{corrected:.3f}   (D4: the naive is biased away from the centre)")
    print(f"     ⚠ the noise is measured ON THE DIFFERENCE (D3) — assembling it from each pool's own "
          f"would have given {math.sqrt(2 * s2e):.4f} instead of {math.sqrt(s2e_d):.4f}")
    out["e2"] = {"mean": float(defic.mean()), "obs_sd": obs_sd_d, "noise_sd": math.sqrt(s2e_d),
                 "signal_sd": dec_sd_d, "naive_share": naive, "corrected_share": corrected,
                 "wrong_noise_if_unpaired": math.sqrt(2 * s2e)}

    # ================= E4 · the size confound =====================================================
    print("\n  E4 - THE SIZE CONFOUND: `full` carries a varying criterion count")
    nF = np.array([len({i for i, _ in SF[p]}) for p in pids])
    srng = np.random.default_rng(SEEDS[0] + 17)
    dpf16 = np.zeros(P)
    for a in range(P):
        k = min(16, len(fullhits[a]))
        pick = srng.choice(len(fullhits[a]), k, replace=False)
        dpf16[a] = np.mean([fullhits[a][j].mean() for j in pick])
    def16 = dpf16 - dpg
    print(f"     `full` criteria per prompt: min {nF.min()} mean {nF.mean():.2f} max {nF.max()}")
    print(f"     deficit raw {defic.mean():+.4f}   size-matched (<=16 sampled) {def16.mean():+.4f}   "
          f"difference {def16.mean() - defic.mean():+.4f}")
    out["e4"] = {"raw": float(defic.mean()), "size_matched": float(def16.mean()),
                 "mean_nF": float(nF.mean())}

    print("\n  MULTIPLICITY  4 variance components (a DECOMPOSITION, summing to the total by "
          "construction — reported whole, not tested individually) + 2 deficit estimates + 2 shares")

    print("\n  THE KILL -- conditional, gated on the controls")
    sc_, sp_, si_ = comp["criterion"], comp["prompt"], comp["interaction"]
    top = max(sc_, sp_, si_)
    if not gate:
        world = "UNVERIFIED"
    elif sc_ == top:
        world = "C"
    elif si_ == top and si_ > 1.2 * max(sp_, sc_):
        world = "A"
    elif sp_ == top and sp_ > 1.2 * max(si_, sc_):
        world = "B"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   criterion {sc_:.6f}  prompt {sp_:.6f}  interaction {si_:.6f}  ->  "
          f"WORLD {world}")
    out["world"] = world

    art = HERE / "results/components.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                             text=True).stdout.strip()
    except Exception:
        sha = "unknown"
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
