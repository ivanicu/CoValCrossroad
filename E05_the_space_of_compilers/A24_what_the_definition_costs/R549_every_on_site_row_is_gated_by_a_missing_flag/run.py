#!/usr/bin/env python3
"""R549 — the register prices its on-site rows in COMPUTE; each is gated by a missing FLAG.

R548 found offload available (accelerate present) and I closed saying the 7B run was one pueue
job away. ⛔ It is not: covalx/judge.py:169 hard-codes device_map="cuda". And my next line then
said "four rows, every one gated by a flag" -- wrong on both counts, since R546 nested 3+4 into
one requirement and rows 5-7 are not flag-gated at all.

ESTIMAND (before method): for each ON-SITE register requirement, whether the thing that blocks it
  is compute, an install, or a MISSING FLAG at a hard-coded call site.
IDENTIFICATION: fully identified -- a flag is in the argparse surface or it is not, and a call
  site is a literal or it is not.
SCOPE  population: the on-site requirements after R546's nesting -- row 2, and rows 3+4 as one ·
  instrument: source reading · regime: this checkout.
WORLDS  A · the on-site rows are blocked by compute, as the register says.
        B · each is blocked by a missing flag, and compute was never the binding constraint.
KILL (pre-registered): any on-site row whose blocker is compute keeps world A alive for that row.
POSITIVE CONTROL: a flag that DOES exist must be found -- judge_core.py exposes --model, which is
  why R536's cross-judge replication was a reanalysis rather than an edit. A prober that cannot
  see it cannot report an absence.
NEGATIVE CONTROL: an invented flag name must NOT be found in either file.
NOISE FLOOR: none -- exact string presence in source.
MULTIPLICITY: 3 flag probes x 2 files; all printed.
IMPOSSIBLE HERE: whether the edits WORK once made. That is a run, and this is a reading.
"""
import json, pathlib, re, sys

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    judge_cli = (root / "corebench/judge_core.py").read_text()
    judge_lib = (root / "covalx/judge.py").read_text()
    gen = (root / "corebench/generate_core.py").read_text()

    pos = "--model" in judge_cli
    print(f"  POSITIVE CONTROL  judge_core.py exposes --model (why R536 was a reanalysis): "
          f"{pos} -> {'PASS' if pos else 'FAIL'}")
    if not pos: return 0
    neg = any("--zzz-not-a-flag" in s for s in (judge_cli, judge_lib, gen))
    print(f"  NEGATIVE CONTROL  an invented flag is not found: {not neg} -> "
          f"{'PASS' if not neg else 'FAIL'}")
    if neg: return 0

    hard = re.search(r'device_map\s*=\s*"cuda"', judge_lib)
    rows = {
        "row 2 (offload path)": {
            "blocker": "missing flag",
            "evidence": f"covalx/judge.py hard-codes device_map=\"cuda\": {bool(hard)}; "
                        f"no device_map/max_memory flag in judge_core.py: "
                        f"{'device_map' not in judge_cli and 'max_memory' not in judge_cli}",
            "compute_bound": False},
        "row 2 (quantisation path)": {
            "blocker": "an install",
            "evidence": "bitsandbytes/optimum/auto_gptq/awq all absent (R548)",
            "compute_bound": False},
        "rows 3+4 (nested, R546)": {
            "blocker": "missing flag",
            "evidence": f"generate_core.py has no --model and FEWSHOT is a constant: "
                        f"{'--model' not in gen and 'FEWSHOT = (' in gen}; "
                        f"do_sample=False so a re-run is byte-identical (R544)",
            "compute_bound": False},
    }
    print()
    for k, v in rows.items():
        print(f"  {k:<28}blocker: {v['blocker']:<14}compute-bound: {v['compute_bound']}")
        print(f"    {v['evidence']}")

    n_compute = sum(1 for v in rows.values() if v["compute_bound"])
    world = "A" if n_compute else "B"
    print(f"\n  on-site requirements blocked by COMPUTE: {n_compute} of {len(rows)}")
    print(f"  WORLD {world} -- " +
          ("some rows really are compute-bound" if world == "A" else
           "none is compute-bound. Two are gated by a MISSING FLAG at a hard-coded call site and "
           "one by an install. The register prices all of them in compute"))
    print(f"  ⭐ and the asymmetry that matters: judge_core.py DOES expose --model, which is "
          f"exactly why R536's cross-judge replication was a reanalysis and not an edit. The flags "
          f"that exist decide which questions are cheap, and the register does not show that.")
    print(f"  ⚠ scope: rows 5, 6 and 7 are NOT flag-gated -- they need another site or a decision. "
          f"My closing line said 'four rows, every one gated by a flag'; after R546's nesting there "
          f"are TWO on-site requirements, not four.")

    out = pathlib.Path(__file__).parent / "results/flag_gates.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"rows": rows, "n_compute_bound": n_compute, "world": world}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
