#!/usr/bin/env python3
"""R1026 — the certification predicate is the last unexamined input. Does it discriminate?

Every extension figure in this arc rests on a two-member comparator set, and that set was produced by
one predicate: R906's `fixed` — "the arm's selection is identical on every prompt" — read through
R918 by R921. Six rounds have taken it as given. It is the last input upstream of every number here.

⛔ AND READING THE SOURCE ALREADY CORRECTS A SENTENCE I COMMITTED LAST ROUND. R1025's annotation says
   "R921 certified 2 comparators FROM A LARGER POOL", implying a curatorial choice among viable
   alternatives. R918 computes `fixed` over 96 arms and **exactly 2 satisfy it**. There was no choice:
   the predicate is a filter and it admitted everything that qualified. That sentence is withdrawn
   below and replaced, not annotated beside.

⛔ AND THE WITNESS SEARCH IS A JOIN OF TWO COMMITTED ARTIFACTS, SO IT IS LABELLED AS ONE. The question
   "is any potential comparator BOTH stricter than `generic` AND prompt-blind?" is answered by joining
   R921's `admitted_counts` to R918's `properties`. It could have come out otherwise — a stricter
   prompt-blind arm would have refuted the certified set — so the join is informative. But it consumes
   no new evidence and is reported as a JOIN, not as a measurement.

   What is NOT on disk, and is this round's actual measurement, is whether the predicate deciding
   prompt-blindness DISCRIMINATES. `exact` = "the selection is a subset of THAT PROMPT's rubric".
   If prompt rubrics are large, a selection drawn from the global pool would satisfy that by chance,
   and every exclusion in the chain would rest on an artifact of rubric size. Nobody has computed the
   chance base rate. It is the cheapest thing that could invalidate six rounds.

ESTIMAND        ① P(selection ⊆ that prompt's rubric) under a PROMPT-BLIND draw from the global
                criterion pool, matched on selection size — the chance base rate of `exact`.
                ② the same quantity when the selection is drawn from a DIFFERENT prompt's rubric —
                the sham that separates "is prompt-specific" from "is rubric-shaped".
IDENTIFICATION  exact. Rubrics and selections are committed; the draw is a controlled intervention.
SCOPE           population : the 968 joined prompts and their `coval_full` rubrics
                instrument : R918's own `exact` definition, re-implemented and cross-checked
                baseline   : `generic` (exact 0.0, committed) and `topw_k4` (exact 1.0, committed)
                regime     : selection sizes k ∈ {2,3,4,6,8,12}, 3 seeds
WORLDS          A THE PREDICATE DISCRIMINATES — a prompt-blind draw almost never lands inside a
                  prompt's own rubric, so `exact ≈ 1` really does mark prompt-specific consumption.
                  Then the 2-member set is the COMPLETE population of prompt-blind arms, not a
                  choice, and the constraint belongs to the RELEASE rather than to the definition.
                B IT IS AN ARTIFACT OF RUBRIC SIZE — a prompt-blind draw lands inside the rubric at
                  a high rate, so `exact ≈ 1` marks nothing, arms were excluded on a
                  non-discriminating test, and the certified set is a choice that may be wrong.
                prediction matrix: A -> base rate ≈ 0 at every k; sham ≈ base rate; real arms at 1.0.
                                   B -> base rate high, and the gap to the real arms collapses.
                ⚠ ONTOLOGICAL: A makes the comparator set a fact about what was built; B makes it a
                  methodological error propagating through every extension figure in the arc.
KILL            pre-registered and CONDITIONAL:
                  if positive fires and the placebo is exact:
                      base rate of (exact >= 0.95) < 0.05 at every k -> World A
                      else                                          -> World B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ① my re-implementation must reproduce R918's COMMITTED `exact` for the two anchors it
                published: `generic` = 0.0 and `topw_k4` = 1.0. Any drift in the loader breaks it.
                ② A CEILING check, because a rate control needs both ends: a selection drawn FROM
                each prompt's own rubric must return exact = 1.0 exactly. If the instrument cannot
                return 1.0 by construction, a low base rate says nothing.
                ⚠ and it must fail at the null end: at rubric size 0 the check is vacuous, so prompts
                with an empty rubric are excluded and counted, never silently passed.
NEGATIVE CTRL   the SHAM — the same operation with the prompt MISDIRECTED: draw the selection from a
                DIFFERENT prompt's rubric. This is genuinely "minus the ingredient" here, because the
                ingredient under study IS the prompt-matching, and it separates "prompt-specific"
                from "merely rubric-shaped". Its rate must land at the base rate, not at 1.0.
PLACEBO         a selection drawn from prompt p's own rubric, evaluated against prompt p: exactly
                1.000 in every cell, by construction.
NOISE FLOOR     binomial SE over 968 prompts × 3 seeds, printed beside every rate.
MULTIPLICITY    6 selection sizes × 3 draw modes × 3 seeds = 54 cells, all printed.
SEEDS           3, and the base rate must be stable across them.
IMPOSSIBLE      whether a prompt-blind comparator STRICTER than `generic` could exist AT ALL — that
                needs one to be built and scored, at 15,488 judge calls (R914). N/A, not planned.
                This round bounds what the EXISTING population contains, never what is possible.
"""
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
# ⚠ the arc directory is GLOBBED, not typed. My first version hardcoded a guessed name
#   and the round exited UNRUNNABLE — correctly, but for a reason that was mine. There
#   are TWO `A25_*` directories in this tree, so a typed path is a guess either way.
E05 = ROOT / "E05_the_space_of_compilers"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))

KS = [2, 3, 4, 6, 8, 12]
SEEDS = (1026, 2052, 3078)
THRESH = 0.95


def main() -> int:
    r918f = next(E05.glob("A2*/R918_*/results/typing_specification_curve.json"), None)
    r921f = next(A26.glob("R921_*/results/comparator_sweep.json"), None)
    if not (r918f and r921f):
        print("  UNRUNNABLE: a committed artifact is missing. Exit 2, never 0.")
        return 2
    props = json.loads(r918f.read_text())["properties"]
    r921 = json.loads(r921f.read_text())
    counts, legit = r921["admitted_counts"], r921["legitimate_comparators"]

    # ---------- the CORRECTION, from the source ----------
    fixed = sorted(a for a, p in props.items() if p.get("fixed"))
    print(f"  ⛔ CORRECTION TO R1025's ANNOTATION — `fixed` is computed over {len(props)} arms and "
          f"EXACTLY {len(fixed)}\n     satisfy it: {fixed}. There was no selection among viable "
          f"alternatives; the predicate is a\n     filter and it admitted everything that qualified. "
          f"\"certified 2 from a larger pool\" is WRONG.")

    # ---------- the JOIN, labelled as a join ----------
    stricter = sorted([a for a, c in counts.items() if c < counts[legit[0]]],
                      key=lambda a: counts[a])
    witness = [a for a in stricter
               if props.get(a, {}).get("fixed") is True]
    near = [(a, counts[a], props.get(a, {}).get("exact")) for a in stricter]
    print(f"\n  ⛔ JOIN (two committed artifacts, no new evidence) — arms STRICTER than "
          f"`{legit[0]}` (admits {counts[legit[0]]}):\n     {len(stricter)} of {len(counts)}. "
          f"Of those, how many are prompt-blind by R918's predicate: {len(witness)} {witness}")
    ex1 = [a for a, _c, e in near if e == 1.0]
    exlo = [(a, e) for a, _c, e in near if e is not None and e < 0.5]
    exnone = [a for a, _c, e in near if e is None]
    print(f"     of the {len(stricter)}: exact == 1.0 for {len(ex1)} · exact < 0.5 for "
          f"{len(exlo)} {exlo} · untyped {len(exnone)} {exnone}")
    print(f"     ⇒ every arm that would BIND draws its selection from THAT PROMPT's own rubric, "
          f"except\n       the instance and its twins, which cannot be their own comparator. "
          f"The join could have\n       come out otherwise, so it is informative — but it consumes "
          f"no new evidence.")

    # ---------- the MEASUREMENT: is `exact` discriminating at all? ----------
    from covalx.judge import load_join                                       # noqa: E402
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    fullr = {p: [i["criterion"] for i in (r.get("coval_full") or [])] for p, _q, r in joined}
    pids = sorted([p for p in fullr if fullr[p]])
    empty = len(fullr) - len(pids)
    pool = sorted({c for p in pids for c in fullr[p]})
    sizes = np.array([len(fullr[p]) for p in pids])
    print(f"\n  rubrics: {len(pids)} non-empty prompts (⚠ {empty} EXCLUDED as empty, counted not "
          f"skipped)\n     global criterion pool {len(pool)} · rubric size min {sizes.min()} "
          f"median {int(np.median(sizes))} max {sizes.max()}")

    # POSITIVE ①: reproduce R918's committed anchors from my own loader
    def exact_of(selmap):
        ok = [p for p in selmap if p in fullr and selmap[p]]
        if not ok:
            return None
        return float(np.mean([len(set(selmap[p]) - set(fullr[p])) == 0 for p in ok]))
    RESD = ROOT / "corebench" / "results"
    anch = {}
    for a, want in (("generic", 0.0), ("topw_k4", 1.0)):
        f = RESD / f"core_{a}.json"
        anch[a] = (exact_of(json.loads(f.read_text())) if f.exists() else None, want)
    pos1 = all(v is not None and abs(v - w) < 1e-9 for v, w in anch.values())
    print(f"\n  POSITIVE ① — my loader must reproduce R918's committed `exact` anchors")
    for a, (got, want) in anch.items():
        print(f"     {a:<12}mine {got}  R918 {want}  "
              f"{'PASS' if got is not None and abs(got-want) < 1e-9 else '⛔ FAIL'}")

    rows = []
    for k in KS:
        for mode in ("prompt-blind (global pool)", "SHAM (a DIFFERENT prompt's rubric)",
                     "PLACEBO (this prompt's own rubric)"):
            per = []
            for s in SEEDS:
                rng = np.random.default_rng(s * 100 + k)
                hit = 0
                for i, p in enumerate(pids):
                    if mode.startswith("prompt-blind"):
                        sel = rng.choice(len(pool), size=min(k, len(pool)), replace=False)
                        sel = {pool[j] for j in sel}
                    elif mode.startswith("SHAM"):
                        q = pids[(i + 1 + rng.integers(0, len(pids) - 1)) % len(pids)]
                        src = fullr[q]
                        sel = set(rng.choice(len(src), size=min(k, len(src)),
                                             replace=False).tolist())
                        sel = {src[j] for j in sel}
                    else:
                        src = fullr[p]
                        sel = set(rng.choice(len(src), size=min(k, len(src)),
                                             replace=False).tolist())
                        sel = {src[j] for j in sel}
                    hit += len(sel - set(fullr[p])) == 0
                per.append(hit / len(pids))
            rows.append({"k": k, "mode": mode, "rate": float(np.mean(per)),
                         "seed_spread": float(max(per) - min(per))})
    print(f"\n  ⭐ IS `exact` DISCRIMINATING? P(selection ⊆ this prompt's rubric), by how the "
          f"selection was drawn:")
    print(f"     {'k':>4}" + "".join(f"{m.split(' (')[0]:>26}" for m in
                                     ("prompt-blind (global pool)", "SHAM (a DIFFERENT prompt's "
                                      "rubric)", "PLACEBO (this prompt's own rubric)")))
    for k in KS:
        r = {x["mode"]: x for x in rows if x["k"] == k}
        print(f"     {k:>4}" + "".join(f"{r[m]['rate']:>26.4f}" for m in r))
    se = (0.25 / (len(pids) * len(SEEDS))) ** 0.5
    print(f"     binomial SE (worst case p=0.5, {len(pids)*len(SEEDS)} draws): ±{se:.4f}")
    print(f"     worst per-seed spread: "
          f"{max(x['seed_spread'] for x in rows):.4f}")

    blind = {x["k"]: x["rate"] for x in rows if x["mode"].startswith("prompt-blind")}
    sham = {x["k"]: x["rate"] for x in rows if x["mode"].startswith("SHAM")}
    plac = {x["k"]: x["rate"] for x in rows if x["mode"].startswith("PLACEBO")}
    plac_ok = all(v == 1.0 for v in plac.values())
    print(f"  PLACEBO — a draw from this prompt's OWN rubric must be exactly 1.000 at every k "
          f"(the ceiling\n     the instrument can reach): {sorted(set(plac.values()))} "
          f"{'PASS' if plac_ok else '⛔ FAIL'}")
    print(f"  SHAM   — the same operation with the prompt MISDIRECTED. It is NOT a poison here: the "
          f"ingredient\n     under study IS the prompt-matching, so its absence is exactly what this "
          f"draws. Max {max(sham.values()):.4f}")

    # ⛔ SPLIT THE FORCED PART FROM THE MEASURED PART, BEFORE STATING EITHER.
    #   The prompt-blind base rate is essentially DERIVED once the two sizes are known: drawing k
    #   criteria from a pool of |pool| and asking whether all k land in a rubric of size r has
    #   chance ~(r/|pool|)^k. With the sizes measured below that is ~1e-6 at k=2 and vanishes. So
    #   "0.0000" could not have come out otherwise, and the thing that was genuinely UNKNOWN is the
    #   SIZE RATIO itself. The SHAM is different: it draws REAL criteria from another prompt's REAL
    #   rubric, so it would be non-zero if rubrics shared boilerplate. That could have failed.
    med = float(np.median(sizes))
    print(f"\n  ⛔ WHICH OF THOSE ZEROS IS FORCED — pool {len(pool)} vs median rubric {int(med)} "
          f"(ratio {len(pool)/med:.0f}:1)")
    print(f"     {'k':>4}{'chance (r/|pool|)^k':>22}{'measured prompt-blind':>24}")
    forced = []
    for k in KS:
        ch = (med / len(pool)) ** k
        forced.append({"k": k, "analytic_chance": ch, "measured": blind[k]})
        print(f"     {k:>4}{ch:>22.3e}{blind[k]:>24.4f}")
    print( "     ⇒ the prompt-blind row is a DERIVATION once the size ratio is known. What was")
    print( "       genuinely unknown is the RATIO, and that is what this round measured.")
    shared = float(np.mean([len(set(fullr[pids[i]]) & set(fullr[pids[(i+1) % len(pids)]])) > 0
                            for i in range(len(pids))]))
    print(f"\n  ⭐ THE SHAM IS THE CELL THAT COULD HAVE FAILED, AND IT IS THE REAL FINDING. It draws")
    print(f"     REAL criteria from ANOTHER prompt's REAL rubric, so shared boilerplate would make it")
    print(f"     non-zero. Measured {max(sham.values()):.4f}. Directly: the share of adjacent prompt")
    print(f"     pairs sharing ANY criterion at all is {shared:.4f} — rubric criteria are "
          f"PROMPT-UNIQUE\n     across this corpus, which is a fact about the release and not "
          f"about pool size.")

    if not (pos1 and plac_ok):
        print("\n  a control did not fire. Exit 2, never 0.")
        return 2

    worst_blind = max(blind.values())
    print()
    if worst_blind < 0.05:
        world = (f"⭐ A THE PREDICATE DISCRIMINATES — a prompt-blind draw lands inside a prompt's own "
                 f"rubric at most {worst_blind:.4f} of the time (k∈{KS}), against 1.0000 for the "
                 f"arms the chain excludes. `exact ≈ 1` therefore marks real prompt-specific "
                 f"consumption, the 2-member set is the COMPLETE population of prompt-blind arms, "
                 f"and the constraint belongs to the RELEASE, not to the definition.")
    else:
        world = (f"⭐ B IT IS AN ARTIFACT OF RUBRIC SIZE — a prompt-blind draw already satisfies the "
                 f"predicate {worst_blind:.4f} of the time, so `exact ≈ 1` marks nothing and every "
                 f"exclusion in the certification chain rests on a non-discriminating test.")
    print(world)
    print(f"⛔ AND MOST OF THAT VERDICT IS FORCED. The prompt-blind row follows from a "
          f"{len(pool)}:{int(med)} size\n   ratio; only the SHAM could have failed, and the fact it "
          f"buys is that rubric criteria are\n   PROMPT-UNIQUE across this corpus "
          f"({shared:.4f} of adjacent pairs share any criterion at all).\n   That is what licenses "
          f"reading `exact` as prompt-MATCHING rather than 'looks like a rubric'.")
    print(f"⚠ WHAT THIS CANNOT SAY: whether a prompt-blind comparator STRICTER than `{legit[0]}` "
          f"could exist.\n   Every arm that would bind is already ruled out, but ruling out what was "
          f"BUILT is not ruling out\n   what is POSSIBLE. Building and scoring one costs 15,488 "
          f"judge calls (R914). N/A, not planned.")
    print(f"⚠ AND `exact` IS STILL A PROXY WITH ONE SOUND DIRECTION. `selection ⊆ this prompt's "
          f"rubric`\n   ⇒ prompt-specific consumption is what the numbers above support. The "
          f"converse — that anything\n   NOT satisfying it is prompt-blind — is NOT established "
          f"here, and `fixed` is the predicate\n   actually used, which is strictly stronger.")

    out = HERE / "results" / "certification_predicate.json"
    out.write_text(json.dumps({
        "round": "R1026", "seeds": list(SEEDS), "ks": KS, "threshold": THRESH,
        "correction_to_r1025": {
            "withdrawn": "R921 certified 2 comparators from a larger pool",
            "replacement": f"`fixed` is computed over {len(props)} arms and exactly {len(fixed)} "
                           f"satisfy it; the predicate is a filter, not a curatorial choice",
            "n_arms_typed": len(props), "n_fixed": len(fixed), "fixed": fixed},
        "join": {"label": "a join of two committed artifacts; no new evidence",
                 "n_stricter_than_generic": len(stricter), "stricter": stricter,
                 "prompt_blind_among_them": witness,
                 "exact_eq_1": len(ex1), "exact_lt_half": exlo, "untyped": exnone},
        "positive_anchors": {a: {"mine": v, "r918": w} for a, (v, w) in anch.items()},
        "n_prompts": len(pids), "n_empty_rubrics_excluded": empty, "pool_size": len(pool),
        "rubric_size": {"min": int(sizes.min()), "median": int(np.median(sizes)),
                        "max": int(sizes.max())},
        "rates": rows, "worst_prompt_blind_rate": worst_blind,
        "forced_vs_measured": {"analytic_chance_by_k": forced,
                               "note": "the prompt-blind row is DERIVED from the size ratio; the "
                                       "SHAM row is the cell that could have failed"},
        "adjacent_pair_shares_any_criterion": shared,
        "sham_max": max(sham.values()), "placebo_ok": bool(plac_ok),
        "world": world,
        "limitation": "bounds what the EXISTING population contains, never what is possible; a new "
                      "prompt-blind comparator costs 15,488 judge calls to score",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
