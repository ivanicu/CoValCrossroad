"""R1056 — q needs a family of 10. The certified family is 2. Can it be grown, or is q permanently inert?

R1055 established by arithmetic that `need(q=90) = ceil(0.9k)` equals `need(q=100) = k` for every
family size k < 10, so the clause's q parameter distinguishes nothing at the current family of 2.

⛔ THE OBVIOUS RELAXATION IS THE WRONG ONE, AND CHECKING SAVED THE ROUND. R918 stores two per-arm
   properties and they are NOT nested: `fixed` = the arm's criterion selection is LITERALLY IDENTICAL
   on every prompt (2 arms), and `exact` = the share of prompts where the selection is a subset of
   the full rubric (86 arms at 1.0). Sweeping `exact` looks like relaxing certification and is not —
   it is a different question, and every threshold from 0.01 to 1.0 returns the same 86.

⭐ THE REAL RELAXATION OF `fixed` IS SELECTION DIVERSITY: how many DISTINCT selections does an arm
   use across the prompts, and what share do its most common ones cover? `fixed` is the k=1 cell of
   that curve. This round computes the curve and asks whether ANY defensible cell yields a family of
   10 — and if one does, whether an arm at that cell is still prompt-BLIND in any meaningful sense.

ESTIMAND        the size of the certified family as a function of the prompt-blindness threshold, and
                whether any threshold reaches the k=10 that makes q testable
IDENTIFICATION  exact over the arms with a committed selection file. ⚠ Reaching 10 is necessary for q
                to bite; it is not sufficient for the resulting family to be LEGITIMATE, which is a
                definitional question this round surfaces rather than settles.
SCOPE           population : arms with a core_<arm>.json selection on disk
                instrument : distinct-selection count and modal-selection coverage per arm
                baseline   : the current certified family, |family| = 2
                regime     : this release, 968 prompts
WORLDS          A THE FAMILY CAN BE GROWN — some threshold on selection diversity yields >= 10 arms,
                  so q is testable after a stated relaxation, and the clause should either adopt that
                  relaxation or drop q.
                B q IS PERMANENTLY INERT IN THIS RELEASE — the distribution is bimodal, with a tiny
                  blind set and a large prompt-conditioned one and nothing between, so no defensible
                  threshold reaches 10 and the clause declares a parameter this release cannot
                  exercise at all.
                prediction matrix: A -> a threshold with family >= 10 exists and is not absurd
                                   B -> family jumps from ~2 straight past any usable middle
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      some threshold gives 10 <= family < half the population -> World A, name it
                      otherwise                                              -> World B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   at the strictest cell (1 distinct selection) the family must be EXACTLY R918's
                `fixed` set — the two known comparators. If the curve's own endpoint disagrees with
                the committed typing, the selection loader is reading something else.
NEGATIVE CTRL   at the most permissive cell every typed arm must be in the family, or the sweep is
                not a sweep.
PLACEBO         an arm with no selection file contributes nothing and is COUNTED as untypable, never
                silently dropped.
NOISE FLOOR     N/A - the counts are exact over committed text. Stated rather than omitted.
MULTIPLICITY    the whole curve is reported, not the cell that fires.
SEEDS           N/A - deterministic.
IMPOSSIBLE      whether an arm using few-but-more-than-one selections is prompt-BLIND in the sense
                the clause intends. That is a definitional choice, not a measurement.
                SETTLES: OUT-OF-RELEASE for the concept; IN-RELEASE for its consequences, since each
                candidate family can be run through the operator.
"""
import json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
R918 = next(ROOT.glob("E05_the_space_of_compilers/A25*/R918_*/results/"
                      "typing_specification_curve.json"), None)
K_NEEDED = 10          # from R1055: ceil(0.9k) < k first holds at k = 10


def main() -> int:
    if R918 is None:
        print("  UNRUNNABLE: R918's typing artifact is missing. Exit 2, never 0."); return 2
    typed = json.loads(R918.read_text())["properties"]
    committed_fixed = {a for a, p in typed.items() if p.get("fixed")}

    rows, untypable = {}, []
    for arm in sorted(typed):
        f = RES / f"core_{arm}.json"
        if not f.exists():
            untypable.append(arm); continue
        try:
            sel = json.loads(f.read_text())
        except Exception:
            untypable.append(arm); continue
        sets = [frozenset(v) for v in sel.values() if v]
        if len(sets) < 50:
            untypable.append(arm); continue
        cnt = {}
        for s in sets:
            cnt[s] = cnt.get(s, 0) + 1
        top = sorted(cnt.values(), reverse=True)
        rows[arm] = {"n_prompts": len(sets), "n_distinct": len(cnt),
                     "modal_share": top[0] / len(sets),
                     "top2_share": sum(top[:2]) / len(sets)}
    if len(rows) < 20:
        print("  UNRUNNABLE: too few arms have a selection file. Exit 2, never 0."); return 2
    print(f"  ⭐ arms with a committed selection {len(rows)} · untypable and NAMED {len(untypable)}: "
          f"{sorted(untypable)[:6]}")

    strict = {a for a, v in rows.items() if v["n_distinct"] == 1}
    pos = strict == (committed_fixed & set(rows))
    permissive = {a for a, v in rows.items() if v["n_distinct"] <= max(v["n_prompts"] for v in
                                                                      rows.values())}
    neg = permissive == set(rows)
    print(f"  POSITIVE — the strictest cell must equal R918's committed `fixed` set: {pos}  "
          f"({sorted(strict)} vs {sorted(committed_fixed & set(rows))})")
    print(f"  NEGATIVE — the most permissive cell must contain every typed arm: {neg}")
    if not (pos and neg):
        print("  the sweep does not reproduce the committed typing. Exit 2, never 0."); return 2

    print(f"\n  ⭐ CERTIFICATION CURVE — family size as the blindness threshold relaxes")
    curve = []
    for k in (1, 2, 3, 5, 10, 25, 50, 100, 250, 500, 1000):
        fam = sorted(a for a, v in rows.items() if v["n_distinct"] <= k)
        curve.append({"rule": f"n_distinct <= {k}", "family": len(fam),
                      "reaches_q": len(fam) >= K_NEEDED,
                      "share_of_population": len(fam) / len(rows)})
        print(f"     n_distinct <= {k:<5} family {len(fam):>3} of {len(rows)}  "
              f"({len(fam) / len(rows):.3f})  reaches q@{K_NEEDED}: {len(fam) >= K_NEEDED}")
    for m in (1.0, 0.95, 0.9, 0.75, 0.5, 0.25):
        fam = sorted(a for a, v in rows.items() if v["modal_share"] >= m)
        curve.append({"rule": f"modal_share >= {m}", "family": len(fam),
                      "reaches_q": len(fam) >= K_NEEDED,
                      "share_of_population": len(fam) / len(rows)})
        print(f"     modal_share >= {m:<5} family {len(fam):>3} of {len(rows)}  "
              f"({len(fam) / len(rows):.3f})  reaches q@{K_NEEDED}: {len(fam) >= K_NEEDED}")

    usable = [c for c in curve if c["reaches_q"] and c["share_of_population"] < 0.5]
    print()
    if usable:
        best = min(usable, key=lambda c: c["family"])
        world = (f"⭐ A THE FAMILY CAN BE GROWN — the smallest rule reaching q's threshold while "
                 f"staying under half the population is `{best['rule']}`, giving a family of "
                 f"{best['family']} of {len(rows)} ({best['share_of_population']:.3f}). So q is "
                 f"testable AFTER a stated relaxation, and the clause must either adopt that "
                 f"relaxation explicitly or drop q. ⚠ Reaching 10 is NECESSARY for q to bite and "
                 f"NOT SUFFICIENT for the family to be legitimate: an arm using several selections "
                 f"conditions on the prompt, just coarsely.")
    else:
        world = (f"⛔ B q IS PERMANENTLY INERT IN THIS RELEASE — no rule on the curve reaches a "
                 f"family of {K_NEEDED} while remaining under half the population. The distribution "
                 f"is bimodal: a tiny genuinely blind set and a large prompt-conditioned one, with "
                 f"nothing usable between. The clause declares a parameter this release cannot "
                 f"exercise at any defensible threshold.")
    print(world)
    print(f"⛔ AND `exact` IS NOT THE KNOB, WHICH IS WHY THIS ROUND DID NOT SWEEP IT. R918's `exact`")
    print(f"   asks whether a selection is a SUBSET OF THE RUBRIC; `fixed` asks whether it is the")
    print(f"   SAME ACROSS PROMPTS. 86 arms sit at exact = 1.0 and 2 at fixed, and every threshold")
    print(f"   from 0.01 to 1.0 on `exact` returns the same 86. Two properties, one field name away")
    print(f"   from each other, and sweeping the wrong one would have manufactured a family of 86.")

    o = HERE / "results" / "certification_curve.json"
    o.write_text(json.dumps({
        "round": "R1056", "arms": len(rows), "untypable": sorted(untypable),
        "k_needed_for_q": K_NEEDED, "committed_fixed": sorted(committed_fixed),
        "curve": curve, "usable_rules": usable, "world": world,
        "controls": {"positive_strictest_equals_committed": bool(pos),
                     "negative_permissive_is_everything": bool(neg)},
        "limitation": "reaching the size q needs is necessary, never sufficient: an arm using few "
                      "but more than one selection still conditions on the prompt",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
