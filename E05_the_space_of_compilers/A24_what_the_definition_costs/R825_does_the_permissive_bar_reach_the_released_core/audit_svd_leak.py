#!/usr/bin/env python3
"""R825 · THE LEAK CHANNEL THE PREREGISTRATION DID NOT COVER.

E4 audits the VECTORISER: it is fit on fit-half documents only, and the round measures what
that guard is worth by re-running with it fit on all prompts. That audit is real and it is
also INCOMPLETE, because `build()` has a SECOND unsupervised stage:

    v.fit(docs)                                          # fit-half only  -- guarded, audited
    M = v.transform(all documents)
    Z = TruncatedSVD(100).fit_transform(M)                # ALL prompts    -- NOT guarded
    Z = (Z - Z.mean(0)) / Z.std(0)                        # ALL prompts    -- NOT guarded

The SVD basis and the standardisation are both learned from the evaluation half's documents.
No labels are involved, so this is TRANSDUCTIVE leakage rather than label leakage -- but E4's
delta cannot see it, because the SVD is fit on all prompts in BOTH of E4's conditions. A leak
that is present in the control as well as the treatment is invisible to that control.

⛔ WHY THE DIRECTION IS NOT ASSUMED. It is tempting to argue the leak can only inflate the bar,
which would make a WORLD A verdict conservative and this audit unnecessary. That argument is
not forced: an unsupervised basis fit on more documents can also be WORSE for the fit half by
spending components on evaluation-half variance. So the sign is measured here, not derived.

WHAT THIS MEASURES  the same held-out bar at the same cells, under three feature pipelines:
  as_run    vectoriser inside the split, SVD + z-score on all prompts        (what R825 reports)
  strict    vectoriser AND SVD AND z-score all fit inside the split          (no leak channel)
  all_leak  vectoriser also fit on all prompts                               (E4's LEAK arm)
The `as_run - strict` delta is the size of the unaudited channel. If it is at or below the
per-tier noise floor the reported bar stands as measured; if it is not, the bar is an
overestimate by that amount and every verdict that used it inherits the correction.
"""
import itertools
import json
import pathlib
import sys

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls                              # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
PR = list(itertools.combinations(range(4), 2))
NSPLIT = 10
CORE_A2 = 0.566477


def lex(t):
    import re
    w = t.split()
    lw = [len(x) for x in w] or [0]
    return [len(t), len(w), len(set(x.lower() for x in w)),
            (len(set(x.lower() for x in w)) / len(w)) if w else 0.0,
            len(re.findall(r"[.!?]+", t)), t.count("?"), t.count("\n"),
            len(re.findall(r"(?m)^\s*[-*•]", t)), sum(c.isdigit() for c in t), t.count(","),
            float(np.mean(lw)), t.count(":"), sum(c.isupper() for c in t), t.count("(")]


def main():
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
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted(p for p in base if p in tg and p in text and len(tg[p]) >= 2)
    H = {p: np.array([cls(np.array(y, float)) for y, _ in tg[p]]) for p in pids}
    N = len(pids)
    TXT = [[text[p][j] for j in range(4)] for p in pids]
    XL = np.array([[lex(t) for t in row] for row in TXT], float)
    Y = np.array([np.sign(H[p].sum(axis=0)) for p in pids])
    splits = [np.random.default_rng(3000 + s).permutation(N) for s in range(NSPLIT)]
    print(f"  POPULATION  {N} prompts x 4 = {N*4} documents · {NSPLIT} splits (R825's splits)")

    def a2_h(S, sub):
        return float(np.mean([float((H[pids[i]] == np.sign(S[i][[u for u, _ in PR]]
                     - S[i][[w for _, w in PR]])).mean()) for i in sub]))

    def zblock(Z, fit_rows, mode):
        """fit_rows indexes DOCUMENTS (prompt*4+j) belonging to the fit half."""
        if mode == "strict":
            m, s = Z[fit_rows].mean(0), Z[fit_rows].std(0) + 1e-12
        else:
            m, s = Z.mean(0), Z.std(0) + 1e-12
        return (Z - m) / s

    def build(tier, fit, mode):
        """mode: as_run | strict | all_leak."""
        docrows = np.array([i * 4 + j for i in fit for j in range(4)])
        if mode == "strict":
            mu, sd = XL.reshape(-1, 14)[docrows].mean(0), XL.reshape(-1, 14)[docrows].std(0) + 1e-12
        else:
            mu, sd = XL.reshape(-1, 14).mean(0), XL.reshape(-1, 14).std(0) + 1e-12
        blocks = [(XL - mu) / sd]
        if tier == "T1_lexical14":
            return blocks[0]
        vsrc = range(N) if mode == "all_leak" else fit
        docs = [TXT[i][j] for i in vsrc for j in range(4)]
        alld = [TXT[i][j] for i in range(N) for j in range(4)]
        specs = []
        if tier in ("T2_+char_ngram", "T4_all"):
            specs.append(dict(analyzer="char_wb", ngram_range=(3, 5), min_df=5,
                              max_features=8000, k=100))
        if tier in ("T3_+word_ngram", "T4_all"):
            specs.append(dict(analyzer="word", ngram_range=(1, 2), min_df=5,
                              max_features=20000, k=200))
        for sp in specs:
            k = sp.pop("k")
            v = TfidfVectorizer(**sp)
            v.fit(docs)
            M = v.transform(alld)
            svd = TruncatedSVD(n_components=k, random_state=0)
            if mode == "strict":
                svd.fit(M[docrows])          # ⭐ the basis never sees the evaluation half
                Z = svd.transform(M)
            else:
                Z = svd.fit_transform(M)     # what R825 does
            blocks.append(zblock(Z, docrows, mode).reshape(N, 4, -1))
        return np.concatenate(blocks, axis=2)

    def bar_of(tier, mode):
        vals = []
        for s, pm in enumerate(splits):
            fit, ev = pm[: N // 2], pm[N // 2:]
            Xs = build(tier, fit, mode)
            d, y = [], []
            for i in fit:
                for k, (u, w) in enumerate(PR):
                    if Y[i][k] == 0:
                        continue
                    d.append(Xs[i][u] - Xs[i][w])
                    y.append(Y[i][k])
            m = LogisticRegression(C=1.0, max_iter=1500, random_state=s).fit(np.array(d),
                                                                            np.array(y))
            vals.append(a2_h(Xs @ np.asarray(m.coef_).ravel(), ev))
        return float(np.mean(vals)), float(np.std(vals))

    TIERS = ["T1_lexical14", "T2_+char_ngram", "T3_+word_ngram", "T4_all"]
    out = {}
    print("\n  THE UNAUDITED CHANNEL, PER TIER (logistic_C1.0, held out, 10 splits)")
    print(f"     {'tier':<16} {'as_run':>10} {'strict':>10} {'as_run-strict':>15} "
          f"{'floor':>8}  {'all_leak':>10}")
    for t in TIERS:
        a, asd = bar_of(t, "as_run")
        st, ssd = bar_of(t, "strict")
        lk, _ = bar_of(t, "all_leak")
        floor = float(np.hypot(asd, ssd) / np.sqrt(NSPLIT))
        out[t] = {"as_run": a, "as_run_sd": asd, "strict": st, "strict_sd": ssd,
                  "delta": a - st, "paired_se": floor, "all_leak": lk}
        flag = "INSIDE the floor" if abs(a - st) <= 1.96 * floor else "⛔ OUTSIDE — the bar is inflated"
        print(f"     {t:<16} {a:>10.6f} {st:>10.6f} {a - st:>+15.6f} {1.96*floor:>8.4f}  "
              f"{lk:>10.6f}   {flag}")

    worst = max(TIERS, key=lambda t: out[t]["delta"])
    print(f"\n  ⭐ largest unaudited inflation: {worst} {out[worst]['delta']:+.6f}")
    print(f"  ⭐ strictest bar at any tier: {max(out[t]['strict'] for t in TIERS):.6f} "
          f"vs `coval_core` {CORE_A2}  -> gap "
          f"{CORE_A2 - max(out[t]['strict'] for t in TIERS):+.6f}")
    ap = HERE / "results" / "svd_leak_audit.json"
    ap.parent.mkdir(exist_ok=True)
    ap.write_text(json.dumps(out, indent=1, sort_keys=True))
    print(f"  ARTIFACT {ap.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
