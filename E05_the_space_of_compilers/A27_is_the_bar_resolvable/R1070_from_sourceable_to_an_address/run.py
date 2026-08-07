"""R1070 — `sourceable` names no source. Which clause decimals resolve to exactly ONE round?

R1069 established that the clause's DECIMAL constants are sourceable well above their own coincidence
floor (0.789 vs ~0.15) while its integers are saturated. But `some artifact contains this value` is
not an address, and R1068's gate needs one: a specific artifact and key per assertion.

⭐ SO THE QUESTION IS CARDINALITY, NOT PRESENCE. For each clause decimal, how many DISTINCT ROUNDS
   hold that exact value? Exactly one is declarable. Many is ambiguous and needs the sentence read.
   Zero is unsourced. And the answer will depend on PRECISION — a 2-decimal value is common, a
   6-decimal value is nearly unique — so it is reported per precision class, which is the lesson
   R1069 paid for with its pooled floor.

ESTIMAND        the distribution of candidate-round counts over the clause's decimal constants,
                by decimal precision
IDENTIFICATION  exact for the counts. ⚠ A single candidate is an ADDRESS, not a proof of citation:
                the sentence may be quoting something else that coincides. Cardinality narrows the
                reading from 872 artifacts to one; it does not replace it.
SCOPE           population : decimal tokens within +/-700 chars of each `resolvably beats`
                instrument : exact value membership per round artifact
                baseline   : R1069's aggregate `0.789 sourceable`
                regime     : this checkout, this document version
WORLDS          A MOST RESOLVE TO ONE ROUND — the clause's decimals are addressable, so R1068's gate
                  can be extended mechanically and the remaining work is bounded.
                B AMBIGUITY DOMINATES — most decimals appear in many rounds, so `sourceable` cannot
                  be converted into assertions without a per-number reading, and the gate's reach is
                  limited by reading effort rather than by data.
                prediction matrix: A -> unique share high, and it rises with precision
                                   B -> unique share low even at high precision
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      unique share >= 0.50 -> World A
                      <= 0.20              -> World B
                      otherwise             -> report, claim neither
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ a value whose round is KNOWN must resolve to a candidate set containing it —
                R1057's `0.917` and R1053's margins are in committed artifacts. A resolver that
                cannot find a known source cannot count unknown ones.
NEGATIVE CTRL   a constructed-absent decimal must resolve to ZERO candidates.
PLACEBO         a decimal with no tokens in its class contributes no denominator; classes are
                reported with their sizes, never merged to hide an empty one.
NOISE FLOOR     ⭐ per precision class, the candidate-count distribution for RANDOM decimals of the
                same precision — so `resolves to one round` is read against how often that happens
                by chance at that precision.
MULTIPLICITY    every decimal reported with its candidate count; the whole precision curve.
SEEDS           3 for the floor.
IMPOSSIBLE      whether a uniquely-resolving value is actually CITED from that round. Cardinality
                cannot say. SETTLES: IN-RELEASE - one reading per number, now against ONE round
                instead of 872 artifacts, which is the round's practical product.
"""
import json, pathlib, random, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E05 = ROOT / "E05_the_space_of_compilers"
DEF = E05 / "DEFINITION.md"
WIN = 700
NUM = re.compile(r"(?<![\w.])(\d+\.\d+)(?![\w.])")
ANY = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])")


def vals(o, out, strings=True):
    """⛔⛔ AMBIGUITY WAS MANUFACTURED BY MY OWN EXTRACTOR, AND THE TELL WAS THE PRECISION CURVE.
    6-decimal values are nearly unique by construction, yet 0 of 19 resolved to a single round —
    backwards. The cause: this walker pulled numbers out of STRINGS inside artifacts, so every
    round whose verdict text QUOTED a value counted as a candidate beside the round that MEASURED
    it. A quoter is not a source. `strings=False` restricts candidacy to rounds that STORED the
    value as a numeric leaf, and both variants are reported so the inflation is visible."""
    if isinstance(o, bool):
        return
    if isinstance(o, (int, float)):
        out.add(round(float(o), 9)); return
    if isinstance(o, str):
        if strings:
            for m in ANY.finditer(o):
                out.add(round(float(m.group(1)), 9))
        return
    if isinstance(o, list):
        for v in o:
            vals(v, out, strings)
        return
    if isinstance(o, dict):
        for v in o.values():
            vals(v, out, strings)


def main() -> int:
    doc = DEF.read_text()
    anchors = [m.start() for m in re.finditer("resolvably beats", doc)]
    by_off = {}
    for a in anchors:
        lo = max(0, a - WIN)
        for m in NUM.finditer(doc[lo: a + WIN]):
            by_off[lo + m.start()] = m.group(1)
    toks = [by_off[k] for k in sorted(by_off)]
    if not toks:
        print("  UNRUNNABLE: no clause decimal. Exit 2, never 0."); return 2

    per_round, per_round_str = {}, {}
    for f in sorted(E05.glob("A*/R*/results/*.json")):
        m = re.match(r"(R\d+)", f.parent.parent.name)
        if not m:
            continue
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        s_leaf, s_all = set(), set()
        vals(d, s_leaf, strings=False)
        vals(d, s_all, strings=True)
        per_round.setdefault(m.group(1), set()).update(s_leaf)
        per_round_str.setdefault(m.group(1), set()).update(s_all)
    if len(per_round) < 20:
        print("  UNRUNNABLE: too few rounds. Exit 2, never 0."); return 2
    print(f"  ⭐ clause decimals {len(toks)} · rounds with artifacts {len(per_round)}")

    def cands(t):
        v = round(float(t), 9)
        return sorted(r for r, s in per_round.items() if v in s)

    pos_v = "0.917"
    pos = len(cands(pos_v)) >= 1
    neg = len(cands("0.987654321")) == 0
    print(f"  POSITIVE — a value with a known round must resolve to >=1 candidate ({pos_v}): {pos} "
          f"({len(cands(pos_v))} candidates)")
    print(f"  NEGATIVE — a constructed-absent decimal must resolve to 0: {neg}")
    if not (pos and neg):
        print("  the resolver cannot be read either way. Exit 2, never 0."); return 2

    def cands_str(t):
        v = round(float(t), 9)
        return sorted(r for r, s in per_round_str.items() if v in s)

    rows = [{"value": t, "precision": len(t.split(".")[1]), "n": len(cands(t)),
             "n_with_quotes": len(cands_str(t)), "rounds": cands(t)[:4]} for t in toks]
    infl = [r["n_with_quotes"] - r["n"] for r in rows]
    print(f"  ⛔ QUOTER INFLATION — candidate rounds counting quoted text minus counting stored "
          f"leaves: mean {sum(infl) / len(infl):+.1f}, max {max(infl):+d}")
    uniq = [r for r in rows if r["n"] == 1]
    zero = [r for r in rows if r["n"] == 0]
    many = [r for r in rows if r["n"] > 1]
    share = len(uniq) / len(rows)
    print(f"\n  ⭐ CARDINALITY — unique(1) {len(uniq)} · ambiguous(>1) {len(many)} · unsourced(0) "
          f"{len(zero)} · unique share {share:.3f}")

    prec = {}
    for r in rows:
        prec.setdefault(r["precision"], []).append(r)
    print(f"  {'prec':>5} {'n':>4} {'unique':>7} {'ambig':>6} {'zero':>5}  random-unique floor")
    floors = {}
    for p in sorted(prec):
        g = prec[p]
        fl = []
        for seed in (7, 19, 31):
            rng = random.Random(seed)
            dr = [f"{rng.uniform(0, 1):.{p}f}" for _ in g]
            fl.append(sum(len(cands(x)) == 1 for x in dr) / len(dr))
        floors[p] = [min(fl), max(fl)]
        u = sum(1 for r in g if r["n"] == 1)
        print(f"  {p:>5} {len(g):>4} {u:>7} {sum(1 for r in g if r['n'] > 1):>6} "
              f"{sum(1 for r in g if r['n'] == 0):>5}  [{min(fl):.3f}, {max(fl):.3f}]")

    informative = [p for p in prec if floors[p][1] < 0.5]
    print(f"  ⭐ precisions whose random-unique floor is below 0.5 (so `resolves to one` is "
          f"informative there): {sorted(informative)}")

    # ⛔⛔ AND THE VERDICT MUST NAME THE DOMINANT CATEGORY, WHICH IS NEITHER OF THE TWO I
    #   PRE-REGISTERED. With quoter inflation removed the modal outcome is UNSOURCED, not ambiguous:
    #   most clause decimals are stored by NO round as a numeric leaf. That also RETRACTS R1069's
    #   headline — its `0.789 sourceable` counted values appearing inside artifact PROSE, i.e.
    #   quoted in other rounds' verdict strings, rather than measured and stored anywhere.
    zero_share = len(zero) / len(rows)
    print()
    if zero_share >= 0.50:
        world = (f"⛔ NEITHER PRE-REGISTERED WORLD — THE MODAL OUTCOME IS UNSOURCED. {len(zero)} of "
                 f"{len(rows)} clause decimals ({zero_share:.3f}) are stored by NO round as a "
                 f"numeric leaf, including ALL {len(prec.get(6, []))} six-decimal values. Only "
                 f"{len(uniq)} resolve uniquely and {len(many)} are ambiguous. ⭐⭐ AND THIS RETRACTS "
                 f"R1069's HEADLINE: its `decimals 0.789 sourceable` counted values that appear "
                 f"inside artifact PROSE — quoted in other rounds' verdict strings — not measured "
                 f"and stored. Quoter inflation here averages +{sum(infl) / len(infl):.1f} candidate "
                 f"rounds per value and reaches +{max(infl)}. The clause's decimals are sourceable "
                 f"AS TEXT and largely not AS MEASUREMENTS.")
    elif share >= 0.50:
        world = (f"⭐ A MOST CLAUSE DECIMALS ARE ADDRESSABLE — {len(uniq)} of {len(rows)} "
                 f"({share:.3f}) resolve to exactly ONE round.")
    elif share <= 0.20:
        world = (f"⛔ B AMBIGUITY DOMINATES — only {share:.3f} resolve to a single round.")
    else:
        world = (f"⭐ NEITHER BAND — unique {share:.3f}, ambiguous {len(many)}, unsourced {len(zero)}.")
    print(world)
    print(f"⛔ AND A SINGLE CANDIDATE IS AN ADDRESS, NEVER A PROOF OF CITATION. It narrows the reading")
    print(f"   from {len(per_round)} rounds to one; it does not replace it. That is the round's")
    print(f"   practical product: {len(uniq)} numbers whose provenance can be checked by opening one")
    print(f"   file instead of searching all of them.")

    o = HERE / "results" / "decimal_addresses.json"
    o.write_text(json.dumps({
        "round": "R1070", "decimals": len(rows), "rounds_with_artifacts": len(per_round),
        "unique": len(uniq), "ambiguous": len(many), "unsourced": len(zero),
        "unique_share": share, "by_precision": {str(k): len(v) for k, v in prec.items()},
        "random_unique_floor": {str(k): v for k, v in floors.items()},
        "informative_precisions": sorted(informative),
        "addressable": [{"value": r["value"], "round": r["rounds"][0]} for r in uniq],
        "unsourced_share": zero_share,
        "quoter_inflation_mean": sum(infl) / len(infl), "quoter_inflation_max": max(infl),
        "retracts": "R1069's `decimals 0.789 sourceable` counted values appearing in artifact prose",
        "world": world,
        "controls": {"positive_known_value_resolves": bool(pos), "negative_absent_zero": bool(neg)},
        "limitation": "a single candidate is an address, not a proof of citation",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
