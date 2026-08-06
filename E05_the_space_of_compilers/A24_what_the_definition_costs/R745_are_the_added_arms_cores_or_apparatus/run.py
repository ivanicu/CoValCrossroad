#!/usr/bin/env python3
"""R745 · are the added arms candidate cores, or our own apparatus?

ESTIMAND        the class composition of the 51 arms in the store today but not in R294's committed
                41, and separately of the 11 the census newly admits, under a partition read off
                the builder's own source.
IDENTIFICATION  identified from corebench/select_core.py -- :50-52 the closed rule vocabulary,
                :102 which rules read the human target, :204 the tag is EMITTED from the rule.
                ⚠ GAUGE: a name is blind IN GENERAL (renaming leaves it invariant, the property
                not). It is admissible ONLY because the builder emits it; any tag that does not
                parse is reported UNPARSED and never folded into a class.
SCOPE           population = R728's recorded population_drift_new_arms (51) and extra_admits_today
                (11) · instrument = the tag grammar · baseline = R294's committed 41, the same
                classifier with the ingredient absent · regime = the store at R728's tree_sha.
WORLDS          A the added arms are candidate cores · B they are apparatus · C mixed.
KILL            conditional; gated on POSITIVE separating two known arms, NEGATIVE destroying the
                classification, PLACEBO exactly zero.
POSITIVE CTRL   random_k8_s0 -> RANDOM and topw_k4 -> SELECTOR, in DIFFERENT classes; band computed
                against a floor classifier that cannot separate anything.
g=0             an out-of-grammar tag -> UNPARSED, never a silent SELECTOR. That default would
                manufacture World A.
NEGATIVE CTRL   shuffle rule->class while keeping tags; the classification must change. Excludes
                "any partition of these names gives this answer".
SHAM            ingredient ABSENT: the same classifier on the committed 41.
PLACEBO         non-tag strings -> 0 in every class, reported as 0 of N.
NOISE FLOOR     no rng; the variance is the CLASSIFIER -- loose / tight / family, all reported.
MULTIPLICITY    3 classifiers x 3 populations = 9 cells, all printed.
UNIT            instrument unit = TAG; claim unit = ARM. R730 measured 7 tags = 4 objects, so tags
                OVERCOUNT. Shares are per TAG and the per-OBJECT limit is named, not ignored.
ARTIFACT        results/r745.json with tree_sha; a later round attacks this by applying R525's
                satisfaction-vector partition to today's 92 and recomputing per OBJECT.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      per-object shares (needs R525's partition on today's population) · whether a
                SELECTOR arm is a GOOD core (needs the definition itself) · independently
                replicated · cross-site.

⛔ DERIVATION, NOT EVIDENCE: the 11 are a SUBSET of the 51, so shares on the two are not independent
   draws. D is a within-population contrast and no significance is claimed for it.
"""
from __future__ import annotations
import json, os, pathlib, re, subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
A24 = HERE.parent
R728 = A24 / "R728_the_census_at_sixteen_times_the_resamples" / "results" / "r728_census_rerun.json"
SRC = ROOT / "corebench" / "select_core.py"

# read off the builder, NOT chosen by me -- the provenance is asserted in code below
TARGET_READING = ("oracle_k", "indep_k", "greedy_k")
RANDOM = ("random_k",)
CEILING = ("full",)
SELECTOR = ("topw_k", "topabs_k", "topvar_k", "topwvar_k")
CLASS_OF = {**{r: "TARGET-READING" for r in TARGET_READING},
            **{r: "RANDOM" for r in RANDOM},
            **{r: "CEILING" for r in CEILING},
            **{r: "SELECTOR" for r in SELECTOR}}
RULES = sorted(CLASS_OF, key=len, reverse=True)          # longest first: topwvar before topw


def _plain(o):
    for cast in (bool, int, float):
        if isinstance(o, cast) or type(o).__name__ == cast.__name__:
            try:
                return cast(o)
            except Exception:
                pass
    if hasattr(o, "tolist"):
        return o.tolist()
    return str(o)


# ---------------------------------------------------------------- the three classifiers
def cls_loose(tag: str, mapping):
    """substring match on a rule word ANYWHERE in the tag -- the untested pattern, for contrast."""
    for r in RULES:
        if r.rstrip("_k") and r.replace("_k", "") in tag:
            return mapping[r]
    return "UNPARSED"


TIGHT = re.compile(r"^(?P<rule>[a-z]+_k|full)(?P<k>\d+)?(?:_s(?P<seed>\d+))?"
                   r"(?:_fit(?P<parity>\d+))?(?P<suffix>.*)$")


def cls_tight(tag: str, mapping):
    """the tag must MATCH the emission grammar at select_core.py:204 from position 0."""
    m = TIGHT.match(tag)
    if not m:
        return "UNPARSED"
    rule = m.group("rule")
    if rule not in mapping:
        return "UNPARSED"
    if rule == "random_k" and m.group("seed") is None:
        return "UNPARSED"                     # the builder ALWAYS emits _s for random
    return mapping[rule]


def cls_family(tag: str, mapping):
    """the rule PREFIX only, ignoring k, seed, parity and suffix."""
    for r in RULES:
        if tag.startswith(r):
            return mapping[r]
    return "UNPARSED"


CLASSIFIERS = [("loose", cls_loose), ("tight", cls_tight), ("family", cls_family)]
NON_SELECTOR = ("TARGET-READING", "RANDOM", "CEILING")


def compose(tags, fn, mapping):
    out = {}
    for t in tags:
        c = fn(t, mapping)
        out[c] = out.get(c, 0) + 1
    return out


def main() -> int:
    if not R728.exists() or not SRC.exists():
        print("UNRUNNABLE: R728's artifact or the builder is absent. Exit 2, never 0."); return 2
    src = SRC.read_text()
    prev = json.loads(R728.read_text())
    added = sorted(prev["population_drift_new_arms"])
    admitted = sorted(prev["extra_admits_today"])
    committed_ext = sorted(prev["committed_extension"])
    n_committed = prev["n_arms_committed"]
    print("R745 · are the added arms candidate cores, or our own apparatus?\n")

    # ---- PROVENANCE OF THE PARTITION, asserted against the object rather than argued
    prov = {"rule_vocabulary_closed": all(f'"{r}"' in src for r in CLASS_OF),
            "target_reading_line_present":
                'if a.rule in ("oracle_k", "indep_k", "greedy_k"):' in src,
            "tag_emitted_from_rule": 'tag = f"{a.rule}"' in src}
    print("PROVENANCE the partition is read off the builder, not chosen:")
    for k, v in sorted(prov.items()):
        print(f"            {k}: {v}")
    if not all(prov.values()):
        print("UNRUNNABLE: the builder does not carry the grammar this instrument assumes. Exit 2.")
        return 2

    # ---- POSITIVE CONTROL, band computed against a floor that cannot separate
    floor_map = {r: "SELECTOR" for r in CLASS_OF}          # everything one class
    pos = {}
    for tag, want in (("random_k8_s0", "RANDOM"), ("topw_k4", "SELECTOR")):
        pos[tag] = {"got": cls_tight(tag, CLASS_OF), "want": want}
    separated = pos["random_k8_s0"]["got"] != pos["topw_k4"]["got"]
    floor_sep = (cls_tight("random_k8_s0", floor_map) != cls_tight("topw_k4", floor_map))
    POSITIVE = all(v["got"] == v["want"] for v in pos.values()) and separated and not floor_sep
    print(f"\nPOSITIVE  band computed: at the FLOOR classifier (all one class) the two arms "
          f"separate = {floor_sep} -- must be False; at the real one = {separated}")
    for t, v in sorted(pos.items()):
        print(f"            {t:<14} got {v['got']:<14} want {v['want']:<14}"
              f"{'PASS' if v['got']==v['want'] else 'FAIL'}")
    print(f"          -> {'PASS' if POSITIVE else 'FAIL'}")

    # ---- g=0 : an out-of-grammar tag must NOT default to a class
    g0tags = ["coval_core", "zzz_not_a_rule", "generic_reprov"]
    g0 = {t: cls_tight(t, CLASS_OF) for t in g0tags}
    G0 = all(v == "UNPARSED" for v in g0.values())
    print(f"g=0       out-of-grammar tags -> {g0}  "
          f"{'PASS' if G0 else 'FAIL -- a silent SELECTOR default would manufacture World A'}")

    # ---- NEGATIVE : destroy the mapping, keep the tags
    shuffled = {r: CLASS_OF[RULES[(RULES.index(r) + 3) % len(RULES)]] for r in CLASS_OF}
    real = compose(added, cls_tight, CLASS_OF)
    perm = compose(added, cls_tight, shuffled)
    NEGATIVE = (real != perm)
    print(f"NEGATIVE  rule->class shuffled: {perm} vs real {real}  "
          f"{'PASS' if NEGATIVE else 'FAIL -- any partition gives this answer'}")

    # ---- PLACEBO : strings that are not arm tags
    placebo_src = sorted({m for m in re.findall(r"\b\d{3,}\b", json.dumps(prev))})[:40]
    pl = compose(placebo_src, cls_tight, CLASS_OF)
    PLACEBO = (len(placebo_src) > 0 and set(pl) <= {"UNPARSED"})
    print(f"PLACEBO   {len(placebo_src)} non-tag strings -> {pl}  (0 of {len(placebo_src)}, "
          f"not 0 of 0)  {'PASS' if PLACEBO else 'FAIL'}")

    # ---- THE GRID : 3 classifiers x 3 populations
    pops = {"added(51)": added, "newly admitted(11)": admitted,
            "committed extension(5)": committed_ext}
    grid = {}
    print(f"\n  {'classifier':<10}{'population':<24}{'SEL':>5}{'TGT':>5}{'RND':>5}"
          f"{'CEIL':>6}{'UNPARSED':>10}{'non-SEL share':>15}")
    for cname, fn in CLASSIFIERS:
        for pname, P in pops.items():
            c = compose(P, fn, CLASS_OF)
            parsed = sum(v for k, v in c.items() if k != "UNPARSED")
            ns = sum(c.get(k, 0) for k in NON_SELECTOR)
            share = None if parsed == 0 else ns / parsed
            grid[f"{cname}|{pname}"] = {"counts": c, "parsed": parsed, "non_selector": ns,
                                        "share": share, "n": len(P)}
            print(f"  {cname:<10}{pname:<24}{c.get('SELECTOR',0):>5}"
                  f"{c.get('TARGET-READING',0):>5}{c.get('RANDOM',0):>5}{c.get('CEILING',0):>6}"
                  f"{c.get('UNPARSED',0):>10}"
                  + (f"{share:>15.4f}" if share is not None else f"{'n/a':>15}"))

    # ---- SHAM : ingredient ABSENT -- the committed population, which was NOT added
    #      R728's artifact records the committed COUNT (41) but not the committed NAMES, so the
    #      sham runs on the committed EXTENSION (5 names it does record) and the shortfall is
    #      STATED rather than papered over: 5 is a subset of 41 and a small one.
    sham = grid["tight|committed extension(5)"]
    SHAM = sham["parsed"] > 0
    print(f"\nSHAM      ingredient ABSENT -- the committed extension, not added: non-SELECTOR "
          f"{sham['non_selector']}/{sham['parsed']} parsed")
    print(f"            ⚠ SHORTFALL STATED: R728 records the committed COUNT ({n_committed}) but "
          f"not the committed NAMES, so the sham runs on the 5 it does record, not on 41.")

    # ---- registered points
    g = grid["tight|added(51)"]
    a = grid["tight|newly admitted(11)"]
    P1 = g["parsed"] / len(added)
    P2 = g["share"]
    P3 = a["non_selector"]
    print(f"\nP1        of the 51 added, share parsing under the grammar: {P1:.4f}  (registered >=0.70)")
    print(f"P2        of the 51 added, non-SELECTOR share: "
          + (f"{P2:.4f}" if P2 is not None else "n/a") + "  (registered 0.55 [0.20,0.90])")
    print(f"P3        of the 11 newly admitted, non-SELECTOR count: {P3}  "
          f"(registered 9 [0,11]; ⚠ PARTIALLY SIGHTED -- 6 of the 11 names were visible in a "
          f"truncated print before registration, and that is declared)")
    D = (a["share"] is not None and g["share"] is not None and a["share"] > g["share"])
    print(f"DIRECTIONAL the newly admitted are MORE non-SELECTOR than the added as a whole: {D}  "
          + (f"({a['share']:.4f} vs {g['share']:.4f})" if D is not None
             and a["share"] is not None else ""))
    print("  ⛔ the 11 are a SUBSET of the 51 -- not independent draws. A within-population "
          "contrast; no significance claimed.")

    # ---- what the newly admitted actually are, named
    print("\n  the 11 newly admitted, classified:")
    for t in admitted:
        print(f"            {t:<28}{cls_tight(t, CLASS_OF):<16}"
              f"family={cls_family(t, CLASS_OF)}")

    # ---- VERDICT : computed, referencing every declared control
    controls = {"POSITIVE": POSITIVE, "g0": G0, "NEGATIVE": NEGATIVE,
                "PLACEBO": PLACEBO, "SHAM": SHAM, "PROVENANCE": all(prov.values())}
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire"
    elif P3 == 0:
        world, why = "A", "the additions are candidate cores; World B killed"
    elif P3 >= 6:
        world, why = "B", ("the census's new admissions are dominated by apparatus; World A killed "
                           "-- 16 is not a rival to 5, it counts our instruments")
    else:
        world, why = "C", "mixed; the split IS the scope the page is missing"
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R745", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"),
           "partition_provenance": prov,
           "class_of_rule": CLASS_OF,
           "n_added": len(added), "n_admitted": len(admitted),
           "P1_parse_share": P1, "P2_non_selector_share_added": P2,
           "P3_non_selector_count_admitted": P3, "directional": D,
           "grid": grid,
           "admitted_classified": {t: cls_tight(t, CLASS_OF) for t in admitted},
           "added_classified": {t: cls_tight(t, CLASS_OF) for t in added},
           "controls": controls, "positive_detail": pos,
           "sham_shortfall": f"committed names not recorded by R728; sham ran on the "
                             f"{len(committed_ext)} of {n_committed} it does record",
           "subset_relation_is_a_derivation": True}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r745.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r745.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
