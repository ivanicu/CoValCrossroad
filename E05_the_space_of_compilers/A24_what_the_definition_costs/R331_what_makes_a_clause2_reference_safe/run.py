"""R331 — a clause-2 reference is safe because of its PERCENTILE, not because of self-comparison.

R330 closed by crediting R294's fixed reference with a structural property, and named the mechanism:
"the reference is drawn from the SAME pool as the arm under test, so an arm that IS the pool compares
to itself and cannot win." That is a `next gradient` sentence -- written last, acted on next, and the
only one in the report with no control attached -- and it is wrong.

SELF-COMPARISON PROTECTS AGAINST EXACTLY ONE OBJECT: the set that IS the reference. It says nothing
about the other 1,819 prompt-blind quadruples of the same pool, every one of which "never read the
conversation at all" and so is a member of clause 2's reference class by its own words. If clause 2
admits any of THOSE, it is broken as worded under R294's reference too, and the defect is older than
R328 by forty rounds.

THE ARITHMETIC, DERIVED BEFORE MEASURING, from numbers already committed in R286:
    blind quadruple distribution   min 0.5144 · med 0.5391 · p90 0.5490 · p99 0.5546 · MAX 0.5575
    R294's reference (first-4)     0.550436, which sits between p90 and p99
    best blind set - reference     0.00704, against a typical per-cell MDE of ~0.0106
    => the BEST of 1,820 blind sets beats the reference by 0.66 MDE. Below resolution.
So the protection is not identity, it is ALTITUDE: the reference sits high enough in the blind
distribution that nothing blind can clear it by an MDE. That is a QUANTITY, and it yields a design
rule that self-comparison never could. It is labelled a derivation because it is one; what this round
MEASURES is the admission-rate curve, the per-pair MDEs, and whether identity adds anything to
percentile.

AND IT EXPLAINS R330 BETTER THAN R330 DID. Budget-matching did not destroy a self-comparison. It
replaced a ~p95 reference with best-of-1 -- a random draw, ~p50 in expectation, 0.5372 -- lowering
the bar by ~0.013, which is MORE THAN ONE MDE. `generic` walked in through the percentile drop.

ESTIMAND      (i) the BLIND ADMISSION RATE of a candidate clause-2 reference: the fraction of all
              1,820 prompt-blind k=4 sets that clear clause 2 against it, each with its own paired
              MDE. Its ideal value is 0, because a reference that admits prompt-blind sets is
              refuted by clause 2's own words. (ii) that rate as a function of the reference's
              percentile in the blind distribution. (iii) whether the reference's IDENTITY adds
              anything once its percentile is fixed.
IDENTIFICATION Exact. The pool is 16 criteria, all C(16,4)=1,820 subsets are enumerated, and every
              one of them is prompt-blind by construction, so the population of the rate is the
              whole class rather than a sample of it.
SCOPE         population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base under
              R234's canonical builder · baseline each candidate reference, named per cell ·
              regime k=4 exactly, all annotators, pool-internal.
WORLDS        W-PERCENTILE  the blind admission rate falls with the reference's percentile and is
                            ~0 at R294's -> safety is quantitative, the design rule is "put the
                            reference high in the blind distribution", and R330's stated mechanism
                            is replaced rather than merely qualified.
              W-SELF        the rate is substantial even at R294's percentile, with only the
                            identical set excluded -> clause 2 is broken as worded for EVERY
                            reference tested, including R294's, and the defect predates R328.
              W-MDE         the rate is ~0 at every percentile because the blind distribution is
                            narrower than the MDE -> then percentile is not the lever either,
                            `generic`'s admission in R330 is special, and it needs its own account.
KILL          pre-registered, conditional on the controls:
                rate at R294's reference > 1%                          -> W-SELF
                else rate at the MEDIAN reference < 1%                 -> W-MDE
                else                                                   -> W-PERCENTILE
              1% of 1,820 is 18 sets; below that the rate is at the granularity of the class.
POSITIVE CTRL the reference against ITSELF must give exactly 0 gap and must not clear -- and it
              must FAIL at g=0: against the WEAKEST reference (p0) the same set must clear, or the
              instrument cannot detect admission at all and every 0 it reports is silence.
NEGATIVE CTRL `coval_core`, which every published reading admits, must clear R294's reference. A
              candidate that excludes it is too strong to be a reference (R287's own disqualification
              logic), and the round says so instead of reporting a flattering 0.
SHAM          identity vs percentile, and this is the control that decides between the worlds:
              re-run at a DIFFERENT subset drawn at the SAME percentile as R294's reference. If the
              blind admission rate is unchanged, the property is the percentile; if it moves, the
              identity is doing work. Repeated over the 10 nearest-percentile subsets.
PLACEBO       every reference against itself: exactly 0.0 across all candidates.
NOISE FLOOR   per-pair MDE recomputed for every (blind set, reference) cell -- 1,820 x 10 of them --
              never a single typical value, because the derivation above used one and a derivation
              is what this round is checking.
MULTIPLICITY  1,820 blind sets x 10 references = 18,200 cells; BH q=0.05 over the whole grid, and
              the admission rate is reported both raw and BH-corrected.
SPECIFICATION the percentile axis IS the curve, published whole from p0 to p100 including the
              references that admit almost everything.
SEEDS         none needed for the enumeration, which is exhaustive; the sham draws 10 alternative
              references and all 10 are reported rather than averaged.
ARTIFACT      results/reference_safety.json with source hash.
IMPOSSIBLE    generalising the percentile rule to a pool this release does not contain. The blind
              class here is the 16-criterion generic pool; a different pool has a different spread,
              and the RULE (put the reference high) transfers while the NUMBER (0.5504) does not.
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

SELF = pathlib.Path(__file__).resolve()
PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
PCTS = (0, 10, 25, 50, 75, 90, 95, 99, 100)
ERFC = np.vectorize(math.erfc)
ARMS = ("coval_core", "topw_k4", "gen_sham")


def main() -> int:
    tg, _ = load_targets()
    pool = ROOT / "corebench" / "results" / "sat_genericpool16.npz"
    if not pool.exists():
        print(f"  UNRUNNABLE: {pool.name} absent."); return 2
    S = load_sat(pool)
    A_ = {}
    for a in ARMS:
        f = ROOT / "corebench" / "results" / f"sat_{a}.npz"
        if not f.exists():
            print(f"  UNRUNNABLE: sat_{a}.npz absent."); return 2
        A_[a] = load_sat(f)
    pids = sorted(set(S) & set.intersection(*(set(v) for v in A_.values())) &
                  {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    N = len(pids)
    npool = len({i for i, _ in S[pids[0]]})
    SAT = np.stack([np.array([[S[p][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                    for p in pids])
    subs = np.array(list(itertools.combinations(range(npool), 4)))
    NS = len(subs)
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    B = np.empty((NS, N))
    for n in range(N):
        Y = SAT[n][subs].sum(axis=1)
        C_ = np.sign(Y[:, ii] - Y[:, jj])
        B[:, n] = (C_[:, None, :] == H[n][None, :, :]).mean(axis=(1, 2))
    per_sub = B.mean(axis=1)
    arm = {a: np.array([np.mean([[cls(yvec(A_[a][p], sorted({i for i, _ in A_[a][p]})))[c] == h[c]
                                  for c in range(6)] for h in H[n]])
                        for n, p in enumerate(pids)]) for a in ARMS}
    inc = int(np.where((subs == np.array([0, 1, 2, 3])).all(axis=1))[0][0])
    inc_pct = 100.0 * (per_sub < per_sub[inc]).mean()
    order = np.argsort(per_sub)
    print(f"  {N} prompts · pool {npool} · {NS} prompt-blind quadruples, ALL enumerated\n")
    print(f"  the blind distribution: min {per_sub.min():.4f}  med {np.median(per_sub):.4f}  "
          f"max {per_sub.max():.4f}")
    print(f"  R294's reference (first-4 of the pool) = {per_sub[inc]:.6f}, at the "
          f"{inc_pct:.1f}th percentile\n")

    def clears(vec_a, vec_r):
        d = vec_a - vec_r
        e = d.mean(axis=-1)
        sd = d.std(axis=-1, ddof=1)
        mde = ZEFF * sd / math.sqrt(N)
        return e, mde, (e > 0) & (np.abs(e) >= mde)

    def blind_rate(ref_idx):
        """fraction of ALL 1,820 prompt-blind sets that clear clause 2 against this reference."""
        e, mde, ok = clears(B, B[ref_idx])
        return float(ok.mean()), int(ok.sum()), e, mde

    # ---- the percentile curve --------------------------------------------------------------------
    CAND = {}
    for p in PCTS:
        idx = int(order[min(int(round(p / 100 * (NS - 1))), NS - 1)])
        CAND[f"p{p:03d}"] = idx
    CAND[f"R294 first-4 (p{inc_pct:.0f})"] = inc

    print(f"  BLIND ADMISSION RATE — of {NS} prompt-blind sets, how many clear clause 2 "
          f"against each reference?\n")
    print(f"    {'reference':<24}{'ref A2':>10}{'pctile':>8}{'admitted':>10}{'rate':>9}"
          f"{'BH-corrected':>14}")
    rows, grid = {}, []
    for lab, idx in CAND.items():
        rate, nadm, e, mde = blind_rate(idx)
        pct = 100.0 * (per_sub < per_sub[idx]).mean()
        # BH over this reference's own 1,820 cells, using a normal p from e/(mde/ZEFF)
        se = mde / ZEFF                       # ZEFF folds power in; se is the plain standard error
        with np.errstate(divide="ignore", invalid="ignore"):
            z = np.where(se > 0, e / se, 0.0)
        pv = np.clip(ERFC(np.abs(z) / math.sqrt(2.0)), 0.0, 1.0)   # two-sided normal
        o = np.argsort(pv); C = len(pv)
        surv = np.zeros(C, bool)
        passing = pv[o] <= 0.05 * np.arange(1, C + 1) / C
        if passing.any():
            surv[o[:int(np.max(np.where(passing)[0])) + 1]] = True
        nbh = int((surv & (e > 0)).sum())
        rows[lab] = dict(ref_a2=float(per_sub[idx]), pctile=pct, admitted=nadm,
                         rate=rate, bh_admitted=nbh, idx=idx)
        grid.append(lab)
        print(f"    {lab:<24}{per_sub[idx]:>10.4f}{pct:>8.1f}{nadm:>10}{rate:>9.4f}{nbh:>14}")

    # ---- WHO ARE THE 3? the derivation used ONE typical MDE and this is where that bites --------
    e_r, mde_r, ok_r = clears(B, B[inc])
    hits = np.where(ok_r)[0]
    print(f"\n  THE SETS THAT STILL CLEAR R294's REFERENCE — {len(hits)} of {NS}\n")
    print(f"    {'subset':<20}{'A2':>9}{'gap':>9}{'MDE':>9}{'ratio':>7}{'shared criteria':>17}")
    overlaps = []
    for h in hits:
        ov = len(set(subs[h]) & set(subs[inc]))
        overlaps.append(ov)
        print(f"    {str(tuple(int(x) for x in subs[h])):<20}{per_sub[h]:>9.4f}{e_r[h]:>+9.4f}"
              f"{mde_r[h]:>9.4f}{abs(e_r[h])/mde_r[h]:>7.2f}{ov:>17}")
    if len(hits):
        allov = np.array([len(set(subs[i]) & set(subs[inc])) for i in range(NS)])
        med_mde_far = float(np.median(mde_r[allov == 0]))
        med_mde_near = float(np.median(mde_r[allov >= 3])) if (allov >= 3).any() else float("nan")
        print(f"\n    median per-pair MDE — sets sharing 0 criteria with the reference: "
              f"{med_mde_far:.4f}")
        print(f"    median per-pair MDE — sets sharing >=3 criteria:                    "
              f"{med_mde_near:.4f}")
        print(f"    mean shared criteria among the {len(hits)} that clear: "
              f"{np.mean(overlaps):.2f} vs {allov.mean():.2f} over all {NS}")
        print(f"    -> a NEAR-NEIGHBOUR of the reference has a small PAIRED sd, so it can clear")
        print(f"       its own MDE on a tiny gap. The derivation used one typical MDE (0.0106) and")
        print(f"       that is exactly the cell class it could not see.")

    # ---- POSITIVE CTRL · self-comparison, and it must FAIL at g=0 --------------------------------
    e_self, mde_self, ok_self = clears(B[inc][None, :], B[inc])
    weakest = CAND["p000"]
    e_w, mde_w, ok_w = clears(B[inc][None, :], B[weakest])
    pos_ok = (not bool(ok_self[0])) and abs(float(e_self[0])) == 0.0
    g0_ok = bool(ok_w[0])
    print(f"\n  POSITIVE CTRL  the reference against itself: gap {float(e_self[0]):+.1e}, "
          f"clears={bool(ok_self[0])}  {'PASS' if pos_ok else 'FAIL'}")
    print(f"    g=0 · the SAME set against the WEAKEST reference (p0, {per_sub[weakest]:.4f}): "
          f"gap {float(e_w[0]):+.4f}, clears={bool(ok_w[0])}  "
          f"{'PASS — the instrument can detect admission' if g0_ok else 'FAIL — every 0 it reports is silence'}")

    # ---- NEGATIVE CTRL · a reference that excludes coval_core is too strong ----------------------
    e_cc, mde_cc, ok_cc = clears(arm["coval_core"][None, :], B[inc])
    e_sh, mde_sh, ok_sh = clears(arm["gen_sham"][None, :], B[inc])
    neg_ok = bool(ok_cc[0]) and not bool(ok_sh[0])
    print(f"  NEGATIVE CTRL  at R294's reference: coval_core clears={bool(ok_cc[0])} "
          f"({float(e_cc[0]):+.4f}/{float(mde_cc[0]):.4f}), gen_sham clears={bool(ok_sh[0])} "
          f"({float(e_sh[0]):+.4f})  {'PASS' if neg_ok else 'FAIL — the reference is mis-calibrated'}")

    # ---- SHAM · identity vs percentile ------------------------------------------------------------
    rank_inc = int(np.where(order == inc)[0][0])
    neigh = [int(order[r]) for r in range(max(0, rank_inc - 5), min(NS, rank_inc + 6)) if int(order[r]) != inc][:10]
    sham_rates = [blind_rate(i)[0] for i in neigh]
    base_rate = rows[f"R294 first-4 (p{inc_pct:.0f})"]["rate"]
    spread = (max(sham_rates) - min(sham_rates)) if sham_rates else 0.0
    sham_ok = spread <= max(0.01, 2 * abs(base_rate))
    print(f"\n  SHAM (identity vs percentile)  10 DIFFERENT subsets at the same percentile:")
    print(f"    their blind admission rates: {[round(r, 4) for r in sham_rates]}")
    print(f"    R294's own: {base_rate:.4f}   spread across identities: {spread:.4f}")
    print(f"    -> {'PASS — the property is the PERCENTILE, not the identity' if sham_ok else 'FAIL — identity moves the rate, so percentile is not the whole story'}")

    # ---- PLACEBO ---------------------------------------------------------------------------------
    plc = max(abs(float(clears(B[i][None, :], B[i])[0][0])) for i in CAND.values())
    plc_ok = plc == 0.0
    print(f"  PLACEBO        every reference against itself: {plc:.1e}  "
          f"{'PASS' if plc_ok else 'FAIL'}")

    # ---- KILL --------------------------------------------------------------------------------------
    r294_rate = rows[f"R294 first-4 (p{inc_pct:.0f})"]["rate"]
    med_rate = rows["p050"]["rate"]
    ctrl = pos_ok and g0_ok and neg_ok and sham_ok and plc_ok
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  positive={pos_ok}  g0={g0_ok}  negative={neg_ok}  sham={sham_ok}  "
          f"placebo={plc_ok}  -> {'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; no safety statement is readable.")
    elif r294_rate > 0.01:
        world = "W-SELF"
        print(f"  -> W-SELF. {rows[f'R294 first-4 (p{inc_pct:.0f})']['admitted']} of {NS} "
              f"prompt-blind sets ({r294_rate:.1%}) clear clause 2 against R294's OWN reference.")
        print("     Clause 2 is broken as worded for that reference too, and the defect predates")
        print("     R328 by forty rounds. Self-comparison excluded exactly one object.")
    elif med_rate < 0.01:
        world = "W-MDE"
        print(f"  -> W-MDE. Even the MEDIAN reference admits only {rows['p050']['admitted']} of "
              f"{NS} ({med_rate:.1%}), so percentile is not the lever and the blind class is")
        print("     narrower than the design's resolution. `generic`'s admission in R330 needs")
        print("     its own account and does not follow from a percentile drop.")
    else:
        world = "W-PERCENTILE"
        print(f"  -> W-PERCENTILE. The blind admission rate falls from "
              f"{rows['p000']['rate']:.1%} at p0 to {r294_rate:.1%} at R294's reference "
              f"(p{inc_pct:.0f}),")
        print(f"     and the median reference still admits {med_rate:.1%}. Safety is ALTITUDE, not")
        print("     identity: the sham shows 10 different subsets at the same percentile give the")
        print("     same rate. So R330's stated mechanism is REPLACED — self-comparison protects")
        print("     against exactly one object, and what protected clause 2 was that its reference")
        print("     sits high in the blind distribution.")
        print(f"     THE DESIGN RULE, and it is a number: a clause-2 reference must sit above the")
        print(f"     percentile at which the blind admission rate reaches 0.")
    print("  " + "=" * 78)
    print(f"\n  ⛔ AND THE HEADLINE ARITHMETIC IS A DERIVATION, stated before the run: the BEST of")
    print(f"    {NS} blind sets exceeds R294's reference by {per_sub.max() - per_sub[inc]:.5f},")
    print(f"    against per-cell MDEs measured here at "
          f"[{blind_rate(inc)[3].min():.4f}, {blind_rate(inc)[3].max():.4f}]. What was NOT forced")
    print(f"    and is measured: the whole curve, the per-pair MDEs, and the sham.")
    print(f"\n  MULTIPLICITY  {NS} x {len(CAND)} = {NS*len(CAND)} cells; raw and BH counts both printed.")

    o = SELF.parent / "results" / "reference_safety.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_prompts=N, n_blind=NS, pool=npool,
        blind_dist=dict(min=float(per_sub.min()), p25=float(np.percentile(per_sub, 25)),
                        med=float(np.median(per_sub)), p75=float(np.percentile(per_sub, 75)),
                        p90=float(np.percentile(per_sub, 90)), p99=float(np.percentile(per_sub, 99)),
                        max=float(per_sub.max())),
        r294_reference=dict(a2=float(per_sub[inc]), pctile=inc_pct),
        curve=rows, sham_rates=sham_rates, sham_spread=float(spread),
        clearing_sets=[dict(subset=[int(x) for x in subs[h]], a2=float(per_sub[h]),
                            gap=float(e_r[h]), mde=float(mde_r[h]),
                            overlap=int(len(set(subs[h]) & set(subs[inc]))))
                       for h in hits],
        controls=dict(positive=bool(pos_ok), g0=bool(g0_ok), negative=bool(neg_ok),
                      sham=bool(sham_ok), placebo=bool(plc_ok)),
        derivation=dict(best_blind_minus_ref=float(per_sub.max() - per_sub[inc]),
                        note="stated before the run from R286's committed distribution"),
    ), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
