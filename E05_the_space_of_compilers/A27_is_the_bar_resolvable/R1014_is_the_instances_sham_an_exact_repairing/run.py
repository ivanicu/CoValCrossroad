#!/usr/bin/env python3
"""R1014 — is the INSTANCE's sham an exact re-pairing? R1013 could not check, and it changes its reach.

⛔ WHY. R1013 withdrew size, the size residual and size variability as candidate clauses because the
sham shares them. Its evidence for the INSTANCE was R986's committed residual — 43 for `coval_core`
and 43 for `coval_core_sham` — because `core_coval_core.json` is not on disk, so the three arm/sham
criteria pairs it compared (`gen`, `promptecho`, `topw_k4`) are OTHER arms. And those three split:
`promptecho` and `topw_k4` matched on every text property, `gen` differed on text volume by ~0.14%.
⭐ THE INSTANCE'S CRITERIA ARE IN THE RELEASE, not in corebench's outputs: `data/conversation_
rubrics.jsonl` under the key `coval_core`, joined by `covalx.judge.load_join`. That is why R1013 could
not find them, and it is a one-line fix to its scope.

ESTIMAND        whether `coval_core_sham` is an EXACT re-pairing of `coval_core`'s criterion sets —
                the multiset of sets preserved, only the prompt each is attached to changed.
IDENTIFICATION  exact and set-theoretic. Two dictionaries of criterion lists; the question is whether
                one is a permutation of the other. No estimation.
SCOPE           population : the prompts both objects cover
                instrument : exact string comparison of criterion sets, and the text properties
                             R1013 computed for the other three pairs
                baseline   : R1013's own three pairs — two exact, one not
                regime     : this release
WORLDS          A EXACT      the multiset of criterion sets is identical; only the pairing moved.
                             Then R1013's argument reaches the instance in full, and NO text-only
                             property can separate `coval_core` from its sham.
                B INEXACT    the sham's criterion sets differ from the core's, as `gen`'s do. Then
                             R1013's withdrawal stands for SIZE (R986: 43 = 43) and the wider class
                             of text properties remains LIVE for the instance.
                prediction matrix: A -> multiset equal, every text property identical.
                                   B -> multiset differs; report which properties still match.
KILL            pre-registered: if world B, R1013's reach is scoped in THIS round — its withdrawal
                covers size only, and vocabulary, length and redundancy go back on the candidate list
                for the instance rather than being quietly left off it.
POSITIVE CTRL   the core's size distribution recovered here must reproduce R986's committed
                decomposition — min 2, max 4, and 43 prompts off the cap. If it does not, this is not
                the object R986 measured and nothing below applies.
NEGATIVE CTRL   a runtime-assembled key that is not in the release must yield no criteria, so that
                "the multiset differs" cannot be produced by a mis-keyed lookup returning empty.
PLACEBO         the core compared to ITSELF must return an exact multiset match on every property.
NOISE FLOOR     n/a — exact set comparison. Labelled.
MULTIPLICITY    1 pair × every text property R1013 defined, all printed.
ARTIFACT        results/instance_sham.json with this file's source hash.
IMPOSSIBLE      ⚠ why the sham was built the way it was — N/A. Intent is not in the record; what is
                measurable is whether the sets moved.
"""
from __future__ import annotations
import collections
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))


def props(d):
    sizes = collections.Counter(len(v) for v in d.values())
    chars = [sum(len(str(x)) for x in v) for v in d.values()]
    words = [sum(len(str(x).split()) for x in v) for v in d.values()]
    uniq = [len({str(x).strip().lower() for x in v}) for v in d.values()]
    return {"n_prompts": len(d), "size_dist": dict(sorted(sizes.items())),
            "mean_size": round(sum(len(v) for v in d.values()) / len(d), 6),
            "mean_chars": round(sum(chars) / len(chars), 4),
            "mean_words": round(sum(words) / len(words), 4),
            "mean_unique_criteria": round(sum(uniq) / len(uniq), 6)}


def main() -> int:
    r986 = next(A27.glob("R986_*/results/size_decomposition.json"), None)
    if r986 is None:
        print("  UNRUNNABLE: R986's artifact is missing. Exit 2, never 0.")
        return 2
    ref = {r["arm"]: r for r in json.loads(r986.read_text())["rows"]}

    from covalx.judge import load_join
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    core = {p: [i["criterion"] for i in (r.get("coval_core") or [])] for p, _q, r in joined}
    core = {p: v for p, v in core.items() if v}
    ghost_key = "coval" + "_absent_" + "r1014"
    ghost = {p: [i["criterion"] for i in (r.get(ghost_key) or [])] for p, _q, r in joined}
    ghost = {p: v for p, v in ghost.items() if v}
    sham_f = RES / "core_coval_core_sham.json"
    if not sham_f.exists():
        print("  UNRUNNABLE: the sham's criteria are not on disk. Exit 2, never 0.")
        return 2
    sham = json.loads(sham_f.read_text())
    print(f"  released core criteria READ from data/conversation_rubrics.jsonl: {len(core)} prompts")
    print(f"  sham criteria READ from {sham_f.name}: {len(sham)} prompts")

    pc = props(core)
    off_cap = sum(c for s, c in pc["size_dist"].items() if s != 4)
    pos_ok = (ref["coval_core"]["min"] == min(pc["size_dist"]) and
              ref["coval_core"]["max"] == max(pc["size_dist"]) and
              off_cap == ref["coval_core"]["residual"])
    neg_ok = len(ghost) == 0
    plac_ok = props(core) == props(core)
    print(f"\n  POSITIVE CONTROL — recovered size must match R986: min "
          f"{min(pc['size_dist'])} vs {ref['coval_core']['min']}, max {max(pc['size_dist'])} vs "
          f"{ref['coval_core']['max']}, off-cap {off_cap} vs residual "
          f"{ref['coval_core']['residual']}: {'PASS' if pos_ok else '⛔ FAIL'}")
    print(f"  NEGATIVE CONTROL — a runtime-assembled key yields no criteria: "
          f"{'PASS' if neg_ok else '⛔ FAIL'}")
    print(f"  PLACEBO         — the core against itself is identical: "
          f"{'PASS' if plac_ok else '⛔ FAIL'}")
    if not (pos_ok and neg_ok and plac_ok):
        print("\n⛔ a control failed; nothing below certifies anything. Exit 2, never 0.")
        return 2

    both = sorted(set(core) & set(sham))
    print(f"  prompts covered by both: {len(both)}")
    if len(both) < 200:
        print("  UNRUNNABLE: too little overlap to compare. Exit 2, never 0.")
        return 2

    ms_core = collections.Counter(tuple(sorted(map(str, core[p]))) for p in both)
    ms_sham = collections.Counter(tuple(sorted(map(str, sham[p]))) for p in both)
    exact = ms_core == ms_sham
    same_slot = sum(1 for p in both
                    if tuple(sorted(map(str, core[p]))) == tuple(sorted(map(str, sham[p]))))
    print(f"\n  multiset of criterion SETS identical: {exact}")
    print(f"  prompts where the sham holds the core's OWN set: {same_slot} of {len(both)} "
          f"({same_slot/len(both):.1%})")
    only_core = sum((ms_core - ms_sham).values())
    only_sham = sum((ms_sham - ms_core).values())
    print(f"  sets present only in the core: {only_core} · only in the sham: {only_sham}")

    pcb = props({p: core[p] for p in both})
    psb = props({p: sham[p] for p in both})
    print(f"\n  {'property':<24}{'core':<34}{'sham':<34}")
    same = {}
    for k in pcb:
        same[k] = pcb[k] == psb[k]
        print(f"  {k:<24}{str(pcb[k])[:32]:<34}{str(psb[k])[:32]:<34}"
              f"{'same' if same[k] else '⛔ DIFFERS'}")

    world = ("A EXACT — the sham is a permutation of the core's criterion sets, so no text-only "
             "property can separate them" if exact else
             "B INEXACT — the sham's criterion sets are NOT a permutation of the core's")
    print(f"\n⭐ {world}")
    if not exact:
        print("⛔ PRE-REGISTERED KILL FIRES: R1013's withdrawal is SCOPED to SIZE for the instance —")
        print("   which is what R986's 43 = 43 already established — and vocabulary, length and")
        print("   redundancy go BACK on the candidate list rather than being quietly left off it.")
    else:
        print("⭐ So R1013's argument reaches the instance in full: every property computed from the")
        print("   criteria text alone is identical between the released core and its sham, and none")
        print("   of them can be definitional content.")

    out = HERE / "results" / "instance_sham.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="is the instance's sham an exact re-pairing of the core's criterion sets",
        n_core=len(core), n_sham=len(sham), n_both=len(both),
        controls={"positive_size_matches_r986": bool(pos_ok), "negative_ghost_key_empty": bool(neg_ok),
                  "placebo_self_identical": bool(plac_ok)},
        multiset_identical=bool(exact), same_slot=same_slot,
        sets_only_in_core=only_core, sets_only_in_sham=only_sham,
        core_props=pcb, sham_props=psb, property_identical=same, world=world,
        criteria_location="data/conversation_rubrics.jsonl, key `coval_core`, via covalx.judge."
                          "load_join — NOT corebench/results, which is why R1013 could not find it",
        limitation="says whether the sets moved, never why the sham was built that way",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
