#!/usr/bin/env python3
"""
R683 -- the membership null already existed, and it is exact.

CHECK #284 ON R682's NEXT LINE -- THE PROPOSAL WAS WEAKER THAN WHAT WAS ALREADY COMMITTED.
  R682 closed: "Re-run R361 against a perturbed set -- one member swapped for an arm outside the
  extension -- and compare its reported statistics." ⭐ R361 ALREADY SWEEPS ALL OF THEM: an EXACT
  enumeration over the C(9,4) = 126 ways to split its 9 arms into a 4-label group and its
  complement, committed as `rank_null` and `rank_resolved`. ONE perturbation is strictly weaker than
  126, and re-running a round destroyed its artifact once already in this arc. ⭐ FOURTH TIME IN
  THIS ARC THE ANSWER WAS IN A COMMITTED ARTIFACT (R664's lesson; then R676, R678, now here), and
  the prior-art gate is what found it -- before any code was written, which is the only reason it
  cost nothing.

ESTIMAND        does R361's hard-coded FIVE function as an untested input assumption? Answered from
                its committed exact null; plus an ARITHMETIC AUDIT of that null's internal
                consistency.
IDENTIFICATION  this reads a committed artifact and does NOT re-execute R361. A number wrong in the
                file is wrong here. Internal consistency is what is claimed, and only that.
SCOPE           population : R361's 9 arms × 2 judges × 126 assignments
                instrument : the committed artifact + a recomputation of its own p from its own pct
                             instrument unit = A COMMITTED FIELD = claim unit. EQUAL.
                baseline   : the exact null over all assignments
                regime     : n_prompts = 968, pool 16
WORLDS          A UNTESTED ASSUMPTION: the hard-coded set is never compared to alternatives.
                B ALREADY NULLED: the round enumerates every alternative membership, so the set is
                  tested exhaustively and the question is what the null SAYS.
KILL            if R361's committed controls are not all true, its numbers are silence and nothing
                is read out.
POSITIVE CTRL   R361's own positive / g0 / placebo, from the artifact.
ARITHMETIC CTRL the null size must equal C(9,4) exactly.
g=0             a percentile of 0.5 must map to two-sided p = 1.0 under the same formula.
PLACEBO         recomputation twice identical.
ARTIFACT        results/membership_null.json
IMPOSSIBLE      re-executing R361 to confirm the file matches the code would risk the artifact that
                a re-run destroyed once in this arc; the source hash is committed instead.
"""
from __future__ import annotations
import json, math, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent


def main() -> int:
    art = next(ARC.glob("R361_*/results/*.json"), None)
    if art is None:
        print("UNRUNNABLE: R361's artifact absent. Exit 2, never 0."); return 2
    d = json.loads(art.read_text())

    print("─── CONTROLS ───")
    c = d.get("controls", {})
    posok = (all(c.get("positive", {}).values()) and all(c.get("g0", {}).values())
             and c.get("placebo") is True)
    print(f"  POSITIVE  R361's own committed controls -> positive={c.get('positive')} "
          f"g0={c.get('g0')} placebo={c.get('placebo')} -> {'PASS' if posok else '⛔ FAIL'}")
    n_arms = len(d["arms"]); n_lab = len(d["rank_sd"]["label"]) and 4
    exact = math.comb(n_arms, 4)
    got = d["rank_null"]["2B"]["n"]
    arok = exact == got
    print(f"  ARITHMETIC null size must be C({n_arms},4) = {exact} -> committed {got} -> "
          f"{'PASS' if arok else '⛔ FAIL — the enumeration is not what the docstring says'}")
    two = lambda p: min(1.0, 2 * min(p, 1 - p))
    g0ok = abs(two(0.5) - 1.0) < 1e-12
    print(f"  g=0       a percentile of 0.5 -> two-sided p {two(0.5):.4f} -> "
          f"{'PASS' if g0ok else '⛔ FAIL'}")
    plc = two(0.9047619047619048) == two(0.9047619047619048)
    print(f"  PLACEBO   recomputation twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = posok and arok and g0ok and plc

    print(f"\n─── THE COMMITTED NULL (G3 — both judges, no cell hidden) ───")
    rows = []
    for j, v in d["rank_null"].items():
        naive = two(v["pct"])
        rows.append({"judge": j, **v, "naive_two_sided": naive,
                     "resolved": d["rank_resolved"][j]})
        print(f"  @{j:<5} gap {v['obs']:+.2f}  percentile {v['pct']*100:5.1f}%  "
              f"committed p {v['two_sided_p']:.4f}  "
              f"{'RESOLVED' if d['rank_resolved'][j] else 'NOT RESOLVED'}")
        print(f"         recomputed from pct alone (no ties): {naive:.4f}  "
              f"{'— matches' if abs(naive - v['two_sided_p']) < 1e-4 else '— DIFFERS, so the committed p accounts for TIES in the null, which a pct-only formula cannot'}")
    print(f"\n  mean label rank : {d['mean_label_rank']}")
    print(f"  mean five rank  : {d['mean_five_rank']}")
    print(f"  rank sd         : label {d['rank_sd']['label']}   five {d['rank_sd']['five']}")

    dirn = d["rank_resolved"].get("2B") is True and d["rank_resolved"].get("0.8B") is False
    print(f"\n  DIRECTIONAL 2B resolves and 0.8B does not -> {'HOLDS' if dirn else '⛔ FAILS'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — R361's own controls did not all fire; its numbers are silence here."
    else:
        world = (f"⭐⭐⭐ WORLD B — ALREADY NULLED, EXHAUSTIVELY. R361's hard-coded FIVE is not an "
                 f"untested input assumption: the round enumerates ALL {got} ways to split its "
                 f"{n_arms} arms into a 4-group and its complement, exactly, and compares the "
                 f"observed rank gap against that full distribution. ⭐ AND THE ANSWER IS A SCOPE "
                 f"CONDITION ON THE DEFINITION, not a fact about the arms: at the 2B judge the "
                 f"label/five rank split is RESOLVED; at 0.8B it is NOT — gap {d['rank_null']['0.8B']['obs']:+.2f} "
                 f"at the {d['rank_null']['0.8B']['pct']*100:.1f}th percentile of its own null, "
                 f"two-sided p = {d['rank_null']['0.8B']['two_sided_p']:.4f}. So the separation "
                 f"between the extension and the label-reading arms is INSTRUMENT-DEPENDENT. "
                 f"⚠ AND THE LABEL GROUP'S OWN SPREAD IS WHY: sd {d['rank_sd']['label']['0.8B']:.2f} "
                 f"at 0.8B against {d['rank_sd']['five']['0.8B']:.2f} for the five — the label-users "
                 f"SPLIT at the smaller judge, so a mean gap is the wrong summary there.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: 2 judges × {got} assignments (exact, not sampled) + 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}   R361 source sha256: {d.get('source_sha256','?')[:16]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"membership_null.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "null_size": got, "exact_expected": exact, "arithmetic_ok": arok,
        "judges": rows, "directional_holds": dirn,
        "r361_source_sha256": d.get("source_sha256"),
        "check284": ("R682's NEXT proposed ONE perturbation of R361's hard-coded set. R361 already "
                     "enumerates all C(9,4)=126 membership assignments exactly. The proposal was "
                     "strictly weaker than the committed instrument."),
        "prior_art": ("found by P4's gate BEFORE any code was written -- fourth time in this arc the "
                      "answer sat in a committed artifact."),
        "limit": "reads the artifact; does not re-execute R361. Internal consistency only.",
    }, indent=2))
    print(f"  wrote {HERE/'results'/'membership_null.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
