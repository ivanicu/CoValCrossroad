#!/usr/bin/env python3
"""R791 · A2 is the mean of SIX pairwise comparisons — does the decomposition see what the scalar can't?

R790's NEXT asked the first question in this arc no re-threshold can answer: should clause ② be a
scalar comparison at all? CHECK #393 ran the gauge test — A2 per prompt is the mean over annotators
of the mean over the SIX response-pairs, and the two means commute, so A2 is EXACTLY the mean of six
component agreements. The measurement is invariant under permuting which comparison an arm gets
right; the property is not obviously invariant. P4: R733/R457/R771/R772/R774 all decompose across
PROMPTS; none decomposes across the six comparisons INSIDE a prompt.

ESTIMAND        E1 six component effects x 190 pairs · E2 ⭐ the decisive pair · E3 ⭐ how many pairs
                each family resolves after its own BH, and whether the admitted sets differ ·
                E4 the effective rank of the (20 x 6) component matrix
IDENTIFICATION  exact given the per-(prompt, component) arrays. ⚠ PARTIAL on annotators; the
                hierarchical cell is run rather than assumed
DERIVED FIRST   D1 A2 = mean of the six components, exactly — printed as a CODE CHECK, not evidence
                · D2 the componentwise family cannot resolve fewer at the same nominal level, so
                only the POST-BH comparison is a finding · D3 if the components are perfectly
                correlated the decomposition is a reparameterisation · D4 alias pairs must return
                all six effects exactly 0
WORLDS          A the components see more · B they see nothing more · C reparameterisation — C is
                checked FIRST because it voids A's reading
CONTROLS        OBJECT (D1 + R789's matrix) · PLACEBO (aliases, exact) · POSITIVE (band both ends AND
                component-SPECIFIC) · NEGATIVE (the gauge permutation itself, A2 exactly invariant)
                · SHAM (the scalar alone) · NOISE FLOOR (annotator split-half, per component)
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

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
R789 = (ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
        / "R789_how_many_levels_the_a2_axis_resolves/results/ladder.json")
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
NC = len(PR)
RULES = {"point": 0.0, "ci_only": 1.959964, "strict_mde": 2.801585, "conservative": 4.761549}
STRICT = RULES["strict_mde"]
SEEDS = [31337, 31338, 31339]
NBOOT = 1200

INSTRUMENT_UNIT = "an (arm, arm, component, prompt) paired difference"
CLAIM_UNIT = "an (arm, arm) PAIR"
CLAIM_UNIT_E3 = "an ADMITTED SET"


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
    """Benjamini-Hochberg over the WHOLE grid. Threshold at rank k is q*k/C."""
    pv = np.asarray(pv, float)
    m = len(pv)
    order = np.argsort(pv)
    kmax = 0
    for r, i in enumerate(order, start=1):
        if pv[i] <= q * r / m:
            kmax = r
    keep = np.zeros(m, bool)
    keep[order[:kmax]] = True
    return keep


def main():
    out = {"instrument_unit": INSTRUMENT_UNIT, "claim_unit": CLAIM_UNIT,
           "claim_unit_e3": CLAIM_UNIT_E3,
           "units_distinct": len({INSTRUMENT_UNIT, CLAIM_UNIT, CLAIM_UNIT_E3}) == 3}

    # ================= OBJECT CHECK -- exit 2, never 0 ============================================
    print("  OBJECT CHECK")
    if not R789.is_file():
        print("  UNRUNNABLE: R789's artifact is absent. Exit 2, never 0.")
        return 2
    prev = json.loads(R789.read_text())
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    P = len(pids)
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]

    def comps_from_Y(Y):
        """per-(prompt, component) agreement, and the SIGNS -- kept so the annotator split-half
        noise floor is computable rather than registered UNCOMPUTED. A2 = the mean over components,
        EXACTLY (D1)."""
        G = np.zeros((P, NC))
        SG = np.zeros((P, NC))
        for a in range(P):
            sg = np.sign(Y[a][[i for i, _ in PR]] - Y[a][[j for _, j in PR]])
            SG[a] = sg
            G[a] = (HC[a] == sg).mean(axis=0)                           # mean over ANNOTATORS
        return G, SG

    CG, A2v, SGN = {}, {}, {}
    for t in prev["e2"]["a2"]:
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
        CG[t], SGN[t] = comps_from_Y(Y)
        A2v[t] = CG[t].mean(axis=1)

    names = sorted(CG)
    d1 = max(abs(float(A2v[t].mean()) - prev["e2"]["a2"][t]) for t in names)
    print(f"     prompts {P}   named arms {len(names)}   components {NC}")
    print(f"     D1 identity  |mean of the six components - R789's A2|  worst {d1:.3e}   "
          f"⚠ a CODE CHECK, not evidence")

    par = {t: t for t in names}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    alias_pairs = [(x, y) for x, y in itertools.combinations(names, 2)
                   if np.array_equal(CG[x], CG[y])]
    for x, y in alias_pairs:
        par[find(x)] = find(y)
    reps = sorted({find(t) for t in names}, key=lambda t: A2v[t].mean())
    rep_of = {t: reps.index(find(t)) for t in names}
    n = len(reps)
    C = np.array([CG[t] for t in reps])                                 # (n, P, NC)
    SG = np.array([SGN[t] for t in reps])                               # (n, P, NC)
    A2 = C.mean(axis=2)                                                 # (n, P)
    PAIRS = list(itertools.combinations(range(n), 2))
    pk = {}
    for k, (i, j) in enumerate(PAIRS):
        pk[(i, j)] = pk[(j, i)] = k
    ri = dict(rep_of)
    DECISIVE = ("coval_core", "topw_k4", "generic", "gen")
    missing = [t for t in DECISIVE if t not in ri]
    print(f"     alias pairs {len(alias_pairs)}   distinct objects {n}   pairs {len(PAIRS)}   "
          f"decisive arms present {len(DECISIVE) - len(missing)} of {len(DECISIVE)}")

    prevT = {}
    for s in prev["e1"]["matrix"]:
        prevT[(s["a"], s["b"])] = prevT[(s["b"], s["a"])] = s["t"]

    def tstats(Dm):
        """Dm (..., P) -> (eff, sd, se, mde, t)."""
        eff = Dm.mean(axis=-1)
        sd = Dm.std(axis=-1, ddof=1)
        se = sd / math.sqrt(Dm.shape[-1])
        with np.errstate(divide="ignore", invalid="ignore"):
            t = np.where(se > 0, np.abs(eff) / np.where(se > 0, se, 1.0),
                         np.where(eff != 0, np.inf, 0.0))
        return eff, sd, se, 2.801585 * se, t

    DS = np.array([A2[i] - A2[j] for i, j in PAIRS])                    # scalar (npair, P)
    DC = np.array([C[i] - C[j] for i, j in PAIRS])                      # component (npair, P, NC)
    _, _, _, _, TS = tstats(DS)
    worst = max((abs(prevT[(reps[i], reps[j])] - TS[k])
                 for k, (i, j) in enumerate(PAIRS) if (reps[i], reps[j]) in prevT), default=1.0)
    print(f"     worst |scalar t - R789's committed t| over {len(PAIRS)} pairs: {worst:.3e}")
    if n != 20 or P != 968 or d1 > 1e-12 or worst > 1e-9 or missing or not alias_pairs:
        print(f"  UNRUNNABLE: objects {n}, prompts {P}, D1 {d1:.3e}, worst {worst:.3e}, missing "
              f"{missing}. Exit 2, never 0.")
        return 2
    out["object"] = {"prompts": P, "named": len(names), "objects": n, "components": NC,
                     "alias_pairs": len(alias_pairs), "d1_worst": d1, "worst_t_delta": worst}

    # ---- shared bootstrap draws for every statistic ---------------------------------------------
    def boot_p(Dm, rng, nb=NBOOT, blk=200):
        """two-sided bootstrap p for the paired mean, floored at 1/(nb+1)."""
        shp = Dm.shape[:-1]
        le = np.zeros(shp)
        ge = np.zeros(shp)
        done = 0
        while done < nb:
            b = min(blk, nb - done)
            idx = rng.integers(0, Dm.shape[-1], size=(b, Dm.shape[-1]))
            m = Dm[..., idx].mean(axis=-1)                              # (..., b)
            le += (m <= 0).sum(axis=-1)
            ge += (m >= 0).sum(axis=-1)
            done += b
        p = 2.0 * np.minimum(le, ge) / nb
        return np.maximum(np.minimum(p, 1.0), 1.0 / (nb + 1))

    rng = np.random.default_rng(SEEDS[0])
    PS = boot_p(DS, rng)
    PC = boot_p(DC.transpose(0, 2, 1), np.random.default_rng(SEEDS[0]))   # (npair, NC)
    effC, _, _, mdeC, TC = tstats(DC.transpose(0, 2, 1))
    effS, _, _, mdeS, _ = tstats(DS)

    # ================= E1 · the identity, and the component effects ===============================
    print(f"\n  E1 - SIX COMPONENT EFFECTS x {len(PAIRS)} PAIRS = {NC * len(PAIRS)} CELLS")
    idn = float(np.abs(effC.mean(axis=1) - effS).max())
    print(f"     D1 check: |mean of the six component effects - the scalar effect| worst "
          f"{idn:.3e}   ⚠ forced by algebra")
    keepS = bh(PS)
    keepC = bh(PC.ravel()).reshape(PC.shape)
    resS = int(((np.abs(effS) >= mdeS) & keepS).sum())
    resC_cells = int(((np.abs(effC) >= mdeC) & keepC).sum())
    resC_pairs = int((((np.abs(effC) >= mdeC) & keepC).any(axis=1)).sum())
    print(f"     SCALAR      cells {len(PAIRS)}   surviving BH+MDE {resS}   not {len(PAIRS) - resS}")
    print(f"     COMPONENT   cells {NC * len(PAIRS)}   surviving BH+MDE {resC_cells}   "
          f"not {NC * len(PAIRS) - resC_cells}")
    print(f"     COMPONENT   PAIRS with >=1 surviving component: {resC_pairs} of {len(PAIRS)}")
    print(f"     ⚠ D2: more cells is arithmetic. The finding is {resC_pairs} vs {resS} AFTER each "
          f"family's own BH.")
    out["e1"] = {"identity_worst": idn, "scalar_resolved": resS,
                 "component_cells_resolved": resC_cells, "component_pairs_resolved": resC_pairs,
                 "scalar_cells": len(PAIRS), "component_cells": NC * len(PAIRS)}

    # ================= E2 · the decisive pair =====================================================
    print("\n  E2 - THE DECISIVE PAIR: `coval_core` - `topw_k4`, which the scalar cannot resolve")
    dec = {}
    for a, b in (("coval_core", "topw_k4"), ("coval_core", "generic"), ("coval_core", "gen")):
        k = pk[(ri[a], ri[b])]
        sgn = 1.0 if ri[a] < ri[b] else -1.0
        row = {"scalar": {"eff": float(sgn * effS[k]), "mde": float(mdeS[k]),
                          "t": float(TS[k]), "p": float(PS[k]), "bh": bool(keepS[k])},
               "components": []}
        print(f"     {a} - {b}   scalar eff {sgn * effS[k]:+.6f}  mde {mdeS[k]:.6f}  "
              f"t {TS[k]:.2f}  p {PS[k]:.4f}  BH {bool(keepS[k])}")
        for c in range(NC):
            surv = bool(keepC[k, c] and abs(effC[k, c]) >= mdeC[k, c])
            row["components"].append({"pair": f"{L[PR[c][0]]}{L[PR[c][1]]}",
                                      "eff": float(sgn * effC[k, c]), "mde": float(mdeC[k, c]),
                                      "t": float(TC[k, c]), "p": float(PC[k, c]), "survives": surv})
            print(f"        component {L[PR[c][0]]}{L[PR[c][1]]}  eff {sgn * effC[k, c]:+.6f}  "
                  f"mde {mdeC[k, c]:.6f}  t {TC[k, c]:.2f}  p {PC[k, c]:.4f}  "
                  f"{'SURVIVES BH+MDE' if surv else '--'}")
        dec[f"{a}__{b}"] = row
    decisive_any = any(c["survives"] for c in dec["coval_core__topw_k4"]["components"])
    print(f"     ⭐ any component resolving `coval_core` from `topw_k4` after BH: {decisive_any}")
    out["e2"] = dec

    # ================= E4 · the effective rank (checked before E3's reading) ======================
    print("\n  E4 - IS THE DECOMPOSITION A REPARAMETERISATION?  (D3)")
    M = C.mean(axis=1)                                                  # (n, NC) arm x component
    Mc = M - M.mean(axis=0, keepdims=True)
    sv = np.linalg.svd(Mc, compute_uv=False)
    var = sv ** 2 / (sv ** 2).sum()
    print("     eigenvalue shares of the (20 x 6) centred component matrix: " +
          "  ".join(f"{v:.4f}" for v in var))
    print(f"     first share {var[0]:.4f}   {'>= 0.90 -> REPARAMETERISATION' if var[0] >= 0.90 else '< 0.90 -> the components carry more than one direction'}")
    shared = M.mean(axis=0)
    print("     shared component profile (mean over arms): " +
          "  ".join(f"{L[PR[c][0]]}{L[PR[c][1]]} {shared[c]:.4f}" for c in range(NC)))
    out["e4"] = {"eigen_shares": var.tolist(), "first_share": float(var[0]),
                 "shared_profile": shared.tolist()}

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    pl = max(float(np.abs(CG[x] - CG[y]).max()) for x, y in alias_pairs)
    plok = pl == 0.0
    print(f"     PLACEBO   {len(alias_pairs)} alias pairs: worst |component effect| {pl:.1e}   "
          f"expected EXACTLY 0 by D4   {'PASS' if plok else 'FAIL'}")

    med = int(np.argsort(A2.mean(axis=1))[n // 2])
    sd_med = float(np.median([DC[k, :, 0].std(ddof=1) for k in range(len(PAIRS))]))
    prng = np.random.default_rng(SEEDS[0] + 7)
    noise = prng.normal(0, 1, P)
    noise = (noise - noise.mean()) / noise.std(ddof=1) * sd_med
    dose, fl, ce, spec_ok = {}, None, None, None
    for delta in (0.0, 0.005, 0.01, 0.02, 0.05):
        Cp = C[med].copy()
        Cp[:, 0] += delta + noise
        Dp = (C[med] - Cp).transpose()                                  # (NC, P)
        e, _, _, m, _ = tstats(Dp)
        p = boot_p(Dp, np.random.default_rng(SEEDS[0] + 9), nb=400)
        k6 = bh(p)
        surv = [(bool(k6[c] and abs(e[c]) >= m[c])) for c in range(NC)]
        dose[str(delta)] = surv
        print(f"     POSITIVE  delta {delta:<6} on component AB only -> surviving components "
              f"{[L[PR[c][0]] + L[PR[c][1]] for c in range(NC) if surv[c]] or 'none'}")
        if delta == 0.0:
            fl = sum(surv)
        if delta == 0.05:
            ce = sum(surv)
            spec_ok = surv[0] and not any(surv[1:])
    posok = fl == 0 and ce >= 1 and fl != ce and bool(spec_ok)
    print(f"               band COMPUTED: floor {fl} components at delta 0, ceiling {ce} at 0.05   "
          f"specificity (only AB fires) {spec_ok}   POSITIVE {'PASS' if posok else 'FAIL'}")

    # NEGATIVE -- the gauge operation: permute component labels within each prompt
    nrng = np.random.default_rng(SEEDS[0] + 13)
    Cperm = np.array([C[med][a][nrng.permutation(NC)] for a in range(P)])
    a2_inv = float(np.abs(Cperm.mean(axis=1) - A2[med]).max())
    other = (med + 1) % n
    Dg0 = (C[med] - C[other]).transpose()
    Dg1 = (Cperm - C[other]).transpose()
    e0, _, _, _, _ = tstats(Dg0)
    e1, _, _, _, _ = tstats(Dg1)
    moved = float(np.abs(e0 - e1).max())
    negok = a2_inv < 1e-12 and moved > 0
    print(f"     NEGATIVE  component labels permuted within each prompt: A2 unchanged to "
          f"{a2_inv:.1e} (a DERIVATION, checked) while the largest component effect moves by "
          f"{moved:.6f}   {'PASS' if negok else 'FAIL'}")
    print(f"               world it excludes: 'the component differences are an artefact of which "
          f"comparison is indexed where'")
    srng = np.random.default_rng(SEEDS[0] + 17)
    Csyn = C[other] + srng.normal(0, sd_med / math.sqrt(2), (P, NC))
    esyn, _, _, msyn, _ = tstats((C[other] - Csyn).transpose())
    psyn = boot_p((C[other] - Csyn).transpose(), np.random.default_rng(SEEDS[0] + 19), nb=400)
    nsyn = int(((np.abs(esyn) >= msyn) & bh(psyn)).sum())
    print(f"               synthetic arm with i.i.d. component noise and no structure: "
          f"{nsyn} of {NC} components resolve (expected ~0)")

    # SHAM -- the machinery minus the decomposition
    print(f"     SHAM      the SCALAR alone over the same {len(PAIRS)} pairs: {resS} resolve, "
          f"against {resC_pairs} pairs componentwise")

    # NOISE FLOOR -- MEASURED: annotator split-half, per component
    frng = np.random.default_rng(SEEDS[0] + 23)
    runs = []
    usable = [a for a in range(P) if len(HC[a]) >= 4]
    for _ in range(20):
        h1 = np.zeros((n, NC))
        h2 = np.zeros((n, NC))
        for a in usable:
            k = len(HC[a])
            perm = frng.permutation(k)
            i1, i2 = perm[:k // 2], perm[k // 2:2 * (k // 2)]
            for t_ in range(n):
                sg = SG[t_][a]
                h1[t_] += (HC[a][i1] == sg).mean(axis=0)
                h2[t_] += (HC[a][i2] == sg).mean(axis=0)
        h1 /= len(usable)
        h2 /= len(usable)
        runs.append(np.abs(h1 - h2).mean(axis=0))
    floor_c = np.array(runs).mean(axis=0)
    print(f"     NOISE FLOOR  annotator split-half, 20 draws, {len(usable)} prompts with >=4 "
          f"annotators: mean |half1 - half2| per component")
    print("                  " + "  ".join(
        f"{L[PR[c][0]]}{L[PR[c][1]]} {floor_c[c]:.6f}" for c in range(NC)))
    print(f"                  ⚠ MARGINAL, per arm. Every effect above is a PAIRED difference in "
          f"which the annotator draw is common, so this floor may not be compared to them directly "
          f"(R790's unit note). It bounds the per-ARM component estimate, not the pair.")

    gate = plok and posok and negok
    out["controls"] = {"placebo_worst": pl, "placebo_ok": plok, "dose": dose, "floor": fl,
                       "ceiling": ce, "specific": spec_ok, "positive_ok": posok,
                       "negative_a2_invariance": a2_inv, "negative_moved": moved,
                       "negative_ok": negok, "synthetic_resolved": nsyn,
                       "noise_floor_per_component": floor_c.tolist(), "gate": gate}
    print(f"     GATE      {'PASS -- the kill may evaluate' if gate else 'FAIL -- UNVERIFIED'}")

    # ================= E3 · the definition-level decision =========================================
    print("\n  E3 - DOES A COMPONENTWISE CLAUSE ② ADMIT A DIFFERENT SET?")
    gi = ri["generic"]

    def admitted(resolved_fn):
        return sorted(t for t in names
                      if A2[rep_of[t]].mean() > A2[gi].mean() and resolved_fn(rep_of[t], gi))

    adm_s = admitted(lambda i, j: i != j and keepS[pk[(i, j)]]
                     and abs(effS[pk[(i, j)]]) >= mdeS[pk[(i, j)]])
    adm_c = admitted(lambda i, j: i != j and bool(((np.abs(effC[pk[(i, j)]]) >= mdeC[pk[(i, j)]])
                                                   & keepC[pk[(i, j)]]).any()))
    print(f"     SCALAR clause ②      admits {len(adm_s)} named arms: {adm_s}")
    print(f"     COMPONENTWISE clause ② admits {len(adm_c)} named arms: {adm_c}")
    print(f"     the two admitted sets are {'IDENTICAL' if adm_s == adm_c else 'DIFFERENT'}"
          f"{'' if adm_s == adm_c else ': ' + str(sorted(set(adm_c) ^ set(adm_s)))}")
    out["e3"] = {"scalar_admits": adm_s, "component_admits": adm_c, "identical": adm_s == adm_c}

    # ================= SPECIFICATION CURVE ========================================================
    print("\n  SPECIFICATION CURVE")
    spec = {}
    for rn, thr in RULES.items():
        rs = int((TS >= thr).sum()) if thr > 0 else int((np.abs(effS) > 0).sum())
        rc = int(((TC >= thr).any(axis=1)).sum()) if thr > 0 else int((np.abs(effC) > 0).any(axis=1).sum())
        dec_c = bool((TC[pk[(ri["coval_core"], ri["topw_k4"])]] >= thr).any()) if thr > 0 else True
        spec[rn] = {"scalar_pairs": rs, "component_pairs": rc, "decisive_pair": dec_c}
        print(f"     {rn:<13} t >= {thr:<9.6f}  scalar resolves {rs:>3}/{len(PAIRS)}   "
              f"componentwise {rc:>3}/{len(PAIRS)}   decisive pair {dec_c}")
    print("     ⚠ these are PRE-multiplicity counts; D2 makes componentwise >= scalar arithmetic.")
    for sd_ in SEEDS:
        pS = boot_p(DS, np.random.default_rng(sd_))
        pC = boot_p(DC.transpose(0, 2, 1), np.random.default_rng(sd_))
        kS, kC = bh(pS), bh(pC.ravel()).reshape(pC.shape)
        a = int(((np.abs(effS) >= mdeS) & kS).sum())
        b = int((((np.abs(effC) >= mdeC) & kC).any(axis=1)).sum())
        spec[f"seed{sd_}"] = {"scalar": a, "component_pairs": b}
        print(f"     seed {sd_}   post-BH scalar {a}   componentwise pairs {b}")
    out["spec"] = spec

    # ================= THE KILL ===================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    more = resC_pairs > resS
    if not gate:
        world = "UNVERIFIED"
    elif var[0] >= 0.90:
        world = "C"
    elif decisive_any and more:
        world = "A"
    elif (not decisive_any) and (not more):
        world = "B"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   first eigenshare {var[0]:.4f}   decisive pair any component "
          f"{decisive_any}   componentwise pairs {resC_pairs} vs scalar {resS}  ->  WORLD {world}")
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
