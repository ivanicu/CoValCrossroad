#!/usr/bin/env python3
"""R826 · is clause ④ evaluable without a stated modelling budget?

Three defensible response-only classes give three verdicts on the released core. This sweeps the
modelling-effort dial and asks whether the bar SATURATES. See PREREGISTRATION.txt for D1-D4 (D2:
a crossing exists BY CONSTRUCTION, so finding one is not a finding), the worlds and the gated kill.
"""
import hashlib, itertools, json, pathlib, re, sys
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

sys.stdout.reconfigure(line_buffering=True)
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls                            # noqa: E402

RES = ROOT / "corebench/results"; HERE = pathlib.Path(__file__).resolve().parent
PR = list(itertools.combinations(range(4), 2))
NSPLIT = 8
KS = [0, 5, 10, 20, 40, 60, 100, 150, 200]
KMAX = 200
R824_BAR, R825_BAR, CORE_A2 = 0.519689, 0.572335, 0.566477
TCRIT = {7: 2.365}


def _plain(o):
    for t, f in ((np.bool_, bool), (np.integer, int), (np.floating, float)):
        if isinstance(o, t):
            return f(o)
    raise TypeError(type(o))


def lex(t):
    w = t.split(); lw = [len(x) for x in w] or [0]
    return [len(t), len(w), len(set(x.lower() for x in w)),
            (len(set(x.lower() for x in w)) / len(w)) if w else 0.0,
            len(re.findall(r"[.!?]+", t)), t.count("?"), t.count("\n"),
            len(re.findall(r"(?m)^\s*[-*•]", t)), sum(c.isdigit() for c in t), t.count(","),
            float(np.mean(lw)), t.count(":"), sum(c.isupper() for c in t), t.count("(")]


def bh(pv, q=0.05):
    p = np.asarray(pv, float); o = np.argsort(p); m = len(p); keep = np.zeros(m, bool)
    for r, i in enumerate(o, 1):
        if p[i] <= q * r / m:
            keep[o[:r]] = True
    return keep


def main():
    out = {"instrument_unit": "a RULE CLASS at effort k", "claim_unit": "a CLAUSE"}
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
    from score import yvec
    sat = load_sat(RES / "sat_coval_core.npz")
    CORE = np.array([float((H[p] == np.array(cls(yvec(sat[p],
                     sorted({i for i, _ in sat[p]}))))).mean()) for p in pids])
    print(f"  POPULATION {N} prompts · `coval_core` {CORE.mean():.6f} · k in {KS} · {NSPLIT} splits")
    print(f"  ⛔ D2: a crossing EXISTS BY CONSTRUCTION between k=0 ({R824_BAR}, admits) and")
    print(f"     k=100 ({R825_BAR}, excludes). Only its LOCATION and SATURATION are measurable.")

    def a2(S, sub):
        return np.array([float((H[pids[i]] == np.sign(S[i][[u for u, _ in PR]]
                        - S[i][[w for _, w in PR]])).mean()) for i in sub])

    def fit_bar(Xs, fit, ev, Ys):
        d, y = [], []
        for i in fit:
            for kk, (u, w) in enumerate(PR):
                if Ys[i][kk] == 0: continue
                d.append(Xs[i][u] - Xs[i][w]); y.append(Ys[i][kk])
        if len(set(y)) < 2: return None
        m = LogisticRegression(C=1.0, max_iter=1500).fit(np.array(d), np.array(y))
        return a2(Xs @ np.asarray(m.coef_).ravel(), ev)

    real = {k: [] for k in KS}; sham = {k: [] for k in KS}
    paired = {k: [] for k in KS}
    for s in range(NSPLIT):
        pm = np.random.default_rng(3000 + s).permutation(N)
        fit, ev = pm[: N // 2], pm[N // 2:]
        rows = np.array([i * 4 + j for i in fit for j in range(4)])
        mu, sd = XL.reshape(-1, 14)[rows].mean(0), XL.reshape(-1, 14)[rows].std(0) + 1e-12
        XLz = (XL - mu) / sd
        docs = [TXT[i][j] for i in fit for j in range(4)]
        alld = [TXT[i][j] for i in range(N) for j in range(4)]
        v = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=5, max_features=8000)
        v.fit(docs); Mfit = v.transform(docs)
        # D4: components are NESTED -- one SVD(KMAX) fit per split serves every k by slicing
        svd = TruncatedSVD(n_components=KMAX, random_state=0).fit(Mfit)
        Zf = svd.transform(Mfit); zm, zs = Zf.mean(0), Zf.std(0) + 1e-12
        ZALL = ((svd.transform(v.transform(alld)) - zm) / zs).reshape(N, 4, -1)
        rng = np.random.default_rng(900 + s)
        ZRND = rng.normal(size=ZALL.shape)
        for k in KS:
            Xs = XLz if k == 0 else np.concatenate([XLz, ZALL[:, :, :k]], axis=2)
            b = fit_bar(Xs, fit, ev, Y)
            real[k].append(float(b.mean())); paired[k].append(float((b - CORE[ev]).mean()))
            Xr = XLz if k == 0 else np.concatenate([XLz, ZRND[:, :, :k]], axis=2)
            br = fit_bar(Xr, fit, ev, Y)
            sham[k].append(float(br.mean()))
        print(f"     split {s}: " + " ".join(f"k{k}={real[k][-1]:.4f}" for k in KS))

    print("\n  E1/E3 - THE EFFORT CURVE, HELD OUT")
    print(f"     {'k':>4} {'bar':>9} {'sd':>8} {'rise':>9} {'sham':>9} {'excess':>9}  vs core")
    prev = None; rows_out = []
    for k in KS:
        b = np.array(real[k]); sh = np.array(sham[k]); pd_ = np.array(paired[k])
        se = pd_.std(ddof=1) / np.sqrt(len(pd_)); t = TCRIT[len(pd_) - 1]
        lo, hi = pd_.mean() - t * se, pd_.mean() + t * se
        vd = "EXCLUDES core" if lo > 0 else ("admits core" if hi < 0 else "indistinguishable")
        rise = float(b.mean() - prev) if prev is not None else float("nan")
        rows_out.append({"k": k, "bar": float(b.mean()), "sd": float(b.std(ddof=1)),
                         "rise": rise, "sham": float(sh.mean()),
                         "excess": float(b.mean() - sh.mean()), "paired": float(pd_.mean()),
                         "lo": float(lo), "hi": float(hi), "verdict": vd,
                         "p": float(2 * min((pd_ > 0).mean(), (pd_ < 0).mean()))})
        print(f"     {k:>4} {b.mean():9.6f} {b.std(ddof=1):8.5f} "
              f"{('     n/a' if prev is None else f'{rise:+9.6f}')} {sh.mean():9.6f} "
              f"{b.mean()-sh.mean():+9.6f}  {pd_.mean():+.6f} [{lo:+.6f},{hi:+.6f}] {vd}")
        prev = b.mean()
    out["curve"] = rows_out

    print("\n  OBJECT CHECK - the two cells whose answers are known")
    nf = float(np.mean([r["sd"] for r in rows_out]))
    ok0 = abs(rows_out[0]["bar"] - R824_BAR) < 3 * nf
    i100 = KS.index(100)
    ok100 = abs(rows_out[i100]["bar"] - R825_BAR) < 3 * nf
    print(f"     k=0   {rows_out[0]['bar']:.6f} vs R824 {R824_BAR}   {'PASS' if ok0 else 'FAIL'}")
    print(f"     k=100 {rows_out[i100]['bar']:.6f} vs R825 {R825_BAR}   "
          f"{'PASS' if ok100 else 'FAIL'}   (tol 3x mean per-split sd = {3*nf:.4f})")
    if not (ok0 and ok100):
        print("  UNRUNNABLE: a known cell did not reproduce. Exit 2, never 0.")
        return 2

    print("\n  CONTROLS")
    plac = 0.0
    print(f"     PLACEBO   `coval_core` against itself: {plac:.1e}   PASS - exactly 0")
    pos = {}
    for g in (1.0, 0.5, 0.2, 0.0):
        r3 = np.random.default_rng(777); wt = np.zeros(14); wt[0] = 1.0
        vals = []
        for s in range(4):
            pm = np.random.default_rng(3000 + s).permutation(N)
            fit, ev = pm[: N // 2], pm[N // 2:]
            rws = np.array([i * 4 + j for i in fit for j in range(4)])
            mu, sd = XL.reshape(-1, 14)[rws].mean(0), XL.reshape(-1, 14)[rws].std(0) + 1e-12
            XLz = (XL - mu) / sd
            Ypl = np.array([[np.sign(g * ((XLz[i][u] - XLz[i][w]) @ wt)
                             + (1 - g) * r3.normal() * 3.0) or 1.0 for u, w in PR]
                            for i in range(N)])
            d, y = [], []
            for i in fit:
                for kk, (u, w) in enumerate(PR):
                    d.append(XLz[i][u] - XLz[i][w]); y.append(Ypl[i][kk])
            m = LogisticRegression(C=1.0, max_iter=1500).fit(np.array(d), np.array(y))
            S = XLz @ np.asarray(m.coef_).ravel()
            sc = [float((Ypl[i] == np.sign(S[i][[u for u, _ in PR]]
                  - S[i][[w for _, w in PR]])).mean()) for i in ev]
            vals.append(float(np.mean(sc)))
        pos[str(g)] = float(np.mean(vals))
    mono = all(pos[str(a)] >= pos[str(b)] - 1e-9 for a, b in ((1.0,.5),(.5,.2),(.2,0.)))
    pos_ok = bool(pos["1.0"] > 0.90 and pos["0.0"] < 0.60 and mono)
    print(f"     POSITIVE  dose vs THE PLANT: " + "  ".join(f"g={g} {pos[str(g)]:.4f}"
          for g in (1.0,0.5,0.2,0.0)) + f"   monotone {mono}   PASS: {pos_ok}")
    neg = []
    for s in range(4):
        pm = np.random.default_rng(3000 + s).permutation(N)
        fit, ev = pm[: N // 2], pm[N // 2:]
        rws = np.array([i * 4 + j for i in fit for j in range(4)])
        mu, sd = XL.reshape(-1, 14)[rws].mean(0), XL.reshape(-1, 14)[rws].std(0) + 1e-12
        r2 = np.random.default_rng(600 + s)
        Ysh = np.array([Y[i][r2.permutation(6)] * r2.choice([-1, 1], 6) for i in range(N)])
        b = fit_bar((XL - mu) / sd, fit, ev, Ysh)
        if b is not None: neg.append(float(b.mean()))
    neg_m = float(np.mean(neg)); neg_ok = neg_m < rows_out[0]["bar"]
    print(f"     NEGATIVE  labels shuffled at fit: {neg_m:.6f}   below the k=0 bar: {neg_ok}")
    print(f"     SHAM      swept at EVERY k (column above); excess at kmax "
          f"{rows_out[-1]['excess']:+.6f}")
    print(f"     NOISE FLOOR  mean per-split sd across k: {nf:.6f}")
    gate = bool(pos_ok and neg_ok)
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo": plac, "positive": pos, "positive_ok": pos_ok,
                       "negative": neg_m, "negative_ok": neg_ok, "noise_floor": nf, "gate": gate}

    keep = bh([r["p"] for r in rows_out])
    print(f"     BH q=0.05 over {len(rows_out)} paired tests: {int(keep.sum())} survive, "
          f"{int((~keep).sum())} do not (reported, not hidden)")

    print("\n  THE KILL -- conditional, gated on the controls")
    last_rise = rows_out[-1]["rise"]; sat = abs(last_rise) <= nf
    cross = next((r["k"] for r in rows_out if r["lo"] > 0), None)
    if not gate: world = "UNVERIFIED"
    elif not sat: world = "C"
    elif rows_out[-1]["lo"] > 0: world = "A"
    elif rows_out[-1]["hi"] < 0: world = "B"
    else: world = "UNVERIFIED"
    print(f"     gate {gate} · last rise {last_rise:+.6f} vs noise floor {nf:.6f} · "
          f"saturated {sat} · crossing k* = {cross}")
    print(f"     ->  WORLD {world}")
    out["world"] = world; out["k_star"] = cross; out["saturated"] = sat
    (HERE / "results").mkdir(exist_ok=True)
    ap = HERE / "results" / "effort_curve.json"
    ap.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    print(f"\n  ARTIFACT {ap.relative_to(ROOT)}  md5 {hashlib.md5(ap.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
