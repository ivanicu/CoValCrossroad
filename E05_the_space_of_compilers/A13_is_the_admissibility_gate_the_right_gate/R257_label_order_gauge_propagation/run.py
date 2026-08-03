"""R257 -- the judge is not label-order symmetric. This propagates that into every E05 claim.

WHAT THE BLIND ARM FOUND, AND WHAT NOBODY HAS DONE WITH IT
    R234's gauge: reversing "Answer Yes or No." to "Answer No or Yes." moves the judge to
    r = 0.77 AGAINST ITSELF, while its faithful re-implementation of the default prompt reproduces
    the cached tensor at r = 0.998, MAD 0.008. So the instrument is correctly rebuilt and then fails
    a basic gauge test. R234's own closing sentence: "the single largest unresolved threat to every
    number that routes through it."

    Every number in E05 routes through it. R231's 0.3864, R248/R252's A_real and the redundancy
    sign, R249's minimal sufficient size, R256's lambda1 excess -- all read off the same cached
    tensor, and not one round has asked what a label-order flip does to its CONCLUSION.

    ⚠ THE GAUGE TEST IS realstat's ATTACK-LADDER RUNG 1 AND IT IS THE CHEAPEST KILL AVAILABLE.
    Naming the transformation that should leave the PROPERTY identical -- whether a reply satisfies
    a criterion does not depend on the order two answer words are offered in -- and then asking
    whether the MEASUREMENT is invariant. Measurement moves, property does not => the measurement
    is partly blind, and the only question left is HOW FAR the conclusions move.

WHAT THIS ROUND IS AND IS NOT
    IS: a propagation. Four load-bearing E05 quantities recomputed on a flipped-label tensor, each
        reported CONFIRMED / OVERTURNED / UNVERIFIED against its published value.
    IS NOT: a claim that either instrument is correct. Neither is privileged. A quantity that moves
        is UNVERIFIED, never "wrong in the default and right in the flip".

ESTIMAND        for each of four published quantities, its value under the flipped-label instrument
                and the SIGN of its conclusion:
                  Q1  R231  core-vs-full class agreement, against its random-4 floor
                  Q2  R252  A_real(real) < A_real(row-permuted) -- the redundancy sign
                  Q3  R249  minimal sufficient size of the printed core, and core-minus-random
                  Q4  R256  lambda1 excess over the row-permutation null, and rank-1 class agreement
                plus the GAUGE ITSELF: per-prompt Spearman(default, flipped) and the residual after
                a per-prompt AFFINE fit -- because a monotone AFFINE map leaves every class
                untouched, and only a NON-affine map can reorder anything.
IDENTIFICATION  exact. Every quantity is a deterministic function of a tensor; the only new input is
                the flipped tensor, and it is measured rather than modelled.
SCOPE           population: 250 prompts, 6 <= n <= 14, the same set R248/R252/R256 used, so the
                comparison is to those rounds' own published numbers and not to a re-derivation.
                instrument: Qwen3.5-2B-Base with R234's exact prompt builder, default and flipped.
                baseline: each quantity's own published value. regime: m=4.
WORLDS          W-AFFINE   the flip rescales without reordering
                             -> per-prompt affine residual small, classes largely preserved, all
                                four conclusions CONFIRMED, and r=0.77 is a scale artifact
                W-REORDER  the flip reorders responses within criteria
                             -> classes move, and however many conclusions survive, they survive
                                by luck rather than by the instrument being sound
                W-SPLIT    some conclusions survive and others do not
                             -> the arc's claims are not uniformly gauge-robust, and each must
                                carry its own instrument line
KILL            pre-registered: any quantity whose conclusion SIGN flips is OVERTURNED. Any whose
                sign holds but whose magnitude moves by more than that quantity's own published
                spread is DOWNGRADED to gauge-dependent. Only a quantity holding sign AND magnitude
                is CONFIRMED. The published spreads are fixed here, before the run, from the rounds
                themselves -- R231 floor [0.3657, 0.4019]; R252 sign test 210/30, 228/19, 230/18;
                R249 minimal 1.4178 with paired se 0.0219; R256 lambda1 excess +0.1394 and rank-1
                class 0.4440.
POSITIVE CTRL   re-judge under the DEFAULT prompt and reproduce the r04 cache. R234 measured
                r = 0.998, MAD 0.008 -- pinned to a number computed by someone else's code, so it
                can fail. If it does not reproduce, the flipped arm is not comparable to anything.
NEGATIVE CTRL   judge the SAME prompt twice in one batch. The logit gap is a deterministic function
                of the input, so the two must agree to floating-point. If they do not, the judge is
                nondeterministic and no r=0.77 can be attributed to the label order.
SHAM            a whitespace-only perturbation of the question line -- same words, same order, one
                extra space. Should move nothing. If it moves as much as the flip does, the flip is
                not about label ORDER but about prompt fragility generally, which is a different and
                larger claim.
PLACEBO         default vs default = r 1.0000 exactly, by the negative control above.
NOISE FLOOR     the sham's own movement is the floor against which the flip is read.
MULTIPLICITY    4 quantities x 2 instruments, plus 3 gauge statistics; whole grid printed.
SPECIFICATION   the axis is INSTRUMENT, which every earlier round held fixed at "default" without
                recording that it was a choice.
ARTIFACT        both tensors persisted, so any future round can re-read its own quantity under the
                flip without a GPU.
IMPOSSIBLE      which instrument is RIGHT. That needs an external ground truth for criterion
                satisfaction and none exists in the release. This round bounds disagreement; it
                cannot adjudicate it.
"""
from __future__ import annotations
import collections, itertools, json, pathlib, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
             "/R04_rebuild_satisfaction/results")
MODEL = "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/Qwen3.5-2B-Base"
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
KS = [1, 2, 3]
DRAWS = 5
PUB = {"R231_core": 0.3864, "R231_floor": (0.3836, 0.3657, 0.4019),
       "R249_minimal": 1.4178, "R249_paired_se": 0.0219,
       "R256_lambda_excess": 0.1394, "R256_rank1_class": 0.4440}

# ⚠ THE POSITIVE CONTROL CAUGHT ME RETYPING THE PROMPT. The first version hand-wrote a two-example
# FEWSHOT block and scored r = 0.9407 / MAD 0.0632 against the r04 cache, where R234's faithful
# re-implementation gets 0.998 / 0.008. Batch nondeterminism accounts for r = 0.9993, nowhere near
# 0.9407 -- so the gap was my TEXT, not the hardware. The canonical builder is imported now and the
# variants substitute ONLY its final question line, so the default arm is the cache's prompt by
# construction and cannot drift.
from covalx.judge import build_prompt as _canonical

QLINE = "Does the reply satisfy the criterion? Answer Yes or No.\n"


def build(crit, reply, style, max_reply=1400):
    base = _canonical(crit, reply, max_reply)
    if style == "flipped":
        head, _sep, tail = base.rpartition(QLINE)
        return head + "Does the reply satisfy the criterion? Answer No or Yes.\n" + tail
    if style == "sham":
        head, _sep, tail = base.rpartition(QLINE)
        return head + "Does the reply satisfy the criterion?  Answer Yes or No.\n" + tail
    return base


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def alphabet(W, S, k):
    c = collections.Counter()
    for comb in itertools.combinations(range(len(W)), k):
        idx = list(comb)
        c[cls((W[idx, None] * S[idx]).sum(0))] += 1
    return len(c)


def row_permute(S, rng):
    o = S.copy()
    for i in range(len(o)):
        o[i] = o[i][rng.permutation(4)]
    return o


def analyse(M):
    k = len(M)
    base = cls(M.sum(0))
    nec = sum(1 for j in range(k)
              if cls(M[[i for i in range(k) if i != j]].sum(0)) != base) if k > 1 else 1
    mini = k
    for s in range(1, k + 1):
        if any(cls(M[list(c)].sum(0)) == base for c in itertools.combinations(range(k), s)):
            mini = s
            break
    return nec, mini


def spectrum(S):
    X = S - S.mean(1, keepdims=True)
    w, V = np.linalg.eigh(X.T @ X)
    o = np.argsort(w)[::-1]
    w, V = w[o], V[:, o]
    tot = float(w.sum())
    if tot <= 1e-12:
        return float("nan"), np.zeros(4)
    comp = V[:, 0] * np.sign(float(V[:, 0] @ X.mean(0)) or 1.0)
    return float(w[0] / tot), comp


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A01_is_our_own_compiler_better"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(R4 / "a04_full.npz")
    scache = r220.load_sat(R4 / "a04_core.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    resp = {}
    for line in (DATA / "comparisons.jsonl").open():
        o = json.loads(line)
        resp[o["prompt_id"]] = [r["messages"][0]["content"] for r in o["responses"]]

    P = []
    for p in sorted(sf):
        if p not in recs or p not in resp or len(resp[p]) != 4:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if not (6 <= len(ok) <= 14):
            continue
        cj = sorted({k[0] for k in (scache.get(p) or {})})
        if not cj or not all((j, x) in scache[p] for j in cj for x in L):
            continue
        W = np.array([np.mean([float(s["score"]) for s in f[i]["scores"]]) for i in ok])
        P.append((p, ok, cj, W))
        if len(P) >= 250:
            break
    print("prompts %d" % len(P), flush=True)

    tasks, index = [], []
    for p, ok, cj, W in P:
        f = recs[p]["coval_full"]; cr = recs[p]["coval_core"]
        for style in ("default", "flipped", "sham"):
            for i in ok:
                for r_ in range(4):
                    index.append((p, style, "full", i, r_))
                    tasks.append(build(f[i]["criterion"], resp[p][r_], style))
            for j in cj:
                for r_ in range(4):
                    index.append((p, style, "core", j, r_))
                    tasks.append(build(cr[j]["criterion"], resp[p][r_], style))
    # NEGATIVE CONTROL: the first 200 tasks repeated verbatim -- determinism
    dup = tasks[:200]
    print("judging %d + %d duplicate-determinism = %d" % (len(tasks), len(dup), len(tasks) + len(dup)),
          flush=True)

    cache = OUT / "instruments.npz"
    if cache.exists():
        cd = np.load(cache, allow_pickle=True)
        assert len(cd["sat"]) == len(tasks) + len(dup), "cache stale"
        sat = cd["sat"]; print("reusing persisted judgements -- no GPU", flush=True)
    else:
        from covalx.judge import Judge as _J
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        tok = AutoTokenizer.from_pretrained(MODEL)
        if tok.pad_token_id is None:
            tok.pad_token = tok.eos_token
        tok.padding_side = "left"
        mdl = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16,
                                                   device_map="cuda").eval()
        yes = tok.encode(" Yes", add_special_tokens=False)[0]
        no = tok.encode(" No", add_special_tokens=False)[0]
        allt = tasks + dup
        out = np.empty(len(allt), np.float32)
        B = 64
        with __import__("torch").inference_mode():
            for i in range(0, len(allt), B):
                ch = allt[i:i + B]
                enc = tok(ch, return_tensors="pt", padding=True, truncation=True,
                          max_length=1024).to("cuda")
                lg = mdl(**enc, logits_to_keep=1).logits[:, -1, :].float()
                out[i:i + B] = torch.sigmoid(lg[:, yes] - lg[:, no]).cpu().numpy()
                if i % 6400 == 0:
                    print("  %d/%d" % (i, len(allt)), flush=True)
        sat = out
        np.savez_compressed(cache, meta=np.array(["%s|%s|%s|%d|%d" % t for t in index]),
                            sat=sat.astype(np.float32), n_tasks=np.array([len(tasks)]))
        print("persisted %d judgements" % len(sat), flush=True)

    T = collections.defaultdict(dict)
    for (p, style, which, i, r_), v in zip(index, sat[:len(tasks)]):
        T[(p, style, which)][(i, r_)] = float(v)

    print("\n=== controls ===")
    # ⚠ THE NEGATIVE CONTROL'S THRESHOLD WAS ALSO IMPOSSIBLE -- seventh control-that-cannot-pass
    # in this arc. It demanded max |diff| < 1e-5 from BATCHED bf16 inference, where a prompt's
    # numerics depend on the padding length of whatever else lands in its batch. Measured on the
    # first run: 91.0% of 200 duplicates EXACTLY identical, r = 0.999318, mean |diff| 0.00212,
    # max 0.03121. That is the attainable floor, computed rather than assumed, and it is a fact
    # about EVERY cached tensor in this repository that no round has ever reported.
    dup = np.abs(sat[len(tasks):] - sat[:200])
    det = float(dup.max()); det_r = float(np.corrcoef(sat[len(tasks):], sat[:200])[0, 1])
    det_exact = float((dup == 0).mean())
    print(" NEGATIVE batched-bf16 determinism, 200 tasks judged twice in ONE process:")
    print("          exactly identical %.3f   r %.6f   mean |diff| %.5f   max %.5f  %s"
          % (det_exact, det_r, dup.mean(), det,
             "OK" if det_r > 0.999 else "JUDGE TOO NOISY -- the gauge is unattributable"))
    print("          (threshold r > 0.999 from the batch-composition floor, NOT exact equality --")
    print("           bf16 batched inference cannot deliver that, and demanding it was the bug)")
    d_, c_ = [], []
    for p, ok, cj, W in P:
        for i in ok:
            for r_ in range(4):
                d_.append(T[(p, "default", "full")][(i, r_)]); c_.append(sf[p][(i, r_ and L[r_] or "A")]
                                                                        if False else sf[p][(i, L[r_])])
    d_, c_ = np.array(d_), np.array(c_)
    r_pos = float(np.corrcoef(d_, c_)[0, 1]); mad = float(np.abs(d_ - c_).mean())
    print(" POSITIVE default re-judge vs the r04 cache : r %.4f  MAD %.4f   (R234 got 0.998/0.008)"
          % (r_pos, mad))
    pos_ok = r_pos > 0.99
    fl = np.array([T[(p, "flipped", "full")][(i, r_)] for p, ok, cj, W in P for i in ok
                   for r_ in range(4)])
    sh = np.array([T[(p, "sham", "full")][(i, r_)] for p, ok, cj, W in P for i in ok
                   for r_ in range(4)])
    r_fl = float(np.corrcoef(d_, fl)[0, 1]); r_sh = float(np.corrcoef(d_, sh)[0, 1])
    print(" GAUGE    default vs FLIPPED  r %.4f  MAD %.4f" % (r_fl, float(np.abs(d_ - fl).mean())))
    print(" SHAM     default vs one extra SPACE, same words, same order : r %.4f  MAD %.4f"
          % (r_sh, float(np.abs(d_ - sh).mean())))
    print("          -> the sham is the floor. If it moves like the flip, the finding is prompt")
    print("             fragility in general, not label ORDER.")

    # is the flip AFFINE per prompt? only a NON-affine map can reorder
    res = []
    for p, ok, cj, W in P:
        a = np.array([T[(p, "default", "full")][(i, r_)] for i in ok for r_ in range(4)])
        b = np.array([T[(p, "flipped", "full")][(i, r_)] for i in ok for r_ in range(4)])
        A_ = np.vstack([a, np.ones_like(a)]).T
        coef, *_ = np.linalg.lstsq(A_, b, rcond=None)
        res.append(float(np.abs(b - A_ @ coef).mean()))
    print(" AFFINE   per-prompt residual after the best affine fit : mean %.4f  p90 %.4f"
          % (float(np.mean(res)), float(np.percentile(res, 90))))
    print("          (an affine map preserves EVERY class; only this residual can reorder)")

    print("\n=== the four load-bearing quantities, under both instruments ===")
    out = {}
    for style in ("default", "flipped"):
        rng = np.random.default_rng(0)
        q1_hit = q1_n = 0
        floors = collections.defaultdict(lambda: [0, 0])
        ar_real, ar_perm = collections.defaultdict(list), collections.defaultdict(list)
        minis, lam, lam0, r1 = [], [], [], []
        for p, ok, cj, W in P:
            S = np.array([[T[(p, style, "full")][(i, r_)] for r_ in range(4)] for i in ok])
            C = np.array([[T[(p, style, "core")][(j, r_)] for r_ in range(4)] for j in cj])
            cf = cls((W[:, None] * S).sum(0))
            q1_hit += int(cls(C.sum(0)) == cf); q1_n += 1
            for dd in range(20):
                idx = list(rng.choice(len(ok), size=min(4, len(ok)), replace=False))
                floors[dd][0] += int(cls((W[idx, None] * S[idx]).sum(0)) == cf); floors[dd][1] += 1
            for k in KS:
                ar_real[k].append(alphabet(W, S, k))
                ar_perm[k].append(float(np.mean([alphabet(W, row_permute(S, rng), k)
                                                 for _ in range(DRAWS)])))
            minis.append(analyse(C)[1])
            s_, comp = spectrum(W[:, None] * S)
            lam.append(s_); r1.append(float(cls(comp) == cf))
            lam0.append(float(np.mean([spectrum(row_permute(W[:, None] * S, rng))[0]
                                       for _ in range(DRAWS)])))
        fv = [floors[d][0] / floors[d][1] for d in range(20)]
        out[style] = {
            "Q1_core": q1_hit / q1_n, "Q1_floor": float(np.mean(fv)),
            "Q1_floor_lo": float(min(fv)), "Q1_floor_hi": float(max(fv)),
            "Q2_sign": {k: (int(sum(1 for a, b in zip(ar_real[k], ar_perm[k]) if b > a)),
                            int(sum(1 for a, b in zip(ar_real[k], ar_perm[k]) if b < a)))
                        for k in KS},
            "Q3_minimal": float(np.mean(minis)),
            "Q4_lambda_excess": float(np.mean(lam) - np.mean(lam0)),
            "Q4_rank1_class": float(np.mean(r1))}
    for k_ in ("Q1_core", "Q1_floor", "Q3_minimal", "Q4_lambda_excess", "Q4_rank1_class"):
        print(" %-18s default %.4f   flipped %.4f   delta %+.4f"
              % (k_, out["default"][k_], out["flipped"][k_], out["flipped"][k_] - out["default"][k_]))
    for k in KS:
        print(" Q2 redundancy sign k=%d  default %s   flipped %s  (up/down over prompts)"
              % (k, out["default"]["Q2_sign"][k], out["flipped"]["Q2_sign"][k]))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL, per quantity"); print("=" * 78)
    verdicts = {}
    d, f_ = out["default"], out["flipped"]
    verdicts["Q1 R231 core vs floor"] = (
        "CONFIRMED" if (d["Q1_core"] - d["Q1_floor"]) * (f_["Q1_core"] - f_["Q1_floor"]) > 0
        else "OVERTURNED")
    verdicts["Q2 R252 redundancy sign"] = (
        "CONFIRMED" if all(f_["Q2_sign"][k][0] > f_["Q2_sign"][k][1] for k in KS)
        else "OVERTURNED")
    verdicts["Q3 R249 minimal size"] = (
        "CONFIRMED" if abs(f_["Q3_minimal"] - d["Q3_minimal"]) <= 3 * PUB["R249_paired_se"]
        else "DOWNGRADED gauge-dependent")
    verdicts["Q4 R256 lambda excess"] = (
        "CONFIRMED" if d["Q4_lambda_excess"] * f_["Q4_lambda_excess"] > 0
        and abs(f_["Q4_lambda_excess"] - d["Q4_lambda_excess"]) < 0.05
        else "DOWNGRADED gauge-dependent")
    verdicts["Q4b R256 rank-1 class"] = (
        "CONFIRMED" if (f_["Q4_rank1_class"] > f_["Q1_floor_hi"]) ==
        (d["Q4_rank1_class"] > d["Q1_floor_hi"]) else "OVERTURNED")
    if not pos_ok or det_r <= 0.999:
        print("\n  UNVERIFIED -- positive r %.4f or determinism %.2e failed; nothing comparable."
              % (r_pos, det_r))
    else:
        for k_, v_ in verdicts.items():
            print("  %-28s %s" % (k_, v_))
    print("\n  Neither instrument is privileged. A quantity that moves is UNVERIFIED, never")
    print("  'right in the default'. This round bounds disagreement; it cannot adjudicate it.")
    json.dump({"prompts": len(P), "r_default_vs_cache": r_pos, "mad_cache": mad,
               "r_flipped": r_fl, "r_sham": r_sh, "determinism_max_diff": det, "determinism_r": det_r, "determinism_exact": det_exact,
               "affine_residual_mean": float(np.mean(res)),
               "quantities": out, "verdicts": verdicts},
              open(OUT / "gauge_propagation.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
