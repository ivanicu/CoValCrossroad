"""Pareto frontier over the tournament's axes, computed from results/tournament.json.

⚠ THE FRONTIER COUNT IS NOT THE FINDING. With 7 axes and 8 arms almost everything is
non-dominated by dimensionality alone -- that is arithmetic, not evidence. What the frontier
DOES establish is that no arm wins every axis, so "better Core" has no single referent and a
champion could only be declared by weighting the axes, which is the governance choice the
whole round exists to keep visible.

NOT IDENTIFIED is excluded from BOTH sides of every comparison. An arm never gains a
dominance win on an axis it could not be measured on -- that would convert a missing
measurement into an advantage.
"""
import json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
r = json.load(open(HERE / "results" / "tournament.json"))
ARMS = r["arms"]


def axes_of(a):
    ra, vm, t = r["rank_acc"], r["veto_rate_majority"], r["transport"][a]
    ident = t.get("same_direction", 0) + t.get("inverted", 0) + t.get("lost", 0)
    inv = (t.get("inverted", 0) / ident) if ident else None
    return {"acc_phi": ra["phi"][a], "acc_qwen3b": ra["qwen3b"][a],
            "acc_no_fewshot": ra["no_fewshot"][a],
            "gauge_stability": -(max(ra[i][a] for i in ra) - min(ra[i][a] for i in ra)),
            "veto_avoidance": -vm["base"][a],
            "not_inverted": (1 - inv) if inv is not None else None,
            "readability": -(r["K"][a]["chars_median"] or 0)}


V = {a: axes_of(a) for a in ARMS}
AX = list(V["B_full"])


def dominates(a, b):
    ge, gt = [], False
    for x in AX:
        if V[a][x] is None or V[b][x] is None:
            continue
        ge.append(V[a][x] >= V[b][x] - 1e-12)
        if V[a][x] > V[b][x] + 1e-12:
            gt = True
    return bool(ge) and all(ge) and gt


front = [a for a in ARMS if not any(dominates(b, a) for b in ARMS if b != a)]
print("%-15s %s" % ("arm", " ".join("%15s" % x for x in AX)))
for a in ARMS:
    print("%-15s %s" % (a, " ".join(
        "%15s" % (("%.4f" % V[a][x]) if V[a][x] is not None else "NOT IDENT") for x in AX)))
print("\nwinner per axis:")
for x in AX:
    cand = [(V[a][x], a) for a in ARMS if V[a][x] is not None]
    print("  %-16s %s" % (x, max(cand)[1]))
print("\nfrontier: %d of %d arms" % (len(front), len(ARMS)))
for a in ARMS:
    by = [b for b in ARMS if b != a and dominates(b, a)]
    print("  %-15s %s" % (a, "on the frontier" if a in front else "dominated by " + ", ".join(by)))
r["pareto"] = {"axes": AX, "values": V, "frontier": front}
(HERE / "results" / "tournament.json").write_text(json.dumps(r, indent=1))
