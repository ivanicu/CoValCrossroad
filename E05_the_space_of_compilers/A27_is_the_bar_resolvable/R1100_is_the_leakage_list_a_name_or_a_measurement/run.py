#!/usr/bin/env python3
"""R1100 — clause ③ has been enforced by a NAME LIST read out of source. Execute it instead.

R1099's NEXT proposed scoring `topw_k1/k12/k2` against the released comparators to settle whether
they are baselines. ⛔ THAT QUESTION IS ALREADY ANSWERED AND ITS FRAMING IS WRONG. R1098's committed
`released` set contains `topw_k3, topw_k4, topw_k4_detA, topw_k4_detB, topw_k6, topw_k8` — six topw
arms DO resolvably beat both released comparators, and three do not. **`topw` has no single status;
`k` decides.** Re-scoring would have been bookkeeping, and the round says so before doing anything
else. §4's `the closing sentence is a claim and never gets a control`, committed by me one round ago.

So this round attacks the instrument underneath, which has never been executed. Clause ③ — *consumes
no prompt-specific human labels* — is operationalised in this arc by R1094's `leakage_excludes`, a
list of 19 NAMES. That list was built by READING `corebench/select_core.py` (its docstring says
`oracle_k ... LEAKY BY CONSTRUCTION`, and a branch names the three rules that open the target file).
R1084 measured a static source read at **precision 0.111, recall 1.000** against execution on this
very repo, and its ruling was `the parse can NOMINATE and it cannot DECIDE`. R1094's list was a
nomination that this arc has been treating as a decision. This round runs the confirmation.

ESTIMAND        for each generating configuration, TARGET-CONSUMPTION: does deranging the human
                rankings across prompts change the arm the generator emits? And PROMPT-CONSUMPTION:
                does deranging the prompt->rubric pairing change it? Both by INTERVENTION on the
                input file, re-running the real generator, comparing the emitted arrays.
IDENTIFICATION  identified for every configuration `corebench/select_core.py` can produce. NOT
                identified for `coval_core*`, `gen`, `generic`, `genericpool16`, `*_08bR`,
                `*_detA/B`, `*_kA/kB` — other generators or other judges; registered, not guessed.
UNIT OF THE     the emitted `sat_<tag>.npz` (meta, sat) arrays — i.e. WHICH criteria the rule
  INSTRUMENT    selected, per prompt, as satisfaction values indexed positionally.
UNIT OF THE     the same, for the T axis: the rubric is untouched there, so the emitted texts change
  CLAIM         iff the selection changes. ⚠ NOT the same for the P axis — there the rubric content
                itself moves, so texts change trivially and only the ARRAY comparison is the claim's
                unit. Both are computed and both are reported.
SCOPE           population: 11 configurations over 7 rules. instrument: the released generator, run
                unmodified against intervened data in an isolated root. baseline: the IDENTITY
                intervention. regime: 968 prompts, the 2B judge npz, fit-parity 1 where the rule
                fits.
WORLDS          A THE NAME LIST IS THE MEASUREMENT   every configuration's executed T-verdict agrees
                                    with its membership in R1094's `leakage_excludes`.
                B THE NAME LIST IS A PROXY THAT MISSES  >= 1 configuration disagrees, so clause ③ has
                                    been enforced by a string match and every ③-scoped statement in
                                    this arc (R1094, R1095, R1099) inherits that list's errors.
                Prediction matrix on (disagreements, oracle changes):
                  A -> (0, yes)    B -> (>= 1, yes)
                ⚠ `oracle changes` is in BOTH rows: it is the harness control, not a separator.
KILL            pre-registered. World A is KILLED if >= 1 configuration's executed T-verdict differs
                from its `leakage_excludes` membership, AND the harness controls below are green —
                a disagreement while the harness is broken is UNVERIFIED, never a kill.
                                    if pos_ctrl and identity_clean: evaluate(disagreements)
                                    else:                           UNVERIFIED
POSITIVE CTRL   T axis: `oracle_k4_fit1` MUST change under T-derange. It is the arm the release
                labels leaky by construction. If it does not, the intervened root is not being read
                and every `unchanged` in this round is silence rather than a measurement.
                P axis: `full` MUST change under P-derange — it selects every judged index, so a
                different rubric moves it. If it does not, the P intervention did not land.
g=0 GUARD       the IDENTITY intervention (byte copy, nothing deranged) must change NOTHING, for
                every configuration. This is the check that the harness can return `unchanged` —
                without it, `oracle changed` is compatible with `the copy is always different`.
NEGATIVE CTRL   the derangements must have NO fixed points and must preserve the record count and
                the join size, so `changed` cannot be produced by records going missing.
SHAM            the same intervention pipeline with the derangement replaced by the identity
                permutation — same file rewrite, same I/O, same size, minus the ingredient (the
                destruction of the pairing). This is the IDENTITY arm above, and it is a sham in
                §1's exact sense rather than a poison: nothing is misdirected, one thing is absent.
PLACEBO         `random_k4` reads neither the target nor the rubric CONTENT — only which indices are
                judged. It must be unchanged on T. It is the contrast that must return exactly zero.
⚠ SCOPE OF P    the P axis answers `does the arm consume the prompt's own rubric RECORD`. It is NOT
                an instrument for clause ③'s AUTHORSHIP reading, and the round computes the witness
                rather than asserting it: `random_k4` reads no human content at all and still moves
                under P, because deranging the record changes which indices are judged. So P cannot
                separate `consumes the human WEIGHTS` from `consumes the candidate SET`. Reported as
                a limitation with its witness; the separating intervention is named in NEXT.
NOISE FLOOR     none needed: the comparison is exact array equality, not an estimate. Stated rather
                than fabricated.
MULTIPLICITY    11 configurations x 2 axes = 22 cells, all reported, survivors and non-survivors.
SPECIFICATION   rule x k, with topw swept at k in {1, 4, 12} — the k values that R1098 places on
                BOTH sides of the released bound, so the sweep spans the disagreement it explains.
SEEDS           the derangements use 3 seeds; a verdict counts only if all three agree. And the seed
                flag is VERIFIED to change the draw — the leaky arm must emit 3 DISTINCT results
                under T, or `agrees across 3 seeds` is one run reported three times. That check gates
                the kill alongside the others.
ARTIFACT        results/leakage_executed.json with the source hash.
REPRODUCIBILITY deterministic given the seeds; two seeds are compared cell by cell.
IMPOSSIBLE      | criterion | what it would require |
                | the executed verdict for `coval_core`, `gen`, `generic`, `genericpool16` | their
                  generators; `select_core.py` does not produce them, and `core_generic.json` is a
                  fixed 4-criterion list repeated on all 968 prompts, so it has no rule to re-run |
                | the verdict for `*_08bR` arms | the 8B judge npz, a different instrument axis |
                | cross-release | a second release |
"""
from __future__ import annotations

import hashlib, json, os, pathlib, shutil, subprocess, sys, tempfile
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
OUT = HERE / "results" / "leakage_executed.json"
A27 = ROOT / "E05_the_space_of_compilers" / "A27_is_the_bar_resolvable"
PY = str(ROOT / ".venv" / "bin" / "python")
SEEDS = (11, 23, 41)

# rule, k, fit_parity, emitted tag
CONFIGS = [
    ("topw_k", 1, -1, "topw_k1"),
    ("topw_k", 4, -1, "topw_k4"),
    ("topw_k", 12, -1, "topw_k12"),
    ("topabs_k", 4, -1, "topabs_k4"),
    ("topvar_k", 4, -1, "topvar_k4"),
    ("topwvar_k", 4, -1, "topwvar_k4"),
    ("random_k", 4, -1, "random_k4_s0"),
    ("full", 4, -1, "full"),
    ("indep_k", 4, 1, "indep_k4_fit1"),
    ("greedy_k", 4, 1, "greedy_k4_fit1"),
    ("oracle_k", 4, 1, "oracle_k4_fit1"),
]


def derangement(n: int, rng) -> list[int]:
    """A permutation with no fixed point. Rejection-sampled; n >= 2."""
    while True:
        p = rng.permutation(n)
        if not any(p[i] == i for i in range(n)):
            return [int(x) for x in p]


def write_data(dst: pathlib.Path, axis: str, seed: int) -> dict:
    """Materialise data/ under `dst`. axis in {identity, T, P}. Returns the intervention's stats."""
    dst.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    comp = (ROOT / "data" / "comparisons.jsonl").read_text(encoding="utf-8").splitlines()
    rub = (ROOT / "data" / "conversation_rubrics.jsonl").read_text(encoding="utf-8").splitlines()
    comp = [l for l in comp if l.strip()]
    rub = [l for l in rub if l.strip()]
    stats = {"n_comparisons": len(comp), "n_rubrics": len(rub), "fixed_points": None}

    if axis == "T":
        recs = [json.loads(l) for l in comp]
        perm = derangement(len(recs), rng)
        blocks = [r.get("metadata", {}).get("assessments", []) for r in recs]
        for i, r in enumerate(recs):
            r.setdefault("metadata", {})["assessments"] = blocks[perm[i]]
        stats["fixed_points"] = sum(1 for i, j in enumerate(perm) if i == j)
        comp = [json.dumps(r) for r in recs]
    elif axis == "P":
        recs = [json.loads(l) for l in rub]
        perm = derangement(len(recs), rng)
        fulls = [r.get("coval_full") for r in recs]
        for i, r in enumerate(recs):
            r["coval_full"] = fulls[perm[i]]
        stats["fixed_points"] = sum(1 for i, j in enumerate(perm) if i == j)
        rub = [json.dumps(r) for r in recs]
    elif axis != "identity":
        raise ValueError(axis)

    (dst / "comparisons.jsonl").write_text("\n".join(comp) + "\n", encoding="utf-8")
    (dst / "conversation_rubrics.jsonl").write_text("\n".join(rub) + "\n", encoding="utf-8")
    return stats


def build_root(base: pathlib.Path, axis: str, seed: int) -> tuple[pathlib.Path, dict]:
    """An isolated ROOT. ⚠ select_core.py must be COPIED, never symlinked: it computes ROOT with
    Path(__file__).resolve(), which follows symlinks straight back to the real repo and would make
    every intervention a silent no-op."""
    r = base / f"{axis}_{seed}"
    (r / "corebench").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "corebench" / "select_core.py", r / "corebench" / "select_core.py")
    for name in ("covalx", "E01_the_rubric_was_the_object"):
        os.symlink(ROOT / name, r / name)
    stats = write_data(r / "data", axis, seed)
    return r, stats


def emit(root: pathlib.Path, rule: str, k: int, fit: int, tag: str) -> tuple | None:
    outdir = root / "arms"
    cmd = [PY, str(root / "corebench" / "select_core.py"), "--rule", rule, "--outdir", str(outdir)]
    if rule != "full":
        cmd += ["--k", str(k)]
    if fit >= 0:
        cmd += ["--fit-parity", str(fit)]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(root), timeout=1800)
    npz = outdir / f"sat_{tag}.npz"
    if p.returncode != 0 or not npz.exists():
        return None
    d = np.load(npz, allow_pickle=True)
    meta = np.array([str(x) for x in d["meta"]])
    sat = np.asarray(d["sat"], np.float32)
    core = json.loads((outdir / f"core_{tag}.json").read_text())
    joins = [l for l in p.stdout.splitlines() if "join:" in l]
    return (hashlib.sha256(meta.tobytes()).hexdigest(), hashlib.sha256(sat.tobytes()).hexdigest(),
            hashlib.sha256(json.dumps(core, sort_keys=True).encode()).hexdigest(),
            len(core), joins[0].strip() if joins else "")


def main() -> int:
    f94 = next(A27.glob("R1094_*/results/two_readings.json"), None)
    f98 = next(A27.glob("R1098_*/results/families_nest.json"), None)
    if f94 is None or f98 is None:
        print("  UNRUNNABLE: a prior artifact is absent. Exit 2, never 0."); return 2
    leak = set(json.loads(f94.read_text())["readings"]["leakage_excludes"])
    sets98 = json.loads(f98.read_text())["sets"]

    scratch = os.environ.get("R1100_SCRATCH") or tempfile.gettempdir()
    base = pathlib.Path(tempfile.mkdtemp(prefix="r1100_", dir=scratch))
    print(f"  isolated roots under {base}")
    results, ivstats = {}, {}
    try:
        for axis in ("identity", "T", "P"):
            for seed in SEEDS:
                root, st = build_root(base, axis, seed)
                ivstats[f"{axis}_{seed}"] = st
                for rule, k, fit, tag in CONFIGS:
                    got = emit(root, rule, k, fit, tag)
                    results.setdefault(tag, {})[f"{axis}_{seed}"] = got
                    if got is None:
                        print(f"    ⚠ {axis}/{seed}/{tag}: generator failed")
                print(f"  {axis} seed {seed}: {len(CONFIGS)} configs emitted")
    finally:
        pass

    # ---- verdicts: a cell is `changed` iff the emitted arrays differ from the identity run
    per_arm, unrunnable = {}, []
    for _rule, _k, _fit, tag in CONFIGS:
        row = results[tag]
        if any(row[f"{a}_{s}"] is None for a in ("identity", "T", "P") for s in SEEDS):
            unrunnable.append(tag); continue
        ref = row[f"identity_{SEEDS[0]}"]
        ident_clean = all(row[f"identity_{s}"][:3] == ref[:3] for s in SEEDS)
        vT = [row[f"T_{s}"][:3] != ref[:3] for s in SEEDS]
        vP_sel = [row[f"P_{s}"][:2] != ref[:2] for s in SEEDS]
        vP_txt = [row[f"P_{s}"][2] != ref[2] for s in SEEDS]
        per_arm[tag] = {
            "identity_stable_across_seeds": ident_clean,
            "T_changed": all(vT), "T_seed_agreement": len(set(vT)) == 1,
            "P_selection_changed": all(vP_sel), "P_seed_agreement": len(set(vP_sel)) == 1,
            "P_texts_changed": all(vP_txt),
            "in_R1094_leakage_excludes": tag in leak,
            "n_prompts_identity": ref[3],
            "join_identity": ref[4],
        }

    # ---- controls
    pos_T = per_arm.get("oracle_k4_fit1", {}).get("T_changed") is True
    pos_P = per_arm.get("full", {}).get("P_selection_changed") is True
    g0 = all(v["identity_stable_across_seeds"] for v in per_arm.values())
    placebo = per_arm.get("random_k4_s0", {}).get("T_changed") is False
    no_fixed = all(s["fixed_points"] == 0 for k, s in ivstats.items() if not k.startswith("identity"))
    counts_kept = len({s["n_comparisons"] for s in ivstats.values()}) == 1 and \
                  len({s["n_rubrics"] for s in ivstats.values()}) == 1
    joins_kept = len({v["join_identity"] for v in per_arm.values() if v["join_identity"]}) == 1
    seed_ok = all(v["T_seed_agreement"] and v["P_seed_agreement"] for v in per_arm.values())
    # ⚠ THE SEED FLAG MUST BE SHOWN TO CHANGE THE DRAWS. Three seeds that silently produce the same
    #    permutation would make `agrees across 3 seeds` one run reported three times. A leaky arm's
    #    emitted values must therefore DIFFER between T seeds -- different derangement, different
    #    targets, different selection.
    seeds_differ = len({results["oracle_k4_fit1"][f"T_{s}"][1] for s in SEEDS}) == len(SEEDS)
    controls = {
        "POSITIVE T oracle_k4_fit1 changes when the rankings are deranged": pos_T,
        "POSITIVE P full changes when the rubric pairing is deranged": pos_P,
        "g=0 the identity intervention changes NOTHING, every config": g0,
        "PLACEBO random_k4 is unchanged on T": placebo,
        "NEGATIVE the derangements have zero fixed points": no_fixed,
        "NEGATIVE record counts are preserved by every intervention": counts_kept,
        "NEGATIVE the join size is identical across configs": joins_kept,
        "SEEDS every verdict agrees across 3 seeds": seed_ok,
        "SEEDS the seed flag CHANGES the draw: 3 distinct oracle emissions under T": seeds_differ,
    }

    # ---- the kill, gated on its own controls (a kill that can fire on a broken instrument is not
    #      a commitment). Only then is the pre-registered threshold binding.
    disagree = sorted(t for t, v in per_arm.items()
                      if v["T_changed"] != v["in_R1094_leakage_excludes"])
    gate_open = (pos_T and pos_P and g0 and placebo and no_fixed and counts_kept and seed_ok
                 and seeds_differ)
    if gate_open:
        world_A_killed = len(disagree) >= 1
        verdict_status = "EVALUATED"
    else:
        world_A_killed = None
        verdict_status = "UNVERIFIED — a control is red, so the threshold is not binding"

    # ---- the bookkeeping R1099's NEXT actually asked for, labelled as a derivation
    rel = set(sets98["released"])
    topw_released = sorted(t for t in rel if t.startswith("topw"))
    topw_blind_only = sorted(t for t in set(sets98["blind_minus_comparators"]) - rel
                             if t.startswith("topw"))

    n_changed_T = sum(1 for v in per_arm.values() if v["T_changed"])
    # ⚠ The P axis' own scope, COMPUTED not typed. If the placebo — an arm that reads no human
    #   content — moves under P, then P is measuring `the record moved`, not `human authorship was
    #   consumed`, and no authorship statement may be built on it.
    p_placebo_moves = per_arm.get("random_k4_s0", {}).get("P_selection_changed") is True
    p_all_move = all(v["P_selection_changed"] for v in per_arm.values())
    p_authorship_valid = not p_placebo_moves
    payload = {
        "round": "R1100",
        "question": "is clause ③'s leakage list a name list or a measurement?",
        "refuses": {
            "claim": "whether the three topw arms in the surviving slack are baselines too",
            "round": "R1099 (its NEXT line)",
            "status": "REFUSED AS FRAMED — bookkeeping, and the framing presupposes topw has one status",
            "why": ("R1098's committed released ②′ set already contains "
                    f"{topw_released} and excludes {topw_blind_only}. Six topw arms DO resolvably "
                    "beat both released comparators. `topw` is not a baseline or a candidate; k is."),
            "derivation_not_measurement": True,
        },
        "per_arm": per_arm,
        "unrunnable_configs": unrunnable,
        "intervention_stats": ivstats,
        "controls": controls,
        "kill": {"gate_open": gate_open, "status": verdict_status,
                 "world_A_killed": world_A_killed, "disagreements": disagree},
        "P_axis_scope": {
            "measures": "does the arm consume the prompt's own rubric RECORD",
            "all_configs_move": p_all_move,
            "placebo_random_k4_moves": p_placebo_moves,
            "valid_as_an_authorship_instrument": p_authorship_valid,
            "why": ("`random_k4` reads no criterion text, no human weight and no human label — it "
                    "draws uniformly from the judged index set, and the only human-determined thing "
                    "it touches is HOW MANY criteria the prompt has — so its movement under P is the "
                    "candidate SET changing, not authorship being consumed. P therefore cannot be "
                    "read as clause ③'s AUTHORSHIP reading, and this round makes no authorship "
                    "claim."),
            "separating_intervention": ("derange the per-criterion human `scores` WITHIN each "
                                        "prompt's own rubric, leaving the texts and the index set "
                                        "untouched. `topw_k`, `topabs_k`, `topwvar_k` must move; "
                                        "`topvar_k`, `random_k`, `full` must not."),
        },
        "grid": {"cells_tested": len(per_arm) * 2, "T_changed": n_changed_T,
                 "T_unchanged": len(per_arm) - n_changed_T,
                 "P_selection_changed": sum(1 for v in per_arm.values() if v["P_selection_changed"])},
        "seeds": list(SEEDS),
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
    }
    if gate_open:
        payload["verdict"] = (
            f"⭐ EXECUTED: {n_changed_T} of {len(per_arm)} configurations consume the human target. "
            f"Disagreements with R1094's name list: {len(disagree)} {disagree}. "
            + ("World A survives — the name list reproduces the executed verdict exactly, so clause "
               "③'s instrument is validated rather than merely asserted."
               if not disagree else
               "World A is KILLED — clause ③ has been enforced by a string match that the "
               "intervention contradicts.")
            + (f" ⚠ AND THE P AXIS CARRIES NO AUTHORSHIP CLAIM: all "
               f"{payload['grid']['P_selection_changed']} configurations move under it, INCLUDING "
               f"the placebo `random_k4`, which reads no criterion text, no human weight and no "
               f"human label — so P measures the record moving, not authorship being consumed."
               if not p_authorship_valid else
               " The P axis' placebo held, so P may carry an authorship reading."))
    else:
        payload["verdict"] = ("⚠ UNVERIFIED. " + verdict_status +
                              f" Controls: {json.dumps(controls)}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, sort_keys=True))
    print()
    for t, v in per_arm.items():
        print(f"  {t:16s} T={'CONSUMES' if v['T_changed'] else 'blind   '} "
              f"P_sel={'changes' if v['P_selection_changed'] else 'stable '} "
              f"R1094_leaky={v['in_R1094_leakage_excludes']}")
    print()
    for k, v in controls.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print()
    print(" ", payload["verdict"])
    shutil.rmtree(base, ignore_errors=True)
    return 0 if gate_open else 2


if __name__ == "__main__":
    sys.exit(main())
