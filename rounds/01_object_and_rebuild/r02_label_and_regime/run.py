"""A02 -- Label/position bias, and task-position drift.

Two effects the release can identify CLEANLY that the prior analysis did not:

1. LABEL BIAS.  The dataset card states candidate-to-label assignment was
   randomized per prompt.  Randomization is what makes this identifiable: under
   the null that labels carry no information, each of A/B/C/D should win
   equally often ACROSS prompts.  Any deviation is a pure presentation effect,
   because content is randomized with respect to label.
   The prior analysis explicitly declined this ("candidate source identity is
   unpublished, so we cannot separate model quality from label") -- but label
   bias does not need source identity.  Randomization already did the work.

2. TASK-POSITION DRIFT.  Each annotator did 5-20 tasks in order.  Fatigue,
   learning and satisficing all predict drift in: rationale length, veto rate,
   tie rate, and rubric scale use.  The release preserves the order of
   `assessments` within each annotator record, which is the only order signal
   available.

Both are measured with the annotator as the cluster unit, since one person
contributes many rows.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = str(_HERE.parents[2])
_RES = str(_HERE / "results")

LABELS = ("A", "B", "C", "D")


def parse_ranking(s: str) -> list[set[str]]:
    """'B>A=C>D' -> [{B},{A,C},{D}]"""
    out = []
    for grp in str(s).split(">"):
        members = {t.strip() for t in grp.split("=") if t.strip() in LABELS}
        if members:
            out.append(members)
    return out


def top_set(s: str) -> set[str]:
    r = parse_ranking(s)
    return r[0] if r else set()


def borda(s: str) -> dict[str, float]:
    r = parse_ranking(s)
    pts, rank = {}, 0
    for grp in r:
        size = len(grp)
        # average points for tied group
        avg = np.mean([len(LABELS) - 1 - (rank + i) for i in range(size)])
        for m in grp:
            pts[m] = float(avg)
        rank += size
    return pts


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, default=Path(_ROOT + "/data/comparisons.jsonl"))
    p.add_argument("--annotators", type=Path, default=Path(_ROOT + "/data/annotators.jsonl"))
    p.add_argument("--out", type=Path, default=Path(_RES + "/a02_position_bias.json"))
    a = p.parse_args()

    top = Counter()
    borda_sum = defaultdict(float)
    veto_by_label = Counter()
    n_assess = 0
    per_annotator_top = defaultdict(Counter)

    for line in open(a.data, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        for asm in rec["metadata"]["assessments"]:
            rb = asm.get("ranking_blocks") or {}
            w = rb.get("world") or []
            if not w:
                continue
            n_assess += 1
            ts = top_set(w[0].get("ranking", ""))
            for lab in ts:
                top[lab] += 1.0 / len(ts)
                per_annotator_top[asm["annotator_id"]][lab] += 1.0 / len(ts)
            for lab, pts in borda(w[0].get("ranking", "")).items():
                borda_sum[lab] += pts
            for u in rb.get("unacceptable") or []:
                for r in u.get("rating") or []:
                    m = re.match(r"\s*([ABCD])\b", str(r))
                    if m:
                        veto_by_label[m.group(1)] += 1

    exp = n_assess / 4
    chi2 = sum((top[l] - exp) ** 2 / exp for l in LABELS)
    # cluster-robust: bootstrap over annotators
    rng = np.random.default_rng(20260727)
    ann = list(per_annotator_top)
    shares = []
    for _ in range(2000):
        pick = rng.integers(0, len(ann), size=len(ann))
        c = Counter()
        for i in pick:
            c.update(per_annotator_top[ann[i]])
        tot = sum(c.values())
        shares.append([c[l] / tot for l in LABELS])
    shares = np.array(shares)

    print("=== LABEL BIAS (labels were randomized -> any deviation is presentation) ===")
    print(f"  assessments with a world ranking: {n_assess:,}   expected top share per label: 25.00%")
    for i, l in enumerate(LABELS):
        lo, hi = np.percentile(shares[:, i], [2.5, 97.5])
        flag = "  <-- outside 25%" if (lo > 0.25 or hi < 0.25) else ""
        print(f"   {l}: top={top[l]/n_assess:6.2%}  95%CI=[{lo:.2%},{hi:.2%}]"
              f"  borda={borda_sum[l]/n_assess:5.3f}  vetoes={veto_by_label[l]:,}{flag}")
    print(f"  chi2(3) = {chi2:.1f}  (annotator-clustered CIs above are the honest test)")

    # ---- task position drift -------------------------------------------
    pos_stats = defaultdict(lambda: {"n": 0, "rat_len": [], "veto": [], "tie": []})
    for line in open(a.annotators, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        for i, asm in enumerate(rec.get("assessments") or []):
            rb = asm.get("ranking_blocks") or {}
            w = rb.get("world") or []
            if not w:
                continue
            s = pos_stats[i + 1]
            s["n"] += 1
            s["rat_len"].append(len(w[0].get("rationale", "")))
            u = rb.get("unacceptable") or []
            if u:
                s["veto"].append(1.0 if (u[0].get("rating") or []) else 0.0)
            s["tie"].append(1.0 if "=" in str(w[0].get("ranking", "")) else 0.0)

    print("\n=== TASK-POSITION DRIFT (fatigue / satisficing) ===")
    print(f"  {'pos':>4} {'n':>7} {'rationale chars':>16} {'tie rate':>9} {'veto rate':>10}")
    drift = []
    for i in sorted(pos_stats):
        s = pos_stats[i]
        if s["n"] < 50:
            continue
        rl = float(np.mean(s["rat_len"]))
        tr = float(np.mean(s["tie"]))
        vr = float(np.mean(s["veto"])) if s["veto"] else float("nan")
        drift.append({"position": i, "n": s["n"], "rationale_chars": rl,
                      "tie_rate": tr, "veto_rate": vr})
        print(f"  {i:>4} {s['n']:>7,} {rl:>16.1f} {tr:>9.3f} {vr:>10.3f}")

    if len(drift) >= 3:
        x = np.array([d["position"] for d in drift], dtype=float)
        for key in ("rationale_chars", "tie_rate"):
            y = np.array([d[key] for d in drift])
            r = float(np.corrcoef(x, y)[0, 1])
            slope = float(np.polyfit(x, y, 1)[0])
            print(f"  trend {key:16s}: r={r:+.3f}  slope={slope:+.4f}/task")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "assessments": n_assess,
        "label_top_share": {l: top[l] / n_assess for l in LABELS},
        "label_top_ci": {l: [float(np.percentile(shares[:, i], 2.5)),
                             float(np.percentile(shares[:, i], 97.5))]
                         for i, l in enumerate(LABELS)},
        "label_borda_mean": {l: borda_sum[l] / n_assess for l in LABELS},
        "label_vetoes": dict(veto_by_label),
        "chi2": chi2,
        "position_drift": drift,
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
