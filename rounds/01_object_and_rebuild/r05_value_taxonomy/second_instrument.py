"""r05 second instrument -- does the compression penalty survive a different survival measure?

r05's docstring justifies its design like this:

    "The prior analysis established that CoVal-core preserves consensus items
     better than polarized ones (embedding similarity 0.736 vs 0.520). ...
     Survival is computed lexically (token-overlap), NOT by embedding, so it is
     a different instrument. Two independent instruments agreeing is evidence;
     one instrument repeated is not."

A construct review went looking for the 0.736/0.520 result. It exists in that one
docstring, entered in the commit that created the file, and is computed nowhere --
in this repository or its history (`git log --all -S"0.736"`). It was inherited
from the source package and cited as established without being checked.

So r05's own argument was standing on ONE instrument, in a paragraph explaining
that one instrument is not enough. This script supplies the second one that was
always supposed to be there.

Instrument A (r05 as shipped): Jaccard token overlap against the prompt's core.
Instrument B (here):           TF-IDF cosine against the same core.

These are genuinely different: Jaccard counts shared tokens as equal, TF-IDF
down-weights terms common across the corpus, so a criterion that "survives" only
by sharing the words *should*, *the*, *response* scores near zero under B and can
score well under A.

The threshold for B is chosen to match A's OVERALL survival rate, because an
absolute cutoff is not comparable between two differently-scaled similarities --
comparing them at different base rates would test the threshold, not the
instrument.

Verdict is the family ranking, not the magnitudes: r05's claim is that the
polarization penalty is present in EVERY family, not that it has a given size.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"


def _load_r05():
    spec = importlib.util.spec_from_file_location("r05", _HERE / "run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "a05_second_instrument.json")
    p.add_argument("--jaccard-threshold", type=float, default=0.5)
    a = p.parse_args()

    r05 = _load_r05()
    toks, families_of = r05.toks, r05.families_of

    # ---- pass 1: read everything, build the corpus IDF ----------------------
    prompts = []
    df = Counter()
    for line in open(a.data, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        items = rec.get("coval_full") or []
        core = [c["criterion"] for c in (rec.get("coval_core") or [])]
        if not items or not core:
            continue
        raters = {s["annotator_id"] for it in items for s in it.get("scores") or []}
        thr = max(2, (len(raters) + 1) // 2)
        rows = []
        for it in items:
            sc = [float(s["score"]) for s in it.get("scores") or []]
            if not sc:
                continue
            arr = np.array(sc)
            pos, neg = float((arr > 0).mean()), float((arr < 0).mean())
            t = toks(it["criterion"])
            df.update(set(t))
            rows.append({"t": t, "shared": len(arr) >= thr,
                         "polarized": bool(pos > 0 and neg > 0 and min(pos, neg) >= 0.25),
                         "families": families_of(it["criterion"])})
        ct = [toks(c) for c in core]
        for c in ct:
            df.update(set(c))
        if rows:
            prompts.append((rows, ct))
    N = sum(len(r) for r, _ in prompts) + sum(len(c) for _, c in prompts)
    idf = {w: math.log(N / (1 + n)) for w, n in df.items()}
    print(f"prompts {len(prompts):,}   criteria {sum(len(r) for r,_ in prompts):,}   "
          f"vocab {len(idf):,}")

    def vec(t):
        v = {w: idf.get(w, 0.0) for w in t}
        nrm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return v, nrm

    def cos(a_, b_):
        (va, na), (vb, nb) = a_, b_
        if len(va) > len(vb):
            va, vb = vb, va
        return sum(x * vb.get(w, 0.0) for w, x in va.items()) / (na * nb)

    # ---- pass 2: both instruments on every criterion ------------------------
    all_rows = []
    for rows, ct in prompts:
        cvs = [vec(c) for c in ct]
        for r in rows:
            jb = max((len(r["t"] & c) / max(len(r["t"] | c), 1) for c in ct), default=0.0)
            rv = vec(r["t"])
            cb = max((cos(rv, cv) for cv in cvs), default=0.0)
            all_rows.append({**r, "jac": jb, "cos": cb})

    jac_rate = float(np.mean([r["jac"] >= a.jaccard_threshold for r in all_rows]))
    cuts = np.array([r["cos"] for r in all_rows])
    cos_thr = float(np.quantile(cuts, 1.0 - jac_rate))
    print(f"instrument A (jaccard >= {a.jaccard_threshold}) survival rate = {jac_rate:.4f}")
    print(f"instrument B (tf-idf cosine) threshold matched to it = {cos_thr:.4f}\n")
    for r in all_rows:
        r["survA"] = r["jac"] >= a.jaccard_threshold
        r["survB"] = r["cos"] >= cos_thr

    fams = sorted({f for r in all_rows for f in r["families"]})
    pen = {}
    print(f"{'family':24s} {'penalty A':>10} {'penalty B':>10}   {'n pol/non':>12}")
    for fam in fams:
        sub = [r for r in all_rows if fam in r["families"] and r["shared"]]
        pol = [r for r in sub if r["polarized"]]
        non = [r for r in sub if not r["polarized"]]
        if len(pol) < 20 or len(non) < 20:
            continue
        pa = float(np.mean([r["survA"] for r in pol]) - np.mean([r["survA"] for r in non]))
        pb = float(np.mean([r["survB"] for r in pol]) - np.mean([r["survB"] for r in non]))
        pen[fam] = {"penalty_jaccard": pa, "penalty_tfidf": pb,
                    "n_pol": len(pol), "n_non": len(non)}
        print(f"{fam:24s} {pa:>+10.3f} {pb:>+10.3f}   {f'{len(pol)}/{len(non)}':>12}")

    A = np.array([v["penalty_jaccard"] for v in pen.values()])
    B = np.array([v["penalty_tfidf"] for v in pen.values()])
    from scipy.stats import spearmanr
    rho, pv = spearmanr(A, B)
    both_neg = int(((A < 0) & (B < 0)).sum())
    print(f"\n  families with a NEGATIVE penalty under BOTH instruments: {both_neg}/{len(A)}")
    print(f"  family-ranking agreement (Spearman): rho={rho:+.3f}  p={pv:.2g}")
    print(f"  penalty range   A {A.min():+.3f}..{A.max():+.3f}   B {B.min():+.3f}..{B.max():+.3f}")

    verdict = ("CONFIRMED under a second instrument: the polarization penalty is negative in "
               "every family under both, and the family ordering agrees"
               if both_neg == len(A) and rho > 0.5 else
               "INSTRUMENT-DEPENDENT: the penalty does not hold in every family under both "
               "measures, so r05's claim is a property of token overlap")
    print(f"\n  -> {verdict}")
    print("\n  NOTE: both instruments are LEXICAL. A shared blindness to true paraphrase "
          "(different words, same meaning) is NOT ruled out by their agreement, and the "
          "embedding result that was supposed to cover that gap could not be located.")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"jaccard_survival_rate": jac_rate, "tfidf_threshold_matched": cos_thr,
         "per_family": pen, "spearman_rho": float(rho), "spearman_p": float(pv),
         "families_negative_under_both": both_neg, "families": len(A),
         "verdict": verdict,
         "note": "supplies the second instrument r05's docstring assumed. The cited "
                 "embedding result (0.736 vs 0.520) is computed nowhere in this "
                 "repository or its history and remains UNVERIFIED. Both instruments "
                 "here are lexical, so a shared blindness to paraphrase is not excluded."},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
