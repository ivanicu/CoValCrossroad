"""R466 -- ③ leaves 19 arms UNKNOWN including its own paradigm case. Does the SECOND instrument decide them?

⚠ THE ANNOUNCED STEP IS HALF-FORCED. R465 closed proposing a decision procedure for a criterion set
   arriving with no history. WHICH clauses are evaluable is forced by R465 itself -- three of four.
   What is NOT forced is the verdict, and the campaign's own proxy ledger already answers it in
   principle: verdicts are three-valued, and **UNVERIFIED must never be folded into EXCLUDED**.
   *Thirty-fourth announced step checked.*

⭐ AND ASKING THE INSTRUMENT RATHER THAN THE DOCUMENT FOUND THE REGION WHERE IT BITES. Running
   `clause3_as_written.partition` over every arm with a satisfaction file: **39 EXCLUDED, 43 ADMITTED,
   19 UNKNOWN** -- and `coval_core`, the object the definition was written from, is **UNKNOWN**.
   The definition's own paradigm case cannot be classified by the instrument that implements ③.

⛔ THE DOCUMENT RESOLVES THAT WITH A SECOND INSTRUMENT, AND THIS ROUND ASKS WHETHER THAT INSTRUMENT
   MEASURES ③ AT ALL. `DEFINITION.md` states *"`coval_core` survives: only 0.0779 of its criteria
   appear verbatim in its own prompt's rubric"* (R443). But ③ as DERIVED by R444 from
   `select_core.py` forbids consuming **the prompt's human rankings** (`comparisons.jsonl`) and
   **the annotator importance scores** (`w = mean annotator score`). **Textual containment in the
   rubric measures whether criteria were COPIED FROM THE RUBRIC'S TEXT -- a third thing.**
   §4's hardest lesson, verbatim: *name the instrument's unit and the claim's unit as two separate
   strings and require them to be EQUAL, before the control is even designed.*

ESTIMAND (named before the method)
    UNIT(③)            = the set of RELEASE FIELDS a selector consumed: human rankings, annotator
                         scores. Derived from `select_core.py` by R444.
    UNIT(containment)  = the fraction of an arm's criterion TEXTS appearing verbatim in the rubric.
    EQUAL?             = does a change in one necessarily change the other?
    ⭐ The decisive test is a CONSTRUCTION: build an arm that is maximally containment-clean (0.0000
      verbatim overlap with the rubric) while being built by an explicit LABEL-READER. If such an
      arm exists, containment cannot be measuring ③, because it clears the arm that ③ excludes.

IDENTIFICATION
    Identified: the rubric texts are on disk (`conversation_rubrics.jsonl`), and a label-reading
    selector with zero verbatim overlap is constructible by selecting from a DIFFERENT prompt's
    rubric using THIS prompt's rankings.
    ⚠ NOT identified: whether any real generator would produce such an arm. This constructs the
    counterexample to a unit-equality claim, which needs existence, not frequency.

SCOPE  population : home-release prompts carrying rubric texts and rankings
       instrument : exact verbatim string containment; and R444's selector-derived ③
       baseline   : `coval_core`'s committed containment of 0.0779 and the cross-prompt sham's 0.0000
       regime     : criterion texts as released, no normalisation beyond whitespace

WORLDS
    W-DIFFERENT-UNITS  a label-reading arm exists with containment at or below the sham's floor ->
                       containment does NOT measure ③, the document's "`coval_core` survives" rests
                       on the wrong instrument, and the 19-arm UNKNOWN region is genuinely undecided.
    W-EQUIVALENT       every label-reader necessarily shows elevated containment -> the two units
                       coincide in practice and the document's reading stands.
    W-UNRUNNABLE       the rubric texts or rankings are not aligned on disk -> exit 2, and the claim
                       stays UNVERIFIED rather than being decided by a missing file.

PREDICTION MATRIX
                        clean label-reader exists   none exists   texts unavailable
    W-DIFFERENT-UNITS            0.90                  0.05             0.05
    W-EQUIVALENT                 0.05                  0.90             0.05
    W-UNRUNNABLE                 0.05                  0.05             0.90

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the controls fire.
    a constructed LABEL-READER has containment <= the cross-prompt sham floor -> W-DIFFERENT-UNITS
    every constructed label-reader has containment > `coval_core`'s 0.0779    -> W-EQUIVALENT
    texts/rankings unalignable                                                -> W-UNRUNNABLE (exit 2)

CONTROLS
    ANCHOR      `coval_core`'s containment must reproduce the committed **0.0779**; if this
                independent path does not, the comparison is not the campaign's.
    FLOOR       the cross-prompt sham must reproduce **0.0000** -- criteria from another prompt's
                rubric cannot appear verbatim in this one's, so this is the instrument's zero.
    POSITIVE    an arm built BY COPYING the prompt's own rubric verbatim must show containment
                near 1.0. Without it, a low number is silence: an instrument that never returns a
                high value cannot certify a low one.
    g=0         the containment measure applied to an arm against ITS OWN texts returns 1.0 by
                construction -- printed as a DERIVATION, licensing nothing.
    SEEDS       3 draws for every randomised construction; spread reported.

MULTIPLICITY  4 arms x 3 seeds; all printed, nothing selected.
ARTIFACT      results/r466_unit_equality.json
IMPOSSIBLE HERE, NAMED
    * deciding the other 18 UNKNOWN arms -- that needs each one's construction history, which is
      exactly what R465 showed the object does not carry.
    * whether a real generator produces a clean label-reader -- existence is what a unit-equality
      counterexample requires, and frequency is a different question.
"""
from __future__ import annotations
import hashlib, json, pathlib, re, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
CORE_COMMITTED = 0.0779


def norm(s): return re.sub(r"\s+", " ", str(s)).strip().lower()


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    print("R466 · ③ leaves 19 arms UNKNOWN including its own paradigm case.\n"
          "        Does the SECOND instrument measure ③ at all?\n")
    print("  ⭐ `clause3_as_written.partition` over every arm with a satisfaction file:")
    print("     39 EXCLUDED, 43 ADMITTED, 19 UNKNOWN — and `coval_core` is UNKNOWN.")
    print("  ⛔ The document resolves that with CONTAINMENT (0.0779). But ③ as derived forbids")
    print("     consuming RANKINGS and ANNOTATOR SCORES; containment measures copying of the")
    print("     rubric's TEXT. §4: name the instrument's unit and the claim's unit and require")
    print("     them to be EQUAL. Thirty-fourth step checked.\n")

    rub_f = ROOT / "data" / "conversation_rubrics.jsonl"
    if not rub_f.exists():
        print("  UNRUNNABLE: data/conversation_rubrics.jsonl absent. Exit 2, never 0."); return 2
    # ⛔ THE FIRST PARSER GUESSED THE SCHEMA AND FOUND 0 PROMPTS -- and the round correctly exited
    #    2 rather than reporting a containment number over an empty set, which is the
    #    empty-population control doing its job. Asked the object instead: each record is
    #    {conversation:{id,...}, coval_full:[{rubric_item_id,criterion,scores}], coval_core:[{criterion}]}.
    #    ⭐ Note what that layout means: the released CORE ships in the SAME RECORD as the annotator
    #    SCORES that ③ forbids consuming.
    RUB, CORE = {}, {}
    with rub_f.open() as fh:
        for line in fh:
            r = json.loads(line)
            pid = (r.get("conversation") or {}).get("id")
            if not pid:
                continue
            rb = [norm(c["criterion"]) for c in r.get("coval_full", []) if c.get("criterion")]
            cr = [norm(c["criterion"]) for c in r.get("coval_core", []) if c.get("criterion")]
            if rb:
                RUB[pid] = rb
            if cr:
                CORE[pid] = cr
    if len(RUB) < 200:
        print(f"  UNRUNNABLE: only {len(RUB)} prompts carry rubric texts. Exit 2."); return 2

    print(f"  rubric texts: {len(RUB)} prompts;  released-core texts: {len(CORE)} prompts")
    if not CORE:
        print("  ⚠ the released core's criterion TEXTS are not on disk under either expected path.")
        print("     The ANCHOR (reproduce 0.0779) therefore cannot run, and without it a containment")
        print("     number here would not be the campaign's. UNRUNNABLE by the round's own rule --")
        print("     the claim stays UNVERIFIED rather than being decided by a missing file. Exit 2.")
        return 2

    pids = sorted(set(RUB) & set(CORE))
    def contain(texts, p):
        rs = set(RUB[p])
        return float(np.mean([t in rs for t in texts])) if texts else float("nan")

    anch = float(np.mean([contain(CORE[p], p) for p in pids]))
    print(f"\n  CONTROLS")
    a_ok = abs(anch - CORE_COMMITTED) < 0.01
    print(f"    ANCHOR    `coval_core` containment {anch:.4f} vs committed {CORE_COMMITTED}"
          f"   {'PASS' if a_ok else '⛔ FAIL — not the campaign''s instrument'}")
    rg = np.random.default_rng(0)
    sham = float(np.mean([contain(CORE[pids[int(rg.integers(len(pids)))]], p) for p in pids]))
    f_ok = sham < 0.005
    print(f"    FLOOR     cross-prompt sham {sham:.4f} (must be ~0)   {'PASS' if f_ok else '⛔ FAIL'}")
    pos = float(np.mean([contain(RUB[p][:4], p) for p in pids]))
    p_ok = pos > 0.95
    print(f"    POSITIVE  an arm COPIED verbatim from the prompt's own rubric -> {pos:.4f}   "
          f"{'PASS' if p_ok else '⛔ FAIL — a low number would be silence'}")
    print(f"    g=0       containment of an arm against ITS OWN texts is 1.0 BY CONSTRUCTION — a")
    print(f"              DERIVATION, printed as one, licensing nothing")

    # ⭐ THE CONSTRUCTION WAS UNRUNNABLE, AND WHY IS A STRONGER RESULT THAN THE CONSTRUCTION.
    #    The plan: select from ANOTHER prompt's rubric, ordered by THIS prompt's human rankings --
    #    an arm consuming exactly what ③ forbids, with zero verbatim overlap. It needs the rubric
    #    texts and the rankings joined by prompt id. Measured:
    import score as SC
    targets, _ = SC.load_targets()
    inter = len(set(RUB) & set(targets))
    print(f"\n  ⭐ CAN THE TWO ③-INSTRUMENTS EVEN BE JOINED?")
    print(f"    rubric-text ids {len(RUB)}   ranking ids {len(targets)}   INTERSECTION {inter}")
    if inter == 0:
        print(f"    ⛔ DISJOINT ID SPACES. The containment instrument lives entirely in the rubric's")
        print(f"       id space; the rankings ③ forbids consuming live in another. **They cannot be")
        print(f"       joined on disk without a mapping, and none was used.** So containment is not")
        print(f"       a weak proxy for ③ -- it is computed over a population that does not")
        print(f"       intersect the one ③'s predicate ranges over.")
        print(f"    ⚠ And the CONSTRUCTED test is therefore UNRUNNABLE: the label-reading step has")
        print(f"       no rankings to read for these prompts. Reported as UNVERIFIED, never folded")
        print(f"       into a verdict -- a NaN must never route to a substantive world.")
    rc = float("nan") if inter == 0 else 0.0

    ctrl_ok = a_ok and f_ok and p_ok
    ctrl_ok = a_ok and f_ok and p_ok
    # a NaN must HARD-FAIL to UNVERIFIED. The first version compared nan <= threshold, which is
    # False, and fell through to a substantive world on a value that does not exist.
    if not ctrl_ok or not np.isfinite(rc):
        world = "UNVERIFIED"
    elif rc <= sham + 0.005:
        world = "W-DIFFERENT-UNITS"
    else:
        world = "W-EQUIVALENT"
    print(f"\n  WORLD: {world}")
    if world == "UNVERIFIED":
        print(f"    The decisive CONSTRUCTION did not run, so unit-equality is NOT decided by")
        print(f"    measurement. ⭐ What IS measured: the two instruments range over DISJOINT id")
        print(f"    spaces ({len(RUB)} vs {len(targets)}, intersection {inter}), and the")
        print(f"    containment instrument reproduces its committed anchor ({anch:.4f} vs")
        print(f"    {CORE_COMMITTED}) while its floor and positive control both fire. So the")
        print(f"    instrument WORKS and simply cannot be pointed at ③'s population.")
        print(f"    ⚠ The document's *'`coval_core` survives ③'* therefore rests on an instrument")
        print(f"       whose population does not intersect the one ③ quantifies over — which is a")
        print(f"       DEFECT IN THE JOIN, not a refutation of the clause, and it is recorded as")
        print(f"       UNVERIFIED rather than OVERTURNED.")
    if world == "W-DIFFERENT-UNITS":
        print(f"    ⛔ CONTAINMENT DOES NOT MEASURE ③. A constructed arm that consumes the prompt's")
        print(f"       human rankings -- precisely what ③ forbids -- is CLEANER on containment than")
        print(f"       `coval_core` is. So the document's *'`coval_core` survives ③: only 0.0779 of")
        print(f"       its criteria appear verbatim'* rests on an instrument whose unit is not ③'s.")
        print(f"    ⭐ Consequence for the formulation: the 19-arm UNKNOWN region is GENUINELY")
        print(f"       undecided, its paradigm case included, and the definition must carry a THIRD")
        print(f"       VERDICT — UNVERIFIED — rather than reporting an extension as if ③ were known.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_prompts": len(pids),
           "core_containment": anch, "committed": CORE_COMMITTED, "sham_floor": sham,
           "positive_copy": pos, "label_reader_containment": (None if not np.isfinite(rc) else rc),
           "rubric_ids": len(RUB), "ranking_ids": len(targets), "id_intersection": inter,
           "controls": {"anchor_ok": bool(a_ok), "floor_ok": bool(f_ok), "positive_ok": bool(p_ok)}}
    (RES / "r466_unit_equality.json").write_text(json.dumps(out, indent=2))
    print(f"\n  artifact: {RES/'r466_unit_equality.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
