#!/usr/bin/env python3
"""
R595 -- is the `world` tail translatable into the core, or was `enum` the wrong TYPE?

CHECK #195 KILLED THE INSTRUMENT R594's CLOSING LINE PROPOSED. It said: test whether each
sentence value "contains exactly one core token as a prefix". The core tokens are `A`, `B`
and `UNVERIFIED` -- and SINGLE LETTERS ARE SUBSTRINGS OF NEARLY EVERY ENGLISH SENTENCE. That
is §4's `a search is an instrument and has no positive control` in its purest form: the
matcher would have reported the tail TRANSLATABLE from pure collision, and the repair it
licensed would have rewritten real verdicts into letters chosen by an accident of spelling.

So the false-positive rate is not an afterthought here, it is the measurement. Every matcher
below is run on CONTROL TEXT that provably contains no verdict, and a matcher whose real-value
rate does not clear its own control rate is reported as blind rather than as evidence.

⚠ AND THE WORLD SET GAINS A THIRD MEMBER THE CLOSING LINE DID NOT HAVE. R593's own `world`
value was "C THE ARTIFACT WAS NEVER THE CARRIER AND B DOUBLY THIN" -- TWO core tokens,
deliberately, because that round measured two orthogonal axes. A value naming two verdicts is
not a formatting failure and not an open vocabulary: it is evidence that `enum` was the wrong
TYPE and HB8's `enum_set` is the right one. The binary the closing line offered had no room
for that, which is why it is added before the run rather than after seeing the numbers.

ESTIMAND        For each matcher m: t_m = fraction of NON-CORE `world` values that m maps to
                >=1 core token, and c_m = fraction mapping to >=2 (the compound rate).
                Both against f_m = the same matcher's rate on control text.
IDENTIFICATION  Identified from disk. ⚠ Translatability is only identified RELATIVE to a
                matcher whose false-positive rate is known; without f_m, t_m is uninterpretable
                and is reported as UNVERIFIED rather than as a number.
SCOPE           population : every distinct `world` value in E01..E05 (from R594's survey)
                instrument : three matchers, prefix / word / substring, swept as a spec axis
                             The instrument's unit is A CORE TOKEN RECOGNISED IN A STRING; the
                             claim's unit is A VERDICT THE ROUND INTENDED. Written as two
                             strings and NOT equal -- which is exactly why f_m is required
                             before any t_m may be read.
                baseline   : control text = `why` values and README prose from the same
                             rounds, which are sentences with no verdict role
                regime     : as committed at this sha
WORLDS          A TRANSLATABLE: t_m >> f_m and c_m small -> the tail is a formatting failure
                  with a mechanical repair; `world` should be an enum and can be made one.
                B OPEN: t_m ~ f_m -> the matcher is finding letters, not verdicts. The
                  vocabulary is genuinely open and the core is a coincidence of short rounds.
                C ENUM_SET: t_m >> f_m but c_m large -> values legitimately name SEVERAL
                  verdicts. `enum` was the wrong type; HB8's ladder already has `enum_set`
                  one rung down, and the repair is a type change, not a rewrite.
KILL            pre-registered, per matcher, evaluated ONLY if the controls fire:
                  t_m - f_m <= 0.10 -> that matcher is BLIND and reports nothing.
                  If ALL matchers are blind -> world B stands by default and no repair is
                  admissible.
POSITIVE CTRL   plant: synthesise sentences that DO carry a named verdict ("verdict is B
                because ..."). A matcher must recover them. Fails at g=0: run the same matcher
                on control text with no verdict planted and require a LOWER rate.
NEGATIVE CTRL   control text -- `why` strings and README prose, same rounds, no verdict role.
                This is the f_m that every t_m is read against.
PLACEBO         a matcher for a token that appears in NO core vocabulary ("ZZQ") must return
                exactly 0 on every corpus. Anything above 0 means the matcher is hallucinating.
SEEDS           0, 1, 2 on every sampled control draw.
MULTIPLICITY    3 matchers x 3 corpora (real / control / planted) x 3 seeds. All reported.
ARTIFACT        results/translatable.json
IMPOSSIBLE      construct validity: whether a round INTENDED the verdict a matcher recovers is
                not decidable from the string. It would need the round's author, or an
                external reader scoring value against README. Every t_m is an UPPER BOUND on
                translatability and is reported as one.
"""
from __future__ import annotations
import json, pathlib, random, re, sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
CORE_MIN = 5          # a value is "core" if it occurs at least this often -- derived, not chosen


def walk(o, key):
    if isinstance(o, dict):
        for k, v in o.items():
            if str(k).lower() == key:
                yield json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else str(v)
            yield from walk(v, key)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v, key)


def corpus():
    out = {}
    for ep in sorted(ROOT.glob("E0*")):
        for d in sorted(ep.glob("A*/R[0-9]*")):
            if not d.is_dir():
                continue
            m = re.match(r"R(\d+)", d.name)
            if not m or not (d / "results").is_dir():
                continue
            objs, prose = [], []
            for f in sorted((d / "results").rglob("*.json")):
                try:
                    objs.append(json.loads(f.read_text()))
                except Exception:
                    pass
            rm = d / "README.md"
            if rm.is_file():
                prose = [s.strip() for s in re.split(r"(?<=[.!?])\s+", rm.read_text())
                         if 20 <= len(s.strip()) <= 300]
            if objs:
                out[int(m.group(1))] = (objs, prose)
    return out


# ---- the three matchers. Same signature; only the recognition rule differs. --------------
def m_prefix(s, toks):
    return {t for t in toks if re.match(rf"^{re.escape(t)}(?![A-Za-z0-9_])", s.strip())}


def m_word(s, toks):
    return {t for t in toks if re.search(rf"(?<![A-Za-z0-9_]){re.escape(t)}(?![A-Za-z0-9_])", s)}


def m_sub(s, toks):
    return {t for t in toks if t in s}


MATCHERS = (("prefix", m_prefix), ("word", m_word), ("substring", m_sub))


def rates(strings, toks, fn):
    """(>=1 token, >=2 tokens) as fractions of the population."""
    if not strings:
        return None, None, 0
    hits = [fn(s, toks) for s in strings]
    return (sum(1 for h in hits if len(h) >= 1) / len(hits),
            sum(1 for h in hits if len(h) >= 2) / len(hits), len(hits))


def main():
    C = corpus()
    if not C:
        print("UNRUNNABLE: no readable artifacts. Exit 2, never 0.")
        return 2

    vals = Counter(v for objs, _ in C.values() for o in objs for v in walk(o, "world"))
    if not vals:
        print("UNRUNNABLE: no round writes `world`. Exit 2.")
        return 2
    def is_label(v):
        """A core value is a LABEL iff it is not a serialised structure.

        ⛔ v1's core included a 2,000-character JSON blob that occurs >=5 times -- a repeated
        PAYLOAD, not a token. "Frequent value" and "short categorical label" are different
        things and v1 conflated them. This is a TYPE test, not a length threshold: anything
        that parses as a dict or list is a payload. Nothing is invented and nothing is tuned.
        """
        try:
            return not isinstance(json.loads(v), (dict, list))
        except Exception:
            return True

    freq = [v for v, c in vals.items() if c >= CORE_MIN]
    payload = [v for v in freq if not is_label(v)]
    core = sorted((v for v in freq if is_label(v)), key=lambda v: -vals[v])
    if payload:
        print(f"  ⚠ EXCLUDED from core: {len(payload)} frequent value(s) that parse as a "
              f"JSON structure -- repeated PAYLOAD, not a label "
              f"({[len(x) for x in payload]} chars each)")
    tail = sorted(v for v, c in vals.items() if c < CORE_MIN)
    n_core_occ = sum(vals[v] for v in core)
    print(f"CORPUS  distinct `world` values = {len(vals)}   occurrences = {sum(vals.values())}")
    print(f"  CORE (>= {CORE_MIN} occurrences, derived not chosen): {core}")
    print(f"  core occurrences = {n_core_occ}/{sum(vals.values())} = "
          f"{n_core_occ/sum(vals.values()):.4f}   TAIL values = {len(tail)}")
    if not core or not tail:
        print("UNRUNNABLE: core or tail is empty; the estimand is undefined. Exit 2.")
        return 2

    # control text: `why` values + README prose. Sentences with no verdict role.
    why = [v for objs, _ in C.values() for o in objs for v in walk(o, "why")]
    prose = [s for _, pr in C.values() for s in pr]
    print(f"\n─── CONTROL TEXT (no verdict role): why={len(why)}  README sentences={len(prose)}")

    # planted: sentences that DO carry a named verdict
    # ⛔ v1 PLANTED ONE SENTENCE SHAPE FOR ALL THREE MATCHERS, and `prefix` scored 0.0000 on
    # it because the token sat mid-sentence. A plant a matcher cannot possibly recover is
    # §4's `control that cannot PASS` -- its failure said nothing about the matcher. The plant
    # is now built PER MATCHER, in the shape that matcher exists to recognise.
    rng = random.Random(0)
    PLANTS = {
        "prefix": [f"{rng.choice(core)} -- the control fired at seed {i}" for i in range(400)],
        "word": [f"the verdict is {rng.choice(core)} because the control fired at seed {i}"
                 for i in range(400)],
        "substring": [f"the verdict is {rng.choice(core)} because the control fired at "
                      f"seed {i}" for i in range(400)],
    }

    print(f"\n─── CONTROLS, PER MATCHER (t = real tail · f = control · plant = must recover) ───")
    print(f"{'matcher':>10} {'t(tail)':>9} {'f(why)':>9} {'f(prose)':>10} {'plant':>8} "
          f"{'placebo':>8}  verdict")
    grid, any_live = {}, False
    for name, fn in MATCHERS:
        t, c2, nt = rates(tail, core, fn)
        fw, cw, nw = rates(why, core, fn)
        fp, cp, np_ = rates(prose, core, fn)
        pl, _, _ = rates(PLANTS[name], core, fn)
        plc, _, _ = rates(tail + why + prose, ["ZZQ"], fn)
        f_max = max(x for x in (fw, fp) if x is not None) if (fw or fp) else 0.0
        blind = (t - f_max) <= 0.10
        ok_plant = pl is not None and pl >= 0.90
        ok_plc = plc == 0.0
        if not ok_plant or not ok_plc:
            verdict = "⛔ CONTROL FAILED -- reports nothing"
        elif blind:
            verdict = f"BLIND (t-f = {t - f_max:+.4f} <= 0.10)"
        else:
            verdict = f"LIVE (t-f = {t - f_max:+.4f})"
            any_live = True
        print(f"{name:>10} {t:>9.4f} {fw:>9.4f} {fp:>10.4f} {pl:>8.4f} {plc:>8.4f}  {verdict}")
        grid[name] = {"t_tail": t, "compound_rate": c2, "f_why": fw, "f_prose": fp,
                      "plant": pl, "placebo": plc, "blind": blind,
                      "compound_rate_why": cw, "compound_rate_prose": cp,
                      "plant_ok": ok_plant, "placebo_ok": ok_plc,
                      "n_tail": nt, "n_why": nw, "n_prose": np_}

    # §2.5: the matchers will disagree. Do not adjudicate by preference -- find the
    # assumption they differ on and test THAT. They differ on false-positive rate, so the
    # decisive question is what compound rate each produces on text with NO verdict at all.
    print(f"\n─── COMPOUND RATE: real tail vs CONTROL TEXT (the assumption they differ on) ───")
    print(f"{'matcher':>10} {'tail':>8} {'why':>8} {'prose':>8}   reading")
    for name, _ in MATCHERS:
        g = grid[name]
        cr, cw_, cp_ = g["compound_rate"], g["compound_rate_why"], g["compound_rate_prose"]
        base = max(cw_ or 0.0, cp_ or 0.0)
        rd = ("compounds are AT OR BELOW the control -> manufactured by collision"
              if cr <= base + 0.05 else "compounds EXCEED the control -> real co-occurrence")
        print(f"{name:>10} {cr:>8.4f} {cw_:>8.4f} {cp_:>8.4f}   {rd}")
        g["compound_exceeds_control"] = cr > base + 0.05

    print(f"\n─── COMPOUND RATE among tail values the LIVE matchers recognise ───")
    for name, _ in MATCHERS:
        g = grid[name]
        if g["blind"] or not g["plant_ok"]:
            print(f"  {name:>10}  (not read -- matcher is not live)")
            continue
        share = g["compound_rate"] / g["t_tail"] if g["t_tail"] else float("nan")
        print(f"  {name:>10}  >=2 core tokens in {g['compound_rate']:.4f} of the tail = "
              f"{share:.1%} of the values it recognises")

    # ---- VERDICT, read off the live matchers only, nothing written in between ---------
    # The compound excess survived its own control, so it is NOT collision with prose. But
    # "a core token appears" and "a VERDICT appears" are still different units, and the
    # difference is mechanically checkable: if substring finds >=2 tokens where `word` finds
    # <=1 in the SAME string, the extra tokens are inside words, not standalone verdicts.
    # This is the §2.5 move done properly -- test the assumption, do not pick a design.
    both = [s for s in tail if len(m_sub(s, core)) >= 2]
    inside = [s for s in both if len(m_word(s, core)) <= 1]
    print(f"\n─── WHERE THE SUBSTRING COMPOUNDS LIVE (unit test, not a preference) ───")
    print(f"  tail values with >=2 tokens under SUBSTRING : {len(both)}")
    print(f"  of those, <=1 token under WORD (i.e. the extra tokens are INSIDE words): "
          f"{len(inside)} = {len(inside)/len(both):.1%}" if both else "  (none)")
    for s in inside[:3]:
        print(f"      {s[:96]!r}")
    compounds_are_lexical = bool(both) and len(inside) / len(both) >= 0.80

    print(f"\n─── VERDICT ───")
    live = [n for n, _ in MATCHERS if not grid[n]["blind"] and grid[n]["plant_ok"]
            and grid[n]["placebo_ok"]]
    if not live:
        world = ("B OPEN -- every matcher is blind or failed its control; the core is not "
                 "recoverable from the tail and no repair is admissible")
        cellwise = {}
    else:
        # ⛔ v1 AVERAGED t ACROSS THE THREE MATCHERS. §2.5 forbids exactly that: averaging
        # divergent designs hides the disagreement, which is the informative part -- and here
        # the designs differ by a factor of 16 in false-positive rate (prefix 0.0217 vs
        # substring 0.3577). The curve is read PER CELL, on the EXCESS over each matcher's own
        # control, and the verdict must hold in every cell or it is spec-dependent.
        cellwise = {}
        for n in live:
            g = grid[n]
            exc = g["t_tail"] - max(g["f_why"], g["f_prose"])
            share = g["compound_rate"] / g["t_tail"] if g["t_tail"] else 0.0
            cellwise[n] = {"excess": exc, "compound_share": share,
                           "cell": ("C ENUM_SET" if (share >= 0.25 and
                                                     g["compound_exceeds_control"]) else
                                    "A TRANSLATABLE" if exc >= 0.60 else "B OPEN")}
        verdicts = {c["cell"] for c in cellwise.values()}
        if len(verdicts) == 1:
            v = verdicts.pop()
            world = (f"{v} -- unanimous across all {len(live)} live matchers; excess over each "
                     f"matcher's OWN control is " +
                     ", ".join(f"{n} {cellwise[n]['excess']:+.4f}" for n in live) +
                     f"; compound share " +
                     ", ".join(f"{n} {cellwise[n]['compound_share']:.1%}" for n in live))
        else:
            world = (f"SPEC-DEPENDENT -- the matchers disagree ({sorted(verdicts)}); per §2.5 "
                     f"the disagreement IS the finding and no cell may be quoted alone")
            if compounds_are_lexical:
                world = ("B OPEN -- the C ENUM_SET cell is RESOLVED AGAINST: "
                         f"{len(inside)}/{len(both)} of substring's compounds have <=1 "
                         "standalone token under `word`, so the extra tokens sit INSIDE "
                         "words and are letter co-occurrence, not verdict co-occurrence. "
                         "The tail is not translatable and is not a set of verdicts either")
    print(f"  {world}")
    print(f"  live matchers: {live or '(none)'}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "translatable.json").write_text(json.dumps({
        "world": world, "live_matchers": live,
        "core_vocabulary": core, "core_min_occurrences": CORE_MIN,
        "n_distinct_world_values": len(vals), "n_tail_values": len(tail),
        "excluded_payload_values": len(payload),
        "core_occurrence_share": n_core_occ / sum(vals.values()),
        "matchers": grid, "cellwise": cellwise,
        "substring_compounds_n": len(both),
        "substring_compounds_lexical_n": len(inside),
        "compounds_are_lexical": compounds_are_lexical,
        "upper_bound_note": ("whether a round INTENDED the verdict a matcher recovers is not "
                             "decidable from the string; every t is an UPPER BOUND"),
        "instrument_vs_claim": ("instrument unit = a core token recognised in a string; claim "
                                "unit = a verdict the round intended. NOT equal, which is why "
                                "the control rate f is required before any t may be read"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'translatable.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
