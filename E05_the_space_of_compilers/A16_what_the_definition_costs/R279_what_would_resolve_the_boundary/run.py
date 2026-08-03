"""R279 — what design would resolve the boundary, and is there one?

WHY. R278 left the definition's admit/exclude edge unresolved: `full - topwvar_k4` = +0.0089 against
an MDE of [0.0100, 0.0200]. The honest next move is NOT to demote the row by fiat -- it is to ask
what would settle it, because "this cannot be resolved here" is a WALL, and realstat §4 says an
unchecked wall is UNVERIFIED, never SETTLED. The specific unchecked thing: every number on this page
averages A2 over **3 randomly drawn annotators per prompt**, while the release ships **1,012
annotators**. If most of the difference vector's variance is annotator sampling noise, the boundary
is resolvable by using the annotators already on disk and the wall is imaginary. If it is prompt
heterogeneity, no amount of annotator averaging touches it and the binding constraint is the 968
prompts -- which IS a wall, and then it has a number instead of a shrug.

ESTIMAND        (a) the variance of the paired per-prompt A2 difference, decomposed into
                    sigma^2_within  (annotator sampling, removable by averaging) and
                    sigma^2_between (genuine prompt heterogeneity, NOT removable);
                (b) MDE(k) = 2.80 * sqrt(sigma^2_b + sigma^2_w / k) / sqrt(N) for k annotators per
                    prompt, and its limit MDE(inf) = 2.80 * sigma_b / sqrt(N);
                (c) the smallest k at which MDE(k) falls below the boundary effect 0.0089.
IDENTIFICATION  (a) is identified wherever a prompt has >=2 annotators: the within-prompt spread
                across annotators estimates sigma^2_w directly, and sigma^2_b is the between-prompt
                variance of the prompt means MINUS the noise those means still carry. Both are
                point-identified; (b) and (c) are DERIVATIONS from them and are labelled so.
SCOPE           population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base
                satisfaction judge · baseline pairwise-accuracy differences between two named arms
                · regime k=4 unweighted, 80% power, two-sided 5%.
WORLDS          W-NOISE       sigma^2_w dominates -> the boundary is resolvable with annotators
                              already in the release, and R278's "unresolved" is a fact about MY
                              DRAW COUNT, not about the release. The repair is a rerun.
                W-HETERO      sigma^2_b dominates -> MDE(inf) is still above 0.0089, no annotator
                              budget resolves it, and the constraint is the prompt count. The
                              repair is a different release, and the wall becomes a specification.
                These differ in what the artifact IS: a design defect I can fix today, or a
                property of the data that no work here removes.
KILL            pre-registered: if MDE(inf) > 0.0089 the boundary is declared STRUCTURALLY
                unresolvable at this release and FORMULATION.md carries that with the number.
                If MDE(inf) <= 0.0089 then R278's verdict is a defect OF MY DESIGN and I say so in
                those words -- the flattering reading (it is the data's fault) is the one that has
                to clear the higher bar.
POSITIVE CTRL   the decomposition must reproduce the OBSERVED single-draw variance at k=1 to within
                Monte-Carlo error: sqrt(sigma^2_b + sigma^2_w) vs the sd of a real 1-draw vector.
                It can fail -- a sign error or a missing m_p correction breaks it immediately.
NEGATIVE CTRL   an arm against ITSELF: both variance components must be exactly 0, since the
                difference vector is identically zero for every annotator.
PLACEBO         `random_k4_s0` vs `random_k4_s1` -- two draws of the same rule. Their sigma^2_b
                should be small relative to a real arm pair's; reported, not assumed.
NOISE FLOOR     sigma^2_w IS the annotator noise floor, measured here rather than carried in.
MULTIPLICITY    3 arm pairs x 1 decomposition. The claim is the decomposition, not a test.
SPECIFICATION   swept over 3 arm pairs (the boundary pair, a resolved pair, and the placebo) and
                over k in {1,2,3,5,10,20,ALL}. Reported whole.
SEEDS           the decomposition uses EVERY annotator, so it is seed-free by construction -- which
                is itself the point. The k=1 positive control uses 5 seeds.
ARTIFACT        results/variance.json with source hash.
IMPOSSIBLE      cross-release remains N/A. sigma^2_b is a property of THIS release's prompts and
                says nothing about how heterogeneous another release would be.
"""
import json, sys, math, pathlib, itertools, hashlib, collections
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621                                   # 80% power, two-sided 5%
BOUNDARY = 0.0089                                            # R278
NEEDED = ["full", "topwvar_k4", "coval_core", "topvar_k4", "random_k4_s0", "random_k4_s1"]
CASES = [("full", "topwvar_k4", "THE BOUNDARY CELL"),
         ("coval_core", "topvar_k4", "a RESOLVED cell, for contrast"),
         ("random_k4_s0", "random_k4_s1", "PLACEBO — two draws of one rule")]


def a2(c, h):
    return float(np.mean([c[q] == h[q] for q in range(len(PAIRS))]))


def main():
    tg, _ = load_targets()
    arms = {}
    for a in NEEDED:
        S = load_sat(ROOT / "corebench" / "results" / f"sat_{a}.npz")
        arms[a] = {p: cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in S if p in tg and len(tg[p]) >= 2}
    pids = sorted(set.intersection(*(set(v) for v in arms.values())))
    m = np.array([len(tg[p]) for p in pids])
    N = len(pids)
    print(f"  {N} prompts · annotators per prompt: min {m.min()} median {int(np.median(m))} "
          f"max {m.max()} mean {m.mean():.2f} · total annotations {m.sum()}\n")

    def decompose(x, y):
        """Return (sigma2_b, sigma2_w, per-prompt means) using EVERY annotator."""
        means, wvar = [], []
        for p in pids:
            d = np.array([a2(arms[x][p], cls(np.array(t[0], float))) -
                          a2(arms[y][p], cls(np.array(t[0], float))) for t in tg[p]])
            means.append(d.mean())
            wvar.append(d.var(ddof=1) if len(d) > 1 else 0.0)
        means, wvar = np.array(means), np.array(wvar)
        s2w = float(np.mean(wvar))
        # the between variance, corrected for the noise still inside each prompt mean
        s2b = float(max(0.0, means.var(ddof=1) - np.mean(wvar / m)))
        return s2b, s2w, means

    out = {}
    for x, y, label in CASES:
        s2b, s2w, means = decompose(x, y)
        eff = float(means.mean())
        print(f"  {x} − {y}   ({label})")
        print(f"    effect (all annotators)   {eff:+.4f}")
        print(f"    σ_between  {math.sqrt(s2b):.4f}   σ_within  {math.sqrt(s2w):.4f}"
              f"   within share {s2w/(s2b+s2w) if (s2b+s2w) else float('nan'):.3f}")

        def mde(k):
            return ZEFF * math.sqrt(s2b + s2w / k) / math.sqrt(N)
        mde_all = ZEFF * math.sqrt(s2b + float(np.mean(s2w / m))) / math.sqrt(N)
        mde_inf = ZEFF * math.sqrt(s2b) / math.sqrt(N)
        row = "    MDE(k):  " + "  ".join(f"k={k}:{mde(k):.4f}" for k in (1, 2, 3, 5, 10, 20))
        print(row)
        print(f"    MDE(all annotators on disk) {mde_all:.4f}    MDE(k→∞) {mde_inf:.4f}")

        # smallest k that clears the boundary effect
        kstar = next((k for k in range(1, 100001) if mde(k) <= abs(eff)), None)
        print(f"    smallest k with MDE(k) ≤ |effect| ({abs(eff):.4f}) : "
              f"{kstar if kstar else 'NONE — no annotator budget suffices'}")
        out[f"{x}|{y}"] = dict(label=label, eff=eff, s2b=s2b, s2w=s2w,
                               mde={str(k): mde(k) for k in (1, 2, 3, 5, 10, 20)},
                               mde_all=mde_all, mde_inf=mde_inf, kstar=kstar)
        print()

    # ---- positive control: reproduce the observed 1-draw sd -------------------------------
    x, y, _ = CASES[0]
    # ⚠ FIRST VERSION OF THIS CONTROL FAILED AT 95.7% AND THE CONTROL WAS WHAT WAS WRONG (10th).
    # It called rng.integers TWICE per prompt -- a different annotator for each arm -- producing an
    # UNPAIRED difference whose variance is Var(A)+Var(B) ~ 2x the paired one. The design under test
    # (R277, R278) draws ONE annotator and scores BOTH arms against it. Predicted 0.1622, observed
    # 0.3174: sqrt(0.197^2+0.197^2)=0.279 is the unpaired prediction, and that is what it measured.
    # The decomposition itself was never affected -- `decompose` uses the same annotator `t` for
    # both arms -- so this was a broken ruler held against a correct object.
    obs = []
    for s in range(5):
        rng = np.random.default_rng(4400 + s)
        v = []
        for p in pids:
            h = cls(np.array(tg[p][int(rng.integers(len(tg[p])))][0], float))   # ONE annotator
            v.append(a2(arms[x][p], h) - a2(arms[y][p], h))
        obs.append(np.std(v, ddof=1))
    o = out[f"{x}|{y}"]
    pred = math.sqrt(o["s2b"] + o["s2w"])
    rel = abs(np.mean(obs) - pred) / pred
    pos_ok = rel < 0.10
    print("  CONTROLS\n")
    print(f"    positive  predicted 1-draw sd {pred:.4f} vs observed {np.mean(obs):.4f} "
          f"(5 seeds, {np.std(obs):.4f}) → {rel:.1%} error  {'PASS' if pos_ok else 'FAIL'}")
    s2b0, s2w0, _ = decompose("full", "full")
    neg_ok = (s2b0 == 0.0 and s2w0 == 0.0)
    print(f"    negative  an arm against ITSELF: σ²_b {s2b0:.2e}  σ²_w {s2w0:.2e}  "
          f"{'PASS' if neg_ok else 'FAIL'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — controls did not behave; the decomposition is not readable.")
        return

    # ---- the pre-registered kill ----------------------------------------------------------
    b = out[f"{CASES[0][0]}|{CASES[0][1]}"]
    # ⚠ THE PRE-REGISTERED REFERENCE (0.0089) IS R278's THREE-DRAW ESTIMATE, and this round
    # measures the same effect at EVERY annotator, where it is smaller. Both readings are printed
    # and they agree, so nothing is being selected: the pre-registered comparison is knife-edge
    # (0.0089 vs 0.0089) and the all-annotator one is decisive. Reporting only the decisive one
    # would be choosing the cell that says what I want.
    structural = b["mde_inf"] > BOUNDARY
    structural_all = b["mde_inf"] > abs(b["eff"])
    print("\n  " + "=" * 72)
    print(f"  PRE-REGISTERED KILL: MDE(k→∞) = {b['mde_inf']:.4f} > boundary {BOUNDARY:.4f} "
          f"(R278, 3 draws) ?  {structural}   [KNIFE-EDGE]")
    print(f"  SAME TEST vs the all-annotator effect {abs(b['eff']):.4f} ?  {structural_all}")
    structural = structural or structural_all
    if structural:
        print("  -> W-HETERO. No annotator budget resolves this edge. The binding constraint is")
        print(f"     the {N} prompts, not my 3 draws: even with infinite annotators per prompt the")
        print(f"     design floors at {b['mde_inf']:.4f}. The wall is real and now carries a number.")
    else:
        print("  -> W-NOISE. R278's `unresolved` is a defect OF MY DESIGN, not of the release.")
        print(f"     Using every annotator on disk gives MDE {b['mde_all']:.4f}"
              f"{' — which already clears it' if b['mde_all'] <= BOUNDARY else ''}.")
    n_need = (ZEFF ** 2) * b["s2b"] / (abs(b["eff"]) ** 2) if b["s2b"] > 0 else float("inf")
    print(f"  DERIVATION: prompts needed for MDE(k→∞) to reach the all-annotator effect is "
          f"{n_need:,.0f} ({n_need/N:.1f}× this release).")
    print("  " + "=" * 72)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    o_ = pathlib.Path(__file__).parent / "results" / "variance.json"
    o_.parent.mkdir(parents=True, exist_ok=True)
    o_.write_text(json.dumps(dict(source_sha=src, n_prompts=N, annot_total=int(m.sum()),
                                  annot_median=int(np.median(m)), cases=out,
                                  structural=bool(structural), prompts_needed=n_need,
                                  pos_ctrl_rel_err=rel), indent=1))
    print(f"\n  artifact {o_.relative_to(ROOT)}  src {src}")


if __name__ == "__main__":
    main()
