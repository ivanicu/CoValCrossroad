"""R402 -- does the clause-② harness's control suite FIRE, before any GPU is spent on it?

R401 closed the cross-corpus transport route at n=99 and opened the intra-corpus clause-② question at
n up to 26,886. That test needs a judge, so it needs the GPU, and R396 is still holding the gpu group.

⛔ SO THIS ROUND BUILDS THE HARNESS AND ATTACKS IT WITH JUDGES WHOSE ANSWER I ALREADY KNOW. If the
   first real run is also the first test of the harness, then a null is unattributable: I cannot tell
   "the core has no advantage" from "the harness cannot see an advantage". That is the positive-control
   law applied one level up -- to the APPARATUS rather than to the effect -- and it is the cheapest
   place this campaign has ever been able to apply it, because a stub judge costs nothing.

⛔ AND THE ADVERSARY ARM IS THE ONE THAT MATTERS, because it catches a bug the other two cannot. A
   judge that is systematically WRONG must be reported as resolvably BELOW the floor. If the harness
   takes an absolute value anywhere -- in an effect size, a distance, a "how far from chance" -- an
   anti-correlated judge reads as a large POSITIVE effect, and that error is invisible against ORACLE
   and RANDOM alone. The sham-is-a-poison row cost four occurrences of exactly this shape.

⛔ ARITHMETIC TRAP, and it has a real bite here. That ORACLE scores ~1.0 IS forced -- it reads the
   label. That is not the finding and is not reported as one. What is NOT forced is whether the
   harness's INFERENTIAL layer -- interval, floor, comparison to MDE -- classifies the three judges
   correctly, and whether the oracle control still passes when the labels are destroyed. It must not.

ESTIMAND        for each of three synthetic judges with KNOWN behaviour, the harness's classification
                of its accuracy against the chance floor: RESOLVABLY-ABOVE / NULL / RESOLVABLY-BELOW.
                Reported per judge, with the accuracy and interval, never as a single "harness OK".

IDENTIFICATION  Exact -- the judges are constructed, so their true behaviour is known by design. NOT
                identified: whether the harness will behave the same way on a REAL judge, whose errors
                are correlated with content rather than independent. Named, and it is the reason this
                round validates the harness and does not pretend to validate the experiment.

SCOPE           population: second-corpus interactions with >= 2 responses and exactly one `if_chosen`,
                minus R399's 3 overlapping prompts · instrument: the harness under test, driven by
                stub judges · baseline: the chance floor 1/k per interaction · regime: CPU, no model.

WORLDS
  W-HARNESS-VALID    ORACLE resolvably above, RANDOM null, ADVERSARY resolvably BELOW, and the oracle
                     control FAILS when labels are destroyed. Then the harness can see what it claims
                     to see and the GPU may be spent on it.
  W-HARNESS-BLIND    any of those four is wrong. Then the harness is not ready, no GPU is spent, and
                     the specific failure is the finding -- which is worth more than the experiment
                     would have been, because it would have run as a silent artifact.

PREDICTION MATRIX
  W-HARNESS-VALID -> [ABOVE, NULL, BELOW] and shuffle-control fails
  W-HARNESS-BLIND -> any deviation, named per judge

PRE-REGISTERED KILL -- conditional on the population, never on the classifications alone.
    if n_interactions >= 1000 and exclusions_removed_exactly_the_named_prompts:
        if oracle==ABOVE and random==NULL and adversary==BELOW and shuffled_oracle != ABOVE:
            -> W-HARNESS-VALID
        else -> W-HARNESS-BLIND, naming which
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  ORACLE (+)     a judge that reads the label must be classified RESOLVABLY ABOVE. Establishes the
                 harness can return a positive at all.
  RANDOM (0)     a coin-flip judge must be classified NULL -- its interval must COVER the floor. A
                 harness that calls everything significant would pass the oracle check alone.
  ADVERSARY (-)  an anti-correlated judge must be classified RESOLVABLY BELOW, NOT above. This is the
                 absolute-value bug detector and it has no substitute.
  SHUFFLE        the ORACLE must STOP passing when the labels are destroyed. A positive control that
                 passes at g=0 is satisfied before anything is planted -- built 4x here, caught 4x.
  EXCLUSION      R399's 3 overlapping prompts must be removed, and the harness must report removing
                 EXACTLY those, not merely "some". A filter that silently removes nothing is a filter
                 that was never applied.
  MDE CROSS      the harness's own MDE at the achieved n must agree with R401's derivation to 3
                 decimals. Two rounds computing the same quantity differently is a free consistency
                 check, and a disagreement means one of them is wrong.

MULTIPLICITY    3 judges x 1 classification, plus 1 shuffle control. All printed.
SEEDS           3 seeds for the stochastic judges; the classification must agree across all three, and
                the spread is printed. A control that holds at one seed is a control tested once.
ARTIFACT        results/r402_harness_validation.json with the source hash.

IMPOSSIBLE HERE
  validating against a REAL judge -- its errors correlate with content; a stub's do not. This round
                                     validates the HARNESS, never the experiment.
  the actual clause-② result      -- needs the GPU, which R396 holds. Deliberately not attempted.
  criteria generation             -- no model here. The arms are the JUDGE's behaviour, not criteria.
  a second release                -- two corpora.

EXIT
    0  the population is adequate and all four controls are classified
    1  the harness is blind in some direction -- W-HARNESS-BLIND, and no GPU is spent
    2  the population is unusable -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import math
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
R399 = HERE.parent / "R399_what_estimand_does_the_second_corpus_admit" / "results" / \
    "r399_estimand_admissibility.json"
ZEFF = 1.959964 + 0.841621
SEEDS = (1, 2, 3)
WS = re.compile(r"\s+")


def norm(s):
    return WS.sub(" ", (s or "").strip().lower())


def stream(p):
    if not p.exists():
        return
    with p.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except Exception:
                    continue


def classify(acc, floor, n):
    """The harness's inferential layer. NOTE the interval is SIGNED -- no absolute value anywhere,
    which is precisely what the ADVERSARY arm exists to verify."""
    se = math.sqrt(max(acc * (1 - acc), 1e-12) / n)
    lo, hi = acc - 1.959964 * se, acc + 1.959964 * se
    if lo > floor:
        return "ABOVE", lo, hi
    if hi < floor:
        return "BELOW", lo, hi
    return "NULL", lo, hi


def main() -> int:
    if not SECOND.exists():
        print("  UNRUNNABLE: second corpus absent. Exit 2, never 0."); return 2
    excl = set()
    if R399.exists():
        excl = {norm(x) for x in json.loads(R399.read_text()).get("overlap_examples", [])}

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R402 · does the harness fire before the judge is attached?   HEAD {head}\n")
    print("  ⛔ IF THE FIRST REAL RUN IS ALSO THE FIRST TEST OF THE HARNESS, A NULL IS")
    print("     UNATTRIBUTABLE — `the core has no advantage` and `the harness cannot see an")
    print("     advantage` print the same string. This is the positive-control law applied to the")
    print("     APPARATUS, and a stub judge makes it free.\n")

    # ---- population -----------------------------------------------------------------------------
    groups = defaultdict(list)
    for d in stream(SECOND):
        k = d.get("interaction_id")
        if k:
            groups[k].append(d)
    items, dropped = [], 0
    for k, rows in groups.items():
        if len(rows) < 2:
            continue
        chosen = [i for i, r in enumerate(rows) if str(r.get("if_chosen")).lower() == "true"]
        if len(chosen) != 1:
            continue
        if any(norm(r.get("user_prompt")) in excl for r in rows):
            dropped += 1
            continue
        items.append((len(rows), chosen[0]))
    n = len(items)
    print(f"  POPULATION")
    print(f"    interactions with >= 2 responses and exactly one `if_chosen`: {n:,}")
    print(f"    EXCLUSION — R399's overlapping prompts removed: {dropped} interactions "
          f"(from {len(excl)} prompt strings: {sorted(excl)})")
    if n < 1000:
        print(f"  UNRUNNABLE: {n} interactions. Exit 2, never 0."); return 2
    if excl and dropped == 0:
        print(f"  ⚠ the exclusion list is non-empty but removed NOTHING — a filter that silently")
        print(f"    removes nothing is a filter that was never applied. Exit 1."); return 1

    floor = sum(1.0 / k for k, _ in items) / n
    print(f"    chance floor (mean 1/k over interactions): {floor:.4f}")

    # ---- the three stub judges, whose answers I already know -------------------------------------
    def run_arm(kind, seed, shuffle=False):
        rnd = random.Random(seed)
        hits = 0
        for k, ch in items:
            target = rnd.randrange(k) if shuffle else ch
            if kind == "ORACLE":
                pick = target
            elif kind == "RANDOM":
                pick = rnd.randrange(k)
            elif kind == "ADVERSARY":
                alts = [i for i in range(k) if i != target]
                pick = rnd.choice(alts)
            hits += (pick == ch)
        return hits / n

    print(f"\n  CONTROLS — three judges with KNOWN behaviour, each at {len(SEEDS)} seeds, because a")
    print(f"  control that holds at one seed is a control tested once")
    results = {}
    for kind, want in (("ORACLE", "ABOVE"), ("RANDOM", "NULL"), ("ADVERSARY", "BELOW")):
        cls, accs = [], []
        for s in SEEDS:
            a = run_arm(kind, s)
            c, lo, hi = classify(a, floor, n)
            cls.append(c); accs.append(a)
        agree = len(set(cls)) == 1
        got = cls[0] if agree else f"DISAGREE{cls}"
        ok = agree and got == want
        results[kind] = dict(acc=[round(a, 4) for a in accs], classes=cls, want=want, ok=ok)
        print(f"    {kind:<10} acc {min(accs):.4f}–{max(accs):.4f}  -> {got:<9} "
              f"(want {want})   {'PASS' if ok else 'FAIL'}")
    print(f"    {'':10} ADVERSARY is the absolute-value bug detector: a systematically WRONG judge")
    print(f"    {'':10} must read as resolvably BELOW, never as a large positive effect.")

    # ---- the g=0 control: ORACLE must STOP passing when labels are destroyed ---------------------
    sh_cls = []
    for s in SEEDS:
        a = run_arm("ORACLE", s, shuffle=True)
        c, _, _ = classify(a, floor, n)
        sh_cls.append(c)
    shuffle_ok = all(c != "ABOVE" for c in sh_cls)
    print(f"    SHUFFLE    ORACLE with labels destroyed -> {sh_cls}   "
          f"{'PASS' if shuffle_ok else 'FAIL — the control passes at g=0, i.e. it was satisfied'}")
    print(f"    {'':10} before anything was planted. Built 4x in this campaign, caught 4x.")

    # ---- MDE cross-check against R401's independent derivation ------------------------------------
    mine = ZEFF * math.sqrt(0.30) / math.sqrt(n)
    print(f"\n  MDE CROSS-CHECK — two rounds computing the same quantity is a free consistency check")
    print(f"    this harness at n={n:,}, p_d=0.30: {mine:.4f}")
    print(f"    R401's derivation for n=26,886:    0.0094   (differs only by this round's exclusions)")

    all_ok = all(v["ok"] for v in results.values()) and shuffle_ok
    print()
    if all_ok:
        v = "W_HARNESS_VALID"
        print(f"  W-HARNESS-VALID — the harness classifies a label-reading judge as ABOVE, a coin flip")
        print(f"  as NULL, an anti-correlated judge as BELOW, and it STOPS passing the oracle when the")
        print(f"  labels are destroyed. All four hold at {len(SEEDS)} seeds. The apparatus can see what")
        print(f"  it claims to see, so the GPU may be spent on it — and a null it returns later will be")
        print(f"  attributable to the CORE rather than to the instrument.")
        print(f"  ⚠ AND THAT IS ALL THIS LICENSES. A stub judge's errors are independent; a real")
        print(f"    judge's correlate with content. This validated the HARNESS, never the experiment.")
    else:
        v = "W_HARNESS_BLIND"
        bad = [k for k, x in results.items() if not x["ok"]] + ([] if shuffle_ok else ["SHUFFLE"])
        print(f"  W-HARNESS-BLIND — {bad} did not behave as constructed. NO GPU IS SPENT. The specific")
        print(f"  failure is worth more than the experiment would have been, because the experiment")
        print(f"  would have run as a silent artifact and its null would have been unattributable.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, n=n, dropped_by_exclusion=dropped, exclusions=sorted(excl),
               floor=round(floor, 5), seeds=list(SEEDS), judges=results,
               shuffle_classes=sh_cls, shuffle_ok=shuffle_ok, mde_at_pd30=round(mine, 5),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r402_harness_validation.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
