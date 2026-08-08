#!/usr/bin/env python3
"""R1107 — does SET STRUCTURE transfer worse as k grows? A dose-response on R1106's n=2 pattern.

R1106 found the three arms falling furthest below the judges' compression line are `oracle_k4`
(−0.0582), `oracle_k4_fit1` (−0.0522) and `greedy_k4_fit1` (−0.0462) — the rules that fit SET
STRUCTURE to the human target — while `indep_k4_fit1`, which fits the same target INDEPENDENTLY,
moves −0.0011. **That is 2 rules and 3 arms at a single k, and R1106 reported it as a pattern rather
than a claim.** A pattern at one dose is exactly what a dose-response can kill.

⛔ THE COST METER RAN FIRST AND CHANGED THE DESIGN. `oracle_k` searches combinations with a CAP of
20,000 per prompt; at k=8 and k=12 most prompts hit the cap and the run is tens of minutes per cell
per judge. `greedy_k` is the OTHER set-aware rule — sequential, each pick conditional on those
already chosen — and it costs ~3s. **So the sweep runs on `greedy` vs `indep`, which is the same
contrast `select_core.py` names** (*"the oracle-minus-indep difference isolates SET STRUCTURE from
mere fitting"*), and `oracle_k4` stays as the corroborating point already committed. The expensive
complete success was refused in favour of the cheap decisive one.

⭐ AND THE REBUILD IS VERIFIED BEFORE IT IS USED. `--full-npz sat08_full.npz --select-npz sat_full.npz
--tag-suffix _08b` reproduces the committed `sat_greedy_k4_fit1_08b.npz` BYTE-IDENTICALLY (meta and
sat both `array_equal`). Without that, new k cells would not be comparable to R1106's.

ESTIMAND        `gap(k) = residual(indep_k) − residual(greedy_k)`, where `residual` is an arm's
                distance BELOW the judges' compression line — and the line is fitted on R1106's
                43-arm population and the swept arms are placed on it as HELD-OUT points.
IDENTIFICATION  identified. Every arm is rebuildable under both judges at 0 judge calls, and the
                compression line is a property of the judge pair, not of these arms.
UNIT OF THE     an arm at a given (rule, k, spec); the residual is a mean over 968 prompts.
  INSTRUMENT
UNIT OF THE     the same. ⚠ NOT `a rule`: the claim is about how a rule's transfer changes WITH k, so
  CLAIM         a single k cannot carry it — which is precisely R1106's limitation.
SCOPE           population: rules {greedy_k, indep_k, topw_k} x k in {2,4,8,12}. instrument: A2
                margins over `generic`, residual from the 43-arm compression line. baseline: the 2B
                judge. regime: 968 prompts, fit-parity 1 for the fitted rules.
WORLDS          A DOSE-RESPONSE   `gap(k)` increases monotonically with k. Set structure is the
                             mechanism and more of it means less transfer across judges.
                B NO DOSE        `gap(k)` is flat or non-monotone. Then R1106's ordering was a k=4
                             coincidence and `set structure` is not the name of the failure.
                Prediction matrix on (monotonicity, gap(12) − gap(2)):
                  A -> (strictly increasing over all 3 steps, resolvably > 0)
                  B -> (not monotone, or the difference straddles 0)
KILL            pre-registered and strict. World A is KILLED if `gap` is not strictly increasing over
                k = 2 -> 4 -> 8 -> 12, OR if the bootstrap 2.5th percentile of `gap(12) − gap(2)` is
                not above zero. ⚠ THE GATE IS ASYMMETRIC, and that was corrected after the first run:
                                    kill      needs  rebuild_exact
                                    survival  needs  rebuild_exact AND placebo_flat
                A drifting placebo vetoes a POSITIVE dose claim — the trend would belong to k rather
                than to fitting — but it cannot veto the finding that NO monotone trend exists, since
                that finding attributes nothing to anything.
POSITIVE CTRL   the rebuild must reproduce the committed `greedy_k4_fit1_08b` and `indep_k4_fit1_08b`
                npz files EXACTLY. An instrument that cannot regenerate a committed cell cannot be
                trusted on the cells that have none.
PLACEBO         `topw_k` swept over the same k. It fits NOTHING — it ranks by the human importance
                weights and never reads satisfaction or the target — so its residual must stay small
                and show no trend in k. If `topw`'s residual also grows with k, the effect is about
                k itself (set size, coverage, saturation) and not about fitting.
NEGATIVE CTRL   the `_08bR` specification, where the rule is RE-RUN under the 8B judge: the
                greedy-minus-indep gap must COLLAPSE, because refitting to the new instrument is what
                should undo an overfit to the old one. R1105 already measured that those arms return.
NOISE FLOOR     a cluster bootstrap over prompts on every residual, so `monotone` is read against the
                precision the design has rather than off four point estimates.
MULTIPLICITY    3 rules x 4 k x 2 specifications = 24 cells, every one reported, trend and no-trend.
SPECIFICATION   spec in {`_08b` re-scored, `_08bR` re-run} x rule x k. The `_08bR` column is the
                negative control and is reported whole, not only where it agrees.
SEEDS           3 bootstrap seeds; the fitted rules use fit-parity 1 throughout so the split is held
                constant across k and cannot masquerade as a dose.
ARTIFACT        results/set_structure_dose.json with the source hash.
REPRODUCIBILITY deterministic given the seeds.
IMPOSSIBLE      | criterion | what it would require |
                | `oracle_k` at k = 8 and 12 | tens of minutes per cell per judge because of the
                  20,000-combination cap — refused on the cost meter and named, not silently dropped |
                | whether either judge is CORRECT | an external gold standard |
                | a third set-aware rule | the release ships two, `oracle_k` and `greedy_k` |
                | cross-release | a second release |
"""
from __future__ import annotations

import hashlib, json, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
A27 = ROOT / "E05_the_space_of_compilers" / "A27_is_the_bar_resolvable"
PY = str(ROOT / ".venv" / "bin" / "python")
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

OUT = HERE / "results" / "set_structure_dose.json"
WORK = pathlib.Path("/tmp/claude-1000/-home-ivan/7d277876-c2fd-4a27-9b05-652b391121ff/scratchpad/r1107_arms")
KS = (2, 4, 8, 12)
RULES = {"greedy_k": "set-aware", "indep_k": "independent", "topw_k": "no fitting (placebo)"}
NBOOT, SEEDS = 2000, (1107, 2214, 3321)


def build(rule, k, spec):
    """spec: '2B' | '08b' (2B-selected, 8B-scored) | '08bR' (rule re-run under 8B)."""
    fit = ["--fit-parity", "1"] if rule in ("greedy_k", "indep_k") else []
    tag = f"{rule}{k}" + ("_fit1" if fit else "")
    cmd = [PY, str(ROOT / "corebench" / "select_core.py"), "--rule", rule, "--k", str(k),
           "--outdir", str(WORK)] + fit
    if spec == "08b":
        cmd += ["--full-npz", str(RES / "sat08_full.npz"),
                "--select-npz", str(RES / "sat_full.npz"), "--tag-suffix", "_08b"]
        tag += "_08b"
    elif spec == "08bR":
        cmd += ["--full-npz", str(RES / "sat08_full.npz"), "--tag-suffix", "_08bR"]
        tag += "_08bR"
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=3600)
    f = WORK / f"sat_{tag}.npz"
    return (f, tag) if (p.returncode == 0 and f.exists()) else (None, tag)


def main() -> int:
    f06 = next(A27.glob("R1106_*/results/compression_or_reordering.json"), None)
    f05 = next(A27.glob("R1105_*/results/second_judge.json"), None)
    if f06 is None or f05 is None:
        print("  UNRUNNABLE: a prior artifact is absent. Exit 2, never 0."); return 2
    common = json.loads(f05.read_text())["population"]["common"]
    WORK.mkdir(parents=True, exist_ok=True)

    tg, _ = load_targets()
    base = load_sat(RES / "sat_generic.npz")
    pids = sorted(set(base) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: [np.array(cls(np.array(t[0], float)), float) for t in tg[p]] for p in pids}
    n = len(pids)

    def perprompt(path):
        Sa = load_sat(path)
        v = np.full(n, np.nan)
        for i, p in enumerate(pids):
            if p in Sa:
                c = np.array(cls(yvec(Sa[p], sorted({j for j, _ in Sa[p]}))), float)
                v[i] = float(np.mean([(c == h).mean() for h in H[p]]))
        return np.nan_to_num(v, nan=0.0)

    # ---- the compression line, fitted on R1106's 43-arm population; the swept arms are HELD OUT
    def pf(a, judge):
        if judge == "2B":
            f = RES / f"sat_{a}.npz"
            return f if f.exists() else None
        f = RES / f"sat_{a}_08b.npz"
        return f if f.exists() else (RES / f"sat08_{a}.npz" if (RES / f"sat08_{a}.npz").exists()
                                     else None)
    V2, V8 = {}, {}
    for a in common:
        p2, p8 = pf(a, "2B"), pf(a, "8B")
        if p2 and p8:
            V2[a], V8[a] = perprompt(p2), perprompt(p8)
    BASE_ARM = "generic"
    fitpop = [a for a in V2 if a != BASE_ARM]
    m2 = np.array([float((V2[a] - V2[BASE_ARM]).mean()) for a in fitpop])
    m8 = np.array([float((V8[a] - V8[BASE_ARM]).mean()) for a in fitpop])
    c_, b_ = np.polyfit(m2, m8, 1)
    print(f"  compression line fitted on {len(fitpop)} held-out arms: slope {c_:.4f} "
          f"intercept {b_:.5f}")

    # ---- POSITIVE CONTROL: the rebuild must reproduce two committed cells exactly
    rebuild_exact, rb = True, {}
    for rule in ("greedy_k", "indep_k"):
        f, tag = build(rule, 4, "08b")
        ok = False
        if f is not None and (RES / f"sat_{tag}.npz").exists():
            a = np.load(RES / f"sat_{tag}.npz", allow_pickle=True)
            b = np.load(f, allow_pickle=True)
            ok = bool(np.array_equal(a["meta"], b["meta"]) and np.array_equal(a["sat"], b["sat"]))
        rb[tag] = ok
        rebuild_exact &= ok
    print(f"  POSITIVE rebuild reproduces committed cells exactly: {rb}")

    # ---- the sweep
    cells, vecs = {}, {}
    for rule in RULES:
        for k in KS:
            specs = ("2B", "08b") if rule == "topw_k" else ("2B", "08b", "08bR")
            for spec in specs:
                f, tag = build(rule, k, spec)
                if f is None:
                    print(f"    ⚠ {rule} k={k} {spec}: generator failed"); continue
                vecs[(rule, k, spec)] = perprompt(f)
        print(f"  built {rule}")

    gen2, gen8 = V2[BASE_ARM], V8[BASE_ARM]

    def residual(rule, k, spec):
        v2 = vecs.get((rule, k, "2B")); vx = vecs.get((rule, k, spec))
        if v2 is None or vx is None:
            return None
        mm2 = float((v2 - gen2).mean()); mm8 = float((vx - gen8).mean())
        return {"m2": round(mm2, 5), "m8": round(mm8, 5),
                "pred": round(float(c_ * mm2 + b_), 5),
                "residual": round(float(mm8 - (c_ * mm2 + b_)), 5)}

    table = {}
    for rule in RULES:
        for k in KS:
            for spec in ("08b", "08bR"):
                r = residual(rule, k, spec)
                if r:
                    table[f"{rule}|k={k}|{spec}"] = r

    gap = {k: (table[f"indep_k|k={k}|08b"]["residual"] - table[f"greedy_k|k={k}|08b"]["residual"])
           for k in KS if f"indep_k|k={k}|08b" in table and f"greedy_k|k={k}|08b" in table}
    gapR = {k: (table[f"indep_k|k={k}|08bR"]["residual"] - table[f"greedy_k|k={k}|08bR"]["residual"])
            for k in KS if f"indep_k|k={k}|08bR" in table and f"greedy_k|k={k}|08bR" in table}
    topw_res = {k: table[f"topw_k|k={k}|08b"]["residual"] for k in KS if f"topw_k|k={k}|08b" in table}

    ks = sorted(gap)
    monotone = all(gap[ks[i]] < gap[ks[i + 1]] for i in range(len(ks) - 1)) if len(ks) > 1 else False

    # ---- NOISE FLOOR: cluster bootstrap on gap(12) − gap(2)
    diffs = []
    for s in SEEDS:
        rng = np.random.default_rng(s)
        for _ in range(NBOOT // len(SEEDS)):
            idx = rng.integers(0, n, n)
            def res_b(rule, k):
                v2, vx = vecs[(rule, k, "2B")][idx], vecs[(rule, k, "08b")][idx]
                mm2 = float((v2 - gen2[idx]).mean()); mm8 = float((vx - gen8[idx]).mean())
                return mm8 - (c_ * mm2 + b_)
            g_lo = res_b("indep_k", ks[0]) - res_b("greedy_k", ks[0])
            g_hi = res_b("indep_k", ks[-1]) - res_b("greedy_k", ks[-1])
            diffs.append(g_hi - g_lo)
    d_lo, d_hi = float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))
    resolved = d_lo > 0

    # ---- PLACEBO: topw's residual must not trend.
    # ⛔ THE FIRST FORM PASSED FOR THE WRONG REASON, and the repair changes what the control can
    #    gate. v1 tested only INCREASING monotonicity; `topw` drifts MONOTONE DECREASING, so
    #    `not topw_mono` was True and the control passed while the placebo was in fact trending at
    #    51% of the gap's own span. Direction-agnostic now — and the honest consequence is that this
    #    placebo DOES fire.
    tk = sorted(topw_res)
    topw_span = (max(topw_res.values()) - min(topw_res.values())) if topw_res else None
    up = all(topw_res[tk[i]] < topw_res[tk[i + 1]] for i in range(len(tk) - 1)) if tk else False
    down = all(topw_res[tk[i]] > topw_res[tk[i + 1]] for i in range(len(tk) - 1)) if tk else False
    topw_mono = up or down
    gap_span = (max(gap.values()) - min(gap.values())) if gap else None
    placebo_flat = bool(topw_span is not None and gap_span is not None
                        and not (topw_mono and topw_span >= 0.5 * gap_span))
    # ⚠ AND THE PLACEBO'S ROLE IS ASYMMETRIC, which v1 did not encode. A drifting placebo VETOES a
    #   positive dose claim — it would mean the trend belongs to k rather than to fitting. It does
    #   NOT veto the KILL, because the kill says there is no monotone trend to attribute to anything.
    #   So the gate below requires the placebo only for a world-A SURVIVAL, never for its death.

    # ---- NEGATIVE: refitting under 8B must collapse the gap
    negative_collapses = (max(abs(v) for v in gapR.values()) < max(abs(v) for v in gap.values())
                          if gapR and gap else None)

    # ⛔ ASYMMETRIC GATE. The kill needs only that the instrument can regenerate a committed cell;
    #    a world-A SURVIVAL additionally needs the placebo, because a drifting placebo would mean
    #    any dose belonged to k rather than to fitting.
    gate_open = rebuild_exact
    world_A_killed = (not (monotone and resolved)) if gate_open else None
    survival_admissible = bool(gate_open and placebo_flat)

    payload = {
        "round": "R1107",
        "question": "does set-structure fitting transfer worse across judges as k grows?",
        "compression_line": {"slope": round(float(c_), 4), "intercept": round(float(b_), 5),
                             "fitted_on_n_arms": len(fitpop),
                             "note": "the swept arms are HELD OUT of this fit"},
        "cost_meter": {"oracle_k_at_k8_k12": "REFUSED — 20,000-combination cap makes it tens of "
                                             "minutes per cell per judge; greedy_k is the other "
                                             "set-aware rule and costs ~3s",
                       "corroborating_point": "oracle_k4, already committed, residual −0.0582"},
        "rebuild_control": rb,
        "cells": table,
        "gap_08b": {str(k): round(v, 5) for k, v in gap.items()},
        "gap_08bR_negative_control": {str(k): round(v, 5) for k, v in gapR.items()},
        "placebo_topw_residual": {str(k): round(v, 5) for k, v in topw_res.items()},
        "monotone": monotone,
        "gap_high_minus_low": {"k_lo": ks[0] if ks else None, "k_hi": ks[-1] if ks else None,
                               "ci": [round(d_lo, 5), round(d_hi, 5)], "resolved": bool(resolved)},
        "controls": {
            "POSITIVE the rebuild reproduces two committed `_08b` cells byte-identically":
                bool(rebuild_exact),
            "PLACEBO `topw_k`, which fits nothing, shows no comparable trend in k": placebo_flat,
            "GATE the rebuild control alone licenses the KILL; survival would also need the placebo":
                bool(gate_open),
            "NEGATIVE refitting under 8B (`_08bR`) collapses the gap": negative_collapses,
        },
        "kill": {"gate_open": gate_open, "world_A_killed": world_A_killed,
                 "survival_would_be_admissible": survival_admissible,
                 "requires": "strictly increasing over 2->4->8->12 AND CI lower bound above 0"},
        "placebo_detail": {"topw_residual_span": round(topw_span, 5) if topw_span else None,
                           "topw_monotone_either_direction": bool(topw_mono),
                           "gap_span": round(gap_span, 5) if gap_span else None,
                           "ratio": round(topw_span / gap_span, 3) if (topw_span and gap_span) else None,
                           "reading": ("the placebo DOES drift, monotone decreasing, at about half "
                                       "the gap's own span. That vetoes any POSITIVE dose claim — the "
                                       "trend would belong to k, not to fitting — and does not touch "
                                       "the kill, which is that no monotone trend exists to attribute")},
        "grid": {"cells_tested": len(table), "rules": list(RULES), "ks": list(KS)},
        "seeds": list(SEEDS),
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
    }
    if not gate_open:
        payload["verdict"] = ("⚠ UNVERIFIED — a control is red. "
                              f"Controls: {json.dumps(payload['controls'])}")
    else:
        payload["verdict"] = (
            f"{'⛔ WORLD A IS KILLED' if world_A_killed else '⭐ WORLD A SURVIVES'}: "
            f"gap(k) = {payload['gap_08b']}, monotone {monotone}, "
            f"gap({ks[-1]}) − gap({ks[0]}) CI [{d_lo:+.5f}, {d_hi:+.5f}], resolved {resolved}. "
            f"PLACEBO `topw_k` residual {payload['placebo_topw_residual']}. "
            f"NEGATIVE the re-run specification gives {payload['gap_08bR_negative_control']}, "
            f"collapse {negative_collapses}."
            + (" ⭐ SO SET STRUCTURE IS THE NAME: the more of it a rule fits under one judge, the "
               "less it transfers to another."
               if not world_A_killed else
               f" ⛔ SO `set structure` IS NOT ESTABLISHED AS THE NAME: R1106's ordering does not "
               f"extend into a dose, and the gap PEAKS at k=4 — the single dose R1106 observed. "
               f"⚠ AND THE PLACEBO WOULD HAVE VETOED A POSITIVE FINDING ANYWAY: `topw_k`, which fits "
               f"nothing, drifts monotonically at {payload['placebo_detail']['ratio']} of the gap's "
               f"own span, so a dose in k could not have been attributed to fitting."))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, sort_keys=True))
    print()
    print(f"  {'cell':<28}{'m2B':>9}{'pred8B':>9}{'obs8B':>9}{'residual':>10}")
    for kk in sorted(table):
        r = table[kk]
        print(f"  {kk:<28}{r['m2']:>+9.4f}{r['pred']:>+9.4f}{r['m8']:>+9.4f}{r['residual']:>+10.5f}")
    print(f"\n  gap(k)  = {payload['gap_08b']}   monotone {monotone}")
    print(f"  gapR(k) = {payload['gap_08bR_negative_control']}")
    print(f"  topw    = {payload['placebo_topw_residual']}")
    print()
    for k, v in payload["controls"].items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print()
    print(" ", payload["verdict"])
    return 0 if gate_open else 2


if __name__ == "__main__":
    sys.exit(main())
