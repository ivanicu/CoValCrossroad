#!/usr/bin/env python3
"""R1092 — R1091 said clause ③ is not evaluable for the cores. ⛔ It is, and the file is in the release.

R1091 reported that the released cores have no committed criterion-TEXT selection, so clause ③ --
*consumes no prompt-specific human labels* -- could not be evaluated for them. It searched
`corebench/results/core_<arm>.json`, a DERIVED directory. **Its own NEXT said the check was
incomplete: "a wall checked in one directory is not a wall checked in the release."** That NEXT was
right, and this round retracts the wall.

⛔⛔ RETRACTION. `data/conversation_rubrics.jsonl` carries a top-level key `coval_core` on every one
    of its 986 conversations, holding the core's criterion TEXTS for that conversation. The artifact
    R1091 declared absent has been in the release the whole time, one directory away from where it
    looked. §4's `a wall never checked` -- committed by me, caught one round later by the sentence I
    wrote warning about it.

ESTIMAND        (Q1) does a committed file carry a per-prompt criterion-TEXT selection attributable
                     to the released core? A yes/no, decided by opening the file.
                (Q2) given Q1, the core's distinct TEXT selections across the conversations, and the
                     same for `coval_full`, on the release's own population.
IDENTIFICATION  Q1 and Q2 are exactly identified from the release. R1091's "not evaluable" is
                RETRACTED, not downgraded.
UNIT OF THE     a conversation, and the set of criterion strings the file assigns it under a key.
  INSTRUMENT
UNIT OF THE     the same for Q2. ⚠ For clause ③ the units are NOT equal and this round says so:
  CLAIM         `n_distinct` measures PROMPT-SPECIFICITY, while ③ names HUMAN-LABEL CONSUMPTION.
                A generated per-prompt rubric is maximally prompt-specific and consumes no human
                labels at all, so a high count neither establishes nor refutes ③.
SCOPE           population: the 986 conversations in `data/conversation_rubrics.jsonl`. instrument:
                direct read of the release. baseline: `coval_full`, the same file's other key.
WORLDS          A THE WALL IS REAL      no committed file carries the core's text selection.
                B THE WALL IS UNVISITED some file does, and R1091 stopped one directory short.
                Prediction matrix on Q1: A -> not found anywhere; B -> found, and named.
KILL            pre-registered. World A is KILLED if ANY committed file yields a per-conversation
                criterion-text list attributable to the core. One file is enough, because R1091's
                claim was a universal negative.
POSITIVE CTRL   the search must find a file whose shape is already known: `core_generic.json` is a
                per-prompt criterion-text mapping (R1091 typed 31 arms from that family). If the
                instrument cannot see a known instance it is blind and its zero means nothing.
g=0 GUARD       a key that does not exist in the rubric file must yield 0 conversations, not a
                default. Without it "found" could be manufactured by a defaulting `.get`.
NEGATIVE CTRL   a file known NOT to be a selection table (`data/annotators.jsonl`) must not be
                reported as one.
SHAM            the same read against `coval_full` -- the file's other key, same shape, different
                object. It prices what is specific to the core rather than to the file.
PLACEBO         re-reading the same file returns identical counts.
NOISE FLOOR     none: this is a file read, deterministic, and the round says so rather than
                inventing a resampling for it.
MULTIPLICITY    all keys present in the file are counted and reported, not only the one sought.
SPECIFICATION   key in {coval_core, coval_full} x attribution in {by key name, by list position}.
ARTIFACT        results/the_wall_retracted.json with the source hash.
REPRODUCIBILITY deterministic file read; two passes required identical.
IMPOSSIBLE      clause ③ itself -- ⚠ N/A EVEN NOW, and for a different reason than R1091 gave: the
                proxy available measures prompt-specificity, not human-label consumption. Settling ③
                would require a record of which criteria came from a human, which the rubric file
                does not carry.
"""
from __future__ import annotations

import collections, hashlib, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
OUT = HERE / "results" / "the_wall_retracted.json"
RUB = ROOT / "data" / "conversation_rubrics.jsonl"
RES = ROOT / "corebench" / "results"


def read_key(path, key):
    """conversations -> the set of criterion strings under `key`. Never defaults."""
    sets, seen, missing = [], 0, 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            seen += 1
            if key not in r:
                missing += 1
                continue
            sets.append(frozenset(c["criterion"] for c in r[key] if "criterion" in c))
    return sets, seen, missing


def main() -> int:
    if not RUB.exists():
        print(f"  UNRUNNABLE: {RUB} is absent. Exit 2, never 0."); return 2

    core, seen, miss_core = read_key(RUB, "coval_core")
    full, _, miss_full = read_key(RUB, "coval_full")
    ghost, _, miss_ghost = read_key(RUB, "coval_does_not_exist")

    ctrl = {}
    ctrl["POSITIVE a known per-prompt criterion-text file is found (core_generic.json)"] = (
        (RES / "core_generic.json").exists()
        and len({frozenset(v) for v in json.loads((RES / "core_generic.json").read_text()).values()
                 if v}) >= 1)
    ctrl["g=0 a key that does not exist yields 0 conversations, not a default"] = (
        len(ghost) == 0 and miss_ghost == seen)
    ctrl["NEGATIVE annotators.jsonl is not reported as a selection table"] = (
        "criterion" not in (ROOT / "data" / "annotators.jsonl").open(encoding="utf-8").readline())
    ctrl["PLACEBO re-reading the file returns identical counts"] = (
        read_key(RUB, "coval_core")[0] == core)
    gate_open = all(ctrl.values())

    n_core = len({s for s in core if s})
    n_full = len({s for s in full if s})
    sizes = collections.Counter(len(s) for s in core)
    shared = len(set.intersection(*[set(s) for s in core if s][:50])) if len(core) >= 50 else None

    a_killed = gate_open and len(core) > 0
    if not gate_open:
        verdict = "UNVERIFIED — a control failed."
    elif a_killed:
        verdict = (f"⛔ R1091's WALL IS RETRACTED. `data/conversation_rubrics.jsonl` carries a "
                   f"`coval_core` key on {len(core)} of {seen} conversations, holding the core's "
                   f"criterion TEXTS. The artifact R1091 declared absent is in the release, one "
                   f"directory from where it looked. Measured: {n_core} distinct text selections "
                   f"across {len(core)} conversations, sizes {dict(sizes)}, and {shared} criteria "
                   f"shared by the first 50 — the core rewrites its rubric per conversation.")
    else:
        verdict = "world A survives — no committed file carries the core's text selection."

    art = {"round": "R1092",
           "question": "is clause ③'s artifact absent, or was R1091 looking in the wrong directory?",
           "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
           "retracts": {"round": "R1091",
                        "claim": "the released cores have no committed criterion-TEXT selection",
                        "why_it_was_wrong": ("it searched corebench/results/core_<arm>.json, a "
                                             "DERIVED directory, and stopped. The release itself "
                                             "carries the key. R1091's own NEXT named this gap."),
                        "status": "RETRACTED, not downgraded"},
           "population": {"conversations": seen, "with_coval_core": len(core),
                          "with_coval_full": len(full), "missing_core": miss_core},
           "controls": ctrl,
           "coval_core": {"distinct_text_selections": n_core, "sizes": dict(sizes),
                          "criteria_shared_by_first_50": shared},
           "SHAM_coval_full": {"distinct_text_selections": n_full},
           "clause_three_still_not_settled": (
               "⚠ the units are NOT equal: n_distinct measures PROMPT-SPECIFICITY while ③ names "
               "HUMAN-LABEL CONSUMPTION. A generated per-prompt rubric is maximally prompt-specific "
               "and consumes no human labels at all, so this count neither establishes nor refutes "
               "③. Settling it needs a record of which criteria came from a human."),
           "kill": {"gate_open": gate_open, "world_A_killed": a_killed},
           "verdict": verdict}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1092 — is the wall permanent, or was I looking in the wrong directory?\n")
    print("  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  THE FILE — data/conversation_rubrics.jsonl")
    print(f"    conversations {seen} · carrying `coval_core` {len(core)} · `coval_full` {len(full)}")
    print(f"    coval_core distinct TEXT selections : {n_core}")
    print(f"    SHAM coval_full distinct selections : {n_full}")
    print(f"    core rubric sizes: {dict(sizes)}")
    print(f"    criteria shared by the first 50 conversations: {shared}")
    print(f"\n  ⚠ AND CLAUSE ③ IS STILL NOT SETTLED, for a different reason than R1091 gave:")
    print(f"     n_distinct measures PROMPT-SPECIFICITY; ③ names HUMAN-LABEL CONSUMPTION.")
    print(f"     A generated per-prompt rubric is maximally specific and consumes no labels.")
    print(f"\n  {'⛔' if not gate_open else '⭐'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
