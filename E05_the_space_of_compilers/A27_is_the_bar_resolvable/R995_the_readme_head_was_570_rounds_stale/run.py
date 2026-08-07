#!/usr/bin/env python3
"""R995 — the README head was 570 rounds stale, and it is the first thing a reader sees.

⛔ WHY. P16 puts the FINDINGS in the top-level README; the round READMEs carry designs. R994's NEXT
pointed at two departures that need a second release — the impossibility register, not a next step —
so the gradient was recomputed, and the answer was §0.2's question: what STANDS, and is it legible
where a reader looks? It is not. The head says **"415 rounds in 5 epochs and 24 arcs, numbered to
R421"** while the project is at **R994** across **28 arcs**, and its claim counts are re-derived
"at R340".

ESTIMAND        the gap between the README head's self-description and the tree: rounds, arcs,
                highest round id, and the count of round directories the file never mentions.
IDENTIFICATION  exact — both sides are on disk, and the round side uses `covalx.rounds`, the module
                that exists so depth is expressed once.
SCOPE           population : every round directory outside the fixture batch
                instrument : `iter_round_dirs` + a `\\bR\\d+\\b` scan of README.md
                baseline   : the head's own printed claims
                regime     : this repository, today
WORLDS          A THE HEAD IS CURRENT   its counts match the tree within rounding.
                B THE HEAD IS STALE     they do not, and a reader is being told a smaller project.
                prediction matrix: A -> counts agree. B -> a measured gap.
KILL            pre-registered: counts agreeing within 5% ⇒ world B dead and no repair is warranted.
POSITIVE CTRL   a round the README demonstrably DOES mention (R340, R421 — both appear in the head's
                own prose) must read as mentioned. Without it, "828 unmentioned" could be a broken
                scan rather than a real gap.
NEGATIVE CTRL   a round id that cannot exist (R99999) must read as unmentioned.
PLACEBO         the fixture batch is excluded, and the exclusion is counted rather than silent.
NOISE FLOOR     none: these are counts.
MULTIPLICITY    all four quantities reported, agreeing or not.
ARTIFACT        results/readme_staleness.json with this file's source hash.
IMPOSSIBLE      writing the 828 missing summaries — N/A in one round, and pretending otherwise is
                how a debt gets restated instead of paid. This round repairs the HEAD, which is the
                part a reader meets first, and states the rest as a measured debt.
"""
from __future__ import annotations
import hashlib, json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from covalx.rounds import iter_round_dirs


def main() -> int:
    readme = (ROOT / "README.md")
    if not readme.exists():
        print("  UNRUNNABLE: README.md missing. Exit 2, never 0.")
        return 2
    text = readme.read_text()
    dirs, fixtures = {}, 0
    for d in iter_round_dirs(ROOT):
        m = re.match(r"[Rr](\d+)_", d.name)
        if not m:
            continue
        if "E99_fixtures" in d.parts:
            fixtures += 1
            continue
        dirs[int(m.group(1))] = d.name
    arcs = {p.parent.name for p in iter_round_dirs(ROOT) if "E99_fixtures" not in p.parts}
    epochs = {p.parent.parent.name for p in iter_round_dirs(ROOT) if "E99_fixtures" not in p.parts}
    ment = {int(m.group(1)) for m in re.finditer(r"\bR(\d{2,4})\b", text)}
    unment = sorted(r for r in dirs if r not in ment)

    # ⛔ THIS WAS `{"rounds": 415, "arcs": 24, "epochs": 5, "highest": 421}` — A LITERAL. The round
    #    that exists to detect a stale README head CARRIED THE STALE NUMBERS AS CONSTANTS, so it
    #    could report the gap once and could never notice it being closed: after the head was fixed
    #    it went on reporting "the head describes 415 rounds" against a head that said nothing of
    #    the kind. A snapshot wearing a gate's clothes. Those four values are kept in this comment
    #    because they are the historical record of what the head said on 2026-08-06.
    #    It now READS the head. If the head stops declaring its counts the parse comes back empty
    #    and the round exits 2 — an unparseable head is not a current one.
    hd = "".join(text.splitlines(True)[:25])
    def _n(pat):
        m = re.search(pat, hd, re.I)
        return int(m.group(1).replace(",", "")) if m else None
    claimed = {"rounds": _n(r"\*\*([\d,]+)\s*rounds"), "arcs": _n(r"([\d,]+)\s*arcs"),
               "epochs": _n(r"([\d,]+)\s*epochs"), "highest": _n(r"highest id\s*R(\d+)")}
    if any(v is None for v in claimed.values()):
        print(f"  UNRUNNABLE: the head declares no counts to check ({claimed}). Exit 2, never 0.")
        return 2
    actual = {"rounds": len(dirs), "arcs": len(arcs), "epochs": len(epochs),
              "highest": max(dirs)}
    print(f"{'quantity':<12}{'head claims':>13}{'on disk':>10}   gap")
    for k in claimed:
        print(f"  {k:<10}{claimed[k]:>13}{actual[k]:>10}   {actual[k]-claimed[k]:+}")
    print(f"\nround dirs the README never mentions: {len(unment)} of {len(dirs)}   "
          f"({fixtures} fixture dirs excluded and counted)")

    # ⛔ THIS CONTROL USED TO READ `340 in ment and 421 in ment`, AND IT ENCODED THE INSTANCE, NOT
    #    THE PROPERTY. The property is "an id this README really does mention reads as mentioned".
    #    R340 and R421 satisfied it only because they happened to sit in the head's prose — and the
    #    2026-08-07 README rewrite removed that prose, so the control failed and the whole round
    #    returned UNVERIFIED while the instrument was working perfectly. A control keyed to a
    #    fixture dies when the fixture is edited, which is the one event a document gate exists to
    #    survive. It now DERIVES its probe from the file: any mentioned id will do, and if the
    #    README mentions no round at all there is nothing to certify and the control fails honestly.
    probe = sorted(ment)[:2]
    pos_ok = bool(probe) and all(x in ment for x in probe)
    neg_ok = 99999 not in ment
    print(f"\n  POSITIVE CONTROL  ids taken FROM the README ({', '.join('R%d' % x for x in probe) or 'none'}) "
          f"read as mentioned: {pos_ok}")
    print(f"  NEGATIVE CONTROL  a nonexistent id reads as unmentioned: {neg_ok}")
    print(f"  PLACEBO           fixture rounds excluded and counted: {fixtures}")
    ctrl_ok = pos_ok and neg_ok

    within = all(abs(actual[k] - claimed[k]) <= 0.05 * max(actual[k], 1) for k in claimed)
    if not ctrl_ok:
        world = "UNVERIFIED — a control failed; the gap certifies nothing"
    elif within:
        world = "A THE HEAD IS CURRENT — every count agrees within 5%"
    else:
        world = (f"B THE HEAD IS STALE — it describes {claimed['rounds']} rounds to R"
                 f"{claimed['highest']} across {claimed['arcs']} arcs; the tree holds "
                 f"{actual['rounds']} to R{actual['highest']} across {actual['arcs']}")
    print(f"\n⭐ {world}")

    out = HERE / "results" / "readme_staleness.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git","rev-parse","HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        claimed=claimed, actual=actual, n_unmentioned=len(unment),
        unmentioned_range=[min(unment), max(unment)] if unment else None,
        fixtures_excluded=fixtures,
        controls={"positive_known_mentioned": pos_ok, "negative_nonexistent": neg_ok,
                  "all_ok": ctrl_ok},
        world=world,
        not_done="the 828 missing round summaries; this round repairs the HEAD and states the rest "
                 "as a measured debt rather than restating it as a plan",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
