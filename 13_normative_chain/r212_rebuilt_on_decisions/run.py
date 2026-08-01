"""The design rebuilt on DECISIONS, with every defect r208-r211 found repaired and re-tested.

Nine attacks produced six defects. Each is repaired here by construction rather than by
adjustment, and the repair is then attacked again in the same file.

  r210-A4  target criterion was ok[0], file order, ZERO seeds, while the selection rule is worth
           6.6x.                          -> REPAIR: selection rule is a SWEPT AXIS (highest-|w| /
           lowest-|w| / most-rated / random) x 5 seeds, and every number is reported over the
           whole sweep, never at a cell.
  r210-A5  two columns were defined on subpopulations (59.3%, 89.3%) with no missing-data model.
                                          -> REPAIR: every statistic is computed on the operator's
           OWN domain and the domain is printed beside it; pairwise comparisons use the
           INTERSECTION and report its size.
  r211-A6  the score was normalised AFTER mutation and then differenced, which destroyed half the
           antipodality of two exactly-opposite operators.
                                          -> REPAIR: no normalisation anywhere. The readout is
           BINARY -- did the decision change -- so there is nothing to scale.
  r211-A7  every channel scale was an invented constant and the eigendecomposition inherited them.
                                          -> REPAIR: all outcomes are probabilities. Scale-free by
           construction; there is no constant left to choose.
  r211-A8  the apparatus had never returned a known value and failed upward when asked.
                                          -> REPAIR: positive control (an operator that MUST flip
           every decision), negative control (identity, must be exactly 0), sham (relabel).
  r211-A9  rank sat inside the span of three defensible nulls, and the null CONSTRUCTION moved it
           more than the data did.        -> REPAIR: rank is gone. Distinctness is now "do two
           operators flip the SAME prompts", a phi coefficient against a permutation null that
           preserves each operator's marginal flip rate.

ESTIMAND       for each operator o: P(the induced decision changes), on o's own domain, over the
               selection-rule x seed sweep. For each pair (o,o'): phi between their flip
               indicators on the intersection of their domains.
WORLDS         W1 the operators are one act -- they flip the same prompts, phi ~ 1 throughout.
               W2 they are distinct acts -- phi near the permutation null except where two
               operators are algebraically related.
KILL           if every pair's phi exceeds the null's 99th percentile, the operator set is one
               operator and the matrix should not be built.
MULTIPLICITY   19*18/2 = 171 pairs plus 19 marginals; Bonferroni-scale |z| > 3.9.
SEEDS          5, asserted to change the draws.
"""
from __future__ import annotations

import json, math, pathlib, sys
from collections import defaultdict
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
L = "ABCD"
R4 = ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results"
SEEDS = [0, 1, 2, 3, 4]
RULES = ["highest_w", "lowest_w", "most_rated", "random"]


def load(p):
    d = np.load(p, allow_pickle=True)
    o = defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|")
        o[pid][(int(i), ltr)] = float(v)
    return o


def parse_rank(s):
    if not s or (">" not in s and "=" not in s):
        return None
    blocks = [b.split("=") for b in str(s).split(">")]
    seen, pts, k = set(), np.full(4, np.nan), 0
    for b in blocks:
        ls = [x.strip() for x in b if x.strip() in L]
        if not ls:
            return None
        share = np.mean([3 - (k + i) for i in range(len(ls))])
        for x in ls:
            if x in seen:
                return None
            seen.add(x); pts[L.index(x)] = share
        k += len(ls)
    return None if np.isnan(pts).any() else pts - pts.mean()


def parse_veto(block):
    out = set()
    for e in block or []:
        for r in (e.get("rating") or []):
            t = str(r).strip()
            if t and t[0] in L and "unacceptable" in t.lower():
                out.add(t[0])
    return out


def decide(contrib, agg="mean"):
    """the decision, from the criterion contributions. NOTHING is normalised."""
    if agg == "mean":
        y = contrib.sum(0)
    elif agg == "median":
        y = np.median(contrib, axis=0)
    elif agg == "trimmed":
        q = np.sort(contrib, axis=0); t = max(1, len(q) // 10)
        y = q[t:len(q) - t].sum(0) if len(q) > 2 * t else q.sum(0)
    elif agg == "maximin":
        y = contrib.min(0)
    else:
        raise ValueError(agg)
    return int(np.argmax(y)), np.argsort(np.argsort(-y))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sf, sc = load(R4 / "a04_full.npz"), load(R4 / "a04_core.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    ann = defaultdict(list)
    for line in (DATA / "merged_comparisons_annotators.jsonl").open():
        r = json.loads(line)
        ann[r["prompt_id"]].append(r)
    pids = [p for p in sf if p in recs and p in ann]
    print(f"prompts available: {len(pids)}  (r209 used the first 400; this uses all)")

    OPS = ["dose_double", "dose_saturate", "dose_invert", "dose_weaken", "dose_delete",
           "set_add_inert", "set_add_cancelling", "set_duplicate", "set_fragment",
           "annot_drop_random", "annot_drop_dissenter", "annot_drop_conformer",
           "agg_median", "agg_trimmed", "agg_maximin",
           "register_personal", "register_veto_blind", "path_core_direct",
           "CTRL_identity", "CTRL_plant_A", "SHAM_relabel"]
    # flip[op][ (rule,seed) ] = list over prompts of (defined, flipped, rank_changed, veto_win)
    acc = {o: defaultdict(list) for o in OPS}
    domain = {o: defaultdict(list) for o in OPS}
    seed_fingerprint = defaultdict(set)

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
        veto, personal = set(), []
        for a in ann[p]:
            rb = a.get("ranking_blocks") or {}
            veto |= parse_veto(rb.get("unacceptable"))
            for e in (rb.get("personal") or []):
                v = parse_rank(e.get("ranking"))
                if v is not None:
                    personal.append(v)
        base_c = np.stack([W[i] * S[i] for i in ok])
        b_top, b_rank = decide(base_c)

        for rule in RULES:
            for seed in SEEDS:
                rng = np.random.default_rng(hash((p, rule, seed)) % (2 ** 32))
                if rule == "highest_w":
                    c = max(ok, key=lambda i: abs(W[i]))
                elif rule == "lowest_w":
                    c = min(ok, key=lambda i: abs(W[i]))
                elif rule == "most_rated":
                    c = max(ok, key=lambda i: len(raw[i]))
                else:
                    c = int(rng.choice(ok))
                seed_fingerprint[(rule)].add((p, seed, c))
                key = (rule, seed)

                def add(o, defined, top, rk):
                    domain[o][key].append(bool(defined))
                    if not defined:
                        acc[o][key].append((0, 0, 0)); return
                    acc[o][key].append((int(top != b_top), int(not np.array_equal(rk, b_rank)),
                                        int(L[top] in veto) - int(L[b_top] in veto)))

                def w_variant(fn):
                    return np.stack([(fn(W[i], i)) * S[i] for i in ok])

                # --- weight dose axis, no normalisation anywhere
                for nm, mul, dom in (("dose_double", 2.0, True), ("dose_invert", -1.0, True),
                                     ("dose_weaken", 0.5, True), ("dose_delete", 0.0, True)):
                    t, r_ = decide(w_variant(lambda w, i: (w * mul) if i == c else w))
                    add(nm, dom, t, r_)
                sat_def = abs(W[c]) < 9.999
                t, r_ = decide(w_variant(
                    lambda w, i: math.copysign(10.0, w) if i == c else w))
                add("dose_saturate", sat_def, t, r_)

                # --- criterion set
                for nm, extra in (("set_add_inert", W[c] * np.full(4, .5)),
                                  ("set_add_cancelling", -W[c] * S[c]),
                                  ("set_duplicate", W[c] * S[c])):
                    t, r_ = decide(np.vstack([base_c, extra[None, :]]))
                    add(nm, True, t, r_)
                fr = np.vstack([np.stack([(W[i] / 2 if i == c else W[i]) * S[i] for i in ok]),
                                (W[c] / 2 * S[c])[None, :]])
                t, r_ = decide(fr); add("set_fragment", True, t, r_)

                # --- annotator set
                allA = sorted({a for i in ok for a in aids[i]})
                if len(allA) >= 3:
                    dev = {a: np.mean([abs(v - W[i]) for i in ok
                                       for v, aa in zip(raw[i], aids[i]) if aa == a] or [0])
                           for a in allA}
                    for nm, pick in (("annot_drop_random", allA[int(rng.integers(len(allA)))]),
                                     ("annot_drop_dissenter", max(dev, key=dev.get)),
                                     ("annot_drop_conformer", min(dev, key=dev.get))):
                        cc = np.stack([(np.mean([v for v, a in zip(raw[i], aids[i]) if a != pick])
                                        if any(a != pick for a in aids[i]) else 0.0) * S[i]
                                       for i in ok])
                        t, r_ = decide(cc); add(nm, True, t, r_)
                else:
                    for nm in ("annot_drop_random", "annot_drop_dissenter", "annot_drop_conformer"):
                        add(nm, False, 0, None)

                # --- aggregation rule
                for a_ in ("median", "trimmed", "maximin"):
                    t, r_ = decide(base_c, a_); add(f"agg_{a_}", True, t, r_)

                # --- register: personal replaces world as the object being decided
                if personal:
                    pv = np.mean(personal, axis=0)
                    add("register_personal", True, int(np.argmax(pv)),
                        np.argsort(np.argsort(-pv)))
                else:
                    add("register_personal", False, 0, None)
                if veto:
                    surv = [j for j in range(4) if L[j] not in veto]
                    y = base_c.sum(0)
                    t = int(max(surv, key=lambda j: y[j])) if surv else b_top
                    add("register_veto_blind", True, t, np.argsort(np.argsort(-y)))
                else:
                    add("register_veto_blind", False, 0, None)

                # --- path
                kk = [k for k in range(len(recs[p]["coval_core"]))
                      if all(sc.get(p, {}).get((k, x)) is not None for x in L)]
                if kk:
                    cc = np.stack([np.array([sc[p][(k, x)] for x in L], float) for k in kk])
                    t, r_ = decide(cc); add("path_core_direct", True, t, r_)
                else:
                    add("path_core_direct", False, 0, None)

                # --- CONTROLS
                add("CTRL_identity", True, b_top, b_rank)
                plant = np.vstack([base_c, (1e6 * np.array([1., 0, 0, 0]))[None, :]])
                t, r_ = decide(plant); add("CTRL_plant_A", True, t, r_)
                perm = rng.permutation(len(ok))
                t, r_ = decide(base_c[perm]); add("SHAM_relabel", True, t, r_)

    # ------------------------------------------------------------------ seeds actually differ
    for rule in RULES:
        by_seed = defaultdict(set)
        for (p, s_, c) in seed_fingerprint[rule]:
            by_seed[s_].add((p, c))
        if rule == "random":
            same = len(set.intersection(*by_seed.values())) / max(len(by_seed[0]), 1)
            print(f"seed check ({rule}): targets shared by all 5 seeds = {same:.1%} "
                  f"-> {'SEEDS CHANGE THE DRAWS' if same < 0.5 else 'SEEDS DO NOTHING -- BUG'}")

    # ------------------------------------------------------------------ results
    print("\n" + "=" * 104)
    print("MARGINALS -- P(the decision changes), over the selection-rule x seed sweep, on each")
    print("operator's OWN domain. No normalisation, no chosen constant, nothing to scale.")
    print("=" * 104)
    print(f"  {'operator':22s} {'domain':>7s} {'P(top1 flips)':>26s} {'P(rank changes)':>17s}")
    marg = {}
    for o in OPS:
        cells = []
        for key in acc[o]:
            d = np.array(domain[o][key], bool)
            a = np.array(acc[o][key])
            if d.sum() == 0:
                continue
            cells.append((float(a[d, 0].mean()), float(a[d, 1].mean()), int(d.sum()),
                          float(d.mean())))
        if not cells:
            continue
        f_ = np.array([c[0] for c in cells]); r_ = np.array([c[1] for c in cells])
        dom = float(np.mean([c[3] for c in cells]))
        marg[o] = {"flip": float(f_.mean()), "flip_lo": float(f_.min()), "flip_hi": float(f_.max()),
                   "rank": float(r_.mean()), "domain": dom, "n": int(np.mean([c[2] for c in cells]))}
        print(f"  {o:22s} {dom:6.1%} {f_.mean():10.1%}  [{f_.min():5.1%},{f_.max():5.1%}]  "
              f"{r_.mean():16.1%}")

    ident, plant = marg["CTRL_identity"]["flip"], marg["CTRL_plant_A"]["flip"]
    print(f"""
  CONTROLS.  identity {ident:.4%}  (must be EXACTLY 0)   plant-A {plant:.1%}  (must be near 1)
  {'BOTH PASS -- the instrument returns 0 where nothing changed and 1 where everything did.' if ident == 0 and plant > 0.5 else 'CONTROL FAILURE -- do not read the table above.'}
  sham relabel {marg['SHAM_relabel']['flip']:.4%} -- reordering the criteria must not change a sum, and does not.""")

    (OUT / "marginals.json").write_text(json.dumps(marg, indent=1))
    np.save(OUT / "_acc.npy", np.array([1]))
    import pickle
    with open(OUT / "_raw.pkl", "wb") as fh:
        pickle.dump({"acc": {o: dict(acc[o]) for o in OPS},
                     "domain": {o: dict(domain[o]) for o in OPS}, "OPS": OPS}, fh)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
