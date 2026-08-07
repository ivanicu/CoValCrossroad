#!/usr/bin/env python3
"""R824 · is ④'s class closed under fitting?

④ reads "every rule computable from the response set alone" — a constraint on what a rule CONSUMES
AT INFERENCE, silent about what its CONSTRUCTION consumed. A supervised response-only predictor
reads only responses at inference but was fit on other prompts' human labels. See PREREGISTRATION.txt
for the two readings, D1-D4, the worlds and the gated kill.
"""
import hashlib
import itertools
import json
import pathlib
import re
import sys

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                    # noqa: E402
from assurance.null_is_informative import assert_null_is_informative   # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
NSPLIT = 20
STRICT_BAR = 0.455679
FEATNAMES = ["len_chars", "len_words", "distinct_words", "ttr", "sentences", "questions",
             "newlines", "bullets", "digits", "commas", "mean_word_len", "colons",
             "uppercase", "parens"]
FEATSETS = {"all14": FEATNAMES,
            "length_only": ["len_chars", "len_words", "distinct_words"],
            "non_length": [f for f in FEATNAMES if f not in
                           ("len_chars", "len_words", "distinct_words")]}


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    raise TypeError(type(o))


def feats(t):
    w = t.split()
    lw = [len(x) for x in w] or [0]
    return [len(t), len(w), len(set(x.lower() for x in w)),
            (len(set(x.lower() for x in w)) / len(w)) if w else 0.0,
            len(re.findall(r"[.!?]+", t)), t.count("?"), t.count("\n"),
            len(re.findall(r"(?m)^\s*[-*•]", t)), sum(c.isdigit() for c in t), t.count(","),
            float(np.mean(lw)), t.count(":"), sum(c.isupper() for c in t), t.count("(")]


def models(seed):
    m = [(f"logistic_C{c}", LogisticRegression(C=c, max_iter=2000, random_state=seed))
         for c in (0.01, 0.1, 1.0, 10.0, 100.0)]
    m.append(("ridge", RidgeClassifier(random_state=seed)))
    m.append(("gboost", GradientBoostingClassifier(n_estimators=60, max_depth=2,
                                                   random_state=seed)))
    return m


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
    out = {"instrument_unit": "a RULE", "claim_unit": "a CLAUSE"}
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
    X = np.array([[feats(t) for t in text[p]] for p in pids], float)          # (N, 4, 14)
    mu, sd = X.reshape(-1, 14).mean(0), X.reshape(-1, 14).std(0) + 1e-12
    Xz = (X - mu) / sd
    print(f"  POPULATION  {N} prompts x 4 responses x {len(FEATNAMES)} features")

    def a2_vs_key(S, sub, K):
        """S (N,4) scores vs an ARBITRARY answer key K (N,6). The positive control MUST use this:
        ⛔ the first version scored a PLANTED model against the REAL human labels, so it measured
        how well a length-planted rule predicts humans (0.4511, i.e. the strict bar) instead of
        whether the plant was recovered. §4: the control targeted a different statistic."""
        v = []
        for i in sub:
            s_ = np.sign(S[i][[u for u, _ in PR]] - S[i][[w for _, w in PR]])
            m = K[i] != 0
            if m.any():
                v.append(float((K[i][m] == s_[m]).mean()))
        return float(np.mean(v)) if v else float("nan")

    def a2_from_scores(S, sub):
        """S (N,4) scores -> A2 over the prompt subset `sub`."""
        v = []
        for i in sub:
            s = np.sign(S[i][[u for u, _ in PR]] - S[i][[w for _, w in PR]])
            v.append(float((H[pids[i]] == s).mean()))
        return float(np.mean(v)), np.array(v)

    # human MAJORITY pairwise sign per prompt, the supervised target
    Y = np.array([np.sign(H[p].sum(axis=0)) for p in pids])                   # (N, 6)

    def pairdata(sub, Xs, Ys):
        d, y = [], []
        for i in sub:
            for k, (u, w) in enumerate(PR):
                if Ys[i][k] == 0:
                    continue
                d.append(Xs[i][u] - Xs[i][w])
                y.append(Ys[i][k])
        return np.array(d), np.array(y)

    def fit_eval(name, mdl, sub_fit, sub_ev, Xs, Ys, key=None):
        d, y = pairdata(sub_fit, Xs, Ys)
        if len(set(y.tolist())) < 2:
            return None
        mdl.fit(d, y)
        w = None
        if hasattr(mdl, "coef_"):
            w = np.asarray(mdl.coef_).ravel()
            S = Xs @ w
        else:
            S = np.array([[float(mdl.decision_function((Xs[i][j] - Xs[i]).mean(axis=0)
                          .reshape(1, -1))[0]) for j in range(4)] for i in range(len(Xs))])
        return a2_from_scores(S, sub_ev)[0] if key is None else a2_vs_key(S, sub_ev, key)

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK - the strict bar must reproduce R823")
    S_len = X[:, :, 0]
    strict_all, strict_v = a2_from_scores(S_len, range(N))
    ok = abs(strict_all - STRICT_BAR) < 5e-5
    print(f"     `max_len_chars` {strict_all:.6f} vs R823's committed {STRICT_BAR}   "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: the strict bar did not reproduce. Exit 2, never 0.")
        return 2
    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if not p.stem.startswith("sat08") and "_08b" not in p.stem)
    A2 = {}
    for a in arms:
        try:
            sat = load_sat(RES / f"sat_{a}.npz")
        except Exception:
            continue
        if not all(p in sat for p in pids):
            continue
        A2[a] = np.array([float((H[p] == np.array(cls(yvec(sat[p],
                          sorted({i for i, _ in sat[p]}))))).mean()) for p in pids])
    print(f"     arms scoreable: {len(A2)}")
    out["object"] = {"strict_bar": strict_all, "n_prompts": N, "n_arms": len(A2)}

    # ================= E3 · the specification curve (run first; E1 reads its max) ================
    print("\n  E3 - THE SPECIFICATION CURVE OF THE LEARNED BAR  (held out, never in sample)")
    print("     ⛔ D1 (DERIVATION): a fitted combination cannot score below its best single feature")
    print("        IN SAMPLE, so an in-sample rise is forced. Only the held-out bar can differ.")
    rng = np.random.default_rng(20250806)
    splits = [np.random.default_rng(2000 + s).permutation(N) for s in range(NSPLIT)]
    curve = {}
    for fs, cols in FEATSETS.items():
        ci = [FEATNAMES.index(c) for c in cols]
        for mname, _ in models(0):
            vals = []
            for s, pm in enumerate(splits):
                fit, ev = pm[: N // 2], pm[N // 2:]
                mdl = dict(models(s))[mname]
                r = fit_eval(mname, mdl, fit, ev, Xz[:, :, ci], Y)
                if r is not None:
                    vals.append(r)
            curve[f"{fs}|{mname}"] = {"mean": float(np.mean(vals)), "sd": float(np.std(vals)),
                                      "n": len(vals)}
    for k in sorted(curve, key=lambda k: -curve[k]["mean"]):
        v = curve[k]
        print(f"     {k:<28} held-out A2 {v['mean']:.6f} ± {v['sd']:.6f}   "
              f"{'ABOVE' if v['mean'] > STRICT_BAR else 'below'} the strict bar")
    best_cell = max(curve, key=lambda k: curve[k]["mean"])
    bar_learned = curve[best_cell]["mean"]
    nf = curve[best_cell]["sd"]
    n_above = sum(1 for v in curve.values() if v["mean"] > STRICT_BAR)
    print(f"     ⭐ best cell `{best_cell}` {bar_learned:.6f} ± {nf:.6f}   "
          f"cells above the strict bar: {n_above} of {len(curve)}")
    out["e3"] = {"curve": curve, "best_cell": best_cell, "bar_learned": bar_learned,
                 "noise_floor": nf, "cells_above": n_above, "cells": len(curve)}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    plac = []
    for s, pm in enumerate(splits):
        fit, ev = pm[: N // 2], pm[N // 2:]
        Ysh = Y.copy()
        r2 = np.random.default_rng(500 + s)
        for i in range(N):
            Ysh[i] = Ysh[i][r2.permutation(6)] * r2.choice([-1, 1], 6)
        v = fit_eval("logistic_C1.0", dict(models(s))["logistic_C1.0"], fit, ev, Xz, Ysh)
        if v is not None:
            plac.append(v)
    plac_m = float(np.mean(plac))
    chance = float(np.mean([a2_from_scores(rng.normal(size=(N, 4)), range(N))[0]
                            for _ in range(20)]))
    plac_ok = bool(plac_m < STRICT_BAR and abs(plac_m - chance) < 0.02)
    print(f"     PLACEBO   labels SHUFFLED at fit: {plac_m:.6f}   random-scorer chance "
          f"{chance:.6f}   below the strict bar and at chance: {plac_ok}")

    # ⭐ POSITIVE as a DOSE-RESPONSE, scored against the PLANT and not against the humans.
    #    g=0 plants RANDOM signs -- a learnable-shaped target with no learnable signal -- because
    #    the first version planted all-zero signs, which pairdata drops entirely, returning nan.
    #    A control that returns nan is not a control.
    pos = {}
    for g in (1.0, 0.5, 0.2, 0.0):
        r3 = np.random.default_rng(777)
        wtrue = np.zeros(14)
        wtrue[0] = 1.0
        Ypl = np.zeros((N, 6))
        for i in range(N):
            for k, (u, w) in enumerate(PR):
                sig = (Xz[i][u] - Xz[i][w]) @ wtrue
                noise = r3.normal() * 3.0
                Ypl[i][k] = np.sign(g * sig + (1.0 - g) * noise) or 1.0
        vals = []
        for s_ in range(8):
            pm = splits[s_]
            fit, ev = pm[: N // 2], pm[N // 2:]
            v = fit_eval("logistic_C1.0", dict(models(s_))["logistic_C1.0"], fit, ev, Xz, Ypl,
                         key=Ypl)
            if v is not None and not np.isnan(v):
                vals.append(v)
        pos[str(g)] = float(np.mean(vals)) if vals else float("nan")
        print(f"     POSITIVE  g={g:<4} recovery against the PLANT: {pos[str(g)]:.6f}")
    dose_monotone = all(pos[str(a)] >= pos[str(b)] - 1e-9 for a, b in
                        ((1.0, 0.5), (0.5, 0.2), (0.2, 0.0)))
    pos_ok = bool(pos["1.0"] > 0.90 and pos["0.0"] < 0.60 and dose_monotone)
    print(f"     POSITIVE  recovers at g=1 ({pos['1.0']:.4f}), fails at g=0 ({pos['0.0']:.4f}), "
          f"monotone in dose: {dose_monotone}   PASS: {pos_ok}")

    real_margin = float(np.mean([(A2[a] - strict_v).mean() for a in A2]))
    nl = np.array([float(strict_v[rng.integers(0, N, size=N)].mean() - strict_v.mean())
                   for _ in range(200)])
    try:
        assert_null_is_informative(nl, real_margin, name="R824 negative control")
        neg_ok = bool(abs(nl.mean()) < 2 * nl.std() and real_margin > nl.max())
        print(f"     NEGATIVE  synthetic arm from the bar's own distribution: {nl.mean():+.5f} ± "
              f"{nl.std():.5f}   real {real_margin:+.5f}   PASS: {neg_ok}")
    except AssertionError as e:
        print(f"     NEGATIVE  ⛔ {e}")
        neg_ok = False

    # ⭐ SHAM: the IDENTICAL procedure on RANDOM features, matched in count and dimension
    Xr = rng.normal(size=Xz.shape)
    sham_vals = []
    for s, pm in enumerate(splits):
        fit, ev = pm[: N // 2], pm[N // 2:]
        v = fit_eval("logistic_C1.0", dict(models(s))["logistic_C1.0"], fit, ev, Xr, Y)
        if v is not None:
            sham_vals.append(v)
    sham = float(np.mean(sham_vals))
    print(f"     SHAM      the SAME learner on 14 RANDOM features: held-out {sham:.6f} ± "
          f"{np.std(sham_vals):.6f}")
    print(f"               so fitting on noise buys {sham - chance:+.6f} over chance; the real "
          f"learned bar is {bar_learned - sham:+.6f} above the sham")
    print(f"     NOISE FLOOR  best cell across {NSPLIT} splits: sd {nf:.6f}")

    gate = bool(plac_ok and pos_ok and neg_ok)
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["positive_dose"] = pos
    out["controls"] = {"placebo": plac_m, "chance": chance, "placebo_ok": plac_ok,
                       "positive": pos, "positive_ok": pos_ok, "negative_mean": float(nl.mean()),
                       "negative_sd": float(nl.std()), "negative_ok": neg_ok, "sham": sham,
                       "sham_sd": float(np.std(sham_vals)), "gate": gate}

    # ================= E1/E2 · the two readings ==================================================
    print("\n  E1/E2 - ④'s EXCLUSION COUNT UNDER EACH READING")
    idx = rng.integers(0, N, size=(NBOOT, N))
    rows, ps = [], []
    for a in sorted(A2, key=lambda a: A2[a].mean()):
        m_s = float((A2[a] - strict_v).mean())
        d = (A2[a] - strict_v)[idx].mean(axis=1)
        lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
        p = max(min(2.0 * min((d <= 0).mean(), (d >= 0).mean()), 1.0), 1.0 / (NBOOT + 1))
        # permissive: the learned bar is a scalar with its own sd across splits
        m_p = float(A2[a].mean() - bar_learned)
        se_a = float(np.std(A2[a][idx].mean(axis=1)))
        lo_p = m_p - 1.96 * np.hypot(se_a, nf)
        hi_p = m_p + 1.96 * np.hypot(se_a, nf)
        rows.append({"arm": a, "a2": float(A2[a].mean()),
                     "strict_margin": m_s, "strict_lo": lo, "strict_hi": hi,
                     "strict_excluded": bool(hi < 0),
                     "perm_margin": m_p, "perm_lo": lo_p, "perm_hi": hi_p,
                     "perm_excluded": bool(hi_p < 0)})
        ps.append(p)
    ex_s = [r["arm"] for r in rows if r["strict_excluded"]]
    ex_p = [r["arm"] for r in rows if r["perm_excluded"]]
    for r in rows[:6]:
        print(f"     {r['arm']:<22} A2 {r['a2']:.4f}   strict {r['strict_margin']:+.4f} "
              f"[{r['strict_lo']:+.4f}, {r['strict_hi']:+.4f}]{'  EXCLUDED' if r['strict_excluded'] else '':<10}"
              f"   permissive {r['perm_margin']:+.4f} [{r['perm_lo']:+.4f}, {r['perm_hi']:+.4f}]"
              f"{'  EXCLUDED' if r['perm_excluded'] else ''}")
    print(f"     ⭐ STRICT reading: ④ excludes {len(ex_s)} of {len(rows)}")
    print(f"     ⭐ PERMISSIVE reading: ④ excludes {len(ex_p)} of {len(rows)}   {ex_p if ex_p else ''}")
    keep = bh(ps)
    print(f"     BH q=0.05 over {len(ps)} arm tests: {int(keep.sum())} survive, "
          f"{int((~keep).sum())} do not (reported, not hidden)")
    out["e1"] = {"rows": rows, "excluded_strict": len(ex_s), "excluded_permissive": len(ex_p),
                 "excluded_permissive_names": ex_p, "bh_survive": int(keep.sum())}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif bar_learned > STRICT_BAR + nf and len(ex_p) >= 1:
        world = "B"
    elif bar_learned <= STRICT_BAR + nf:
        world = "A"
    else:
        world = "C"
    print(f"     gate {gate} · learned bar {bar_learned:.6f} vs strict {STRICT_BAR} + nf {nf:.6f} "
          f"· permissive exclusions {len(ex_p)} · sham {sham:.6f}")
    print(f"     ->  WORLD {world}")
    out["world"] = world
    out["bar_learned"] = bar_learned
    out["strict_bar"] = STRICT_BAR

    HERE.joinpath("results").mkdir(exist_ok=True)
    ap = HERE / "results" / "closed_under_fitting.json"
    ap.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    print(f"\n  ARTIFACT {ap.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(ap.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
