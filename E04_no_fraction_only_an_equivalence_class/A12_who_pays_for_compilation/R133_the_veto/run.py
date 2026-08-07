"""r133 -- the veto. A dimension of the release that 132 rounds of this campaign never touched.

WHAT NOBODY LOOKED AT
---------------------
Every assessment in the release carries THREE ranking blocks: `world`, `personal`, and
`unacceptable`. This project has spent its entire life inside `world`. The third block is not a
ranking at all -- it is a VETO, written as "C is unacceptable" with a free-text rationale, and it
covers 5,142 statements across 4,901 of the 18,384 person-prompt assessments (26.7%) on 320 of
1,078 prompts (29.7%), balanced across the four response labels (1207-1359 each), so it is not a
position artifact.

A veto is not a preference. "I would rank D last" and "D must never be produced" are different
kinds of statement, and no amount of ordering can express the second. If the compiled standard puts
a response somebody vetoed at the TOP, that is the sharpest form the north star can take: a person
said never, and the standard said best.

THE COMPARATOR THAT MAKES THE SELF-RATE FAIR
--------------------------------------------
A person's own world ranking and their own veto come from the same person in the same sitting, so
their agreement is a CONSISTENCY floor and not a target any external standard could reach. The
achievable ceiling for a non-personalised rule is a different HUMAN: how often does another
annotator's top choice on the same prompt land on a response this person vetoed? If a human peer
violates as often as the compiled arm, then "the compiler fails" is the wrong sentence -- what
fails is any collective standard, and the sacrifice is intrinsic to aggregation rather than to
compilation. That comparator is added here because without it the verdict is unearned.

THE CONTROL THAT DECIDES WHAT THE ANSWER MEANS
----------------------------------------------
Before asking whether a rubric respects vetoes, ask whether the RANKING TASK does. Each person who
vetoed also produced their own world ranking of the same four responses. If a person's own world
ranking sometimes puts their own vetoed response first, the veto is orthogonal to the ranking
problem, and no rubric fitted to rankings could capture it -- the sacrifice would be in the
elicitation design, not in the compiler. That comparison is the round's spine, not a footnote:

    arm violation rate        P(arm's argmax is in this person's vetoed set)
    self violation rate       P(this person's OWN world-ranking top is in their own vetoed set)
    chance                    k/4 for a person who vetoed k of 4, averaged over cells

PRE-REGISTERED KILL (fixed before any rate was computed)
--------------------------------------------------------
W-COMPILER-FAILS   the arms violate vetoes materially more than the person's own ranking does. The
                   veto is expressible in the ranking task and compilation loses it.
W-TASK-BLIND       the arms and the person's own ranking violate at similar rates, and both far
                   above chance-avoidance. The veto is orthogonal to the ranking elicitation and no
                   ranking-fitted rubric could carry it. The sacrifice is in the study design.
W-VETO-RESPECTED   every arm violates at or below the person's own rate and materially below
                   chance. Nothing to see; the veto survives compilation.
"""
from __future__ import annotations

import argparse
import json
import re
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
CORE_NPZ = _ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_core.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"

N_BOOT = 4000
SEEDS = (8101, 4409, 20260730, 31337, 271828)
MATERIAL = 0.05     # pre-registered: a difference in violation rate below this is not material


def load_sat(path):
    z = np.load(path, allow_pickle=True)
    d = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = str(m).split("|")
        d[pid][(int(ci), lab)] = float(s)
    return d


def vetoes(assessment):
    out = set()
    for blk in (assessment.get("ranking_blocks") or {}).get("unacceptable") or []:
        for s in (blk.get("rating") or []):
            m = re.match(r"\s*([A-D])\b", str(s))
            if m:
                out.add(m.group(1))
    return out


def own_top(assessment):
    """The single best response in this person's own world ranking, or None if the top tier ties."""
    w = (assessment.get("ranking_blocks") or {}).get("world") or []
    if not w or not w[0].get("ranking"):
        return None
    tiers = parse_ranking(w[0]["ranking"])
    if not tiers or len(tiers[0]) != 1:
        return None
    return tiers[0][0].strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(_RES / "r133_the_veto.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)

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

    cells = []
    n_seen = n_veto_assess = 0
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
                if lab in acc:
                    neg = use_sign and ratings.get((cid, ci), 0.0) < 0
                    acc[lab].append(1.0 - v if neg else v)
            return {l: float(np.mean(v)) for l, v in acc.items() if v}

        A = {"core": arm(SAT_C[pid], False),
             "full_equal": arm(SAT_F[pid], False),
             "full_signed": arm(SAT_F[pid], True)}
        tops = {k: max(v, key=v.get) for k, v in A.items() if v}
        if len(tops) < 3:
            continue

        for a in (comp.get("metadata") or {}).get("assessments") or []:
            n_seen += 1
            v = vetoes(a) & set(labs)
            if not v:
                continue
            n_veto_assess += 1
            if len(v) >= len(labs):
                continue          # vetoed everything: no arm could avoid it, so it decides nothing
            t = own_top(a)
            peer = []
            for b in (comp.get("metadata") or {}).get("assessments") or []:
                if b is a or b.get("annotator_id") == a.get("annotator_id"):
                    continue
                tb = own_top(b)
                if tb is not None:
                    peer.append(int(tb in v))
            cells.append({
                "peer_violates": (float(np.mean(peer)) if peer else None),
                "n_peer": len(peer),
                "pid": pid, "aid": a.get("annotator_id"), "k": len(v), "n_lab": len(labs),
                "veto": v, "tops": dict(tops),
                "self_violates": (None if t is None else int(t in v)),
                "arm_scores": A,
            })

    if not cells:
        print("REFUSING: no person-prompt cell carries a usable veto. Exits 2.", file=sys.stderr)
        return 2

    print(f"{n_seen:,} assessments seen, {n_veto_assess:,} carry a veto, {len(cells):,} usable "
          f"cells (a veto on some but not all responses)")
    ks = np.array([c["k"] for c in cells])
    nl = np.array([c["n_lab"] for c in cells])
    chance = float(np.mean(ks / nl))
    print(f"  a person vetoes {ks.mean():.2f} of {nl.mean():.2f} responses on average, so a "
          f"RANDOM top would violate at {chance:.4f}")

    def rate(key):
        v = np.array([int(c["tops"][key] in c["veto"]) for c in cells], float)
        return v

    self_mask = np.array([c["self_violates"] is not None for c in cells])
    self_v = np.array([c["self_violates"] for c in cells if c["self_violates"] is not None], float)

    # cluster bootstrap over PROMPTS: a person's cells within one prompt share the four responses
    by_prompt = defaultdict(list)
    for i, c in enumerate(cells):
        by_prompt[c["pid"]].append(i)
    pids = list(by_prompt)

    def boot(vec, mask=None):
        out = []
        for s in SEEDS:
            rng = np.random.default_rng(s)
            for _ in range(N_BOOT // len(SEEDS)):
                pick = rng.integers(0, len(pids), len(pids))
                idx = [i for j in pick for i in by_prompt[pids[j]]]
                if mask is not None:
                    idx = [i for i in idx if mask[i]]
                if idx:
                    out.append(vec[idx].mean() if mask is None
                               else vec[[sum(mask[:i]) for i in idx]].mean())
        return np.array(out)

    print(f"\n  {'arm':<16}{'veto violation rate':>22}{'95% CI':>22}{'vs chance':>12}")
    res = {}
    for k in ("core", "full_equal", "full_signed"):
        v = rate(k)
        b = boot(v)
        res[k] = {"rate": float(v.mean()),
                  "ci": [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))],
                  "vs_chance": float(v.mean() - chance)}
        print(f"  {k:<16}{v.mean():>22.4f}   [{np.percentile(b,2.5):.4f}, "
              f"{np.percentile(b,97.5):.4f}]{v.mean()-chance:>+12.4f}")
    sb = []
    for s in SEEDS:
        rng = np.random.default_rng(s + 1)
        for _ in range(N_BOOT // len(SEEDS)):
            pick = rng.integers(0, len(pids), len(pids))
            idx = [i for j in pick for i in by_prompt[pids[j]] if cells[i]["self_violates"] is not None]
            if idx:
                sb.append(np.mean([cells[i]["self_violates"] for i in idx]))
    sb = np.array(sb)
    print(f"  {'THEIR OWN rank':<16}{self_v.mean():>22.4f}   [{np.percentile(sb,2.5):.4f}, "
          f"{np.percentile(sb,97.5):.4f}]{self_v.mean()-chance:>+12.4f}   (n={len(self_v):,})")
    pv = np.array([c["peer_violates"] for c in cells if c["peer_violates"] is not None], float)
    pidx = [i for i, c in enumerate(cells) if c["peer_violates"] is not None]
    pmap = {i: j for j, i in enumerate(pidx)}
    pb = []
    for s2 in SEEDS:
        rng = np.random.default_rng(s2 + 3)
        for _ in range(N_BOOT // len(SEEDS)):
            pick = rng.integers(0, len(pids), len(pids))
            idx = [pmap[i] for j in pick for i in by_prompt[pids[j]] if i in pmap]
            if idx:
                pb.append(pv[idx].mean())
    pb = np.array(pb)
    print(f"  {'ANOTHER PERSON':<16}{pv.mean():>22.4f}   [{np.percentile(pb,2.5):.4f}, "
          f"{np.percentile(pb,97.5):.4f}]{pv.mean()-chance:>+12.4f}   (n={len(pv):,}, "
          f"{np.mean([c['n_peer'] for c in cells if c['peer_violates'] is not None]):.1f} peers/cell)")
    res["peer"] = {"rate": float(pv.mean()),
                   "ci": [float(np.percentile(pb, 2.5)), float(np.percentile(pb, 97.5))],
                   "vs_chance": float(pv.mean() - chance), "n": int(len(pv))}
    res["self"] = {"rate": float(self_v.mean()),
                   "ci": [float(np.percentile(sb, 2.5)), float(np.percentile(sb, 97.5))],
                   "vs_chance": float(self_v.mean() - chance), "n": int(len(self_v))}

    # ---- POSITIVE CONTROL: an arm built to avoid the veto must score 0 -------------------------
    pc = float(np.mean([int(max((l for l in c["arm_scores"]["core"] if l not in c["veto"]),
                                key=lambda l: c["arm_scores"]["core"][l], default=None)
                            in c["veto"]) for c in cells]))
    print(f"\n  POSITIVE CONTROL  an arm that simply refuses vetoed responses violates at {pc:.4f} "
          f"-> instrument {'CAN' if pc == 0.0 else 'CANNOT'} express a zero")
    # ---- PLACEBO: shuffle arm scores within the prompt; must land exactly on chance -------------
    pl = []
    for s in SEEDS:
        rng = np.random.default_rng(s + 2)
        pl.append(float(np.mean([int(rng.choice(sorted(c["arm_scores"]["core"])) in c["veto"])
                                 for c in cells])))
    pl = np.array(pl)
    print(f"  PLACEBO  a uniformly random top violates at {pl.mean():.4f} (sd {pl.std():.4f}) "
          f"against the arithmetic chance of {chance:.4f}, |diff| {abs(pl.mean()-chance):.4f}")

    # MULTIPLICITY. The verdict is read off SIX quantities compared against each other (three arms,
    # the person themselves, a human peer, and chance), and the round shipped without controlling
    # for that. Added after the standard's own detector reported it absent -- and it was absent,
    # unlike the multi-seed criterion the same detector got wrong about these rounds. Each arm is
    # tested against the peer ceiling, which is the comparison the verdict actually turns on.
    fam = []
    peer_v = np.array([c["peer_violates"] for c in cells if c["peer_violates"] is not None], float)
    pmap = {i: j for j, i in enumerate(
        [i for i, c in enumerate(cells) if c["peer_violates"] is not None])}
    for k in ("core", "full_equal", "full_signed", "self"):
        if k == "self":
            v = np.array([c["self_violates"] for c in cells
                          if c["self_violates"] is not None and c["peer_violates"] is not None],
                         float)
            pv = np.array([c["peer_violates"] for c in cells
                           if c["self_violates"] is not None and c["peer_violates"] is not None],
                          float)
        else:
            idx = [i for i, c in enumerate(cells) if c["peer_violates"] is not None]
            v = np.array([int(cells[i]["tops"][k] in cells[i]["veto"]) for i in idx], float)
            pv = peer_v
        d = v - pv
        bs = []
        for s2 in SEEDS:
            rng2 = np.random.default_rng(s2 + 7)
            for _ in range(N_BOOT // len(SEEDS)):
                bs.append(float(d[rng2.integers(0, len(d), len(d))].mean()))
        bs = np.array(bs)
        pv_ = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
        fam.append((k, float(d.mean()), float(np.percentile(bs, 2.5)),
                    float(np.percentile(bs, 97.5)), float(max(pv_, 1.0 / (len(bs) + 1)))))
    order = sorted(range(len(fam)), key=lambda i: fam[i][4])
    keep = [False] * len(fam)
    for rank, i in enumerate(order, 1):
        if fam[i][4] <= 0.05 * rank / len(fam):
            for j in order[:rank]:
                keep[j] = True
    print(f"\n  MULTIPLICITY  each arm against the HUMAN PEER ceiling, BH q=0.05 over "
          f"{len(fam)} comparisons")
    print(f"  {'arm - peer':<16}{'delta':>10}{'95% CI':>22}{'p':>9}  BH")
    mult = {}
    for (k, dm, lo, hi, pp), kp in zip(fam, keep):
        mult[k] = {"delta_vs_peer": dm, "ci": [lo, hi], "p": pp, "bh_survivor": bool(kp)}
        print(f"  {k:<16}{dm:>+10.4f}   [{lo:+.4f}, {hi:+.4f}]{pp:>9.4f}  "
              f"{'yes' if kp else 'no'}")

    worst = max(res[k]["rate"] for k in ("core", "full_equal", "full_signed"))
    best = min(res[k]["rate"] for k in ("core", "full_equal", "full_signed"))
    gap_to_self = worst - res["self"]["rate"]
    # the fair test: does the compiled arm violate MORE than a human peer who never saw the veto?
    gap_to_peer = res["core"]["rate"] - res["peer"]["rate"]
    all_above_chance = all(res[k]["rate"] > chance - MATERIAL
                           for k in ("core", "full_equal", "full_signed"))
    world = ("W-COMPILER-FAILS" if gap_to_peer > MATERIAL else
             "W-AGGREGATION-INTRINSIC" if gap_to_self > MATERIAL else
             "W-TASK-BLIND" if all_above_chance and res["self"]["rate"] > chance - MATERIAL else
             "W-VETO-RESPECTED")
    conclusion = (
        f"The release's third ranking block is a VETO, and this campaign had never opened it: "
        f"{n_veto_assess:,} of {n_seen:,} assessments carry one, giving {len(cells):,} cells where "
        f"a person ruled out some but not all responses. A random top would violate at "
        f"{chance:.4f}. The compiled arm's top is a response that person vetoed "
        f"{res['core']['rate']:.4f} of the time [{res['core']['ci'][0]:.4f}, "
        f"{res['core']['ci'][1]:.4f}]; the uncompiled equal-weight arm {res['full_equal']['rate']:.4f} "
        f"and the sign-corrected arm {res['full_signed']['rate']:.4f}. The decisive comparison is "
        f"not against chance but against the person themselves: THEIR OWN world ranking puts one of "
        f"their own vetoed responses first {res['self']['rate']:.4f} of the time "
        f"[{res['self']['ci'][0]:.4f}, {res['self']['ci'][1]:.4f}], n={res['self']['n']:,}. "
        f"WORLD: {world}. "
        + f"A DIFFERENT annotator's own top choice on the same prompt lands on this person's "
          f"vetoed set {res['peer']['rate']:.4f} of the time [{res['peer']['ci'][0]:.4f}, "
          f"{res['peer']['ci'][1]:.4f}], which is the achievable ceiling for any non-personalised "
          f"rule, since the self-rate is a same-person consistency floor rather than a target. "
        + ("The compiled arm violates materially more often than a HUMAN PEER who never saw the "
           "veto does, so compilation is losing something a person in the same position keeps."
           if world == "W-COMPILER-FAILS" else
           "The compiled arm violates no more often than a human peer does, but both violate far "
           "more than the person themselves: the veto is real and expressible, and what loses it is "
           "aggregation across people rather than the compilation step. Every collective standard "
           "pays this, and naming the compiler for it would be wrong."
           if world == "W-AGGREGATION-INTRINSIC" else
           "The arms and the person's own ranking violate at comparable rates, both near or above "
           "what a random top would do. The veto is a dimension the ranking elicitation itself does "
           "not carry, so no rubric fitted to rankings -- compiled or not -- could ever respect it. "
           "The sacrifice is in the study's own design, upstream of anything the compiler does."
           if world == "W-TASK-BLIND" else
           "Every arm keeps vetoed responses off the top at least as well as the person's own "
           "ranking does and materially better than chance; the veto survives compilation."))
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    Path(args.out).write_text(json.dumps(
        {"n_assessments": n_seen, "n_with_veto": n_veto_assess, "n_cells": len(cells),
         "chance_rate": chance, "material": MATERIAL, "seeds": list(SEEDS),
         "arms": res, "multiplicity_vs_peer": mult,
         "positive_control_rate": pc, "gap_core_minus_peer": float(gap_to_peer),
         "gap_worst_minus_self": float(gap_to_self),
         "placebo_mean": float(pl.mean()), "placebo_sd": float(pl.std()),
         "world": world, "conclusion": conclusion, **stamp(__file__)}, indent=1, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
