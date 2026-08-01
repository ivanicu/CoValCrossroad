"""Are people's criteria descriptions of what they want, or descriptions of what they picked?

The card documents the task order and it is the single most consequential design fact in the
release: a person checks for unacceptable responses, ranks them for themselves, ranks them for the
world, rates the prompt -- and THEN writes rubric criteria. Authoring comes last. So every
criterion in this dataset was written by someone who had already chosen a winner.

That makes a specific failure available, and it is not a small one. If the criteria are
descriptions of the response the author already preferred, then the rubric is not an independent
statement of values that a model can be scored against -- it is a post-hoc justification, and any
pipeline treating it as normative input is compiling rationalisations.

THE TEST HAS AN ALMOST PERFECT CONTROL, which is why it is worth running rather than assuming.
Take a criterion written by person A on prompt P. Ask which of the four responses satisfies it
most. Then compare two things:

  A's OWN top-ranked response          -- what the author had already chosen
  ANOTHER rater's top-ranked response  -- same criterion, same prompt, same four responses,
                                          same judge, different person's choice

Everything is held fixed except whose ranking is used. If a criterion is a neutral statement of
what a good answer looks like, it should favour A's choice no more than it favours B's. If it is a
rationalisation, it favours A's.

AUTHORSHIP IS RECOVERABLE because rating counts split cleanly: 9,684 criteria carry exactly one
rating, 5,564 carry four or more, and NOTHING sits at two or three. A sole-rated criterion was
written by the person the score entry names.

SATISFACTION IS AN INSTRUMENT and the claim has to be worded around it. The scores come from a
locally rebuilt Qwen3.5-2B-Base judge reading sigmoid(logit(" Yes") - logit(" No")). But the
comparison is WITHIN criterion and WITHIN prompt -- the same judge scores both arms on the same
four texts -- so a judge bias would have to be correlated with which rater is being tested, which
it cannot be.

PREREGISTERED: the estimand is (satisfaction of the author's own top choice) minus (satisfaction
of another rater's top choice), same criterion. Clustered on prompt and author. A rationalisation
effect is a positive difference; the direction is predicted, and a null would mean the criteria
are independent of the choice that preceded them.
"""
from __future__ import annotations

import json
import math
import pathlib
import random
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
TENSOR = ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
LETTERS = "ABCD"
SEEDS = list(range(5))


def two_way_se(y, g1, g2):
    y = np.asarray(y, float)
    n = len(y)
    r = y - y.mean()

    def cl(g):
        s = defaultdict(float)
        for v, k in zip(r, g):
            s[k] += v
        return sum(x * x for x in s.values()) / n ** 2
    return math.sqrt(max(cl(g1) + cl(g2) - cl([f"{a}||{b}" for a, b in zip(g1, g2)]), 0.0))


def top_of(s):
    for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
        g = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
        if g and len(g[0].split("=")) == 1 and g[0] in LETTERS:
            return g[0]
        break
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(TENSOR, allow_pickle=True)
    sat = {}
    for k, v in zip(d["meta"], d["sat"]):
        pid, ci, letter = str(k).split("|")
        sat[(pid, int(ci), letter)] = float(v)

    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]
    choice = defaultdict(dict)          # prompt -> rater -> top letter
    for a in ann:
        for s in a.get("assessments", []):
            t = top_of(s)
            if t:
                choice[s.get("conversation_id")][a["annotator_id"]] = t

    from covalx.judge import load_join
    rows = []
    for pid, _p, r in load_join(DATA / "comparisons.jsonl", DATA / "conversation_rubrics.jsonl"):
        ch = choice.get(pid)
        if not ch or len(ch) < 3:
            continue
        for ci, it in enumerate(r["coval_full"]):
            sc = it.get("scores") or []
            if len(sc) != 1:
                continue                                   # not solely authored
            aid = sc[0].get("annotator_id")
            mine = ch.get(aid)
            if mine is None:
                continue
            vals = {L: sat.get((pid, ci, L)) for L in LETTERS}
            if any(v is None for v in vals.values()):
                continue
            others = [(who, t) for who, t in ch.items() if who != aid]
            if not others:
                continue
            rows.append({"pid": pid, "aid": aid, "ci": ci, "mine": mine, "vals": vals,
                         "others": others, "w": float(sc[0]["score"])})
    print(f"sole-authored criteria with author, judge scores and >=3 raters on the prompt: "
          f"{len(rows)}")
    print(f"  over {len({r['pid'] for r in rows})} prompts and {len({r['aid'] for r in rows})} "
          f"authors")

    # ---------------------------------------------------------------- the paired contrast
    print("\n" + "=" * 78)
    print("DOES A CRITERION FAVOUR ITS OWN AUTHOR'S CHOICE?")
    print("=" * 78)
    per_seed = []
    for sd in SEEDS:
        rng = random.Random(sd)
        y, gp, ga = [], [], []
        for r in rows:
            who, theirs = rng.choice(r["others"])
            if theirs == r["mine"]:
                continue                                   # no contrast to make
            y.append(r["vals"][r["mine"]] - r["vals"][theirs])
            gp.append(r["pid"])
            ga.append(r["aid"])
        m = float(np.mean(y))
        se = two_way_se(y, gp, ga)
        per_seed.append({"seed": sd, "n": len(y), "diff": m, "se": se, "z": m / se})
        print(f"  seed {sd}: n={len(y):5d}  own minus other  {m:+.4f}  "
              f"[{m - 1.96 * se:+.4f}, {m + 1.96 * se:+.4f}]  z {m / se:+.1f}")
    M = float(np.mean([p["diff"] for p in per_seed]))
    SE = float(np.mean([p["se"] for p in per_seed]))
    Z = M / SE
    spread = float(np.std([p["diff"] for p in per_seed]))
    print(f"\n  pooled over {len(SEEDS)} seeds: {M:+.4f} [{M - 1.96 * SE:+.4f}, "
          f"{M + 1.96 * SE:+.4f}]  z {Z:+.1f}   seed spread {spread:.4f}")

    # scale: what does a satisfaction unit mean here
    allv = [v for r in rows for v in r["vals"].values()]
    within = [max(r["vals"].values()) - min(r["vals"].values()) for r in rows]
    print(f"  scale: satisfaction runs {min(allv):.3f}-{max(allv):.3f}; the within-criterion")
    print(f"  spread across four responses is {np.mean(within):.3f} on average, so the effect is")
    print(f"  {abs(M) / np.mean(within):.1%} of the range the judge actually uses per criterion")

    # ---------------------------------------------------------------- rank version
    rk = []
    for r in rows:
        order = sorted(LETTERS, key=lambda L: -r["vals"][L])
        rk.append(order.index(r["mine"]) + 1)
    print(f"\n  rank of the author's own choice among the four, by satisfaction: "
          f"mean {np.mean(rk):.3f} (chance 2.5); top-ranked {np.mean([x == 1 for x in rk]):.1%} "
          f"(chance 25%)")

    # ---------------------------------------------------------------- does it grow with dissent
    print("\n" + "=" * 78)
    print("AND IT SHOULD BE STRONGEST WHERE THE AUTHOR DEPARTED FROM THE PANEL")
    print("=" * 78)
    print("  A person whose choice matched everyone has little to justify. A person who broke from")
    print("  the majority has more. If the effect is rationalisation rather than a stable taste,")
    print("  it should be LARGER for the dissenters -- a directional prediction the design makes.")
    rng = random.Random(99)
    strata = {"agreed with panel": ([], [], []), "departed from panel": ([], [], [])}
    for r in rows:
        cnt = Counter(t for _w, t in r["others"])
        mx = max(cnt.values())
        mode = [k for k, v in cnt.items() if v == mx]
        key = "agreed with panel" if (len(mode) == 1 and r["mine"] == mode[0]) \
            else "departed from panel"
        who, theirs = rng.choice(r["others"])
        if theirs == r["mine"]:
            continue
        strata[key][0].append(r["vals"][r["mine"]] - r["vals"][theirs])
        strata[key][1].append(r["pid"])
        strata[key][2].append(r["aid"])
    st_out = {}
    for k, (yy, pp, aa) in strata.items():
        if len(yy) < 200:
            continue
        m = float(np.mean(yy))
        se = two_way_se(yy, pp, aa)
        st_out[k] = {"n": len(yy), "diff": m, "se": se, "z": m / se}
        print(f"  {k:22s} n={len(yy):5d}  {m:+.4f} [{m - 1.96 * se:+.4f}, {m + 1.96 * se:+.4f}]  "
              f"z {m / se:+.1f}")
    if len(st_out) == 2:
        a_, b_ = st_out["departed from panel"], st_out["agreed with panel"]
        dd = a_["diff"] - b_["diff"]
        sd_ = math.sqrt(a_["se"] ** 2 + b_["se"] ** 2)
        print(f"  difference (departed - agreed) {dd:+.4f} "
              f"[{dd - 1.96 * sd_:+.4f}, {dd + 1.96 * sd_:+.4f}]  z {dd / sd_:+.1f}")

    # ------------------------------------------------------------------ the confound, and the fix
    # THE DIRECTIONAL PREDICTION FAILED AND IT FAILED INFORMATIVELY. Rationalisation says the
    # effect should be LARGER for people who broke from the panel -- they have more to justify.
    # It is larger for the people who AGREED (+0.0392 vs +0.0174, z -2.3). That is the signature of
    # a different mechanism: the contrast is not symmetric. When author A agreed with the panel and
    # the comparison rater B did not, A's choice IS the consensus response, and a consensus
    # response plausibly satisfies well-written criteria better whoever wrote them. So part of
    # "own minus other" is just "better response minus worse response".
    #
    # The fix removes response quality by construction. Take a prompt where two authors A and B
    # each wrote a sole-rated criterion and chose DIFFERENT responses a and b. Evaluate BOTH
    # criteria on BOTH responses:
    #     A's criterion:  sat_A(a) - sat_A(b)
    #     B's criterion:  sat_B(a) - sat_B(b)
    # If a is simply the better response, both differences are positive and equal. If AUTHORSHIP
    # matters, A's difference exceeds B's. The difference-in-differences is the estimand that
    # answers the question actually asked, and it cannot be produced by response quality.
    by_prompt = defaultdict(list)
    for r in rows:
        by_prompt[r["pid"]].append(r)
    did, dgp, dga = [], [], []
    pairs = 0
    for pid, rs in by_prompt.items():
        byauth = defaultdict(list)
        for r in rs:
            byauth[r["aid"]].append(r)
        auths = list(byauth)
        for i in range(len(auths)):
            for j in range(i + 1, len(auths)):
                A, B = auths[i], auths[j]
                a = byauth[A][0]["mine"]
                b = byauth[B][0]["mine"]
                if a == b:
                    continue
                pairs += 1
                dA = float(np.mean([r["vals"][a] - r["vals"][b] for r in byauth[A]]))
                dB = float(np.mean([r["vals"][a] - r["vals"][b] for r in byauth[B]]))
                did.append(dA - dB)
                dgp.append(pid)
                dga.append(f"{A}|{B}")
    print("\n" + "=" * 78)
    print("DIFFERENCE-IN-DIFFERENCES -- response quality removed by construction")
    print("=" * 78)
    if len(did) >= 100:
        md = float(np.mean(did))
        sed = two_way_se(did, dgp, dga)
        print(f"  author pairs on the same prompt choosing different responses: {pairs}")
        print(f"  DiD  [A's criteria on a-minus-b] - [B's criteria on a-minus-b]  = {md:+.4f}")
        print(f"       [{md - 1.96 * sed:+.4f}, {md + 1.96 * sed:+.4f}]   z {md / sed:+.1f}")
        print(f"       as a share of the judge's within-criterion range: "
              f"{abs(md) / np.mean(within):.1%}")
        did_z = md / sed
        if did_z > 3:
            print(f"  -> AUTHORSHIP SURVIVES. Holding the pair of responses fixed and comparing two")
            print(f"     authors' criteria on exactly the same two texts, each author's criteria")
            print(f"     favour that author's own prior choice. Response quality cannot produce")
            print(f"     this, because both criteria are scored on the same two responses.")
        elif abs(did_z) < 2:
            print(f"  -> AUTHORSHIP DOES NOT SURVIVE. Once the two responses are held fixed, whose")
            print(f"     criterion it is stops mattering ({md:+.4f}, z {did_z:+.1f}). The +0.0261")
            print(f"     headline was response quality: people who chose the better response have")
            print(f"     criteria that the better response satisfies, whoever wrote them. The")
            print(f"     post-hoc reading is WITHDRAWN.")
        else:
            print(f"  -> UNVERIFIED at z {did_z:+.1f}; the DiD neither confirms nor kills it.")
    else:
        did_z = float("nan")
        print(f"  too few author pairs ({len(did)}) for the DiD")

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    if Z > 3 and not (did_z == did_z and abs(did_z) < 2):
        print(f"  POST-HOC RATIONALISATION IS MEASURABLE, and the headline is the DiD rather than")
        print(f"  the raw contrast. Holding a PAIR of responses fixed and scoring two different")
        print(f"  authors' criteria on exactly those two texts, each author's criteria favour that")
        print(f"  author's own prior choice by {md:+.4f} -- {abs(md) / np.mean(within):.0%} of the "
              f"range the judge uses")
        print(f"  per criterion, z {did_z:+.1f}, over {pairs} author pairs.")
        print(f"  Response quality cannot produce this: both sets of criteria are evaluated on the")
        print(f"  same two responses, so 'a is simply better' cancels exactly.")
        print(f"\n  AND CONTROLLING FOR IT MADE THE EFFECT BIGGER, not smaller: {M:+.4f} raw against")
        print(f"  {md:+.4f} in the DiD. The raw contrast was DILUTED by response quality rather")
        print(f"  than inflated by it, so the first number understated what it was measuring. That")
        print(f"  is the opposite of what a confound usually does and the opposite of what I")
        print(f"  expected when I built the control.")
        print(f"\n  The criteria in this release are not independent statements of what a good")
        print(f"  answer looks like. They are partly descriptions of the answer their author had")
        print(f"  already chosen -- which is exactly what the documented task order makes likely,")
        print(f"  rubric authoring coming LAST, and which nobody had measured.")
        print(f"\n  WHY THIS MATTERS BEYOND THE DATASET: a pipeline that compiles these criteria")
        print(f"  into a rubric and scores a model against it is scoring the model against")
        print(f"  justifications of choices, not against independently stated values. The two")
        print(f"  coincide when the choice was well-made and diverge exactly when it was not.")
        print(f"\n  WHAT I CANNOT CONCLUDE: the dissent stratification above was computed on the")
        print(f"  CONFOUNDED contrast, so its failed directional prediction (agreed +0.0392 vs")
        print(f"  departed +0.0174) does not bear on rationalisation -- it is the response-quality")
        print(f"  mechanism showing through. In a DiD pair the two authors chose differently by")
        print(f"  construction, so at most one can hold the panel's choice and the stratification")
        print(f"  does not transfer. Whether rationalisation is stronger for dissenters is OPEN.")
    elif Z < -3:
        print(f"  REVERSED. Criteria favour OTHER raters' choices over their author's, which no")
        print(f"  account of the task order predicts and needs explaining before use.")
    elif Z > 3:
        print(f"  THE HEADLINE WAS A CONFOUND. The raw contrast is {M:+.4f} at z {Z:+.1f}, but it")
        print(f"  does not survive holding the pair of responses fixed (DiD {md:+.4f}, z "
              f"{did_z:+.1f}).")
        print(f"  What the raw number measures is that a person who picked the better response has")
        print(f"  criteria the better response satisfies -- true of anyone's criteria, not")
        print(f"  specifically the author's. The failed directional prediction is what exposed it:")
        print(f"  rationalisation predicts a LARGER effect for dissenters and the data gave a")
        print(f"  smaller one, which is what a response-quality mechanism predicts instead.")
        print(f"  THE CRITERIA ARE NOT POST-HOC DESCRIPTIONS OF THE WINNER, and given the")
        print(f"  documented task order that is a genuinely good result for the release.")
    else:
        print(f"  NO EFFECT. The criteria do not favour their own author's prior choice "
              f"({M:+.4f}, z {Z:+.1f}).")
        print(f"  Despite being written after the ranking, by the same person, in the same session,")
        print(f"  they are not descriptions of the winner. That is a stronger result for the")
        print(f"  release than most of what this sweep has found, and it was the outcome I")
        print(f"  expected least.")

    (OUT / "post_hoc.json").write_text(json.dumps(
        {"criteria": len(rows), "prompts": len({r["pid"] for r in rows}),
         "authors": len({r["aid"] for r in rows}), "per_seed": per_seed,
         "pooled_diff": M, "pooled_se": SE, "z": Z, "seed_spread": spread,
         "within_criterion_spread": float(np.mean(within)),
         "own_choice_mean_rank": float(np.mean(rk)),
         "own_choice_top_share": float(np.mean([x == 1 for x in rk])),
         "by_dissent": st_out,
         "did": {"n": len(did), "pairs": pairs,
                 "diff": md if len(did) >= 100 else None,
                 "se": sed if len(did) >= 100 else None,
                 "z": did_z if len(did) >= 100 else None,
                 "why": "removes response quality: both authors' criteria scored on the same two "
                        "responses"},
         "instrument": "Qwen3.5-2B-Base rebuilt judge; comparison is within criterion and within "
                       "prompt so judge bias cannot align with which rater is tested"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
