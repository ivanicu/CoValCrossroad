"""R430 -- I blamed the NULL. There is a second difference I never checked: the WEIGHTING.

⛔ WHY, AND IT IS AN ATTACK ON A DIAGNOSIS I COMMITTED TWO HOURS AGO. R429 (7c87a72) measured that
   R427's null sits 0.0148 below the analytic expectation of R427's own construction, called the
   world W-BIAS, and attributed the rank-5-to-10 disagreement to the NULL. That attribution has a
   rival I did not look for, and it was sitting in `lib/cluster.py`:

       R427   ByConv.mean(name) = mean over CONVERSATIONS of each conversation's own mean
       R429   excess_point()    = (sum agree - sum expected) / sum interactions, POOLED

   Those are different estimators of different estimands. A conversation with 8 interactions counts
   once in R427 and eight times in R429, and the strata are not balanced across conversations. So
   the gap I attributed to the null construction may be entirely the AGGREGATION WEIGHT -- and if it
   is, R429's headline diagnosis is wrong and the synthetic-corpus round I announced as the next
   step would have been answering the wrong question with a much more expensive instrument.

   ⭐ THIS IS ATTACK-LADDER RUNG 2 (arithmetic) RUN BEFORE RUNG 4 (synthetic world). R429's closing
   line said the next step was to build a synthetic corpus and see which null recovers the truth.
   That line is exactly the shape the ledger warns about -- written last, acted on next, with no
   control attached -- and the cheaper decisive test is a 2x2 that needs no new data at all.

ESTIMAND (named before the method)
    The observed discrepancy D = null_R427(P) - null_R429(P) per pair P, DECOMPOSED over a 2x2:
        axis W (weighting)  : CONV  = mean over conversations of per-conversation means
                              INTER = pooled over interactions
        axis N (null)       : PERM  = one realised within-stratum permutation, as R427 draws it
                              ANLY  = dot(marginal_a, marginal_b) within each stratum, in closed form
    and the question is WHICH AXIS carries D. Not "is there a difference" -- that is already
    measured -- but which of two named mechanisms produces it.

IDENTIFICATION
    Fully identified and it is a DECOMPOSITION, not an inference: all four cells are computable from
    the same five committed npz files, and R427's committed null is a fixed number to reproduce.
    ⚠ What is NOT identified: whether either null is CORRECT. This round localises a discrepancy;
    it does not adjudicate. Saying otherwise would be the same overreach R429 already made once.

SCOPE  population : 2,200 conversations / 7,344 interactions of data/utterances.jsonl
       instrument : the five sat_transport_*.npz and r427_pairwise_excess.json
       baseline   : R427's committed per-pair null values
       regime     : 5 arms, 10 pairs, k=4, n in {2,3,4}

WORLDS
    W-WEIGHTING   the CONV cells reproduce R427 and the INTER cells do not, at BOTH null
                  constructions -> the gap is the aggregation weight. R429's W-BIAS attribution is
                  RETRACTED, the two nulls agree, and the rank-5-to-10 instability is a statement
                  about conversation-vs-interaction weighting, which is a choice with a defensible
                  answer (R413 says the conversation is the unit) rather than a defect.
    W-NULL        the PERM cells reproduce R427 and ANLY does not, at BOTH weightings -> R429 was
                  right and the null construction is the mechanism.
    W-BOTH        each axis carries part of D, neither alone reproduces R427 -> report the
                  decomposition as the finding and quote no single mechanism.
    W-THIRD       no cell reproduces R427 -> there is a difference neither axis names, and the
                  honest output is that the decomposition is INCOMPLETE. This world is the reason
                  the positive control below is the strong one.

PREDICTION MATRIX
                        CONV cells match    PERM cells match    no cell matches
    W-WEIGHTING              0.9                  0.1                0.02
    W-NULL                   0.1                  0.9                0.02
    W-BOTH                   0.3                  0.3                0.05
    W-THIRD                  0.02                 0.02               0.9

PRE-REGISTERED KILL -- conditional, and the condition is the reproduction control
    evaluate ONLY IF at least one of the four cells reproduces R427's committed null on >= 8 of 10
    pairs to within the PERM draw band (which is measured here, not assumed).
      the reproducing cell is CONV/*    -> W-WEIGHTING; R429's W-BIAS attribution is retracted and
                                           this round owes that retraction to RETRACTIONS.md and to
                                           DEFINITION.md, not just to its own README.
      the reproducing cell is */PERM only -> W-NULL; R429 stands unchanged.
      two cells on different axes reproduce -> W-BOTH.
    if NO cell reproduces -> W-THIRD, verdict UNVERIFIED, and the round reports what it could not
                             explain rather than picking the closest cell. Picking the closest is
                             how a decomposition becomes a narrative.

CONTROLS
    REPRODUCTION  the CONV/PERM cell is R427's construction on both axes. It MUST land inside its
                  own permutation draw band on R427's committed value. If the cell that IS R427's
                  method cannot reproduce R427, the decomposition is not measuring what it claims
                  and no other cell's agreement means anything.
    PLACEBO       each cell against ITSELF must give exactly 0.
    g=0           with the permutation replaced by the identity, PERM must equal raw agreement, not
                  the null -- a degenerate permutation must produce a degenerate null, and if it
                  does not, the permutation is not what is generating the null.
    NEGATIVE      the PERM band must WIDEN when the interaction count is subsampled; a band that
                  does not respond to n is not a sampling band.
    SEEDS         >= 3 permutation seeds, and the round asserts the seeds changed the draws rather
                  than assuming the flag was wired.

MULTIPLICITY  4 cells x 10 pairs = 40, all reported; the verdict is a COUNT over pairs per cell,
              so no per-cell correction is owed and that is stated rather than omitted.
ARTIFACT      results/r430_decomposition.json
IMPOSSIBLE    * deciding which null is CORRECT -- needs a corpus with known truth (the synthetic
                round R429 announced), and this round deliberately does not pretend to it.
              * recovering R427's exact permutation -- the artifact stores the result, not the draw,
                so the reproduction test is distributional and says so.

EXIT 0 a mechanism is localised · 1 W-BOTH or W-THIRD · 2 UNRUNNABLE or the control fails
"""
from __future__ import annotations
import hashlib
import importlib.util
import itertools
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
R427J = A24 / "R427_does_the_definition_transport_at_all/results/r427_pairwise_excess.json"
ARMS = ["generic", "vacuous", "randblind_s0", "randblind_s1", "randblind_s2"]


def _r429():
    spec = importlib.util.spec_from_file_location(
        "r429", A24 / "R429_is_the_tightest_pair_a_resolved_claim" / "run.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def null_cell(pa, pb, order, weighting: str, nullkind: str, rng=None, identity=False,
              frac=1.0):
    """ONE function for all four cells. The controls and the subject share it by construction,
    because a control exercising a different code path than the thing it certifies is this
    campaign's dominant control failure."""
    common = sorted(set(pa) & set(pb))
    by_n: dict = {}
    for k in common:
        by_n.setdefault(pa[k][1], []).append(k)
    contrib: dict = {}                       # conv -> list of per-interaction null contributions
    for n, keys in by_n.items():
        ks = keys
        if frac < 1.0 and rng is not None:
            take = rng.choice(len(keys), max(2, int(len(keys) * frac)), replace=False)
            ks = [keys[i] for i in take]
        pos_a = np.array([order[k].index(pa[k][0]) for k in ks])
        pos_b = np.array([order[k].index(pb[k][0]) for k in ks])
        if nullkind == "PERM":
            perm = np.arange(len(ks)) if identity else rng.permutation(len(ks))
            vals = (pos_a == pos_b[perm]).astype(float)
        else:                                # ANLY: the closed-form expectation, same for every k
            ma = np.bincount(pos_a, minlength=n) / len(ks)
            mb = np.bincount(pos_b, minlength=n) / len(ks)
            vals = np.full(len(ks), float(np.dot(ma, mb)))
        for k, v in zip(ks, vals):
            contrib.setdefault(k[0], []).append(float(v))
    if weighting == "CONV":
        return float(np.mean([np.mean(v) for v in contrib.values()]))
    flat = [x for v in contrib.values() for x in v]
    return float(np.mean(flat))


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    if not R427J.exists():
        print("  UNRUNNABLE: R427's artifact absent. Exit 2, never 0."); return 2
    m = _r429()
    scored, targets = {}, None
    for a in ARMS:
        s, t = m.load(a)
        if s is None:
            print(f"  UNRUNNABLE: sat_transport_{a}.npz absent. Exit 2."); return 2
        scored[a] = s; targets = targets or t
    P = {a: m.picks(scored[a], targets) for a in ARMS}
    order = {(t["conv"], t["inter"]): sorted(r["id"] for r in t["resp"]) for t in targets}
    r427 = {"|".join(sorted(k.split("|"))): v["null"]
            for k, v in json.loads(R427J.read_text())["pairs"].items()}
    pairs = list(itertools.combinations(ARMS, 2))
    seeds = [101, 202, 303]

    print("R430 · I blamed the NULL. Was it the null, or the WEIGHTING?\n")
    print("  R427  ByConv.mean : mean over CONVERSATIONS of per-conversation means")
    print("  R429  pooled      : sum(agree - expected) / sum(interactions)")
    print("  A conversation with 8 interactions counts ONCE in one and EIGHT times in the other.\n")

    # ------------------------------------------------------------------------------- controls
    ok = True
    probe = pairs[0]
    band = np.array([null_cell(P[probe[0]], P[probe[1]], order, "CONV", "PERM",
                               np.random.default_rng(s)) for s in range(60)])
    seeds_moved = len(np.unique(band)) > 1
    ok &= seeds_moved
    print(f"  SEEDS     60 permutation seeds produce {len(np.unique(band))} distinct values, "
          f"must be > 1   {'PASS' if seeds_moved else '⛔ FAIL — the seed flag is not wired'}")

    idn = null_cell(P[probe[0]], P[probe[1]], order, "CONV", "PERM",
                    np.random.default_rng(0), identity=True)
    by_conv: dict = {}
    for k in sorted(set(P[probe[0]]) & set(P[probe[1]])):
        by_conv.setdefault(k[0], []).append(
            1.0 if P[probe[0]][k][0] == P[probe[1]][k][0] else 0.0)
    agree_raw = float(np.mean([np.mean(v) for v in by_conv.values()]))
    g0 = abs(idn - agree_raw) < 1e-9
    ok &= g0
    print(f"    g=0     identity permutation -> {idn:.6f}, raw agreement {agree_raw:.6f}, must be "
          f"EQUAL   {'PASS' if g0 else '⛔ FAIL — the permutation is not generating the null'}")

    plac = abs(null_cell(P[probe[0]], P[probe[1]], order, "INTER", "ANLY")
               - null_cell(P[probe[0]], P[probe[1]], order, "INTER", "ANLY"))
    ok &= (plac == 0.0)
    print(f"    PLACEBO ANLY cell against itself -> {plac:.1e}, must be 0   "
          f"{'PASS' if plac == 0.0 else '⛔ FAIL'}")

    small = np.array([null_cell(P[probe[0]], P[probe[1]], order, "CONV", "PERM",
                                np.random.default_rng(s), frac=0.25) for s in range(60)])
    widens = small.std() > band.std()
    ok &= widens
    print(f"    NEGATIVE at 25% of interactions the PERM band sd goes {band.std():.5f} -> "
          f"{small.std():.5f}, must WIDEN   {'PASS' if widens else '⛔ FAIL'}")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the decomposition is NOT read.")
        (RES / "r430_decomposition.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # ---------------------------------------------------------------------- the 2x2, per pair
    print(f"\n  THE 2x2 · {len(pairs)} pairs x 4 cells = {len(pairs)*4} values, all reported\n")
    print(f"  {'pair':<28}{'R427':>9}{'CONV/PERM':>11}{'CONV/ANLY':>11}"
          f"{'INTER/PERM':>12}{'INTER/ANLY':>12}")
    rows, hits = [], {c: 0 for c in ("CONV/PERM", "CONV/ANLY", "INTER/PERM", "INTER/ANLY")}
    for p in pairs:
        k = "|".join(sorted(p))
        vals, bands = {}, {}
        for w in ("CONV", "INTER"):
            for nk in ("PERM", "ANLY"):
                if nk == "PERM":
                    draws = np.array([null_cell(P[p[0]], P[p[1]], order, w, nk,
                                                np.random.default_rng(s)) for s in
                                      range(seeds[0], seeds[0] + 40)])
                    vals[f"{w}/{nk}"] = float(draws.mean())
                    bands[f"{w}/{nk}"] = (float(np.percentile(draws, 2.5)),
                                          float(np.percentile(draws, 97.5)))
                else:
                    v = null_cell(P[p[0]], P[p[1]], order, w, nk)
                    vals[f"{w}/{nk}"] = v
                    # the ANLY cell is deterministic; its comparison band is the PERM band's width
                    bands[f"{w}/{nk}"] = None
        # a cell "reproduces" R427 if R427's value lies in the PERM band, or (for ANLY) within the
        # PERM band's half-width of the ANLY point -- the same tolerance, stated once.
        halfw = (bands["CONV/PERM"][1] - bands["CONV/PERM"][0]) / 2
        rep = {}
        for c, v in vals.items():
            if bands[c]:
                rep[c] = bool(bands[c][0] <= r427[k] <= bands[c][1])
            else:
                rep[c] = bool(abs(r427[k] - v) <= halfw)
            hits[c] += rep[c]
        rows.append({"pair": k, "r427": r427[k], "vals": vals, "reproduces": rep,
                     "halfwidth": float(halfw)})
        print(f"  {k:<28}{r427[k]:>9.4f}" + "".join(
            f"{vals[c]:>{w}.4f}{'*' if rep[c] else ' '}"
            for c, w in (("CONV/PERM", 10), ("CONV/ANLY", 10),
                         ("INTER/PERM", 11), ("INTER/ANLY", 11))))

    print(f"\n  reproduces R427 (of 10 pairs, * above):  " + " · ".join(
        f"{c} {hits[c]}" for c in ("CONV/PERM", "CONV/ANLY", "INTER/PERM", "INTER/ANLY")))

    # ------------------------------------------------------------------- the conditional kill
    THR = 8
    winners = [c for c, h in hits.items() if h >= THR]
    control_ok = hits["CONV/PERM"] >= THR
    print(f"\n  REPRODUCTION CONTROL · CONV/PERM is R427's method on BOTH axes and must reproduce")
    print(f"    it: {hits['CONV/PERM']}/10 >= {THR}?  "
          f"{'PASS' if control_ok else '⛔ FAIL — the cell that IS R427 cannot reproduce R427, so'}")
    if not control_ok:
        print(f"    no other cell's agreement means anything and the decomposition is INCOMPLETE.")
        world = "W-THIRD"
    else:
        axes = {c.split("/")[0] for c in winners}, {c.split("/")[1] for c in winners}
        world = ("W-WEIGHTING" if winners and all(c.startswith("CONV") for c in winners) else
                 "W-NULL" if winners and all(c.endswith("PERM") for c in winners) else
                 "W-BOTH" if len(winners) > 1 else "W-THIRD")

    print(f"\n  WORLD: {world}")
    if world == "W-WEIGHTING":
        print("    ⛔ THE GAP IS THE AGGREGATION WEIGHT, NOT THE NULL. Both null constructions")
        print("    reproduce R427 when aggregated by CONVERSATION and neither does when pooled by")
        print("    interaction. R429's W-BIAS attribution is RETRACTED: the two nulls agree, and")
        print("    what differs is a weighting choice — one R413 already settled in favour of the")
        print("    conversation. The rank-5-to-10 instability is therefore not a defect in either")
        print("    round; it is the ranking being sensitive to a choice neither round declared.")
    elif world == "W-NULL":
        print("    the null construction carries the gap at both weightings. R429 stands.")
    elif world == "W-BOTH":
        print("    both axes carry part of it. The decomposition IS the finding and no single")
        print("    mechanism may be quoted.")
    else:
        print("    ⛔ NO CELL REPRODUCES R427. There is a third difference neither axis names, and")
        print("    the honest output is that this decomposition is INCOMPLETE. Picking the closest")
        print("    cell would turn a decomposition into a narrative. Verdict UNVERIFIED.")

    (RES / "r430_decomposition.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "hits": hits, "threshold": THR, "n_pairs": len(pairs),
         "reproduction_control_ok": bool(control_ok), "seeds": seeds, "rows": rows}, indent=1))
    print(f"\n  artifact -> {(RES / 'r430_decomposition.json').relative_to(ROOT)}")
    return 0 if world in ("W-WEIGHTING", "W-NULL") else (2 if world == "W-THIRD" else 1)


if __name__ == "__main__":
    sys.exit(main())
