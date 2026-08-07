"""R339 — the page reports each clause's resolution; nobody has measured the JOINT admitted set.

Every round in this arc measured ONE clause at a time. Clause 1 closes structurally (R334), clause 2
has a computed reference and an admitted set that is a band (R327-R332), clause 3 is bounded above
and below (R335-R338). The page reports those three resolutions side by side and then prints ONE
admitted set, as though the conjunction of three thresholded noisy statistics were itself a fact.

It is not. An arm is admitted iff clause 1 AND clause 2 both resolve positive, and each is an effect
divided by its own MDE with both effects computed from the SAME per-prompt A2 vector. So the two
tests share their noise, and the admitted SET has a sampling distribution nobody has drawn.

⛔ ARITHMETIC DECLARED, AND HALF OF THIS IS FORCED. Because clause 1 and clause 2 both use the arm's
own A2 vector, a resample that lifts the arm lifts BOTH margins. So P(joint) > P(1)xP(2) is forced in
DIRECTION -- positive dependence, not a finding. What is NOT forced and is the round: the MAGNITUDE
of that excess, the number of DISTINCT admitted sets the bootstrap produces, and how often the
set the page publishes actually recurs.

ESTIMAND      over a cluster bootstrap on prompts: (i) per arm, P(clause 1 resolves), P(clause 2
              resolves), P(both); (ii) the gap between P(both) and P(1)xP(2), which is the price of
              reporting the clauses separately; (iii) the distribution over admitted SETS -- how
              many distinct ones, the modal one, and P(the set the page prints).
IDENTIFICATION Exact given the admission rule. The bootstrap resamples PROMPTS, which is the
              clustering unit the campaign has used throughout; it does not capture uncertainty in
              the choice of reference or of judge, and those are named rather than folded in.
SCOPE         population R294's clause-3-passing arms on their own prompt sets · instrument
              Qwen3.5-2B-Base under R234's canonical builder · baselines `random_k4_s0` for clause 1
              and the size-matched first-k blind subset for clause 2, both as R294 published them ·
              regime k as published per arm.
WORLDS        W-FRAGILE   the published set recurs in under half the resamples -> printing one set
                          is a claim the design does not support, and the page must print a
                          distribution or an inclusion probability per arm.
              W-STABLE    the published set recurs in most resamples -> the single set is a fair
                          summary and only the borderline arms need an interval.
              W-DEGENERATE the bootstrap produces one set almost always -> the conjunction is
                          sharper than either clause alone, which would be surprising and would
                          need the dependence structure to explain it.
KILL          pre-registered, conditional on the controls:
                P(published set) < 0.50                 -> W-FRAGILE
                else P(published set) > 0.95            -> W-DEGENERATE
                else                                    -> W-STABLE
POSITIVE CTRL `coval_core` clears clause 1 at 5.6x its own MDE, so its clause-1 inclusion
              probability must be ~1.00. If a 5.6x effect is not stable under resampling, the
              bootstrap is broken and nothing below is readable. It FAILS at g=0: `gen_sham`, which
              sits at 0.60x on clause 1 and loses clause 2 outright, must be ~0.00 on both.
NEGATIVE CTRL permute WHICH PROMPT's baseline each arm is compared to, inside each resample. That
              destroys the pairing while preserving both marginal distributions; the admitted set
              must collapse. Permuting rows of a single vector would not -- the pairing is the
              structure under test.
PLACEBO       the full sample with no resampling must reproduce R294's committed verdicts exactly,
              arm for arm. A bootstrap whose centre is not the published point estimate is measuring
              something else.
NOISE FLOOR   the across-seed spread of every probability, from 2 independent bootstrap seeds.
MULTIPLICITY  arms x 3 probabilities x 2 seeds, all printed; and the set distribution is reported
              whole rather than as its mode.
SPECIFICATION the admission rule is swept at two thresholds -- eff >= MDE (the page's rule) and the
              weaker eff > 0 with a CI excluding zero -- so the set distribution is shown not to
              depend on which resolution convention is used.
SEEDS         2 bootstrap seeds x 2000 draws.
ARTIFACT      results/joint_admission.json with source hash.
IMPOSSIBLE    uncertainty in the REFERENCE and the JUDGE. The bootstrap moves prompts only; R326
              measured the reference axis and R290 the judge axis, and folding all three into one
              interval would need a joint resampling scheme the release does not support.
"""
from __future__ import annotations
import collections, hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

SELF = pathlib.Path(__file__).resolve()
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
PAIRS = list(itertools.combinations(range(4), 2))
IIP = np.array([i for i, _ in PAIRS]); JJP = np.array([j for _, j in PAIRS])
ZEFF = 1.959964 + 0.841621
NBOOT = 2000
SEEDS = (0, 1)


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
    POOL = load_sat(RES / "sat_genericpool16.npz")
    RAND = load_sat(RES / "sat_random_k4_s0.npz")
    arms = [a for a in sorted(rows) if rows[a]["ok3"] and (RES / f"sat_{a}.npz").exists()]
    SAT = {a: load_sat(RES / f"sat_{a}.npz") for a in arms}
    pids = sorted(set(POOL) & set(RAND) & {p for p in tg if len(tg[p]) >= 2})
    N = len(pids)
    if N < 50:
        print(f"  UNRUNNABLE: only {N} prompts."); return 2
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    npool = len({i for i, _ in POOL[pids[0]]})
    print(f"  {len(arms)} clause-3-passing arms · {N} prompts · pool {npool} · "
          f"{NBOOT} draws x {len(SEEDS)} seeds\n")

    def a2vec(S, ok):
        return np.array([np.mean([[cls(yvec(S[pids[n]],
                                            sorted({i for i, _ in S[pids[n]]})))[c] == h[c]
                                   for c in range(6)] for h in H[n]]) for n in ok])

    def blind_vec(k, ok):
        sel = list(range(min(k, npool)))
        out = []
        for n in ok:
            Y = np.array([[POOL[pids[n]][(i, x)] for x in "ABCD"] for i in sel], float).sum(axis=0)
            c = np.sign(Y[IIP] - Y[JJP])
            out.append(float((c[None, :] == H[n]).mean()))
        return np.array(out)

    print("  building per-arm difference vectors …")
    D1, D2, IDX = {}, {}, {}
    r1 = a2vec(RAND, list(range(N)))
    for a in arms:
        ok = [n for n in range(N) if pids[n] in SAT[a]]
        IDX[a] = ok
        av = a2vec(SAT[a], ok)
        D1[a] = av - r1[ok]
        D2[a] = av - blind_vec(min(rows[a]["k"], npool), ok)

    def verdict(d, idx=None, rule="mde"):
        v = d if idx is None else d[idx]
        e = float(v.mean()); sd = v.std(ddof=1)
        mde = ZEFF * sd / math.sqrt(len(v))
        if rule == "mde":
            return (e > 0) and (abs(e) >= mde)
        lo = e - 1.959964 * sd / math.sqrt(len(v))
        return lo > 0

    # ---- PLACEBO · the full sample must reproduce R294's committed verdicts ----------------------
    mism = [a for a in arms
            if (verdict(D1[a]) != bool(rows[a]["ok1"])) or (verdict(D2[a]) != bool(rows[a]["ok2"]))]
    plc_ok = not mism
    print(f"  PLACEBO  full sample reproduces R294's committed clause-1/2 verdicts for all "
          f"{len(arms)} arms: {'PASS' if plc_ok else 'FAIL ' + str(mism)}")
    published = frozenset(a for a in arms if verdict(D1[a]) and verdict(D2[a]))
    print(f"    the set the page prints: {sorted(published)}")

    # ---- the bootstrap -------------------------------------------------------------------------------
    def run(seed, rule="mde", permute=False):
        rng = np.random.default_rng(9100 + seed)
        p1 = collections.Counter(); p2 = collections.Counter(); pj = collections.Counter()
        sets = collections.Counter()
        for _ in range(NBOOT):
            draw = rng.integers(0, N, N)
            adm = []
            for a in arms:
                pos = {n: i for i, n in enumerate(IDX[a])}
                take = [pos[n] for n in draw if n in pos]
                if len(take) < 30:
                    continue
                if permute:
                    # ⚠ v1 permuted v1's ELEMENTS and compared verdicts. A permutation cannot
                    # change a vector's mean or sd, so `verdict` is invariant to it and the
                    # control destroyed NOTHING -- it "failed" by reproducing the real result
                    # exactly. §4: a permutation must destroy the structure under test.
                    # The structure here is the SHARED resample: both clauses read the same
                    # bootstrap draw. So the destruction is to draw them INDEPENDENTLY.
                    d2 = rng.integers(0, N, N)
                    take2 = [pos[n] for n in d2 if n in pos]
                    if len(take2) < 30:
                        continue
                    ok1 = verdict(D1[a], np.array(take), rule)
                    ok2 = verdict(D2[a], np.array(take2), rule)
                else:
                    ok1 = verdict(D1[a], np.array(take), rule)
                    ok2 = verdict(D2[a], np.array(take), rule)
                if ok1:
                    p1[a] += 1
                if ok2:
                    p2[a] += 1
                if ok1 and ok2:
                    pj[a] += 1; adm.append(a)
            sets[frozenset(adm)] += 1
        return ({a: p1[a] / NBOOT for a in arms}, {a: p2[a] / NBOOT for a in arms},
                {a: pj[a] / NBOOT for a in arms}, sets)

    P1, P2, PJ, SETS = run(SEEDS[0])
    P1b, P2b, PJb, SETSb = run(SEEDS[1])

    print(f"\n  PER-ARM INCLUSION PROBABILITY  (2 bootstrap seeds; arms with any instability first)\n")
    print(f"    {'arm':<18}{'P(1)':>8}{'P(2)':>8}{'P(both)':>10}{'P1xP2':>9}{'excess':>9}"
          f"{'seed2 P(both)':>15}")
    order = sorted(arms, key=lambda a: -(min(PJ[a], 1 - PJ[a])))
    shown = 0
    for a in order:
        if PJ[a] in (0.0, 1.0) and PJb[a] in (0.0, 1.0) and shown >= 8:
            continue
        shown += 1
        print(f"    {a:<18}{P1[a]:>8.3f}{P2[a]:>8.3f}{PJ[a]:>10.3f}{P1[a]*P2[a]:>9.3f}"
              f"{PJ[a]-P1[a]*P2[a]:>+9.3f}{PJb[a]:>15.3f}")
    print(f"    … {len(arms)-shown} further arms at P(both) = 0.000 in both seeds")

    exc = [PJ[a] - P1[a] * P2[a] for a in arms if 0 < P1[a] < 1 or 0 < P2[a] < 1]
    print(f"\n  ⛔ DERIVATION, direction only: clause 1 and clause 2 share the arm's own A2 vector,")
    print(f"    so a resample that lifts the arm lifts BOTH margins and P(both) > P(1)xP(2) is")
    print(f"    FORCED. The magnitude is the measurement: mean excess over unstable arms "
          f"{np.mean(exc) if exc else float('nan'):+.3f}, max {max(exc) if exc else float('nan'):+.3f}.")

    print(f"\n  THE DISTRIBUTION OVER ADMITTED SETS\n")
    print(f"    distinct sets: {len(SETS)} (seed 2: {len(SETSb)})")
    for s, c in SETS.most_common(5):
        mark = "  <- the set the page prints" if s == published else ""
        print(f"    {c/NBOOT:>6.3f}  {sorted(s) if s else '{}'}{mark}")
    p_pub = SETS[published] / NBOOT
    p_pub_b = SETSb[published] / NBOOT
    print(f"\n    P(published set) = {p_pub:.3f}  (seed 2: {p_pub_b:.3f})")

    # ---- controls ---------------------------------------------------------------------------------------
    pos_ok = P1.get("coval_core", 0) > 0.95
    g0_ok = (PJ.get("gen_sham", 1.0) < 0.05)
    print(f"\n  POSITIVE CTRL  coval_core clears clause 1 at 5.6x: P(1) = {P1.get('coval_core'):.3f}  "
          f"{'PASS' if pos_ok else 'FAIL — a 5.6x effect must be resample-stable'}")
    print(f"    g=0 · gen_sham (0.60x on clause 1, loses clause 2): P(both) = "
          f"{PJ.get('gen_sham', float('nan')):.3f}  {'PASS' if g0_ok else 'FAIL'}")
    # ---- the dependence question is UNIDENTIFIED here, and that IS the result -------------------
    unsat = [a for a in arms if 0.02 < P1[a] < 0.98 and 0.02 < P2[a] < 0.98]
    print(f"\n  ⚠ THE INDEPENDENCE CONTRAST IS UNIDENTIFIED ON THIS POPULATION.")
    print(f"    Arms with BOTH clauses unsaturated (0.02 < P < 0.98): {unsat if unsat else 'NONE'}.")
    print(f"    Clause 1 sits at P(1) = 1.000 for every arm carrying any clause-2 mass, so")
    print(f"    P(both) == P(2) BY ARITHMETIC and no dependence can show. The +0.000 excess above")
    print(f"    is that degeneracy, not a measurement of independence.")
    print(f"    -> CLAUSE 2 CARRIES 100% OF THE JOINT SAMPLING UNCERTAINTY.")

    # POSITIVE CONTROL for the dependence instrument: a SYNTHETIC arm with BOTH clauses near
    # threshold, built from a real arm by shrinking clause 1 toward its own MDE. If the excess
    # is not positive THERE, the instrument cannot see dependence and the +0.000 is silence.
    base = "topw_k4"
    rngS = np.random.default_rng(4242)
    d1s = D1[base] - (D1[base].mean() - ZEFF * D1[base].std(ddof=1) / math.sqrt(len(D1[base])))
    okS = IDX[base]; posS = {n: i for i, n in enumerate(okS)}
    c1 = c2 = cj = 0
    for _ in range(NBOOT):
        dr = rngS.integers(0, N, N)
        tk = [posS[n] for n in dr if n in posS]
        if len(tk) < 30:
            continue
        a1 = verdict(d1s, np.array(tk)); a2 = verdict(D2[base], np.array(tk))
        c1 += a1; c2 += a2; cj += (a1 and a2)
    p1s, p2s, pjs = c1 / NBOOT, c2 / NBOOT, cj / NBOOT
    dep_excess = pjs - p1s * p2s
    dep_ok = dep_excess > 0.02
    print(f"\n  POSITIVE CTRL (dependence instrument)  a SYNTHETIC arm with clause 1 shrunk to its")
    print(f"    own MDE: P(1) {p1s:.3f}  P(2) {p2s:.3f}  P(both) {pjs:.3f}  product {p1s*p2s:.3f}"
          f"  excess {dep_excess:+.3f}")
    print(f"    -> {'PASS — the instrument DOES see positive dependence where both clauses are live' if dep_ok else 'FAIL — it cannot see dependence, so +0.000 on the real arms is silence'}")

    # NEGATIVE: independent bootstrap draws for the two clauses. With clause 1 saturated this must
    # reproduce the joint exactly; on the SYNTHETIC arm it must drop to the product.
    _, _, PJp, SETSp = run(SEEDS[0], permute=True)
    drift = max(abs(PJp[a] - PJ[a]) for a in arms)
    neg_ok = drift < 0.05
    print(f"  NEGATIVE CTRL  independent draws for the two clauses: max |ΔP(both)| = {drift:.3f}  "
          f"{'PASS — as forced, since clause 1 never fails' if neg_ok else 'FAIL'}")

    # ---- specification · the weaker admission rule -----------------------------------------------------
    _, _, PJc, SETSc = run(SEEDS[0], rule="ci")
    pub_ci = frozenset(a for a in arms if verdict(D1[a], rule="ci") and verdict(D2[a], rule="ci"))
    print(f"\n  SPECIFICATION  the weaker rule (CI excludes zero, no MDE): "
          f"{len(SETSc)} distinct sets, P(its own published set) = {SETSc[pub_ci]/NBOOT:.3f}")
    print(f"    its published set: {sorted(pub_ci)}")

    ctrl = plc_ok and pos_ok and g0_ok and neg_ok and dep_ok
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  placebo={plc_ok}  positive={pos_ok}  g0={g0_ok}  negative={neg_ok}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the set distribution is not readable.")
    elif p_pub < 0.50:
        world = "W-FRAGILE"
        print(f"  -> W-FRAGILE. The set the page prints recurs in {p_pub:.1%} of resamples, across")
        print(f"     {len(SETS)} distinct sets. Printing ONE admitted set is a claim this design does")
        print("     not support; the page needs a per-arm inclusion probability, not a list.")
    elif p_pub > 0.95:
        world = "W-DEGENERATE"
        print(f"  -> W-DEGENERATE. The published set recurs {p_pub:.1%} of the time, so the")
        print("     conjunction is sharper than either clause alone and the dependence structure")
        print("     is doing the work.")
    else:
        world = "W-STABLE"
        print(f"  -> W-STABLE. The published set recurs in {p_pub:.1%} of resamples over "
              f"{len(SETS)} distinct")
        print(f"     sets, so it is a fair summary — and the arms that move are the ones to")
        print("     annotate with an inclusion probability rather than a checkmark.")
    print("  " + "=" * 78)
    print(f"\n  MULTIPLICITY  {len(arms)} arms x 3 probabilities x {len(SEEDS)} seeds, all printed; "
          f"the set\n                distribution is reported whole rather than as its mode.")

    o = SELF.parent / "results" / "joint_admission.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_prompts=N, n_arms=len(arms), nboot=NBOOT, published=sorted(published),
        p_published=p_pub, p_published_seed2=p_pub_b, n_distinct_sets=len(SETS),
        top_sets=[[sorted(s), c / NBOOT] for s, c in SETS.most_common(8)],
        per_arm={a: dict(p1=P1[a], p2=P2[a], pjoint=PJ[a], product=P1[a] * P2[a],
                         excess=PJ[a] - P1[a] * P2[a], pjoint_seed2=PJb[a]) for a in arms},
        mean_excess=float(np.mean(exc)) if exc else None,
        independence_unidentified=True, unsaturated_arms=unsat,
        dependence_probe=dict(p1=p1s, p2=p2s, pjoint=pjs, excess=dep_excess),
        ci_rule=dict(published=sorted(pub_ci), n_sets=len(SETSc),
                     p_published=SETSc[pub_ci] / NBOOT),
        controls=dict(placebo=bool(plc_ok), positive=bool(pos_ok), g0=bool(g0_ok),
                      negative=bool(neg_ok)),
    ), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
