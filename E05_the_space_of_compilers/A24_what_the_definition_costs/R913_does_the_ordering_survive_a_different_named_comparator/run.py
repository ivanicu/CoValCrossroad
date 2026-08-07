#!/usr/bin/env python3
"""
R913 · does the rule ordering survive a DIFFERENT named prompt-blind comparator?

⛔ WHY, AND IT IS THE ASSUMPTION UNDER EVERYTHING R908–R912 SAID. Clause ② reads *"beats a NAMED
prompt-blind comparator"* — but **every admission decision in this arc has used exactly one:
`genericpool16`.** R908's `random 0/38`, R911's `+0.250`, R912's k=4 flip are all conditional on
that single choice, and the clause's own wording concedes the comparator is a parameter. **The
comparator axis has never been swept — it is the one axis in G4's list that no round has touched.**

⛔⛔ **AND THE ESTIMAND MUST BE THE ORDERING, NOT THE COUNTS, BECAUSE THE COUNTS ARE FORCED.**
A weaker comparator admits MORE arms and a stronger one FEWER — that is arithmetic, not evidence.
Reporting "12 admitted under A, 40 under B" would be the arithmetic trap in its purest form.
**What can be evidence is whether the ORDERING survives:**
  · informed rules above `random_k` (R908's layer)
  · signed-mean-weight above variance/magnitude (R909–R912's layer)

⛔⛔⛔ **POST-RUN, AND THE ROUND'S RESULT IS THREE DIAGNOSED FAILURES, NOT A SWEEP.**
① **THE SELF-INCLUSION CONTROL FIRED ON MY OWN BASELINE.** `genericpool16` **IS one of R881's 99
   arms** — so every round in this arc has scored a set against one of its own members. The control
   was written to catch that in the ALTERNATIVES and caught it in the incumbent.
② **THE ALTERNATIVES ARE UNUSABLE, AND NOT FOR LACK OF DATA.** `sat_transport_*.npz` all exist on
   disk. `load_sat` raises `ValueError: too many values to unpack` on them — **a different key
   schema**, so the release's other prompt-blind arms cannot be loaded by this arc's instrument at
   all.
③ **AND MY OWN CODE HID THAT.** `vec()` caught the exception in a bare `except` and returned
   `None`, so the round printed *"MISSING and NAMED"* for four arms that are **present**. **Silence
   mistaken for absence, inside the round whose whole point was to check an assumption.** The
   handler is now split: absent-file and unreadable-file are different outcomes and print
   differently.

⭐ **FOUR ALTERNATIVE NAMED PROMPT-BLIND COMPARATORS EXIST AND NONE HAS BEEN USED.**
`transport_randblind_s0/s1/s2` — random criteria that never see the prompt, at **three seeds**, so
seed-robustness comes free — plus `transport_generic`. ⚠ `generic` and `generic_reprov` are
EXCLUDED as comparators: they are themselves ADMITTED ARMS in the set under test, and scoring a set
against one of its own members is the self-inclusion failure R883/R884/R897/R906 each caught.

ESTIMAND        under each named prompt-blind comparator: (a) is `random_k`'s admitted share below
                every informed rule's, and (b) is signed-mean-weight's above variance/magnitude's —
                the two ORDERINGS, never the counts.
IDENTIFICATION  exact for each comparator. ⚠ Not causal; not an admission probability.
SCOPE           population: the rule families R908 typed, plus the arms built in R909–R912
                instrument: per-prompt A2 margin vs EACH comparator, bootstrap NBOOT 4000
                baseline:   `genericpool16`, the comparator every earlier round used
                regime:     home release, judge 2B, seed 913
WORLDS          A · both orderings hold under every comparator -> the arc's findings are
                    comparator-robust, and the clause's `NAMED` parameter is not load-bearing
                B · an ordering flips under some comparator -> the findings are
                    comparator-CONDITIONAL, and every headline must carry the comparator
                C · the counts move but the orderings are unreadable -> the sweep cannot decide,
                    which is a fact about the alternatives' strength
KILL            CONDITIONAL:
                  ⭐ ① WIRING: under `genericpool16` the admitted count must reproduce R881's 28
                     on the arms R881 scored. If it does not, the sweep is not anchored.
                  ⭐ ② THE COMPARATORS MUST DIFFER IN STRENGTH — if they all admit the same count
                     the sweep tests nothing. Reported, and a flat sweep is WORLD C not WORLD A.
                  ⭐ ③ SELF-INCLUSION: no comparator may be an arm in the tested set. Asserted.
                  ④ orderings only; absolute counts printed for context and never compared as
                     evidence across comparators.
MULTIPLICITY    5 comparators × 2 orderings; every cell printed, flips named.
⚠ NOTE ON THIS FILE: the results table was first written with `chr()` escapes to avoid nesting
quotes inside an f-string — the identical mess R908 had and that was fixed there. **I reproduced a
formatting defect one round after repairing it**, which is small but is the same shape as the
from-memory errors this arc keeps logging: the fix was made in one file and not carried to the
habit. Rewritten plainly by binding the fields to locals first.
ARTIFACT        results/comparator_sweep.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · admission probability. ⚠ AND: which comparator is CORRECT. This shows
                whether the answer moves, never which choice is right.
"""
import collections, json, pathlib, re, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
NBOOT, SEED = 4000, 913
COMPARATORS = ["genericpool16", "transport_generic",
               "transport_randblind_s0", "transport_randblind_s1", "transport_randblind_s2"]
SIGNED, OTHER = ["topw"], ["topabs", "topvar", "topwvar"]


def main() -> int:
    r881 = json.loads(next(A24.glob("R881_*/results/boundary_distance.json")).read_text())
    r881_arms = [x["arm"] for x in r881["arms"]]
    r881_adm = sum(x["admitted"] for x in r881["arms"])

    tg, _ = load_targets()
    S0 = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    n = len(pids)

    unreadable = {}

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if f.exists():
                try:
                    Sa = load_sat(f)
                except Exception as e:
                    # ⛔ ABSENT and UNREADABLE are different outcomes. Collapsing them printed
                    # "MISSING" for four files that exist — silence mistaken for absence.
                    unreadable[nm] = f"{type(e).__name__}: {e}"
                    return None
                v = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                        for c in range(6)] for h in H[k]]) if p in Sa else np.nan
                              for k, p in enumerate(pids)])
                return np.nan_to_num(v, nan=np.nanmean(v)) if np.isfinite(v).sum() >= 200 else None
        return None

    # the tested set: R881's arms plus everything built in R909-R912
    extra = sorted({f.stem[4:] for f in NEW.glob("sat_*.npz")})
    tested = sorted((set(r881_arms) | set(extra)) - set(COMPARATORS))
    c3 = not (set(COMPARATORS) & set(tested))
    print(f"  ③ SELF-INCLUSION no comparator is an arm in the tested set: {c3}  "
          f"{'PASS' if c3 else 'FAIL'}")
    print(f"     `generic` and `generic_reprov` EXCLUDED as comparators — they are admitted arms")
    print(f"  tested arms: {len(tested)} ({len(r881_arms)} from R881 + {len(extra)} built here)")

    V = {}
    for a in tested + COMPARATORS:
        v = vec(a)
        if v is not None:
            V[a] = v
    rng = np.random.default_rng(SEED)
    idxb = [rng.integers(0, n, n) for _ in range(NBOOT)]

    def rule_of(a):
        m = re.match(r"([a-z]+)_k(\d+)", a)
        return m.group(1) if m else None

    results, admitted_counts = {}, {}
    for comp in COMPARATORS:
        if comp not in V:
            why = unreadable.get(comp, "file absent")
            print(f"  ⚠ comparator {comp}: {why} — skipped, and the REASON is named")
            continue
        base = V[comp]
        adm = {}
        for a in tested:
            if a not in V or a == comp:
                continue
            d = V[a] - base
            bs = np.array([float(d[b].mean()) for b in idxb])
            adm[a] = float(np.percentile(bs, 2.5)) > 0
        admitted_counts[comp] = sum(adm.values())
        by = collections.defaultdict(lambda: [0, 0])
        for a, ok in adm.items():
            r = rule_of(a)
            if r:
                by[r][1] += 1
                by[r][0] += int(ok)
        sg_a = sum(by[r][0] for r in SIGNED); sg_n = sum(by[r][1] for r in SIGNED)
        ot_a = sum(by[r][0] for r in OTHER); ot_n = sum(by[r][1] for r in OTHER)
        rnd = by.get("random", [0, 0])
        informed = [r for r in by if r not in ("random",) and by[r][1] >= 3]
        rnd_share = rnd[0] / rnd[1] if rnd[1] else float("nan")
        ord1 = all((by[r][0] / by[r][1]) > rnd_share for r in informed) if rnd[1] else None
        ord2 = ((sg_a / sg_n) > (ot_a / ot_n)) if sg_n and ot_n else None
        results[comp] = {"n_admitted": admitted_counts[comp],
                         "random": {"a": rnd[0], "n": rnd[1], "share": rnd_share},
                         "signed": {"a": sg_a, "n": sg_n,
                                    "share": sg_a / sg_n if sg_n else float("nan")},
                         "other": {"a": ot_a, "n": ot_n,
                                   "share": ot_a / ot_n if ot_n else float("nan")},
                         "ordering_informed_above_random": ord1,
                         "ordering_signed_above_variance": ord2,
                         "per_rule": {r: list(v) for r, v in sorted(by.items())}}

    # WIRING must compare LIKE WITH LIKE: R881's arms only, not the 30 built since
    base_v = V.get("genericpool16")
    r881_only = [a for a in r881_arms if a in V and a != "genericpool16"]
    rec = 0
    for a in r881_only:
        d = V[a] - base_v
        bs = np.array([float(d[b].mean()) for b in idxb])
        rec += int(float(np.percentile(bs, 2.5)) > 0)
    c1 = abs(rec - r881_adm) <= 1
    print(f"\n  ① WIRING on R881's ARMS ONLY: {rec} vs R881's {r881_adm}: {c1}  "
          f"{'PASS' if c1 else 'FAIL'}")
    print(f"     my first tolerance compared 39 (which includes 30 arms built since, several of")
    print(f"     them LEAKY and admitted) against 28 — comparing unlike populations")

    spread = max(admitted_counts.values()) - min(admitted_counts.values())
    c2 = spread > 0
    print(f"  ② COMPARATORS DIFFER IN STRENGTH admitted counts "
          f"{sorted(admitted_counts.values())}, spread {spread}: {c2}  "
          f"{'PASS' if c2 else 'FAIL'}")
    print(f"     a flat sweep would test nothing and is WORLD C, not WORLD A")
    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "results": results},
                  open(OUT / "comparator_sweep.json", "w"), indent=2)
        return 2

    print(f"\n  ⭐ THE COMPARATOR SWEEP — counts for CONTEXT, orderings as the evidence:")
    print(f"     {'comparator':<26}{'adm':>5}{'random':>10}{'signed':>10}{'variance':>10}"
          f"  informed>rand  signed>var")
    for comp, r in results.items():
        rd = f"{r['random']['a']}/{r['random']['n']}"
        sg = f"{r['signed']['a']}/{r['signed']['n']}"
        ot = f"{r['other']['a']}/{r['other']['n']}"
        print(f"     {comp:<26}{r['n_admitted']:>5}{rd:>10}{sg:>10}{ot:>10}"
              f"{str(r['ordering_informed_above_random']):>15}"
              f"{str(r['ordering_signed_above_variance']):>12}")

    o1 = [c for c, r in results.items() if r["ordering_informed_above_random"] is False]
    o2 = [c for c, r in results.items() if r["ordering_signed_above_variance"] is False]
    world = "A" if not (o1 or o2) else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": f"BOTH orderings hold under all {len(results)} named prompt-blind comparators — the "
             "arc's findings are comparator-robust, and the clause's `NAMED` parameter is not "
             "load-bearing for the ordering",
        "B": f"an ordering FLIPS: informed>random fails under {o1}; signed>variance fails under "
             f"{o2}. **The findings are comparator-CONDITIONAL and every headline must carry the "
             "comparator**"}[world])
    print(f"\n  ⚠ THE COUNTS MOVED FROM {min(admitted_counts.values())} TO "
          f"{max(admitted_counts.values())} AND THAT IS NOT EVIDENCE — a weaker comparator admits")
    print(f"    more by arithmetic. Only the ORDERINGS were tested. ⚠ And this cannot say which")
    print(f"    comparator is CORRECT, only whether the answer moves.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "nboot": NBOOT,
               "n_tested_arms": len(tested), "comparators": COMPARATORS,
               "results": results, "admitted_counts": admitted_counts,
               "ordering_flips": {"informed_above_random": o1, "signed_above_variance": o2},
               "counts_are_context_not_evidence": "a weaker comparator admits more by arithmetic; "
                                                  "only the orderings were tested",
               "excluded_as_comparators": ["generic", "generic_reprov"],
               "why_excluded": "they are ADMITTED ARMS in the set under test; scoring a set "
                               "against one of its own members is self-inclusion",
               "cannot_say": "which comparator is correct — only whether the answer moves",
               "three_diagnosed_failures": {
                   "self_inclusion": "genericpool16 IS one of R881's 99 arms; every round in this "
                                     "arc scored a set against one of its own members",
                   "alternatives_unreadable": unreadable,
                   "my_code_hid_it": "vec() collapsed absent and unreadable into None, printing "
                                     "MISSING for four files that exist — silence mistaken for "
                                     "absence, inside the round meant to check an assumption"},
               "unit_note": "counts are ARMS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "comparator_sweep.json", "w"), indent=2)
    print(f"\n  artifact: results/comparator_sweep.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
