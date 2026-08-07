#!/usr/bin/env python3
"""
R918 · the population every rate in this arc reads is decided by two hand-chosen numbers — swept.

⛔ WHY. R917 corrected every published rate by restricting the population to candidates, and in doing
so read R906's typing as given. **R906's typing is where the population comes from**, and R908, R909,
R910, R911 and R917 all read it. So the arc has one upstream object nobody has attacked.

⭐ AND THE CHEAP HYPOTHESIS DIED BEFORE THIS ROUND COST ANYTHING. My first guess was that the typing
restates my own arm names — in which case *"the partition is complete at three kinds"* would be a
DERIVATION about a naming scheme. **It is not**: `R906_*/run.py:109-119` reads each arm's committed
per-prompt selection and computes three properties of the DATA — `fixed` (identical set on every
prompt), `exact` (share of prompts where the selection is a subset of that prompt's rubric), `lex`
(share of criteria matching a rubric item at `T_LEX = 0.60`). One read killed it; that read is this
round's justification for existing, not a finding.

⭐⭐ **WHAT SURVIVES IS SHARPER. The typing is a DECISION TREE ON TWO NUMBERS:**

    fixed              -> FIXED_CHECKLIST
    exact > 0.95       -> RUBRIC_SELECTOR          <- the population of every rate in the arc
    lex   > 0.25       -> PARAPHRASING_GENERATOR
    else               -> OTHER_SOURCE

`0.95` and `0.25` were chosen in the line that used them. `assurance/a_verdict_threshold_is_named.py`
flags exactly this class and has been failing on this corpus the whole time. **G4 says a cell is not
a curve.** So: sweep both, and report what the arc's numbers do.

⭐⭐⭐ **AND THE GAUGE TEST RUNS FIRST, BECAUSE IT CAN END THE ROUND FOR FREE.** A threshold is
load-bearing only if arms sit NEAR it. If `exact` is bimodal at {0, 1} with an empty middle, then
every threshold in a wide band gives the identical partition, the number was never a degree of
freedom, and the correct verdict is that the arc is SAFE — which is a stronger defence of R917's
numbers than any sweep could give. Measured, not assumed: control ② reports the widest empty
interval around each published threshold.

ESTIMAND        the four-kind partition of R881's arms, and R917's corrected `topw` share, as
                functions of (t_exact, t_lex) over their defensible ranges.
IDENTIFICATION  exact — every quantity is recomputed from the committed selection files.
SCOPE           population: the 99 arms scored in R881
                instrument: R906's three properties, recomputed here from the same objects
                baseline:   R906's published cell (0.95, 0.25), reproduced exactly first
                regime:     home release, T_LEX = 0.60 inherited from R905
WORLDS          A · the partition is stable across the grid -> the thresholds were never degrees of
                    freedom and every downstream rate is safe from this
                B · the partition moves materially -> every rate in the arc inherits an undeclared
                    researcher degree of freedom, and R917's corrected numbers need a band
                C · the properties are degenerate (all at 0 or 1) -> the tree is really a structural
                    predicate wearing a threshold's clothes; say so and stop calling them thresholds
KILL            CONDITIONAL:
                  ⭐ ① WIRING/POSITIVE: at (0.95, 0.25) this must reproduce R906's published
                     built-counts for all four kinds AND its 3 untypable arms. Different code, same
                     objects — if it does not reproduce, nothing swept means anything.
                  ⭐ ② GAUGE, run before any sweep: the empirical distribution of `exact` and
                     `lex`, and the widest arm-free interval containing each published threshold.
                  ⭐ ③ THE SWEEP MUST BE ABLE TO MOVE THE ANSWER: at `t_exact` BELOW the minimum
                     observed `exact`, every non-fixed arm must become RUBRIC_SELECTOR. If the
                     extreme does not move the partition, the sweep instrument is blind and a flat
                     curve proves nothing.
                     ⚠ This is the control the `random`-rule placebo lacked in R917, where the null
                     was a point mass at 0 and could not fail.
                     ⛔ AND IT FIRED ON THE FIRST RUN, AGAINST ME, FOR THE SAME REASON. I first
                     wrote the extreme as `t_exact = 0.0`. **Seven arms have `exact` EXACTLY 0.0,
                     and the tree tests `exact > te` — a strict inequality cannot fire on a
                     structural zero at any `te >= 0`.** So the extreme I pre-registered was
                     unreachable inside [0, 1] and the control failed on its own arithmetic rather
                     than on the object. Corrected to `T_EXTREME = -0.001`, which is below the
                     observed minimum. **This is R917's placebo defect one level up, and it is the
                     third structural-zero error in this session** — the pattern is that I choose a
                     boundary value without checking whether the comparison operator can reach it.
                  ⭐ ④ downstream: R917's `topw` candidates-only share recomputed at every cell.
MULTIPLICITY    |t_exact| × |t_lex| cells; every cell printed, including those that do not move.
ARTIFACT        results/typing_specification_curve.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · admission probability. ⚠ AND: this sweeps the TREE's thresholds, not
                `T_LEX = 0.60` inside the lexical match, which is R905's and is inherited whole.
"""
import difflib, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
RES = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
T_LEX = 0.60
PUB_EXACT, PUB_LEX = 0.95, 0.25
GRID_E = [-0.001, 0.0, 0.50, 0.70, 0.80, 0.90, 0.95, 0.99, 1.0]
T_EXTREME = -0.001    # ⚠ NOT 0.0 — see control ③; a strict `>` cannot fire on a structural zero
GRID_L = [0.05, 0.10, 0.25, 0.40, 0.60]


def main() -> int:
    r881 = next(A24.glob("R881_*/results/boundary_distance.json"), None)
    if r881 is None:
        print("  UNRUNNABLE: R881 artifact missing. Exit 2, never 0.")
        return 2
    adm = {x["arm"]: bool(x["admitted"]) for x in json.loads(r881.read_text())["arms"]}
    r906 = json.loads(next(A24.glob("R906_*/results/bar_by_source.json")).read_text())
    pub = {k["kind"]: len(k["built"]) for k in r906["kinds"]}
    pub_untypable = set(r906["untypable_named"])
    print(f"  admission READ from R881: {sum(adm.values())} of {len(adm)}")
    print(f"  R906 published: {pub}  untypable {sorted(pub_untypable)}")

    sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
    from covalx.judge import load_join                                       # noqa: E402
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    fullr = {p: [i["criterion"] for i in (r.get("coval_full") or [])] for p, _q, r in joined}
    corec = {p: [i["criterion"] for i in (r.get("coval_core") or [])] for p, _q, r in joined}

    def sel_of(arm):
        if arm == "coval_core":
            return {p: v for p, v in corec.items() if v}
        f = RES / f"core_{arm}.json"
        if not f.exists():
            return None
        try:
            return json.loads(f.read_text())
        except Exception:
            return None

    # ---------- properties, computed once per arm ----------
    props, untypable = {}, []
    for arm in sorted(adm):
        sel = sel_of(arm)
        if not sel:
            untypable.append(arm); continue
        pids = [p for p in sel if p in fullr and sel[p]]
        if len(pids) < 50:
            untypable.append(arm); continue
        sets = [frozenset(sel[p]) for p in pids]
        fixed = len(set(sets)) == 1
        exact = float(np.mean([len(s - frozenset(fullr[p])) == 0 for s, p in zip(sets, pids)]))
        props[arm] = {"fixed": bool(fixed), "exact": exact, "lex": None,
                      "pids": pids, "sel": sel}
    print(f"  typed-able {len(props)} · UNTYPABLE and NAMED {len(untypable)}: {sorted(untypable)}")
    c1_unt = set(untypable) == pub_untypable

    # lex only where it can ever matter: not fixed, and exact below the top grid threshold
    need = [a for a, v in props.items() if not v["fixed"] and v["exact"] <= max(GRID_E)]
    print(f"  lexical similarity needed for {len(need)} arm(s) — the rest are settled by `exact`")
    for a in need:
        v = props[a]
        sample = v["pids"][:150]
        v["lex"] = float(np.mean([np.mean([max((difflib.SequenceMatcher(None, c, z).ratio()
                                                for z in fullr[p]), default=0.0) >= T_LEX
                                           for c in v["sel"][p]]) for p in sample]))
    for v in props.values():
        v.pop("pids", None); v.pop("sel", None)

    def partition(te, tl):
        out = {}
        for a, v in props.items():
            if v["fixed"]:
                out[a] = "FIXED_CHECKLIST"
            elif v["exact"] > te:
                out[a] = "RUBRIC_SELECTOR"
            elif v["lex"] is not None and v["lex"] > tl:
                out[a] = "PARAPHRASING_GENERATOR"
            else:
                out[a] = "OTHER_SOURCE"
        return out

    # ---------- ① WIRING ----------
    base = partition(PUB_EXACT, PUB_LEX)
    got = {k: sum(v == k for v in base.values()) for k in set(base.values())}
    c1 = all(got.get(k, 0) == pub[k] for k in pub) and c1_unt
    print(f"\n  ① WIRING/POSITIVE — recomputed at R906's published ({PUB_EXACT}, {PUB_LEX}):")
    print(f"     {'kind':<26}{'recomputed':>12}{'R906':>8}   match")
    for k in sorted(pub):
        print(f"     {k:<26}{got.get(k, 0):>12}{pub[k]:>8}   {got.get(k, 0) == pub[k]}")
    print(f"     untypable set identical: {c1_unt}")
    print(f"     ① {c1}  {'PASS' if c1 else 'FAIL'}")

    # ---------- ② GAUGE, before any sweep ----------
    ex = sorted(v["exact"] for v in props.values() if not v["fixed"])
    lx = sorted(v["lex"] for v in props.values() if v["lex"] is not None)

    def empty_band(vals, t):
        below = max([v for v in vals if v <= t], default=None)
        above = min([v for v in vals if v > t], default=None)
        return (below, above, (above - below) if (below is not None and above is not None)
                else None)

    be = empty_band(ex, PUB_EXACT)
    bl = empty_band(lx, PUB_LEX)
    print(f"\n  ② GAUGE — where do arms actually sit relative to each threshold?")
    print(f"     `exact` over {len(ex)} non-fixed arms: min {min(ex):.3f} max {max(ex):.3f}  "
          f"at 1.0: {sum(v == 1.0 for v in ex)}  at 0.0: {sum(v == 0.0 for v in ex)}  "
          f"strictly between: {sum(0.0 < v < 1.0 for v in ex)}")
    print(f"        widest arm-free band around {PUB_EXACT}: ({be[0]}, {be[1]}]  "
          f"width {be[2] if be[2] is not None else 'unbounded'}")
    print(f"     `lex` over {len(lx)} arm(s): {[round(v, 3) for v in lx]}")
    print(f"        widest arm-free band around {PUB_LEX}: ({bl[0]}, {bl[1]}]  "
          f"width {bl[2] if bl[2] is not None else 'unbounded'}")

    # ---------- ③ the sweep must be able to move the answer ----------
    extreme = partition(T_EXTREME, PUB_LEX)
    nonfixed = [a for a, v in props.items() if not v["fixed"]]
    all_rs = all(extreme[a] == "RUBRIC_SELECTOR" for a in nonfixed)
    moved_at_extreme = sum(extreme[a] != base[a] for a in props)
    c3 = all_rs and moved_at_extreme > 0
    print(f"\n  ③ SWEEP-CAN-MOVE — at t_exact = {T_EXTREME} (below min observed "
          f"{min(ex):.3f}; NOT 0.0, a strict `>` cannot fire on the {sum(v == 0.0 for v in ex)} "
          f"arms sitting at exactly 0.0) every non-fixed arm must become RUBRIC_SELECTOR:")
    print(f"     all {len(nonfixed)} non-fixed arms reassigned: {all_rs}; "
          f"arms whose kind changed vs published: {moved_at_extreme}")
    print(f"     ③ {c3}  {'PASS' if c3 else 'FAIL — a flat curve from a blind sweep proves nothing'}")

    if not (c1 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c3": c3,
                   "recomputed": got, "published": pub},
                  open(OUT / "typing_specification_curve.json", "w"), indent=2)
        return 2

    # ---------- ④ the curve, and what it does downstream ----------
    r916 = json.loads(next(A24.glob("R916_*/results/apparatus_audit.json")).read_text())
    apparatus = {a for a, h in r916["hits"].items()
                 if any(x in h["signatures"] for x in ("COMPARATOR", "WHOLE_RUBRIC", "MISDIRECTED"))}

    def is08(a):
        return a.endswith("_08b") or a.endswith("_08bR")

    cells = []
    print(f"\n  ④ SPECIFICATION CURVE — {len(GRID_E)}×{len(GRID_L)} cells, every one printed:")
    print(f"     {'t_exact':>8}{'t_lex':>7}{'FIXED':>7}{'RUBRIC':>8}{'PARA':>6}{'OTHER':>7}"
          f"{'topw candidates':>18}")
    for te in GRID_E:
        for tl in GRID_L:
            pt = partition(te, tl)
            cnt = {k: sum(v == k for v in pt.values()) for k in
                   ("FIXED_CHECKLIST", "RUBRIC_SELECTOR", "PARAPHRASING_GENERATOR", "OTHER_SOURCE")}
            tw = [a for a, k in pt.items() if k == "RUBRIC_SELECTOR"
                  and a.startswith("topw_") and a not in apparatus and not is08(a)]
            ta = sum(adm[a] for a in tw)
            cells.append({"t_exact": te, "t_lex": tl, "counts": cnt,
                          "topw_candidates": [ta, len(tw)],
                          "topw_share": (ta / len(tw)) if tw else None})
            print(f"     {te:>8.2f}{tl:>7.2f}{cnt['FIXED_CHECKLIST']:>7}"
                  f"{cnt['RUBRIC_SELECTOR']:>8}{cnt['PARAPHRASING_GENERATOR']:>6}"
                  f"{cnt['OTHER_SOURCE']:>7}{f'{ta}/{len(tw)}':>18}")

    shares = {c["topw_share"] for c in cells if c["topw_share"] is not None}
    parts = {json.dumps(c["counts"], sort_keys=True) for c in cells}
    stable = len(shares) == 1
    world = "A" if stable else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: distinct partitions across the grid: {len(parts)}; "
          f"distinct `topw` candidate shares: {len(shares)} — {sorted(shares)}")
    if stable:
        print(f"     **The two thresholds are not degrees of freedom.** `exact` is degenerate: "
              f"{sum(v == 1.0 for v in ex)} of {len(ex)} non-fixed arms sit at exactly 1.0 and "
              f"{sum(0.0 < v < 1.0 for v in ex)} sit strictly between — so every threshold in "
              f"({be[0]}, {be[1]}] gives the identical partition. R917's corrected numbers do not "
              f"inherit a researcher degree of freedom from here, and control ③ shows the sweep "
              f"could have moved them.")
        print(f"     ⚠ SO CALL IT WHAT IT IS: `exact > 0.95` is a STRUCTURAL PREDICATE — is the "
              f"selection a subset of the prompt's rubric — wearing a threshold's clothes. Naming "
              f"it as a threshold invited exactly the attack this round ran, and cost the round.")
    else:
        print(f"     **The population moves with the threshold**, so every rate downstream of "
              f"R906 carries an undeclared degree of freedom and must be reported as a band.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world,
               "published_cell": {"t_exact": PUB_EXACT, "t_lex": PUB_LEX},
               "t_lex_inner_inherited": T_LEX,
               "properties": {a: {k: v for k, v in p.items()} for a, p in props.items()},
               "untypable": sorted(untypable),
               "gauge": {"exact_at_one": int(sum(v == 1.0 for v in ex)),
                         "exact_strictly_between": int(sum(0.0 < v < 1.0 for v in ex)),
                         "exact_empty_band_around_published": be,
                         "lex_values": lx, "lex_empty_band_around_published": bl},
               "sweep_can_move": {"all_rubric_at_zero": bool(all_rs),
                                  "arms_changed_at_extreme": int(moved_at_extreme)},
               "cells": cells, "distinct_partitions": len(parts),
               "distinct_topw_shares": sorted(shares),
               "killed_before_running": "the hypothesis that R906's typing restates arm names — "
                                        "it reads the committed per-prompt selections",
               "unit_note": "counts are ARMS; share = admitted/built within a kind",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "typing_specification_curve.json", "w"), indent=2)
    print(f"\n  artifact: results/typing_specification_curve.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
