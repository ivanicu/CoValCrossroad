#!/usr/bin/env python3
"""R475 — does the release's own DATASET CARD decide clause ③, and does the OBJECT agree with it?

ESTIMAND
    Two, and they are of different kinds, which is the point of the round.
    (a) DOCUMENTARY. Does `data/DATASET_CARD.md` state how `coval_core` was selected, in terms that
        clause ③ as derived by R444 can classify?  ③ excludes selectors consuming the annotator
        importance scores (`W_READERS = {topw_k, topabs_k, topwvar_k}`) or the prompt's human
        rankings (`TARGET_READERS`).  This is a reading, not a measurement, and is labelled so.
    (b) BEHAVIOURAL, and it is what makes (a) more than a quotation.  Let `m(c)` be the `coval_full`
        item most similar to core item `c` within the same prompt.  ESTIMAND = the mean PERCENTILE
        of `m(c)`'s annotator weight among that prompt's items, under two weightings:
            w      = mean annotator score          (the `topw_k` reading)
            |w|    = |mean annotator score|        (the `topabs_k` reading -- the card says the
                                                    process "rewrites all rubric items to have
                                                    positive weight", i.e. negates the negatives)
        Under the card, both exceed 0.5 and **|w| exceeds w**, because a strongly-negative item is
        eligible after negation and its `w` percentile is near 0 while its `|w|` percentile is near 1.

IDENTIFICATION
    ⚠ THE JOIN THE FILE DESTROYS.  `coval_core` items carry ONLY `criterion` -- no `rubric_item_id`,
    no `scores` (verified on the object this round).  So the exact provenance link is NOT in the
    release and the estimand is recovered through a SIMILARITY MATCH, which is an instrument and is
    controlled below.  This is precisely why R466 returned UNKNOWN and R469 concluded ③ was
    undecidable here: both were reasoning about INSTRUMENTS, and provenance is a RECORD.

SCOPE
    population  968 home-release prompts with both a core and a full rubric (986 have a core; the
                968 are the ones the campaign's ranking join covers -- both reported).
    instrument  token-Jaccard nearest-neighbour within prompt; swept over 3 tokenisations (G4).
    baseline    the prompt's own items, as a percentile -- so prompt-level difficulty cancels.
    regime      k in {2,3,4}; median 16 annotators/item.

WORLDS
    A  CARD-TRUE, abs   core selects on |w| (rewrite-then-rank).  -> |w| pct high, w pct lower.
    B  CARD-TRUE, raw   core selects on w  (negation is rare in effect) -> w pct exceeds |w| pct.
    C  CARD-FALSE       core is not rating-driven at all          -> both about 0.5.
    D  MATCHER-BLIND    the matcher cannot find the source item   -> controls below fail, verdict
                                                                    UNVERIFIED, never C.

PREDICTION MATRIX
                      pct(|w|)   pct(w)    plant recovered
    A  card-true abs    >0.5      lower        yes
    B  card-true raw    >0.5      approx same  yes
    C  card-false      ~0.5      ~0.5          yes
    D  matcher-blind    any       any          NO   -> UNVERIFIED

PRE-REGISTERED KILL  (a CONDITIONAL, never a bare threshold -- CLAUDE.md P16)
    if plant_recovered and crossprompt_is_null:
        card-true iff pct(|w|) exceeds the cross-prompt null by more than the null's own spread
    else:
        UNVERIFIED

CONTROLS
    POSITIVE   plant a pseudo-core = the 4 highest-|w| items VERBATIM, run the same matcher.
               Must return pct(|w|) ~ 1.0.  A matcher that cannot recover a verbatim plant is blind.
    g=0        plant a pseudo-core = 4 RANDOM items verbatim -> must return ~0.5, NOT ~1.0.
               (This is what makes the positive control able to fail -- CLAUDE.md P4 "control that
               cannot PASS", built 4x, caught 4x.)
    NEGATIVE   match each prompt's core against a DIFFERENT prompt's full items.  Destroys the
               provenance while preserving every other property (text style, length, item count).
               Must return ~0.5.  This is the control that would expose a matcher biased toward
               high-|w| text for reasons of style rather than provenance.
    PLACEBO    percentile of a field that cannot be involved: the item's INDEX in the file.
               Must return ~0.5 under the real match.

MULTIPLICITY
    3 tokenisations x 2 weightings x {real, cross, plant, random} = 24 cells; all reported.

ARTIFACT  results/r475_card_vs_object.json          SEED 0 (cross-prompt pairing, random plant)

IMPOSSIBLE HERE, NAMED
    interventionally validated  -- would require re-running the authors' selection pipeline, which
                                   is not released (the card describes it; no code ships).
    independently replicated    -- a second release built by the same documented process.
    construct validated         -- an external gold standard for "is this item rating-selected".
"""
import json, sys, re, random, pathlib
import numpy as np
sys.path.insert(0, "assurance")
from clause3_as_written import W_READERS, TARGET_READERS

random.seed(0); np.random.seed(0)
ROOT = pathlib.Path(".")
OUT = ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/R475_the_card_decides_clause_three/results"

STOP = set("a an the to of and or in on for is are be with that this it as by not".split())
def tok_words(s):   return set(re.findall(r"[a-z']+", s.lower()))
def tok_content(s): return tok_words(s) - STOP
def tok_char3(s):
    s = re.sub(r"\s+", " ", s.lower().strip())
    return {s[i:i+3] for i in range(max(0, len(s)-2))}
TOKENISERS = {"words": tok_words, "content": tok_content, "char3": tok_char3}

def jac(a, b):
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)

# ---- load ------------------------------------------------------------------
rows = []
with open("data/conversation_rubrics.jsonl") as f:
    for line in f:
        r = json.loads(line)
        full = [x for x in r.get("coval_full", []) if x.get("criterion") and x.get("scores")]
        core = [x["criterion"] for x in r.get("coval_core", []) if x.get("criterion")]
        if len(full) >= 5 and core:
            w = np.array([np.mean([s["score"] for s in x["scores"]]) for x in full], float)
            rows.append({"full": [x["criterion"] for x in full], "w": w, "core": core})
print(f"  prompts with a core and >=5 rated full items: {len(rows)}")

def pct(vals, i):
    """percentile of element i among vals -- ties get the midpoint, so a constant vector -> 0.5"""
    v = np.asarray(vals, float)
    return float((np.sum(v < v[i]) + 0.5*np.sum(v == v[i])) / len(v))

def measure(tokname, arm):
    """-> dict of mean percentiles under the named arm. arm decides WHICH core text is matched
    against WHICH prompt's full items -- that is the only thing the controls vary."""
    T = TOKENISERS[tokname]
    ftok = [[T(c) for c in r["full"]] for r in rows]
    acc = {"w": [], "absw": [], "index": [], "sim": []}
    n = len(rows)
    for i, r in enumerate(rows):
        if arm == "real":       cores = r["core"];                       tgt = i
        elif arm == "cross":    cores = rows[(i+1) % n]["core"];         tgt = i
        elif arm in ("oracle_abs","oracle_raw"): cores = [None]; tgt = i
        elif arm == "plant_abs":  # the 4 highest-|w| items, VERBATIM
            o = np.argsort(-np.abs(r["w"]))[:4];  cores = [r["full"][j] for j in o]; tgt = i
        elif arm == "plant_raw":  # the 4 highest-w items, VERBATIM
            o = np.argsort(-r["w"])[:4];          cores = [r["full"][j] for j in o]; tgt = i
        elif arm == "random":   # 4 random items, VERBATIM  (g=0)
            o = random.sample(range(len(r["full"])), min(4, len(r["full"])))
            cores = [r["full"][j] for j in o];    tgt = i
        w = rows[tgt]["w"]; F = ftok[tgt]
        if arm.startswith("oracle"):          # CEILING: the plant WITHOUT the matcher
            o = (np.argsort(-np.abs(w)) if arm.endswith("abs") else np.argsort(-w))[:4]
            for j in map(int, o):
                acc["sim"].append(1.0); acc["w"].append(pct(w, j))
                acc["absw"].append(pct(np.abs(w), j)); acc["index"].append((j+0.5)/len(w))
            continue
        for c in cores:
            ct = T(c)
            sims = [jac(ct, f) for f in F]
            j = int(np.argmax(sims))
            acc["sim"].append(sims[j])
            acc["w"].append(pct(w, j))
            acc["absw"].append(pct(np.abs(w), j))
            acc["index"].append((j + 0.5) / len(w))          # PLACEBO
    return {k: float(np.mean(v)) for k, v in acc.items()} | {"n_items": len(acc["w"])}

grid = {t: {a: measure(t, a) for a in ("real", "cross", "plant_abs", "plant_raw", "oracle_abs", "oracle_raw", "random")} for t in TOKENISERS}

print(f"\n  {'tokeniser':<9} {'arm':<7} {'pct(|w|)':>9} {'pct(w)':>8} {'pct(idx)':>9} {'sim':>7}")
for t in TOKENISERS:
    for a in ("oracle_abs", "plant_abs", "oracle_raw", "plant_raw", "random", "real", "cross"):
        g = grid[t][a]
        print(f"  {t:<9} {a:<7} {g['absw']:>9.4f} {g['w']:>8.4f} {g['index']:>9.4f} {g['sim']:>7.4f}")

# ---- the pre-registered kill, as a conditional -----------------------------
# ⛔ THE CEILING IS DERIVED (CLAUDE.md P4 "control that cannot PASS", 6th build, caught 6th time).
# Planting the top-4 of a prompt with m items gives mean percentile  1 - 2/m  -- NOT 1.0.  The first
# version of this gate demanded >0.95 and failed on a matcher that recovered the plant VERBATIM
# (sim = 1.0000).  Derive, then confirm.
ALG = float(np.mean([1.0 - 2.0/len(r["w"]) for r in rows for _ in range(min(4, len(r["w"])))]))
CA = grid["words"]["oracle_abs"]["absw"]; CR = grid["words"]["oracle_raw"]["w"]
print(f"\n  CEILING, algebraic  mean(1 - 2/m) = {ALG:.4f}   <- assumes DISTINCT w; the data has ties")
print(f"  CEILING, MEASURED   oracle |w| = {CA:.4f}   oracle w = {CR:.4f}   <- matcher removed")
# POSITIVE CONTROL, correctly posed: does the matcher recover the ceiling the design can return?
ok_plant = (all(abs(grid[t]["plant_abs"]["absw"] - CA) < 0.01 for t in TOKENISERS) and
            all(abs(grid[t]["plant_raw"]["w"]    - CR) < 0.01 for t in TOKENISERS))
ok_g0     = all(0.35 < grid[t]["random"]["absw"] < 0.65 for t in TOKENISERS)  # control CAN fail
ok_cross  = all(0.35 < grid[t]["cross"]["absw"]  < 0.65 for t in TOKENISERS)  # NEGATIVE
ok_placebo= all(0.35 < grid[t]["real"]["index"]  < 0.65 for t in TOKENISERS)  # PLACEBO
print(f"\n  POSITIVE  matcher recovers the MEASURED ceiling to within 0.01               : {ok_plant}")
print(f"  g=0       verbatim RANDOM plant lands mid-scale (control can fail)       : {ok_g0}")
print(f"  NEGATIVE  cross-prompt match is null                                     : {ok_cross}")
print(f"  PLACEBO   file-index percentile is null under the real match             : {ok_placebo}")

if not (ok_plant and ok_g0 and ok_cross and ok_placebo):
    verdict, world = "UNVERIFIED", "D (matcher blind or a control failed)"
else:
    spread = float(np.std([grid[t]["cross"]["absw"] for t in TOKENISERS]))
    lo = min(grid[t]["real"]["absw"] for t in TOKENISERS)
    hi = max(grid[t]["cross"]["absw"] for t in TOKENISERS)
    card_true = lo > hi + max(spread, 0.02)
    if not card_true:
        verdict, world = "CARD-NOT-CONFIRMED-BY-OBJECT", "C"
    else:
        d_abs = np.mean([grid[t]["real"]["absw"] for t in TOKENISERS])
        d_raw = np.mean([grid[t]["real"]["w"]    for t in TOKENISERS])
        verdict = "CARD-CONFIRMED"
        world = "A (rewrite-then-rank on |w|)" if d_abs > d_raw + 0.02 else "B (rank on w)"
        # how far from chance to a PURE rating-selector, in each weighting.  The matcher recovers
        # the source item only at sim ~ 0.49 (the release rewrote the text), and imperfect matching
        # attenuates TOWARD chance -- so each fraction is a LOWER BOUND, never a point estimate.
        for key, plant in (("absw", "plant_abs"), ("w", "plant_raw")):
            C = np.mean([grid[t]["cross"][key] for t in TOKENISERS])
            P = np.mean([grid[t]["oracle_abs" if key=="absw" else "oracle_raw"][key] for t in TOKENISERS])
            R = np.mean([grid[t]["real"][key]  for t in TOKENISERS])
            print(f"  fraction of the way from chance to a pure top-4 selector, {key:>4}: "
                  f"({R:.4f}-{C:.4f})/({P:.4f}-{C:.4f}) = {(R-C)/(P-C):>6.1%}  (LOWER BOUND)")
print(f"\n  VERDICT {verdict}   surviving world: {world}")

# ---- what this does to clause ③ and to the extension -----------------------
card_says_w = True   # DOCUMENTARY, quoted verbatim in README.md; not a measurement
print(f"\n  ③ as derived by R444 excludes W_READERS={sorted(W_READERS)}")
print(f"    the card: 'select up to four rubric items with the HIGHEST AVERAGE RATINGS',")
print(f"              having 'first rewritten all rubric items to have positive weight'")
print(f"    -> that IS topabs_k, which is in W_READERS.")
status = "EXCLUDED" if (card_says_w and verdict == "CARD-CONFIRMED") else "UNKNOWN"
print(f"    -> `coval_core` under ③: {status}   (was UNKNOWN in R466/R469/R470)")
print(f"    -> the extension of the definition is {'0 under EVERY reading' if status=='EXCLUDED' else 'unchanged [0,1]'}")

OUT.mkdir(parents=True, exist_ok=True)
json.dump({"n_prompts": len(rows), "grid": grid, "verdict": verdict, "world": world,
           "controls": {"positive": ok_plant, "g0": ok_g0, "negative": ok_cross, "placebo": ok_placebo},
           "coval_core_clause3": status},
          open(OUT/"r475_card_vs_object.json", "w"), indent=2)
sys.exit(0 if verdict != "UNVERIFIED" else 2)
