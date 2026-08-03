#!/usr/bin/env python3
"""
corebench/unit_robustness.py -- does the core ranking survive a change of RESAMPLING UNIT?

The G-family round found the same comparison separable when resampled by annotator and null
when resampled by prompt, and named the difference as an estimand choice rather than a
tiebreak. That ambiguity is not local to G: EVERY A-family comparison today was
prompt-weighted and prompt-resampled BY DEFAULT, and nobody chose that. A ranking that holds
only under an unexamined default is a property of the default.

ESTIMAND        the arm ordering and the count of separating pairs on A2, computed two ways:
                PROMPT-weighted, resampled over 968 prompts (the day's default), and
                ANNOTATOR-weighted, resampled over the annotators who judged (the unit the
                subgroup round used). Named before the method.
WORLDS          A the ordering and the survivor set AGREE -> the ranking is unit-robust and
                  the day's default was harmless
                B they DISAGREE -> the ranking is conditional on an unexamined choice, and
                  every comparison today inherits that condition
KILL            pre-registered: any adjacent pair inverting with BOTH units separating it,
                or the top-ranked competent arm changing -> world B.
POSITIVE CTRL   under both units the leaky arms rank top and the incompetent arms bottom.
PLACEBO         an arm against itself: exactly 0 under both units.
"""
from __future__ import annotations
import collections, itertools, json, hashlib, pathlib, sys
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, yvec, cls
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
NBOOT, Q = 1000, 0.05
ARMS = ["coval_core", "topw_k4", "gen", "topabs_k4", "topwvar_k4", "topvar_k4",
        "full", "random_k4_s0", "gen_sham", "oracle_k4_fit1", "indep_k4_fit1"]
INCOMPETENT, LEAKY = {"random_k4_s0", "gen_sham"}, {"oracle_k4_fit1", "indep_k4_fit1"}


def parse_ranking(s):
    sc = {}
    for lvl, grp in enumerate(s.split(">")):
        for tok in grp.split("="):
            tok = tok.strip()
            if tok in L: sc[tok] = -lvl
    return [sc[c] for c in L] if len(sc) == 4 else None


def load_judgements():
    out = collections.defaultdict(list)
    for line in open(ROOT/"data"/"comparisons.jsonl", encoding="utf-8"):
        if not line.strip(): continue
        rec = json.loads(line); pid = rec["prompt_id"]
        for asm in rec.get("metadata", {}).get("assessments", []):
            for e in (asm.get("ranking_blocks") or {}).get("world") or []:
                y = parse_ranking(e["ranking"]) if e.get("ranking") else None
                if y: out[pid].append((y, asm.get("annotator_id")))
    return out


def a2_cells(sat, J):
    """-> list of (pid, annotator, a2). One row per judgement, so either unit can group it."""
    rows = []
    for p in sat:
        if p not in J: continue
        c = cls(yvec(sat[p], sorted({i for i, _ in sat[p]})))
        for y, aid in J[p]:
            h = cls(np.array(y, float))
            rows.append((p, aid, float(np.mean([c[q] == h[q] for q in range(6)]))))
    return rows


def compare(rowsA, rowsB, unit, seed=0):
    ka = {(p, a): v for p, a, v in rowsA}; kb = {(p, a): v for p, a, v in rowsB}
    keys = sorted(set(ka) & set(kb))
    g = collections.defaultdict(list)
    for k in keys: g[k[0] if unit == "prompt" else k[1]].append(ka[k] - kb[k])
    units = sorted(g); mu = np.array([np.mean(g[u]) for u in units])
    rng = np.random.default_rng(seed)
    b = np.array([mu[rng.integers(0, len(mu), len(mu))].mean() for _ in range(NBOOT)])
    return float(mu.mean()), 2 * min((b <= 0).mean(), (b >= 0).mean()), len(units)


if __name__ == "__main__":
    J = load_judgements()
    R = {a: a2_cells(load_sat(ROOT/"corebench"/"results"/f"sat_{a}.npz"), J)
         for a in ARMS if (ROOT/"corebench"/"results"/f"sat_{a}.npz").exists()}
    arms = list(R)
    comp = [a for a in arms if a not in INCOMPETENT and a not in LEAKY]
    print(f"\n  UNIT ROBUSTNESS -- A2, {len(arms)} arms, {len(list(itertools.combinations(arms,2)))} pairs\n")
    out = {}
    for unit in ("prompt", "annotator"):
        absv = {a: float(np.mean([v for _p, _q, v in R[a]])) for a in arms}
        res = []
        for x, y in itertools.combinations(arms, 2):
            m, p_, n = compare(R[x], R[y], unit)
            res.append([x, y, m, p_])
        C = len(res); o = sorted(range(C), key=lambda i: res[i][3]); surv = set()
        for rank, i in enumerate(o, 1):
            if res[i][3] <= Q*rank/C: surv = set(o[:rank])
        order = sorted(arms, key=lambda z: -absv[z])
        cc = [i for i, r in enumerate(res) if r[0] in comp and r[1] in comp]
        ok = set(order[:2]) == (LEAKY & set(arms))
        out[unit] = (order, {frozenset((res[i][0], res[i][1])) for i in surv}, len(surv), C,
                     len(surv & set(cc)), len(cc), ok, n)
        print(f"    [{'PASS' if ok else 'FAIL'}] {unit:<10} n_units={n:<5} surviving "
              f"{len(surv):>2}/{C}   competent {len(surv & set(cc)):>2}/{len(cc)}")
        print(f"       {' > '.join(a for a in order if a in comp)}")

    op, oa = [a for a in out["prompt"][0] if a in comp], [a for a in out["annotator"][0] if a in comp]
    inv = []
    for i in range(len(op)-1):
        x, y = op[i], op[i+1]
        if oa.index(x) > oa.index(y):
            both = frozenset((x, y)) in out["prompt"][1] and frozenset((x, y)) in out["annotator"][1]
            inv.append((x, y, "BOTH separate" if both else "at least one is a tie"))
    hard = [i for i in inv if i[2] == "BOTH separate"]
    print(f"\n    top competent arm    prompt: {op[0]}   annotator: {oa[0]}")
    print(f"    adjacent inversions  {len(inv)} {inv if inv else ''}")
    print(f"    of those, BOTH units separate the pair: {len(hard)}")
    v = ("WORLD B -- the ranking is conditional on the resampling unit" if hard or op[0] != oa[0]
         else "WORLD A -- the ordering is UNIT-ROBUST; the day's prompt-default was harmless")
    print(f"\n    VERDICT: {v}\n")
    (ROOT/"corebench"/"results"/"unit_robustness.json").write_text(json.dumps(
        {"source_sha256_16": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "prompt_order": op, "annotator_order": oa, "inversions": inv, "verdict": v,
         "surviving": {u: [out[u][2], out[u][3], out[u][4], out[u][5]] for u in out}},
        indent=2, sort_keys=True))
