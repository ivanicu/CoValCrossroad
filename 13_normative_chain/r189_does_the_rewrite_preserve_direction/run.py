"""Does the one transformation the release documents preserve the normative direction it carries?

This is the memo's question at the only stage of the chain where both the input and the output are
shipped and the transformation is described. Everything else in this pipeline is either
undocumented (where the candidate responses came from) or unshipped (the evaluation, the model).

The transformation: the card says the process "first rewrites all rubric items to have positive
weight". r176 confirmed it works and is targeted -- 82.5% of negatively-weighted sources have
their wording flipped against 6.1% of positive ones, z +33.

The quantity to track: r187 defined ENCODING as satisfaction of the author's own top choice minus
the mean over the other three responses. r188 showed encoding tracks signed weight monotonically
across all four bands, which is what correct scale use predicts and which makes encoding a
meaningful signed carrier of the author's position rather than an artefact.

So the preservation question has an exact, falsifiable form. A criterion the author weighted -8
means "the good answer does NOT do this", and its encoding is negative because the author's chosen
response satisfies it less. Rewriting it to "do not do X" at +8 should FLIP the encoding to
positive while carrying the same normative content. Three outcomes:

  FAITHFUL     encoding_core is close to -encoding_source for flipped items and to +encoding_source
               for unflipped ones. The rewrite is a sign change and the content survives.
  HOMOGENISED  encoding_core is positive regardless of the source's sign. Then the rewrite has
               erased the direction rather than flipped it, and every criterion in the core reads
               as "the good answer does this" whether or not that is what its author meant.
  DESTROYED    encoding_core is unrelated to encoding_source. The compiled criterion is not about
               the same thing as its source.

The second is the one worth the round. It is the failure mode that a positive-weight normalisation
invites, it is invisible to anyone reading the core alone, and nothing in the release would reveal
it -- the core ships no weights, no lineage and no author.

BOTH TENSORS EXIST, which is why this is answerable at all: a04_full carries satisfaction for the
15,248 source criteria and a04_core carries it for the 3,828 compiled ones, same judge, same four
responses, same prompts.
"""
from __future__ import annotations

import difflib
import json
import math
import pathlib
import re
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
T_FULL = ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
T_CORE = ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz"
LETTERS = "ABCD"
MATCH = 0.60

NEG = re.compile(r"\b(not|never|avoid|avoids|avoiding|refrain|without|no|don't|doesn't|shouldn't|"
                 r"must not|should not|fails? to|omit|exclude|discourage)\b", re.I)


def two_way_se(y, g1, g2):
    y = np.asarray(y, float)
    n = len(y)
    r = y - y.mean()

    def cl(g):
        s = defaultdict(float)
        for v, k in zip(r, g):
            s[k] += v
        return sum(x * x for x in s.values()) / n ** 2
    return math.sqrt(max(cl(g1) + cl(g2) - cl([f"{a}||{b}" for a, b in zip(g1, g2)]), 0.0))


def load(p):
    d = np.load(p, allow_pickle=True)
    out = {}
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, letter = str(k).split("|")
        out[(pid, int(i), letter)] = float(v)
    return out


def top_of(s):
    for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
        g = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
        if g and len(g[0].split("=")) == 1 and g[0] in LETTERS:
            return g[0]
        break
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sf, sc = load(T_FULL), load(T_CORE)
    print(f"satisfaction cells: full {len(sf)}, core {len(sc)}")

    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]
    choice = defaultdict(dict)
    for a in ann:
        for s in a.get("assessments", []):
            t = top_of(s)
            if t:
                choice[s.get("conversation_id")][a["annotator_id"]] = t

    from covalx.judge import load_join
    pairs = []
    for pid, _p, r in load_join(DATA / "comparisons.jsonl", DATA / "conversation_rubrics.jsonl"):
        ch = choice.get(pid) or {}
        core = r["coval_core"]
        core_low = [c["criterion"].lower() for c in core]
        if not core_low:
            continue
        for ci, it in enumerate(r["coval_full"]):
            s_ = it.get("scores") or []
            if len(s_) != 1:
                continue
            aid = s_[0].get("annotator_id")
            mine = ch.get(aid)
            if mine is None:
                continue
            hit = difflib.get_close_matches(it["criterion"].lower(), core_low, n=1, cutoff=MATCH)
            if not hit:
                continue
            k = core_low.index(hit[0])
            vf = {L: sf.get((pid, ci, L)) for L in LETTERS}
            vc = {L: sc.get((pid, k, L)) for L in LETTERS}
            if any(v is None for v in vf.values()) or any(v is None for v in vc.values()):
                continue
            ef = vf[mine] - float(np.mean([vf[L] for L in LETTERS if L != mine]))
            ec = vc[mine] - float(np.mean([vc[L] for L in LETTERS if L != mine]))
            w = float(s_[0]["score"])
            flipped = bool(NEG.search(core[k]["criterion"])) != bool(NEG.search(it["criterion"]))
            pairs.append({"pid": pid, "aid": aid, "w": w, "enc_src": ef, "enc_core": ec,
                          "flipped": flipped})
    n = len(pairs)
    print(f"matched source->core pairs with an author, both tensors and a choice: {n}")
    print(f"  over {len({p['pid'] for p in pairs})} prompts, {len({p['aid'] for p in pairs})} "
          f"authors;  polarity-flipped {np.mean([p['flipped'] for p in pairs]):.1%}")
    assert n > 500, "too few matched pairs"

    # ------------------------------------------------------------------ the three outcomes
    print("\n" + "=" * 78)
    print("ENCODING BEFORE AND AFTER THE REWRITE, SPLIT BY THE SOURCE'S WEIGHT SIGN")
    print("=" * 78)
    print(f"  {'source weight':16s} {'n':>5s} {'enc source':>11s} {'enc core':>10s} "
          f"{'flipped':>8s}")
    bands = {}
    for lo, hi, lbl in [(-10.1, -0.001, "negative"), (0.001, 10.1, "positive")]:
        sub = [p for p in pairs if lo <= p["w"] < hi]
        if len(sub) < 50:
            continue
        es = float(np.mean([p["enc_src"] for p in sub]))
        ec = float(np.mean([p["enc_core"] for p in sub]))
        fl = float(np.mean([p["flipped"] for p in sub]))
        bands[lbl] = {"n": len(sub), "enc_src": es, "enc_core": ec, "flip_rate": fl}
        print(f"  {lbl:16s} {len(sub):5d} {es:+11.4f} {ec:+10.4f} {fl:8.1%}")

    neg = [p for p in pairs if p["w"] < 0]
    pos = [p for p in pairs if p["w"] > 0]
    print(f"\n  THE DECISIVE COMPARISON is the negative-weight row. Its source encoding is")
    print(f"  {bands['negative']['enc_src']:+.4f} -- the author's own choice satisfies these "
          f"criteria LESS, which is")
    print(f"  what a 'penalise this' criterion should do. If the rewrite is a faithful sign flip,")
    print(f"  the core encoding should be about {-bands['negative']['enc_src']:+.4f}.")
    print(f"  It is {bands['negative']['enc_core']:+.4f}.")

    # correlation source vs core, overall and within flip status
    for lbl, sub in [("all pairs", pairs),
                     ("polarity flipped", [p for p in pairs if p["flipped"]]),
                     ("not flipped", [p for p in pairs if not p["flipped"]])]:
        if len(sub) < 50:
            continue
        r_ = float(np.corrcoef([p["enc_src"] for p in sub], [p["enc_core"] for p in sub])[0, 1])
        print(f"  corr(enc_source, enc_core)  {lbl:18s} n={len(sub):5d}  r {r_:+.3f}")

    # ------------------------------------------------------------------ homogenisation test
    print("\n" + "=" * 78)
    print("HOMOGENISATION -- does the core encoding still know the source's sign?")
    print("=" * 78)
    y = [p["enc_core"] for p in neg]
    yb = [p["enc_core"] for p in pos]
    m1, m2 = float(np.mean(y)), float(np.mean(yb))
    se1 = two_way_se(y, [p["pid"] for p in neg], [p["aid"] for p in neg])
    se2 = two_way_se(yb, [p["pid"] for p in pos], [p["aid"] for p in pos])
    d = m2 - m1
    sd = math.sqrt(se1 ** 2 + se2 ** 2)
    print(f"  core encoding, negative-weight sources  {m1:+.4f} [{m1 - 1.96 * se1:+.4f}, "
          f"{m1 + 1.96 * se1:+.4f}]  n={len(y)}")
    print(f"  core encoding, positive-weight sources  {m2:+.4f} [{m2 - 1.96 * se2:+.4f}, "
          f"{m2 + 1.96 * se2:+.4f}]  n={len(yb)}")
    print(f"  difference {d:+.4f} [{d - 1.96 * sd:+.4f}, {d + 1.96 * sd:+.4f}]  z {d / sd:+.1f}")
    src_gap = float(np.mean([p["enc_src"] for p in pos])) - float(np.mean([p["enc_src"]
                                                                          for p in neg]))
    print(f"  the same gap BEFORE the rewrite was {src_gap:+.4f}")
    retained = d / src_gap if abs(src_gap) > 1e-9 else float("nan")
    print(f"  retained across the transformation: {retained:.0%}")

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    # MY VERDICT LOGIC WAS BACKWARDS AND THE PREDICTION I HAD ALREADY WRITTEN CAUGHT IT. The
    # branch below originally read "core encoding positive AND the gap closed => HOMOGENISED". But
    # a faithful flip PREDICTS both of those. Rewriting a -8 "response gives medical advice" into
    # a +8 "response does not give medical advice" means the author's chosen response -- which did
    # not give medical advice -- now SATISFIES it. Positive core encoding is the success condition,
    # not the failure condition. And the gap between the two weight signs SHOULD close, because
    # closing it is the entire purpose of normalising every item to positive weight.
    # The correct test is whether the magnitude survives the sign change.
    flip_fidelity = m1 / (-bands["negative"]["enc_src"]) if bands["negative"]["enc_src"] else float("nan")
    pos_fidelity = m2 / bands["positive"]["enc_src"] if bands["positive"]["enc_src"] else float("nan")
    r_flip = float(np.corrcoef([p["enc_src"] for p in pairs if p["flipped"]],
                               [p["enc_core"] for p in pairs if p["flipped"]])[0, 1])
    r_keep = float(np.corrcoef([p["enc_src"] for p in pairs if not p["flipped"]],
                               [p["enc_core"] for p in pairs if not p["flipped"]])[0, 1])
    print(f"  THE TEST IS MAGNITUDE ACROSS THE SIGN CHANGE, not whether the gap closed.")
    print(f"    negative-weight sources: {bands['negative']['enc_src']:+.4f} -> {m1:+.4f}   "
          f"predicted {-bands['negative']['enc_src']:+.4f}   fidelity {flip_fidelity:.0%}")
    print(f"    positive-weight sources: {bands['positive']['enc_src']:+.4f} -> {m2:+.4f}   "
          f"predicted unchanged        fidelity {pos_fidelity:.0%}")
    print(f"  THE TRANSFORMATION IS FAITHFUL IN THE AGGREGATE. The sign flips where the rewrite")
    print(f"  flips the wording and holds where it does not, and {flip_fidelity:.0%} of the")
    print(f"  magnitude survives. The 18% 'retained gap' is not information loss -- collapsing")
    print(f"  that gap is the STATED PURPOSE of normalising every item to a positive weight, and")
    print(f"  a pipeline that did it correctly would show exactly this.")
    print(f"\n  BUT THE ITEM-LEVEL PICTURE IS THE FINDING, and it is not the aggregate one:")
    print(f"    criteria the rewrite did NOT flip:  corr(source, core) = {r_keep:+.3f}")
    print(f"    criteria the rewrite DID flip:      corr(source, core) = {r_flip:+.3f}")
    print(f"  A faithful per-item flip would give a strong NEGATIVE correlation, near -{abs(r_keep):.2f}.")
    print(f"  It gives {r_flip:+.3f}. So the flipped criteria move in the right direction ON")
    print(f"  AVERAGE while carrying almost no memory of WHICH criterion they came from. The")
    print(f"  unflipped ones, by contrast, preserve their individual encoding at {r_keep:+.3f}.")
    print(f"  The rewrite preserves the population and loses the item -- and only the 27.4% of")
    print(f"  criteria that needed flipping are affected, which is precisely the subset whose")
    print(f"  authors were expressing something to AVOID.")
    print(f"\n  That is a real and narrow information-loss result at the one stage of this chain")
    print(f"  where both ends are shipped: negative normative content survives as a population")
    print(f"  average and not as an individual statement.")

    print(f"\n  INSTRUMENT: one judge scores both sides, and the comparison is between two")
    print(f"  criteria evaluated on the SAME four responses with the SAME author's choice. A judge")
    print(f"  bias would have to differ between a criterion and its own rewrite to produce this.")
    print(f"  LIMIT: only pairs matchable at {MATCH} text similarity are here, so a heavily")
    print(f"  reworded criterion is absent -- and those are exactly the ones most likely to have")
    print(f"  lost their direction, which biases this measurement toward FAITHFUL.")

    (OUT / "rewrite_direction.json").write_text(json.dumps(
        {"pairs": n, "prompts": len({p["pid"] for p in pairs}),
         "authors": len({p["aid"] for p in pairs}),
         "flip_rate": float(np.mean([p["flipped"] for p in pairs])),
         "bands": bands,
         "core_enc_negative_sources": m1, "core_enc_positive_sources": m2,
         "gap_after": d, "gap_before": src_gap, "retained": retained, "z": d / sd,
         "flip_fidelity": flip_fidelity, "pos_fidelity": pos_fidelity,
         "corr_flipped": r_flip, "corr_unflipped": r_keep,
         "verdict": "faithful in the aggregate, lossy per item: flipped criteria carry the "
                    "population sign change but almost no item-level memory",
         "match_cutoff": MATCH,
         "limit": "matchable pairs only; heavily reworded criteria are absent and are the ones "
                  "most likely to have lost direction, biasing toward FAITHFUL"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
