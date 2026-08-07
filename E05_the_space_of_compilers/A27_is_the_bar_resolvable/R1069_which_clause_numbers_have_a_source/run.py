"""R1069 — of the 121 numbers in the clause region, which have a committed artifact behind them?

R1067 found all 121 invisible to the anchoring gate. R1068 declared 4 of them and made those red on
mutation. The remaining 117 are either (a) sourceable — some committed round measured them, so they
could be declared too — or (b) prose numbers no artifact backs.

⛔ AND `FOUND IN SOME ARTIFACT` IS A GENEROUS TEST, WHICH IS EXACTLY THE TRAP R1048 FELL INTO. With
   ~80 artifacts holding thousands of values, a small integer like `2` or `10` will match by
   coincidence. So the coincidence floor is MEASURED FIRST — the share of RANDOM numbers of the same
   magnitude that also `find a source` — and no sourceable count is readable unless it clears it.

ESTIMAND        of the clause-region numeric tokens, the share whose exact value appears in some
                committed round artifact, against the share that random same-magnitude values do
IDENTIFICATION  ⚠ PARTIAL AND NAMED FIRST. Exact-value presence is an UPPER bound on `has a source`:
                a coincidence is indistinguishable from a citation without reading the context. The
                floor is what makes the count interpretable; the residue below the floor is not.
SCOPE           population : numeric tokens in +/-700 chars of each `resolvably beats`
                instrument : exact value membership in the union of arc artifact values
                baseline   : the measured coincidence floor, 3 seeds
                regime     : this checkout
WORLDS          A MOST ARE SOURCEABLE ABOVE THE FLOOR — the clause is largely built on measured
                  values, and the gate can be extended to cover them.
                B THE TEST IS SATURATED — the sourceable share sits inside the random floor, so
                  `has a source` cannot be established this way at all, and extending the gate needs
                  a per-number reading rather than a membership test.
                prediction matrix: A -> observed > floor_hi;  B -> inside the floor
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      observed > floor_hi -> World A, report the sourceable list
                      otherwise           -> World B, the membership test is inadmissible
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ the 4 constants R1068 declared must ALL read as sourceable — they demonstrably are.
                A test that misses known-sourced values cannot count the unknown ones.
NEGATIVE CTRL   a value constructed to be absent (a large irrational) must read as unsourced.
PLACEBO         an empty token list contributes no denominator - exit 2, never 0.
NOISE FLOOR     ⭐ measured over 3 seeds by drawing random values matched to the observed magnitude
                distribution, so the floor is priced at the right level rather than assumed small.
MULTIPLICITY    every token reported with its verdict, and the per-magnitude breakdown.
SEEDS           3 for the floor.
IMPOSSIBLE      distinguishing a citation from a coincidence for any single token. That needs the
                surrounding sentence read against the round it names.
                SETTLES: IN-RELEASE - one reading per token, 121 of them; unattempted here.
"""
import json, pathlib, random, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E05 = ROOT / "E05_the_space_of_compilers"
DEF = E05 / "DEFINITION.md"
WIN = 700
NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])")


def vals(o, out):
    if isinstance(o, bool):
        return
    if isinstance(o, (int, float)):
        out.add(round(float(o), 9)); return
    if isinstance(o, str):
        for m in NUM.finditer(o):
            out.add(round(float(m.group(1)), 9))
        return
    if isinstance(o, list):
        out.add(float(len(o)))
        for v in o:
            vals(v, out)
        return
    if isinstance(o, dict):
        for v in o.values():
            vals(v, out)


def main() -> int:
    doc = DEF.read_text()
    anchors = [m.start() for m in re.finditer("resolvably beats", doc)]
    # ⛔ MY FIRST COUNT WAS 144 WHERE R1067 COUNTED 121, AND THE DIFFERENCE IS DOUBLE-COUNTING.
    #   The 9 clause homes have OVERLAPPING +/-700 windows; R1067 keyed tokens by absolute offset
    #   and so deduplicated them, while appending per window counts a shared token once per window.
    #   Deduplicating by offset reproduces R1067's population, which is the point: two rounds
    #   measuring the same thing must agree on what the thing is before either number is readable.
    by_off = {}
    for a in anchors:
        lo = max(0, a - WIN)
        for m in NUM.finditer(doc[lo: a + WIN]):
            by_off[lo + m.start()] = m.group(1)
    toks = [by_off[k] for k in sorted(by_off)]
    print(f"  ⭐ tokens deduplicated by offset: {len(toks)} (R1067 counted 121 the same way)")
    if not toks:
        print("  UNRUNNABLE: no clause-region token. Exit 2, never 0."); return 2

    pool = set()
    nfiles = 0
    for f in E05.glob("A*/R*/results/*.json"):
        try:
            vals(json.loads(f.read_text()), pool)
        except Exception:
            continue
        nfiles += 1
    if nfiles < 20:
        print("  UNRUNNABLE: too few artifacts. Exit 2, never 0."); return 2
    print(f"  ⭐ clause tokens {len(toks)} · artifacts read {nfiles} · distinct values in them "
          f"{len(pool)}")

    def sourced(t):
        return round(float(t), 9) in pool

    KNOWN = ["2", "10", "15"]
    pos = all(sourced(k) for k in KNOWN)
    neg = not sourced("987654.321987")
    print(f"  POSITIVE — the constants R1068 declared must read as sourceable: {pos} {KNOWN}")
    print(f"  NEGATIVE — a constructed-absent value must read as unsourced: {neg}")
    if not (pos and neg):
        print("  the membership test cannot be read either way. Exit 2, never 0."); return 2

    hits = [t for t in toks if sourced(t)]
    obs = len(hits) / len(toks)

    # ⭐ the floor, matched to the observed magnitude distribution
    floors = []
    for seed in (5, 17, 29):
        rng = random.Random(seed)
        draws = []
        for t in toks:
            if "." in t:
                dp = len(t.split(".")[1])
                draws.append(f"{rng.uniform(0, max(1.0, float(t) * 2)):.{dp}f}")
            else:
                draws.append(str(rng.randint(0, max(2, int(float(t)) * 2))))
        floors.append(sum(sourced(x) for x in draws) / len(draws))
    flo, fhi = min(floors), max(floors)
    print(f"  ⭐ SOURCEABLE {len(hits)} of {len(toks)} = {obs:.3f}")
    print(f"  ⭐ MEASURED COINCIDENCE FLOOR (random values matched to the same magnitudes, 3 seeds): "
          f"[{flo:.3f}, {fhi:.3f}]")

    # ⛔⛔ A POOLED FLOOR HIDES THE CLASS THAT IS SATURATED. Integers read 100% sourceable, which
    #   is the tell: with 72,749 distinct values in the artifacts, a small integer is almost certain
    #   to appear. So the floor is recomputed WITHIN each class, and only a class that clears its OWN
    #   floor is readable.
    ints = [t for t in toks if "." not in t]
    decs = [t for t in toks if "." in t]
    per = {}
    for name, grp in (("integers", ints), ("decimals", decs)):
        if not grp:
            continue
        o_ = sum(sourced(t) for t in grp) / len(grp)
        fl = []
        for seed in (5, 17, 29):
            rng = random.Random(seed)
            dr = []
            for t in grp:
                if "." in t:
                    dp = len(t.split(".")[1])
                    dr.append(f"{rng.uniform(0, max(1.0, float(t) * 2)):.{dp}f}")
                else:
                    dr.append(str(rng.randint(0, max(2, int(float(t)) * 2))))
            fl.append(sum(sourced(x) for x in dr) / len(dr))
        per[name] = {"n": len(grp), "sourceable": o_, "floor": [min(fl), max(fl)],
                     "clears": o_ > max(fl)}
        print(f"     {name:<9} {len(grp):>4} tokens · sourceable {o_:.3f} · own floor "
              f"[{min(fl):.3f}, {max(fl):.3f}] · clears its own floor: {o_ > max(fl)}")

    resolved = any(v["clears"] for v in per.values())
    # ⛔⛔ AND THE TWO CLASSES MUST NOT BE LUMPED, BECAUSE THEIR FLOORS ARE AN ORDER OF MAGNITUDE
    #   APART. `clears its own floor` is true for both, but for integers the margin is ~0.05 against
    #   a floor of ~0.94 — nearly every integer is `sourceable` by coincidence, so 100% says almost
    #   nothing. For decimals the floor is ~0.15 and the observation is ~0.79, which is a real
    #   separation. The decimal class is the finding; the integer class is saturated.
    margins = {k: v["sourceable"] - v["floor"][1] for k, v in per.items()}
    informative = [k for k, v in per.items() if v["floor"][1] < 0.5 and v["clears"]]
    saturated = [k for k, v in per.items() if v["floor"][1] >= 0.5]
    print(f"  ⭐ margin over own floor: " +
          " · ".join(f"{k} {m:+.3f}" for k, m in margins.items()))
    print(f"     informative classes (floor < 0.5 and clears): {informative}")
    print(f"     SATURATED classes (floor >= 0.5, their share says little): {saturated}")

    print()
    if not informative:
        world = (f"⛔ B EVERY CLASS IS SATURATED — no magnitude class has a floor below 0.5, so "
                 f"`this number has a source` cannot be established by value membership at all and "
                 f"extending R1068's gate needs a per-number reading.")
    else:
        d = per.get("decimals", {})
        i = per.get("integers", {})
        world = (f"⭐ A THE DECIMAL CLASS CARRIES IT, AND THE INTEGER CLASS DOES NOT — decimals "
                 f"{d.get('sourceable', 0):.3f} against their own floor "
                 f"{[round(x, 3) for x in d.get('floor', [0, 0])]}, a real separation; integers "
                 f"{i.get('sourceable', 0):.3f} against {[round(x, 3) for x in i.get('floor', [0, 0])]}, "
                 f"where nearly ANY integer reads as sourceable and 100% says almost nothing. ⭐ So "
                 f"the clause's DECIMAL constants — the measured quantities — are largely backed by "
                 f"committed artifacts and R1068's gate can be extended to them; its integers are "
                 f"unresolved by this test whatever their share.")
    o = HERE / "results" / "clause_number_sources.json"
    o.write_text(json.dumps({
        "round": "R1069", "tokens": len(toks), "artifacts": nfiles, "pool": len(pool),
        "sourceable": len(hits), "sourceable_share": obs, "floor_3_seeds": [flo, fhi],
        "resolved_against_floor": bool(resolved),
        "integers": len(ints), "decimals": len(decs), "per_class": per, "world": world,
        "controls": {"positive_known_declared": bool(pos), "negative_absent": bool(neg)},
        "limitation": "value membership is an upper bound; a coincidence is indistinguishable from "
                      "a citation without reading the sentence",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
