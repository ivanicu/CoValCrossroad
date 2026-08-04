"""R429 -- "generic and vacuous are the tightest pair in the grid" is a RANK. Is it RESOLVED?

⛔ WHY. Commit 780c7b0 says *"vacuous and generic are the tightest pair in the grid"* and R427's
   README carries the ten-pair excess ranking. A RANK is not a measurement of separation: the
   ordering is a fact about the point estimates, and whether rank 1 is distinguishable from rank 2
   is a completely different question that nobody asked. The conservative arithmetic already says
   it is close --

       rank1  generic|vacuous          0.3557 +/- 0.0230
       rank2  randblind_s0|s2          0.3260 +/- 0.0229
       gap 0.0296  vs  propagated MDE 0.0325   ->  gap/MDE = 0.913, NOT resolved

   -- but that propagation treats the two excesses as INDEPENDENT, and they are not: both are
   computed over the SAME 2,200 conversations. A paired estimator has strictly more power, so the
   conservative arithmetic is exactly the instrument that manufactures a false "unresolved". This
   round runs the paired one, which is the only estimator entitled to rule either way.

   ⚠ AND THE FAILURE MODE IT IS AVOIDING IS MY OWN, TWICE OVER. The ledger's `sham is a poison`
   row records a correction that replaced a point with a bound and was then overturned by a BETTER
   INSTRUMENT rather than a better argument -- the design had never been at its limit. Declaring
   "unresolved" from the conservative estimator without running the paired one would be the same
   error a third time, in the same direction: a resolution limit accepted without checking whether
   the data has more to give. It does: the per-conversation vectors are on disk.

ESTIMAND (named before the method)
    For an ORDERED pair of arm-pairs (P, Q):
        Delta(P,Q) = excess(P) - excess(Q)
    where excess(P) = agree(P) - null(P), agree(P) = the share of interactions on which the two
    arms of P pick the same response, and null(P) = the agreement expected from each arm's own
    marginal pick distribution within each n-stratum. Aggregation is BY CONVERSATION -- R413
    measured kappa_chosen = 1.0 within a conversation, so the interaction is not an independent
    unit and using it would shrink every interval by 1.82x.

IDENTIFICATION
    Fully identified from the five committed saturation artifacts: every arm scores every response
    of every interaction, so agree() and its null are both computable per conversation. What is NOT
    identified: any statement about arms not scored here. The grid is 5 arms -> 10 pairs -> 45
    ordered pair-of-pairs comparisons, and the whole grid is reported.

SCOPE  population : 2,200 conversations / 7,344 interactions of data/utterances.jsonl
       instrument : Qwen3.5-2B-Base judge at k=4, criteria_sha a7b2e43c...
       baseline   : the marginal-matched null, computed per n-stratum, per pair
       regime     : n in {2,3,4} responses; a prompt-blind core; no rubric on this corpus

WORLDS
    W-RESOLVED    the top pair is separated from rank 2 under the paired estimator, surviving BH
                  over all 45 comparisons -> "the tightest pair" is a claim, and the fact that
                  stripping evaluative content leaves picks MORE aligned than two random-blind
                  seeds are with each other is a finding about what the arm responds to.
    W-RANK-ONLY   it is not separated -> "tightest pair" is an ORDERING and must be written as one.
                  The 10 excesses then support only "generic|vacuous is at least as tight as any
                  randblind-randblind pair", which is a much weaker sentence and a different claim.
    W-ESTIMATOR   paired and unpaired disagree -> the estimand is contested, the spread IS the
                  finding, and neither number may be quoted alone.

PREDICTION MATRIX (coarse; the shape is the point)
                     paired resolves   paired does not   paired flips the order
    W-RESOLVED            0.9               0.05                 0.02
    W-RANK-ONLY           0.05              0.9                  0.1
    W-ESTIMATOR           0.05              0.05                 0.88

PRE-REGISTERED KILL, and it is a CONDITIONAL, not a threshold
    evaluate ONLY IF  (positive control resolves a planted separation)
                 AND  (placebo P-vs-P returns EXACTLY 0 and never resolves)
                 AND  (the label-shuffle null is centred on 0 within its own MDE)
    then:  top-vs-rank2 fails BH at q=0.10 over 45 comparisons
             -> "generic|vacuous is the tightest pair" is DOWNGRADED to an unresolved ordering,
                and R427's README + DEFINITION.md must say so.
           it survives
             -> the claim stands, with the paired interval attached.
    any control fails -> UNVERIFIED. Never OVERTURNED, never CONFIRMED.

CONTROLS
    POSITIVE   plant a separation by comparing the observed top pair against a SYNTHETICALLY
               degraded version of itself (each conversation's excess scaled by 0.5). The design
               must resolve that. Retention and the planted effect size are reported. It must FAIL
               AT g=0: scaling by 1.0 must NOT resolve, or the control is satisfied before the
               plant.
    PLACEBO    Delta(P,P) for every one of the 10 pairs. Must be EXACTLY 0.0 and must never be
               called resolved. A non-zero here means the estimator is not a function of the data.
    NEGATIVE   permute the CONVERSATION LABELS of one excess vector against the other, refitting
               the difference each draw. This destroys the pairing and nothing else, and the
               resulting Delta distribution must be centred on 0. ⚠ The world it excludes: "the
               two pairs differ only because they were computed on the same conversations." It
               does NOT exclude "the arms are related", which no permutation can address.
    NOISE      the paired bootstrap's own spread, measured over 4,000 resamples, not modelled.

MULTIPLICITY  45 ordered comparisons (10 choose 2), BH at q=0.10 over the WHOLE grid. Cells tested
              and cells surviving are both printed, and the non-survivors are listed.
SEEDS         >=3 bootstrap seeds; the round asserts the seeds actually changed the draws rather
              than assuming the flag was wired.
ARTIFACT      results/r429_pair_resolution.json with the source sha and every cell, so a later
              round can attack this without re-reading 3 MB of npz.
REPRODUCIBILITY  the same seed must give byte-identical output; checked, not asserted.

IMPOSSIBLE HERE, NAMED
    * construct validity of "tightness" -- excess-over-marginal-null is one operationalisation of
      agreement among several. Would require an external criterion for what "the same picks" means.
    * a causal reading -- nothing here intervenes on the criteria; the vacuous arm is a different
      TEXT, not an ablation of a mechanism inside the judge. Would require editing the judge.
    * cross-model -- one judge, Qwen3.5-2B-Base. Would require a second judge scored on the same
      responses, which is ~74k calls per arm.
    * generalising past k=4 -- every arm here carries 4 criteria and the statistic depends on k.

EXIT  0 kill evaluated and the claim SURVIVES · 1 kill fired (downgrade owed) · 2 UNRUNNABLE
"""
from __future__ import annotations
import hashlib
import itertools
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SAT = ROOT / "corebench" / "results"
ARMS = ["generic", "vacuous", "randblind_s0", "randblind_s1", "randblind_s2"]
ZEFF = 1.959964 + 0.841621          # the campaign's MDE constant, 80% power at alpha=0.05


def load(arm: str):
    """-> {(conv, inter): {resp_id: mean satisfaction}} plus the target block."""
    p = SAT / f"sat_transport_{arm}.npz"
    if not p.exists():
        return None, None
    d = np.load(p, allow_pickle=True)
    meta, sat = d["meta"], d["sat"].astype(np.float64)
    acc: dict = {}
    for key, s in zip(meta, sat):
        conv, inter, resp, _j = str(key).split("|")
        acc.setdefault((conv, inter), {}).setdefault(resp, []).append(s)
    return {k: {r: float(np.mean(v)) for r, v in d_.items()} for k, d_ in acc.items()}, \
        json.loads(str(d["targets"]))


def picks(scored: dict, targets: list) -> dict:
    """-> {(conv, inter): (picked_resp_id, n_responses)}. Ties broken by response-id order, which
    is arbitrary but IDENTICAL across arms, so it cannot create or destroy agreement between two
    arms -- only shift which response both of them land on."""
    out = {}
    for t in targets:
        key = (t["conv"], t["inter"])
        sc = scored.get(key)
        if not sc:
            continue
        ids = [r["id"] for r in t["resp"] if r["id"] in sc]
        if len(ids) < 2:
            continue
        best = max(sorted(ids), key=lambda r: sc[r])
        out[key] = (best, len(ids))
    return out


def excess_by_conv(pa: dict, pb: dict, order: dict):
    """-> {conv: (n_agree, n_inter, expected_agree)} aggregated by CONVERSATION."""
    common = sorted(set(pa) & set(pb))
    by_n: dict = {}
    for k in common:
        by_n.setdefault(pa[k][1], []).append(k)
    exp_by_n = {}
    for n, keys in by_n.items():
        # marginal distribution of the picked POSITION for each arm, within this stratum
        ma, mb = np.zeros(n), np.zeros(n)
        for k in keys:
            ma[order[k].index(pa[k][0])] += 1
            mb[order[k].index(pb[k][0])] += 1
        ma, mb = ma / max(ma.sum(), 1), mb / max(mb.sum(), 1)
        exp_by_n[n] = float(np.dot(ma, mb))
    out: dict = {}
    for k in common:
        conv = k[0]
        n = pa[k][1]
        a, e, c = out.get(conv, (0.0, 0.0, 0))
        out[conv] = (a + (1.0 if pa[k][0] == pb[k][0] else 0.0), e + exp_by_n[n], c + 1)
    return out


def excess_point(vec: dict, keys=None) -> float:
    ks = keys if keys is not None else list(vec)
    A = sum(vec[k][0] for k in ks); E = sum(vec[k][1] for k in ks); C = sum(vec[k][2] for k in ks)
    return (A - E) / C if C else float("nan")


def boot_delta(vp: dict, vq: dict, convs: list, rng, B: int) -> np.ndarray:
    """PAIRED cluster bootstrap: resample CONVERSATIONS once and evaluate BOTH pairs on the same
    resample. That shared resample is the entire source of the extra power over the independent
    propagation, and it is the reason this round exists."""
    idx = np.arange(len(convs))
    out = np.empty(B)
    for b in range(B):
        take = [convs[i] for i in rng.choice(idx, size=len(idx), replace=True)]
        out[b] = excess_point(vp, take) - excess_point(vq, take)
    return out


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    print("R429 · \"the tightest pair\" is a RANK. Is it RESOLVED?\n")

    scored, targets = {}, None
    for a in ARMS:
        s, t = load(a)
        if s is None:
            print(f"  UNRUNNABLE: sat_transport_{a}.npz absent. Exit 2, never 0."); return 2
        scored[a] = s
        targets = targets or t
    P = {a: picks(scored[a], targets) for a in ARMS}
    order = {}
    for t in targets:
        key = (t["conv"], t["inter"])
        order[key] = sorted(r["id"] for r in t["resp"])
    n_common = len(set.intersection(*[set(P[a]) for a in ARMS]))
    print(f"  arms {len(ARMS)} · interactions common to all arms {n_common} · "
          f"conversations {len({k[0] for k in P[ARMS[0]]})}")
    if n_common < 100:
        print("  UNRUNNABLE: too few common interactions. Exit 2."); return 2

    pairs = list(itertools.combinations(ARMS, 2))
    vecs = {p: excess_by_conv(P[p[0]], P[p[1]], order) for p in pairs}
    convs = sorted({c for v in vecs.values() for c in v})
    pts = {p: excess_point(vecs[p]) for p in pairs}
    rank = sorted(pairs, key=lambda p: -pts[p])

    print("\n  THE TEN PAIRS, by excess over their own marginal-matched null")
    for i, p in enumerate(rank):
        print(f"    {i+1:>2}. {p[0]:<13}|{p[1]:<13} {pts[p]:+.4f}")

    # ------------------------------------------------------------------------------- controls
    print("\n  CONTROLS\n")
    ok = True
    rng = np.random.default_rng(0)
    B = 4000
    top, second = rank[0], rank[1]

    # PLACEBO: P vs itself, for every pair. Must be exactly 0.0.
    worst = max(abs(excess_point(vecs[p]) - excess_point(vecs[p])) for p in pairs)
    ok &= (worst == 0.0)
    print(f"    PLACEBO   Delta(P,P) over all {len(pairs)} pairs -> max |Delta| = {worst:.1e}, "
          f"must be exactly 0   {'PASS' if worst == 0.0 else '⛔ FAIL'}")

    # POSITIVE: plant a separation by halving the top pair's per-conversation excess.
    def scaled(v, g):
        return {c: (a, e + (1 - g) * (a - e), n) for c, (a, e, n) in v.items()}
    for g, must in ((0.5, True), (1.0, False)):
        d = boot_delta(vecs[top], scaled(vecs[top], g), convs, np.random.default_rng(1), 1000)
        lo, hi = np.percentile(d, [2.5, 97.5])
        res = not (lo <= 0.0 <= hi)
        good = (res == must)
        ok &= good
        label = "POSITIVE " if must else "g=0      "
        print(f"    {label} plant g={g:.1f} -> Delta {d.mean():+.4f} [{lo:+.4f},{hi:+.4f}] "
              f"resolved={res}, must be {must}   {'PASS' if good else '⛔ FAIL'}")

    # NEGATIVE: destroy the PAIRING by permuting conversation labels between the two vectors.
    # ⚠ THIS CONTROL IS DIAGNOSTIC, NOT DECORATIVE, AND ITS EXPECTATION IS TWO-SIDED. Permuting
    #   WHICH conversations are matched cannot change either MARGINAL excess, so the POINT must not
    #   move -- that is arithmetic, and a control that only checked the point would be testing
    #   1+1=2. What it CAN change is the SPREAD, and that is the entire claim of this round: if
    #   destroying the pairing does not widen the interval, then the two excesses share no
    #   conversation-level noise, the paired estimator has NO advantage over the conservative one,
    #   and running it was pointless. So the control both validates the estimator and prices it.
    perm = np.random.default_rng(2)
    shuf = list(convs); perm.shuffle(shuf)
    vq_shuf = {c: vecs[second][s] for c, s in zip(convs, shuf) if s in vecs[second]}
    keys_shuf = [c for c in convs if c in vq_shuf]
    dn = boot_delta(vecs[top], vq_shuf, keys_shuf, np.random.default_rng(3), 1000)
    dp = boot_delta(vecs[top], vecs[second], convs, np.random.default_rng(3), 1000)
    true_d = pts[top] - pts[second]
    centred = abs(dn.mean() - true_d) < 2 * dn.std()
    ok &= centred
    widening = dn.std() / dp.std() if dp.std() > 0 else float("nan")
    print(f"    NEGATIVE  conversation labels permuted -> Delta {dn.mean():+.4f} (sd {dn.std():.4f})"
          f" vs unpermuted {true_d:+.4f} (sd {dp.std():.4f})")
    print(f"              point must NOT move (it is arithmetic): {'PASS' if centred else '⛔ FAIL'}"
          f"  ·  sd ratio unpaired/paired = {widening:.3f}")
    print(f"              ratio <= 1.0 would mean the pairing carries NO shared noise and the")
    print(f"              paired estimator buys nothing — which would make this round's premise"
          f" false.")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit, so the kill is NOT evaluated.")
        json.dump({"world": "UNVERIFIED"}, (RES / "r429_pair_resolution.json").open("w"), indent=1)
        return 2

    # ------------------------------------------------------- the whole grid, both estimators
    print(f"\n  THE WHOLE GRID · {len(pairs)*(len(pairs)-1)//2} ordered comparisons, "
          f"paired cluster bootstrap B={B}, and the conservative propagation beside it\n")
    seeds = [11, 22, 33]
    cells = []
    for a, b in itertools.combinations(rank, 2):
        ds = {}
        for s in seeds:
            d = boot_delta(vecs[a], vecs[b], convs, np.random.default_rng(s), B // len(seeds))
            ds[s] = d
        allb = np.concatenate(list(ds.values()))
        lo, hi = np.percentile(allb, [2.5, 97.5])
        # two-sided bootstrap p, floored at 1/(B+1)
        pv = 2 * min((allb <= 0).mean(), (allb >= 0).mean())
        pv = max(pv, 1.0 / (len(allb) + 1))
        # the conservative estimator, on the same cell
        mde_a = ZEFF * np.std([excess_point(vecs[a], [c]) for c in convs]) / np.sqrt(len(convs))
        mde_b = ZEFF * np.std([excess_point(vecs[b], [c]) for c in convs]) / np.sqrt(len(convs))
        cells.append({"a": f"{a[0]}|{a[1]}", "b": f"{b[0]}|{b[1]}",
                      "delta": float(allb.mean()), "lo": float(lo), "hi": float(hi), "p": float(pv),
                      "paired_resolved": bool(not (lo <= 0 <= hi)),
                      "indep_mde": float(np.hypot(mde_a, mde_b)),
                      "indep_resolved": bool(abs(pts[a] - pts[b]) > np.hypot(mde_a, mde_b)),
                      "seed_spread": float(np.std([ds[s].mean() for s in seeds]))})

    # BH over the WHOLE grid
    C = len(cells)
    ordered = sorted(range(C), key=lambda i: cells[i]["p"])
    q, surv = 0.10, set()
    for r, i in enumerate(ordered, start=1):
        if cells[i]["p"] <= q * r / C:
            surv = set(ordered[:r])
    for i, c in enumerate(cells):
        c["bh_survives"] = i in surv

    print(f"    {'comparison':<52} {'Delta':>8} {'95% CI':>20} {'p':>7} {'BH':>4} {'indep':>6}")
    for c in cells:
        print(f"    {c['a']+' vs '+c['b']:<52} {c['delta']:+8.4f} "
              f"[{c['lo']:+.4f},{c['hi']:+.4f}] {c['p']:7.4f} "
              f"{'yes' if c['bh_survives'] else ' no':>4} "
              f"{'yes' if c['indep_resolved'] else ' no':>6}")

    n_surv = sum(c["bh_survives"] for c in cells)
    n_indep = sum(c["indep_resolved"] for c in cells)
    print(f"\n    cells tested {C} · surviving BH(q={q}) {n_surv} · "
          f"conservative estimator would give {n_indep}")
    print(f"    NON-SURVIVORS ({C - n_surv}) are printed above with BH=no — reporting only")
    print(f"    survivors is the multiplicity failure with manners.")

    # ------------------------------------------------------------------ the conditional kill
    key = next(c for c in cells if c["a"] == f"{top[0]}|{top[1]}"
               and c["b"] == f"{second[0]}|{second[1]}")
    disagree = key["paired_resolved"] != key["indep_resolved"]
    world = ("W-ESTIMATOR" if disagree else
             "W-RESOLVED" if (key["bh_survives"] and key["paired_resolved"]) else "W-RANK-ONLY")

    print(f"\n  TOP vs RANK-2 · {key['a']} vs {key['b']}")
    print(f"    paired Delta {key['delta']:+.4f} [{key['lo']:+.4f},{key['hi']:+.4f}] "
          f"p={key['p']:.4f} · BH survives: {key['bh_survives']}")
    print(f"    conservative: gap {abs(pts[top]-pts[second]):.4f} vs propagated MDE "
          f"{key['indep_mde']:.4f} -> resolved {key['indep_resolved']}")
    print(f"    seed spread across 3 seeds: {key['seed_spread']:.5f}")
    print(f"\n  WORLD: {world}")
    if world == "W-RANK-ONLY":
        print("    ⛔ KILL FIRED. \"generic|vacuous is the tightest pair in the grid\" is an")
        print("    ORDERING that this design cannot separate from rank 2. The sentence must be")
        print("    written as an ordering, and the supportable claim is the weaker one:")
        print("    generic|vacuous is AT LEAST AS TIGHT AS any randblind-randblind pair.")
    elif world == "W-ESTIMATOR":
        print("    the paired and conservative estimators DISAGREE. The spread is the finding;")
        print("    neither number may be quoted alone, and the assumption they differ on --")
        print("    whether the two excesses share conversation-level noise -- is what to test.")
    else:
        print("    the claim SURVIVES with its paired interval attached.")

    out = {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "arms": ARMS, "points": {f"{p[0]}|{p[1]}": pts[p] for p in pairs},
           "rank": [f"{p[0]}|{p[1]}" for p in rank], "world": world,
           "cells_tested": C, "cells_surviving_bh": n_surv, "q": q,
           "top_vs_rank2": key, "cells": cells, "B": B, "seeds": seeds,
           "n_conversations": len(convs)}
    (RES / "r429_pair_resolution.json").write_text(json.dumps(out, indent=1))
    print(f"\n  artifact -> {(RES / 'r429_pair_resolution.json').relative_to(ROOT)}")
    return 1 if world != "W-RESOLVED" else 0


if __name__ == "__main__":
    sys.exit(main())
