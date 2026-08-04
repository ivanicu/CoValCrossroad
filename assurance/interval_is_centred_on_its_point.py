"""How far off-centre does each published point estimate sit inside its own interval?

`point_and_interval_share_a_source.py` reads the SOURCE and returns 28 candidate rounds whose mean
and interval are built from different variables. That is where to look, not a verdict: a mean taken
from the observed statistic beside a CI from a bootstrap array is correct practice when the
bootstrap is centred on that statistic.

This decides them from data already committed, without opening a single source file:

    offcentre = (point - (lo + hi) / 2) / ((hi - lo) / 2)

Scale-free, needs no reported sd, and reads directly: 0 = perfectly centred, +-1 = sitting on the
bound, |x| > 1 = outside the interval. A centred bootstrap lands near 0 whatever arrays it used. A
mean and an interval that estimate different objects do not.

⚠ WHY THIS ORDERING AND NOT 28 SOURCE READS. R141's own numbers make the case: the check that fails
on `outside the interval` flagged 6 of its 14 raters nodes, while all 14 sat 4.5-9.5 seed-sd off
their centre. The displacement was visible in the committed JSON the whole time; only the threshold
hid it. 28 source reads is a day. This is minutes, and it clears the correct ones outright.

⚠ AND IT IS AN INSTRUMENT, SO IT CARRIES ITS OWN CONTROLS. Positive: R141's `raters` nodes must come
out far off-centre -- a case diagnosed from its own source and annotated in its README. Negative: a
synthetic pair centred by construction must return ~0, and one displaced by construction must not.
g=0: no pairs found is exit 2, never a clean bill.

EXIT
    0  controls hold and the triage is reported
    1  a control misbehaved: the ordering below would be silence
    2  no mean/interval pairs found at all
"""
from __future__ import annotations
import contextlib
import importlib.util
import io
import pathlib
import statistics as st
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOUND = 0.25          # |offcentre| below this is "centred": a correct bootstrap, cleared


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "assurance" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.argv = [name]
    spec.loader.exec_module(m)
    return m


def offcentre(point: float, lo: float, hi: float):
    half = (hi - lo) / 2
    return None if half == 0 else (point - (lo + hi) / 2) / half


def main() -> int:
    with contextlib.redirect_stdout(io.StringIO()):
        coh = _load("artifacts_are_internally_coherent")

    c_centred = offcentre(0.05, 0.04, 0.06)
    c_off = offcentre(0.059, 0.04, 0.06)
    neg_ok = abs(c_centred) < 1e-9 and abs(c_off) > 0.8
    print(f"  synthetic control: centred pair -> {c_centred:+.3f} (want 0), "
          f"displaced pair -> {c_off:+.3f} (want near 1)  {'PASS' if neg_ok else 'FAIL'}")

    with contextlib.redirect_stdout(io.StringIO()):
        r = coh.scan(ROOT)
    pairs = []
    # ⚠ v1 iterated r["outside"] -- the nodes ALREADY flagged as outside their interval. A
    # population pre-filtered to the positives can only return |offcentre| > 1 and can clear
    # NOTHING, which is the opposite failure to a check that cannot fail and just as blind. My
    # claim's unit was "every paired node"; my instrument's was "the violations". `all_pairs` was
    # added to the scanner for exactly this, additively.
    for rid, path, mv, (lo, hi) in r["all_pairs"]:
        oc = offcentre(mv, lo, hi)
        if oc is not None:
            pairs.append((rid, path, oc))
    if not pairs:
        print("  UNRUNNABLE: no mean/interval pairs available. Exit 2, never 0.")
        return 2

    raters = [oc for rid, p, oc in pairs if "R141" in rid and p.endswith(".raters")]
    pos_ok = bool(raters) and min(abs(x) for x in raters) > BOUND
    print(f"  real control: R141's `raters` nodes must sit far off-centre -- {len(raters)} node(s), "
          f"|offcentre| {min(abs(x) for x in raters):.2f}..{max(abs(x) for x in raters):.2f}"
          f"  {'PASS' if pos_ok else 'FAIL'}" if raters else
          "  real control: R141's raters nodes NOT FOUND -> FAIL")

    by_round: dict[str, list[float]] = {}
    for rid, _p, oc in pairs:
        by_round.setdefault(rid, []).append(oc)
    print(f"\n  {len(pairs)} paired nodes across {len(by_round)} round(s), by median |offcentre|\n")
    print(f"    {'round':<34}{'n':>4}{'median':>10}{'max':>9}   reading")
    cleared, flagged = [], []
    for rid in sorted(by_round, key=lambda k: -st.median([abs(x) for x in by_round[k]])):
        v = [abs(x) for x in by_round[rid]]
        med, mx = st.median(v), max(v)
        verdict = "OFF-CENTRE — read the source" if med > BOUND else "centred — cleared without a read"
        (flagged if med > BOUND else cleared).append(rid)
        print(f"    {rid:<34}{len(v):>4}{med:>10.2f}{mx:>9.2f}   {verdict}")

    print(f"\n  cleared by arithmetic: {len(cleared)}   need a source read: {len(flagged)}")
    print("  ⚠ SCOPE, and it is narrow: this only sees pairs the coherence scanner could pair")
    print("    UNAMBIGUOUSLY, and that scanner skips 5,186 nodes because the CI's own stem names")
    print("    another key. A candidate absent from this table is NOT cleared -- it is unpaired,")
    print("    which is a different thing and the one this ordering cannot help with.")

    if not neg_ok or not pos_ok:
        print("\n  DRIFTED: a control misbehaved, so the ordering above would be silence.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
