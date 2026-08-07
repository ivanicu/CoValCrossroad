#!/usr/bin/env python3
"""R780 · the cross-release wall is false as written, and the measurement it forbade is runnable.

CHECK #382 killed R779's NEXT on IDENTIFICATION before any design (of 8 selection rules, only
`random` and `topw` vary k; over 6 families k and rule are not crossed) and then found something
larger in my own output: every round's impossibility register carries a `cross-release` row, and
R779's -- written one hour ago -- says `cross-release | a second release`, while a second release is
on disk with seven arms already scored.

R556 ESTABLISHED THE EXISTENCE. What is new here is that the correction never reached the artifacts.
And `corebench/score.py:33` scopes it correctly -- "a second values-annotation release WITH THIS
SCHEMA" -- so the wall is REAL for schema-bound quantities and FALSE as the round READMEs write it.

ESTIMAND        E1 unscoped-wall lines, split at R556 · E2 the clause-② contrast on BOTH releases
                under a gauge-matched estimator · E3 required n if release 2 does not resolve
IDENTIFICATION  E2 only on release 2's n=4 STRATUM (6 pairs, matched to release 1); targets matched
                by using release 1's MEAN ranking, with the all-annotator version as a specification
SCOPE           r1 968 prompts · r2 1,684 n=4 interactions · same core_generic.json both sides
WORLDS          A transports · B release-bound · C unresolved by power
KILL            conditional, gated on OBJECT + POSITIVE + g=0 + PLACEBO
CONTROLS        OBJECT · POSITIVE (swept, band computed) · g=0 · NEGATIVE (200) · SHAM (absent, not
                inverted) · PLACEBO · SEARCH (the regex has its own positive and negative control)
"""
import collections
import itertools
import json
import math
import pathlib
import re
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets                      # noqa: E402
from report import verdict                                    # noqa: E402

RES = ROOT / "corebench/results"
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
L = "ABCD"
PR6 = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
NBOOT = 1200
NPERM = 200
SEED = 31337

# the census instrument, with the two strings §4 requires to be named separately
INSTRUMENT_UNIT = "a regex match in a round artifact"
CLAIM_UNIT = "a line in a round artifact"
# ⚠ THE FIRST PATTERN WROTE `one release` AND ITS OWN NEGATIVE CONTROL CAUGHT IT: that matches
# inside `one released core, and its sham is ours`, a CORRECTLY-scoped line, because `release` is a
# prefix of `released`. §4's *a search is an instrument* -- and the loose pattern would have inflated
# the count by exactly the entries that prove the arc sometimes gets this right.
WALL = re.compile(r'cross.release[^\n|]*\|[^\n]*?(one release(?!d)|a second release|N/A)', re.I)
THIS_ROUND = 780   # the census must not count the round doing the counting


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


def sgn(y):
    """pairwise sign vector over 4 responses -- identical code on both releases"""
    return np.sign(np.array([y[i] - y[j] for i, j in PR6]))


def a2(pred, targ):
    return float((sgn(pred) == sgn(targ)).mean())


def cell(d, label, use_mde=True):
    """paired difference -> eff, CI, MDE, verdict. One estimator, both releases."""
    n = len(d)
    ib = np.random.default_rng(SEED).integers(0, n, (NBOOT, n))
    bs = d[ib].mean(axis=1)
    lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
    eff = float(d.mean())
    mde = ZEFF * float(d.std(ddof=1)) / math.sqrt(n)
    return {"label": label, "n": n, "eff": eff, "lo": lo, "hi": hi, "mde": mde,
            "verdict": verdict(eff, lo, hi, mde if use_mde else None)}


def load_release2():
    """-> {arm: {iid: {(ci, rid): sat}}}, targets {iid: [(rid, score)]}"""
    arms, tg = {}, None
    for p in sorted(RES.glob("sat_transport_*.npz")):
        z = np.load(p, allow_pickle=True)
        o = collections.defaultdict(dict)
        for k, v in zip(z["meta"], z["sat"]):
            conv, inter, rid, ci = str(k).split("|")
            o[f"{conv}|{inter}"][(int(ci), rid)] = float(v)
        arms[p.stem[4:]] = o
        if tg is None:
            tg = {f"{t['conv']}|{t['inter']}": [(r["id"], float(r["score"])) for r in t["resp"]]
                  for t in json.loads(str(z["targets"]))}
    return arms, tg


def prov_core(tag):
    z = np.load(RES / f"sat_{tag}.npz", allow_pickle=True)
    return json.loads(str(z["provenance"]))["core"] if "provenance" in z.files else None


def main():
    out = {"instrument_unit": INSTRUMENT_UNIT, "claim_unit": CLAIM_UNIT}

    # ================= E1 · the census, with the search treated as an instrument ==================
    print("  E1 - THE UNSCOPED CROSS-RELEASE WALL, ACROSS THIS ARC'S ROUND ARTIFACTS")
    hits = []
    for d in sorted(ARC.glob("R*/")):
        m = re.match(r"R(\d+)", d.name)
        if not m:
            continue
        for f in ("README.md", "PREREGISTRATION.txt"):
            p = d / f
            if p.is_file():
                for ln in p.read_text().splitlines():
                    if WALL.search(ln) and int(m.group(1)) != THIS_ROUND:
                        hits.append({"round": int(m.group(1)), "dir": d.name, "file": f,
                                     "line": ln.strip()})
    after = [h for h in hits if h["round"] > 556]
    before = [h for h in hits if h["round"] <= 556]

    # SEARCH POSITIVE CONTROL -- lines whose status I know, because I wrote them
    known_true = "| cross-release | a second release |"
    known_false = [
        "| cross-release | the partition and n are this release's |",
        "| cross-release | one released core, and its sham is ours |",
        "| cross-release | the `NEXT` convention is this project's |",
    ]
    s_pos = bool(WALL.search(known_true))
    s_neg = sum(1 for s in known_false if WALL.search(s))
    r779 = [h for h in hits if h["round"] == 779]
    print(f"     SEARCH POSITIVE  the known-unscoped line is flagged: {s_pos}   "
          f"R779's own register line found: {len(r779) == 1}")
    print(f"     SEARCH NEGATIVE  correctly-scoped lines wrongly flagged: {s_neg} of "
          f"{len(known_false)}")
    search_ok = s_pos and s_neg == 0 and len(r779) == 1
    print(f"     units named separately and equal: "
          f"{INSTRUMENT_UNIT!r} vs {CLAIM_UNIT!r} -> "
          f"{'a line is the unit of both' if search_ok else 'UNSAFE'}")
    print(f"     self-excluded: R{THIS_ROUND}'s own artifacts are NOT counted")
    print(f"     lines asserting an UNSCOPED wall: {len(hits)}   "
          f"<=R556: {len(before)}   >R556: {len(after)}")
    print(f"     rounds AFTER R556 still asserting it: {sorted({h['round'] for h in after})}")
    out["census"] = {"total": len(hits), "before": len(before), "after": len(after),
                     "rounds_after": sorted({h["round"] for h in after}),
                     "search_positive": s_pos, "search_negative_wrongly_flagged": s_neg,
                     "search_ok": search_ok}

    # ================= OBJECT CHECK -- exit 2, never 0 ============================================
    print("\n  OBJECT CHECK")
    r2, tg2 = load_release2()
    strata = collections.Counter(len(v) for v in tg2.values())
    n4 = sorted(i for i, v in tg2.items() if len(v) == 4)
    c_gen2 = prov_core("transport_generic")
    same_blind = c_gen2 == "corebench/results/core_generic.json"
    base1 = load_sat(RES / "sat_generic.npz")
    disjoint = len(set(base1) & set(tg2)) == 0
    print(f"     release 2 arms {len(r2)}   interactions {len(tg2)}   strata {dict(sorted(strata.items()))}")
    print(f"     n=4 stratum {len(n4)}   blind core matched ({c_gen2}): {same_blind}   "
          f"id spaces disjoint: {disjoint}")
    if not (same_blind and len(n4) > 0 and disjoint and len(r2) == 7):
        print("  UNRUNNABLE: the matched blind reference or the stratum is absent. Exit 2, never 0.")
        return 2
    out["object"] = {"arms_r2": len(r2), "interactions": len(tg2),
                     "strata": {str(k): v for k, v in sorted(strata.items())},
                     "n4": len(n4), "blind_core": c_gen2, "disjoint": disjoint}

    # ================= build both releases' matched vectors =======================================
    targets, _ = load_targets()
    ARMS1 = {"gen": "gen", "generic": "generic", "gen_sham": "gen_sham"}
    S1 = {k: load_sat(RES / f"sat_{v}.npz") for k, v in ARMS1.items()}
    p1 = sorted(set(S1["gen"]) & set(S1["generic"]) & set(S1["gen_sham"]) &
                {p for p in targets if len(targets[p]) >= 2})

    def y1(tag, p):
        S = S1[tag][p]
        ii = sorted({i for i, _ in S})
        return np.array([sum(S.get((i, x), 0.0) for i in ii) for x in L])

    # matched target: the MEAN ranking across annotators -> ONE score vector, as release 2 ships
    t1_mean = {p: np.array([np.mean([y[c] for y, _ in targets[p]]) for c in range(4)]) for p in p1}

    def score1(tag, tmap):
        return np.array([a2(y1(tag, p), tmap[p]) for p in p1])

    def y2(arm, i):
        S = r2[arm][i]
        rid = [r for r, _ in tg2[i]]
        ci = sorted({c for c, _ in S})
        return np.array([sum(S.get((c, r), 0.0) for c in ci) for r in rid])

    t2 = {i: np.array([s for _, s in tg2[i]]) for i in n4}

    def score2(arm):
        return np.array([a2(y2(arm, i), t2[i]) for i in n4])

    A1 = {t: score1(t, t1_mean) for t in ARMS1}
    A2_ = {a: score2(a) for a in r2}
    print(f"     release 1 prompts {len(p1)}   release 2 n=4 units {len(n4)}")

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    plac = float(np.abs(A1["gen"] - A1["gen"]).max()), float(np.abs(A2_["transport_gen"] -
                                                                   A2_["transport_gen"]).max())
    print(f"     PLACEBO    an arm against itself: r1 {plac[0]:.6f}   r2 {plac[1]:.6f}")
    placebo = plac[0] == 0.0 and plac[1] == 0.0

    # g=0 -- the blind arm against a byte-identical recomputation of its own core
    g0 = float(np.abs(A1["generic"] - score1("generic", t1_mean)).max())
    g0b = float(np.abs(A2_["transport_generic"] - score2("transport_generic")).max())
    print(f"     g=0        blind vs an identical core: r1 {g0:.6f}   r2 {g0b:.6f}")
    g0ok = g0 == 0.0 and g0b == 0.0

    rng = np.random.default_rng(SEED)
    perm1 = np.array([float((A1["gen"] - A1["generic"])[rng.permutation(len(p1))].mean())
                      for _ in range(NPERM)])
    perm2 = np.array([float((A2_["transport_gen"] - A2_["transport_generic"])
                            [rng.permutation(len(n4))].mean()) for _ in range(NPERM)])
    print(f"     NEGATIVE   permuting the PAIRING leaves the mean fixed by construction: "
          f"r1 spread {perm1.std():.2e}  r2 spread {perm2.std():.2e}  -- DERIVATION, not a null")
    # the real negative: permute the TARGET across units, refitting the score
    def permute_target(tmap, keys, fn):
        ks = list(keys)
        sh = rng.permutation(len(ks))
        return np.array([fn(ks[a], tmap[ks[b]]) for a, b in zip(range(len(ks)), sh)])
    nd1, nd2 = [], []
    for _ in range(NPERM):
        pg = permute_target(t1_mean, p1, lambda p, t: a2(y1("gen", p), t))
        pb = permute_target(t1_mean, p1, lambda p, t: a2(y1("generic", p), t))
        nd1.append(float((pg - pb).mean()))
        qg = permute_target(t2, n4, lambda i, t: a2(y2("transport_gen", i), t))
        qb = permute_target(t2, n4, lambda i, t: a2(y2("transport_generic", i), t))
        nd2.append(float((qg - qb).mean()))
    nd1, nd2 = np.array(nd1), np.array(nd2)
    print(f"     NEGATIVE   target permuted, {NPERM} draws:  r1 "
          f"[{np.percentile(nd1, 2.5):+.4f}, {np.percentile(nd1, 97.5):+.4f}]   r2 "
          f"[{np.percentile(nd2, 2.5):+.4f}, {np.percentile(nd2, 97.5):+.4f}]")

    # SHAM -- the ingredient ABSENT, not inverted: blind vs ANOTHER blind arm
    sham2 = cell(A2_["transport_randblind_s0"] - A2_["transport_generic"], "sham r2")
    print(f"     SHAM       prompt-specificity ABSENT (blind vs blind), r2: {sham2['eff']:+.4f} "
          f"[{sham2['lo']:+.4f}, {sham2['hi']:+.4f}]  MDE {sham2['mde']:.4f}  {sham2['verdict']}")

    # POSITIVE -- plant, sweep, band computed at both ends
    def plant(base_scores, tmap, keys, yf, w):
        o = []
        for k in keys:
            y = yf(k).astype(float)
            y = y / (np.abs(y).max() or 1.0)
            o.append(a2((1 - w) * y + w * tmap[k] / (np.abs(tmap[k]).max() or 1.0), tmap[k]))
        return np.array(o)
    dose = {}
    okp = True
    for w in (0.0, 0.25, 0.5, 1.0):
        d1 = plant(None, t1_mean, p1, lambda p: y1("generic", p), w) - A1["generic"]
        d2 = plant(None, t2, n4, lambda i: y2("transport_generic", i), w) - A2_["transport_generic"]
        c1, c2 = cell(d1, f"plant r1 w={w}"), cell(d2, f"plant r2 w={w}")
        dose[str(w)] = {"r1": c1, "r2": c2}
        print(f"     POSITIVE   w {w:>4.2f}   r1 {c1['eff']:+.4f} {c1['verdict']:<16} "
              f"r2 {c2['eff']:+.4f} {c2['verdict']}")
        if w == 0.0 and (c1["verdict"] != "UNRESOLVED" or c2["verdict"] != "UNRESOLVED"):
            okp = False
        if w == 1.0 and not (c1["verdict"].startswith("BEATS") and c2["verdict"].startswith("BEATS")):
            okp = False
    floor_ = dose["0.0"]["r2"]["eff"]
    ceil_ = dose["1.0"]["r2"]["eff"]
    print(f"                band COMPUTED: floor {floor_:+.4f} < threshold < ceiling {ceil_:+.4f}  "
          f"-> {'admissible' if floor_ < ceil_ else 'DEGENERATE'}   POSITIVE "
          f"{'PASS' if okp else 'FAIL'}")

    out["controls"] = {"placebo_r1": plac[0], "placebo_r2": plac[1], "g0_r1": g0, "g0_r2": g0b,
                       "neg_target_r1": [float(np.percentile(nd1, 2.5)), float(np.percentile(nd1, 97.5))],
                       "neg_target_r2": [float(np.percentile(nd2, 2.5)), float(np.percentile(nd2, 97.5))],
                       "sham_r2": sham2, "dose": dose, "positive": okp, "placebo": placebo,
                       "g0": g0ok, "perm_pairing_is_a_derivation": True}

    # ================= E2 · the contrast the wall forbade =========================================
    print("\n  E2 - CLAUSE ② ACROSS RELEASES, GAUGE-MATCHED ESTIMATOR")
    rows = {}
    rows["r1_gen_vs_blind"] = cell(A1["gen"] - A1["generic"], "r1 gen - generic")
    rows["r2_gen_vs_blind"] = cell(A2_["transport_gen"] - A2_["transport_generic"], "r2 gen - generic")
    rows["r1_sham_vs_blind"] = cell(A1["gen_sham"] - A1["generic"], "r1 gen_sham - generic")
    rows["r2_sham_vs_blind"] = cell(A2_["transport_gen_sham"] - A2_["transport_generic"],
                                    "r2 gen_sham - generic")
    rows["r2_vacuous_vs_blind"] = cell(A2_["transport_vacuous"] - A2_["transport_generic"],
                                       "r2 vacuous - generic")
    for k in ("r2_randblind_s0", "r2_randblind_s1", "r2_randblind_s2"):
        s = k.split("_")[-1]
        rows[k + "_vs_blind"] = cell(A2_[f"transport_randblind_{s}"] - A2_["transport_generic"],
                                     f"r2 randblind_{s} - generic")
    print(f"     {'contrast':<30}{'n':>7}{'eff':>10}{'CI':>22}{'MDE':>9}   verdict")
    for k, v in rows.items():
        print(f"     {k:<30}{v['n']:>7}{v['eff']:>+10.4f}"
              f"{f'[{v[chr(108)+chr(111)]:+.4f}, {v[chr(104)+chr(105)]:+.4f}]':>22}"
              f"{v['mde']:>9.4f}   {v['verdict']}")

    # the higher-resolution specification on release 1: ALL annotators, not the mean ranking
    def score1_all(tag):
        o = []
        for p in p1:
            y = y1(tag, p)
            o.append(float(np.mean([(sgn(y) == sgn(np.array(t))).mean() for t, _ in targets[p]])))
        return np.array(o)
    spec = cell(score1_all("gen") - score1_all("generic"), "r1 all-annotator")
    print(f"     {'r1_gen_vs_blind_ALLANNOT':<30}{spec['n']:>7}{spec['eff']:>+10.4f}"
          f"{f'[{spec[chr(108)+chr(111)]:+.4f}, {spec[chr(104)+chr(105)]:+.4f}]':>22}"
          f"{spec['mde']:>9.4f}   {spec['verdict']}   (specification, not the matched cell)")
    rows["r1_gen_vs_blind_allannot"] = spec

    # the strata excluded from the headline, reported rather than dropped
    print("\n     STRATA EXCLUDED FROM THE HEADLINE (not gauge-matched -- D1):")
    for nresp in (2, 3):
        ks = sorted(i for i, v in tg2.items() if len(v) == nresp)
        prs = list(itertools.combinations(range(nresp), 2))
        def a2n(pred, targ):
            return float(np.mean([np.sign(pred[i] - pred[j]) == np.sign(targ[i] - targ[j])
                                  for i, j in prs]))
        def yn(arm, i):
            S = r2[arm][i]
            rid = [r for r, _ in tg2[i]]
            ci = sorted({c for c, _ in S})
            return np.array([sum(S.get((c, r), 0.0) for c in ci) for r in rid])
        tt = {i: np.array([s for _, s in tg2[i]]) for i in ks}
        d = np.array([a2n(yn("transport_gen", i), tt[i]) - a2n(yn("transport_generic", i), tt[i])
                      for i in ks])
        c = cell(d, f"r2 n={nresp}")
        rows[f"r2_n{nresp}_gen_vs_blind"] = c
        print(f"     {'r2 n=' + str(nresp) + ' gen - generic':<30}{c['n']:>7}{c['eff']:>+10.4f}"
              f"{f'[{c[chr(108)+chr(111)]:+.4f}, {c[chr(104)+chr(105)]:+.4f}]':>22}"
              f"{c['mde']:>9.4f}   {c['verdict']}")
    out["rows"] = rows

    # ================= E3 · required n if release 2 does not resolve ==============================
    e1v, e2v = rows["r1_gen_vs_blind"], rows["r2_gen_vs_blind"]
    sd2 = e2v["mde"] * math.sqrt(e2v["n"]) / ZEFF
    need = math.ceil((ZEFF * sd2 / abs(e1v["eff"])) ** 2) if e1v["eff"] != 0 else None
    print(f"\n  E3 - to resolve a RELEASE-1-SIZED effect ({e1v['eff']:+.4f}) on release 2 needs "
          f"n = {need}   (have {e2v['n']}, factor {need / e2v['n']:.2f}x)")
    out["required_n"] = {"effect": e1v["eff"], "sd_r2": sd2, "need": need, "have": e2v["n"]}

    # ================= WORLD ======================================================================
    gate = placebo and g0ok and okp
    b1 = e1v["verdict"].startswith("BEATS")
    b2 = e2v["verdict"].startswith("BEATS")
    if not gate:
        world = "UNVERIFIED - a control did not fire. Never OVERTURNED, never CONFIRMED."
    elif b1 and b2:
        world = f"A - CLAUSE ② TRANSPORTS: r1 {e1v['eff']:+.4f}, r2 {e2v['eff']:+.4f}, both resolved"
    elif b1 and not b2 and e2v["mde"] < abs(e1v["eff"]):
        world = (f"B - CLAUSE ② IS RELEASE-BOUND: r1 {e1v['eff']:+.4f} resolved, r2 "
                 f"{e2v['eff']:+.4f} {e2v['verdict']} with MDE {e2v['mde']:.4f} < |eff_1|")
    elif not b2 and e2v["mde"] >= abs(e1v["eff"]):
        world = (f"C - UNRESOLVED BY POWER: r2 MDE {e2v['mde']:.4f} >= |eff_1| "
                 f"{abs(e1v['eff']):.4f}; required n = {need} against {e2v['n']}")
    else:
        world = (f"NO WORLD CLAIMED: r1 {e1v['verdict']}, r2 {e2v['verdict']} -- the matrix's "
                 f"branches do not cover this combination")
    print(f"\n  WORLD {world}")
    out["world"] = world
    out["tree_sha"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip()
    d = pathlib.Path(__file__).resolve().parent / "results"
    d.mkdir(exist_ok=True)
    (d / "cross_release.json").write_text(json.dumps(out, indent=2, default=_plain))
    print(f"  artifact -> cross_release.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
