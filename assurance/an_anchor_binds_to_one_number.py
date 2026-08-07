#!/usr/bin/env python3
"""An anchor that matches two sentences carrying DIFFERENT numbers has not identified anything.

⭐ WHY THIS EXISTS (R1082). `definition_matches_the_record.read_claims` is `re.search(pat, text)` --
   the FIRST match, over the whole document, once per anchor. Three of its 343 anchors matched a
   second, unrelated sentence:

     published_ref_pctile   R348's POOL[0:k] percentile   AND  R812's POOL[0:4] percentile
     r432_floor             R432's headroom floor          AND  an unrelated token-Jaccard floor
     r485_oracle            `oracle_k4`'s SCORE            AND  its mean selection POSITION

   All three agreed with the artifact only because `re.search` reached the intended sentence FIRST.
   Prepending the other sentence made the gate exit 1 on each. **Its greenness was a fact about
   document layout.** R1049 measured the same defect class in the CURRENCY gate and the repair never
   crossed over; this is the invariant, named once, so the next anchor cannot reintroduce it.

⛔ THE FAILING CONDITION IS `distinct > 1`, NOT `n > 1`, AND THAT IS BOUNDED LENIENCY WITH A NAMED
   WORLD. Two homes carrying the SAME number cannot change the verdict whatever the order, so
   failing the commit on them would be over-strict. They are still unattributable in R1049's sense
   -- a PASS cannot be traced to a sentence -- so they are reported as a WARNING and counted. The
   world this leniency admits: *a document repeats a correct number in two places, one of which
   later goes stale while the other keeps the gate green.* That world is NOT covered here and needs
   the one-home-per-fact discipline of P16, which is prose, not a gate.
"""
from __future__ import annotations

import importlib
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))


def homes(anchors: dict, text: str) -> dict:
    out = {}
    for label, pat in anchors.items():
        hits = list(re.finditer(pat, text))
        vals = []
        for m in hits:
            try:
                vals.append(float(m.group(1).replace(",", "").replace("−", "-")))
            except (ValueError, IndexError):
                pass
        out[label] = {"n": len(hits), "distinct": sorted(set(vals))}
    return out


def controls(anchors: dict, text: str) -> dict:
    """the instrument is a search, and a search has no positive control unless you give it one."""
    # POSITIVE: an anchor deliberately made promiscuous MUST be caught.
    plant = dict(anchors)
    plant["_planted_promiscuous"] = r"\*\*(\d+\.\d+)\*\*"      # matches every bolded decimal
    p = homes(plant, text)["_planted_promiscuous"]
    pos = len(p["distinct"]) > 1
    # NEGATIVE: an anchor that cannot match anything must not be reported as ambiguous.
    neg = homes({"_absent": r"THIS_STRING_IS_NOT_IN_THE_DOCUMENT_(\d+)"}, text)["_absent"]
    neg_ok = neg["n"] == 0 and not neg["distinct"]
    # g=0: on an EMPTY document nothing may be flagged -- a flag there would be self-generated.
    g0 = homes(plant, "")
    g0_ok = all(v["n"] == 0 for v in g0.values())
    # SHAM: the same search with the capturing group removed from the value's position. It must
    # still match the same number of times -- so `distinct` responds to the VALUE, not to matching.
    sham = homes({"_sham": r"(?:\*\*)(\d+\.\d+)(?:\*\*)"}, text)["_sham"]
    sham_ok = sham["n"] == homes({"_sham2": r"\*\*(\d+\.\d+)\*\*"}, text)["_sham2"]["n"]
    return {"POSITIVE a deliberately promiscuous anchor is caught": pos,
            "NEGATIVE an anchor matching nothing is not flagged": neg_ok,
            "g=0 nothing is flagged in an empty document": g0_ok,
            "SHAM match count is independent of how the group is written": sham_ok}


def main() -> int:
    try:
        G = importlib.import_module("definition_matches_the_record")
    except Exception as e:                                    # noqa: BLE001 - reported, not hidden
        print(f"  UNRUNNABLE: the gate module will not import ({e}). Exit 2, never 0.")
        return 2
    doc = G.DOC
    if not doc.exists():
        print(f"  UNRUNNABLE: {doc} is absent. Exit 2, never 0.")
        return 2
    text = doc.read_text(encoding="utf-8")
    anchors = dict(G.ASSERTIONS)
    if not anchors:
        print("  UNRUNNABLE: no anchors declared — a gate that examined nothing has not passed. "
              "Exit 2, never 0.")
        return 2

    cc = controls(anchors, text)
    print("  CONTROLS on this gate, before its own verdict:")
    for k, v in cc.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    if not all(cc.values()):
        print("  the instrument does not separate the known cases. Exit 2, never 0.")
        return 2

    h = homes(anchors, text)
    ambiguous = {k: v for k, v in h.items() if len(v["distinct"]) > 1}
    repeated = {k: v for k, v in h.items() if v["n"] > 1 and len(v["distinct"]) <= 1}
    absent = [k for k, v in h.items() if v["n"] == 0]

    print(f"\n  {len(anchors)} anchors against {doc.name} ({len(text.splitlines())} lines)")
    print(f"    bind to exactly one number : {len(anchors) - len(ambiguous) - len(absent)}")
    print(f"    match nothing at all       : {len(absent)}"
          + (f"  {absent[:6]}" if absent else ""))
    print(f"    repeat the SAME number     : {len(repeated)}"
          + (f"  {sorted(repeated)[:6]}" if repeated else "")
          + "   ⚠ unattributable (R1049), not failed")
    print(f"    bind to DIFFERENT numbers  : {len(ambiguous)}")

    if ambiguous:
        print("\n  ⛔ RED — an anchor below matches two sentences carrying different numbers. The")
        print("     gate reads `re.search`, so its verdict is decided by which one appears FIRST,")
        print("     and inserting a paragraph above can silently rebind it to the other:")
        for k, v in sorted(ambiguous.items()):
            print(f"       {k:<28} {v['n']} homes, values {v['distinct']}")
        print("     Remedy: extend the pattern with context unique to the intended sentence.")
        print("     R1082 did exactly that for published_ref_pctile, r432_floor and r485_oracle.")
        return 1

    print("\n  GREEN — every anchor that matches at all binds to a single number.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
