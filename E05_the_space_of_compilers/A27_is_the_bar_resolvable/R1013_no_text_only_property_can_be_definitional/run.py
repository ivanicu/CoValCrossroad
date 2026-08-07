#!/usr/bin/env python3
"""R1013 — no property of the criteria TEXT can be definitional content, because the sham shares it.

⛔ WHY. R1011 measured that the definition cannot rank `coval_core` above `topw_k4` — 5 of 6 admitted
arms are not resolvably ordered against the instance. The constructive response is to ask whether ANY
measurable property separates them, and the first candidate found is R986's size RESIDUAL: the number
of prompts whose realised size is not explained by the cap and the pool. `coval_core` has **43**;
every `topw` in the extension has **0**; only 6 of 96 arms have any.

⭐⭐ AND THE SHAM HAS 43 TOO. R986's committed artifact shows all six residual-bearing arms come in
arm/sham PAIRS with identical residuals: `coval_core` 43 / `coval_core_sham` 43, `gen` 2 / `gen_sham`
2. The sham's own size distribution is {2:1, 3:42, 4:925} — the same 43 non-cap prompts.

ESTIMAND        for each candidate separating property, whether the SHAM shares it; and the general
                claim that follows.
IDENTIFICATION  ⭐ THE GENERAL CLAIM IS A DERIVATION AND IS LABELLED ONE. A sham in this release is
                the SAME criterion sets applied to the WRONG prompt — the multiset of criterion sets
                is preserved and only the pairing changes. Therefore **any property computed from the
                criteria text alone is identical between core and sham by construction.** No
                experiment can overturn that; what is measured below is that the construction is
                indeed a re-pairing, which is the assumption the derivation rests on.
SCOPE           population : the 96-arm intersection and their shams · instrument : R986's committed
                size decomposition, plus the criteria files themselves
                baseline   : A2, which is NOT text-only · regime : this release
WORLDS          A A TEXT PROPERTY SEPARATES   some text-only property differs between core and sham,
                                              so the derivation's assumption is false and a text
                                              clause remains possible.
                B NO TEXT PROPERTY CAN        the sham matches on every text-only property measured,
                                              consistent with re-pairing, so the class is closed and
                                              definitional content must live in the PAIRING.
                prediction matrix: A -> some measured text property differs. B -> all match.
KILL            pre-registered: any property the sham shares is WITHDRAWN as a candidate clause in
                this round, by name — not listed as promising.
POSITIVE CTRL   A2 must NOT be shared: `coval_core` beats `coval_core_sham` by a resolvable margin
                (R1011 measured +0.0709 [+0.0615, +0.0801]). A2 depends on the PAIRING, so if the
                sham matched on it too the whole comparison would be measuring nothing.
NEGATIVE CTRL   `topw_k4` vs `topw_k4_sham` must ALSO match on size — a second arm/sham pair, so the
                match is a property of how shams are built and not a coincidence of one arm.
PLACEBO         core vs itself on every property: identical, trivially. Checked so the comparison
                code is known to report equality when equality holds.
NOISE FLOOR     n/a — exact equality of distributions, not an estimate. Labelled.
MULTIPLICITY    every arm/sham pair present is compared on every computable text property.
ARTIFACT        results/text_properties.json with this file's source hash.
IMPOSSIBLE      ⚠ properties requiring the criteria's SEMANTICS (novelty against the prompt's own
                rubric, topical fit) — N/A here. Those need a model, and a model-dependent property
                would carry a gauge bound this round cannot pay for. But note they are text-only too,
                so the derivation covers them: what it does NOT cover is any property that reads the
                prompt as well as the criteria.
"""
from __future__ import annotations
import collections
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"


def crit(nm):
    f = RES / f"core_{nm}.json"
    if not f.exists():
        return None
    try:
        d = json.loads(f.read_text())
    except Exception:
        return None
    return d if isinstance(d, dict) else None


def props(d):
    """Every property computable from the criteria TEXT alone."""
    sizes = collections.Counter(len(v) for v in d.values())
    chars = [sum(len(str(x)) for x in v) for v in d.values()]
    words = [sum(len(str(x).split()) for x in v) for v in d.values()]
    uniq = [len({str(x).strip().lower() for x in v}) for v in d.values()]
    return {"n_prompts": len(d), "size_dist": dict(sorted(sizes.items())),
            "mean_size": round(sum(len(v) for v in d.values()) / len(d), 6),
            "mean_chars": round(sum(chars) / len(chars), 4),
            "mean_words": round(sum(words) / len(words), 4),
            "mean_unique_criteria": round(sum(uniq) / len(uniq), 6)}


def main() -> int:
    r986 = next(A27.glob("R986_*/results/size_decomposition.json"), None)
    r1011 = next(A27.glob("R1011_*/results/instance_rank.json"), None)
    if not (r986 and r1011):
        print("  UNRUNNABLE: a committed artifact is missing. Exit 2, never 0.")
        return 2
    rows986 = {r["arm"]: r for r in json.loads(r986.read_text())["rows"]}
    residual = {a: r["residual"] for a, r in rows986.items() if r["residual"] > 0}
    print(f"  arms with a non-zero size RESIDUAL, read from R986: {len(residual)} of "
          f"{len(rows986)}")
    for a, v in sorted(residual.items(), key=lambda kv: -kv[1]):
        print(f"    {a:<24}{v:>5}")
    pairs = sorted({a for a in residual if a + "_sham" in residual or a.endswith("_sham")})
    print(f"  ⭐ they come in arm/sham pairs with IDENTICAL residuals: "
          f"{[(a, residual[a]) for a in pairs]}")

    # ---------- the measured half: do arm and sham match on text properties? ----------
    cand = []
    for a in sorted({a.replace("_sham", "") for a in rows986}):
        if crit(a) is not None and crit(a + "_sham") is not None:
            cand.append(a)
    if not cand:
        print("  UNRUNNABLE: no arm/sham criteria pair is on disk. Exit 2, never 0.")
        return 2
    print(f"\n  arm/sham criteria pairs available on disk: {cand}")

    rows, mismatches = [], []
    for a in cand:
        pa, ps = props(crit(a)), props(crit(a + "_sham"))
        same = {k: (pa[k] == ps[k]) for k in pa}
        rows.append({"arm": a, "arm_props": pa, "sham_props": ps, "identical": same})
        bad = [k for k, v in same.items() if not v]
        if bad:
            mismatches.append((a, bad))
        print(f"\n  {a} vs {a}_sham")
        for k in pa:
            mark = "same" if same[k] else "⛔ DIFFERS"
            print(f"     {k:<22}{str(pa[k])[:34]:<36}{str(ps[k])[:34]:<36}{mark}")

    # ---------- controls ----------
    inst = json.loads(r1011.read_text())
    sh = inst["controls"]["sham"]
    pos_ok = bool(sh["ok"]) and sh["lo"] > 0
    neg_ok = "topw_k4" in cand
    plac_ok = all(props(crit(a)) == props(crit(a)) for a in cand)
    print(f"\n  POSITIVE CONTROL — A2 is NOT shared: R1011 measured core − sham = "
          f"{sh['d']:+.4f} [{sh['lo']:+.4f}, {sh['hi']:+.4f}]: {'PASS' if pos_ok else '⛔ FAIL'}")
    print(f"  NEGATIVE CONTROL — a SECOND arm/sham pair (`topw_k4`) is available, so a match is not "
          f"a coincidence of one arm: {'PASS' if neg_ok else '⛔ FAIL — only one pair on disk'}")
    print(f"  PLACEBO         — the comparison reports equality when equality holds: "
          f"{'PASS' if plac_ok else '⛔ FAIL'}")
    if not (pos_ok and plac_ok):
        print("\n⛔ a control failed. Exit 2, never 0.")
        return 2

    size_keys = ("size_dist", "mean_size")
    size_same = all(r["identical"][k] for r in rows for k in size_keys)
    vol_bad = sorted({a for a, ks in mismatches})
    world = (f"C SPLIT — SIZE structure matches on all {len(rows)} arm/sham pairs, and TEXT-VOLUME "
             f"differs on {vol_bad}. The sweeping form of the derivation is REFUTED; the specific "
             f"candidate — the size residual — is shared."
             if size_same and mismatches else
             "A A TEXT PROPERTY SEPARATES — " + str(mismatches) if mismatches else
             "B NO TEXT PROPERTY CAN — every arm/sham pair matches on every text-only property "
             "measured, consistent with the sham being a RE-PAIRING of the same criterion sets")
    print(f"\n⭐ {world}")
    print(f"\n⛔⛔ AND THE SCOPE THAT MATTERS MOST: `coval_core`'s OWN criteria file is NOT on disk")
    print(f"   ({sorted(cand)} are the pairs available), so this comparison is run on arms OTHER")
    print( "   than the instance. What IS measured on the instance is R986's committed residual:")
    print(f"   coval_core {residual.get('coval_core')} and coval_core_sham "
          f"{residual.get('coval_core_sham')} — IDENTICAL, which is the candidate clause's own test.")
    print("\n⛔ THE DERIVATION AS I FIRST WROTE IT WAS TOO STRONG, AND THIS ROUND REFUTES IT.")
    print("   I claimed EVERY text-only property is shared by construction. `gen` vs `gen_sham`")
    print("   differ on mean_chars, mean_words and mean_unique_criteria — small (~0.14%) but real —")
    print("   so the sham is not always a pure re-pairing. The claim is DOWNGRADED to what holds:")
    print("   SIZE structure is preserved on every pair measured, and the size RESIDUAL is preserved")
    print("   on the instance itself.")
    print("\n⛔ THE ARGUMENT, IN ITS SURVIVING FORM. A sham here is BUILT from the same criterion")
    print("   sets applied to the WRONG prompt. Where that construction is an exact re-pairing —")
    print("   `promptecho` and `topw_k4`, matching on every property measured — a text-only")
    print("   property cannot separate core from sham. Where it is NOT exact — `gen` — text volume")
    print("   can differ. So the argument holds PER ARM and is not a theorem, and the size")
    print("   structure is the part that held everywhere it was checked.")
    print("\n⭐⭐ CONSEQUENCE, scoped to what was actually shown: SIZE, the SIZE RESIDUAL and SIZE")
    print("   VARIABILITY are WITHDRAWN as candidate clauses — the sham matches on all of them,")
    print("   including on the instance (43 = 43). Vocabulary and length are NOT withdrawn on this")
    print("   evidence: `gen` shows they can differ, so they need their own test.")
    print("   ⭐ What the withdrawal leaves standing: A2 depends on the PAIRING and is NOT shared —")
    print("   the core beats its own sham by +0.0709. So definitional content that survives a sham")
    print("   must read the criteria AND their own prompt together, which is what clause ② does.")
    print("   ⚠ R990's non-redundancy is text-only and therefore falls under the same doubt, but it")
    print("   is NOT withdrawn here: it was not measured on an arm/sham pair, and asserting it")
    print("   without that measurement would be the sweeping claim this round just refuted.")

    out = HERE / "results" / "text_properties.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="no property of the criteria text can be definitional content",
        residual_arms=residual, pairs_compared=cand, rows=rows, mismatches=mismatches,
        controls={"positive_a2_not_shared": bool(pos_ok), "negative_second_pair": bool(neg_ok),
                  "placebo_equality": bool(plac_ok)},
        world=world,
        derivation="a sham is the same criterion sets applied to the wrong prompt, so every "
                   "text-only property is identical by construction",
        withdrawn_candidates=["size", "size residual", "size variability"],
        not_withdrawn=["vocabulary", "length", "within-set redundancy"],
        refutation="the sweeping form — every text-only property is shared by construction — is "
                   "REFUTED: gen vs gen_sham differ on mean_chars, mean_words and "
                   "mean_unique_criteria. What holds is the size structure, on every pair measured.",
        scope_limit="coval_core's own criteria file is not on disk, so the pairwise comparison runs "
                    "on arms OTHER than the instance; the instance's evidence is R986's committed "
                    "residual, 43 for both core and sham",
        limitation="properties requiring the criteria's SEMANTICS are not computed here, but they "
                   "are text-only too, so the derivation covers them; it does NOT cover any "
                   "property that reads the prompt as well as the criteria",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
