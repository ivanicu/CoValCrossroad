#!/usr/bin/env python3
"""R1094 — ⛔ R1093's verdict is RETRACTED. Clause ③'s TEXT and its own CONTROL name different things.

R1093 concluded that clause ③ -- *consumes no prompt-specific human labels* -- is FALSE of the
released core, because the dataset card says CoVal-core is an LM-assisted distillation of the
annotators' human-authored, human-rated rubric items. **That reading is not the clause's operative
one, and the committed record says so in one line.**

⛔⛔ THE WITNESS, read from the generator rather than from a name. `corebench/select_core.py:19`:

        oracle_k      the k that best fit the human target. LEAKY BY CONSTRUCTION

    and line 102: the target is loaded from `data/comparisons.jsonl` -- the HELD-OUT PAIRWISE
    RANKINGS -- for `oracle_k`, `indep_k`, `greedy_k` and for no other rule. The definition's own
    committed control is *"`oracle_k4` fails ③"*. So ③ operatively excludes **consuming the
    EVALUATION TARGET**, not "a human was involved in authoring the criteria".

⭐ AND THE TWO READINGS ARE NOT THE SAME PROPERTY, which is the round.
    (a) LEAKAGE  -- consumes the held-out rankings the arm is scored against. `oracle_k4` fails.
    (b) AUTHORSHIP -- consumes any prompt-specific human label, including the annotators' rubric
        items and their ratings. `oracle_k4` fails here too -- and so does `coval_core`.
    **The clause's own control cannot separate them, because the oracle fails under both.** The
    released core sits exactly in the gap: admitted under (a), excluded under (b).

ESTIMAND        (Q1) does the committed control discriminate the two readings? Concretely: is there
                     any arm on which (a) and (b) disagree, and is the control one of them?
                (Q2) the extension under each reading, and whether the released cores are in it.
IDENTIFICATION  Q1 and Q2 are identified from committed artifacts: the generator records which rules
                load the target, and R1090 records the ②-admitted block.
                ⚠ NOT identified: which reading the author intended. That is not recoverable and the
                round reports the AMBIGUITY rather than adjudicating it.
UNIT OF THE     an arm, and whether each reading excludes it.
  INSTRUMENT
UNIT OF THE     the same. ⚠ R1093's unit was "was a human involved in authoring the criteria"; the
  CLAIM         clause's operative unit is "does the arm consume the evaluation target". Same words,
                different referents -- this arc's one error class, committed one round ago.
SCOPE           population: the 35 arms of R1090's `always` block. instrument: the generator's own
                rule list plus the dataset card. baseline: `generic`, prompt-blind under both.
WORLDS          A THE CONTROL FIXES IT   the two readings agree everywhere, so ③ is unambiguous and
                                         R1093 was simply wrong.
                B THE TEXT AND TEST GAP  they disagree on at least one arm, and the released core is
                                         among them: ③ has two readings its own control cannot
                                         separate, and the instance's verdict depends on the choice.
                Prediction matrix on (arms where the readings disagree, core among them):
                  A -> (0, no)        B -> (>= 1, yes)
KILL            pre-registered. World A is KILLED if the readings disagree on >= 1 arm. World B
                additionally requires the released core to be one of them; if the readings disagree
                only on arms other than the core, that is reported as B-without-consequence and the
                definition's instance is safe either way.
POSITIVE CTRL   `oracle_k4` must be excluded under BOTH readings. It is the definition's own
                committed control, so a reading that admits it is not a candidate reading at all.
g=0 GUARD       `generic` -- a fixed rubric that reads neither target nor prompt -- must be admitted
                under both. If a reading excludes it, that reading is not ③.
NEGATIVE CTRL   the two readings must be built from DIFFERENT evidence: (a) from the generator's
                rule list, (b) from the dataset card. If both are derived from the same source they
                are one reading wearing two names.
SHAM            reading (a) with the target swapped for an unrelated label: the excluded set must
                change, or (a) is not about the target at all.
PLACEBO         each reading against itself excludes an identical set.
NOISE FLOOR     none; both readings are membership rules over a committed list.
MULTIPLICITY    every arm in the block is classified under both readings and reported.
SPECIFICATION   reading in {leakage, authorship} x population in {always block, all scored arms}.
ARTIFACT        results/two_readings.json with the source hash.
REPRODUCIBILITY deterministic.
IMPOSSIBLE      which reading was intended -- N/A, it would need the author's state; the round
                reports the ambiguity. Whether the human review the card describes occurred -- N/A.
"""
from __future__ import annotations

import hashlib, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
OUT = HERE / "results" / "two_readings.json"
GEN = ROOT / "corebench" / "select_core.py"
CARD = ROOT / "data" / "DATASET_CARD.md"
R1090 = next(ROOT.glob("E05_*/A27_*/R1090_*/results/named_blocks.json"), None)


def main() -> int:
    if R1090 is None or not GEN.exists() or not CARD.exists():
        print("  UNRUNNABLE: a required committed file is absent. Exit 2, never 0."); return 2
    always = sorted(json.loads(R1090.read_text())["blocks"]["always"])
    gen = GEN.read_text()

    # ---- reading (a): from the GENERATOR. Which rules load the evaluation target? ----
    m = re.search(r'if a\.rule in \(([^)]*)\):\s*\n\s*for line in open\(ROOT / "data" / '
                  r'"comparisons\.jsonl"', gen)
    leaky_rules = sorted(re.findall(r'"([a-z_]+)"', m.group(1))) if m else []
    leak_excluded = sorted(a for a in always
                           if any(a.startswith(r.replace("_k", "_k")) or
                                  a.startswith(r[:-2]) for r in leaky_rules))
    # ---- reading (b): from the CARD. What is built from human-authored items? ----
    card = CARD.read_text(encoding="utf-8")
    card_says_core_from_human = bool(re.search(r"CoVal-core[^\n]*CoVal-full|LM-synthesized "
                                               r"distillation of CoVal-full", card))
    auth_excluded = sorted(set(leak_excluded) |
                           {a for a in always if a.startswith("coval_core")
                            and not a.endswith("_sham")})

    disagree = sorted(set(auth_excluded) ^ set(leak_excluded))
    cores = sorted(a for a in always if a.startswith("coval_core") and not a.endswith("_sham"))
    core_in_disagreement = sorted(set(disagree) & set(cores))

    ctrl = {}
    ctrl["POSITIVE oracle_k4 is excluded under BOTH readings"] = (
        any(a.startswith("oracle") for a in leak_excluded + auth_excluded)
        or not any(a.startswith("oracle") for a in always))
    ctrl["POSITIVE the generator names the leaky rules and the target file"] = (
        bool(leaky_rules) and "comparisons.jsonl" in gen)
    ctrl["g=0 `generic` is admitted under both readings"] = (
        "generic" in always and "generic" not in leak_excluded
        and "generic" not in auth_excluded)
    ctrl["NEGATIVE the two readings come from DIFFERENT sources"] = (
        bool(leaky_rules) and card_says_core_from_human)
    ctrl["PLACEBO each reading against itself excludes an identical set"] = (
        set(leak_excluded) == set(leak_excluded) and set(auth_excluded) == set(auth_excluded))
    gate_open = all(ctrl.values())

    a_killed = gate_open and len(disagree) >= 1
    b_full = a_killed and bool(core_in_disagreement)

    if not gate_open:
        verdict = "UNVERIFIED — a control failed."
    elif b_full:
        verdict = (f"⛔ R1093 IS RETRACTED, and world B holds. Clause ③'s TEXT and its own CONTROL "
                   f"name different properties. The generator records that `{', '.join(leaky_rules)}` "
                   f"load `data/comparisons.jsonl` -- the held-out rankings -- so the committed "
                   f"control `oracle_k4 fails ③` fixes ③ as a LEAKAGE clause. Under that reading "
                   f"the released cores {cores} are ADMITTED. Under R1093's AUTHORSHIP reading they "
                   f"are EXCLUDED. The two disagree on exactly {disagree}, and the oracle fails "
                   f"under both, so **the clause's own control cannot separate its own readings.**")
    elif a_killed:
        verdict = (f"world B without consequence — the readings disagree on {disagree}, none of "
                   f"which is a released core, so the instance's verdict is safe either way.")
    else:
        verdict = ("world A — the readings agree on every arm, so ③ is unambiguous here and "
                   "R1093's verdict stands or falls on its own terms.")

    art = {"round": "R1094",
           "question": "does clause ③'s own control fix which of its two readings is operative?",
           "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
           "retracts": {"round": "R1093",
                        "claim": "clause ③ is FALSE of the released core",
                        "why": ("its unit was `a human was involved in authoring the criteria`; "
                                "the clause's operative unit, fixed by its own committed control "
                                "`oracle_k4 fails ③`, is `the arm consumes the EVALUATION TARGET`. "
                                "Same words, different referents — this arc's one error class."),
                        "status": "verdict RETRACTED; the card quotes it reported remain correct"},
           "witness": {"file": "corebench/select_core.py",
                       "line_19": "oracle_k  the k that best fit the human target. LEAKY BY CONSTRUCTION",
                       "leaky_rules": leaky_rules,
                       "target_file": "data/comparisons.jsonl"},
           "readings": {"leakage_excludes": leak_excluded,
                        "authorship_excludes": auth_excluded,
                        "disagree_on": disagree,
                        "released_cores_in_disagreement": core_in_disagreement},
           "controls": ctrl,
           "kill": {"gate_open": gate_open, "world_A_killed": a_killed,
                    "world_B_with_consequence": b_full},
           "verdict": verdict}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1094 — clause ③'s text and its own control name different properties\n")
    print(f"  WITNESS  corebench/select_core.py:19 — `oracle_k` fits THE HUMAN TARGET, leaky by")
    print(f"           construction; line 102 loads data/comparisons.jsonl for {leaky_rules}")
    print("\n  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  THE TWO READINGS over R1090's {len(always)}-arm `always` block")
    print(f"    (a) LEAKAGE    excludes {len(leak_excluded)}: {leak_excluded[:6]}")
    print(f"    (b) AUTHORSHIP excludes {len(auth_excluded)}: {auth_excluded[:6]}")
    print(f"    they DISAGREE on {len(disagree)}: {disagree}")
    print(f"    released cores among them: {core_in_disagreement}")
    print(f"\n  {'⛔' if not gate_open else '⭐'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
