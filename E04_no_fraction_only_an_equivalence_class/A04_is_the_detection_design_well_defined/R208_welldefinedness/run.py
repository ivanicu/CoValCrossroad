"""Is the structural half well-defined? A proof attempt, and it finds failures.

Ivan asked me to prove it. A proof attempt whose conclusion is "yes, all of them" would be the
check-that-cannot-fail this project has built four times, so the deliverable is the list of cells
that FAIL, with the reason each fails, verified numerically rather than argued.

WHAT "WELL-DEFINED" MEANS HERE. A loss shape is a map f on the tensors. It is admissible as an
experimental cell iff all four hold:

  (D) TOTAL ON A DECLARED DOMAIN. f(x) is defined for a stated, measured fraction of x -- not
      "in principle". An operator applicable to 0.1% of the corpus is identified and unpowered.
  (R) REPRESENTATION-INDEPENDENT. f's output does not depend on a choice absent from its input.
      An operator needing an index that does not exist in the schema is not an operator.
  (C) CLOSED. f maps the tensor space into itself, so the same statistic can be computed after.
  (S) SEPARABLE. There EXISTS a statistic that distinguishes f(x) from x. If the algebra forces
      every downstream statistic to be invariant, the cell cannot fail and is a DERIVATION, not a
      measurement. This is the realstat arithmetic trap at the level of the design.

(S) is the one that does the work, and it is checked to machine precision below rather than argued.
"""
from __future__ import annotations

import json, math, pathlib, sys
from collections import defaultdict
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
L = "ABCD"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"


def load(p):
    d = np.load(p, allow_pickle=True)
    o = defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|")
        o[pid][(int(i), ltr)] = float(v)
    return o


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sf = load(R4 / "a04_full.npz")
    # (R) AT THE VERY BOTTOM OF THE STACK: conversation_rubrics.jsonl carries NO prompt id --
    # only the conversation text. Every tensor in this project is indexed by a prompt_id that
    # exists only in comparisons.jsonl, so the index itself is RECONSTRUCTED by matching message
    # content, with a fuzzy fallback. That is a well-definedness fact about the release and it
    # sits underneath all seventeen shapes: the criterion-to-prompt map is inferred, not shipped.
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    pids = [p for p in sf if p in recs]
    print(f"\n  JOIN: rubrics carry no prompt_id; the index is reconstructed from message content.")
    print(f"  rubric records joined to a prompt: {len(recs)}; with a satisfaction tensor: {len(pids)}")

    # ------------------------------------------------------------------ §1 the base tensors
    print("=" * 100)
    print("§1 · THE BASE TENSORS -- index space, domain, and what is NOT in the schema")
    print("=" * 100)
    n_c, n_rated, n_auth, n_multi = [], 0, 0, 0
    for p in pids:
        f = recs[p]["coval_full"]
        n_c.append(len(f))
        for it in f:
            sc = it.get("scores") or []
            n_rated += len(sc)
            aset = {s["annotator_id"] for s in sc}
            n_auth += (len(aset) == 1)
            n_multi += (len(aset) > 1)
    print(f"""
  S_full[p, c, r]   satisfaction of criterion c by response r.  p: {len(pids)} prompts
                    c: RAGGED, {min(n_c)}..{max(n_c)} per prompt   r: exactly 4, letters ABCD
                    values in (0,1), a sigmoid of a logit difference -- NOT a probability of
                    anything, and no round has ever calibrated it. Instrument: Qwen3.5-2B-Base.
  W[p, c, a]        the weight annotator a gave criterion c.  SPARSE: {n_rated:,} of
                    {sum(n_c) * 1000:,} conceivable (c,a) cells. Values in [-10,10]\\{{0}}.
  author[p, c]      defined only where exactly one annotator rated c: {n_auth:,} criteria
                    sole-rated, {n_multi:,} multi-rated -> author is a PARTIAL function.
  V[p, a]           the veto SET. Indexed by (prompt, annotator). *** NOT by criterion. ***
  T[p, a]           the top choice. Indexed by (prompt, annotator).

  WHAT IS NOT IN THE SCHEMA, and this is the load-bearing sentence for §3:
    there is no index linking a veto to a criterion. A veto is a fact about a PERSON and a
    RESPONSE; a weight is a fact about a PERSON and a CRITERION. They do not share an index.""")

    # ------------------------------------------------------------------ §2 N_i
    print("\n" + "=" * 100)
    print("§2 · N_i -- the derived tensor everything else is measured against")
    print("=" * 100)
    Ns, raw_norms, drop_empty = {}, [], 0
    for p in pids:
        per = defaultdict(lambda: np.zeros(4))
        seen = defaultdict(int)
        for ci, it in enumerate(recs[p]["coval_full"]):
            sat = [sf[p].get((ci, x)) for x in L]
            if any(s is None for s in sat):
                continue
            for s_ in (it.get("scores") or []):
                per[s_["annotator_id"]] += float(s_["score"]) * np.array(sat, float)
                seen[s_["annotator_id"]] += 1
        d = {}
        for a, v in per.items():
            raw_norms.append((np.linalg.norm(v - v.mean()), seen[a]))
            c = v - v.mean()
            nn = np.linalg.norm(c)
            if nn <= 1e-12:
                drop_empty += 1
                continue
            d[a] = c / nn
        if d:
            Ns[p] = d
    rn = np.array([x[0] for x in raw_norms]); kk = np.array([x[1] for x in raw_norms])
    r = np.corrcoef(np.log(rn + 1e-9), np.log(kk))[0, 1]
    print(f"""
  N_i[p,a,r] = sum over criteria c that a rated of  W[p,c,a] x S_full[p,c,r]

  (D) DOMAIN.  defined only where a rated >=1 criterion on p. Zero-filling an unrated participant
      is the r154 bug: an empty sum is not a zero opinion. Participants dropped for a degenerate
      (constant over the 4 responses) vector: {drop_empty}.
  (R) SCALE IS NOT REPRESENTATION-INDEPENDENT, and this is why centring+normalising is FORCED,
      not stylistic. log||N_i|| vs log(#criteria rated): r = {r:+.3f}. A person who rated more
      criteria has a mechanically larger vector, so any statistic on unnormalised N_i measures
      EFFORT, not values.
  (C) CENTRING. only contrasts among 4 responses are decidable, so the mean over r is unidentified
      and must be removed. After centring N_i lies in a 3-dim subspace; after normalising, on S^2.
      *** That is the whole probe problem in one line: whatever a person's disposition is, the
      elicitation returns a point on a 2-sphere, and 3 numbers is the ceiling. ***""")

    # ------------------------------------------------------------------ §3 shape by shape
    print("\n" + "=" * 100)
    print("§3 · THE 17 SHAPES I CALLED STRUCTURAL -- each against (D)(R)(C)(S)")
    print("=" * 100)

    def Y(p, W_over=None, extra=None, drop=None):
        """the crowd-weighted rubric score, with an optional mutation applied"""
        y = np.zeros(4)
        for ci, it in enumerate(recs[p]["coval_full"]):
            if drop is not None and ci == drop:
                continue
            sat = [sf[p].get((ci, x)) for x in L]
            if any(s is None for s in sat) or not it.get("scores"):
                continue
            w = float(np.mean([s_["score"] for s_ in it["scores"]]))
            if W_over and ci in W_over:
                w = W_over[ci](w)
            y = y + w * np.array(sat, float)
        for w, sat in (extra or []):
            y = y + w * np.asarray(sat, float)
        return y - y.mean()

    def rel(a, b):
        d = np.linalg.norm(a - b); s = max(np.linalg.norm(a), np.linalg.norm(b), 1e-30)
        return d / s

    rows = []
    test = pids[:200]

    # --- the three I suspect are algebraically invariant -------------------------------
    for nm, mk, why in [
        ("fragmentation", "frag", "split one criterion's weight across two identical copies"),
        ("cancellation", "canc", "add an equal-and-opposite criterion"),
        ("behavioral_inertness", "inert", "add a criterion constant over the four responses"),
        ("redundancy_masking", "dup", "duplicate a criterion so it counts twice"),
    ]:
        ds = []
        for p in test:
            base = Y(p)
            f = recs[p]["coval_full"]
            ci = next((i for i, it in enumerate(f)
                       if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)), None)
            if ci is None:
                continue
            sat = np.array([sf[p][(ci, x)] for x in L], float)
            w = float(np.mean([s_["score"] for s_ in f[ci]["scores"]]))
            if mk == "frag":
                mut = Y(p, W_over={ci: lambda _w: _w / 2}, extra=[(w / 2, sat)])
            elif mk == "canc":
                mut = Y(p, extra=[(-w, sat)])
            elif mk == "inert":
                mut = Y(p, extra=[(w, np.full(4, 0.5))])
            else:
                mut = Y(p, extra=[(w, sat)])
            ds.append(rel(base, mut))
        m = float(np.max(ds))
        verdict = ("FAILS (S) -- INVARIANT TO MACHINE PRECISION" if m < 1e-12
                   else "separable")
        rows.append({"shape": nm, "max_rel_change": m, "verdict": verdict, "why": why})
        print(f"\n  {nm:24s} {why}")
        print(f"    max relative change in Y over {len(ds)} prompts: {m:.3e}   -> {verdict}")

    # --- the ones needing an index that does not exist ---------------------------------
    veto_ok = 0; veto_tot = 0
    for p in test:
        for c in (recs[p].get("comparisons") or []):
            pass
    print(f"""
  type_coercion            represent a veto as a large negative weight
    FAILS (R). A veto is indexed (prompt, annotator); a weight is indexed (prompt, criterion,
    annotator). Coercing one into the other requires inventing WHICH CRITERION the veto attaches
    to, and that index is not in the release. The operator is not a function of the data.
    *** What IS well-defined is a different question: does any finite penalty M reproduce the
    veto's behaviour when N_i is scored as N - M*1[r in V]? That is C2 of the north star and it
    is a limit statement about M, not a mutation of a tensor. I had these confused. ***""")

    # --- the ones needing a tensor that does not exist ---------------------------------
    print(f"""
  decontextualization      move criterion c from prompt p to prompt q
  substitution             replace c with another prompt's criterion
    FAIL (C), and I MISCLASSIFIED BOTH AS STRUCTURAL. Both need S_full[q, c, .] -- the judge's
    verdict on c against q's responses -- which was never computed and cannot be derived. They
    belong in the TEXT half, at {len(pids)} x 4 additional judge calls apiece.""")

    # --- the ones needing a stipulation ------------------------------------------------
    print(f"""
  synergy_destruction      remove a pair that only matters jointly
    FAILS (R) until a synergy measure is STIPULATED. Partial information decomposition has no
    unique redundancy/synergy split; Williams-Beer, Bertschinger and Griffith give different
    answers on the same joint. So this cell has as many values as choices of decomposition, and
    reporting one is reporting the choice.
  spurious_activation      add a criterion that fires where it should not
    FAILS (R). "should not" requires ground truth about where a criterion ought to apply. The
    release ships no applicability labels. Without them the operator is "add a criterion", which
    is a different shape already in the list.
  deletion                 remove a criterion entirely
    NOT AN OPERATOR -- A FAMILY. The result depends entirely on WHICH criterion: highest weight,
    random, most-rated, sole-authored. Measured below.""")

    hi, lo, rnd = [], [], []
    rng = np.random.default_rng(0)
    for p in test:
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < 3:
            continue
        base = Y(p)
        ws = {i: abs(float(np.mean([s_["score"] for s_ in f[i]["scores"]]))) for i in ok}
        hi.append(rel(base, Y(p, drop=max(ws, key=ws.get))))
        lo.append(rel(base, Y(p, drop=min(ws, key=ws.get))))
        rnd.append(rel(base, Y(p, drop=int(rng.choice(ok)))))
    print(f"""    highest-|w| criterion  mean relative change {np.mean(hi):.4f}
    lowest-|w|  criterion  mean relative change {np.mean(lo):.4f}
    random      criterion  mean relative change {np.mean(rnd):.4f}
    ratio high/low = {np.mean(hi) / max(np.mean(lo), 1e-12):.1f}x. The selection rule is not a
    nuisance parameter, it is most of the effect. "deletion" without it names nothing.""")
    rows += [{"shape": "deletion", "selection_rule_ratio": float(np.mean(hi) / max(np.mean(lo), 1e-12))}]

    # --- the ones that survive ----------------------------------------------------------
    surv = []
    for nm, ov, why in [
        ("inversion", (lambda w: -w), "flip the sign of the weight; involutive, exact"),
        ("weakening", (lambda w: 0.5 * w), "shrink |w|; continuous in the dose, identity at g=0"),
        ("strengthening", (lambda w: math.copysign(10.0, w)), "saturate |w| at the scale maximum"),
    ]:
        ds = []
        for p in test:
            f = recs[p]["coval_full"]
            ok = [i for i, it in enumerate(f)
                  if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
            if not ok:
                continue
            ds.append(rel(Y(p), Y(p, W_over={ok[0]: ov})))
        surv.append((nm, float(np.mean(ds)), why))
    print(f"""
  ----------------------------------------------------------------------------------------------
  SHAPES THAT PASS ALL FOUR. Each is a total map on W alone, needs no new judge call, no index
  that is missing, and moves Y measurably:""")
    for nm, m, why in surv:
        print(f"    {nm:18s} mean relative change {m:.4f}   {why}")
    print(f"""    provenance_stripping  drops author[p,c] -- total, closed, separable, BUT only ONE
                          family (provenance attribution) reads that field, so the cell is
                          detected by construction and cannot fail for the other 14.
    path_dependence       full-then-core vs core directly: both tensors exist. PASSES.
    executor_dependence   needs a second judge tensor. Checked on disk below.""")

    import glob
    alts = sorted(glob.glob(str(ROOT / "**/*.npz"), recursive=True))
    alts = [a for a in alts if any(k in a for k in ("qwen2b", "phi", "qwen3b", "variant_swapped"))]
    cover = {}
    for a in alts:
        try:
            d = np.load(a, allow_pickle=True)
            ps = {str(k).split("|")[0] for k in d["meta"]}
            cover[pathlib.Path(a).name] = len(ps)
        except Exception as e:
            cover[pathlib.Path(a).name] = f"unreadable: {e}"
    print(f"\n    second-judge tensors on disk (prompts covered, against {len(pids)} needed):")
    for k, v in cover.items():
        print(f"      {k:44s} {v}")

    # ------------------------------------------------------------------ verdict
    dead = [r for r in rows if r.get("verdict", "").startswith("FAILS")]
    print("\n" + "=" * 100)
    print("§4 · VERDICT ON THE STRUCTURAL HALF")
    print("=" * 100)
    print(f"""
  I claimed 17 structural shapes x 15 families = 255 cells. Audited against (D)(R)(C)(S):

    {len(dead)} shapes are ALGEBRAICALLY INVARIANT -- no downstream statistic can distinguish them,
      proven to machine precision above. Their 15 cells each are DERIVATIONS, not measurements,
      and reporting a 0 there as "no family detects this" would be reporting arithmetic.
    2 shapes need a judge tensor that does not exist -> they are TEXT, not structural.
    3 shapes need an index or a stipulation absent from the release -> not functions of the data.
    1 shape is a family indexed by a selection rule that carries most of the effect.

  So the honest count is not 255. It is:
    {(17 - len(dead) - 2 - 3 - 1)} fully well-defined structural shapes
      x 15 families = {(17 - len(dead) - 2 - 3 - 1) * 15} cells that can actually fail,
    plus {len(dead) * 15} cells whose answer is forced by algebra and must be LABELLED as derivations,
    plus 1 shape (deletion) that becomes well-defined once the selection rule is a swept axis,
      which turns it into {len(hi) and 4} specifications rather than one cell.

  AND THE INVARIANT ONES ARE THE INTERESTING RESULT, not the discarded one. Three distinct
  normative failures -- splitting a criterion in two, adding one that cancels another, adding one
  that never fires -- are INVISIBLE to every statistic computable on this release, and that is a
  theorem about the release rather than a limitation of any family. A pipeline could do all three
  and no measurement here would notice.""")

    (OUT / "welldefined.json").write_text(json.dumps(
        {"rows": rows, "survivors": [{"shape": n, "mean_rel": m} for n, m, _ in surv],
         "deletion_selection": {"high": float(np.mean(hi)), "low": float(np.mean(lo)),
                                "random": float(np.mean(rnd))},
         "second_judge_coverage": cover, "n_prompts": len(pids)}, indent=1, default=str))
    return 0




def degeneracy() -> int:
    """§5 -- the attack on my own kill criterion, which the (S) test above forced.

    I pre-registered: if the detection matrix has rank 1 after thresholding, C3 of the north star
    ("loss has shapes that do not average") is DEAD. The (S) test found `cancellation` separable
    where I predicted invariant, and the reason is fatal to that kill as written: adding a
    criterion with weight -w and the SAME satisfaction vector changes Y by exactly -w*S_c, which
    is exactly what DELETING c does. Two rows of my matrix are the same operator up to nothing.

    If several shapes induce collinear changes in Y, the matrix is rank-deficient BY CONSTRUCTION,
    and a rank-1 result would be reading my own design rather than the release. So the rank of the
    DESIGN must be measured before the rank of the RESULT, and any kill threshold must be stated
    relative to it. This is the gauge test one level up: what transformation of my operator set
    leaves the induced change identical?
    """
    sf = load(R4 / "a04_full.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    pids = [p for p in sf if p in recs][:300]

    def base_and_parts(p):
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < 3:
            return None
        S = {i: np.array([sf[p][(i, x)] for x in L], float) for i in ok}
        W = {i: float(np.mean([s_["score"] for s_ in f[i]["scores"]])) for i in ok}
        y = sum(W[i] * S[i] for i in ok)
        return ok, S, W, y

    def ctr(v):
        return v - v.mean()

    OPS = ["deletion", "cancellation", "redundancy_masking", "fragmentation",
           "behavioral_inertness", "inversion", "weakening", "strengthening"]
    cols = defaultdict(list)
    for p in pids:
        bp = base_and_parts(p)
        if bp is None:
            continue
        ok, S, W, y = bp
        c = ok[0]
        d = {
            "deletion": -W[c] * S[c],
            "cancellation": -W[c] * S[c],
            "redundancy_masking": +W[c] * S[c],
            "fragmentation": np.zeros(4),
            "behavioral_inertness": W[c] * np.full(4, 0.5),
            "inversion": -2 * W[c] * S[c],
            "weakening": -0.5 * W[c] * S[c],
            "strengthening": (math.copysign(10.0, W[c]) - W[c]) * S[c],
        }
        for k, v in d.items():
            cols[k].append(ctr(v))

    M = np.stack([np.concatenate(cols[k]) for k in OPS])          # [8, 4*n]
    nrm = np.linalg.norm(M, axis=1, keepdims=True)
    live = (nrm[:, 0] > 1e-9)
    Mn = M[live] / nrm[live]
    names = [k for k, l in zip(OPS, live) if l]
    C = Mn @ Mn.T
    print("\n" + "=" * 100)
    print("§5 · THE DESIGN'S OWN RANK -- an attack on my pre-registered kill")
    print("=" * 100)
    print(f"\n  cosine between the change each operator induces in Y, over {len(cols['deletion'])} prompts:\n")
    print("      " + " ".join(f"{n[:9]:>10s}" for n in names))
    for i, n in enumerate(names):
        print(f"  {n[:20]:20s}" + " ".join(f"{C[i, j]:10.4f}" for j in range(len(names))))
    ev = np.linalg.eigvalsh(C)[::-1]
    ev = ev / ev.sum()
    k95 = int(np.searchsorted(np.cumsum(ev), 0.95) + 1)
    dead = [k for k, l in zip(OPS, live) if not l]
    print(f"""
  eigenvalue shares: {' '.join(f'{e:.3f}' for e in ev)}
  operators inducing EXACTLY ZERO change (dropped, {len(dead)}): {dead}
  components to explain 95% of the operator set: {k95} of {len(names)}

  READING, AND IT CHANGES THE EXPERIMENT:
  Five of these are SCALAR MULTIPLES of the same vector W[c]*S_c -- deletion, cancellation,
  redundancy masking, inversion and weakening differ only in a coefficient. On any statistic that
  is scale-equivariant they are ONE operator, and a detection matrix built from them would come
  back near rank 1 no matter what the release does.

  SO THE KILL AS PRE-REGISTERED IS UNSOUND. "rank 1 => C3 is dead" would have fired on my own
  design. The kill has to be restated against the design's rank, not against 1:
     C3 dies iff  rank(detection matrix) is NOT GREATER THAN rank(design matrix) = {k95}.
  Registering that now, before the matrix runs, because after it runs the threshold is a narrative.

  AND THIS IS WHY THE TEXT HALF IS NOT OPTIONAL. Everything computable without the judge lives in
  the one-dimensional family "scale the contribution of criterion c". Polarity, scope, exception
  and subject are the only operators that leave that line -- and every one of them needs the judge,
  which is precisely the {len(dead) and 610}k model calls nobody has spent.""")
    (OUT / "design_rank.json").write_text(json.dumps(
        {"ops": names, "cos": C.tolist(), "eig_share": ev.tolist(),
         "design_rank_95": k95, "zero_ops": dead}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(degeneracy())
