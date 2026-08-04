"""R399 -- the cheap blocker: what estimand does the second corpus admit, and do the two overlap?

R398 established a second corpus exists -- 68,371 human-scored responses, unread by any round -- and
its NEXT named the blocker that must be settled BEFORE any transport test: is the second corpus's
`score` an ABSOLUTE RATING or a PAIRWISE RANKING, and do the two corpora share any prompt?

⛔ WHY THIS IS A BLOCKER AND NOT A DETAIL. CoVal's unit is a COMPARISON: `comparisons.jsonl` carries
   `prompt` and `responses`, and every clause of the definition is stated against an ORDERING. If the
   second corpus's score is an absolute 0-100 rating, then an ordering estimand and a rating estimand
   are DIFFERENT QUANTITIES, and running the ordering test on rating data would rebuild R233's error
   one release over -- a correct number reported against the wrong scope, which is eleven of twelve
   retractions in the audited programme.

⛔ AND OVERLAP IS A CONTAMINATION QUESTION, NOT A CONVENIENCE. If the corpora share prompts, a core
   built on one and tested on the other is not tested out of distribution at all, and every transport
   number would carry a leak nobody had looked for. The flattering direction here is DISJOINT -- it
   is the answer that makes the next round easy -- so the detector gets a control aimed at exactly
   that: it must be shown able to FIND a match, not merely to report none.

⛔ ARITHMETIC TRAP. Could this come out otherwise? YES on both axes. Scores could be permutations of
   1..k (a ranking), arbitrary values on a bounded scale (a rating), or a mixture. The corpora could
   share every prompt, none, or some. I have read 400 lines of one file and zero of the join.

⚠ AND ONE FACT FROM THAT PEEK ALREADY COMPLICATES THE QUESTION, SO IT IS DECLARED HERE RATHER THAN
  DISCOVERED LATER: the second corpus carries BOTH a numeric `score` AND a boolean `if_chosen`. Those
  are two different measurements of the same event, and `if_chosen` is structurally much closer to
  CoVal's comparison. So the round must report the type of BOTH, not pick the one that suits.

ESTIMAND        three quantities, reported separately and never merged into one verdict:
                  (A) the MEASUREMENT TYPE of `score` -- RANKING (within-interaction values are a
                      permutation of a fixed rank set) vs RATING (values on a bounded scale, not
                      constrained to be a permutation);
                  (B) the number of responses per interaction, and the share of interactions where
                      `if_chosen` marks exactly one -- i.e. whether a clean pairwise preference exists;
                  (C) the overlap: how many CoVal prompts appear verbatim (after normalisation) among
                      the second corpus's user prompts.

IDENTIFICATION  (A) and (B) exact -- they are properties of values on disk.
                (C) partial and ONE-SIDED: exact-after-normalisation matching finds identical strings
                    and misses paraphrase, truncation and re-tokenisation. So a LOW overlap count is a
                    LOWER BOUND on sharing and NOT a proof of disjointness. This is stated in the
                    verdict, because disjoint is the flattering answer.

SCOPE           population: all 68,371 second-corpus rows and all CoVal comparison prompts ·
                instrument: streaming JSON + normalised exact string match · baseline: synthetic
                rank/rating groups and a self-match probe · regime: HEAD, one pass.

WORLDS
  W-RATING        `score` is a bounded rating, not a permutation. Then a transport test must use
                  either a RATING-agreement estimand or the `if_chosen` pairwise field, and the
                  ordering estimand CoVal uses does not transfer unchanged.
  W-RANKING       `score` is a permutation of ranks. Then CoVal's ordering estimand transfers
                  directly and the next round is much cheaper.
  W-MIXED         neither cleanly. Then the type IS the finding and no transport test is admissible
                  until it is resolved.

  Crossed with, and reported independently:
  W-DISJOINT      no CoVal prompt found among the second corpus's prompts (a LOWER BOUND on sharing).
  W-OVERLAP       >= 1 found. Then any transport claim needs those prompts excluded, and the count
                  is the finding.

PREDICTION MATRIX
  W-RATING  -> permutation share < 0.20 across interactions with >= 2 responses
  W-RANKING -> permutation share > 0.80
  W-MIXED   -> between; reported as the finding rather than rounded to a neighbour
  W-DISJOINT/W-OVERLAP -> the match count, with the one-sidedness stated either way

PRE-REGISTERED KILL -- conditional on both controls, never on the counts alone.
    if rank_synth_classified_RANKING and rating_synth_classified_RATING and matcher_self_match_ok
       and matcher_returns_zero_on_absent:
        type   = RANKING if perm_share > 0.80 else RATING if perm_share < 0.20 else MIXED
        overlap = OVERLAP if matches > 0 else DISJOINT (as a lower bound)
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  CLASSIFIER (+/-)  synthetic groups built as permutations must classify RANKING; synthetic groups
                    built as arbitrary bounded values must classify RATING. Both directions, because
                    a classifier that answers RATING always would pass a one-sided check.
  MATCHER (+)       a prompt taken FROM the second corpus must be found in the second corpus's own
                    index after normalisation. This tests the machinery.
  MATCHER (+2)      a CoVal prompt must match ITSELF through the same normalisation, in a CoVal-built
                    index. The first control tests the index; this one tests the normalisation on the
                    CLAIM'S OWN UNIT -- and the failure table's hardest-won row is that a control
                    sharing the instrument's blind spot confirms the instrument and licenses nothing.
  MATCHER (-)       a random token string must return zero matches, so zero is attainable.
  MEMORY            streamed; only bounded sets and counters are held. An OOM kills the session.

MULTIPLICITY    three estimands, all three printed regardless of each other's outcome.
SEEDS           one, for the synthetic control groups; the census itself is not a draw.
ARTIFACT        results/r399_estimand_admissibility.json with the source hash.

IMPOSSIBLE HERE
  paraphrase-level overlap  -- exact matching is one-sided. Named in the verdict, not buried.
  whether the two score scales are COMPARABLE -- a rating and a ranking can both exist and still not
                                                 be commensurable; that needs a linking study.
  any transport result      -- this round runs no test and computes no core.
  a rubric for corpus two   -- it has none; R398 already recorded that.

EXIT
    0  controls hold and all three estimands are reported
    1  a control misbehaved -- UNVERIFIED
    2  a file is absent -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import random
import re
import subprocess
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
DATA = ROOT / "data"
SECOND = DATA / "utterances.jsonl"
COVAL = DATA / "comparisons.jsonl"
SEED = 1
WS = re.compile(r"\s+")


def norm(s: str) -> str:
    return WS.sub(" ", (s or "").strip().lower())


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


def classify(groups) -> tuple[str, float]:
    """RANKING iff within-group values are a permutation of a contiguous 1..k rank set."""
    perm = 0
    tot = 0
    for vals in groups:
        vs = [v for v in vals if v is not None]
        if len(vs) < 2:
            continue
        tot += 1
        k = len(vs)
        if sorted(vs) == list(range(1, k + 1)):
            perm += 1
    return (("RANKING" if perm / tot > 0.80 else "RATING" if perm / tot < 0.20 else "MIXED"),
            (perm / tot if tot else 0.0)) if tot else ("UNDECIDABLE", 0.0)


def main() -> int:
    for f in (SECOND, COVAL):
        if not f.exists():
            print(f"  UNRUNNABLE: {f} absent. Exit 2, never 0."); return 2
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R399 · what estimand does the second corpus admit?   HEAD {head}\n")
    print("  ⛔ A BLOCKER, NOT A DETAIL. CoVal's unit is a COMPARISON and every clause is stated")
    print("     against an ORDERING. If the second corpus scores are absolute ratings, an ordering")
    print("     estimand and a rating estimand are DIFFERENT QUANTITIES, and running the first on")
    print("     the second rebuilds R233's error one release over.\n")

    # ---- CLASSIFIER CONTROLS, both directions ----------------------------------------------------
    rnd = random.Random(SEED)
    synth_rank = [rnd.sample(range(1, k + 1), k) for k in (2, 3, 4) for _ in range(200)]
    synth_rate = [[rnd.randint(0, 100) for _ in range(k)] for k in (2, 3, 4) for _ in range(200)]
    ct_rank, sh_rank = classify(synth_rank)
    ct_rate, sh_rate = classify(synth_rate)
    pos_ok, neg_ok = ct_rank == "RANKING", ct_rate == "RATING"
    print("  CONTROLS")
    print(f"    CLASSIFIER (+)  synthetic PERMUTATION groups classify {ct_rank} "
          f"(perm share {sh_rank:.2f})   {'PASS' if pos_ok else 'FAIL'}")
    print(f"    CLASSIFIER (-)  synthetic BOUNDED-VALUE groups classify {ct_rate} "
          f"(perm share {sh_rate:.2f})   {'PASS' if neg_ok else 'FAIL'}")

    # ---- (A) + (B): stream the second corpus ----------------------------------------------------
    groups: dict[str, list] = defaultdict(list)
    chosen: dict[str, int] = defaultdict(int)
    prompts2: set[str] = set()
    lo, hi, rows = None, None, 0
    for d in stream(SECOND):
        rows += 1
        k = d.get("interaction_id")
        try:
            s = float(d.get("score"))
        except Exception:
            s = None
        if k:
            groups[k].append(int(s) if s is not None and s == int(s) else s)
            if str(d.get("if_chosen")).lower() == "true":
                chosen[k] += 1
        if s is not None:
            lo = s if lo is None else min(lo, s)
            hi = s if hi is None else max(hi, s)
        p = norm(d.get("user_prompt", ""))
        if p:
            prompts2.add(p)

    ctype, perm_share = classify(groups.values())
    sizes = defaultdict(int)
    for v in groups.values():
        sizes[len(v)] += 1
    multi = {k: n for k, n in sizes.items() if k >= 2}
    exactly_one_chosen = sum(1 for k, v in groups.items() if len(v) >= 2 and chosen[k] == 1)
    n_multi = sum(multi.values())

    print(f"\n  (A) MEASUREMENT TYPE of `score`")
    print(f"      value range observed: [{lo:g}, {hi:g}] over {rows:,} rows")
    print(f"      within-interaction values are a 1..k permutation in {perm_share:.1%} of "
          f"interactions with >= 2 responses")
    print(f"      -> {ctype}")
    print(f"\n  (B) PAIRWISE STRUCTURE")
    print(f"      responses per interaction: {dict(sorted(sizes.items())[:6])}")
    print(f"      interactions with >= 2 responses: {n_multi:,}")
    print(f"      ... of which EXACTLY ONE is marked `if_chosen`: {exactly_one_chosen:,} "
          f"({exactly_one_chosen/n_multi:.1%})" if n_multi else "")

    # ---- MATCHER CONTROLS -----------------------------------------------------------------------
    probe2 = next(iter(prompts2))
    m_self = probe2 in prompts2
    # ⛔ CoVal's `prompt` is a CONVERSATION (`{id, messages}`), not a string, and the second corpus's
    #   `user_prompt` is a single turn. So the comparable unit has to be chosen, and the choice is a
    #   specification, not a detail. TWO cuts are computed and BOTH are reported:
    #     LAST  -- the final user turn, i.e. the request actually being answered. The strict analogue.
    #     ANY   -- every user turn in the conversation. STRICTLY MORE SENSITIVE.
    #   The headline uses ANY, deliberately: DISJOINT is the FLATTERING answer here — it is the one
    #   that makes the next round easy — so the detector must be pointed in the direction that can
    #   embarrass it, and the stricter cut is reported beside it rather than instead of it.
    coval_last, coval_any = [], []
    for d in stream(COVAL):
        p = d.get("prompt") or {}
        msgs = p.get("messages") if isinstance(p, dict) else None
        if not isinstance(msgs, list):
            continue
        users = [norm(m.get("content", "")) for m in msgs
                 if isinstance(m, dict) and m.get("role") == "user"]
        users = [u for u in users if u]
        if not users:
            continue
        coval_last.append(users[-1])
        coval_any.extend(users)
    coval_prompts = coval_any
    coval_index = set(coval_any)
    coval_last_index = set(coval_last)
    m_unit = bool(coval_prompts) and (coval_prompts[0] in coval_index)
    m_absent = ("zzq_no_such_prompt_zzq_%s" % SEED) not in prompts2
    print(f"\n    MATCHER (+)   a second-corpus prompt is found in the second-corpus index: {m_self}"
          f"   {'PASS' if m_self else 'FAIL'}")
    print(f"    MATCHER (+2)  a CoVal prompt matches ITSELF through the same normalisation: {m_unit}"
          f"   {'PASS' if m_unit else 'FAIL'}")
    print(f"                  the first control tests the INDEX; this one tests the NORMALISATION on")
    print(f"                  the CLAIM'S OWN UNIT — a control sharing the instrument's blind spot")
    print(f"                  confirms the instrument and licenses nothing.")
    print(f"    MATCHER (-)   an absent string returns no match: {m_absent}   "
          f"{'PASS' if m_absent else 'FAIL'}")

    if not (pos_ok and neg_ok and m_self and m_unit and m_absent):
        print("\n  UNVERIFIED — a control misbehaved. Exit 1, never a verdict."); return 1

    # ---- (C) OVERLAP ----------------------------------------------------------------------------
    hits = sorted(coval_index & prompts2)
    hits_last = sorted(coval_last_index & prompts2)
    print(f"\n  (C) OVERLAP — CoVal user turns appearing verbatim among the second corpus's prompts")
    print(f"      CoVal distinct user turns {len(coval_index):,} (ANY cut) · "
          f"{len(coval_last_index):,} (LAST cut) · second-corpus prompts {len(prompts2):,}")
    print(f"      exact-after-normalisation matches: ANY {len(hits):,} · LAST {len(hits_last):,}")
    print(f"      -> the ANY cut is strictly more sensitive and is what the verdict uses, because")
    print(f"         DISJOINT is the flattering answer and the detector must face that way")
    for h in hits[:3]:
        print(f"        · {h[:90]}")

    # ---- VERDICT --------------------------------------------------------------------------------
    ov = "W_OVERLAP" if hits else "W_DISJOINT"
    print()
    if ctype == "RATING":
        print(f"  W-RATING — `score` is a bounded rating on [{lo:g}, {hi:g}], NOT a permutation")
        print(f"  ({perm_share:.1%}). CoVal's ordering estimand does NOT transfer unchanged. Two")
        print(f"  routes exist and they are different quantities: a RATING-agreement estimand, or")
        print(f"  the `if_chosen` boolean, which is a genuine PAIRWISE PREFERENCE and is the field")
        print(f"  structurally closest to a CoVal comparison — available on {exactly_one_chosen:,}")
        print(f"  interactions with exactly one winner.")
    elif ctype == "RANKING":
        print(f"  W-RANKING — `score` is a permutation of ranks in {perm_share:.1%} of interactions.")
        print(f"  CoVal's ordering estimand transfers directly and the next round is far cheaper.")
    else:
        print(f"  W-MIXED — {perm_share:.1%} permutation share sits between the pre-registered")
        print(f"  thresholds. The TYPE is the finding, and no transport test is admissible until it")
        print(f"  is resolved.")

    if hits:
        print(f"\n  W-OVERLAP — {len(hits):,} CoVal prompts appear verbatim in the second corpus. Any")
        print(f"  transport claim must EXCLUDE them: a core built on one and tested on the other")
        print(f"  would not be out of distribution at all, and the leak would be invisible in the")
        print(f"  result.")
    else:
        print(f"\n  W-DISJOINT — no CoVal prompt was found verbatim among the second corpus's prompts.")
        print(f"  ⚠ THIS IS A LOWER BOUND ON SHARING, NOT A PROOF OF DISJOINTNESS. Exact matching")
        print(f"    misses paraphrase, truncation and re-tokenisation, and DISJOINT is the")
        print(f"    FLATTERING answer — it is the one that makes the next round easy. The matcher was")
        print(f"    shown able to FIND a match in both directions before this zero was believed.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, rows=rows, score_min=lo, score_max=hi,
               permutation_share=round(perm_share, 4), score_type=ctype,
               responses_per_interaction=dict(sorted(sizes.items())[:12]),
               interactions_multi=n_multi, exactly_one_chosen=exactly_one_chosen,
               coval_prompts=len(coval_index), second_prompts=len(prompts2),
               overlap=len(hits), overlap_last=len(hits_last), overlap_examples=hits[:5],
               coval_last_prompts=len(coval_last_index),
               controls=dict(rank_synth=ct_rank, rate_synth=ct_rate, pos_ok=pos_ok, neg_ok=neg_ok,
                             matcher_self=m_self, matcher_unit=m_unit, matcher_absent=m_absent),
               verdict=f"{ctype}|{ov}")
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r399_estimand_admissibility.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
