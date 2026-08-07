#!/usr/bin/env python3
"""R1082 — the anchoring gate reads `re.search`: the FIRST home of each anchor, and nothing else.

R1049 measured this defect class in the CURRENCY gate: 16 of 63 registered facts are multi-home, so
a PASS is not attributable to the annotation that was supposed to carry it. **The repair never
crossed to the sibling gate.** `definition_matches_the_record.py:1634` is `re.search(pat, text)` over
the whole 2774-line document, once per anchor, 343 anchors. Whatever a later occurrence says is
structurally invisible.

That is a fix landing on one path of two, and the invariant nobody named is: *an anchor identifies a
SENTENCE, and a pattern that matches more than one sentence has not identified anything.*

ESTIMAND        Over the 343 anchors of `definition_matches_the_record.ASSERTIONS`, against the
                committed DEFINITION.md:
                  Q1  n_multi   -- anchors matching MORE THAN ONCE
                  Q2  n_disagree-- anchors whose matches capture MORE THAN ONE DISTINCT VALUE
                  Q3  n_wrongfirst -- anchors in Q2 where the FIRST match (the one the gate reads)
                                     is NOT the value that agrees with the artifact
                Q3 is the one that decides anything: it is the count of quantities the document
                states twice, inconsistently, where the gate is green by ORDER rather than by fact.
IDENTIFICATION  fully identified: patterns, document and artifacts are all committed and the gate's
                own comparison function is imported rather than re-implemented.
SCOPE           population: the 343 committed anchors. instrument: the gate module itself, imported.
                baseline: the pattern's match count against a document it was not written for.
                regime: this checkout, this DEFINITION.md.
WORLDS          A ANCHORED       each pattern names one sentence; first-match is not a choice.
                                 predicts Q1 ~= 0.
                B UNATTRIBUTABLE multi-home but the homes AGREE: the PASS cannot be attributed to a
                                 sentence, but no statement is wrong. predicts Q1 > 0, Q2 = 0.
                C CONTRADICTED   the document states a checked quantity twice with DIFFERENT values
                                 and the gate is green because `re.search` stops at the first.
                                 predicts Q2 > 0, and Q3 > 0 makes it live rather than latent.
KILL            pre-registered. Evaluated ONLY if the control gate opens.
                  World C is ADMITTED only if Q2 >= 1 AND, for at least one such anchor, a non-first
                  captured value disagrees with the artifact under the gate's OWN `same()`. Q2 >= 1
                  with every value agreeing is world B and must be reported as B, not as C.
                  If Q1 == 0 the whole line is dead and this round is closure on world A.
⛔ THE PRE-REGISTERED KILL WAS MIS-SPECIFIED AND ITS VERDICT IS WITHHELD. Q2 = 3 satisfies the
   condition as written, and the condition as written is wrong: this instrument's unit is *a regex
   match capturing a number*, while world C's unit is *a statement of the same quantity*. §4 requires
   those to be EQUAL before the control is designed, and I wrote the kill without checking. Read from
   the object, the three hits are three DIFFERENT quantities -- R348's POOL[0:k] percentile then
   R812's POOL[0:4] percentile; R432's headroom floor then an unrelated token-Jaccard floor;
   `oracle_k4`'s SCORE then its mean selection POSITION. **C is UNVERIFIED: never ADMITTED, never
   OVERTURNED.** Folding it into either would manufacture a permanent verdict.
⭐ WORLD D, ADDED AFTER THE FACT AND LABELLED AS SUCH. The consequence needs no semantic judgement:
   a GAUGE TEST. Prepending text to a document must leave a claim about the document's CONTENT
   invariant. Prepend the SECOND home's own sentence and re-run THE REAL GATE. This was not
   pre-registered; its strength is that it executes the gate under test and carries its own control
   (prepending a number-free paragraph must change nothing), not that it was declared first.
POSITIVE CTRL   plant, into a COPY of DEFINITION.md, a second occurrence of a real anchor's sentence
                carrying a CORRUPTED value. Required, all computed: (i) this round's counter reports
                n=2 and n_distinct=2; (ii) the gate, run on the planted copy, still exits 0 -- the
                blindness, computed rather than asserted. Retention 1.0; MDE is one occurrence.
g=0 GUARD       the same measurement on the UNPLANTED copy must return the anchor's real counts. If
                the counter reported n>1 without a plant on an anchor known to be single-home, it
                would be counting its own artefact.
NEGATIVE CTRL   plant a second occurrence with the SAME value: n=2, n_distinct=1, gate exits 0 and
                that is CORRECT. Separates "the document repeats itself" from "the document
                contradicts itself" -- without it, Q1 would be read as a defect count.
SHAM            the same operation minus the ingredient: plant the sentence with the NUMBER REMOVED,
                so the pattern cannot match it. Match count must be unchanged. This shows the
                counter responds to the captured value and not to the surrounding prose.
PLACEBO         run all 343 patterns against a document they were not written for (the concatenated
                round READMEs). A pattern that fires there is promiscuous, and its match count in
                DEFINITION.md is not evidence of a second HOME. Must be near zero.
NOISE FLOOR     the placebo rate above, per specification cell.
MULTIPLICITY    all 343 anchors are reported by class, not only the multi-home ones.
SPECIFICATION   region      whole document vs the statement region the gate actually reads
                overlap     non-overlapping finditer vs overlapping scan
                normalise   with and without the gate's own comma / U+2212 normalisation
ARTIFACT        results/first_home_only.json with the source hash.
REPRODUCIBILITY the measurement is deterministic; run twice, required byte-identical.
IMPOSSIBLE      cross-repository -- N/A, would need a second document with its own anchor set.
                Author intent for each duplicated sentence -- N/A, would need the transcript.
"""
from __future__ import annotations

import hashlib
import importlib
import importlib.util
import io
import json
import pathlib
import re
import shutil
import sys
import tempfile
from contextlib import redirect_stdout

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
OUT = HERE / "results" / "first_home_only.json"

sys.path.insert(0, str(ROOT / "assurance"))
G = importlib.import_module("definition_matches_the_record")     # ⭐ the gate itself, imported

# ⭐ THE MEASUREMENT IS PINNED TO THE REVISION IT WAS MADE AGAINST, because the repair ships in the
#    same commit. Reading the anchors from the live file would regenerate this artifact from the
#    FIXED gate and the finding would silently disappear from its own evidence. `PINNED` is the
#    commit that was HEAD when the four multi-home anchors were measured.
PINNED = "e0f433c1"


PINNED_TMP = ROOT / "assurance" / "_r1082_pinned_gate.py"    # inside assurance/ so its ROOT resolves


def pinned_module():
    """THE GATE AS COMMITTED AT `PINNED`, importable and runnable.

    Kept alive for the whole round so the BEFORE and AFTER verdicts are two executions of two real
    gates rather than one execution and one recollection. Removed in main()'s finally."""
    import subprocess
    src = subprocess.run(["git", "-C", str(ROOT), "show",
                          f"{PINNED}:assurance/definition_matches_the_record.py"],
                         capture_output=True, text=True, timeout=60, check=True).stdout
    PINNED_TMP.write_text(src)
    spec = importlib.util.spec_from_file_location("_r1082_pinned_gate", PINNED_TMP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def drop_pinned():
    PINNED_TMP.unlink(missing_ok=True)
    for q in (ROOT / "assurance" / "__pycache__").glob("_r1082_pinned_gate*"):
        q.unlink(missing_ok=True)


def norm(s: str, on: bool = True) -> float | None:
    """the gate's OWN conversion, at line 1639. Reused, not re-implemented."""
    try:
        return float(s.replace(",", "").replace("−", "-")) if on else float(s)
    except ValueError:
        return None


def scan(text: str, overlap: bool = False, normalise: bool = True,
         anchors: dict | None = None) -> dict:
    """every home of every anchor, not just the first."""
    out = {}
    for label, pat in (anchors if anchors is not None else G.ASSERTIONS).items():
        rx = re.compile(pat)
        if overlap:
            hits, i = [], 0
            while i < len(text):
                m = rx.search(text, i)
                if not m:
                    break
                hits.append(m)
                i = m.start() + 1
        else:
            hits = list(rx.finditer(text))
        vals = [norm(m.group(1), normalise) for m in hits]
        vals = [v for v in vals if v is not None]
        out[label] = {"n": len(hits), "vals": vals,
                      "distinct": sorted(set(vals)),
                      "spans": [(m.start(), m.end()) for m in hits][:8]}
    return out


def run_gate(doc: pathlib.Path, mod=None) -> int:
    """execute a real gate against a given document. Its verdict, not my model of it."""
    m = mod or G
    keep = m.DOC
    m.DOC = doc
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = m.main()
        return rc
    finally:
        m.DOC = keep


def main() -> int:
    doc = ROOT / "E05_the_space_of_compilers" / "DEFINITION.md"
    if not doc.exists():
        print("  UNRUNNABLE: DEFINITION.md absent. Exit 2, never 0.")
        return 2
    text = doc.read_text(encoding="utf-8")
    truth = G.derive()
    try:
        P = pinned_module()
    except Exception as e:                                   # noqa: BLE001 - reported, not hidden
        print(f"  UNRUNNABLE: the pinned gate could not be loaded ({e}). Exit 2, never 0.")
        return 2
    A, pin = dict(P.ASSERTIONS), PINNED
    if not A:
        print("  UNRUNNABLE: the pinned anchor set is empty. Exit 2, never 0.")
        return 2
    if not G.ASSERTIONS:
        print("  UNRUNNABLE: no anchors declared. Exit 2, never 0.")
        return 2

    # ---------------------------------------------------------------- the measurement
    base = scan(text, anchors=A)
    multi = {k: v for k, v in base.items() if v["n"] > 1}
    disagree = {k: v for k, v in base.items() if len(v["distinct"]) > 1}

    wrongfirst, latent = {}, {}
    for k, v in disagree.items():
        tv = truth.get(k, (None,))[0]
        if tv is None:
            continue
        agreeing = [x for x in v["distinct"] if G.same(x, tv)]
        first_ok = bool(v["vals"]) and G.same(v["vals"][0], tv)
        rec = {"first": v["vals"][0] if v["vals"] else None, "distinct": v["distinct"],
               "artifact": tv, "n": v["n"], "first_agrees": first_ok,
               "any_agrees": bool(agreeing)}
        if not first_ok:
            wrongfirst[k] = rec
        elif len(v["distinct"]) > 1:
            latent[k] = rec          # green by ORDER: a later home states something else

    # ---------------------------------------------------------------- controls
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="r1082_"))
    ctrl, plant_label = {}, None
    try:
        # choose a real single-home anchor whose artifact value is known -- the plant target
        for k, v in base.items():
            if v["n"] == 1 and truth.get(k, (None,))[0] is not None and v["vals"]:
                plant_label = k
                break
        if plant_label is None:
            print("  UNRUNNABLE: no single-home evaluable anchor to plant against. Exit 2.")
            return 2

        pv = base[plant_label]["vals"][0]
        m = re.search(A[plant_label], text)
        sentence = text[max(0, m.start() - 120): m.end() + 120]

        def planted(new_sentence: str) -> pathlib.Path:
            p = tmp / "DEFINITION.md"
            p.write_text(text + "\n\n" + new_sentence + "\n", encoding="utf-8")
            return p

        # POSITIVE: a second home carrying a CORRUPTED value
        corrupt = sentence.replace(m.group(1), f"{pv + 1.0:g}", 1)
        pos_doc = planted(corrupt)
        pos_scan = scan(pos_doc.read_text(encoding="utf-8"), anchors=A)[plant_label]
        pos_rc = run_gate(pos_doc)
        ctrl["POSITIVE the counter sees the planted second home"] = pos_scan["n"] == 2
        ctrl["POSITIVE the planted home carries a DIFFERENT value"] = len(pos_scan["distinct"]) == 2
        ctrl["POSITIVE the GATE stays green on the contradicted document"] = pos_rc == 0

        # NEGATIVE: a second home carrying the SAME value -- repetition, not contradiction
        neg_doc = planted(sentence)
        neg_scan = scan(neg_doc.read_text(encoding="utf-8"), anchors=A)[plant_label]
        ctrl["NEGATIVE a repeated home is n=2 but distinct=1"] = (
            neg_scan["n"] == 2 and len(neg_scan["distinct"]) == 1)
        ctrl["NEGATIVE the gate is green on mere repetition, correctly"] = run_gate(neg_doc) == 0

        # SHAM: the same sentence with the NUMBER removed -- the pattern cannot match it
        sham_doc = planted(sentence.replace(m.group(1), "the value", 1))
        sham_scan = scan(sham_doc.read_text(encoding="utf-8"), anchors=A)[plant_label]
        ctrl["SHAM a home without the number does not count as a home"] = sham_scan["n"] == 1

        # g=0: the unplanted copy must reproduce the real counts
        g0_doc = planted("")
        ctrl["g=0 the unplanted copy reproduces the real count"] = (
            scan(g0_doc.read_text(encoding="utf-8"), anchors=A)[plant_label]["n"] == 1)
        ctrl["g=0 the gate is green on the unmodified document"] = run_gate(doc) == 0

        # PLACEBO: the patterns against a document they were not written for
        foreign = "\n".join(p.read_text(errors="replace")
                            for p in sorted(ROOT.glob("E*/A*/R*/README.md"))[:400])
        fscan = scan(foreign, anchors=A)
        promiscuous = sorted(k for k, v in fscan.items() if v["n"] > 0)
        ctrl["PLACEBO fewer than a tenth of patterns fire on a foreign document"] = (
            len(promiscuous) < len(A) / 10)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---------------------------------------------------------------- specification curve
    spec = []
    region_start = text.find("resolvably beats")
    regions = {"whole_document": text,
               "from_first_clause_home": text[region_start:] if region_start >= 0 else text}
    for rname, rtext in regions.items():
        for overlap in (False, True):
            for normalise in (True, False):
                s = scan(rtext, overlap=overlap, normalise=normalise, anchors=A)
                spec.append({"region": rname, "overlap": overlap, "normalise": normalise,
                             "anchors": len(s),
                             "multi_home": sum(1 for v in s.values() if v["n"] > 1),
                             "disagreeing": sum(1 for v in s.values() if len(v["distinct"]) > 1),
                             "unmatched": sum(1 for v in s.values() if v["n"] == 0)})

    # ---------------------------------------------------------------- ORDER DEPENDENCE, executed
    # ⛔ THE PRE-REGISTERED WORLD C WAS MIS-SPECIFIED AND IS NOT ADMITTED. Its kill asked whether the
    #    document states one quantity twice with different values. My instrument's unit is "a regex
    #    match capturing a number"; that claim's unit is "a statement of the same quantity". §4:
    #    those must be EQUAL before the control is even designed, and they are not. Reading the three
    #    hits from the object settles it -- `published_ref_pctile` hits R348's POOL[0:k] and then
    #    R812's POOL[0:4]; `r432_floor` hits R432's headroom floor and then an unrelated
    #    token-Jaccard floor; `r485_oracle` hits `oracle_k4`'s SCORE and then its mean selection
    #    POSITION. Three different quantities, not three contradictions. C is NOT ADMITTED.
    # ⭐ WHAT IS ADMISSIBLE IS THE CONSEQUENCE, AND IT NEEDS NO SEMANTIC JUDGEMENT AT ALL. A gauge
    #    test: prepending text to a document must leave a claim about the document's CONTENT
    #    invariant. Prepend the SECOND home's own sentence and re-run the real gate. If the verdict
    #    flips, the gate binds by DOCUMENT ORDER, and its greenness is a fact about layout.
    order = {}
    tmp2 = pathlib.Path(tempfile.mkdtemp(prefix="r1082_order_"))
    try:
        for k in sorted(set(list(wrongfirst) + list(latent))):
            hits = list(re.finditer(A[k], text))
            if len(hits) < 2:
                continue
            second = text[max(0, hits[1].start() - 200): hits[1].end() + 60]
            p = tmp2 / "DEFINITION.md"
            p.write_text(second + "\n\n" + text, encoding="utf-8")
            moved = scan(p.read_text(encoding="utf-8"), anchors=A)[k]
            tv = truth.get(k, (None,))[0]
            order[k] = {
                "first_value_after_prepending": moved["vals"][0] if moved["vals"] else None,
                "artifact": tv,
                "gate_still_agrees": bool(moved["vals"]) and tv is not None
                                     and G.same(moved["vals"][0], tv),
                "PINNED_gate_exit_code": run_gate(p, P),      # the gate as it was: BEFORE
                "REPAIRED_gate_exit_code": run_gate(p),       # the gate in this commit: AFTER
            }
        # CONTROL on the gauge test itself: prepending an IRRELEVANT paragraph must NOT flip
        # anything. Without this, a flip could be caused by prepending rather than by the sentence.
        p = tmp2 / "DEFINITION.md"
        p.write_text("Lorem ipsum, carrying no anchor and no number.\n\n" + text, encoding="utf-8")
        ctrl["GAUGE prepending a number-free paragraph leaves the gate green"] = run_gate(p) == 0
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    flipped = sorted(k for k, v in order.items() if not v["gate_still_agrees"])
    order_dependent = bool(flipped)

    repro = scan(text, anchors=A) == base
    gate_open = all(ctrl.values()) and repro

    q1, q2, q3 = len(multi), len(disagree), len(wrongfirst)
    # world C stays UNADMITTED: this instrument cannot establish "the same quantity, stated twice".
    c_admitted = False

    if not gate_open:
        verdict = ("UNVERIFIED — a control failed, so no count licenses a claim about the gate. "
                   "A kill that can fire on a broken instrument is not a commitment.")
    elif q1 == 0:
        verdict = ("world A (ANCHORED) survives — every anchor matches exactly once, so `re.search` "
                   "reading the first home is not a choice and this line is closed.")
    elif order_dependent:
        verdict = (f"world D (ORDER-BOUND) — {q1} of {len(A)} anchors are multi-home and "
                   f"{len(flipped)} of them bind to a DIFFERENT number once the second home is "
                   f"moved above the first: {flipped}. The gate's agreement with the artifact is "
                   f"a fact about document LAYOUT. World C (the document contradicting itself) is "
                   f"NOT admitted — reading the hits from the object shows three different "
                   f"quantities, and this instrument's unit was never the claim's unit.")
    else:
        verdict = (f"world B (UNATTRIBUTABLE) — {q1} of {len(A)} anchors are multi-home "
                   f"and {q2} capture more than one distinct value, but no prepending flips the "
                   f"gate, so the exposure is latent rather than live. C is NOT admitted.")

    art = {
        "round": "R1082",
        "question": "does the anchoring gate's first-match read hide a second, disagreeing home?",
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "gate_module": G.__file__,
        "gate_read_site": "definition_matches_the_record.read_claims -> re.search(pat, text)",
        "prior_art": {"R1049": "measured this defect class in the CURRENCY gate: 16 of 63 facts "
                               "multi-home. The repair never crossed to this gate.",
                      "R1044": "measured this gate's NARROWNESS; not its attribution.",
                      "R1066/R1067/R1068": "artifact-coupling and coverage; not attribution."},
        "pinned_revision": pin,
        "population": {"anchors": len(A),
                       "evaluable_against_an_artifact":
                           sum(1 for k in A if truth.get(k, (None,))[0] is not None)},
        "Q1_multi_home": q1,
        "Q2_disagreeing_homes": q2,
        "Q3_first_home_disagrees_with_artifact": q3,
        "green_by_order": latent,
        "wrong_first": wrongfirst,
        "multi_home_anchors": {k: {"n": v["n"], "distinct": v["distinct"]}
                               for k, v in sorted(multi.items())},
        "controls": ctrl,
        "reproducible": repro,
        "specification_curve": spec,
        "kill": {"gate_open": gate_open, "world_C_admitted": c_admitted,
                 "world_C_retraction": ("the pre-registered world C asked whether the document "
                                        "states ONE quantity twice with different values. This "
                                        "instrument's unit is a regex match capturing a number; "
                                        "that claim's unit is a statement of the same quantity. "
                                        "They are not equal, so C is UNVERIFIED, never ADMITTED "
                                        "and never OVERTURNED. Read from the object, the three "
                                        "hits are three different quantities."),
                 "world_D_order_bound": order_dependent, "anchors_that_flip": flipped},
        "order_dependence": order,
        "verdict": verdict,
    }
    art["repair"] = {
        "what": "three promiscuous anchors were tightened with unique surrounding context",
        "anchors": ["published_ref_pctile", "r432_floor", "r485_oracle"],
        "pinned_gate_fails_the_prepended_document":
            [k for k, v in order.items() if v["PINNED_gate_exit_code"] != 0],
        "repaired_gate_fails_the_prepended_document":
            [k for k, v in order.items() if v["REPAIRED_gate_exit_code"] != 0],
    }
    drop_pinned()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1082 — the anchoring gate reads only the first home\n")
    print(f"  gate  {pathlib.Path(G.__file__).name}:read_claims -> re.search(pat, text)")
    print(f"  measured against the anchor set PINNED at {pin} (the repair ships in this commit)")
    print(f"  {len(A)} anchors, "
          f"{art['population']['evaluable_against_an_artifact']} evaluable against an artifact")
    print("\n  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"    {'PASS' if repro else '⛔ FAIL'}  REPRODUCIBILITY the scan repeated identically")
    print(f"\n  THE COUNTS")
    print(f"    Q1 anchors matching more than once                     {q1:>5}")
    print(f"    Q2 anchors capturing more than one DISTINCT value      {q2:>5}")
    print(f"    Q3 of those, the FIRST home disagrees with the artifact{q3:>5}")
    print(f"       green by ORDER (first agrees, a later home does not){len(latent):>5}")
    if wrongfirst or latent:
        print(f"\n  THE ANCHORS THE GATE CANNOT SEE PAST")
        for k, r in sorted({**wrongfirst, **latent}.items())[:12]:
            print(f"    {k:<28} first={r['first']!s:<12} homes={r['distinct']} "
                  f"artifact={r['artifact']}")
    print(f"\n  SPECIFICATION CURVE — {len(spec)} cells, all reported")
    print(f"    {'region':<24}{'overlap':>9}{'norm':>7}{'multi':>7}{'disagree':>10}{'unmatched':>11}")
    for s in spec:
        print(f"    {s['region']:<24}{str(s['overlap']):>9}{str(s['normalise']):>7}"
              f"{s['multi_home']:>7}{s['disagreeing']:>10}{s['unmatched']:>11}")
    print(f"\n  ORDER DEPENDENCE — a gauge test: prepending text must leave a claim about the")
    print(f"     document's CONTENT invariant. Prepend the SECOND home and re-run the real gate.")
    print(f"    {'anchor':<26}{'binds to':>10}{'artifact':>11}   PINNED gate   REPAIRED gate")
    for k, v in sorted(order.items()):
        print(f"    {k:<26}{v['first_value_after_prepending']!s:>10}{v['artifact']!s:>11}   "
              f"rc={v['PINNED_gate_exit_code']} {'⛔ FAILS' if v['PINNED_gate_exit_code'] else 'ok'}"
              f"      rc={v['REPAIRED_gate_exit_code']} "
              f"{'⛔ FAILS' if v['REPAIRED_gate_exit_code'] else '⭐ immune'}")
    print(f"\n  KILL gate_open={gate_open}  world_C_admitted={c_admitted}  "
          f"world_D_order_bound={order_dependent}")
    print(f"\n  {'⛔' if not gate_open else '⭐' if order_dependent else '·'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
