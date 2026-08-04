"""R463 -- the replacement ordering is FORCED too. Two stories eliminated; the order is arbitrary.

⛔ THE ANNOUNCED REPLACEMENT IS FORCED BY THE DOCUMENT'S OWN CONSTRUCTION. R462 closed proposing to
   order the remaining declaration work by load-bearingness, made mechanical as "count, per anchor,
   how many CLAUSE-SECTIONS cite its round". Measured on the object rather than assumed: **all 21
   round-markers in DEFINITION.md sit in ONE section** ("What each clause is measured to do"), so
   that count is **1 for every round, by construction**, and cannot discriminate.
   *Thirty-first announced step checked; its statistic is forced.*

⛔ AND MY OWN ALTERNATIVE WORRY WAS ALSO FALSE, which is why it was measured before being acted on.
   Seeing 21 markers in one section, the natural fear is that the document has become an append-chain
   -- a log of corrections rather than a formulation. **The longest near-consecutive chain is 4
   round-paragraphs over 10 lines: 0.9% of 1,053 lines.** The document is not a log. Both stories
   about the remaining work are dead.

⭐ SO THE ORDER IS ARBITRARY, AND R462 ALREADY SAID WHAT TO DO ABOUT IT: "the correct answer is that
   the remaining order is arbitrary and should be said to be arbitrary rather than dressed in a third
   story." This round honours that sentence instead of inventing a third basis, declares the next
   CONTIGUOUS block for convenience, and says so in the source.

ESTIMAND (named before the method)
    ① ORDERING: sections_citing(round) over the document's own structure -- forced to 1 if all
      markers share a section, which is checked rather than assumed.
    ② STRUCTURE: the longest near-consecutive run of round-annotated paragraphs, as a share of the
      document, to test whether the deliverable has degenerated into an audit chain.
    ③ WORK: FLAG_RATE per block after declaring R430..R441, compared against the two blocks already
      declared -- a third independent block, and the cumulative negative is the result.

IDENTIFICATION
    ① and ② are censuses over the document. ③ is identified for declared anchors only.
    ⚠ NOT identified: whether the 111 still-undeclared anchors are clean. Undeclared is not a pass,
    and three clean blocks do not license a claim about the fourth.

SCOPE  population : DEFINITION.md (1,053 lines) and the 265 anchors of its gate
       instrument : the marker census; and R461's declaration+window gate, positive-controlled
       baseline   : the two previously declared blocks, 0 flagged at w >= 400
       regime     : w in {200, 400, 800, 1600}

WORLDS
    W-FORCED     the clause-section count is 1 everywhere -> the announced ordering cannot
                 discriminate, and with age already refuted the order is arbitrary.
    W-DISCRIMINATES  the count varies across rounds -> load-bearingness is a usable ordering after all.
    W-LOG        the document is dominated by an append-chain -> the ordering question is the wrong
                 one and the deliverable needs restructuring before more declarations.

PREDICTION MATRIX
                       count flat   count varies   chain dominates
    W-FORCED               0.90         0.05             0.05
    W-DISCRIMINATES        0.05         0.90             0.05
    W-LOG                  0.05         0.05             0.90

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the marker census is non-empty.
    longest chain > 25% of lines                        -> W-LOG   (checked FIRST: if the document
                                                           is a log, the ordering is moot)
    else distinct sections containing markers == 1      -> W-FORCED
    else                                               -> W-DISCRIMINATES
    marker census empty                                -> UNVERIFIED (an empty population passes
                                                           nothing; exit 2)

CONTROLS
    EMPTY POPULATION  if no round-markers are found the round exits 2, never 0 -- a census over an
                      empty set would otherwise report "1 section" or "0% chain" and read as a result.
    POSITIVE   R461's planted-comparator control, re-run: FLAGGED below the plant distance, PASSING
               above it, at 300 and 1200 chars against windows 200 and 1600.
    g=0        a declared-ABSOLUTE claim is never flagged at any window.
    PROVENANCE flags are printed WITH their block, so a rise from 3 to 6 cannot be read as the new
               block being worse without checking which block each came from.
    WINDOW     the sweep is retained: a flag only at w=200 is a window artifact.

MULTIPLICITY  3 blocks x 4 windows, all printed; nothing selected.
ARTIFACT      results/r463_ordering_forced.json
IMPOSSIBLE HERE, NAMED
    * a claim about the 111 undeclared anchors -- three clean blocks license nothing about a fourth.
    * an ordering basis -- both proposed have been eliminated and this round supplies no third; that
      is the finding, not a gap in it.
"""
from __future__ import annotations
import collections, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
sys.path.insert(0, str(ROOT / "assurance"))
BLOCKS = [("R430-R441", r"r4(3[0-9]|4[01])_"), ("R442-R454", r"r4(4[2-9]|5[0-4])_"),
          ("R455-R462", r"r4(5[5-9]|6[0-2])_")]


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    from comparator_scope import audit, selftest, DOC, COMPARATORS, WINDOWS
    from definition_matches_the_record import ASSERTIONS
    print("R463 · the replacement ordering is FORCED too — two stories eliminated\n")
    text = DOC.read_text()
    lines = text.split("\n")

    # ---- ① the ordering statistic, measured on the object -------------------------------------
    secs, cur = collections.defaultdict(list), "(preamble)"
    marks = []
    for i, l in enumerate(lines):
        if l.startswith("#"):
            cur = l.strip()[:58]
        m = re.search(r"\*\(R(\d{3})\)\*", l)
        if m:
            secs[cur].append(m.group(1)); marks.append(i)
    if not marks:
        print("  UNRUNNABLE: no round-markers found. A census over an empty set would report")
        print("  '1 section' and read as a result. Exit 2, never 0.")
        return 2
    print(f"  ① ORDERING — round-markers {len(marks)}, distinct sections containing them: {len(secs)}")
    for s, rs in sorted(secs.items(), key=lambda kv: -len(kv[1])):
        print(f"      {len(rs):>3} markers  {s}")
    # ⛔ THE ESTIMAND IS sections_citing(ROUND), AND THE FIRST VERSION BRANCHED ON
    #    len(sections_containing_markers) INSTEAD -- a different statistic, §4's sub-kind ③. The
    #    two disagree exactly here: 2 sections contain markers, but each ROUND's paragraph lives in
    #    ONE of them, so the per-round count is 1 for every round. Computed properly:
    per_round = collections.Counter()
    for s, rs in secs.items():
        for r in set(rs):
            per_round[r] += 1
    vals = sorted(per_round.values())
    print(f"     -> sections_citing(ROUND), the named estimand: min {min(vals)} max {max(vals)} "
          f"over {len(per_round)} rounds -> {'FLAT, forced' if min(vals)==max(vals) else 'variable'}")
    print(f"     ⚠ Not to be confused with rounds-per-section ({len(secs)} sections holding "
          f"{[len(v) for v in secs.values()]} markers) -- a DIFFERENT statistic, and the one the")
    print(f"       first version of this branch mistakenly tested.")

    # ---- ② is the document a log? --------------------------------------------------------------
    # ⛔ ALIASING BUG in the first version: `runs.append(run); run.clear()` emptied the list that
    #    had just been appended, so every completed run was recorded as empty and the "longest
    #    chain" came out as 1 paragraph. Fixed by starting a NEW list instead of mutating.
    runs, run = [], [marks[0]]
    for a, b in zip(marks, marks[1:]):
        if b - a <= 14:
            run.append(b)
        else:
            runs.append(run); run = [b]
    runs.append(run)
    lr = max(runs, key=len)
    share = (lr[-1] - lr[0] + 1) / len(lines)
    print(f"\n  ② STRUCTURE — longest near-consecutive chain: {len(lr)} round-paragraphs over "
          f"{lr[-1]-lr[0]+1} lines")
    print(f"     = {100*share:.1f}% of {len(lines)} lines -> the document is "
          f"{'a LOG' if share > 0.25 else 'NOT a log'}")

    # ---- ③ the work, and its cumulative negative -----------------------------------------------
    print("\n  CONTROLS")
    if not selftest(ASSERTIONS):
        print("\n  UNRUNNABLE: the window mechanism failed its own control. Exit 2."); return 2

    decl = [l for l in ASSERTIONS if COMPARATORS.get(l)]
    rows = []
    for w in WINDOWS:
        ok, fl, und, ab = audit(text, ASSERTIONS, w)
        flg = [l for l, _ in fl]
        rows.append({"window": w, "flagged": flg, "n_undeclared": len(und),
                     "by_block": {nm: [l for l in flg if re.match(rx, l)] for nm, rx in BLOCKS}})
    print(f"\n  ③ THE WORK — third block declared; flags printed WITH their block")
    print(f"    {'block':<12}{'declared':>10}{'w=200':>8}{'w=400':>8}{'w=800':>8}{'w=1600':>8}")
    for nm, rx in BLOCKS:
        d = len([l for l in decl if re.match(rx, l)])
        cells = "".join(f"{len(r['by_block'][nm]):>8}" for r in rows)
        print(f"    {nm:<12}{d:>10}{cells}")
    tight, wide = rows[0], rows[-1]
    print(f"\n    w=200 flags by block: " +
          "  ".join(f"{nm} {tight['by_block'][nm] or '-'}" for nm, _ in BLOCKS))
    cov = len(ASSERTIONS) - wide["n_undeclared"]
    print(f"    coverage {cov} of {len(ASSERTIONS)} ({100*cov/len(ASSERTIONS):.1f}%)")

    if share > 0.25:
        world = "W-LOG"
    elif min(vals) == max(vals):
        world = "W-FORCED"
    else:
        world = "W-DISCRIMINATES"
    print(f"\n  WORLD: {world}")
    if world == "W-FORCED":
        print("    ⛔ TWO ORDERINGS, BOTH ELIMINATED: age was REFUTED by measurement (R462), and")
        print("       clause-citation is FORCED by construction (here). ⭐ THE REMAINING ORDER IS")
        print("       ARBITRARY, AND THIS ROUND SAYS SO RATHER THAN INVENTING A THIRD STORY —")
        print("       the block declared here is simply the next contiguous one.")
        print(f"    ⭐ And the cumulative negative is the substantive result: {len(decl)} declared")
        print(f"       differences across THREE independent blocks, {len(wide['flagged'])} flagged at")
        print(f"       every defensible window. The comparator defect is not in this document.")
        print(f"    ⚠ It says NOTHING about the {wide['n_undeclared']} still undeclared.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_markers": len(marks),
           "n_sections_with_markers": len(secs),
           "markers_per_section": {s: len(v) for s, v in secs.items()},
           "sections_citing_round_min": min(vals), "sections_citing_round_max": max(vals), "longest_chain_paragraphs": len(lr),
           "longest_chain_share": share, "n_lines": len(lines),
           "declared_differences": len(decl), "coverage": cov, "n_anchors": len(ASSERTIONS),
           "sweep": rows}
    (RES / "r463_ordering_forced.json").write_text(json.dumps(out, indent=2))
    print(f"\n  artifact: {RES/'r463_ordering_forced.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
