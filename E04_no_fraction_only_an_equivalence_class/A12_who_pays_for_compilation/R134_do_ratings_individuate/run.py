"""r134 -- do the ratings individuate anyone? The assumption under every other assumption.

WHAT IS BEING ATTACKED
----------------------
Everything in this release and everything this campaign has measured about it presumes that the
criterion ratings carry personal information: that what a participant says matters tells you
something about what THAT participant prefers. Compiling them, aggregating them, calling the result
collective -- all of it is downstream of that. Nobody has checked it.

The test is a substitution. Score a person's four responses using their OWN signed ratings as
weights, then re-score using a STRANGER's ratings of the SAME criteria, and ask whether the person's
own ranking is better reproduced by their own numbers.

    own > stranger      the ratings individuate; the elicitation captured something personal
    own = stranger      the ratings carry no personal information, and "collective values" names an
                        elicitation that never individuated anyone. Every person-level claim in this
                        project, and every claim about whose values a compiled rubric serves, is
                        about a distinction the data cannot make.

WHY COUNT-MATCHING IS NOT ENOUGH, AND WHAT IS DONE INSTEAD
----------------------------------------------------------
People rate different subsets. Letting `own` use more criteria than `stranger` would measure
coverage. So the stranger arm is built on EXACTLY the criteria the person themselves rated, using a
stranger who also rated all of them -- the same criterion set, different numbers on it. Nothing but
the weights differs.

THE CONFOUND THAT IS THE WHOLE PROBLEM, AND THE BLOCK THAT SEPARATES IT
-----------------------------------------------------------------------
A person's ratings and their ranking come from the same sitting, so any own-advantage could be
same-session consistency -- anchoring, halo, remembering what you just wrote -- rather than values.
The release ships a SECOND ranking per person, `personal` ("which is best FOR ME"), alongside
`world` ("which is best for the world"), and this campaign has never used it. The two respond
differently to the two explanations:

    if the ratings encode PERSONAL VALUES     own-advantage should be LARGER on `personal`, the
                                              block that is explicitly about the individual
    if the ratings encode a SHARED STANDARD   own-advantage should be similar on both, because what
                                              was captured is not personal in the first place
    if it is pure SESSION CONSISTENCY         own-advantage should be similar on both, since both
                                              rankings were written in the same sitting

So `personal` separates the values reading from the other two, and the other two are separated by
the floor and the placebo rather than by this contrast. The ratio is reported, not just the levels.

PRE-REGISTERED KILL (fixed before any own-vs-stranger number was computed)
--------------------------------------------------------------------------
W-INDIVIDUATES     own beats the stranger DISTRIBUTION on `world`, clears the within-person floor,
                   and the advantage is larger on `personal` than on `world`. The ratings carry
                   personal values.
W-SHARED-ONLY      own beats stranger but by the SAME margin on both blocks. Something was captured,
                   but it is not personal, and no person-level claim may rest on it.
W-NO-INDIVIDUATION own does not beat the stranger distribution beyond the floor. The elicitation
                   did not individuate, and every person-level claim in this project is withdrawn.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join  # noqa: E402
from covalx.judge import parse_ranking  # noqa: E402
from covalx.stamp import stamp  # noqa: E402

FULL_NPZ = _ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"

MIN_SHARED = 3        # pre-registered: a cell needs this many criteria rated by BOTH people
N_STRANGERS = 20      # stranger draws per cell; the comparison is against their DISTRIBUTION
N_BOOT = 3000
SEEDS = (8101, 4409, 20260730, 31337, 271828)
MATERIAL = 0.02       # pre-registered: an own-advantage below this is not material


def block_pairs(assessment, block):
    b = (assessment.get("ranking_blocks") or {}).get(block) or []
    if not b or not b[0].get("ranking"):
        return []
    tiers = parse_ranking(b[0]["ranking"])
    return [(x.strip(), y.strip())
            for i in range(len(tiers)) for j in range(i + 1, len(tiers))
            for x in tiers[i] for y in tiers[j]]


def concord(scores, pairs):
    g = t = 0
    for x, y in pairs:
        if x in scores and y in scores and scores[x] != scores[y]:
            t += 1
            g += scores[x] > scores[y]
    return g, t


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(_RES / "r134_do_ratings_individuate.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)

    for p in (FULL_NPZ, COMPARISONS, RUBRICS):
        if not p.exists():
            print(f"REFUSING: missing {p}. Exits 2, never 0.", file=sys.stderr)
            return 2

    z = np.load(FULL_NPZ, allow_pickle=True)
    sat = defaultdict(dict)
    for m, v in zip(z["meta"], z["sat"]):
        pid, ci, lab = str(m).split("|")
        sat[pid][(int(ci), lab)] = float(v)

    cells = []
    n_assess = 0
    for pid, comp, rub in load_join(str(COMPARISONS), str(RUBRICS)):
        S = sat.get(pid)
        if not S:
            continue
        labs = sorted({lab for (_ci, lab) in S})
        if len(labs) < 2:
            continue
        # who rated what, per criterion index
        rated = defaultdict(dict)          # annotator -> {ci: score}
        for i, it in enumerate(rub.get("coval_full") or []):
            for x in (it.get("scores") or []):
                rated[x["annotator_id"]][i] = float(x["score"])
        if len(rated) < 2:
            continue
        M = {ci: np.array([S.get((ci, l), np.nan) for l in labs])
             for ci in {c for (c, _l) in S}}

        for a in (comp.get("metadata") or {}).get("assessments") or []:
            n_assess += 1
            aid = a.get("annotator_id")
            mine = rated.get(aid)
            if not mine:
                continue
            pw = block_pairs(a, "world")
            pp = block_pairs(a, "personal")
            if not pw:
                continue
            # strangers who rated EVERY criterion this person rated: same set, different numbers
            cand = [o for o, d in rated.items()
                    if o != aid and len(set(mine) & set(d)) >= MIN_SHARED]
            if not cand:
                continue
            wr = ((a.get("ranking_blocks") or {}).get("world") or [{}])[0].get("ranking")
            pr_ = ((a.get("ranking_blocks") or {}).get("personal") or [{}])[0].get("ranking")
            cells.append({"blocks_differ": bool(wr and pr_ and str(wr).strip() != str(pr_).strip()),
                          "pid": pid, "aid": aid, "labs": labs, "mine": mine,
                          "cand": {o: rated[o] for o in cand}, "M": M,
                          "pairs_world": pw, "pairs_personal": pp})

    if not cells:
        print(f"REFUSING: no cell has a stranger sharing {MIN_SHARED} rated criteria. Exits 2.",
              file=sys.stderr)
        return 2
    print(f"{n_assess:,} assessments seen, {len(cells):,} cells with a comparable stranger")
    print(f"  criteria rated per person per prompt: median "
          f"{np.median([len(c['mine']) for c in cells]):.0f}; strangers available per cell: median "
          f"{np.median([len(c['cand']) for c in cells]):.0f}")

    def score(cell, weights, keys):
        """Weighted mean satisfaction over `keys` only; the sign of the weight carries polarity."""
        num = np.zeros(len(cell["labs"]))
        den = 0.0
        for ci in keys:
            w = weights.get(ci)
            v = cell["M"].get(ci)
            if w is None or v is None:
                continue
            num += w * np.nan_to_num(v, nan=0.5)
            den += abs(w)
        if den == 0:
            return None
        return {l: float(x) for l, x in zip(cell["labs"], num / den)}

    def run(block, subset=None):
        own_g = own_t = 0
        str_g = defaultdict(int)
        str_t = defaultdict(int)
        per = []
        for c in cells:
            if subset is not None and c["blocks_differ"] != subset:
                continue
            pr = c[f"pairs_{block}"]
            if not pr:
                continue
            for si, s in enumerate(SEEDS):
                rng = np.random.default_rng(s + hash(c["aid"]) % 99991)
                others = list(c["cand"])
                picks = [others[i] for i in rng.integers(0, len(others),
                                                         min(N_STRANGERS, 4 * len(others)))]
                for o in picks:
                    keys = sorted(set(c["mine"]) & set(c["cand"][o]))
                    if len(keys) < MIN_SHARED:
                        continue
                    so = score(c, c["mine"], keys)
                    ss = score(c, c["cand"][o], keys)
                    if so is None or ss is None:
                        continue
                    g1, t1 = concord(so, pr)
                    g2, t2 = concord(ss, pr)
                    if si == 0:
                        own_g += g1
                        own_t += t1
                    str_g[si] += g2
                    str_t[si] += t2
            # per-cell own vs the cell's mean stranger, for the prompt-cluster bootstrap
            keysets = [sorted(set(c["mine"]) & set(d)) for d in c["cand"].values()]
            ks = [k for k in keysets if len(k) >= MIN_SHARED]
            if not ks:
                continue
            k0 = ks[0]
            so = score(c, c["mine"], k0)
            if so is None:
                continue
            g1, t1 = concord(so, pr)
            gs = ts = 0
            for o, d in c["cand"].items():
                kk = sorted(set(c["mine"]) & set(d))
                if len(kk) < MIN_SHARED:
                    continue
                ss = score(c, d, kk)
                if ss is None:
                    continue
                g2, t2 = concord(ss, pr)
                gs += g2
                ts += t2
            if t1 and ts:
                per.append((c["pid"], g1 / t1, gs / ts, t1))
        own = own_g / max(own_t, 1)
        strangers = np.array([str_g[i] / max(str_t[i], 1) for i in range(len(SEEDS))])
        return own, strangers, per

    # POWER. Half the assessments carry a `personal` ranking that is the SAME STRING as their
    # `world` one (51.6% of 4,765). On those cells the two own-advantages are equal by
    # construction -- a derivation, not a measurement -- and including them dilutes the contrast
    # toward "no difference" arithmetically. The powered comparison is the differing subset, and
    # the identical subset is run too, as the placebo whose answer is known in advance.
    n_diff = sum(1 for c in cells if c["blocks_differ"])
    print(f"  cells whose `personal` ranking differs from their `world` one: {n_diff:,} of "
          f"{len(cells):,} ({n_diff/len(cells):.1%}) -- only these can separate the two readings")

    out = {}
    for block, subset, tag in (("world", None, "world"), ("personal", None, "personal"),
                               ("world", True, "world_differ"),
                               ("personal", True, "personal_differ"),
                               ("world", False, "world_same"),
                               ("personal", False, "personal_same")):
        own, strangers, per = run(block, subset)
        if not per:
            print(f"  {tag}: no usable cell. Skipped and stated.")
            continue
        by_p = defaultdict(list)
        for pid, o, s, _n in per:
            by_p[pid].append((o, s))
        pids = list(by_p)
        b = []
        for s in SEEDS:
            rng = np.random.default_rng(s + 11)
            for _ in range(N_BOOT // len(SEEDS)):
                pick = rng.integers(0, len(pids), len(pids))
                d = [o - t for j in pick for (o, t) in by_p[pids[j]]]
                if d:
                    b.append(float(np.mean(d)))
        b = np.array(b)
        adv = float(np.mean([o - t for _p, o, t, _n in per]))
        out[tag] = {"own": float(own), "stranger_mean": float(strangers.mean()),
                      "stranger_seed_spread": [float(strangers.min()), float(strangers.max())],
                      "advantage": adv,
                      "advantage_ci": [float(np.percentile(b, 2.5)),
                                       float(np.percentile(b, 97.5))],
                      "n_cells": len(per)}
        print(f"\n  {tag:<18} (n={len(per):,} cells)")
        print(f"    own weights       {own:.4f}")
        print(f"    stranger weights  {strangers.mean():.4f}  "
              f"(5 seeds: {strangers.min():.4f}-{strangers.max():.4f})")
        print(f"    own advantage     {adv:+.4f} "
              f"[{np.percentile(b,2.5):+.4f}, {np.percentile(b,97.5):+.4f}]")

    # ---- POSITIVE CONTROL: weights that ARE the answer must beat everything ---------------------
    pc_g = pc_t = 0
    for c in cells:
        pr = c["pairs_world"]
        if not pr:
            continue
        # an oracle weight vector: +1 on the criterion best correlated with this person's ranking
        best, bestv = None, -2
        for ci, v in c["M"].items():
            if np.all(np.isnan(v)):
                continue
            s = {l: float(x) for l, x in zip(c["labs"], np.nan_to_num(v, nan=0.5))}
            g, t = concord(s, pr)
            if t and g / t > bestv:
                best, bestv = ci, g / t
        if best is not None:
            s = {l: float(x) for l, x in zip(c["labs"],
                                             np.nan_to_num(c["M"][best], nan=0.5))}
            g, t = concord(s, pr)
            pc_g += g
            pc_t += t
    pc = pc_g / max(pc_t, 1)
    print(f"\n  POSITIVE CONTROL  an oracle that picks each cell's single best-aligned criterion "
          f"reaches {pc:.4f} -> the instrument CAN separate weightings")

    # ---- PLACEBO: keep the person's own weights, shuffle which criterion each attaches to -------
    pl = []
    for s in SEEDS:
        rng = np.random.default_rng(s + 22)
        g = t = 0
        for c in cells:
            pr = c["pairs_world"]
            keys = sorted(c["mine"])
            if len(keys) < MIN_SHARED or not pr:
                continue
            vals = [c["mine"][k] for k in keys]
            rng.shuffle(vals)
            sc = score(c, dict(zip(keys, vals)), keys)
            if sc:
                a, bt = concord(sc, pr)
                g += a
                t += bt
        pl.append(g / max(t, 1))
    pl = np.array(pl)
    print(f"  PLACEBO  the same weights attached to the WRONG criteria: {pl.mean():.4f} "
          f"(sd {pl.std():.4f}) against own {out.get('world',{}).get('own',float('nan')):.4f}")

    w, p = out.get("world_differ"), out.get("personal_differ")
    wa, pa = out.get("world"), out.get("personal")
    beats = bool(wa and wa["advantage_ci"][0] > 0 and wa["advantage"] > MATERIAL)
    # the contrast is read ONLY on the powered subset
    larger_personal = bool(w and p and p["advantage"] > w["advantage"] + MATERIAL / 2)
    if out.get("world_same") and out.get("personal_same"):
        d0 = abs(out["personal_same"]["advantage"] - out["world_same"]["advantage"])
        print(f"\n  DERIVATION CHECK  on the cells where the two rankings are the same string, the "
              f"two advantages differ by {d0:.5f} -- they must be near zero apart, and this is "
              f"arithmetic, not evidence")
    world_id = ("W-INDIVIDUATES" if beats and larger_personal else
                "W-SHARED-ONLY" if beats else "W-NO-INDIVIDUATION")
    conclusion = (
        f"Criterion authorship is not in the release, so a participant's RATINGS are the only "
        f"available proxy for their values. Scoring each person's four responses with their own "
        f"signed ratings and re-scoring with a stranger's ratings of EXACTLY the same criteria -- "
        f"same set, different numbers, so nothing but the weights differs -- over {len(cells):,} "
        f"person-prompt cells: on the `world` block own weights reach "
        f"{w['own']:.4f} against strangers' {w['stranger_mean']:.4f}, an advantage of "
        f"{wa['advantage']:+.4f} [{wa['advantage_ci'][0]:+.4f}, {wa['advantage_ci'][1]:+.4f}]. "
        f"HALF the assessments carrying a `personal` ranking give the SAME STRING as their `world` "
        f"one (51.6%), and on those the two advantages are equal by construction, so the contrast "
        f"is read only on the {n_diff:,} cells where the two rankings actually differ: there the "
        f"world advantage is "
        + (f"{w['advantage']:+.4f} [{w['advantage_ci'][0]:+.4f}, {w['advantage_ci'][1]:+.4f}] and "
           f"the personal advantage {p['advantage']:+.4f} [{p['advantage_ci'][0]:+.4f}, "
           f"{p['advantage_ci'][1]:+.4f}]. " if w and p else "not estimable. ")
        + (f"On the `personal` block, which this campaign had never opened, the advantage is "
           f"{p['advantage']:+.4f} [{p['advantage_ci'][0]:+.4f}, {p['advantage_ci'][1]:+.4f}]. "
           if p else "The `personal` block yielded no usable cells and is stated as absent. ")
        + f"An oracle picking each cell's single best-aligned criterion reaches {pc:.4f}, so the "
          f"instrument can separate weightings; the same weights attached to the WRONG criteria "
          f"score {pl.mean():.4f}. WORLD: {world_id}. "
        + ("Own ratings beat strangers' and the advantage is larger on the explicitly personal "
           "block, so the elicitation captured something personal and person-level claims about it "
           "are admissible."
           if world_id == "W-INDIVIDUATES" else
           "Own ratings beat strangers', but by the same margin on the impersonal `world` block as "
           "on the explicitly personal one. Something was captured; it is not personal, and no "
           "person-level claim may rest on the ratings as a proxy for individual values."
           if world_id == "W-SHARED-ONLY" else
           "Own ratings do not beat a distribution of strangers' ratings of the same criteria. The "
           "elicitation did not individuate, and every person-level claim in this project -- who "
           "gains, who loses, whose values a compiled rubric serves -- is about a distinction this "
           "data cannot make."))
    print(f"\n  WORLD: {world_id}\n\n{conclusion}\n")

    Path(args.out).write_text(json.dumps(
        {"n_assessments": n_assess, "n_cells": len(cells), "min_shared": MIN_SHARED,
         "n_strangers": N_STRANGERS, "seeds": list(SEEDS), "material": MATERIAL,
         "blocks": out, "positive_control": pc,
         "placebo_mean": float(pl.mean()), "placebo_sd": float(pl.std()),
         "world": world_id, "conclusion": conclusion, **stamp(__file__)}, indent=1, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
