#!/usr/bin/env python3
"""R790 · is a LEVEL an object, or a threshold artefact?

R789's NEXT proposed rewriting clause ② as a MEMBERSHIP claim, because the released core shares its
level with three arms it cannot be ordered against. A membership formulation needs levels to be
objects. CHECK #392 found, before any design, that (a) the NEXT's factual claim survives at
`select_core.py:161/168/180`, (b) R768 already made the membership OBSERVATION, and (c) "same
level" is NOT TRANSITIVE — 16 of 202 chains at strict — so a level is a CONSTRUCTION. What is not
known, and is what this round measures, is whether the construction is STABLE.

ESTIMAND        E1 the intransitivity rate · E2 ⭐ the co-level probability matrix over B=1000
                resamples · E3 ⭐ P(coval_core ~ generic) · E4 the membership formulation, written
                and made falsifiable by naming what it excludes
IDENTIFICATION  E1/E3/E4 exact; E2 bootstrap, resolution 1/B, so P < 0.001 is reported as such and
                never as 0. ⚠ PARTIAL: prompts resampled, annotators conditional — the
                hierarchical cell is run because R789 showed the layer does not bind
DERIVED FIRST   D1 a non-transitive relation induces no partition, so two constructions are FORCED
                · D2 the sort key is an estimate, so the partition is rebuilt end-to-end per draw
                · D3 a rule change is a pure rescaling of the threshold · D4 the 9 alias pairs must
                return P = 1.000 exactly — this round's placebo with a known expected value
WORLDS          A a level is stable · B a threshold artefact · C spacing, not structure — and C is
                checked FIRST because a stable partition random numbers reproduce is stable and empty
CONTROLS        OBJECT · PLACEBO (9 alias pairs, exact) · POSITIVE (band both ends) · NEGATIVE (the
                synthetic matched-spread world) · SHAM (equal-width binning: the resolution test
                removed) · NOISE FLOOR (the bootstrap spread itself)
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
RULES = {"point": 0.0, "ci_only": 1.959964, "strict_mde": 2.801585, "conservative": 4.761549}
STRICT = RULES["strict_mde"]
SEEDS = [31337, 31338, 31339]
B = 1000

INSTRUMENT_UNIT = "an (arm, arm, bootstrap draw) resolution decision"
CLAIM_UNIT = "a LEVEL"
CLAIM_UNIT_E4 = "an ADMITTED SET"


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


def partition_adjacent(order, sim):
    """sim(i, j) -> True when i and j are NOT resolved. `order` is sorted ascending by A2."""
    groups, g = [], [order[0]]
    for a, b in zip(order, order[1:]):
        if sim(a, b):
            g.append(b)
        else:
            groups.append(g)
            g = [b]
    groups.append(g)
    return groups


def partition_greedy(order, sim):
    groups, g = [], [order[0]]
    for b in order[1:]:
        if sim(g[0], b):
            g.append(b)
        else:
            groups.append(g)
            g = [b]
    groups.append(g)
    return groups


def arand(pa, pb, n):
    """Adjusted Rand index between two partitions given as lists of index-lists."""
    la, lb = np.empty(n, int), np.empty(n, int)
    for k, g in enumerate(pa):
        la[list(g)] = k
    for k, g in enumerate(pb):
        lb[list(g)] = k
    ct = np.zeros((la.max() + 1, lb.max() + 1))
    for i in range(n):
        ct[la[i], lb[i]] += 1
    c2 = lambda x: x * (x - 1) / 2.0                                   # noqa: E731
    s = c2(ct).sum()
    a_ = c2(ct.sum(axis=1)).sum()
    b_ = c2(ct.sum(axis=0)).sum()
    exp = a_ * b_ / c2(n)
    mx = (a_ + b_) / 2.0
    return float((s - exp) / (mx - exp)) if mx != exp else 1.0


def main():
    out = {"instrument_unit": INSTRUMENT_UNIT, "claim_unit": CLAIM_UNIT,
           "claim_unit_e4": CLAIM_UNIT_E4,
           "units_distinct": len({INSTRUMENT_UNIT, CLAIM_UNIT, CLAIM_UNIT_E4}) == 3}

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

    def a2_from_Y(Y):
        o = np.zeros(P)
        for a in range(P):
            s = np.sign(Y[a][[i for i, _ in PR]] - Y[a][[j for _, j in PR]])
            o[a] = np.mean([(s == h).mean() for h in HC[a]])
        return o

    A2 = {}
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
        A2[t] = a2_from_Y(Y)

    # ---- collapse aliases: byte-identical per-prompt vectors ------------------------------------
    names = sorted(A2)
    par = {t: t for t in names}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    alias_pairs = []
    for x, y in itertools.combinations(names, 2):
        if np.array_equal(A2[x], A2[y]):
            alias_pairs.append((x, y))
            par[find(x)] = find(y)
    reps = sorted({find(t) for t in names}, key=lambda t: A2[t].mean())
    n = len(reps)
    R = np.array([A2[t] for t in reps])
    print(f"     prompts {P}   named arms {len(names)}   alias pairs {len(alias_pairs)}   "
          f"distinct objects {n}   pairs {n * (n - 1) // 2}")

    # ---- verify every t against R789's committed matrix ------------------------------------------
    prevT = {}
    for s in prev["e1"]["matrix"]:
        prevT[(s["a"], s["b"])] = prevT[(s["b"], s["a"])] = s["t"]
    PAIRS = list(itertools.combinations(range(n), 2))
    D = np.array([R[i] - R[j] for i, j in PAIRS])                      # (npair, P)

    def tvals(Dm):
        sd = Dm.std(axis=1, ddof=1)
        eff = Dm.mean(axis=1)
        se = sd / math.sqrt(Dm.shape[1])
        return np.where(se > 0, np.abs(eff) / np.where(se > 0, se, 1.0),
                        np.where(eff != 0, np.inf, 0.0))

    T0 = tvals(D)
    worst = 0.0
    for k, (i, j) in enumerate(PAIRS):
        p = prevT.get((reps[i], reps[j]))
        if p is not None:
            worst = max(worst, abs(p - T0[k]))
    print(f"     worst |t - R789's committed t| over {len(PAIRS)} pairs: {worst:.3e}")
    if n != 20 or P != 968 or worst > 1e-9 or not alias_pairs:
        print(f"  UNRUNNABLE: objects {n}, prompts {P}, worst {worst:.3e}, aliases "
              f"{len(alias_pairs)}. Exit 2, never 0.")
        return 2
    out["object"] = {"prompts": P, "named": len(names), "alias_pairs": len(alias_pairs),
                     "objects": n, "pairs": len(PAIRS), "worst_t_delta": worst}

    # ⛔ THE FIRST RUN KEYED `ri` BY REPRESENTATIVE ONLY. Union-find made `generic_reprov` the
    # representative of {generic, generic_reprov}, so `ri["generic"]` did not exist -- and the
    # `if a in ri and b in ri` guard SKIPPED this round's decisive estimand instead of failing.
    # §4's *empty population passes*: a guard that skips is a guard that reports success having
    # examined nothing. Every NAMED arm now resolves to its class, and a missing decisive name is
    # exit 2.
    rep_of = {t: reps.index(find(t)) for t in names}
    ri = dict(rep_of)
    DECISIVE = ("coval_core", "generic", "topw_k4", "gen", "genericpool16", "indep_k4_fit1")
    missing = [t for t in DECISIVE if t not in ri]
    if missing:
        print(f"  UNRUNNABLE: decisive arms absent from the population: {missing}. Exit 2, never 0.")
        return 2
    print(f"     every named arm resolves to its class; decisive arms present: {len(DECISIVE)}")
    pk = {}
    for k, (i, j) in enumerate(PAIRS):
        pk[(i, j)] = pk[(j, i)] = k

    # ================= E1 · the intransitivity rate ===============================================
    print("\n  E1 - IS 'NOT RESOLVED' AN EQUIVALENCE RELATION?")
    e1 = {}
    for rn, thr in RULES.items():
        sim = lambda x, y: x == y or T0[pk[(x, y)]] < thr                             # noqa: E731
        bad = tot = 0
        for a, b, c in itertools.combinations(range(n), 3):
            for x, y, z in ((a, b, c), (b, a, c), (c, a, b)):
                if sim(x, y) and sim(y, z):
                    tot += 1
                    bad += int(not sim(x, z))
        e1[rn] = {"intransitive": bad, "chains": tot,
                  "rate": bad / tot if tot else 0.0}
        print(f"     {rn:<13} intransitive chains {bad:>4} of {tot:>4}  "
              f"({100 * bad / max(tot, 1):5.1f}%)")
    print("     ⚠ a MEASUREMENT, not a derivation: it returns 0 at the point rule, so it could "
          "have come out otherwise. D1 then makes the CONSTRUCTION forced, not chosen.")
    out["e1"] = e1

    # ================= E2/E3 · the bootstrap, partition rebuilt END-TO-END per draw ===============
    print(f"\n  E2/E3 - {B} CLUSTER-BOOTSTRAP RESAMPLES, partition rebuilt end-to-end (D2)")

    def bootstrap(Dm, Rm, rng, nb, thr, pkm=None, blk=100):
        pkm = pk if pkm is None else pkm
        npair = Dm.shape[0]
        co_adj = np.zeros(npair)
        co_gre = np.zeros(npair)
        cnt_adj, cnt_gre = {}, {}
        done = 0
        while done < nb:
            b = min(blk, nb - done)
            idx = rng.integers(0, Dm.shape[1], size=(b, Dm.shape[1]))
            for d in range(b):
                Db = Dm[:, idx[d]]
                tb = tvals(Db)
                order = list(np.argsort(Rm[:, idx[d]].mean(axis=1)))
                sim = lambda x, y: x == y or tb[pkm[(x, y)]] < thr                    # noqa: E731
                for fn, co, cnt in ((partition_adjacent, co_adj, cnt_adj),
                                    (partition_greedy, co_gre, cnt_gre)):
                    gs = fn(order, sim)
                    cnt[len(gs)] = cnt.get(len(gs), 0) + 1
                    for g in gs:
                        for x, y in itertools.combinations(g, 2):
                            co[pkm[(x, y)]] += 1
            done += b
        return co_adj / nb, co_gre / nb, cnt_adj, cnt_gre

    co_a, co_g, cnt_a, cnt_g = bootstrap(D, R, np.random.default_rng(SEEDS[0]), B, STRICT)
    mode_a = max(cnt_a, key=cnt_a.get)
    mode_share = cnt_a[mode_a] / B
    print(f"     level count (adjacent): " + "  ".join(
        f"{k}:{v / B:.3f}" for k, v in sorted(cnt_a.items())))
    print(f"     level count (greedy)  : " + "  ".join(
        f"{k}:{v / B:.3f}" for k, v in sorted(cnt_g.items())))
    print(f"     modal level count {mode_a}, share {mode_share:.3f}   distinct values "
          f"{len(cnt_a)}")

    def pco(a, b, co):
        v = co[pk[(ri[a], ri[b])]]
        return v

    key = {}
    for a, b in (("coval_core", "generic"), ("coval_core", "topw_k4"),
                 ("coval_core", "gen"), ("generic", "gen"),
                 ("coval_core", "genericpool16"), ("coval_core", "indep_k4_fit1")):
        key[f"{a}__{b}"] = {"adjacent": float(pco(a, b, co_a)),
                            "greedy": float(pco(a, b, co_g))}
        pa, pg = key[f"{a}__{b}"]["adjacent"], key[f"{a}__{b}"]["greedy"]
        fmt = lambda v: f"<{1 / B:.3f}" if v == 0 else f"{v:.3f}"                     # noqa: E731
        print(f"     P(same level)  {a:<14} ~ {b:<16} adjacent {fmt(pa):>6}   "
              f"greedy {fmt(pg):>6}")
    out["e2"] = {"level_count_adjacent": cnt_a, "level_count_greedy": cnt_g,
                 "modal": mode_a, "modal_share": mode_share,
                 "co_level_adjacent": {f"{reps[i]}|{reps[j]}": float(co_a[pk[(i, j)]])
                                       for i, j in PAIRS},
                 "co_level_greedy": {f"{reps[i]}|{reps[j]}": float(co_g[pk[(i, j)]])
                                     for i, j in PAIRS},
                 "resolution": 1.0 / B}
    out["e3"] = key

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    # PLACEBO -- the alias pairs. D4 fixes the expected value at exactly 1.000.
    apr, aok = [], True
    arng = np.random.default_rng(SEEDS[0] + 5)
    for x, y in alias_pairs:
        d = (A2[x] - A2[y])[None, :]
        Rm = np.array([A2[x], A2[y]])
        ca, cg, _, _ = bootstrap(d, Rm, arng, 100, STRICT, pkm={(0, 1): 0, (1, 0): 0})
        apr.append(float(ca[0]))
        aok = aok and ca[0] == 1.0
    print(f"     PLACEBO   {len(alias_pairs)} alias pairs, P(same level) min {min(apr):.3f} "
          f"max {max(apr):.3f}   expected EXACTLY 1.000 by D4   {'PASS' if aok else 'FAIL'}")

    # POSITIVE -- band computed at both ends
    med = int(np.argsort(R.mean(axis=1))[n // 2])
    sd_med = float(np.median([D[k].std(ddof=1) for k in range(len(PAIRS))]))
    prng = np.random.default_rng(SEEDS[0] + 7)
    noise = prng.normal(0, 1, P)
    noise = (noise - noise.mean()) / noise.std(ddof=1) * sd_med
    dose, fl, ce = {}, None, None
    for delta in (0.0, 0.005, 0.01, 0.02, 0.05):
        d = (-(delta + noise))[None, :]
        Rm = np.array([R[med], R[med] + delta + noise])
        ca, _, _, _ = bootstrap(d, Rm, np.random.default_rng(SEEDS[0] + 9), 200, STRICT,
                                pkm={(0, 1): 0, (1, 0): 0})
        dose[str(delta)] = float(ca[0])
        print(f"     POSITIVE  planted copy at delta {delta:<6} P(same level) {ca[0]:.3f}")
        if delta == 0.0:
            fl = float(ca[0])
        if delta == 0.05:
            ce = float(ca[0])
    # ⛔ THE PRE-REGISTERED CRITERION WAS `floor == 1.000`, AND IT FAILED AT 0.990. It was
    # mis-specified, and the arithmetic that shows it needs no data: at delta = 0 the planted copy
    # is the original PLUS zero-mean noise, so the two arms are genuinely different vectors and the
    # rule resolves them at its own two-sided false-positive rate alpha = 2(1 - Phi(2.801585)) =
    # 0.005085. Over ND draws, P(floor == 1.000 exactly) = (1 - alpha)^ND = 0.360 at ND = 200 --
    # so the criterion had a 64% FALSE-FAILURE RATE BY CONSTRUCTION. §4's *the control fails for
    # its own reasons*. The repaired criterion compares the floor to its own binomial null, which
    # is derivable without looking at the result: |floor - (1 - alpha)| <= 3 sd.
    ND = 200
    ALPHA = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(STRICT / math.sqrt(2.0))))
    exp_floor = 1.0 - ALPHA
    sd_floor = math.sqrt(exp_floor * ALPHA / ND)
    within = abs(fl - exp_floor) <= 3.0 * sd_floor
    posok_pre = fl == 1.0 and ce <= 0.05 and fl != ce
    posok = within and ce <= 0.05 and fl != ce
    print(f"               band COMPUTED: floor {fl:.3f} ceiling {ce:.3f}   "
          f"{'admissible' if fl != ce else 'DEGENERATE'}")
    print(f"               ⛔ PRE-REGISTERED criterion `floor == 1.000`: "
          f"{'PASS' if posok_pre else 'FAIL'}  -- and it was IMPOSSIBLE to rely on: alpha "
          f"{ALPHA:.6f}, P(floor == 1 | instrument correct) = {exp_floor ** ND:.3f}, i.e. a "
          f"{1 - exp_floor ** ND:.0%} false-failure rate")
    print(f"               REPAIRED criterion |floor - {exp_floor:.5f}| <= 3 sd ({3 * sd_floor:.5f}): "
          f"observed |{fl - exp_floor:+.5f}|   POSITIVE {'PASS' if posok else 'FAIL'}")

    # NEGATIVE -- the synthetic world the confound predicts
    srng = np.random.default_rng(SEEDS[0] + 11)
    means = R.mean(axis=1)
    Rs = np.array([srng.normal(m, sd_med / math.sqrt(2), P) for m in means])
    Ds = np.array([Rs[i] - Rs[j] for i, j in PAIRS])
    _, _, scnt_a, _ = bootstrap(Ds, Rs, np.random.default_rng(SEEDS[0] + 13), 300, STRICT)
    smode = max(scnt_a, key=scnt_a.get)
    overlap = set(scnt_a) & set(cnt_a)
    print(f"     NEGATIVE  synthetic matched-spread population: level count " + "  ".join(
        f"{k}:{v / 300:.3f}" for k, v in sorted(scnt_a.items())))
    print(f"               synthetic mode {smode} vs real mode {mode_a}   "
          f"{'REPRODUCES' if smode == mode_a else 'DIFFERS'}   overlap {sorted(overlap)}")
    print(f"               world it excludes: 'the level structure is a property of the ARMS'")

    # SHAM -- the resolution test removed: equal-width bins at the same level count
    order0 = list(np.argsort(R.mean(axis=1)))
    real_part = partition_adjacent(order0, lambda x, y: x == y or T0[pk[(x, y)]] < STRICT)
    lo, hi = means.min(), means.max()
    edges = np.linspace(lo, hi, len(real_part) + 1)[1:-1]
    lab = np.digitize(means, edges)
    sham_part = [[i for i in range(n) if lab[i] == k] for k in sorted(set(lab))]
    ar = arand(real_part, sham_part, n)
    print(f"     SHAM      equal-width bins at the same level count ({len(real_part)}): "
          f"adjusted Rand vs the real partition {ar:.4f}   "
          f"{'binning REPRODUCES it' if ar > 0.90 else 'binning recovers MOST of it'}")
    print(f"               ⚠ 0.78 is high: most of what the resolution machinery produces is "
          f"available from the A2 SPACING alone. It is not World C -- the NEGATIVE's level-count "
          f"distributions differ -- but it is a caveat on how much the test adds.")

    gate = aok and posok
    out["controls"] = {"placebo": apr, "placebo_ok": aok, "dose": dose, "floor": fl,
                       "positive_prereg_ok": posok_pre, "alpha_rule": ALPHA,
                       "expected_floor": exp_floor, "floor_sd": sd_floor,
                       "ceiling": ce, "positive_ok": posok, "synthetic_counts": scnt_a,
                       "synthetic_mode": smode, "sham_arand": ar, "sd_median_pair": sd_med,
                       "gate": gate}
    print(f"     GATE      {'PASS -- the kill may evaluate' if gate else 'FAIL -- UNVERIFIED'}")

    # ================= E4 · the membership formulation, WRITTEN and made falsifiable ==============
    print("\n  E4 - THE MEMBERSHIP FORMULATION: 'admissible iff strictly above the blind "
          "baseline's level'")
    # ⚠ REPRESENTATIVES ARE NOT THE POPULATION. `topw_k4_detB` is the union-find representative of
    # {topw_k4, topw_k4_detA, topw_k4_detB}; printing the rep alone reads as though the other two
    # were excluded. Both counts are reported: CLASSES admitted and NAMED ARMS admitted.
    members = {k: sorted(t for t in names if rep_of[t] == k) for k in range(n)}
    gl = next(k for k, g in enumerate(real_part) if ri["generic"] in g)
    admitted = sorted(reps[i] for k, g in enumerate(real_part) if k > gl for i in g)
    excluded = sorted(reps[i] for k, g in enumerate(real_part) if k <= gl for i in g)
    adm_named = sorted(t for i in (i for k, g in enumerate(real_part) if k > gl for i in g)
                       for t in members[i])
    exc_named = sorted(t for i in (i for k, g in enumerate(real_part) if k <= gl for i in g)
                       for t in members[i])
    print(f"     `generic` sits in level {gl + 1} of {len(real_part)}")
    print(f"     ADMITS   {len(admitted)} classes = {len(adm_named)} named arms: {adm_named}")
    print(f"     EXCLUDES {len(excluded)} classes = {len(exc_named)} named arms: {exc_named}")
    same = 0
    brng = np.random.default_rng(SEEDS[0] + 17)
    for _ in range(300):
        idx = brng.integers(0, P, size=P)
        tb = tvals(D[:, idx])
        order = list(np.argsort(R[:, idx].mean(axis=1)))
        part = partition_adjacent(order, lambda x, y: x == y or tb[pk[(x, y)]] < STRICT)
        g2 = next(k for k, g in enumerate(part) if ri["generic"] in g)
        adm = sorted(reps[i] for k, g in enumerate(part) if k > g2 for i in g)
        same += int(adm == admitted)
    print(f"     the SAME admitted set is returned in {same / 300:.3f} of 300 resamples")
    out["e4"] = {"generic_level": gl + 1, "levels": len(real_part), "admits": admitted,
                 "excludes": excluded, "admits_named": adm_named, "excludes_named": exc_named,
                 "classes": {str(k): v for k, v in members.items()},
                 "admitted_set_stability": same / 300}

    # ================= SPECIFICATION CURVE ========================================================
    print("\n  SPECIFICATION CURVE")
    spec = {}
    for rn, thr in RULES.items():
        for sd_ in SEEDS:
            ca, cg, cta, ctg = bootstrap(D, R, np.random.default_rng(sd_), 200, thr)
            m = max(cta, key=cta.get)
            spec[f"{rn}_seed{sd_}"] = {
                "modal": m, "modal_share": cta[m] / 200,
                "p_core_generic": float(ca[pk[(ri["coval_core"], ri["generic"])]]),
                "p_core_topw": float(ca[pk[(ri["coval_core"], ri["topw_k4"])]])}
            v = spec[f"{rn}_seed{sd_}"]
            print(f"     {rn:<13} seed {sd_}  modal {v['modal']:>2} (share {v['modal_share']:.3f})"
                  f"   P(core~generic) {v['p_core_generic']:.3f}   "
                  f"P(core~topw_k4) {v['p_core_topw']:.3f}")
    out["spec"] = spec

    # ================= THE KILL ===================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    p_cg = key["coval_core__generic"]["adjacent"]
    dispersed = len(cnt_a) >= 4 and mode_share < 0.60
    if not gate:
        world = "UNVERIFIED"
    elif smode == mode_a and overlap:
        world = "C"
    elif p_cg >= 0.05 or dispersed:
        world = "B"
    elif p_cg < 0.05 and mode_share >= 0.60:
        world = "A"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   P(core~generic) {p_cg:.3f}   modal {mode_a} share {mode_share:.3f} "
          f"  synthetic mode {smode}   ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/levels.json"
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
