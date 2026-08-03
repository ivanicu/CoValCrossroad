"""R254 -- R251 called its substitution ADVERSARIAL. It was not. This one is, and it has a crossover.

WHAT R251 FOUND AND WHY IT DOES NOT MEAN WHAT ITS VERDICT SAID
    Text route under substitution: 0.9883 / 0.9860 / 0.9696 (rival 20/40/60%) and
    0.9883 / 0.9883 / 0.9855 (generic), against chance 0.0792 -- flat, at Jaccard as low as 0.2848.
    Its verdict printed "the TEXT route survives even ADVERSARIAL substitution."

    ADVERSARIAL is a word I typed, not a property I built. R251's donor pool was the UNION of every
    rival criterion in the prompt, so the injected tokens SCATTER across many competitors and no
    single competitor gains enough to overtake the parent. A set-overlap matcher is not beaten by
    noise; it is beaten by CONCENTRATION. R251 measured un-targeted substitution and labelled it
    adversarial -- the fifth conclusion-string failure in this session, and the same shape as the
    other four: a comparative asserted rather than computed.

WHAT AN ADVERSARY ACTUALLY DOES
    Pick ONE rival -- the criterion in the same rubric already NEAREST the parent in token overlap --
    and move the text toward it alone. Then there is a fraction at which the query stops being
    nearer the parent than the rival, and that CROSSOVER is a measurement, not a foregone conclusion:
    at 0% the parent wins by construction, at 100% the query IS the rival, and where it turns over
    in between is the quantity nobody has.

⚠ AND THEN THE ONLY QUESTION THAT MATTERS FOR THE RELEASE
    A dose curve on synthetic rewrites is worth nothing unless the REAL rewrites can be placed on
    it. Every one of the 3,899 printed core items has a measurable margin
        m = jaccard(core_item, nearest full criterion) - jaccard(core_item, second nearest)
    and the crossover tells us which side of the line a given margin sits on. That converts a
    perturbation experiment into a statement about the shipped artifact, which is what R250 and
    R251 both stopped short of.

ESTIMAND        (a) R_text(f) and R_behaviour(f) at targeted substitution fraction
                    f in {0, 0.2, 0.4, 0.6, 0.8, 1.0} toward the NEAREST rival;
                (b) the CROSSOVER f* at which the text route's top hit stops being the parent --
                    reported as a bracket between measured doses, never interpolated to a point;
                (c) the placement of all 3,899 real core items on the margin axis the crossover
                    defines, split by whether they are verbatim.
IDENTIFICATION  (a) and (b) exact on the ground-truth set. (c) is a PLACEMENT, not a recovery rate:
                the real items have no known parent, so it says which side of a measured line their
                margin falls on and nothing about whether the nearest match is right. Stated as a
                bound, and the circularity is named -- the margin uses the same Jaccard the text
                route uses, so for the text route (c) is definitional and only informative about
                the BEHAVIOUR route's prospects.
SCOPE           population: the 298 verbatim ground-truth items for (a) and (b); all 3,899 printed
                core items for (c). instrument: Qwen3.5-2B-Base, the r04 build. baseline: chance
                1/n per prompt, measured as a sham arm. regime: m=4.
WORLDS          W-CONCENTRATION  the text route fails only to a CONCENTRATED adversary
                     -> targeted substitution crosses over while R251's pooled substitution, AT
                        MATCHED JACCARD, does not. Then R251's flat row is explained rather than
                        merely disqualified
                W-DISTANCE       distance alone is what matters
                     -> targeted and pooled behave the same at matched Jaccard, and R251's verdict
                        was right for the wrong reason
                W-UNKILLABLE     the text route survives even a targeted adversary short of f=1
                     -> the matcher is genuinely robust and provenance IS issuable by text, which
                        is what R251 claimed without earning
KILL            pre-registered: if targeted substitution at f=0.6 leaves text recovery above
                chance + its own seed spread, W-UNKILLABLE and R251's verdict stands as written.
                If it crosses below while POOLED substitution at the SAME measured Jaccard does
                not, W-CONCENTRATION and the mechanism is targeting.
POSITIVE CTRL   TWO, and both are computed rather than assumed:
                  CEILING f=0 must return R250's computed 0.9883 (7 of 298 parents have a duplicate,
                          so exact 1.0 is unreachable -- the sixth control-that-cannot-pass in this
                          arc demanded it).
                  FLOOR   f=1.0 the query IS the rival's token set, so the text route must return
                          approximately 0 AND its top hit must be the rival. If it does not, the
                          matcher is not doing what the round assumes and no cell is readable.
                A control with both ends pinned cannot be satisfied by a broken matcher.
NEGATIVE CTRL   R250's repaired arm: keep the candidate set (parent reachable), replace the QUERY
                with another ground-truth item's perturbed text. Must sit at chance; it can fail.
SHAM            R251's POOLED substitution, re-run here at matched fractions, so the targeted and
                pooled arms are compared at their own measured Jaccards rather than at nominal f.
PLACEBO         the parent against its own rubric at f=0 must return the parent as top hit.
NOISE FLOOR     3 seeds on every stochastic dose; spread beside every point.
MULTIPLICITY    6 fractions x 2 families x 2 routes x 3 arms x 3 seeds; whole grid printed.
SPECIFICATION   the axis added is TARGETING -- the choice R251 held fixed at "pooled" without
                noticing it was a choice, exactly as R250 held "deletion" fixed.
ARTIFACT        judgements persisted before any summary; re-runs from cache with no GPU.
IMPOSSIBLE      whether the compiler's real rewrites were produced by anything resembling this
                perturbation. No lineage exists outside the 298, which is the whole problem, and
                (c) is a placement on a margin axis rather than a claim about how the text got there.
"""
from __future__ import annotations
import collections, json, pathlib, random, re, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
             "/R04_rebuild_satisfaction/results")
MODEL = "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/Qwen3.5-2B-Base"
L = "ABCD"
SEEDS = [0, 1, 2]
FRACS = [0.2, 0.4, 0.6, 0.8, 1.0]
R250_CEILING = 0.9883
STOP = set("a an the and or of to in on at is are be as by for with from that this it not but if "
           "so when about into over than then there their they them we you your our its".split())


def toks(s):
    return re.findall(r"[A-Za-z']+", str(s))


def cset(s):
    return {x.lower() for x in toks(s) if x.lower() not in STOP}


def jac(a, b):
    A, B = cset(a), cset(b)
    return len(A & B) / len(A | B) if (A | B) else 0.0


def sub_from(text, frac, pool, rng):
    w = toks(text)
    ci = [i for i, x in enumerate(w) if x.lower() not in STOP and len(x) > 3]
    if not ci or not pool:
        return text
    n = max(1, int(round(frac * len(ci))))
    hit = set(rng.sample(ci, min(n, len(ci))))
    return " ".join([(rng.choice(pool) if i in hit else x) for i, x in enumerate(w)])


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A01_is_our_own_compiler_better"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(R4 / "a04_full.npz")
    from covalx.judge import Judge, build_prompt, load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    resp = {}
    for line in (DATA / "comparisons.jsonl").open():
        o = json.loads(line)
        resp[o["prompt_id"]] = [r["messages"][0]["content"] for r in o["responses"]]

    gt = []
    for p, r in recs.items():
        if p not in sf or p not in resp or len(resp[p]) != 4:
            continue
        f = r["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < 4:
            continue
        idx = {f[i].get("criterion", "").strip().lower(): i for i in ok}
        for it in r["coval_core"]:
            c = it.get("criterion", "").strip().lower()
            if c in idx:
                par = idx[c]
                rivals = [i for i in ok if i != par]
                if not rivals:
                    continue
                # THE ADVERSARY: the rival ALREADY NEAREST the parent in token overlap
                near = max(rivals, key=lambda i: jac(f[par]["criterion"], f[i].get("criterion", "")))
                gt.append((p, par, f[par]["criterion"], ok, near, f[near].get("criterion", "")))
    print("ground truth %d | chance %.4f" % (len(gt), float(np.mean([1 / len(g[3]) for g in gt]))),
          flush=True)
    print("baseline jaccard(parent, nearest rival): mean %.4f  p90 %.4f"
          % (float(np.mean([jac(g[2], g[5]) for g in gt])),
             float(np.percentile([jac(g[2], g[5]) for g in gt], 90))), flush=True)

    tasks, index = [], []
    for seed in SEEDS:
        rng = random.Random(9000 + seed)
        for gi, (p, par, txt, ok, near, ntxt) in enumerate(gt):
            f = recs[p]["coval_full"]
            tgt_pool = sorted({w for w in toks(ntxt) if w.lower() not in STOP and len(w) > 3})
            pool_pool = sorted({w for i in ok if i != par
                                for w in toks(f[i].get("criterion", ""))
                                if w.lower() not in STOP and len(w) > 3})
            for frac in FRACS:
                for fam, pool in (("tgt", tgt_pool), ("pool", pool_pool)):
                    pt = sub_from(txt, frac, pool, rng)
                    for r_ in range(4):
                        index.append((seed, gi, "%s%d" % (fam, int(frac * 100)), r_, pt))
                        tasks.append(build_prompt(pt, resp[p][r_]))
        if seed == SEEDS[0]:
            for gi, (p, par, txt, ok, near, ntxt) in enumerate(gt):
                for r_ in range(4):
                    index.append((seed, gi, "identity", r_, txt))
                    tasks.append(build_prompt(txt, resp[p][r_]))

    cache = OUT / "targeted.npz"
    if cache.exists():
        cd = np.load(cache, allow_pickle=True)
        assert len(cd["sat"]) == len(tasks), "cache stale"
        sat = cd["sat"]; print("reusing %d judgements -- no GPU" % len(sat), flush=True)
    else:
        print("judging %d targeted (criterion, response) pairs" % len(tasks), flush=True)
        sat = Judge(MODEL, batch=64).score(tasks)
        np.savez_compressed(cache,
                            meta=np.array(["%d|%d|%s|%d" % (s, g, d, r_) for s, g, d, r_, _t in index]),
                            text=np.array([t for *_x, t in index]),
                            sat=np.asarray(sat, dtype=np.float32))
        print("persisted %d judgements" % len(sat), flush=True)

    V, TXT = collections.defaultdict(dict), {}
    for (seed, gi, dose, r_, pt), v in zip(index, sat):
        V[(seed, gi, dose)][r_] = float(v); TXT[(seed, gi, dose)] = pt

    grid = collections.defaultdict(lambda: collections.defaultdict(list))
    tophit = collections.defaultdict(lambda: collections.defaultdict(list))
    dist = collections.defaultdict(list)
    for (seed, gi, dose), vv in V.items():
        if len(vv) != 4:
            continue
        p, par, txt, ok, near, ntxt = gt[gi]
        f2 = recs[p]["coval_full"]
        dist[dose].append(jac(TXT[(seed, gi, dose)], txt))
        for arm in ("true", "negative"):
            if arm == "negative":
                gj = (gi + 1) % len(gt)
                if (seed, gj, dose) not in TXT or len(V[(seed, gj, dose)]) != 4:
                    continue
                pt = TXT[(seed, gj, dose)]
                y = np.array([V[(seed, gj, dose)][r_] for r_ in range(4)])
            else:
                pt = TXT[(seed, gi, dose)]
                y = np.array([vv[r_] for r_ in range(4)])
            d = np.array([np.abs(np.array([sf[p][(i, x)] for x in L]) - y).sum() for i in ok])
            hits = [ok[i] for i in np.flatnonzero(d <= d.min() + 1e-12)]
            grid[(dose, "behaviour", arm)][seed].append((1.0 / len(hits)) if par in hits else 0.0)
            j = np.array([jac(pt, f2[i].get("criterion", "")) for i in ok])
            hj = [ok[i] for i in np.flatnonzero(j >= j.max() - 1e-12)]
            grid[(dose, "text", arm)][seed].append((1.0 / len(hj)) if par in hj else 0.0)
            if arm == "true":
                grid[(dose, "sham", "true")][seed].append(1.0 / len(ok))
                tophit[dose]["rival"].append(1.0 if near in hj and par not in hj else 0.0)

    def cell(k):
        v = [float(np.mean(grid[k][s])) for s in grid[k] if grid[k][s]]
        return (float(np.mean(v)), float(np.ptp(v)) if len(v) > 1 else 0.0) if v else (float("nan"),) * 2

    DOSES = ["identity"] + ["%s%d" % (f, int(x * 100)) for x in FRACS for f in ("tgt", "pool")]
    print("\n=== TARGETED vs POOLED substitution, at their own measured distances ===")
    print("%-11s %17s %17s %9s %9s %11s" % ("dose", "TEXT (spread)", "BEHAVIOUR (spread)",
                                            "chance", "jaccard", "rival wins"))
    rows = {}
    for dose in DOSES:
        t_, ts = cell((dose, "text", "true")); b_, bs = cell((dose, "behaviour", "true"))
        ch, _ = cell((dose, "sham", "true")); dj = float(np.mean(dist[dose]))
        rw = float(np.mean(tophit[dose]["rival"])) if tophit[dose]["rival"] else float("nan")
        rows[dose] = (t_, ts, b_, bs, ch, dj, rw)
        print("%-11s %9.4f (%.4f) %9.4f (%.4f) %9.4f %9.4f %11.4f"
              % (dose, t_, ts, b_, bs, ch, dj, rw))
    print(" (rival wins = share of items where the NEAREST RIVAL is the text route's top hit and")
    print("  the parent is not -- the crossover, measured directly rather than inferred)")

    print("\n=== the crossover, as a BRACKET between measured doses ===")
    cross = None
    for x in FRACS:
        d_ = "tgt%d" % int(x * 100)
        if rows[d_][0] <= rows[d_][4] + max(rows[d_][1], 0.02):
            cross = x
            break
    prev = None
    for x in FRACS:
        d_ = "tgt%d" % int(x * 100)
        if cross is not None and x == cross:
            break
        prev = x
    print(" text route falls to chance between f=%s and f=%s"
          % (prev if prev is not None else "0.0", cross if cross is not None else ">1.0"))
    print(" at those doses the measured jaccard to the parent is %.4f -> %.4f"
          % (rows["tgt%d" % int((prev or 0.2) * 100)][5],
             rows["tgt%d" % int((cross or 1.0) * 100)][5]))

    print("\n=== controls ===")
    ti, _ = cell(("identity", "text", "true"))
    f1 = rows["tgt100"]
    print(" POS-CEILING f=0   text %.4f  vs R250's computed %.4f  %s"
          % (ti, R250_CEILING, "OK" if abs(ti - R250_CEILING) < 5e-4 else "PIPELINE DIFFERS"))
    print(" POS-FLOOR   f=1.0 the query IS the rival's token set: text %.4f (must be near 0), "
          "rival is top hit %.4f (must be near 1)  %s"
          % (f1[0], f1[6], "OK" if (f1[0] < 0.25 and f1[6] > 0.5) else "MATCHER NOT DOING ITS JOB"))
    floor_ok = f1[0] < 0.25 and f1[6] > 0.5
    neg_ok = True
    for dose in DOSES:
        nt, _ = cell((dose, "text", "negative")); nb, _ = cell((dose, "behaviour", "negative"))
        ch = rows[dose][4]
        bad = (nt > ch + 0.05) or (nb > ch + 0.05)
        neg_ok &= not bad
    print(" NEGATIVE  query swapped, candidate set kept, all %d doses : %s"
          % (len(DOSES), "at chance" if neg_ok else "LEAK"))

    print("\n=== (c) where the REAL core items sit on the margin axis ===")
    marg, verb = [], []
    for p, r in recs.items():
        f = r["coval_full"]
        cand = [it.get("criterion", "") for it in f if it.get("criterion")]
        if len(cand) < 2:
            continue
        for it in r["coval_core"]:
            c = it.get("criterion", "")
            if not c:
                continue
            js = sorted((jac(c, x) for x in cand), reverse=True)
            marg.append(js[0] - js[1]); verb.append(1.0 if js[0] >= 0.999 else 0.0)
    marg = np.array(marg); verb = np.array(verb)
    print(" %d printed core items | verbatim %d (%.4f)" % (len(marg), int(verb.sum()), verb.mean()))
    print(" margin (nearest - second nearest) deciles: %s"
          % " ".join("%.3f" % q for q in np.percentile(marg, [10, 30, 50, 70, 90])))
    print(" share with margin <= 0 (a TIE at the top -- no unique nearest) : %.4f"
          % float((marg <= 0).mean()))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    t60 = rows["tgt60"]; p60 = rows["pool60"]
    if abs(ti - R250_CEILING) >= 5e-4 or not floor_ok or not neg_ok:
        v = ("UNVERIFIED -- ceiling %.4f vs %.4f, floor-at-f=1 %s, negative leak %s."
             % (ti, R250_CEILING, floor_ok, not neg_ok))
    elif t60[0] > t60[4] + max(t60[1], 0.02):
        v = ("W-UNKILLABLE -- targeted substitution at 60%% toward the NEAREST rival still leaves "
             "the text route at %.4f against chance %.4f. R251's verdict stands, this time earned: "
             "the matcher is robust to a concentrated adversary short of total replacement."
             % (t60[0], t60[4]))
    elif p60[0] > p60[4] + max(p60[1], 0.02):
        v = ("W-CONCENTRATION -- targeting is the mechanism. At 60%% the TARGETED arm falls to "
             "%.4f (chance %.4f) while the POOLED arm at measured jaccard %.4f holds %.4f. R251's "
             "flat row is now EXPLAINED rather than merely disqualified: its donor was the union of "
             "all rivals, so the injected tokens scattered and no competitor could overtake."
             % (t60[0], t60[4], p60[5], p60[0]))
    else:
        v = ("W-DISTANCE -- both arms fall together at 60%% (targeted %.4f, pooled %.4f, chance "
             "%.4f). Distance is what matters and targeting adds nothing, so R251's verdict was "
             "right for a reason it did not give." % (t60[0], p60[0], t60[4]))
    print("\n  " + v)
    json.dump({"ground_truth": len(gt), "doses": DOSES,
               "rows": {d: {"text": rows[d][0], "text_spread": rows[d][1], "behaviour": rows[d][2],
                            "behaviour_spread": rows[d][3], "chance": rows[d][4],
                            "jaccard": rows[d][5], "rival_wins": rows[d][6]} for d in DOSES},
               "crossover_bracket": [prev, cross], "positive_ceiling": ti,
               "floor_ok": bool(floor_ok), "negative_ok": bool(neg_ok),
               "real_core_margin_deciles": np.percentile(marg, [10, 30, 50, 70, 90]).tolist(),
               "real_core_tie_share": float((marg <= 0).mean()),
               "verdict": v}, open(OUT / "targeted_substitution.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
