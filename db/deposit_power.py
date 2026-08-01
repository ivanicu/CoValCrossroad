"""Power statements for the nulls, and the three that still lack one.

r204 measured the MDE for two nulls. r203's classifier, once it detected nulls STRUCTURALLY -- a
stated CI that spans zero, whatever the prose calls it -- found five, not two. The three extra
carry no resolution statement in any vocabulary: not MDE, not power, not this project's own
"effect over floor".

A null without a resolution is silence reported as evidence. That is a law this project has
applied to others repeatedly and is now recording against itself, by name, in the graph rather
than in a round nobody indexes.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "db"))
import derivation_chain as dc  # noqa: E402
from derivation_chain import edge, evid, node  # noqa: E402


def main() -> int:
    N = {}
    N["power-r188-compilation-null"] = node(
        "power-r188-compilation-null", "control",
        "POWER for the claim that compilation neither concentrates nor removes the "
        "rationalisation. Observed +0.0131, se 0.0130, z +1.01 over 373 (author, prompt) groups. "
        "MDE at 80% power and alpha .05 is +0.0365, which is 0.168 sd of the encoding "
        "distribution. The effect it had to rule out is r187's incoming +0.0478, so MDE/effect = "
        "0.76: the design could have detected three quarters of the rationalisation and found "
        "none. ADEQUATELY POWERED for the effect that matters; NOT powered for a subtle one, and "
        "the claim should be read with that bound rather than as a flat null.",
        d=8, status="settled")
    evid(N["power-r188-compilation-null"], "r204-power",
         "MDE derived from the round's own per-group contributions, not from a summary", 8)

    N["power-weight-deletion-null"] = node(
        "power-weight-deletion-null", "control",
        "POWER for the weight-deletion null. Its statement already carried its resolution in this "
        "project's own vocabulary -- 'effect over floor 0.97', meaning the observed effect sits AT "
        "the split-half resampling floor -- which is a stronger statement than an MDE because the "
        "floor is measured from the data rather than assumed from a normal. Derived from the "
        "published CI [-0.0068,+0.0099]: se 0.00426, MDE +0.0119 against an observed +0.0015. "
        "The null is resolved, and my first detector missed it by searching for the wrong word.",
        d=8, status="settled")
    evid(N["power-weight-deletion-null"], "r204-power",
         "MDE recomputed from the CI already in the node's own statement", 8)

    N["three-nulls-without-a-resolution"] = node(
        "three-nulls-without-a-resolution", "defect",
        "THREE STANDING NULLS IN THIS GRAPH CARRY NO RESOLUTION STATEMENT of any kind -- not MDE, "
        "not power, not 'effect over floor': the-compiled-rubric-does-not-inherit-the-aggregation-"
        "target, the-veto-is-lost-by-aggregation-not-by-compilation, and "
        "whether-disagreement-ITSELF-predicts-being-dropped-is-unsettled. A null without a "
        "resolution is silence reported as evidence, which is a rule this project has applied to "
        "others and had not applied to itself. Found by making r203's classifier detect nulls "
        "STRUCTURALLY -- a stated CI spanning zero -- rather than by their wording, which is what "
        "surfaced three beyond the two already known.",
        d=8, status="settled")
    evid(N["three-nulls-without-a-resolution"], "r204-null-register",
         "5 nulls detected structurally against 2 found by reading; 3 carry no resolution", 8)

    for src, dst, note in [
        ("power-r188-compilation-null", "compilation-passes-it-through",
         "the null is powered to 76% of the effect it rules out"),
        ("power-weight-deletion-null", "weight-deletion-null-under-the-reference-judge",
         "resolution already present as effect-over-floor 0.97"),
    ]:
        tgt = dc.q("SELECT id FROM node WHERE name=%s", (dst,))
        if tgt and src in N:
            edge(N[src], tgt[0][0], "tested_by", note=note)

    print(f"deposited {len(N)} nodes: 2 power controls and 1 defect")
    print("  the defect names three nulls that state no resolution -- silence reported as evidence,")
    print("  a rule this project applies to others and had not applied to itself.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
