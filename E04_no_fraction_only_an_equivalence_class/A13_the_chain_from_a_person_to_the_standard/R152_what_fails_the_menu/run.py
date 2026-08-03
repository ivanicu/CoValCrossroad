"""What do the prompts with a failed candidate set have in common?

r151 established that full rejection -- marking all four responses unacceptable -- is five times more
concentrated on particular prompts than rater style explains. Those prompts are the only direct
evidence in this release that the candidate generation itself can fail. This asks what they are.

THE OUTCOME IS A RATE, NOT A FLAG. A prompt with 30 raters has more chances to collect at least one
full rejection than a prompt with 6, so "has a full rejection" is partly a measurement of panel size.
Everything below uses the per-prompt RATE, and panel size is carried as a covariate so it can be
seen rather than assumed away.

THE FORK THAT MATTERS. Two mechanisms produce the same concentration and they say different things
about response generation:

  SHARED INADEQUACY   everyone finds the menu poor on these prompts. Then the partial-veto rate is
                      elevated too, disagreement need not be high, and the finding is that the four
                      responses genuinely failed a question.
  DISPERSED DEMAND    people want different things here, so somebody is always unsatisfied. Then
                      disagreement is high, the partial-veto rate need not be, and the finding is
                      about the question being contested rather than the answers being bad.

These are distinguishable: shared inadequacy predicts full and partial rejection move together;
dispersed demand predicts full rejection tracks disagreement instead.

A NEAR-TAUTOLOGY IS NAMED IN ADVANCE. Full rejection is itself a kind of veto, so of course it
correlates with vetoing. The non-trivial version is whether the OTHER raters -- those who did not
fully reject -- veto more on these prompts. That measure excludes the full rejectors from its own
predictor and is the one reported as evidence.

Multiplicity over the whole feature family, BH at q=0.05, and a held-out split of the prompts.
No model is executed anywhere in this round.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import sys
from collections import defaultdict

import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}

TOPICS = {
    "health": r"\b(health|medic|symptom|doctor|therap|depress|anxi|medication|diagnos|sleep|"
              r"diet|vaccine)\b",
    "politics": r"\b(politic|election|government|immigra|vote|war|protest|law|policy|rights)\b",
    "relationships": r"\b(relationship|partner|friend|family|parent|marriage|divorce|dating)\b",
    "money": r"\b(money|invest|financ|salary|debt|tax|budget|loan|price)\b",
    "identity": r"\b(gender|race|religio|ethnic|nationalit|culture|belief|faith|sexual)\b",
    "advice_seeking": r"\b(should i|what should|how (do|can|should) i|advice|help me|recommend)\b",
    "moral": r"\b(right|wrong|moral|ethic|fair|unfair|justif|deserve|ought)\b",
}


def parse_ranking(txt: str):
    v = np.full(4, np.nan)
    groups = [g.strip() for g in txt.replace(" ", "").split(">") if g.strip()]
    if not groups:
        return None
    for gi, g in enumerate(groups):
        for letter in g.split("="):
            if letter in RANK_MAP:
                v[RANK_MAP[letter]] = -gi
    return v if not np.isnan(v).all() else None


def parse_unacc(blocks):
    """THE FIX, shared with r151 and r154. Not-asked is an EMPTY LIST, never a missing key, so a
    `blk is None` guard never fires and 13,672 never-posed questions get counted as answered-zero.
    The question was asked iff the unacceptable or personal block is a NON-EMPTY list."""
    blk = blocks.get("unacceptable")
    if not (blk or blocks.get("personal")):
        return set(), False
    out = set()
    for b in blk or []:
        for r in b.get("rating", []) or []:
            for letter, idx in RANK_MAP.items():
                if r.strip().startswith(letter):
                    out.add(idx)
    return out, True


def prompt_texts() -> dict[str, str]:
    out = {}
    with (ROOT / "data" / "comparisons.jsonl").open() as fh:
        for line in fh:
            r = json.loads(line)
            msgs = r["prompt"]["messages"]
            parts = []
            for m in msgs:
                # THE RELEASE SHIPS TWO MESSAGE SCHEMAS. comparisons.jsonl uses a flat
                # {role, content:str}; conversation_rubrics.jsonl uses a nested
                # {author:{role}, content:{parts:[str]}}. Reading only the nested form here
                # returned prompt text for ZERO of 1,095 prompts, every topic feature came out
                # constant, and the correlation helper correctly refused to report a constant --
                # so seven features vanished from the table without a word. Silent exclusion is a
                # scope claim; both schemas are handled and the match count is printed.
                role = m.get("role") or (m.get("author") or {}).get("role")
                if role != "user":
                    continue
                c = m.get("content")
                if isinstance(c, str):
                    parts.append(c)
                elif isinstance(c, dict):
                    parts.extend(x for x in (c.get("parts") or []) if isinstance(x, str))
            out[r["prompt_id"]] = " ".join(parts)
    return out


def kendall_dist(a: np.ndarray, b: np.ndarray) -> float:
    bad = tot = 0.0
    for i in range(4):
        for j in range(i + 1, 4):
            if np.isnan(a[i]) or np.isnan(a[j]) or np.isnan(b[i]) or np.isnan(b[j]):
                continue
            tot += 1
            da, db = a[i] - a[j], b[i] - b[j]
            if da == 0 or db == 0:
                bad += 0.5
            elif (da > 0) != (db > 0):
                bad += 1
    return bad / tot if tot else float("nan")


def load():
    per: dict[str, dict] = defaultdict(dict)
    subj: dict[str, list] = defaultdict(list)
    imp: dict[str, list] = defaultdict(list)
    with (ROOT / "data" / "annotators.jsonl").open() as fh:
        for line in fh:
            rec = json.loads(line)
            aid = rec["annotator_id"]
            for a in rec.get("assessments", []):
                blocks = a.get("ranking_blocks") or {}
                cid = a["conversation_id"]
                v = None
                for key in ("world", "personal"):
                    for b in blocks.get(key, []) or []:
                        v = parse_ranking(b.get("ranking") or "")
                        if v is not None:
                            break
                    if v is not None:
                        break
                u, has = parse_unacc(blocks)
                if not has:
                    continue
                per[cid][aid] = {"rank": v, "veto": u, "n": len(u)}
                if a.get("subjectivity"):
                    subj[cid].append(a["subjectivity"])
                if a.get("importance"):
                    imp[cid].append(a["importance"])
    return per, subj, imp


def features(per, subj, imp, texts) -> list[dict]:
    rows = []
    for cid, people in per.items():
        n = len(people)
        if n < 5:
            continue
        full = [a for a, d in people.items() if d["n"] == 4]
        rate = len(full) / n
        others = [d for a, d in people.items() if d["n"] != 4]
        # partial veto rate among NON-full-rejectors: excludes the outcome from its own predictor
        others_veto = float(np.mean([d["n"] > 0 for d in others])) if others else float("nan")
        others_veto_mean = float(np.mean([d["n"] for d in others])) if others else float("nan")
        ranks = [d["rank"] for d in people.values() if d["rank"] is not None]
        dis = float("nan")
        if len(ranks) >= 2:
            ds = [kendall_dist(ranks[i], ranks[j])
                  for i in range(len(ranks)) for j in range(i + 1, len(ranks))]
            ds = [d for d in ds if not math.isnan(d)]
            dis = float(np.mean(ds)) if ds else float("nan")
        t = texts.get(cid, "")
        row = {"pid": cid, "rate": rate, "panel": n, "any_full": int(len(full) > 0),
               "others_veto_share": others_veto, "others_veto_mean": others_veto_mean,
               "disagreement": dis, "prompt_chars": len(t),
               "subjectivity_values": float(np.mean(
                   [s.startswith("The correct answer depends") for s in subj[cid]]))
               if subj[cid] else float("nan"),
               "importance_high": float(np.mean(
                   [i.startswith("Very") or i.startswith("Extremely") for i in imp[cid]]))
               if imp[cid] else float("nan")}
        for name, pat in TOPICS.items():
            row[f"topic_{name}"] = int(bool(re.search(pat, t, re.I)))
        rows.append(row)
    return rows


def corr_test(rows, feat, outcome="rate"):
    x = np.array([r[feat] for r in rows], float)
    y = np.array([r[outcome] for r in rows], float)
    m = ~(np.isnan(x) | np.isnan(y))
    x, y = x[m], y[m]
    if len(x) < 30 or x.std() == 0:
        return None
    r = float(np.corrcoef(x, y)[0, 1])
    z = 0.5 * math.log((1 + r) / (1 - r)) if abs(r) < 1 else 0.0
    se = 1 / math.sqrt(len(x) - 3)
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z / se) / math.sqrt(2))))
    return {"feature": feat, "r": r, "n": len(x), "p": p,
            "ci95": [math.tanh(z - 1.96 * se), math.tanh(z + 1.96 * se)]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--salts", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    per, subj, imp = load()
    texts = prompt_texts()
    rows = features(per, subj, imp, texts)
    hit = [r for r in rows if r["any_full"]]
    print(f"prompts analysed {len(rows)}   with >=1 full rejection {len(hit)}   "
          f"prompt text matched {sum(1 for r in rows if r['prompt_chars'] > 0)}")
    print(f"panel size: hit {np.mean([r['panel'] for r in hit]):.1f}  "
          f"clean {np.mean([r['panel'] for r in rows if not r['any_full']]):.1f}"
          f"   <- the confound the RATE outcome removes")

    feats = ["others_veto_share", "others_veto_mean", "disagreement", "panel", "prompt_chars",
             "subjectivity_values", "importance_high"] + [f"topic_{t}" for t in TOPICS]
    res, dropped = [], []
    for f in feats:
        c = corr_test(rows, f)
        (res.append(c) if c else dropped.append(f))
    if dropped:
        print(f"DROPPED as constant or under-covered (named, not silently omitted): {dropped}")
    ps = [c["p"] for c in res]
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    kmax = -1
    for rank_, i in enumerate(order, 1):
        if ps[i] <= 0.05 * rank_ / len(ps):
            kmax = rank_
    for rank_, i in enumerate(order, 1):
        res[i]["bh"] = rank_ <= kmax

    print(f"\ncorrelation with the per-prompt full-rejection RATE  ({len(res)} features, BH q=0.05)")
    for c in sorted(res, key=lambda c: c["p"]):
        print(f"  {c['feature']:22s} r={c['r']:+.4f} [{c['ci95'][0]:+.3f},{c['ci95'][1]:+.3f}] "
              f"n={c['n']:4d} p={c['p']:.5f} {'BH' if c['bh'] else ''}")

    # held out: do the BH-surviving features replicate on a disjoint half?
    print("\nheld out (disjoint halves of the prompts):")
    survivors = [c["feature"] for c in res if c["bh"]]
    held = {}
    for f in survivors:
        signs = []
        for salt in args.salts:
            a = [r for r in rows if (hash((r["pid"], salt)) & 0xFFFF) % 2 == 0]
            b = [r for r in rows if (hash((r["pid"], salt)) & 0xFFFF) % 2 == 1]
            ca, cb = corr_test(a, f), corr_test(b, f)
            if ca and cb:
                signs.append((ca["r"] > 0) == (cb["r"] > 0))
        held[f] = f"{sum(signs)}/{len(signs)}"
        print(f"  {f:22s} halves agree on sign in {held[f]} splits")

    # the fork
    ov = corr_test(rows, "others_veto_share")
    dg = corr_test(rows, "disagreement")
    verdict = "UNDECIDED"
    if ov and dg:
        verdict = ("SHARED INADEQUACY -- other raters veto more on these prompts, and that is "
                   "stronger than disagreement" if abs(ov["r"]) > abs(dg["r"]) else
                   "DISPERSED DEMAND -- full rejection tracks disagreement more than shared "
                   "dissatisfaction")
        print(f"\nothers_veto_share r={ov['r']:+.4f}   disagreement r={dg['r']:+.4f}")
        print(f"VERDICT: {verdict}")

    (OUT / "what_fails.json").write_text(json.dumps({
        "n_prompts": len(rows), "n_with_full_rejection": len(hit),
        "panel_hit": round(float(np.mean([r["panel"] for r in hit])), 2),
        "panel_clean": round(float(np.mean([r["panel"] for r in rows if not r["any_full"]])), 2),
        "features": sorted(res, key=lambda c: c["p"]),
        "held_out": held, "verdict": verdict,
        "instrument": "none -- rankings, veto blocks and prompt text only",
    }, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
