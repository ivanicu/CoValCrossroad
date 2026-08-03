"""R293 — does the definition exclude an arm FITTED ON THE TARGET it is scored against?

WHY, AND IT IS AN EXCLUSION TEST THE DEFINITION HAS NEVER FACED. Nine arms have been run against
both clauses. The sat store holds **more than forty**, and among them are arms the definition has
never been asked about — including `oracle_k4`, whose own docstring in `select_core.py` reads
*"the k that best fit the human target. LEAKY BY CONSTRUCTION -- an upper bound, labelled, never a
candidate."*

**It was never a candidate to ITS AUTHOR. That is not the same as being excluded BY THE DEFINITION.**
A definition that admits an arm selected using the answer key has no clause against leakage, and
`realstat §4 the definition describes the instance` says a clause is only load-bearing if it
excludes an admissible object. This is the reverse test and the more dangerous one: does the
definition FAIL to exclude an object it obviously must?

⚠ AND THE HONEST VERSION IS ALSO ON DISK. `oracle_k4_fit1`, `greedy_k4_fit1` and `indep_k4_fit1`
are fitted on **parity-1 annotators only** and are evaluable on parity-0 — a genuinely held-out
fit. If those are admitted, that is not a defect: it means *fit a core to human judgements* is an
admissible route, which is a real finding about what a core can be. **The leaky and the held-out
arms must therefore be judged separately and never averaged.**

ESTIMAND        for each fitted arm: clause ① (vs random-from-rubric) and clause ② (vs the
                size-matched prompt-blind arm), and the admit/exclude verdict.
IDENTIFICATION  exact, but ONLY IF the evaluation annotators are disjoint from the fit annotators.
                For `*_fit1` the evaluation is restricted to parity-0. For `oracle_k4` no disjoint
                set exists — it was fitted on all of them — so its number is reported as LEAKY and
                is not comparable to the others.
SCOPE           population CoVal prompts with >=2 annotators (>=2 in the evaluation parity for the
                held-out arms) · instrument Qwen3.5-2B-Base · baseline named per clause · regime
                k=4, A2·annotator, cluster bootstrap over prompts.
WORLDS          W-LEAKPROOF  `oracle_k4` is EXCLUDED -> the definition happens to reject a fitted
                             arm without naming leakage, and the reason it rejects is worth knowing.
                W-LEAKY      `oracle_k4` is ADMITTED -> the definition has NO defence against an
                             arm built from the answer key, and it needs a third clause.
KILL            pre-registered: if `oracle_k4` clears both clauses, FORMULATION.md records that the
                definition admits a leaky arm and a held-out requirement is added to its text.
                I do not get to exclude it by pointing at its docstring; the docstring is its
                author's intent, not the definition's verdict.
POSITIVE CTRL   `oracle_k4` scored on the annotators it was FITTED on must be very high — well
                above every honest arm. If it is not, the fit did not take and nothing below reads.
NEGATIVE CTRL   `gen_sham` under the same pipeline must be excluded, as everywhere else.
PLACEBO         an arm against itself: exactly 0.
NOISE FLOOR     per-cell MDE, computed in-cell.
MULTIPLICITY    4 fitted arms x 2 clauses + 2 controls; BH over the tested cells.
SPECIFICATION   leaky vs held-out is the axis and both are published; the held-out arms are further
                split by fit rule (oracle / greedy / indep).
SEEDS           the evaluation is over ALL annotators of the evaluation parity, so seed-free.
ARTIFACT        results/fitted_arms.json with source hash.
IMPOSSIBLE      whether a fitted core generalises to a NEW release — one release, unchanged.
"""
import json, sys, math, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402
from report import row, header, verdict, POS                 # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
NBOOT = 2000
FITTED = {"oracle_k4": "LEAKY — fitted on ALL annotators",
          "oracle_k4_fit1": "held out — fitted on parity 1",
          "greedy_k4_fit1": "held out — greedy, parity 1",
          "indep_k4_fit1": "held out — independent scoring, parity 1"}
REF = ["random_k4_s0", "generic", "gen_sham"]


def main():
    tg, _ = load_targets()
    names = list(FITTED) + REF
    S = {}
    for a in names:
        p = ROOT / "corebench" / "results" / f"sat_{a}.npz"
        if not p.exists():
            print(f"  MISSING artifact: {a} — round is UNRUNNABLE, not null."); return 2
        S[a] = load_sat(p)
    pids = sorted(set.intersection(*(set(v) for v in S.values())) &
                  {p for p in tg if len(tg[p]) >= 2})
    # evaluation annotators: parity 0 for the held-out arms, ALL for the leaky one
    EV0 = {p: [t for i, t in enumerate(tg[p]) if i % 2 == 0] for p in pids}
    FIT1 = {p: [t for i, t in enumerate(tg[p]) if i % 2 == 1] for p in pids}
    pids = [p for p in pids if len(EV0[p]) >= 1 and len(FIT1[p]) >= 1]
    N = len(pids)
    print(f"  {N} prompts with both parities · evaluation on parity 0 for held-out arms\n")
    HC0 = {p: [cls(np.array(t[0], float)) for t in EV0[p]] for p in pids}
    HC1 = {p: [cls(np.array(t[0], float)) for t in FIT1[p]] for p in pids}
    AC = {a: {p: cls(yvec(S[a][p], sorted({i for i, _ in S[a][p]}))) for p in pids} for a in names}

    def vec(a, H):
        return np.array([np.mean([[AC[a][p][q] == h[q] for q in range(6)] for h in H[p]])
                         for p in pids])
    on_ev = {a: vec(a, HC0) for a in names}
    on_fit = {a: vec(a, HC1) for a in names}

    IDX = np.random.default_rng(31337).integers(0, N, (NBOOT, N))

    def cell(x, y, V):
        d = V[x] - V[y]
        mde = ZEFF * d.std(ddof=1) / math.sqrt(N)
        bs = d[IDX].mean(axis=1)
        return (float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)),
                float(2 * min((bs <= 0).mean(), (bs >= 0).mean())), mde)

    # ---- positive control: did the fit take? ----------------------------------------------
    o_fit, o_ev = on_fit["oracle_k4"].mean(), on_ev["oracle_k4"].mean()
    best_honest = max(on_ev[a].mean() for a in REF)
    pos_ok = o_fit > best_honest + 0.05
    print("  POSITIVE CONTROL — did the fit take?\n")
    print(f"    oracle_k4 on the annotators it was FITTED on : {o_fit:.4f}")
    print(f"    oracle_k4 on parity 0                        : {o_ev:.4f}")
    print(f"    best honest reference on parity 0            : {best_honest:.4f}")
    print(f"    {'PASS — the fit took, and by a wide margin' if pos_ok else 'FAIL — the fit did not take; nothing below reads'}")
    self_d = cell("oracle_k4", "oracle_k4", on_ev)
    print(f"  PLACEBO  an arm against itself: {self_d[0]:.2e}  "
          f"{'PASS' if self_d[0] == 0 else 'FAIL'}")
    if not (pos_ok and self_d[0] == 0):
        print("\n  UNVERIFIED — controls did not behave.")
        return 1

    # ---- the two clauses, per fitted arm ---------------------------------------------------
    print(f"\n  THE DEFINITION APPLIED TO FITTED ARMS  (evaluation: parity 0, disjoint from the fit)\n")
    print("  " + header("arm · clause", width=34))
    out, grid, admitted = {}, [], []
    for a, why in FITTED.items():
        V = on_fit if a == "oracle_k4" else on_ev      # the leaky arm has no disjoint set
        c1 = cell(a, "random_k4_s0", V)
        c2 = cell(a, "generic", V)
        print("  " + row(f"{a} · ① vs random", *c1[:3], c1[4], width=34))
        print("  " + row(f"{a} · ② vs prompt-blind", *c2[:3], c2[4], width=34,
                         extra=f"  [{why}]"))
        ok = verdict(*c1[:3], c1[4]) == POS and verdict(*c2[:3], c2[4]) == POS
        if ok: admitted.append(a)
        out[a] = dict(why=why, c1=c1[:3], mde1=c1[4], c2=c2[:3], mde2=c2[4], admitted=bool(ok))
        grid += [(f"{a}|1", c1[3]), (f"{a}|2", c2[3])]
        print()
    ns = cell("gen_sham", "generic", on_ev)
    neg_ok = verdict(*ns[:3], ns[4]) != POS
    print("  NEGATIVE CONTROL  " + row("gen_sham · ② vs prompt-blind", *ns[:3], ns[4], width=30)
          + ("  PASS" if neg_ok else "  FAIL"))
    grid.sort(key=lambda z: z[1]); C = len(grid)
    surv = sum(1 for i, (_, p) in enumerate(grid, 1) if p <= 0.05 * i / C)
    print(f"  BH q=0.05 over {C} cells · {surv} survive")

    leaky_admitted = "oracle_k4" in admitted
    print("\n  " + "=" * 76)
    print(f"  PRE-REGISTERED KILL: is the LEAKY `oracle_k4` ADMITTED ?  {leaky_admitted}")
    print(f"    admitted overall: {admitted}")
    if leaky_admitted:
        print("  -> W-LEAKY. The definition has NO defence against an arm built from the answer")
        print("     key. A held-out requirement goes into its text; the docstring calling it")
        print("     `never a candidate` is its author's intent, not the definition's verdict.")
    else:
        print("  -> W-LEAKPROOF. The definition excludes the leaky arm WITHOUT naming leakage.")
    ho = [a for a in admitted if a != "oracle_k4"]
    print(f"  HELD-OUT fitted arms admitted: {ho}")
    if ho:
        print("     -> `fit a core to human judgements` is an ADMISSIBLE ROUTE on this release,")
        print("        which is a finding about what a core can be, not a defect.")
    print("  " + "=" * 76)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    o = pathlib.Path(__file__).parent / "results" / "fitted_arms.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(source_sha=src, n_prompts=N, arms=out, admitted=admitted,
                                 leaky_admitted=bool(leaky_admitted),
                                 oracle_on_fit=float(o_fit), oracle_on_ev=float(o_ev)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
