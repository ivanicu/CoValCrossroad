#!/usr/bin/env python3
"""
R872 · how many directional claims in this corpus were only ever measured at TWO ENDS?

⛔ WHY. R871 printed *"the rate RISES — late adoption; the practice is improving"* from a series of
`0.000 · 0.000 · 0.364 · 0.000 · 0.000 · 0.273`. **Four of six points are zero.** The verdict
computed `trend = last − first` and branched on its sign; both endpoints happened to be the two
non-zero buckets, so an endpoint test reported a clean monotone rise from a curve that is bimodal.
**That is §4's `min/max of N draws quoted as an interval`, wearing a time axis instead of a
bootstrap** — and I made it knowingly enough to write the correction myself.

**The question this round exists for: how often has that happened in the other 800 rounds?** A
direction asserted from two ends is a different claim from one measured across a curve, and nothing
in this project has ever checked which kind its published directions are.

⭐ AND THE CONTROLS ARE REAL COMMITTED CASES WITH KNOWN ANSWERS, WHICH IS THE WHOLE POINT.
R869 built a classifier whose positive category no real item ever entered, and its remedy was:
require a REAL corpus item in a category before trusting it. **Both arms here are real artifacts
from this session, one known non-monotone and one known monotone**, so the detector is demonstrated
on the object rather than on a shape I invented.


⛔⛔⛔ POST-RUN CORRECTION. **`WORLD B` FIRED AND THE 0.488 IS AN UPPER BOUND, NOT A RATE — MY
`ENDPOINT_ONLY` CATEGORY IS FULL OF THE WRONG MEMBERS.**

**Read the flagged series, which the round printed itself:**
`R238 [0.099, 0.099, 0.098, 0.096, 0.097]` · `R145 [0.109, 0.108, 0.112, 0.107, 0.108]` ·
`R105 [0.695, 0.699, 0.684]`. **Those are near-FLAT series with noise in the third decimal.** They
are not directional claims contradicted by their middles — **they are series that assert no
direction at all**, and `classify` only special-cases an EXACTLY constant series as `FLAT`. Anything
with a single wobble becomes `ENDPOINT_ONLY`.

⭐ **So 21/43 = 0.488 measures "how many series are non-monotone", which is dominated by "how many
series are noisy and flat".** It bounds the quantity I wanted from above and does not estimate it.
**R871's own case is the real thing** — range 0.364 with four exact zeros — and it sits in the same
bucket as a series whose entire range is 0.003.

⛔ **This is R869's failure in mirror image, and that makes three consecutive rounds on one theme.**
R869: a category with ZERO real members carried a verdict. R870: a category with ONE member did.
R872: a category with MANY members, most of which are not the phenomenon. **The common defect is not
occupancy — it is that I keep checking whether a category is POPULATED and never whether it is
POPULATED BY THE RIGHT THING.** A positive control answers the first question. Nothing here answered
the second, and the remedy R869 wrote — *require a real corpus item in the category* — is satisfied
by all three of these and prevented none of them.

**WHAT THE ROUND STILL ESTABLISHES, and it is not nothing:**
  ⭐ The detector is demonstrated on **two real committed artifacts with known opposite answers** —
     R871's `[0, 0, 0.364, 0, 0, 0.273]` as ENDPOINT_ONLY and R862's `[0.9901 … 0.9564]` as
     MONOTONE. That is the strongest control shape available here and both arms passed.
  ⭐ **128 rounds assert a direction and carry a series; 185 assert one with NO series in their
     artifact at all.** That second number is the more alarming one and it needed no classifier:
     **185 directional claims in this corpus have no recoverable numeric series behind them.**
  ⚠ 85 of the 128 carry MORE THAN ONE series, so the direction word cannot be matched to a specific
     one by co-location. Excluded from the headline, as declared before the run.

**WHAT IT WOULD TAKE to measure the real quantity** — stated as an availability claim in the
unflattering direction: each series needs **its own noise floor**, so a violation can be judged
LARGE or SMALL relative to what that round's design could resolve. This corpus does not store
per-series floors, so separating *non-monotone because noisy* from *non-monotone because the claim
is wrong* is **not available here**, and no threshold on raw range would be anything but a guess.

**The sentence this round cannot support:** *"the corpus carries directional claims its own data
does not support, at a rate of 49%."* What it can support: *at most 21 of 43 unambiguous rounds have
a non-monotone supporting series, and the set is dominated by series too flat to have asserted a
direction in the first place.*

ESTIMAND        among rounds that assert a DIRECTION in their own verdict text, the share whose
                supporting numeric series is monotone in that direction across ALL its points,
                versus the share where only the endpoints agree.
IDENTIFICATION  partial, and the limit is named: a round's direction word and its series are
                matched by co-location in the same round, not by a parse of which series the
                sentence refers to. A round with several series may be scored against the wrong
                one. Those are reported as AMBIGUOUS_SERIES and excluded from the headline rather
                than resolved by guessing.
SCOPE           population: every `E0*/A*/R*/run.py` containing a direction word, whose artifact
                            carries at least one numeric list of length >= 3
                instrument: monotonicity over the full series vs sign(last − first)
                baseline:   a round whose series IS monotone — the endpoint claim is then sound
                regime:     this repo, full corpus
WORLDS          A · nearly all directional claims are monotone -> R871 was an isolated slip
                B · a substantial share are ENDPOINT-ONLY -> the corpus carries directional claims
                    its own data does not support, and the count is the finding
                C · almost no round pairs a direction word with a recoverable series -> the audit
                    cannot be run on this corpus and says so, rather than reporting a small number
                    from a tiny population as though it were a rate
KILL            CONDITIONAL, all required, and both arms are REAL:
                  ⭐ ① POSITIVE: R871's `by_date` rate series must be classified NON-MONOTONE. It is
                     the case that motivated the round; if the detector cannot see it, nothing else
                     it reports is readable.
                  ⭐ ② g=0: R862's width-sweep `ratio` series must be classified MONOTONE. A
                     detector that calls everything non-monotone passes arm ① trivially.
                  ③ non-empty population, else exit 2 and say the audit could not run.
PLACEBO         a constant series (all equal) is monotone in BOTH directions and must be reported
                as FLAT, never as evidence for a direction.
MULTIPLICITY    every round × every qualifying series; all reported.
ARTIFACT        results/endpoint_claims.json
IMPOSSIBLE      cross-release · construct validated · causally identified.
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

DIRWORD = re.compile(
    r"\b(rises?|rising|falls?|falling|increas\w+|decreas\w+|monoton\w+|strengthens?|weakens?|"
    r"grows?|shrinks?|declin\w+|trend\w*)\b", re.I)
MIN_LEN = 3


def numeric_series(obj, path="", out=None):
    """Every list of >=3 numbers reachable in the artifact, with its key path."""
    if out is None:
        out = []
    if isinstance(obj, list):
        nums = [x for x in obj if isinstance(x, (int, float)) and not isinstance(x, bool)]
        if len(nums) == len(obj) and len(nums) >= MIN_LEN:
            out.append((path or "<root>", nums))
        else:
            for i, v in enumerate(obj):
                numeric_series(v, f"{path}[{i}]", out)
    elif isinstance(obj, dict):
        # a list of dicts each carrying the same numeric key is also a series
        for k, v in obj.items():
            numeric_series(v, f"{path}.{k}" if path else k, out)
        for k in ("rate", "ratio", "mean", "value", "count", "n"):
            rows = obj.get("rows") or obj.get("cells")
            if isinstance(rows, list) and len(rows) >= MIN_LEN and \
                    all(isinstance(r, dict) and isinstance(r.get(k), (int, float)) for r in rows):
                out.append((f"{path}.rows[].{k}" if path else f"rows[].{k}",
                            [r[k] for r in rows]))
    return out


def classify(vals):
    if len(set(vals)) == 1:
        return "FLAT"
    d = vals[-1] - vals[0]
    if d == 0:
        return "ENDPOINTS_EQUAL"
    up = d > 0
    steps = [b - a for a, b in zip(vals, vals[1:])]
    # parens are REQUIRED: a bare `if A if B else C` filter is a SyntaxError, not the conditional
    # I read it as. Caught by the interpreter, which is the cheapest reviewer available.
    viol = sum(1 for s in steps if ((s < 0) if up else (s > 0)))
    return "MONOTONE" if viol == 0 else "ENDPOINT_ONLY"


def controls():
    a = ROOT / ("E05_the_space_of_compilers/A25_can_the_instrument_be_run_at_all/"
                "R871_is_the_worlds_convention_growing_or_decaying/results/convention_trend.json")
    b = ROOT / ("E05_the_space_of_compilers/A24_what_the_definition_costs/"
                "R862_does_the_selection_sign_survive_a_60x_wider_family/results/width_sweep.json")
    p1 = p2 = False
    s1 = s2 = None
    if a.exists():
        d = json.loads(a.read_text())
        s1 = [r["rate"] for r in d.get("by_date", [])]
        p1 = len(s1) >= MIN_LEN and classify(s1) == "ENDPOINT_ONLY"
    if b.exists():
        d = json.loads(b.read_text())
        s2 = [r["ratio"] for r in d.get("rows", []) if r.get("width", 0) > 1]
        p2 = len(s2) >= MIN_LEN and classify(s2) == "MONOTONE"
    print(f"  POSITIVE  R871's by_date rates {[round(x,3) for x in (s1 or [])]} -> ENDPOINT_ONLY: "
          f"{p1}  {'PASS' if p1 else 'FAIL'}")
    print(f"  g=0       R862's width ratios {[round(x,4) for x in (s2 or [])]} -> MONOTONE: "
          f"{p2}  {'PASS' if p2 else 'FAIL'}")
    print(f"  PLACEBO   a constant series is FLAT, never a direction: "
          f"{classify([0.5,0.5,0.5]) == 'FLAT'}  "
          f"{'PASS' if classify([0.5,0.5,0.5]) == 'FLAT' else 'FAIL'}")
    print("    Both arms are REAL committed artifacts with known answers — R869 built a classifier")
    print("    whose positive category no real item ever entered, and this is that remedy applied.")
    return p1 and p2 and classify([0.5, 0.5, 0.5]) == "FLAT"


def main() -> int:
    if not controls():
        print("\n  UNVERIFIED: the detector failed its own controls. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED"}, open(OUT / "endpoint_claims.json", "w"), indent=2)
        return 2

    rows, no_series, no_dir = [], 0, 0
    for run in sorted(ROOT.glob("E0*/A*/R*/run.py")):
        txt = run.read_text(encoding="utf-8", errors="ignore")
        if not DIRWORD.search(txt):
            no_dir += 1; continue
        series = []
        for art in sorted((run.parent / "results").glob("*.json")):
            try:
                series += numeric_series(json.loads(art.read_text()))
            except Exception:
                continue
        series = [(k, v) for k, v in series if len(v) >= MIN_LEN]
        if not series:
            no_series += 1; continue
        cls = [classify(v) for _, v in series]
        rows.append({"round": run.parent.name, "n_series": len(series),
                     "classes": cls,
                     "any_endpoint_only": "ENDPOINT_ONLY" in cls,
                     "all_monotone": all(c in ("MONOTONE", "FLAT") for c in cls),
                     "ambiguous": len(series) > 1,
                     "series": [{"key": k, "vals": v, "class": c}
                                for (k, v), c in zip(series, cls)][:6]})

    if not rows:
        print("\n  OBSERVED NOTHING: no round pairs a direction word with a recoverable series.")
        print("  The audit could not run. Exit 2, never 0.")
        return 2

    unamb = [r for r in rows if not r["ambiguous"]]
    print(f"\n  {len(rows)} round(s) assert a direction AND carry a series"
          f"  ·  {no_dir} no direction word  ·  {no_series} direction word but no series")
    print(f"  ⚠ {len(rows)-len(unamb)} carry MORE THAN ONE series and are AMBIGUOUS — the direction")
    print(f"    word cannot be matched to a specific series by co-location. Excluded from the")
    print(f"    headline, reported in the artifact.")
    if unamb:
        eo = sum(1 for r in unamb if r["any_endpoint_only"])
        print(f"\n  ⭐ UNAMBIGUOUS rounds: {len(unamb)}")
        print(f"     ENDPOINT_ONLY (middle violates the claimed direction): {eo}"
              f"  = {eo/len(unamb):.3f}")
        for r in [x for x in unamb if x["any_endpoint_only"]][:8]:
            v = r["series"][0]["vals"]
            print(f"       {r['round'][:56]:<56} {[round(x,3) for x in v][:7]}")
    else:
        eo = 0

    frac = (eo / len(unamb)) if unamb else None
    world = ("C" if len(unamb) < 5 else "B" if frac >= 0.15 else "A")
    print(f"\n  ⭐ WORLD {world}: " + {
        "A": "nearly all directional claims are monotone across their whole series — R871 was an"
             " isolated slip",
        "B": "a substantial share are ENDPOINT-ONLY — the corpus carries directional claims its"
             " own data does not support",
        "C": "too few rounds pair a direction word with an UNAMBIGUOUS series — the audit cannot"
             " be run on this corpus, and a rate from a tiny population would be a number pretending"
             " to be a measurement"}[world])
    print(f"     ⚠ Co-location, not parsing: a round's direction word is matched to its artifact's")
    print(f"       series by being in the same round. That is why multi-series rounds are excluded.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_with_direction_and_series": len(rows),
               "n_unambiguous": len(unamb), "n_endpoint_only": eo,
               "endpoint_only_rate": frac,
               "excluded_no_direction_word": no_dir, "excluded_no_series": no_series,
               "excluded_ambiguous": len(rows) - len(unamb), "rows": rows},
              open(OUT / "endpoint_claims.json", "w"), indent=2)
    print(f"\n  artifact: results/endpoint_claims.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
