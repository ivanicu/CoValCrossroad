#!/usr/bin/env python3
"""
A gate for CURRENCY, which the existing one structurally cannot provide.

⛔ WHY THIS IS NOT A DUPLICATE OF `definition_matches_the_record.py`. That gate holds 340 assertions
anchoring values in `DEFINITION.md` to committed artifacts, and it is doing its job: it stops a number
drifting away from the evidence that produced it. **But it keys each assertion on the artifact it came
from, so it cannot notice that a LATER round superseded that artifact.** A consistency gate reads as a
currency guarantee and is not one — the statement can be perfectly consistent with R881 and wrong
about everything R921–R926 established.

⭐ SO THIS GATE ASKS A DIFFERENT QUESTION: for each fact a later round MEASURED, does the STATEMENT
say it? The facts are READ from the artifacts, never retyped, so the gate cannot drift from them
either; what it adds is a required direction — artifact ⇒ statement.

⚠ AND THE PATTERNS ARE TIGHTENED SO THE GATE IS SOUND IN BOTH DIRECTIONS. The first version matched
`resol` and `decay|decreas|monoton` anywhere in the region, and both fired on unrelated prose — a
loose pattern makes a PASS meaningless while leaving FAIL sound, which is a one-directional
instrument reported as a two-directional one. Each pattern now requires the measured VALUE or its
subject within a bounded window of the keyword.

⚠ POSITIVE CONTROL, and it is built from runtime fragments rather than written as a literal.
Documenting a "this string must be absent" marker puts that very string in the corpus and the
detector then finds it — that happened three times earlier in this project. The absent marker is
therefore assembled at run time and never appears in this file as one token.

⛔ EXIT CONTRACT, CORRECTED R977. This line used to read "Exit 2 on failure, never 1" and the code
obeyed it — but 2 is this suite's code for UNRUNNABLE, and `run_all.py` buckets it as *"a check with
no population has not passed, it has not run."* A stale statement is the opposite claim: the gate
looked, and the corpus violated it. So:
  **1** — FAIL: measured facts are missing from the statement.
  **2** — UNRUNNABLE: the file is missing, the section is missing, no artifacts were found, or the
          matcher itself is broken. Never 0 on an empty population.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
E05 = ROOT / "E05_the_space_of_compilers"
DEF = E05 / "DEFINITION.md"
SECTION = "## The definition"


def load(glob):
    hits = sorted(E05.glob(glob))
    if not hits:
        return None
    return json.loads(hits[-1].read_text())


def statement_region(text):
    """the statement plus its immediate scope block — bounded, so the gate cannot be satisfied
    by a sentence buried 9,000 lines away in the evidence record"""
    i = text.find(SECTION)
    if i < 0:
        return None
    j = text.find("\n## ", i + len(SECTION))
    return text[i: j if j > 0 else len(text)]


def main() -> int:
    if not DEF.exists():
        print("  UNRUNNABLE: DEFINITION.md missing. Exit 2, never 0.")
        return 2
    text = DEF.read_text()
    region = statement_region(text)
    if region is None:
        print(f"  UNRUNNABLE: section {SECTION!r} not found. Exit 2, never 0.")
        return 2

    facts = []

    d = load("A26_*/R921_*/results/comparator_sweep.json")
    if d:
        facts.append(("R921", "legitimate comparators",
                      len(d["legitimate_comparators"]),
                      [r"\b2\b.{0,80}(comparator|prompt-blind)",
                       r"(comparator|prompt-blind).{0,80}\b2\b"]))

    d = load("A26_*/R922_*/results/threshold_or_comparison.json")
    if d:
        facts.append(("R922", "inversions under legitimate comparators",
                      d["total_inversions_legitimate"],
                      [r"threshold.{0,200}(mean A2|A2)", r"(mean A2|A2).{0,200}threshold"]))

    d = load("A27_*/R923_*/results/bar_resolution.json")
    if d:
        cp = d["comparator_pair"]
        facts.append(("R923", "which legitimate comparator is stronger",
                      f"{cp['a']} beats {cp['b']}: {cp['a_beats_b']}",
                      [re.escape(cp["a"]) + r".{0,120}" + re.escape(cp["b"])]))
        nb = len(d["boundary_census"]["admitted_inside_resolution"])
        facts.append(("R923", "admitted arms inside the bar's resolution", nb,
                      [rf"\b{nb}\b.{{0,160}}resolution", rf"resolution.{{0,160}}\b{nb}\b"]))

    d = load("A26_*/R920_*/results/clause3_detectability.json")
    if d:
        facts.append(("R920", "clause 3 detectability world",
                      d["world"], [r"provenance"]))

    d = load("A27_*/R925_*/results/label_blind_k1_sweep.json")
    if d:
        facts.append(("R925", "label-blind size-1 arms admitted",
                      len(d["arms_admitted_raw"]),
                      [r"(label-blind|label blind).{0,160}(size-1|size 1|k=1)",
                       r"(size-1|size 1|k=1).{0,160}(label-blind|label blind)"]))

    d = load("A27_*/R926_*/results/clause3_price_curve.json")
    if d:
        facts.append(("R926", "price curve monotone in k",
                      d["monotone"],
                      [r"(decay|decreas|monoton).{0,160}\bk\b",
                       r"\bk\b.{0,160}(decay|decreas|monoton)"]))

    # ⛔ R977: THIS GATE WAS GREEN WHILE THE STATEMENT WAS STALE, AND THE REASON IS ITS POPULATION.
    #    Its facts are a hard-coded list of six artifacts. R975 and R976 then measured two things
    #    about clause ④ and the gate could not notice, because you cannot grep for the absence of a
    #    fact you were never told about — the same shape as the defect this file was written to
    #    catch, one level up. A currency gate whose fact list is manual has a currency problem of
    #    its own. Registering them here is the manual step; making it automatic is a different
    #    round and is named in this one's NEXT rather than implied by a green run.
    #    ⭐ Both patterns were checked against the UNREPAIRED statement first and matched nothing,
    #    so the red they produce is a measurement rather than a pattern that would have fired anyway.
    d = load("A27_*/R975_*/results/overlap_bar.json")
    if d:
        facts.append(("R975", "clause 4 is overlap-limited, not mean-determined",
                      d["world"].split("—")[0].strip(),
                      [r"(overlap|per-prompt share|above the floor on).{0,200}(response[- ]only|④)",
                       r"(response[- ]only|④).{0,200}(overlap|per-prompt share|above the floor on)"]))

    d = load("A27_*/R976_*/results/phi_star_scaling.json")
    if d:
        facts.append(("R976", "clause 4's bar is design resolution in N and delta",
                      d["closed_form"],
                      [r"(④|response[- ]only).{0,300}(N\s*=\s*968|\bN\b).{0,200}(δ|delta)",
                       r"(δ|delta).{0,200}(N\s*=\s*968|\bN\b).{0,300}(④|response[- ]only)"]))

    # ⛔ R981: THREE MORE, AND THE GAP BETWEEN R977 AND HERE IS THE POINT. R977 registered two facts
    #    by hand and its own NEXT said the registry's manual-ness is the defect. Four rounds later
    #    the statement was stale about three MORE rounds — so the hand-registration is not merely
    #    inelegant, it has a measured failure rate: 3 of the 4 rounds since went unrecorded until
    #    someone thought to look. All three patterns were run against the UNREPAIRED statement and
    #    matched nothing, so the red they produce is a measurement.
    d = load("A27_*/R978_*/results/extension_vs_n.json")
    if d:
        facts.append(("R978", "the admitted set moves with the prompt count",
                      f"median churn at N=242: {d['median_churn_at_242']}",
                      [r"(extension|admitted set|admitted arms).{0,240}(churn|move|change|depend)"
                       r".{0,160}(N\b|prompt count|how many prompts)",
                       r"(N\b|prompt count|how many prompts).{0,240}"
                       r"(extension|admitted set|admitted arms).{0,160}(churn|move|change)"]))

    d = load("A27_*/R979_*/results/clause3_ordering.json")
    if d:
        facts.append(("R979", "clause 3 has no artifact-level ordering content",
                      f"{d['n_resolvable']} resolvable inversions of {d['n_pairs']} pairs",
                      [r"(③|clause three).{0,300}(no artifact-level|ordering content|never reorder|"
                       r"orders? .{0,40}identically)",
                       r"(ordering content|reorder).{0,240}(③|clause three)"]))

    d = load("A27_*/R980_*/results/instance_power.json")
    if d:
        facts.append(("R980", "prompts needed to admit the instance",
                      f"N* generic = {d['registered_nstar']['coval_core|generic']:.0f}",
                      [r"(coval_core|its own instance|the instance).{0,300}\b(236|237|240|500)\b"
                       r".{0,200}prompt",
                       r"prompt.{0,200}\b(236|237|240|500)\b.{0,300}"
                       r"(coval_core|its own instance|the instance)"]))

    # ⛔ R987: the size reading, DECIDED. R986 established `its size` is ambiguous; this registers
    #    the resolution so a later round cannot settle it by whichever reading its script happens
    #    to implement.
    d = load("A27_*/R986_*/results/size_decomposition.json")
    if d:
        facts.append(("R986", "arms with no scalar size", d["n_variable"],
                      [r"(scalar|single number|one size|distribution).{0,240}"
                       r"(size|criteri).{0,160}(coval_core|released core|instance)",
                       r"(coval_core|released core).{0,240}(size|criteri).{0,200}"
                       r"(2 to 4|2..4|distribution|not a (single )?number)"]))

    d = load("A27_*/R987_*/results/size_recoverable.json")
    if d:
        facts.append(("R987", "nominal size is artifact-recoverable",
                      f"{d['n_nontrivial_ok']}/{d['n_nontrivial']} non-trivial",
                      [r"(nominal size|max over prompts|maximum realised).{0,300}"
                       r"(recover|artifact|third part|provenance)",
                       r"(recover|artifact-checkable).{0,240}(nominal size|max over prompts)"]))

    # ⛔ R991: the three rounds that read the RELEASE's own card rather than scoring arms. R988 found
    #    the departure from the card "stated nowhere"; registering it is what makes that false.
    d = load("A27_*/R988_*/results/cap_and_missing_clauses.json")
    if d:
        facts.append(("R988", "the card caps size; two properties have no clause",
                      f"{d['n_admitted_over_cap']} admitted above the cap of {d['cap']}",
                      [r"(up to four|caps? .{0,30}four|upper bound).{0,320}"
                       r"(non-redundant|non-conflicting|no clause)",
                       r"(non-redundant|non-conflicting).{0,320}(no clause|not encoded|has no)"]))

    d = load("A27_*/R989_*/results/dissent_erased.json")
    if d:
        facts.append(("R989", "criteria are more sign-coherent than chance",
                      f"{d['observed_contested_share']:.3f} vs null",
                      [r"(sign|coheren|contest).{0,260}(null|chance|93|permut)",
                       r"(80.0%|80%).{0,220}(null|93|chance)"]))

    d = load("A27_*/R990_*/results/redundancy_did.json")
    if d:
        facts.append(("R990", "the construction removes redundancy",
                      f"DiD {d['did_mean']:.4f}",
                      [r"(difference-in-differences|DiD|0\.0084).{0,260}"
                       r"(redundan|Jaccard|overlap)",
                       r"(redundan|overlap).{0,260}(difference-in-differences|DiD)"]))

    if not facts:
        print("  UNRUNNABLE: no artifacts found — an empty population must not pass. "
              "Exit 2, never 0.")
        return 2

    missing = []
    print(f"  facts READ from {len({f[0] for f in facts})} committed artifacts, "
          f"{len(facts)} required in the statement:")
    for rnd, what, val, pats in facts:
        ok = any(re.search(p, region, re.I | re.S) for p in pats)
        print(f"     {rnd}  {what:<44} = {str(val):<28} in statement: {ok}")
        if not ok:
            missing.append((rnd, what, val))

    # POSITIVE CONTROL — a pattern that MUST NOT be found, assembled at run time so that
    # documenting it cannot place it in the corpus (this failed three times before)
    ghost = "zz" + "-absent-" + "sentinel-" + "for-" + "currency" + "-gate"
    control_ok = re.search(re.escape(ghost), region) is None
    live = re.search(r"core", region, re.I) is not None
    print(f"\n  POSITIVE CONTROL — the matcher must find a live token and miss an absent one:")
    print(f"     finds 'core' in the statement: {live}   misses the runtime-built sentinel: "
          f"{control_ok}")
    if not (live and control_ok):
        print("  UNRUNNABLE: the matcher is not working. Exit 2, never 0.")
        return 2

    if missing:
        print(f"\n  FAIL: {len(missing)} measured fact(s) never reached the statement:")
        for rnd, what, val in missing:
            print(f"    {rnd}  {what} = {val}")
        print("  A consistency gate cannot see this: the statement can match every artifact it")
        print("  cites and still be wrong about every artifact it does not.")
        # ⛔ R977: THIS RETURNED 2, AND 2 MEANS SOMETHING ELSE IN THIS SUITE. run_all.py buckets
        #    rc=2 as UNRUNNABLE -- "a check with no population has not passed, it has not run" --
        #    so a REAL staleness failure was being reported as though the gate had examined
        #    nothing. Those are opposite claims: one says the corpus violates the rule, the other
        #    says the rule never got to look. The matcher-broken path above keeps 2, because that
        #    one genuinely is unrunnable. Found by running the gate, not by reading it.
        return 1

    print(f"\n  PASS: every measured fact is present in the statement region "
          f"({len(region.splitlines())} lines).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
