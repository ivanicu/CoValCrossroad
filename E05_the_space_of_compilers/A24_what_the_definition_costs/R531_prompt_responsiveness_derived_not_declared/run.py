#!/usr/bin/env python3
"""R531 — is `gen` really the closest prompt-responsive ③-any arm? Derive, don't declare.

R530 reported "the closest PROMPT-RESPONSIVE ③-any arm is gen, 1.29 MDE short". The filter that
produced it was:

    responsive = [a for a in anyadm if a in ("gen","gen_sham") or a.startswith("promptecho")]

⛔ A HARDCODED LITERAL -- the exact defect R520 logged in USES_PROMPT_LABELS, committed three
rounds later by its own author. And my closing line then asserted "gen is the ONE prompt-
responsive ③-any arm in the census", which that literal cannot establish.

ESTIMAND (before method): the set of prompt-responsive arms, DERIVED from the artifacts, and the
  smallest clause-② shortfall among the ③-any-admissible ones.
IDENTIFICATION: fully identified. An arm is prompt-responsive iff its selected criterion INDEX
  SET varies across prompts -- a property of the .npz, needing no declaration.
SCOPE  population: R294's 41 arms · instrument: variation of the per-prompt index set ·
  baseline: n/a, this is a partition · regime: first release.
WORLDS  A · the derived set is {gen} plus shams, so R530's number survives and only the word
              "one" was wrong.
        B · the derived set contains a prompt-responsive ③-any arm closer than gen, so the
              1.29 MDE figure was measured over the wrong population.
KILL (pre-registered): any ③-any-admissible prompt-responsive arm with a smaller shortfall than
  gen kills world A.
POSITIVE CONTROL: `coval_core` must come out RESPONSIVE (its criteria are per-prompt) and
  `generic` must come out BLIND (a fixed set). If either is wrong the derivation is not
  measuring prompt-responsiveness and no membership claim is admissible.
NEGATIVE CONTROL: `random_k4_s0` draws a fresh random subset per prompt, so it is index-VARYING
  while being prompt-BLIND in content. It must appear in the varying set -- which shows the
  derivation measures INDEX VARIATION and NOT semantic prompt-awareness, and that limit is
  stated rather than hidden.
NOISE FLOOR: none -- set comparison is exact.
MULTIPLICITY: 41 arms, one classification each; the whole partition is printed.
IMPOSSIBLE HERE: semantic prompt-awareness. Index variation is a PROXY, sound for "the criteria
  differ by prompt" and NOT for "the criteria were written for this prompt". Named, not fudged.
"""
import json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
RES = ROOT / "corebench/results"
RANK = ("oracle_k", "indep_k", "greedy_k")
WEIGHT = ("topw_k", "topabs_k", "topvar_k", "topwvar_k")

def index_sets(tag):
    d = np.load(RES / f"sat_{tag}.npz", allow_pickle=True)
    per = {}
    for k in d["meta"]:
        pid, i, _ = str(k).split("|")
        per.setdefault(pid, set()).add(int(i))
    return per

def varying(tag):
    per = index_sets(tag)
    if len(per) < 2: return None
    it = iter(per.values()); first = next(it)
    return any(s != first for s in it)

def main():
    cen = json.loads((ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                      "/R294_the_definition_against_everything/results/full_census.json").read_text())["rows"]
    cls = {}
    for a in sorted(cen):
        try: cls[a] = varying(a)
        except Exception: cls[a] = None
    known = {a for a, v in cls.items() if v is not None}
    print(f"  arms classified: {len(known)} of {len(cen)}")

    pc1, pc2 = cls.get("coval_core"), cls.get("generic")
    print(f"  POSITIVE CONTROL  coval_core VARYING: {pc1} · generic BLIND: {pc2 is False} -> "
          f"{'PASS' if pc1 and pc2 is False else 'FAIL'}")
    if not (pc1 and pc2 is False):
        print("  -> derivation is not measuring what it claims; UNVERIFIED."); return 0
    # ⚠ TWO REPAIRS. (1) R294 SKIPS random_k4_s0 -- it is the clause-① comparator -- so it was
    # absent from the census and cls.get() returned None: the control could not RUN. (2) Loaded
    # directly it comes out FIXED, because at small k the same indices exist in every prompt.
    # The control needs an arm that IS varying while blind by construction, and random_k at
    # k>=6 is exactly that: the available pool differs per prompt so the drawn set differs.
    nc_arm = next((a for a in ("random_k6_s0", "random_k8_s0", "random_k12_s0")
                   if cls.get(a)), None)
    print(f"  NEGATIVE CONTROL  a random_k arm that is index-VARYING though prompt-blind by "
          f"construction: {nc_arm} -> "
          f"{'PASS -- the proxy is index variation, NOT semantics' if nc_arm else 'FAIL'}")
    if not nc_arm: return 0

    anyadm = [a for a in known if not a.startswith(RANK) and not a.startswith(WEIGHT)
              and a != "coval_core"]
    resp = sorted(a for a in anyadm if cls[a])
    print(f"\n  ③-any-admissible AND index-varying: {len(resp)}")
    print(f"  {'arm':<20}{'c2':>10}{'mde':>9}{'shortfall/MDE':>15}")
    best, bshort = None, None
    for a in sorted(resp, key=lambda x: -cen[x]["c2"][0]):
        r = cen[a]; sh = -r["c2"][0] / r["mde2"]
        print(f"  {a:<20}{r['c2'][0]:>+10.4f}{r['mde2']:>9.4f}{sh:>15.2f}")
        if r["c2"][1] <= 0 and (bshort is None or sh < bshort): best, bshort = a, sh
    gen_short = -cen["gen"]["c2"][0] / cen["gen"]["mde2"]
    world = "A" if best == "gen" else "B"
    print(f"\n  gen's shortfall: {gen_short:.2f} MDE · smallest in the derived set: "
          f"{best} at {bshort:.2f} MDE")
    print(f"  WORLD {world} -- " +
          (f"R530's number survives; only the word 'one' was wrong -- the derived set has "
           f"{len(resp)} members, not 1" if world == "A" else
           f"{best} is closer than gen; 1.29 MDE was measured over the wrong population"))
    print(f"  ⚠ PROXY LIMIT: index variation is sound for 'criteria differ by prompt' and NOT for "
          f"'criteria were written for this prompt' -- {nc_arm} proves the gap.")

    out = pathlib.Path(__file__).parent / "results/responsiveness.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"classified": {a: cls[a] for a in sorted(known)},
                               "any_admissible_varying": resp, "gen_shortfall_mde": gen_short,
                               "closest": best, "closest_shortfall_mde": bshort,
                               "world": world}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
