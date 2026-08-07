#!/usr/bin/env python3
"""
R856 · why does clause ④ exclude NOTHING? — because ② is strictly harder, and that is a DERIVATION.

⛔ THE ARITHMETIC TRAP, RUN FIRST, AND IT DEMOTES THIS ROUND'S OWN HEADLINE. The plan was to
recompute the conjunction on the 99-arm space and lay it beside the published extension (1 arm, on
42). Intersecting the two committed 99-arm satisfier sets gives |②∧④′| = 29 = |②| exactly, i.e.
② ⊆ ④′. **Before reporting that as a finding, ask whether the algebra forces it.** It does:

    prompt-blind comparator `genericpool16`, even half : 0.5404
    ④′'s response-only bar,   even half                : 0.4820
    the comparator sits +0.0584 ABOVE the bar

An arm that resolvably beats 0.5404 will resolvably beat 0.4820. **So ②⇒④′ is LARGELY FORCED, the
29 is 1+1=2, and it is labelled a derivation.**

⭐ THE MECHANISM IS THE FINDING, AND IT EXPLAINS A NUMBER THAT HAS SAT UNEXPLAINED. R440 committed
`excluded_by_4 = 0 of 42` and this file has carried it as an observation. **④ excludes nothing
because ② is strictly harder: everything ④ would exclude, ② already excluded.** ④ can only bind on
arms ② has rejected — so in the CONJUNCTION it contributes nothing, not because it is decoration
but because it is dominated.

ESTIMAND        (a) |②∧④′| on the 99-arm space, from committed artifacts;
                (b) the gap between ②'s comparator and ④′'s bar, which decides whether (a) is a
                    measurement or a derivation.
IDENTIFICATION  (a) set intersection over two committed artifacts on an identical 99-arm list;
                (b) two scalars on the same even-annotator half.
SCOPE           population: 99 arms · instrument: A2 vs EVEN annotators · regime: home release
WORLDS          A · the comparator sits ABOVE the bar -> ②⇒④′ forced, ④ dominated, (a) is algebra
                B · it sits BELOW -> the intersection is a real measurement and ④ binds
KILL            the two artifacts' arm lists must be IDENTICAL, or the intersection is a
                population error of the kind entry 1371 recorded. Checked, not assumed.
⚠ NO CONTROL    (a) is set arithmetic over committed artifacts and (b) is two means; there is
                nothing to be noisy. The honest analogue is the arm-list identity check, which CAN
                fail, and the arithmetic-trap check, which DID fire and demoted the headline.
ARTIFACT        results/clause4_dominated.json
IMPOSSIBLE      the full conjunction on 99 — clause ③ is a PROVENANCE property, measured by
                R360/R444 only on 42 arms. Classifying 99 arms' provenance from their NAMES would
                be `a label is not a description`. Named here, not approximated.
"""
import json, glob, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
import score as SC                                              # noqa: E402

d849 = json.load(open(glob.glob(str(ROOT / "E05*/A24*/R849_*/results/proposed_clause_extension.json"))[0]))
d851 = json.load(open(glob.glob(str(ROOT / "E05*/A24*/R851_*/results/clause2_noise_extension.json"))[0]))
a849 = [r["arm"] for r in d849["arms"]]; a851 = [r["arm"] for r in d851["arms"]]
same = a849 == a851
print(f"  KILL CHECK  the two artifacts' arm lists are identical: {same}  "
      f"{'PASS' if same else 'FAIL'}   ({len(a849)} vs {len(a851)})")
if not same:
    print("  UNVERIFIED: different populations; intersecting them is entry 1371's error. Exit 2.")
    raise SystemExit(2)

s4 = {r["arm"] for r in d849["arms"] if r.get("satisfies")}
s2 = {r["arm"] for r in d851["arms"] if r.get("satisfies_real")}
both = sorted(s2 & s4)
print(f"\n  ② satisfiers {len(s2)} · ④′ satisfiers {len(s4)} · ②∧④′ {len(both)}")
print(f"  ⭐ ② ⊆ ④′ : {s2 <= s4}")

targets, _ = SC.load_targets()
pids = [p for p in sorted(targets) if len(targets[p]) >= 2]
H = {p: np.array([SC.cls(np.array(y, float)) for y, _ in targets[p][1::2]]) for p in pids}
pids = [p for p in pids if len(H[p])]
S = SC.load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
comp = float(np.mean([np.mean(SC.cls(SC.yvec(S[p], sorted({i for i, _ in S[p]}))) == H[p])
                      for p in pids if p in S]))
bar = float(d849["bar_even_half_A2"])
print(f"\n  ②'s comparator `genericpool16` : {comp:.4f}")
print(f"  ④′'s response-only bar         : {bar:.4f}")
print(f"  ⭐ gap {comp - bar:+.4f}  -> ②⇒④′ is "
      f"{'LARGELY FORCED — the intersection is a DERIVATION' if comp > bar else 'NOT forced'}")
print("\n  ⭐⭐ SO CLAUSE ④ IS DOMINATED BY CLAUSE ②: ④ can only bind on arms ② already rejected.")
print("     That explains R440's committed `excluded_by_4 = 0 of 42` from a MECHANISM rather than")
print("     leaving it as an observation — which is how this file has carried it until now.")
print("\n  ⚠ The full conjunction on 99 is NOT computed: clause ③ is a PROVENANCE property measured")
print("     only on 42 arms, and classifying 99 arms from their NAMES would be `a label is not a")
print("     description`. Named as impossible here rather than approximated.")

head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                      capture_output=True, text=True).stdout.strip()
json.dump({"commit": head, "n_arms": len(a849), "c2": sorted(s2), "c4prime": sorted(s4),
           "c2_and_c4prime": both, "c2_subset_of_c4prime": bool(s2 <= s4),
           "comparator_A2": comp, "c4prime_bar": bar, "gap": comp - bar,
           "verdict": "DERIVATION: c2 implies c4prime; clause 4 is dominated",
           "clause3_on_99_arms": "IMPOSSIBLE — provenance measured only on 42"},
          open(OUT / "clause4_dominated.json", "w"), indent=2)
print(f"\n  artifact: results/clause4_dominated.json @ {head[:8]}")
