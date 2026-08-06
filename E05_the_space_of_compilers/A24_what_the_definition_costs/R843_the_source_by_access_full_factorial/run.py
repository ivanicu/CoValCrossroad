#!/usr/bin/env python3
"""R843 · the SOURCE x ACCESS full factorial — the cell R811 called structurally absent.

See PREREGISTRATION.txt. Two sources (the prompt's own rubric · the fixed generic 16) crossed with
four ACCESS levels (nothing · prompt text · other prompts' labels · this prompt's labels). Every
cell is scored from committed satisfaction matrices; the only new object is the SELECTOR.
"""
import hashlib
import itertools
import json
import math
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls, L                       # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
PR = list(itertools.combinations(range(4), 2))
KS = [2, 4, 8]
SEEDS = [0, 1, 2, 3, 4]
NBOOT = 1200
ORACLE_CAP = 3000          # subsets sampled when C(n,k) exceeds it; printed per (source, k)
CEIL_ATT = 0.686265        # R804's in-sample supremum over weak orders — a DERIVED upper bound
NFIT = 2                   # cross-fitting halves for A2


def _plain(o):
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def bh(pv, q=0.05):
    p = np.asarray(pv, float)
    o = np.argsort(p)
    m = len(p)
    kmax = 0
    for r, i in enumerate(o, 1):
        if p[i] <= q * r / m:
            kmax = r
    keep = np.zeros(m, bool)
    keep[o[:kmax]] = True
    return keep


def main():
    out = {"instrument_unit": "a (prompt, annotator) judgement", "claim_unit": "a SOURCE x ACCESS cell"}
    tg, _ = load_targets()

    # ---------------------------------------------------------------- candidate sets and texts
    pool_txt = list(json.loads((RES / "core_genericpool16.json").read_text()).values())[0]
    POOLTXT = [c["criterion"] if isinstance(c, dict) else c for c in pool_txt]
    # ⛔ THE RUBRIC FILE DOES NOT CARRY `prompt_id`. It keys on `conversation.id`, and that id has
    #    ZERO overlap with the 1,078 prompt ids — measured, not assumed. The release joins the two
    #    by MESSAGE CONTENT, which is what `covalx.judge.load_join` exists for. Re-deriving the key
    #    by hand here would have silently produced an empty population, and an empty population
    #    that still runs is the failure this project names most often.
    from covalx.judge import load_join                                 # noqa: E402
    rub = {}
    for pid, _p, r in load_join(ROOT / "data/comparisons.jsonl",
                                ROOT / "data/conversation_rubrics.jsonl"):
        items = r.get("coval_full") or []
        rub[pid] = ([it["criterion"] for it in items],
                    [float(np.mean([s["score"] for s in (it.get("scores") or [])]))
                     if it.get("scores") else 0.0 for it in items])
    ptxt = {}
    for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        ptxt[r["prompt_id"]] = " ".join(str(m.get("content", ""))
                                        for m in r["prompt"]["messages"] if m.get("content"))

    FULL = load_sat(RES / "sat_full.npz")
    POOL = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(set(FULL) & set(POOL) & set(rub) & set(ptxt) &
                  {p for p in tg if len(tg[p]) >= 2})
    H0 = {p: np.array([cls(np.array(t[0], float))
                       for i, t in enumerate(tg[p]) if i % 2 == 0]) for p in pids}
    pids = [p for p in pids if len(H0[p]) >= 1 and len(rub[p][0]) >= max(KS)]
    N = len(pids)
    NPOOL = len({i for i, _ in POOL[pids[0]]})

    def mat(sat, p, n):
        """(n_criteria, 4) satisfaction. Missing entries are 0.0, the repo's own convention."""
        return np.array([[sat[p].get((i, x), 0.0) for x in L] for i in range(n)], float)

    S1 = {p: mat(FULL, p, len(rub[p][0])) for p in pids}      # the prompt's own rubric
    S2 = {p: mat(POOL, p, NPOOL) for p in pids}               # the fixed generic 16
    W1 = {p: np.array(rub[p][1], float) for p in pids}        # human importance, S1 only
    print(f"  POPULATION  {N} prompts · S1 median {int(np.median([S1[p].shape[0] for p in pids]))} "
          f"own criteria · S2 {NPOOL} fixed generic criteria · agreement on the EVEN annotator half")
    print(f"  ⛔ DERIVED   every cell <= CEIL_ATT {CEIL_ATT} (R804). Asserted, never evidence.")

    # ---------------------------------------------------------------- the estimand
    def agree(C, p, idx):
        """A2 agreement of the subset `idx` of candidate matrix C on prompt p."""
        y = C[list(idx)].sum(axis=0)
        c = np.sign(y[[u for u, _ in PR]] - y[[w for _, w in PR]])
        return float((H0[p] == c).mean())

    def cell(SRC, sel, k):
        """-> per-prompt vector of agreement, one entry per prompt."""
        return np.array([agree(SRC[p], p, sel(p, k)) for p in pids])

    # ---------------------------------------------------------------- A1: label-free relevance
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import normalize
    allc = sorted({c for p in pids for c in rub[p][0]} | set(POOLTXT))
    vec = TfidfVectorizer(stop_words="english", sublinear_tf=True, min_df=2)
    vec.fit([ptxt[p] for p in pids] + allc)
    Pv = normalize(vec.transform([ptxt[p] for p in pids])).tocsr()
    poolv = normalize(vec.transform(POOLTXT)).tocsr()
    REL2 = np.asarray((Pv @ poolv.T).todense())                       # (N, 16) label-free
    REL1 = {}
    for i, p in enumerate(pids):
        cv = normalize(vec.transform(rub[p][0])).tocsr()
        REL1[p] = np.asarray((Pv[i] @ cv.T).todense()).ravel()
    pidx = {p: i for i, p in enumerate(pids)}
    print(f"  A1 RELEVANCE  tf-idf cosine(prompt text, criterion text). Reads no human label "
          f"anywhere. S1 mean {np.mean([REL1[p].mean() for p in pids]):.4f} · "
          f"S2 mean {REL2.mean():.4f}")

    # ---------------------------------------------------------------- A2: fit on OTHER prompts
    # per-criterion single-criterion agreement, the quantity A2 learns to predict
    def solo(SRC, p):
        C = SRC[p]
        s = np.sign(C[:, [u for u, _ in PR]] - C[:, [w for _, w in PR]])
        return np.array([float((H0[p] == s[i]).mean()) for i in range(C.shape[0])])

    SOLO1 = {p: solo(S1, p) for p in pids}
    SOLO2 = {p: solo(S2, p) for p in pids}
    half = np.array([pidx[p] % NFIT for p in pids])
    # S2: criteria are SHARED, so the transferable object is a ranking of the 16 fit on the other half
    RANK2 = {}
    for h in range(NFIT):
        fitp = [p for p in pids if pidx[p] % NFIT != h]
        RANK2[h] = np.mean([SOLO2[p] for p in fitp], axis=0)
    # S1: criteria are NOT shared, so the transferable object is a regression on label-free features
    from sklearn.linear_model import Ridge
    def feats(p):
        t = rub[p][0]
        return np.column_stack([REL1[p],
                                [len(x) for x in t],
                                [len(x.split()) for x in t],
                                [x.count(",") for x in t],
                                np.arange(len(t)) / max(len(t) - 1, 1)])
    MODEL1 = {}
    for h in range(NFIT):
        fitp = [p for p in pids if pidx[p] % NFIT != h]
        X = np.vstack([feats(p) for p in fitp])
        y = np.concatenate([SOLO1[p] for p in fitp])
        MODEL1[h] = Ridge(alpha=1.0).fit(X, y)
    PRED1 = {p: MODEL1[pidx[p] % NFIT].predict(feats(p)) for p in pids}

    # ---------------------------------------------------------------- A3: this prompt's labels
    rng_or = np.random.default_rng(4343)
    def oracle(SRC, p, k):
        C = SRC[p]
        n = C.shape[0]
        tot = math.comb(n, k)
        if tot <= ORACLE_CAP:
            subs = np.array(list(itertools.combinations(range(n), k)))
        else:
            subs = np.array([rng_or.choice(n, k, replace=False) for _ in range(ORACLE_CAP)])
        M = np.zeros((len(subs), n))
        M[np.arange(len(subs))[:, None], subs] = 1.0
        Y = M @ C
        Sg = np.sign(Y[:, [u for u, _ in PR]] - Y[:, [w for _, w in PR]])
        sc = (Sg[:, None, :] == H0[p][None, :, :]).mean(axis=(1, 2))
        return tuple(subs[int(np.argmax(sc))])

    # ---------------------------------------------------------------- the eight cells
    def top(v, k):
        return tuple(np.argsort(-np.asarray(v, float))[:k])

    def make(src, acc, seed=0):
        if src == "S1":
            SRC, REL, PREDW, WW = S1, REL1, PRED1, W1
            nof = lambda p: S1[p].shape[0]
        else:
            SRC, nof = S2, (lambda p: NPOOL)
        if acc == "A0":
            # ⛔ NOT `hash((seed, p))`. Python salts str hashing PER PROCESS, so a seed built from
            #    it is a different seed on every run and "two seeds byte-identical" becomes
            #    unprovable. `e97d14dc` found 33 such lines across 29 files in this project.
            def _sd(p):
                return int(hashlib.md5(f"{seed}|{p}".encode()).hexdigest()[:8], 16)
            r = {p: np.random.default_rng(_sd(p)) for p in pids}
            return SRC, (lambda p, k: tuple(r[p].choice(nof(p), k, replace=False)))
        if acc == "A1":
            f = (lambda p, k: top(REL1[p], k)) if src == "S1" else \
                (lambda p, k: top(REL2[pidx[p]], k))
            return SRC, f
        if acc == "A2":
            f = (lambda p, k: top(PRED1[p], k)) if src == "S1" else \
                (lambda p, k: top(RANK2[pidx[p] % NFIT], k))
            return SRC, f
        if acc == "A3":
            return SRC, (lambda p, k: oracle(SRC, p, k))
        raise ValueError(acc)

    print("\n  E1 - THE 8-CELL TABLE  (rows SOURCE, columns ACCESS; A0 averaged over "
          f"{len(SEEDS)} seeds)")
    print(f"     {'':>4} {'A0 nothing':>12}{'A1 prompt':>12}{'A2 other lbl':>13}{'A3 this lbl':>13}"
          f"   {'Δ_source at A1':>15}")
    TAB, VEC = {}, {}
    for k in KS:
        for src in ("S1", "S2"):
            for acc in ("A0", "A1", "A2", "A3"):
                if acc == "A0":
                    vs = [cell(*make(src, acc, s), k) for s in SEEDS]
                    v = np.mean(vs, axis=0)
                    TAB[(k, src, acc, "sd_seed")] = float(np.std([x.mean() for x in vs]))
                else:
                    v = cell(*make(src, acc), k)
                VEC[(k, src, acc)] = v
                TAB[(k, src, acc)] = float(v.mean())
        for src in ("S1", "S2"):
            row = [TAB[(k, src, a)] for a in ("A0", "A1", "A2", "A3")]
            lab = "own rubric" if src == "S1" else "generic 16"
            print(f"     k={k} {src} {lab:<11}" + "".join(f"{x:>12.6f}" for x in row))
        print(f"          Δ_source(A1) = {TAB[(k,'S1','A1')] - TAB[(k,'S2','A1')]:+.6f}   "
              f"Δ_source(A0) = {TAB[(k,'S1','A0')] - TAB[(k,'S2','A0')]:+.6f}")
    out["table"] = {f"k{k}|{s}|{a}": TAB[(k, s, a)] for k in KS for s in ("S1", "S2")
                    for a in ("A0", "A1", "A2", "A3")}

    over = [f"k{k}|{s}|{a}" for k in KS for s in ("S1", "S2") for a in ("A0", "A1", "A2", "A3")
            if TAB[(k, s, a)] > CEIL_ATT]
    print(f"\n  ⛔ FORCED CHECK  every cell <= {CEIL_ATT}: violations {len(over)}  "
          f"{'PASS' if not over else 'FAIL — INSTRUMENT BROKEN'}")
    if over:
        print("  UNRUNNABLE. Exit 2, never 0.")
        return 2

    # ---------------------------------------------------------------- OBJECT
    print("\n  OBJECT CHECK - this round's own selector must reproduce the committed arms")
    obj, ok = {}, True
    for k in KS:
        tw = np.array([agree(S1[p], p, top(W1[p], k)) for p in pids]).mean()
        arm = RES / f"sat_topw_k{k}.npz"
        if arm.is_file():
            A = load_sat(arm)
            ref = np.array([agree(mat(A, p, len({i for i, _ in A[p]})), p,
                                  range(len({i for i, _ in A[p]}))) for p in pids if p in A]).mean()
            d = abs(tw - ref)
            ok &= d < 2e-3
            obj[f"topw_k{k}"] = {"recomputed": float(tw), "committed": float(ref), "d": float(d)}
            print(f"     topw_k{k:<2} recomputed {tw:.6f} vs committed arm {ref:.6f}  "
                  f"|Δ| {d:.6f}  {'PASS' if d < 2e-3 else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: the selector is not the arm. Exit 2, never 0.")
        return 2
    out["object"] = obj

    # ---------------------------------------------------------------- CONTROLS
    print("\n  CONTROLS")
    rng = np.random.default_rng(843)
    perm = rng.permutation(N)
    plac2 = np.array([agree(S2[p], p, top(REL2[perm[pidx[p]]], 4)) for p in pids]).mean()
    plac1 = np.array([agree(S1[p], p, top(rng.permutation(REL1[p]), 4)) for p in pids]).mean()
    sham2 = np.mean([np.array([agree(S2[p], p, top(np.random.default_rng(900 + s + pidx[p])
                                                   .normal(size=NPOOL), 4)) for p in pids]).mean()
                     for s in range(3)])
    a0_2, a1_2 = TAB[(4, "S2", "A0")], TAB[(4, "S2", "A1")]
    plac_ok = abs(plac2 - a0_2) < 0.01
    sham_ok = sham2 < a1_2
    print(f"     PLACEBO   A1 relevance sent to the WRONG prompt: S2 {plac2:.6f} vs its A0 "
          f"{a0_2:.6f}   PASS: {plac_ok}   (S1 within-prompt shuffle {plac1:.6f})")
    print(f"     SHAM      A1 with RANDOM relevance, matched cardinality: {sham2:.6f} · "
          f"A1's excess over it {a1_2 - sham2:+.6f}   PASS: {sham_ok}")

    # POSITIVE: a planted target built from a KNOWN subset of the generic 16
    pos = {}
    plant = (1, 5, 9, 13)
    for g in (1.0, 0.0):
        r3 = np.random.default_rng(77)
        Hp = {}
        for p in pids:
            y = S2[p][list(plant)].sum(axis=0)
            sg = np.sign(y[[u for u, _ in PR]] - y[[w for _, w in PR]])
            noise = np.sign(r3.normal(size=6))
            Hp[p] = np.array([np.where(r3.random(6) < g, sg, noise)])
        keep = H0
        H0 = Hp
        pos[str(g)] = {"A3": float(cell(*make("S2", "A3"), 4).mean()),
                       "A0": float(np.mean([cell(*make("S2", "A0", s), 4).mean() for s in SEEDS]))}
        H0 = keep
    pos_ok = bool(pos["1.0"]["A3"] > 0.90 and abs(pos["0.0"]["A3"] - pos["0.0"]["A0"]) < 0.08)
    print(f"     POSITIVE  planted target from generic criteria {plant}: "
          f"g=1 A3 {pos['1.0']['A3']:.4f} vs A0 {pos['1.0']['A0']:.4f} · "
          f"g=0 A3 {pos['0.0']['A3']:.4f} vs A0 {pos['0.0']['A0']:.4f}   PASS: {pos_ok}")

    nf = {f"k{k}|{s}": TAB[(k, s, "A0", "sd_seed")] for k in KS for s in ("S1", "S2")}
    print(f"     NOISE     A0 seed spread: " + "  ".join(f"{a} {b:.4f}" for a, b in nf.items()))
    gate = bool(plac_ok and sham_ok and pos_ok and not over and ok)
    print(f"     GATE      {'PASS — the kill may evaluate' if gate else 'FAIL — UNVERIFIED'}")
    out["controls"] = {"placebo_s2": float(plac2), "placebo_s1": float(plac1), "sham_s2": float(sham2),
                       "positive": pos, "noise": nf, "placebo_ok": plac_ok, "sham_ok": sham_ok,
                       "positive_ok": pos_ok, "gate": gate}

    # ---------------------------------------------------------------- E2-E4, paired bootstrap
    idx = rng.integers(0, N, size=(NBOOT, N))
    def ci(v):
        b = v[idx].mean(axis=1)
        return float(v.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
    print("\n  E2/E3/E4 - CONTRASTS, paired on the prompt")
    con, ps = {}, []
    for k in KS:
        for a in ("A0", "A1", "A2", "A3"):
            m, lo, hi = ci(VEC[(k, "S1", a)] - VEC[(k, "S2", a)])
            con[f"dsource|k{k}|{a}"] = {"mean": m, "lo": lo, "hi": hi}
            ps.append(min(1.0, 2 * min((( VEC[(k,"S1",a)] - VEC[(k,"S2",a)])[idx].mean(axis=1) <= 0).mean(),
                                       (( VEC[(k,"S1",a)] - VEC[(k,"S2",a)])[idx].mean(axis=1) >= 0).mean())))
        for s in ("S1", "S2"):
            for j, (x, y) in enumerate((("A0", "A1"), ("A1", "A2"), ("A2", "A3"))):
                m, lo, hi = ci(VEC[(k, s, y)] - VEC[(k, s, x)])
                con[f"daccess|k{k}|{s}|{x}->{y}"] = {"mean": m, "lo": lo, "hi": hi}
    for k in KS:
        g = (VEC[(k, "S1", "A1")] - VEC[(k, "S2", "A1")]) - \
            (VEC[(k, "S1", "A0")] - VEC[(k, "S2", "A0")])
        m, lo, hi = ci(g)
        con[f"GAMMA|k{k}"] = {"mean": m, "lo": lo, "hi": hi}
        print(f"     ⭐ Γ(k={k}) = Δ_source(A1) − Δ_source(A0) = {m:+.6f} [{lo:+.6f}, {hi:+.6f}]   "
              f"{'NON-ADDITIVE — R811 s two effects are not separately interpretable' if lo*hi > 0 else 'additive within resolution'}")
    for k in KS:
        for s in ("S1", "S2"):
            row = " ".join(f"{x}->{y} {con[f'daccess|k{k}|{s}|{x}->{y}']['mean']:+.4f}"
                           for x, y in (("A0", "A1"), ("A1", "A2"), ("A2", "A3")))
            print(f"     Δ_access k={k} {s}: {row}")
    keep = bh(ps)
    print(f"     BH q=0.05 over {len(ps)} Δ_source tests: {int(keep.sum())} survive, "
          f"{int((~keep).sum())} do not (printed, not hidden)")
    out["contrasts"] = con

    # ---------------------------------------------------------------- E5 + the kill
    print("\n  E5 / THE KILL — each world's predicate evaluated INDEPENDENTLY")
    k = 4
    mono = all(TAB[(k, s, b)] >= TAB[(k, s, a)] - 1e-12
               for s in ("S1", "S2") for a, b in (("A0", "A1"), ("A1", "A2"), ("A2", "A3")))
    fl = max(nf.values())
    w_access = bool(mono and max(abs(con[f"dsource|k{k}|{a}"]["mean"]) for a in
                                 ("A0", "A1", "A2", "A3")) <= fl)
    w_source = bool(all(con[f"dsource|k{k}|{a}"]["lo"] > 0 for a in ("A0", "A1", "A2", "A3")))
    w_context = bool(TAB[(k, "S2", "A1")] >= TAB[(k, "S1", "A3")] - fl)
    w_joint = bool(con[f"GAMMA|k{k}"]["lo"] * con[f"GAMMA|k{k}"]["hi"] > 0)
    if not gate:
        verdict = "UNVERIFIED"
    else:
        verdict = {"W-JOINT": w_joint, "W-ACCESS": w_access, "W-SOURCE": w_source,
                   "W-CONTEXT": w_context}
    print(f"     monotone in ACCESS on both rows: {mono}")
    print(f"     W-JOINT   Γ resolvably non-zero .................. {w_joint}")
    print(f"     W-ACCESS  ordered by access, not by source ....... {w_access}")
    print(f"     W-SOURCE  own rubric dominates at every access ... {w_source}")
    print(f"     W-CONTEXT generic+context reaches own+labels ..... {w_context}   "
          f"(S2×A1 {TAB[(k,'S2','A1')]:.6f} vs S1×A3 {TAB[(k,'S1','A3')]:.6f})")
    out["verdict"] = verdict
    out["worlds"] = {"monotone": mono, "W-JOINT": w_joint, "W-ACCESS": w_access,
                     "W-SOURCE": w_source, "W-CONTEXT": w_context}

    (HERE / "results").mkdir(exist_ok=True)
    ap = HERE / "results" / "source_by_access.json"
    ap.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    print(f"\n  ARTIFACT {ap.relative_to(ROOT)}  md5 {hashlib.md5(ap.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
