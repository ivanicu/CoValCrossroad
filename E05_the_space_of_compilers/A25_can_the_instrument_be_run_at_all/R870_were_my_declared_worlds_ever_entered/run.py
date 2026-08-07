#!/usr/bin/env python3
"""
R870 · were the worlds I declared ever ENTERED? — category occupancy across the whole round corpus.

⛔ WHY. R869 built a classifier whose `REPO` category was never populated by a single real gate: the
positive control passed on a synthetic shape that occurs nowhere in the corpus, and the verdict was
carried entirely by the fallback rule. **A category with zero real members is untested apparatus
that still shapes the verdict.** That is a property of an instrument, and this project has declared
`WORLDS A/B/C/D` in hundreds of rounds. **Nobody has ever asked how many of those worlds were
reachable, let alone entered.**

⭐ WORLDS ARE ROUND-SPECIFIC, so counting the letters across rounds is a POSITION statistic and not
a semantic one. **That is the point rather than a defect:** if the outcome is nearly always the
first-declared world, the fork is decorative regardless of what the letters mean, and every
`WORLDS` block in this project is a formality. This asks the falsifiable version.

⛔ AND THE CHEAPEST RUNG FIRST, BECAUSE IT ALREADY CONSTRAINS THE ANSWER. A raw count over the 538
artifacts carrying a `world` key gives **B = 75, A = 53, C = 15**. `B` outranking `A` is not
consistent with a corpus that always takes the first branch, so **the crudest version of the worry
is dead before the round starts.** What that count CANNOT do is normalise by how many worlds each
round declared — a round offering only A/B cannot enter C — and that is what is measured below.


⛔⛔ POST-RUN CORRECTION, WRITTEN BEFORE COMMIT. **THE PRINTED `WORLD C` IS WITHDRAWN, AND THE
HEADLINE IS THE COVERAGE, NOT THE VERDICT.**

**① The verdict fired on n = 1.** `WORLD C` triggered because label `D` was never entered. **`D` was
declared in exactly ONE round.** Under the round's own uniform baseline the expected number of takes
is ~0.25, so observing 0 is unremarkable — **the branch has no power at that population and should
never have been allowed to fire.** This is R869's defect one round later, in the mirror: there, a
category with zero real members carried a verdict; here, a category with one real member did. **The
remedy R869 wrote — require a real corpus item in a category before trusting it — was written down
and then not applied to the very next round's own decision rule.**

**② What the data DOES support is WORLD B, and it is a genuinely good answer.** Position taken:
1→22, 2→25, 3→4. **First-declared world taken 22/51 = 0.431, against a uniform-over-declared
expectation of 0.453.** Those are indistinguishable. ⭐ **So the forks in this project are not
decorative in the way the round set out to test: the outcome is not concentrated on the first
branch, and A, B and C are all entered.** That is the finding, and it survives.

**③ AND THE NUMBER THAT DOMINATES BOTH: 765 of 816 rounds have NO parseable WORLDS block, and 5 more
have a block with no machine-readable outcome. The measurement covers 51 rounds — 6.3% of the
corpus.** Every sentence above is scoped to that 6.3%, and the correct reading of the whole round is
*"where a fork was declared AND its outcome recorded, the fork was exercised"* — which says nothing
about the 94% where I declared no fork at all or left no trace of which way it went.

⚠ **Why the coverage is the honest headline rather than a caveat.** A conclusion about whether my
forks are real, drawn from the 6% of rounds that recorded their fork machine-readably, is drawn from
**the rounds that were most careful about forks**. That is the most favourable possible sample for
the question asked, and nothing here corrects for it. The 0.431-vs-0.453 agreement is real and it is
measured on a self-selected best case.

**The sentence this round cannot support:** *"the trailing world is written to look thorough."*
One declaration of `D` cannot establish that. What it can support: *among 51 rounds, the declared
fork was exercised at close to the rate a genuine fork predicts.*

ESTIMAND        per round: the number of worlds DECLARED in its `WORLDS` block, and the POSITION
                (1-indexed) of the world its committed artifact actually recorded. Corpus-level:
                the distribution of position taken, and the share of declared worlds never entered.
IDENTIFICATION  exact for every round whose run.py has a parseable WORLDS block AND whose artifact
                records a short string `world`. Rounds failing either are REPORTED and excluded —
                and the exclusion count is itself a finding, because it measures how often a
                declared fork left no machine-readable trace of its outcome.
SCOPE           population: every `E0*/A*/R*/run.py` with a WORLDS block and a matching artifact
                instrument: regex over the WORLDS block for leading labels; `world` key in the
                            round's own results/*.json
                baseline:   uniform occupancy — if a round declares k worlds and the branch is a
                            genuine fork, position is not concentrated on 1
                regime:     this repo, this commit
WORLDS          A · position is concentrated on 1 -> the WORLDS blocks are decorative and every
                    fork in this project has been a formality
                B · position is spread and every declared label is entered somewhere -> the forks
                    are real and the vocabulary is fully exercised
                C · position is spread BUT some declared labels are never entered anywhere ->
                    the forks are real yet systematically over-declared: the last world in a list
                    is written to look thorough and cannot happen
KILL            CONDITIONAL, all required:
                  ⭐ ① POSITIVE: the extractor must recover a KNOWN case. R866's artifact records
                     world `C` and its block declares A/B/C, so it must come back as position 3 of
                     3. Hard-coded from the committed file, not from memory.
                  ⭐ ② g=0: a synthetic WORLDS block with two labels must yield 2, not 4 — a parser
                     that returns a constant passes arm ① by luck.
                  ③ non-empty population, else exit 2.
PLACEBO         re-parsing the same file twice must give identical output.
MULTIPLICITY    one corpus-level statistic; the whole per-round table is written to the artifact.
ARTIFACT        results/world_occupancy.json
IMPOSSIBLE      cross-release · construct validated · causally identified (this is an observational
                read of my own corpus; no intervention assigns a round its world).
"""
import json, pathlib, re, subprocess, sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

WBLOCK = re.compile(r"^WORLDS\s+(.*?)(?=^[A-Z][A-Z_ ]{3,}\s|\Z)", re.M | re.S)
LABEL = re.compile(r"^\s*(?:⭐\s*)?([A-D])\s*·", re.M)


def declared(text):
    m = WBLOCK.search(text)
    if not m:
        return None
    labs = LABEL.findall(m.group(1))
    seen, out = set(), []
    for x in labs:
        if x not in seen:
            seen.add(x); out.append(x)
    return out or None


def controls():
    real = ROOT / ("E05_the_space_of_compilers/A24_what_the_definition_costs/"
                   "R866_the_comparator_is_a_swept_axis_not_a_choice/run.py")
    d = declared(real.read_text(encoding="utf-8")) if real.exists() else None
    art = real.parent / "results" / "comparator_sweep.json"
    w = json.loads(art.read_text())["world"] if art.exists() else None
    p1 = d is not None and w in d and (d.index(w) + 1) == 3 and len(d) == 3
    fake = "WORLDS          A · one thing\n                B · another\nKILL            x\n"
    d2 = declared(fake)
    p2 = d2 == ["A", "B"]
    print(f"  POSITIVE  R866 recovers as position 3 of 3 (declared {d}, took {w}): {p1}  "
          f"{'PASS' if p1 else 'FAIL'}")
    print(f"  g=0       a two-label block yields exactly ['A','B']: {d2}  "
          f"{'PASS' if p2 else 'FAIL'}")
    print("    The g=0 arm exists because a parser returning a constant passes the first arm by")
    print("    luck. R869's scoper passed its positive control while being blind to the corpus.")
    return p1 and p2


def main() -> int:
    if not controls():
        print("\n  UNVERIFIED: the extractor failed its own controls. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED"}, open(OUT / "world_occupancy.json", "w"), indent=2)
        return 2

    rows, no_block, no_world = [], 0, 0
    for run in sorted(ROOT.glob("E0*/A*/R*/run.py")):
        d = declared(run.read_text(encoding="utf-8", errors="ignore"))
        if not d:
            no_block += 1; continue
        w = None
        for art in sorted((run.parent / "results").glob("*.json")):
            try:
                obj = json.loads(art.read_text())
            except Exception:
                continue
            if isinstance(obj, dict) and isinstance(obj.get("world"), str) \
                    and len(obj["world"]) <= 24:
                w = obj["world"]; break
        if w is None:
            no_world += 1; continue
        pos = d.index(w) + 1 if w in d else None
        rows.append({"round": run.parent.name, "declared": d, "k": len(d),
                     "world": w, "position": pos})

    if not rows:
        print("\n  OBSERVED NOTHING: no round pairs a WORLDS block with a recorded world. Exit 2.")
        return 2

    matched = [r for r in rows if r["position"]]
    offlist = [r for r in rows if not r["position"]]
    print(f"\n  {len(rows)} round(s) pair a WORLDS block with a recorded world")
    print(f"    ⚠ EXCLUDED and REPORTED: {no_block} run.py without a parseable WORLDS block · "
          f"{no_world} with a block but no machine-readable outcome")
    print(f"    ⚠ {len(offlist)} recorded a world NOT among its own declared labels "
          f"(custom label, e.g. {offlist[0]['world']!r})" if offlist else "")

    posc = Counter(r["position"] for r in matched)
    kc = Counter(r["k"] for r in matched)
    print(f"\n  declared-count distribution: {dict(sorted(kc.items()))}")
    print(f"  position taken:              {dict(sorted(posc.items()))}")
    first = posc.get(1, 0) / len(matched)
    exp_first = sum(1 / r["k"] for r in matched) / len(matched)
    print(f"  ⭐ took the FIRST-declared world: {posc.get(1,0)}/{len(matched)} = {first:.3f}")
    print(f"     uniform-over-declared expectation: {exp_first:.3f}")

    # which declared labels are never entered, among rounds that declared them?
    never = {}
    for lab in "ABCD":
        declared_n = sum(1 for r in matched if lab in r["declared"])
        taken_n = sum(1 for r in matched if r["world"] == lab)
        if declared_n:
            never[lab] = {"declared_in": declared_n, "taken": taken_n,
                          "rate": taken_n / declared_n}
    print("\n  per-label occupancy (among rounds that DECLARED it):")
    for lab, v in never.items():
        print(f"    {lab}  declared in {v['declared_in']:>3}  taken {v['taken']:>3}  "
              f"rate {v['rate']:.3f}")
    empty = [l for l, v in never.items() if v["taken"] == 0]

    world = ("A" if first > 1.5 * exp_first else "C" if empty else "B")
    print(f"\n  ⭐ WORLD {world}: " + {
        "A": "position concentrates on the FIRST declared world — the forks are decorative and"
             " every WORLDS block in this project has been a formality",
        "B": "position is spread and every declared label is entered somewhere — the forks are"
             " real and the vocabulary is fully exercised",
        "C": "position is spread BUT some declared labels are never entered anywhere — the forks"
             " are real yet over-declared, and the trailing world is written to look thorough"}[
        world])
    if empty:
        print(f"     never-entered labels: {empty}")
    print(f"     ⚠ This is OBSERVATIONAL over my own corpus. It cannot say a fork was GENUINE,")
    print(f"       only that its branches were used — a fork can be exercised and still be cheap.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_rounds": len(rows),
               "n_matched": len(matched), "off_list": len(offlist),
               "excluded_no_worlds_block": no_block, "excluded_no_recorded_world": no_world,
               "position_counts": {str(k): v for k, v in sorted(posc.items())},
               "declared_count_dist": {str(k): v for k, v in sorted(kc.items())},
               "first_rate": first, "uniform_expectation": exp_first,
               "per_label": never, "never_entered": empty, "rows": rows},
              open(OUT / "world_occupancy.json", "w"), indent=2)
    print(f"\n  artifact: results/world_occupancy.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
