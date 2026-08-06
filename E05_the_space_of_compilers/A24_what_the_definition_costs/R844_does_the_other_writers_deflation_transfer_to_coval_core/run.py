#!/usr/bin/env python3
"""
R844 · does the OTHER WRITER's deflation transfer to `coval_core`?

⛔ WHY, AND WHY IT IS NOT MY QUESTION. This repository has two concurrent writers (entry 1360,
D8: a reflog commit this session did not make, two shell-snapshot ids, and the other writer's own
commit body saying so). §2 of the standard lists `independently replicated` as STRUCTURALLY
IMPOSSIBLE here because it "needs a second team". **There is one, working the same object, with
its own context, right now.** So this round does the thing §2.5 says is the only evidence that
survives a framing error: take a claim the OTHER designer derived independently, and run it
against mine.

Their R843 (`d4205a7e`), reached with no input from me:
    "A1's relevance vector sent to the WRONG prompt scores 0.552705 against A1's own 0.551732
     and A0's 0.540676 -- the permuted selector is as good as the real one. So A1's gain over A0
     is NOT prompt-specific fit ... what it buys is a better fixed subset."
    "REMEDY: the contextualisation estimand is A1 minus ITS OWN PLACEBO, never A1 minus A0."

**If that transfers, R841's `coval_core - generic` is the wrong estimand and my result is about a
better fixed subset rather than about reading the conversation.** That is a direct threat to the
definition's clause (2), and it was not available to me from inside my own framing.

ESTIMAND        (a) PROMPT-SPECIFICITY  `coval_core - coval_core_sham`
                    -- the other writer's estimand: the arm minus ITS OWN wrong-prompt placebo
                (b) MISDIRECTION COST   `coval_core_sham - genericpool16`
                    -- does pointing the instrument at the wrong prompt land AT the
                       never-reads-a-prompt floor (placebo) or BELOW it (poison)?
                on GRADED A2 and EXACT, over EVERY annotator (R841 established 3 draws is 17.6%).
IDENTIFICATION  yes; all arms are released score matrices and every ranking is on disk.
SCOPE           population: prompts scored by all compared arms, paired
                instrument: judge J via sat_*.npz; A2 as corebench/rule_sweep.py
                baseline:   R843's A1 result, which is the world being tested for transfer
                regime:     all annotators per prompt, median 16
WORLDS          A · the deflation TRANSFERS -> core - sham is at or inside its own floor, and
                    R841's advantage is a better fixed subset, not conversation-reading
                B · it does NOT transfer -> core - sham is resolvably positive AND sham sits
                    BELOW the never-reads-a-prompt arm, which is the poison signature and means
                    misdirection actively hurts, i.e. WHICH prompt is read matters
KILL            CONDITIONAL: if the placebo (an arm against itself) is exactly 0 and the two
                compared populations are the same prompts, read the intervals; else UNVERIFIED.
POSITIVE CTRL   `coval_core - coval_core` must be exactly 0.0 in both metrics; a non-zero
                self-difference means the pairing is broken and nothing else here is readable.
NEGATIVE CTRL   `genericpool16 - generic`: two arms that BOTH never read the prompt. Their
                difference is not required to be zero -- they are different fixed sets -- but it
                bounds how much of any gap is "a better fixed subset", which is exactly the
                mechanism the other writer identified. Reported, never subtracted.
MULTIPLICITY    2 estimands x 2 metrics = 4 cells, reported whole.
ARTIFACT        results/deflation_transfer.json with the commit hash.
IMPOSSIBLE      causally identified (no intervention on the compiler) · cross-release ·
                construct validated. N/A with what each would require, never "planned".
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402


def graded(c, h): return float(np.mean([c[q] == h[q] for q in range(6)]))
def exact(c, h):  return float(all(c[q] == h[q] for q in range(6)))


def cells(name, tg):
    f = ROOT / "corebench" / "results" / f"sat_{name}.npz"
    if not f.exists():
        return None
    S = load_sat(f)
    return {p: cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in S
            if p in tg and len(tg[p]) >= 2}


def paired(A, B, tg, fn):
    """EVERY annotator per prompt -- no draw, so no seed and nothing to be unstable about."""
    ks = sorted(set(A) & set(B))
    d = [float(np.mean([fn(A[p], cls(np.array(y, float))) - fn(B[p], cls(np.array(y, float)))
                        for y, _ in tg[p]])) for p in ks]
    return np.array(d), len(ks)


def boot(d, n=4000, seed=11):
    rng = np.random.default_rng(seed)
    bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n)])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return float(d.mean()), float(lo), float(hi), 2.802 * float(bs.std(ddof=1))


def main() -> int:
    tg, _ = load_targets()
    need = ("coval_core", "coval_core_sham", "generic", "genericpool16")
    arm = {n: cells(n, tg) for n in need}
    missing = [n for n, v in arm.items() if v is None]
    if missing:
        print(f"  UNRUNNABLE: missing arm(s) {missing}. Exit 2, never 0.")
        return 2

    # ---- PLACEBO / kill precondition ------------------------------------------------------------
    pg, npair = paired(arm["coval_core"], arm["coval_core"], tg, graded)
    pe, _ = paired(arm["coval_core"], arm["coval_core"], tg, exact)
    ok = abs(pg.mean()) < 1e-12 and abs(pe.mean()) < 1e-12
    print(f"  PLACEBO  coval_core - itself: graded {pg.mean():+.2e}  exact {pe.mean():+.2e}  "
          f"{'PASS' if ok else 'FAIL'}   (n={npair} paired prompts)")
    if not ok:
        print("\n  UNVERIFIED: a self-difference is non-zero, so the pairing is broken and no")
        print("  interval below is readable. Exit 2, never 0.")
        return 2

    rows = []
    print(f"\n  {'estimand':<38}{'metric':<8}{'obs':>10}{'95% CI':>24}{'MDE':>9}  verdict")
    for lab, a, b in (("(a) core - its OWN wrong-prompt sham", "coval_core", "coval_core_sham"),
                      ("(b) sham - never-reads-a-prompt pool", "coval_core_sham", "genericpool16"),
                      ("NEG two never-read arms differ?", "genericpool16", "generic")):
        for mname, fn in (("graded", graded), ("exact", exact)):
            d, n = paired(arm[a], arm[b], tg, fn)
            o, lo, hi, mde = boot(d)
            v = "RESOLVED" if (lo > 0 or hi < 0) else "contains 0"
            rows.append({"estimand": lab, "metric": mname, "n": n, "obs": o,
                         "ci": [lo, hi], "mde": mde, "verdict": v})
            print(f"  {lab:<38}{mname:<8}{o:>+10.4f}   [{lo:+.4f}, {hi:+.4f}]{mde:>9.4f}  {v}")

    a_ex = [r for r in rows if r["estimand"].startswith("(a)") and r["metric"] == "exact"][0]
    b_ex = [r for r in rows if r["estimand"].startswith("(b)") and r["metric"] == "exact"][0]
    transfers = not (a_ex["verdict"] == "RESOLVED" and a_ex["obs"] > 0)
    print(f"\n  ⭐ WORLD {'A — the deflation TRANSFERS' if transfers else 'B — it does NOT transfer'}")
    print(f"     (a) is {a_ex['verdict']} at {a_ex['obs']:+.4f}; (b) is {b_ex['obs']:+.4f} "
          f"{'BELOW' if b_ex['obs'] < 0 else 'at/above'} the never-reads-a-prompt arm")
    print("     ⚠ (b) below zero is the POISON signature: misdirection actively HURTS, which is")
    print("     a stronger statement than 'reading helps' and is what separates this from R843's A1,")
    print("     where the wrong-prompt arm scored AS WELL AS the right one.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "transfers": bool(transfers), "rows": rows,
               "other_writer_round": "R843 @ d4205a7e",
               "their_A1_numbers": {"A1": 0.551732, "A1_wrong_prompt": 0.552705, "A0": 0.540676}},
              open(OUT / "deflation_transfer.json", "w"), indent=2)
    print(f"\n  artifact: results/deflation_transfer.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
