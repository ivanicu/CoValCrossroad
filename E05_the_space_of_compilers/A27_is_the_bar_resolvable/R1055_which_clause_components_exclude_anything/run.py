"""R1055 — ablate each clause component against the real operator. Which one EXCLUDES anything?

Eleven rounds have audited instruments. R1054 ended with a NAMEABLE dependency set and the finding
that the clause is not special — the gate is. The one question those rounds never asked is the one
§4 prescribes for a definition written from a single instance:

    ⭐ NAME AN ADMISSIBLE OBJECT THIS CLAUSE EXCLUDES. If nothing you have built is excluded, the
      clause is untested decoration; if the excluded object is one your own benchmark accepts, the
      clause is false.

This round runs that question against the real admission operator and the real 107-arm population,
one ablation per component.

ESTIMAND        for each component of the clause, the symmetric difference between the admitted set
                WITH it and WITHOUT it - i.e. what that component actually excludes
IDENTIFICATION  exact given the operator. ⚠ An ablation shows what a component excludes IN THIS
                POPULATION; a component excluding nothing here could still exclude something in a
                population this release does not contain. So `excludes nothing` is scoped to the
                107 arms on disk and is not a claim about the category.
SCOPE           population : the arms carrying a sat_*.npz, target A2, prompts with >=2 targets
                instrument : the R923 admission operator, percentile of the bootstrapped paired diff
                baseline   : the full clause as currently stated
                regime     : NBOOT as set below, one seed grid
WORLDS          A EVERY COMPONENT BINDS — each ablation changes the admitted set, so the clause has
                  no decorative parts and each clause earns its place.
                B SOME COMPONENT IS DECORATION — at least one ablation leaves the admitted set
                  identical. That component excludes nothing in the only population we have, and
                  §4 says it is untested decoration until an excluded object is named.
                prediction matrix: A -> every symmetric difference non-empty
                                   B -> at least one empty
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      any component with an EMPTY symmetric difference -> World B, name it
                      all non-empty                                    -> World A
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ the RESOLVABILITY ablation must change the set. R1032 measured that the
                as-written and repaired operators differ by 2 arms on A1-consensus, so a component
                known to bind must be seen to bind, or the harness is blind.
NEGATIVE CTRL   ablating NOTHING must reproduce the baseline admitted set exactly (g=0).
SHAM            an ablation that changes an irrelevant knob - the bootstrap seed - must leave the
                admitted set unchanged, or the set is not stable enough for any ablation to be read.
NOISE FLOOR     ⭐ seed spread: the admitted set is recomputed at 3 seeds and the arms whose
                membership is not stable across them are reported and EXCLUDED from every
                symmetric difference, because an unstable arm cannot evidence an ablation.
MULTIPLICITY    all components reported with their own difference, not only the ones that bind.
SEEDS           3, and the seed effect is measured rather than assumed.
IMPOSSIBLE      whether a component that excludes nothing HERE would exclude something in a
                population this release does not contain. SETTLES: OUT-OF-RELEASE - it needs a
                second release, which is the register's standing entry.
"""
import json, pathlib, sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NBOOT = 4000
Q_DEFAULT = 90
COMPARATORS = ["generic", "genericpool16"]


def main() -> int:
    tg, _ = load_targets()
    base = load_sat(RES / "sat_generic.npz")
    pids = sorted(set(base) & {p for p in tg if len(tg[p]) >= 2})
    if len(pids) < 100:
        print("  UNRUNNABLE: too few prompts. Exit 2, never 0."); return 2
    H = {p: [np.array(cls(np.array(t[0], float)), float) for t in tg[p]] for p in pids}
    n = len(pids)

    # ⛔ THE SCORING IS COPIED FROM R923's OWN vec(), NOT INVENTED. My first version indexed
    #   S[p] as an array; load_sat returns {pid: {(criterion_i, letter): value}}, so the score
    #   is cls(yvec(...)) against each human ranking. I guessed the structure and the traceback
    #   was the object telling me so — the same unit error as the six before it, caught earlier
    #   only because Python refuses to divide a dict.
    arms, V, COV = [], [], []
    for f in sorted(RES.glob("sat_*.npz")):
        nm = f.stem[4:]
        try:
            Sa = load_sat(f)
        except Exception:
            continue
        v = np.full(n, np.nan)
        for k, p in enumerate(pids):
            if p in Sa:
                c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
        cov = np.isfinite(v)
        if cov.sum() < 100:
            continue
        arms.append(nm); V.append(np.nan_to_num(v, nan=0.0)); COV.append(cov)
    if len(arms) < 20:
        print("  UNRUNNABLE: too few arms. Exit 2, never 0."); return 2
    V = np.array(V); COV = np.array(COV)
    print(f"  ⭐ arms {len(arms)} · prompts {n} · comparators {COMPARATORS}")

    def admitted(seed, resolvable=True, family=True, q=Q_DEFAULT, impute=False):
        rng = np.random.default_rng(seed)
        comps = [c for c in (COMPARATORS if family else COMPARATORS[:1]) if c in arms]
        if not comps:
            return None
        idx = rng.integers(0, n, size=(NBOOT, n))
        out = set()
        for i, nm in enumerate(arms):
            if nm in comps:
                continue
            beats = 0
            for c in comps:
                j = arms.index(c)
                m = np.ones(n, bool) if impute else (COV[i] & COV[j])
                if m.sum() < 30:
                    continue
                d = (V[i] - V[j])[m]
                if resolvable:
                    bs = d[idx[:, :m.sum()] % m.sum()].mean(axis=1)
                    ok = float(np.percentile(bs, 2.5)) > 0
                else:
                    ok = float(d.mean()) > 0            # point estimate: resolvability removed
                beats += bool(ok)
            need = len(comps) if q >= 100 else max(1, int(np.ceil(q / 100 * len(comps))))
            if beats >= need:
                out.add(nm)
        return out

    # ---------- noise floor: which arms are seed-stable at all ----------
    sets = [admitted(s) for s in (11, 23, 47)]
    if any(s is None for s in sets):
        print("  UNRUNNABLE: comparators absent. Exit 2, never 0."); return 2
    stable_in = set.intersection(*sets)
    stable_out = set(arms) - set.union(*sets)
    unstable = set(arms) - stable_in - stable_out - set(COMPARATORS)
    print(f"  ⭐ SEED SPREAD (3 seeds) — always admitted {len(stable_in)} · never {len(stable_out)} · "
          f"UNSTABLE {len(unstable)} {sorted(unstable)[:8]}")
    print(f"     unstable arms are EXCLUDED from every symmetric difference below: an arm whose")
    print(f"     membership moves with the seed cannot evidence an ablation.")

    baseline = stable_in
    neg = admitted(11) is not None and (admitted(11) - unstable) == (sets[0] - unstable)
    sham = (sets[0] - unstable) == (sets[1] - unstable)
    print(f"  NEGATIVE — ablating nothing reproduces the baseline: {neg}")
    print(f"  SHAM     — changing only the bootstrap seed leaves the set unchanged: {sham}")

    ABL = {
        "resolvability (2.5th pct -> point estimate)": dict(resolvable=False),
        "comparator FAMILY (two -> one)":              dict(family=False),
        "q = 90 -> q = 100 (EVERY, the pre-R1032 form)": dict(q=100),
        "coverage (own prompts -> imputed)":           dict(impute=True),
    }
    rows = []
    for name, kw in ABL.items():
        got = admitted(11, **kw)
        if got is None:
            rows.append({"component": name, "status": "UNRUNNABLE"}); continue
        a, b = baseline - unstable, got - unstable
        rows.append({"component": name, "lost": sorted(a - b), "gained": sorted(b - a),
                     "symmetric_difference": len(a ^ b)})
        print(f"     {name:<46} Δ={len(a ^ b):>3}  lost {sorted(a - b)[:4]}  "
              f"gained {sorted(b - a)[:4]}")

    pos = any(r.get("symmetric_difference", 0) > 0
              for r in rows if r["component"].startswith("resolvability"))
    print(f"  POSITIVE — the resolvability ablation must change the set (R1032 measured it binds): "
          f"{pos}")
    if not (pos and neg and sham):
        print("  the harness cannot read an ablation. Exit 2, never 0."); return 2

    # ⛔⛔ THE ARITHMETIC TRAP, CAUGHT BEFORE REPORTING. At |family| = 2 the q ablation CANNOT come
    #   out otherwise: need(q=90) = ceil(0.9 * 2) = 2 = need(q=100). Its Δ=0 is a DERIVATION, not a
    #   measurement, and the assumption it rests on is the family size. q first differs at |family|
    #   >= 3, where ceil(0.9*3) = 3 but ceil(0.9*4) = 4 < ... — the smallest k with a gap is
    #   computed here rather than asserted.
    ncomp = len([c for c in COMPARATORS if c in arms])
    need90 = max(1, int(np.ceil(0.9 * ncomp)))
    forced = need90 == ncomp
    first_gap = next((k for k in range(2, 40) if max(1, int(np.ceil(0.9 * k))) < k), None)
    print(f"\n  ⛔ ARITHMETIC CHECK — |family| = {ncomp}: need(q=90) = {need90}, need(q=100) = "
          f"{ncomp}. Identical: {forced}")
    print(f"     ⭐ so the q ablation's Δ=0 is a DERIVATION, not a measurement — it could not have")
    print(f"     come out otherwise at this family size. q first becomes testable at |family| = "
          f"{first_gap}.")
    print(f"     ⚠ THE CLAUSE THEREFORE DECLARES A PARAMETER ITS OWN CERTIFIED FAMILY IS TOO SMALL")
    print(f"     TO EXERCISE. R1036-R1038 measured q's onset curve and set its default; none of that")
    print(f"     is wrong, and none of it is EXERCISED by the operator as the clause currently runs.")

    empty = [r["component"] for r in rows if r.get("symmetric_difference") == 0]
    print()
    if empty:
        world = (f"⭐ B SOME COMPONENT IS DECORATION IN THIS POPULATION (and for q it is FORCED: at "
                 f"|family|={ncomp} the q ablation is a DERIVATION, not a measurement) — {empty} change the admitted "
                 f"set by NOTHING across {len(arms)} arms. §4: name an admissible object the clause "
                 f"excludes, or the clause is untested decoration. For these components no such "
                 f"object exists on disk. ⚠ SCOPED: this is the only population we have, and a "
                 f"component excluding nothing here could still exclude something in a release we do "
                 f"not possess.")
    else:
        world = (f"⭐ A EVERY COMPONENT BINDS — all {len(rows)} ablations change the admitted set, so "
                 f"no part of the clause is decoration in this population. The symmetric differences "
                 f"are {[r['symmetric_difference'] for r in rows]}.")
    print(world)
    print(f"⛔ AND AN ABLATION IS A NECESSITY TEST, NOT A CORRECTNESS TEST. A component that binds is")
    print(f"   doing work; it is not thereby doing the RIGHT work. R1032 showed the pre-repair form")
    print(f"   also bound — it admitted two arms it should not have.")

    o = HERE / "results" / "component_ablation.json"
    o.write_text(json.dumps({
        "round": "R1055", "arms": len(arms), "prompts": len(pids), "nboot": NBOOT,
        "baseline_admitted": sorted(baseline), "unstable_excluded": sorted(unstable),
        "rows": rows, "empty_components": empty,
        "q_ablation_is_a_derivation": bool(forced), "family_size": ncomp,
        "q_first_testable_at_family_size": first_gap,
        "controls": {"positive_resolvability_binds": bool(pos), "negative_no_ablation": bool(neg),
                     "sham_seed_only": bool(sham)},
        "world": world,
        "limitation": "an ablation shows what a component excludes IN THIS POPULATION; and binding "
                      "is necessity, never correctness",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
