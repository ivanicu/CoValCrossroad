"""Step 2 -- typed annotation of the source corpus by two independent model families.

One family alone would give a schema filled with one model's opinions and no way to see it. Two
families from different pretraining lineages give a per-field agreement rate, and the fields where
they disagree are marked UNRECOVERABLE rather than resolved. The agreement rate is therefore a
measurement of which parts of "force" are even readable off the text -- which is the first thing
the programme needs to know, because a field no instrument can recover cannot be preserved or lost.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())))

from covalx.chain.annotate import FIELDS, annotate, merge  # noqa: E402
from covalx.chain.corpus import build, stats               # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent / "results"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", nargs=2, default=["qwen25_7b", "phi35_mini"])
    ap.add_argument("--per-stratum", type=int, default=50)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    rules, rows = build(args.per_stratum)
    (OUT / "corpus.jsonl").write_text(
        "\n".join(json.dumps({**r.as_dict(), "raw_weight": row["raw_weight"],
                              "author_id": row["author_id"], "prompt": row["prompt"]})
                  for r, row in zip(rules, rows)))
    print(json.dumps(stats(), indent=1))
    print(f"corpus: {len(rules)} rules")

    out = []
    for fam in args.families:
        print(f"annotating with {fam} ...", flush=True)
        out.append(annotate(rules, rows, fam, OUT / f"annot_{fam}.jsonl"))

    merged, report = merge(out[0], out[1])
    (OUT / "annot_merged.jsonl").write_text("\n".join(json.dumps(m) for m in merged))
    (OUT / "annot_agreement.json").write_text(json.dumps(report, indent=1))

    print(f"\nagreement between {args.families[0]} and {args.families[1]}  (n={report['n']})")
    for f in FIELDS:
        a = report["agreement"][f.name]
        rec = sum(1 for m in merged if m[f.name] != "__unrecoverable__") / max(1, len(merged))
        print(f"  {f.name:16s} agree {a:6.1%}   recovered after margin gate {rec:6.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
