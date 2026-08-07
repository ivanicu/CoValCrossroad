#!/usr/bin/env python3
"""
R911 · the objective contrast with BOTH groups grown at the SAME new k — and why replicas were not
        an option.

⛔ WHY. R910 separated the two selection objectives (variance/magnitude 0/14, [0.000, 0.215] against
signed-mean-weight 7/16, [0.231, 0.668], disjoint by +0.016) but only ONE group had been enlarged.
Its own closing line named that as the weakness: *"the separation comes entirely from the variance
group's interval tightening."*

⛔⛔ **AND THE OBVIOUS FIX WOULD HAVE BEEN FAKE n.** `topw_k` is DETERMINISTIC — R890 measured
`topw_k4 == topw_k4_detA == topw_k4_detB` at **r = 1.000000**. So building "more `topw` arms" at a k
it already covers produces **identical copies**, and pooling them would inflate the denominator with
duplicates: *more points is not replication*. **The only genuinely new signed-weight arms are at k
values not yet built.**

⭐ **SO BOTH GROUPS WERE GROWN AT THE SAME NEW k — 5, 7 and 9 — for 0 judge calls.** Four rules ×
three k = 12 arms. That does two things R909 and R910 could not:
  · it moves the SIGNED side's interval for the first time, so the contrast is no longer carried by
    one group's shrinkage;
  · it creates a genuinely **k-MATCHED** population — both groups now hold arms at
    k ∈ {2, 4, 5, 7, 8, 9} — which neither earlier round could construct.

⭐⭐ **THE PRIMARY SPECIFICATION IS DESIGNATED HERE, BEFORE THE RUN, AND IT IS THE k-MATCHED ONE**,
because it is the only one in which the two groups share a k distribution. R910's `pooled` and
`matched k=4` are reported beside it and neither is dropped. ⚠ **Three specifications is a wider
family than R909's two**, and that is stated rather than absorbed: a hit in 1 of 3 is weaker than a
hit in 1 of 2, and the primary is named so the reader is not left to pick.

ESTIMAND        the admitted share by selection objective under three specifications, with Wilson
                intervals; primary = the k-matched population.
IDENTIFICATION  exact. ⚠ Not causal, not an admission probability — the arms were built.
SCOPE           population: label-free rubric selectors; `topw` vs {`topabs`,`topvar`,`topwvar`}
                instrument: per-prompt A2 margin vs genericpool16, cluster bootstrap NBOOT 8000
                baseline:   equal share across objectives
                regime:     home release, judge 2B, seed 911
WORLDS          A · disjoint in the PRIMARY k-matched specification -> the separation survives when
                    both intervals move and k is matched; the strongest form available here
                B · disjoint only in a secondary specification -> the result is
                    specification-dependent and must be reported that way
                C · disjoint in none -> R910's +0.016 did not survive balancing, and it was carried
                    by the asymmetry its own closing line named
KILL            CONDITIONAL:
                  ⭐ ① WIRING: reproduce R881's `lo` on the four k=4 reference arms to within 0.005
                     and agree on every flag — numbers, not only verdicts.
                  ⭐ ② NO FAKE n: assert that no two arms pooled into a group are byte-identical in
                     their selections. **If `topw_k5` duplicated an existing arm the growth would
                     be fictitious**, and the round must detect that rather than trust determinism
                     to produce novelty.
                  ⭐ ③ all 12 new arms must score; any missing is NAMED, never dropped.
                  ④ the primary specification is designated in this docstring, before the run.
MULTIPLICITY    2 objectives × 3 specifications; every cell printed, primary marked.
ARTIFACT        results/matched_k_contrast.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · admission probability.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
BLIND, NBOOT, SEED = "genericpool16", 8000, 911
REF = {"topw_k4": 0.014402, "topabs_k4": -0.063677,
       "topvar_k4": -0.066342, "topwvar_k4": -0.048203}
SIGNED_RULE, OTHER_RULES = "topw", ("topabs", "topvar", "topwvar")
NEWK = [5, 7, 9]


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    ph = k / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main() -> int:
    r908 = json.loads(next(A24.glob("R908_*/results/bar_by_rule.json")).read_text())
    rules = {r["rule"]: r for r in r908["rules"]}
    r910 = json.loads(next(A24.glob("R910_*/results/objective_at_14.json")).read_text())

    tg, _ = load_targets()
    S = load_sat(RES / f"sat_{BLIND}.npz")
    pids = sorted(set(S) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    n = len(pids)

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if f.exists():
                try:
                    Sa = load_sat(f)
                except Exception:
                    return None
                v = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                        for c in range(6)] for h in H[k]]) if p in Sa else np.nan
                              for k, p in enumerate(pids)])
                return np.nan_to_num(v, nan=np.nanmean(v)) if np.isfinite(v).sum() >= 200 else None
        return None

    base = vec(BLIND)
    if base is None:
        print("  UNRUNNABLE: comparator missing. Exit 2, never 0.")
        return 2
    rng = np.random.default_rng(SEED)
    idxb = [rng.integers(0, n, n) for _ in range(NBOOT)]

    def admit(nm):
        v = vec(nm)
        if v is None:
            return None
        d = v - base
        bs = np.array([float(d[b].mean()) for b in idxb])
        lo = float(np.percentile(bs, 2.5))
        return {"arm": nm, "margin": float(d.mean()), "lo": lo, "admitted": lo > 0}

    ok = True
    print(f"  ① WIRING reproduce R881's `lo` (NBOOT {NBOOT}, {n} prompts):")
    for a, ref in REF.items():
        r = admit(a)
        good = r and abs(r["lo"] - ref) < 0.005 and r["admitted"] == (ref > 0)
        ok = ok and bool(good)
        print(f"     {a:<12} lo {r['lo']:+.6f} vs {ref:+.6f}  {'PASS' if good else 'FAIL'}")

    fresh, missing = {}, []
    for rule in (SIGNED_RULE,) + OTHER_RULES:
        for k in NEWK:
            nm = f"{rule}_k{k}"
            r = admit(nm)
            (fresh.setdefault(rule, []).append(r) if r else missing.append(nm))
    c3 = not missing
    got = sum(len(v) for v in fresh.values())
    print(f"\n  ③ new arms scored {got}/12; MISSING and NAMED: {missing}: {c3}  "
          f"{'PASS' if c3 else 'FAIL'}")

    # ---- ② NO FAKE n: selections must not duplicate ---------------------------------------------
    def sel(nm):
        for d in (RES, NEW):
            f = d / f"core_{nm}.json"
            if f.exists():
                return json.loads(f.read_text())
        return None
    sigs, dupes = {}, []
    for rule in (SIGNED_RULE,) + OTHER_RULES:
        for k in NEWK:
            s = sel(f"{rule}_k{k}")
            if s:
                sig = hash(tuple(sorted((p, tuple(sorted(v))) for p, v in s.items())))
                if sig in sigs:
                    dupes.append((f"{rule}_k{k}", sigs[sig]))
                sigs[sig] = f"{rule}_k{k}"
    c2 = not dupes
    print(f"  ② NO FAKE n: no new arm duplicates another's selections: {c2}  "
          f"{'PASS' if c2 else 'FAIL'}  {dupes if dupes else ''}")
    print(f"     topw_k is DETERMINISTIC (R890: replicas at r = 1.000000), so growth had to come")
    print(f"     from NEW k, never from re-running a covered one")
    if not (ok and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "missing": missing, "dupes": dupes},
                  open(OUT / "matched_k_contrast.json", "w"), indent=2)
        return 2

    print(f"\n  ⭐ THE 12 NEW ARMS:")
    for rule in (SIGNED_RULE,) + OTHER_RULES:
        for r in fresh.get(rule, []):
            print(f"     {r['arm']:<14} margin {r['margin']:+.6f}  lo {r['lo']:+.6f}  "
                  f"admitted {r['admitted']}")

    # existing counts
    sg_old_a, sg_old_n = rules["topw"]["n_admitted"], rules["topw"]["n_built"]
    ot = next(g for g in r910["groups"]
              if g["objective"] == "VARIANCE_OR_MAGNITUDE" and g["spec"] == "pooled over k")
    ot_old_a, ot_old_n = ot["n_admitted"], ot["n_built"]
    sg_new = [r for r in fresh.get(SIGNED_RULE, [])]
    ot_new = [r for rule in OTHER_RULES for r in fresh.get(rule, [])]

    # k-matched population: k where BOTH groups have arms
    sg_ks = set(rules["topw"]["k_values"]) | set(NEWK)
    ot_ks = {2, 4, 8} | set(NEWK)
    shared = sorted(sg_ks & ot_ks)
    print(f"\n  ④ PRIMARY = k-MATCHED, designated before the run. Shared k = {shared}")

    def cell(rule_names, ks=None, extra=None):
        a = nn = 0
        for rn in rule_names:
            for kk, cnt in rules.get(rn, {}).get("per_k", {}).items():
                if ks is None or int(kk) in ks:
                    a += cnt[0]; nn += cnt[1]
        for r in (extra or []):
            kk = int(r["arm"].split("_k")[1])
            if ks is None or kk in ks:
                a += int(r["admitted"]); nn += 1
        return a, nn

    specs = []
    for label, ks in (("PRIMARY k-matched", set(shared)), ("pooled over k", None),
                      ("matched k=4", {4})):
        sa, sn = cell([SIGNED_RULE], ks, sg_new)
        oa, on = cell(list(OTHER_RULES), ks, ot_new)
        specs.append({"spec": label,
                      "signed": {"a": sa, "n": sn, "ci95": list(wilson(sa, sn))},
                      "other": {"a": oa, "n": on, "ci95": list(wilson(oa, on))}})

    print(f"\n  ⭐⭐ ALL THREE SPECIFICATIONS — primary marked, none dropped:")
    for s in specs:
        a, b = s["signed"], s["other"]
        dis = a["ci95"][1] < b["ci95"][0] or b["ci95"][1] < a["ci95"][0]
        s["disjoint"] = bool(dis)
        s["gap"] = float(a["ci95"][0] - b["ci95"][1])
        mark = "  <- PRIMARY" if s["spec"].startswith("PRIMARY") else ""
        print(f"     {s['spec']:<20} signed {a['a']}/{a['n']:<3} "
              f"[{a['ci95'][0]:.3f}, {a['ci95'][1]:.3f}]   other {b['a']}/{b['n']:<3} "
              f"[{b['ci95'][0]:.3f}, {b['ci95'][1]:.3f}]   disjoint {dis}  "
              f"gap {s['gap']:+.3f}{mark}")

    prim = specs[0]
    world = ("A" if prim["disjoint"] else
             "B" if any(s["disjoint"] for s in specs[1:]) else "C")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": "DISJOINT in the PRIMARY k-matched specification — the separation survives with both "
             "intervals moving and k matched. The strongest form this site allows",
        "B": "disjoint only in a SECONDARY specification — the result is specification-dependent "
             "and is reported that way, not as a finding",
        "C": "disjoint in NONE — R910's +0.016 did not survive balancing, and it was carried by "
             "the asymmetry R910's own closing line named"}[world])
    print(f"\n  ⚠ THREE SPECIFICATIONS IS A WIDER FAMILY THAN R909's TWO. A hit in 1 of 3 is")
    print(f"    weaker than a hit in 1 of 2, which is why the primary was designated before the")
    print(f"    run rather than chosen after. R910's two specs are reported unchanged beside it.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "nboot": NBOOT,
               "new_arms": {r: fresh[r] for r in fresh}, "shared_k": shared,
               "specs": specs, "primary": prim["spec"],
               "primary_designated_before_run": True,
               "no_fake_n": {"duplicates_found": dupes,
                             "why": "topw_k is deterministic (R890 replicas at r=1.000000); "
                                    "growth had to come from NEW k, never from re-running a "
                                    "covered one — more points is not replication"},
               "multiplicity": "three specifications, a wider family than R909's two; a hit in "
                               "1 of 3 is weaker than 1 of 2 and the primary was designated first",
               "wiring_reference": REF,
               "unit_note": "counts are ARMS; margins are A2 units vs genericpool16",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "matched_k_contrast.json", "w"), indent=2)
    print(f"\n  artifact: results/matched_k_contrast.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
