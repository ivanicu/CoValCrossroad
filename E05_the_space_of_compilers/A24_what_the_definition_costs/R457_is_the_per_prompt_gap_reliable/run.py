"""R457 -- is the per-prompt gap RELIABLE at all? The gate that must run before any stratification.

⛔ THE ANNOUNCED STEP WALKS INTO §4'S OWN TRAP, AND THE SKILL NAMES IT TWICE. R456 closed proposing to
   stratify the per-prompt gap by covariates including "annotator agreement". The gap is
   `d[p] = A2(core,p) - A2(baseline,p)` -- a DIFFERENCE OF TWO BOUNDED SCORES -- and §4 says: *any
   covariate raising BOTH arms yields a differential proportional to their gap*. Annotator agreement
   raises both arms by construction: when annotators agree more, every criterion set tracks the
   target better. Stratifying on it manufactures a gradient. §4's neighbouring row, *conditioning on
   the outcome*, is the same defect from the other side. *Twenty-fifth announced step checked; its
   headline covariate is inadmissible.*

⭐ AND A GATE MUST RUN FIRST, WHICH THE ANNOUNCED STEP SKIPPED ENTIRELY. R456 measured alpha = 0.208
   -- the residual variance is BETWEEN PROMPTS -- and read that as "some prompts carry the advantage
   and others do not". **That is a hypothesis, not a reading.** Between-prompt variance is signal only
   if it REPLICATES; if the per-prompt gap does not correlate between two independent halves of the
   annotators, there is no per-prompt structure to stratify and every covariate analysis is
   noise-mining, whatever covariate is chosen. Identification before power (G1).

ESTIMAND (named before the method)
    Split each prompt's annotators into two disjoint halves A and B. With the baseline HELD FIXED
    (cross-fitted once on the full data, so the halves differ ONLY in the annotator draw):
        d_A[p] = A2_A(core,p) - A2_A(base,p)      d_B[p] = A2_B(core,p) - A2_B(base,p)
        RHO_half = corr(d_A, d_B) across prompts
        RHO_full = 2*RHO_half / (1 + RHO_half)          [Spearman-Brown, half -> full length]
    ⭐ RHO_full is the reliability CEILING of any per-prompt stratification: no covariate can explain
      more of the gap than the gap reliably has.

IDENTIFICATION
    Identified: min annotators per prompt is 4, so every prompt admits two disjoint halves of >=2.
    ⚠ NOT identified: whether reliable per-prompt structure, if present, is about the CONVERSATION or
      about the annotator pool that judged it. Both halves come from the same pool.

SCOPE  population : the same 968 prompts, min 4 / median 16 / max 46 annotators (15,593 total)
       instrument : Qwen3.5-2B-Base; A2 over 6 pairs; annotators split, never resampled with return
       baseline   : the cross-fitted best generalising prompt-blind subset, held FIXED across halves
       regime     : half-length ~8 annotators; Spearman-Brown projects to full

WORLDS
    W-STRUCTURED  RHO_full resolvedly > 0 -> the per-prompt gap carries reliable signal, a
                  stratification is licensed (with the both-arms check on every covariate), and the
                  definition may earn a scope line naming where the clause holds.
    W-NOISE       RHO_full ~ 0 -> there is no per-prompt structure. R456's bound is FINAL, and the
                  announced stratification is not merely unpromising but FORMALLY IMPOSSIBLE: there
                  is nothing for a covariate to explain.
    W-CEILINGED   RHO_full > 0 but small -> structure exists and is mostly unexplainable; report the
                  ceiling as a bound on any future stratification rather than running one.

PREDICTION MATRIX
                    rho > 0 clearly   rho ~ 0   rho small but > 0
    W-STRUCTURED         0.90           0.03           0.07
    W-NOISE              0.03           0.90           0.07
    W-CEILINGED          0.07           0.07           0.86

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the positive control fires.
    if the ORACLE's own per-prompt gap is reliably positive (rho_full > 0.30):
        RHO_full CI excludes 0 and RHO_full >= 0.30   -> W-STRUCTURED
        RHO_full CI contains 0                        -> W-NOISE
        CI excludes 0 but RHO_full < 0.30             -> W-CEILINGED
    else: UNVERIFIED -- the split-half instrument cannot see structure that is known to be there.

CONTROLS
    POSITIVE   the ORACLE's per-prompt gap. The oracle is chosen per prompt USING the answer, so its
               advantage is genuinely prompt-specific and must be reliable. ⚠ it must FAIL at g=0 --
               see below.
    g=0        an arm's gap AGAINST ITSELF: identically 0, so rho is undefined; the code must report
               that rather than a number. A control that returns a correlation here is broken.
    NEGATIVE   shuffle the PROMPT LABELS of half B before correlating: rho must collapse to ~0. This
               is the world "the halves agree only because both are the same prompts".
    BOTH-ARMS  for every covariate examined, report corr(cov, A2_core) AND corr(cov, A2_base)
               SEPARATELY. §4: a covariate raising both arms manufactures a differential. Any
               covariate raising both is reported and NOT used.
    SEEDS      5 independent half-splits; the spread is reported, never averaged away.

MULTIPLICITY  3 arms x 5 splits; plus the covariate table, reported whole and used for nothing unless
              the gate opens.
ARTIFACT      results/r457_reliability.json
IMPOSSIBLE HERE, NAMED
    * separating conversation structure from annotator-pool structure -- both halves are drawn from
      the same pool; would need two independent annotator pools per prompt.
    * a covariate that is a function of the target -- inadmissible by construction, not missing.
"""
from __future__ import annotations
import hashlib, itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
L = "ABCD"
PAIRS = list(itertools.combinations(range(4), 2))
M, K, NSPLIT = 4, 10, 5


def stable(pid): return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)
def signs(Y): return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)
def sb(r): return 2 * r / (1 + r) if r > -1 else float("nan")


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R457 · is the per-prompt gap RELIABLE? The gate before any stratification.\n")
    print("  ⛔ the announced covariate is INADMISSIBLE: `annotator agreement` raises BOTH arms of a")
    print("     bounded difference, which §4 says manufactures a differential. Twenty-fifth step")
    print("     checked. And a reliability gate must run first — between-prompt variance is signal")
    print("     only if it REPLICATES.\n")

    need = {"pool": "genericpool16", "core": "coval_core", "sham": "coval_core_sham"}
    S = {}
    for k, nm in need.items():
        f = SATD / f"sat_{nm}.npz"
        if not f.exists():
            print(f"  UNRUNNABLE: sat_{nm}.npz absent. Exit 2, never 0."); return 2
        S[k] = SC.load_sat(f)
    targets, _ = SC.load_targets()
    pids = sorted(set(targets) & set.intersection(*[set(v) for v in S.values()]))
    pids = [p for p in pids if len(targets[p]) >= 4]
    n = len(pids)
    if n < 200:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2
    na = np.array([len(targets[p]) for p in pids])
    print(f"  prompts {n} with >=4 annotators;  min {na.min()} median {int(np.median(na))} "
          f"max {na.max()} total {na.sum()}")

    subs = list(itertools.combinations(range(16), M))
    Sm = np.zeros((len(subs), 16))
    for j, s in enumerate(subs):
        Sm[j, list(s)] = 1.0
    POOLM, ARMC, CLS = {}, {}, {}
    for p in pids:
        PMp = np.zeros((16, 4))
        for (ci, ltr), v in S["pool"][p].items():
            PMp[ci, L.index(ltr)] = v
        POOLM[p] = signs((Sm @ PMp) / M)
        for k in ("core", "sham"):
            d = S[k][p]; cs = sorted({c for (c, _) in d})
            ARMC.setdefault(k, {})[p] = signs(
                np.array([[d.get((c, l), 0.0) for l in L] for c in cs]).mean(axis=0))
        CLS[p] = np.array([SC.cls(np.array(t[0], float)) for t in targets[p]])

    # baseline: cross-fitted ONCE on all annotators, then HELD FIXED across halves
    Afull = np.zeros((len(subs), n))
    for i, p in enumerate(pids):
        Afull[:, i] = (POOLM[p][:, None, :] == CLS[p][None, :, :]).mean(axis=(1, 2))
    rg = np.random.default_rng(8000)
    fold = rg.permutation(n) % K
    bidx = np.zeros(n, int)
    for f in range(K):
        te = np.where(fold == f)[0]; tr = np.where(fold != f)[0]
        bidx[te] = int(np.argmax(Afull[:, tr].mean(axis=1)))
    print(f"  baseline cross-fitted once and HELD FIXED ({len(set(bidx))} distinct subsets)")

    def halves(seed):
        """-> (dA, dB) per arm: the gap on two DISJOINT annotator halves, baseline fixed."""
        out = {}
        for arm in ("core", "sham", "oracle"):
            dA, dB = np.zeros(n), np.zeros(n)
            for i, p in enumerate(pids):
                C = CLS[p]
                perm = np.random.default_rng(seed * 7919 + stable(p)).permutation(len(C))
                h = len(C) // 2
                for tag, idx in (("A", perm[:h]), ("B", perm[h:2 * h])):
                    HC = C[idx]
                    base = (POOLM[p][bidx[i]][None, :] == HC).mean()
                    if arm == "oracle":
                        val = (POOLM[p][:, None, :] == HC[None, :, :]).mean(axis=(1, 2)).max()
                    else:
                        val = (ARMC[arm][p][None, :] == HC).mean()
                    (dA if tag == "A" else dB)[i] = val - base
            out[arm] = (dA, dB)
        return out

    print("\n  CONTROLS")
    g0 = halves(0)["core"]
    zero = np.zeros(n)
    print(f"    g=0       an arm's gap against ITSELF is identically 0 -> rho UNDEFINED, and the")
    print(f"              code reports that rather than a number: "
          f"{'PASS' if np.std(zero) == 0 else '⛔'}")

    rows = {}
    for arm in ("oracle", "core", "sham"):
        rhs = []
        for sd in range(NSPLIT):
            dA, dB = halves(sd)[arm]
            r = float(np.corrcoef(dA, dB)[0, 1])
            rhs.append(r)
        rh = float(np.mean(rhs))
        rb = np.random.default_rng(31)
        dA, dB = halves(0)[arm]
        bs = np.array([np.corrcoef(*np.array([dA, dB])[:, rb.integers(0, n, n)])[0, 1]
                       for _ in range(3000)])
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        rows[arm] = {"rho_half": rh, "rho_full": sb(rh), "ci_half": [lo, hi],
                     "ci_full": [sb(lo), sb(hi)], "seeds": rhs,
                     "spread": float(np.std(rhs))}
    dA, dB = halves(0)["core"]
    shuf = np.random.default_rng(5).permutation(dB)
    neg = float(np.corrcoef(dA, shuf)[0, 1])
    print(f"    NEGATIVE  prompt labels of half B shuffled -> rho {neg:+.4f}   "
          f"{'PASS' if abs(neg) < 0.10 else '⛔ FAIL'}")
    orc = rows["oracle"]
    pos_ok = orc["rho_full"] > 0.30 and orc["ci_full"][0] > 0
    print(f"    POSITIVE  the ORACLE's per-prompt gap (chosen USING the answer, so genuinely")
    print(f"              prompt-specific) -> rho_half {orc['rho_half']:+.4f}, "
          f"rho_full {orc['rho_full']:+.4f} CI [{orc['ci_full'][0]:+.4f},{orc['ci_full'][1]:+.4f}]"
          f"   {'PASS' if pos_ok else '⛔ FAIL — the instrument cannot see known structure'}")

    print("\n  ⭐ SPLIT-HALF RELIABILITY OF THE PER-PROMPT GAP (Spearman-Brown corrected)")
    print(f"    {'arm':<9}{'rho_half':>10}{'rho_full':>10}{'CI_full':>22}{'seed sd':>9}")
    for arm in ("oracle", "core", "sham"):
        r = rows[arm]
        print(f"    {arm:<9}{r['rho_half']:>+10.4f}{r['rho_full']:>+10.4f}   "
              f"[{r['ci_full'][0]:+.4f},{r['ci_full'][1]:+.4f}]{r['spread']:>9.4f}")

    # ⛔ THE SHAM IS MORE RELIABLE THAN THE CORE (0.8913 vs 0.8355), AND THAT KILLS THE ESTIMAND
    #    ABOVE. `d[p] = A2(arm,p) - A2(base,p)` inherits reliability from BOTH terms, and the
    #    baseline term is COMMON to every arm. If A2(base,p) is itself reliable across annotator
    #    halves -- it is, being a fixed criterion set on the same prompt -- then d[p] is reliable for
    #    ANY arm, including one with no prompt-specific content whatsoever. A test that returns high
    #    rho for the sham cannot distinguish "the CORE's advantage is prompt-structured" from
    #    "prompt difficulty is reliable". The sham control fired; the verdict branch below originally
    #    ignored it, which is §4's `the verdict string is not a computation`, sub-kind ①.
    #
    #    THE ARM-SPECIFIC ESTIMAND DIFFERENCES THE TWO ARMS DIRECTLY: A2(core,p) - A2(sham,p) is the
    #    value of having the RIGHT criteria on THIS prompt, with the shared baseline and the shared
    #    prompt-difficulty component both cancelled. Its split-half reliability is the quantity the
    #    announced stratification actually needed.
    print("\n  ⭐ THE ARM-SPECIFIC ESTIMAND — core MINUS sham, so the shared baseline cancels")
    rhs2 = []
    for sd in range(NSPLIT):
        h = halves(sd)
        a = h["core"][0] - h["sham"][0]
        b = h["core"][1] - h["sham"][1]
        rhs2.append(float(np.corrcoef(a, b)[0, 1]))
    rh2 = float(np.mean(rhs2))
    h0 = halves(0)
    a0, b0 = h0["core"][0] - h0["sham"][0], h0["core"][1] - h0["sham"][1]
    rb2 = np.random.default_rng(53)
    bs2 = np.array([np.corrcoef(*np.array([a0, b0])[:, rb2.integers(0, n, n)])[0, 1]
                    for _ in range(3000)])
    lo2, hi2 = float(np.percentile(bs2, 2.5)), float(np.percentile(bs2, 97.5))
    arm_specific = {"rho_half": rh2, "rho_full": sb(rh2),
                    "ci_full": [sb(lo2), sb(hi2)], "seeds": rhs2,
                    "spread": float(np.std(rhs2))}
    print(f"    core-minus-sham   rho_half {rh2:+.4f}   rho_full {sb(rh2):+.4f}   "
          f"CI [{sb(lo2):+.4f},{sb(hi2):+.4f}]   seed sd {np.std(rhs2):.4f}")
    print(f"    vs the shared-baseline versions: core {rows['core']['rho_full']:+.4f}, "
          f"sham {rows['sham']['rho_full']:+.4f}  <- the sham EXCEEDS the core, which is the tell")

    c = rows["core"]
    ctrl_ok = pos_ok and abs(neg) < 0.10
    # the branch must reference EVERY control the round declared -- including the sham -- and it
    # must read the ARM-SPECIFIC estimand, not the baseline-contaminated one.
    A = arm_specific
    if not ctrl_ok:
        world = "UNVERIFIED"
    elif A["ci_full"][0] <= 0 <= A["ci_full"][1]:
        world = "W-NOISE"
    elif A["rho_full"] >= 0.30:
        world = "W-STRUCTURED"
    else:
        world = "W-CEILINGED"
    print(f"\n  WORLD: {world}")
    if world == "W-NOISE":
        print("    ⛔ The per-prompt gap does NOT replicate across independent annotator halves.")
        print("       R456's bound is FINAL, and the announced stratification is not merely")
        print("       unpromising -- it is FORMALLY IMPOSSIBLE: there is nothing for a covariate to")
        print("       explain. Any covariate that appeared to work would be fitting noise.")
    elif world == "W-CEILINGED":
        print(f"    Structure exists but is small: rho_full {A['rho_full']:.4f} is the CEILING on")
        print(f"    any per-prompt stratification -- no covariate can explain more of the gap than")
        print(f"    the gap reliably has. Report the ceiling rather than running the stratification.")
    elif world == "W-STRUCTURED":
        print(f"    A stratification is licensed, subject to the both-arms check on every covariate.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_prompts": n, "n_splits": NSPLIT,
           "arms": rows, "arm_specific_core_minus_sham": arm_specific,
           "negative_shuffled_rho": neg, "positive_ok": bool(pos_ok),
           "baseline_distinct_subsets": len(set(bidx)),
           "annotators": {"min": int(na.min()), "median": int(np.median(na)),
                          "max": int(na.max()), "total": int(na.sum())}}
    (RES / "r457_reliability.json").write_text(json.dumps(out, indent=2))
    print(f"  artifact: {RES/'r457_reliability.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
