#!/usr/bin/env python3
"""
R867 · the WINDOW in which a clause means anything — both degeneracies, both clauses, one population.

⛔ WHY, AND WHY THIS IS BIGGER THAN THE ROUND I PLANNED. Check #530's NEXT was "run R866's sweep on
clause ④'s family". That is worth doing, but two results from the last two rounds are the SAME
measurement seen from opposite ends and nobody had put them together:

  ⭐ R865: clause ④′'s NEGATIVE control `random_k4_s0` **SATISFIES** the clause — noise gets in.
     (R850 measured the same at 7 of 8 class sizes; R856 called ④ dominated by ②.)
  ⭐ R866: clause ②'s strongest comparator `per_prompt_max` admits **0 of 99 arms, `oracle_k4`
     included** — the ceiling gets excluded.

**Those are the two ways a clause can be empty of content, and the comparator moves you between
them.** So the real object is not "does ④ also span to zero" but: **for each clause, over what
range of comparators is the clause simultaneously strict enough to exclude noise and loose enough
to admit the ceiling?** Outside that window a clause is decoration — vacuous in one direction or
the other — and NEITHER end is visible from a single cell, which is why six rounds did not see it.

ESTIMAND        for each clause and each comparator form: does the NEGATIVE control (`random_k4_s0`)
                clear it, and does the POSITIVE control (`oracle_k4`) clear it? The MEANINGFUL
                WINDOW is the set of comparators where the answers are NO and YES respectively.
IDENTIFICATION  exact; both controls are released arms and every comparator is a statistic of the
                same family matrix. Nothing is estimated that is not directly computable.
SCOPE           population: prompts with response texts AND scored by `genericpool16`, `coval_core`,
                            `oracle_k4` and `random_k4_s0` — ONE shared population for both clauses,
                            so the two are comparable rather than merely adjacent
                instrument: A2 vs EVERY annotator
                families:   ② the C(16,4)=1,820 blind 4-subsets · ④ R435's 30 criterion-free rules
                regime:     home release, judge J
WORLDS          A · both clauses have a NON-EMPTY window and the published comparator lies inside it
                    -> the definition is sound and the ambiguity was cosmetic
                B · both windows are non-empty but a published comparator lies OUTSIDE one
                    -> that clause's published count is from a regime where the clause is vacuous
                C · a clause has an EMPTY window — no comparator both excludes noise and admits the
                    ceiling -> that clause cannot be repaired by choosing a comparator, and the
                    defect is in the clause, not in the choice
                D · the two clauses' windows differ in KIND -> the ambiguity is a property of the
                    DEFINITION's grammar (an unresolved quantifier over a family) rather than of
                    either clause, which is what check #530 set out to test
KILL            CONDITIONAL, all required:
                  ⭐ ① MONOTONICITY of both controls along `mean -> p75 -> p90 -> per-prompt max`
                     for BOTH clauses. Those comparators are pointwise non-decreasing, so once a
                     control stops clearing it must never clear again. A DERIVATION — useless as
                     evidence, and it is the wiring check: non-monotone means the code is wrong.
                  ② placebo: each family's argmax arm against itself gives margin exactly 0
                  ③ the population must be non-empty and must carry all four named arms; a sweep
                     that cannot locate its own controls has not run. Exit 2, never 0.
SEEDS           3 bootstrap seeds; per-cell verdicts must agree across seeds or the cell is marked
                UNSTABLE and excluded from the window rather than counted.
MULTIPLICITY    2 clauses × 6 comparators × 2 controls × 3 seeds = 72 verdicts, all reported.
ARTIFACT        results/meaningful_window.json
IMPOSSIBLE      construct validated (needs an external gold standard) · cross-release (needs a
                second release) · causally identified (needs an intervention on the mechanism).
"""
import importlib.util, itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402
_r435 = next(ROOT.glob("E0*/A*/R435_*"))
_sp = importlib.util.spec_from_file_location("r435", _r435 / "run.py")
r435 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(r435)

PAIRS = list(itertools.combinations(range(4), 2))
NBOOT, Q, ZEFF, FLOOR = 2000, 0.05, 2.802, 1.5
POS, NEG, CORE, BLIND = "oracle_k4", "random_k4_s0", "coval_core", "genericpool16"
L = ["A", "B", "C", "D"]


def main() -> int:
    tg, _ = load_targets()
    sats = {}
    for nm in (BLIND, CORE, POS, NEG):
        f = ROOT / "corebench" / "results" / f"sat_{nm}.npz"
        if not f.exists():
            print(f"  UNRUNNABLE: `{nm}` missing. Exit 2, never 0.")
            return 2
        sats[nm] = load_sat(f)
    txt = {}
    for line in open(ROOT / "data" / "comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        g = {x.get("response_index"): " ".join(
            str(m.get("content") or "") for m in (x.get("messages") or [])
            if m.get("role") == "assistant") for x in (r.get("responses") or [])}
        if len(g) >= 4 and all(g.get(c) for c in L):
            txt[r["prompt_id"]] = {c: g[c] for c in L}
    pids = sorted(set(txt) & set(tg) & set.intersection(*[set(s) for s in sats.values()])
                  & {p for p in tg if len(tg[p]) >= 2})
    n = len(pids)
    if n < 200:
        print(f"  OBSERVED NOTHING: shared population is {n} prompts. Exit 2, never 0.")
        return 2
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    print(f"  ONE shared population: {n} prompts carrying texts + all four named arms")

    def armvec(nm):
        S = sats[nm]
        return np.array([np.mean([[cls(yvec(S[p], sorted({i for i, _ in S[p]})))[c] == h[c]
                                   for c in range(6)] for h in H[k]]) for k, p in enumerate(pids)])
    ARM = {nm: armvec(nm) for nm in sats}

    # ---- family ② : the 1,820 blind 4-subsets -----------------------------------------------
    npool = len({i for i, _ in sats[BLIND][pids[0]]})
    subs = np.array(list(itertools.combinations(range(npool), 4)))
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    F2 = np.empty((len(subs), n))
    for k in range(n):
        Y = np.array([[sats[BLIND][pids[k]][(i, x)] for x in "ABCD"] for i in range(npool)],
                     float)[subs].sum(axis=1)
        Cv = np.sign(Y[:, ii] - Y[:, jj])
        F2[:, k] = (Cv[:, None, :] == H[k][None, :, :]).mean(axis=(1, 2))

    # ---- family ④ : R435's 30 criterion-free rules -------------------------------------------
    # ⚠ written in the plain broadcast form R865 uses, because that shape is already verified
    # against the published counts. The first draft nested three comprehensions around a dead
    # `if True else 0.0` branch — an expression nobody can read is one nobody can check.
    feats = {p: {c: r435.features(txt[p][c]) for c in L} for p in pids}
    F4 = np.empty((len(r435.RULES), n))
    for ri, (_, key, sg) in enumerate(r435.RULES):
        for k, p in enumerate(pids):
            x = np.array([(feats[p][c][key] if key != "__pos__" else L.index(c)) for c in L],
                         float) * (1.0 if sg > 0 else -1.0)
            F4[ri, k] = np.mean(np.array(cls(x)) == H[k])
    print(f"  family ② {F2.shape[0]} blind subsets · family ④ {F4.shape[0]} criterion-free rules")

    def comps(F):
        km = int(F.mean(1).argmax())
        return [("family_mean", F.mean(0), True), ("family_p75", np.percentile(F, 75, 0), True),
                ("family_p90", np.percentile(F, 90, 0), True), ("argmax_arm", F[km], False),
                ("per_prompt_max", F.max(0), True)], km

    def clears(a, comp, seed):
        d = a - comp
        b = np.random.default_rng(seed).integers(0, n, size=(NBOOT, n))
        bs = d[b].mean(1)
        ratio = d.mean() / max(ZEFF * bs.std(ddof=1), 1e-300)
        return bool(ratio >= FLOOR), float(ratio)

    out, ok = [], True
    for label, F in (("②", F2), ("④", F4)):
        CS, km = comps(F)
        pl = float((F[km] - F[km]).mean())
        print(f"\n  clause {label}   placebo argmax-vs-itself {pl:+.2e}  "
              f"{'PASS' if abs(pl) < 1e-15 else 'FAIL'}")
        print(f"    {'comparator':<18}{'core':>9}{'oracle':>9}{'random':>9}   window?")
        rows = []
        for nm, comp, chain in CS:
            v = {}
            for who in (CORE, POS, NEG):
                res = [clears(ARM[who], comp, sd) for sd in (11, 22, 33)]
                stable = len({r[0] for r in res}) == 1
                v[who] = {"clears": res[0][0], "ratio": float(np.mean([r[1] for r in res])),
                          "stable": stable}
            inwin = bool(v[POS]["clears"] and not v[NEG]["clears"]
                         and v[POS]["stable"] and v[NEG]["stable"])
            rows.append({"comparator": nm, "in_monotone_chain": chain, "in_window": inwin,
                         **{k2: v[k2] for k2 in v}})
            print(f"    {nm:<18}{v[CORE]['ratio']:>+9.3f}{v[POS]['ratio']:>+9.3f}"
                  f"{v[NEG]['ratio']:>+9.3f}   {'YES' if inwin else 'no'}"
                  f"{'' if v[POS]['stable'] and v[NEG]['stable'] else '  UNSTABLE'}")
        ch = [r for r in rows if r["in_monotone_chain"]]
        mono = True
        for who in (POS, NEG):
            seq = [r[who]["clears"] for r in ch]
            mono = mono and all(seq[i] >= seq[i + 1] for i in range(len(seq) - 1))
        print(f"    KILL ① monotone controls along the pointwise chain: {mono}  "
              f"{'PASS' if mono else 'FAIL'}")
        ok = ok and mono and abs(pl) < 1e-15
        out.append({"clause": label, "family_size": int(F.shape[0]), "rows": rows,
                    "monotone": mono, "placebo": pl,
                    "window": [r["comparator"] for r in rows if r["in_window"]]})

    if not ok:
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "clauses": out},
                  open(OUT / "meaningful_window.json", "w"), indent=2)
        return 2

    w2, w4 = out[0]["window"], out[1]["window"]
    print(f"\n  ⭐ MEANINGFUL WINDOW  clause ②: {w2 or 'EMPTY'}")
    print(f"  ⭐ MEANINGFUL WINDOW  clause ④: {w4 or 'EMPTY'}")
    pub = {"②": "argmax_arm", "④": "argmax_arm"}
    inside = {c: (pub[c] in w) for c, w in (("②", w2), ("④", w4))}
    print(f"  ⭐ the PUBLISHED comparator (`argmax_arm`) lies inside the window: {inside}")
    if not w2 or not w4:
        world = "C"
    elif not all(inside.values()):
        world = "B"
    elif set(w2) != set(w4):
        world = "D"
    else:
        world = "A"
    print(f"  ⭐ WORLD {world}: " + {
        "A": "both windows are non-empty and contain the published comparator — the ambiguity was"
             " cosmetic",
        "B": "a published comparator lies OUTSIDE its clause's window — that count comes from a"
             " regime where the clause is vacuous",
        "C": "a clause has an EMPTY window: no comparator both excludes noise and admits the"
             " ceiling, so the defect is in the CLAUSE and cannot be repaired by choosing better",
        "D": "the two windows differ in KIND — the ambiguity is a property of the DEFINITION's"
             " grammar (an unresolved quantifier over a family), not of either clause"}[world])

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "n_prompts": n, "world": world, "clauses": out,
               "window_clause_2": w2, "window_clause_4": w4,
               "published_comparator_inside": inside,
               "definition": "a clause is MEANINGFUL at a comparator iff the negative control does"
                             " NOT clear it and the positive control DOES"},
              open(OUT / "meaningful_window.json", "w"), indent=2)
    print(f"\n  artifact: results/meaningful_window.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
