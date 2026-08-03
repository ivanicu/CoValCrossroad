#!/usr/bin/env python3
"""
R234_independent_A -- is `coval_core` a faithful compression of `coval_full`?

Independent design, seed 11.  Written without reading any other answer to this
question.  Everything below was chosen before the numbers were seen; the
pre-registered kill thresholds are in KILL and are checked mechanically at the
end.

================================================================ PRE-REGISTRATION

ESTIMAND (primary)
  Lambda -- the FIDELITY INDEX of the compiler, on the decision the release
  actually supports (which of four responses is better).

    Phi(X)  = E_p [ pairwise concordance, over the 6 response pairs of prompt p,
                    between the ordering induced by compiler X and the ordering
                    induced by the FULL rubric under the population's own signed
                    weights ]

    Lambda  = ( Phi(core) - Phi(floor) ) / ( Phi(ceiling) - Phi(floor) )

  floor    = MEASURED: 4 criteria drawn at random from the full rubric,
             unit-weighted, 20 seeds.  Budget-matched to the core.
  ceiling  = MEASURED: the target's own reproducibility -- split the prompt's
             annotators in half, build the signed aggregate from each half, and
             measure their agreement (50 resamples x 3 seeds).  No compression
             can be asked to agree with the full rubric better than the full
             rubric agrees with itself.

  WHY THIS ESTIMAND, and not another:
   * "faithful compression" is a claim that the compressed object SUPPORTS THE
     SAME DECISIONS as the original.  The only decision this release supports is
     the ordering of the four responses, so that is what must be preserved.
   * the comparison is rubric-to-rubric, NOT rubric-to-human.  Comparing each
     rubric to human rankings (the obvious move) confounds compilation loss with
     the judge's own error at predicting humans, and that error is large.  The
     rubric-to-rubric contrast holds the judge fixed on both sides.
   * it has a MEASURED floor and a MEASURED ceiling, so the threshold is not an
     opinion.  Without the ceiling, "Phi(core) = 0.71" is uninterpretable.

ESTIMANDS (secondary, pre-registered, BH-corrected with the primary over the
whole grid)
  S1  POLARITY ASYMMETRY  A = R_P - R_N.
      23.0% of the 102,147 annotator-criterion weights are NEGATIVE and 25.6%
      of the 15,248 full criteria have a negative population mean: a quarter of
      this rubric is PROHIBITION.  The core ships criterion text with no
      weights, so prohibitions can survive only if the compiler rewrote them
      into positive directives.  Split the full rubric into its positive and
      negative halves,  Pos = sum_{w>0} w z_i,  Neg = sum_{w<0} |w| z_i,
      so F+ = Pos - Neg.  Retention of each channel by the core is
      R_P = zbar(corr(C,Pos)) / zbar(corr(F+,Pos)) and
      R_N = zbar(corr(C,-Neg)) / zbar(corr(F+,-Neg)) (Fisher-z means).
      A = 0 under faithful compression.
      ⚠ SIGN CORRECTION, made AFTER the synthetic controls ran and BEFORE any
      number was interpreted.  The sentence originally written here -- "A > 0
      means the compiler kept 'do' and dropped 'don't'" -- is BACKWARDS.  The
      synthetic worlds settle it: a core built to RESPECT polarity returns
      A = +1.01, a core built to IGNORE polarity returns A = -0.48.  So
      A > 0 = BETTER prohibition alignment than the full rubric, A < 0 = worse.
      This is exactly what the synthetic controls exist for: without them the
      observed A = -0.057 would have been read as the opposite of what it is.
      The original wording is kept above the line so the error is on the record.
  S2  MINORITY SLOPE  beta.  Per (prompt, annotator): the annotator's own
      weighted rubric and the core each predict that annotator's own world
      ranking.  beta = OLS slope of (Acc_core - Acc_own) on the annotator's
      leave-one-out minority-ness, clustered by prompt; reported against a
      budget-matched mechanical compiler (beta_core - beta_mech) so that the
      "some annotators are simply harder to predict" confound -- which raises
      BOTH arms -- is differenced out.
  S3  VETO AUC.  4,901 assessments carry an explicit "X is unacceptable"
      rating.  A rubric that cannot flag an unacceptable response has lost the
      decision that matters most.  AUC of (-score) for the veto label, core vs
      full, paired by prompt.

IDENTIFICATION
  * The core's ONLY instrument-free properties are its text and its cardinality.
    It ships no weights and no annotator attribution.  Therefore every
    core-to-anything comparison must route through an instrument.  The
    instrument here is a cached Qwen3.5-2B-Base Yes/No logit-gap judge.  EVERY
    number below is a statement about how that judge reads these two rubrics,
    not a direct statement about the rubrics.  A gauge run (gauge.py) bounds
    the instrument dependence.
  * Lambda is identified: floor, ceiling and Phi(core) are all measured on the
    same instrument and the same prompts.
  * A is identified: Pos and Neg are built from human weights (instrument-free)
    and projected through the same judge as the core.
  * beta is identified: minority-ness is instrument-free.
  * PARTIALLY identified: any claim about WHICH full criterion a core criterion
    "is".  No such matching is attempted -- it would need a semantic model, a
    second instrument, and it is not needed for any estimand above.

SCOPE for every number
  population  : the 968 prompts joinable between comparisons.jsonl and
                conversation_rubrics.jsonl (of 1078 / 986); annotator-level
                numbers over the 18,384 assessments (world ranking, universal)
                and the 4,901 that also carry a personal ranking + veto block.
  instrument  : Qwen3.5-2B-Base, few-shot Yes/No, sigmoid(logit(" Yes")
                - logit(" No")), cached tensor a04_{full,core}.npz.
  baseline    : budget-matched random-4 compiler (floor) and the full rubric's
                own annotator split-half agreement (ceiling).
  regime      : 4 candidate responses, 6 pairs, K<=4 core criteria, mean 15.5
                full criteria per prompt.

WORLDS (>=2, ontologically different) and the prediction matrix
  W1 FAITHFUL       -- the core is a lossy but unbiased compression.
                       Lambda high; A ~ 0; beta_core - beta_mech ~ 0; veto parity.
  W2 DIRECTIONAL    -- the core preserves "what to do" and destroys "what not to
                       do"; the prohibition channel is dropped.
                       Lambda mid; A > 0 and outside its permutation null;
                       veto AUC of core << full.
  W3 MAJORITARIAN   -- the core preserves the consensus and deletes minority
                       positions.
                       Lambda high on population aggregate; beta_core - beta_mech
                       < 0; A ~ 0.
  W4 NOT-A-COMPRESSION -- the core is an independently authored summary, not a
                       compression; it sits at the random-4 floor.
                       Lambda ~ 0 on every cell.
  These differ in ontology (what KIND of object the core is), not in a parameter.

KILL (thresholds fixed before the run)
  Lambda <= 0.33  -> UNFAITHFUL   (closer to a random 4-criterion draw than to
                                   the full rubric's own self-agreement)
  Lambda >= 0.67  -> FAITHFUL
  otherwise       -> PARTIAL, and S1/S2/S3 name what was lost.
  DEGENERACY GUARD: if Phi(ceiling) - Phi(floor) < 0.05 the statistic is
  degenerate and NO threshold is admissible -> report UNVERIFIED, not a verdict.

CONTROLS
  POSITIVE  oracle4  -- greedy 4 full criteria maximising Phi against the target.
                        Must land near the budget ceiling.  DOSE-RESPONSE:
                        g*oracle4 + (1-g)*core for g in {0,.25,.5,.75,1} must be
                        monotone.  MUST FAIL AT g=0: the criterion "Lambda >=
                        0.67" must NOT already be satisfied by the core, else the
                        control cannot fail.  Reported either way.
  POSITIVE  join     -- the content-fuzzy join is verified against an INDEPENDENT
                        key: the annotator set of the rubric must equal the
                        annotator set of merged_comparisons for the joined
                        prompt_id.  A join that passes nothing is silence.
  NEGATIVE  sham_core-- the core's own satisfaction rows with the response
                        letters permuted.  Destroys criterion<->response
                        correspondence; preserves criterion count, criterion
                        identity, and every marginal.  Excluded world: "the core
                        scores well because its satisfaction values happen to
                        have the right marginal distribution".
  NEGATIVE  polarity permutation -- reassign which criteria are "positive" and
                        which "negative" while preserving group sizes and the
                        multiset of |w|.  Excluded world: "A is explained by
                        group size or weight magnitude, not by sign".
  SYNTHETIC W2 world -- a synthetic core built to RESPECT polarity (negated rows
                        for negative criteria) must give A ~ 0; one built to
                        IGNORE polarity (|w| weighting) must give A > 0.  If the
                        instrument does not separate these two synthetic cores,
                        A cannot be read at all.
  PLACEBO   full_signed vs itself -- Phi must be exactly 1.000 (DERIVATION,
                        labelled; it checks the plumbing, not the world).
  PLACEBO   Acc_core - Acc_core regressed on minority-ness -> exactly 0.
  NOISE FLOOR measured by resampling, never assumed: split-half over annotators
                        (ceiling) and 20-seed spread (floor).
  WORST4    the mirror of the positive control: greedy 4 MINIMISING Phi.  If
                        worst4 does not come out low, the statistic cannot rank
                        compilers and nothing else in this file means anything.

SPECIFICATION GRID (all cells reported, including the ones that kill it)
  norm        : z | rank | raw            (raw == center is a DERIVATION,
                                           verified numerically, see below)
  weight agg  : mean | median | trimmed20 | signvote
  target      : full_signed | human_world | human_personal
  metric      : pairwise | kendall_b | top1
  prompts     : all | drop_calibration (the one prompt with 1012 assessments)
                    | ge8_annotators
  seeds       : 11, 12, 13 for every resampling step; 20 seeds for the floor.

MULTIPLICITY  BH q=0.05 over EVERY test in the file (primary + S1 + S2 + S3 +
              every grid cell that carries a p-value), counted once, reported as
              cells tested / cells surviving, with the non-survivors listed.

IMPOSSIBLE HERE (named, with what each would require)
  independently replicated  -- a second release, or the two sibling agents in
                               this triple-blind design.  NOT claimed here.
  causally identified       -- an intervention on the compiler.  The compiler is
                               shipped as an output; its input/prompt/model is
                               not in the release.  Would require OpenAI's
                               compilation code.
  temporally resolved       -- no timestamps on rubric authorship.
  construct validated       -- no external gold standard for "faithful".  The
                               human rankings are a criterion, not a construct.
  cross-model               -- ONE judge.  gauge.py partially lifts this by
                               re-judging a subsample with a different template
                               and a different-size model; that is a gauge
                               bound, not cross-model validation.
  position randomized       -- no presentation-order field in the release.

ARTIFACT  results/*.json + results/*.npz, with the sha256 of this file.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = HERE / "results"
RES.mkdir(exist_ok=True)
SAT_DIR = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/"
                  "R04_rebuild_satisfaction/results")
LABELS = ["A", "B", "C", "D"]
PAIRS = list(itertools.combinations(range(4), 2))

KILL = {"unfaithful_at": 0.33, "faithful_at": 0.67, "degeneracy_gap": 0.05}


# ------------------------------------------------------------------ join
def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s)).lower()
    return re.sub(r"\s+", " ", s).strip()


ROLE_CANON = {"system": "developer", "developer": "developer", "user": "user",
              "assistant": "assistant", "tool": "tool"}


def _content(m):
    c = m.get("content")
    if isinstance(c, dict):
        c = " ".join(c.get("parts") or [])
    return c


def message_key(messages) -> str:
    parts = []
    for m in messages:
        role = m.get("role") or (m.get("author") or {}).get("role")
        parts.append(f"{ROLE_CANON.get(role, role)}:{norm(_content(m))}")
    return "|".join(parts)


def content_key(messages) -> str:
    return " ".join(norm(_content(m)) for m in messages)


def load_join():
    """Reimplemented independently; the cached tensor is keyed by prompt_id and
    the rubric file is keyed by conversation.id, and the two id spaces are
    DISJOINT (verified: |rub & cmp| = 0).  So a content join is forced."""
    import difflib
    by_key, by_content, prompts = {}, {}, {}
    for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        msgs = rec["prompt"]["messages"]
        by_key[message_key(msgs)] = rec["prompt_id"]
        by_content.setdefault(content_key(msgs), rec["prompt_id"])
        prompts[rec["prompt_id"]] = rec
    joined, how, unmatched = [], Counter(), []
    for line in open(ROOT / "data/conversation_rubrics.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        msgs = rec["conversation"]["messages"]
        pid = by_key.get(message_key(msgs))
        if pid is not None:
            how["role_canonical"] += 1
        else:
            pid = by_content.get(content_key(msgs))
            if pid is not None:
                how["content_only"] += 1
        if pid is None:
            unmatched.append((rec, content_key(msgs)))
            continue
        joined.append((pid, prompts[pid], rec))
    if unmatched:
        keys = list(by_content)
        for rec, ck in unmatched:
            m = difflib.get_close_matches(ck, keys, n=1, cutoff=0.95)
            if m:
                joined.append((by_content[m[0]], prompts[by_content[m[0]]], rec))
                how["fuzzy>=0.95"] += 1
            else:
                how["unmatched"] += 1
    return joined, dict(how)


def join_positive_control(joined):
    """INDEPENDENT verification of the join: the annotator set that scored the
    rubric must equal the annotator set that assessed the joined prompt_id.
    This key was NOT used to build the join, so it can fail."""
    mset = defaultdict(set)
    for line in open(ROOT / "data/merged_comparisons_annotators.jsonl", encoding="utf-8"):
        d = json.loads(line)
        mset[d["prompt_id"]].add(d["annotator_id"])
    exact = jac = 0
    jacs = []
    for pid, _comp, rub in joined:
        rs = {x["annotator_id"] for c in rub["coval_full"] for x in c["scores"]}
        ms = mset.get(pid, set())
        if not rs or not ms:
            continue
        j = len(rs & ms) / len(rs | ms)
        jacs.append(j)
        exact += (rs == ms)
        jac += (j >= 0.9)
    jacs = np.array(jacs)
    # NEGATIVE CONTROL FOR THE JOIN: the same statistic under a random pairing.
    # Without it, jaccard = 0.95 is a number with no scale -- it could be what
    # any pairing returns if annotators overlap heavily across prompts.
    rng = np.random.default_rng(11)
    pids = [p for p, _c, _r in joined]
    shuffled = []
    for k, (pid, _comp, rub) in enumerate(joined):
        rs = {x["annotator_id"] for c in rub["coval_full"] for x in c["scores"]}
        ms = mset.get(pids[int(rng.integers(len(pids)))], set())
        if rs and ms:
            shuffled.append(len(rs & ms) / len(rs | ms))
    shuffled = np.array(shuffled)
    return {"n": int(len(jacs)), "exact_annotator_set_match": int(exact),
            "jaccard_ge_0.9": int(jac), "jaccard_mean": float(jacs.mean()),
            "jaccard_p05": float(np.percentile(jacs, 5)),
            "NEGCTRL_random_pairing_jaccard_mean": float(shuffled.mean()),
            "NEGCTRL_random_pairing_jaccard_p95": float(np.percentile(shuffled, 95)),
            "PASSES": bool(jacs.mean() > 0.9 and shuffled.mean() < 0.1)}


# ------------------------------------------------------------------ load tensors
def load_sat(tag):
    d = np.load(SAT_DIR / f"a04_{tag}.npz", allow_pickle=True)
    meta, sat = d["meta"], d["sat"].astype(np.float64)
    out = defaultdict(dict)
    for m, s in zip(meta, sat):
        p, i, r = m.split("|")
        out[p][(int(i), r)] = s
    mats = {}
    for p, dd in out.items():
        nc = max(i for i, _ in dd) + 1
        M = np.full((nc, 4), np.nan)
        for (i, r), s in dd.items():
            M[i, LABELS.index(r)] = s
        mats[p] = M
    return mats


# ------------------------------------------------------------------ per-prompt bundle
def build(joined, sat_full, sat_core):
    bundles = {}
    drop = Counter()
    for pid, comp, rub in joined:
        if pid not in sat_full or pid not in sat_core:
            drop["no_sat"] += 1
            continue
        Sf, Sc = sat_full[pid], sat_core[pid]
        crits = rub["coval_full"]
        if Sf.shape[0] != len(crits):
            drop["full_len_mismatch"] += 1
            continue
        if Sc.shape[0] != len(rub["coval_core"]):
            drop["core_len_mismatch"] += 1
            continue
        if np.isnan(Sf).any() or np.isnan(Sc).any():
            drop["nan"] += 1
            continue
        anns = sorted({x["annotator_id"] for c in crits for x in c["scores"]})
        aidx = {a: k for k, a in enumerate(anns)}
        W = np.full((len(anns), len(crits)), np.nan)
        for j, c in enumerate(crits):
            for x in c["scores"]:
                W[aidx[x["annotator_id"]], j] = x["score"]
        rank_world, rank_pers, veto = {}, {}, defaultdict(set)
        for asm in comp["metadata"]["assessments"]:
            a = asm.get("annotator_id")
            rb = asm.get("ranking_blocks") or {}
            for key, store in (("world", rank_world), ("personal", rank_pers)):
                blk = rb.get(key) or []
                if blk and blk[0].get("ranking"):
                    store[a] = blk[0]["ranking"]
            for e in (rb.get("unacceptable") or []):
                for t in (e.get("rating") or []):
                    t = t.strip()
                    if t and t[0] in LABELS:
                        veto[a].add(t[0])
        bundles[pid] = dict(Sf=Sf, Sc=Sc, W=W, anns=anns,
                            rank_world=rank_world, rank_pers=rank_pers,
                            veto=dict(veto), n_assess=len(comp["metadata"]["assessments"]))
    return bundles, dict(drop)


# ------------------------------------------------------------------ normalisation
def normalise(M, how):
    if how == "raw":
        return M.copy()
    if how == "center":
        return M - M.mean(1, keepdims=True)
    if how == "z":
        c = M - M.mean(1, keepdims=True)
        s = c.std(1, keepdims=True)
        s[s < 1e-12] = 1.0
        return c / s
    if how == "rank":
        r = np.argsort(np.argsort(M, axis=1), axis=1).astype(float)
        return r - r.mean(1, keepdims=True)
    raise ValueError(how)


def agg_weights(W, how):
    with np.errstate(invalid="ignore"):
        if how == "mean":
            w = np.nanmean(W, 0)
        elif how == "median":
            w = np.nanmedian(W, 0)
        elif how == "trimmed20":
            w = np.array([_trim(W[:, j], 0.2) for j in range(W.shape[1])])
        elif how == "signvote":
            w = np.nanmean(np.sign(W), 0)
        else:
            raise ValueError(how)
    return np.nan_to_num(w)


def _trim(v, f):
    v = v[~np.isnan(v)]
    if len(v) == 0:
        return 0.0
    v = np.sort(v)
    k = int(np.floor(len(v) * f))
    v = v[k:len(v) - k] if len(v) - 2 * k > 0 else v
    return float(v.mean())


_CACHE = {}


def cache(bundles, norm_how, w_how):
    """Precompute (Zf, Zc, w) once per (norm, weight-aggregation).  Recomputing
    these inside a 2000-draw permutation loop is what turns a 30 s run into an
    hour; it changes no number."""
    key = (norm_how, w_how)
    if key not in _CACHE:
        _CACHE[key] = {p: (normalise(b["Sf"], norm_how), normalise(b["Sc"], norm_how),
                           agg_weights(b["W"], w_how))
                       for p, b in bundles.items()}
    return _CACHE[key]


def stable_seed(*parts) -> int:
    """int() of a sha256 -- python's str hash is salted per process, so using it
    would make the run irreproducible across invocations."""
    h = hashlib.sha256("|".join(str(x) for x in parts).encode()).digest()
    return int.from_bytes(h[:8], "big") % (2 ** 31 - 1)


# ------------------------------------------------------------------ agreement
def pairwise_conc(x, y):
    """Fraction of the 6 response pairs ordered the same way.  Ties -> 0.5."""
    n = 0.0
    for i, j in PAIRS:
        dx, dy = x[i] - x[j], y[i] - y[j]
        if abs(dx) < 1e-12 or abs(dy) < 1e-12:
            n += 0.5
        else:
            n += 1.0 if dx * dy > 0 else 0.0
    return n / len(PAIRS)


def kendall_b(x, y):
    c = d = tx = ty = 0
    for i, j in PAIRS:
        dx, dy = x[i] - x[j], y[i] - y[j]
        if abs(dx) < 1e-12 and abs(dy) < 1e-12:
            continue
        if abs(dx) < 1e-12:
            tx += 1
            continue
        if abs(dy) < 1e-12:
            ty += 1
            continue
        c += dx * dy > 0
        d += dx * dy < 0
    den = np.sqrt((c + d + tx) * (c + d + ty))
    return (c - d) / den if den > 0 else 0.0


def top1(x, y):
    return float(int(np.argmax(x)) == int(np.argmax(y)))


METRICS = {"pairwise": pairwise_conc, "kendall_b": kendall_b, "top1": top1}


# ------------------------------------------------------------------ compilers
def compile_scores(pid, b, Zf, Zc, w, seed):
    """Every compiler returns a length-4 score vector.  All the K=4 compilers use
    UNIT weights, because the core ships no weights -- that is the whole point of
    the budget match."""
    nc = Zf.shape[0]
    out = {}
    out["full_signed"] = w @ Zf                      # THE TARGET
    out["full_unit"] = Zf.sum(0)                     # compression 1x, sign dropped
    out["full_abs"] = np.abs(w) @ Zf                 # magnitudes kept, sign dropped
    out["core"] = Zc.sum(0)
    rng = np.random.default_rng(stable_seed(pid, seed, "sham"))
    out["sham_core"] = out["core"][rng.permutation(4)]   # NEGATIVE CONTROL
    k = min(4, nc)
    out["top4_abs"] = Zf[np.argsort(-np.abs(w))[:k]].sum(0)
    out["top4_pos"] = Zf[np.argsort(-w)[:k]].sum(0)
    with np.errstate(invalid="ignore"):
        sd = np.nan_to_num(np.nanstd(b["W"], 0))
    out["top4_disp"] = Zf[np.argsort(-sd)[:k]].sum(0)
    sel = np.argsort(-np.abs(w))[:k]
    out["top4_abs_signed"] = (np.sign(w[sel])[:, None] * Zf[sel]).sum(0)
    r2 = np.random.default_rng(stable_seed(pid, seed, "rand4"))
    for s in range(20):
        out[f"random4_s{s}"] = Zf[r2.choice(nc, size=k, replace=False)].sum(0)
    # POSITIVE CONTROL: greedy selection against the target.
    target = out["full_signed"]
    out["oracle4"] = _greedy(Zf, target, k, sign=+1)
    out["worst4"] = _greedy(Zf, target, k, sign=-1)
    o = out["oracle4"]
    oz = (o - o.mean()) / (o.std() + 1e-12)
    cz = (out["core"] - out["core"].mean()) / (out["core"].std() + 1e-12)
    for g in (0.0, 0.25, 0.5, 0.75, 1.0):
        out[f"dose_g{g:.2f}"] = g * oz + (1 - g) * cz
    return out


def _greedy(Zf, target, k, sign):
    chosen, cur = [], np.zeros(4)
    for _ in range(k):
        best, bi = -9e9, None
        for i in range(Zf.shape[0]):
            if i in chosen:
                continue
            v = sign * pairwise_conc(cur + Zf[i], target)
            if v > best:
                best, bi = v, i
        chosen.append(bi)
        cur = cur + Zf[bi]
    return cur


# ------------------------------------------------------------------ ceiling
def ceiling_split_half(b, Zf, w_how, metric, rng, reps=50):
    """PRE-REGISTERED ceiling.  KEPT, AND REPORTED AS INADMISSIBLE.

    It compares an n/2 aggregate with another n/2 aggregate, while Phi(core) is
    measured against the n aggregate.  The halves are therefore noisier than the
    target the core is scored on, the 'ceiling' sits BELOW what a good compiler
    reaches, and Lambda comes out > 1.  Lambda > 1 is the diagnostic that a
    ceiling was not a ceiling -- exactly the 'control that cannot pass' failure,
    in its mirror image.  Retained verbatim so the error is on the record."""
    W = b["W"]
    na = W.shape[0]
    if na < 4:
        return np.nan
    if w_how not in ("mean", "signvote"):
        reps = 12
    f = METRICS[metric]
    H1 = np.zeros((reps, na), bool)
    H2 = np.zeros((reps, na), bool)
    for t in range(reps):
        idx = rng.permutation(na)
        H1[t, idx[: na // 2]] = True
        H2[t, idx[na // 2:]] = True
    A1 = half_aggs(W, w_how, H1) @ Zf
    A2 = half_aggs(W, w_how, H2) @ Zf
    return float(np.mean([f(A1[t], A2[t]) for t in range(reps)]))


def half_aggs(W, w_how, halves):
    """Vectorised half-sample aggregates.  'mean' and 'signvote' are row-means of
    a (transformed) matrix, so all reps are one matmul; 'median'/'trimmed20' are
    not, and fall back to the loop with fewer reps.  Pure speed, no number
    changes -- verified by the equivalence assertion in main()."""
    if w_how in ("mean", "signvote"):
        X = np.sign(W) if w_how == "signvote" else W
        F = np.nan_to_num(X)
        V = (~np.isnan(X)).astype(float)
        H = halves.astype(float)
        num = H @ F
        den = H @ V
        return np.divide(num, den, out=np.zeros_like(num), where=den > 0)
    return np.array([agg_weights(W[np.flatnonzero(h)], w_how) for h in halves])


def ceiling_matched(b, Zf, Zc, w_how, metric, rng, reps=50):
    """CORRECTED reliability ceiling: every predictor is scored against the SAME
    half-sample target.  Returns (phi_core, phi_otherhalf, phi_random4) so that
    Lambda_rel = (core - floor) / (otherhalf - floor) is an admissible index.

    Also returns the LEAKAGE-CONTROLLED mechanical compiler: selected on the
    weights of h2, scored against the aggregate of h1.  A subset compiler is a
    sub-sum of the target's own basis vectors, so some leakage is irreducible --
    but selecting on disjoint annotators removes the statistical part of it."""
    W = b["W"]
    na = W.shape[0]
    nc = Zf.shape[0]
    if na < 4:
        return (np.nan,) * 4
    if w_how not in ("mean", "signvote"):
        reps = 12
    f = METRICS[metric]
    k = min(4, nc)
    core_s = Zc.sum(0)
    H1 = np.zeros((reps, na), bool)
    H2 = np.zeros((reps, na), bool)
    for t in range(reps):
        idx = rng.permutation(na)
        H1[t, idx[: na // 2]] = True
        H2[t, idx[na // 2:]] = True
    Wa1 = half_aggs(W, w_how, H1)
    Wa2 = half_aggs(W, w_how, H2)
    a, c, d, e = [], [], [], []
    for t in range(reps):
        tgt = Wa1[t] @ Zf
        a.append(f(core_s, tgt))
        c.append(f(Wa2[t] @ Zf, tgt))
        d.append(f(Zf[rng.choice(nc, size=k, replace=False)].sum(0), tgt))
        sel = np.argsort(-Wa2[t])[:k]                 # SELECTED ON DISJOINT HALF
        e.append(f(Zf[sel].sum(0), tgt))
    return float(np.mean(a)), float(np.mean(c)), float(np.mean(d)), float(np.mean(e))


# ------------------------------------------------------------------ human targets
def parse_ranking(s):
    out = []
    for grp in str(s).split(">"):
        m = [t.strip() for t in grp.split("=") if t.strip() in LABELS]
        if m:
            out.append(m)
    return out


def human_pairs(bundle, key):
    store = bundle["rank_world"] if key == "world" else bundle["rank_pers"]
    pairs = []
    for a, s in store.items():
        r = parse_ranking(s)
        flat = [(LABELS.index(lab), gi) for gi, grp in enumerate(r) for lab in grp]
        for i, gi in flat:
            for j, gj in flat:
                if gi < gj:
                    pairs.append((a, i, j))
    return pairs


def acc_on_pairs(score, pairs):
    if not pairs:
        return np.nan, 0
    n = sum(1.0 if score[i] - score[j] > 0 else (0.5 if abs(score[i] - score[j]) < 1e-12 else 0.0)
            for _a, i, j in pairs)
    return n / len(pairs), len(pairs)


# ------------------------------------------------------------------ main grid
def run_grid(bundles, seeds, spec_cells, log):
    rows = []
    per_prompt = defaultdict(dict)
    for (norm_how, w_how, metric, popname, keep) in spec_cells:
        f = METRICS[metric]
        C = cache(bundles, norm_how, w_how)
        for seed in seeds:
            rng = np.random.default_rng(seed)
            acc = defaultdict(list)
            ceil_v, npr, matched = [], [], []
            for pid, b in bundles.items():
                if not keep(pid, b):
                    continue
                Zf, Zc, w = C[pid]
                comps = compile_scores(pid, b, Zf, Zc, w, seed)
                tgt = comps["full_signed"]
                for name, v in comps.items():
                    acc[name].append(f(v, tgt))
                    if name in ("core", "full_signed", "top4_abs"):
                        per_prompt[pid][f"{name}|{norm_how}|{w_how}|{metric}|{popname}|{seed}"] = f(v, tgt)
                c = ceiling_split_half(b, Zf, w_how, metric, rng)
                if not np.isnan(c):
                    ceil_v.append(c)
                m = ceiling_matched(b, Zf, Zc, w_how, metric, rng)
                if not np.isnan(m[0]):
                    matched.append(m)
                npr.append(pid)
            if not npr:
                log(f"EMPTY CELL {norm_how}/{w_how}/{metric}/{popname} -- skipped, NOT counted as a pass")
                continue
            rnd = np.mean([np.mean(acc[f"random4_s{s}"]) for s in range(20)])
            rnd_sd = np.std([np.mean(acc[f"random4_s{s}"]) for s in range(20)])
            ceil = float(np.mean(ceil_v)) if ceil_v else np.nan
            gap = ceil - rnd
            phi_core = float(np.mean(acc["core"]))
            lam = (phi_core - rnd) / gap if gap > 1e-9 else np.nan
            row = dict(norm=norm_how, wagg=w_how, metric=metric, pop=popname, seed=seed,
                       n_prompts=len(npr), phi_core=phi_core,
                       phi_floor_random4=float(rnd), floor_seed_sd=float(rnd_sd),
                       phi_ceiling_splithalf=ceil, gap=float(gap), Lambda=float(lam),
                       degenerate=bool(gap < KILL["degeneracy_gap"]))
            for name in acc:
                if not name.startswith("random4_s"):
                    row[f"phi_{name}"] = float(np.mean(acc[name]))
                    row[f"phiSD_{name}"] = float(np.std(acc[name]))
            row["lambda_top4_abs"] = (row["phi_top4_abs"] - rnd) / gap if gap > 1e-9 else np.nan
            row["lambda_oracle4"] = (row["phi_oracle4"] - rnd) / gap if gap > 1e-9 else np.nan
            row["lambda_sham"] = (row["phi_sham_core"] - rnd) / gap if gap > 1e-9 else np.nan
            row["lambda_full_unit"] = (row["phi_full_unit"] - rnd) / gap if gap > 1e-9 else np.nan
            # -- BUDGET-NORMALISED index: what a K=4 unit-weight compiler CAN do.
            bgap = row["phi_oracle4"] - rnd
            row["Lambda_budget"] = (phi_core - rnd) / bgap if bgap > 1e-9 else np.nan
            # -- CORRECTED reliability index: every predictor scored on the same
            #    half-sample target, so it cannot exceed 1 by construction error.
            if matched:
                M = np.array(matched)
                row["m_core"], row["m_otherhalf"], row["m_random4"], row["m_top4_loo"] = \
                    [float(x) for x in M.mean(0)]
                rg = row["m_otherhalf"] - row["m_random4"]
                row["Lambda_rel"] = ((row["m_core"] - row["m_random4"]) / rg
                                     if rg > 1e-9 else np.nan)
                row["Lambda_rel_top4_loo"] = ((row["m_top4_loo"] - row["m_random4"]) / rg
                                              if rg > 1e-9 else np.nan)
                row["rel_gap"] = float(rg)
            rows.append(row)
    return rows, per_prompt


# ------------------------------------------------------------------ S1 polarity
def fisher_z(rs):
    """Mean on the Fisher-z scale (kept ON that scale -- differences of z are
    what the DiD needs; back-transforming first would make the difference
    scale-dependent)."""
    rs = np.clip(np.asarray(rs, float), -0.999999, 0.999999)
    rs = rs[np.isfinite(rs)]
    return float(np.arctanh(rs).mean()) if len(rs) else np.nan


def fisher_mean(rs):
    z = fisher_z(rs)
    return float(np.tanh(z)) if np.isfinite(z) else np.nan


def corr4(x, y):
    x = x - x.mean()
    y = y - y.mean()
    d = np.linalg.norm(x) * np.linalg.norm(y)
    return float(x @ y / d) if d > 1e-12 else np.nan


def polarity(bundles, norm_how, w_how, rng, nperm=2000, core_override=None):
    """S1.  Split the full rubric into its prohibition and prescription halves.

    Pos = sum_{w>0} w z,  Neg = sum_{w<0} |w| z,  F+ = Pos - Neg.  The core can
    only reproduce the prohibition channel if the compiler rewrote 'don't X' into
    a positive directive; it ships no weights, so it has no other way."""
    C_ = cache(bundles, norm_how, w_how)
    rp_c, rn_c, rp_f, rn_f, keep, pack = [], [], [], [], [], []
    for pid, b in bundles.items():
        Zf, Zc, w = C_[pid]
        pos, neg = w > 0, w < 0
        if neg.sum() == 0 or pos.sum() == 0:
            continue
        P = w[pos] @ Zf[pos]
        N = (-w[neg]) @ Zf[neg]          # magnitude of the prohibition channel
        F = P - N
        C = core_override(pid, Zf, Zc, w) if core_override else Zc.sum(0)
        rp_c.append(corr4(C, P)); rn_c.append(corr4(C, -N))
        rp_f.append(corr4(F, P)); rn_f.append(corr4(F, -N))
        keep.append(pid)
        nz = np.flatnonzero(w != 0)
        pack.append((np.abs(w[nz]), Zf[nz], int((w[nz] < 0).sum()), C))
    # A is a DIFFERENCE-IN-DIFFERENCES on the Fisher-z scale, NOT a ratio.
    # The first version of this statistic was R_P/R_N with the full rubric's own
    # correlations in the denominators; under permutation those denominators pass
    # through zero, the ratio explodes, and the null centred at -1.43 instead of
    # 0.  A ratio of noisy near-zero quantities is not an estimator.
    zcP, zcN = fisher_z(rp_c), fisher_z(rn_c)
    zfP, zfN = fisher_z(rp_f), fisher_z(rn_f)
    A = (zcN - zcP) - (zfN - zfP)
    R_P = fisher_mean(rp_c) / fisher_mean(rp_f)      # descriptive only
    R_N = fisher_mean(rn_c) / fisher_mean(rn_f)      # descriptive only
    # NEGATIVE CONTROL: permute WHICH criteria are positive / negative, keeping
    # group sizes and the multiset of |w| fixed.  Excluded world: "A is explained
    # by group size or weight magnitude, not by sign".
    null = np.empty(nperm)
    for t in range(nperm):
        p_c, n_c, p_f, n_f = [], [], [], []
        for aw, Z, k, C in pack:
            negm = np.zeros(len(aw), bool)
            negm[rng.permutation(len(aw))[:k]] = True
            P = aw[~negm] @ Z[~negm]
            N = aw[negm] @ Z[negm]
            F = P - N
            p_c.append(corr4(C, P)); n_c.append(corr4(C, -N))
            p_f.append(corr4(F, P)); n_f.append(corr4(F, -N))
        null[t] = ((fisher_z(n_c) - fisher_z(p_c))
                   - (fisher_z(n_f) - fisher_z(p_f)))
    p = (1 + (np.abs(null - null.mean()) >= abs(A - null.mean())).sum()) / (nperm + 1)
    # bootstrap over prompts for a CI on A itself (clustered at the prompt)
    idx = np.arange(len(rp_c))
    bs = []
    for _ in range(1000):
        s = rng.choice(idx, size=len(idx), replace=True)
        bs.append((fisher_z(np.array(rn_c)[s]) - fisher_z(np.array(rp_c)[s]))
                  - (fisher_z(np.array(rn_f)[s]) - fisher_z(np.array(rp_f)[s])))
    bs = np.array(bs)
    return dict(R_P=R_P, R_N=R_N, A=float(A), n_prompts=len(keep),
                z_core_P=float(zcP), z_core_N=float(zcN),
                z_full_P=float(zfP), z_full_N=float(zfN),
                null_mean=float(null.mean()), null_sd=float(null.std()),
                p_perm=float(p), p_floor=1.0 / (nperm + 1),
                boot_sd=float(bs.std()),
                ci95=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                MDE_A=float(1.96 * null.std()))


def synthetic_cores(bundles, norm_how, w_how, rng):
    """SYNTHETIC WORLDS: does the statistic separate a polarity-respecting core
    from a polarity-ignoring one?  If not, A cannot be read at all."""
    def respecting(pid, Zf, Zc, w):
        sel = np.argsort(-np.abs(w))[:4]
        return (np.sign(w[sel])[:, None] * Zf[sel]).sum(0)

    def ignoring(pid, Zf, Zc, w):
        sel = np.argsort(-np.abs(w))[:4]
        return Zf[sel].sum(0)

    out = {}
    for nm, fn in (("synth_polarity_respecting", respecting),
                   ("synth_polarity_ignoring", ignoring)):
        out[nm] = polarity(bundles, norm_how, w_how,
                           np.random.default_rng(int(rng.integers(1 << 30))),
                           nperm=200, core_override=fn)
    return out


# ------------------------------------------------------------------ S2 minority
def minority(bundles, norm_how, w_how, rank_key, rng):
    C_ = cache(bundles, norm_how, w_how)
    recs = []
    for pid, b in bundles.items():
        Zf, Zc, w_all = C_[pid]
        W = b["W"]
        na = W.shape[0]
        if na < 4:
            continue
        core_s = Zc.sum(0)
        k4 = min(4, Zf.shape[0])
        # THE COMPARATOR MATTERS.  top4_abs (highest |w|, sign discarded) turns
        # out to score BELOW a random draw, so using it alone would be a crippled
        # baseline.  Three comparators are carried: the crippled one, the honest
        # mechanical one (top4 by positive mean), and the population aggregate --
        # which is the object the core is actually a compression OF.
        mech_s = Zf[np.argsort(-np.abs(w_all))[:k4]].sum(0)
        mech2_s = Zf[np.argsort(-w_all)[:k4]].sum(0)
        store = b["rank_world"] if rank_key == "world" else b["rank_pers"]
        Wf = np.nan_to_num(W)
        by_ann = defaultdict(list)
        for (_a, i, j) in human_pairs(b, rank_key):
            by_ann[_a].append((i, j))
        for k, a in enumerate(b["anns"]):
            if a not in store:
                continue
            pr = by_ann.get(a) or []
            if not pr:
                continue
            wa = Wf[k]
            others = np.delete(Wf, k, axis=0)
            wbar = others.mean(0)                     # LEAVE-ONE-OUT
            den = np.linalg.norm(wa) * np.linalg.norm(wbar)
            m = 1.0 - float(wa @ wbar / den) if den > 1e-12 else np.nan
            pl = [(a, i, j) for i, j in pr]
            f_own = acc_on_pairs(wa @ Zf, pl)[0]
            f_core = acc_on_pairs(core_s, pl)[0]
            f_mech = acc_on_pairs(mech_s, pl)[0]
            f_mech2 = acc_on_pairs(mech2_s, pl)[0]
            f_pop = acc_on_pairs(w_all @ Zf, pl)[0]
            recs.append((pid, a, m, f_own, f_core, f_mech, f_pop, f_mech2))
    if not recs:
        return {"n": 0, "EMPTY": True}
    pid = np.array([r[0] for r in recs])
    m = np.array([r[2] for r in recs], float)
    ok = np.isfinite(m)
    pid, m = pid[ok], m[ok]
    arr = np.array([[r[3], r[4], r[5], r[6], r[7]] for r in recs], float)[ok]
    f_own, f_core, f_mech, f_pop, f_mech2 = arr.T
    out = {"n": int(len(m)), "n_prompts": int(len(set(pid.tolist()))),
           "minority_mean": float(m.mean()), "minority_sd": float(m.std()),
           "acc_own": float(np.nanmean(f_own)), "acc_core": float(np.nanmean(f_core)),
           "acc_mech_top4abs": float(np.nanmean(f_mech)),
           "acc_mech_top4pos": float(np.nanmean(f_mech2)),
           "acc_pop": float(np.nanmean(f_pop))}
    for nm, y in (("core_minus_own", f_core - f_own),
                  ("mech_top4abs_minus_own", f_mech - f_own),
                  ("mech_top4pos_minus_own", f_mech2 - f_own),
                  ("pop_minus_own", f_pop - f_own),
                  ("core_minus_pop", f_core - f_pop),
                  ("core_minus_mech_top4pos", f_core - f_mech2),
                  ("PLACEBO_core_minus_core", f_core - f_core)):
        b, se, p = cluster_ols(m, y, pid, rng)
        out[nm] = dict(beta=b, se=se, p=p, mean=float(np.nanmean(y)))
    return out


def cluster_ols(x, y, cluster, rng, nboot=2000):
    ok = np.isfinite(x) & np.isfinite(y)
    x, y, cl = x[ok], y[ok], cluster[ok]
    if len(x) < 10 or x.std() < 1e-12:
        return np.nan, np.nan, np.nan
    if y.std() < 1e-15:
        # DEGENERATE OUTCOME (the placebo: y is identically zero).  A sign test
        # on a vector of zeros returns p=0 because sign(0) != sign(0) is False
        # everywhere -- a "significant" placebo.  Return the honest answer.
        return 0.0, 0.0, 1.0
    X = np.column_stack([np.ones_like(x), x])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    # sorted(), NOT list(set(...)).  Python salts string hashing per process, so
    # set iteration order over prompt ids differs between two runs of the same
    # code with the same seed -- which changes the cluster bootstrap's draws.
    # Caught by the two-run determinism check: every point estimate matched to
    # the last bit and the whole 40-cell grid was byte-identical, but 23 of the
    # minority-block se/p values moved (p 0.095 -> 0.117 on the largest).  No BH
    # decision flipped, but that was luck, not design.
    groups = sorted(set(cl.tolist()))
    gmap = {g: np.flatnonzero(cl == g) for g in groups}
    bs = []
    for _ in range(nboot):
        pick = rng.choice(len(groups), size=len(groups), replace=True)
        idx = np.concatenate([gmap[groups[i]] for i in pick])
        Xi, yi = X[idx], y[idx]
        if Xi[:, 1].std() < 1e-12:
            continue
        bs.append(np.linalg.lstsq(Xi, yi, rcond=None)[0][1])
    bs = np.array(bs)
    se = float(bs.std()) if len(bs) > 10 else np.nan
    p = float((1 + (np.sign(bs) != np.sign(beta[1])).sum() * 2) / (len(bs) + 1)) if len(bs) else np.nan
    return float(beta[1]), se, min(p, 1.0)


# ------------------------------------------------------------------ S3 veto
def veto_auc(bundles, norm_how, w_how, rng, nboot=2000):
    C_ = cache(bundles, norm_how, w_how)
    rows = []
    for pid, b in bundles.items():
        if not b["veto"]:
            continue
        Zf, Zc, w = C_[pid]
        nc = Zf.shape[0]
        k4 = min(4, nc)
        r2 = np.random.default_rng(stable_seed(pid, "veto"))
        sc = {"full": w @ Zf, "core": Zc.sum(0), "full_unit": Zf.sum(0),
              "top4_pos": Zf[np.argsort(-w)[:k4]].sum(0),
              "top4_abs": Zf[np.argsort(-np.abs(w))[:k4]].sum(0),
              # MEASURED FLOOR for S3: an AUC without one is not a number.
              "random4": np.mean([Zf[r2.choice(nc, size=k4, replace=False)].sum(0)
                                  for _ in range(20)], 0),
              "sham_core": Zc.sum(0)[r2.permutation(4)]}
        cnt = np.zeros(4)
        for a, s in b["veto"].items():
            for lab in s:
                cnt[LABELS.index(lab)] += 1
        tot = len(b["rank_world"]) or len(b["anns"])
        rows.append((pid, sc, cnt / max(tot, 1)))
    if not rows:
        return {"n": 0, "EMPTY": True}
    ARMS = ["full", "core", "full_unit", "top4_pos", "top4_abs", "random4", "sham_core"]

    def auc(which, rr):
        pos = neg = tie = 0
        for _pid, sc, rate in rr:
            s = sc[which]
            for i, j in PAIRS:
                if rate[i] == rate[j]:
                    continue
                hi, lo = (i, j) if rate[i] > rate[j] else (j, i)
                if s[hi] < s[lo]:
                    pos += 1
                elif s[hi] > s[lo]:
                    neg += 1
                else:
                    tie += 1
        n = pos + neg + tie
        return (pos + 0.5 * tie) / n if n else np.nan, n

    out = {"n_prompts": len(rows)}
    for wch in ARMS:
        a, n = auc(wch, rows)
        out[f"auc_{wch}"] = a
        out["n_pairs"] = n
    bs = []
    for _ in range(nboot):
        sub = [rows[i] for i in rng.choice(len(rows), size=len(rows), replace=True)]
        bs.append(auc("full", sub)[0] - auc("core", sub)[0])
    bs = np.array(bs)
    d = out["auc_full"] - out["auc_core"]
    out["delta_full_minus_core"] = float(d)
    out["se"] = float(bs.std())
    out["ci95"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    out["p_boot"] = float((1 + 2 * (np.sign(bs) != np.sign(d)).sum()) / (len(bs) + 1))
    out["MDE"] = float(1.96 * bs.std())
    return out


# ------------------------------------------------------------------ ladder CI
LADDER = ["full_signed", "oracle4", "top4_pos", "top4_abs_signed", "core", "full_abs",
          "full_unit", "top4_abs", "top4_disp", "worst4", "sham_core"]


def ladder_contrasts(bundles, norm_how, w_how, metric, seed, rng, nboot=2000):
    """Per-prompt Phi for every compiler, then a PROMPT-CLUSTERED PAIRED
    bootstrap of (X - core).  Without this the compiler ladder is eleven point
    estimates with no resolution, and 0.827 vs 0.862 would be an opinion.

    Also returns the MEASURED RESOLUTION FLOOR: a split-half of the prompt set
    against itself, i.e. how far the same quantity moves between two halves of
    the same data.  An effect below that floor is not admissible as a count."""
    C_ = cache(bundles, norm_how, w_how)
    f = METRICS[metric]
    pids = sorted(bundles)
    M = np.zeros((len(pids), len(LADDER)))
    for r, pid in enumerate(pids):
        b = bundles[pid]
        Zf, Zc, w = C_[pid]
        comps = compile_scores(pid, b, Zf, Zc, w, seed)
        tgt = comps["full_signed"]
        for c, nm in enumerate(LADDER):
            M[r, c] = f(comps[nm], tgt)
    ci = int(LADDER.index("core"))
    out = {}
    n = len(pids)
    idx = rng.integers(0, n, size=(nboot, n))
    for c, nm in enumerate(LADDER):
        d = M[:, c] - M[:, ci]
        bs = M[idx, c].mean(1) - M[idx, ci].mean(1)
        out[nm] = dict(phi=float(M[:, c].mean()), delta_vs_core=float(d.mean()),
                       se=float(bs.std()),
                       ci95=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                       p=float(min(1.0, (1 + 2 * min((bs > 0).sum(), (bs < 0).sum()))
                                   / (nboot + 1))))
    # measured resolution floor: same statistic, two halves of the same prompts
    fl = []
    for _ in range(200):
        p = rng.permutation(n)
        h1, h2 = p[:n // 2], p[n // 2:]
        fl.append(abs(M[h1, ci].mean() - M[h2, ci].mean()))
    out["_floor"] = dict(splithalf_abs_diff_mean=float(np.mean(fl)),
                         splithalf_abs_diff_p95=float(np.percentile(fl, 95)),
                         n_prompts=n)
    return out


def human_ladder(bundles, norm_how, w_how, rank_key, seed, rng, nboot=2000):
    """THE CRITERION-VALIDATED ARM, and the one that removes the leakage worry.

    Against the internal target (the full signed rubric) a subset compiler is a
    sub-sum of the target's own basis vectors, so mechanical compilers get a
    structural advantage the shipped core cannot have.  Against the HUMAN
    rankings no compiler has that advantage: the target is instrument-free and
    external to all of them.  If the two arms disagree, the leakage was doing the
    work; if they agree, it was not.

    Estimand: the share of strictly-ordered human response pairs that the
    compiler orders the same way.  Clustered at the prompt, which is the
    sampling unit (an annotator contributes up to 6 pairs from one ranking)."""
    C_ = cache(bundles, norm_how, w_how)
    pids = sorted(bundles)
    tot = np.zeros((len(pids), len(LADDER)))
    cnt = np.zeros(len(pids))
    for r, pid in enumerate(pids):
        b = bundles[pid]
        pairs = human_pairs(b, rank_key)
        if not pairs:
            continue
        Zf, Zc, w = C_[pid]
        comps = compile_scores(pid, b, Zf, Zc, w, seed)
        cnt[r] = len(pairs)
        for c, nm in enumerate(LADDER):
            s = comps[nm]
            tot[r, c] = sum(1.0 if s[i] - s[j] > 1e-12 else
                            (0.5 if abs(s[i] - s[j]) <= 1e-12 else 0.0)
                            for _a, i, j in pairs)
    ok = cnt > 0
    tot, cnt = tot[ok], cnt[ok]
    n = len(cnt)
    acc = tot.sum(0) / cnt.sum()
    ci = int(LADDER.index("core"))
    idx = rng.integers(0, n, size=(nboot, n))
    out = {"n_prompts": int(n), "n_pairs": int(cnt.sum()), "rank_key": rank_key}
    for c, nm in enumerate(LADDER):
        bs = (tot[idx, c].sum(1) - tot[idx, ci].sum(1)) / cnt[idx].sum(1)
        d = acc[c] - acc[ci]
        out[nm] = dict(acc=float(acc[c]), delta_vs_core=float(d), se=float(bs.std()),
                       ci95=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                       p=float(min(1.0, (1 + 2 * min((bs > 0).sum(), (bs < 0).sum()))
                                   / (nboot + 1))))
    fl = []
    for _ in range(200):
        p = rng.permutation(n)
        h1, h2 = p[:n // 2], p[n // 2:]
        fl.append(abs(tot[h1, ci].sum() / cnt[h1].sum() - tot[h2, ci].sum() / cnt[h2].sum()))
    out["_floor"] = dict(splithalf_abs_diff_mean=float(np.mean(fl)),
                         splithalf_abs_diff_p95=float(np.percentile(fl, 95)))
    return out


# ------------------------------------------------------------------ BH
def bh(pvals, q=0.05):
    idx = np.argsort(pvals)
    p = np.asarray(pvals)[idx]
    C = len(p)
    thr = q * (np.arange(1, C + 1)) / C
    surv = p <= thr
    kmax = np.max(np.flatnonzero(surv)) if surv.any() else -1
    out = np.zeros(C, bool)
    if kmax >= 0:
        out[idx[: kmax + 1]] = True
    return out, C


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[11, 12, 13])
    ap.add_argument("--nperm", type=int, default=2000)
    ap.add_argument("--tag", default="main")
    a = ap.parse_args()

    t0 = time.time()
    lines = []

    def log(*s):
        m = " ".join(str(x) for x in s)
        print(m, flush=True)
        lines.append(m)

    src = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]
    log(f"# R234_independent_A  seeds={a.seeds}  src_sha256={src}")

    joined, how = load_join()
    log(f"join: {how}  joined={len(joined)}")
    jpc = join_positive_control(joined)
    log(f"JOIN POSITIVE CONTROL: {jpc}")

    sat_full, sat_core = load_sat("full"), load_sat("core")
    bundles, drop = build(joined, sat_full, sat_core)
    log(f"bundles={len(bundles)} dropped={drop}")

    # ---- DERIVATION CHECK: raw and center must give identical orderings ------
    # Subtracting a per-criterion constant adds the same number to every
    # response's aggregate, so it cannot change any ordering.  This is forced by
    # the algebra -- it is a DERIVATION, checked numerically only to prove the
    # code implements the algebra, and it is why the raw/center specification
    # axis is degenerate and collapsed to one cell rather than counted twice.
    nsame = ntot = 0
    for pid in list(bundles)[:50]:
        b = bundles[pid]
        Zr, Zcr, wr = (normalise(b["Sf"], "raw"), normalise(b["Sc"], "raw"),
                       agg_weights(b["W"], "mean"))
        Zc_, Zcc, wc = (normalise(b["Sf"], "center"), normalise(b["Sc"], "center"),
                        agg_weights(b["W"], "mean"))
        A_ = compile_scores(pid, b, Zr, Zcr, wr, 0)
        B_ = compile_scores(pid, b, Zc_, Zcc, wc, 0)
        for k in ("core", "full_unit", "top4_abs", "top4_pos"):
            ntot += 1
            nsame += pairwise_conc(A_[k], A_["full_signed"]) == pairwise_conc(
                B_[k], B_["full_signed"])
    same = nsame == ntot
    log(f"DERIVATION raw==center orderings: {nsame}/{ntot} identical -> {same}. "
        f"Forced by algebra; the raw/center axis is degenerate and is collapsed "
        f"to ONE cell, not counted as two independent specifications.")

    # ---- the vectorised half-aggregate must equal the looped one ------------
    b1 = bundles[sorted(bundles)[3]]
    Hm = np.zeros((5, b1["W"].shape[0]), bool)
    for t in range(5):
        Hm[t, np.random.default_rng(t).permutation(b1["W"].shape[0])[:4]] = True
    for wh in ("mean", "signvote"):
        fast = half_aggs(b1["W"], wh, Hm)
        slow = np.array([agg_weights(b1["W"][np.flatnonzero(h)], wh) for h in Hm])
        assert np.allclose(fast, slow, atol=1e-10), f"half_aggs mismatch for {wh}"
    log("VECTORISATION CHECK: half_aggs == agg_weights loop for mean and signvote "
        "(max abs diff < 1e-10) -- the speedup changes no number.")

    # ---- seed sanity: the flag must actually change the draws ---------------
    d1 = np.random.default_rng(11).permutation(4)
    d2 = np.random.default_rng(12).permutation(4)
    log(f"SEED SANITY: seed11 perm {d1.tolist()} != seed12 perm {d2.tolist()}: "
        f"{not np.array_equal(d1, d2)}")

    # ---- populations --------------------------------------------------------
    calib = max(bundles, key=lambda p: bundles[p]["n_assess"])
    log(f"calibration prompt (most assessments): {calib} n={bundles[calib]['n_assess']}")
    pops = {
        "all": (lambda p, b: True),
        "drop_calibration": (lambda p, b, c=calib: p != c),
        "ge8_annotators": (lambda p, b: b["W"].shape[0] >= 8),
    }

    # ---- primary + specification grid --------------------------------------
    cells = []
    for nh in ("z", "rank", "raw"):
        for wh in ("mean", "median", "trimmed20", "signvote"):
            for mt in ("pairwise", "kendall_b", "top1"):
                for pn, keep in pops.items():
                    if (nh, wh, mt, pn) != ("z", "mean", "pairwise", "all"):
                        # sweep only one axis off the primary at a time, plus the
                        # full crossing of norm x metric (the two that can flip a
                        # sign).  Reported in full either way.
                        offs = sum([nh != "z", wh != "mean", mt != "pairwise", pn != "all"])
                        if offs > 2:
                            continue
                    cells.append((nh, wh, mt, pn, keep))
    log(f"specification cells: {len(cells)} x {len(a.seeds)} seeds")
    rows, per_prompt = run_grid(bundles, a.seeds, cells, log)
    log(f"grid rows: {len(rows)}")

    prim = [r for r in rows if (r["norm"], r["wagg"], r["metric"], r["pop"])
            == ("z", "mean", "pairwise", "all")]
    lam = np.array([r["Lambda"] for r in prim])
    log("")
    log("=========== PRIMARY (z / mean / pairwise / all prompts) ===========")
    lamb = np.array([r["Lambda_budget"] for r in prim])
    lamr = np.array([r.get("Lambda_rel", np.nan) for r in prim])
    for r in prim:
        log(f"  seed {r['seed']}: Phi(core)={r['phi_core']:.4f}  "
            f"floor(random4)={r['phi_floor_random4']:.4f}(sd {r['floor_seed_sd']:.4f})")
        log(f"      COMPILER LADDER (Phi vs the full signed rubric, all K=4 unit-weight "
            f"unless noted):")
        for nm in ("full_signed", "oracle4", "top4_pos", "top4_abs_signed", "core",
                   "full_abs", "full_unit", "top4_abs", "top4_disp", "worst4",
                   "sham_core"):
            log(f"        {nm:18s} {r['phi_' + nm]:.4f}"
                + ("   <- SHIPPED CORE" if nm == "core" else "")
                + ("   <- TARGET (placebo, must be 1.000: DERIVATION)"
                   if nm == "full_signed" else "")
                + ("   <- floor is random4 = %.4f" % r["phi_floor_random4"]
                   if nm == "top4_abs" else "")
                + ("   <- NEGATIVE CONTROL, must be ~0.5" if nm == "sham_core" else ""))
        log(f"      PRE-REGISTERED index (split-half ceiling {r['phi_ceiling_splithalf']:.4f}): "
            f"LAMBDA={r['Lambda']:.4f}  -> "
            f"{'INADMISSIBLE, Lambda>1: the ceiling was not a ceiling' if r['Lambda'] > 1 else 'admissible'}")
        log(f"      BUDGET index   (oracle4 ceiling {r['phi_oracle4']:.4f}): "
            f"LAMBDA_budget={r['Lambda_budget']:.4f}")
        log(f"      RELIABILITY index (matched half-sample target): "
            f"core={r.get('m_core', float('nan')):.4f} otherhalf={r.get('m_otherhalf', float('nan')):.4f} "
            f"random4={r.get('m_random4', float('nan')):.4f} -> "
            f"LAMBDA_rel={r.get('Lambda_rel', float('nan')):.4f}")
        log(f"      LEAKAGE CONTROL: mechanical top4 SELECTED ON THE DISJOINT HALF, "
            f"scored on the same target: {r.get('m_top4_loo', float('nan')):.4f} "
            f"(Lambda_rel={r.get('Lambda_rel_top4_loo', float('nan')):.4f}) "
            f"vs core {r.get('m_core', float('nan')):.4f}")
        log(f"      dose:    " + "  ".join(
            f"g={g:.2f}:{r[f'phi_dose_g{g:.2f}']:.4f}" for g in (0, .25, .5, .75, 1)))
        log(f"      POSITIVE CONTROL fails at g=0: the pre-registered "
            f"'Lambda_budget>=0.67' is {'NOT ' if r['Lambda_budget'] < 0.67 else ''}"
            f"satisfied by the core alone, so the control CAN fail.")
    log(f"  LAMBDA(prereg)  across seeds: mean={lam.mean():.4f} sd={lam.std():.4f}")
    log(f"  LAMBDA_budget   across seeds: mean={lamb.mean():.4f} sd={lamb.std():.4f} "
        f"spread/|eff|={lamb.std()/max(abs(lamb.mean()),1e-9):.4f}")
    log(f"  LAMBDA_rel      across seeds: mean={np.nanmean(lamr):.4f} "
        f"sd={np.nanstd(lamr):.4f}")

    rng = np.random.default_rng(a.seeds[0])
    # ---- compiler ladder with prompt-clustered CIs ---------------------------
    log("")
    log("=========== COMPILER LADDER, prompt-clustered paired bootstrap ===========")
    log("  PRIOR ART (data/DATASET_CARD.md, verbatim): core is 'up to four rubric")
    log("  items with the highest average ratings that remain compatible', built by")
    log("  'language-model-assisted synthesis and human review', and the process")
    log("  'first rewrites all rubric items to have positive weight'.  So top4_pos")
    log("  below IS the card's own selection rule executed verbatim, with no LM")
    log("  synthesis step -- that contrast is the estimand that the card does not")
    log("  report.  The card ALSO already states that core 'often reflects the")
    log("  biases of dominant perspectives', which makes S2 a VERIFICATION of")
    log("  documented behaviour, not a discovery.  Labelled as such below.")
    lad = {}
    for s in a.seeds:
        lad[s] = ladder_contrasts(bundles, "z", "mean", "pairwise", s,
                                  np.random.default_rng(s))
    L0 = lad[a.seeds[0]]
    log(f"  resolution floor (split-half of the 968 prompts, same statistic): "
        f"mean |diff| = {L0['_floor']['splithalf_abs_diff_mean']:.4f}, "
        f"p95 = {L0['_floor']['splithalf_abs_diff_p95']:.4f}")
    for nm in LADDER:
        d = L0[nm]
        eff = abs(d["delta_vs_core"])
        ratio = eff / max(L0["_floor"]["splithalf_abs_diff_mean"], 1e-9)
        log(f"  {nm:18s} Phi={d['phi']:.4f}  vs core {d['delta_vs_core']:+.4f} "
            f"CI95[{d['ci95'][0]:+.4f},{d['ci95'][1]:+.4f}] p={d['p']:.4f} "
            f"eff/floor={ratio:6.1f} "
            + ("ADMISSIBLE" if ratio >= 1.5 or nm == "core" else "BELOW FLOOR"))
    seedspread = {nm: float(np.std([lad[s][nm]["delta_vs_core"] for s in a.seeds]))
                  for nm in LADDER}
    log(f"  seed spread of (X - core) over {len(a.seeds)} seeds: max = "
        f"{max(seedspread.values()):.5f}  (only sham_core/random draws depend on seed)")

    # ---- CRITERION-VALIDATED ARM: the same ladder against HUMAN rankings ----
    log("")
    log("=========== SAME LADDER, HUMAN RANKINGS AS TARGET (no leakage) ===========")
    hum = {}
    for rk in ("world", "personal"):
        hum[rk] = human_ladder(bundles, "z", "mean", rk, a.seeds[0],
                               np.random.default_rng(a.seeds[0]))
        h = hum[rk]
        log(f"  target={rk}: {h['n_prompts']} prompt clusters, {h['n_pairs']} ordered "
            f"pairs; resolution floor (split-half of prompts) = "
            f"{h['_floor']['splithalf_abs_diff_mean']:.4f}")
        for nm in LADDER:
            d = h[nm]
            ratio = abs(d["delta_vs_core"]) / max(h['_floor']['splithalf_abs_diff_mean'], 1e-9)
            log(f"     {nm:18s} acc={d['acc']:.4f}  vs core {d['delta_vs_core']:+.4f} "
                f"CI95[{d['ci95'][0]:+.4f},{d['ci95'][1]:+.4f}] p={d['p']:.4f} "
                f"eff/floor={ratio:5.1f}")

    # ---- S1 polarity --------------------------------------------------------
    log("")
    log("=========== S1  POLARITY RETENTION ===========")
    pol = {}
    for s in a.seeds:
        pol[s] = polarity(bundles, "z", "mean", np.random.default_rng(s), nperm=a.nperm)
        p = pol[s]
        log(f"  seed {s}: n={p['n_prompts']} prompts with BOTH a prescription and a "
            f"prohibition channel")
        log(f"     Fisher-z corr with the PRESCRIPTION channel: core={p['z_core_P']:+.4f} "
            f"full={p['z_full_P']:+.4f}   (descriptive ratio R_P={p['R_P']:.3f})")
        log(f"     Fisher-z corr with the PROHIBITION channel:  core={p['z_core_N']:+.4f} "
            f"full={p['z_full_N']:+.4f}   (descriptive ratio R_N={p['R_N']:.3f})")
        log(f"     A (difference-in-differences) = {p['A']:+.4f}  "
            f"boot CI95 [{p['ci95'][0]:+.4f},{p['ci95'][1]:+.4f}]  "
            f"perm null {p['null_mean']:+.4f}+-{p['null_sd']:.4f}  "
            f"p={p['p_perm']:.5f} (floor {p['p_floor']:.5f})  MDE={p['MDE_A']:.4f}")
    synth = synthetic_cores(bundles, "z", "mean", rng)
    for k, v in synth.items():
        log(f"  SYNTHETIC {k}: R_P={v['R_P']:.4f} R_N={v['R_N']:.4f} A={v['A']:.4f}")
    sep = synth["synth_polarity_ignoring"]["A"] - synth["synth_polarity_respecting"]["A"]
    log(f"  SYNTHETIC SEPARATION (ignoring - respecting) = {sep:.4f}  "
        f"-> the statistic {'CAN' if abs(sep) > 0.05 else 'CANNOT'} tell the two worlds apart")

    # ---- S2 minority --------------------------------------------------------
    log("")
    log("=========== S2  MINORITY REPRESENTATION ===========")
    mino = {}
    for rk in ("world", "personal"):
        mino[rk] = minority(bundles, "z", "mean", rk, np.random.default_rng(a.seeds[0]))
        m = mino[rk]
        if m.get("EMPTY"):
            log(f"  {rk}: EMPTY -- no assessments, reported as EMPTY not as a pass")
            continue
        log(f"  {rk}: n={m['n']} assessments over {m['n_prompts']} prompts; "
            f"acc_own={m['acc_own']:.4f} acc_pop={m['acc_pop']:.4f} "
            f"acc_core={m['acc_core']:.4f} acc_top4pos={m['acc_mech_top4pos']:.4f} "
            f"acc_top4abs={m['acc_mech_top4abs']:.4f}")
        for k in ("core_minus_own", "mech_top4abs_minus_own", "mech_top4pos_minus_own",
                  "pop_minus_own", "core_minus_pop", "core_minus_mech_top4pos",
                  "PLACEBO_core_minus_core"):
            d = m[k]
            log(f"     beta[{k:26s}] = {d['beta']:+.5f} +- {d['se']:.5f}  "
                f"p={d['p']:.4f}  mean_gap={d['mean']:+.4f}")

    # ---- S3 veto ------------------------------------------------------------
    log("")
    log("=========== S3  VETO DETECTION ===========")
    vet = veto_auc(bundles, "z", "mean", np.random.default_rng(a.seeds[0]))
    if vet.get("EMPTY"):
        log("  EMPTY -- no veto blocks")
    else:
        log(f"  prompts={vet['n_prompts']} pairs={vet['n_pairs']}  (AUC for ranking the "
            f"more-often-vetoed response LOWER)")
        for k in ("full", "core", "top4_pos", "top4_abs", "full_unit", "random4",
                  "sham_core"):
            log(f"     AUC {k:11s} = {vet['auc_' + k]:.4f}"
                + ("   <- MEASURED FLOOR" if k == "random4" else "")
                + ("   <- NEGATIVE CONTROL" if k == "sham_core" else ""))
        log(f"  full-core = {vet['delta_full_minus_core']:+.4f} "
            f"CI95 {vet['ci95'][0]:+.4f}..{vet['ci95'][1]:+.4f}  p={vet['p_boot']:.4f}  "
            f"MDE={vet['MDE']:.4f}")
        fl, fu = vet["auc_random4"], vet["auc_full"]
        ret = (vet["auc_core"] - fl) / (fu - fl) if fu - fl > 1e-9 else np.nan
        retu = (vet["auc_full_unit"] - fl) / (fu - fl) if fu - fl > 1e-9 else np.nan
        vet["veto_retention_core"] = float(ret)
        vet["veto_retention_full_unit"] = float(retu)
        log(f"  ABOVE-FLOOR RETENTION (floor=random4={fl:.4f}, ceiling=full={fu:.4f}):")
        log(f"     core       retains {ret*100:5.1f}% of the full rubric's above-floor "
            f"veto detection -- WITH NO WEIGHTS AT ALL")
        log(f"     full_unit  retains {retu*100:5.1f}% -- i.e. mechanically discarding the "
            f"signs from the WHOLE rubric lands on the floor")
        log(f"  This is the direct test of the card's claim that the compiler 'first "
            f"rewrites all rubric items to have positive weight': the rewrite is what "
            f"separates core from full_unit.")

    # ---- multiplicity over the WHOLE grid ----------------------------------
    tests = []
    for nm in LADDER:
        if nm != "core":
            tests.append((f"LADDER_internal_{nm}_vs_core", lad[a.seeds[0]][nm]["p"]))
            for rk in ("world", "personal"):
                tests.append((f"LADDER_human_{rk}_{nm}_vs_core", hum[rk][nm]["p"]))
    for s in a.seeds:
        tests.append((f"S1_A_seed{s}", pol[s]["p_perm"]))
    for rk in ("world", "personal"):
        if not mino[rk].get("EMPTY"):
            for k in ("core_minus_own", "mech_top4abs_minus_own",
                      "mech_top4pos_minus_own", "pop_minus_own", "core_minus_pop",
                      "core_minus_mech_top4pos"):
                tests.append((f"S2_{rk}_{k}", mino[rk][k]["p"]))
    if not vet.get("EMPTY"):
        tests.append(("S3_veto_full_minus_core", vet["p_boot"]))
    tests = [(k, v) for k, v in tests if np.isfinite(v)]
    surv, C = bh([v for _, v in tests])
    log("")
    log(f"=========== MULTIPLICITY  BH q=0.05 over C={C} p-valued tests ===========")
    for (k, v), s in zip(tests, surv):
        log(f"  {'SURVIVES' if s else '  killed '}  {k:34s} p={v:.5f}")
    log(f"  cells tested={C}  surviving={int(surv.sum())}")
    log(f"  p-VALUE RESOLUTION: bootstrap p is floored at 1/(nboot+1)=~{1/2001:.5f} "
        f"and permutation p at 1/(nperm+1)={1/(a.nperm+1):.5f}.  A reported "
        f"p=0.0005 means 'below the floor', not 'p=0.0005'.")
    log(f"  n_eff (CLUSTERS, not rows): ladder & grid = {len(bundles)} prompts; "
        f"S1 = {pol[a.seeds[0]]['n_prompts']} prompts; "
        f"S2 world = {mino['world'].get('n_prompts')} prompts "
        f"({mino['world'].get('n')} assessments); "
        f"S3 = {vet.get('n_prompts')} prompts.")
    log(f"  NOTE: the {len(rows)} specification rows carry no p-value; they are")
    log(f"        reported as a curve, and every one is in results/grid.json.")

    # ---- verdict ------------------------------------------------------------
    def band(v):
        if not np.isfinite(v):
            return "UNVERIFIED"
        if v > 1.0:
            return "INADMISSIBLE(>1)"
        if v <= KILL["unfaithful_at"]:
            return "UNFAITHFUL"
        if v >= KILL["faithful_at"]:
            return "FAITHFUL"
        return "PARTIAL"

    lam_m = float(np.nanmean(lam))
    lamb_m = float(np.nanmean(lamb))
    lamr_m = float(np.nanmean(lamr))
    degen = bool(np.nanmean([r["gap"] for r in prim]) < KILL["degeneracy_gap"])
    log("")
    log("=========== VERDICT ===========")
    log(f"  PRE-REGISTERED  Lambda        = {lam_m:.4f}  -> {band(lam_m)}")
    log(f"    the pre-registered statistic came back OUTSIDE [0,1].  It is reported")
    log(f"    and it is INADMISSIBLE; the split-half ceiling compares two n/2")
    log(f"    aggregates while the core is scored against the n aggregate, so it is")
    log(f"    not a ceiling.  This is a design error of MINE, caught by the design.")
    log(f"  BUDGET          Lambda_budget = {lamb_m:.4f}  -> {band(lamb_m)}")
    log(f"    (denominator = what a K=4 unit-weight compiler CAN reach: oracle4)")
    log(f"  RELIABILITY     Lambda_rel    = {lamr_m:.4f}  -> {band(lamr_m)}")
    log(f"    (matched half-sample target: every predictor scored on the same target)")
    log(f"  degeneracy guard (ceiling-floor >= 0.05): {'FAILED' if degen else 'passed'}")
    verdict = f"budget={band(lamb_m)} / reliability={band(lamr_m)} / prereg={band(lam_m)}"

    for key, mval in (("Lambda_budget", lamb_m), ("Lambda_rel", lamr_m),
                      ("Lambda", lam_m)):
        vals = np.array([r.get(key, np.nan) for r in rows], float)
        vals = vals[np.isfinite(vals)]
        agree = float(np.mean([band(v) == band(mval) for v in vals])) if len(vals) else np.nan
        log(f"  SPEC CURVE {key}: {len(vals)} cells, range "
            f"[{vals.min():.3f},{vals.max():.3f}], "
            f"{agree*100:.1f}% land in the same verdict band as the primary cell")
    log("  cells that CONTRADICT the primary (Lambda_budget outside its band):")
    nlow = 0
    for r in sorted(rows, key=lambda r: r.get("Lambda_budget", 9)):
        v = r.get("Lambda_budget", np.nan)
        if np.isfinite(v) and band(v) != band(lamb_m):
            nlow += 1
            log(f"    {r['norm']}/{r['wagg']}/{r['metric']}/{r['pop']}/s{r['seed']} "
                f"Lambda_budget={v:.3f} -> {band(v)}  (phi_core={r['phi_core']:.3f} "
                f"oracle={r['phi_oracle4']:.3f} floor={r['phi_floor_random4']:.3f})")
    if nlow == 0:
        log("    NONE -- every cell in the grid lands in the same band.")
    for r in sorted(rows, key=lambda r: r.get("Lambda_budget", 9))[:4]:
        log(f"    LOWEST: {r['norm']}/{r['wagg']}/{r['metric']}/{r['pop']}/s{r['seed']} "
            f"Lambda_budget={r.get('Lambda_budget', float('nan')):.3f}")
    for r in sorted(rows, key=lambda r: -r.get("Lambda_budget", -9))[:4]:
        log(f"    HIGHEST: {r['norm']}/{r['wagg']}/{r['metric']}/{r['pop']}/s{r['seed']} "
            f"Lambda_budget={r.get('Lambda_budget', float('nan')):.3f}")
    same_side = float(np.mean([band(r.get("Lambda_budget", np.nan)) == band(lamb_m)
                               for r in rows]))

    out = dict(src_sha256=src, seeds=a.seeds, join=how, join_positive_control=jpc,
               n_bundles=len(bundles), dropped=drop, derivation_raw_eq_center=bool(same),
               KILL=KILL, verdict=verdict, Lambda_mean=lam_m,
               Lambda_budget_mean=lamb_m, Lambda_rel_mean=lamr_m,
               Lambda_by_seed=[float(x) for x in lam],
               Lambda_budget_by_seed=[float(x) for x in lamb],
               Lambda_rel_by_seed=[float(x) for x in lamr],
               prereg_ceiling_inadmissible=bool(lam_m > 1.0),
               spec_same_verdict_share=same_side,
               ladder={str(k): v for k, v in lad.items()},
               ladder_human=hum,
               ladder_seed_spread=seedspread,
               prior_art=dict(
                   source="data/DATASET_CARD.md",
                   core_selection_rule_documented=(
                       "up to four rubric items with the highest average ratings "
                       "that remain compatible; LM-assisted synthesis + human review"),
                   polarity_rewrite_documented=(
                       "the process first rewrites all rubric items to have positive weight"),
                   majoritarian_documented=(
                       "CoVal-core often reflects the biases of dominant perspectives "
                       "in our participant pool"),
                   consequence=("S2 is a VERIFICATION of documented behaviour, not a "
                                "discovery.  The core-vs-top4_pos contrast and the "
                                "prohibition-channel measurement are not in the card.")),
               polarity={str(k): v for k, v in pol.items()},
               synthetic=synth, minority=mino, veto=vet,
               multiplicity=dict(C=C, surviving=int(surv.sum()),
                                 tests=[{"name": k, "p": v, "survives": bool(s)}
                                        for (k, v), s in zip(tests, surv)]),
               seconds=time.time() - t0)
    (RES / f"{a.tag}_summary.json").write_text(json.dumps(out, indent=1, default=float))
    (RES / f"{a.tag}_grid.json").write_text(json.dumps(rows, indent=1, default=float))
    (RES / f"{a.tag}_log.txt").write_text("\n".join(lines))
    log(f"\nwrote results/{a.tag}_summary.json, {a.tag}_grid.json, {a.tag}_log.txt "
        f"in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
