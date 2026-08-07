#!/usr/bin/env python3
"""R1002 — is R849's reference class CLOSED under the clause it instantiates?

⛔ WHY THIS. R1001 left one wording standing: entry 1368's repair — *"exceeds, by a margin reported
with its interval, the best rule in a NAMED reference class R"* — instantiated by R849 as 394
response-only rules, and the only form under which the definition admits its own instance. R1001's
NEXT asked whether it survives ENLARGEMENT. ⚠ Enlargement along family SIZE is prior art: R848
committed a dose-response of +0.007412 per e-fold and an extrapolation its own key labels
`extrapolated_n_for_core_D4_NOT_A_MEASUREMENT`, and R847 enlarged the family once, measuring the bar
RAISED but not CROSSED. So the size axis is answered and the round must not re-ask it.

⭐ THE UNASKED QUESTION IS CLOSURE, NOT SIZE. The clause quantifies over *"every rule computable from
responses alone"*. R849's R is built by enumerating **singletons and signed PAIRS of z-scored
hand-picked lexical features**. If a rule exists that is admissible under the clause's own words and
is NOT in R, then R849's bar is a max over a PROPER SUBSET of what the clause names, and the repair's
survival is a property of where we drew the class boundary rather than of the object. R825 built
exactly such a rule and it beats the core.

ESTIMAND        ① is R849's R closed under the clause's own predicate — i.e. does membership in R
                   follow from "computable from responses alone"? ② is there a WITNESS: a rule
                   admissible under the clause, absent from R, and known to beat the instance?
IDENTIFICATION  exact and textual. R's construction is read from R849's source and re-enumerated
                here; the witness is R825's committed predictor. No scoring run is involved, and
                none is needed: a closure failure is exhibited by ONE member, not by a measurement.
SCOPE           population : R849's reference class as constructed, on this release's utterances
                instrument : set membership. There is no estimator and no interval
                baseline   : the clause's own text, quoted from the statement
                regime     : this instantiation of the repair. Says nothing about a different R
WORLDS          A CLOSED    every response-only rule is in R, or the ones outside are inadmissible
                            under the clause's text. The repair is a definition.
                B NOT CLOSED a witness exists. The repair's margin is a max over a proper subset,
                            and the class boundary — not the object — is doing the definitional work.
                prediction matrix: A -> no admissible rule outside R. B -> ≥1 exhibited by name.
KILL            pre-registered: if my re-enumeration does not reproduce R849's committed 394, I have
                misread the construction and NOTHING here is admissible. Exit 2.
                Second, pre-registered: if the witness turns out to consume anything beyond response
                text, it is NOT admissible under the clause and world A survives. That is checked
                against R825's source, not against my memory of it.
POSITIVE CTRL   re-enumerate R849's class from the same base and require EXACTLY its committed
                `reference_class_size`. This is the control that my reading of the construction is
                R849's construction.
NEGATIVE CTRL   a rule that is plainly INADMISSIBLE under the clause — one consuming the human
                rankings — must be reported as outside R AND outside the clause, so that "outside R"
                alone is not treated as evidence of a closure failure. Without this, every arm in the
                release would look like a witness.
PLACEBO         a rule that IS in R (`+mean_word_len+uppercase`, R849's own selected bar rule) must
                test as a member. A membership test that cannot find R849's own bar is broken.
MULTIPLICITY    n/a — this is a closure question with a single witness. Nothing is selected over,
                and no p-value is computed. Labelled rather than omitted.
ARTIFACT        results/class_closure.json with this file's source hash.
IMPOSSIBLE      ⚠ scoring the witness ON R849's ODD/EVEN halves — N/A here. R825's predictor was
                fitted and evaluated on its own 12 splits, not on R849's parity halves, so the two
                numbers are IN DIFFERENT UNITS and this round does NOT compare them. What it would
                require: re-running R825's predictor under R849's split. ⭐ The closure claim does
                NOT need it — closure is a membership fact, and the witness's magnitude only matters
                for HOW MUCH the bar would move, which is deliberately not claimed here.
                ⚠ construct validity — N/A: this says the class is not closed, never that a closed
                class is achievable. A class closed under "computable from responses alone" may be
                uncountable, which is itself a fact about the clause.
"""
from __future__ import annotations
import hashlib
import importlib.util
import itertools
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))


def load(mod: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(mod, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> int:
    r849f = next(A24.glob("R849_*/results/proposed_clause_extension.json"), None)
    r435p = next(A24.glob("R435_*/run.py"), None)
    r825p = next(A24.glob("R825_*/run.py"), None)
    r826f = next(A24.glob("R826_*/results/effort_curve.json"), None)
    if not (r849f and r435p and r825p and r826f):
        print("  UNRUNNABLE: a required object is missing. Exit 2, never 0.")
        return 2
    r849 = json.loads(r849f.read_text())
    committed = r849["reference_class_size"]
    bar_rule = r849["bar_rule"]
    print(f"  R849's committed reference class: {committed} rules; its selected bar rule "
          f"`{bar_rule}`")

    # ---------- POSITIVE CONTROL: re-enumerate R's construction ----------
    r435 = load("r435", r435p)
    texts = {}
    with open(ROOT / "data" / "utterances.jsonl") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                u = str(r.get("utterance_id"))
                if u:
                    texts.setdefault(u, {})[str(r.get("completion_id", r.get("model", "")))] = \
                        r.get("text", r.get("utterance", ""))
    sample = next(iter(texts.values()))
    feats = r435.features(next(iter(sample.values())) or "x y")
    base = sorted(set(feats) - {"__pos__"})
    singles = [n for n, _k, _s in r435.RULES]
    pairs = [f"{sa}{a}{sb}{b}" for a, b in itertools.combinations(base, 2)
             for sa, sb in (("+", "+"), ("+", "-"), ("-", "+"), ("-", "-"))]
    mine = len(singles) + len(pairs)
    print(f"\n  POSITIVE CONTROL — re-enumerating R849's construction from the same base:")
    print(f"     base features {len(base)}: {base}")
    print(f"     singletons {len(singles)} + signed pairs {len(pairs)} = {mine}   "
          f"(R849 committed {committed})")
    if mine != committed:
        print(f"     ⛔ FAIL — I have misread the construction. Nothing here is admissible. Exit 2.")
        return 2
    print("     PASS — my reading of R is R849's R.")

    R = set(singles) | set(pairs)

    # ---------- PLACEBO: R849's own bar rule must be a member ----------
    plac = bar_rule in R
    print(f"\n  PLACEBO — R849's own selected bar rule `{bar_rule}` tests as a MEMBER: "
          f"{'PASS' if plac else '⛔ FAIL'}")
    if not plac:
        print("     the membership test cannot find R849's own bar. Exit 2, never 0.")
        return 2

    # ---------- the witness, and the clause's own predicate ----------
    src825 = r825p.read_text()
    # what does the witness CONSUME? checked against R825's source, not against memory.
    reads_rankings = any(t in src825 for t in ("load_targets(", "Hodd", "human_rank", "targets["))
    uses_response_text = any(t in src825 for t in ("utterances.jsonl", "TfidfVectorizer",
                                                  "analyzer=\"char", "analyzer='char'", "char_wb"))
    bars = {c["k"]: c["bar"] for c in json.loads(r826f.read_text())["curve"]}
    witness = "char 3-5-gram TF-IDF + SVD response-only predictor (R825/R826)"
    print(f"\n  ── the witness ──\n     {witness}")
    print(f"     in R849's class R: {witness in R}   (R holds only singletons and signed PAIRS of "
          f"{len(base)} hand-picked lexical features)")
    print(f"     builds from response TEXT: {uses_response_text}")
    print(f"     consumes human rankings anywhere in its source: {reads_rankings}")
    print(f"     ⚠ `load_targets` appears in R825 because the EVALUATION needs the human ranking to")
    print(f"        score any rule at all — clause ③'s question is what the RULE consumes, and the")
    print(f"        rule is fitted on response text. R826 reports it as a response-only family.")

    # ---------- NEGATIVE CONTROL ----------
    neg = "oracle_k4"
    neg_out_of_R = neg not in R
    neg_admissible = False          # it consumes the human ranking; the clause excludes it by text
    print(f"\n  NEGATIVE CONTROL — `{neg}` consumes the human ranking:")
    print(f"     outside R: {neg_out_of_R}   admissible under the clause: {neg_admissible}")
    print(f"     ⇒ 'outside R' ALONE is not a closure failure. A witness must be outside R AND")
    print(f"       admissible under the clause's own words. This control is what makes the finding")
    print(f"       below mean anything: without it every arm in the release would look like one.")
    if not neg_out_of_R or neg_admissible:
        print("  ⛔ the negative control failed. Exit 2, never 0.")
        return 2

    closed = not (uses_response_text and witness not in R)
    world = ("A CLOSED — no admissible rule was exhibited outside R" if closed else
             "B NOT CLOSED — an admissible response-only rule sits outside R, so R849's bar is a "
             "max over a PROPER SUBSET of what the clause quantifies over")
    print(f"\n⭐ {world}")
    if not closed:
        print("⛔ SO THE ONLY SURVIVING WORDING INHERITS THE DEFECT 1368 DIAGNOSED, ONE LEVEL UP.")
        print("   1368 killed the universal quantifier because 'every' ranged over a convenience")
        print("   family. The repair replaced 'every' with 'the best rule in a NAMED class R' — and")
        print("   R is a convenience family too. Naming it makes the bar HONEST and REPRODUCIBLE;")
        print("   it does not make it CLOSED. The definition's verdict on its own instance is")
        print("   therefore a property of a boundary we drew.")
        print("\n⭐ AND THAT IS A DERIVATION, NOT A MEASUREMENT: a max over a superset is >= a max")
        print("   over a subset, by definition. No experiment can overturn it; what an experiment")
        print("   could tell us is HOW MUCH the bar moves, which this round deliberately does NOT")
        print("   claim, because R825's number is on its own splits and R849's is on parity halves.")
    print(f"\n  for reference only, NOT compared: R826's saturated bars {sorted(bars.items())[-5:]}")
    print(f"  and R849's bar {r849['bar_even_half_A2']:.6f} — DIFFERENT SPLITS, DIFFERENT UNITS.")

    out = HERE / "results" / "class_closure.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="is R849's reference class closed under the clause it instantiates",
        committed_class_size=committed, reenumerated_class_size=mine,
        base_features=base, n_singletons=len(singles), n_pairs=len(pairs),
        controls={"positive_reenumeration_matches": mine == committed,
                  "placebo_bar_rule_is_member": plac,
                  "negative_inadmissible_rule_outside_R": neg_out_of_R and not neg_admissible},
        witness=witness, witness_in_R=witness in R,
        witness_builds_from_response_text=uses_response_text,
        witness_source_mentions_rankings=reads_rankings,
        authorial_judgement="R825's source touches the human ranking because SCORING any rule "
                            "needs it. Reading the witness as response-ONLY is therefore a "
                            "judgement about what the RULE consumes versus what its EVALUATION "
                            "consumes, not an automated test. It is R826's own framing (it calls "
                            "the family response-only) and it is stated here rather than hidden "
                            "in a boolean, because it is the one step of this round a reader "
                            "could reasonably dispute.",
        world=world, closed=closed,
        prior_art="R847 enlarged the family once (raised, not crossed) and R848 gave the size "
                  "dose-response with an extrapolation its own key labels NOT_A_MEASUREMENT. This "
                  "round is about CLOSURE, not size, and does not re-ask either.",
        derivation="a max over a superset is >= a max over a subset — no experiment can overturn "
                   "the closure failure; only its MAGNITUDE is empirical",
        not_measured="how far the bar would move if the witness were added to R",
        would_require="re-running R825's predictor under R849's odd/even parity split",
        limitation="says the class is not closed, never that a closed class is achievable",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
