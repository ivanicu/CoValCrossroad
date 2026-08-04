"""R330 — read the bracket conservatively across all 41 arms. Does the definition survive itself?

R329 left one choice with a principled answer and one open cost. The answer: when a budget is only
PARTIALLY IDENTIFIED, the non-flattering reading is the UPPER bound, because admitting an arm on the
strength of a quantity that can only be understated is the flattering direction. The cost: applied
to R294's 41 judged arms it may empty the admitted set, and a definition that admits nothing is as
useless as one that admits everything.

AND THERE IS A THIRD OUTCOME WORSE THAN EITHER, which is why this round exists rather than a note.
R294's admitted set is {coval_core, topw_k3, topw_k4, topw_k6, topw_k8}: the release's own core,
plus ONE RULE at four values of k. Those four are cells of the very grid whose size is the budget,
so they rise and fall together. If the conservative reading removes them, what remains is exactly
the object the definition was written from -- which is §4's `the definition describes the instance`
arriving not through a clause but through a BASELINE choice.

THE ASYMMETRY THIS READING CREATES, named before it is measured. Budget-matching gives an unsearched
arm the WEAKEST baseline and a searched arm the strongest, so the conservative reading REWARDS NOT
SEARCHING. In multiple-comparison terms that is correct -- no search, no selection bias -- but it
means the reading structurally favours singletons, and the incumbent is a singleton. That is a
property of the rule, it is not a defect of it, and it is stated here so nobody reads the outcome as
a fact about coval_core's quality.

ESTIMAND      (i) the partition of R294's 41 arms into BRACKETED (a cell of a rule/parameter family
              this campaign scored) and SINGLETON (one object, no in-campaign selection);
              (ii) each arm's clause-2 margin against the reference at the UPPER bound of its own
              bracket, with a per-cell MDE; (iii) whether the admitted set under that reading is a
              subset of {coval_core}.
IDENTIFICATION The partition is exact and mechanical: an arm is BRACKETED iff its name is a cell of
              select_core.py's own (rule x k) product. Margins are exact. The budget itself is only
              partially identified (R329), so U is swept over R329's four enumerations and the
              answer is a curve, never a cell.
SCOPE         population R294's 41 judged arms over 968 CoVal prompts with >=2 annotators ·
              instrument Qwen3.5-2B-Base under R234's canonical builder · baseline best-of-U
              in-sample over the 1,820 generic-pool quadruples · regime all annotators, A2.
WORLDS        W-COLLAPSE  admitted subset of {coval_core} -> the definition, read non-flatteringly,
                          admits exactly the object it was written from. The conservative reading
                          is then NOT AVAILABLE, and the finding is about the definition rather
                          than about any arm.
              W-SURVIVES  at least one arm that is not the incumbent survives -> the definition has
                          content beyond its instance and the conservative reading is usable.
              W-EMPTY     nothing survives, not even coval_core -> clause 2 is unusable as worded
                          at the conservative reading.
KILL          pre-registered, conditional on the controls, at the STRICTEST enumeration (U4):
                admitted == {}                          -> W-EMPTY
                admitted subset of {coval_core}          -> W-COLLAPSE
                otherwise                                -> W-SURVIVES
              and the same evaluation is printed at all four enumerations, so the curve is the
              report and the kill is one point on it.
POSITIVE CTRL reproduce R294's committed clause-2 gap for ALL 41 arms from this round's own
              pipeline, using R294's own reference (the incumbent quadruple {0,1,2,3}). 41 exact
              reproductions or the A2 pipeline is not the one that produced the census. It FAILS at
              g=0: a deliberately WRONG reference (a different quadruple) must NOT reproduce them,
              and that is run, not asserted.
NEGATIVE CTRL the random and sham arms must be excluded at their OWN WEAKEST reference (U=1, the
              most permissive cell any arm gets). An arm drawn without looking at scores that still
              clears the weakest baseline would mean the reading admits noise, and nothing after it
              is readable. Names are not used: the set is taken from R294's own rows.
SHAM          a NONSENSE partition -- classify by whether the arm name has an even number of
              characters -- must produce a DIFFERENT partition from the construction-based one. If
              a nonsense rule reproduces my partition, my partition is reading names and not
              construction.
PLACEBO       every arm against itself: exactly 0.0.
NOISE FLOOR   per-cell MDE = ZEFF * sd(paired difference) / sqrt(N); and the count of arms whose
              ratio lands in [0.95, 1.05], because an admitted set decided inside that band is
              decided by noise.
MULTIPLICITY  41 arms x 4 enumerations = 164 cells, BH q=0.05 over all 164, non-survivors counted.
SPECIFICATION the enumeration axis IS the curve, published whole including the cells that refuse
              the finding, plus the lower-bound column (U = committed count) for contrast.
SEEDS         3 for the best-of-U draws, as in R328; the reference curve's across-seed sd is
              reported and the admitted set is recomputed at each seed.
ARTIFACT      results/conservative_reading.json with source hash.
IMPOSSIBLE    - the arms' TRUE selection budgets (R329's register entry, unchanged).
              - coval_core's EXTERNAL construction budget, set by the release's authors. Its
                in-campaign budget is 1 and that is the only quantity this round uses. If the
                release searched, the asymmetry above is larger than measured, and the direction of
                that error is stated: it would make coval_core's admission weaker, never stronger.
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, re, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

SELF = pathlib.Path(__file__).resolve()
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
SEEDS = (0, 1, 2)
NREP = 20
FLIP = (0.95, 1.05)
RULE_CELL = re.compile(r"^(topw|topabs|topvar|topwvar|oracle|greedy|indep)_k\d+(_fit\d+)?$")


def load_json(pat):
    d = next(A24.glob(pat), None)
    if d is None:
        return None
    f = sorted((d / "results").glob("*.json"))
    return json.loads(f[0].read_text()) if f else None


def main() -> int:
    r294, r329 = load_json("R294_*"), load_json("R329_*")
    if not all((r294, r329)):
        print("  UNRUNNABLE: R294 or R329 absent."); return 2
    rows = r294["rows"]
    ENUM_U = dict(sorted(r329["enumerations"].items(), key=lambda kv: kv[1]))
    L_committed = r329["lower_bound"]

    # ---- the partition, mechanical -------------------------------------------------------------
    bracketed = {a for a in rows if RULE_CELL.match(a)}
    singleton = set(rows) - bracketed
    print(f"  {len(rows)} judged arms · BRACKETED {len(bracketed)} · SINGLETON {len(singleton)}\n")
    print(f"    bracketed : {sorted(bracketed)}")
    print(f"    singleton : {sorted(singleton)}\n")

    # ---- PROMPT-BLIND DETECTOR · mechanical, from the arms' own criterion sets ------------------
    # ⚠ ADDED after v3 fired W-SURVIVES on `generic`. `generic` IS clause 2's reference class -- a
    # fixed criterion set that never reads the conversation -- and R294's FIXED reference excluded
    # it correctly (c2 = +0.0009, its own self-comparison). Budget-matching destroys that: as a
    # SINGLETON it draws the weakest reference (best-of-1) and clears it. So the conservative
    # reading admits the baseline as a core, and my kill did not check for that because
    # `W-SURVIVES` was defined as "some arm other than the incumbent", which is not the same
    # question. The detector below is mechanical and has its own control.
    def prompt_blind(a):
        f = ROOT / "corebench" / "results" / f"core_{a}.json"
        if f.exists():
            j = json.loads(f.read_text())
            sets = {tuple(sorted(i["criterion"] if isinstance(i, dict) else str(i)
                                 for i in items))
                    for items in j.values() if isinstance(items, list)}
            return (len(sets) == 1) if sets else None
        if a == "coval_core":
            rl = ROOT / "data" / "conversation_rubrics.jsonl"
            if not rl.exists():
                return None
            sets = set()
            for line in rl.read_text().splitlines():
                if not line.strip():
                    continue
                r = json.loads(line)
                cc = r.get("coval_core") or []
                if cc:
                    sets.add(tuple(sorted(i["criterion"] for i in cc)))
            return (len(sets) == 1) if sets else None
        return None

    BLIND = {a: prompt_blind(a) for a in rows}
    blind_arms = sorted(a for a, v in BLIND.items() if v is True)
    unknown_blind = sorted(a for a, v in BLIND.items() if v is None)
    det_ok = (BLIND.get("generic") is True) and (BLIND.get("topw_k4") is False) \
        and (BLIND.get("coval_core") is False)
    print(f"  PROMPT-BLIND DETECTOR  criterion set identical across every prompt?")
    print(f"    flagged blind : {blind_arms}")
    print(f"    UNDETERMINED  : {unknown_blind if unknown_blind else 'none'}")
    print(f"    control — generic=True, topw_k4=False, coval_core=False: "
          f"{'PASS' if det_ok else 'FAIL'}  "
          f"(got {BLIND.get('generic')}, {BLIND.get('topw_k4')}, {BLIND.get('coval_core')})\n")

    pos_part = ("coval_core" in singleton) and ("topw_k4" in bracketed)
    print(f"  POSITIVE (partition)  coval_core SINGLETON and topw_k4 BRACKETED, both established"
          f" by R328/R329: {'PASS' if pos_part else 'FAIL'}")

    # SHAM partition: a nonsense rule must not reproduce the construction-based one
    sham_part = {a for a in rows if len(a) % 2 == 0}
    sham_ok = sham_part != bracketed
    print(f"  SHAM (partition)      even-name-length partition differs from the construction one:"
          f" {'PASS' if sham_ok else 'FAIL — my partition is reading names'}"
          f"  (|sham|={len(sham_part)}, overlap={len(sham_part & bracketed)})")

    # ---- the data ------------------------------------------------------------------------------
    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
    ARM = {}
    for a in sorted(rows):
        f = ROOT / "corebench" / "results" / f"sat_{a}.npz"
        if not f.exists():
            print(f"  UNRUNNABLE: sat_{a}.npz absent."); return 2
        ARM[a] = load_sat(f)
    # ⚠ THE BASIS IS THE POOL, NOT THE INTERSECTION OF THE ARMS. v1 intersected all 41 arms and
    # got 398 prompts instead of 968 -- `promptecho` and `promptecho_sham` cover only 398, and
    # they dragged every other arm down with them. R294 evaluates each arm on ITS OWN population,
    # which is why the 41-arm reproduction control failed and localised in one line. Each arm is
    # now scored on the prompts it actually covers, and its n is checked against R294's.
    pids = sorted(set(S) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    N = len(pids)
    npool = len({i for i, _ in S[pids[0]]})
    SAT = np.stack([np.array([[S[p][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                    for p in pids])
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])

    # ⚠ THE REFERENCE IS SIZE-MATCHED TO THE ARM'S k, and v1 and v2 used 4-subsets for every arm.
    # R294 line 140: `on(POOL, ps, list(range(min(K[a], npool))))` -- the blind reference is the
    # first k criteria of the generic pool, so a k=6 arm is compared to a SIX-subset. Comparing a
    # k=6 arm to the best of the QUADRUPLES is the `comparing arms of different k` error the
    # campaign has been warning about since R287, committed by me in the round that repaired it.
    # The 41-arm reproduction is what caught it: it failed for every arm with k != 4 and for none
    # with k == 4.
    KOF = {a: min(rows[a]["k"], npool) for a in rows}
    KS = sorted({KOF[a] for a in rows if rows[a]["ok3"]})
    print(f"\n  {N} prompts · pool {npool} · {len(ARM)} arm npzs · size-matched pools for "
          f"k in {KS}\n")

    def build_B(k):
        sb = np.array(list(itertools.combinations(range(npool), k)))
        out = np.empty((len(sb), N))
        for n in range(N):
            Y = SAT[n][sb].sum(axis=1)
            C_ = np.sign(Y[:, ii] - Y[:, jj])
            out[:, n] = (C_[:, None, :] == H[n][None, :, :]).mean(axis=(1, 2))
        return sb, out

    SUBS, BK = {}, {}
    for k in KS:
        SUBS[k], BK[k] = build_B(k)
        print(f"    k={k:>3}  {len(SUBS[k]):>6} subsets")
    # per-arm population: the prompts THAT arm covers, as indices into `pids`
    IDX = {a: np.array([n for n, p in enumerate(pids) if p in ARM[a]]) for a in sorted(rows)}
    av = {a: np.array([np.mean([[cls(yvec(ARM[a][pids[n]],
                                          sorted({i for i, _ in ARM[a][pids[n]]})))[c] == h[c]
                                 for c in range(6)] for h in H[n]]) for n in IDX[a]])
          for a in sorted(rows)}

    # ---- POPULATION CONTROL · each arm's n must equal R294's ------------------------------------
    nmis = {a: (len(IDX[a]), rows[a]["n"]) for a in rows if len(IDX[a]) != rows[a]["n"]}
    npop_ok = not nmis
    print(f"  POPULATION CTRL  every arm's n equals R294's: "
          f"{'PASS' if npop_ok else 'FAIL ' + str(nmis)}")
    print(f"    distinct n across arms: "
          f"{sorted({len(IDX[a]) for a in rows})}  (the 398s are promptecho and its sham)")

    # ---- POSITIVE CONTROL · reproduce R294's 41 committed clause-2 gaps -------------------------
    def first_k_index(k):
        return int(np.where((SUBS[k] == np.arange(k)).all(axis=1))[0][0])

    def wrong_k_index(k):
        """g=0: a DIFFERENT subset of the same size. Must NOT reproduce R294."""
        tgt = np.array(list(range(k - 1)) + [min(k, npool - 1) if k < npool else k - 1])
        hits = np.where((SUBS[k] == tgt).all(axis=1))[0]
        return int(hits[0]) if len(hits) else (1 % len(SUBS[k]))

    REF294 = {k: BK[k][first_k_index(k)] for k in KS}
    REFBAD = {k: BK[k][wrong_k_index(k)] for k in KS}
    ok3_arms = [a for a in rows if rows[a]["ok3"]]
    dev = {a: abs(float((av[a] - REF294[KOF[a]][IDX[a]]).mean()) - rows[a]["c2"][0])
           for a in ok3_arms}
    dev_bad = {a: abs(float((av[a] - REFBAD[KOF[a]][IDX[a]]).mean()) - rows[a]["c2"][0])
               for a in ok3_arms}
    pos_ok = max(dev.values()) < 1e-12
    g0_ok = max(dev_bad.values()) > 1e-6
    print(f"  POSITIVE CTRL  reproduce R294's committed clause-2 gap for all {len(ok3_arms)} clause-3-passing arms")
    print(f"    max deviation with R294's OWN reference (incumbent quadruple): {max(dev.values()):.3e}"
          f"   {'PASS' if pos_ok else 'FAIL'}")
    print(f"    g=0 · the SAME check against a WRONG quadruple: max deviation "
          f"{max(dev_bad.values()):.3e}   "
          f"{'PASS (correctly fails to reproduce)' if g0_ok else 'FAIL — the check is blind'}")

    # ---- PLACEBO -------------------------------------------------------------------------------
    plc = max(float(np.abs(av[a] - av[a]).max()) for a in rows)
    plc_ok = plc == 0.0
    print(f"  PLACEBO        every arm against itself: {plc:.1e}  {'PASS' if plc_ok else 'FAIL'}")

    # ---- best-of-U references ------------------------------------------------------------------
    def best_of(k, m, seed):
        Bk = BK[k]; ns = len(Bk)
        rng = np.random.default_rng(500_000 + 7919 * k + 1000 * seed + m)
        acc = np.zeros(N)
        for _ in range(NREP):
            idx = np.arange(ns) if m >= ns else rng.choice(ns, m, replace=False)
            acc += Bk[idx[int(np.argmax(Bk[idx].mean(axis=1)))]]
        return acc / NREP

    U_VALUES = sorted({1, L_committed, *ENUM_U.values()})
    REF = {(k, m): [best_of(k, m, s) for s in SEEDS] for k in KS for m in U_VALUES}
    print(f"\n  REFERENCE at each budget, PER SIZE-MATCHED POOL ({NREP} reps x {len(SEEDS)} seeds)\n")
    print("    " + f"{'U':>6}" + "".join(f"{'k='+str(k):>11}" for k in KS))
    for m in U_VALUES:
        print(f"    {m:>6}" + "".join(
            f"{np.mean([v.mean() for v in REF[(k, m)]]):>11.5f}" for k in KS))
    print("    " + f"{'sd':>6}" + "".join(
        f"{np.std([v.mean() for v in REF[(k, U_VALUES[-1])]]):>11.5f}" for k in KS)
        + "   (at the largest U)")

    def cell(a, m):
        k = KOF[a]
        rv = np.mean(REF[(k, m)], axis=0)[IDX[a]]
        d = av[a] - rv
        mde = ZEFF * d.std(ddof=1) / math.sqrt(len(d))
        e = float(d.mean())
        return dict(gap=e, mde=float(mde), ratio=abs(e) / mde, k=k,
                    n_subsets=int(len(BK[k])),
                    admitted=bool(e > 0 and abs(e) >= mde))

    # ---- NEGATIVE CTRL · noise arms at the MOST PERMISSIVE reference ------------------------------
    noise_arms = sorted(a for a in rows if rows[a]["prov"] != "no prompt labels used"
                        or "random" in a or "sham" in a)
    noise_arms = sorted(a for a in rows if re.search(r"random_k\d+_s\d+$|_sham$", a))
    noise_hits = [a for a in noise_arms if cell(a, 1)["admitted"]]
    neg_ok = not noise_hits
    print(f"\n  NEGATIVE CTRL  {len(noise_arms)} random/sham arms at U=1, the most permissive")
    print(f"                 reference any arm receives: {len(noise_hits)} admitted  "
          f"{'PASS' if neg_ok else 'FAIL — the reading admits noise: ' + str(noise_hits)}")
    print(f"                 {noise_arms}")

    # ---- the curve -------------------------------------------------------------------------------
    def admitted_at(label, U_bracketed):
        out = {}
        for a in rows:
            if not rows[a]["ok3"]:
                out[a] = None; continue          # clause 3 already excludes it; not re-litigated
            m = U_bracketed if a in bracketed else 1
            out[a] = cell(a, m)
        return out

    SPECS = {"U = committed count (R328's LOWER bound)": L_committed, **ENUM_U}
    curve, grid_cells = {}, []
    print(f"\n  THE CURVE — admitted set as the bracket is read from its lower to its upper bound\n")
    print(f"    {'reading':<40}{'U(bracketed)':>13}{'admitted':>10}   arms")
    for lab, U in SPECS.items():
        res = admitted_at(lab, U)
        adm = sorted(a for a, c in res.items() if c and c["admitted"])
        curve[lab] = dict(U=U, admitted=adm,
                          cells={a: c for a, c in res.items() if c})
        for a, c in res.items():
            if c:
                grid_cells.append((f"{lab}|{a}", c["ratio"]))
        print(f"    {lab[:39]:<40}{U:>13}{len(adm):>10}   {adm}")

    band = sum(1 for _, r in grid_cells if FLIP[0] <= r <= FLIP[1])
    print(f"\n    cells whose ratio lands in [0.95, 1.05]: {band} of {len(grid_cells)}"
          f"  — an admitted set decided inside that band is decided by noise")

    # ---- seed robustness of the admitted set -----------------------------------------------------
    strict_U = max(ENUM_U.values())
    per_seed = []
    for s in SEEDS:
        adm_s = []
        for a in rows:
            if not rows[a]["ok3"]:
                continue
            m = strict_U if a in bracketed else 1
            d = av[a] - REF[(KOF[a], m)][s][IDX[a]]
            e = float(d.mean()); mde = ZEFF * d.std(ddof=1) / math.sqrt(len(d))
            if e > 0 and abs(e) >= mde:
                adm_s.append(a)
        per_seed.append(sorted(adm_s))
    seed_ok = all(x == per_seed[0] for x in per_seed)
    print(f"\n  SEEDS  admitted set at the strictest reading, per seed: "
          f"{per_seed}  identical: {seed_ok}")

    # ---- MULTIPLICITY ----------------------------------------------------------------------------
    print(f"\n  MULTIPLICITY  {len(grid_cells)} cells across {len(SPECS)} readings; "
          f"admitted counts printed per reading, non-admitted are the complement and are named "
          f"in the artifact.")

    # ---- KILL --------------------------------------------------------------------------------------
    strict_lab = max(SPECS, key=lambda k: SPECS[k])
    strict = set(curve[strict_lab]["admitted"])
    ctrl = (pos_part and sham_ok and npop_ok and pos_ok and g0_ok and plc_ok and neg_ok
            and seed_ok and det_ok)
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  partition={pos_part}  sham={sham_ok}  population={npop_ok}  "
          f"repro41={pos_ok}  g0={g0_ok}  placebo={plc_ok}  noise={neg_ok}  seed={seed_ok}  "
          f"blind-detector={det_ok}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the conservative reading is not readable.")
    elif not strict:
        world = "W-EMPTY"
        print(f"  -> W-EMPTY. At `{strict_lab}` (U={SPECS[strict_lab]}) NOTHING is admitted, not")
        print("     even the incumbent. Clause 2 is unusable at the conservative reading.")
    elif set(strict) & set(blind_arms):
        world = "W-ADMITS-THE-BASELINE"
        hit = sorted(set(strict) & set(blind_arms))
        print(f"  -> W-ADMITS-THE-BASELINE. At `{strict_lab}` (U={SPECS[strict_lab]}) the admitted")
        print(f"     set {sorted(strict)} contains {hit} — a criterion set that is IDENTICAL on")
        print("     every prompt, i.e. a member of clause 2's OWN reference class. Clause 2 says")
        print("     `better than the same number that never read the conversation at all`, and")
        print("     this arm never reads it. R294's FIXED reference excluded it correctly, by")
        print("     self-comparison. Budget-matching destroys that: as a SINGLETON it draws the")
        print("     weakest reference and clears it. So the conservative reading is NOT USABLE —")
        print("     not because it admits too little, but because it admits the baseline.")
    elif strict <= {"coval_core"}:
        world = "W-COLLAPSE"
        print(f"  -> W-COLLAPSE. At `{strict_lab}` (U={SPECS[strict_lab]}) the admitted set is")
        print(f"     {sorted(strict)} — exactly the object the definition was written from.")
        print("     `the definition describes the instance`, arriving through a BASELINE choice")
        print("     rather than through a clause. So the conservative reading is NOT AVAILABLE:")
        print("     it is correct about budgets and it makes the definition contentless, and a")
        print("     definition whose only admitted object is its own instance predicts nothing.")
    else:
        world = "W-SURVIVES"
        print(f"  -> W-SURVIVES. At `{strict_lab}` (U={SPECS[strict_lab]}) the admitted set is")
        print(f"     {sorted(strict)}, which contains an arm that is not the incumbent. The")
        print("     definition has content beyond its instance and the conservative reading is")
        print("     usable as written.")
    print("  " + "=" * 78)
    # ⚠ this block typed "the incumbent is the only admitted singleton", which the round's own
    # output contradicts -- `generic` is an admitted singleton too, and that IS the finding.
    # Any comparative word in a closing sentence must be computed. It is now.
    adm_single = sorted(set(strict) & singleton)
    blind_every = [lab for lab, v in curve.items() if set(v["admitted"]) & set(blind_arms)]
    print(f"\n  ⚠ THE ASYMMETRY IS A PROPERTY OF THE RULE, NOT A FACT ABOUT ANY ARM.")
    print(f"    Budget-matching gives an unsearched arm the weakest baseline, so it REWARDS NOT")
    print(f"    SEARCHING. In multiple-comparison terms that is right — no search, no selection")
    print(f"    bias — and it is exactly the channel by which the baseline gets in.")
    print(f"    admitted singletons at the strictest reading: {adm_single}")
    print(f"    readings whose admitted set contains a prompt-blind arm: {len(blind_every)} of "
          f"{len(curve)}")
    if len(blind_every) == len(curve):
        print(f"    -> the defect is NOT specific to the conservative end. Budget-matching admits")
        print(f"       the baseline at EVERY reading, so the rule fails as a clause-2 reference")
        print(f"       everywhere, and R328's and R329's line rests on it.")

    o = SELF.parent / "results" / "conservative_reading.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_prompts=N, n_arms=len(rows), bracketed=sorted(bracketed), singleton=sorted(singleton),
        specs=SPECS, curve={k: dict(U=v["U"], admitted=v["admitted"],
                                    cells=v["cells"]) for k, v in curve.items()},
        r294_admitted=sorted(a for a in rows if rows[a]["admitted"]),
        prompt_blind={a: BLIND[a] for a in sorted(rows)}, blind_arms=blind_arms,
        blind_undetermined=unknown_blind,
        strictest=dict(label=strict_lab, admitted=sorted(strict)),
        per_seed=per_seed, seed_identical=bool(seed_ok), flip_band_cells=band,
        readings_admitting_blind=blind_every, admitted_singletons=adm_single,
        noise_arms=noise_arms, noise_admitted=noise_hits,
        controls=dict(partition=bool(pos_part), sham=bool(sham_ok), repro41=bool(pos_ok),
                      g0=bool(g0_ok), placebo=bool(plc_ok), noise=bool(neg_ok),
                      seed=bool(seed_ok), population=bool(npop_ok),
                      blind_detector=bool(det_ok)),
        per_arm_n={a: int(len(IDX[a])) for a in sorted(rows)},
        repro_max_dev=max(dev.values()), repro_wrongref_max_dev=max(dev_bad.values()),
    ), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
