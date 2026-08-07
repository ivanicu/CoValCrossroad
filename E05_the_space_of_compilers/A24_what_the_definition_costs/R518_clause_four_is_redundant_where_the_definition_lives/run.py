#!/usr/bin/env python3
"""R518 — ④ at the home judge: redundant, or unresolvable?

R517 concluded ④'s independence "has never been observable" because in both populations a
marginal was degenerate. That is right for the second release and WRONG for home: at the home
judge ②'s marginal is 9, not 0, and the joint is computable from two files already on disk.
R517 also raised a wall -- "settling ④ needs a scoring run rather than a reanalysis" -- which
this round tests first, per the attack ladder.

ESTIMAND (before method): among arms that PASS ②, the margin by which each clears ④'s bar,
  expressed in units of its own MDE. That is what decides whether "④ excludes 0" is a
  measurement or a resolution limit.
IDENTIFICATION: fully identified on the join of R294's ② verdicts and R436's ④ scores.
SCOPE  population: the 41 arms carrying both · instrument: A2 vs the best criterion-free rule ·
  baseline: `min_ttr` at 0.4512 · regime: home judge J, 968 prompts.
WORLDS  A · the 0 is a RESOLUTION limit -- ②-passers sit near ④'s bar within their MDEs, so
              nothing can be concluded, and R517 stands.
        B · the 0 is a MEASUREMENT -- ②-passers clear ④'s bar by many MDEs, so ④ cannot
              exclude a ②-passer here and is redundant where the definition lives.
KILL (pre-registered): if any ②-passing arm's margin over ④'s bar is under 2x its MDE,
  world B dies and R517's UNVERIFIED stands.
POSITIVE CONTROL (on the wall, run FIRST): the join must be non-empty and ②'s marginal must be
  non-degenerate. If either fails, R517's reading was right and no scoring run is avoidable.
NEGATIVE CONTROL: the instrument must be able to place an arm BELOW ④'s bar. `promptecho_sham`
  sits at d = -0.0106, so the scale is not one-sided -- and its ② verdict is checked, because an
  arm below the bar that also fails ② cannot populate the informative cell either way.
NOISE FLOOR: each arm's own MDE, as computed by R436; margins reported as multiples of it.
MULTIPLICITY: 41 arms, one contrast each; BH was applied in R436 and its `bh` flag is carried.
IMPOSSIBLE HERE: the second release, where ② admits 0 of 7 so the cell is genuinely unidentified.
  Unchanged from R517 and restated, not quietly dropped.
"""
import glob, json, pathlib, sys

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    cen = json.loads((root / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                      "/R294_the_definition_against_everything/results/full_census.json").read_text())["rows"]
    r436 = json.loads(pathlib.Path(glob.glob(str(root/"E05_the_space_of_compilers/*/R436*/results/*.json"))[0]).read_text())
    atJ = {c["arm"]: c for c in r436["cells"] if not c["arm"].endswith(("_08b", "_08bR"))}
    common = sorted(set(cen) & set(atJ))

    # POSITIVE CONTROL on the wall -- run first
    n_pass2 = sum(1 for a in common if cen[a]["ok2"])
    wall_ok = len(common) > 5 and n_pass2 > 0
    print(f"  POSITIVE CONTROL (the wall)  join = {len(common)} arms, ② marginal = {n_pass2}")
    print(f"    -> {'the joint IS computable from disk; the wall is FALSE' if wall_ok else 'wall stands'}")
    if not common:
        print("  empty join -> UNRUNNABLE"); return 2

    # NEGATIVE CONTROL: can the scale place an arm below ④'s bar?
    below = [a for a in common if atJ[a]["d"] < 0]
    print(f"  NEGATIVE CONTROL  arms with a point estimate BELOW ④'s bar: {below}")
    for a in below:
        print(f"    {a}: d={atJ[a]['d']:+.4f} mde={atJ[a]['mde']:.4f} "
              f"|d|/mde={abs(atJ[a]['d'])/atJ[a]['mde']:.2f}  ②ok={cen[a]['ok2']}")
    print(f"    -> {'PASS -- the scale is two-sided' if below else 'FAIL -- one-sided scale'}")

    passers = [a for a in common if cen[a]["ok2"]]
    ratios = {a: atJ[a]["d"] / atJ[a]["mde"] for a in passers}
    lo = min(ratios.values()); hi = max(ratios.values())
    print(f"\n  among the {len(passers)} arms PASSING ②, margin over ④'s bar in MDE units:")
    for a in sorted(passers, key=lambda x: ratios[x]):
        print(f"    {a:<20}d={atJ[a]['d']:+.4f}  mde={atJ[a]['mde']:.4f}  {ratios[a]:>5.2f}x")
    world = "B" if lo >= 2.0 else "A"
    print(f"\n  smallest margin {lo:.2f}x MDE, largest {hi:.2f}x   (kill at <2.00x)")
    print(f"  WORLD {world} -- " +
          ("the zero is a MEASUREMENT: ④ cannot exclude a ②-passer at home, so it is "
           "REDUNDANT where the definition lives" if world == "B" else
           "the zero is a RESOLUTION limit; R517's UNVERIFIED stands"))

    out = pathlib.Path(__file__).parent / "results/clause4_at_home.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        "n_join": len(common), "n_pass2": n_pass2, "wall_false": bool(wall_ok),
        "below_bar": {a: {"d": atJ[a]["d"], "mde": atJ[a]["mde"], "ok2": cen[a]["ok2"]} for a in below},
        "margins_in_mde": ratios, "min_margin": lo, "max_margin": hi, "world": world,
        "second_release": "still unidentified -- ② admits 0 of 7 (R434)"}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
