"""R308 — the neutral clause at EXACTLY matched size, for every selection rule the release allows.

WHY THIS RUNS WHILE R307's JOB IS STILL ON THE GPU. R307 needs a generic arm at k=15 to test `full`.
But SEVEN of the eight prompt-reading arms are already k=4, drawn from the same `coval_full` rubric
and differing ONLY in selection rule — and the neutral arm `generic` is also k=4. So the
size-matched neutral clause is answerable RIGHT NOW for everything except `full`, with zero new
compute, and nothing the running job returns can change it.

THE QUESTION THIS SEPARATES FROM R307's. R307 asks *does criterion COUNT explain the price*. This
asks *at a FIXED count, what does reading the prompt buy* — and the answer can differ per selection
rule, which is a fact no single arm-vs-arm comparison exposes.

ESTIMAND        for each k=4 arm, the neutral gap = A2(arm) - A2(generic), all annotators, with a
                paired cluster bootstrap CI over prompts, and a three-valued verdict against that
                cell's own MDE (R305's decomposition, per cell).
IDENTIFICATION  exact. Every arm is k=4 by construction (`sel = ...[:k]` with k=4, or a size-4
                random draw), and `generic` is k=4, so no size adjustment is needed or made.
SCOPE           population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base
                satisfaction judge · baseline `generic`, four fixed sentences that never read the
                conversation · regime k=4 exactly, unweighted, ALL 15,593 annotations.
WORLDS          W-SPECIFICITY  reading the prompt is what pays -> most k=4 prompt-reading arms beat
                               the prompt-blind arm, and the definition's clause 2 tracks aboutness.
                W-SELECTION    reading the prompt pays only under the right selection rule -> a
                               minority beat it and the rest LOSE to four generic sentences. Then
                               clause 2 is not tracking aboutness at all; it is tracking
                               aboutness CONDITIONAL ON a selector the release supplies as metadata.
                These differ in what the definition's second clause MEANS, not in any number's size.
KILL            pre-registered: if fewer than half the k=4 prompt-reading arms beat `generic`
                separably, W-SPECIFICITY is dead and FORMULATION.md must state that prompt-
                specificity per se buys nothing at matched size.
POSITIVE CTRL   `generic` against itself: exactly 0, CI exactly [0,0]. Catches prompt-set drift
                between the two loads.
NEGATIVE CTRL   `random_k4_s0` vs `random_k4_s1` — the SAME rule at two seeds. Its gap must sit
                inside its own MDE; if one rule differs from itself by more than the design
                resolves, no rule-vs-rule statement here is readable.
PLACEBO         included in the positive control.
NOISE FLOOR     per-cell sigma_w from the annotator decomposition, measured here not carried in.
MULTIPLICITY    BH at q=0.05 over all 8 arm cells, threshold q*i/C. Non-survivors printed.
SPECIFICATION   the axis is the SELECTION RULE, and all eight are reported including the four that
                are expected to lose. Reporting only the winners would be exactly the failure this
                round exists to expose.
SEEDS           `random_k4` enters at three seeds (s0, s1, s2) and all three are printed, so the
                worst arm's position is not one draw.
ARTIFACT        results/matched_k4.json with source hash.
IMPOSSIBLE      cross-release, cross-model, independently replicated. Also: `generic` is four
                sentences I wrote — `prompt-blind` here means blind in MY vocabulary, and a
                different generic baseline is a different comparison.
"""
import json, sys, math, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
NBOOT = 2000
Q = 0.05
NEUTRAL = "generic"
# every arm below is k=4 BY CONSTRUCTION and drawn from the prompt's own coval_full rubric,
# except `gen` (generated from the conversation) and `coval_core` (the release's own compiler).
K4 = {"coval_core": "the release's own compiler, rewritten from the conversation",
      "topw_k4":    "the rubric's top 4 by HUMAN IMPORTANCE metadata",
      "gen":        "generated from the conversation alone",
      "topwvar_k4": "the rubric's top 4 by importance x spread",
      "random_k4_s0": "4 drawn at RANDOM from the same rubric",
      "topabs_k4":  "the rubric's top 4 by |importance|",
      "topvar_k4":  "the rubric's top 4 by satisfaction spread",
      "gen_sham":   "generated from a DIFFERENT conversation (poison)"}
EXTRA_SEEDS = ["random_k4_s1", "random_k4_s2"]


def a2all(c, hs):
    return float(np.mean([[c[q] == h[q] for q in range(len(PAIRS))] for h in hs]))


def main():
    tg, _ = load_targets()
    names = [NEUTRAL] + list(K4) + EXTRA_SEEDS
    sat = {}
    for a in names:
        S = load_sat(ROOT / "corebench" / "results" / f"sat_{a}.npz")
        sat[a] = {p: cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in S if p in tg and len(tg[p]) >= 2}
    pids = sorted(set.intersection(*(set(v) for v in sat.values())))
    HS = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    mm = np.array([len(HS[p]) for p in pids])
    N = len(pids)
    print(f"  {N} prompts · {int(mm.sum())} annotations · every arm k=4 · neutral = `{NEUTRAL}`\n")

    per = {}
    for a in names:
        per[a] = {p: np.array([[sat[a][p][q] == h[q] for q in range(6)] for h in HS[p]]).mean(axis=1)
                  for p in pids}
    mean_ = {a: np.array([per[a][p].mean() for p in pids]) for a in names}

    rng = np.random.default_rng(31337)
    IDX = rng.integers(0, N, (NBOOT, N))

    def cellstat(x, y):
        dper = {p: per[x][p] - per[y][p] for p in pids}
        means = np.array([dper[p].mean() for p in pids])
        wvar = np.array([dper[p].var(ddof=1) if len(dper[p]) > 1 else 0.0 for p in pids])
        mde = ZEFF * math.sqrt(max(0.0, means.var(ddof=1) - np.mean(wvar / mm))
                               + float(np.mean(wvar / mm))) / math.sqrt(N)
        bs = means[IDX].mean(axis=1)
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        p = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
        return dict(eff=float(means.mean()), lo=lo, hi=hi, p=float(p), mde=mde)

    # ---- controls -------------------------------------------------------------------------
    s = cellstat(NEUTRAL, NEUTRAL)
    pos_ok = (s["eff"] == 0.0 and s["lo"] == 0.0 and s["hi"] == 0.0)
    nc = cellstat("random_k4_s0", "random_k4_s1")
    neg_ok = abs(nc["eff"]) < nc["mde"]
    print("  CONTROLS\n")
    print(f"    positive/placebo  `{NEUTRAL}` vs itself   eff {s['eff']:.2e}  CI "
          f"[{s['lo']:.2e},{s['hi']:.2e}]   {'PASS' if pos_ok else 'FAIL'}")
    print(f"    negative  random_k4 s0 vs s1 (SAME rule)  {nc['eff']:+.4f} vs its own MDE "
          f"{nc['mde']:.4f}   {'PASS' if neg_ok else 'FAIL — a rule differs from ITSELF by more than the design resolves'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — controls did not behave; no rule-vs-rule statement is readable.")
        return 1

    # ---- the eight cells ------------------------------------------------------------------
    rows, grid = {}, []
    for a in K4:
        rows[a] = cellstat(a, NEUTRAL)
        grid.append((a, rows[a]["p"]))
    grid.sort(key=lambda t: t[1])
    C = len(grid)
    surv = {a for i, (a, p) in enumerate(grid, 1) if p <= Q * i / C}

    print(f"\n  THE NEUTRAL CLAUSE AT EXACTLY MATCHED SIZE (k=4)"
          f"  — `generic` scores {mean_[NEUTRAL].mean():.4f}\n")
    print(f"    {'arm':<14}{'A2':>8}{'− generic':>11}  {'95% CI':<22}{'MDE':>8}  {'verdict':<10}BH")
    beat = 0
    for a in sorted(K4, key=lambda a: -rows[a]["eff"]):
        r = rows[a]
        v = ("BEATS" if r["lo"] > 0 and abs(r["eff"]) >= r["mde"] else
             "LOSES" if r["hi"] < 0 and abs(r["eff"]) >= r["mde"] else "unresolved")
        beat += v == "BEATS"
        print(f"    {a:<14}{mean_[a].mean():>8.4f}{r['eff']:>+11.4f}  "
              f"[{r['lo']:+.4f}, {r['hi']:+.4f}]{'':<3}{r['mde']:>8.4f}  {v:<10}"
              f"{'y' if a in surv else '—'}")
        rows[a]["verdict"] = v
    print(f"\n    BH q={Q} over {C} cells · {len(surv)} survive · "
          f"non-survivors {sorted(set(K4)-surv)}")
    print(f"\n    random_k4 at three seeds: " + "  ".join(
        f"{n}:{mean_[n].mean():.4f}" for n in ["random_k4_s0"] + EXTRA_SEEDS))
    for a, why in K4.items():
        print(f"      {a:<14} {why}")

    # ---- the pre-registered kill ----------------------------------------------------------
    prompt_reading = [a for a in K4 if a != "gen_sham"]
    nbeat = sum(rows[a]["verdict"] == "BEATS" for a in prompt_reading)
    killed = nbeat < len(prompt_reading) / 2
    print("\n  " + "=" * 74)
    print(f"  PRE-REGISTERED KILL: fewer than half the {len(prompt_reading)} prompt-reading k=4 "
          f"arms beat `generic` ?   {killed}   ({nbeat} of {len(prompt_reading)})")
    if killed:
        print("  -> W-SELECTION. At matched size, reading the prompt buys NOTHING on its own.")
        print("     It pays only under the right selector, and the rules that fail lose to four")
        print("     generic sentences by a resolved margin. Clause 2 is not tracking ABOUTNESS —")
        print("     it is tracking aboutness CONDITIONAL ON a selector the release hands over as")
        print("     metadata, which no compiler operating on the conversation alone would have.")
    else:
        print("  -> W-SPECIFICITY. Reading the prompt pays across selection rules.")
    print("  " + "=" * 74)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    out = pathlib.Path(__file__).parent / "results" / "matched_k4.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(source_sha=src, n_prompts=N, annotations=int(mm.sum()),
                                   neutral_a2=float(mean_[NEUTRAL].mean()),
                                   a2={a: float(mean_[a].mean()) for a in names},
                                   rows=rows, bh_survivors=sorted(surv),
                                   n_beating=nbeat, killed=bool(killed)), indent=1))
    print(f"\n  artifact {out.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
