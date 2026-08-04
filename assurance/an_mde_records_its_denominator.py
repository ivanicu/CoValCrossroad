"""A round that computes an MDE over AGGREGATED UNITS must record how many units it averaged.

R373 measured why this gate exists. The MDE this campaign uses is `ZEFF * sd / sqrt(k)`, and the
sampling distribution of a k-unit sd estimate is chi_{k-1}/sqrt(k-1): at k=2 it lands below HALF its
true value 38.3% of the time, at k=4 13.9%, at k=8 2.8%. A `RESOLVED` verdict from a collapsed
denominator is indistinguishable in the artifact from a real one -- unless k is recorded. R373 found
R368's transport MDE, which DEFINITION.md cites, averaged FOUR strata, and could only find that out
by reading R368's source and then hand-tracing a path into its JSON.

⛔ WHY A WORD LIST IS LEGITIMATE HERE AND WAS NOT IN R373. R373 tried to MEASURE how many past
   rounds record their denominator, using a whitelist of key names. That is invalid: a guessed list
   cannot prove an absence, and R355 and R368 were both false negatives. This gate does something
   different in kind -- it SPECIFIES the acceptable names going forward. A specification cannot be
   wrong about absence, because it defines what counts. The same list is invalid as a measurement
   and valid as a convention, and that distinction is the whole reason this file can exist.

WHAT IS ENFORCED. A round whose source computes `ZEFF * <sd> / math.sqrt(<denominator>)` where the
denominator counts AGGREGATED UNITS (strata, arms, cells, references, contrasts) must write, into
its artifact, a key from the canonical set below holding that count.

Rounds whose denominator is the SAMPLE SIZE are not in scope: a paired difference over 968 prompts
has 967 df and does not collapse. The distinction is the denominator's referent, not its size.

RATCHET, not a gate: the debt list is frozen. It fails on new drift AND on a listed entry becoming
compliant, because a debt list that silently keeps satisfied entries stops measuring anything.

EXIT
    0  no new violation
    1  a violation, or a frozen entry that is now compliant and must be removed
    2  the population is empty -- never a silent pass
"""
from __future__ import annotations
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = pathlib.Path(__file__).resolve().parent
DEBT = HERE / "KNOWN_MDE_WITHOUT_DENOMINATOR.json"

CALL = re.compile(r"ZEFF\s*\*\s*(?P<sd>[^/\n]+?)\s*/\s*math\.sqrt\(\s*(?P<den>[^)]*\([^)]*\)[^)]*|[^)]*)\)")
# the denominator counts AGGREGATED UNITS rather than the sample
AGGREGATED = re.compile(r"len\(\s*(c|con_|contrasts|conts|exc_all|arms|cells|refs|strata|units)\b",
                        re.I)
# ⛔ SPECIFICATION, not a measurement: these are the names a round MAY use. `k` is excluded because
#   in this campaign it means CORE SIZE -- R301 stores k=4 beside an MDE over 968 prompts.
CANONICAL = ("n_units", "kept", "n_strata", "n_pairs_pooled", "n_terms", "denominator_n",
             "n_contrasts", "n_arms", "n_cells")


def keys_of(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.add(str(k)); keys_of(v, out)
    elif isinstance(obj, list):
        for v in obj[:200]:
            keys_of(v, out)
    return out


def scan():
    """-> (violations, compliant_rounds, n_sources_read, n_aggregated_sites)"""
    viol, ok, nsrc, nsite = [], [], 0, 0
    for f in sorted(ROOT.glob("E0*/*/*/*.py")):
        try:
            txt = f.read_text()
        except Exception:
            continue
        nsrc += 1
        hits = [m for m in CALL.finditer(txt) if AGGREGATED.search(m.group("den"))]
        if not hits:
            continue
        nsite += len(hits)
        rel = f.relative_to(ROOT)
        rnd = str(rel).split("/")[2].split("_")[0]
        names = set()
        for a in ROOT.glob(f"E0*/*/{rnd}_*/results/*.json"):
            try:
                keys_of(json.loads(a.read_text()), names)
            except Exception:
                continue
        if names & set(CANONICAL):
            ok.append(rnd)
        else:
            viol.append(dict(round=rnd, file=str(rel), sites=len(hits),
                             dens=sorted({m.group("den").strip() for m in hits})))
    return viol, sorted(set(ok)), nsrc, nsite


def positive_control():
    """The gate must FLAG a source that computes an aggregated-unit MDE, and must NOT flag a
    sample-size one. Both strings are known independently of the scan above.

    ⚠ Exercises the SAME two regexes the scan rules with, not a restatement of them -- the failure
      this campaign logged four times is a control that re-implements the check it validates.
    """
    bad = "mde = ZEFF * sd / math.sqrt(len(contrasts))\n"
    good = "mde = ZEFF * d.std(ddof=1) / math.sqrt(N)\n"
    fb = [m for m in CALL.finditer(bad) if AGGREGATED.search(m.group("den"))]
    fg = [m for m in CALL.finditer(good) if AGGREGATED.search(m.group("den"))]
    empty = [m for m in CALL.finditer("x = 1\nprint('nothing')\n")]
    return (len(fb) == 1), (len(fg) == 0), (len(empty) == 0)


def main() -> int:
    print("  an MDE over AGGREGATED UNITS must record how many units it averaged\n")
    p_flags, p_spares, p_empty = positive_control()
    print(f"    POSITIVE CONTROL  an aggregated-unit estimator is FLAGGED: "
          f"{'PASS' if p_flags else 'FAIL'}")
    print(f"    NEGATIVE CONTROL  a sample-size estimator is NOT flagged:  "
          f"{'PASS' if p_spares else 'FAIL'}")
    print(f"    EMPTY CONTROL     a source with no estimator yields none:  "
          f"{'PASS' if p_empty else 'FAIL'}")
    if not (p_flags and p_spares and p_empty):
        print("\n  UNVERIFIED — the gate's own controls failed. It certifies nothing. Exit 1.")
        return 1

    viol, ok, nsrc, nsite = scan()
    if nsrc == 0:
        print("\n  EMPTY POPULATION: no round source was read. Exit 2, never 0.")
        return 2
    if nsite == 0:
        print(f"\n  EMPTY POPULATION: {nsrc} sources read and NOT ONE computes an MDE over")
        print(f"  aggregated units. The gate examined nothing. Exit 2, never 0.")
        return 2

    frozen = set(json.loads(DEBT.read_text())["rounds"]) if DEBT.exists() else set()
    print(f"\n    {nsrc} sources read · {nsite} aggregated-unit MDE call sites · "
          f"{len(ok)} rounds compliant, {len(viol)} not")
    for v in viol:
        mark = "frozen" if v["round"] in frozen else "NEW"
        print(f"      {mark:>6}  {v['round']:>6}  {v['sites']} site(s)  {v['dens']}")
    if ok:
        print(f"    compliant: {ok}")

    new = [v for v in viol if v["round"] not in frozen]
    now_ok = sorted(frozen & set(ok))
    seen = {v["round"] for v in viol}
    gone = sorted(r for r in frozen if r not in seen and r not in set(ok))

    rc = 0
    if new:
        print(f"\n  FAIL: {len(new)} round(s) compute an MDE over aggregated units without")
        print(f"  recording the count. Write one of {CANONICAL[:4]}... into the artifact.")
        for v in new:
            print(f"    {v['file']}  {v['dens']}")
        rc = 1
    if now_ok:
        print(f"\n  FAIL (shrink-only): {now_ok} now RECORD their denominator and must be removed")
        print(f"  from the frozen list. A debt list that keeps satisfied entries stops measuring.")
        rc = 1
    if gone:
        print(f"\n  NOTE: {gone} are frozen but no longer have an aggregated-unit call site at all")
        print(f"  (rewritten or removed). Not a failure; remove them at the next edit.")

    if rc == 0:
        print(f"\n  PASS: every aggregated-unit MDE outside the frozen debt list records its")
        print(f"  denominator. Frozen debt: {len(frozen)}.")
    print(f"\n  PROXY LEDGER — this enforces that a count is WRITTEN, never that it is CORRECT.")
    print(f"    A round can record `n_units` and compute the MDE over something else entirely.")
    print(f"    What it makes impossible is publishing a resolution verdict whose denominator")
    print(f"    count cannot be read back at all, which is the state R373 measured.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
