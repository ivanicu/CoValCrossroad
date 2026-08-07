#!/usr/bin/env python3
"""R789 · how many LEVELS the A2 axis resolves, and whether a cut separates the core from `generic`.

R788's NEXT proposed replacing `q_resolved` by A2 against a stated cut. A cut is only as good as
the axis's resolution, so this round prices the axis. CHECK #391 found the instrument is prior art
— R768 built the paired-bootstrap pairwise A2 matrix and found 0 of 10 resolved among the five arms
clause ② admits — so what is new is the POPULATION (all 27 arms, 351 pairs), the LADDER (how many
levels the axis resolves), and the decisive pair `coval_core` vs `generic`.

ESTIMAND        E1 the 351-pair matrix · E2 ⭐ the ladder, two constructions · E3 ⭐ the released
                core against the blind baseline · E4 the cut plateaus
IDENTIFICATION  exact given the per-prompt A2 vectors. ⚠ PARTIAL on the annotator level: a prompt
                bootstrap does not resample annotators, so the HIERARCHICAL bootstrap is built as
                a specification cell rather than declared impossible.
DERIVED FIRST   D1 the admitted set changes at each distinct A2, so ℝ gives (#distinct)+1 sets ·
                D2 a plateau IS the gap, and a gap below its pair's MDE is not a distinction ·
                D3 var(a−b)=var(a)+var(b)−2cov, so the pairing must be destroyed to be priced ·
                D4 #levels ≤ #distinct A2, so the measurement is where in [1,20] it lands — and if
                it lands near `q`'s 4, R787's headline is downgraded BY THIS ROUND
WORLDS          A axis finer than q (≥8) · B no finer (≤5) · C the core is not resolvedly above
                the blind baseline — C is checked FIRST because it dominates
CONTROLS        OBJECT · PLACEBO · POSITIVE (band both ends, and the CONSTANT plant is reported as
                the DEGENERATE limit it is) · NEGATIVE (pairing destroyed, + synthetic) · SHAM (a
                fixed scalar cut) · NEUTRAL (the median reference's vector) · NOISE FLOOR (measured)

⚠ A DESIGN NOTE WRITTEN BEFORE THE RUN, because it is §4's *check that cannot fail*: planting a
CONSTANT shift gives a difference vector with sd exactly 0, hence MDE exactly 0, so it resolves at
every non-zero delta and reads nothing about the design's resolution. It is kept and printed as the
degenerate limit; the control that GATES is the plant with zero-mean per-prompt noise at the
population's own median pairwise sd.
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
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls                          # noqa: E402
from report import verdict                                             # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
R782 = (ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
        / "R782_the_released_core_does_not_have_four_criteria/results/size_and_comparator.json")
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621                      # 2.801585 -- R725's `strict`/`mde` threshold on t
SEEDS = [31337, 31338, 31339]
NBOOT_MAIN = 1200
RULES = {"point": 0.0, "ci_only": 1.959964, "strict_mde": 2.801585, "conservative": 4.761549}

INSTRUMENT_UNIT = "an (arm, arm, prompt) paired difference"
CLAIM_UNIT = "an arm pair, and for the ladder a LEVEL"


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


def bh(pv, q=0.05):
    """Benjamini-Hochberg. Threshold at rank k is q*k/C -- the largest is q itself."""
    n = len(pv)
    order = np.argsort(pv)
    keep = np.zeros(n, bool)
    kmax = 0
    for r, i in enumerate(order, start=1):
        if pv[i] <= q * r / n:
            kmax = r
    for r, i in enumerate(order, start=1):
        if r <= kmax:
            keep[i] = True
    return keep


def boot_means_prompt(A2mat, rng, nboot, block=300):
    """Cluster bootstrap over PROMPTS. Shared draws across arms -- correct for a paired design."""
    n, P = A2mat.shape
    out = np.empty((n, nboot))
    done = 0
    while done < nboot:
        b = min(block, nboot - done)
        idx = rng.integers(0, P, size=(b, P))
        out[:, done:done + b] = A2mat[:, idx].mean(axis=2)
        done += b
    return out


def boot_means_hier(AG, NANN, rng, nboot, block=40):
    """HIERARCHICAL: resample prompts, then resample each drawn prompt's annotators."""
    n, P, Amax = AG.shape
    out = np.empty((n, nboot))
    done = 0
    while done < nboot:
        b = min(block, nboot - done)
        pidx = rng.integers(0, P, size=(b, P))
        cnt = NANN[pidx]                                            # (b, P)
        aidx = (rng.random((b, P, Amax)) * cnt[:, :, None]).astype(np.int64)
        valid = np.arange(Amax)[None, None, :] < cnt[:, :, None]
        w = valid.sum(axis=2)
        for t in range(n):
            g = AG[t][pidx[:, :, None], aidx]                       # (b, P, Amax)
            per_prompt = np.where(valid, g, 0.0).sum(axis=2) / w
            out[t, done:done + b] = per_prompt.mean(axis=1)
        done += b
    return out


def pair_stats(d, mdiff, nboot):
    """d = per-prompt paired difference; mdiff = its bootstrap draws."""
    eff = float(d.mean())
    sd = float(d.std(ddof=1))
    P = len(d)
    se = sd / math.sqrt(P)
    mde = ZEFF * se
    lo, hi = (float(np.percentile(mdiff, 2.5)), float(np.percentile(mdiff, 97.5))) \
        if mdiff is not None else (eff, eff)
    if mdiff is None:
        lo = hi = eff
    p = 2.0 * min(float((mdiff <= 0).mean()), float((mdiff >= 0).mean())) if mdiff is not None else 1.0
    p = max(p, 1.0 / (nboot + 1))
    t = abs(eff) / se if se > 0 else (math.inf if eff != 0 else 0.0)
    return {"eff": eff, "sd": sd, "se": se, "mde": mde, "lo": lo, "hi": hi, "p": min(p, 1.0),
            "t": t, "verdict": verdict(eff, lo, hi, mde)}


def ladder(names, a2, resolved):
    """resolved(i, j) -> bool. names sorted ASCENDING by a2. Two constructions, both reported."""
    adj_groups, g = [], [names[0]]
    for i in range(len(names) - 1):
        if resolved(names[i], names[i + 1]):
            adj_groups.append(g)
            g = []
        g.append(names[i + 1])
    adj_groups.append(g)
    adj = len(adj_groups)
    levels, cur = [], [names[0]]
    for nm in names[1:]:
        if resolved(cur[0], nm):
            levels.append(cur)
            cur = [nm]
        else:
            cur.append(nm)
    levels.append(cur)
    return adj, len(levels), [len(x) for x in levels], adj_groups


def main():
    out = {"instrument_unit": INSTRUMENT_UNIT, "claim_unit": CLAIM_UNIT,
           "unit_equal": INSTRUMENT_UNIT == CLAIM_UNIT}

    # ================= OBJECT CHECK -- exit 2, never 0 ============================================
    print("  OBJECT CHECK")
    if not R782.is_file():
        print("  UNRUNNABLE: R782's artifact is absent. Exit 2, never 0.")
        return 2
    q782 = json.loads(R782.read_text())["e4"]["q"]
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    P = len(pids)
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]
    NANN = np.array([len(h) for h in HC])
    Amax = int(NANN.max())

    def agree_from_Y(Y):
        """per-(prompt, annotator) agreement, padded to Amax; and the per-prompt A2."""
        G = np.zeros((P, Amax))
        for a in range(P):
            s = np.sign(Y[a][[i for i, _ in PR]] - Y[a][[j for _, j in PR]])
            g = (HC[a] == s).mean(axis=1)
            G[a, :len(g)] = g
        v = G.sum(axis=1) / NANN
        return G, v

    def a2_from_Y(Y):
        o = np.zeros(P)
        for a in range(P):
            s = np.sign(Y[a][[i for i, _ in PR]] - Y[a][[j for _, j in PR]])
            o[a] = np.mean([(s == h).mean() for h in HC[a]])
        return o

    tags = sorted(set(q782) | {"genericpool16"})
    names, A2rows, AGrows, bad = [], [], [], []
    for t in tags:
        f = RES / f"sat_{t}.npz"
        if not f.is_file():
            continue
        S = load_sat(f)
        if not set(pids) <= set(S):
            continue
        Y = np.zeros((P, 4))
        for a, p in enumerate(pids):
            ii = sorted({i for i, _ in S[p]})
            Y[a] = [sum(S[p].get((i, x), 0.0) for i in ii) for x in L]
        G, v = agree_from_Y(Y)
        if t in q782 and abs(float(v.mean()) - q782[t]["a2"]) > 1e-9:
            bad.append((t, float(v.mean()), q782[t]["a2"]))
        names.append(t)
        A2rows.append(v)
        AGrows.append(G)
    A2mat = np.array(A2rows)
    AG = np.array(AGrows)
    n = len(names)
    print(f"     prompts {P}   annotators/prompt min {NANN.min()} median {int(np.median(NANN))} "
          f"max {Amax}   arms rebuilt {n} of {len(tags)}")
    print(f"     A2 vs R782's published value: mismatches beyond 1e-9  {len(bad)}")
    if n < 27 or P != 968 or bad:
        print(f"  UNRUNNABLE: population {n}, prompts {P}, mismatches {bad[:3]}. Exit 2, never 0.")
        return 2
    out["object"] = {"arms": n, "prompts": P, "amax": Amax, "ann_median": int(np.median(NANN)),
                     "a2_mismatches": len(bad)}

    ix = {t: i for i, t in enumerate(names)}
    a2 = A2mat.mean(axis=1)
    rng = np.random.default_rng(SEEDS[0])
    Mp = boot_means_prompt(A2mat, rng, NBOOT_MAIN)

    def stats(ti, tj, M=None):
        i, j = ix[ti], ix[tj]
        MM = Mp if M is None else M
        return pair_stats(A2mat[i] - A2mat[j], MM[i] - MM[j], NBOOT_MAIN)

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    pl = stats(names[0], names[0])
    plok = pl["eff"] == 0.0 and pl["lo"] == 0.0 and pl["hi"] == 0.0 and pl["verdict"] == "UNRESOLVED"
    print(f"     PLACEBO     `{names[0]}` against itself: eff {pl['eff']:.6f}  CI "
          f"[{pl['lo']:.6f}, {pl['hi']:.6f}]  {pl['verdict']}   {'PASS' if plok else 'FAIL'}")

    # the population's own median pairwise sd -- the noise template the noisy plant uses
    sds = [float((A2mat[ix[x]] - A2mat[ix[y]]).std(ddof=1))
           for x, y in itertools.combinations(names, 2)]
    sd_med = float(np.median(sds))

    prng = np.random.default_rng(SEEDS[0] + 7)
    v0 = A2mat[ix[names[n // 2]]]
    noise = prng.normal(0, 1, P)
    noise = (noise - noise.mean()) / noise.std(ddof=1) * sd_med
    dose, floor_v, ceil_v = {}, None, None
    for delta in (0.0, 0.002, 0.005, 0.01, 0.02, 0.05):
        d_const = np.full(P, delta)
        s_const = pair_stats(d_const, np.full(NBOOT_MAIN, delta), NBOOT_MAIN)
        d_noise = delta + noise
        mb = boot_means_prompt(np.array([d_noise]), np.random.default_rng(SEEDS[0] + 11),
                               NBOOT_MAIN)[0]
        s_noise = pair_stats(d_noise, mb, NBOOT_MAIN)
        dose[f"{delta}"] = {"constant": s_const["verdict"], "noisy": s_noise["verdict"],
                            "noisy_eff": s_noise["eff"], "noisy_mde": s_noise["mde"],
                            "noisy_t": s_noise["t"]}
        print(f"     POSITIVE    delta {delta:<6}  NOISY eff {s_noise['eff']:+.5f} mde "
              f"{s_noise['mde']:.5f} t {s_noise['t']:.2f} -> {s_noise['verdict']:<16} "
              f"| constant plant -> {s_const['verdict']} (sd 0, DEGENERATE)")
        if delta == 0.0:
            floor_v = s_noise["verdict"]
        if delta == 0.05:
            ceil_v = s_noise["verdict"]
    posok = (floor_v == "UNRESOLVED") and (ceil_v not in ("UNRESOLVED", "BELOW RESOLUTION")) \
        and (floor_v != ceil_v)
    print(f"                 band COMPUTED: floor(delta=0) {floor_v}  ceiling(delta=0.05) {ceil_v}"
          f"   {'admissible' if floor_v != ceil_v else 'DEGENERATE'}   "
          f"POSITIVE {'PASS' if posok else 'FAIL'}")
    print(f"                 ⚠ the CONSTANT plant has sd 0 hence mde 0 and resolves at every "
          f"non-zero delta -- kept as the degenerate limit, it does not gate")

    # NEGATIVE -- destroy the pairing
    nrng = np.random.default_rng(SEEDS[0] + 13)
    # ⛔ THE FIRST DRAFT SWEPT `names[:8]`, WHICH CONTAINS EXACT-DUPLICATE ARMS. A duplicate pair
    # has paired sd EXACTLY 0, so the ratio was perm_sd/1e-12 and the mean came back 7.5e9 while
    # `infl > 1.0` printed PASS. §4's *control that cannot PASS*, in its other direction: a control
    # that cannot FAIL. Degenerate pairs are now EXCLUDED and counted, the band is two-sided, and
    # the sweep runs over every pair rather than a slice.
    ratios, degen = [], 0
    for x, y in itertools.combinations(names, 2):
        dpair = A2mat[ix[x]] - A2mat[ix[y]]
        if dpair.std(ddof=1) == 0.0:
            degen += 1
            continue
        perm = A2mat[ix[x]] - A2mat[ix[y]][nrng.permutation(P)]
        ratios.append(float(perm.std(ddof=1) / dpair.std(ddof=1)))
    infl = float(np.median(ratios))
    infl_mean = float(np.mean(ratios))
    # synthetic world the control's own logic requires: independent arms -> ratio ~ 1
    sa = nrng.normal(0.53, 0.12, P)
    sb = nrng.normal(0.53, 0.12, P)
    syn = float((sa - sb[nrng.permutation(P)]).std(ddof=1) / (sa - sb).std(ddof=1))
    negok = 1.02 < infl < 10.0 and abs(syn - 1.0) < 0.15
    print(f"     NEGATIVE    pairing destroyed: MDE inflation median x{infl:.3f} mean x{infl_mean:.3f}"
          f" over {len(ratios)} non-degenerate pairs, {degen} exact-duplicate pairs EXCLUDED "
          f"(R768 measured x2.25) · synthetic independent arms x{syn:.3f} (must be ~1)   "
          f"{'PASS' if negok else 'FAIL'}")
    print(f"                 world it excludes: 'the paired CIs are narrow because of the PAIRING, "
          f"not because the arms track prompt by prompt'")

    # NOISE FLOOR -- measured, split-half over each prompt's annotators
    frng = np.random.default_rng(SEEDS[0] + 17)
    halves = []
    for _ in range(20):
        d = np.zeros((n, P))
        for a in range(P):
            k = NANN[a]
            pm = frng.permutation(k)
            h1, h2 = pm[:k // 2], pm[k // 2:2 * (k // 2)]
            d[:, a] = AG[:, a, h1].mean(axis=1) - AG[:, a, h2].mean(axis=1)
        halves.append(float(np.abs(d.mean(axis=1)).mean()))
    floor_ann = float(np.mean(halves))
    print(f"     NOISE FLOOR annotator split-half, 20 draws: mean |A2_half1 - A2_half2| "
          f"{floor_ann:.6f}   (a floor the PROMPT bootstrap does not contain)")

    gate = plok and posok and negok
    out["controls"] = {"placebo": pl, "placebo_ok": plok, "dose": dose, "positive_ok": posok,
                       "floor_verdict": floor_v, "ceiling_verdict": ceil_v,
                       "negative_inflation": infl, "negative_inflation_mean": infl_mean,
                       "negative_degenerate_pairs_excluded": degen, "negative_synthetic": syn, "negative_ok": negok,
                       "annotator_floor": floor_ann, "sd_median_pairwise": sd_med, "gate": gate}
    print(f"     GATE        {'PASS -- the kill may evaluate' if gate else 'FAIL -- UNVERIFIED'}")

    # ================= E1 · the 351-pair matrix ===================================================
    print(f"\n  E1 - THE PAIRWISE MATRIX, {n} arms, {n * (n - 1) // 2} unordered pairs")
    pairs, pv = [], []
    for x, y in itertools.combinations(names, 2):
        s = stats(x, y)
        s["a"], s["b"] = x, y
        pairs.append(s)
        pv.append(s["p"])
    pv = np.array(pv)
    keep = bh(pv, 0.05)
    n_verdict = sum(1 for s in pairs if s["verdict"] in ("BEATS", "LOSES"))
    print(f"     cells tested {len(pairs)}   surviving the VERDICT rule (CI excludes 0 AND "
          f"|eff| >= mde)  {n_verdict}   NOT surviving {len(pairs) - n_verdict}")
    print(f"     surviving BH q=0.05 on the bootstrap p (no MDE floor)  {int(keep.sum())}   "
          f"NOT surviving {len(pairs) - int(keep.sum())}")
    out["e1"] = {"pairs": len(pairs), "verdict_resolved": n_verdict, "bh_resolved": int(keep.sum()),
                 "matrix": pairs}

    # ================= E2 · THE LADDER, over the whole specification grid =========================
    print("\n  E2 - THE LADDER: how many LEVELS the A2 axis resolves")
    order = sorted(names, key=lambda t: a2[ix[t]])
    tmap = {(s["a"], s["b"]): s["t"] for s in pairs}
    tmap.update({(s["b"], s["a"]): s["t"] for s in pairs})
    distinct = len(set(np.round(a2, 9)))
    print(f"     ⚠ D1/D4: {distinct} distinct A2 values, so a cut over ℝ gives {distinct + 1} "
          f"admitted sets and the ladder is bounded by [1, {distinct}]. DERIVATION, not a finding.")
    spec = {}
    for rn, thr in RULES.items():
        adj, gre, sizes, groups = ladder(order, a2, lambda x, y: tmap[(x, y)] >= thr and thr > 0
                                 or (thr == 0 and a2[ix[x]] != a2[ix[y]]))
        spec[rn] = {"adjacent": adj, "greedy": gre, "greedy_level_sizes": sizes,
                    "adjacent_groups": groups}
        print(f"     rule {rn:<13} t >= {thr:<9.6f}   adjacent {adj:>2}   greedy {gre:>2}   "
              f"greedy level sizes {sizes}")
        if rn == "strict_mde":
            for li, grp in enumerate(groups, start=1):
                print(f"        L{li} [{a2[ix[grp[0]]]:.4f}-{a2[ix[grp[-1]]]:.4f}] "
                      f"{len(grp)}: {', '.join(grp)}")
    ladder_adj = spec["strict_mde"]["adjacent"]
    out["e2"] = {"distinct_a2": distinct, "spec": spec, "order": order,
                 "a2": {t: float(a2[ix[t]]) for t in names}}

    # ---- specification: NBOOT and seeds (the verdict rule uses the CI, so draws matter) ----------
    seedspec = {}
    for sd_ in SEEDS:
        for nb in (600, 1200):
            r2 = np.random.default_rng(sd_)
            M2 = boot_means_prompt(A2mat, r2, nb)
            res = {}
            for x, y in itertools.combinations(names, 2):
                st = pair_stats(A2mat[ix[x]] - A2mat[ix[y]], M2[ix[x]] - M2[ix[y]], nb)
                res[(x, y)] = st["verdict"] in ("BEATS", "LOSES")
            adj, gre, _, _ = ladder(order, a2, lambda x, y: res.get((x, y), res.get((y, x))))
            seedspec[f"seed{sd_}_nboot{nb}"] = {"adjacent": adj, "greedy": gre,
                                                "resolved_pairs": int(sum(res.values()))}
            print(f"     seed {sd_} nboot {nb:<5} adjacent {adj:>2}  greedy {gre:>2}  "
                  f"resolved pairs {int(sum(res.values()))}")
    out["e2"]["seed_spec"] = seedspec

    # ---- specification: HIERARCHICAL bootstrap (annotators resampled too) ------------------------
    print("     hierarchical bootstrap (prompts, then annotators within prompt), nboot 600 ...")
    Mh = boot_means_hier(AG, NANN, np.random.default_rng(SEEDS[0]), 600)
    resh = {}
    for x, y in itertools.combinations(names, 2):
        st = pair_stats(A2mat[ix[x]] - A2mat[ix[y]], Mh[ix[x]] - Mh[ix[y]], 600)
        resh[(x, y)] = st["verdict"] in ("BEATS", "LOSES")
    adjh, greh, _, _ = ladder(order, a2, lambda x, y: resh.get((x, y), resh.get((y, x))))
    print(f"     HIERARCHICAL      adjacent {adjh:>2}  greedy {greh:>2}  "
          f"resolved pairs {int(sum(resh.values()))}")
    out["e2"]["hierarchical"] = {"adjacent": adjh, "greedy": greh,
                                 "resolved_pairs": int(sum(resh.values()))}

    # ================= E3 · THE DECISIVE PAIR =====================================================
    print("\n  E3 - THE DECISIVE PAIR: the released core against the blind baseline")
    dec = {}
    for x, y in (("coval_core", "generic"), ("coval_core", "gen"), ("generic", "gen"),
                 ("coval_core", "genericpool16"), ("generic", "genericpool16")):
        if x in ix and y in ix:
            s = stats(x, y)
            sh = pair_stats(A2mat[ix[x]] - A2mat[ix[y]], Mh[ix[x]] - Mh[ix[y]], 600)
            dec[f"{x}__{y}"] = {"prompt": s, "hier": sh}
            print(f"     {x:<14} - {y:<14} {s['eff']:+.5f}  CI [{s['lo']:+.5f}, {s['hi']:+.5f}]  "
                  f"mde {s['mde']:.5f}  t {s['t']:.2f}  {s['verdict']:<16} | hier {sh['verdict']}")
    core_gen = dec.get("coval_core__generic", {}).get("prompt")
    core_beats = bool(core_gen and core_gen["verdict"] == "BEATS")
    out["e3"] = dec

    # ================= E4 · the plateaus ==========================================================
    print("\n  E4 - THE CUT PLATEAUS")
    asc = sorted(names, key=lambda t: a2[ix[t]])
    gaps = [(asc[i], asc[i + 1], float(a2[ix[asc[i + 1]]] - a2[ix[asc[i]]]),
             float(tmap[(asc[i], asc[i + 1])])) for i in range(n - 1)]
    widest = max(gaps, key=lambda g: g[2])
    print(f"     widest plateau  between `{widest[0]}` and `{widest[1]}`: width {widest[2]:.5f}  "
          f"t {widest[3]:.2f}")
    print(f"     gaps below the annotator floor {floor_ann:.5f}: "
          f"{sum(1 for g in gaps if g[2] < floor_ann)} of {len(gaps)}")
    if core_gen:
        band = float(a2[ix['coval_core']] - a2[ix['generic']])
        adm = [t for t in names if a2[ix[t]] > a2[ix['generic']]]
        print(f"     cuts admitting `coval_core` and excluding `generic`: width {band:.5f} vs that "
              f"pair's mde {core_gen['mde']:.5f}  ratio {band / max(core_gen['mde'], 1e-12):.2f}")
        print(f"     at such a cut the admitted set is {sorted(adm)}")
        out["e4"] = {"widest": widest, "band": band, "band_over_mde":
                     band / max(core_gen["mde"], 1e-12), "admitted": sorted(adm),
                     "gaps_below_annotator_floor": sum(1 for g in gaps if g[2] < floor_ann),
                     "gaps": gaps}

    # ================= E5 · SHAM (a scalar cut) and NEUTRAL (a non-arm vector) ====================
    # ⚠ DECLARED IN THE PREREGISTRATION AND MISSING FROM THE FIRST RUN. Built here rather than
    # recorded as an omission, because it is the control that prices R788's OWN PROPOSAL: a
    # "stated cut" is a SCALAR, and a scalar has no per-prompt vector, so comparing an arm to it
    # destroys the pairing D3 says the paired MDE depends on.
    print("\n  E5 - SHAM (the second ARM removed: a fixed scalar cut) and NEUTRAL (a non-arm vector)")
    idx16 = sorted({i for i, _ in POOL[pids[0]]})
    T = np.zeros((P, len(idx16), 4))
    for a_, p_ in enumerate(pids):
        for bi, i_ in enumerate(idx16):
            for c_, x_ in enumerate(L):
                T[a_, bi, c_] = POOL[p_].get((i_, x_), 0.0)
    SUB = list(itertools.combinations(range(len(idx16)), 4))
    REF = np.zeros((len(SUB), P))
    for si, sset in enumerate(SUB):
        REF[si] = a2_from_Y(T[:, list(sset), :].sum(axis=1))
    if len(SUB) != 1820:
        print("  UNRUNNABLE: the reference class is not 1,820. Exit 2, never 0.")
        return 2
    refA2 = REF.mean(axis=1)
    cut = float(np.median(refA2))
    med_ref = int(np.argsort(refA2)[len(refA2) // 2])
    print(f"     class rebuilt {len(SUB)}   median A2 (the stated cut) {cut:.6f}   "
          f"median reference #{med_ref}")
    Mcut = boot_means_prompt(A2mat, np.random.default_rng(SEEDS[0] + 23), NBOOT_MAIN)
    Mref = boot_means_prompt(np.array([REF[med_ref]]), np.random.default_rng(SEEDS[0] + 23),
                             NBOOT_MAIN)[0]
    sham_res = neut_res = 0
    e5 = {"cut": cut, "median_ref": med_ref, "arms": {}}
    for t in names:
        i = ix[t]
        ss = pair_stats(A2mat[i] - cut, Mcut[i] - cut, NBOOT_MAIN)         # SHAM: no pairing
        sn = pair_stats(A2mat[i] - REF[med_ref], Mcut[i] - Mref, NBOOT_MAIN)  # NEUTRAL: paired
        e5["arms"][t] = {"sham": ss, "neutral": sn}
        sham_res += int(ss["verdict"] in ("BEATS", "LOSES"))
        neut_res += int(sn["verdict"] in ("BEATS", "LOSES"))
    sd_sham = float(np.mean([e5["arms"][t]["sham"]["sd"] for t in names]))
    sd_neut = float(np.mean([e5["arms"][t]["neutral"]["sd"] for t in names]))
    print(f"     SHAM    arm vs the SCALAR cut (pairing absent):  resolved {sham_res} of {n} arms   "
          f"mean sd {sd_sham:.5f}")
    print(f"     NEUTRAL arm vs the MEDIAN REFERENCE's vector  :  resolved {neut_res} of {n} arms   "
          f"mean sd {sd_neut:.5f}   inflation x{sd_sham / max(sd_neut, 1e-12):.3f}")
    for t in ("coval_core", "generic", "gen"):
        if t in ix:
            a_, b_ = e5["arms"][t]["sham"], e5["arms"][t]["neutral"]
            print(f"       {t:<12} SHAM {a_['eff']:+.5f} mde {a_['mde']:.5f} {a_['verdict']:<16} | "
                  f"NEUTRAL {b_['eff']:+.5f} mde {b_['mde']:.5f} {b_['verdict']}")
    e5.update({"sham_resolved": sham_res, "neutral_resolved": neut_res, "sd_sham": sd_sham,
               "sd_neutral": sd_neut, "sd_inflation": sd_sham / max(sd_neut, 1e-12)})
    out["e5"] = e5

    # ---- are the LADDER's own resolved gaps above the marginal annotator floor? ------------------
    res_gaps = [g for g in gaps if g[3] >= RULES["strict_mde"]]
    above = sum(1 for g in res_gaps if g[2] >= floor_ann)
    print(f"     ⚠ UNIT NOTE: the annotator split-half floor {floor_ann:.5f} is a MARGINAL per-arm "
          f"quantity; the gaps are PAIRED differences in which the annotator draw is common, so the "
          f"comparison is not like-for-like. Of the ladder's {len(res_gaps)} resolved adjacent gaps, "
          f"{above} exceed it. The instrument that IS like-for-like is the hierarchical bootstrap, "
          f"which left the ladder at {adjh}/{greh}.")
    out["e2"]["resolved_gaps_above_marginal_floor"] = [len(res_gaps), above]

    # ================= THE KILL ===================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif not core_beats:
        world = "C"
    elif ladder_adj >= 8:
        world = "A"
    elif ladder_adj <= 5:
        world = "B"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   core BEATS generic {core_beats}   ladder(strict, adjacent) "
          f"{ladder_adj}   ->  WORLD {world}")
    out["world"] = world
    out["ladder_adjacent_strict"] = ladder_adj

    art = HERE / "results/ladder.json"
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
