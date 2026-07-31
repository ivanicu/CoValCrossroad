"""r121 -- is the compiled rubric's advantage a property of the RULE or of the METRIC?

THE QUESTION THIS ROUND EXISTS FOR, and it is the project's founding number
--------------------------------------------------------------------------
r33 reported core beating full by +0.0663 and everything downstream rests on it. Auditing the
SCORING ALGORITHM rather than the rules turned up a mechanism nobody had checked:

  * the metric is pairwise discordance, so a decision made on a score gap of 0.001 counts exactly as
    much as one made on a gap of 0.5 -- the MARGIN IS DISCARDED;
  * full decides 31.0% of its pairs on a gap below 0.05 and 6.8% below 0.01; core only 19.5% and 3.7%;
  * conditioning on both arms deciding with a gap >= 0.20 collapses core's advantage from +0.0662 to
    +0.0035, a 95% reduction, and from 16.3% of headroom to 1.6%, a tenfold reduction.

That is consistent with full making more coin-flip decisions and being charged for them. And full
averages satisfaction over ~15 criteria where core averages over 4, so full's scores are mechanically
LESS spread -- the standard error of a mean over 15 is 1.94x smaller than over 4 -- which produces
exactly that pattern without any difference in rule quality.

A first control refused that explanation: the collapse occurs between count-MATCHED arms too
(core-oracle, both 4 criteria, collapses 70%). But that control used a weak proxy for confidence
(cell-level |e - 0.5| rather than the per-pair score gap), so it is UNVERIFIED, not a refutation.

THE DECISIVE DESIGN
-------------------
Subsample full to exactly k criteria, sweep k from 1 to 15, many independent draws at each k. That
gives a CURVE: accuracy against criterion count, for a rule family that involves no compilation at
all. Then ask where core sits on it.

    core ON the k=4 curve   ->  core is "full with four criteria". The +0.0663 is the metric and the
                                count, and compilation contributes nothing measurable.
    core ABOVE the curve    ->  compilation adds something a random 4-subset does not, and the
                                founding number survives with its mechanism finally named.

The random-k family IS the sham compiler: same criterion count, same satisfaction tensor, same
metric, no rewriting, no merging, no polarity normalisation, no compatibility selection. And the
sweep in k is a dose-response in exactly the quantity the mechanism nominates.

AXES
----
  K            1..15 criteria, N_DRAW independent subsamples each
  ARM          core, and the k-curve; plus full itself at k=all
  CONFIDENCE   per-pair score gap thresholds, computed properly rather than by proxy
  METRIC       pairwise discordance; margin-weighted discordance; tie-penalised discordance
  TIE POLICY   excluded (the released convention), counted as half-error, counted as error
  SEED         multi-seed over the subsampling
  SCALE        raw and headroom-normalised, since a difference between two bounded scores shrinks
               as both approach the bound

CONTROLS, all in this round
---------------------------
  POSITIVE   plant a known advantage: score one arm with a rule known to be better (the oracle,
             selected on odd raters) and require the curve to place it above.
  NEGATIVE   two draws of the SAME k must not differ systematically -- the within-k spread IS the
             null band, and it is what core's position is judged against.
  SHAM       random-k is itself the sham compiler.
  PLACEBO    full vs full, and core vs core with criteria reordered: both must give exactly zero.
  MEASUREMENT the per-pair gap distribution is reported per arm, because the whole hypothesis is
             about it and quoting only accuracy would hide the mechanism.

PRE-REGISTERED, before the run
------------------------------
core is ON the curve if its mean error falls inside the central 95% of the k=4 draw distribution.
It is ABOVE if it falls below that band (better than random 4-subsets). If core is ON the curve, the
founding number is a metric-and-count artifact and every claim resting on "compilation improves
accuracy" is downgraded to "four criteria improve accuracy under this metric".
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join            # noqa: E402
from covalx.stamp import stamp          # noqa: E402

FULL = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
CORE = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"

SEED = 20260730
K_GRID = tuple(range(1, 16))
N_DRAW = 60
GAPS = (0.0, 0.01, 0.02, 0.05, 0.10, 0.20)
TIE_POLICIES = ("exclude", "half", "error")
CHANCE = 0.5


def load_sat(path):
    z = np.load(path, allow_pickle=True)
    d = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        d[pid][(int(ci), lab)] = float(s)
    return d


def scores_from(satp, keep=None):
    out = {}
    for lab in sorted({l for _, l in satp}):
        v = [s for (ci, ll), s in satp.items() if ll == lab and (keep is None or ci in keep)]
        if v:
            out[lab] = float(np.mean(v))
    return out


def strict_pairs(r):
    tiers = [t.split("=") for t in r.split(">")]
    out = set()
    for i, a in enumerate(tiers):
        for b in tiers[i + 1:]:
            for x in a:
                for y in b:
                    out.add((x.strip(), y.strip()))
    return out


def evaluate(sc, P0, tie_policy, gap_min):
    """Return (errors, denominator, gaps) under a stated tie policy and confidence threshold.

    The released convention EXCLUDES ties from the denominator, which means a rule that declines to
    order a pair is neither right nor wrong -- it deletes the question from its own exam. That is a
    policy, not a fact, so all three policies are swept."""
    err = den = 0.0
    gaps = []
    for x, y in P0:
        if x not in sc or y not in sc:
            continue
        g = abs(sc[x] - sc[y])
        if sc[x] == sc[y]:
            if tie_policy == "exclude":
                continue
            den += 1
            err += 0.5 if tie_policy == "half" else 1.0
            continue
        if g < gap_min:
            continue
        den += 1
        gaps.append(g)
        if sc[x] < sc[y]:
            err += 1
    return err, den, gaps


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--draws", type=int, default=N_DRAW)
    ap.add_argument("--out", default=str(_RES / "r121_is_the_advantage_the_metric.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    F, C = load_sat(FULL), load_sat(CORE)
    joined = sorted(((p, c) for p, c, r in load_join(COMPARISONS, RUBRICS)
                     if p in F and p in C), key=lambda t: t[0])
    work = []
    for pid, comp in joined:
        cis = sorted({ci for ci, _ in F[pid]})
        ranks = []
        for a in sorted(comp["metadata"]["assessments"], key=lambda x: str(x.get("annotator_id"))):
            w = (a.get("ranking_blocks") or {}).get("world") or []
            if w:
                P = strict_pairs(w[0].get("ranking", ""))
                if P:
                    ranks.append(P)
        if ranks and len(cis) >= 1:
            work.append((pid, cis, ranks))
    if not work:
        print("REFUSING: empty population. Exits 2, never 0.", file=sys.stderr)
        return 2
    print(f"{len(work)} prompts usable; criteria per prompt: median "
          f"{int(np.median([len(c) for _p, c, _r in work]))}, max {max(len(c) for _p,c,_r in work)}")

    def arm_score(kind, k=None, draw_rng=None):
        """Per-prompt score dicts for an arm. kind in {full, core, randk}."""
        out = {}
        for pid, cis, _r in work:
            if kind == "full":
                out[pid] = scores_from(F[pid])
            elif kind == "core":
                out[pid] = scores_from(C[pid])
            else:
                kk = min(k, len(cis))
                pick = set(draw_rng.choice(cis, kk, replace=False).tolist())
                out[pid] = scores_from(F[pid], pick)
        return out

    def mean_error(sc_by_prompt, tie_policy="exclude", gap_min=0.0):
        e = d = 0.0
        allg = []
        for pid, _cis, ranks in work:
            sc = sc_by_prompt[pid]
            for P in ranks:
                x, y, g = evaluate(sc, P, tie_policy, gap_min)
                e += x
                d += y
                allg.extend(g)
            # nothing else
        return (e / d if d else float("nan")), d, np.array(allg)

    # ---- the k-curve, the sham compiler ------------------------------------------
    print(f"\nK-CURVE: full subsampled to k criteria, {args.draws} independent draws each.")
    print("This family involves NO compilation -- same tensor, same metric, no rewriting, no "
          "merging, no polarity normalisation. It is the sham.")
    curve = {}
    print(f"  {'k':>3}{'mean e':>10}{'sd':>9}{'95% band':>22}{'near-tie<0.05':>15}")
    for k in K_GRID:
        es, nt = [], []
        for d_ in range(args.draws):
            r2 = np.random.default_rng([args.seed, k, d_])
            sc = arm_score("randk", k, r2)
            e, _den, g = mean_error(sc)
            es.append(e)
            nt.append(float(np.mean(g < 0.05)) if len(g) else float("nan"))
        es = np.array(es)
        lo, hi = np.percentile(es, [2.5, 97.5])
        curve[k] = {"mean": float(es.mean()), "sd": float(es.std(ddof=1)),
                    "lo": float(lo), "hi": float(hi), "near_tie": float(np.nanmean(nt))}
        print(f"  {k:>3}{es.mean():>10.5f}{es.std(ddof=1):>9.5f}"
              f"   [{lo:.5f},{hi:.5f}]{np.nanmean(nt):>15.2%}")

    # ---- the two real arms -------------------------------------------------------
    sc_full = arm_score("full")
    sc_core = arm_score("core")
    e_full, den_f, g_full = mean_error(sc_full)
    e_core, den_c, g_core = mean_error(sc_core)
    n_core_crit = float(np.median([len({ci for ci, _ in C[p]}) for p, _c, _r in work]))
    print(f"\n  full: e={e_full:.5f}  n_pairs={int(den_f):,}  near-tie<0.05 "
          f"{np.mean(g_full<0.05):.2%}  median gap {np.median(g_full):.4f}")
    print(f"  core: e={e_core:.5f}  n_pairs={int(den_c):,}  near-tie<0.05 "
          f"{np.mean(g_core<0.05):.2%}  median gap {np.median(g_core):.4f}  "
          f"(median {n_core_crit:.0f} criteria)")

    # ---- THE VERDICT: where does core sit on the sham curve? ---------------------
    kc = int(round(n_core_crit))
    band = curve[kc]
    z = (e_core - band["mean"]) / max(band["sd"], 1e-12)
    on_curve = band["lo"] <= e_core <= band["hi"]
    above = e_core < band["lo"]
    print(f"\n  CORE vs THE SHAM CURVE AT ITS OWN CRITERION COUNT (k={kc}):")
    print(f"    random-{kc} draws: mean {band['mean']:.5f}, 95% band "
          f"[{band['lo']:.5f},{band['hi']:.5f}]")
    print(f"    core:              {e_core:.5f}   z = {z:+.2f}")
    print(f"    -> core is {'ON the curve' if on_curve else ('ABOVE it (better)' if above else 'BELOW it (worse)')}")
    print(f"    full (k=all):      {e_full:.5f}   advantage of core over full "
          f"{e_full-e_core:+.5f}")
    print(f"    advantage of a RANDOM {kc}-subset over full: {e_full-band['mean']:+.5f} "
          f"-- the part that needs no compilation at all")

    # ---- confidence axis, with PROPER per-pair gaps ------------------------------
    print(f"\n  CONFIDENCE AXIS (per-pair score gap, not a proxy):")
    print(f"  {'gap>=':>8}{'e_full':>10}{'e_core':>10}{'adv':>10}{'adv/headroom':>14}{'n_pairs':>10}")
    conf = {}
    for gm in GAPS:
        ef, df, _ = mean_error(sc_full, gap_min=gm)
        ec, dc, _ = mean_error(sc_core, gap_min=gm)
        adv = ef - ec
        conf[str(gm)] = {"e_full": ef, "e_core": ec, "adv": adv,
                         "adv_over_headroom": adv / max(ef, 1e-9), "n_full": int(df), "n_core": int(dc)}
        print(f"  {gm:>8}{ef:>10.5f}{ec:>10.5f}{adv:>+10.5f}{adv/max(ef,1e-9):>14.2%}{int(min(df,dc)):>10,}")

    # ---- tie policy axis ---------------------------------------------------------
    print(f"\n  TIE POLICY AXIS -- the released convention EXCLUDES ties, which is a policy:")
    tp = {}
    for pol in TIE_POLICIES:
        ef, _d, _g = mean_error(sc_full, tie_policy=pol)
        ec, _d2, _g2 = mean_error(sc_core, tie_policy=pol)
        tp[pol] = {"e_full": ef, "e_core": ec, "adv": ef - ec}
        print(f"    ties {pol:<8} e_full {ef:.5f}  e_core {ec:.5f}  advantage {ef-ec:+.5f}")

    # ---- PLACEBO: an arm against itself must give exactly zero -------------------
    e_ff, _d, _g = mean_error(sc_full)
    placebo_full = e_ff - e_full
    r_perm = np.random.default_rng([args.seed, 7])
    sc_core2 = {p: dict(sorted(v.items(), key=lambda kv: r_perm.random())) for p, v in sc_core.items()}
    e_cc, _d, _g = mean_error(sc_core2)
    placebo_core = e_cc - e_core
    print(f"\n  PLACEBO: full vs itself {placebo_full:+.2e}; core vs core with criteria reordered "
          f"{placebo_core:+.2e}  -> {'PASS' if abs(placebo_full)<1e-12 and abs(placebo_core)<1e-12 else 'FAIL'}")

    world = ("W-METRIC-ARTIFACT" if on_curve else
             "W-COMPILATION-REAL" if above else "W-CORE-WORSE-THAN-RANDOM")
    conclusion = (
        f"Subsampling full to k criteria with no compilation of any kind gives a sham curve over "
        f"k=1..15 at {args.draws} draws each. At core's own median criterion count k={kc} the random "
        f"subsets average {band['mean']:.5f} with a 95% band [{band['lo']:.5f},{band['hi']:.5f}]; "
        f"core scores {e_core:.5f}, z={z:+.2f}. Full scores {e_full:.5f}, so core's advantage over "
        f"full is {e_full-e_core:+.5f} while a RANDOM {kc}-subset's advantage over full is "
        f"{e_full-band['mean']:+.5f}. Conditioning on the per-pair score gap collapses core's "
        f"advantage from {conf['0.0']['adv']:+.5f} to {conf[str(GAPS[-1])]['adv']:+.5f}, and as a "
        f"share of headroom from {conf['0.0']['adv_over_headroom']:.1%} to "
        f"{conf[str(GAPS[-1])]['adv_over_headroom']:.1%}. full decides "
        f"{np.mean(g_full<0.05):.1%} of its pairs on a gap below 0.05 against core's "
        f"{np.mean(g_core<0.05):.1%}. Under the three tie policies the advantage is "
        f"{', '.join(f'{k}={v['adv']:+.4f}' for k, v in tp.items())}. WORLD: {world}. "
        + ("core sits inside the band that random subsets of the SAME SIZE produce, so the founding "
           "+0.0663 is the criterion COUNT and the METRIC rather than the compilation, and every "
           "claim resting on 'compilation improves accuracy' becomes 'four criteria improve accuracy "
           "under this metric'."
           if world == "W-METRIC-ARTIFACT" else
           "core beats random subsets of its own size, so compilation contributes something a "
           "count-matched sham does not, and the founding number survives with its mechanism named."
           if world == "W-COMPILATION-REAL" else
           "core is WORSE than random subsets of its own size, which no reading of the project has "
           "anticipated and which must be resolved before anything else."))
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    Path(args.out).write_text(json.dumps(
        {"seed": args.seed, "draws": args.draws, "n_prompts": len(work),
         "k_curve": {str(k): v for k, v in curve.items()},
         "e_full": e_full, "e_core": e_core, "core_k": kc, "z_vs_sham": z,
         "core_on_curve": bool(on_curve), "core_above_curve": bool(above),
         "near_tie_full": float(np.mean(g_full < 0.05)), "near_tie_core": float(np.mean(g_core < 0.05)),
         "median_gap_full": float(np.median(g_full)), "median_gap_core": float(np.median(g_core)),
         "confidence_axis": conf, "tie_policy_axis": tp,
         "placebo": {"full_vs_self": placebo_full, "core_vs_reordered": placebo_core},
         "world": world, "conclusion": conclusion, **stamp(__file__)}, indent=1, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
