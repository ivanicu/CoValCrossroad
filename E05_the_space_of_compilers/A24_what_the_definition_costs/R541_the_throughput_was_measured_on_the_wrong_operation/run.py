#!/usr/bin/env python3
"""R541 — R540 measured decode throughput for an operation that does not decode.

R540 measured 89.2 tok/s (0.8B) and 80.6 tok/s (2B) at 128 new tokens and converted 16,440 calls
to 6.55-7.25 hours. ⛔ The judging step does not decode. `judge_core.py` calls
`Judge(model).score(prompts)` on a BATCH -- no `generate()` anywhere in the file, and R417 (quoted
in that file's own provenance comment) established the judge has no stochastic step.

⭐ AND THE PROJECT ALREADY MEASURED THE RIGHT THING, four times, in its own pueue logs, because
`judge_core.py:117` prints elapsed seconds beside the call count. No modelling was needed.

ESTIMAND (before method): judge calls per second on the real operation, and the corrected
  wall-clock for one rows-3/4 round split into GENERATION (which does decode) and JUDGING
  (which does not).
IDENTIFICATION: fully identified -- completed runs with both n_calls and elapsed seconds.
SCOPE  population: completed judge_core runs in the pueue log · instrument: the runs themselves ·
  baseline: R540's decode-based figure · regime: this GPU, 2B judge, batch as invoked.
WORLDS  A · R540's figure survives -- the operations are close enough that the conversion holds.
        B · it does not -- the judging step is far faster than decode, and 7.25 h is wrong by a
              large factor because the instrument's unit was not the claim's unit.
KILL (pre-registered): measured judging within 2x of R540's implied rate keeps world A.
POSITIVE CONTROL: the three 3,168-call runs must agree with each other -- three independent
  replicates of the same operation. Disagreement means the log timings are not comparable.
NEGATIVE CONTROL: the 15,488-call run must take ~5x the 3,168-call runs, since it is ~5x the
  work. A flat time would mean the number measures startup rather than throughput.
NOISE FLOOR: the three replicates, reported as observed spread.
MULTIPLICITY: 4 runs; all printed.
IMPOSSIBLE HERE: the generation half's true cost under batching -- generate_core.py decodes at
  max_new_tokens=110 and R540's decode figure is batch-1, so that half remains a LOWER bound.
"""
import json, pathlib, sys

# transcribed from `pueue log` -- (task, n_calls, seconds); the source of truth is the log itself
RUNS = [(634, 3168, 40.1), (635, 3168, 40.0), (636, 3168, 40.0), (642, 15488, 199.3)]
R540_TOK_S = 80.6          # 2B decode, batch 1
GEN_TOKENS = 110           # generate_core.py:147 max_new_tokens
N_PROMPTS, N_JUDGE = 968, 15472

def main():
    src = (pathlib.Path(__file__).resolve().parents[3] / "corebench/judge_core.py").read_text()
    no_gen = "generate(" not in src
    print(f"  SOURCE READ  judge_core.py contains no generate() call: {no_gen} -> "
          f"{'PASS' if no_gen else 'FAIL'}")
    if not no_gen:
        print("  the judge does decode after all; R540 may stand -> UNRUNNABLE"); return 2

    reps = [(n, s, n / s) for t, n, s in RUNS if n == 3168]
    rates = [r for _, _, r in reps]
    spread = (max(rates) - min(rates)) / (sum(rates) / len(rates))
    print(f"  POSITIVE CONTROL  three 3,168-call replicates agree: "
          f"{[round(r,1) for r in rates]} calls/s, spread {spread:.2%} -> "
          f"{'PASS' if spread < 0.05 else 'FAIL'}")
    if spread >= 0.05: return 0

    big = next((n, s) for t, n, s in RUNS if n == 15488)
    ratio_work, ratio_time = big[0] / 3168, big[1] / 40.0
    nc = abs(ratio_time - ratio_work) / ratio_work < 0.30
    print(f"  NEGATIVE CONTROL  {ratio_work:.2f}x the work must take ~that much longer: "
          f"{ratio_time:.2f}x -> {'PASS -- it is throughput, not startup' if nc else 'FAIL'}")
    if not nc: return 0

    judge_rate = big[0] / big[1]
    judge_s = N_JUDGE / judge_rate
    gen_s = N_PROMPTS * GEN_TOKENS / R540_TOK_S
    total_h = (judge_s + gen_s) / 3600
    r540_h = 16440 * 128 / R540_TOK_S / 3600
    factor = r540_h / total_h
    world = "A" if factor < 2 else "B"

    print(f"\n  measured judging rate: {judge_rate:.1f} calls/s "
          f"({big[0]} calls in {big[1]}s)")
    print(f"  ONE rows-3/4 round, corrected:")
    print(f"    judging    {N_JUDGE:>6} calls  ->  {judge_s/60:>7.1f} min   (measured operation)")
    print(f"    generation {N_PROMPTS:>6} prompts x {GEN_TOKENS} tok  ->  {gen_s/60:>7.1f} min"
          f"   (decode; R540's figure, correctly applied)")
    print(f"    TOTAL                          ->  {(judge_s+gen_s)/60:>7.1f} min")
    print(f"\n  R540 reported {r540_h:.2f} h. Corrected: {total_h*60:.1f} min. "
          f"Overstated {factor:.0f}x.")
    print(f"  WORLD {world} -- " +
          ("R540's conversion holds" if world == "A" else
           "R540 measured decode for an operation that does not decode -- the instrument's unit "
           "was tokens/sec, the claim's unit was judge-calls/sec, and they are not equal"))
    print(f"  ⭐ R540's decode number is NOT void: it is the right instrument for the GENERATION "
          f"half, which does decode. It was applied to the wrong half.")

    out = pathlib.Path(__file__).parent / "results/corrected_cost.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"runs": RUNS, "judge_calls_per_s": judge_rate,
                               "judge_minutes": judge_s/60, "gen_minutes": gen_s/60,
                               "total_minutes": (judge_s+gen_s)/60,
                               "r540_hours": r540_h, "overstatement_factor": factor,
                               "world": world}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
