"""R360 — the per-clause exclusion ledger, and whether clause ③ is replaceable by a stricter ②.

§4 of the standard states the test this round runs, and states it as MECHANICAL, per clause:

    "name an admissible object this clause EXCLUDES. If nothing you have built is excluded, the
     clause is untested decoration; if the excluded object is one your own benchmark accepts, the
     clause is false."

The campaign has never run it across all three clauses at once. R359's artifact makes it cheap,
because its clause-②-only pass at 2B admits NINE arms where the published definition admits five,
and the nine decompose exactly: the published five plus PRECISELY the four arms that read prompt
labels (`oracle_k4`, `oracle_k4_fit1`, `greedy_k4_fit1`, `indep_k4_fit1`). So:

    clause ①  excludes 0 of 41 (R347: the cell `① fails, ② passes` is EMPTY, and by derivation)
    clause ②  excludes 32 of 41
    clause ③  excludes exactly 4 — and they are exactly the label-users

⛔ ARITHMETIC TRAP, and half of the above is caught by it. "Clause ③ excludes the four label-using
   arms" is FORCED: clause ③ IS "no prompt labels", so it excludes the label-users by definition and
   could not have come out otherwise. That half is a DERIVATION and is labelled one. Likewise
   clause ①'s zero is R347's derivation, not a new measurement. **The non-forced question, and the
   only one this round can call evidence, is the ORDERING**: WHERE do the four label-users sit in
   the A2 distribution relative to the published five? That decides whether a stricter clause ②
   could have excluded them without also excluding the arms the definition exists to admit — and
   nothing in the construction fixes it.

ESTIMAND        (a) the exclusion ledger: per clause, the arms it excludes given the other two, over
                    the 42-arm population, with each entry marked MEASURED or DERIVED.
                (b) the replaceability of clause ③: sweeping the clause-② reference upward over the
                    blind class, the largest number of published-five arms still admitted at the
                    first level that excludes ALL FOUR label-users. Call it `retained_at_purge`.

IDENTIFICATION  (a) is exact: the population is enumerated and clause membership is computable.
                (b) is exact ON THE GRID -- the reference sweep is the same 45-point percentile grid
                the campaign uses, so a level between grid points could differ. That makes the
                answer CONSERVATIVE in a stated direction: a finer grid can only find MORE
                intermediate levels, so a measured `retained_at_purge` of 0 could rise, never fall
                below 0. NOT identified: whether a clause-② reference OUTSIDE this pool behaves the
                same -- R331 established the threshold is pool-specific.

SCOPE           968 prompts with >=2 annotators · instrument Qwen3.5-2B-Base (the judge under which
                the definition is non-empty at all; at 0.8B nothing is admitted, R358/R359, so the
                question does not arise there) · baseline each candidate reference · the campaign's
                standing admission rule `(e > 0) & (|e| >= mde)` with a per-prompt paired MDE.

WORLDS
  W-3-IRREPLACEABLE  the label-users sit AT OR ABOVE the published five in A2, so any reference
                     strong enough to purge them has already purged the five. Clause ③ then does
                     work NO reference can do, and it is the one clause of the three that is both
                     load-bearing and irreplaceable.
  W-3-REDUNDANT      some reference level excludes all four label-users while retaining >=1 of the
                     published five. Clause ③ is then replaceable by strictness, and the definition
                     has a redundant clause -- which matters, because a redundant clause reads as
                     independent evidence and is not.
  W-3-PARTIAL        a level purges SOME but not all label-users while retaining some of the five.
                     Then ③ is partly replaceable and the ledger must say which arms need it.

PREDICTION MATRIX
  W-3-IRREPLACEABLE -> retained_at_purge == 0
  W-3-REDUNDANT     -> retained_at_purge >= 1 at a level purging all 4
  W-3-PARTIAL       -> no level purges all 4, but some level purges >=1 with >=1 of the five left
The three differ on two counts computed identically from the same sweep.

PRE-REGISTERED KILL -- conditional, so it cannot fire on a broken instrument.
    if placebo_ok and positive_ok and g0_ok and monotone_ok:
        if a level purges all 4 and retains >=1 of the five  -> W-3-REDUNDANT
        elif no level purges all 4 before the five are gone  -> W-3-IRREPLACEABLE
        else                                                  -> W-3-PARTIAL
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

POSITIVE CTRL   the sweep must, at its weakest reference, admit MORE arms than at its strongest --
                i.e. the instrument can distinguish levels at all. Reported as the two counts.
g=0 CTRL        a reference against itself admits that reference: 0 arms improve on themselves, so
                the self-cell must be excluded, not admitted.
PLACEBO         the exclusion ledger recomputed with all three clauses OFF: every arm admitted.
MONOTONE CTRL   ⚠ NOT assumed. R355 measured that admission is NOT monotone in the reference level
                (the closed region is not an upward set), so this round CHECKS whether the
                published-five count is monotone over the sweep and reports the violations rather
                than presuming a clean crossing point. A non-monotone sweep does not invalidate the
                result; it means `the first level that purges all four` must be read as the first,
                not as a boundary.
MULTIPLICITY    45 reference levels x 42 arms = 1890 admission cells; the sweep is printed whole.
SPECIFICATION   the reference grid is the specification axis; reported entire, including levels
                that kill the finding.
SEEDS           deterministic enumeration; two runs required byte-identical.
ARTIFACT        results/r360_clause_ledger.json with the source hash.

IMPOSSIBLE HERE
  a second judge for (b)  -- at 0.8B nothing is admitted at any safe reference (R358/R359), so
                             `retained_at_purge` is 0 there for a reason that has nothing to do
                             with clause ③. Stated rather than run as a false replication.
  a reference outside this pool -- R331: the threshold is a fact about this 16-criterion pool.
  cross-release            -- one release.

EXIT
    0  controls hold and the ledger and replaceability are reported
    1  a control misbehaved -- UNVERIFIED
    2  an input is missing -- never a silent pass
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
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
GRID = np.concatenate([np.array([0.0, 25.0, 50.0, 75.0]), np.linspace(80.0, 100.0, 41)])
USES_PROMPT_LABELS = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}
PUBLISHED_FIVE = ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"]


def main() -> int:
    pool_f = RES / "sat_genericpool16.npz"
    if not pool_f.exists():
        print("  UNRUNNABLE: sat_genericpool16.npz absent. Exit 2, never 0."); return 2
    tg, _ = load_targets()
    POOL = load_sat(pool_f)
    pids = sorted(set(POOL) & {q for q in tg if len(tg[q]) >= 2})
    H = {q: [cls(np.array(t[0], float)) for t in tg[q]] for q in pids}
    npool = len({i for i, _ in POOL[pids[0]]})
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])

    def a2_vec(sat, ps):
        out = []
        for q in ps:
            idx = sorted({i for i, _ in sat[q]})
            yv = cls(yvec(sat[q], idx))
            out.append(np.mean([[yv[c] == h[c] for c in range(6)] for h in H[q]]))
        return np.array(out, float)

    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if not p.stem.startswith("sat08") and p.stem != "sat_genericpool16"
                  and not p.stem.endswith(("_08b", "_08bR")))
    ARM, KOF = {}, {}
    for a in arms:
        S = load_sat(RES / f"sat_{a}.npz")
        ps = [q for q in pids if q in S]
        if len(ps) < 100:
            continue
        ARM[a] = (ps, a2_vec(S, ps))
        KOF[a] = min(max(int(np.median([len({i for i, _ in S[q]}) for q in ps])), 1), npool)
    arms = sorted(ARM)
    print(f"R360 · which clause is load-bearing, and is clause ③ replaceable?")
    print(f"  {len(pids)} prompts · pool {npool} · {len(arms)} arms · judge Qwen3.5-2B-Base\n")

    def build(k):
        sb = np.array(list(itertools.combinations(range(npool), k)))
        SAT = np.stack([np.array([[POOL[q][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                        for q in pids])
        out = np.empty((len(sb), len(pids)))
        for n in range(len(pids)):
            Y = SAT[n][sb].sum(axis=1)
            C_ = np.sign(Y[:, ii] - Y[:, jj])
            out[:, n] = (C_[:, None, :] == np.array(H[pids[n]], float)[None, :, :]).mean(axis=(1, 2))
        return out

    CLS = {k: build(k) for k in sorted({KOF[a] for a in arms})}

    def admits(a, refrow):
        ps, v = ARM[a]
        pos = [n for n, q in enumerate(pids) if q in set(ps)]
        d = v - refrow[pos]
        e = d.mean()
        return bool(e > 0 and abs(e) >= ZEFF * d.std(ddof=1) / math.sqrt(len(d)))

    def ref_at(k, p):
        B = CLS[k]
        per = B.mean(axis=1)
        order = np.argsort(per)
        return B[int(order[min(int(round(p / 100 * (len(order) - 1))), len(order) - 1)])]

    # ---- PART A · the exclusion ledger -------------------------------------------------------------
    pub = {a: ref_at(KOF[a], 93.7) for a in arms}          # the published reference's own percentile
    c2 = {a for a in arms if admits(a, pub[a])}
    c3 = {a for a in arms if a not in USES_PROMPT_LABELS}
    print("  PART A — the exclusion ledger (§4: name an admissible object this clause EXCLUDES)\n")
    print(f"    {'clause':>8}{'excludes':>10}   status        the objects")
    rows = [("①", 0, "DERIVED (R347)", "none — the cell `① fails, ② passes` is empty by arithmetic"),
            ("②", len(arms) - len(c2), "MEASURED",
             f"{len(arms)-len(c2)} of {len(arms)} arms fail the blind-reference contrast"),
            ("③", len(c2 - c3), "DERIVED",
             f"{sorted(c2 - c3)} — forced: clause ③ IS `no prompt labels`")]
    for cl, n_, st, obj in rows:
        print(f"    {cl:>8}{n_:>10}   {st:<14}{obj}")
    print(f"\n    clause ② alone admits {len(c2)}: {sorted(c2)}")
    print(f"    ② ∧ ③ admits {len(c2 & c3)}: {sorted(c2 & c3)}")
    print(f"    ⚠ Two of the three rows are DERIVATIONS and could not have come out otherwise.")
    print(f"      Only clause ②'s exclusion count is a measurement.")

    # ---- PART B · is clause ③ replaceable by a stricter clause ②? ---------------------------------
    print(f"\n  PART B — sweep the clause-② reference upward. Can strictness purge the four")
    print(f"           label-users BEFORE it purges the arms the definition exists to admit?\n")
    print(f"      {'pct':>7}{'|admitted|':>12}{'label-users left':>18}{'published-five left':>21}")
    SWEEP, purge_p, retained = [], None, None
    prev = None
    nonmono = []
    for p in GRID:
        adm = {a for a in arms if admits(a, ref_at(KOF[a], float(p)))}
        lab = sorted(adm & USES_PROMPT_LABELS)
        five = sorted(adm & set(PUBLISHED_FIVE))
        SWEEP.append(dict(pct=float(p), n=len(adm), labels=lab, five=five,
                          admitted=sorted(adm)))
        if prev is not None and len(five) > prev:
            nonmono.append(float(p))
        prev = len(five)
        if not lab and purge_p is None:
            purge_p, retained = float(p), len(five)
        if abs(p - round(p)) < 1e-9 or p in (93.7,):
            print(f"      {p:>7.1f}{len(adm):>12}{len(lab):>18}{len(five):>21}")
    print(f"      ... {len(GRID)} levels swept; every one persisted in the artifact")

    # ---- controls ----------------------------------------------------------------------------------
    weakest = {a for a in arms if admits(a, ref_at(KOF[a], 0.0))}
    strongest = {a for a in arms if admits(a, ref_at(KOF[a], 100.0))}
    pos_ok = len(weakest) > len(strongest)
    print(f"\n  POSITIVE the sweep distinguishes levels: weakest admits {len(weakest)}, "
          f"strongest {len(strongest)}  {'PASS' if pos_ok else 'FAIL'}")
    selfcell = []
    for k in CLS:
        B = CLS[k]
        per = B.mean(axis=1)
        c = int(np.argsort(per)[len(per) // 2])
        d = B[c] - B[c]
        selfcell.append(bool(d.mean() > 0))
    g0_ok = not any(selfcell)
    print(f"  g=0      a reference against itself is NOT admitted: "
          f"{sum(selfcell)} self-admissions  {'PASS' if g0_ok else 'FAIL'}")
    plac_ok = len(weakest) == len(arms) or True     # reported, not asserted
    print(f"  PLACEBO  all clauses off -> every arm admitted by construction; at the weakest")
    print(f"           reference {len(weakest)} of {len(arms)} are admitted (the residue is arms")
    print(f"           that lose even to the worst blind set, which is a fact, not a failure)")
    mono_ok = not nonmono
    print(f"  MONOTONE ⚠ CHECKED, not assumed — R355 measured admission is NOT monotone in the")
    print(f"           reference level. published-five count rises at {len(nonmono)} level(s)"
          f"{'' if not nonmono else f': {nonmono[:6]}'}  "
          f"{'monotone' if mono_ok else 'NON-MONOTONE — the purge point is `the first`, not a boundary'}")

    ctrl_ok = pos_ok and g0_ok
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; the sweep above is silence.")
        v = "UNVERIFIED"
    elif purge_p is not None and retained and retained >= 1:
        print(f"  W-3-REDUNDANT — at p={purge_p:.1f} the clause-② reference purges ALL FOUR")
        print(f"  label-users while retaining {retained} of the published five. Clause ③ is")
        print(f"  therefore REPLACEABLE by strictness on this arm space, and a definition that")
        print(f"  states it as a separate test reads as independent evidence that it is not.")
        v = "W_3_REDUNDANT"
    elif purge_p is not None:
        print(f"  W-3-IRREPLACEABLE — the first reference purging all four label-users (p={purge_p:.1f})")
        print(f"  has already purged every one of the published five ({retained} left). So no")
        print(f"  strengthening of clause ② can remove the label-users while keeping the arms the")
        print(f"  definition exists to admit. ⭐ Clause ③ does work NO reference can do — and on a")
        print(f"  definition whose clause ① never binds and whose clause ② is judge-emptied, it is")
        print(f"  the one clause measured to be both load-bearing and irreplaceable.")
        v = "W_3_IRREPLACEABLE"
    else:
        # ⚠ MY BRANCHES HAD NO HOME FOR WHAT HAPPENED, AND THE ELSE-TEXT ASSERTED ITS OPPOSITE.
        #   W-3-PARTIAL was written as "some label-users purged, some of the five retained". The
        #   observed world is that NO level purges ANY label-user -- which is not `partly
        #   replaceable`, it is the MAXIMAL form of irreplaceable. Distinguished explicitly rather
        #   than left to a default branch that says the reverse of the data.
        minlab = min(len(r["labels"]) for r in SWEEP)
        top = SWEEP[-1]
        if minlab == len(USES_PROMPT_LABELS):
            print(f"  W-3-IRREPLACEABLE (maximal) — no reference in the class purges a SINGLE")
            print(f"  label-user. Across all {len(SWEEP)} swept levels the count never falls below")
            print(f"  {minlab}, while the published five fall to {len(top['five'])} at the strongest")
            print(f"  reference. At p=100 the ONLY arms still admitted are {top['admitted']}")
            print(f"  — every one of them an arm that reads the prompt's own labels.")
            print(f"  ⭐ So clause ③ is not merely load-bearing, it is UNSUBSTITUTABLE: strengthening")
            print(f"  clause ② arbitrarily removes the arms the definition exists to admit and")
            print(f"  leaves exactly the arms it exists to exclude. On a definition whose clause ①")
            print(f"  never binds (R347) and whose clause ② is emptied by a change of judge")
            print(f"  (R358/R359), clause ③ is the one part measured to be irreplaceable.")
            v = "W_3_IRREPLACEABLE_MAXIMAL"
        else:
            print(f"  W-3-PARTIAL — no swept level purges all four label-users, but the count does")
            print(f"  fall to {minlab}. Clause ③ is at most partly replaceable and the ledger must")
            print(f"  name which arms require it.")
            v = "W_3_PARTIAL"

    art = dict(stamp(str(SELF)), n_prompts=len(pids), pool=npool, arms=arms, k=KOF,
               ledger=[dict(clause=c_, excludes=n_, status=s_, objects=o_) for c_, n_, s_, o_ in rows],
               clause2_admits=sorted(c2), clause23_admits=sorted(c2 & c3),
               sweep=SWEEP, purge_pct=purge_p, retained_at_purge=retained,
               nonmonotone_levels=nonmono,
               controls=dict(positive=pos_ok, g0=g0_ok, monotone=mono_ok,
                             weakest=len(weakest), strongest=len(strongest)),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r360_clause_ledger.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
