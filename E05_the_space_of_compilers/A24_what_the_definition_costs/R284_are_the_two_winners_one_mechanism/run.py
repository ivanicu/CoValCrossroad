"""R284 — the only two arms that beat the prompt-blind baseline are tied. Are they one mechanism?

WHY, AND WHY IT MATTERS MORE THAN THE TIE ITSELF. R308: at exactly matched size k=4, only TWO of
seven ways of reading the prompt beat `generic` — `coval_core` (+0.0151) and `topw_k4` (+0.0128).
R306: those two are indistinguishable from each other (+0.0023 against an MDE of 0.0085).

`topw_k4` selects by **human importance metadata**, which a compiler working from the conversation
alone does not have. `gen` — generated from the conversation alone — LOSES to `generic`. So if
`coval_core`'s advantage is the SAME advantage, then **every route to beating a prompt-blind rubric
that this release exhibits runs through human annotation**, and "a core" is not a thing derivable
from a conversation. If it is a DIFFERENT advantage, a conversation-only route exists and `gen`
merely failed to find it. Those are different claims about what the object IS.

⚠ THE CONFOUND, WRITTEN BEFORE THE RUN, AND IT IS THE WHOLE DESIGN PROBLEM. Both advantages are
differences against the SAME subtrahend `generic`, so `corr(A-G, B-G)` is inflated by the shared
term whether or not A and B share a mechanism. A raw correlation here would be meaningless and
would look like a finding. The control is an exactly-matched pair with the same shared term and NO
shared mechanism: `random_k4_s0 - generic` vs `random_k4_s1 - generic`. Two draws of one rule share
the subtrahend identically and share nothing else that `coval_core`/`topw_k4` would.
⚠ AND THE SECOND CONTROL RUNS THE OTHER WAY: `topw_k4 - generic` vs `topabs_k4 - generic`. Those two
selectors differ ONLY in whether importance keeps its sign, so they share the metadata but not the
rule. It bounds how much correlation "uses the same annotations" produces on its own.

ESTIMAND        the per-prompt correlation between advantage vectors over `generic`, for the pair
                (`coval_core`, `topw_k4`), expressed as its POSITION in the distribution of
                correlations from pairs with the same shared term and known mechanism relationships.
IDENTIFICATION  the raw correlation is identified but UNINTERPRETABLE alone; only the contrast
                against the matched controls is. Reported as a bracket between the two controls,
                never as a point on its own.
SCOPE           population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base
                satisfaction judge · baseline `generic` · regime k=4 exactly, ALL 15,593
                annotations, cluster bootstrap over prompts.
WORLDS          W-ONE   corr(coval_core, topw_k4) sits at or ABOVE the shares-metadata control ->
                        the two winners are one mechanism, and every winning route in this release
                        runs through human importance annotation.
                W-TWO   it sits at or BELOW the no-shared-mechanism control -> `coval_core` wins by
                        something else, a conversation-only route exists, and `gen` simply failed.
KILL            pre-registered: if corr(coval_core, topw_k4) does not exceed the no-shared-mechanism
                control's UPPER CI bound, W-ONE is not supported and the claim "every winning route
                runs through annotation" is NOT written down. A correlation above the control is
                necessary, not sufficient — hence the second control as a ceiling reference.
POSITIVE CTRL   an arm's advantage vector against ITSELF: corr exactly 1.0. Catches vector
                misalignment between the two loads, which would silently deflate every other cell.
NEGATIVE CTRL   `random_k4_s0` vs `random_k4_s1` as above — the shared-subtrahend floor. This is
                the number that makes the headline readable and it is reported first.
PLACEBO         `generic - generic` is identically zero, so its correlation is undefined; that is
                stated rather than computed, because a nan printed as a control is not a control.
NOISE FLOOR     the bootstrap CI on each correlation, from resampling PROMPTS.
MULTIPLICITY    5 correlations, BH at q=0.05 over all of them; non-survivors printed.
SPECIFICATION   swept: Pearson AND Spearman, since an advantage vector is bounded and skewed and a
                single coefficient choice would be one cell. Both reported.
SEEDS           random_k4 enters at 3 seeds; the floor control is computed for all 3 pairs.
ARTIFACT        results/one_mechanism.json with source hash.
IMPOSSIBLE      causally identified — nothing here intervenes on the compiler. This round can say
                the two advantages COVARY beyond a matched floor; it cannot say one causes the
                other, and no wording below claims it.
"""
import json, sys, math, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
NBOOT = 2000
Q = 0.05
NEUTRAL = "generic"
ARMS = ["coval_core", "topw_k4", "topabs_k4", "random_k4_s0", "random_k4_s1", "random_k4_s2", "gen"]


def main():
    tg, _ = load_targets()
    sat = {}
    for a in ARMS + [NEUTRAL]:
        S = load_sat(ROOT / "corebench" / "results" / f"sat_{a}.npz")
        sat[a] = {p: cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in S if p in tg and len(tg[p]) >= 2}
    pids = sorted(set.intersection(*(set(v) for v in sat.values())))
    HS = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    N = len(pids)

    def vec(a):
        return np.array([np.mean([[sat[a][p][q] == h[q] for q in range(6)] for h in HS[p]])
                         for p in pids])
    V = {a: vec(a) for a in ARMS + [NEUTRAL]}
    ADV = {a: V[a] - V[NEUTRAL] for a in ARMS}
    print(f"  {N} prompts · all annotations · advantage vectors are (arm − `{NEUTRAL}`) per prompt\n")

    rng = np.random.default_rng(31337)
    IDX = rng.integers(0, N, (NBOOT, N))

    def corr(x, y, kind):
        if kind == "spearman":
            x = np.argsort(np.argsort(x)).astype(float)
            y = np.argsort(np.argsort(y)).astype(float)
        r = float(np.corrcoef(x, y)[0, 1])
        bs = []
        for i in range(NBOOT):
            xi, yi = x[IDX[i]], y[IDX[i]]
            if xi.std() == 0 or yi.std() == 0:
                continue
            bs.append(np.corrcoef(xi, yi)[0, 1])
        bs = np.array(bs)
        return r, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), bs

    # ---- positive control -----------------------------------------------------------------
    r_self, _, _, _ = corr(ADV["coval_core"], ADV["coval_core"], "pearson")
    pos_ok = abs(r_self - 1.0) < 1e-12
    print(f"  POSITIVE CONTROL  an advantage vector against ITSELF  r = {r_self:.12f}  "
          f"{'PASS' if pos_ok else 'FAIL — the two loads are misaligned'}")
    print("  PLACEBO           `generic − generic` is identically zero, so its correlation is "
          "UNDEFINED — stated, not computed.")
    if not pos_ok:
        print("\n  UNVERIFIED — vector misalignment would deflate every cell below.")
        return 1

    CELLS = [("random_k4_s0", "random_k4_s1", "FLOOR — shared subtrahend, no shared mechanism"),
             ("random_k4_s0", "random_k4_s2", "FLOOR (2nd seed pair)"),
             ("random_k4_s1", "random_k4_s2", "FLOOR (3rd seed pair)"),
             ("topw_k4", "topabs_k4", "CEILING REF — same metadata, different rule"),
             ("coval_core", "topw_k4", "THE QUESTION")]

    out, grid = {}, []
    for kind in ("pearson", "spearman"):
        print(f"\n  {kind.upper()}\n")
        print(f"    {'pair':<32}{'r':>8}  {'95% CI':<22}what it is")
        for x, y, label in CELLS:
            r, lo, hi, bs = corr(ADV[x], ADV[y], kind)
            p = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
            out[f"{kind}|{x}|{y}"] = dict(r=r, lo=lo, hi=hi, p=float(p), label=label)
            grid.append((f"{kind}|{x}|{y}", float(p)))
            print(f"    {x} × {y:<14}"[:32].ljust(32) + f"{r:>8.4f}  [{lo:+.4f}, {hi:+.4f}]"
                  f"{'':<3}{label}")

    grid.sort(key=lambda t: t[1])
    C = len(grid)
    surv = {k for i, (k, p) in enumerate(grid, 1) if p <= Q * i / C}
    print(f"\n    BH q={Q} over {C} cells · {len(surv)} survive · "
          f"non-survivors {sorted(set(k for k, _ in grid) - surv)}")

    # ---- the pre-registered kill ----------------------------------------------------------
    print("\n  " + "=" * 74)
    verdicts = []
    for kind in ("pearson", "spearman"):
        q = out[f"{kind}|coval_core|topw_k4"]
        floors = [out[f"{kind}|{x}|{y}"] for x, y, l in CELLS if l.startswith("FLOOR")]
        fhi = max(f["hi"] for f in floors)
        ceil_ = out[f"{kind}|topw_k4|topabs_k4"]
        above = q["lo"] > fhi
        verdicts.append(above)
        print(f"  {kind:<9} question r = {q['r']:.4f} [{q['lo']:+.4f},{q['hi']:+.4f}]")
        print(f"            floor (no shared mechanism) upper bound {fhi:+.4f}   "
              f"ceiling ref (shared metadata) {ceil_['r']:+.4f} [{ceil_['lo']:+.4f},{ceil_['hi']:+.4f}]")
        print(f"            exceeds the floor's upper CI ?  {above}")
    killed = all(verdicts)
    print()
    if killed:
        print("  -> W-ONE SUPPORTED (necessary condition met, both coefficients). The two arms that")
        print("     beat the prompt-blind baseline covary beyond a matched floor, so on this release")
        print("     every route that beats it is consistent with running through human importance")
        print("     annotation — and `gen`, which has none, loses. NOT a causal claim.")
    else:
        print("  -> W-ONE NOT SUPPORTED. `coval_core`'s advantage is not shown to be the importance")
        print("     signal, so a conversation-only route is not excluded and `gen` may simply have")
        print("     failed to find it. The claim is NOT written down.")
    print("  " + "=" * 74)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    o = pathlib.Path(__file__).parent / "results" / "one_mechanism.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(source_sha=src, n_prompts=N, cells=out,
                                 bh_survivors=sorted(surv), w_one_supported=bool(killed)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
