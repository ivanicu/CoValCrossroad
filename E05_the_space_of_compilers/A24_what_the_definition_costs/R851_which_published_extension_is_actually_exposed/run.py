#!/usr/bin/env python3
"""
R851 · which published extension is actually exposed to R850's noise critique? — and what is it?

⛔ MY OWN NEXT OVERREACHED, AND THE REFUTATION WAS ALREADY IN THE FILE. Entry 1370 closed with
*"every extension this project has ever reported may carry a similar free component"*. The
clause-by-clause table at `DEFINITION.md:582-586` already classifies them:

    ① better than a draw of the prompt's own rubric   0 of 41   DERIVED (region empty by arithmetic)
    ② better than a prompt-blind set                 33 of 42   MEASURED
    ③ no prompt labels                               14 of 42   DERIVED (read from the source)
    ④ better than every criterion-free rule           0 of 42   MEASURED — excludes nothing

**A DERIVED clause has no noise floor of R850's kind**: there is no selection, no interval and no
BH to be free, and shuffling the target cannot move a count obtained by reading which arms consume
labels. **④ strict excludes 0, so it has no extension to inflate.** So exactly ONE published
extension is exposed — **②'s** — and the sweeping version of the worry was wrong.

ESTIMAND        the number of arms satisfying clause ② (beats a size-matched PROMPT-BLIND set,
                resolvably, BH q=0.05) on the REAL target, and the same count on a SHUFFLED target.
                The difference is ②'s excess over what the procedure admits for free.
IDENTIFICATION  yes; every arm and the prompt-blind comparator are released score matrices.
SCOPE           population: all scored arms, per-arm prompt sets (>=200), NOT intersected —
                            R850's population bug, not repeated
                instrument: A2 vs the EVEN annotators; comparator = the prompt-blind arm
                baseline:   the same procedure on a pair-shuffled target
                regime:     home release, judge J
WORLDS          A · ②'s extension is mostly free — the noise count is close to the real one, and
                    the clause that `carries the whole boundary among label-free arms` carries
                    much less than its published count suggests
                B · ②'s extension is mostly real — the noise count is far below, and ② is the one
                    clause of four whose measured selectivity survives its own null
KILL            CONDITIONAL: placebo == 0 exactly, positive control satisfies, negative control
                does not. Otherwise UNVERIFIED and no count is reported.
POSITIVE CTRL   `oracle_k4` must satisfy ②.
NEGATIVE CTRL   `random_k4_s0` must NOT satisfy ②. ⚠ In R850 this control failed at 7 of 8 class
                sizes for ④′, so it is not a formality here.
PLACEBO         the comparator against itself must be exactly 0.
NOISE ARM       identical procedure, pair-labels shuffled. Reported beside, never subtracted
                silently.
MULTIPLICITY    BH q=0.05 over all arms; tested and surviving both reported.
ARTIFACT        results/clause2_noise_extension.json.
IMPOSSIBLE      construct validated · cross-release · causally identified. N/A with what each needs.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
import score as SC                                              # noqa: E402

NBOOT = 2000
BLIND = "genericpool16"          # the prompt-blind, size-matched comparator
POS_CTRL, NEG_CTRL = "oracle_k4", "random_k4_s0"


def bh_mask(p, q=0.05):
    C = len(p); o = np.argsort(p); k = -1
    for rank, i in enumerate(o, 1):
        if p[i] <= q * rank / C:
            k = rank
    m = np.zeros(C, bool)
    if k > 0:
        m[o[:k]] = True
    return m


def main() -> int:
    targets, _ = SC.load_targets()
    pids = [p for p in sorted(targets) if len(targets[p]) >= 2]
    Heven = {p: np.array([SC.cls(np.array(y, float)) for y, _ in targets[p][1::2]]) for p in pids}
    pids = [p for p in pids if len(Heven[p])]
    rngN = np.random.default_rng(20260806)
    Hnoise = {p: Heven[p][:, rngN.permutation(6)] for p in pids}
    print(f"  prompts with a non-empty EVEN half: {len(pids)}")

    def vec(name, H):
        f = ROOT / "corebench" / "results" / f"sat_{name}.npz"
        if not f.exists():
            return None
        try:
            S = SC.load_sat(f)
        except Exception:
            # ⚠ at least one released .npz uses a key shape `load_sat` cannot parse. Skipped and
            # COUNTED below rather than silently dropped -- an arm that cannot be read is not an
            # arm that failed the clause, and conflating them would shrink the denominator.
            return None
        return np.array([np.mean(SC.cls(SC.yvec(S[p], sorted({i for i, _ in S[p]}))) == H[p])
                         if p in S else np.nan for p in pids])

    Bev, Bno = vec(BLIND, Heven), vec(BLIND, Hnoise)
    if Bev is None:
        print(f"  UNRUNNABLE: comparator `{BLIND}` missing. Exit 2, never 0.")
        return 2

    names, Aev, Ano, unreadable, thin = [], [], [], [], []
    for f in sorted((ROOT / "corebench" / "results").glob("sat_*.npz")):
        nm = f.stem[4:]
        v, w = vec(nm, Heven), vec(nm, Hnoise)
        if v is None:
            unreadable.append(nm); continue
        if np.isfinite(v).sum() < 200:
            thin.append(nm); continue
        names.append(nm); Aev.append(v); Ano.append(w)
    print(f"  arms skipped: {len(unreadable)} unreadable {unreadable[:3]} · "
          f"{len(thin)} under 200 prompts — REPORTED, not silently dropped")
    Aev, Ano = np.array(Aev), np.array(Ano)
    n = len(pids)
    print(f"  arms: {len(names)} · per-arm coverage min "
          f"{int(np.isfinite(Aev).sum(1).min())} · median "
          f"{int(np.median(np.isfinite(Aev).sum(1)))}  (NOT intersected — R850's bug)")

    bidx = np.random.default_rng(4242).integers(0, n, size=(NBOOT, n))

    def satisfies(A, B):
        D = A - B
        M = np.isfinite(D).astype(float)
        Dz = np.nan_to_num(D, nan=0.0)
        bs = (Dz[:, bidx].sum(2) / np.maximum(M[:, bidx].sum(2), 1.0)).T
        lo = np.percentile(bs, 2.5, axis=0)
        p = np.maximum(2 * np.minimum((bs <= 0).mean(0), (bs >= 0).mean(0)), 1.0 / (NBOOT + 1))
        return bh_mask(p) & (lo > 0), np.nanmean(D, 1)

    # ---- PLACEBO ---------------------------------------------------------------------------
    pl = float(np.nanmean(Bev - Bev))
    pl_ok = abs(pl) < 1e-12
    print(f"  PLACEBO  comparator vs itself: {pl:+.2e}  {'PASS' if pl_ok else 'FAIL'}")

    sat_r, mean_r = satisfies(Aev, Bev)
    sat_n, _ = satisfies(Ano, Bno)
    ip = names.index(POS_CTRL) if POS_CTRL in names else None
    ineg = names.index(NEG_CTRL) if NEG_CTRL in names else None
    pos_ok = bool(sat_r[ip]) if ip is not None else False
    neg_ok = (not bool(sat_r[ineg])) if ineg is not None else False
    print(f"  POSITIVE  `{POS_CTRL}` satisfies ②: {pos_ok}  {'PASS' if pos_ok else 'FAIL'}")
    print(f"  NEGATIVE  `{NEG_CTRL}` must NOT: {neg_ok}  {'PASS' if neg_ok else 'FAIL'}"
          f"   (it failed for ④′ at 7 of 8 class sizes in R850, so this is not a formality)")

    if not (pl_ok and pos_ok and neg_ok):
        print("\n  UNVERIFIED: a control failed for its own reasons. No count reported. Exit 2.")
        json.dump({"verdict": "UNVERIFIED", "placebo": pl, "pos": pos_ok, "neg": neg_ok},
                  open(OUT / "clause2_noise_extension.json", "w"), indent=2)
        return 2

    R, N = int(sat_r.sum()), int(sat_n.sum())
    print(f"\n  ⭐ clause ② satisfied by {R} of {len(names)} arms on the REAL target")
    print(f"     and by {N} of {len(names)} on a SHUFFLED target — EXCESS {R - N}")
    core = names.index("coval_core") if "coval_core" in names else None
    if core is not None:
        print(f"     `coval_core`: margin {mean_r[core]:+.4f} — "
              f"{'SATISFIES' if sat_r[core] else 'FAILS'}")
    world = "A" if (R - N) < 0.5 * R else "B"
    print(f"  ⭐ WORLD {world}: " + {
        "A": "②'s extension is mostly FREE — the clause that 'carries the whole boundary among"
             " label-free arms' carries much less than its count suggests",
        "B": "②'s extension is mostly REAL — ② is the one clause of four whose measured"
             " selectivity survives its own null"}[world])
    print(f"     ⚠ ① and ③ are DERIVED (0 of 41 by arithmetic; 14 of 42 read from the source) and")
    print(f"     have NO noise floor of this kind. ④ strict excludes 0. So ② was the ONLY exposed")
    print(f"     published extension, and entry 1370's 'every extension' was too broad.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_arms": len(names),
               "clause2_real": R, "clause2_noise": N, "excess": R - N,
               "comparator": BLIND,
               "controls": {"placebo": pl, "pos": pos_ok, "neg": neg_ok},
               "derived_clauses_have_no_noise_floor": ["①", "③"],
               "arms": [{"arm": a, "margin": float(m), "satisfies_real": bool(s),
                         "satisfies_noise": bool(sn)}
                        for a, m, s, sn in zip(names, mean_r, sat_r, sat_n)]},
              open(OUT / "clause2_noise_extension.json", "w"), indent=2)
    print(f"\n  artifact: results/clause2_noise_extension.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
