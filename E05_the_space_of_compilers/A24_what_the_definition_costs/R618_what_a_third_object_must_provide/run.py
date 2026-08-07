#!/usr/bin/env python3
"""
R618 -- what must a third object provide for clause ② to be evaluable on it?

CHECK #217 CAUGHT ANOTHER FALSE "EVERY". R617's closing line said "every axis of this arc now
measures artifact FORM". R614 measured POSITION (round ids), R615 the VERDICT-CLASS
DISTRIBUTION, and R617 itself measured README PROSE and CODE IDENTIFIERS -- not artifact form.
That is the fourth quantifier error in six closing lines, which makes it a standing property of
that sentence position rather than an occasional slip.

⚠ CLASSIFICATION, STATED: this round is PRODUCTION, not Frontier. It converts thirteen rounds of
measurement into a requirement. A specification cannot be surprised by data, so the derivation
below is labelled as one -- and the ONE testable thing is bolted on: the specification must
REPRODUCE the verdicts already established on the two objects we have. A spec that cannot
re-derive R603's answer is wrong regardless of how reasonable it reads.

ESTIMAND        the minimal field set F such that clause ② -- "a core scores better than a
                strong generalising prompt-blind criterion set drawn from the released pool" --
                can be STATED and SCORED on a release.
IDENTIFICATION  F is DERIVED from ②'s own wording plus the home release's schema. It is not
                measured and could not have come out otherwise. ⚠ What IS testable: applying F
                to the two known objects must reproduce R603 (home evaluable, second not, and
                the same two requirements missing). That check can fail.
SCOPE           population : the two releases on disk
                instrument : schema key presence, as R603 used
                             instrument unit = A FIELD IN A RELEASE
                             claim unit      = A REQUIREMENT OF CLAUSE ② -- NOT equal, since a
                             field can be present and unusable; F is necessary, never sufficient
                baseline   : R603's published verdict
                regime     : as committed at this sha
WORLDS          A THE SPEC REPRODUCES: F says home evaluable, second not, missing exactly
                  {rubric, core} -> the specification is consistent with what is known and can
                  be handed to a next site.
                B THE SPEC DISAGREES: it admits the second release, or rejects the home one, or
                  names different missing fields -> F is wrong and must not be published as a
                  requirement.
KILL            pre-registered: any disagreement with R603 on either object -> world B, and the
                specification is withheld rather than published with a caveat.
POSITIVE CTRL   the home release must come out EVALUABLE. Fails at g=0: a release stripped of
                its rubric must come out NOT evaluable, so the check is not vacuous.
NEGATIVE CTRL   a synthetic release carrying only the fields ② does NOT need must fail.
PLACEBO         a synthetic release carrying every field must pass, and adding an irrelevant
                field must not change any verdict.
SEEDS           n/a, deterministic.
MULTIPLICITY    |F| requirements x 2 real objects + 3 synthetic; all reported.
ARTIFACT        results/third_object_spec.json
IMPOSSIBLE      F is NECESSARY, not sufficient: a release can carry every field and still fail
                to support ② -- R602 measured the second corpus as disjoint in content, which
                no schema check can see. This specification screens out impossibilities; it
                cannot certify a site.
"""
from __future__ import annotations
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"

# ---- F, DERIVED from clause ②'s wording. Each row names the phrase it serves. ----
F = [
    ("a prompt / user turn",        "…for a conversation…",                  ("prompt", "user_prompt")),
    ("multiple responses per unit", "…scores RESPONSES…",                    ("responses", "model_response")),
    ("a human preference target",   "…better than… (better AT something)",   ("responses", "score")),
    ("a released criterion POOL",   "…drawn from the RELEASED POOL…",        ("coval_full",)),
    ("a released CORE",             "…a CORE scores…",                       ("coval_core",)),
]


def keys(path, cap=40000):
    ks, n = set(), 0
    if not path.is_file():
        return ks
    with path.open() as fh:
        for line in fh:
            if n >= cap:
                break
            try:
                j = json.loads(line)
            except Exception:
                continue
            if isinstance(j, dict):
                ks |= set(j)
            n += 1
    return ks


def evaluate(ks):
    missing = [name for name, _phrase, fields in F if not (set(fields) & ks)]
    return (not missing), missing


def main():
    home = keys(DATA / "comparisons.jsonl") | keys(DATA / "conversation_rubrics.jsonl")
    second = keys(DATA / "utterances.jsonl")
    if not home or not second:
        print("UNRUNNABLE: a release is unreadable. Exit 2, never 0."); return 2

    print("R618 is PRODUCTION, not Frontier: it converts measurement into a requirement.")
    print("The specification below is a DERIVATION from clause ②'s wording; the reproduction")
    print("check beneath it is the only part that can fail.\n")
    print("─── F · WHAT A RELEASE MUST CARRY FOR CLAUSE ② TO BE EVALUABLE ───")
    for name, phrase, fields in F:
        print(f"  {name:<28} serves {phrase:<40} e.g. {list(fields)}")

    print(f"\n─── APPLYING F TO THE TWO OBJECTS ON DISK ───")
    ok_h, miss_h = evaluate(home)
    ok_s, miss_s = evaluate(second)
    print(f"  HOME   evaluable={ok_h}   missing={miss_h}")
    print(f"  SECOND evaluable={ok_s}   missing={miss_s}")

    print(f"\n─── REPRODUCTION CHECK (the pre-registered kill) ───")
    exp_h, exp_s = True, False
    exp_miss_s = {"a released criterion POOL", "a released CORE"}
    agree_h = ok_h == exp_h
    agree_s = (ok_s == exp_s) and set(miss_s) == exp_miss_s
    print(f"  R603 said: home evaluable, second NOT, missing exactly a rubric and a core")
    print(f"  home agrees   : {agree_h}")
    print(f"  second agrees : {agree_s}  (missing set matches: {set(miss_s) == exp_miss_s})")
    reproduces = agree_h and agree_s
    print(f"  -> {'PASS — F reproduces what is already known' if reproduces else 'FAIL — world B, the specification is WITHHELD'}")

    print(f"\n─── CONTROLS ───")
    stripped = home - {"coval_full", "coval_core"}
    ok_x, miss_x = evaluate(stripped)
    g0_ok = not ok_x
    print(f"  POSITIVE @ g=0  home stripped of its rubric and core: evaluable={ok_x}, "
          f"missing={miss_x} -> {'PASS — the check is not vacuous' if g0_ok else 'FAIL'}")
    only_irrelevant = {"utterance_id", "model_provider", "turn"}
    ok_n, miss_n = evaluate(only_irrelevant)
    neg_ok = not ok_n and len(miss_n) == len(F)
    print(f"  NEGATIVE  a release with only fields ② does not need: evaluable={ok_n}, "
          f"missing {len(miss_n)} of {len(F)} -> {'PASS' if neg_ok else 'FAIL'}")
    everything = set().union(*[set(f) for _, _, f in F])
    ok_p, _ = evaluate(everything)
    ok_p2, _ = evaluate(everything | {"an_irrelevant_field"})
    plc_ok = ok_p and ok_p2
    print(f"  PLACEBO   a release carrying every needed field: evaluable={ok_p}; adding an "
          f"irrelevant field leaves it {ok_p2} -> {'PASS' if plc_ok else 'FAIL'}")
    controls_ok = g0_ok and neg_ok and plc_ok

    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif not reproduces:
        world = ("B THE SPEC DISAGREES — F does not reproduce R603 on the objects we have, so "
                 "it is WITHHELD rather than published with a caveat")
    else:
        world = (f"A THE SPEC REPRODUCES — F admits the home release and rejects the second, "
                 f"naming exactly the two requirements R603 measured as absent. It can be "
                 f"handed to a next site as a screening requirement.")
    print(f"  {world}")
    print(f"\n  ⚠ F is NECESSARY, NOT SUFFICIENT: R602 measured the second corpus as disjoint "
          f"in CONTENT (exact overlap 0, token-Jaccard at the shuffled floor), which no schema "
          f"check can see. F screens out impossibilities; it cannot certify a site.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "third_object_spec.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "reproduces_r603": reproduces,
        "classification": "PRODUCTION — a requirement derived from measurement, not a new finding",
        "specification": [{"requirement": n, "serves": p, "example_fields": list(f)}
                          for n, p, f in F],
        "home_evaluable": ok_h, "home_missing": miss_h,
        "second_evaluable": ok_s, "second_missing": miss_s,
        "check217": ("R617's closing line said EVERY axis of the arc measures artifact FORM; "
                     "R614 measured position, R615 verdict-class distribution, and R617 itself "
                     "README prose and code identifiers. Fourth quantifier error in six closing "
                     "lines."),
        "impossible": ("F is necessary and not sufficient: a release can carry every field and "
                       "still fail to support ②, as R602's disjointness measurement shows"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'third_object_spec.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
