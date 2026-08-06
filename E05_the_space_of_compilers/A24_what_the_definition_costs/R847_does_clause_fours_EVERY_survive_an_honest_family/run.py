#!/usr/bin/env python3
"""
R847 · does clause ④'s "EVERY" survive an honest enlargement of the family?

⛔ WHY. R406 already found this defect in clause ②: *"better than EVERY prompt-blind set"* had been
tested against a **p99** bar, while the **max** over the 1,820 blind subsets is 0.5574753088 against
a reference of 0.5546019830 — so between 18 and 182 subsets beat the bar the word "EVERY" was
tested against. **Clause ④ has the same shape and nobody has said so:** its *"every rule computable
from responses alone"* is realised in R436 as a max over **30 hand-picked single-feature
argmin/argmax rules**. A max over a convenience family is not a universal quantifier.

⚠ AND THE ATTACK MUST CARRY THE OTHER WRITER'S CONTROL. Their R843 (`d4205a7e`, derived with no
input from me) found that a **max over 1,820 subsets scores HIGHER on a pure-noise target than on
the real one** — a maximum over a large family is large by construction. An enlarged-family search
is exactly that shape, so the noise-target arm is not optional here: **it is the kill condition.**

ESTIMAND        sup over a response-only rule family of mean A2, under
                  F0 = R436's committed 30 single-feature rules
                  F1 = F0 + every NORMALISED TWO-FEATURE combination (no label fitting, so still
                       "computable from responses alone" on any reading)
                and whether that sup reaches `coval_core` at 0.5664774811929549.
IDENTIFICATION  yes: features come from the response texts in comparisons.jsonl via
                `r435.features`, reused rather than reimplemented, so the family is an EXTENSION
                of R436's and not a parallel construction that could differ for other reasons.
SCOPE           population: prompts with 4 response texts AND a human ranking (n reported)
                instrument: A2 vs EVERY annotator (R841: a 3-draw design used 17.6% of the data)
                baseline:   R436's committed bar 0.4511956297670583 (`min_ttr`)
                regime:     the home release; no fitting on labels anywhere
WORLDS          A · "EVERY" is honest — enlarging the family by an order of magnitude leaves the
                    bar far below `coval_core`, and clause ④ has genuine content
                B · "EVERY" is a convenience max — a mechanical enlargement moves the bar
                    materially, and clause ④'s verdict is an artifact of family size
                They differ ontologically: A says the clause states a property; B says it states
                the size of the search someone happened to run.
KILL            ⚠ CONDITIONAL, and it compares EXCESS OVER THE SEARCH'S OWN INFLATION, never raw
                maxima, because a larger family has a larger max on noise too:
                  if positive control (human vs itself == 1.0) and negative (reversed ranking near 0)
                  then  raised := (maxF1 - maxF1_noise) > (maxF0 - maxF0_noise)
                        crossed := maxF1 > 0.5664774811929549 AND maxF1 > maxF1_noise
                  else  UNVERIFIED
POSITIVE CTRL   the human's own ranking scored against itself must be exactly 1.0 (R436's control).
NEGATIVE CTRL   the REVERSED human ranking must score near 0 — the scorer can return a low value.
NOISE ARM       the identical search against a SHUFFLED human target. Its max is what family size
                buys for free, and it is subtracted before any claim.
MULTIPLICITY    the whole enlarged family is a search; the reported quantity is a MAXIMUM, so the
                multiplicity is handled by the noise arm rather than by a per-cell correction.
                Cells searched is reported beside the winner.
ARTIFACT        results/every_family.json with the commit hash.
IMPOSSIBLE      causally identified · cross-release · construct validated.
                N/A with what each would require, never "planned".
"""
import itertools, json, pathlib, subprocess, sys, zlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
import score as SC                                              # noqa: E402

R435 = next(ROOT.glob("E0*/A*/R435_*"), None)
if R435 is None:
    print("  UNRUNNABLE: R435 not found; its features/RULES are the family being extended.")
    raise SystemExit(2)
sys.path.insert(0, str(R435))
import importlib.util                                            # noqa: E402
_s = importlib.util.spec_from_file_location("r435", R435 / "run.py")
r435 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r435)

CORE = 0.5664774811929549          # coval_core, the object clause ④ must beat every rule to admit
R436_BAR = 0.4511956297670583      # R436's committed bar, `min_ttr`
L = ["A", "B", "C", "D"]


def stable(p): return zlib.crc32(p.encode()) % 100003


def load_texts():
    texts = {}
    for line in open(ROOT / "data" / "comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        got = {}
        for x in (rec.get("responses") or []):
            c = x.get("response_index")
            got[c] = " ".join(str(m.get("content") or "")
                              for m in (x.get("messages") or []) if m.get("role") == "assistant")
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
    keys = sorted({k for p in pids for c in L for k in feats[p][c]})
    print(f"  response-only features available: {len(keys)}")

    # human cls per prompt, EVERY annotator (R841: a 3-draw design used 17.6% of the release)
    H = {p: np.array([SC.cls(np.array(y, float)) for y, _ in targets[p]]) for p in pids}
    rng0 = np.random.default_rng(20260806)
    Hn = {p: H[p][:, rng0.permutation(6)] for p in pids}          # NOISE arm: pair labels shuffled

    def score(vecs, Ht):
        """mean over prompts of mean over annotators of 6-pair agreement."""
        return float(np.mean([np.mean(SC.cls(vecs[p]) == Ht[p]) for p in pids]))

    # ---- F0: R436's committed 30 -----------------------------------------------------------
    F0 = {}
    for name, key, sign in r435.RULES:
        F0[name] = {p: np.array([(feats[p][c][key] if key != "__pos__" else L.index(c))
                                 for c in L], float) * (1.0 if sign > 0 else -1.0)
                    for p in pids}
    # ---- F1: + every normalised TWO-FEATURE combination, no label fitting -------------------
    base = [k for k in keys if k != "__pos__"]
    Z = {p: {k: ((lambda v: (v - v.mean()) / (v.std() + 1e-12))(
        np.array([feats[p][c][k] for c in L], float))) for k in base} for p in pids}
    F1 = dict(F0)
    for a, b in itertools.combinations(base, 2):
        for sa, sb in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            F1[f"{'+' if sa>0 else '-'}{a}{'+' if sb>0 else '-'}{b}"] = {
                p: sa * Z[p][a] + sb * Z[p][b] for p in pids}
    print(f"  family sizes: F0 = {len(F0)} (R436's committed) · F1 = {len(F1)} "
          f"(+ {len(F1)-len(F0)} two-feature combinations, NO fitting on labels)")

    # ---- controls ---------------------------------------------------------------------------
    own = float(np.mean([np.mean(H[p] == H[p]) for p in pids]))
    rev = float(np.mean([np.mean(SC.cls(-np.array(targets[p][0][0], float)) == H[p])
                         for p in pids]))
    pos_ok, neg_ok = abs(own - 1.0) < 1e-12, rev < 0.30
    print(f"\n  POSITIVE  human ranking vs itself -> {own:.4f}, must be 1.0   "
          f"{'PASS' if pos_ok else 'FAIL'}")
    print(f"  NEGATIVE  REVERSED ranking       -> {rev:.4f}, must be low   "
          f"{'PASS' if neg_ok else 'FAIL'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        return 2

    res = {}
    for lab, fam in (("F0", F0), ("F1", F1)):
        real = {n: score(v, H) for n, v in fam.items()}
        noise = {n: score(v, Hn) for n, v in fam.items()}
        bn, bv = max(real, key=real.get), max(real.values())
        nn, nv = max(noise, key=noise.get), max(noise.values())
        res[lab] = {"n_rules": len(fam), "best": bn, "max": bv,
                    "noise_best": nn, "noise_max": nv, "excess": bv - nv}
        print(f"\n  {lab}  {len(fam):>4} rules · best `{bn}` A2 {bv:.4f}")
        print(f"       NOISE arm (R843's control): best `{nn}` A2 {nv:.4f} "
              f"→ EXCESS over what family size buys = {bv - nv:+.4f}")

    raised = res["F1"]["excess"] > res["F0"]["excess"]
    crossed = res["F1"]["max"] > CORE and res["F1"]["max"] > res["F1"]["noise_max"]
    print(f"\n  R436's committed bar {R436_BAR:.10f} · coval_core {CORE:.10f}")
    print(f"  ⭐ enlarging the family {len(F0)} → {len(F1)} moved the max "
          f"{res['F0']['max']:.4f} → {res['F1']['max']:.4f} "
          f"({res['F1']['max'] - res['F0']['max']:+.4f})")
    print(f"     but the NOISE max moved {res['F0']['noise_max']:.4f} → "
          f"{res['F1']['noise_max']:.4f}, so the excess moved "
          f"{res['F0']['excess']:+.4f} → {res['F1']['excess']:+.4f}")
    print(f"  ⭐ WORLD {'B — EVERY is a convenience max' if raised else 'A — EVERY survives'}"
          f"   ·   clause ④ crossed by a response-only rule: {crossed}")
    print("     ⚠ `raised` compares EXCESS OVER NOISE, never raw maxima: a bigger family has a")
    print("     bigger max on noise too, and reporting the raw jump would be R843's exact error.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "n_prompts": len(pids), "families": res,
               "raised": bool(raised), "crossed": bool(crossed),
               "coval_core": CORE, "r436_committed_bar": R436_BAR,
               "controls": {"human_vs_itself": own, "reversed": rev}},
              open(OUT / "every_family.json", "w"), indent=2)
    print(f"\n  artifact: results/every_family.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
