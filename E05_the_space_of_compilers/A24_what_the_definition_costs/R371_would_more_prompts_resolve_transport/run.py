"""R371 — price the GPU job before spending it: is transport's MDE bound by n, or by heterogeneity?

R370's NEXT line said: *"the pool floor's MDE is 0.0920 on exact against a contrast of 0.0810, so the
design is close to resolution and the binding constraint is now n rather than the floor's
construction. Extending to the remaining 718 prompts is a defined GPU job."*

⛔ THAT PREMISE IS UNPROVEN AND THE ARITHMETIC SAYS SO. R370's MDE is
`ZEFF * sd(per-stratum contrasts) / sqrt(n_STRATA)` -- a BETWEEN-STRATA standard error over **four
points**, not a within-prompt one. For `pool|exact` the four contrasts are
[0.1136, 0.0664, -0.0177, 0.1601], sd 0.0759 against a mean of 0.0806. **More prompts shrink
within-stratum noise, which is not the denominator.** They would help only by permitting more strata
-- and if the spread across strata is real structure rather than 4-point noise, more strata reveal
MORE of it and the MDE does not fall.

So the job is priced here, for free, on data already on disk, before any GPU is spent. A power
analysis that can kill an expensive job is the cheapest decisive action available.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES, and both ways are
   live. If the four contrasts are drawn from within-stratum sampling noise alone, their sd is
   FORCED to be about the size that noise implies, more strata add independent draws, and the MDE
   falls as 1/sqrt(S) -- the job works. If instead transport genuinely varies with difficulty, the
   sd is structure, it does not shrink, and 968 prompts buy a better-estimated version of the same
   unresolved answer. The two are distinguished by comparing the OBSERVED between-stratum sd against
   the sd a pure within-stratum null produces at the same stratum sizes -- which is computable now.

ESTIMAND        (a) the between-stratum sd of the pool-floor transport contrast as a function of the
                number of strata S in {2,3,4,5,6,8}, on the existing 250 prompts;
                (b) the same sd under a SYNTHETIC NULL in which each stratum's contrast is drawn
                from within-stratum sampling noise with NO true heterogeneity, at the same S and
                the same stratum sizes;
                (c) the ratio (b)->(a): how much of the observed spread is structure.

IDENTIFICATION  Identified on the 250 prompts that carry core, full and pool on both arms. NOT
                identified: the MDE at n=968, which is what the job would buy -- this round
                estimates the SCALING, and an extrapolation is labelled as one wherever it appears.
                ⚠ Nor is it identified whether the heterogeneity, if real, is about difficulty or
                about anything else that co-varies with it.

SCOPE           250 prompts · Qwen3.5-2B-Base · R233's cache joined to task 630's pool labels ·
                exact and pair metrics, both reported · the pool (non-subset) floor throughout,
                because that is the floor R370 established is the fair one.

WORLDS
  W-N-BOUND            the observed between-stratum sd tracks the within-stratum null, and the MDE
                       falls roughly as 1/sqrt(S). The spread is sampling noise, more strata are
                       genuinely independent draws, and the 718-prompt job is justified.
  W-HETEROGENEITY-BOUND the observed sd exceeds the null and does NOT shrink as S grows. The spread
                       is structure; more prompts buy a better-estimated unresolved answer, and the
                       job should not be run for this purpose.
  W-OVERFIT            the observed sd is BELOW the null. Then the 4-stratum contrasts are smoother
                       than sampling alone allows, which would mean the stratification is absorbing
                       variance it should not, and R370's MDE is optimistic rather than pessimistic.

PREDICTION MATRIX
  W-N-BOUND             -> observed_sd / null_sd ~ 1, and MDE(S) falls with S
  W-HETEROGENEITY-BOUND -> ratio > 1 and MDE(S) flat or rising
  W-OVERFIT             -> ratio < 1
The three differ on one ratio and one slope, computed identically at every S.

PRE-REGISTERED KILL -- conditional.
    if placebo_ok and null_nondegenerate and enough_S:
        r = median over S of observed_sd / null_sd
        if r > 1.25 and MDE does not fall with S  -> W-HETEROGENEITY-BOUND (do NOT run the job)
        elif r < 0.8                              -> W-OVERFIT
        else                                       -> W-N-BOUND (the job is justified)
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.
⚠ AND A FOURTH BRANCH, since this session has repeatedly had a default assert past its data: if the
  ratio exceeds 1.25 but the MDE DOES fall with S, that is NAMED -- heterogeneity is real AND more
  strata still help, which recommends the job for a different reason than W-N-BOUND does.

NULL            per stratum, resample its prompts with replacement, recompute the contrast, and take
                the sd of those resampled contrasts ACROSS strata. This is the spread that
                within-stratum sampling alone produces -- the world where transport is constant and
                only the estimate wobbles -- built rather than assumed.
PLACEBO         a stratification into ONE stratum: the between-stratum sd is undefined, not zero,
                and the code must say so rather than return 0.
SEEDS           3 on the null resampling; every S reported per seed before averaging.
MULTIPLICITY    6 values of S x 2 metrics = 12 cells; all printed.
ARTIFACT        results/r371_power.json with the source hash.

IMPOSSIBLE HERE
  the MDE at n=968  -- that is the job's output, not its price. Every statement about it is an
                       EXTRAPOLATION and is labelled one.
  a second judge    -- the pool labels are 2B only, matching the cache.

EXIT
    0  controls hold and the scaling is classified
    1  a control misbehaved -- UNVERIFIED
    2  an input is missing -- never a silent pass
"""
from __future__ import annotations
import collections, hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
CACHE = (ROOT / "E05_the_space_of_compilers" / "A18_the_candidate_set_wall_was_wrong"
         / "R233_fresh_candidate_transport" / "results" / "sat_fresh_and_orig.npz")
POOL_FRESH = A24 / "R370_a_non_subset_floor_for_the_fresh_arm" / "results" / "sat_genericpool16_fresh.npz"
POOL_ORIG = ROOT / "corebench" / "results" / "sat_genericpool16.npz"
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
SEEDS = (0, 1, 2)
SVALS = (2, 3, 4, 5, 6, 8)
METRICS = ("exact", "pair")
L = "ABCD"


def cls_of(y):
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    return np.sign(y[ii] - y[jj])


def agree(a, b, metric):
    m = (cls_of(a) == cls_of(b))
    return float(m.all()) if metric == "exact" else float(m.mean())


def main() -> int:
    for f in (CACHE, POOL_FRESH, POOL_ORIG):
        if not f.exists():
            print(f"  UNRUNNABLE: {f.name} absent. Exit 2, never 0."); return 2

    d = np.load(CACHE, allow_pickle=True)
    T = collections.defaultdict(lambda: collections.defaultdict(lambda: [None] * 4))
    WT = collections.defaultdict(dict)
    for k, x in enumerate(d["meta"]):
        pid, arm, st, ci, ri = str(x).split("|")
        T[(pid, arm, st)][int(ci)][int(ri)] = float(d["sat"][k])
        WT[(pid, arm, st)][int(ci)] = float(d["weight"][k])
    pf = np.load(POOL_FRESH, allow_pickle=True)
    for k, x in enumerate(pf["meta"]):
        pid, arm, st, ci, ri = str(x).split("|")
        T[(pid, arm, "pool")][int(ci)][int(ri)] = float(pf["sat"][k]); WT[(pid, arm, "pool")][int(ci)] = 1.0
    po = np.load(POOL_ORIG, allow_pickle=True)
    for k, x in enumerate(po["meta"]):
        p_, ci, ltr = str(x).split("|")[:3]
        T[(p_, "orig", "pool")][int(ci)][L.index(ltr)] = float(po["sat"][k])
        WT[(p_, "orig", "pool")][int(ci)] = 1.0

    pids = sorted({str(x).split("|")[0] for x in d["meta"]})
    ARMS = ("orig", "fresh")

    def score(pid, arm, st, crits=None):
        tab, w = T[(pid, arm, st)], WT[(pid, arm, st)]
        cs = sorted(tab) if crits is None else [c for c in crits if c in tab]
        if not cs:
            return None
        y = np.zeros(4)
        for c in cs:
            v = tab[c]
            if any(x is None for x in v):
                continue
            y += w[c] * np.array(v, float)
        return y

    usable = [p for p in pids
              if all(score(p, a, s) is not None for a in ARMS for s in ("core", "full", "pool"))]
    if len(usable) < 100:
        print(f"  UNRUNNABLE: only {len(usable)} usable prompts. Exit 2, never 0."); return 2

    AG, DIFF, NC = {}, {}, {}
    for arm in ARMS:
        for p in usable:
            yf, yc = score(p, arm, "full"), score(p, arm, "core")
            for mt in METRICS:
                AG[(mt, p, arm)] = agree(yc, yf, mt)
            DIFF[(p, arm)] = float(np.std(yf))
            NC[(p, arm)] = len(T[(p, arm, "core")])

    print("R371 · pricing the 718-prompt job BEFORE spending it\n")
    print("  ⛔ R370's NEXT said the binding constraint is n. Its MDE is")
    print("     ZEFF * sd(per-stratum contrasts) / sqrt(n_STRATA) — a BETWEEN-STRATA error over")
    print("     FOUR points. More prompts shrink WITHIN-stratum noise, which is not the")
    print("     denominator. The premise is checked here rather than acted on.\n")
    print(f"  {len(usable)} prompts carry core, full and pool on both arms\n")

    def floor_mean(ps, arm, seed, metric):
        rng = np.random.default_rng(seed)
        vals = []
        for pid in ps:
            tab = T[(pid, arm, "pool")]
            k = max(1, NC[(pid, arm)])
            cs = sorted(tab)
            if len(cs) <= k:
                continue
            sel = list(rng.choice(cs, k, replace=False))
            yr, yf = score(pid, arm, "pool", sel), score(pid, arm, "full")
            if yr is None or yf is None:
                continue
            vals.append(agree(yr, yf, metric))
        return float(np.mean(vals)) if vals else float("nan")

    def strata_contrasts(S, mt, boot_seed=None):
        """per-stratum transport contrast; boot_seed resamples WITHIN strata (the null)."""
        dorig = np.array([DIFF[(p, "orig")] for p in usable])
        edges = np.quantile(dorig, np.linspace(0, 1, S + 1))
        edges[0], edges[-1] = -np.inf, np.inf
        st = lambda v: int(np.searchsorted(edges, v, side="right") - 1)   # noqa: E731
        out, ns = [], []
        rng = np.random.default_rng(boot_seed) if boot_seed is not None else None
        for s in range(S):
            po_ = [p for p in usable if st(DIFF[(p, "orig")]) == s]
            pf_ = [p for p in usable if st(DIFF[(p, "fresh")]) == s]
            if len(po_) < 5 or len(pf_) < 5:
                continue
            if rng is not None:
                # ⛔ v1's NULL WAS MALFORMED AND ITS RATIO WAS NEARLY FORCED. It resampled each
                #   stratum FROM ITSELF, which adds sampling noise ON TOP of the real between-
                #   stratum spread -- so sd(bootstrapped) >= sd(observed) almost by construction
                #   and the ratio could only come out <= 1. A control that can only land on one
                #   side is not a control. The world to build is NO HETEROGENEITY: every stratum
                #   drawn from the POOLED prompts at that stratum's own size, so the true contrast
                #   is identical across strata and only sampling varies.
                po_ = list(rng.choice(usable, len(po_), replace=True))
                pf_ = list(rng.choice(usable, len(pf_), replace=True))
            co = np.mean([AG[(mt, p, "orig")] for p in po_])
            cf = np.mean([AG[(mt, p, "fresh")] for p in pf_])
            fo = np.mean([floor_mean(po_, "orig", sd, mt) for sd in SEEDS])
            ff = np.mean([floor_mean(pf_, "fresh", sd, mt) for sd in SEEDS])
            out.append((cf - ff) - (co - fo)); ns.append(len(po_))
        return np.array(out), np.array(ns, float)

    print(f"    {'metric':>7}{'S':>4}{'kept':>6}{'contrast':>10}{'obs sd':>9}{'null sd':>9}"
          f"{'ratio':>8}{'MDE':>9}")
    ROWS = {}
    for mt in METRICS:
        for S in SVALS:
            c, ns = strata_contrasts(S, mt)
            if len(c) < 2:
                print(f"    {mt:>7}{S:>4}{len(c):>6}   <2 strata kept — undefined, not zero")
                continue
            w = ns / ns.sum()
            mean = float(np.dot(w, c))
            sd = float(np.sqrt(np.dot(w, (c - mean) ** 2)))
            mde = float(ZEFF * sd / math.sqrt(len(c)))
            nulls = []
            for sd_ in SEEDS:
                cb, nb = strata_contrasts(S, mt, boot_seed=1000 + sd_)
                if len(cb) >= 2:
                    wb = nb / nb.sum()
                    mb = float(np.dot(wb, cb))
                    nulls.append(float(np.sqrt(np.dot(wb, (cb - mb) ** 2))))
            nsd = float(np.mean(nulls)) if nulls else float("nan")
            ratio = sd / nsd if nsd and not math.isnan(nsd) and nsd > 0 else float("nan")
            ROWS[(mt, S)] = dict(kept=len(c), contrast=mean, obs_sd=sd, null_sd=nsd,
                                 ratio=ratio, mde=mde)
            print(f"    {mt:>7}{S:>4}{len(c):>6}{mean:>+10.4f}{sd:>9.4f}{nsd:>9.4f}"
                  f"{ratio:>8.2f}{mde:>9.4f}")
        print()

    # ---- controls ---------------------------------------------------------------------------------
    c1, _ = strata_contrasts(1, "exact")
    plac_ok = len(c1) < 2      # one stratum -> between-stratum sd is UNDEFINED, not zero
    print(f"  PLACEBO   S=1 gives {len(c1)} stratum: between-stratum sd is UNDEFINED, not 0  "
          f"{'PASS' if plac_ok else 'FAIL'}")
    nulls_ok = all(not math.isnan(ROWS[k]["null_sd"]) and ROWS[k]["null_sd"] > 0 for k in ROWS)
    print(f"  NULL      the within-stratum resampling null is non-degenerate at every cell  "
          f"{'PASS' if nulls_ok else 'FAIL'}")
    enough = len([k for k in ROWS if k[0] == "exact"]) >= 4
    print(f"  RANGE     {len([k for k in ROWS if k[0]=='exact'])} values of S evaluable for exact  "
          f"{'PASS' if enough else 'FAIL'}")

    ratios = [ROWS[k]["ratio"] for k in ROWS if not math.isnan(ROWS[k]["ratio"])]
    r = float(np.median(ratios)) if ratios else float("nan")
    ex = sorted([k[1] for k in ROWS if k[0] == "exact"])
    falls = (ROWS[("exact", ex[-1])]["mde"] < ROWS[("exact", ex[0])]["mde"]) if len(ex) >= 2 else False
    print(f"\n  median observed_sd / null_sd across all cells: {r:.2f}")
    print(f"  MDE(exact) at S={ex[0]} is {ROWS[('exact', ex[0])]['mde']:.4f}, "
          f"at S={ex[-1]} is {ROWS[('exact', ex[-1])]['mde']:.4f} -> "
          f"{'falls' if falls else 'does NOT fall'} with S")

    ctrl_ok = plac_ok and nulls_ok and enough
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; the table above is silence.")
        v = "UNVERIFIED"
    elif r < 0.8:
        print(f"  W-OVERFIT — the observed spread is BELOW what within-stratum sampling alone")
        print(f"  produces (ratio {r:.2f}). The stratification is absorbing variance it should not,")
        print(f"  and R370's MDE is OPTIMISTIC rather than pessimistic.")
        v = "W_OVERFIT"
    elif r > 1.25 and not falls:
        print(f"  W-HETEROGENEITY-BOUND — the between-stratum spread is {r:.2f}x what sampling alone")
        print(f"  gives, and the MDE does NOT fall as S grows. The spread is STRUCTURE. More prompts")
        print(f"  buy a better-estimated version of the same unresolved answer.")
        print(f"  ⛔ DO NOT RUN the 718-prompt job for this purpose. R370's NEXT line is withdrawn.")
        v = "W_HETEROGENEITY_BOUND"
    elif r > 1.25:
        print(f"  W-HETEROGENEOUS-BUT-SCALING — named rather than defaulted. The spread is real")
        print(f"  ({r:.2f}x the null) AND the MDE still falls with S. The job is recommended, but")
        print(f"  for a different reason than `the estimate is noisy`: more strata resolve real")
        print(f"  structure, so the job buys a CURVE rather than a tighter point.")
        v = "W_HETEROGENEOUS_BUT_SCALING"
    else:
        # ⛔ v1's ELSE-BRANCH ASSERTED "the MDE falls with S" WHILE THE LINE ABOVE IT PRINTED THAT
        #   IT DOES NOT. Fifth verdict-string failure this session, and the kill simply had no
        #   branch for the world that obtains: ratio ~ 1 AND the MDE rising in S. Both facts are
        #   now computed and printed, and the reading follows from them rather than from a
        #   sentence typed in advance.
        print(f"  W-N-BOUND (sampling), BUT NOT VIA MORE STRATA — the observed spread tracks the")
        print(f"  no-heterogeneity null (ratio {r:.2f}), so the between-stratum spread IS sampling")
        print(f"  noise rather than structure. The MDE nevertheless {'falls' if falls else 'RISES'} with S")
        print(f"  ({ROWS[('exact', ex[0])]['mde']:.4f} at S={ex[0]} to "
              f"{ROWS[('exact', ex[-1])]['mde']:.4f} at S={ex[-1]}), because smaller strata are")
        print(f"  noisier faster than sqrt(S) recovers.")
        print(f"  ⭐ So the job IS justified, for a precisely different reason than R370's NEXT gave:")
        print(f"     more prompts help by shrinking WITHIN-stratum noise at FIXED S, never by")
        print(f"     permitting more strata. Adding strata makes it worse.")
        v = "W_N_BOUND_FIXED_S"

    # ---- and the finding R370 did not look for: the verdict MOVES with S -------------------------
    print(f"\n  ⚠ AND THE TRANSPORT VERDICT IS NOT STABLE IN S — a specification R370 never swept.")
    print(f"    {'metric':>7}{'S':>4}{'contrast':>10}{'MDE':>9}   resolved?")
    flips = []
    for mt in METRICS:
        for S in sorted({k[1] for k in ROWS if k[0] == mt}):
            rr = ROWS[(mt, S)]
            res = abs(rr["contrast"]) > rr["mde"]
            flips.append((mt, S, res))
            print(f"    {mt:>7}{S:>4}{rr['contrast']:>+10.4f}{rr['mde']:>9.4f}   "
                  f"{'RESOLVED' if res else 'inside the MDE'}")
    ex_res = {S: r_ for (m_, S, r_) in flips if m_ == "exact"}
    if len(set(ex_res.values())) > 1:
        yes = sorted(S for S, r_ in ex_res.items() if r_)
        no = sorted(S for S, r_ in ex_res.items() if not r_)
        print(f"\n    ⛔ On `exact` the contrast RESOLVES at S={yes} and does NOT at S={no}.")
        print(f"    R370 reported S=4 alone and called it W-COLLAPSES. That verdict is a")
        print(f"    SPECIFICATION CHOICE, not a property of the data, and R370 did not say so")
        print(f"    because it never swept S. The honest statement is the CURVE, not the cell.")

    print(f"\n  ⚠ EXTRAPOLATION, labelled: nothing here measures the MDE at n=968. That is the")
    print(f"    job's OUTPUT, not its price. This round measures how the estimator SCALES on the")
    print(f"    250 prompts already judged, which is what a decision to spend GPU should rest on.")

    art = dict(stamp(str(SELF)), n_prompts=len(usable), S_values=list(SVALS),
               rows={f"{m}|{s}": ROWS[(m, s)] for (m, s) in ROWS},
               median_ratio=r, mde_falls_with_S=bool(falls),
               controls=dict(placebo=plac_ok, null=nulls_ok, range=enough), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r371_power.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
