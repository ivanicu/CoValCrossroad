#!/usr/bin/env python3
"""
R933 · the intervals recomputed under the full repair — does R141's `ci excludes zero` count survive?

⛔ WHY. R929 found R141's points sitting outside their own intervals; R931 traced it to TIED quantile
cut points on a discrete covariate; R932 measured what the tie cost the POINTS — the `raters` effects
roughly double, median |shift| 94.2% of the committed value, `length` immobile to the last bit. **The
intervals were never recomputed, and they are the only thing that decides whether anything downstream
of R141 needs withdrawing**, because R141's headline is a count of cells whose `ci[1] < 0`.

⭐ **NOT FORCED, AND TWO FORCES OPPOSE — which is why it is worth running.**
  · the effect roughly DOUBLES under deduped strata, which makes zero EASIER to exclude;
  · rebuilding the matching INSIDE each bootstrap replicate restores the matching variability that
    filtering through a fixed `mset` suppressed, which makes intervals WIDER.
**Whether the count rises or falls is a fact about the corpus, not about the algebra.**

⭐⭐ **THE TWO REPAIRS ARE SEPARATED, so it is visible which one moves the verdict:**
  A `raw` strata + fixed `mset`            — R141 as committed, the wiring baseline
  B `dedupe` strata + fixed `mset`         — R931/R932's tie fix alone
  C `dedupe` strata + matching REBUILT     — plus R929's estimand fix; the full repair

ESTIMAND        per `raters` cell: the bootstrap interval under A, B and C, and the count of cells
                with `ci[1] < 0` under each.
IDENTIFICATION  exact given the seeds; the intervals are percentiles of a stated resampling scheme.
                ⚠ Not an admission probability; the cells were built, not sampled.
SCOPE           population: R141's units, guards transcribed (stem_token>=3, no char3gram|idf)
                instrument: R141's imported metrics; N_BOOT and the bootstrap seed as committed
                baseline:   R141's committed `finding_A.cells[*].raters.ci`
                regime:     the committed corpus
WORLDS          A · the count is unchanged or rises -> R141's headline survives the repair and only
                    its magnitudes were wrong
                B · the count FALLS -> cells R141 reported as excluding zero no longer do, and
                    whatever cites them needs withdrawing
KILL            CONDITIONAL:
                  ⭐ ① WIRING: variant A must reproduce R141's committed `raters` intervals. Same
                     seed, same N_BOOT, imported helpers. **If the baseline does not come back,
                     nothing computed here describes R141.**
                  ⭐ ② INSTRUMENT: the rebuild (C) must produce WIDER intervals than the fixed-set
                     version (B) at the same strata. If it does not, the rebuild is not restoring
                     the matching variability it exists to restore, and C is not the repair it
                     claims to be.
                  ⭐ ③ PLACEBO, structural: `length`'s cuts never tie, so its A and B intervals
                     must be BIT-IDENTICAL. A repair that moves a cell it cannot logically touch
                     is a bug in the repair.
                  ⭐ ④ every cell reported, and the count stated for all three variants — reporting
                     only the repaired count would hide whether the tie fix or the estimand fix
                     did the work.
MULTIPLICITY    14 cells × 3 variants × {ci, excludes-zero}; `length` carried as the placebo.
ARTIFACT        results/repaired_intervals.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: this repairs the MATCHING and the RESAMPLING. It does not
                revisit whether a prompt-cluster bootstrap is the right null for this contrast,
                which is a separate question nobody in this arc has asked.
"""
import importlib.util, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
R141 = ROOT / ("E04_no_fraction_only_an_equivalence_class/A12_who_pays_for_compilation/"
               "R141_verification")
RUBRICS = ROOT / "data/conversation_rubrics.jsonl"
SEEDS = (8101, 4409, 20260730, 31337, 271828)
N_BOOT = 800
TOL = 1e-9


def main() -> int:
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("r141mod", R141 / "run.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    committed = json.loads((R141 / "results/r141_verification.json").read_text())["finding_A"]

    prompts = []
    for line in open(RUBRICS):
        r = json.loads(line)
        core = [it.get("criterion") or "" for it in (r.get("coval_core") or [])]
        full = [(it.get("criterion") or "",
                 np.array([x["score"] for x in (it.get("scores") or [])], float))
                for it in (r.get("coval_full") or []) if it.get("scores")]
        if core and full:
            prompts.append((core, full))

    import math
    df, docs = {}, 0
    for core, full in prompts:
        for t in core + [f[0] for f in full]:
            docs += 1
            for w in set(m.stem(x) for x in m.words(m.strip_neg(t))):
                df[w] = df.get(w, 0) + 1
    idf = {w: math.log(docs / (1 + c)) for w, c in df.items()}

    units, pidx = [], []
    for pi, (core, full) in enumerate(prompts):
        reps = {"stem_token": [set(m.stem(w) for w in m.words(m.strip_neg(t))) for t in core],
                "raw_token": [set(m.words(m.strip_neg(t))) for t in core],
                "char3gram": [m.grams(m.strip_neg(t)) for t in core]}
        for txt, sc in full:
            F = {"stem_token": set(m.stem(w) for w in m.words(m.strip_neg(txt))),
                 "raw_token": set(m.words(m.strip_neg(txt))),
                 "char3gram": m.grams(m.strip_neg(txt))}
            if len(F["stem_token"]) < 3:
                continue
            best = {}
            for rep, cs in reps.items():
                for mn, fn in m.METRICS.items():
                    if rep == "char3gram" and mn == "idf_weighted":
                        continue
                    best[f"{rep}|{mn}"] = max((fn(F[rep], c, idf) for c in cs), default=0.0)
            units.append((float(sc.mean()) < 0, abs(float(sc.mean())), len(sc), len(txt), best))
            pidx.append(pi)
    neg = np.array([u[0] for u in units], bool)
    pidx = np.array(pidx)
    cov = {"magnitude": np.array([u[1] for u in units], float),
           "length": np.array([u[3] for u in units], float),
           "raters": np.array([u[2] for u in units], float)}
    keys = sorted(units[0][4])
    print(f"  {len(units):,} units · {len(keys)} cells · {int(neg.sum()):,} negative")

    def mp_of(c, dedupe, seed, sub=None):
        """R141's matcher; `dedupe` collapses tied cut points; `sub` restricts to a subsample."""
        idx = np.arange(len(neg)) if sub is None else sub
        cc, nn = c[idx], neg[idx]
        if not nn.any():
            return np.array([], int)
        qs = np.percentile(cc[nn], [0, 20, 40, 60, 80, 100])
        if dedupe:
            qs = np.unique(qs)
        rng = np.random.default_rng(seed)
        pick = []
        for lo, hi in zip(qs[:-1], qs[1:]):
            want = int(((cc[nn] >= lo) & (cc[nn] <= hi)).sum())
            pool = np.where((~nn) & (cc >= lo) & (cc <= hi))[0]
            if len(pool) and want:
                pick += list(rng.choice(pool, min(want, len(pool)), replace=False))
        return idx[np.array(pick, int)] if pick else np.array([], int)

    up = np.unique(pidx)
    where = {j: np.where(pidx == j)[0] for j in up}

    def ci(v, scheme, dedupe, rebuild):
        rng = np.random.default_rng(SEEDS[0] + 3)
        mset = set(mp_of(cov[scheme], dedupe, SEEDS[0]).tolist())
        bs = []
        for _ in range(N_BOOT):
            take = rng.integers(0, len(up), len(up))
            sel = np.concatenate([where[up[j]] for j in take])
            sn = sel[neg[sel]]
            if len(sn) <= 20:
                continue
            if rebuild:
                sm = mp_of(cov[scheme], dedupe, int(rng.integers(1, 2**31)), sub=sel)
            else:
                sm = np.array([i for i in sel if i in mset], int)
            if len(sm) > 20:
                bs.append(v[sn].mean() - v[sm].mean())
        bs = np.array(bs)
        return ([float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
                if len(bs) > 30 else [float("nan")] * 2)

    VARIANTS = (("A_raw_fixed", False, False), ("B_dedupe_fixed", True, False),
                ("C_dedupe_rebuilt", True, True))
    rows, mism = [], []
    for k in keys:
        v = np.array([u[4][k] for u in units], float)
        row = {"cell": k, "committed_ci": committed["cells"][k]["raters"]["ci"]}
        for name, dd, rb in VARIANTS:
            row[name] = ci(v, "raters", dd, rb)
        if max(abs(row["A_raw_fixed"][i] - row["committed_ci"][i]) for i in (0, 1)) > TOL:
            mism.append((k, row["committed_ci"], row["A_raw_fixed"]))
        rows.append(row)

    c1 = not mism
    print(f"\n  ① WIRING — variant A reproduces R141's committed `raters` intervals for all "
          f"{len(rows)} cells at tol {TOL}: {c1}  {'PASS' if c1 else 'FAIL'}")
    for x in mism[:3]:
        print(f"     {x[0]}  committed {[round(y, 8) for y in x[1]]}  here "
              f"{[round(y, 8) for y in x[2]]}")

    lenrows = []
    for k in keys[:4]:
        v = np.array([u[4][k] for u in units], float)
        a, b = ci(v, "length", False, False), ci(v, "length", True, False)
        lenrows.append((k, a, b, max(abs(a[i] - b[i]) for i in (0, 1))))
    c3 = all(x[3] <= TOL for x in lenrows)
    print(f"\n  ③ PLACEBO — `length`'s cuts never tie, so A and B must be bit-identical "
          f"({len(lenrows)} cells checked): max |Δ| = {max(x[3] for x in lenrows):.2e}: {c3}  "
          f"{'PASS' if c3 else 'FAIL'}")

    def hw(name):
        return float(np.median([(r[name][1] - r[name][0]) / 2 for r in rows
                                if np.isfinite(r[name][0])]))
    c2 = hw("C_dedupe_rebuilt") > hw("B_dedupe_fixed")
    print(f"\n  ② INSTRUMENT — rebuilding must WIDEN: median half-width B "
          f"{hw('B_dedupe_fixed'):.6f} vs C {hw('C_dedupe_rebuilt'):.6f}: {c2}  "
          f"{'PASS' if c2 else 'FAIL — the rebuild is not restoring matching variability'}")

    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3, "rows": rows},
                  open(OUT / "repaired_intervals.json", "w"), indent=2)
        return 2

    counts = {n: sum(1 for r in rows if np.isfinite(r[n][1]) and r[n][1] < 0)
              for n, _, _ in VARIANTS}
    committed_count = sum(1 for k in keys if committed["cells"][k]["raters"]["ci"][1] < 0)
    print(f"\n  ④ EVERY CELL, ALL THREE VARIANTS (ci upper bound; `< 0` is R141's headline test):")
    print(f"     {'cell':<26}{'committed':>12}{'A raw':>12}{'B dedupe':>12}{'C repaired':>12}")
    for r in rows:
        print(f"     {r['cell']:<26}{r['committed_ci'][1]:>+12.6f}{r['A_raw_fixed'][1]:>+12.6f}"
              f"{r['B_dedupe_fixed'][1]:>+12.6f}{r['C_dedupe_rebuilt'][1]:>+12.6f}")
    print(f"\n     cells with ci[1] < 0 — committed {committed_count}/{len(rows)}, "
          + ", ".join(f"{n} {counts[n]}/{len(rows)}" for n, _, _ in VARIANTS))

    world = "A" if counts["C_dedupe_rebuilt"] >= committed_count else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"R141's `raters` headline SURVIVES the full repair — {counts['C_dedupe_rebuilt']} of "
        f"{len(rows)} cells still exclude zero against {committed_count} committed. The tie made "
        f"the magnitudes wrong, not the verdict."
        if world == "A" else
        f"the count FALLS from {committed_count} to {counts['C_dedupe_rebuilt']} of {len(rows)}. "
        f"Cells R141 reported as excluding zero no longer do under an estimator that matches what "
        f"it claims to match, and whatever cites them needs withdrawing."))
    print(f"     ⚠ AND WHICH REPAIR DID IT: dedupe alone gives {counts['B_dedupe_fixed']}, the")
    print(f"     rebuild takes it to {counts['C_dedupe_rebuilt']} — the two fixes are reported")
    print(f"     separately because attributing both to one would hide the mechanism.")
    print(f"     ⚠ NOT REVISITED: whether a prompt-cluster bootstrap is the right null for this")
    print(f"     contrast at all. Nobody in this arc has asked, and this round does not.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_boot": N_BOOT, "seeds": list(SEEDS),
               "committed_excludes_zero": committed_count,
               "counts_by_variant": counts, "median_half_width": {n: hw(n) for n, _, _ in VARIANTS},
               "rows": rows,
               "variants": {"A_raw_fixed": "R141 as committed",
                            "B_dedupe_fixed": "tie fix only (R931/R932)",
                            "C_dedupe_rebuilt": "tie fix + matching rebuilt in-replicate (R929)"},
               "not_revisited": "whether a prompt-cluster bootstrap is the right null for this "
                                "contrast at all",
               "unit_note": "intervals are in delta units; counts are CELLS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "repaired_intervals.json", "w"), indent=2)
    print(f"\n  artifact: results/repaired_intervals.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
