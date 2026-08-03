"""One parser bug and one proxy inversion, and between them they broke four claims.

An independent adversary, given the claims and the raw data and told to refute them, returned three
OVERTURNED out of four. Both root causes are mine and both are recorded here rather than quietly
patched.

BUG ONE -- "NOT ASKED" IS AN EMPTY LIST, NOT A MISSING KEY.

    blocks.get("unacceptable")  ->  []      for 13,672 of 18,678 assessments
                                ->  [...]   for 5,006

I wrote a guard specifically to distinguish a missing answer from an empty one, because collapsing
them turns silence into an endorsement. The guard tested `blk is None`. The key is ALWAYS present.
So the guard never fired once, and every one of the 13,672 assessments where the veto question was
never posed was counted as "asked, and vetoed nothing".

`personal` and `unacceptable` are populated together and only together -- 5,006 assessments, each
annotator's first batch. The remaining 73.2% carry only `world`. Everything computed by defaulting
over all 18,678 rows silently answered a different question.

The damage, on the population where the question was actually administered:

    veto nothing            36.42%   claimed 82.9%
    veto all four            3.90%   claimed 1.1%
    P(veto | own top choice) 9.25%   claimed 2.6%
    P(veto | last)          58.68%   claimed 15.9%

And r150's headline "coverage is 100% of 18,562 assessments" was the artefact itself. Worse: r150
used that artefact to RETRACT r149's "330 of 1,100 prompts carry the block", which was closer to
correct. A retraction issued by a broken instrument has to be retracted in turn.

BUG TWO -- I CERTIFIED THE ABSENCE OF A PROPERTY WITH A TEST THAT ONLY SEES ONE CHANNEL.

r143 concluded force was never elicited because under 1% of criteria carry absolute-force wording.
The dataset card says plainly what the elicitation actually was: "negative weights indicate the
behaviors models should avoid... the absolute value indicated the importance". Force was collected
through the SIGNED WEIGHT, and a lexical scan structurally cannot see it.

    28.32% of criteria have |mean score| >= 8
    98.68% of those carry no absolute-force marker at all
    1,664 are negative at that magnitude -- "Incite violence or use racial slurs" at -10 is an
    absolute prohibition, and no keyword regex will ever find it

PROPERTY: force is present. PROXY: force wording appears. The implication runs one way only, and I
used it backwards -- exactly the failure the proxy ledger exists to prevent.

WHAT THIS RESTORES. Force WAS collected. And `coval_core` items carry exactly one key, `criterion`,
in 3,899 of 3,899 cases -- no weight, no sign, nothing. So compilation really does delete force, the
prediction I withdrew in r143 was right, and the withdrawal is itself withdrawn.
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import statistics as st
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}
MARK = re.compile(r"\b(never|under no|no circumstances|absolutely|must not|forbidden|"
                  r"unacceptable|at all costs|whatever else|always)\b", re.I)


def was_asked(blocks) -> bool:
    """THE FIX. The veto question was posed iff the block is a non-empty list. `is None` never
    fires because the key is always present, and `.get(k, [])` cannot tell the two apart either."""
    return bool(blocks.get("unacceptable")) or bool(blocks.get("personal"))


def parse_unacc(blocks) -> set:
    out = set()
    for b in blocks.get("unacceptable") or []:
        for r in b.get("rating", []) or []:
            for letter, idx in RANK_MAP.items():
                if r.strip().startswith(letter):
                    out.add(idx)
    return out


def parse_rank(blocks, key):
    for b in blocks.get(key) or []:
        t = b.get("ranking")
        if not t:
            continue
        v = np.full(4, np.nan)
        for gi, g in enumerate(t.replace(" ", "").split(">")):
            for letter in g.split("="):
                if letter in RANK_MAP:
                    v[RANK_MAP[letter]] = -gi
        if not np.isnan(v).all():
            return v
    return None


def ranks_of(v):
    order = sorted(range(4), key=lambda i: -(v[i] if not np.isnan(v[i]) else -99))
    pos, prev, p = {}, None, 0
    for k, i in enumerate(order):
        if prev is None or v[i] != prev:
            p = k
        pos[i] = p
        prev = v[i]
    return pos


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- the encoding itself
    enc = Counter()
    asked_rows, all_rows = [], 0
    for line in (ROOT / "data" / "annotators.jsonl").open():
        rec = json.loads(line)
        for a in rec.get("assessments", []):
            b = a.get("ranking_blocks") or {}
            all_rows += 1
            u, p = b.get("unacceptable"), b.get("personal")
            enc["unacc_" + ("MISSING" if u is None else "EMPTY" if u == [] else "FILLED")] += 1
            enc["personal_" + ("MISSING" if p is None else "EMPTY" if p == [] else "FILLED")] += 1
            if was_asked(b):
                asked_rows.append((rec["annotator_id"], a["conversation_id"], b))
    print(f"assessments {all_rows}   veto question actually asked {len(asked_rows)} "
          f"({len(asked_rows) / all_rows:.1%})")
    print("  encoding:", dict(enc))
    print("  the key is NEVER missing, so a `is None` guard never fires and `.get(k, [])` "
          "cannot distinguish not-asked from answered-zero")

    # ---------------------------------------------------------------- C3 recomputed
    cnt, byrank, tot = Counter(), Counter(), Counter()
    for _aid, _cid, b in asked_rows:
        u = parse_unacc(b)
        cnt[len(u)] += 1
        v = parse_rank(b, "personal")
        if v is None:
            v = parse_rank(b, "world")
        if v is None:
            continue
        pos = ranks_of(v)
        for i in range(4):
            tot[pos[i]] += 1
            if i in u:
                byrank[pos[i]] += 1
    n = len(asked_rows)
    dist = {str(k): round(cnt[k] / n, 4) for k in sorted(cnt)}
    prank = {str(p): round(byrank[p] / tot[p], 4) for p in sorted(tot)}
    print(f"\nveto count distribution on the ASKED population: {dist}")
    print(f"P(unacceptable | rank): {prank}")
    print("  claimed in r150: 0 -> 82.9%, 4 -> 1.1%, rank0 -> 2.6%, rank3 -> 15.9%")

    # rank-only explanatory power, recomputed
    base = sum(byrank.values()) / sum(tot.values())
    ll_r = ll_b = 0.0
    for p in tot:
        k, m = byrank[p], tot[p]
        for q_, acc in ((k / m, "r"), (base, "b")):
            q_ = min(max(q_, 1e-9), 1 - 1e-9)
            val = k * math.log(q_) + (m - k) * math.log(1 - q_)
            if acc == "r":
                ll_r += val
            else:
                ll_b += val
    mcf = 1 - ll_r / ll_b
    print(f"rank-only McFadden pseudo-R2: {mcf:.4f}   (claimed 0.0559)")

    # ---------------------------------------------------------------- C2 recomputed
    hi = hi_nomark = hi_neg = crit = 0
    examples = []
    for line in (ROOT / "data" / "conversation_rubrics.jsonl").open():
        r = json.loads(line)
        for it in r["coval_full"]:
            crit += 1
            m = st.fmean(s["score"] for s in it["scores"])
            if abs(m) >= 8:
                hi += 1
                if not MARK.search(it["criterion"]):
                    hi_nomark += 1
                if m < 0:
                    hi_neg += 1
                    if len(examples) < 6:
                        examples.append((round(m, 1), it["criterion"][:90]))
    print(f"\ncriteria {crit}   |mean score| >= 8: {hi} ({hi / crit:.2%})")
    print(f"  carrying NO absolute-force wording: {hi_nomark} ({hi_nomark / hi:.2%})")
    print(f"  negative at that magnitude (prohibitions carried by SIGN alone): {hi_neg}")
    for m, c in examples[:3]:
        print(f"     {m:+.1f}  {c}")

    # core carries no weight at all -- so the deletion is real
    core_keys = Counter()
    for line in (ROOT / "data" / "conversation_rubrics.jsonl").open():
        r = json.loads(line)
        for c in r["coval_core"]:
            core_keys[tuple(sorted(c.keys()))] += 1
    print(f"\ncoval_core key-sets: {dict(core_keys)}")
    print("  -> force WAS elicited, through the weight, and compilation deletes the weight. "
          "The r143 withdrawal of 'compilation loses force' is itself withdrawn.")

    res = {
        "assessments": all_rows, "asked": len(asked_rows),
        "asked_share": round(len(asked_rows) / all_rows, 4),
        "encoding": dict(enc),
        "veto_count_distribution_ASKED": dist,
        "p_unacceptable_by_rank_ASKED": prank,
        "rank_only_pseudo_r2_ASKED": round(mcf, 4),
        "superseded_r150": {"veto_nothing": 0.829, "veto_all_four": 0.011,
                            "p_rank0": 0.026, "p_rank3": 0.159, "pseudo_r2": 0.0559,
                            "coverage": 1.0},
        "criteria": crit, "high_magnitude": hi,
        "high_magnitude_share": round(hi / crit, 4),
        "high_magnitude_without_wording": round(hi_nomark / hi, 4),
        "high_magnitude_negative": hi_neg,
        "core_key_sets": {str(k): v for k, v in core_keys.items()},
        "instrument": "none -- counts and text only",
    }
    (OUT / "empty_list.json").write_text(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
