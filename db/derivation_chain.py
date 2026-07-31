"""The derivation chain: every conclusion linked to the experiments that carry it.

WHY A GRAPH AND NOT A DOCUMENT
------------------------------
A prose paragraph saying "X holds because of experiment R" is a relation written as a sentence, and
a sentence cannot be queried, cannot be invalidated when R is retracted, and cannot tell you what
else falls when it does. The relation belongs in an edge. This module is the generator; the DB is
the ontology.

Idempotent by design: nodes are keyed on `name`, edges on (src,dst,kind), evidence on
(node,experiment,finding). Re-run it after every round and the graph grows rather than duplicating.

WHAT THE THREE LAYERS MEAN HERE
-------------------------------
  node        a claim, an assumption of theirs, a knife, an instrument, a control, a defect
  edge        the inference: attacks / overturns / supports / depends_on / confounds / acquits
  evidence    the pointer from a claim to the round artifact whose numbers carry it

A claim with no evidence row is a claim nobody measured. A claim whose only support is an edge from
another claim is a claim standing on a claim. Both are visible in one query, which is the point.

STATUS VOCABULARY (constrained by the template's CHECK)
  open      the knife exists, nobody has run it
  partial   measured, but not saturated -- one design, or a control still outstanding
  settled   survived attack at the campaign's standard
  refuted   overturned by evidence
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
DB = "coval"
SCHEMA = "claim"


def q(sql: str, args: tuple = ()) -> list[tuple]:
    """One psql round trip. Values are passed as a literal-safe VALUES payload on stdin."""
    payload = sql
    if args:
        esc = ["NULL" if a is None else
               (str(a) if isinstance(a, (int, float)) else
                "'" + str(a).replace("'", "''") + "'") for a in args]
        payload = sql % tuple(esc)
    # search_path goes on the CONNECTION, not into the query: psql prints a status tag for every
    # non-SELECT statement even under -t -A, and a stray "SET" line at the head of the result set
    # silently becomes row 0.
    env = dict(os.environ, PGOPTIONS=f"-c search_path={SCHEMA},public")
    p = subprocess.run(["psql", "-d", DB, "-t", "-A", "-F", "\x1f", "-v", "ON_ERROR_STOP=1",
                        "-c", payload], capture_output=True, text=True, env=env)
    if p.returncode != 0:
        raise RuntimeError(f"psql failed:\n{payload}\n{p.stderr}")
    tags = {"SET", "BEGIN", "COMMIT", "DELETE", "UPDATE", "INSERT"}
    return [tuple(l.split("\x1f")) for l in p.stdout.strip().splitlines()
            if l and l.split()[0] not in tags]


# ---------------------------------------------------------------------------------------------
# vocabularies -- INSERT, never ALTER (the template's design)
# ---------------------------------------------------------------------------------------------
NODE_KINDS = [
    ("their_assumption", "a load-bearing assumption of the CoVal release itself"),
    ("their_result", "a result the release claims to have produced"),
    ("my_claim", "a claim this campaign asserts"),
    ("knife", "an attack vector on a claim -- an experiment that could kill it"),
    ("instrument", "a measuring apparatus that claims depend on"),
    ("defect", "a specific implementation or inference flaw, alleged or established"),
    ("control", "a control whose outcome gates whether a claim may be asserted"),
    ("fact", "a direct count or read off the object, carrying no inference"),
]
EDGE_KINDS = [
    ("attacks", False, "src is an attack designed to kill dst"),
    ("overturns", False, "src's evidence refutes dst"),
    ("supports", False, "src's evidence raises confidence in dst"),
    ("depends_on", False, "dst's failure would take src with it"),
    ("confounds", False, "src is an alternative explanation for dst's evidence"),
    ("acquits", False, "src is a control that ran and cleared dst"),
    ("replicates", True, "src and dst are independent designs reaching the same number"),
    ("refines", False, "src narrows or corrects dst without killing it"),
]
UNIVERSES = [
    ("polarity", None, "the sign of a criterion's human rating and what is done with it"),
    ("weighting", None, "the -10..+10 importance ratings and their use"),
    ("aggregation", None, "how many people back a value and how they are combined"),
    ("instrument", None, "the satisfaction judge and its implementation"),
    ("substitution", None, "what cheap rule reproduces the compiler"),
    ("provenance", None, "which artifact was produced by which code at which time"),
    ("redistribution", None, "who gains and who loses under compilation"),
]


def upsert_vocab():
    for k, d in NODE_KINDS:
        q("INSERT INTO node_kind(kind,descr) VALUES (%s,%s) ON CONFLICT (kind) DO UPDATE "
          "SET descr=EXCLUDED.descr", (k, d))
    for k, sym, d in EDGE_KINDS:
        q("INSERT INTO edge_kind(kind,is_symmetric,descr) VALUES (%s," + ("true" if sym else "false")
          + ",%s) ON CONFLICT (kind) DO UPDATE SET descr=EXCLUDED.descr", (k, d))
    for k, par, d in UNIVERSES:
        q("INSERT INTO universe(kind,parent,descr) VALUES (%s,%s,%s) ON CONFLICT (kind) DO UPDATE "
          "SET descr=EXCLUDED.descr", (k, par, d))


def node(name, kind, statement, universe=None, d=None, status=None, props=None):
    q("INSERT INTO node(kind,name,statement,universe,d_level,status,props) "
      "VALUES (%s,%s,%s,%s," + (str(d) if d is not None else "NULL") + ",%s,%s::jsonb) "
      "ON CONFLICT DO NOTHING", (kind, name, statement, universe, status,
                                 json.dumps(props or {})))
    # `name` is not unique in the template's schema, so enforce single-home here rather than
    # silently accumulating duplicates -- HB7: one home per fact.
    ids = q("SELECT id FROM node WHERE name=%s ORDER BY id", (name,))
    if len(ids) > 1:
        for (extra,) in ids[1:]:
            q("DELETE FROM node WHERE id=%s", (extra,))
    nid = int(ids[0][0])
    q("UPDATE node SET kind=%s, statement=%s, universe=%s, "
      "d_level=" + (str(d) if d is not None else "NULL") + ", status=%s, props=%s::jsonb "
      "WHERE id=" + str(nid), (kind, statement, universe, status, json.dumps(props or {})))
    return nid


def edge(src, dst, kind, df=None, db_=None, note=None):
    q("INSERT INTO edge(src,dst,kind,d_forward,d_backward,note) VALUES "
      f"({src},{dst},%s," + (str(df) if df is not None else "NULL") + ","
      + (str(db_) if db_ is not None else "NULL") + ",%s) "
      "ON CONFLICT (src,dst,kind) DO UPDATE SET d_forward=EXCLUDED.d_forward, "
      "d_backward=EXCLUDED.d_backward, note=EXCLUDED.note", (kind, note))


def evid(nid, experiment, finding, d):
    got = q("SELECT id FROM evidence WHERE node_id=" + str(nid) + " AND experiment=%s",
            (experiment,))
    if got:
        q("UPDATE evidence SET finding=%s, d_level=" + str(d) + " WHERE id=" + got[0][0],
          (finding,))
    else:
        q("INSERT INTO evidence(node_id,experiment,finding,d_level) VALUES "
          f"({nid},%s,%s,{d})", (experiment, finding))


# ---------------------------------------------------------------------------------------------
# the graph as it actually stands. Every d_level and status here is defensible from an artifact
# in this repo or from a direct count printed in the session; nothing is asserted from memory.
# ---------------------------------------------------------------------------------------------
def build():
    upsert_vocab()
    N = {}

    # ---- the instrument everything depends on ------------------------------------------------
    N["INSTR"] = node(
        "a04-satisfaction-tensor", "instrument",
        "Per (prompt, criterion, response) satisfaction in [0,1], produced by a local "
        "Qwen3.5-2B-Base reading sigmoid(logit(' Yes') - logit(' No')) at the answer position of a "
        "two-shot prompt. 75,248 judgements over 968 prompts. Every claim in this campaign that "
        "compares rubric arms is conditional on it.",
        "instrument", 7, "partial",
        {"files": ["01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz",
                   "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz"],
         "built": "2026-07-27 16:45", "model": "Qwen/Qwen3.5-2B-Base"})

    # ---- alleged defects in the instrument, and their verdicts --------------------------------
    for nm, stmt, verdict, ev in [
        ("defect-yes-no-token-id",
         "r04's inline Judge takes yes_id, no_id = encode(' Yes')[0], encode(' No')[0] with no "
         "guard, unlike covalx/judge.py which raises when one encoding prefixes the other. The "
         "tensors predate that guard's commit (eb1f0b7, 2026-07-28 11:54) by 19 hours.",
         "refuted",
         "Qwen2Tokenizer gives ' Yes'->[7179] and ' No'->[2233]: both single tokens, distinct. "
         "The SentencePiece failure mode cannot arise on this BPE tokenizer. ACQUITTED."),
        ("defect-right-truncation-1024",
         "tokenizer(truncation=True, max_length=1024) truncates from the right, and the prompt's "
         "final token is 'Answer:' -- the exact position whose logits are read. Any over-length "
         "judgement would be reading a mid-reply next-word prediction instead of a verdict.",
         "refuted",
         "Over all 75,248 rebuilt judge prompts: median 236 tokens, p99 321, max 537. Zero "
         "exceeded 1024 (0.0000%). truncation_side is indeed 'right', so the mechanism is real "
         "but never fires on this corpus. ACQUITTED."),
        ("defect-1400-char-reply-cut",
         "build_prompt() cuts every reply at 1400 characters before tokenising, so the judge is "
         "structurally blind to anything late in a long response, and differentially so within a "
         "prompt whose four responses differ in length.",
         "refuted",
         "3,872 responses: median 525 chars, p95 691, max 2,624. Six responses (0.2%) exceed "
         "1400, across 6 of 968 prompts, never all four in one prompt. Median within-prompt "
         "length spread 1.30x. ACQUITTED as negligible, not as absent."),
    ]:
        nid = node(nm, "defect", stmt, "instrument", 8, verdict)
        N[nm] = nid
        edge(nid, N["INSTR"], "attacks", 8, None, "an implementation-level attack on the judge")
        evid(nid, "session-direct-check-2026-07-30", ev, 8)

    # ---- CoVal's own assumptions --------------------------------------------------------------
    N["A1"] = node(
        "A1-core-is-a-faithful-compilation", "their_assumption",
        "coval_core, four compiled criteria carrying no ratings, is a faithful compilation of "
        "coval_full's ~15.8 participant-written criteria and their -10..+10 importance ratings.",
        "polarity", 8, "refuted")
    N["A3"] = node(
        "A3-aggregation-yields-a-collective-standard", "their_assumption",
        "Aggregating criteria across participants produces a standard that is collective rather "
        "than an artefact of who happened to be asked.",
        "aggregation", 5, "partial")
    N["A6"] = node(
        "A6-ratings-are-meaningful-importance-weights", "their_assumption",
        "The -10..+10 per-criterion ratings carry usable importance information.",
        "weighting", 7, "partial")

    # ---- direct facts off the object ----------------------------------------------------------
    N["F_SINGLE"] = node(
        "fact-63pct-of-criteria-have-one-rater", "fact",
        "Of coval_full's 15,248 rated criteria, 63.5% carry exactly one rating and 34.0% carry ten "
        "or more; 0.2% lie between. Among the 3,905 negatively-rated criteria, 77.2% are "
        "single-rater, against 58.8% of the positive ones.",
        "aggregation", 9, "settled")
    evid(N["F_SINGLE"], "session-direct-count-2026-07-30",
         "Counted straight off data/conversation_rubrics.jsonl; no model, no inference.", 9)
    edge(N["F_SINGLE"], N["A3"], "attacks", 8, None,
         "a value backed by one rater is not obviously collective")

    N["F_SPLIT"] = node(
        "fact-negative-criteria-are-splits-not-evils", "fact",
        "Among the 890 negatively-rated criteria with at least three raters, 99.1% have at least "
        "one rater on the positive side, the median share of positive raters is 38.5%, and 47.9% "
        "have at least 40% of raters positive. Bootstrapping the rater set, 18.9% of the n>=10 "
        "criteria flip sign in more than 10% of resamples.",
        "aggregation", 8, "settled")
    evid(N["F_SPLIT"], "session-direct-count-2026-07-30",
         "Text inspection confirms the class: 'Take an explicit position on whether Chile should "
         "expand or restrict access to abortion' (-5.23, n=13) is a contested stance, not a harm.",
         8)
    edge(N["F_SPLIT"], N["A3"], "attacks", 7, None,
         "collapsing a near-even split into a sign is the criterion-level sacrifice")

    # ---- the knives on A1 ---------------------------------------------------------------------
    knives = [
        ("K1-polarity-retention", "Does core retain the negatively-rated quarter, and at what "
         "weight relative to the positive portion?", "polarity", "refuted"),
        ("K3-weight-discard", "core carries no ratings. Does it behave like an importance-weighted "
         "summary of full, an unweighted one, or neither?", "weighting", "open"),
        ("K13-sham-ladder", "Where does core sit on a ladder of zero-LLM substitutes: random-4, "
         "top-rated-4, mechanically-selected-4, other-prompt-4, generic-4?", "substitution",
         "partial"),
        ("K16-single-judge-gauge", "Is the whole comparison an artefact of one Qwen judge? No "
         "second judge has been run.", "instrument", "open"),
    ]
    for nm, stmt, uni, st in knives:
        N[nm] = node(nm, "knife", stmt, uni, None, st)
        edge(N[nm], N["A1"], "attacks", 8, None, None)

    # ---- what the knives returned -------------------------------------------------------------
    N["C_POL"] = node(
        "core-retains-the-negative-quarter-at-one-tenth-weight", "my_claim",
        "Regressing core's within-prompt-centred response score on full's positive and "
        "sign-flipped negative components gives beta_neg/beta_pos = 0.094 (95% CI [0.073, 0.114]). "
        "A faithful summary weighting each polarity block by its share of the input would give "
        "0.362. Core therefore carries the negatively-rated quarter at roughly a quarter of "
        "proportional weight and a tenth of the positive block's weight.",
        "polarity", 8, "settled")
    edge(N["C_POL"], N["A1"], "overturns", 8, None,
         "faithfulness on the polarity axis fails")
    edge(N["C_POL"], N["INSTR"], "depends_on", 8, None,
         "every satisfaction value comes from the one judge")
    edge(N["K1-polarity-retention"], N["C_POL"], "supports", 8, None, None)
    evid(N["C_POL"], "r124-my-own-decomposition",
         "beta_pos=+1.1253 (se 0.0093, t=121.3), beta_neg=+0.1067 (se 0.0077, t=13.8), R^2=0.8056 "
         "over 924 prompts / 3,696 units; corr(components)=+0.0877. Placebo: decomposing full's "
         "own positive arm returns exactly (1.0000, -0.0000).", 8)
    evid(N["C_POL"], "independent-design-B-seed-4409",
         "Independent estimand, independent code, seed 4409: ratio 0.094 [0.073, 0.114], "
         "beta_pos 1.124. Synthetic placebo recovers planted (0.7,0.2) as (0.701,0.201) and "
         "(0.7,0.0) as (0.697,0.001).", 8)

    N["CTRL_SIZE"] = node(
        "control-group-size-permutation", "control",
        "The negative block averages ~4.2 criteria per prompt against the positive block's ~11.6, "
        "so its component is a noisier group mean and its regression coefficient is attenuated by "
        "measurement error alone. Control: permute which criteria fall into same-sized pseudo-"
        "groups, ignoring true sign, and read the ratio that group size alone produces.",
        "polarity", 8, "settled")
    evid(N["CTRL_SIZE"], "independent-design-B-seed-4409",
         "Size-only null ratio 0.280 [0.233, 0.334] over 2,000 permutations. Observed 0.094 sits "
         "far below it, p=0.0000. The attenuation is polarity, not count.", 8)
    edge(N["CTRL_SIZE"], N["C_POL"], "acquits", 8, None,
         "the named strongest confound ran and did not explain the effect")
    edge(N["CTRL_SIZE"], N["C_POL"], "confounds", 3, None,
         "recorded as the alternative it was, so the graph shows what was ruled out")

    N["C_SIGNFLIP"] = node(
        "the-full-vs-core-verdict-depends-on-the-analysts-sign-treatment", "my_claim",
        "Whether coval_full beats coval_core at reproducing human world rankings is decided by how "
        "the analyst treats the 25.6% of criteria carrying negative ratings. Sign-ignored: core "
        "wins. Sign-corrected: full wins. Both are true statements about the same release.",
        "polarity", 8, "settled")
    evid(N["C_SIGNFLIP"], "r127-arms",
         "full sign-ignored 0.5941 [0.5827,0.6051]; full all-negatives-flipped 0.6806 "
         "[0.6709,0.6901]; core 0.6604 [0.6502,0.6706]; 80,542 pooled human ordered pairs.", 8)
    evid(N["C_SIGNFLIP"], "independent-design-A-seed-8101",
         "Exact decomposition: total(signed-core)=+0.0256, sign(signed-uniform)=+0.0919, "
         "compile(uniform-core)=-0.0663. Sham permuting which criterion gets which sign, "
         "magnitudes fixed, 500 reps: observed sits ~23 sd outside.", 8)
    evid(N["C_SIGNFLIP"], "independent-design-B-seed-4409",
         "Five treatments: UNWT 0.590, SIGNED 0.683, DROP 0.648, FLIP 0.678, MAGSHAM 0.601. "
         "SIGNED-MAGSHAM=+0.082 [+0.072,+0.091] isolates the sign from the weighting. Dose "
         "response across quartiles of a prompt's negative share: +0.044 -> +0.147.", 8)
    edge(N["C_SIGNFLIP"], N["INSTR"], "depends_on", 8, None, None)

    N["C_CORE_EQ_DROP"] = node(
        "core-is-indistinguishable-from-dropping-the-negatives", "my_claim",
        "coval_core's concordance is statistically indistinguishable from simply deleting every "
        "negatively-rated criterion from coval_full and averaging what remains.",
        "substitution", 6, "partial")
    evid(N["C_CORE_EQ_DROP"], "independent-design-A-seed-8101",
         "posonly 0.6606 vs core 0.6604, difference +0.0003 [-0.006,+0.007], p=0.92 on pooled "
         "concordance and p=0.71 on per-prompt Spearman. FLAGGED BY ITS OWN AUTHOR AS POST-HOC "
         "AND EXPLORATORY, outside the corrected family. One design, one seed, not replicated.", 5)
    evid(N["C_CORE_EQ_DROP"], "independent-design-A-seed-8101-negation-markers",
         "Negation markers appear in 13.0% of negatively-rated full criteria against 12.8% of "
         "positive ones, so core is not reaching the same place by rephrasing them as "
         "prohibitions.", 6)
    edge(N["C_CORE_EQ_DROP"], N["K13-sham-ladder"], "supports", 6, None, None)
    edge(N["C_CORE_EQ_DROP"], N["A1"], "overturns", 5, None,
         "a zero-LLM rule reproduces the compiler on this axis -- but at D5, one design")

    N["C_COLLECTIVE"] = node(
        "a-negative-signs-value-rises-with-the-number-of-raters-behind-it", "my_claim",
        "Per criterion flipped, the concordance gained from a negative sign is monotone in the "
        "evidential basis of that sign: multi-rater and bootstrap-stable 0.0496 per 1000, middle "
        "0.0419, unstable 0.0340, single-rater 0.0215. Single-rater signs fall BELOW a "
        "count-matched draw from the whole negative pool (z=-5.58); stable ones sit above it "
        "(z=+4.03).",
        "aggregation", 6, "partial",
        {"outstanding": "magnitude and discriminability matching between STABLE and SINGLE was "
                        "added after the first run and has not yet reported"})
    evid(N["C_COLLECTIVE"], "r127-whose-sign",
         "SINGLE k=2975 gain +0.06394 (+0.0215/1k, z=-5.58); STABLE k=336 +0.01665 (+0.0496/1k, "
         "z=+4.03); MIDDLE k=75 (+0.0419/1k, z=+1.15); UNSTABLE k=444 (+0.0340/1k, z=+2.14). "
         "Positive control flip-all vs flip-none +0.08644 [+0.07711,+0.09586]. Placebo flipping "
         "the empty set reproduces the unflipped arm at |diff|=0.00e+00.", 6)
    edge(N["C_COLLECTIVE"], N["A3"], "supports", 6, None,
         "the sign's value tracks collective backing, which is what A3 needs")
    edge(N["C_COLLECTIVE"], N["C_SIGNFLIP"], "refines", 6, None,
         "locates where in the negative block the sign-flip advantage lives")
    edge(N["F_SINGLE"], N["C_COLLECTIVE"], "depends_on", 8, None,
         "the blocks exist only because the rater-count distribution is bimodal")

    N["CONF_MAG"] = node(
        "confound-stability-is-magnitude", "control",
        "A sign is bootstrap-stable partly BECAUSE its magnitude is large: mean -8 survives "
        "resampling where mean -0.7 does not. The per-criterion ordering STABLE > SINGLE could "
        "therefore be an effect of |mean rating| and of across-response discriminability rather "
        "than of how many people backed the sign.",
        "aggregation", None, "open")
    edge(N["CONF_MAG"], N["C_COLLECTIVE"], "confounds", 7, None,
         "named before the control was written; the control is queued, not reported")

    N["C_INSTR_CLEAN"] = node(
        "the-judges-implementation-carries-no-established-defect", "my_claim",
        "Three implementation-level attacks on the satisfaction judge -- wrong Yes/No token ids, "
        "right-truncation cutting the read position, and the 1400-character reply cut -- were run "
        "against the object and all three failed. This clears the judge's CODE. It says nothing "
        "about the judge's BEHAVIOUR, which no second judge has ever cross-checked.",
        "instrument", 8, "settled")
    for k in ("defect-yes-no-token-id", "defect-right-truncation-1024",
              "defect-1400-char-reply-cut"):
        edge(N[k], N["C_INSTR_CLEAN"], "supports", 8, None, "an attack that failed")
    edge(N["C_INSTR_CLEAN"], N["INSTR"], "supports", 8, None, None)
    edge(N["K16-single-judge-gauge"], N["C_INSTR_CLEAN"], "attacks", None, None,
         "the open knife: code being clean is not behaviour being valid")
    evid(N["C_INSTR_CLEAN"], "session-direct-check-2026-07-30",
         "Three attacks run against the object, three failures: ' Yes'->[7179] / ' No'->[2233] "
         "single and distinct; max prompt 537 tokens against a 1024 cap; 6 of 3,872 replies over "
         "the 1400-character cut. Each is an acquittal of the CODE and of nothing else.", 8)

    build_triple_blind(N)
    return N


# ---------------------------------------------------------------------------------------------
# the triple-blind layer: for each knife, two clean-context designs that were never told the
# algorithm, plus mine. Their agreement is only worth something where the designs DIFFER, so the
# graph records the estimand each one chose, not just the number it returned.
# ---------------------------------------------------------------------------------------------
def build_triple_blind(N):
    # ---- K1, three designs -------------------------------------------------------------------
    evid(N["C_POL"], "independent-design-A-seed-8101",
         "A third estimand again: ratio of |corr(neg-component, core)| to |corr(pos-component, "
         "core)| = 0.20 [0.150, 0.249]. Size-matched subsample 0.235 (5 seeds, sd 0.002); "
         "split-half reliability correction (rel_pos 0.86, rel_neg 0.69) 0.222 -- both controls "
         "move the estimate UP, not down. r_pos +0.892, r_neg -0.178 [-0.222,-0.133]. "
         "The three designs return 0.094 / 0.094 / 0.20 because they estimate different "
         "quantities; the direction, not the magnitude, is what replicates.", 8)

    N["C_FLIP_MEASURED"] = node(
        "the-flip-reading-of-a-negative-rating-is-measured-not-assumed", "my_claim",
        "The premise all three K1 designs share -- that a negative mean rating means satisfying "
        "the criterion is bad, so satisfaction should be read as 1-v -- was tested rather than "
        "assumed. Scoring responses on negatively-rated criteria FLIPPED predicts held-out human "
        "world rankings at 61.0%; UNFLIPPED at 39.0%. Text inspection agrees: the negatively-rated "
        "criteria are affirmative descriptions of a behaviour ('Invents fake sources', 'Use a "
        "violent tone'), not prohibitions, so high satisfaction means the response did the thing.",
        "polarity", 8, "settled")
    evid(N["C_FLIP_MEASURED"], "independent-design-A-seed-8101",
         "Sign-convention check: flipped 61.0% [0.599,0.622] vs unflipped 39.0% against chance 50%.",
         8)
    evid(N["C_FLIP_MEASURED"], "session-text-inspection-2026-07-30",
         "20 randomly drawn negatively-rated criteria read directly; none is phrased as a "
         "prohibition. Independently corroborated: negation markers appear at 13.0% in negative "
         "criteria against 12.8% in positive ones.", 7)
    edge(N["C_FLIP_MEASURED"], N["C_POL"], "supports", 8, None,
         "the shared premise of all three designs, promoted from assumption to measurement")
    edge(N["C_FLIP_MEASURED"], N["C_SIGNFLIP"], "supports", 8, None, None)

    # ---- K3, and why the two designs disagree ------------------------------------------------
    N["C_FLAT"] = node(
        "core-behaves-as-a-flat-summary-with-a-small-real-weighted-residual", "my_claim",
        "Regressing core's within-prompt-centred score on full's flat average and on the part of "
        "full's importance-weighted average orthogonal to it gives b1 = 0.861 [0.848, 0.872] and "
        "b2 = 0.084 [0.055, 0.112] in standardised units: core is overwhelmingly a flat summary "
        "with a statistically real but structurally minor weighted component, 62% of the ceiling "
        "the noise level permits. Compilation discards most of the importance structure, not all.",
        "weighting", 7, "partial")
    edge(N["C_FLAT"], N["A6"], "refines", 7, None,
         "the ratings carry information; the compilation mostly does not carry it forward")
    edge(N["C_FLAT"], N["A1"], "overturns", 7, None, "faithfulness on the weighting axis fails")
    edge(N["K3-weight-discard"], N["C_FLAT"], "supports", 7, None, None)
    evid(N["C_FLAT"], "independent-design-A-seed-8101",
         "b1 std 0.861, b2 std 0.084, dominance ratio 0.097; high-dispersion tertile b2 = 0.122 "
         "[0.075,0.168], larger where weights actually vary. Length covariate moves b2 by 0.0002. "
         "Author disclosed that its 0.30 dominance bar was chosen post-hoc after both terms "
         "cleared significance -- the ratio 0.097 is far from any defensible co-equal line, but "
         "the threshold itself was not pre-registered.", 6)

    N["C_COLLINEAR"] = node(
        "weighted-and-unweighted-full-are-near-collinear-in-this-release", "fact",
        "Across a prompt's four responses, the importance-weighted and the equal-weight summaries "
        "of coval_full correlate at mean r = 0.957, median 0.992, p10 0.902. Averaging over ~15 "
        "criteria washes out almost everything the -10..+10 magnitudes could change, so any design "
        "that asks 'does core behave weighted or unweighted' by comparing response-level aggregates "
        "is near-unidentifiable before it starts.",
        "weighting", 8, "settled")
    evid(N["C_COLLINEAR"], "independent-design-B-seed-4409",
         "Measured while diagnosing its own FAILED positive control: a synthetic core built 100% "
         "from the weighted formula returned delta = +0.036 against a pre-registered bar of 0.15. "
         "The design returned UNVERIFIED rather than reporting the near-zero as a null.", 8)
    edge(N["C_COLLINEAR"], N["C_FLAT"], "supports", 7, None,
         "explains why design A had to orthogonalise, and why design B could not resolve at all")

    N["UNVERIF_K3B"] = node(
        "K3-design-B-returned-UNVERIFIED-not-a-null", "control",
        "The second K3 design's positive control failed, so its near-zero result is silence rather "
        "than acquittal and may never be folded in with design A's as agreement. Recorded so that "
        "no later reader counts two designs where there is one measurement and one refusal.",
        "weighting", None, "open")
    edge(N["UNVERIF_K3B"], N["C_FLAT"], "confounds", 4, None,
         "not a rival explanation -- a standing note that the replication count here is ONE")

    # ---- K13, the ladder ---------------------------------------------------------------------
    N["C_LADDER"] = node(
        "a-zero-LLM-importance-sort-matches-the-compiler", "my_claim",
        "At a matched budget of four criteria, coval_core scores 0.6563 pairwise concordance and a "
        "deterministic sort of the release's own human importance ratings scores 0.6589-0.6600 -- "
        "statistically indistinguishable, and numerically ahead. Core does beat selection rules "
        "that cannot see the ratings: random-4 by +1.4pp and a text-only mechanical rule by "
        "0 to +2.0pp. So compilation adds real work over a blind selector and no measurable work "
        "over a free sort of data already collected.",
        "substitution", 7, "partial")
    edge(N["C_LADDER"], N["A1"], "overturns", 7, None,
         "the compiler's output is reachable without the compiler")
    edge(N["K13-sham-ladder"], N["C_LADDER"], "supports", 7, None, None)
    evid(N["C_LADDER"], "independent-design-A-seed-8101",
         "core 0.6563; top-importance-4 0.6589 (delta -0.26pp, perm p 0.575 Holm 1.0); "
         "mechanical-4 0.6587 (delta -0.24pp, p 0.627); random-4 0.6422 (delta +1.40pp, Holm "
         "0.0006); all-full 0.6769; placebo 0.5006. Its CV search for the best mechanical rule "
         "converged on alpha ~ 1.0 in 40 of 50 folds -- inter-rater agreement adds nothing beyond "
         "raw importance magnitude.", 7)
    evid(N["C_LADDER"], "independent-design-B-seed-4409",
         "core 0.6563 (identical to design A to four decimals, on an independently written "
         "harness); top-importance-4 0.65998 (delta -0.37pp, Holm 0.42); random-4 +1.38pp; "
         "mechanical-4 +1.98pp (Holm 0.0012); worst-importance-4 +5.10pp. Diverges from design A "
         "on mechanical-4 -- distinguishable there, not here -- because the two built different "
         "mechanical rules. Unoriented sensitivity: top-4 without the free sign information falls "
         "to 0.5606, 9.6pp BELOW core.", 7)

    # ---- K18: the confound two independent designs found and I did not -----------------------
    N["K18"] = node(
        "K18-judge-decisiveness-tracks-text-style", "knife",
        "coval_core's criteria are the shortest text of any arm and the judge is most decisive on "
        "them. If terse, LLM-authored phrasing makes this judge more confident, part of core's "
        "advantage over every full-derived arm is style rather than content -- and the effect runs "
        "the right way to manufacture exactly the advantage the release claims.",
        "instrument", None, "open")
    edge(N["K18"], N["INSTR"], "attacks", None, None, None)
    edge(N["K18"], N["C_LADDER"], "confounds", 6, None,
         "found independently by both K13 designs; neither could remove it without an LLM rewrite")
    edge(N["K18"], N["C_POL"], "confounds", 5, None,
         "the same style gradient would inflate core's loading on any component")
    evid(N["K18"], "independent-design-A-seed-8101",
         "core criteria mean 88 characters against 98 for full; judge saturation 0.437 for core "
         "against 0.419. Measured, named before running, not removable within the design's "
         "constraints.", 7)
    evid(N["K18"], "independent-design-B-seed-4409",
         "core 88 characters against 96-104; mean |sat-0.5| = 0.2186, rank 1 of 13 arms; "
         "corr(length, decisiveness) = -0.95; cross-arm corr(decisiveness, accuracy) = +0.29.", 7)


def attach_round_artifacts():
    """Every round artifact in the repo becomes discoverable evidence, so a claim can never quietly
    outlive the round that produced it. Only rounds whose JSON carries a `conclusion` are linked;
    the rest are listed by the audit query as artifacts with no claim attached."""
    n = 0
    for p in sorted(_ROOT.glob("[0-9][0-9]_*/r*/results/*.json")):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        if not isinstance(d, dict) or "conclusion" not in d:
            continue
        slug = p.parent.parent.name
        rows = q("SELECT id FROM evidence WHERE experiment=%s", (slug,))
        if not rows:
            q("INSERT INTO evidence(node_id,experiment,finding,d_level) VALUES "
              "(NULL,%s,%s,NULL)", (slug, (d.get("conclusion") or "")[:4000]))
            n += 1
    return n


def audit():
    print("\n  ── the chain ──")
    for r in q("""SELECT n.kind, n.name, coalesce(n.status,'-'), coalesce(n.d_level::text,'-'),
                         (SELECT count(*) FROM evidence e WHERE e.node_id=n.id),
                         (SELECT count(*) FROM edge x WHERE x.dst=n.id)
                  FROM node n ORDER BY n.kind, n.name"""):
        print(f"  {r[0]:<18}{r[1]:<62}{r[2]:<9}D{r[3]:<3}ev={r[4]:<3}in={r[5]}")

    print("\n  ── claims asserted with NO evidence row (standing on nothing measured) ──")
    bad = q("""SELECT n.name FROM node n LEFT JOIN evidence e ON e.node_id=n.id
               WHERE n.kind IN ('my_claim','fact') AND n.status IN ('settled','partial')
               GROUP BY n.name HAVING count(e.id)=0""")
    print("  " + ("\n  ".join(r[0] for r in bad) if bad else "(none)"))

    print("\n  ── claims with an OPEN confound edge pointing at them ──")
    for r in q("""SELECT d.name, s.name, e.d_forward FROM edge e
                  JOIN node s ON s.id=e.src JOIN node d ON d.id=e.dst
                  WHERE e.kind='confounds' AND s.status IN ('open','partial')"""):
        print(f"  {r[0]}  <- {r[1]}  (d_forward {r[2]})")

    print("\n  ── what falls if the instrument falls ──")
    for r in q("""SELECT s.name, s.d_level FROM edge e JOIN node s ON s.id=e.src
                  JOIN node d ON d.id=e.dst
                  WHERE e.kind='depends_on' AND d.name='a04-satisfaction-tensor'"""):
        print(f"  {r[0]}  (D{r[1]})")

    print("\n  ── round artifacts in the repo with no claim attached ──")
    orph = q("""SELECT experiment FROM evidence WHERE node_id IS NULL ORDER BY experiment""")
    print(f"  {len(orph)} rounds carry a conclusion but no edge into the chain.")
    for r in orph[:8]:
        print(f"    {r[0]}")
    if len(orph) > 8:
        print(f"    ... and {len(orph)-8} more")


if __name__ == "__main__":
    N = build()
    k = attach_round_artifacts()
    print(f"built {len(N)} nodes; attached {k} new round artifacts")
    audit()
    sys.exit(0)
