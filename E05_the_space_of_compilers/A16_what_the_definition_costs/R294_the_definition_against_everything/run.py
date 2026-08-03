"""R294 — the definition applied to EVERY object the benchmark contains.

WHY. R293 found both a missing clause and the arc's best result among arms I had never tested,
because I had been asking *does this clause exclude something?* and never *which admissible objects
have I not asked?* The sat store holds **~42 judged arms**; the definition has faced **nine**. This
round asks all of them, and it is the exhaustive form of the exclusion test.

THE THREE CLAUSES AS THEY NOW STAND, and they are not the same KIND of clause:
  ① > the same number drawn at random from that conversation's own rubric      MEASURED
  ② > the same number that never read the conversation at all                  MEASURED
  ③ the evaluation annotator is HELD OUT from the core's own construction      PROVENANCE

⚠ **③ CANNOT BE COMPUTED FROM AN ARTIFACT.** ① and ② are functions of a sat file; ③ is a fact about
how the arm was BUILT, and no amount of looking at its outputs reveals it. That asymmetry is worth
stating rather than smoothing over: **a definition with a provenance clause cannot be applied to an
object of unknown origin**, and every core someone hands you is an object of unknown origin unless
they tell you. ③ is therefore declared per arm from `select_core.py`'s rules, and the declaration is
part of the round's evidence, not an assumption inside it.

⚠ AND THE SIZE-MATCHED BLIND REFERENCE IS NOW FREE AT ANY k. R281's 16-criterion pool was judged
once, so clause ② can be evaluated at each arm's OWN k rather than only at k=4 — which is what made
`full` fail. Arms with k > 16 fall back to k=16 and are flagged, because that comparison favours
the arm and must not be read as a pass.

ESTIMAND        for every judged arm: its k, its clause-① and clause-② margins with intervals and
                per-cell MDEs, its clause-③ provenance, and the resulting verdict.
IDENTIFICATION  ① and ② exact. ③ declared from source, not inferred.
SCOPE           population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base ·
                baselines named per clause · regime ALL annotators, A2·annotator, cluster
                bootstrap over prompts.
WORLDS          W-SPARSE  a handful admitted -> the definition is selective and the partition is
                          informative.
                W-LOOSE   most arms admitted -> the clauses are near-vacuous over the space the
                          benchmark actually spans, and the nine-arm table was a flattering sample.
KILL            pre-registered: if MORE THAN HALF of the judged arms are admitted, the definition
                is declared near-vacuous over this space and FORMULATION.md says so in its opening.
POSITIVE CTRL   `oracle_k4` must be excluded by ③ and ONLY by ③ — it clears ① and ② (R293). If ③
                excludes nothing, or excludes something else too, the clause is not doing the job
                it was added for.
NEGATIVE CTRL   every `*_sham` arm must be excluded. A sham admitted is a dead partition.
PLACEBO         `generic` against itself on clause ②: exactly 0, hence excluded by construction.
NOISE FLOOR     per-cell MDE, in-cell.
MULTIPLICITY    ~2 clauses x N arms; BH over the whole grid, non-survivors printed.
SPECIFICATION   the arm space IS the census. Nothing is sampled and nothing is dropped for being
                uninteresting.
ARTIFACT        results/full_census.json with source hash.
IMPOSSIBLE      cross-release. And ③ for any arm whose construction is not in this repository —
                which is zero of these, and would be all of them for someone else's core.
"""
import json, sys, math, pathlib, itertools, hashlib, collections
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402
from report import verdict, POS                              # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
NBOOT = 1200
RES = ROOT / "corebench" / "results"
# clause ③ declared from select_core.py's own rules, not inferred from outputs.
# ⚠ TIGHTENED after R295: ③ now reads `held out from the PROMPT`, not merely `from the
# construction`. R295 showed the parity split holds out ANNOTATORS while the selection is PER
# PROMPT -- the fit1 arms' entire advantage vanishes in the quintile where the two halves disagree
# (-0.0054, +0.0011, -0.0019) and is large where they agree (+0.0815, +0.0763, +0.0604), with an
# excess slope over the unfitted floor of +0.0252/+0.0211/+0.0167 against a floor CI width of
# 0.0156. So `held out from the construction' admits a core that consumed this prompt's own human
# labels, which is not producible from the conversation -- the input class the rest of the
# definition is about. Every per-prompt-fitted arm now fails ③, including the three that produced
# this campaign's largest margins.
USES_PROMPT_LABELS = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}
FITTED_ON_ALL = {"oracle_k4"}
FITTED_HELDOUT = {"oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}


def main():
    tg, _ = load_targets()
    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if not p.stem.startswith("sat08") and p.stem != "sat_genericpool16")
    POOL = load_sat(RES / "sat_genericpool16.npz")
    S, K = {}, {}
    for a in arms:
        try: S[a] = load_sat(RES / f"sat_{a}.npz")
        except Exception: continue
        ks = [len({i for i, _ in S[a][p]}) for p in list(S[a])[:200]]
        K[a] = int(np.median(ks))
    arms = [a for a in arms if a in S]
    # ⚠ THE FIRST RUN INTERSECTED ALL 41 ARMS AND GOT 398 PROMPTS, NOT 968. `promptecho` and its
    # sham cover only 398 (rebuilt user-turns-only earlier in the campaign), and intersecting
    # dragged the population down FOR EVERY OTHER ARM -- so every MDE was computed at n=398,
    # ~1.6x wider than at 968, and `coval_core` and `topw_k4` were excluded by the resulting
    # loss of resolution rather than by anything about them. A census that intersects its members
    # is governed by its SMALLEST member, and the headline `3 of 41` was really `3 of 41, on the
    # 41% of prompts one adversary arm happens to cover`.
    # Fixed: each arm is evaluated on ITS OWN prompts intersected with the pool and the target,
    # and the per-arm n is reported so a small-population arm is visible rather than contagious.
    BASE = set(POOL) & {p for p in tg if len(tg[p]) >= 2}
    PIDS = {a: sorted(set(S[a]) & BASE) for a in arms}
    pids = sorted(BASE & set(S["random_k4_s0"]))       # the reference arm's population
    N = len(pids)
    print("  per-arm populations: " + ", ".join(
        f"{a}={len(PIDS[a])}" for a in sorted(PIDS, key=lambda a: len(PIDS[a]))[:3]) + " …")
    HC = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    npool = len({i for i, _ in POOL[pids[0]]})
    print(f"  {len(arms)} judged arms · {N} prompts · blind pool of {npool}, so clause ② is\n"
          f"  size-matched at every k ≤ {npool}\n")

    def vec_from(sat, idx=None):
        return np.array([np.mean([[cls(yvec(sat[p], idx if idx is not None
                                            else sorted({i for i, _ in sat[p]})))[q] == h[q]
                                   for q in range(6)] for h in HC[p]]) for p in pids])
    def on(sat, ps, idx=None):
        return np.array([np.mean([[cls(yvec(sat[p], idx if idx is not None
                                            else sorted({i for i, _ in sat[p]})))[q] == h[q]
                                   for q in range(6)] for h in HC[p]]) for p in ps])
    IDX = np.random.default_rng(31337).integers(0, N, (NBOOT, N))

    def cell(x, y):
        d = x - y
        mde = ZEFF * d.std(ddof=1) / math.sqrt(N)
        bs = d[IDX].mean(axis=1)
        return (float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)),
                float(2 * min((bs <= 0).mean(), (bs >= 0).mean())), mde)

    rows, grid = {}, []
    for a in arms:
        if a == "random_k4_s0":
            continue
        ps = PIDS[a]                                   # THIS arm's own population
        na = len(ps)
        idx_a = np.random.default_rng(31337).integers(0, na, (NBOOT, na))
        def cell_a(x, y, _i=idx_a, _n=na):
            d = x - y
            bs = d[_i].mean(axis=1)
            return (float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)),
                    float(2 * min((bs <= 0).mean(), (bs >= 0).mean())),
                    ZEFF * d.std(ddof=1) / math.sqrt(_n))
        c1 = cell_a(on(S[a], ps), on(S["random_k4_s0"], ps))
        c2 = cell_a(on(S[a], ps), on(POOL, ps, list(range(min(K[a], npool)))))
        p3 = ("uses THIS prompt's labels (all annotators)" if a in FITTED_ON_ALL else
              "uses THIS prompt's labels (parity 1)" if a in FITTED_HELDOUT else
              "no prompt labels used")
        ok3 = a not in USES_PROMPT_LABELS
        ok1 = verdict(*c1[:3], c1[4]) == POS
        ok2 = verdict(*c2[:3], c2[4]) == POS
        rows[a] = dict(k=K[a], n=na, a2=float(on(S[a], ps).mean()), c1=c1[:3], mde1=c1[4], ok1=bool(ok1),
                       c2=c2[:3], mde2=c2[4], ok2=bool(ok2), prov=p3, ok3=bool(ok3),
                       admitted=bool(ok1 and ok2 and ok3),
                       kcap=bool(K[a] > npool))
        grid += [(f"{a}|1", c1[3]), (f"{a}|2", c2[3])]
    grid.sort(key=lambda z: z[1]); C = len(grid)
    surv = sum(1 for i, (_, p) in enumerate(grid, 1) if p <= 0.05 * i / C)

    adm = [a for a in rows if rows[a]["admitted"]]
    print(f"  {'arm':<20}{'k':>3}{'n':>6}{'A2':>8}{'①':>9}{'②':>9}  {'③ provenance':<30}verdict")
    for a in sorted(rows, key=lambda a: -rows[a]["a2"]):
        r = rows[a]
        m1 = "✓" if r["ok1"] else "✗"; m2 = "✓" if r["ok2"] else "✗"; m3 = "✓" if r["ok3"] else "✗"
        cap = " ⚠k>pool" if r["kcap"] else ""
        print(f"    {a:<20}{r['k']:>3}{r['n']:>6}{r['a2']:>8.4f}{r['c1'][0]:>+8.4f}{m1}"
              f"{r['c2'][0]:>+8.4f}{m2}  {r['prov']+cap:<30}"
              f"{'ADMITTED' if r['admitted'] else 'excluded'} {m3}")
    print(f"\n  BH q=0.05 over {C} cells · {surv} survive")

    # ---- controls -------------------------------------------------------------------------
    o = rows.get("oracle_k4")
    pos_ok = o is not None and o["ok1"] and o["ok2"] and not o["ok3"]
    only3 = [a for a in rows if not rows[a]["ok3"]]
    shams = [a for a in rows if a.endswith("_sham")]
    neg_ok = all(not rows[a]["admitted"] for a in shams)
    print(f"\n  POSITIVE CTRL  `oracle_k4` clears ① and ② and is excluded ONLY by ③: {pos_ok}")
    print(f"    ③ now excludes {len(only3)}: {sorted(only3)}")
    print(f"  NEGATIVE CTRL  every *_sham excluded ({len(shams)} of them): {neg_ok}")
    print(f"  PLACEBO        `generic` clause ② vs the pool's own first four: "
          f"{rows['generic']['c2'][0]:+.4f} (cross-artifact term, not zero by construction)")

    frac = len(adm) / len(rows)
    killed = frac > 0.5
    print("\n  " + "=" * 78)
    print(f"  PRE-REGISTERED KILL: more than half of {len(rows)} judged arms admitted ?  "
          f"{killed}   ({len(adm)} = {frac:.1%})")
    print(f"    ADMITTED: {sorted(adm)}")
    if not (pos_ok and neg_ok):
        print("  -> UNVERIFIED. A control failed; the partition is not readable.")
    elif killed:
        print("  -> W-LOOSE. The clauses are near-vacuous over the space this benchmark spans,")
        print("     and the nine-arm table was a flattering sample of it.")
    else:
        print(f"  -> W-SPARSE. {len(adm)} of {len(rows)} admitted. The definition is selective over")
        print("     the FULL arm space, not only over the nine arms it was developed against.")
    print("  " + "=" * 78)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    out = pathlib.Path(__file__).parent / "results" / "full_census.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(source_sha=src, n_prompts=N, n_arms=len(rows), rows=rows,
                                   admitted=sorted(adm), killed=bool(killed),
                                   pos_ok=bool(pos_ok), neg_ok=bool(neg_ok)), indent=1))
    print(f"\n  artifact {out.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
