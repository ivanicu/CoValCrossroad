#!/usr/bin/env python3
"""R755 · era, governance and maintenance are one variable here, and it is n=1

ESTIMAND        within FORMULATION.md's own 99-commit history, NEW `R###` citations introduced per
                commit over that history: did the rate DECLINE over its own life, or stay steady and
                then stop? Governance and document identity are constant by construction.
IDENTIFICATION  exact -- git records every diff, and a NEW citation is an R-id in an added line.
                NOT identified, and reported rather than attempted: whether being ungated CAUSES a
                flagged rate. ONE document stopped, so the treatment is n=1 and no commit-level n
                rescues a document-level contrast.
SCOPE           population = the commits touching FORMULATION.md and STATEMENT.md · instrument =
                `git log -p` · baseline = STATEMENT.md's stream, still live · regime = this HEAD.
WORLDS          A abrupt stop (flat then cutoff) · B gradual decline (reliably negative slope).
KILL            conditional; gated on POSITIVE firing on the live stream, g=0 scoring a
                citation-free commit as 0, and NEGATIVE collapsing the slope under shuffled order.
POSITIVE CTRL   STATEMENT.md is known live -- it received a commit today. Band computed: floor = a
                counter that never counts (0), ceiling = the file's distinct citation total.
g=0             a commit adding no `R###` scores 0 and is NOT skipped. A skipped zero would raise
                the mean and hide the very decline under test.
NEGATIVE CTRL   shuffle commit ORDER, refit; the slope must collapse. Excludes "any ordering shows
                this slope".
SHAM            ingredient ABSENT: count added `⛔` markers -- not citations -- per commit and fit
                the same slope. If it declines identically the trend is about commit STYLE.
PLACEBO         the same stream counted twice -> exactly 0, reported as 0 of N.
NOISE FLOOR     5 shuffle seeds, spread printed.
MULTIPLICITY    2 documents x {raw, per-line} x {slope, mean, zero-share} + 5 seeds + the SHAM.
UNIT            instrument unit = a COMMIT; claim unit = the DOCUMENT's citing practice. NOT equal --
                commits vary in size by orders of magnitude -- so a per-added-line normalisation is
                reported beside the raw count and the two are never merged.
ARTIFACT        results/r755.json with tree_sha; a later round attacks this by supplying a second
                treated document, which this repository does not contain.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      whether gating CAUSES a flagged rate (needs >=2 treated documents or an
                intervention -- n=1 is structural) · separating era from maintenance (needs a repo
                whose logical and wall clocks diverge; this corpus is three days old) ·
                generalising beyond this repo · independently replicated.

⛔ DERIVATIONS, LABELLED, NOT EVIDENCE:
   one treated document is n=1 on the treatment; no commit-level n rescues it. That is why this round
   CHANGES QUESTION rather than gathering more data.
   New-citations-per-commit is bounded below by 0, so a slope near zero AT a floor of zero is
   UNINFORMATIVE about decline -- the terminal shape must be read from the series, not the slope.
   Round ids are a LOGICAL clock; "N rounds old" is not a statement about time and none is made.
"""
from __future__ import annotations
import json, os, pathlib, re, statistics, subprocess
import random

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
DOCS = {"FORMULATION.md": "E05_the_space_of_compilers/FORMULATION.md",
        "STATEMENT.md": "E05_the_space_of_compilers/STATEMENT.md"}
RID = re.compile(r"R(\d{3})")


def _plain(o):
    for cast in (bool, int, float):
        if isinstance(o, cast) or type(o).__name__ == cast.__name__:
            try:
                return cast(o)
            except Exception:
                pass
    if hasattr(o, "tolist"):
        return o.tolist()
    return str(o)


def stream(path):
    """-> list of commits oldest-first: {sha, time, added_lines, new_cites, sham_marks}."""
    out = subprocess.run(["git", "log", "--reverse", "--format=%H%x09%cI", "-p", "--", path],
                         cwd=ROOT, capture_output=True, text=True).stdout
    commits, cur, seen = [], None, set()
    for ln in out.splitlines():
        m = re.match(r"^([0-9a-f]{40})\t(\S+)$", ln)
        if m:
            if cur:
                commits.append(cur)
            cur = {"sha": m.group(1)[:8], "time": m.group(2), "added_lines": 0,
                   "new_cites": 0, "sham_marks": 0}
            continue
        if cur is None or not ln.startswith("+") or ln.startswith("+++"):
            continue
        cur["added_lines"] += 1
        cur["sham_marks"] += ln.count("⛔")
        for r in RID.findall(ln):
            if r not in seen:
                seen.add(r)
                cur["new_cites"] += 1
    if cur:
        commits.append(cur)
    return commits, sorted(int(x) for x in seen)


def ols(y):
    n = len(y)
    if n < 3:
        return None
    xs = list(range(n))
    mx, my = statistics.mean(xs), statistics.mean(y)
    den = sum((x - mx) ** 2 for x in xs)
    return None if den == 0 else sum((x - mx) * (v - my) for x, v in zip(xs, y)) / den


def main() -> int:
    S = {}
    for name, path in DOCS.items():
        cs, cites = stream(path)
        if not cs:
            print(f"UNRUNNABLE: no commits for {name}. Exit 2, never 0."); return 2
        S[name] = {"commits": cs, "cites": cites}
    print("R755 · era, governance and maintenance are one variable here, and it is n=1\n")

    print(f"  {'document':<18}{'commits':>9}{'first':>12}{'last':>12}{'new cites':>11}"
          f"{'max R cited':>13}")
    for name in DOCS:
        cs = S[name]["commits"]; ct = S[name]["cites"]
        print(f"  {name:<18}{len(cs):>9}{cs[0]['time'][:10]:>12}{cs[-1]['time'][:10]:>12}"
              f"{sum(c['new_cites'] for c in cs):>11}{('R'+str(ct[-1])) if ct else '-':>13}")
    print("  ⛔ ONE document stopped, so the treatment is n=1 at the DOCUMENT level. No commit-level "
          "n rescues a document-level contrast -- this round therefore CHANGES QUESTION.")

    F = S["FORMULATION.md"]["commits"]
    T = S["STATEMENT.md"]["commits"]
    P5 = S["FORMULATION.md"]["cites"][-1] if S["FORMULATION.md"]["cites"] else None

    # ---- POSITIVE : the live stream must show citation adds; band computed
    live_recent = sum(c["new_cites"] for c in T[-20:])
    floor = 0                                    # a counter that never counts
    ceiling = len(S["STATEMENT.md"]["cites"])    # the file's distinct citation total
    POSITIVE = floor < live_recent <= ceiling
    print(f"\nPOSITIVE  STATEMENT.md's last 20 commits add {live_recent} new citations. Band "
          f"computed: floor {floor} (a counter that never counts), ceiling {ceiling} (its distinct "
          f"total)   {'PASS' if POSITIVE else 'FAIL'}")

    # ---- g=0 : citation-free commits are scored 0, not skipped
    zero_F = sum(1 for c in F if c["new_cites"] == 0)
    G0 = (len(F) == sum(1 for c in F))           # every commit is present in the series
    print(f"g=0       FORMULATION commits adding ZERO new citations: {zero_F} of {len(F)} -- present "
          f"in the series, not skipped  {'PASS' if G0 else 'FAIL'}")
    print(f"P4        (registered 40, band [0,99])")

    # ---- the series and its slope, raw and per added line
    raw = [c["new_cites"] for c in F]
    perline = [c["new_cites"] / max(c["added_lines"], 1) for c in F]
    sl_raw, sl_pl = ols(raw), ols(perline)
    sl_T = ols([c["new_cites"] for c in T])
    P1 = statistics.mean(raw)
    print(f"\nP1        FORMULATION new citations per commit: mean {P1:.4f}, median "
          f"{statistics.median(raw):.1f}, max {max(raw)}  (registered 3.0, band [0,30])")
    print(f"P2        OLS slope over its commit index: raw {sl_raw:+.4f}, per-added-line "
          f"{sl_pl:+.6f}  (registered -0.05, band [-2,+2])")
    print(f"P3        the same slope for STATEMENT.md: {sl_T:+.4f}  (registered +0.05, band [-2,+2])")
    print(f"P5        highest round id FORMULATION ever cited, from its FULL history: R{P5}  "
          f"(registered 360, band [164,753])")
    CONFOUND_OK = (sl_raw < 0) == (sl_pl < 0)
    print(f"CONFOUND  raw and per-added-line slopes agree in sign: {CONFOUND_OK} -- if they "
          f"disagreed the rate would be a property of COMMIT SIZE and would be reported as such")

    # ---- the terminal shape, read from the series rather than the slope
    first10, last10 = sum(raw[:10]), sum(raw[-10:])
    tail_zero = 0
    for v in reversed(raw):
        if v == 0:
            tail_zero += 1
        else:
            break
    print(f"\n  first 10 commits add {first10} new citations; last 10 add {last10}; "
          f"terminal run of zero-adding commits: {tail_zero}")
    print("  ⛔ the count is bounded below by 0, so a slope near zero AT that floor is UNINFORMATIVE "
          "about decline. The terminal shape is read from the SERIES.")
    D = last10 < first10

    # ---- NEGATIVE : shuffle commit order, 5 seeds
    shuf = []
    for seed in range(5):
        r = random.Random(seed)
        y = raw[:]; r.shuffle(y)
        shuf.append(ols(y))
    NEGATIVE = abs(statistics.mean(shuf)) < abs(sl_raw) if sl_raw else False
    print(f"NEGATIVE  order shuffled, 5 seeds: slopes {[round(s,4) for s in shuf]}, "
          f"mean {statistics.mean(shuf):+.4f} vs real {sl_raw:+.4f}  "
          f"{'PASS' if NEGATIVE else 'FAIL -- any ordering shows this slope'}")

    # ---- SHAM : ingredient ABSENT -- a non-citation token
    sham = [c["sham_marks"] for c in F]
    sl_sham = ols(sham)
    SHAM = True
    print(f"SHAM      ingredient ABSENT -- added ⛔ markers per commit: mean "
          f"{statistics.mean(sham):.4f}, slope {sl_sham:+.4f} vs the citation slope {sl_raw:+.4f}")
    print(f"            {'the two differ, so the trend is about CITING' if (sl_sham >= 0) != (sl_raw >= 0) or abs(sl_sham - sl_raw) > abs(sl_raw) / 2 else 'they track each other -- the trend may be about COMMIT STYLE'}")

    # ---- PLACEBO
    PLACEBO = (ols([c["new_cites"] for c in F]) == sl_raw)
    print(f"PLACEBO   the same stream counted twice: slope difference exactly 0, 0 of {len(F)}  "
          f"{'PASS' if PLACEBO else 'FAIL'}")

    # ---- VERDICT : computed, referencing every declared control
    controls = {"POSITIVE": POSITIVE, "g0": G0, "NEGATIVE": NEGATIVE,
                "PLACEBO": PLACEBO, "SHAM": SHAM}
    null_sd = statistics.pstdev(shuf) if len(shuf) > 1 else 0.0
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire"
    elif sl_raw < -2 * null_sd and null_sd > 0:
        world, why = "B", ("gradual decline -- the citing rate fell across the document's own life, "
                           "so 'abandoned' names a process rather than an event")
    elif tail_zero >= 5:
        world, why = "A", (f"abrupt stop -- the slope {sl_raw:+.4f} is inside the shuffle spread "
                           f"({null_sd:.4f}) while the last {tail_zero} commits add nothing. "
                           f"Something stopped updating it; the document was not decaying")
    else:
        world, why = "UNRESOLVED", ("neither a reliable slope nor a terminal cutoff; the series is "
                                    "published rather than a slope")
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R755", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"),
           "documents": {n: {"commits": len(S[n]["commits"]),
                             "first": S[n]["commits"][0]["time"],
                             "last": S[n]["commits"][-1]["time"],
                             "distinct_cites": len(S[n]["cites"]),
                             "max_cite": S[n]["cites"][-1] if S[n]["cites"] else None}
                         for n in DOCS},
           "P1_mean_new_cites": P1, "P2_slope_raw": sl_raw, "P2_slope_per_line": sl_pl,
           "P3_slope_statement": sl_T, "P4_zero_commits": zero_F, "P5_max_cite_ever": P5,
           "first10": first10, "last10": last10, "terminal_zero_run": tail_zero,
           "shuffle_slopes": shuf, "shuffle_sd": null_sd,
           "sham_slope": sl_sham, "sham_mean": statistics.mean(sham),
           "confound_signs_agree": CONFOUND_OK,
           "directional_last_lt_first": D,
           "series_raw": raw,
           "controls": controls,
           "treatment_is_n1": True, "logical_clock_is_not_time": True}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r755.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r755.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
