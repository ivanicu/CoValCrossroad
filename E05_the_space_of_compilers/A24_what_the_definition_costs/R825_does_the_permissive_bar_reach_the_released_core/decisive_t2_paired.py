#!/usr/bin/env python3
"""R825 · the decisive comparison, PAIRED, with a CI instead of two point estimates.

The independent SVD audit reports strict T2 = 0.572335 and `coval_core` = 0.566477, a difference of
+0.005858 against a floor of 0.0066 -- i.e. NOT resolvable. But that compares two means computed on
DIFFERENT footings: the bar is a mean over eval halves, the core is a corpus constant.

⛔ THE RIGHT STATISTIC IS PAIRED. On each split, score BOTH on the SAME evaluation half and take the
   difference. The split-to-split variation that dominates the unpaired comparison is common to both
   arms and cancels. This is the cell the whole verdict hinges on and nobody has computed its CI.

Every unsupervised stage (vectoriser, SVD, z-score) is fit on the fit half only.
"""
import itertools, json, pathlib, re, sys
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

sys.stdout.reconfigure(line_buffering=True)
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                       # noqa: E402

RES = ROOT / "corebench/results"; HERE = pathlib.Path(__file__).resolve().parent
PR = list(itertools.combinations(range(4), 2)); NSPLIT = 12


def lex(t):
    w = t.split(); lw = [len(x) for x in w] or [0]
    return [len(t), len(w), len(set(x.lower() for x in w)),
            (len(set(x.lower() for x in w)) / len(w)) if w else 0.0,
            len(re.findall(r"[.!?]+", t)), t.count("?"), t.count("\n"),
            len(re.findall(r"(?m)^\s*[-*•]", t)), sum(c.isdigit() for c in t), t.count(","),
            float(np.mean(lw)), t.count(":"), sum(c.isupper() for c in t), t.count("(")]


def main():
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
    N = len(pids); TXT = [[text[p][j] for j in range(4)] for p in pids]
    XL = np.array([[lex(t) for t in row] for row in TXT], float)
    Y = np.array([np.sign(H[p].sum(axis=0)) for p in pids])
    sat = load_sat(RES / "sat_coval_core.npz")
    CORE = np.array([float((H[p] == np.array(cls(yvec(sat[p],
                     sorted({i for i, _ in sat[p]}))))).mean()) for p in pids])
    print(f"  POPULATION {N} prompts · `coval_core` corpus A2 {CORE.mean():.6f} · {NSPLIT} splits")

    def a2(S, sub):
        return np.array([float((H[pids[i]] == np.sign(S[i][[u for u, _ in PR]]
                        - S[i][[w for _, w in PR]])).mean()) for i in sub])

    diffs, bars, cores = [], [], []
    for s in range(NSPLIT):
        pm = np.random.default_rng(3000 + s).permutation(N)
        fit, ev = pm[: N // 2], pm[N // 2:]
        rows = np.array([i * 4 + j for i in fit for j in range(4)])
        mu, sd = XL.reshape(-1, 14)[rows].mean(0), XL.reshape(-1, 14)[rows].std(0) + 1e-12
        blocks = [(XL - mu) / sd]
        docs = [TXT[i][j] for i in fit for j in range(4)]
        alld = [TXT[i][j] for i in range(N) for j in range(4)]
        v = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=5, max_features=8000)
        v.fit(docs); Mfit = v.transform(docs)
        svd = TruncatedSVD(n_components=100, random_state=0).fit(Mfit)        # FIT HALF ONLY
        Zf = svd.transform(Mfit); zm, zs = Zf.mean(0), Zf.std(0) + 1e-12      # FIT HALF ONLY
        blocks.append(((svd.transform(v.transform(alld)) - zm) / zs).reshape(N, 4, -1))
        Xs = np.concatenate(blocks, axis=2)
        d, y = [], []
        for i in fit:
            for k, (u, w) in enumerate(PR):
                if Y[i][k] == 0: continue
                d.append(Xs[i][u] - Xs[i][w]); y.append(Y[i][k])
        m = LogisticRegression(C=1.0, max_iter=1500, random_state=s).fit(np.array(d), np.array(y))
        bar_v = a2(Xs @ np.asarray(m.coef_).ravel(), ev)
        core_v = CORE[ev]
        diffs.append(float((bar_v - core_v).mean())); bars.append(float(bar_v.mean()))
        cores.append(float(core_v.mean()))
        print(f"     split {s:2d}  bar {bars[-1]:.6f}   core {cores[-1]:.6f}   "
              f"paired diff {diffs[-1]:+.6f}")
    dd = np.array(diffs)
    se = dd.std(ddof=1) / np.sqrt(len(dd))
    lo, hi = dd.mean() - 1.96 * se, dd.mean() + 1.96 * se
    # the comparison word is COMPUTED, never typed
    verdict = ("RESOLVABLY ABOVE the core" if lo > 0 else
               "RESOLVABLY BELOW the core" if hi < 0 else
               "INDISTINGUISHABLE from the core")
    print(f"\n  ⭐ PAIRED bar - core over {len(dd)} splits: {dd.mean():+.6f} "
          f"[{lo:+.6f}, {hi:+.6f}]  (se {se:.6f})")
    print(f"     unpaired would be {np.mean(bars) - np.mean(cores):+.6f}; pairing removes the "
          f"split-to-split variance common to both arms")
    print(f"     splits where the bar beats the core: {int((dd > 0).sum())} of {len(dd)}")
    print(f"  ⭐ VERDICT (computed): the leak-free char-n-gram response-only bar is {verdict}")
    ap = HERE / "results" / "decisive_t2_paired.json"
    ap.write_text(json.dumps({"diffs": diffs, "bars": bars, "cores": cores,
                              "mean": float(dd.mean()), "lo": float(lo), "hi": float(hi),
                              "se": float(se), "n_splits": len(dd),
                              "wins": int((dd > 0).sum()), "verdict": verdict}, indent=1))
    print(f"  ARTIFACT {ap.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
