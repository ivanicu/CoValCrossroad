"""R296 — is there an optimal k, or was `3 to 8 are indistinguishable` a statement about power?

WHY. The definition has refused to name a size since R276, and the wording it settled on is
*"more than one, and 3 to 8 are indistinguishable"* — a bound the design supported at the time.
Two things have changed since: clause ② is now evaluated against a **size-matched prompt-blind
reference at every k** (the 16-criterion pool, judged once), and the census scored the whole `topw`
family at k = 1,2,3,4,6,8,12. So the k-question is answerable in the definition's own currency
rather than in raw A2, and `indistinguishable` can be replaced by a measurement or confirmed as one.

ESTIMAND        (a) clause-② margin as a function of k for the `topw` family, each k against the
                blind pool AT THAT k; (b) every adjacent-k pairwise difference with its own MDE;
                (c) the admitted band's endpoints.
IDENTIFICATION  exact. All quantities are averages over the release's annotations; the k-matched
                reference removes the size confound that made the earlier bound necessary.
SCOPE           968 prompts with >=2 annotators · Qwen3.5-2B-Base · A2·annotator, all annotators ·
                cluster bootstrap over prompts · baseline the k-matched prompt-blind arm.
WORLDS          W-PEAK   some k is separably better than its neighbours -> the definition can name
                         a size, and `3 to 8 indistinguishable` was a power statement.
                W-PLATEAU no adjacent pair separates -> the earlier bound was right, and it was
                         right for a reason now measured rather than assumed.
KILL            pre-registered: if ANY adjacent-k pair separates at its own MDE, the definition's
                size wording changes from a bound to that comparison. If none does, the bound stays
                and this round is recorded as the measurement that licenses it — not as a null.
POSITIVE CTRL   k=1 vs k=4 must separate. If the largest span in the admitted band cannot be
                resolved, the design cannot see k at all and no adjacent null is readable.
NEGATIVE CTRL   `topw_k4` against ITSELF: exactly 0.
NOISE FLOOR     per-cell MDE, in-cell.
MULTIPLICITY    6 adjacent pairs + 7 margins; BH over all 13.
ARTIFACT        results/k_curve.json with source hash.
IMPOSSIBLE      whether an optimal k TRANSFERS — one release, and the census's k=12 failure is a
                fact about this rubric's tail, not about size in general.
"""
import json, sys, math, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402
from report import row, header, verdict, POS                 # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF, NBOOT = 1.959964 + 0.841621, 2000
KS = [1, 2, 3, 4, 6, 8, 12]


def main():
    tg, _ = load_targets(); RES = ROOT / "corebench" / "results"
    S = {k: load_sat(RES / f"sat_topw_k{k}.npz") for k in KS}
    POOL = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(set.intersection(*(set(v) for v in S.values())) & set(POOL) &
                  {p for p in tg if len(tg[p]) >= 2})
    HC = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    N = len(pids)
    print(f"  {N} prompts · topw at k = {KS} · blind reference size-matched at each k\n")

    def vec(sat, idx=None):
        return np.array([np.mean([[cls(yvec(sat[p], idx if idx is not None
                                            else sorted({i for i, _ in sat[p]})))[q] == h[q]
                                   for q in range(6)] for h in HC[p]]) for p in pids])
    A = {k: vec(S[k]) for k in KS}
    B = {k: vec(POOL, list(range(k))) for k in KS}
    M = {k: A[k] - B[k] for k in KS}                       # clause-② margin at each k
    IDX = np.random.default_rng(31337).integers(0, N, (NBOOT, N))

    def cell(d):
        bs = d[IDX].mean(axis=1)
        return (float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)),
                float(2 * min((bs <= 0).mean(), (bs >= 0).mean())),
                ZEFF * d.std(ddof=1) / math.sqrt(N))

    print("  CLAUSE-② MARGIN AT EACH k\n  " + header("topw at k", width=14))
    grid, marg = [], {}
    for k in KS:
        c = cell(M[k]); marg[k] = c
        grid.append((f"k{k}", c[3]))
        print("  " + row(f"k={k}", *c[:3], c[4], width=14,
                         extra=f"  A2 {A[k].mean():.4f} vs blind {B[k].mean():.4f}"))

    print("\n  ADJACENT-k DIFFERENCES IN THE MARGIN\n  " + header("pair", width=14))
    adj = {}
    for a, b in zip(KS, KS[1:]):
        c = cell(M[b] - M[a]); adj[f"{a}->{b}"] = c
        grid.append((f"{a}->{b}", c[3]))
        print("  " + row(f"k={a} → k={b}", *c[:3], c[4], width=14))

    pc = cell(M[4] - M[1]); pos_ok = verdict(*pc[:3], pc[4]) == POS
    nc = cell(M[4] - M[4])
    print(f"\n  POSITIVE CTRL  k=1 → k=4 (the widest span in the admitted band): "
          f"{pc[0]:+.4f} [{pc[1]:+.4f},{pc[2]:+.4f}] vs MDE {pc[4]:.4f}  "
          f"{'PASS' if pos_ok else 'FAIL — the design cannot see k at all'}")
    print(f"  NEGATIVE CTRL  k=4 against itself: {nc[0]:.2e}  "
          f"{'PASS' if nc[0] == 0 else 'FAIL'}")
    grid.sort(key=lambda z: z[1]); C = len(grid)
    surv = sum(1 for i, (_, p) in enumerate(grid, 1) if p <= 0.05 * i / C)
    print(f"  BH q=0.05 over {C} cells · {surv} survive")
    if not (pos_ok and nc[0] == 0):
        print("\n  UNVERIFIED — controls did not behave.")
        return 1

    sep = [k for k, c in adj.items() if verdict(*c[:3], c[4]) in ("BEATS", "LOSES")]
    admitted = [k for k in KS if verdict(*marg[k][:3], marg[k][4]) == POS]
    print("\n  " + "=" * 74)
    print(f"  PRE-REGISTERED KILL: does ANY adjacent-k pair separate ?  {bool(sep)}   {sep}")
    print(f"    admitted at: k = {admitted}")
    if sep:
        print("  -> W-PEAK. The definition can name a size; `3 to 8 indistinguishable` was a")
        print("     statement about power, not about cores.")
    else:
        print("  -> W-PLATEAU. No adjacent k separates. The bound the definition already carries")
        print("     is correct, and it is now LICENSED BY A MEASUREMENT rather than by the absence")
        print("     of one — which is the difference between a bound and a shrug.")
    print("  " + "=" * 74)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    o = pathlib.Path(__file__).parent / "results" / "k_curve.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(source_sha=src, n_prompts=N, ks=KS,
                                 margin={str(k): marg[k] for k in KS}, adjacent=adj,
                                 admitted=admitted, separating=sep), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
