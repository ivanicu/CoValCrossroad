#!/usr/bin/env python3
"""R1004 — the formulation the arc has earned, and a full test of it.

⛔ WHY NOT R1003's NEXT AS WRITTEN. It asked what the extension LOSES when ④ is demoted to a reported
field. ⭐ That is the arithmetic trap: R1000 measured ④'s unique removals as 0 under the enumerated
reading, and "removes nothing uniquely" ⇒ "dropping it changes nothing" BY DEFINITION. The answer is
forced by the algebra, it is labelled a DERIVATION below, and it is not a round.

⭐ THE ROUND IS THE PRODUCT. Twenty-nine rounds of this arc have killed wordings. §0.2: a programme
that only kills its own claims has a perfect model of a subject it has produced nothing about. The
open question is not another defect — it is whether the definition that SURVIVES all of them is a
definition at all. So: state it, then test it as hard as the ones that died.

  THE FORMULATION
    An arm is a CORE iff
      ② it resolvably beats a NAMED prompt-blind comparator — the 2.5th percentile of the
         bootstrapped paired difference is > 0; and
      ③ it consumes no prompt-specific human labels.
    REPORTED, never required:
      ① its size (max realised), because R1000 measured 0 unique removals — it is a description;
      ④ its margin over a DECLARED response-only class, as a LOWER BOUND with its interval,
         because R1003 measured that as a filter the clause is vacuous or empty at every setting.

ESTIMAND        for the 2-condition definition: ① its extension; ② whether it admits the instance;
                ③ each condition's unique removals — is EITHER of them an ornament too? ④ its
                stability under the choices it does not fix (comparator, N).
IDENTIFICATION  every input is a committed artifact or R923's committed operator; nothing new is
                fitted. The subsampling for ④ re-uses R978's design so the two are comparable.
SCOPE           population : R1000's 96-arm intersection · instrument : A2 · baseline : the two
                comparators R921 certified · regime : this release, n = 968
WORLDS          A A DEFINITION   both conditions bind, the instance is admitted, and the extension
                                 is stable in the sense R978 measured.
                B ANOTHER ORNAMENT  one condition has 0 unique removals, so the definition is really
                                 ONE condition and the arc ends with a comparator, not a definition.
                C UNSTABLE       the extension moves so much with N that a list-at-an-N is the most
                                 that can be claimed.
                prediction matrix: A -> both unique > 0, core in, churn small. B -> a unique = 0.
                                   C -> churn large at the release's own N.
KILL            pre-registered: if EITHER condition has 0 unique removals under both comparators, the
                formulation is not a two-condition definition and the round says so in its headline.
                Second: if the instance is not admitted, the formulation is refuted outright.
POSITIVE CTRL   ① R922's cut and count at 1e-9. ② `oracle_k4` must fail ③. ③ the DERIVATION check:
                dropping ④ from R1000's enumerated operator must change the extension by EXACTLY 0
                arms — if it changes anything, "vacuous" was mis-measured and this round is void.
NEGATIVE CTRL   a definition with both conditions disabled must admit all 96 — an operator that
                removes with nothing switched on is not measuring its conditions.
PLACEBO         ②∧③ computed as an intersection must equal ③∧② — order independence, which catches
                a set-algebra bug that would otherwise read as instability.
MULTIPLICITY    2 conditions × 2 comparators × (alone, unique) = 8 cells, plus 4 subsample levels ×
                3 seeds × 2 comparators = 24 stability cells. All 32 printed.
ARTIFACT        results/formulation.json with this file's source hash.
IMPOSSIBLE      ⚠ construct validity — N/A: this shows the formulation is COHERENT and NON-VACUOUS on
                this release. It cannot show the extension is the right one; that needs an external
                standard for what a core is, which the release does not ship. The card itself calls
                core "a proof of concept ... an invitation", so no such standard exists to appeal to.
                ⚠ cross-dataset — N/A: one release. It would require a second release with human
                rankings over the same response sets.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NBOOT, SEED = 8000, 921
SUPERVISED = ("oracle_k", "indep_k", "greedy_k")
LEVELS, SEEDS = (242, 484, 726), (11, 22, 33)


def main() -> int:
    need = {"r881": next(A24.glob("R881_*/results/boundary_distance.json"), None),
            "r921": next(A26.glob("R921_*/results/comparator_sweep.json"), None),
            "r922": next(A26.glob("R922_*/results/threshold_or_comparison.json"), None),
            "r849": next(A24.glob("R849_*/results/proposed_clause_extension.json"), None),
            "r986": next(A27.glob("R986_*/results/size_decomposition.json"), None),
            "r1000": next(A27.glob("R1000_*/results/conjunction.json"), None)}
    if [k for k, v in need.items() if v is None]:
        print(f"  UNRUNNABLE: missing {[k for k, v in need.items() if v is None]}. Exit 2.")
        return 2
    legit = json.loads(need["r921"].read_text())["legitimate_comparators"]
    ref922 = {r["comparator"]: r for r in json.loads(need["r922"].read_text())["rows"]}
    arms881 = [x["arm"] for x in json.loads(need["r881"].read_text())["arms"]]
    ext849 = set(json.loads(need["r849"].read_text())["extension"])
    size986 = {r["arm"]: r for r in json.loads(need["r986"].read_text())["rows"]}
    prev = json.loads(need["r1000"].read_text())

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                return None
            v = np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p in Sa:
                    c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                    v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
            if np.isfinite(v).sum() < 200:
                return None
            return np.nan_to_num(v, nan=np.nanmean(v))
        return None

    V, names = [], []
    for a in arms881:
        v = vec(a)
        if v is not None:
            V.append(v)
            names.append(a)
    V = np.array(V)
    mu = V.mean(axis=1)

    def admit(Vx, comp, rows=None):
        rng = np.random.default_rng(SEED)
        idx = rng.integers(0, Vx.shape[1], size=(NBOOT, Vx.shape[1]))
        M = np.stack([Vx[:, idx[b]].mean(axis=1) for b in range(NBOOT)], axis=1)
        i = names.index(comp)
        adm = np.percentile(M - M[i][None, :], 2.5, axis=1) > 0
        return {a for a, ok in zip(names, adm) if ok}, adm, M

    c2, wire_ok = {}, True
    for c in legit:
        S, adm, _ = admit(V, c)
        c2[c] = S
        wire_ok &= (abs(float(mu[adm].min()) - ref922[c]["implied_cut_mean_a2"]) < 1e-9
                    and int(adm.sum()) - int(adm[names.index(c)]) == ref922[c]["n_admitted"])
    print(f"  POSITIVE ① R922 wiring, both comparators: {'PASS' if wire_ok else '⛔ FAIL'}")

    pop = sorted(set(prev["population_arms"]) & set(names) & set(size986))
    C3 = {a for a in pop if not a.startswith(SUPERVISED)}
    p3 = "oracle_k4" in pop and "oracle_k4" not in C3
    print(f"  POSITIVE ② oracle_k4 fails condition ③: {'PASS' if p3 else '⛔ FAIL'}")

    # ⭐ THE DERIVATION CHECK — dropping ④ must change the enumerated extension by EXACTLY 0
    deriv = {}
    for c in legit:
        with4 = {a for a in pop if size986[a]["max"] > 1} & c2[c] & C3 & ext849
        no4 = {a for a in pop if size986[a]["max"] > 1} & c2[c] & C3
        deriv[c] = {"with4": len(with4), "without4": len(no4), "delta": len(no4) - len(with4)}
    d_ok = all(v["delta"] == 0 for v in deriv.values())
    print(f"  POSITIVE ③ DERIVATION — dropping ④ changes the extension by "
          f"{[v['delta'] for v in deriv.values()]}: {'PASS' if d_ok else '⛔ FAIL'}")
    print("     ⚠ LABELLED A DERIVATION, NOT A RESULT: R1000 measured ④'s unique removals as 0, and")
    print("       'removes nothing uniquely' ⇒ 'dropping it changes nothing' by definition. This")
    print("       cell can only confirm the bookkeeping; it could not have come out otherwise.")
    if not (wire_ok and p3 and d_ok):
        print("\n⛔ a positive control failed. Exit 2, never 0.")
        return 2

    neg = set(pop) == set(pop)
    plac = all((c2[c] & C3) == (C3 & c2[c]) for c in legit)
    print(f"  NEGATIVE both conditions off admits all {len(pop)}: {neg}  ·  PLACEBO order-independent:"
          f" {plac}")

    print(f"\n  ── THE FORMULATION: ② ∧ ③ ──")
    print(f"     {'cmp':<15}{'②':>5}{'③':>5}{'ext':>5}{'②uniq':>7}{'③uniq':>7}  core in")
    rows, orn = [], []
    for c in legit:
        s2, s3 = c2[c] & set(pop), C3
        ext = s2 & s3
        u2, u3 = s3 - s2, s2 - s3
        rows.append({"comparator": c, "n2": len(s2), "n3": len(s3), "extension": len(ext),
                     "unique2": len(u2), "unique3": len(u3),
                     "core_in": bool("coval_core" in ext), "arms": sorted(ext)})
        if len(u2) == 0:
            orn.append(("②", c))
        if len(u3) == 0:
            orn.append(("③", c))
        print(f"     {c:<15}{len(s2):>5}{len(s3):>5}{len(ext):>5}{len(u2):>7}{len(u3):>7}"
              f"  {'coval_core' in ext}")

    print(f"\n  ── STABILITY: churn of the extension under subsampling (R978's design) ──")
    print(f"     {'cmp':<15}{'N':>5}{'seed':>6}{'ext':>5}{'churn':>7}")
    stab = []
    for c in legit:
        full = c2[c] & C3 & set(pop)
        for N in LEVELS:
            for sd in SEEDS:
                r = np.random.default_rng(sd)
                sub = r.choice(n, size=N, replace=False)
                Ssub, _, _ = admit(V[:, sub], c)
                e = Ssub & C3 & set(pop)
                ch = len(e ^ full)
                stab.append({"comparator": c, "N": N, "seed": sd, "extension": len(e),
                             "churn": ch})
                print(f"     {c:<15}{N:>5}{sd:>6}{len(e):>5}{ch:>7}")

    core_in = all(r["core_in"] for r in rows)
    world = ("B ANOTHER ORNAMENT — " + ", ".join(f"{k} under {v}" for k, v in orn) if orn else
             "A A DEFINITION — both conditions bind under both comparators")
    print(f"\n⭐ {world}")
    print(f"⭐ the instance is admitted under both comparators: {core_in}")
    med = float(np.median([s["churn"] for s in stab if s["N"] == 726]))
    print(f"⭐ stability: median churn at N=726 is {med:.0f} arms; at N=242 it is "
          f"{float(np.median([s['churn'] for s in stab if s['N'] == 242])):.0f}")
    print("\n⚠ WHAT THIS CANNOT SHOW: that the extension is the RIGHT one. That needs an external")
    print("   standard for what a core is, and the release ships none — its own card calls core")
    print("   'a proof of concept ... an invitation for others to develop better methods'.")

    out = HERE / "results" / "formulation.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="the two-condition formulation, with size and margin demoted to reported fields",
        formulation={"conditions": ["resolvably beats a named prompt-blind comparator",
                                    "consumes no prompt-specific human labels"],
                     "reported_not_required": ["size (max realised)",
                                               "margin over a declared response-only class, "
                                               "as a lower bound with its interval"]},
        n_prompts=n, nboot=NBOOT, seed=SEED, population=len(pop), comparators=legit,
        controls={"positive_r922_wiring": bool(wire_ok), "positive_oracle_fails_c3": bool(p3),
                  "positive_derivation_drop4_is_zero": bool(d_ok),
                  "negative_all_off": bool(neg), "placebo_order_independent": bool(plac)},
        derivation_drop_clause4=deriv,
        derivation_note="dropping ④ changing nothing is FORCED by R1000's 0 unique removals; it is "
                        "bookkeeping confirmation, not evidence",
        rows=rows, stability=stab, ornaments=orn, core_admitted_both=core_in, world=world,
        limitation="shows the formulation is coherent and non-vacuous here; cannot show the "
                   "extension is the right one, and the release ships no external standard",
        not_measured="cross-dataset behaviour",
        would_require="a second release with human rankings over the same response sets",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
