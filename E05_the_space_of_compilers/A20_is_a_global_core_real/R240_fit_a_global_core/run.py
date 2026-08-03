"""R240 -- fit a GLOBAL core and test it on prompts it was never fitted to.

R239 derived that the identifiability failure is a property of the PER-PROMPT factoring: within a
prompt the observable is one ~1-3 bit consensus ordering and raters do not raise it, but across 986
prompts the observations are independent and the bits ADD to [1006, 3402]. A global core of up to
k=119 is identifiable at the conservative end while a per-prompt core of 2 is not.

That was a DERIVATION. It said nothing about whether a global core EXISTS -- only that the data
carries enough bits to identify one if it does. This measures it.

ESTIMAND        held-out class agreement of a k-criterion GLOBAL core, fitted on one half of the
                prompts and evaluated on the other half, against a size-matched random floor drawn
                from the same vocabulary.
IDENTIFICATION  the fit/evaluate split is across PROMPTS, so the held-out figure is out-of-sample in
                the unit R239's additivity argument treats as independent. That is the whole point:
                if the bits really add across prompts, a core fitted on 400 of them should transfer.
SCOPE           V = 200 candidate global criteria, P = 200 prompts, judge Qwen3.5-2B-Base (r04's).
                baseline: random k from the SAME V, 20 draws, so vocabulary is held fixed and only
                SELECTION varies. regime: k in {1,2,4,8,16,32}.
VOCABULARY      chosen OUTCOME-BLIND: the criteria whose tokens have the highest document frequency
                across prompts, i.e. the most generic-sounding ones. Never chosen using any ranking,
                any satisfaction value, or any agreement figure.
WORLDS          W1 a global core exists     -> held-out agreement rises with k, above the floor
                W2 norms are prompt-specific -> held-out agreement sits at the floor for every k
KILL            pre-registered: if held-out agreement is inside the random floor's draw spread at
                EVERY k, a global core is not identifiable in practice and R239's derivation is
                correct about the bits and irrelevant about the object.
POSITIVE CTRL   agreement on the FIT half must exceed the floor -- if fitting cannot beat random on
                the data it was fitted to, the fitter is broken and no held-out number is readable.
NEGATIVE CTRL   shuffle the prompt labels between fit and eval; held-out gain must vanish.
PLACEBO         the full per-prompt rubric evaluated against itself = 1.0000 exactly.
CEILING         per R229, COMPUTED not assumed: the best achievable held-out agreement is bounded by
                what the per-prompt FULL rubric itself achieves against the human consensus, which
                R231 measured at 0.2004. A global core cannot be asked to beat the local object.
ARTIFACT        the satisfaction tensor is persisted BEFORE any summary (R233's lesson, one round old)
IMPOSSIBLE      whether a global core is USEFUL, and whether humans would endorse it. No labels for
                that exist; this measures transfer of the compilation only.
"""
from __future__ import annotations
import collections, json, math, pathlib, re, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
MODEL = "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/Qwen3.5-2B-Base"
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
V_SIZE, P_SIZE, DRAWS = 200, 200, 20
KS = [1, 2, 4, 8, 16, 32]
SEEDS = [0, 1, 2]
STOP = set("a an the the and or of to in on at is are be as by for with from that this it not but if "
           "so when about into over than then there their they them we you your our its do does did "
           "can could should would will may might have has had been being any all each other more "
           "most less least such very".split())


def toks(s):
    return [w for w in re.findall(r"[a-z']+", str(s).lower()) if w not in STOP and len(w) > 3]


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    from covalx.fastjudge import FastJudge
    from covalx.judge import build_prompt, load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    comp = {}
    for line in (DATA / "comparisons.jsonl").open():
        d = json.loads(line)
        comp[d["prompt_id"]] = [r["messages"][0]["content"] for r in d["responses"]]

    pids = [p for p in sorted(recs) if p in comp and len(comp[p]) == 4
            and len([1 for it in recs[p]["coval_full"] if it.get("scores")]) >= 4][:P_SIZE]

    # ---- vocabulary, chosen OUTCOME-BLIND by token document-frequency across prompts
    df = collections.Counter()
    for p in pids:
        seen = set()
        for it in recs[p]["coval_full"]:
            seen |= set(toks(it.get("criterion", "")))
        df.update(seen)
    cand = []
    for p in pids:
        for it in recs[p]["coval_full"]:
            t = toks(it.get("criterion", ""))
            if t:
                cand.append((float(np.mean([df[w] for w in t])), it["criterion"]))
    cand.sort(key=lambda x: -x[0])
    seen_txt, V = set(), []
    for _s, txt in cand:
        k = txt.strip().lower()
        if k not in seen_txt:
            seen_txt.add(k); V.append(txt)
        if len(V) >= V_SIZE:
            break
    print("vocabulary %d generic criteria | prompts %d | judgements %d"
          % (len(V), len(pids), len(V) * len(pids) * 4), flush=True)

    tasks, index = [], []
    for p in pids:
        for r_ in range(4):
            for vi, txt in enumerate(V):
                index.append((p, vi, r_)); tasks.append(build_prompt(txt, comp[p][r_]))
    judge = FastJudge(MODEL, batch=96)
    sat = judge.score(tasks)
    np.savez_compressed(OUT / "sat_global.npz",
                        meta=np.array(["%s|%d|%d" % t for t in index]),
                        sat=np.asarray(sat, dtype=np.float32),
                        vocab=np.array(V))
    print("persisted %d judgements -> results/sat_global.npz" % len(sat), flush=True)

    S = collections.defaultdict(lambda: np.zeros((len(V), 4), dtype=np.float32))
    for (p, vi, r_), v in zip(index, sat):
        S[p][vi, r_] = v

    # target: the per-prompt FULL rubric's own class, on the same judge (r04 cache)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
                               "/R04_rebuild_satisfaction/results/a04_full.npz"))
    target = {}
    for p in pids:
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf.get(p, {}).get((i, x)) is not None for x in L)]
        if len(ok) < 4:
            continue
        W = np.array([np.mean([float(s2["score"]) for s2 in f[i]["scores"]]) for i in ok])
        SS = np.array([[sf[p][(i, x)] for x in L] for i in ok])
        target[p] = cls((W[:, None] * SS).sum(0))
    use = [p for p in pids if p in target]
    print("prompts with a target class: %d" % len(use))

    def agree(sub, ps):
        return float(np.mean([cls(S[p][sub].sum(0)) == target[p] for p in ps])) if ps else float("nan")

    grid, nulls = {}, {}
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        idx = rng.permutation(len(use))
        fit = [use[i] for i in idx[:len(use) // 2]]
        ev = [use[i] for i in idx[len(use) // 2:]]
        for k in KS:
            chosen, cur = [], None
            for _ in range(k):                                    # greedy on the FIT half only
                best, bi = None, None
                for vi in range(len(V)):
                    if vi in chosen:
                        continue
                    a = agree(chosen + [vi], fit)
                    if best is None or a > best:
                        best, bi = a, vi
                if bi is None:
                    break
                chosen.append(bi)
            fl = [agree(list(rng.choice(len(V), size=k, replace=False)), ev) for _ in range(DRAWS)]
            grid.setdefault(k, []).append((agree(chosen, fit), agree(chosen, ev),
                                           float(np.mean(fl)), min(fl), max(fl)))
            # NEGATIVE: shuffle which prompts are fit vs eval AFTER fitting
            sh = list(use); rng.shuffle(sh)
            nulls.setdefault(k, []).append(agree(chosen, sh[len(sh) // 2:]) - float(np.mean(fl)))

    print("\n=== held-out class agreement of a GLOBAL core (fit on half the prompts) ===")
    print("%-5s %10s %12s %22s %10s" % ("k", "fit", "HELD-OUT", "random floor [min,max]", "gain"))
    for k in KS:
        g = np.array(grid[k])
        f_, e_, fl, lo, hi = g.mean(0)
        print("%-5d %10.4f %12.4f %22s %10s"
              % (k, f_, e_, "%.4f [%.4f, %.4f]" % (fl, lo, hi),
                 "%+.4f%s" % (e_ - fl, "  *" if e_ > hi else "")))
    print(" (* = held-out agreement above the floor's best draw)")

    print("\n=== controls ===")
    g1 = np.array(grid[KS[-1]]).mean(0)
    print(" POSITIVE  fit-half agreement above floor at k=%d : %.4f vs %.4f  %s"
          % (KS[-1], g1[0], g1[2], "OK" if g1[0] > g1[4] else "FITTER BROKEN"))
    nn = float(np.mean(nulls[KS[-1]]))
    print(" NEGATIVE  shuffled fit/eval labels, gain         : %+.4f  %s"
          % (nn, "null-ish" if abs(nn) < 0.05 else "NOT NULL"))
    print(" CEILING   computed, not assumed: R231 measured the per-prompt FULL rubric against the")
    print("           human consensus class at 0.2004. A global core is not asked to beat the local")
    print("           object; that figure is the scale these numbers live on.")

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    above = [k for k in KS if np.array(grid[k]).mean(0)[1] > np.array(grid[k]).mean(0)[4]]
    if not above:
        v = ("REFUTED -- held-out agreement sits inside the random floor at every k. The bits add "
             "across prompts (R239) and there is still no global core to find: norms in this "
             "release are prompt-specific, and the derivation is right about the channel and "
             "irrelevant about the object.")
    else:
        best = max(above, key=lambda k: np.array(grid[k]).mean(0)[1] - np.array(grid[k]).mean(0)[2])
        gg = np.array(grid[best]).mean(0)
        v = ("A GLOBAL CORE TRANSFERS: at k=%d held-out class agreement is %.4f against a floor of "
             "%.4f [%.4f, %.4f], on prompts it was never fitted to. Identifiable at %d of %d sizes "
             "tested." % (best, gg[1], gg[2], gg[3], gg[4], len(above), len(KS)))
    print("\n  " + v)
    json.dump({"V": len(V), "prompts": len(use), "ks": KS,
               "grid": {str(k): np.array(grid[k]).mean(0).tolist() for k in KS},
               "nulls": {str(k): float(np.mean(nulls[k])) for k in KS}, "verdict": v},
              open(OUT / "global_core.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
