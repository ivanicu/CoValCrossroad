#!/usr/bin/env python3
"""
R877 · the admitted set is one direction wide — WHAT direction?

⛔ WHY. R876 measured PR = 1.6368 for the 25 arms the definition admits, against a size-matched null
of 3.5605 [3.0313, 4.2135] — **below all 999 draws**. The admitted set is essentially ONE axis. **A
definition whose admitted set has a single axis is really selecting on that axis and should say so**,
and the axis has never been named.

⚠ **FIRST, A CORRECTION TO MY OWN NEXT.** Check #543 said *"read the top eigenvector's per-prompt
loadings"*. **R876's eigenvector is over ARMS** — a 25×25 correlation matrix — so its components are
per-ARM loadings and there are 25 of them, not 968. The per-PROMPT axis is **PC1 of the 25×968 score
matrix in prompt space**, which is a different object. The NEXT was written from memory of what the
matrix was, and the matrix is in the artifact.

⚠ **AND THE CANDIDATES MUST BE INDEPENDENT OF ARM SCORES OR THE TEST IS CIRCULAR.** PC1 of a set of
arms will correlate with *"mean A2 over those arms"* by construction — that is the arithmetic trap,
not a finding. So the candidate properties are split and LABELLED:
  · **INDEPENDENT** — computed from the target or the responses, never from an arm:
    `n_annotators`, `human_tie_rate`, `mean_response_length`, `response_length_spread`.
  · **PARTIALLY INDEPENDENT** — `mean A2 of the 71 REJECTED arms`: different arms, same task.
  · **CIRCULAR, reported as a WIRING CHECK and never as evidence** — `mean A2 of the 25 admitted
    arms` themselves. It MUST come back near 1; if it does not, the matrix is built wrong.

ESTIMAND        the correlation between the admitted set's first principal direction in prompt space
                and each candidate prompt property, against a prompt-permutation null.
IDENTIFICATION  exact for the PC; the candidates are all computable from released files. Whether the
                axis "is" any named property is NOT identified — correlation with a property is not
                identity, and the round reports correlations, not an interpretation.
SCOPE           population: the 25 arms R876 admitted (aliases excluded) × the shared prompts
                instrument: PC1 of the per-arm-centred score matrix; Pearson vs each candidate
                baseline:   prompt-permutation null, 1000 draws per candidate
                regime:     home release, judge J
WORLDS          A · PC1 tracks an INDEPENDENT prompt property well above its null -> the definition
                    is selecting on that property, and the clause should say so
                B · PC1 tracks only the partially-independent difficulty proxy -> the axis is
                    "how hard the prompt is for any arm", which is a property of the TASK and not
                    of what a core is
                C · PC1 tracks nothing above null -> the axis exists but is not any property this
                    round can name, and that is reported rather than dressed up
KILL            CONDITIONAL, all required:
                  ⭐ ① WIRING: PC1 must correlate ≥ 0.9 in absolute value with the mean A2 of the
                     admitted arms. This is CIRCULAR and is not evidence — it is the only check that
                     the matrix and the PC are what I think they are.
                  ⭐ ② g=0: a prompt-PERMUTED PC1 must correlate ~0 with every candidate. A pipeline
                     that finds structure in a shuffled axis is finding its own arithmetic.
                  ⭐ ③ the null must have non-zero spread for every candidate, else that candidate
                     is unreadable and is reported as such rather than scored.
                  ④ variance explained by PC1 must be consistent with R876's PR = 1.6368 — a set at
                     1.6 effective dimensions cannot have PC1 explaining, say, 30%.
MULTIPLICITY    5 candidates × 1 null each; BH q=0.05 across the candidate family, non-survivors
                reported beside survivors.
SEEDS           3 seeds for the null; spread reported.
ARTIFACT        results/the_axis.json
IMPOSSIBLE      cross-release · construct validated · causally identified. ⚠ And the one this round
                adds: **correlation with a property is not identity**. Even WORLD A licenses only
                "the axis co-varies with X", never "the axis IS X".
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

CORE, BLIND = "coval_core", "genericpool16"
ALIASES = ("coval_core_2bA", "coval_core_2bB")
NDRAW, Q = 1000, 0.05
L = ["A", "B", "C", "D"]


def bh(p, q=Q):
    C = len(p); o = np.argsort(p); k = -1
    for rank, i in enumerate(o, 1):
        if p[i] <= q * rank / C:
            k = rank
    m = np.zeros(C, bool)
    if k > 0:
        m[o[:k]] = True
    return m


def main() -> int:
    a875 = next((ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs").glob(
        "R875_*/results/admits_beyond_instance.json"), None)
    a876 = next((ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs").glob(
        "R876_*/results/admitted_diversity.json"), None)
    if a875 is None or a876 is None:
        print("  UNRUNNABLE: R875/R876 artifacts missing. Exit 2, never 0.")
        return 2
    d875, d876 = json.loads(a875.read_text()), json.loads(a876.read_text())
    admitted = [r["arm"] for r in d875["rows"]
                if r["admit_B"] and r["r_with_core"] is not None and r["arm"] not in ALIASES]
    rejected = [r["arm"] for r in d875["rows"] if not r["admit_B"]]
    print(f"  admitted {len(admitted)} · rejected {len(rejected)} · R876 PR = {d876['pr_observed']:.4f}")

    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / f"sat_{BLIND}.npz")
    A = load_sat(ROOT / "corebench" / "results" / f"sat_{CORE}.npz")
    pids = sorted(set(S) & set(A) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    n = len(pids)

    def vec(nm):
        f = ROOT / "corebench" / "results" / f"sat_{nm}.npz"
        if not f.exists():
            return None
        try:
            Sa = load_sat(f)
        except Exception:
            return None
        v = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                for c in range(6)] for h in H[k]]) if p in Sa else np.nan
                      for k, p in enumerate(pids)])
        return None if np.isfinite(v).sum() < 200 else np.nan_to_num(v, nan=np.nanmean(v))

    M = np.array([v for v in (vec(a) for a in admitted) if v is not None])
    R = np.array([v for v in (vec(a) for a in rejected) if v is not None])
    print(f"  matrix {M.shape} (arms x prompts) · rejected matrix {R.shape}")

    Mc = M - M.mean(axis=1, keepdims=True)
    U, s2, Vt = np.linalg.svd(Mc, full_matrices=False)
    pc1 = Vt[0]                                   # per-PROMPT axis, length n
    varexp = float(s2[0] ** 2 / (s2 ** 2).sum())
    print(f"  PC1 explains {varexp:.4f} of variance  (R876 PR {d876['pr_observed']:.4f} implies a "
          f"dominant first direction)")

    # ---- candidate prompt properties -----------------------------------------------------------
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
    lens = np.array([[len(txt[p][c]) for c in L] if p in txt else [np.nan] * 4 for p in pids],
                    float)
    cands = {
        "n_annotators": np.array([len(H[k]) for k in range(n)], float),
        "human_tie_rate": np.array([float(np.mean(H[k] == 0)) for k in range(n)]),
        "mean_response_length": np.nanmean(lens, axis=1),
        "response_length_spread": np.nanstd(lens, axis=1),
        "mean_A2_of_REJECTED_arms": R.mean(axis=0) if len(R) else np.full(n, np.nan),
    }
    kinds = {"n_annotators": "INDEPENDENT", "human_tie_rate": "INDEPENDENT",
             "mean_response_length": "INDEPENDENT", "response_length_spread": "INDEPENDENT",
             "mean_A2_of_REJECTED_arms": "PARTIALLY INDEPENDENT"}

    def pear(a, b):
        m = np.isfinite(a) & np.isfinite(b)
        if m.sum() < 100 or a[m].std() == 0 or b[m].std() == 0:
            return None
        return float(np.corrcoef(a[m], b[m])[0, 1])

    wiring = pear(pc1, M.mean(axis=0))
    k1 = wiring is not None and abs(wiring) >= 0.9
    print(f"  ① WIRING (CIRCULAR, not evidence)  |corr(PC1, mean A2 of admitted)| = "
          f"{abs(wiring):.4f} >= 0.9: {k1}  {'PASS' if k1 else 'FAIL'}")
    rngp = np.random.default_rng(7)
    pc1_perm = pc1[rngp.permutation(n)]
    perm_max = max(abs(pear(pc1_perm, v) or 0) for v in cands.values())
    k2 = perm_max < 0.15
    print(f"  ② g=0  a prompt-PERMUTED PC1 vs every candidate: max |r| = {perm_max:.4f} < 0.15: "
          f"{k2}  {'PASS' if k2 else 'FAIL'}")
    k4 = varexp >= 0.4
    print(f"  ④ PC1 variance {varexp:.4f} >= 0.40, consistent with PR {d876['pr_observed']:.3f}: "
          f"{k4}  {'PASS' if k4 else 'FAIL'}")

    rows, ps = [], []
    for nm, v in cands.items():
        r = pear(pc1, v)
        if r is None:
            rows.append({"candidate": nm, "kind": kinds[nm], "r": None, "p": None,
                         "note": "UNREADABLE — degenerate or too few prompts"})
            continue
        draws = []
        for sd in (11, 22, 33):
            rg = np.random.default_rng(sd)
            draws += [abs(pear(pc1[rg.permutation(n)], v) or 0) for _ in range(NDRAW // 3)]
        draws = np.array(draws)
        p = max(float((draws >= abs(r)).mean()), 1.0 / (len(draws) + 1))
        rows.append({"candidate": nm, "kind": kinds[nm], "r": r, "p": p,
                     "null_sd": float(draws.std()), "null_p95": float(np.percentile(draws, 95))})
        ps.append(p)
    k3 = all(x.get("null_sd", 0) > 1e-6 for x in rows if x["r"] is not None)
    print(f"  ③ every null has non-zero spread: {k3}  {'PASS' if k3 else 'FAIL'}")
    if not (k1 and k2 and k3 and k4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "rows": rows}, open(OUT / "the_axis.json", "w"),
                  indent=2)
        return 2

    live = [x for x in rows if x["r"] is not None]
    surv = bh(np.array([x["p"] for x in live]))
    for x, sv in zip(live, surv):
        x["survives_bh"] = bool(sv)
    print(f"\n  {'candidate':<28}{'kind':<24}{'r':>9}{'p':>10}{'null p95':>10}  BH")
    for x in sorted(live, key=lambda z: -abs(z["r"])):
        print(f"  {x['candidate']:<28}{x['kind']:<24}{x['r']:>+9.4f}{x['p']:>10.4f}"
              f"{x['null_p95']:>10.4f}  {'✓' if x['survives_bh'] else '·'}")

    ind = [x for x in live if x["kind"] == "INDEPENDENT" and x["survives_bh"]]
    par = [x for x in live if x["kind"].startswith("PARTIALLY") and x["survives_bh"]]
    world = "A" if ind else ("B" if par else "C")
    print(f"\n  ⭐ WORLD {world}: " + {
        "A": "PC1 tracks an INDEPENDENT prompt property above its null — the definition is "
             "selecting on that property and the clause should say so",
        "B": "PC1 tracks only the partially-independent difficulty proxy — the axis is 'how hard "
             "the prompt is for any arm', a property of the TASK and not of what a core is",
        "C": "PC1 tracks nothing above null — the axis exists and is not any property this round "
             "can name, reported rather than dressed up"}[world])
    if ind:
        b = max(ind, key=lambda z: abs(z["r"]))
        print(f"     strongest INDEPENDENT: {b['candidate']} r={b['r']:+.4f} p={b['p']:.4f}")
    print(f"     ⚠ CORRELATION IS NOT IDENTITY. Even WORLD A licenses 'the axis co-varies with X',")
    print(f"       never 'the axis IS X'. The wiring check is circular by construction and is")
    print(f"       reported as a wiring check, never as a finding.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_admitted": int(M.shape[0]), "n_prompts": n,
               "pc1_variance_explained": varexp, "wiring_corr": wiring,
               "permuted_max_abs_r": perm_max, "candidates": rows,
               "correction_to_next": "check #543 said 'per-prompt loadings of R876's eigenvector'; "
                                     "that eigenvector is over ARMS. The per-prompt axis is PC1 of "
                                     "the 25x968 matrix, a different object.",
               "not_identity": "correlation with a property is not identity"},
              open(OUT / "the_axis.json", "w"), indent=2)
    print(f"\n  artifact: results/the_axis.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
