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
