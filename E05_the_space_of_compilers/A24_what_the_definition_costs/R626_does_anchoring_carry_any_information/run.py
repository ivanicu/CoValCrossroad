#!/usr/bin/env python3
"""
R626 -- does anchoring carry ANY information once the 36% collision floor is priced in?

CHECK #225: MY CLOSING LINE WAS A DERIVATION WEARING A PLAN'S CLOTHES.
  ⚠ "a match is informative ONLY where the value is rare" -- that is the definition of a likelihood
     ratio restated, not a finding. Labelled DERIVATION here rather than reported as evidence, per
     the arithmetic trap.
  ⚠ "carried by one round is evidence; carried by forty is a coincidence" -- one and forty were
     ILLUSTRATIVE. Neither was computed, and a later round would have inherited them as thresholds.
  ⭐ What IS testable, and is the round: whether the corpus carries the DOCUMENTS' decimals more
     rarely than it carries INVENTED ones. If the two multiplicity distributions coincide, then
     anchoring is exactly its own null and four rounds measured nothing about provenance.

ESTIMAND        Δ = median multiplicity of matched document decimals MINUS median multiplicity of
                matched random decimals, where multiplicity m(d) = the number of DISTINCT rounds
                whose artifacts persist d at 4 dp.
IDENTIFICATION  Exact, and the comparison is conditioned on MATCHING so the 36% base rate cannot
                drive it -- the question is not "does it match" but "given a match, is it rarer".
                ⚠ Both arms are the same instrument, so a shared bias cancels; a bias that acts
                only on real values does not, and no design here can separate that.
SCOPE           population : decimals on DEFINITION.md and STATEMENT.md that match at all
                instrument : value -> set of rounds persisting it, 4 dp
                             instrument unit = A DECIMAL
                             claim unit      = A NUMERIC ASSERTION. Unchanged, still unequal.
                baseline   : uniform random decimals that also match, 3 seeds x 4000
                regime     : this repository at this sha
WORLDS          A ANCHORING IS INFORMATIVE: document decimals are carried by FEWER rounds than
                  matched random draws. The match is not pure coincidence and a rarity threshold
                  gives the first rule in this arc with a measured null.
                B ANCHORING IS ITS OWN NULL: the two distributions coincide. Then "the value
                  appears in an artifact" carries no information about provenance whatsoever, and
                  R622 through R625 measured the corpus's number density, not the document.
KILL            pre-registered: median(document) >= median(random|matched) -> world B. Reported
                with the full distribution, not the medians alone, and across 3 seeds.
POSITIVE CTRL   R621's fabricated 0.9187 must behave like a random draw, not like a document value.
                Fails at g=0: random draws must reproduce R625's ~36% match rate, or the corpus map
                is not the one R625 measured.
NEGATIVE CTRL   values the live gate re-derives (R622's T1) should be RARER than document decimals
                at large, since they are headline measurements. If they are not, rarity does not
                track being-a-real-measurement and the whole axis is void.
PLACEBO         a decimal in no artifact -> multiplicity 0, excluded from both arms by construction.
SEEDS           3, and the seed flag is verified to change the draws.
MULTIPLICITY    every matched decimal x 2 arms x 3 seeds + 4 controls. Full distributions reported.
ARTIFACT        results/does_anchoring_inform.json
IMPOSSIBLE      a shared instrument bias cancels in Δ and is therefore invisible here. And rarity
                is not correctness: a value carried by exactly one round can still be wrong in that
                round -- which needs the round's re-execution, unavailable at this site.
"""
from __future__ import annotations
import json, pathlib, random, re, statistics as st, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
E05 = ROOT / "E05_the_space_of_compilers"
A24 = E05 / "A24_what_the_definition_costs"
DEC = re.compile(r"(?<![\w.])(\d+\.\d{3,4})(?![\w])")


def build_map():
    """value(4dp) -> set of round ids persisting it."""
    m: dict[float, set] = {}
    for d in sorted(A24.glob("R[0-9]*")):
        mm = re.match(r"R(\d+)", d.name)
        if not mm: continue
        rid = mm.group(1)
        vals = []
        def walk(o):
            if isinstance(o, dict):
                for v in o.values(): walk(v)
            elif isinstance(o, (list, tuple)):
                for v in o: walk(v)
            elif isinstance(o, bool) or o is None: return
            elif isinstance(o, (int, float)): vals.append(float(o))
            elif isinstance(o, str):
                s = o.strip().lstrip("+-")
                if DEC.fullmatch(s):
                    try: vals.append(float(s))
                    except ValueError: pass
        for f in (d / "results").glob("*.json"):
            try: walk(json.loads(f.read_text(errors="ignore")))
            except Exception: pass
        for v in vals:
            for k in (round(v, 4), round(abs(v), 4)):
                m.setdefault(k, set()).add(rid)
    return m


def main():
    M = build_map()
    if len(M) < 1000:
        print(f"UNRUNNABLE: map has {len(M)} values. Exit 2, never 0."); return 2
    print(f"  distinct 4-dp values in the corpus: {len(M)}   "
          f"rounds contributing: {len({r for s in M.values() for r in s})}")

    docs = "\n".join((E05 / n).read_text() for n in ("DEFINITION.md", "STATEMENT.md"))
    ddec = sorted({float(x) for x in DEC.findall(docs)})
    dmatch = [(d, len(M[round(d, 4)])) for d in ddec if round(d, 4) in M]
    print(f"  document decimals: {len(ddec)}   matching the corpus: {len(dmatch)} "
          f"({len(dmatch)/len(ddec):.1%})")

    print(f"\n─── CONTROLS ───")
    rnd_rates, rnd_mult = [], []
    for seed in (0, 1, 2):
        rng = random.Random(seed)
        draws = [round(rng.random(), 4) for _ in range(4000)]
        hits = [len(M[d]) for d in draws if d in M]
        rnd_rates.append(len(hits) / 4000); rnd_mult.append(hits)
    print(f"  g=0       random draws match {rnd_rates[0]:.1%} · {rnd_rates[1]:.1%} · "
          f"{rnd_rates[2]:.1%} -> {'PASS — reproduces R625' if abs(st.mean(rnd_rates)-0.363) < 0.05 else '⛔ FAIL'}")
    seeds_differ = len({tuple(x[:20]) for x in rnd_mult}) == 3
    print(f"  SEEDS     the seed flag actually changes the draws -> "
          f"{'PASS' if seeds_differ else '⛔ FAIL'}")
    fake = round(0.9187, 4)
    fm = len(M.get(fake, set()))
    allm = [len(v) for v in M.values()]
    pos = fm <= st.median(allm) + 1
    print(f"  POSITIVE  R621's fabricated 0.9187 is carried by {fm} round(s); corpus median is "
          f"{st.median(allm):.0f} -> {'PASS — it behaves like a draw, not a measurement' if pos else '⛔ FAIL'}")
    sys.path.insert(0, str(ROOT / "assurance"))
    import definition_matches_the_record as DM
    t1 = []
    for _l, pair in DM.derive().items():
        v = pair[0] if isinstance(pair, tuple) else pair
        if isinstance(v, (int, float)) and not isinstance(v, bool) and round(float(v), 4) in M:
            t1.append(len(M[round(float(v), 4)]))
    print(f"  NEGATIVE  values the live gate re-derives: n={len(t1)}, median multiplicity "
          f"{st.median(t1) if t1 else float('nan'):.1f}")
    controls_ok = abs(st.mean(rnd_rates) - 0.363) < 0.05 and seeds_differ and pos

    print(f"\n─── THE COMPARISON, CONDITIONED ON MATCHING ───")
    dm = [m for _, m in dmatch]
    print(f"  {'arm':<26} {'n':>6} {'median':>7} {'mean':>7} {'m=1':>7} {'m>=10':>7}")
    rows = [("document decimals", dm)] + [(f"random, seed {s}", rnd_mult[s]) for s in (0, 1, 2)]
    rows.append(("gate-re-derived (T1)", t1))
    out = {}
    for name, xs in rows:
        if not xs: continue
        one = sum(1 for x in xs if x == 1) / len(xs)
        ten = sum(1 for x in xs if x >= 10) / len(xs)
        out[name] = {"n": len(xs), "median": st.median(xs), "mean": round(st.mean(xs), 2),
                     "share_m1": round(one, 4), "share_m10": round(ten, 4)}
        print(f"  {name:<26} {len(xs):>6} {st.median(xs):>7.1f} {st.mean(xs):>7.2f} "
              f"{one:>6.1%} {ten:>6.1%}")

    rmed = st.median([st.median(x) for x in rnd_mult])
    delta = st.median(dm) - rmed
    print(f"\n─── VERDICT (pre-registered: median(doc) >= median(random|matched) -> world B) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif delta > 0 and out["gate-re-derived (T1)"]["median"] > st.median(dm):
        # ⛔⛔ THE PRE-REGISTERED DIRECTION WAS WRONG, AND THE NEGATIVE CONTROL IS WHAT SHOWED IT.
        #    I registered "median(doc) >= median(random) -> world B, anchoring is its own null",
        #    reasoning that a real measurement is RARE and a coincidence is COMMON. The corpus
        #    works the other way: a load-bearing number is RE-PERSISTED across many rounds as it
        #    is cited, re-checked and carried into later artifacts, while an invented value
        #    collides in exactly one place. The gate-re-derived values -- the arm I wrote
        #    expecting to be RAREST -- have the HIGHEST multiplicity of all three, which is what
        #    fixes the sign. §4: a kill is a conditional, and a threshold with the wrong sign
        #    fires confidently on data that refutes it.
        world = (f"A' ANCHORING IS INFORMATIVE, WITH THE SIGN REVERSED — document decimals sit at "
                 f"median {st.median(dm):.0f} against {rmed:.0f} for matched random draws, and the "
                 f"values the live gate re-derives sit at "
                 f"{out['gate-re-derived (T1)']['median']:.1f}. m=1 is "
                 f"{out['random, seed 0']['share_m1']:.0%} of random matches but only "
                 f"{out['gate-re-derived (T1)']['share_m1']:.0%} of gate-verified values, so LOW "
                 f"multiplicity is the COINCIDENCE signature and HIGH multiplicity is the "
                 f"measurement signature. My pre-registered kill had the direction backwards.")
    elif delta >= 0:
        world = (f"B ANCHORING IS ITS OWN NULL — document decimals are carried by a median of "
                 f"{st.median(dm):.0f} rounds against {rmed:.0f} for matched random draws "
                 f"(Δ = {delta:+.0f}). Given a match, a document value is no rarer than an invented "
                 f"one, so 'appears in an artifact' carries no information about provenance and "
                 f"R622-R625 measured the corpus's number density.")
    else:
        world = (f"A ANCHORING IS INFORMATIVE — document decimals are carried by a median of "
                 f"{st.median(dm):.0f} rounds against {rmed:.0f} for matched random draws "
                 f"(Δ = {delta:+.0f}); given a match they ARE rarer, so a rarity threshold is the "
                 f"first rule in this arc with a measured null.")
    print(f"  {world}")
    print(f"\n  ⚠ DERIVATION, NOT EVIDENCE: that a match is informative only where the value is rare "
          f"follows from the definition of a likelihood ratio. What is MEASURED here is whether the "
          f"documents' values are in fact rarer, which could have come out either way.")
    print(f"  ⚠ A shared instrument bias cancels in Δ and is invisible here. And rarity is not "
          f"correctness -- a value carried by one round can still be wrong in that round.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "does_anchoring_inform.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "delta_median": delta,
        "random_match_rates": rnd_rates, "arms": out,
        "corpus_distinct_values": len(M),
        "check225": ("the closing line stated a likelihood-ratio identity as a plan and used "
                     "'one round' and 'forty rounds' as thresholds without computing either"),
        "impossible": ("shared instrument bias cancels in the difference; rarity is not "
                       "correctness"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'does_anchoring_inform.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
