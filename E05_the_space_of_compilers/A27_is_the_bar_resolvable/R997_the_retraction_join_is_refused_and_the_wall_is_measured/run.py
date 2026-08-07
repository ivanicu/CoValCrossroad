#!/usr/bin/env python3
"""R997 — the retraction join is refused, and the wall is measured with its mechanism.

⛔ WHY. R996 bounded the README's finding debt at 504 and said tightening it means joining the
retraction ledger to round ids — "a join between two artifacts neither of which was built to be
joined, and its own control would have to come before its own count." **The control ran first, and
it refuses the join.**

⭐ THE MECHANISM, READ FROM THE OBJECT. The only declared-link format this project has is R954's
header — `<!-- retraction: class=…; claim=R<n>; killed_by=R<n> -->` — and
`assurance/a_retraction_declares_its_class.py:50` sets `FLOOR_ENTRY = 1388` while the ledger's ids
run **236..1387**. The gate prints its own verdict: *"binds from entry 1388 onward … 0 entr(y/ies)
in scope"*, and exits 2 — **empty population, correctly**. So the format has never bound on a single
entry, and there is no ground truth for a round↔retraction link anywhere in the corpus.

ESTIMAND        whether the retraction ledger can be joined to round ids, and if not, the exact
                condition under which it could.
IDENTIFICATION  NOT identified, and that is the finding. A join needs a ground truth to calibrate
                against; there are 0 declared links, so any looser instrument is uncalibrated by
                construction.
SCOPE           population : the 1,149 numbered entries of RETRACTIONS.md, ids 236..1387
                instrument : the R954 header (ground truth) and a loose `\\bR\\d{2,4}\\b` scan
                baseline   : none available — that is the result
                regime     : this repository, today
WORLDS          A THE JOIN IS AVAILABLE   enough entries carry a declared link to calibrate a
                              looser instrument, and 504 can be tightened.
                B THE JOIN IS UNAVAILABLE  no declared links exist, so the loose scan has nothing
                              to be checked against and 504 stands as an upper bound.
                prediction matrix: A -> declared links > 0. B -> 0, with the mechanism named.
KILL            pre-registered: ≥ 20 declared links ⇒ world B dead and the join is attempted.
POSITIVE CTRL   the header regex must MATCH a synthetic entry written in R954's own documented
                format. Without that, "0 declared links" could be a broken pattern rather than an
                absent structure — the difference between silence and a measurement.
NEGATIVE CTRL   the same regex must NOT match an entry with a bare `R123` mention, which is exactly
                what the loose scan would count.
PLACEBO         the ledger's id range must be recoverable independently and must sit below the
                gate's floor — the arithmetic that makes the emptiness structural rather than
                accidental.
NOISE FLOOR     none: counts of a literal pattern.
MULTIPLICITY    both instruments reported, declared and loose, with the ratio between them.
ARTIFACT        results/join_refused.json with this file's source hash.
IMPOSSIBLE      tightening 504 — N/A **on this corpus**, and the reopening condition is exact:
                retraction entry 1388, written with the header R954 already ships a gate for.
                ⚠ AND R951 REPORTED 8 ENTRIES DECLARING A LINK. Today's count under the R954 header
                is 0. Those are probably different instruments — R951 predates R954's format — but
                the discrepancy is NOT resolved here and is recorded as UNVERIFIED rather than
                explained away.
"""
from __future__ import annotations
import hashlib, json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LED = ROOT / "RETRACTIONS.md"
GATE = ROOT / "assurance/a_retraction_declares_its_class.py"
HEADER = re.compile(r"<!--\s*retraction:\s*class=([^;]+);\s*claim=R(\d+);\s*killed_by=R(\d+)\s*-->")
LOOSE = re.compile(r"\bR\d{2,4}\b")
KILL_AT = 20


def main() -> int:
    if not (LED.exists() and GATE.exists()):
        print("  UNRUNNABLE: the ledger or its gate is missing. Exit 2, never 0.")
        return 2
    text = LED.read_text()
    ids = [int(m.group(1)) for m in re.finditer(r"^## (\d+) · ", text, re.M)]
    entries = [e for e in re.split(r"\n(?=## \d+ · )", text) if re.match(r"## \d+ · ", e)]
    floor = int(re.search(r"FLOOR_ENTRY\s*=\s*(\d+)", GATE.read_text()).group(1))
    print(f"LEDGER  {len(entries)} numbered entries, ids {min(ids)}..{max(ids)}")
    print(f"GATE    a_retraction_declares_its_class.py FLOOR_ENTRY = {floor}")

    # ── CONTROLS FIRST. R996's lesson: the control before the count.
    synth = ("## 9999 · a synthetic entry\n"
             "<!-- retraction: class=verdict string is not a computation; claim=R123; "
             "killed_by=R456 -->\nbody\n")
    pos_ok = bool(HEADER.search(synth))
    bare = "## 9998 · another\nthis withdraws what R123 said, in prose\n"
    neg_ok = not HEADER.search(bare) and bool(LOOSE.search(bare))
    plac_ok = max(ids) < floor
    print(f"\n  POSITIVE CONTROL  the header regex matches an entry in R954's documented format: "
          f"{pos_ok}")
    print(f"  NEGATIVE CONTROL  it does NOT match a bare prose mention that the loose scan counts: "
          f"{neg_ok}")
    print(f"  PLACEBO           the ledger's highest id {max(ids)} sits below the gate's floor "
          f"{floor}: {plac_ok} — the emptiness is structural, not accidental")
    ctrl_ok = pos_ok and neg_ok and plac_ok
    if not ctrl_ok:
        print("\n  ⛔ a control failed; the count below would be uninterpretable. Exit 2, never 0.")
        return 2

    declared = [e for e in entries if HEADER.search(e)]
    loose = [e for e in entries if LOOSE.search(e)]
    print(f"\n  DECLARED links : {len(declared)} of {len(entries)}")
    print(f"  LOOSE mentions : {len(loose)} of {len(entries)} ({len(loose)/len(entries):.0%})")
    print(f"  ⚠ the loose instrument fires on {len(loose)/len(entries):.0%} of entries with "
          f"{len(declared)} declared links to calibrate against — uncalibrated BY CONSTRUCTION")

    if len(declared) >= KILL_AT:
        world = (f"A THE JOIN IS AVAILABLE — {len(declared)} declared links, above the registered "
                 f"threshold of {KILL_AT}")
    else:
        world = (f"B THE JOIN IS UNAVAILABLE — {len(declared)} declared links. R954's format binds "
                 f"from entry {floor} and the ledger stops at {max(ids)}, so it has never bound on "
                 f"a single entry. 504 stands as an upper bound.")
    print(f"\n⭐ {world}")
    print(f"\n⭐ REOPENS AT: retraction entry {floor}, written with the header R954 already ships a "
          f"gate for.")
    print("⚠ AND R951 REPORTED 8 ENTRIES DECLARING A LINK; today's count under R954's header is 0.")
    print("   R951 predates R954's format, so these are probably different instruments — but that")
    print("   is NOT resolved here and is recorded as UNVERIFIED rather than explained away.")

    out = HERE / "results" / "join_refused.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git","rev-parse","HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_entries=len(entries), id_min=min(ids), id_max=max(ids), gate_floor=floor,
        n_declared=len(declared), n_loose=len(loose), loose_share=len(loose)/len(entries),
        kill_threshold=KILL_AT,
        controls={"positive_header_matches_documented_format": pos_ok,
                  "negative_header_ignores_prose_mention": neg_ok,
                  "placebo_max_id_below_floor": plac_ok, "all_ok": ctrl_ok},
        world=world, reopens_at_entry=floor,
        unverified="R951 reported 8 entries declaring a link; under R954's header the count is 0. "
                   "R951 predates that format, so probably different instruments — not resolved.",
        upper_bound_stands=504,
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
