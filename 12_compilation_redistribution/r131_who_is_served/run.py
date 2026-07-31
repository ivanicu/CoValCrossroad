"""r131 -- who is served by the compilation, person by person, against a within-person floor.

THE NORTH STAR, MADE MEASURABLE
-------------------------------
No Invisible Sacrifice. An aggregate concordance number is exactly the thing compilation optimises,
so it is the last place a loser would show up. The release gives every rating and every ranking an
`annotator_id` in one namespace, so the question can be asked at the level it matters:

    for each person, does the compiled arm reproduce THAT PERSON's own ranking better or worse
    than the uncompiled arm does?

THE MISTAKE THIS ROUND EXISTS TO NOT REPEAT
-------------------------------------------
Rounds r116-r119 measured exactly this and measured it against ONE full baseline -- the equal-weight
arm, which reads a criterion rated -10 as if satisfying it were good. r123 showed that convention
decides the sign of the whole comparison. So every arm here is computed against BOTH:

    full_equal    every criterion averaged as-is. Removes an advantage core cannot have, since
                  core carries no ratings at all.
    full_signed   criteria with a negative mean rating read as 1 - v. Grants full information core
                  structurally lacks.

Neither is "the" baseline. Reporting one is how the earlier rounds got a sign they did not earn.

THE FLOOR, WHICH IS THE POINT OF THE ROUND
------------------------------------------
A spread across people is not heterogeneity until it exceeds what the SAME person produces when you
resample their own prompts. So each person's prompt set is split in half at random and the identical
gain is computed on each half; the half-to-half spread is the resolution floor, and any claim about
who loses must clear it. Without that floor, "12% of people are harmed" is a statement about how
many prompts each person happened to see.

PRE-REGISTERED KILL (fixed before any per-person number was computed)
---------------------------------------------------------------------
W-UNIFORM       between-person spread does not exceed the within-person floor under either
                baseline. Compilation is a summary; there are no locatable losers, and every
                person-level sacrifice claim this project has made is withdrawn.
W-REDISTRIBUTES between-person spread exceeds the floor under BOTH baselines. Compilation moves
                accuracy between people, and the identity of the losers is a real question.
W-BASELINE-BOUND  the spread clears the floor under one baseline and not the other. The
                redistribution claim is conditional on a convention and must always be stated with it.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join  # noqa: E402
from covalx.judge import parse_ranking  # noqa: E402
from covalx.stamp import stamp  # noqa: E402

FULL_NPZ = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
CORE_NPZ = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"

MIN_PROMPTS = 4      # pre-registered: a person needs this many prompts before a split-half floor
                     # is even definable, and 4 is the smallest number that gives 2 per half
MIN_PAIRS = 8        # ... and this many ordered pairs, so a half is not one decision
N_SPLIT = 200        # random half-splits per person, for the within-person floor
N_BOOT = 2000        # two-way (person x prompt) cluster bootstrap
HARM_EPS = 0.01      # pre-registered: a person is HARMED if their gain is below -0.01, not below 0.
                     # A threshold at exactly 0 counts every coin-flip as a casualty.


def own_pairs(assessment):
    """One person's strict ordered pairs from their own world ranking. Ties dropped."""
    w = (assessment.get("ranking_blocks") or {}).get("world") or []
    if not w or not w[0].get("ranking"):
        return []
    tiers = parse_ranking(w[0]["ranking"])
    out = []
    for a in range(len(tiers)):
        for b in range(a + 1, len(tiers)):
            for x in tiers[a]:
                for y in tiers[b]:
                    out.append((x, y))
    return out


def load_sat(path):
    z = np.load(path, allow_pickle=True)
    d = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = str(m).split("|")
        d[pid][(int(ci), lab)] = float(s)
    return d


def concord(scores, pairs):
    """(agreements, comparable) for one arm against one person's pairs. Arm ties are not decisions."""
    good = tot = 0
    for x, y in pairs:
        if x in scores and y in scores and scores[x] != scores[y]:
            tot += 1
            good += scores[x] > scores[y]
    return good, tot


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260730)
    ap.add_argument("--out", default=str(_RES / "r131_who_is_served.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    for p in (FULL_NPZ, CORE_NPZ, COMPARISONS, RUBRICS):
        if not p.exists():
            print(f"REFUSING: missing {p}. Exits 2, never 0.", file=sys.stderr)
            return 2
    SAT_F, SAT_C = load_sat(FULL_NPZ), load_sat(CORE_NPZ)

    ratings = {}
    for line in open(RUBRICS):
        r = json.loads(line)
        cid = r["conversation"]["id"]
        for i, it in enumerate(r.get("coval_full") or []):
            s = [x["score"] for x in (it.get("scores") or [])]
            if s:
                ratings[(cid, i)] = float(np.mean(s))

    # cells[(person, prompt)][arm] = (agree, comparable)
    cells = defaultdict(dict)
    person_cov = defaultdict(lambda: defaultdict(list))
    for pid, comp, rub in load_join(str(COMPARISONS), str(RUBRICS)):
        if pid not in SAT_F or pid not in SAT_C:
            continue
        cid = rub["conversation"]["id"]
        labs = sorted({lab for (_ci, lab) in SAT_C[pid]})
        if len(labs) < 2:
            continue

        def arm(sat, use_sign):
            acc = {l: [] for l in labs}
            for (ci, lab), v in sat.items():
                if lab not in acc:
                    continue
                neg = use_sign and ratings.get((cid, ci), 0.0) < 0
                acc[lab].append(1.0 - v if neg else v)
            return {l: float(np.mean(v)) for l, v in acc.items() if v}

        arms = {"core": arm(SAT_C[pid], False),
                "full_equal": arm(SAT_F[pid], False),
                "full_signed": arm(SAT_F[pid], True)}
        for a in (comp.get("metadata") or {}).get("assessments") or []:
            aid = a.get("annotator_id")
            pr = own_pairs(a)
            if not aid or not pr:
                continue
            cells[(aid, pid)] = {k: concord(v, pr) for k, v in arms.items()}
            person_cov[aid]["subjectivity"].append(a.get("subjectivity") or "")
            person_cov[aid]["importance"].append(a.get("importance") or "")
            # how extreme this person's own ratings are, and how far from their peers'
            mine = [(x["score"], (cid, i))
                    for i, it in enumerate(rub.get("coval_full") or [])
                    for x in (it.get("scores") or []) if x.get("annotator_id") == aid]
            if mine:
                person_cov[aid]["abs_rating"].extend(abs(s) for s, _ in mine)
                person_cov[aid]["dev_from_mean"].extend(
                    abs(s - ratings[k]) for s, k in mine if k in ratings)
                person_cov[aid]["n_rated"].append(len(mine))

    by_person = defaultdict(list)
    for (aid, pid), d in cells.items():
        by_person[aid].append((pid, d))
    people = {a: v for a, v in by_person.items()
              if len(v) >= MIN_PROMPTS
              and sum(d["core"][1] for _p, d in v) >= MIN_PAIRS}
    if not people:
        print(f"REFUSING: no annotator has {MIN_PROMPTS} prompts and {MIN_PAIRS} comparable pairs. "
              f"A per-person statistic over an empty population is not a null. Exits 2.",
              file=sys.stderr)
        return 2
    print(f"{len(by_person)} annotators seen, {len(people)} with >= {MIN_PROMPTS} prompts and "
          f">= {MIN_PAIRS} pairs; {len(cells):,} person-prompt cells")

    def gain(rows, base):
        gc = tc = gb = tb = 0
        for _p, d in rows:
            a, b = d["core"], d[base]
            gc += a[0]; tc += a[1]
            gb += b[0]; tb += b[1]
        if not tc or not tb:
            return None
        return gc / tc - gb / tb

    out = {}
    for base in ("full_equal", "full_signed"):
        g = {a: gain(v, base) for a, v in people.items()}
        g = {a: v for a, v in g.items() if v is not None}
        vals = np.array(list(g.values()))

        # ---- the within-person floor: same statistic, this person's own prompts, split in half --
        floor = []
        for a, rows in people.items():
            if len(rows) < MIN_PROMPTS:
                continue
            d = []
            for s in range(N_SPLIT):
                r2 = np.random.default_rng(args.seed + 7000 + s)
                idx = r2.permutation(len(rows))
                h1 = [rows[i] for i in idx[: len(rows) // 2]]
                h2 = [rows[i] for i in idx[len(rows) // 2:]]
                x, y = gain(h1, base), gain(h2, base)
                if x is not None and y is not None:
                    d.append(x - y)
            if d:
                # sd of a half-gain is sd(difference)/sqrt(2); scale to the full-set n by /sqrt(2)
                floor.append(np.std(d) / 2.0)
        floor = np.array(floor)
        floor_sd = float(np.mean(floor)) if floor.size else float("nan")
        between_sd = float(vals.std(ddof=1))
        excess = float(np.sqrt(max(between_sd ** 2 - floor_sd ** 2, 0.0)))

        harmed = float((vals < -HARM_EPS).mean())
        helped = float((vals > HARM_EPS).mean())
        # the tail is the north star's actual object: the mean of the worst decile
        k = max(1, len(vals) // 10)
        cvar = float(np.sort(vals)[:k].mean())

        idx = rng.integers(0, len(vals), size=(N_BOOT, len(vals)))
        bm = vals[idx].mean(1)
        out[base] = {
            "n_people": len(vals), "mean_gain": float(vals.mean()),
            "mean_gain_ci": [float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))],
            "median_gain": float(np.median(vals)),
            "between_person_sd": between_sd, "within_person_floor_sd": floor_sd,
            "excess_sd_over_floor": excess,
            "spread_clears_floor": bool(between_sd > 1.5 * floor_sd),
            "harmed_share": harmed, "helped_share": helped,
            "worst_decile_mean_gain": cvar,
            "harm_eps": HARM_EPS,
        }
        print(f"\n  BASELINE {base}")
        print(f"    mean gain      {vals.mean():+.5f} "
              f"[{np.percentile(bm,2.5):+.5f}, {np.percentile(bm,97.5):+.5f}]")
        print(f"    median gain    {np.median(vals):+.5f}")
        print(f"    harmed (< -{HARM_EPS})  {harmed:.1%}     helped (> +{HARM_EPS})  {helped:.1%}")
        print(f"    worst decile mean gain  {cvar:+.5f}")
        print(f"    between-person sd {between_sd:.5f}  vs within-person floor {floor_sd:.5f}  "
              f"-> excess {excess:.5f}  ({'CLEARS' if between_sd > 1.5*floor_sd else 'DOES NOT CLEAR'})")

        # ---- do the losers share anything measurable? -----------------------------------------
        # STRONGEST CONFOUND on this sub-analysis, named before it ran: a person's gain is
        # estimated from however many prompts they happened to see, so people with MORE prompts
        # have a LESS noisy gain, shrunk toward the common mean. Any covariate that tracks
        # exposure -- and n_rated obviously does -- will then correlate with gain for a pure
        # noise-shrinkage reason and no substantive one. Every covariate correlation below is
        # therefore reported both raw and PARTIALLED on the person's prompt count, and only the
        # partial one may be read as structure.
        n_prompts = {a: float(len(people[a])) for a in g}

        def partial(xs, ys, zs):
            X = np.column_stack([np.asarray(zs, float), np.ones(len(zs))])
            rx = np.asarray(xs, float) - X @ np.linalg.lstsq(X, np.asarray(xs, float),
                                                            rcond=None)[0]
            ry = np.asarray(ys, float) - X @ np.linalg.lstsq(X, np.asarray(ys, float),
                                                            rcond=None)[0]
            return float(np.corrcoef(rx, ry)[0, 1]), rx, ry

        cov = {}
        for name in ("abs_rating", "dev_from_mean", "n_rated"):
            xs, ys, zs = [], [], []
            for a, v in g.items():
                c = person_cov[a].get(name) or []
                if c:
                    xs.append(float(np.mean(c)))
                    ys.append(v)
                    zs.append(n_prompts[a])
            if len(xs) > 10:
                r = float(np.corrcoef(xs, ys)[0, 1])
                r2 = np.random.default_rng(args.seed + 99)
                nul = [abs(np.corrcoef(xs, r2.permutation(ys))[0, 1]) for _ in range(2000)]
                pr, rx, ry = partial(xs, ys, zs)
                nulp = [abs(np.corrcoef(rx, r2.permutation(ry))[0, 1]) for _ in range(2000)]
                cov[name] = {"r": r, "p_perm": float((np.array(nul) >= abs(r)).mean()),
                             "r_partial_on_n_prompts": pr,
                             "p_perm_partial": float((np.array(nulp) >= abs(pr)).mean()),
                             "r_with_n_prompts": float(np.corrcoef(xs, zs)[0, 1]),
                             "n": len(xs)}
        subj = defaultdict(list)
        for a, v in g.items():
            s = person_cov[a].get("subjectivity") or []
            if s:
                subj[max(set(s), key=s.count)].append(v)
        out[base]["loser_covariates"] = cov
        out[base]["gain_by_modal_subjectivity"] = {
            k: {"n": len(v), "mean": float(np.mean(v))} for k, v in subj.items() if len(v) >= 10}
        if cov:
            print(f"    do the losers share anything?")
            print(f"      {'covariate':<16}{'raw r':>9}{'p':>9}{'partial r':>11}{'p':>9}"
                  f"{'r w/ nprompts':>15}")
            for k2, v2 in cov.items():
                print(f"      {k2:<16}{v2['r']:>+9.3f}{v2['p_perm']:>9.4f}"
                      f"{v2['r_partial_on_n_prompts']:>+11.3f}{v2['p_perm_partial']:>9.4f}"
                      f"{v2['r_with_n_prompts']:>+15.3f}")

    eq, sg = out["full_equal"], out["full_signed"]
    world = ("W-REDISTRIBUTES" if eq["spread_clears_floor"] and sg["spread_clears_floor"] else
             "W-UNIFORM" if not eq["spread_clears_floor"] and not sg["spread_clears_floor"] else
             "W-BASELINE-BOUND")
    conclusion = (
        f"Per-person concordance gain from compilation, over {eq['n_people']} annotators with at "
        f"least {MIN_PROMPTS} prompts and {MIN_PAIRS} ordered pairs each, computed against BOTH "
        f"full baselines because the choice between them decides the sign of the aggregate. "
        f"Against full_equal the mean gain is {eq['mean_gain']:+.5f} "
        f"[{eq['mean_gain_ci'][0]:+.5f}, {eq['mean_gain_ci'][1]:+.5f}], {eq['harmed_share']:.1%} of "
        f"people are harmed by more than {HARM_EPS}, and the worst decile averages "
        f"{eq['worst_decile_mean_gain']:+.5f}. Against full_signed the mean gain is "
        f"{sg['mean_gain']:+.5f} [{sg['mean_gain_ci'][0]:+.5f}, {sg['mean_gain_ci'][1]:+.5f}], "
        f"{sg['harmed_share']:.1%} harmed, worst decile {sg['worst_decile_mean_gain']:+.5f}. "
        f"The between-person spread is {eq['between_person_sd']:.5f} against a within-person "
        f"split-half floor of {eq['within_person_floor_sd']:.5f} (equal) and "
        f"{sg['between_person_sd']:.5f} against {sg['within_person_floor_sd']:.5f} (signed). "
        f"WORLD: {world}. "
        + ("The spread clears its own resampling floor under both conventions, so compilation moves "
           "accuracy between people rather than merely summarising, and who the losers are is a "
           "real question with a real answer."
           if world == "W-REDISTRIBUTES" else
           "The spread does not exceed what the same person produces on a random half of their own "
           "prompts under either convention. There are no locatable person-level losers here, and "
           "every person-level sacrifice claim this project has made on this data is withdrawn."
           if world == "W-UNIFORM" else
           "The spread clears the floor under one baseline convention and not the other, so the "
           "redistribution claim is conditional on a choice about how to read a negative rating and "
           "may never be stated without it."))
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    Path(args.out).write_text(json.dumps(
        {"seed": args.seed, "n_annotators_seen": len(by_person), "n_cells": len(cells),
         "min_prompts": MIN_PROMPTS, "min_pairs": MIN_PAIRS, "n_split": N_SPLIT,
         "baselines": out, "world": world, "conclusion": conclusion, **stamp(__file__)},
        indent=1, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
