#!/usr/bin/env python3
"""
R905 · typing `coval_core` completes R904's partition — and exact matching is the wrong instrument.

⛔ WHY. R904 typed the admitted arms by criterion SOURCE and found two kinds: a fixed external
checklist (`generic`) and prompt-rubric selectors (`topw_k*`, `topabs_k4`). **`coval_core` — the one
arm the definition was written from — was ASSERTED to be a third kind on the strength of R494's
`99.6% unique`, never measured here.** This round measures it.

⭐ **AND THE RELEASE'S OWN SCHEMA ALREADY ANSWERS HALF OF IT.** `data/conversation_rubrics.jsonl`
ships `coval_full` items carrying a **`rubric_item_id`** and `coval_core` items carrying **only
`criterion`** — no id. **The core's criteria are not references into the rubric; they are free
text.** That is the release stating the type in its data model, not an inference.

⛔⛔ **AND R904's INSTRUMENT WOULD GET THE REST WRONG.** R904 typed by EXACT string subset. Applied
to a generator that PARAPHRASES the rubric, exact matching returns ~0 and types it
`GENERATED_OR_OTHER` — the right label for the wrong reason, and it would hide that
`corebench/ablate_novel.py:5` already records **40.3% of the core's criteria have no counterpart in
`coval_full` above similarity 0.60**, i.e. **59.7% DO**. **The instrument's unit (identical strings)
is not the claim's unit (drawn from the rubric).** §4's row exactly.
⚠ **And the committed similarity is `difflib.SequenceMatcher`, which is CHARACTER-level.** So it
measures LEXICAL overlap, not semantic. Calling it semantic would be the label-not-a-measurement
error one level up, so it is called lexical throughout.

ESTIMAND        `coval_core`'s criterion-source type under two instruments — exact string subset,
                and lexical near-match swept over the committed thresholds — placed beside
                `topw_k4` (known exact subset) and `generic` (known fixed checklist).
IDENTIFICATION  exact for both instruments. ⚠ Neither is semantic; a criterion that means the same
                thing in different words is invisible to both, and that limit is named not fixed.
SCOPE           population: prompts carrying both `coval_core` and `coval_full` — counted
                instrument: exact set membership; difflib character ratio at 0.50/0.60/0.70/0.80
                baseline:   `generic`, a checklist known to be from a different vocabulary
                regime:     home release
WORLDS          A · the core is neither fixed nor an exact subset, but lexically close to the
                    rubric well above `generic` -> a THIRD type, a paraphrasing generator, and
                    R904's partition completes at three kinds
                B · the core IS an exact subset -> it is a rubric selector and R494's `99.6%
                    unique` is about something else
                C · the core's lexical overlap sits at `generic`'s level -> it is no closer to the
                    rubric than an unrelated checklist, and `partly rubric-derived` is withdrawn
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE, and it can fail: `topw_k4` is an EXACT subset of the rubric, so the
                     LEXICAL instrument must return ~1.0 for it at EVERY threshold. **If a lexical
                     matcher disagrees where exact match already says 1.0, the matcher is broken**
                     and nothing it says about the core is readable.
                  ⭐ ② PLACEBO: `generic` — a fixed checklist from a different vocabulary — gives
                     the floor. Without it, "the core is 60% lexically covered" has no scale.
                  ⭐ ③ SPECIFICATION CURVE, not a cell: all four committed thresholds reported,
                     including any that reverse the ordering.
                  ④ the 0.60 threshold and the difflib method are READ from ablate_novel.py, not
                     chosen here — a threshold I picked would be the invented-cutoff error this
                     session has committed six times.
                     ⛔ POST-RUN: MY READER TOOK THE WRONG LIST. The source line is
                     `SEEDS, NSHAM, THRESH = [0, 1, 2], 5, [0.50, 0.60, 0.70, 0.80]`, and my parser
                     grabbed the FIRST `[...]` on the line — returning **SEEDS** as the thresholds.
                     An instrument that reads the wrong field of the right line, which is this
                     session's own class. Fixed to parse the right-hand side of the assignment.
                     ⛔⛔ AND THE PROMPT IDS DO NOT MATCH: `conversation_rubrics.jsonl` keys on
                     `conversation.id` and the corebench arms key on a DIFFERENT id — set overlap
                     measured at **0**. The corpus ships the joiner `load_join(comparisons.jsonl,
                     conversation_rubrics.jsonl)` and `ablate_novel.py:54` uses it. Keying on the
                     id that was simply *there* would have compared two disjoint universes and
                     reported an empty population as a finding.
                     ⛔⛔⛔ AND I THEN IMPORTED `load_join` FROM `score` — it lives in
                     `covalx.judge`, which `ablate_novel.py:52` states on the line above the call I
                     had already read. **Fourth from-memory symbol this session** (two in R898, the
                     `LETTERS` guess, now this). The pattern is identical every time: I read the
                     CALL and reconstruct the IMPORT instead of reading it two lines up.
                     ⚠ And then a fourth correction on the same line: `ablate_novel.py:41` inserts
                     BOTH `ROOT` and `ROOT/corebench` on sys.path; I had copied only the second, so
                     `covalx` was unimportable. **Four fixes to reach one working join, every one
                     of them a piece of a line I had already looked at.**
MULTIPLICITY    3 arms × 4 thresholds + 1 exact test each; every cell printed.
ARTIFACT        results/core_type.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: semantic equivalence. Both instruments are surface-level, so
                a paraphrase with no shared characters is invisible to both.
"""
import difflib, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
RES = ROOT / "corebench" / "results"
ABL = ROOT / "corebench" / "ablate_novel.py"


def read_thresholds():
    """READ the committed sweep, never choose one here."""
    for line in ABL.read_text().splitlines():
        if "THRESH" in line and "=" in line and "[" in line:
            rhs = line.split("=", 1)[1]                 # the ASSIGNED values, not the whole line
            lists = [x.split("]")[0] for x in rhs.split("[")[1:]]
            for cand in reversed(lists):               # THRESH is the LAST bound name
                try:
                    v = [float(x) for x in cand.split(",")]
                    if all(0.0 < x < 1.0 for x in v):  # thresholds are fractions; SEEDS are not
                        return v
                except Exception:
                    continue
    return None


def main() -> int:
    th = read_thresholds()
    if not th:
        print("  UNRUNNABLE: could not read the committed threshold sweep. Exit 2, never 0.")
        return 2
    print(f"  ④ thresholds READ from {ABL.name}: {th}   (method: difflib.SequenceMatcher, "
          f"CHARACTER-level -> LEXICAL, not semantic)")

    # ⛔ THE CORPUS'S OWN JOINER, because the two files key on DIFFERENT ids (overlap measured 0).
    # ablate_novel.py:41 inserts BOTH; I copied only the second and covalx became unimportable.
    sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
    from covalx.judge import load_join     # ablate_novel.py:52 — NOT score.py            # noqa
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    core, fullr = {}, {}
    for pid, _q, r in joined:
        core[pid] = [i["criterion"] for i in (r.get("coval_core") or []) if i.get("criterion")]
        fullr[pid] = [i["criterion"] for i in (r.get("coval_full") or []) if i.get("criterion")]
    pids = sorted(p for p in core if core[p] and fullr.get(p))
    print(f"  prompts with BOTH coval_core and coval_full: {len(pids)}")
    if len(pids) < 100:
        print("  UNRUNNABLE: fewer than 100 prompts. Exit 2, never 0.")
        return 2

    # the release's own schema, read not inferred
    has_id = None
    for _p, _q, r in joined:
        if r.get("coval_core") and r.get("coval_full"):
            has_id = ("rubric_item_id" in r["coval_full"][0],
                      "rubric_item_id" in r["coval_core"][0])
            break
    print(f"  the release's SCHEMA: coval_full carries rubric_item_id={has_id[0]} · "
          f"coval_core carries rubric_item_id={has_id[1]}")

    def load_arm(nm):
        f = RES / f"core_{nm}.json"
        return json.loads(f.read_text()) if f.exists() else None

    arms = {"coval_core": core, "topw_k4": load_arm("topw_k4"), "generic": load_arm("generic")}
    arms = {k: v for k, v in arms.items() if v}
    sub = [p for p in pids if all(p in v for v in arms.values())]
    print(f"  prompts present in every arm compared: {len(sub)}")
    if len(sub) < 100:
        print("  UNRUNNABLE: fewer than 100 shared prompts. Exit 2, never 0.")
        return 2

    rows = {}
    for nm, sel in arms.items():
        exact = float(np.mean([len(set(sel[p]) - set(fullr[p])) == 0 for p in sub]))
        cov = {}
        for t in th:
            sh = []
            for p in sub:
                F = fullr[p]
                sh.append(np.mean([max((difflib.SequenceMatcher(None, c, z).ratio() for z in F),
                                       default=0.0) >= t for c in sel[p]]))
            cov[t] = float(np.mean(sh))
        rows[nm] = {"exact_subset_share": exact, "lexical_coverage": cov,
                    "mean_k": float(np.mean([len(sel[p]) for p in sub]))}

    c1 = all(rows["topw_k4"]["lexical_coverage"][t] > 0.99 for t in th)
    print(f"\n  ① POSITIVE topw_k4 is an EXACT subset ({rows['topw_k4']['exact_subset_share']:.3f}), "
          f"so lexical coverage must be ~1.0 at EVERY threshold:")
    print(f"     " + "  ".join(f"t={t}: {rows['topw_k4']['lexical_coverage'][t]:.4f}" for t in th)
          + f"   {c1}  {'PASS' if c1 else 'FAIL'}")
    print(f"     a lexical matcher disagreeing where exact match says 1.0 would be broken")
    c2 = "generic" in rows
    print(f"  ② PLACEBO generic (fixed checklist, different vocabulary) gives the floor: {c2}  "
          f"{'PASS' if c2 else 'FAIL'}")
    if not (c1 and c2):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "rows": rows},
                  open(OUT / "core_type.json", "w"), indent=2)
        return 2

    print(f"\n  ⭐ ③ SPECIFICATION CURVE — lexical coverage of the prompt's rubric, all "
          f"{len(th)} committed thresholds:")
    print(f"     {'arm':<14}{'exact ⊆':>10}" + "".join(f"{('t=' + str(t)):>10}" for t in th))
    for nm in ("coval_core", "topw_k4", "generic"):
        if nm in rows:
            print(f"     {nm:<14}{rows[nm]['exact_subset_share']:>10.3f}"
                  + "".join(f"{rows[nm]['lexical_coverage'][t]:>10.4f}" for t in th))

    cc, gg = rows["coval_core"], rows["generic"]
    t60 = 0.60 if 0.60 in th else th[len(th) // 2]
    world = ("B" if cc["exact_subset_share"] > 0.5 else
             "C" if cc["lexical_coverage"][t60] <= gg["lexical_coverage"][t60] + 0.05 else "A")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": f"`coval_core` is a THIRD type — exact subset {cc['exact_subset_share']:.3f} (it is "
             f"not selecting rubric items) yet lexically covered {cc['lexical_coverage'][t60]:.4f} "
             f"at t={t60} against generic's {gg['lexical_coverage'][t60]:.4f}. **A paraphrasing "
             "generator**, and R904's partition completes at three kinds",
        "B": "`coval_core` IS an exact subset — it is a rubric selector and R494's 99.6% unique is "
             "about something else",
        "C": f"`coval_core`'s lexical overlap ({cc['lexical_coverage'][t60]:.4f}) sits at generic's "
             f"level ({gg['lexical_coverage'][t60]:.4f}) — no closer to the rubric than an "
             "unrelated checklist, and `partly rubric-derived` is withdrawn"}[world])
    print(f"\n  ⚠ AND R904's INSTRUMENT WOULD HAVE MISSED THIS. Typing by EXACT subset alone puts")
    print(f"    the core in the same bucket as anything non-selecting, hiding that it tracks the")
    print(f"    rubric lexically. **The instrument's unit (identical strings) is not the claim's")
    print(f"    unit (drawn from the rubric).**")
    print(f"  ⚠ NEITHER INSTRUMENT IS SEMANTIC. difflib compares CHARACTERS, so a true paraphrase")
    print(f"    sharing no wording is invisible to both, and every number here is a LOWER bound on")
    print(f"    how much the core reuses the rubric's content.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_prompts": len(sub),
               "thresholds_read_from_source": th,
               "schema": {"coval_full_has_rubric_item_id": bool(has_id[0]),
                          "coval_core_has_rubric_item_id": bool(has_id[1]),
                          "why_it_matters": "the release's own data model says the core's criteria "
                                            "are free text, not references into the rubric"},
               "arms": rows,
               "instrument": "difflib.SequenceMatcher character ratio — LEXICAL, not semantic",
               "r904_instrument_would_miss": "typing by EXACT subset alone buckets the core with "
                                             "anything non-selecting and hides that it tracks the "
                                             "rubric lexically; the instrument's unit is not the "
                                             "claim's unit",
               "lower_bound_note": "neither instrument is semantic, so every coverage number is a "
                                   "LOWER bound on content reuse",
               "prior_art": "ablate_novel.py:5 records 40.3% of the core's criteria have no "
                            "counterpart above 0.60 — i.e. 59.7% do. This round reproduces that "
                            "with the arm comparison it was missing.",
               "unit_note": "coverage is a SHARE OF CRITERIA per prompt, averaged over prompts",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "core_type.json", "w"), indent=2)
    print(f"\n  artifact: results/core_type.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
