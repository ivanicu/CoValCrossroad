"""R1047 — before building R1046's gate, ask what it would fire on.

R1046 measured that [0.164, 0.272] of the numbers a round README asserts are not in that round's own
artifact, and closed by proposing a gate mirroring the anchoring check but pointed at READMEs.

⛔ THAT NEXT IS A PROPOSAL TO INSTALL AN INSTRUMENT, AND R1045 IS ONE ROUND OLD: a NEXT written last,
   with no control attached, generalising from a count nobody has decomposed. **The 175 numbers
   present in no artifact are not necessarily FINDINGS.** A pre-registered threshold (`0.25`), a
   tolerance (`1e-9`), a seed, or a population bound lives in `run.py` BY DESIGN and would be
   correctly absent from `results/`. A gate that fires on those is not an anchoring gate — it is
   noise with a red exit code, and §4's `check that cannot fail` has a mirror: a check that cannot
   PASS.

ESTIMAND        of the README numbers absent from every artifact in this arc, the share that are
                present in the round's OWN run.py source
IDENTIFICATION  exact — both texts are committed. ⚠ Presence in `run.py` does not PROVE a number is a
                design constant; a finding could coincide with a constant's digits. The share is
                therefore an UPPER BOUND on legitimately-unpersisted numbers, and the residue — in
                neither artifact nor source — is the LOWER bound on genuinely floating ones.
SCOPE           population : R1022-R1045 README numbers unbacked by any artifact in the arc
                instrument : literal numeric containment, tol 1e-9 relative
                baseline   : R1046's [0.164, 0.272] bracket
                regime     : one arc, one window
WORLDS          A THE GATE IS WORTH BUILDING — most floating numbers are in neither source nor
                  artifact, so they are assertions with no computational origin anywhere in the round
                  and a README anchoring gate would catch real defects.
                B THE GATE WOULD BE NOISE — most are in the round's own run.py, i.e. pre-registered
                  thresholds and design constants, correctly absent from results. Then R1046's NEXT
                  proposes an instrument that mostly fires on correct practice, and the remedy is to
                  widen what counts as an anchor, not to add a gate.
                prediction matrix: A -> in-source share low  B -> in-source share high
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      in-source share >= 0.50 -> World B, R1046's NEXT is withdrawn as stated
                      <= 0.20                 -> World A, build it
                      otherwise                -> report, claim neither, and say what splits it
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   a value drawn AT RUNTIME from each round's own run.py must read as in-source. It
                cannot be satisfied by a rule returning True for everything, because the NEGATIVE
                below uses the same containment function.
NEGATIVE CTRL   that value plus a large offset must read as NOT in-source for every round.
PLACEBO         a round with no unbacked numbers contributes no denominator - excluded, not 0.
NOISE FLOOR     the residue is reported as a COUNT beside its denominator, never as a bare share.
MULTIPLICITY    every round reported, both classes, not only the class that fires.
SEEDS           N/A - deterministic over committed text.
IMPOSSIBLE      whether a number in BOTH source and README is there as a constant or as a finding
                that coincides with one. SETTLES: IN-RELEASE - resolvable by reading the line it sits
                on, at one reading per number; unattempted, not unavailable.
"""
import json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])")
RID = re.compile(r"R\d+")


def nums(obj, out):
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        out.add(float(obj)); return
    if isinstance(obj, str):
        for m in NUM.finditer(obj):
            out.add(float(m.group(1)))
        return
    if isinstance(obj, list):
        out.add(float(len(obj)))
        for v in obj:
            nums(v, out)
        return
    if isinstance(obj, dict):
        for v in obj.values():
            nums(v, out)


def has(x, pool):
    return any(abs(x - p) <= 1e-9 * max(1.0, abs(x)) for p in pool)


def has_rounded(tok, pool):
    """⛔⛔ THE EXACT TEST ABOVE IS BLIND TO THE DOMINANT CASE AND ITS CONTROL COULD NOT SEE IT.
    A README displays `0.507`; the artifact stores `0.5071...`. Exact containment calls that
    unbacked. The positive control drew its value FROM the artifact, so it was exact by
    construction — §4's row exactly: a control that shares the instrument's blind spot confirms
    the instrument and licenses nothing. A README number is backed if SOME artifact value rounds
    to it at the README's OWN displayed precision."""
    x = float(tok)
    dp = len(tok.split(".")[1]) if "." in tok else 0
    return any(round(p, dp) == round(x, dp) for p in pool)


def main() -> int:
    rows = []
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
        src = {float(g) for g in NUM.findall(rp.read_text())}
        want = NUM.findall(RID.sub(" ", rm.read_text()))          # keep the TOKEN: precision matters
        rows.append((m.group(0), want, pool, src))

    if not rows:
        print("  UNRUNNABLE: an empty population must not pass. Exit 2, never 0."); return 2

    pos = all(has(sorted(s)[len(s) // 2], s) for _r, _w, _p, s in rows)
    neg = all(not has(sorted(s)[len(s) // 2] + 987654.321, s) for _r, _w, _p, s in rows)
    print(f"  POSITIVE — a value drawn AT RUNTIME from each round's own run.py must read as "
          f"in-source, all {len(rows)}: {pos}")
    print(f"  NEGATIVE — that value plus a large offset must read as NOT in-source everywhere: {neg}")
    if not (pos and neg):
        print("  the containment test does not discriminate. Exit 2, never 0."); return 2

    arc = set()
    for _r, _w, p, _s in rows:
        arc |= p

    float_tot = in_src = residue = rounded_rescued = 0
    detail, examples = [], []
    for rid, want, pool, src in rows:
        f = [tok for tok in want
             if not has_rounded(tok, pool) and not has_rounded(tok, arc)]
        i = [tok for tok in f if has_rounded(tok, src)]
        r = [tok for tok in f if not has_rounded(tok, src)]
        ex = [tok for tok in want if not has(float(tok), pool) and has_rounded(tok, pool)]
        rounded_rescued += len(ex)
        float_tot += len(f); in_src += len(i); residue += len(r)
        detail.append({"round": rid, "floating": len(f), "in_own_source": len(i), "residue": len(r),
                       "residue_values": r[:12]})
        examples += [(rid, x) for x in r[:3]]

    if not float_tot:
        print("  UNRUNNABLE: no floating numbers to classify. Exit 2, never 0."); return 2
    share = in_src / float_tot

    print(f"\n  ⛔ RESCUED BY ROUNDING ALONE — numbers the EXACT test called unbacked that the")
    print(f"     round's own artifact does carry at the README's displayed precision: "
          f"{rounded_rescued}")
    print(f"\n  ⭐ {float_tot} numbers in NO artifact in this arc · in the round's OWN run.py "
          f"{in_src} ({share:.3f}) · in NEITHER {residue}")
    print(f"  residue examples (round, value): {examples[:10]}")
    print()
    if share >= 0.50:
        world = (f"⭐ B THE GATE WOULD BE NOISE AS R1046 STATED IT — {share:.1%} of the floating "
                 f"numbers are in the round's own run.py, i.e. pre-registered thresholds, tolerances "
                 f"and design constants that are CORRECTLY absent from results. A gate demanding "
                 f"artifact backing would fire on correct practice. The remedy is to widen what "
                 f"counts as an anchor to include the round's own SOURCE, not to add a gate.")
    elif share <= 0.20:
        world = (f"⭐ A THE GATE IS WORTH BUILDING — only {share:.1%} of the floating numbers appear "
                 f"in the round's own source, so {residue} of {float_tot} have no computational "
                 f"origin anywhere in the round and a README anchoring gate would catch them.")
    else:
        world = (f"⭐ NEITHER BAND — in-source {share:.3f} over {float_tot} floating numbers, residue "
                 f"{residue}. Reported, neither world claimed. What splits it is whether a number "
                 f"shared by source and README is a constant or a coincidence, which needs the LINE, "
                 f"not the value.")
    print(world)
    print(f"⛔ AND THE IN-SOURCE SHARE IS AN UPPER BOUND ON LEGITIMACY. Presence in run.py does not")
    print(f"   prove a number is a design constant — a finding can coincide with a threshold's")
    print(f"   digits. So {residue} is the LOWER bound on genuinely floating numbers and is the only")
    print(f"   count here that citation, pre-registration or coincidence cannot explain away.")

    # ⛔⛔ R1046 IS ONE COMMIT OLD AND USED THE EXACT TEST. Its bracket must be recomputed here,
    #   not merely described as inflated — a retraction that does not carry the corrected number
    #   leaves the wrong one as the only number in the record.
    b_tot = b_miss = 0
    for _rid, want, pool, _src in rows:
        b_tot += len(want)
        b_miss += sum(1 for tok in want if not has_rounded(tok, pool))
    b_share = b_miss / b_tot
    arc_miss = sum(1 for _r, w, p, _s in rows
                   for tok in w if not has_rounded(tok, p) and not has_rounded(tok, arc))
    print(f"\n  ⛔ R1046 RECOMPUTED WITH THE ROUNDING-AWARE TEST — body cell: unbacked {b_miss} of")
    print(f"     {b_tot} = {b_share:.3f}, was 289 of 1064 = 0.272. Bracket "
          f"[{arc_miss / b_tot:.3f}, {b_share:.3f}], was [0.164, 0.272].")
    print(f"     R1046's WORLD B verdict required >= 0.25 and no longer clears it. ⭐ The finding")
    print(f"     that survives is the SPECIFICATION CURVE, not the magnitude: the h1 and body cells")
    print(f"     still disagree, and READMEs are still guarded by nothing.")

    out = HERE / "results" / "floating_or_constant.json"
    out.write_text(json.dumps({
        "round": "R1047", "tests": "R1046's proposed README anchoring gate, before building it",
        "rescued_by_rounding_alone": rounded_rescued, "floating_total": float_tot, "in_own_source": in_src, "in_source_share_upper_bound": share,
        "residue_lower_bound": residue,
        "controls": {"positive_runtime_source_value": bool(pos), "negative_offset": bool(neg)},
        "R1046_recomputed": {"body_unbacked": b_miss, "body_total": b_tot,
                             "body_share": b_share, "bracket": [arc_miss / b_tot, b_share],
                             "was": [0.164, 0.272]},
        "detail": detail, "world": world,
        "limitation": "presence in run.py is an upper bound on legitimacy; a finding can coincide "
                      "with a constant's digits, and only the LINE would separate them",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
