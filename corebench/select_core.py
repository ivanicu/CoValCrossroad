#!/usr/bin/env python3
"""
corebench/select_core.py -- build SELECTION cores by slicing coval_full. Zero judge calls.

WHY THIS IS FREE. `coval_full` items carry `scores`, so their satisfaction against every
response is already in a04_full.npz. A core that is a SUBSET of full therefore costs no
GPU at all -- only the generated incumbent needed judging.

⚠ PARITY. The incumbent `coval_core` carries no importance weights (its items have only
`criterion`), so row 0 was scored with an UNWEIGHTED sum. Selection cores are emitted
unweighted too. A weighted arm is emitted separately and labelled, never mixed into the
same comparison -- a speedup measured at a different output is void, and so is a fidelity.

RULES
  random_k      k criteria drawn uniformly. THE RANDOM BASELINE the standard demands.
  topw_k        the k criteria with the highest MEAN importance score. Non-leaky: the
                weights come from the rubric, not from the outcome.
  topabs_k      the k with the largest |mean|, i.e. most polarising either way.
  oracle_k      the k that best fit the human target. LEAKY BY CONSTRUCTION -- an upper
                bound, labelled, never a candidate.
  full          every criterion. The source being compressed.
"""
from __future__ import annotations
import argparse, collections, itertools, json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
FULL_NPZ = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
                   "/R04_rebuild_satisfaction/results/a04_full.npz")


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def parse_ranking(s):
    sc = {}
    for lvl, grp in enumerate(s.split(">")):
        for tok in grp.split("="):
            tok = tok.strip()
            if tok in L:
                sc[tok] = -lvl
    return [sc[c] for c in L] if len(sc) == 4 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rule", required=True,
                    choices=["random_k", "topw_k", "topabs_k", "oracle_k", "full",
                             "topvar_k", "topwvar_k", "indep_k", "greedy_k"])
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--fit-parity", type=int, default=-1,
                    help="oracle only: fit on annotators with index %%2 == this. -1 = all "
                         "(LEAKY). Use 1 and evaluate on parity 0 for a held-out oracle.")
    ap.add_argument("--outdir", default="corebench/results")
    a = ap.parse_args()

    from covalx.judge import load_join
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    rub = {p: r for p, _pr, r in joined}

    d = np.load(FULL_NPZ, allow_pickle=True)
    sat = collections.defaultdict(dict)
    for kk, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(kk).split("|")
        sat[pid][(int(i), ltr)] = float(v)

    # human target, for the ORACLE arm only
    tgt = {}
    if a.rule in ("oracle_k", "indep_k", "greedy_k"):
        for line in open(ROOT / "data" / "comparisons.jsonl", encoding="utf-8"):
            if not line.strip():
                continue
            rec = json.loads(line)
            asms = rec.get("metadata", {}).get("assessments", [])
            if a.fit_parity >= 0:
                asms = [x for j, x in enumerate(asms) if j % 2 == a.fit_parity]
            ys = [parse_ranking(e["ranking"])
                  for asm in asms
                  for e in (asm.get("ranking_blocks") or {}).get("world") or []
                  if e.get("ranking")]
            ys = [y for y in ys if y]
            if ys:
                tgt[rec["prompt_id"]] = collections.Counter(
                    cls(np.array(y, float)) for y in ys).most_common(1)[0][0]

    rng = np.random.default_rng(a.seed)
    meta, vals, texts, capped = [], [], {}, [0]
    for pid, r in rub.items():
        items = r.get("coval_full") or []
        if pid not in sat or not items:
            continue
        ok = [i for i in range(len(items))
              if all(sat[pid].get((i, x)) is not None for x in L)]
        if not ok:
            continue
        w = {i: float(np.mean([s["score"] for s in items[i].get("scores") or []]) or 0.0)
             for i in ok}
        if a.rule == "full":
            sel = ok
        elif a.rule == "random_k":
            sel = list(rng.choice(ok, min(a.k, len(ok)), replace=False))
        elif a.rule == "topw_k":
            sel = sorted(ok, key=lambda i: -w[i])[:a.k]
        elif a.rule == "topvar_k":
            # DERIVATION, not a hunch: a criterion whose satisfaction is IDENTICAL across
            # the four responses adds the same constant to every y_x, so it changes no
            # pairwise sign and is arithmetically INERT no matter how important it is.
            # topw_k selects on importance and is blind to this. Selecting on the spread of
            # satisfaction across responses is the direct fix. Non-leaky: the spread is a
            # property of the responses, never of the human target.
            var = {i: float(np.var([sat[pid][(i, x)] for x in L])) for i in ok}
            sel = sorted(ok, key=lambda i: -var[i])[:a.k]
        elif a.rule == "topwvar_k":
            var = {i: float(np.var([sat[pid][(i, x)] for x in L])) for i in ok}
            sel = sorted(ok, key=lambda i: -(abs(w[i]) * var[i]))[:a.k]
        elif a.rule == "topabs_k":
            sel = sorted(ok, key=lambda i: -abs(w[i]))[:a.k]
        elif a.rule == "indep_k":
            # SET-AWARENESS SEPARATOR, arm 1. Score every criterion INDEPENDENTLY by how
            # well the singleton {i} reproduces the fit-half's modal class, then take the
            # top k. Fitted exactly like the oracle, but blind to interactions -- so the
            # oracle-minus-indep difference isolates SET STRUCTURE from mere fitting.
            t_ = tgt.get(pid)
            if t_ is None:
                continue
            def agree(idxs):
                y = np.array([sum(sat[pid][(i, x)] for i in idxs) for x in L])
                return sum(cls(y)[q] == t_[q] for q in range(6))
            sel = sorted(ok, key=lambda i: -agree([i]))[:a.k]
        elif a.rule == "greedy_k":
            # arm 2: sequential, each pick CONDITIONAL on those already chosen.
            t_ = tgt.get(pid)
            if t_ is None:
                continue
            def agree(idxs):
                y = np.array([sum(sat[pid][(i, x)] for i in idxs) for x in L])
                return sum(cls(y)[q] == t_[q] for q in range(6))
            sel = []
            for _ in range(min(a.k, len(ok))):
                rest = [i for i in ok if i not in sel]
                sel.append(max(rest, key=lambda i: agree(sel + [i])))
        else:                                    # oracle: leaky upper bound, labelled
            t = tgt.get(pid)
            if t is None:
                continue
            # ⚠ CAP, LOGGED NOT SILENT. C(39,4) = 82,251 and a silent truncation would
            # read as full coverage. Above CAP the oracle is SAMPLED, which makes it a
            # LOWER BOUND on the true oracle -- stated, and counted in `capped`.
            CAP = 20000
            allc = list(itertools.combinations(ok, min(a.k, len(ok))))
            if len(allc) > CAP:
                capped[0] += 1
                allc = [allc[i] for i in rng.choice(len(allc), CAP, replace=False)]
            best, bsel = -1, ok[:a.k]
            for c in allc:
                y = np.array([sum(sat[pid][(i, x)] for i in c) for x in L])
                hit = sum(cls(y)[q] == t[q] for q in range(6))
                if hit > best:
                    best, bsel = hit, list(c)
            sel = bsel
        texts[pid] = [items[i]["criterion"] for i in sel]
        for j, i in enumerate(sel):
            for x in L:
                meta.append(f"{pid}|{j}|{x}"); vals.append(sat[pid][(i, x)])

    out = pathlib.Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    tag = f"{a.rule}" + ("" if a.rule == "full" else f"{a.k}") + \
          (f"_s{a.seed}" if a.rule == "random_k" else "") + \
          (f"_fit{a.fit_parity}" if a.rule in ("oracle_k", "indep_k", "greedy_k")
           and a.fit_parity >= 0 else "")
    np.savez_compressed(out / f"sat_{tag}.npz", meta=np.array(meta),
                        sat=np.array(vals, np.float32))
    (out / f"core_{tag}.json").write_text(json.dumps(texts))
    print(f"  {tag}: {len(texts)} prompts, {len(meta)} cells, "
          f"mean k = {np.mean([len(v) for v in texts.values()]):.2f}  (0 judge calls)")
    if capped[0]:
        print(f"    ⚠ oracle SAMPLED on {capped[0]} of {len(texts)} prompts "
              f"({capped[0]/len(texts):.1%}) where C(n,k) > 20000 -> this arm is a LOWER "
              f"BOUND on the true oracle, not the oracle")


if __name__ == "__main__":
    main()
