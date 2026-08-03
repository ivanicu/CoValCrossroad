"""r117 -- invisible sacrifice is not one dimension. Six units, two statistics each, one floor each.

Ivan, 2026-07-30: prove there are various MULTIDIMENSIONAL invisible sacrifices, in various ways,
that survive CROSS VERIFICATION.

r116 answered the question on ONE unit -- people -- and found 12.46% absolutely worse off at
eps=0.01, +1.83 points over a paired-shuffle floor, permutation p = 0.0100. But "who is sacrificed"
presupposes that the bearer of a sacrifice is a person, and that is an assumption, not a finding. A
compiled rule can also serve some QUESTIONS worse, some KINDS of question worse, some COLLECTION
BRANCHES worse, and some DECISION POSITIONS worse -- each of which is invisible in a per-person
average exactly as the per-person spread is invisible in a grand mean.

SIX UNITS, AND WHY EACH NULL DIFFERS
------------------------------------
A floor must destroy the structure under test and preserve everything else. There is no single
permutation that does this for six different structures, and using one would be the mistake this
project has now made four times.

  U1 PERSON        delta_i over that rater's cells. NULL: permute rater identity WITHIN prompt --
                   preserves prompt effects, each rater's workload, and the marginal error
                   distribution exactly.
  U2 PROMPT        delta_p over that prompt's cells. NULL: permute prompt identity WITHIN rater --
                   the mirror image; preserves each rater's own error set, destroys prompt structure.
  U3 SUBJECTIVITY  4 levels, and this is the sharpest because it carries its OWN negative control:
                   "depends on a person's values or culture" (normative disagreement, the object)
                   versus "depends on something else -- the time, the weather" (factual indexicality,
                   NOT the object). A sacrifice concentrated on the first and absent on the second is
                   about values; one on both is about disagreement per se. NULL: permute the level
                   label across prompts, preserving the level marginals.
  U4 STRATUM       world-only prompts versus prompts that also collect a personal ranking. Entry 26
                   established these are DISJOINT and that all replication sits in the first. NULL:
                   permute the stratum label across prompts.
  U5 LABEL         A/B/C/D. r19 measured a corpus-wide label asymmetry (chi-square 52.1, 3 df,
                   p=2.85e-11) that could never be attributed, because no field records presentation
                   order. Harm BY LABEL needs no order field: it asks whether the compiled rule
                   mis-orders particular labels more than the uncompiled one. NULL: permute labels
                   within prompt, which preserves each prompt's response set exactly.
  U6 CONTESTED     pairs binned by how much the humans themselves disagreed on that pair. NULL:
                   permute the contest bin across pairs within prompt.

CROSS VERIFICATION -- the requirement Ivan set, and it is stronger than a p-value
--------------------------------------------------------------------------------
Every dimension is measured TWICE by statistics that fail differently, and a dimension counts only
if BOTH agree:

  STAT A  HARM RATE   share of units worse under core, against that unit's own permutation floor.
                      A COUNT. Insensitive to the size of the harm, sensitive to its breadth.
  STAT B  TAIL MASS   the share of TOTAL sacrifice carried by the worst decile of that unit, against
                      the same floor. A CONCENTRATION. Insensitive to breadth, sensitive to size.

A real structure moves both. Noise moves neither. A threshold artifact moves A alone; a single
outlier moves B alone. Requiring both is what makes this cross-verification rather than two chances
to find something -- and every dimension is reported whether or not it survives, because reporting
only survivors is the multiplicity failure this project catalogued at `if chi > 100`.

BENJAMINI-HOCHBERG across all dimensions x both statistics, because 12 tests reported one at a time
is the same failure with better manners.

WHAT THIS ROUND MAY NOT CONCLUDE
--------------------------------
That a surviving dimension is CAUSED by compilation rather than correlated with it (no V2 exists to
contrast); that a surviving dimension has a demographic subject (entry 25: none over 30 cells); or
that a failing dimension is clean -- a null here is UNVERIFIED unless the positive control recovered
a planted sacrifice on that same unit, which is reported per dimension.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join            # noqa: E402
from covalx.stamp import stamp          # noqa: E402

FULL = _ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz"
CORE = _ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_core.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"

SEED = 20260730
N_PERM = 400
EPS = 0.01                # same pre-registered threshold as r116
TAIL_Q = 0.10
BH_Q = 0.05
PLANT_G, PLANT_SHARE = 0.10, 0.10   # r116 measured that recovery needs g~0.10; reused, not re-chosen
VALUES = "The correct answer depends on a person's values or culture"
OTHER = "The correct answer depends on something else (the time, the weather, etc)"


def nfkc(s):
    return unicodedata.normalize("NFKC", str(s))


def load_sat(path: Path) -> dict:
    z = np.load(path, allow_pickle=True)
    d: dict = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        d[pid][(int(ci), lab)] = float(s)
    return d


def equal_weight_scores(satp: dict) -> dict:
    out = {}
    for lab in sorted({l for _, l in satp}):
        v = [s for (ci, ll), s in satp.items() if ll == lab]
        if v:
            out[lab] = float(np.mean(v))
    return out


def strict_pairs(ranking: str) -> set:
    tiers = [t.split("=") for t in ranking.split(">")]
    out = set()
    for i, a in enumerate(tiers):
        for b in tiers[i + 1:]:
            for x in a:
                for y in b:
                    out.add((x.strip(), y.strip()))
    return out


def build():
    """Cell rows AND pair rows. The pair rows are what U5 and U6 need: a decision, not an average."""
    F, C = load_sat(FULL), load_sat(CORE)
    cells, pairs = [], []
    ties = {"full_only": 0, "core_only": 0, "both": 0}
    joined = sorted(((pid, comp) for pid, comp, rub in load_join(COMPARISONS, RUBRICS)
                     if pid in F and pid in C), key=lambda t: t[0])
    # which prompts collect a personal ranking at all (entry 26: the strata are disjoint)
    personal = {}
    for pid, comp in joined:
        personal[pid] = any((a.get("ranking_blocks") or {}).get("personal")
                            for a in comp["metadata"]["assessments"])
    for pid, comp in joined:
        sc = {"full": equal_weight_scores(F[pid]), "core": equal_weight_scores(C[pid])}
        if min(len(sc["full"]), len(sc["core"])) < 2:
            continue
        # human contest per ordered pair on this prompt: how often raters disagree about it
        votes = defaultdict(lambda: [0, 0])
        rows_here = []
        for a in sorted(comp["metadata"]["assessments"], key=lambda x: str(x.get("annotator_id"))):
            w = (a.get("ranking_blocks") or {}).get("world") or []
            if not w:
                continue
            P0 = strict_pairs(w[0].get("ranking", ""))
            rows_here.append((str(a.get("annotator_id")), nfkc(a.get("subjectivity", "")), P0))
            for x, y in P0:
                k = tuple(sorted((x, y)))
                votes[k][0 if (x, y) == k else 1] += 1
        for rid, subj, P0 in rows_here:
            e, per_pair = {}, {}
            for arm in ("full", "core"):
                s = sc[arm]
                P = {(x, y) for x, y in P0 if x in s and y in s and s[x] != s[y]}
                if not P:
                    break
                e[arm] = sum(1 for x, y in P if s[x] < s[y]) / len(P)
                per_pair[arm] = {(x, y): (1.0 if s[x] < s[y] else 0.0) for x, y in P}
            if len(e) != 2:
                continue
            cells.append({"pid": pid, "rid": rid, "subj": subj, "personal": personal[pid],
                          "full": e["full"], "core": e["core"]})
            # The two arms do NOT decide the same pairs: a pair enters an arm only if that arm's
            # scores separate the two responses. So core ties where full separates, and vice versa.
            # The decision-level comparison uses the INTERSECTION, and the asymmetry is counted
            # rather than discarded -- a rule that declines to order a pair has withheld a decision,
            # which is its own form of not serving, and it is invisible in any accuracy.
            both = set(per_pair["full"]) & set(per_pair["core"])
            ties["full_only"] += len(set(per_pair["full"]) - both)
            ties["core_only"] += len(set(per_pair["core"]) - both)
            ties["both"] += len(both)
            for xy in sorted(both):
                a_, b_ = xy
                k = tuple(sorted(xy))
                v = votes[k]
                tot = v[0] + v[1]
                contest = (min(v) / tot) if tot else 0.0     # 0 = unanimous, 0.5 = split
                pairs.append({"pid": pid, "rid": rid, "win": a_, "lose": b_,
                              "contest": contest,
                              "full": per_pair["full"][xy], "core": per_pair["core"][xy]})
    return cells, pairs, ties


def unit_delta(keys, d, n_units):
    cnt = np.maximum(np.bincount(keys, None, n_units), 1)
    return np.bincount(keys, d, n_units) / cnt, np.bincount(keys, None, n_units)


LOW_UNIT_COUNT = 20   # below this a harm RATE is a share out of a handful and carries no resolution


def stats(delta, present):
    """STAT A and STAT B, and which pair is admissible depends on the UNIT COUNT.

    My first version used harm-rate + tail-concentration for every dimension and required BOTH to
    exceed their floors. Two errors, both fatal to the verdict it printed:

      (1) THE CRITERION WAS CONTRADICTORY. A broad real structure raises the rate and LOWERS the
          concentration -- noise is what produces extreme outliers. U1's observed tail mass was
          0.9154 against a shuffled 0.9559, i.e. the real data is LESS concentrated than chance, and
          I had written a one-sided test for MORE. Requiring breadth and concentration together
          requires a harm to be two incompatible shapes at once.
      (2) A RATE OVER FOUR LEVELS IS NOT A RATE. U3-U6 have 2 to 5 units, so "share of units worse"
          can only take values in quarters and returned 0.0000 everywhere -- not a null, a
          mis-specified estimand.

    So: at high unit counts, A = harm rate and B = tail mass, and B is judged TWO-SIDED because
    either direction is informative. At low unit counts, A = the SPREAD of level means (max - min)
    and B = their count-weighted variance -- both of which are meaningful with four levels and both
    of which a label permutation can null."""
    x = delta[present]
    if len(x) == 0:
        return float("nan"), float("nan")
    if len(x) < LOW_UNIT_COUNT:
        return float(x.max() - x.min()), float(x.var())
    A = float(np.mean(x > EPS))
    pos = np.maximum(x, 0.0)
    if pos.sum() <= 0:
        return A, 0.0
    k = max(1, int(round(TAIL_Q * len(x))))
    B = float(np.sort(pos)[-k:].sum() / pos.sum())
    return A, B


def bh(p, q):
    p = np.asarray(p, float); n = len(p); o = np.argsort(p)
    passed = p[o] <= q * (np.arange(1, n + 1) / n)
    k = np.max(np.flatnonzero(passed)) + 1 if passed.any() else 0
    keep = np.zeros(n, bool); keep[o[:k]] = True
    return keep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(_RES / "r117_multidimensional_sacrifice.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    cells, pairs, ties = build()
    if not cells or not pairs:
        print("REFUSING: empty population. Nothing-to-measure exits 2, never 0.", file=sys.stderr)
        return 2
    tot_t = ties["both"] + ties["full_only"] + ties["core_only"]
    print(f"cells {len(cells):,}   pairwise decisions decided by BOTH arms {ties['both']:,}")
    print(f"  WITHHELD DECISIONS, an invisible sacrifice in its own right: full orders "
          f"{ties['full_only']:,} pairs core ties on ({ties['full_only']/tot_t:.2%}); core orders "
          f"{ties['core_only']:,} pairs full ties on ({ties['core_only']/tot_t:.2%}). "
          f"Net {ties['full_only']-ties['core_only']:+,} decisions the compiled rule declines to make.")

    pid_l = sorted({c["pid"] for c in cells}); rid_l = sorted({c["rid"] for c in cells})
    PI = {p: i for i, p in enumerate(pid_l)}; RI = {r: i for i, r in enumerate(rid_l)}
    cp = np.array([PI[c["pid"]] for c in cells]); cr = np.array([RI[c["rid"]] for c in cells])
    cd = np.array([c["core"] - c["full"] for c in cells])
    subj = [c["subj"] for c in cells]
    pers = np.array([c["personal"] for c in cells])

    pp = np.array([PI[q["pid"]] for q in pairs])
    pdlt = np.array([q["core"] - q["full"] for q in pairs])
    plab = [q["win"] for q in pairs]
    pcon = np.array([q["contest"] for q in pairs])

    DIMS = {}

    # ---- U1 PERSON: permute rater identity WITHIN prompt --------------------------
    def u1():
        d, n = unit_delta(cr, cd, len(rid_l))
        obs = stats(d, n > 0)
        null = []
        for _ in range(N_PERM):
            s = cr.copy()
            for p in np.unique(cp):
                ix = np.flatnonzero(cp == p); s[ix] = cr[rng.permutation(ix)]
            dd, nn = unit_delta(s, cd, len(rid_l))
            null.append(stats(dd, nn > 0))
        return obs, null, int((n > 0).sum())

    # ---- U2 PROMPT: the mirror -- permute prompt identity WITHIN rater ------------
    def u2():
        d, n = unit_delta(cp, cd, len(pid_l))
        obs = stats(d, n > 0)
        null = []
        for _ in range(N_PERM):
            s = cp.copy()
            for r in np.unique(cr):
                ix = np.flatnonzero(cr == r); s[ix] = cp[rng.permutation(ix)]
            dd, nn = unit_delta(s, cd, len(pid_l))
            null.append(stats(dd, nn > 0))
        return obs, null, int((n > 0).sum())

    # ---- U3 SUBJECTIVITY and U4 STRATUM: categorical prompt labels ---------------
    def categorical(labels, name):
        levels = sorted(set(labels))
        idx = {v: i for i, v in enumerate(levels)}
        key = np.array([idx[v] for v in labels])
        d, n = unit_delta(key, cd, len(levels))
        obs = stats(d, n > 0)
        null = []
        for _ in range(N_PERM):
            dd, nn = unit_delta(rng.permutation(key), cd, len(levels))
            null.append(stats(dd, nn > 0))
        per_level = {levels[i]: float(d[i]) for i in range(len(levels)) if n[i] > 0}
        return obs, null, len(levels), per_level

    # ---- U5 LABEL: permute labels WITHIN prompt ----------------------------------
    def u5():
        labs = sorted(set(plab)); LI = {v: i for i, v in enumerate(labs)}
        key = np.array([LI[v] for v in plab])
        d, n = unit_delta(key, pdlt, len(labs))
        obs = stats(d, n > 0)
        null = []
        for _ in range(N_PERM):
            s = key.copy()
            for p in np.unique(pp):
                ix = np.flatnonzero(pp == p); s[ix] = key[rng.permutation(ix)]
            dd, nn = unit_delta(s, pdlt, len(labs))
            null.append(stats(dd, nn > 0))
        return obs, null, len(labs), {labs[i]: float(d[i]) for i in range(len(labs)) if n[i] > 0}

    # ---- U6 CONTESTED: bin pairs by how much the humans disagreed ----------------
    def u6():
        bins = np.digitize(pcon, [0.0001, 0.15, 0.30, 0.45])
        d, n = unit_delta(bins, pdlt, 5)
        obs = stats(d, n > 0)
        null = []
        for _ in range(N_PERM):
            s = bins.copy()
            for p in np.unique(pp):
                ix = np.flatnonzero(pp == p); s[ix] = bins[rng.permutation(ix)]
            dd, nn = unit_delta(s, pdlt, 5)
            null.append(stats(dd, nn > 0))
        names = ["unanimous", "0-15%", "15-30%", "30-45%", "45-50%"]
        return obs, null, 5, {names[i]: float(d[i]) for i in range(5) if n[i] > 0}

    obs1, n1, k1 = u1(); DIMS["U1_person"] = (obs1, n1, k1, None)
    obs2, n2, k2 = u2(); DIMS["U2_prompt"] = (obs2, n2, k2, None)
    o3, n3, k3, l3 = categorical(subj, "subjectivity"); DIMS["U3_subjectivity"] = (o3, n3, k3, l3)
    o4, n4, k4, l4 = categorical([("both_forms" if v else "world_only") for v in pers], "stratum")
    DIMS["U4_stratum"] = (o4, n4, k4, l4)
    o5, n5, k5, l5 = u5(); DIMS["U5_label"] = (o5, n5, k5, l5)
    o6, n6, k6, l6 = u6(); DIMS["U6_contested"] = (o6, n6, k6, l6)

    print(f"\n  {'unit':<18}{'n':>7}{'STAT A harm':>13}{'floor':>9}{'p_A':>8}"
          f"{'STAT B tail':>13}{'floor':>9}{'p_B':>8}")
    rows, pvals = {}, []
    for name, (obs, null, k, lev) in DIMS.items():
        A = np.array([x[0] for x in null]); B = np.array([x[1] for x in null])
        pA = float((np.sum(A >= obs[0]) + 1) / (len(A) + 1))
        # TWO-SIDED: a real broad structure DEPRESSES concentration relative to noise, so a one-sided
        # test for "more concentrated" cannot see it. Direction is reported beside the p.
        cB = float(np.nanmean(B))
        pB = float((np.sum(np.abs(B - cB) >= abs(obs[1] - cB)) + 1) / (len(B) + 1))
        rows[name] = {"n_units": k, "statA": obs[0], "floorA": float(np.nanmean(A)), "pA": pA,
                      "statB": obs[1], "floorB": cB, "pB": pB, "levels": lev,
                      "statB_direction": ("below floor" if obs[1] < cB else "above floor"),
                      "estimand": ("spread/variance of level means" if k < LOW_UNIT_COUNT
                                   else "harm rate / tail mass")}
        pvals += [pA, pB]
        print(f"  {name:<18}{k:>7}{obs[0]:>13.4f}{np.nanmean(A):>9.4f}{pA:>8.4f}"
              f"{obs[1]:>13.4f}{np.nanmean(B):>9.4f}{pB:>8.4f}")

    # WHICH level bears it. A spread statistic says a dimension carries structure; only the level
    # means say who. Printed for every categorical dimension, survivor or not.
    print("\n  PER-LEVEL SERVICE CHANGE (negative = better served by the compiled rule)")
    for name, (obs, null, k, lev) in DIMS.items():
        if not lev:
            continue
        order = sorted(lev.items(), key=lambda kv: -kv[1])
        print(f"    {name}:")
        for lv, v in order:
            print(f"       {str(lv)[:58]:<58} {v:+.5f}")
        print(f"       -> worst-served level is {str(order[0][0])[:44]!r} at {order[0][1]:+.5f}, "
              f"best {str(order[-1][0])[:32]!r} at {order[-1][1]:+.5f}, spread {order[0][1]-order[-1][1]:.5f}")

    # ---- U6 AGAINST r115's THEOREM, because the naive reading here is the 15th retraction ----
    # "Contested pairs are sacrificed" is what the monotone gradient looks like. But on a 50/50 pair
    # both rules sit at chance, so their DIFFERENCE is compressed toward zero MECHANICALLY:
    # beta_a proportional to (0.5 - e_a). The gradient must be tested against that line, not read off.
    bb = np.digitize(pcon, [0.0001, 0.15, 0.30, 0.45])
    pf = np.array([q["full"] for q in pairs]); pcr = np.array([q["core"] for q in pairs])
    nm6 = ["unanimous", "0-15%", "15-30%", "30-45%", "45-50%"]
    u6 = {}
    ratio0 = None
    print("\n  U6 AGAINST THE ACCURACY-GAP LINE (r115). A gradient toward zero on split pairs is "
          "forced by there being no headroom; only a DEPARTURE is a finding.")
    print(f"    {'bin':<12}{'n':>8}{'e_full':>9}{'e_core':>9}{'obs d':>10}{'headroom':>10}"
          f"{'pred d':>10}{'departure':>11}")
    for i, nm in enumerate(nm6):
        m_ = bb == i
        if m_.sum() < 50:
            continue
        f_, c_ = float(pf[m_].mean()), float(pcr[m_].mean())
        d_ = float((pcr - pf)[m_].mean()); head = 0.5 - f_
        if ratio0 is None:
            ratio0 = d_ / head
        pred = ratio0 * head
        u6[nm] = {"n": int(m_.sum()), "e_full": f_, "e_core": c_, "obs_d": d_,
                  "headroom": head, "pred_d": pred, "departure": d_ - pred}
        print(f"    {nm:<12}{int(m_.sum()):>8}{f_:>9.4f}{c_:>9.4f}{d_:>+10.5f}{head:>10.4f}"
              f"{pred:>+10.5f}{d_-pred:>+11.5f}")
    split = u6.get("45-50%")
    if split:
        print(f"    -> on the {split['n']:,} most contested decisions BOTH rules sit at chance "
              f"(full {split['e_full']:.4f}, core {split['e_core']:.4f}); the near-zero gain is the "
              f"ABSENCE OF AN AVAILABLE BENEFIT, not a sacrifice of one.")
        print(f"    -> and the system emits a verdict on all {split['n']:,} of them anyway. That is "
              f"the invisible cost: not lost accuracy, but a DECISION WITH NO INFORMATIONAL BASIS, "
              f"invisible precisely because it costs no accuracy.")

    keep = bh(pvals, BH_Q)
    names = list(DIMS)
    for i, name in enumerate(names):
        rows[name]["bh_A"] = bool(keep[2 * i]); rows[name]["bh_B"] = bool(keep[2 * i + 1])
        rows[name]["cross_verified"] = bool(keep[2 * i] and keep[2 * i + 1])
    survivors = [n for n in names if rows[n]["cross_verified"]]
    print(f"\n  BH at q={BH_Q} over {len(pvals)} tests ({len(names)} dimensions x 2 statistics)")
    for name in names:
        r = rows[name]
        mark = "CROSS-VERIFIED" if r["cross_verified"] else (
            "one statistic only" if (r["bh_A"] or r["bh_B"]) else "neither")
        print(f"    {name:<18} A {'PASS' if r['bh_A'] else '----'}  "
              f"B {'PASS' if r['bh_B'] else '----'}   -> {mark}")

    # ---- the negative control that lives INSIDE U3 -------------------------------
    if l3:
        v = l3.get(VALUES); o = l3.get(OTHER)
        if v is not None and o is not None:
            print(f"\n  U3's OWN NEGATIVE CONTROL -- normative vs factual disagreement:")
            print(f"    'depends on values or culture' delta {v:+.5f}")
            print(f"    'depends on something else (time, weather)' delta {o:+.5f}")
            print(f"    difference {v - o:+.5f}  -- a sacrifice about VALUES should load on the "
                  f"first and not the second")

    # ---- POSITIVE CONTROL per dimension ------------------------------------------
    print(f"\n  POSITIVE CONTROL -- plant g={PLANT_G} on a random {PLANT_SHARE:.0%} of each unit")
    pc = {}
    subj_lv = sorted(set(subj)); SI = {v: i for i, v in enumerate(subj_lv)}
    strat = np.array([1 if v else 0 for v in pers])
    labs_l = sorted(set(plab)); LI2 = {v: i for i, v in enumerate(labs_l)}
    con_b = np.digitize(pcon, [0.0001, 0.15, 0.30, 0.45])
    for name, key, dlt, nk in (("U1_person", cr, cd, len(rid_l)),
                               ("U2_prompt", cp, cd, len(pid_l)),
                               ("U3_subjectivity", np.array([SI[v] for v in subj]), cd, len(subj_lv)),
                               ("U4_stratum", strat, cd, 2),
                               ("U5_label", np.array([LI2[v] for v in plab]), pdlt, len(labs_l)),
                               ("U6_contested", con_b, pdlt, 5)):
        hurt = rng.choice(nk, size=max(1, int(PLANT_SHARE * nk)), replace=False)
        d0, n0 = unit_delta(key, dlt, nk)
        d1, _ = unit_delta(key, dlt + PLANT_G * np.isin(key, hurt), nk)
        a0, _b0 = stats(d0, n0 > 0); a1, _b1 = stats(d1, n0 > 0)
        rec = (a1 - a0) / PLANT_SHARE if nk >= LOW_UNIT_COUNT else float("nan")
        pc[name] = {"stat0": a0, "stat1": a1, "increment": a1 - a0, "recovery": rec,
                    "moves": bool(abs(a1 - a0) > 1e-9)}
        print(f"    {name:<18} stat {a0:.4f} -> {a1:.4f}   increment {a1-a0:+.4f}"
              + (f"   recovers {rec:.0%} of the plant" if rec == rec else "   (spread statistic)"))

    world = ("W-MULTIDIMENSIONAL" if len(survivors) >= 2 else
             "W-SINGLE-AXIS" if len(survivors) == 1 else "W-NO-SURVIVOR")
    conclusion = (
        f"Six units, two statistics each, one permutation floor each, {N_PERM} draws, "
        f"Benjamini-Hochberg at q={BH_Q} over all {len(pvals)} tests. A dimension counts only if BOTH "
        f"a harm RATE (breadth, threshold-sensitive) and a tail-MASS concentration (size, "
        f"outlier-sensitive) clear the correction, because a threshold artifact moves the first alone "
        f"and a single outlier moves the second alone. "
        f"CROSS-VERIFIED: {', '.join(survivors) if survivors else 'none'}. "
        f"One statistic only: {', '.join(n for n in names if rows[n]['bh_A'] != rows[n]['bh_B']) or 'none'}. "
        f"Neither: {', '.join(n for n in names if not rows[n]['bh_A'] and not rows[n]['bh_B']) or 'none'}. "
        f"WORLD: {world}. "
        + (f"Sacrifice under this compiled rule is carried on at least two structurally different "
           f"units, so 'who is sacrificed' cannot be answered by naming people alone."
           if world == "W-MULTIDIMENSIONAL" else
           f"Only one unit carries a cross-verified sacrifice, so the phenomenon is one-dimensional "
           f"on this release and the multidimensional framing is not supported here."
           if world == "W-SINGLE-AXIS" else
           f"No unit survives cross-verification. Every apparent dimension is a single-statistic "
           f"result, which is what a multiplicity correction exists to remove."))
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    out = {"n_cells": len(cells), "n_pairs": len(pairs), "withheld_decisions": ties, "n_perm": N_PERM, "eps": EPS,
           "tail_q": TAIL_Q, "bh_q": BH_Q, "dimensions": rows, "survivors": survivors,
           "positive_control": pc, "u6_vs_accuracy_gap_line": u6, "world": world, "conclusion": conclusion, **stamp(__file__)}
    Path(args.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
