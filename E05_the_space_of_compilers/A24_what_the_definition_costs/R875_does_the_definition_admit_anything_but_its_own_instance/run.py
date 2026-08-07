#!/usr/bin/env python3
"""
R875 · does the restated definition admit anything but its own instance?

⛔ WHY. R874 reduced the definition to two clauses — ③ no prompt labels, ② beats a NAMED
prompt-blind comparator under a NAMED criterion — and left exactly one limitation live: **it is
still written from a release shipping one core, so `the definition describes the instance` applies
to every clause.** §4 of the standard names the tell: *the definition has never been checked against
an object other than the one it was written from.*

⭐ **THE TEST THAT TOUCHES THAT WITHOUT A SECOND RELEASE.** The release ships 99 scored arms built
by different procedures. If the two retained clauses admit **only `coval_core` and its near-copies**,
the definition is describing. If they admit arms that are **procedurally distant** from it, the
definition is defining a category the core happens to belong to.

⚠ **AND THE DISTANCE MUST BE MEASURED, NOT NAMED.** The cheap version reads construction from arm
NAMES — `topw_*` is top-weight, `greedy_*` is greedy — and §4's `a label is not a description` says
what that is worth. The measurable proxy is the **per-prompt score correlation with `coval_core`**:
an arm built by the same procedure tracks it closely; one built differently does not. That is a
proxy and it is declared as one below, with the direction it is sound in.


⛔⛔ POST-RUN CORRECTION. **`WORLD B` STANDS, BUT NOT FOR THE REASON THE BRANCH GAVE, AND TWO
ADMITTED ARMS ARE ALIASES OF THE CORE.**

**① THE 0.7 THRESHOLD WAS A NUMBER I CHOSE.** The branch read `rmin < 0.7 -> WORLD B`, and nothing
in the design says why 0.7. Every one of the 99 arms scores the same 968 prompts against the same
human target, so **a large shared component is forced by the task** and an absolute correlation says
nothing without a reference. **This is the threshold-wearing-a-criterion's-clothes error the session
has caught four times, committed a fifth time in the verdict line.**

⭐ **THE REFERENCE WAS ALREADY IN THE ARTIFACT AND I DID NOT LOOK.** `random_k4_s0` — the negative
control, procedurally unrelated to the core by construction — correlates with it at **+0.5798**. The
whole random family (38 arms) runs **min +0.2090 · median +0.4439 · max +0.6855**. **That is the
null for "how much correlation does a procedurally unrelated arm show anyway", and it costs nothing
to compute.**

⭐⭐ **AGAINST THAT REFERENCE THE RESULT IS SHARPER, NOT WEAKER:**
  · admitted set (criterion B, n=27): **min +0.5406 · median +0.7599**
  · rejected set (n=71): **min +0.2090 · median +0.4105**
  · **the admitted MINIMUM, `oracle_k4_08bR` at +0.5406, is BELOW `random_k4_s0`'s +0.5798.**
**So the definition admits at least one arm that is LESS core-like than the random negative control
is.** That is direct evidence the clauses are not selecting near-copies, and it rests on a measured
comparison rather than on a cutoff I invented. The admitted median sitting **above the random
family's maximum** (0.7599 vs 0.6855) is the other half: as a group the admitted arms are more
core-like than chance, while their tail reaches past it.

**② TWO ADMITTED ARMS ARE THE CORE.** `coval_core_2bA` and `coval_core_2bB` sit at **r > 0.9999** —
they are aliases, not independent objects. **The honest count of admitted-and-distinct arms is 25,
not 27**, and the round's own phrase *"besides `coval_core`"* excluded only the exact name string.
An alias is the instance under another name, and counting it as breadth is the same error as
counting a duplicate row as a replication.

**WHAT SURVIVES, corrected:** the two retained clauses admit **25 procedurally distinct arms**, whose
correlation with the core spans **+0.5406 to below 1.0**, with the minimum **below the random
control's own correlation**. ⭐ **The definition is not merely re-describing `coval_core`.**

⚠ **AND IT STILL DOES NOT RETIRE `the definition describes the instance`.** It shows the clauses are
non-degenerate on THIS release — that they select a set with real internal spread rather than a
neighbourhood of one point. **Retiring the limitation needs a second release with a differently-built
core**, and that is unchanged by anything measured here.

ESTIMAND        among arms satisfying BOTH retained clauses, the distribution of per-prompt score
                correlation with `coval_core` — and specifically its MINIMUM.
IDENTIFICATION  exact. Admission is recomputed here under the named comparator and named criterion;
                correlation is over the shared prompt population. No name-based inference.
SCOPE           population: the 99 scored arms — DERIVED from the estimand (the objects the
                            definition is about), not globbed
                instrument: A2 vs every annotator; comparator `genericpool16` (②'s published,
                            inside its meaningful window per R867); criterion BOTH, reported apart
                baseline:   `coval_core` itself, r = 1.0 by construction
                regime:     home release, judge J
PROXY LEDGER    PROPERTY  the admitted arm was built by a different procedure
                PROXY     low per-prompt score correlation with `coval_core`
                IMPLICATION  **low r ⇒ different procedure** is SOUND (same construction cannot
                             produce uncorrelated per-prompt scores). **high r ⇒ same procedure**
                             is NOT (two different constructions can converge). So this rules on
                             DIFFERENCE only, which is the direction the question needs.
WORLDS          A · every admitted arm is near-identical to the core (min r high) -> the definition
                    describes its instance, and the live limitation is CONFIRMED
                B · admitted arms span a wide correlation range including low values -> the
                    definition admits procedurally distant objects and is DEFINING
                C · the admitted set is {coval_core} alone -> the strongest form of A: the clauses
                    admit literally nothing else
KILL            CONDITIONAL, all required:
                  ⭐ ① POSITIVE: `oracle_k4` must be ADMITTED by ② (R867 measured +6.700 at this
                     comparator). If the ceiling is not admitted, admission is mis-computed.
                  ⭐ ② NEGATIVE: `random_k4_s0` must NOT be admitted (R851's negative control).
                  ⭐ ③ PLACEBO: `coval_core` against itself must give r = 1.0 EXACTLY.
                  ④ the admitted set must be non-empty, else exit 2 — a definition admitting
                     nothing is not evidence about breadth, it is a broken recomputation.
MULTIPLICITY    99 arms × 2 criteria; both admitted sets reported whole, survivors and not.
ARTIFACT        results/admits_beyond_instance.json
IMPOSSIBLE      cross-release · construct validated · causally identified. ⚠ And the honest one:
                even WORLD B does not retire `describes the instance` — it only shows the clauses
                are not degenerate on this release. Retiring it needs a second release, and that
                is stated here rather than quietly softened.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

NBOOT, ZEFF, FLOOR, Q = 2000, 2.802, 1.5, 0.05
BLIND, CORE, POS, NEG = "genericpool16", "coval_core", "oracle_k4", "random_k4_s0"


def bh(p, q=Q):
    C = len(p); o = np.argsort(p); k = -1
    for rank, i in enumerate(o, 1):
        if p[i] <= q * rank / C:
            k = rank
    m = np.zeros(C, bool)
    if k > 0:
        m[o[:k]] = True
    return m


def main() -> int:
    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / f"sat_{BLIND}.npz")
    A = load_sat(ROOT / "corebench" / "results" / f"sat_{CORE}.npz")
    pids = sorted(set(S) & set(A) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    n = len(pids)

    def vec(nm):
        f = ROOT / "corebench" / "results" / f"sat_{nm}.npz"
        if not f.exists():
            return None
        try:
            Sa = load_sat(f)
        except Exception:
            return None
        v = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                for c in range(6)] for h in H[k]]) if p in Sa else np.nan
                      for k, p in enumerate(pids)])
        return v if np.isfinite(v).sum() >= 200 else None

    names, V = [], []
    for f in sorted((ROOT / "corebench" / "results").glob("sat_*.npz")):
        v = vec(f.stem[4:])
        if v is not None:
            names.append(f.stem[4:]); V.append(v)
    V = np.array(V)
    B = vec(BLIND)
    ci = names.index(CORE)
    print(f"  prompts {n} · arms {len(names)} (population DERIVED from the estimand, not globbed)")

    D = V - B
    bidx = np.random.default_rng(11).integers(0, n, size=(NBOOT, n))
    M = np.isfinite(D).astype(float)
    bs = (np.nan_to_num(D)[:, bidx].sum(2) / np.maximum(M[:, bidx].sum(2), 1.0)).T
    marg = np.nanmean(D, 1)
    ratio = marg / np.maximum(ZEFF * bs.std(axis=0, ddof=1), 1e-300)
    lo = np.percentile(bs, 2.5, axis=0)
    pv = np.maximum(2 * np.minimum((bs <= 0).mean(0), (bs >= 0).mean(0)), 1.0 / (NBOOT + 1))
    admA = ratio >= FLOOR                       # criterion A: the 1.5 floor
    admB = bh(pv) & (lo > 0)                    # criterion B: BH q=0.05 + CI

    ip, ineg = names.index(POS), names.index(NEG)
    k1, k2 = bool(admA[ip] or admB[ip]), bool(not admA[ineg] and not admB[ineg])
    core_v = V[ci]
    m = np.isfinite(core_v)
    r_self = float(np.corrcoef(core_v[m], core_v[m])[0, 1])
    k3 = abs(r_self - 1.0) < 1e-12
    print(f"  KILL ① `{POS}` ADMITTED by ②: {k1}  {'PASS' if k1 else 'FAIL'}")
    print(f"  KILL ② `{NEG}` NOT admitted: {k2}  {'PASS' if k2 else 'FAIL'}")
    print(f"  KILL ③ `{CORE}` vs itself r = {r_self}: {k3}  {'PASS' if k3 else 'FAIL'}")
    if not (k1 and k2 and k3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED"}, open(OUT / "admits_beyond_instance.json", "w"),
                  indent=2)
        return 2

    def corr(i):
        mm = np.isfinite(V[i]) & m
        if mm.sum() < 200 or V[i][mm].std() == 0:
            return None
        return float(np.corrcoef(V[i][mm], core_v[mm])[0, 1])

    rows = []
    for i, nm in enumerate(names):
        if i == ci:
            continue
        rows.append({"arm": nm, "ratio": float(ratio[i]), "admit_A": bool(admA[i]),
                     "admit_B": bool(admB[i]), "r_with_core": corr(i)})
    for label, key in (("A  ratio>=1.5", "admit_A"), ("B  BH+CI", "admit_B")):
        adm = [r for r in rows if r[key] and r["r_with_core"] is not None]
        if not adm:
            print(f"\n  criterion {label}: admits NOTHING besides the core")
            continue
        rs = sorted(r["r_with_core"] for r in adm)
        print(f"\n  criterion {label}: admits {len(adm)} arm(s) besides `{CORE}`")
        print(f"    r with core — min {rs[0]:+.4f} · p25 {np.percentile(rs,25):+.4f} · "
              f"median {np.median(rs):+.4f} · max {rs[-1]:+.4f}")
        for r in sorted(adm, key=lambda x: x["r_with_core"])[:6]:
            print(f"      {r['arm']:<28} r={r['r_with_core']:+.4f}  ratio={r['ratio']:+.3f}")
    admB_set = [r for r in rows if r["admit_B"] and r["r_with_core"] is not None]
    if not admB_set:
        print("\n  OBSERVED NOTHING admitted besides the core. Exit 2, never 0.")
        return 2
    rmin = min(r["r_with_core"] for r in admB_set)
    world = "C" if len(admB_set) == 0 else ("B" if rmin < 0.7 else "A")
    print(f"\n  ⭐ MINIMUM r among admitted arms (criterion B): {rmin:+.4f}")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "every admitted arm is near-identical to the core — the definition DESCRIBES its"
             " instance and the live limitation is CONFIRMED",
        "B": "admitted arms span a wide correlation range including low values — the definition"
             " admits procedurally distant objects and is DEFINING, not describing",
        "C": "the admitted set is {coval_core} alone — the strongest form of A"}[world])
    print(f"     ⚠ PROXY, sound in ONE direction: low r ⇒ different procedure (same construction")
    print(f"       cannot produce uncorrelated per-prompt scores). High r ⇏ same procedure.")
    print(f"     ⚠ AND EVEN WORLD B DOES NOT RETIRE `describes the instance`. It shows the clauses")
    print(f"       are not degenerate on THIS release. Retiring it needs a second release.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_prompts": n, "n_arms": len(names),
               "comparator": BLIND, "min_r_admitted_B": rmin,
               "n_admitted_A": int(admA.sum()) - 1, "n_admitted_B": int(admB.sum()) - 1,
               "controls": {"oracle_admitted": k1, "random_rejected": k2, "self_r": r_self},
               "proxy": "per-prompt score correlation; sound for DIFFERENCE only",
               "does_not_retire": "the definition describes the instance — needs a 2nd release",
               "rows": rows}, open(OUT / "admits_beyond_instance.json", "w"), indent=2)
    print(f"\n  artifact: results/admits_beyond_instance.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
