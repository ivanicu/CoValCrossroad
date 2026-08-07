#!/usr/bin/env python3
"""R556 · Register row 5 asks for "a second team OR a second release". One is on disk.

Row 5 lists independent replication as needing "a second team or a second release" and prices it
at "another site". A second release IS here: data/utterances.jsonl, 8,011 conversations, wired
into generate_core.py --corpus second and judge_transport.load_second (R433).

⚠ TWO AXES, NAMED AS SEPARATE STRINGS BEFORE THE CONTROL (§4):
   second JUDGE  = Qwen3.5-0.8B-Base scoring the SAME release   -> used by R536, R537
   second CORPUS = data/utterances.jsonl, a DIFFERENT release   -> usage is what this measures
   These are different axes and I nearly counted judge rounds as corpus rounds.

ESTIMAND  of the claims on the statement's "What stands" table, how many carry a result computed
          on the SECOND CORPUS?
IDENT     fully identified: artifacts on disk record which corpus produced them.
SCOPE     population = round artifacts under E05 · instrument = a key/value scan of results JSON ·
          baseline = zero second-corpus results · regime = this repo.
WORLDS    A the second corpus has been used -> row 5's "another site" price is wrong and the
            replication axis is partly discharged here.
          B it is present but unused -> row 5's price is right in PRACTICE but wrong in KIND:
            what is missing is not a site, it is a round.
KILL      pre-registered: >=1 artifact whose recorded corpus is the second release -> WORLD A.
POS CTRL  the scan must find artifacts recording the HOME corpus, else a zero is silence.
NEG CTRL  an invented corpus token must appear in no artifact.
ARTIFACT  results/second_release.json
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"

def walk(o, hit, depth=0):
    """Collect every string value and key anywhere in a JSON artifact."""
    if depth > 6: return
    if isinstance(o, dict):
        for k, v in o.items():
            hit.add(str(k).lower())
            walk(v, hit, depth + 1)
    elif isinstance(o, list):
        for v in o[:200]: walk(v, hit, depth + 1)
    elif isinstance(o, str) and len(o) < 200:
        hit.add(o.lower())

arts = sorted(E05.rglob("results/*.json"))
if not arts:
    print("  no artifacts -> UNRUNNABLE"); sys.exit(2)

SECOND = {"second", "corpus=second", "utterances.jsonl", "load_second", "second_corpus",
          "_08b", "second-path"}
HOME   = {"home", "corpus=home", "comparisons.jsonl", "conversation_rubrics.jsonl"}
FAKE   = {"corpus=notarealcorpus9z"}

n_second, n_home, n_fake, second_files = 0, 0, 0, []
for a in arts:
    try: d = json.loads(a.read_text())
    except Exception: continue
    hit = set(); walk(d, hit)
    blob = " ".join(hit)
    # ⚠ the SECOND-CORPUS token must not be satisfied by the SECOND-JUDGE token. Require a
    #   corpus-specific marker, never the bare word "second".
    # ⛔ FIRST VERSION MATCHED THE TOKEN ANYWHERE and returned 4. One hit was R550's gate audit,
    # whose amended-rounds dict contains the DIRECTORY NAME
    # "R399_what_estimand_does_the_second_corpus_admit". The instrument matched a round's NAME
    # and I would have reported it as a corpus RESULT. §4: a search is an instrument.
    # Require the marker to be a DATA PATH in a value, not a substring of a key.
    raw = a.read_text()
    is_sec = ("data/utterances.jsonl" in raw or '"corpus": "second"' in raw
              or "corpus=second" in raw)
    if is_sec: n_second += 1; second_files.append(str(a.relative_to(ROOT)))
    if any(t in blob for t in HOME): n_home += 1
    if any(t in blob for t in FAKE): n_fake += 1

print(f"  POSITIVE CONTROL  artifacts recording the HOME corpus: {n_home} -> "
      f"{'PASS' if n_home else 'FAIL -- a zero elsewhere would be silence'}")
print(f"  NEGATIVE CONTROL  an invented corpus token appears in: {n_fake} -> "
      f"{'PASS' if n_fake == 0 else 'FAIL'}")
if not n_home or n_fake:
    sys.exit(2)

print(f"\n  artifacts scanned: {len(arts)}")
print(f"  recording the SECOND CORPUS (utterances.jsonl / corpus=second / load_second): {n_second}")
for f in second_files[:8]: print(f"    {f}")

world = "A" if n_second else "B"
print(f"\n  WORLD {world} -- " + (
    "the second corpus HAS produced results; row 5's 'another site' price is wrong."
    if world == "A" else
    "the second release is present and UNUSED. Row 5's price is wrong in KIND: what is missing "
    "is not a SITE, it is a ROUND."))
(pathlib.Path(__file__).parent / "results" / "second_release.json").write_text(json.dumps(
    {"world": world, "artifacts_scanned": len(arts), "n_second_corpus": n_second,
     "n_home_corpus": n_home, "second_corpus_files": second_files[:20],
     "axis_note": "second JUDGE (0.8B, same release) is a DIFFERENT axis and is excluded here"},
    indent=2))
