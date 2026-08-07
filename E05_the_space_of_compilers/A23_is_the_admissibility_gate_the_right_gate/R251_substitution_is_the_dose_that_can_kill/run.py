"""R251 -- R250's dose axis could not kill the text route. This one can, and that is the point.

WHAT R250 ESTABLISHED AND WHAT IT COULD NOT
    Behaviour route: 0.3031 / 0.1913 / 0.1051 at 20/40/60% content-token DELETION, against chance
    0.0792. Text route: 0.9883 / 0.9871 / 0.9855 -- flat, at every dose, out to 60%.

    R250 says in its own output why the flat row is not evidence: DELETING tokens never INTRODUCES
    a competitor's tokens, so a subset of the parent stays nearer the parent than anything else.
    A set-overlap matcher cannot be killed by deletion. The text route was never tested.

    That makes R250's headline reading -- provenance survives to 40% -- rest entirely on the
    BEHAVIOUR route, and its own verdict string quoted the disqualified one via max().

WHAT A REAL REWRITE DOES, AND WHAT THIS ROUND ADDS
    Rewriting SUBSTITUTES. R249 measured the direction the compiler travels: the core's criteria are
    shorter (88.2 vs 97.7 chars) and as redundant as a generic vocabulary, so the compiler moves
    text TOWARD SHARED WORDING. Substitution is therefore not an adversarial extreme here -- it is
    the realistic dose, and deletion was the unrealistic one.

    Two substitution families, because they fail differently:
      SUB-RIVAL    replace content tokens with tokens from ANOTHER criterion in the same rubric.
                   Directly seeds a competitor. The adversarial bound.
      SUB-GENERIC  replace content tokens with tokens from R240's 200-criterion generic vocabulary.
                   The direction R249 measured. The realistic bound.

⚠ THE COMPARISON THAT MAKES THIS DECISIVE, AND WHY R250 ALONE COULD NOT
    Recovery must be compared AT MATCHED TEXT DISTANCE. If substitution kills the text route at the
    same token-Jaccard where deletion does not, the mechanism is SUBSTITUTION and not DISTANCE, and
    that is a statement neither round makes alone. Distance is therefore a measured covariate here,
    reported per cell, and the headline comparison is interpolated to a common Jaccard.

ESTIMAND        recovery R(route, family, dose) of a KNOWN parent among its own prompt's rubric,
                and the token-Jaccard at which each route reaches chance -- separately for deletion
                (from R250's persisted curve) and for each substitution family.
IDENTIFICATION  exact on the ground-truth set: the parent is known by string identity. The
                matched-distance comparison is an interpolation between measured cells and is
                labelled as such, never as a measured cell of its own.
SCOPE           population: the 298 core items that are verbatim copies of a criterion in their own
                prompt's full rubric. instrument: Qwen3.5-2B-Base via covalx.judge, the same build
                as r04 and R250, so all three curves live on one scale. baseline: chance = 1/n per
                prompt, measured as a sham arm. regime: m=4, doses below.
WORLDS          W1 provenance survives realistic rewriting
                     -> the text route stays above chance under SUB-GENERIC at 40%
                W2 only BEHAVIOUR is usable
                     -> text collapses to chance under substitution while behaviour holds its
                        R250 level. The certificate must then name the route, because the two
                        disagree about what is recoverable
                W3 provenance dies past verbatim copying
                     -> both routes at chance under both families by 40%. Then 0.0777 -- the
                        verbatim share -- IS the whole of recoverable provenance, and that is the
                        register entry, measured
KILL            pre-registered, thresholds fixed before the run:
                  - text route under SUB-GENERIC at 40% within its sham arm's spread of chance
                    -> the text route is unusable for real rewrites and R250's flat row is retired
                  - BOTH routes within chance at 40% under BOTH families -> W3, and the
                    certificate's provenance field is capped at the verbatim share
                  - text route above chance under SUB-RIVAL at 40% -> W1 and the field is issuable
                    by text alone, which no result so far supports
POSITIVE CTRL   dose 0 in this round's own pipeline must return the CEILING COMPUTED IN R250,
                0.9883, not 1.0 -- 7 of 298 parents have a duplicate in their own rubric and the
                1/k tie rule makes exact 1.0 unreachable. Pinned to a number computed elsewhere,
                so it can fail.
NEGATIVE CTRL   R250's REPAIRED one, carried forward: keep the candidate set (parent reachable),
                replace the QUERY with another ground-truth item's perturbed text. Must sit at
                chance. It can fail, because the parent is reachable throughout.
SHAM            a random criterion from the same prompt: the chance floor, measured not computed.
DISTANCE CTRL   every dose reports its own mean token-Jaccard to the parent. A substitution dose
                whose distance does not fall below the matched deletion dose is not a stronger
                perturbation and its cell is void -- checked mechanically, not by eye.
NOISE FLOOR     3 seeds on every stochastic dose; spread beside every point.
MULTIPLICITY    (3 deletion doses from R250 + 6 substitution doses) x 2 routes x 3 arms x 3 seeds.
                Whole grid printed, including the cells that kill the finding.
SPECIFICATION   the axis this round adds is PERTURBATION FAMILY -- the one R250 held fixed at
                "deletion" without noticing it was a choice.
ARTIFACT        judgements persisted before any summary; the round re-runs from cache with no GPU.
IMPOSSIBLE      whether the compiler's ACTUAL rewrites sit where SUB-GENERIC puts them. The real
                rewrites have no ground truth -- that is the whole problem -- so their position on
                this axis is measured only through token-Jaccard, which is the very quantity the
                text route uses. Circular for the text route, and stated rather than worked around.
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
GTENSOR = ROOT / ("E05_the_space_of_compilers/A20_is_a_global_core_real/R240_fit_a_global_core"
                  "/results/sat_global.npz")
MODEL = "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/Qwen3.5-2B-Base"
L = "ABCD"
SEEDS = [0, 1, 2]
FAMILIES = [("rival", 0.2), ("rival", 0.4), ("rival", 0.6),
            ("generic", 0.2), ("generic", 0.4), ("generic", 0.6)]
R250_CEILING = 0.9883
R250_DELETION = {0.2: (0.9883, 0.3031, 0.7995), 0.4: (0.9871, 0.1913, 0.6000),
                 0.6: (0.9855, 0.1051, 0.4014)}       # dose -> (text, behaviour, jaccard)
STOP = set("a an the and or of to in on at is are be as by for with from that this it not but if "
           "so when about into over than then there their they them we you your our its".split())


def toks(s):
    return re.findall(r"[A-Za-z']+", str(s))


def jac(a, b):
    A = {x.lower() for x in toks(a) if x.lower() not in STOP}
    B = {x.lower() for x in toks(b) if x.lower() not in STOP}
    return len(A & B) / len(A | B) if (A | B) else 0.0


def substitute(text, frac, donor_tokens, rng):
    """Replace `frac` of the content tokens with tokens drawn from a donor pool. Unlike deletion
    this INTRODUCES foreign tokens, which is the only thing a set-overlap matcher can lose to."""
    w = toks(text)
    ci = [i for i, x in enumerate(w) if x.lower() not in STOP and len(x) > 3]
    if not ci or not donor_tokens:
        return text
    n = max(1, int(round(frac * len(ci))))
    hit = set(rng.sample(ci, min(n, len(ci))))
    out = [(rng.choice(donor_tokens) if i in hit else x) for i, x in enumerate(w)]
    return " ".join(out)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
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
                gt.append((p, idx[c], f[idx[c]]["criterion"], ok))
    print("ground truth %d items | chance %.4f"
          % (len(gt), float(np.mean([1 / len(g[3]) for g in gt]))), flush=True)

    gen_pool = []
    if GTENSOR.exists():
        gv = np.load(GTENSOR, allow_pickle=True)["vocab"]
        for s in gv:
            gen_pool += [w for w in toks(s) if w.lower() not in STOP and len(w) > 3]
    gen_pool = sorted(set(gen_pool))
    print("generic donor pool: %d distinct content tokens from R240's vocabulary" % len(gen_pool),
          flush=True)

    tasks, index = [], []
    for seed in SEEDS:
        rng = random.Random(7000 + seed)
        for gi, (p, parent, txt, ok) in enumerate(gt):
            f = recs[p]["coval_full"]
            rivals = [f[i].get("criterion", "") for i in ok if i != parent]
            rival_pool = sorted({w for c in rivals for w in toks(c)
                                 if w.lower() not in STOP and len(w) > 3})
            for fam, frac in FAMILIES:
                pool = rival_pool if fam == "rival" else gen_pool
                pt = substitute(txt, frac, pool, rng)
                for r_ in range(4):
                    index.append((seed, gi, "%s%d" % (fam, int(frac * 100)), r_, pt))
                    tasks.append(build_prompt(pt, resp[p][r_]))
        for gi, (p, parent, txt, ok) in enumerate(gt):        # dose 0, judged once
            if seed != SEEDS[0]:
                break
            for r_ in range(4):
                index.append((seed, gi, "identity", r_, txt))
                tasks.append(build_prompt(txt, resp[p][r_]))

    cache = OUT / "substituted.npz"
    if cache.exists():
        cd = np.load(cache, allow_pickle=True)
        assert len(cd["sat"]) == len(tasks), "cache stale -- task count differs"
        sat = cd["sat"]
        print("reusing %d persisted judgements -- no GPU" % len(sat), flush=True)
    else:
        print("judging %d substituted (criterion, response) pairs" % len(tasks), flush=True)
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
    dist = collections.defaultdict(list)
    for (seed, gi, dose), vv in V.items():
        if len(vv) != 4:
            continue
        p, parent, txt, ok = gt[gi]
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
            grid[(dose, "behaviour", arm)][seed].append(
                (1.0 / len(hits)) if parent in hits else 0.0)
            j = np.array([jac(pt, f2[i].get("criterion", "")) for i in ok])
            hj = [ok[i] for i in np.flatnonzero(j >= j.max() - 1e-12)]
            grid[(dose, "text", arm)][seed].append((1.0 / len(hj)) if parent in hj else 0.0)
            if arm == "true":
                grid[(dose, "sham", "true")][seed].append(1.0 / len(ok))

    def cell(k):
        v = [float(np.mean(grid[k][s])) for s in grid[k] if grid[k][s]]
        return (float(np.mean(v)), float(np.ptp(v)) if len(v) > 1 else 0.0) if v else (float("nan"),) * 2

    DOSES = ["identity"] + ["%s%d" % (f, int(x * 100)) for f, x in FAMILIES]
    print("\n=== SUBSTITUTION: the dose that introduces a competitor's tokens ===")
    print("%-12s %18s %18s %10s %11s" % ("dose", "TEXT (spread)", "BEHAVIOUR (spread)",
                                         "chance", "jaccard"))
    rows = {}
    for dose in DOSES:
        t_, ts = cell((dose, "text", "true")); b_, bs = cell((dose, "behaviour", "true"))
        ch, _ = cell((dose, "sham", "true")); dj = float(np.mean(dist[dose]))
        rows[dose] = (t_, ts, b_, bs, ch, dj)
        print("%-12s %10.4f (%.4f) %10.4f (%.4f) %10.4f %11.4f" % (dose, t_, ts, b_, bs, ch, dj))

    print("\n=== the comparison R250 could not make: MATCHED TEXT DISTANCE ===")
    print("%-28s %10s %10s %10s" % ("perturbation @ jaccard", "jaccard", "TEXT", "BEHAVIOUR"))
    for frac, (dt, db, dj) in sorted(R250_DELETION.items()):
        print("%-28s %10.4f %10.4f %10.4f" % ("DELETION %d%%" % int(frac * 100), dj, dt, db))
    for fam in ("rival", "generic"):
        for frac in (0.2, 0.4, 0.6):
            d_ = "%s%d" % (fam, int(frac * 100))
            print("%-28s %10.4f %10.4f %10.4f"
                  % ("SUBSTITUTION %s %d%%" % (fam, int(frac * 100)), rows[d_][5],
                     rows[d_][0], rows[d_][2]))
    print(" -> read DOWN the jaccard column: wherever a substitution row sits at the same distance")
    print("    as a deletion row, any difference in TEXT recovery is the FAMILY, not the distance.")

    print("\n=== controls ===")
    ti, _ = cell(("identity", "text", "true"))
    print(" POSITIVE  dose 0 text route : %.4f  vs R250's COMPUTED ceiling %.4f  %s"
          % (ti, R250_CEILING, "OK" if abs(ti - R250_CEILING) < 5e-4 else "PIPELINE DIFFERS"))
    dist_ok = True
    for fam in ("rival", "generic"):
        for frac in (0.2, 0.4, 0.6):
            d_ = "%s%d" % (fam, int(frac * 100))
            ok_ = rows[d_][5] <= R250_DELETION[frac][2] + 1e-9
            dist_ok &= ok_
            if not ok_:
                print(" DISTANCE  %s is NOT closer to the parent than deletion at the same frac "
                      "(%.4f > %.4f) -- cell VOID" % (d_, rows[d_][5], R250_DELETION[frac][2]))
    print(" DISTANCE  every substitution dose moves the text at least as far as matched deletion: %s"
          % ("OK" if dist_ok else "SOME CELLS VOID"))
    neg_ok = True
    for dose in DOSES:
        nt, _ = cell((dose, "text", "negative")); nb, _ = cell((dose, "behaviour", "negative"))
        ch = rows[dose][4]
        bad = (nt > ch + 0.05) or (nb > ch + 0.05)
        neg_ok &= not bad
        print("   NEG %-12s text %.4f  behaviour %.4f  chance %.4f  %s"
              % (dose, nt, nb, ch, "LEAK" if bad else "at chance"))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    g40 = rows["generic40"]; r40 = rows["rival40"]
    if abs(ti - R250_CEILING) >= 5e-4 or not neg_ok:
        v = "UNVERIFIED -- positive %.4f vs %.4f, negative leak %s." % (ti, R250_CEILING, not neg_ok)
    elif r40[0] > r40[4] + max(r40[1], 0.02):
        v = ("W1 -- the TEXT route survives even ADVERSARIAL substitution: %.4f at rival-40%% "
             "against chance %.4f. Provenance is issuable by text alone." % (r40[0], r40[4]))
    elif g40[0] <= g40[4] + max(g40[1], 0.02) and g40[2] > g40[4] + max(g40[3], 0.02):
        v = ("W2 -- ONLY THE BEHAVIOUR ROUTE IS USABLE. Under generic substitution at 40%% the text "
             "route falls to %.4f against chance %.4f while behaviour holds %.4f. R250's flat "
             "0.9871 text row is RETIRED: it measured a matcher that deletion cannot hurt. The "
             "certificate's provenance field must name the ROUTE, because the two routes disagree "
             "about what is recoverable." % (g40[0], g40[4], g40[2]))
    elif g40[0] <= g40[4] + 0.02 and g40[2] <= g40[4] + max(g40[3], 0.02):
        v = ("W3 -- provenance dies past verbatim copying. Both routes are at chance under generic "
             "substitution at 40%% (text %.4f, behaviour %.4f, chance %.4f). The verbatim share, "
             "0.0777, IS the whole of recoverable provenance on this release, and that is now a "
             "measurement with an MDE rather than an assertion." % (g40[0], g40[2], g40[4]))
    else:
        v = ("MIXED -- text %.4f behaviour %.4f against chance %.4f at generic-40%%; the arms do "
             "not separate cleanly. Reported as MIXED, never rounded to either world."
             % (g40[0], g40[2], g40[4]))
    print("\n  " + v)
    json.dump({"ground_truth": len(gt), "doses": DOSES,
               "rows": {d: {"text": rows[d][0], "text_spread": rows[d][1], "behaviour": rows[d][2],
                            "behaviour_spread": rows[d][3], "chance": rows[d][4],
                            "jaccard": rows[d][5]} for d in DOSES},
               "r250_deletion": {str(k): v_ for k, v_ in R250_DELETION.items()},
               "positive": ti, "distance_ok": bool(dist_ok), "negative_ok": bool(neg_ok),
               "verdict": v}, open(OUT / "substitution_dose.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
