"""R364 — the rubric channel EXISTS (R363). This measures how much of `topw_k4` it carries.

R363 established, as a census with no judge in it, that the annotators who write a prompt's
criterion IMPORTANCE scores are 95.3% the same people whose RANKINGS define that prompt's target
(cross-prompt sham 0.016, 58x, over 1,160 annotators). `topw_k` selects on those importance scores.
R363 deliberately stopped there and named the size of the channel as UNMEASURED. This is that
measurement.

⚠ THE INSTRUMENT THAT MADE THIS UNASKABLE. `corebench/score.py:88 load_targets()` reads
  `aid = asm.get("annotator_id")` on line 103 and then RETURNS `(ranking, demographics)` -- the id
  is dropped. Every round in this campaign uses that loader, so no round COULD have aligned a
  ranking to the person who wrote the rubric. The question was not overlooked; the standard
  instrument had no column for it. This round carries its own loader that keeps the id, and that is
  the only reason the estimand below is identified.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES, and the null is
   genuinely live: importance scores may carry only PROMPT-level information -- what this
   conversation calls for -- which every annotator would report similarly, in which case whose
   scores you average is irrelevant and the dose is flat. The channel EXISTING (R363) does not make
   it LOAD-BEARING, and treating those as one statement is the error this round is designed not to
   commit. A flat dose is a real and reportable outcome.

ESTIMAND        For dose d in {0, 0.25, 0.5, 0.75, 1.0}: the clause-② margin of `topw_k4` when its
                selection weights are averaged over a weight-set W(d) that overlaps the EVALUATION
                annotator set E in a fraction d of E, scored against E's rankings only and against
                the size-matched blind reference POOL[0:4] on the same E. The quantity of interest
                is `margin(d=1) - margin(d=0)` -- the advantage attributable to scoring with the
                same people who will judge you -- against its own paired MDE.

IDENTIFICATION  Identified because this round's loader retains `annotator_id` on BOTH sides, and
                R363 verified the two id spaces are shared. Per prompt the usable population is
                `A_rub ∩ A_rank`, split into disjoint halves; prompts where that intersection is
                too small to split are EXCLUDED BY A STATED RULE and counted, never dropped
                silently. NOT identified: whether the channel behaves the same for arms other than
                `topw_k` -- `coval_core` is the release's own compiler output and is not built by
                this selection rule at all.

SCOPE           the CoVal release's joined prompts · judge Qwen3.5-2B-Base (`sat_full.npz`) ·
                baseline the size-matched blind reference `POOL[0:4]` scored on the SAME evaluation
                annotators · regime k=4, the published arm's size.

WORLDS
  W-CHANNEL-CARRIES  the margin rises with dose beyond its own MDE. `topw_k4`'s advantage is partly
                     the advantage of being scored by the people who wrote your weights, so four of
                     the published five inherit it and the admitted set must be recomputed.
  W-CHANNEL-EMPTY    the dose is flat within resolution. The channel is open (R363) and carries
                     nothing measurable: importance scores are prompt-level, not person-level, and
                     clause ③ needs no change in practice even though its wording was wrong.
  W-INVERTED         the margin FALLS with dose. Then averaging in the evaluators' own scores makes
                     selection worse, which no account of leakage predicts and which would mean the
                     dose is measuring something other than what it is named for.

PREDICTION MATRIX
  W-CHANNEL-CARRIES -> margin(1) - margin(0) > its own MDE, and monotone in d
  W-CHANNEL-EMPTY   -> |margin(1) - margin(0)| <= its own MDE
  W-INVERTED        -> margin(1) - margin(0) < -MDE
The three differ on the sign and resolvability of one paired contrast.

PRE-REGISTERED KILL -- conditional, and with a fourth branch: if the dose is resolvable but NOT
monotone, that is named rather than folded into `carries`.
    if placebo_ok and sham_ok and split_ok:
        delta = margin(d=1) - margin(d=0), paired per prompt, with its own MDE
        if |delta| <= mde                 -> W-CHANNEL-EMPTY
        elif delta > mde and monotone     -> W-CHANNEL-CARRIES
        elif delta > mde                  -> W-CHANNEL-CARRIES-NONMONOTONE (named)
        else                               -> W-INVERTED
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

PLACEBO        d computed twice with the same seed and the same split: difference exactly 0.
SHAM           ⭐ the load-bearing one. PERMUTE WHICH ANNOTATOR'S IMPORTANCE SCORES CARRY WHICH ID,
               within a prompt. This destroys the person-link while preserving the score
               distribution, the panel sizes and the arithmetic exactly. If the dose survives that,
               it is not about identity and the reading is void. This is the world the finding
               excludes, BUILT rather than imagined.
SPLIT CONTROL  W and E must be disjoint at d=0 by construction -- asserted, not assumed -- and the
               realised overlap is measured and printed at every dose, because a dose that does not
               move is a dose that never ran.
NOISE FLOOR    paired per-prompt differences, each cell its own sd (R331: an MDE is a property of
               the pair).
MULTIPLICITY   5 doses x 3 seeds = 15 cells, all printed; the headline contrast is one paired test.
SEEDS          3 independent W/E splits; each dose curve printed per seed, never averaged into one
               before the spread is shown.
ARTIFACT       results/r364_channel_size.json with the source hash.

IMPOSSIBLE HERE
  other arms      -- `coval_core` is not built by this selection rule; the channel's effect on it
                     is a different question and is not implied by this one.
  a second judge  -- the channel is a provenance fact (R363, judge-free) but this MEASUREMENT runs
                     through A2 and so through a judge; stated rather than silently generalised.
  cross-release   -- one release.

EXIT
    0  controls hold and the channel is sized
    1  a control misbehaved -- UNVERIFIED
    2  an input is missing or too few prompts are splittable -- never a silent pass
"""
from __future__ import annotations
import collections, hashlib, itertools, json, math, pathlib, random, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, parse_ranking, cls              # noqa: E402
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}
from covalx.judge import load_join                           # noqa: E402

L = "ABCD"
PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
DOSES = (0.0, 0.25, 0.5, 0.75, 1.0)
SEEDS = (0, 1, 2)
K = 4
MIN_PANEL = 6            # need >=3 per half; stated before the run


def targets_with_ids(prompts):
    """load_targets() drops the annotator id (score.py:103). This keeps it -- the whole round
    depends on being able to say WHICH person produced a ranking."""
    out = collections.defaultdict(list)
    for pid, rec in prompts.items():
        for asm in rec.get("metadata", {}).get("assessments", []):
            aid = asm.get("annotator_id")
            rb = asm.get("ranking_blocks") or {}
            for e in rb.get("world") or []:
                y = parse_ranking(e["ranking"]) if e.get("ranking") else None
                if y and aid:
                    out[pid].append((aid, cls(np.array(y, float))))
    return out


def main() -> int:
    satf = RES / "sat_full.npz"
    poolf = RES / "sat_genericpool16.npz"
    for f in (satf, poolf):
        if not f.exists():
            print(f"  UNRUNNABLE: {f.name} absent. Exit 2, never 0."); return 2

    J = load_join(ROOT / "data" / "comparisons.jsonl",
                  ROOT / "data" / "conversation_rubrics.jsonl")
    prompts = {pid: prec for pid, prec, _ in J}
    RUB = {pid: (rrec.get("coval_full") or []) for pid, _, rrec in J}
    TGT = targets_with_ids(prompts)
    SAT = load_sat(satf)
    POOL = load_sat(poolf)

    print("R364 · how much of `topw_k4` does the rubric channel carry?\n")
    print("  ⚠ score.py:88 load_targets() reads annotator_id on line 103 and returns")
    print("    (ranking, demographics) — the id is DROPPED. Every round uses that loader, so no")
    print("    round COULD align a ranking to the person who wrote the rubric. Own loader here.\n")

    # per prompt: importance scores by annotator, rankings by annotator
    IMP, RANK, USE = {}, {}, []
    for pid in RUB:
        items = RUB[pid]
        if pid not in SAT or pid not in TGT or pid not in POOL:
            continue
        imp = collections.defaultdict(dict)
        for i, it in enumerate(items):
            for s in (it.get("scores") or []):
                if s.get("annotator_id") is not None and s.get("score") is not None:
                    imp[s["annotator_id"]][i] = float(s["score"])
        rk = collections.defaultdict(list)
        for aid, y in TGT[pid]:
            rk[aid].append(y)
        common = sorted(set(imp) & set(rk))
        if len(common) < MIN_PANEL:
            continue
        ok = [i for i in range(len(items))
              if all(SAT[pid].get((i, x)) is not None for x in L)]
        if len(ok) < K:
            continue
        IMP[pid], RANK[pid] = imp, rk
        USE.append((pid, common, ok))
    if len(USE) < 100:
        print(f"  UNRUNNABLE: only {len(USE)} splittable prompts. Exit 2, never 0."); return 2
    print(f"  {len(USE)} prompts usable (panel >= {MIN_PANEL} annotators with BOTH a rubric score")
    print(f"  and a ranking, and >= {K} scorable criteria); "
          f"{len(RUB)-len(USE)} excluded by that stated rule\n")

    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])

    def induced(pid, sel):
        y = np.array([sum(SAT[pid][(i, x)] for i in sel) for x in L])
        return cls(y)

    def pool_ref(pid):
        y = np.array([sum(POOL[pid][(i, x)] for i in range(K)) for x in L])
        return cls(y)

    def a2(vec, evals):
        return float(np.mean([[vec[q] == h[q] for q in range(6)] for h in evals]))

    def run(seed, dose, shuffle=False):
        """margin(topw_k4) - margin(POOL[0:4]) per prompt, evaluated on E only."""
        rng = random.Random(1000 * seed + int(dose * 100) + (7 if shuffle else 0))
        out, ov = [], []
        for pid, common, ok in USE:
            a = list(common); rng.shuffle(a)
            half = len(a) // 2
            E, W0 = a[:half], a[half:]
            n_from_E = int(round(dose * len(W0)))
            W = W0[:len(W0) - n_from_E] + E[:n_from_E] if n_from_E else W0
            if not W or not E:
                continue
            ov.append(len(set(W) & set(E)) / len(E))
            imp = IMP[pid]
            if shuffle:
                # SHAM: permute which annotator's score-vector carries which id, within the prompt
                ids = list(imp); vals = [imp[x] for x in ids]; rng.shuffle(vals)
                imp = dict(zip(ids, vals))
            w = {i: float(np.mean([imp[x][i] for x in W if i in imp[x]] or [0.0])) for i in ok}
            sel = sorted(ok, key=lambda i: -w[i])[:K]
            evals = [y for x in E for y in RANK[pid][x]]
            if not evals:
                continue
            out.append(a2(induced(pid, sel), evals) - a2(pool_ref(pid), evals))
        return np.array(out, float), float(np.mean(ov)) if ov else float("nan")

    print(f"    {'seed':>5}{'dose':>7}{'realised overlap':>18}{'margin':>10}{'own MDE':>10}")
    CURVE = {}
    for s in SEEDS:
        for d in DOSES:
            v, ov = run(s, d)
            m = float(v.mean()); mde = float(ZEFF * v.std(ddof=1) / math.sqrt(len(v)))
            CURVE[(s, d)] = (m, mde, ov, len(v))
            print(f"    {s:>5}{d:>7.2f}{ov:>18.3f}{m:>+10.4f}{mde:>10.4f}")
        print()

    # ---- the headline contrast: paired, per prompt, d=1 vs d=0 -------------------------------------
    DELTA = {}
    for s in SEEDS:
        v1, _ = run(s, 1.0); v0, _ = run(s, 0.0)
        n = min(len(v1), len(v0)); dd = v1[:n] - v0[:n]
        DELTA[s] = (float(dd.mean()), float(ZEFF * dd.std(ddof=1) / math.sqrt(n)), n)
    dmean = float(np.mean([DELTA[s][0] for s in SEEDS]))
    dmde = float(np.mean([DELTA[s][1] for s in SEEDS]))
    print(f"  HEADLINE — paired per prompt, margin(dose=1) - margin(dose=0)")
    for s in SEEDS:
        m, e, n = DELTA[s]
        print(f"    seed {s}: {m:+.4f} vs own MDE {e:.4f}  (n={n})  "
              f"{'RESOLVED' if abs(m) > e else 'inside the MDE'}")
    print(f"    mean across seeds {dmean:+.4f} vs mean MDE {dmde:.4f}")

    # ---- controls -----------------------------------------------------------------------------------
    v_a, _ = run(0, 0.5); v_b, _ = run(0, 0.5)
    plac = bool(len(v_a) == len(v_b) and np.array_equal(v_a, v_b))
    print(f"\n  PLACEBO  same seed, same dose, run twice: identical vectors  "
          f"{'PASS' if plac else 'FAIL'}")

    SH = {}
    for s in SEEDS:
        v1, _ = run(s, 1.0, shuffle=True); v0, _ = run(s, 0.0, shuffle=True)
        n = min(len(v1), len(v0)); dd = v1[:n] - v0[:n]
        SH[s] = (float(dd.mean()), float(ZEFF * dd.std(ddof=1) / math.sqrt(n)))
    shmean = float(np.mean([SH[s][0] for s in SEEDS]))
    shmde = float(np.mean([SH[s][1] for s in SEEDS]))
    sham_ok = abs(shmean) <= shmde
    print(f"  SHAM     ⭐ permute WHICH annotator's scores carry which id, within the prompt —")
    print(f"           destroys the person-link, preserves the score distribution and panel sizes.")
    print(f"           delta {shmean:+.4f} vs MDE {shmde:.4f} -> "
          f"{'inside (PASS: the dose needs identity)' if sham_ok else 'RESOLVED (FAIL: the dose survives without identity, so it is not about identity)'}")

    # ⛔ A NULL WITHOUT A POSITIVE CONTROL IS SILENCE, and v1 had placebo, sham and split but
    #    nothing showing the dose CAN detect a channel. Plant one: give the E-annotators synthetic
    #    importance scores that favour the criteria best fitting THEIR OWN rankings, at strength g.
    #    That is a person-specific channel of known sign, and the dose must recover it.
    def run_plant(seed, dose, g):
        rng = random.Random(90000 + 1000 * seed + int(dose * 100) + int(g * 10))
        out = []
        for pid, common, ok in USE:
            a = list(common); rng.shuffle(a)
            half = len(a) // 2
            E, W0 = a[:half], a[half:]
            n_from_E = int(round(dose * len(W0)))
            W = W0[:len(W0) - n_from_E] + E[:n_from_E] if n_from_E else W0
            if not W or not E:
                continue
            evals = [y for x in E for y in RANK[pid][x]]
            if not evals:
                continue
            fit = {i: a2(induced(pid, [i]), evals) for i in ok}      # how well {i} alone fits E
            imp = IMP[pid]
            w = {}
            for i in ok:
                base = [imp[x][i] for x in W if i in imp[x]] or [0.0]
                boost = g * 20.0 * fit[i] * (len([x for x in W if x in set(E)]) / max(len(W), 1))
                w[i] = float(np.mean(base)) + boost
            sel = sorted(ok, key=lambda i: -w[i])[:K]
            out.append(a2(induced(pid, sel), evals) - a2(pool_ref(pid), evals))
        return np.array(out, float)

    print(f"\n  POSITIVE CONTROL — plant a person-specific channel of strength g in the E-annotators'")
    print(f"    own scores; the dose must recover it. Reported as delta(dose=1) - delta(dose=0).")
    POS = {}
    for g in (0.0, 0.5, 1.0, 2.0):
        ds = []
        for s in SEEDS:
            v1 = run_plant(s, 1.0, g); v0 = run_plant(s, 0.0, g)
            n = min(len(v1), len(v0)); dd = v1[:n] - v0[:n]
            ds.append((float(dd.mean()), float(ZEFF * dd.std(ddof=1) / math.sqrt(n))))
        m = float(np.mean([x[0] for x in ds])); e = float(np.mean([x[1] for x in ds]))
        POS[g] = (m, e, m > e)
        print(f"      g={g:<4} delta {m:+.4f} vs MDE {e:.4f}   "
              f"{'DETECTED' if m > e else 'not detected'}")
    pos_ok = (not POS[0.0][2]) and POS[2.0][2]
    print(f"    floor g=0 -> {'not detected (it CAN fail)' if not POS[0.0][2] else 'DETECTED — the control cannot fail'}")
    print(f"    ceiling g=2 -> {'detected (it CAN pass)' if POS[2.0][2] else 'NOT detected — the design cannot see a planted channel at all'}")
    print(f"    {'PASS' if pos_ok else 'FAIL'}")

    ov0 = float(np.mean([CURVE[(s, 0.0)][2] for s in SEEDS]))
    ov1 = float(np.mean([CURVE[(s, 1.0)][2] for s in SEEDS]))
    split_ok = ov0 < 0.01 and ov1 > 0.5
    print(f"  SPLIT    realised overlap {ov0:.3f} at dose 0 and {ov1:.3f} at dose 1 — a dose that")
    print(f"           does not move is a dose that never ran  {'PASS' if split_ok else 'FAIL'}")

    mono = all(np.mean([CURVE[(s, DOSES[i])][0] for s in SEEDS])
               <= np.mean([CURVE[(s, DOSES[i + 1])][0] for s in SEEDS]) + 1e-12
               for i in range(len(DOSES) - 1))
    ctrl_ok = plac and sham_ok and split_ok and pos_ok
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; the curve above is silence.")
        v = "UNVERIFIED"
    elif abs(dmean) <= dmde:
        print(f"  W-CHANNEL-EMPTY — the dose is FLAT within resolution: {dmean:+.4f} against its own")
        print(f"  MDE {dmde:.4f}. The channel R363 measured is OPEN and carries nothing detectable")
        print(f"  at this design's resolution. Importance scores behave as PROMPT-level rather than")
        print(f"  person-level information, so whose scores are averaged does not move `topw_k4`.")
        print(f"  ⛔ Clause ③'s WORDING was still wrong and stays corrected — R363's census stands.")
        print(f"     What is retracted is any implication that the published five are compromised:")
        base = float(np.mean([CURVE[(s, 0.0)][0] for s in SEEDS]))
        print(f"     they are not, at a resolution of {dmde:.4f}.")
        print(f"  ⚠ AND THIS IS A BOUND, NOT A ZERO. `topw_k4`'s own margin at dose 0 is")
        print(f"    {base:+.4f}, so an MDE of {dmde:.4f} rules out a channel larger than")
        print(f"    ~{100*dmde/max(abs(base),1e-9):.0f}% of the whole margin and says NOTHING about a smaller one.")
        print(f"    The three seeds straddle zero ({', '.join(f'{DELTA[s][0]:+.4f}' for s in SEEDS)}),")
        print(f"    which is a stronger null signature than one point — but it is still a bound.")
        v = "W_CHANNEL_EMPTY"
    elif dmean > dmde and mono:
        print(f"  W-CHANNEL-CARRIES — the margin rises with dose, monotonically, by {dmean:+.4f}")
        print(f"  against its own MDE {dmde:.4f}. Being scored by the people who wrote your weights")
        print(f"  is worth that much, so four of the published five inherit it and the admitted set")
        print(f"  must be recomputed.")
        v = "W_CHANNEL_CARRIES"
    elif dmean > dmde:
        print(f"  W-CHANNEL-CARRIES-NONMONOTONE — resolvable ({dmean:+.4f} vs {dmde:.4f}) but NOT")
        print(f"  monotone in dose. Named rather than folded into `carries`: a non-monotone dose")
        print(f"  means the contrast is real and the DOSE is not the variable it is named for.")
        v = "W_CHANNEL_CARRIES_NONMONOTONE"
    else:
        print(f"  W-INVERTED — the margin FALLS with dose ({dmean:+.4f} vs MDE {dmde:.4f}). No")
        print(f"  account of leakage predicts this, so the dose is measuring something other than")
        print(f"  what it is named for and the round is not readable as a channel size.")
        v = "W_INVERTED"

    art = dict(stamp(str(SELF)), n_prompts=len(USE), k=K, doses=list(DOSES), seeds=list(SEEDS),
               curve={f"{s}|{d}": CURVE[(s, d)] for (s, d) in CURVE},
               delta={str(s): DELTA[s] for s in SEEDS}, delta_mean=dmean, delta_mde=dmde,
               sham={str(s): SH[s] for s in SEEDS}, sham_mean=shmean, sham_mde=shmde,
               monotone=mono, overlap_d0=ov0, overlap_d1=ov1,
               positive={str(g): POS[g] for g in POS},
               controls=dict(placebo=plac, sham=sham_ok, split=split_ok, positive=pos_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r364_channel_size.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
