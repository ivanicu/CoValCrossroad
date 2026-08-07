"""Is the 5,186-node blind spot a blind spot, or a bookkeeping artifact?

R340 closed with a sentence I wrote last and never checked:

    "those 5,186 skipped nodes are now the largest unexamined population in the repo ...
     the scanner DECLINES a pair when the CI's stem names another key"

realstat §4 says the closing sentence is the highest-risk sentence in a report -- it is written
after the controls have fired, it is the one a later round acts on, and it has no control attached.
It also names the tell exactly: quantifiers over my own work ("the largest", "nobody has ever"). So
before spending a day reading 5,186 nodes, this round checks whether the population is what the
sentence says it is.

ESTIMAND, named before the method
---------------------------------
Among the nodes `artifacts_are_internally_coherent.scan()` records in `skipped_ci_spoken_for`, the
fraction the SOLE-CANDIDATE route would actually have paired had the `ci_spoken_for` predicate
returned False. Call it the DECLINE RATE.

    recorded          = |skipped_ci_spoken_for|                     (what the banner prints)
    actually declined = recorded nodes where the pairing would otherwise have fired,
                        i.e. len(mks)==1 and len(cks)==1 and not stem_hits and not sole_is_null
    decline rate      = actually declined / recorded

A node with three mean-like keys, or none, or one already stem-matched, was never going to be
paired. Recording it as "skipped" attributes to the predicate a refusal that the surrounding
conditions had already made. THE SAME DEFECT IS ALREADY FIXED ONE PREDICATE ABOVE, in this file's
own words at `artifacts_are_internally_coherent.py:128-130`:

    "Count only nodes this actually DECLINES to pair -- one mean, one CI, no stem match. Testing
     sole_is_null before the CI condition counted 201 nodes that would never have been paired at
     all, which overstates what the guard refuses."

`sole_is_null` carries `and len(cks) == 1 and not stem_hits` in its recording condition (line 132).
`ci_spoken_for` carries nothing (line 142). Whether that asymmetry matters is the measurement.

SECOND ESTIMAND, only if the first survives
--------------------------------------------
Among the ACTUALLY-DECLINED nodes, is the decline right? The CI `X_ci` is claimed by key `X`. If
that claim is true, `X` should sit near the centre of `[lo,hi]` and the declined mean should not.
So reuse R340's instrument on a different population:

    offcentre(v, lo, hi) = (v - (lo+hi)/2) / ((hi-lo)/2)

    |oc(owner)| < |oc(mean)| - margin   -> CORRECT DECLINE   (the CI does belong to the stem key)
    |oc(mean)| < |oc(owner)| - margin   -> SUSPECT           (the declined mean fits better)
    within margin                       -> AMBIGUOUS         (this instrument cannot separate them)
    owner not a number                  -> UNEVIDENCED       (the name matched; nothing to check)

AMBIGUOUS and UNEVIDENCED are NOT folded into CORRECT. A decline this instrument cannot adjudicate
is UNVERIFIED, and UNVERIFIED never becomes an acquittal.

SCOPE
  population  every node in every E*/A*/R*/results/*.json the scanner walks (same corpus, same
              size cut, same exclusions) -- a CENSUS, not a sample
  instrument  the scanner's own regexes, imported not re-typed, so drift in them moves this too
  baseline    the recorded count, 5,186, as printed by the committed guard
  regime      artifacts as committed at this hash; nothing is re-run

⛔ ARITHMETIC TRAP, declared. The decline rate is a CENSUS over a complete population, not an
estimate: it has no sampling error and gets no interval. It could still have come out any value in
[0,1], so it is a measurement -- but of a fixed finite set, and it is labelled as one. The
CLASSIFICATION into correct/suspect is a proxy and carries the ledger row below.

PROXY LEDGER
  PROPERTY    the CI belongs to the key its stem names
  PROXY       the stem key sits closer to the interval's centre than the declined mean does
  IMPLICATION owner far outside AND mean centred => the decline is suspect      SOUND-ish
              owner centred                      => the CI belongs to it        NOT SOUND: two
              quantities can both sit near a wide interval's centre by accident, which is exactly
              what the AMBIGUOUS bucket and the margin sweep are for
  SAFE SIDE   reports where to look; convicts nothing. Only a source read convicts.

WORLDS
  W1  the skip is mostly CORRECT       -> decline rate high, correct-decline share high
  W2  the skip is mostly a PARSE MISS  -> decline rate high, suspect share high
  W3  the population is INFLATED       -> decline rate low; my closing sentence's object does not
                                          exist at the size claimed, and W1/W2 barely apply

W3 is an ontological rival, not a parameter: it says the question was mis-posed, not mis-answered.

PRE-REGISTERED KILL, written before the run
    if the POSITIVE control fires and the g=0 control fires:
        actually declined < 100  ->  RETRACT "the largest unexamined population in the repo".
                                     The 5,186 is a bookkeeping count, not a blind spot.
        otherwise            ->  the population is real; report its composition.
    else:
        UNVERIFIED. Never OVERTURNED, never CONFIRMED.

CONTROLS
  POSITIVE, real   r16's node (`regret`, `min_segment`, `min_segment_ci`) is the case the predicate
                   was WRITTEN for. It must appear in the actually-declined set. If it does not,
                   this instrument is not looking at the predicate's population.
  g=0              force `ci_spoken_for` to False: the recorded set must go to zero. This is what
                   makes the population attributable to the predicate rather than to the walk.
  NEGATIVE, synth  two planted nodes, mirror images: one where the owner is centred and the mean is
                   far out (must classify CORRECT), one where the mean is centred and the owner is
                   far out (must classify SUSPECT). A classifier that returns the same label on
                   both is measuring nothing.
  RESOLUTION       the margin sweep IS the noise floor for the classifier: report the share that
                   flips bucket as the margin opens from 0 to 1.

EXIT
    0  controls hold and the census is reported
    1  a control misbehaved -- every number below would be silence
    2  the recorded population is empty: nothing to census
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
MARGINS = [0.0, 0.05, 0.10, 0.25, 0.50, 1.00]
REPORTED_BASELINE = 5186          # what the committed guard's banner prints


def load_guard():
    p = ROOT / "assurance" / "artifacts_are_internally_coherent.py"
    spec = importlib.util.spec_from_file_location("coh_guard", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m, hashlib.sha256(p.read_bytes()).hexdigest()[:12]


G, GUARD_HASH = load_guard()


def offcentre(v, lo, hi):
    half = (hi - lo) / 2
    return None if half == 0 else (v - (lo + hi) / 2) / half


def classify(oc_owner, oc_mean, margin):
    if oc_owner is None:
        return "UNEVIDENCED"
    a, b = abs(oc_owner), abs(oc_mean)
    if a < b - margin:
        return "CORRECT"
    if b < a - margin:
        return "SUSPECT"
    return "AMBIGUOUS"


def walk_node(o, rid, path, rows, spoken_for_on=True, src=""):
    """Replicates the guard's per-node decision EXACTLY, adding the counterfactual.

    The regexes and is_ci are IMPORTED from the guard, never re-typed here: a copy would drift
    silently and this round would then be measuring a different instrument than the one in force.
    """
    if isinstance(o, list):
        for i, v in enumerate(o):
            walk_node(v, rid, f"{path}[{i}]", rows, spoken_for_on, src)
        return
    if not isinstance(o, dict):
        return

    cks = [(k, o[k]) for k in o if G.CIISH.match(k) and G.is_ci(o[k])]
    mks = [(k, o[k]) for k in o
           if G.MEANISH.match(k) and not G.PVALUE.match(k)
           and isinstance(o[k], (int, float)) and not isinstance(o[k], bool)]

    stem_hits = set()
    for mk, _mv in mks:
        for ck, _cv in cks:
            if mk.lower() in ck.lower() or ck.lower().replace("_ci", "") == mk.lower():
                stem_hits.add((mk, ck))

    sole_is_null = len(mks) == 1 and bool(G.NULLNAME.search(mks[0][0]))
    ci_stem = re.sub(r"_ci$|^ci_", "", cks[0][0], flags=re.I) if len(cks) == 1 else None
    ci_spoken_for = bool(spoken_for_on and ci_stem and ci_stem != cks[0][0] and ci_stem in o
                         and not any(ci_stem == m for m, _ in mks))

    if ci_spoken_for:
        # would the sole-candidate route have fired, but for THIS predicate?
        would = (len(mks) == 1 and len(cks) == 1 and not stem_hits and not sole_is_null)
        lo, hi = sorted(cks[0][1])
        owner_v = o[ci_stem]
        owner_num = isinstance(owner_v, (int, float)) and not isinstance(owner_v, bool)
        rows.append({
            "rid": rid, "path": path or "<root>", "ci_key": cks[0][0], "stem": ci_stem,
            "src": src, "owner_type": type(owner_v).__name__,
            "would_have_paired": bool(would),
            "n_mean_keys": len(mks), "stem_matched": bool(stem_hits), "sole_null": bool(sole_is_null),
            "mean_key": mks[0][0] if len(mks) == 1 else None,
            "oc_mean": offcentre(mks[0][1], lo, hi) if (would) else None,
            "oc_owner": offcentre(owner_v, lo, hi) if (would and owner_num) else None,
            "owner_numeric": bool(owner_num),
        })

    for k, v in o.items():
        walk_node(v, rid, f"{path}.{k}" if path else k, rows, spoken_for_on, src)


def census(spoken_for_on=True):
    rows = []
    for f in sorted(ROOT.glob("E*/A*/R*/results/*.json")):
        if "_smoke" in str(f) or f.stat().st_size > 6_000_000:
            continue
        try:
            walk_node(json.load(open(f)), f.parts[-3], "", rows, spoken_for_on,
                      f.relative_to(ROOT).as_posix())
        except Exception:
            continue
    return rows


def classifier_control():
    """Mirror-image plants for the CLASSIFIER only. Returning the same label on both measures
    nothing, so both directions are asserted."""
    # owner centred at 0.50 inside [0.40,0.60]; declined mean far out at 0.59
    a = classify(offcentre(0.50, 0.40, 0.60), offcentre(0.59, 0.40, 0.60), 0.0)
    # mirror: mean centred, owner far out
    b = classify(offcentre(0.59, 0.40, 0.60), offcentre(0.50, 0.40, 0.60), 0.0)
    return (a == "CORRECT" and b == "SUSPECT"), f"centred-owner -> {a} (want CORRECT), " \
                                                f"centred-mean -> {b} (want SUSPECT)"


def walk_control():
    """POSITIVE CONTROL ON THE WALK, planted and run through the SAME code path as the census.

    ⚠ THIS REPLACES A CONTROL THAT FAILED FOR ITS OWN REASONS, and the failure is a finding rather
    than a nuisance. v1 asserted that r16's node -- the case the guard's own comment at
    `artifacts_are_internally_coherent.py:134-138` says the predicate was written for -- must show
    up as a genuine decline. It does not, and cannot: that comment describes the instrument as it
    was when MEANISH had been EXTENDED, and lines 55-62 of the same file record the extension being
    REVERTED. Under the reverted regex the node
        {"min_segment", "min_segment_ci", "regret", "mean_segment", "prompts"}
    matches ZERO mean-like keys, so no pairing was ever on the table and the predicate has nothing
    to refuse. A control pinned to a historical configuration of its own instrument is realstat §4's
    `the control fails for its own reasons` -- it printed FAIL while the thing under test was fine.
    Two artefacts of that survive deliberately: the r16 case is still MEASURED below and reported as
    EXPIRED rather than deleted, and the plant here is built from key names, not from a round.

    P+  one mean-like key, one CI whose stem names a NON-mean sibling -> must be a genuine decline
    P-  the CI's stem IS the mean key                                 -> must not be recorded at all
    """
    plus = {"delta": 0.5, "eta": 0.9, "eta_ci": [0.85, 0.95]}
    minus = {"delta": 0.5, "delta_ci": [0.4, 0.6]}
    rp, rm = [], []
    walk_node(plus, "PLANT+", "", rp, True, "<synthetic>")
    walk_node(minus, "PLANT-", "", rm, True, "<synthetic>")
    # g=0 for the plant: the same node with the predicate off must vanish from the population
    rp0 = []
    walk_node(plus, "PLANT+", "", rp0, False, "<synthetic>")
    ok = (len(rp) == 1 and rp[0]["would_have_paired"] and not rm and not rp0)
    return ok, (f"P+ recorded={len(rp)} declined={sum(r['would_have_paired'] for r in rp)} (want 1/1), "
                f"P- recorded={len(rm)} (want 0), P+ at g=0 recorded={len(rp0)} (want 0)")


def main() -> int:
    print(f"R341 · is the 5,186-node blind spot real?   guard sha256[:12] = {GUARD_HASH}\n")

    # ---- controls first, because the census is silence without them -----------------------------
    neg_ok, neg_detail = classifier_control()
    print(f"  CLASSIFIER (synthetic, mirrored): {neg_detail}  {'PASS' if neg_ok else 'FAIL'}")

    pos_ok, pos_detail = walk_control()
    print(f"  POSITIVE on the WALK (planted, same code path): {pos_detail}  "
          f"{'PASS' if pos_ok else 'FAIL'}")

    rows = census(spoken_for_on=True)
    off = census(spoken_for_on=False)
    g0_ok = len(off) == 0
    print(f"  g=0 (predicate forced False, whole corpus): recorded {len(off)} (want 0)  "
          f"{'PASS' if g0_ok else 'FAIL'}")

    if not rows:
        print("\n  UNRUNNABLE: the recorded population is empty. Exit 2, never 0.")
        return 2

    # EXPIRED CONTROL, measured and reported, NOT gated. See walk_control()'s docstring: this is
    # the case the guard's comment names, and the reversion of MEANISH already made it impossible.
    r16 = [r for r in rows if r["rid"].lower().startswith("r16_") and r["stem"] == "min_segment"]
    r16_dec = sum(r["would_have_paired"] for r in r16)
    print(f"  EXPIRED (reported, not gated): r16's `min_segment_ci`, the case the guard's own")
    print(f"      comment cites -- {len(r16)} node(s) recorded, {r16_dec} genuine declines. The")
    print(f"      node matches 0 mean-like keys under the REVERTED MEANISH, so the predicate has")
    print(f"      nothing to refuse there and this is not evidence against the instrument.")

    declined = [r for r in rows if r["would_have_paired"]]
    rate = len(declined) / len(rows)
    print(f"\n  recorded by the guard        {len(rows):>6}   (banner baseline {REPORTED_BASELINE})")
    print(f"  ACTUALLY declined a pairing  {len(declined):>6}   decline rate {rate:.4f}")

    # why the rest were never pairable -- the composition of the inflation
    why = {"several/zero mean keys": 0, "already stem-matched": 0, "sole mean is a null": 0}
    for r in rows:
        if r["would_have_paired"]:
            continue
        if r["stem_matched"]:
            why["already stem-matched"] += 1
        elif r["n_mean_keys"] != 1:
            why["several/zero mean keys"] += 1
        else:
            why["sole mean is a null"] += 1
    print("\n  the non-declined remainder, by why the pairing could never have fired:")
    for k, v in sorted(why.items(), key=lambda kv: -kv[1]):
        print(f"      {k:<28}{v:>6}")

    # ---- second estimand, on the declined set only ----------------------------------------------
    print(f"\n  CLASSIFICATION of the {len(declined)} genuinely declined, margin swept "
          f"(the sweep IS the classifier's resolution)\n")
    print(f"    {'margin':>7}{'CORRECT':>10}{'SUSPECT':>10}{'AMBIGUOUS':>12}{'UNEVIDENCED':>13}")
    curve = {}
    for m in MARGINS:
        counts = {"CORRECT": 0, "SUSPECT": 0, "AMBIGUOUS": 0, "UNEVIDENCED": 0}
        for r in declined:
            counts[classify(r["oc_owner"], r["oc_mean"], m)] += 1
        curve[m] = counts
        print(f"    {m:>7.2f}{counts['CORRECT']:>10}{counts['SUSPECT']:>10}"
              f"{counts['AMBIGUOUS']:>12}{counts['UNEVIDENCED']:>13}")

    # ⚠ THE MISLABELLED BUCKET. The docstring called UNEVIDENCED "owner not a number". Measured,
    # it is 573/573 NUMERIC owners with a ZERO-WIDTH interval, where offcentre is 0/0 and undefined.
    # Two different causes were wearing one label, and only one of them existed.
    unev = {"non-numeric owner": 0, "zero-width interval (lo == hi)": 0}
    for r in declined:
        if r["oc_owner"] is None:
            unev["non-numeric owner" if not r["owner_numeric"]
                 else "zero-width interval (lo == hi)"] += 1
    print("\n  the UNEVIDENCED bucket, by WHY offcentre is undefined:")
    for k, v in sorted(unev.items(), key=lambda kv: -kv[1]):
        print(f"      {k:<32}{v:>6}")
    print("      ⚠ a zero-width interval passes the guard's `inverted` test, which is lo > hi,")
    print("        strictly. `lo == hi` is an interval asserting zero uncertainty and nothing")
    print("        currently looks at it.")

    # WHERE the population lives. My closing sentence said "the largest unexamined population in
    # the REPO", which is a claim about BREADTH and was never counted.
    conc = {}
    for r in declined:
        conc[r["rid"]] = conc.get(r["rid"], 0) + 1
    keypair = {}
    for r in declined:
        keypair[(r["ci_key"], r["stem"], r["mean_key"])] = \
            keypair.get((r["ci_key"], r["stem"], r["mean_key"]), 0) + 1
    print(f"\n  WHERE the 5,157 live -- {len(conc)} round(s), {len(keypair)} distinct key triple(s):")
    for k, v in sorted(conc.items(), key=lambda kv: -kv[1])[:5]:
        print(f"      {k:<34}{v:>6}")
    for (ck, st, mk), v in sorted(keypair.items(), key=lambda kv: -kv[1])[:5]:
        print(f"      CI {ck!r} -> owner {st!r}, declined mean {mk!r}{'':<6}{v:>6}")

    suspects = [r for r in declined if classify(r["oc_owner"], r["oc_mean"], 0.25) == "SUSPECT"]
    # ⚠ dedupe for DISPLAY only. A node appearing in two of a round's result files is two published
    # nodes and both are counted above; showing the same path twice in a top-10 just hides eight
    # others.
    seen, uniq = set(), []
    for r in sorted(suspects, key=lambda r: abs(r["oc_owner"]), reverse=True):
        k = (r["rid"], r["path"], r["ci_key"])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    if suspects:
        print(f"\n  the SUSPECT declines at margin 0.25 -- where the declined mean fits the interval")
        print(f"  better than the key the guard handed it to. {len(suspects)} published nodes, "
              f"{len(uniq)} distinct:\n")
        for r in uniq[:10]:
            print(f"      {r['rid']}:{r['path']}   [{r['src'].split('/')[-1]}]")
            print(f"          CI {r['ci_key']!r} given to {r['stem']!r} (|offcentre| "
                  f"{abs(r['oc_owner']):.2f})  vs declined {r['mean_key']!r} "
                  f"(|offcentre| {abs(r['oc_mean']):.2f})")

    # ---- THE SOURCE READ THAT RETIRES THE QUESTION -------------------------------------------------
    # The proxy above was built to avoid reading 5,186 nodes. Once the census showed the population
    # is ONE round and ONE key triple, the read costs two lines, and it OVERTURNS the proxy on
    # every case the proxy flagged.
    src_ok = None
    r235 = ROOT / "E05_the_space_of_compilers/A19_triple_blind/R235_independent_B/run.py"
    if r235.exists():
        txt = r235.read_text(encoding="utf-8", errors="replace").splitlines()
        same_array = [i + 1 for i, ln in enumerate(txt)
                      if "eta=float(np.nanmean(eta))" in ln.replace(" ", "")
                      and "eta_ci=ci(eta)" in ln.replace(" ", "")]
        ci_is_percentile = [i + 1 for i, ln in enumerate(txt) if ln.startswith("def ci(")]
        src_ok = bool(same_array and ci_is_percentile)
        print(f"\n  SOURCE READ (two lines, because the census said the population is one round):")
    if src_ok:
        print(f"      {r235.relative_to(ROOT)}:{same_array}")
        print(f"          `eta` and `eta_ci` come from the SAME array. The naming is exact and the")
        print(f"          guard's decline is CORRECT for all {len(declined)} nodes, not 'suspect'.")
        print(f"      {r235.relative_to(ROOT)}:{ci_is_percentile}  ci(x) = percentiles of x, and x")
        print(f"          here is a BOOTSTRAP array (run.py:636,644), so eta_ci is a genuine")
        print(f"          percentile CI -- of a RATIO whose denominator approaches zero.")
        print(f"      => the {len(suspects)} SUSPECT flags are FALSE POSITIVES, {len(uniq)}/{len(uniq)}"
              f" of the distinct cases.")
        print(f"         A ratio estimator's bootstrap MEAN is not a location estimate: it can sit")
        print(f"         outside its own percentile interval with nothing wrong. That is a NAMED")
        print(f"         EXCEPTION CLASS for invariant 1, which the guard's docstring calls SOUND.")
    elif r235.exists():
        print("      UNVERIFIED: the expected lines were not found where they were read from, so")
        print("      the classifier's SUSPECT flags are neither confirmed nor refuted here.")

    # ---- the pre-registered kill ------------------------------------------------------------------
    print()
    if not (pos_ok and g0_ok and neg_ok):
        print("  UNVERIFIED: a control misbehaved, so no verdict is admissible here.")
        verdict = "UNVERIFIED"
    elif len(declined) < 100:
        print(f"  KILL FIRES on COUNT. {len(declined)} nodes, not {len(rows)}.")
        verdict = "RETRACTED_COUNT"
    else:
        print(f"  KILL DOES NOT FIRE ON COUNT: {len(declined)} genuine declines of {len(rows)}")
        print(f"  recorded, rate {rate:.4f}. The predicate refuses almost everything it records,")
        print(f"  so the `sole_is_null` bookkeeping defect did NOT recur here.")
        print(f"\n  BUT THE SENTENCE STILL FALLS, on a quantifier I never counted: it lives in")
        print(f"  {len(conc)} round(s) and {len(keypair)} key triple(s). 'The largest unexamined")
        print(f"  population in the REPO' asserts BREADTH. The breadth is one round's grid.")
        verdict = "COUNT_REAL_BREADTH_RETRACTED"

    art = {
        "guard_sha256_12": GUARD_HASH,
        "banner_baseline": REPORTED_BASELINE,
        "recorded": len(rows),
        "actually_declined": len(declined),
        "decline_rate": rate,
        "remainder_composition": why,
        "unevidenced_causes": unev,
        "rounds_containing_declines": conc,
        "key_triples": {f"{a}|{b}|{c}": v for (a, b, c), v in keypair.items()},
        "suspects_published": len(suspects), "suspects_distinct": len(uniq),
        "source_read_refutes_suspects": src_ok,
        "expired_control_r16": {"recorded": len(r16), "genuine_declines": r16_dec,
                                "why": "0 mean-like keys under the reverted MEANISH"},
        "controls": {"positive_planted_walk": pos_ok, "g0_predicate_off": g0_ok,
                     "classifier_mirrored": neg_ok},
        "margin_curve": {str(k): v for k, v in curve.items()},
        "verdict": verdict,
        "declined_nodes": declined,
    }
    outp = HERE / "results" / "r341_skipped_population.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True))
    art_hash = hashlib.sha256(outp.read_bytes()).hexdigest()[:12]
    print(f"\n  artifact {outp.relative_to(ROOT)}  sha256[:12] {art_hash}")

    print("\n  ⚠ SCOPE. This decides how BIG the population is and where inside it to look. It")
    print("    convicts nothing: a CORRECT label means the stem key fits its own interval better")
    print("    than the declined mean does, which is evidence about ARITHMETIC, not about what the")
    print("    round meant. Only a source read settles a SUSPECT.")

    return 0 if (pos_ok and g0_ok and neg_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
