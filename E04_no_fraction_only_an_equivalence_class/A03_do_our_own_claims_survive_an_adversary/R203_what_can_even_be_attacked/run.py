"""Forty-nine standing claims and one attack. Which of them is the attack even shaped for?

r202 built a calibrated jackknife and four claims now carry it. The obvious next move is "attack
the other 49", and it is wrong: a jackknife answers ONE question -- is this mean carried by a
handful of units -- and most of the claims in this graph are not means. Running it on them would
produce verdicts about quantities that do not exist, which is worse than not running it.

So this is the register the severe-experiment standard asks for: for each standing claim, what
attack its SHAPE admits, and where none applies, what would be required instead. A claim marked
"structurally cannot" is not excused; it is one whose attack is a different thing.

SIX SHAPES, and each takes a different attack:

  MEAN over units          jackknife with calibration.
  RELIABILITY (split-half) seed variation -- the statistic is already a resampling, so the attack
                           is whether the resampling's own spread swamps it.
  GAUGE-DEPENDENT          the claim already concedes the dependence; the attack is gauge
                           variation, and a jackknife answers a question it does not ask.
  COUNT or EXISTENCE       "9,684 criteria have exactly one rater", "the lowest option is used
                           zero times". A jackknife is meaningless. The attack is RE-DERIVATION
                           from the object, which the generated consolidators do on every run.
  PROXY                    the attack is not statistical -- it is whether the proxy implies the
                           property, and in which direction. That is the proxy ledger.
  ASSUMPTION               the memo's premises. Attacked by showing them false, which is design.

I EXPECTED THE REGISTER TO SHRINK THE PROBLEM AND IT DID NOT. The hope was that most "unattacked"
claims would turn out to be counts, re-derived on every consolidator run, leaving a handful that
genuinely need resampling. The count went the other way: the jackknife is shaped for MORE claims
than I assumed, and the honest outstanding number is larger than the one I quoted last round.
Recording that here rather than in a footnote, because a triage that only ever exonerates is not a
triage.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "db"))
OUT = pathlib.Path(__file__).resolve().parent / "results"

import derivation_chain as dc  # noqa: E402

# Shape signatures, checked in order. Each is a claim about the STATEMENT's form, and the first
# match wins -- so the order encodes which attack takes precedence when a claim has two shapes.
# TWO SHAPES AND ONE LOOSER PATTERN ADDED AFTER READING THE RESIDUAL, which is the only honest way
# to shrink an UNCLASSIFIED bucket. The first pass left 27 of 79 unfiled -- a third -- and reading
# them showed the classifier was missing two real kinds and one form of the kind it had:
#   ASSUMPTION      A2/A3/A4/A6 are the memo's stated PREMISES, not findings. No resampling touches
#                   them; their attack is whether the premise is false, which is a design question.
#   GAUGE-DEPENDENT several claims label themselves as depending on the instrument -- "GAUGE-
#                   DEPENDENT, and the drift is four times the effect". Their attack is gauge
#                   variation, and r130/r165 already ran it. A jackknife would be answering a
#                   question the claim has already conceded.
#   MEAN            the pattern required a z or a bracketed CI, so "+0.0439", "0.6563 pairwise
#                   concordance" and "loses 0.0229" all fell through. Bare signed decimals count.
# NULL ADDED AFTER r204, which found the two lowest-z claims in the MEAN bucket were nulls -- and
# that sending a null to a jackknife asks a malformed question, since there is no effect to be
# carried by a handful of units. r202's own tool would return NO RESOLUTION, correctly.
# DETECTED STRUCTURALLY, not by wording: a claim whose stated confidence interval SPANS ZERO is a
# null whatever its prose calls it. Wording alone would have missed "MEASUREMENT ONLY... a clean
# null for that instrument" and over-matched any statement containing the word "no".
_CI = re.compile(r"\[\s*([+-]?\d*\.\d+)\s*,\s*([+-]?\d*\.\d+)\s*\]")


def _ci_spans_zero(stmt):
    for mm in _CI.finditer(stmt):
        lo, hi = float(mm.group(1)), float(mm.group(2))
        if lo <= 0 <= hi:
            return True
    return False


SHAPES = [
    ("ASSUMPTION", re.compile(r"^(A\d|The release aggregates|What a participant says|"
                              r"Aggregating criteria)", re.I),
     "not resampling: a premise is attacked by showing it false, which is a design question"),
    ("GAUGE-DEPENDENT", re.compile(r"GAUGE-DEPENDENT|judge-dependent|drift is|"
                                   r"SIGN-ROBUST, SIGNIFICANCE", re.I),
     "gauge variation -- and the claim has already conceded the dependence, so a jackknife would "
     "answer a question it does not ask"),
    ("RELIABILITY", re.compile(r"Spearman-Brown|split-half|S-B [+-]", re.I),
     "seed variation: the statistic is itself a resampling, so the attack is whether its own "
     "spread swamps the effect"),
    ("MEAN", re.compile(r"z [+-]\d|\[\+?-?\d?\.\d+, ?[+-]?\d?\.\d+\]|paired|DiD|per assessment|"
                        r"of assessments|[+-]0\.\d{3,4}\b|\b0\.\d{4}\b|concordance", re.I),
     "calibrated jackknife: is the mean carried by a handful of units"),
    ("PROXY", re.compile(r"regex|lexical|keyword|proxy|match rule|text match|0\.60 similarity",
                         re.I),
     "proxy ledger: does the measured thing imply the claimed thing, and in which direction"),
    ("COUNT", re.compile(r"exactly (zero|one)|\bzero times\b|\d{1,3},\d{3}|"
                         r"\b\d+ of \d+\b|never|absent|does not ship|no pointer", re.I),
     "re-derivation from the object -- which the generated consolidators already do on every run"),
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = dc.q("SELECT n.id, n.kind, n.name, coalesce(n.statement,''), coalesce(n.status,'') "
                "FROM node n WHERE n.kind IN ('my_claim','fact','their_assumption') "
                "AND n.status <> 'refuted' ORDER BY n.name")
    print(f"standing claims (my_claim / fact / their_assumption, not refuted): {len(rows)}")

    # which already carry a robustness control
    attacked = {nm for (nm,) in dc.q(
        "SELECT d.name FROM edge e JOIN node s ON s.id=e.src JOIN node d ON d.id=e.dst "
        "WHERE e.kind='tested_by' AND s.name LIKE 'robustness-%'")}
    print(f"already carrying a robustness control: {len(attacked)}  {sorted(attacked)}")

    buckets = defaultdict(list)
    for _id, kind, name, stmt, status in rows:
        shape = "UNCLASSIFIED"
        why = "no signature matched; needs reading"
        if _ci_spans_zero(stmt) or re.search(r"clean null|a null\b|neither concentrates|"
                                             r"indistinguishable from zero", stmt, re.I):
            buckets["NULL"].append(
                {"name": name, "kind": kind, "status": status, "attacked": name in attacked,
                 "why": "POWER, not resampling: what effect could this design have detected, "
                        "against the effect that would matter. A null without an MDE or a "
                        "resolution floor is silence reported as evidence."})
            continue
        for lbl, pat, note in SHAPES:
            if pat.search(stmt):
                shape, why = lbl, note
                break
        buckets[shape].append({"name": name, "kind": kind, "status": status,
                               "attacked": name in attacked, "why": why})

    print("\n" + "=" * 96)
    print("THE REGISTER")
    print("=" * 96)
    order = ["MEAN", "NULL", "RELIABILITY", "GAUGE-DEPENDENT", "PROXY", "COUNT", "ASSUMPTION",
             "UNCLASSIFIED"]
    for shape in order:
        items = buckets.get(shape, [])
        if not items:
            continue
        done = sum(1 for i in items if i["attacked"])
        print(f"\n{shape}  ({len(items)} claims, {done} already attacked)")
        print(f"  attack: {items[0]['why']}")
        for i in items:
            mark = "[attacked]" if i["attacked"] else "          "
            print(f"    {mark} {i['name'][:58]:58s} {i['kind']:16s} {i['status']}")

    print("\n" + "=" * 96)
    print("READING")
    print("=" * 96)
    n_mean = len(buckets.get("MEAN", []))
    mean_done = sum(1 for i in buckets.get("MEAN", []) if i["attacked"])
    n_count = len(buckets.get("COUNT", []))
    n_rel = len(buckets.get("RELIABILITY", []))
    n_prox = len(buckets.get("PROXY", []))
    n_unc = len(buckets.get("UNCLASSIFIED", []))
    print(f"  {len(rows)} standing claims:")
    print(f"    {n_mean:2d} MEAN         {mean_done} attacked, {n_mean - mean_done} outstanding "
          f"-- the jackknife applies")
    print(f"    {n_rel:2d} RELIABILITY  the statistic IS a resampling; seed spread is the attack")
    print(f"    {n_prox:2d} PROXY        not a statistical question at all")
    print(f"    {n_count:2d} COUNT        re-derived every time a consolidator runs")
    n_asm = len(buckets.get("ASSUMPTION", []))
    n_gau = len(buckets.get("GAUGE-DEPENDENT", []))
    n_null = len(buckets.get("NULL", []))
    print(f"    {n_null:2d} NULL         power, not resampling -- added by r204 after two nulls")
    print(f"                    were filed as MEANs and would have gone to a malformed check")
    print(f"    {n_gau:2d} GAUGE-DEP    the claim already concedes the dependence")
    print(f"    {n_asm:2d} ASSUMPTION   a premise, not a finding")
    print(f"    {n_unc:2d} UNCLASSIFIED needs reading")
    print(f"\n  THE RESIDUAL WENT 27 -> {n_unc} BY READING IT, not by widening a pattern until it")
    print(f"  swallowed everything. Two shapes were genuinely missing -- premises and")
    print(f"  self-conceded gauge dependence -- and the MEAN pattern had required a z or a")
    print(f"  bracketed CI, so bare effects like '+0.0439' fell through. A classifier tuned until")
    print(f"  nothing is left over is a classifier that has stopped classifying.")
    print(f"\n  'FORTY-NINE UNATTACKED' WAS WRONG IN BOTH DIRECTIONS. The standing set is {len(rows)},")
    print(f"  not 49 -- that figure was the ledger's narrower scope. And the jackknife turns out to")
    print(f"  be shaped for {n_mean} of them, so the outstanding count is {n_mean - mean_done}, "
          f"MORE than the number")
    print(f"  I quoted last round, not fewer.")
    print(f"  I built this register expecting it to shrink the problem -- expecting most claims to")
    print(f"  be counts that every consolidator run re-derives. {n_count} are. A triage that only")
    print(f"  ever exonerates is not a triage, and this one did the opposite of what I wanted.")
    print(f"  What it DOES buy is that {n_rel + n_gau + n_prox + n_asm + n_count} claims now have "
          f"a NAMED attack that is not the")
    print(f"  jackknife, so 'unattacked' stops meaning 'ignored' for them.")
    print(f"\n  WHAT THE REGISTER DOES NOT DO. Classification is by regex over the statement, so a")
    print(f"  claim whose statement omits its own shape lands in UNCLASSIFIED or the wrong bucket.")
    print(f"  That is the same shape-versus-substance limit r197's scanner failed on, and it is")
    print(f"  why the {n_unc} unclassified are listed by name rather than counted and dropped.")
    print(f"  The register is a triage, and a triage that hides its residual is a filter.")

    (OUT / "register.json").write_text(json.dumps(
        {"standing": len(rows), "attacked": sorted(attacked),
         "buckets": {k: v for k, v in buckets.items()},
         "outstanding_for_jackknife": n_mean - mean_done,
         "limit": "regex classification over statements; a claim that omits its shape is "
                  "misfiled, and UNCLASSIFIED is listed rather than dropped"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
