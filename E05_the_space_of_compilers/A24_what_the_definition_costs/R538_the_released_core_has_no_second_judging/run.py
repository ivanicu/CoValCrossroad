#!/usr/bin/env python3
"""R538 — is there a second judging of the released core on disk, or is R537's gap real?

R537 closed naming a real limit: sat_coval_core_08b is absent, so the released core is the one
admitted arm whose position cannot be replicated across judges. My next line then said a STRONGER
judge "needs an install" -- the same shape as five walls already demolished this session, so it
gets checked before it is believed.

Two things to establish:
  (a) is a third judge family on disk at all?
  (b) sat_coval_core_2bA / _2bB exist, and R524 put them in a duplicate class that did NOT
      contain coval_core. If they are a different JUDGING of the released core, R537's gap is
      partly fillable. If they are the same judging on a subsample, it is not.

ESTIMAND (before method): (a) the count of distinct judge families among the artifacts, and
  (b) the number of shared (prompt, criterion, response) cells on which coval_core_2bA differs
  from coval_core.
IDENTIFICATION: fully identified -- the .npz files are the objects.
SCOPE  population: every saturation artifact in corebench/results · instrument: exact cell
  comparison on the SHARED prompts · regime: first release.
WORLDS  A · 2bA is a different judging -> R537's gap is partly fillable from disk.
        B · 2bA is the same judging on a subsample -> the gap is real, and R524's "no documented
              prediction either way" for that duplicate class is resolved: identity is correct.
KILL (pre-registered): any differing shared cell kills world B.
POSITIVE CONTROL: the comparison must be able to find differences -- coval_core vs coval_core_sham
  on shared prompts must differ. Otherwise a zero says nothing.
NEGATIVE CONTROL: coval_core against ITSELF on the shared prompts must give exactly 0 differing
  cells, so the comparison does not manufacture agreement or disagreement.
NOISE FLOOR: none -- exact cell equality.
MULTIPLICITY: 1 family scan + 2 arm comparisons; all printed.
IMPOSSIBLE HERE: a judge stronger than the home 2B. No _7b or qwen artifact exists, so that wall
  SURVIVES being checked -- the first this session to do so on a second look.
"""
import json, pathlib, sys

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(root / "corebench"))
    from score import load_sat
    RES = root / "corebench/results"

    fams = {"2B (sat_*)": len(list(RES.glob("sat_*.npz"))),
            "0.8B judging (sat08_*)": len(list(RES.glob("sat08_*.npz"))),
            "0.8B arms (*_08b)": len(list(RES.glob("*_08b.npz"))),
            "7B (*_7b*)": len(list(RES.glob("*_7b*.npz"))),
            "qwen-tagged": len(list(RES.glob("*qwen*")))}
    print("  judge families among the artifacts:")
    for k, v in fams.items(): print(f"    {k:<26}{v:>4}")
    third = fams["7B (*_7b*)"] + fams["qwen-tagged"]
    print(f"  ⭐ a judge STRONGER than home on disk: {third} -> "
          f"{'the wall SURVIVES' if third == 0 else 'the wall is FALSE'}")

    C = load_sat(RES / "sat_coval_core.npz")
    A = load_sat(RES / "sat_coval_core_2bA.npz")
    S = load_sat(RES / "sat_coval_core_sham.npz")
    common = sorted(set(A) & set(C))
    if not common:
        print("  empty overlap -> UNRUNNABLE"); return 2

    pos = [p for p in common if S.get(p) != C[p]]
    print(f"\n  POSITIVE CONTROL  the comparison can find differences "
          f"(coval_core vs its sham on {len(common)} shared prompts): "
          f"{len(pos)} differ -> {'PASS' if pos else 'FAIL'}")
    neg = [p for p in common if C[p] != C[p]]
    print(f"  NEGATIVE CONTROL  coval_core against itself: {len(neg)} differ -> "
          f"{'PASS' if not neg else 'FAIL'}")
    if not pos: return 0

    diff = [p for p in common if A[p] != C[p]]
    world = "A" if diff else "B"
    print(f"\n  coval_core_2bA: {len(A)} prompts · coval_core: {len(C)} · shared: {len(common)}")
    print(f"  ⭐ shared prompts whose cells DIFFER: {len(diff)} of {len(common)}")
    print(f"  WORLD {world} -- " +
          ("2bA is a DIFFERENT judging; R537's gap is partly fillable"
           if world == "A" else
           "2bA is the SAME judging on a 200-prompt subsample -- R537's gap is REAL, and "
           "R524's undocumented duplicate class is resolved: identity is the correct outcome"))

    out = pathlib.Path(__file__).parent / "results/second_judging.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"families": fams, "third_judge_artifacts": third,
                               "n_2bA": len(A), "n_core": len(C), "n_shared": len(common),
                               "n_differing": len(diff), "world": world}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
