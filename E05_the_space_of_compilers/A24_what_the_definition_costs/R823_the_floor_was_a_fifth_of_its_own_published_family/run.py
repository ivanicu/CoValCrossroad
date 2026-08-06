#!/usr/bin/env python3
"""R823 · ④'s floor was the max over a fifth of its own published family.

DEFINITION.md:118 names ④'s scope as R435's 30-rule family and says "extending it is how this clause
gets refuted". R803 built SIX rules, all six members of that thirty, and R821 retained ④ on
`0 of 58` against that subset's max. See PREREGISTRATION.txt for estimands, D1-D4, worlds, kill.
"""
import hashlib
import itertools
import json
import pathlib
import re
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                    # noqa: E402
from assurance.null_is_informative import assert_null_is_informative   # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R435J = ARC / "R435_is_a_sufficiency_clause_even_statable/results/r435_bar_stability.json"
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
FLOOR_COMMITTED = 0.4557
# R803's six, named in its own artifact as {characters, tokens, position} x {longer, shorter}
SIX = ["max_len_chars", "min_len_chars", "max_len_words", "min_len_words", "last", "first"]


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    raise TypeError(type(o))


def feats(t):
    """the 14 base features R435's family is built from, per response text."""
    w = t.split()
    lw = [len(x) for x in w] or [0]
    return {
        "len_chars": len(t), "len_words": len(w), "distinct_words": len(set(x.lower() for x in w)),
        "ttr": (len(set(x.lower() for x in w)) / len(w)) if w else 0.0,
        "sentences": len(re.findall(r"[.!?]+", t)), "questions": t.count("?"),
        "newlines": t.count("\n"), "bullets": len(re.findall(r"(?m)^\s*[-*•]", t)),
        "digits": sum(c.isdigit() for c in t), "commas": t.count(","),
        "mean_word_len": float(np.mean(lw)), "colons": t.count(":"),
        "uppercase": sum(c.isupper() for c in t), "parens": t.count("("),
    }


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
    fam30 = json.loads(R435J.read_text())["family"]
    assert len(fam30) == 30, len(fam30)
    assert all(s in fam30 for s in SIX), [s for s in SIX if s not in fam30]

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
    print(f"  POPULATION  {N} prompts · R435's published family: {len(fam30)} rules · "
          f"R803's subset: {len(SIX)}   all six in the thirty: True")

    # ---- score matrix for every rule in the family, on THIS population -------------------------
    F = {p: [feats(t) for t in text[p]] for p in pids}
    def rule_matrix(name):
        if name == "first":
            return np.tile(np.array([4.0, 3.0, 2.0, 1.0]), (N, 1))
        if name == "last":
            return np.tile(np.array([1.0, 2.0, 3.0, 4.0]), (N, 1))
        sgn, key = (1.0, name[4:]) if name.startswith("max_") else (-1.0, name[4:])
        return sgn * np.array([[F[p][i][key] for i in range(4)] for p in pids], float)

    def per_prompt(Smat):
        v = np.zeros(N)
        for i, p in enumerate(pids):
            s = np.sign(Smat[i][[u for u, _ in PR]] - Smat[i][[w for _, w in PR]])
            v[i] = float((H[p] == s).mean())
        return v

    RV = {r: per_prompt(rule_matrix(r)) for r in fam30}
    A = {r: float(RV[r].mean()) for r in fam30}

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK - the SIX must reproduce R803's committed floor on this population")
    six_best = max(SIX, key=lambda r: A[r])
    floor6 = A[six_best]
    ok = abs(floor6 - FLOOR_COMMITTED) < 5e-5
    print(f"     best of the six: `{six_best}` {floor6:.6f} vs R803's committed "
          f"{FLOOR_COMMITTED}   {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: 30 new feature implementations are unvalidated. Exit 2, never 0.")
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
    print(f"     arms scoreable on this population: {len(A2)}")
    out["object"] = {"n_prompts": N, "n_arms": len(A2), "floor6": floor6, "six_best": six_best,
                     "reproduced": ok}

    # ================= E1 · the full family ======================================================
    print("\n  E1 - THE FULL 30-RULE FAMILY ON R803's POPULATION")
    print("     ⛔ D1 (a DERIVATION, never evidence): max over a superset is monotone")
    print("        non-decreasing. THE RISE IS FORCED. What is measurable is its SIZE, whether it")
    print("        CROSSES an arm, and how much of it is winner's curse (the sham).")
    order = sorted(fam30, key=lambda r: -A[r])
    best30 = order[0]
    floor30 = A[best30]
    for r in order[:8]:
        tag = "  <- in R803's six" if r in SIX else ""
        print(f"     {r:<22} {A[r]:.6f}{tag}")
    print(f"     ...   worst `{order[-1]}` {A[order[-1]]:.6f}")
    print(f"     ⭐ floor over 30 rules `{best30}` {floor30:.6f}   over R803's 6 `{six_best}` "
          f"{floor6:.6f}   rise {floor30 - floor6:+.6f}")
    fl6_v, fl30_v = RV[six_best], RV[best30]
    out["e1"] = {"accs": A, "best30": best30, "floor30": floor30, "floor6": floor6,
                 "rise": floor30 - floor6, "rank": order,
                 "six_are_subset": bool(all(s in fam30 for s in SIX))}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    rng = np.random.default_rng(20250806)
    idx = rng.integers(0, N, size=(NBOOT, N))

    def ci(v):
        d = v[idx].mean(axis=1)
        return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5)), \
            max(min(2.0 * min((d <= 0).mean(), (d >= 0).mean()), 1.0), 1.0 / (NBOOT + 1))

    plac = float((fl30_v - fl30_v).mean())
    print(f"     PLACEBO   the 30-rule floor against itself: {plac:.1e}   "
          f"{'PASS - exactly 0' if plac == 0.0 else 'FAIL'}")

    pos = {}
    for d in (0.10, 0.05, 0.01, 0.0):
        pv = np.clip(fl30_v - d, 0.0, 1.0)
        m = float((pv - fl30_v).mean())
        lo, hi, _ = ci(pv - fl30_v)
        pos[str(d)] = {"margin": m, "lo": lo, "hi": hi, "removed": bool(hi < 0)}
        print(f"     POSITIVE  δ={d:<5} margin {m:+.4f} [{lo:+.4f}, {hi:+.4f}]   "
              f"④ removes it: {hi < 0}")
    pos_ok = all(pos[str(d)]["removed"] for d in (0.10, 0.05, 0.01)) and not pos["0.0"]["removed"]
    print(f"               ladder fires at δ>0 and NOT at δ=0: {pos_ok}")

    real_margin = float(np.mean([(A2[a] - fl30_v).mean() for a in A2]))
    nl = np.array([float(fl30_v[rng.integers(0, N, size=N)].mean() - fl30_v.mean())
                   for _ in range(200)])
    try:
        info = assert_null_is_informative(nl, real_margin, name="R823 negative control")
        neg_ok = bool(abs(nl.mean()) < 2 * nl.std() and real_margin > nl.max())
        print(f"     NEGATIVE  synthetic arm resampled from the floor's own distribution: "
              f"{nl.mean():+.5f} ± {nl.std():.5f}   real {real_margin:+.5f}   PASS: {neg_ok}")
    except AssertionError as e:
        print(f"     NEGATIVE  ⛔ {e}")
        neg_ok = False
        info = {"spread": 0.0}

    # ⭐ SHAM: how much does m=6 -> m=30 raise a MAX, on scorers with no signal at all?
    # ⛔ THE FIRST VERSION SORTED THE RANDOM SCORERS DESCENDING AND TOOK THE TOP SIX, so
    #    `sham6 == sham30` BY CONSTRUCTION and the rise was 0.000000 necessarily. §4's opening row
    #    — a check that cannot fail — built inside the round whose subject is selection. A
    #    six-subset must be drawn at RANDOM, which is what R803's choice has to be compared against.
    sham_acc = np.array([float(per_prompt(rng.normal(size=(N, 4))).mean()) for _ in range(30)])
    sham30 = float(sham_acc.max())
    sham6_draws = np.array([float(sham_acc[rng.choice(30, len(SIX), replace=False)].max())
                            for _ in range(2000)])
    sham6 = float(sham6_draws.mean())
    sham_rise = sham30 - sham6
    print(f"     SHAM      30 RANDOM per-response scorers: max over 30 {sham30:.6f}; over a "
          f"RANDOM 6 {sham6:.6f} ± {sham6_draws.std():.6f}")
    print(f"               so pure selection buys {sham_rise:+.6f} going 6 -> 30 on noise")
    # and the same question asked of the REAL family: what was R803's choice of six worth?
    real6_draws = np.array([float(max(A[r] for r in np.array(fam30)[rng.choice(30, len(SIX),
                            replace=False)])) for _ in range(2000)])
    p_contains = float(np.mean(real6_draws >= floor30 - 1e-12))
    print(f"     ⭐ R803's SIX vs a RANDOM six of the same thirty: random-6 max "
          f"{real6_draws.mean():.6f} ± {real6_draws.std():.6f}, R803's {floor6:.6f}, "
          f"full-30 {floor30:.6f}")
    print(f"        a random six contains the family argmax {p_contains:.3f} of the time "
          f"(DERIVED: 6/30 = 0.200) — R803's six did, and by design: its axes are "
          f"{{chars, words, position}} x {{longer, shorter}}, and length is the known bias")

    nf = {}
    for tag, v in (("6", fl6_v), ("30", fl30_v)):
        hs = [float(v[rng.permutation(N)[: N // 2]].mean()) for _ in range(20)]
        nf[tag] = float(np.std(hs))
        print(f"     NOISE FLOOR  m={tag:<3} 20 half-splits of the floor: sd {nf[tag]:.4f}")

    gate = bool(plac == 0.0 and pos_ok and neg_ok)
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["sham_detail"] = {"random6_real_mean": float(real6_draws.mean()),
                          "random6_real_sd": float(real6_draws.std()),
                          "p_random6_contains_argmax": p_contains,
                          "sham6_sd": float(sham6_draws.std())}
    out["controls"] = {"placebo": plac, "positive": pos, "positive_ok": pos_ok,
                       "negative_mean": float(nl.mean()), "negative_sd": float(nl.std()),
                       "negative_real": real_margin, "negative_ok": neg_ok,
                       "sham6": sham6, "sham30": sham30, "sham_rise": sham_rise,
                       "excess_over_sham": (floor30 - floor6) - sham_rise,
                       "noise_floor": nf, "gate": gate}

    # ================= E2 · does ④ bind at home now? =============================================
    print("\n  E2 - ④'s EXCLUSION COUNT AT THE 30-RULE FLOOR")
    rows, ps = [], []
    for a in sorted(A2, key=lambda a: A2[a].mean()):
        m = float((A2[a] - fl30_v).mean())
        lo, hi, p = ci(A2[a] - fl30_v)
        v = "EXCLUDED" if hi < 0 else ("PASSES ④" if lo > 0 else "UNVERIFIED")
        m6 = float((A2[a] - fl6_v).mean())
        _, hi6, _ = ci(A2[a] - fl6_v)
        v6 = "EXCLUDED" if hi6 < 0 else "not excluded"
        rows.append({"arm": a, "a2": float(A2[a].mean()), "m30": m, "lo": lo, "hi": hi, "p": p,
                     "verdict30": v, "m6": m6, "verdict6": v6})
        ps.append(p)
    ex30 = [r for r in rows if r["verdict30"] == "EXCLUDED"]
    ex6 = [r for r in rows if r["verdict6"] == "EXCLUDED"]
    un30 = [r for r in rows if r["verdict30"] == "UNVERIFIED"]
    for r in rows[:6]:
        print(f"     {r['arm']:<22} A2 {r['a2']:.4f}   vs 30-floor {r['m30']:+.4f} "
              f"[{r['lo']:+.4f}, {r['hi']:+.4f}] {r['verdict30']:<10}   vs 6-floor "
              f"{r['m6']:+.4f} {r['verdict6']}")
    print(f"     ⭐ ④ excludes {len(ex30)} of {len(rows)} at the 30-rule floor   "
          f"{len(ex6)} of {len(rows)} at R803's 6-rule floor   UNVERIFIED {len(un30)}")
    if ex30:
        print(f"        newly excluded: {[r['arm'] for r in ex30]}")
    keep = bh(ps)
    print(f"     BH q=0.05 over {len(ps)} tests: {int(keep.sum())} survive, {int((~keep).sum())} "
          f"do not (reported, not hidden)")
    out["e2"] = {"rows": rows, "excluded30": len(ex30), "excluded6": len(ex6),
                 "unverified30": len(un30), "bh_survive": int(keep.sum())}

    # ================= E3 · the HELD-OUT floor ===================================================
    print("\n  E3 - THE HELD-OUT FLOOR  (the in-sample max over a bigger class is optimistic)")
    ho = {}
    for tag, fam in (("6", SIX), ("30", fam30)):
        vals = []
        for s in range(20):
            r2 = np.random.default_rng(1000 + s)
            pm = r2.permutation(N)
            fit, ev = pm[: N // 2], pm[N // 2:]
            b = max(fam, key=lambda r: RV[r][fit].mean())
            vals.append(float(RV[b][ev].mean()))
        ho[tag] = {"mean": float(np.mean(vals)), "sd": float(np.std(vals))}
        print(f"     m={tag:<3} held-out floor {np.mean(vals):.6f} ± {np.std(vals):.6f}   "
              f"in-sample {(floor6 if tag == '6' else floor30):.6f}   optimism "
              f"{(floor6 if tag == '6' else floor30) - np.mean(vals):+.6f}")
    print(f"     ⭐ held-out rise 6->30: {ho['30']['mean'] - ho['6']['mean']:+.6f}   "
          f"in-sample rise {floor30 - floor6:+.6f}")
    out["e3"] = ho

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    rise = floor30 - floor6
    if not gate:
        world = "UNVERIFIED"
    elif len(ex30) >= 1 and rise > sham_rise:
        world = "B"
    elif rise <= nf["6"] and len(ex30) == 0:
        world = "A"
    else:
        world = "C"
    print(f"     gate {gate} · rise {rise:+.6f} vs sham rise {sham_rise:+.6f} · noise floor(6) "
          f"{nf['6']:.4f} · ④ excludes {len(ex30)} of {len(rows)}")
    print(f"     ->  WORLD {world}")
    out["world"] = world
    out["rise"] = rise

    HERE.joinpath("results").mkdir(exist_ok=True)
    ap = HERE / "results" / "full_family_floor.json"
    ap.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    print(f"\n  ARTIFACT {ap.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(ap.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
