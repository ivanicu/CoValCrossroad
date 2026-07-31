"""End-to-end normative information preservation, measured as dimensions -- the loss IS the object.

The chain is N -> A -> G -> C -> R -> J -> S -> D -> Y. Everything downstream of the rubric acts on
one prompt's four candidate responses, so every stage from the rubric onward induces a set of
FUNCTIONS ON FOUR POINTS. That space is 4-dimensional, 3 after centering, and the ceiling is not a
modelling choice -- it is arithmetic:

    however many criteria people wrote and however many numbers they attached, at most THREE
    independent normative distinctions can possibly reach the decision when the decision is a
    choice among four responses.

That is a DERIVATION and is labelled as one. It is reported first because it frames every number
below: the elicitation collects on the order of n_criteria x n_annotators values per prompt, and
the channel to behaviour is three-dimensional. Loss is therefore guaranteed; the question this
round asks is WHICH three survive, and whether they are the ones people cared about.

MEASUREMENT. Each stage is represented as a matrix whose rows are vectors over the four responses:

    N       one row per annotator: their OWN rubric applied to the responses
            (sum over criteria of their rating times that criterion's satisfaction)
    R_full  one row per criterion in the full rubric: its satisfaction across responses
    R_core  one row per criterion in the compiled core rubric
    Y       one row per annotator: their actual ranking of the responses

Between consecutive stages the surviving dimensions are counted by PRINCIPAL ANGLES between the
row spaces. A dimension counts as preserved when its principal cosine exceeds a threshold, and the
threshold is swept rather than chosen. Then

    preserved = #angles above cutoff        lost = dim(upstream) - preserved
    invented  = dim(downstream) - preserved

`invented` is the one that is easy to forget and it is where a compilation step can add structure
nobody asked for.

THE NULL IS NOT OPTIONAL. Two random subspaces of dimension 2 and 3 inside a 4-dimensional space
intersect substantially by chance. Every preserved-dimension count is therefore reported beside the
count obtained after permuting the response labels within each row, which destroys the alignment
between stages while preserving every marginal. A preserved count that does not exceed its null is
not preservation; it is dimension arithmetic.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
from collections import defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
LETTERS = "ABCD"


def load_sat(path: pathlib.Path) -> dict[str, np.ndarray]:
    """meta is 'conversation|criterion_index|response_letter' -> [n_criteria, 4] per conversation."""
    z = np.load(path, allow_pickle=True)
    sat, meta = z["sat"], z["meta"]
    cells: dict[str, dict[tuple[int, int], float]] = defaultdict(dict)
    for s, m in zip(sat, meta):
        cid, ci, rl = str(m).split("|")
        if rl not in LETTERS:
            continue
        cells[cid][(int(ci), LETTERS.index(rl))] = float(s)
    out = {}
    for cid, d in cells.items():
        n = max(k[0] for k in d) + 1
        M = np.full((n, 4), np.nan)
        for (i, j), v in d.items():
            M[i, j] = v
        out[cid] = M
    return out


def load_ratings() -> dict[str, tuple[np.ndarray, list[str]]]:
    """[n_criteria, n_annotators] signed weights, NaN where that person did not rate it.

    KEYED BY prompt_id, NOT by conversation.id. The release uses two disjoint id namespaces --
    conversation_rubrics has its own ids and comparisons/annotators have another, with zero overlap
    -- so the rubric file has to be joined to the prompt file by message text. That join already
    exists in covalx.judge and is reused rather than rewritten, because a second implementation of
    a join is a second chance to align the wrong rows and no chance to notice.
    """
    from covalx.judge import load_join
    out = {}
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    for pid, _prompt, r in joined:
            cid = pid
            ann = sorted({s["annotator_id"] for it in r["coval_full"] for s in it["scores"]})
            idx = {a: i for i, a in enumerate(ann)}
            M = np.full((len(r["coval_full"]), len(ann)), np.nan)
            for i, it in enumerate(r["coval_full"]):
                for s in it["scores"]:
                    M[i, idx[s["annotator_id"]]] = float(s["score"])
            out[cid] = (M, ann)
    return out


RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}


def load_rankings(prefer=("world", "personal")) -> dict[str, dict[str, np.ndarray]]:
    """Human rankings per (conversation, annotator) as a score vector over the four responses.

    THE BLOCK CHOICE WAS SILENT AND IS NOT NEUTRAL. `world` is populated for all 18,678
    assessments; `personal` for only 5,006. Preferring world therefore ALWAYS took world and never
    once fell through -- so every number in this round is about what people said the model should do
    IN GENERAL, not about what they personally preferred, and nothing in the output said so.

    Those are different questions. `prefer=("personal",)` runs the whole chain on the smaller
    personal-preference population instead, which is the robustness check the silent default hid.
    """
    out: dict[str, dict[str, np.ndarray]] = defaultdict(dict)
    with (ROOT / "data" / "annotators.jsonl").open() as fh:
        for line in fh:
            rec = json.loads(line)
            aid = rec["annotator_id"]
            for a in rec.get("assessments", []):
                blocks = a.get("ranking_blocks") or {}
                for key in prefer:
                    for b in blocks.get(key, []) or []:
                        txt = b.get("ranking")
                        if not txt:
                            continue
                        v = _parse_ranking(txt)
                        if v is not None:
                            out[a["conversation_id"]][aid] = v
                            break
                    if aid in out[a["conversation_id"]]:
                        break
    return out


def _parse_ranking(txt: str) -> np.ndarray | None:
    """'A>B>C=D' -> a score vector. Higher is better."""
    v = np.full(4, np.nan)
    groups = [g.strip() for g in txt.replace(" ", "").split(">") if g.strip()]
    if not groups:
        return None
    for gi, g in enumerate(groups):
        for letter in g.split("="):
            if letter in RANK_MAP:
                v[RANK_MAP[letter]] = -gi
    return v if not np.isnan(v).all() else None


def _center_rows(M: np.ndarray) -> np.ndarray:
    M = np.asarray(M, float)
    keep = ~np.isnan(M).any(axis=1)
    M = M[keep]
    if M.size == 0:
        return np.zeros((0, 4))
    M = M - M.mean(axis=1, keepdims=True)          # centering: only contrasts can act on a choice
    nz = np.linalg.norm(M, axis=1) > 1e-9
    return M[nz]


def _basis(M: np.ndarray, tol: float = 1e-8) -> np.ndarray:
    if M.shape[0] == 0:
        return np.zeros((4, 0))
    u, s, _ = np.linalg.svd(M.T, full_matrices=False)
    return u[:, s > tol * max(1.0, s[0])]


def preserved_dims(A: np.ndarray, B: np.ndarray, cutoff: float) -> tuple[int, int, int, list]:
    """Principal angles between the row spaces of A and B."""
    Qa, Qb = _basis(_center_rows(A)), _basis(_center_rows(B))
    da, db = Qa.shape[1], Qb.shape[1]
    if da == 0 or db == 0:
        return 0, da, db, []
    s = np.linalg.svd(Qa.T @ Qb, compute_uv=False)
    keep = int(np.sum(s >= cutoff))
    return keep, da, db, [round(float(x), 4) for x in s]


def permuted(M: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Permute response labels INDEPENDENTLY within each row: destroys cross-stage alignment,
    preserves every row's own distribution of values exactly."""
    A = np.array(M, float, copy=True)
    for i in range(A.shape[0]):
        A[i] = A[i][rng.permutation(A.shape[1])]
    return A


def direction(M: np.ndarray) -> np.ndarray | None:
    """A stage's PREFERRED DIRECTION over the four responses: the centered aggregate, unit norm.

    This replaces the subspace measurement below, which is retained as a documented control
    because it is an instructive failure: in a 3-dimensional ambient space every stage with three
    or more rows spans EVERYTHING, so principal angles between stages are identically zero and the
    'preserved dimensions' count is 3.00 at every arrow, every cutoff -- and 3.00 in the NULL too.
    A check whose null equals its observation has no resolution. It would have read as perfect
    end-to-end preservation, and only running the null exposed that it could not have read anything
    else.
    """
    A = _center_rows(M)
    if A.shape[0] == 0:
        return None
    v = A.mean(axis=0)
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else None


def align(a: np.ndarray | None, b: np.ndarray | None) -> float:
    return float(np.dot(a, b)) if a is not None and b is not None else float("nan")


def top_set(v: np.ndarray, tol: float = 1e-9) -> set:
    return set(np.nonzero(v >= v.max() - tol)[0].tolist())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cutoffs", type=float, nargs="+", default=[0.5, 0.7, 0.9])
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    ap.add_argument("--block", choices=["world", "personal"], default="world",
                    help="which ranking block the chain's terminal stage Y is read from; the "
                         "default was previously silent and always resolved to world")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    base = ROOT / "01_object_and_rebuild" / "r04_rebuild_satisfaction" / "results"
    sat_full = load_sat(base / "a04_full.npz")
    sat_core = load_sat(base / "a04_core.npz")
    ratings = load_ratings()
    rankings = load_rankings((args.block,))

    cids = [c for c in sat_full if c in sat_core and c in ratings and c in rankings]
    print(f"conversations usable end to end: {len(cids)}")

    # ---- the ceiling, stated as a derivation
    raw_dims, ceiling = [], []
    for cid in cids:
        M, _ann = ratings[cid]
        raw_dims.append(int(np.linalg.matrix_rank(np.nan_to_num(M))))
        ceiling.append(3)
    print(f"DERIVATION  mean rank of what people expressed: {np.mean(raw_dims):.1f} dimensions; "
          f"the channel to a 4-way choice carries at most 3. This is arithmetic, not a finding.")

    arrows = ("N->R_full", "R_full->R_core", "R_core->Y", "N->Y")
    res = {a: {str(c): {"obs": [], "null": [], "up": [], "down": []}
               for c in args.cutoffs} for a in arrows}

    for cid in cids:
        Mr, ann = ratings[cid]
        SF, SC = sat_full[cid], sat_core[cid]
        n = min(Mr.shape[0], SF.shape[0])
        if n < 2:
            continue
        # N: each annotator's OWN rubric applied to the responses
        W = np.nan_to_num(Mr[:n])
        N = (W.T @ np.nan_to_num(SF[:n]))                       # [annotators, 4]
        Y = np.array([rankings[cid][a] for a in ann if a in rankings[cid]], float)
        if Y.shape[0] == 0:
            continue
        stages = {"N": N, "R_full": SF, "R_core": SC, "Y": Y}

        for arrow in arrows:
            a, b = arrow.split("->")
            for c in args.cutoffs:
                k, da, db, _s = preserved_dims(stages[a], stages[b], c)
                res[arrow][str(c)]["obs"].append(k)
                res[arrow][str(c)]["up"].append(da)
                res[arrow][str(c)]["down"].append(db)
                nulls = []
                for sd in args.seeds:
                    rng = np.random.default_rng(hash((cid, arrow, sd)) % (2**31))
                    kn, _, _, _ = preserved_dims(stages[a], permuted(stages[b], rng), c)
                    nulls.append(kn)
                res[arrow][str(c)]["null"].append(float(np.mean(nulls)))

    summary = {}
    print(f"\n{'arrow':16s} {'cut':>4s} {'dim up':>7s} {'dim down':>9s} "
          f"{'preserved':>10s} {'null':>7s} {'excess':>7s} {'lost':>6s} {'invented':>9s}")
    for arrow in arrows:
        summary[arrow] = {}
        for c in args.cutoffs:
            d = res[arrow][str(c)]
            if not d["obs"]:
                continue
            obs, null = float(np.mean(d["obs"])), float(np.mean(d["null"]))
            up, down = float(np.mean(d["up"])), float(np.mean(d["down"]))
            se = float(np.std(d["obs"], ddof=1) / math.sqrt(len(d["obs"])))
            summary[arrow][str(c)] = {
                "n_conversations": len(d["obs"]), "dim_up": round(up, 3),
                "dim_down": round(down, 3), "preserved": round(obs, 3),
                "preserved_ci95": [round(obs - 1.96 * se, 3), round(obs + 1.96 * se, 3)],
                "null": round(null, 3), "excess_over_null": round(obs - null, 3),
                "lost": round(up - obs, 3), "invented": round(down - obs, 3)}
            print(f"{arrow:16s} {c:4.1f} {up:7.2f} {down:9.2f} {obs:10.2f} {null:7.2f} "
                  f"{obs - null:+7.2f} {up - obs:6.2f} {down - obs:9.2f}")

    # ------------------------------------------------------------------ the non-degenerate object
    # Each annotator carries a DIRECTION over the four responses. The chain either transmits it or
    # does not, and the obstruction is the shape the verified nerve code was written for: people
    # pairwise share a best response while no response is best for all of them.
    from covalx.chain.cohomology import analyse
    rows, nerve = [], []
    skipped_Y = 0
    for cid in cids:
        Mr, ann = ratings[cid]
        SF, SC = sat_full[cid], sat_core[cid]
        n = min(Mr.shape[0], SF.shape[0])
        if n < 2:
            continue
        W = np.nan_to_num(Mr[:n])
        indiv = _center_rows(W.T @ np.nan_to_num(SF[:n]))          # one row per annotator
        d_N, d_F = direction(W.T @ np.nan_to_num(SF[:n])), direction(SF)
        d_C = direction(SC)
        Yr = np.array([rankings[cid][a] for a in ann if a in rankings[cid]], float)
        if Yr.ndim != 2 or Yr.shape[0] == 0:
            # On the personal block many prompts have NO ranking at all -- it covers 5,006 of
            # 18,678 assessments -- so the chain's terminal stage is undefined there. Counted and
            # reported rather than dropped, because a silently smaller n is a different study.
            skipped_Y += 1
            continue
        d_Y = direction(Yr)
        rows.append({"N->R_full": align(d_N, d_F), "R_full->R_core": align(d_F, d_C),
                     "R_core->Y": align(d_C, d_Y), "N->Y": align(d_N, d_Y),
                     "served": float(np.mean([align(direction(v[None, :]), d_C) > 0
                                              for v in indiv])) if indiv.shape[0] else np.nan})
        # nerve of the individuals' top-choice sets: local agreement without a global choice
        Yc = _center_rows(Yr)
        if Yc.shape[0] >= 3:
            # rows = annotators, columns = responses. NOT transposed: `analyse` enumerates the
            # nerve over its COLUMN sets, so passing the transpose would enumerate 2^n_annotators
            # subsets instead of 2^4. The orientation is load-bearing, not cosmetic.
            M = np.zeros((Yc.shape[0], 4), dtype=bool)
            for i, v in enumerate(Yc):
                for j in top_set(v):
                    M[i, j] = True
            obs = analyse(M)
            # NULL. "no response is top for everyone" is true at ~100% under ANY null once there
            # are a dozen people and four options, so the binary cannot fail and is not evidence.
            # The residual is. Each person keeps the SIZE of their top-set and loses only WHICH
            # responses are in it, so the null preserves ties, decisiveness and panel size exactly.
            nulls = []
            for sd in args.seeds:
                rng = np.random.default_rng(hash((cid, "nerve", sd)) % (2**31))
                Mn = np.zeros_like(M)
                for i in range(M.shape[0]):
                    Mn[i, rng.permutation(4)[: int(M[i].sum())]] = True
                nulls.append(analyse(Mn))
            obs["residual_null"] = float(np.mean([x["residual_G0"] for x in nulls]))
            obs["H1_null"] = float(np.mean([x["H1_nonzero"] for x in nulls]))
            obs["no_global_null"] = float(np.mean([not x["global_section_exists"] for x in nulls]))
            nerve.append(obs)

    def col(k):
        v = np.array([r[k] for r in rows], float)
        v = v[~np.isnan(v)]
        se = float(np.std(v, ddof=1) / math.sqrt(len(v)))
        return round(float(v.mean()), 4), [round(float(v.mean()) - 1.96 * se, 4),
                                           round(float(v.mean()) + 1.96 * se, 4)], len(v)

    print(f"\nterminal stage Y read from the {args.block!r} block; prompts with no Y at all: "
          f"{skipped_Y} of {len(cids)}")
    print("\nDIRECTION TRANSMITTED ALONG THE CHAIN (cosine, 1 = fully transmitted, 0 = orthogonal)")
    align_summary = {}
    for k in ("N->R_full", "R_full->R_core", "R_core->Y", "N->Y"):
        m, ci, n = col(k)
        align_summary[k] = {"cosine": m, "ci95": ci, "n_eff": n}
        print(f"  {k:16s} {m:+.4f}  CI {ci}  n={n}")
    m, ci, n = col("served")
    align_summary["share_of_people_aligned_with_core"] = {"share": m, "ci95": ci, "n_eff": n}
    print(f"  {'people served':16s} {m:.1%}  CI {ci}  n={n}")

    h1 = sum(1 for r in nerve if r["H1_nonzero"])
    nogl = sum(1 for r in nerve if not r["global_section_exists"])
    print(f"\nOBSTRUCTION over individuals' top choices  (n={len(nerve)} prompts)")
    print(f"  no response is top for everyone          : {nogl}/{len(nerve)} "
          f"({nogl / max(1, len(nerve)):.1%})")
    print(f"  H1 non-zero (pairwise agreement, no triple): {h1}/{len(nerve)} "
          f"({h1 / max(1, len(nerve)):.1%})")
    if nerve:
        res_o = float(np.mean([r["residual_G0"] for r in nerve]))
        res_n = float(np.mean([r["residual_null"] for r in nerve]))
        pan = float(np.mean([r["n_criteria"] for r in nerve]))
        h1n = float(np.mean([r["H1_null"] for r in nerve]))
        ngn = float(np.mean([r["no_global_null"] for r in nerve]))
        print(f"  no global section, NULL                  : {ngn:.1%}   "
              f"<- the binary cannot discriminate; it is ~certain either way")
        print(f"  H1 non-zero, NULL                        : {h1n:.1%}")
        print(f"  residual under G0: observed {res_o:.2f} vs null {res_n:.2f} of {pan:.1f} people"
              f"  ({res_o / pan:.1%} vs {res_n / pan:.1%} unserved)")
        print(f"  agreement recovered relative to chance   : "
              f"{(res_n - res_o) / res_n:.1%} of the null residual is removed by real agreement")

    (OUT / "information_loss.json").write_text(json.dumps(
        {"summary": summary, "alignment": align_summary,
         "obstruction": {"n_prompts": len(nerve), "no_global_section": nogl, "H1_nonzero": h1,
                         "mean_residual_G0": round(float(np.mean(
                             [r["residual_G0"] for r in nerve])), 3) if nerve else None},
         "degenerate_control_note": (
             "the subspace table above reads 3.00 everywhere INCLUDING the null: in a "
             "3-dimensional ambient space every stage spans everything, so principal angles "
             "cannot discriminate. Kept as a documented instance of a check that cannot fail."),
         "n_conversations": len(cids),
         "mean_rank_expressed": round(float(np.mean(raw_dims)), 3),
         "channel_ceiling": 3,
         "derivation_note": ("the 3-dimensional ceiling is arithmetic: contrasts among four "
                             "responses span three dimensions. It is not evidence."),
         "cutoffs": args.cutoffs, "seeds": args.seeds}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
