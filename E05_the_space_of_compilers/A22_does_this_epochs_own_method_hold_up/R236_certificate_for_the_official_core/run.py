"""R236 -- issue the certificate for the OFFICIAL CoVal core, from measurements already made.

Arc E05.A09. The formulation says core = (Q, class, representative, certificate) and never said what
a certificate contains. covalx/certificate.py is the schema; this populates it for the released core
using only numbers this repository has measured, each carrying its round.

This is CLOSURE, not a frontier action, and it is labelled one: nothing here is a new measurement.
What it tests is whether the schema can express what was found -- including the parts that FAIL.
"""
from __future__ import annotations
import json, pathlib, sys

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
from covalx.certificate import Field, emit, render, MEASURED, NOT_MEASURED, FAILED

OUT = pathlib.Path(__file__).resolve().parent / "results"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    F = {
      "Q": Field(MEASURED, "the weak ordering over the four shown responses",
                 scope="declared HERE, by me, not by the release -- the dataset card names no Q",
                 note="R231 measured that the verdict INVERTS between this Q and 'predict human "
                      "pairwise preferences', on the same data and the same judge"),
      "identifiability": Field(
          MEASURED, "log2|H(Q)| = 3.70 bits (13 classes) vs H_have = 6.23 bits -- IDENTIFIABLE",
          scope="968 prompts, median n=15 criteria, m=4 responses. R224 derivation + R230",
          note="the CLASS is identifiable by construction; the MEMBER is not. R228 puts the "
               "largest identifiable member-core at k<=2, and the official core prints 4"),
      "class_agreement": Field(
          MEASURED, "0.3864 against a random-4 floor of 0.3836 [0.3657, 0.4019], ceiling 1.0",
          scope="968 prompts, judge Qwen3.5-2B, floor measured over 20 draws. R231",
          note="+0.0028 above the floor, INSIDE the floor's own draw spread -- on this Q the "
               "official core is indistinguishable from four criteria picked at random"),
      "representative": Field(
          FAILED, "4 criteria printed, at most 2 identifiable",
          scope="R228: recovery excess at k=4 is +0.0068 against a seed spread of 0.0084",
          note="FAILED is the right status and not an accusation: the artifact does not DISTINGUISH "
               "identified items from chosen ones, and a certificate that cannot tell them apart "
               "has failed that field. Naming the split would pass it without changing the core"),
      "instrument": Field(
          MEASURED, "Qwen3.5-2B-Base; class agreement spans 0.2893-0.4300 across five instruments",
          scope="base / phi / qwen3b / response-order-swapped / no-fewshot. R231",
          note="R231 also: changing the judge moves the induced class MORE than dropping 11 of 15 "
               "criteria does (0.2359 cross-judge vs 0.3836 cross-criterion)"),
      "transport": Field(
          NOT_MEASURED, requires="a second candidate set per prompt. R12's cached fresh generations "
                                 "make this RUNNABLE -- 250 prompts x 4 -- and R233 is running it; "
                                 "human rankings for generated responses remain unavailable",
          note="asserted STRUCTURALLY IMPOSSIBLE four times before the artifact was found in this "
               "repository's own results directory (RETRACTIONS.md entry 96)"),
      "provenance": Field(
          FAILED, "0.00 -- no core item carries a source",
          scope="all 986 rubrics; every coval_core item has exactly one field, `criterion`. R232",
          note="R223's entire lineage analysis is inference from text overlap because of this"),
    }

    REGISTER = [
      "no human rankings exist for any response outside the released four -- needs new elicitation",
      "no model trained on the standard is released, so downstream behaviour (C4) is unmeasurable",
      "`unacceptable` covers 26.66% of assessments, so no veto claim generalises to the corpus",
      "whether a k<=2 core is USEFUL is not measurable here -- identifiability is not utility",
      "three designs from one model family test FRAMING, never POPULATION",
    ]

    cert = emit("OpenAI CoVal `coval_core`", F, REGISTER)
    print(render(cert))

    print("\n" + "=" * 78)
    print("SCHEMA CONTROLS -- a certificate that cannot come back bad is a badge")
    print("=" * 78)
    ok = 0
    for name, fn in [
        ("MEASURED without a scope is refused",
         lambda: Field(MEASURED, "0.9", scope=None)),
        ("NOT_MEASURED without a requirement is refused",
         lambda: Field(NOT_MEASURED)),
        ("a two-valued status is refused",
         lambda: Field(True)),
        ("an empty register is refused",
         lambda: emit("x", {"Q": Field(MEASURED, "q", scope="s")}, [])),
    ]:
        try:
            fn(); print(" %-46s NOT REFUSED -- the schema is a badge" % name)
        except (ValueError, TypeError) as e:
            print(" %-46s refused: %s" % (name, str(e).split(".")[0][:60])); ok += 1
    print("\n %d/4 schema guards fire." % ok)
    print(" And this certificate itself has %d FAILED field(s) -- it can come back bad, and did."
          % cert["counts"][FAILED])

    (OUT / "official_core_certificate.json").write_text(json.dumps(cert, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
