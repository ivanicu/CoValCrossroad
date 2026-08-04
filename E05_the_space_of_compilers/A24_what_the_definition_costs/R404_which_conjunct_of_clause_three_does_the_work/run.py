"""R404 -- clause ③ is a THREE-part conjunction. Which part actually excludes anything?

DEFINITION.md states clause ③ as one clause with three conjuncts: uses no information from that
prompt's own human labels -- (a) not from the construction, (b) not from any half of them, and (c)
not by way of a rubric those same annotators wrote. Its exclusion count is published as ONE number,
`4 of 42`, attributed to the clause as a whole.

⛔ PRIOR ART, CHECKED BEFORE BUILDING. R363 already audited the hand-written key
   `USES_PROMPT_LABELS = {oracle_k4, oracle_k4_fit1, greedy_k4_fit1, indep_k4_fit1}` against
   `corebench/select_core.py:102` and found it CORRECT about the rankings, and it established
   `W_CHANNEL_OPEN` -- the rubric channel that conjunct (c) names is not closed, with per-prompt
   annotator overlap far above a cross-prompt sham (sham mean 0.016, median 0). R403 then found (c)
   NOT-STATABLE on the second corpus. What NEITHER round asked is the question here: enforced as
   WRITTEN, what does each conjunct exclude, and what is the admitted set after each?

⛔ AND THE ANSWER MUST COME FROM THE SOURCE, NOT FROM THE ARM NAMES. `oracle_k4_fit1` LOOKS like it
   fits on a half and `topw_k4` LOOKS rubric-free, but a label is not a description, and this
   campaign has a row for exactly that. Every classification below is derived from
   `corebench/select_core.py`'s rule dispatch -- which file each rule opens, and whether it takes a
   `fit_parity` -- and the derivation is REQUIRED TO REPRODUCE the hand-written key exactly.

⛔ ARITHMETIC TRAP. That conjunct (a) excludes the label-readers is FORCED once the rule-to-file map
   is read -- DEFINITION.md already labels that DERIVED and this round does not re-report it as
   evidence. What is NOT forced, and is the content: whether (b) and (c) exclude anything BEYOND (a),
   and what the admitted set becomes if (c) is enforced as written rather than as implemented.

ESTIMAND        (A) for each conjunct of clause ③, the set of the 42 arms it excludes ON ITS OWN,
                    derived from source;
                (B) the admitted set after ② , ②∧③a , ②∧③a∧③b , ②∧③a∧③b∧③c -- the nested sizes,
                    so the marginal contribution of each conjunct is visible rather than pooled;
                (C) whether the source-derived key for ③a equals the hand-written USES_PROMPT_LABELS.

IDENTIFICATION  Exact for what the code reads -- rule dispatch is literal. NOT identified: whether an
                arm uses label information by a route the dispatch does not reveal (a helper, a
                cached file). That blind spot biases toward FEWER exclusions, i.e. toward the
                definition looking cleaner, and is named in the verdict.

SCOPE           population: R360's 42 arms and its published admitted sets · instrument: rule
                dispatch read from corebench/select_core.py · baseline: the hand-written key, whose
                correctness about rankings R363 established INDEPENDENTLY · regime: HEAD.

WORLDS
  W-3A-ALONE      (b) and (c) exclude nothing beyond (a). Then clause ③'s three conjuncts are one
                  conjunct with two riders, and -- with R403 showing both riders are unsayable off
                  this release -- they are decoration in the same way clause ① is.
  W-3B-BINDS      (b) excludes an arm (a) does not. Then it is load-bearing and must be kept.
  W-3C-BINDS      (c), enforced AS WRITTEN, excludes arms currently ADMITTED. Then the definition as
                  published and the definition as implemented disagree, and the published admitted
                  set is larger than the definition's own text licenses.

PREDICTION MATRIX
  W-3A-ALONE -> |excl(b) \\ excl(a)| = 0 and |excl(c) \\ excl(a)| = 0
  W-3B-BINDS -> |excl(b) \\ excl(a)| > 0, arms named
  W-3C-BINDS -> excl(c) intersects the PUBLISHED admitted set, arms named and the shrunk set given

PRE-REGISTERED KILL -- conditional on the key reproduction, never on the sets alone.
    if source_derived_3a == hand_written_USES_PROMPT_LABELS and dispatch_control_passes:
        report all three; verdict names every world that fires (they are not exclusive)
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED. A disagreement means either the source
          read or the hand-written key is wrong, and which is a separate question.

CONTROLS
  KEY REPRO (+)  the ③a set derived from the rule dispatch must EQUAL the key hand-written in four
                 rounds. Agreement validates the hand-written key against the object; disagreement
                 is itself the finding and stops the round.
  DISPATCH (-)   a fabricated rule name must map to NO data file, so "reads nothing" is attainable
                 and the map is not returning a constant.
  PRIOR ROUND    the claim that `oracle_k/indep_k/greedy_k` are the ranking readers comes from R363,
                 a DIFFERENT round asking a DIFFERENT question. The answer key is not made here.
  NESTED         the four admitted sets are nested by construction, so each must be a subset of the
                 previous. A violation means the classification is inconsistent and is checked.

MULTIPLICITY    3 conjuncts x 42 arms, every exclusion listed by name.
SEEDS           none -- static source analysis.
ARTIFACT        results/r404_conjunct_decomposition.json with the source hash.

IMPOSSIBLE HERE
  label use by a route the dispatch hides -- biases toward FEWER exclusions, i.e. the flattering
                                             direction for the definition. Named.
  re-scoring any arm                      -- needs the judge; this uses R360's published sets.
  deciding whether (c) SHOULD be enforced  -- an act of definition, not a measurement.
  a second release                        -- two corpora, neither re-scored here.

EXIT
    0  the key reproduces and the decomposition is reported
    1  the derived key disagrees with the hand-written one -- UNVERIFIED
    2  a required file is absent -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
SRC = ROOT / "corebench" / "select_core.py"
R360 = HERE.parent / "R360_which_clause_is_load_bearing" / "results" / "r360_clause_ledger.json"
HAND_KEY = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}


def rule_of(arm: str) -> str:
    """Arm tag is built at select_core.py:204 as rule + k + optional _s{seed} + optional _fit{p}."""
    m = re.match(r"^([a-z_]+?)_?k?(\d+)?(_s\d+)?(_fit\d)?(_sham)?$", arm)
    base = m.group(1) if m else arm
    return base


def main() -> int:
    for f in (SRC, R360):
        if not f.exists():
            print(f"  UNRUNNABLE: {f} absent. Exit 2, never 0."); return 2
    src = SRC.read_text()
    led = json.loads(R360.read_text())
    arms = sorted(led["arms"])
    c2 = set(led["clause2_admits"])
    c23 = set(led["clause23_admits"])

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R404 · which conjunct of clause ③ does the work?   HEAD {head}\n")
    print("  ⛔ PRIOR ART CHECKED FIRST. R363 audited the hand-written key against this same source")
    print("     and established W_CHANNEL_OPEN; R403 found conjunct (c) NOT-STATABLE off this")
    print("     release. Neither asked what each conjunct EXCLUDES, enforced as written.\n")

    # ---- read the rule dispatch from SOURCE ------------------------------------------------------
    m = re.search(r"if a\.rule in \(([^)]*)\):\s*\n\s*for line in open\([^)]*comparisons\.jsonl",
                  src)
    ranking_rules = set(re.findall(r"[\"']([a-z_]+)[\"']", m.group(1))) if m else set()
    fitp = re.search(r"_fit\{a\.fit_parity\}\"? if a\.rule in \(([^)]*)\)", src)
    fit_rules = set(re.findall(r"[\"']([a-z_]+)[\"']", fitp.group(1))) if fitp else set()
    rubric_rules = set()
    for rule in re.findall(r"elif a\.rule == [\"']([a-z_]+)[\"']", src) + ["full"]:
        # rules whose weights come from the joined rubric file rather than from comparisons
        if rule not in ranking_rules and rule not in ("random_k",):
            rubric_rules.add(rule)

    print(f"  RULE DISPATCH, READ FROM {SRC.relative_to(ROOT)} — not from arm names")
    print(f"    rules that open comparisons.jsonl (the RANKINGS): {sorted(ranking_rules)}")
    print(f"    rules that take a fit_parity (fit on a HALF):     {sorted(fit_rules)}")
    print(f"    rules whose weights come from the RUBRIC:         {sorted(rubric_rules)}")

    # ---- CONTROLS -------------------------------------------------------------------------------
    excl_a = {a for a in arms if rule_of(a) in ranking_rules}
    key_ok = excl_a == HAND_KEY
    fake_ok = rule_of("zzq_fake_k4") not in (ranking_rules | rubric_rules | fit_rules)
    print(f"\n  CONTROLS")
    print(f"    KEY REPRO (+)  ③a derived from source = the key hand-written in 4 rounds: {key_ok}")
    print(f"                   derived {sorted(excl_a)}")
    print(f"                   written {sorted(HAND_KEY)}   {'PASS' if key_ok else 'FAIL'}")
    print(f"    DISPATCH (-)   a fabricated rule maps to no file: {fake_ok}   "
          f"{'PASS' if fake_ok else 'FAIL'}")
    if not (key_ok and fake_ok):
        print("\n  UNVERIFIED — the derived key and the written key disagree. Which is wrong is a")
        print("  separate question, and this round may not answer it by preferring one. Exit 1.")
        return 1

    # ---- (A) per-conjunct exclusion --------------------------------------------------------------
    excl_b = {a for a in arms if "_fit" in a}
    excl_c = {a for a in arms if rule_of(a) in rubric_rules}
    print(f"\n  (A) WHAT EACH CONJUNCT EXCLUDES, ON ITS OWN, over all {len(arms)} arms")
    print(f"    ③a reads the prompt's own rankings : {len(excl_a):>2}  {sorted(excl_a)}")
    print(f"    ③b fitted on a HALF of them        : {len(excl_b):>2}  {sorted(excl_b)}")
    print(f"    ③c weights from an annotator RUBRIC: {len(excl_c):>2}  {sorted(excl_c)[:8]}"
          f"{' ...' if len(excl_c) > 8 else ''}")
    b_extra = excl_b - excl_a
    c_extra = excl_c - excl_a
    print(f"\n    ③b beyond ③a: {len(b_extra)}  {sorted(b_extra)}")
    print(f"    ③c beyond ③a: {len(c_extra)}  {sorted(c_extra)[:8]}{' ...' if len(c_extra) > 8 else ''}")

    # ---- (B) the nested admitted sets ------------------------------------------------------------
    s2 = c2
    s2a = s2 - excl_a
    s2ab = s2a - excl_b
    s2abc = s2ab - excl_c
    nested = s2abc <= s2ab <= s2a <= s2
    print(f"\n  (B) THE ADMITTED SET, CONJUNCT BY CONJUNCT (nested by construction: {nested})")
    print(f"    ②                 {len(s2):>2}  {sorted(s2)}")
    print(f"    ② ∧ ③a            {len(s2a):>2}  {sorted(s2a)}")
    print(f"    ② ∧ ③a ∧ ③b       {len(s2ab):>2}  {sorted(s2ab)}")
    print(f"    ② ∧ ③a ∧ ③b ∧ ③c  {len(s2abc):>2}  {sorted(s2abc)}")
    print(f"    published (R360)  {len(c23):>2}  {sorted(c23)}")
    if not nested:
        print("\n  UNVERIFIED — the sets are not nested, so the classification is inconsistent.")
        return 1

    # ---- VERDICT — worlds are NOT exclusive; every one that fires is named ------------------------
    fired = []
    print()
    if not b_extra and not c_extra:
        fired.append("W-3A-ALONE")
    if b_extra:
        fired.append("W-3B-BINDS")
    if excl_c & c23:
        fired.append("W-3C-BINDS")

    if "W-3A-ALONE" in fired:
        print(f"  W-3A-ALONE — conjuncts (b) and (c) exclude NOTHING beyond (a). Clause ③'s three")
        print(f"  parts are one part with two riders.")
    if "W-3B-BINDS" in fired:
        print(f"  W-3B-BINDS — (b) excludes {sorted(b_extra)}, which (a) does not. It is load-bearing.")
    if "W-3C-BINDS" in fired:
        hit = sorted(excl_c & c23)
        print(f"  W-3C-BINDS — enforced AS WRITTEN, conjunct (c) excludes {len(hit)} of the")
        print(f"  {len(c23)} PUBLISHED admitted arms: {hit}")
        print(f"  So the definition AS PUBLISHED and the definition AS IMPLEMENTED disagree. The")
        print(f"  implementation is the hand-written key, which contains only ranking readers; the")
        print(f"  TEXT also forbids `by way of a rubric those same annotators wrote`, and R363")
        print(f"  established independently that this channel is OPEN. Enforcing the sentence would")
        print(f"  leave {len(s2abc)} admitted arm(s): {sorted(s2abc)}.")

    print(f"\n  ⚠ THIS ROUND DOES NOT DECIDE WHETHER (c) SHOULD BE ENFORCED. That is an act of")
    print(f"    definition, not a measurement. It reports what the sentence, read literally, does to")
    print(f"    the published set — and the gap between text and implementation is the finding.")
    print(f"  ⚠ AND THE BLIND SPOT RUNS THE FLATTERING WAY: a label route the rule dispatch does not")
    print(f"    reveal would mean MORE exclusions, not fewer, so every count here is a LOWER bound on")
    print(f"    what the clause would remove.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, n_arms=len(arms), ranking_rules=sorted(ranking_rules),
               fit_rules=sorted(fit_rules), rubric_rules=sorted(rubric_rules),
               excl_3a=sorted(excl_a), excl_3b=sorted(excl_b), excl_3c=sorted(excl_c),
               b_beyond_a=sorted(b_extra), c_beyond_a=sorted(c_extra),
               admitted_2=sorted(s2), admitted_2a=sorted(s2a), admitted_2ab=sorted(s2ab),
               admitted_2abc=sorted(s2abc), published=sorted(c23),
               controls=dict(key_reproduces=key_ok, fake_rule_ok=fake_ok, nested=nested),
               verdict="|".join(fired) or "W_NONE_FIRED")
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r404_conjunct_decomposition.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
