#!/usr/bin/env python3
"""R1021 — the core is excluded under A1·consensus and its TWINS are not. Which is the imputation?

⛔ WHY. R1020 found that under `A1·consensus`, at 96 arms, the extension is `coval_core_2bA`,
`coval_core_2bB`, `topw_k6`, `topw_k8` — and **not `coval_core`**. ⚠ The two admitted twins are
exactly the arms R1011 measured at **200 of 968 prompts (21%)**, whose A2 the committed loader fills
with the arm's **own mean** for the missing 768.

⭐⭐ AND R1005 MEASURED THE TWINS' OUTPUTS AS IDENTICAL TO THE CORE'S — agreement **exactly 1.000** —
on the prompts they share. So:

    DERIVATION, LABELLED. On the 200 prompts all three cover, the twins' class vectors ARE the core's.
    Any statistic computed there from those vectors must therefore be IDENTICAL for all three. It
    could not come out otherwise, and the check below can only confirm the bookkeeping.

    MEASUREMENT. Whether the SPLIT at 968 — twins in, core out — disappears when the comparison is
    restricted to those 200 prompts, where nothing is imputed for anyone.

ESTIMAND        ① the A1·consensus paired difference of core and each twin, on the 200 shared prompts
                   (forced to 0 by the derivation, computed as a control);
                ② the ②′∧③ admission of core and twins on those 200 prompts, where every arm's score
                   is real;
                ③ therefore: is the 968-prompt split a TARGET effect or the IMPUTATION?
IDENTIFICATION  exact. The 200-prompt restriction removes every imputed value for the twins and takes
                a real subset for the core and both comparators. No arm is filled in anywhere.
SCOPE           population : the 200 prompts `coval_core_2bA` actually covers
                instrument : A1·consensus, copied from R288 as in R1020
                baseline   : the same clause ②′ comparators, restricted to the same 200
                regime     : this release
WORLDS          A THE IMPUTATION   on 200 real prompts, core and twins are admitted or excluded
                            TOGETHER. Then R1020's split is an artifact of filling 768 values with
                            the twins' own mean, and the core's exclusion under A1·consensus is a
                            claim about imputed data.
                B THE TARGET       they still split on 200 real prompts. Then the exclusion is a
                            genuine target effect and survives removing every imputed value.
                prediction matrix: A -> identical admission, and the 200-prompt difference is 0.
                                   B -> they differ on 200 too, which the derivation forbids unless
                                   R1005's 1.000 is wrong — so B firing is a finding about R1005.
KILL            pre-registered: if world A, R1020's headline is SCOPED in this round — "excludes its
                own instance" becomes "excludes its own instance while admitting two arms whose
                admission rests on imputed values", which is a materially weaker claim and must
                replace it rather than sit beside it.
POSITIVE CTRL   the derivation's own check: on the 200 prompts, core-vs-twin A1·consensus difference
                must be EXACTLY 0. If it is not, either R1005's identity is wrong or the restriction
                is not doing what it says, and nothing below is admissible.
NEGATIVE CTRL   at 968 prompts the same difference must be NON-zero — that is the phenomenon R1020
                found, and if it vanishes here the two rounds are not measuring the same thing.
PLACEBO         a full-coverage arm restricted to 200 and compared with itself: exactly 0.
NOISE FLOOR     the bootstrap interval at n = 200, which is wider than at 968 by construction and is
                reported so an "admitted together" is not read as a tie the design could not resolve.
MULTIPLICITY    2 comparators × {core, 2 twins} × {200, 968}, all cells printed.
ARTIFACT        results/coverage_or_target.json with this file's source hash.
IMPOSSIBLE      ⚠ what the twins WOULD score on the other 768 — N/A: they were never run there. That
                is the defect, not a gap in this round, and it is why the 200-prompt restriction is
                the only comparison in which no value is invented.
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
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NBOOT, SEED = 8000, 1021
CORE = "coval_core"
TWINS = ["coval_core_2bA", "coval_core_2bB"]


def main() -> int:
    r921 = next(A26.glob("R921_*/results/comparator_sweep.json"), None)
    r1020 = next(A27.glob("R1020_*/results/a1_at_full_population.json"), None)
    if not (r921 and r1020):
        print("  UNRUNNABLE: a committed artifact is missing. Exit 2, never 0.")
        return 2
    legit = json.loads(r921.read_text())["legitimate_comparators"]
    prev = json.loads(r1020.read_text())
    print(f"  R1020's A1·consensus extension: {prev['extension_a1_consensus']}")
    print(f"  ⚠ it contains the twins and NOT `{CORE}`.")

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    HC = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    CONS = {p: np.sign(HC[p].sum(axis=0)) for p in pids}

    def raw(nm):
        """per-prompt A1·consensus, and the set of prompts the arm actually covers."""
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                return None, None
            v, cov = {}, set()
            for p in pids:
                if p not in Sa:
                    continue
                c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                m = min(len(c), len(CONS[p]))
                v[p] = float((c[:m] == CONS[p][:m]).all())
                cov.add(p)
            return v, cov
        return None, None

    V, COV = {}, {}
    for a in [CORE] + TWINS + list(legit):
        v, c = raw(a)
        if v is None:
            print(f"  UNRUNNABLE: `{a}` is not scoreable. Exit 2, never 0.")
            return 2
        V[a], COV[a] = v, c
    shared = sorted(set.intersection(*[COV[a] for a in [CORE] + TWINS]))
    print(f"\n  coverage: {CORE} {len(COV[CORE])} · twins "
          f"{[len(COV[t]) for t in TWINS]} · shared by all three: {len(shared)}")
    if len(shared) < 100:
        print("  UNRUNNABLE: too few shared prompts. Exit 2, never 0.")
        return 2

    def arr(a, ps):
        return np.array([V[a][p] for p in ps], float)

    def imputed(a, ps):
        """the loader's behaviour: real where covered, the arm's OWN MEAN elsewhere."""
        vals = [V[a].get(p) for p in ps]
        obs = [x for x in vals if x is not None]
        mu = float(np.mean(obs)) if obs else 0.0
        return np.array([mu if x is None else x for x in vals], float)

    # ---------- POSITIVE CONTROL: the derivation's own check ----------
    devs = {t: float(np.abs(arr(CORE, shared) - arr(t, shared)).max()) for t in TWINS}
    pos_ok = all(v == 0.0 for v in devs.values())
    print(f"\n  POSITIVE (the DERIVATION's check) — on the {len(shared)} shared prompts the core and "
          f"each twin must be IDENTICAL: max|Δ| {devs} → {'PASS' if pos_ok else '⛔ FAIL'}")
    print("     ⚠ LABELLED A DERIVATION: R1005 measured their outputs identical there at agreement")
    print("       exactly 1.000, so a statistic computed from those vectors could not differ. This")
    print("       cell confirms bookkeeping; it is not evidence.")
    if not pos_ok:
        print("  either R1005's identity is wrong or the restriction is not doing what it says. "
              "Exit 2, never 0.")
        return 2

    # ---------- NEGATIVE CONTROL: at 968, with imputation, they DO differ ----------
    full = pids
    d968 = {t: float(np.abs(imputed(CORE, full) - imputed(t, full)).mean()) for t in TWINS}
    neg_ok = all(v > 0 for v in d968.values())
    print(f"  NEGATIVE — at {len(full)} prompts WITH the loader's imputation they must DIFFER: "
          f"mean|Δ| {d968} → {'PASS' if neg_ok else '⛔ FAIL'}")
    plac = float(np.abs(arr(legit[0], shared) - arr(legit[0], shared)).max())
    plac_ok = plac == 0.0
    print(f"  PLACEBO  — a full-coverage arm against itself on the same 200: {plac:.1e} "
          f"{'PASS' if plac_ok else '⛔ FAIL'}")
    if not (neg_ok and plac_ok):
        print("\n⛔ a control failed. Exit 2, never 0.")
        return 2

    rng = np.random.default_rng(SEED)
    idx200 = rng.integers(0, len(shared), size=(NBOOT, len(shared)))
    idxF = rng.integers(0, len(full), size=(NBOOT, len(full)))

    def admit(a, c, ps, index, imp):
        x = (imputed(a, ps) if imp else arr(a, ps)) - (imputed(c, ps) if imp else arr(c, ps))
        bs = x[index].mean(axis=1)
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        return lo > 0, lo, hi, float(x.mean())

    print(f"\n  {'arm':<18}{'n':>6}{'cmp':<16}{'Δ':>10}{'lo':>10}{'hi':>10}  admitted")
    rows = []
    for label, ps, index, imp in (("200 real", shared, idx200, False),
                                  ("968 imputed", full, idxF, True)):
        for a in [CORE] + TWINS:
            for c in legit:
                ok, lo, hi, m = admit(a, c, ps, index, imp)
                rows.append({"regime": label, "arm": a, "comparator": c, "delta": m,
                             "lo": lo, "hi": hi, "admitted": bool(ok)})
                print(f"  {a:<18}{len(ps):>6}{c:<16}{m:>+10.4f}{lo:>+10.4f}{hi:>+10.4f}  {ok}")

    def ext(label):
        out = set()
        for a in [CORE] + TWINS:
            cells = [r for r in rows if r["regime"] == label and r["arm"] == a]
            if cells and all(r["admitted"] for r in cells):
                out.add(a)
        return out

    e200, e968 = ext("200 real"), ext("968 imputed")
    print(f"\n  admitted on 200 REAL prompts   : {sorted(e200)}")
    print(f"  admitted on 968 with imputation: {sorted(e968)}")
    together = (CORE in e200) == all(t in e200 for t in TWINS)
    world = ("A THE IMPUTATION — on 200 real prompts the core and its twins are admitted or excluded "
             "TOGETHER, so R1020's split is an artifact of filling 768 values with the twins' own "
             "mean" if together else
             "B THE TARGET — they split even on 200 real prompts, which the derivation forbids "
             "unless R1005's identity is wrong")
    print(f"\n⭐ {world}")
    if together:
        print("⛔ PRE-REGISTERED KILL FIRES: R1020's headline is SCOPED here, not left standing.")
        print("   'the definition excludes its own instance' becomes 'the definition excludes its")
        print("   own instance while admitting two arms whose admission rests on imputed values' —")
        print("   materially weaker, and it REPLACES the earlier wording rather than sitting beside")
        print("   it. ⭐ The target effect on the core is real; the CONTRAST with the twins is not.")
    print(f"\n⚠ THE 200-PROMPT INTERVALS ARE WIDER BY CONSTRUCTION (n = {len(shared)} against "
          f"{len(full)}), so an 'admitted together' here")
    print("   must not be read as a tie the design could not resolve — the intervals are printed.")
    print("⚠ AND WHAT THE TWINS WOULD SCORE ON THE OTHER 768 IS UNKNOWABLE: they were never run")
    print("   there. That is the defect, not a gap in this round.")

    out = HERE / "results" / "coverage_or_target.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="is the core's exclusion under A1·consensus a target effect or the imputation",
        n_shared=len(shared), n_full=len(full), nboot=NBOOT, seed=SEED,
        controls={"positive_derivation_identical_on_shared": devs, "positive_ok": bool(pos_ok),
                  "negative_differ_at_968_with_imputation": d968, "negative_ok": bool(neg_ok),
                  "placebo_self": plac, "placebo_ok": bool(plac_ok)},
        rows=rows, admitted_200_real=sorted(e200), admitted_968_imputed=sorted(e968),
        together=bool(together), world=world,
        derivation="on the shared prompts the twins' class vectors ARE the core's (R1005, agreement "
                   "exactly 1.000), so any statistic computed there is identical by construction",
        limitation="what the twins would score on the other 768 prompts is unknowable — they were "
                   "never run there",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
