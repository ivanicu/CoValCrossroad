"""Local-to-global obstruction in a rubric, computed exactly -- and named carefully.

THE OBJECT. For one prompt, let R be the candidate responses and C the criteria. Fix a threshold
theta and set

    U_c = { r in R : satisfaction(c, r) >= theta }        the responses that satisfy criterion c
    A_r = { c in C : satisfaction(c, r) >= theta }        the criteria satisfied by response r

The nerve of the cover {U_c} is the simplicial complex X on C whose faces are the subsets of
criteria that some single response satisfies simultaneously. A GLOBAL SECTION is a response
satisfying every criterion at once; an obstruction is local agreement that does not assemble.

WHY THIS IS COMPUTABLE AND NOT ESTIMATED. X is the down-closure of the four sets A_r, so it is a
union of four simplices. Simplices are contractible and an intersection of simplices is a simplex,
so the nerve lemma applies TO THE FOUR MAXIMAL FACES and

    X  is homotopy equivalent to  N({A_r}),  a subcomplex of the 3-simplex.

That is at most 15 faces. The Betti numbers are ranks of two small boundary matrices over F2, so
they are exact integers and not a statistic. Note the nerve lemma does NOT apply to the cover
{U_c} itself -- the U_c are subsets of a four-point discrete space and their intersections are
disconnected -- which is precisely why H1 can be non-zero at all.

WHAT H1 != 0 MEANS IN WORDS, and it is worth stating because the algebra is otherwise a ritual:

    three responses pairwise share a satisfied criterion, and no criterion is satisfied by all
    three.

Local compatibility everywhere, global compatibility nowhere. That is the shape of a genuine
obstruction rather than a metaphor for one.

WHAT THIS IS NOT ALLOWED TO BE CALLED. Following the memo's rule: the output is the BEST-FOUND
JOINT RESIDUAL UNDER A NAMED REPAIR CLASS, and a Betti number of an explicitly constructed complex
at an explicitly named threshold. It becomes a statement about the rubric rather than about the
measurement only if it survives:

    - a sweep over theta                      (else it is a thresholding artefact)
    - a change of executor                    (else it is one judge's opinion)
    - a marginal-preserving null              (else a hollow triangle is just combinatorics)

The null is the one that matters most. With four responses and a dozen criteria, pairwise overlap
without triple overlap happens by chance at a rate that has to be measured before any observed rate
means anything.

REPAIR CLASSES, named:
    G0  choose one of the released candidates            exhaustive, certifiable, tiny
    G1  choose any response in the release               tests whether the obstruction is local
    G2  generate a response targeting a subset           the richer class; not run here
A residual under G0 that vanishes under G1 was never an obstruction, only a shortage of candidates.
"""
from __future__ import annotations

import itertools
import math

import numpy as np


def _rank_f2(m: np.ndarray) -> int:
    """Gaussian elimination over F2. Exact; no tolerance, no condition number."""
    a = (m.copy() % 2).astype(np.uint8)
    rows, cols = a.shape
    r = 0
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if a[i, c]:
                piv = i
                break
        if piv is None:
            continue
        a[[r, piv]] = a[[piv, r]]
        for i in range(rows):
            if i != r and a[i, c]:
                a[i] ^= a[r]
        r += 1
        if r == rows:
            break
    return r


def nerve_faces(sets: list[set]) -> list[tuple[int, ...]]:
    """Faces of the nerve of `sets`: S is a face iff the intersection over S is non-empty."""
    n = len(sets)
    faces = []
    for k in range(1, n + 1):
        for S in itertools.combinations(range(n), k):
            inter = set.intersection(*(sets[i] for i in S))
            if inter:
                faces.append(S)
    return faces


def betti(faces: list[tuple[int, ...]]) -> tuple[int, int]:
    """(b0, b1) over F2 of the complex given by its faces (closed under subsets by construction)."""
    by_dim: dict[int, list[tuple[int, ...]]] = {}
    for f in faces:
        by_dim.setdefault(len(f) - 1, []).append(f)
    v = by_dim.get(0, [])
    e = by_dim.get(1, [])
    t = by_dim.get(2, [])
    nv, ne, nt = len(v), len(e), len(t)
    if nv == 0:
        return 0, 0
    vi = {f: i for i, f in enumerate(v)}
    ei = {f: i for i, f in enumerate(e)}

    d1 = np.zeros((nv, ne), dtype=np.uint8)
    for f, j in ei.items():
        for x in f:
            d1[vi[(x,)], j] = 1
    r1 = _rank_f2(d1) if ne else 0

    d2 = np.zeros((ne, nt), dtype=np.uint8)
    for j, f in enumerate(t):                  # enumerate yields (index, face), not (face, index)
        for sub in itertools.combinations(f, 2):
            d2[ei[sub], j] = 1
    r2 = _rank_f2(d2) if nt else 0

    b0 = nv - r1
    b1 = ne - r1 - r2
    return b0, b1


def analyse(M: np.ndarray) -> dict:
    """M is boolean [n_criteria, n_responses]: does response r satisfy criterion c?

    Returns the full end-to-end profile for one prompt at one threshold.
    """
    n_c, n_r = M.shape
    A = [set(np.nonzero(M[:, r])[0].tolist()) for r in range(n_r)]
    faces = nerve_faces(A) if any(A) else []
    b0, b1 = betti(faces)

    # k-wise satisfiability profile over CRITERIA: what fraction of k-subsets of criteria have a
    # common satisfier? Computed by inclusion-exclusion over the four response sets, exactly.
    prof = {}
    kmax = min(n_c, 6)
    for k in range(1, kmax + 1):
        tot = math.comb(n_c, k)
        if tot == 0:
            continue
        cnt = 0
        for m in range(1, n_r + 1):
            for S in itertools.combinations(range(n_r), m):
                inter = set.intersection(*(A[i] for i in S)) if S else set()
                cnt += ((-1) ** (m + 1)) * math.comb(len(inter), k)
        prof[k] = cnt / tot

    best = max((len(a) for a in A), default=0)
    # the memo's phrasing: pairwise repairable but not jointly
    pair_ok = prof.get(2, 0.0)
    return {
        "n_criteria": n_c, "n_responses": n_r,
        "max_simultaneously_satisfied": best,
        "residual_G0": n_c - best,
        "residual_G0_frac": (n_c - best) / n_c if n_c else float("nan"),
        "global_section_exists": best == n_c,
        "b0": b0, "b1": b1,
        "H1_nonzero": b1 > 0,
        "kwise_profile": {str(k): round(v, 4) for k, v in prof.items()},
        "pairwise_satisfiable_frac": round(pair_ok, 4),
        "criteria_with_no_satisfier": int(sum(1 for c in range(n_c) if not M[c].any())),
    }


def null_M(M: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Marginal-preserving null: keep each criterion's number of satisfying responses and each
    response's number of satisfied criteria as close as possible, destroy only which-goes-with-which.

    Uses curveball / trade swaps, which preserve BOTH margins exactly -- a null that preserves only
    the row margin would let the column totals drift and would then be answering a different
    question than the observed matrix poses.
    """
    A = M.copy()
    n_r, n_c = A.shape
    for _ in range(20 * n_r * n_c):
        i, j = rng.integers(0, n_r, 2)
        if i == j:
            continue
        a = np.nonzero(A[i] & ~A[j])[0]
        b = np.nonzero(A[j] & ~A[i])[0]
        if len(a) == 0 or len(b) == 0:
            continue
        k = min(len(a), len(b))
        pa = rng.permutation(a)[:k]
        pb = rng.permutation(b)[:k]
        A[i, pa] = False
        A[i, pb] = True
        A[j, pb] = False
        A[j, pa] = True
    return A


# ------------------------------------------------------------------ controls

def control_compatible(n_c: int = 8, n_r: int = 4) -> np.ndarray:
    """One response satisfies everything. Residual must be 0 and H1 must be 0."""
    M = np.zeros((n_c, n_r), dtype=bool)
    M[:, 0] = True
    M[: n_c // 2, 1] = True
    return M


def control_incompatible() -> np.ndarray:
    """A criterion and its negation. No response can satisfy both, so the residual is certified
    >= 1 by construction and any method reporting 0 here is broken."""
    M = np.zeros((2, 4), dtype=bool)
    M[0, :2] = True
    M[1, 2:] = True
    return M


def control_hollow_triangle() -> np.ndarray:
    """The smallest genuine H1: three responses pairwise share a criterion, none shared by all
    three. b1 must be exactly 1, or the homology code is wrong."""
    M = np.zeros((3, 4), dtype=bool)
    M[0, [0, 1]] = True
    M[1, [1, 2]] = True
    M[2, [0, 2]] = True
    return M


def control_filled_triangle() -> np.ndarray:
    """Three responses pairwise sharing a criterion AND one criterion shared by all three.

    b1 must be 0. This control exists because the hollow-triangle control alone never exercises the
    2-face boundary matrix -- the hollow complex has no triangles -- so a transposition bug in that
    code path passed three green controls and only surfaced on real data. A control suite that
    never builds the object it is meant to test is not a suite.
    """
    M = np.zeros((4, 4), dtype=bool)
    M[0, [0, 1]] = True
    M[1, [1, 2]] = True
    M[2, [0, 2]] = True
    M[3, [0, 1, 2]] = True
    return M
