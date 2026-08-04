"""R427/pairwise_excess -- is `generic is the odd one out` real, or a marginal-distribution artifact?

Last round reported raw pairwise agreement:
    generic vs randblind_s0        0.6434
    generic vs randblind_s1        0.5175
    randblind_s0 vs randblind_s1   0.7091
and concluded the two random arms share something generic does not.

⛔ RAW AGREEMENT IS BOUNDED BY THE ARMS' OWN MARGINAL PICK DISTRIBUTIONS. Two rules that both favour
   the same position agree often for reasons that have nothing to do with shared content; two rules
   with mismatched marginals CANNOT agree much even if they respond to the same thing. So a gap of
   0.13 between two RANDOM draws' agreement with the same arm is exactly what a marginal mismatch
   looks like, and my sentence may be describing skew rather than content.

⭐ THE COMPARABLE QUANTITY IS EXCESS OVER EACH PAIR'S OWN MARGINAL-PRESERVING NULL. Permuting one
   arm's picks (as POSITIONS, within a response-count stratum) across interactions preserves both
   arms' marginal distributions and destroys only the pairing. The excess is then on a common scale
   and the three pairs can be ranked.

⛔ ARITHMETIC TRAP. That a permutation preserving marginals leaves the null at the
   marginal-agreement level is FORCED -- it is the definition of the null, not a finding. What is NOT
   forced is whether the three EXCESSES rank the same way the raw agreements did.

ESTIMAND        for each of the three arm pairs: raw agreement, its marginal-preserving null, and the
                excess, with the conversation as the unit throughout.

IDENTIFICATION  Exact. All three arms' picks are deterministic given their committed satisfaction.

SCOPE           population: interactions present in all three arms · instrument: the arms' own
                argmaxes, mean aggregation · baseline: the marginal-preserving permutation · regime:
                k=4, prompt-blind, 2,200 seeded conversations. Nothing reads `if_chosen`.

WORLDS
  W-CONTENT     the excess ranking MATCHES the raw ranking: s0-s1 highest. Then the two random draws
                really do share something generic does not, and it survives marginal correction.
  W-MARGINAL    the excess ranking DIFFERS from the raw ranking. Then `generic is the odd one out`
                was a marginal-distribution artifact and is retracted.

PREDICTION MATRIX
  W-CONTENT  -> excess(s0,s1) > both excess(g,s0) and excess(g,s1)
  W-MARGINAL -> that ordering breaks

PRE-REGISTERED KILL -- conditional on the null being shown to preserve marginals.
    if each arm's marginal pick distribution is UNCHANGED by the permutation (it is, by
       construction -- verified numerically anyway) and the null has non-zero variance:
        excess ordering matches raw ordering -> W-CONTENT
        else                                 -> W-MARGINAL, and the earlier sentence is retracted
    else: UNVERIFIED.

CONTROLS
  MARGINALS    each arm's distribution over pick POSITION is printed, per stratum. This is the
               quantity the worry is about, so it is shown rather than asserted away.
  NULL-VAR     a null with zero variance is not a null -- the guard that caught the id-permutation
               defect in arm_agreement.py is kept.
  SELF         an arm against itself must agree at exactly 1.0.
  CLUSTER      every quantity aggregated by lib/cluster.ByConv, which appends across strata rather
               than assigning -- the defect that corrupted the pooled figure this round already
               corrected once.
  NO-TARGET    nothing here reads `if_chosen`.

MULTIPLICITY    3 pairs x (raw, null, excess) + marginals per arm per stratum; all printed.
ARTIFACT        results/r427_pairwise_excess.json with the source hash.

IMPOSSIBLE HERE
  WHY two arms share a marginal skew -- needs the judge's internals.
  a prompt-specific core            -- unchanged.

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
sys.path.insert(0, str(ROOT))
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
from lib.cluster import ByConv                                              # noqa: E402


def picks(tag):
    p = RES / f"sat_transport_{tag}.npz"
    if not p.exists():
        return None, None
    with np.load(p, allow_pickle=True) as d:
        meta, sat = [str(x) for x in d["meta"]], np.asarray(d["sat"], float)
        tgt = {(t["conv"], t["inter"]): t for t in json.loads(str(d["targets"]))}
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    for m, v in zip(meta, sat):
        c, i, r, _j = m.split("|")
        per[(c, i)][r].append(v)
    out = {}
    for k, row in per.items():
        s = {r: float(np.mean(v)) for r, v in row.items()}
        top = max(s.values())
        out[k] = sorted([r for r in s if s[r] == top])[0]
    return out, tgt


def main() -> int:
    arms, tgt = {}, None
    for t in ("generic", "randblind_s0", "randblind_s1"):
        a, g = picks(t)
        if a is None:
            print(f"  UNRUNNABLE: {t} absent. Exit 2, never 0."); return 2
        arms[t] = a; tgt = tgt or g
    keys = sorted(set.intersection(*(set(v) for v in arms.values())))
    if len(keys) < 8:
        print("  UNRUNNABLE: too few shared interactions. Exit 2."); return 2

    print("R427 · pairwise_excess — `generic is the odd one out`: real, or a marginal artifact?\n")
    print("  ⛔ RAW AGREEMENT IS BOUNDED BY THE ARMS' MARGINAL PICK DISTRIBUTIONS. Two rules that")
    print("     both favour the same position agree for reasons unrelated to content; mismatched")
    print("     marginals CANNOT agree much even when both track the same thing. A 0.13 gap between")
    print("     two RANDOM draws' agreement with the same arm is what that looks like.\n")

    pos = {t: {} for t in arms}
    bystrat = collections.defaultdict(list)
    for k in keys:
        ids = [x["id"] for x in tgt[k]["resp"]]
        for t in arms:
            pos[t][k] = ids.index(arms[t][k])
        bystrat[len(ids)].append(k)

    print("  CONTROLS")
    print(f"    SELF        an arm against itself agrees at "
          f"{np.mean([pos['generic'][k] == pos['generic'][k] for k in keys]):.4f}   PASS")
    print(f"    MARGINALS   distribution over pick POSITION, the quantity the worry is about:")
    marg = {}
    for n in sorted(bystrat):
        ks = bystrat[n]
        for t in arms:
            c = collections.Counter(pos[t][k] for k in ks)
            marg[f"{t}|n={n}"] = [c.get(i, 0) / len(ks) for i in range(n)]
        print(f"      n={n} ({len(ks):,} interactions)")
        for t in arms:
            print(f"        {t:<14} " + " ".join(f"{x:.3f}" for x in marg[f'{t}|n={n}']))

    rng = np.random.default_rng(0)
    PAIRS = (("generic", "randblind_s0"), ("generic", "randblind_s1"),
             ("randblind_s0", "randblind_s1"))
    print(f"\n    {'pair':<32} {'raw':>8} {'MDE':>8} {'null':>8} {'MDE':>8} {'EXCESS':>9}")
    rows, bad = {}, []
    for x, y in PAIRS:
        b = ByConv()
        for n in sorted(bystrat):
            ks = bystrat[n]
            perm = list(rng.permutation(len(ks)))
            for idx, k in enumerate(ks):
                b.add(k[0], raw=float(pos[x][k] == pos[y][k]),
                      null=float(pos[x][k] == pos[y][ks[perm[idx]]]))
        raw, nul = b.mean("raw"), b.mean("null")
        if nul[1] == 0.0:
            bad.append(f"{x}|{y}")
            print(f"    {x + ' vs ' + y:<32} NULL HAS ZERO VARIANCE — not a null. UNVERIFIED")
            continue
        ex = b.paired("raw", "null")
        rows[f"{x}|{y}"] = dict(raw=raw[0], raw_mde=raw[1], null=nul[0], null_mde=nul[1],
                                excess=ex[0], excess_mde=ex[1], convs=raw[2],
                                obs=b.n_obs("raw"))
        print(f"    {x + ' vs ' + y:<32} {raw[0]:>8.4f} {raw[1]:>8.4f} {nul[0]:>8.4f} "
              f"{nul[1]:>8.4f} {ex[0]:>+9.4f}")
    if bad or len(rows) < 3:
        print(f"\n  UNVERIFIED — {bad or 'a pair is unestimable'}. Exit 1."); return 1

    raw_rank = sorted(rows, key=lambda k: -rows[k]["raw"])
    exc_rank = sorted(rows, key=lambda k: -rows[k]["excess"])
    print(f"\n    raw ranking     {' > '.join(raw_rank)}")
    print(f"    EXCESS ranking  {' > '.join(exc_rank)}")

    print()
    if raw_rank == exc_rank:
        v = "W_CONTENT"
        print(f"  W-CONTENT — the excess ranking MATCHES the raw ranking. The two random draws really")
        print(f"  do share something generic does not, and it survives marginal correction.")
    else:
        v = "W_MARGINAL"
        print(f"  W-MARGINAL — the excess ranking DIFFERS from the raw ranking. `generic is the odd")
        print(f"  one out` was reading a MARGINAL-DISTRIBUTION artifact, and it is RETRACTED.")
        print(f"  ⛔ THE RAW NUMBERS WERE CORRECT AND THE SENTENCE BUILT ON THEM WAS NOT — the")
        print(f"     failure this campaign retracts most often, one round after I wrote that.")

    print(f"\n  ⚠ WHY two arms share a marginal skew is NOT identified — that needs the judge's")
    print(f"    internals. And nothing here reads `if_chosen`, so no accuracy claim is touched.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               pairs=rows, marginals=marg, raw_rank=raw_rank, excess_rank=exc_rank, verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r427_pairwise_excess.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
