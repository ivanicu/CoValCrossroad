"""R290 — does the definition's partition survive a DIFFERENT JUDGE?

WHY, AND WHY THIS SHOULD HAVE RUN LONG AGO. Every number in FORMULATION.md is a satisfaction score
from **one model**, Qwen3.5-2B-Base. The impossibility register in every round of this arc carried
`cross-model — needs more than one site`, and that line is right about the RELEASE and wrong about
the JUDGE. The judge is my instrument, not the site. Qwen3.5-0.8B-Base has been on the model store
the whole time. **I wrote a measurable thing into the impossible column and then stopped looking at
it**, which is the `wall never checked` failure aimed at the one document whose job is honesty.

ESTIMAND        under each judge: each arm's A2·annotator, its clause-① margin (vs random-from-
                rubric) and clause-② margin (vs the prompt-blind arm), and the ADMITTED SET;
                plus the per-prompt agreement between the two judges' scores.
IDENTIFICATION  exact under each judge separately. The cross-judge comparison is a comparison of
                two partitions, not of two scales — the raw numbers are NOT comparable across
                judges and no cell below subtracts one judge's score from the other's.
SCOPE           population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base AND
                Qwen3.5-0.8B-Base · baseline named per clause · regime k=4, ALL 15,593 annotations,
                cluster bootstrap over prompts.
WORLDS          W-JUDGE-FREE  the admitted set is identical under both judges -> the partition is a
                              property of the arms and the definition's scope widens: it holds
                              across a 2.5x model-size change.
                W-JUDGE-BOUND the admitted set moves -> every number in the file is
                              instrument-dependent, and the definition must name its judge exactly
                              as R288/R289 forced it to name its statistic.
KILL            pre-registered: if the ADMITTED SET differs between judges, FORMULATION.md's
                definition names `Qwen3.5-2B-Base` in its scope line, permanently, and every
                margin in the file is re-labelled as judge-conditional.
POSITIVE CTRL   ⛔ THE ONE THAT DECIDES WHETHER THIS ROUND CAN BE READ AT ALL. The 0.8B judge must
                (a) clear its OWN measured chance floor — partner drawn from a different prompt —
                and (b) recover the benchmark's LARGEST known gap, `generic − random_k4_s0`
                (+0.0587 at 2B), with the same sign and separably. **A judge that scores everything
                at chance produces a different partition for the trivial reason that it produces
                no partition**, and that is UNVERIFIED, never evidence of judge-dependence. This
                control is what separates "the judges disagree" from "the second judge is blind".
NEGATIVE CTRL   an arm against itself under each judge: exactly 0.
PLACEBO         included above.
NOISE FLOOR     each judge's own per-cell MDE, computed in its own units.
MULTIPLICITY    2 judges x arms x 2 clauses; BH over the whole grid of tested cells.
SPECIFICATION   the judge axis is the comparison; both partitions published whole.
SEEDS           chance floors at 5 seeds per judge; the arms are deterministic given the judge.
ARTIFACT        results/cross_judge.json with source hash.
IMPOSSIBLE      cross-RELEASE remains genuinely impossible — one release, and nothing here bounds
                what the definition admits on a second one. That line stays in the register; the
                cross-JUDGE line comes out of it, which is the point of the round.
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
ARMS = ["coval_core", "topw_k4", "generic", "gen", "random_k4_s0"]
JUDGES = {"2B  Qwen3.5-2B-Base": "sat_", "0.8B Qwen3.5-0.8B-Base": "sat08_"}


def main():
    tg, _ = load_targets()
    missing = [a for a in ARMS
               if not (ROOT / "corebench" / "results" / f"sat08_{a}.npz").exists()]
    if missing:
        print(f"  the 0.8B artifacts are not all on disk yet: {missing}")
        print("  This round is UNRUNNABLE until they land — that is not a null result.")
        return 2

    S = {}
    for jn, pre in JUDGES.items():
        S[jn] = {a: load_sat(ROOT / "corebench" / "results" / f"{pre}{a}.npz") for a in ARMS}
    pids = sorted(set.intersection(*(set(v) for j in S.values() for v in j.values())) &
                  {p for p in tg if len(tg[p]) >= 2})
    N = len(pids)
    HC = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    print(f"  {N} prompts · {sum(len(h) for h in HC)} annotations · {len(JUDGES)} judges\n")

    AC = {jn: {a: [np.array(cls(yvec(S[jn][a][p], sorted({i for i, _ in S[jn][a][p]}))), float)
                   for p in pids] for a in ARMS} for jn in JUDGES}
    SC = {jn: {a: np.array([np.mean([(AC[jn][a][n] == h).mean() for h in HC[n]])
                            for n in range(N)]) for a in ARMS} for jn in JUDGES}

    IDX = np.random.default_rng(31337).integers(0, N, (NBOOT, N))

    def cell(jn, x, y):
        d = SC[jn][x] - SC[jn][y]
        mde = ZEFF * d.std(ddof=1) / math.sqrt(N)
        bs = d[IDX].mean(axis=1)
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        p = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
        return float(d.mean()), lo, hi, float(p), mde

    # ---- POSITIVE CONTROL: is the second judge a judge at all? ----------------------------
    print("  POSITIVE CONTROL — can each judge see anything?\n")
    ok = {}
    for jn in JUDGES:
        fl = []
        for s in range(5):
            rng = np.random.default_rng(7300 + s); v = []
            for n in range(N):
                q = int(rng.integers(N))
                if q != n:
                    v.append((AC[jn]["coval_core"][n] == HC[q][int(rng.integers(len(HC[q])))]).mean())
            fl.append(float(np.mean(v)))
        chance = float(np.mean(fl))
        above = SC[jn]["coval_core"].mean() - chance
        e, lo, hi, _, mde = cell(jn, "generic", "random_k4_s0")
        a_ok = above > 3 * float(np.std(fl))
        b_ok = lo > 0 and abs(e) >= mde
        ok[jn] = a_ok and b_ok
        print(f"    {jn:<24} chance {chance:.4f} · coval {SC[jn]['coval_core'].mean():.4f} "
              f"(+{above:.4f}) {'OK' if a_ok else 'AT CHANCE'}")
        print(f"    {'':<24} largest known gap `generic − random` {e:+.4f} "
              f"[{lo:+.4f},{hi:+.4f}] vs MDE {mde:.4f}  {'OK' if b_ok else 'NOT RECOVERED'}")
    self_dev = max(abs(cell(jn, a, a)[0]) for jn in JUDGES for a in ARMS)
    print(f"\n  NEGATIVE CONTROL  an arm against itself, both judges: {self_dev:.2e}  "
          f"{'PASS' if self_dev == 0 else 'FAIL'}")
    blind = [jn for jn in JUDGES if not ok[jn]]
    if blind:
        print(f"\n  UNVERIFIED — {blind} did not clear its own controls. A judge that cannot see the")
        print("  benchmark's largest gap produces a different partition for the trivial reason that")
        print("  it produces no partition. That is NOT evidence of judge-dependence.")
        return 1

    # ---- the two partitions ---------------------------------------------------------------
    adm, cells, grid = {}, {}, []
    print(f"\n  EACH JUDGE'S PARTITION  (clause ① vs random-from-rubric, ② vs prompt-blind)\n")
    print(f"    {'judge':<24}{'arm':<13}{'A2':>8}{'① margin':>11}{'② margin':>11}  verdict")
    for jn in JUDGES:
        a_list = []
        for a in ARMS:
            if a in ("random_k4_s0", "generic"):
                continue
            c1 = cell(jn, a, "random_k4_s0"); c2 = cell(jn, a, "generic")
            o1 = c1[1] > 0 and abs(c1[0]) >= c1[4]
            o2 = c2[1] > 0 and abs(c2[0]) >= c2[4]
            cells[f"{jn}|{a}"] = dict(a2=float(SC[jn][a].mean()), c1=c1[:3], c2=c2[:3],
                                      ok1=bool(o1), ok2=bool(o2))
            grid += [(f"{jn}|{a}|1", c1[3]), (f"{jn}|{a}|2", c2[3])]
            if o1 and o2:
                a_list.append(a)
            print(f"    {jn:<24}{a:<13}{SC[jn][a].mean():>8.4f}{c1[0]:>+11.4f}{c2[0]:>+11.4f}  "
                  f"{'ADMITTED' if o1 and o2 else 'excluded'}")
        adm[jn] = a_list
        print()
    grid.sort(key=lambda z: z[1]); C_ = len(grid)
    surv = sum(1 for i, (_, p) in enumerate(grid, 1) if p <= Q * i / C_)

    # how much do the judges agree per prompt, at all?
    rr = {a: float(np.corrcoef(SC[list(JUDGES)[0]][a], SC[list(JUDGES)[1]][a])[0, 1]) for a in ARMS}
    print(f"    per-prompt score correlation between judges: " +
          "  ".join(f"{a} {v:.3f}" for a, v in rr.items()))
    print(f"    BH q={Q} over {C_} cells · {surv} survive")

    sets = {jn: tuple(sorted(adm[jn])) for jn in JUDGES}
    moved = len(set(sets.values())) > 1
    print("\n  " + "=" * 76)
    print(f"  PRE-REGISTERED KILL: does the ADMITTED SET differ between judges ?  {moved}")
    for jn in JUDGES:
        print(f"      {jn:<24}{sorted(adm[jn])}")
    if moved:
        print("  -> W-JUDGE-BOUND. Every number in the file is instrument-dependent. The definition")
        print("     must name its judge, exactly as R288/R289 forced it to name its statistic.")
    else:
        print("  -> W-JUDGE-FREE. The same arms are admitted by a judge 2.5x smaller, so the")
        print("     partition is a property of the arms and the definition's scope WIDENS.")
        print("     Bounded to these two models; cross-RELEASE stays genuinely impossible.")
    print("  " + "=" * 76)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    o = pathlib.Path(__file__).parent / "results" / "cross_judge.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(source_sha=src, n_prompts=N,
                                 admitted={jn: sorted(v) for jn, v in adm.items()},
                                 cells=cells, judge_corr=rr, moved=bool(moved)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
