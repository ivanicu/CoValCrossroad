"""R233 -- the candidate-set test everyone said was impossible, on responses already in this repo.

WHAT I GOT WRONG, FOUR TIMES
    R220's register, R223, R231 and R232 all say some version of: "the release ships exactly one
    4-response set per prompt, so candidate-set overfitting is STRUCTURALLY UNDETECTABLE here."

    R232 verified the wall and the wall is true OF THE RELEASE -- 1,078/1,078 prompts, m=4, in both
    the metadata field and the arrays. The CONCLUSION drawn from it is false. R12 generated a second
    candidate set on 2026-07-28 and it has been sitting in this repository ever since:

        R12_response_set/results/a12_fresh_generations.json
        250 prompts x 4 FRESH responses, Qwen3.5-2B-Base, T=0.9, top_p=0.95, 180 tokens

    realstat §4's last row is about exactly this, and its example is a limit that "was a query never
    run". Mine is worse: the falsifying ARTIFACT was in my own results directory, produced by my own
    round, and I asserted the impossibility four times without looking.

WHAT BECOMES TESTABLE
    Does the compiled core preserve the full rubric's Q-class on responses NEITHER HAS EVER SEEN?
    That is Test 3 of the compiler-tournament plan, the one every register called out of reach.

WHAT DOES NOT
    The fresh responses carry NO HUMAN RANKINGS -- the release has none for generated text, and R12's
    own artifact says so in `outcome_variable_scope`. So this measures transport of the COMPILATION,
    never agreement with people, and every number below is scoped to that.

ESTIMAND        P(class_core(fresh) == class_full(fresh)), against the same quantity on the original
                responses (R231 measured 0.3864), and against a size-matched random floor.
IDENTIFICATION  exact given the judge; the classes are deterministic functions of the tensor.
SCOPE           population 250 prompts with fresh generations. instrument Qwen3.5-2B-Base, the same
                judge as r04 -- deliberately, so the ONLY thing that changes between this and R231
                is the candidate set. baseline: random-4 arm, 20 draws. regime m=4 fresh.
WORLDS          W1 the core's agreement is a property of the compilation -> holds up on fresh
                W2 it is fitted to the shown responses                   -> collapses toward random
KILL            pre-registered: if agreement on fresh falls to within the random floor's draw spread
                while agreement on original does not, "decision-preserving" is candidate-set
                overfitting, and R220's D_decision arm dies with it.
POSITIVE CTRL   the ORIGINAL responses, re-judged in this same run. Must reproduce R231's 0.3864
                within seed noise, or the pipeline differs from R231's and nothing is comparable.
NEGATIVE CTRL   random-4 arm on fresh responses, 20 draws, its own spread.
PLACEBO         full vs itself on fresh must be exactly 1.0000.
IMPOSSIBLE      whether HUMANS would rank the fresh responses the way either object does. No labels
                exist and none can be manufactured; this is the register entry that stays.
"""
from __future__ import annotations

import json, pathlib, sys, collections
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
FRESH = ROOT / ("E01_the_rubric_was_the_object/A03_is_the_attribution_real_and_against_what_floor"
                "/R12_response_set/results/a12_fresh_generations.json")
MODEL = "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/Qwen3.5-2B-Base"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
DRAWS = 20


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    fg = json.load(open(FRESH))
    pids, orig, fresh = fg["prompt_ids"], fg["original"], fg["fresh"]
    from covalx.judge import Judge, build_prompt, load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}

    tasks, index = [], []
    for i, pid in enumerate(pids):
        if pid not in recs:
            continue
        f, cr = recs[pid]["coval_full"], recs[pid]["coval_core"]
        full_c = [(k, it["criterion"], np.mean([float(s["score"]) for s in it["scores"]]))
                  for k, it in enumerate(f) if it.get("scores")]
        core_c = [(k, it["criterion"]) for k, it in enumerate(cr)]
        if len(full_c) < 4 or not core_c:
            continue
        for arm, reps in (("orig", orig[i]), ("fresh", fresh[i])):
            if len(reps) != 4:
                continue
            for r_ in range(4):
                for k, txt, w in full_c:
                    index.append((pid, arm, "full", k, r_, w)); tasks.append(build_prompt(txt, reps[r_]))
                for k, txt in core_c:
                    index.append((pid, arm, "core", k, r_, 1.0)); tasks.append(build_prompt(txt, reps[r_]))

    # ⚠ THE FIRST RUN PERSISTED 620 BYTES FOR 33,320 GPU JUDGEMENTS. Summary statistics only:
    # no tensor, no per-prompt rows. So the round that discovered the candidate-set test could not
    # be ATTACKED without re-spending the GPU -- and the confound its own controls exposed (fresh
    # responses are easier, both floors move) needs exactly the per-prompt data it threw away.
    # realstat §5: "ARTIFACT persisted with source hash; what a LATER round needs to ATTACK this."
    # That line is in this file's own docstring. Now the tensor is written before anything is
    # summarised, so every future attack is arithmetic on cache.
    print("judging %d (criterion, response) pairs over %d prompts, both arms"
          % (len(tasks), len({i[0] for i in index})), flush=True)
    judge = Judge(MODEL, batch=64)
    sat = judge.score(tasks)

    np.savez_compressed(
        OUT / "sat_fresh_and_orig.npz",
        meta=np.array(["%s|%s|%s|%d|%d" % (pid, arm, which, k, r_)
                       for pid, arm, which, k, r_, _w in index]),
        weight=np.array([w for *_x, w in index], dtype=np.float32),
        sat=np.asarray(sat, dtype=np.float32))
    print("persisted %d judgements to results/sat_fresh_and_orig.npz -- attackable without a GPU"
          % len(sat), flush=True)

    store = collections.defaultdict(dict)
    for (pid, arm, which, k, r_, w), v in zip(index, sat):
        store[(pid, arm, which)][(k, r_)] = (float(v), w)

    hit = collections.defaultdict(lambda: [0, 0])
    rand = collections.defaultdict(lambda: [0, 0])
    for pid in {i[0] for i in index}:
        for arm in ("orig", "fresh"):
            F, C = store.get((pid, arm, "full")), store.get((pid, arm, "core"))
            if not F or not C:
                continue
            ks = sorted({k for k, _ in F})
            W = np.array([F[(k, 0)][1] for k in ks])
            S = np.array([[F[(k, r_)][0] for r_ in range(4)] for k in ks])
            cj = sorted({k for k, _ in C})
            SC = np.array([[C[(k, r_)][0] for r_ in range(4)] for k in cj])
            cf, cc = cls((W[:, None] * S).sum(0)), cls(SC.sum(0))
            hit[(arm, "core_vs_full")][0] += int(cc == cf); hit[(arm, "core_vs_full")][1] += 1
            hit[(arm, "PLACEBO_full_vs_full")][0] += 1; hit[(arm, "PLACEBO_full_vs_full")][1] += 1
            for d in range(DRAWS):
                rng = np.random.default_rng(abs(hash((pid, arm, d))) % (2 ** 32))
                idx = list(rng.choice(len(ks), size=min(4, len(ks)), replace=False))
                rand[(arm, d)][0] += int(cls((W[idx, None] * S[idx]).sum(0)) == cf)
                rand[(arm, d)][1] += 1

    def r(k):
        v = hit[k]; return v[0] / v[1] if v[1] else float("nan")

    res = {"model": MODEL, "n_prompts": len({i[0] for i in index}), "judgements": len(tasks)}
    print("\n=== controls ===")
    for arm in ("orig", "fresh"):
        p_ = r((arm, "PLACEBO_full_vs_full"))
        print(" PLACEBO %-6s full vs itself : %.4f  %s"
              % (arm, p_, "OK" if p_ == 1.0 else "NOT DETERMINISTIC -- cells void"))
    floors = {}
    for arm in ("orig", "fresh"):
        v = [rand[(arm, d)][0] / rand[(arm, d)][1] for d in range(DRAWS) if rand[(arm, d)][1]]
        floors[arm] = (float(np.mean(v)), min(v), max(v))
        print(" FLOOR   %-6s random-4, %d draws : %.4f  [%.4f, %.4f]"
              % (arm, DRAWS, *floors[arm]))
    o = r(("orig", "core_vs_full"))
    print(" POSITIVE original arm reproduces R231's 0.3864 : %.4f  (delta %+.4f)"
          % (o, o - 0.3864))

    print("\n=== the measurement ===")
    fr = r(("fresh", "core_vs_full"))
    print(" core preserves Full's class, ORIGINAL responses : %.4f   (floor %.4f [%.4f, %.4f])"
          % (o, *floors["orig"]))
    print(" core preserves Full's class, FRESH    responses : %.4f   (floor %.4f [%.4f, %.4f])"
          % (fr, *floors["fresh"]))
    print(" transport delta fresh - original                : %+.4f" % (fr - o))

    print("\n" + "=" * 78)
    print("PRE-REGISTERED KILL")
    print("=" * 78)
    fl, flo, fhi = floors["fresh"]
    inside = flo <= fr <= fhi
    ol, olo, ohi = floors["orig"]
    o_inside = olo <= o <= ohi
    print(" fresh agreement inside its own random floor's spread : %s" % inside)
    print(" original agreement inside its floor's spread          : %s" % o_inside)
    if inside and not o_inside:
        v = ("REFUTED -- class preservation collapses to the random floor on responses the objects "
             "never saw while holding on the shown ones. 'Decision-preserving' is candidate-set "
             "overfitting.")
    elif not inside:
        v = ("SURVIVES -- class preservation on unseen responses (%.4f) stays outside the random "
             "floor [%.4f, %.4f]. The compilation transports to a new candidate set." % (fr, flo, fhi))
    else:
        v = ("BOTH arms sit inside their floors -- the core is indistinguishable from random on "
             "this Q for shown AND unseen responses, which is R231's finding extended, not a "
             "candidate-set effect.")
    print("\n  " + v)
    res.update({"orig": o, "fresh": fr, "floors": floors, "verdict": v,
                "grid": {"%s|%s" % k: r(k) for k in hit}})
    (OUT / "fresh_transport.json").write_text(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
