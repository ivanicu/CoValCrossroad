"""R458 -- how much of the RELIABLE per-prompt advantage do target-free features explain?

⛔ THE ANNOUNCED STEP OVERCLAIMED ITS OWN NULL. R457 closed: "a null there would be the strongest
   statement available: the advantage varies by prompt in a way nothing observable predicts."
   **A null on THREE hand-picked covariates says those three.** "Nothing observable" is a quantifier
   over an unenumerated population -- §4's `closing sentence` row names exactly this, and its tell is
   the word *nothing*. *Twenty-sixth announced step checked; its framing corrected before running.*

⭐ AND A STRONGER DESIGN IS AVAILABLE FOR THE SAME COST. Instead of three cherry-picked covariates,
   fit a CROSS-FITTED predictor from a whole target-free feature set and report out-of-fold R²
   against R457's measured reliability ceiling. That converts "does covariate X matter" into "how
   much is explainable at all", which is the question the definition needs, and it makes the null
   quantitative instead of rhetorical.

⚠ EVERY FEATURE IS TARGET-FREE BY CONSTRUCTION. Nothing here touches the human ranking. That is not
  a preference: §4 says a covariate raising BOTH arms of a bounded difference manufactures a
  differential, and anything derived from the target raises both. The both-arms diagnostic is printed
  for every feature anyway, including those that survive.

ESTIMAND (named before the method)
    d[p] = A2(core,p) - A2(sham,p)   -- R457's ARM-SPECIFIC estimand: the value of having the RIGHT
    criteria on this prompt, with the shared baseline and shared prompt-difficulty cancelled.
    R2_oof = out-of-fold R² of a 10-fold cross-fitted ridge predicting d[p] from target-free features.
    ⭐ Compared against R457's reliability ceiling rho_full = 0.8812: a predictor of an observed
      variable with reliability r cannot exceed R² = r, so 0.8812 is the arithmetic ceiling and
      R2_oof / 0.8812 is the share of RELIABLE variance explained.

IDENTIFICATION
    Identified: features and outcome are both on disk. ⚠ NOT identified: any claim about features
    NOT in the set. The scope line names the set; "nothing observable" is not a statement this or any
    finite design can make.

SCOPE  population : the 968 home-release prompts
       instrument : Qwen3.5-2B-Base; A2 over 6 pairs, all annotators per prompt
       baseline   : R457's ceiling 0.8812; and an out-of-fold R² whose null is 0, not 1/(n-p)
       regime     : ridge, 10-fold cross-fitted, features standardised within training folds only

WORLDS
    W-EXPLAINED  R2_oof >= 0.30 -> observable, target-free structure explains a substantial share of
                 where the core's advantage lives. The definition can earn a scope line naming it.
    W-OPAQUE     R2_oof ~ 0 -> THESE features explain none of a reliably-varying quantity. The
                 advantage is prompt-specific, replicable, and unexplained by the observables tried.
    W-PARTIAL    in between -> report the share of reliable variance as a bound.

PREDICTION MATRIX
                    R2 >= 0.30   R2 ~ 0   in between
    W-EXPLAINED        0.90        0.03      0.07
    W-OPAQUE           0.03        0.90      0.07
    W-PARTIAL          0.07        0.07      0.86

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the controls fire.
    if POSITIVE recovers a planted feature at R2_oof > 0.80 and does NOT fire at g=0:
        R2_oof >= 0.30                      -> W-EXPLAINED
        R2_oof <= 0.05                      -> W-OPAQUE
        otherwise                           -> W-PARTIAL, reported as a share of the ceiling
    else: UNVERIFIED.

CONTROLS
    POSITIVE   append a planted feature `d + noise` to the matrix; the pipeline must recover it at
               high out-of-fold R². ⚠ and it must FAIL at g=0 -- a pure-noise appended feature must
               not raise R2_oof above the unplanted value.
    NEGATIVE   shuffle d against the features: out-of-fold R² must sit at or below 0 (it CAN go
               negative, which is the property that makes it an honest null here).
    BOTH-ARMS  for every feature, corr(feat, A2_core) and corr(feat, A2_sham) printed SEPARATELY.
               §4: a covariate raising both arms manufactures a differential.
    CEILING    R457's rho_full = 0.8812, stated, so R2_oof is read as a SHARE and never as an
               absolute.
    SEEDS      3 fold assignments; spread reported.

MULTIPLICITY  1 outcome x 4 feature blocks x 3 seeds, plus the per-feature both-arms table; all
              printed, nothing selected.
ARTIFACT      results/r458_explainability.json
IMPOSSIBLE HERE, NAMED
    * a statement about features not in the set -- no finite design makes it, and the announced
      "nothing observable" was exactly that.
    * semantic features of the prompt -- would need an embedding model; the round is confined to what  REQUIRES: INTERVENTION
      is computable from the release without a second instrument.
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
K = 10
CEILING = 0.8812     # R457, Spearman-Brown corrected reliability of d


def stable(pid): return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)
def signs(Y): return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)


def ridge_oof(X, y, seed, lam=1.0):
    """10-fold cross-fitted ridge; standardisation fitted on TRAIN only. -> out-of-fold R²."""
    n = len(y)
    fold = np.random.default_rng(seed).permutation(n) % K
    pred = np.zeros(n)
    for f in range(K):
        te = fold == f; tr = ~te
        mu, sd = X[tr].mean(0), X[tr].std(0)
        sd[sd == 0] = 1.0
        Xt, Xe = (X[tr] - mu) / sd, (X[te] - mu) / sd
        ym = y[tr].mean()
        A = Xt.T @ Xt + lam * np.eye(X.shape[1])
        w = np.linalg.solve(A, Xt.T @ (y[tr] - ym))
        pred[te] = Xe @ w + ym
    ss_res = float(((y - pred) ** 2).sum()); ss_tot = float(((y - y.mean()) ** 2).sum())
    return 1 - ss_res / ss_tot


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R458 · how much of the RELIABLE per-prompt advantage do target-free features explain?\n")
    print("  ⛔ R457 closed 'a null would show nothing observable predicts it'. A null on THREE")
    print("     covariates says THOSE THREE — `nothing observable` quantifies an unenumerated")
    print("     population. Twenty-sixth step checked, framing corrected. So this round measures")
    print("     HOW MUCH IS EXPLAINABLE, against R457's ceiling, instead of testing three guesses.\n")

    need = {"pool": "genericpool16", "core": "coval_core", "sham": "coval_core_sham"}
    S = {}
    for k, nm in need.items():
        f = SATD / f"sat_{nm}.npz"
        if not f.exists():
            print(f"  UNRUNNABLE: sat_{nm}.npz absent. Exit 2, never 0."); return 2
        S[k] = SC.load_sat(f)
    cf = ROOT / "data" / "comparisons.jsonl"
    if not cf.exists():
        print("  UNRUNNABLE: data/comparisons.jsonl absent. Exit 2."); return 2
    lens = {}
    with cf.open() as fh:
        for line in fh:
            r = json.loads(line)
            txt = [m["content"] for resp in r["responses"]
                   for m in resp["messages"] if m["role"] == "assistant"]
            if txt:
                lens[r["prompt_id"]] = np.array([len(t) for t in txt], float)
    targets, _ = SC.load_targets()
    pids = sorted(set(targets) & set(lens) & set.intersection(*[set(v) for v in S.values()]))
    pids = [p for p in pids if len(lens[p]) >= 4]
    n = len(pids)
    print(f"  prompts with satisfaction AND response texts: {n}")
    if n < 200:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2

    # ---- outcome: R457's arm-specific gap, all annotators ---------------------------------------
    a2c, a2s = np.zeros(n), np.zeros(n)
    FEAT, names = [], None
    for i, p in enumerate(pids):
        HC = np.array([SC.cls(np.array(t[0], float)) for t in targets[p]])
        row, nm = [], []
        mats = {}
        for k in ("core", "sham"):
            d = S[k][p]; cs = sorted({c for (c, _) in d})
            mats[k] = np.array([[d.get((c, l), 0.0) for l in L] for c in cs])
        PMp = np.zeros((16, 4))
        for (ci, ltr), v in S["pool"][p].items():
            PMp[ci, L.index(ltr)] = v
        mats["pool"] = PMp
        a2c[i] = (signs(mats["core"].mean(0))[None, :] == HC).mean()
        a2s[i] = (signs(mats["sham"].mean(0))[None, :] == HC).mean()
        for k in ("core", "sham", "pool"):
            M = mats[k]; r = M.mean(0)
            row += [M.mean(), M.std(), float(r.max() - r.min()), float(r.std()), M.shape[0]]
            nm += [f"{k}_mean", f"{k}_sd", f"{k}_range", f"{k}_respsd", f"{k}_k"]
        Ln = lens[p][:4] if len(lens[p]) >= 4 else np.pad(lens[p], (0, 4 - len(lens[p])))
        row += [float(np.log1p(Ln.mean())), float(np.log1p(Ln.std())),
                float(np.log1p(Ln.max() - Ln.min()))]
        nm += ["len_mean", "len_sd", "len_range"]
        FEAT.append(row)
        if names is None:
            names = nm
    X = np.array(FEAT); y = a2c - a2s
    keep = X.std(0) > 0
    X, names = X[:, keep], [nm for nm, k in zip(names, keep) if k]
    print(f"  features: {X.shape[1]} target-free columns; outcome d = A2(core) - A2(sham), "
          f"mean {y.mean():+.4f}")

    print("\n  CONTROLS")
    rgs = (0, 1, 2)
    base_r2 = [ridge_oof(X, y, 100 + s) for s in rgs]
    Xp = np.column_stack([X, y + np.random.default_rng(3).normal(0, y.std() * 0.3, n)])
    pos_r2 = [ridge_oof(Xp, y, 100 + s) for s in rgs]
    Xn = np.column_stack([X, np.random.default_rng(4).normal(0, 1, n)])
    g0_r2 = [ridge_oof(Xn, y, 100 + s) for s in rgs]
    pos_ok = np.mean(pos_r2) > 0.80 and np.mean(g0_r2) <= np.mean(base_r2) + 0.02
    print(f"    POSITIVE  a planted `d + noise` column -> R2_oof {np.mean(pos_r2):+.4f}"
          f"   {'PASS' if np.mean(pos_r2) > 0.80 else '⛔ FAIL — the pipeline cannot recover signal'}")
    print(f"    g=0       a pure-noise column -> {np.mean(g0_r2):+.4f} vs unplanted "
          f"{np.mean(base_r2):+.4f}   "
          f"{'PASS (does not fire)' if np.mean(g0_r2) <= np.mean(base_r2)+0.02 else '⛔ FAIL'}")
    ysh = np.random.default_rng(9).permutation(y)
    neg = float(np.mean([ridge_oof(X, ysh, 100 + s) for s in rgs]))
    neg_ok = neg <= 0.02
    print(f"    NEGATIVE  outcome shuffled against the features -> {neg:+.4f}   "
          f"{'PASS' if neg_ok else '⛔ FAIL'}")
    print(f"    CEILING   R457's reliability of d = {CEILING:.4f}; a predictor of an observed")
    print(f"              variable cannot exceed R² = its reliability, so R2_oof is read as a SHARE")

    print("\n  ⭐ BOTH-ARMS DIAGNOSTIC — §4: a covariate raising BOTH arms manufactures a differential")
    print(f"    {'feature':<14}{'r(f,core)':>11}{'r(f,sham)':>11}{'r(f,d)':>9}  raises both?")
    both = []
    for j, nm in enumerate(names):
        rc = float(np.corrcoef(X[:, j], a2c)[0, 1]); rs = float(np.corrcoef(X[:, j], a2s)[0, 1])
        rd = float(np.corrcoef(X[:, j], y)[0, 1])
        raises = bool(rc * rs > 0 and min(abs(rc), abs(rs)) > 0.10)
        both.append({"feature": nm, "r_core": rc, "r_sham": rs, "r_d": rd, "raises_both": raises})
        print(f"    {nm:<14}{rc:>+11.4f}{rs:>+11.4f}{rd:>+9.4f}  {'YES ⚠' if raises else 'no'}")

    print("\n  ⭐ EXPLAINABILITY — out-of-fold R², by feature block")
    blocks = {"all": list(range(len(names))),
              "core only": [i for i, nm in enumerate(names) if nm.startswith("core")],
              "sham only": [i for i, nm in enumerate(names) if nm.startswith("sham")],
              "pool only": [i for i, nm in enumerate(names) if nm.startswith("pool")],
              "lengths only": [i for i, nm in enumerate(names) if nm.startswith("len")]}
    res = {}
    print(f"    {'block':<14}{'ncol':>6}{'R2_oof':>10}{'share of ceiling':>19}")
    for bn, idx in blocks.items():
        if not idx:
            continue
        rr = [ridge_oof(X[:, idx], y, 100 + s) for s in rgs]
        m = float(np.mean(rr))
        res[bn] = {"ncol": len(idx), "r2": m, "spread": float(np.std(rr)),
                   "share_of_ceiling": m / CEILING}
        print(f"    {bn:<14}{len(idx):>6}{m:>+10.4f}{m/CEILING:>19.3f}")

    r2 = res["all"]["r2"]
    ctrl_ok = bool(pos_ok and neg_ok)
    if not ctrl_ok:
        world = "UNVERIFIED"
    elif r2 >= 0.30:
        world = "W-EXPLAINED"
    elif r2 <= 0.05:
        world = "W-OPAQUE"
    else:
        world = "W-PARTIAL"
    print(f"\n  WORLD: {world}")
    if world == "W-OPAQUE":
        print(f"    {len(names)} target-free features explain R2_oof = {r2:+.4f} of a quantity that")
        print(f"    replicates at {CEILING:.4f}. ⚠ THE SCOPE IS THESE FEATURES, not 'observables':")
        print(f"    {', '.join(names)}.")
        print(f"    The core's advantage is prompt-specific, REPLICABLE, and unexplained by them.")
    elif world == "W-PARTIAL":
        print(f"    R2_oof {r2:+.4f} is {r2/CEILING:.1%} of the reliable variance. The rest is")
        print(f"    replicable and unexplained by these {len(names)} features.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_prompts": n, "features": names,
           "ceiling_from_r457": CEILING, "blocks": res, "both_arms": both,
           "controls": {"positive_r2": float(np.mean(pos_r2)), "g0_r2": float(np.mean(g0_r2)),
                        "unplanted_r2": float(np.mean(base_r2)), "negative_r2": neg,
                        "positive_ok": bool(pos_ok), "negative_ok": bool(neg_ok)}}
    (RES / "r458_explainability.json").write_text(json.dumps(out, indent=2))
    print(f"  artifact: {RES/'r458_explainability.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
