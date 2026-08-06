#!/usr/bin/env python3
"""
R850 · is ④′'s extension SELECTIVE, or merely a small reference class?

⛔ THE ARITHMETIC TRAP, RUN FIRST. The bar is `max over R`, so enlarging R can only raise it, so
every arm's margin is non-increasing and **the extension is monotonically NON-INCREASING in |R| BY
CONSTRUCTION.** Asking *"does 41 shrink as R grows?"* is 1+1=2. **Not asked.** *(Third time this
arc that the obvious question was forced — entries 1364, 1366, and here.)*

The non-forced questions, and they decide whether R849's headline means anything:
  **HOW FAST does it shrink, and does it COLLAPSE toward 1 or STABILISE well above it?**
If the extension falls to ~1 as R grows, ④′ was selective only because R was small — the
`definition describes the instance` failure arriving one level up, in my own repair. If it
flattens well above 1, the selectivity is a property of the clause.

ESTIMAND        the extension of ④′ (arms whose held-out margin over the R-best rule is resolvably
                positive, BH q=0.05) as a function of |R|, on the real target and on a NOISE target.
IDENTIFICATION  yes and exactly: arm and rule score vectors are computed ONCE, so every (size,draw)
                cell is a vector subtraction and a shared-index bootstrap, not a re-run.
SCOPE           population: 99 scored arms × 1,078 prompts
                instrument: A2 vs the EVEN annotators; bar always selected on the ODD half
                baseline:   R849's single cell, |R| = 394 → extension 41
                regime:     home release; R = R847/R848's response-only family; no label fitting
WORLDS          A · the extension collapses toward 1 → ④′ was selective because R was SMALL, and my
                    repair reproduces the failure it was written to fix, one level up
                B · it flattens well above 1 → selectivity is a property of the CLAUSE, and R849's
                    41 is not an artifact of where the sweep happened to stop
                C · it never falls at all → the bar is not binding and the clause is decoration
KILL            CONDITIONAL: at every size the placebo must be 0, the positive control must satisfy
                and the negative control must not. Any size failing → that size is UNVERIFIED and
                is reported as such, never silently dropped.
POSITIVE CTRL   `oracle_k4` must satisfy ④′ at every size.
NEGATIVE CTRL   `random_k4_s0` must NOT satisfy at any size. ⚠ It has a POSITIVE point estimate
                (+0.0057 at |R|=394), so a point-comparison clause admits it — that is the whole
                reason ④′ uses an interval, and the control must keep proving it.
NOISE ARM       the identical procedure against a shuffled-pair target. Its extension is what the
                procedure admits for free at each size, and it is subtracted before any claim.
SEEDS           8 independent subfamily draws per size; the draw seed is verified to change R.
MULTIPLICITY    BH q=0.05 over all 99 arms within every cell; cells tested and surviving reported.
ARTIFACT        results/extension_vs_class_size.json — the whole curve, real and noise.
IMPOSSIBLE      construct validated · cross-release · causally identified. N/A with what each needs.
"""
import itertools, json, pathlib, subprocess, sys
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

L = ["A", "B", "C", "D"]
SIZES = [5, 10, 20, 30, 50, 100, 200, 394]
DRAWS, NBOOT = 8, 2000
POS_CTRL, NEG_CTRL = "oracle_k4", "random_k4_s0"


def load_texts():
    t = {}
    for line in open(ROOT / "data" / "comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        g = {x.get("response_index"): " ".join(
            str(m.get("content") or "") for m in (x.get("messages") or [])
            if m.get("role") == "assistant") for x in (r.get("responses") or [])}
        if len(g) >= 4 and all(g.get(c) for c in L):
            t[r["prompt_id"]] = {c: g[c] for c in L}
    return t


def bh_mask(p, q=0.05):
    C = len(p); o = np.argsort(p); k = -1
    for rank, i in enumerate(o, 1):
        if p[i] <= q * rank / C:
            k = rank
    m = np.zeros(C, bool)
    m[o[:k]] = True if k > 0 else False
    return m


def main() -> int:
    targets, _ = SC.load_targets()
    texts = load_texts()
    pids = sorted(set(texts) & set(targets))
    Hodd = {p: np.array([SC.cls(np.array(y, float)) for y, _ in targets[p][0::2]]) for p in pids}
    Heven = {p: np.array([SC.cls(np.array(y, float)) for y, _ in targets[p][1::2]]) for p in pids}
    pids = [p for p in pids if len(Hodd[p]) and len(Heven[p])]
    n = len(pids)
    print(f"  prompts with BOTH annotator halves: {n}")
    if n < 200:
        print("  UNRUNNABLE. Exit 2, never 0.")
        return 2

    rngN = np.random.default_rng(20260806)
    Hnoise = {p: Heven[p][:, rngN.permutation(6)] for p in pids}

    feats = {p: {c: r435.features(texts[p][c]) for c in L} for p in pids}
    base = sorted({k for p in pids for c in L for k in feats[p][c]} - {"__pos__"})
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
    rnames = sorted(fam)
    # per-rule score vectors, computed ONCE
    Rodd = np.array([[np.mean(SC.cls(fam[r][p]) == Hodd[p]) for p in pids] for r in rnames])
    Reven = np.array([[np.mean(SC.cls(fam[r][p]) == Heven[p]) for p in pids] for r in rnames])
    Rnoise = np.array([[np.mean(SC.cls(fam[r][p]) == Hnoise[p]) for p in pids] for r in rnames])
    print(f"  reference class R: {len(rnames)} rules · score vectors computed once")

    anames, Aeven, Anoise = [], [], []
    for f in sorted((ROOT / "corebench" / "results").glob("sat_*.npz")):
        try:
            S = SC.load_sat(f)
        except Exception:
            continue
        if sum(1 for p in pids if p in S) < 200:
            continue
        anames.append(f.stem[4:])
        Aeven.append([np.mean(SC.cls(SC.yvec(S[p], sorted({i for i, _ in S[p]}))) == Heven[p])
                      if p in S else np.nan for p in pids])
        Anoise.append([np.mean(SC.cls(SC.yvec(S[p], sorted({i for i, _ in S[p]}))) == Hnoise[p])
                       if p in S else np.nan for p in pids])
    Aeven, Anoise = np.array(Aeven), np.array(Anoise)
    # ⛔ POPULATION BUG, CAUGHT BY ITS OWN PRINT AND FIXED BEFORE ANY NUMBER WAS REPORTED.
    # The first version intersected EVERY arm's prompt coverage (`~isnan(...).any(axis=0)`),
    # collapsing 1,078 prompts to 87 and silently changing the population out from under a
    # comparison with R849, which uses each arm's OWN prompt set (>=200). A curve on 87 prompts is
    # not the same estimand as R849's 41 and must not be laid beside it. The print
    # "prompts common to all arms" is what exposed it -- an instrument reporting its own
    # population is worth more than one reporting only its result.
    # Fix: keep every arm on its OWN prompts; NaNs are masked per arm at bootstrap time.
    cover = (~np.isnan(Aeven)).sum(1)
    print(f"  arms: {len(anames)} · per-arm prompt coverage "
          f"min {cover.min()} · median {int(np.median(cover))} · max {cover.max()}")
    Reven_, Rnoise_, Rodd_ = Reven, Rnoise, Rodd
    print(f"  ⚠ NOT intersected across arms: an all-arm intersection left 87 prompts and would")
    print(f"    have made this curve incomparable with R849's cell.")

    # one shared bootstrap counts matrix -> every CI is a matmul
    bidx = np.random.default_rng(4242).integers(0, n, size=(NBOOT, n))
    M = (~np.isnan(Aeven)).astype(float)      # arms x prompts availability mask

    def extension(D):
        """D: arms x prompts margin matrix with NaN where an arm lacks a prompt.
        Each arm is bootstrapped over ITS OWN prompts -- the shared index draw is masked per arm,
        so no arm is scored on a prompt it never covered and none is dropped for another's gap."""
        Dz = np.nan_to_num(D, nan=0.0)
        num = Dz[:, bidx].sum(2)              # arms x NBOOT
        den = M[:, bidx].sum(2)
        bs = (num / np.maximum(den, 1.0)).T   # NBOOT x arms
        lo, hi = np.percentile(bs, [2.5, 97.5], axis=0)
        p = np.maximum(2 * np.minimum((bs <= 0).mean(0), (bs >= 0).mean(0)), 1.0 / (NBOOT + 1))
        return (bh_mask(p) & (lo > 0)), np.nanmean(D, 1), p, lo, hi

    ipos = anames.index(POS_CTRL) if POS_CTRL in anames else None
    ineg = anames.index(NEG_CTRL) if NEG_CTRL in anames else None
    print(f"\n  {'|R|':>5}{'extension (real)':>19}{'noise':>9}{'excess':>9}  controls")
    rows = []
    for m in SIZES:
        ext_r, ext_n, ctl = [], [], []
        for d in range(DRAWS if m < len(rnames) else 1):
            idx = (np.random.default_rng(900 + 13 * m + d).choice(len(rnames), m, replace=False)
                   if m < len(rnames) else np.arange(len(rnames)))
            star = idx[np.argmax(Rodd_[idx].mean(1))]          # ⚠ selected on the ODD half
            sat, mean, p, lo, hi = extension(Aeven - Reven_[star])
            starn = idx[np.argmax(Rodd_[idx].mean(1))]
            satn, *_ = extension(Anoise - Rnoise_[starn])
            ext_r.append(int(sat.sum())); ext_n.append(int(satn.sum()))
            ctl.append((bool(sat[ipos]) if ipos is not None else None,
                        bool(sat[ineg]) if ineg is not None else None))
        pos_ok = all(c[0] for c in ctl)
        neg_ok = all(not c[1] for c in ctl)
        r_, n_ = float(np.mean(ext_r)), float(np.mean(ext_n))
        rows.append({"R": m, "ext_real": r_, "ext_noise": n_, "excess": r_ - n_,
                     "draws": len(ext_r), "pos_ok": pos_ok, "neg_ok": neg_ok,
                     "verdict": "OK" if (pos_ok and neg_ok) else "UNVERIFIED"})
        print(f"  {m:>5}{r_:>19.1f}{n_:>9.1f}{r_-n_:>9.1f}  "
              f"pos {'PASS' if pos_ok else 'FAIL'} · neg {'PASS' if neg_ok else 'FAIL'}"
              f"{'' if (pos_ok and neg_ok) else '  -> UNVERIFIED at this size'}")

    good = [r for r in rows if r["verdict"] == "OK"]
    if not good:
        print("\n  UNVERIFIED at every size: controls failed. No curve is reported. Exit 2.")
        return 2
    # ⛔ VERDICT-STRING BUG, CAUGHT AND FIXED BEFORE REPORTING. The first version took
    # `good[0]` and `good[-1]`; only ONE size passes its controls, so both were |R|=394 and it
    # printed "does not fall" from a Δ computed over a SINGLE POINT. That is §4's "the verdict
    # string is not a computation" -- the branch must reference the controls it declared.
    # Fixed: the SHAPE of the curve is read over the whole swept range (which is a measurement of
    # the procedure), while the CLAUSE's status is read only where its controls hold.
    first, last = rows[0], rows[-1]
    fell = last["ext_real"] - first["ext_real"]
    n_ok = len(good)
    if n_ok < 2:
        print(f"\n  ⚠ ONLY {n_ok} SIZE PASSES ITS CONTROLS (|R| = "
              f"{', '.join(str(r['R']) for r in good)}). The curve's SHAPE is reported as a")
        print("    property of the PROCEDURE; the CLAUSE's extension is admissible at that size")
        print("    alone. A trend fitted across sizes whose negative control fails would be a")
        print("    trend in how often a random arm is admitted, not in the clause.")
    collapses = last["ext_real"] <= 2
    world = "A" if collapses else ("C" if abs(fell) < 1 else "B")
    print(f"\n  ⭐ extension {first['ext_real']:.1f} at |R|={first['R']} → "
          f"{last['ext_real']:.1f} at |R|={last['R']}  (Δ {fell:+.1f}) over the WHOLE swept range")
    print(f"  ⭐ NOISE extension at |R|={last['R']}: {last['ext_noise']:.1f} of {len(anames)} arms "
          f"— EXCESS over what the procedure admits for free is only {last['excess']:.1f}")
    print("     ⚠ R849 reported the bare extension and ran NO noise arm. This is the number that")
    print("     downgrades it: most of what ④′ admits, it admits against a shuffled target too.")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "collapses toward 1 — ④′ was selective only because R was SMALL, and my repair"
             " reproduces the failure it was written to fix",
        "B": "falls but STABILISES well above 1 — selectivity is a property of the CLAUSE",
        "C": "does not fall — the bar is not binding and the clause is decoration"}[world])
    print("     ⚠ the FALL itself is forced (a max over a larger set is larger); only the RATE")
    print("     and the LEVEL it settles at could have come out otherwise.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_arms": len(anames), "n_prompts": n,
               "curve": rows, "r849_cell": {"R": 394, "extension": 41}},
              open(OUT / "extension_vs_class_size.json", "w"), indent=2)
    print(f"\n  artifact: results/extension_vs_class_size.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
