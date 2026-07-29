"""r65 -- for how many core criteria can a satisfy-edit and a violate-edit be the same kind of object?

CLAIM CARD
----------
Claim      tau_c's symmetric design applies to CoVal-core criteria generally: for
           each one, R+ and R- can be built as the same kind of edit.
Estimand   the share of core criteria whose SURFACE is prohibitive ("do not X"),
           for which satisfying is the ABSENCE of something and violating is its
           PRESENCE -- so the two arms must insert categorically different kinds
           of content and cannot be matched objects.
Target
observed?  PARTLY, and the bound is one-sided. A prohibitive surface is
           mechanically detectable and is sufficient for asymmetry. An affirmative
           surface is NOT sufficient for symmetry -- "acknowledge regional
           differences" may still admit only a one-sided edit. So this measures a
           FLOOR on the asymmetric share and nothing about the ceiling.
Alternative
worlds     SMALL  prohibitive surfaces are rare, symmetry is the normal case, and
                  the design needs only a screen for the exceptions.
           LARGE  they are common, a substantial fraction of criteria cannot be
                  measured by the symmetric design at all, and the exclusion rate
                  becomes a headline number rather than a footnote.
Intervention
           none.
Null       the same regex on coval_FULL, which the compiler has NOT polarity-
           rewritten. If core and full carry the same prohibitive share, the
           rewrite changed weights without changing phrasing -- which is itself
           worth knowing, because r44 established the rewrite as core's single
           largest source of advantage.

WHY THIS EXISTS
---------------
`ADVERSARY_FORECAST.md` objection 3, P=0.75, and the one I predicted would cost
most: the symmetric design borrows r52's "same kind of object" logic, where both
arms genuinely were two token lists differing only in source. A satisfy-edit and a
violate-edit frequently are not. This bounds how often.

SCOPE
-----
A regex over surface forms. It cannot see a criterion that is asymmetric in
substance while affirmative in phrasing, and it will fire on constructions like
"not only... but also" where the negation is not the criterion's operative sense.
The matched sample is published in the artifact so a reader can judge the rate
rather than trust it, and the number is reported as a FLOOR.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

# The LOOSE pattern over-fires: it matches an incidental negation inside an
# affirmative criterion -- "Explain that stepping on cracks has NO effect",
# "Make clear that AI is NOT a substitute". Those are prescriptions, not
# prohibitions, and counting them inflates the asymmetric share. Caught by
# this package's own readme_row_carries_the_verdict check, which flagged the
# scope sentence admitting the over-fire as absent from the README row.
NEG = re.compile(r"\b(not|never|avoid|avoids|without|refrain|refrains|no|nor|omit|omits|"
                 r"exclude|excludes|abstain)\b", re.I)
# The STRICT pattern requires a DEONTIC negation -- an instruction not to do
# something -- which is what makes satisfaction an absence. This is the
# headline; the loose rate is reported beside it as the over-count.
STRICT = re.compile(r"\b(do not|does not|should not|must not|never|avoid|avoids|refrain|"
                    r"without|no\s+\w+ing)\b", re.I)


def positive_control() -> dict:
    """Known prohibitive and known affirmative strings must classify correctly."""
    proh = ["Do not use offensive language.", "Avoid speculation about motives.",
            "The response should never fabricate a citation."]
    affirm = ["Acknowledge regional differences in impact.",
              "Support claims with concrete economic data.",
              "Give arguments both for and against eating beef."]
    hit_p = [bool(NEG.search(s)) for s in proh]
    hit_a = [bool(NEG.search(s)) for s in affirm]
    return {"prohibitive_detected": hit_p, "affirmative_detected": hit_a,
            "all_pass": bool(all(hit_p) and not any(hit_a))}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r65_edit_symmetry_floor.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)

    pc = positive_control()
    print(f"positive control: {'PASS' if pc['all_pass'] else 'FAIL'}  {pc}")
    if not pc["all_pass"]:
        raise SystemExit("REFUSING: the surface classifier misreads known strings.")

    core, full = [], []
    for line in open(_ROOT / "data/conversation_rubrics.jsonl"):
        rec = json.loads(line)
        core += [c["criterion"] for c in rec.get("coval_core") or []]
        full += [c["criterion"] for c in rec.get("coval_full") or []]
    if not core:
        raise SystemExit("REFUSING: no core criteria. Nothing observed is not a pass.")

    loose_core = [c for c in core if NEG.search(c)]
    core_hits = [c for c in loose_core if STRICT.search(c)]
    full_hits = [c for c in full if NEG.search(c) and STRICT.search(c)]
    s_core, s_full = len(core_hits) / len(core), len(full_hits) / len(full)
    s_loose = len(loose_core) / len(core)
    false_pos = [c for c in loose_core if not STRICT.search(c)]

    world = "LARGE" if s_core >= 0.15 else "SMALL"
    verdict = (
        f"{world} FLOOR: {s_core:.4f} of the {len(core):,} CoVal-core criteria carry a DEONTIC "
        f"prohibition. A looser negation regex gives {s_loose:.4f}, and the {len(false_pos)} "
        f"criteria in the gap are affirmative ones with an incidental negation -- \"Explain that "
        f"stepping on cracks has NO effect\" -- so the strict figure is the defensible one and "
        f"the loose one is an over-count. Those criteria are prohibitive on "
        f"their SURFACE -- \"do not X\", \"avoid X\", \"without X\" -- so satisfying them is the "
        f"ABSENCE of something and violating them is its PRESENCE. For those, tau_c's two arms must "
        f"insert categorically different kinds of content (a refusal against the prohibited material) "
        f"and cannot be the same kind of object, which is what the symmetric design assumes. "
        f"THE NULL IS INFORMATIVE IN ITS OWN RIGHT: coval_full, which the compiler has NOT polarity-"
        f"rewritten, carries {s_full:.4f}, so core is {s_core/s_full:.2f}x as prohibitive as the raw "
        f"set it was compiled from -- the rewrite r44 identified as core's single largest source of "
        f"advantage (+0.0733) changes WEIGHTS to positive and leaves prohibitive PHRASING in place, "
        f"{'increasing' if s_core > s_full else 'reducing'} its share. Positive weight is not "
        f"affirmative wording. "
        f"THIS IS A FLOOR AND ONLY A FLOOR: a prohibitive surface is sufficient for asymmetry, an "
        f"affirmative surface is NOT sufficient for symmetry, so the true share of criteria the "
        f"symmetric design cannot measure is at least {s_core:.4f} and is not bounded above by "
        f"anything here. CONSEQUENCE: tau_c needs a per-criterion constructibility screen with the "
        f"exclusion rate reported as a headline, and {s_core:.1%} is the floor that rate must clear."
    )

    doc = {
        "n_core": len(core),
        "n_full": len(full),
        "core_prohibitive_share_strict_deontic": s_core,
        "core_negation_share_loose": s_loose,
        "n_loose_only_false_positives": len(false_pos),
        "sample_loose_only_false_positives": false_pos[:6],
        "full_prohibitive_share": s_full,
        "regex_loose": NEG.pattern,
        "regex_strict": STRICT.pattern,
        "sample_prohibitive_core": core_hits[:12],
        "sample_affirmative_core": [c for c in core if not NEG.search(c)][:8],
        "world": world,
        "positive_control": pc,
        "scope": ("A regex over surface forms. It cannot see a criterion asymmetric in substance but "
                  "affirmative in phrasing, and it fires on constructions like 'not only... but also' "
                  "where the negation is not the operative sense. The matched sample is published "
                  "here so a reader can judge the rate rather than trust it. The figure is a FLOOR on "
                  "the asymmetric share and says nothing about the ceiling."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  core criteria {len(core):,}   prohibitive surface {s_core:.4f}")
    print(f"  full criteria {len(full):,}   prohibitive surface {s_full:.4f}  (NOT polarity-rewritten)")
    print(f"\n  WORLD: {world} FLOOR")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
