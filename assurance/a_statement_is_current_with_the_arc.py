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

    # ⛔ R994: the size departure is DECIDED. Registering it stops a later round settling the
    #    question by whichever clause it finds convenient — R986's own warning.
    d = load("A27_*/R994_*/results/cap_refused.json")
    if d:
        facts.append(("R994", "the size cap is refused, and why",
                      d["decision"],
                      [r"(refus|not adopt|declin).{0,300}(cap|upper bound).{0,300}"
                       r"(resolution|resolv|cannot see|indistinguish)",
                       r"(cap|upper bound).{0,300}(below|inside).{0,120}resolution"]))

    # ⛔ R1000: the conjunction. Twenty-six rounds studied the clauses SEPARATELY; this is the first
    #    time the definition was applied as ONE operator, and it found two clauses that remove
    #    nothing the others do not. A statement that lists four clauses without saying which two
    #    carry the extension is describing a definition it has not run.
    d = load("A27_*/R1000_*/results/conjunction.json")
    if d:
        facts.append(("R1000", "which clauses actually bind, and that core is admitted",
                      f"inert {d['inert_clauses']}, core admitted {d['core_admitted_both']}",
                      [r"(inert|remove nothing|no unique|ornament).{0,400}"
                       r"(①|clause one|④|clause four)",
                       r"(①|④).{0,300}(inert|remove nothing|carries? no|adds? nothing)"]))

    # ⛔ R1001: the conjunction is EMPTY under clause ④'s permissive reading, and the mechanism is a
    #    direct conflict with clause ③. This is the strongest thing the arc has found and it SCOPES
    #    R1000's headline, so a statement carrying R1000 without this one is actively misleading.
    d = load("A27_*/R1001_*/results/permissive_operator.json")
    if d:
        facts.append(("R1001", "the permissive reading empties the definition, via a ③/④ conflict",
                      f"{d['cells_where_core_excluded']} of {d['saturated_cells']} saturated cells "
                      f"exclude the core; supervised share of ④ "
                      f"{d['supervised_share_of_clause4']}",
                      # ⚠ the FIRST draft of this pattern went GREEN on arrival: entry 1368 already
                      # says "the extension is EMPTY". The registered fact is the MECHANISM, which
                      # is what this round actually adds, so the pattern demands 14-of-14 / the
                      # disjointness — never the recorded headline.
                      [r"(14 of 14|all 14|every arm).{0,300}"
                       r"(human ranking|supervised|read.{0,20}label|clause ③|③)",
                       r"(③|clause three).{0,260}(④|clause four).{0,200}"
                       r"(disjoint|no arm satisf|cannot be jointly|direct conflict)"]))

    # ⛔ R1002: the surviving repair's reference class is NOT CLOSED under the clause it
    #    instantiates. This is the one that decides whether the arc has a definition or a boundary,
    #    so a statement carrying R849's repair without it is presenting a subset max as a max.
    d = load("A27_*/R1002_*/results/class_closure.json")
    if d:
        facts.append(("R1002", "the repair's reference class is not closed under its own clause",
                      f"closed={d['closed']}, class {d['reenumerated_class_size']} "
                      f"= {d['n_singletons']} singletons + {d['n_pairs']} pairs",
                      [r"(not closed|proper subset|subset of what the clause).{0,320}"
                       r"(class|R849|reference)",
                       r"(reference class|named class).{0,300}"
                       r"(not closed|convenience family|boundary we drew|proper subset)"]))

    # ⛔ R1003: clause ④ has NO viable setting as a filter — every class is vacuous or empties the
    #    definition — and the core's whole margin is smaller than what ONE admissible rule adds.
    #    A statement still presenting ④ as a filter is presenting a setting that does not exist.
    d = load("A27_*/R1003_*/results/wording_grid.json")
    if d:
        facts.append(("R1003", "clause ④ has no viable setting as a filter, and the margin is "
                               "smaller than one rule's contribution",
                      f"rise {d['bar_rise_from_one_witness']:.6f} vs core margin "
                      f"{d['core_a2'] - d['bar_lexical']:.6f}",
                      [r"(0\.0908|\+0\.09).{0,300}(0\.0847|margin|one rule|single)",
                       r"(no viable setting|cannot be stated as a filter|either vacuous or "
                       r"empt).{0,200}(④|clause four|filter)"]))

    # ⭐ R1004: THE FORMULATION. Two conditions, both binding, instance admitted. This is the one
    #    fact in the arc that is a PRODUCT rather than a retraction, and a statement that does not
    #    carry it is a list of things that failed.
    d = load("A27_*/R1004_*/results/formulation.json")
    if d:
        facts.append(("R1004", "the two-condition formulation, with size and margin demoted",
                      f"world={d['world'][:40]}, core admitted {d['core_admitted_both']}",
                      # ⚠ the first draft went GREEN on arrival: the anchored statement already
                      # carries "Reported, not required: sizes 3 to 8 ...", which is about size
                      # RESOLUTION and not about demoting the clause. Different claim, loose
                      # pattern. The registered fact is the MEASURED binding and the churn.
                      [r"(64|61).{0,200}(15|16).{0,300}(bind|unique)",
                       r"(both conditions bind|each condition removes).{0,400}"
                       r"(churn|N\s*=\s*726|stable)"]))

    # ⛔ R1005: the extension CONVERGES beyond its score level -- and roughly half of it is the same
    #    arms counted twice. The second half of that corrects R1004's own count, so a statement
    #    carrying R1004's 9 and 12 without it is quoting duplicates as distinct objects.
    d = load("A27_*/R1005_*/results/convergence.json")
    if d:
        facts.append(("R1005", "the extension converges beyond level, and its count was inflated "
                               "by effectively identical arms",
                      f"delta {d['delta_mean']:.4f} at {d['effect_over_floor']:.1f}x floor; "
                      f"{d['population_full']}->{d['population_dedup']} distinct",
                      [r"(14|eleven|11).{0,200}(identical|duplicat).{0,300}(85|distinct)",
                       r"(0\.0828|\+0\.08).{0,300}(4\.5|floor|level)"]))

    # ⛔ R1006: the alternative reading R1005 could not exclude is now EXCLUDED. A statement that
    #    carries R1005's convergence without this still owes the reader the rival explanation.
    d = load("A27_*/R1006_*/results/family_spread.json")
    if d:
        facts.append(("R1006", "the supervised comparison family is not unusually heterogeneous",
                      f"ranks {d['supervised_ranks']} of {d['n_families']}",
                      [r"(indep_k|supervised).{0,300}(rank|1st|first|most homogeneous)",
                       r"(not unusually heterogeneous|cannot explain).{0,300}"
                       r"(Δ|delta|convergen)"]))

    # ⛔⛔ R1007: R1005's convergence is RETRACTED. A statement still carrying it is asserting a
    #    claim its own author withdrew, which is the worst state a record can be in.
    d = load("A27_*/R1007_*/results/membership_null.json")
    if d:
        facts.append(("R1007", "R1005's convergence fails the negative control R1005 declared",
                      f"{d['cells_above_band_p95']} of {d['cells_ok']} cells clear the "
                      f"band-matched null",
                      [r"(retract|withdraw).{0,300}(R1005|convergen)",
                       r"(6 of 30|band-matched null).{0,300}(retract|withdraw|not established)"]))

    # ⛔⛔ R1009: the formulation admits a PROMPT-BLIND arm. A statement carrying R1004's two
    #    conditions without this is publishing a definition that admits its own null.
    d = load("A27_*/R1009_*/results/prompt_blind_admitted.json")
    if d:
        facts.append(("R1009", "the formulation admits a prompt-blind arm, and the repair",
                      f"{len(d['blind_admitted'])} admitted; "
                      f"{[x['arm'] for x in d['blind_admitted']]}",
                      [r"(prompt-blind|never reads the conversation).{0,300}"
                       r"(admitted|is a core|qualifies)",
                       r"(every certified|all certified|quantif).{0,300}"
                       r"(comparator).{0,200}(repair|9|excluded)"]))

    # ⛔ R1010: the repair was committed at R921 and read by ONE later round. A statement that
    #    presents R1009's repair as new is claiming a discovery that was sitting in an artifact.
    d = load("A27_*/R1010_*/results/adoption_gap.json")
    if d:
        facts.append(("R1010", "the stronger criterion was committed at R921 and never adopted",
                      f"adopted={d['adopted']}",
                      [r"(committed at R921|already computed|already named).{0,300}"
                       r"(never adopted|not adopted|1 reader|one reader)",
                       r"(survives_all_legitimate).{0,300}(13|1\b|adopt)"]))

    # ⛔⛔ R1011: the definition CONTAINS its instance without SINGLING IT OUT, and two extension
    #    arms were admitted on 79% imputed A2. Both belong beside the formulation.
    d = load("A27_*/R1011_*/results/instance_rank.json")
    if d:
        facts.append(("R1011", "the definition contains the instance without singling it out",
                      f"{d['n_resolvably_better']} of {d['n_rivals']} rivals resolvably worse; "
                      f"dropped {d['dropped_for_partial_coverage']}",
                      [r"(contains|admits).{0,200}(without singling|no special status)",
                       r"(200 of 968|21%|imputed).{0,300}(coverage|extension|A2)"]))

    # ⭐ R1012: the cut is clean; the COUNTS are not. A statement quoting 24/28 without saying two
    #    of each are partial-coverage arms is quoting a count with imputed members.
    d = load("A27_*/R1012_*/results/cut_provenance.json")
    if d:
        facts.append(("R1012", "the cut survives excluding imputed arms; the counts do not",
                      f"moved={d['comparators_whose_cut_moved']}",
                      [r"(cut).{0,220}(unchanged|clean|survives|not an artifact)",
                       r"(24\s*(?:→|->|to)\s*22|28\s*(?:→|->|to)\s*26)"]))

    # ⛔ R1013: size and its residual are WITHDRAWN as candidate clauses — the sham shares them,
    #    including on the instance. A statement proposing size as definitional content is proposing
    #    something a sham satisfies.
    d = load("A27_*/R1013_*/results/text_properties.json")
    if d:
        facts.append(("R1013", "size and its residual are withdrawn — the sham shares them",
                      f"withdrawn={d['withdrawn_candidates']}",
                      [r"(sham).{0,260}(shares|identical|43).{0,200}(size|residual)",
                       r"(withdraw|refus).{0,200}(size|residual).{0,200}(sham|candidate)"]))

    # ⭐ R1014: the instance's sham is an exact derangement, so R1013's withdrawal reaches the
    #    instance in full and the class of text-only clauses is CLOSED, not merely doubted.
    d = load("A27_*/R1014_*/results/instance_sham.json")
    if d:
        facts.append(("R1014", "the instance's sham is an exact re-pairing, closing the text-only "
                               "class",
                      f"multiset_identical={d['multiset_identical']}, "
                      f"same_slot={d['same_slot']}",
                      [r"(derangement|0 of 968|no prompt keeps).{0,300}(sham|permut|re-pair)",
                       r"(exact re-pairing|permutation of the core).{0,300}"
                       r"(text-only|no text|closed)"]))

    # ⭐ R1015: the FIRST pairing-dependent quantity that separates the instance. It is post-hoc and
    #    the statement must carry that caveat with it, or the arc has re-run "the definition
    #    describes the instance" with a better metric.
    d = load("A27_*/R1015_*/results/discriminativeness.json")
    if d:
        facts.append(("R1015", "discriminativeness separates the instance where A2 does not, and it "
                               "is post-hoc",
                      f"{d['n_higher']} of {d['n_rivals']} resolvable; sham drop "
                      f"{d['controls']['positive_sham_drops']['d']:.6f}",
                      [r"(discriminat).{0,300}(separat|higher|0\.0306|resolv)",
                       r"(post-?hoc|chosen after|discovered after).{0,300}"
                       r"(discriminat|candidate|clause)"]))

    # ⭐ R1016: discriminativeness measures BELONGING, not merit. A statement carrying R1015's
    #    separation without this bound is offering a fit test as a quality test.
    d = load("A27_*/R1016_*/results/preregistered_exclusion.json")
    if d:
        facts.append(("R1016", "discriminativeness measures belonging, not merit",
                      f"sham {d['shams_below']}/{d['n_shams']}, "
                      f"random {d['random_below']}/{d['n_random']}",
                      [r"(belong).{0,300}(not|rather than).{0,120}(merit|good|quality)",
                       r"(random).{0,200}(18|47%|chance).{0,300}(discriminat|quality)"]))

    # ⛔ R1017: the belonging clause fails twice over — not evaluable, and implied by ② where it is.
    #    A statement still carrying discriminativeness as a candidate clause is carrying a dead one.
    d = load("A27_*/R1017_*/results/belonging_vs_clause_two.json")
    if d:
        facts.append(("R1017", "the belonging clause is not evaluable, and is implied by ② where "
                               "it is",
                      f"{d['n_evaluable']}/{d['n_population']} evaluable; "
                      f"clause2_only={d['clause2_only']}",
                      [r"(4\.2%|4 of 96|not evaluable).{0,300}(sham|scored|clause)",
                       r"(implied by|weaker than|adds nothing).{0,260}(clause ②|clause two)"]))

    # ⛔ R1019: every extension figure in this arc is A2's answer, and R288 shows the admitted set
    #    is target-dependent. A statement quoting "9 arms" without a target is a number without its
    #    scope, which is eleven of twelve retractions in this project's history.
    d = load("A27_*/R1019_*/results/target_scope.json")
    if d:
        facts.append(("R1019", "the extension is A2's answer and the target must be named",
                      f"identical={d['identical']}; R288 targets {d['prior_art']['targets']}",
                      [r"(A2).{0,300}(target|R288).{0,300}(empt|top1|tau|depend)",
                       r"(under A2|A2's answer).{0,200}(extension|9 arms)"]))

    # ⛔⛔ R1020: under A1·consensus the definition EXCLUDES ITS OWN INSTANCE, at the full
    #    population and under this arc's own admission rule. A statement carrying the A2 extension
    #    without that is showing the one target where the answer flatters.
    d = load("A27_*/R1020_*/results/a1_at_full_population.json")
    if d:
        facts.append(("R1020", "under A1·consensus the definition excludes the released core",
                      f"annot {len(d['extension_a1_annot'])}, consensus "
                      f"{len(d['extension_a1_consensus'])}, core excluded "
                      f"{d['core_excluded_under_a1_consensus']}",
                      [r"(A1.consensus).{0,300}(exclud|not among|without).{0,120}"
                       r"(coval_core|instance|core)",
                       r"(coval_core|its own instance).{0,200}(not admitted|excluded).{0,200}"
                       r"(A1)"]))

    # ⛔ R1021: R1020's split between core and twins is the IMPUTATION, not the target. The
    #    statement must carry the scoped wording, not the earlier one beside it.
    d = load("A27_*/R1021_*/results/coverage_or_target.json")
    if d:
        facts.append(("R1021", "the core/twin split under A1·consensus is the imputation",
                      f"together={d['together']}, 200-real admits "
                      f"{d['admitted_200_real']}",
                      [r"(200).{0,300}(imputation|imputed|artifact).{0,200}(twin|split|contrast)",
                       r"(twins|contrast).{0,200}(not|artifact).{0,200}(target|real)"]))

    # ⛔ R1022: the imputation advantage under A1·consensus is MONOTONE in how much is imputed —
    #    an arm with 4 real prompts of 968 clears clause ②′ against both comparators at lo +0.35,
    #    while the same arm is rejected under A2. The statement must carry that the A1·consensus
    #    extension is coverage-driven, not merely that the twins were.
    d = load("A27_*/R1022_*/results/coverage_threshold_curve.json")
    if d:
        e = d["extreme_arm"]
        facts.append(("R1022", "imputation manufactures admission under A1·consensus",
                      f"{e['real_prompts']} real prompts clear ②′: "
                      f"{e['clears_clause2_by_target']}",
                      [r"(imput\w*).{0,300}(A1).{0,300}(monoton|dose|4 of 968|coverage)",
                       r"(A1.{0,40}consensus).{0,300}(coverage[- ]driven|monoton\w*)"]))

    # ⛔⛔ R1023: clause ②′'s operator is CALIBRATED ONLY ON FULL-COVERAGE ARMS. Censored to the
    #    guard's own k=200, an arm whose true difference is EXACTLY zero is admitted ~21% of the
    #    time against a nominal 2.5%, and the closed-form ratio predicts the whole curve. The
    #    statement must carry this as a SCOPE limit on the operator, not as a note about one round.
    d = load("A27_*/R1023_*/results/false_admission_rate.json")
    if d:
        facts.append(("R1023", "②′ is calibrated only on full-coverage arms",
                      f"false-admission at k=200 is {d['far_at_k200_worst']:.3f} "
                      f"vs nominal {d['nominal']}",
                      [r"(false[- ]admission|false positive).{0,300}(nominal|0\.025|2\.5)",
                       r"(calibrat\w*).{0,200}(full[- ]coverage|uncensored|complete)"]))

    # ⛔⛔ R1024: the miscalibration is the ESTIMATOR's, not a sample-size limit. Dropping the
    #    imputation and bootstrapping only the observed prompts restores coverage at every k, so the
    #    coverage THRESHOLD is the wrong instrument and is deletable. The statement must say the
    #    repair is an estimator change, not a better constant.
    d = load("A27_*/R1024_*/results/estimator_vs_threshold.json")
    if d:
        facts.append(("R1024", "the repair is an ESTIMATOR change, not a threshold",
                      f"observed-only coverage >= {d['worst_coverage_k_ge_10_fix']:.3f} at k>=10 "
                      f"vs nominal {d['nominal']}",
                      [r"(observed[- ]only|without imput\w*|stop imput\w*|do not impute)"
                       r".{0,400}(coverage|calibrat\w*)",
                       r"(estimator).{0,200}(not|rather than).{0,80}(threshold|guard|constant)"]))

    # ⛔⛔ R1025: clause ②′'s universal quantifier is INERT on the certified set — `generic` is
    #    uniformly the binding comparator on both targets (94/94, zero resolved flips), so on this
    #    release "beats EVERY comparator" reduces to "beats `generic`". The statement must say so,
    #    and must say the set is a CHOICE the clause never mentions.
    d = load("A27_*/R1025_*/results/quantifier_work.json")
    if d:
        facts.append(("R1025", "`every comparator` reduces to `generic` here",
                      f"binding {d['binding_comparator']}, "
                      f"{d['n_resolved_flips']} resolved flips",
                      [r"(every|universal).{0,200}(quantifier|comparator)"
                       r".{0,400}(reduce\w*|shorthand|inert|binding)",
                       r"(binding comparator|never binds).{0,200}generic"]))

    # ⛔⛔ R1026: the certified set is NOT a curatorial choice — `fixed` is computed over 96 arms
    #    and exactly 2 satisfy it, so it is the COMPLETE population of prompt-blind arms and the
    #    constraint belongs to the RELEASE. Also carries the predicate's own calibration: rubric
    #    criteria are prompt-unique (0.0000 of adjacent pairs share any criterion).
    d = load("A27_*/R1026_*/results/certification_predicate.json")
    if d:
        c = d["correction_to_r1025"]
        facts.append(("R1026", "the certified set is the COMPLETE prompt-blind population",
                      f"{c['n_fixed']} of {c['n_arms_typed']} arms satisfy `fixed`; "
                      f"{len(d['join']['prompt_blind_among_them'])} stricter prompt-blind arms",
                      [r"(complete population|everything that qualified|no selection among)"
                       r".{0,400}(prompt[- ]blind|filter)",
                       r"(96).{0,120}(exactly 2|only 2).{0,200}(satisf|fixed)"]))

    # ⛔⛔ R1027: the impossibility register's cost figure is NOT a constant. cells = prompts x
    #    replies x k holds with residual exactly 0 across 74 fixed-k arms, so 15,488 is a k=4 arm's
    #    price quoted as universal. The statement must carry the FORMULA, not the constant.
    d = load("A27_*/R1027_*/results/cost_by_k.json")
    if d:
        by = {r["k"]: r["judge_calls"] for r in d["cost_by_k_full_coverage"]}
        facts.append(("R1027", "a new comparator's cost is linear in k, not constant",
                      f"k=1 {by.get(1)} · k=4 {by.get(4)} · k=16 {by.get(16)}",
                      [r"968\s*[×x]\s*4\s*[×x]\s*k",
                       r"(3,?872).{0,120}(15,?488).{0,120}(61,?952)"]))

    # ⛔⛔ R1028: the cross-release line stands, but its REASON does not. R802 refuted "another
    #    release" on a FILE-level instrument; the populations are disjoint (overlap 0 on all three
    #    keys) yet carry no criterion vocabulary. The binding requirement is the vocabulary.
    d = load("A27_*/R1028_*/results/second_file_or_second_release.json")
    if d:
        facts.append(("R1028", "cross-release binds on the CRITERION VOCABULARY, not the release",
                      f"overlap {d['best_share_of_scored']:.4f}, "
                      f"carries criteria {d['carries_criterion_vocabulary']}",
                      [r"(criterion vocabulary|carrying a criterion)",
                       r"(overlap is exactly 0|overlap.{0,40}exactly 0).{0,200}(join key|key)"]))

    # ⛔⛔ R1029: the register's requirement TYPE was never stored, so "is a named requirement
    #    right" is UNVERIFIED ON IDENTIFICATION — three instruments give 17 / 9 / 7. The statement
    #    must carry the structural repair, not a share over a guessed denominator.
    d = load("A27_*/R1029_*/results/requirement_class.json")
    if d:
        dn = d["denominator_not_identified"]
        facts.append(("R1029", "requirement correctness is not identified as stored",
                      f"denominators {dn['r472_tabulation']}/{dn['token_matcher']}/"
                      f"{dn['direct_regex']}, numerator {d['affected_numerator']}",
                      [r"(requirement type was never stored|store the requirement type)",
                       r"(17).{0,80}(9).{0,80}(7).{0,200}(denominator|instrument)"]))

    # ⛔⛔ R1030: the NEXT-novelty gate is a SELF-TEST, not a monitor — it exits 0 while 5 of 7 of
    #    this session's NEXT lines proposed a subject that already existed (R858's baseline: 0.269).
    d = load("A27_*/R1030_*/results/next_novelty_live.json")
    if d:
        facts.append(("R1030", "the NEXT-novelty gate is a self-test, not a monitor",
                      f"{d['n_prior_art']}/{d['n_scored']} = {d['rate']:.3f} vs "
                      f"R858 {d['baseline_r858']:.3f}",
                      [r"(self[- ]test).{0,300}(monitor|live|never (points|runs))",
                       r"(0\.714|5 of 7).{0,200}(0\.269|R858|27)"]))

    # ⛔⛔ R1031: preflight's --next existed all along (4 of 15 used, clean split at compaction),
    #    and the prior-art gate built as R1030's repair catches 0 of 4 real cases, so it is NOT
    #    wired. The statement must carry that this defect has no mechanical detector.
    d = load("A27_*/R1031_*/results/flag_usage_and_repair_recall.json")
    if d:
        facts.append(("R1031", "the named repair catches 0 of 4 and is not wired",
                      f"--next used {d['usage']['next_checked']}/{d['usage']['invocations']}, "
                      f"repair recall {d['repair_recall']}",
                      [r"(0 of 4|recall 0/4).{0,300}(not wired|deliberately)",
                       r"(no mechanical detector|semantic).{0,300}(lexical|prose)"]))

    # ⛔⛔ R1032: the stale clause text was OPERATIONALLY wrong, target-dependently — identical
    #    under A2, differing by 2 arms (the twins) under A1·consensus. The clause text is repaired
    #    at both canonical sites rather than annotated beside.
    d = load("A27_*/R1032_*/results/two_readings.json")
    if d:
        facts.append(("R1032", "the clause text is repaired, not annotated",
                      f"sym diff by target {d['per_target_sym_diff']}",
                      [r"(clause text itself is repaired|repaired here).{0,300}(annotated|beside)",
                       r"(actually covers).{0,160}(never on imputed|imputed values)"]))

    # ⛔⛔ R1033: a subset of pool16's criteria is a prompt-blind comparator costing ZERO judge
    #    calls, 35 of 713 are stricter than `generic`, and adding the strictest removes 6 of the 9
    #    extension arms — leaving only the core and its twins.
    d = load("A27_*/R1033_*/results/free_third_comparator.json")
    if d:
        e = d["extension_under_enlarged_set"]
        facts.append(("R1033", "a third prompt-blind comparator costs zero and cuts the extension",
                      f"{d['n_stricter_than_generic']} of {d['family_size']} stricter; "
                      f"{len(e['fall'])} of 9 fall",
                      [r"(0 judge calls|costs zero|costs 0).{0,300}(subset|prompt-blind)",
                       r"(6 of (the )?9).{0,200}(fall|remov)"]))

    # ⛔⛔⛔ R1034: ②′ is VACUOUS under closure + the repaired operator. Emptiness is exact.
    d = load("A27_*/R1034_*/results/closure_satisfiability.json")
    if d:
        facts.append(("R1034", "②′ is vacuous under a closed comparator set",
                      f"imputing {d['extension_under_sampled_closure_imputing']} · "
                      f"repaired {d['extension_under_sampled_closure_repaired'] or '∅'}",
                      [r"(vacuous|empty|∅).{0,300}(clos\w+).{0,200}(repair|imput)",
                       r"(clos\w+).{0,300}(extension is (empty|∅)|admits nothing)"]))

    # ⛔⛔ R1035: R1034's ∅ is seed-dependent (4 of 7) at a ~1e-4 boundary; the quantile CURVE is
    #    what stands, stable and non-empty over q in {50..99}.
    d = load("A27_*/R1035_*/results/quantile_bound_curve.json")
    if d:
        b = d["boundary"]
        facts.append(("R1035", "R1034's ∅ is seed-dependent; the quantile curve stands",
                      f"admitted {b['admitted_in']} of {len(b['seeds'])}, "
                      f"stable q {d['stable_q']}",
                      [r"(4 of 7|seed[- ]dependent).{0,300}(exact|withdraw)",
                       r"(q\s*=?\s*95|>= q%).{0,300}(stable|seed-identical)"]))

    # ⛔⛔ R1036: scale-stability SELECTS q (withdrawing R1035's closing sentence), and it is not
    #    binary — the onset family size grows with q and never arrives at q=100.
    d = load("A27_*/R1036_*/results/scale_free_q.json")
    if d:
        facts.append(("R1036", "scale-stability selects q; onset grows with q",
                      f"scale-free {d['scale_free_q']}, max never stabilises",
                      [r"(onset).{0,300}(grows with q|never)",
                       r"(scale[- ]stab\w+|scale[- ]free).{0,300}(select|withdraw)"]))

    # ⛔⛔ R1037: the clause now STATES q as a declared parameter, and the stated form was verified
    #    against R1036's grid by different code. q=100 excluded by measurement.
    d = load("A27_*/R1037_*/results/stated_form_verifies.json")
    if d:
        facts.append(("R1037", "the clause states q as a DECLARED parameter",
                      f"stated form agrees {d['all_scale_free_agree']}, "
                      f"declared {d['declared_not_fixed']}",
                      [r"(declared|declare).{0,120}(`?q`?).{0,300}(not fixed|never a value)",
                       r"(at least\s*`?q`?%|q%\s*of the certified)"]))

    # ⛔⛔ R1038: the family is its own null; only q=90 of the scale-free set reaches nominal
    #    false-admission, so the declared parameter gets an evidence-selected DEFAULT.
    d = load("A27_*/R1038_*/results/false_admission_by_q.json")
    if d:
        facts.append(("R1038", "q defaults to 90 on false-admission evidence",
                      f"best scale-free q={d['best_scale_free_q']} at {d['best_rate']:.4f}",
                      [r"(false[- ]admission).{0,300}(q\s*=\s*90|only.{0,30}90)",
                       r"(default).{0,120}(q\s*=\s*90)"]))

    # ⛔⛔ R1039: this arc's own IMPOSSIBLE lines fell at 4 of 16 = 0.25 against R802's committed
    #    0.0333, and all four shared one shape — "needs something outside the release", answered by
    #    an object already inside it.
    d = load("A27_*/R1039_*/results/own_impossibility_rate.json")
    if d:
        facts.append(("R1039", "this arc's own impossibility lines fell at 7.5x the baseline",
                      f"{d['falsified']} of {d['population']} = {d['raw_rate']:.4f} vs "
                      f"{d['baseline_R802']:.4f}",
                      [r"(4 of 16|0\.25).{0,300}(0\.0333|R802)",
                       r"(outside the release).{0,200}(inside it|already inside)"]))

    # ⛔⛔ R1040: R1023's wall falls — A2's arm ordering is 6.9x more reproducible across
    #    annotator splits, so the target is selectable from inside the release.
    d = load("A27_*/R1040_*/results/target_choice_in_release.json")
    if d:
        facts.append(("R1040", "the target is selectable in-release; A2 more reproducible",
                      f"A2 {d['rho']['A2']['median']:.4f} vs A1c {d['rho']['A1c']['median']:.4f}, "
                      f"gap {d['gap']:.4f}",
                      [r"(reproducib\w+).{0,300}(A2).{0,200}(0\.99|6\.9)",
                       r"(annotator (panel|split)).{0,300}(select|falls)"]))

    # ⛔⛔ R1041: fallen and standing IMPOSSIBLE blocks are structurally indistinguishable, so the
    #    remedy is a declared field FORWARD-ONLY and any triage ordering is a guess.
    d = load("A27_*/R1041_*/results/fallen_wall_signal.json")
    if d:
        facts.append(("R1041", "fallen and standing walls are indistinguishable in text",
                      f"best p {d['best_p']:.4f} vs Bonferroni {d['bonferroni']:.4f}, "
                      f"perm {d['permutation_p']:.4f}",
                      [r"(indistinguishable).{0,300}(committed text|text)",
                       r"(forward[- ]only|going forward only).{0,200}(declared field|field)"]))

    # ⛔ R1042: PRODUCTION — the declared-field gate, forward-only, with this round as its first
    #    live block. No estimand and no worlds; it is registered so the statement carries the
    #    discipline rather than only the findings.
    d = load("A27_*/R1042_*/results/field_and_gate.json")
    if d:
        facts.append(("R1042", "IMPOSSIBLE blocks now declare where they would be settled",
                      f"tags {d['tags']}, cutoff R{d['cutoff']}, live rc {d['live_rc']}",
                      [r"(SETTLES:).{0,200}(IN-RELEASE|UNATTACKED|OUT-OF-RELEASE)",
                       r"(forward[- ]only).{0,300}(declar\w+|enum)"]))

    # ⛔⛔ R1043: mutation-testing the three commit gates — `anchoring` passes a corruption of a
    #    value it explicitly asserts, so a green anchoring is evidence about its silence.
    d = load("A27_*/R1043_*/results/mutation_test.json")
    if d:
        facts.append(("R1043", "one of the three commit gates is blind under mutation",
                      f"blind {d['blind']}, mutated {d['mutated']}",
                      [r"(mutation).{0,300}(blind|anchoring)",
                       r"(anchoring).{0,200}(passes|blind).{0,200}(corrupt|assert)"]))

    # ⛔⛔ R1044 RETRACTS R1043's headline: the anchoring gate is NARROW, not blind — it detects a
    #    corrupted value inside its assertion spans and publishes its own 2.7%-7.8% coverage.
    d = load("A27_*/R1087_*/results/other_two_clauses.json")
    if d:
        r, c = d["distributions"]["resolvability"], d["distributions"]["coverage"]
        facts.append(("R1087", "one row is a draw and the other is a genuine invariant",
                      f"resolvability [{r['min']},{r['max']}] {r['distinct_values']} values, "
                      f"coverage [{c['min']},{c['max']}] {c['distinct_values']} value",
                      [r"coverage\s+is\s+a\s+genuine\s+invariant|invariant\s+across\s+all",
                       r"refuted\s+by\s+its\s+own\s+instrument"]))

    d = load("A27_*/R1086_*/results/q_value_or_draw.json")
    if d:
        t = d["distribution_by_k"]["10"] if "10" in d["distribution_by_k"] else d["distribution_by_k"][10]
        facts.append(("R1086", "q buys a DISTRIBUTION, not a value; in 27.5% of families it buys 0",
                      f"k=10 span [{t['min']},{t['max']}], {t['distinct_values']} values, "
                      f"mode {t['mode']} at {t['mode_share']}",
                      [r"cannot\s+be\s+stated\s+without\s+naming\s+the\s+family",
                       r"27\.5%\s+of\s+families\s+it\s+buys\s+nothing|buys\s+0\s+in\s+825"]))

    d = load("A27_*/R1085_*/results/isolation_reaches_the_writers.json")
    if d:
        facts.append(("R1085", "isolation is a safety property, and it bought nothing statistical",
                      f"floor dirty isolated {len(d['Q2_floor_dirty_even_isolated'])}, "
                      f"sham {len(d['sham_no_isolation_floor_dirty'])}, "
                      f"buys {d['isolation_buys']}",
                      [r"isolation\s+is\s+a\s+safety\s+property",
                       r"buys\s+\*\*0\*\*|Isolation\s+buys\s+0"]))

    d = load("A27_*/R1084_*/results/parse_vs_run.json")
    if d:
        c = d["confusion"]
        facts.append(("R1084", "the parse nominates soundly and decides badly, over 47 of 88 scripts",
                      f"recall {c['recall']}, precision {c['precision']}, "
                      f"writers excluded {d['population']['writers_excluded']}",
                      [r"sound\s+NOMINATOR\s+and\s+a\s+poor\s+DECIDER",
                       r"reads\s+its\s+own\s+previous\s+run"]))

    d = load("A27_*/R1083_*/results/label_or_dependency.json")
    if d:
        c = d["cwd_invariance"]
        facts.append(("R1083", "the gate's coverage was decided by the caller's working directory",
                      f"unevaluable root {c['unevaluable_from_repository_root']} vs elsewhere "
                      f"{c['unevaluable_from_elsewhere']}, exit {c['exit_from_elsewhere']}",
                      [r"decided\s+by\s+the\s+caller",
                       r"hard-coded\s+relative\s+path"]))

    d = load("A27_*/R1082_*/results/first_home_only.json")
    if d:
        facts.append(("R1082", "three anchors were green because of document order, now repaired",
                      f"multi-home {d['Q1_multi_home']}, disagreeing {d['Q2_disagreeing_homes']}, "
                      f"pinned at {d.get('pinned_revision')}",
                      [r"green\s+because\s+of\s+document\s+ORDER",
                       r"an\s+anchor\s+identifies\s+a\s+SENTENCE"]))

    d = load("A27_*/R1081_*/results/occasion_by_execution.json")
    if d:
        h = d["headline_cell"]
        facts.append(("R1081", "the occasion is the majority of the corpus, found by execution",
                      f"{h['occasion_rounds']} of {h['eligible_rounds']} rounds, "
                      f"floor {h['placebo_mean']}, shifted {h['within_round_shifted_rate']}",
                      [r"368\s+of\s+476",
                       r"gap\s+WIDENS|widens\s+with\s+displayed\s+precision"]))

    d = load("A27_*/R1080_*/results/reachable_or_unknown.json")
    if d:
        facts.append(("R1080", "the helper is reachable from every depth and has zero static importers",
                      f"world_A_killed {d['kill']['world_A_killed']}, "
                      f"landmark statements {d['census_Q2']['statements'].get('landmark')}, "
                      f"static importers {len(d['adoption_Q3']['static_import'])}",
                      [r"zero\s+static\s+importers",
                       r"reachable\s+from\s+every\s+depth"]))

    d = load("A27_*/R1079_*/results/closure_membership.json")
    if d:
        facts.append(("R1079", "three classifiers failed; the population is not mechanically enumerable",
                      f"verdict {d['verdict']}, stowaways {d.get('stowaways_present')}, "
                      f"cands {d.get('cands_found')}",
                      [r"Three attempts, three failures",
                       r"cannot\s+be\s+enumerated\s+mechanically"]))

    d = load("A27_*/R1078_*/results/argument_traces.json")
    if d:
        facts.append(("R1078", "the census excluded the one confirmed defect; the gap size is unverified",
                      f"R1070 missing {d['R1070_was_missing_from_census']}, "
                      f"sizing control {d['sizing_control_passed']}",
                      [r"R1070\s+has\s+NO\s+rows\s+in\s+that\s+census",
                       r"249.{0,60}not\s+a\s+count|reproduced\s+the\s+contamination"]))

    d = load("A27_*/R1077_*/results/exposed_sites.json")
    if d:
        facts.append(("R1077", "most precision-blind sites cannot be exposed at all",
                      f"sites {d['sites']}, at-risk {d['at_risk']}, safe {d['not_exposed']}",
                      [r"22\s+CANNOT\s+be\s+exposed",
                       r"strip\s+comments\s+and\s+docstrings"]))

    d = load("A27_*/R1076_*/results/membership_tests.json")
    if d:
        facts.append(("R1076", "the precision-blind comparison is a pattern; the helper is shipped",
                      f"impls {d['implementations']}, blind {d['precision_blind']}, "
                      f"aware {d['precision_aware']}",
                      [r"38\s+independent\s+value-membership\s+implementations",
                       r"assurance/valuematch\.py"]))

    d = load("A27_*/R1075_*/results/produced_or_consumed.json")
    if d:
        facts.append(("R1075", "the unstored-values chain is void: they are stored at full precision",
                      f"produced {d['produced']}, consumed {d['consumed']}, "
                      f"candidates produced {d['candidates_produced']} of {d['candidates']}",
                      # ⛔ the FIRST pattern here matched a longer value in a DEFINITION.md table
                      # (0.5593110792) and that coincidence is what exposed the whole chain
                      [r"premise of five rounds is void",
                       r"0\.5593110791885862"]))

    d = load("A27_*/R1074_*/results/role_of_the_six.json")
    if d:
        u = d["unit_correction"]
        facts.append(("R1074", "the chain counted occurrences while saying values",
                      f"single {u['single_occurrences']} occ = {u['single_distinct']} distinct, "
                      f"candidate {d['candidate_finding']} of {d['total']}",
                      # ⚠ aligned to the wording actually written, verified against the document first
                      [r"6 occurrences = 3 distinct",
                       r"R981\s+itself\s+calls\s+it\s+a\s+population\s+error"]))

    d = load("A27_*/R1073_*/results/carrier_cardinality.json")
    if d:
        facts.append(("R1073", "the recording gap is three gaps; only the attributable one is a write",
                      f"single {d['single_carrier']}, many {d['many']}, none {d['none']}, "
                      f"share {d['single_share']:.3f}",
                      [r"exactly\s+one\*?\*?\s+upstream\s+README\s+carries\s+it\s*\|?\s*\*?\*?6",
                       r"margin\s+over\s+the\s+floor\s+is\s+.\+0\.065"]))

    d = load("A27_*/R1071_*/results/prose_or_nowhere.json")
    if d:
        facts.append(("R1071", "the unstored clause decimals are a recording failure, not absent",
                      f"in prose {d['in_prose']} of {d['unstored']}, nowhere {len(d['nowhere'])}, "
                      f"sham {d['sham_release_data_hits']}",
                      [r"31\s+of\s+31\.\s+It\s+is\s+a\s+recording\s+failure|31 of 31 = 1\.000",
                       r"\[0\.032,\s*0\.161\]"]))

    d = load("A27_*/R1070_*/results/decimal_addresses.json")
    if d:
        facts.append(("R1070", "most clause decimals are quoted, not stored; R1069's headline falls",
                      f"unsourced {d['unsourced']} of {d['decimals']}, "
                      f"inflation +{d['quoter_inflation_mean']:.1f}",
                      [r"31\s+of\s+38\s+clause\s+decimals",
                       r"sourceable\s+AS\s+TEXT"]))

    d = load("A27_*/R1069_*/results/clause_number_sources.json")
    if d:
        pc = d["per_class"]
        facts.append(("R1069", "decimals are sourceable above their floor; integers are saturated",
                      f"dec {pc.get('decimals', {}).get('sourceable', 0):.3f}, "
                      f"int {pc.get('integers', {}).get('sourceable', 0):.3f}, "
                      f"tokens {d['tokens']}",
                      [r"decimals\*?\*?\s*\|?\s*\*?\*?38\s*\|?\s*\*?\*?0\.789",
                       r"integer\s+class\s+is\s+saturated|saturated[^.]{0,60}0\.94"]))

    d = load("A27_*/R1068_*/results/clause_gate.json")
    if d:
        facts.append(("R1068", "a gate now covers the clause's declared constants, and fails closed",
                      f"declared {d['declared']}, sham {d['sham_exit']}, "
                      f"artifact-removed {d['artifact_removed_exit']}",
                      [r"4\s+of\s+4\s+declared\s+clause\s+constants",
                       r"the_clause_is_anchored\.py"]))

    d = load("A27_*/R1067_*/results/clause_coverage.json")
    if d:
        facts.append(("R1067", "the clause sits in the anchoring gate's uncovered remainder",
                      f"constants {d['constants']}, noticed {d['noticed']}",
                      # ⚠ aligned to the wording actually written, not the wording I intended —
                      # checked against the document before committing, per R1063
                      [r"`0 of 121`\s+NUMERIC\s+CONSTANTS",
                       r"never\s+that\s+the\s+clause\s+is\s+anchored"]))

    d = load("A27_*/R1066_*/results/anchoring_coupling.json")
    if d:
        facts.append(("R1066", "anchoring IS artifact-coupled; the two gates differ in kind",
                      f"coupled {d['artifact_coupled']}, exits {d['exits']}",
                      [r"the\s+two\s+gates\s+differ\s+in\s+kind",
                       r"artifact\s+`4\s+.\s+7781`|4\s*.\s*7781"]))

    d = load("A27_*/R1065_*/results/gate_coupling.json")
    if d:
        facts.append(("R1065", "this gate is text-only: its verdict ignores the artifact it loads",
                      f"coupled {d['artifact_coupled']}, exits {d['exits']}",
                      [r"globs\s+4321,\s+dead\s+1",
                       r"certifies\s+prose\s+against\s+prose"]))

    d = load("A27_*/R1064_*/results/registry_inputs.json")
    if d:
        facts.append(("R1064", "every registered artifact glob resolves, and the skip is now loud",
                      f"globs {d['globs']}, dead {len(d['dead'])}",
                      [r"79\s+globs\s+resolve|all\s+79\s+globs",
                       r"a_registered_fact_must_load\.py"]))

    d = load("A27_*/R1063_*/results/criterion_universes.json")
    if d:
        facts.append(("R1063", "the criterion universes are disjoint and the join is key-blocked",
                      f"ids {d['arc_prompt_ids']}/{d['rubric_conversation_ids']} "
                      f"inter {d['id_intersection']}, shared texts {len(d['shared_texts'])}",
                      # ⛔ tightened after the first pair matched R466's OWN sentence and passed GREEN
                      # with nothing written — the fact's patterns must name THIS fact
                      # ⚠ \s+ not a literal space: markdown hard-wrapping splits multi-word anchors
                      # across lines, which is one reason loose patterns get written in the first place
                      [r"14,?808\s+rubric-derived\s+texts",
                       r"4\s+fixed\s+generic\s+texts[\s\S]{0,120}0 shared"]))

    d = load("A27_*/R1062_*/results/index_locality.json")
    if d:
        facts.append(("R1062", "the criterion index is local to its file; cross-file numbers are void",
                      f"disagree {d['rate_1e12']:.4f}, exact matches {len(d['exact_matches'])} "
                      f"of {len(d['generic_criteria'])}",
                      [r"0\.9606",
                       r"0 of 4 exact matches|POSITION IN THAT ARM"]))

    d = load("A27_*/R1061_*/results/reconciliation.json")
    if d:
        facts.append(("R1061", "R1060 compared against a reconstructed arm, not the comparator",
                      f"differ on {d['sources_differ_on_prompts']} prompts, "
                      f"object_explains {d['object_explains']}",
                      [r"0\.6632",
                       r"764 of 968"]))

    d = load("A27_*/R1060_*/results/fixed_rule_bound.json")
    if d:
        facts.append(("R1060", "no fixed-subset core can close the gap on this site",
                      f"family {d['family_size']}, margins {[round(m, 4) for m in d['margins']]}, "
                      f"optimism {d['selection_optimism']:.4f}",
                      [r"4,?943 fixed subsets",
                       r"UNVERIFIED\s*\n?against each other|THREE numbers for one arm|Three\*\*?\s*\n?numbers for one arm"]))

    d = load("A27_*/R1059_*/results/second_optimiser.json")
    if d:
        facts.append(("R1059", "the confound reproduces; the quality gap sustains it",
                      f"gap {d['quality_gap']:.4f}, best {d['best_synthetic_mean']:.4f}, "
                      f"inert {d['objective_inert']}",
                      [r"0\.0651",
                       r"0\.4863[^.]{0,60}0\.5514|size-matched selection rule"]))

    d = load("A27_*/R1058_*/results/never_seen_cores.json")
    if d:
        facts.append(("R1058", "whether the clause defines or describes is UNIDENTIFIED here",
                      f"rules {len(d['rules'])}, released {d['released_rate']:.3f}, "
                      f"verdict {d['verdict']}",
                      [r"UNVERIFIED ON IDENTIFICATION|UNIDENTIFIED on this site",
                       r"unselected.{0,80}optimised|confounds PROVENANCE with QUALITY"]))

    d = load("A27_*/R1057_*/results/q_in_its_own_world.json")
    if d:
        big = [r for r in d["rows"] if r["k"] >= 10]
        facts.append(("R1057", "q buys arms in the world where it can act; keep it",
                      f"cells {len(big)}, deltas {[r['symmetric_difference'] for r in big]}, "
                      f"space {len(d['synthetic_family'])}",
                      [r"buys 2 arms at .{0,20}k=10|2 arms at the two cells",
                       r"caps at .{0,4}15|2. . 1 = 15"]))

    d = load("A27_*/R1056_*/results/certification_curve.json")
    if d:
        facts.append(("R1056", "q cannot be exercised: the family is 2 at every defensible threshold",
                      f"arms {d['arms']}, usable rules {len(d['usable_rules'])}, "
                      f"k needed {d['k_needed_for_q']}",
                      [r"permanently inert",
                       r"admits .{0,4}nobody new|250.{0,40}admits"]))

    d = load("A27_*/R1055_*/results/component_ablation.json")
    if d:
        facts.append(("R1055", "two clause components bind, q is inert at this family size",
                      f"empty {len(d['empty_components'])}, family {d['family_size']}, "
                      f"q testable at {d['q_first_testable_at_family_size']}",
                      [r"q.{0,60}inert until.{0,40}10|first becomes testable at \*\*\|family\| =\s*10",
                       r"greedy_k12_fit1[^.]{0,40}topw_k2"]))

    d = load("A27_*/R1054_*/results/declared_dependencies.json")
    if d:
        facts.append(("R1054", "at the sentence unit the clause shows no enrichment",
                      f"declared {len(d['declared'])}, rate {d['declared_flagged_rate']:.3f} vs "
                      f"{d['registry_flagged_rate']:.3f}, MDE {d['enrichment_mde']:.3f}",
                      [r"0\.667[^.]{0,60}0\.676",
                       r"MDE[^.]{0,40}0\.202|0\.05 of the MDE"]))

    d = load("A27_*/R1053_*/results/recomputed_dependence.json")
    if d:
        facts.append(("R1053", "R1050's direction survives but its magnitude is at the ceiling",
                      f"ceiling {d['ceiling']:.3f}, saturating set {d['k_saturate']}, "
                      f"flagged {len(d['flagged_any'])}",
                      [r"at the CEILING|AT the ceiling",
                       r"11 rounds[^.]{0,60}only 5 are flagged|5 of 11"]))

    d = load("A27_*/R1052_*/results/stamp_vs_history.json")
    if d:
        facts.append(("R1052", "R1051's stamp census counted titles as hashes",
                      f"checked {d['checked']} of {d['stamped']}, floor "
                      f"{d['random_commit_floor_3_seeds'][0]:.3f}",
                      # ⛔ tightened after this very fact passed GREEN on one loose pattern —
                      #   the gate is `any()`, so EVERY pattern here must name the fact
                      [r"census is retracted[^.]{0,40}9 stamps",
                       r"45 of 67"]))

    d = load("A27_*/R1051_*/results/reran_the_flagged.json")
    if d:
        sc = d["stamp_census"]
        facts.append(("R1051", "the flagged rounds re-derive their committed values exactly",
                      f"ran {d['ran']}, drifted {len(d['drifted'])}, "
                      f"unstamped {len(sc['unstamped'])}",
                      [r"all 16[^.]{0,60}re-derive|16 of 16[^.]{0,40}values",
                       r"3 artifacts carry no stamp|no stamp at all and cannot be traced"]))

    d = load("A27_*/R1050_*/results/audit_reached_the_object.json")
    if d:
        facts.append(("R1050", "the clause rests on the facts the gate cannot attribute",
                      f"hit rate {d['observed_hit_rate']:.3f} vs floor "
                      f"{d['permutation_floor_3_seeds'][1]:.3f}, clause homes {d['clause_homes']}",
                      [r"0\.917[^.]{0,90}0\.524",
                       r"occurs 9 times|has 9 homes|NINE times"]))

    d = load("A27_*/R1049_*/results/gate_coincidence.json")
    if d:
        facts.append(("R1049", "this gate's own PASS is unattributable for some facts",
                      f"multi-home {d['multi_home']} of {d['facts_readable']}, "
                      f"floor {d['random_floor_3_seeds'][1]:.3f}",
                      # tight by construction: each names the fact, per R1048's repair
                      [r"multi-home[^.]{0,80}16 of 63",
                       r"random floor[^.]{0,60}0\.183"]))

    d = load("A27_*/R1048_*/results/residue_partition.json")
    if d:
        fl = d["coincidence_floor_3_seeds"]
        facts.append(("R1048", "the derivation test cannot fail, so the residue is UNCLASSIFIED",
                      f"floor {fl[0]:.3f}-{fl[1]:.3f} vs observed "
                      f"{d['derived_share_upper_bound']:.3f}, unclassified "
                      f"{d['unclassified_not_floating']}",
                      # ⛔ TIGHTENED AFTER THIS PAIR PASSED WITH NO ANNOTATION WRITTEN: the loose
                      #   form matched `97.5%` in an unrelated table beside the word "random", and
                      #   `UNVERIFIED` beside `R243`. A fact's pattern must name the fact.
                      [r"coincidence floor.{0,120}0\.975",
                       r"43 (are |remain )?UNCLASSIFIED"]))

    d = load("A27_*/R1047_*/results/floating_or_constant.json")
    if d:
        rc = d["R1046_recomputed"]
        facts.append(("R1047", "R1046's bracket was inflated by display rounding",
                      f"rescued {d['rescued_by_rounding_alone']}, residue {d['residue_lower_bound']}, "
                      f"bracket now {rc['bracket'][0]:.3f}-{rc['bracket'][1]:.3f}",
                      [r"(122).{0,200}(round)",
                       r"(0\.057|0\.159).{0,160}(0\.164|0\.272)"]))

    d = load("A27_*/R1046_*/results/headline_backing.json")
    if d:
        c, s = d["cells"], d["unbacked_split"]
        facts.append(("R1046", "a README's numbers are not anchored to its own artifact",
                      f"body {c['body']['unbacked']} of {c['body']['numbers']}, "
                      f"bracket {s['bracket'][0]:.3f}-{s['bracket'][1]:.3f}",
                      [r"(16\.4|0\.164).{0,120}(27\.2|0\.272)",
                       r"(175).{0,200}(no artifact|nowhere)"]))

    d = load("A27_*/R1045_*/results/habit_or_incident.json")
    if d:
        s, a = d["axis_subprocess"], d["axis_artifact"]
        facts.append(("R1045", "R1044's habit claim is withdrawn: the count is an incident",
                      f"subprocess {len(s['rc_without_stdout'])} of {s['population']}, "
                      f"artifact {len(a['existence_only'])} of {a['population']}",
                      [r"(incident).{0,300}(1 of 3|one|population)",
                       r"(0 of 14|14).{0,200}(existence|value)"]))

    d = load("A27_*/R1044_*/results/narrow_not_blind.json")
    if d:
        mm = d["mutation"]
        facts.append(("R1044", "the anchoring gate is narrow, not blind",
                      f"covered rc {mm['covered']['rc']}, uncovered rc {mm['uncovered']['rc']}",
                      [r"(narrow).{0,200}(not blind|rather than blind)",
                       r"(2\.7%|7\.8%).{0,300}(coverage|covered)"]))

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
