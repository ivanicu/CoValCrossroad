"""r85 -- ten rounds run on the long-form third. Does the rubric behave differently there?

CLAIM CARD
----------
Claim      entry 161: ten rounds take a head slice of a form-sorted file and so
           run on >=97% long-form prompts against a 30.3% baseline, and
           "generalisation to the other 70% is untested -- and, because no prompt
           exists under both forms, untestable from this data."
Estimand   the rubric's pairwise agreement with REAL HUMAN rankings, computed
           separately on the long-form and short-form prompts of the FULL join.
Target
observed?  YES, and the "untestable" was too strong. It is exact for a
           prompt-for-prompt contrast -- no prompt appears under both forms. It is
           NOT true for a round-level one: rounds using the whole join have both
           populations in hand, and 291 long against 677 short is far more n than
           the r12-vs-r46 comparison that entry 159 already leaned on.
Alternative
worlds     N NO DIFFERENCE  agreement is equivalent across forms at delta=0.01.
                            Then the ten sliced rounds sit on a population that is
                            not special on this axis, and entry 161's scope block
                            stands as a provenance fact rather than a threat.
           D DIFFERENT      agreement differs materially. Then the ten rounds'
                            results are measured where the rubric behaves
                            differently, and the scope block needs to say so much
                            more loudly.
Intervention
           none. The same computation, partitioned.
Null       shuffle the form labels across prompts and recompute; the gap must
           collapse. A partition of 968 prompts into 291 and 677 will show SOME
           difference by chance, and the shuffle says how much.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
The forms cover DISJOINT prompts (entry 158), so any difference is between
different questions as well as different instruments, and this design cannot
separate them -- exactly the defect that withdrew entry 157's attribution. What
it CAN do is bound the size of any form-associated difference, which is what the
scope block needs and does not have.

WHAT IT DOES NOT DO
-------------------
It does not license "form does not matter". A null here means the rubric's
agreement with humans is similar on both prompt sets; it says nothing about
whether the same prompt asked under both instruments would produce the same
rankings, which no data in this release can answer.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import human_pairs, load_join  # noqa: E402

SAT = _ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
DELTA = 0.01
N_BOOT = 3000
N_SHUFFLE = 400


def long_form_prompts():
    by_ann = defaultdict(list)
    for line in open(COMPARISONS, encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        for asm in rec["metadata"]["assessments"]:
            by_ann[asm["annotator_id"]].append((rec["prompt_id"], asm))
    out = set()
    for _aid, seq in by_ann.items():
        for pid, asm in seq:
            rb = asm.get("ranking_blocks") or {}
            if (rb.get("world") or []) and rb.get("personal"):
                out.add(pid)
    return out


def weights(items):
    """r32's signed_magnitude, from the human ratings."""
    w = []
    for it in items:
        sc = [float(s["score"]) for s in (it.get("scores") or [])]
        w.append(float(np.mean(sc)) if sc else 0.0)
    return np.array(w, float)


def agree(satp, items, w, pairs):
    ok = tot = 0
    for a_, b_ in pairs:
        sa = sb = 0.0
        for ci in range(len(items)):
            if w[ci] == 0.0:
                continue
            va, vb = satp.get((ci, a_)), satp.get((ci, b_))
            if va is None or vb is None:
                continue
            sa += w[ci] * va
            sb += w[ci] * vb
        if sa == sb:
            continue
        tot += 1
        ok += int(sa > sb)
    return ok, tot


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r85_agreement_by_form.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    for p in (SAT, COMPARISONS, RUBRICS):
        if not p.exists():
            raise SystemExit(f"REFUSING: {p.relative_to(_ROOT)} absent.")

    z = np.load(SAT, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s_ in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        sat[pid][(int(ci), lab)] = float(s_)

    L = long_form_prompts()
    rows = []
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        pairs = human_pairs(comp["metadata"]["assessments"])
        items = rub.get("coval_full") or []
        if not pairs or not items or pid not in sat:
            continue
        ok, tot = agree(sat[pid], items, weights(items), pairs)
        if tot:
            rows.append({"pid": pid, "ok": ok, "tot": tot, "long": pid in L})
    if len(rows) < 300:
        raise SystemExit(f"REFUSING: only {len(rows)} usable prompts.")
    ok = np.array([r["ok"] for r in rows], float)
    tot = np.array([r["tot"] for r in rows], float)
    isl = np.array([r["long"] for r in rows], bool)
    print(f"prompts {len(rows)}   long-form {int(isl.sum())}   short-form {int((~isl).sum())}")

    def rate(m):
        return float(ok[m].sum() / tot[m].sum())

    def boot(m, seed):
        idx = np.flatnonzero(m)
        rng = np.random.default_rng(seed)
        b = [float(ok[s].sum() / tot[s].sum())
             for s in (idx[rng.integers(0, len(idx), len(idx))] for _ in range(N_BOOT))]
        return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))

    rl, rs = rate(isl), rate(~isl)
    ll, lh = boot(isl, 1)
    sl, sh = boot(~isl, 2)
    gap = rl - rs
    # paired bootstrap for the GAP: resample prompts once, recompute both arms
    rng = np.random.default_rng(20260907)
    n = len(rows)
    gb = []
    for _ in range(N_BOOT):
        s_ = rng.integers(0, n, n)
        m = isl[s_]
        if m.sum() > 30 and (~m).sum() > 30:
            gb.append(ok[s_][m].sum() / tot[s_][m].sum()
                      - ok[s_][~m].sum() / tot[s_][~m].sum())
    glo, ghi = float(np.percentile(gb, 2.5)), float(np.percentile(gb, 97.5))
    print(f"\n  long-form  agreement {rl:.4f} [{ll:.4f},{lh:.4f}]  ({int(isl.sum())} prompts)")
    print(f"  short-form agreement {rs:.4f} [{sl:.4f},{sh:.4f}]  ({int((~isl).sum())} prompts)")
    print(f"  gap {gap:+.4f} [{glo:+.4f},{ghi:+.4f}]")

    # NULL: shuffle the form labels, keeping the 291/677 split sizes
    srng = np.random.default_rng(20260908)
    null = []
    for _ in range(N_SHUFFLE):
        lab = isl.copy()
        srng.shuffle(lab)
        null.append(rate(lab) - rate(~lab))
    null = np.array(null)
    nlo, nhi = float(np.percentile(null, 2.5)), float(np.percentile(null, 97.5))
    print(f"  form-label shuffle null: [{nlo:+.4f},{nhi:+.4f}] over {N_SHUFFLE} draws")

    # THE ANSWERABLE MARGIN, r60's pattern. "UNRESOLVED" alone tells a reader
    # nothing about how close the test came; the half-width says what delta this
    # design could have settled, and 293 long-form prompts is the binding limit.
    half = (ghi - glo) / 2
    equivalent = bool(glo > -DELTA and ghi < DELTA)
    significant = bool(glo > 0 or ghi < 0)
    outside_null = bool(gap < nlo or gap > nhi)
    world = ("D DIFFERENT" if significant and not equivalent else
             "N NO DIFFERENCE" if equivalent else
             f"B BOUNDED -- no detectable difference, and any form effect is under {half:.3f}")

    verdict = (
        f"{world}. Entry 161 found ten rounds running on >=97% long-form prompts because they head-slice "
        f"a form-sorted file, and said generalisation was 'untestable from this data'. That is exact "
        f"for a PROMPT-FOR-PROMPT contrast and too strong for a ROUND-LEVEL one: rounds using the whole "
        f"join hold both populations. Computing the rubric's pairwise agreement with REAL HUMAN "
        f"rankings separately, over {len(rows)} prompts split {int(isl.sum())} long and "
        f"{int((~isl).sum())} short: {rl:.4f} [{ll:.4f},{lh:.4f}] against {rs:.4f} [{sl:.4f},{sh:.4f}], "
        f"a gap of {gap:+.4f} [{glo:+.4f},{ghi:+.4f}] under a paired prompt bootstrap. Shuffling the "
        f"form labels at the same split sizes gives [{nlo:+.4f},{nhi:+.4f}], and the observed gap is "
        f"{'OUTSIDE' if outside_null else 'inside'} that. SIGNIFICANCE AND EQUIVALENCE SEPARATELY: the "
        f"gap {'differs' if significant else 'does not differ'} from zero and is "
        f"{'' if equivalent else 'NOT '}practically equivalent at delta={DELTA}. "
        f"THE ANSWERABLE MARGIN IS THE USEFUL NUMBER: the interval's half-width is {half:.4f}, so "
        f"this design could have settled equivalence at delta={half:.3f} and not at {DELTA}. The "
        f"binding limit is {int(isl.sum())} long-form prompts, and no rearrangement of this release "
        f"adds more. So the correct statement is NOT 'the forms are equivalent' and NOT 'we cannot "
        f"tell' -- it is that any form-associated difference in this quantity is smaller than "
        f"{half:.3f}, and the point estimate is {gap:+.4f}, about {abs(gap)/rl:.1%} of the agreement "
        f"level. "
        f"WHAT THIS DOES FOR ENTRY 161's SCOPE BLOCK: it "
        f"{'stands as a provenance fact rather than a threat -- the ten rounds sit where the rubric agrees with humans at a rate indistinguishable from the rest' if equivalent else 'needs strengthening: the ten rounds are measured where the rubric behaves differently'}. "
        f"THE CONFOUND, WRITTEN BEFORE THE RUN AND UNRESOLVED: the forms cover DISJOINT prompts, so any "
        f"difference is between different questions as well as different instruments. This bounds the "
        f"size of a form-associated difference; it cannot attribute one, and it does not license 'form "
        f"does not matter' -- no data here can say what the same prompt would produce under the other "
        f"instrument."
    )

    doc = {
        "n_prompts": len(rows), "n_long": int(isl.sum()), "n_short": int((~isl).sum()),
        "long_form_agreement": rl, "long_form_ci": [ll, lh],
        "short_form_agreement": rs, "short_form_ci": [sl, sh],
        "gap": gap, "gap_ci": [glo, ghi], "answerable_margin": float(half),
        "shuffle_null_ci": [nlo, nhi], "gap_outside_null": outside_null,
        "significant": significant, "equivalent_at_delta": equivalent, "delta": DELTA,
        "world": world,
        "outcome_variable_scope": (
            "Agreement is against REAL HUMAN pairwise rankings. Satisfaction comes from r04's "
            "tensor, so the judge is in the loop for s(c,r) but the target is human."),
        "scope": (
            "The forms cover disjoint prompts, so this compares instruments and questions together "
            "and cannot separate them. Weights are r32's signed_magnitude over coval_full. A null "
            "bounds the size of any form-associated difference in THIS quantity; other quantities "
            "are not covered and the ten sliced rounds measure several of them."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
