#!/usr/bin/env python3
"""R827 · is the core-on-ceiling coincidence structural, or is it item difficulty?

A raw per-prompt correlation between any two arms is FORCED by shared item difficulty (measured:
random_k4_s0 x oracle_k4 = +0.5132 with no shared mechanism). See PREREGISTRATION.txt for the
partial-correlation estimand, D1-D4, the four worlds (D registered in advance) and the gated kill.
"""
import hashlib, itertools, json, pathlib, re, sys
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

sys.stdout.reconfigure(line_buffering=True)
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                          # noqa: E402

RES = ROOT / "corebench/results"; HERE = pathlib.Path(__file__).resolve().parent
PR = list(itertools.combinations(range(4), 2)); NSPLIT = 8; KDIM = 100; NBOOT = 2000
RAW_KNOWN = {("random_k4_s0", "oracle_k4"): 0.5132, ("gen_sham", "oracle_k4"): 0.3873}


def _plain(o):
    for t, f in ((np.bool_, bool), (np.integer, int), (np.floating, float)):
        if isinstance(o, t): return f(o)
    raise TypeError(type(o))


def lex(t):
    w = t.split(); lw = [len(x) for x in w] or [0]
    return [len(t), len(w), len(set(x.lower() for x in w)),
            (len(set(x.lower() for x in w)) / len(w)) if w else 0.0,
            len(re.findall(r"[.!?]+", t)), t.count("?"), t.count("\n"),
            len(re.findall(r"(?m)^\s*[-*•]", t)), sum(c.isdigit() for c in t), t.count(","),
            float(np.mean(lw)), t.count(":"), sum(c.isupper() for c in t), t.count("(")]


def resid(y, X):
    """residual of y on [1, X]; X may be (n,) or (n,d)."""
    X = np.atleast_2d(X.T).T if X.ndim == 1 else X
    A = np.column_stack([np.ones(len(y)), X])
    return y - A @ np.linalg.lstsq(A, y, rcond=None)[0]


def partial_r(a, b, Z):
    ra, rb = resid(a, Z), resid(b, Z)
    if ra.std() < 1e-12 or rb.std() < 1e-12: return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    out = {"instrument_unit": "a PROMPT", "claim_unit": "PROFILE AGREEMENT, never mechanism"}
    tg, _ = load_targets(); text = {}
    for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
        if not line.strip(): continue
        r = json.loads(line); rs = r.get("responses") or []
        if len(rs) == 4:
            text[r["prompt_id"]] = [" ".join(str(m.get("content", "")) for m in
                                    (it.get("messages") or []) if isinstance(m, dict)) for it in rs]
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted(p for p in base if p in tg and p in text and len(tg[p]) >= 2)
    H = {p: np.array([cls(np.array(y, float)) for y, _ in tg[p]]) for p in pids}
    N = len(pids)
    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if not p.stem.startswith("sat08") and "_08b" not in p.stem)
    V = {}
    for a in arms:
        try: s = load_sat(RES / f"sat_{a}.npz")
        except Exception: continue
        if not all(p in s for p in pids): continue
        V[a] = np.array([float((H[p] == np.array(cls(yvec(s[p],
                         sorted({i for i, _ in s[p]}))))).mean()) for p in pids])
    print(f"  POPULATION {N} prompts · {len(V)} arms")

    # ---- OBJECT: the round's premise must reproduce ------------------------------------------
    print("\n  OBJECT CHECK - the raw correlations this round is premised on")
    ok = True
    for (a, b), want in RAW_KNOWN.items():
        got = float(np.corrcoef(V[a], V[b])[0, 1])
        good = abs(got - want) < 5e-4; ok = ok and good
        print(f"     {a} x {b}: {got:+.4f} vs {want}   {'PASS' if good else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: the premise did not reproduce. Exit 2, never 0."); return 2

    # ---- the saturated response-only bar, OUT OF FOLD (D4) -------------------------------------
    print("\n  building the saturated response-only bar, OUT OF FOLD")
    print("     ⚠ D4: a split-AVERAGED vector is less attenuated than a single arm's. Each prompt")
    print("       is scored only by models that did NOT see it, and the count is reported.")
    TXT = [[text[p][j] for j in range(4)] for p in pids]
    XL = np.array([[lex(t) for t in row] for row in TXT], float)
    Y = np.array([np.sign(H[p].sum(axis=0)) for p in pids])
    # ⛔ THE FIRST VERSION REUSED R826's RANDOM 50/50 SPLITS and the assert below caught it:
    #    a prompt lands in the FIT half all 8 times with probability (1/2)^8, so ~3.8 of 968 were
    #    never scored out of fold. Random halves do not guarantee coverage; K-FOLD does.
    # ⚠ SCOPE CHANGE, STATED: 8-fold cross-fitting trains on 7/8 = 847 prompts, not 484, so this
    #    bar is NOT the same estimator as R826's half-split bar and its LEVEL is not comparable.
    #    Only its per-prompt PROFILE is used here, which is what the correlation needs.
    acc = np.zeros(N); cnt = np.zeros(N)
    order = np.random.default_rng(3000).permutation(N)
    folds = np.array_split(order, NSPLIT)
    for s_, ev in enumerate(folds):
        fit = np.setdiff1d(order, ev)
        rows = np.array([i * 4 + j for i in fit for j in range(4)])
        mu, sd = XL.reshape(-1, 14)[rows].mean(0), XL.reshape(-1, 14)[rows].std(0) + 1e-12
        XLz = (XL - mu) / sd
        docs = [TXT[i][j] for i in fit for j in range(4)]
        alld = [TXT[i][j] for i in range(N) for j in range(4)]
        v = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=5, max_features=8000)
        v.fit(docs); Mf = v.transform(docs)
        svd = TruncatedSVD(n_components=KDIM, random_state=0).fit(Mf)
        Zf = svd.transform(Mf); zm, zs = Zf.mean(0), Zf.std(0) + 1e-12
        Z = ((svd.transform(v.transform(alld)) - zm) / zs).reshape(N, 4, -1)
        Xs = np.concatenate([XLz, Z], axis=2)
        d, y = [], []
        for i in fit:
            for k, (u, w) in enumerate(PR):
                if Y[i][k] == 0: continue
                d.append(Xs[i][u] - Xs[i][w]); y.append(Y[i][k])
        m = LogisticRegression(C=1.0, max_iter=1500).fit(np.array(d), np.array(y))
        S = Xs @ np.asarray(m.coef_).ravel()
        for i in ev:
            acc[i] += float((H[pids[i]] == np.sign(S[i][[u for u, _ in PR]]
                             - S[i][[w for _, w in PR]])).mean()); cnt[i] += 1
        print(f"     fold {s_}: fit {len(fit)} · scored {len(ev)}")
    assert cnt.min() > 0, "a prompt was never in an eval fold"
    assert cnt.max() == 1, f"k-fold must score each prompt ONCE, got max {cnt.max()}"
    BAR = acc / cnt
    print(f"     out-of-fold bar {BAR.mean():.6f} · each prompt scored by "
          f"exactly {cnt.min():.0f} model each (8-fold cross-fitting, fit on 7/8)")
    out["bar_oof_mean"] = float(BAR.mean())

    CORE = V["coval_core"]
    raw = float(np.corrcoef(CORE, BAR)[0, 1])
    print(f"     ⛔ RAW r(core, bar) = {raw:+.4f}  -- a DERIVATION-grade number: forced by difficulty")

    # ---- the difficulty index, from arms EXCLUDING both ----------------------------------------
    def diffic(exclude):
        keep = [a for a in V if a not in exclude]
        M = np.array([V[a] for a in keep])
        tie = np.array([float((H[p] == 0).mean()) for p in pids])
        nann = np.array([float(len(H[p])) for p in pids])
        return np.column_stack([M.mean(0), tie, np.log(nann)]), len(keep)

    Zc, nkeep = diffic({"coval_core"})
    pr = partial_r(CORE, BAR, Zc)
    print(f"\n  E1 - PARTIAL r, difficulty index from {nkeep} arms EXCLUDING `coval_core`")
    print(f"     ⭐ partial r(core, bar | difficulty) = {pr:+.4f}   (raw was {raw:+.4f})")
    rng = np.random.default_rng(20250806)
    idx = rng.integers(0, N, size=(NBOOT, N))
    bs = np.array([partial_r(CORE[i], BAR[i], Zc[i]) for i in idx[:400]])
    lo, hi = np.nanpercentile(bs, 2.5), np.nanpercentile(bs, 97.5)
    print(f"     bootstrap 95% [{lo:+.4f}, {hi:+.4f}]  (400 draws over prompts)")
    out["e1"] = {"raw": raw, "partial": pr, "lo": float(lo), "hi": float(hi), "n_index_arms": nkeep}

    # ---- E2 · the null: accuracy-matched, mechanism-unrelated pairs -----------------------------
    print("\n  E2 - THE NULL: all arm pairs, each with the index rebuilt EXCLUDING that pair")
    names = sorted(V)
    nullr, pairs = [], []
    for a, b in itertools.combinations(names, 2):
        if "coval_core" in (a, b): continue
        Z, _ = diffic({a, b})
        r = partial_r(V[a], V[b], Z)
        if not np.isnan(r): nullr.append(r); pairs.append((a, b))
    nullr = np.array(nullr)
    p95, p50, p05 = np.percentile(nullr, [95, 50, 5])
    print(f"     {len(nullr)} pairs · median {p50:+.4f} · 5th {p05:+.4f} · 95th {p95:+.4f}")
    print(f"     ⭐ partial r(core, bar) {pr:+.4f} sits at percentile "
          f"{float((nullr < pr).mean() * 100):.1f} of this null")
    out["e2"] = {"n_pairs": len(nullr), "p05": float(p05), "p50": float(p50), "p95": float(p95),
                 "pctile_of_core_bar": float((nullr < pr).mean() * 100)}

    # ---- CONTROLS ------------------------------------------------------------------------------
    print("\n  CONTROLS")
    pos = {}
    for a, b in (("topw_k4", "topw_k6"), ("random_k4_s0", "random_k4_s1")):
        if a in V and b in V:
            Z, _ = diffic({a, b})
            pos[f"{a}|{b}"] = partial_r(V[a], V[b], Z)
    pos_ok = bool(pos) and all(v > p95 for v in pos.values())
    for k, v in pos.items():
        print(f"     POSITIVE  {k}: partial r {v:+.4f}   above null p95 {p95:+.4f}: {v > p95}")
    print(f"               shared-mechanism pairs exceed the null: {pos_ok}")
    rp = rng.permutation(N)
    plac = partial_r(CORE, BAR[rp], Zc)
    plac_ok = abs(plac) < 0.10
    print(f"     PLACEBO   core vs a PERMUTATION of the bar: {plac:+.4f}   near zero: {plac_ok}")
    Zr = rng.normal(size=Zc.shape)
    shamr = partial_r(CORE, BAR, Zr)
    sham_ok = abs(shamr - raw) < 0.02
    print(f"     SHAM      residualise on RANDOM vectors: {shamr:+.4f} vs raw {raw:+.4f}   "
          f"removes nothing: {sham_ok}")
    half = rng.permutation([a for a in V if a != "coval_core"])[: max(4, len(V) // 3)]
    Z2, _ = diffic(set(V) - set(half) | {"coval_core"})
    neg = partial_r(CORE, BAR, Z2)
    neg_ok = abs(neg - pr) < (hi - lo)
    print(f"     NEGATIVE  index from a DIFFERENT disjoint subset ({len(half)} arms): {neg:+.4f} "
          f"vs {pr:+.4f}   within the bootstrap width: {neg_ok}")
    gate = bool(pos_ok and plac_ok and sham_ok and neg_ok)
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"positive": pos, "positive_ok": pos_ok, "placebo": plac,
                       "placebo_ok": plac_ok, "sham": shamr, "sham_ok": sham_ok,
                       "negative": neg, "negative_ok": neg_ok, "gate": gate}

    # ---- THE KILL ------------------------------------------------------------------------------
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate: world = "UNVERIFIED"
    elif pr > p95: world = "A"
    elif pr < p05: world = "D"          # registered in advance this time
    elif p05 <= pr <= p95: world = "B"
    else: world = "C"
    print(f"     gate {gate} · partial r {pr:+.4f} · null [{p05:+.4f}, {p95:+.4f}]")
    print(f"     ->  WORLD {world}")
    out["world"] = world
    (HERE / "results").mkdir(exist_ok=True)
    ap = HERE / "results" / "structural_or_difficulty.json"
    ap.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    print(f"\n  ARTIFACT {ap.relative_to(ROOT)}  md5 {hashlib.md5(ap.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
