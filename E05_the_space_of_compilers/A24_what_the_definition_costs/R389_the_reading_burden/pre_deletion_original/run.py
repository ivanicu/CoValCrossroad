"""R389 -- three units paid; and the instrument I reached for measured my own habit.

R388 paid one unit of the backfill debt and priced the cheap half exactly: 21.3s of machine time.
Its NEXT proposed paying two more and recording "where the time goes -- reading the docstring,
reading the output, deciding the sentence".

⛔ THAT IS ME TIMING MY OWN ATTENTION, AND IT IS UNVERIFIABLE. A self-reported split of my own
   reading time cannot be checked by anyone -- the same class of claim R385, R386 and R387 each
   refused. Replaced by a property of the OBJECT:

       does the round STATE its own finding, or must one be constructed for it?

   If it states one, writing the backfilled row is READING. If it does not, the row is a
   RECONSTRUCTION, which is where a plausible wrong sentence comes from.

⛔⛔ AND THIS ROUND WAS WRITTEN TWICE, because the first copy was DESTROYED BY MY OWN TOOLING.
   Running every `assurance/*.py` in a bulk loop executes `_isolated.py`, whose selftest plants a
   saboteur that deletes an epoch directory. It ran against the LIVE TREE: 1,408 tracked files
   deleted, plus every UNCOMMITTED file -- which was this round's entire directory and the two
   backfilled README rows. `git restore` recovered the 1,408. It recovered none of the untracked
   work, because git cannot restore what it was never given.
   **The only work that survived was the work that had been committed.** R388 survived; R389 did
   not. That is the cost of running a destructive selftest through a convenience loop, and it is
   recorded here rather than quietly re-done.

WHAT WAS PRODUCED: two more units paid. R24_regime_receipt and R28_multiplicative now carry
backfilled rows -- 5 rows over 3 rounds, 24 numbers, every one verified against a fresh run by the
gate R388 built.
⭐ R28's is a NEGATIVE finding -- the additive decomposition is demonstrably misspecifiable AND the
   multiplicative alternative is not thereby established -- the harder kind to backfill and the kind
   most worth having, because an unresolved question left unstated reads as settled.

⛔ ARITHMETIC TRAP, answered before the run. Could the structure share come out otherwise? YES:
   these rounds span months and several conventions, and nothing guarantees a shared format. What
   IS partly forced and is controlled: any marker list is a search instrument, so it gets a positive
   control on rounds whose answer I know by having read them.

ESTIMAND        (a) over every round with an artifact and no finding site: does its run.py docstring
                    open with a TITLED first line naming what the round is for?
                (b) for the three units paid: wall-clock, output lines, self-stated verdict.
                (a) is a census; (b) is n = 3, three observations.

IDENTIFICATION  (a) exact -- `ast` plus one anchored pattern. NOT identified: whether a titled
                docstring is TRUE of its code. R380 found a gate whose docstring described the
                opposite of what it did.

SCOPE           population: rounds with an artifact, a run.py, no finding site, excluding this
                session's own A24 rounds · instrument: ast.get_docstring + an anchored title
                pattern · regime: HEAD.

WORLDS
  W-FORMAT-SHARED  >= 80% titled: the sentence is READ, the burden is bounded, this is a project.
  W-FORMAT-ABSENT  <= 30%: each unit is a reconstruction and the debt is a permanent condition.
  W-SPLIT          between: two tiers with different unit costs, and the counts are the estimate.

PRE-REGISTERED KILL -- conditional on the controls, never on the share alone.
    if title_positive_control_ok and title_negative_control_ok:
        f = share titled
        if f >= 0.80 -> W-FORMAT-SHARED ; elif f <= 0.30 -> W-FORMAT-ABSENT ; else -> W-SPLIT
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  TITLE (+)   R21, R24, R28 -- the three units paid, whose docstrings I have READ -- must all be
              titled. Their answer is known independently of the pattern. ⛔ THIS CONTROL KILLED MY
              FIRST INSTRUMENT: a marker list of ESTIMAND / WORLDS / KILL -- the headings I write
              TODAY -- scored them 1, 0 and 0. I had excluded this session's rounds for that exact
              bias and then built the instrument out of the same habit. Reading the docstrings gave
              the corpus's real convention instead.
  TITLE (-)   a file with no docstring must be untitled and score zero markers.
  SELF        this session's A24 rounds excluded -- written to my format by me.
  EMPTY       fewer than 50 population rounds -> exit 2.

MULTIPLICITY    one census, both tiers printed. SEEDS none -- static parsing.
ARTIFACT        results/r389_reading_burden.json with the source hash.

IMPOSSIBLE HERE
  whether a docstring is TRUE of its code -- structure is checkable, truth is not.
  my own attention time                   -- unverifiable by anyone.
  a second release                        -- one release.

EXIT  0 controls hold · 1 a control misbehaved · 2 the population is too small
"""
from __future__ import annotations
import ast, hashlib, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
A24 = HERE.parent
TITLE = re.compile(r"^\s*r?\d+\s*[-–—]{1,2}\s*\S.*", re.I)
MARKERS = ("ESTIMAND", "CLAIM CARD", "WORLDS", "KILL", "POSITIVE CONTROL", "POSITIVE CTRL",
           "SCOPE", "IDENTIFICATION", "VERDICT")
POS = ("R21_donor_distance", "R24_regime_receipt", "R28_multiplicative")
PAID = {"R21_donor_distance": dict(wall_s=21.3, out_lines=25, self_verdict=True),
        "R24_regime_receipt": dict(wall_s=2.0, out_lines=20, self_verdict=True),
        "R28_multiplicative": dict(wall_s=36.0, out_lines=39, self_verdict=True)}
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp
except Exception:
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}


def parse(src: str):
    try:
        doc = ast.get_docstring(ast.parse(src)) or ""
    except SyntaxError:
        return None, False, 0
    first = doc.splitlines()[0] if doc.splitlines() else ""
    return doc, bool(TITLE.match(first)), sum(1 for m in MARKERS if m in doc)


def main() -> int:
    root_txt = (ROOT / "README.md").read_text()
    pop = []
    for d in sorted(ROOT.glob("E0*/A*/R*")):
        if not d.is_dir() or d == HERE:
            continue
        if d.parent == A24 and d.name[:4] in ("R370", "R371", "R372", "R373", "R374", "R375",
                                              "R376", "R377", "R378", "R379", "R380", "R381",
                                              "R382", "R383", "R384", "R385", "R386", "R387",
                                              "R388", "R389"):
            continue
        if (d / "README.md").exists() or d.name in root_txt:
            continue
        if not (d / "results").is_dir() or not (d / "run.py").exists():
            continue
        pop.append(d)
    if len(pop) < 50:
        print(f"  UNRUNNABLE: only {len(pop)} population rounds. Exit 2, never 0."); return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R389 · is the sentence READ from the round, or invented for it?   HEAD {head}\n")
    print(f"  ⛔ THIS ROUND WAS WRITTEN TWICE. Running every assurance/*.py in a bulk loop executes")
    print(f"     `_isolated.py`, whose selftest plants a saboteur that deletes an epoch directory.")
    print(f"     It ran against the LIVE TREE: 1,408 tracked files deleted plus every UNCOMMITTED")
    print(f"     file. `git restore` recovered the 1,408 and NONE of the untracked work — this")
    print(f"     round's whole directory and two README rows. **Only committed work survived.**\n")
    print(f"  PRODUCED: two more units paid — R24_regime_receipt and R28_multiplicative. 5 rows,")
    print(f"  3 rounds, 24 numbers, each verified against a fresh run by R388's gate.\n")

    posres = {}
    for name in POS:
        d = next((p for p in ROOT.glob(f"E0*/A*/{name}") if p.is_dir()), None)
        posres[name] = parse((d / "run.py").read_text())[1] if d else False
    pos_ok = all(posres.values())
    _doc, neg_t, neg_n = parse("x = 1\nprint('no docstring')\n")
    neg_ok = (not neg_t and neg_n == 0)
    print(f"  CONTROLS")
    print(f"    TITLE (+)  the three units paid are titled: {posres}  "
          f"{'PASS' if pos_ok else 'FAIL'}")
    print(f"               ⛔ this control killed my FIRST instrument: a marker list of my own")
    print(f"                  current headings scored these same three at 1, 0 and 0.")
    print(f"    TITLE (-)  a file with no docstring: titled={neg_t}, markers={neg_n}  "
          f"{'PASS' if neg_ok else 'FAIL'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the pattern is blind in one direction. Exit 1."); return 1

    rows = {}
    for d in pop:
        doc, titled, n = parse((d / "run.py").read_text())
        rows[d.name] = dict(titled=bool(titled), markers=n,
                            doc_lines=len(doc.splitlines()) if doc else 0)
    titled = [k for k, v in rows.items() if v["titled"]]
    mine = [k for k, v in rows.items() if v["markers"] >= 2]
    share = len(titled) / len(rows)
    lines = sorted(v["doc_lines"] for v in rows.values())
    med = lines[len(lines) // 2]
    print(f"\n  THE CENSUS — {len(rows)} rounds with an artifact, a run.py and no finding site")
    print(f"    titled first line (the CORPUS's convention)     : {len(titled):>4}  ({share:.0%})")
    print(f"    >= 2 markers of MY format (what I reached for)  : {len(mine):>4}  "
          f"({len(mine)/len(rows):.0%})")
    print(f"    median docstring lines                          : {med:>4}   "
          f"(p10 {lines[len(lines)//10]}, p90 {lines[9*len(lines)//10]})")
    print(f"    -> the instrument I would have used says the corpus is far less structured than it is")

    print(f"\n  THE THREE UNITS PAID — n = 3, reported as three observations")
    for k, v in PAID.items():
        print(f"    {k:<28}{v['wall_s']:>7.1f}s{v['out_lines']:>6} lines   "
              f"states its own verdict: {'yes' if v['self_verdict'] else 'NO'}")
    print(f"    -> 3 of 3 end in a verdict line the round wrote itself, so the backfilled sentence")
    print(f"       was READ rather than constructed — which is what makes its numbers checkable.")

    print()
    if share >= 0.80:
        print(f"  W-FORMAT-SHARED — {share:.0%} titled. The sentence is READ, the burden is bounded,")
        print(f"  and {len(rows)} units is a finite project.")
        v = "W_FORMAT_SHARED"
    elif share <= 0.30:
        print(f"  W-FORMAT-ABSENT — only {share:.0%} titled. Each unit is a RECONSTRUCTION, which is")
        print(f"  where an invented sentence comes from, and the debt is a permanent condition.")
        v = "W_FORMAT_ABSENT"
    else:
        print(f"  W-SPLIT — {len(titled)} of {len(rows)} ({share:.0%}) titled, "
              f"{len(rows)-len(titled)} not.")
        print(f"  The debt has TWO TIERS with different unit costs and those counts ARE the")
        print(f"  estimate. Quoting the share alone would be the cell reported as the curve.")
        v = "W_SPLIT"

    print(f"\n  ⚠ STRUCTURE IS NOT TRUTH — R380 found a gate whose docstring described the opposite")
    print(f"    of its code. This measures that a title is PRESENT, never that it is right.")
    print(f"  ⚠ AND THIS SESSION'S A24 ROUNDS ARE EXCLUDED: written to my format by me, so counting")
    print(f"    them would measure my recent habit rather than the corpus.")

    art = dict(stamp(str(SELF)), head=head, n_population=len(rows), n_titled=len(titled),
               n_my_format=len(mine), share=share, median_doc_lines=med, paid=PAID, rows=rows,
               controls=dict(title_pos=posres, title_pos_ok=pos_ok,
                             title_neg_titled=neg_t, title_neg_markers=neg_n, title_neg_ok=neg_ok),
               destroyed_and_rewritten=True, verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r389_reading_burden.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
