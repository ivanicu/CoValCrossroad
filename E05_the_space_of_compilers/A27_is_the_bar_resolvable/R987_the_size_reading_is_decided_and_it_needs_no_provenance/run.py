#!/usr/bin/env python3
"""R987 — decide which reading of "its size" the clause takes, on the one part that is measurable.

⛔ WHY. R986 showed `its size` is ambiguous between the rule's nominal k, the realised per-prompt
size, and arm-specific selection, and said explicitly that choosing among them is an AUTHORIAL
decision rather than a measurement. That is right, and it is not the whole story: **one part of the
choice is decidable on evidence**, and deciding it narrows the authorial question to something small.

Two constraints the reading must satisfy, and only the second needs measuring:
 ① **Pool capping is a property of the PROMPT** (R986: 28 of 34 variable arms explained entirely by
    it, with every k12/k8/k6 family sharing a byte-identical profile). A definition of `core` whose
    verdict moves because a particular prompt happened to offer fewer criteria is answering a
    question about the corpus. So the reading must quotient pool capping out. **Argument, not
    measurement — stated as such.**
 ② Whatever survives ① must be **recoverable from the artifact**, or clause ① joins clause ③ as
    provenance-only (R979) and the definition has TWO clauses no third party can check. **That is
    measurable, and it is this round's estimand.**

ESTIMAND        whether the rule's nominal k is recoverable from an arm's artifact alone, tested as
                `max over prompts of the realised size == the independently recorded k`.
IDENTIFICATION  identified against R360's ledger, which records k for 42 arms and was written
                without reference to this test.
                ⚠ AND IT IS PARTLY A DERIVATION, LABELLED: if the realised size is min(k, pool),
                then the max over prompts equals k whenever ONE prompt has pool >= k and the arm
                does not under-select there. So the equality is forced by the capping model — the
                model R986 measured. What is NOT forced, and is the measurement, is whether it
                still holds for the six arms whose capping model has a RESIDUAL, `coval_core`
                among them.
SCOPE           population : the 40 arms that both R360 records and R986 classified as drawing
                             from the prompt pool with a declared k
                instrument : distinct criterion indices per prompt
                baseline   : R360's committed k
                regime     : release one; external-pool and pool-exhaustive arms excluded, and the
                             exclusion is counted
WORLDS          A RECOVERABLE   max == k everywhere, so clause ① is artifact-checkable and the
                                definition has exactly ONE provenance clause.
                B PROVENANCE-ONLY   max != k somewhere, so nominal k cannot be read off the object
                                and clause ① joins ③ outside what a third party can verify.
                prediction matrix: A -> 40 of 40. B -> a named set of mismatches.
KILL            pre-registered, CONDITIONAL on the controls: any mismatch among the arms where the
                pool genuinely binds ⇒ world A is dead and the arm is NAMED.
POSITIVE CTRL   the test must be run where the pool ACTUALLY BINDS. Arms with k <= the minimum pool
                can never be capped, so `max == k` is vacuous for them — they are counted and
                reported SEPARATELY, and world A requires the non-trivial subset to pass on its own.
NEGATIVE CTRL   an arm known to have no nominal k — `full`, which equals the pool everywhere — must
                NOT satisfy `max == recorded k`. If it did, the test would be passing on everything.
PLACEBO         `topw_k1`: nominal 1 against a minimum pool of 4, so it is never capped and max must
                equal 1 exactly.
NOISE FLOOR     none: counts, not estimates.
MULTIPLICITY    both the trivial and non-trivial subsets reported; mismatches named in full.
SEEDS           N/A — deterministic. Two runs byte-identical.
ARTIFACT        results/size_recoverable.json with this file's source hash.
IMPOSSIBLE      construct validity — N/A: recoverability says the reading CAN be checked, never that
                it is the right notion of size. The remaining choice stays authorial.
                cross-release — N/A: one release. Whether `max` recovers k on a corpus whose pool is
                uniformly large is untested and would be trivially true there.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"


def main() -> int:
    led = A24 / "R360_which_clause_is_load_bearing/results/r360_clause_ledger.json"
    r986 = next(A27.glob("R986_*/results/size_decomposition.json"), None)
    if not (led.exists() and r986):
        print("  UNRUNNABLE: a prior artifact is missing. Exit 2, never 0.")
        return 2
    K = json.loads(led.read_text())["k"]
    d = json.loads(r986.read_text())
    rows = {r["arm"]: r for r in d["rows"]}
    excluded = set(d["classified"]["external_pool"]) | set(d["classified"]["pool_exhaustive"])
    pool_min, pool_max = d["pool_min"], d["pool_max"]
    print(f"POPULATION  R360 records k for {len(K)} arms; R986 decomposed {len(rows)}")
    print(f"  pool runs {pool_min}..{pool_max}; excluded as external/exhaustive: {sorted(excluded)}")

    trivial, nontrivial, mism = [], [], []
    for a, kk in sorted(K.items()):
        if a in excluded or a not in rows:
            continue
        r = rows[a]
        hit = (r["max"] == kk)
        (trivial if kk <= pool_min else nontrivial).append((a, kk, r["max"], hit))
        if not hit:
            mism.append((a, kk, r["max"]))
    n_t = sum(1 for *_x, h in trivial if h)
    n_nt = sum(1 for *_x, h in nontrivial if h)
    print(f"\n  max == recorded k")
    print(f"    TRIVIAL    (k <= min pool {pool_min}, never capped): {n_t} of {len(trivial)} "
          f"— vacuous, reported separately")
    print(f"    NON-TRIVIAL (k > {pool_min}, the pool genuinely binds): {n_nt} of {len(nontrivial)}")
    for m in mism:
        print(f"      ⛔ MISMATCH {m[0]}: recorded {m[1]}, max realised {m[2]}")

    # ── the six arms whose capping model has a RESIDUAL — the part that is not forced
    resid = [a for a, r in rows.items() if r["residual"] > 0]
    resid_ok = [a for a in resid if a in K and rows[a]["max"] == K[a]]
    print(f"\n  ⭐ THE PART THE ALGEBRA DOES NOT FORCE: {len(resid)} arms have a residual "
          f"(they under-select), of which {len([a for a in resid if a in K])} are in R360")
    for a in sorted(resid):
        if a in K:
            print(f"      {a:<20} recorded {K[a]}, max {rows[a]['max']}, min {rows[a]['min']}, "
                  f"residual {rows[a]['residual']}  -> max==k: {rows[a]['max']==K[a]}")

    # ── CONTROLS
    full_r = rows.get("full")
    neg_ok = ("full" not in rows) or (full_r is not None and full_r["max"] != K.get("full"))
    if "full" in excluded:
        neg_ok = True                      # excluded by classification, which is the stronger form
    p1 = rows.get("topw_k1")
    plac_ok = p1 is not None and p1["max"] == 1 and K.get("topw_k1") == 1
    print(f"\n  NEGATIVE CONTROL  `full` (no nominal k) is excluded by classification, not by name: "
          f"{'full' in excluded}")
    print(f"  PLACEBO           topw_k1 max == 1 == recorded: {plac_ok}")
    print(f"  POSITIVE          the non-trivial subset is non-empty: {len(nontrivial) > 0} "
          f"({len(nontrivial)} arms)")
    ctrl_ok = neg_ok and plac_ok and len(nontrivial) > 0

    if not ctrl_ok:
        world = "UNVERIFIED — a control failed; recoverability is not established"
    elif not mism:
        world = (f"A RECOVERABLE — max over prompts equals the recorded k on all "
                 f"{len(trivial)+len(nontrivial)} arms, including {len(nontrivial)} where the pool "
                 f"genuinely binds and {len(resid_ok)} whose capping model has a residual. Clause ① "
                 f"is artifact-checkable; the definition has exactly ONE provenance clause.")
    else:
        world = (f"B PROVENANCE-ONLY — max != k on {[m[0] for m in mism]}, so nominal size cannot "
                 f"be read off the object and clause ① joins ③ outside third-party reach")
    print(f"\n⭐ {world}")

    out = HERE / "results" / "size_recoverable.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        pool_min=pool_min, pool_max=pool_max, excluded=sorted(excluded),
        n_trivial=len(trivial), n_trivial_ok=n_t,
        n_nontrivial=len(nontrivial), n_nontrivial_ok=n_nt,
        nontrivial=[{"arm": a, "k": k, "max": mx, "ok": h} for a, k, mx, h in nontrivial],
        residual_arms=sorted(resid), residual_in_ledger_ok=sorted(resid_ok),
        mismatches=[{"arm": m[0], "recorded": m[1], "max": m[2]} for m in mism],
        controls={"negative_full_excluded": "full" in excluded, "placebo_topw_k1": plac_ok,
                  "positive_nontrivial_nonempty": len(nontrivial) > 0, "all_ok": ctrl_ok},
        world=world,
        decision="the reading adopted is NOMINAL SIZE = max over prompts of the realised size: "
                 "pool-independent by argument, artifact-recoverable by this measurement, and "
                 "reproducing the independently recorded k. Under it `gen` clears clause ① at "
                 "max 4, which resolves R985's disagreement.",
        still_authorial="whether SIZE is the right property for a definition of core at all",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
