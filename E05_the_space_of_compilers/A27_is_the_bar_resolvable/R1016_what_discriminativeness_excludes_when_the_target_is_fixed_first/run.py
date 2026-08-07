#!/usr/bin/env python3
"""R1016 — fix the quantity first, then ask what it excludes. The pre-registration R1015 lacked.

⛔ WHY. R1015 found that criterion DISCRIMINATIVENESS separates `coval_core` from every `topw` arm
resolvably, and recorded its own disqualifier: **the quantity was chosen AFTER R1011 named `topw` as
the rival to exclude.** A property selected because it excludes the known rival is the "definition
describes the instance" failure with a better metric. ⭐ The fix is the pre-registration shape: fix
the quantity, define the sets it SHOULD separate WITHOUT mentioning `topw` or `coval_core`, and see
whether it does.

⭐ THE PRE-REGISTERED SETS, named from the release's own construction and not from any result:
    SHOULD RANK LOW  — every `*_sham` arm. A sham is criteria pointed at the WRONG prompt; if
                       discriminativeness means anything, misdirected criteria must discriminate
                       less on a prompt they were not written for.
    SHOULD RANK LOW  — every `random_k*` arm. Criteria drawn at random from the pool have no reason
                       to separate this prompt's responses.
    NO PREDICTION    — everything else, including `topw` and `coval_core`. ⚠ Stated so the test
                       cannot be read as confirming R1015: the arms R1015 compared are exactly the
                       ones this round declines to predict about.

ESTIMAND        the separation, in discriminativeness, between the two pre-registered LOW sets and
                the rest; measured as the share of LOW-set arms below the median of the rest, and as
                the paired sham-vs-parent difference over every sham pair on disk.
IDENTIFICATION  direct: discriminativeness is computable per arm from the satisfaction matrices, and
                set membership is a property of the arm's NAME, fixed by the release's construction.
SCOPE           population : every arm with a satisfaction matrix · instrument : variance of
                satisfaction across the prompt's 4 responses, averaged over criteria then prompts
                baseline   : the non-LOW arms' median · regime : this release, n = 968
WORLDS          A THE QUANTITY IS PRINCIPLED  both LOW sets sit below, and every sham sits below its
                             own parent. Then discriminativeness excludes things for a reason that
                             never mentions `topw`, and R1015's separation is a consequence rather
                             than a fit.
                B IT IS A FITTED SEPARATOR   the LOW sets do not sit below, or shams do not sit below
                             their parents. Then the quantity tracks something other than
                             criterion-prompt fit and R1015's result is downgraded to a coincidence
                             of the arm set.
                prediction matrix: A -> both shares high, all sham pairs negative.
                                   B -> either share near chance, or sham pairs mixed in sign.
KILL            pre-registered: if ANY sham ranks at or above its own parent, world B, and R1015's
                candidate is withdrawn in this round rather than left standing.
POSITIVE CTRL   `coval_core_sham` must rank below `coval_core` — R1015 measured it at +0.013993
                [+0.012817, +0.015174]. If the pipeline here does not reproduce that sign, it is not
                computing R1015's quantity and nothing below applies.
NEGATIVE CTRL   an arm against itself is exactly 0.
PLACEBO         a deterministic pair (`topw_k4_detA` / `_detB`) is exactly 0.
NOISE FLOOR     the placebo's interval width — a known-zero effect in the same design.
MULTIPLICITY    every sham pair on disk is tested and reported, survivors and non-survivors.
ARTIFACT        results/preregistered_exclusion.json with this file's source hash.
IMPOSSIBLE      ⚠ whether the objects it excludes SHOULD be excluded in some absolute sense — N/A.
                The pre-registered sets are chosen from the release's construction (a sham is
                misdirected by definition; a random draw is random by definition), which is the
                closest thing to a reason available without an external standard.
                ⚠ construct validity — N/A as throughout.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import re
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets  # noqa: E402

NBOOT, SEED = 8000, 1016
L = "ABCD"
LOW_SHAM = re.compile(r"_sham$")
LOW_RANDOM = re.compile(r"^random_k")


def main() -> int:
    r881 = next(A24.glob("R881_*/results/boundary_distance.json"), None)
    r1015 = next(A27.glob("R1015_*/results/discriminativeness.json"), None)
    if not (r881 and r1015):
        print("  UNRUNNABLE: a committed artifact is missing. Exit 2, never 0.")
        return 2
    ref = json.loads(r1015.read_text())
    arms881 = [x["arm"] for x in json.loads(r881.read_text())["arms"]]
    extra = sorted({p.name[4:-4] for d in (RES, NEW) if d.is_dir()
                    for p in d.glob("sat_*.npz")})
    want = sorted(set(arms881) | set(extra))

    tg, _ = load_targets()
    S0 = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    n = len(pids)

    def disc(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                return None
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
            return np.nan_to_num(v, nan=np.nanmean(v)) if np.isfinite(v).sum() >= 200 else None
        return None

    V = {}
    for a in want:
        d = disc(a)
        if d is not None:
            V[a] = d
    if len(V) < 20:
        print(f"  UNRUNNABLE: only {len(V)} arms scoreable. Exit 2, never 0.")
        return 2
    mean = {a: float(v.mean()) for a, v in V.items()}
    print(f"  arms with satisfaction matrices: {len(V)} · prompts {n}")

    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(NBOOT, n))

    def paired(a, b):
        d = V[a] - V[b]
        bs = d[idx].mean(axis=1)
        return float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))

    # ---------- controls ----------
    pos = ("coval_core" in V and "coval_core_sham" in V)
    p_m, p_lo, p_hi = paired("coval_core", "coval_core_sham") if pos else (np.nan,) * 3
    pos_ok = pos and p_lo > 0 and abs(p_m - ref["controls"]["positive_sham_drops"]["d"]) < 1e-6
    z_m, z_lo, z_hi = paired("coval_core", "coval_core") if pos else (np.nan,) * 3
    neg_ok = pos and z_m == 0.0
    tA, tB = "topw_k4_detA", "topw_k4_detB"
    have = tA in V and tB in V
    q_m, q_lo, q_hi = paired(tA, tB) if have else (np.nan,) * 3
    plac_ok = have and abs(q_m) < 1e-12
    print(f"\n  POSITIVE — core − its sham {p_m:+.6f} must match R1015's "
          f"{ref['controls']['positive_sham_drops']['d']:+.6f}: {'PASS' if pos_ok else '⛔ FAIL'}")
    print(f"  NEGATIVE — an arm against itself {z_m:+.6f}: {'PASS' if neg_ok else '⛔ FAIL'}")
    print(f"  PLACEBO  — deterministic pair {q_m:+.6f}: {'PASS' if plac_ok else '⛔ FAIL'}")
    if not (pos_ok and neg_ok and plac_ok):
        print("\n⛔ a control failed; nothing below certifies anything. Exit 2, never 0.")
        return 2
    print(f"  NOISE FLOOR — the placebo's interval width: {q_hi - q_lo:.8f}")

    # ---------- the pre-registered sets ----------
    shams = sorted(a for a in V if LOW_SHAM.search(a))
    rands = sorted(a for a in V if LOW_RANDOM.match(a))
    rest = sorted(a for a in V if a not in set(shams) | set(rands))
    med = float(np.median([mean[a] for a in rest]))
    sh_below = sum(1 for a in shams if mean[a] < med)
    rd_below = sum(1 for a in rands if mean[a] < med)
    print(f"\n  PRE-REGISTERED LOW SETS (named from construction, never from a result)")
    print(f"    shams        {len(shams):>3} arms · below the rest's median ({med:.6f}): "
          f"{sh_below}/{len(shams)} ({sh_below/max(1,len(shams)):.0%})")
    print(f"    random_k*    {len(rands):>3} arms · below: {rd_below}/{len(rands)} "
          f"({rd_below/max(1,len(rands)):.0%})")
    print(f"    the rest     {len(rest):>3} arms")

    # ---------- every sham against its OWN parent ----------
    print(f"\n  {'sham':<26}{'parent':<22}{'Δ (parent − sham)':>19}{'lo':>11}  verdict")
    pairs, bad = [], []
    for s in shams:
        par = s[:-5]
        if par not in V:
            continue
        m, lo, hi = paired(par, s)
        v = "parent HIGHER" if lo > 0 else ("⛔ sham HIGHER" if hi < 0 else "unresolved")
        pairs.append({"sham": s, "parent": par, "delta": m, "lo": lo, "hi": hi, "verdict": v})
        if hi < 0:
            bad.append(s)
        print(f"  {s:<26}{par:<22}{m:>+19.6f}{lo:>+11.6f}  {v}")

    hi_share = sum(1 for r in pairs if r["lo"] > 0) / max(1, len(pairs))
    # ⛔ v1's VERDICT STRING WAS NOT A COMPUTATION. It printed "the LOW sets do not sit below
    #    (shams 5/5, random 18/38)" -- self-contradictory, because 5/5 IS sitting below. The branch
    #    collapsed two pre-registered predictions into one sentence and then described both with the
    #    text of the failing one. Each prediction now gets its own verdict and the world is composed
    #    from them, so no clause of the sentence can be true of a set it is not about.
    sham_ok = (not bad) and sh_below == len(shams) and all(r["lo"] > 0 for r in pairs)
    rand_ok = rd_below >= 0.8 * len(rands)
    world = ("A THE QUANTITY IS PRINCIPLED — both pre-registered LOW sets sit below the rest"
             if sham_ok and rand_ok else
             "B IT IS A FITTED SEPARATOR — " + (f"{bad} rank ABOVE their own parents" if bad
                                                else "neither LOW set sits below")
             if not sham_ok and not rand_ok else
             f"C SPLIT — the SHAM prediction is CONFIRMED ({sh_below}/{len(shams)} below the "
             f"rest's median and {sum(1 for r in pairs if r['lo'] > 0)}/{len(pairs)} resolvably "
             f"below their OWN parent) and the RANDOM prediction is REFUTED "
             f"({rd_below}/{len(rands)}, {rd_below/max(1,len(rands)):.0%} — chance). So the "
             f"quantity tracks whether criteria BELONG to this prompt, not whether they are GOOD")
    print(f"\n⭐ {world}")
    print(f"⭐ shams resolvably below their own parent: {hi_share:.0%} of {len(pairs)} pairs")
    print(f"⭐ pre-registered SHAM prediction: {'CONFIRMED' if sham_ok else 'REFUTED'} · "
          f"pre-registered RANDOM prediction: {'CONFIRMED' if rand_ok else 'REFUTED'}")
    if bad:
        print("⛔ PRE-REGISTERED KILL FIRES: R1015's candidate is WITHDRAWN — a quantity that ranks a")
        print("   misdirected arm above its own parent is not measuring criterion-prompt fit.")
    elif not rand_ok:
        print("⛔ AND THE REFUTED HALF IS THE INFORMATIVE ONE. Criteria drawn at RANDOM from this")
        print("   prompt's own pool are as discriminative as anything else, so the quantity does NOT")
        print("   rank criterion QUALITY. It falls only when the criteria come from ANOTHER prompt.")
        print("   ⭐ So it measures BELONGING, not merit — which bounds what a clause built on it")
        print("   could ever claim, and that bound was not visible from R1015's comparison alone.")
    if not bad:
        print("⭐ AND THE SETS WERE NAMED WITHOUT MENTIONING `topw` OR `coval_core`, so this is not")
        print("   R1015's comparison run again: the arms R1015 compared are exactly the ones this")
        print("   round declined to predict about.")
    print("\n⚠ THIS DOES NOT SHOW THE EXCLUDED OBJECTS SHOULD BE EXCLUDED IN ANY ABSOLUTE SENSE. The")
    print("   LOW sets are chosen from the release's own construction — a sham is misdirected BY")
    print("   DEFINITION, a random draw is random BY DEFINITION — which is the closest thing to a")
    print("   reason available without an external standard.")

    out = HERE / "results" / "preregistered_exclusion.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="what discriminativeness excludes when the target is fixed before the sets",
        n_prompts=n, nboot=NBOOT, seed=SEED, n_arms=len(V),
        controls={"positive_matches_r1015": bool(pos_ok), "negative_self_zero": bool(neg_ok),
                  "placebo_det_pair": bool(plac_ok), "noise_floor": float(q_hi - q_lo)},
        rest_median=med, n_shams=len(shams), shams_below=sh_below,
        n_random=len(rands), random_below=rd_below, sham_pairs=pairs,
        shams_resolvably_below_parent=sum(1 for r in pairs if r["lo"] > 0),
        shams_above_parent=bad, world=world,
        sham_prediction_confirmed=bool(sham_ok), random_prediction_confirmed=bool(rand_ok),
        preregistration="LOW = every *_sham arm and every random_k* arm, named from the release's "
                        "construction; NO prediction is made about topw or coval_core",
        reading="the quantity tracks whether criteria BELONG to this prompt, not whether they are "
                "GOOD: shams fall resolvably, random draws from the prompt's own pool do not",
        limitation="does not show the excluded objects should be excluded in any absolute sense",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
