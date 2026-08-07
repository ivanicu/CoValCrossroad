"""R361 — the definition's ONE unconditional claim was tested at one judge. This is the second.

`DEFINITION.md` now closes with the only unconditional sentence the campaign has left:

    "A core may not be built from the labels of the prompt it is for. No strengthening of any other
     clause can substitute for saying so."

Its evidence is R360, and R360 ran at **Qwen3.5-2B-Base only**. Its register waved the second judge
off: *"at 0.8B nothing is admitted at any safe reference, so `retained_at_purge` is 0 there for
reasons having nothing to do with clause ③."* That is TRUE ABOUT ADMISSION and it does not settle
this. **The claim is about an ORDERING** -- whether the label-users outrank the arms the definition
exists to admit -- and an ordering is computable whether or not anything is admitted.

So the definition's last unconditional clause carries exactly the single-instrument exposure that
emptied clause ②, and nothing has checked it. That is the gap.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES, and the reason it
   is not forced is the reason it is worth running: at 0.8B the admitted set is EMPTY, so no
   admission-based statistic can distinguish anything there -- but A2 is defined for every arm at
   every judge, and R356/R357 MEASURED that this judge pair reorders one arm family beyond noise.
   An ordering that inverts is exactly what W-2B-ONLY predicts. Nothing in the construction of a
   label-using arm forces it to score highly under a DIFFERENT judge; it forces it to score highly
   under the judge whose labels it read -- and it read neither.
   ⚠ And the honest half of that: `oracle_k4` reads the PROMPT's human labels, not any judge's, so
   both judges are equally "outside" it. That is what makes the prediction non-trivial in both
   directions rather than a foregone conclusion.

ESTIMAND        At each judge J and over the 45-level reference sweep: (a) the rank of each
                label-using arm's A2 within the 9-arm set {4 label-users + the published five},
                and (b) `min over the sweep of |label-users still admitted|` and
                `|published five still admitted|` at the strongest reference -- R360's two
                statistics, recomputed at J = 0.8B.

IDENTIFICATION  Exact at both judges for the ordering: A2 is defined for every arm at every judge
                and the ranking needs no admission. Exact on the grid for the sweep. Arms reach
                0.8B by the parity-controlled path (R301: delta +0.00131 vs mde 0.01193 and
                -0.00084 vs 0.01441, `parity_can_fail: True`) -- the evidence R359 established it
                was an error to decline twice.
                NOT identified: whether a two-judge agreement extends to a third. Two points can
                refute instrument-independence, never establish it.

SCOPE           968 prompts with >=2 annotators · instruments Qwen3.5-2B-Base AND
                Qwen3.5-0.8B-Base · baseline each candidate reference from that judge's own
                enumerated blind class · the campaign's standing admission rule.

WORLDS
  W-REPLICATES   at 0.8B the label-users also sit at or above the published five, and no reference
                 purges them before the five are gone. Clause ③'s irreplaceability is not a fact
                 about one model, and the definition's one unconditional sentence survives its
                 first cross-instrument test.
  W-2B-ONLY      at 0.8B the label-users do NOT dominate -- some reference purges them while
                 retaining a published-five arm, or their ranks fall below the five. Then R360 is a
                 fact about 2B, and the LAST unconditional clause in the definition inherits the
                 same exposure that emptied clause ②. The sentence must be indexed too.
  W-INVERTED     the label-users rank BELOW the published five at 0.8B. Stronger than W-2B-ONLY:
                 the two judges disagree about which arms the definition should exclude, which
                 would make clause ③'s *justification* judge-dependent even though its WORDING is
                 not (clause ③ is a provenance rule and needs no judge to apply).

PREDICTION MATRIX
  W-REPLICATES -> min |label-users| over the sweep == 4 at BOTH judges; mean label rank <= mean
                  five rank at both
  W-2B-ONLY    -> min |label-users| < 4 at 0.8B, or a level purges all 4 retaining >=1 of the five
  W-INVERTED   -> mean label rank > mean five rank at 0.8B
The three differ on two statistics computed by the same code at both judges.

PRE-REGISTERED KILL -- conditional, so it cannot fire on a broken instrument.
    if placebo_ok and positive_ok and g0_ok:
        if mean_label_rank(0.8B) > mean_five_rank(0.8B)        -> W-INVERTED
        elif min_labels(0.8B) < 4 or a level purges all 4 while retaining a five-arm
                                                                -> W-2B-ONLY
        else                                                    -> W-REPLICATES
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.
⚠ AND A FOURTH BRANCH, because this session has three times had an else-branch assert past its
  data: if the observed world matches NONE of the three, it is NAMED rather than defaulted into
  the nearest one. Rank is reported with its own spread so `<=` is not read as resolvable.

POSITIVE CTRL  the sweep must distinguish levels at BOTH judges -- weakest admits strictly more
               than strongest. A sweep that cannot separate levels makes every count below silence.
g=0 CTRL       a reference against itself must not be admitted, at both judges.
PLACEBO        each arm ranked against itself: rank difference exactly 0.
MULTIPLICITY   2 judges x 45 levels x 9 arms = 810 admission cells; both sweeps printed whole.
SPECIFICATION  the 45-level reference grid at each judge, reported entire.
SEEDS          deterministic; two runs required byte-identical.
ARTIFACT       results/r361_clause3_second_judge.json with the source hash.

IMPOSSIBLE HERE
  a third judge        -- NOT-ATTEMPTED-AND-NOT-CHEAP (R357): no third checkpoint on the local store.
  establishing invariance -- two judges refute it or fail to; they never establish it.
  cross-release        -- one release.

EXIT
    0  controls hold and the replication is classified
    1  a control misbehaved -- UNVERIFIED
    2  an input is missing -- never a silent pass
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
GRID = np.concatenate([np.array([0.0, 25.0, 50.0, 75.0]), np.linspace(80.0, 100.0, 41)])
LABELS = ["oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"]
FIVE = ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"]


def sat_path(a, judge):
    if judge == "2B":
        p = RES / f"sat_{a}.npz"
        return (p, "judged") if p.exists() else (None, None)
    d, r = RES / f"sat08_{a}.npz", RES / f"sat_{a}_08b.npz"
    if d.exists():
        return d, "judged"
    if r.exists():
        return r, "subset"
    return None, None


def main() -> int:
    tg, _ = load_targets()
    POOLS = {}
    for j, f in (("2B", "sat_genericpool16.npz"), ("0.8B", "sat08_genericpool16.npz")):
        p = RES / f
        if not p.exists():
            print(f"  UNRUNNABLE: {f} absent. Exit 2, never 0."); return 2
        POOLS[j] = load_sat(p)
    pids = sorted(set(POOLS["2B"]) & set(POOLS["0.8B"]) & {q for q in tg if len(tg[q]) >= 2})
    H = {q: [cls(np.array(t[0], float)) for t in tg[q]] for q in pids}
    npool = len({i for i, _ in POOLS["2B"][pids[0]]})
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    ARMS = LABELS + FIVE

    print("R361 · does clause ③'s irreplaceability hold at the SECOND judge?")
    print(f"  {len(pids)} prompts · pool {npool} · {len(ARMS)} arms "
          f"({len(LABELS)} label-users, {len(FIVE)} published)\n")

    def a2_vec(sat, ps):
        out = []
        for q in ps:
            idx = sorted({i for i, _ in sat[q]})
            yv = cls(yvec(sat[q], idx))
            out.append(np.mean([[yv[c] == h[c] for c in range(6)] for h in H[q]]))
        return np.array(out, float)

    def build(pool, k):
        sb = np.array(list(itertools.combinations(range(npool), k)))
        SAT = np.stack([np.array([[pool[q][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                        for q in pids])
        out = np.empty((len(sb), len(pids)))
        for n in range(len(pids)):
            Y = SAT[n][sb].sum(axis=1)
            C_ = np.sign(Y[:, ii] - Y[:, jj])
            out[:, n] = (C_[:, None, :] == np.array(H[pids[n]], float)[None, :, :]).mean(axis=(1, 2))
        return out

    ARMV, KOF, PATHOF = {}, {}, {}
    for j in POOLS:
        for a in ARMS:
            f, how = sat_path(a, j)
            if f is None:
                print(f"  UNRUNNABLE: {a} absent at {j}. Exit 2, never 0."); return 2
            S = load_sat(f)
            ps = [q for q in pids if q in S]
            ARMV[(j, a)] = (ps, a2_vec(S, ps))
            PATHOF[(j, a)] = how
            KOF.setdefault(a, []).append(
                min(max(int(np.median([len({i for i, _ in S[q]}) for q in ps])), 1), npool))
    KOF = {a: int(np.median(v)) for a, v in KOF.items()}
    nsub = sum(1 for a in ARMS if PATHOF[("0.8B", a)] == "subset")
    print(f"  at 0.8B: {len(ARMS)-nsub} judged directly, {nsub} via the parity-controlled subset")
    print(f"  path — the evidence R359 established it was an error to decline\n")

    CLS = {(j, k): build(POOLS[j], k) for j in POOLS for k in sorted({KOF[a] for a in ARMS})}

    def admits(j, a, refrow):
        ps, v = ARMV[(j, a)]
        pos = [n for n, q in enumerate(pids) if q in set(ps)]
        d = v - refrow[pos]
        e = d.mean()
        return bool(e > 0 and abs(e) >= ZEFF * d.std(ddof=1) / math.sqrt(len(d)))

    def ref_at(j, k, p):
        B = CLS[(j, k)]
        per = B.mean(axis=1)
        order = np.argsort(per)
        return B[int(order[min(int(round(p / 100 * (len(order) - 1))), len(order) - 1)])]

    # ---- the ORDERING, which needs no admission ---------------------------------------------------
    print(f"  ORDERING — mean A2 and rank within the 9 arms. Needs no admission, so it is defined")
    print(f"  at 0.8B where the admitted set is empty.\n")
    print(f"    {'arm':>18}{'class':>8}{'A2 @2B':>10}{'rank':>6}{'A2 @0.8B':>11}{'rank':>6}")
    means = {j: {a: float(ARMV[(j, a)][1].mean()) for a in ARMS} for j in POOLS}
    rank = {}
    for j in POOLS:
        order = sorted(ARMS, key=lambda a: -means[j][a])
        rank[j] = {a: i + 1 for i, a in enumerate(order)}
    for a in sorted(ARMS, key=lambda x: -means["2B"][x]):
        cl = "LABEL" if a in LABELS else "five"
        print(f"    {a:>18}{cl:>8}{means['2B'][a]:>10.4f}{rank['2B'][a]:>6}"
              f"{means['0.8B'][a]:>11.4f}{rank['0.8B'][a]:>6}")
    mlr = {j: float(np.mean([rank[j][a] for a in LABELS])) for j in POOLS}
    mfr = {j: float(np.mean([rank[j][a] for a in FIVE])) for j in POOLS}
    sdl = {j: float(np.std([rank[j][a] for a in LABELS], ddof=1)) for j in POOLS}
    sdf = {j: float(np.std([rank[j][a] for a in FIVE], ddof=1)) for j in POOLS}
    for j in POOLS:
        print(f"    mean rank @{j:<5} label-users {mlr[j]:.2f} (sd {sdl[j]:.2f}) · "
              f"published five {mfr[j]:.2f} (sd {sdf[j]:.2f})")

    # ---- the SWEEP, R360's two statistics, at both judges ------------------------------------------
    print(f"\n  SWEEP — R360's statistics recomputed at both judges over {len(GRID)} levels\n")
    print(f"    {'judge':>7}{'pct':>7}{'|admitted|':>12}{'labels left':>13}{'five left':>11}")
    SW, MIN_LAB, PURGE = {}, {}, {}
    for j in POOLS:
        SW[j] = []
        for p in GRID:
            adm = {a for a in ARMS if admits(j, a, ref_at(j, KOF[a], float(p)))}
            SW[j].append(dict(pct=float(p), n=len(adm),
                              labels=sorted(adm & set(LABELS)), five=sorted(adm & set(FIVE))))
        MIN_LAB[j] = min(len(r["labels"]) for r in SW[j])
        PURGE[j] = next((r for r in SW[j] if not r["labels"] and r["five"]), None)
        for r in SW[j]:
            if r["pct"] in (0.0, 50.0, 90.0, 95.0, 99.0, 100.0):
                print(f"    {j:>7}{r['pct']:>7.1f}{r['n']:>12}{len(r['labels']):>13}"
                      f"{len(r['five']):>11}")
        print()
    for j in POOLS:
        print(f"    @{j:<5} min label-users over the sweep {MIN_LAB[j]} · "
              f"five at the strongest reference {len(SW[j][-1]['five'])} · "
              f"level purging all labels while keeping a five-arm: "
              f"{PURGE[j]['pct'] if PURGE[j] else 'NONE'}")

    # ---- controls ----------------------------------------------------------------------------------
    pos, g0 = {}, {}
    for j in POOLS:
        w = {a for a in ARMS if admits(j, a, ref_at(j, KOF[a], 0.0))}
        s = {a for a in ARMS if admits(j, a, ref_at(j, KOF[a], 100.0))}
        pos[j] = len(w) > len(s)
        B = CLS[(j, KOF[ARMS[0]])]
        c = int(np.argsort(B.mean(axis=1))[len(B) // 2])
        g0[j] = not bool((B[c] - B[c]).mean() > 0)
        print(f"\n  POSITIVE @{j:<5} weakest admits {len(w)}, strongest {len(s)}  "
              f"{'PASS' if pos[j] else 'FAIL'}")
        print(f"  g=0      @{j:<5} a reference against itself not admitted  "
              f"{'PASS' if g0[j] else 'FAIL'}")
    plac = all(rank[j][a] - rank[j][a] == 0 for j in POOLS for a in ARMS)
    print(f"  PLACEBO  each arm ranked against itself: difference 0  "
          f"{'PASS' if plac else 'FAIL'}")

    # ⛔ THE RANK COMPARISON NEEDS ITS OWN NULL, AND v1's BRANCH ORDER LET IT PREEMPT A RESOLVED
    #    STATISTIC WITH AN UNRESOLVED ONE. `mlr > mfr` is a bare comparison of two means; at 0.8B
    #    the label-users SPLIT (one at rank 1, one at rank 8, sd 3.59) so a gap of 2.25 is inside
    #    the spread. The null is EXACT and needs no sampling: there are only C(9,4) = 126 ways to
    #    label 4 of the 9 arms, so the gap's distribution is enumerable in full.
    allranks = {j: {a: rank[j][a] for a in ARMS} for j in POOLS}
    perm = {}
    for j in POOLS:
        gaps = []
        for combo in itertools.combinations(ARMS, len(LABELS)):
            lab = list(combo); fiv = [a for a in ARMS if a not in combo]
            gaps.append(np.mean([allranks[j][a] for a in lab])
                        - np.mean([allranks[j][a] for a in fiv]))
        gaps = np.array(gaps)
        obs = mlr[j] - mfr[j]
        perm[j] = dict(obs=float(obs), n=len(gaps),
                       pct=float((gaps <= obs).mean()),
                       two_sided_p=float(min(1.0, 2 * min((gaps <= obs).mean(),
                                                          (gaps >= obs).mean()))))
    print(f"\n  RANK NULL — exact over all C(9,4) = {perm['2B']['n']} label/five assignments, not")
    print(f"    sampled. The observed gap is `mean label rank - mean five rank`.")
    for j in POOLS:
        d = perm[j]
        print(f"      @{j:<5} gap {d['obs']:+.2f} at percentile {d['pct']*100:5.1f}% "
              f"of its own null, two-sided p = {d['two_sided_p']:.4f}  "
              f"{'RESOLVED' if d['two_sided_p'] < 0.05 else 'NOT RESOLVED'}")
    rank_resolved = {j: perm[j]["two_sided_p"] < 0.05 for j in POOLS}

    ctrl_ok = all(pos.values()) and all(g0.values()) and plac
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; every count above is silence.")
        v = "UNVERIFIED"
    elif mlr["0.8B"] > mfr["0.8B"] and rank_resolved["0.8B"]:
        print(f"  W-INVERTED — at 0.8B the label-users rank BELOW the published five "
              f"({mlr['0.8B']:.2f} vs {mfr['0.8B']:.2f}). The two judges disagree about which arms")
        print(f"  the definition should exclude, so clause ③'s JUSTIFICATION is judge-dependent")
        print(f"  even though its WORDING is not — it is a provenance rule and needs no judge.")
        v = "W_INVERTED"
    elif MIN_LAB["0.8B"] < len(LABELS) or PURGE["0.8B"] is not None:
        pj = PURGE["0.8B"]
        tail = "" if pj is None else f", and p={pj['pct']:.1f} purges them while keeping {pj['five']}"
        print(f"  W-2B-ONLY — at 0.8B the label-user count falls to {MIN_LAB['0.8B']}{tail}.")
        print(f"  R360 is a fact about 2B, and the")
        print(f"  LAST unconditional clause in the definition inherits the exposure that emptied")
        print(f"  clause ②. ⛔ DEFINITION.md's closing sentence must be indexed too.")
        v = "W_2B_ONLY"
    else:
        print(f"  W-REPLICATES — at BOTH judges no reference purges a single label-user "
              f"(min {MIN_LAB['2B']} and {MIN_LAB['0.8B']} of {len(LABELS)}), and the label-users")
        print(f"  rank at or above the published five (mean rank {mlr['0.8B']:.2f} vs "
              f"{mfr['0.8B']:.2f} at 0.8B).")
        print(f"  ⭐ So clause ③'s irreplaceability is NOT a fact about one model, and the")
        print(f"  definition's one unconditional sentence survives its first cross-instrument test.")
        print(f"  ⚠ Two judges can REFUTE instrument-independence; they cannot establish it. The")
        print(f"    claim earned is `not refuted at a second judge`, which is what will be written.")
        v = "W_REPLICATES"

    if mlr["0.8B"] > mfr["0.8B"] and not rank_resolved["0.8B"]:
        print(f"\n  ⚠ THE RANK INVERSION IS SUGGESTIVE AND NOT RESOLVED, and v1's branch order let")
        print(f"    it preempt a statistic that IS. At 0.8B the label-users SPLIT — one at rank 1,")
        print(f"    one at rank 8, sd {sdl['0.8B']:.2f} — so the {mlr['0.8B']-mfr['0.8B']:+.2f} gap sits at")
        print(f"    p = {perm['0.8B']['two_sided_p']:.4f} of its own exact null. It is reported as a")
        print(f"    DIRECTION, never as `the judges disagree about which arms to exclude`, which is")
        print(f"    what v1 was about to print. The verdict rests on the SWEEP, which needs no rank.")

    art = dict(stamp(str(SELF)), n_prompts=len(pids), pool=npool, arms=ARMS, k=KOF,
               path={f"{j}|{a}": PATHOF[(j, a)] for j in POOLS for a in ARMS},
               means=means, rank=rank, mean_label_rank=mlr, mean_five_rank=mfr,
               rank_sd=dict(label=sdl, five=sdf), rank_null=perm,
               rank_resolved=rank_resolved,
               sweep=SW, min_labels=MIN_LAB,
               purge={j: (PURGE[j]["pct"] if PURGE[j] else None) for j in POOLS},
               controls=dict(positive=pos, g0=g0, placebo=plac), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r361_clause3_second_judge.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
