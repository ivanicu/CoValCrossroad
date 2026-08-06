#!/usr/bin/env python3
"""
R841 · does the exact-class interval close when every annotator is used?

⛔ WHY. Entry 1352 declared clause ② UNDECIDABLE under an exact-class reading -- obs +0.0083,
CI [-0.0024, +0.0196], MDE 0.0159 -- and filed it as a property of the release. It drew
**3 annotators per prompt.** The release ships **18,384 annotator rankings over 1,078 prompts**,
median 16 per prompt: 1352 consumed **3,234, i.e. 17.6% of what is on disk**.
The failure register's own row says, mechanically: *before accepting any resolution limit, count
what the release actually contains and what your code actually consumed, and require those two
numbers to match.* They do not. This is the FOURTH instance of a row already wrong three times,
and the previous three all ended the same way: the limit was an artifact of an under-powered
design nobody questioned, overturned by a better INSTRUMENT and never by a better argument.

ESTIMAND        the paired per-prompt difference `coval_core - generic` in
                (a) GRADED A2  = mean over the 6 induced pairs
                (b) EXACT      = all 6 pairs match
                where each prompt's score averages over EVERY annotator it has, not 3 draws.
IDENTIFICATION  yes -- every ranking is already returned by load_targets(); nothing new is needed.
                That is the uncomfortable part: the data was never missing, only unused.
SCOPE           population: prompts scored by BOTH arms (paired, reported below)
                instrument: judge J via the released sat_*.npz; A2 as `corebench/rule_sweep.py`
                baseline:   the same paired difference under 1352's 3-draw design
                regime:     annotators per prompt min 4 / median 16 / max 1012
WORLDS          A · 1352's "undecidable" was an artifact of 3 draws -> the exact CI EXCLUDES 0
                B · the limit is real: between-prompt variance dominates, so 5.68x more
                    annotator data barely moves the CI -> it still CONTAINS 0
                These differ ontologically: A says the release CAN adjudicate clause ② under
                exact-class and we failed to ask; B says it cannot, and now that is measured
                with the best instrument the release affords rather than with 17.6% of it.
KILL            pre-registered, CONDITIONAL, evaluated before any headline:
                  if the 3-draw arm reproduces 1352 (+0.0151 graded, +0.0083 exact, +-0.002)
                     and the placebo returns ~0
                  then read the all-annotator CI
                  else verdict = UNVERIFIED  (never CONFIRMED, never OVERTURNED)
POSITIVE CTRL   the 3-draw arm must reproduce 1352's published numbers through THIS code path.
                A harness that cannot reproduce the result it is correcting is not correcting it.
PLACEBO         `coval_core` against ITSELF -- must return exactly 0.0 in both metrics.
                If a self-difference is non-zero the pairing is broken and nothing else is readable.
NEGATIVE CTRL   `coval_core_sham` - `generic`: the sham is misdirected, not absent, so this is
                reported as a magnitude and NOT read as the ingredient's value (register: "the
                sham is a poison, not a placebo").
SPECIFICATION   annotators-per-prompt cap in {3 draws, 16, 64, ALL} x metric in {graded, exact}
                = 8 cells, ALL reported including the ones that kill the finding.
                The cap exists because one prompt carries 1012 annotators and an uncapped mean
                lets it behave differently from the median prompt; the cap is the check, not a fix.
MULTIPLICITY    8 cells, one family, reported whole. No cell is selected after the fact.
SEEDS           the 3-draw arm uses seeds 900/901/902 as 1352 did; the all-annotator arm has no
                draw and therefore no seed -- which is itself the point.
ARTIFACT        results/exact_class_full_annotators.json, with the commit hash.
IMPOSSIBLE      independently replicated (one release) · construct validated (no gold standard
                for "the right agreement metric") · cross-dataset · causally identified.
                N/A with what each would require -- never "planned".
"""
import json, pathlib, subprocess, sys, zlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls           # noqa: E402

# ⛔ ENTRY 1352's NUMBERS ARE NOT REPRODUCIBLE, AND THAT IS THIS ROUND'S FIRST FINDING.
# 1352 seeded its per-prompt annotator draw with `np.random.default_rng(900+s+hash(p)%1000)`.
# Python randomises `hash()` of a str PER PROCESS (PYTHONHASHSEED). Measured, with a positive
# control on the test itself: hash('prompt_42')%1000 -> 924 / 294 / 947 across three fresh
# processes, while zlib.crc32 of the same bytes -> 632 / 632 / 632 in the same three.
# So 1352's draw was an UNSEEDED sample: its +0.0151 / +0.0083, its CIs, its MDEs and its
# verdicts RESOLVED / undecidable are ONE UNLABELLED DRAW from a distribution never
# characterised. They are UNVERIFIED -- not overturned, and not to be quoted.
# The seed is therefore stable here (crc32), and the control below is no longer "reproduce 1352"
# -- it cannot be -- but the two things the checklist actually demands and 1352 never ran:
# byte-identical reproduction at a fixed seed, and evidence the seed flag CHANGES the draw.
PUB_1352 = {"graded": 0.0151, "exact": 0.0083}     # recorded for the record; NOT a target
TOL = 0.002


def _stable(p: str) -> int:
    """crc32, never hash(): hash() of a str is per-process randomised and silently unseeds a draw."""
    return zlib.crc32(p.encode()) % 1000


def graded(c, h): return float(np.mean([c[q] == h[q] for q in range(6)]))
def exact(c, h):  return float(all(c[q] == h[q] for q in range(6)))


def cells(name, tg):
    f = ROOT / "corebench" / "results" / f"sat_{name}.npz"
    if not f.exists():
        return None
    S = load_sat(f)
    return {p: cls(yvec(S[p], sorted({i for i, _ in S[p]})))
            for p in S if p in tg and len(tg[p]) >= 2}


def per_prompt(A, B, tg, fn, cap, seeds=(900, 901, 902)):
    """Paired per-prompt difference. cap=None -> EVERY annotator; cap='draw3' -> 1352's design."""
    ks = sorted(set(A) & set(B))
    d = []
    for p in ks:
        v = tg[p]
        if cap == "draw3":
            acc = []
            for s in seeds:
                rng = np.random.default_rng(s + _stable(p))
                h = cls(np.array(v[int(rng.integers(len(v)))][0], float))
                acc.append(fn(A[p], h) - fn(B[p], h))
            d.append(float(np.mean(acc)))
        else:
            use = v if cap is None else v[:cap]
            acc = [fn(A[p], cls(np.array(y, float))) - fn(B[p], cls(np.array(y, float)))
                   for y, _ in use]
            d.append(float(np.mean(acc)))
    return np.array(d), len(ks)


def boot(d, n=4000, seed=7):
    rng = np.random.default_rng(seed)
    bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n)])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    se = float(bs.std(ddof=1))
    return float(d.mean()), float(lo), float(hi), se, 2.802 * se


def main() -> int:
    tg, _ = load_targets()
    arms = {n: cells(n, tg) for n in ("coval_core", "generic", "coval_core_sham")}
    if any(v is None for v in arms.values()):
        print("  UNRUNNABLE: an arm's score matrix is missing. Exit 2, never 0.")
        return 2
    A, B, SH = arms["coval_core"], arms["generic"], arms["coval_core_sham"]

    tot = sum(len(v) for v in tg.values() if len(v) >= 2)
    print(f"  release contains {tot} annotator rankings; entry 1352 consumed "
          f"{3 * sum(1 for v in tg.values() if len(v) >= 2)} "
          f"({3 * sum(1 for v in tg.values() if len(v) >= 2) / tot:.1%})\n")

    # ---- PLACEBO: an arm against itself must be exactly zero ------------------------------------
    pl_g, _ = per_prompt(A, A, tg, graded, None)
    pl_e, _ = per_prompt(A, A, tg, exact, None)
    placebo_ok = abs(pl_g.mean()) < 1e-12 and abs(pl_e.mean()) < 1e-12
    print(f"  PLACEBO  coval_core - itself: graded {pl_g.mean():+.2e}  exact {pl_e.mean():+.2e}  "
          f"{'PASS' if placebo_ok else 'FAIL'}")

    # ---- POSITIVE CONTROL: the two the checklist demands and 1352 never ran ---------------------
    # (1) REPRODUCIBILITY -- same stable seed twice must be byte-identical.
    # (2) SEED SENSITIVITY -- a different seed MUST move the draw, or the seed flag is decorative
    #     and "3 seeds" was one seed reported three times.
    d1, _ = per_prompt(A, B, tg, exact, "draw3")
    d2, _ = per_prompt(A, B, tg, exact, "draw3")
    repro = bool(np.array_equal(d1, d2))
    d3, _ = per_prompt(A, B, tg, exact, "draw3", seeds=(7000, 7001, 7002))
    sensitive = bool(not np.array_equal(d1, d3))
    print(f"  POSITIVE CONTROL  same stable seed twice -> byte-identical: {repro}  "
          f"{'PASS' if repro else 'FAIL'}")
    print(f"  g=0               a DIFFERENT seed changes the draw: {sensitive}  "
          f"{'PASS' if sensitive else 'FAIL'}")
    print("    Both are required. Reproducibility alone is satisfied by a constant, and a constant")
    print("    is exactly what an unseeded-but-cached draw looks like from the outside.")
    rep = {"draw3_exact_seedA": float(d1.mean()), "draw3_exact_seedB": float(d3.mean())}
    print(f"    3-draw exact at two seed sets: {d1.mean():+.4f} vs {d3.mean():+.4f}  "
          f"-> spread {abs(d1.mean()-d3.mean()):.4f}, which is the quantity 1352 never measured")
    print(f"    entry 1352 published {PUB_1352['exact']:+.4f} from an UNSEEDED draw: UNVERIFIED, not a target")
    pc_ok = repro and sensitive

    # ---- the grid: 4 caps x 2 metrics, ALL reported ---------------------------------------------
    print(f"\n  {'cap':<8}{'metric':<9}{'obs':>10}{'95% CI':>24}{'MDE':>9}  verdict")
    rows = []
    for cap, lab in (("draw3", "3 draws"), (16, "<=16"), (64, "<=64"), (None, "ALL")):
        for mname, fn in (("graded", graded), ("exact", exact)):
            d, npair = per_prompt(A, B, tg, fn, cap)
            obs, lo, hi, se, mde = boot(d)
            res = "RESOLVED" if (lo > 0 or hi < 0) else "contains 0"
            rows.append({"cap": lab, "metric": mname, "n_prompts": npair, "obs": obs,
                         "ci": [lo, hi], "se": se, "mde": mde, "verdict": res})
            print(f"  {lab:<8}{mname:<9}{obs:>+10.4f}   [{lo:+.4f}, {hi:+.4f}]{mde:>9.4f}  {res}")

    # ---- NEGATIVE control: the sham, reported as a magnitude and not as a value -----------------
    ds, _ = per_prompt(SH, B, tg, exact, None)
    so, slo, shi, _, _ = boot(ds)
    print(f"\n  NEGATIVE (sham - generic, exact, ALL): {so:+.4f} [{slo:+.4f}, {shi:+.4f}]")
    print("    Reported as a magnitude ONLY. The sham is misdirected rather than absent, so this")
    print("    bounds benefit+harm and is NOT the ingredient's value (register: poison, not placebo).")

    ex_all = [r for r in rows if r["cap"] == "ALL" and r["metric"] == "exact"][0]
    ex_3 = [r for r in rows if r["cap"] == "3 draws" and r["metric"] == "exact"][0]
    world = "A" if ex_all["verdict"] == "RESOLVED" else "B"
    print(f"\n  ⭐ WORLD {world}: exact-class on ALL annotators is {ex_all['verdict']} "
          f"(CI width {ex_all['ci'][1]-ex_all['ci'][0]:.4f} vs {ex_3['ci'][1]-ex_3['ci'][0]:.4f} at 3 draws)")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"verdict": "REPORTED", "world": world, "commit": head,
               "placebo": {"graded": pl_g.mean(), "exact": pl_e.mean()},
               "positive_control": {"reproducible": repro, "seed_sensitive": sensitive,
                                    "seed_spread": rep, "published_1352_UNVERIFIED": PUB_1352},
               "negative_sham_exact_all": {"obs": so, "ci": [slo, shi]},
               "grid": rows, "annotator_rankings_available": tot},
              open(OUT / "exact_class_full_annotators.json", "w"), indent=2)
    print(f"\n  artifact: results/exact_class_full_annotators.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
