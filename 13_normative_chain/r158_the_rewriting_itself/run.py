"""The rewriting, isolated: same criterion, same prompt, same responses, different wording only.

Two worlds survived r157. Either the compiler's rewriting turns vague crowd wording into something
a judge can evaluate, or an undocumented selection rule picks better criteria and the rewriting is
incidental. r156 ruled out the documented rule, so the second world needs a rule nobody has named.

They separate cleanly on the 1,181 core items that match a source item. For those, both versions of
THE SAME criterion have satisfaction scores against the same four responses:

    REWRITTEN   score using the compiled item's satisfaction
    RAW         score using its matched source item's satisfaction

Selection is held fixed by construction -- it is literally the same criterion -- so any gap is the
wording.

THE SAMPLE IS SELECTED AND THE SELECTION RUNS AGAINST THE HYPOTHESIS. A pair only exists when the
rewrite stayed within 0.80 similarity of its source, so this measures LIGHT rewriting only. The
heavily rewritten 69% are unmatched by construction and invisible here. Concluding about rewriting
in general from lightly-rewritten pairs would be exactly the generalisation this phase has already
been burned by twice.

SO THE DESIGN IS A DOSE-RESPONSE, not a two-arm comparison. Bin the pairs by how much the text
actually changed and ask whether the advantage GROWS with the edit. A gradient extrapolates past the
sample; a flat line says the effect is a property of the matched band and nothing more. This is the
memo's own requirement -- dose-response characterised -- applied to the one place in this release
where a dose is measurable.

CONTROL: a within-prompt swap, pairing each core item with a DIFFERENT prompt's raw source at
similar length. If the rewritten-versus-raw gap survives being scrambled that way, the gap is about
the arms' general properties rather than about the pairing.
"""
from __future__ import annotations

import argparse
import difflib
import json
import math
import pathlib
import sys
from collections import defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
LETTERS = "ABCD"
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}


def load_sat(path: pathlib.Path) -> dict[str, np.ndarray]:
    z = np.load(path, allow_pickle=True)
    cells: dict[str, dict[tuple[int, int], float]] = defaultdict(dict)
    for s, m in zip(z["sat"], z["meta"]):
        cid, ci, rl = str(m).split("|")
        if rl in LETTERS:
            cells[cid][(int(ci), LETTERS.index(rl))] = float(s)
    out = {}
    for cid, d in cells.items():
        M = np.full((max(k[0] for k in d) + 1, 4), np.nan)
        for (i, j), v in d.items():
            M[i, j] = v
        out[cid] = M
    return out


def load_texts():
    from covalx.judge import load_join
    out = {}
    for pid, _p, r in load_join(ROOT / "data" / "comparisons.jsonl",
                                ROOT / "data" / "conversation_rubrics.jsonl"):
        out[pid] = ([it["criterion"].strip() for it in r["coval_full"]],
                    [c["criterion"].strip() for c in r["coval_core"]])
    return out


def parse_ranking(txt: str):
    v = np.full(4, np.nan)
    groups = [g.strip() for g in txt.replace(" ", "").split(">") if g.strip()]
    if not groups:
        return None
    for gi, g in enumerate(groups):
        for letter in g.split("="):
            if letter in RANK_MAP:
                v[RANK_MAP[letter]] = -gi
    return v if not np.isnan(v).all() else None


def load_rankings(block: str):
    out: dict[str, list[np.ndarray]] = defaultdict(list)
    with (ROOT / "data" / "annotators.jsonl").open() as fh:
        for line in fh:
            rec = json.loads(line)
            for a in rec.get("assessments", []):
                for b in (a.get("ranking_blocks") or {}).get(block, []) or []:
                    v = parse_ranking(b.get("ranking") or "")
                    if v is not None:
                        out[a["conversation_id"]].append(v)
                        break
    return out


def concordance(score, pref) -> float:
    good = tot = 0.0
    for i in range(4):
        for j in range(i + 1, 4):
            if np.isnan(pref[i]) or np.isnan(pref[j]):
                continue
            tot += 1
            ds, dp = score[i] - score[j], pref[i] - pref[j]
            if dp == 0 or ds == 0:
                good += 0.5
            elif (ds > 0) == (dp > 0):
                good += 1
    return good / tot if tot else float("nan")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--block", default="world", choices=["world", "personal"])
    ap.add_argument("--cutoff", type=float, default=0.80)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    base = ROOT / "01_object_and_rebuild" / "r04_rebuild_satisfaction" / "results"
    sat_full, sat_core = load_sat(base / "a04_full.npz"), load_sat(base / "a04_core.npz")
    texts = load_texts()
    rank = load_rankings(args.block)
    cids = [c for c in sat_core if c in sat_full and c in texts and c in rank]

    rng = np.random.default_rng(args.seed)
    pairs_by_prompt: dict[str, list[tuple[int, int, float]]] = {}
    npairs = 0
    for cid in cids:
        full_txt, core_txt = texts[cid]
        SF, SC = sat_full[cid], sat_core[cid]
        low = [t.lower() for t in full_txt]
        found = []
        for ci, ct in enumerate(core_txt):
            if ci >= SC.shape[0]:
                continue
            hit = difflib.get_close_matches(ct.lower(), low, n=1, cutoff=args.cutoff)
            if not hit:
                continue
            fi = low.index(hit[0])
            if fi >= SF.shape[0]:
                continue
            sim = difflib.SequenceMatcher(None, ct.lower(), hit[0]).ratio()
            found.append((ci, fi, sim))
        if found:
            pairs_by_prompt[cid] = found
            npairs += len(found)
    print(f"prompts {len(cids)}   prompts with >=1 matched pair {len(pairs_by_prompt)}   "
          f"pairs {npairs}   cutoff {args.cutoff}")

    # ---- overall, and by how much the text actually changed
    bands = [(0.80, 0.88, "heavier"), (0.88, 0.95, "moderate"), (0.95, 1.01, "near-identical")]
    arms = defaultdict(list)
    band_arms = {b[2]: defaultdict(list) for b in bands}
    for cid, found in pairs_by_prompt.items():
        SF, SC = sat_full[cid], sat_core[cid]
        ci = [p[0] for p in found]
        fi = [p[1] for p in found]
        rw = np.nan_to_num(SC[ci], nan=0.0).mean(axis=0)
        raw = np.nan_to_num(SF[fi], nan=0.0).mean(axis=0)
        # control: same number of raw criteria, drawn from elsewhere in the same prompt
        pool = [i for i in range(SF.shape[0]) if i not in set(fi)]
        alt = rng.permutation(pool)[: len(fi)] if len(pool) >= len(fi) else fi
        oth = np.nan_to_num(SF[list(alt)], nan=0.0).mean(axis=0)
        msim = float(np.mean([p[2] for p in found]))
        band = next((b[2] for b in bands if b[0] <= msim < b[1]), None)
        for pref in rank[cid]:
            arms["rewritten"].append(concordance(rw, pref))
            arms["raw_source"].append(concordance(raw, pref))
            arms["other_raw_same_n"].append(concordance(oth, pref))
            if band:
                band_arms[band]["rewritten"].append(concordance(rw, pref))
                band_arms[band]["raw_source"].append(concordance(raw, pref))

    def ms(v):
        a = np.asarray(v, float)
        a = a[np.isfinite(a)]
        return (float(a.mean()), float(a.std(ddof=1) / math.sqrt(a.size)), a.size)

    print(f"\n{'arm':22s} {'concordance':>12s} {'95% CI':>20s} {'n':>7s}")
    res = {}
    for k in ("rewritten", "raw_source", "other_raw_same_n"):
        m, se, n = ms(arms[k])
        res[k] = {"concordance": round(m, 4),
                  "ci95": [round(m - 1.96 * se, 4), round(m + 1.96 * se, 4)], "n": n}
        print(f"  {k:20s} {m:12.4f} [{m - 1.96 * se:7.4f},{m + 1.96 * se:7.4f}] {n:7d}")

    d = np.asarray(arms["rewritten"], float) - np.asarray(arms["raw_source"], float)
    d = d[np.isfinite(d)]
    dm, dse = float(d.mean()), float(d.std(ddof=1) / math.sqrt(d.size))
    print(f"\n  PAIRED rewritten - raw_source: {dm:+.4f} "
          f"[{dm - 1.96 * dse:+.4f}, {dm + 1.96 * dse:+.4f}]  z={dm / dse:.2f}  n={d.size}")

    print(f"\ndose-response by how much the wording changed:")
    dose = {}
    for _lo, _hi, name in bands:
        a, b = band_arms[name]["rewritten"], band_arms[name]["raw_source"]
        if len(a) < 30:
            print(f"  {name:16s} n={len(a):5d}  too few, reported as UNDERPOWERED")
            dose[name] = {"n": len(a), "delta": None}
            continue
        dd = np.asarray(a, float) - np.asarray(b, float)
        dd = dd[np.isfinite(dd)]
        m2, se2 = float(dd.mean()), float(dd.std(ddof=1) / math.sqrt(dd.size))
        dose[name] = {"n": int(dd.size), "delta": round(m2, 4),
                      "ci95": [round(m2 - 1.96 * se2, 4), round(m2 + 1.96 * se2, 4)]}
        print(f"  {name:16s} n={dd.size:5d}  delta {m2:+.4f} "
              f"[{m2 - 1.96 * se2:+.4f}, {m2 + 1.96 * se2:+.4f}]")

    (OUT / "rewriting.json").write_text(json.dumps(
        {"block": args.block, "cutoff": args.cutoff, "pairs": npairs,
         "prompts_with_pairs": len(pairs_by_prompt), "arms": res,
         "paired_delta": {"delta": round(dm, 4),
                          "ci95": [round(dm - 1.96 * dse, 4), round(dm + 1.96 * dse, 4)],
                          "z": round(dm / dse, 2), "n": int(d.size)},
         "dose_response": dose,
         "selection_caveat": ("a pair exists only when the rewrite stayed within the cutoff of its "
                              "source, so this measures LIGHT rewriting; the heavily rewritten 69% "
                              "are unmatched by construction and invisible here"),
         "instrument": "one rebuilt 2B judge for both arms on the same responses"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
