#!/usr/bin/env python3
"""
R912 · the k=4 cell CANNOT be balanced — and that is structural, not a shortage.

⛔ WHY. R911 separated the two selection objectives in its primary k-matched specification
(+0.250) and in the pooled one (+0.133), but **not at matched k=4** (−0.024). R911's closing line
proposed growing the variance group there and asserted the generator could not, *"because the rule
is deterministic"*. **That assertion was wrong in one direction and right in another, and reading
`select_core.py` settles both.**

⭐ **WRONG:** `--select-npz` exists precisely to *"re-run the rule under the new judge"*. A rule that
CONSUMES satisfaction can be re-run on a DIFFERENT satisfaction while still emitting values from the
same judge, giving a genuinely new arm at 0 judge calls. **Two such arms were built** —
`topvar_k4_sel08`, `topwvar_k4_sel08`: selection driven by the 0.8B satisfaction, **values emitted
from the 2B judge**, so the scoring judge is unchanged and R895's judge-mixing defect is not
reintroduced.

⛔⛔ **RIGHT, AND SHARPER THAN THE ORIGINAL CLAIM:** `select_core.py:72` states that
`(random_k, topw_k, topabs_k, full)` are **satisfaction-BLIND**. So `--select-npz` changes nothing
for them:
  · `topw_k4` — the ONLY signed-weight rule — **cannot produce a new arm at k=4 at all**
  · `topabs_k4` — also blind, so it cannot either
  · only `topvar_k` and `topwvar_k` can grow
**Therefore the k=4 cell can be grown on ONE SIDE ONLY, by structural necessity rather than by
choice.** That is the honest headline of this round, and it must lead rather than trail: **growing
one side is exactly the defect R911 fixed everywhere else, and at k=4 it is irreducible.**

⚠ **AND THE NEW ARMS ARE NOT FORCED TO FAIL.** A variance rule driven by a different judge's
satisfaction selects a different criterion set; nothing makes its margin negative. If either is
ADMITTED the variance group's clean zero breaks and the whole R909–R911 line weakens — which is
what makes this worth running rather than assuming.

ESTIMAND        the k=4 contrast with the variance group at 10 arms instead of 8, and an explicit
                statement of which side CAN grow there.
IDENTIFICATION  exact. ⚠ Not causal, not an admission probability.
SCOPE           population: k=4 arms only — `topw_k4` (signed, cannot grow) vs
                            {topabs,topvar,topwvar}_k4 plus the two `_sel08` arms
                instrument: per-prompt A2 margin vs genericpool16, bootstrap NBOOT 8000
                baseline:   equal share across objectives
                regime:     home release, judge 2B for VALUES throughout, seed 912
WORLDS          A · the new arms are REJECTED and k=4 becomes disjoint -> every specification now
                    separates, but the k=4 one does so by one-sided growth that cannot be balanced
                B · the new arms are REJECTED and k=4 still overlaps -> the cell stays the odd one
                C · either new arm is ADMITTED -> the variance group's zero breaks and R909–R911's
                    line weakens. **Reachable, and the reason to run this**
KILL            CONDITIONAL:
                  ⭐ ① WIRING: reproduce R881's `lo` on the four k=4 reference arms.
                  ⭐ ② THE NEW ARMS MUST DIFFER from their originals — if `topvar_k4_sel08`
                     duplicates `topvar_k4`'s selections, `--select-npz` did nothing and the growth
                     is fictitious. Checked on the committed criterion sets, not assumed.
                  ⭐ ③ SAME SCORING JUDGE: the new arms' values come from the 2B npz. Asserted by
                     construction and stated, because R895's defect was exactly this.
                  ④ the satisfaction-blind rule list is READ from select_core.py, not recalled.
MULTIPLICITY    one cell, one contrast; both new arms printed whether admitted or not.
ARTIFACT        results/k4_one_sided.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · admission probability. ⚠ AND newly named and STRUCTURAL: **a balanced
                k=4 comparison**. It would require a second signed-weight rule that consumes
                satisfaction, and the generator has none.
"""
import json, pathlib, re, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
GEN = ROOT / "corebench" / "select_core.py"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
BLIND, NBOOT, SEED = "genericpool16", 8000, 912
REF = {"topw_k4": 0.014402, "topabs_k4": -0.063677,
       "topvar_k4": -0.066342, "topwvar_k4": -0.048203}
OLD_OTHER = ["topabs_k4", "topvar_k4", "topwvar_k4",
             "topabs_k2", "topabs_k8", "topvar_k2", "topvar_k8", "topwvar_k2", "topwvar_k8"]
NEWARMS = ["topvar_k4_sel08", "topwvar_k4_sel08"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    ph = k / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main() -> int:
    m = re.search(r"\(([^)]*)\) are satisfaction-blind", GEN.read_text())
    blind = [x.strip() for x in m.group(1).split(",")] if m else None
    print(f"  ④ satisfaction-BLIND rules READ from {GEN.name}: {blind}")
    c4 = blind is not None and "topw_k" in blind
    print(f"     `topw_k` — the only signed-weight rule — is blind, so it CANNOT grow at k=4: "
          f"{c4}  {'PASS' if c4 else 'FAIL'}")

    def sel(nm):
        for d in (RES, NEW):
            f = d / f"core_{nm}.json"
            if f.exists():
                return json.loads(f.read_text())
        return None
    c2 = True
    for a in NEWARMS:
        base_nm = a.replace("_sel08", "")
        s_new, s_old = sel(a), sel(base_nm)
        if not s_new or not s_old:
            print(f"  ② {a}: selections MISSING"); c2 = False; continue
        shared = sorted(set(s_new) & set(s_old))
        same = sum(set(s_new[p]) == set(s_old[p]) for p in shared)
        diff = len(shared) - same
        ok = diff > 0
        c2 = c2 and ok
        print(f"  ② {a:<18} differs from {base_nm} on {diff}/{len(shared)} prompts: {ok}  "
              f"{'PASS' if ok else 'FAIL'}")
    print(f"     if --select-npz changed nothing the growth would be fictitious")

    tg, _ = load_targets()
    S = load_sat(RES / f"sat_{BLIND}.npz")
    pids = sorted(set(S) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    n = len(pids)

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if f.exists():
                try:
                    Sa = load_sat(f)
                except Exception:
                    return None
                v = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                        for c in range(6)] for h in H[k]]) if p in Sa else np.nan
                              for k, p in enumerate(pids)])
                return np.nan_to_num(v, nan=np.nanmean(v)) if np.isfinite(v).sum() >= 200 else None
        return None

    base = vec(BLIND)
    if base is None:
        print("  UNRUNNABLE: comparator missing. Exit 2, never 0.")
        return 2
    rng = np.random.default_rng(SEED)
    idxb = [rng.integers(0, n, n) for _ in range(NBOOT)]

    def admit(nm):
        v = vec(nm)
        if v is None:
            return None
        d = v - base
        bs = np.array([float(d[b].mean()) for b in idxb])
        lo = float(np.percentile(bs, 2.5))
        return {"arm": nm, "margin": float(d.mean()), "lo": lo, "admitted": lo > 0}

    ok = True
    print(f"\n  ① WIRING reproduce R881's `lo`:")
    for a, ref in REF.items():
        r = admit(a)
        good = r and abs(r["lo"] - ref) < 0.005 and r["admitted"] == (ref > 0)
        ok = ok and bool(good)
        print(f"     {a:<12} lo {r['lo']:+.6f} vs {ref:+.6f}  {'PASS' if good else 'FAIL'}")
    if not (ok and c2 and c4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "controls": [bool(ok), bool(c2), bool(c4)]},
                  open(OUT / "k4_one_sided.json", "w"), indent=2)
        return 2

    fresh = [admit(a) for a in NEWARMS]
    fresh = [r for r in fresh if r]
    print(f"\n  ⭐ THE TWO NEW k=4 ARMS — printed whether admitted or not:")
    for r in fresh:
        print(f"     {r['arm']:<20} margin {r['margin']:+.6f}  lo {r['lo']:+.6f}  "
              f"admitted {r['admitted']}")
    new_adm = sum(r["admitted"] for r in fresh)

    r911 = json.loads(next(A24.glob("R911_*/results/matched_k_contrast.json")).read_text())
    k4 = next(s for s in r911["specs"] if s["spec"] == "matched k=4")
    sa, sn = k4["signed"]["a"], k4["signed"]["n"]
    oa, on = k4["other"]["a"] + new_adm, k4["other"]["n"] + len(fresh)
    sci, oci = wilson(sa, sn), wilson(oa, on)
    dis = sci[1] < oci[0] or oci[1] < sci[0]
    gap = sci[0] - oci[1]
    print(f"\n  ⭐⭐ THE k=4 CELL, variance group {k4['other']['n']} -> {on}:")
    print(f"     signed   {sa}/{sn:<3} [{sci[0]:.3f}, {sci[1]:.3f}]   (CANNOT grow — blind rule)")
    print(f"     variance {oa}/{on:<3} [{oci[0]:.3f}, {oci[1]:.3f}]")
    print(f"     disjoint {dis}   gap {gap:+.3f}   (was {k4['gap']:+.3f} at {k4['other']['n']})")

    world = "C" if new_adm else ("A" if dis else "B")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": "the new arms are REJECTED and k=4 now separates — **but by ONE-SIDED growth that "
             "cannot be balanced**, because `topw_k` is satisfaction-blind and has no second "
             "signed-weight rule to pair with",
        "B": "the new arms are REJECTED and k=4 still overlaps — the cell stays the odd one",
        "C": f"{new_adm} of the new arms IS ADMITTED — the variance group's clean zero breaks and "
             "the R909–R911 line weakens. This was reachable and is why the round was run"}[world])
    print(f"\n  ⛔⛔ AND THE STRUCTURAL FACT LEADS, NOT TRAILS: at k=4 only the variance side can")
    print(f"     grow. `topw_k` and `topabs_k` are satisfaction-BLIND per select_core.py:72, so")
    print(f"     `--select-npz` cannot make a new signed arm there. **Growing one side is the")
    print(f"     defect R911 fixed everywhere else, and at k=4 it is irreducible.** A balanced")
    print(f"     k=4 comparison would need a second signed-weight rule that consumes satisfaction,")
    print(f"     and the generator has none — that goes in the impossibility register as")
    print(f"     STRUCTURAL, with what it would require.")
    print(f"\n  ⚠ SO THE k=4 RESULT IS WEAKER THAN THE k-MATCHED ONE BY CONSTRUCTION, whatever its")
    print(f"    verdict. R911's PRIMARY specification remains the one to quote.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "new_arms": fresh,
               "n_new_admitted": new_adm,
               "k4": {"signed": {"a": sa, "n": sn, "ci95": list(sci)},
                      "variance": {"a": oa, "n": on, "ci95": list(oci)},
                      "disjoint": bool(dis), "gap": float(gap),
                      "gap_before": k4["gap"], "n_before": k4["other"]["n"]},
               "satisfaction_blind_rules": blind,
               "structural_impossibility": {
                   "what": "a BALANCED k=4 comparison",
                   "why": "topw_k is the only signed-weight rule and is satisfaction-blind, so "
                          "--select-npz cannot produce a new signed arm at k=4; topabs_k is blind "
                          "too",
                   "would_require": "a second signed-weight rule that consumes satisfaction",
                   "consequence": "growing one side is the defect R911 fixed everywhere else, and "
                                  "at k=4 it is irreducible"},
               "same_scoring_judge": "the new arms emit values from the 2B npz; only the SELECTION "
                                     "used the 0.8B satisfaction, so R895's judge-mixing defect is "
                                     "not reintroduced",
               "quote_instead": "R911's PRIMARY k-matched specification",
               "unit_note": "counts are ARMS; margins are A2 units vs genericpool16",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "k4_one_sided.json", "w"), indent=2)
    print(f"\n  artifact: results/k4_one_sided.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
