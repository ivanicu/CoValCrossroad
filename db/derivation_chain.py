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
    # The separator must NOT be a character Python calls whitespace. \x1f is: Python treats the
    # C0 separators \x1c-\x1f as whitespace, so stdout.strip() silently ate the trailing empty
    # field of whichever row happened to land last, and exactly one row in sixty-two came back with
    # four columns instead of five. It surfaced as an unpack error in a downstream generator, which
    # is lucky -- a tuple one short is otherwise a value shifted into the wrong name.
    SEP = "\x01"
    p = subprocess.run(["psql", "-d", DB, "-t", "-A", "-F", SEP, "-v", "ON_ERROR_STOP=1",
                        "-c", payload], capture_output=True, text=True, env=env)
    if p.returncode != 0:
        raise RuntimeError(f"psql failed:\n{payload}\n{p.stderr}")
    tags = {"SET", "BEGIN", "COMMIT", "DELETE", "UPDATE", "INSERT"}
    out = []
    for l in p.stdout.split("\n"):
        l = l.rstrip("\r")
        if not l or (SEP not in l and l.split(" ")[0] in tags):
            continue
        out.append(tuple(l.split(SEP)))
    return out


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
        "than of how many people backed the sign. RAN, and the prediction was BACKWARDS: SINGLE "
        "carries |mean| 7.26 against STABLE's 3.92, because a lone rater who marks a criterion "
        "negative uses the scale's -10 ceiling while averaging ten raters pulls toward the middle. "
        "Magnitude works against the finding rather than explaining it.",
        "aggregation", 8, "settled")
    evid(N["CONF_MAG"], "r127-whose-sign",
         "STABLE per 1000 = +0.0496 against a magnitude- and discriminability-matched SINGLE draw "
         "at +0.0221 (sd 0.0009 over 20 seeds), z = +29.48. Covariate means: SINGLE |mean rating| "
         "7.26 / discriminability 0.134; STABLE 3.92 / 0.179. The evidential-basis reading survives "
         "matching on both.", 8)
    edge(N["CONF_MAG"], N["C_COLLECTIVE"], "acquits", 8, None,
         "named before the control was written, then run in the same round and refuted")
    edge(N["CONF_MAG"], N["C_COLLECTIVE"], "confounds", 2, None,
         "kept at low confidence so the ruled-out alternative stays in the audit trail")

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
    build_wave2(N)
    N.update(build_retractions(N))
    return N


def build_retractions(N):
    """This project's own retracted claims, as first-class REFUTED nodes.

    The graph's first shape audit showed 17 my_claims of which 0 were refuted, while 5 of 5 alleged
    defects were. That is not a record of a careful project; it is an ontology that cannot express
    its own retractions. `person-level-harm-COUNTS-are-withdrawn` was entered as a SETTLED claim
    about a withdrawal, so the thing withdrawn had no node and nothing pointed at it. A reader --
    including a later me -- would see a campaign that never got anything wrong.

    Each retracted claim gets a node with status='refuted' and an `overturns` edge from whatever
    killed it, so the kill is queryable and the corrected number travels with it."""
    R = {}
    R["r116_harm"] = node(
        "RETRACTED-12.46pct-of-people-are-harmed-by-compilation", "my_claim",
        "Rounds r116 through r119 reported that 12.46% of people suffer a concordance loss above "
        "0.01 under compilation, and built a multidimensional sacrifice programme on counts of that "
        "shape. The number was computed against ONE baseline (full_equal, which reads a criterion "
        "rated -10 as if satisfying it were good) and with NO within-person floor. Both defects are "
        "individually fatal to it.",
        "redistribution", 3, "refuted")
    evid(R["r116_harm"], "r123-the-baseline-was-crippled",
         "Against the sign-corrected baseline the same quantity is 57.07%, not 12.46% -- the "
         "convention, not the world, was choosing the number.", 8)
    evid(R["r116_harm"], "r131-who-is-served",
         "Between-person spread 0.06870 against a within-person split-half floor of 0.06130 "
         "(equal) and 0.05348 against 0.05062 (signed): neither clears. The count was a statement "
         "about how many prompts each person happened to see.", 8)
    if "R_HARM_COUNTS" in N:
        edge(N["R_HARM_COUNTS"], R["r116_harm"], "overturns", 8, None,
             "the floor the original rounds never had")

    R["r117_prompt"] = node(
        "RETRACTED-17.05pct-prompt-level-harm", "my_claim",
        "The prompt-level companion to the person-level count, 17.05% against full_equal. It "
        "inherits the baseline defect exactly (35.54% against full_signed) and was never given a "
        "within-prompt floor of its own.",
        "redistribution", 3, "refuted")
    evid(R["r117_prompt"], "r123-the-baseline-was-crippled",
         "17.05% -> 35.54% purely by correcting how a negative rating is read.", 8)
    if "R_HARM_COUNTS" in N:
        edge(N["R_HARM_COUNTS"], R["r117_prompt"], "overturns", 7, None,
             "the same missing floor, one level up; the audit caught this node standing with "
             "evidence and no incoming kill edge")

    R["nat_med"] = node(
        "RETRACTED-the-natural-mediator-reading-of-the-arm-gap", "my_claim",
        "An earlier reading treated core's advantage over full as evidence that compilation adds "
        "information. Three independent designs now put core statistically level with a "
        "deterministic sort of the release's own importance ratings, and the advantage itself is "
        "conditional on handing full its worst configuration.",
        "substitution", 3, "refuted")
    if "C_LADDER" in N:
        edge(N["C_LADDER"], R["nat_med"], "overturns", 7, None,
             "a zero-LLM sort reaches the same place")
    if "C_SIGNFLIP" in N:
        edge(N["C_SIGNFLIP"], R["nat_med"], "overturns", 8, None,
             "the sign convention decides the direction of the gap")

    R["gradient"] = node(
        "RETRACTED-the-consensus-gradient-as-first-reported", "my_claim",
        "Reported as partial r +0.099 at p 0.0025 without naming a baseline and without a "
        "predictability control. Both were wrong: adding the person's own best-arm accuracy kills "
        "it entirely under full_equal (-0.003, p 0.92) and attenuates it to +0.074 (p 0.0205) "
        "under full_signed, and an independent design showed the ratings are not a personal-values "
        "proxy at all, so even the surviving version may be about expression rather than values.",
        "redistribution", 2, "refuted")
    if "C_CONSENSUS_GRADIENT" in N:
        edge(N["C_CONSENSUS_GRADIENT"], R["gradient"], "overturns", 7, None,
             "the same round, one control later")
    if "C_SHARED_NOT_PERSONAL" in N:
        edge(N["C_SHARED_NOT_PERSONAL"], R["gradient"], "overturns", 7, None,
             "and the covariate is not the thing it was read as")
    return R


def build_wave2(N):
    """K18 and K8, two clean-context designs each, plus the corrections they forced on me."""

    # ---- K18 dies, and takes one of my own reported numbers with it --------------------------
    N["F_ECOLOGICAL"] = node(
        "fact-the-length-decisiveness-correlation-was-ecological", "fact",
        "The -0.95 correlation between criterion text length and judge decisiveness, which two "
        "K13 designs reported and which I passed on as K18's mechanism, is an ARM-LEVEL "
        "correlation over roughly thirteen points, each an arm's mean. At the level the mechanism "
        "would have to operate -- the individual criterion -- it is -0.036 over 14,984 instances "
        "and -0.037 over 18,811, i.e. r-squared about 0.001. An ecological correlation was read as "
        "an individual one, by them and then by me.",
        "instrument", 8, "settled")
    evid(N["F_ECOLOGICAL"], "independent-design-K18-A-seed-8101",
         "Within-arm criterion-level rho = -0.036 (n=14,984), partial rho = -0.052 controlling a "
         "hedge/conjunction/comma density proxy for content complexity.", 8)
    evid(N["F_ECOLOGICAL"], "independent-design-K18-B-seed-4409",
         "Per-instance rho = -0.037 (n=18,811), reached independently and independently diagnosed "
         "as an arm-level artefact of the project's wider battery of arms.", 8)

    N["C_CONTENT_NOT_STYLE"] = node(
        "cores-advantage-is-content-and-the-style-mechanism-runs-backwards", "my_claim",
        "Holding authorship and criterion count fixed and varying only text length inside "
        "coval_full, the SHORTER four-criterion subset scores WORSE, not better: -0.0287 "
        "[-0.0424, -0.0149]. Core beats the terse human subset by +0.1009 [+0.0892, +0.1126], more "
        "than it beats full at large. Controlling for log length does not shrink core's advantage "
        "at all -- the style-explained share is 1.035 [1.022, 1.050], i.e. slightly negative. And "
        "core (88.2 chars, decisiveness 0.219) is MORE decisive than a 65.1-char human subset "
        "(0.211), so decisiveness does not track brevity.",
        "instrument", 8, "settled")
    evid(N["C_CONTENT_NOT_STYLE"], "independent-design-K18-A-seed-8101",
         "short4 - long4 = -0.0287, Wilcoxon p=3.1e-5, survives BH over 6 cells; core - short4 = "
         "+0.1009 (rank-biserial +0.50); style-attributable share -26% vs sham and -43% vs long4, "
         "both NEGATIVE. Label-shuffle negative control returns 0.4992; list-position placebo "
         "+0.0009 (p=0.78) despite a real length gap.", 8)
    evid(N["C_CONTENT_NOT_STYLE"], "independent-design-K18-B-seed-4409",
         "r_style = 1.035 [1.022, 1.050] over 5 seeds x 2000 draws; length-matched tercile (63.9 "
         "chars, shorter than core's 88.2) still trails core by -0.081 [-0.088,-0.073], which is "
         "117% of the raw gap. All 6 pre-registered tests reject under Holm.", 8)
    edge(N["F_ECOLOGICAL"], N["C_CONTENT_NOT_STYLE"], "supports", 8, None,
         "the mechanism K18 needed does not exist at the criterion level")
    if "K18" in N:
        edge(N["C_CONTENT_NOT_STYLE"], N["K18"], "overturns", 8, None,
             "two independent designs, both CONFIRMED, and the direction is reversed")
        q("UPDATE node SET status='refuted' WHERE id=" + str(N["K18"]))
        # the confound edges K18 held over two claims are now discharged, and the discharge is
        # recorded as its own control rather than by deleting the edge -- a ruled-out alternative
        # is part of the audit trail, not something to erase.
        for tgt in ("C_LADDER", "C_POL"):
            if tgt in N:
                edge(N["C_CONTENT_NOT_STYLE"], N[tgt], "acquits", 8, None,
                     "the style confound was named, run, and refuted in the same iteration")

    # ---- K8: the criterion-level sacrifice ---------------------------------------------------
    N["F_VERBATIM"] = node(
        "fact-7.8pct-of-core-criteria-are-verbatim-copies", "fact",
        "298 of coval_core's 3,828 criteria (7.8%) match a coval_full criterion exactly after "
        "normalisation. The release carries no provenance link, but that subset IS provenance for "
        "7.8% of the compilation, and it makes one proxy-free retention test possible.",
        "provenance", 9, "settled")
    evid(N["F_VERBATIM"], "independent-design-K8-B-seed-4409",
         "298/3828 exact-text matches after normalisation; the remaining 92% are paraphrased or "
         "synthesised and are not recoverable by reading text.", 9)

    N["F_RATER_GAP"] = node(
        "fact-no-criterion-has-two-or-three-raters", "fact",
        "The rater-count distribution has a literal hole: 63.5% of criteria carry exactly one "
        "rating, ZERO carry two or three, about 2.4% carry four to nine, and 34.0% carry ten or "
        "more. My earlier statement that 0.2% lie between counted only n=2 and n=3 and understated "
        "the 4-9 band by an order of magnitude. The jump from 1 straight to 4 is a protocol "
        "signature, not a sampling curve: two collection regimes were glued together.",
        "aggregation", 9, "settled")
    evid(N["F_RATER_GAP"], "independent-design-K8-B-seed-4409",
         "Verified independently while checking the facts it was handed rather than taking them "
         "from the brief -- which is why the understatement was caught.", 9)
    if "F_SINGLE" in N:
        edge(N["F_RATER_GAP"], N["F_SINGLE"], "refines", 9, None,
             "corrects the size of the middle band without touching the bimodality")

    N["C_MAJORITY_CAPTURE"] = node(
        "when-a-contested-criterion-survives-the-majority-captures-it", "my_claim",
        "Among 4,127 coval_full criteria on which raters split by sign, the ones whose satisfaction "
        "fingerprint survives detectably into the compiled arm side with the rater MAJORITY 88.7% "
        "of the time [86.7%, 90.7%], and the rate scales monotonically with how lopsided the split "
        "is: 58.1% at the weakest splits, 98.1% at the strongest. The failure mode is not that "
        "dissent is erased at random -- it is that the majority takes the compiled criterion.",
        "redistribution", 7, "partial")
    evid(N["C_MAJORITY_CAPTURE"], "independent-design-K8-A-seed-8101",
         "997 majority-side / 127 minority-side / 3,003 washed out; binomial p=5.7e-168; "
         "prompt-clustered bootstrap CI [86.7%, 90.7%]; stable at rater thresholds 5/10/15 "
         "(88.1% / 88.7% / 88.6%). Positive control on 304 exact-text matches: median r=0.866 "
         "against a null median of 0.007.", 7)
    edge(N["C_MAJORITY_CAPTURE"], N["A3"], "attacks", 7, None,
         "a standard that reliably resolves splits toward the majority is an aggregation rule, "
         "not a representation of the participants")

    N["C_CONTESTED_DROPPED"] = node(
        "whether-disagreement-ITSELF-predicts-being-dropped-is-unsettled", "my_claim",
        "Both K8 designs find the raw association -- contested criteria are retained far less "
        "often. They DISAGREE on whether it survives adjustment for rating magnitude, and the "
        "disagreement is a design difference, not noise: A regresses a continuous matchability "
        "score linearly on |mean rating| and gets +0.003 [-0.019, 0.025], a magnitude-mediated "
        "null; B fits a logistic on a thresholded nearest-neighbour retention indicator with "
        "standardised |mean| and log rater count and gets OR 0.354 [0.247, 0.493]. B additionally "
        "has a proxy-free arm A did not use as an outcome: among the 286 multi-rated criteria KNOWN "
        "to have been copied verbatim into core, 11.2% are contested against a 40.9% population "
        "base rate, z=-10.2 -- but that arm is unadjusted for magnitude, which is exactly the "
        "quantity in dispute.",
        "redistribution", 4, "partial",
        {"resolution": "an adjusted analysis on the verbatim-copy subset would settle it; neither "
                       "design ran one"})
    evid(C := N["C_CONTESTED_DROPPED"], "independent-design-K8-A-seed-8101",
         "Raw -0.098 [-0.117,-0.079]; magnitude-adjusted +0.003 [-0.019,0.025]; "
         "magnitude-quintile-matched +0.008 with no consistent sign; robust at rater thresholds "
         "5/10/15. Verdict UNVERIFIED on its own pre-registered bar.", 5)
    evid(C, "independent-design-K8-B-seed-4409",
         "Adjusted OR 0.354 [0.247,0.493], retention 2.6% vs 13.9% (-11.3pp); unadjusted OR 0.168, "
         "so the magnitude confound is real and large but the effect survives it; stable in both "
         "rater-count regimes (4-9: 0.387; >=10: 0.356); mismatched-prompt placebo returns "
         "OR ~0.82, near null. Verdict CONFIRMED.", 6)
    edge(N["F_VERBATIM"], C, "supports", 6, None, "the proxy-free arm exists only because of it")

    N["C_ADJUDICATED"] = node(
        "disagreement-itself-costs-a-criterion-its-place-on-ground-truth", "my_claim",
        "The dispute is settled on the one ground truth the release offers. 365 of 3,899 coval_core "
        "criteria (9.4%) have a verbatim twin in coval_full, so for those retention is a fact and "
        "not a proxy. Among the 5,564 full criteria with at least four raters, 10.9% of the copied "
        "are contested against 43.0% of the not-copied; adjusted for |mean rating|, log rater count "
        "and the criterion's own across-response discriminability, contested carries OR 0.3164 "
        "[0.1958, 0.4786]. The release's own documented selection signal moves as it must "
        "(|mean rating| OR 1.5379 [1.3188, 1.8055]), so the contested coefficient is a measurement "
        "and not a silence. Neither earlier design ran this: one had ground truth but no "
        "adjustment, the other had adjustment but only a proxy.",
        "redistribution", 8, "settled")
    evid(N["C_ADJUDICATED"], "r132-verbatim-adjudication",
         "Logistic, cluster-bootstrapped over 986 prompts, 4,000 fits across 5 seeds whose mean "
         "contested coefficients agree to three decimals (-1.1569 to -1.1627). Within-prompt "
         "permutation of the outcome puts the coefficient at -0.0618 (sd 0.1461) and the observed "
         "value at z = -7.46. STRUCTURAL LIMIT stated in the artifact: verbatim copying is ONE "
         "retention pathway and 92% of core is rewritten, so a pathway shift would read as a drop "
         "-- a limit that cuts identically for both disputants.", 8)
    edge(N["C_ADJUDICATED"], C, "refines", 8, None,
         "the unsettled claim is settled in design B's direction, on ground truth rather than "
         "either proxy")
    edge(N["C_ADJUDICATED"], N["A3"], "overturns", 7, None,
         "an aggregation that systematically drops the criteria people disagree about is not "
         "producing a collective standard; it is producing the uncontested residue")
    if "C_MAJORITY_CAPTURE" in N:
        edge(N["C_ADJUDICATED"], N["C_MAJORITY_CAPTURE"], "supports", 7, None,
             "dropped when contested, and captured by the majority when retained")

    N["D_DEAD_COVARIATE"] = node(
        "defect-a-covariate-i-claimed-to-adjust-for-was-silently-all-zero", "defect",
        "The adjudication's first run looked the satisfaction tensor up by CONVERSATION id while "
        "the tensor is keyed by PROMPT id, so every discriminability value was 0.0 and an "
        "adjustment I had stated in the docstring was never made. The verdict did not change when "
        "fixed (OR 0.3083 -> 0.3164), but the claim 'adjusted for discriminability' was false as "
        "printed. The tell was a reported p of 2.0000 -- not a small p, an IMPOSSIBLE one, from "
        "2*min(a,b) with one side exactly 1.0 on a degenerate constant column.",
        "provenance", 9, "refuted")
    evid(N["D_DEAD_COVARIATE"], "session-self-audit-2026-07-30",
         "Found by reading an out-of-range p-value rather than by the result looking wrong; the "
         "result looked fine. A p above 1 is a free assertion that a column is dead.", 9)
    edge(N["D_DEAD_COVARIATE"], N["C_ADJUDICATED"], "refines", 9, None,
         "the defect was in the same round and is recorded beside its own correction")

    # ---- K5: the north star, and the retraction it forces ------------------------------------
    N["R_HARM_COUNTS"] = node(
        "person-level-harm-COUNTS-are-withdrawn", "my_claim",
        "Rounds r116-r119 reported counts of harmed people under compilation. Re-measured with a "
        "within-person floor -- split each annotator's own prompt set in half at random and compute "
        "the identical gain on each half -- the between-person spread does NOT exceed that floor "
        "under either baseline: 0.06870 against 0.06130 (full_equal), 0.05348 against 0.05062 "
        "(full_signed). '12.8% of people are harmed' and '59.4% of people are harmed' are "
        "statements about how many prompts each person happened to see, not about people. Every "
        "person-level sacrifice COUNT this project has published on this data is withdrawn.",
        "redistribution", 8, "settled")
    evid(N["R_HARM_COUNTS"], "r131-who-is-served",
         "975 annotators with >=4 prompts and >=8 ordered pairs, 15,103 person-prompt cells, 200 "
         "random half-splits per person. Mean gain +0.06809 [+0.06373,+0.07242] against full_equal "
         "and -0.01887 [-0.02218,-0.01545] against full_signed; worst decile -0.04907 and -0.11114. "
         "WORLD: W-UNIFORM under the pre-registered 1.5x-floor rule.", 8)

    N["C_CONSENSUS_GRADIENT"] = node(
        "core-serves-the-people-furthest-from-consensus-relatively-better", "my_claim",
        "The person-level spread is noise-dominated, but it is not structureless: if it were, no "
        "covariate could predict it. Two do, after partialling out a person's prompt count -- the "
        "noise-shrinkage confound, named before the control ran and only weakly related to either "
        "covariate. Against the signed baseline, where the aggregate favours full, a person's "
        "deviation from their peers' rating means predicts a HIGHER gain (partial r +0.099, "
        "permutation p 0.0025) and the number of criteria they rated predicts a LOWER one "
        "(-0.129, p 0.0000). full's ratings encode the majority's view, so the ratings-free "
        "compiled arm is relatively kinder to the people furthest from it. SECOND CONTROL, which "
        "three agreeing designs had all skipped: a person far from consensus may simply be HARDER "
        "TO PREDICT AT ALL, and if both arms regress toward chance for them the gap between the "
        "better arm and the worse one shrinks for a reason that has nothing to do with compilation. "
        "The confound is real -- distance from consensus correlates -0.199 with a person's own "
        "best-arm accuracy -- and it splits the two baselines. Against full_equal both gradients "
        "vanish entirely (-0.003, p 0.92; -0.006, p 0.84): they WERE the artifact. Against "
        "full_signed both survive attenuated: dev_from_mean +0.074 (p 0.0205) and n_rated -0.109 "
        "(p 0.0005). About half a percent of variance, on one baseline convention only.",
        "redistribution", 5, "partial")
    evid(N["C_CONSENSUS_GRADIENT"], "r131-who-is-served",
         "dev_from_mean raw +0.109 -> partial +0.099 (p 0.0025); n_rated raw -0.133 -> partial "
         "-0.129 (p 0.0000); correlations of each covariate with prompt count are -0.085 and "
         "+0.037, so exposure is not the driver. Adding the person's own best-arm accuracy as a "
         "second control kills both gradients under full_equal and attenuates both under "
         "full_signed to +0.074 (p 0.0205) and -0.109 (p 0.0005). The claim as first stated here "
         "-- +0.099 at p 0.0025, unqualified -- was an overstatement on both counts: it was one "
         "control short, and it was baseline-conditional.", 5)
    edge(N["R_HARM_COUNTS"], N["C_CONSENSUS_GRADIENT"], "refines", 8, None,
         "a COUNT of losers needs the spread to clear the floor and does not; a GRADIENT on a "
         "person characteristic does not need that, and two are real")
    if "C_MAJORITY_CAPTURE" in N:
        edge(N["C_CONSENSUS_GRADIENT"], N["C_MAJORITY_CAPTURE"], "supports", 6, None,
             "the same asymmetry reached from the opposite direction: the ratings carry the "
             "majority, so distance from the majority is what the compiled arm relieves")
    edge(N["C_CONSENSUS_GRADIENT"], N["A3"], "attacks", 6, None,
         "a standard whose benefit depends on distance from consensus is redistributive")
    evid(N["R_HARM_COUNTS"], "independent-design-K5-A-seed-8101",
         "Reached the same conclusion from a different direction and more starkly: median "
         "WITHIN-person sd of the person-prompt gain is 23.15pp against a BETWEEN-person sd of "
         "8.51pp, so the between-person spread is about a THIRD of its own resampling floor. "
         "ICC 0.022 with permutation p 0.0 over 5 seeds -- real structure, tiny share of variance, "
         "and it warns against over-reading that p at n=15,031.", 8)
    evid(N["C_CONSENSUS_GRADIENT"], "independent-design-K5-A-seed-8101",
         "Distance from pooled consensus predicts a LESS negative person-level gain, rho +0.133 "
         "(p 2.6e-5), the same sign as the +0.099 partial found here; engagement (criteria rated "
         "per prompt) rho -0.215, also the same sign as -0.129. CRUCIALLY it baselines against the "
         "person's OWN importance-weighted full arm, not the pooled one, and offers a rival reading "
         "for its own version: an idiosyncratic rater's own ratings predict their own ranking more "
         "noisily, which weakens their personal baseline rather than core serving them better. "
         "That reading cannot explain the pooled-baseline version, so the two designs agreeing on "
         "sign across DIFFERENT baselines is worth more than either alone.", 7)

    N["C_ITEM_COUNT_DOMINATES"] = node(
        "most-of-the-compiled-arms-shortfall-is-item-count-not-lost-personalisation", "my_claim",
        "Compilation reproduces a person's own ranking 1.25pp worse than that person's own "
        "importance-weighted full arm [-2.01, -0.48], which is BH-significant and Cohen's d -0.047. "
        "But core also trails a NON-personalised pooled full arm by 2.05pp, a LARGER gap. So the "
        "shortfall is dominated by having four criteria instead of fifteen, not by losing the "
        "person's own weighting. The redistribution story, at the level this project originally "
        "posed it, is not what the data shows.",
        "redistribution", 6, "partial")
    evid(N["C_ITEM_COUNT_DOMINATES"], "independent-design-K5-A-seed-8101",
         "core vs personal -1.25pp (p 0.0014, two-way cluster on person x prompt, 15,031 rows, "
         "79,640 pairs); core vs full_pooled -2.05pp (p 1.6e-8). Below its own pre-registered 2.0pp "
         "practical floor, hence UNVERIFIED rather than OVERTURNED. Sign-convention spec cell: "
         "against UNSIGNED pooled full, core WINS by +6.89pp -- the negative-quarter fact is "
         "load-bearing, not cosmetic.", 6)
    edge(N["C_ITEM_COUNT_DOMINATES"], N["R_HARM_COUNTS"], "supports", 6, None, None)

    N["DISC_SHAM"] = node(
        "discrepancy-core-vs-random-subset-differs-6x-between-designs", "control",
        "Two designs measured the same-looking quantity -- core against a random count-matched "
        "subset of that prompt's own full criteria -- and got +1.40pp and +9.14pp. A 6.5x gap on "
        "nominally the same comparison looked like a design difference somewhere. LOCATED, in one "
        "line: r131/independent_A.py:359 builds its random subset as sat_full_arr[idx].mean(axis=0) "
        "with NO sign applied -- its own result JSON says 'unsigned mean satisfaction' -- while the "
        "ladder's random-4 is direction-signed by each criterion\'s polarity. So core beats an "
        "arbitrary count-matched subset by +1.40pp when that subset gets the free sign information "
        "and by +9.14pp when it does not. The 7.74pp difference matches the independently measured "
        "cost of dropping sign orientation (8.87pp on full, 9.6pp on top-importance-4) to within a "
        "point. RESOLVED: not a discrepancy, two answers to two questions. The one that bears on "
        "whether the compiler does work is the signed one, because the sign is free and any real "
        "substitute would use it.",
        "substitution", 9, "settled")
    evid(N["DISC_SHAM"], "session-source-diff-2026-07-30",
         "r131/independent_A.py:359 unsigned; r126/independent_A.py signs every full-derived rung "
         "by sign(mean importance). Magnitude of the gap reproduces the sign-orientation cost "
         "measured independently by a third design.", 9)
    edge(N["DISC_SHAM"], N["C_LADDER"], "acquits", 9, None,
         "the ladder's lowest rung is one number once the sign convention is named")
    edge(N["DISC_SHAM"], N["C_LADDER"], "confounds", 1, None,
         "kept at minimum confidence so the resolved alternative stays in the audit trail")

    N["C_VETO"] = node(
        "the-veto-is-lost-by-aggregation-not-by-compilation", "my_claim",
        "The release's third ranking block is a VETO -- 'C is unacceptable' with a rationale -- "
        "carried by 2,422 of 15,593 assessments, and 132 rounds of this campaign never opened it. "
        "A veto is not a preference: no ordering expresses 'never produce this'. Measured on the "
        "2,275 cells where a person ruled out some but not all responses: the person's OWN world "
        "ranking puts one of their own vetoed responses first only 3.90% of the time, so the veto "
        "IS expressible in the ranking task. The compiled arm does it 15.47% of the time, the "
        "sign-corrected uncompiled arm 13.80%, and a RANDOM top 37.82%. But a DIFFERENT annotator's "
        "own top choice on the same prompt lands on this person's vetoed set 17.19% of the time -- "
        "so the compiled standard violates LESS often than a human peer in the same position. What "
        "loses the veto is aggregation across people, not the compilation step. Every collective "
        "standard pays roughly one veto in six, and it is invisible in every aggregate concordance "
        "number the field reports. DOWNGRADED by a held-out split swept over 12 partitions: the "
        "ORDERING is stable everywhere -- 0.039 self, 0.138 full_signed, 0.155 core, 0.278 "
        "full_equal, 0.378 chance -- but the specific core-versus-peer comparison FAILS in 7 of 12 "
        "held-out halves, with the confirmation-half mean at -0.0105 over a range of [-0.0417, "
        "+0.0132] that crosses zero. On the full sample it was -0.0172 [-0.0311, -0.0040] at "
        "p 0.0155, i.e. a small effect whose CI barely excluded zero, and halving the data was "
        "enough to unmake it. The sentence 'core beats a human peer, significantly' is withdrawn; "
        "'core is not worse than a human peer' survives.",
        "redistribution", 6, "partial")
    evid(N["C_VETO"], "r133-the-veto",
         "Cluster-bootstrapped over prompts, 4,000 fits across 5 seeds. core 0.1547 "
         "[0.1298,0.1831]; full_signed 0.1380 [0.1165,0.1595]; full_equal 0.2778 [0.2397,0.3190]; "
         "self 0.0390 [0.0311,0.0474] n=2,076; peer 0.1719 [0.1570,0.1871] n=2,275 at 11.1 peers "
         "per cell. Positive control: an arm that simply refuses vetoed responses scores exactly "
         "0.0000. Placebo: a uniformly random top lands at 0.3728 (sd 0.0088) against an arithmetic "
         "chance of 0.3782, |diff| 0.0054. The FIRST run, without the peer comparator, returned "
         "W-COMPILER-FAILS -- a verdict that was unearned, because the self-rate is a same-person "
         "consistency floor and not a target any external rule could reach. MULTIPLICITY added "
         "after the standard's own detector reported it absent, and it was: BH q=0.05 over the four "
         "arm-versus-peer comparisons, all four survive. core - peer = -0.0172 [-0.0311,-0.0040] "
         "p 0.0155, so the compiled standard respects vetoes SIGNIFICANTLY BETTER than a human peer "
         "rather than merely no worse; full_signed - peer = -0.0339; full_equal - peer = +0.1059, "
         "so the naive unsigned arm is significantly WORSE than a person; self - peer = -0.1342.", 8)
    edge(N["C_VETO"], N["A3"], "attacks", 8, None,
         "a collective standard cannot carry a categorical veto, and this one does not")
    if "C_MAJORITY_CAPTURE" in N:
        edge(N["C_VETO"], N["C_MAJORITY_CAPTURE"], "supports", 7, None,
             "the same object seen at the response level rather than the criterion level")
    edge(N["C_VETO"], N["INSTR"], "depends_on", 8, None, None)

    N["A2"] = node(
        "A2-participant-criteria-and-ratings-represent-their-values", "their_assumption",
        "What a participant says matters is informative about what THAT participant prefers. Every "
        "downstream step -- compiling, aggregating, calling the result collective -- is stacked on "
        "it, and nothing in this campaign had checked it.",
        "aggregation", 6, "partial")
    N["C_SHARED_NOT_PERSONAL"] = node(
        "the-ratings-capture-a-shared-standard-not-personal-values", "my_claim",
        "Criterion AUTHORSHIP is not in the release, so ratings are the only proxy for a person's "
        "values. Scoring a person's four responses with their OWN signed ratings and re-scoring "
        "with a STRANGER's ratings of exactly the same criteria -- same set, different numbers -- "
        "own wins by +0.0398 [+0.0359, +0.0439] over 14,925 cells, far above a placebo that "
        "attaches the same weights to the wrong criteria (0.5595 against 0.6661). So the ratings "
        "carry real information. But the advantage is the SAME SIZE whether the target is the "
        "impersonal `world` ranking or the explicitly personal one, and that holds on the powered "
        "subset where the two rankings actually differ: +0.0356 [+0.0247,+0.0462] against +0.0332 "
        "[+0.0226,+0.0436], with personal if anything SMALLER. What was elicited is a shared "
        "standard some people express better than others, not individual values.",
        "aggregation", 7, "settled")
    evid(N["C_SHARED_NOT_PERSONAL"], "r134-do-ratings-individuate",
         "20 stranger draws per cell across 5 seeds whose stranger means span 0.6276-0.6289; "
         "prompt-clustered bootstrap; oracle positive control at 0.9192 shows the instrument can "
         "separate weightings. POWER: 51.6% of the assessments carrying a `personal` ranking give "
         "the SAME STRING as their `world` one, where the two advantages are equal by construction, "
         "so the contrast is read only on the 1,547 differing cells. FLAW STATED: the "
         "same-string arm conflates 'identical ranking' with 'no personal block at all' (13,378 vs "
         "1,829 cells), so its 0.00979 derivation check is not clean; the differ-subset comparison "
         "is, because both arms require the block to exist.", 7)
    evid(N["C_SHARED_NOT_PERSONAL"], "independent-design-A2-B-seed-4409",
         "Same number from an independent design over 286,433 units covering 1,010 of 1,012 "
         "annotators: own 0.665-0.673 against stranger 0.628-0.633, +3.8 to +4.1pp, z 7.3-16.3, "
         "p to 1e-59. Its decisive addition is a criterion I did not have: the stranger-vs-stranger "
         "FLOOR has SD 0.29, so the own-advantage is 0.13-0.14 of it -- an eighth of the natural "
         "spread between any two people predicting the same person. Its pre-registered rule "
         "required significance AND index > 2; all six grid cells passed significance and all six "
         "failed the floor. Verdict OVERTURNED. Its subjectivity stratification points the same way "
         "as my personal-block contrast from a different angle: the own-advantage is 0.0425 on "
         "prompts with a single correct answer against 0.0370 on values-and-culture prompts -- "
         "LARGER where values should matter least, which is consistency, not values.", 8)
    N["LIMIT_WRITEINS"] = node(
        "limit-both-individuation-designs-are-blind-to-the-single-rater-write-ins", "control",
        "An own-versus-stranger contrast requires two people to have rated the same criterion, so "
        "both designs are restricted to the multiply-rated pool -- about 5.6 criteria per prompt. "
        "The 65% of criteria that carry exactly one rating are structurally excluded, and they are "
        "the part of the elicitation most likely to hold idiosyncratic personal content. "
        "W-SHARED-ONLY is therefore a statement about the shared-criteria regime and is not "
        "evidence that the write-in layer is equally impersonal.",
        "aggregation", None, "open")
    edge(N["LIMIT_WRITEINS"], N["C_SHARED_NOT_PERSONAL"], "confounds", 7, None,
         "the excluded 65% is exactly where the effect would live if it existed")
    edge(N["C_SHARED_NOT_PERSONAL"], N["A2"], "refines", 7, None,
         "something was captured, but not the thing the assumption names")
    edge(N["C_SHARED_NOT_PERSONAL"], N["A3"], "attacks", 7, None,
         "an aggregation of a shared standard is not an aggregation of individual values")
    if "C_CONSENSUS_GRADIENT" in N:
        edge(N["C_SHARED_NOT_PERSONAL"], N["C_CONSENSUS_GRADIENT"], "confounds", 6, None,
             "my own consensus gradient reads the ratings as a proxy for a person's values, and "
             "this says they are not one; the gradient may be about expression rather than values")

    N["A4"] = node(
        "A4-the-world-ranking-is-the-right-aggregation-target", "their_assumption",
        "The release aggregates each participant's `best for the world` ranking. Each participant "
        "also gave a `best for me` ranking, and the two differ on 45.8% of the assessments carrying "
        "both.",
        "aggregation", 6, "partial")
    N["C_TARGET_NEUTRAL"] = node(
        "the-compiled-rubric-does-not-inherit-the-aggregation-targets-bias", "my_claim",
        "An attack on A4 that FAILED, and informatively. On the 1,588 assessments where a person's "
        "`world` and `personal` rankings actually differ -- the only cells where the question "
        "exists, since on the rest every arm scores identically against both by construction -- the "
        "compiled arm reaches 0.6482 against `world` and 0.6391 against `personal`, a gap of "
        "+0.0091 whose CI [-0.0039, +0.0221] includes zero. The difficulty control, the pooled "
        "crowd's own Borda ordering, shows +0.0441 [+0.0305, +0.0581]: direct aggregation of world "
        "rankings IS strongly world-biased. The rubric is not. Choosing `world` as the target costs "
        "little at the rubric level, and this is a point in the release's favour.",
        "aggregation", 7, "settled")
    evid(N["C_TARGET_NEUTRAL"], "r135-which-target",
         "Derivation check passes exactly: on cells where the two rankings are the same string every "
         "arm's gap is 0.00e+00. Core's excess over the difficulty control is -0.0350. PARTITION "
         "FLAW STATED IN THE ARTIFACT: the pre-registered world set had no branch for a materially "
         "NEGATIVE excess, so the run labels this W-NOT-MEASURABLE, which is wrong for what "
         "happened. The fourth world is written into the file dated rather than retro-fitted into "
         "the branch, because repairing a partition after seeing the result is the move this "
         "project forbids.", 7)
    edge(N["C_TARGET_NEUTRAL"], N["A4"], "supports", 7, None,
         "an attack that failed, recorded as support rather than quietly dropped")

    N["C_HELDOUT"] = node(
        "six-headlines-survive-a-held-out-split-and-one-does-not", "my_claim",
        "The campaign's own standard detector reported `confirmatory` ABSENT in all 128 rounds: "
        "every finding was discovered and tested on the same prompts. Splitting them by a sha256 of "
        "the prompt id and recomputing every settled headline on the half it was not found on, "
        "swept over 12 independent salts because the partition is itself a researcher degree of "
        "freedom: full_equal accuracy 11/12 CONFIRMED, core accuracy 10/12, full_signed 10/12, the "
        "contested-criteria log-odds 10/12 (always negative, range -1.85 to -0.69), the polarity "
        "ratio 8/12 (always between +0.087 and +0.119, never near the 0.362 a faithful compilation "
        "would give), own-minus-stranger 7/12 (always positive, always tiny). The veto arm's "
        "core-versus-peer comparison FAILED in 7 of 12.",
        "redistribution", 8, "settled")
    evid(N["C_HELDOUT"], "r136-held-out-confirmation",
         "12 salts, each a deterministic partition fixed before scoring. Pre-registered: CONFIRMED "
         "if the held-out half reproduces the sign and its CI contains the discovery point; FAILED "
         "if the sign flips or the confirmation CI contains zero when discovery's did not. WHAT IT "
         "DOES NOT BUY, stated in the artifact: both halves are one release, one panel, one judge, "
         "so a survivor is shown not to be an artifact of WHICH PROMPTS were read and nothing more. "
         "The word replication is not available for it.", 8)
    if "C_VETO" in N:
        edge(N["C_HELDOUT"], N["C_VETO"], "refines", 8, None,
             "kills the core-versus-peer comparison specifically; the ordering survives")
    for k in ("C_POL", "C_SIGNFLIP", "C_ADJUDICATED", "C_SHARED_NOT_PERSONAL"):
        if k in N:
            edge(N["C_HELDOUT"], N[k], "supports", 8, None,
                 "survives on prompts it was not found on")

    # ---- the partition that should have existed from the start ------------------------------
    N["INSTR_FREE"] = node(
        "instrument-free-vs-instrument-dependent-is-the-partition-that-matters", "fact",
        "The release does NOT ship its own satisfaction scores, so r04 rebuilt one with a local "
        "Qwen3.5-2B. Every claim routed through it is therefore a claim about what a 2B model "
        "thinks, not about what CoVal's compilation does -- and this campaign has been stating the "
        "second while measuring the first. The corpus splits cleanly. INSTRUMENT-FREE, counted "
        "directly off the release: 63.5% of criteria have exactly one rater and ZERO have two or "
        "three; 25.6% carry a negative mean; among multi-rated negatives 99.1% have at least one "
        "rater on the positive side; 7.8-9.4% of core criteria are verbatim copies of a full "
        "criterion; 48.4% of people's world and personal rankings differ; 26.7% of assessments "
        "carry a veto; and contested criteria are 2.3-3.2x less likely to be copied verbatim. "
        "INSTRUMENT-DEPENDENT, i.e. conditional on one local judge: the polarity ratio, every arm "
        "concordance, own-versus-stranger, the veto violation rates, and the whole person-level "
        "analysis.",
        "instrument", 9, "settled")
    evid(N["INSTR_FREE"], "session-partition-2026-07-30",
         "The load-bearing result was re-fitted with the judge removed entirely: contested -> "
         "verbatim retention OR 0.3083 [0.1906, 0.4681] controlling |mean rating| and log rater "
         "count linearly, and OR 0.4343 [0.2610, 0.6627] with |mean rating| entered as quintile "
         "dummies, a non-parametric control. Both intervals exclude 1 over 3,000 prompt-clustered "
         "bootstrap fits across 5 seeds. Outcome is a normalised text match; predictor is the "
         "release's own ratings; no forward pass anywhere.", 9)
    if "C_ADJUDICATED" in N:
        edge(N["INSTR_FREE"], N["C_ADJUDICATED"], "supports", 9, None,
             "the claim survives with the instrument removed, so it is about the artifact")
    for k in ("C_POL", "C_SIGNFLIP", "C_VETO", "C_SHARED_NOT_PERSONAL", "C_LADDER", "C_FLAT",
              "R_HARM_COUNTS", "C_CONSENSUS_GRADIENT", "C_TARGET_NEUTRAL", "C_COLLECTIVE"):
        if k in N:
            edge(N["INSTR_FREE"], N[k], "confounds", 7, None,
                 "conditional on one local 2B judge that is not the release's own scorer; the "
                 "claim is about a rubric-scoring pipeline built this way, not about CoVal")

    N["C_BATCH"] = node(
        "the-judges-batching-dependence-is-real-per-judgement-and-immaterial-per-claim", "my_claim",
        "The judge is exactly deterministic given a batching and not across batchings: on 480 fixed "
        "prompts, batch=1 disagrees with batch=48 on 165 of 480 judgements up to 5.4e-02, and "
        "length-sorting on 158 up to 6.2e-02, because Qwen3.5's gated-delta recurrence does not "
        "fully mask left-pad tokens. The stored tensors were produced at batch 48 in file order, an "
        "unregistered implementation choice under every published number. Re-scoring the ENTIRE "
        "grid under length-sorted batching changes every single one of 75,244 judgements -- zero "
        "identical, mean |delta| 9.5e-03, max 6.4e-02 -- and moves the arm concordances and their "
        "gaps by at most 0.0007 against a pre-registered tolerance of 0.005. A defect that touches "
        "100% of the values is immaterial where the claims are, because ~16 criteria and tens of "
        "thousands of ordered pairs average it away. Bounds one dimension of the instrument's "
        "arbitrariness at under 0.001.",
        "instrument", 8, "settled")
    evid(N["C_BATCH"], "r137-batch-gauge",
         "core 0.6604 -> 0.6607; full_equal 0.5941 -> 0.5937; full_signed 0.6806 -> 0.6803; "
         "core-minus-full_equal 0.0663 -> 0.0670; core-minus-full_signed -0.0202 -> -0.0196. Found "
         "while optimising for speed: the optimised judge disagreed with the reference by 4.2e-02 "
         "and the only behavioural difference was length-sorted batching, so the REFERENCE was "
         "re-run under five batchings to locate it.", 8)
    edge(N["C_BATCH"], N["INSTR"], "supports", 8, None,
         "the instrument survives one arbitrariness check at the level that matters")
    if "INSTR_FREE" in N:
        edge(N["C_BATCH"], N["INSTR_FREE"], "refines", 8, None,
             "instrument-dependent does not mean unbounded: this dimension is bounded at <0.001")

    N["K19"] = node(
        "K19-the-judges-fewshot-only-demonstrates-positive-criteria", "knife",
        "Both exemplars in the judge's two-shot prompt state a criterion in positive prescriptive "
        "form. If the judge is a systematically noisier reader of criteria that describe an "
        "undesirable behaviour, that alone attenuates every measurement on the negative quarter -- "
        "the same quarter that carries the polarity result, the sign-flip result, and most of the "
        "contested criteria. Named by an independent design as the most credible way its own "
        "conclusion could be an underestimate.",
        "instrument", None, "open")
    edge(N["K19"], N["INSTR"], "attacks", None, None, None)
    edge(N["K19"], C, "confounds", 6, None,
         "would attenuate matchability specifically for majority-negative criteria")
    edge(N["K19"], N["C_POL"], "confounds", 5, None,
         "would attenuate the negative block's loading for an instrument reason")

    N["D_GAUGE_PROMPTS"] = node(
        "defect-my-own-gauge-variants-were-malformed", "defect",
        "The first draft of the gauge round built its prompt variants by chained .replace on a "
        "template. Two of five came out broken: the negated-question variant's second and third "
        "replacements cancelled, leaving a Yes exemplar under a 'does the reply VIOLATE' question, "
        "and the reordered-fewshot variant lost its second exemplar's question line. Both then "
        "reported large concordance drifts that were my own malformed prompts, not the judge's "
        "gauge dependence. Caught by reading the constructed strings, not by the numbers -- the "
        "numbers looked like a finding.",
        "instrument", 9, "refuted")
    evid(N["D_GAUGE_PROMPTS"], "session-self-audit-2026-07-30",
         "Rebuilt from a structured exemplar spec; the malformed run's max drift 0.2131 fell to "
         "0.1736 and relocated entirely to the negated-question x sign-flipped cell, which is a "
         "double negation rather than a template artefact. A prompt template is code: it gets "
         "built, not patched.", 9)


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

    print("\n  ── this project's OWN retracted claims ──")
    for r in q("""SELECT name, coalesce(d_level::text,'-'),
                         (SELECT count(*) FROM edge x WHERE x.dst=n.id AND x.kind='overturns')
                  FROM node n WHERE kind='my_claim' AND status='refuted' ORDER BY name"""):
        print(f"  {r[0]:<58} D{r[1]:<3} killed by {r[2]} edge(s)")

    orphan_retract = q("""SELECT name FROM node n WHERE kind='my_claim' AND status='refuted'
                          AND NOT EXISTS (SELECT 1 FROM edge x WHERE x.dst=n.id
                                          AND x.kind='overturns')""")
    if orphan_retract:
        print("  !! retracted with NO incoming kill edge -- a retraction nobody can trace back:")
        for r in orphan_retract:
            print(f"     {r[0]}")

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
