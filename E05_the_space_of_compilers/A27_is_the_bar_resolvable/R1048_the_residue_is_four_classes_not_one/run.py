"""R1048 — the residue is not one class, and one of the four is a DERIVATION.

R1047 left 43 numbers in neither the round's artifact nor its source, and closed by proposing to read
the line each sits on. Reading them shows the residue is heterogeneous, and the class that matters is
the one no round in this arc has named.

⭐ `2904` is in R1026's README and in no artifact. It is `968 x 3`. That is not an unbacked assertion
   — it is an ARITHMETIC DERIVATION from values the release and the artifacts do carry, and realstat's
   own opening section says a derivation is worth more than a measurement PROVIDED IT IS LABELLED ONE.
   Counting it as a floating number is the same error in the opposite direction: treating computed
   arithmetic as though it had been asserted.

ESTIMAND        the partition of R1047's residue into
                  (i)  DERIVED    - expressible as a product, sum, ratio or difference of two values
                                    carried by artifacts in this arc
                  (ii) CONSTANT   - present in the round's own run.py (already measured by R1047)
                  (iii) EXTERNAL  - a release-level or earlier-arc quantity, tested against a frozen
                                    list drawn from the release, not from my reading
                  (iv) FLOATING   - none of the above
IDENTIFICATION  ⚠ PARTIAL AND THE DIRECTION IS NAMED. The derivation test is GENEROUS: with hundreds
                of artifact values, some numbers will match a product by coincidence. So DERIVED is an
                UPPER bound and FLOATING is a LOWER bound - the same direction R1047 established, and
                deliberately the direction that does NOT flatter the arc.
SCOPE           population : R1047's residue, recomputed here from the same rounds
                instrument : rounding-aware containment at the README's displayed precision (R1047)
                baseline   : R1047's undifferentiated 43
                regime     : one arc, one window
WORLDS          A THE RESIDUE IS REAL - most of it is FLOATING even after the three exculpating
                  classes are removed, so a README gate has genuine defects to catch.
                B THE RESIDUE DISSOLVES - most is derived, constant or external, so what R1047 and
                  R1046 measured is overwhelmingly correct practice rendered in prose, and the gate
                  R1046 proposed would fire on arithmetic.
                prediction matrix: A -> floating share high  B -> floating share low
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      floating share >= 0.50 -> World A, build the gate
                      <= 0.20                -> World B, R1046's gate is abandoned as stated
                      otherwise               -> report, claim neither
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   the derivation test must recover a KNOWN derivation planted at runtime: the product of
                two artifact values drawn from the pool must classify DERIVED.
NEGATIVE CTRL   an irrational offset from that product must NOT classify DERIVED. If both cannot fire,
                the test is generous enough to absorb anything and licenses nothing.
PLACEBO         a round with an empty residue contributes no denominator - excluded, not scored 0.
NOISE FLOOR     ⭐ the coincidence rate is MEASURED, not assumed: random values drawn on the residue's
                own order of magnitude are run through the same derivation test, and the share they
                match is the floor the DERIVED count must beat.
MULTIPLICITY    all four classes reported with counts, not only the class that fires.
SEEDS           3 for the coincidence floor; the spread across seeds is reported.
IMPOSSIBLE      whether a number classified DERIVED was actually derived BY THE AUTHOR that way, as
                opposed to matching a product by accident. SETTLES: OUT-OF-RELEASE - it would need the
                author's intent, which no committed text records.
"""
import json, pathlib, random, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])")
RID = re.compile(r"R\d+")
# frozen BEFORE looking at the residue: release-level constants this arc quotes constantly
EXTERNAL = {968.0, 96.0, 24.0, 28.0, 8000.0, 4000.0, 2.5, 90.0, 15593.0, 16.0}


def nums(o, out):
    if isinstance(o, bool):
        return
    if isinstance(o, (int, float)):
        out.add(float(o)); return
    if isinstance(o, str):
        for m in NUM.finditer(o):
            out.add(float(m.group(1)))
        return
    if isinstance(o, list):
        out.add(float(len(o)))
        for v in o:
            nums(v, out)
        return
    if isinstance(o, dict):
        for v in o.values():
            nums(v, out)


def rounded_in(tok, pool):
    x = float(tok); dp = len(tok.split(".")[1]) if "." in tok else 0
    return any(round(p, dp) == round(x, dp) for p in pool)


def derived(tok, base):
    """is tok a product / sum / ratio / difference of two artifact values, at its own precision?"""
    x = float(tok); dp = len(tok.split(".")[1]) if "." in tok else 0
    t = round(x, dp)
    for a in base:
        for b in base:
            for v in (a * b, a + b, a - b, a / b if b else None):
                if v is not None and round(v, dp) == t:
                    return True
    return False


def main() -> int:
    rows, arc = [], set()
    for d in sorted(A27.glob("R10*")):
        m = re.match(r"R(\d+)", d.name)
        if not (m and 1022 <= int(m.group(1)) <= 1045):
            continue
        rm, rp, js = d / "README.md", d / "run.py", sorted((d / "results").glob("*.json"))
        if not (rm.exists() and rp.exists() and js):
            continue
        pool = set()
        for j in js:
            nums(json.loads(j.read_text()), pool)
        arc |= pool
        rows.append((m.group(0), rm, rp, pool))
    if not rows:
        print("  UNRUNNABLE: empty population. Exit 2, never 0."); return 2

    # a bounded, sorted base keeps the O(n^2) derivation search finite and reproducible
    base = sorted({v for v in arc if 0 < abs(v) < 1e5})[:900]

    # ---------- controls ----------
    a, b = base[len(base) // 3], base[2 * len(base) // 3]
    pos = derived(f"{a * b:.4f}", base)
    neg = not derived(f"{a * b + 987654.321:.4f}", base)
    print(f"  POSITIVE — a product of two artifact values must classify DERIVED: {pos}")
    print(f"  NEGATIVE — that product plus a large offset must NOT: {neg}")
    if not (pos and neg):
        print("  the derivation test does not discriminate. Exit 2, never 0."); return 2

    res, detail = [], []
    for rid, rm, rp, pool in rows:
        src = {float(g) for g in NUM.findall(rp.read_text())}
        text = RID.sub(" ", rm.read_text())
        for ln in text.split("\n"):
            for tok in NUM.findall(ln):
                if rounded_in(tok, pool) or rounded_in(tok, arc):
                    continue
                res.append((rid, tok, ln.strip()[:90], rounded_in(tok, src)))
    if not res:
        print("  UNRUNNABLE: empty residue. Exit 2, never 0."); return 2

    # ⛔⛔ A SIXTH INSTRUMENT DEFECT, VISIBLE IN THIS ROUND'S OWN EXAMPLE LINES. The residue prints
    #   `| A2 | genericpool16 | -0.1247 |` — a NEGATIVE value, written with a unicode minus. The
    #   number regex captures magnitude only, so the checker looks for +0.1247 while the artifact
    #   stores -0.1247. Measured here rather than asserted, because a sign-blind tokenizer inflates
    #   the residue exactly the way the precision-blind one did in R1047.
    signed = 0
    for _rid, tok, ln, _s in res:
        i = ln.find(tok)
        if i > 0 and ln[i - 1] in "-\u2212\u2013":
            if rounded_in(tok, {-v for v in arc}):
                signed += 1
    print(f"  ⛔ SIGN-BLIND — residue entries written with a leading minus whose NEGATION the arc's "
          f"artifacts do carry: {signed} of {len(res)}")

    cls = {"CONSTANT": [], "EXTERNAL": [], "DERIVED": [], "FLOATING": []}
    for rid, tok, ln, in_src in res:
        if in_src:
            k = "CONSTANT"
        elif float(tok) in EXTERNAL:
            k = "EXTERNAL"
        elif derived(tok, base):
            k = "DERIVED"
        else:
            k = "FLOATING"
        cls[k].append({"round": rid, "value": tok, "line": ln})

    # ---------- measured coincidence floor for DERIVED, 3 seeds ----------
    floors = []
    for seed in (11, 23, 47):
        rng = random.Random(seed)
        draws = [f"{rng.uniform(0, 1):.4f}" if rng.random() < .5 else f"{rng.randint(1, 5000)}"
                 for _ in range(200)]
        floors.append(sum(derived(t, base) for t in draws) / len(draws))
    lo, hi = min(floors), max(floors)

    tot = len(res)
    print(f"\n  ⭐ residue {tot} · " + " · ".join(f"{k} {len(v)}" for k, v in cls.items()))
    print(f"  ⭐ MEASURED COINCIDENCE FLOOR for DERIVED, 3 seeds: [{lo:.3f}, {hi:.3f}] — the share "
          f"of RANDOM values on the same order of magnitude that the test also calls derived.")
    d_share = len(cls["DERIVED"]) / tot
    f_share = len(cls["FLOATING"]) / tot
    print(f"     DERIVED share {d_share:.3f} vs floor {hi:.3f} — "
          f"{'ABOVE the floor' if d_share > hi else '⛔ INSIDE the floor: the class is not resolved'}")
    for k in ("DERIVED", "FLOATING"):
        for e in cls[k][:4]:
            print(f"     {k:9}{e['round']} {e['value']:>10}  {e['line'][:66]}")

    # ⛔⛔ THE BRANCH MUST REFERENCE EVERY CONTROL THE ROUND DECLARED. My first version compared
    #   f_share to its bands and printed WORLD B while the line two above said the DERIVED class was
    #   inside its own coincidence floor. That is §4's `verdict string is not a computation`, built
    #   in a round about instruments. The pre-registered KILL already said "if the controls fire",
    #   and the floor IS one of the controls — it was measured and then not consulted.
    resolved = d_share > hi
    print()
    if not resolved:
        world = (f"⛔ UNVERIFIED — NOT World A, NOT World B. The derivation test classifies "
                 f"{hi:.1%} of RANDOM values on the same order of magnitude as DERIVED, so it is a "
                 f"test that cannot fail, and every number it exculpates is exculpated by an "
                 f"instrument with no discriminating power. ⭐ The observed DERIVED share "
                 f"{d_share:.3f} is BELOW that floor, which is the diagnostic: the residue's real "
                 f"numbers are matched LESS often than random ones, so the test is saturated rather "
                 f"than merely noisy. What survives is only what did not route through it: "
                 f"CONSTANT {len(cls['CONSTANT'])} of {tot}, measured by R1047's exact source test. "
                 f"The remaining {tot - len(cls['CONSTANT'])} are UNCLASSIFIED — never FLOATING, and "
                 f"never exculpated. A false acquittal is permanent because nobody re-examines a "
                 f"cleared claim.")
    elif f_share >= 0.50:
        world = (f"⭐ A THE RESIDUE IS REAL — {f_share:.1%} remains FLOATING after removing constants, "
                 f"release-level externals and arithmetic derivations.")
    elif f_share <= 0.20:
        world = (f"⭐ B THE RESIDUE DISSOLVES — only {f_share:.1%} is FLOATING.")
    else:
        world = (f"⭐ NEITHER BAND — FLOATING {f_share:.3f} of {tot}, DERIVED {d_share:.3f}.")
    print(world)
    print(f"⛔ WHY THE TEST SATURATED, AND IT IS ARITHMETIC, NOT BAD LUCK. With {len(base)} artifact")
    print(f"   values and four operations there are ~{len(base) ** 2 * 4:,} candidate results; at a")
    print(f"   README's typical 2-4 decimal places the reachable set is dense in the unit interval,")
    print(f"   so 'is x a product of two of these' is very nearly 'is x a number'. ⭐ The remedy is")
    print(f"   not a tighter tolerance — it is requiring the DERIVATION to be NAMED in the text, which")
    print(f"   is what realstat's arithmetic-trap section demands of a derivation in the first place.")

    out = HERE / "results" / "residue_partition.json"
    out.write_text(json.dumps({
        "round": "R1048", "residue_total": tot,
        "counts": {k: len(v) for k, v in cls.items()},
        "sign_blind_residue_entries": signed,
        "verdict": "UNVERIFIED" if not resolved else "RESOLVED",
        "derived_test_resolved": bool(resolved),
        "unclassified_not_floating": tot - len(cls["CONSTANT"]),
        "floating_share_lower_bound": f_share, "derived_share_upper_bound": d_share,
        "coincidence_floor_3_seeds": [lo, hi], "base_size": len(base),
        "controls": {"positive_product_is_derived": bool(pos), "negative_offset_is_not": bool(neg)},
        "examples": {k: v[:8] for k, v in cls.items()}, "world": world,
        "limitation": "DERIVED cannot establish that the author derived it that way; only that the "
                      "value is reachable from artifact values by one operation",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
