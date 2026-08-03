"""r127 -- whose opinion is the minus sign? The signed-rubric advantage, split by evidential basis.

THE CLAIM UNDER ATTACK (mine, and CoVal's A3 with it)
-----------------------------------------------------
r123 and an independent design both found that coval_full beats coval_core once the 25.6% of
criteria carrying NEGATIVE human ratings are sign-corrected, and that it is specifically the SIGN
and not the weighting that does the work (signed - magnitude-only = +0.082).

Reading the object rather than the number produced two facts that neither of those runs used:

  1. 63.5% of full's 15,248 criteria were rated by exactly ONE person. The rater-count
     distribution is bimodal -- n=1 (63.5%) or n>=10 (34.0%), with 0.2% in between. That is two
     data-collection regimes glued together, not one sample.
  2. 77.2% of the NEGATIVE criteria are n=1, against 58.8% of the positive ones. So "negative" is
     entangled with "only one person ever saw it".
  3. Among the multi-rated negatives, 99.1% have at least one rater on the POSITIVE side and 47.9%
     have >=40% of raters there. Those are not bad behaviours; they are splits.

So the minus sign that carries the advantage may be one person's opinion, or it may be a near-even
disagreement flattened into a direction. Either way it would not be a collective standard, which is
the thing CoVal's aggregation claims to produce.

ESTIMAND
--------
The gain in pairwise concordance with human rankings obtained by flipping a BLOCK of negative
criteria, per criterion flipped, where blocks partition the negatives by the evidential basis of
their sign:

    SINGLE     n == 1                      sign is one person's rating
    STABLE     n >= 5, bootstrap flip < 5% sign survives resampling the raters
    UNSTABLE   n >= 5, bootstrap flip >=10% sign does not survive resampling the raters
    MIDDLE     n >= 5, 5% <= flip < 10%    stated, not merged into either side

A block's gain is compared against a COUNT-MATCHED null: flip the same NUMBER of negative criteria,
drawn at random from the whole negative pool. Without that null the answer is arithmetic -- SINGLE
is 77% of the negatives and would carry most of any gain by sheer count.

THE TRAP THIS ROUND EXISTS TO AVOID
-----------------------------------
For n == 1 the bootstrap over raters is degenerate: every resample returns the same value, so the
flip rate is exactly 0.000 and a single rater scores as MAXIMALLY STABLE. Stability is UNDEFINED
there, not zero. SINGLE is therefore its own block and is never admitted to STABLE. A run that
computed stability blind to n would conclude that the most reliable signs in the dataset are the
ones held by one person.

PRE-REGISTERED KILL (written before any block gain was computed)
----------------------------------------------------------------
W-COLLECTIVE   STABLE's per-criterion gain exceeds its count-matched null (BH q=0.05) AND exceeds
               SINGLE's. The sign is a collective quantity; the r123 finding stands as stated.
W-ONE-PERSON   SINGLE's per-criterion gain exceeds its count-matched null while STABLE's does not.
               The advantage is single-rater opinion and the word "collective" is withdrawn from
               every sentence that rests on it, mine included.
W-NEITHER      No block exceeds its count-matched null. The sign carries no locatable evidence and
               the aggregate +0.082 is not attributable to any identified group of criteria.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join  # noqa: E402
from covalx.judge import human_pairs  # noqa: E402  -- the canonical parser, judge.py:241
from covalx.stamp import stamp  # noqa: E402

FULL_NPZ = _ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz"
CORE_NPZ = _ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_core.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"

# --- pre-registered, before any block gain was seen -----------------------------------------
STABLE_MAX_FLIP = 0.05      # bootstrap sign-flip rate below which a multi-rated sign is STABLE
UNSTABLE_MIN_FLIP = 0.10    # ... at or above which it is UNSTABLE. The gap is MIDDLE, reported.
MIN_MULTI = 5               # a sign needs >= 5 raters before its stability is even estimable
N_BOOT_SIGN = 2000          # resamples of the rater set, per criterion
N_NULL_SEEDS = 20           # count-matched null draws per block
N_BOOT_CI = 2000            # cluster bootstrap over prompts for the concordance CIs
BH_Q = 0.05


# ---------------------------------------------------------------------------------------------
# the scoring atom: a rubric arm scores each response, and its error is the share of the human
# ordered pairs it gets the wrong way round. Ties in the arm's own scores are excluded from the
# denominator, which is the project's standing convention and is stated here rather than assumed.
# ---------------------------------------------------------------------------------------------
def arm_error(scores_by_prompt, pairs_by_prompt):
    """Pooled over prompts: disagreements / comparable pairs. Returns (e, n_pairs, per_prompt)."""
    bad = tot = 0
    per = {}
    for pid, s in scores_by_prompt.items():
        pb = pd = 0
        for x, y in pairs_by_prompt.get(pid, ()):
            if x not in s or y not in s:
                continue
            if s[x] == s[y]:
                continue          # tie in the arm -> not a comparable decision
            pd += 1
            if s[x] < s[y]:
                pb += 1
        if pd:
            per[pid] = (pb, pd)
            bad += pb
            tot += pd
    return (bad / tot if tot else float("nan")), tot, per


def cluster_boot(per, rng, n=N_BOOT_CI):
    """Bootstrap over PROMPTS (responses are nested in prompts), returning the accuracy spread."""
    pids = np.array(list(per.keys()))
    b = np.array([per[p][0] for p in pids], float)
    d = np.array([per[p][1] for p in pids], float)
    idx = rng.integers(0, len(pids), size=(n, len(pids)))
    acc = 1.0 - (b[idx].sum(1) / np.maximum(d[idx].sum(1), 1e-12))
    return float(np.percentile(acc, 2.5)), float(np.percentile(acc, 97.5))


def paired_boot(perA, perB, rng, n=N_BOOT_CI):
    """CI for accuracy(A) - accuracy(B) on the SAME prompts -- paired, not two independent CIs."""
    pids = np.array(sorted(set(perA) & set(perB)))
    bA = np.array([perA[p][0] for p in pids], float)
    dA = np.array([perA[p][1] for p in pids], float)
    bB = np.array([perB[p][0] for p in pids], float)
    dB = np.array([perB[p][1] for p in pids], float)
    idx = rng.integers(0, len(pids), size=(n, len(pids)))
    a = 1.0 - bA[idx].sum(1) / np.maximum(dA[idx].sum(1), 1e-12)
    c = 1.0 - bB[idx].sum(1) / np.maximum(dB[idx].sum(1), 1e-12)
    dd = a - c
    p = 2 * min((dd <= 0).mean(), (dd >= 0).mean())
    return float(np.mean(dd)), float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5)), \
        float(max(p, 1.0 / (n + 1)))


def bh(pvals, q=BH_Q):
    order = np.argsort(pvals)
    keep = np.zeros(len(pvals), bool)
    C = len(pvals)
    for rank, i in enumerate(order, start=1):
        if pvals[i] <= q * rank / C:
            keep[order[:rank]] = True
    return keep


def load_sat(path):
    z = np.load(path, allow_pickle=True)
    d = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = str(m).split("|")
        d[pid][(int(ci), lab)] = float(s)
    return d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260730)
    ap.add_argument("--out", default=str(_RES / "r127_whose_sign.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    for p in (FULL_NPZ, CORE_NPZ, COMPARISONS, RUBRICS):
        if not p.exists():
            print(f"REFUSING: missing {p}. Exits 2, never 0.", file=sys.stderr)
            return 2

    SAT_F = load_sat(FULL_NPZ)
    SAT_C = load_sat(CORE_NPZ)

    # ---- criterion table: sign, rater count, bootstrap sign stability -----------------------
    ratings = {}
    for line in open(RUBRICS):
        r = json.loads(line)
        cid = r["conversation"]["id"]
        for i, it in enumerate(r.get("coval_full") or []):
            s = [x["score"] for x in (it.get("scores") or [])]
            if s:
                ratings[(cid, i)] = np.asarray(s, float)

    block = {}
    flip_rate = {}
    for k, s in ratings.items():
        n = len(s)
        mu = s.mean()
        if n < MIN_MULTI:
            # stability is UNDEFINED, not zero: every resample of a single rater returns that
            # rater. Never admitted to STABLE.
            block[k] = "SINGLE" if n == 1 else "FEW"
            flip_rate[k] = None
            continue
        b = rng.choice(s, size=(N_BOOT_SIGN, n), replace=True).mean(1)
        fr = float((np.sign(b) != np.sign(mu)).mean())
        flip_rate[k] = fr
        block[k] = ("STABLE" if fr < STABLE_MAX_FLIP else
                    "UNSTABLE" if fr >= UNSTABLE_MIN_FLIP else "MIDDLE")

    # ---- align prompts -----------------------------------------------------------------------
    prompts = []
    for pid, comp, rub in load_join(str(COMPARISONS), str(RUBRICS)):
        if pid not in SAT_F or pid not in SAT_C:
            continue
        cid = rub["conversation"]["id"]
        crit = defaultdict(dict)          # ci -> {label: sat}
        for (ci, lab), v in SAT_F[pid].items():
            crit[ci][lab] = v
        core = defaultdict(dict)
        for (ci, lab), v in SAT_C[pid].items():
            core[ci][lab] = v
        labs = sorted(set.intersection(*[set(d) for d in crit.values()])) if crit else []
        if len(labs) < 2 or not core:
            continue
        # every annotator's own world ranking contributes its ordered pairs -- the canonical
        # parser pools them and drops ties, so a prompt's pair count is its annotator count times
        # the strict pairs each one implied, not 6.
        pairs = human_pairs((comp.get("metadata") or {}).get("assessments") or [])
        if not pairs:
            continue
        items = []
        for ci, d in crit.items():
            k = (cid, ci)
            if k not in ratings:
                continue
            items.append((ci, float(ratings[k].mean()) < 0, block[k],
                          np.array([d.get(l, np.nan) for l in labs])))
        if not items:
            continue
        core_mat = np.array([[core[ci].get(l, np.nan) for l in labs] for ci in sorted(core)])
        prompts.append({"pid": pid, "cid": cid, "labs": labs, "items": items, "pairs": pairs,
                        "core": core_mat})

    if not prompts:
        print("REFUSING: zero prompts survived alignment. A statistic over an empty population is "
              "not a null. Exits 2.", file=sys.stderr)
        return 2

    n_neg = sum(1 for p in prompts for _ci, neg, _b, _v in p["items"] if neg)
    n_all = sum(len(p["items"]) for p in prompts)
    counts = defaultdict(int)
    for p in prompts:
        for _ci, neg, b, _v in p["items"]:
            if neg:
                counts[b] += 1
    print(f"{len(prompts)} prompts, {n_all} criterion instances, {n_neg} negative "
          f"({n_neg/n_all:.1%})")
    print(f"  negative criteria by evidential basis of the sign:")
    for b in ("SINGLE", "FEW", "STABLE", "MIDDLE", "UNSTABLE"):
        if counts[b]:
            print(f"    {b:<10}{counts[b]:>7}  ({counts[b]/n_neg:.1%} of negatives)")

    pairs_by_prompt = {p["pid"]: p["pairs"] for p in prompts}

    def build(flip_set):
        """flip_set: set of (pid, ci) whose satisfaction is read as 1-v. Everything else raw."""
        out = {}
        for p in prompts:
            acc = {l: [] for l in p["labs"]}
            for ci, _neg, _b, vec in p["items"]:
                f = (p["pid"], ci) in flip_set
                for j, l in enumerate(p["labs"]):
                    v = vec[j]
                    if np.isnan(v):
                        continue
                    acc[l].append(1.0 - v if f else v)
            out[p["pid"]] = {l: float(np.mean(v)) for l, v in acc.items() if v}
        return out

    def core_scores():
        out = {}
        for p in prompts:
            m = p["core"]
            out[p["pid"]] = {l: float(np.nanmean(m[:, j])) for j, l in enumerate(p["labs"])}
        return out

    negs_by_block = defaultdict(list)
    all_negs = []
    for p in prompts:
        for ci, neg, b, _v in p["items"]:
            if neg:
                negs_by_block[b].append((p["pid"], ci))
                all_negs.append((p["pid"], ci))

    # ---- PLACEBO with a value known in advance ----------------------------------------------
    e_unwt, n_pairs, per_unwt = arm_error(build(set()), pairs_by_prompt)
    e_placebo, _, _ = arm_error(build(set()), pairs_by_prompt)
    assert e_placebo == e_unwt
    print(f"\n  PLACEBO  flipping the empty set reproduces the unflipped arm exactly: "
          f"|diff| = {abs(e_placebo - e_unwt):.2e}   (a derivation, not a finding)")

    e_all, _, per_all = arm_error(build(set(all_negs)), pairs_by_prompt)
    e_core, _, per_core = arm_error(core_scores(), pairs_by_prompt)
    print(f"\n  {'arm':<28}{'accuracy':>10}{'95% CI':>22}{'pairs':>9}")
    for nm, e, per in (("full, signs ignored", e_unwt, per_unwt),
                       ("full, all negatives flipped", e_all, per_all),
                       ("core (4 compiled criteria)", e_core, per_core)):
        lo, hi = cluster_boot(per, np.random.default_rng(args.seed + 1))
        print(f"  {nm:<28}{1-e:>10.4f}   [{lo:.4f}, {hi:.4f}]{sum(v[1] for v in per.values()):>9}")

    # POSITIVE CONTROL: the instrument must be shown to move on a case whose answer is known --
    # flipping every negative is the case r123 and the independent design both measured.
    d_all, lo_all, hi_all, p_all = paired_boot(per_all, per_unwt,
                                               np.random.default_rng(args.seed + 2))
    moved = lo_all > 0
    print(f"\n  POSITIVE CONTROL  flip-all vs flip-none = {d_all:+.5f} [{lo_all:+.5f}, {hi_all:+.5f}]"
          f"  -> instrument {'MOVES' if moved else 'DOES NOT MOVE'}")
    if not moved:
        print("REFUSING to report block gains: the instrument has not been shown to return a "
              "non-zero answer on the one case whose answer is known. Every block null would be "
              "silence rather than a measurement. Exits 3.", file=sys.stderr)
        return 3

    # ---- per-block gain, against a COUNT-MATCHED null ----------------------------------------
    print(f"\n  Each block flipped ALONE, against {N_NULL_SEEDS} count-matched draws from the "
          f"whole negative pool.\n  The null holds the NUMBER of flips fixed and randomises WHICH "
          f"criteria are flipped -- without it, the\n  largest block wins by counting.\n")
    print(f"  {'block':<10}{'k':>7}{'gain':>10}{'per 1k':>9}{'null mean':>11}{'null sd':>9}"
          f"{'z':>8}{'p_boot':>9}")
    rows = []
    for b in ("SINGLE", "FEW", "STABLE", "MIDDLE", "UNSTABLE"):
        S = negs_by_block.get(b) or []
        if not S:
            continue
        e_b, _, per_b = arm_error(build(set(S)), pairs_by_prompt)
        gain, glo, ghi, gp = paired_boot(per_b, per_unwt, np.random.default_rng(args.seed + 3))
        null = []
        for s in range(N_NULL_SEEDS):
            r2 = np.random.default_rng(args.seed + 1000 + s)
            pick = [all_negs[i] for i in r2.choice(len(all_negs), size=len(S), replace=False)]
            e_n, _, _ = arm_error(build(set(pick)), pairs_by_prompt)
            null.append((1 - e_n) - (1 - e_unwt))
        null = np.array(null)
        z = (gain - null.mean()) / (null.std(ddof=1) if null.std(ddof=1) > 0 else np.nan)
        rows.append({"block": b, "k": len(S), "gain": gain, "ci": [glo, ghi], "p_boot": gp,
                     "per_1k": 1000 * gain / len(S),
                     "null_mean": float(null.mean()), "null_sd": float(null.std(ddof=1)),
                     "z_vs_count_matched": float(z)})
        print(f"  {b:<10}{len(S):>7}{gain:>+10.5f}{1000*gain/len(S):>+9.4f}"
              f"{null.mean():>+11.5f}{null.std(ddof=1):>9.5f}{z:>+8.2f}{gp:>9.4f}")

    keep = bh(np.array([r["p_boot"] for r in rows]))
    for r, k in zip(rows, keep):
        r["bh_survivor"] = bool(k)

    got = {r["block"]: r for r in rows}

    # ---- STRONGEST CONFOUND, and its control in the same iteration ---------------------------
    # A sign is STABLE partly BECAUSE its magnitude is large: mean -8 survives resampling in a way
    # mean -0.7 does not. So the per-criterion ordering STABLE > SINGLE could be an effect of
    # |mean rating|, not of how many people backed the sign. A second candidate: DISCRIMINABILITY
    # -- a criterion whose satisfaction varies across the four responses moves any ranking more,
    # and if STABLE criteria happen to discriminate more, that alone produces the ordering.
    # Control: draw a SINGLE-block subset matched to STABLE on both, then compare per-criterion
    # gain at matched covariates. Pre-registered: the evidential-basis reading survives only if
    # STABLE still exceeds matched SINGLE with the matched-null z > 2.
    # MEASURED, and the opposite of what was predicted: SINGLE carries the LARGER |mean rating|
    # (7.26 vs 3.92), because a lone rater who bothers to mark a criterion negative uses the
    # scale's -10 ceiling while averaging ten raters pulls toward the middle. So the magnitude
    # confound runs AGAINST the finding rather than explaining it, and STABLE wins per criterion
    # at half the magnitude. Discriminability does favour STABLE (0.179 vs 0.134) and is the
    # covariate the matching actually has to remove.
    print(f"\n  CONFOUND CONTROL  |mean rating| and across-response discriminability, matched.")
    meta = {}
    for p in prompts:
        for ci, neg, b, vec in p["items"]:
            if not neg:
                continue
            v = vec[~np.isnan(vec)]
            meta[(p["pid"], ci)] = (abs(float(ratings[(p["cid"], ci)].mean())),
                                    float(v.std()) if v.size > 1 else 0.0, b)
    S_stable = [k for k in negs_by_block.get("STABLE", []) if k in meta]
    S_single = [k for k in negs_by_block.get("SINGLE", []) if k in meta]
    for nm, S in (("STABLE", S_stable), ("SINGLE", S_single)):
        mm = np.array([meta[k][0] for k in S])
        dd = np.array([meta[k][1] for k in S])
        print(f"    {nm:<8}n={len(S):>5}  |mean rating| {mm.mean():.2f} (sd {mm.std():.2f})   "
              f"discriminability {dd.mean():.4f} (sd {dd.std():.4f})")

    matched_rows = []
    if S_stable and S_single:
        tgt = np.array([[meta[k][0], meta[k][1]] for k in S_stable])
        pool = np.array([[meta[k][0], meta[k][1]] for k in S_single])
        # standardise both covariates on the pooled scale so neither dominates the distance
        both = np.vstack([tgt, pool])
        sc = both.std(0)
        sc[sc == 0] = 1.0
        gains_matched = []
        for s in range(N_NULL_SEEDS):
            r2 = np.random.default_rng(args.seed + 5000 + s)
            avail = list(range(len(S_single)))
            pick = []
            order = r2.permutation(len(S_stable))
            for i in order:
                if not avail:
                    break
                d = np.abs((pool[avail] - tgt[i]) / sc).sum(1)
                j = int(np.argmin(d))
                pick.append(S_single[avail[j]])
                avail.pop(j)
            e_m, _, per_m = arm_error(build(set(pick)), pairs_by_prompt)
            g, _, _, _ = paired_boot(per_m, per_unwt, np.random.default_rng(args.seed + 6000 + s),
                                     n=400)
            gains_matched.append(1000 * g / max(len(pick), 1))
        gm = np.array(gains_matched)
        stable_pk_obs = got["STABLE"]["per_1k"]
        zc = (stable_pk_obs - gm.mean()) / (gm.std(ddof=1) if gm.std(ddof=1) > 0 else np.nan)
        matched_rows = {"n_matched": len(S_stable), "stable_per_1k": stable_pk_obs,
                        "matched_single_per_1k_mean": float(gm.mean()),
                        "matched_single_per_1k_sd": float(gm.std(ddof=1)),
                        "z_stable_vs_matched_single": float(zc),
                        "seeds": N_NULL_SEEDS}
        print(f"    STABLE per 1k = {stable_pk_obs:+.4f}   vs magnitude+discriminability-matched "
              f"SINGLE = {gm.mean():+.4f} (sd {gm.std(ddof=1):.4f}, {N_NULL_SEEDS} seeds)   "
              f"z = {zc:+.2f}")
        print(f"    -> the evidential-basis reading "
              f"{'SURVIVES' if zc > 2 else 'DOES NOT SURVIVE'} covariate matching.")

    stable_beats_null = bool(got.get("STABLE") and got["STABLE"]["z_vs_count_matched"] > 2
                             and got["STABLE"]["bh_survivor"])
    single_beats_null = bool(got.get("SINGLE") and got["SINGLE"]["z_vs_count_matched"] > 2
                             and got["SINGLE"]["bh_survivor"])
    stable_pk = got.get("STABLE", {}).get("per_1k", float("-inf"))
    single_pk = got.get("SINGLE", {}).get("per_1k", float("-inf"))
    world = ("W-COLLECTIVE" if stable_beats_null and stable_pk > single_pk else
             "W-ONE-PERSON" if single_beats_null and not stable_beats_null else
             "W-NEITHER" if not (stable_beats_null or single_beats_null) else
             "W-BOTH")

    conclusion = (
        f"63.5% of coval_full's criteria were rated by exactly one person and the rater-count "
        f"distribution is bimodal (n=1 or n>=10, 0.2% between); 77.2% of the negatively-rated "
        f"criteria are single-rater, against 58.8% of the positive ones, so the sign that carries "
        f"the signed arm's advantage is entangled with how many people ever saw the criterion. "
        f"Splitting the negatives by the evidential basis of their sign -- SINGLE (one rater), "
        f"STABLE (>= {MIN_MULTI} raters, bootstrap sign-flip < {STABLE_MAX_FLIP:.0%}), UNSTABLE "
        f"(>= {UNSTABLE_MIN_FLIP:.0%}) -- and flipping each block alone against a count-matched "
        f"null of the same size drawn from the whole negative pool gives: "
        + "; ".join(f"{r['block']} k={r['k']} gain {r['gain']:+.5f} "
                    f"({r['per_1k']:+.4f} per 1000 flipped, z={r['z_vs_count_matched']:+.2f} vs "
                    f"count-matched)" for r in rows)
        + f". WORLD: {world}. "
        + ("The stable multi-rater signs beat their count-matched null and outperform single-rater "
           "signs per criterion flipped, so the advantage is a collective quantity and the r123 "
           "finding stands as stated." if world == "W-COLLECTIVE" else
           "Single-rater signs beat their count-matched null while stable multi-rater signs do not: "
           "the advantage is one person's opinion per criterion, and the word 'collective' is "
           "withdrawn from every sentence resting on it, this project's included."
           if world == "W-ONE-PERSON" else
           "No block beats its count-matched null, so the aggregate advantage is not attributable "
           "to any identified group of criteria and is carried by the flip operation at large."
           if world == "W-NEITHER" else
           "Both single-rater and stable multi-rater signs beat their count-matched nulls; the "
           "advantage is not exclusively either, and the per-criterion comparison decides which "
           "dominates.")
        + " Stability is UNDEFINED for a single rater, not zero: every resample of one rater returns "
          "that rater, so an n=1 sign scores as maximally stable under any bootstrap blind to n. "
          "SINGLE is therefore never admitted to STABLE, and a run that skipped this would have "
          "concluded that the most reliable signs in the dataset are the ones held by one person.")
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    Path(args.out).write_text(json.dumps(
        {"seed": args.seed, "n_prompts": len(prompts), "n_criteria": n_all, "n_negative": n_neg,
         "block_counts": dict(counts),
         "acc_unwt": 1 - e_unwt, "acc_signed_all": 1 - e_all, "acc_core": 1 - e_core,
         "n_pairs": n_pairs,
         "positive_control": {"delta": d_all, "ci": [lo_all, hi_all], "p": p_all, "moved": moved},
         "placebo_empty_flip_diff": abs(e_placebo - e_unwt),
         "blocks": rows, "world": world, "conclusion": conclusion,
         "preregistered": {"stable_max_flip": STABLE_MAX_FLIP,
                           "unstable_min_flip": UNSTABLE_MIN_FLIP, "min_multi": MIN_MULTI,
                           "n_boot_sign": N_BOOT_SIGN, "n_null_seeds": N_NULL_SEEDS,
                           "n_boot_ci": N_BOOT_CI, "bh_q": BH_Q},
         **stamp(__file__)}, indent=1, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
