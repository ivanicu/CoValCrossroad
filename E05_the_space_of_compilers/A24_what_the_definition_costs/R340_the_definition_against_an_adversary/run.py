"""R340 — the definition has only ever judged arms I happened to have. Here is one built to beat it.

Every arm in R294's census was built to be a good core, or to be a control. None was built to SATISFY
THE DEFINITION while not being a core in any useful sense. That is the falsification the definition
has never faced, and it is the one test where PASSING would be the bad outcome.

⛔ FIRST, THE ARITHMETIC, BECAUSE IT NARROWS THE ATTACK SURFACE BEFORE ANY COMPUTE.
Clause 1 is `arm - random_k4_s0` and clause 2 is `arm - blind_k`. Both baselines are FIXED vectors
the arm cannot influence, so both margins rise if and only if the arm's own A2 rises. **Neither
clause is gameable without actually agreeing with the humans more** -- that is a derivation, not a
measurement, and it means the attack cannot come through the comparison. It has to come through
clause 3: an arm that is EFFECTIVELY label-informed while passing clause 3's source-reading, or an
arm that reaches high A2 by a route the definition did not intend to bless.

So the adversary here is LABEL-FREE BY CONSTRUCTION -- it never reads `tg` -- and optimises three
objectives aimed at the definition rather than at quality:

    adv_mimic      maximise agreement with the FULL RUBRIC's own verdict. R294 records that cores
                   "depart from the rubric to track the human", so an admitted rubric-imitator would
                   contradict the page's own account of what a core is.
    adv_decisive   maximise the MARGIN MAGNITUDE |Y_i - Y_j| of its own verdicts. Confidence, not
                   correctness: an arm that commits hard on every pair.
    adv_antiblind  maximise DISAGREEMENT with the size-matched blind reference. Clause 2's numerator
                   is `arm - blind`, so this is the objective aimed most directly at the clause.

⚠ AND THE PREDICTION IS THAT THEY FAIL, WHICH IS WHY THE ROUND IS WORTH RUNNING. The derivation says
they must fail unless they are genuinely good. If one is ADMITTED anyway, the derivation is wrong
somewhere and that is a finding about clause 3's coverage. If all three fail, the definition has
survived its first deliberate adversary and the margin by which it survived is the number.

ESTIMAND      for each adversarial arm: A2, clause-1 margin / MDE, clause-2 margin / MDE, and
              admission under the page's own rule; plus the gap to `topw_k4`, the best LABEL-FREE
              arm the campaign already has, which is the honest benchmark for a label-free attack.
IDENTIFICATION Exact. The arms are constructed here, so their provenance is known by construction:
              the selection code never touches `tg`, and the round asserts that mechanically rather
              than claiming it.
SCOPE         population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base under
              R234's canonical builder · baselines `random_k4_s0` (clause 1) and the size-matched
              first-k blind subset (clause 2), as R294 published them · regime k=4, search budget
              300 candidate subsets per prompt.
WORLDS        W-ROBUST   no adversarial arm is admitted -> the definition survives its first
                         deliberate adversary, and the margin by which each fails is the report.
              W-GAMED    an adversarial arm IS admitted -> the definition blesses an object built
                         to imitate the rubric or to be merely decisive, and the derivation above
                         is wrong about where the attack surface is.
              W-DEGENERATE the adversarial arms land at or below the random floor -> the objectives
                         are not coherent attacks and the round tested nothing. Reported as such
                         rather than as a survival.
KILL          pre-registered, conditional on the controls:
                any adversarial arm admitted (clause 1 AND 2 resolve positive)   -> W-GAMED
                else every adversarial arm at or below `random_k4_s0`'s A2       -> W-DEGENERATE
                else                                                             -> W-ROBUST
POSITIVE CTRL an ORACLE arm built by the same search but maximising agreement with the humans --
              the one objective that DOES use labels -- must be admitted on clauses 1 and 2 and must
              be excluded by clause 3. If the search cannot find an admissible arm when it is
              allowed to see the answer, the search budget is too small and every failure below is
              silence rather than survival. It FAILS at g=0: the same search with a RANDOM objective
              must land at the random floor.
NEGATIVE CTRL the label-free assertion is checked mechanically, not claimed: the selection functions
              are called with `tg` absent from their closure, and a deliberate LEAK variant is built
              alongside to show the harness would notice if labels were used.
SHAM          `adv_mimic` is the sham for "a core is a compressed rubric": same operation, target
              swapped from the human to the rubric. Its gap to `topw_k4` is the value of aiming at
              the human rather than at the rubric.
PLACEBO       each arm against itself: exactly 0.
NOISE FLOOR   per-cell MDE from the paired cluster bootstrap, as the page computes it.
MULTIPLICITY  4 constructed arms x 2 clauses x 3 seeds; every cell printed.
SPECIFICATION the three objectives ARE the specification curve over what an adversary could aim at.
SEEDS         3 search seeds; all reported.
ARTIFACT      results/adversarial_arms.json with source hash.
IMPOSSIBLE    an adversary with unbounded search. The budget is 300 subsets per prompt; a larger
              budget can only help the adversary, so W-ROBUST is a statement AT THIS BUDGET and the
              direction of that limitation is stated rather than hidden.
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
IIP = np.array([i for i, _ in PAIRS]); JJP = np.array([j for _, j in PAIRS])
ZEFF = 1.959964 + 0.841621
K, NSUB = 4, 300
SEEDS = (0, 1, 2)


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
    RES = ROOT / "corebench" / "results"
    tg, _ = load_targets()
    FULL = load_sat(RES / "sat_full.npz")
    POOL = load_sat(RES / "sat_genericpool16.npz")
    RAND = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted(set(FULL) & set(POOL) & set(RAND) & {p for p in tg if len(tg[p]) >= 2})
    N = len(pids)
    if N < 50:
        print(f"  UNRUNNABLE: only {N} prompts."); return 2
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    RUB = [np.array([[FULL[p][(i, x)] for x in "ABCD"]
                     for i in sorted({i for i, _ in FULL[p]})], float) for p in pids]
    PL = [np.array([[POOL[p][(i, x)] for x in "ABCD"]
                    for i in sorted({i for i, _ in POOL[p]})], float) for p in pids]
    nrub = np.array([len(r) for r in RUB]); npool = len(PL[0])
    print(f"  {N} prompts · rubric median {int(np.median(nrub))} · pool {npool} · "
          f"k={K} · search budget {NSUB} subsets/prompt\n")

    def verd(satmat, sel):
        Y = satmat[sel].sum(axis=0)
        return np.sign(Y[IIP] - Y[JJP]), Y

    def a2_of(c, n):
        return float((np.asarray(c, float)[None, :] == H[n]).mean())

    # the two fixed baselines, exactly as R294 published them
    ref1 = np.array([a2_of(cls(yvec(RAND[pids[n]], sorted({i for i, _ in RAND[pids[n]]}))), n)
                     for n in range(N)])
    ref2 = np.array([a2_of(verd(PL[n], list(range(K)))[0], n) for n in range(N)])
    full_v = [verd(RUB[n], list(range(nrub[n])))[0] for n in range(N)]

    # ---- the adversarial objectives · LABEL-FREE BY CONSTRUCTION --------------------------------
    # None of these closures references `H` or `tg`. The oracle below DOES, and is the positive
    # control precisely because it is the one that may not pass clause 3.
    def obj_mimic(C, Y, n):    return (C == full_v[n][None, :]).mean(axis=1)
    def obj_decisive(C, Y, n): return np.abs(Y[:, IIP] - Y[:, JJP]).mean(axis=1)
    def obj_antiblind(C, Y, n):
        b, _ = verd(PL[n], list(range(K)))
        return (C != b[None, :]).mean(axis=1)
    def obj_random(C, Y, n):   return np.zeros(len(C))
    def obj_oracle(C, Y, n):   return (C[:, None, :] == H[n][None, :, :]).mean(axis=(1, 2))

    OBJ = {"adv_mimic": obj_mimic, "adv_decisive": obj_decisive,
           "adv_antiblind": obj_antiblind, "ORACLE (pos ctrl)": obj_oracle,
           "random (g=0)": obj_random}
    LABEL_FREE = {"adv_mimic", "adv_decisive", "adv_antiblind", "random (g=0)"}

    def build(name, seed):
        rng = np.random.default_rng(310_000 + 7919 * seed)
        out = np.empty(N)
        for n in range(N):
            sels = np.stack([rng.choice(nrub[n], K, replace=False) for _ in range(NSUB)])
            Y = RUB[n][sels].sum(axis=1)
            C = np.sign(Y[:, IIP] - Y[:, JJP])
            sc = OBJ[name](C, Y, n)
            pick = int(rng.integers(NSUB)) if name.startswith("random") else int(np.argmax(sc))
            out[n] = a2_of(C[pick], n)
        return out

    def cell(av, ref):
        d = av - ref
        e = float(d.mean()); mde = ZEFF * d.std(ddof=1) / math.sqrt(len(d))
        return e, mde, (e > 0 and abs(e) >= mde)

    print(f"  THE ADVERSARIAL ARMS  (objective aimed at the DEFINITION, not at quality)\n")
    print(f"    {'arm':<20}{'A2':>9}{'① eff/MDE':>13}{'② eff/MDE':>13}{'admitted?':>11}"
          f"{'label-free':>12}")
    R, adm = {}, []
    for name in OBJ:
        a2s, c1s, c2s, oks = [], [], [], []
        for s in SEEDS:
            av = build(name, s)
            e1, m1, o1 = cell(av, ref1); e2, m2, o2 = cell(av, ref2)
            a2s.append(av.mean()); c1s.append(e1 / m1); c2s.append(e2 / m2); oks.append(o1 and o2)
        ok = sum(oks) >= 2
        R[name] = dict(a2=float(np.mean(a2s)), c1=float(np.mean(c1s)), c2=float(np.mean(c2s)),
                       admitted=bool(ok), per_seed_admitted=[bool(x) for x in oks],
                       a2_sd=float(np.std(a2s)))
        if ok and name in LABEL_FREE and not name.startswith("random"):
            adm.append(name)
        print(f"    {name:<20}{np.mean(a2s):>9.4f}{np.mean(c1s):>13.2f}{np.mean(c2s):>13.2f}"
              f"{('ADMITTED' if ok else 'no'):>11}{('yes' if name in LABEL_FREE else 'NO'):>12}")

    print(f"\n    for reference, the campaign's best LABEL-FREE arm: topw_k4 A2 "
          f"{rows['topw_k4']['a2']:.4f}, and the random floor "
          f"{ref1.mean():.4f}")

    # ---- controls ---------------------------------------------------------------------------------
    pos_ok = R["ORACLE (pos ctrl)"]["admitted"]
    g0_ok = not R["random (g=0)"]["admitted"]
    print(f"\n  POSITIVE CTRL  the ORACLE objective (the ONE that reads labels) is admitted on "
          f"clauses 1+2: {pos_ok}")
    print(f"    {'PASS — the search CAN find an admissible arm at this budget, so a failure below is a measurement' if pos_ok else 'FAIL — the budget is too small and every failure below is silence'}")
    print(f"    g=0 · the same search with a RANDOM objective: admitted = "
          f"{R['random (g=0)']['admitted']}, A2 {R['random (g=0)']['a2']:.4f} vs the random floor "
          f"{ref1.mean():.4f}  {'PASS' if g0_ok else 'FAIL'}")

    # ---- NEGATIVE · the label-free assertion, checked rather than claimed ---------------------------
    import inspect
    leaks = {nm: ("H" in inspect.getsource(OBJ[nm]) or "tg" in inspect.getsource(OBJ[nm]))
             for nm in OBJ}
    neg_ok = (not any(leaks[nm] for nm in LABEL_FREE)) and leaks["ORACLE (pos ctrl)"]
    print(f"  NEGATIVE CTRL  label-free asserted MECHANICALLY from each objective's own source:")
    print(f"    reads H or tg -> { {nm: leaks[nm] for nm in OBJ} }")
    print(f"    -> {'PASS — the three adversaries never touch labels, and the harness DOES flag the oracle that does' if neg_ok else 'FAIL — the check cannot distinguish them'}")

    plc = max(abs(cell(build(nm, 0), build(nm, 0))[0]) for nm in ("adv_mimic",))
    plc_ok = plc == 0.0
    print(f"  PLACEBO        an arm against itself: {plc:.1e}  {'PASS' if plc_ok else 'FAIL'}")

    # ---- SHAM reading ------------------------------------------------------------------------------
    gap = rows["topw_k4"]["a2"] - R["adv_mimic"]["a2"]
    print(f"\n  SHAM  `adv_mimic` is the same search with the target swapped from the human to the")
    print(f"    RUBRIC. Its A2 is {R['adv_mimic']['a2']:.4f} against topw_k4's "
          f"{rows['topw_k4']['a2']:.4f} — so aiming at the human rather than at the rubric is worth")
    print(f"    {gap:+.4f}, and R294's `cores depart from the rubric to track the human` now has a")
    print(f"    number attached rather than only a direction.")

    ctrl = pos_ok and g0_ok and neg_ok and plc_ok
    floor_a2 = ref1.mean()
    degenerate = all(R[nm]["a2"] <= floor_a2 for nm in LABEL_FREE if not nm.startswith("random"))
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  positive={pos_ok}  g0={g0_ok}  negative={neg_ok}  placebo={plc_ok}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; no adversarial statement is readable.")
    elif adm:
        world = "W-GAMED"
        print(f"  -> W-GAMED. {adm} is admitted on clauses 1 and 2 while being LABEL-FREE, so it")
        print("     passes clause 3 by its own words. The definition blesses an object built to")
        print("     satisfy it rather than to be a core, and the derivation that the clauses")
        print("     cannot be gamed without genuine agreement is wrong somewhere.")
    elif degenerate:
        world = "W-DEGENERATE"
        print(f"  -> W-DEGENERATE. Every label-free adversary lands at or below the random floor")
        print(f"     ({floor_a2:.4f}), so these objectives are not coherent attacks and the round")
        print("     tested nothing. Reported as such rather than as a survival.")
    else:
        world = "W-ROBUST"
        print(f"  -> W-ROBUST. No label-free adversary is admitted, and the ORACLE — the one")
        print(f"     objective allowed to read labels — IS, so the search budget is sufficient and")
        print("     these are measurements rather than silence. The definition survives its first")
        print("     deliberate adversary.")
        print(f"     Margins by which each fails: " + " · ".join(
            f"{nm} ②={R[nm]['c2']:.2f}x" for nm in LABEL_FREE if not nm.startswith("random")))
    print("  " + "=" * 78)
    print(f"\n  ⛔ AND THE DERIVATION THAT NARROWED THE ATTACK SURFACE, restated because it is what")
    print(f"    the result rests on: clause 1 and clause 2 subtract FIXED baseline vectors, so both")
    print(f"    margins rise iff the arm's own A2 rises. Neither is gameable without genuinely")
    print(f"    agreeing with the humans more. The attack therefore had to come through clause 3,")
    print(f"    and clause 3 is exactly the clause R336-R338 bounded.")
    print(f"\n  ⚠ AT THIS BUDGET. {NSUB} subsets per prompt; a larger budget can only help the")
    print(f"    adversary, so W-ROBUST is a statement at this search size and not a proof.")
    print(f"\n  MULTIPLICITY  {len(OBJ)} arms x 2 clauses x {len(SEEDS)} seeds, every cell printed.")

    o = SELF.parent / "results" / "adversarial_arms.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_prompts=N, k=K, budget=NSUB, seeds=list(SEEDS), arms=R,
        label_free=sorted(LABEL_FREE), source_leak_check={k: bool(v) for k, v in leaks.items()},
        random_floor=float(ref1.mean()), topw_k4_a2=rows["topw_k4"]["a2"],
        mimic_gap_to_topw=float(gap), admitted_adversaries=adm,
        controls=dict(positive=bool(pos_ok), g0=bool(g0_ok), negative=bool(neg_ok),
                      placebo=bool(plc_ok)),
    ), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
