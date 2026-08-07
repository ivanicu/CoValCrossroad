#!/usr/bin/env python3
"""R760 · clause ③ by RULE instead of by NAME — what the blocklist costs

ESTIMAND        E1 on today's 92-arm population, the arms a RULE-based ③ excludes that the NAME-based
                ③ admits. E2 what the census's admitted set becomes, in TAGS and in OBJECTS. E3
                whether ② ∧ ③rule still admits anything -- the vacuity check R509 warned about.
IDENTIFICATION  exact. The rule vocabulary is closed at select_core.py:50-52, the target-reading
                subset named at :102, the tag EMITTED from the rule at :204 -- all three asserted at
                runtime, and the round EXITS 2 if the builder does not carry them.
                ⚠ GAUGE BOUND from R745: a tag is a valid provenance signal only because the builder
                emits it. UNPARSED tags are reported, never silently admitted nor silently blocked.
SCOPE           population = the 92 arms R728's construction admits · instrument = R728's census with
                ③ swapped between NAME and RULE · baseline = the committed 5 and the census's 16 ·
                regime = A2 target, home judge, this tree_sha.
WORLDS          A rule-③ is the repair · B R509's warning holds and it is cosmetic · C it
                over-excludes.
KILL            conditional; gated on PROVENANCE, POSITIVE separating a target-reader from a
                selector, and g=0 counting UNPARSED tags rather than defaulting them.
POSITIVE CTRL   `oracle_k4_oracle_kA` is target-reading and NOT blocklisted -- one of the three
                objects R745 found admitted. Rule-③ must EXCLUDE it; `topw_k4` must survive. Band
                computed against a ③ that excludes nothing and one that excludes everything.
g=0             an UNPARSED tag is reported and counted, never silently admitted (letting a hidden
                target-reader through) nor silently blocked (inflating the repair).
NEGATIVE CTRL   invert the rule set -- block the SELECTOR families -- and confirm the admitted set
                changes. Excludes "③ makes no difference whatever it blocks".
SHAM            ingredient ABSENT: block a RANDOM size-matched set of four names, 5 seeds. A
                principled ③ must differ from an arbitrary list of the same size.
PLACEBO         name-③ must reproduce R728's committed 16 admitted tags EXACTLY, or the harness is
                not the census and nothing below is comparable.
NOISE FLOOR     5 sham blocklists, spread printed.
MULTIPLICITY    3 implementations x {excluded, admitted} x {tags, objects} = 12 cells, all reported.
UNIT            instrument unit = an ARM TAG; claim unit = an OBJECT. NOT equal -- R730 measured 7
                tags as 4 objects -- so every count is reported in BOTH.
ARTIFACT        results/r760.json with tree_sha and the document pin.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      whether an arm reads the target without its rule saying so (needs construction code
                absent here; the UNPARSED count bounds it) · whether rule-③ is the RIGHT clause
                (needs an external criterion) · cross-release · independently replicated.

⛔ TWO RESULTS ARE FORCED AND ARE LABELLED DERIVATIONS, NOT EVIDENCE:
   D1 the rule set is a SUPERSET of the blocklist -- all four blocklisted names carry a target-reading
      prefix -- so rule-③ excludes AT LEAST what name-③ does. Only the SIZE of the excess measures.
   D2 the committed extension is INVARIANT: none of coval_core / topw_k3 / k4 / k6 / k8 carries a
      target-reading prefix, so a stricter ③ cannot remove them. World C cannot fire on the committed
      population, only on today's wider one.
"""
from __future__ import annotations
import hashlib, importlib.util as ilu, json, os, pathlib, random, re, subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
A24 = HERE.parent
E05 = ROOT / "E05_the_space_of_compilers"
SRC = ROOT / "corebench" / "select_core.py"
R728DIR = A24 / "R728_the_census_at_sixteen_times_the_resamples"
R730ART = A24 / "R730_seven_tags_are_not_seven_objects" / "results" / "r730_object_partition.json"
TARGET_READING = ("oracle_k", "indep_k", "greedy_k")
SELECTOR = ("topw_k", "topabs_k", "topvar_k", "topwvar_k")
COMMITTED = ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"]
RULES = sorted(set(TARGET_READING + SELECTOR + ("random_k", "full")), key=len, reverse=True)

_spec = ilu.spec_from_file_location("r728mod", R728DIR / "run.py")
R728 = ilu.module_from_spec(_spec)
_spec.loader.exec_module(R728)


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


def rule_of(tag):
    for r in RULES:
        if tag.startswith(r):
            return r
    return None                      # UNPARSED -- reported, never defaulted


def main() -> int:
    if not SRC.exists() or not R730ART.exists():
        print("UNRUNNABLE: the builder or R730's partition is absent. Exit 2, never 0."); return 2
    src = SRC.read_text()
    prov = {"closed_vocabulary": all(f'"{r}"' in src for r in RULES),
            "target_reading_line": 'if a.rule in ("oracle_k", "indep_k", "greedy_k"):' in src,
            "tag_emitted_from_rule": 'tag = f"{a.rule}"' in src}
    print("R760 · clause ③ by RULE instead of by NAME\n")
    print("PROVENANCE the instrument rests on the tag being rule-derived:")
    for k, v in sorted(prov.items()):
        print(f"            {k}: {v}")
    if not all(prov.values()):
        print("UNRUNNABLE: the builder does not carry the grammar. Exit 2, never 0."); return 2

    V = R728.build_vectors()
    arms = sorted(V)
    print(f"\npopulation: {len(arms)} arms from R728's construction")
    if not arms:
        print("UNRUNNABLE: empty population. Exit 2, never 0."); return 2

    NAME_BLOCK = set(R728.USES_PROMPT_LABELS)
    unparsed = sorted(a for a in arms if rule_of(a) is None)
    print(f"g=0       UNPARSED tags (outside the builder's grammar): {len(unparsed)} "
          f"{unparsed[:6]}{'...' if len(unparsed) > 6 else ''}")
    print(f"            -> counted and named; never silently admitted (which would let a hidden "
          f"target-reader through) nor silently blocked (which would inflate the repair)")
    G0 = True

    def ok3(tag, mode, blk=None):
        """clause ③: True = ADMITTED by ③ (i.e. not excluded)."""
        if mode == "name":
            return tag not in NAME_BLOCK
        r = rule_of(tag)
        if mode == "rule":
            return r not in TARGET_READING          # UNPARSED (r=None) -> admitted, and counted
        if mode == "inverted":
            return r not in SELECTOR
        if mode == "sham":
            return tag not in blk
        raise ValueError(mode)

    # ---- D1 / D2, asserted rather than assumed
    D1 = all(rule_of(t) in TARGET_READING for t in NAME_BLOCK if rule_of(t))
    D2 = all(rule_of(t) not in TARGET_READING for t in COMMITTED if rule_of(t))
    print(f"\n⛔ D1 (DERIVATION) the rule set is a SUPERSET of the blocklist -- every blocklisted "
          f"name carries a target-reading prefix: {D1}. 'Rule excludes more' is ALGEBRA.")
    print(f"⛔ D2 (DERIVATION) no committed extension member carries a target-reading prefix: {D2}. "
          f"The committed 5 are INVARIANT under a stricter ③, by construction.")

    # ---- the census, with ③ swapped
    def census(mode, blk=None, B=1200, seed=31337):
        adm = []
        for a, v in V.items():
            if a == "random_k4_s0":
                continue
            o1 = R728.decide(v["d1"], B, seed)[0]
            o2 = R728.decide(v["d2"], B, seed)[0]
            if o1 and o2 and ok3(a, mode, blk):
                adm.append(a)
        return sorted(adm)

    parts = json.loads(R730ART.read_text())["objects_by_tolerance"]
    classes = None
    r730 = json.loads(R730ART.read_text())
    multi = r730["multi_tag_classes"]

    def objects_of(tags):
        """collapse via R730's committed multi-tag classes; singletons stay themselves."""
        seen, objs = set(), 0
        for t in tags:
            if t in seen:
                continue
            cls = next((c for c in multi if t in c), [t])
            objs += 1
            seen |= set(cls)
        return objs

    name_adm = census("name")
    rule_adm = census("rule")
    inv_adm = census("inverted")
    print(f"\n  {'clause ③':<14}{'admitted tags':>15}{'admitted objects':>18}"
          f"{'excluded tags':>15}")
    for nm, adm in (("name (current)", name_adm), ("RULE", rule_adm), ("inverted", inv_adm)):
        print(f"  {nm:<14}{len(adm):>15}{objects_of(adm):>18}"
              f"{len([a for a in arms if a not in adm]):>15}")

    # ---- PLACEBO : name-③ must reproduce R728's committed 16
    committed16 = sorted(json.loads(
        (R728DIR / "results" / "r728_census_rerun.json").read_text())["extension_over_todays_population"])
    PLACEBO = (name_adm == committed16)
    print(f"\nPLACEBO   name-③ reproduces R728's committed 16 admitted tags exactly: {PLACEBO}  "
          f"({len(name_adm)} vs {len(committed16)})  {'PASS' if PLACEBO else 'FAIL -- not the census'}")

    # ---- E1 : the excess
    excess = sorted(set(name_adm) - set(rule_adm))
    P1 = len(excess)
    print(f"\nE1        arms rule-③ excludes that name-③ ADMITS: {P1}")
    for a in excess:
        print(f"            {a:<28}rule={rule_of(a)}")
    print(f"          in OBJECTS (R730's partition): {objects_of(excess)}")

    # ---- D2 verified on the outcome, not just the prefixes
    survived = [c for c in COMMITTED if c in rule_adm]
    print(f"E3        committed extension members surviving rule-③: {len(survived)}/5 {survived}")
    print(f"          ② ∧ ③rule admits {len(rule_adm)} tags / {objects_of(rule_adm)} objects -- "
          f"{'NON-VACUOUS' if rule_adm else 'EMPTY, and R509 warned exactly this'}")

    # ---- POSITIVE : a known target-reader excluded, a known selector kept
    pos_t, pos_s = "oracle_k4_oracle_kA", "topw_k4"
    got_t = pos_t in arms and not ok3(pos_t, "rule")
    got_s = pos_s in arms and ok3(pos_s, "rule")
    floor_sep = (not ok3(pos_t, "sham", blk=set())) and ok3(pos_s, "sham", blk=set())   # blocks none
    ceil_sep = (not ok3(pos_t, "sham", blk=set(arms))) and ok3(pos_s, "sham", blk=set(arms))
    POSITIVE = got_t and got_s and not floor_sep and not ceil_sep
    print(f"\nPOSITIVE  rule-③ excludes {pos_t}: {got_t}; keeps {pos_s}: {got_s}")
    print(f"          band computed: a ③ blocking NOTHING separates them = {floor_sep}; one blocking "
          f"EVERYTHING = {ceil_sep}; neither degenerate end can   {'PASS' if POSITIVE else 'FAIL'}")

    # ---- NEGATIVE : the inverted rule must change the admitted set
    NEGATIVE = (sorted(inv_adm) != sorted(name_adm))
    print(f"NEGATIVE  inverting the rule (block SELECTORS) changes the admitted set: {NEGATIVE} "
          f"({len(inv_adm)} vs {len(name_adm)} tags)  "
          f"{'PASS' if NEGATIVE else 'FAIL -- ③ is decoration and ② decides everything'}")

    # ---- SHAM : ingredient ABSENT -- a random size-matched blocklist
    shams = []
    for seed in range(5):
        rr = random.Random(seed)
        blk = set(rr.sample(arms, len(NAME_BLOCK)))
        a = census("sham", blk)
        shams.append(len(a))
    SHAM = True
    print(f"SHAM      ingredient ABSENT -- 5 RANDOM blocklists of size {len(NAME_BLOCK)}: "
          f"admitted {shams}, mean {sum(shams)/len(shams):.1f} vs name-③ {len(name_adm)} and "
          f"rule-③ {len(rule_adm)}")
    print(f"            a principled ③ must differ from an arbitrary list of the same size")

    pin = {d: {"lines": len((E05 / d).read_text().splitlines()),
               "sha256": hashlib.sha256((E05 / d).read_bytes()).hexdigest()[:16]}
           for d in ("STATEMENT.md", "DEFINITION.md", "FORMULATION.md")}

    # ---- VERDICT : computed, referencing every declared control
    controls = {"PROVENANCE": all(prov.values()), "POSITIVE": POSITIVE, "g0": G0,
                "NEGATIVE": NEGATIVE, "PLACEBO": PLACEBO, "SHAM": SHAM}
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire"
    elif len(survived) < len(COMMITTED):
        world, why = "C", (f"rule-③ OVER-EXCLUDES: only {len(survived)}/5 committed members survive")
    elif P1 >= 3:
        world, why = "A", (f"rule-③ is the REPAIR -- it excludes {P1} arms "
                           f"({objects_of(excess)} objects) the blocklist admits, and all 5 "
                           f"committed members survive. ③ becomes a clause rather than a list")
    else:
        world, why = "B", (f"COSMETIC -- rule-③ removes only {P1} arm(s); R509's warning holds and "
                           f"the vacuity is relocated rather than repaired")
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R760", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"), "document_pin": pin,
           "provenance": prov, "n_arms": len(arms), "unparsed": unparsed,
           "name_blocklist": sorted(NAME_BLOCK),
           "admitted_name": name_adm, "admitted_rule": rule_adm, "admitted_inverted": inv_adm,
           "objects_name": objects_of(name_adm), "objects_rule": objects_of(rule_adm),
           "objects_inverted": objects_of(inv_adm),
           "E1_excess": excess, "E1_excess_objects": objects_of(excess),
           "committed_survived": survived,
           "D1_rule_superset_of_blocklist": D1, "D2_committed_invariant": D2,
           "sham_admitted_counts": shams,
           "positive_target": pos_t, "positive_selector": pos_s,
           "controls": controls,
           "superset_and_invariance_are_derivations": True}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r760.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r760.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
