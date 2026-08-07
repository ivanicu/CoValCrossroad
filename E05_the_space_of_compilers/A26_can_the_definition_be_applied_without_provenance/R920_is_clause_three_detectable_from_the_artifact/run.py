#!/usr/bin/env python3
"""
R920 · clause ③ is currently enforced by READING THE GENERATOR'S SOURCE — is it detectable from the
        artifact instead?

⛔ WHY. The definition's clause ③ says a core *consumes no prompt-specific labels*. Every time this
arc has applied it, it has been applied by reading `corebench/select_core.py:102` — the line where
`oracle_k`, `indep_k` and `greedy_k` open `data/comparisons.jsonl`. **That is a fact about the
producer, not a property of the produced object.** So the definition as written cannot be applied to
a core someone hands you, and nobody has said so.

⭐ AND R919's NEXT WAS FORCED BY ALGEBRA — the second mis-specified NEXT in a row, so it is recorded
here rather than run. It asked whether `topw`'s `0.438 -> 0.778` is carried by apparatus removal or
by judge matching. **R917's own artifact answers it without an experiment**: the apparatus arms
dropped from `RUBRIC_SELECTOR` are `['full']`, and `full` matches no `([a-z]+)_k(\\d+)` pattern, so it
was never in ANY per-rule tally. The decomposition is therefore **100% judge, 0% apparatus, by
construction** — a DERIVATION, labelled as one, and not evidence. (R919's NEXT was unidentified;
R918's was forced; this is a pattern in my closing sentences, which is where §4 says it lives.)

⭐⭐ **THE DETECTOR, AND WHY IT IS NOT CIRCULAR.** For a prompt whose full rubric has `n` criteria,
every size-`k` subset is a candidate core. Their A2 scores form a distribution. An arm that consumed
the labels should sit HIGH in that distribution; a label-blind heuristic should sit wherever its
heuristic lands. So define

    pi(arm) = mean over prompts of [ percentile of the arm's own A2 among sampled size-k subsets ]

⚠ **`pi` needs the human labels — it does NOT need the generator's source.** That is the whole point,
and it is a real weakening of the requirement: from *"you must show me your code"* to *"you must let
me score it on labelled data"*. It is not a removal of the requirement, and this round does not claim
one.

⚠ **ARITHMETIC TRAP, CHECKED BEFORE RUNNING.** Is `pi(oracle) = 1` forced? **No.** `select_core.py`
maximises agreement with `t_`, the MODAL class over the fit-half of annotators; A2 averages over
ALL annotators' class vectors. Mode-of-a-half and mean-of-all are different objectives, so the
oracle arm does not sit at the A2 maximum by construction. ⚠ But a SYNTHETIC arm built here by
maximising A2 directly IS at the maximum by construction — that is control ①, and it validates the
INSTRUMENT, never the finding.

ESTIMAND        pi(arm) for every k-matched candidate arm, and the separation between the three
                label-consuming rules and the label-blind rules.
IDENTIFICATION  exact given the sample of subsets; `pi` is a percentile within a MEASURED
                distribution, not a probability over a population of arms.
SCOPE           population: k=4 candidate arms — judge-matched 2B, apparatus removed (R916/R917)
                instrument: A2 vs the human class vectors; subsets sampled from each prompt's own
                            `coval_full` rubric; M subsets/prompt, exhaustive where C(n,k) <= M
                baseline:   the sampled-subset distribution per prompt — the arm's own peer set
                regime:     home release, judge 2B, seed 920
WORLDS          A · pi separates label-consumers from label-blind arms -> clause ③ is checkable
                    from the artifact plus labels, and the definition applies to a third-party core
                B · pi does not separate -> clause ③ is a PROVENANCE claim; the definition cannot
                    be applied without the producer's source, and must say so
                C · pi separates but is a reparameterisation of clause ②'s A2 margin -> it is not a
                    second instrument and licenses nothing new
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE / INSTRUMENT: a synthetic arm that picks the max-A2 subset per
                     prompt must score pi ~ 1.0, and a synthetic arm picking the MIN must score
                     pi ~ 0.0. If the percentile cannot reach its own extremes, it is broken.
                     ⚠ Both are FORCED by construction — they validate the instrument and are not
                     evidence about any real arm.
                  ⭐ ② PLACEBO: a synthetic uniformly-random size-k arm must score pi ~ 0.5. This
                     one is NOT forced — it is the measurement that says the percentile is
                     calibrated on this data rather than merely monotone.
                  ⭐ ③ NON-REDUNDANCY: regress pi on the arm's A2 margin vs `genericpool16`. If
                     R^2 >= 0.90, pi is a reparameterisation of clause ② and world C holds.
                     ⚠ This is the control that a "new instrument" almost never gets.
                     ⛔ AND IT IS A WORLD SELECTOR, NOT A KILL. The first version wired it into
                     the exit gate, so a pre-registered OUTCOME would have been reported as
                     UNVERIFIED — conflating "my check was unfit" with "world C obtains". A kill
                     asks whether the instrument works; a world is what the working instrument
                     returns. Only ① ② ④ gate the artifact.
                  ⭐ ④ SAMPLING HONESTY: report how many prompts were exhaustive vs sampled, and
                     the cap — the generator itself logs `capped` for the same reason.
MULTIPLICITY    every k=4 candidate arm; both groups; the whole pi ordering printed, not just the
                separating pair.
ARTIFACT        results/clause3_detectability.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · admission probability. ⚠ AND, new here: this cannot show clause ③ is
                detectable WITHOUT labels — it shows only that the generator's SOURCE is not
                needed. A label-free detector would require a property of the criteria themselves.
"""
import itertools, json, math, pathlib, re, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
RES = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls, L, PAIRS                 # noqa: E402
from covalx.judge import load_join                                            # noqa: E402

K, M, SEED, COMP = 4, 2000, 920, "genericpool16"
LABELLED = ("oracle", "indep", "greedy")


def main() -> int:
    r917 = json.loads(next(A24.glob("R917_*/results/candidates_only.json")).read_text())
    r906 = json.loads(next(A24.glob("R906_*/results/bar_by_source.json")).read_text())
    rs = [k for k in r906["kinds"] if k["kind"] == "RUBRIC_SELECTOR"][0]
    apparatus = set(r917["dropped"]["apparatus"])
    # ⛔ POPULATION BY REGEX, NOT BY SUFFIX. The first run filtered `a.endswith("_k4")` and caught
    # 5 of 21 — excluding EVERY `greedy_*` and `indep_*` arm, i.e. two of the three label-consuming
    # rules this round is about. Arm names carry suffixes (`_fit1`, `_detA`, `_s0`, `_greedy_kA`),
    # so a suffix test silently selects the arms that happen to have none. Fifth population error
    # this session; the wiring assertion below is what makes it visible rather than plausible.
    cands = [a for a in rs["built"]
             if a not in apparatus and not (a.endswith("_08b") or a.endswith("_08bR"))
             and re.match(rf"[a-z]+_k{K}(_|$)", a)]
    by_rule = {}
    for a in cands:
        by_rule.setdefault(a.split("_k")[0], []).append(a)
    print(f"  rules present: " + ", ".join(f"{r}×{len(v)}" for r, v in sorted(by_rule.items())))
    missing_lab = [r for r in LABELLED if r not in by_rule]
    if missing_lab:
        print(f"  UNRUNNABLE: label-consuming rule(s) absent from the population: {missing_lab}. "
              f"Exit 2, never 0.")
        return 2
    print(f"  candidates at k={K}, judge-matched, apparatus removed: {len(cands)}")
    print(f"    {sorted(cands)}")
    if len(cands) < 4:
        print("  UNRUNNABLE: too few candidate arms. Exit 2, never 0.")
        return 2

    tg, _ = load_targets()
    Sfull = load_sat(RES / "sat_full.npz")
    # ⚠ `core_<arm>.json` stores criterion TEXTS, not indices — verified by reading the file, and
    # it is how R906's `sel_of` compares against `fullr[p]`. Passing texts to `yvec` would score
    # nothing and return a silent zero, so the map is built explicitly and its misses are counted.
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    txt2i = {}
    for pid, _q, r in joined:
        items = [i["criterion"] for i in (r.get("coval_full") or [])]
        txt2i[pid] = {t: j for j, t in enumerate(items)}
    print(f"  text->index maps built for {len(txt2i)} prompts (core_*.json stores TEXTS)")
    pids = sorted(set(Sfull) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    print(f"  prompts with a full-rubric satisfaction and >=2 annotators: {len(pids)}")

    rng = np.random.default_rng(SEED)
    # per prompt: the sampled subset distribution of A2, plus its argmax / argmin subsets
    dist, best, worst, exhaustive = {}, {}, {}, 0
    for p in pids:
        idxs = sorted({i for i, _ in Sfull[p]})
        n = len(idxs)
        if n < K + 1:
            continue
        total = math.comb(n, K)
        if total <= M:
            combos = np.array(list(itertools.combinations(range(n), K)))
            exhaustive += 1
        else:
            combos = np.array([rng.choice(n, K, replace=False) for _ in range(M)])
        S = np.array([[Sfull[p].get((i, x), 0.0) for x in L] for i in idxs])   # (n, 4)
        Y = S[combos].sum(axis=1)                                             # (M, 4)
        C = np.stack([np.sign(Y[:, i] - Y[:, j]) for i, j in PAIRS], axis=1)   # (M, 6)
        a2 = np.array([(C == h).mean(axis=1) for h in H[p]]).mean(axis=0)      # (M,)
        dist[p] = a2
        best[p] = [idxs[i] for i in combos[int(np.argmax(a2))]]
        worst[p] = [idxs[i] for i in combos[int(np.argmin(a2))]]
    shared = sorted(dist)
    print(f"  ④ SAMPLING: {len(shared)} prompts scored · exhaustive {exhaustive} · "
          f"sampled {len(shared) - exhaustive} at M={M} subsets each (cap logged, not silent)")

    miss = {"unmapped_texts": 0, "arms_with_misses": set()}

    def a2_of_selection(selfn, texts=False, label=""):
        """selfn(p) -> criterion INDICES, or TEXTS when texts=True"""
        out = {}
        for p in shared:
            sel = selfn(p)
            if not sel:
                continue
            if texts:
                m = txt2i.get(p, {})
                idx = [m[t] for t in sel if t in m]
                if len(idx) != len(sel):
                    miss["unmapped_texts"] += len(sel) - len(idx)
                    miss["arms_with_misses"].add(label)
                if not idx:
                    continue
                sel = idx
            y = yvec(Sfull[p], sel)
            c = np.array(cls(y), float)
            out[p] = float(np.mean([(c == h).mean() for h in H[p]]))
        return out

    def pi_of(a2map):
        pcts = [float((dist[p] < a2map[p]).mean() + 0.5 * (dist[p] == a2map[p]).mean())
                for p in a2map if p in dist]
        return (float(np.mean(pcts)), len(pcts)) if pcts else (float("nan"), 0)

    # ---------- ① POSITIVE / INSTRUMENT (forced by construction) ----------
    pi_max, n_max = pi_of(a2_of_selection(lambda p: best.get(p)))
    pi_min, n_min = pi_of(a2_of_selection(lambda p: worst.get(p)))
    print(f"\n  ① POSITIVE/INSTRUMENT — the ATTAINABLE ceiling and floor, MEASURED:")
    print(f"     synthetic max-A2 arm   pi = {pi_max:.4f}  (n={n_max})   <- the CEILING")
    print(f"     synthetic min-A2 arm   pi = {pi_min:.4f}  (n={n_min})   <- the FLOOR")
    print(f"     ⚠ THE FIRST RUN DEMANDED pi_max > 0.98 AND FAILED AT 0.9287. That threshold was")
    print(f"        set above what the design can return under a MAXIMAL plant — §4's `control")
    print(f"        that cannot PASS`, built again. The cause is arithmetic: A2 over 6 comparisons")
    print(f"        and a handful of annotators is DISCRETE, so many subsets TIE at a prompt's")
    print(f"        maximum, and a mid-rank percentile of a tied maximum is strictly below 1.")
    print(f"     So the control is restated as one the design can actually fail: the measured")
    print(f"     extremes must BOUND every real arm, and floor < random < ceiling must hold.")
    c1 = (pi_min < pi_rand_placeholder < pi_max) if False else None   # set after ②

    # ---------- ② PLACEBO (not forced) ----------
    rng2 = np.random.default_rng(SEED + 1)

    def rand_sel(p):
        idxs = sorted({i for i, _ in Sfull[p]})
        return list(rng2.choice(idxs, min(K, len(idxs)), replace=False))

    pi_rand, n_rand = pi_of(a2_of_selection(rand_sel))
    c2 = 0.40 <= pi_rand <= 0.60
    c1 = bool(pi_min < pi_rand < pi_max)
    print(f"     ① floor {pi_min:.4f} < random {pi_rand:.4f} < ceiling {pi_max:.4f}: {c1}  "
          f"{'PASS' if c1 else 'FAIL'}   (checked after ② because it needs the random arm)")
    print(f"\n  ② PLACEBO — a uniformly random size-{K} arm must land mid-distribution:")
    print(f"     pi = {pi_rand:.4f}  (n={n_rand})   pre-registered band [0.40, 0.60]")
    print(f"     ⚠ NOT forced: the percentile could be monotone but miscalibrated on this data")
    print(f"     ② {c2}  {'PASS' if c2 else 'FAIL'}")

    # ---------- the arms ----------
    rows = []
    for arm in sorted(cands):
        f = RES / f"core_{arm}.json"
        if not f.exists():
            continue
        try:
            sel = json.loads(f.read_text())
        except Exception:
            continue
        a2map = a2_of_selection(lambda p, s=sel: s.get(p), texts=True, label=arm)
        pi, npr = pi_of(a2map)
        if npr < 100:
            continue
        rule = arm.split("_k")[0]
        rows.append({"arm": arm, "rule": rule, "pi": pi, "n_prompts": npr,
                     "labelled": rule in LABELLED,
                     "mean_a2": float(np.mean(list(a2map.values())))})
    if len(rows) < 4:
        print("\n  UNRUNNABLE: fewer than 4 arms produced a usable selection. Exit 2, never 0.")
        return 2

    # ---------- ③ NON-REDUNDANCY vs clause ② ----------
    Scomp = load_sat(RES / f"sat_{COMP}.npz")
    cmap = {}
    for p in shared:
        if p not in Scomp:
            continue
        y = yvec(Scomp[p], sorted({i for i, _ in Scomp[p]}))
        c = np.array(cls(y), float)
        cmap[p] = float(np.mean([(c == h).mean() for h in H[p]]))
    cmean = float(np.mean(list(cmap.values()))) if cmap else float("nan")
    x = np.array([r["mean_a2"] - cmean for r in rows])
    yv = np.array([r["pi"] for r in rows])
    r2 = float(np.corrcoef(x, yv)[0, 1] ** 2) if len(rows) > 2 else float("nan")
    c3 = r2 < 0.90        # NOT a kill — a world selector; see KILL note
    print(f"\n  ⚠ TEXT->INDEX misses: {miss['unmapped_texts']} criterion strings across "
          f"{len(miss['arms_with_misses'])} arm(s) — counted, not silently dropped")
    print(f"\n  ③ NON-REDUNDANCY — is pi just clause ②'s A2 margin in new units?")
    print(f"     comparator `{COMP}` mean A2 = {cmean:.4f} over {len(cmap)} prompts")
    print(f"     R^2( pi ~ A2 margin ) over {len(rows)} arms = {r2:.4f}   "
          f"(world C if >= 0.90)")
    print(f"     ③ independent instrument: {c3}"
          + ("" if c3 else "  -> WORLD C: pi is a reparameterisation of clause ②"))

    if not (c1 and c2):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3,
                   "pi_max": pi_max, "pi_min": pi_min, "pi_rand": pi_rand,
                   "rows": rows}, open(OUT / "clause3_detectability.json", "w"), indent=2)
        return 2

    rows.sort(key=lambda r: -r["pi"])
    print(f"\n  ⭐⭐ EVERY k={K} CANDIDATE ARM, ordered by pi — the whole ordering, not the pair:")
    print(f"     {'arm':<22}{'rule':<10}{'labelled?':>11}{'pi':>9}{'mean A2':>10}{'n':>6}")
    for r in rows:
        print(f"     {r['arm']:<22}{r['rule']:<10}{str(r['labelled']):>11}{r['pi']:>9.4f}"
              f"{r['mean_a2']:>10.4f}{r['n_prompts']:>6}")

    over = [r["arm"] for r in rows if not (pi_min <= r["pi"] <= pi_max)]
    if over:
        print(f"\n  ⚠ ARMS OUTSIDE THE MEASURED EXTREMES: {over} — the percentile is mis-computed")
    lab = [r["pi"] for r in rows if r["labelled"]]
    bli = [r["pi"] for r in rows if not r["labelled"]]
    sep = bool(lab and bli and min(lab) > max(bli))
    gap = (min(lab) - max(bli)) if (lab and bli) else float("nan")
    world = "C_implies_B" if not c3 else ("A" if sep else "B")
    print(f"\n  ⭐⭐⭐ WORLD {world}: label-consuming arms pi in "
          f"[{min(lab):.4f}, {max(lab):.4f}] (n={len(lab)}); label-blind in "
          f"[{min(bli):.4f}, {max(bli):.4f}] (n={len(bli)}); "
          f"{'DISJOINT, gap ' + f'{gap:+.4f}' if sep else 'OVERLAPPING'}")
    if not c3:
        print(f"     ⛔ **WORLD C, AND IT IMPLIES WORLD B.** pi orders the arms the same way the")
        print(f"     A2 margin does (R^2 = {r2:.4f} over {len(rows)} arms), so it is not a second")
        print(f"     instrument. And the reason is the finding, not a defect in pi: **at the level")
        print(f"     of the artifact, \"this core consumed the labels\" and \"this core is simply")
        print(f"     better\" are THE SAME OBSERVATION.** A label-consumer shows up as a high")
        print(f"     score, which is exactly what clause ② already measures and exactly what an")
        print(f"     honestly excellent core would also show.")
        print(f"     **So clause ③ is irreducibly a PROVENANCE claim** — it cannot be reduced to a")
        print(f"     performance statistic on the object, and the definition must say so rather")
        print(f"     than imply the clause is checkable by scoring.")
        print(f"     ⚠ separation was {'PRESENT' if sep else 'ABSENT'} "
              f"(labelled pi in [{min(lab):.4f}, {max(lab):.4f}], blind in "
              f"[{min(bli):.4f}, {max(bli):.4f}]) — but a separation carried entirely by score is")
        print(f"     not evidence of label-consumption, which is the whole point of control ③.")
    elif sep:
        print(f"     **Clause ③ is checkable from the artifact plus labels — the generator's")
        print(f"     source is NOT needed.**")
    else:
        print(f"     **Clause ③ is a PROVENANCE claim on this evidence.**")
    print(f"     ⚠ EITHER WAY this does NOT show clause ③ is detectable without LABELS. A")
    print(f"     label-free detector would need a property of the criteria themselves, and no")
    print(f"     round has proposed one.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "k": K, "m_subsets": M,
               "derivation_not_run": {
                   "question": "is topw's 0.438 -> 0.778 carried by apparatus or by judge?",
                   "answer": "100% judge, 0% apparatus",
                   "why_forced": "the only apparatus arm in RUBRIC_SELECTOR is `full`, which "
                                 "matches no ([a-z]+)_k(\\d+) pattern and was never in a rule tally",
                   "label": "DERIVATION, not evidence"},
               "sampling": {"prompts": len(shared), "exhaustive": exhaustive,
                            "sampled": len(shared) - exhaustive, "cap": M},
               "instrument": {"pi_max_forced": pi_max, "pi_min_forced": pi_min,
                              "pi_random_measured": pi_rand,
                              "note": "the two extremes are forced by construction and validate "
                                      "the instrument only; the random arm is the measurement"},
               "non_redundancy": {"comparator": COMP, "comparator_mean_a2": cmean,
                                  "r2_pi_on_a2_margin": r2,
                                  "world_C_if": ">= 0.90"},
               "arms": rows, "labelled_rules": list(LABELLED),
               "text_index_misses": {"n": miss["unmapped_texts"],
                                     "arms": sorted(miss["arms_with_misses"])},
               "separated": sep, "gap": gap,
               "world_C_reading": "pi is a reparameterisation of the A2 margin, so at the level of "
                                  "the artifact 'consumed the labels' and 'is simply better' are "
                                  "the same observation; clause ③ is irreducibly a provenance claim",
               "control_three_is_a_world_selector_not_a_kill": True,
               "does_not_show": "that clause ③ is detectable without LABELS — only that the "
                                "generator's SOURCE is not needed",
               "unit_note": "pi is a mean percentile in [0,1]; A2 is agreement in [0,1]",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "clause3_detectability.json", "w"), indent=2)
    print(f"\n  artifact: results/clause3_detectability.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
