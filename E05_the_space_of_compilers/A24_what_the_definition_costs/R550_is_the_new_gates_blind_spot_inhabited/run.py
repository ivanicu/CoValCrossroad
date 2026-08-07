#!/usr/bin/env python3
"""R550 · Is the blind spot I declared in R549's NEXT line actually inhabited?

ESTIMAND  the share of round directories touched by >=2 distinct commits -- i.e. committed
          once and then MODIFIED, which is exactly what every_round_is_committed.py cannot see.
IDENT     fully identified: git log --follow-free path history over the whole repo.
SCOPE     population = every RNNN dir under ENN/ANN · instrument = git log --oneline -- <dir> ·
          baseline = 1 commit (write-once) · regime = this repo's whole history.
WORLDS    A write-once: rounds get one commit; the blind spot is EMPTY and the gate is complete.
          B amended: rounds are routinely revisited; the gate certifies staleness and must extend.
KILL      pre-registered: >=10% of rounds with >=2 commits -> WORLD B, the gate is insufficient.
          <10% -> WORLD A, and the NEXT line overstated a hazard.
POS CTRL  a path KNOWN to have many commits (assurance/) must return >=2. Else the counter is blind.
NEG CTRL  an invented path returns 0.
LIVE      separately: any tracked-but-DIRTY file inside a round dir right now -- the blind spot,
          observed rather than inferred.
ARTIFACT  results/blind_spot.json
"""
import json, pathlib, subprocess, collections

root = pathlib.Path(__file__).resolve().parents[3]
def sh(*a):
    return subprocess.run(a, cwd=root, capture_output=True, text=True).stdout

def ncommits(rel):
    out = sh("git", "log", "--oneline", "--", rel)
    return len([l for l in out.splitlines() if l.strip()])

rounds = sorted(p for p in root.glob("E*/A*/R*") if p.is_dir())
print(f"  population: {len(rounds)} round directories\n")

pc = ncommits("assurance")
nc = ncommits("E00_not_a_thing/A00_x/R000_y")
print(f"  POSITIVE CONTROL  a known-busy path (assurance/) has >=2 commits: {pc} -> {'PASS' if pc >= 2 else 'FAIL'}")
print(f"  NEGATIVE CONTROL  an invented path has 0 commits: {nc} -> {'PASS' if nc == 0 else 'FAIL'}")
if pc < 2 or nc != 0:
    raise SystemExit(2)

counts = {str(p.relative_to(root)): ncommits(str(p.relative_to(root))) for p in rounds}
hist = collections.Counter(counts.values())
amended = {k: v for k, v in counts.items() if v >= 2}
share = len(amended) / len(rounds)

print(f"\n  commits per round directory:")
for n in sorted(hist):
    print(f"    {n} commit(s): {hist[n]:4d} rounds")
print(f"\n  amended (>=2 commits): {len(amended)} of {len(rounds)} = {share:.1%}   [KILL at >=10%]")

# LIVE observation of the blind spot itself
dirty = [l for l in sh("git", "status", "--porcelain").splitlines()
         if any(l[3:].startswith(str(p.relative_to(root))) for p in rounds)]
print(f"  live blind spot: tracked-but-modified files inside round dirs RIGHT NOW: {len(dirty)}")
for d in dirty[:5]:
    print(f"    {d}")

world = "B" if share >= 0.10 else "A"
print(f"\n  WORLD {world} -- " + ("rounds ARE routinely amended; the gate certifies staleness."
      if world == "B" else "rounds are effectively write-once; the blind spot is nearly empty."))
if amended:
    top = sorted(amended.items(), key=lambda kv: -kv[1])[:4]
    print(f"  the amended ones, most-revisited first:")
    for k, v in top:
        print(f"    {v}x  {k.split('/')[-1]}")

(pathlib.Path(__file__).parent / "results" / "blind_spot.json").write_text(json.dumps(
    {"world": world, "n_rounds": len(rounds), "n_amended": len(amended), "share": share,
     "histogram": {str(k): v for k, v in sorted(hist.items())},
     "live_dirty_in_rounds": len(dirty), "amended": amended,
     "pos_ctrl_assurance_commits": pc, "neg_ctrl_invented": nc}, indent=2))
