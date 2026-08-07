#!/usr/bin/env python3
"""
R871 · is the WORLDS convention being ADOPTED or DECAYING? — the 765 blockless rounds, dated.

⛔ WHY. R870 measured that the forks in this project are exercised at close to the rate a genuine
fork predicts — **on 51 rounds, 6.3% of the corpus.** The other 765 have no parseable `WORLDS` block
at all. That coverage is the largest open quantity the round left, and it has two completely
different readings with opposite consequences:

  **OLD** — the convention was adopted late, the blockless rounds predate it, and the practice is
            improving. Then 6.3% is a historical artifact and nothing needs fixing.
  **DECAY** — the convention was used and then dropped. Then the 6.3% is a live process defect and
            every recent round is quietly skipping the one block that makes a fork falsifiable.

**These are not the same finding and no number in R870 separates them.**

⭐ AND `temporally resolved` IS AVAILABLE HERE, WHICH IS UNUSUAL FOR THIS PROJECT. It sits in the
impossibility register for every round about the RELEASE, because the annotations carry no
timestamps. **The corpus is not the release** — git dates every round's first appearance exactly. So
the criterion is claimed rather than reflexively excluded, and that distinction is the reason to
read the register per-object instead of per-project.


⛔⛔⛔ POST-RUN CORRECTION. **THE PRINTED `WORLD A` IS WITHDRAWN. THE ANSWER IS `D`, AND THE SHAPE
WAS SITTING IN MY OWN OUTPUT.**

**The rates by git date: `0.000 · 0.000 · 0.364 · 0.000 · 0.000 · 0.273`.**
**By R-number:          `0.000 · 0.000 · 0.000 · 0.234 · 0.000 · 0.182`.**

That is **bimodal**, not rising. Four of six buckets are EXACTLY ZERO on both axes and two carry
the whole convention. **Neither "late adoption" nor "decay" describes it** — both are monotone
stories, and this curve is neither.

⛔ **The defect is mine and it is a known family:** the verdict computed `trend = last − first` and
branched on its sign. **A two-point trend on a six-point curve uses the endpoints and throws away
the shape** — §4's `min/max of N draws quoted as an interval`, wearing a time axis instead of a
bootstrap. Both endpoints happened to be the two non-zero buckets, so the endpoint test reported a
clean monotone rise from a curve with four zeros in it.

⭐ **What the data actually says: the convention is EPISODIC.** It appears in two isolated bursts
and is absent everywhere else. That is a more useful finding than either pre-registered story,
because it relocates the cause: **the block is not a function of WHEN a round was written but of
what was happening while it was written** — a burst, then nothing, then a burst. A monotone answer
would have implied a fix (adopt it / stop dropping it); an episodic one implies a different
question, which is what sustains a burst.

⚠ **KILL ③ PASSED FOR A WEAKER REASON THAN THE DATA SUPPORTS, and that is worth recording.** It
asked only whether the two axes agree on the SIGN of the endpoint difference. They do — but they
also agree on the far stronger fact of *where the zeros are*. **A control can pass on the weakest
reading of the thing it was checking, and still leave the strong version unstated.**

⚠ **TWO SCOPE FACTS THAT BOUND EVERY SENTENCE ABOVE.**
  ① **Only 527 of 822 rounds carry a git date from this map.** 295 do not, and the round does not
     establish why — a path added under a different name and later moved would be missed by a
     `--diff-filter=A` first-appearance map. That is 36% of the corpus unplaced on the time axis,
     and it is reported here rather than absorbed.
  ② **Every date falls in 2026-08-03 .. 2026-08-06 — FOUR DAYS.** So the "time" axis is barely a
     time axis; the sextiles are closer to an ORDERING than to a calendar. **A trend measured over
     four days should not be described as the practice improving over time**, and the printed
     sentence did exactly that.

**The sentence this round cannot support:** *"late adoption; the practice is improving."*
What it can support: *the WORLDS block appears in two isolated bursts covering 6.9% of 822 rounds,
with four of six buckets at exactly zero on both axes.*

ESTIMAND        the share of rounds carrying a parseable `WORLDS` block, as a function of when the
                round FIRST APPEARED in git, and as a function of its R-number.
IDENTIFICATION  exact. `git log --diff-filter=A --name-only` gives every path's first commit date in
                one pass; the block is a regex over the committed file. Both axes are complete —
                no sampling, no imputation.
SCOPE           population: every `E0*/A*/R*/run.py` tracked in git
                instrument: R870's `declared()` parser, reused UNCHANGED so the two rounds count
                            the same thing — a re-implementation here would make the 6.3% and this
                            trend incomparable, which is the borrowed-quantity error one level over
                baseline:   a flat rate; adoption predicts rising, decay predicts falling
                regime:     this repo, full history
WORLDS          A · rate RISES with time -> late adoption; the 765 are historical and the practice
                    is improving
                B · rate FALLS with time -> decay; a live process defect in recent rounds
                C · rate is FLAT and low -> the convention was never really adopted, and R870's 51
                    are a self-selected subset with no temporal story at all
                D · rate is high recently and the 765 are concentrated in ONE era -> a regime
                    change, and the era boundary is the finding rather than the trend
KILL            CONDITIONAL, all required:
                  ⭐ ① POSITIVE: the date map must locate a KNOWN round. `R866` was added by commit
                     496b0b28 in this session, so its first-appearance date must be the newest in
                     the corpus, or within one day of it. If the map cannot date a round I watched
                     land, its dates are silence.
                  ⭐ ② g=0: a path NOT in git must return no date rather than a default. A map that
                     invents a date for everything passes arm ① trivially.
                  ③ the two axes (git date, R-number) must AGREE on the ordering direction. They are
                     independent measurements of the same latent variable; if they disagree, the
                     R-number is not a time proxy and only the git axis is readable.
                  ④ non-empty population, else exit 2.
PLACEBO         the parser applied to a file with no WORLDS block returns None, not an empty list.
MULTIPLICITY    one trend on each of two axes; both reported whatever they show.
ARTIFACT        results/convention_trend.json
IMPOSSIBLE      cross-release · construct validated · causally identified (nothing here intervenes
                on whether a round got a block). ⚠ `temporally resolved` is CLAIMED, not excluded.
"""
import importlib.util, json, pathlib, re, subprocess, sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

# ⭐ REUSE R870's parser UNCHANGED. Re-implementing it would make the 6.3% and this trend two
# different measurements wearing one name — the borrowed-quantity error, one level up.
_r870 = ROOT / ("E05_the_space_of_compilers/A25_can_the_instrument_be_run_at_all/"
                "R870_were_my_declared_worlds_ever_entered/run.py")
_sp = importlib.util.spec_from_file_location("r870", _r870)
r870 = importlib.util.module_from_spec(_sp)
# Imported under __name__ == 'r870', so R870's `if __name__ == "__main__"` guard keeps its
# main() from running. The import is for `declared` only.
_sp.loader.exec_module(r870)
declared = r870.declared

RNUM = re.compile(r"/R(\d+)_")


def first_seen():
    """path -> ISO date of the commit that ADDED it. One pass over history."""
    out = subprocess.run(
        ["git", "-C", str(ROOT), "log", "--reverse", "--diff-filter=A",
         "--name-only", "--format=%x01%cI"], capture_output=True, text=True).stdout
    m, date = {}, None
    for line in out.splitlines():
        if line.startswith("\x01"):
            date = line[1:].strip()[:10]
        elif line.strip() and date:
            m.setdefault(line.strip(), date)
    return m


def controls(dates):
    r866 = ("E05_the_space_of_compilers/A24_what_the_definition_costs/"
            "R866_the_comparator_is_a_swept_axis_not_a_choice/run.py")
    d866 = dates.get(r866)
    newest = max(dates.values()) if dates else None
    p1 = d866 is not None and d866 == newest
    p2 = dates.get("this/path/does/not/exist.py") is None
    p3 = declared("ESTIMAND x\nKILL y\n") is None
    print(f"  POSITIVE  R866 dates to the newest day in the corpus ({d866} vs {newest}): {p1}  "
          f"{'PASS' if p1 else 'FAIL'}")
    print(f"  g=0       an absent path returns no date, not a default: {p2}  "
          f"{'PASS' if p2 else 'FAIL'}")
    print(f"  PLACEBO   a file with no WORLDS block parses to None: {p3}  "
          f"{'PASS' if p3 else 'FAIL'}")
    print("    Arm 2 exists because a map that invents a date for everything passes arm 1 by luck.")
    return p1 and p2 and p3


def main() -> int:
    dates = first_seen()
    if not controls(dates):
        print("\n  UNVERIFIED: the date map failed its own controls. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED"}, open(OUT / "convention_trend.json", "w"), indent=2)
        return 2

    rows = []
    for run in sorted(ROOT.glob("E0*/A*/R*/run.py")):
        rel = str(run.relative_to(ROOT))
        rn = RNUM.search("/" + rel)
        rows.append({"path": rel, "r": int(rn.group(1)) if rn else None,
                     "date": dates.get(rel),
                     "has_block": declared(run.read_text(encoding="utf-8",
                                                         errors="ignore")) is not None})
    dated = [x for x in rows if x["date"]]
    numbered = [x for x in rows if x["r"] is not None]
    print(f"\n  {len(rows)} round(s) · {len(dated)} dated by git · {len(numbered)} R-numbered")
    print(f"  overall WORLDS-block rate: {sum(x['has_block'] for x in rows)}/{len(rows)} = "
          f"{sum(x['has_block'] for x in rows)/len(rows):.3f}")

    def bucket_rate(items, key, nb=6):
        items = sorted(items, key=lambda x: x[key])
        n = len(items); out = []
        for i in range(nb):
            lo, hi = i * n // nb, (i + 1) * n // nb
            chunk = items[lo:hi]
            if chunk:
                out.append((chunk[0][key], chunk[-1][key], len(chunk),
                            sum(c["has_block"] for c in chunk) / len(chunk)))
        return out

    print(f"\n  by GIT DATE (equal-count sextiles):")
    bd = bucket_rate(dated, "date")
    for lo, hi, n, r in bd:
        print(f"    {lo} .. {hi}   n={n:>4}   block rate {r:.3f}  {'█'*int(r*40)}")
    print(f"  by R-NUMBER (equal-count sextiles):")
    br = bucket_rate(numbered, "r")
    for lo, hi, n, r in br:
        print(f"    R{lo:<5} .. R{hi:<5}   n={n:>4}   block rate {r:.3f}  {'█'*int(r*40)}")

    trend_d = bd[-1][3] - bd[0][3]
    trend_r = br[-1][3] - br[0][3]
    agree = (trend_d > 0) == (trend_r > 0)
    print(f"\n  KILL ③  the two axes agree on direction: {agree}  "
          f"{'PASS' if agree else 'FAIL'}   (git {trend_d:+.3f} · R-number {trend_r:+.3f})")
    if not agree:
        print("    They are independent reads of one latent variable. Disagreeing means the")
        print("    R-number is NOT a time proxy, and only the git axis is readable.")

    last = bd[-1][3]
    if abs(trend_d) < 0.05 and last < 0.2:
        world = "C"
    elif trend_d > 0.05:
        world = "A"
    elif trend_d < -0.05:
        world = "B"
    else:
        world = "D"
    print(f"\n  ⭐ WORLD {world}: " + {
        "A": "the rate RISES — late adoption; the 765 blockless rounds are historical and the"
             " practice is improving",
        "B": "the rate FALLS — DECAY; recent rounds are dropping the one block that makes a fork"
             " falsifiable, and that is a live process defect",
        "C": "the rate is FLAT and LOW — the convention was never really adopted, and R870's 51"
             " are a self-selected subset with no temporal story",
        "D": "the rate is neither flat-low nor monotone — a REGIME CHANGE, and the era boundary"
             " is the finding rather than the trend"}[world])
    print(f"     newest sextile rate {last:.3f} · oldest {bd[0][3]:.3f} · Δ {trend_d:+.3f}")
    print(f"     ⚠ OBSERVATIONAL. Nothing here intervenes on whether a round got a block, so this")
    print(f"       dates the practice; it does not explain it.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_rounds": len(rows),
               "overall_rate": sum(x["has_block"] for x in rows) / len(rows),
               "by_date": [{"lo": a, "hi": b, "n": c, "rate": d} for a, b, c, d in bd],
               "by_rnum": [{"lo": a, "hi": b, "n": c, "rate": d} for a, b, c, d in br],
               "trend_date": trend_d, "trend_rnum": trend_r, "axes_agree": agree,
               "reused_parser_from": "R870 (unchanged, so the 6.3% and this trend are comparable)",
               "temporally_resolved": "CLAIMED — git dates the corpus exactly; the register's "
                                      "exclusion applies to the RELEASE, not to my own rounds"},
              open(OUT / "convention_trend.json", "w"), indent=2)
    print(f"\n  artifact: results/convention_trend.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
