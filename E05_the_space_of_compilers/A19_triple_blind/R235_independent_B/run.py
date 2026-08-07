#!/usr/bin/env python
r"""
R235_independent_B -- IS THE COMPILED CORE A FAITHFUL COMPRESSION OF THE FULL RUBRIC?

Independent design, seed 29.  Written against ~/.claude/skills/realstat/SKILL.md.
This docstring is the pre-registration: estimand, identification, worlds, kill
thresholds and controls were written and committed to file BEFORE any number in
sections C-E was computed.  (Sections A1-A2 -- the gauge/identification checks --
were run first ON PURPOSE, because they decide whether the design is admissible at
all; their outcome is reported and they can kill the round.)

================================================================================
G1 . ESTIMAND BEFORE METHOD
================================================================================

"Faithful compression" is a claim about a FUNCTION, not about text.  A rubric's
function is to ORDER candidate responses.  So the compression is faithful iff the
compressed rubric induces the same ordering as the thing it compressed -- and is
worth having iff that ordering still tracks the people the rubric came from.

But a raw comparison `fidelity(core) vs fidelity(full)` is uninterpretable, because
it confounds three different losses that the compiler does not equally control:

    (i)  BUDGET    15.5 criteria -> ~4.  Any 4-criterion rubric loses information.
    (ii) FORMAT    signed weights in [-10,+10] -> unsigned directives.  The core
                   literally cannot express "do NOT do this".
    (iii) SELECTION which 4.  <- THIS is the only thing the compiler chooses.

So the estimand fixes (i) and (ii) and measures (iii), anchored between two
quantities that are MEASURED on the same instrument, same responses, same people:

  PRIMARY ESTIMAND  --  compiler efficiency  eta

      eta = ( F(core) - F(rand_B) ) / ( F(best_B) - F(rand_B) )

      B          = the core's own size for that prompt (4, sometimes 3, once 2)
      F(rho)     = mean fidelity of the ordering induced by rubric rho
      rand_B     = a uniformly random B-subset of the FULL rubric's criteria.
                   Computed EXACTLY (all C(K,B) subsets enumerated), not sampled.
      best_B     = the B-subset whose ordering best matches the target, SELECTED ON
                   A HELD-OUT HALF OF THE ANNOTATORS and evaluated on the other half.

      eta = 1  the compiler is as good as an oracle selection at its own budget
      eta = 0  the compiler is indistinguishable from choosing 4 criteria at random
      eta < 0  the compiler is WORSE than random: compilation is anti-faithful

  Two targets, run as CO-PRIMARY because they can dissociate and the dissociation
  is itself the finding:

      INTRINSIC  target = the ordering the FULL rubric itself induces (consensus
                 signed weights).  This is the literal reading of "faithful
                 compression of the full rubric" and needs no human ranking.
      EXTRINSIC  target = the ordering the PERSON actually wrote (personal / world).
                 This asks whether the compression preserves the decision that the
                 rubric existed to support.

  SECONDARY ESTIMANDS
      rho_format = F(best_B | unsigned uniform weights) / F(best_B | signed weights)
                   -- how much of the achievable fidelity the core's FORMAT forbids,
                   independent of how good the compiler is.
      inv        = fraction of (person, prompt) assessments the rubric ACTIVELY
                   INVERTS (tau_b < 0), for core vs full-consensus vs full-personal.
                   A compression of a plural object can preserve the majority and
                   destroy the minority; a mean fidelity cannot see that.

================================================================================
IDENTIFICATION (asked before power)
================================================================================
A1  If satisfaction were additively separable, sat(c,r) = a_c + b_r, then for any
    positive-weight rubric  score(r) = sum_c w_c a_c + (sum_c w_c) b_r, so EVERY
    rubric induces the SAME ordering and eta is 0/0.  The design is then degenerate
    and no threshold is admissible (realstat s4, "floor == ceiling").
    => measure the criterion x response INTERACTION share of variance.  GATE.
A2  Even with interaction, a given prompt may admit only one achievable ordering
    across all C(K,B) subsets.  => measure, per prompt, the number of achievable
    orderings and the max ordering frequency.  This is the DESIGN'S RESOLUTION and
    it caps eta's meaning.  Reported; prompts with 1 achievable ordering are
    carried in the main population and also split out as a spec cell.
A3  The extrinsic arm needs a positive control before any null is admissible: does
    the FULL rubric predict human rankings above chance at all?  If not, the
    extrinsic arm is SILENCE, not an acquittal.

    PARTIAL IDENTIFICATION.  Only 44.4% of (annotator, criterion) weight cells are
    filled and the score 0 is essentially never used (1 of 102,147).  "Not rated"
    and "rated zero" are therefore not distinguishable in this release.  Consensus
    weight is treated two ways (mean-of-observed, and sum/n with missing:=0) and
    both are carried as specification cells.  Nothing here identifies which is right.

================================================================================
WORLDS (>=2, ontologically different, with a prediction matrix)
================================================================================
  W1 FAITHFUL COMPILER      eta_intrinsic high AND eta_extrinsic high.
  W2 DECISION-INERT OBJECT  F(full) ~ chance vs humans.  Then the core loses
                            nothing because there was nothing to lose; "faithful"
                            is true and vacuous.  Distinguished by A3.
  W3 MAJORITY CAPTURE       eta high on the consensus target, but `inv` for the
                            core >> `inv` for full-personal.  The compression is
                            faithful to the average and unfaithful to the plural.
  W4 FORMAT-CAPPED          F(best_B|unsigned) << F(best_B|signed).  Then no
                            compiler in this output format can be faithful and the
                            deficiency is structural, not a compilation error.
  Prediction matrix: A3 separates W2 from the rest; rho_format separates W4;
  `inv` separates W3; eta separates W1 from "no better than random".

================================================================================
KILL, PRE-REGISTERED WITH THRESHOLDS
================================================================================
  K1  PRIMARY CELL = (judge=main, satnorm=raw, weighting=uniform, target=intrinsic,
      metric=tau_b).  If the 95% cluster-bootstrap CI for Delta = F(core)-F(rand_B)
      contains 0 -> "better than an arbitrary compression" is NOT SUPPORTED.
  K2  If Delta < 0 with CI excluding 0 in a MAJORITY of grid cells -> INVERTED.
  K3  If eta's CI upper bound < 0.5 -> "faithful" is downgraded to "directional".
  K4  If the SHAM compiler (top-B by how many people rated the criterion -- budget
      and format matched, zero selection intelligence) attains an eta whose CI
      overlaps the core's, the compilation adds nothing beyond a trivial heuristic.
  K5  If (F(best_B) - F(rand_B)) <= 2x the MEASURED noise floor in a cell, that cell
      is UNVERIFIED -- no verdict, in either direction.

================================================================================
CONTROLS
================================================================================
  POSITIVE (dose-response, and it can fail at g=0):  plant a synthetic "core" made
      of j criteria drawn from the held-out oracle subset and B-j at random,
      j=0..B.  Run it through the identical pipeline.  Requirements: eta(j=0) CI
      must CONTAIN 0 (the control is able to fail), eta must be monotone in j, and
      eta(j=B) is the retention.  MDE reported from the same bootstrap.
  NEGATIVE:  keep the response main effect b_r, independently permute each
      criterion's INTERACTION RESIDUAL across the four responses.  Preserves every
      marginal, every weight, every target, the criterion count and the main
      effect; destroys only which response a criterion actually favours.
      The world it excludes: "all this fidelity is one response simply being better
      and every criterion agreeing".  Under it, Delta must go to 0.
  SHAM:  top-B by rater count -- same budget, same unsigned format, same compute,
      minus the ingredient under study (selection intelligence).
  PLACEBO:  two independent random B-subsets; their fidelity difference must be 0.
      (Zero expectation here is a DERIVATION by symmetry -- it tests the plumbing,
      the aggregation and the bootstrap, not the phenomenon.  Labelled as such.)
  NOISE FLOOR:  MEASURED, by splitting annotators in half within prompt and
      recomputing the same statistic on each half, over 5 seeds.  effect/floor is
      reported per P14 and no count is quoted below 1.5.
  CEILING BEFORE THRESHOLD:  F(best_B) is computed before eta is thresholded, and a
      cell where floor and ceiling are not separated by 2x the noise floor is
      declared UNVERIFIED rather than passed.

================================================================================
SPECIFICATION GRID (reported whole, including cells that kill the finding)
================================================================================
  judge      main | phi | qwen3b            (966 prompts)
             v_default | v_nofewshot | v_swapped   (300 prompts, prompt variants)
  satnorm    raw | z   (z = per-criterion z-score across the 4 responses; this
             makes the statistic invariant to per-criterion affine rescaling of the
             judge, which is the gauge the judge is free in)
  weighting  uniform (+1, matched to the core's information state)
             | signed (consensus mean weight)
  target     intrinsic | personal | world
  metric     tau_b | top1 | pair | veto (predicted-worst falls in the person's
             "unacceptable" block -- a different field of the release entirely)
  seeds      5, controlling annotator half-splits, plants and bootstrap draws
  multiplicity  BH q=0.05 over the WHOLE grid; non-survivors reported.

STRUCTURALLY IMPOSSIBLE HERE (realstat s2), each with what it would require:
  causally identified / interventionally validated : re-running the compiler with a
      criterion held out.  Requires the compiler, which the release does not ship.
  independently replicated : a second release, or the triple-blind arms.
  temporally resolved : per-criterion timestamps; not in the release.
  construct validated : an external gold standard for "the right ordering".  There
      is none; the whole point of the dataset is that there is none.
  cross-dataset / cross-domain : one release.
  position randomized : no presentation-order field for the four responses.

================================================================================
ADDENDUM, written after the first run.  The pre-registration above is UNCHANGED;
this records what the run forced me to add, and why.  (Annotate, never rewrite.)
================================================================================
(1) THE PRE-REGISTERED NEGATIVE CONTROL WAS NOT A NEGATIVE CONTROL.
    NC0 permutes each criterion's interaction residual across responses while
    preserving the response main effect.  Under it, Delta did NOT go to zero: it
    stayed at +0.144 against a real +0.160 for target=world, weighting=uniform.
    The reason is arithmetic, and it is a GAUGE failure of the control, not evidence
    about the object: an unsigned uniformly-weighted rubric scores a response by the
    MEAN satisfaction of its criteria, and NC0 preserves every column mean exactly.
    So the quantity the control was meant to destroy is the one it holds fixed.
    Kept and reported as a control that cannot fail; two controls that CAN were added
    (NC1 foreign core, NC2 response-shuffled core), and `core_ordering_unchanged`
    reports the invariance directly.
(2) THE PRE-REGISTERED SHAM WAS TOO WEAK.  `top_pop` (the B most-rated criteria) sits
    at eta ~ 0.23.  The results named a stronger trivial compiler -- `top_w`, the B
    criteria with the highest consensus weight -- which BEATS the core on the
    intrinsic target.  K4' adds a paired bootstrap of (core - top_w) in every cell.
    Declaring this after seeing it is a real weakness and it is labelled as post hoc;
    the pre-registered K4 verdict is reported separately and unchanged.
(3) SCOPE FOUND IN THE DATA, NOT IN THE DESCRIPTION.  `personal` rankings exist for
    only 30.1% of assessments, concentrated in 29.8% of prompts (a prompt-level split:
    70% of prompts have none at all, 30% have them for nearly every assessment).
    `world` is the extrinsic target of record; every `personal` number is scoped.
(4) eta CAN EXCEED 1, and does, because the held-out oracle ceiling is itself
    estimated on half the annotators and is therefore noisy downward, while the core
    is a fixed object that pays no such penalty.  `eta_in` (normalised by the
    IN-SAMPLE oracle, a strict upper bound) is reported alongside every eta.
"""
import json, pickle, hashlib, itertools, sys, time, math, warnings
from pathlib import Path
from math import comb
import numpy as np

warnings.filterwarnings("ignore", message="Mean of empty slice")
warnings.filterwarnings("ignore", message="All-NaN slice encountered")
warnings.filterwarnings("ignore", category=RuntimeWarning)

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)

SEEDS = [29, 1729, 4242, 80085, 31337]
NBOOT = 2000
LETTERS = "ABCD"

# ---------------------------------------------------------------- orderings ---
ORD = sorted(set(itertools.permutations(range(4))))          # 24 rank-vectors
O2I = {o: i for i, o in enumerate(ORD)}
CODE = np.full(256, -1, dtype=np.int16)
for o, i in O2I.items():
    CODE[o[0] * 64 + o[1] * 16 + o[2] * 4 + o[3]] = i
ORDA = np.array(ORD, dtype=np.int8)                          # (24,4)
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]


def _tau_top_pair(pred_ranks, targ_ranks):
    """pred (24,4) strict ranks, targ (n,4) ranks with ties (0=best).
    returns tau_b (24,n), top1 (24,n), pair (24,n), valid_tau (n,), valid_pair (n,)"""
    P = pred_ranks[:, None, :]                                # (24,1,4)
    T = targ_ranks[None, :, :]                                # (1,n,4)
    C = np.zeros((P.shape[0], T.shape[1]))
    D = np.zeros_like(C)
    ty = np.zeros(T.shape[1])
    for (i, j) in PAIRS:
        sp = np.sign(P[..., j] - P[..., i])                   # +1 if i better
        st = np.sign(T[..., j] - T[..., i])
        C += (sp * st > 0)
        D += (sp * st < 0)
        ty += (st[0] == 0)
    n_un = 6.0 - ty                                            # untied target pairs
    den = np.sqrt(6.0 * n_un)
    with np.errstate(invalid="ignore", divide="ignore"):
        tau = (C - D) / den[None, :]
        pair = C / n_un[None, :]
    best_pred = np.argmin(pred_ranks, axis=1)                  # (24,)
    top1 = (targ_ranks[None, :, :][0][:, best_pred].T == 0).astype(float)  # (24,n)
    return tau, top1, pair, (n_un > 0), (n_un > 0)


def ordering_tables(rank, veto):
    """rank (n,4) int (may contain -1 rows meaning absent); veto (n,4) bool."""
    ok = (rank[:, 0] >= 0)
    n = rank.shape[0]
    tau = np.full((24, n), np.nan)
    top1 = np.full((24, n), np.nan)
    pair = np.full((24, n), np.nan)
    if ok.any():
        t, o, p, vt, vp = _tau_top_pair(ORDA, rank[ok])
        tau[:, ok] = t
        top1[:, ok] = o
        pair[:, ok] = p
    # veto: predicted-worst must be a response the person called unacceptable
    worst = np.argmax(ORDA, axis=1)                            # (24,)
    nv = veto.sum(1)
    vok = (nv >= 1) & (nv <= 3)
    vt = np.full((24, n), np.nan)
    vt[:, vok] = veto[vok][:, worst].T.astype(float)
    return dict(tau_b=tau, top1=top1, pair=pair, veto=vt)


# 24x24 ordering-vs-ordering tables, for the INTRINSIC target
def _oo_tables():
    t, o, p, _, _ = _tau_top_pair(ORDA, ORDA)
    return dict(tau_b=t, top1=o, pair=p)
OO = _oo_tables()

# --------------------------------------------------------------- subset cache -
_SUBCACHE = {}
def subsets_for(K, B):
    key = (K, B)
    if key not in _SUBCACHE:
        _SUBCACHE[key] = np.array(list(itertools.combinations(range(K), B)), dtype=np.int32)
    return _SUBCACHE[key]


def order_code(scores):
    """scores (...,4) -> ordering index (...,), deterministic alphabetical tie-break."""
    scores = np.atleast_2d(scores)
    order = np.argsort(-scores, axis=1, kind="stable")
    ranks = np.empty_like(order)
    np.put_along_axis(ranks, order, np.arange(4)[None, :].repeat(order.shape[0], 0), axis=1)
    code = ranks[:, 0] * 64 + ranks[:, 1] * 16 + ranks[:, 2] * 4 + ranks[:, 3]
    return CODE[code]


def znorm(S):
    m = S.mean(1, keepdims=True)
    s = S.std(1, keepdims=True)
    s = np.where(s < 1e-9, 1.0, s)
    return (S - m) / s


# ================================================================= SECTION A ==
def section_A(recs, judges):
    """gauge / identification.  These gates can kill the round."""
    res = {}
    for j in judges:
        tot = vr = vc = vi = 0.0
        for r in recs.values():
            if j not in r["sat"]:
                continue
            M = r["sat"][j][0].astype(np.float64)
            g = M.mean(); rm = M.mean(0); cm = M.mean(1)
            sst = ((M - g) ** 2).sum()
            ssr = M.shape[0] * ((rm - g) ** 2).sum()
            ssc = 4 * ((cm - g) ** 2).sum()
            tot += sst; vr += ssr; vc += ssc; vi += sst - ssr - ssc
        res[j] = dict(response_main=vr / tot, criterion_main=vc / tot, interaction=vi / tot)
    return res


# ================================================================= SECTION B ==
def enumerate_cell(recs, judge, satnorm, weighting, wmiss="obs"):
    """For every prompt: the ordering histogram over all C(K,B) subsets, plus the
    ordering induced by the core, the full rubric, and the reference compilers."""
    out = {}
    ties = 0; nsub_tot = 0
    for pid, r in recs.items():
        if judge not in r["sat"]:
            continue
        Sf, Sc = r["sat"][judge][0].astype(np.float64), r["sat"][judge][1].astype(np.float64)
        if satnorm == "z":
            Sf, Sc = znorm(Sf), znorm(Sc)
        K, B = r["K"], r["M"]
        W = r["W"].astype(np.float64)
        nrat = (~np.isnan(W)).sum(0)
        with np.errstate(invalid="ignore"):
            wmean = np.nanmean(W, axis=0)
        wmean = np.nan_to_num(wmean, nan=0.0)
        wzero = np.nan_to_num(W, nan=0.0).sum(0) / W.shape[0]
        w = {"uniform": np.ones(K), "signed": wmean, "signed_m0": wzero}[weighting]

        contrib = w[:, None] * Sf
        subs = subsets_for(K, B)
        cs = contrib[subs].sum(1)                                  # (C,4)
        nsub_tot += cs.shape[0]
        srt = np.sort(cs, axis=1)
        ties += int((np.diff(srt, axis=1) == 0).any(1).sum())
        codes = order_code(cs)
        hist = np.bincount(codes, minlength=24).astype(np.float64)

        # compilers
        o_core = int(order_code(Sc.sum(0)[None, :])[0])            # uniform +1 on core
        o_full = int(order_code(contrib.sum(0)[None, :])[0])
        pos = np.maximum(wmean, 0.0)
        o_full_pos = int(order_code((pos[:, None] * Sf).sum(0)[None, :])[0])
        o_full_sgn = int(order_code((wmean[:, None] * Sf).sum(0)[None, :])[0])

        def topsel(key):
            idx = np.argsort(-key, kind="stable")[:B]
            return int(order_code(contrib[idx].sum(0)[None, :])[0]), idx
        o_absw, _ = topsel(np.abs(wmean))
        o_w, _ = topsel(wmean)
        o_pop, _ = topsel(nrat.astype(float))

        # per-annotator personal-weight ordering (extrinsic only)
        Wp = np.nan_to_num(W, nan=0.0)
        o_pers = order_code(Wp @ Sf)                               # (n_ann_w,)

        out[pid] = dict(hist=hist, C=cs.shape[0], subs=subs, codes=codes.astype(np.int8),
                        o_core=o_core, o_full=o_full, o_full_pos=o_full_pos,
                        o_full_sgn=o_full_sgn, o_absw=o_absw, o_w=o_w, o_pop=o_pop,
                        o_pers=o_pers, K=K, B=B, w=w, wmean=wmean, Sf=Sf, Sc=Sc, W=W)
    return out, dict(tie_subsets=ties, n_subsets=nsub_tot,
                     tie_rate=ties / max(nsub_tot, 1))


# ================================================================= SECTION C ==
def eval_cell(recs, cell, target, metric, seed, tabs):
    """Return per-prompt values for every compiler, plus resolution diagnostics.
    Oracle selection is HELD OUT: annotators are split in half, the oracle ordering
    is chosen on one half and scored on the other, symmetrised over both folds."""
    rng = np.random.default_rng(seed)
    names = ["core", "rand", "best_ho", "best_in", "worst_in", "top_absw", "top_w",
             "top_pop", "full", "full_pos", "full_pers", "half_noise", "target_reliab"]
    acc = {k: [] for k in names}
    resol = []
    pids = []
    for pid, c in cell.items():
        r = recs[pid]
        hist = c["hist"]; Cn = c["C"]
        avail = np.nonzero(hist)[0]
        freq = hist / Cn

        if target == "intrinsic":
            # target = ordering induced by consensus signed weights on a half of the
            # annotators; oracle selected against the other half's ordering.
            W = c["W"]; n = W.shape[0]
            if n < 2:
                continue
            perm = rng.permutation(n)
            h1, h2 = perm[: n // 2], perm[n // 2:]
            def cons(ix):
                with np.errstate(invalid="ignore"):
                    wm = np.nanmean(W[ix], axis=0)
                return np.nan_to_num(wm, nan=0.0)
            t1 = int(order_code((cons(h1)[:, None] * c["Sf"]).sum(0)[None, :])[0])
            t2 = int(order_code((cons(h2)[:, None] * c["Sf"]).sum(0)[None, :])[0])
            tab = OO[metric] if metric in OO else None
            if tab is None:
                continue
            folds = [(t1, t2), (t2, t1)]
            vals = {k: [] for k in names}
            for fi, (ttr, tte) in enumerate(folds):
                v_te = tab[:, tte]                      # (24,) value of each ordering
                v_tr = tab[:, ttr]
                o_star = avail[int(np.argmax(v_tr[avail]))]
                vals["best_ho"].append(v_te[o_star])
                vals["best_in"].append(float(np.max(v_te[avail])))
                vals["worst_in"].append(float(np.min(v_te[avail])))
                vals["rand"].append(float((freq[avail] * v_te[avail]).sum()))
                vals["core"].append(v_te[c["o_core"]])
                vals["top_absw"].append(v_te[c["o_absw"]])
                vals["top_w"].append(v_te[c["o_w"]])
                vals["top_pop"].append(v_te[c["o_pop"]])
                vals["full"].append(v_te[c["o_full"]])
                vals["full_pos"].append(v_te[c["o_full_pos"]])
                vals["full_pers"].append(np.nan)
                # how far the fidelity estimate moves when the ANNOTATOR SAMPLE is
                # resampled: same compiler, other half of the people.  fold 0 only,
                # because the two folds are exact negatives of each other.
                vals["half_noise"].append(v_te[c["o_core"]] - v_tr[c["o_core"]] if fi == 0 else np.nan)
                # split-half reproducibility of the TARGET itself = reliability ceiling
                vals["target_reliab"].append(tab[ttr, tte])
            for k in names:
                with np.errstate(invalid="ignore"):
                    acc[k].append(float(np.nanmean(vals[k])) if not np.all(np.isnan(vals[k])) else np.nan)
            spread = float(np.max(OO[metric][:, t2][avail]) - np.min(OO[metric][:, t2][avail]))
        else:
            T = tabs[pid][target][metric]                 # (24, n_assess)
            has = ~np.isnan(T[0])
            idx = np.nonzero(has)[0]
            if len(idx) < 2:
                continue
            perm = rng.permutation(len(idx))
            h1, h2 = idx[perm[: len(idx) // 2]], idx[perm[len(idx) // 2:]]
            vals = {k: [] for k in names}
            for fi, (tr, te) in enumerate([(h1, h2), (h2, h1)]):
                v_te = np.nanmean(T[:, te], axis=1)
                v_tr = np.nanmean(T[:, tr], axis=1)
                o_star = avail[int(np.argmax(v_tr[avail]))]
                vals["best_ho"].append(v_te[o_star])
                vals["best_in"].append(float(np.max(v_te[avail])))
                vals["worst_in"].append(float(np.min(v_te[avail])))
                vals["rand"].append(float((freq[avail] * v_te[avail]).sum()))
                vals["core"].append(v_te[c["o_core"]])
                vals["top_absw"].append(v_te[c["o_absw"]])
                vals["top_w"].append(v_te[c["o_w"]])
                vals["top_pop"].append(v_te[c["o_pop"]])
                vals["full"].append(v_te[c["o_full"]])
                vals["full_pos"].append(v_te[c["o_full_pos"]])
                # personal: each assessor scored by the ordering their OWN weights give
                rw = r["ranker_w"]
                pv = []
                for a in te:
                    wi = rw[a]
                    if wi >= 0:
                        pv.append(T[c["o_pers"][wi], a])
                vals["full_pers"].append(float(np.nanmean(pv)) if pv else np.nan)
                vals["half_noise"].append(v_te[c["o_core"]] - v_tr[c["o_core"]] if fi == 0 else np.nan)
                # target reliability: the ordering the train half likes best, scored
                # by the test half, relative to what the test half's own best is
                vals["target_reliab"].append(v_te[int(np.argmax(v_tr))] - float(np.max(v_te)))
            for k in names:
                with np.errstate(invalid="ignore"):
                    acc[k].append(float(np.nanmean(vals[k])) if not np.all(np.isnan(vals[k])) else np.nan)
            v_all = np.nanmean(T, axis=1)
            spread = float(np.max(v_all[avail]) - np.min(v_all[avail]))
        resol.append((len(avail), float(freq.max()), spread))
        pids.append(pid)
    return ({k: np.array(v) for k, v in acc.items()}, np.array(resol), pids)


# ================================================================= bootstrap ==
def cluster_boot(mat, seed, nboot=NBOOT):
    """mat (n_prompts, n_series) -> (nboot, n_series) bootstrap means over prompts."""
    rng = np.random.default_rng(seed)
    n = mat.shape[0]
    idx = rng.integers(0, n, size=(nboot, n))
    counts = np.zeros((nboot, n), dtype=np.float32)
    for b in range(nboot):
        counts[b] = np.bincount(idx[b], minlength=n)
    good = ~np.isnan(mat)
    M = np.nan_to_num(mat, nan=0.0)
    num = counts @ M
    den = counts @ good.astype(np.float32)
    with np.errstate(invalid="ignore", divide="ignore"):
        return num / np.where(den == 0, np.nan, den)


def ci(x, lo=2.5, hi=97.5):
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return (np.nan, np.nan)
    return (float(np.percentile(x, lo)), float(np.percentile(x, hi)))


def bh(pvals, q=0.05):
    p = np.asarray(pvals, float)
    ok = ~np.isnan(p)
    idx = np.nonzero(ok)[0]
    o = idx[np.argsort(p[idx])]
    C = len(o)
    thr = q * (np.arange(1, C + 1)) / C
    passed = p[o] <= thr
    k = np.nonzero(passed)[0]
    cut = p[o][k.max()] if len(k) else -1
    out = np.zeros_like(p, dtype=bool)
    out[ok] = p[ok] <= cut
    return out, (thr[-1] if C else np.nan)


# ==================================================================== driver ==
def main():
    t0 = time.time()
    D = pickle.load(open(OUT / "prepared.pkl", "rb"))
    recs = D["recs"]
    print(f"[load] {len(recs)} prompts  ({time.time()-t0:.1f}s)")

    JUDGES_FULL = ["main", "phi", "qwen3b"]
    JUDGES_VAR = ["v_default", "v_nofewshot", "v_swapped"]
    ALLJ = JUDGES_FULL + JUDGES_VAR

    R = {"meta": dict(n_prompts=len(recs),
                      n_assessments=int(sum(len(r["rank_ann"]) for r in recs.values())),
                      seeds=SEEDS, nboot=NBOOT,
                      join_control=D["join_control"],
                      src_sha=hashlib.sha256(open(__file__, "rb").read()).hexdigest()[:16])}

    # ---------------- A0 scope ----------------
    hp = np.array([r["has_personal"].mean() for r in recs.values()])
    hw = np.array([r["has_world"].mean() for r in recs.values()])
    nrat = np.concatenate([(~np.isnan(r["W"])).mean(0) for r in recs.values()])
    R["A0_scope"] = dict(
        n_prompts=len(recs),
        n_assessments=int(sum(len(r["rank_ann"]) for r in recs.values())),
        frac_assessments_with_personal=float(hp.mean()),
        frac_assessments_with_world=float(hw.mean()),
        frac_prompts_zero_personal=float((hp == 0).mean()),
        frac_prompts_near_full_personal=float((hp > 0.9).mean()),
        weight_matrix_fill_rate=float(nrat.mean()),
        note=("`personal` is a PROMPT-LEVEL design split of the release: 70% of prompts "
              "carry no personal ranking at all and 30% carry it for nearly every "
              "assessment.  It is therefore a valid subpopulation, not an "
              "outcome-selected one -- but every `personal` number below holds only "
              "over that ~29% of prompts.  `world` has 100% coverage and is the "
              "extrinsic target of record."))
    print("[A0]", json.dumps({k: v for k, v in R["A0_scope"].items() if k != "note"}))

    # ---------------- seed flag actually changes the draws ----------------
    _a = np.random.default_rng(SEEDS[0]).permutation(50)
    _b = np.random.default_rng(SEEDS[1]).permutation(50)
    R["seed_flag_live"] = bool(not np.array_equal(_a, _b))
    assert R["seed_flag_live"], "seed flag is inert"
    R["reproducibility"] = dict(note="two runs at the same seed must be byte-identical; "
                                     "checked on the primary cell after the grid is built")

    # ---------------- A1 gauge ----------------
    R["A1_variance_decomposition"] = section_A(recs, ALLJ)
    print("[A1]", json.dumps(R["A1_variance_decomposition"]["main"]))

    # ---------------- per-prompt target tables (judge-independent) ------------
    tabs = {}
    for pid, r in recs.items():
        tabs[pid] = dict(
            personal=ordering_tables(r["rank_personal"], r["veto"]),
            world=ordering_tables(r["rank_world"], r["veto"]),
        )
    print(f"[tabs] built ({time.time()-t0:.1f}s)")

    # ---------------- enumeration cells ----------------
    cells = {}
    encfg = []
    for j in ALLJ:
        for sn in ["raw", "z"]:
            for wt in ["uniform", "signed"]:
                encfg.append((j, sn, wt))
    # extra specification cell: missing weights read as 0 instead of dropped
    encfg.append(("main", "raw", "signed_m0"))
    encfg.append(("main", "z", "signed_m0"))
    for (j, sn, wt) in encfg:
        cells[(j, sn, wt)], diag = enumerate_cell(recs, j, sn, wt)
        R.setdefault("B_enumeration", {})[f"{j}|{sn}|{wt}"] = dict(
            prompts=len(cells[(j, sn, wt)]), **{k: float(v) for k, v in diag.items()})
        print(f"[enum] {j:12s} {sn:3s} {wt:9s} prompts={len(cells[(j,sn,wt)]):4d} "
              f"subsets={diag['n_subsets']:9d} tie-rate={diag['tie_rate']:.2e} "
              f"({time.time()-t0:.1f}s)")

    # ---------------- A2 resolution ----------------
    c0 = cells[("main", "raw", "uniform")]
    navail = np.array([int((c["hist"] > 0).sum()) for c in c0.values()])
    maxfreq = np.array([float(c["hist"].max() / c["C"]) for c in c0.values()])
    R["A2_resolution"] = dict(
        mean_achievable_orderings=float(navail.mean()),
        median_achievable_orderings=float(np.median(navail)),
        frac_prompts_single_ordering=float((navail == 1).mean()),
        mean_max_ordering_freq=float(maxfreq.mean()),
        frac_prompts_maxfreq_gt_0p95=float((maxfreq > 0.95).mean()),
        hist_achievable=np.bincount(navail, minlength=25)[:25].tolist(),
    )
    print("[A2]", json.dumps({k: v for k, v in R["A2_resolution"].items() if k != "hist_achievable"}))

    # ---------------- C : the grid ----------------
    GRID = []
    for (j, sn, wt) in encfg:
        for tg in ["intrinsic", "personal", "world"]:
            for mt in (["tau_b", "top1", "pair"] if tg == "intrinsic"
                       else ["tau_b", "top1", "pair", "veto"]):
                GRID.append((j, sn, wt, tg, mt))
    print(f"[grid] {len(GRID)} cells")

    grid_rows = []
    for gi, (j, sn, wt, tg, mt) in enumerate(GRID):
        per_seed = []
        for s in SEEDS:
            vals, resol, pids = eval_cell(recs, cells[(j, sn, wt)], tg, mt, s, tabs)
            per_seed.append((vals, resol))
        keys = list(per_seed[0][0].keys())
        # average over seeds at the prompt level (seeds only reshuffle the split)
        n = len(per_seed[0][0]["core"])
        stack = {k: np.nanmean(np.stack([ps[0][k] for ps in per_seed]), axis=0) for k in keys}
        seed_spread = {k: float(np.nanstd([np.nanmean(ps[0][k]) for ps in per_seed])) for k in keys}
        mat = np.stack([stack[k] for k in keys], axis=1)
        boot = cluster_boot(mat, seed=SEEDS[0] + gi)
        col = {k: i for i, k in enumerate(keys)}
        m = {k: float(np.nanmean(stack[k])) for k in keys}
        d_core = boot[:, col["core"]] - boot[:, col["rand"]]
        d_sham = boot[:, col["top_pop"]] - boot[:, col["rand"]]
        gap = boot[:, col["best_ho"]] - boot[:, col["rand"]]
        gap_in = boot[:, col["best_in"]] - boot[:, col["rand"]]
        with np.errstate(invalid="ignore", divide="ignore"):
            eta = np.where(np.abs(gap) > 1e-12, d_core / gap, np.nan)
            eta_sham = np.where(np.abs(gap) > 1e-12, d_sham / gap, np.nan)
            # THE COMPILER LADDER: every reference compiler on the same scale, so the
            # core's eta can be read against what trivial rules already achieve.
            ladder = {}
            for k in ["core", "top_w", "top_absw", "top_pop", "full", "full_pos",
                      "best_ho", "best_in", "worst_in"]:
                dk = boot[:, col[k]] - boot[:, col["rand"]]
                ladder[k] = dict(mean=float(np.nanmean(boot[:, col[k]])),
                                 eta=float(np.nanmean(np.where(np.abs(gap) > 1e-12, dk / gap, np.nan))),
                                 eta_ci=ci(np.where(np.abs(gap) > 1e-12, dk / gap, np.nan)),
                                 eta_in=float(np.nanmean(np.where(np.abs(gap_in) > 1e-12,
                                                                  dk / gap_in, np.nan))))
            # is the core BEATEN by a trivial weight-ranked compiler?  bootstrap the
            # paired difference, not two CIs read against each other.
            d_vs_topw = boot[:, col["core"]] - boot[:, col["top_w"]]
            d_vs_full = boot[:, col["core"]] - boot[:, col["full"]]
            with np.errstate(invalid="ignore", divide="ignore"):
                retention = np.where(np.abs(boot[:, col["full"]]) > 1e-9,
                                     boot[:, col["core"]] / boot[:, col["full"]], np.nan)
        # MEASURED noise floors, two of them, both from replicates not from a model:
        #  (a) annotator resample: the same compiler scored by two disjoint halves of
        #      the people; the bootstrap sd of that difference / sqrt(2).
        #  (b) prompt resample: the bootstrap sd of Delta itself.
        nf_ann = float(np.nanstd(boot[:, col["half_noise"]]) / math.sqrt(2))
        nf_pr = float(np.nanstd(d_core))
        row = dict(judge=j, satnorm=sn, weighting=wt, target=tg, metric=mt,
                   n_prompts=int(n), means=m, seed_spread=seed_spread,
                   delta_core=float(np.nanmean(d_core)), delta_core_ci=ci(d_core),
                   delta_sham=float(np.nanmean(d_sham)), delta_sham_ci=ci(d_sham),
                   headroom=float(np.nanmean(gap)), headroom_ci=ci(gap),
                   eta=float(np.nanmean(eta)), eta_ci=ci(eta),
                   eta_in=float(np.nanmean(np.where(np.abs(gap_in) > 1e-12, d_core / gap_in, np.nan))),
                   eta_sham=float(np.nanmean(eta_sham)), eta_sham_ci=ci(eta_sham),
                   ladder=ladder,
                   core_minus_topw=float(np.nanmean(d_vs_topw)), core_minus_topw_ci=ci(d_vs_topw),
                   # THE RELIABILITY BENCHMARK.  `target_reliab` is what the target
                   # scores against ITSELF when the annotator sample is split in half.
                   # A compression cannot sensibly be asked to beat that.  If
                   # core - target_reliab has a CI containing 0, the core reproduces
                   # the full rubric to within the rubric's own sampling noise.
                   core_minus_reliab=float(np.nanmean(boot[:, col["core"]] - boot[:, col["target_reliab"]])),
                   core_minus_reliab_ci=ci(boot[:, col["core"]] - boot[:, col["target_reliab"]]),
                   target_reliab=float(np.nanmean(boot[:, col["target_reliab"]])),
                   core_minus_full=float(np.nanmean(d_vs_full)), core_minus_full_ci=ci(d_vs_full),
                   retention_core_over_full=float(np.nanmean(retention)), retention_ci=ci(retention),
                   p_two_sided=float(max(2 * min((d_core <= 0).mean(), (d_core >= 0).mean()),
                                         1.0 / NBOOT)),
                   se=nf_pr,
                   mde=float(2.8 * nf_pr),
                   noise_floor_annotator=nf_ann,
                   noise_floor_prompt=nf_pr,
                   effect_over_floor=float(abs(np.nanmean(d_core)) / nf_pr) if nf_pr > 0 else np.nan,
                   ci_width_over_effect=float(
                       (ci(d_core)[1] - ci(d_core)[0]) / abs(np.nanmean(d_core)))
                       if abs(np.nanmean(d_core)) > 1e-12 else np.nan,
                   # K5: a cell whose ceiling is not separated from its floor by 2x the
                   # measured noise cannot return a verdict in EITHER direction.
                   K5_admissible=bool(np.nanmean(gap) > 2 * nf_pr),
                   resolution=dict(mean_navail=float(np.nanmean(per_seed[0][1][:, 0])),
                                   mean_maxfreq=float(np.nanmean(per_seed[0][1][:, 1])),
                                   mean_spread=float(np.nanmean(per_seed[0][1][:, 2]))))
        grid_rows.append(row)
        if gi % 12 == 0:
            print(f"  [{gi:3d}/{len(GRID)}] {j:11s} {sn} {wt:7s} {tg:9s} {mt:6s} "
                  f"eta={row['eta']:+.3f} d={row['delta_core']:+.4f} "
                  f"headroom={row['headroom']:.4f} ({time.time()-t0:.0f}s)")

    # determinism: same seed, same input -> byte-identical draws
    _v1, _, _ = eval_cell(recs, cells[("main", "raw", "uniform")], "intrinsic", "tau_b", SEEDS[0], tabs)
    _v2, _, _ = eval_cell(recs, cells[("main", "raw", "uniform")], "intrinsic", "tau_b", SEEDS[0], tabs)
    R["reproducibility"] = dict(
        byte_identical_same_seed=bool(all(
            hashlib.sha256(_v1[k].tobytes()).hexdigest() == hashlib.sha256(_v2[k].tobytes()).hexdigest()
            for k in _v1)),
        hash_primary=hashlib.sha256(
            np.stack([_v1[k] for k in sorted(_v1)]).tobytes()).hexdigest()[:16])
    assert R["reproducibility"]["byte_identical_same_seed"]

    ps = [r["p_two_sided"] for r in grid_rows]
    surv, _ = bh(ps, 0.05)
    for r, s in zip(grid_rows, surv):
        r["bh_survives"] = bool(s)
    R["C_grid"] = grid_rows
    R["C_multiplicity"] = dict(cells_tested=len(grid_rows), cells_surviving_bh=int(surv.sum()),
                               q=0.05,
                               n_delta_positive=int(sum(r["delta_core"] > 0 for r in grid_rows)),
                               n_delta_negative=int(sum(r["delta_core"] < 0 for r in grid_rows)),
                               n_ci_excludes_zero=int(sum(
                                   (r["delta_core_ci"][0] > 0) or (r["delta_core_ci"][1] < 0)
                                   for r in grid_rows)),
                               n_ci_excl_zero_negative=int(sum(
                                   r["delta_core_ci"][1] < 0 for r in grid_rows)))
    print("[C]", json.dumps(R["C_multiplicity"]))

    with open(OUT / "grid.json", "w") as f:
        json.dump(R, f, indent=1, default=float)
    print(f"[write] grid.json  ({time.time()-t0:.0f}s)")

    # ---------------- D : controls ----------------
    R["D_controls"] = controls(recs, cells, tabs, t0)

    # ---------------- E : verdict against the pre-registered kills -------------
    def find(**kw):
        for r in grid_rows:
            if all(r[k] == v for k, v in kw.items()):
                return r
        return None
    prim = find(judge="main", satnorm="raw", weighting="uniform",
                target="intrinsic", metric="tau_b")
    adm = [r for r in grid_rows if r["K5_admissible"]]
    R["E_verdict"] = dict(
        primary_cell=prim,
        K1_delta_ci_excludes_zero=bool(prim["delta_core_ci"][0] > 0 or prim["delta_core_ci"][1] < 0),
        K2_majority_negative_significant=bool(
            sum(r["delta_core_ci"][1] < 0 for r in grid_rows) > len(grid_rows) / 2),
        K3_eta_ci_upper_below_half=bool(prim["eta_ci"][1] < 0.5),
        K4_sham_overlaps_core=bool(prim["eta_sham_ci"][1] >= prim["eta_ci"][0]
                                   and prim["eta_ci"][1] >= prim["eta_sham_ci"][0]),
        # K4', added after the fact and labelled as such: `top_pop` was the
        # pre-registered sham, but the results named a STRONGER trivial compiler --
        # take the B criteria with the highest consensus weight.  A paired bootstrap
        # of core - top_w is the honest test, and it is reported for every cell.
        K4prime_core_minus_topw=prim["core_minus_topw"],
        K4prime_core_minus_topw_ci=prim["core_minus_topw_ci"],
        K4prime_cells_where_topw_beats_core_significantly=int(sum(
            r["core_minus_topw_ci"][1] < 0 for r in grid_rows)),
        K4prime_cells_where_core_beats_topw_significantly=int(sum(
            r["core_minus_topw_ci"][0] > 0 for r in grid_rows)),
        K5_cells_admissible=len(adm), K5_cells_total=len(grid_rows),
        eta_across_admissible_cells=dict(
            median=float(np.nanmedian([r["eta"] for r in adm])),
            q10=float(np.nanpercentile([r["eta"] for r in adm], 10)),
            q90=float(np.nanpercentile([r["eta"] for r in adm], 90)),
            frac_above_0p5=float(np.mean([r["eta"] > 0.5 for r in adm])),
            frac_below_0=float(np.mean([r["eta"] < 0 for r in adm]))),
        eta_sham_across_admissible=dict(
            median=float(np.nanmedian([r["eta_sham"] for r in adm]))),
        cells_that_contradict=[
            dict(judge=r["judge"], satnorm=r["satnorm"], weighting=r["weighting"],
                 target=r["target"], metric=r["metric"], eta=r["eta"],
                 delta=r["delta_core"], delta_ci=r["delta_core_ci"],
                 effect_over_floor=r["effect_over_floor"])
            for r in grid_rows
            if (r["delta_core_ci"][0] <= 0 <= r["delta_core_ci"][1]) or r["eta"] < 0.5],
    )
    with open(OUT / "results.json", "w") as f:
        json.dump(R, f, indent=1, default=float)
    print(f"[write] results.json  ({time.time()-t0:.0f}s)")
    print("[E]", json.dumps({k: v for k, v in R["E_verdict"].items()
                             if k not in ("primary_cell", "cells_that_contradict")}, default=float))

    # ---------------- F : a readable specification curve, whole ----------------
    with open(OUT / "specification_curve.tsv", "w") as f:
        cols = ["judge", "satnorm", "weighting", "target", "metric", "n_prompts",
                "core", "rand", "best_ho", "best_in", "top_w", "top_pop", "full",
                "target_reliab", "delta_core", "ci_lo", "ci_hi", "eta", "eta_lo",
                "eta_hi", "eta_in", "eta_topw", "core_minus_topw", "cmt_lo", "cmt_hi",
                "core_minus_reliab", "cmr_lo", "cmr_hi", "retention", "effect_over_floor",
                "p", "bh_survives", "K5_admissible"]
        f.write("\t".join(cols) + "\n")
        for r in grid_rows:
            m = r["means"]; L = r["ladder"]
            f.write("\t".join(str(x) for x in [
                r["judge"], r["satnorm"], r["weighting"], r["target"], r["metric"], r["n_prompts"],
                f"{m['core']:.4f}", f"{m['rand']:.4f}", f"{m['best_ho']:.4f}", f"{m['best_in']:.4f}",
                f"{m['top_w']:.4f}", f"{m['top_pop']:.4f}", f"{m['full']:.4f}",
                f"{r['target_reliab']:.4f}",
                f"{r['delta_core']:.4f}", f"{r['delta_core_ci'][0]:.4f}", f"{r['delta_core_ci'][1]:.4f}",
                f"{r['eta']:.4f}", f"{r['eta_ci'][0]:.4f}", f"{r['eta_ci'][1]:.4f}", f"{r['eta_in']:.4f}",
                f"{L['top_w']['eta']:.4f}",
                f"{r['core_minus_topw']:.4f}", f"{r['core_minus_topw_ci'][0]:.4f}", f"{r['core_minus_topw_ci'][1]:.4f}",
                f"{r['core_minus_reliab']:.4f}", f"{r['core_minus_reliab_ci'][0]:.4f}", f"{r['core_minus_reliab_ci'][1]:.4f}",
                f"{r['retention_core_over_full']:.4f}", f"{r['effect_over_floor']:.2f}",
                f"{r['p_two_sided']:.5f}", int(r["bh_survives"]), int(r["K5_admissible"])]) + "\n")
    print(f"[write] specification_curve.tsv  ({time.time()-t0:.0f}s)")


# ================================================================= SECTION D ==
def plant_orderings(cell, tabs, recs, target, metric, seed):
    """POSITIVE CONTROL with dose-response.  A synthetic 'core' of j oracle criteria
    plus B-j random ones, j = 0..B.  j=0 must NOT pass (the control can fail)."""
    rng = np.random.default_rng(seed)
    doses = {}
    for pid, c in cell.items():
        r = recs[pid]
        K, B = c["K"], c["B"]
        if target == "intrinsic":
            W = c["W"]; n = W.shape[0]
            if n < 2:
                continue
            perm = rng.permutation(n); h1, h2 = perm[: n // 2], perm[n // 2:]
            with np.errstate(invalid="ignore"):
                w1 = np.nan_to_num(np.nanmean(W[h1], axis=0), nan=0.0)
                w2 = np.nan_to_num(np.nanmean(W[h2], axis=0), nan=0.0)
            t1 = int(order_code((w1[:, None] * c["Sf"]).sum(0)[None, :])[0])
            t2 = int(order_code((w2[:, None] * c["Sf"]).sum(0)[None, :])[0])
            v_tr, v_te = OO[metric][:, t1], OO[metric][:, t2]
        else:
            T = tabs[pid][target][metric]
            has = ~np.isnan(T[0]); idx = np.nonzero(has)[0]
            if len(idx) < 2:
                continue
            p2 = rng.permutation(len(idx))
            h1, h2 = idx[p2[: len(idx) // 2]], idx[p2[len(idx) // 2:]]
            v_tr, v_te = np.nanmean(T[:, h1], axis=1), np.nanmean(T[:, h2], axis=1)
        codes, subs = c["codes"], c["subs"]
        avail = np.nonzero(c["hist"])[0]
        o_star = avail[int(np.argmax(v_tr[avail]))]
        cand = np.nonzero(codes == o_star)[0]
        star = subs[cand[0]]                                   # a subset achieving it
        contrib = c["w"][:, None] * c["Sf"]
        freq = c["hist"] / c["C"]
        for jd in range(B + 1):
            take = list(star[:jd])
            pool = [k for k in range(K) if k not in take]
            if len(pool) < B - jd:
                continue
            take = take + list(rng.choice(pool, size=B - jd, replace=False))
            o = int(order_code(contrib[take].sum(0)[None, :])[0])
            d = doses.setdefault(jd, {"plant": [], "rand": [], "best": []})
            d["plant"].append(v_te[o])
            d["rand"].append(float((freq[avail] * v_te[avail]).sum()))
            d["best"].append(v_te[o_star])
    out = {}
    for jd, d in sorted(doses.items()):
        pl = np.array(d["plant"]); rd = np.array(d["rand"]); bs = np.array(d["best"])
        mat = np.stack([pl, rd, bs], 1)
        bt = cluster_boot(mat, seed=seed + 7 * jd, nboot=800)
        gap = bt[:, 2] - bt[:, 1]
        with np.errstate(invalid="ignore", divide="ignore"):
            eta = np.where(np.abs(gap) > 1e-12, (bt[:, 0] - bt[:, 1]) / gap, np.nan)
        out[jd] = dict(n=int(len(pl)), delta=float(np.nanmean(pl - rd)),
                       delta_ci=ci(bt[:, 0] - bt[:, 1]),
                       eta=float(np.nanmean(eta)), eta_ci=ci(eta))
    return out


def core_path_control(recs, cell, tabs, target, metric, seed):
    """POSITIVE CONTROL ON THE CORE CODE PATH, and it can fail.
    The core is read through one specific route: its own satisfaction matrix Sc,
    summed with uniform weights, turned into an ordering.  Replace Sc by the rows of
    a KNOWN subset of the full rubric and re-run the identical route.  If the route
    is right, planting the (target-agnostic) oracle subset must return eta near 1 and
    planting a random subset must return eta near 0 with a CI containing 0."""
    out = {}
    rng = np.random.default_rng(seed)
    plants = {}
    for pid, c in cell.items():
        contrib = c["w"][:, None] * c["Sf"]
        # target-agnostic "good" subset: the one whose ordering matches the FULL
        # rubric's own ordering under signed consensus weights (chosen without ever
        # looking at the evaluation target's held-out half)
        v = OO["tau_b"][:, c["o_full_sgn"]]
        avail = np.nonzero(c["hist"])[0]
        o_good = avail[int(np.argmax(v[avail]))]
        cand = np.nonzero(c["codes"] == o_good)[0]
        good_idx = c["subs"][cand[0]]
        rnd_idx = rng.choice(c["K"], size=c["B"], replace=False)
        plants[pid] = (int(order_code(contrib[good_idx].sum(0)[None, :])[0]),
                       int(order_code(contrib[rnd_idx].sum(0)[None, :])[0]))
    for label, k in [("planted_good", 0), ("planted_random", 1)]:
        cell2 = {pid: dict(c, o_core=plants[pid][k]) for pid, c in cell.items()}
        vals, _, _ = eval_cell(recs, cell2, target, metric, seed, tabs)
        keys = list(vals.keys())
        mat = np.stack([vals[kk] for kk in keys], 1)
        bt = cluster_boot(mat, seed=seed + 17, nboot=800)
        col = {kk: i for i, kk in enumerate(keys)}
        d = bt[:, col["core"]] - bt[:, col["rand"]]
        gap = bt[:, col["best_ho"]] - bt[:, col["rand"]]
        with np.errstate(invalid="ignore", divide="ignore"):
            eta = np.where(np.abs(gap) > 1e-12, d / gap, np.nan)
        out[label] = dict(delta=float(np.nanmean(d)), delta_ci=ci(d),
                          eta=float(np.nanmean(eta)), eta_ci=ci(eta))
    return out


def _score_fake(recs, tabs, fake, judge, satnorm, weighting, target, metric, seed):
    cell, _ = enumerate_cell(fake, judge, satnorm, weighting)
    vals, _, _ = eval_cell(recs, cell, target, metric, seed, tabs)
    keys = list(vals.keys())
    mat = np.stack([vals[k] for k in keys], 1)
    bt = cluster_boot(mat, seed=seed + 11, nboot=800)
    col = {k: i for i, k in enumerate(keys)}
    d = bt[:, col["core"]] - bt[:, col["rand"]]
    gap = bt[:, col["best_ho"]] - bt[:, col["rand"]]
    with np.errstate(invalid="ignore", divide="ignore"):
        eta = np.where(np.abs(gap) > 1e-12, d / gap, np.nan)
    return dict(delta=float(np.nanmean(d)), delta_ci=ci(d),
                eta=float(np.nanmean(eta)), eta_ci=ci(eta),
                headroom=float(np.nanmean(gap)),
                core_level=float(np.nanmean(bt[:, col["core"]])),
                full_vs_target=float(np.nanmean(bt[:, col["full"]])),
                rand_level=float(np.nanmean(bt[:, col["rand"]])))


def negative_controls(recs, tabs, judge, satnorm, weighting, target, metric, seed):
    """THREE negative controls, because the first one turned out not to be one.

    NC0  keep the response main effect, permute each criterion's INTERACTION
         RESIDUAL across responses.  This was the pre-registered control.  Its own
         result exposed a gauge failure: an unsigned uniformly-weighted rubric scores
         a response by the MEAN satisfaction over its criteria, and NC0 preserves
         every column mean by construction -- so the statistic is nearly invariant
         under it and it CANNOT drive Delta to zero.  Kept and reported, labelled as
         a control that does not control (realstat s4: "check that cannot fail",
         mirror image).  `core_ordering_unchanged` measures the invariance directly.
    NC1  FOREIGN CORE: give each prompt another prompt's compiled core (matched on
         core size).  Destroys the core<->prompt correspondence and nothing else.
         Excludes the world: "any four compiled-style directives scored by this judge
         would order responses this way; the content of THIS core is irrelevant."
    NC2  RESPONSE-SHUFFLED CORE: permute the four response columns of the core's
         satisfaction matrix (one permutation per prompt).  Destroys the
         core<->response alignment exactly, preserves the core's own criterion
         structure, its level, its spread and its budget.  Delta must go to zero."""
    out = {}

    # ---- NC0
    rng = np.random.default_rng(seed)
    fake0 = {}
    unchanged = 0; tot = 0
    for pid, r in recs.items():
        if judge not in r["sat"]:
            continue
        Sf, Sc = (r["sat"][judge][0].astype(np.float64).copy(),
                  r["sat"][judge][1].astype(np.float64).copy())
        before = int(order_code(Sc.sum(0)[None, :])[0])
        for S in (Sf, Sc):
            b = S.mean(0, keepdims=True); R_ = S - b
            for i in range(S.shape[0]):
                R_[i] = R_[i][rng.permutation(4)]
            S[:] = b + R_
        after = int(order_code(Sc.sum(0)[None, :])[0])
        unchanged += (before == after); tot += 1
        fake0[pid] = dict(r); fake0[pid]["sat"] = dict(r["sat"])
        fake0[pid]["sat"][judge] = (Sf.astype(np.float32), Sc.astype(np.float32))
    out["NC0_residual_permute"] = _score_fake(recs, tabs, fake0, judge, satnorm,
                                              weighting, target, metric, seed)
    out["NC0_residual_permute"]["core_ordering_unchanged"] = unchanged / max(tot, 1)

    # ---- NC1 foreign core
    rng = np.random.default_rng(seed + 1)
    bysize = {}
    for pid, r in recs.items():
        if judge in r["sat"]:
            bysize.setdefault(r["M"], []).append(pid)
    donor = {}
    for M, lst in bysize.items():
        if len(lst) < 2:
            continue
        sh = list(lst)
        for _ in range(20):                       # derangement by rejection
            rng.shuffle(sh)
            if all(a != b for a, b in zip(lst, sh)):
                break
        donor.update(dict(zip(lst, sh)))
    fake1 = {}
    for pid, r in recs.items():
        if judge not in r["sat"] or pid not in donor:
            continue
        fake1[pid] = dict(r); fake1[pid]["sat"] = dict(r["sat"])
        fake1[pid]["sat"][judge] = (r["sat"][judge][0], recs[donor[pid]]["sat"][judge][1])
    out["NC1_foreign_core"] = _score_fake(recs, tabs, fake1, judge, satnorm,
                                          weighting, target, metric, seed)

    # ---- NC2 response-shuffled core
    rng = np.random.default_rng(seed + 2)
    fake2 = {}
    for pid, r in recs.items():
        if judge not in r["sat"]:
            continue
        Sc = r["sat"][judge][1][:, rng.permutation(4)]
        fake2[pid] = dict(r); fake2[pid]["sat"] = dict(r["sat"])
        fake2[pid]["sat"][judge] = (r["sat"][judge][0], Sc)
    out["NC2_response_shuffled_core"] = _score_fake(recs, tabs, fake2, judge, satnorm,
                                                    weighting, target, metric, seed)
    return out


def placebo(cell, tabs, recs, target, metric, seed, ndraw=100):
    """Two PLACEBOS, both of which must return exactly zero.
    P1  two independent random B-subsets (ndraw pairs per prompt, to make the test
        precise enough to detect a plumbing fault).  Zero by symmetry: a DERIVATION,
        so what it tests is the aggregation / clustering / bootstrap, not the object.
    P2  the exactly-enumerated random-subset expectation minus the mean of ndraw
        sampled subsets.  Zero by construction, and it independently checks that the
        ordering histogram and the sampling path agree."""
    rng = np.random.default_rng(seed)
    a, b, ex, sm = [], [], [], []
    for pid, c in cell.items():
        if target == "intrinsic":
            W = c["W"]; n = W.shape[0]
            if n < 2: continue
            with np.errstate(invalid="ignore"):
                wm = np.nan_to_num(np.nanmean(W, axis=0), nan=0.0)
            t = int(order_code((wm[:, None] * c["Sf"]).sum(0)[None, :])[0])
            v = OO[metric][:, t]
        else:
            T = tabs[pid][target][metric]
            if np.isnan(T[0]).all(): continue
            v = np.nanmean(T, axis=1)
        i1 = rng.integers(0, c["C"], ndraw); i2 = rng.integers(0, c["C"], ndraw)
        a.append(float(np.mean(v[c["codes"][i1]]))); b.append(float(np.mean(v[c["codes"][i2]])))
        avail = np.nonzero(c["hist"])[0]
        ex.append(float(((c["hist"] / c["C"])[avail] * v[avail]).sum()))
        sm.append(float(np.mean(v[c["codes"][rng.integers(0, c["C"], 400)]])))
    mat = np.stack([np.array(a), np.array(b), np.array(ex), np.array(sm)], 1)
    bt = cluster_boot(mat, seed=seed + 13, nboot=800)
    d1 = bt[:, 0] - bt[:, 1]; d2 = bt[:, 2] - bt[:, 3]
    return dict(P1_two_random_subsets=dict(delta=float(np.nanmean(d1)), delta_ci=ci(d1)),
                P2_exact_minus_sampled=dict(delta=float(np.nanmean(d2)), delta_ci=ci(d2)))


def inversion_and_format(recs, cells, tabs, seed):
    """W3 (majority capture) and W4 (format cap)."""
    out = {}
    for (j, sn, wt) in [("main", "raw", "uniform"), ("main", "raw", "signed")]:
        cell = cells[(j, sn, wt)]
        for target in ["personal", "world"]:
            inv = {k: [] for k in ["core", "full_sgn", "full_pers", "rand"]}
            rng = np.random.default_rng(seed)
            for pid, c in cell.items():
                r = recs[pid]
                T = tabs[pid][target]["tau_b"]
                has = ~np.isnan(T[0])
                if not has.any(): continue
                rw = r["ranker_w"]
                for a in np.nonzero(has)[0]:
                    inv["core"].append(T[c["o_core"], a] < 0)
                    inv["full_sgn"].append(T[c["o_full_sgn"], a] < 0)
                    inv["rand"].append(T[c["codes"][rng.integers(0, c["C"])], a] < 0)
                    wi = rw[a]
                    inv["full_pers"].append(T[c["o_pers"][wi], a] < 0 if wi >= 0 else np.nan)
            out[f"{wt}|{target}"] = {k: float(np.nanmean(np.array(v, float))) for k, v in inv.items()}
    # format cap: ceiling under unsigned uniform vs under signed weights
    fmt = {}
    for target in ["intrinsic", "personal", "world"]:
        for metric in ["tau_b"]:
            r_u, _, _ = eval_cell(recs, cells[("main", "raw", "uniform")], target, metric, seed, tabs)
            r_s, _, _ = eval_cell(recs, cells[("main", "raw", "signed")], target, metric, seed, tabs)
            fmt[target] = dict(
                best_ho_unsigned=float(np.nanmean(r_u["best_ho"])),
                best_ho_signed=float(np.nanmean(r_s["best_ho"])),
                rand_unsigned=float(np.nanmean(r_u["rand"])),
                rand_signed=float(np.nanmean(r_s["rand"])),
                full_all_unsigned=float(np.nanmean(r_u["full"])),
                full_all_signed=float(np.nanmean(r_s["full"])),
                full_pos_signed=float(np.nanmean(r_s["full_pos"])),
                full_personal=float(np.nanmean(r_s["full_pers"])),
                core=float(np.nanmean(r_u["core"])))
    out["format_cap"] = fmt
    return out


def a3_positive_control_extrinsic(recs, cells, tabs, seed):
    """Does the FULL rubric beat chance against humans?  If not, the extrinsic arm
    is silence, not an acquittal.  Chance = mean over all 24 orderings."""
    out = {}
    cell = cells[("main", "raw", "signed")]
    for target in ["personal", "world"]:
        for metric in ["tau_b", "top1", "veto"]:
            full, chance, core, pers = [], [], [], []
            for pid, c in cell.items():
                T = tabs[pid][target][metric]
                if np.isnan(T).all(): continue
                v = np.nanmean(T, axis=1)
                full.append(v[c["o_full_sgn"]]); chance.append(float(np.nanmean(v)))
                core.append(v[c["o_core"]])
                rw = recs[pid]["ranker_w"]
                pv = [T[c["o_pers"][rw[a]], a] for a in range(T.shape[1])
                      if rw[a] >= 0 and not np.isnan(T[0, a])]
                pers.append(float(np.nanmean(pv)) if pv else np.nan)
            mat = np.stack([np.array(full), np.array(chance), np.array(core), np.array(pers)], 1)
            bt = cluster_boot(mat, seed=seed, nboot=800)
            out[f"{target}|{metric}"] = dict(
                full=float(np.nanmean(bt[:, 0])), chance=float(np.nanmean(bt[:, 1])),
                core=float(np.nanmean(bt[:, 2])), personal=float(np.nanmean(bt[:, 3])),
                full_minus_chance=float(np.nanmean(bt[:, 0] - bt[:, 1])),
                full_minus_chance_ci=ci(bt[:, 0] - bt[:, 1]),
                personal_minus_chance=float(np.nanmean(bt[:, 3] - bt[:, 1])),
                personal_minus_chance_ci=ci(bt[:, 3] - bt[:, 1]))
    return out


def controls(recs, cells, tabs, t0):
    out = {}
    primary = ("main", "raw", "uniform")
    out["A3_positive_control_extrinsic"] = a3_positive_control_extrinsic(recs, cells, tabs, SEEDS[0])
    print(f"[D] A3 done ({time.time()-t0:.0f}s)")
    out["positive_dose_response"] = {}
    for tg in ["intrinsic", "world"]:
        per = [plant_orderings(cells[primary], tabs, recs, tg, "tau_b", s) for s in SEEDS[:3]]
        agg = {}
        for jd in per[0]:
            agg[jd] = dict(
                eta=float(np.mean([p[jd]["eta"] for p in per])),
                eta_ci=per[0][jd]["eta_ci"],
                eta_seed_spread=float(np.std([p[jd]["eta"] for p in per])),
                delta=float(np.mean([p[jd]["delta"] for p in per])),
                delta_ci=per[0][jd]["delta_ci"], n=per[0][jd]["n"])
        out["positive_dose_response"][tg] = agg
    print(f"[D] positive control done ({time.time()-t0:.0f}s)")
    out["core_path_control"] = {
        tg: core_path_control(recs, cells[primary], tabs, tg, "tau_b", SEEDS[0])
        for tg in ["intrinsic", "world"]}
    print(f"[D] core-path control done ({time.time()-t0:.0f}s)")
    out["negative_controls"] = {
        f"{wt}|{tg}": negative_controls(recs, tabs, "main", "raw", wt, tg, "tau_b", SEEDS[0])
        for wt in ["uniform", "signed"] for tg in ["intrinsic", "world"]}
    print(f"[D] negative control done ({time.time()-t0:.0f}s)")
    out["placebo"] = {tg: placebo(cells[primary], tabs, recs, tg, "tau_b", SEEDS[0])
                      for tg in ["intrinsic", "world"]}
    out["inversion_and_format"] = inversion_and_format(recs, cells, tabs, SEEDS[0])
    print(f"[D] all controls done ({time.time()-t0:.0f}s)")
    return out


if __name__ == "__main__":
    main()
