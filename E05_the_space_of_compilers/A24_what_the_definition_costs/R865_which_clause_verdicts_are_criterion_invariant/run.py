#!/usr/bin/env python3
"""
R865 · which of the definition's clause verdicts survive a change of ADMISSIBILITY CRITERION?

⛔ WHY. R864 established that this project runs TWO admissibility criteria and that they disagree on
the headline comparison: `margin/MDE >= 1.5` FAILS at 0.910 while `outside a 60-draw empirical null`
PASSES at p <= 0.017. The definition's clause table at `DEFINITION.md:582-586` records **one verdict
per clause with no field for criterion-dependence** — so the deliverable's own schema cannot express
what R864 measured. **A table that is under-typed relative to its evidence will silently report the
criterion the author happened to run.**

⛔ THE ARITHMETIC RUNG, RUN FIRST, AND IT SETTLES HALF THE TABLE FOR FREE.
Two of the four clauses are marked **DERIVED**: ① (`0 of 41`, the region is empty by arithmetic) and
③ (`14 of 42`, read off which arms consume prompt labels). **A derived clause has no threshold, no
interval and no multiplicity — so there is nothing for a criterion to act on, and its verdict is
criterion-INVARIANT by construction.** This is a DERIVATION; its assumption is that the table's
DERIVED labels are accurate, which R851 checked against the source. **So at most TWO of four verdicts
can move, and the round's scope is ② and ④′.**

⚠ AND THE TWO CRITERIA DO NOT OBVIOUSLY NEST — which is why this is a measurement and not a second
derivation. `ratio >= 1.5` demands `margin >= 1.5 * 2.802 * SE = 4.203 * SE`, a FLAT per-arm bar.
BH at q=0.05 over C arms demands rank-dependent `q*k/C`: for the top arm that is `0.05/99 = 5.05e-4`
(z ≈ 3.48, LOOSER than 4.203) and for an arm at rank 40 it is `0.0202` (z ≈ 2.32, looser still).
**So BH looks uniformly looser — but BH also requires the CI lower bound above zero AND is computed
on a different tail estimate, so the containment is not algebraic.** Predicting it is not measuring
it, and the last two rounds punished exactly that move.

ESTIMAND        for clauses ② and ④′, the extension count under each criterion, and the SIGNED
                disagreement: |A\\B| and |B\\A| over the same 99 arms and the same bootstrap.
IDENTIFICATION  exact; both criteria are functions of the same per-arm difference vectors, so they
                are computed from ONE bootstrap and differ only in the decision rule. That removes
                sampling noise as an explanation for any disagreement.
SCOPE           population: all scored arms with >=200 prompts, per-arm prompt sets, NOT intersected
                instrument: A2 vs the EVEN annotators (R851's instrument, so counts are comparable)
                baseline:   ② `genericpool16` · ④′ the best criterion-free rule from R435's family
                regime:     home release, judge J
WORLDS          A · A ⊂ B strictly -> the 1.5 floor is the binding constraint everywhere, and every
                    published count is the floor's count, not the clause's
                B · B ⊂ A strictly -> BH multiplicity binds, and the floor has never been the
                    operative rule
                C · NEITHER nests — arms pass each criterion that fail the other. Then the two
                    criteria measure genuinely different things, the clause table needs a
                    criterion column, and no single count is "the" extension of the clause
KILL            CONDITIONAL, all required:
                  ① positive control `oracle_k4` satisfies ② under BOTH criteria
                  ② negative control `random_k4_s0` satisfies ② under NEITHER
                  ③ placebo: comparator vs itself gives margin exactly 0 under both
                  ⭐ ④ the SEED must be able to change the decisions. ⛔ The first draft of this arm
                     asserted "both rules read the same margins" by calling `decide` twice and
                     comparing the margin vector — **which cannot fail**, because `marg` is
                     `nanmean(D, 1)` and never touches the bootstrap. Caught before running; §4's
                     `check that cannot fail`, built a fifth time. **That the two rules share one
                     bootstrap is STRUCTURAL — they are two returns of one call — so it is a
                     DERIVATION, not a control**, and it is labelled as one below. The failable
                     question in its place: does resampling move the two counts, and by how much
                     relative to the disagreement between them? A disagreement smaller than the
                     seed spread is not a disagreement.
⛔⛔ REPAIR AFTER THE FIRST RUN, RECORDED RATHER THAN SMOOTHED AWAY. The first run exited 2 with
                `UNVERIFIED: a control failed for its own reasons` — and the diagnosis is that the
                sentence was true of the ROUND rather than of the clause. `random_k4_s0` satisfies
                ④′, so ④′'s negative control fails. **That is not a malfunction: R850 measured the
                same failure at 7 of 8 class sizes, and R851's docstring says so in as many words.**
                A random 4-criteria set really does beat the best criterion-free rule, which is the
                same fact R856 reported as ④ being dominated by ②.
                ⛔ **The defect was mine: `ok_all` accumulated across BOTH clauses**, so ②'s fully
                clean controls — positive PASS, negative PASS, placebo PASS — were overridden by
                ④′'s expected failure and ②'s readable result was withheld. **§4's `the control
                fails for its own reasons`, in its contaminating form: a control that fails for a
                DIFFERENT object's reasons.** The kill is now PER CLAUSE. ④′ is reported as
                UNVERIFIED with the reason attached; ② is reported.
MULTIPLICITY    BH q=0.05 over all arms for criterion B; criterion A is per-arm by construction and
                that asymmetry is itself part of what is being compared. Both counts reported with
                their non-survivors.
SEEDS           3 bootstrap seeds; the disagreement counts are reported per seed, not averaged.
ARTIFACT        results/criterion_invariance.json
IMPOSSIBLE      construct validated (needs an external gold standard) · cross-release (needs a
                second release) · causally identified (needs an intervention on the mechanism).
"""
import importlib.util, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
import score as SC                                                # noqa: E402
_r435 = next(ROOT.glob("E0*/A*/R435_*"))
_s = importlib.util.spec_from_file_location("r435", _r435 / "run.py")
r435 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r435)

NBOOT, Q, ZEFF, FLOOR = 2000, 0.05, 2.802, 1.5
BLIND, POS, NEG = "genericpool16", "oracle_k4", "random_k4_s0"
L = ["A", "B", "C", "D"]


def bh_mask(p, q=Q):
    C = len(p); o = np.argsort(p); k = -1
    for rank, i in enumerate(o, 1):
        if p[i] <= q * rank / C:
            k = rank
    m = np.zeros(C, bool)
    if k > 0:
        m[o[:k]] = True
    return m


def main() -> int:
    tg, _ = SC.load_targets()
    pids = [p for p in sorted(tg) if len(tg[p]) >= 2]
    H = {p: np.array([SC.cls(np.array(y, float)) for y, _ in tg[p][1::2]]) for p in pids}
    pids = [p for p in pids if len(H[p])]
    n = len(pids)

    def vec(name):
        f = ROOT / "corebench" / "results" / f"sat_{name}.npz"
        if not f.exists():
            return None
        try:
            S = SC.load_sat(f)
        except Exception:
            return None
        return np.array([np.mean(SC.cls(SC.yvec(S[p], sorted({i for i, _ in S[p]}))) == H[p])
                         if p in S else np.nan for p in pids])

    names, A = [], []
    for f in sorted((ROOT / "corebench" / "results").glob("sat_*.npz")):
        v = vec(f.stem[4:])
        if v is not None and np.isfinite(v).sum() >= 200:
            names.append(f.stem[4:]); A.append(v)
    A = np.array(A)
    B2 = vec(BLIND)
    print(f"  prompts {n} · arms {len(names)}")

    # ---- clause ④'s comparator: the best criterion-free rule, on the same population -------------
    txt = {}
    for line in open(ROOT / "data" / "comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        g = {x.get("response_index"): " ".join(
            str(m.get("content") or "") for m in (x.get("messages") or [])
            if m.get("role") == "assistant") for x in (r.get("responses") or [])}
        if len(g) >= 4 and all(g.get(c) for c in L):
            txt[r["prompt_id"]] = {c: g[c] for c in L}
    feats = {p: {c: r435.features(txt[p][c]) for c in L} for p in pids if p in txt}
    R = []
    for _, key, sign in r435.RULES:
        R.append(np.array([np.mean(SC.cls(np.array(
            [(feats[p][c][key] if key != "__pos__" else L.index(c)) for c in L], float)
            * (1.0 if sign > 0 else -1.0)) == H[p]) if p in feats else np.nan for p in pids]))
    R = np.array(R)
    rstar = int(np.nanmean(R, 1).argmax())
    B4 = R[rstar]
    print(f"  ④′ comparator = `{[x[0] for x in r435.RULES][rstar]}` "
          f"({np.nanmean(B4):.6f}) · ② comparator = `{BLIND}` ({np.nanmean(B2):.6f})")

    def decide(D, seed):
        """One bootstrap, TWO decision rules. Returns (mask_A, mask_B, margins, ratios)."""
        bidx = np.random.default_rng(seed).integers(0, n, size=(NBOOT, n))
        M = np.isfinite(D).astype(float)
        Dz = np.nan_to_num(D, nan=0.0)
        bs = (Dz[:, bidx].sum(2) / np.maximum(M[:, bidx].sum(2), 1.0)).T   # (NBOOT, K)
        marg = np.nanmean(D, 1)
        se = bs.std(axis=0, ddof=1)
        ratio = marg / np.maximum(ZEFF * se, 1e-300)
        lo = np.percentile(bs, 2.5, axis=0)
        pv = np.maximum(2 * np.minimum((bs <= 0).mean(0), (bs >= 0).mean(0)), 1.0 / (NBOOT + 1))
        return (ratio >= FLOOR), (bh_mask(pv) & (lo > 0)), marg, ratio

    ip = names.index(POS) if POS in names else None
    ineg = names.index(NEG) if NEG in names else None
    rows = []
    for label, comp in (("②", B2), ("④′", B4)):
        D = A - comp
        print(f"\n  clause {label}   (comparator held fixed; ONE bootstrap, TWO decision rules)")
        per_seed = []
        for sd in (11, 22, 33):
            mA, mB, marg, ratio = decide(D, sd)
            onlyA = int((mA & ~mB).sum()); onlyB = int((mB & ~mA).sum())
            per_seed.append({"seed": sd, "count_A_floor": int(mA.sum()),
                             "count_B_bh": int(mB.sum()), "both": int((mA & mB).sum()),
                             "only_A": onlyA, "only_B": onlyB})
            print(f"    seed {sd}: A(ratio>={FLOOR}) {int(mA.sum()):>3} · B(BH+CI) "
                  f"{int(mB.sum()):>3} · both {int((mA&mB).sum()):>3} · "
                  f"only-A {onlyA:>3} · only-B {onlyB:>3}")
            if sd == 11:
                pos_ok = (bool(mA[ip]) and bool(mB[ip])) if ip is not None else False
                neg_ok = ((not mA[ineg]) and (not mB[ineg])) if ineg is not None else False
                pl = float(np.nanmean(comp - comp))
                print(f"      POSITIVE `{POS}` under BOTH: {pos_ok}  "
                      f"{'PASS' if pos_ok else 'FAIL'}")
                print(f"      NEGATIVE `{NEG}` under NEITHER: {neg_ok}  "
                      f"{'PASS' if neg_ok else 'FAIL'}")
                print(f"      PLACEBO comparator vs itself {pl:+.2e}  "
                      f"{'PASS' if abs(pl) < 1e-12 else 'FAIL'}")
                print("      DERIVATION (not a control): the two rules are two returns of ONE")
                print("      `decide` call, so they read the same bootstrap by construction. The")
                print("      first draft asserted this by comparing margins across two calls --")
                print("      a check that cannot fail, since `marg` never touches the bootstrap.")
                clause_ok = bool(pos_ok and neg_ok and abs(pl) < 1e-12)
                ctl = {"positive": bool(pos_ok), "negative": bool(neg_ok),
                       "placebo": float(pl), "readable": clause_ok}
                if not neg_ok:
                    print(f"      ⚠ {label} NEGATIVE CONTROL FAILS -- and it is EXPECTED: R850")
                    print(f"        measured the same failure at 7 of 8 class sizes, and R856")
                    print(f"        reported {label} as dominated by ②. A random 4-criteria set")
                    print(f"        really does clear this clause. {label} is UNVERIFIED; the")
                    print(f"        other clause is NOT contaminated by it.")
                core_i = names.index("coval_core") if "coval_core" in names else None
                if core_i is not None:
                    print(f"      `coval_core`: margin {marg[core_i]:+.6f} · ratio "
                          f"{ratio[core_i]:+.4f} -> A {bool(mA[core_i])} · B {bool(mB[core_i])}")
        rows.append({"clause": label, "per_seed": per_seed, "controls": ctl})

    readable = [r for r in rows if r["controls"]["readable"]]
    print(f"\n  READABLE CLAUSES: {[r['clause'] for r in readable]} of "
          f"{[r['clause'] for r in rows]}")
    if not readable:
        print("  UNVERIFIED: no clause passed its own controls. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "rows": rows},
                  open(OUT / "criterion_invariance.json", "w"), indent=2)
        return 2

    # ---- KILL ④, the failable form: is the disagreement bigger than the seed spread? ----------
    print()
    for r in readable:
        cA = [x["count_A_floor"] for x in r["per_seed"]]
        cB = [x["count_B_bh"] for x in r["per_seed"]]
        gap = abs(float(np.mean(cA)) - float(np.mean(cB)))
        spread = max(max(cA) - min(cA), max(cB) - min(cB))
        r["seed_spread"] = spread; r["criterion_gap"] = gap
        verdict = "READABLE" if gap > spread else "INSIDE THE SEED SPREAD"
        print(f"  KILL ④ clause {r['clause']}: criterion gap {gap:.1f} vs seed spread "
              f"{spread}  -> {verdict}")
    print("    A disagreement smaller than the seed spread is not a disagreement. This is the")
    print("    arm that replaced the one that could not fail.")

    tot_onlyA = sum(s["only_A"] for r in readable for s in r["per_seed"])
    tot_onlyB = sum(s["only_B"] for r in readable for s in r["per_seed"])
    excl = [r["clause"] for r in rows if not r["controls"]["readable"]]
    if excl:
        print(f"  ⚠ EXCLUDED from the verdict (own controls failed): {excl}. Their counts are in")
        print(f"    the artifact and are NOT folded into the world call.")
    world = "C" if (tot_onlyA > 0 and tot_onlyB > 0) else ("A" if tot_onlyB > 0 else "B")
    print(f"\n  ⭐ across both clauses × 3 seeds: only-A {tot_onlyA} · only-B {tot_onlyB}")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "A ⊂ B — the 1.5 floor is the BINDING constraint, and every published count is the"
             " floor's count rather than the clause's",
        "B": "B ⊂ A — BH multiplicity binds and the floor has never been the operative rule",
        "C": "NEITHER nests — arms pass each criterion that fail the other, so the two measure"
             " different things and no single count is 'the' extension of the clause"}[world])
    print(f"     ⛔ clauses ① and ③ are DERIVED and carry no threshold, so their verdicts are")
    print(f"        criterion-INVARIANT by construction — a derivation, not a measurement, and")
    print(f"        it is why at most 2 of the table's 4 rows could have moved at all.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "n_prompts": n, "n_arms": len(names), "world": world,
               "readable_clauses": [r["clause"] for r in readable],
               "excluded_clauses": excl,
               "exclusion_reason": {"④′": "negative control random_k4_s0 SATISFIES the clause; "
                                          "R850 measured the same at 7 of 8 class sizes and R856 "
                                          "reported ④ as dominated by ②"} if excl else {},
               "clauses": rows, "total_only_A": tot_onlyA, "total_only_B": tot_onlyB,
               "derived_clauses_criterion_invariant": ["①", "③"],
               "floor": FLOOR, "q": Q,
               "comparators": {"②": BLIND, "④′": [x[0] for x in r435.RULES][rstar]}},
              open(OUT / "criterion_invariance.json", "w"), indent=2)
    print(f"\n  artifact: results/criterion_invariance.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
