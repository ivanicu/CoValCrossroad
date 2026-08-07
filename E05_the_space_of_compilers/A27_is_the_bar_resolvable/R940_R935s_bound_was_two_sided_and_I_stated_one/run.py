#!/usr/bin/env python3
"""
R940 · R935's `pass on silence` list contains a check that plants and fires — the bound was
        two-sided and I stated only one side.

⛔ WHY, AND WHY NOT THE ROUND MY NEXT PROPOSED. R939 ended by proposing mutation-testing the whole
suite to turn R935's *passes on silence* count into a *passes on a mutant* count. **The cost meter
kills it:** most gates have no function to mutate — their mutant is a planted violation, which is
precisely what R935 already measured — and mutating 66 checks against a suite that takes twenty
minutes buys a diffuse result for an enormous spend. The cheap sharp question was one file away.

⭐ **R935 FLAGGED `attack_scope_reaches_the_reader` AS PASSING ON SILENCE. IT DOES NOT.** Read: it
writes four separate mutations into the LIVE `assurance/ASSURANCE.md`, runs the real gate against
each, and restores in a `finally`. Run: **4/4 vectors behave as specified**, including *"entry 57's
exact bug (110-char cut)"* and a NEGATIVE vector — *"reflowed whitespace (must NOT flag)"* — so it
has both directions. Its exit 0 is EARNED, and R935's static detector missed it because the file
says `write_text` and *"vector"* where the regex wanted `plant` or `positive control`.

⭐⭐⭐ **AND THAT CORRECTS MORE THAN A COUNT — IT CORRECTS THE SHAPE OF THE BOUND.** R935 wrote:
*"BOUNDED FROM ONE SIDE ONLY: 'has a plant token' is not 'has a WORKING plant' … so 12–17%
UNDERSTATES the defect."* **That names one direction and there are two:**
  · a TOKEN with no working plant -> protection overstated, defect understated.
    Instance: R934's own placebo, which compared two empty lists and passed.
  · a WORKING PLANT with no token -> protection understated, **defect OVERSTATED**.
    Instance: this one, measured here.
**I published a two-sided error as one-sided, in the direction that made my own number look
conservative.** That is the flattering direction, which is the one the register says an
unavailability claim must never take.

ESTIMAND        how many of R935's 11 `pass on silence` checks actually carry a working plant, and
                the corrected count and share.
IDENTIFICATION  exact — a read of eleven files plus one live run of the one that plants.
SCOPE           population: R935's committed `pass_on_silence` list, read from its artifact
                instrument: mutating writes cited by LINE, plus running the candidate
                baseline:   R935's own count of 11 and share of 17%
                regime:     the committed corpus at HEAD
WORLDS          A · at least one carries a real plant -> R935's count over-counts the defect and
                    its one-sided bound is wrong in the flattering direction
                B · none does -> the detector had no false negatives here and R935 stands
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE: the audit must find the known plant — `attack_scope_reaches_the_
                     reader` must show mutating writes AND its run must report 4/4 vectors. If the
                     audit cannot see a plant I have already read, it cannot be trusted on ten
                     files I have not.
                  ⭐ ② NEGATIVE / DISCRIMINATION: `consistency` also contains a `write_text`, but
                     it writes its OWN output json. The audit must classify it as NOT a plant, or
                     it is counting any write and would find a plant in anything that saves a file.
                  ⭐ ③ EVERY VERDICT CITES A LINE. A keyword verdict is what produced the error
                     being corrected; a line number is checkable by someone else.
                  ⭐ ④ BOTH DIRECTIONS OF THE BOUND REPORTED, each with a named instance, because
                     stating one was the defect.
MULTIPLICITY    11 checks × {mutating writes, classification}; all printed including the zeros.
ARTIFACT        results/two_sided_bound.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: this corrects the FALSE-NEGATIVE direction by reading. The
                false-POSITIVE direction — a token whose plant is vacuous — is instanced but NOT
                counted here, so the corrected number is still one-sided, now in the other
                direction, and says so.
"""
import json, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
MUTATE = re.compile(r"\.write_text\(|shutil\.copy|shutil\.move")
OWN_OUTPUT = re.compile(r"write_text\(json\.dumps|/ *[\"'][\w.]+\.json[\"']\s*\)\.write_text")


def main() -> int:
    r935 = next(A27.glob("R935_*/results/pass_on_silence.json"), None)
    if r935 is None:
        print("  UNRUNNABLE: R935 artifact missing. Exit 2, never 0.")
        return 2
    d = json.loads(r935.read_text())
    silent = d["pass_on_silence"]
    n_checks = d["n_checks"]
    print(f"  R935 committed: {len(silent)} pass-on-silence of {n_checks} checks "
          f"({d['share_pass_on_silence']:.0%})")

    rows = []
    for k in silent:
        f = ROOT / "assurance" / f"{k}.py"
        lines = f.read_text().splitlines()
        writes = [(i + 1, l.strip()) for i, l in enumerate(lines) if MUTATE.search(l)]
        own = [w for w in writes if OWN_OUTPUT.search(w[1])]
        real = [w for w in writes if w not in own]
        rows.append({"check": k, "n_writes": len(writes), "n_own_output": len(own),
                     "n_mutating": len(real),
                     "evidence": [f"L{ln}: {s[:70]}" for ln, s in real[:3]],
                     "is_plant": bool(real)})
    print(f"\n  ③ EVERY VERDICT CITES A LINE — mutating writes per check:")
    print(f"     {'check':<44}{'writes':>7}{'own-out':>9}{'plant?':>8}")
    for r in rows:
        print(f"     {r['check']:<44}{r['n_writes']:>7}{r['n_own_output']:>9}"
              f"{str(r['is_plant']):>8}")
        for e in r["evidence"]:
            print(f"        {e}")

    plants = [r for r in rows if r["is_plant"]]
    c1_seen = any(r["check"] == "attack_scope_reaches_the_reader" and r["is_plant"] for r in rows)
    run = subprocess.run([str(ROOT / ".venv/bin/python"),
                          "assurance/attack_scope_reaches_the_reader.py"],
                         cwd=ROOT, capture_output=True, text=True)
    m = re.search(r"(\d+)/(\d+) vectors behave as specified", run.stdout or "")
    vectors = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    c1 = c1_seen and vectors[0] == vectors[1] and vectors[1] >= 4
    print(f"\n  ① POSITIVE — the known plant is seen by the audit: {c1_seen}; and running it "
          f"reports {vectors[0]}/{vectors[1]} vectors: {c1}  {'PASS' if c1 else 'FAIL'}")

    cons = next((r for r in rows if r["check"] == "consistency"), None)
    c2 = cons is not None and cons["n_writes"] > 0 and not cons["is_plant"]
    print(f"\n  ② NEGATIVE / DISCRIMINATION — `consistency` writes {cons['n_writes'] if cons else 0} "
          f"file(s) but they are its OWN output, so it must NOT count as a plant: {c2}  "
          f"{'PASS' if c2 else 'FAIL — the audit counts any write'}")

    if not (c1 and c2):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "rows": rows},
                  open(OUT / "two_sided_bound.json", "w"), indent=2)
        return 2

    corrected = len(silent) - len(plants)
    world = "A" if plants else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: {len(plants)} of {len(silent)} 'silent' checks actually "
          f"carry a working plant — {[p['check'] for p in plants]}")
    print(f"     R935's count {len(silent)} -> {corrected}; share "
          f"{d['share_pass_on_silence']:.0%} -> {corrected / n_checks:.0%}")
    print(f"     detector false-negative rate on this subset: {len(plants)}/{len(silent)} = "
          f"{len(plants)/len(silent):.0%}")

    print(f"\n  ④ BOTH DIRECTIONS OF THE BOUND, each with a named instance:")
    print(f"     TOKEN, no working plant  -> protection OVERSTATED, defect understated.")
    print(f"        instance: R934's own placebo, which compared two empty lists and passed.")
    print(f"     WORKING PLANT, no token  -> protection UNDERSTATED, defect OVERSTATED.")
    print(f"        instance: attack_scope_reaches_the_reader, {vectors[0]}/{vectors[1]} vectors.")
    print(f"     ⛔ R935 NAMED ONLY THE FIRST, which is the direction that made its own number look")
    print(f"     conservative — the flattering direction an unavailability claim must never take.")
    print(f"     ⚠ AND THIS ROUND IS ITSELF ONE-SIDED, now the other way: it corrects the")
    print(f"     false-NEGATIVE direction by reading and does NOT count the false-POSITIVE one.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world,
               "r935_count": len(silent), "r935_share": d["share_pass_on_silence"],
               "corrected_count": corrected, "corrected_share": corrected / n_checks,
               "n_checks": n_checks,
               "false_negatives": [p["check"] for p in plants],
               "false_negative_rate_on_subset": len(plants) / len(silent),
               "vectors_of_the_missed_plant": list(vectors),
               "rows": rows,
               "bound_is_two_sided": {
                   "token_without_working_plant": {"effect": "defect UNDERSTATED",
                                                   "instance": "R934's own placebo"},
                   "working_plant_without_token": {"effect": "defect OVERSTATED",
                                                   "instance": "attack_scope_reaches_the_reader"},
                   "r935_named_only": "token_without_working_plant",
                   "why_that_matters": "it is the direction that made R935's number look "
                                       "conservative — the flattering direction"},
               "this_round_is_also_one_sided": "it corrects the false-negative direction by "
                                               "reading and does not count the false-positive one",
               "unit_note": "counts are CHECKS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "two_sided_bound.json", "w"), indent=2)
    print(f"\n  artifact: results/two_sided_bound.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
