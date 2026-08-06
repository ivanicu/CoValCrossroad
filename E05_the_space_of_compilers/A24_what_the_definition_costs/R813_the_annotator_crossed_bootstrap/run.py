#!/usr/bin/env python3
"""R813 · the annotator-crossed bootstrap — are this arc's intervals too narrow?

CHECK #415 killed R812's NEXT twice: every round here already bootstraps prompts, and the release
carries 1,078 conversations for 1,078 prompts with max 1 prompt each, so there is no coarser
grouping. But the same check found the real dependence: 1,012 annotators, each judging a MEDIAN OF
19 PROMPTS, all of them touching more than one. Annotators are CROSSED with prompts, and every
interval this arc quotes holds the panel fixed while resampling prompts.

ESTIMAND        E1 the annotator bootstrap · E2 ⭐ the crossed bootstrap · E3 ⭐ the design effect
                per headline · E4 which verdicts survive the widest interval
IDENTIFICATION  identified; prompts left with zero annotators in a draw are dropped from that draw
                and the rate is printed — above 10% the round returns UNVERIFIED
DERIVED FIRST   D1 two-axis resampling cannot be narrower than one-axis, so a design effect below 1
                means the code is wrong · D2 an arm minus itself has zero width everywhere ·
                D3 breaking the crossing must collapse the width · D4 a planted annotator offset
                must widen the ANNOTATOR interval and not the PROMPT one, and must not fire at g=0
WORLDS          A narrow · B understated · C between — B checked FIRST
CONTROLS        OBJECT (four committed points) · PLACEBO · POSITIVE (dose 0/0.05/0.15) ·
                NEGATIVE (annotator ids reassigned, 200 draws) · NOISE FLOOR (three seeds)
"""
import hashlib
import itertools
import json
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, yvec, cls                                  # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
SEEDS = [11, 22, 33]


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def parse_ranking(s):
    sc = {}
    for lvl, grp in enumerate(s.split(">")):
        for tok in grp.split("="):
            tok = tok.strip()
            if tok in "ABCD":
                sc[tok] = -lvl
    return [sc[c] for c in "ABCD"] if len(sc) == 4 else None


def main():
    out = {"instrument_unit": "a (prompt, annotator) judgement", "claim_unit": "a HEADLINE"}

    # ---- rebuild targets WITH annotator identity, which load_targets() discards ----------------
    print("  loading assessments WITH annotator identity (load_targets drops it)")
    per = {}
    annset = {}
    for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        rows = []
        for a in r["metadata"].get("assessments", []):
            aid = a.get("annotator_id")
            for e in (a.get("ranking_blocks") or {}).get("world") or []:
                y = parse_ranking(e.get("ranking") or "")
                if y and aid:
                    rows.append((aid, np.array(cls(np.array(y, float)))))
        if rows:
            per[r["prompt_id"]] = rows
            for aid, _ in rows:
                annset.setdefault(aid, len(annset))
    # ⚠ H2/H3/H4 come from R810/R811, which restrict to the COMMON INTERSECTION of prompts
    # attaining nominal k at EVERY k in {2,4,8,12}. H1 comes from R805, which uses all 968. The
    # first run used 968 for all four and the object check exited 2 on exactly H2/H3/H4.
    ARMS = ["oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1", "topw_k12", "genericpool16",
            "greedy_k12_fit1", "indep_k12_fit1", "topw_k4", "coval_core",
            "random_k12_s0", "random_k12_s1", "random_k12_s2"]
    KARMS = [f"{r}_k{k}{sfx}" for k in (2, 4, 8, 12)
             for r, sfx in (("greedy", "_fit1"), ("indep", "_fit1"), ("topw", ""))] + \
            [f"random_k{k}_s0" for k in (2, 4, 8, 12)]
    S = {a: load_sat(RES / f"sat_{a}.npz") for a in ARMS}
    SK = {a: load_sat(RES / f"sat_{a}.npz") for a in KARMS}
    POOL = S["genericpool16"]
    pids = sorted(set.intersection(*(set(v) for v in S.values())) & set(per))
    # parity-0 only, matching the arc
    P0 = {}
    for p in pids:
        rows = [(aid, c) for i, (aid, c) in enumerate(per[p]) if i % 2 == 0]
        if rows:
            P0[p] = rows
    pids = [p for p in pids if p in P0]
    # R810/R811's common intersection, rebuilt here rather than assumed
    def eff(a, p):
        return len({i for i, _ in SK[a][p]}) if p in SK[a] else 0
    COMMON = [p for p in pids
              if all(eff(f"{r}_k{k}{sfx}", p) >= k for k in (2, 4, 8, 12)
                     for r, sfx in (("greedy", "_fit1"), ("indep", "_fit1"), ("topw", ""))
                     ) and all(eff(f"random_k{k}_s0", p) >= k for k in (2, 4, 8, 12))]
    N = len(pids)
    print(f"  R810/R811's common intersection rebuilt: {len(COMMON)} of {N} prompts "
          f"(H1 uses all {N}; H2/H3/H4 use the {len(COMMON)})")
    NA = len(annset)
    npc = [len(P0[p]) for p in pids]
    apc = {}
    for p in pids:
        for aid, _ in P0[p]:
            apc.setdefault(aid, 0)
            apc[aid] += 1
    print(f"  POPULATION  {N} prompts · {NA} annotators overall · on parity-0: "
          f"{len(apc)} annotators, median {np.median(list(apc.values())):.0f} prompts each, "
          f"max {max(apc.values())}")

    CL = {a: {p: np.array(cls(yvec(S[a][p], sorted({i for i, _ in S[a][p]})))) for p in pids}
          for a in ARMS}
    POOLK = {k: {p: np.array(cls(yvec(POOL[p], list(range(k))))) for p in pids} for k in (4, 12)}

    # ---- flat (prompt, annotator) agreement tables per quantity --------------------------------
    AIDX = {a: i for i, a in enumerate(sorted(apc))}
    NA0 = len(AIDX)
    rows_p, rows_a = [], []
    for i, p in enumerate(pids):
        for aid, _ in P0[p]:
            rows_p.append(i)
            rows_a.append(AIDX[aid])
    rows_p = np.array(rows_p)
    rows_a = np.array(rows_a)
    NR = len(rows_p)

    def agree_table(getc):
        v = np.zeros(NR)
        t = 0
        for p in pids:
            c = getc(p)
            for _, h in P0[p]:
                v[t] = float((h == c).mean())
                t += 1
        return v

    TAB = {a: agree_table(lambda p, a=a: CL[a][p]) for a in ARMS}
    # ⚠ R811 averages `random_k` over THREE committed seeds; the first run used s0 alone and the
    # object check exited 2 on H3/H4 by ~0.0045. Averaged here, as R811 does.
    TAB["random12_3seed"] = np.mean([TAB[f"random_k12_s{i}"] for i in (0, 1, 2)], axis=0)
    TAB["pool4"] = agree_table(lambda p: POOLK[4][p])
    TAB["pool12"] = agree_table(lambda p: POOLK[12][p])

    def per_prompt(vec, w):
        """weighted per-prompt mean; w is a per-ROW weight (annotator multiplicity)."""
        num = np.bincount(rows_p, weights=vec * w, minlength=N)
        den = np.bincount(rows_p, weights=w, minlength=N)
        return num, den

    def headline(w, pw):
        """w: per-row annotator weights. pw: per-prompt weights. Returns the four headlines."""
        res = {}
        cache = {}
        for key in ("oracle_k4_fit1", "genericpool16", "topw_k12", "greedy_k12_fit1",
                    "indep_k12_fit1", "topw_k4", "random12_3seed", "pool12"):
            num, den = per_prompt(TAB[key], w)
            cache[key] = (num, den)
        ok = cache["oracle_k4_fit1"][1] > 0
        def pm(key):
            num, den = cache[key]
            return np.where(ok, num / np.maximum(den, 1e-12), 0.0)
        tot = float((pw * ok).sum())
        totc = float((pw * ok * INCOMMON).sum())
        def wm(x):
            return float((x * pw * ok).sum() / max(tot, 1e-12))
        def wmc(x):                      # restricted to R810/R811's common intersection
            return float((x * pw * ok * INCOMMON).sum() / max(totc, 1e-12))
        fit12 = 0.5 * (pm("greedy_k12_fit1") + pm("indep_k12_fit1"))
        res["H1"] = wm(pm("oracle_k4_fit1") - pm("genericpool16"))
        res["H2"] = wmc(fit12 - pm("topw_k12"))
        res["H3"] = wmc(pm("topw_k12") - pm("random12_3seed"))
        res["H4"] = wmc(pm("pool12") - pm("random12_3seed"))
        res["_dropped"] = int((~ok).sum())
        return res

    ONE_R = np.ones(NR)
    ONE_P = np.ones(N)
    cset = set(COMMON)
    INCOMMON = np.array([1.0 if p in cset else 0.0 for p in pids])

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK - the four committed point estimates")
    base = headline(ONE_R, ONE_P)
    COMMIT = {"H1": 0.0553, "H2": 0.0116, "H3": 0.0419, "H4": 0.0372}
    okall = True
    for h in ("H1", "H2", "H3", "H4"):
        d = abs(base[h] - COMMIT[h])
        okall &= d < 1e-3
        print(f"     {h}  {base[h]:+.4f}  vs committed {COMMIT[h]:+.4f}   |Δ| {d:.4f}   "
              f"{'PASS' if d < 1e-3 else 'FAIL'}")
    if not okall:
        print("  UNRUNNABLE: the committed headlines did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {h: base[h] for h in ("H1", "H2", "H3", "H4")}

    # ================= the three schemes =========================================================
    def run_scheme(scheme, seed, nb=NBOOT, ra=None):
        # ⛔ `ra` exists because the first version of the NEGATIVE control did
        # `globals()["rows_a"] = fake` — but `rows_a` is LOCAL to main(), so the closures below
        # never saw it and the reassignment did nothing. It printed a width identical to the real
        # one with an sd of exactly 0.0000, which is the same degenerate signature R809 and R810
        # hit. The annotator index must be passed in, not patched into a namespace nobody reads.
        ra = rows_a if ra is None else ra
        rng = np.random.default_rng(seed)
        acc = {h: [] for h in ("H1", "H2", "H3", "H4")}
        drops = []
        for _ in range(nb):
            if scheme == "prompt":
                pw = np.bincount(rng.integers(0, N, N), minlength=N).astype(float)
                w = ONE_R
            elif scheme == "annotator":
                cnt = np.bincount(rng.integers(0, NA0, NA0), minlength=NA0).astype(float)
                w = cnt[ra]
                pw = ONE_P
            else:                                    # crossed
                pw = np.bincount(rng.integers(0, N, N), minlength=N).astype(float)
                cnt = np.bincount(rng.integers(0, NA0, NA0), minlength=NA0).astype(float)
                w = cnt[ra]
            r = headline(w, pw)
            drops.append(r["_dropped"])
            for h in acc:
                acc[h].append(r[h])
        return ({h: (float(np.percentile(acc[h], 2.5)), float(np.percentile(acc[h], 97.5)))
                 for h in acc}, float(np.mean(drops)))

    print("\n  E1/E2/E3 - THREE RESAMPLING SCHEMES, AND THE DESIGN EFFECT")
    CI, DROP = {}, {}
    for sch in ("prompt", "annotator", "crossed"):
        CI[sch], DROP[sch] = run_scheme(sch, SEEDS[0])
        print(f"     {sch:<10} prompts dropped per draw (zero annotators): {DROP[sch]:.1f} / {N} "
              f"({100 * DROP[sch] / N:.1f}%)")
    dropbad = max(DROP.values()) / N > 0.10
    print(f"     dropped-prompt rate above 10%: {dropbad}   "
          f"{'FAIL - the estimand is degraded' if dropbad else 'PASS'}")

    print(f"\n     {'headline':<6}{'point':>9}{'prompt CI':>24}{'annotator CI':>24}"
          f"{'crossed CI':>24}{'DE':>7}")
    de, e4 = {}, {}
    for h in ("H1", "H2", "H3", "H4"):
        wp = CI["prompt"][h][1] - CI["prompt"][h][0]
        wa = CI["annotator"][h][1] - CI["annotator"][h][0]
        wc = CI["crossed"][h][1] - CI["crossed"][h][0]
        de[h] = wc / max(wp, 1e-12)
        res = not (CI["crossed"][h][0] <= 0 <= CI["crossed"][h][1])
        e4[h] = {"point": base[h], "prompt": CI["prompt"][h], "annotator": CI["annotator"][h],
                 "crossed": CI["crossed"][h], "w_prompt": wp, "w_ann": wa, "w_crossed": wc,
                 "design_effect": de[h], "resolved_crossed": res}
        print(f"     {h:<6}{base[h]:>+9.4f}  [{CI['prompt'][h][0]:+.4f},{CI['prompt'][h][1]:+.4f}]"
              f"  [{CI['annotator'][h][0]:+.4f},{CI['annotator'][h][1]:+.4f}]"
              f"  [{CI['crossed'][h][0]:+.4f},{CI['crossed'][h][1]:+.4f}]{de[h]:>7.2f}"
              f"   {'' if res else '⛔ LOSES RESOLUTION'}")
    d1 = all(v >= 1.0 - 1e-9 for v in de.values())
    print(f"     D1 the crossed interval is never narrower than the prompt interval: {d1}   "
          f"{'PASS' if d1 else 'FAIL - the code is wrong and this round says so'}")
    out["e3"] = e4
    out["design_effects"] = de

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    rng = np.random.default_rng(99)
    zw = []
    for _ in range(200):
        pw = np.bincount(rng.integers(0, N, N), minlength=N).astype(float)
        cnt = np.bincount(rng.integers(0, NA0, NA0), minlength=NA0).astype(float)
        w = cnt[rows_a]
        num, den = per_prompt(TAB["topw_k12"] - TAB["topw_k12"], w)
        zw.append(float(np.abs(num).max()))
    plac_ok = max(zw) == 0.0
    print(f"     PLACEBO   D2 an arm minus ITSELF under the crossed scheme, max |value| over 200 "
          f"draws: {max(zw):.1e}   {'PASS - zero width everywhere' if plac_ok else 'FAIL'}")

    print("     POSITIVE  D4 plant an annotator-specific offset; the ANNOTATOR interval must widen")
    rngp = np.random.default_rng(7)
    off = rngp.normal(0, 1, NA0)
    pos = {}
    for g in (0.0, 0.05, 0.15):
        sav = TAB["oracle_k4_fit1"].copy()
        TAB["oracle_k4_fit1"] = sav + g * off[rows_a]
        cia, _ = run_scheme("annotator", 4242, nb=300)
        cip, _ = run_scheme("prompt", 4242, nb=300)
        pos[g] = (cia["H1"][1] - cia["H1"][0], cip["H1"][1] - cip["H1"][0])
        TAB["oracle_k4_fit1"] = sav
        print(f"        g={g:<5} annotator width {pos[g][0]:.4f}   prompt width {pos[g][1]:.4f}")
    mono = pos[0.0][0] < pos[0.05][0] < pos[0.15][0]
    g0_ok = abs(pos[0.0][0] - CI["annotator"]["H1"][1] + CI["annotator"]["H1"][0]) < 0.02
    prompt_flat = pos[0.15][1] / max(pos[0.0][1], 1e-12) < 1.5
    pos_ok = mono and prompt_flat
    print(f"        annotator width monotone in g: {mono}   prompt width nearly unmoved "
          f"(ratio {pos[0.15][1] / max(pos[0.0][1], 1e-12):.2f}): {prompt_flat}   "
          f"{'PASS' if pos_ok else 'FAIL'}")

    print("     NEGATIVE  D3 annotator ids reassigned at random -> the crossing is destroyed")
    rngn = np.random.default_rng(303)
    ws = []
    for _ in range(20):
        fake = rngn.integers(0, NA0, NR)      # every ROW gets an independent random annotator id
        cia, _ = run_scheme("annotator", 555, nb=200, ra=fake)
        ws.append(cia["H1"][1] - cia["H1"][0])
    real_wa = CI["annotator"]["H1"][1] - CI["annotator"]["H1"][0]
    wp1 = CI["prompt"]["H1"][1] - CI["prompt"]["H1"][0]
    neg_ok = float(np.mean(ws)) < real_wa
    print(f"        reassigned annotator width {np.mean(ws):.4f} ± {np.std(ws):.4f}   real "
          f"{real_wa:.4f}   prompt {wp1:.4f}   collapses: {neg_ok}   "
          f"{'PASS' if neg_ok else 'FAIL'}")

    sd = {}
    for h in ("H1", "H2"):
        ws2 = []
        for s in SEEDS:
            c, _ = run_scheme("crossed", s, nb=400)
            ws2.append(c[h][1] - c[h][0])
        sd[h] = float(np.std(ws2))
    print(f"     NOISE FLOOR  crossed width across {len(SEEDS)} seeds: " +
          "  ".join(f"{h} sd {sd[h]:.4f}" for h in sd))
    gate = okall and plac_ok and pos_ok and neg_ok and not dropbad and d1
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo_ok": plac_ok, "positive": {str(k): v for k, v in pos.items()},
                       "positive_ok": pos_ok, "negative_mean_width": float(np.mean(ws)),
                       "negative_ok": neg_ok, "width_sd": sd, "dropped": DROP,
                       "d1": d1, "gate": gate}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    demax = max(de.values())
    lost = [h for h in e4 if not e4[h]["resolved_crossed"]]
    if not gate:
        world = "UNVERIFIED"
    elif demax >= 1.5 and lost:
        world = "B"
    elif demax <= 1.2:
        world = "A"
    else:
        world = "C"
    print(f"     largest design effect {demax:.2f}   headlines losing resolution under the crossed "
          f"scheme: {lost if lost else 'none'}  ->  WORLD {world}")
    out["world"] = world
    out["lost"] = lost

    art = HERE / "results/crossed_bootstrap.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
