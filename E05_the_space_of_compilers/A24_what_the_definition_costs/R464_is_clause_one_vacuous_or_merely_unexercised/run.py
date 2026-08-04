"""R464 -- clause ① excludes 0 of 41 arms. Is it VACUOUS, or merely UNEXERCISED?

⛔ THE ANNOUNCED STEP IS LARGELY A LOOKUP. R463 closed proposing to find the provenance of the 37
   unlabelled anchors "from the artifact keys the gate already reads". Checked: **23 of the 37 already
   carry a source tag inside the gate's own code** (`clause1_excludes` -> R347, `clause2_excludes` ->
   R360, `clause3_excludes` -> R444). It is a lookup for most of them, not a search.
   *Thirty-second announced step checked.*

⛔ AND THE WORRY THAT REPLACED IT WAS A CASE-SENSITIVE GREP. Counting `EXCLUDES` in DEFINITION.md
   returns **1**, which reads as "§4's per-clause remedy was applied once". The document carries a
   full per-clause table under a LOWERCASE `| clause | excludes |` header, so the true count is 4.
   **A grep is a measuring instrument** -- caught before it became a round, and recorded because the
   near-miss is the same class §4 lists three times.

⭐ WHAT THE TABLE ACTUALLY SHOWS, AND IT IS THE QUEST'S CORE:
       ①  better than a random draw of the prompt's own rubric   ->  excludes **0 of 41**  (DERIVED)
       ②  better than a prompt-blind set                          ->  excludes 33 of 42   (MEASURED)
       ③  no prompt labels                                        ->  excludes 14 of 42   (DERIVED)
       ④  better than every response-only rule                    ->  excludes all 7 on the 2nd release
   §4's remedy, verbatim: *"name an admissible object this clause EXCLUDES. If nothing you have built
   is excluded, the clause is untested decoration."* **Clause ① excludes nothing.**

⚠ BUT "EXCLUDES NOTHING BUILT" AND "EXCLUDES NOTHING CONSTRUCTIBLE" ARE DIFFERENT CLAIMS, and only
  the second makes a clause vacuous. That distinction is what this round measures, and it is not
  forced: whether a deliberately-failing object is excluded depends on the inequality's strictness
  and on the noise floor, neither of which is decided in advance.

ESTIMAND (named before the method)
    Clause ① is: the core scores better than a random draw of the prompt's OWN rubric, at size k.
    Build objects DESIGNED to fail it and ask whether ① excludes them:
        EXCL(x) = [ mean_p A2(x,p) - mean_p A2(R_p,p) <= 0 ] with R_p a random k-subset of prompt p's
                  own rubric, paired, against the design's MDE.
    Arms constructed for the purpose, in increasing order of how hard they should be to exclude:
        `rubric_random`   a random rubric k-subset -- ① compares it to its own generating process
        `rubric_worst`    the WORST rubric k-subset per prompt -- must be excluded if ① means anything
        `rubric_anti`     the rubric subset that best ANTI-matches the human -- the hardest floor
        `coval_core`      the released core -- must NOT be excluded (the g=0 direction)
    ⭐ VACUOUS iff even `rubric_worst` and `rubric_anti` are not excluded.

IDENTIFICATION
    Identified: `sat_full.npz` carries every rubric criterion per prompt (k mean 15.5, min 4), so
    random and adversarial rubric subsets are constructible with no new judging.
    ⚠ NOT identified: whether an object failing ① could arise from a real GENERATOR. This measures
    whether the clause has extension, not whether anything would ever land in it.

SCOPE  population : home-release prompts carrying both the rubric and the core
       instrument : Qwen3.5-2B-Base; A2 over 6 pairs, 3 annotator draws held common
       baseline   : per-prompt random k-subsets of that prompt's OWN rubric, k matched to the core
       regime     : k matched per prompt to the core's own k (2..4)

WORLDS
    W-VACUOUS      not even the adversarially-worst rubric subset is excluded -> ① cannot exclude
                   anything constructible here and is decoration by §4's own test; the definition
                   should say so rather than carry it as a clause.
    W-UNEXERCISED  the adversarial arms ARE excluded -> ① is a real predicate with a real extension,
                   and "0 of 41" is a fact about the ARM SPACE, not about the clause. The document's
                   `DERIVED` status is then correct and its reading must be narrowed accordingly.
    W-DEGENERATE   even the released core is excluded -> the comparison is mis-specified and nothing
                   here is readable.

PREDICTION MATRIX
                    worst not excluded   worst excluded   core also excluded
    W-VACUOUS              0.90               0.05              0.05
    W-UNEXERCISED          0.05               0.90              0.05
    W-DEGENERATE           0.05               0.05              0.90

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the controls fire.
    the released core IS excluded                        -> W-DEGENERATE (checked FIRST)
    else `rubric_worst` or `rubric_anti` excluded        -> W-UNEXERCISED
    else                                                 -> W-VACUOUS
    a control fails                                      -> UNVERIFIED

CONTROLS
    g=0 / PLACEBO  `rubric_random` is a draw from the SAME process ① compares against, so its gap
                   must be ~0 and it must sit on the exclusion boundary, not far from it. If a draw
                   from the reference process is confidently excluded, the test is mis-calibrated.
    POSITIVE       `rubric_anti` is built by choosing, per prompt, the rubric subset that ANTI-matches
                   the human. If ① cannot exclude that, it cannot exclude anything.
    NEGATIVE       the released core must NOT be excluded -- the direction that would invalidate the
                   whole comparison.
    MDE            paired cluster bootstrap over prompts, reported beside every gap.
    SEEDS          3 draws for every randomised arm; spread reported.

MULTIPLICITY  4 arms x 3 seeds; all printed, nothing selected.
ARTIFACT      results/r464_clause_one.json
IMPOSSIBLE HERE, NAMED
    * whether a real GENERATOR would ever produce an ①-failing object -- needs a generator, and this
      round deliberately constructs adversarially instead.
    * clause ①'s behaviour on the second release -- the rubric does not exist there (R433).
"""
from __future__ import annotations
import hashlib, itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
ZEFF = 1.959964 + 0.841621
L = "ABCD"
PAIRS = list(itertools.combinations(range(4), 2))


def stable(pid): return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)
def signs(Y): return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R464 · clause ① excludes 0 of 41. VACUOUS, or merely UNEXERCISED?\n")
    print("  ⛔ the announced step is largely a LOOKUP: 23 of the 37 unlabelled anchors already")
    print("     carry a source tag in the gate's own code. Thirty-second step checked.")
    print("  ⛔ and the worry that replaced it was a CASE-SENSITIVE GREP -- `EXCLUDES` returns 1,")
    print("     but the per-clause table uses a lowercase header and the true count is 4.\n")

    for nm in ("full", "coval_core"):
        if not (SATD / f"sat_{nm}.npz").exists():
            print(f"  UNRUNNABLE: sat_{nm}.npz absent. Exit 2, never 0."); return 2
    rub, core = SC.load_sat(SATD / "sat_full.npz"), SC.load_sat(SATD / "sat_coval_core.npz")
    targets, _ = SC.load_targets()
    pids = sorted(set(rub) & set(core) & set(targets))
    n = len(pids)
    if n < 200:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2
    SEEDS = (0, 1, 2)
    HC = {p: np.array([SC.cls(np.array(targets[p][int(np.random.default_rng(1000 * s + stable(p))
                                                      .integers(len(targets[p])))][0], float))
                       for s in SEEDS]) for p in pids}
    RM, CM, KK = {}, {}, {}
    for p in pids:
        cs = sorted({c for (c, _) in rub[p]})
        RM[p] = np.array([[rub[p].get((c, l), 0.0) for l in L] for c in cs])
        ks = sorted({c for (c, _) in core[p]})
        CM[p] = np.array([[core[p].get((c, l), 0.0) for l in L] for c in ks])
        KK[p] = min(len(ks), len(cs))
    print(f"  prompts {n};  rubric k mean {np.mean([len(RM[p]) for p in pids]):.1f}, "
          f"core k mean {np.mean([KK[p] for p in pids]):.2f}")

    def a2(Y, p):
        return float((signs(Y)[None, :] == HC[p]).mean())

    def ref_vec(seed):
        """a random k-subset of each prompt's OWN rubric -- the process ① compares against."""
        v = np.zeros(n)
        for i, p in enumerate(pids):
            rg = np.random.default_rng(seed * 9176 + stable(p))
            idx = rg.choice(len(RM[p]), size=KK[p], replace=False)
            v[i] = a2(RM[p][idx].mean(axis=0), p)
        return v

    def arm(kind, seed=0):
        v = np.zeros(n)
        for i, p in enumerate(pids):
            if kind == "coval_core":
                v[i] = a2(CM[p].mean(axis=0), p); continue
            rg = np.random.default_rng(seed * 4441 + stable(p))
            cand = list(itertools.combinations(range(len(RM[p])), KK[p]))
            if len(cand) > 400:
                cand = [tuple(rg.choice(len(RM[p]), size=KK[p], replace=False)) for _ in range(400)]
            scores = np.array([a2(RM[p][list(c)].mean(axis=0), p) for c in cand])
            j = (int(rg.integers(len(cand))) if kind == "rubric_random"
                 else int(np.argmin(scores)))
            v[i] = scores[j]
        return v

    def paired(x, r, seed=0):
        d = x - r
        mde = ZEFF * d.std(ddof=1) / np.sqrt(n)
        rb = np.random.default_rng(19 + seed)
        bs = np.array([d[rb.integers(0, n, n)].mean() for _ in range(3000)])
        return (float(d.mean()), float(mde), float(np.percentile(bs, 2.5)),
                float(np.percentile(bs, 97.5)))

    print("\n  ⭐ DOES ① EXCLUDE ANYTHING CONSTRUCTIBLE?  (excluded = gap <= 0 and CI excludes 0)")
    print(f"    {'arm':<16}{'gap vs random rubric':>22}{'MDE':>9}{'CI':>22}  excluded?")
    rows = {}
    for kind in ("coval_core", "rubric_random", "rubric_worst", "rubric_anti"):
        gs = []
        for sd in SEEDS:
            r = ref_vec(sd)
            k = "rubric_worst" if kind == "rubric_anti" else kind   # anti == worst under this target
            x = arm(k, sd)
            gs.append(paired(x, r, sd))
        g = float(np.mean([a[0] for a in gs])); m = float(np.mean([a[1] for a in gs]))
        lo = float(np.mean([a[2] for a in gs])); hi = float(np.mean([a[3] for a in gs]))
        exc = bool(hi < 0)
        rows[kind] = {"gap": g, "mde": m, "ci": [lo, hi], "excluded": exc,
                      "spread": float(np.std([a[0] for a in gs]))}
        print(f"    {kind:<16}{g:>+22.4f}{m:>9.4f}   [{lo:+.4f},{hi:+.4f}]  "
              f"{'EXCLUDED' if exc else 'not excluded'}")

    print("\n  CONTROLS")
    rr = rows["rubric_random"]
    g0_ok = not rr["excluded"] and abs(rr["gap"]) < 3 * rr["mde"]
    print(f"    g=0/PLACEBO  `rubric_random` is a draw from the SAME process ① compares against ->")
    print(f"                 gap {rr['gap']:+.4f} vs MDE {rr['mde']:.4f}, "
          f"{'not excluded' if not rr['excluded'] else 'EXCLUDED'}   "
          f"{'PASS' if g0_ok else '⛔ FAIL — the reference process is being excluded by itself'}")
    cc = rows["coval_core"]
    neg_ok = not cc["excluded"]
    print(f"    NEGATIVE     the released core must NOT be excluded -> "
          f"{'not excluded' if neg_ok else 'EXCLUDED'}   {'PASS' if neg_ok else '⛔ FAIL'}")
    rw = rows["rubric_worst"]
    print(f"    POSITIVE     the adversarially WORST rubric subset -> "
          f"{'EXCLUDED' if rw['excluded'] else 'not excluded'}   "
          f"{'PASS — ① has extension' if rw['excluded'] else '⚠ ① excludes nothing even here'}")

    ctrl_ok = g0_ok and neg_ok
    if not ctrl_ok:
        world = "UNVERIFIED"
    elif cc["excluded"]:
        world = "W-DEGENERATE"
    elif rw["excluded"] or rows["rubric_anti"]["excluded"]:
        world = "W-UNEXERCISED"
    else:
        world = "W-VACUOUS"
    print(f"\n  WORLD: {world}")
    if world == "W-UNEXERCISED":
        print(f"    ⭐ ① IS A REAL PREDICATE WITH A REAL EXTENSION: the adversarially worst rubric")
        print(f"       subset is excluded at {rw['gap']:+.4f} [{rw['ci'][0]:+.4f},{rw['ci'][1]:+.4f}].")
        print(f"       So `0 of 41` is a fact about the ARM SPACE, not about the clause, and §4's")
        print(f"       'untested decoration' verdict does NOT apply — the clause is UNEXERCISED.")
        print(f"    ⚠ What it does NOT establish: that any real generator would produce such an")
        print(f"       object. The excluded arm here was built adversarially, on purpose.")
    elif world == "W-VACUOUS":
        print(f"    ⛔ ① excludes nothing constructible. By §4's own test it is DECORATION and the")
        print(f"       definition should say so rather than carry it as a clause.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_prompts": n, "arms": rows,
           "controls": {"g0_ok": bool(g0_ok), "negative_ok": bool(neg_ok)}}
    (RES / "r464_clause_one.json").write_text(json.dumps(out, indent=2))
    print(f"\n  artifact: {RES/'r464_clause_one.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
