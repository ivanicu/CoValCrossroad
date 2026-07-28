"""A07 -- Does the values rubric see anthropomorphism at all?

The Trustworthy AI role names TWO full-stack problems:
  (a) methods for public input into model values
  (b) understanding impacts of anthropomorphism of AI

They are usually studied by different people. This connects them on one dataset.

The question
------------
Humans ranked 4,312 responses. Some of those responses talk like a person --
first-person stance, emotional attunement, asking the user something back.
Two things can be true independently:

  1. anthropomorphic style PREDICTS human preference
  2. the crowd-written rubric CAPTURES that style

If (1) and not (2), then the public-input pipeline is systematically blind to a
property that is driving the very preferences it is trying to encode -- and any
model optimized against the rubric is free to move on that axis unobserved.
That is a deployment-relevant blind spot, not a literary observation.

Design
------
* Marker lexicon is explicit and auditable (printed, disputable line by line).
* Everything is WITHIN-PROMPT: responses are only ever compared against the
  three others for the same prompt, so topic cannot drive the result.
* Length is the obvious confound and is controlled two ways: as a regressor,
  and by a length-matched subsample.
* The decisive test regresses human Borda on rubric score AND anthropomorphism
  together. A positive independent anthropomorphism coefficient means the rubric
  does not absorb it.
* Standard errors are clustered on prompt (one prompt contributes 4 rows).
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = str(_HERE.parents[1])
_RES = str(_HERE / "results")

LABELS = ("A", "B", "C", "D")

# ---- auditable marker lexicon ------------------------------------------
MARKERS: dict[str, tuple[str, ...]] = {
    "first_person_stance": (
        r"\bi think\b", r"\bi believe\b", r"\bi feel\b", r"\bin my (view|opinion)\b",
        r"\bi'd\b", r"\bi would\b", r"\bi'm\b", r"\bi am\b", r"\bmy sense\b",
    ),
    "self_as_agent": (
        r"\bas an ai\b", r"\bi'm here\b", r"\bi can help\b", r"\bi cannot\b",
        r"\bi can't\b", r"\bi don't have\b", r"\bi'm not able\b", r"\bmy role\b",
    ),
    "emotional_attunement": (
        r"\bi'm sorry\b", r"\bi understand how\b", r"\bthat sounds\b",
        r"\bit's understandable\b", r"\bi hear you\b", r"\bthat must be\b",
        r"\bit makes sense that you\b", r"\bi appreciate\b",
    ),
    "user_directed_warmth": (
        r"\byou might feel\b", r"\byour feelings\b", r"\btake care\b",
        r"\byou're not alone\b", r"\bbe kind to yourself\b", r"\bit's okay to\b",
    ),
    "turn_taking": (
        r"\?\s*$", r"\bwould you like\b", r"\bcan you tell me\b",
        r"\bwhat matters most to you\b", r"\blet me know\b", r"\bif you'd like\b",
    ),
}

# Does any criterion in the whole corpus even talk about this axis?
#
# NOTE: substring matching leaks badly here -- "persona" matches "personal",
# "personality", "personalities"; "friend" matches "friendly", "friendships".
# A first pass using substrings reported 2.96%, of which 321/452 hits were
# these false positives. Word-boundary regexes only, and split into two tiers
# because "be empathetic" is not the same claim as "do not pretend to be human".
RUBRIC_ANTHRO_T1 = (   # unambiguous: the model presenting AS a person
    r"\banthropomorph", r"\bhuman-?like\b", r"\blike a (person|human|friend)\b",
    r"\bpersona\b", r"\bpretend(s|ing)? to (be|feel|have)\b",
    r"\bclaim(s|ing)? to (have|feel)\b", r"\bsentient\b", r"\bparasocial\b",
    r"\bemotional attachment\b", r"\bact like a friend\b",
    r"\bfirst[- ]person\b", r"\bas an ai\b", r"\bits own (opinion|feelings|views)\b",
    r"\bpersonal opinion\b", r"\bhas feelings\b", r"\breal friend\b",
)
RUBRIC_ANTHRO_T2 = (   # relational/affective style -- adjacent, not the same claim
    r"\bempath(y|etic|ise|ize)", r"\bwarmth\b", r"\bcaring\b",
    r"\bemotional support\b", r"\bcompassion", r"\brapport\b",
    r"\bfriend(s)?\b",
)
RUBRIC_ANTHRO_TERMS = RUBRIC_ANTHRO_T1


def marker_counts(text: str) -> dict[str, float]:
    t = text.lower()
    out = {}
    for fam, pats in MARKERS.items():
        n = sum(len(re.findall(p, t, flags=re.MULTILINE)) for p in pats)
        out[fam] = n
    return out


def parse_ranking(s: str) -> list[list[str]]:
    out = []
    for grp in str(s).split(">"):
        m = [t.strip() for t in grp.split("=") if t.strip() in LABELS]
        if m:
            out.append(m)
    return out


def borda_points(s: str) -> dict[str, float]:
    r = parse_ranking(s)
    pts, rank = {}, 0
    for grp in r:
        size = len(grp)
        avg = float(np.mean([len(LABELS) - 1 - (rank + i) for i in range(size)]))
        for m in grp:
            pts[m] = avg
        rank += size
    return pts


def cluster_ols(X: np.ndarray, y: np.ndarray, groups: np.ndarray):
    """OLS with cluster-robust (CR0) standard errors."""
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    resid = y - X @ beta
    meat = np.zeros((X.shape[1], X.shape[1]))
    for g in np.unique(groups):
        m = groups == g
        u = X[m].T @ resid[m]
        meat += np.outer(u, u)
    V = XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(V))
    return beta, se


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--comparisons", type=Path, default=Path(_ROOT + "/data/comparisons.jsonl"))
    p.add_argument("--rubrics", type=Path, default=Path(_ROOT + "/data/conversation_rubrics.jsonl"))
    p.add_argument("--sat", type=Path, default=Path(_ROOT) / "rounds" / "r04_rebuild_satisfaction" / "results" / "a04_full.npz")
    p.add_argument("--out", type=Path, default=Path(_RES + "/a07_anthropomorphism.json"))
    a = p.parse_args()

    # ---- 1. does the rubric corpus even mention this axis? -------------
    total_crit = 0
    t1_crit = t2_crit = 0
    hits = defaultdict(int)
    examples = []
    for line in open(a.rubrics, encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        for it in rec.get("coval_full") or []:
            total_crit += 1
            t = it["criterion"].lower()
            f1 = [w for w in RUBRIC_ANTHRO_T1 if re.search(w, t)]
            f2 = [w for w in RUBRIC_ANTHRO_T2 if re.search(w, t)]
            if f1:
                t1_crit += 1
                for w in f1:
                    hits[w] += 1
                if len(examples) < 8:
                    examples.append(it["criterion"][:100])
            if f2:
                t2_crit += 1
    print("=== 1. does the crowd-written rubric talk about anthropomorphism? ===")
    print(f"  TIER 1 (model presenting AS a person): {t1_crit:,} / {total_crit:,} = {t1_crit/total_crit:.2%}")
    print(f"  TIER 2 (relational/affective style):   {t2_crit:,} / {total_crit:,} = {t2_crit/total_crit:.2%}")
    for w, n in sorted(hits.items(), key=lambda kv: -kv[1])[:8]:
        print(f"     {w:34s} {n:,}")
    print("  tier-1 examples:")
    for e in examples[:5]:
        print(f"     - {e}")
    anthro_crit = t1_crit

    # ---- 2. markers per response + human Borda ------------------------
    rows = []
    for line in open(a.comparisons, encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        pid = rec["prompt_id"]
        texts = {r["response_index"]: r["messages"][0]["content"] for r in rec["responses"]}
        borda = defaultdict(list)
        for asm in rec["metadata"]["assessments"]:
            w = (asm.get("ranking_blocks") or {}).get("world") or []
            if not w:
                continue
            for lab, pt in borda_points(w[0].get("ranking", "")).items():
                borda[lab].append(pt)
        if not borda:
            continue
        for lab, txt in texts.items():
            if lab not in borda:
                continue
            mc = marker_counts(txt)
            nwords = max(len(txt.split()), 1)
            rows.append({
                "prompt": pid, "label": lab,
                "borda": float(np.mean(borda[lab])),
                "n_raters": len(borda[lab]),
                "chars": len(txt), "words": nwords,
                "anthro_total": sum(mc.values()),
                "anthro_per_100w": 100.0 * sum(mc.values()) / nwords,
                **{f"m_{k}": v for k, v in mc.items()},
            })
    print(f"\n=== 2. responses measured: {len(rows):,} ===")

    prompts = np.array([r["prompt"] for r in rows])
    borda = np.array([r["borda"] for r in rows])
    anth = np.array([r["anthro_per_100w"] for r in rows])
    words = np.array([r["words"] for r in rows], dtype=float)

    # within-prompt demeaning: compare a response only to its 3 siblings
    def demean(v):
        out = np.empty_like(v, dtype=float)
        for pr in np.unique(prompts):
            m = prompts == pr
            out[m] = v[m] - v[m].mean()
        return out

    by, ba, bw = demean(borda), demean(anth), demean(np.log(words))

    print("\n=== 3. within-prompt: does anthropomorphic style predict human preference? ===")
    X = np.column_stack([np.ones_like(ba), ba])
    beta, se = cluster_ols(X, by, prompts)
    print(f"  anthropomorphism alone            beta={beta[1]:+.4f}  se={se[1]:.4f}  t={beta[1]/se[1]:+.2f}")
    X2 = np.column_stack([np.ones_like(ba), ba, bw])
    beta2, se2 = cluster_ols(X2, by, prompts)
    print(f"  + controlling for log(length)     beta={beta2[1]:+.4f}  se={se2[1]:.4f}  t={beta2[1]/se2[1]:+.2f}"
          f"   [length beta={beta2[2]:+.4f} t={beta2[2]/se2[2]:+.2f}]")

    # per family
    print("\n  per marker family (within-prompt, length-controlled):")
    fam_out = {}
    for fam in MARKERS:
        v = np.array([100.0 * r[f"m_{fam}"] / r["words"] for r in rows])
        bv = demean(v)
        Xf = np.column_stack([np.ones_like(bv), bv, bw])
        bf, sf = cluster_ols(Xf, by, prompts)
        fam_out[fam] = {"beta": float(bf[1]), "se": float(sf[1]), "t": float(bf[1] / sf[1])}
        print(f"    {fam:22s} beta={bf[1]:+.4f}  t={bf[1]/sf[1]:+.2f}")

    # ---- 4. THE DECISIVE TEST: does the rubric absorb it? -------------
    result_blind = None
    if a.sat.exists():
        z = np.load(a.sat, allow_pickle=True)
        lut = defaultdict(list)
        for m, s in zip(z["meta"], z["sat"]):
            pid, ci, lab = str(m).split("|")
            lut[(pid, lab)].append(float(s))
        rub = np.array([
            float(np.mean(lut[(r["prompt"], r["label"])])) if lut.get((r["prompt"], r["label"])) else np.nan
            for r in rows
        ])
        ok = ~np.isnan(rub)
        print(f"\n=== 4. DECISIVE: is the human preference for this style ABSORBED by the rubric? ===")
        print(f"  responses with a rubric score: {ok.sum():,}")
        br = demean(rub.copy())
        Xd = np.column_stack([np.ones(ok.sum()), br[ok], ba[ok], bw[ok]])
        bd, sd = cluster_ols(Xd, by[ok], prompts[ok])
        names = ["const", "rubric_score", "anthropomorphism", "log_length"]
        for i, nm in enumerate(names):
            if i == 0:
                continue
            print(f"    {nm:20s} beta={bd[i]:+.4f}  se={sd[i]:.4f}  t={bd[i]/sd[i]:+.2f}")
        indep = abs(bd[2] / sd[2]) > 2 and bd[2] > 0
        result_blind = {
            "rubric_beta": float(bd[1]), "rubric_t": float(bd[1] / sd[1]),
            "anthro_beta": float(bd[2]), "anthro_t": float(bd[2] / sd[2]),
            "length_beta": float(bd[3]), "length_t": float(bd[3] / sd[3]),
            "rubric_is_blind": bool(indep),
        }
        print(f"\n  -> {'RUBRIC IS BLIND: humans reward this style and the rubric does not absorb it'if indep else 'rubric absorbs it (no independent effect)'}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "criteria_total": total_crit,
        "criteria_tier1_anthropomorphism": t1_crit,
        "criteria_tier1_share": t1_crit / total_crit,
        "criteria_tier2_affective": t2_crit,
        "criteria_tier2_share": t2_crit / total_crit,
        "term_hits": dict(hits),
        "responses": len(rows),
        "anthro_alone": {"beta": float(beta[1]), "se": float(se[1])},
        "anthro_length_controlled": {"beta": float(beta2[1]), "se": float(se2[1])},
        "per_family": fam_out,
        "rubric_absorption_test": result_blind,
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
