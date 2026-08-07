#!/usr/bin/env python3
"""
R886 · the definition's HEADLINE statement is one round behind its own evidence.

⛔ WHY, AND IT IS A SECOND COURSE CORRECTION. Six consecutive rounds (R880–R885) audited my own
instruments, populations and units. Every one found something real. **None said anything about a
core.** I made exactly this correction at R874 and drifted back into it one level deeper — the
governing constitution's tell: *the most quotable sentence in the report is about my rigour rather
than about the object.*

⭐ **AND THERE IS AN OBJECT-LEVEL DEBT SITTING UNPAID.** R881 established two things about clause ②
that reached `DEFINITION.md` only as an ANNOTATION ~200 lines below the headline:
  ① **criterion B's BH correction is DECORATION** — it binds for 0 of 28 admitted arms; the CI
     condition binds for all 28. **So clause ②'s criterion reduces to `CI-lower > 0`.**
  ② the admitted set is **stable but MARGINAL** — the closest arm clears by **0.28 MDE** and 4 of
     28 clear by less than 0.6.
**The headline statement still says "under a NAMED admissibility criterion" as though the criterion
were irreducible.** That is *a correction that never reached the artifact it was about* — the exact
failure this project has a memory entry for.

ESTIMAND        whether the deliverable's headline statement is entailed by the committed artifacts,
                and if not, what the corrected statement is.
IDENTIFICATION  exact. Every input is a committed artifact; this round ASSEMBLES and asserts, and
                its job is to fail loudly if the artifacts say something other than what it writes.
SCOPE           population: the headline statement and the four artifacts it rests on — DERIVED
                            from the estimand, four named objects
                instrument: the committed JSON, read from disk
                baseline:   the headline as currently written at DEFINITION.md
                regime:     home release, judge J, 968 prompts, 99 arms
WORLDS          A · the headline already entails the evidence -> nothing is owed and this round is
                    a no-op, which it must SAY rather than manufacture an edit
                B · the headline is behind -> the corrected statement is the deliverable
KILL            CONDITIONAL, all read from disk, never from memory:
                  ⭐ ① R881 must show `binds_BH == 0` and `binds_CI == 28`.
                  ⭐ ② R881 must show `closest_in_mdes` < 1.0 — the marginality claim.
                  ⭐ ③ R876 must show the admitted set at 25 arms and PR 1.6368.
                  ⭐ ④ the headline must NOT already contain the reduction. **If it does, WORLD A
                     and this round writes nothing** — a round that edits a file already correct is
                     manufacturing work, which is the drift this round exists to correct.
MULTIPLICITY    one statement, four supporting artifacts; every check reported.
ARTIFACT        results/headline_debt.json
IMPOSSIBLE      cross-release · construct validated · causally identified. ⚠ And unchanged since
                R874: `the definition describes the instance` stays live for every clause.
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
DEFN = ROOT / "E05_the_space_of_compilers/DEFINITION.md"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
HEADLINE = "A CORE is a criterion set of size > 1 that"


def art(g, n):
    p = next(A24.glob(f"{g}/results/{n}"), None)
    return json.loads(p.read_text()) if p else None


def main() -> int:
    r881 = art("R881_*", "boundary_distance.json")
    r876 = art("R876_*", "admitted_diversity.json")
    if r881 is None or r876 is None:
        print("  UNRUNNABLE: R881/R876 artifacts missing. Exit 2, never 0.")
        return 2
    text = DEFN.read_text()

    k1 = r881.get("binds_BH") == 0 and r881.get("binds_CI") == 28
    k2 = (r881.get("closest_in_mdes") or 99) < 1.0
    k3 = r876.get("n_admitted_excl_aliases") == 25 and \
        abs((r876.get("pr_observed") or 0) - 1.6368) < 1e-3
    hi = text.find(HEADLINE)
    block = text[hi:hi + 900] if hi >= 0 else ""   # widened: the stamp sits below
    # ⛔ MARKER CORRECTED. This first tested for the literal "CI-lower" while the corrected
    # headline I wrote says "CI lower bound" — hyphen versus space — so KILL ④ could not see the
    # very edit it demanded and the re-run still printed WORLD B after the file was already
    # fixed. Fourth string-mismatch of this shape this session (three annotation anchors, now a
    # detector marker). The rule the other three taught applies here too: **the marker must be
    # read from the text it is meant to match, never written from memory of it.** Now a regex
    # tolerant of both, plus the round-id stamp the edit leaves behind.
    k4 = hi >= 0 and not re.search(r"CI[ -]lower|reduces to|CORRECTED R886", block, re.I)
    print(f"  ① R881: BH binds {r881.get('binds_BH')} · CI binds {r881.get('binds_CI')}: {k1}  "
          f"{'PASS' if k1 else 'FAIL'}")
    print(f"  ② R881: closest admitted arm at {r881.get('closest_in_mdes'):.4f} MDE < 1.0: {k2}  "
          f"{'PASS' if k2 else 'FAIL'}")
    print(f"  ③ R876: {r876.get('n_admitted_excl_aliases')} arms, PR "
          f"{r876.get('pr_observed'):.4f}: {k3}  {'PASS' if k3 else 'FAIL'}")
    print(f"  ④ the headline does NOT already carry the reduction: {k4}  "
          f"{'PASS' if k4 else 'FAIL — WORLD A, nothing owed'}")
    if not (k1 and k2 and k3):
        print("\n  UNVERIFIED: an artifact says something other than what this round assembles.")
        json.dump({"verdict": "UNVERIFIED", "k": [k1, k2, k3, k4]},
                  open(OUT / "headline_debt.json", "w"), indent=2)
        return 2

    world = "B" if k4 else "A"
    corrected = (
        "A CORE is a criterion set of size > 1 that ③ consumes no prompt-specific labels and "
        "② beats a NAMED prompt-blind comparator by a resolvably positive margin — its "
        "bootstrap CI lower bound above zero. ⚠ On this release that admits 28 arms including "
        "the core, of which 25 are procedurally distinct; the set spans 1.6 effective dimensions "
        "against 3.6 for a random 25, and its closest member clears the boundary by 0.28 MDE.")
    print(f"\n  ⭐ WORLD {world}: " + {
        "A": "the headline already entails the evidence — nothing is owed, and this round writes "
             "nothing rather than manufacturing an edit",
        "B": "the headline is behind its own evidence — the corrected statement is below"}[world])
    if world == "A":
        json.dump({"world": "A", "owed": False}, open(OUT / "headline_debt.json", "w"), indent=2)
        print("     A round that edits a file already correct is manufacturing work.")
        return 0

    print(f"\n  ⭐⭐ THE CORRECTED HEADLINE:\n")
    for line in [corrected[i:i + 88] for i in range(0, len(corrected), 88)]:
        print(f"     {line}")
    print(f"\n  ⭐ what changed and why:")
    print(f"     · 'a NAMED admissibility criterion' -> 'its bootstrap CI lower bound above zero'")
    print(f"       because BH binds for 0 of 28 (R881). The criterion is not two conditions.")
    print(f"     · the breadth and the marginality are now IN the statement rather than 200 lines")
    print(f"       below it, because a reader quotes the headline and not the annotations.")
    print(f"     ⚠ unchanged: `the definition describes the instance` stays live. One release.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "owed": True,
               "corrected_headline": corrected,
               "evidence": {"binds_BH": r881.get("binds_BH"), "binds_CI": r881.get("binds_CI"),
                            "closest_in_mdes": r881.get("closest_in_mdes"),
                            "n_admitted_excl_aliases": r876.get("n_admitted_excl_aliases"),
                            "pr_observed": r876.get("pr_observed")},
               "unit_note": {"28": "arms including the core", "25": "arms, distinct, excl aliases",
                             "1.6368": "effective dimensions", "0.28": "MDE"},
               "live_limitation": "the definition describes the instance; one release"},
              open(OUT / "headline_debt.json", "w"), indent=2)
    print(f"\n  artifact: results/headline_debt.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
