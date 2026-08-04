"""R427/arm_agreement -- do generic and randblind make the SAME PICKS, or just the same score?

`generic` 0.4374 and `randblind_s0` 0.4397 differ by -0.0024 against an MDE of 0.0189. Two arms
landing at the same ACCURACY is weak evidence that their criteria do not matter: two genuinely
different rankers can be equally wrong in different places and produce identical means.

⭐ THE SHARP VERSION IS PER-INTERACTION AGREEMENT. If the two arms pick the SAME response far more
   often than two rules with their marginals would by chance, then the judge produces nearly the same
   ordering whatever it is asked -- and the criteria are close to inert as an INPUT, not merely
   equal as an OUTPUT. That is a much stronger statement than `their means are within noise`, and it
   is the one the round has been circling.

⛔ ARITHMETIC TRAP. Two rules over n responses agree at 1/n by chance -- forced, a derivation. What
   is NOT forced is the observed rate, nor how far it sits above a null that PRESERVES each arm's
   own pick distribution while destroying the pairing.

ESTIMAND        (A) P(generic's argmax == randblind's argmax), per response-count stratum;
                (B) the same under a null that shuffles randblind's picks across interactions WITHIN
                    a stratum -- preserving both arms' marginal pick distributions, destroying only
                    the pairing;
                (C) the excess of (A) over (B).

IDENTIFICATION  Exact. Both arms' picks are deterministic given their committed satisfaction.

SCOPE           population: interactions present in BOTH committed arms · instrument: the two arms'
                own argmaxes, mean aggregation · baseline: the shuffled-pairing null · regime: k=4,
                prompt-blind, 2,200 seeded conversations. Nothing here touches `if_chosen`.

WORLDS
  W-SAME-ORDERING    agreement far exceeds the shuffled null. The judge's ranking is largely
                     independent of which criteria it is handed; the criteria are inert as an INPUT,
                     and `generic - randblind ~ 0` is not a coincidence of two means.
  W-DIFFERENT-RULES  agreement sits near the shuffled null. Then the two arms rank differently and
                     merely score alike -- equally wrong in different places -- and the criteria DO
                     change the ordering even though they do not change the accuracy.

PREDICTION MATRIX
  W-SAME-ORDERING   -> agreement >> null, excess resolvable against its MDE
  W-DIFFERENT-RULES -> agreement within MDE of the null

PRE-REGISTERED KILL -- conditional on both controls firing.
    if self-agreement == 1.0 exactly and a random picker agrees at ~1/n:
        excess over the shuffled null > its MDE -> W-SAME-ORDERING
        else                                    -> W-DIFFERENT-RULES
    else: UNVERIFIED -- the agreement estimator is unfit.

CONTROLS
  SELF (+)      generic against ITSELF must agree at exactly 1.0. An estimator that cannot return 1
                on an identical pair cannot be trusted with a partial one.
  RANDOM (-)    generic against a seeded uniform picker must agree at ~1/n within MDE. This is the
                floor, and it is what makes a high rate mean something.
  SHUFFLE       the null preserves each arm's own marginal pick distribution and destroys ONLY the
                pairing. ⚠ It answers `did the pairing matter`, never WHY -- the world it excludes is
                exactly `the two arms' picks are independent given their marginals`.
  NO-TARGET     nothing here reads `if_chosen`. Stated because every accuracy in this round does, and
                an agreement effect must not be readable as an accuracy effect.
  STRATIFIED    per response count, because 1/n differs and pooling is the error caught twice already.

MULTIPLICITY    strata x 3 quantities; every stratum printed.
ARTIFACT        results/r427_arm_agreement.json with the source hash.

IMPOSSIBLE HERE
  a claim about prompt-SPECIFIC cores -- both arms are prompt-blind by construction.
  WHY the judge ranks as it does       -- needs mechanistic access this design does not have.

EXIT
    0  the controls hold and a branch is reached
    1  a control misbehaved -- UNVERIFIED
    2  an arm is absent -- never a silent pass
"""
from __future__ import annotations
import collections
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
ZEFF = 1.959964 + 0.841621


def picks(tag):
    p = RES / f"sat_transport_{tag}.npz"
    if not p.exists():
        return None, None
    with np.load(p, allow_pickle=True) as d:
        meta, sat = [str(x) for x in d["meta"]], np.asarray(d["sat"], float)
        tgt = json.loads(str(d["targets"]))
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    for m, v in zip(meta, sat):
        c, i, r, _j = m.split("|")
        per[(c, i)][r].append(v)
    out = {}
    for k, row in per.items():
        s = {r: float(np.mean(v)) for r, v in row.items()}
        top = max(s.values())
        out[k] = sorted([r for r in s if s[r] == top])[0]
    return out, {(t["conv"], t["inter"]): t for t in tgt}


def clus(by):
    a = np.array([np.mean(v) for v in by.values() if v], float)
    if len(a) < 2:
        return None
    return float(a.mean()), float(ZEFF * a.std(ddof=1) / np.sqrt(len(a))), len(a)


def main() -> int:
    g, tg = picks("generic")
    r, _ = picks("randblind_s0")
    if g is None or r is None:
        print("  UNRUNNABLE: an arm is absent. Exit 2, never 0."); return 2
    keys = sorted(set(g) & set(r))
    if len(keys) < 8:
        print("  UNRUNNABLE: too few shared interactions. Exit 2."); return 2

    print("R427 · arm_agreement — do generic and randblind make the SAME PICKS, or just the same score?\n")
    print("  ⭐ TWO ARMS LANDING AT THE SAME ACCURACY IS WEAK EVIDENCE THAT THEIR CRITERIA DO NOT")
    print("     MATTER: two genuinely different rankers can be equally wrong in DIFFERENT places and")
    print("     produce identical means. Per-interaction agreement is the sharp version.")
    print("  ⚠ NOTHING HERE READS `if_chosen`. An agreement effect must not be readable as accuracy.\n")

    rng = np.random.default_rng(0)
    S = collections.defaultdict(lambda: collections.defaultdict(lambda: ([], [], [], [])))
    bystrat = collections.defaultdict(list)
    for k in keys:
        t = tg[k]
        n = len(t["resp"])
        ids = [x["id"] for x in t["resp"]]
        a, b, c, e = S[n][k[0]]
        a.append(float(g[k] == r[k]))                       # observed agreement
        b.append(float(g[k] == g[k]))                       # SELF control
        c.append(float(g[k] == ids[int(rng.integers(n))]))  # RANDOM control
        e.append(1.0 / n)                                   # its expectation, SAME weighting
        bystrat[n].append(k)

    selfc = clus({kk: v[1] for n in S for kk, v in S[n].items()})
    randc = clus({kk: v[2] for n in S for kk, v in S[n].items()})
    # ⛔ SECOND TIME IN TWENTY MINUTES, AND THE SAME DEFECT VERBATIM. In R427/position.py the
    #    observed rate was conversation-clustered while the expectation was a flat mean of 1/n over
    #    interactions -- two weightings compared as one object. I wrote it again here. Both sides are
    #    now clustered identically. ⚠ A THIRD OCCURRENCE MUST BECOME A SHARED HELPER rather than a
    #    third patch: the campaign's own rule is that the same bug three times is an infrastructure
    #    problem, and this estimator shape recurs in every arm comparison in this round.
    erc = clus({kk: v[3] for n in S for kk, v in S[n].items()})
    exp_rand = erc[0]
    self_ok = selfc is not None and abs(selfc[0] - 1.0) < 1e-12
    rand_ok = randc is not None and abs(randc[0] - exp_rand) <= max(randc[1], 1e-9)
    print("  CONTROLS")
    print(f"    SELF (+)    generic against ITSELF agrees at {selfc[0]:.4f}   "
          f"{'PASS' if self_ok else 'FAIL'}")
    print(f"    RANDOM (-)  generic against a seeded uniform picker: {randc[0]:.4f} vs the")
    print(f"                derivation {exp_rand:.4f} (MDE {randc[1]:.4f})   "
          f"{'PASS' if rand_ok else 'FAIL'}")
    if not (self_ok and rand_ok):
        print("\n  UNVERIFIED — the agreement estimator is unfit. Exit 1."); return 1

    print(f"\n    {'n_resp':<8} {'agreement':>10} {'MDE':>8} {'shuffled null':>14} {'MDE':>8} "
          f"{'excess':>9} {'1/n':>7} {'convs':>7}")
    rows, hits, rows_bad = {}, [], []
    for n in sorted(S):
        obs = clus({kk: v[0] for kk, v in S[n].items()})
        # ⛔ MY FIRST NULL WAS A CHECK THAT COULD NOT FAIL, AND IT PRINTED 0.0000 WITH MDE 0.0000
        #    IN EVERY STRATUM BEFORE I NOTICED. It compared generic's chosen ID against randblind's
        #    chosen ID FROM A DIFFERENT INTERACTION -- and response ids are `utterance_id`, unique
        #    per interaction, so the two can NEVER be equal. The null was zero BY CONSTRUCTION, the
        #    excess was the raw agreement wearing a null's clothes, and the verdict read +0.7183.
        #    The tell was printed on the same line: a null with zero variance is not a null.
        #    ⚠ THE FIX IS TO PERMUTE POSITIONS, NOT IDS. Within a stratum every interaction has the
        #    same number of responses, so randblind's pick as a POSITION INDEX transfers meaningfully
        #    and preserves its marginal distribution over positions.
        ks = bystrat[n]
        pos_of = {}
        for k in ks:
            ids_k = [x["id"] for x in tg[k]["resp"]]
            pos_of[k] = (ids_k.index(g[k]), ids_k.index(r[k]))
        perm = list(rng.permutation(len(ks)))
        nullby = collections.defaultdict(list)
        for idx, k in enumerate(ks):
            nullby[k[0]].append(float(pos_of[k][0] == pos_of[ks[perm[idx]]][1]))
        nul = clus(nullby)
        if nul is not None and nul[1] == 0.0:
            print(f"    {n:<8} NULL HAS ZERO VARIANCE — a null that cannot vary is not a null. "
                  f"UNVERIFIED for this stratum."); rows_bad.append(n); continue
        if obs is None or nul is None:
            print(f"    {n:<8} {'—':>10} {'—':>8} {'—':>14} {'—':>8} {'—':>9} {1/n:>7.4f} "
                  f"{len(S[n]):>7}   UNVERIFIED")
            continue
        ex = obs[0] - nul[0]
        mde = float(np.hypot(obs[1], nul[1]))
        rows[n] = dict(agree=obs[0], agree_mde=obs[1], null=nul[0], null_mde=nul[1],
                       excess=ex, excess_mde=mde, chance=1/n, convs=obs[2])
        if ex > mde:
            hits.append(n)
        print(f"    {n:<8} {obs[0]:>10.4f} {obs[1]:>8.4f} {nul[0]:>14.4f} {nul[1]:>8.4f} "
              f"{ex:>+9.4f} {1/n:>7.4f} {obs[2]:>7,}" + ("   ⭐" if ex > mde else ""))

    pooled = clus({kk: v[0] for n in S for kk, v in S[n].items()})
    print(f"\n    pooled agreement {pooled[0]:.4f} (MDE {pooled[1]:.4f}) · "
          f"strata where excess > MDE: {hits or 'none'} of {len(rows)}")

    print()
    if rows_bad:
        print(f"  UNVERIFIED — strata {rows_bad} have a degenerate null. Exit 1.")
        return 1
    if hits:
        v = "W_SAME_ORDERING"
        print(f"  W-SAME-ORDERING — the two arms pick the SAME response far more often than their")
        print(f"  marginals allow, in strata {hits}. The judge's ranking is largely independent of")
        print(f"  WHICH criteria it is handed.")
        print(f"  ⛔ SO `generic − randblind ≈ 0` IS NOT TWO MEANS COINCIDING. The criteria are close")
        print(f"     to inert as an INPUT: hand the same judge four quality sentences or four")
        print(f"     sentences written for other prompts, and it ranks these responses much the same.")
    else:
        v = "W_DIFFERENT_RULES"
        print(f"  W-DIFFERENT-RULES — agreement sits within MDE of the shuffled null in every")
        print(f"  stratum. The two arms RANK differently and merely SCORE alike — equally wrong in")
        print(f"  different places — so the criteria do change the ordering even though they do not")
        print(f"  change the accuracy. `generic − randblind ≈ 0` is a coincidence of two means.")

    print(f"\n  ⚠ BOTH ARMS ARE PROMPT-BLIND BY CONSTRUCTION, so nothing here speaks to a")
    print(f"    prompt-specific core. And WHY the judge ranks as it does needs mechanistic access")
    print(f"    this design does not have.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               strata={str(k): v2 for k, v2 in rows.items()}, pooled_agreement=pooled[0],
               pooled_mde=pooled[1], excess_strata=hits,
               controls=dict(self_agree=selfc[0], rand=randc[0], rand_expected=exp_rand),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r427_arm_agreement.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
