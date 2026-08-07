#!/usr/bin/env python3
"""R825 · the FOURTH unguarded stage, decomposed instead of bundled.

The SVD-leak audit's `strict` mode also standardises the 14 lexical features on the fit half,
which R825's `build()` does not — XLz is computed once from ALL prompts. That is a fourth
transductive channel, and `as_run - strict` BUNDLES it with the SVD channel.

⛔ DERIVED FIRST, and it kills half the channel for free: the model consumes PAIRWISE DIFFERENCES,
   and ((x_u - mu) - (x_w - mu))/sd = (x_u - x_w)/sd. THE MEAN CANCELS EXACTLY (verified below at
   machine precision). Only the per-feature sd survives, and it enters ONLY by rescaling each
   coefficient, i.e. through the L2 penalty geometry at finite C. At C -> inf it must vanish
   entirely, which is a prediction this script tests rather than asserts.

Runs on T1 only -- no TF-IDF -- so it is seconds, not a third 30-minute restart.
"""
import itertools
import json
import pathlib
import re
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression

sys.stdout.reconfigure(line_buffering=True)
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls                              # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
PR = list(itertools.combinations(range(4), 2))
NSPLIT = 8


def lex(t):
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
        if len(rs) == 4:
            text[r["prompt_id"]] = [" ".join(str(m.get("content", "")) for m in
                                    (it.get("messages") or []) if isinstance(m, dict))
                                    for it in rs]
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted(p for p in base if p in tg and p in text and len(tg[p]) >= 2)
    H = {p: np.array([cls(np.array(y, float)) for y, _ in tg[p]]) for p in pids}
    N = len(pids)
    XL = np.array([[lex(t) for t in [text[p][j] for j in range(4)]] for p in pids], float)
    Y = np.array([np.sign(H[p].sum(axis=0)) for p in pids])
    splits = [np.random.default_rng(3000 + s).permutation(N) for s in range(NSPLIT)]
    print(f"  POPULATION  {N} prompts · T1 only · {NSPLIT} splits (R825's split seeds)")

    # ---- the DERIVATION, checked on the real data, not on a synthetic ------------------------
    mu_a = XL.reshape(-1, 14).mean(0)
    sd_a = XL.reshape(-1, 14).std(0) + 1e-12
    half = splits[0][: N // 2]
    rows = np.array([i * 4 + j for i in half for j in range(4)])
    mu_h = XL.reshape(-1, 14)[rows].mean(0)
    sd_h = XL.reshape(-1, 14)[rows].std(0) + 1e-12
    d_all = ((XL - mu_a) / sd_a)[:, 0] - ((XL - mu_a) / sd_a)[:, 1]
    d_hm = ((XL - mu_h) / sd_a)[:, 0] - ((XL - mu_h) / sd_a)[:, 1]
    print(f"  ⛔ DERIVATION on the real features: swapping the MEAN changes the pairwise "
          f"difference by max {np.abs(d_all - d_hm).max():.3e}  -> IT CANCELS")
    print(f"     the per-feature sd moves half-vs-all by up to "
          f"{np.abs(sd_h / sd_a - 1).max() * 100:.2f}%  -> only THIS can leak")

    def a2_h(S, sub):
        return float(np.mean([float((H[pids[i]] == np.sign(S[i][[u for u, _ in PR]]
                     - S[i][[w for _, w in PR]])).mean()) for i in sub]))

    def bar(mode, C):
        vals = []
        for s, pm in enumerate(splits):
            fit, ev = pm[: N // 2], pm[N // 2:]
            r = np.array([i * 4 + j for i in fit for j in range(4)])
            sd = (XL.reshape(-1, 14)[r].std(0) + 1e-12) if mode == "strict" else sd_a
            Xs = (XL - mu_a) / sd
            d, y = [], []
            for i in fit:
                for k, (u, w) in enumerate(PR):
                    if Y[i][k] == 0:
                        continue
                    d.append(Xs[i][u] - Xs[i][w])
                    y.append(Y[i][k])
            m = LogisticRegression(C=C, max_iter=3000, random_state=s).fit(np.array(d),
                                                                          np.array(y))
            vals.append(a2_h(Xs @ np.asarray(m.coef_).ravel(), ev))
        return float(np.mean(vals)), float(np.std(vals))

    print("\n  THE CHANNEL, AND THE PREDICTION THAT IT VANISHES AS C GROWS")
    out = {}
    for C in (0.01, 0.1, 1.0, 100.0, 10000.0):
        a, sa = bar("as_run", C)
        st, ss = bar("strict", C)
        out[str(C)] = {"as_run": a, "strict": st, "delta": a - st, "sd_as_run": sa,
                       "sd_strict": ss}
        print(f"     C={C:<8} as_run {a:.6f} ± {sa:.4f}   strict {st:.6f} ± {ss:.4f}   "
              f"channel {a - st:+.6f}")
    ds = [abs(out[str(C)]["delta"]) for C in (0.01, 0.1, 1.0, 100.0, 10000.0)]
    print(f"     ⭐ |channel| at C=0.01 {ds[0]:.6f} -> at C=1e4 {ds[-1]:.6f}   "
          f"shrinks as the penalty weakens: {ds[-1] <= ds[0]}")
    print(f"     ⭐ at R825's operating point C=1.0 the lexical-sd channel is "
          f"{out['1.0']['delta']:+.6f}, against a per-split sd of {out['1.0']['sd_as_run']:.4f}")
    (HERE / "results").mkdir(exist_ok=True)
    ap = HERE / "results" / "lexical_sd_channel.json"
    ap.write_text(json.dumps({"grid": out, "mean_cancels_max_abs": float(np.abs(d_all - d_hm).max()),
                              "sd_shift_pct": float(np.abs(sd_h / sd_a - 1).max() * 100)},
                             indent=1, sort_keys=True))
    print(f"\n  ARTIFACT {ap.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
