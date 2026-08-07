#!/usr/bin/env python3
"""R1017 — does a BELONGING clause add anything to clause ②, and is it even evaluable?

⛔ WHY. R1016 established that discriminativeness measures whether criteria BELONG to this prompt —
shams fall resolvably, 5 of 5 — and NOT whether they are good, since random draws from the prompt's
own pool sit at chance. So it can support a belonging clause and not a merit one. R1016's NEXT: does
a belonging clause add anything to clause ②, whose comparator is prompt-blind and may already exclude
everything a belonging test would?

⭐ THE NATURAL FORM IS SELF-REFERENTIAL AND MENTIONS NO RIVAL:
      ⑤  an arm BELONGS iff it discriminates resolvably more than THE SAME CRITERIA ON THE WRONG
         PROMPT — i.e. it beats its own sham.
   That is the only form that needs no threshold, no comparator and no calibration against another
   arm, which is what makes it worth testing rather than the version that would have needed a cut.

ESTIMAND        ① IDENTIFICATION FIRST: for how many arms is ⑤ evaluable at all?
                ② among those, the 2×2 against clause ②: does belonging admit anything ② rejects,
                   and does ② admit anything that fails belonging?
IDENTIFICATION  ⚠ AND IT IS THE ROUND'S FIRST RESULT, NOT A PRELIMINARY. A sham must be SCORED by the
                judge, not computed from an arm's outputs: misdirecting criteria changes which
                (criterion, response) pairs exist, so there is no way to derive a sham's satisfaction
                matrix from its parent's. ⑤ is therefore evaluable ONLY for arms whose sham was
                actually run. This round counts them before comparing anything.
SCOPE           population : every arm with a satisfaction matrix, then the sub-population with a
                             scored sham · instrument : discriminativeness, R1015's quantity
                baseline   : clause ②'s admitted set, READ from R1000 · regime : this release
WORLDS          A ⑤ ADDS      some arm passes ⑤ and fails ②, or vice versa. The two clauses cut the
                             space differently and ⑤ is worth stating.
                B ⑤ IS WEAKER everything ② admits also belongs, and belonging admits strictly more.
                             Then ⑤ adds nothing to a conjunction that already contains ②.
                C NOT EVALUABLE too few arms have a scored sham for the question to be answered at
                             all. Then ⑤ is not a clause a definition can apply to candidates, and
                             THAT is the finding.
                prediction matrix: A -> the off-diagonal cells are non-empty. B -> ②⊆⑤ strictly.
                                   C -> the evaluable set is a small fraction of the population.
KILL            pre-registered: if fewer than 10% of arms have a scored sham, world C is reported as
                the headline — a clause that cannot be evaluated for 90% of candidates is not a
                clause, whatever its 2×2 says on the remainder.
POSITIVE CTRL   `coval_core` must pass ⑤ — R1015/R1016 measured +0.013993 [+0.012817, +0.015174]. If
                the instance fails its own belonging test, the clause is mis-specified.
NEGATIVE CTRL   every SHAM, treated as a candidate, must FAIL ⑤ against its own parent — a
                misdirected arm must not certify as belonging. This is the direction that matters:
                a belonging test a sham passes is not a belonging test.
PLACEBO         an arm against itself gives exactly 0, so it fails the strict `lo > 0` test. A
                clause that admits an arm for beating itself is degenerate.
NOISE FLOOR     the deterministic pair's interval width, measured.
MULTIPLICITY    every evaluable arm × 2 clauses = the full 2×2, all cells printed including empty.
ARTIFACT        results/belonging_vs_clause_two.json with this file's source hash.
IMPOSSIBLE      ⚠ evaluating ⑤ for the 90%+ of arms with no scored sham — N/A, and it is the point:
                it would require running the judge on a misdirected version of every candidate,
                which R921 prices at 15,488 judge calls for ONE new scored object.
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
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets  # noqa: E402

NBOOT, SEED = 8000, 1017
L = "ABCD"


def main() -> int:
    r1000 = next(A27.glob("R1000_*/results/conjunction.json"), None)
    r1016 = next(A27.glob("R1016_*/results/preregistered_exclusion.json"), None)
    if not (r1000 and r1016):
        print("  UNRUNNABLE: a committed artifact is missing. Exit 2, never 0.")
        return 2
    conj = json.loads(r1000.read_text())
    pop = conj["population_arms"]
    c2 = set(conj["cells"]["generic"]["conjunction"]) & \
        set(conj["cells"]["genericpool16"]["conjunction"])
    print(f"  clause ②′ admitted set READ from R1000: {len(c2)} arms")

    tg, _ = load_targets()
    S0 = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    n = len(pids)

    def disc(nm):
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
                sp = Sa.get(p)
                if not sp:
                    continue
                crit = sorted({i for i, _ in sp})
                if not crit:
                    continue
                M = np.array([[sp.get((i, x), 0.0) for x in L] for i in crit], float)
                v[k] = float(M.var(axis=1).mean())
            return np.nan_to_num(v, nan=np.nanmean(v)) if np.isfinite(v).sum() >= 200 else None
        return None

    scored = sorted({p.name[4:-4] for d in (RES, NEW) if d.is_dir() for p in d.glob("sat_*.npz")})
    # ---------- IDENTIFICATION, FIRST AND AS A RESULT ----------
    evaluable = sorted(a for a in pop if f"{a}_sham" in scored)
    share = len(evaluable) / len(pop)
    print(f"\n  ⚠ IDENTIFICATION FIRST — clause ⑤ needs a SCORED sham per candidate. A sham cannot be")
    print(f"    derived from its parent's matrix: misdirecting criteria changes which (criterion,")
    print(f"    response) pairs exist at all.")
    print(f"    arms in the population        : {len(pop)}")
    print(f"    arms with a SCORED sham       : {len(evaluable)}  ({share:.1%})  {evaluable}")
    if share < 0.10:
        print(f"\n⭐ C NOT EVALUABLE — clause ⑤ can be applied to {share:.1%} of candidates.")
        print("   ⛔ PRE-REGISTERED KILL FIRES: a clause that cannot be evaluated for 90%+ of")
        print("      candidates is NOT A CLAUSE, whatever its 2x2 says on the remainder. It would")
        print("      require running the judge on a misdirected version of every candidate, which")
        print("      R921 prices at 15,488 judge calls for ONE new scored object.")

    V = {}
    for a in set(evaluable) | {f"{x}_sham" for x in evaluable}:
        d = disc(a)
        if d is not None:
            V[a] = d
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(NBOOT, n))

    def paired(a, b):
        d = V[a] - V[b]
        bs = d[idx].mean(axis=1)
        return float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))

    rows, pos_ok, neg_ok = [], False, True
    print(f"\n  {'arm':<16}{'Δ vs own sham':>16}{'lo':>11}  belongs  clause ②  agree")
    for a in evaluable:
        if a not in V or f"{a}_sham" not in V:
            continue
        m, lo, hi = paired(a, f"{a}_sham")
        bel = lo > 0
        in2 = a in c2
        rows.append({"arm": a, "delta": m, "lo": lo, "hi": hi, "belongs": bool(bel),
                     "clause2": bool(in2), "agree": bool(bel == in2)})
        if a == "coval_core":
            pos_ok = bel
        print(f"  {a:<16}{m:>+16.6f}{lo:>+11.6f}  {str(bel):<8}{str(in2):<10}{bel == in2}")
        # NEGATIVE: the sham itself, as a candidate, must FAIL against its parent
        sm, slo, shi = paired(f"{a}_sham", a)
        if slo > 0:
            neg_ok = False
    z_m, z_lo, z_hi = paired("coval_core", "coval_core") if "coval_core" in V else (np.nan,) * 3
    plac_ok = z_lo == 0.0 and not (z_lo > 0)
    print(f"\n  POSITIVE — `coval_core` must pass ⑤: {'PASS' if pos_ok else '⛔ FAIL'}")
    print(f"  NEGATIVE — every sham, as a candidate, must FAIL ⑤ against its parent: "
          f"{'PASS' if neg_ok else '⛔ FAIL'}")
    print(f"  PLACEBO  — an arm against itself gives {z_m:+.6f} and fails the strict lo>0 test: "
          f"{'PASS' if plac_ok else '⛔ FAIL'}")
    if not (pos_ok and neg_ok and plac_ok):
        print("\n⛔ a control failed; the 2x2 below certifies nothing. Exit 2, never 0.")
        return 2

    b_only = [r["arm"] for r in rows if r["belongs"] and not r["clause2"]]
    c_only = [r["arm"] for r in rows if r["clause2"] and not r["belongs"]]
    both = [r["arm"] for r in rows if r["belongs"] and r["clause2"]]
    none = [r["arm"] for r in rows if not r["belongs"] and not r["clause2"]]
    print(f"\n  THE 2x2 over the {len(rows)} evaluable arms (every cell printed, empty included)")
    print(f"    belongs AND clause ②      {len(both):>2}  {both}")
    print(f"    belongs, NOT clause ②     {len(b_only):>2}  {b_only}")
    print(f"    clause ②, NOT belongs     {len(c_only):>2}  {c_only}")
    print(f"    neither                   {len(none):>2}  {none}")

    if share < 0.10:
        world = (f"C NOT EVALUABLE — ⑤ applies to {len(evaluable)} of {len(pop)} arms ({share:.1%})")
    elif c_only:
        world = f"A ⑤ ADDS — {c_only} pass clause ② and FAIL belonging"
    elif b_only:
        world = (f"B ⑤ IS WEAKER — everything clause ② admits also belongs, and belonging admits "
                 f"{len(b_only)} more: {b_only}")
    else:
        world = "A ⑤ ADDS — the two clauses coincide exactly on the evaluable set"
    print(f"\n⭐ {world}")
    if share >= 0.10 and not c_only and b_only:
        print("⛔ So ⑤ adds NOTHING to a conjunction that already contains ②: it is implied by it on")
        print("   this sample, and stating it would be decoration.")
    print(f"\n⚠ AND THE 2x2 RESTS ON {len(rows)} ARMS. Whatever it shows is a bound from a handful,")
    print("   not a law — which is the same limit as the identification result above, seen from the")
    print("   other side.")

    out = HERE / "results" / "belonging_vs_clause_two.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="does a belonging clause add anything to clause ②, and is it evaluable",
        n_prompts=n, nboot=NBOOT, seed=SEED, n_population=len(pop),
        n_evaluable=len(evaluable), evaluable_share=share, evaluable=evaluable,
        controls={"positive_core_belongs": bool(pos_ok), "negative_shams_fail": bool(neg_ok),
                  "placebo_self_fails": bool(plac_ok)},
        rows=rows, both=both, belongs_only=b_only, clause2_only=c_only, neither=none, world=world,
        identification_note="a sham must be SCORED, not computed: misdirecting criteria changes "
                            "which (criterion, response) pairs exist, so a sham's satisfaction "
                            "matrix cannot be derived from its parent's",
        price="R921 records 15,488 judge calls for one new scored object",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
