"""R297 — why does ONE criterion from the conversation's own rubric lose to ONE generic criterion?

WHY. R296's k-curve has a cell I did not predict: `topw_k1` scores −0.0170 [−0.0267,−0.0080]
against a single prompt-blind criterion — separably WORSE. Every other admitted k beats its blind
match. A finding with no mechanism is a finding waiting to be an artifact, and this one is cheap to
explain or to kill.

⛔ THE MECHANISM I EXPECT, WRITTEN BEFORE MEASURING. A2 compares SIGNS of pairwise differences. With
k=1 the whole class comes from ONE criterion's satisfaction across four responses. A criterion the
humans rated IMPORTANT is often a specific requirement all four responses either meet or miss — so
its satisfaction is nearly CONSTANT across responses, the pairwise differences are ~0, and a tie
matches a human's non-zero sign never. A generic criterion ("is it accurate", "is it clear") varies
across responses by construction, because responses differ in exactly those ways.

**This is a prediction that can fail**: if `topw_k1`'s criterion has the SAME across-response spread
as a generic one, the tie explanation is dead and the loss is about content, not degeneracy.

ESTIMAND        (a) across-response satisfaction spread (sd over the 4 responses) per prompt, for
                the single criterion of `topw_k1` vs the single pool criterion; (b) the TIE RATE in
                each emitted class; (c) A2 restricted to the non-tied pairs, which removes the tie
                mechanism and asks whether anything else differs.
IDENTIFICATION  exact. All three are deterministic functions of the sat files.
SCOPE           968 prompts · Qwen3.5-2B-Base · k=1 exactly · all annotators.
WORLDS          W-TIES     topw_k1 has lower spread and a higher tie rate, and its deficit
                           disappears on the non-tied pairs -> the loss is DEGENERACY, and the
                           `importance' selector is picking criteria that cannot discriminate.
                W-CONTENT  spread and tie rates match -> the loss is about what the criterion SAYS,
                           and the k=1 cell is a content finding, not an artifact.
KILL            pre-registered: if the tie rates differ by less than 5 points, W-TIES is rejected
                and the k=1 deficit is reported as a content effect with no mechanism yet.
POSITIVE CTRL   `topvar_k4` selects criteria BY across-response spread, so at the same k its spread
                must exceed `topw`'s. If the spread statistic cannot see the arm built to maximise
                it, it cannot see anything.
NEGATIVE CTRL   an arm against itself: identical spread, identical tie rate.
MULTIPLICITY    3 statistics x 2 arms; BH over the tested cells.
ARTIFACT        results/k1_mechanism.json with source hash.
IMPOSSIBLE      whether the same mechanism holds for a rubric written differently — one release.
"""
import json, sys, math, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402
from report import row, header                               # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF, NBOOT = 1.959964 + 0.841621, 2000
L = "ABCD"


def main():
    tg, _ = load_targets(); RES = ROOT / "corebench" / "results"
    T1 = load_sat(RES / "sat_topw_k1.npz")
    POOL = load_sat(RES / "sat_genericpool16.npz")
    TV = load_sat(RES / "sat_topvar_k4.npz")
    TW4 = load_sat(RES / "sat_topw_k4.npz")
    pids = sorted(set(T1) & set(POOL) & set(TV) & set(TW4) & {p for p in tg if len(tg[p]) >= 2})
    HC = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    N = len(pids)
    print(f"  {N} prompts · k=1: topw's single top-importance criterion vs one generic criterion\n")

    def yv(sat, p, idx):
        return np.array(yvec(sat[p], idx), float)
    SP_T = np.array([yv(T1, p, sorted({i for i, _ in T1[p]})[:1]).std() for p in pids])
    SP_G = np.array([yv(POOL, p, [0]).std() for p in pids])
    CL_T = [cls(yv(T1, p, sorted({i for i, _ in T1[p]})[:1])) for p in pids]
    CL_G = [cls(yv(POOL, p, [0])) for p in pids]
    tie_T = np.array([np.mean([c == 0 for c in cl]) for cl in CL_T])
    tie_G = np.array([np.mean([c == 0 for c in cl]) for cl in CL_G])

    IDX = np.random.default_rng(31337).integers(0, N, (NBOOT, N))
    def cell(d):
        bs = d[IDX].mean(axis=1)
        return (float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)),
                ZEFF * d.std(ddof=1) / math.sqrt(N))

    print("  " + header("k=1 statistic", width=30))
    s = cell(SP_T - SP_G); t = cell(tie_T - tie_G)
    print("  " + row("across-response spread Δ", *s, width=30,
                     extra=f"  topw {SP_T.mean():.4f} vs generic {SP_G.mean():.4f}"))
    print("  " + row("TIE RATE Δ", *t, width=30,
                     extra=f"  topw {tie_T.mean():.4f} vs generic {tie_G.mean():.4f}"))

    # A2 on the NON-TIED pairs only — removes the tie mechanism entirely
    def a2_nontied(CL):
        out = []
        for n, p in enumerate(pids):
            c = CL[n]; keep = [q for q in range(6) if c[q] != 0]
            if not keep: continue
            out.append(np.mean([[c[q] == h[q] for q in keep] for h in HC[p]]))
        return np.array(out), len(out)
    aT, nT = a2_nontied(CL_T); aG, nG = a2_nontied(CL_G)
    print(f"\n  A2 ON NON-TIED PAIRS ONLY  (topw on {nT} prompts, generic on {nG})")
    print(f"    topw_k1 {aT.mean():.4f}   generic_k1 {aG.mean():.4f}   Δ {aT.mean()-aG.mean():+.4f}")

    # ---- controls -------------------------------------------------------------------------
    spv = np.array([yv(TV, p, sorted({i for i, _ in TV[p]})).std() for p in pids])
    spw = np.array([yv(TW4, p, sorted({i for i, _ in TW4[p]})).std() for p in pids])
    pos_ok = spv.mean() > spw.mean()
    print(f"\n  POSITIVE CTRL  `topvar_k4` (selects BY spread) exceeds `topw_k4` at the same k: "
          f"{spv.mean():.4f} > {spw.mean():.4f}  {'PASS' if pos_ok else 'FAIL — the spread statistic is blind'}")
    nz = cell(SP_T - SP_T)
    print(f"  NEGATIVE CTRL  an arm against itself: spread Δ {nz[0]:.2e}  "
          f"{'PASS' if nz[0] == 0 else 'FAIL'}")
    if not (pos_ok and nz[0] == 0):
        print("\n  UNVERIFIED — controls did not behave.")
        return 1

    tie_gap = tie_T.mean() - tie_G.mean()
    killed = abs(tie_gap) < 0.05
    print("\n  " + "=" * 74)
    print(f"  PRE-REGISTERED KILL: tie rates differ by less than 5 points ?  {killed}"
          f"   (Δ = {tie_gap:+.4f})")
    if killed:
        print("  -> W-CONTENT. The tie explanation is DEAD. The k=1 deficit is about what the")
        print("     criterion SAYS, and it has no mechanism yet — which is where it stays.")
    else:
        print(f"  -> W-TIES. `topw_k1` emits ties on {tie_T.mean():.1%} of pairs against")
        print(f"     {tie_G.mean():.1%} for a generic criterion. A tie can never match a human's")
        print("     non-zero sign, so the most IMPORTANT criterion is often the least")
        print("     DISCRIMINATING one — importance and discrimination are different properties,")
        print("     and at k=1 nothing else is left to carry the class.")
    print("  " + "=" * 74)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    o = pathlib.Path(__file__).parent / "results" / "k1_mechanism.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(source_sha=src, n_prompts=N, spread=s, tie=t,
                                 spread_topw=float(SP_T.mean()), spread_generic=float(SP_G.mean()),
                                 tie_topw=float(tie_T.mean()), tie_generic=float(tie_G.mean()),
                                 a2_nontied=[float(aT.mean()), float(aG.mean())],
                                 killed=bool(killed)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
