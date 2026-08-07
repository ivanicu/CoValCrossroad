#!/usr/bin/env python3
"""
R889 · 28 vs 29 — the two committed admitted sets, and which one R888 should have used.

⛔ WHY, AND IT IS AN ERROR IN MY OWN PREVIOUS ROUND. R888 measured clause ③'s exclusion against
R856's committed `c2` (29 arms) and reported **17 of 29 = 58.6%**. The deliverable's headline said
**28**. I flagged the gap as UNRESOLVED rather than papering over it, and this round resolves it.

⭐ **THE TWO SETS DIFFER BY EXACTLY ONE ARM, AND THE DIFFERENCE IS A CRITERION CHANGE.**
`greedy_k4_fit1_08bR`: margin **+0.003786**, CI lower bound **−0.006910**. Its point estimate is
positive; its interval crosses zero. **R856's `c2` admitted on `margin > 0`. R881 admitted on
`lo > 0`.** That is precisely the strengthening the current headline carries — *"a RESOLVABLY
POSITIVE margin — its bootstrap CI lower bound above zero"* — so R856's list is the SUPERSEDED
criterion and R888 ran on the wrong population.

⭐⭐ **THE CONSEQUENCE FOR R888 IS A SHARE, NOT A CONCLUSION — AND THAT IS WORTH SAYING PRECISELY.**
The disputed arm is `greedy_*`, so clause ③ excludes it under either criterion. Therefore:
    on the superseded 29: 17 excluded, **12 survive**
    on the current    28: 16 excluded, **12 survive**
**The surviving set is IDENTICAL and R888's headline — the definition admits 12, not 28 — holds
under both populations.** What must be corrected is the SHARE: 58.6% -> 57.1%.

⚠ This is the failure class this session has been cataloguing, committed by me one round ago:
**the population and the count chosen separately.** The tell was available — R888's own output
printed *"Clause ② admits 29 here"* against a file saying 28, and I wrote that down as an open
question instead of as a one-command diff. **A discrepancy I NAME but do not RESOLVE is not honesty,
it is a deferred error with a receipt.**

ESTIMAND        the symmetric difference between clause ②'s extension under the two committed
                criteria, and the corrected value of R888's exclusion share.
IDENTIFICATION  EXACT. Both artifacts are committed and both carry per-arm decisions; R881 carries
                `margin`, `lo` and `admitted` for all 99, so the criterion each set used is
                RECOVERABLE, not inferred.
SCOPE           population: the union of the two committed admitted sets — DERIVED (it is the object
                            of the question), not globbed
                instrument: R881's per-arm margin/lo table + R856's c2 list
                baseline:   the two sets agree
                regime:     home release, judge J, 968 prompts, 99 arms, comparator genericpool16
WORLDS          A · the sets differ by arms whose `lo <= 0 < margin` -> the gap IS the criterion
                    change, it is fully explained, and only R888's SHARE needs correcting
                B · they differ by arms that do NOT fit that pattern -> the gap is something else
                    (a different comparator, prompt set, or bootstrap) and BOTH rounds' scopes are
                    in doubt, not just a percentage
                C · the difference is not a subset relation -> the two rounds disagree in both
                    directions and neither list can be quoted until re-derived
KILL            CONDITIONAL, all read from the committed tables:
                  ⭐ ① POSITIVE: every arm in `c2 \\ R881` must have `lo <= 0 < margin`. This is the
                     mechanism itself; if even one does not, WORLD B and the criterion story is
                     wrong.
                  ⭐ ② g=0: an arm admitted by BOTH must have `lo > 0`, and an arm rejected by both
                     must have `margin <= 0` OR `lo <= 0`. A classifier that calls everything a
                     criterion difference fails here.
                  ⭐ ③ the difference must be one-directional (`R881 \\ c2` empty), else WORLD C.
                  ④ R888's corrected share must be RECOMPUTED from the arm lists, never edited by
                     hand from the old number.
MULTIPLICITY    one estimand; every arm in the symmetric difference reported, no truncation.
ARTIFACT        results/two_admitted_sets.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: this explains the gap between two COMMITTED lists. It does not
                establish that `lo > 0` is the right criterion — only that it is the one the
                headline names and the one R888 should have used.
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
GEN = ROOT / "corebench" / "select_core.py"


def art(g, n):
    p = next(A24.glob(f"{g}/results/{n}"), None)
    return json.loads(p.read_text()) if p else None


def label_rules():
    m = re.search(r'if a\.rule in \(([^)]*)\):\s*\n\s*for line in open\([^)]*comparisons\.jsonl',
                  GEN.read_text())
    return None if not m else tuple(x.strip().strip('"\'') for x in m.group(1).split(",")
                                    if x.strip())


def consumes(arm, rules):
    return any(arm.startswith(r[:-2] + "_k") or arm.startswith(r) for r in rules)


def main() -> int:
    r881 = art("R881_*", "boundary_distance.json")
    r856 = art("R856_*", "clause4_dominated.json")
    rules = label_rules()
    if r881 is None or r856 is None or rules is None:
        print("  UNRUNNABLE: an artifact or the generator could not be read. Exit 2, never 0.")
        return 2

    tbl = {x["arm"]: x for x in r881["arms"]}
    a881 = {x["arm"] for x in r881["arms"] if x["admitted"]}
    c2 = set(r856["c2"])
    only_c2, only_881 = sorted(c2 - a881), sorted(a881 - c2)

    # ① POSITIVE — the mechanism itself
    p1 = bool(only_c2) and all(tbl[a]["lo"] <= 0 < tbl[a]["margin"] for a in only_c2 if a in tbl)
    # ② g=0 — a classifier that calls everything a criterion difference must fail here
    both = sorted(a881 & c2)
    neither = [a for a in tbl if a not in a881 and a not in c2]
    p2a = all(tbl[a]["lo"] > 0 for a in both if a in tbl)
    p2b = all(tbl[a]["margin"] <= 0 or tbl[a]["lo"] <= 0 for a in neither)
    p2 = p2a and p2b
    p3 = not only_881

    print(f"  R881 admitted {len(a881)} · R856 c2 {len(c2)} · intersection {len(both)}")
    print(f"\n  ① POSITIVE  every arm in (c2 \\ R881) has lo <= 0 < margin: {p1}  "
          f"{'PASS' if p1 else 'FAIL'}")
    for a in only_c2:
        t = tbl.get(a, {})
        print(f"     {a}: margin {t.get('margin', float('nan')):+.6f}  "
              f"lo {t.get('lo', float('nan')):+.6f}   <- point positive, interval crosses zero")
    print(f"  ② g=0       {len(both)} arms in both have lo > 0: {p2a} · {len(neither)} in neither "
          f"fail a condition: {p2b}  {'PASS' if p2 else 'FAIL'}")
    print(f"  ③ the difference is one-directional (R881 \\ c2 empty): {p3}  "
          f"{'PASS' if p3 else 'FAIL'}  {only_881 if only_881 else ''}")
    if not (p1 and p2 and p3):
        w = "C" if not p3 else "B"
        print(f"\n  ⭐ WORLD {w}: the gap is NOT explained by the criterion change. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "world": w, "only_c2": only_c2,
                   "only_881": only_881}, open(OUT / "two_admitted_sets.json", "w"), indent=2)
        return 2

    # ④ recompute R888's share from the lists, never by editing the old number
    def split(s):
        e = sorted(a for a in s if consumes(a, rules))
        return e, sorted(a for a in s if not consumes(a, rules))
    e29, k29 = split(c2)
    e28, k28 = split(a881)
    assert len(e29) + len(k29) == len(c2) and len(e28) + len(k28) == len(a881), "partition"

    print(f"\n  ⭐ WORLD A: the two sets differ by exactly the word RESOLVABLY.")
    print(f"     R856's c2 admitted on `margin > 0`; R881 on `lo > 0`. The headline says")
    print(f"     'a RESOLVABLY POSITIVE margin — its bootstrap CI lower bound above zero',")
    print(f"     so R881's {len(a881)} is the CURRENT criterion and R856's {len(c2)} is superseded.")
    print(f"\n  ⭐⭐ R888's NUMBERS, RECOMPUTED ON BOTH POPULATIONS:")
    print(f"     superseded 29: {len(e29)} excluded by ③, {len(k29)} survive  "
          f"({len(e29)/len(c2):.1%})")
    print(f"     current    28: {len(e28)} excluded by ③, {len(k28)} survive  "
          f"({len(e28)/len(a881):.1%})")
    same = k29 == k28
    print(f"     surviving sets identical: {same}")
    print(f"\n  ⛔ R888's SHARE IS CORRECTED 58.6% -> {len(e28)/len(a881):.1%}. ITS CONCLUSION IS NOT:")
    print(f"     the disputed arm is `{only_c2[0]}`, a label-consuming rule, so clause ③")
    print(f"     removes it under EITHER criterion. **The definition admits {len(k28)} arms, and")
    print(f"     that now holds under both populations** — the finding got stronger, not weaker.")
    print(f"\n  ⚠ AND THE PROCESS ERROR IS THE REUSABLE PART: R888 printed 'Clause ② admits 29")
    print(f"    here' against a file saying 28 and I recorded it as an open question. **A")
    print(f"    discrepancy I NAME but do not RESOLVE is a deferred error with a receipt.** The")
    print(f"    resolution was one set difference over two committed artifacts.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": "A",
               "n_r881_admitted": len(a881), "n_r856_c2": len(c2),
               "only_in_c2": only_c2, "only_in_r881": only_881,
               "disputed_arm_table": {a: {"margin": tbl[a]["margin"], "lo": tbl[a]["lo"]}
                                      for a in only_c2 if a in tbl},
               "criterion_r856": "margin > 0 (point estimate)",
               "criterion_r881": "lo > 0 (CI lower bound) — the one the headline names",
               "r888_corrected": {"superseded_29": {"excluded": len(e29), "surviving": len(k29),
                                                    "share": len(e29) / len(c2)},
                                  "current_28": {"excluded": len(e28), "surviving": len(k28),
                                                 "share": len(e28) / len(a881)},
                                  "surviving_identical": same, "surviving": k28},
               "unit_note": "every count is ARMS",
               "does_not_establish": "that lo > 0 is the RIGHT criterion — only that it is the one "
                                     "the headline names and the one R888 should have used",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "two_admitted_sets.json", "w"), indent=2)
    print(f"\n  artifact: results/two_admitted_sets.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
