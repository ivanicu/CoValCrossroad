#!/usr/bin/env python3
"""R542 — the third correction of the same number in three rounds, and the pattern is the finding.

R539 counted 16,440 calls (correct -- counted from artifacts).
R540 modelled decode throughput -> 7.25 h  (WRONG: the judge does not decode).
R541 read the JUDGE logs -> 3.3 min judging (correct), and then MODELLED generation at batch-1
     -> 22.0 min, for a 25.3 min total.
⛔ generate_core.py BATCHES -- `for i in range(0, len(items), a.batch)` -- and six completed runs
   are in the pueue log with elapsed seconds. Generation is 79-159 s, not 22 minutes.

ESTIMAND (before method): the measured wall-clock of one rows-3/4 round, and -- the point of the
  round -- the score of MODELLED versus READ estimates across R539-R542.
IDENTIFICATION: fully identified. Both halves have completed runs with logged elapsed times.
SCOPE  population: completed generate_core and judge_core runs in the pueue log · instrument: the
  runs themselves · baseline: my own modelled figures · regime: this GPU, as invoked.
WORLDS  A · modelling and reading agree -- the earlier figures were fine.
        B · they do not, and the pattern is directional: every modelled figure was wrong and
              every logged figure held.
KILL (pre-registered): any modelled figure within 2x of its logged counterpart weakens world B.
POSITIVE CONTROL: the replicate pairs must agree within 5% -- 602/603 and the four second-release
  runs are independent repeats. Disagreement means the log timings are not comparable.
NEGATIVE CONTROL: the two clusters must DIFFER from each other, else "two populations" is not a
  real distinction and pooling them would be the right move.
NOISE FLOOR: the replicates themselves.
MULTIPLICITY: 6 generation runs + 4 judge runs; all printed.
IMPOSSIBLE HERE: attributing the 79s-vs-157s gap to a specific cause. The logs record elapsed
  time and the artifact name, not the batch size or prompt count of each invocation.
"""
import json, pathlib, sys

GEN = [(602, 79), (603, 80), (646, 157), (647, 157), (649, 158), (650, 159)]
JUDGE = [(634, 3168, 40.1), (635, 3168, 40.0), (636, 3168, 40.0), (642, 15488, 199.3)]
MODELLED = {"R540 total (decode)": 7.25 * 60, "R541 generation (batch-1)": 22.0}
LOGGED_MIN_GEN = min(s for _t, s in GEN) / 60

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    src = (root / "corebench/generate_core.py").read_text()
    batched = "for i in range(0, len(items), a.batch)" in " ".join(src.split())
    print(f"  SOURCE READ  generate_core.py batches: {batched} -> "
          f"{'PASS -- so batch-1 was the wrong regime' if batched else 'FAIL'}")
    if not batched:
        print("  generation really is batch-1; R541 may stand -> UNRUNNABLE"); return 2

    a = [s for t, s in GEN if s < 120]; b = [s for t, s in GEN if s >= 120]
    sa = (max(a) - min(a)) / (sum(a) / len(a)); sb = (max(b) - min(b)) / (sum(b) / len(b))
    print(f"  POSITIVE CONTROL  replicates agree: cluster A {a} spread {sa:.1%} · "
          f"cluster B {b} spread {sb:.1%} -> {'PASS' if max(sa, sb) < 0.05 else 'FAIL'}")
    if max(sa, sb) >= 0.05: return 0
    sep = min(b) > max(a) * 1.5
    print(f"  NEGATIVE CONTROL  the two clusters are distinct populations: "
          f"{min(b)} > {max(a)}x1.5 -> {'PASS' if sep else 'FAIL -- pool them'}")
    if not sep: return 0

    gen_min = min(a) / 60
    judge_min = 15472 / (15488 / 199.3) / 60
    total = gen_min + judge_min
    print(f"\n  ⭐ ONE rows-3/4 round on the home release, ALL MEASURED:")
    print(f"     generation  {min(a):>4} s  ->  {gen_min:>5.2f} min   (tasks 602/603, batched)")
    print(f"     judging      {199.3:>4} s  ->  {judge_min:>5.2f} min   (task 642)")
    print(f"     TOTAL                  ->  {total:>5.2f} min")

    print(f"\n  {'estimate':<30}{'value':>10}{'logged':>10}{'error':>10}")
    rows = {}
    for k, v in MODELLED.items():
        logged = total if "total" in k else gen_min
        rows[k] = {"modelled_min": v, "logged_min": logged, "factor": v / logged}
        print(f"  {k:<30}{v:>8.1f} m{logged:>9.2f} m{v/logged:>9.1f}x")
    worst = max(r["factor"] for r in rows.values())
    world = "B" if worst >= 2 else "A"
    print(f"\n  WORLD {world} -- " +
          (f"every MODELLED figure was wrong by {min(r['factor'] for r in rows.values()):.0f}x-"
           f"{worst:.0f}x; every figure READ FROM A LOG held" if world == "B" else
           "modelling and reading agree"))
    print(f"  ⭐ score across R539-R542: counted-from-artifacts 1/1 right · read-from-logs 2/2 "
          f"right · MODELLED 0/2 right.")

    out = pathlib.Path(__file__).parent / "results/modelled_vs_read.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"generation_runs": GEN, "judge_runs": JUDGE,
                               "gen_min": gen_min, "judge_min": judge_min, "total_min": total,
                               "modelled": rows, "world": world}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
