"""Does compilation ADD the distributive cost, or inherit it?

r145 found a group-level constituency: within the same prompt and matched on decisiveness, South
African participants are unserved by the panel's own plurality 15.6 points more often than their
co-panelists, on a 34% base. That is a fact about the PANEL. It says nothing yet about the pipeline,
because the plurality is not what the pipeline computes.

So run the identical measurement with the chooser swapped, on the same prompts and the same people:

    PLURALITY   the response top-ranked by the most people          instrument-free
    FULL        the response the full rubric scores highest          via the rebuilt judge
    CORE        the response the compiled core rubric scores highest via the rebuilt judge

Paired by construction -- same prompt, same panel, same four candidates -- so the difference between
choosers is measured within prompt and the comparison is tight.

    gap under CORE  >  gap under PLURALITY   -> compilation ADDS a distributive cost
    gap under CORE  ~  gap under PLURALITY   -> compilation INHERITS the panel's own disagreement
    gap under CORE  <  gap under PLURALITY   -> compilation REDUCES it

INSTRUMENT WARNING, on the face of the round rather than in a footnote. The plurality arm executes
no model. The FULL and CORE arms route through the locally rebuilt 2B satisfaction judge, because
the release ships no satisfaction labels and never scores a response against coval_core -- humans
ranked the responses directly. So any statement about what compilation does is conditional on that
judge, and the honest form of a positive result is "a pipeline built with this judge widens the gap",
not "compilation widens the gap".

What is NOT conditional on the judge: the comparison between the two model-based arms. FULL and CORE
run through the SAME judge on the SAME responses, so a difference between them cannot be the judge --
that is the one contrast here with the instrument divided out, and it is the one that actually
answers the question in the title.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
from collections import defaultdict

import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
from covalx.legacy import round_results  # noqa: E402
OUT = pathlib.Path(__file__).resolve().parent / "results"
LETTERS = "ABCD"
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}
MIN_STRATA = 20


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


def load_rankings():
    rank: dict[str, dict[str, np.ndarray]] = defaultdict(dict)
    demo: dict[str, dict] = {}
    with (ROOT / "data" / "annotators.jsonl").open() as fh:
        for line in fh:
            rec = json.loads(line)
            aid = rec["annotator_id"]
            demo[aid] = rec.get("demographics", {}) or {}
            for a in rec.get("assessments", []):
                blocks = a.get("ranking_blocks") or {}
                for key in ("world", "personal"):
                    got = False
                    for b in blocks.get(key, []) or []:
                        v = parse_ranking(b.get("ranking") or "")
                        if v is not None:
                            rank[a["conversation_id"]][aid] = v
                            got = True
                            break
                    if got:
                        break
    return rank, demo


def choosers(pid, per, sat_full, sat_core) -> dict[str, int]:
    tops = {a: set(np.nonzero(v >= np.nanmax(v) - 1e-9)[0].tolist()) for a, v in per.items()}
    counts = [sum(1 for t in tops.values() if r in t) for r in range(4)]
    out = {"plurality": int(np.argmax(counts))}
    for name, tensor in (("full", sat_full), ("core", sat_core)):
        M = tensor.get(pid)
        out[name] = int(np.argmax(np.nanmean(M, axis=0))) if M is not None else None
    return out, tops


def group_gaps(rank, demo, sat_full, sat_core, arm: str) -> dict:
    """Within-prompt, decisiveness-matched gap per demographic group, for one chooser."""
    strata: dict[tuple[str, str], list[float]] = defaultdict(list)
    rows = 0
    unserved_all = []
    for pid, per in rank.items():
        if len(per) < 4:
            continue
        ch, tops = choosers(pid, per, sat_full, sat_core)
        pick = ch.get(arm)
        if pick is None:
            continue
        for size in (1, 2, 3):
            members = [(a, 0 if pick in t else 1) for a, t in tops.items() if len(t) == size]
            if len(members) < 4:
                continue
            for k in {kk for a, _u in members for kk in (demo.get(a) or {})}:
                vals = [(demo.get(a, {}).get(k), u) for a, u in members]
                vals = [(v, u) for v, u in vals if isinstance(v, str) and v and len(v) < 60]
                for g in {v for v, _u in vals}:
                    ins = [u for v, u in vals if v == g]
                    outs = [u for v, u in vals if v != g]
                    if ins and outs:
                        strata[(k, g)].append(float(np.mean(ins)) - float(np.mean(outs)))
        for a, t in tops.items():
            unserved_all.append(0 if pick in t else 1)
            rows += 1
    res = {}
    for key, d in strata.items():
        if len(d) < MIN_STRATA:
            continue
        arr = np.array(d)
        m, se = float(arr.mean()), float(arr.std(ddof=1) / math.sqrt(len(arr)))
        res[key] = {"delta": m, "se": se, "n_strata": len(d)}
    return {"gaps": res, "base_unserved": float(np.mean(unserved_all)), "rows": rows}


def paired_diff(rank, demo, sat_full, sat_core, arm_a: str, arm_b: str) -> dict:
    """Gap(arm_b) - Gap(arm_a) computed on the SAME prompt-strata, so the difference is paired and
    the prompt-level variance cancels instead of being added twice."""
    strata: dict[tuple[str, str], list[float]] = defaultdict(list)
    for pid, per in rank.items():
        if len(per) < 4:
            continue
        ch, tops = choosers(pid, per, sat_full, sat_core)
        pa, pb = ch.get(arm_a), ch.get(arm_b)
        if pa is None or pb is None:
            continue
        for size in (1, 2, 3):
            members = [a for a, t in tops.items() if len(t) == size]
            if len(members) < 4:
                continue
            for k in {kk for a in members for kk in (demo.get(a) or {})}:
                vals = [(demo.get(a, {}).get(k), tops[a]) for a in members]
                vals = [(v, t) for v, t in vals if isinstance(v, str) and v and len(v) < 60]
                for g in {v for v, _t in vals}:
                    ins = [t for v, t in vals if v == g]
                    outs = [t for v, t in vals if v != g]
                    if not ins or not outs:
                        continue
                    ga = (np.mean([0 if pa in t else 1 for t in ins])
                          - np.mean([0 if pa in t else 1 for t in outs]))
                    gb = (np.mean([0 if pb in t else 1 for t in ins])
                          - np.mean([0 if pb in t else 1 for t in outs]))
                    strata[(k, g)].append(float(gb - ga))
    out = {}
    for key, d in strata.items():
        if len(d) < MIN_STRATA:
            continue
        arr = np.array(d)
        m, se = float(arr.mean()), float(arr.std(ddof=1) / math.sqrt(len(arr)))
        out[key] = {"diff": m, "ci95": [m - 1.96 * se, m + 1.96 * se], "n_strata": len(d),
                    "z": m / se if se else 0.0}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=8)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    base = round_results("R04")
    sat_full, sat_core = load_sat(base / "a04_full.npz"), load_sat(base / "a04_core.npz")
    rank, demo = load_rankings()

    arms = {a: group_gaps(rank, demo, sat_full, sat_core, a)
            for a in ("plurality", "full", "core")}
    print("chooser        base unserved   rows   groups")
    for a, r in arms.items():
        print(f"  {a:12s} {r['base_unserved']:12.1%} {r['rows']:7d} {len(r['gaps']):8d}")

    d_core_vs_plur = paired_diff(rank, demo, sat_full, sat_core, "plurality", "core")
    d_core_vs_full = paired_diff(rank, demo, sat_full, sat_core, "full", "core")

    keys = sorted(arms["plurality"]["gaps"],
                  key=lambda k: -abs(arms["plurality"]["gaps"][k]["delta"]))[: args.top]
    # NORMALISED GAP. A noisier chooser mechanically compresses group gaps, because a chooser
    # approaching random has a gap of zero by construction. The rubric arms leave 49.5-58.0%
    # unserved against plurality's 34.0%, so their raw gaps are NOT comparable to plurality's.
    # Dividing each gap by its own arm's base rate is the minimum correction; without it the
    # apparent "compilation compresses group gaps" is an artefact of compilation being worse.
    #
    # AND PLURALITY IS NOT A PEER ARM. It is the argmax of exactly the quantity being measured --
    # the response that serves the most people -- so it is the CEILING, and "plurality serves more"
    # is a derivation, not a finding. The only contrast between two comparable choosers, sharing
    # the same judge on the same responses, is core vs full.
    base = {a: arms[a]["base_unserved"] for a in arms}
    print(f"\n{'group':30s} {'plurality':>10s} {'full':>9s} {'core':>9s}"
          f"{'  | normalised by own base rate':>34s}")
    table = []
    for k in keys:
        p = arms["plurality"]["gaps"][k]["delta"]
        f = arms["full"]["gaps"].get(k, {}).get("delta")
        c = arms["core"]["gaps"].get(k, {}).get("delta")
        dp, df = d_core_vs_plur.get(k), d_core_vs_full.get(k)
        fs = f"{f:+9.4f}" if f is not None else "        -"
        cs = f"{c:+9.4f}" if c is not None else "        -"
        dps = (f"{dp['diff']:+.4f} [{dp['ci95'][0]:+.3f},{dp['ci95'][1]:+.3f}]" if dp else "-")
        dfs = (f"{df['diff']:+.4f} [{df['ci95'][0]:+.3f},{df['ci95'][1]:+.3f}]" if df else "-")
        npl = p / base["plurality"]
        nf = f / base["full"] if f is not None else None
        nc = c / base["core"] if c is not None else None
        print(f"  {k[1][:28]:28s} {p:+10.4f} {fs} {cs}   "
              f"{npl:+.3f} / {nf:+.3f} / {nc:+.3f}" if nf is not None and nc is not None
              else f"  {k[1][:28]:28s} {p:+10.4f} {fs} {cs}")
        print(f"  {'':28s} {'':10s} {'':9s} {'':9s}   core-plur {dps}  core-full {dfs}")
        table.append({"axis": k[0], "group": k[1], "plurality": round(p, 4),
                      "full": round(f, 4) if f is not None else None,
                      "core": round(c, 4) if c is not None else None,
                      "core_minus_plurality": dp, "core_minus_full": df,
                      "normalised": {"plurality": round(p / base["plurality"], 4),
                                     "full": round(f / base["full"], 4) if f is not None else None,
                                     "core": round(c / base["core"], 4) if c is not None else None}})

    sig_p = sum(1 for v in d_core_vs_plur.values() if v["ci95"][0] > 0 or v["ci95"][1] < 0)
    sig_f = sum(1 for v in d_core_vs_full.values() if v["ci95"][0] > 0 or v["ci95"][1] < 0)
    print(f"\ngroups whose gap CHANGES (CI excludes 0):  core vs plurality {sig_p}/"
          f"{len(d_core_vs_plur)}   core vs full {sig_f}/{len(d_core_vs_full)}")

    (OUT / "compilation_adds.json").write_text(json.dumps({
        "base_unserved": {a: round(r["base_unserved"], 4) for a, r in arms.items()},
        "table": table,
        "n_groups_changed_core_vs_plurality": sig_p,
        "n_groups_changed_core_vs_full": sig_f,
        "n_groups": len(d_core_vs_plur),
        "instrument": ("plurality arm executes no model; full and core arms route through the "
                       "rebuilt 2B judge. The core-vs-full contrast shares that judge on the same "
                       "responses, so it is the one comparison with the instrument divided out."),
    }, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
