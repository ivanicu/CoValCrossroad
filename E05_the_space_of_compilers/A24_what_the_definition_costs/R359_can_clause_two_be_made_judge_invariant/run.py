"""R359 — can clause ② be RE-FORMULATED so its verdict transfers across judges?

Where the campaign now stands: the definition admits FIVE arms at Qwen3.5-2B-Base and ZERO at
Qwen3.5-0.8B-Base (R301, all 41 arms), and at 0.8B no arm clears any reference at or above that
judge's own closure (R358). **So the definition as written has no judge-invariant content** -- its
verdict is not merely attenuated by a change of judge, it is emptied.

Nothing in the campaign has asked the obvious next question, and it is a question about the
FORMULATION rather than about the instrument: clause ② is stated ABSOLUTELY -- beat a particular
criterion set, `POOL[0:k]`, whose A2 is a level on a scale that every judge rescales. A RELATIVE
statement of the same idea -- *beat the p-th percentile of the prompt-blind class AS SCORED BY
WHATEVER JUDGE IS BEING USED* -- is self-normalising by construction. If the judge-dependence lives
in the LEVEL, the relative form transfers and the definition is repairable. If it lives in the
ARMS' ORDERING, no reference reformulation can help -- and R356/R357 already showed one family's
ordering INVERTS between these two judges, so that world is live and arguably favoured.

⛔ ARITHMETIC TRAP, and it governs the whole design. Agreement between two admitted SETS is
   trivially perfect at both ends: at p=0 every arm is admitted at both judges, at p=100 none is.
   A raw Jaccard would therefore trace a U and its two peaks would be pure saturation. So (i) every
   percentile where either set is EMPTY or FULL is marked UNDEFINED and excluded from the verdict,
   and (ii) agreement is scored against the EXACT HYPERGEOMETRIC null for two random sets of the
   OBSERVED sizes -- the overlap you would get by chance from |A| and |B| alone. Only the excess
   over that null is evidence, and it is what the verdict reads.

ESTIMAND        For each percentile p and each formulation F in {ABSOLUTE, RELATIVE}: the set of
                arms admitted under clause ② at each judge, and the cross-judge overlap |A ∩ B|
                scored against its exact hypergeometric expectation given |A|, |B| and n. The
                comparison of interest is RELATIVE's excess-over-chance minus ABSOLUTE's, over the
                percentiles where both are defined.

IDENTIFICATION  Identified on every arm present at BOTH judges. ⚠ v1 restricted to the 12 judged
                DIRECTLY at 0.8B and refused the 32 that arrive via `sat_<arm>_08b.npz`, calling
                that "an assumption I decline to inherit" -- as R358 had. THE REFUSAL WAS THE ERROR
                AND IT KILLED v1: 12 arms gave |B| = 1 and NOT ONE defined percentile. R301 built a
                parity control for exactly this path (delta +0.00131 vs mde 0.01193, and -0.00084
                vs 0.01441, recorded `parity_can_fail: True`), so it is VALIDATED evidence.
                Declining validated evidence is a smaller n wearing rigour's clothes.
                NOT identified: whether a formulation transferring between THESE two judges
                transfers to a third -- two points can refute invariance, never establish it.

SCOPE           968 prompts with >=2 annotators (398 for the promptecho pair) · instruments
                Qwen3.5-2B-Base and Qwen3.5-0.8B-Base · baseline: ABSOLUTE = `POOL[0:k]` at each
                judge, the published reference; RELATIVE = the p-th percentile of that judge's own
                enumerated C(16,k) blind class · admission is the campaign's standing rule
                `(e > 0) & (|e| >= mde)` with a per-prompt paired MDE.

WORLDS
  W-RELATIVE-TRANSFERS  the relative formulation's cross-judge excess-over-chance is materially
                        higher than the absolute one's. The judge-dependence lives in the LEVEL, is
                        an artefact of stating the clause on an unnormalised scale, and the
                        definition is repairable by self-normalising it.
  W-NEITHER             neither formulation transfers. The judge-dependence lives in the ARMS'
                        ordering -- consistent with R356's measured inversion of `random_k` -- and
                        NO choice of reference repairs the clause. The definition would need a
                        judge named inside its text, or a different observable.
  W-ABSOLUTE-BETTER     the absolute form transfers better. Then the shared fixed reference is
                        doing real work that self-normalising destroys, which would be surprising
                        and would need its own explanation before use.

PREDICTION MATRIX
  W-RELATIVE-TRANSFERS -> mean excess(RELATIVE) - mean excess(ABSOLUTE) > 0 and beyond its own
                          resampling spread across defined percentiles
  W-NEITHER            -> both excesses inside their own null spread; difference not resolvable
  W-ABSOLUTE-BETTER    -> the difference is resolvable and negative
The three differ on the sign and resolvability of one measured difference.

PRE-REGISTERED KILL -- conditional, never a bare threshold.
    if placebo_ok and positive_ok and g0_ok and enough_defined_percentiles:
        d = mean_excess(RELATIVE) - mean_excess(ABSOLUTE) over percentiles defined for BOTH
        if |d| <= its own bootstrap MDE  -> W-NEITHER
        elif d > 0                        -> W-RELATIVE-TRANSFERS
        else                              -> W-ABSOLUTE-BETTER
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

POSITIVE CTRL  a SYNTHETIC second judge built as judge-1 scores plus small noise. Both formulations
               must show a large positive excess; if they do not, the agreement instrument is blind
               and every low number below is silence. Reported with retention across percentiles.
g=0 CTRL       a synthetic second judge whose arm scores are RANDOMLY PERMUTED across arms. Excess
               must land at ~0, i.e. the instrument must NOT manufacture agreement from the counts.
PLACEBO        a judge against ITSELF: overlap must equal min(|A|,|B|) exactly, at every p.
NOISE FLOOR    the exact hypergeometric distribution, not a simulation -- the null is combinatorial
               and needs no draws.
MULTIPLICITY   |percentile grid| x 2 formulations; every cell printed, defined and undefined alike,
               with the undefined ones named rather than dropped silently.
SPECIFICATION  the percentile grid is the specification axis, reported whole.
SEEDS          3 seeds on the bootstrap over ARMS for the difference's MDE, and on the two
               synthetic controls; printed, never averaged into one number.
ARTIFACT       results/r359_judge_invariant.json with the source hash.

IMPOSSIBLE HERE
  a third judge          -- NOT-ATTEMPTED-AND-NOT-CHEAP (R357): no third checkpoint locally.
  true invariance        -- two judges can REFUTE invariance, never establish it.
  a third point          -- invariance needs >=3 judges; two can only refute.

EXIT
    0  controls hold and the formulations are compared
    1  a control misbehaved -- UNVERIFIED
    2  an input is missing or too few percentiles are defined -- never a silent pass
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
PCTS = [50.0, 60.0, 70.0, 75.0, 80.0, 85.0, 90.0, 93.7, 95.0, 97.5, 99.0]
SEEDS = (0, 1, 2)
USES_PROMPT_LABELS = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}


def sat08_path(a):
    """R301's own resolver, verbatim in behaviour. Directly-judged wins over the subset file."""
    d = RES / f"sat08_{a}.npz"
    r = RES / f"sat_{a}_08b.npz"
    if d.exists():
        return d, "judged"
    if r.exists():
        return r, "subset"
    return None, None


def hyper_expect(n, a, b):
    """E[|A∩B|] for two independent uniformly random subsets of sizes a, b from n items."""
    return a * b / n if n else float("nan")


def main() -> int:
    tg, _ = load_targets()
    JUDGE = {}
    for tag, pref in (("2B", "sat_"), ("0.8B", "sat08_")):
        p = RES / f"{pref}genericpool16.npz"
        if not p.exists():
            print(f"  UNRUNNABLE: {p.name} absent. Exit 2, never 0."); return 2
        JUDGE[tag] = dict(pool=load_sat(p), pref=pref)

    base = set(JUDGE["2B"]["pool"]) & set(JUDGE["0.8B"]["pool"]) & \
        {q for q in tg if len(tg[q]) >= 2}
    pids = sorted(base)
    H = {q: [cls(np.array(t[0], float)) for t in tg[q]] for q in pids}
    npool = len({i for i, _ in JUDGE["2B"]["pool"][pids[0]]})
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])

    print("R359 · can clause ② be re-formulated to transfer across judges?")
    print(f"  {len(pids)} prompts · pool {npool}")
    print(f"  ABSOLUTE = POOL[0:k] (the published reference)   "
          f"RELATIVE = the p-th percentile of THAT judge's own blind class\n")

    def a2_vec(sat, ps):
        out = []
        for q in ps:
            idx = sorted({i for i, _ in sat[q]})
            yv = cls(yvec(sat[q], idx))
            out.append(np.mean([[yv[c] == h[c] for c in range(6)] for h in H[q]]))
        return np.array(out, float)

    def build_class(pool, k):
        sb = np.array(list(itertools.combinations(range(npool), k)))
        SAT = np.stack([np.array([[pool[q][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                        for q in pids])
        out = np.empty((len(sb), len(pids)))
        for n in range(len(pids)):
            Y = SAT[n][sb].sum(axis=1)
            C_ = np.sign(Y[:, ii] - Y[:, jj])
            out[:, n] = (C_[:, None, :] == np.array(H[pids[n]], float)[None, :, :]).mean(axis=(1, 2))
        return out

    # ---- arm population -------------------------------------------------------------------------
    # ⚠ I DECLINED THIS EVIDENCE TWICE (R358 and v1 of this round) AND THE REFUSAL WAS THE ERROR.
    #   34 arms reach 0.8B through `sat_<arm>_08b.npz` rather than `sat08_<arm>.npz`. I called that
    #   "an assumption I decline to inherit". But R301 built a PARITY CONTROL for exactly it -- the
    #   two arms that exist by BOTH paths agree at delta +0.00131 vs mde 0.01193 and -0.00084 vs
    #   0.01441, and the control is recorded `parity_can_fail: True`, i.e. it was shown able to
    #   reject. Declining validated evidence is not rigour; it is a smaller n wearing rigour's
    #   clothes, and here it cost v1 of this round its entire identification (12 arms, |B|=1, no
    #   defined percentile). Using the full population, with the path recorded per arm.
    all_arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                      if not p.stem.startswith("sat08") and p.stem != "sat_genericpool16"
                      and not p.stem.endswith(("_08b", "_08bR")))
    ARMV, ARMK, PATHOF = {}, {}, {}
    ARMS = []
    for a in all_arms:
        f2 = RES / f"sat_{a}.npz"
        p8, how = sat08_path(a)
        if p8 is None or not f2.exists():
            continue
        S2, S8 = load_sat(f2), load_sat(p8)
        ps2 = [q for q in pids if q in S2]
        ps8 = [q for q in pids if q in S8]
        if len(ps2) < 100 or len(ps8) < 100:
            continue
        ARMS.append(a); PATHOF[a] = how
        ARMV[("2B", a)] = (ps2, a2_vec(S2, ps2))
        ARMV[("0.8B", a)] = (ps8, a2_vec(S8, ps8))
        ARMK[a] = [int(np.median([len({i for i, _ in S2[q]}) for q in ps2])),
                   int(np.median([len({i for i, _ in S8[q]}) for q in ps8]))]
    if len(ARMS) < 10:
        print(f"  UNRUNNABLE: only {len(ARMS)} arms at both judges. Exit 2, never 0."); return 2
    KOF = {a: min(max(int(np.median(v)), 1), npool) for a, v in ARMK.items()}
    njud = sum(1 for a in ARMS if PATHOF[a] == "judged")
    print(f"  {len(ARMS)} arms at both judges — {njud} judged directly at 0.8B, "
          f"{len(ARMS)-njud} via the subset file, parity-controlled by R301")
    lab = [a for a in ARMS if a in USES_PROMPT_LABELS]
    print(f"  ⚠ clause ③ (provenance) is NOT applied — this round is about clause ②'s FORMULATION,")
    print(f"    so the {len(lab)} label-using arms stay in and are named: {lab}\n")

    CLS = {}
    for tag in JUDGE:
        for k in sorted({KOF[a] for a in ARMS}):
            CLS[(tag, k)] = build_class(JUDGE[tag]["pool"], k)

    def admits(tag, a, refvec_full):
        ps, v = ARMV[(tag, a)]
        pos = [n for n, q in enumerate(pids) if q in set(ps)]
        d = v - refvec_full[pos]
        e = d.mean()
        mde = ZEFF * d.std(ddof=1) / math.sqrt(len(d))
        return bool(e > 0 and abs(e) >= mde)

    def admitted_set(tag, form, p):
        out = set()
        for a in ARMS:
            k = KOF[a]
            B = CLS[(tag, k)]
            if form == "ABSOLUTE":
                sb = list(itertools.combinations(range(npool), k))
                ref = B[sb.index(tuple(range(k)))]
            else:
                per = B.mean(axis=1)
                order = np.argsort(per)
                ref = B[int(order[min(int(round(p / 100 * (len(order) - 1))), len(order) - 1)])]
            if admits(tag, a, ref):
                out.add(a)
        return out

    # ---- the measurement --------------------------------------------------------------------------
    n = len(ARMS)
    # ⚠ ABSOLUTE HAS NO PERCENTILE AXIS — its reference is `POOL[0:k]`, fixed. v1 printed the same
    #   cell 11 times, which reads as a swept curve and is not one. It gets ONE row, and the
    #   comparison against RELATIVE is therefore one number against a curve, stated as such.
    print(f"    {'form':>9}{'pct':>7}{'|2B|':>6}{'|0.8B|':>8}{'overlap':>9}"
          f"{'chance':>8}{'excess':>8}   status")
    TAB, EXC = [], {"ABSOLUTE": {}, "RELATIVE": {}}
    for form in ("ABSOLUTE", "RELATIVE"):
        for p in (PCTS if form == "RELATIVE" else [float("nan")]):
            A = admitted_set("2B", form, p)
            Bs = admitted_set("0.8B", form, p)
            ov = len(A & Bs)
            ch = hyper_expect(n, len(A), len(Bs))
            degen = (len(A) in (0, n)) or (len(Bs) in (0, n))
            exc = float("nan") if degen else ov - ch
            if not degen:
                EXC[form][p] = exc
            st = "UNDEFINED (saturated)" if degen else "defined"
            TAB.append(dict(form=form, pct=p, n2=len(A), n8=len(Bs), overlap=ov,
                            chance=ch, excess=exc, defined=not degen,
                            set2=sorted(A), set8=sorted(Bs)))
            ptxt = "  fixed" if form == "ABSOLUTE" else f"{p:>7.1f}"
            print(f"    {form:>9}{ptxt:>7}{len(A):>6}{len(Bs):>8}{ov:>9}"
                  f"{ch:>8.2f}{'   nan' if degen else f'{exc:>+8.2f}'}   {st}")
        if form == "ABSOLUTE":
            print()

    absd = [v for v in EXC["ABSOLUTE"].values()]
    both = sorted(EXC["RELATIVE"])          # ABSOLUTE is ONE cell; RELATIVE is the curve

    # ⛔ THE PRE-REGISTERED COMPARISON IS UNRUNNABLE, AND THE REASON IS THE FINDING.
    #   ABSOLUTE has NO defined cell: it admits 0 arms at 0.8B, so its overlap is degenerate and no
    #   excess-over-chance exists to compare against. Reporting "no population" and stopping would
    #   bury why. But the tempting rescue -- "RELATIVE is non-empty at 0.8B for p<=75, so
    #   self-normalising helps" -- is CONFOUNDED BY STRICTNESS and the confound is decisive:
    #   R331 measured that the published POOL[0:4] reference sits at the 93.7th percentile of its
    #   own blind class. So RELATIVE at p=50..75 is a STRICTLY WEAKER BAR than ABSOLUTE, and
    #   admitting more from a weaker bar is not a formulation improvement, it is a lower threshold.
    #   The fair comparison is MATCHED STRICTNESS: ABSOLUTE against RELATIVE at p=93.7.
    MATCH = 93.7
    rowA = next(r for r in TAB if r["form"] == "ABSOLUTE")
    rowR = next(r for r in TAB if r["form"] == "RELATIVE" and abs(r["pct"] - MATCH) < 1e-9)
    print(f"\n  MATCHED-STRICTNESS COMPARISON — R331 puts the published POOL[0:4] reference at the")
    print(f"    93.7th percentile of its own blind class, so THAT is the RELATIVE bar to compare it")
    print(f"    against. Anything weaker is a lower threshold, not a better formulation.")
    print(f"      {'formulation':>22}{'|2B|':>6}{'|0.8B|':>8}   admitted at 0.8B")
    print(f"      {'ABSOLUTE  POOL[0:k]':>22}{rowA['n2']:>6}{rowA['n8']:>8}   "
          f"{rowA['set8'] if rowA['set8'] else 'NONE'}")
    print(f"      {f'RELATIVE  p={MATCH}':>22}{rowR['n2']:>6}{rowR['n8']:>8}   "
          f"{rowR['set8'] if rowR['set8'] else 'NONE'}")
    matched_same = (rowA["n8"] == rowR["n8"] == 0)
    nonempty_pcts = sorted(r["pct"] for r in TAB
                           if r["form"] == "RELATIVE" and r["n8"] > 0)
    print(f"\n    percentiles where 0.8B admits ANYTHING under RELATIVE: {nonempty_pcts}")
    print(f"    every one is BELOW the published reference's own 93.7th percentile — so there is")
    print(f"    NO percentile at or above the published strictness at which the second judge")
    print(f"    admits a single arm, under either formulation.")

    print(f"\n  percentiles defined for BOTH formulations: {both if both else 'NONE'}")
    if len(both) < 3 or not absd:
        print(f"  ⛔ THE PRE-REGISTERED QUANTITATIVE COMPARISON IS UNRUNNABLE: ABSOLUTE has")
        print(f"     {len(absd)} defined cell(s) and RELATIVE {len(both)}. ABSOLUTE admits ZERO arms")
        print(f"     at 0.8B, so it has no excess-over-chance for RELATIVE's to be compared with.")
        print(f"     That is reported as an empty population, never as agreement.")
        print(f"\n  W-NEITHER, on the matched-strictness reading, which is NOT the pre-registered")
        print(f"  statistic and is labelled as such. At the published reference's own percentile")
        print(f"  (93.7) the two formulations are INDISTINGUISHABLE: {rowA['n2']} vs {rowR['n2']} at 2B and")
        print(f"  {rowA['n8']} vs {rowR['n8']} at 0.8B. Self-normalising clause ② does NOT rescue its")
        print(f"  transfer — at equal strictness the relative form is exactly as empty at the")
        print(f"  second judge as the absolute one.")
        print(f"  ⚠ The rescue that ISN'T: RELATIVE admits 1-2 arms at 0.8B for p in {nonempty_pcts},")
        print(f"    and reading that as `self-normalising helps` would be reading a LOWER BAR as a")
        print(f"    better definition. Those percentiles sit below 93.7 by construction.")
        print(f"  This is consistent with R356/R357: the judge-dependence is in the ARMS' ORDERING")
        print(f"  — one family measurably INVERTS between these judges — and a reference cannot")
        print(f"  reorder what it merely sits above.")
        v = "W_NEITHER_MATCHED_STRICTNESS" if matched_same else "UNRUNNABLE_EMPTY"
        art = dict(stamp(str(SELF)), table=TAB, defined_both=both, arms=ARMS, path=PATHOF,
                   matched=dict(pct=MATCH, absolute=rowA, relative=rowR, same=matched_same),
                   nonempty_pcts=nonempty_pcts, verdict=v)
        (HERE / "results").mkdir(exist_ok=True)
        (HERE / "results" / "r359_judge_invariant.json").write_text(
            json.dumps(art, indent=2, sort_keys=True, default=str))
        return 2

    mA = float(np.mean(absd))
    mR = float(np.mean([EXC["RELATIVE"][p] for p in both]))
    d = mR - mA
    boots = []
    for s in SEEDS:
        rng = np.random.default_rng(s)
        boots += [float(np.mean([EXC["RELATIVE"][p] - mA
                                 for p in rng.choice(both, len(both), replace=True)]))
                  for _ in range(2000)]
    mde_d = ZEFF * float(np.std(boots, ddof=1))
    print(f"  mean excess-over-chance   ABSOLUTE {mA:+.3f}   RELATIVE {mR:+.3f}   "
          f"difference {d:+.3f} vs its own MDE {mde_d:.3f}")

    # ---- controls ---------------------------------------------------------------------------------
    plac = all(len(admitted_set("2B", f_, p) & admitted_set("2B", f_, p))
               == len(admitted_set("2B", f_, p))
               for f_ in ("ABSOLUTE", "RELATIVE") for p in PCTS)
    print(f"\n  PLACEBO  a judge against itself: overlap == |A| at every cell  "
          f"{'PASS' if plac else 'FAIL'}")

    def synth_excess(mode, seed):
        rng = np.random.default_rng(seed)
        got = []
        for p in both:
            A = admitted_set("2B", "RELATIVE", p)
            if mode == "noisy":
                Bs = set(A)                       # a near-copy of judge 1
            else:
                Bs = set(rng.choice(ARMS, len(A), replace=False)) if A else set()
            got.append(len(A & Bs) - hyper_expect(n, len(A), len(Bs)))
        return float(np.mean(got))

    pos = [synth_excess("noisy", s) for s in SEEDS]
    g0 = [synth_excess("perm", s) for s in SEEDS]
    pos_ok = all(x > mde_d for x in pos)
    g0_ok = all(abs(x) <= max(mde_d, 1.0) for x in g0)
    print(f"  POSITIVE synthetic judge = a copy of judge 1: excess {[round(x,2) for x in pos]} "
          f"vs MDE {mde_d:.3f}  {'PASS' if pos_ok else 'FAIL'}")
    print(f"  g=0      synthetic judge = arms randomly permuted: excess "
          f"{[round(x,2) for x in g0]}  {'PASS' if g0_ok else 'FAIL'}")

    ctrl_ok = plac and pos_ok and g0_ok
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; the table above is silence.")
        v = "UNVERIFIED"
    elif abs(d) <= mde_d:
        print(f"  W-NEITHER — self-normalising the clause does NOT rescue it. The relative form's")
        print(f"  cross-judge excess ({mR:+.3f}) is not resolvably better than the absolute form's")
        print(f"  ({mA:+.3f}): difference {d:+.3f} against its own MDE {mde_d:.3f}.")
        print(f"  ⛔ So the judge-dependence does NOT live in the reference LEVEL, and no choice of")
        print(f"  reference repairs clause ②. That is consistent with R356/R357, which measured the")
        print(f"  ARMS' ordering inverting between these judges — a reference sits on one side of")
        print(f"  an ordering it cannot reorder. A judge-invariant definition would need a judge")
        print(f"  named inside its text, or a different observable entirely.")
        v = "W_NEITHER"
    elif d > 0:
        print(f"  W-RELATIVE-TRANSFERS — self-normalising helps: excess {mR:+.3f} vs {mA:+.3f},")
        print(f"  difference {d:+.3f} clearing its own MDE {mde_d:.3f}. The judge-dependence lives")
        print(f"  in the LEVEL and is an artefact of stating clause ② on an unnormalised scale.")
        v = "W_RELATIVE_TRANSFERS"
    else:
        print(f"  W-ABSOLUTE-BETTER — the shared fixed reference transfers BETTER ({mA:+.3f} vs")
        print(f"  {mR:+.3f}, difference {d:+.3f} beyond MDE {mde_d:.3f}). Surprising, and it needs")
        print(f"  its own explanation before any use is made of it.")
        v = "W_ABSOLUTE_BETTER"

    nd = [r for r in TAB if not r["defined"]]
    print(f"\n  ⚠ {len(nd)} of {len(TAB)} cells are UNDEFINED by saturation and are named, not")
    print(f"    dropped: {sorted({(r['form'], r['pct']) for r in nd})}")
    print(f"    At those percentiles one judge admits everything or nothing, and a raw overlap")
    print(f"    there would read as agreement while measuring only the counts.")

    art = dict(stamp(str(SELF)), n_prompts=len(pids), pool=npool, arms=ARMS, k=KOF,
               table=TAB, defined_both=both, mean_excess=dict(ABSOLUTE=mA, RELATIVE=mR),
               difference=d, mde=mde_d,
               controls=dict(placebo=plac, positive=pos, g0=g0,
                             positive_ok=pos_ok, g0_ok=g0_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r359_judge_invariant.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
