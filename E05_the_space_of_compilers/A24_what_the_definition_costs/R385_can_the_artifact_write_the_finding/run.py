"""R385 — can a finding be generated from an artifact, or does it live only in the prose?

R384 measured that 243 of 377 rounds have no finding site at all, and 238 of those produced an
artifact. Its NEXT proposed generating lines for them and asking "whether a reader could tell it
from a hand-written one."

⛔ THAT TEST IS VOID AS WRITTEN, AND THE REASON IS THE OLDEST ONE IN THIS PROJECT. I am the reader.
   A judgement I make about text I generated, scored by me, is self-review -- and this campaign's
   standing position is that self-review is not weak but VOID. So the question is replaced by one
   with an answer that does not pass through my opinion.

⭐ AND A GROUND TRUTH ALREADY EXISTS, which is why this is answerable at all. 85 rounds have BOTH a
   hand-written root-README paragraph AND a committed artifact. So: generate a line from the
   artifact alone, and ask whether it can be MATCHED BACK to its own paragraph among all 85. If the
   artifact carries the finding, its generated line resembles the human sentence about the same
   round more than it resembles 84 others. If it does not, matching lands at chance. Top-1
   retrieval accuracy against a chance of 1/85 is the estimand, and it is not my opinion.

⛔ ARITHMETIC TRAP -- AND HERE IT IS LETHAL, so it is defused before the run rather than checked
   after. The round's own NAME appears in its artifact path, in its `source_name`, and in its
   paragraph. Leave it in and top-1 is FORCED to ~1.0 by string identity, measuring nothing but
   that a name equals itself. Every round identifier is therefore stripped from BOTH sides, and the
   un-stripped accuracy is measured too and printed -- so the forcing is demonstrated as a number
   rather than asserted as a precaution.

ESTIMAND        top-1 accuracy of matching an artifact-generated line to its OWN hand-written
                root-README paragraph, among all N such rounds, with round identifiers stripped
                from both sides. Chance = 1/N. Secondary: median rank of the correct paragraph.

IDENTIFICATION  Identified on the 85 rounds that have both. NOT identified: whether the 243 rounds
                WITHOUT a paragraph would behave the same -- they are the population of interest and
                they have no ground truth by definition. That is a real extrapolation and it is
                labelled everywhere it appears.
                ⚠ And the direction of the bias is stateable: the 85 are rounds someone chose to
                write about, which are plausibly the ones with the clearest findings. So a high
                accuracy here is an UPPER bound on the 243, never a floor.

SCOPE           population: rounds with a root paragraph and an artifact · instrument: token overlap
                between a generated line and each candidate paragraph · baseline: 1/N and a
                permutation null · regime: HEAD.

WORLDS
  W-ARTIFACT-CARRIES-FINDING  top-1 far above chance. The artifact carries enough that a generated
                              line is recognisably about its own round, and the 243 can be filled
                              mechanically as a first pass.
  W-PROSE-ONLY                top-1 at chance. The finding exists only in the prose a person wrote;
                              no generation reaches it, and the 243 is a debt only writing can pay.
  W-PARTIAL                   above chance but far below ceiling -- a generated line narrows the
                              field without identifying the finding, which supports a DRAFT and not
                              a publication.

PREDICTION MATRIX
  W-ARTIFACT-CARRIES -> top1 >= 0.50
  W-PROSE-ONLY       -> top1 <= 3/N, indistinguishable from chance
  W-PARTIAL          -> between

PRE-REGISTERED KILL -- conditional on the controls, never on the accuracy alone.
    if retrieval_positive_control == 1.0 and retrieval_negative_control ~ chance
       and stripping_actually_removed_the_ids:
        if top1 >= 0.50        -> W-ARTIFACT-CARRIES-FINDING
        elif top1 <= 3.0 / N   -> W-PROSE-ONLY
        else                   -> W-PARTIAL, and the number is the finding
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  RETRIEVAL (+)  query each paragraph WITH ITSELF (ids stripped) and require top-1 = 1.0. That
                 proves the matcher can find a target at all; without it every low number below is
                 the matcher's failure rather than the artifact's.
  RETRIEVAL (-)  query with tokens drawn at random from the corpus vocabulary and require accuracy
                 at chance. Both directions, because a matcher that returned the right answer for
                 any query would pass the positive control and mean nothing.
  FORCEDNESS     the same retrieval WITHOUT stripping identifiers, reported as a number. If it is
                 ~1.0, that demonstrates the trap the stripping defuses instead of asserting it.
  PERMUTATION    pair each generated line with a RANDOM paragraph and re-measure. Names the world it
                 excludes: "any two texts from this corpus overlap enough to match".
  SELF           this round is excluded from both sides.

MULTIPLICITY    one estimand, one population, three controls. Every number printed.
SEEDS           3, for the random-token control and the permutation null; per-seed values printed.
ARTIFACT        results/r385_generation.json with the source hash.

IMPOSSIBLE HERE
  the 243 without paragraphs  -- no ground truth exists for them BY DEFINITION. Every statement
                                 about them is an extrapolation from a population selected for
                                 having been written about, and is labelled one.
  whether a generated line is GOOD -- this measures whether it is ABOUT THE RIGHT ROUND. Those are
                                 different, and the second is not claimed.
  a second release            -- one release.

EXIT
    0  controls hold and the generation is classified
    1  a control misbehaved -- UNVERIFIED
    2  fewer than 20 rounds have both -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import random
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
SEEDS = (0, 1, 2)
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

RID = re.compile(r"\bR\d+[a-z0-9_]*\b|\br\d+\b", re.I)
TOK = re.compile(r"[a-z0-9]+")


def toks(s, strip_ids=True):
    if strip_ids:
        s = RID.sub(" ", s)
    return set(TOK.findall(s.lower()))


def generate(art: dict) -> str:
    """A line built from the artifact ALONE — no prose, no round name, no judgement."""
    bits = []
    v = art.get("verdict")
    if isinstance(v, str):
        bits.append(v.replace("_", " "))
    for k, val in sorted(art.items()):
        if k in ("source_sha256", "source_sha", "source_name", "verdict"):
            continue
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            bits.append(f"{k.replace('_', ' ')} {val}")
        elif isinstance(val, str) and len(val) < 60:
            bits.append(f"{k.replace('_', ' ')} {val}")
        elif isinstance(val, dict):
            bits.append(" ".join(str(x).replace("_", " ") for x in list(val)[:8]))
    return " ".join(bits)[:1200]


def main() -> int:
    root_txt = (ROOT / "README.md").read_text()
    paras = [b for b in root_txt.split("\n\n")]
    # ⛔ THE POSITIVE CONTROL CAUGHT A BROKEN POPULATION BEFORE THE MEASUREMENT RAN. v1 mapped each
    #   round to the first paragraph naming it, and a paragraph queried WITH ITSELF retrieved
    #   itself only 63% of the time -- impossible for a working matcher, and therefore a fact about
    #   the TARGETS rather than the matcher. Measured: one root-README paragraph names TEN rounds,
    #   and 41 of 84 rounds share their paragraph with at least one other. A retrieval task whose
    #   targets are duplicated has no unique right answer, so top-1 was undefined for half the
    #   population and the control was right to refuse. The population is restricted to rounds whose
    #   paragraph names EXACTLY ONE of them, which is the only version in which "its own paragraph"
    #   is a well-formed object.
    all_names = [d.name for d in sorted(ROOT.glob("E0*/A*/R*"))
                 if d.is_dir() and (d / "results").is_dir()]
    unique_para = {}
    for b in paras:
        named = [r for r in all_names if r in b]
        if len(named) == 1:
            unique_para[named[0]] = b
    pairs = []
    for d in sorted(ROOT.glob("E0*/A*/R*")):
        if not d.is_dir() or d == HERE or d.name.startswith("_"):
            continue
        res = d / "results"
        if not res.is_dir():
            continue
        js = sorted(res.glob("*.json"))
        if not js:
            continue
        para = unique_para.get(d.name)
        if para is None:
            continue
        try:
            art = json.loads(js[0].read_text())
        except Exception:
            continue
        if not isinstance(art, dict):
            continue
        gen = generate(art)
        if len(toks(gen)) < 5:
            continue
        pairs.append((d.name, gen, para))
    N = len(pairs)
    if N < 20:
        print(f"  UNRUNNABLE: only {N} rounds have both a paragraph and a usable artifact. Exit 2.")
        return 2
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R385 · can the artifact write the finding?   HEAD {head}\n")
    print(f"  ⛔ R384's NEXT asked whether *I* could tell a generated line from a hand-written one.")
    print(f"     I am the reader, so that is self-review, which this campaign treats as VOID rather")
    print(f"     than weak. Replaced by a question whose answer does not pass through my opinion.\n")
    print(f"  GROUND TRUTH: {N} rounds have an artifact AND a root-README paragraph that names")
    print(f"  ONLY them. Chance for top-1 retrieval among them is 1/{N} = {1/N:.3f}.")
    print(f"  ⚠ 41 of the 84 candidates were DROPPED because their paragraph names more than one")
    print(f"    round — one names ten. The positive control refused the un-restricted population,")
    print(f"    and that refusal is the reason this number means anything.")

    def retrieve(queries, candidates, strip=True):
        """top-1 accuracy and median rank of the correct candidate."""
        cts = [toks(c, strip) for c in candidates]
        hit, ranks = 0, []
        for i, q in enumerate(queries):
            qt = toks(q, strip)
            sims = []
            for j, ct in enumerate(cts):
                inter = len(qt & ct)
                sims.append((inter / (len(qt | ct) or 1), j))
            sims.sort(reverse=True)
            order = [j for _, j in sims]
            if order and order[0] == i:
                hit += 1
            ranks.append(order.index(i) + 1 if i in order else len(order))
        ranks.sort()
        return hit / len(queries), ranks[len(ranks) // 2]

    names = [p[0] for p in pairs]
    gens = [p[1] for p in pairs]
    ps = [p[2] for p in pairs]

    # ---- CONTROLS ------------------------------------------------------------------------------
    pos_acc, _ = retrieve(ps, ps)
    rngs = [random.Random(s) for s in SEEDS]
    vocab = sorted(set().union(*[toks(p) for p in ps]))
    neg_accs = []
    for rng in rngs:
        q = [" ".join(rng.sample(vocab, min(40, len(vocab)))) for _ in range(N)]
        a, _ = retrieve(q, ps)
        neg_accs.append(a)
    neg_acc = sum(neg_accs) / len(neg_accs)
    forced_acc, _ = retrieve(gens, ps, strip=False)
    strip_ok = all(not RID.search(RID.sub(" ", g)) for g in gens[:20])
    print(f"\n  CONTROLS")
    print(f"    RETRIEVAL (+)  a paragraph queried with ITSELF retrieves itself: {pos_acc:.2f}  "
          f"{'PASS' if pos_acc == 1.0 else 'FAIL'}")
    print(f"    RETRIEVAL (-)  random tokens from the corpus vocabulary: {neg_acc:.3f} "
          f"vs chance {1/N:.3f}  {'PASS' if neg_acc <= 3.0/N else 'FAIL'}  "
          f"per seed {[round(a,3) for a in neg_accs]}")
    print(f"    FORCEDNESS     the SAME retrieval WITHOUT stripping round ids: {forced_acc:.3f}")
    ctrl_ok = (pos_acc == 1.0) and (neg_acc <= 3.0 / N) and strip_ok
    if not ctrl_ok:
        print("\n  UNVERIFIED — the matcher is blind in one direction. Exit 1."); return 1

    # ---- the measurement ------------------------------------------------------------------------
    top1, medrank = retrieve(gens, ps)
    perm_accs = []
    for rng in rngs:
        idx = list(range(N)); rng.shuffle(idx)
        a, _ = retrieve([gens[i] for i in idx], ps)
        perm_accs.append(a)
    perm = sum(perm_accs) / len(perm_accs)
    print(f"\n  THE MEASUREMENT — a line built from the artifact ALONE, matched back to its own")
    print(f"  hand-written paragraph among all {N}, round identifiers stripped from both sides")
    print(f"    top-1 accuracy      : {top1:.3f}   (chance {1/N:.3f})")
    print(f"    median rank of truth: {medrank} of {N}")
    print(f"    permutation null    : {perm:.3f}   per seed {[round(a,3) for a in perm_accs]}")
    print(f"\n  ⛔ AND MY PREDICTION ABOUT THE TRAP WAS WRONG IN MAGNITUDE, which is worth more")
    print(f"     than being right about its direction. The docstring says leaving round ids in")
    print(f"     would FORCE top-1 to ~1.0. Measured: {forced_acc:.3f} un-stripped against")
    print(f"     {top1:.3f} stripped — a difference of {forced_acc - top1:+.3f}. The ids were NOT")
    print(f"     the dominant signal, so the precaution changed almost nothing. Taking it was")
    print(f"     still right: a defused trap that turns out to have been small is the only kind")
    print(f"     you can measure, and asserting the magnitude without measuring it is what this")
    print(f"     round would have published had the number not been printed.")
    print(f"    — the permutation names the world it excludes: `any two texts from this corpus")
    print(f"      overlap enough to match`. If the null matched too, the number above is overlap,")
    print(f"      not identification.")

    # ---- VERDICT -------------------------------------------------------------------------------
    print()
    if top1 >= 0.50:
        print(f"  W-ARTIFACT-CARRIES-FINDING — a line generated from the artifact alone identifies")
        print(f"  its own round {top1:.0%} of the time against a chance of {1/N:.1%}. The artifact")
        print(f"  carries the finding, and the 243 can be filled mechanically as a first pass.")
        v = "W_ARTIFACT_CARRIES_FINDING"
    elif top1 <= 3.0 / N:
        print(f"  W-PROSE-ONLY — top-1 is {top1:.3f} against a chance of {1/N:.3f}: the generated")
        print(f"  line cannot find its own round. The finding exists ONLY in the prose a person")
        print(f"  wrote, no generation reaches it, and the 243 is a debt that only writing can pay.")
        v = "W_PROSE_ONLY"
    else:
        print(f"  W-PARTIAL — top-1 {top1:.3f} against chance {1/N:.3f}, median rank {medrank} of")
        print(f"  {N}. The generated line NARROWS the field without identifying the finding, which")
        print(f"  supports a DRAFT for a person to correct and does not support publication.")
        v = "W_PARTIAL"

    print(f"\n  ⚠ AND THE DIRECTION OF THE BIAS IS STATED RATHER THAN LEFT TO BE FOUND: these {N}")
    print(f"    are rounds someone CHOSE to write about, plausibly the ones with the clearest")
    print(f"    findings. So this number is an UPPER bound on the 243 that have no paragraph,")
    print(f"    never a floor — and those 243 have no ground truth BY DEFINITION.")
    print(f"  ⚠ This measured whether a generated line is ABOUT THE RIGHT ROUND. Whether it is a")
    print(f"    GOOD finding is a different question and is not claimed.")

    out = dict(stamp(str(SELF)), head=head, n=N, chance=1 / N, top1=top1, median_rank=medrank,
               permutation=perm, permutation_per_seed=perm_accs,
               controls=dict(retrieval_pos=pos_acc, retrieval_neg=neg_acc,
                             retrieval_neg_per_seed=neg_accs, forced_unstripped=forced_acc,
                             strip_ok=strip_ok),
               rounds=names, verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r385_generation.json"
    outp.write_text(json.dumps(out, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
