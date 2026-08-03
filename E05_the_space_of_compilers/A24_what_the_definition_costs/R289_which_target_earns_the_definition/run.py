"""R289 — the definition names A2·annotator. Can that choice be ARGUED rather than inherited?

WHY. R288 forced the definition to name its statistic, and it named the one the campaign happened to
start with. `A2·consensus` agrees with it at Kendall τ = 0.944 over nine arms, admits the SAME two
arms, and has a higher ceiling (0.6352 vs 0.5519). **Nothing in this file says why one rather than
the other**, and "it is what I have been computing since round 220" is not an argument.

THE DISCRIMINATOR THAT DOES NOT REQUIRE DECIDING WHAT A CORE IS FOR. When two estimators agree on
the ORDERING, the one that RESOLVES MORE OF IT at the same n is strictly the better instrument for
that ordering. That is answerable here and does not smuggle in a claim about purpose.

⚠ AND THE TRAP IS THE SCALE. `A2·consensus` numbers are larger (0.6853 vs 0.5665 for `coval_core`)
because a consensus is denoised, not because the arms are better. Comparing raw gaps across targets
would be the units error twice over. Every comparison below is made in **resolution units** — each
target's gap divided by its OWN measured MDE — and each target's chance floor is MEASURED
per-comparison-type, because R285 established chance is neither 0.5 nor the same across types.

ESTIMAND        for each of the two targets: (a) its measured chance floor and ceiling, hence its
                band; (b) the number of the 45 arm-pairs RESOLVED at its own per-cell MDE;
                (c) the median |gap| / MDE across all 45 pairs — its resolving power per pair.
IDENTIFICATION  exact. Both targets are deterministic functions of data on disk; the floors are
                measured by drawing the comparison partner from a DIFFERENT prompt.
SCOPE           population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base ·
                baseline each pair is its own · regime ALL 15,593 annotations, cluster bootstrap.
WORLDS          W-CONSENSUS  consensus resolves strictly more pairs at equal or better agreement
                             -> the definition should name it, and the current choice was inherited
                             rather than reasoned. Change the text.
                W-ANNOTATOR  annotator resolves as many or more -> the inherited choice happens to
                             be the defensible one, and the file can say WHY instead of nothing.
                W-TIE        neither dominates -> the choice is genuinely free and must be declared
                             as a convention, not defended as a finding.
KILL            pre-registered: if `A2·consensus` resolves MORE of the 45 pairs than `A2·annotator`
                AND their orderings agree at τ >= 0.90, the definition's named target CHANGES.
                I am not permitted to keep the incumbent on the grounds that it is the incumbent.
POSITIVE CTRL   an arm against ITSELF under both targets: gap exactly 0, and NOT resolved. A target
                that "resolves" a self-comparison is broken and is dropped.
NEGATIVE CTRL   `random_k4_s0` vs `random_k4_s1` — the same rule at two seeds — must be UNRESOLVED
                under both. A target that separates a rule from itself is counting noise as signal,
                and would inflate exactly the statistic this round compares.
PLACEBO         included in the positive control.
NOISE FLOOR     per-cell MDE computed within each target, in that target's own units.
MULTIPLICITY    45 pairs x 2 targets = 90 cells; BH over all 90. Non-survivors reported.
SPECIFICATION   the target axis is the comparison; both are reported whole including every pair
                each fails to resolve.
SEEDS           the chance floors use 5 seeds each; consensus is seed-free by construction.
ARTIFACT        results/which_target.json with source hash.
IMPOSSIBLE      construct validity — whether either target is the right GOAL. Unchanged from R288:
                that needs an external criterion the release does not carry, and resolving power
                says nothing about it. A sharper instrument pointed at the wrong thing is sharper.
"""
import json, sys, math, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
NBOOT = 1500
Q = 0.05
ARMS = ["coval_core", "topw_k4", "generic", "gen", "full",
        "topwvar_k4", "random_k4_s0", "topabs_k4", "topvar_k4", "gen_sham"]


def main():
    tg, _ = load_targets()
    A_ = {a: load_sat(ROOT / "corebench" / "results" / f"sat_{a}.npz")
          for a in ARMS + ["random_k4_s1"]}
    pids = sorted(set.intersection(*(set(v) for v in A_.values())) &
                  {p for p in tg if len(tg[p]) >= 2})
    N = len(pids)
    HC = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    CONS = [np.sign(h.sum(axis=0)) for h in HC]
    AC = {a: [np.array(cls(yvec(A_[a][p], sorted({i for i, _ in A_[a][p]}))), float)
              for p in pids] for a in A_}
    print(f"  {N} prompts · {sum(len(h) for h in HC)} annotations · 2 targets\n")

    def score(a, tname):
        if tname == "A2·annotator":
            return np.array([np.mean([(AC[a][n] == h).mean() for h in HC[n]]) for n in range(N)])
        return np.array([(AC[a][n] == CONS[n]).mean() for n in range(N)])

    T = ["A2·annotator", "A2·consensus"]
    SC = {t: {a: score(a, t) for a in A_} for t in T}

    # ---- measured chance and ceiling PER TARGET -------------------------------------------
    def floors(tname):
        out = []
        for s in range(5):
            rng = np.random.default_rng(7100 + s); v = []
            for n in range(N):
                q = int(rng.integers(N))
                if q == n:
                    continue
                other = CONS[q] if tname == "A2·consensus" else HC[q][int(rng.integers(len(HC[q])))]
                v.append((AC["coval_core"][n] == other).mean())
            out.append(float(np.mean(v)))
        return float(np.mean(out)), float(np.std(out))

    CEIL = {"A2·annotator": float(np.mean([np.mean([(HC[n][i] == HC[n][j]).mean()
                                                    for i, j in itertools.combinations(range(len(HC[n])), 2)])
                                           for n in range(N)])),
            "A2·consensus": float(np.mean([np.mean([(CONS[n] == h).mean() for h in HC[n]])
                                           for n in range(N)]))}
    FL = {t: floors(t) for t in T}
    print("  EACH TARGET'S OWN SCALE — chance MEASURED, not assumed\n")
    print(f"    {'target':<15}{'chance':>9}{'ceiling':>10}{'band':>9}")
    for t in T:
        print(f"    {t:<15}{FL[t][0]:>9.4f}{CEIL[t]:>10.4f}{CEIL[t]-FL[t][0]:>9.4f}")

    IDX = np.random.default_rng(31337).integers(0, N, (NBOOT, N))

    def cell(x, y, t):
        d = SC[t][x] - SC[t][y]
        mde = ZEFF * d.std(ddof=1) / math.sqrt(N)
        bs = d[IDX].mean(axis=1)
        p = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
        return float(d.mean()), mde, float(p)

    # ---- controls -------------------------------------------------------------------------
    print("\n  CONTROLS\n")
    pos_ok = neg_ok = True
    for t in T:
        e0, m0, _ = cell("coval_core", "coval_core", t)
        e1, m1, _ = cell("random_k4_s0", "random_k4_s1", t)
        p_ok = (e0 == 0.0)
        n_ok = abs(e1) < m1
        pos_ok &= p_ok; neg_ok &= n_ok
        print(f"    {t:<15} self-comparison {e0:.2e} {'PASS' if p_ok else 'FAIL'}   ·   "
              f"same rule two seeds {e1:+.4f} vs MDE {m1:.4f} "
              f"{'PASS' if n_ok else 'FAIL — separates a rule from ITSELF'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — a target failed a control; no resolving-power comparison is readable.")
        return 1

    # ---- resolving power over all 45 pairs ------------------------------------------------
    res, ratios, grid = {}, {}, []
    for t in T:
        r, rat = 0, []
        for x, y in itertools.combinations(ARMS, 2):
            e, mde, p = cell(x, y, t)
            rat.append(abs(e) / mde)
            r += abs(e) >= mde
            grid.append((f"{t}|{x}|{y}", p))
        res[t] = r; ratios[t] = np.array(rat)
    grid.sort(key=lambda z: z[1]); C_ = len(grid)
    surv = sum(1 for i, (_, p) in enumerate(grid, 1) if p <= Q * i / C_)

    print(f"\n  RESOLVING POWER OVER ALL {len(list(itertools.combinations(ARMS,2)))} ARM PAIRS\n")
    print(f"    {'target':<15}{'RESOLVED':>10}{'median |gap|/MDE':>19}{'p90 |gap|/MDE':>16}")
    for t in T:
        print(f"    {t:<15}{res[t]:>7}/45{np.median(ratios[t]):>19.2f}"
              f"{np.percentile(ratios[t], 90):>16.2f}")
    print(f"\n    BH q={Q} over {C_} cells · {surv} survive · {C_-surv} do not")

    # ordering agreement, computed
    o = {t: sorted(ARMS, key=lambda a: -SC[t][a].mean()) for t in T}
    c = d = 0
    for x, y in itertools.combinations(ARMS, 2):
        s = np.sign(o[T[0]].index(x) - o[T[0]].index(y)) * np.sign(o[T[1]].index(x) - o[T[1]].index(y))
        c += s > 0; d += s < 0
    tau = (c - d) / (c + d)
    print(f"    ordering agreement between the two targets: Kendall τ = {tau:+.3f}")

    win = max(T, key=lambda t: res[t])
    changes = (res["A2·consensus"] > res["A2·annotator"]) and tau >= 0.90
    print("\n  " + "=" * 76)
    print(f"  PRE-REGISTERED KILL: consensus resolves MORE pairs AND τ ≥ 0.90 ?  {changes}")
    if changes:
        print(f"  -> W-CONSENSUS. The definition's named target CHANGES to A2·consensus: same")
        print(f"     ordering (τ={tau:+.3f}), strictly more of it resolved ({res['A2·consensus']} vs")
        print(f"     {res['A2·annotator']} of 45). The incumbent was inherited, not reasoned.")
    elif res["A2·annotator"] > res["A2·consensus"]:
        print(f"  -> W-ANNOTATOR. The inherited choice is the defensible one: it resolves")
        print(f"     {res['A2·annotator']} of 45 against {res['A2·consensus']}, at τ={tau:+.3f}. The file can now say WHY.")
    else:
        print(f"  -> W-TIE. Both resolve {res[T[0]]} of 45. The choice is a CONVENTION and must be")
        print(f"     declared as one rather than defended as a finding.")
    print("  ⚠ Resolving power says nothing about whether either target is the right GOAL.")
    print("     A sharper instrument pointed at the wrong thing is sharper.")
    print("  " + "=" * 76)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    out = pathlib.Path(__file__).parent / "results" / "which_target.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(source_sha=src, n_prompts=N,
                                   chance={t: FL[t] for t in T}, ceiling=CEIL,
                                   resolved={k_: int(v) for k_, v in res.items()}, tau=float(tau),
                                   median_ratio={t: float(np.median(ratios[t])) for t in T},
                                   winner=win, target_changes=bool(changes)), indent=1))
    print(f"\n  artifact {out.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
