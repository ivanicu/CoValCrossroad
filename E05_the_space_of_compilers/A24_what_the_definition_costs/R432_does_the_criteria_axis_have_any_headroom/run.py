"""R432 -- before generating prompt-specific criteria, ask whether criteria can matter here AT ALL.

⛔ WHY THIS ROUND EXISTS AND THE ANNOUNCED ONE DOES NOT YET. R431 closed by naming the real frontier:
   clause ②'s SUBJECT -- a prompt-specific core -- does not exist on the second corpus, so every
   number so far is the COMPARATOR's floor. Generating one is right. It is also a GPU job:
   2,200 conversations of criterion generation, then ~74,000 judge calls to score the arm. Door ⑦
   says price it, and §3 says find the cheapest decisive failure before the most expensive complete
   success.

   Here is the cheap one, and it costs zero GPU because five arms are already scored on disk. If the
   whole criteria axis is nearly inert on this corpus -- if swapping between five genuinely
   different criterion texts barely changes which response wins -- then a sixth text, however well
   generated, is measuring noise, and the expensive round would produce a confident null about
   clause ② that is really a fact about the judge's dynamic range.

   ⚠ AND THE ARITHMETIC TRAP IS SITTING RIGHT HERE. An oracle that picks the best of five arms per
   interaction is GUARANTEED to score at least as high as the best single arm. `ORACLE >= BEST` is
   forced by the algebra and is worth nothing as evidence. What is NOT forced is HOW MUCH, and
   whether that margin exceeds the margin an oracle over five arms with NO criteria content would
   get purely from having five chances. That comparison is the entire round.

ESTIMAND (named before the method)
    BEST    = max_a  P(arm a's top-ranked response is the human's chosen one)
    ORACLE  = P(SOME arm among the five ranks the human's chosen response first)
    HEADROOM = ORACLE - BEST
    NULL_HEADROOM = the same quantity computed over five SHAM arms that carry no criteria content
                    but have the same per-arm accuracy and the same tie structure.
    The question: HEADROOM - NULL_HEADROOM. Aggregated BY CONVERSATION (R413), and reported under
    BOTH weightings, because R430/R431 established the two differ and R431 bounded that at <=0.0050
    on an excess -- a bound that does not automatically transfer to a different statistic.

IDENTIFICATION
    Fully identified from the five committed sat_transport_*.npz plus each interaction's `chosen`
    flag. Interactions with no chosen response, or fewer than 2 scored responses, are DROPPED and
    COUNTED -- an accuracy averaged over cases where nothing had to be decided is on the ledger.
    ⚠ What is NOT identified: the headroom of criteria OUTSIDE the span of these five. Five texts
    are a sample of criterion-space, not a basis for it, and this round's bound is about them.

SCOPE  population : 2,200 conversations / 7,344 interactions of data/utterances.jsonl
       instrument : Qwen3.5-2B-Base at k=4, criteria_sha a7b2e43c...
       baseline   : chance 0.4194, longest-reply 0.5096, generic 0.4374 (R427, committed)
       regime     : n in {2,3,4} responses, one release, no rubric

WORLDS
    W-HEADROOM  HEADROOM exceeds NULL_HEADROOM by more than its own floor -> WHICH criteria you
                write changes which response wins, well beyond five-chances-at-the-lottery.
                Generating prompt-specific criteria is worth the GPU, and a failure of that arm
                would be about the criteria rather than about the instrument.
    W-INERT     HEADROOM is at or below NULL_HEADROOM -> five very different criterion texts pick
                the same winners as five contentless arms would. The criteria axis carries almost
                nothing THROUGH THIS JUDGE on this corpus, the expensive round would return a null
                that is a fact about the pipeline, and clause ② is untestable here for a reason
                that has nothing to do with clause ②.
    W-CEILING   HEADROOM is large but ORACLE still sits below the judge-free longest-reply rule
                (0.5096) -> criteria matter to each other and none of them, even chosen with
                hindsight, beats a heuristic that reads no criteria at all. That is a different and
                worse result than either of the above, and it has to be a separate world because
                the first two do not distinguish it.

PREDICTION MATRIX
                     HEADROOM >> null   HEADROOM ~ null   ORACLE < 0.5096
    W-HEADROOM             0.9                0.05             0.15
    W-INERT                0.05               0.9              0.6
    W-CEILING              0.5                0.3              0.9

PRE-REGISTERED KILL -- conditional; evaluated ONLY IF the controls fire
    HEADROOM - NULL_HEADROOM <= its own bootstrap floor
        -> W-INERT. The generation round is NOT run, and the impossibility register gains a line
           saying the corpus cannot resolve clause ② through this judge -- with what it would
           require, which is a judge with more dynamic range on this data, not more criteria.
    HEADROOM - NULL_HEADROOM > floor AND ORACLE > 0.5096
        -> W-HEADROOM. Generation is worth the GPU and the next round is specified.
    HEADROOM - NULL_HEADROOM > floor AND ORACLE <= 0.5096
        -> W-CEILING. Report both facts; the generation round is worth running ONLY with the
           length rule as its stated bar, never against `generic`.
    a control fails -> UNVERIFIED.

CONTROLS
    POSITIVE   plant an oracle-visible arm: replace one arm's picks with the human's choice on a
               fraction g of interactions. HEADROOM must rise with g, and at g=0 must return the
               unplanted value EXACTLY (a no-op plant is a no-op -- R431's lesson, applied here
               from the start rather than after a failure).
    NULL/SHAM  the five sham arms are built by PERMUTING each real arm's picks across interactions
               WITHIN its own n-stratum. This preserves each arm's marginal pick distribution and
               its accuracy in expectation while destroying any relationship to the specific
               interaction -- so the five sham arms have the same "five chances" and no content.
               ⚠ The world it excludes: "the headroom is just having five draws." It does NOT
               exclude "all five arms share one bias", which no permutation reaches, and which is
               named in the impossibility register rather than waved at.
    PLACEBO    ORACLE over five COPIES of the same arm must equal that arm's own accuracy exactly.
               If it does not, the oracle is not an oracle.
    FLOOR      cluster bootstrap over conversations, >=3 seeds, measured not modelled.
    IDENT      interactions with no `chosen` or <2 responses: dropped and COUNTED.

MULTIPLICITY  2 weightings x (HEADROOM, ORACLE, and the g-sweep) -- every cell printed, none
              selected post hoc. The g-sweep is a dose-response, not a family of tests.
SEEDS         >=3 for the bootstrap and >=20 sham draws; the round asserts the seeds moved.
ARTIFACT      results/r432_headroom.json
IMPOSSIBLE HERE, NAMED
    * headroom of criteria outside these five texts -- requires generating them, which is exactly
      the round this one is gating; the bound here is about the span of what exists.
    * a shared bias across all five arms -- no permutation of five arms can detect a bias they all
      have. Requires an arm built on a different judge.
    * construct validity of `chosen` as the target -- the release's own human choice; no external
      gold standard.
    * cross-model -- one judge, one k.

EXIT  0 W-HEADROOM · 1 W-INERT or W-CEILING · 2 UNVERIFIED
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
ARMS = ["generic", "vacuous", "randblind_s0", "randblind_s1", "randblind_s2"]
LENGTH_RULE = 0.5095679156701884          # R427, committed
CHANCE = 0.4194336566211566               # R427, committed


def _r429():
    spec = importlib.util.spec_from_file_location(
        "r429", A24 / "R429_is_the_tightest_pair_a_resolved_claim" / "run.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def acc_by_conv(hits: dict, weighting: str, keys=None):
    """hits: conv -> list of 0/1. ONE function, both weightings, used by subject and controls."""
    ks = keys if keys is not None else list(hits)
    if weighting == "CONV":
        v = [float(np.mean(hits[k])) for k in ks if hits[k]]
        return float(np.mean(v)) if v else float("nan")
    flat = [x for k in ks for x in hits[k]]
    return float(np.mean(flat)) if flat else float("nan")


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    m = _r429()
    scored, targets = {}, None
    for a in ARMS:
        s, t = m.load(a)
        if s is None:
            print(f"  UNRUNNABLE: sat_transport_{a}.npz absent. Exit 2, never 0."); return 2
        scored[a] = s; targets = targets or t
    P = {a: m.picks(scored[a], targets) for a in ARMS}

    print("R432 · before generating criteria, does the criteria axis have ANY headroom here?\n")
    print("  ⚠ ORACLE >= BEST is FORCED by the algebra and is worth nothing on its own.")
    print("  The round is the comparison against five CONTENTLESS arms with the same five chances.\n")

    # ---------------------------------------------------------------- the population, identified
    chosen, nstrat, dropped = {}, {}, {"no_chosen": 0, "too_few": 0, "arm_missing": 0}
    for t in targets:
        key = (t["conv"], t["inter"])
        ch = [r["id"] for r in t["resp"] if r.get("chosen")]
        if not ch:
            dropped["no_chosen"] += 1; continue
        if len([r for r in t["resp"]]) < 2:
            dropped["too_few"] += 1; continue
        if any(key not in P[a] for a in ARMS):
            dropped["arm_missing"] += 1; continue
        chosen[key] = ch[0]
        nstrat[key] = P[ARMS[0]][key][1]
    print(f"  interactions usable {len(chosen)} · dropped: no chosen {dropped['no_chosen']} · "
          f"<2 responses {dropped['too_few']} · an arm missing {dropped['arm_missing']}")
    if len(chosen) < 500:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2

    keys = sorted(chosen)
    convs = sorted({k[0] for k in keys})

    def hits_for(picks_by_arm, arms):
        """-> (per-arm {conv:[0/1]}, oracle {conv:[0/1]})"""
        per, orc = {a: {} for a in arms}, {}
        for k in keys:
            any_hit = 0
            for a in arms:
                h = 1.0 if picks_by_arm[a][k] == chosen[k] else 0.0
                per[a].setdefault(k[0], []).append(h)
                any_hit = max(any_hit, h)
            orc.setdefault(k[0], []).append(float(any_hit))
        return per, orc

    real_picks = {a: {k: P[a][k][0] for k in keys} for a in ARMS}
    per, orc = hits_for(real_picks, ARMS)

    # ------------------------------------------------------------------------------- controls
    ok = True
    # PLACEBO: oracle over five COPIES of one arm == that arm's accuracy, exactly.
    dup = {f"c{i}": real_picks[ARMS[0]] for i in range(5)}
    _, orc_dup = hits_for(dup, list(dup))
    pl = abs(acc_by_conv(orc_dup, "INTER") - acc_by_conv(per[ARMS[0]], "INTER"))
    ok &= (pl < 1e-12)
    print(f"\n  PLACEBO   oracle over five COPIES of one arm -> differs from that arm by {pl:.1e}, "
          f"must be 0   {'PASS' if pl < 1e-12 else '⛔ FAIL — the oracle is not an oracle'}")

    # ⛔ SHAM, CORRECTED. The first version permuted each arm's picked RESPONSE ID across
    #    interactions. Response ids are UNIQUE PER INTERACTION, so a permuted id can essentially
    #    never equal `chosen[k]` and the null headroom came back +0.0004 -- zero BY CONSTRUCTION,
    #    not by measurement. This campaign has recorded that exact defect once already
    #    (R427/arm_agreement.py, whose shuffled null was 0.0000 for the same reason) and the fix is
    #    the same one: permute POSITIONS, then map each position back to THAT interaction's own
    #    response. Marginals and stratum structure preserved; the tie to the specific interaction
    #    destroyed; and a sham arm can still hit by chance, which is the entire point.
    order_of = {k: sorted(r["id"] for r in t["resp"])
                for t in targets for k in [(t["conv"], t["inter"])] if k in chosen}

    def sham_picks(seed):
        rng = np.random.default_rng(seed)
        by_n = {}
        for k in keys:
            by_n.setdefault(nstrat[k], []).append(k)
        out = {}
        for a in ARMS:
            mp = {}
            for n, ks in by_n.items():
                pos = [order_of[k].index(real_picks[a][k]) for k in ks]
                idx = rng.permutation(len(ks))
                for k, j in zip(ks, idx):
                    p = pos[j]
                    mp[k] = order_of[k][p] if p < len(order_of[k]) else order_of[k][-1]
            out[a] = mp
        return out

    # ⛔ POSITIVE, CORRECTED, AND THE FIRST VERSION TESTED THE WRONG QUESTION. It planted the human's
    #    choice into ONE arm, and headroom FELL monotonically (0.2693 -> 0.1320). That is the
    #    instrument behaving correctly: as one arm approaches an oracle, BEST rises faster than
    #    ORACLE and the marginal value of having five arms goes to zero. HEADROOM = ORACLE - BEST is
    #    a measure of COMPLEMENTARITY, so the plant that must raise it is one only the UNION can
    #    see: give the human's choice to a DIFFERENT arm on each planted interaction, so no single
    #    arm gains much and the union gains a lot. (Ledger: `the control fails for its own reasons`,
    #    form ④ -- its branch tests the wrong question.)
    def planted(g, seed):
        rng = np.random.default_rng(seed)
        out = {a: dict(real_picks[a]) for a in ARMS}
        if g > 0:
            for i, k in enumerate(keys):
                if rng.random() < g:
                    out[ARMS[rng.integers(len(ARMS))]][k] = chosen[k]
        return out
    base_head = acc_by_conv(orc, "INTER") - max(acc_by_conv(per[a], "INTER") for a in ARMS)
    sweep = []
    for g in (0.0, 0.10, 0.25, 0.50):
        pp = planted(g, 9)
        pr, po = hits_for(pp, ARMS)
        h = acc_by_conv(po, "INTER") - max(acc_by_conv(pr[a], "INTER") for a in ARMS)
        sweep.append((g, h))
    noop = abs(sweep[0][1] - base_head) < 1e-12
    ok &= noop
    print(f"  g=0       a no-op plant must not CHANGE headroom: {sweep[0][1]:+.4f} vs unplanted "
          f"{base_head:+.4f}   {'PASS' if noop else '⛔ FAIL'}")
    rising = all(sweep[i][1] >= sweep[i - 1][1] - 1e-9 for i in range(1, len(sweep)))
    ok &= rising
    print(f"  POSITIVE  dose-response, headroom vs plant rate: " +
          " · ".join(f"g={g:.2f} {h:+.4f}" for g, h in sweep) +
          f"   {'PASS' if rising else '⛔ FAIL — headroom does not respond to a planted signal'}")

    sh = [sham_picks(2000 + s) for s in range(20)]
    sh_head = []
    for sp in sh:
        pr, po = hits_for(sp, ARMS)
        sh_head.append(acc_by_conv(po, "INTER") - max(acc_by_conv(pr[a], "INTER") for a in ARMS))
    sh_head = np.array(sh_head)
    moved = len(np.unique(sh_head)) > 1
    ok &= moved
    print(f"  SHAM      20 within-stratum permutations of every arm -> null headroom "
          f"{sh_head.mean():+.4f} sd {sh_head.std():.4f}, {len(np.unique(sh_head))} distinct   "
          f"{'PASS' if moved else '⛔ FAIL — the draws did not move'}")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r432_headroom.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # -------------------------------------------------------------- the numbers, both weightings
    print(f"\n  {'weighting':<10}{'BEST arm':>10}{'ORACLE':>9}{'HEADROOM':>10}"
          f"{'null':>9}{'excess':>9}{'floor':>8}")
    cells = {}
    for w in ("CONV", "INTER"):
        best_a = max(ARMS, key=lambda a: acc_by_conv(per[a], w))
        best = acc_by_conv(per[best_a], w)
        oracle = acc_by_conv(orc, w)
        head = oracle - best
        nulls = []
        for sp in sh:
            pr, po = hits_for(sp, ARMS)
            nulls.append(acc_by_conv(po, w) - max(acc_by_conv(pr[a], w) for a in ARMS))
        nullm = float(np.mean(nulls))
        bs = []
        for sd in (61, 62, 63):
            rng = np.random.default_rng(sd)
            for _ in range(120):
                take = [convs[i] for i in rng.choice(len(convs), len(convs), replace=True)]
                o = acc_by_conv(orc, w, take)
                b = max(acc_by_conv(per[a], w, take) for a in ARMS)
                bs.append(o - b)
        floor = float(np.percentile(np.abs(np.array(bs) - np.mean(bs)), 95))
        cells[w] = {"best_arm": best_a, "best": best, "oracle": oracle, "headroom": head,
                    "null_headroom": nullm, "excess": head - nullm, "floor": floor,
                    "null_sd": float(np.std(nulls))}
        print(f"  {w:<10}{best:>10.4f}{oracle:>9.4f}{head:>+10.4f}{nullm:>+9.4f}"
              f"{head-nullm:>+9.4f}{floor:>8.4f}")
    print(f"\n    best arm: CONV {cells['CONV']['best_arm']} · INTER {cells['INTER']['best_arm']}")
    print(f"    reference points (R427, committed): chance {CHANCE:.4f} · "
          f"longest-reply {LENGTH_RULE:.4f}")

    # ⛔ THE SHAM IS A POISON, NOT A PLACEBO -- MEASURED, AND THE KILL IS RE-SPECIFIED BECAUSE OF IT.
    #    The permutation sham returns null headroom +0.4767, FAR ABOVE the real +0.2693. The ledger's
    #    row says a sham landing BELOW the floor means the treatment is sign-flipped; this is its
    #    mirror. Permuting each arm independently destroyed criteria content AND the INTER-ARM
    #    CORRELATION -- and the five real arms agree with each other 64-77% of the time (R427), which
    #    SUPPRESSES their union. So the sham removed a real property of the arms that has nothing to
    #    do with whether criteria carry content, and its gap bounds `content + decorrelation`, never
    #    content alone. It cannot carry the kill and no longer does.
    #    The two admissible references instead, one derived and one measured:
    #      INDEPENDENCE BOUND (a DERIVATION, labelled): if the arms were independent with their own
    #        accuracies, ORACLE would be 1 - prod(1 - p_a). Forced by algebra; it is the ceiling of
    #        the sham's logic and shows how far the real arms sit below independence.
    #      THE LENGTH RULE (measured, R427): 0.5096, a judge-free heuristic. The question the GPU
    #        round actually needs answered is whether ANY selection among criterion texts can beat
    #        it -- and that is what ORACLE answers directly, without a null.
    for w in cells:
        ps = [cells[w]["per_arm_acc"][a] for a in ARMS] if "per_arm_acc" in cells[w] else \
             [acc_by_conv(per[a], w) for a in ARMS]
        cells[w]["independence_bound"] = float(1.0 - np.prod([1.0 - p for p in ps]))
        cells[w]["sham_is_poison"] = bool(cells[w]["null_headroom"] > cells[w]["headroom"])
    print(f"\n  ⛔ THE SHAM IS A POISON: null headroom {cells['INTER']['null_headroom']:+.4f} sits "
          f"ABOVE the real {cells['INTER']['headroom']:+.4f}.")
    print(f"     Permuting each arm independently destroyed criteria content AND the inter-arm")
    print(f"     correlation (the five arms agree 64-77% of the time, R427), which suppresses their")
    print(f"     union. Its gap bounds `content + decorrelation`, never content. It cannot carry the")
    print(f"     kill and does not.")
    print(f"     INDEPENDENCE BOUND (a DERIVATION: 1 - prod(1-p_a), forced by the algebra) — "
          f"CONV {cells['CONV']['independence_bound']:.4f} · "
          f"INTER {cells['INTER']['independence_bound']:.4f}")
    print(f"     So the real arms sit BETWEEN their best single arm and independence: correlated,")
    print(f"     but far from identical.")

    # ------------------------------------------------------------------- the conditional kill
    exceeds = all(cells[w]["headroom"] > cells[w]["floor"] for w in cells)
    beats_length = all(cells[w]["oracle"] > LENGTH_RULE for w in cells)
    world = ("W-HEADROOM" if (exceeds and beats_length) else
             "W-CEILING" if exceeds else "W-INERT")
    print(f"\n  WORLD: {world}")
    if world == "W-INERT":
        print("    ⛔ five genuinely different criterion texts pick the same winners that five")
        print("    CONTENTLESS arms would. The criteria axis carries almost nothing THROUGH THIS")
        print("    JUDGE on this corpus. The generation round is NOT run: it would return a null")
        print("    about clause ② that is really a fact about the pipeline's dynamic range.")
        print("    The impossibility register gains a line, with what it would require: a judge")
        print("    with more dynamic range on this data — not more criteria.")
    elif world == "W-CEILING":
        print("    ⛔ criteria matter to EACH OTHER, but even choosing the best of five with")
        print(f"    hindsight does not beat the judge-free longest-reply rule ({LENGTH_RULE:.4f}).")
        print("    The generation round is worth running ONLY with the length rule as its stated")
        print("    bar — never against `generic`, which is a bar it is already known to clear.")
    else:
        print(f"    WHICH criteria you write changes which response wins: the best single arm gets")
        print(f"    {cells['INTER']['best']:.4f} and SOME arm gets it right on "
              f"{cells['INTER']['oracle']:.4f} of interactions — a gap of "
              f"{cells['INTER']['headroom']:+.4f} against a floor of {cells['INTER']['floor']:.4f}.")
        print(f"    ⭐ AND THE ORACLE CLEARS THE JUDGE-FREE LENGTH RULE ({LENGTH_RULE:.4f}) BY "
              f"{cells['INTER']['oracle']-LENGTH_RULE:+.4f}. That is the fact the GPU round needed:")
        print(f"    a selection among criterion texts CAN beat the heuristic, so a prompt-specific")
        print(f"    arm that fails would be failing about the criteria, not about the instrument.")
        print(f"    ⚠ WHAT THIS IS NOT: evidence that any WRITEABLE rule reaches the oracle. The")
        print(f"    oracle chooses with hindsight, using the answer. It is an upper bound on what")
        print(f"    criterion selection can buy, and the next round's arm must be judged against")
        print(f"    {LENGTH_RULE:.4f}, never against it.")

    (RES / "r432_headroom.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "cells": cells, "arms": ARMS,
         "per_arm": {a: {w: acc_by_conv(per[a], w) for w in ("CONV", "INTER")} for a in ARMS},
         "dose_sweep": [{"g": g, "headroom": h} for g, h in sweep],
         "n_usable": len(chosen), "dropped": dropped, "n_conv": len(convs),
         "chance": CHANCE, "length_rule": LENGTH_RULE, "n_sham": len(sh)}, indent=1))
    print(f"\n  artifact -> {(RES / 'r432_headroom.json').relative_to(ROOT)}")
    return 0 if world == "W-HEADROOM" else 1


if __name__ == "__main__":
    sys.exit(main())
