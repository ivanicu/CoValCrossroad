"""r134/independent_A -- do a person's OWN criterion ratings predict THEIR OWN ranking of the
four responses better than a DIFFERENT person's ratings of the SAME criteria do?

THE CLAIM UNDER ATTACK
-----------------------
OpenAI's Collective Alignment release treats a participant's -10..+10 criterion ratings as a
proxy for that participant's values, and everything downstream (compiling criteria, aggregating
ratings, deriving "collective" policy) assumes the elicitation INDIVIDUATES: what a person says
matters is informative about what THAT person actually prefers. If a stranger's ratings predict a
person's own preferences just as well as that person's own ratings do, the ratings carry no
personal signal and "collective values" is a description of an elicitation that never
individuated anyone -- it would be measuring something common to the rating exercise itself
(response quality, generic rater severity, criterion wording), not a person-specific value.

ESTIMAND, IN WORDS -- read before any code below
--------------------------------------------------
UNIT: an (annotator P, prompt X, ranking-block b) instance, i.e. one person's assessment of one
prompt, evaluated separately for b = "world" (all 15,593 assessments carry this) and b =
"personal" (3,584 do -- a strict subset, used as a same-sitting confound probe, see below).

For each instance, and each admissible STRANGER Q -- another annotator who also assessed prompt
X, with Q != P and |S_P intersect S_Q| >= K_MIN criteria in common, where S_A = the set of
coval_full criterion indices annotator A actually rated for prompt X (indices are built with the
IDENTICAL filter covalx's own satisfaction-tensor build used: keep a coval_full item only if its
`scores` list is non-empty, then enumerate in file order -- this is required for the index to line
up with `meta`'s "criterionindex" field in the precomputed .npz) --

  I(P,Q)      = S_P intersect S_Q                                    (shared, count-matched set)
  score_r(A)  = sum_{c in I(P,Q)} rating_A(c) * sat(X, c, r)          for r in {A,B,C,D}
                (SIGNED rating as weight -- per the established convention, this makes a
                negative-mean "undesirable behaviour" criterion automatically count AGAINST a
                response that satisfies it, without needing to know which quarter of criteria are
                flipped)
  pred(A)     = the 4 responses ordered by score_r(A) descending
  agree(A)    = fraction of P's DECISIVE (non-tied) pairs in P's TRUE ranking (ranking_blocks[b])
                that pred(A) places in the same relative order (a scoring tie = 0.5 credit,
                chance = 0.5 in expectation)
  diff(P,X,Q,b) = agree(P's own ratings, restricted to I(P,Q)) - agree(Q's ratings, restricted to I(P,Q))

Both arms see EXACTLY the same criteria (I(P,Q)) and the same count -- this is what makes "own"
and "other" comparable rather than a coverage artefact (the task's stated trap).

  D(P,X,b)   = mean over admissible Q of diff(P,X,Q,b)          [instance statistic]
  D_bar(b)   = mean over instances (P,X) of D(P,X,b)            [HEADLINE, b in {world, personal}]

UNIT OF THE HEADLINE: percentage points of pairwise ranking concordance, own-minus-stranger,
averaged first within a person-prompt instance over admissible strangers (so a prompt with 40
raters does not get 40x the weight of a prompt with 4), then across instances (equal weight per
instance; clustered inference below accounts for prompt and person correlation).

D_bar(b) > 0  means a person's own ratings out-predict a random co-rater's ratings of the SAME
shared criteria at reconstructing that person's own ranking -- i.e. the ratings carry
person-specific (individuating) information beyond what the criterion text + a generic rater
supplies. D_bar(b) <= 0 (or indistinguishable from the floor below) means they do not.

PRE-REGISTERED, BEFORE SEEING ANY OUTCOME NUMBER
--------------------------------------------------
K_MIN = 4 shared criteria.  Chosen from a FEASIBILITY pass over the mechanical coverage
distribution only (not the ranking-agreement outcome): median per-annotator coverage is 6/14
criteria, and 95.3% of random same-prompt annotator pairs already share >=4 criteria (97.7% share
>=3, 98.8% share >=2) -- so K_MIN=4 keeps the design honest (a real, non-trivial shared basket)
while discarding only ~5% of pairs to attrition.

ALPHA = 0.05, Holm-Bonferroni over the 3-test family: {D_bar(world) vs floor, D_bar(personal) vs
floor, D_bar(world) - D_bar(personal) vs 0}.  (The positive control and the placebo below are
validity/manipulation checks, not part of this hypothesis family.)

VERDICT RULE (fixed before running): "individuates" is CONFIRMED only if, for b=world (primary):
  (i)   the positive control passes (own-only agreement beats 0.5 chance, Holm-adjusted p<0.05)
  (ii)  D_bar(world)'s prompt-clustered AND person-clustered 95% CIs both exclude 0
  (iii) |D_bar(world)| exceeds the FLOOR (the stranger-vs-stranger spread, defined below) by the
        pre-registered margin of >= 1 floor-SD
If (i) fails, verdict is UNVERIFIED (the instrument itself carries no measurable signal, so the
own-vs-other question cannot be asked). If (i) passes but (ii) or (iii) fails, verdict is
OVERTURNED for individuation (own is not detectably better than a stranger).

POSITIVE CONTROL
-----------------
Own-only, unrestricted: does a person's own FULL rating vector (their whole S_P, no stranger
intersection) predict their own world ranking above chance? This is a scaled-down replay of the
release's own reported ~60% pairwise concordance and of this repo's established finding that
signed/flip-aware scoring beats chance (61% vs 39%) -- a case whose rough answer (>0.5, roughly
55-65%) is already known. If this fails, the satisfaction-tensor + signed-weighted-sum mechanism
carries no signal at all, and asking whether OWN beats OTHER is moot -- there is nothing for
"other" to lack.

PLACEBO (hand-derivable in advance)
-------------------------------------
A synthetic 2-criterion, 4-response toy is checked by assertion BEFORE the real data is touched:
criterion c0 has sat = (0.9, 0.1, 0.5, 0.5) for (A,B,C,D) and c1 has sat = (0.1, 0.9, 0.5, 0.5).
own = {c0:+10, c1:-10} (wants c0, dislikes c1) -> score = (0.9*10-0.1*10, 0.1*10-0.9*10, 0, 0) =
(8, -8, 0, 0) -> predicted order A > C=D > B.  other = {c0:-10, c1:+10} (the flipped, opposite
values) -> score = (-8, 8, 0, 0) -> predicted order B > C=D > A, the EXACT reverse on the decisive
A-vs-B pair. Against a hand-picked true ranking "A>B=C=D" (2 decisive pairs: A>B, A>C; C=D and B=C
undecided so excluded), own must score agree=1.0 (gets both A>B and A>C right) and other must
score agree=0.0 on the A>B pair, 0.5 on the tied A>C pair (since other's A and C scores tie at
-8 vs 0 -- wait, computed below exactly) -- the assertion recomputes this by hand in the script
and checks the code's own `score_vec`/`agreement` functions reproduce it exactly.

STRONGEST CONFOUND, WRITTEN BEFORE RUNNING
---------------------------------------------
SAME-SITTING CONSISTENCY (halo/anchoring): a person's ratings and their ranking are elicited in
the same session by the same person. Any "own beats stranger" gap could be pure within-session
consistency (a rater in an "A is great" mood rates A-favouring criteria higher AND ranks A higher)
rather than the criterion TEXT carrying real value content -- a person would out-predict a
stranger even if the criteria were semantic noise, purely because their own numbers are
internally consistent with their own mood that day.
CONTROL IN THE SAME SCRIPT: the dataset carries a SECOND, independent ranking block per person on
a subset of prompts -- "personal" ("what's best for you") vs "world" ("what's better in general").
Both come from the same sitting as the ratings, so this does not fully remove the confound, but if
it is PURE generic halo, the own-advantage should be statistically indistinguishable in size
between world and personal (halo does not care what the ranking question asked). If own-advantage
is reliably LARGER for personal (the explicitly self-interested question) than for world, that
differential is evidence of content beyond generic halo. This script reports both and the paired
world-vs-personal contrast, and states plainly in the final report that a full session-independent
control is not obtainable from this dataset.

FLOOR
-----
For each instance with >=2 admissible strangers, draw random PAIRS (Qa, Qb) of DISTINCT strangers
(both != P) from the admissible pool, restricted to the 3-way shared set I3 = S_P & S_Qa & S_Qb
(|I3| >= K_MIN, else the pair is skipped) and compute
    floor_diff = agree(Qa's ratings on I3) - agree(Qb's ratings on I3)
Both arms of a floor_diff are STRANGERS to P -- by construction there is no true "own" effect in
this quantity, so its spread is exactly "how much would the own-vs-other statistic move if you had
picked a different stranger to compare against, given zero true individuation" -- i.e. the
resampling-within-condition noise floor the task asks for. Up to 3 stranger-pairs per instance are
drawn per seed, across 5 seeds (8101 + 0..4), and the floor's stability across those seeds is
reported.

CLUSTERING
----------
A person appears on median 16 prompts (max 32); a prompt carries median 16 raters (max 46). Two
one-way cluster bootstraps (2000 resamples each, resample-with-replacement of prompt IDs / of
person IDs, keeping all of a resampled cluster's instances) are computed and the WIDER of the two
95% CIs is reported as the primary (conservative, standard practice when a joint two-way bootstrap
is not implemented).

DATA / COMPUTE
---------------
Everything needed (comparisons.jsonl, conversation_rubrics.jsonl, the precomputed a04_full.npz
satisfaction tensor) is already on disk; this script makes no GPU or LLM calls.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
_RES.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(_ROOT))

from covalx import load_join  # noqa: E402
from covalx.judge import parse_ranking  # noqa: E402

COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
SAT_NPZ = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
LABELS = ("A", "B", "C", "D")

SEED = 8101
SUBSEEDS = [SEED + k for k in range(5)]  # >=5 seeds, per the standard
K_MIN = 4
N_BOOT = 2000
FLOOR_PAIRS_PER_INSTANCE = 3
ALPHA = 0.05


# ===================================================================== utils
def decisive_pairs(groups: list[list[str]]) -> list[tuple[str, str]]:
    pairs = []
    for gi in range(len(groups)):
        for gj in range(gi + 1, len(groups)):
            for a in groups[gi]:
                for b in groups[gj]:
                    pairs.append((a, b))
    return pairs


def score_vec(rating: dict, crit_ids: list, sat: dict) -> dict:
    out = {lab: 0.0 for lab in LABELS}
    for c in crit_ids:
        w = rating.get(c)
        if w is None:
            continue
        for lab in LABELS:
            s = sat.get((c, lab))
            if s is not None:
                out[lab] += w * s
    return out


def agreement(scores: dict, pairs: list) -> float | None:
    if not pairs:
        return None
    correct = 0.0
    for a, b in pairs:
        sa, sb = scores[a], scores[b]
        if sa > sb:
            correct += 1.0
        elif sa == sb:
            correct += 0.5
    return correct / len(pairs)


def holm_bonferroni(pvals: dict, alpha: float = ALPHA) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out = {}
    running_max = 0.0
    for i, (k, p) in enumerate(items):
        adj = min(1.0, (m - i) * p)
        running_max = max(running_max, adj)
        out[k] = running_max
    return {k: (out[k], out[k] < alpha) for k in out}


def normal_p_two_sided(z: float) -> float:
    from math import erf, sqrt
    return 2.0 * (1.0 - 0.5 * (1.0 + erf(abs(z) / sqrt(2.0))))


# ===================================================================== placebo
def run_placebo() -> dict:
    crit_ids = [0, 1]
    sat = {
        (0, "A"): 0.9, (0, "B"): 0.1, (0, "C"): 0.5, (0, "D"): 0.5,
        (1, "A"): 0.1, (1, "B"): 0.9, (1, "C"): 0.5, (1, "D"): 0.5,
    }
    own = {0: 10.0, 1: -10.0}
    other = {0: -10.0, 1: 10.0}
    own_scores = score_vec(own, crit_ids, sat)
    other_scores = score_vec(other, crit_ids, sat)
    # hand computation:
    # own:   A = 0.9*10 + 0.1*-10 =  8 ; B = 0.1*10 + 0.9*-10 = -8 ; C = D = 0.5*10+0.5*-10 = 0
    # other: A = 0.9*-10 + 0.1*10 = -8 ; B = 0.1*-10 + 0.9*10 =  8 ; C = D = 0
    expect_own = {"A": 8.0, "B": -8.0, "C": 0.0, "D": 0.0}
    expect_other = {"A": -8.0, "B": 8.0, "C": 0.0, "D": 0.0}
    assert own_scores == expect_own, (own_scores, expect_own)
    assert other_scores == expect_other, (other_scores, expect_other)
    true_ranking = parse_ranking("A>B=C=D")
    pairs = decisive_pairs(true_ranking)
    # true_ranking groups: [[A],[B,C,D]] -> decisive pairs = (A,B),(A,C),(A,D)
    assert sorted(pairs) == sorted([("A", "B"), ("A", "C"), ("A", "D")]), pairs
    agree_own = agreement(own_scores, pairs)
    agree_other = agreement(other_scores, pairs)
    # own: A(8)>B(-8) correct; A(8)>C(0) correct; A(8)>D(0) correct -> 1.0
    # other: A(-8)>B(8)? no, wrong (0). A(-8)>C(0)? no, wrong (0). A(-8)>D(0)? no, wrong (0). -> 0.0
    assert agree_own == 1.0, agree_own
    assert agree_other == 0.0, agree_other
    return {
        "passed": True,
        "own_scores": own_scores, "other_scores": other_scores,
        "agree_own": agree_own, "agree_other": agree_other,
        "hand_derivation": "own=1.0 (all 3 decisive pairs correct), other=0.0 (all 3 wrong, "
                            "reversed by construction)",
    }


# ===================================================================== load
def build_sat_lookup(path: Path) -> dict:
    z = np.load(path, allow_pickle=True)
    d: dict = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        d[pid][(int(ci), lab)] = float(s)
    return d


def main() -> int:
    print("=== r134/independent_A: does a person's OWN ratings predict their OWN ranking "
          "better than a stranger's ratings of the same criteria do? ===")

    placebo = run_placebo()
    print(f"[placebo] passed={placebo['passed']}  own={placebo['agree_own']} "
          f"other={placebo['agree_other']}")

    sat_lookup = build_sat_lookup(SAT_NPZ)
    joined = load_join(COMPARISONS, RUBRICS)
    print(f"joined prompts: {len(joined)}")

    # ---- per-prompt structures -------------------------------------------------
    # crit_filter mirrors covalx's own tensor-build filter EXACTLY: keep coval_full
    # items with >=1 score, enumerate in file order, so `ci` lines up with the .npz.
    prompt_data = {}  # pid -> dict(crit_ids, ann_rating, world_blk, personal_blk)
    n_no_sat = 0
    for pid, comp, rub in joined:
        crits = [it for it in (rub.get("coval_full") or []) if it.get("scores")]
        crit_ids = list(range(len(crits)))
        ann_rating: dict = defaultdict(dict)
        for ci, it in enumerate(crits):
            for s in it["scores"]:
                ann_rating[s["annotator_id"]][ci] = float(s["score"])
        sat = sat_lookup.get(pid)
        if not sat:
            n_no_sat += 1
            continue
        asm_world, asm_personal = {}, {}
        for a in comp["metadata"]["assessments"]:
            aid = a["annotator_id"]
            wblk = (a.get("ranking_blocks") or {}).get("world") or []
            if wblk:
                asm_world[aid] = wblk[0].get("ranking", "")
            pblk = (a.get("ranking_blocks") or {}).get("personal") or []
            if pblk:
                asm_personal[aid] = pblk[0].get("ranking", "")
        prompt_data[pid] = dict(crit_ids=crit_ids, ann_rating=ann_rating,
                                 world=asm_world, personal=asm_personal, sat=sat)
    print(f"prompts with no satisfaction tensor entries: {n_no_sat}")

    # ---- positive control: own-only, unrestricted, both blocks ------------------
    pc = {}
    for block in ("world", "personal"):
        vals = []
        for pid, d in prompt_data.items():
            rankings = d[block]
            for aid, rstr in rankings.items():
                rating = d["ann_rating"].get(aid)
                if not rating:
                    continue
                groups = parse_ranking(rstr)
                pairs = decisive_pairs(groups)
                if not pairs:
                    continue
                sv = score_vec(rating, list(rating.keys()), d["sat"])
                ag = agreement(sv, pairs)
                if ag is not None:
                    vals.append(ag)
        vals = np.asarray(vals, dtype=np.float64)
        n = len(vals)
        mean = float(vals.mean()) if n else float("nan")
        se = float(vals.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
        z = (mean - 0.5) / se if se > 0 else float("nan")
        p = normal_p_two_sided(z) if se > 0 else float("nan")
        pc[block] = dict(n=n, mean_agreement=mean, se=se, z_vs_chance=z, p_two_sided=p,
                         ci95=[mean - 1.96 * se, mean + 1.96 * se])
        print(f"[positive control:{block}] n={n} mean_agree={mean:.4f} se={se:.4f} "
              f"z={z:.2f} p={p:.2e}")

    # ---- main computation: per (P,X,block) instance ------------------------------
    def compute_block(block: str, seeds: list[int]):
        instances = []  # dict per instance
        floor_vals_by_seed = {s: [] for s in seeds}
        rngs = {s: np.random.default_rng(s) for s in seeds}

        for pid, d in prompt_data.items():
            crit_ids = d["crit_ids"]
            rankings = d[block]
            ann_rating = d["ann_rating"]
            sat = d["sat"]
            # P-candidates: need BOTH ratings and the ranking block being predicted.
            people = [aid for aid in rankings if aid in ann_rating and ann_rating[aid]]
            # Q-candidates (strangers): need only RATINGS -- their own ranking (in any
            # block) is never used, so restricting this pool by ranking-block
            # availability would be an arbitrary, block-dependent shrinkage of the
            # "other" pool (this WAS a bug: it silently made the personal-block
            # stranger pool tiny and non-comparable to the world-block pool).
            raters_pool = [aid for aid in ann_rating if ann_rating[aid]]
            for p_aid in people:
                S_p = set(ann_rating[p_aid].keys())
                if not S_p:
                    continue
                groups = parse_ranking(rankings[p_aid])
                pairs = decisive_pairs(groups)
                if not pairs:
                    continue
                admissible = []
                for q_aid in raters_pool:
                    if q_aid == p_aid:
                        continue
                    S_q = set(ann_rating[q_aid].keys())
                    inter = S_p & S_q
                    if len(inter) >= K_MIN:
                        admissible.append((q_aid, inter))
                if not admissible:
                    continue

                diffs = []
                other_agrees = []
                for q_aid, inter in admissible:
                    I = list(inter)
                    own_sv = score_vec(ann_rating[p_aid], I, sat)
                    oth_sv = score_vec(ann_rating[q_aid], I, sat)
                    a_own = agreement(own_sv, pairs)
                    a_oth = agreement(oth_sv, pairs)
                    if a_own is None or a_oth is None:
                        continue
                    diffs.append(a_own - a_oth)
                    other_agrees.append(a_oth)
                if not diffs:
                    continue
                D_inst = float(np.mean(diffs))
                instances.append(dict(prompt_id=pid, annotator_id=p_aid, D=D_inst,
                                       n_admissible=len(diffs),
                                       own_beats_other_rate=float(np.mean(
                                           [1.0 if x > 0 else (0.5 if x == 0 else 0.0)
                                            for x in diffs]))))

                # floor: random stranger-vs-stranger pairs, 3-way intersection with S_p
                if len(admissible) >= 2:
                    for s in seeds:
                        rng = rngs[s]
                        m = len(admissible)
                        n_draw = min(FLOOR_PAIRS_PER_INSTANCE, m * (m - 1) // 2)
                        tried = set()
                        attempts = 0
                        draws = 0
                        while draws < n_draw and attempts < n_draw * 8:
                            attempts += 1
                            ia, ib = rng.choice(m, size=2, replace=False)
                            key = (min(ia, ib), max(ia, ib))
                            if key in tried:
                                continue
                            tried.add(key)
                            qa_aid, inter_a = admissible[ia]
                            qb_aid, inter_b = admissible[ib]
                            I3 = list(S_p & inter_a & inter_b)
                            if len(I3) < K_MIN:
                                continue
                            sv_a = score_vec(ann_rating[qa_aid], I3, sat)
                            sv_b = score_vec(ann_rating[qb_aid], I3, sat)
                            ag_a = agreement(sv_a, pairs)
                            ag_b = agreement(sv_b, pairs)
                            if ag_a is None or ag_b is None:
                                continue
                            floor_vals_by_seed[s].append(ag_a - ag_b)
                            draws += 1
        return instances, floor_vals_by_seed

    results_by_block = {}
    instances_by_block = {}
    for block in ("world", "personal"):
        instances, floor_by_seed = compute_block(block, SUBSEEDS)
        instances_by_block[block] = instances
        n_inst = len(instances)
        D_vals = np.array([r["D"] for r in instances], dtype=np.float64)
        headline = float(D_vals.mean()) if n_inst else float("nan")
        headline_sd = float(D_vals.std(ddof=1)) if n_inst > 1 else float("nan")
        win_rate = float(np.mean([r["own_beats_other_rate"] for r in instances])) if n_inst else float("nan")

        # cluster bootstrap, prompt and person
        by_prompt: dict = defaultdict(list)
        by_person: dict = defaultdict(list)
        for i, r in enumerate(instances):
            by_prompt[r["prompt_id"]].append(D_vals[i])
            by_person[r["annotator_id"]].append(D_vals[i])
        by_prompt = {k: np.array(v) for k, v in by_prompt.items()}
        by_person = {k: np.array(v) for k, v in by_person.items()}

        def cluster_boot(groups: dict, seed: int, n_boot: int = N_BOOT):
            rng = np.random.default_rng(seed)
            keys = list(groups.keys())
            k = len(keys)
            if k == 0:
                return dict(mean=float("nan"), ci95=[float("nan"), float("nan")], se=float("nan"))
            means = np.empty(n_boot)
            arrs = [groups[key] for key in keys]
            for b in range(n_boot):
                idx = rng.integers(0, k, size=k)
                pooled = np.concatenate([arrs[i] for i in idx])
                means[b] = pooled.mean()
            lo, hi = np.percentile(means, [2.5, 97.5])
            return dict(mean=float(means.mean()), ci95=[float(lo), float(hi)],
                        se=float(means.std(ddof=1)), n_clusters=k)

        boot_prompt_by_seed = [cluster_boot(by_prompt, s) for s in SUBSEEDS]
        boot_person_by_seed = [cluster_boot(by_person, s) for s in SUBSEEDS]
        # headline seed = first sub-seed (8101), stability = spread across all 5
        boot_prompt = boot_prompt_by_seed[0]
        boot_person = boot_person_by_seed[0]
        prompt_ci_width = boot_prompt["ci95"][1] - boot_prompt["ci95"][0] if n_inst else float("nan")
        person_ci_width = boot_person["ci95"][1] - boot_person["ci95"][0] if n_inst else float("nan")
        wider = "person" if (person_ci_width or 0) >= (prompt_ci_width or 0) else "prompt"
        primary_ci = boot_person["ci95"] if wider == "person" else boot_prompt["ci95"]

        # floor, pooled across seeds
        floor_all = np.concatenate([np.array(v) for v in floor_by_seed.values() if v]) \
            if any(floor_by_seed.values()) else np.array([])
        floor_stats = dict(
            n=int(floor_all.size),
            mean=float(floor_all.mean()) if floor_all.size else float("nan"),
            sd=float(floor_all.std(ddof=1)) if floor_all.size > 1 else float("nan"),
            abs_mean=float(np.mean(np.abs(floor_all))) if floor_all.size else float("nan"),
            p95_abs=float(np.percentile(np.abs(floor_all), 95)) if floor_all.size else float("nan"),
            per_seed_mean=[float(np.mean(v)) if v else float("nan") for v in floor_by_seed.values()],
            per_seed_sd=[float(np.std(v, ddof=1)) if len(v) > 1 else float("nan")
                         for v in floor_by_seed.values()],
        )
        floor_p = None
        if floor_all.size and not np.isnan(headline):
            floor_p = float(np.mean(np.abs(floor_all) >= abs(headline)))

        clears_floor = (not np.isnan(headline) and floor_stats["sd"] > 0
                         and abs(headline) >= floor_stats["sd"])

        results_by_block[block] = dict(
            n_instances=n_inst,
            headline_D=headline,
            headline_sd_across_instances=headline_sd,
            own_beats_other_win_rate=win_rate,
            cluster_bootstrap_prompt=boot_prompt,
            cluster_bootstrap_person=boot_person,
            cluster_bootstrap_prompt_seed_spread=boot_prompt_by_seed,
            cluster_bootstrap_person_seed_spread=boot_person_by_seed,
            primary_ci_source=wider,
            primary_ci95=primary_ci,
            floor=floor_stats,
            floor_empirical_p=floor_p,
            clears_floor_by_1sd=bool(clears_floor),
            standardized_effect_vs_floor_sd=(headline / floor_stats["sd"]
                                              if floor_stats["sd"] and floor_stats["sd"] > 0
                                              else None),
        )
        print(f"[{block}] n_inst={n_inst} D_bar={headline:.4f} "
              f"prompt_ci95={boot_prompt['ci95']} person_ci95={boot_person['ci95']} "
              f"floor_sd={floor_stats['sd']:.4f} floor_p={floor_p}")

    # ---- world vs personal paired contrast (same-sitting confound probe) --------
    # restrict to instances that exist in BOTH blocks (same P, same X); reuse the
    # instances already computed above -- no recomputation.
    world_map = {(r["prompt_id"], r["annotator_id"]): r["D"] for r in instances_by_block["world"]}
    personal_map = {(r["prompt_id"], r["annotator_id"]): r["D"] for r in instances_by_block["personal"]}
    common_keys = sorted(set(world_map) & set(personal_map))
    paired_diff = np.array([personal_map[k] - world_map[k] for k in common_keys])
    n_common = len(paired_diff)
    if n_common > 1:
        rng = np.random.default_rng(SEED)
        boot_means = np.empty(N_BOOT)
        for b in range(N_BOOT):
            idx = rng.integers(0, n_common, size=n_common)
            boot_means[b] = paired_diff[idx].mean()
        wvp_mean = float(paired_diff.mean())
        wvp_ci = [float(x) for x in np.percentile(boot_means, [2.5, 97.5])]
        wvp_se = float(paired_diff.std(ddof=1) / np.sqrt(n_common))
        wvp_z = wvp_mean / wvp_se if wvp_se > 0 else float("nan")
        wvp_p = normal_p_two_sided(wvp_z) if wvp_se > 0 else float("nan")
    else:
        wvp_mean = wvp_se = wvp_z = wvp_p = float("nan")
        wvp_ci = [float("nan"), float("nan")]
    world_vs_personal = dict(
        n_common_instances=n_common,
        mean_personal_minus_world=wvp_mean,
        ci95=wvp_ci, se=wvp_se, z=wvp_z, p_two_sided=wvp_p,
        interpretation=("personal-D > world-D would indicate content beyond generic same-session "
                         "halo (halo should hit both blocks equally); personal-D ~= world-D is "
                         "consistent with (does not prove) generic halo"),
    )
    print(f"[world-vs-personal paired] n={n_common} mean(personal-world)={wvp_mean:.4f} "
          f"ci95={wvp_ci} p={wvp_p}")

    # ---- multiplicity: Holm-Bonferroni over the 3-test family --------------------
    def z_and_p_from_headline(block_res):
        # use the wider (primary) CI's implied SE for a conservative p-value
        lo, hi = block_res["primary_ci95"]
        if any(np.isnan(x) for x in (lo, hi)):
            return float("nan"), float("nan")
        se = (hi - lo) / (2 * 1.96)
        z = block_res["headline_D"] / se if se > 0 else float("nan")
        p = normal_p_two_sided(z) if se > 0 else float("nan")
        return z, p

    z_world, p_world = z_and_p_from_headline(results_by_block["world"])
    z_personal, p_personal = z_and_p_from_headline(results_by_block["personal"])
    family_p = {"world_D_vs_0": p_world, "personal_D_vs_0": p_personal,
                "world_vs_personal": wvp_p}
    holm = holm_bonferroni({k: v for k, v in family_p.items() if not np.isnan(v)})

    # ---- verdict -------------------------------------------------------------
    pc_world_pass = pc["world"]["p_two_sided"] < ALPHA and pc["world"]["mean_agreement"] > 0.5
    world_res = results_by_block["world"]
    ci_excludes_zero_prompt = (world_res["cluster_bootstrap_prompt"]["ci95"][0] > 0
                                or world_res["cluster_bootstrap_prompt"]["ci95"][1] < 0)
    ci_excludes_zero_person = (world_res["cluster_bootstrap_person"]["ci95"][0] > 0
                                or world_res["cluster_bootstrap_person"]["ci95"][1] < 0)
    clears_floor = world_res["clears_floor_by_1sd"]
    holm_world_sig = holm.get("world_D_vs_0", (None, False))[1]

    if not pc_world_pass:
        verdict = "UNVERIFIED"
        verdict_reason = ("positive control failed: own-ratings-weighted score does not beat "
                           "chance at predicting the person's own world ranking, so the "
                           "instrument carries no measurable signal and the own-vs-other "
                           "question cannot be asked with it.")
    elif ci_excludes_zero_prompt and ci_excludes_zero_person and clears_floor and holm_world_sig:
        verdict = "CONFIRMED" if world_res["headline_D"] > 0 else "OVERTURNED"
        verdict_reason = ("own ratings individuate: the own-vs-stranger gap is nonzero under "
                           "both clustering schemes, clears the stranger-vs-stranger floor by "
                           ">=1 floor-SD, and survives Holm-Bonferroni correction.") \
            if world_res["headline_D"] > 0 else \
            ("own ratings show a reliable NEGATIVE gap vs strangers -- own ratings predict the "
             "person's own ranking WORSE than a stranger's do; individuation is overturned in "
             "the opposite direction from the one hypothesized.")
    else:
        verdict = "OVERTURNED"
        reasons = []
        if not (ci_excludes_zero_prompt and ci_excludes_zero_person):
            reasons.append("95% CI (prompt- and/or person-clustered) includes 0")
        if not clears_floor:
            reasons.append("|D_bar| does not clear the stranger-vs-stranger floor by 1 SD")
        if not holm_world_sig:
            reasons.append("does not survive Holm-Bonferroni correction across the 3-test family")
        verdict_reason = "own ratings do not individuate at the pre-registered bar: " + "; ".join(reasons)

    out = dict(
        seed=SEED, subseeds=SUBSEEDS, k_min=K_MIN, alpha=ALPHA, n_boot=N_BOOT,
        floor_pairs_per_instance=FLOOR_PAIRS_PER_INSTANCE,
        estimand="mean over (person,prompt) instances of [pairwise-concordance(own ratings, "
                 "restricted to criteria shared with a stranger) minus pairwise-concordance"
                 "(stranger ratings, same criteria)] against the person's own true ranking; "
                 "unit = percentage points of pairwise ranking concordance",
        placebo=placebo,
        positive_control=pc,
        results_by_block=results_by_block,
        world_vs_personal=world_vs_personal,
        multiplicity=dict(family_raw_p=family_p, holm_bonferroni=holm),
        dataset_coverage=dict(
            n_prompts_joined=len(joined),
            n_prompts_with_satisfaction=len(prompt_data),
            n_prompts_missing_satisfaction=n_no_sat,
        ),
        verdict=verdict,
        verdict_reason=verdict_reason,
    )

    out_path = _RES / "independent_A.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=lambda o: None if isinstance(o, float) and np.isnan(o) else o)
    print(f"wrote {out_path}")
    print(f"VERDICT: {verdict} -- {verdict_reason}")

    if world_res["n_instances"] == 0 or pc["world"]["n"] == 0:
        print("FATAL: no usable instances -- data cannot support the question")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
