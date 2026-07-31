"""The 1.1% who reject the whole menu -- a harsh rater, or a prompt with no acceptable answer?

r150 found that 1.1% of assessments mark ALL FOUR responses unacceptable. Those participants are the
only ones in this release whose position is unrepresentable in principle rather than merely
outvoted: the pipeline must return one of four, and for them every available outcome is one they
have explicitly rejected. They are not unserved. They are overridden.

But the same 1.1% is produced by two worlds that mean opposite things, and this is the identical
person-versus-prompt fork that r145 had to resolve for the unserved third:

  RATER STYLE     a few people are simply harsh and reject everything everywhere. Then full
                  rejection is a scale-usage artefact, carries no information about the candidate
                  set, and pooling it with genuine rejection would manufacture a finding.
  PROMPT PROPERTY certain prompts genuinely admit no acceptable answer among the four offered. Then
                  full rejection is a measurement OF THE CANDIDATE GENERATION, and it is the only
                  direct evidence in the release that the menu itself can be inadequate.

THE SEPARATOR IS CONCENTRATION. If it is rater style, full rejections spread evenly across whichever
prompts those people happened to see. If it is a prompt property, they pile onto particular prompts,
and different people pile onto the same ones.

    null: permute each person's own rejection labels across the prompts THEY rated. That preserves
    every person's rate exactly -- a harsh rater stays exactly as harsh -- and destroys only the
    link between rejection and prompt. Whatever concentration survives that permutation is the part
    the raters' own styles cannot explain.

And the same floor discipline r145 required applies to the person side: a between-person spread in
rejection rate is manufactured by binomial noise at nine prompts each, so it is compared against a
within-person split-half floor before any count is quoted.

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

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}
MIN_PROMPTS = 6

from covalx.floors import (SCALE as FLOOR_SCALE,  # noqa: E402
                           read as floor_read)


def parse_unacceptable(blocks):
    """THE FIX. Not-asked is an EMPTY LIST, never a missing key, so `blk is None` never fires and
    13,672 never-posed questions were being counted as answered-zero. The question was asked iff
    the unacceptable or personal block is a NON-EMPTY list."""
    blk = blocks.get("unacceptable")
    if not (blk or blocks.get("personal")):
        return set(), [], False
    out, rats = set(), []
    for b in blk or []:
        for r in b.get("rating", []) or []:
            s = r.strip()
            for letter, idx in RANK_MAP.items():
                if s.startswith(letter):
                    out.add(idx)
        if b.get("rationale"):
            rats.append(b["rationale"])
    return out, rats, True


def load():
    rows = []
    demo: dict[str, dict] = {}
    with (ROOT / "data" / "annotators.jsonl").open() as fh:
        for line in fh:
            rec = json.loads(line)
            aid = rec["annotator_id"]
            demo[aid] = rec.get("demographics", {}) or {}
            for a in rec.get("assessments", []):
                blocks = a.get("ranking_blocks") or {}
                u, rats, has = parse_unacceptable(blocks)
                if not has:
                    continue
                rows.append({"pid": a["conversation_id"], "a": aid, "n_veto": len(u),
                             "all4": int(len(u) == 4), "any": int(len(u) > 0),
                             "rationales": rats,
                             "subjectivity": a.get("subjectivity"),
                             "importance": a.get("importance")})
    return rows, demo


def concentration(rows, key: str, field: str) -> float:
    """Variance of the per-`key` mean of `field` -- how unevenly the thing piles up."""
    by = defaultdict(list)
    for r in rows:
        by[r[key]].append(r[field])
    means = [np.mean(v) for v in by.values() if len(v) >= 3]
    return float(np.var(means, ddof=1)) if len(means) > 2 else float("nan")


def permute_within_person(rows, rng):
    """Preserves each person's own rejection count exactly; destroys only which prompt got it."""
    by = defaultdict(list)
    for i, r in enumerate(rows):
        by[r["a"]].append(i)
    out = [dict(r) for r in rows]
    for _a, idx in by.items():
        vals = [rows[i]["all4"] for i in idx]
        perm = rng.permutation(len(vals))
        for j, i in enumerate(idx):
            out[i]["all4"] = vals[perm[j]]
    return out


def split_half_floor(rows, seeds) -> float:
    by = defaultdict(list)
    for r in rows:
        by[r["a"]].append(r["all4"])
    by = {a: v for a, v in by.items() if len(v) >= MIN_PROMPTS}
    out = []
    for sd in seeds:
        rng = np.random.default_rng(sd)
        d = []
        for v in by.values():
            x = np.array(v, float)
            i = rng.permutation(len(x))
            h = len(x) // 2
            d.append(abs(x[i[:h]].mean() - x[i[h:]].mean()))
        out.append(float(np.mean(d)) * FLOOR_SCALE)   # see covalx.floors
    return float(np.mean(out)), by


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    rows, demo = load()
    n = len(rows)
    all4 = sum(r["all4"] for r in rows)
    print(f"assessments {n}   full rejections {all4} ({all4 / n:.2%})   "
          f"people {len({r['a'] for r in rows})}   prompts {len({r['pid'] for r in rows})}")

    # prompts touched by at least one full rejection, and the worst prompt
    by_p = defaultdict(list)
    for r in rows:
        by_p[r["pid"]].append(r["all4"])
    touched = sum(1 for v in by_p.values() if sum(v) > 0)
    worst = max(by_p.items(), key=lambda kv: np.mean(kv[1]) if len(kv[1]) >= 5 else -1)
    print(f"prompts with >=1 full rejection: {touched}/{len(by_p)} ({touched / len(by_p):.1%})")
    print(f"worst prompt: {np.mean(worst[1]):.1%} of its {len(worst[1])} raters rejected "
          f"the entire menu")
    dist = defaultdict(int)
    for v in by_p.values():
        dist[sum(v)] += 1
    print("prompts by number of full rejectors: "
          + "  ".join(f"{k}:{dist[k]}" for k in sorted(dist)[:7]))

    # ---- PERSON SIDE, with the floor
    floor, by_a = split_half_floor(rows, args.seeds)
    sd_obs = float(np.std([np.mean(v) for v in by_a.values()], ddof=1))
    print(f"\nperson side: {len(by_a)} people with >={MIN_PROMPTS} prompts")
    print(f"  between-person sd of rejection rate {sd_obs:.4f}")
    rd = floor_read(sd_obs, floor)
    print(f"  within-person split-half floor      {floor:.4f}   ratio {rd['ratio']}")
    print(f"  -> {rd['verdict']}")

    # ---- PROMPT SIDE, against the within-person permutation
    obs = concentration(rows, "pid", "all4")
    nulls = []
    for sd in args.seeds:
        rng = np.random.default_rng(sd + 4242)
        nulls.append(concentration(permute_within_person(rows, rng), "pid", "all4"))
    nl = float(np.mean(nulls))
    print(f"\nprompt side: variance of per-prompt rejection rate")
    print(f"  observed {obs:.6f}   null {nl:.6f}   ratio {obs / nl if nl else float('nan'):.2f}")
    print(f"  null by seed {[round(x, 6) for x in nulls]}")

    # do full rejectors say the prompt is subjective / important?
    def share(field, val, sub):
        s = [r for r in rows if sub(r)]
        return sum(1 for r in s if (r.get(field) or "").startswith(val)) / len(s) if s else None
    print("\nwhat full rejectors say about the prompt itself")
    for label, sub in (("full rejectors", lambda r: r["all4"]),
                       ("everyone else", lambda r: not r["all4"])):
        v = share("subjectivity", "The correct answer depends", sub)
        print(f"  {label:16s} 'answer depends on values/culture': "
              f"{v:.1%}" if v is not None else f"  {label}: n/a")

    # rationale text: is the complaint about the menu, or about content?
    MENU = re.compile(r"\b(none|neither|all (of them|four)|any of|no(ne)? of the|every (answer|"
                      r"response|option))\b", re.I)
    r_all = [t for r in rows if r["all4"] for t in r["rationales"]]
    r_part = [t for r in rows if r["any"] and not r["all4"] for t in r["rationales"]]
    for label, txts in (("full rejection", r_all), ("partial rejection", r_part)):
        if txts:
            print(f"  {label:18s} n={len(txts):5d}  mean chars {np.mean([len(t) for t in txts]):5.0f}"
                  f"   mentions the whole menu {sum(1 for t in txts if MENU.search(t)) / len(txts):.1%}")

    (OUT / "none_of_the_above.json").write_text(json.dumps({
        "assessments": n, "full_rejections": all4, "rate": round(all4 / n, 5),
        "prompts_touched": touched, "prompts": len(by_p),
        "prompts_touched_share": round(touched / len(by_p), 4),
        "worst_prompt_share": round(float(np.mean(worst[1])), 4),
        "person_between_sd": round(sd_obs, 5),
        "person_split_half_floor": round(floor, 5),
        "person_sd_over_floor": round(sd_obs / floor, 3) if floor else None,
        "prompt_concentration_observed": obs,
        "prompt_concentration_null": nl,
        "prompt_concentration_ratio": round(obs / nl, 3) if nl else None,
        "prompt_null_by_seed": nulls,
        "rationale_full_n": len(r_all), "rationale_partial_n": len(r_part),
        "instrument": "none -- veto blocks and rationale text only",
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
