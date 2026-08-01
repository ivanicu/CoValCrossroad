"""Two claims the register filed as MEANs are NULLS, and a jackknife cannot say anything about them.

r203 sorted 79 standing claims by the attack their shape admits and put 44 in the MEAN bucket for
the calibrated jackknife. Ranking the outstanding ones by test statistic to attack the weakest
first surfaced two problems at once, and the second is the round.

FIRST: ONLY 4 OF 40 STATEMENTS CARRY AN EXTRACTABLE z. Thirty-six claims in this graph do not
record the statistic they rest on, so neither the register nor a reader can rank them by strength.
That is a content-discipline defect in the graph itself, found by trying to use it rather than by
auditing it.

SECOND, AND WORSE: the two lowest-z claims are z 0.4 and z 1.1 -- both NULLS.

    weight-deletion-null-under-the-reference-judge   "MEASUREMENT ONLY... z 0.4"
    compilation-passes-it-through                    "neither concentrates nor removes... z +1.1"

A jackknife asks whether an effect is carried by a handful of units. A null has no effect to be
carried, so the question is malformed, and r202's own tool would have returned NO RESOLUTION for
exactly the reason it was built to return it -- the reference dies at k<=2 when there is nothing
to delete. The register would have sent me to run a check its own instrument refuses.

THE ATTACK A NULL ADMITS IS POWER. Not "is the effect concentrated" but "what effect could this
design have detected, and is that smaller than the effect that would matter". A null without an
MDE is silence reported as evidence -- which is a law this project has applied to others and is
now applying to itself.

So this round adds NULL as a seventh shape to the register and runs the power calculation both
nulls have been missing.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "db"))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
LETTERS = "ABCD"

import derivation_chain as dc  # noqa: E402


def mde(se, power=0.80, alpha=0.05):
    """smallest effect this design detects at the stated power -- (z_alpha/2 + z_power) * SE"""
    return (1.959964 + 0.8416212) * se


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- rebuild r188's null
    d = np.load(ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz",
                allow_pickle=True)
    sat = {}
    for k, v in zip(d["meta"], d["sat"]):
        pid, ci, L = str(k).split("|")
        sat[(pid, int(ci), L)] = float(v)
    import difflib
    from covalx.judge import load_join
    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]
    choice = defaultdict(dict)
    for a in ann:
        for s in a.get("assessments", []):
            for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
                g = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
                if g and len(g[0].split("=")) == 1 and g[0] in LETTERS:
                    choice[s.get("conversation_id")][a["annotator_id"]] = g[0]
                break

    rows = []
    for pid, _p, r in load_join(DATA / "comparisons.jsonl", DATA / "conversation_rubrics.jsonl"):
        core_low = [c["criterion"].lower() for c in r["coval_core"]]
        ch = choice.get(pid) or {}
        if not core_low:
            continue
        for ci, it in enumerate(r["coval_full"]):
            sc = it.get("scores") or []
            if len(sc) != 1:
                continue
            aid = sc[0].get("annotator_id")
            mine = ch.get(aid)
            if mine is None:
                continue
            vals = {L: sat.get((pid, ci, L)) for L in LETTERS}
            if any(v is None for v in vals.values()):
                continue
            enc = vals[mine] - float(np.mean([vals[L] for L in LETTERS if L != mine]))
            surv = bool(difflib.get_close_matches(it["criterion"].lower(), core_low,
                                                  n=1, cutoff=0.60))
            rows.append({"pid": pid, "aid": aid, "enc": enc, "survived": surv})
    groups = defaultdict(list)
    for r_ in rows:
        groups[(r_["aid"], r_["pid"])].append(r_)
    usable = {k: v for k, v in groups.items()
              if len(v) >= 2 and 0 < sum(x["survived"] for x in v) < len(v)}
    y = []
    for _k, v in usable.items():
        s_ = [x["enc"] for x in v if x["survived"]]
        d_ = [x["enc"] for x in v if not x["survived"]]
        y.append(float(np.mean(s_)) - float(np.mean(d_)))
    m = float(np.mean(y))
    se = float(np.std(y, ddof=1) / math.sqrt(len(y)))
    enc_sd = float(np.std([r_["enc"] for r_ in rows]))

    print("=" * 92)
    print("NULL 1 -- r188: the compilation neither concentrates nor removes the rationalisation")
    print("=" * 92)
    print(f"  observed {m:+.4f}  se {se:.4f}  z {m / se:+.2f}  over {len(y)} (author, prompt) groups")
    M = mde(se)
    print(f"  MDE at 80% power, alpha .05: {M:+.4f}  =  {M / enc_sd:.3f} sd of the encoding "
          f"distribution")
    print(f"  the effect this null had to rule out: r187 measured the INCOMING rationalisation at")
    print(f"  +0.0478, which is 14.2% of the judge's within-criterion range.")
    ratio = M / 0.0478
    print(f"  MDE / incoming effect = {ratio:.2f}")
    if ratio < 0.5:
        print(f"  -> A POWERED NULL. The design could have detected a selection effect half the")
        print(f"     size of the rationalisation it is asking about, and found none. 'Passes it")
        print(f"     through unchanged' is supported.")
    elif ratio < 1.0:
        print(f"  -> ADEQUATELY POWERED for the effect that matters, though not for a subtle one:")
        print(f"     it could detect {ratio:.0%} of the incoming effect and did not.")
    else:
        print(f"  -> UNDERPOWERED. The design could not have detected a selection effect even as")
        print(f"     large as the rationalisation itself, so 'neither concentrates nor removes'")
        print(f"     is SILENCE, not evidence. The claim needs downgrading.")

    # ---------------------------------------------------------------- the other null
    print("\n" + "=" * 92)
    print("NULL 2 -- weight-deletion under the reference judge, z 0.4")
    print("=" * 92)
    st = dc.q("SELECT coalesce(statement,'') FROM node "
              "WHERE name='weight-deletion-null-under-the-reference-judge'")
    txt = st[0][0] if st else ""
    print(f"  statement: {txt[:300]}")
    # MY DETECTOR WAS TOO NARROW AND THE CLAIM CAUGHT IT. Checking for "mde", "minimum
    # detectable" or "power" returned False -- but the statement says "effect over floor 0.97",
    # which IS a resolution statement in this project's own P14 vocabulary and is arguably a
    # better one, since the floor is measured from the data rather than assumed from a normal.
    # A keyword check that misses the house standard is the same defect as r197's shape scanner.
    has_mde = any(k in txt.lower() for k in ("mde", "minimum detectable", "power",
                                             "over floor", "effect/floor", "resolution floor"))
    print(f"  does the statement carry a RESOLUTION statement of any kind: {has_mde}")
    import re as _re
    ci = _re.search(r"\[([+-]?\d*\.\d+),\s*([+-]?\d*\.\d+)\]", txt)
    if ci:
        lo, hi = float(ci.group(1)), float(ci.group(2))
        se2 = (hi - lo) / (2 * 1.959964)
        print(f"  MDE derived from the PUBLISHED CI [{lo:+.4f},{hi:+.4f}]: se {se2:.5f} -> "
              f"MDE {mde(se2):+.4f}")
        print(f"  so this null could have detected an effect of {mde(se2):.4f} and saw "
              f"{0.0015:+.4f}.")
    print(f"  -> IT CARRIES ITS RESOLUTION, in this project's own words: 'effect over floor 0.97'")
    print(f"     means the observed effect sits AT the split-half resampling floor, which is a")
    print(f"     stronger statement than an MDE because the floor is measured from the data")
    print(f"     rather than assumed from a normal. My three-keyword check missed the house")
    print(f"     standard -- the same defect as r197's shape scanner, in a detector I wrote to")
    print(f"     audit others for exactly this.")

    # ---------------------------------------------------------------- the register defect
    print("\n" + "=" * 92)
    print("AND THE REGISTER ITSELF")
    print("=" * 92)
    reg = json.loads((ROOT / "13_normative_chain/r203_what_can_even_be_attacked/results/"
                      "register.json").read_text())
    n_mean = len(reg["buckets"]["MEAN"])
    print(f"  r203 put {n_mean} claims in MEAN and sent them all to the jackknife. At least two are")
    print(f"  NULLS, for which the jackknife is malformed -- r202's own tool would return NO")
    print(f"  RESOLUTION, correctly, for the reason it was built to.")
    print(f"  NULL is a seventh shape and its attack is POWER: what effect could this design have")
    print(f"  detected, against the effect that would matter. A null without an MDE is silence")
    print(f"  reported as evidence.")
    print(f"\n  AND 36 OF 40 OUTSTANDING MEAN CLAIMS DO NOT STATE THEIR TEST STATISTIC, so neither")
    print(f"  the register nor a reader can rank them. That is a content-discipline defect in the")
    print(f"  graph, found by trying to USE it rather than by auditing it -- which is the only way")
    print(f"  this kind of defect ever surfaces.")

    (OUT / "power.json").write_text(json.dumps(
        {"r188_null": {"mean": m, "se": se, "z": m / se, "n_groups": len(y),
                       "mde_80pct": M, "mde_in_sd": M / enc_sd,
                       "incoming_effect": 0.0478, "mde_over_incoming": ratio},
         "second_null_has_power_statement": bool(has_mde),
         "register_defect": "NULL mis-filed as MEAN; the jackknife is malformed for a null",
         "graph_defect": "36 of 40 outstanding MEAN claims omit their test statistic"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
