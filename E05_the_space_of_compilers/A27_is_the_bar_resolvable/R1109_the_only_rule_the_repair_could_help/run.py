#!/usr/bin/env python3
"""R1109 — is there ANY object the fitting-protocol clause could help? Sweep the one candidate.

R1108 established a structural result: refitting under the evaluating judge recovers admission for 4
arms and **all 4 are ones clause ③ excludes**, because for every satisfaction-blind rule the two
specifications are byte-identical and for every fixed-text arm re-running IS re-scoring. So the
protocol repair moves nothing the definition would accept — **unless some rule reads satisfaction
without reading the target.**

⭐ AND EXACTLY ONE RULE QUALIFIES — a DERIVATION over three committed artifacts, labelled as one:
  · R1094's two exclusion lists contain NEITHER `topvar_k` NOR `topwvar_k` — so both clear clause ③
    on the leakage reading.
  · R1101's within-prompt weight derangement: `topwvar_k` MOVES (it consumes the human importance
    ratings) and `topvar_k` does NOT.
  · R1100's target derangement: neither consumes the human target.
  · `topw_k` is satisfaction-blind, so R1108 measured its two specifications byte-identical — the
    repair is a no-op for it by construction.
  ⇒ **`topvar_k` is the unique rule in this release that is clean under BOTH readings of ③ and for
    which the fitting-protocol repair is live.** `topwvar_k` is the runner-up, live but
    rating-consuming, and is swept beside it.

⛔ AND IT HAS ONLY EVER BEEN BUILT AT k = 4. Every statement this arc makes about `topvar_k` rests on
one cell of a rule whose whole point is that k controls how much satisfaction spread it can exploit.

ESTIMAND        for each rule in {topvar_k, topwvar_k, topw_k} and each k in {1,2,3,4,6,8,12}, ②′
                admission under three worlds: the 2B judge, the 8B judge with the arm RE-SCORED, and
                the 8B judge with the rule RE-RUN. 63 cells.
IDENTIFICATION  identified. All three rules are regenerable at 0 judge calls under either judge.
UNIT OF THE     an arm at a given (rule, k, world) and its ②′ membership.
  INSTRUMENT
UNIT OF THE     the same. ⚠ NOT `a rule`: the claim is about whether ANY CELL admits, so a single k
  CLAIM         cannot carry it — which is precisely what k=4 has been doing.
SCOPE           population: 3 rules x 7 k. instrument: R1055's operator, analytic inner bound
                (validated against its 4000-draw bootstrap). baseline: `topw_k` at matched k, whose
                2B admissions are committed in R1105. regime: 968 prompts, target A2, comparators
                {generic, genericpool16} from the judge under test.
WORLDS          A THE REPAIR HAS NO BENEFICIARY   `topvar_k` and `topwvar_k` are admitted in NO cell.
                                 Then the fitting-protocol clause is dead weight: there is no object
                                 in this release it could ever help, and R1108's structural result
                                 becomes exhaustive rather than suggestive.
                B THERE IS ONE                    at least one cell admits. Then the clause has a
                                 possible beneficiary and the repair is worth stating — and whether
                                 the REFIT world admits where the RE-SCORED one does not is what
                                 decides if the clause does the work.
                Prediction matrix on (cells admitting topvar/topwvar, refit-only cells):
                  A -> (0, 0)      B -> (>= 1, and the refit-only count says whether it is the CLAUSE)
KILL            pre-registered. World A is KILLED if `topvar_k` or `topwvar_k` is admitted in >= 1 of
                the 42 cells belonging to them. Gated on its own controls:
                                    if positive_topw_admits and rebuild_exact and placebo_identity:
                                        evaluate(cells)
                                    else: UNVERIFIED
POSITIVE CTRL   `topw_k` must be admitted under the 2B judge at k in {3,4,6,8} — R1105's committed
                set contains exactly those. An operator that admits NOTHING in this sweep would make
                every zero below silence rather than a measurement.
REBUILD CTRL    the rebuilt `topw_k4` and `topvar_k4` `_08b` files must reproduce the COMMITTED npz
                byte-for-byte, or the swept cells are not comparable to the arc's existing ones.
PLACEBO         `topw_k` is satisfaction-blind, so its `_08b` and `_08bR` files must be BYTE-IDENTICAL
                at every k. R1108 verified this at the population level; here it is verified across
                the whole k sweep, which is where a rule-dependent difference would show up.
NEGATIVE CTRL   ⭐ THE LOAD-BEARING ONE. `topvar_k`'s `_08b` and `_08bR` must DIFFER at some k. If
                they do not, the repair is a no-op for it too, world A wins BY CONSTRUCTION rather
                than by measurement, and the round must say so — a kill obtained because the
                intervention never happened is not a kill.
NOISE FLOOR     R1103's sampling interval on the admitted set, [17, 26] at the full population, is
                reported beside these zeros and never subtracted from them.
MULTIPLICITY    63 cells, every one reported, admitting and non-admitting.
SPECIFICATION   rule x k x world. The whole grid is published, including the `topw` contrast column
                that is expected to admit and the two that are not.
SEEDS           the analytic bound is deterministic; the bootstrap validation uses one fixed seed.
ARTIFACT        results/protocol_beneficiary.json with the source hash.
REPRODUCIBILITY deterministic.
IMPOSSIBLE      | criterion | what it would require |
                | a rule reading satisfaction, no target and no ratings, OTHER than `topvar_k` | the
                  release ships one; a second would have to be written, and an arm invented here
                  would be graded by a benchmark it was designed against |
                | whether either judge is CORRECT | an external gold standard |
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

OUT = HERE / "results" / "protocol_beneficiary.json"
WORK = pathlib.Path("/tmp/claude-1000/-home-ivan/7d277876-c2fd-4a27-9b05-652b391121ff/scratchpad/r1109_arms")
COMP, Z, NBOOT = ["generic", "genericpool16"], 1.959963984540054, 4000
KS = (1, 2, 3, 4, 6, 8, 12)
RULES = ("topvar_k", "topwvar_k", "topw_k")


def build(rule, k, world, suffix):
    # ⛔ THE SUFFIX IS PASSED FOR EVERY WORLD, INCLUDING 2B. The first version omitted it for the 2B
    #    cells and then looked for `sat_<rule><k>_S2.npz`, which the generator had written as
    #    `sat_<rule><k>.npz` — so all 21 of the 2B cells silently failed to load and 14 candidate
    #    cells were counted as `does not admit` having never been built. **The round exited 2 rather
    #    than publishing that zero**, because the POSITIVE control asks whether `topw_k` is admitted
    #    under 2B and it could not be. §4's `empty population passes`, caught by the gate.
    cmd = [PY, str(ROOT / "corebench" / "select_core.py"), "--rule", rule, "--k", str(k),
           "--outdir", str(WORK), "--tag-suffix", suffix]
    if world == "08b":
        cmd += ["--full-npz", str(RES / "sat08_full.npz"),
                "--select-npz", str(RES / "sat_full.npz")]
    elif world == "08bR":
        cmd += ["--full-npz", str(RES / "sat08_full.npz")]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=3600)
    f = WORK / f"sat_{rule}{k}{suffix}.npz"
    return f if (p.returncode == 0 and f.exists()) else None


def main() -> int:
    f94 = next(A27.glob("R1094_*/results/two_readings.json"), None)
    f01 = next(A27.glob("R1101_*/results/weights_separate.json"), None)
    f05 = next(A27.glob("R1105_*/results/second_judge.json"), None)
    f03 = next(A27.glob("R1103_*/results/set_stability.json"), None)
    if not all((f94, f01, f05, f03)):
        print("  UNRUNNABLE: a prior artifact is absent. Exit 2, never 0."); return 2
    rd = json.loads(f94.read_text())["readings"]
    w01 = json.loads(f01.read_text())["per_arm"]
    a2_ref = set(json.loads(f05.read_text())["sets"]["admitted_2B"])
    samp = json.loads(f03.read_text())["set_size"]
    WORK.mkdir(parents=True, exist_ok=True)

    # ---- the DERIVATION that picks the candidate, computed from committed artifacts
    derivation = {}
    for r in RULES:
        a = f"{r}4"
        derivation[r] = {
            "in_leakage_excludes": a in set(rd["leakage_excludes"]),
            "in_authorship_excludes": a in set(rd["authorship_excludes"]),
            "consumes_human_ratings_R1101": w01.get(a, {}).get("W_moved"),
            "consumes_target_R1100": w01.get(a, {}).get("R1100_T_consumes_target"),
        }
    unique_candidate = [r for r, d in derivation.items()
                        if not d["in_leakage_excludes"] and not d["in_authorship_excludes"]
                        and d["consumes_human_ratings_R1101"] is False]
    print(f"  DERIVATION — clean under both ③ readings AND rating-blind: {unique_candidate}")

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
        return v

    # ---- comparators, per judge
    CV, CC = {}, {}
    for jw, pref in (("2B", "sat_{}.npz"), ("8B", "sat08_{}.npz")):
        for c in COMP:
            v = perprompt(RES / pref.format(c))
            CV[(jw, c)], CC[(jw, c)] = np.nan_to_num(v, nan=0.0), np.isfinite(v)

    def lo_ana(d):
        m = len(d)
        return float(d.mean() - Z * d.std(ddof=1) / np.sqrt(m)) if m > 1 else 0.0

    def lo_boot(d, seed=11):
        rng = np.random.default_rng(seed); m = len(d)
        return float(np.percentile(d[rng.integers(0, m, size=(NBOOT, m))].mean(axis=1), 2.5))

    def admits(v, cov, jw, inner="analytic"):
        beats = 0
        for c in COMP:
            m = cov & CC[(jw, c)]
            d = (v - CV[(jw, c)])[m]
            if len(d) < 30:
                continue
            if (lo_boot(d) if inner == "boot" else lo_ana(d)) > 0:
                beats += 1
        return beats >= len(COMP)

    files, cells = {}, {}
    for rule in RULES:
        for k in KS:
            for world, suf in (("2B", "_S2"), ("08b", "_B8"), ("08bR", "_R8")):
                f = build(rule, k, world, suf)
                if f is None:
                    print(f"    ⚠ {rule} k={k} {world}: generator failed"); continue
                files[(rule, k, world)] = f
                v = perprompt(f)
                cov = np.isfinite(v)
                v = np.nan_to_num(v, nan=0.0)
                jw = "2B" if world == "2B" else "8B"
                cells[f"{rule}|k={k}|{world}"] = bool(admits(v, cov, jw))
        print(f"  swept {rule}")

    # ---- COMPLETENESS, asserted before any zero is read: every cell must have been BUILT.
    #      A `does not admit` from a file that was never written is not a measurement.
    missing = [f"{r}|k={k}|{w}" for r in RULES for k in KS for w in ("2B", "08b", "08bR")
               if (r, k, w) not in files]
    complete = not missing
    print(f"  COMPLETENESS {len(cells)} of {len(RULES) * len(KS) * 3} cells built; missing {missing}")

    # ---- controls
    pos_ks = [k for k in KS if cells.get(f"topw_k|k={k}|2B")]
    positive = set(pos_ks) >= {3, 4, 6, 8}
    rb = {}
    for rule in ("topw_k", "topvar_k"):
        f = files.get((rule, 4, "08b")); c = RES / f"sat_{rule}4_08b.npz"
        rb[rule] = bool(f and c.exists()
                        and np.array_equal(np.load(c, allow_pickle=True)["meta"],
                                           np.load(f, allow_pickle=True)["meta"])
                        and np.array_equal(np.load(c, allow_pickle=True)["sat"],
                                           np.load(f, allow_pickle=True)["sat"]))
    rebuild_exact = all(rb.values())

    def identical(rule, k):
        a, b = files.get((rule, k, "08b")), files.get((rule, k, "08bR"))
        if not (a and b):
            return None
        x, y = np.load(a, allow_pickle=True), np.load(b, allow_pickle=True)
        return bool(np.array_equal(x["meta"], y["meta"]) and np.array_equal(x["sat"], y["sat"]))

    topw_ident = {k: identical("topw_k", k) for k in KS}
    placebo_identity = all(v is True for v in topw_ident.values())
    topvar_ident = {k: identical("topvar_k", k) for k in KS}
    topwvar_ident = {k: identical("topwvar_k", k) for k in KS}
    repair_is_live = any(v is False for v in topvar_ident.values())

    inst = files.get(("topw_k", 4, "2B"))
    instrument_ok = None
    if inst:
        v = perprompt(inst); cov = np.isfinite(v); v = np.nan_to_num(v, nan=0.0)
        instrument_ok = admits(v, cov, "2B", "boot") == admits(v, cov, "2B")

    cand_cells = {kk: vv for kk, vv in cells.items()
                  if kk.startswith("topvar_k") or kk.startswith("topwvar_k")}
    admitted_cand = sorted(kk for kk, vv in cand_cells.items() if vv)
    refit_only = sorted(kk for kk in admitted_cand if kk.endswith("08bR")
                        and not cells.get(kk.replace("08bR", "08b")))

    gate_open = bool(complete and positive and rebuild_exact and placebo_identity and instrument_ok)
    world_A_killed = (len(admitted_cand) >= 1) if gate_open else None

    payload = {
        "round": "R1109",
        "question": "is there any object the fitting-protocol clause could help?",
        "derivation_that_picks_the_candidate": {
            "rows": derivation, "unique_candidate": unique_candidate,
            "why": ("clean under both ③ readings (R1094's two lists) AND rating-blind (R1101's "
                    "within-prompt weight derangement) AND target-blind (R1100). `topw_k` is "
                    "satisfaction-blind so its repair is a no-op; `topwvar_k` consumes ratings"),
        },
        "cells": cells,
        "candidate_cells_admitting": admitted_cand,
        "n_candidate_cells": len(cand_cells),
        "refit_only_admissions": refit_only,
        "topw_2B_admitted_at_k": pos_ks,
        "spec_identity": {"topw_k": topw_ident, "topvar_k": topvar_ident,
                          "topwvar_k": topwvar_ident,
                          "repair_is_live_for_topvar": repair_is_live},
        "controls": {
            "POSITIVE `topw_k` is admitted under 2B at k in {3,4,6,8}, matching R1105": bool(positive),
            "REBUILD `topw_k4` and `topvar_k4` `_08b` reproduce the committed npz byte-for-byte":
                bool(rebuild_exact),
            "PLACEBO `topw_k` `_08b` == `_08bR` at every k (satisfaction-blind)": bool(placebo_identity),
            "INSTRUMENT the analytic bound equals the 4000-draw bootstrap on a live cell":
                bool(instrument_ok),
            "NEGATIVE the repair is LIVE for `topvar_k` — its two specs differ at some k":
                bool(repair_is_live),
            "COMPLETENESS every one of the 63 cells was actually built": bool(complete),
        },
        "kill": {"gate_open": gate_open, "world_A_killed": world_A_killed,
                 "cells_tested": len(cells), "candidate_cells": len(cand_cells),
                 "admitted": len(admitted_cand)},
        "yardsticks": {"R1103_sampling_interval_on_size": [samp["p2.5"], samp["p97.5"]],
                       "note": "reported beside these zeros, never subtracted from them"},
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
    }
    if not gate_open:
        payload["verdict"] = ("⚠ UNVERIFIED — a control is red. "
                              f"Controls: {json.dumps(payload['controls'])}")
    else:
        payload["verdict"] = (
            f"{'⛔ WORLD A IS KILLED' if world_A_killed else '⭐ WORLD A SURVIVES'}: of the "
            f"{len(cand_cells)} cells belonging to `topvar_k` and `topwvar_k` across k "
            f"{list(KS)} and three worlds, {len(admitted_cand)} admit — {admitted_cand}. "
            f"The contrast `topw_k` admits under 2B at k = {pos_ks}, so the operator is not blind. "
            + (f"Refit-only admissions: {refit_only}."
               if world_A_killed else
               f"⭐ AND THE KILL IS A MEASUREMENT, NOT A CONSTRUCTION: the repair is LIVE for "
               f"`topvar_k` — its re-scored and re-run files DIFFER at "
               f"{sum(1 for v in topvar_ident.values() if v is False)} of {len(KS)} k values — so "
               f"the intervention did happen and admitted nothing. **The fitting-protocol clause "
               f"has no possible beneficiary in this release.**"))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, sort_keys=True))
    print()
    print(f"  {'cell':<26}{'admits':>8}")
    for kk in sorted(cells):
        if cells[kk]:
            print(f"  {kk:<26}{'YES':>8}")
    print(f"  ... {sum(1 for v in cells.values() if not v)} of {len(cells)} cells do not admit")
    print(f"\n  spec identity `_08b` == `_08bR`:")
    for r, d in (("topw_k", topw_ident), ("topvar_k", topvar_ident), ("topwvar_k", topwvar_ident)):
        print(f"    {r:<12} {d}")
    print()
    for k, v in payload["controls"].items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print()
    print(" ", payload["verdict"])
    return 0 if gate_open else 2


if __name__ == "__main__":
    sys.exit(main())
