#!/usr/bin/env python3
"""R1101 — does `topw` consume prompt-specific HUMAN RATINGS? The within-prompt weight derangement.

R1100 executed clause ③'s LEAKAGE reading and reproduced R1094's name list exactly (11/11). It could
not touch the AUTHORSHIP reading, because its P axis deranged the whole rubric record and therefore
moved `random_k4` too — an arm that reads no criterion text, no human weight and no human label. That
axis measures `the record moved`, never `authorship was consumed`, and R1100 built no claim on it.

This is the separator R1100 named. Permute, WITHIN each prompt, which criterion carries which
annotator `scores` list. The criterion TEXTS stay where they are, the criterion COUNT is identical,
the judged index set `ok` is identical, and the satisfaction npz is untouched — so the ONLY thing that
moves is the vector of human importance ratings `w[i] = mean(scores)`.

⛔ WHY IT MATTERS AND WHY IT IS NOT MORE BOOKKEEPING. Six `topw` arms — k ∈ {3,4,6,8} — are in
R1098's committed released ②′ set. `coval_full` is crowd-written and its weights are human-assigned
signed ratings (dataset card). **If `topw` ranks by those ratings, then clause ③'s AUTHORSHIP reading
excludes six arms the definition currently admits** — which is a change to the admitted set, not to a
list of names. The round therefore also computes the LADDER — how large the admitted set is under
each reading — because R1094 established that ③'s own control cannot separate its two readings, and
what a control cannot settle, a COST sometimes can.

ESTIMAND        for each generating configuration, WEIGHT-CONSUMPTION: does deranging the human
                importance ratings WITHIN a prompt change the criteria the rule selects? Reported
                twice — binary (any prompt moved) and graded (the share of prompts whose selected set
                changed), because a binary verdict cannot distinguish `ranks by w` from `touches w`.
IDENTIFICATION  identified for every configuration `corebench/select_core.py` produces. The same
                arms R1100 could not reach are unreachable here for the same reasons; registered.
UNIT OF THE     the emitted `sat_<tag>.npz` (meta, sat) arrays — which criteria were selected. Under
  INSTRUMENT    W the texts and the index set are FIXED, so this is exactly the selection.
UNIT OF THE     the same. ⚠ This is the equality R1100's P axis did NOT have, and it is why that axis
  CLAIM         was disqualified: there `the record moved` and `the selection consumed authorship`
                were different strings.
SCOPE           population: 11 configurations over 7 rules. instrument: the released generator, run
                unmodified against intervened data in isolated roots. baseline: the untouched file.
                regime: 968 prompts, the 2B judge npz, fit-parity 1 where the rule fits.
WORLDS          A THE WEIGHTS ARE NOT SEPARABLE HERE   the executed partition does not match the
                                    pre-registration — some predicted-stable rule moves, or a
                                    predicted-mover does not. The intervention is confounded and NO
                                    authorship statement follows from it either.
                B `topw` RANKS BY HUMAN RATINGS   exactly {topw_k*, topabs_k4, topwvar_k4} move and
                                    the other 8 are stable. Then ③'s authorship reading, executed
                                    rather than named, removes the six admitted `topw` arms.
                PRE-REGISTERED PARTITION, written before the run and derived from the source:
                  MOVE   : topw_k1, topw_k4, topw_k12, topabs_k4, topwvar_k4   (rank on w or |w|)
                  STABLE : topvar_k4, random_k4, full, indep_k4, greedy_k4, oracle_k4  (never read w)
                ⚠ The STABLE set deliberately contains the three LEAKY arms. If the intervention were
                  too broad, they would move — so this prediction has both directions populated and
                  is not a one-sided confirmation.
KILL            pre-registered. World B is KILLED if the executed partition differs from the
                pre-registration in ANY of the 11 cells. Gated on its own controls:
                                    if sham_clean and pos_reverse: evaluate(partition)
                                    else:                          UNVERIFIED
SHAM            ⭐ THE LOAD-BEARING CONTROL. The same file rewrite — full JSON parse and re-serialise
                of every rubric record — with the permutation set to the IDENTITY. Same operation,
                same I/O, same size, minus the ingredient. If any arm moves under it, the round is
                VOID, because the round-trip itself (float re-formatting, key order) changed `w` and
                every W verdict would be measuring serialisation. A byte copy could NOT catch this.
POSITIVE CTRL   a REVERSAL axis: within each prompt the scores are reassigned in reverse rank order,
                so `topw_k1` must now select the criterion that previously had the LOWEST weight.
                This requires an exact PREDICTED OUTCOME, not merely `something changed` — a control
                that only asks `did it move` shares the instrument's blind spot.
NEGATIVE CTRL   the derangement is within-prompt and has zero fixed points per prompt; the criterion
                texts, the criterion count and the judged index set are asserted unchanged, so
                `moved` cannot be produced by the candidate set shifting.
PLACEBO         `random_k4` and `full` must be EXACTLY stable under W. They ignore `w` entirely.
NOISE FLOOR     none needed for the binary verdict (exact array equality). The GRADED verdict's floor
                is the sham's per-prompt change rate, which must be 0.000.
MULTIPLICITY    11 configurations x 3 axes = 33 cells, all reported, movers and non-movers.
SPECIFICATION   rule x k, topw swept at k in {1, 4, 12} — spanning R1098's released bound.
SEEDS           W at 3 seeds; a verdict counts only if all three agree, and the seed flag is verified
                to change the draw (3 distinct emissions for a mover).
ARTIFACT        results/weights_separate.json with the source hash.
REPRODUCIBILITY deterministic given the seeds.
IMPOSSIBLE      | criterion | what it would require |
                | `coval_core*`, `gen`, `generic`, `genericpool16` | their generators; `select_core.py`
                  does not produce them |
                | `*_08bR`, `*_detA/B`, `*_kA/kB` | the 8B judge npz / tag-suffix provenance |
                | whether the ANNOTATORS' ratings are `human labels` in the release's own sense | an
                  external reading of the clause; the dataset card's wording is quoted, not adjudicated |
                | cross-release | a second release |
"""
from __future__ import annotations

import hashlib, json, os, pathlib, shutil, subprocess, sys, tempfile
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))          # the reversal control imports covalx.judge.load_join
OUT = HERE / "results" / "weights_separate.json"
A27 = ROOT / "E05_the_space_of_compilers" / "A27_is_the_bar_resolvable"
PY = str(ROOT / ".venv" / "bin" / "python")
SEEDS = (11, 23, 41)

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

# ⛔ WRITTEN BEFORE THE RUN, derived from `select_core.py`: `w` is read by topw_k (`-w[i]`),
#    topabs_k (`-abs(w[i])`) and topwvar_k (`-(abs(w[i]) * var[i])`) and by nothing else.
PREREG_MOVE = {"topw_k1", "topw_k4", "topw_k12", "topabs_k4", "topwvar_k4"}


def within_prompt_perm(n: int, rng, mode: str) -> list[int]:
    if mode == "identity":
        return list(range(n))
    if mode == "reverse":
        return list(range(n))[::-1]
    while True:                                   # derangement: no criterion keeps its own ratings
        p = rng.permutation(n)
        if not any(p[i] == i for i in range(n)):
            return [int(x) for x in p]


def write_data(dst: pathlib.Path, axis: str, seed: int) -> dict:
    """axis in {identity, sham, W, reverse}. `identity` is a byte copy; `sham` is the full JSON
    round-trip with the identity permutation — the two differ exactly by the serialisation."""
    dst.mkdir(parents=True, exist_ok=True)
    os.symlink(ROOT / "data" / "comparisons.jsonl", dst / "comparisons.jsonl")
    rub_p = ROOT / "data" / "conversation_rubrics.jsonl"
    st = {"n_rubrics": 0, "fixed_points": 0, "singletons": 0, "texts_preserved": True,
          "counts_preserved": True}

    if axis == "identity":
        shutil.copy2(rub_p, dst / "conversation_rubrics.jsonl")
        st["n_rubrics"] = sum(1 for l in open(rub_p, encoding="utf-8") if l.strip())
        return st

    mode = {"sham": "identity", "W": "derange", "reverse": "reverse"}[axis]
    rng = np.random.default_rng(seed)
    out = []
    for line in open(rub_p, encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        items = rec.get("coval_full") or []
        n = len(items)
        st["n_rubrics"] += 1
        if n < 2:
            st["singletons"] += 1
            out.append(json.dumps(rec)); continue
        if mode == "reverse":
            # reassign scores in REVERSE RANK order: the highest-mean list goes to the criterion
            # that had the lowest mean, so argmax(w) must become the old argmin(w).
            means = [float(np.mean([s["score"] for s in (it.get("scores") or [])]) or 0.0)
                     for it in items]
            order = sorted(range(n), key=lambda i: means[i])          # ascending
            perm = [0] * n
            for rank, i in enumerate(order):
                perm[i] = order[n - 1 - rank]                          # i receives its mirror's list
        else:
            perm = within_prompt_perm(n, rng, mode)
        st["fixed_points"] += sum(1 for i, j in enumerate(perm) if i == j and mode == "derange")
        scores = [it.get("scores") for it in items]
        texts = [it.get("criterion") for it in items]
        for i, it in enumerate(items):
            it["scores"] = scores[perm[i]]
        if [it.get("criterion") for it in items] != texts:
            st["texts_preserved"] = False
        if len(items) != n:
            st["counts_preserved"] = False
        out.append(json.dumps(rec))
    (dst / "conversation_rubrics.jsonl").write_text("\n".join(out) + "\n", encoding="utf-8")
    return st


def build_root(base: pathlib.Path, axis: str, seed: int) -> tuple[pathlib.Path, dict]:
    """⚠ select_core.py is COPIED, never symlinked: it computes ROOT with Path(__file__).resolve(),
    which follows symlinks back to the real repo and would make every intervention a no-op. Measured
    in R1100, not assumed."""
    r = base / f"{axis}_{seed}"
    (r / "corebench").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "corebench" / "select_core.py", r / "corebench" / "select_core.py")
    for name in ("covalx", "E01_the_rubric_was_the_object"):
        os.symlink(ROOT / name, r / name)
    return r, write_data(r / "data", axis, seed)


def emit(root: pathlib.Path, rule: str, k: int, fit: int, tag: str):
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
    return {"meta_h": hashlib.sha256(meta.tobytes()).hexdigest(),
            "sat_h": hashlib.sha256(sat.tobytes()).hexdigest(),
            "core": {p_: sorted(v) for p_, v in core.items()},
            "n_prompts": len(core)}


def changed_rate(ref, got) -> float:
    """Share of prompts whose SELECTED CRITERION SET changed. Graded, because a binary verdict cannot
    tell `ranks by w` from `brushes against w`."""
    keys = set(ref["core"]) & set(got["core"])
    if not keys:
        return float("nan")
    return sum(1 for kk in keys if ref["core"][kk] != got["core"][kk]) / len(keys)


def main() -> int:
    f98 = next(A27.glob("R1098_*/results/families_nest.json"), None)
    f00 = next(A27.glob("R1100_*/results/leakage_executed.json"), None)
    f94 = next(A27.glob("R1094_*/results/two_readings.json"), None)
    if f98 is None or f00 is None or f94 is None:
        print("  UNRUNNABLE: a prior artifact is absent. Exit 2, never 0."); return 2
    rel = set(json.loads(f98.read_text())["sets"]["released"])
    r1100 = json.loads(f00.read_text())["per_arm"]
    rd = json.loads(f94.read_text())["readings"]
    leak_x, auth_x = set(rd["leakage_excludes"]), set(rd["authorship_excludes"])

    scratch = os.environ.get("R1101_SCRATCH") or tempfile.gettempdir()
    base = pathlib.Path(tempfile.mkdtemp(prefix="r1101_", dir=scratch))
    print(f"  isolated roots under {base}")
    AXES = [("identity", SEEDS[0]), ("sham", SEEDS[0]), ("reverse", SEEDS[0])] + \
           [("W", s) for s in SEEDS]
    res, ivst = {}, {}
    for axis, seed in AXES:
        root, st = build_root(base, axis, seed)
        ivst[f"{axis}_{seed}"] = st
        for rule, k, fit, tag in CONFIGS:
            got = emit(root, rule, k, fit, tag)
            res.setdefault(tag, {})[f"{axis}_{seed}"] = got
            if got is None:
                print(f"    ⚠ {axis}/{seed}/{tag}: generator failed")
        print(f"  {axis} seed {seed}: {len(CONFIGS)} configs emitted")

    ident = f"identity_{SEEDS[0]}"
    per_arm, unrunnable = {}, []
    for _r, _k, _f, tag in CONFIGS:
        row = res[tag]
        if any(v is None for v in row.values()):
            unrunnable.append(tag); continue
        ref = row[ident]
        sham = row[f"sham_{SEEDS[0]}"]
        rev = row[f"reverse_{SEEDS[0]}"]
        wv = [row[f"W_{s}"] for s in SEEDS]
        moved = [(w["meta_h"], w["sat_h"]) != (ref["meta_h"], ref["sat_h"]) for w in wv]
        per_arm[tag] = {
            "sham_clean": (sham["meta_h"], sham["sat_h"]) == (ref["meta_h"], ref["sat_h"]),
            "sham_rate": changed_rate(ref, sham),
            "W_moved": all(moved), "W_seed_agreement": len(set(moved)) == 1,
            "W_rate_per_seed": [round(changed_rate(ref, w), 4) for w in wv],
            "reverse_moved": (rev["meta_h"], rev["sat_h"]) != (ref["meta_h"], ref["sat_h"]),
            "reverse_rate": round(changed_rate(ref, rev), 4),
            "prereg_move": tag in PREREG_MOVE,
            "R1100_T_consumes_target": r1100.get(tag, {}).get("T_changed"),
            "in_released_2prime": tag in rel,
        }

    # ---- the REVERSAL positive control, an exact predicted outcome rather than `it moved`
    rev_root = base / f"reverse_{SEEDS[0]}"
    id_root = base / f"identity_{SEEDS[0]}"
    def top1(root):
        c = json.loads((root / "arms" / "core_topw_k1.json").read_text())
        return {p_: v[0] for p_, v in c.items() if v}
    def bottom1_from_identity():
        """the criterion with the LOWEST mean human rating, per prompt, from the UNTOUCHED file"""
        low = {}
        from covalx.judge import load_join
        joined = load_join(id_root / "data" / "comparisons.jsonl",
                           id_root / "data" / "conversation_rubrics.jsonl")
        for pid, _pr, r in joined:
            items = r.get("coval_full") or []
            if not items:
                continue
            m = [float(np.mean([s["score"] for s in (it.get("scores") or [])]) or 0.0)
                 for it in items]
            low[pid] = items[int(np.argmin(m))]["criterion"]
        return low
    t1_rev, low = top1(rev_root), bottom1_from_identity()
    shared = [p_ for p_ in t1_rev if p_ in low]
    rev_hits = sum(1 for p_ in shared if t1_rev[p_] == low[p_])
    rev_frac = rev_hits / len(shared) if shared else float("nan")
    # ⚠ NOT required to be 1.000: `ok` excludes criteria unjudged in the npz, so the argmin over the
    #    FULL rubric can be outside the candidate set. The threshold is stated as a floor, and the
    #    identity run's own rate is the comparison that makes it a measurement rather than a number.
    t1_id = top1(id_root)
    base_hits = sum(1 for p_ in shared if p_ in t1_id and t1_id[p_] == low[p_])
    base_frac = base_hits / len(shared) if shared else float("nan")

    sham_clean = all(v["sham_clean"] for v in per_arm.values())
    sham_rate0 = all(v["sham_rate"] == 0.0 for v in per_arm.values())
    placebo = (per_arm.get("random_k4_s0", {}).get("W_moved") is False
               and per_arm.get("full", {}).get("W_moved") is False)
    no_fixed = all(s["fixed_points"] == 0 for k, s in ivst.items() if k.startswith("W_"))
    struct = all(s["texts_preserved"] and s["counts_preserved"] for s in ivst.values())
    seed_ok = all(v["W_seed_agreement"] for v in per_arm.values())
    movers = [t for t, v in per_arm.items() if v["W_moved"]]
    seeds_differ = (len({res[movers[0]][f"W_{s}"]["sat_h"] for s in SEEDS}) == len(SEEDS)
                    if movers else False)
    pos_reverse = (rev_frac > base_frac + 0.5) if shared else False

    controls = {
        "SHAM the JSON round-trip alone moves NOTHING (else the round is void)": sham_clean,
        "SHAM the round-trip's per-prompt change rate is exactly 0.000": sham_rate0,
        "POSITIVE reversal makes topw_k1 select the previously LOWEST-rated criterion": pos_reverse,
        "PLACEBO random_k4 and full are exactly stable under W": placebo,
        "NEGATIVE the within-prompt derangements have zero fixed points": no_fixed,
        "NEGATIVE criterion texts and counts are preserved by every intervention": struct,
        "SEEDS every W verdict agrees across 3 seeds": seed_ok,
        "SEEDS the seed flag CHANGES the draw: distinct emissions for a mover": seeds_differ,
    }

    executed_move = {t for t, v in per_arm.items() if v["W_moved"]}
    mismatch = sorted(executed_move ^ PREREG_MOVE)
    gate_open = (sham_clean and sham_rate0 and pos_reverse and placebo and no_fixed and struct
                 and seed_ok and seeds_differ)
    world_B_killed = (len(mismatch) >= 1) if gate_open else None

    # ---- the CONSEQUENCE, labelled a derivation: it follows from the W partition and R1098's set
    topw_admitted = sorted(t for t in rel if t.startswith("topw"))
    after_leak = sorted(rel - leak_x)
    after_auth = sorted(rel - auth_x)
    after_auth_plus = sorted(rel - auth_x - set(topw_admitted))
    consequence = {
        "derivation_not_measurement": True,
        "holds_only_if": "the annotators' signed importance ratings count as prompt-specific human "
                         "labels under clause ③'s AUTHORSHIP reading — a reading of the clause, "
                         "which this round does not adjudicate",
        "topw_arms_in_released_2prime": topw_admitted,
        "n_removed_if_authorship_reading": len(topw_admitted),
        # ⭐ THE LADDER, computed over committed sets rather than asserted. R1094 left ③'s two
        #    readings unseparated by its own control. This round does not separate them by reading
        #    the clause harder -- it prices what each COSTS.
        "admitted_set_ladder": {
            "released_2prime": len(rel),
            "after_leakage_reading": len(after_leak),
            "after_authorship_reading_as_R1094_applied_it": len(after_auth),
            "after_authorship_extended_by_this_round": len(after_auth_plus),
            "survivors_leakage": after_leak,
            "survivors_authorship_R1094": after_auth,
            "survivors_authorship_extended": after_auth_plus,
        },
        "vacuity": {
            "authorship_extended_admits_nothing": len(after_auth_plus) == 0,
            "why_it_bites": ("R1094's authorship list excludes arms that consume the human TARGET "
                             "or the authored core, but NOT arms that consume the human RATINGS on "
                             "the prompt's own criteria. This round measures that `topw` does "
                             "exactly that. Applied consistently, the authorship reading therefore "
                             "removes the six `topw` arms as well -- and the released ②′ set is "
                             "EMPTY. A definition whose admitted set is empty describes no object, "
                             "so this is a cost the leakage reading does not carry."),
            "not_an_adjudication": ("vacuity is an argument, not a measurement, and it does not "
                                    "make the leakage reading TRUE -- it prices the alternative. "
                                    "R1094's finding stands: the clause's own control cannot "
                                    "separate its readings."),
        },
    }

    payload = {
        "round": "R1101",
        "question": "does `topw` consume prompt-specific human ratings?",
        "prereg_move": sorted(PREREG_MOVE),
        "executed_move": sorted(executed_move),
        "mismatch": mismatch,
        "per_arm": per_arm,
        "unrunnable_configs": unrunnable,
        "intervention_stats": ivst,
        "reversal_control": {"prompts_compared": len(shared), "reverse_hits_argmin": round(rev_frac, 4),
                             "identity_hits_argmin": round(base_frac, 4)},
        "controls": controls,
        "kill": {"gate_open": gate_open, "world_B_killed": world_B_killed, "mismatch": mismatch},
        "grid": {"cells_tested": len(per_arm) * 3, "W_moved": len(executed_move),
                 "W_stable": len(per_arm) - len(executed_move)},
        "consequence_if_world_B": consequence,
        "seeds": list(SEEDS),
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
    }
    if not gate_open:
        payload["verdict"] = ("⚠ UNVERIFIED — a control is red, so the pre-registered partition is "
                              f"not binding. Controls: {json.dumps(controls)}")
    elif mismatch:
        payload["verdict"] = (f"⛔ WORLD B IS KILLED. The executed partition differs from the "
                              f"pre-registration on {len(mismatch)} cell(s): {mismatch}. The "
                              f"intervention does not isolate the human ratings, and NO authorship "
                              f"statement follows from it.")
    else:
        payload["verdict"] = (
            f"⭐ WORLD B HOLDS, EXACTLY. {len(executed_move)} of {len(per_arm)} configurations move "
            f"when the human importance ratings are deranged WITHIN the prompt — "
            f"{sorted(executed_move)} — and the other {len(per_arm) - len(executed_move)}, including "
            f"the three arms R1100 measured as target-consuming, are byte-stable. **`topw` RANKS BY "
            f"PROMPT-SPECIFIC HUMAN RATINGS.** Derivation, conditional on the authorship reading of "
            f"③ counting those ratings as human labels: it would remove "
            f"{consequence['n_removed_if_authorship_reading']} arms "
            f"({topw_admitted}) from the released ②′ set — taking it from "
            f"{consequence['admitted_set_ladder']['released_2prime']} to "
            f"{consequence['admitted_set_ladder']['after_authorship_extended_by_this_round']}, "
            f"against {consequence['admitted_set_ladder']['after_leakage_reading']} under the "
            f"leakage reading."
            + (" ⛔ SO THE AUTHORSHIP READING, APPLIED CONSISTENTLY, ADMITS NOTHING — a definition "
               "whose admitted set is empty describes no object. That is a cost the leakage "
               "reading does not carry, and it is an argument, not an adjudication: R1094's "
               "finding that the clause's own control cannot separate its readings still stands."
               if consequence["vacuity"]["authorship_extended_admits_nothing"] else ""))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, sort_keys=True))
    print()
    for t, v in per_arm.items():
        print(f"  {t:16s} W={'MOVES ' if v['W_moved'] else 'stable'} "
              f"rate={v['W_rate_per_seed'][0]:.3f} rev={v['reverse_rate']:.3f} "
              f"sham={'clean' if v['sham_clean'] else 'DIRTY'} prereg_move={v['prereg_move']}")
    print(f"\n  reversal control: topw_k1 picks the previously LOWEST-rated criterion on "
          f"{rev_frac:.3f} of {len(shared)} prompts (identity run: {base_frac:.3f})")
    print()
    for k, v in controls.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print()
    print(" ", payload["verdict"])
    shutil.rmtree(base, ignore_errors=True)
    return 0 if gate_open else 2


if __name__ == "__main__":
    sys.exit(main())
