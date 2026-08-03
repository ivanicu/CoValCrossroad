"""R286 — is clause 2 a property of CORES, or of whoever wrote the generic criteria?

THE ATTACK, AND IT IS AIMED AT THE CLAUSE I INSTALLED ONE ROUND AGO. The revised clause 2 reads
*better than the same NUMBER of criteria that never read the conversation.* R281 then found the
neutral arm is not one object: four hand-picked sentences score 0.5514 while four drawn at random
from a 16-criterion pool average 0.5403 ± 0.0070, and `gen`'s verdict FLIPS between them.

If the clause's threshold moves with the quality of the generic vocabulary, then the clause does not
measure a property of cores at all — it measures *how good my baseline happens to be*, and anyone
with better generic criteria would fail arms this definition admits. **That is the meta-separator
for the clause: not "which arms pass" but "is the question well posed".**

The cheapest decisive instrument: all **C(16,4) = 1820** four-subsets of the pool are enumerable
exactly, pool-internal (so no cross-artifact noise), and free — the satisfaction values are already
on disk.

⚠ AND THE ARGMAX OVER 1820 IS THE TRAP, NOT THE ANSWER. The best subset chosen on the same prompts
it is scored on is a selection artifact; quoting it would be the "conditioning on the outcome" row.
Every headline number here is HELD OUT: choose the subset on half the prompts, score it on the other
half, over 10 random splits, and report the shrinkage between the two as its own quantity.

ESTIMAND        (a) the full distribution of A2 over all 1820 prompt-blind k=4 subsets;
                (b) the HELD-OUT A2 of the best subset chosen on disjoint prompts, 10 splits;
                (c) the gap between (b) and `coval_core` / `topw_k4`, with a paired bootstrap;
                (d) the in-sample vs held-out shrinkage, as the size of the selection artifact.
IDENTIFICATION  (a) exact — a complete enumeration, not a sample. (b) is identified by the split;
                (c) is a paired difference; (d) is a difference of (a)'s max and (b).
SCOPE           population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base,
                ONE judging run (the pool), so no cross-artifact term · baseline the arms as
                published in R280 · regime k=4 exactly, unweighted, ALL annotators.
WORLDS          W-INTRINSIC  even the best held-out generic quadruple stays separably BELOW
                             `coval_core` -> clause 2 survives its own meta-separator: no
                             prompt-blind vocabulary of that size reaches the admitted arms, so
                             the clause is about cores.
                W-BASELINE   the best held-out generic quadruple reaches or passes `coval_core`
                             -> the clause's threshold is a property of the baseline's quality.
                             It must then be restated with its baseline NAMED, and "better than
                             prompt-blind criteria" becomes meaningless without saying WHICH.
KILL            pre-registered: if the held-out best subset's A2 is not separably below
                `coval_core` (paired bootstrap CI on the difference must exclude 0 with
                coval_core ahead), W-BASELINE holds and FORMULATION.md must name the baseline
                inside the clause, permanently.
POSITIVE CTRL   the incumbent quadruple {0,1,2,3} must appear in the enumeration at exactly its
                pool-internal value (0.5504, R281). It can fail on any subset-indexing error, which
                would silently shift the whole distribution.
NEGATIVE CTRL   the in-sample argmax must EXCEED the held-out value. If it does not, the selection
                step is doing nothing and the split is not testing what it claims to.
PLACEBO         a subset against itself: exactly 0.
NOISE FLOOR     the across-split spread of the held-out value, reported as sd over 10 splits.
MULTIPLICITY    the enumeration is a distribution, not a test family; the only tests are the 2
                arm comparisons, BH over both.
SPECIFICATION   swept: 10 splits x {best, 2nd best, 90th percentile} selection rules, so the
                headline does not rest on the single most extreme choice.
SEEDS           10 split seeds, all reported.
ARTIFACT        results/baseline_ceiling.json with source hash.
IMPOSSIBLE      whether a LARGER or better-written generic pool exists that would pass — the pool
                is 16 criteria I wrote, and this round bounds only what THIS vocabulary reaches.
                A negative result here is a bound, not a proof of impossibility.
"""
import json, sys, math, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
K = 4
NSPLIT = 10
NBOOT = 2000
ZEFF = 1.959964 + 0.841621
L = "ABCD"


def main():
    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
    pids = sorted(p for p in S if p in tg and len(tg[p]) >= 2)
    npool = len({i for i, _ in S[pids[0]]})
    N = len(pids)

    # per-prompt satisfaction matrix (npool x 4) and human class matrix (m x 6)
    SAT = np.stack([np.array([[S[p][(i, x)] for x in L] for i in range(npool)], float) for p in pids])
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    subs = np.array(list(itertools.combinations(range(npool), K)))
    print(f"  {N} prompts · pool {npool} · all C({npool},{K}) = {len(subs)} subsets enumerated exactly\n")

    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])

    def scores():
        """A2 of every subset on every prompt -> (nsub, N)."""
        out = np.empty((len(subs), N))
        for n in range(N):
            Y = SAT[n][subs].sum(axis=1)                     # (nsub, 4)
            C = np.sign(Y[:, ii] - Y[:, jj])                 # (nsub, 6)
            out[:, n] = (C[:, None, :] == H[n][None, :, :]).mean(axis=(1, 2))
        return out
    A = scores()
    per_sub = A.mean(axis=1)

    # ---- positive control -----------------------------------------------------------------
    inc = int(np.where((subs == np.array([0, 1, 2, 3])).all(axis=1))[0][0])
    pos_ok = abs(per_sub[inc] - 0.5504) < 5e-4
    print(f"  POSITIVE CONTROL  the incumbent quadruple {{0,1,2,3}} is subset #{inc}, "
          f"A2 = {per_sub[inc]:.4f}  (R281 pool-internal 0.5504)  {'PASS' if pos_ok else 'FAIL'}")
    if not pos_ok:
        print("\n  UNVERIFIED — subset indexing is wrong; the whole distribution is shifted.")
        return 1

    q = np.percentile(per_sub, [0, 25, 50, 75, 90, 99, 100])
    print(f"\n  THE FULL DISTRIBUTION OF PROMPT-BLIND QUADRUPLES  ({len(subs)} subsets)\n")
    print(f"    min {q[0]:.4f}  p25 {q[1]:.4f}  median {q[2]:.4f}  p75 {q[3]:.4f}  "
          f"p90 {q[4]:.4f}  p99 {q[5]:.4f}  MAX {q[6]:.4f}")
    print(f"    the incumbent sits at the {100*(per_sub < per_sub[inc]).mean():.1f}th percentile")

    # ---- held-out selection ---------------------------------------------------------------
    ARMS = {}
    for a in ("coval_core", "topw_k4"):
        Sa = load_sat(ROOT / "corebench" / "results" / f"sat_{a}.npz")
        ARMS[a] = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                      for c in range(6)] for h in H[n]])
                            for n, p in enumerate(pids)])

    rows = {"best": [], "second": [], "p90": []}
    held_vec = {k: [] for k in rows}
    for s in range(NSPLIT):
        rng = np.random.default_rng(2600 + s)
        perm = rng.permutation(N)
        fit, ev = perm[:N // 2], perm[N // 2:]
        order = np.argsort(-A[:, fit].mean(axis=1))
        pick = {"best": order[0], "second": order[1],
                "p90": order[int(0.10 * len(order))]}
        for k_, idx in pick.items():
            rows[k_].append((float(A[idx, fit].mean()), float(A[idx, ev].mean())))
            held_vec[k_].append((idx, ev))

    print(f"\n  HELD-OUT SELECTION — subset chosen on half the prompts, scored on the other half"
          f"  ({NSPLIT} splits)\n")
    print(f"    {'rule':<9}{'in-sample':>11}{'held-out':>11}{'shrinkage':>11}{'sd(held)':>10}")
    for k_, v in rows.items():
        ins = np.array([x[0] for x in v]); hel = np.array([x[1] for x in v])
        print(f"    {k_:<9}{ins.mean():>11.4f}{hel.mean():>11.4f}"
              f"{ins.mean()-hel.mean():>+11.4f}{hel.std():>10.4f}")
    ins_b = np.array([x[0] for x in rows["best"]]); hel_b = np.array([x[1] for x in rows["best"]])
    neg_ok = ins_b.mean() > hel_b.mean()
    print(f"\n    NEGATIVE CTRL: in-sample argmax exceeds held-out ?  "
          f"{'PASS — the selection step does something' if neg_ok else 'FAIL — selection is inert, the split tests nothing'}")

    # ---- the comparison, paired on the EVALUATION prompts only ----------------------------
    print(f"\n  THE BEST HELD-OUT PROMPT-BLIND QUADRUPLE vs THE ADMITTED ARMS\n")
    print(f"    {'arm':<13}{'arm A2':>9}{'best-blind':>12}{'gap':>9}  {'95% CI':<22}verdict")
    out, grid = {}, []
    for a, av in ARMS.items():
        # ⚠ THE FIRST VERSION CONCATENATED THE 10 EVAL HALVES AND BOOTSTRAPPED THE ROWS.
        # That is 4,840 rows which are 968 PROMPTS appearing ~5 times each -- n_eff is the CLUSTER
        # count, not the row count, and the CI came out ~2.2x too narrow (P14: n_eff is clusters).
        # Corrected: average each prompt's difference over the splits where it was HELD OUT, then
        # bootstrap the 968 prompt-level values. The verdict is unchanged; the interval was not.
        acc = np.zeros(N); cnt = np.zeros(N)
        for idx, ev in held_vec["best"]:
            acc[ev] += av[ev] - A[idx, ev]; cnt[ev] += 1
        keep = cnt > 0
        d = acc[keep] / cnt[keep]
        rb = np.random.default_rng(555)
        bs = np.array([d[rb.integers(0, len(d), len(d))].mean() for _ in range(NBOOT)])
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        p2 = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
        mde_cell = ZEFF * d.std(ddof=1) / math.sqrt(len(d))
        # R292: the verdict is now COMPUTED against this cell's own MDE, not off the CI alone.
        # The old line said `arm ahead, separably` whenever lo > 0, and topw_k4's +0.0096 against
        # an MDE of 0.0104 was published that way. CI-excludes-zero and |eff| >= MDE are different
        # questions and this arc answers the second one.
        from report import verdict as _v
        v = {"BEATS": "arm ahead, separably", "LOSES": "blind ahead",
             "UNRESOLVED": "NOT SEPARABLE", "BELOW RESOLUTION": "BELOW RESOLUTION"}[
                 _v(float(d.mean()), lo, hi, mde_cell)]
        out[a] = dict(arm=float(av.mean()), blind=float(hel_b.mean()), gap=float(d.mean()),
                      lo=lo, hi=hi, p=float(p2), mde=float(mde_cell), verdict=v)
        grid.append((a, float(p2)))
        print(f"    {a:<13}{av.mean():>9.4f}{hel_b.mean():>12.4f}{d.mean():>+9.4f}  "
              f"[{lo:+.4f}, {hi:+.4f}]{'':<3}{v}   n_eff={len(d)}")
    grid.sort(key=lambda t: t[1]); C_ = len(grid)
    surv = {a for i, (a, p) in enumerate(grid, 1) if p <= 0.05 * i / C_}
    print(f"\n    BH over {C_} cells · survivors {sorted(surv)}")

    # ⚠ R292: the KILL read `lo > 0` -- the CI criterion -- while the table two lines above now
    # reads |eff| >= MDE. A kill on a different rule than its own table is the verdict-string
    # failure moved into the branch, which is worse: the table is read by a person and the branch
    # is not. Both now use the same computed verdict.
    ahead = [a for a in out if out[a]["verdict"] == "arm ahead, separably"]
    killed = len(ahead) < len(out)
    print("\n  " + "=" * 74)
    print(f"  PRE-REGISTERED KILL: is the best held-out blind quadruple NOT separably below "
          f"both arms ?  {killed}")
    if killed:
        print(f"  -> W-BASELINE, PARTIAL. {len(ahead)} of {len(out)} admitted arms stay separably")
        print(f"     ahead of the best held-out blind quadruple: {ahead}.")
        print(f"     Not ahead by this arc's resolution rule: {[a for a in out if a not in ahead]}")
        print("     For those, `no prompt-blind quadruple reaches the admitted arms` is NOT")
        print("     established -- the blind arm is not shown to be behind, only not shown ahead.")
    else:
        print("  -> W-INTRINSIC. No prompt-blind quadruple in this vocabulary reaches the admitted")
        print("     arms even when CHOSEN to, so the clause is about cores, not about my baseline —")
        print("     bounded to THIS 16-criterion pool, which is what the round can support.")
    print("  " + "=" * 74)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    o = pathlib.Path(__file__).parent / "results" / "baseline_ceiling.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(source_sha=src, n_prompts=N, n_subsets=len(subs),
                                 dist=dict(zip(["min", "p25", "med", "p75", "p90", "p99", "max"],
                                               q.tolist())),
                                 incumbent=float(per_sub[inc]),
                                 selection={k_: [list(x) for x in v] for k_, v in rows.items()},
                                 arms=out, killed=bool(killed)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
