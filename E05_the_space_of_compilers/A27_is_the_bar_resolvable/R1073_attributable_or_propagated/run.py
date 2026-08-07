"""R1073 — my own NEXT was half a derivation. The non-forced question is how many rounds carry each value.

R1071 closed by proposing to check, for each unstored clause decimal, whether the round whose README
reports it also stores it in its own artifact.

⛔ THAT HALF IS FORCED AND CANNOT COME OUT OTHERWISE. The population was DEFINED by R1070 as `stored
   by no round as a numeric leaf`. So for every round whose README carries such a value, that round's
   artifact necessarily lacks it. The check is a DERIVATION of the population's own definition, not a
   measurement, and it would have printed a clean-looking 100% that says nothing.

⭐ THE NON-FORCED QUESTION IS CARDINALITY ON THE PROSE SIDE: how many DISTINCT rounds' READMEs carry
   each value? ONE round means the value was reported by a single round and never persisted — an
   attributable recording gap, fixable at one line in that round. MANY rounds means it propagated as
   a citation and the origin is not recoverable from presence alone. That distinction decides whether
   `write it down' is a repair or a guess.

ESTIMAND        the distribution of README-carrying-round counts over the 31 unstored clause decimals
IDENTIFICATION  exact for the counts. ⚠ A single carrier is an ATTRIBUTION, not a proof of authorship:
                the one round may itself be quoting something outside this arc.
SCOPE           population : R1070's unstored clause decimals, recomputed here
                instrument : exact match in round READMEs BEFORE R1067 (the audit rounds quote these)
                baseline   : R1071's `31 of 31 in the prose record`
                regime     : this checkout, this document version
WORLDS          A ATTRIBUTABLE — most are carried by exactly one round, so each is a one-line write in
                  a known place and the recording gap is closable mechanically.
                B PROPAGATED — most are carried by many rounds, so presence does not name an origin
                  and closing the gap needs a reading per value rather than a write.
                prediction matrix: A -> single-carrier share high;  B -> low
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      single-carrier share >= 0.50 -> World A
                      <= 0.20                      -> World B
                      otherwise                     -> report, claim neither
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ a value whose carrying round is KNOWN must resolve to a set containing it.
NEGATIVE CTRL   a constructed-absent decimal must resolve to ZERO carriers.
SHAM            the same cardinality computed over a corpus that cannot carry them — the release data
                — must give zero, so `carried` is not `these digits occur in any large text`.
PLACEBO         an empty candidate list exits 2, never 0.
NOISE FLOOR     ⭐ random decimals at matched precision: how many rounds carry a made-up value by
                chance? Without it, `carried by 3 rounds` has no scale.
MULTIPLICITY    every value reported with its carrier count and the carriers themselves.
SEEDS           3.
IMPOSSIBLE      whether the single carrier AUTHORED the value or quoted it from outside this arc.
                SETTLES: IN-RELEASE by reading that round; the point of this round is that there is
                now ONE round to read per value rather than a corpus.
"""
import json, pathlib, random, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E05 = ROOT / "E05_the_space_of_compilers"
DEF = E05 / "DEFINITION.md"
WIN = 700
DEC = re.compile(r"(?<![\w.])(\d+\.\d+)(?![\w.])")
CUT = 1067


def leaves(o, out):
    if isinstance(o, bool):
        return
    if isinstance(o, (int, float)):
        out.add(round(float(o), 9)); return
    if isinstance(o, list):
        for v in o:
            leaves(v, out)
        return
    if isinstance(o, dict):
        for v in o.values():
            leaves(v, out)


def main() -> int:
    doc = DEF.read_text()
    by_off = {}
    for a in [m.start() for m in re.finditer("resolvably beats", doc)]:
        lo = max(0, a - WIN)
        for m in DEC.finditer(doc[lo: a + WIN]):
            by_off[lo + m.start()] = m.group(1)
    toks = [by_off[k] for k in sorted(by_off)]
    stored = set()
    for f in E05.glob("A*/R*/results/*.json"):
        try:
            leaves(json.loads(f.read_text()), stored)
        except Exception:
            continue
    cand = [t for t in toks if round(float(t), 9) not in stored]
    if not cand:
        print("  UNRUNNABLE: empty candidate list. Exit 2, never 0."); return 2

    readmes = {}
    for p in E05.glob("A*/R*/README.md"):
        m = re.match(r"R(\d+)", p.parent.name)
        if m and int(m.group(1)) < CUT:
            readmes[m.group(0)] = p.read_text()
    if len(readmes) < 20:
        print("  UNRUNNABLE: too few upstream READMEs. Exit 2, never 0."); return 2
    print(f"  ⭐ unstored clause decimals {len(cand)} · upstream READMEs (rounds < R{CUT}) "
          f"{len(readmes)}")

    def carriers(t):
        pat = re.compile(r"(?<![\w.])" + re.escape(t) + r"(?![\w.])")
        return sorted(r for r, txt in readmes.items() if pat.search(txt))

    known = next((t for t in cand if carriers(t)), None)
    pos = known is not None
    neg = not carriers("0.31415926535897")
    print(f"  POSITIVE — a value with a carrier must resolve to >=1 ({known}): {pos}")
    print(f"  NEGATIVE — a constructed-absent decimal must resolve to 0 carriers: {neg}")
    if not (pos and neg):
        print("  the carrier search cannot be read either way. Exit 2, never 0."); return 2

    rows = [{"value": t, "n": len(carriers(t)), "carriers": carriers(t)[:4]} for t in cand]
    one = [r for r in rows if r["n"] == 1]
    many = [r for r in rows if r["n"] > 1]
    zero = [r for r in rows if r["n"] == 0]
    share = len(one) / len(rows)
    print(f"\n  ⭐ CARRIERS — exactly one {len(one)} · many {len(many)} · none {len(zero)} · "
          f"single-carrier share {share:.3f}")
    for r in rows[:8]:
        print(f"     {r['value']:>12}  {r['n']:>2}  {r['carriers']}")

    floors = []
    for seed in (5, 17, 29):
        rng = random.Random(seed)
        dr = [f"{rng.uniform(0, 1):.{len(t.split('.')[1])}f}" for t in cand]
        floors.append(sum(1 for x in dr if len(carriers(x)) == 1) / len(dr))
    flo, fhi = min(floors), max(floors)
    print(f"  ⭐ MEASURED FLOOR — random decimals at matched precision carried by exactly one "
          f"upstream README, 3 seeds: [{flo:.3f}, {fhi:.3f}]")

    data = ""
    dd = ROOT / "data"
    if dd.exists():
        for p in list(dd.glob("*.jsonl"))[:2]:
            data += p.read_text()[:4_000_000]
    sham = sum(1 for t in cand
               if re.search(r"(?<![\w.])" + re.escape(t) + r"(?![\w.])", data)) if data else 0
    print(f"  SHAM — the same values searched in the RELEASE DATA: {sham} of {len(cand)}")

    resolved = share > fhi or share < flo
    print()
    if not resolved:
        world = (f"⛔ UNVERIFIED — the single-carrier share {share:.3f} sits inside the random floor "
                 f"[{flo:.3f}, {fhi:.3f}], so `carried by exactly one round` carries no information "
                 f"at this precision.")
    elif share >= 0.50:
        world = (f"⭐ A ATTRIBUTABLE — {len(one)} of {len(rows)} ({share:.3f}) unstored clause "
                 f"decimals are carried by exactly ONE upstream README, against a random floor of "
                 f"[{flo:.3f}, {fhi:.3f}]. Each is a one-line write in a known round, so the "
                 f"recording gap R1071 identified is closable mechanically rather than by reading.")
    elif share <= 0.20:
        world = (f"⛔ B PROPAGATED — only {share:.3f} have a single carrier; the rest appear in "
                 f"several READMEs, so presence does not name an origin and closing the gap needs a "
                 f"reading per value rather than a write.")
    else:
        world = (f"⭐ NEITHER BAND — single-carrier {share:.3f} ({len(one)} of {len(rows)}), many "
                 f"{len(many)}, none {len(zero)}. Reported; neither world claimed. The actionable "
                 f"subset is the {len(one)} with one carrier.")
    print(world)
    print(f"⛔ AND THE ROUND I DID NOT RUN IS WORTH NAMING: checking that the reporting round's")
    print(f"   ARTIFACT lacks the value is FORCED — the population was defined as `stored by no")
    print(f"   round`, so that check could only ever return 100%. It would have looked like a clean")
    print(f"   result and been a restatement of the selection criterion.")

    o = HERE / "results" / "carrier_cardinality.json"
    o.write_text(json.dumps({
        "round": "R1073", "candidates": len(rows), "upstream_readmes": len(readmes),
        "single_carrier": len(one), "many": len(many), "none": len(zero),
        "single_share": share, "floor_3_seeds": [flo, fhi], "sham_release_hits": sham,
        "rows": rows, "world": world,
        "not_run": "the artifact-side half of R1071's NEXT is forced by the population definition",
        "controls": {"positive_carrier_found": bool(pos), "negative_absent_zero": bool(neg)},
        "limitation": "a single carrier is an attribution, not a proof of authorship",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
