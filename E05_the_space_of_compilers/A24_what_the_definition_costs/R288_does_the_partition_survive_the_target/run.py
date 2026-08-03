"""R288 — does the definition's partition survive a change of TARGET?

⚠ THIS ROUND EXISTS BECAUSE I CLOSED THE LAST ONE WITH AN UNCHECKED WALL. R287's closing line said
the remaining frontier is *"whether A2 against a single drawn annotator is the right target at all,
which no round here has attacked because the release offers no external criterion."* Two claims are
run together there and only ONE is true:
  · CONSTRUCT validity — is agreeing with humans the right goal — genuinely needs an external gold
    standard the release does not have. Correctly impossible.
  · TARGET / ESTIMATOR robustness — does the partition depend on WHICH human-agreement statistic —
    is fully answerable with what is on disk, and the standard names it twice (`metric-robust`,
    `estimator-robust`). **I asserted a wall around both.** realstat §4: an unchecked wall is
    UNVERIFIED, never SETTLED, and a closing sentence is exactly where one gets installed unexamined.

THE QUESTION. Every number in the definition is A2 — pairwise accuracy against a SINGLE drawn
annotator. That is one of at least six defensible targets this release supports. If the ADMITTED
SET moves when the target moves, the definition is target-dependent and must say so in its own text.

ESTIMAND        for each of 6 targets: each arm's score, its clause-① margin (vs random-from-rubric)
                and clause-② margin (vs size-matched prompt-blind), and the resulting ADMITTED SET.
IDENTIFICATION  exact for all six; each is a deterministic function of data already on disk.
SCOPE           population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base ·
                baselines named per clause · regime k=4 (k=15 blind arm for `full`), ALL 15,593
                annotations, cluster bootstrap over prompts.
WORLDS          W-STABLE  the admitted set is identical across all six targets -> the partition is
                          a property of the arms, and A2 was a representative choice rather than a
                          lucky one.
                W-TARGET  the admitted set changes on >=1 defensible target -> the definition is
                          target-dependent, the clause must name its statistic, and every number in
                          the file inherits that scope.
KILL            pre-registered: if the ADMITTED SET differs on any of the six targets, the
                definition's text must carry its target explicitly and FORMULATION.md records the
                disagreement rather than the majority.
POSITIVE CTRL   `gen_sham` (criteria from a DIFFERENT conversation) must be excluded under EVERY
                target. A target that admits it is not measuring agreement and is dropped, with
                that stated — the same disqualification logic R287 applied to a baseline.
NEGATIVE CTRL   an arm against itself under each target: identical score, gap exactly 0.
PLACEBO         included above.
NOISE FLOOR     per-cell MDE recomputed IN EACH TARGET's own units — a gap of 0.02 means different
                things in A2, A1 and tau, and comparing them on one scale would be the units error.
MULTIPLICITY    6 targets x 9 arms x 2 clauses; BH over the whole grid of tested cells.
SPECIFICATION   the target axis IS the specification curve. All six published, including any that
                the positive control disqualifies.
SEEDS           the consensus targets are seed-free; the single-annotator targets average over ALL
                annotators rather than drawing, so there is no draw to seed.
ARTIFACT        results/target_sweep.json with source hash.
IMPOSSIBLE      construct validity — whether human pairwise agreement is the right goal at all.
                Needs an external criterion the release does not carry. Named, not planned, and
                NOT conflated with the robustness question this round does answer.
"""
import json, sys, math, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
NBOOT = 1500
Q = 0.05
L = "ABCD"
ARMS = ["coval_core", "topw_k4", "generic", "gen", "full",
        "topwvar_k4", "random_k4_s0", "topabs_k4", "topvar_k4", "gen_sham"]
K = {"full": 15}                                  # everything else is k=4


def tau_b(a, b):
    n = len(a); c = d = ta = tb = 0
    for i, j in itertools.combinations(range(n), 2):
        x, y = np.sign(a[i] - a[j]), np.sign(b[i] - b[j])
        if x == 0 and y == 0: ta += 1; tb += 1
        elif x == 0: ta += 1
        elif y == 0: tb += 1
        elif x == y: c += 1
        else: d += 1
    den = math.sqrt((c + d + ta) * (c + d + tb))
    return (c - d) / den if den else 0.0


def main():
    tg, _ = load_targets()
    P = load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
    A_ = {a: load_sat(ROOT / "corebench" / "results" / f"sat_{a}.npz") for a in ARMS}
    pids = sorted(set(P) & set.intersection(*(set(v) for v in A_.values())) &
                  {p for p in tg if len(tg[p]) >= 2})
    N = len(pids)
    HY = [np.array([np.array(t[0], float) for t in tg[p]]) for p in pids]     # raw human scores
    HC = [np.array([cls(y) for y in hy], float) for hy in HY]
    CONS = [np.sign(hc.sum(axis=0)) for hc in HC]                             # consensus class
    MEANY = [hy.mean(axis=0) for hy in HY]
    print(f"  {N} prompts · {sum(len(h) for h in HY)} annotations · 6 targets\n")

    def yv(sat, p, idx=None):
        ks = sorted({i for i, _ in sat[p]}) if idx is None else idx
        return np.array(yvec(sat[p], ks), float)

    # the blind reference at each needed k, from the pool
    BLIND = {4: [0, 1, 2, 3], 15: list(range(15))}

    def target_vecs(gety):
        """gety(n) -> the 4-vector for prompt index n. Returns 6 per-prompt score arrays."""
        T = {k: np.empty(N) for k in
             ("A2·annot", "A2·consensus", "A1·annot", "A1·consensus", "tau·mean", "top1·mean")}
        for n in range(N):
            y = gety(n); c = np.array(cls(y), float)
            T["A2·annot"][n] = np.mean([(c == h).mean() for h in HC[n]])
            T["A2·consensus"][n] = (c == CONS[n]).mean()
            T["A1·annot"][n] = np.mean([float((c == h).all()) for h in HC[n]])
            T["A1·consensus"][n] = float((c == CONS[n]).all())
            T["tau·mean"][n] = tau_b(y, MEANY[n])
            T["top1·mean"][n] = float(int(np.argmax(y)) == int(np.argmax(MEANY[n])))
        return T

    SC = {a: target_vecs(lambda n, a=a: yv(A_[a], pids[n])) for a in ARMS}
    SC["_blind4"] = target_vecs(lambda n: np.array(yvec(P[pids[n]], BLIND[4]), float))
    SC["_blind15"] = target_vecs(lambda n: np.array(yvec(P[pids[n]], BLIND[15]), float))

    IDX = np.random.default_rng(31337).integers(0, N, (NBOOT, N))

    def gap(x, y):
        d = x - y
        mde = ZEFF * d.std(ddof=1) / math.sqrt(N)
        bs = d[IDX].mean(axis=1)
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        p = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
        return float(d.mean()), lo, hi, float(p), mde

    TARGETS = list(SC["coval_core"].keys())
    admitted, cells, grid = {}, {}, []
    for tname in TARGETS:
        adm = []
        for a in ARMS:
            if a == "random_k4_s0":
                continue
            blind = SC["_blind15" if K.get(a) == 15 else "_blind4"][tname]
            c1 = gap(SC[a][tname], SC["random_k4_s0"][tname])
            c2 = gap(SC[a][tname], blind)
            ok1 = c1[1] > 0 and abs(c1[0]) >= c1[4]
            ok2 = c2[1] > 0 and abs(c2[0]) >= c2[4]
            cells[f"{tname}|{a}"] = dict(c1=c1[:3], c2=c2[:3], mde1=c1[4], mde2=c2[4],
                                         ok1=bool(ok1), ok2=bool(ok2))
            grid += [(f"{tname}|{a}|1", c1[3]), (f"{tname}|{a}|2", c2[3])]
            if ok1 and ok2:
                adm.append(a)
        admitted[tname] = adm

    grid.sort(key=lambda x: x[1]); C_ = len(grid)
    surv = sum(1 for i, (_, p) in enumerate(grid, 1) if p <= Q * i / C_)

    print("  EACH TARGET, ITS SCALE, AND WHAT IT ADMITS\n")
    print(f"    {'target':<15}{'coval':>8}{'topw':>8}{'generic':>9}{'gen':>8}{'full':>8}"
          f"{'sham':>8}   ADMITTED")
    for tname in TARGETS:
        r = "".join(f"{SC[a][tname].mean():>8.4f}" if a != 'generic' else
                    f"{SC[a][tname].mean():>9.4f}"
                    for a in ("coval_core", "topw_k4", "generic", "gen", "full", "gen_sham"))
        print(f"    {tname:<15}{r}   {sorted(admitted[tname])}")

    # ---- controls -------------------------------------------------------------------------
    sham_bad = [t for t in TARGETS if "gen_sham" in admitted[t]]
    pos_ok = not sham_bad
    self_dev = max(abs(gap(SC[a][t], SC[a][t])[0]) for a in ARMS for t in TARGETS)
    neg_ok = self_dev == 0.0
    print(f"\n  POSITIVE CTRL  `gen_sham` excluded under EVERY target ?  "
          f"{'PASS' if pos_ok else f'FAIL at {sham_bad} — those targets are DISQUALIFIED'}")
    print(f"  NEGATIVE CTRL  an arm against itself, all targets: max |gap| = {self_dev:.2e}  "
          f"{'PASS' if neg_ok else 'FAIL'}")
    print(f"  BH q={Q} over {C_} cells · {surv} survive · {C_ - surv} do not")

    live = [t for t in TARGETS if t not in sham_bad]
    sets = {t: tuple(sorted(admitted[t])) for t in live}
    distinct = set(sets.values())
    print("\n  " + "=" * 76)
    print(f"  PRE-REGISTERED KILL: does the ADMITTED SET differ across the "
          f"{len(live)} live targets ?  {len(distinct) > 1}")
    for s in sorted(distinct):
        print(f"      {list(s)!s:<34} on {[t for t in live if sets[t] == s]}")
    if not neg_ok:
        print("  -> UNVERIFIED. The self-comparison is not zero; no target statement is readable.")
    elif len(distinct) > 1:
        print("  -> W-TARGET. The definition is TARGET-DEPENDENT. Its text must name the statistic,")
        print("     and the disagreement is published rather than resolved by majority.")
    else:
        print("  -> W-STABLE. The same arms are admitted under every live target, so A2 was a")
        print("     REPRESENTATIVE choice and not a lucky one. Construct validity is untouched.")
    print("  " + "=" * 76)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    o = pathlib.Path(__file__).parent / "results" / "target_sweep.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(source_sha=src, n_prompts=N, targets=TARGETS,
                                 scores={a: {t: float(SC[a][t].mean()) for t in TARGETS}
                                         for a in ARMS},
                                 admitted={t: sorted(v) for t, v in admitted.items()},
                                 cells=cells, disqualified=sham_bad,
                                 distinct_sets=[list(s) for s in sorted(distinct)]), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
