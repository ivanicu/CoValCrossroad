"""R247 -- R246 killed the modal rival. So calibrate what survived, and ask whether it is a CORE.

WHERE R246 LEFT IT
    The modal-class rival is dead: the target distribution has 24 classes over 200 prompts, modal
    share 0.10, entropy 4.485 bits against 4.585 for uniform-over-24. Nearly flat. A response-blind
    constant predictor scores 0.0633 while the fitted core scores 0.3500.
    The REPAIRED negative control (permute targets, refit, evaluate on true targets) came back at
    0.1667-0.2533, BELOW the random-k floor at every k -- greedy selection with no signal transfers
    WORSE than no selection. That is a control behaving correctly, and it clears overfitting.

WHAT IS STILL NOT ESTABLISHED, AND IT IS THE PART THAT MATTERS FOR THE FORMULATION
  (1) CALIBRATION. The fitted core sits at the random floor's MAX-OF-20-DRAWS. R240 compared to
      that max and crossed at 1 of 6 sizes by 1/300. R246 compared to the floor's MEAN and crossed
      at 6 of 6. Neither is a test: max-of-20 is an extreme order statistic and the mean ignores
      the spread. The floor's DISTRIBUTION is the null, and the statistic is where the fitted value
      falls in it, corrected over the whole k grid.
  (2) IS IT A *CORE*? A core is a SELECTION. If using the entire 200-criterion vocabulary scores
      what the fitted 32 scores, then nothing was selected and the finding is "generic criteria
      carry a transferable signal" -- true, useful, and NOT a core. R240 never ran an all-in arm.
      This is the sham realstat asks for: the same operation minus the ingredient under study,
      where the ingredient is SELECTION.
  (3) IS IT ONE SCALAR? If a single universal quality axis drives it, a response-LENGTH predictor
      should recover much of the same class agreement while containing no norm content at all.

ESTIMAND        (a) the empirical percentile of the fitted global core's held-out class agreement
                    within the random-k floor's own draw distribution, per k, BH-corrected over the
                    whole k grid;
                (b) the held-out agreement of two shams that remove the ingredient under study:
                    SHAM-ALL   every one of the 200 vocabulary criteria, no selection at all
                    SHAM-LEN   rank by response character length, no criterion content at all
IDENTIFICATION  exact; every arm is a deterministic function of the persisted R240 tensor plus the
                released response text. No new judgements.
SCOPE           population: the same 200 prompts, split 100/100, 10 seeds (R240 and R246 used 3).
                instrument: R240's sat_global.npz, byte-identical. baseline: 50 random-k draws per
                seed = 500 draws, so the empirical p resolves to 1/501. regime: k in {1..32}, m=4.
WORLDS          W1 a global core exists and SELECTION is what carries it
                     -> fitted beats the floor distribution AND beats SHAM-ALL
                W2 generic criteria transfer, but selection adds nothing
                     -> fitted ~= SHAM-ALL; "core" is the wrong word and the finding is about the
                        vocabulary, not about a compiler
                W3 one scalar quality axis explains it
                     -> SHAM-LEN recovers most of the agreement, with zero norm content
KILL            pre-registered, all three, written before the run:
                  - if the BH-corrected empirical p exceeds 0.05 at every k, the transfer is not
                    distinguishable from selecting k criteria at random and claim 7 stays OPEN.
                  - if fitted - SHAM-ALL is inside the fitted arm's seed spread at every k, the
                    object is NOT a core: report it as a vocabulary effect and rename the claim.
                  - if SHAM-LEN alone lands within the fitted arm's seed spread, the class
                    agreement is a length artifact and every arm above is uninterpretable.
POSITIVE CTRL   at 3 seeds this must still reproduce R240/R246's held-out numbers exactly. Pinned
                to published values computed elsewhere, so it can fail.
NEGATIVE CTRL   R246's repaired arm (permuted-target refit) carried forward at 10 seeds; it must
                stay at or below the floor. If it rises above with more seeds, R246's clearance of
                overfitting was underpowered and this round says so.
PLACEBO         SHAM-ALL evaluated against its OWN induced classes = 1.0000 exactly.
NOISE FLOOR     10 seeds; ptp reported beside every arm.
MULTIPLICITY    6 k x 5 arms x 10 seeds = 300 cells; BH over the 6 k tests; non-survivors printed.
SPECIFICATION   the axis swept is WHAT THE BASELINE HOLDS FIXED: selection (B1) / signal (B3) /
                nothing (SHAM-ALL) / content (SHAM-LEN).
ARTIFACT        all 500 floor draws per k persisted, so a later round can re-test without refitting.
IMPOSSIBLE      whether the transferable signal is a NORM rather than a stylistic regularity of the
                judge. That needs a second judge family scoring the same global vocabulary; the
                r04/R164 caches cover the per-prompt rubric, not this 200-criterion vocabulary.
"""
from __future__ import annotations
import collections, json, pathlib, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
TENSOR = ROOT / ("E05_the_space_of_compilers/A10_is_a_global_core_real/R240_fit_a_global_core"
                 "/results/sat_global.npz")
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
KS = [1, 2, 4, 8, 16, 32]
SEEDS = list(range(10))
DRAWS = 50
R240_HELDOUT = {1: 0.2867, 2: 0.2967, 4: 0.3067, 8: 0.3467, 16: 0.3567, 32: 0.3500}


def cls_arr(Y):
    return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)


def bh(ps, q=0.05):
    o = np.argsort(ps); s = np.array(ps)[o]; C = len(ps)
    keep = np.zeros(C, bool)
    for i in range(C - 1, -1, -1):
        if s[i] <= q * (i + 1) / C:
            keep[o[:i + 1]] = True
            break
    return keep


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(TENSOR, allow_pickle=True)
    V = [str(x) for x in d["vocab"]]
    S = collections.defaultdict(lambda: np.zeros((len(V), 4), dtype=np.float32))
    for m, v in zip(d["meta"], d["sat"]):
        p, vi, r_ = str(m).split("|")
        S[p][int(vi), int(r_)] = v

    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A01_is_our_own_compiler_better"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
                               "/R04_rebuild_satisfaction/results/a04_full.npz"))
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    lens = {}
    for line in (DATA / "comparisons.jsonl").open():
        o = json.loads(line)
        lens[o["prompt_id"]] = [float(len(r["messages"][0]["content"])) for r in o["responses"]]

    use, tgt, ln = [], [], []
    for p in sorted(S):
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf.get(p, {}).get((i, x)) is not None for x in L)]
        if len(ok) < 4 or p not in lens or len(lens[p]) != 4:
            continue
        W = np.array([np.mean([float(s2["score"]) for s2 in f[i]["scores"]]) for i in ok])
        SS = np.array([[sf[p][(i, x)] for x in L] for i in ok])
        use.append(p); tgt.append(cls_arr((W[:, None] * SS).sum(0))); ln.append(lens[p])
    A = np.stack([S[p] for p in use]).astype(np.float64)
    T = np.stack(tgt); LN = np.array(ln)
    P_, Vn = A.shape[0], A.shape[1]
    print("prompts %d | vocabulary %d | seeds %d | floor draws %d/seed = %d total"
          % (P_, Vn, len(SEEDS), DRAWS, DRAWS * len(SEEDS)))

    def agree_idx(sub, rows):
        y = A[np.ix_(rows, sub)].sum(1)
        return float((cls_arr(y) == T[rows]).all(-1).mean())

    def greedy(k, rows, target):
        chosen, cur, Ar = [], np.zeros((len(rows), 4)), A[rows]
        for _ in range(k):
            hit = (cls_arr(cur[:, None, :] + Ar) == target[:, None, :]).all(-1).mean(0)
            hit[chosen] = -1.0
            bi = int(np.argmax(hit)); chosen.append(bi); cur = cur + Ar[:, bi, :]
        return chosen

    g = collections.defaultdict(lambda: collections.defaultdict(list))
    floors = collections.defaultdict(list)
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        idx = rng.permutation(P_)
        fit, ev = idx[:P_ // 2], idx[P_ // 2:]
        Tp = T[fit][rng.permutation(len(fit))]
        sham_all = agree_idx(list(range(Vn)), ev)
        sham_len = float((cls_arr(LN[ev]) == T[ev]).all(-1).mean())
        for k in KS:
            ch = greedy(k, fit, T[fit])
            g[k]["fit"].append(agree_idx(ch, fit))
            g[k]["held"].append(agree_idx(ch, ev))
            fl = [agree_idx(list(rng.choice(Vn, size=k, replace=False)), ev) for _ in range(DRAWS)]
            floors[k].extend(fl)
            g[k]["B1"].append(float(np.mean(fl)))
            g[k]["B3perm"].append(agree_idx(greedy(k, fit, Tp), ev))
            g[k]["SHAM_ALL"].append(sham_all)
            g[k]["SHAM_LEN"].append(sham_len)

    print("\n=== POSITIVE CONTROL: first 3 seeds must reproduce R240/R246 exactly ===")
    ok_all = True
    for k in KS:
        h3 = float(np.mean(g[k]["held"][:3]))
        good = abs(h3 - R240_HELDOUT[k]) < 5e-4
        ok_all &= good
        print(" k=%-3d seeds 0-2 held-out %.4f  published %.4f  %s"
              % (k, h3, R240_HELDOUT[k], "OK" if good else "MISMATCH"))

    print("\n=== the whole grid, 10 seeds, every arm on the same held-out prompts ===")
    print("%-4s %17s %9s %9s %10s %10s %9s" % ("k", "FITTED (ptp)", "B1 rand", "B3 perm",
                                               "SHAM_ALL", "SHAM_LEN", "emp p"))
    rows, praw = [], []
    for k in KS:
        h = np.array(g[k]["held"]); fl = np.array(floors[k])
        p_emp = float((fl.sum() * 0 + (fl >= h.mean()).sum() + 1) / (len(fl) + 1))
        praw.append(p_emp)
        rows.append((k, h.mean(), np.ptp(h), np.mean(g[k]["B1"]), np.mean(g[k]["B3perm"]),
                     np.mean(g[k]["SHAM_ALL"]), np.mean(g[k]["SHAM_LEN"]), p_emp))
        print("%-4d %9.4f (%.4f) %9.4f %9.4f %10.4f %10.4f %9.4f"
              % (k, h.mean(), np.ptp(h), np.mean(g[k]["B1"]), np.mean(g[k]["B3perm"]),
                 np.mean(g[k]["SHAM_ALL"]), np.mean(g[k]["SHAM_LEN"]), p_emp))
    keep = bh(praw)
    print("\n=== multiplicity: BH q=0.05 over all %d k tests ===" % len(KS))
    print(" survivors : %s" % ([k for k, s in zip(KS, keep) if s] or "NONE"))
    print(" killed    : %s" % ([k for k, s in zip(KS, keep) if not s] or "none"))
    print(" (empirical p is floored at 1/%d = %.4f by the draw count)"
          % (len(floors[KS[0]]) + 1, 1 / (len(floors[KS[0]]) + 1)))

    print("\n=== the sham that decides whether this is a CORE ===")
    sa = np.mean(g[KS[-1]]["SHAM_ALL"])
    for k in KS:
        h = np.array(g[k]["held"]); dd = h.mean() - np.mean(g[k]["SHAM_ALL"])
        print(" k=%-3d fitted %.4f  all-200 %.4f  delta %+.4f  seed ptp %.4f  -> %s"
              % (k, h.mean(), np.mean(g[k]["SHAM_ALL"]), dd, np.ptp(h),
                 "SELECTION ADDS" if abs(dd) > np.ptp(h) and dd > 0 else "inside spread"))

    print("\n=== controls ===")
    negok = all(np.mean(g[k]["B3perm"]) <= np.mean(g[k]["B1"]) + 1e-9 for k in KS)
    print(" NEGATIVE  permuted-target refit stays at or below the random floor : %s"
          % ("OK" if negok else "ROSE ABOVE -- R246's clearance of overfitting was underpowered"))
    ch = greedy(4, np.arange(P_), T)
    sc = cls_arr(A[:, list(range(Vn))].sum(1))
    print(" PLACEBO   all-200 core against its own induced classes : %.4f  %s"
          % (float((sc == sc).all(-1).mean()), "OK"))
    print(" SHAM_LEN  response length alone, no criterion content   : %.4f" % np.mean(g[1]["SHAM_LEN"]))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    surv_k = [k for k, s in zip(KS, keep) if s]
    sel_k = [k for k in KS if (np.array(g[k]["held"]).mean() - np.mean(g[k]["SHAM_ALL"]))
             > np.ptp(g[k]["held"])]
    lenmax = max(np.mean(g[k]["SHAM_LEN"]) for k in KS)
    if not ok_all:
        v = "UNVERIFIED -- does not reproduce the published held-out numbers; nothing comparable."
    elif lenmax >= min(np.array(g[k]["held"]).mean() - np.ptp(g[k]["held"]) for k in KS):
        v = ("UNVERIFIED -- response length alone reaches %.4f, inside the fitted arm's own spread. "
             "The class agreement is a length artifact and no arm above is interpretable." % lenmax)
    elif not surv_k:
        v = ("REFUTED -- at no k does the fitted core's held-out agreement clear its own random-k "
             "floor distribution after BH over the grid. Claim 7 stays OPEN.")
    elif not sel_k:
        v = ("SURVIVES BUT IT IS NOT A CORE -- the fitted core clears the floor at k=%s, and at NO "
             "k does it beat using the ENTIRE 200-criterion vocabulary by more than its seed "
             "spread. Selection is not the ingredient. The transferable object is the generic "
             "VOCABULARY, and calling it a core imports a compression claim the measurement does "
             "not support." % surv_k)
    else:
        v = ("A GLOBAL CORE, AND SELECTION IS THE INGREDIENT -- clears the floor distribution at "
             "k=%s after BH, and beats the unselected all-200 arm by more than its seed spread at "
             "k=%s." % (surv_k, sel_k))
    print("\n  " + v)
    json.dump({"prompts": P_, "seeds": SEEDS, "draws_total": len(floors[KS[0]]),
               "reproduces_published": bool(ok_all),
               "rows": [{"k": r[0], "fitted": r[1], "ptp": r[2], "B1": r[3], "B3perm": r[4],
                         "sham_all": r[5], "sham_len": r[6], "p_emp": r[7]} for r in rows],
               "bh_survivors": surv_k, "selection_adds_at": sel_k,
               "floor_draws": {str(k): list(map(float, floors[k])) for k in KS},
               "verdict": v}, open(OUT / "selection_test.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
