#!/usr/bin/env python3
"""R825 · does ④'s permissive bar reach the released core?

R824 adopted the permissive reading; its bar is 0.519689 and `coval_core` is 0.566477 — a gap of
0.046789. If a richer response-only predictor closes it, ④ excludes the released core and the
definition admits nothing that matters. See PREREGISTRATION.txt for tiers, D1-D4, worlds, kill.
"""
import hashlib
import itertools
import json
import pathlib
import re
import sys

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, RidgeClassifier

# ⛔ PYTHON BLOCK-BUFFERS stdout on ANY non-tty — a pipe AND a file redirect both. R825's first
#    attempt was killed at ~15 min and captured ZERO BYTES, so there was no diagnostic at all. Every
#    round in this arc has printed into a buffer that only flushes on exit; they were readable purely
#    because they finished. A long run must be line-buffered or it is unobservable while it matters.
sys.stdout.reconfigure(line_buffering=True)

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                    # noqa: E402
from assurance.null_is_informative import assert_null_is_informative   # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
PR = list(itertools.combinations(range(4), 2))
NSPLIT = 8
NBOOT = 1200
R824_BAR = 0.519689
CORE_A2 = 0.566477
CEIL_HO = 0.633370          # R804, the GENERALISING ceiling — a derived upper bound on any bar
TIERS = ["T1_lexical14", "T2_+char_ngram", "T3_+word_ngram", "T4_all"]


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    raise TypeError(type(o))


def lex(t):
    w = t.split()
    lw = [len(x) for x in w] or [0]
    return [len(t), len(w), len(set(x.lower() for x in w)),
            (len(set(x.lower() for x in w)) / len(w)) if w else 0.0,
            len(re.findall(r"[.!?]+", t)), t.count("?"), t.count("\n"),
            len(re.findall(r"(?m)^\s*[-*•]", t)), sum(c.isdigit() for c in t), t.count(","),
            float(np.mean(lw)), t.count(":"), sum(c.isupper() for c in t), t.count("(")]


def models(seed):
    return [(f"logistic_C{c}", LogisticRegression(C=c, max_iter=1500, random_state=seed))
            for c in (0.01, 0.1, 1.0, 10.0)] + [
        ("ridge", RidgeClassifier(random_state=seed)),
        ("gboost_d3", GradientBoostingClassifier(n_estimators=80, max_depth=3, random_state=seed))]


def bh(pv, q=0.05):
    p = np.asarray(pv, float)
    o = np.argsort(p)
    m = len(p)
    keep = np.zeros(m, bool)
    for r, i in enumerate(o, 1):
        if p[i] <= q * r / m:
            keep[o[:r]] = True
    return keep


def main():
    out = {"instrument_unit": "a RULE CLASS", "claim_unit": "a CLAUSE"}
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
    mu, sd = XL.reshape(-1, 14).mean(0), XL.reshape(-1, 14).std(0) + 1e-12
    XLz = (XL - mu) / sd
    Y = np.array([np.sign(H[p].sum(axis=0)) for p in pids])
    print(f"  POPULATION  {N} prompts x 4 responses = {N*4} documents · {NSPLIT} splits")
    print(f"  TARGETS     R824's bar {R824_BAR} · `coval_core` {CORE_A2} · gap "
          f"{CORE_A2 - R824_BAR:.6f} · DERIVED ceiling CEIL_HO {CEIL_HO}")

    def a2_key(S, sub, K):
        v = []
        for i in sub:
            s_ = np.sign(S[i][[u for u, _ in PR]] - S[i][[w for _, w in PR]])
            m = K[i] != 0
            if m.any():
                v.append(float((K[i][m] == s_[m]).mean()))
        return float(np.mean(v)) if v else float("nan")

    def a2_h(S, sub):
        return a2_key(S, sub, np.array([np.ones(6) for _ in range(N)])) if False else float(
            np.mean([float((H[pids[i]] == np.sign(S[i][[u for u, _ in PR]]
                     - S[i][[w for _, w in PR]])).mean()) for i in sub]))

    def build(tier, fit_docs_idx, leak):
        """-> Xz (N,4,d); EVERY unsupervised stage fit on fit-half documents only unless leak=True.

        THE FIRST VERSION GUARDED ONE OF THREE UNSUPERVISED STAGES. The vectoriser was fit on the
        fit half, but TruncatedSVD(...).fit_transform(M) and the z-score after it were fit on ALL
        prompts, so the SVD basis and the standardisation both saw the evaluation half. That is
        TRANSDUCTIVE leakage -- no labels involved -- and E4 CANNOT SEE IT, because the SVD leaks in
        both of E4's conditions, and a leak present in the control as well as the treatment is
        invisible to that control. D3 named the vocabulary and stopped there.
        The direction is NOT derived: a basis fit on more documents can also be WORSE for the fit
        half by spending components on evaluation-half variance. The sign is measured, not argued.
        Found by an independent session auditing this directory; verified here against this source
        before being accepted.
        """
        if tier == "T1_lexical14":
            return XLz
        blocks = [XLz]
        src = list(range(N)) if leak else list(fit_docs_idx)
        docs = [TXT[i][j] for i in src for j in range(4)]
        allrows = [TXT[i][j] for i in range(N) for j in range(4)]

        def embed(vec, ncomp):
            vec.fit(docs)
            Mfit = vec.transform(docs)
            svd = TruncatedSVD(n_components=ncomp, random_state=0).fit(Mfit)   # FIT HALF ONLY
            Zf = svd.transform(Mfit)
            mu_, sd_ = Zf.mean(0), Zf.std(0) + 1e-12                           # FIT HALF ONLY
            Z = (svd.transform(vec.transform(allrows)) - mu_) / sd_
            return Z.reshape(N, 4, -1)

        if "char" in tier or tier == "T4_all":
            blocks.append(embed(TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=10,
                                                max_features=4000), 60))
        if "word" in tier or tier == "T4_all":
            blocks.append(embed(TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=10,
                                                max_features=10000), 120))
        return np.concatenate(blocks, axis=2)

    def pairdata(sub, Xs, Ys):
        d, y = [], []
        for i in sub:
            for k, (u, w) in enumerate(PR):
                if Ys[i][k] == 0:
                    continue
                d.append(Xs[i][u] - Xs[i][w])
                y.append(Ys[i][k])
        return np.array(d), np.array(y)

    def fit_eval(mdl, fit, ev, Xs, Ys, key=None):
        d, y = pairdata(fit, Xs, Ys)
        if len(set(y.tolist())) < 2:
            return None
        mdl.fit(d, y)
        w = np.asarray(mdl.coef_).ravel() if hasattr(mdl, "coef_") else None
        if w is not None:
            S = Xs @ w
        else:
            S = np.array([[float(mdl.decision_function((Xs[i][j] - Xs[i].mean(axis=0))
                          .reshape(1, -1))[0]) for j in range(4)] for i in range(N)])
        return a2_h(S, ev) if key is None else a2_key(S, ev, key)

    splits = [np.random.default_rng(3000 + s).permutation(N) for s in range(NSPLIT)]
    rng = np.random.default_rng(20250806)

    # ================= E1/E4 · the tier x capacity x leak grid ===================================
    print("\n  E1/E4 - THE TIER x CAPACITY GRID, HELD OUT, VECTORISER FIT INSIDE THE SPLIT")
    print("     ⛔ D1 (DERIVATION): in-sample capacity monotonicity is FORCED. All figures held out.")
    grid, dims = {}, {}
    # ⚠ BUDGET REDUCTION, RECORDED NOT SILENT: the preregistration allowed one run under 25 min and
    #   the full 2x4x10x6 grid overran it and was killed. The leak audit now runs at the RICHEST
    #   TIER ONLY -- the tier where a leaked vocabulary can actually help -- and splits are 8 not 10.
    #   §2: an unavailability claim in the flattering direction is still an unavailability claim.
    for leak in (False, True):
        for tier in (TIERS if not leak else [TIERS[-1]]):
            per_model = {m: [] for m, _ in models(0)}
            for s, pm in enumerate(splits):
                fit, ev = pm[: N // 2], pm[N // 2:]
                Xs = build(tier, fit, leak)
                dims[tier] = int(Xs.shape[2])
                for mname, _ in models(s):
                    v = fit_eval(dict(models(s))[mname], fit, ev, Xs, Y)
                    if v is not None:
                        per_model[mname].append(v)
            for mname, vals in per_model.items():
                if vals:
                    grid[f"{'LEAK' if leak else 'clean'}|{tier}|{mname}"] = {
                        "mean": float(np.mean(vals)), "sd": float(np.std(vals)), "n": len(vals)}
    clean = {k: v for k, v in grid.items() if k.startswith("clean|")}
    for t in TIERS:
        cells = {k: v for k, v in clean.items() if f"|{t}|" in k}
        b = max(cells, key=lambda k: cells[k]["mean"])
        print(f"     {t:<16} d={dims[t]:<4} best `{b.split('|')[2]:<13}` "
              f"{cells[b]['mean']:.6f} ± {cells[b]['sd']:.6f}   "
              f"gap to `coval_core` {CORE_A2 - cells[b]['mean']:+.6f}")
    best_cell = max(clean, key=lambda k: clean[k]["mean"])
    bar = clean[best_cell]["mean"]
    se = clean[best_cell]["sd"] / np.sqrt(clean[best_cell]["n"])
    nf_t = {t: float(np.mean([v["sd"] for k, v in clean.items() if f"|{t}|" in k])) for t in TIERS}
    print(f"     ⭐ best clean cell `{best_cell}` {bar:.6f} ± {clean[best_cell]['sd']:.6f} "
          f"(se {se:.6f})")
    leak_pairs = [(k, k.replace("clean|", "LEAK|")) for k in clean if k.replace("clean|", "LEAK|")
                  in grid]
    leak_delta = float(np.mean([grid[b]["mean"] - grid[a]["mean"] for a, b in leak_pairs]))
    print(f"     ⭐ LEAK AUDIT: vectoriser fit on ALL prompts raises the bar by {leak_delta:+.6f} "
          f"over {len(leak_pairs)} cells AT THE RICHEST TIER ONLY (budget) — what the guard prevents")
    out["e1"] = {"grid": grid, "best_cell": best_cell, "bar": bar, "se": se, "dims": dims,
                 "noise_floor_per_tier": nf_t, "leak_delta": leak_delta}

    # ================= FORCED CHECK ==============================================================
    over = [k for k, v in grid.items() if v["mean"] > CEIL_HO]
    print(f"\n  ⛔ FORCED CHECK (a DERIVATION, never evidence): every bar <= CEIL_HO {CEIL_HO}. "
          f"violations: {len(over)}   {'PASS' if not over else 'FAIL — INSTRUMENT BROKEN'}")
    if over:
        print("  UNRUNNABLE: a bar exceeded the generalising ceiling. Exit 2, never 0.")
        return 2

    # ================= OBJECT ====================================================================
    t1 = clean.get("clean|T1_lexical14|logistic_C1.0", {}).get("mean", float("nan"))
    ok = abs(t1 - R824_BAR) < 2e-3
    print(f"\n  OBJECT CHECK  tier1 logistic_C1.0 {t1:.6f} vs R824's {R824_BAR} "
          f"(tol 2e-3, 10 vs 20 splits)   {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: tier 1 did not reproduce R824. Exit 2, never 0.")
        return 2

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    plac = {}
    for tier in TIERS:
        vals = []
        for s, pm in enumerate(splits[:5]):
            fit, ev = pm[: N // 2], pm[N // 2:]
            Xs = build(tier, fit, False)
            r2 = np.random.default_rng(600 + s)
            Ysh = np.array([Y[i][r2.permutation(6)] * r2.choice([-1, 1], 6) for i in range(N)])
            v = fit_eval(dict(models(s))["logistic_C1.0"], fit, ev, Xs, Ysh)
            if v is not None:
                vals.append(v)
        plac[tier] = float(np.mean(vals))
    chance = float(np.mean([a2_h(rng.normal(size=(N, 4)), range(N)) for _ in range(20)]))
    plac_ok = all(v < R824_BAR and abs(v - chance) < 0.03 for v in plac.values())
    print(f"     PLACEBO   shuffled labels per tier: " +
          "  ".join(f"{t[:2]} {plac[t]:.4f}" for t in TIERS) + f"   chance {chance:.4f}   "
          f"PASS: {plac_ok}")

    pos = {}
    for g in (1.0, 0.5, 0.2, 0.0):
        r3 = np.random.default_rng(777)
        wt = np.zeros(XLz.shape[2])
        wt[0] = 1.0
        Ypl = np.array([[np.sign(g * ((XLz[i][u] - XLz[i][w]) @ wt) + (1 - g) * r3.normal() * 3.0)
                         or 1.0 for u, w in PR] for i in range(N)])
        vals = []
        for s, pm in enumerate(splits[:5]):
            fit, ev = pm[: N // 2], pm[N // 2:]
            v = fit_eval(dict(models(s))["logistic_C1.0"], fit, ev, XLz, Ypl, key=Ypl)
            if v is not None and not np.isnan(v):
                vals.append(v)
        pos[str(g)] = float(np.mean(vals)) if vals else float("nan")
    mono = all(pos[str(a)] >= pos[str(b)] - 1e-9 for a, b in ((1.0, .5), (.5, .2), (.2, 0.)))
    pos_ok = bool(pos["1.0"] > 0.90 and pos["0.0"] < 0.60 and mono)
    print(f"     POSITIVE  dose vs THE PLANT: " + "  ".join(f"g={g} {pos[str(g)]:.4f}"
          for g in (1.0, 0.5, 0.2, 0.0)) + f"   monotone {mono}   PASS: {pos_ok}")

    A2 = {}
    for a in sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                    if not p.stem.startswith("sat08") and "_08b" not in p.stem):
        try:
            sat = load_sat(RES / f"sat_{a}.npz")
        except Exception:
            continue
        if not all(p in sat for p in pids):
            continue
        A2[a] = np.array([float((H[p] == np.array(cls(yvec(sat[p],
                          sorted({i for i, _ in sat[p]}))))).mean()) for p in pids])
    barv = np.full(N, bar)
    real_margin = float(np.mean([(A2[a] - barv).mean() for a in A2]))
    strict_v = np.array([float((H[pids[i]] == np.sign(
        XL[i][[u for u, _ in PR], 0] - XL[i][[w for _, w in PR], 0])).mean()) for i in range(N)])
    nl = np.array([float(strict_v[rng.integers(0, N, size=N)].mean() - strict_v.mean())
                   for _ in range(200)])
    try:
        assert_null_is_informative(nl, real_margin, name="R825 negative control")
        neg_ok = bool(abs(nl.mean()) < 2 * nl.std())
        print(f"     NEGATIVE  synthetic arm from the strict bar's own distribution: "
              f"{nl.mean():+.5f} ± {nl.std():.5f}   PASS: {neg_ok}")
    except AssertionError as e:
        print(f"     NEGATIVE  ⛔ {e}")
        neg_ok = False

    # ⭐ SHAM SWEPT PER TIER — random features MATCHED IN DIMENSION at each tier
    sham = {}
    for tier in TIERS:
        d = dims[tier]
        vals = []
        for s, pm in enumerate(splits[:5]):
            fit, ev = pm[: N // 2], pm[N // 2:]
            Xr = np.random.default_rng(900 + s).normal(size=(N, 4, d))
            v = fit_eval(dict(models(s))["logistic_C1.0"], fit, ev, Xr, Y)
            if v is not None:
                vals.append(v)
        sham[tier] = float(np.mean(vals))
        print(f"     SHAM      [{tier:<16} d={d:<4}] {d} RANDOM features: {sham[tier]:.6f}   "
              f"excess of the real tier over it "
              f"{max(v['mean'] for k, v in clean.items() if f'|{tier}|' in k) - sham[tier]:+.6f}")
    print(f"     NOISE FLOOR per tier: " + "  ".join(f"{t[:2]} {nf_t[t]:.4f}" for t in TIERS))

    gate = bool(plac_ok and pos_ok and neg_ok and not over)
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo": plac, "chance": chance, "placebo_ok": plac_ok, "positive": pos,
                       "positive_ok": pos_ok, "negative_mean": float(nl.mean()),
                       "negative_sd": float(nl.std()), "negative_ok": neg_ok, "sham": sham,
                       "ceiling_violations": len(over), "gate": gate}

    # ================= E2 · the gap, and does ④ exclude the core? ================================
    print("\n  E2 - ④'s EXCLUSION COUNT AT THE RICHEST BAR")
    idx = rng.integers(0, N, size=(NBOOT, N))
    rows, ps = [], []
    for a in sorted(A2, key=lambda a: A2[a].mean()):
        m = float(A2[a].mean() - bar)
        se_a = float(np.std(A2[a][idx].mean(axis=1)))
        half = 1.96 * np.hypot(se_a, se)
        rows.append({"arm": a, "a2": float(A2[a].mean()), "margin": m, "lo": m - half,
                     "hi": m + half, "excluded": bool(m + half < 0)})
        d = (A2[a][idx].mean(axis=1) - bar)
        ps.append(max(min(2.0 * min((d <= 0).mean(), (d >= 0).mean()), 1.0), 1.0 / (NBOOT + 1)))
    ex = [r["arm"] for r in rows if r["excluded"]]
    core = next(r for r in rows if r["arm"] == "coval_core")
    print(f"     ⭐ ④ excludes {len(ex)} of {len(rows)} at bar {bar:.6f}")
    print(f"     ⭐ `coval_core` {core['a2']:.6f}   margin {core['margin']:+.6f} "
          f"[{core['lo']:+.6f}, {core['hi']:+.6f}]   EXCLUDED: {core['excluded']}")
    keep = bh(ps)
    print(f"     BH q=0.05 over {len(ps)} arm tests: {int(keep.sum())} survive, "
          f"{int((~keep).sum())} do not (reported, not hidden)")
    out["e2"] = {"rows": rows, "excluded": len(ex), "core": core, "bh_survive": int(keep.sum())}

    # ================= E3 · saturation ===========================================================
    print("\n  E3 - SATURATION")
    tb = {t: max(v["mean"] for k, v in clean.items() if f"|{t}|" in k) for t in TIERS}
    for i, t in enumerate(TIERS):
        d = tb[t] - tb[TIERS[i - 1]] if i else 0.0
        print(f"     {t:<16} best {tb[t]:.6f}   rise over previous {d:+.6f}   "
              f"noise floor {nf_t[t]:.4f}   {'INSIDE the floor' if i and abs(d) <= nf_t[t] else ('—' if not i else 'OUTSIDE')}")
    last_rise = tb[TIERS[-1]] - tb[TIERS[-2]]
    saturated = bool(abs(last_rise) <= nf_t[TIERS[-1]])
    print(f"     ⭐ saturated at the richest tier: {saturated}   "
          f"bar + 1.96se = {bar + 1.96 * se:.6f} vs `coval_core` {CORE_A2}")
    out["e3"] = {"tier_best": tb, "last_rise": last_rise, "saturated": saturated}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif bar + 1.96 * se >= CORE_A2:
        world = "B"
    elif saturated:
        world = "A"
    else:
        world = "C"
    print(f"     gate {gate} · bar {bar:.6f} + 1.96se = {bar + 1.96*se:.6f} · core {CORE_A2} · "
          f"saturated {saturated} · ④ excludes {len(ex)} of {len(rows)}")
    print(f"     ->  WORLD {world}")
    out["world"] = world

    HERE.joinpath("results").mkdir(exist_ok=True)
    ap = HERE / "results" / "richest_bar.json"
    ap.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    print(f"\n  ARTIFACT {ap.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(ap.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
