"""r60 -- when a person's WORLD ordering contradicts their own PERSONAL one, which does the rubric follow?

CLAIM CARD
----------
Claim      the rubric measures a shared normative standard rather than personal taste.
Estimand   on the pairs where a single participant's world ordering and personal
           ordering are REVERSED, the fraction on which the rubric-induced
           ordering sides with world. Chance is exactly 1/2 by construction --
           the two orderings make opposite predictions on every such pair, so the
           rubric must pick a side.
Target
observed?  FULLY. Both orderings are released, from the same person, about the
           same four responses, with no generated text and no proxy anywhere. Of
           every estimand in this project this is the only one whose target is
           human data on both arms.
Alternative
worlds     N NORMATIVE       rubric sides with world above 1/2 -- it encodes the
                             impartial standard participants were asked for, and
                             "values rubric" is apt.
           P PREFERENCE      sides with personal above 1/2 -- it tracks taste and
                             the normative framing is decoration.
           I INDISTINGUISHABLE  equivalent to 1/2 at delta=0.01 -- the rubric has
                             no purchase on the distinction, which would mean the
                             choice of ranking block (entry 88) does not matter
                             for anything measured so far.
Intervention
           none. Observational, paired WITHIN person: the same participant
           supplies both orderings, so population, prompt, response set and
           rubric are all held fixed by construction.
Null       1/2, and it is exact rather than estimated. Plus a rubric-shuffle arm:
           permuting the four response scores within a prompt must return 1/2.
Stopping   this is a single pass over persisted data. No sweep, no follow-up
           conditional on the result.

WHY THIS EXISTS
---------------
Entry 88: every number in this project is measured against `ranking_blocks["world"]`
and no document said so. The personal ordering is present for 26.7% of
assessments and had never been used. Where both exist they disagree often --
identical in only 53.2% of cases, top choice differing in 29.0%, and 9.70% of
strict world pairs reversed in personal -- so the distinction is not cosmetic.

NO GPU. r41's persisted satisfaction tensor already covers the original four
responses for 250 prompts under the released core criteria, and its reproduction
control matched all 1,500 of r12's per-prompt values exactly.

SCOPE THIS DOES NOT REACH
-------------------------
Equal weights over CoVal-core, judge-scored satisfaction. The rubric-induced
ordering is the judge's, so a null here is "this judge, on these criteria, cannot
tell the orderings apart" -- not "rubrics cannot". And the reversed-pair subset is
selected: it is by definition the pairs where the participant was ambivalent
enough to order them differently under two framings.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
from covalx.judge import parse_ranking  # noqa: E402

TENSOR = _ROOT / "rounds/05_human_protocol_and_power/r41_criterion_support/results/r41_satisfaction_qwen2b.npz"
R41 = _ROOT / "rounds/05_human_protocol_and_power/r41_criterion_support/results/r41_criterion_support.json"
LABELS = ["A", "B", "C", "D"]


def strict_pairs(rk):
    """Strict pairwise preferences, ties dropped -- covalx.human_pairs' rule."""
    f = {lab: gi for gi, grp in enumerate(rk) for lab in grp}
    out = set()
    labs = list(f)
    for i, a in enumerate(labs):
        for b in labs[i + 1:]:
            if f[a] < f[b]:
                out.add((a, b))
            elif f[b] < f[a]:
                out.add((b, a))
    return out


def side(scores: dict, a: str, b: str):
    """Which of a,b does the rubric rank higher? None if it cannot separate them."""
    if a not in scores or b not in scores:
        return None
    if scores[a] == scores[b]:
        return None
    return a if scores[a] > scores[b] else b


def collect(rng, shuffle=False):
    d = np.load(TENSOR)
    Z, off = d["z_orig_real"], d["off_real"].astype(int)
    pids = json.loads(R41.read_text())["per_prompt"]["pids"]
    by_pid = {}
    for k, pid in enumerate(pids):
        blk = Z[off[k]:off[k + 1]]
        if blk.shape[0] == 0:
            continue
        s = blk.mean(axis=0)
        if shuffle:
            s = rng.permutation(s)
        by_pid[pid] = {LABELS[i]: float(s[i]) for i in range(min(4, len(s)))}

    world_side = personal_side = unresolved = 0
    n_asm = n_rev = 0
    per_prompt = {}
    for line in open(_ROOT / "data/comparisons.jsonl"):
        rec = json.loads(line)
        pid = rec.get("prompt_id")
        if pid not in by_pid:
            continue
        sc = by_pid[pid]
        for asm in (rec.get("metadata") or {}).get("assessments") or []:
            rb = asm.get("ranking_blocks") or {}
            w, p = rb.get("world") or [], rb.get("personal") or []
            if not w or not p:
                continue
            rw, rp = parse_ranking(w[0].get("ranking", "")), parse_ranking(p[0].get("ranking", ""))
            if not rw or not rp:
                continue
            n_asm += 1
            pw, pp = strict_pairs(rw), strict_pairs(rp)
            for (a, b) in pw:
                if (b, a) not in pp:            # not a contradiction -- uninformative
                    continue
                n_rev += 1
                s = side(sc, a, b)
                if s is None:
                    unresolved += 1
                elif s == a:
                    world_side += 1
                    per_prompt.setdefault(pid, []).append(1)
                else:
                    personal_side += 1
                    per_prompt.setdefault(pid, []).append(0)
    return dict(world=world_side, personal=personal_side, unresolved=unresolved,
                n_assessments=n_asm, n_reversed=n_rev, per_prompt=per_prompt)


def boot_ci(per_prompt, rng, boot):
    """Cluster bootstrap on PROMPT -- pairs within a prompt share a rubric."""
    keys = list(per_prompt)
    if not keys:
        return [float("nan"), float("nan")]
    out = []
    for _ in range(boot):
        pick = rng.integers(0, len(keys), len(keys))
        vals = [v for i in pick for v in per_prompt[keys[i]]]
        out.append(float(np.mean(vals)) if vals else np.nan)
    return [float(np.nanpercentile(out, 2.5)), float(np.nanpercentile(out, 97.5))]


def positive_control():
    """A 'rubric' that IS one ordering must side with it every time."""
    sc_w = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0}
    ok_w = side(sc_w, "A", "B") == "A"
    ok_p = side({"A": 1.0, "B": 2.0}, "A", "B") == "B"
    tie = side({"A": 1.0, "B": 1.0}, "A", "B") is None
    return {"prefers_higher_score": ok_w, "prefers_other_when_lower": ok_p,
            "tie_returns_none": tie, "all_pass": bool(ok_w and ok_p and tie)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=8000)
    ap.add_argument("--out", type=Path, default=_RES / "r60_world_vs_personal.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        a.boot = 200
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20260728)

    pc = positive_control()
    print(f"positive control: {'PASS' if pc['all_pass'] else 'FAIL'}  {pc}")
    if not pc["all_pass"]:
        raise SystemExit("REFUSING: the side() rule cannot order known scores.")

    real = collect(rng)
    shuf = collect(np.random.default_rng(4242), shuffle=True)
    if real["n_reversed"] == 0:
        raise SystemExit("REFUSING: no reversed pairs. An empty population has not passed.")

    resolved = real["world"] + real["personal"]
    share = real["world"] / resolved if resolved else float("nan")
    ci = boot_ci(real["per_prompt"], rng, a.boot)
    s_res = shuf["world"] + shuf["personal"]
    s_share = shuf["world"] / s_res if s_res else float("nan")
    s_ci = boot_ci(shuf["per_prompt"], np.random.default_rng(99), a.boot)

    DELTA = 0.01
    equivalent = bool(ci[0] > 0.5 - DELTA and ci[1] < 0.5 + DELTA)

    # Can this question be answered from this release AT ALL, at this margin?
    # Half-width scales as 1/sqrt(n), so the pairs needed to reach +-DELTA follow
    # from the pairs in hand. Reported whatever the outcome, because an
    # INCONCLUSIVE result whose required n exceeds the whole release is a
    # statement about the DATA, not about the rubric -- and that is the useful
    # thing to publish.
    half = (ci[1] - ci[0]) / 2
    need = int(round(resolved * (half / DELTA) ** 2)) if half > 0 else 0
    RELEASE_REVERSED = 2444   # all 18,384 assessments, measured before this round
    answerable = need <= RELEASE_REVERSED
    # And the useful inverse: what margin IS reachable if every reversed pair
    # in the release were used? Reporting only "not answerable at 0.01" would
    # leave a reader unable to tell whether the shortfall is 10% or 10x.
    reachable = half * (resolved / RELEASE_REVERSED) ** 0.5 if RELEASE_REVERSED else float("nan")
    significant = bool(ci[0] > 0.5 or ci[1] < 0.5)
    world_name = ("N NORMATIVE" if significant and share > 0.5 else
                  "P PREFERENCE" if significant and share < 0.5 else
                  "I INDISTINGUISHABLE" if equivalent else "INCONCLUSIVE")

    verdict = (
        f"{world_name}. On the {resolved:,} pairs where a participant's WORLD ordering and their own "
        f"PERSONAL ordering are REVERSED -- the only pairs on which the two make opposite predictions "
        f"-- the rubric-induced ordering sides with WORLD on {share:.4f} of them "
        f"[{ci[0]:.4f}, {ci[1]:.4f}], against an exact chance value of 0.5. Shuffling the four "
        f"response scores within each prompt gives {s_share:.4f} [{s_ci[0]:.4f}, {s_ci[1]:.4f}]. "
        f"{real['unresolved']:,} reversed pairs were unresolvable because the rubric scored the two "
        f"responses identically and are excluded from the denominator, not counted as either side. "
        f"Drawn from {real['n_assessments']:,} assessments carrying both orderings across 250 "
        f"prompts, paired WITHIN person so population, prompt, response set and rubric are held "
        f"fixed by construction. This is the only estimand in this project whose target is human "
        f"data on BOTH arms. SCOPE: equal weights over CoVal-core with judge-scored satisfaction, so "
        f"a null reads 'this judge on these criteria cannot tell the orderings apart', not 'rubrics "
        f"cannot'; and the reversed-pair subset is by definition the pairs where the participant "
        f"ordered differently under two framings. "
        f"POWER: the observed 95% half-width is {half:.4f}, so resolving delta={DELTA} would need "
        f"about {need:,} reversed pairs. The ENTIRE release contains {RELEASE_REVERSED:,}, so this "
        f"question is {'answerable' if answerable else 'NOT ANSWERABLE'} from CoVal at this margin "
        f"even using every assessment in it -- which makes an inconclusive reading here a fact about "
        f"the DATA rather than about the rubric. Using EVERY reversed pair in the release would reach "
        f"a half-width of about {reachable:.4f}, so the answerable margin is roughly "
        f"delta={reachable:.3f} -- {RELEASE_REVERSED/need:.2f}x the data needed for 0.01."
    )

    doc = {
        "n_assessments_with_both": real["n_assessments"],
        "n_reversed_pairs": real["n_reversed"],
        "n_resolved": resolved,
        "n_unresolved_rubric_tie": real["unresolved"],
        "sides_with_world": real["world"],
        "sides_with_personal": real["personal"],
        "world_share": share,
        "world_share_ci95_cluster_bootstrap_on_prompt": ci,
        "shuffled_rubric_world_share": s_share,
        "shuffled_rubric_ci95": s_ci,
        "chance": 0.5,
        "delta": DELTA,
        "significant": significant,
        "equivalent_at_delta": equivalent,
        "world": world_name,
        "ci95_half_width": None,
        "reversed_pairs_needed_for_delta": None,
        "reversed_pairs_in_entire_release": RELEASE_REVERSED,
        "answerable_from_this_release_at_delta": None,
        "reachable_half_width_using_whole_release": None,
        "positive_control": pc,
        # ⚠ POPULATION FACT ADDED 2026-07-29 (entry 156). This round can only ever
        # run on assessments carrying BOTH a world and a personal ranking, and
        # that is not a random subset of the release: `personal` is present on
        # 4,901 of 18,384 assessments (26.66%) and on NONE past a rater's fifth
        # task -- positions 1-4 complete, position 5 partial (887 of 990), zero
        # from 6 onward. The same 4,901 carry the `unacceptable` block, so the
        # release has a LONG form for early tasks and a SHORT form after.
        #
        # So the world-versus-personal question is structurally confined to a
        # rater's EARLIEST tasks, which are also the only tasks carrying the
        # safety priming of the unacceptable-content check. The shortage this
        # round reports is therefore not merely a sample-size problem: more of
        # this release cannot supply the missing pairs, because the question was
        # not asked after task five.
        "personal_block_coverage": {
            "assessments_with_personal": 4901, "assessments_total": 18384,
            "share": 4901 / 18384, "present_at_positions": "1-4 complete, 5 partial, 0 from 6",
            "same_assessments_as_unacceptable_block": True,
            # STRONGER THAN A SHARE (entry 158): the forms cover DISJOINT PROMPTS.
            # 1,078 prompts partition into 321 long-form and 757 short-form with
            # intersection zero. So the personal ranking does not exist for 757
            # prompts at all -- not sparsely, not at all -- and no prompt has data
            # under both instruments.
            "prompts_long_form": 321, "prompts_short_form": 757,
            "prompts_total": 1078, "prompt_set_intersection": 0},
        "scope": ("POPULATION: the personal ranking exists for 321 of the release's 1,078 prompts "
                  "and for NONE of the other 757 -- the long-form and short-form prompt sets are "
                  "DISJOINT, intersection zero. It is also confined to a rater's first ~5 tasks and "
                  "to the same assessments carrying the unacceptable-content check, so form, task "
                  "position and prompt identity are all three perfectly confounded. This contrast "
                  "cannot be extended by collecting more of this release, and cannot be compared "
                  "across forms because no prompt appears under both. "
                  "Equal weights over CoVal-core, judge-scored satisfaction (r41's persisted tensor, "
                  "reproduction control 1500/1500 exact). The rubric-induced ordering is the "
                  "JUDGE's, so a null is a statement about this judge on these criteria. The "
                  "reversed-pair subset is selected by construction: it is the pairs a participant "
                  "ordered one way for themselves and the other way for the world."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    doc["ci95_half_width"] = half
    doc["reversed_pairs_needed_for_delta"] = need
    doc["answerable_from_this_release_at_delta"] = bool(answerable)
    doc["reachable_half_width_using_whole_release"] = float(reachable)
    a.out.write_text(json.dumps(doc, indent=1))

    print(f"\nassessments with both orderings : {real['n_assessments']:,}")
    print(f"reversed pairs                  : {real['n_reversed']:,}")
    print(f"  resolved by the rubric        : {resolved:,}   (ties excluded: {real['unresolved']:,})")
    print(f"  sides with WORLD              : {real['world']:,}")
    print(f"  sides with PERSONAL           : {real['personal']:,}")
    print(f"\n  world share {share:.4f}  {ci}   chance = 0.5")
    print(f"  shuffled    {s_share:.4f}  {s_ci}")
    print(f"\n  half-width {half:.4f} -> need ~{need:,} reversed pairs for delta=0.01;"
          f" the whole release has {RELEASE_REVERSED:,}"
          f"  => {'answerable' if answerable else 'NOT ANSWERABLE'}")
    print(f"\n  WORLD: {world_name}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
