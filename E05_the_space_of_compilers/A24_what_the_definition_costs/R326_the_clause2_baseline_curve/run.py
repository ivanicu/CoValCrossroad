"""R326 — the clause-2 baseline curve: the decline is a DERIVATION, the crossing is a measurement.

R325 fixed clause 1's column; the previous round found clause 2 binds at 1.19x and that clause 2 has
TWO published references. R289 asked `which target earns the definition` for the TARGET axis. The
same question for the clause-2 BASELINE axis was never asked, and six ordered points already exist
across R286, R287, R307 and R308.

⛔ AND THE OBVIOUS PLOT IS THE ARITHMETIC TRAP. `gap = arm_A2 - ref_A2`, and the arm is fixed, so
plotting the gap against the reference's own A2 plots a quantity against something it is DEFINED as
a difference from. Verified to four decimals at all six points: every published gap equals
0.566477 - ref exactly. **The monotone decline is a DERIVATION and is labelled one.** What is not
forced is where the ratio to each cell's OWN MDE crosses 1.0, because those MDEs are measured per
cell and vary independently (0.0099-0.0107 here).

ESTIMAND      for each admitted arm, the clause-2 margin divided by that cell's own MDE across
              every published prompt-blind reference, ordered by reference strength — and the
              strongest LEGITIMATE reference at which the arm is still resolvable.
IDENTIFICATION exact per cell; all six are committed by R286/R287/R307/R308. This round reads them
              and adds no estimate. The ORDERING is by reference A2, which is observed, not chosen.
SCOPE         population 968 prompts, 15,593 annotations · instrument Qwen3.5-2B-Base · regime
              A2·annotator, clause 2 · references as published.
WORLDS        W-STABLE    both admitted arms stay resolvable at every legitimate reference -> the
                          admission is baseline-robust and the thinness is cosmetic.
              W-CROSSES   an admitted arm falls below its own MDE at some legitimate reference ->
                          its admission is baseline-dependent and the page must say which
                          references support it.
              W-ALL-FAIL  both fall below at the strongest legitimate reference -> clause 2 does
                          not support either admission at the design's own resolution.
KILL          both arms >= 1.0x at every legitimate reference        -> W-STABLE
              exactly one falls below at some legitimate reference   -> W-CROSSES
              both fall below at the strongest legitimate reference  -> W-ALL-FAIL
POSITIVE CTRL the weakest reference must give the LARGEST ratio for both arms. If the ordering did
              not come out that way the reference-strength axis would not be the axis, and nothing
              ordered along it would mean anything.
              Fails at g=0: a curve that is FLAT across references would mean the baseline choice
              does not act, so the spread must be non-trivial.
NEGATIVE CTRL the IN-SAMPLE argmax is DISQUALIFIED as a baseline (R287: an argmax over 1,820 with
              no split is a selection artifact). It is carried in the table as the negative
              control -- the point that should NOT be used -- rather than deleted, so the reader
              can see what an illegitimate reference does.
PLACEBO       gap vs (arm - ref) must agree to 4 decimals at every point, confirming the decline is
              arithmetic. This is the DERIVATION check, not evidence.
NOISE FLOOR   each cell's own MDE, committed by the round that produced it.
MULTIPLICITY  6 references x 2 arms; every cell printed including the disqualified one.
ARTIFACT      results/baseline_curve.json with source hash.
IMPOSSIBLE    a reference stronger than the held-out best of 1,820 that is still legitimate. The
              in-sample argmax is stronger and is not legitimate; anything beyond needs a larger
              candidate pool, which is a generation cost rather than a release limit.
"""
import hashlib, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
A24 = SELF.parent.parent
ARM_A2 = {"coval_core": 0.5664774811929549, "topw_k4": 0.5641806235396515}

# (label, reference A2, legitimate?, source, {arm: (gap, mde)})
POINTS = []


def load(pat, name):
    d = next(A24.glob(pat), None)
    if d is None:
        return None
    f = sorted((d / "results").glob("*.json"))
    return json.loads(f[0].read_text()) if f else None


def main():
    r286, r287 = load("R286_*", "ceiling"), load("R287_*", "budget")
    r307, r308 = load("R307_*", "neutral"), load("R308_*", "matched")
    if not all((r286, r287, r307, r308)):
        print("  UNRUNNABLE: a source artifact is absent."); return 2

    for lab, ref in r287["refs"].items():
        cells = {a: r287["cells"].get(f"{a}|{lab}") for a in ARM_A2}
        POINTS.append([lab, ref, True, "R287",
                       {a: (c["gap"], c["mde"]) for a, c in cells.items() if c}])
    ins = next((k for k in r287["cells"] if "IN-SAMPLE" in k), None)
    if ins:
        lab = ins.split("|", 1)[1]
        # ⚠ REPAIRED by R328, 2026-08-03. This was the TYPED literal 0.5575138121466373 with
        # source "R287". R287's artifact does not contain that number -- it disqualified the
        # ceiling and never committed a ref for it. The literal is R286's
        # selection["best"][0][1]: the HELD-OUT score of split 0, i.e. a held-out number
        # published as the in-sample ceiling. The true in-sample argmax is R286's dist["max"]
        # = 0.55747530882624, which R328 reproduced to 1e-12 and which R287's OWN committed
        # gap already implies (0.5664774811929549 - 0.009002172366714738). Read, not typed.
        POINTS.append([lab, r286["dist"]["max"], False, "R286 dist[max] · cells R287",
                       {a: (r287["cells"][f"{a}|{lab}"]["gap"], r287["cells"][f"{a}|{lab}"]["mde"])
                        for a in ARM_A2 if f"{a}|{lab}" in r287["cells"]}])
    POINTS.append(["neutral pool-16", 0.5403157241364976, True, "R307",
                   {a: (v["gap"], v["mde"]) for a, v in r307["arms"].items() if a in ARM_A2}])
    POINTS.append(["generic at matched k=4", 0.5513543391990778, True, "R308",
                   {a: (v["eff"], v["mde"]) for a, v in r308["rows"].items() if a in ARM_A2}])
    POINTS.append(["best held-out of 1,820", 0.5546019829643504, True, "R286",
                   {a: (v["gap"], v["mde"]) for a, v in r286["arms"].items() if a in ARM_A2}])
    POINTS.sort(key=lambda p: p[1])

    # ---- PLACEBO / the derivation check ---------------------------------------------------------
    print("  PLACEBO — is the decline forced? gap must equal (arm A2 - reference A2)\n")
    # ⚠ TOLERANCE REPAIRED by R328, 2026-08-03. It was 1e-4 and it PASSED on a reference that was
    # wrong by 3.85e-5 -- the check was 2.6x too loose to catch the one defect it exists to catch.
    # This is an EXACT algebraic identity; the only slack it needs is float reassociation between
    # mean(a-r) and mean(a)-mean(r), which is ~1e-15. And the max deviation is now PRINTED, because
    # a boolean hides the very margin that told you the tolerance was wrong.
    TOL = 1e-9
    forced, worst = True, 0.0
    for lab, ref, ok, src, arms in POINTS:
        for a, (gap, _) in arms.items():
            d = abs(gap - (ARM_A2[a] - ref))
            worst = max(worst, d)
            if d > TOL:
                forced = False
                print(f"    {a} at {lab}: gap {gap:+.6f} vs arm-ref {ARM_A2[a]-ref:+.6f}  "
                      f"DIFFERS by {d:.3e}")
    print(f"    every published gap equals arm minus reference to {TOL:.0e}: {forced}   "
          f"(worst deviation observed {worst:.3e})")
    print("    -> THE MONOTONE DECLINE IS A DERIVATION. What is measured is the ratio to each")
    print("       cell's OWN MDE, because those vary independently of the reference.\n")

    print(f"    {'reference':<34}{'ref A2':>9}{'legit':>7}"
          f"{'coval_core':>22}{'topw_k4':>22}")
    rows = []
    for lab, ref, ok, src, arms in POINTS:
        cells = {}
        out = []
        for a in ("coval_core", "topw_k4"):
            if a not in arms:
                out.append(f"{'--':>22}"); continue
            gap, mde = arms[a]
            r = abs(gap) / mde
            cells[a] = dict(gap=gap, mde=mde, ratio=r, resolved=bool(r >= 1.0))
            mark = "" if r >= 1.0 else "  UNRESOLVED"
            out.append(f"{gap:+.4f}/{mde:.4f}={r:>5.2f}x{mark:<12}"[:22].rjust(22))
        rows.append(dict(ref=lab, ref_a2=ref, legit=ok, source=src, cells=cells))
        print(f"    {lab[:33]:<34}{ref:>9.4f}{('yes' if ok else 'NO'):>7}" + "".join(out))

    # ⚠ MERGE REFERENCES THAT ARE THE SAME REFERENCE. R287 and R286 both report the held-out best
    # of 1,820 at A2 0.5546 -- one carries coval_core, the other carries BOTH arms. Selecting the
    # strongest by max(ref_a2) picked whichever sorted last, and when that was R287's row the cell
    # dict held ONLY coval_core, so topw_k4 at 0.92x -- UNRESOLVED at the strongest legitimate
    # reference -- was invisible to the kill and the round printed W-STABLE. The verdict was
    # computed over a population that did not contain the case. Same failure class as the four
    # already logged this session; the fix is again to make the population explicit in code.
    legit = [r for r in rows if r["legit"]]
    merged = {}
    for r in legit:
        k = round(r["ref_a2"], 6)
        if k in merged:
            merged[k]["cells"].update(r["cells"])
            merged[k]["source"] += "+" + r["source"]
        else:
            merged[k] = dict(r, cells=dict(r["cells"]))
    legit = sorted(merged.values(), key=lambda r: r["ref_a2"])
    strongest = legit[-1]
    print(f"\n  merged {len(rows)} published rows into {len(legit)} distinct legitimate "
          f"references (+1 disqualified); strongest = {strongest['ref']} "
          f"[{strongest['source']}] with {len(strongest['cells'])} arms")
    # ---- controls ---------------------------------------------------------------------------------
    weakest = min(legit, key=lambda r: r["ref_a2"])
    pos_ok = all(weakest["cells"].get(a, {}).get("ratio", 0) >=
                 max((r["cells"][a]["ratio"] for r in legit if a in r["cells"]), default=0) - 1e-9
                 for a in weakest["cells"])
    ratios = [c["ratio"] for r in legit for c in r["cells"].values()]
    flat = (max(ratios) - min(ratios)) < 0.2
    print(f"\n  POSITIVE  the weakest legitimate reference gives the largest ratio: {pos_ok}")
    print(f"  KNOB      the curve is not flat (spread {max(ratios)-min(ratios):.2f}): {not flat}")
    dis = [r for r in rows if not r["legit"]]
    print(f"  NEGATIVE  the disqualified in-sample argmax is carried, not deleted: {len(dis) == 1}"
          + (f"  ({', '.join(f'{a} {c[chr(114)+chr(97)+chr(116)+chr(105)+chr(111)]:.2f}x' for a, c in dis[0]['cells'].items())})" if dis else ""))

    fails = [a for a, c in strongest["cells"].items() if not c["resolved"]]
    ctrl = pos_ok and not flat and bool(dis)
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  positive={pos_ok}  knob={not flat}  negative={bool(dis)}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the curve is not readable.")
    elif not fails:
        world = "W-STABLE"
        print(f"  -> W-STABLE. Both admitted arms stay resolvable at every legitimate reference,")
        print(f"     including the strongest ({strongest['ref']}).")
    elif len(fails) == len(strongest["cells"]):
        world = "W-ALL-FAIL"
        print(f"  -> W-ALL-FAIL. Both fall below their own MDE at {strongest['ref']}.")
    else:
        world = "W-CROSSES"
        c = strongest["cells"]
        print(f"  -> W-CROSSES. At the STRONGEST LEGITIMATE reference ({strongest['ref']}, "
              f"A2 {strongest['ref_a2']:.4f}):")
        for a in ("coval_core", "topw_k4"):
            if a in c:
                print(f"       {a:<12} {c[a]['gap']:+.4f} / {c[a]['mde']:.4f} = "
                      f"{c[a]['ratio']:.2f}x  {'RESOLVED' if c[a]['resolved'] else 'UNRESOLVED'}")
        print(f"     {fails} falls BELOW its own MDE there. Its CI still excludes zero and it")
        print("     still survives BH -- the same split R325 drew for clause 1, now landing on an")
        print("     ADMITTED arm at the definition's strongest baseline. The admission is")
        print("     baseline-dependent, and the page should say which references support it.")
    print("  " + "=" * 78)

    o = SELF.parent / "results" / "baseline_curve.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        decline_is_derivation=bool(forced), arm_a2=ARM_A2, points=rows,
        strongest_legitimate=strongest["ref"], unresolved_there=fails,
        positive_ok=bool(pos_ok), not_flat=bool(not flat),
        disqualified_carried=bool(dis)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
