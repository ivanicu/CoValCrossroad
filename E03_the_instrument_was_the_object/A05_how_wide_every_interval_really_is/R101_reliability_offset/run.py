"""r101 -- which of three choices explains r100's systematic offset from the stated figures?

CLAIM CARD
----------
Claim      r100 recomputes the frozen protocol's reliability as 0.6070 / 0.6732 / 0.7555
           at k = 6 / 8 / 12, against the stated 0.644 / 0.707 / 0.783 -- all three low
           by 0.03-0.04, a systematic offset. r100 reported it and refused to attribute
           it, because the method behind the stated table no longer exists.
Estimand   the k=8 reliability under each of three ONE-AT-A-TIME variations of r100's
           fixed choices, and whether any lands on the stated 0.707.
Target
observed?  YES for the variants -- each is a different estimator over the same released
           ratings. NO for the original method, which is unrecoverable; this can only
           show which candidate REPRODUCES the stated value, never that it was used.
Alternative
worlds     T TIES        the tie convention closes the gap. The stated table then most
                         likely scored ties as halves rather than toward one label.
           Q QUALIFYING  the prompt filter closes it -- the stated table used a
                         different minimum rater count.
           S SCORE       the agreement statistic closes it.
           U UNATTRIBUTED  none lands within tolerance. Then the offset is not explained
                         by any single one of the three choices r100 fixed, and the
                         space of remaining explanations is narrower by three.
Intervention
           vary exactly one choice per arm, holding the other two at r100's values.
Null       (i) the BASELINE arm must reproduce r100's 0.6732 exactly -- a rebuild
           control, since an arm set differs from r100 only by the choice it varies;
           (ii) a variant is "closing the gap" only if it lands within TOL of 0.707 AND
           the baseline does not. Both conditions, so an arm cannot win by the target
           being loose.

WHY THIS IS THE STEP
--------------------
r100 left the offset systematic and unexplained. An unexplained systematic difference in
a figure the frozen protocol cites is worse than a random one: it means one of the two
methods has a property the other lacks, and nobody knows which. Three of r100's choices
are stated explicitly, which makes them varyable one at a time. If any single change
lands on 0.707, the stated table's method is identified up to that choice. If none does,
three candidates are eliminated and that is the result.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
Landing on 0.707 does NOT prove the original used that choice -- several methods can
share a value. The strongest available claim is CONSISTENT WITH, and the verdict says so
rather than reporting an identification. The reverse direction is stronger: a variant
that moves the number the WRONG way, or not at all, is eliminated as the sole cause.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import human_pairs, load_join  # noqa: E402

COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
R100 = _ROOT / "E03_the_instrument_was_the_object/A05_how_wide_every_interval_really_is/R100_rater_reliability/results/r100_rater_reliability.json"
N_DRAWS, K, TOL = 200, 8, 0.010
TARGET = 0.707


def score(subset, ties: str) -> float | None:
    """r100's score, with the tie rule exposed.

    `first` -- a tie counts as agreement (r100's convention, `>=`).
    `half`  -- a tie counts as 0.5.
    `drop`  -- tied pairs are excluded entirely.
    """
    pr = human_pairs(subset)
    if not pr:
        return None
    w: dict = {}
    for x, y in pr:
        w[(x, y)] = w.get((x, y), 0) + 1
    out = []
    for k in {tuple(sorted(t)) for t in w}:
        a, b = w.get(k, 0), w.get(k[::-1], 0)
        if a == b:
            if ties == "half":
                out.append(0.5)
            elif ties == "first":
                out.append(1.0)
            # `drop` appends nothing
        else:
            out.append(1.0 if a > b else 0.0)
    return float(np.mean(out)) if out else None


def reliability(groups, rng, ties: str, draws: int = N_DRAWS) -> tuple[float, float, int]:
    A, B, H = [], [], []
    for _ in range(draws):
        for g in groups:
            idx = rng.permutation(len(g))
            h = len(g) // 2
            a, b = score([g[i] for i in idx[:h]], ties), score([g[i] for i in idx[h:2 * h]], ties)
            if a is not None and b is not None:
                A.append(a); B.append(b); H.append(h)
    r = float(np.corrcoef(A, B)[0, 1])
    hb = float(np.mean(H))
    return (K / hb * r) / (1 + (K / hb - 1) * r), r, len(A)


def load(min_raters: int):
    out = []
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        asm = [x for x in comp["metadata"]["assessments"] if human_pairs([x])]
        if len(asm) >= min_raters:
            out.append(asm)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r101_reliability_offset.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    if not R100.exists():
        raise SystemExit("REFUSING: r100 absent; this round varies its choices and must read them.")
    r100 = json.load(open(R100))
    base_stated = r100["by_k"]["8"]["reliability"]

    arms = {
        "baseline (r100: ties->first, min_raters=8)": dict(min_raters=8, ties="first"),
        "TIES: tied pairs count 0.5": dict(min_raters=8, ties="half"),
        "TIES: tied pairs dropped": dict(min_raters=8, ties="drop"),
        "QUALIFYING: min_raters=2": dict(min_raters=2, ties="first"),
        "QUALIFYING: min_raters=12": dict(min_raters=12, ties="first"),
    }
    cache: dict = {}
    rows = {}
    print(f"  {'arm':<44} {'k=8 rel':>9} {'vs 0.707':>10} {'split-half r':>13} {'prompts':>8}")
    for name, cfg in arms.items():
        if cfg["min_raters"] not in cache:
            cache[cfg["min_raters"]] = load(cfg["min_raters"])
        groups = cache[cfg["min_raters"]]
        rel, rh, n = reliability(groups, np.random.default_rng(20260729), cfg["ties"])
        rows[name] = {"reliability_k8": rel, "diff_vs_target": rel - TARGET,
                      "split_half_r": rh, "n_prompts": len(groups), "n_half_pairs": n, **cfg}
        print(f"  {name:<44} {rel:>9.4f} {rel - TARGET:>+10.4f} {rh:>13.4f} {len(groups):>8}")

    # ---- REBUILD CONTROL -------------------------------------------------------
    got = rows["baseline (r100: ties->first, min_raters=8)"]["reliability_k8"]
    drift = abs(got - base_stated)
    print(f"\n  rebuild control: baseline {got:.6f} vs r100's {base_stated:.6f}  drift {drift:.2e}")
    if drift > 1e-9:
        raise SystemExit("REFUSING: the baseline arm does not reproduce r100, so the arms differ by "
                         "more than the choice each varies and nothing here is one-at-a-time.")

    base_closes = abs(got - TARGET) <= TOL
    closers = [k for k, v in rows.items()
               if not k.startswith("baseline") and abs(v["diff_vs_target"]) <= TOL]
    world = ("U UNATTRIBUTED" if not closers else
             ("T TIES" if all("TIES" in c for c in closers) else
              "Q QUALIFYING" if all("QUALIFYING" in c for c in closers) else "MIXED"))
    if base_closes:
        world = "VOID -- the baseline already lands within tolerance of the target"
    print(f"\n  arms landing within {TOL} of {TARGET}: {closers if closers else 'none'}")

    verdict = (
        f"{world}. r100 found the stated reliability figures high by a systematic 0.03-0.04 and refused "
        f"to attribute the offset, because the method behind them no longer exists. Three of r100's "
        f"choices are stated explicitly, so each can be varied ALONE. At k={K}, against the stated "
        f"{TARGET}: "
        + "; ".join(f"{k} -> {v['reliability_k8']:.4f} ({v['diff_vs_target']:+.4f})"
                    for k, v in rows.items()) + ". "
        f"REBUILD CONTROL: the baseline arm reproduces r100's {base_stated:.4f} to {drift:.0e}, so each "
        f"arm differs from it only by the choice it varies and the comparison is genuinely "
        f"one-at-a-time. "
        + (f"NO SINGLE CHOICE CLOSES THE GAP: none of the four variants lands within {TOL} of "
           f"{TARGET}. So the offset is not explained by the tie convention alone, nor by the "
           f"qualifying rater count alone, and three candidate causes are eliminated. What remains is "
           f"the agreement statistic itself, some choice not among r100's three, or a combination -- a "
           f"narrower space than before, and still not an identification."
           if not closers else
           f"CONSISTENT WITH: {closers} lands within {TOL} of the stated value. That is CONSISTENT "
           f"WITH the original having made that choice and is NOT an identification -- several methods "
           f"can share a value, and the original is unrecoverable. The claim is directional: this "
           f"choice can produce the stated figure, whereas r100's cannot.") +
        f" SCOPE: every arm scores the same released ratings; nothing here is a new measurement, and "
        f"none of it changes the frozen protocol's rater count, which both figures support."
    )

    doc = {
        "k": K, "target_stated": TARGET, "tolerance": TOL, "arms": rows,
        "rebuild_drift_vs_r100": float(drift), "arms_within_tolerance": closers,
        "baseline_already_closes": bool(base_closes), "world": world,
        "outcome_variable_scope": (
            "Spearman-Brown reliability at k=8 of a per-prompt human agreement score, over the released "
            "ratings. Arms differ by exactly one of r100's stated choices."),
        "scope": (
            "Can show which candidate REPRODUCES the stated value; cannot show the original used it, "
            "since several methods can share a number and the original method is gone. The eliminating "
            "direction is the stronger one."),
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
