#!/usr/bin/env python3
"""
R599 -- does the deliverable state ONE definition, or several?

Found while R598's suite was running, by reading the object rather than the gates: two lines of
STATEMENT.md state the definition and they DISAGREE.

    line  90 (claim table)   "The definition is ② ∧ ③. ① and ④ are retired"        (R519)
    line 165 (formulation)   "① is DELETABLE, and the definition is ② ③ ④"          (R514, R515)

Checked against the object: R519's artifact records clause ④ dropping 0 of the 9 ②-passers,
identical to ①. So ④ adds nothing, line 90 is current, and line 165 is STALE -- written while ④
was still in and never updated when R519 retired it. That is the failure named in my own
memory: A CORRECTION MUST REACH THE ARTIFACT THAT PROVOKED IT. The retirement reached the claim
table and not the formulation section.

⚠ AND `definition_matches_the_record.py` PASSES. The gate that exists to check the definition
against the record does not catch a contradiction INSIDE the document, because its unit is
`document vs artifact` and never `document vs itself`.

So the round generalises the incident rather than just fixing the line: HOW MANY PLACES STATE
THE DEFINITION, ACROSS ALL THREE DOCUMENTS, AND DO THEY AGREE?

ESTIMAND        n_state = sites in {STATEMENT, DEFINITION, FORMULATION}.md asserting a clause
                set for "the definition", and |distinct clause sets| among them.
                1 distinct set  -> the deliverable states one definition.
                >1              -> it states several, and the count is the defect size.
IDENTIFICATION  Identified up to the recogniser. ⚠ "asserts a clause set" is a PATTERN over
                prose, so this is a search, and a search is an instrument (§4). It gets a
                positive control on text where the answer is known, a false-positive rate on
                text that discusses clauses WITHOUT defining, and its unit is written beside
                the claim's unit and required to differ-or-match explicitly.
SCOPE           population : the three deliverable .md files
                instrument : a sentence containing "the definition is" (case-folded) followed
                             within 60 chars by >=1 clause glyph from ①②③④
                             instrument unit = A SENTENCE MATCHING THE PATTERN
                             claim unit      = A PLACE THAT ASSERTS WHAT THE DEFINITION IS
                             NOT equal -- a sentence may quote, negate, or historicise. Hence
                             every hit is printed verbatim and the count is an UPPER BOUND.
                baseline   : the clause set R519's ARTIFACT supports (drops > 0 among passers)
                regime     : as committed at this sha
WORLDS          A ONE DEFINITION: all sites agree -> the incident was a single stale line and
                  is now repaired; nothing systemic.
                B SEVERAL: >=2 distinct clause sets -> the deliverable does not state a single
                  definition, and which one a reader gets depends on where they open it.
                C THE RECOGNISER IS BLIND: it finds <=1 site anywhere -> the count says nothing
                  and the incident stands alone as an anecdote.
KILL            pre-registered: if the recogniser's false-positive rate on the control text
                exceeds 0.20, no count is admissible and the verdict is UNVERIFIED.
POSITIVE CTRL   plant three synthetic sentences stating three different clause sets. The
                recogniser must find 3 sites and 3 distinct sets. Fails at g=0: on text with
                no such sentence it must find 0.
NEGATIVE CTRL   text that mentions clauses WITHOUT defining ("clause ② admits 9 arms") must
                yield 0 sites -- this is the false-positive rate the kill reads.
PLACEBO         a clause glyph that does not exist (⑨) must yield 0 sites.
SEEDS           n/a, deterministic.
MULTIPLICITY    3 documents x 1 recogniser + 3 control corpora. All reported.
ARTIFACT        results/one_definition.json
IMPOSSIBLE      construct validity for "this sentence ASSERTS the definition": intent is not in
                the string; a historicised statement reads identically to a live one. Every
                hit is printed so a reader can overrule the count, and the count is an upper
                bound, never a verdict on the prose.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
GLYPH = "①②③④"
# ⛔ v1: `(.{0,60})` with re.S consumed ACROSS sentence boundaries, so finditer's
# non-overlapping matches cannibalised each other -- 3 planted sentences were found as 1, and
# the positive control caught it. The window now stops at the first sentence end or newline.
PAT = re.compile(r"the definition is([^\n.]{0,70})", re.I)
# ⛔ v1 also captured clauses the sentence RETIRES: line 90 reads "The definition is ② ∧ ③.
# ① and ④ are retired" and v1 recorded ①②③④. A recogniser that cannot tell assertion from
# retirement is measuring mentions, not definitions. The tail is now cut at the first negation
# cue, and BOTH readings are reported as a specification axis rather than one being chosen.
# ⭐ L81 SAYS ANNOTATE, NEVER REWRITE — so a superseded sentence STAYS IN THE DOCUMENT, and a
# recogniser counting ASSERTED sets can never reach 1 under that doctrine. The metric and the rule
# were in conflict, which only became visible after the repair landed and the count did not move.
# The estimand is therefore LIVE sets: a site is dead if a supersession marker follows it closely.
SUPERSEDED = re.compile(r"SUPERSEDED|superseded|no longer the definition|predates", re.I)
NEG = re.compile(r"\b(are |is |be )?(retired|deletable|dropped|removed|excluded)\b|"
                 r"\bnot\b|\bno longer\b", re.I)


def sites(text, glyphs=GLYPH, trim_negation=True):
    out = []
    for m in PAT.finditer(text):
        tail = m.group(1)
        raw = sorted({g for g in glyphs if g in tail})
        n = NEG.search(tail)
        trimmed = sorted({g for g in glyphs if g in tail[:n.start()]}) if n else raw
        cs = trimmed if trim_negation else raw
        if cs:
            ln = text[:m.start()].count("\n") + 1
            after = text[m.end(): m.end() + 260]
            dead = bool(SUPERSEDED.search(after))
            out.append({"line": ln, "clauses": "".join(cs), "clauses_raw": "".join(raw),
                        "live": not dead,
                        "negation_cue": n.group(0) if n else None,
                        "verbatim": re.sub(r"\s+", " ",
                                           text[max(0, m.start()-10):m.end()])[:150]})
    return out


def main():
    docs = {n: (E05 / n) for n in ("STATEMENT.md", "DEFINITION.md", "FORMULATION.md")}
    missing = [n for n, p in docs.items() if not p.is_file()]
    if missing:
        print(f"UNRUNNABLE: absent documents {missing}. Exit 2, never 0.")
        return 2

    # ---- CONTROLS FIRST -----------------------------------------------------------
    print("─── CONTROLS ───")
    plant = ("The definition is ② ∧ ③ here.\n\nThe definition is ② ③ ④ over there.\n\n"
             "The definition is ① ∧ ② somewhere else.\n")
    ps = sites(plant)
    pos_ok = len(ps) == 3 and len({s["clauses"] for s in ps}) == 3
    print(f"  POSITIVE  3 planted sentences, 3 different sets -> found {len(ps)} site(s), "
          f"{len({s['clauses'] for s in ps})} distinct -> {'PASS' if pos_ok else '⛔ FAIL'}")
    g0 = sites("nothing here defines anything at all.\n")
    print(f"  g=0       text with no such sentence -> {len(g0)} site(s) -> "
          f"{'PASS (can fail)' if not g0 else '⛔ FAIL'}")
    negtxt = ("clause ② admits 9 arms and clause ③ drops 4 of them. "
              "Under ① nothing is dropped. The clauses ①②③④ were each measured.\n")
    ns = sites(negtxt)
    fpr = len(ns) / max(1, len(re.findall(r"[.!?]", negtxt)))
    neg_ok = fpr <= 0.20
    print(f"  NEGATIVE  clauses mentioned but not defined -> {len(ns)} site(s), "
          f"FPR={fpr:.3f} -> {'PASS' if neg_ok else '⛔ FAIL'}")
    plc = sum(len(sites(p.read_text(), glyphs="⑨")) for p in docs.values())
    plc_ok = plc == 0
    print(f"  PLACEBO   nonexistent glyph ⑨ across all three -> {plc} site(s) -> "
          f"{'PASS' if plc_ok else '⛔ FAIL'}")
    controls_ok = pos_ok and not g0 and neg_ok and plc_ok

    # ---- BASELINE from the artifact, not from any document ------------------------
    r519 = next(iter((E05 / "A24_what_the_definition_costs").glob("R519_*/results/*.json")), None)
    supported = None
    if r519:
        j = json.loads(r519.read_text())
        name2glyph = {"one": "①", "two": "②", "three": "③", "four": "④"}
        keep = {name2glyph[k] for k, v in j["per_clause"].items()
                if v.get("n_passers_dropped", 0) > 0}
        keep.add("②")                      # ② is the baseline the others are measured against
        supported = "".join(sorted(keep, key=GLYPH.index))
        print(f"\n─── BASELINE FROM THE ARTIFACT (R519, n_arms={j['n_arms']}, "
              f"n_pass2={j['n_pass2']}) ───")
        for k, v in j["per_clause"].items():
            print(f"    clause {k:<6} drops {v['n_passers_dropped']} of {j['n_pass2']} passers")
        print(f"    -> clause set the ARTIFACT supports: {supported}")

    # ---- THE MEASUREMENT ----------------------------------------------------------
    print(f"\n─── SITES ASSERTING A DEFINITION (upper bound; every hit printed) ───")
    found, allsets = {}, []
    for n, p in docs.items():
        s = sites(p.read_text())
        found[n] = s
        allsets += [x["clauses"] for x in s if x["live"]]
        print(f"  {n} — {len(s)} site(s)")
        for x in s:
            print(f"    line {x['line']:>5}  clauses {x['clauses']:<5} "
                  f"{'LIVE ' if x['live'] else 'DEAD '} …{x['verbatim']}…")
    raw_sets = sorted({x["clauses_raw"] for s in found.values() for x in s if x["live"]})
    print(f"\n  SPECIFICATION AXIS — negation handling:")
    print(f"    trimmed at the first negation cue : {sorted(set(allsets))}")
    print(f"    raw, every glyph in the window    : {raw_sets}")
    distinct = sorted(set(allsets))
    print(f"\n  distinct clause sets asserted across the deliverable: {len(distinct)} "
          f"{distinct}")
    if supported:
        agree = [c for c in distinct if c == supported]
        print(f"  agreeing with the artifact ({supported}): {len(agree)} of {len(distinct)}")

    # ---- VERDICT, a function of the controls, nothing written between --------------
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no count is admissible"
    elif len(allsets) <= 1:
        world = ("C THE RECOGNISER IS BLIND — it finds at most one site anywhere, so the "
                 "count says nothing and the incident stands alone")
    elif len(distinct) == 1:
        world = (f"A ONE DEFINITION — all {len(allsets)} site(s) assert {distinct[0]}")
    else:
        world = (f"B SEVERAL — {len(allsets)} site(s) assert {len(distinct)} DIFFERENT clause "
                 f"sets {distinct}; which definition a reader gets depends on where they open "
                 f"the deliverable")
    print(f"  {world}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "one_definition.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "artifact_supported_set": supported,
        "sites": found, "distinct_sets": distinct, "n_live_sites": len(allsets),
        "n_sites_total": sum(len(v) for v in found.values()),
        "positive_control": {"found": len(ps), "distinct": len({s['clauses'] for s in ps})},
        "negative_control_fpr": fpr, "placebo_hits": plc,
        "instrument_vs_claim": ("instrument unit = a sentence matching the pattern; claim unit "
                                "= a place asserting what the definition IS. NOT equal, so "
                                "every hit is printed and the count is an UPPER BOUND"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'one_definition.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
