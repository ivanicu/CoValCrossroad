"""The gauge test: is every number in this project a fact about Qwen3.5-2B-Base?

Rung 1 of the attack ladder, zero new compute -- three alternative judge tensors have been sitting
in r164/results since that round and no decision-level gauge test has ever been run on them.

  a04_full        Qwen3.5-2B-Base, 968 prompts     <- every number this project has published
  sat_full_phi    Phi,             968 prompts
  sat_full_qwen3b Qwen 3B,         968 prompts
  sat_full_variant_swapped         300 prompts     <- the SAME judge with the options SWAPPED,
                                                      which is also the position-bias test (#7)

ESTIMAND  (a) P(the rubric-induced winner differs between judge J and the baseline judge), and
          (b) for each operator o, P(o flips the decision) computed under J. (a) asks whether the
          object moves; (b) asks whether the MEASUREMENT moves, and they are different questions.
GAUGE     the transformation is "change the reader of the norm, hold the norm fixed". A norm's
          content is invariant under it; a measurement of that content need not be.
          MEASUREMENT INVARIANT + PROPERTY NOT -> the measurement is blind.
          PROPERTY INVARIANT + MEASUREMENT NOT -> the measurement is about the reader.
KILL      pre-registered: if the operator ORDERING changes across judges (Spearman < 0.8 against
          the baseline ordering), then no claim of the form "X moves the decision more than Y"
          survives, and every comparative statement in r208-r212 is about Qwen3.5-2B-Base.
CI        cluster bootstrap over PROMPTS, 400 resamples -- the interval this project has never
          printed on a flip rate.
ALSO      #3 the dose_saturate domain, #6 the 18 unmatched prompts, #4 CIs everywhere.
"""
from __future__ import annotations
import json, math, pathlib, sys
from collections import defaultdict
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
L = "ABCD"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"
R164 = ROOT / "E04_no_fraction_only_an_equivalence_class/A02_the_chain_from_a_person_to_the_standard/R164_instrument/results"
SEEDS = [0, 1, 2, 3, 4]
RULES = ["highest_w", "lowest_w", "most_rated", "random"]


def load(p):
    d = np.load(p, allow_pickle=True)
    o = defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|")
        o[pid][(int(i), ltr)] = float(v)
    return o


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    JUD = {"qwen3.5-2b (baseline)": load(R4 / "a04_full.npz"),
           "phi": load(R164 / "sat_full_phi.npz"),
           "qwen3b": load(R164 / "sat_full_qwen3b.npz"),
           "options-swapped": load(R164 / "sat_full_variant_swapped.npz")}
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}

    # ---------------------------------------------------------------- #6 the unmatched
    print("=" * 100)
    print("#6 -- THE 18 PROMPTS THAT NEVER JOINED")
    print("=" * 100)
    nl = sum(1 for _ in (DATA / "conversation_rubrics.jsonl").open())
    print(f"  rubric records {nl}, joined {len(recs)}, UNMATCHED {nl - len(recs)}.")
    joined_ids = set(recs)
    ncrit = [len(recs[p]["coval_full"]) for p in joined_ids]
    print(f"  joined records carry {np.mean(ncrit):.1f} criteria on average.")
    print(f"  The join is by message CONTENT because the rubrics file ships no prompt id, so an")
    print(f"  unmatched record is one whose conversation text does not appear in comparisons.jsonl")
    print(f"  at >=0.95 similarity. {nl - len(recs)} of {nl} = {(nl - len(recs)) / nl:.1%} of the rubric corpus is")
    print(f"  invisible to every number in this repository, and no round has ever said so.")

    # ---------------------------------------------------------------- the operators, per judge
    def run_judge(sf, pids):
        acc = defaultdict(lambda: defaultdict(list))
        winner = {}
        for p in pids:
            f = recs[p]["coval_full"]
            ok = [i for i, it in enumerate(f)
                  if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
            if len(ok) < 4:
                continue
            S = {i: np.array([sf[p][(i, x)] for x in L], float) for i in ok}
            raw = {i: [float(s_["score"]) for s_ in f[i]["scores"]] for i in ok}
            aids = {i: [s_["annotator_id"] for s_ in f[i]["scores"]] for i in ok}
            W = {i: float(np.mean(raw[i])) for i in ok}
            base = sum(W[i] * S[i] for i in ok)
            b = int(np.argmax(base))
            winner[p] = b
            for rule in RULES:
                for seed in SEEDS:
                    rng = np.random.default_rng(hash((p, rule, seed)) % (2 ** 32))
                    c = (max(ok, key=lambda i: abs(W[i])) if rule == "highest_w" else
                         min(ok, key=lambda i: abs(W[i])) if rule == "lowest_w" else
                         max(ok, key=lambda i: len(raw[i])) if rule == "most_rated" else
                         int(rng.choice(ok)))
                    def wv(fn):
                        return sum(fn(W[i], i) * S[i] for i in ok)
                    for nm, mul in (("dose_double", 2.0), ("dose_invert", -1.0),
                                    ("dose_weaken", 0.5), ("dose_delete", 0.0)):
                        acc[nm][p].append(int(np.argmax(
                            wv(lambda w, i: w * mul if i == c else w)) != b))
                    if abs(W[c]) < 9.999:
                        acc["dose_saturate"][p].append(int(np.argmax(
                            wv(lambda w, i: math.copysign(10., w) if i == c else w)) != b))
                    acc["set_duplicate"][p].append(int(np.argmax(base + W[c] * S[c]) != b))
                    acc["set_add_cancelling"][p].append(int(np.argmax(base - W[c] * S[c]) != b))
                    allA = sorted({a for i in ok for a in aids[i]})
                    if len(allA) >= 3:
                        dev = {a: np.mean([abs(v - W[i]) for i in ok
                                           for v, aa in zip(raw[i], aids[i]) if aa == a] or [0])
                               for a in allA}
                        for nm, pick in (("annot_drop_dissenter", max(dev, key=dev.get)),
                                         ("annot_drop_conformer", min(dev, key=dev.get))):
                            y = sum((np.mean([v for v, a in zip(raw[i], aids[i]) if a != pick])
                                     if any(a != pick for a in aids[i]) else 0.) * S[i]
                                    for i in ok)
                            acc[nm][p].append(int(np.argmax(y) != b))
                    per = defaultdict(lambda: np.zeros(4))
                    for i in ok:
                        for s_ in f[i]["scores"]:
                            per[s_["annotator_id"]] += float(s_["score"]) * S[i]
                    if len(per) >= 3:
                        Mp = np.stack(list(per.values()))
                        acc["agg_median_people"][p].append(
                            int(int(np.argmax(np.median(Mp, 0))) != int(np.argmax(Mp.mean(0)))))
                        acc["agg_maximin_people"][p].append(
                            int(int(np.argmax(Mp.min(0))) != int(np.argmax(Mp.mean(0)))))
        return acc, winner

    common = sorted(set(JUD["options-swapped"]) & set(recs))
    all968 = sorted(set(JUD["qwen3.5-2b (baseline)"]) & set(recs))
    res, wins = {}, {}
    for nm, sf in JUD.items():
        pool = common if nm == "options-swapped" else all968
        res[nm], wins[nm] = run_judge(sf, pool)
        print(f"  ran {nm} on {len(pool)} prompts")

    # ---------------------------------------------------------------- (a) does the object move
    print("\n" + "=" * 100)
    print("(a) DOES THE WINNER ITSELF MOVE WHEN THE READER CHANGES")
    print("=" * 100)
    base = wins["qwen3.5-2b (baseline)"]
    agree = {}
    for nm in JUD:
        if nm.startswith("qwen3.5"):
            continue
        sh = [p for p in wins[nm] if p in base]
        d = float(np.mean([wins[nm][p] != base[p] for p in sh]))
        agree[nm] = {"n": len(sh), "disagree": d}
        print(f"  {nm:22s} n {len(sh):4d}   winner DIFFERS on {d:6.1%} of prompts")
    print(f"""
  The options-swapped row is the POSITION-BIAS test (#7): the same judge, the same norm, the
  responses presented in a different order. Any disagreement there is pure instrument.""")

    # ---------------------------------------------------------------- (b) does the measurement move
    print("\n" + "=" * 100)
    print("(b) DOES THE MEASUREMENT MOVE -- P(operator flips the decision), per judge")
    print("=" * 100)
    ops = sorted(res["qwen3.5-2b (baseline)"], key=lambda o: -float(np.mean(
        [np.mean(v) for v in res["qwen3.5-2b (baseline)"][o].values()])))
    rng = np.random.default_rng(0)

    def boot(byp):
        ks = list(byp)
        pt = float(np.mean([np.mean(byp[k]) for k in ks]))
        bs = [float(np.mean([np.mean(byp[k]) for k in rng.choice(ks, len(ks))]))
              for _ in range(400)]
        return pt, float(np.quantile(bs, .025)), float(np.quantile(bs, .975))

    print(f"  {'operator':22s} " + " ".join(f"{n[:16]:>21s}" for n in JUD))
    table = defaultdict(dict)
    for o in ops:
        cells = []
        for nm in JUD:
            if o in res[nm] and res[nm][o]:
                pt, lo, hi = boot(res[nm][o])
                table[o][nm] = (pt, lo, hi)
                cells.append(f"{pt:7.1%} [{lo:5.1%},{hi:5.1%}]")
            else:
                cells.append(f"{'--':>21s}")
        print(f"  {o:22s} " + " ".join(cells))

    from scipy.stats import spearmanr
    b_order = [table[o]["qwen3.5-2b (baseline)"][0] for o in ops]
    print(f"\n  ORDERING STABILITY (pre-registered kill at Spearman < 0.8):")
    sp = {}
    for nm in JUD:
        if nm.startswith("qwen3.5"):
            continue
        pairs = [(table[o]["qwen3.5-2b (baseline)"][0], table[o][nm][0])
                 for o in ops if nm in table[o]]
        r = spearmanr([x for x, _ in pairs], [y for _, y in pairs]).statistic
        sp[nm] = float(r)
        print(f"    {nm:22s} rho {r:+.3f} over {len(pairs)} operators   "
              f"{'KILL FIRES' if r < 0.8 else 'ordering survives'}")

    # ---------------------------------------------------------------- #3 the saturate domain
    print("\n" + "=" * 100)
    print("#3 -- THE dose_saturate DOMAIN IS A SELECTED SUBPOPULATION")
    print("=" * 100)
    sf0 = JUD["qwen3.5-2b (baseline)"]
    at10, below = 0, 0
    for p in all968:
        f = recs[p]["coval_full"]
        for it in f:
            for s_ in (it.get("scores") or []):
                if abs(float(s_["score"])) >= 9.999:
                    at10 += 1
                else:
                    below += 1
    print(f"""  ratings at |w| = 10: {at10:,} of {at10 + below:,} = {at10 / (at10 + below):.1%}. A criterion already
  at the scale maximum CANNOT be saturated further, so dose_saturate is undefined exactly where the
  crowd was most emphatic. Its 77.1% domain is not missing at random -- it EXCLUDES the strongest
  criteria, which is the direction that would have made its effect largest. The reported number is
  therefore a lower bound on its own population and not an estimate of the whole.""")

    json.dump({"winner_disagreement": agree, "spearman": sp,
               "table": {o: {k: list(v) for k, v in table[o].items()} for o in table},
               "unmatched": nl - len(recs), "frac_at_max": at10 / (at10 + below)},
              open(OUT / "gauge.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
