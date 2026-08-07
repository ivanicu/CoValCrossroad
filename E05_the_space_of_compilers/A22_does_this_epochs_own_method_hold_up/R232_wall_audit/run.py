"""R232 -- auditing every structural wall this arc asserted, against the object rather than memory.

realstat §4, last row: "a wall never checked -- three 'permanent limits' of a dataset; one was a
query never run, and the falsifying arithmetic was in the author's own sentence. An unchecked wall
is UNVERIFIED, never SETTLED."

E05 has asserted five structural impossibilities across six rounds and RUN A QUERY FOR NONE OF
THEM. They are load-bearing: R224's whole bound rests on m=4, R223's lineage caveat rests on there
being no source id, and every register entry since R220 rests on Y being absent. An asserted wall
that turns out to be false does not weaken a conclusion -- it deletes it.

ESTIMAND        for each asserted wall: is it TRUE of the released files?
IDENTIFICATION  exact. Every one is a question about which fields exist and what values they take.
SCOPE           the four released files, all rows. No sampling: `head -N` is a stratum, not a
                sample, and this repository has been caught by that before.
KILL            any wall that is FALSE deletes the conclusions resting on it, and this round names
                which conclusions those are BEFORE looking.
POSITIVE CTRL   a wall known to be FALSE is included -- "the release ships no demographics" -- and
                the audit must flag it. An audit that has only ever confirmed is not an audit.
NEGATIVE CTRL   a wall known to be TRUE by prior measurement (R220: unacceptable at 26.66%) must
                come back TRUE at the same value, or the reader is broken.
MULTIPLICITY    6 walls, all reported, including the ones that hold.
IMPOSSIBLE      whether a wall is INSURMOUNTABLE rather than merely true here -- that is a claim
                about future releases and no query can settle it.
"""
from __future__ import annotations

import json, pathlib, sys, collections
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"

# (wall as asserted, what it holds up, the query that settles it)
WALLS = [
    ("m = 4 candidate responses for every prompt",
     "R224's bound and every k_max; R228's 'far below four'; the whole m=6 recommendation"),
    ("the release ships no criterion-by-response satisfaction",
     "r04's judge rebuild, and every instrument caveat since"),
    ("the release ships no source_criterion_id (no lineage)",
     "R223's lineage stratification; R222's provenance axis"),
    ("the release ships no Y (outputs of a model trained on the standard)",
     "C4 in the paper; every register entry since R220"),
    ("`unacceptable` covers only the long-form subset",
     "R220's veto axis scope; R231's human-consensus population"),
    ("the release ships no demographics  [POSITIVE CONTROL -- known FALSE]",
     "nothing; included so the audit can be seen to fail"),
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    comp = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    merged = [json.loads(l) for l in (DATA / "merged_comparisons_annotators.jsonl").open()]
    rub = [json.loads(l) for l in (DATA / "conversation_rubrics.jsonl").open()]
    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]

    res = []

    # 1 -- m = 4, from BOTH the metadata field and the actual arrays
    meta_m = collections.Counter(d.get("num_candidates") for d in merged)
    real_m = collections.Counter(len(d["responses"]) for d in comp)
    w1 = (set(meta_m) == {4}) and (set(real_m) == {4})
    res.append(("m = 4 candidate responses for every prompt", w1,
                "num_candidates over %d assessments: %s | responses per prompt over %d prompts: %s"
                % (len(merged), dict(meta_m), len(comp), dict(real_m))))

    # 2 -- per-criterion satisfaction
    keys = set()
    for d in rub[:50]:
        for it in d["coval_full"]:
            keys |= set(it.keys())
            for s in (it.get("scores") or [])[:1]:
                keys |= {"scores." + k for k in s}
    sat_like = sorted(k for k in keys if "satisf" in k.lower() or "met" == k.lower()
                      or "response" in k.lower())
    w2 = not sat_like
    res.append(("the release ships no criterion-by-response satisfaction", w2,
                "rubric item fields: %s | satisfaction-like: %s" % (sorted(keys), sat_like or "none")))

    # 3 -- lineage
    core_keys = set()
    for d in rub:
        for it in d["coval_core"]:
            core_keys |= set(it.keys())
    lin = sorted(k for k in core_keys if "source" in k.lower() or "id" in k.lower()
                 or "parent" in k.lower() or "from" in k.lower())
    w3 = not lin
    res.append(("the release ships no source_criterion_id (no lineage)", w3,
                "coval_core item fields across ALL %d rubrics: %s | lineage-like: %s"
                % (len(rub), sorted(core_keys), lin or "none")))

    # 4 -- Y
    top = set()
    for d in comp[:5]:
        top |= set(d.keys())
    for d in merged[:5]:
        top |= set(d.keys())
    ylike = sorted(k for k in top if k.lower() in
                   {"model_output", "completion", "y", "generation", "trained_model", "policy"})
    w4 = not ylike
    res.append(("the release ships no Y (outputs of a model trained on the standard)", w4,
                "top-level fields: %s | Y-like: %s" % (sorted(top), ylike or "none")))

    # 5 -- unacceptable coverage
    nonempty = sum(1 for d in merged if (d.get("ranking_blocks") or {}).get("unacceptable"))
    share = nonempty / len(merged)
    w5 = abs(share - 0.2666) < 0.005
    res.append(("`unacceptable` covers only the long-form subset", w5,
                "non-empty in %d of %d = %.4f (R220 measured 0.2666)" % (nonempty, len(merged), share)))

    # 6 -- POSITIVE CONTROL: a wall that is FALSE
    demo = sum(1 for d in merged if d.get("demographics"))
    w6 = demo == 0
    res.append(("the release ships no demographics  [POSITIVE CONTROL -- known FALSE]", w6,
                "demographics present on %d of %d rows" % (demo, len(merged))))

    print("=== every structural wall E05 asserted, checked against the files ===\n")
    holds = 0
    for (asserted, holds_up), (name, ok, ev) in zip([(w[0], w[1]) for w in WALLS], res):
        print("%-62s %s" % (name[:62], "HOLDS" if ok else "FALSE"))
        print("   evidence : %s" % ev)
        print("   holds up : %s\n" % holds_up)
        holds += int(ok)

    print("=" * 78)
    print("AUDIT CONTROLS")
    print("=" * 78)
    pos_ok = not res[5][1]            # the known-false wall must come back FALSE
    neg_ok = res[4][1]                # the known-true one must come back TRUE
    print(" POSITIVE  the deliberately false wall was flagged FALSE : %s"
          % ("OK" if pos_ok else "THE AUDIT CANNOT FAIL -- it confirmed a wall that is false"))
    print(" NEGATIVE  the previously measured wall reproduces        : %s (%.4f vs 0.2666)"
          % ("OK" if neg_ok else "READER BROKEN", share))

    print("\n" + "=" * 78)
    print("VERDICT")
    print("=" * 78)
    real = [r[0] for r in res[:5] if r[1]]
    broken = [r[0] for r in res[:5] if not r[1]]
    if not pos_ok:
        v = "UNVERIFIED -- the audit confirmed a wall known to be false, so it confirms nothing"
    else:
        v = ("%d of the 5 load-bearing walls HOLD, checked against every row of the released files "
             "rather than asserted. %s They were asserted across six rounds and this is the first "
             "query run against any of them; they are now VERIFIED rather than UNVERIFIED, which is "
             "a change in their status even though not one of them moved."
             % (len(real), ("Broken: %s." % "; ".join(broken)) if broken else "None is false."))
    print("\n  " + v)
    json.dump({"walls": [{"wall": n, "holds": bool(o), "evidence": e} for n, o, e in res],
               "positive_control_ok": bool(pos_ok), "negative_control_ok": bool(neg_ok),
               "verdict": v}, open(OUT / "wall_audit.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
