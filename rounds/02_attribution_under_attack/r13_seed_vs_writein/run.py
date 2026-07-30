"""r13 -- Seed criteria vs write-in criteria: who carries the advantage?

r12 showed the real rubric's edge over an unrelated rubric does not survive on
responses its authors never saw. Two readings remain: the criteria encode facts
about those four responses (they were written after reading them), or the gold
model simply fails out of distribution.

Seed criteria were prepared alongside candidate generation; write-ins were
authored after the annotator read all four. So the released corpus already
contains the experiment: split the rubric by provenance and measure attribution
separately.

Provenance: the release does not FLAG seed vs write-in, so this splits on rater
count -- and r48 shows that split is an IDENTIFICATION rather than a heuristic.
The two classes are separated by a structural gap (18 of 15,248 criteria lie
between them; ZERO are ambiguous under the per-prompt rule below), and the
many-rated class is capped at exactly 6 per prompt with 728/986 prompts at the
cap -- the signature of a fixed set pre-populated for every participant, which
is what DATASET_CARD.md:357 documents as 'pre-seeded'.
Seeds were shown to every rater for a prompt, write-ins to nobody, so rating
count separates them cleanly -- the visibility distribution is perfectly bimodal
(9,684 items with one score, 5,564 rated by at least half, nothing between).
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = str(_HERE.parents[2])
_RES = str(_HERE / "results")
sys.path.insert(0, _ROOT)
from covalx import LABELS, human_pairs, load_join  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparisons", type=Path, default=Path(_ROOT) / "data/comparisons.jsonl")
    ap.add_argument("--rubrics", type=Path, default=Path(_ROOT) / "data/conversation_rubrics.jsonl")
    ap.add_argument("--sat", type=Path,
                    default=Path(_ROOT) / "rounds/01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz")
    ap.add_argument("--out", type=Path, default=Path(_RES) / "r13_seed_vs_writein.json")
    ap.add_argument("--boot", type=int, default=4000)
    ap.add_argument("--with-shuffled", action="store_true",
                    help="judge the donor's criteria against THIS prompt's responses, "
                         "which the saved matrix cannot supply")
    ap.add_argument("--prompts", type=int, default=250)
    a = ap.parse_args()

    z = np.load(a.sat, allow_pickle=True)
    lut = {}
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = str(m).split("|")
        lut.setdefault((pid, int(ci)), {})[lab] = float(s)

    joined = load_join(a.comparisons, a.rubrics)
    rng = np.random.default_rng(20260727)
    prompts = [p for p, _, _ in joined]
    donor = {p: prompts[(i + 1 + rng.integers(0, len(prompts) - 1)) % len(prompts)]
             for i, p in enumerate(prompts)}

    # provenance-split criterion index per prompt
    crit = {}
    for pid, comp, rub in joined:
        items = rub.get("coval_full") or []
        raters = {s["annotator_id"] for it in items for s in it.get("scores") or []}
        thr = max(2, (len(raters) + 1) // 2)
        seed, writein, ci = [], [], 0
        for it in items:
            sc = it.get("scores") or []
            if sc:
                (seed if len(sc) >= thr else writein).append(ci)
            ci += 1
        crit[pid] = {"seed": seed, "writein": writein}

    pairs = {pid: human_pairs(comp["metadata"]["assessments"]) for pid, comp, _ in joined}

    def agree(pid, idx_source_pid, which):
        """score this prompt's responses using `which` criteria taken from idx_source_pid"""
        idx = crit.get(idx_source_pid, {}).get(which, [])
        if not idx or not pairs.get(pid):
            return None
        score = {}
        for lab in LABELS:
            v = [lut[(idx_source_pid, c)][lab] for c in idx
                 if (idx_source_pid, c) in lut and lab in lut[(idx_source_pid, c)]]
            if v:
                score[lab] = float(np.mean(v))
        if len(score) < 2:
            return None
        ok = tot = 0
        for x, y in pairs[pid]:
            if x in score and y in score:
                tot += 1
                ok += int(score[x] > score[y])
        return ok / tot if tot else None

    if a.with_shuffled:
        import torch
        from covalx import Judge, build_prompt
        sub = prompts[: a.prompts]
        texts = {pid: {r["response_index"]: r["messages"][0]["content"]
                       for r in comp["responses"]}
                 for pid, comp, _ in joined if pid in set(sub)}
        crit_text = {}
        for pid, comp, rub in joined:
            items = rub.get("coval_full") or []
            crit_text[pid] = [it["criterion"] for it in items if it.get("scores")]
        judge = Judge(__import__("os").environ.get("COVALX_MODEL_2B",
                                                   "Qwen/Qwen3.5-2B-Base"), batch=32)
        tasks, meta = [], []
        for pid in sub:
            d = donor[pid]
            for which in ("seed", "writein"):
                for ci in crit.get(d, {}).get(which, []):
                    if ci >= len(crit_text.get(d, [])):
                        continue
                    for lab in texts.get(pid, {}):
                        tasks.append(build_prompt(crit_text[d][ci], texts[pid][lab]))
                        meta.append((which, pid, ci, lab))
        print(f"  shuffled-arm judgements: {len(tasks):,}", flush=True)
        sat = judge.score(tasks)
        shuf = {}
        for (which, pid, ci, lab), s in zip(meta, sat):
            shuf.setdefault((which, pid), {}).setdefault(lab, []).append(float(s))
        shuf_acc = {"seed": {}, "writein": {}}
        for which in ("seed", "writein"):
            for pid in sub:
                d0 = shuf.get((which, pid))
                if not d0 or not pairs.get(pid):
                    continue
                score = {lab: float(np.mean(v)) for lab, v in d0.items()}
                ok = tot = 0
                for x, y in pairs[pid]:
                    if x in score and y in score:
                        tot += 1
                        ok += int(score[x] > score[y])
                if tot:
                    shuf_acc[which][pid] = ok / tot
        del judge
        torch.cuda.empty_cache()
    else:
        shuf_acc = {"seed": {}, "writein": {}}

    out = {}
    # CORRECTED 2026-07-28 after an independent statistics review.  The previous
    # version computed `arr[:len(sa)].mean() - sa.mean()`: a POSITIONAL prefix of
    # the all-prompts array minus the mean of a differently-ordered subset, and
    # then reported it next to a `real` computed over ALL prompts.  The printed
    # columns therefore did not subtract to the printed attribution (0.5835 -
    # 0.5368 = 0.0468, but 0.0391 was published).  A comment asserted that pairing
    # was unavailable; it was not -- the shuffled arm iterates `sub`, so the pids
    # were in hand and simply were not recorded.  Both arms are now keyed by pid
    # and differenced PER PROMPT, and the bootstrap resamples prompts (one unit),
    # not two independent sets.  This is retraction #1's failure recurring: an
    # uncertainty compared against a differently-paired uncertainty.
    print(f"{'provenance':12s} {'real(all)':>9} {'real(pair)':>10} {'shuffled':>9} "
          f"{'attribution':>12} {'95% CI':>22} {'n':>5}")
    for which in ("seed", "writein"):
        real_by_pid = {}
        for pid in prompts:
            r = agree(pid, pid, which)
            if r is not None:
                real_by_pid[pid] = r
        arr = np.array(list(real_by_pid.values()))
        bs = np.array([arr[rng.integers(0, len(arr), size=len(arr))].mean()
                       for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        rec = {"real_all_prompts": float(arr.mean()), "ci": [float(lo), float(hi)],
               "prompts": int(len(arr)),
               # deprecated alias: `real` used to mean the all-prompts mean, and
               # was printed beside a shuffled arm computed on a subset.  Kept so
               # the overwrite guard below sees no field disappear across the
               # rename, and so an older reader gets the value it expected.
               "real": float(arr.mean())}
        sd = shuf_acc[which]
        common = sorted(set(real_by_pid) & set(sd))
        if common:
            x = np.array([real_by_pid[p] for p in common])
            y = np.array([sd[p] for p in common])
            dif = x - y                      # PAIRED on the prompt
            attr = float(dif.mean())
            bsd = np.array([dif[rng.integers(0, len(dif), size=len(dif))].mean()
                            for _ in range(a.boot)])
            alo, ahi = np.percentile(bsd, [2.5, 97.5])
            rec.update({"real_paired": float(x.mean()), "shuffled": float(y.mean()),
                        "attribution": attr, "attribution_ci": [float(alo), float(ahi)],
                        "paired_prompts": len(common), "paired": True,
                        # per-prompt differences kept so the seed-vs-write-in GAP
                        # can get an interval of its own.  The two arms sit on
                        # different prompt subsets (a prompt with no usable
                        # write-in criteria appears in one and not the other), so
                        # the gap must be bootstrapped on their INTERSECTION --
                        # otherwise it is two unpaired means differenced, which is
                        # the exact defect this round was just repaired for.
                        "per_prompt_diff": {p: float(v) for p, v in zip(common, dif)}})
            print(f"{which:12s} {arr.mean():>9.4f} {x.mean():>10.4f} {y.mean():>9.4f} "
                  f"{attr:>+12.4f} {f'[{alo:+.4f},{ahi:+.4f}]':>22} {len(common):>5}")
        else:
            print(f"{which:12s} {arr.mean():>9.4f} {'--':>10} {'--':>9} {'--':>12} "
                  f"{f'[{lo:.4f},{hi:.4f}]':>22} {len(arr):>5}")
        out[which] = rec

    d = out["writein"]["real_all_prompts"] - out["seed"]["real_all_prompts"]
    print(f"\n  write-in minus seed (real, all prompts): {d:+.4f}")
    out["writein_minus_seed"] = float(d)
    if out["seed"].get("paired") and out["writein"].get("paired"):
        gap = out["seed"]["attribution"] - out["writein"]["attribution"]
        print(f"  seed minus write-in ATTRIBUTION (unpaired means): {gap:+.4f}")
        out["attribution_gap_seed_minus_writein"] = float(gap)
        ds, dw = out["seed"]["per_prompt_diff"], out["writein"]["per_prompt_diff"]
        both = sorted(set(ds) & set(dw))
        if len(both) >= 30:
            g = np.array([ds[p] - dw[p] for p in both])
            gb = np.array([g[rng.integers(0, len(g), size=len(g))].mean()
                           for _ in range(a.boot)])
            glo, ghi = np.percentile(gb, [2.5, 97.5])
            print(f"  seed minus write-in, PAIRED on {len(both)} shared prompts: "
                  f"{g.mean():+.4f} [{glo:+.4f},{ghi:+.4f}]"
                  f"   {'excludes zero' if glo > 0 or ghi < 0 else 'INCLUDES ZERO'}")
            out["gap_paired"] = {"mean": float(g.mean()), "ci": [float(glo), float(ghi)],
                                 "prompts": len(both),
                                 "excludes_zero": bool(glo > 0 or ghi < 0)}
        else:
            print(f"  gap CI unavailable: only {len(both)} prompts carry both arms")
    Path(_RES).mkdir(parents=True, exist_ok=True)
    # GUARD, added 2026-07-28 after an independent reproducibility review ran
    # this round the way the README documents it -- with no flags -- and watched
    # it silently replace a 20-line result with a 4-line one, deleting the very
    # `attribution` fields that RETRACTIONS entry 6 and the r13 headline stand
    # on.  Without --with-shuffled there is no shuffled arm and no attribution;
    # that is a legitimate partial run, but it must never be allowed to
    # overwrite a complete one in place.  A round that destroys its own evidence
    # when invoked as documented is worse than a round that fails.
    if a.out.exists():
        try:
            prior = json.loads(a.out.read_text())
        except Exception:
            prior = {}
        lost = sorted({k for w in ("seed", "writein")
                       for k in (prior.get(w) or {})} - {k for w in ("seed", "writein")
                                                         for k in (out.get(w) or {})})
        if lost:
            alt = a.out.with_name(a.out.stem + "_partial.json")
            alt.write_text(json.dumps(out, indent=1))
            raise SystemExit(
                f"REFUSING TO OVERWRITE {a.out}\n"
                f"  the existing result carries fields this run did not produce: {lost}\n"
                f"  this run had no shuffled arm -- pass --with-shuffled (needs a GPU and\n"
                f"  the local judge model) to reproduce the full result.\n"
                f"  the partial result was written to {alt} instead.")
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
