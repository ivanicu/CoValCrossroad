#!/usr/bin/env python3
"""R1015 — is clause ②'s A2 the ONLY pairing-dependent content, or is there another candidate?

⛔ WHY. R1014 closed the text-only class: the released core's sham is an exact DERANGEMENT of its own
criterion sets, so every property of the criteria text alone is identical between core and sham and
none can be definitional content. What survives must read the criteria AND their own prompt together.
Clause ② does that — but R1011 showed clause ②'s metric cannot rank the instance above `topw_k4`.
⭐ So the question is whether ANOTHER pairing-dependent quantity exists, and whether it separates
where A2 does not.

⭐ THE CANDIDATE: **criterion DISCRIMINATIVENESS** — the spread of a criterion's satisfaction across
THIS prompt's own responses. A criterion every response satisfies equally tells you nothing about this
prompt, however well written it is. It needs the criteria AND the prompt's responses, so it is
pairing-dependent; and it reads NO human labels, so it satisfies clause ③ automatically and is
independent of the comparator.

ESTIMAND        per arm, the mean across prompts of the variance of each criterion's satisfaction
                across that prompt's responses; and whether it resolvably separates `coval_core`
                from the `topw` arms in the ②′ extension, where A2 does not.
IDENTIFICATION  direct: the satisfaction matrices are on disk per arm per prompt. No human labels, no
                comparator, no model beyond the judge that produced the release's scores.
SCOPE           population : the ②′ extension's full-coverage arms (R1011) plus the sham
                instrument : variance of satisfaction across the 4 responses, averaged over criteria
                             then over prompts; cluster bootstrap over prompts
                baseline   : `coval_core_sham` — the SAME criteria on the WRONG prompt
                regime     : this release, n = 968
WORLDS          A ANOTHER QUANTITY SEPARATES  discriminativeness resolvably orders `coval_core` above
                             the `topw` arms. Then clause ② is one option among several and a second
                             pairing-dependent clause is available.
                B ONLY CLAUSE ②              it does not separate them, as A2 did not. Then every
                             pairing-dependent quantity measured so far fails to single out the
                             instance, and clause ② is the only content the data supports.
                prediction matrix: A -> lo > 0 against every topw arm. B -> intervals straddle 0.
KILL            pre-registered: if world B, the statement records that TWO independent
                pairing-dependent quantities fail to rank the instance — which is a stronger form of
                R1011's finding than R1011 could make, because it is no longer about one metric.
POSITIVE CTRL   ⭐ THE SHAM IS THE CONTROL THIS ROUND IS BUILT ON. Discriminativeness must DROP
                resolvably for `coval_core_sham` — the same criteria on the wrong prompt. If it does
                not, the quantity is NOT pairing-dependent and the whole round is void: a quantity a
                derangement leaves unchanged is text-only by R1014's argument.
NEGATIVE CTRL   an arm compared to ITSELF must give exactly zero.
PLACEBO         `topw_k4_detA` vs `_detB`, a deterministic pair, must give exactly zero.
NOISE FLOOR     the placebo pair's interval width — a known-zero effect in the same design.
MULTIPLICITY    every extension arm × 1 reference, all pairs reported.
ARTIFACT        results/discriminativeness.json with this file's source hash.
IMPOSSIBLE      ⚠ construct validity — N/A: a discriminative criterion is not thereby a GOOD one.
                This asks whether the quantity separates, never whether separation means quality.
                ⚠ the judge — every satisfaction value routes through the release's judge, so this
                is a claim about what that judge scores, not about the criteria in the abstract.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls  # noqa: E402

NBOOT, SEED = 8000, 1015
CORE, SHAM = "coval_core", "coval_core_sham"
L = "ABCD"


def main() -> int:
    r1011 = next(A27.glob("R1011_*/results/instance_rank.json"), None)
    if r1011 is None:
        print("  UNRUNNABLE: R1011's artifact is missing. Exit 2, never 0.")
        return 2
    ext = json.loads(r1011.read_text())["extension"]
    tg, _ = load_targets()
    S0 = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    n = len(pids)
    print(f"  extension READ from R1011 (full-coverage only): {ext}")

    def disc(nm):
        """mean over criteria of the VARIANCE of satisfaction across this prompt's responses."""
        f = RES / f"sat_{nm}.npz"
        if not f.exists():
            return None
        Sa = load_sat(f)
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
        return v if np.isfinite(v).sum() >= 200 else None

    want = sorted(set(ext) | {CORE, SHAM})
    V = {}
    for a in want:
        d = disc(a)
        if d is not None:
            V[a] = np.nan_to_num(d, nan=np.nanmean(d))
    if CORE not in V or SHAM not in V:
        print(f"  UNRUNNABLE: need both {CORE} and {SHAM}; have {sorted(V)}. Exit 2, never 0.")
        return 2
    print(f"  arms with satisfaction matrices: {sorted(V)}")

    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(NBOOT, n))

    def paired(a, b):
        d = V[a] - V[b]
        bs = d[idx].mean(axis=1)
        return float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))

    s_m, s_lo, s_hi = paired(CORE, SHAM)
    pos_ok = s_lo > 0
    z_m, z_lo, z_hi = paired(CORE, CORE)
    neg_ok = z_m == 0.0 and z_lo == 0.0 and z_hi == 0.0
    tA, tB = "topw_k4_detA", "topw_k4_detB"
    have = tA in V and tB in V
    p_m, p_lo, p_hi = paired(tA, tB) if have else (np.nan,) * 3
    plac_ok = have and abs(p_m) < 1e-12 and abs(p_lo) < 1e-12 and abs(p_hi) < 1e-12
    print(f"\n  ⭐ POSITIVE CONTROL — discriminativeness must DROP for the sham (same criteria, WRONG")
    print(f"     prompt): core − sham = {s_m:+.6f} [{s_lo:+.6f}, {s_hi:+.6f}]  "
          f"{'PASS' if pos_ok else '⛔ FAIL'}")
    print(f"     ⚠ if this fails the quantity is NOT pairing-dependent and the round is VOID — a")
    print(f"       quantity a derangement leaves unchanged is text-only by R1014's argument.")
    print(f"  NEGATIVE  an arm against itself: {z_m:+.6f}  {'PASS' if neg_ok else '⛔ FAIL'}")
    print(f"  PLACEBO   {tA} vs {tB} (deterministic pair): {p_m:+.6f} "
          f"[{p_lo:+.6f}, {p_hi:+.6f}]  {'PASS' if plac_ok else '⛔ FAIL'}")
    if not (pos_ok and neg_ok and plac_ok):
        print("\n⛔ a control failed; nothing below certifies anything. Exit 2, never 0.")
        return 2
    floor = p_hi - p_lo
    print(f"  NOISE FLOOR — the placebo pair's interval width: {floor:.8f}")

    print(f"\n  {'arm':<20}{'disc':>11}{'Δ (core − arm)':>16}{'lo':>11}{'hi':>11}  resolvable")
    print(f"  {CORE:<20}{V[CORE].mean():>11.6f}")
    rows = []
    for a in [x for x in ext if x in V and not x.startswith("coval_core")]:
        m, lo, hi = paired(CORE, a)
        res = "core HIGHER" if lo > 0 else ("core LOWER" if hi < 0 else "no")
        rows.append({"arm": a, "disc": float(V[a].mean()), "delta": m, "lo": lo, "hi": hi,
                     "resolvable": res})
        print(f"  {a:<20}{V[a].mean():>11.6f}{m:>+16.6f}{lo:>+11.6f}{hi:>+11.6f}  {res}")

    higher = [r for r in rows if r["resolvable"] == "core HIGHER"]
    lower = [r for r in rows if r["resolvable"] == "core LOWER"]
    world = ("A ANOTHER QUANTITY SEPARATES — discriminativeness resolvably orders the instance above "
             f"all {len(rows)} topw arms" if rows and len(higher) == len(rows) else
             f"B ONLY CLAUSE ② — discriminativeness resolves {len(higher)} higher and {len(lower)} "
             f"lower of {len(rows)}, so it does not single out the instance either")
    print(f"\n⭐ {world}")
    if not (rows and len(higher) == len(rows)):
        print("⛔ PRE-REGISTERED KILL FIRES: TWO independent pairing-dependent quantities — A2")
        print("   (R1011) and discriminativeness (here) — both fail to rank the instance above the")
        print("   topw family. That is stronger than R1011 alone, because it is no longer about one")
        print("   metric: the failure to single out the instance survives changing the quantity.")
    print("\n⚠ A DISCRIMINATIVE CRITERION IS NOT THEREBY A GOOD ONE. This asks whether the quantity")
    print("   separates, never whether separation would mean quality. And every satisfaction value")
    print("   routes through the release's judge, so it is a claim about what that judge scores.")

    out = HERE / "results" / "discriminativeness.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="is clause ②'s A2 the only pairing-dependent content that could be definitional",
        n_prompts=n, nboot=NBOOT, seed=SEED, extension=ext,
        controls={"positive_sham_drops": {"d": s_m, "lo": s_lo, "hi": s_hi, "ok": bool(pos_ok)},
                  "negative_self_zero": bool(neg_ok),
                  "placebo_det_pair": {"d": p_m, "ok": bool(plac_ok)}},
        noise_floor=floor, core_disc=float(V[CORE].mean()), sham_disc=float(V[SHAM].mean()),
        rows=rows, world=world, n_higher=len(higher), n_lower=len(lower), n_rivals=len(rows),
        limitation="a discriminative criterion is not thereby a good one; and every satisfaction "
                   "value routes through the release's judge",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
