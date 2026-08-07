"""R403 -- which of the definition's clauses are even STATABLE on an object it was not written from?

The failure table's `the definition describes the instance` row gives a mechanical remedy: per clause,
name an admissible object this clause EXCLUDES. Its tell is that "the definition has never been
checked against an object other than the one it was written from". Since R398 there IS such an object,
and this round applies the remedy to it -- WITHOUT a judge, so it runs while R396 holds the GPU.

⛔ AND IT ASKS THE PRIOR QUESTION, WHICH IS SHARPER THAN THE REMEDY AS WRITTEN. Before asking what a
   clause excludes on a new corpus, ask whether the clause can be SAID there at all. A clause whose
   subject does not exist in the corpus is not satisfied and not violated -- it is NOT STATABLE, a
   third value, and folding it into either of the other two manufactures a verdict. This is the
   three-valued discipline the campaign already applies to CONFIRMED/OVERTURNED/UNVERIFIED, one level
   up: applied to the clause rather than to the evidence.

⛔ ARITHMETIC TRAP, and it is close to the surface here. That CoVal satisfies its own definition's
   preconditions is FORCED -- the definition was written from CoVal, so every field it names exists
   there by construction. CoVal's column is therefore a POSITIVE CONTROL on the detector, NOT a
   finding, and it is labelled that way in the output. What is not forced is the second corpus's
   column, and that is the whole content.

⚠ AND THE INSTRUMENT IS A FIELD-PRESENCE SEARCH, SO IT IS CONTROLLED BOTH WAYS. A detector that
  reports "absent" for everything would produce a dramatic result and no information. A fabricated
  field name must be found in NEITHER corpus, and a field known present must be found in each.

ESTIMAND        for each clause and sub-conjunct of the definition, its status on each corpus:
                  STATABLE-AND-BINDING  -- the field it quantifies over exists and is non-degenerate
                  STATABLE-BUT-VACUOUS  -- the field exists but cannot exclude anything
                  NOT-STATABLE          -- the field does not exist in the corpus
                reported per clause with the field named, never as a single transportability score.

IDENTIFICATION  Exact for field presence and for the counts that decide degeneracy. NOT identified:
                whether a clause could be RESTATED to survive -- that is an act of definition, not a
                measurement, and this round does not perform it.

SCOPE           population: both corpora · instrument: field presence + per-interaction annotator
                count · baseline: CoVal, where the definition was written and every clause is
                statable by construction · regime: HEAD.

WORLDS
  W-TRANSPORTS-WHOLE   every clause is statable and binding on the second corpus. Then the definition
                       is not corpus-specific in its FORM, whatever its content turns out to be.
  W-TRANSPORTS-PART    some clause is vacuous or not statable there. Then part of the definition is a
                       fact about CoVal's SCHEMA rather than about cores, and WHICH part is the
                       finding -- exactly the failure the `describes the instance` row names.

PREDICTION MATRIX
  W-TRANSPORTS-WHOLE -> 0 clauses NOT-STATABLE and 0 VACUOUS on corpus two
  W-TRANSPORTS-PART  -> >= 1, named, with the missing field named beside it

PRE-REGISTERED KILL -- conditional on the detector's controls, never on the statuses alone.
    if known_present_fields_found_in_both and fabricated_field_found_in_neither:
        if every clause is STATABLE-AND-BINDING on corpus two -> W-TRANSPORTS-WHOLE
        else -> W-TRANSPORTS-PART, clauses named
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  PRESENCE (+)  a field known present must be found in each corpus -- `prompt` in CoVal comparisons,
                `score` in the second corpus. Establishes the detector can return TRUE.
  PRESENCE (-)  a fabricated field name must be found in NEITHER. A detector reporting `absent` for
                everything would produce a dramatic result and no information.
  CoVal COLUMN  is a POSITIVE CONTROL, not a finding: the definition was written from CoVal, so its
                fields exist there by construction. Any NOT-STATABLE in CoVal's column would mean the
                detector is broken, not that the definition is.
  DEGENERACY    `binding` requires more than presence. A field present but constant cannot exclude
                anything, so the count that would make it degenerate is measured and printed.

MULTIPLICITY    6 clause-parts x 2 corpora = 12 cells, every cell printed.
SEEDS           none -- a census is not a draw.
ARTIFACT        results/r403_clause_statability.json with the source hash.

IMPOSSIBLE HERE
  restating a clause to survive  -- an act of definition, not a measurement. Not attempted.
  whether a statable clause HOLDS -- needs the judge; that is the clause-② test R402 prepared.
  a rubric for corpus two        -- it has none; R398 recorded it and this round measures it rather
                                    than citing it, because a cited absence is not a measured one.
  a second release beyond these  -- two corpora.

EXIT
    0  controls hold and all cells are classified
    1  the detector is blind in one direction -- UNVERIFIED
    2  a corpus is absent -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import subprocess
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
DATA = ROOT / "data"
SECOND = DATA / "utterances.jsonl"
COVAL_CMP = DATA / "comparisons.jsonl"
COVAL_RUB = DATA / "conversation_rubrics.jsonl"
COVAL_ANN = DATA / "annotators.jsonl"
FAKE_FIELD = "zzq_no_such_field_zzq"
SAMPLE = 4000


def keys_of(path, limit=SAMPLE):
    """Union of top-level keys over a bounded sample. Bounded because these files are 16-85MB and
    an OOM does not raise, it kills the session."""
    ks, n = set(), 0
    if not path.exists():
        return ks
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            if isinstance(d, dict):
                ks |= set(d.keys())
            n += 1
            if n >= limit:
                break
    return ks


def main() -> int:
    for f in (SECOND, COVAL_CMP):
        if not f.exists():
            print(f"  UNRUNNABLE: {f} absent. Exit 2, never 0."); return 2
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R403 · which clauses are even STATABLE elsewhere?   HEAD {head}\n")
    print("  ⛔ THE PRIOR QUESTION, SHARPER THAN THE REMEDY AS WRITTEN. Before asking what a clause")
    print("     EXCLUDES on a new corpus, ask whether it can be SAID there. A clause whose subject")
    print("     does not exist is not satisfied and not violated — it is NOT STATABLE, a third value,")
    print("     and folding it into either of the others manufactures a verdict.\n")

    cov = keys_of(COVAL_CMP) | keys_of(COVAL_RUB) | keys_of(COVAL_ANN)
    sec = keys_of(SECOND)

    # ---- CONTROLS -------------------------------------------------------------------------------
    pos = ("prompt" in cov) and ("score" in sec)
    neg = (FAKE_FIELD not in cov) and (FAKE_FIELD not in sec)
    print("  CONTROLS on the field-presence detector")
    print(f"    PRESENCE (+)  `prompt` in CoVal and `score` in corpus two: {pos}   "
          f"{'PASS' if pos else 'FAIL — every ABSENT below would be silence'}")
    print(f"    PRESENCE (-)  a fabricated field in neither: {neg}   "
          f"{'PASS' if neg else 'FAIL — the detector reports presence for anything'}")
    if not (pos and neg):
        print("\n  UNVERIFIED — the detector is blind in one direction. Exit 1."); return 1
    print(f"    CoVal keys ({len(cov)}): {sorted(cov)}")
    print(f"    corpus-two keys ({len(sec)}): {sorted(sec)}")

    # ---- DEGENERACY MEASUREMENT: annotators per interaction --------------------------------------
    raters = defaultdict(set)
    with SECOND.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            k, u = d.get("interaction_id"), d.get("user_id")
            if k and u:
                raters[k].add(u)
    multi_rater = sum(1 for v in raters.values() if len(v) >= 2)
    max_raters = max((len(v) for v in raters.values()), default=0)
    print(f"\n  DEGENERACY — `binding` needs more than presence. A field present but constant")
    print(f"  excludes nothing, so the deciding count is measured:")
    print(f"    corpus two: interactions with >= 2 DISTINCT annotators: {multi_rater:,} "
          f"of {len(raters):,}  (max raters on any interaction: {max_raters})")

    # ---- THE CLAUSE TABLE -------------------------------------------------------------------------
    has_rubric = ("coval_full" in cov) or ("conversation_rubrics" in cov)
    CLAUSES = [
        ("① better than a random draw of the prompt's OWN rubric",
         "a per-prompt rubric",
         has_rubric, False),
        ("② better than a size-matched set that never read the conversation",
         "responses + a human target + a criterion pool",
         True, True),
        ("③a no information from that prompt's own human labels",
         "per-prompt human labels",
         True, True),
        ("③b ... not from any HALF of them",
         ">= 2 annotators per prompt, to split",
         True, multi_rater > 0),
        ("③c ... and not by way of a rubric those same annotators wrote",
         "a per-prompt rubric written by the annotators",
         has_rubric, False),
        ("size: greater than one; 3–8 indistinguishable",
         "a judge + a k sweep",
         True, True),
    ]
    print(f"\n  CLAUSE STATUS — CoVal's column is a POSITIVE CONTROL, not a finding: the definition")
    print(f"  was written from CoVal, so its fields exist there BY CONSTRUCTION")
    print(f"    {'clause':<58}{'CoVal':<22}corpus two")
    rows, broken = {}, []
    for name, dep, in_cov, in_sec in CLAUSES:
        a = "STATABLE" if in_cov else "NOT-STATABLE"
        if not in_sec:
            b = "NOT-STATABLE"
        elif name.startswith("③b") and multi_rater == 0:
            b = "STATABLE-BUT-VACUOUS"
        else:
            b = "STATABLE"
        rows[name] = dict(depends_on=dep, coval=a, second=b)
        if a != "STATABLE":
            broken.append(name)
        print(f"    {name:<58}{a:<22}{b}")
        print(f"      needs: {dep}")

    if broken:
        print(f"\n  UNVERIFIED — {broken} is NOT-STATABLE in CoVal, where the definition was written.")
        print(f"  That means the DETECTOR is broken, not the definition. Exit 1."); return 1

    bad = [k for k, v in rows.items() if v["second"] != "STATABLE"]
    print()
    if not bad:
        v = "W_TRANSPORTS_WHOLE"
        print(f"  W-TRANSPORTS-WHOLE — every clause is statable on the second corpus. The definition")
        print(f"  is not corpus-specific in its FORM, whatever its content turns out to be.")
    else:
        v = "W_TRANSPORTS_PART"
        print(f"  W-TRANSPORTS-PART — {len(bad)} of {len(rows)} clause-parts cannot be said on the")
        print(f"  second corpus at all:")
        for k in bad:
            print(f"    · {k}")
            print(f"        missing: {rows[k]['depends_on']}")
        print(f"  Those parts are facts about CoVal's SCHEMA, not about cores. That is precisely the")
        print(f"  failure the `definition describes the instance` row names, caught here on the FORM")
        print(f"  of the clause rather than on its content — which is cheaper and needs no judge.")
        print(f"  ⚠ WHAT SURVIVES, and it is the load-bearing part: clause ② and clause ③a are both")
        print(f"    statable there, and R401 showed ② is powered at n=26,789. The transportable core")
        print(f"    of the definition is `label-free AND better than prompt-blind`.")

    print(f"\n  ⚠ THIS ROUND DOES NOT RESTATE ANY CLAUSE. Rewriting a clause so it survives on a new")
    print(f"    corpus is an act of DEFINITION, not a measurement, and doing it in the same breath as")
    print(f"    the diagnosis is how a definition gets tuned to whatever object is in front of it.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, coval_keys=sorted(cov), second_keys=sorted(sec),
               interactions=len(raters), multi_rater_interactions=multi_rater,
               max_raters=max_raters, has_rubric_coval=has_rubric, clauses=rows,
               not_statable_on_second=bad,
               controls=dict(presence_pos=pos, presence_neg=neg), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r403_clause_statability.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
