"""R386 — what share of a finding's NUMBERS are in the artifact that produced it?

R385 measured that a line generated from an artifact alone identifies its own round 46% of the time
at median rank 2 of 46 -- a draft, not a publication. Its NEXT proposed: hand-write findings for ten
close-miss rounds without looking at the generated line, and let a third instrument judge which
matches the truth.

⛔ THAT DESIGN IS NOT CONSTRUCTIBLE IN THIS SESSION, AND THE REASON IS LEAKAGE I CAUSED MYSELF.
   The hand-written arm would be written by me, and I have been APPENDING TO THE ROOT README ALL
   SESSION -- the document that holds the targets. So the "hand-written from the artifact only" arm
   would be contaminated by knowledge of the answer, and would win by construction. Worse, the
   contamination is UNVERIFIABLE from outside: "I did not use what I remember" is exactly the kind
   of claim this project treats as void. A clean-context writer would fix it and is not available
   here, so the arm is named as impossible rather than approximated.

⭐ BUT THE DECISION IT SERVES IS STILL ANSWERABLE, by a quantity that needs no writing at all.
   The question behind it is: **can generation carry a finding's content, or only gesture at it?**
   A finding's checkable content is its NUMBERS. So: for each round with a hand-written paragraph
   and an artifact, what share of the numbers in the paragraph appear in the artifact?
   That is fully objective, requires no vocabulary of mine, and no text is written to produce it.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES, both ways. Every
   number in a paragraph could have been copied out of the artifact -- I write these paragraphs by
   reading the run output, so a share near 1.0 is entirely possible and would say the artifact
   carries the quantitative content. Or the paragraph's numbers could be counts computed while
   writing, ratios formed on the spot, or figures from OTHER rounds cited for contrast, none of
   which the artifact holds. Nothing in the design forces either.
   ⚠ What IS partly forced and is controlled for: small integers (0,1,2,3...) collide by accident
   across any two numeric texts. The headline is therefore computed over numbers with >= 3
   significant characters as well as over all numbers, and BOTH are printed.

ESTIMAND        for each round with a root-README paragraph naming only it AND a committed artifact:
                  (a) numeric recall = share of the paragraph's numbers that appear in the artifact
                  (b) the same restricted to numbers of >= 3 characters, where accidental collision
                      is rare
                  (c) the distribution across rounds, not merely its mean

IDENTIFICATION  Exact per round -- string containment over a fixed set. NOT identified: whether a
                number absent from the artifact was WRONG, or simply computed elsewhere. Absence is
                absence; it bounds what generation can carry and says nothing about correctness.
                NOT identified: the 243 rounds without a paragraph, which have no ground truth.

SCOPE           population: the same 46 rounds R385 used, for comparability · instrument: numeric
                token extraction and containment · baseline: a permutation pairing · regime: HEAD.

WORLDS
  W-ARTIFACT-HAS-THE-NUMBERS  recall high. The artifact carries the quantitative content and what
                              generation lacks is prose shape -- a solvable problem, and the 243 can
                              be drafted with their numbers intact.
  W-NUMBERS-COMPUTED-IN-PROSE recall low. The numbers in a finding are formed while writing --
                              ratios, comparisons, counts across rounds -- and generation cannot
                              reach them. Then a generated draft is quantitatively empty, and the
                              243 is a debt only writing can pay, as R385's W-PROSE-ONLY would have
                              said had it fired.
  W-SPLIT                     high for long numbers, low for short ones, or vice versa -- and then
                              the collision control decides which reading survives.

PREDICTION MATRIX
  W-ARTIFACT-HAS  -> recall >= 0.70 on long numbers
  W-COMPUTED      -> recall <= 0.30 on long numbers
  W-SPLIT         -> the two recalls disagree by more than 0.30

PRE-REGISTERED KILL -- conditional on the controls, never on the recall alone.
    if permutation_null_is_below_observed and paragraphs_contain_numbers_at_all:
        r = median per-round recall on numbers of >= 3 characters
        if r >= 0.70   -> W-ARTIFACT-HAS-THE-NUMBERS
        elif r <= 0.30 -> W-NUMBERS-COMPUTED-IN-PROSE
        else           -> W-SPLIT, and the two recalls are the finding
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  PERMUTATION   pair each paragraph with a RANDOM other round's artifact and re-measure. Names the
                world it excludes: "any artifact contains any paragraph's numbers, because numbers
                are common". If the null matches the observed value, the recall is collision and not
                provenance.
  COLLISION     recall computed twice, over all numbers and over numbers with >= 3 characters. Small
                integers collide by accident; long decimals do not. Both printed, neither hidden.
  POPULATION    a paragraph with NO numbers cannot have a recall; those rounds are counted and
                excluded, and the count is printed rather than silently dropped.
  SELF          this round excluded from both sides, standard since R382.

MULTIPLICITY    one estimand at two resolutions over one population. Every count printed.
SEEDS           3 for the permutation; per-seed values printed.
ARTIFACT        results/r386_numeric_recall.json with the source hash.

IMPOSSIBLE HERE
  the hand-written arm R385 proposed  -- I would write it and I have been editing the document that
                                         holds the targets all session. A clean-context writer would
                                         fix it and is not available; the arm is named, not faked.
  whether an absent number is WRONG   -- absence bounds what generation can carry, nothing more.
  the 243 without paragraphs          -- no ground truth, by definition.
  a second release                    -- one release.

EXIT
    0  controls hold and the recall is classified
    1  a control misbehaved -- UNVERIFIED
    2  too few rounds carry numbers -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import random
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
SEEDS = (0, 1, 2)
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

# a NUMBER as it appears in prose or JSON: digits with an optional decimal part. Round ids are
# stripped first so `R385` never contributes `385`.
RID = re.compile(r"\bR\d+[a-z0-9_]*\b|\br\d+\b", re.I)
NUM = re.compile(r"\d+(?:\.\d+)?")


def nums(s: str) -> set:
    return set(NUM.findall(RID.sub(" ", s)))


def main() -> int:
    root_txt = (ROOT / "README.md").read_text()
    paras = root_txt.split("\n\n")
    all_names = [d.name for d in sorted(ROOT.glob("E0*/A*/R*"))
                 if d.is_dir() and (d / "results").is_dir()]
    unique = {}
    for b in paras:
        named = [r for r in all_names if r in b]
        if len(named) == 1:
            unique[named[0]] = b

    rows = {}
    for d in sorted(ROOT.glob("E0*/A*/R*")):
        if not d.is_dir() or d == HERE or d.name not in unique:
            continue
        js = sorted((d / "results").glob("*.json"))
        if not js:
            continue
        art = js[0].read_text()
        pn = nums(unique[d.name])
        if not pn:
            rows[d.name] = None                       # counted, not silently dropped
            continue
        an = nums(art)
        long_p = {x for x in pn if len(x) >= 3}
        rows[d.name] = dict(
            p_nums=len(pn), a_nums=len(an),
            recall_all=len(pn & an) / len(pn),
            recall_long=(len(long_p & an) / len(long_p)) if long_p else None,
            n_long=len(long_p), artifact=str(js[0].relative_to(ROOT)))
    usable = {k: v for k, v in rows.items() if v and v["recall_long"] is not None}
    nonum = [k for k, v in rows.items() if v is None]
    nolong = [k for k, v in rows.items() if v and v["recall_long"] is None]
    if len(usable) < 15:
        print(f"  UNRUNNABLE: only {len(usable)} rounds carry a paragraph with long numbers. "
              f"Exit 2, never 0.")
        return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R386 · what the artifact cannot say   HEAD {head}\n")
    print(f"  ⛔ R385's NEXT asked me to HAND-WRITE findings and compare. Not constructible here:")
    print(f"     I would write them, and I have been APPENDING TO THE ROOT README all session —")
    print(f"     the document holding the targets. That arm leaks by construction, and")
    print(f"     \"I did not use what I remember\" is unverifiable from outside. Named, not faked.\n")
    print(f"  POPULATION  {len(usable)} rounds with a paragraph naming only them, an artifact, and")
    print(f"              at least one number of >= 3 characters in the paragraph")
    print(f"              excluded: {len(nonum)} paragraph(s) with no numbers, "
          f"{len(nolong)} with only short ones — counted, not dropped silently")

    ra = sorted(v["recall_all"] for v in usable.values())
    rl = sorted(v["recall_long"] for v in usable.values())
    med_all, med_long = ra[len(ra) // 2], rl[len(rl) // 2]

    # ---- CONTROLS ------------------------------------------------------------------------------
    arts = {k: nums(pathlib.Path(ROOT / v["artifact"]).read_text()) for k, v in usable.items()}
    keys = sorted(usable)
    perm_all, perm_long = [], []
    for s in SEEDS:
        rng = random.Random(s)
        shuffled = keys[:]
        rng.shuffle(shuffled)
        pa, pl = [], []
        for k, other in zip(keys, shuffled):
            pn = nums(unique[k]); an = arts[other]
            lp = {x for x in pn if len(x) >= 3}
            pa.append(len(pn & an) / len(pn))
            if lp:
                pl.append(len(lp & an) / len(lp))
        pa.sort(); pl.sort()
        perm_all.append(pa[len(pa) // 2]); perm_long.append(pl[len(pl) // 2])
    p_all = sum(perm_all) / len(perm_all)
    p_long = sum(perm_long) / len(perm_long)
    perm_ok = (med_long > p_long)
    pop_ok = len(usable) >= 15
    print(f"\n  CONTROLS")
    print(f"    PERMUTATION  a paragraph paired with a RANDOM other round's artifact:")
    print(f"                 median recall_long {p_long:.3f} vs observed {med_long:.3f}  "
          f"{'PASS' if perm_ok else 'FAIL — the recall is COLLISION, not provenance'}")
    print(f"                 per seed {[round(x,3) for x in perm_long]}")
    print(f"                 it names the world it excludes: `any artifact contains any")
    print(f"                 paragraph's numbers, because numbers are common`")
    print(f"    COLLISION    recall over ALL numbers {med_all:.3f} vs over LONG numbers "
          f"{med_long:.3f}")
    print(f"                 — small integers collide by accident; both printed, neither hidden")
    if not (perm_ok and pop_ok):
        print("\n  UNVERIFIED — the recall cannot be separated from collision. Exit 1."); return 1

    # ---- the distribution, not merely the mean --------------------------------------------------
    qs = [0.10, 0.25, 0.50, 0.75, 0.90]
    print(f"\n  THE DISTRIBUTION, not merely the mean — per-round recall on numbers >= 3 chars")
    print(f"    " + "".join(f"p{int(q*100):<3}" + " " for q in qs))
    print(f"    " + "".join(f"{rl[min(int(q*len(rl)), len(rl)-1)]:<4.2f}" + " " for q in qs))
    zero = sum(1 for v in rl if v == 0.0)
    full = sum(1 for v in rl if v == 1.0)
    print(f"    rounds whose paragraph shares NO long number with its artifact: {zero} of {len(rl)}"
          f"   ({zero/len(rl):.0%})")
    print(f"    rounds where every long number is in the artifact: {full} of {len(rl)} "
          f"({full/len(rl):.0%})")

    # ---- VERDICT -------------------------------------------------------------------------------
    print()
    if med_long >= 0.70:
        print(f"  W-ARTIFACT-HAS-THE-NUMBERS — median recall {med_long:.2f} on long numbers. The")
        print(f"  artifact carries the quantitative content, and what a generated draft lacks is")
        print(f"  prose SHAPE rather than substance. The 243 can be drafted with numbers intact.")
        v = "W_ARTIFACT_HAS_THE_NUMBERS"
    elif med_long <= 0.30:
        print(f"  W-NUMBERS-COMPUTED-IN-PROSE — median recall {med_long:.2f} on long numbers, "
              f"against")
        print(f"  a permutation null of {p_long:.2f}. The numbers in a finding are largely formed")
        print(f"  WHILE WRITING — ratios, comparisons, counts across rounds — and no generation from")
        print(f"  the artifact reaches them. A generated draft would be quantitatively empty, and")
        print(f"  the 243 is a debt that only writing can pay.")
        v = "W_NUMBERS_COMPUTED_IN_PROSE"
    else:
        print(f"  W-SPLIT — median recall {med_long:.2f} on long numbers and {med_all:.2f} on all.")
        print(f"  Neither reading wins: a generated draft would carry part of the quantitative")
        print(f"  content and invent none of it, but would be missing a substantial share. The two")
        print(f"  numbers ARE the finding, and quoting either alone would be the cell reported as")
        print(f"  though it were the curve.")
        v = "W_SPLIT"

    print(f"\n  ⚠ ABSENCE IS ABSENCE. A number missing from the artifact is not WRONG — it may have")
    print(f"    been computed while writing, or cited from another round. This bounds what")
    print(f"    generation can CARRY and says nothing about correctness.")
    print(f"  ⚠ AND THE POPULATION IS THE FLATTERING ONE, as in R385: these are rounds someone")
    print(f"    chose to write about. The 243 without paragraphs have no ground truth by")
    print(f"    definition, and every statement about them is an extrapolation.")

    out = dict(stamp(str(SELF)), head=head, n=len(usable), median_recall_all=med_all,
               median_recall_long=med_long, perm_long=p_long, perm_long_per_seed=perm_long,
               perm_all=p_all, quantiles={f"p{int(q*100)}": rl[min(int(q*len(rl)), len(rl)-1)]
                                          for q in qs},
               zero_overlap=zero, full_overlap=full,
               excluded_no_numbers=nonum, excluded_short_only=nolong,
               rows=usable, controls=dict(permutation=perm_ok, population=pop_ok), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r386_numeric_recall.json"
    outp.write_text(json.dumps(out, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
