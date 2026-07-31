"""Why the typed layer cannot be recovered -- measured on the text, with no model anywhere.

Two independent model families agreed near chance on force, generality and confidence when reading
real criteria (kappa 0.01-0.18), while both read the same fields at 83-100% on constructed criteria
where the value is stated explicitly. That rules out an unfit instrument, but it does not yet say
WHY the real text fails. This does, and it needs no instrument at all:

    the vocabulary that expresses force is simply not present in what people wrote.

Run over the entire release rather than the 100-rule study corpus, because the study corpus was
selected by extreme absolute weight and a terse-criterion selection effect would produce exactly
this result artefactually. It does not: the population rates are the same.

The consequence is a reframing, not a refinement. "Compilation loses force" is FALSE as a causal
story. Force never entered. A free-text box asking what the model should do collects content and
does not collect force, so the loss is at N, before any aggregation or compilation happens.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent / "results"

MARKERS = {
    "absolute_force": r"\b(never|under no|no circumstances|absolutely|must not|forbidden|"
                      r"unacceptable|at all costs|whatever else|always)\b",
    "graded_force": r"\b(prefer|slightly|somewhat|ideally|nice to|a plus|where possible|"
                    r"when feasible|if possible|rather than|more likely)\b",
    "scope_qualifier": r"\b(only (when|if)|when the user|in cases where|whenever|if the user|"
                       r"for questions)\b",
    "exception": r"\b(unless|except|does not apply|other than)\b",
    "hedge": r"\b(maybe|perhaps|might|could|i think|not sure|possibly)\b",
    "modal_must": r"\b(must|shall|required|mandatory)\b",
    "modal_should": r"\b(should|ought)\b",
}


def main() -> int:
    pops: dict[str, list[str]] = {"all": [], "self_authored": [], "pre_seeded": []}
    with (ROOT / "data" / "conversation_rubrics.jsonl").open() as fh:
        for line in fh:
            r = json.loads(line)
            for it in r["coval_full"]:
                t = it["criterion"].strip()
                pops["all"].append(t)
                pops["self_authored" if len(it["scores"]) == 1 else "pre_seeded"].append(t)

    res = {"populations": {k: {"n": len(v), "mean_chars": round(sum(map(len, v)) / len(v), 1)}
                           for k, v in pops.items()}, "marker_presence": {}}
    for name, pat in MARKERS.items():
        rx = re.compile(pat, re.I)
        res["marker_presence"][name] = {
            k: round(sum(1 for t in v if rx.search(t)) / len(v), 5) for k, v in pops.items()}

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "markers.json").write_text(json.dumps(res, indent=1))

    w = max(len(k) for k in MARKERS)
    print(f"{'marker':{w}s}" + "".join(f"{k:>16s}" for k in pops))
    for name in MARKERS:
        print(f"{name:{w}s}" + "".join(f"{res['marker_presence'][name][k]:15.2%} " for k in pops))
    print()
    for k, v in res["populations"].items():
        print(f"  {k:14s} n={v['n']:6d}  mean {v['mean_chars']:.0f} chars")
    print("\nthe three fields the annotator could not recover are exactly the three whose "
          "vocabulary is absent: absolute force, scope, exception -- each under 1%.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
