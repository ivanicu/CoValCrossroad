#!/usr/bin/env python3
"""
corebench/learned_core.py -- the first DEPLOYABLE candidate: a rule fitted on some prompts
and applied to prompts it has never seen.

WHY THIS AND NOT indep_HO. indep_HO reached the combination search, but it is fitted on the
odd annotators OF THE SAME PROMPT -- it transfers to nothing, because a new prompt has no
annotations to fit on. So it bounded the information available; it is not a rule. The only
rules that have actually been deployable so far are topw_k4 and its variants, and none of
them is fitted at all.

DEPLOYMENT CONSTRAINT, which is what makes the feature list short: a new prompt arrives with
a rubric and four responses and NO human rankings. So a feature is admissible only if it can
be computed from the rubric and the responses. Importance scores: yes, they are rubric-side.
Satisfaction of a criterion on each response: yes, it is judged. Anything derived from the
human target: NO, and that is the line indep_HO crosses.

ESTIMAND        exact-class agreement on HELD-OUT PROMPTS of a top-k rule whose per-criterion
                score is a ridge fit over deployable features, against topw_k4 on the same
                held-out prompts. Named before the method.
IDENTIFICATION  identified; the split is by prompt, so nothing about a test prompt enters
                the fit.
SCOPE           population : the held-out half of 968 prompts
                instrument : ridge on 8 deployable features -> top-4 selection
                baseline   : topw_k4, restricted to the same held-out prompts
                regime     : k=4, exact-class match
WORLDS          A the learned rule beats topw_k4 out of sample -> a deployable gain exists
                B it does not -> importance alone is the best deployable rule found, and
                  the benchmark's answer is that the trivial rule is the answer
KILL            pre-registered: paired CI on (learned - topw) over held-out prompts. If it
                includes zero, world B, and the round says so rather than reaching for a
                better feature set.
POSITIVE CTRL   a LEAKY variant that includes the target-derived usefulness as a feature
                must beat topw_k4 clearly. If even the leaky arm cannot, the pipeline is
                broken and neither arm is readable.
NEGATIVE CTRL   shuffle the fitted coefficients across features; the rule must collapse
                toward random_k4.
PLACEBO         fit on the test half and evaluate on the test half -> must beat the honest
                split, and the size of that difference IS the overfitting being avoided.
SEEDS           3 splits.
"""
from __future__ import annotations
import collections, itertools, json, hashlib, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
K, SEEDS = 4, [0, 1, 2]
FULL_NPZ = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
                   "/R04_rebuild_satisfaction/results/a04_full.npz")


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def parse_ranking(s):
    sc = {}
    for lvl, grp in enumerate(s.split(">")):
        for tok in grp.split("="):
            tok = tok.strip()
            if tok in L:
                sc[tok] = -lvl
    return [sc[c] for c in L] if len(sc) == 4 else None


def feats(items, sat_p, ok):
    """8 DEPLOYABLE features. Every one computable from rubric + responses alone."""
    F = {}
    for i in ok:
        sc = [s["score"] for s in items[i].get("scores") or []] or [0.0]
        s4 = np.array([sat_p[(i, x)] for x in L], float)
        F[i] = np.array([np.mean(sc), np.std(sc), len(sc), abs(np.mean(sc)),
                         np.var(s4), np.mean(s4), s4.max() - s4.min(),
                         len(items[i]["criterion"].split())], float)
    return F


def main():
    from covalx.judge import load_join
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    rub = {p: r for p, _pr, r in joined}
    d = np.load(FULL_NPZ, allow_pickle=True)
    sat = collections.defaultdict(dict)
    for kk, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(kk).split("|")
        sat[pid][(int(i), ltr)] = float(v)

    tgt = {}
    for line in open(ROOT / "data" / "comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        ys = [parse_ranking(e["ranking"])
              for asm in rec.get("metadata", {}).get("assessments", [])
              for e in (asm.get("ranking_blocks") or {}).get("world") or [] if e.get("ranking")]
        ys = [y for y in ys if y]
        if ys:
            tgt[rec["prompt_id"]] = collections.Counter(
                cls(np.array(y, float)) for y in ys).most_common(1)[0][0]

    P = []
    for pid, r in rub.items():
        items = r.get("coval_full") or []
        if pid not in sat or pid not in tgt or not items:
            continue
        ok = [i for i in range(len(items)) if all(sat[pid].get((i, x)) is not None for x in L)]
        if len(ok) < K:
            continue
        P.append((pid, items, ok))

    def usefulness(pid, i):
        y = np.array([sat[pid][(i, x)] for x in L])
        t = tgt[pid]
        return sum(cls(y)[q] == t[q] for q in range(6)) / 6.0

    def fit(train, leaky=False):
        X, Y = [], []
        for pid, items, ok in train:
            F = feats(items, sat[pid], ok)
            for i in ok:
                f = F[i]
                X.append(np.append(f, usefulness(pid, i)) if leaky else f)
                Y.append(usefulness(pid, i))
        X = np.array(X); Y = np.array(Y)
        X = (X - X.mean(0)) / (X.std(0) + 1e-9)
        return np.linalg.solve(X.T @ X + 1.0 * np.eye(X.shape[1]), X.T @ Y), X.mean(0), X.std(0)

    def apply(test, w, mu, sd, leaky=False, shuffle_w=None):
        hits = {}
        for pid, items, ok in test:
            F = feats(items, sat[pid], ok)
            ww = shuffle_w if shuffle_w is not None else w
            s = {}
            for i in ok:
                f = np.append(F[i], usefulness(pid, i)) if leaky else F[i]
                s[i] = float(((f - mu) / (sd + 1e-9)) @ ww)
            sel = sorted(ok, key=lambda i: -s[i])[:K]
            y = np.array([sum(sat[pid][(i, x)] for i in sel) for x in L])
            hits[pid] = float(cls(y) == tgt[pid])
        return hits

    def topw(test):
        hits = {}
        for pid, items, ok in test:
            w_ = {i: float(np.mean([s["score"] for s in items[i].get("scores") or []] or [0]))
                  for i in ok}
            sel = sorted(ok, key=lambda i: -w_[i])[:K]
            y = np.array([sum(sat[pid][(i, x)] for i in sel) for x in L])
            hits[pid] = float(cls(y) == tgt[pid])
        return hits

    print(f"\n  learned deployable core -- {len(P)} prompts, prompt-level split, {len(SEEDS)} seeds\n")
    rows = collections.defaultdict(list)
    for s in SEEDS:
        rng = np.random.default_rng(s)
        idx = rng.permutation(len(P)); half = len(P) // 2
        train = [P[i] for i in idx[:half]]; test = [P[i] for i in idx[half:]]
        w, mu, sd = fit(train)
        h_learn = apply(test, w, mu, sd)
        h_topw = topw(test)
        wl, mul, sdl = fit(train, leaky=True)
        h_leak = apply(test, wl, mul, sdl, leaky=True)
        rs = np.random.default_rng(1000 + s); wsh = w.copy(); rs.shuffle(wsh)
        h_shuf = apply(test, w, mu, sd, shuffle_w=wsh)
        w2, mu2, sd2 = fit(test)
        h_over = apply(test, w2, mu2, sd2)
        pids = sorted(h_learn)
        for name, h in (("learned", h_learn), ("topw", h_topw), ("LEAKY", h_leak),
                        ("shuffled_w", h_shuf), ("PLACEBO_fit_on_test", h_over)):
            rows[name].append(float(np.mean([h[p] for p in pids])))
        rows["_d_learn_topw"].append(np.array([h_learn[p] - h_topw[p] for p in pids]))
        rows["_d_leak_topw"].append(np.array([h_leak[p] - h_topw[p] for p in pids]))

    for name in ("learned", "topw", "LEAKY", "shuffled_w", "PLACEBO_fit_on_test"):
        v = rows[name]
        print(f"    {name:<22}{np.mean(v):>9.4f}   seeds {['%.4f' % x for x in v]}")

    def paired(dd):
        d_ = np.concatenate(dd); rb = np.random.default_rng(5)
        b = np.array([d_[rb.integers(0, len(d_), len(d_))].mean() for _ in range(2000)])
        return d_.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5)

    m, lo, hi = paired(rows["_d_learn_topw"])
    lm, llo, lhi = paired(rows["_d_leak_topw"])
    print(f"\n    [{'PASS' if llo > 0 else 'FAIL'}] POSITIVE: the LEAKY arm beats topw "
          f"{lm:+.4f} [{llo:+.4f}, {lhi:+.4f}]")
    print(f"    [{'PASS' if np.mean(rows['shuffled_w']) < np.mean(rows['learned']) else 'FAIL'}]"
          f" NEGATIVE: shuffling the coefficients degrades "
          f"{np.mean(rows['learned']):.4f} -> {np.mean(rows['shuffled_w']):.4f}")
    print(f"    [{'PASS' if np.mean(rows['PLACEBO_fit_on_test']) >= np.mean(rows['learned']) else 'FAIL'}]"
          f" PLACEBO: fitting on test beats the honest split "
          f"{np.mean(rows['PLACEBO_fit_on_test']):.4f} vs {np.mean(rows['learned']):.4f}"
          f"  (that difference IS the overfitting avoided)")
    print(f"\n    learned - topw = {m:+.4f}   95% CI [{lo:+.4f}, {hi:+.4f}]")
    print(f"\n    VERDICT: {'WORLD A -- a deployable gain exists' if lo > 0 else 'WORLD B -- NOT separable; importance alone remains the best deployable rule found'}\n")
    (pathlib.Path(__file__).parent / "results" / "learned.json").write_text(json.dumps(
        {"source_sha256_16": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "means": {k: [float(x) for x in v] for k, v in rows.items() if not k.startswith("_")},
         "d_learn_topw": [float(m), float(lo), float(hi)],
         "d_leak_topw": [float(lm), float(llo), float(lhi)]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
