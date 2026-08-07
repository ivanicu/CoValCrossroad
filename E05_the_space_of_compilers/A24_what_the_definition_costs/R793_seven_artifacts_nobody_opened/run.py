#!/usr/bin/env python3
"""R793 · seven artifacts nobody opened, and the one that retired a clause consumed 1 annotator of 16.

CHECK #395 ran R792's NEXT: of 11 deliberate artifacts in `corebench/results/`, **7 are opened by no
run.py in this arc's 468**. Two of the seven bear on committed work. `whose_verdicts.json` retired a
definitional clause on a statistic its own docstring does not register — and `whose_verdicts.py:79`
samples ONE annotator per prompt where the release ships a median of 16. That is the standard's own
poison row, in the artifact that decided a clause.

ESTIMAND        E1 the coverage enumeration · E2 ⭐ `whose_verdicts` on ALL annotators ·
                E3 ⭐ the normalisation curve · E4 ordering vs verdicts, against R792
IDENTIFICATION  E1/E2/E4 exact; E3 exact GIVEN a normalisation, and the choice among them is NOT
                identified by this data — the curve is the deliverable, not an adjudication
DERIVED FIRST   D1 the `vs FULL` column cannot move (deterministic) — the exact object check ·
                D2 all-annotator averaging IS the arc's A2 · D3 sampling 1 of 16 inflates variance
                and leaves expectation alone, so a POINT move would mean something else ·
                D4 dividing by a ceiling is not disattenuation (that divides by its square root)
WORLDS          A robust to the instrument, fragile to the normalisation · B robust to both ·
                C the instrument changes the answer — C checked FIRST, D3 says it should not fire
CONTROLS        OBJECT (D1 exact) · PLACEBO (an arm vs its own class = 1.0) · POSITIVE (band) ·
                NEGATIVE (full's class shuffled; `vs HUMAN` exactly unchanged) · SHAM (a random
                arm's class in place of full's) · NOISE FLOOR (CEIL_H bootstrap + split-half)
"""
import hashlib
import itertools
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                    # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
SHIPPED = RES / "whose_verdicts.json"
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
ARMS = ["coval_core", "topw_k4", "gen", "full", "topvar_k4", "random_k4_s0", "gen_sham"]
TOP = ("coval_core", "topw_k4", "gen")
NBOOT = 1200
SEEDS = [31337, 31338, 31339]


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def main():
    out = {"instrument_unit": "a (prompt, annotator) judgement for HUMAN, a PROMPT for FULL",
           "claim_unit": "an ARM", "claim_unit_e1": "an ARTIFACT"}

    # ================= E1 · the coverage enumeration, with both controls =========================
    print("  E1 - COVERAGE: which deliberate artifacts has this arc ever opened?")
    # ⛔ THE FIRST RUN COUNTED ITSELF. This round's own run.py names `whose_verdicts`,
    # `unit_robustness` and the subgroup file, so the scanner scored them READ and UNREAD fell
    # 7 -> 5 — the round changed the population it was measuring, by existing. R631 recorded this
    # exact vector ("a round scanning a population its own rounds write to contaminates itself
    # within one round"); R780 fixed it the same way. THIS_ROUND is excluded, and the exclusion is
    # printed so the count is auditable.
    THIS_ROUND = HERE.name
    runs = sorted(q for q in ARC.glob("R*/run.py") if q.parent.name != THIS_ROUND)
    src = {q.parent.name: q.read_text(errors="ignore") for q in runs}
    arts = [f.name for f in sorted(RES.iterdir())
            if not f.name.startswith(("sat_", "sat08_", "core_"))]
    hits = {a: sorted({r.split("_")[0] for r, s in src.items() if a[:-5] in s}) for a in arts}
    unread = [a for a, w in hits.items() if not w]
    pc = "R792" in hits.get("subgroup_coval_core_vs_topw_k4.json", [])
    # ⛔ AND THE NEGATIVE CONTROL'S SENTINEL WAS A LITERAL IN A SCANNED FILE, so it matched this
    # round's own source and printed FAIL. Assembled at runtime so the literal never exists on disk.
    sentinel = "zzz" + "_not" + "_a_file_" + format(0xDEAD, "x")
    nc = not any(sentinel in s for s in src.values())
    for a in arts:
        print(f"     {a:<40} {len(hits[a]):>3} rounds  "
              f"{'-- NONE --' if not hits[a] else ', '.join(hits[a][:4]) + ('…' if len(hits[a]) > 4 else '')}")
    print(f"     run.py files scanned {len(runs)} (this round, {THIS_ROUND}, EXCLUDED)   "
          f"artifacts {len(arts)}   UNREAD {len(unread)}")
    print(f"     POSITIVE CONTROL (R792 opens the subgroup file) {'PASS' if pc else 'FAIL'}   "
          f"NEGATIVE CONTROL (an impossible name matches nothing) {'PASS' if nc else 'FAIL'}")
    if not (pc and nc):
        print("  UNRUNNABLE: the enumeration instrument failed its own controls. Exit 2, never 0.")
        return 2
    out["e1"] = {"run_files": len(runs), "self_excluded": THIS_ROUND, "artifacts": len(arts), "unread": unread,
                 "hits": hits, "positive": pc, "negative": nc}

    # ================= OBJECT: rebuild, and reproduce the deterministic column ====================
    print("\n  OBJECT CHECK")
    if not SHIPPED.is_file():
        print("  UNRUNNABLE: the shipped artifact is absent. Exit 2, never 0.")
        return 2
    ship = json.loads(SHIPPED.read_text())["arms"]
    targets, _ = load_targets()
    SAT = {}
    for a in ARMS:
        f = RES / f"sat_{a}.npz"
        if f.is_file():
            SAT[a] = load_sat(f)
    fullS = SAT.get("full")
    fullc = {p: cls(yvec(fullS[p], sorted({i for i, _ in fullS[p]}))) for p in fullS}
    pids = sorted(p for p in fullc if p in targets and len(targets[p]) >= 2
                  and all(p in SAT[a] for a in SAT))
    P = len(pids)
    HC = [np.array([cls(np.array(y, float)) for y, _ in targets[p]]) for p in pids]
    nann = np.array([len(h) for h in HC])
    FC = np.array([fullc[p] for p in pids], float)
    print(f"     prompts {P}   annotators/prompt min {nann.min()} median {int(np.median(nann))} "
          f"max {nann.max()}   arms {len(SAT)}")

    C = {}
    for a in SAT:
        C[a] = np.array([cls(yvec(SAT[a][p], sorted({i for i, _ in SAT[a][p]}))) for p in pids],
                        float)

    def vs_human_all(cm):
        return np.array([(HC[i] == cm[i]).mean() for i in range(P)])

    def vs_full(cm, fc=None):
        fc = FC if fc is None else fc
        return (cm == fc).mean(axis=1)

    VH = {a: vs_human_all(C[a]) for a in C}
    VF = {a: vs_full(C[a]) for a in C}
    worst = max(abs(float(VF[a].mean()) - ship[a][1]) for a in C if a in ship)
    plac = float(vs_full(C["full"], FC).mean())
    okobj = worst < 1e-9 and abs(plac - 1.0) < 1e-12
    print(f"     D1  recomputed `vs FULL` against the shipped column: worst |Δ| {worst:.3e}   "
          f"(deterministic, so it CANNOT move)   {'PASS' if worst < 1e-9 else 'FAIL'}")
    print(f"     PLACEBO  `full` against FULL = {plac:.12f}, must be exactly 1.0   "
          f"{'PASS' if abs(plac - 1.0) < 1e-12 else 'FAIL'}")
    if not okobj:
        print("  UNRUNNABLE: the deterministic column did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"prompts": P, "ann_median": int(np.median(nann)), "vs_full_worst": worst,
                     "placebo": plac}

    # ================= E2 · all annotators against one =============================================
    print("\n  E2 - ALL ANNOTATORS AGAINST THE SHIPPED 1-ANNOTATOR DESIGN")
    rng = np.random.default_rng(SEEDS[0])
    BI = rng.integers(0, P, size=(NBOOT, P))
    rows = {}
    for a in sorted(C):
        d = VH[a] - VF[a]
        db = d[BI].mean(axis=1)
        lo, hi = float(np.percentile(db, 2.5)), float(np.percentile(db, 97.5))
        rows[a] = {"vs_human_all": float(VH[a].mean()), "vs_full": float(VF[a].mean()),
                   "raw_diff": float(d.mean()), "lo": lo, "hi": hi,
                   "shipped_vs_human": ship[a][0] if a in ship else None,
                   "shipped_raw": ship[a][2] if a in ship else None}
        r = rows[a]
        print(f"     {a:<14} vs HUMAN all {r['vs_human_all']:.4f} (shipped 1-ann "
              f"{r['shipped_vs_human']:.4f}, Δ {r['vs_human_all'] - r['shipped_vs_human']:+.4f})  "
              f"vs FULL {r['vs_full']:.4f}   raw {r['raw_diff']:+.4f} [{lo:+.4f}, {hi:+.4f}]")
    dmax = max(abs(rows[a]["vs_human_all"] - rows[a]["shipped_vs_human"]) for a in rows)
    print(f"     D3: the point estimates move at most {dmax:.4f}. Sampling 1 of "
          f"{int(np.median(nann))} inflates VARIANCE and leaves EXPECTATION alone, so a small move "
          f"here is the prediction and a large one would mean something else.")
    out["e2"] = rows

    # ================= NOISE FLOOR + CEIL_H =======================================================
    ceil_pairs = []
    for i in range(P):
        h = HC[i]
        if len(h) < 2:
            continue
        m = (h[:, None, :] == h[None, :, :]).mean(axis=2)
        iu = np.triu_indices(len(h), 1)
        ceil_pairs.append(m[iu].mean())
    ceil_pairs = np.array(ceil_pairs)
    CEIL_H = float(ceil_pairs.mean())
    cb = ceil_pairs[rng.integers(0, len(ceil_pairs), size=(NBOOT, len(ceil_pairs)))].mean(axis=1)
    clo, chi = float(np.percentile(cb, 2.5)), float(np.percentile(cb, 97.5))
    print(f"\n     NOISE FLOOR  CEIL_H over ALL annotator pairs = {CEIL_H:.6f} "
          f"[{clo:.6f}, {chi:.6f}]   (the shipped script sampled ONE pair per prompt)")

    # ================= E3 · the normalisation curve ===============================================
    print("\n  E3 - THE NORMALISATION CURVE: where the clause's fate is decided")

    def world(kind, ch=CEIL_H):
        if kind == "raw":
            return "B" if all(rows[a]["raw_diff"] > 0 and rows[a]["lo"] > 0 for a in TOP) else "A"
        if kind == "ceiling":
            return "B" if all(rows[a]["vs_human_all"] / ch > rows[a]["vs_full"] for a in TOP) else "A"
        if kind == "sqrt":
            return "B" if all(rows[a]["vs_human_all"] / math.sqrt(ch) > rows[a]["vs_full"]
                              for a in TOP) else "A"
        raise ValueError(kind)

    curve = {k: world(k) for k in ("raw", "ceiling", "sqrt")}
    for k, v in curve.items():
        note = {"raw": "the REGISTERED statistic", "ceiling": "the SHIPPED statistic",
                "sqrt": "standard disattenuation (D4)"}[k]
        print(f"     {k:<9} -> WORLD {v}    ({note})")
    swept = [world("ceiling", ch) for ch in cb[:400]]
    shareB = sum(1 for w in swept if w == "B") / len(swept)
    print(f"     CEIL_H swept over its own bootstrap interval: WORLD B in {shareB:.3f} of "
          f"{len(swept)} draws   {'>= 0.95 -> stable' if shareB >= 0.95 else '< 0.95 -> the ceiling estimate itself moves the verdict'}")
    for a in TOP:
        r = rows[a]
        print(f"       {a:<12} vs HUMAN {r['vs_human_all']:.4f} /CEIL_H = "
              f"{r['vs_human_all'] / CEIL_H:.4f}   /sqrt = "
              f"{r['vs_human_all'] / math.sqrt(CEIL_H):.4f}   vs FULL {r['vs_full']:.4f}")
    agree = len(set(curve.values())) == 1
    out["e3"] = {"curve": curve, "ceil_h": CEIL_H, "ceil_ci": [clo, chi],
                 "ceiling_sweep_shareB": shareB, "cells_agree": agree}

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    prng = np.random.default_rng(SEEDS[0] + 7)
    dose, fl, ce = {}, None, None
    for delta in (0.0, 0.05, 0.10, 0.20, 0.30):
        d = (VH["coval_core"] + delta) - VF["coval_core"]
        db = d[BI].mean(axis=1)
        pos = bool(np.percentile(db, 2.5) > 0)
        dose[str(delta)] = {"eff": float(d.mean()), "crosses": pos}
        print(f"     POSITIVE  delta {delta:<5} raw {d.mean():+.4f}  "
              f"{'crosses zero, resolved positive' if pos else 'still negative'}")
        if delta == 0.0:
            fl = pos
        if delta == 0.30:
            ce = pos
    posok = (fl is False) and (ce is True)
    print(f"     POSITIVE  band COMPUTED: floor {fl} at delta 0, ceiling {ce} at 0.30   "
          f"{'admissible' if fl != ce else 'DEGENERATE'}   {'PASS' if posok else 'FAIL'}")

    nrng = np.random.default_rng(SEEDS[0] + 13)
    FCp = FC[nrng.permutation(P)]
    vf_sh = vs_full(C["coval_core"], FCp)
    vh_unchanged = float(np.abs(vs_human_all(C["coval_core"]) - VH["coval_core"]).max())
    negok = vh_unchanged == 0.0 and vf_sh.mean() < VF["coval_core"].mean()
    print(f"     NEGATIVE  `full`'s class shuffled across prompts: vs FULL "
          f"{VF['coval_core'].mean():.4f} -> {vf_sh.mean():.4f}; vs HUMAN unchanged to "
          f"{vh_unchanged:.1e} (a DERIVATION, checked)   {'PASS' if negok else 'FAIL'}")
    print(f"               world it excludes: 'the vs-FULL column reflects something other than the "
          f"PROMPT-MATCHED rubric'")

    sham_arm = "random_k4_s0"
    vf_sham = (C["coval_core"] == C[sham_arm]).mean(axis=1)
    print(f"     SHAM      the same comparison against `{sham_arm}`'s class instead of `full`'s: "
          f"{vf_sham.mean():.4f} against {VF['coval_core'].mean():.4f}")

    frng = np.random.default_rng(SEEDS[0] + 17)
    halves = []
    for _ in range(20):
        h1 = np.zeros(P)
        h2 = np.zeros(P)
        for i in range(P):
            k = len(HC[i])
            pm = frng.permutation(k)
            a1, a2_ = pm[:k // 2], pm[k // 2:2 * (k // 2)]
            h1[i] = (HC[i][a1] == C["coval_core"][i]).mean()
            h2[i] = (HC[i][a2_] == C["coval_core"][i]).mean()
        halves.append(abs(h1.mean() - h2.mean()))
    print(f"     NOISE FLOOR  annotator split-half on the human column, 20 draws: "
          f"{np.mean(halves):.6f}")

    gate = okobj and posok and negok
    out["controls"] = {"dose": dose, "positive_ok": posok, "negative_ok": negok,
                       "negative_vf_shuffled": float(vf_sh.mean()),
                       "sham_vs_random_class": float(vf_sham.mean()),
                       "split_half": float(np.mean(halves)), "gate": gate}
    print(f"     GATE      {'PASS -- the kill may evaluate' if gate else 'FAIL -- UNVERIFIED'}")

    # ================= E4 · ordering vs verdicts, against R792 ====================================
    print("\n  E4 - `unit_robustness` SAYS THE ORDERING IS UNIT-ROBUST; R792 SAYS 11 VERDICTS FLIP")
    ur = json.loads((RES / "unit_robustness.json").read_text())
    same_order = ur["prompt_order"] == ur["annotator_order"]
    r792 = json.loads((ARC / "R792_the_estimand_was_a_default_nobody_chose"
                       / "results/estimand.json").read_text())
    flips = r792["e2"]["flips_default_vs_prior"]
    print(f"     `unit_robustness.json`: prompt order == annotator order -> {same_order}; "
          f"inversions {ur['inversions']}")
    print(f"     R792: {flips} of 190 pair VERDICTS flip between the two units")
    print(f"     -> both hold: an ORDERING claim and a PAIRWISE-RESOLUTION claim are different "
          f"objects. R792's headline needs the qualifier, and gets it here.")
    out["e4"] = {"unit_order_same": same_order, "r792_flips": flips,
                 "consistent": bool(same_order and flips > 0)}

    # ================= THE KILL ===================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world_v = "UNVERIFIED"
    elif dmax > 0.05:
        world_v = "C"
    elif agree and curve["raw"] == "B":
        world_v = "B"
    elif not agree:
        world_v = "A"
    else:
        world_v = "NO WORLD CLAIMED"
    print(f"     gate {gate}   max point move {dmax:.4f}   curve {curve}   sweep shareB "
          f"{shareB:.3f}  ->  WORLD {world_v}")
    out["world"] = world_v

    art = HERE / "results/coverage.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                             text=True).stdout.strip()
    except Exception:
        sha = "unknown"
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
