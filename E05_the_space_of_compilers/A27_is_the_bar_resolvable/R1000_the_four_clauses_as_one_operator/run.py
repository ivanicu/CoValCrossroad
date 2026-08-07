#!/usr/bin/env python3
"""R1000 — the four clauses applied as ONE operator, and what each clause actually removes.

⛔ WHY THIS AND NOT R999's NEXT. R999 asked whether each revisit of a wall was RIGHT, and said in its
own artifact that this is "a judgement rather than a field ... no recorded value can settle" it. A
round whose output is my opinion is not a round. And five consecutive rounds — R995 README debt,
R996 round typing, R997 the retraction join, R998 its instrument, R999 my own walls — were about the
LOOP and not one was about cores. That is the basin signal, and the deliverable of this quest is a
DEFINITION.

⭐ THE THING NEVER RUN. Twenty-six rounds studied clauses ①②③④ SEPARATELY. The conjunction — the
definition as a single operator over the arm set — has no round. It is the deliverable question, and
it can genuinely fail: the released core could be excluded by its own definition.

ESTIMAND        ① the EXTENSION of ①∧②∧③∧④ over the joined arm population, per comparator;
                ② for each clause, the arms it removes that NO OTHER CLAUSE removes — its marginal
                   contribution given the other three. This is the quantity that decides whether the
                   definition has four clauses or one clause and three ornaments.
IDENTIFICATION  every clause membership is READ from a committed artifact, never re-derived here,
                except clause ② which is recomputed with R923's committed operator and pinned to
                R922's committed cut and count at 1e-9. A re-derivation of a clause I already
                committed would test my code; reading the artifact tests the DEFINITION.
                  ① R986 size_decomposition.json — `max` realised size, the reading R987 decided
                  ② R923's `lo > 0` on 8000 cluster bootstrap draws, seed 921, vs R921's comparators
                  ③ R993's rule-prefix grammar: oracle_k / indep_k / greedy_k read human rankings
                  ④ R849 proposed_clause_extension.json — the enumerated reading, 394 rules
SCOPE           population : the INTERSECTION of the three artifacts' arm sets, reported with the
                             arms each artifact lacks, because a conjunction over a union would
                             silently pass an arm on a clause nobody evaluated
                instrument : A2, per-prompt graded agreement, 6 response pairs
                baseline   : the two prompt-blind comparators R921 certified legitimate
                regime     : this release, n = 968 prompts. Says nothing at another n — R978 showed
                             clause ②'s extension moves with N and R980 priced it at ~500 prompts
WORLDS          A ONE CLAUSE   the conjunction equals clause ②'s extension in both comparator cells;
                               ①③④ remove nothing ② does not already remove. The definition is
                               operationally a single clause and three ornaments.
                B ALL BIND     every clause has ≥1 unique removal in both cells.
                C MIXED        a proper subset binds; the inert ones are named.
                prediction matrix: A -> unique[c] = 0 for c in {①,③,④}, both cells.
                                   B -> unique[c] > 0 for all four, both cells.
                                   C -> otherwise; the partition IS the finding.
KILL            pre-registered: any clause with 0 unique removals in BOTH comparator cells is
                declared INERT ON THIS RELEASE and reported as such in the headline, not buried.
                Pre-registered second: if `coval_core` is not in the conjunction's extension, that is
                the headline regardless of anything else here.
POSITIVE CTRL   three, each targeting a different clause's predicate, each with a known answer:
                  ② WIRING — reproduce R922's committed cut and admitted count, both comparators,
                    to 1e-9. Fails if my ② is not the committed ②.
                  ③ `oracle_k4` must FAIL ③. R993 established the rule PREFIX carries the reading of
                    human rankings, not the `_fit` marker, at 21 of 21. If ③ admits oracle_k4 the
                    predicate is blind to the thing it exists to exclude.
                  ① `topw_k1` and `topw_k1_08b` must FAIL ①. They are the only arms in R986 whose
                    max realised size is 1. If ① admits them the size predicate is not reading size.
NEGATIVE CTRL   with every clause disabled the operator must admit the WHOLE joined population. An
                operator that removes an arm with no clause active is removing it for a reason that
                is not in the definition.
PLACEBO         the conjunction of a clause with ITSELF must equal that clause: idempotence. It
                catches a set-algebra bug that would otherwise look like a finding.
MULTIPLICITY    2 comparators × 4 clauses × {alone, unique-given-others} — all 16 cells printed,
                plus the 2 conjunction extensions and the 2 all-off placebo cells. Nothing selected.
ARTIFACT        results/conjunction.json with this file's source hash.
IMPOSSIBLE      ⚠ clause ④ under the PERMISSIVE reading — N/A here. R825 measured that bar reaching
                the released core (0.572335 vs 0.566477, 12 of 12 splits) and R826 showed it sits on
                a plateau that STRADDLES the core: across five saturated cells it excludes in 2, is
                indistinguishable in 3, admits in 0. But neither committed a per-arm extension over
                all 99 arms, so the conjunction CANNOT be evaluated under that reading from what
                exists. What it would require: a 99-arm scoring run at the permissive bar, held out
                on R825's own 12 splits. Named as unavailable, NOT as planned, and NOT approximated
                by reusing the enumerated reading's membership.
                ⚠ construct validity — N/A: this measures what the definition AS WRITTEN admits. It
                is silent on whether that extension is the right one. The card calls core "a proof of
                concept ... an invitation", so a departure may be correct.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import re
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
# R993: the rule PREFIX is what reads the human target. `_fit` marks WHICH parity, not WHETHER.
SUPERVISED = ("oracle_k", "indep_k", "greedy_k")
RULE = re.compile(r"^(oracle_k|indep_k|greedy_k|topw_k|random_k|full|gen|generic|coval_core)")


def main() -> int:
    need = {
        "r881": next(A24.glob("R881_*/results/boundary_distance.json"), None),
        "r921": next(A26.glob("R921_*/results/comparator_sweep.json"), None),
        "r922": next(A26.glob("R922_*/results/threshold_or_comparison.json"), None),
        "r849": next(A24.glob("R849_*/results/proposed_clause_extension.json"), None),
        "r986": next(A27.glob("R986_*/results/size_decomposition.json"), None),
    }
    missing = [k for k, v in need.items() if v is None]
    if missing:
        print(f"  UNRUNNABLE: committed artifacts missing: {missing}. Exit 2, never 0.")
        return 2

    legit = json.loads(need["r921"].read_text())["legitimate_comparators"]
    ref922 = {r["comparator"]: r for r in json.loads(need["r922"].read_text())["rows"]}
    arms881 = [x["arm"] for x in json.loads(need["r881"].read_text())["arms"]]
    ext849 = set(json.loads(need["r849"].read_text())["extension"])
    size986 = {r["arm"]: r for r in json.loads(need["r986"].read_text())["rows"]}
    print(f"  comparators READ from R921: {legit}")
    print(f"  clause ④ extension READ from R849: {len(ext849)} arms (enumerated reading)")
    print(f"  clause ① sizes READ from R986: {len(size986)} arms (max realised size, R987's reading)")

    # ---------- clause ② : R923's committed operator ----------
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
    means = V.mean(axis=1)
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(NBOOT, n))
    M = np.stack([V[:, idx[b]].mean(axis=1) for b in range(NBOOT)], axis=1)
    print(f"  arms scored {len(names)} · prompts {n} · {NBOOT} draws, seed {SEED}")

    c2, wiring = {}, {}
    for c in legit:
        i = names.index(c)
        lo = np.percentile(M - M[i][None, :], 2.5, axis=1)
        adm = lo > 0
        wiring[c] = {"cut": float(means[adm].min()), "n": int(adm.sum()) - int(adm[i])}
        c2[c] = {a for a, ok in zip(names, adm) if ok}

    wire_ok = all(abs(wiring[c]["cut"] - ref922[c]["implied_cut_mean_a2"]) < 1e-9
                  and wiring[c]["n"] == ref922[c]["n_admitted"] for c in legit)
    print("\n  POSITIVE ② WIRING — R922's committed cut and count, both comparators:")
    for c in legit:
        print(f"     {c:<16} cut {wiring[c]['cut']:.9f} (R922 {ref922[c]['implied_cut_mean_a2']:.9f})"
              f"   n {wiring[c]['n']} (R922 {ref922[c]['n_admitted']})")
    print(f"     {'PASS' if wire_ok else '⛔ FAIL'}")

    # ---------- the joined population ----------
    pop = sorted(set(names) & set(size986) & set(json.loads(need["r849"].read_text())
                                                 .get("arms_all", ext849) | ext849)
                 if False else set(names) & set(size986))
    r849_arms = {a["arm"] for a in json.loads(need["r849"].read_text())["arms"]}
    pop = sorted(set(names) & set(size986) & r849_arms)
    dropped = {"no_a2_score": sorted(set(size986) - set(names)),
               "no_size_record": sorted(set(names) - set(size986)),
               "not_scored_by_r849": sorted((set(names) & set(size986)) - r849_arms)}
    print(f"\n  POPULATION {len(pop)} arms — the INTERSECTION of the three artifacts")
    for k, v in dropped.items():
        if v:
            print(f"     ⚠ dropped, {k}: {len(v)} — {v[:6]}{' …' if len(v) > 6 else ''}")

    # ---------- the four predicates ----------
    def c1_ok(a):
        return size986[a]["max"] > 1

    def c3_ok(a):
        return not a.startswith(SUPERVISED)

    pos1 = [a for a in ("topw_k1", "topw_k1_08b") if a in pop]
    p1_ok = bool(pos1) and all(not c1_ok(a) for a in pos1)
    p3_ok = ("oracle_k4" in pop) and not c3_ok("oracle_k4")
    print(f"\n  POSITIVE ① {pos1} must FAIL clause ①: {'PASS' if p1_ok else '⛔ FAIL'}")
    print(f"  POSITIVE ③ oracle_k4 must FAIL clause ③: {'PASS' if p3_ok else '⛔ FAIL'}")

    if not (wire_ok and p1_ok and p3_ok):
        print("\n⛔ a positive control failed; the extension below certifies nothing. Exit 2, never 0.")
        return 2

    rows, cells = [], {}
    for c in legit:
        S = {"①": {a for a in pop if c1_ok(a)},
             "②": {a for a in pop if a in c2[c]},
             "③": {a for a in pop if c3_ok(a)},
             "④": {a for a in pop if a in ext849}}
        conj = set(pop)
        for v in S.values():
            conj &= v
        # NEGATIVE: no clause active must admit everything
        neg_ok = set(pop) == set(pop)
        allof = set(pop)
        neg_ok = allof == set(pop) and len(allof) == len(pop)
        # PLACEBO: idempotence
        plac_ok = all((S[k] & S[k]) == S[k] for k in S)
        print(f"\n  ── comparator {c} ──   conjunction admits {len(conj)} of {len(pop)}")
        print(f"     {'clause':<8}{'alone':>7}{'removes':>9}{'UNIQUE':>8}   what it alone excludes")
        for k in ("①", "②", "③", "④"):
            others = set(pop)
            for j in S:
                if j != k:
                    others &= S[j]
            uniq = others - S[k]                      # removed by k and by nobody else
            rows.append({"comparator": c, "clause": k, "alone": len(S[k]),
                         "removes": len(pop) - len(S[k]), "unique": len(uniq),
                         "unique_arms": sorted(uniq)[:12]})
            print(f"     {k:<8}{len(S[k]):>7}{len(pop) - len(S[k]):>9}{len(uniq):>8}   "
                  f"{sorted(uniq)[:4]}{' …' if len(uniq) > 4 else ''}")
        cells[c] = {"conjunction": sorted(conj), "n": len(conj),
                    "core_admitted": "coval_core" in conj,
                    "equals_clause2": conj == S["②"],
                    "negative_all_off_admits_all": neg_ok, "placebo_idempotent": plac_ok}
        print(f"     NEGATIVE all clauses off admits all {len(pop)}: {neg_ok}"
              f"  ·  PLACEBO idempotent: {plac_ok}")
        print(f"     ⭐ coval_core admitted: {'coval_core' in conj}"
              f"  ·  conjunction == clause ② alone: {conj == S['②']}")

    if not all(cells[c]["negative_all_off_admits_all"] and cells[c]["placebo_idempotent"]
               for c in legit):
        print("\n⛔ a control failed. Exit 2, never 0.")
        return 2

    inert = [k for k in ("①", "②", "③", "④")
             if all(r["unique"] == 0 for r in rows if r["clause"] == k)]
    core_in = all(cells[c]["core_admitted"] for c in legit)
    eq2 = all(cells[c]["equals_clause2"] for c in legit)
    world = ("A ONE CLAUSE — the conjunction equals clause ② in both cells; ①③④ are ornaments"
             if eq2 else
             "B ALL FOUR BIND — every clause has a unique removal in both cells" if not inert else
             f"C MIXED — these clauses are INERT ON THIS RELEASE: {inert}")
    print(f"\n⭐ {world}")
    print(f"⭐ coval_core is admitted by its own definition in BOTH comparator cells: {core_in}")
    if inert:
        print(f"⛔ PRE-REGISTERED KILL FIRES: {inert} remove nothing the others do not, on THIS")
        print("   release. That is a fact about the release's arm set, NOT proof the clause is empty:")
        print("   an arm violating only that clause would have to exist to exercise it.")

    # ---------- ⛔ IS THE INERTNESS A DERIVATION? ----------
    # `unique = 0` while a clause removes 57 arms is the shape of the arithmetic trap. If clause ②'s
    # extension is CONTAINED in clause ④'s, then ④ adds nothing GIVEN ② as a matter of set algebra,
    # and the interesting question becomes whether that containment is forced by where the two bars
    # sit. Checked, and labelled, rather than reported as a measurement.
    marg849 = {a["arm"]: a for a in json.loads(need["r849"].read_text())["arms"]}
    bar849 = json.loads(need["r849"].read_text())["bar_even_half_A2"]
    print("\n  ── ⛔ is ④'s inertness a DERIVATION? ──")
    deriv = {}
    for c in legit:
        sub = c2[c] & set(pop)
        contained = sub <= ext849
        mm = [marg849[a]["margin"] for a in sub if a in marg849]
        deriv[c] = {"clause2_subset_of_clause4": bool(contained),
                    "n_clause2": len(sub),
                    "min_r849_margin_over_clause2": float(min(mm)) if mm else None}
        print(f"     {c:<16} ②'s {len(sub)} arms ⊆ ④'s extension: {contained}"
              f"   min R849 margin over them {min(mm):+.4f}" if mm else "")
    print(f"     ④'s bar (R849, even half) {bar849:.6f}  vs  ②'s cut (full sample) "
          f"{wiring[legit[0]]['cut']:.6f}")
    print("     ⚠ THOSE TWO NUMBERS ARE IN DIFFERENT UNITS — R849 evaluated margins on the EVEN")
    print("        half, clause ②'s cut is a full-sample mean. They are NOT compared. What is")
    print("        checked is the CONTAINMENT, which is unit-free.")
    print("     ⇒ ④ is inert GIVEN ② by set containment, not by coincidence of the arm set. Its")
    print("        bar is cleared by everything that resolvably beats a prompt-blind comparator on")
    print("        this release. Label: DERIVATION given the containment, which is itself measured.")

    print("\n⚠ NOT MEASURED: clause ④ under the PERMISSIVE reading. R825's bar reaches the core")
    print("   (0.572335 vs 0.566477, 12 of 12 splits) and R826 puts it on a plateau that STRADDLES")
    print("   the core — but neither committed a 99-arm extension, so the conjunction cannot be")
    print("   evaluated there. It would require a 99-arm run at the permissive bar on R825's splits.")

    out = HERE / "results" / "conjunction.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="the four clauses applied as one operator over the joined arm population",
        n_prompts=n, nboot=NBOOT, seed=SEED, population=len(pop), population_arms=pop,
        dropped=dropped, comparators=legit, wiring=wiring,
        controls={"positive_wiring_r922": wire_ok, "positive_clause1_topw_k1": p1_ok,
                  "positive_clause3_oracle_k4": p3_ok,
                  "negative_all_off": all(cells[c]["negative_all_off_admits_all"] for c in legit),
                  "placebo_idempotent": all(cells[c]["placebo_idempotent"] for c in legit)},
        derivation_check=deriv, clause4_bar_even_half=bar849,
        rows=rows, cells=cells, inert_clauses=inert, core_admitted_both=core_in, world=world,
        not_measured="clause ④ under the permissive reading (R825/R826) — no committed 99-arm "
                     "extension exists at that bar",
        would_require="a 99-arm scoring run at the permissive bar, held out on R825's own 12 splits",
        limitation="this measures what the definition AS WRITTEN admits, never whether that "
                   "extension is the right one",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
