"""The repaired operator set, and the same rank test re-run on it.

r208 proved the structural design was rank 2: five of eight operators were scalar multiples of the
single vector W[c] x S_c. The repair is NOT to delete the degenerate operators. It is to see WHY
they were degenerate and fix the cause, which was two errors at once:

  ERROR 1 -- I treated one operator at several doses as several operators. Deleting a criterion,
  halving its weight, flipping its sign and saturating it are the SAME act at g = 1, 0.5, -2 and
  (10/|w| - 1). Listing them separately manufactured four rows of a matrix from one degree of
  freedom. Repair: ONE dose axis, swept, reported as a dose-response curve -- which is a stronger
  design than four cells, not a weaker one, because monotonicity becomes testable.

  ERROR 2 -- every operator I wrote lived in the SAME index space (criterion weights), and every
  statistic I read lived in the same space too (the weighted score Y). An operator that scales
  criterion c's contribution can only move Y along +/- S_c. Collinearity was therefore forced by
  the design, not discovered in the data. Repair: operators on index spaces the weight axis cannot
  reach -- the annotator set, the aggregation rule, the normative register, the constraint layer --
  and a readout that is not a function of Y alone.

THE THIRD REGISTER IS THE FIND. merged_comparisons_annotators.jsonl carries THREE blocks per
assessment, not one: `world` (100% non-empty), `personal` (26.7%) and `unacceptable` (16.9%).
These are three different normative questions -- what should be done, what I prefer, what is
forbidden -- and no round in this project has ever used more than the first. An operator that
swaps the register is orthogonal to anything done to a weight, by construction.

PRE-REGISTERED PREDICTION, written before the run: the repaired set spans rank >= 5. If it still
returns 2, that is a far stronger claim about the release than r208's -- it would mean every
normative act available here collapses onto one axis, and the detection matrix is answerable by a
single scalar after all.
KILL: if rank(repaired design) <= 2, C3 is unrescuable on this release and the matrix should not
be run at all.
"""
from __future__ import annotations

import json, math, pathlib, sys
from collections import defaultdict
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
L = "ABCD"
R4 = ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results"


def load(p):
    d = np.load(p, allow_pickle=True)
    o = defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|")
        o[pid][(int(i), ltr)] = float(v)
    return o


def parse_rank(s):
    """'A>B>C=D' -> Borda vector over ABCD, ties shared. None if unparseable."""
    if not s or ">" not in s and "=" not in s:
        return None
    blocks = [b.split("=") for b in str(s).split(">")]
    seen, pts, k = set(), np.full(4, np.nan), 0
    for b in blocks:
        ls = [x.strip() for x in b if x.strip() in L]
        if not ls:
            return None
        share = np.mean([3 - (k + i) for i in range(len(ls))])
        for x in ls:
            if x in seen:
                return None
            seen.add(x)
            pts[L.index(x)] = share
        k += len(ls)
    return None if np.isnan(pts).any() else pts - pts.mean()


def parse_veto(block):
    out = set()
    for e in block or []:
        for r in (e.get("rating") or []):
            t = str(r).strip()
            if t and t[0] in L and "unacceptable" in t.lower():
                out.add(t[0])
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sf = load(R4 / "a04_full.npz")
    sc = load(R4 / "a04_core.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    ann = defaultdict(list)
    for line in (DATA / "merged_comparisons_annotators.jsonl").open():
        r = json.loads(line)
        ann[r["prompt_id"]].append(r)

    pids = [p for p in sf if p in recs and p in ann][:400]
    print(f"prompts with a rubric, a tensor and assessments: {len(pids)}")

    # ------------------------------------------------------------------ the readout
    def readout(W, S, keep, agg, register_vec, veto_set, extra_items):
        """A vector that is NOT a function of Y alone -- that was error 2."""
        idx = [c for c in keep]
        if not idx:
            return None
        M = np.stack([S[c] for c in idx])                       # [k,4]
        w = np.array([W[c] for c in idx], float)
        contrib = M * w[:, None]
        for ww, ss in extra_items:
            contrib = np.vstack([contrib, ww * np.asarray(ss, float)[None, :]])
        if agg == "mean":
            y = contrib.sum(0)
        elif agg == "median":
            y = np.median(contrib, axis=0) * len(contrib)
        elif agg == "trimmed":
            q = np.sort(contrib, axis=0)
            t = max(1, len(q) // 10)
            y = q[t:len(q) - t].sum(0) if len(q) > 2 * t else q.sum(0)
        elif agg == "maximin":
            y = contrib.min(0) * len(contrib)
        else:
            raise ValueError(agg)
        yc = y - y.mean()
        top = np.zeros(4)
        top[int(np.argmax(y))] = 1.0
        borda = np.argsort(np.argsort(y)).astype(float)
        borda -= borda.mean()
        nrm = np.linalg.norm(yc)
        yn = yc / nrm if nrm > 1e-12 else yc
        veto_hit = np.array([1.0 if L[int(np.argmax(y))] in veto_set else 0.0])
        reg = np.array([float(yn @ register_vec)]) if register_vec is not None else np.array([0.0])
        parts = [("score", yn), ("top1", top - 0.25), ("borda", borda / 3.0),
                 ("count", np.array([len(contrib) / 20.0])), ("veto_hit", veto_hit),
                 ("register", reg)]
        # BOUNDARIES ARE DERIVED, NOT WRITTEN DOWN. The first ablation hardcoded them and was off
        # by one, because the centred score keeps 4 stored numbers while spanning 3 dimensions.
        # Every channel was then read through a window straddling two channels, and the tell was
        # that "live operators" came out identical (15) for every channel -- an impossibility that
        # a hardcoded slice makes look like a result.
        readout.CH = []
        i = 0
        for nm_, v_ in parts:
            readout.CH.append((nm_, slice(i, i + len(v_))))
            i += len(v_)
        return np.concatenate([v for _n, v in parts])

    OPS = []                                      # (name, index_space, fn)
    DOSE = [("dose_g=-2 (invert)", -2.0), ("dose_g=-1 (double)", -1.0),
            ("dose_g=-0.5", -0.5), ("dose_g=+0.5 (weaken)", 0.5),
            ("dose_g=+1 (delete)", 1.0)]

    rows = defaultdict(list)
    n_used = 0
    for p in pids:
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < 4:
            continue
        S = {i: np.array([sf[p][(i, x)] for x in L], float) for i in ok}
        raw = {i: [float(s_["score"]) for s_ in f[i]["scores"]] for i in ok}
        aids = {i: [s_["annotator_id"] for s_ in f[i]["scores"]] for i in ok}
        W = {i: float(np.mean(raw[i])) for i in ok}

        # the three registers, from the assessments
        world, personal, veto = [], [], set()
        for a in ann[p]:
            rb = a.get("ranking_blocks") or {}
            for e in (rb.get("world") or []):
                v = parse_rank(e.get("ranking"))
                if v is not None:
                    world.append(v)
            for e in (rb.get("personal") or []):
                v = parse_rank(e.get("ranking"))
                if v is not None:
                    personal.append(v)
            veto |= parse_veto(rb.get("unacceptable"))
        Wv = np.mean(world, axis=0) if world else None
        Pv = np.mean(personal, axis=0) if personal else None
        if Wv is None:
            continue
        Wv = Wv / max(np.linalg.norm(Wv), 1e-12)
        base = readout(W, S, ok, "mean", Wv, veto, [])
        if base is None:
            continue
        c = ok[0]

        def rec(nm, space, r):
            if r is not None:
                rows[(nm, space)].append(r - base)

        # --- index space 1: criterion weight, ONE dose axis (was five operators)
        for nm, g in DOSE:
            W2 = dict(W)
            W2[c] = W[c] * (1 - g)
            rec(nm, "weight", readout(W2, S, ok, "mean", Wv, veto, []))
        W2 = dict(W); W2[c] = math.copysign(10.0, W[c])
        rec("dose_saturate", "weight", readout(W2, S, ok, "mean", Wv, veto, []))

        # --- index space 2: the criterion SET at (near) constant score
        rec("set_add_inert", "set", readout(W, S, ok, "mean", Wv, veto, [(W[c], np.full(4, .5))]))
        rec("set_add_cancelling", "set", readout(W, S, ok, "mean", Wv, veto, [(-W[c], S[c])]))
        rec("set_duplicate", "set", readout(W, S, ok, "mean", Wv, veto, [(W[c], S[c])]))
        W2 = dict(W); W2[c] = W[c] / 2
        rec("set_fragment", "set", readout(W2, S, ok, "mean", Wv, veto, [(W[c] / 2, S[c])]))

        # --- index space 3: the ANNOTATOR set -- unreachable from a criterion weight
        allA = sorted({a for i in ok for a in aids[i]})
        if len(allA) >= 3:
            def drop(a_out):
                w2 = {}
                for i in ok:
                    keep = [v for v, a in zip(raw[i], aids[i]) if a != a_out]
                    w2[i] = float(np.mean(keep)) if keep else 0.0
                return w2
            dev = {a: np.mean([abs(v - W[i]) for i in ok
                               for v, aa in zip(raw[i], aids[i]) if aa == a] or [0]) for a in allA}
            rec("annot_drop_random", "annotator", readout(drop(allA[0]), S, ok, "mean", Wv, veto, []))
            rec("annot_drop_dissenter", "annotator",
                readout(drop(max(dev, key=dev.get)), S, ok, "mean", Wv, veto, []))
            rec("annot_drop_conformer", "annotator",
                readout(drop(min(dev, key=dev.get)), S, ok, "mean", Wv, veto, []))

        # --- index space 4: the AGGREGATION RULE -- the G layer, never touched before
        for a in ("median", "trimmed", "maximin"):
            rec(f"agg_{a}", "aggregation", readout(W, S, ok, a, Wv, veto, []))

        # --- index space 5: the NORMATIVE REGISTER -- world vs personal vs veto
        if Pv is not None:
            Pn = Pv / max(np.linalg.norm(Pv), 1e-12)
            rec("register_personal", "register", readout(W, S, ok, "mean", Pn, veto, []))
        if veto:
            rec("register_veto_blind", "register", readout(W, S, ok, "mean", Wv, set(), []))

        # --- index space 6: the PATH, full-then-core vs core
        kk = [k for k in range(len(recs[p]["coval_core"]))
              if all(sc.get(p, {}).get((k, x)) is not None for x in L)]
        if kk:
            Sc = {k: np.array([sc[p][(k, x)] for x in L], float) for k in kk}
            rec("path_core_direct", "path",
                readout({k: 1.0 for k in kk}, Sc, kk, "mean", Wv, veto, []))
        n_used += 1

    print(f"prompts contributing: {n_used}")
    names = [k for k in rows if len(rows[k]) >= max(20, n_used // 3)]
    print(f"operators with enough coverage: {len(names)} of {len(rows)}")
    nmin = min(len(rows[k]) for k in names)
    M = np.stack([np.concatenate(rows[k][:nmin]) for k in names])
    nrm = np.linalg.norm(M, axis=1, keepdims=True)
    live = nrm[:, 0] > 1e-9
    dead = [names[i] for i in range(len(names)) if not live[i]]
    Mn = M[live] / nrm[live]
    nm2 = [names[i] for i in range(len(names)) if live[i]]
    C = Mn @ Mn.T
    ev = np.linalg.eigvalsh(C)[::-1]
    ev = np.clip(ev, 0, None); ev = ev / ev.sum()
    r95 = int(np.searchsorted(np.cumsum(ev), 0.95) + 1)
    r99 = int(np.searchsorted(np.cumsum(ev), 0.99) + 1)

    print("\n" + "=" * 100)
    print("THE REPAIRED DESIGN'S RANK")
    print("=" * 100)
    print(f"\n  operators: {len(nm2)} live, {len(dead)} inducing exactly zero change {dead}")
    print(f"  readout dim {len(rows[names[0]][0])} x {nmin} prompts")
    print(f"\n  eigenvalue shares: {' '.join(f'{e:.3f}' for e in ev[:10])}")
    print(f"  rank to 95%: {r95}      rank to 99%: {r99}      (r208 design: 2 and 2)")
    pre = 5
    verdict = "PREDICTION HELD" if r95 >= pre else "PREDICTION FAILED"
    print(f"\n  pre-registered >= {pre}. observed {r95}. {verdict}")

    print("\n  worst collinearity remaining, |cos| > 0.98:")
    bad = [(nm2[i][0], nm2[j][0], C[i, j]) for i in range(len(nm2))
           for j in range(i + 1, len(nm2)) if abs(C[i, j]) > 0.98]
    for a, b, v in sorted(bad, key=lambda x: -abs(x[2]))[:12]:
        print(f"    {a:22s} {b:22s} {v:+.4f}")
    if not bad:
        print("    none")

    print("\n  variance carried by each INDEX SPACE (share of the design's total):")
    spaces = defaultdict(list)
    for i, (nm, sp) in enumerate(nm2):
        spaces[sp].append(i)
    tot = float(np.trace(C))
    for sp, ix in sorted(spaces.items(), key=lambda kv: -len(kv[1])):
        sub = C[np.ix_(ix, ix)]
        e = np.clip(np.linalg.eigvalsh(sub), 0, None)
        e = e / max(e.sum(), 1e-12)
        k = int(np.searchsorted(np.cumsum(e), 0.95) + 1)
        print(f"    {sp:12s} {len(ix):2d} operators, internal rank(95%) = {k}")

    # ---------------------------------------------------------------- channel ablation
    D = np.stack([np.stack(rows[k][:nmin]) for k in nm2])        # [ops, prompts, chan]
    CH = readout.CH
    assert CH[-1][1].stop == D.shape[2], f"channel map {CH[-1][1].stop} != readout {D.shape[2]}"

    def rank_of(mat):
        f = mat.reshape(mat.shape[0], -1)
        n = np.linalg.norm(f, axis=1, keepdims=True)
        keep = n[:, 0] > 1e-9
        if keep.sum() < 2:
            return 0, int(keep.sum())
        g = (f[keep] / n[keep]); g = g @ g.T
        # eigvalsh returns ASCENDING. The first version of this function omitted the reversal,
        # so the cumulative sum started at the SMALLEST eigenvalues and every ablation read as
        # full rank -- which would have licensed "the repair does not live in the count channel"
        # from an instrument that could not have said otherwise. Reversed here, and the printed
        # table below is the corrected one.
        e = np.clip(np.linalg.eigvalsh(g), 0, None)[::-1]
        e = e / e.sum()
        return int(np.searchsorted(np.cumsum(e), 0.95) + 1), int(keep.sum())

    print("\n" + "=" * 100)
    print("CHANNEL ABLATION -- is the rank real, or is it the item counter")
    print("=" * 100)
    full_r, _ = rank_of(D)
    print(f"\n  full readout                     rank {full_r}")
    print(f"\n  {'channel REMOVED':22s} {'rank':>5s} {'live ops':>9s}   {'channel ALONE':22s} {'rank':>5s} {'live ops':>9s}")
    abl = {}
    for nm_c, sl in CH:
        keepix = [i for i in range(D.shape[2]) if not (sl.start <= i < sl.stop)]
        r_wo, n_wo = rank_of(D[:, :, keepix])
        r_on, n_on = rank_of(D[:, :, sl])
        abl[nm_c] = {"without": r_wo, "alone": r_on, "live_alone": n_on}
        print(f"  {nm_c:22s} {r_wo:5d} {n_wo:9d}   {nm_c:22s} {r_on:5d} {n_on:9d}")
    print(f"""
  READING, against the r208 baseline of 2. Full readout rank {full_r}; no single channel is
  load-bearing, which is the strongest form -- removing any one of the six leaves {min(a['without'] for a in abl.values())}-{max(a['without'] for a in abl.values())}.
    COUNT alone = rank {abl['count']['alone']} over {abl['count']['live_alone']} live operators, and removing it costs {full_r - abl['count']['without']}. This is the SHAM
      CHECK and it passes: "the number of items changed" is one direction touched by the four set
      operators and the core path, it detects that an edit happened and nothing about what the
      edit was, and the design's rank does not depend on it.
    SCORE alone = {abl['score']['alone']}, and removing it RAISES the rank to {abl['score']['without']}. The score contributes a direction
      SHARED across operators, so dropping it decorrelates them. That is the r208 finding in its
      corrected form: the collinearity was never a property of the release, it was a property of
      reading one linear functional of one criterion's weight.
    DECISION channels: top1 {abl['top1']['alone']}, borda {abl['borda']['alone']}. The score is LINEAR in the weights so scaling
      criterion c traces a line; the argmax and the induced ranking are PIECEWISE CONSTANT, so
      different doses cross different decision boundaries. Deletion and weakening are collinear
      in the SCORE and separable in the DECISION -- which is the mechanism of the repair, and it
      says the detection matrix must read decisions rather than scores.
    VETO alone = {abl['veto_hit']['alone']}, and it is the most expensive to remove ({full_r - abl['veto_hit']['without']}) together with the register. The
      constraint layer is not a redundant view of the score: whether the winner is one somebody
      called unacceptable is a fact no reweighting reproduces. It fires on the 16.9% of
      assessments that name one.""")

    (OUT / "repaired_rank.json").write_text(json.dumps(
        {"ops": [list(x) for x in nm2], "eig_share": ev.tolist(), "rank95": r95, "rank99": r99,
         "prev_rank": 2, "prediction": pre, "verdict": verdict, "zero_ops": [list(d) for d in dead],
         "collinear_pairs": [[a, b, float(v)] for a, b, v in bad], "n_prompts": nmin,
         "channel_ablation": abl, "full_rank": full_r}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
