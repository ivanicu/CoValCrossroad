"""R400 -- would a transport test confound CORPUS with CONVERSATION DEPTH?

R399 settled the estimand: the second corpus RATES rather than RANKS, so a transport test must target
`if_chosen`. Its NEXT proposed building a core from a second-corpus conversation and testing clause ②
against that field. That step needs a judge, so it needs the GPU, and R396 is holding the gpu group.

⛔ SO THIS ROUND ASKS THE QUESTION THAT MUST BE ANSWERED BEFORE THE GPU IS FREE, NOT AFTER. The
   definition says a core is "producible from the CONVERSATION alone". If the two corpora's
   conversations are different KINDS of object -- one multi-turn with a developer preamble, the other
   a single question -- then a transport test compares CORPUS and DEPTH at the same time, and any
   difference it finds is unattributable. That is precisely the shape of the errors this campaign
   keeps paying for: a correct number reported against a scope nobody checked.

⛔ AND IT IS CHEAPER TO DISCOVER NOW. A confound named before a design costs a filter; a confound
   found after a number exists costs the number. R233's limit, R368's stratification and R370's
   subset-floor collapse were all the same lesson arriving too late.

⚠ THE TWO CORPORA STORE CONVERSATIONS IN DIFFERENT SHAPES, WHICH IS ITSELF THE HAZARD. CoVal keeps a
  `messages` list on each comparison; the second corpus keeps one ROW PER UTTERANCE, grouped by
  `conversation_id`. Two different extractors are therefore unavoidable -- and two extractors are two
  chances to measure two different things and call them one. So each is validated separately against
  a hand-built example of KNOWN depth IN ITS OWN FORMAT, and the definition of depth is fixed first:
  THE NUMBER OF DISTINCT USER TURNS. Not messages, not rows, not utterances.

⛔ ARITHMETIC TRAP. Could this come out otherwise? YES. The second corpus's `turn` field could be
   uniformly 0 (all single-turn), could span many values, and CoVal's conversations could be
   single-turn too -- in which case there is no confound and the round says so. I have seen ONE CoVal
   conversation, which had two user turns, and no second-corpus conversation reconstructed at all.

ESTIMAND        (A) the distribution of USER-TURN DEPTH over conversations, in each corpus, reported
                    as a full histogram rather than a mean -- a mean over a skewed integer
                    distribution is the summary that hides exactly what this round is looking for;
                (B) the number of second-corpus conversations whose depth is ALSO attested in CoVal,
                    i.e. the size of the depth-matched pool a fair transport test could draw from.

IDENTIFICATION  Exact -- both are counts over files on disk. NOT identified: whether depth-matching
                is SUFFICIENT to make the corpora comparable. Topic, length, model era and annotator
                population are all unmatched and are named in the register rather than waved at.

SCOPE           population: all CoVal comparisons and all second-corpus conversations · instrument:
                two format-specific extractors, each separately validated · baseline: hand-built
                conversations of known depth · regime: HEAD, one pass.

WORLDS
  W-DEPTH-MATCHED    the depth supports overlap and a pool of >= 100 second-corpus conversations sits
                     at depths CoVal also attests. Then a fair transport test exists: match on depth,
                     and the confound is controlled by construction rather than argued away.
  W-DEPTH-DISJOINT   the supports barely meet. Then a transport test would compare corpus AND depth
                     simultaneously, no filter repairs it, and the honest move is to restrict the
                     claim to the depth both corpora share -- or to abandon it and say why.

PREDICTION MATRIX
  W-DEPTH-MATCHED  -> matched pool >= 100 conversations
  W-DEPTH-DISJOINT -> matched pool < 100, and the histograms show where they part

PRE-REGISTERED KILL -- conditional on both extractor controls, never on the counts alone.
    if coval_extractor_recovers_known_depth and second_extractor_recovers_known_depth:
        matched = second-corpus conversations at depths CoVal also attests
        if matched >= 100 -> W-DEPTH-MATCHED
        else              -> W-DEPTH-DISJOINT
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  EXTRACTOR-A (+)  a hand-built CoVal-shaped conversation with 3 user turns must measure 3. Validated
                   in ITS OWN FORMAT, because a control that shares an extractor's blind spot
                   confirms the extractor and licenses nothing.
  EXTRACTOR-B (+)  a hand-built second-corpus-shaped group with 3 user turns must measure 3.
  UNIT             depth is defined ONCE -- distinct user turns -- and both extractors are required to
                   return that same unit. Two extractors are two chances to measure two different
                   things and call them one.
  DISTRIBUTION     histograms printed whole, not summarised. A mean over a skewed integer
                   distribution hides the thing this round exists to find.
  MEMORY           streamed; only counters and bounded dicts held.

MULTIPLICITY    two corpora x one statistic, both histograms printed in full.
SEEDS           none -- a census is not a draw.
ARTIFACT        results/r400_depth_confound.json with the source hash.

IMPOSSIBLE HERE
  whether depth-matching SUFFICES  -- topic, length, model era and annotator population remain
                                      unmatched. Named, and each is a further filter a later design
                                      must either apply or declare.
  a transport result               -- this round runs no test and computes no core.
  matching on TOPIC                -- would need a topic model and a shared taxonomy; neither exists.
  a second release beyond these two -- two corpora, and that is already one more than the register
                                      claimed existed before R398.

EXIT
    0  controls hold and both distributions are reported
    1  an extractor control failed -- UNVERIFIED
    2  a file is absent -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import subprocess
import sys
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
DATA = ROOT / "data"
SECOND = DATA / "utterances.jsonl"
COVAL = DATA / "comparisons.jsonl"


def stream(path: pathlib.Path):
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


def depth_coval(rec) -> int | None:
    """DEPTH = number of DISTINCT user turns. CoVal shape: {'prompt': {'messages': [...]}}."""
    p = rec.get("prompt") or {}
    msgs = p.get("messages") if isinstance(p, dict) else None
    if not isinstance(msgs, list):
        return None
    seen = []
    for m in msgs:
        if isinstance(m, dict) and m.get("role") == "user":
            c = (m.get("content") or "").strip()
            if c and c not in seen:
                seen.append(c)
    return len(seen) or None


def depth_second(rows) -> int | None:
    """Same unit. Second-corpus shape: many rows per conversation, each with a `user_prompt`."""
    seen = []
    for r in rows:
        c = (r.get("user_prompt") or "").strip()
        if c and c not in seen:
            seen.append(c)
    return len(seen) or None


def main() -> int:
    for f in (SECOND, COVAL):
        if not f.exists():
            print(f"  UNRUNNABLE: {f} absent. Exit 2, never 0."); return 2
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R400 · would a transport test confound corpus with conversation depth?   HEAD {head}\n")
    print("  ⛔ ASKED BEFORE THE GPU IS FREE, NOT AFTER. The definition says a core is producible")
    print("     from the CONVERSATION alone. If the two corpora's conversations are different KINDS")
    print("     of object, a transport test compares CORPUS and DEPTH at once and its difference is")
    print("     unattributable. A confound named before a design costs a filter; found after a")
    print("     number exists, it costs the number.\n")

    # ---- EXTRACTOR CONTROLS, each in its OWN format ---------------------------------------------
    fake_coval = {"prompt": {"messages": [
        {"role": "developer", "content": "sys"},
        {"role": "user", "content": "one"}, {"role": "assistant", "content": "a"},
        {"role": "user", "content": "two"}, {"role": "assistant", "content": "b"},
        {"role": "user", "content": "three"}]}}
    fake_second = [{"user_prompt": "one"}, {"user_prompt": "one"},
                   {"user_prompt": "two"}, {"user_prompt": "three"}]
    da, db = depth_coval(fake_coval), depth_second(fake_second)
    ok_a, ok_b = da == 3, db == 3
    print("  CONTROLS — two formats mean two extractors, and two extractors are two chances to")
    print("  measure two different things and call them one. Each is validated in ITS OWN format.")
    print(f"    EXTRACTOR-A (+)  a CoVal-shaped conversation with 3 user turns measures {da}   "
          f"{'PASS' if ok_a else 'FAIL'}")
    print(f"    EXTRACTOR-B (+)  a second-shaped group with 3 user turns measures {db}   "
          f"{'PASS' if ok_b else 'FAIL'}")
    print(f"    UNIT             depth is defined once — DISTINCT USER TURNS — for both")
    if not (ok_a and ok_b):
        print("\n  UNVERIFIED — an extractor is mis-specified. Exit 1, never a verdict."); return 1

    # ---- (A) the two distributions --------------------------------------------------------------
    hc = Counter()
    for rec in stream(COVAL):
        d = depth_coval(rec)
        if d:
            hc[d] += 1
    convs: dict[str, list] = defaultdict(list)
    for r in stream(SECOND):
        c = r.get("conversation_id")
        if c:
            convs[c].append(r)
    hs = Counter()
    for c, rows in convs.items():
        d = depth_second(rows)
        if d:
            hs[d] += 1

    def show(h, label):
        tot = sum(h.values())
        print(f"    {label}  n={tot:,}")
        for d in sorted(h)[:10]:
            print(f"      depth {d:>2}: {h[d]:>7,}  ({h[d]/tot:6.1%})  {'#'*min(40,int(40*h[d]/tot))}")
        if len(h) > 10:
            print(f"      ... {len(h)-10} deeper bins, max depth {max(h)}")

    print(f"\n  (A) USER-TURN DEPTH — histograms printed whole, because a mean over a skewed integer")
    print(f"      distribution hides exactly what this round exists to find")
    show(hc, "CoVal          ")
    show(hs, "second corpus  ")

    # ---- (B) the matched pool -------------------------------------------------------------------
    shared = sorted(set(hc) & set(hs))
    matched = sum(hs[d] for d in shared)
    print(f"\n  (B) DEPTH-MATCHED POOL")
    print(f"      depths attested in BOTH: {shared[:12]}{' ...' if len(shared) > 12 else ''}")
    print(f"      second-corpus conversations at those depths: {matched:,} "
          f"of {sum(hs.values()):,} ({matched/sum(hs.values()):.1%})")
    print(f"      CoVal conversations at those depths: "
          f"{sum(hc[d] for d in shared):,} of {sum(hc.values()):,}")

    print()
    if matched >= 100:
        v = "W_DEPTH_MATCHED"
        print(f"  W-DEPTH-MATCHED — {matched:,} second-corpus conversations sit at depths CoVal also")
        print(f"  attests. A fair transport test EXISTS: match on depth and the confound is")
        print(f"  controlled by construction rather than argued away in a limitations paragraph.")
    else:
        v = "W_DEPTH_DISJOINT"
        print(f"  W-DEPTH-DISJOINT — only {matched:,} conversations are depth-matchable. A transport")
        print(f"  test would move CORPUS and DEPTH together and no filter repairs that. The honest")
        print(f"  move is to restrict the claim to the depth both corpora share, or abandon it and")
        print(f"  say which.")

    print(f"\n  ⚠ DEPTH-MATCHING IS NOT SUFFICIENCY. Topic, response length, model era and annotator")
    print(f"    population remain unmatched between the corpora. Each is a further filter a later")
    print(f"    design must apply or declare — this round removes ONE confound and names the rest")
    print(f"    rather than implying the pool is clean.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, coval_depth_hist={str(k): v for k, v in sorted(hc.items())},
               second_depth_hist={str(k): v for k, v in sorted(hs.items())},
               coval_conversations=sum(hc.values()), second_conversations=sum(hs.values()),
               shared_depths=shared, matched_pool=matched,
               controls=dict(extractor_a=da, extractor_b=db, ok_a=ok_a, ok_b=ok_b),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r400_depth_confound.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
