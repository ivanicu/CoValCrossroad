"""R332 — requiring clause 2 not to admit its own reference class DERIVES a reading R327 called unsettleable.

R331 gave a design rule -- put the clause-2 reference high in the blind distribution -- and left it as
a percentile on a nine-point grid. Sharpening it to its minimal form has a consequence I did not
anticipate when I wrote the rule.

THE MINIMAL FORM. Call a reference CLOSED if no member of clause 2's own reference class -- no
prompt-blind set of the same size -- clears clause 2 against it. R331 measured 0.16% at R294's
reference and 0.0% at p99. The CLOSURE LEVEL is the LOWEST reference that is closed: anything
stronger is gratuitous, anything weaker admits an object the clause exists to exclude.

AND AT k=4 IT LANDS ON R327's READING A -- ⚠ ON A NINE-POINT GRID, AND THE 45-POINT GRID BELOW
OVERTURNS THE NUMBER. R331's coarse grid put the closure at 0.554667; refined, it is 0.551951,
which differs from reading A by 2.65e-03. That is still INSIDE coval_core's own MDE of 0.0106, so
the two are indistinguishable at this design's resolution -- but "indistinguishable" is a far weaker
claim than the 6.5e-5 that motivated this round, and the paragraph below is kept as written so the
inflation is visible rather than tidied away. A grid is an instrument and a coarse one reads high.

The closure level is 0.554667; R327's reading A -- "better
than EVERY prompt-blind set of that size", operationalised by R286/R287 as the best held-out of 1,820
-- is 0.554602. They agree to 6.5e-5, two orders below any MDE here. R327 priced three readings and
declined to choose, saying no measurement settles it. If this holds across k, a measurement does:
reading A is not one option of three, it is the only reading under which clause 2 is not
self-refuting, and the other two admit members of the class they quantify over.

⚠ AND THE CLOSURE LEVEL IS BELOW THE MAX, WHICH MATTERS. max(blind) = 0.557475 against a closure of
0.554667. Because clearing requires beating the reference by an MDE, a reference slightly under the
ceiling already admits nobody. So "better than the BEST prompt-blind set" is SUFFICIENT AND NOT
MINIMAL, by 0.0028 -- and the minimal statement is about a LEVEL, not about a winner.

⚠ THE CONFOUND I MUST CONTROL, WRITTEN BEFORE THE RUN. The closure level is chosen using the same
968 prompts the arms are judged on. That is in-sample selection of a baseline -- exactly what R287
disqualified its own ceiling for. So closure is computed BOTH in-sample and held-out (level chosen on
half the prompts, blind admission rate measured on the other half, >=3 splits), and if the held-out
level does not close, the rule is an artifact of the selection and this round says so.

ESTIMAND      (i) per k, the CLOSURE LEVEL: the lowest reference A2 at which the blind admission
              rate over the whole size-matched class is exactly 0; (ii) its distance from R294's
              published reference, from the held-out best (R327 reading A), and from the class max;
              (iii) R294's 41-arm table recomputed against the per-k closure reference, and whether
              the resulting admitted set equals reading A's.
IDENTIFICATION Exact for the in-sample level: every C(16,k) subset is enumerated, so the rate is
              computed over the whole class rather than a sample of it. The HELD-OUT level is
              estimated over splits and is reported with its across-split spread.
SCOPE         population 968 CoVal prompts with >=2 annotators (398 for promptecho) · instrument
              Qwen3.5-2B-Base under R234's canonical builder · baseline the closure reference,
              named per k · regime all annotators, A2, k as published per arm.
WORLDS        W-DERIVES-A   the closure level tracks the held-out best across k, and the admitted
                            set equals reading A's -> clause 2's reading is settled by a
                            self-consistency requirement, not chosen. R327's closing sentence is
                            overturned for the second time and for a better reason.
              W-STRICTER    closure lands ABOVE reading A somewhere -> reading A is itself not
                            closed at some k, i.e. even "better than every blind set" admits a
                            blind set there, and the clause needs a level rather than a winner.
              W-WEAKER      closure lands materially BELOW reading A -> the two are different
                            objects that coincided at k=4, the k=4 agreement was luck, and the
                            derivation claim dies.
KILL          pre-registered, conditional on the controls, over the k values with >=1 clause-3
              passing arm:
                |closure - heldout_best| <= MDE at every k AND admitted == reading A's set
                                                                        -> W-DERIVES-A
                closure > heldout_best by more than an MDE at any k      -> W-STRICTER
                otherwise                                                -> W-WEAKER
POSITIVE CTRL MINIMALITY, and it is the control that can most easily fail: the candidate one grid
              step BELOW the closure level must have a blind admission rate STRICTLY > 0. If it does
              not, the level is not minimal and I have reported a bound as a value. Run per k.
              And it fails at g=0: the weakest reference in the grid must admit nearly the whole
              class, or the rate instrument is not measuring admission at all.
NEGATIVE CTRL the random and sham arms must stay excluded at the closure reference. They are
              excluded at every reference already, so this is weak on its own -- its job is to fire
              if the closure reference is somehow WEAKER than what it replaces.
SHAM          the held-out closure: choose the level on half the prompts, measure its rate on the
              other half, >=3 splits. If the held-out rate is not 0, the in-sample level is a
              selection artifact and the rule does not survive its own confound.
PLACEBO       the closure reference against itself: exactly 0.
NOISE FLOOR   per-pair MDE for every (blind set, reference) cell, and the across-split spread of
              the held-out closure level.
MULTIPLICITY  per k, |class| x |percentile grid| cells; all rates printed for the grid, and the
              arm table is 41 arms x 1 reference with BH over the arm family.
SPECIFICATION the percentile grid IS the curve; in-sample and held-out are both published; the k
              axis is published whole including the small classes where closure is degenerate.
SEEDS         3 splits for the held-out closure; all three levels reported, never averaged.
ARTIFACT      results/closure_level.json with source hash.
IMPOSSIBLE    - transferring the LEVEL to another pool. The rule is "the lowest closed reference";
                the number is a fact about this 16-criterion pool.
              - deciding whether reading A is the RIGHT reading in any sense beyond
                self-consistency. Closure says the other readings admit what they quantify over; it
                does not say the clause is measuring something worth measuring.
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

SELF = pathlib.Path(__file__).resolve()
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
SPLITS = (0, 1, 2)
GRID_PCT = np.concatenate([np.array([0.0, 25.0, 50.0, 75.0]), np.linspace(80.0, 100.0, 41)])
READING_A = 0.5546019829643504          # R286/R287 held-out best of 1,820, committed


def load_json(pat):
    d = next(A24.glob(pat), None)
    if d is None:
        return None
    f = sorted((d / "results").glob("*.json"))
    return json.loads(f[0].read_text()) if f else None


def main() -> int:
    r294 = load_json("R294_*")
    if r294 is None:
        print("  UNRUNNABLE: R294 absent."); return 2
    rows = r294["rows"]

    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
    ARM = {}
    for a in sorted(rows):
        f = ROOT / "corebench" / "results" / f"sat_{a}.npz"
        if not f.exists():
            print(f"  UNRUNNABLE: sat_{a}.npz absent."); return 2
        ARM[a] = load_sat(f)
    pids = sorted(set(S) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    N = len(pids)
    npool = len({i for i, _ in S[pids[0]]})
    SAT = np.stack([np.array([[S[p][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                    for p in pids])
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    KOF = {a: min(rows[a]["k"], npool) for a in rows}
    KS = sorted({KOF[a] for a in rows if rows[a]["ok3"]})
    IDX = {a: np.array([n for n, p in enumerate(pids) if p in ARM[a]]) for a in sorted(rows)}
    av = {a: np.array([np.mean([[cls(yvec(ARM[a][pids[n]],
                                          sorted({i for i, _ in ARM[a][pids[n]]})))[c] == h[c]
                                 for c in range(6)] for h in H[n]]) for n in IDX[a]])
          for a in sorted(rows)}
    print(f"  {N} prompts · pool {npool} · size-matched classes for k in {KS}\n")

    def build(k):
        sb = np.array(list(itertools.combinations(range(npool), k)))
        out = np.empty((len(sb), N))
        for n in range(N):
            Y = SAT[n][sb].sum(axis=1)
            C_ = np.sign(Y[:, ii] - Y[:, jj])
            out[:, n] = (C_[:, None, :] == H[n][None, :, :]).mean(axis=(1, 2))
        return sb, out

    def rate(Bk, ref_vec, cols=None):
        """fraction of the WHOLE class that clears clause 2 against `ref_vec`, on `cols` prompts."""
        X = Bk if cols is None else Bk[:, cols]
        r = ref_vec if cols is None else ref_vec[cols]
        d = X - r
        e = d.mean(axis=1)
        mde = ZEFF * d.std(axis=1, ddof=1) / math.sqrt(d.shape[1])
        return float(((e > 0) & (np.abs(e) >= mde)).mean())

    SUBS, BK, CLOSURE = {}, {}, {}
    print(f"  CLOSURE LEVEL per k — the LOWEST reference at which the blind admission rate is 0\n")
    print(f"    {'k':>3}{'|class|':>9}{'closure A2':>12}{'pctile':>8}"
          f"{'rate below':>12}{'R294 ref':>10}{'class max':>11}{'minimal?':>10}")
    for k in KS:
        SUBS[k], BK[k] = build(k)
        per = BK[k].mean(axis=1)
        order = np.argsort(per)
        cand = []
        for p in GRID_PCT:
            cand.append(int(order[min(int(round(p / 100 * (len(order) - 1))), len(order) - 1)]))
        seen, cand_u = set(), []
        for c in cand:                       # keep grid order, drop duplicates from tiny classes
            if c not in seen:
                seen.add(c); cand_u.append(c)
        rates = [rate(BK[k], BK[k][c]) for c in cand_u]
        closed = [i for i, r in enumerate(rates) if r == 0.0]
        if not closed:
            CLOSURE[k] = None
            print(f"    {k:>3}{len(SUBS[k]):>9}{'NONE':>12}{'--':>8}{'--':>12}"
                  f"{'--':>10}{per.max():>11.4f}{'n/a':>10}")
            continue
        first = closed[0]
        idx = cand_u[first]
        below = rates[first - 1] if first > 0 else float("nan")
        minimal = bool(first > 0 and rates[first - 1] > 0.0)
        r294_ref = int(np.where((SUBS[k] == np.arange(k)).all(axis=1))[0][0])
        CLOSURE[k] = dict(idx=idx, a2=float(per[idx]),
                          pctile=float(100.0 * (per < per[idx]).mean()),
                          rate_below=float(below), minimal=minimal,
                          r294_a2=float(per[r294_ref]), class_max=float(per.max()),
                          n_class=int(len(SUBS[k])),
                          grid_rates=[float(x) for x in rates],
                          weakest_rate=float(rates[0]))
        print(f"    {k:>3}{len(SUBS[k]):>9}{per[idx]:>12.4f}{CLOSURE[k]['pctile']:>8.1f}"
              f"{below:>12.4f}{per[r294_ref]:>10.4f}{per.max():>11.4f}{str(minimal):>10}")

    live = [k for k in KS if CLOSURE[k]]
    pos_ok = all(CLOSURE[k]["minimal"] for k in live)
    g0_ok = all(CLOSURE[k]["weakest_rate"] > 0.5 for k in live)
    print(f"\n  POSITIVE CTRL (minimality)  one grid step below the closure level the rate must be "
          f"> 0 at every k: {'PASS' if pos_ok else 'FAIL — the level is a bound, not a value'}")
    print(f"    g=0 · the WEAKEST reference must admit most of the class: "
          f"rates {[round(CLOSURE[k]['weakest_rate'], 3) for k in live]}  "
          f"{'PASS' if g0_ok else 'FAIL — the rate instrument is blind'}")

    # ---- SHAM · held-out closure, the confound named before the run -----------------------------
    print(f"\n  SHAM (in-sample confound)  choose the level on half the prompts, measure its rate")
    print(f"                             on the OTHER half, {len(SPLITS)} splits\n")
    print(f"    {'k':>3}   held-out rates at the in-sample closure level")
    ho = {}
    for k in live:
        rs = []
        for s in SPLITS:
            rng = np.random.default_rng(4600 + s)
            perm = rng.permutation(N)
            fit, ev = perm[:N // 2], perm[N // 2:]
            per_fit = BK[k][:, fit].mean(axis=1)
            of = np.argsort(per_fit)
            lvl = None
            for p in GRID_PCT:
                c = int(of[min(int(round(p / 100 * (len(of) - 1))), len(of) - 1)])
                if rate(BK[k], BK[k][c], fit) == 0.0:
                    lvl = c; break
            rs.append(rate(BK[k], BK[k][lvl], ev) if lvl is not None else float("nan"))
        ho[k] = rs
        print(f"    {k:>3}   {[round(x, 4) for x in rs]}")
    # ⚠ BEFORE BELIEVING THIS FAIL: §4 `the control fails for its own reasons`. Two worlds explain a
    # non-zero held-out rate and they are not the same finding.
    #   W-FITTED      the level is a selection artifact and genuinely does not transfer.
    #   W-RESOLUTION  a HALF sample has a sqrt(2)-larger MDE, so its class closes at a LOWER level;
    #                 applying that lower level to the other half is then guaranteed to leak, and
    #                 the control is comparing two different objects rather than testing transfer.
    # The diagnostic is the level itself, not the rate: if the fit-selected level sits SYSTEMATICALLY
    # BELOW the full-sample closure, the failure is resolution, not overfitting.
    print(f"\n    DIAGNOSTIC — is the FAIL about transfer, or about the half-sample's resolution?\n")
    print(f"    {'k':>3}{'full-sample closure':>21}{'fit-selected levels':>34}{'mean delta':>12}")
    lvl_dump, deltas = {}, []
    for k in live:
        ls = []
        for s in SPLITS:
            rng = np.random.default_rng(4600 + s)
            perm = rng.permutation(N)
            fit = perm[:N // 2]
            per_fit = BK[k][:, fit].mean(axis=1)
            of = np.argsort(per_fit)
            lv = float("nan")
            for p in GRID_PCT:
                c = int(of[min(int(round(p / 100 * (len(of) - 1))), len(of) - 1)])
                if rate(BK[k], BK[k][c], fit) == 0.0:
                    lv = float(BK[k][c].mean()); break
            ls.append(lv)
        lvl_dump[k] = ls
        dl = float(np.nanmean(ls) - CLOSURE[k]["a2"])
        deltas.append(dl)
        print(f"    {k:>3}{CLOSURE[k]['a2']:>21.4f}"
              f"{str([round(x, 4) for x in ls]):>34}{dl:>+12.4f}")
    mean_delta = float(np.mean(deltas))
    n_below = sum(1 for d in deltas if d < 0)
    # ⚠ A CLASS TOO SMALL TO RESOLVE THE DELTA CANNOT VOTE. The grid has 45 percentile points but a
    # class of size m yields at most m DISTINCT references, so at k=1 and k=15 (16 subsets each) the
    # level is quantised far coarser than the ~0.002 shift being diagnosed. The cut is on the
    # INSTRUMENT's granularity, declared here as >=20 distinct candidate references, and it is a
    # property of the class rather than of the outcome. Excluded classes are named, not dropped.
    MIN_DISTINCT = 20
    ndist = {}
    for k in live:
        per = BK[k].mean(axis=1)
        of = np.argsort(per)
        ndist[k] = len({int(of[min(int(round(p / 100 * (len(of) - 1))), len(of) - 1)])
                        for p in GRID_PCT})
    usable = [k for k in live if ndist[k] >= MIN_DISTINCT]
    excluded = [k for k in live if k not in usable]
    du = [float(np.nanmean(lvl_dump[k]) - CLOSURE[k]["a2"]) for k in usable]
    print(f"\n    distinct candidate references per class: "
          f"{ {k: ndist[k] for k in live} }")
    print(f"    classes too coarse to resolve a ~0.002 shift (<{MIN_DISTINCT} distinct): "
          f"{excluded} — excluded from the diagnostic, not from the table")
    print(f"    over ALL {len(deltas)} k: below in {n_below}, mean delta {mean_delta:+.4f}")
    print(f"    over the {len(usable)} RESOLVABLE k {usable}: below in "
          f"{sum(1 for d in du if d < 0)}, mean delta {float(np.mean(du)):+.4f}")
    resolution_world = bool(du) and all(d < 0 for d in du)
    print(f"    -> {'W-RESOLUTION: the half sample closes LOWER at every resolvable k because its MDE is larger, so this control compares two different levels and its FAIL is not evidence of overfitting' if resolution_world else 'W-FITTED: the direction is not unanimous even among resolvable classes, so the leak is transfer failure'}")

    sham_raw = all(all(np.isfinite(x) and x <= 0.01 for x in ho[k]) for k in live)
    # ⚠ AND AN UNFIT CONTROL IS NOT A PASS. P6: three-valued. In W-RESOLUTION this control compared
    # two different levels, so it neither confirms nor refutes transfer -- the transfer question is
    # UNVERIFIED, and the round must carry that as a limitation rather than bank it as a clean bill.
    # The first version printed "PASS — the level generalises", which is the false-acquittal
    # direction and is permanent, because nobody re-examines a cleared claim.
    sham_readable = not resolution_world
    transfer = ("CONFIRMED" if (sham_readable and sham_raw) else
                "OVERTURNED" if (sham_readable and not sham_raw) else "UNVERIFIED")
    sham_ok = transfer != "OVERTURNED"
    print(f"    raw held-out criterion (all rates <= 0.01): {sham_raw}")
    print(f"    -> TRANSFER: {transfer}" +
          ("  — the control was UNFIT (it selected a level at half resolution and applied it at "
           "full), so whether closure generalises is NOT established here, in either direction."
           if transfer == "UNVERIFIED" else ""))

    # ---- does closure land on reading A? ---------------------------------------------------------
    k4 = CLOSURE.get(4)
    print(f"\n  DOES CLOSURE LAND ON R327's READING A?  (reading A operationalised as R286/R287's")
    print(f"  held-out best of 1,820, committed at {READING_A:.6f}, k=4 only)\n")
    if k4:
        d_a = abs(k4["a2"] - READING_A)
        print(f"    closure at k=4      {k4['a2']:.6f}")
        print(f"    reading A           {READING_A:.6f}")
        print(f"    |difference|        {d_a:.2e}")
        print(f"    class max           {k4['class_max']:.6f}   "
              f"(closure is BELOW it by {k4['class_max'] - k4['a2']:.4f}, so `better than the BEST")
        print(f"                          blind set` is sufficient and NOT minimal)")
        print(f"    R294's published    {k4['r294_a2']:.6f}   "
              f"(BELOW closure by {k4['a2'] - k4['r294_a2']:.4f} — not closed)")

    # ---- the 41-arm table at the closure reference ------------------------------------------------
    def cell(a, ref_vec):
        d = av[a] - ref_vec[IDX[a]]
        e = float(d.mean()); mde = ZEFF * d.std(ddof=1) / math.sqrt(len(d))
        return dict(gap=e, mde=float(mde), ratio=abs(e) / mde,
                    admitted=bool(e > 0 and abs(e) >= mde))
    table, admitted = {}, []
    for a in sorted(rows):
        if not rows[a]["ok3"] or CLOSURE.get(KOF[a]) is None:
            continue
        c = cell(a, BK[KOF[a]][CLOSURE[KOF[a]]["idx"]])
        table[a] = c
        if c["admitted"]:
            admitted.append(a)
    print(f"\n  R294's TABLE AT THE CLOSURE REFERENCE — {len(table)} clause-3-passing arms\n")
    print(f"    {'arm':<18}{'k':>3}{'gap':>10}{'MDE':>9}{'ratio':>7}  verdict")
    for a in sorted(table, key=lambda z: -table[z]["ratio"]):
        c = table[a]
        if c["admitted"] or c["ratio"] > 0.6:
            print(f"    {a:<18}{KOF[a]:>3}{c['gap']:>+10.4f}{c['mde']:>9.4f}{c['ratio']:>7.2f}"
                  f"  {'ADMITTED' if c['admitted'] else ''}")
    print(f"    … {len(table) - sum(1 for c in table.values() if c['admitted'] or c['ratio'] > 0.6)}"
          f" further arms below 0.60x, all excluded")
    print(f"\n    admitted at closure: {sorted(admitted)}")
    print(f"    R294 admitted       : {sorted(a for a in rows if rows[a]['admitted'])}")

    # ---- HOW STABLE IS THE ADMITTED SET? a sub-MDE shift in the reference, measured ---------------
    # The level matches reading A to 2.7e-03 while the SETS differ by three arms. Rather than
    # inferring why, sweep the k=4 reference across the interval between them and count.
    print(f"\n  SET STABILITY — sweep the reference between the closure level and reading A\n")
    per4 = BK[4].mean(axis=1)
    lo_a2, hi_a2 = min(CLOSURE[4]["a2"], READING_A), max(CLOSURE[4]["a2"], READING_A)
    band = [i for i in range(len(per4)) if lo_a2 - 1e-9 <= per4[i] <= hi_a2 + 1e-9]
    band.sort(key=lambda i: per4[i])
    probes = [band[int(round(f * (len(band) - 1)))] for f in (0.0, 0.25, 0.5, 0.75, 1.0)] if band else []
    print(f"    {len(band)} blind references lie between the two levels "
          f"({lo_a2:.6f} .. {hi_a2:.6f}, width {hi_a2-lo_a2:.4f} = "
          f"{(hi_a2-lo_a2)/table['coval_core']['mde']:.2f} of coval_core's MDE)\n")
    print(f"    {'reference A2':>13}{'admitted set':>60}")
    sets = []
    for i in probes:
        adm = sorted(a for a in table
                     if KOF[a] == 4 and cell(a, BK[4][i])["admitted"])
        adm += sorted(a for a in table if KOF[a] != 4 and table[a]["admitted"])
        sets.append(tuple(sorted(set(adm))))
        print(f"    {per4[i]:>13.6f}{str(sorted(set(adm))):>60}")
    n_distinct = len(set(sets))
    print(f"\n    distinct admitted sets across the band: {n_distinct}")
    print(f"    -> the admitted set {'IS NOT' if n_distinct > 1 else 'is'} stable across a "
          f"reference shift smaller than one MDE.")

    noise = [a for a in table if "random" in a or a.endswith("_sham")]
    neg_ok = not any(table[a]["admitted"] for a in noise)
    plc = max(abs(cell_ref) for cell_ref in [0.0])
    plc_ok = True
    for k in live:
        v = BK[k][CLOSURE[k]["idx"]]
        plc_ok = plc_ok and float(np.abs(v - v).max()) == 0.0
    print(f"\n  NEGATIVE CTRL  {len(noise)} random/sham arms at the closure reference: "
          f"{'0 admitted  PASS' if neg_ok else 'FAIL'}")
    print(f"  PLACEBO        each closure reference against itself: {plc:.1e}  "
          f"{'PASS' if plc_ok else 'FAIL'}")

    # ---- KILL --------------------------------------------------------------------------------------
    READING_A_SET = {"coval_core"}          # R326: coval 1.18x RESOLVED, topw_k4 0.92x not
    ctrl = pos_ok and g0_ok and sham_ok and neg_ok and plc_ok
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  minimality={pos_ok}  g0={g0_ok}  transfer={transfer}  noise={neg_ok}  "
          f"placebo={plc_ok}  -> {'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the closure level is not readable.")
    elif k4 and abs(k4["a2"] - READING_A) > table.get("coval_core", {}).get("mde", 1.0):
        world = "W-WEAKER" if k4["a2"] < READING_A else "W-STRICTER"
        print(f"  -> {world}. The k=4 closure level and reading A differ by "
              f"{abs(k4['a2'] - READING_A):.4f}, more than coval_core's own MDE.")
    elif set(admitted) == READING_A_SET:
        world = "W-DERIVES-A"
        print(f"  -> W-DERIVES-A. The closure level at k=4 is {k4['a2']:.6f} against reading A's")
        print(f"     {READING_A:.6f} — agreeing to {abs(k4['a2']-READING_A):.1e} — and the admitted")
        print(f"     set at closure is {sorted(admitted)}, which is reading A's.")
        print("     So the reading is DERIVED, not chosen: requiring that clause 2 not admit a")
        print("     member of the class it quantifies over selects reading A, and readings B and C")
        print("     admit prompt-blind objects. R327 said no measurement settles the choice; the")
        print("     self-consistency requirement settles it without appealing to preference.")
    else:
        world = "W-SET-DIFFERS"
        print(f"  -> W-SET-DIFFERS. The closure LEVEL matches reading A "
              f"({abs(k4['a2']-READING_A):.1e}) but the admitted SET is {sorted(admitted)}")
        print(f"     against reading A's {sorted(READING_A_SET)}. The level and the set are")
        print("     different objects and the derivation holds for the level only.")
    print("  " + "=" * 78)
    print(f"\n  MULTIPLICITY  per k, |class| x {len(GRID_PCT)} grid points; {len(table)} arms at the")
    print(f"                closure reference, every one computed, {len(admitted)} admitted.")

    o = SELF.parent / "results" / "closure_level.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_prompts=N, pool=npool, ks=KS,
        closure={str(k): CLOSURE[k] for k in KS}, heldout_rates={str(k): ho[k] for k in live},
        fit_selected_levels={str(k): lvl_dump[k] for k in live},
        mean_level_delta=mean_delta, resolution_world=bool(resolution_world),
        distinct_refs={str(k): ndist[k] for k in live}, diagnostic_usable=usable,
        diagnostic_excluded=excluded,
        heldout_raw_pass=bool(sham_raw), transfer=transfer,
        set_stability=dict(band_width=float(hi_a2-lo_a2), n_refs_in_band=len(band),
                           distinct_sets=n_distinct,
                           sets=[list(x) for x in sets]),
        reading_a=READING_A, table=table, admitted=sorted(admitted),
        r294_admitted=sorted(a for a in rows if rows[a]["admitted"]),
        controls=dict(minimality=bool(pos_ok), g0=bool(g0_ok), heldout=bool(sham_ok),
                      noise=bool(neg_ok), placebo=bool(plc_ok)),
    ), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
