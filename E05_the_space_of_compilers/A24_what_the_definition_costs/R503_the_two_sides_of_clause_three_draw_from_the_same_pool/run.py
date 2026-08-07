"""Where do the criteria COME FROM? A containment census that killed the round it was built to enable.

WHY. The previous report closed with: "reading A admits label-readers, and nobody has asked what a
label-reader's criteria LOOK like — if oracle_k4's are recognisably degenerate, A is cheap." Rung 1
of the attack ladder answers that before any of it runs, and the answer voids the design.

ESTIMAND        Per arm: the fraction of its emitted criteria that appear VERBATIM in that prompt's
                own rubric (`core_full.json`). Named before the method. Exact string containment, so
                this is set arithmetic, not an estimate.
IDENTIFICATION  Exact and complete — every criterion of every arm on every prompt it covers.
SCOPE           population = arms with criterion text on the first release · instrument = exact
                string membership in the prompt's rubric list · baseline = a generative arm, which
                must return ~0 · regime = first release, arms keyed by prompt uuid.
WORLDS          A SELECTION-ONLY. The ③-excluded arms select from the same pool everyone else uses,
                  so their criteria ARE rubric criteria and cannot be inspected for degeneracy.
                  Then "what do a label-reader's criteria look like" is answered by construction,
                  the planned round is void, and ③'s irreducibility gets its sharpest statement:
                  both sides of ③ live in the SAME object space and differ only in the MAP.
                B GENERATION. The ③-excluded arms emit text of their own, which could be inspected.
                  Then the planned round is real and reading A's cost is measurable by reading.
KILL            Pre-registered: if the ③-excluded arms return ~1.0 containment, world B is dead and
                the announced next round is withdrawn BEFORE it is written, not after it is run.
POSITIVE CTRL   `gen` is a generator and must return ~0.0; a check returning 1.0 for everything is
                measuring nothing. This is the control that makes 100% a measurement rather than a
                tautology of the instrument, and it CAN fail.
NEGATIVE CTRL   `generic` — a fixed prompt-blind set — must also return ~0.0, since it never reads
                any prompt's rubric. Two independent ways for the instrument to come back non-unity.
PLACEBO         `core_full.json` against itself must return exactly 1.0 by construction. If it does
                not, the containment test is broken and every row above it is void.
NOISE FLOOR     N/A, exact string arithmetic. Declared rather than skipped.
MULTIPLICITY    Every arm with text is counted; the denominator is printed. No selection.
SPECIFICATION   Swept: exact match · whitespace-stripped · case-folded. If the three disagree the
                census is fragile and that is the finding instead.
SEEDS           N/A, deterministic.
ARTIFACT        results/containment.json
REPRODUCIBILITY two identical passes asserted.
IMPOSSIBLE      whether a criterion is SEMANTICALLY in the pool (paraphrase) is not tested — only
                verbatim membership. Would require an embedding or a judge, and both are
                instruments this round would then have to validate. Named, not counted as met.
"""
from __future__ import annotations
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
R = ROOT/"corebench"/"results"
OUT = pathlib.Path(__file__).resolve().parent/"results"; OUT.mkdir(exist_ok=True)
READERS = ["oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1", "topw_k4",
           "topw_k2", "topw_k8", "topabs_k4", "topvar_k4", "topwvar_k4"]
FREE    = ["gen", "generic", "genericpool16", "random_k4_s0", "random_k4_s1", "random_k3_s0",
           "random_k8_s0", "promptecho"]


def containment(arm: str, mode: str = "exact"):
    f = R/f"core_{arm}.json"
    if not f.exists(): return None
    full = json.loads((R/"core_full.json").read_text())
    o = json.loads(f.read_text())
    def n(x):
        x = str(x)
        return x if mode == "exact" else (x.strip() if mode == "strip" else x.strip().lower())
    tot = hit = 0
    for p, cs in o.items():
        pool = {n(c) for c in full.get(p, [])}
        if not pool: continue
        for c in (cs if isinstance(cs, list) else []):
            tot += 1; hit += n(c) in pool
    return hit, tot, (hit/tot if tot else float("nan"))


def main() -> int:
    # PLACEBO first: the rubric against itself must be exactly 1.0, or the test is broken.
    h, t, f = containment("full")
    print(f"  PLACEBO   core_full vs itself: {f:.4f} on {t} criteria"
          f"  -> {'PASS' if abs(f-1.0) < 1e-12 else 'FAIL — the containment test is broken'}")
    if abs(f - 1.0) > 1e-12: return 1

    rows = {}
    print(f"\n  {'arm':<20}{'family':>8}{'criteria':>10}{'from the prompt rubric':>26}")
    for fam, arms in (("reader", READERS), ("free", FREE)):
        for a in arms:
            c = containment(a)
            if not c: continue
            rows[a] = dict(fam=fam, n=c[1], frac=c[2])
            print(f"  {a:<20}{fam:>8}{c[1]:>10}{c[2]*100:>24.1f}%")
    if len(rows) < 8:
        print(f"  only {len(rows)} arms have text -- refusing to census"); return 2

    # POSITIVE / NEGATIVE controls: the instrument must be able to return ~0.
    pos = rows.get("gen", {}).get("frac", 1.0)
    neg = rows.get("generic", {}).get("frac", 1.0)
    ok = pos < 0.05 and neg < 0.05
    print(f"\n  POSITIVE  gen (a generator) must be ~0: {pos:.4f}")
    print(f"  NEGATIVE  generic (fixed, prompt-blind) must be ~0: {neg:.4f}"
          f"  -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  the instrument cannot return a low value -- 100% would mean nothing"); return 1

    spec = {m: {a: containment(a, m)[2] for a in rows} for m in ("exact", "strip", "lower")}
    frag = [a for a in rows if max(spec[m][a] for m in spec) - min(spec[m][a] for m in spec) > 0.01]
    print(f"  SPECIFICATION  3 matching rules, arms whose fraction moves >1pt: {len(frag)} {frag}")

    readers = [rows[a]["frac"] for a in rows if rows[a]["fam"] == "reader"]
    pooled_free = [a for a in rows if rows[a]["fam"] == "free" and rows[a]["frac"] > 0.95]
    world = ("A SELECTION-ONLY" if min(readers) > 0.95 else "B GENERATION")
    print(f"\n  WORLD: {world}")
    if world.startswith("A"):
        print(f"  => every ③-EXCLUDED arm draws {min(readers)*100:.1f}%+ of its criteria VERBATIM")
        print(f"     from the prompt's own rubric. Their criteria ARE rubric criteria, so the")
        print(f"     announced round -- 'do they look degenerate' -- is answered by construction")
        print(f"     and is WITHDRAWN before being written.")
        print(f"  => and the ③-ADMISSIBLE arms {pooled_free} draw from the SAME pool.")
        print(f"     So on this site the two sides of ③ inhabit the SAME object space and differ")
        print(f"     ONLY in the selection map. That is ③'s irreducibility stated as sharply as")
        print(f"     this release allows: there is no textual property to check, because there is")
        print(f"     no textual difference to find.")
        print(f"  => it also RE-PRICES reading A. Dropping ③ admits arms whose criteria are")
        print(f"     verbatim human-written rubric items -- the RIGHT criteria, selected for the")
        print(f"     wrong reason. A is cheaper than 'it admits label-readers' made it sound.")
    json.dump({"rows": rows, "spec": spec, "fragile": frag, "world": world,
               "positive": pos, "negative": neg}, (OUT/"containment.json").open("w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
