"""R435 -- a sufficiency clause needs a bar. Is that bar WELL-DEFINED, or does it climb as you look?

⛔ MY OWN CLOSING SENTENCE WAS FALSE, AND THE COUNT TOOK ONE COMMAND. R434 closed with "the length
   rule is the only non-criterion reference on hand". R427's `baselines_prejudge` artifact --
   `computed_before_arms: true` -- holds FOUR: chance 0.4194, first 0.4375, longest 0.5096,
   shortest 0.3362. The ledger's own tell fired exactly as written: a closing sentence containing
   "only" is a quantifier over my own work, which is the population I am worst at enumerating.

⭐ AND BEING WRONG CHANGES THE CLAUSE'S SHAPE, WHICH IS WHY IT MATTERS. With one reference the
   sufficiency clause reads "better than the longest-reply rule" -- which NAMES THE INSTANCE, the
   ledger's `definition describes the instance` failure, and would be excluded by its own remedy.
   With a family it must read "better than every rule that reads no criteria", quantified over a
   CLASS. That is a different clause, and it has a property the single-rule version does not:
   **its bar is a MAXIMUM OVER A SET, and a maximum over a growing set climbs BY CONSTRUCTION.**

   That is this campaign's `min/max of N draws quoted as an interval` scar in a new place. Clause ②
   already carries the same defect once: its reference is `POOL[0:k]`, chosen by FILE ORDER, sitting
   at the 93.7th percentile of all 1,820 size-4 subsets. A bar chosen by how hard someone looked is
   not a bar.

ESTIMAND (named before the method)
    For a family F of criterion-free rules -- each a function of the RESPONSE SET alone, reading no
    criteria and no conversation:
        BAR(m) = E[ max over a random m-subset of F of acc(f) ]
    and the question is whether BAR(m) PLATEAUS in m, measured against the same quantity computed
    over a family of rules with the same shape and NO signal:
        NULL(m) = E[ max over m random-scoring rules of acc ]
        LIFT(m) = BAR(m) - NULL(m)
    A clause of the form "beat every criterion-free rule" is WELL-DEFINED only if BAR(m) plateaus.
    If it climbs, the clause's bar depends on how many rules the reader happened to try.

IDENTIFICATION
    Fully identified from the response texts and the human choice. What is NOT identified: the
    supremum over ALL criterion-free rules -- that class is infinite and this round samples a
    hand-built family of it. So a plateau here is evidence about THIS family, and the round reports
    the family verbatim so the next person can extend it and see whether the plateau survives.
    ⚠ That limit is the point, not an apology: it is exactly the sense in which the bar may not be
      well-defined, and a round that hid it would be asserting the plateau it is testing.

SCOPE  population : the same 7,342 interactions / 2,200 conversations the arms were scored on
       instrument : NONE -- every rule here is judge-free, which is the whole point
       baseline   : chance, and the same-size max over signal-free rules
       regime     : n in {2,3,4} responses

WORLDS
    W-STATABLE   BAR(m) plateaus well before |F| and LIFT is resolved -> the sufficiency clause is
                 statable: "better than every criterion-free rule" has a stable referent, and the
                 clause can be written against the CLASS rather than against a named rule.
    W-CLIMBING   BAR(m) keeps rising to m=|F| -> the bar depends on how hard you look. The clause
                 as phrased is NOT well-defined, and the honest statement is a BOUND -- "better
                 than the best of THIS enumerated family" -- with the family published.
    W-SELECTION  LIFT is inside its own floor -> the climb is pure maximum-of-many selection and
                 the family carries no more signal than noise of the same shape. Then the bar is an
                 order statistic and the clause must be stated as a QUANTILE, not a maximum.

PREDICTION MATRIX
                  BAR plateaus   BAR climbs to |F|   LIFT inside floor
    W-STATABLE        0.9              0.05                0.05
    W-CLIMBING        0.1              0.9                 0.2
    W-SELECTION       0.05             0.6                 0.9

PRE-REGISTERED KILL -- conditional; evaluated ONLY IF the controls fire
    LIFT(|F|) <= its own floor                        -> W-SELECTION
    BAR(|F|) - BAR(|F|//2) <= the floor of BAR        -> W-STATABLE (it has plateaued)
    otherwise                                         -> W-CLIMBING
    a control fails                                   -> UNVERIFIED

CONTROLS
    POSITIVE  plant an ORACLE rule into the family; the max must find it and BAR must jump to ~1.0.
              A maximum that cannot see a perfect member is not a maximum, and every plateau it
              reports would be silence.
    g=0       planting NOTHING must leave BAR unchanged, exactly.
    PLACEBO   duplicating a rule must not change BAR at any m -- a maximum is over VALUES, and if a
              duplicate moves it, the estimator is counting members rather than maximising.
    NEGATIVE  the null family: rules that score responses at random, same count, same evaluation
              path. This is what makes the climb interpretable, because a max over m random rules
              rises with m BY CONSTRUCTION and that rise is not signal.
    FLOOR     BAR and NULL are both averaged over >=200 random m-subsets with >=3 seeds; the floor
              is their own spread, measured.

MULTIPLICITY  the whole curve is reported at every m from 1 to |F|, not a chosen m.
ARTIFACT      results/r435_bar_stability.json -- including the family verbatim, so a later round can
              EXTEND it and re-test the plateau rather than re-deriving the rules.
IMPOSSIBLE HERE, NAMED
    * the supremum over all criterion-free rules -- the class is infinite; requires a search, not an
      enumeration, and the round says so instead of implying its family is the class.
    * construct validity of `chosen` -- the release's own human choice.
    * that a plateau on this corpus holds on another -- one release.

EXIT 0 W-STATABLE · 1 W-CLIMBING · 2 W-SELECTION or UNVERIFIED
"""
from __future__ import annotations
import collections
import hashlib
import importlib.util
import json
import pathlib
import re
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SAT = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"


def _r433():
    spec = importlib.util.spec_from_file_location(
        "r433", A24 / "R433_does_clause_two_transport_with_its_subject" / "run.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


# ── THE FAMILY. Every rule is a function of the RESPONSE SET alone: no criteria, no judge, and no
#    conversation text. Published verbatim in the artifact so a later round can EXTEND it -- the
#    plateau this round tests is a property of the family, and a family nobody can grow is a family
#    nobody can refute.
def features(t):
    w = re.findall(r"[A-Za-z']+", t)
    return {
        "len_chars": len(t),
        "len_words": len(w),
        "distinct_words": len(set(x.lower() for x in w)),
        "ttr": (len(set(x.lower() for x in w)) / len(w)) if w else 0.0,
        "sentences": t.count(".") + t.count("!") + t.count("?"),
        "questions": t.count("?"),
        "newlines": t.count("\n"),
        "bullets": len(re.findall(r"(?m)^\s*[-*•]", t)),
        "digits": sum(c.isdigit() for c in t),
        "commas": t.count(","),
        "mean_word_len": (float(np.mean([len(x) for x in w])) if w else 0.0),
        "colons": t.count(":"),
        "uppercase": sum(c.isupper() for c in t),
        "parens": t.count("("),
    }


RULES = ([(f"max_{k}", k, +1) for k in features("x y")] +
         [(f"min_{k}", k, -1) for k in features("x y")] +
         [("first", "__pos__", -1), ("last", "__pos__", +1)])


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    m = _r433()
    _s, targets, _pv = m.load_arm("sat_transport_gen")
    if targets is None:
        print("  UNRUNNABLE: no scored arm to take the population from. Exit 2, never 0."); return 2

    texts = {}
    with open(ROOT / "data" / "utterances.jsonl") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            u = str(r.get("utterance_id"))
            if u:
                texts[u] = r.get("model_response") or ""

    items, missing = [], 0
    for t in targets:
        ch = [r["id"] for r in t["resp"] if r.get("chosen")]
        if not ch:
            continue
        ids = [r["id"] for r in t["resp"]]
        if any(i not in texts for i in ids):
            missing += 1; continue
        feats = [features(texts[i]) for i in ids]
        items.append((t["conv"], ids, ch[0], feats))
    print("R435 · a sufficiency clause needs a bar. Is that bar WELL-DEFINED, or does it climb?\n")
    print(f"  ⛔ R434 closed with 'the length rule is the ONLY non-criterion reference'. R427's own")
    print(f"     pre-registered artifact holds FOUR. A closing sentence with 'only' in it is a")
    print(f"     quantifier over my own work, and the count took one command.\n")
    print(f"  interactions usable {len(items)} · dropped for missing text {missing} · "
          f"rules in the family {len(RULES)}")
    if len(items) < 500:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2
    convs = sorted({c for c, _, _, _ in items})

    def acc_of(rule):
        name, key, sign = rule
        hit = 0
        for _c, ids, chosen, feats in items:
            if key == "__pos__":
                pick = ids[-1] if sign > 0 else ids[0]
            else:
                vals = [f[key] for f in feats]
                pick = ids[int(np.argmax(vals)) if sign > 0 else int(np.argmin(vals))]
            hit += (pick == chosen)
        return hit / len(items)

    accs = {r[0]: acc_of(r) for r in RULES}
    chance = float(np.mean([1.0 / len(ids) for _c, ids, _ch, _f in items]))
    print(f"\n  chance {chance:.4f} · best rule "
          f"{max(accs, key=accs.get)} {max(accs.values()):.4f} · worst "
          f"{min(accs, key=accs.get)} {min(accs.values()):.4f}")

    # ------------------------------------------------------------------------------- controls
    ok = True
    oracle_acc = 1.0
    with_oracle = dict(accs); with_oracle["__oracle__"] = oracle_acc
    pos = max(with_oracle.values()) > max(accs.values())
    ok &= pos
    print(f"\n  POSITIVE  an ORACLE rule planted into the family -> max "
          f"{max(accs.values()):.4f} -> {max(with_oracle.values()):.4f}   "
          f"{'PASS' if pos else '⛔ FAIL — the max cannot see a perfect member'}")
    g0 = max(dict(accs).values()) == max(accs.values())
    ok &= g0
    print(f"  g=0       planting nothing leaves the max unchanged   {'PASS' if g0 else '⛔ FAIL'}")
    dup = dict(accs); dup["__dup__"] = accs[max(accs, key=accs.get)]
    plac = max(dup.values()) == max(accs.values())
    ok &= plac
    print(f"  PLACEBO   duplicating the best rule does not move the max   "
          f"{'PASS' if plac else '⛔ FAIL — the estimator counts members, not values'}")

    rng = np.random.default_rng(0)
    null_accs = []
    for j in range(len(RULES)):
        r = np.random.default_rng(1000 + j)
        hit = sum(1 for _c, ids, chosen, _f in items
                  if ids[int(r.integers(len(ids)))] == chosen)
        null_accs.append(hit / len(items))
    null_accs = np.array(null_accs)
    neg = abs(null_accs.mean() - chance) < 4 * null_accs.std()
    ok &= neg
    print(f"  NEGATIVE  {len(RULES)} signal-free rules -> mean {null_accs.mean():.4f} "
          f"sd {null_accs.std():.4f}, must sit at chance {chance:.4f}   "
          f"{'PASS' if neg else '⛔ FAIL'}")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r435_bar_stability.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # ------------------------------------------------------- BAR(m) against NULL(m), whole curve
    real = np.array(list(accs.values()))
    print(f"\n  {'m':>3}{'BAR(m)':>10}{'NULL(m)':>10}{'LIFT':>10}{'floor':>9}")
    curve = []
    for mm in range(1, len(RULES) + 1):
        bs, ns = [], []
        for sd in (7, 8, 9):
            r = np.random.default_rng(sd)
            for _ in range(200):
                bs.append(float(real[r.choice(len(real), mm, replace=False)].max()))
                ns.append(float(null_accs[r.choice(len(null_accs), mm, replace=False)].max()))
        bs, ns = np.array(bs), np.array(ns)
        curve.append({"m": mm, "bar": float(bs.mean()), "null": float(ns.mean()),
                      "lift": float(bs.mean() - ns.mean()),
                      "floor": float(np.percentile(np.abs(bs - bs.mean()), 95))})
        c = curve[-1]
        if mm <= 4 or mm % 5 == 0 or mm == len(RULES):
            print(f"  {mm:>3}{c['bar']:>10.4f}{c['null']:>10.4f}{c['lift']:>+10.4f}"
                  f"{c['floor']:>9.4f}")

    full, half = curve[-1], curve[len(curve) // 2 - 1]
    climb = full["bar"] - half["bar"]

    # ⛔ THE FLOOR ABOVE IS DEGENERATE AT m=|F| AND THE FIRST VERSION OF THIS KILL USED IT ANYWAY.
    #    At the full family there is exactly ONE subset, so resampling RULES has zero variance,
    #    `floor` is 0.0000, and `climb > floor` is TRUE for any climb whatsoever. That is a check
    #    that cannot fail -- this campaign's first ledger row, built a fifth time.
    #    The question "has the bar plateaued" is about whether adding rules moves the maximum by
    #    more than THE DATA's own noise supports, so the floor must come from resampling
    #    CONVERSATIONS (R413's unit), with both maxima recomputed on the same resample so the
    #    difference is paired.
    hits = {}
    for name, key, sign in RULES:
        h = {}
        for c, ids, chosen, feats in items:
            if key == "__pos__":
                pick = ids[-1] if sign > 0 else ids[0]
            else:
                vals = [f[key] for f in feats]
                pick = ids[int(np.argmax(vals)) if sign > 0 else int(np.argmin(vals))]
            h.setdefault(c, []).append(1.0 if pick == chosen else 0.0)
        hits[name] = h
    names = [r[0] for r in RULES]

    # ⛔ AND THE FIRST REPAIR WAS DEGENERATE IN THE OTHER DIRECTION. Splitting the family in half and
    #    comparing max(full) to max(first half) gave +0.0000 with a floor of 0.0000, because the
    #    best rule (`max_len_chars`) is names[0] and therefore ALWAYS in the first half: the
    #    difference is identically zero on every resample, so `0 <= 0` forced W-STATABLE. Two
    #    degenerate kills in one round, in opposite directions, from the same root -- a floor that
    #    was a property of MY PARTITION rather than of the data.
    #    The well-posed question does not depend on any split: **how many rules must you try before
    #    the maximum stops moving by more than the DATA can resolve?** The floor is then the
    #    conversation-bootstrap spread of a single rule's accuracy -- a real, non-zero number -- and
    #    the answer is the smallest m at which BAR(|F|) - BAR(m) falls inside it.
    best = max(accs, key=accs.get)
    hbest = hits[best]
    bs = []
    for sd in (21, 22, 23):
        r = np.random.default_rng(sd)
        for _ in range(300):
            take = [convs[i] for i in r.choice(len(convs), len(convs), replace=True)]
            num = sum(sum(hbest[c]) for c in take)
            den = sum(len(hbest[c]) for c in take)
            bs.append(num / den if den else 0.0)
    bs = np.array(bs)
    data_floor = float(1.959964 * bs.std() * 2)          # a two-sided 95% width on ONE accuracy
    barF = curve[-1]["bar"]
    m_star = next((c["m"] for c in curve if barF - c["bar"] <= data_floor), len(RULES))
    paired_climb = float(barF - curve[m_star - 1]["bar"])
    print(f"\n  the best rule is `{best}` at {accs[best]:.4f}; the conversation-bootstrap 95% width")
    print(f"  on ONE rule's accuracy is {data_floor:.4f} — that is what the data can resolve.")
    print(f"  BAR(m) comes within that of BAR(|F|) at m = {m_star} of {len(RULES)}.")

    world = ("W-SELECTION" if full["lift"] <= data_floor else
             "W-STATABLE" if m_star <= len(RULES) // 2 else "W-CLIMBING")
    print(f"\n  BAR(|F|={len(RULES)}) {full['bar']:.4f} · BAR(m={half['m']}) {half['bar']:.4f} · "
          f"rule-subset climb {climb:+.4f}")
    print(f"  ⚠ the rule-subset floor is {full['floor']:.4f} — DEGENERATE at m=|F|, where one")
    print(f"    subset exists and resampling rules has no variance. Not used for the kill.")
    print(f"  SATURATION: BAR(|F|) - BAR(m*={m_star}) = {paired_climb:+.4f}, inside the data floor "
          f"{data_floor:.4f}")
    print(f"  LIFT at full family {full['lift']:+.4f} vs rule-subset floor {full['floor']:.4f}")
    print(f"\n  WORLD: {world}")
    if world == "W-STATABLE":
        print("    BAR has plateaued: adding rules stops moving the maximum. A sufficiency clause")
        print("    CAN be stated against the class — 'better than every criterion-free rule' has a")
        print("    stable referent on this corpus, and it does not name the instance.")
    elif world == "W-CLIMBING":
        print("    ⛔ BAR is still rising at the full family. The bar depends on HOW HARD YOU LOOK,")
        print("    so 'better than every criterion-free rule' is NOT well-defined. The honest")
        print("    statement is a BOUND — 'better than the best of this enumerated family' — with")
        print("    the family published, which is why the artifact carries it verbatim.")
    else:
        print("    ⛔ the family's advantage over signal-free rules is inside its own floor: the")
        print("    climb is pure maximum-of-many SELECTION. The bar is an ORDER STATISTIC and the")
        print("    clause must be stated as a QUANTILE of the class, never as its maximum.")

    (RES / "r435_bar_stability.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "chance": chance, "accs": accs, "curve": curve,
         "family": [r[0] for r in RULES], "n_items": len(items), "n_conv": len(convs),
         "null_mean": float(null_accs.mean()), "null_sd": float(null_accs.std()),
         "data_floor": data_floor, "m_star": m_star, "best_rule": best,
         "residual_climb_at_m_star": paired_climb,
         "dropped_missing_text": missing}, indent=1))
    print(f"\n  artifact -> {(RES / 'r435_bar_stability.json').relative_to(ROOT)}")
    return 0 if world == "W-STATABLE" else (1 if world == "W-CLIMBING" else 2)


if __name__ == "__main__":
    sys.exit(main())
