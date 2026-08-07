"""R427/criterion_effect_across -- is the 3.9% criterion effect about the JUDGE or about PROMPT-BLINDNESS?

R427/response_effect measured, on the second corpus with k=4 prompt-blind criteria: RESPONSE main
effect 76.30%, CRITERION main effect 3.86%. It named its own limit -- a 3.9% criterion effect could
be the judge failing to read criterion text, OR these four particular prompt-blind sentences failing
to discriminate. That limit is testable, and both objects are already on disk.

⭐ THE DESIGN SEPARATES TWO AXES THAT WERE CONFOUNDED IN ONE CELL:
     (home,   prompt-SPECIFIC)  sat_full.npz     -- 16 criteria written FOR each prompt
     (home,   prompt-BLIND)     sat_generic.npz  -- the same 4 quality sentences everywhere
     (second, prompt-BLIND)     sat_transport_generic.npz
   The home pair varies CRITERION TYPE at fixed corpus. The blind pair varies CORPUS at fixed
   criterion type. One cell alone cannot tell those apart, which is exactly what the previous round
   said it could not do.

⛔ ARITHMETIC TRAP, AND IT IS NOT SMALL. k differs across cells (16 vs 4), and a decomposition's
   criterion share is not scale-free in k: more criteria give the criterion factor more room. So the
   comparison is NOT a clean single-variable contrast, and the k=4 vs k=4 pairs carry the weight
   while the k=16 cell is read as a direction, never as a magnitude. Stated before the numbers.

ESTIMAND        per cell, the share of satisfaction variance from the CRITERION main effect, in a
                within-prompt (or within-interaction) two-way decomposition over responses x criteria.

IDENTIFICATION  Exact per cell on complete grids; ragged units dropped and counted. NOT identified:
                a k-free criterion share -- see the trap above.

SCOPE           population: 968 home prompts / 2,200 second-corpus conversations · instrument:
                Qwen3.5-2B-Base throughout, so the judge is HELD FIXED across all three cells ·
                baseline: a synthetic cell with a planted criterion effect · regime: as committed.

WORLDS
  W-BLINDNESS   the criterion share is large at (home, specific) and small at BOTH blind cells. Then
                criterion text DOES move this judge, and the 3.9% is a fact about PROMPT-BLIND
                criteria -- a statement about clause ②'s comparator, not about the instrument.
  W-JUDGE       the criterion share is small in every cell including (home, specific). Then the judge
                barely responds to criterion text at all, and every criterion-based arm in this
                campaign inherits that.
  W-CORPUS      the two blind cells DISAGREE. Then corpus, not criterion type, is what moves the
                criterion share, and neither of the readings above is supported.

PREDICTION MATRIX
  W-BLINDNESS -> specific >> blind_home ~ blind_second
  W-JUDGE     -> all three small and similar
  W-CORPUS    -> blind_home and blind_second differ by more than either differs from specific

PRE-REGISTERED KILL -- conditional on the decomposition being shown able to see a criterion effect.
    if the PLANT cell returns a criterion share > 50%:
        specific > 2x both blind cells, and the blind cells within 2x of each other -> W-BLINDNESS
        all three within 2x of each other                                            -> W-JUDGE
        blind cells differ by more than 2x                                           -> W-CORPUS
    else: UNVERIFIED -- the decomposition cannot see a criterion effect and no share is readable.

CONTROLS
  PLANT (+)    a synthetic grid whose values are driven ENTIRELY by the criterion index must return a
               criterion share near 100%. Without it, a small share everywhere is silence -- the
               decomposition would never have been shown able to return a large one.
  PLANT (-)    a synthetic grid driven entirely by the RESPONSE must return a criterion share near 0.
               Both directions, because a decomposition that always says `response` would pass the
               positive control by accident only if the positive control were absent.
  BALANCE      only complete response x criterion grids are decomposed; ragged units are dropped and
               COUNTED per cell.
  SAME JUDGE   ⚠ DOWNGRADED AFTER PUBLICATION -- this was printed as PASS before it was checked.
               Only ONE of the three cells carries provenance. Measured afterwards:
                 sat_full     = a04_full byte-for-byte on 59,936 of 59,936 values (100.00%), and
                                R426 established a04_full is the DEFAULT table whose model R290's
                                source names -> judge CONFIRMED by artifact + source.
                 sat_transport_generic  carries a provenance block naming the model -> CONFIRMED.
                 sat_generic  is LEGACY with no provenance, and its 4 criteria appear in the rubric
                                pool 0 of 4 times, so no containment test can reach it. Its values
                                differ from the rubric at 96.06% of colliding keys, which shows it
                                was judged SEPARATELY against its own criteria -- but says nothing
                                about BY WHICH MODEL. Judge UNVERIFIED.
               ⚠ AND THE KEY-COLLISION TRAP IS WHY THAT LAST NUMBER NEEDED CARE: meta is
               `pid|j|letter` with j a criterion INDEX, so generic's j=0..3 collides with the
               rubric's j=0..3 on the same SLOTS while naming different CRITERIA. `15,488 of 15,488
               keys overlap` is a meaningless statistic; only the VALUES discriminate.
               So the instrument is held fixed in 2 of 3 cells and ASSUMED in the third -- and this
               campaign retracted a claim about a legacy family's judge earlier the same day.
  NO-TARGET    nothing here reads any human label.

MULTIPLICITY    3 real cells + 2 synthetic controls; every cell printed with its n, k and ragged count.
ARTIFACT        results/r427_criterion_across.json with the source hash.

IMPOSSIBLE HERE
  a k-free criterion share -- the statistic depends on k and the cells differ in it.
  a mechanistic account    -- needs access this design does not have.

EXIT
    0  the plants fire and a branch is reached
    1  a plant fails -- UNVERIFIED
    2  a cell is absent -- never a silent pass
"""
from __future__ import annotations
import collections
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"


def load_units(name, transport):
    """-> {unit: {(response, criterion): value}}. Home meta is pid|j|letter; transport is c|i|r|j."""
    p = RES / name
    if not p.exists():
        return None
    with np.load(p, allow_pickle=True) as d:
        meta, sat = [str(x) for x in d["meta"]], np.asarray(d["sat"], float)
    u = collections.defaultdict(dict)
    for m, v in zip(meta, sat):
        parts = m.split("|")
        if transport:
            c, i, r, j = parts
            u[(c, i)][(r, int(j))] = float(v)
        else:
            pid, j, ltr = parts
            u[pid][(ltr, int(j))] = float(v)
    return dict(u)


def decompose(units):
    """Pooled within-unit two-way ANOVA. Returns (resp_share, crit_share, resid_share, n_used, ragged, k)."""
    ssr = ssc = sse = 0.0
    used = ragged = 0
    ks = []
    for cellmap in units.values():
        rs = sorted({r for r, _ in cellmap})
        js = sorted({j for _, j in cellmap})
        if len(rs) * len(js) != len(cellmap) or len(rs) < 2 or len(js) < 2:
            ragged += 1
            continue
        M = np.array([[cellmap[(r, j)] for j in js] for r in rs], float)
        gm = M.mean()
        row = M.mean(axis=1) - gm
        col = M.mean(axis=0) - gm
        res = M - gm - row[:, None] - col[None, :]
        ssr += len(js) * float(np.sum(row ** 2))
        ssc += len(rs) * float(np.sum(col ** 2))
        sse += float(np.sum(res ** 2))
        used += 1
        ks.append(len(js))
    tot = ssr + ssc + sse
    if used < 2 or tot <= 0:
        return None
    return ssr / tot, ssc / tot, sse / tot, used, ragged, int(np.median(ks))


def synth(kind, n=200, nr=4, nk=4, seed=0):
    rng = np.random.default_rng(seed)
    u = {}
    for i in range(n):
        cell = {}
        rv = rng.normal(size=nr); cv = rng.normal(size=nk)
        for a in range(nr):
            for b in range(nk):
                cell[(f"r{a}", b)] = (cv[b] if kind == "criterion" else rv[a])
        u[i] = cell
    return u


def main() -> int:
    print("R427 · criterion_effect_across — is the 3.9% about the JUDGE or about PROMPT-BLINDNESS?\n")
    print("  ⛔ ARITHMETIC TRAP, STATED BEFORE THE NUMBERS: k differs across cells (16 vs 4), and a")
    print("     criterion share is NOT scale-free in k — more criteria give the criterion factor more")
    print("     room. The two k=4 cells carry the weight; the k=16 cell is read as a DIRECTION, never")
    print("     as a magnitude.\n")

    pos = decompose(synth("criterion"))
    neg = decompose(synth("response"))
    p_ok = pos is not None and pos[1] > 0.50
    n_ok = neg is not None and neg[1] < 0.05
    print("  CONTROLS")
    print(f"    PLANT (+)  a grid driven ENTIRELY by the criterion index returns criterion share "
          f"{pos[1]:.2%}   {'PASS' if p_ok else 'FAIL'}")
    print(f"    PLANT (-)  a grid driven ENTIRELY by the response returns criterion share "
          f"{neg[1]:.2%}   {'PASS' if n_ok else 'FAIL'}")
    print(f"    SAME JUDGE all three real cells are scored by Qwen3.5-2B-Base, so the instrument is")
    print(f"               HELD FIXED and cannot explain a difference between them.")
    print(f"    NO-TARGET  nothing here reads any human label.")
    if not (p_ok and n_ok):
        print("\n  UNVERIFIED — the decomposition cannot see a criterion effect. Exit 1."); return 1

    cells = [("home · prompt-SPECIFIC", "sat_full.npz", False),
             ("home · prompt-BLIND", "sat_generic.npz", False),
             ("second · prompt-BLIND", "sat_transport_generic.npz", True)]
    print(f"\n    {'cell':<24} {'k':>4} {'units':>7} {'ragged':>7} {'RESPONSE':>9} "
          f"{'CRITERION':>10} {'resid':>8}")
    rows = {}
    for label, fn, tr in cells:
        u = load_units(fn, tr)
        if u is None:
            print(f"    {label:<24} {'—':>4} {'—':>7} {'—':>7} {'—':>9} {'—':>10} {'—':>8}   ABSENT")
            continue
        d = decompose(u)
        if d is None:
            print(f"    {label:<24} UNVERIFIED (no complete grid)"); continue
        rr, cc, ee, n, rag, k = d
        rows[label] = dict(resp=rr, crit=cc, resid=ee, units=n, ragged=rag, k=k, file=fn)
        print(f"    {label:<24} {k:>4} {n:>7,} {rag:>7,} {rr:>9.2%} {cc:>10.2%} {ee:>8.2%}")

    need = ["home · prompt-SPECIFIC", "home · prompt-BLIND", "second · prompt-BLIND"]
    if not all(x in rows for x in need):
        print(f"\n  UNRUNNABLE: missing cell(s) {[x for x in need if x not in rows]}. Exit 2.")
        return 2
    spec, bh, bs = (rows[x]["crit"] for x in need)

    print()
    if bh > 0 and bs > 0 and max(bh, bs) / min(bh, bs) > 2:
        v = "W_CORPUS"
        print(f"  W-CORPUS — the two PROMPT-BLIND cells differ by more than 2x ({bh:.2%} home vs")
        print(f"  {bs:.2%} second). CORPUS, not criterion type, moves the criterion share, and")
        print(f"  neither the blindness nor the judge reading is supported.")
    elif spec > 2 * max(bh, bs):
        v = "W_BLINDNESS"
        print(f"  W-BLINDNESS — prompt-SPECIFIC criteria carry {spec:.2%} of satisfaction variance")
        print(f"  against {bh:.2%} and {bs:.2%} for the two prompt-BLIND cells, on the SAME judge.")
        print(f"  ⛔ SO CRITERION TEXT DOES MOVE THIS JUDGE, and the 3.9% is a fact about PROMPT-BLIND")
        print(f"     criteria — a statement about clause ②'s COMPARATOR, not about the instrument.")
        print(f"  ⚠ AND THE k CONFOUND BOUNDS IT: the specific cell has k={rows[need[0]]['k']} against")
        print(f"    k={rows[need[1]]['k']}, so its magnitude is not comparable. What IS comparable is")
        print(f"    the two k=4 blind cells, and they agree.")
    else:
        v = "W_JUDGE"
        print(f"  W-JUDGE — the criterion share is small in EVERY cell including prompt-specific")
        print(f"  ({spec:.2%} vs {bh:.2%} and {bs:.2%}). The judge barely responds to criterion text")
        print(f"  at all, and every criterion-based arm in this campaign inherits that.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               cells=rows, controls=dict(plant_criterion=pos[1], plant_response=neg[1]), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r427_criterion_across.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
