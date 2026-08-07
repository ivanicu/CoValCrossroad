"""R408 -- the LITERAL reading of clause ②: `better than`, with no significance term, at the maximum.

R407 answered the universal reading at the per-k maximum blind set and found no label-free arm
admitted -- then named the reason that answer is scoped: R360's `admits` is `e > 0 AND |e| >= ZEFF*se`,
SIGNIFICANTLY better, while the definition's sentence says `scores better than`. The coded test is
stricter, in the direction that flatters, and the literal one had never been run.

⛔ THIS ROUND RUNS IT, AND THE RE-IMPLEMENTATION IS THE RISK, SO IT IS CONTROLLED BEFORE IT IS USED.
   R360's `build`, `ref_at` and `admits` are nested inside its `main()` and cannot be imported. The
   scoring layer CAN be -- `score.load_sat/load_targets/yvec/cls` -- and is, rather than copied,
   because a re-implemented classifier tests the copy. What must be re-implemented is the subset
   enumeration and the two decision rules, and the POSITIVE CONTROL is exact: my STRICT variant must
   reproduce R360's committed p=100 cell ARM FOR ARM. If it does not, my re-implementation diverges
   and no literal result from it is admissible.

⛔ ARITHMETIC TRAP, AND IT CUTS ONE WAY ONLY. `literal ⊇ strict` is FORCED -- dropping a conjunct
   cannot shrink an admitted set -- so finding the literal set at least as large is not evidence and
   is asserted as a sanity check rather than reported as a result. What is NOT forced is whether any
   LABEL-FREE arm enters, which is the entire question.

⚠ AND THE LITERAL READING IS THE SENTENCE'S READING AND ALSO THE ONE WITH NO ERROR CONTROL. `e > 0`
  admits an arm whose advantage is indistinguishable from noise. That is not a reason to prefer the
  strict test -- the definition does not contain it -- but it IS a fact about the sentence, and if the
  literal reading admits arms the strict one rejects, the honest report is that the definition as
  written has no error control, not that a core was found.

ESTIMAND        at p = 100 (the per-k MAXIMUM prompt-blind set), the admitted set under
                  (a) STRICT  : e > 0 and |e| >= ZEFF * se        -- R360's coded rule
                  (b) LITERAL : e > 0                             -- the definition's sentence
                split each time into label-free and label-reading, and reported as two sets, never as
                one "the answer".

IDENTIFICATION  Exact given the cached per-arm satisfaction arrays. NOT identified: whether `e > 0`
                on this sample would survive a second release -- one release, and an unguarded
                positive mean is exactly the quantity that would not.

SCOPE           population: the 9 arms clause ② admits · instrument: cached sat_*.npz scored by
                Qwen3.5-2B-Base, loaded through R360's own scoring module · baseline: the highest
                prompt-blind subset of each arm's own size · regime: p = 100 only.

WORLDS
  W-LITERAL-ALSO-EMPTY  the literal test admits no label-free arm either. Then clause ②, at the
                        universal reference, is unsatisfiable without label access under BOTH
                        readings, and R407's conclusion survives the objection it raised against
                        itself.
  W-LITERAL-ADMITS      some label-free arm has e > 0 against the maximum. Then R407's emptiness was
                        partly an artifact of a significance term the definition does not contain,
                        and the arms are named -- together with whether their advantage clears its
                        own noise, because the sentence does not require that and a reader will.

PREDICTION MATRIX
  W-LITERAL-ALSO-EMPTY -> (literal admitted - label readers) == empty
  W-LITERAL-ADMITS     -> non-empty, arms named with their e and se

PRE-REGISTERED KILL -- conditional on the reproduction, never on the literal set alone.
    if strict_variant_reproduces_R360_committed_p100_cell_exactly:
        if (literal - labels) == set() -> W-LITERAL-ALSO-EMPTY
        else -> W-LITERAL-ADMITS, arms named with e and se
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED. A diverging re-implementation makes both
          numbers mine rather than the object's.

CONTROLS
  REPRODUCE (+)   the STRICT variant must return R360's committed p=100 admitted set exactly. This is
                  a control whose answer was produced by a DIFFERENT round for a DIFFERENT purpose.
  SUPERSET        literal must be a superset of strict. Forced by construction, so it is a sanity
                  assertion on the code and NOT reported as a finding -- if it fails, a sign is wrong.
  SCORING LAYER   `load_sat/load_targets/yvec/cls` are IMPORTED from the same module R360 uses, never
                  copied. Only the enumeration and the two rules are re-implemented.
  K RESTRICTION   only the k values the 9 tested arms need are built, which is a COST saving and is
                  declared: ref_at is per-k, so restricting k cannot change any tested arm's verdict.

MULTIPLICITY    2 rules x 9 arms = 18 cells, all printed with e and se.
SEEDS           none -- deterministic enumeration.
ARTIFACT        results/r408_literal_test.json with the source hash.

IMPOSSIBLE HERE
  whether `e > 0` replicates on another release -- one release, and an unguarded positive mean is
                                    precisely the quantity that would not survive. Named.
  a second judge                  -- at 0.8B nothing is admitted at any safe reference (R358/R359).
  deciding WHICH rule the definition means -- an act of definition. Both are reported.

EXIT
    0  the reproduction holds and both sets are reported
    1  the strict variant does not reproduce R360 -- UNVERIFIED
    2  an input is missing -- never a silent pass
"""
from __future__ import annotations
import hashlib
import itertools
import json
import math
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
R360 = HERE.parent / "R360_which_clause_is_load_bearing" / "results" / "r360_clause_ledger.json"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
USES_PROMPT_LABELS = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}


def main() -> int:
    pool_f = RES / "sat_genericpool16.npz"
    if not (pool_f.exists() and R360.exists()):
        print("  UNRUNNABLE: pool or R360 artifact absent. Exit 2, never 0."); return 2
    committed = set(json.loads(R360.read_text())["sweep"][-1]["admitted"])
    tg, _ = load_targets()
    POOL = load_sat(pool_f)
    pids = sorted(set(POOL) & {q for q in tg if len(tg[q]) >= 2})
    H = {q: [cls(np.array(t[0], float)) for t in tg[q]] for q in pids}
    npool = len({i for i, _ in POOL[pids[0]]})
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    print(f"R408 · the LITERAL reading at the universal reference   "
          f"{len(pids)} prompts · pool {npool}\n")
    print("  ⛔ THE RE-IMPLEMENTATION IS THE RISK, SO IT IS CONTROLLED BEFORE IT IS USED. The scoring")
    print("     layer is IMPORTED from the module R360 uses; only the enumeration and the two")
    print("     decision rules are re-implemented, and the STRICT one must reproduce R360's")
    print("     committed p=100 cell arm for arm before any literal number is admissible.\n")

    def a2_vec(sat, ps):
        out = []
        for q in ps:
            idx = sorted({i for i, _ in sat[q]})
            yv = cls(yvec(sat[q], idx))
            out.append(np.mean([[yv[c] == h[c] for c in range(6)] for h in H[q]]))
        return np.array(out, float)

    all_arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                      if not p.stem.startswith("sat08") and p.stem != "sat_genericpool16"
                      and not p.stem.endswith(("_08b", "_08bR")))
    ARM, KOF = {}, {}
    for a in all_arms:
        S = load_sat(RES / f"sat_{a}.npz")
        ps = [q for q in pids if q in S]
        if len(ps) < 100:
            continue
        ARM[a] = (ps, a2_vec(S, ps))
        KOF[a] = min(max(int(np.median([len({i for i, _ in S[q]}) for q in ps])), 1), npool)

    tested = sorted(a for a in ARM if a in set(json.loads(R360.read_text())["clause2_admits"])
                    or a in committed)
    ks = sorted({KOF[a] for a in tested})
    print(f"  {len(tested)} arms tested · k values built {ks}  (K RESTRICTION declared: ref_at is")
    print(f"  per-k, so restricting k cannot change any tested arm's verdict — it is a cost saving)")

    def build(k):
        sb = np.array(list(itertools.combinations(range(npool), k)))
        SAT = np.stack([np.array([[POOL[q][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                        for q in pids])
        out = np.empty((len(sb), len(pids)))
        for n in range(len(pids)):
            Y = SAT[n][sb].sum(axis=1)
            C_ = np.sign(Y[:, ii] - Y[:, jj])
            out[:, n] = (C_[:, None, :] == np.array(H[pids[n]], float)[None, :, :]).mean(axis=(1, 2))
        return out

    CLS = {k: build(k) for k in ks}

    def ref_max(k):
        B = CLS[k]
        return B[int(np.argsort(B.mean(axis=1))[-1])]

    def stats(a):
        ps, v = ARM[a]
        pos = [n for n, q in enumerate(pids) if q in set(ps)]
        d = v - ref_max(KOF[a])[pos]
        e = float(d.mean())
        se = float(d.std(ddof=1) / math.sqrt(len(d)))
        return e, se

    print(f"\n  BOTH RULES AT p = 100, EVERY CELL PRINTED")
    print(f"    {'arm':<20}{'k':>3}{'e':>12}{'se':>10}{'strict':>9}{'literal':>9}   labels?")
    strict, literal, rows = set(), set(), {}
    for a in tested:
        e, se = stats(a)
        s_ok = bool(e > 0 and abs(e) >= ZEFF * se)
        l_ok = bool(e > 0)
        if s_ok:
            strict.add(a)
        if l_ok:
            literal.add(a)
        rows[a] = dict(k=KOF[a], e=e, se=se, strict=s_ok, literal=l_ok,
                       reads_labels=a in USES_PROMPT_LABELS)
        print(f"    {a:<20}{KOF[a]:>3}{e:>+12.6f}{se:>10.6f}{str(s_ok):>9}{str(l_ok):>9}   "
              f"{'yes' if a in USES_PROMPT_LABELS else ''}")

    # ---- CONTROLS ---------------------------------------------------------------------------------
    repro = strict == committed
    superset = strict <= literal
    print(f"\n  CONTROLS")
    print(f"    REPRODUCE (+)  my STRICT variant vs R360's committed p=100 cell: {repro}")
    print(f"                   mine      {sorted(strict)}")
    print(f"                   committed {sorted(committed)}   {'PASS' if repro else 'FAIL'}")
    print(f"    SUPERSET       literal ⊇ strict: {superset}   "
          f"{'PASS' if superset else 'FAIL — a sign is wrong'}")
    print(f"                   forced by construction, so a sanity assertion and NOT a finding")
    if not repro:
        print(f"\n  UNVERIFIED — the re-implementation diverges from R360, so both numbers would be")
        print(f"  mine rather than the object's. Exit 1, and the divergence is the thing to fix.")
        return 1

    free_lit = sorted(literal - USES_PROMPT_LABELS)
    free_str = sorted(strict - USES_PROMPT_LABELS)
    print(f"\n  LABEL-FREE ADMITTED")
    print(f"    under STRICT : {free_str}   (n={len(free_str)})")
    print(f"    under LITERAL: {free_lit}   (n={len(free_lit)})")

    print()
    if not free_lit:
        v = "W_LITERAL_ALSO_EMPTY"
        print(f"  W-LITERAL-ALSO-EMPTY — even with no significance term, NO label-free arm scores")
        print(f"  better than the maximum prompt-blind set of its own size. Clause ② at the universal")
        print(f"  reference is unsatisfiable without label access under BOTH readings, so R407's")
        print(f"  conclusion survives the objection R407 itself raised against it.")
    else:
        v = "W_LITERAL_ADMITS"
        print(f"  W-LITERAL-ADMITS — {free_lit} scores better than the maximum blind set, but only")
        print(f"  under the sentence's own unguarded `e > 0`. R407's emptiness was therefore partly")
        print(f"  an artifact of a significance term the definition does not contain.")
        print(f"  ⚠ AND THE HONEST REPORT IS THAT THE DEFINITION AS WRITTEN HAS NO ERROR CONTROL —")
        print(f"    not that a core was found. Each arm's e and se are printed above; every one of")
        print(f"    these sits inside its own noise by the strict column, which is what `literal`")
        print(f"    means here.")

    print(f"\n  ⚠ ONE RELEASE. An unguarded positive mean is precisely the quantity that would not")
    print(f"    survive a second one, and this round cannot speak to that.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               n_prompts=len(pids), pool=npool, tested=tested, ks=ks, rows=rows,
               strict=sorted(strict), literal=sorted(literal), committed=sorted(committed),
               label_free_strict=free_str, label_free_literal=free_lit,
               controls=dict(reproduces_r360=repro, superset=superset), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r408_literal_test.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
