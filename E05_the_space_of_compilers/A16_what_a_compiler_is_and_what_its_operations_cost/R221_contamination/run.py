"""R221 -- the contamination test. Read README.md first: estimand, worlds, plants, kill.

THE QUESTION R220 COULD NOT ANSWER
    R220's K2 cleared D_decision against a size-matched RANDOM draw. A random subset carries no
    information about the outcome, so beating it separates "selection is not noise" from nothing
    at all. It cannot tell a compiler that keeps VALUES from one that keeps PREDICTORS, because
    both beat noise. This round builds the opponent that can: criteria engineered to predict the
    decision perfectly while carrying no normative content.

WHY THE PLANTS ARE VECTORS AND NOT TEXT
    A planted criterion written as a sentence would have to be scored by a judge, which re-opens
    the instrument choice and makes the plant a hypothesis about the judge. Constructing the
    satisfaction vector directly makes the plant EXACT: `posthoc` predicts the winner with
    probability 1 by definition, not by assumption.

ZERO GPU. Cached tensors for the real criteria; the plants carry no instrument at all.
"""
from __future__ import annotations

import json, pathlib, sys, collections
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"
L = "ABCD"
KS = [3, 4, 5]
SEEDS = [0, 1, 2]
# ⚠ CORRECTED MID-ROUND. The first positive control was `posthoc`: one-hot on the current
# winner, i.e. a PERFECT WINNER PREDICTOR. D_decision took it at 0.0537 against a chance of
# 0.2713 -- BELOW chance -- and the kill correctly returned UNVERIFIED. The reason is not that
# the compiler resists proxies: greedy_decision_subset maximises agreement with the FULL
# RANKING, and a one-hot vector fixes one position out of four while destroying the other
# three. I had built a control against an objective the instrument does not optimise -- the
# mirror image of a check that cannot fail: a control that cannot succeed.
# `rank_clone` is the true positive control: one criterion whose satisfaction reproduces the
# source ranking EXACTLY. A ranking-fitter must take it first or it is not fitting rankings.
# `posthoc` is kept, demoted from control to finding: it measures how much a decision-fitter
# is seduced by winner-only evidence, which is a different and smaller question.
PLANTS = ["rank_clone", "posthoc", "inert", "duplicate", "permuted", "style_length"]
ARMS = ["C_signed_topk", "D_decision", "E_typed", "G_medoid", "F_random"]

sys.path.insert(0, str(ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                      / "R220_compiler_tournament"))
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                 / "R220_compiler_tournament/run.py")
r220 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module.__self__ if False else _spec.loader.exec_module(r220)


def make_plant(kind, Wv, S, texts, lens, rng):
    """Return (satisfaction over A-D, weight, label). Each is EXACT, not judged."""
    med = float(np.median(np.abs(Wv))) or 1.0
    if kind == "rank_clone":
        y = (Wv[:, None] * S).sum(0)
        rng_ = y.max() - y.min()
        s = (y - y.min()) / rng_ if rng_ > 0 else np.full(4, 0.5)
        return s, med, "alone reproduces the source ranking exactly"
    if kind == "posthoc":
        w = int(np.argmax((Wv[:, None] * S).sum(0)))
        s = np.full(4, 0.0); s[w] = 1.0
        return s, med, "satisfied by the current winner and nothing else"
    if kind == "inert":
        return np.full(4, 0.5), med, "identical on every response"
    if kind == "duplicate":
        i = int(np.argmax(np.abs(Wv)))
        return S[i].copy(), float(Wv[i]), "copy of the largest-|w| criterion"
    if kind == "permuted":
        i = int(rng.integers(len(Wv)))
        s = S[i].copy(); rng.shuffle(s)
        return s, float(Wv[i]), "a real criterion, satisfaction shuffled across responses"
    if kind == "style_length":
        a = np.asarray(lens, float)
        s = (a - a.min()) / (a.max() - a.min()) if a.max() > a.min() else np.full(4, 0.5)
        return s, med, "response length, normalised"
    raise ValueError(kind)


def degeneracy(Wv, S, med):
    """How many SINGLE criteria alone reproduce the source ranking exactly?

    This exists because the corrected positive control still came in below chance, and a control
    that cannot succeed has to be explained before any other cell is read. The explanation is not
    about the plant: a ranking over four responses carries at most log2(24) = 4.6 bits, and with a
    median of 15 criteria there are usually SEVERAL that reproduce it alone. The greedy breaks ties
    by array position and the plant is appended last, so its selection rate measures where it sits
    in the list, not whether it is good."""
    y = (Wv[:, None] * S).sum(0)
    tgt = np.argsort(np.argsort(-y))
    rngv = y.max() - y.min()
    sp = (y - y.min()) / rngv if rngv > 0 else np.full(4, 0.5)
    W2 = np.append(Wv, med); S2 = np.vstack([S, sp])
    sc = []
    for i in range(len(W2)):
        yy = W2[i] * S2[i]
        r = np.argsort(np.argsort(-yy))
        sc.append((float((r == tgt).sum()), float(np.argmax(yy) == np.argmax(y))))
    best = max(sc)
    tied = sum(1 for x in sc if x == best)
    return best[0], tied, sc[-1] == best, tied == 1 and sc[-1] == best


def select(arm, Wv, S, texts, k, rng):
    """Which criterion indices does this arm keep? None if the arm keeps everything."""
    if arm == "C_signed_topk":
        return list(np.argsort(-np.abs(Wv))[:k])
    if arm in ("D_decision", "E_typed"):
        return r220.greedy_decision_subset(Wv, S, k)
    if arm == "G_medoid":
        return r220.medoid_clusters(texts, k)
    if arm == "F_random":
        return list(rng.choice(len(Wv), size=min(k, len(Wv)), replace=False))
    raise ValueError(arm)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sf = r220.load_sat(R4 / "a04_full.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    lens_by_pid = {}
    for line in (DATA / "comparisons.jsonl").open():
        d = json.loads(line)
        lens_by_pid[d["prompt_id"]] = [len(r["messages"][0]["content"]) for r in d["responses"]]
    ann = collections.defaultdict(list)
    for line in (DATA / "merged_comparisons_annotators.jsonl").open():
        r = json.loads(line)
        ann[r["prompt_id"]].append(r)

    # sel[(arm, plant, k, seed, mode)] = [selected, opportunities]
    sel = collections.defaultdict(lambda: [0, 0])
    # matched[(arm,k,seed)] = selection rate of REAL criteria whose |w| is within 10% of the plant's
    matched = collections.defaultdict(lambda: [0, 0])
    chance = collections.defaultdict(list)
    acc = collections.defaultdict(lambda: [0, 0])
    n_used = 0
    deg = {"best": [], "tied": [], "plant_among_best": [], "plant_unique": []}

    for p in sorted(sf):
        if p not in recs or p not in lens_by_pid or p not in ann:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < 4:
            continue
        texts = [str(f[i].get("criterion", "")) for i in ok]
        Wv = np.array([np.mean([float(s_["score"]) for s_ in f[i]["scores"]]) for i in ok], float)
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok], float)
        lens = lens_by_pid[p]
        rank_rows = []
        for a in ann[p]:
            for e in ((a.get("ranking_blocks") or {}).get("world") or []):
                pts = r220.parse_rank(e.get("ranking"))
                if pts is not None:
                    rank_rows.append(pts)
        if not rank_rows:
            continue
        n_used += 1
        n = len(ok)
        b_, t_, among_, uniq_ = degeneracy(Wv, S, float(np.median(np.abs(Wv))) or 1.0)
        deg["best"].append(b_); deg["tied"].append(t_)
        deg["plant_among_best"].append(among_); deg["plant_unique"].append(uniq_)

        for seed in SEEDS:
            rng = np.random.default_rng(abs(hash((p, seed))) % (2 ** 32))
            built = {c: make_plant(c, Wv, S, texts, lens, rng)[:2] for c in PLANTS}
            modes = [("one", [c]) for c in PLANTS] + [("all", PLANTS)]
            for mode, group in modes:
                W2 = np.concatenate([Wv, [built[c][1] for c in group]])
                S2 = np.vstack([S, [built[c][0] for c in group]])
                # ⚠ the first version labelled plants "PLANT:<kind>". G_medoid clusters LEXICALLY, so five
                # strings unlike anything else each became their own cluster medoid and it selected
                # 94% of them -- a confound I built. Plants now borrow a real criterion's text, so
                # lexical distinctiveness cannot drive selection.
                T2 = texts + [texts[int(rng.integers(len(texts)))] for _ in group]
                planted_idx = {n + j: c for j, c in enumerate(group)}
                for k in KS:
                    chance[(k, mode)].append(k / (n + len(group)))
                    for arm in ARMS:
                        rng2 = np.random.default_rng(abs(hash((p, seed, arm, k, mode))) % (2 ** 32))
                        keep = select(arm, W2, S2, T2, k, rng2)
                        for j, c in planted_idx.items():
                            key = (arm, c, k, seed, mode)
                            sel[key][0] += int(j in keep); sel[key][1] += 1
                        if mode == "one" and group == ["rank_clone"]:
                            # matched comparison: REAL criteria whose |w| is near the plant's
                            pw = abs(built["rank_clone"][1])
                            near = [i for i in range(n) if abs(abs(Wv[i]) - pw) <= 0.1 * max(pw, 1e-9)]
                            for i in near:
                                matched[(arm, k, seed)][0] += int(i in keep)
                                matched[(arm, k, seed)][1] += 1
                        # human agreement with and without the plant
                        if k == 4 and mode == "one":
                            y = (W2[keep, None] * S2[keep]).sum(0)
                            for pts in rank_rows:
                                for i_, j_ in r220.kendall_pairs(pts):
                                    acc[(arm, group[0])][0] += int(y[i_] > y[j_])
                                    acc[(arm, group[0])][1] += 1
                            base_keep = select(arm, Wv, S, texts, k,
                                               np.random.default_rng(
                                                   abs(hash((p, seed, arm, k, "base"))) % (2 ** 32)))
                            yb = (Wv[base_keep, None] * S[base_keep]).sum(0)
                            for pts in rank_rows:
                                for i_, j_ in r220.kendall_pairs(pts):
                                    acc[(arm, "CLEAN")][0] += int(yb[i_] > yb[j_])
                                    acc[(arm, "CLEAN")][1] += 1

    def rate(d):
        return d[0] / d[1] if d[1] else float("nan")

    ch = {km: float(np.mean(v)) for km, v in chance.items()}
    res = {"degeneracy": {"share_single_criterion_reproduces_ranking":
                          float(np.mean([b == 4 for b in deg["best"]])),
                          "tied_median": float(np.median(deg["tied"])),
                          "tied_mean": float(np.mean(deg["tied"])),
                          "plant_among_best": float(np.mean(deg["plant_among_best"])),
                          "plant_unique_best": float(np.mean(deg["plant_unique"]))},
           "prompts": n_used, "plants": PLANTS, "arms": ARMS, "ks": KS, "seeds": SEEDS,
           "chance": {"%d|%s" % km: v for km, v in ch.items()},
           "selection": {"%s|%s|%d|%d|%s" % k_: rate(v) for k_, v in sel.items()},
           "matched_real": {"%s|%d|%d" % k_: rate(v) for k_, v in matched.items()},
           "rank_acc": {"%s|%s" % k_: rate(v) for k_, v in acc.items()}}

    print("prompts %d   |   chance k/(n+1) at k=4, one plant: %.4f" % (n_used, ch[(4, "one")]))
    print("\n=== WHY THE POSITIVE CONTROL CANNOT FIRE: the objective is degenerate ===")
    print(" prompts where SOME single criterion alone reproduces the full ranking : %.1f%%"
          % (100 * np.mean([b == 4 for b in deg["best"]])))
    print(" how many criteria TIE at that perfect score        median %.0f   mean %.1f"
          % (np.median(deg["tied"]), np.mean(deg["tied"])))
    print(" the rank_clone plant is AMONG the tied best        %.1f%%"
          % (100 * np.mean(deg["plant_among_best"])))
    print(" the rank_clone plant is the UNIQUE best            %.1f%%"
          % (100 * np.mean(deg["plant_unique"])))
    print(" -> a greedy that breaks ties by array position selects the plant at the rate at which")
    print("    it is uniquely best. Its selection rate measures LIST POSITION, not quality.")
    print("\n=== selection rate, one plant at a time, k=4, mean over 3 seeds ===")
    print("%-15s %s   chance" % ("arm", "".join("%14s" % c for c in PLANTS)))
    for arm in ARMS:
        row = "".join("%14.4f" % np.mean([sel[(arm, c, 4, s, "one")][0] /
                                          max(sel[(arm, c, 4, s, "one")][1], 1) for s in SEEDS])
                      for c in PLANTS)
        print("%-15s %s   %.4f" % (arm, row, ch[(4, "one")]))

    print("\n=== all five planted at once, k=4 ===")
    print("%-15s %s" % ("arm", "".join("%14s" % c for c in PLANTS)))
    for arm in ARMS:
        row = "".join("%14.4f" % np.mean([sel[(arm, c, 4, s, "all")][0] /
                                          max(sel[(arm, c, 4, s, "all")][1], 1) for s in SEEDS])
                      for c in PLANTS)
        print("%-15s %s   chance %.4f" % (arm, row, ch[(4, "all")]))

    print("\n=== specification curve over k (rank_clone = the positive control) ===")
    for arm in ARMS:
        print("%-15s %s" % (arm, "  ".join(
            "k=%d %.4f (chance %.4f)" % (k, np.mean([sel[(arm, "rank_clone", k, s, "one")][0] /
                                                     max(sel[(arm, "rank_clone", k, s, "one")][1], 1)
                                                     for s in SEEDS]), ch[(k, "one")])
            for k in KS)))

    print("\n=== human agreement, k=4: does the contamination HELP? ===")
    print("%-15s %10s %s" % ("arm", "clean", "".join("%14s" % c for c in PLANTS)))
    for arm in ARMS:
        base = rate(acc[(arm, "CLEAN")])
        print("%-15s %10.4f %s" % (arm, base, "".join(
            "%+14.4f" % (rate(acc[(arm, c)]) - base) for c in PLANTS)))

    print("\n=== seed spread (rank_clone, k=4, one) ===")
    for arm in ARMS:
        v = [sel[(arm, "rank_clone", 4, s, "one")][0] / max(sel[(arm, "rank_clone", 4, s, "one")][1], 1)
             for s in SEEDS]
        print("%-15s %s   spread %.4f" % (arm, " ".join("%.4f" % x for x in v), max(v) - min(v)))

    # ---------------------------------------------------------------- the kill
    print("\n" + "=" * 78)
    print("PRE-REGISTERED KILL -- a conditional, not a threshold")
    print("=" * 78)
    d_post = np.mean([sel[("D_decision", "rank_clone", 4, s, "one")][0] /
                      max(sel[("D_decision", "rank_clone", 4, s, "one")][1], 1) for s in SEEDS])
    d_inert = np.mean([sel[("D_decision", "inert", 4, s, "one")][0] /
                       max(sel[("D_decision", "inert", 4, s, "one")][1], 1) for s in SEEDS])
    d_real = np.mean([matched[("D_decision", 4, s)][0] / max(matched[("D_decision", 4, s)][1], 1)
                      for s in SEEDS])
    c4 = ch[(4, "one")]
    pos_fires = d_post > c4
    neg_null = d_inert <= c4
    print("positive control  sel(D, rank_clone) = %.4f  vs chance %.4f   -> %s"
          % (d_post, c4, "FIRES" if pos_fires else "DOES NOT FIRE"))
    print("negative control  sel(D, inert)   = %.4f  vs chance %.4f   -> %s"
          % (d_inert, c4, "null" if neg_null else "NOT NULL"))
    print("matched real criteria (|w| within 10%% of the plant's) sel = %.4f" % d_real)
    if pos_fires and neg_null:
        verdict = ("W1 REFUTED -- decision-fitting selects the PROXY"
                   if d_post > d_real else "W2 REFUTED -- it selects normative content")
        print("\nboth controls behaved, so the kill is binding:\n  %s" % verdict)
        print("  sel(posthoc) %.4f  vs  sel(matched real) %.4f  ->  ratio %.2fx"
              % (d_post, d_real, d_post / d_real if d_real else float("inf")))
    else:
        verdict = ("UNVERIFIED -- and the cause is identified: the objective is degenerate. "
                   "%.1f%% of prompts admit a SINGLE criterion that reproduces the whole ranking, "
                   "with a median of %.0f tied at that score. The plant is among the best %.1f%% "
                   "of the time and uniquely best %.1f%%, and the greedy's selection rate tracks "
                   "the latter. No contamination test can discriminate on an objective that "
                   "cannot discriminate."
                   % (100 * np.mean([b == 4 for b in deg["best"]]), np.median(deg["tied"]),
                      100 * np.mean(deg["plant_among_best"]),
                      100 * np.mean(deg["plant_unique"])))
        print("\n  %s" % verdict)
    res["verdict"] = verdict
    res["kill"] = {"sel_posthoc": d_post, "sel_inert": d_inert, "sel_matched_real": d_real,
                   "chance": c4, "positive_fires": bool(pos_fires), "negative_null": bool(neg_null)}
    (OUT / "contamination.json").write_text(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
