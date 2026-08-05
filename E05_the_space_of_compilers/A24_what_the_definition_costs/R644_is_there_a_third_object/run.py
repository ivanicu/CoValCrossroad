#!/usr/bin/env python3
"""
R644 -- does any object on disk besides the two releases satisfy the five fields?

CHECK #245: A COMPLETENESS CLAIM AND AN UNCOMPUTED SUPERLATIVE.
  ⛔ "the production work is DONE" -- the four inert sites still carry the old code. The CORRECTIVE
     work is done; the PREVENTIVE installation is not. Twenty-eighth.
  ⛔ "the arc's OLDEST open item" -- never enumerated.

⭐ AND GOING TO THE OBJECT FOUND SOMETHING THE ARC HAS NEVER OPENED. `data/metadata.jsonl` is 85 MB
   and has appeared in no round this session, alongside merged_comparisons_annotators.jsonl (26 MB)
   and annotators.jsonl (16 MB). The arc has spent forty rounds on two files while six sit in the
   same directory.

ESTIMAND        for every .jsonl on disk, which of R618's five fields it carries:
                  ① a prompt / user turn        ② multiple responses per unit
                  ③ a human preference target   ④ a released criterion POOL
                  ⑤ a released CORE
IDENTIFICATION  Exact by key presence, the same instrument R618 used and R618 validated by
                REPRODUCTION against R603's verdict. ⚠ NECESSARY, NOT SUFFICIENT, unchanged from
                R618: a file can carry all five keys and still be useless, and R602 measured the
                second corpus as disjoint in CONTENT, which no schema check can see.
SCOPE           population : every .jsonl under data/
                instrument : key presence over a streamed prefix, cap 40k lines
                             instrument unit = A FIELD IN A FILE
                             claim unit      = AN EVALUABLE OBJECT. NOT equal -- a release may span
                             SEVERAL files, so a per-file verdict understates what a JOIN could do,
                             and the join is reported separately.
                baseline   : the home release (5/5) and the second (3/5), both measured in R618
                regime     : this repository at this sha
WORLDS          A A THIRD OBJECT EXISTS: some file or join carries all five -> clause ② becomes
                  testable cross-object for the first time and the arc has a new experiment.
                B NO THIRD OBJECT: nothing beyond the home release qualifies -> R618's
                  specification IS the deliverable and the arc closes on it.
                C A JOIN QUALIFIES BUT NO SINGLE FILE: the fields exist but are split across files
                  -> the object is constructible rather than found, which is a different claim and
                  a different amount of work.
KILL            pre-registered: any non-home file or join scoring 5/5 -> world A, and it is named.
POSITIVE CTRL   the home release must score 5/5 -- it is the object the definition was written
                from. Fails at g=0: a file with none of the fields must score 0.
NEGATIVE CTRL   the second release must score exactly 3/5, missing pool and core, reproducing
                R618's published result. A different number means the instrument has drifted.
PLACEBO         a key no file uses -> 0 files.
SEEDS           n/a, deterministic.
MULTIPLICITY    every file x 5 fields + the join + 4 controls. Full table printed.
ARTIFACT        results/is_there_a_third_object.json
IMPOSSIBLE      key presence is NECESSARY and NOT SUFFICIENT. R602 measured the second corpus as
                disjoint in content -- exact overlap 0, token-Jaccard at the shuffled floor -- and
                no schema check can see that. This screens; it cannot certify.
"""
from __future__ import annotations
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
CAP = 40000

FIELDS = [
    ("① prompt / user turn",        ("prompt", "user_prompt", "conversation", "text", "utterance")),
    ("② multiple responses / unit", ("responses", "model_response", "completions", "outputs")),
    ("③ human preference target",   ("score", "preference", "ranking", "label", "rating", "winner")),
    ("④ released criterion POOL",   ("coval_full", "rubric", "criteria", "rubrics")),
    ("⑤ released CORE",             ("coval_core", "core")),
]


def keys_of(p):
    ks, n = set(), 0
    try:
        with p.open() as fh:
            for line in fh:
                if n >= CAP: break
                try: j = json.loads(line)
                except Exception: continue
                if isinstance(j, dict):
                    ks |= set(j)
                    for v in j.values():
                        if isinstance(v, list) and v and isinstance(v[0], dict):
                            ks |= {f"{k}[]" for k in v[0]}
                n += 1
    except Exception:
        return None
    return ks


def score(ks):
    if ks is None: return []
    got = []
    for name, cands in FIELDS:
        hit = any(c in ks or f"{c}[]" in ks or any(k.startswith(c) for k in ks) for c in cands)
        got.append(hit)
    return got


def main():
    files = sorted(DATA.glob("*.jsonl"))
    if len(files) < 2:
        print(f"UNRUNNABLE: {len(files)} jsonl files. Exit 2, never 0."); return 2
    print(f"  .jsonl files under data/: {len(files)}  (cap {CAP} lines each)")

    table = {}
    for f in files:
        ks = keys_of(f)
        table[f.name] = {"keys": sorted(ks)[:14] if ks else None, "score": score(ks),
                         "n_keys": len(ks) if ks else 0}

    print(f"\n─── EVERY OBJECT ON DISK AGAINST R618's FIVE FIELDS ───")
    print(f"  {'file':<42} {'keys':>5}  ① ② ③ ④ ⑤   total")
    for n, v in table.items():
        s = v["score"]
        print(f"  {n:<42} {v['n_keys']:>5}  " + " ".join("✓" if x else "·" for x in s)
              + f"   {sum(s)}/5")

    home = [n for n in table if n in ("comparisons.jsonl", "conversation_rubrics.jsonl")]
    second = [n for n in table if n == "utterances.jsonl"]
    home_union = set()
    for n in home: home_union |= set(table[n]["keys"] or [])
    hs = score(home_union)
    print(f"\n  HOME RELEASE (union of {len(home)} files): "
          + " ".join("✓" if x else "·" for x in hs) + f"  {sum(hs)}/5")

    all_union = set()
    for n, v in table.items():
        if n not in home: all_union |= set(v["keys"] or [])
    js = score(all_union)
    print(f"  JOIN of every NON-HOME file:              "
          + " ".join("✓" if x else "·" for x in js) + f"  {sum(js)}/5")

    print(f"\n─── CONTROLS ───")
    pos = sum(hs) == 5
    print(f"  POSITIVE  the home release scores 5/5 -> {'PASS' if pos else f'⛔ FAIL ({sum(hs)}/5)'}")
    sec = score(set(table.get("utterances.jsonl", {}).get("keys") or []))
    neg = sum(sec) == 3 and not sec[3] and not sec[4]
    print(f"  NEGATIVE  the second release scores exactly 3/5 missing pool+core -> "
          f"{'PASS' if neg else f'⚠ {sum(sec)}/5 — the instrument has drifted from R618'}")
    g0 = score(set())
    print(f"  g=0       a file with no keys scores {sum(g0)}/5 -> "
          f"{'PASS' if sum(g0) == 0 else '⛔ FAIL'}")
    plc = sum(1 for v in table.values() if "zzq_nokey" in (v["keys"] or []))
    print(f"  PLACEBO   a key no file uses -> {plc} -> {'PASS' if plc == 0 else '⛔ FAIL'}")
    controls_ok = pos and sum(g0) == 0 and plc == 0

    winners = [n for n, v in table.items() if n not in home and sum(v["score"]) == 5]
    print(f"\n─── VERDICT (pre-registered: any non-home file or join at 5/5 -> world A) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif winners:
        world = (f"A A THIRD OBJECT EXISTS — {winners} carries all five fields. Clause ② becomes "
                 f"testable cross-object for the first time.")
    elif sum(js) == 5:
        world = (f"C A JOIN QUALIFIES BUT NO SINGLE FILE — the five fields exist across the "
                 f"non-home files but no one file carries them. The object is CONSTRUCTIBLE rather "
                 f"than found, which is a different claim and a different amount of work.")
    else:
        world = (f"B NO THIRD OBJECT — nothing beyond the home release reaches 5/5, alone or "
                 f"joined (best non-home join: {sum(js)}/5). R618's specification IS the "
                 f"deliverable, and the arc can close on it.")
    print(f"  {world}")
    print(f"\n  ⚠ NECESSARY, NOT SUFFICIENT — unchanged from R618. A file can carry all five keys "
          f"and still be useless: R602 measured the second corpus as disjoint in CONTENT, which no "
          f"schema check can see. This screens out impossibilities; it cannot certify a site.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "is_there_a_third_object.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "per_file": {n: {"n_keys": v["n_keys"], "score": v["score"], "total": sum(v["score"]),
                         "sample_keys": v["keys"]} for n, v in table.items()},
        "home_union_score": hs, "nonhome_join_score": js,
        "check245": ("'the production work is done' -- the four inert sites still carry the old "
                     "code; and 'the arc's oldest open item' was never enumerated"),
        "impossible": "key presence is necessary and not sufficient; content disjointness is invisible",
    }, indent=2))
    print(f"\n  wrote {OUT / 'is_there_a_third_object.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
