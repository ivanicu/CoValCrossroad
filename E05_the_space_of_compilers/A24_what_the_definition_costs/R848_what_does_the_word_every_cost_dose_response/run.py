#!/usr/bin/env python3
"""
R848 · what does the word "every" COST? — the bar's dose-response in family size.

⛔ THE ARITHMETIC TRAP, RUN FIRST, AND IT KILLED THE OBVIOUS QUESTION. R847's NEXT proposed
"is membership monotone in search effort?". **Clause ④ requires `core > max(family)`, and a max is
non-decreasing in the family. So membership is monotonically NON-INCREASING BY CONSTRUCTION.**
That is a DERIVATION -- the same trap caught one round earlier in entry 1364 -- and asking it would
have produced a confident 1+1=2. **It is not asked here.**

The non-forced question is the DOSE-RESPONSE the standard names explicitly: **how FAST does the bar
grow with family size, against how fast a max over NOISE grows for free?** That prices the word
"every" instead of merely observing that it is a search.

ESTIMAND        the growth curve `max A2 over a random subfamily of size n`, for n across the
                available range, on (a) the real human target and (b) a shuffled-pair NOISE target;
                and the separation between the two slopes.
IDENTIFICATION  yes and exactly: every rule's per-prompt score is computed ONCE, so subsampling is
                arithmetic on a fixed vector rather than a re-run. ⚠ R847 did not persist these,
                which is why this round recomputes them and commits them -- an artifact a later
                round can ATTACK is part of the checklist and R847 shipped only its summary.
SCOPE           population: prompts with 4 response texts AND a human ranking (n reported)
                instrument: A2 vs EVERY annotator; family = R847's 394 (30 committed + 364 combos)
                baseline:   the identical curve on the noise target
                regime:     home release, no fitting on labels anywhere
WORLDS          A · the real curve grows FASTER than noise -> enlarging the family buys real
                    content, the bar is genuinely unbounded-by-search, and "every" is priceable
                B · the two curves grow at the same rate -> the enlargement measured SEARCH and
                    nothing else, and R847's +0.0241 excess was luck at one size
                C · both flatten -> the bar has a ceiling well under `coval_core` and clause ④ is
                    safe against this family class, which would be the first POSITIVE result
                    about the clause rather than another caveat
KILL            CONDITIONAL, pre-registered:
                  if positive control (human vs itself == 1.0) and negative (reversed near 0)
                  then compare slopes; a real slope <= noise slope => world B, extrapolation VOID
                  else UNVERIFIED
POSITIVE CTRL   the human's own ranking against itself must be exactly 1.0.
NEGATIVE CTRL   the reversed ranking must score low -- the scorer can return a low value.
NOISE ARM       identical family, shuffled pair-labels. Its curve is what family size buys free.
SEEDS           >=3 -- 24 independent subfamily draws at each size, and the draw seed is verified
                to change the subset (a "seeds" flag that changes nothing is the checklist's own
                warning, and entry 1358 found 29 files where it changed nothing).
MULTIPLICITY    the reported quantity is a MAXIMUM at each size; multiplicity is handled by the
                noise arm rather than a per-cell correction. Sizes tested reported in full.
ARTIFACT        results/dose_response.json -- per-rule real and noise scores PERSISTED, plus both
                curves, so a later round can re-cut them without recomputing anything.
IMPOSSIBLE      the true supremum (not a finite set) · causally identified · cross-release.
                N/A with what each would require, never "planned".
⚠ EXTRAPOLATION  any projected family size needed to reach `coval_core` is a MODEL, fitted on a
                bounded statistic that cannot grow without limit. It is labelled D4 and is NOT a
                measurement. Reporting it as one would be this project's most-repeated error.
"""
import itertools, json, pathlib, subprocess, sys, zlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
import score as SC                                              # noqa: E402

R435 = next(ROOT.glob("E0*/A*/R435_*"), None)
import importlib.util                                            # noqa: E402
_s = importlib.util.spec_from_file_location("r435", R435 / "run.py")
r435 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r435)

CORE = 0.5664774811929549
L = ["A", "B", "C", "D"]
SIZES = [5, 10, 20, 30, 50, 100, 200, 300, 394]
DRAWS = 24


def load_texts():
    texts = {}
    for line in open(ROOT / "data" / "comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        got = {}
        for x in (rec.get("responses") or []):
            got[x.get("response_index")] = " ".join(
                str(m.get("content") or "") for m in (x.get("messages") or [])
                if m.get("role") == "assistant")
        if len(got) >= 4 and all(got.get(c) for c in L):
            texts[rec["prompt_id"]] = {c: got[c] for c in L}
    return texts


def main() -> int:
    targets, _ = SC.load_targets()
    texts = load_texts()
    pids = sorted(set(texts) & set(targets))
    print(f"  prompts with 4 response texts AND a human ranking: {len(pids)}")
    if len(pids) < 200:
        print("  UNRUNNABLE: too few usable prompts. Exit 2, never 0.")
        return 2

    feats = {p: {c: r435.features(texts[p][c]) for c in L} for p in pids}
    base = sorted({k for p in pids for c in L for k in feats[p][c]} - {"__pos__"})
    H = {p: np.array([SC.cls(np.array(y, float)) for y, _ in targets[p]]) for p in pids}
    rng0 = np.random.default_rng(20260806)
    Hn = {p: H[p][:, rng0.permutation(6)] for p in pids}

    # ---- controls, before any curve ------------------------------------------------------------
    own = float(np.mean([np.mean(H[p] == H[p]) for p in pids]))
    rev = float(np.mean([np.mean(SC.cls(-np.array(targets[p][0][0], float)) == H[p])
                         for p in pids]))
    pos_ok, neg_ok = abs(own - 1.0) < 1e-12, rev < 0.30
    print(f"  POSITIVE  human vs itself {own:.4f}, must be 1.0   {'PASS' if pos_ok else 'FAIL'}")
    print(f"  NEGATIVE  reversed        {rev:.4f}, must be low   {'PASS' if neg_ok else 'FAIL'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        return 2

    # ---- the family, exactly R847's ------------------------------------------------------------
    fam = {}
    for name, key, sign in r435.RULES:
        fam[name] = {p: np.array([(feats[p][c][key] if key != "__pos__" else L.index(c))
                                  for c in L], float) * (1.0 if sign > 0 else -1.0) for p in pids}
    Z = {p: {k: ((lambda v: (v - v.mean()) / (v.std() + 1e-12))(
        np.array([feats[p][c][k] for c in L], float))) for k in base} for p in pids}
    for a, b in itertools.combinations(base, 2):
        for sa, sb in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            fam[f"{'+' if sa>0 else '-'}{a}{'+' if sb>0 else '-'}{b}"] = {
                p: sa * Z[p][a] + sb * Z[p][b] for p in pids}
    names = sorted(fam)
    print(f"  family: {len(names)} rules (R847's 30 committed + {len(names)-30} combinations)")

    # ---- score every rule ONCE; subsampling is then exact arithmetic ---------------------------
    real = np.array([np.mean([np.mean(SC.cls(fam[n][p]) == H[p]) for p in pids]) for n in names])
    noise = np.array([np.mean([np.mean(SC.cls(fam[n][p]) == Hn[p]) for p in pids]) for n in names])
    print(f"  scored {len(names)} rules on both targets · real max {real.max():.4f} "
          f"· noise max {noise.max():.4f}")

    # ---- SEED CHECK: the draw seed must actually change the subset ------------------------------
    s1 = np.random.default_rng(1).choice(len(names), 30, replace=False)
    s2 = np.random.default_rng(2).choice(len(names), 30, replace=False)
    seed_ok = not np.array_equal(np.sort(s1), np.sort(s2))
    print(f"  SEED CHECK  a different draw seed changes the subfamily: {seed_ok}  "
          f"{'PASS' if seed_ok else 'FAIL — the seeds flag is decorative'}")
    if not seed_ok:
        return 2

    # ---- the curves -----------------------------------------------------------------------------
    print(f"\n  {'n':>5}{'real max (mean of draws)':>27}{'noise max':>13}{'excess':>10}")
    rows = []
    for n in SIZES:
        rm, nm = [], []
        for d in range(DRAWS if n < len(names) else 1):
            idx = np.random.default_rng(5000 + 97 * n + d).choice(len(names), n, replace=False) \
                if n < len(names) else np.arange(len(names))
            rm.append(float(real[idx].max())); nm.append(float(noise[idx].max()))
        r_, n_ = float(np.mean(rm)), float(np.mean(nm))
        rows.append({"n": n, "real": r_, "noise": n_, "excess": r_ - n_,
                     "real_sd": float(np.std(rm)), "draws": len(rm)})
        print(f"  {n:>5}{r_:>27.4f}{n_:>13.4f}{r_-n_:>+10.4f}")

    ln = np.log([r["n"] for r in rows])
    br = float(np.polyfit(ln, [r["real"] for r in rows], 1)[0])
    bn = float(np.polyfit(ln, [r["noise"] for r in rows], 1)[0])
    print(f"\n  slope per ln(n):  real {br:+.5f}   noise {bn:+.5f}   "
          f"separation {br-bn:+.5f}")
    world = "A" if br > bn * 1.5 else ("B" if br <= bn else "C")
    print(f"  ⭐ WORLD {world}: "
          + {"A": "the real curve outgrows noise — enlarging buys content",
             "B": "the curves grow alike — the enlargement measured SEARCH, and R847's excess"
                  " was luck at one size",
             "C": "real outgrows noise but weakly"}[world])

    a_ = float(np.polyfit(ln, [r["real"] for r in rows], 1)[1])
    need = float(np.exp((CORE - a_) / br)) if br > 0 else float("inf")
    print(f"\n  ⚠ EXTRAPOLATION, D4 AND NOT A MEASUREMENT: fitting max ≈ {a_:.4f} + {br:.5f}·ln(n),")
    print(f"    reaching coval_core {CORE:.4f} would need n ≈ {need:.3g} rules.")
    print("    A2 is BOUNDED ABOVE by 1 and by the human ceiling, so a log fit MUST eventually")
    print("    break; the number above is what the fitted model says, not what the world says.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "n_prompts": len(pids), "world": world,
               "curve": rows, "slope_real_per_lnn": br, "slope_noise_per_lnn": bn,
               "extrapolated_n_for_core_D4_NOT_A_MEASUREMENT": need,
               "controls": {"human_vs_itself": own, "reversed": rev, "seed_changes_subset": seed_ok},
               "per_rule": {"names": names, "real": real.tolist(), "noise": noise.tolist()}},
              open(OUT / "dose_response.json", "w"), indent=2)
    print(f"\n  artifact: results/dose_response.json @ {head[:8]} — per-rule scores PERSISTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
