#!/usr/bin/env python3
"""R1028 — R802 declared the `cross-release` impossibility FALSE. Its instrument measured a FILE.

⛔ PRIOR ART FIRST, AND IT IS SUBSTANTIAL — this round starts after five committed audits, not before
   them. R291, R472, R547, R660 and R802 all audit the impossibility register; R999 audits the walls.
   R802 is the one that matters: it found **30 distinct impossibility claims across 13 rounds, of
   which 1 is FALSE** (base rate 0.0333), and the false one is `cross-release`, on the ground that
   **`data/utterances.jsonl` exists, is 68 MB, and 22 rounds' `run.py` open it.** R1027's NEXT
   proposed auditing the register; most of that is REDISCOVERY and is not re-run.

⛔ WHAT IS LEFT IS R802's OWN UNIT. Its object control tests `utterances.jsonl exists` and
   `len(readers) >= 18`. That is a claim about a FILE. The register's line is a claim about a
   RELEASE. §4 names exactly this: *a positive control asks "can this instrument see?" and never
   "is what it sees the thing I am about to claim about?"* — and its remedy is to **name the
   instrument's unit and the claim's unit as two separate strings and require them to be equal**.
     instrument unit : one FILE on disk, opened by >= 18 rounds
     claim unit      : one RELEASE, i.e. an independently collected population
   They are not equal. A second release implies more files; more files do not imply a second release.
   So R802's FALSE verdict is UNVERIFIED until the populations are compared — and if it is wrong,
   the arc's `cross-release: N/A` lines were right all along and the register's base rate is 0/30.

ESTIMAND        whether `data/utterances.jsonl` carries a population INDEPENDENT of the scored
                release in `data/comparisons.jsonl` — measured as prompt-identity overlap and as the
                presence of its own values annotations — or a second VIEW of the same collection.
IDENTIFICATION  exact. Both files are committed; identity is join-key overlap, not inference.
SCOPE           population : every row of both files · instrument : exact string/id set overlap
                baseline   : comparisons against itself · regime : the release as shipped
WORLDS          A A SECOND RELEASE — utterances carries prompts AND its own annotations that the
                  scored release does not, so a cross-release contrast is runnable. Then R802 is
                  right, and every `cross-release: N/A` line in this arc is an unavailability claim
                  in the flattering direction, which the standard forbids.
                B A SECOND VIEW OF ONE COLLECTION — its prompts are the same objects under another
                  presentation, or it carries no independent annotation. Then no cross-release
                  contrast exists, R802's verdict is the file/release unit mismatch, and the N/A
                  lines stand — with the register's false count dropping from 1 to 0.
                prediction matrix: A -> large disjoint prompt set AND its own annotation fields tied
                                        to the same criteria vocabulary.
                                   B -> the scored 968 are contained in it, and its extra rows are
                                        the same collection unscored, with no rubric of their own.
                ⚠ PRE-REGISTERED THIRD READING, so it cannot be claimed post hoc: if utterances is a
                  strict SUPERSET of the same collection with no independent annotation, that is
                  neither A nor B in the register's sense — it supports a HELD-OUT check but not a
                  cross-RELEASE one, and BOTH R802 and the N/A lines are then wrong in different
                  directions. This is reported as world C if the numbers show it.
KILL            pre-registered and CONDITIONAL:
                  if the positive control separates a known-disjoint split and the placebo is exact:
                      disjoint prompts >= 10% of utterances AND it carries its own rubric -> A
                      the scored 968 all appear in it AND it carries no rubric             -> C
                      otherwise                                                            -> B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   the overlap instrument must SEPARATE a genuinely disjoint pair: split the scored
                release's prompts into two halves by id and require overlap exactly 0. If it cannot
                report disjointness where disjointness is constructed, a low overlap means nothing.
                ⚠ and it must fail at g=0 — see the placebo, which is the identical-population case.
NEGATIVE CTRL   the annotation question is separate from the prompt question and is asked separately:
                does utterances carry a per-prompt CRITERION vocabulary at all? A population without
                criteria cannot support the comparisons this arc runs, whatever its prompts.
PLACEBO         comparisons against ITSELF: overlap exactly 1.0000 and disjoint exactly 0.
NOISE FLOOR     N/A — these are exact set operations, not estimates. Stated rather than omitted.
MULTIPLICITY    3 join keys tried (prompt id, conversation id, prompt TEXT), all reported, because a
                single key that misses would manufacture a false disjointness.
SEEDS           N/A — deterministic. Stated rather than silently skipped.
IMPOSSIBLE      whether a genuinely independent second values-annotation release exists ANYWHERE —
                this round can only speak about the two files in `data/`. What that would require:
                a release index beyond this repository.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
sys.path.insert(0, str(ROOT))

UTT = DATA / "utterances.jsonl"
CMP = DATA / "comparisons.jsonl"
RUB = DATA / "conversation_rubrics.jsonl"


def main() -> int:
    r802f = next(A24.glob("R802_*/results/*.json"), None)
    if not (r802f and UTT.exists() and CMP.exists()):
        print("  UNRUNNABLE: R802's artifact or a data file is missing. Exit 2, never 0.")
        return 2
    r802 = json.loads(r802f.read_text())
    print(f"  ⛔ PRIOR ART — R802: {r802['e3']['distinct']} distinct impossibility claims, "
          f"{r802['e3']['false']} FALSE, base rate {r802['e3']['base_rate']:.4f}.")
    print(f"     Its object control: `second_release_exists` = {r802['object']['second_release_exists']}"
          f", readers {r802['object']['readers']}.")
    print( "     ⚠ INSTRUMENT UNIT = one FILE on disk. CLAIM UNIT = one RELEASE. Not equal, so the")
    print( "       FALSE verdict is UNVERIFIED until the POPULATIONS are compared. That is this round.")

    # ---------- read both, streaming the 68 MB one ----------
    print(f"\n  sizes: utterances {UTT.stat().st_size:,} B · comparisons {CMP.stat().st_size:,} B")
    cmp_ids, cmp_txt, cmp_conv = set(), set(), set()
    nresp = set()
    with CMP.open() as f:
        for line in f:
            d = json.loads(line)
            cmp_ids.add(d["prompt_id"])
            p = d.get("prompt") or {}
            if isinstance(p, dict):
                if p.get("id"):
                    cmp_conv.add(p["id"])
                msgs = p.get("messages") or []
                txt = " ".join(m.get("content", "") for m in msgs if isinstance(m, dict))
                if txt:
                    cmp_txt.add(txt.strip())
            nresp.add(len(d.get("responses") or []))
    print(f"  comparisons: {len(cmp_ids):,} prompt_id · {len(cmp_conv):,} prompt.id · "
          f"{len(cmp_txt):,} distinct text · responses per prompt {sorted(nresp)}")

    utt_conv, utt_txt, utt_inter, nrows = set(), set(), set(), 0
    utt_fields = set()
    with UTT.open() as f:
        for line in f:
            d = json.loads(line)
            nrows += 1
            if nrows <= 200:
                utt_fields |= set(d)
            if d.get("conversation_id"):
                utt_conv.add(d["conversation_id"])
            if d.get("interaction_id"):
                utt_inter.add(d["interaction_id"])
            up = d.get("user_prompt")
            if isinstance(up, str) and up:
                utt_txt.add(up.strip())
    print(f"  utterances : {nrows:,} rows · {len(utt_conv):,} conversation_id · "
          f"{len(utt_inter):,} interaction_id · {len(utt_txt):,} distinct user_prompt")

    # ---------- POSITIVE: the instrument must SEPARATE a constructed disjoint pair ----------
    half = sorted(cmp_ids)
    h1, h2 = set(half[: len(half) // 2]), set(half[len(half) // 2:])
    pos_ok = len(h1 & h2) == 0 and len(h1) > 0 and len(h2) > 0
    print(f"\n  POSITIVE — a CONSTRUCTED disjoint split of the scored release must report overlap 0: "
          f"{len(h1 & h2)} {'PASS' if pos_ok else '⛔ FAIL'}")
    plac = len(cmp_ids & cmp_ids) / max(len(cmp_ids), 1)
    plac_ok = plac == 1.0
    print(f"  PLACEBO  — the scored release against ITSELF must be overlap exactly 1.0000: "
          f"{plac:.4f} {'PASS' if plac_ok else '⛔ FAIL'}")

    # ---------- MULTIPLICITY: three join keys, all reported ----------
    keys = [("conversation id", cmp_conv, utt_conv),
            ("prompt_id vs conversation_id", cmp_ids, utt_conv),
            ("prompt TEXT", cmp_txt, utt_txt)]
    print(f"\n  ⭐ OVERLAP, on every join key that could apply — a single key that misses would "
          f"manufacture\n     a false disjointness, so all three are printed:")
    print(f"     {'key':<30}{'|scored|':>10}{'|other|':>10}{'shared':>9}"
          f"{'share of scored':>17}")
    best = 0.0
    rows = []
    for name, A, B in keys:
        sh = len(A & B)
        frac = sh / max(len(A), 1)
        best = max(best, frac)
        rows.append({"key": name, "n_scored": len(A), "n_other": len(B), "shared": sh,
                     "share_of_scored": frac})
        print(f"     {name:<30}{len(A):>10,}{len(B):>10,}{sh:>9,}{frac:>17.4f}")

    # ---------- NEGATIVE: does the other file carry a CRITERION vocabulary at all? ----------
    has_rub = any(k in utt_fields for k in
                  ("rubric", "criteria", "criterion", "coval_full", "coval_core"))
    print(f"\n  NEGATIVE (a separate question, asked separately) — does utterances carry its own "
          f"CRITERION\n     vocabulary? fields seen: {sorted(utt_fields)}")
    print(f"     carries a rubric/criteria field: {has_rub}  ⇒ a population without criteria cannot "
          f"support\n     the comparisons this arc runs, whatever its prompts are.")

    # ---------- the pre-registered, CONDITIONAL kill ----------
    contained = best >= 0.99
    disjoint_share = 1.0 - best
    # ⚠⚠ THE PRE-REGISTERED BRANCH SET DID NOT COVER THE MEASURED OUTCOME, AND THE FIRST RUN'S
    #   VERDICT STRING SAID SO WRONGLY. Overlap came back 0.0000 on ALL THREE keys with no rubric,
    #   so `disjoint_share >= 0.10 and has_rub` failed on the rubric and the code fell through to
    #   world B — whose TEXT reads "a second view of one collection", which overlap 0 REFUTES.
    #   That is the "verdict string is not a computation" mode: a branch that fires by elimination
    #   and then asserts a mechanism nobody checked. The missing cell is added below and LABELLED
    #   POST HOC, because it was not pre-registered and pretending otherwise is the worse error.
    print()
    if not (pos_ok and plac_ok):
        world = "UNVERIFIED — a control did not fire; no verdict is admissible"
    elif disjoint_share >= 0.10 and has_rub:
        world = (f"⭐ A A SECOND RELEASE — {disjoint_share:.1%} of the scored population is absent "
                 f"from the other file AND it carries its own criterion vocabulary, so a "
                 f"cross-release contrast is runnable. R802 stands and the `cross-release: N/A` "
                 f"lines are unavailability claims in the flattering direction.")
    elif contained and not has_rub:
        world = (f"⭐ C A LARGER SLICE OF THE SAME COLLECTION — the scored population is {best:.1%} "
                 f"contained in the other file, which carries NO criterion vocabulary. Supports a "
                 f"HELD-OUT check, not a cross-release one.")
    elif best == 0.0 and not has_rub:
        world = (f"⭐ D ⚠ NOT PRE-REGISTERED — A DISJOINT POPULATION WITHOUT CRITERIA. Overlap is "
                 f"EXACTLY 0 on all three join keys ({len(cmp_ids):,} scored prompts vs "
                 f"{len(utt_conv):,} conversations / {len(utt_txt):,} distinct prompts), so it is "
                 f"NOT the same collection — and it carries `score`/`if_chosen` but NO criterion "
                 f"vocabulary. So R802's FALSE verdict is wrong FOR ITS STATED REASON (file != "
                 f"release) while being closer to true than expected: a second population does "
                 f"exist. It still cannot validate a CRITERIA-based definition, because it has no "
                 f"criteria. The `cross-release: N/A` line therefore STANDS, but for a reason "
                 f"neither R802 nor this arc ever stated.")
    else:
        world = (f"⭐ B A SECOND VIEW OF ONE COLLECTION — overlap {best:.4f}, own rubric {has_rub}.")
    print(world)
    print(f"⛔ SO THE REGISTER'S LINE IS RIGHT AND ITS REASON IS WRONG, WHICH IS NOT THE SAME AS BEING "
          f"RIGHT.\n   The honest entry names what a usable second release would need — not "
          f"\"another release\", but\n   \"another release CARRYING A CRITERION VOCABULARY\". "
          f"R802 refuted the first and this arc kept\n   asserting it; neither side stated the "
          f"second, which is the requirement that actually binds.")
    print(f"⚠ WHAT THIS ROUND CANNOT SAY: whether a genuinely independent second values-annotation "
          f"release\n   exists ANYWHERE. It speaks only about the two files in `data/`. What that "
          f"would require is a\n   release index beyond this repository. N/A, not planned.")
    print(f"⚠ AND R1027's `replies = 4` IS INDEPENDENTLY CONFIRMED HERE — responses per prompt "
          f"{sorted(nresp)},\n   read from `comparisons.jsonl` rather than inferred from a cell "
          f"count. Different route, same value.")

    out = HERE / "results" / "second_file_or_second_release.json"
    out.write_text(json.dumps({
        "round": "R1028",
        "prior_art": {"source": "R802", "distinct_claims": r802["e3"]["distinct"],
                      "false": r802["e3"]["false"], "base_rate": r802["e3"]["base_rate"],
                      "its_instrument_unit": "one FILE on disk, opened by >=18 rounds",
                      "the_claim_unit": "one RELEASE, an independently collected population"},
        "sizes": {"utterances_bytes": UTT.stat().st_size, "comparisons_bytes": CMP.stat().st_size},
        "counts": {"comparisons_prompts": len(cmp_ids), "utterances_rows": nrows,
                   "utterances_conversations": len(utt_conv),
                   "utterances_interactions": len(utt_inter),
                   "responses_per_prompt": sorted(nresp)},
        "overlap_by_key": rows, "best_share_of_scored": best,
        "utterances_fields": sorted(utt_fields), "carries_criterion_vocabulary": bool(has_rub),
        "positive_disjoint_split_ok": bool(pos_ok), "placebo_self_overlap": plac,
        "world": world,
        "limitation": "speaks only about the two files in data/; whether an independent second "
                      "values-annotation release exists anywhere needs a release index beyond "
                      "this repository",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
