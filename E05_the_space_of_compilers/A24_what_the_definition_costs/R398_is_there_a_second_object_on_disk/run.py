"""R398 -- the impossibility register says "one release". Is that a wall, or a query never run?

DEFINITION.md line 193 registers `transfer to another release` as impossible, requiring "one release"
-- meaning a second one. Every transport result in the campaign is bounded by it, and R233's limit is
stated in the definition in the strongest possible terms: the fresh responses carry NO HUMAN
RANKINGS, so transport is of the COMPILATION, "and never agreement with people".

⛔ THIS CAMPAIGN'S OWN FAILURE TABLE HAS AN ENTRY FOR EXACTLY THIS. "A wall never checked": three
   permanent limits of a dataset, one of which was a query nobody ran. And separately: "a retraction
   feels so much like the end of an audit that nobody asks the cheapest question left -- does the
   data have more to give? Here it had 5x more, sitting on disk, unused through three rounds of
   increasingly careful reasoning about what could not be known."

⛔ SO THIS ROUND ASKS THE CHEAPEST QUESTION LEFT, AND IT IS EMBARRASSING THAT IT IS STILL UNASKED.
   `data/` holds 215MB. Two of its files -- utterances.jsonl (68MB) and metadata.jsonl (85MB) --
   are dated two days AFTER the four release files, are absent from DATASET_CARD.md, and a literal
   search of every .py and .md in the repository returns ZERO references to either. 153MB fetched
   and never opened.

⚠ AND THE EXCITEMENT IS THE RED FLAG, WHICH IS WHY THE DESIGN IS A CENSUS AND NOT A TRANSPORT TEST.
  A head of one line shows fields -- user_prompt, model_response, model_name, score, if_chosen,
  conversation_type -- that are NOT CoVal's schema and that LOOK like exactly what the definition
  needs. That appearance is worth nothing until counted. This round establishes only WHETHER a usable
  second object is present. It runs no transport test, computes no core, and reports no effect.

⛔ ARITHMETIC TRAP. Could this come out otherwise? YES. The files could be CoVal auxiliaries under
   different names, could be truncated, could carry no populated scores, or could have one response
   per prompt -- which would make ranking impossible and the wall real. I have read ONE line of each.

ESTIMAND        whether `data/utterances.jsonl` constitutes a SECOND corpus usable by this
                definition, decomposed into four counts, each reported separately:
                  (1) rows and distinct conversations
                  (2) the share of rows carrying a numerically parseable human `score`
                  (3) the number of prompts with >= 2 DISTINCT model responses (ranking needs a pair)
                  (4) the number of distinct models, since a prompt-blind baseline needs variation
                A single "usable" boolean would hide which of the four fails, so all four are printed
                whatever the verdict.

IDENTIFICATION  Exact -- these are counts over a file on disk. NOT identified: whether the scores are
                COMPARABLE to CoVal's human rankings, whether the two corpora share a population, and
                whether any core transports. Those are later rounds and this one must not pre-empt
                them by wording its verdict as though it had measured them.

SCOPE           population: the rows of data/utterances.jsonl · instrument: a streaming JSON reader ·
                baseline: the same reader run against a KNOWN CoVal file · regime: HEAD, one pass.

WORLDS
  W-SECOND-OBJECT   a second corpus is present with human-scored responses and >= 2 responses per
                    prompt. Then the register's `one release` line is FALSE, it has been false since
                    at least the fetch date, and the campaign's largest stated limit -- transport, and
                    "never agreement with people" -- becomes testable rather than structural.
  W-WALL-REAL       the files cannot serve: no scores, or one response per prompt, or malformed.
                    Then the wall stands and is CHECKED rather than assumed, which is worth the eight
                    minutes on its own, because an unchecked wall is UNVERIFIED and not SETTLED.

PREDICTION MATRIX
  W-SECOND-OBJECT -> >= 100 conversations AND score-share >= 0.5 AND >= 100 prompts with >= 2 responses
  W-WALL-REAL     -> any one of those fails, and WHICH one is the finding

PRE-REGISTERED KILL -- conditional on the reader's controls, never on the counts alone.
    if reader_parses_known_coval_file and reader_returns_zero_on_a_nonexistent_path:
        if conversations >= 100 and score_share >= 0.5 and multi_response_prompts >= 100:
            -> W-SECOND-OBJECT
        else -> W-WALL-REAL, naming which criterion failed
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  READER (+)  the same streaming reader must parse a KNOWN-GOOD CoVal file and return non-zero rows.
              A count of zero from a reader never shown to return non-zero is silence, not evidence
              that the file is empty.
  READER (-)  pointed at a path that does not exist it must return zero and say so, rather than
              raising into a traceback that a caller might read as "no data".
  MEMORY      streamed line by line. The file is 68MB and an OOM does not raise, it kills the
              session -- so nothing accumulates except counters and bounded sets.
  PRIOR ART   the zero-references claim is RE-MEASURED here rather than quoted from my shell history,
              because it is the sentence that makes this round look like a discovery.

MULTIPLICITY    four criteria, all four printed whatever the verdict, so a pass on three and a fail
                on one cannot be reported as a pass.
SEEDS           none -- a census is not a draw.
ARTIFACT        results/r398_second_object.json with the source hash.

IMPOSSIBLE HERE
  whether the scores are comparable to CoVal's rankings -- needs a shared population or a linking
                                                            study; named, not assumed either way.
  whether any core transports                          -- a later round. This one runs no test.
  the corpus's provenance and licence                  -- the schema resembles a published dataset,
                                                            but naming it from field names is D5 and
                                                            the finding does not need the name.
  a rubric for the second corpus                       -- CoVal's `full` has no counterpart here, so
                                                            clauses defined against `full` cannot
                                                            transport even if clause 2 can.

EXIT
    0  controls hold and the census is reported
    1  a control misbehaved -- UNVERIFIED
    2  the file is absent -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
DATA = ROOT / "data"
TARGET = DATA / "utterances.jsonl"
KNOWN_GOOD = DATA / "comparisons.jsonl"


def stream(path: pathlib.Path, limit: int | None = None):
    """Streaming reader. Nothing accumulates: an OOM does not raise, it kills the session."""
    n = 0
    if not path.exists():
        return
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue
            n += 1
            if limit and n >= limit:
                return


def main() -> int:
    if not TARGET.exists():
        print(f"  UNRUNNABLE: {TARGET} absent. Exit 2, never 0."); return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R398 · is `one release` a wall, or a query never run?   HEAD {head}\n")
    print("  ⛔ THE CHEAPEST QUESTION LEFT, AND IT IS EMBARRASSING THAT IT WAS STILL UNASKED.")
    print("     DEFINITION.md registers `transfer to another release` as impossible, requiring a")
    print("     second release — and the campaign's own failure table has an entry for a wall")
    print("     nobody checked, and another for never asking whether the data has more to give.\n")

    # ---- PRIOR ART, re-measured rather than quoted ----------------------------------------------
    refs = subprocess.run(
        ["grep", "-rl", "utterances.jsonl", "--include=*.py", "--include=*.md", "."],
        cwd=str(ROOT), capture_output=True, text=True).stdout.strip().splitlines()
    refs = [r for r in refs if "R398" not in r]
    print(f"  PRIOR ART — re-measured here, not quoted from my shell history, because it is the")
    print(f"  sentence that makes this round look like a discovery")
    print(f"    files referencing `utterances.jsonl` (excluding this round): {len(refs)}  {refs[:3]}")
    print(f"    size on disk: {TARGET.stat().st_size/1e6:.0f} MB   "
          f"fetched {TARGET.stat().st_mtime and ''}"
          f"{__import__('time').strftime('%Y-%m-%d', __import__('time').localtime(TARGET.stat().st_mtime))}")

    # ---- READER CONTROLS ------------------------------------------------------------------------
    known_rows = sum(1 for _ in stream(KNOWN_GOOD, limit=50))
    ghost_rows = sum(1 for _ in stream(DATA / "zzq_no_such_file_zzq.jsonl", limit=50))
    pos_ok, neg_ok = known_rows > 0, ghost_rows == 0
    print(f"\n  CONTROLS on the streaming reader")
    print(f"    READER (+)  a KNOWN-GOOD CoVal file yields {known_rows} rows   "
          f"{'PASS' if pos_ok else 'FAIL — a zero below would be silence'}")
    print(f"    READER (-)  a nonexistent path yields {ghost_rows} rows   "
          f"{'PASS' if neg_ok else 'FAIL'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the reader is blind in one direction. Exit 1."); return 1

    # ---- THE CENSUS — four criteria, all printed regardless of the verdict -----------------------
    print(f"\n  CENSUS of {TARGET.name} — streamed, nothing accumulated but counters")
    rows = 0
    convs, models = set(), set()
    scored = 0
    prompt_responses: dict[str, set] = {}
    for d in stream(TARGET):
        rows += 1
        c = d.get("conversation_id")
        if c:
            convs.add(c)
        m = d.get("model_name")
        if m:
            models.add(m)
        s = d.get("score")
        try:
            if s is not None and str(s).strip() not in ("", "None", "nan"):
                float(s); scored += 1
        except Exception:
            pass
        key = d.get("interaction_id") or c
        r = d.get("model_response")
        if key and r:
            prompt_responses.setdefault(key, set()).add(hash(r) if False else r[:160])

    multi = sum(1 for v in prompt_responses.values() if len(v) >= 2)
    share = scored / rows if rows else 0.0
    print(f"    (1) rows {rows:,} · distinct conversations {len(convs):,}")
    print(f"    (2) rows with a parseable human `score`: {scored:,}  ({share:.1%})")
    print(f"    (3) prompts with >= 2 DISTINCT model responses: {multi:,} "
          f"of {len(prompt_responses):,}")
    print(f"    (4) distinct models: {len(models)}   {sorted(models)[:6]}")

    ok = [len(convs) >= 100, share >= 0.5, multi >= 100]
    names = ["conversations>=100", "score_share>=0.5", "multi_response_prompts>=100"]
    failed = [n for n, o in zip(names, ok) if not o]

    print()
    if all(ok):
        v = "W_SECOND_OBJECT"
        print(f"  W-SECOND-OBJECT — a second corpus IS present, with human-scored responses and")
        print(f"  {multi:,} prompts carrying at least two distinct model responses. The register's")
        print(f"  `transfer to another release — one release` line is FALSE, and has been false since")
        print(f"  the day these files were fetched. The campaign's largest stated limit — that")
        print(f"  transport is of the COMPILATION and `never agreement with people` — is not")
        print(f"  structural. It is untested.")
        print(f"  ⚠ AND THIS ROUND TESTED NOTHING ELSE. It computed no core, ran no transport, and")
        print(f"    reports no effect. `A second object exists` is the whole claim.")
        print(f"  ⚠ AND CLAUSES DEFINED AGAINST `full` STILL CANNOT TRANSPORT: this corpus has no")
        print(f"    rubric, so only clause ② and the human-agreement target have a counterpart here.")
    else:
        v = "W_WALL_REAL"
        print(f"  W-WALL-REAL — the wall stands, and is now CHECKED rather than assumed. Failing")
        print(f"  criteria: {failed}. An unchecked wall is UNVERIFIED, not SETTLED, and the eight")
        print(f"  minutes this cost bought the difference.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, target=str(TARGET.relative_to(ROOT)),
               size_bytes=TARGET.stat().st_size, prior_art_references=len(refs),
               rows=rows, conversations=len(convs), scored=scored, score_share=round(share, 4),
               prompts=len(prompt_responses), multi_response_prompts=multi,
               models=sorted(models)[:40], n_models=len(models),
               criteria=dict(zip(names, ok)), failed=failed,
               controls=dict(known_good_rows=known_rows, ghost_rows=ghost_rows,
                             pos_ok=pos_ok, neg_ok=neg_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r398_second_object.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
